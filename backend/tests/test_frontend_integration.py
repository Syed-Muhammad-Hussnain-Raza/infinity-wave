"""Verify end-to-end API integration matching frontend contracts."""
import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    with httpx.Client(base_url=BASE_URL) as client:
        # 1. Admin Login
        res_admin = client.post("/api/auth/login", json={"email": "admin@novaworks.example", "password": "Demo123!"})
        assert res_admin.status_code == 200, res_admin.text
        admin_data = res_admin.json()
        admin_token = admin_data["access_token"]
        print("[1] Admin Login: SUCCESS, role =", admin_data["user"]["role"])

        # 2. Admin Projects
        res_p = client.get("/api/projects", headers={"Authorization": f"Bearer {admin_token}"})
        assert res_p.status_code == 200
        projects = res_p.json()
        if len(projects) == 0:
            print("  Ingesting challenge transcript...")
            with open("backend/tests/challenge_transcript.txt", "r", encoding="utf-8") as f:
                transcript_text = f.read()
            res_trans = client.post(
                "/api/transcripts/process",
                json={"transcript": transcript_text},
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=60.0,
            )
            assert res_trans.status_code == 200, res_trans.text
            res_p = client.get("/api/projects", headers={"Authorization": f"Bearer {admin_token}"})
            projects = res_p.json()

        print(f"[2] Admin Projects count: {len(projects)}")
        assert len(projects) == 3
        for p in projects:
            print(f'    - {p["name"]} (Client: {p["client_name"]}, Manager: {p["manager"]["name"]}, Tasks: {p["task_count"]})')

        # 3. Admin Team Directory
        res_u = client.get("/api/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert res_u.status_code == 200
        users = res_u.json()
        print(f"[3] Team Directory count: {len(users)}")
        assert len(users) == 10

        # 4. Manager Ayesha Login & Projects
        res_ayesha = client.post("/api/auth/login", json={"email": "ayesha@novaworks.example", "password": "Demo123!"})
        assert res_ayesha.status_code == 200
        ayesha_data = res_ayesha.json()
        ayesha_token = ayesha_data["access_token"]
        print("[4] Ayesha Login: SUCCESS, role =", ayesha_data["user"]["role"])

        res_ayesha_p = client.get("/api/projects", headers={"Authorization": f"Bearer {ayesha_token}"})
        assert res_ayesha_p.status_code == 200
        ayesha_projects = res_ayesha_p.json()
        print(f"[4b] Ayesha Projects count: {len(ayesha_projects)}")
        assert len(ayesha_projects) == 1
        assert ayesha_projects[0]["name"] == "UrbanCart Website"
        print("    - Correctly scoped to:", ayesha_projects[0]["name"])

        # 5. Agent Ali Login & Tasks
        res_ali = client.post("/api/auth/login", json={"email": "ali@novaworks.example", "password": "Demo123!"})
        assert res_ali.status_code == 200
        ali_token = res_ali.json()["access_token"]
        res_ali_t = client.get("/api/tasks/my", headers={"Authorization": f"Bearer {ali_token}"})
        assert res_ali_t.status_code == 200
        ali_tasks = res_ali_t.json()
        print(f"[5] Ali Tasks count: {len(ali_tasks)}")
        assert len(ali_tasks) == 3
        for t in ali_tasks:
            print(f'    - {t["title"]} ({t["estimated_hours"]}h, {t["deadline"]})')

        # 6. Agent Hamza Login & Tasks (Cross-project)
        res_hamza = client.post("/api/auth/login", json={"email": "hamza@novaworks.example", "password": "Demo123!"})
        assert res_hamza.status_code == 200
        hamza_token = res_hamza.json()["access_token"]
        res_hamza_t = client.get("/api/tasks/my", headers={"Authorization": f"Bearer {hamza_token}"})
        assert res_hamza_t.status_code == 200
        hamza_tasks = res_hamza_t.json()
        print(f"[6] Hamza Tasks count: {len(hamza_tasks)}")
        assert len(hamza_tasks) == 2
        for t in hamza_tasks:
            print(f'    - {t["title"]} in project "{t["project_name"]}" ({t["estimated_hours"]}h, {t["deadline"]})')

if __name__ == "__main__":
    test_flow()
    print("\nALL INTEGRATION ENDPOINTS VERIFIED SUCCESSFULLY!")
