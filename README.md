# AI Project Manager - Meeting to Execution

An AI-powered Project Manager CRM built for **NovaWorks Technologies** that automatically transforms raw, unstructured meeting transcripts into structured, validated projects and technical delivery tasks with role-based access control.

---

## Team

1. [TEAM MEMBER 1 - Zia Ul Mustafa]
2. [TEAM MEMBER 2 - Muhammad Taha]
3. [TEAM MEMBER 3 - Syed Muhammad Hussnain Raza]

---

## Problem

Client delivery planning meetings at NovaWorks Technologies involve dense technical discussions, budget/effort debates, mid-meeting scope corrections, and out-of-scope feature rejections. Manually parsing these conversations into project management systems is error-prone and time-consuming, often resulting in:

- Missed or misallocated task assignments.
- Incorrect deadline commitments.
- Scope creep from rejected or postponed discussions mistakenly recorded as deliverables.
- Inaccurate hourly effort estimates.

---

## Solution

**NovaWorks AI Project Manager** automates the entire planning-to-execution pipeline:

1. An **Administrator** logs into the CRM.
2. Pastes raw meeting notes or full transcripts into the **Create from Transcript** portal.
3. The backend calls **Google Gemini** (Primary AI Provider) using native structured JSON output.
4. If a transient infrastructure failure occurs (HTTP 503, HTTP 429, timeout, connection drop), the system automatically falls back to **Groq** using strict JSON Schema mode.
5. Both AI providers receive an identical, sanitized team directory to assign only real employees without hallucinating team members.
6. The extracted plan is validated against **Pydantic** schemas and database business rules (manager roles, agent roles, positive hours, deadline alignment).
7. Projects and tasks are persisted to the database in a **single atomic transaction**.
8. Users view their authorized data strictly enforced by backend **Role-Based Access Control (RBAC)**.

---

## Key Features

- **JWT Authentication**: Secure login with bcrypt password hashing and token management.
- **Backend-Enforced RBAC**: Authorization validated on API routes, preventing horizontal privilege escalation.
- **Admin Dashboard**: Workspace overview with real-time project counts, task counts, and active team accounts.
- **Team Directory**: Filterable directory of all 10 verified NovaWorks team members displaying specialization and skills.
- **Role-Scoped Project Views**:
  - Administrators view all projects across all managers.
  - Managers view only projects they personally manage.
  - Agents access project details strictly scoped to their assigned tasks.
- **Focused Agent Task View (`/my-tasks`)**: Dedicated view for developers showing task descriptions, project names, hourly estimates, and deadlines.
- **Dual-Provider AI Transcript Engine**:
  - **Primary**: Google Gemini (`gemini-3.5-flash-lite`).
  - **Fallback**: Groq (`openai/gpt-oss-20b`).
- **Sanitized Directory Ingestion**: AI prompts only receive public employee attributes (`id`, `name`, `role`, `specialization`, `skills`). Never passwords, hashes, or tokens.
- **Strict Structured Outputs**: Guarantees identical JSON contracts regardless of provider.
- **Multi-Layer Validation**: Pydantic schema validation followed by database constraint checks.
- **Atomic Database Transactions**: Automatic rollback if any project, task, or foreign key check fails.
- **Persistent Data**: SQLite for local development, ready for hosted PostgreSQL (Supabase).
- **Responsive Web UI**: Built with React 19, Tailwind CSS v4, and Vite with clean loading, success, and error states.

---

## AI Workflow

```text
Meeting Transcript
        ↓
FastAPI Backend
        ↓
Google Gemini (Primary: gemini-3.5-flash-lite)
        ↓ (On HTTP 503 / 429 / timeout / connection failure)
Groq Fallback (Fallback: openai/gpt-oss-20b)
        ↓
Structured JSON
        ↓
Pydantic Validation (Type safety & constraints)
        ↓
Business & DB Validation (Manager role, Agent role, Deadlines, Hours > 0)
        ↓
SQLAlchemy Transaction (Atomic commit or rollback)
        ↓
Persistent Database (Projects + Tasks + Transcripts)
        ↓
Role-Based Frontend (Admin / Manager / Agent)
```

### Team Directory Privacy & Grounding

