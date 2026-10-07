"""AI Service coordinating Primary (Google Gemini) and Fallback (Groq) providers.
Follows strict separation of concerns, identical instructions, same output contract,
and transient-only fallback behavior.
"""
import json
import logging
from typing import List, Dict, Any, Tuple
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.transcript import AIExtractedOutput

logger = logging.getLogger(__name__)


import copy
from pydantic import ValidationError

SYSTEM_INSTRUCTIONS = """You are the Lead Technical Project Manager AI for NovaWorks Technologies.
Your task is to analyze meeting transcripts and extract structured Projects and Tasks.

### MANDATORY INSTRUCTIONS:
1. Extract only actual decisions agreed upon during the meeting.
2. Follow FINAL decisions and corrections made later in the meeting (e.g. during final recaps or estimate revisions).
3. Ignore rejected, postponed, or future features explicitly mentioned as out-of-scope.
4. Never invent employees. Use ONLY the user IDs from the supplied directory.
5. Managers must be users with role "MANAGER". Match the project's manager by name to their ID in the directory.
6. Task assignees must be users with role "AGENT". Match each task owner by name to their ID in the directory.
7. Preserve all explicit hourly estimates (estimatedHours must be a positive number > 0).
8. Preserve all explicit deadlines. Convert all dates to standard ISO "YYYY-MM-DD" format (assume year 2026 if only month and day are specified).
9. Do not create management tasks. Only technical delivery tasks.
10. Do not merge separate tasks merely because they share an assignee. Keep distinct tasks distinct.
11. Return strictly structured JSON matching the following contract:
{
  "projects": [
    {
      "name": "Project Name",
      "clientName": "Client Name",
      "description": "Project overview",
      "managerId": 1,
      "deadline": "YYYY-MM-DD",
      "tasks": [
        {
          "title": "Task Title",
          "description": "Task description",
          "assigneeId": 5,
          "deadline": "YYYY-MM-DD",
          "estimatedHours": 12.0
        }
      ]
    }
  ]
}"""


def is_transient_error(error: Exception) -> bool:
    """Determine if an exception represents a transient provider failure
    (503, 429, timeout, connection error, temporary service unavailable, or malformed JSON).
    Explicitly returns False for Pydantic validation errors or invalid data.
    """
    if isinstance(error, ValidationError):
        return False

    if isinstance(error, (json.JSONDecodeError, ValueError)):
        return True

    status_code = getattr(error, "code", getattr(error, "status_code", None))
    if status_code in (503, 429, 502, 504):
        return True
    if status_code in (400, 401, 403, 404, 422):
        return False

    err_str = str(error).lower()
    err_type = type(error).__name__.lower()

    # Transient error indicators
    if any(code in err_str for code in ["503", "429", "502", "504", "unavailable", "rate limit", "high demand", "overloaded", "quota exceeded"]):
        return True

    # Timeouts and network connection errors
    if any(term in err_type or term in err_str for term in ["timeout", "connect", "connection", "network", "servererror", "resourceexhausted"]):
        return True

    return False


