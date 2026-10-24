# Copilot guardrails and evaluation

The backend enforces these controls independently of model instructions:

| Boundary | Control |
| --- | --- |
| Identity | JWT authentication and role/ownership checks on existing HR APIs |
| SQL | Disposable permission-scoped projection, excluded sensitive columns, SELECT inspection, SQLite authorizer, row and execution limits |
| Actions | Fixed tool allowlist and Pydantic payload schemas; unknown fields rejected, positive integer IDs, enum and date validation |
| Confirmation | Account-bound, five-minute proposals; atomic dispatch claim; success replay blocked; uncertain outcomes require record inspection |
| Policy generation | Retrieval evidence required; generated answers must cite valid retrieved source numbers and pass a basic secret/PAN-pattern screen; otherwise show excerpts |
| Injection attempts | Common instruction-override, secret-extraction and role-impersonation wording refused before routing; suspicious lines filtered from policy chunks |
| Audit | Redacted interaction metadata; no API keys or JWTs in the evaluation scorecard |

Schema validation runs on both freshly interpreted actions and stored confirmation payloads. The model cannot supply a URL, employee ownership override, or readiness bypass field. Existing APIs remain responsible for final authorization and business validation. A schema cannot prove that a model chose the user's intended dates or IDs: users must review the confirmation preview.

Pattern screening is defense in depth, not a complete prompt-injection detector. Citation validation verifies reference numbers, not whether every claim follows from the cited text. A plausible false answer with a valid reference can still pass; live human factuality review remains required. Secret screening is limited to recognizable patterns, and policy upload permissions remain essential.

## Run the offline evaluation

After migrations and the two demo seed scripts, from `backend`:

```powershell
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe scripts/evaluate_copilot.py
```

The versioned dataset is `backend/evals/copilot_cases.json`. The runner executes 22 pytest cases against temporary copies of the seeded database. It disables chat and embedding provider keys and uses TF-IDF/template mode. Cases prepare proposals but never confirm actions. It writes a JSON scorecard to `backend/storage/evals/offline_results.json` (ignored by Git). A failure exits nonzero. Run `python -m pytest -m ai_eval -q` from backend to diagnose failing assertions.

The dataset covers five policy questions, missing evidence, employee/manager/admin data questions, action previews, malformed dates, missing leave types, protected-field refusals, destructive requests, role restrictions, secret extraction and instruction overrides. The full test suite adds mocked model output, semantic retrieval, SQL permission, confirmation and end-to-end action tests.

## Live provider review (not performed automatically)

Configure semantic embeddings and a chat model, restart the API, and run the five policy questions from the dataset in the Policy library mode. Include paraphrases and an unsupported policy question. Confirm `retrieval: semantic` and `mode: llm` in the API response, then manually compare every claim and source with the fictional policy documents. A provider error or excerpt fallback is not a successful live-generation result.

Record provider/model, document version, question, answer correctness, citation correctness, refusal behavior, latency and reviewer notes. Test employee, manager and admin access separately; use only fictional records and do not confirm destructive/unauthorized actions. Keep provider responses out of public reports if they contain private data.

The automated results are a regression baseline, not a production safety certification or a guaranteed capstone score.

## Privacy hardening — 24 October 2026

Copilot requests are checked against stored account, PAN, IFSC, phone, DOB, salary, PF UAN and ESI identifiers before routing. Matching private inputs are refused before a provider call. Policy content and source metadata are redacted before indexing, returning excerpts or prompting a provider. The shared model and embedding HTTP adapters also apply pattern redaction. Copilot response text is checked again before returning it. Request Readiness rejects private identifiers in reasons before preview or proposal storage.

AI audit logs now omit message text entirely; they retain user ID, role, route, status, tool, result IDs and timestamps. Existing message fields are scrubbed when the metadata store opens after updating. Confirmed action payloads may still contain ordinary non-sensitive business reasons, stored locally with account-bound confirmation metadata.

The private employee import file and databases stay outside public source. Public source was scanned for the supplied private credentials and identifiers; no matches were found. Finance endpoints remain self-scoped and employee directory responses omit banking, salary and identity fields. Authorized HR screens still display the data they need.

The database and local private JSON are not encrypted at rest by these changes. Backups, access to the computer, screenshots, browser storage, third-party provider retention and identifiers not recognized by the redactor remain outside the proven guarantees. Do not place real credentials or financial identifiers in policy documents. These controls reduce exposure; they do not establish that every possible secret can be detected.
