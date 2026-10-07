"""Real AI Integration Verification for Gemini (Primary) and Groq (Fallback).
Tests:
1. Gemini directly with structured JSON
2. Groq directly with strict structured JSON
3. Simulated Gemini 503 -> Groq processes the transcript
DOES NOT print any API keys.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
load_dotenv(backend_dir / ".env")
load_dotenv(backend_dir.parent / ".env")

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from app.main import app
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import Project, Task, Transcript
from app.db.seed import run_seed
from app.services.ai_service import ai_service

client = TestClient(app)


def get_admin_token() -> str:
    res = client.post("/api/auth/login", json={"email": "admin@novaworks.example", "password": "Demo123!"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


def run_live_ai_verifications():
    print("=" * 60)
    print("LIVE AI PROVIDER VERIFICATION (GEMINI & GROQ)")
    print("=" * 60)

    # Security check: Never print API keys
    assert settings.GEMINI_API_KEY, "GEMINI_API_KEY must be set in .env"
    assert settings.GROQ_API_KEY, "GROQ_API_KEY must be set in .env"
    print(f"Primary Provider : Gemini ({settings.GEMINI_MODEL}) [Key configured: YES]")
    print(f"Fallback Provider: Groq ({settings.GROQ_MODEL}) [Key configured: YES]")

    run_seed()
    db: Session = SessionLocal()
    admin_token = get_admin_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    transcript_path = backend_dir / "tests" / "challenge_transcript.txt"
    with open(transcript_path, "r", encoding="utf-8") as f:
        challenge_transcript = f.read()

    try:
        # ------------------------------------------------------------------
        # 1. Test Gemini Directly
        # ------------------------------------------------------------------
        print("\n[Step 1] Live Gemini Direct Verification...")
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()

        # Endpoint call will route to Gemini primarily
        res_gemini = client.post(
            "/api/transcripts/process",
            json={"transcript": challenge_transcript},
            headers=headers,
        )
        assert res_gemini.status_code == 200, f"Gemini call failed ({res_gemini.status_code}): {res_gemini.text}"
        data_gemini = res_gemini.json()
        assert data_gemini.get("ai_provider") == "gemini", f"Expected provider 'gemini', got {data_gemini.get('ai_provider')}"
        assert data_gemini["projects_created"] == 3
        assert data_gemini["tasks_created"] == 12
        print(f"  PASS: Gemini direct call succeeded! Provider: {data_gemini.get('ai_provider')}, Projects: {data_gemini['projects_created']}, Tasks: {data_gemini['tasks_created']}")

        # ------------------------------------------------------------------
        # 2. Test Groq Directly (via ai_service._call_groq)
        # ------------------------------------------------------------------
        print("\n[Step 2] Live Groq Direct Verification (Strict Structured JSON)...")
        from app.db.models import User
        users = db.query(User).all()
        user_dir = [
            {"id": u.id, "name": u.name, "role": u.role.value, "specialization": u.specialization, "skills": u.skills}
            for u in users
        ]
        import json
        dir_text = json.dumps(user_dir, indent=2)

        sample_groq_transcript = (
            "UrbanCart Website for client UrbanCart Clothing. Manager is Ayesha Khan. Deadline 20 October 2026. "
            "Ali owns Product catalog UI: 12 hours, 12 October 2026. "
            "Hamza owns Product APIs: 14 hours, 14 October 2026."
        )

        groq_extracted = ai_service._call_groq(dir_text, sample_groq_transcript)
        assert len(groq_extracted.projects) >= 1, f"Expected projects from Groq, got {len(groq_extracted.projects)}"
        total_groq_tasks = sum(len(p.tasks) for p in groq_extracted.projects)
        assert total_groq_tasks >= 1, f"Expected tasks from Groq, got {total_groq_tasks}"
        print(f"  PASS: Groq direct strict JSON schema succeeded! Projects: {len(groq_extracted.projects)}, Tasks: {total_groq_tasks}")

        # ------------------------------------------------------------------
        # 3. Test Fallback Flow (Simulated Gemini 503 -> Groq Fallback)
        # ------------------------------------------------------------------
        print("\n[Step 3] Live Fallback Verification (Simulating Gemini 503 -> Real Groq)...")
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()

        # Simulate Gemini 503 while allowing Groq to call live API
        with patch.object(ai_service, "_call_gemini", side_effect=Exception("503 Service Unavailable: Gemini overloaded")):
            res_fallback = client.post(
                "/api/transcripts/process",
                json={"transcript": challenge_transcript},
                headers=headers,
            )
            assert res_fallback.status_code == 200, f"Fallback failed ({res_fallback.status_code}): {res_fallback.text}"
            data_fallback = res_fallback.json()
            assert data_fallback.get("ai_provider") == "groq", f"Expected provider 'groq', got {data_fallback.get('ai_provider')}"
            assert data_fallback["projects_created"] == 3
            assert data_fallback["tasks_created"] == 12
            print(f"  PASS: Simulated Gemini 503 successfully fell back to real Groq! Provider: {data_fallback.get('ai_provider')}, Projects: {data_fallback['projects_created']}, Tasks: {data_fallback['tasks_created']}")

        # Verify DB persisted from Groq fallback
        assert db.query(Project).count() == 3
        assert db.query(Task).count() == 12
        assert db.query(Transcript).count() >= 1
        print("  PASS: Database persistence verified from Groq fallback processing.")

    finally:
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()
        db.close()
        print("\n[Teardown] Database cleaned up to initial seed state.")

    print("\n" + "=" * 60)
    print("ALL REAL AI INTEGRATION TESTS PASSED (GEMINI & GROQ)!")
    print("=" * 60)


if __name__ == "__main__":
    run_live_ai_verifications()
