# Denwa — Backend

The backend for **Denwa**, an AI-powered callback support system. When a business misses a customer
phone call, Denwa retrieves verified company knowledge, places an automated AI voice callback via
CALL-E, and captures a structured outcome for the dashboard.

## End-to-end flow

1. **Missed-call intake** — a Telnyx `call.hangup` webhook (or the dev
   `/internal/dev/trigger-callback` endpoint) creates a `pending` CallJob. Webhook verification is
   Ed25519 signature based, with a timestamp replay guard; both can be skipped in dev
   (`WEBHOOK_SKIP_SIGNATURE_CHECK=true`). Events are deduplicated on their own `id`.
2. **Retrieve** — the RAG pipeline (`app/rag/`) chunks the company's uploaded docs, embeds them
   (fastembed ONNX, numpy fallback when unavailable) and returns the top-k context for the caller's
   likely topic.
3. **Build the task** — `app/rag/builder.py` pre-seeds the CALL-E task string + `resultSchema` from
   the retrieved context (optionally condensed by Groq). Everything the agent can say is fixed now —
   CALL-E has no mid-call injection.
4. **Call** — `app/calle_client/` places the outbound CALL-E call with idempotency keys and polls to
   a terminal outcome.
5. **Result** — the callback worker (`app/worker/`) persists `question_asked`, `answer_given`,
   `resolved`, `needs_human_followup`, `transcript_url` into `CallResult`; the dashboard reads them.

The worker (DB-backed `CallJob.status` queue, crash-safe, no broker) autostarts with the app and,
without a `CALLE_API_KEY`, polls without dialing so jobs queue safely in dev.

## Directory structure

```text
backend/
├── app/
│   ├── main.py              # FastAPI app, lifespan (worker start), CORS, router mounting
│   ├── config.py            # Environment configuration loading
│   ├── api/                 # REST endpoints: companies, calls, documents, webhooks, dev
│   ├── calle_client/        # CALL-E API client (idempotency, polling, error handling)
│   ├── db/                  # SQLAlchemy models (Company, Document, Chunk, CallJob, CallResult, TelephonyEvent)
│   ├── integrations/        # ai_ml.py — retrieval + task builder glue for CALL-E
│   ├── queue/               # Persistent database-backed job queue
│   ├── rag/                 # Chunker, embedder, store, retriever, builder, ingest (vendored)
│   ├── region/              # Caller number → CALL-E region resolver
│   ├── utils/               # phone normalization, helpers
│   └── worker/              # Background callback orchestrator
├── scripts/                 # Standalone dev utilities (check_db.py)
├── tests/                   # Pytest suite (API, RAG, worker)
├── test_webhook.py          # Standalone webhook verification harness
├── requirements.txt
└── .env.example
```

## API endpoints

All routes are mounted under `/api/v1` (the webhook is also mounted at the bare path).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health |
| `POST` | `/companies/` | Register a new company/workspace |
| `GET` | `/companies/{id}` | Fetch company profile |
| `GET` | `/companies/lookup?phone_number=…` | Sign-in: find a company by its business number |
| `POST` | `/webhooks/telephony` | Telnyx missed-call webhook (root + `/api/v1`) |
| `GET` | `/calls/?company_id={id}` | List call jobs + structured results |
| `GET` | `/calls/{call_job_id}` | Detail for one call/outcome |
| `POST` | `/documents/upload` | Upload FAQ/knowledge docs → chunk + embed + persist |
| `GET` | `/documents/?company_id={id}` | List a company's documents |
| `POST` | `/internal/dev/trigger-callback` | Simulate an inbound missed call (dev/testing) |
| `GET` | `/internal/dev/config-status` | Provider/feature status booleans (no secrets) for the UI |

## Getting started

```bash
pip install -r requirements.txt
cp .env.example .env          # set CALLE_API_KEY (required), GROQ_API_KEY (optional)

uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Interactive docs: `http://127.0.0.1:8000/docs`.
- The background worker starts automatically and dials CALL-E for any `pending` job.
- Run all tests: `python -m pytest -q`. Run the webhook harness: `python test_webhook.py`.

## Telephony webhook notes

- Only acts on `call.hangup` with a “missed” `hangup_cause`; every other event type is acknowledged
  `200 OK` and ignored (see the config in `app/config.py`).
- Envelope shape: `{"data": {"id", "event_type", "payload": {...}}, "meta": ...}`.
- The `hangup_cause` set is best-effort — confirm it against your first real call before trusting it
  in a demo.
- For live delivery Telnyx needs a public HTTPS URL: `cloudflared tunnel --url http://127.0.0.1:8000`
  and set the connection webhook URL to `https://<tunnel>/api/v1/webhooks/telephony`.