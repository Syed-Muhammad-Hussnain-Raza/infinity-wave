"""Real Gemini Integration Test for Phase 3.
Only runs when GEMINI_API_KEY is configured in the environment.
DOES NOT hardcode answers; tests genuine AI processing with the official challenge transcript.
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

from app.main import app
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import User, Project, Task, Transcript
from app.db.seed import run_seed

client = TestClient(app)


def get_admin_token() -> str:
    res = client.post("/api/auth/login", json={"email": "admin@novaworks.example", "password": "Demo123!"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


def run_real_gemini_test():
    print("=" * 60)
    print("REAL GEMINI API INTEGRATION TEST")
    print("=" * 60)

    if not settings.GEMINI_API_KEY or not settings.GEMINI_API_KEY.strip():
        print("GEMINI_API_KEY configured: NO")
        print("Skipping real Gemini API integration test (no key configured).")
        return

    print("GEMINI_API_KEY configured: YES")
    print(f"GEMINI_MODEL: {settings.GEMINI_MODEL}")

    # Ensure DB is seeded
    run_seed()
    db: Session = SessionLocal()
    admin_token = get_admin_token()
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Load official challenge transcript
    transcript_path = backend_dir / "tests" / "challenge_transcript.txt"
    if not transcript_path.exists():
        print(f"ERROR: {transcript_path} not found")
        return

    with open(transcript_path, "r", encoding="utf-8") as f:
        challenge_transcript = f.read()

    try:
        # Clean up any existing projects/tasks
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()

        # ------------------------------------------------------------------
        # 1. Official Challenge Transcript Test
        # ------------------------------------------------------------------
        print("\n[Step 1] Sending official challenge transcript to /api/transcripts/process...")
        res = client.post(
            "/api/transcripts/process",
            json={"transcript": challenge_transcript},
            headers=headers,
        )

        assert res.status_code == 200, f"Processing failed ({res.status_code}): {res.text}"
        data = res.json()
        print("Response received from Gemini:")
        print(f"  Message: {data['message']}")
        print(f"  Projects created: {data['projects_created']}")
        print(f"  Tasks created: {data['tasks_created']}")

        assert data["projects_created"] == 3, f"Expected 3 projects, got {data['projects_created']}"
        assert data["tasks_created"] == 12, f"Expected 12 tasks, got {data['tasks_created']}"

        # Fetch created projects and verify details
        projects = db.query(Project).all()
        assert len(projects) == 3

        projects_by_name = {p.name.lower(): p for p in projects}

        # Verify UrbanCart
        urbancart = next((p for name, p in projects_by_name.items() if "urban" in name), None)
        assert urbancart is not None, "UrbanCart project not found"
        assert urbancart.manager.name == "Ayesha Khan", f"Expected manager Ayesha Khan, got {urbancart.manager.name}"
        assert urbancart.deadline in ("2026-10-20", "20 October 2026"), f"Unexpected deadline: {urbancart.deadline}"
        assert len(urbancart.tasks) == 4, f"Expected 4 tasks for UrbanCart, got {len(urbancart.tasks)}"
        urbancart_hours = sum(t.estimated_hours for t in urbancart.tasks)
        print(f"  UrbanCart: Manager={urbancart.manager.name}, Deadline={urbancart.deadline}, Tasks={len(urbancart.tasks)}, Total Hours={urbancart_hours}")
        assert urbancart_hours == 40.0, f"Expected 40 hours for UrbanCart, got {urbancart_hours}"

        # Verify QuickServe
        quickserve = next((p for name, p in projects_by_name.items() if "quick" in name), None)
        assert quickserve is not None, "QuickServe project not found"
        assert quickserve.manager.name == "Bilal Ahmed", f"Expected manager Bilal Ahmed, got {quickserve.manager.name}"
        assert quickserve.deadline in ("2026-10-24", "24 October 2026"), f"Unexpected deadline: {quickserve.deadline}"
        assert len(quickserve.tasks) == 4, f"Expected 4 tasks for QuickServe, got {len(quickserve.tasks)}"
        quickserve_hours = sum(t.estimated_hours for t in quickserve.tasks)
        print(f"  QuickServe: Manager={quickserve.manager.name}, Deadline={quickserve.deadline}, Tasks={len(quickserve.tasks)}, Total Hours={quickserve_hours}")
        assert quickserve_hours == 46.0, f"Expected 46 hours for QuickServe, got {quickserve_hours}"

        # Verify HelpDeskPro
        helpdesk = next((p for name, p in projects_by_name.items() if "help" in name), None)
        assert helpdesk is not None, "HelpDeskPro project not found"
        assert helpdesk.manager.name == "Hina Malik", f"Expected manager Hina Malik, got {helpdesk.manager.name}"
        assert helpdesk.deadline in ("2026-10-22", "22 October 2026"), f"Unexpected deadline: {helpdesk.deadline}"
        assert len(helpdesk.tasks) == 4, f"Expected 4 tasks for HelpDeskPro, got {len(helpdesk.tasks)}"
        helpdesk_hours = sum(t.estimated_hours for t in helpdesk.tasks)
        print(f"  HelpDeskPro: Manager={helpdesk.manager.name}, Deadline={helpdesk.deadline}, Tasks={len(helpdesk.tasks)}, Total Hours={helpdesk_hours}")
        assert helpdesk_hours == 38.0, f"Expected 38 hours for HelpDeskPro, got {helpdesk_hours}"

        print("  PASS: Official Challenge Transcript produced 3 projects, 12 tasks, and exactly expected hours (40, 46, 38)!")

        # ------------------------------------------------------------------
        # 2. Changed Input Test
        # ------------------------------------------------------------------
        print("\n[Step 2] Testing Changed Input Transcript...")
        # Clean DB before second test
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()

        # Modify transcript: change Usman's QuickServe integration task estimate to 12 hours, deadline 23 October
        modified_transcript = challenge_transcript.replace(
            "Usman owns Mobile integration and testing:\n10 hours, 22 October.",
            "Usman owns Mobile integration and testing:\n12 hours, 23 October."
        ).replace(
            "Usman owns Mobile integration and testing: 10 hours, 22 October.",
            "Usman owns Mobile integration and testing: 12 hours, 23 October."
        )

        res_mod = client.post(
            "/api/transcripts/process",
            json={"transcript": modified_transcript},
            headers=headers,
        )
        assert res_mod.status_code == 200, f"Modified processing failed: {res_mod.text}"

        # Find Usman's task in QuickServe
        mod_task = (
            db.query(Task)
            .filter(Task.title.ilike("%mobile integration%"))
            .first()
        )
        assert mod_task is not None, "Modified Mobile Integration task not found"
        print(f"  Extracted modified task: '{mod_task.title}' | Estimated Hours: {mod_task.estimated_hours} | Deadline: {mod_task.deadline}")
        assert mod_task.estimated_hours == 12.0, f"Expected 12.0 hours, got {mod_task.estimated_hours}"
        assert mod_task.deadline in ("2026-10-23", "23 October 2026"), f"Expected deadline 2026-10-23, got {mod_task.deadline}"

        print("  PASS: Genuine AI extraction verified on modified transcript (12 hours / 2026-10-23)!")

    finally:
        # Final cleanup to leave pure seed state
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()
        db.close()
        print("\n[Teardown] Database cleaned up to pure seed state.")

    print("\n" + "=" * 60)
    print("ALL REAL GEMINI TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_real_gemini_test()
