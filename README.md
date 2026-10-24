# RekhaCB — AI-Powered HR Automation

RekhaCB brings everyday HR tasks and an AI assistant into one workspace. Employees can find policy information, explore leave plans, check their records, and prepare requests. Managers can review their team's requests and approve them through the same HR system.

Built as an AI engineering capstone, RekhaCB extends the **CB Nest starter provided by Codebasics**. The original HRMS supplies the business records and APIs; the capstone adds policy retrieval, permission-controlled data queries, confirmed actions, and **Request Readiness**.

> New to the codebase? Start with the [Learner Guide](docs/Learner_Guide.md) for the starter architecture, database, and code walkthrough. For the Copilot additions, see the [AI architecture](docs/ai_architecture.md).

## What makes it different

**Request Readiness** helps an employee understand a leave request before submitting it:

**Plan → Check → Compare → Prepare → Confirm**

- Review six checks: balance, overlapping requests, dates, pending commitments, approval path, and policy evidence.
- Preview requested days and the projected remaining balance.
- Pin one plan and compare another set of dates or a half-day option.
- Read an approver brief with the reason, balance impact, warnings, and policy references.
- Export a JSON review snapshot with a fingerprint for identifying the reviewed information.
- Refresh checks when preparing and confirming the request.

Readiness calculations use application rules and HR records. A language model does not decide the employee's leave balance. A review or exported fingerprint is not an approval or a digital signature.

## Features

| Area | What you can do |
| --- | --- |
| Policy assistant | Ask HR policy questions and inspect retrieved source references |
| People and projects | Query permitted employee, skill, project, and assignment information |
| HR actions | Prepare supported actions, review the details, and confirm execution |
| Leave workflow | Check balances, plan leave, submit requests, and review decisions |
| Manager workspace | Review and decide leave requests for direct reports |
| Support tickets | Create a ticket through chat and find it in the Tickets module |
| Existing HRMS | Use profiles, documents, attendance, calendars, announcements, polls, policies, and finance screens |

Available actions depend on the signed-in user's role. Unsupported operations can be performed through the regular HRMS screens where permitted.

### Core HRMS modules

- JWT authentication with ADMIN, MANAGER, and EMPLOYEE roles.
- Employee directory with search, filters, and pagination.
- Attendance clock-in and clock-out with work-mode tracking.
- Leave balances, applications, and approval workflows.
- Announcements, polls, and notifications.
- Team calendar with leave, WFH, holidays, and upcoming birthdays.
- Profile editing, profile photos, job history, and employee documents.
- Finance views for salary, statutory information, and payroll history.
- Ticket assignment, status updates, and onboarding tasks.
- HR policy upload and download library.
- Employee document search, viewing, and downloading; self-deletion is limited to the `OTHER` document type.
- Password-protected PDF payslips using DOB in `DD-MM-YY` format.
- Notifications for supported announcements, polls, tickets, leave decisions, and documents uploaded by others.

The implemented Copilot endpoints extend the starter's AI contracts; they are no longer described as unimplemented `501` stubs.

## Technology

| Layer | Stack |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Database | SQLite with aiosqlite |
| Policy RAG | Semantic embeddings, persistent SQLite vector index and cosine search; offline TF-IDF baseline |
| Optional AI providers | OpenAI-compatible embeddings and chat-completions APIs |
| Authentication | JWT and backend role checks |

## Quick start with Docker

Use Docker Desktop with Compose v2. On Windows, enable the WSL 2 backend. Run these commands from the complete project root:

```powershell
Copy-Item backend/.env.example backend/.env
```

Edit `backend/.env` and replace the example JWT secret before starting. The backend rejects missing secrets, `change_me`, and secrets shorter than 32 characters. Generate a random value and paste it into `JWT_SECRET_KEY`:

```powershell
py -3.12 -c "import secrets; print(secrets.token_urlsafe(48))"
```

```powershell
docker compose up -d --build
docker compose exec api python -m alembic upgrade head
docker compose exec api python scripts/seed.py
docker compose exec api python scripts/seed_rekha.py
docker compose ps
```

Open http://localhost:3000/login. API documentation is available at http://localhost:8000/docs and http://localhost:8000/redoc.

**The seed script resets business data. Use it only for initial setup or a deliberate reset.** For later starts, use `docker compose up -d`.

## Run locally in VS Code

Install **Python 3.12**, **Node.js 22**, and Git if you plan to clone the repository. Open the complete `RekhaCB` folder in VS Code.

