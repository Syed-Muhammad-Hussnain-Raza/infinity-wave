# NovaWorks AI Project Manager - Backend

A clean, high-performance FastAPI backend foundation for NovaWorks AI Project Manager CRM.

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
      user.py            # User read/create/update schemas (no password leak)
      project.py         # Project schemas with relations
      task.py            # Task schemas with assignee info
      transcript.py      # Transcript extraction schemas
    api/
      auth.py            # /api/auth/login, /api/auth/me
      users.py           # /api/users (team directory)
      projects.py        # /api/projects
      tasks.py           # /api/tasks
      transcripts.py     # /api/transcripts/process stub
    services/
      auth_service.py    # Authentication & user creation business logic
      project_service.py # Role-based project and task queries
      transcript_service.py # Transcript persistence logic
      ai_service.py      # OpenRouter AI integration stub
    dependencies/
      auth.py            # get_current_user & role-based authorization guards
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

---

## Demo Accounts

All accounts use password: `Demo123!`

| Role | Name | Email | Password |
| --- | --- | --- | --- |
| Admin | Admin | `admin@novaworks.example` | `Demo123!` |
| Manager | Ayesha Khan | `ayesha@novaworks.example` | `Demo123!` |
| Manager | Bilal Ahmed | `bilal@novaworks.example` | `Demo123!` |
| Manager | Hina Malik | `hina@novaworks.example` | `Demo123!` |
| Agent | Ali Raza | `ali@novaworks.example` | `Demo123!` |
| Agent | Hamza Shah | `hamza@novaworks.example` | `Demo123!` |
| Agent | Sara Noor | `sara@novaworks.example` | `Demo123!` |
| Agent | Usman Tariq | `usman@novaworks.example` | `Demo123!` |
| Agent | Zain Abbas | `zain@novaworks.example` | `Demo123!` |
| Agent | Maryam Asif | `maryam@novaworks.example` | `Demo123!` |

---

## Implemented Foundation Endpoints

- `GET /health` - Health check status
- `POST /api/auth/login` - Authenticate and obtain JWT access token
- `GET /api/auth/me` - Authenticated user profile
- `GET /api/users` - Team directory list (supports optional `?role=` query parameter)
- `GET /api/projects` - Role-scoped project retrieval
- `POST /api/projects` - Project creation (Admin or Manager only)
- `GET /api/tasks` - Role-scoped task retrieval
- `POST /api/tasks` - Task creation (Admin or Manager only)
- `POST /api/transcripts/process` - Stub ready for OpenRouter AI processing