To prevent the model from inventing non-existent employees, the backend injects a sanitized team directory into the AI system context:

- `id`
- `name`
- `role` (`ADMIN`, `MANAGER`, `AGENT`)
- `specialization`
- `skills`

**Security Boundary**: Password hashes, JWT secrets, emails, and API keys are strictly excluded from AI prompts.

---

## Technology Stack

### Backend

- **Runtime**: Python 3.11+
- **Framework**: FastAPI (`>=0.110.0`)
- **Server**: Uvicorn (`>=0.29.0`)
- **ORM**: SQLAlchemy (`>=2.0.28`)
- **Validation**: Pydantic v2 (`>=2.6.4`) & Pydantic Settings (`>=2.2.1`)
- **Authentication**: PyJWT (`>=2.8.0`) with Passlib/Bcrypt (`>=4.1.2`)
- **HTTP Client**: HTTPX (`>=0.27.0`)
- **Database**: SQLite (local development) / PostgreSQL ready (Supabase)

### Frontend

- **Framework**: React 19 (`^19.2.8`) & React DOM (`^19.2.8`)
- **Build Tool**: Vite (`^8.3.0`)
- **Language**: TypeScript (`~6.0.2`)
- **Styling**: Tailwind CSS v4 (`^4.3.3`) via `@tailwindcss/vite`
- **Routing**: React Router DOM (`^7.18.4`)
- **HTTP Client**: Axios (`^1.20.0`)
- **Icons**: Lucide React (`^1.52.0`)

### AI Integration

- **Primary Provider**: Google Gemini (`google-genai>=1.0.0`, Model: `gemini-3.5-flash-lite`)
- **Fallback Provider**: Groq (`groq>=0.9.0`, Model: `openai/gpt-oss-20b`)

---

## Architecture

```text
infinity-wave/
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI route controllers (auth, projects, tasks, transcripts, users)
│   │   ├── core/                # Configuration settings & JWT security utilities
│   │   ├── db/                  # Database session, SQLAlchemy models & seed data
│   │   ├── dependencies/        # Auth guards & role-based access dependencies
│   │   ├── schemas/             # Pydantic request/response & AI extraction contracts
│   │   ├── services/            # Business logic (AI orchestration, transcript pipeline, RBAC queries)
│   │   └── main.py              # Application entrypoint, CORS & lifespan handler
│   ├── tests/
│   │   ├── challenge_transcript.txt    # Official 60-minute hackathon transcript
│   │   ├── test_rbac.py                # Automated RBAC & authorization suite
│   │   ├── test_transcript.py          # Deterministic transcript & fallback mock suite
│   │   ├── test_real_ai.py             # Live Gemini & Groq integration tests
│   │   └── test_frontend_integration.py# End-to-end API client contract tests
│   ├── requirements.txt         # Backend Python dependencies
│   ├── .env.example             # Backend environment template
│   └── README.md                # Backend technical guide
├── frontend/
│   ├── src/
│   │   ├── components/layout/   # AppLayout sidebar and navigation
│   │   ├── context/             # AuthContext (JWT session management)
│   │   ├── pages/               # Admin, Manager, Agent, and Project views
│   │   ├── services/            # Axios API client & typed endpoints
│   │   ├── types/               # Authoritative TypeScript data interfaces
│   │   ├── App.tsx              # Role-protected route definitions
│   │   ├── index.css            # Tailwind CSS v4 directives & font imports
│   │   └── main.tsx             # Application bootstrap
│   ├── package.json             # Frontend dependencies & scripts
│   ├── tsconfig.json            # TypeScript configuration
│   ├── vite.config.ts           # Vite build configuration
│   └── .env.example             # Frontend environment template
├── .env.example                 # Root environment template
├── .gitignore                   # Git exclusion rules (strictly ignores .env)
└── README.md                    # Project documentation
```

---

## Role-Based Access

| Role | Access Permissions | UI Views |
| --- | --- | --- |
| **ADMIN** | Full visibility into all projects and tasks. Can view team directory and process meeting transcripts. | `/admin` (Dashboard), `/admin/transcript`, `/projects`, `/team` |
| **MANAGER** | Can only view projects where `project.manager_id == current_user.id` and tasks belonging to those projects. Unauthorized access returns `404 Not Found`. | `/manager` (My Projects), `/projects`, `/projects/:id` |
| **AGENT** | Can only view tasks assigned to `current_user.id`. Project detail view (`/projects/:id`) displays only the agent's assigned tasks. | `/my-tasks` (Focused Task List), `/projects/:id` |