### 1. Backend — first-time setup

Open a PowerShell terminal from the project root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` and replace `JWT_SECRET_KEY=change_me` with a long random secret. Keep this file private.

Then initialize the database:

```powershell
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe scripts/seed.py
.\.venv\Scripts\python.exe scripts/seed_rekha.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

**Run `seed.py` only for initial setup or a deliberate reset. It resets HRMS business data.** `seed_rekha.py` adds the fictional demonstration handbook and can be rerun.

These commands call the virtual environment's Python directly, so PowerShell activation is unnecessary.

### 2. Frontend — second terminal

Keep the backend terminal running. Open another terminal from the project root:

```powershell
cd frontend
npm.cmd ci
Copy-Item .env.example .env.local
npm.cmd run dev
```

The frontend example uses `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`.

Open:

- Website: http://localhost:3000/login
- Copilot: http://localhost:3000/ai-copilot
- API documentation: http://localhost:8000/docs

### Start again after closing VS Code

In the backend terminal:

```powershell
cd backend
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

In the frontend terminal:

```powershell
cd frontend
npm.cmd run dev
```

Do not recreate the environment or reseed the database for a normal restart.

## Demo accounts

These accounts contain fictional demonstration data.

| Role | Email | Password |
| --- | --- | --- |
| Employee | employee@mock-hrms.dev | password123 |
| Manager | manager@mock-hrms.dev | password123 |
| Admin | admin@mock-hrms.dev | password123 |

Use these credentials only for the local demo.

## Configuration

Backend settings are stored in `backend/.env`; use `backend/.env.example` as the reference.

```dotenv
APP_NAME=RekhaCB
APP_TIMEZONE=Asia/Kolkata
DATABASE_URL=sqlite+aiosqlite:///./storage/rekhacb.db
JWT_SECRET_KEY=replace-with-a-long-random-secret
```

The frontend uses `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`. JWT expiry and upload-directory settings are also defined in the backend environment example.

Do not commit `.env` files, API keys, SQLite databases, virtual environments, generated build folders, or `node_modules`.

## AI configuration

### Local mode — no API key

Policy search returns relevant excerpts with source references. Data queries use a limited set of templates, and actions support a constrained range of phrases and identifiers. This mode is useful for a reproducible demonstration, but it is not a general conversational language model.

### Model-assisted mode

Set the following in `backend/.env`:

```dotenv
AI_API_KEY=your-provider-key
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4.1-mini
```

Use a compatible provider and a model available in your account, then restart the backend. This enables model-assisted policy answers, SQL generation, and action extraction.

Relevant prompts and policy evidence can be sent to the configured provider. Use approved demonstration data and keep API keys out of GitHub. Live provider behaviour requires separate evaluation; the recorded automated checks did not use a live provider.

## A short demo to try

1. Sign in as the employee and open **RekhaCB Copilot → Request Readiness**.
2. Choose unused future leave dates, a leave type, and a reason.
3. Check readiness, pin the plan, and compare a shorter option.
4. Prepare the checked request, review it, and confirm submission.
5. Open **Leaves** and note the number in the **ID** column. This is the leave request ID, not the employee ID.
6. Sign in as the seeded manager. In **HR actions**, enter `Approve leave <request ID>` using the actual numeric ID.
7. Review and confirm the proposal, then verify the updated status in Leaves.

Other example prompts:

```text
Can I take a half-day leave?
Show my project assignments
Check my leave balance
Create a ticket for VPN connection failure
Show all employee salaries
```

The salary query should be refused because salary fields are excluded from the Copilot's query dataset. Select **Policy library**, **People & projects**, or **HR actions** explicitly if automatic routing chooses the wrong mode.

## Permissions and action handling

- SQL runs against a separate, disposable database projection containing permitted rows and safe columns.
- Employees receive their own employee-related rows; managers receive their own rows and direct reports; admins have broader access to the permitted dataset.
- Passwords, bank details, PAN information, and salaries are excluded from this projection, including for admins.
- Queries are restricted to read-only operations with execution and result limits.
- Actions use the existing authenticated backend APIs rather than directly writing HR business tables.
- Confirmation proposals belong to the signed-in user, expire after five minutes, and can be used only once.
- Audit metadata records the user, route, tool, status, and redacted interaction information.

Regular HRMS screens have their own permissions. The Copilot's data boundary is separate.

## Implementation details

Policy documents are split into overlapping chunks. Semantic mode generates embeddings and stores them in a persistent SQLite vector index. Policy content, source metadata, provider and model changes invalidate the index snapshot automatically. Queries use exact cosine search with source references. Auto mode uses semantic retrieval when an API key is configured; without a key, it uses the offline TF-IDF baseline.

Action execution uses an internal HTTP ASGI transport to call the existing JWT-authenticated FastAPI endpoints. Business validation and role checks remain in those endpoints. The Copilot stores confirmation and audit metadata in `storage/copilot.db`; it does not directly write HR business records.

## Project structure

```text
RekhaCB/
├── backend/             # FastAPI application, migrations, scripts, tests
├── frontend/            # Next.js application and public assets
├── docs/                # Architecture, permissions, evaluation, walkthrough
└── docker-compose.yml   # Optional Docker setup
```

The backend includes API endpoints, models, schemas, services, Alembic migrations, seed scripts, and tests. Copilot services live under `backend/app/services/ai/`; the frontend Copilot workspace is under `frontend/app/ai-copilot/`.

## Common Docker commands

```powershell
# Start services
docker compose up -d