def _clean_and_parse_json(raw_text: str) -> dict:
    """Extract and parse JSON safely from LLM output, removing markdown fences."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


class AIService:
    """Manages AI extraction with Gemini as primary and Groq as fallback."""

    def __init__(self):
        self._gemini_client = None
        self._groq_client = None

    def get_gemini_client(self):
        """Lazy init of Gemini client."""
        if not settings.GEMINI_API_KEY or not settings.GEMINI_API_KEY.strip():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini API key is not configured.",
            )
        if self._gemini_client is None:
            from google import genai
            self._gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY.strip())
        return self._gemini_client

    def get_groq_client(self):
        """Lazy init of Groq client."""
        if not settings.GROQ_API_KEY or not settings.GROQ_API_KEY.strip():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Groq API key is not configured.",
            )
        if self._groq_client is None:
            from groq import Groq
            self._groq_client = Groq(api_key=settings.GROQ_API_KEY.strip())
        return self._groq_client

    @staticmethod
    def _to_strict_json_schema(schema_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a standard Pydantic JSON schema into strict mode for Groq:
        - additionalProperties: false on every object schema
        - all properties listed in required
        """
        s = copy.deepcopy(schema_dict)

        def _walk(obj):
            if isinstance(obj, dict):
                if obj.get("type") == "object" or "properties" in obj:
                    obj["additionalProperties"] = False
                    if "properties" in obj:
                        obj["required"] = list(obj["properties"].keys())
                for v in obj.values():
                    _walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    _walk(item)

        _walk(s)
        return s

    def _call_gemini(self, prompt: str) -> AIExtractedOutput:
        """Call primary provider (Gemini)."""
        client = self.get_gemini_client()
        from google.genai import types

        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIExtractedOutput,
                temperature=0.1,
            ),
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini.")

        parsed_data = _clean_and_parse_json(response.text)
        return AIExtractedOutput.model_validate(parsed_data)

    def _call_groq(self, directory_text: str, transcript_text: str) -> AIExtractedOutput:
        """Call fallback provider (Groq) using strict JSON Schema."""
        client = self.get_groq_client()
        strict_schema = self._to_strict_json_schema(AIExtractedOutput.model_json_schema())

        messages = [
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTIONS,
            },
            {
                "role": "user",
                "content": f"### VERIFIED TEAM DIRECTORY:\n{directory_text}\n\n### TRANSCRIPT TO PROCESS:\n{transcript_text}"
            }
        ]

        try:
            completion = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "project_plan",
                        "strict": True,
                        "schema": strict_schema,
                    },
                },
                temperature=0.1,
            )
        except Exception as e:
            # If strict schema fails for any model variation, retry with standard json_object
            logger.warning("Groq strict json_schema call failed (%s), retrying with json_object mode", e)
            completion = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
            )

        if not completion.choices or not completion.choices[0].message.content:
            raise ValueError("Empty response received from Groq.")

        content = completion.choices[0].message.content
        parsed_data = _clean_and_parse_json(content)
        return AIExtractedOutput.model_validate(parsed_data)

    def parse_meeting_transcript(
        self,
        transcript_text: str,
        users_directory: List[Dict[str, Any]],
    ) -> Tuple[AIExtractedOutput, str]:
        """Process transcript:
        1. Attempt Gemini (Primary).
        2. If transient failure (503, 429, timeout, connection), fallback to Groq.
        3. Returns (AIExtractedOutput, provider_name).
        """
        if not transcript_text or not transcript_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript text cannot be empty.",
            )

        # Sanitize directory
        directory_text = json.dumps(
            [
                {
                    "id": u["id"],
                    "name": u["name"],
                    "role": u["role"],
                    "specialization": u.get("specialization"),
                    "skills": u.get("skills"),
                }
                for u in users_directory
            ],
            indent=2,
        )

        prompt = f"""{SYSTEM_INSTRUCTIONS}

### VERIFIED TEAM DIRECTORY:
{directory_text}

### TRANSCRIPT TO PROCESS:
{transcript_text}
"""

        # 1. Try Gemini
        try:
            output = self._call_gemini(prompt)
            logger.info("Transcript processed successfully using primary provider: gemini")
            return output, "gemini"
        except Exception as e:
            # Check if transient error eligible for Groq fallback
            if is_transient_error(e):
                logger.warning(
                    "Gemini encountered transient error (%s: %s). Attempting fallback to Groq...",
                    type(e).__name__, str(e)[:150]
                )
                try:
                    output = self._call_groq(directory_text, transcript_text)
                    logger.info("Transcript processed successfully using fallback provider: groq")
                    return output, "groq"
                except Exception as groq_err:
                    logger.error(
                        "Groq fallback also failed (%s: %s).",
                        type(groq_err).__name__, str(groq_err)[:150]
                    )
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="AI providers are temporarily unavailable. Please try again.",
                    )
            else:
                # Non-transient error (e.g. invalid application data or unconfigured client)
                logger.error("Gemini non-transient failure: %s", type(e).__name__)
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="AI output did not match expected Project/Task validation schema.",
                )


ai_service = AIService()