> **Note**: Authorization is strictly enforced by the FastAPI backend on every request. Client-side routing serves solely for user experience.

---

## Demo Accounts

All demo accounts are seeded with password: `Demo123!`

| Role | Name | Email | Password | Specialization |
| --- | --- | --- | --- | --- |
| **Admin** | Admin | `admin@novaworks.example` | `Demo123!` | System Administrator |
| **Manager** | Ayesha Khan | `ayesha@novaworks.example` | `Demo123!` | E-Commerce & Mobile Delivery PM |
| **Manager** | Bilal Ahmed | `bilal@novaworks.example` | `Demo123!` | Fintech & Core Banking PM |
| **Manager** | Hina Malik | `hina@novaworks.example` | `Demo123!` | Healthcare & Analytics PM |
| **Agent** | Ali Raza | `ali@novaworks.example` | `Demo123!` | Backend Engineering |
| **Agent** | Hamza Shah | `hamza@novaworks.example` | `Demo123!` | Full Stack & API Engineering |
| **Agent** | Sara Noor | `sara@novaworks.example` | `Demo123!` | Frontend Engineering |
| **Agent** | Usman Tariq | `usman@novaworks.example` | `Demo123!` | DevOps & Cloud Architecture |
| **Agent** | Zain Abbas | `zain@novaworks.example` | `Demo123!` | QA & Test Automation |
| **Agent** | Maryam Asif | `maryam@novaworks.example` | `Demo123!` | UI/UX Design & Frontend |

---

## Local Setup

### 1. Clone Repository

```bash
git clone https://github.com/Syed-Muhammad-Hussnain-Raza/infinity-wave.git
cd infinity-wave
```

### 2. Backend Setup

Create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

Configure backend environment variables:

```bash
# Copy root environment template
cp .env.example .env
```

Edit `.env` to configure your API keys (never commit this file):

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
DATABASE_URL=sqlite:///./novaworks.db
SECRET_KEY=novaworks_super_secret_hackathon_key_2026_dev_only
```

Initialize database & seed demo accounts:

```bash
# Seeding is idempotent and automatically verified on startup
python -m backend.app.db.seed
```

### 3. Frontend Setup

In a new terminal window:

```bash
cd frontend
npm install
```

Configure frontend environment variables:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Verify `frontend/.env` contains:

```env
VITE_API_URL=http://127.0.0.1:8000
```

---

## Environment Variables

| Variable | Purpose | Location |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database connection string (SQLite locally, PostgreSQL hosted) | Backend (`.env`) |
| `SECRET_KEY` | Secret key for signing JWT tokens | Backend (`.env`) |
| `ALGORITHM` | JWT signing algorithm (default: `HS256`) | Backend (`.env`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiration window for access tokens (default: `480`) | Backend (`.env`) |
| `GEMINI_API_KEY` | Google AI Studio API key for primary extraction | Backend (`.env` only) |
| `GEMINI_MODEL` | Gemini model name (default: `gemini-3.5-flash-lite`) | Backend (`.env`) |
| `GROQ_API_KEY` | Groq API key for transient fallback extraction | Backend (`.env` only) |
| `GROQ_MODEL` | Groq model name (default: `openai/gpt-oss-20b`) | Backend (`.env`) |
| `ALLOWED_ORIGINS` | Permitted CORS frontend origins | Backend (`.env`) |
| `VITE_API_URL` | Base URL pointing to the FastAPI backend | Frontend (`frontend/.env`) |

> **Security Warning**: Never commit `.env` files. Both root `.gitignore` and `frontend/.gitignore` exclude `.env` files from version control. AI provider keys belong exclusively to the backend.

---

## Running the Application

### Start Backend Server

From the repository root with your virtual environment active:

```bash
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

### Start Frontend Application

In a separate terminal window:

```bash
cd frontend
npm run dev
```

- Web Application: `http://localhost:5173`

---

## AI Transcript Demo