# Restart services
docker compose restart api web

# Stop services
docker compose down

# Apply database migrations
docker compose exec api python -m alembic upgrade head

# Inspect logs
docker compose logs --tail 100 api web
```

For dependency or image changes, rebuild with `docker compose up -d --build`. Back up any data you need before deliberately reseeding or resetting the database.

## API notes

- Base path: `/api/v1`.
- Health checks: `/health` and `/api/v1/health`.
- Copilot routes: `POST /api/v1/chat/policy`, `/chat/sql`, `/chat/actions`, and `/chat/router` under the same API base.
- Request Readiness: `POST /api/v1/readiness/analyze` and `POST /api/v1/readiness/prepare`.
- Employee self-upload: `POST /api/v1/employees/me/documents`.
- Employee self-delete: `DELETE /api/v1/employees/me/documents/{document_id}`, limited to `OTHER` documents.
- Staff document and payslip uploads use employee-specific routes and backend role checks.

Standard response format:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

Errors use `success: false` with an error code and message. See the running API documentation for endpoint schemas and authentication requirements.

## Documentation

- [Learner Guide](docs/Learner_Guide.md)
- [Product requirements](docs/PRD.md)
- [Database reference](docs/db_tables_samples.md)
- [AI architecture](docs/ai_architecture.md)
- [Copilot permissions](docs/ai_permissions_matrix.md)
- [Evaluation results](docs/ai_eval_results.md)
- [Demo walkthrough](docs/demo_walkthrough.md)
- API reference material: `docs/api/`

Documentation links require the accompanying project files to be present in the repository.

## Verification

The recorded build-environment checks included **39 passing backend tests** and a successful frontend production build. These are previous recorded results, not a claim that tests were rerun for this README update.

After initial migration and seeding, run from `backend`:

```powershell
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m pytest -q
```

From `frontend`:

```powershell
npm.cmd run typecheck
npm.cmd run build
```

Coverage includes retrieval, query restrictions, role permissions, confirmation handling, and request flows. Tests copy the seeded business database into a temporary directory rather than creating test requests in the running application's database. See the evaluation document for the recorded evidence and limits.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `No suitable Python runtime found` | Install Python 3.12 and check that `py -3.12 --version` works before creating the environment |
| PowerShell blocks `npm.ps1` | Use `npm.cmd` as shown above |
| Virtual environment activation is blocked | Call `.\.venv\Scripts\python.exe` directly |
| Python path includes `backend\backend` | If already inside `backend`, use `.\.venv\Scripts\python.exe` |
| Website cannot reach the API | Keep the backend running on port 8000 and check the frontend API base URL |
| Manager cannot approve a request | Use the actual pending leave request ID and confirm the employee is a direct report |

## Limitations

This is a local capstone application. Local mode understands limited phrasing, and model-assisted output can be incorrect. Leave calculations follow the starter application's calendar-day rules, including weekends. Pending requests do not reserve leave balance.

There is a gap between readiness validation and the final business write. Production work should strengthen transactional validation and idempotency, and add rate limiting, operational monitoring, production session management, and provider evaluations.

## Demo video

[Watch the RekhaCB capstone project demo on YouTube](https://www.youtube.com/watch?v=tkBHs0jMX-k)

## Credits

Capstone project by **Kartik Mishra**, built on the **Codebasics CB Nest starter**. Original copyright notices and applicable terms remain in effect. No additional open-source license is granted by this README.

Copyright (c) Codebasics. All rights reserved.

## Confirmation retries

A confirmation is claimed immediately before API dispatch, blocking concurrent duplicate execution. Confirmed validation or authorization rejections release the claim so it can be retried within its original five-minute lifetime; correct changed details by preparing a new proposal. Successful submissions cannot be replayed. Connection failures, server errors, or a process crash during dispatch can leave the outcome uncertain: check the HRMS record before preparing another request. This does not provide transactional idempotency across the business and metadata databases.

## Semantic policy RAG setup

The pipeline is **policy ingestion → overlapping chunks → embeddings → persistent vector index → cosine retrieval → grounded LLM answer with sources**. SQLite stores the vectors locally; no separate vector database server or additional Python packages are needed.

In `backend/.env`, configure:

```dotenv
POLICY_RETRIEVAL_MODE=semantic
AI_API_KEY=your-chat-provider-key
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4.1-mini
AI_EMBEDDING_MODEL=text-embedding-3-small
POLICY_VECTOR_DB=./storage/policy_vectors.db
POLICY_SIMILARITY_THRESHOLD=0.30
```

Embedding calls reuse `AI_API_KEY` and `AI_BASE_URL` by default. For a separate embeddings provider, set `AI_EMBEDDING_API_KEY` and `AI_EMBEDDING_BASE_URL` to a service that supports the OpenAI-compatible `/embeddings` contract. Your chat provider may not offer embeddings. An embeddings key alone supports semantic retrieval with excerpt responses; a chat key enables generated answers.

Restart the backend and ask a policy question. The first request builds the vector index; later requests reuse it and embed only the question. Policy uploads, edits and deletions refresh the snapshot on the next query. Responses identify `retrieval: semantic` or `tfidf` and `mode: llm` or `local_extractive`. An embedding-provider failure returns an explicit error; a chat-provider failure returns retrieved excerpts with `generation_unavailable: true`.

For offline use, select `POLICY_RETRIEVAL_MODE=tfidf` or leave `auto` with no keys. TF-IDF is lexical retrieval, not a semantic embedding model. The 0.30 semantic threshold needs evaluation with your actual policies. Policy text and questions go to the embedding provider; selected excerpts and questions go to the chat provider. Keep keys and the generated vector database out of GitHub.

The updated backend suite has **59 passing tests**, including mocked semantic RAG and embeddings API tests. No live provider evaluation was performed; run the five assignment policy questions and paraphrases against your configured providers before claiming answer quality. See `docs/ai_eval_results.md`.


## Evaluations and guardrails

Run the versioned offline policy, SQL, action and security evaluation from `backend`:

```powershell
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe scripts/evaluate_copilot.py
```

The runner uses temporary database copies, disables provider calls and writes a JSON scorecard to `storage/evals/offline_results.json`. Latest results: **22/22 offline cases passed**, and **92 full backend tests passed**. A checked-in scorecard is in [docs/eval_offline_results.json](docs/eval_offline_results.json).

New safeguards validate model-generated actions against a fixed tool allowlist and typed payload schemas, reject extra fields and invalid IDs/dates, screen common prompt-override attempts, and check policy citation numbers before displaying generated answers. Invalid generated policy output falls back to retrieved evidence. Existing backend authorization, SQL isolation and confirmation protections remain the security boundaries.

These checks do not prove factual grounding, semantic relevance, or resistance to every prompt injection. Live provider evaluation remains outstanding. See [the guardrails and evaluation guide](docs/ai_guardrails.md) for the exact scope, setup and manual live-review checklist.

## Import an optional private employee profile

Keep employee passwords, contact details, salary, bank information and statutory identifiers in a private local JSON file rather than in this repository. Place the file at `backend/storage/employee_profile.private.json` after initial migration and seeding. From `backend`, run:

```powershell
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe scripts/import_employee.py --profile storage/employee_profile.private.json
```

Enter the HRMS admin password when prompted. The importer calls the existing admin-only employee creation API, which hashes the employee password and initializes leave balances and statutory payroll fields. Duplicate active emails are rejected. Private field values are not printed. No running server is needed: the script uses the configured local database and the real authenticated API through ASGI transport.

The private JSON uses employee-create field names, with optional `department` containing an existing department name. The starter schema uses `occupancy` for employment type. PAN DOB and employee DOB are separate fields. Identifier length checks do not verify PAN, IFSC, UAN or ESI validity against official registries. Review your inputs before importing. Reseeding resets business data; import optional profiles after seeding. `*.private.json` and runtime databases are ignored by Git.
