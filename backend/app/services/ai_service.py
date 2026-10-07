"""AI Service for OpenRouter LLM interactions (Foundation stub).
To be extended in the AI phase.
"""
from typing import Dict, Any, Optional
from app.core.config import settings


class AIService:
    """Wrapper for OpenRouter / LLM calls."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL

    async def parse_meeting_transcript(self, transcript_text: str) -> Dict[str, Any]:
        """Placeholder for OpenRouter transcript parsing.
        Never send user passwords or sensitive credentials here.
        """
        # Will be implemented in the AI transcript processing step
        return {
            "status": "not_implemented",
            "message": "AI Transcript parsing service ready for OpenRouter integration."
        }


ai_service = AIService()
