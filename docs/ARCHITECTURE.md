# Denwa — Architecture (condensed)

Full version: uploaded PDF "Denwa_Architecture.pdf". This is a quick-reference copy so the call flow and data
model are visible from inside the repo.

## Call flow

1. **Missed-call trigger** (Backend, +optional Frontend sim) — customer calls, no answer (Twilio webhook, or demo
   "Simulate missed call" button).
2. **Intake API** (Backend) — webhook/form hits API gateway, creates a `pending` CallJob, queues it.
3. **Region/language resolution** (Backend) — parse caller number (libphonenumber) → CALL-E region code, fallback
   to English if unsupported.
4. **RAG lookup** (AI/ML) — retrieve top-matching chunks for likely topics from the company's pre-embedded docs;
   LLM drafts an answer + a CALL-E task string + resultSchema.
5. **CALL-E places the callback** (Backend, integration) — `calls.createAndWait({ task, recipient, resultSchema })`.
6. **Structured result capture** (Backend) — `{ question_asked, answer_given, resolved, needs_human_followup }`
   stored against the CallJob.
7. **Dashboard** (Frontend) — company sees call log, outcome, unresolved cases.

## Data model

| Table | Key fields |
|---|---|
| Company | id, name, phone_number, created_at |
| Document | id, company_id, filename, raw_text, uploaded_at |
| Chunk | id, document_id, text, embedding_vector |
| CallJob | id, company_id, caller_number, status, created_at |
| CallResult | id, call_job_id, question_asked, answer_given, resolved, needs_human_followup, transcript_url |

## CALL-E integration — confirmed facts

- **No mid-call injection.** Task + resultSchema are fixed at call creation. CALL-E only fires terminal webhooks
  (`call.completed`, `call.failed`, `call.result_validation_failed`). Everything must be pre-seeded before the
  call starts — this is the reason the RAG step happens *before* step 5, not during the call.
- **Region support (confirmed list):** US, SG, MY, IN, AE, AU, CA, GB, VN, DE, JP, FR, MX, BR, ID, PH, KE.
  **NG is not on the list** — plan the demo call target around a supported region/number, or use a virtual number.
- **Build against the stable Calls API** (`@call-e/calle@0.2.2` / `calle-ai==0.2.0`), not Goal Runs (API 0.6,
  still preview — no matching SDK yet). Goal Runs is a stretch-goal migration.
- **Budget:** 20 free calls, then $0.05/call. Coordinate test-call timing with the team.

## MVP scope

- One demo company, 5–10 Q&A pairs.
- "Simulate missed call" trigger (real Twilio is a stretch goal).
- Working RAG retrieval for a given likely topic.
- One real CALL-E call placed to a real phone, agent answers correctly from company data.
- Structured result stored and visible on the dashboard.
