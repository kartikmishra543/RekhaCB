# RekhaCB — AI HR Copilot

RekhaCB brings everyday HR tasks and an AI assistant into one workspace. Employees can find policy information, explore leave plans, check their records, and prepare requests. Managers can review their team's requests and approve them through the same HR system.

Built as an AI engineering capstone, RekhaCB extends the **CB Nest starter provided by Codebasics**. The original HRMS supplies the business records and APIs; the capstone adds policy retrieval, permission-controlled data queries, confirmed actions, and **Request Readiness**.

> **Repository status:** This repository currently contains the README. The application source and supporting documents still need to be uploaded. Setup commands below apply to the complete project folder.

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

## Technology

| Layer | Stack |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy, Alembic |
| Database | SQLite with aiosqlite |
| Policy retrieval | Document chunks and TF-IDF vectors using scikit-learn |
| Optional AI provider | OpenAI-compatible chat-completions API |
| Authentication | JWT and backend role checks |

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

## Project structure

```text
RekhaCB/
├── backend/             # FastAPI application, migrations, scripts, tests
├── frontend/            # Next.js application and public assets
├── docs/                # Architecture, permissions, evaluation, walkthrough
└── docker-compose.yml   # Optional Docker setup
```

Supporting documents in the complete project include `docs/ai_architecture.md`, `docs/ai_permissions_matrix.md`, `docs/ai_eval_results.md`, and `docs/demo_walkthrough.md`.

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

Coverage includes retrieval, query restrictions, role permissions, confirmation handling, and request flows. See the evaluation document for the recorded evidence and limits.

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

The updated demo video link will be added after publication.

## Credits

Capstone project by **Kartik Mishra**, built on the **Codebasics CB Nest starter**. Original copyright notices and applicable terms remain in effect. No additional open-source license is granted by this README.
