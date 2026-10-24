# Evaluation results

Verified in the build environment on 20 October 2026 using Python 3.12 and the supplied database migrations plus demo seeds. All provider calls were disabled during these tests.

| Check | Result |
| --- | --- |
| Backend pytest suite | 39 passed; 3 dependency deprecation warnings |
| Next.js production build | Passed after fixing inherited TypeScript and Suspense issues |
| TypeScript validation | Passed as part of the production build |
| Live LLM provider behavior | Not tested; requires an approved API key |
| Interactive browser/device testing | See the readiness browser verification notes below |
| Docker image startup | Not executed; equivalent native migrations, seed, API tests and frontend build were run |

Full command output is retained in `backend_test_output.txt` and `frontend_build_output.txt`. These results do not establish production readiness or a score against the evaluator's private test set.

## What the automated suite exercises

- Five common policy queries: leave, sick leave, WFH, late attendance and half days. Assertions verify retrieval, citations and relevant answer content. This is a smoke evaluation, not a human-graded factuality benchmark.
- Unsupported policy topic returns no sources.
- Policy text containing an instruction to reveal salaries is filtered and never executed.
- Missing authentication and refresh-token misuse are rejected.
- Employee SQL exposes self rows only and hides raw SQL.
- Manager SQL rows remain inside the direct-report scope.
- Sensitive salary, bank and payroll prompts refuse without data rows.
- Destructive SQL, metadata reads, extension loading and multiple statements fail the query guard.
- Destructive natural-language data requests are refused.
- Ticket proposal has no business write until confirmation; the API creates the ticket after confirmation.
- Cross-account, expired and replayed confirmations refuse.
- Leave submission produces a real pending leave through the existing API.
- Employee leave approval and project assignment are denied.
- Admin project assignment calls the business API successfully.
- A manager cannot approve leave for an unrelated employee.
- Balance lookup returns the real API result.
- Router selects policy and SQL for representative messages.
- Sensitive audit text is redacted.

The tests use temporary copies of a seeded database, real JWT verification, the real FastAPI app and real API handlers. They are not a replacement for adversarial provider tests or an audit of every inherited HRMS endpoint.

## Remaining manual verification

Configure the intended provider and rerun all demo questions. Check that source citations match actual excerpts, compound SQL filters select the intended employees, and ambiguous dates result in clarification rather than invented values. Verify manager/admin action extraction, ticket management, announcement and project creation with the chosen model. Measure latency and failures before making claims about accuracy or reliability.

Record one complete request/approval flow and one refusal in the required video. The README's demo URL is intentionally unfinished until a real recording exists.


## Request Readiness regression coverage

Nine additional tests verify: scoped balance calculations and snapshot metadata; no leave creation during analysis; invalid date and half-day rejection; half-day unit calculation; preparation blocked on insufficient balance; successful prepare/confirm followed by overlap detection; balance changes rejected at confirmation; fingerprints change across different plans; and missing authentication is rejected.

Policy query normalization now maps “leaves” to “leave” before vector lookup. This fixes an observed retrieval miss when only the compact handbook was readable in the local test environment. The no-context refusal test still passes.

## Readiness browser verification limits

The updated Next.js production build completed successfully, including TypeScript checks and all 22 generated pages. The local API and production web server started successfully. Interactive browser testing could not proceed: the available Playwright runtime had no browser binary, and the browser download returned invalid/truncated archives. No browser click-through, visual QA, clipboard, JSON download or mobile-device behavior is claimed as verified. Before recording, manually test scenario pinning, changing dates, expanding policy context, preparing and confirming, and opening the resulting record in Leaves.

The 39 API/integration tests passed after the readiness changes. They verify the browser's underlying endpoint flow using real authentication, a temporary database and the existing leave API, but do not replace browser testing.

## Semantic RAG upgrade — 24 October 2026

The updated backend suite passes 59 tests with three dependency deprecation warnings. The five original policy questions still run against the offline TF-IDF baseline. New tests verify semantic retrieval-to-generation wiring and source references using mocked embeddings and chat responses, persistent vector reuse, content/deletion/model invalidation, a no-match threshold, explicit embedding-provider failures, generation fallback to evidence, and batching/order/vector validation of the embeddings API adapter.

No live embedding or chat provider was called. Mock vectors prove implementation behavior, not semantic accuracy. Before claiming provider-based RAG quality, configure the selected providers, run the five assignment questions plus paraphrases and unsupported questions, and manually check answer correctness, citations, refusal behavior and the chosen similarity threshold. The default 0.30 threshold is a starting configuration, not a calibrated confidence score.

## Guardrails and evaluation dataset — 24 October 2026

- Full backend suite: **92 passed**, three dependency deprecation warnings.
- Offline evaluation runner: **22/22 passed** against the versioned policy/SQL/action/security dataset.
- Provider usage: none. Dataset cases force TF-IDF/templates; semantic and model-output cases use mocks.
- New regression checks reject invalid model action objects, unauthorized extra payload fields, invalid IDs, and missing/out-of-range citations.

Run instructions and limits are documented in `docs/ai_guardrails.md`. No live answer factuality score or adversarial robustness guarantee is claimed.
