# Backend

Owns: API gateway, telephony webhook, job queue, region resolution, CALL-E integration, database.

## Tasks

- [ ] Telephony webhook — receives the real missed-call event from the provider,
      verifies signature/authentication, validates payload, deduplicates via
      `provider_event_id`, resolves the company from the business number, persists
      `TelephonyEvent`, creates the `CallJob`, enqueues it. This is the real production
      entry point — not a customer-facing simulate/trigger feature.
- [ ] API gateway - create company, upload document (proxy to AI/ML ingestion), fetch call
      history, fetch call detail.
      (dev-only: `/internal/dev/trigger-callback` exists purely for testing the
      job/worker/CALL-E pipeline without waiting on a real phone call — never exposed
      to or used by the frontend/product surface.)
- [ ] Job queue - turns a validated telephony event into a pending callback job.
- [ ] Region/language resolver — caller number → CALL-E region code, with fallback.
- [ ] Callback worker/orchestrator — pulls a pending job, calls AI/ML's task-builder, calls CALL-E.
- [ ] CALL-E client - wraps `@call-e/calle` / `calle-ai` (auth, error handling, idempotency key per job). Build
      against the **Calls API**, not Goal Runs.
- [ ] Result capture - poll `createAndWait` or handle the `call.completed` webhook, write result to DB.
- [ ] Core database - companies, documents, telephony events, call jobs, call results.

## Definition of Done

- [ ] Real telephony webhook accepts a valid signed event and rejects an invalid/unauthenticated one.
- [ ] Duplicate `provider_event_id` creates zero additional CallJobs (tested with 2+ identical events).
- [ ] Every endpoint the frontend needs is implemented, documented, returns sensible error codes.
- [ ] A validated event reliably creates a job the worker picks up — 5 consecutive runs, no stuck job.
- [ ] Region resolution verified against the confirmed CALL-E region list, with a working fallback.
- [ ] CALL-E integration places a real call end-to-end at least once, correct task + resultSchema.
- [ ] Structured result correctly parsed, stored, and matches what the dashboard expects.
- [ ] `/internal/dev/trigger-callback` is confirmed dev-only and is not called anywhere in the frontend/product flow.
- [ ] No API keys/secrets committed.

## Layout

```
app/
├── main.py              # FastAPI app, mounts routers
├── config.py            # env var loading
├── api/                 # route handlers (companies, documents, calls)
├── queue/               # job queue
├── region/              # phone number → CALL-E region resolver
├── calle_client/        # CALL-E SDK wrapper
├── worker/              # callback orchestrator
└── db/                  # models + session
```

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