1. Open `http://localhost:5173/login`.
2. Click the quick login button for **Admin** (`admin@novaworks.example` / `Demo123!`) and click **Sign in**.
3. In the sidebar, click **Create from Transcript** (`/admin/transcript`).
4. Paste the official meeting transcript (located at [`backend/tests/challenge_transcript.txt`](file:///d:/InfinityWave/infinity-wave/backend/tests/challenge_transcript.txt)).
5. Click **Generate CRM Data →**.
6. The AI analyzes the transcript, handles mid-meeting corrections, respects rejected features, and commits the result.
7. The interface displays the success summary:
   - **Projects Created**: `3`
   - **Tasks Assigned**: `12`
   - **Provider**: `gemini` (or `groq` if fallback was triggered)
8. Click **View All Projects →** to inspect the generated records.

### Expected Official Transcript Output

- **UrbanCart Website** (Client: UrbanCart Clothing, Manager: Ayesha Khan, Deadline: `2026-10-20`):
  - Product catalog UI (Assignee: Ali Raza, 12h, Deadline: `2026-10-12`)
  - Demo cart UI (Assignee: Ali Raza, 8h, Deadline: `2026-10-15`)
  - Product and cart APIs (Assignee: Hamza Shah, 14h, Deadline: `2026-10-14`)
  - Website integration and testing (Assignee: Ali Raza, 6h, Deadline: `2026-10-19`)
  - *Total Effort: 40 hours*
- **QuickServe Mobile App** (Client: QuickServe Services, Manager: Bilal Ahmed, Deadline: `2026-10-24`):
  - Login and profile screens (Assignee: Sara Noor, 8h, Deadline: `2026-10-12`)
  - Service booking screens (Assignee: Sara Noor, 12h, Deadline: `2026-10-17`)
  - Booking and account APIs (Assignee: Hamza Shah, 16h, Deadline: `2026-10-16`)
  - Mobile integration and testing (Assignee: Usman Tariq, 10h, Deadline: `2026-10-22`)
  - *Total Effort: 46 hours*
- **HelpDeskPro AI Assistant** (Client: HelpDeskPro Solutions, Manager: Hina Malik, Deadline: `2026-10-22`):
  - FAQ document processing (Assignee: Maryam Asif, 10h, Deadline: `2026-10-13`)
  - Assistant answer generation (Assignee: Zain Abbas, 14h, Deadline: `2026-10-17`)
  - Human escalation flow (Assignee: Zain Abbas, 6h, Deadline: `2026-10-18`)
  - Assistant evaluation and testing (Assignee: Maryam Asif, 8h, Deadline: `2026-10-21`)
  - *Total Effort: 38 hours*

---

## Role-Based Demo

### 1. Admin Verification

- **Login**: `admin@novaworks.example` / `Demo123!`
- Has full workspace visibility. Can view all 3 projects, all 12 tasks, team directory, and submit transcripts.

### 2. Manager Verification (Ayesha Khan)

- **Sign out** and log in as `ayesha@novaworks.example` / `Demo123!`.
- Redirected to `/manager` (My Projects).
- **Result**: Only **UrbanCart Website** is visible. Bilal's and Hina's projects are completely hidden. Direct access to `/projects/2` returns `404 Not Found`.

### 3. Agent Verification (Ali Raza)

- **Sign out** and log in as `ali@novaworks.example` / `Demo123!`.
- Redirected to `/my-tasks`.
- **Result**: Displays only Ali's 3 assigned tasks across UrbanCart. Tasks assigned to Hamza, Sara, Usman, Zain, and Maryam are hidden.

### 4. Cross-Project Agent Verification (Hamza Shah)

- **Sign out** and log in as `hamza@novaworks.example` / `Demo123!`.
- Redirected to `/my-tasks`.
- **Result**: Displays his 2 tasks spanning across separate client projects:
  - *Product and cart APIs* under **UrbanCart Website**
  - *Booking and account APIs* under **QuickServe Mobile App**

---

## API Overview

### Authentication

- `POST /api/auth/login` - Authenticate with email/password (supports JSON and form-data for Swagger); returns JWT access token and user profile.
- `GET /api/auth/me` - Retrieve current authenticated user profile.

### Team Directory

- `GET /api/users` - Retrieve directory of team members (supports `?role=` filter). Excludes sensitive credentials.

### Projects

- `GET /api/projects` - Role-scoped project retrieval with `task_count` summary.
- `GET /api/projects/{project_id}` - Role-scoped project detail including authorized tasks (returns 404 on unauthorized).
- `POST /api/projects` - Create a project manually (Admin only).

### Tasks

- `GET /api/tasks` - Role-scoped task retrieval (supports `?project_id=` filter).
- `GET /api/tasks/my` - Focused task list for the current authenticated user with project name.
- `GET /api/tasks/{task_id}` - Single task lookup (returns 404 on unauthorized).
- `POST /api/tasks` - Create a task manually (Admin only).

### AI Transcript Ingestion

- `POST /api/transcripts/process` - Admin-only endpoint that ingests meeting text, orchestrates Gemini/Groq extraction, runs schema validations, and atomically commits projects and tasks.

---

## Testing

The backend includes comprehensive automated test suites that run offline and offline-mocked:

### 1. Deterministic Transcript & Fallback Tests

Verifies Gemini success, Groq fallback on transient errors (503, 429, timeout, connection drop), non-fallback on Pydantic validation errors, directory sanitization, and atomic rollbacks.

```bash
python backend/tests/test_transcript.py
```

*Result: 100% Passed (12 test scenarios)*

### 2. Role-Based Access Control (RBAC) Tests

Verifies Admin, Manager, and Agent isolation, task filtering, creation rules, and constraint enforcement.

```bash
python backend/tests/test_rbac.py
```

*Result: 100% Passed (14 test scenarios)*

### 3. API Contract Integration Tests

Verifies end-to-end integration between frontend query expectations and backend endpoints.

```bash
python backend/tests/test_frontend_integration.py
```

*Result: 100% Passed*

### 4. Live AI Verification Suite

Tests live extraction directly against both Gemini and Groq with simulated 503 fallback routing (requires valid API keys in `.env`).

```bash
python backend/tests/test_real_ai.py
```

*Result: 100% Passed*

### 5. Frontend Production Build Verification

Verifies zero TypeScript errors, zero CSS warnings, and clean bundle generation:

```bash
cd frontend
npm run build
```

*Result: 100% Passed (`tsc -b && vite build` completed in ~320ms)*

---

## Deployment

### Infrastructure Target

- **Backend**: Render
- **Database**: Supabase PostgreSQL
- **Frontend**: [TO BE ADDED]

### Live Links

- **Live Demo**: [TO BE ADDED]
- **Demo Video**: [TO BE ADDED]

---

## Security

- **Stateless JWT Tokens**: Cryptographically signed access tokens using HMAC-SHA256.
- **Server-Side Authorization**: Every route evaluates `get_current_user` and role requirements; the UI never dictates permissions.
- **Credential Hygiene**: Password hashes (`bcrypt`) are strictly stripped before returning user entities over the API.
- **AI Privacy Fence**: Prompts contain only sanitized directory metadata (`id`, `name`, `role`, `specialization`, `skills`). Never passwords, hashes, tokens, or emails.
- **No Client Secrets**: AI keys exist strictly in backend server environment variables and are never bundled into client JS.
- **Git Protection**: `.env` is strictly ignored in version control.

---

## Known Limitations

- **Demo Credentials**: Authentication uses pre-seeded mock accounts designed specifically for the hackathon challenge evaluation.
- **AI Provider Quotas**: Free-tier API keys may encounter rate limits; the automated Groq fallback mitigates transient outages.
- **MVP Scope**: Post-creation editing (updating tasks, reassigning owners, budget tracking) is omitted in this MVP phase to focus on reliable transcript ingestion.

---

## Hackathon MVP Scope

This application is an MVP intentionally focused on the core challenge loop:
$$\text{Meeting Transcript} \longrightarrow \text{AI Extraction} \longrightarrow \text{Project Creation} \longrightarrow \text{Task Assignment} \longrightarrow \text{Role-Based Viewing}$$

Advanced enterprise capabilities (timesheets, resource capacity planning, billing, interactive Gantt charts) are outside the scope of this hackathon submission.

---

## License

Built for Infinity Hack '26.
