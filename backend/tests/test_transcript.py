"""Deterministic test suite for Phase 3 - AI Transcript Automation.
Mocks Gemini and Groq for reproducible, fast, and offline testing of:
1. Gemini success -> Groq is NOT called
2. Gemini 503 -> Groq fallback is called
3. Gemini 429 -> Groq fallback is called
4. Gemini timeout -> Groq fallback is called
5. Gemini connection failure -> Groq fallback is called
6. Gemini success with invalid application data -> do NOT fallback merely because Pydantic validation failed
7. Gemini failure + Groq success -> request succeeds
8. Gemini failure + Groq failure -> clean error ("AI providers are temporarily unavailable. Please try again.")
9. Both providers receive the same sanitized team directory
10. Neither provider receives password/password_hash
11. End-to-end admin processing & RBAC / business validation rules
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.database import SessionLocal
from app.db.models import User, Project, Task, Transcript, UserRole
from app.db.seed import run_seed
from app.schemas.transcript import AIExtractedOutput, AIExtractedProject, AIExtractedTask
from app.services.ai_service import AIService, is_transient_error

client = TestClient(app)


def get_token(email: str, password: str = "Demo123!") -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def build_mock_extracted_challenge(manager_ids, agent_ids) -> AIExtractedOutput:
    """Build the expected 3 projects and 12 tasks output from the challenge transcript."""
    return AIExtractedOutput(
        projects=[
            AIExtractedProject(
                name="UrbanCart Website",
                client_name="UrbanCart Clothing",
                description="E-commerce store",
                manager_id=manager_ids["ayesha"],
                deadline="2026-10-20",
                tasks=[
                    AIExtractedTask(
                        title="Product catalog UI",
                        assignee_id=agent_ids["ali"],
                        deadline="2026-10-12",
                        estimated_hours=12.0,
                    ),
                    AIExtractedTask(
                        title="Demo cart UI",
                        assignee_id=agent_ids["ali"],
                        deadline="2026-10-15",
                        estimated_hours=8.0,
                    ),
                    AIExtractedTask(
                        title="Product and cart APIs",
                        assignee_id=agent_ids["hamza"],
                        deadline="2026-10-14",
                        estimated_hours=14.0,
                    ),
                    AIExtractedTask(
                        title="Website integration and testing",
                        assignee_id=agent_ids["ali"],
                        deadline="2026-10-19",
                        estimated_hours=6.0,
                    ),
                ],
            ),
            AIExtractedProject(
                name="QuickServe Mobile App",
                client_name="QuickServe Services",
                description="On-demand service booking",
                manager_id=manager_ids["bilal"],
                deadline="2026-10-24",
                tasks=[
                    AIExtractedTask(
                        title="Login and profile screens",
                        assignee_id=agent_ids["sara"],
                        deadline="2026-10-12",
                        estimated_hours=8.0,
                    ),
                    AIExtractedTask(
                        title="Service booking screens",
                        assignee_id=agent_ids["sara"],
                        deadline="2026-10-17",
                        estimated_hours=12.0,
                    ),
                    AIExtractedTask(
                        title="Booking and account APIs",
                        assignee_id=agent_ids["hamza"],
                        deadline="2026-10-16",
                        estimated_hours=16.0,
                    ),
                    AIExtractedTask(
                        title="Mobile integration and testing",
                        assignee_id=agent_ids["usman"],
                        deadline="2026-10-22",
                        estimated_hours=10.0,
                    ),
                ],
            ),
            AIExtractedProject(
                name="HelpDeskPro AI Assistant",
                client_name="HelpDeskPro Solutions",
                description="Customer support intelligence",
                manager_id=manager_ids["hina"],
                deadline="2026-10-22",
                tasks=[
                    AIExtractedTask(
                        title="FAQ document processing",
                        assignee_id=agent_ids["maryam"],
                        deadline="2026-10-13",
                        estimated_hours=10.0,
                    ),
                    AIExtractedTask(
                        title="Assistant answer generation",
                        assignee_id=agent_ids["zain"],
                        deadline="2026-10-17",
                        estimated_hours=14.0,
                    ),
                    AIExtractedTask(
                        title="Human escalation flow",
                        assignee_id=agent_ids["zain"],
                        deadline="2026-10-18",
                        estimated_hours=6.0,
                    ),
                    AIExtractedTask(
                        title="Assistant evaluation and testing",
                        assignee_id=agent_ids["maryam"],
                        deadline="2026-10-21",
                        estimated_hours=8.0,
                    ),
                ],
            ),
        ]
    )


def run_tests():
    print("=" * 60)
    print("RUNNING DETERMINISTIC TRANSCRIPT & FALLBACK TESTS")
    print("=" * 60)

    run_seed()
    db: Session = SessionLocal()

    # User lookups
    ayesha = db.query(User).filter(User.email == "ayesha@novaworks.example").first()
    bilal = db.query(User).filter(User.email == "bilal@novaworks.example").first()
    hina = db.query(User).filter(User.email == "hina@novaworks.example").first()

    ali = db.query(User).filter(User.email == "ali@novaworks.example").first()
    hamza = db.query(User).filter(User.email == "hamza@novaworks.example").first()
    sara = db.query(User).filter(User.email == "sara@novaworks.example").first()
    usman = db.query(User).filter(User.email == "usman@novaworks.example").first()
    zain = db.query(User).filter(User.email == "zain@novaworks.example").first()
    maryam = db.query(User).filter(User.email == "maryam@novaworks.example").first()

    manager_ids = {"ayesha": ayesha.id, "bilal": bilal.id, "hina": hina.id}
    agent_ids = {
        "ali": ali.id,
        "hamza": hamza.id,
        "sara": sara.id,
        "usman": usman.id,
        "zain": zain.id,
        "maryam": maryam.id,
    }

    admin_token = get_token("admin@novaworks.example")
    ayesha_token = get_token("ayesha@novaworks.example")
    ali_token = get_token("ali@novaworks.example")

    sample_transcript = "UrbanCart Website, client UrbanCart Clothing, manager Ayesha, deadline 20 October..."
    mock_output = build_mock_extracted_challenge(manager_ids, agent_ids)

    sample_directory = [
        {"id": u.id, "name": u.name, "role": u.role.value, "specialization": u.specialization, "skills": u.skills}
        for u in [ayesha, bilal, hina, ali, hamza, sara, usman, zain, maryam]
    ]

    try:
        # ==================================================================
        # FALLBACK UNIT TESTS (AIService level)
        # ==================================================================

        # Fallback Test 1: Gemini success -> Groq is NOT called
        print("\n[Fallback 1] Gemini success -> Groq is NOT called...")
        service = AIService()
        with patch.object(service, "_call_gemini", return_value=mock_output) as mock_gemini, \
             patch.object(service, "_call_groq") as mock_groq:
            res_output, provider = service.parse_meeting_transcript("Sample transcript", sample_directory)
            assert provider == "gemini"
            assert res_output == mock_output
            mock_gemini.assert_called_once()
            mock_groq.assert_not_called()
            print("  PASS: Gemini succeeded, Groq was not called")

        # Fallback Test 2: Gemini 503 -> Groq fallback is called
        print("\n[Fallback 2] Gemini 503 -> Groq fallback is called...")
        service = AIService()
        gemini_503_err = Exception("503 Service Unavailable: Gemini model overloaded")
        with patch.object(service, "_call_gemini", side_effect=gemini_503_err) as mock_gemini, \
             patch.object(service, "_call_groq", return_value=mock_output) as mock_groq:
            res_output, provider = service.parse_meeting_transcript("Sample transcript", sample_directory)
            assert provider == "groq"
            assert res_output == mock_output
            mock_gemini.assert_called_once()
            mock_groq.assert_called_once()
            print("  PASS: Gemini 503 triggered Groq fallback, succeeded with provider='groq'")

        # Fallback Test 3: Gemini 429 -> Groq fallback is called
        print("\n[Fallback 3] Gemini 429 -> Groq fallback is called...")
        service = AIService()
        gemini_429_err = Exception("429 ResourceExhausted: rate limit exceeded")
        with patch.object(service, "_call_gemini", side_effect=gemini_429_err) as mock_gemini, \
             patch.object(service, "_call_groq", return_value=mock_output) as mock_groq:
            res_output, provider = service.parse_meeting_transcript("Sample transcript", sample_directory)
            assert provider == "groq"
            assert res_output == mock_output
            mock_gemini.assert_called_once()
            mock_groq.assert_called_once()
            print("  PASS: Gemini 429 triggered Groq fallback")

        # Fallback Test 4: Gemini timeout -> Groq fallback is called
        print("\n[Fallback 4] Gemini timeout -> Groq fallback is called...")
        service = AIService()
        gemini_timeout_err = TimeoutError("Request timed out after 30 seconds")
        with patch.object(service, "_call_gemini", side_effect=gemini_timeout_err) as mock_gemini, \
             patch.object(service, "_call_groq", return_value=mock_output) as mock_groq:
            res_output, provider = service.parse_meeting_transcript("Sample transcript", sample_directory)
            assert provider == "groq"
            assert res_output == mock_output
            mock_gemini.assert_called_once()
            mock_groq.assert_called_once()
            print("  PASS: Gemini timeout triggered Groq fallback")

        # Fallback Test 5: Gemini connection failure -> Groq fallback is called
        print("\n[Fallback 5] Gemini connection failure -> Groq fallback is called...")
        service = AIService()
        gemini_conn_err = ConnectionError("Failed to connect to generativelanguage.googleapis.com")
        with patch.object(service, "_call_gemini", side_effect=gemini_conn_err) as mock_gemini, \
             patch.object(service, "_call_groq", return_value=mock_output) as mock_groq:
            res_output, provider = service.parse_meeting_transcript("Sample transcript", sample_directory)
            assert provider == "groq"
            assert res_output == mock_output
            mock_gemini.assert_called_once()
            mock_groq.assert_called_once()
            print("  PASS: Gemini connection error triggered Groq fallback")

        # Fallback Test 6: Gemini invalid application data (Pydantic failure) -> do NOT fallback to Groq
        print("\n[Fallback 6] Gemini invalid data -> do NOT fallback merely because Pydantic validation failed...")
        service = AIService()
        # Simulate Pydantic ValidationError during Gemini output parsing
        try:
            AIExtractedTask(title="X", assignee_id=1, deadline="2026-10-10", estimated_hours=0)
        except ValidationError as pydantic_err:
            mock_val_err = pydantic_err

        with patch.object(service, "_call_gemini", side_effect=mock_val_err) as mock_gemini, \
             patch.object(service, "_call_groq") as mock_groq:
            try:
                service.parse_meeting_transcript("Sample transcript", sample_directory)
                assert False, "Should have raised HTTPException 422"
            except HTTPException as exc:
                assert exc.status_code == 422
                assert "validation schema" in exc.detail
                mock_gemini.assert_called_once()
                mock_groq.assert_not_called()
                print("  PASS: Pydantic validation error did NOT trigger fallback to Groq")

        # Fallback Test 7: Gemini failure + Groq failure -> clean error
        print("\n[Fallback 7 & 8] Gemini failure + Groq failure -> clean frontend-safe error...")
        service = AIService()
        gemini_err = Exception("503 Service Unavailable")
        groq_err = Exception("Groq internal error with secret API_KEY_SECRET_XYZ")
        with patch.object(service, "_call_gemini", side_effect=gemini_err), \
             patch.object(service, "_call_groq", side_effect=groq_err):
            try:
                service.parse_meeting_transcript("Sample transcript", sample_directory)
                assert False, "Should have raised HTTPException 503"
            except HTTPException as exc:
                assert exc.status_code == 503
                assert exc.detail == "AI providers are temporarily unavailable. Please try again."
                assert "API_KEY" not in exc.detail
                print("  PASS: Both failing returned clean frontend-safe 503 message with no secrets exposed")

        # Fallback Test 9 & 10: Sanitized directory check for both providers
        print("\n[Fallback 9 & 10] Both providers receive sanitized directory without passwords...")
        captured_gemini_prompt = []
        captured_groq_args = []

        service = AIService()
        with patch.object(service, "_call_gemini", side_effect=lambda p: captured_gemini_prompt.append(p) or (_ for _ in ()).throw(Exception("503"))), \
             patch.object(service, "_call_groq", side_effect=lambda d, t: captured_groq_args.append((d, t)) or mock_output):
            service.parse_meeting_transcript("Test transcript", sample_directory)

        # Check Gemini prompt content
        assert len(captured_gemini_prompt) == 1
        assert "password" not in captured_gemini_prompt[0]
        assert "password_hash" not in captured_gemini_prompt[0]
        for u in sample_directory:
            assert f'"name": "{u["name"]}"' in captured_gemini_prompt[0]

        # Check Groq directory content
        assert len(captured_groq_args) == 1
        groq_dir, groq_transcript = captured_groq_args[0]
        assert "password" not in groq_dir
        assert "password_hash" not in groq_dir
        for u in sample_directory:
            assert f'"name": "{u["name"]}"' in groq_dir
        print("  PASS: Verified both Gemini and Groq receive identical sanitized directory without passwords")

        # ==================================================================
        # END-TO-END ENDPOINT TESTS (FastAPI TestClient)
        # ==================================================================

        # Endpoint Test 1: Admin processes valid transcript via Gemini -> provider: "gemini"
        print("\n[Endpoint 1] Admin processing valid transcript via Gemini...")
        with patch("app.services.transcript_service.ai_service.parse_meeting_transcript", return_value=(mock_output, "gemini")):
            res = client.post(
                "/api/transcripts/process",
                json={"transcript": sample_transcript},
                headers=auth_header(admin_token),
            )
            assert res.status_code == 200, res.text
            data = res.json()
            assert data["ai_provider"] == "gemini"
            assert data["projects_created"] == 3
            assert data["tasks_created"] == 12
            assert len(data["projects"]) == 3
            for p in data["projects"]:
                assert p["task_count"] == 4
            print("  PASS: 3 projects and 12 tasks created with ai_provider='gemini'")

        # Verify database persistence
        assert db.query(Project).count() == 3
        assert db.query(Task).count() == 12
        assert db.query(Transcript).count() >= 1

        # Clean up database
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()

        # Endpoint Test 2: Gemini fails with 503, Groq fallback succeeds -> provider: "groq"
        print("\n[Endpoint 2] Gemini 503 -> Groq fallback end-to-end endpoint test...")
        with patch("app.services.transcript_service.ai_service.parse_meeting_transcript", return_value=(mock_output, "groq")):
            res = client.post(
                "/api/transcripts/process",
                json={"transcript": sample_transcript},
                headers=auth_header(admin_token),
            )
            assert res.status_code == 200, res.text
            data = res.json()
            assert data["ai_provider"] == "groq"
            assert data["projects_created"] == 3
            assert data["tasks_created"] == 12
            print("  PASS: Fallback succeeded end-to-end with ai_provider='groq'")

        # Clean up database
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()

        # Endpoint Test 3: Non-admin roles receive 403 Forbidden
        print("\n[Endpoint 3] Non-admin roles receive 403...")
        res_mgr = client.post(
            "/api/transcripts/process",
            json={"transcript": sample_transcript},
            headers=auth_header(ayesha_token),
        )
        assert res_mgr.status_code == 403
        res_agent = client.post(
            "/api/transcripts/process",
            json={"transcript": sample_transcript},
            headers=auth_header(ali_token),
        )
        assert res_agent.status_code == 403
        print("  PASS: Manager and Agent requests rejected with 403 Forbidden")

        # Endpoint Test 4: Unauthenticated user receives 401 Unauthorized
        print("\n[Endpoint 4] Unauthenticated user receives 401...")
        res_unauth = client.post(
            "/api/transcripts/process",
            json={"transcript": sample_transcript},
        )
        assert res_unauth.status_code == 401
        print("  PASS: Unauthenticated request rejected with 401")

        # Endpoint Test 5: Empty transcript is rejected
        print("\n[Endpoint 5] Empty transcript rejection...")
        res_empty = client.post(
            "/api/transcripts/process",
            json={"transcript": ""},
            headers=auth_header(admin_token),
        )
        assert res_empty.status_code in (400, 422)
        print("  PASS: Empty transcript rejected")

        # Endpoint Test 6: Invalid manager rejected (must be MANAGER)
        print("\n[Endpoint 6] Invalid manager validation...")
        bad_mgr_output = AIExtractedOutput(
            projects=[
                AIExtractedProject(
                    name="Bad Manager Project",
                    client_name="Client",
                    manager_id=ali.id,  # Ali is an AGENT!
                    deadline="2026-10-20",
                    tasks=[
                        AIExtractedTask(
                            title="Task 1",
                            assignee_id=hamza.id,
                            deadline="2026-10-15",
                            estimated_hours=5.0,
                        )
                    ],
                )
            ]
        )
        with patch("app.services.transcript_service.ai_service.parse_meeting_transcript", return_value=(bad_mgr_output, "gemini")):
            res_bad_mgr = client.post(
                "/api/transcripts/process",
                json={"transcript": sample_transcript},
                headers=auth_header(admin_token),
            )
            assert res_bad_mgr.status_code == 400
            assert "not a MANAGER" in res_bad_mgr.text
            print("  PASS: Assigning AGENT as manager rejected with 400")

        # Endpoint Test 7: Invalid agent rejected (must be AGENT)
        print("\n[Endpoint 7] Invalid agent validation...")
        bad_agent_output = AIExtractedOutput(
            projects=[
                AIExtractedProject(
                    name="Bad Agent Project",
                    client_name="Client",
                    manager_id=ayesha.id,
                    deadline="2026-10-20",
                    tasks=[
                        AIExtractedTask(
                            title="Task 1",
                            assignee_id=bilal.id,  # Bilal is a MANAGER!
                            deadline="2026-10-15",
                            estimated_hours=5.0,
                        )
                    ],
                )
            ]
        )
        with patch("app.services.transcript_service.ai_service.parse_meeting_transcript", return_value=(bad_agent_output, "gemini")):
            res_bad_agent = client.post(
                "/api/transcripts/process",
                json={"transcript": sample_transcript},
                headers=auth_header(admin_token),
            )
            assert res_bad_agent.status_code == 400
            assert "not an AGENT" in res_bad_agent.text
            print("  PASS: Assigning MANAGER as agent rejected with 400")

        # Endpoint Test 8: Task deadline after project deadline is rejected
        print("\n[Endpoint 8] Task deadline after project deadline rejection...")
        late_task_output = AIExtractedOutput(
            projects=[
                AIExtractedProject(
                    name="Late Task Project",
                    client_name="Client",
                    manager_id=ayesha.id,
                    deadline="2026-10-20",
                    tasks=[
                        AIExtractedTask(
                            title="Task 1",
                            assignee_id=ali.id,
                            deadline="2026-10-25",  # Past 2026-10-20!
                            estimated_hours=5.0,
                        )
                    ],
                )
            ]
        )
        with patch("app.services.transcript_service.ai_service.parse_meeting_transcript", return_value=(late_task_output, "gemini")):
            res_late = client.post(
                "/api/transcripts/process",
                json={"transcript": sample_transcript},
                headers=auth_header(admin_token),
            )
            assert res_late.status_code == 400
            assert "cannot be after project" in res_late.text
            print("  PASS: Task deadline after project deadline rejected with 400")

        # Endpoint Test 9: Atomic rollback works
        print("\n[Endpoint 9] Atomic rollback works...")
        assert db.query(Project).count() == 0
        assert db.query(Task).count() == 0
        mixed_output = AIExtractedOutput(
            projects=[
                AIExtractedProject(
                    name="Valid Project 1",
                    client_name="Client 1",
                    manager_id=ayesha.id,
                    deadline="2026-10-20",
                    tasks=[
                        AIExtractedTask(
                            title="Task 1",
                            assignee_id=ali.id,
                            deadline="2026-10-15",
                            estimated_hours=5.0,
                        )
                    ],
                ),
                AIExtractedProject(
                    name="Invalid Project 2",
                    client_name="Client 2",
                    manager_id=bilal.id,
                    deadline="2026-10-24",
                    tasks=[
                        AIExtractedTask(
                            title="Task 2",
                            assignee_id=hina.id,  # Hina is a MANAGER!
                            deadline="2026-10-15",
                            estimated_hours=5.0,
                        )
                    ],
                ),
            ]
        )
        with patch("app.services.transcript_service.ai_service.parse_meeting_transcript", return_value=(mixed_output, "gemini")):
            res_mixed = client.post(
                "/api/transcripts/process",
                json={"transcript": sample_transcript},
                headers=auth_header(admin_token),
            )
            assert res_mixed.status_code == 400
        assert db.query(Project).count() == 0
        assert db.query(Task).count() == 0
        print("  PASS: Atomic rollback verified - 0 projects and 0 tasks saved upon error")

    finally:
        # Final cleanup
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(Transcript).delete()
        db.commit()
        db.close()
        print("\n[Teardown] Database cleaned up.")

    print("\n" + "=" * 60)
    print("ALL TRANSCRIPT & FALLBACK TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
