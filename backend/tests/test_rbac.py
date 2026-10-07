"""Automated test suite for Phase 2 - Role-Based Access Control (RBAC)
and Validation Rules.

Tests:
1. Admin can list all projects.
2. Manager can only list their projects.
3. Agent can only list projects related to their tasks.
4. Manager cannot directly access another manager's project.
5. Agent cannot directly access another agent's task.
6. Agent cannot access an unrelated project.
7. Unauthenticated users receive 401.
8. Password hashes never appear in API responses.
9. Validation rules for projects and tasks.
10. Cleans up test fixtures after run.
"""
import sys
import os
from pathlib import Path

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.database import SessionLocal
from app.db.models import User, Project, Task, UserRole
from app.db.seed import run_seed

client = TestClient(app)


def get_token(email: str, password: str = "Demo123!") -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def run_tests():
    print("=" * 60)
    print("RUNNING RBAC & VALIDATION TEST SUITE")
    print("=" * 60)

    # Make sure DB is seeded
    run_seed()
    db: Session = SessionLocal()

    # Retrieve existing seeded users
    admin_user = db.query(User).filter(User.email == "admin@novaworks.example").first()
    ayesha_mgr = db.query(User).filter(User.email == "ayesha@novaworks.example").first()
    bilal_mgr = db.query(User).filter(User.email == "bilal@novaworks.example").first()
    ali_agent = db.query(User).filter(User.email == "ali@novaworks.example").first()
    hamza_agent = db.query(User).filter(User.email == "hamza@novaworks.example").first()
    sara_agent = db.query(User).filter(User.email == "sara@novaworks.example").first()

    assert admin_user and ayesha_mgr and bilal_mgr and ali_agent and hamza_agent and sara_agent

    admin_token = get_token("admin@novaworks.example")
    ayesha_token = get_token("ayesha@novaworks.example")
    bilal_token = get_token("bilal@novaworks.example")
    ali_token = get_token("ali@novaworks.example")
    hamza_token = get_token("hamza@novaworks.example")
    sara_token = get_token("sara@novaworks.example")

    created_project_ids = []
    created_task_ids = []

    try:
        # ------------------------------------------------------------------
        # Setup temporary test records
        # Project 1: Managed by Ayesha
        # Tasks in P1: Task 1 (assigned to Ali), Task 2 (assigned to Hamza)
        # Project 2: Managed by Bilal
        # Tasks in P2: Task 3 (assigned to Hamza)
        # Project 3: Managed by Bilal (No tasks)
        # Sara has NO tasks in any project.
        # ------------------------------------------------------------------
        print("\n[Setup] Creating test projects and tasks...")
        
        # Test Project 1
        p1_res = client.post(
            "/api/projects",
            json={
                "name": "Test UrbanCart",
                "client_name": "Urban Retail Inc",
                "description": "E-commerce platform",
                "manager_id": ayesha_mgr.id,
                "deadline": "2026-10-20",
            },
            headers=auth_header(admin_token),
        )
        assert p1_res.status_code == 201, p1_res.text
        p1 = p1_res.json()
        created_project_ids.append(p1["id"])

        # Test Project 2
        p2_res = client.post(
            "/api/projects",
            json={
                "name": "Test QuickServe",
                "client_name": "QuickServe Logistics",
                "description": "Logistics portal",
                "manager_id": bilal_mgr.id,
                "deadline": "2026-11-15",
            },
            headers=auth_header(admin_token),
        )
        assert p2_res.status_code == 201, p2_res.text
        p2 = p2_res.json()
        created_project_ids.append(p2["id"])

        # Test Task 1 in P1 (Ali)
        t1_res = client.post(
            "/api/tasks",
            json={
                "project_id": p1["id"],
                "title": "Setup PostgreSQL Schema",
                "description": "Define DB tables and Alembic",
                "assignee_id": ali_agent.id,
                "deadline": "2026-10-15",
                "estimated_hours": 8.0,
            },
            headers=auth_header(admin_token),
        )
        assert t1_res.status_code == 201, t1_res.text
        t1 = t1_res.json()
        created_task_ids.append(t1["id"])

        # Test Task 2 in P1 (Hamza)
        t2_res = client.post(
            "/api/tasks",
            json={
                "project_id": p1["id"],
                "title": "Build Payment Integration",
                "description": "Stripe and checkout flow",
                "assignee_id": hamza_agent.id,
                "deadline": "2026-10-18",
                "estimated_hours": 12.0,
            },
            headers=auth_header(admin_token),
        )
        assert t2_res.status_code == 201, t2_res.text
        t2 = t2_res.json()
        created_task_ids.append(t2["id"])

        # Test Task 3 in P2 (Hamza)
        t3_res = client.post(
            "/api/tasks",
            json={
                "project_id": p2["id"],
                "title": "Dispatch API Service",
                "description": "Tracking endpoints",
                "assignee_id": hamza_agent.id,
                "deadline": "2026-11-10",
                "estimated_hours": 10.0,
            },
            headers=auth_header(admin_token),
        )
        assert t3_res.status_code == 201, t3_res.text
        t3 = t3_res.json()
        created_task_ids.append(t3["id"])

        print("  Created 2 test projects and 3 test tasks successfully.")

        # ------------------------------------------------------------------
        # Test 1: Admin can list all projects
        # ------------------------------------------------------------------
        print("\n[Test 1] Admin listing all projects...")
        res = client.get("/api/projects", headers=auth_header(admin_token))
        assert res.status_code == 200
        p_ids = [p["id"] for p in res.json()]
        assert p1["id"] in p_ids and p2["id"] in p_ids
        print(f"  PASS: Admin sees all projects ({len(p_ids)} total)")

        # ------------------------------------------------------------------
        # Test 2: Manager can only list their projects
        # ------------------------------------------------------------------
        print("\n[Test 2] Manager (Ayesha) listing projects...")
        res_ayesha = client.get("/api/projects", headers=auth_header(ayesha_token))
        assert res_ayesha.status_code == 200
        ayesha_projects = res_ayesha.json()
        ayesha_p_ids = [p["id"] for p in ayesha_projects]
        assert p1["id"] in ayesha_p_ids
        assert p2["id"] not in ayesha_p_ids
        for p in ayesha_projects:
            assert p["manager"]["id"] == ayesha_mgr.id
        print("  PASS: Ayesha only sees project managed by her (Test UrbanCart)")

        # ------------------------------------------------------------------
        # Test 3: Agent can only list projects related to their tasks
        # ------------------------------------------------------------------
        print("\n[Test 3] Agent project visibility...")
        # Ali only has tasks in P1
        res_ali = client.get("/api/projects", headers=auth_header(ali_token))
        assert res_ali.status_code == 200
        ali_p_ids = [p["id"] for p in res_ali.json()]
        assert p1["id"] in ali_p_ids
        assert p2["id"] not in ali_p_ids
        print("  PASS: Ali only sees P1 (UrbanCart)")

        # Hamza has tasks in both P1 and P2
        res_hamza = client.get("/api/projects", headers=auth_header(hamza_token))
        assert res_hamza.status_code == 200
        hamza_p_ids = [p["id"] for p in res_hamza.json()]
        assert p1["id"] in hamza_p_ids
        assert p2["id"] in hamza_p_ids
        print("  PASS: Hamza sees both P1 and P2 spanning his tasks")

        # Sara has no tasks in any project
        res_sara = client.get("/api/projects", headers=auth_header(sara_token))
        assert res_sara.status_code == 200
        assert len(res_sara.json()) == 0
        print("  PASS: Sara (no tasks) sees 0 projects")

        # ------------------------------------------------------------------
        # Test 4: Manager cannot directly access another manager's project
        # ------------------------------------------------------------------
        print("\n[Test 4] Cross-manager direct access protection...")
        # Ayesha tries to access Bilal's project P2
        res_ayesha_p2 = client.get(f"/api/projects/{p2['id']}", headers=auth_header(ayesha_token))
        assert res_ayesha_p2.status_code == 404, f"Expected 404, got {res_ayesha_p2.status_code}"
        print("  PASS: Ayesha accessing Bilal's project receives 404 Not Found")

        # Bilal tries to access Ayesha's project P1
        res_bilal_p1 = client.get(f"/api/projects/{p1['id']}", headers=auth_header(bilal_token))
        assert res_bilal_p1.status_code == 404, f"Expected 404, got {res_bilal_p1.status_code}"
        print("  PASS: Bilal accessing Ayesha's project receives 404 Not Found")

        # ------------------------------------------------------------------
        # Test 5: Agent cannot directly access another agent's task
        # ------------------------------------------------------------------
        print("\n[Test 5] Cross-agent direct task access protection...")
        # Ali tries to directly access Hamza's task T2
        res_ali_t2 = client.get(f"/api/tasks/{t2['id']}", headers=auth_header(ali_token))
        assert res_ali_t2.status_code == 404, f"Expected 404, got {res_ali_t2.status_code}"
        print("  PASS: Ali accessing Hamza's task receives 404 Not Found")

        # Ali accessing his own task T1 succeeds
        res_ali_t1 = client.get(f"/api/tasks/{t1['id']}", headers=auth_header(ali_token))
        assert res_ali_t1.status_code == 200
        assert res_ali_t1.json()["id"] == t1["id"]
        print("  PASS: Ali accessing his own task succeeds")

        # Ali via GET /api/projects/{p1['id']} sees ONLY his own tasks!
        res_p1_detail = client.get(f"/api/projects/{p1['id']}", headers=auth_header(ali_token))
        assert res_p1_detail.status_code == 200
        p1_tasks = res_p1_detail.json()["tasks"]
        assert len(p1_tasks) == 1
        assert p1_tasks[0]["id"] == t1["id"]
        print("  PASS: Ali's project detail view contains ONLY Ali's assigned task")

        # ------------------------------------------------------------------
        # Test 6: Agent cannot access an unrelated project
        # ------------------------------------------------------------------
        print("\n[Test 6] Agent accessing unrelated project...")
        # Ali tries to access P2 (where he has no tasks)
        res_ali_p2 = client.get(f"/api/projects/{p2['id']}", headers=auth_header(ali_token))
        assert res_ali_p2.status_code == 404, f"Expected 404, got {res_ali_p2.status_code}"
        print("  PASS: Ali accessing P2 receives 404 Not Found")

        # Sara tries to access P1 or P2
        res_sara_p1 = client.get(f"/api/projects/{p1['id']}", headers=auth_header(sara_token))
        assert res_sara_p1.status_code == 404
        print("  PASS: Sara accessing P1 receives 404 Not Found")

        # ------------------------------------------------------------------
        # Test 7: GET /api/tasks/my
        # ------------------------------------------------------------------
        print("\n[Test 7] GET /api/tasks/my endpoint...")
        res_my_hamza = client.get("/api/tasks/my", headers=auth_header(hamza_token))
        assert res_my_hamza.status_code == 200
        hamza_my_tasks = res_my_hamza.json()
        assert len(hamza_my_tasks) == 2
        task_titles = [t["title"] for t in hamza_my_tasks]
        assert "Build Payment Integration" in task_titles
        assert "Dispatch API Service" in task_titles
        for t in hamza_my_tasks:
            assert "project_name" in t and t["project_name"] is not None
        print(f"  PASS: /api/tasks/my returned {len(hamza_my_tasks)} tasks with project_name for Hamza")

        # ------------------------------------------------------------------
        # Test 8: Unauthenticated access receives 401
        # ------------------------------------------------------------------
        print("\n[Test 8] Unauthenticated requests receive 401...")
        assert client.get("/api/projects").status_code == 401
        assert client.get(f"/api/projects/{p1['id']}").status_code == 401
        assert client.get("/api/tasks").status_code == 401
        assert client.get("/api/tasks/my").status_code == 401
        assert client.get("/api/users").status_code == 401
        print("  PASS: All protected endpoints reject unauthenticated access with 401")

        # ------------------------------------------------------------------
        # Test 9: Password hashes never appear in API responses
        # ------------------------------------------------------------------
        print("\n[Test 9] Security: Password hashes never exposed...")
        user_list_res = client.get("/api/users", headers=auth_header(admin_token))
        assert user_list_res.status_code == 200
        for u in user_list_res.json():
            assert "password" not in u and "password_hash" not in u
        
        project_res = client.get("/api/projects", headers=auth_header(admin_token))
        for p in project_res.json():
            if p.get("manager"):
                assert "password" not in p["manager"] and "password_hash" not in p["manager"]

        task_res = client.get("/api/tasks", headers=auth_header(admin_token))
        for t in task_res.json():
            if t.get("assignee"):
                assert "password" not in t["assignee"] and "password_hash" not in t["assignee"]

        print("  PASS: No passwords or password_hashes found in any API responses")

        # ------------------------------------------------------------------
        # Test 10: Validation rules
        # ------------------------------------------------------------------
        print("\n[Test 10] Validation rules...")
        # 10a. Manager creating project should be 403 (Admin only)
        mgr_proj_res = client.post(
            "/api/projects",
            json={"name": "P", "client_name": "C"},
            headers=auth_header(ayesha_token),
        )
        assert mgr_proj_res.status_code == 403
        print("  PASS: Non-admin creation rejected with 403 Forbidden")

        # 10b. Project manager must be a MANAGER (not an AGENT)
        bad_mgr_res = client.post(
            "/api/projects",
            json={
                "name": "Invalid PM Project",
                "client_name": "Client",
                "manager_id": ali_agent.id,  # Ali is an AGENT!
            },
            headers=auth_header(admin_token),
        )
        assert bad_mgr_res.status_code == 400
        assert "not a MANAGER" in bad_mgr_res.text
        print("  PASS: Assigning AGENT as manager rejected with 400")

        # 10c. Task assignee must be an AGENT (not a MANAGER)
        bad_assignee_res = client.post(
            "/api/tasks",
            json={
                "project_id": p1["id"],
                "title": "Invalid Assignee Task",
                "assignee_id": ayesha_mgr.id,  # Ayesha is a MANAGER!
            },
            headers=auth_header(admin_token),
        )
        assert bad_assignee_res.status_code == 400
        assert "not an AGENT" in bad_assignee_res.text
        print("  PASS: Assigning MANAGER as task assignee rejected with 400")

        # 10d. Estimated hours must be > 0
        bad_hours_res = client.post(
            "/api/tasks",
            json={
                "project_id": p1["id"],
                "title": "Zero Hours Task",
                "assignee_id": ali_agent.id,
                "estimated_hours": 0.0,
            },
            headers=auth_header(admin_token),
        )
        assert bad_hours_res.status_code == 400 or bad_hours_res.status_code == 422
        print("  PASS: estimated_hours <= 0 rejected with 400/422")

        # 10e. Task deadline after project deadline
        # P1 deadline is 2026-10-20. Try task deadline 2026-10-25
        late_task_res = client.post(
            "/api/tasks",
            json={
                "project_id": p1["id"],
                "title": "Late Task",
                "assignee_id": ali_agent.id,
                "deadline": "2026-10-25",
                "estimated_hours": 5.0,
            },
            headers=auth_header(admin_token),
        )
        assert late_task_res.status_code == 400
        assert "cannot be after project deadline" in late_task_res.text
        print("  PASS: Task deadline after project deadline rejected with 400")

    finally:
        # Clean up test records
        print("\n[Teardown] Cleaning up test projects and tasks...")
        for t_id in created_task_ids:
            task = db.query(Task).filter(Task.id == t_id).first()
            if task:
                db.delete(task)
        for p_id in created_project_ids:
            proj = db.query(Project).filter(Project.id == p_id).first()
            if proj:
                db.delete(proj)
        db.commit()
        db.close()
        print("  Teardown complete. Database returned to initial seed state.")

    print("\n" + "=" * 60)
    print("ALL RBAC & VALIDATION TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
