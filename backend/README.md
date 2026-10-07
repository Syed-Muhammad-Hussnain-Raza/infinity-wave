# NovaWorks AI Project Manager - Backend

A clean, high-performance FastAPI backend for NovaWorks AI Project Manager CRM.

## Tech Stack

- **Framework**: Python 3.11+, FastAPI
- **ORM & DB**: SQLAlchemy 2.0+ (SQLite fallback for local dev, PostgreSQL ready)
- **Validation**: Pydantic v2
- **Auth**: JWT (PyJWT) with bcrypt password hashing
- **Server**: Uvicorn

---

## Directory Structure

```
backend/
  app/
    __init__.py
    main.py              # FastAPI application, CORS, lifespan & router registration
    core/
      config.py          # Pydantic Settings & environment variables
      security.py        # Password hashing (bcrypt) & JWT token utilities
    db/
      database.py        # SQLAlchemy engine, session maker, get_db, init_db
      models.py          # SQLAlchemy models (User, Project, Task, Transcript)
      seed.py            # Idempotent demo accounts seeder (10 users)
    schemas/
      auth.py            # Login, token schemas
      user.py            # User read/create/update & UserSimple schemas
      project.py         # ProjectResponse & ProjectDetailResponse schemas
      task.py            # TaskResponse & MyTaskResponse schemas
      transcript.py      # Transcript extraction schemas
    api/
      auth.py            # /api/auth/login, /api/auth/me
      users.py           # /api/users (team directory)
      projects.py        # /api/projects, /api/projects/{id}
      tasks.py           # /api/tasks, /api/tasks/my, /api/tasks/{id}
      transcripts.py     # /api/transcripts/process stub
    services/
      auth_service.py    # Authentication & user creation business logic
      project_service.py # Role-based project and task queries + validations
      transcript_service.py # Transcript persistence logic
      ai_service.py      # OpenRouter AI integration stub
    dependencies/
      auth.py            # get_current_user & role-based authorization guards
  tests/
    test_rbac.py         # Comprehensive automated RBAC and validation test suite
  main.py                # Direct execution entrypoint
  requirements.txt
  .env.example
  .env
.gitignore
requirements.txt
README.md
```

---

## Quickstart (Local Setup)

### 1. Create and Activate Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Environment Configuration

Copy the example `.env` file:

```bash
cp .env.example backend/.env
```

Default values use local SQLite database `sqlite:///./novaworks.db`.

### 4. Initialize Database & Seed Demo Users

Database tables and demo accounts are automatically initialized upon application startup.
You can also manually run the seeder at any time (it is completely idempotent and will never duplicate users):

```bash
python -m backend.app.db.seed
```

### 5. Start the Server

From the repository root:

```bash
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

Or from within the `backend/` directory:

```bash
cd backend
python main.py
```

The server will be available at:

- **API URL**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/health`

### 6. Run Automated RBAC Test Suite

```bash
python backend/tests/test_rbac.py
```

---

## Demo Accounts

All accounts use password: `Demo123!`

| Role | Name | Email | Password | Specialization |
| --- | --- | --- | --- | --- |
| Admin | Admin | `admin@novaworks.example` | `Demo123!` | System Administrator |
| Manager | Ayesha Khan | `ayesha@novaworks.example` | `Demo123!` | E-Commerce & Mobile Delivery PM |
| Manager | Bilal Ahmed | `bilal@novaworks.example` | `Demo123!` | Fintech & Core Banking PM |
| Manager | Hina Malik | `hina@novaworks.example` | `Demo123!` | Healthcare & Analytics PM |
| Agent | Ali Raza | `ali@novaworks.example` | `Demo123!` | Backend Engineering |
| Agent | Hamza Shah | `hamza@novaworks.example` | `Demo123!` | Full Stack & API Engineering |
| Agent | Sara Noor | `sara@novaworks.example` | `Demo123!` | Frontend Engineering |
| Agent | Usman Tariq | `usman@novaworks.example` | `Demo123!` | DevOps & Cloud Architecture |
| Agent | Zain Abbas | `zain@novaworks.example` | `Demo123!` | QA & Test Automation |
| Agent | Maryam Asif | `maryam@novaworks.example` | `Demo123!` | UI/UX Design & Frontend |

---

## Role-Based Access Control (RBAC) Rules

- **ADMIN**:
  - Full visibility across all projects and tasks.
  - Can create projects and tasks with validation.
  - Full access to all project details and tasks.
- **MANAGER**:
  - Can only view projects where `project.manager_id == current_user.id`.
  - Can view tasks belonging to projects they manage.
  - Direct access to unauthorized projects/tasks returns `404 Not Found` (no existence leakage).
- **AGENT**:
  - Can only view projects that contain at least one task assigned to `current_user.id`.
  - Viewing project detail (`GET /api/projects/{id}`) returns **only** tasks assigned to that agent.
  - Can only view tasks assigned to `current_user.id`.
  - `/api/tasks/my` provides a focused list of the agent's tasks with `project_name`.
  - Direct access to unauthorized projects or other agents' tasks returns `404 Not Found`.

---

## Implemented Endpoints

### System & Directory

- `GET /health` - Health check status
- `GET /api/users` - Team directory list (supports optional `?role=` query parameter; no passwords/hashes)

### Authentication

- `POST /api/auth/login` - Authenticate with email/password, returns JWT token + sanitized user profile
- `GET /api/auth/me` - Authenticated user profile

### Projects

- `GET /api/projects` - Role-scoped project retrieval with `task_count`
- `GET /api/projects/{project_id}` - Role-scoped project detail including authorized tasks (404 on unauthorized)
- `POST /api/projects` - Project creation (Admin only)

### Tasks

- `GET /api/tasks` - Role-scoped task retrieval (supports optional `?project_id=` filter)
- `GET /api/tasks/my` - Focused task list for the current authenticated user (with `project_name`)
- `GET /api/tasks/{task_id}` - Single task lookup (404 on unauthorized)
- `POST /api/tasks` - Task creation (Admin only)

### Transcripts

- `POST /api/transcripts/process` - Stub ready for OpenRouter AI processing (Admin only)
