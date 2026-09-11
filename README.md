# Denwa — AI Callback Support Agent

> When a business misses a call, Denwa reads that business's own knowledge base and has an AI voice
> agent call the customer back with the answer.

Built with [CALL-E](https://call-e.devpost.com/) outbound calling — submission for the **CALL-E:
Your Code Is Calling** hackathon.

## The problem

Businesses miss calls all day: lunch breaks, a full queue, one person doing everything. Every missed
call is a lost customer — most people don't call back. Denwa turns a missed call into a handled one:

1. A customer calls and no one picks up (Telnyx webhook, or a simulated event in dev).
2. Denwa identifies the business and the likely topic (from that business's own uploaded docs).
3. A CALL-E voice agent calls the customer back, greets them, and answers **using only the verified
   company knowledge** — no inventing.
4. The call returns a structured result (`resolved` / `needs_human_followup`) that lands on the
   business dashboard.

RAG runs **before** the call is placed — CALL-E supports no mid-call injection, so everything the
agent may say is pre-seeded when the call is created.

## Repo layout

```
denwa/
├── backend/       # FastAPI monolith: API, job queue, CALL-E client, RAG pipeline, worker
├── frontend/      # React + Vite + TypeScript UI
├── ai-ml/         # Standalone reference/demo of the RAG pipeline (superseded by backend/app/rag)
└── docs/          # Architecture + roles/definition-of-done
```

The AI/ML pipeline used at runtime is vendored into `backend/app/rag/` (chunk → embed → store →
retrieve → CALL-E task). `ai-ml/` is kept as a runnable standalone demo (`python -m demo`).

## Tech stack

| Layer | What |
|---|---|
| Frontend | React, Vite, TypeScript |
| Backend | FastAPI, SQLAlchemy, SQLite, uvicorn |
| Job queue | DB-backed `CallJob.status` transitions (`pending` → `in_progress` → `completed`/`failed`) |
| RAG embeddings | fastembed/ONNX (`BAAI/bge-small-en-v1.5`), numpy hashing fallback when unavailable |
| LLM condensing | Groq `openai/gpt-oss-120b` (free tier) — deterministic local fallback without a key |
| Calling | CALL-E Calls API (`createAndWait`, terminal webhooks) — `https://api.heycall-e.com` |
| Inbound missed calls | Telnyx Call Control webhooks (optional for real calls; otherwise simulate) |

## Prerequisites

- Python 3.12+ and Node 20+.
- `CALLE_API_KEY` from the [CALL-E dashboard](https://dashboard.heycall-e.com) for outbound AІ calls.
- Optional: `GROQ_API_KEY` (console.groq.com) for stronger answer condensing; a Telnyx account +
  number + tunnel only if you want **real** inbound missed-call detection.

## Getting started

```bash
# 1. Backend config (real values, never committed)
cp backend/.env.example backend/.env
#    -> set CALLE_API_KEY (required), optionally GROQ_API_KEY, TELNYX_PUBLIC_KEY

# 2. Backend API  (http://127.0.0.1:8000, docs at /docs)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
#    -> the background callback worker starts automatically (WORKER_ENABLED=true)
#    -> without CALLE_API_KEY it polls but never dials (jobs stay "pending")

# 3. Frontend   (http://127.0.0.1:5173)
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

The frontend talks to `http://127.0.0.1:8000/api/v1` by default; override with
`VITE_API_BASE_URL` in `frontend/.env` if needed.

### Environment variables (`backend/.env`)

| Variable | Required | Notes |
|---|---|---|
| `CALLE_API_KEY` | yes | CALL-E dashboard — powers outbound AI callbacks |
| `BUSINESS_PHONE_NUMBER` | for webhooks | Your real number (E.164), reference value for onboarding |
| `GROQ_API_KEY` | no | Free at console.groq.com — improves the callback script |
| `LLM_MODEL` | no | `openai/gpt-oss-120b` default (or `qwen/qwen3-32b`, `openai/gpt-oss-20b`) |
| `EMBEDDING_MODEL` | no | fastembed model id; numpy fallback used if fastembed is missing |
| `TELNYX_PUBLIC_KEY` | no | Enables real webhook signature verification (production) |
| `WEBHOOK_SKIP_SIGNATURE_CHECK` | no | `true` in dev, `false` in production |
| `WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS` | no | Replay-window for webhook timestamps (default 300) |
| `WORKER_ENABLED` | no | `true` default; set `false` in tests |
| `DATABASE_URL` | no | `sqlite:///./denwa.db` default |

## Using the app

1. **Onboard**: create a workspace with your business number — or sign back into an existing one via
   **“Find my business by phone number”** / saved workspaces on the login screen.
2. **Knowledge Base**: upload FAQ/docs — they are chunked and embedded immediately and re-loaded on
   every backend start.
3. **Call flow**: a missed call (real webhook or simulated) creates a `pending` CallJob; the worker
   builds a task from retrieved knowledge and CALL-E dials the caller back.
4. **Provider status**: the **Phone Numbers / Settings** screens show live status for CALL-E, Telnyx,
   Groq and the worker (`GET /api/v1/internal/dev/config-status`).

### Running a full loop without a phone call

```bash
# Register a workspace through the UI, then simulate an inbound missed call:
curl -X POST "http://127.0.0.1:8000/api/v1/internal/dev/trigger-callback?company_id=1&caller_number=%2B16502539999"
```

This queues a CallJob exactly like a real webhook would — with a `CALLE_API_KEY` set the worker will
place a **real** CALL-E call to that number (each call costs one of your 20 free credits). Without a
key, the job stays `pending`.

### Real inbound missed calls (Telnyx, optional)

1. Expose the backend: `cloudflared tunnel --url http://127.0.0.1:8000` (or `ngrok http 8000`) →
   gives you an `https://…` URL.
2. Register your business number as a workspace in the UI.
3. Add your number as a company/connection in Telnyx and set the connection webhook URL to
   `https://<tunnel>/api/v1/webhooks/telephony`. Be mindful the webhook is routed by the `to` number
   and must match the registered company's number.
4. Call the number and let it go unanswered. Watch backend logs for `call.hangup received: ...`.

Keep `WEBHOOK_SKIP_SIGNATURE_CHECK=true` during local testing; flip to `false` and set
`TELNYX_PUBLIC_KEY` for production. The `hangup_cause` set treated as “missed”
(`no_answer`, `originator_cancel`, `call_rejected`, `timeout`) is best-effort and should be verified
against your first real call.

## Testing

```bash
cd backend
pip install -r requirements.txt
python -m pytest -q                      # API + RAG + worker suite
python test_webhook.py                   # standalone webhook harness (15 checks)
python scripts/check_db.py               # dev: list DB tables
```

## CALL-E integration notes

- Task + `resultSchema` are fixed when the call is created; only terminal webhooks
  (`call.completed`, `call.failed`, `call.result_validation_failed`) fire.
- Supported regions (confirmed): US, SG, MY, IN, AE, AU, CA, GB, VN, DE, JP, FR, MX, BR, ID, PH, KE.
- Budget: every new CALL-E account gets **20 free calls**, then `$0.05`/call.

## Git workflow

- `main` is always demo-ready.
- Before pushing: pull + run tests, and check your diff for secrets — `.env`/`*.log`/
  `*.tsbuildinfo` are gitignored, real keys must never be committed.
- Roles and definitions of done live in `docs/ROLES_AND_DOD.md`.