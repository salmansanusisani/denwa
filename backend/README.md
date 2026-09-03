# Denwa - Backend 

The backend for **Denwa**, an AI-powered callback support system for businesses. When a business misses a customer phone call, Denwa orchestrates verified knowledge retrieval, places an automated AI voice callback via CALL-E, and captures structured outcome results for the dashboard.

---

## Architecture & End-to-End Flow

1. **Telephony Webhook Intake (`/webhooks/telephony`)**:
   - Authenticates incoming missed-call events using HMAC-SHA1 signature verification (`X-Twilio-Signature`).
   - Filters for genuine missed-call statuses (`no-answer`, `busy`, `failed`).
   - Deduplicates on provider `CallSid` to prevent replayed events from generating redundant callbacks.
   - Normalizes phone numbers to E.164 and routes the event to the matching registered `Company`.
   - Persists a `TelephonyEvent` and enqueues a `CallJob` with `status="pending"`.

2. **Persistent Job Queue (`app/queue/job_queue.py`)**:
   - Database-backed queue utilizing `CallJob.status` (`pending` → `in_progress` → `completed`/`failed`) for crash-safety and durability without external broker dependencies.

3. **AI/ML Context Integration (`app/integrations/ai_ml.py`)**:
   - Connects to the knowledge retrieval pipeline to extract verified company context and assemble prompt-safe CALL-E tasks and `resultSchema`.

4. **Region Resolution (`app/region/resolver.py`)**:
   - Maps caller phone numbers to confirmed CALL-E supported region codes, with automatic fallback handling.

5. **CALL-E Client & Callback Worker (`app/calle_client/`, `app/worker/`)**:
   - Outbound call execution using CALL-E's stable Calls API with unique `Idempotency-Key` headers.
   - Polls for terminal call outcomes and extracts structured result fields (`question_asked`, `answer_given`, `resolved`, `needs_human_followup`, `transcript_url`).
   - Persists outcomes into the `CallResult` table.

---

## Directory Structure

```text
backend/
├── app/
│   ├── main.py              # FastAPI app initialization, CORS, and router mounting
│   ├── config.py            # Environment configuration loading
│   ├── api/                 # REST API endpoints (companies, calls, documents, webhooks)
│   ├── db/                  # SQLAlchemy models (Company, Document, Chunk, CallJob, CallResult, TelephonyEvent)
│   ├── queue/               # Persistent database-backed job queue
│   ├── region/              # Caller number to CALL-E region resolver
│   ├── integrations/        # AI/ML task builder client
│   ├── calle_client/        # CALL-E API client wrapper (idempotency, polling, error handling)
│   └── worker/              # Background callback orchestrator
├── tests/                   # Comprehensive pytest test suite
├── test_webhook.py          # Standalone webhook signature & idempotency verification test
└── requirements.txt         # Python dependencies