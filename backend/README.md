# Backend

Owns: API gateway, job queue, region resolution, CALL-E integration, database.

## Tasks

- [ ] API gateway — create company, upload document (proxy to AI/ML ingestion), trigger intake event, fetch call
      history, fetch call detail.
- [ ] Job queue — turns an intake event into a pending callback job.
- [ ] Region/language resolver — caller number → CALL-E region code, with fallback.
- [ ] Callback worker/orchestrator — pulls a pending job, calls AI/ML's task-builder, calls CALL-E.
- [ ] CALL-E client — wraps `@call-e/calle` / `calle-ai` (auth, error handling, idempotency key per job). Build
      against the **Calls API**, not Goal Runs.
- [ ] Result capture — poll `createAndWait` or handle the `call.completed` webhook, write result to DB.
- [ ] Core database — companies, documents, call jobs, call results.

## Definition of Done

- [ ] Every endpoint the frontend needs is implemented, documented, returns sensible error codes.
- [ ] Intake event reliably creates a job the worker picks up — 5 consecutive runs, no stuck job.
- [ ] Region resolution verified against the confirmed CALL-E region list, with a working fallback.
- [ ] CALL-E integration places a real call end-to-end at least once, correct task + resultSchema.
- [ ] Structured result correctly parsed, stored, and matches what the dashboard expects.
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
