# Denwa - Backend 

The backend for **Denwa**, an AI-powered callback support system for businesses. When a business misses a customer phone call, Denwa orchestrates verified knowledge retrieval, places an automated AI voice callback via CALL-E, and captures structured outcome results for the dashboard.

---

## Architecture & End-to-End Flow

1. **Telephony Webhook Intake (`/webhooks/telephony`)**:
   - Provider: **Telnyx** (Call Control API v2).
   - Authenticates incoming events using Ed25519 signature verification (`telnyx-signature-ed25519` + `telnyx-timestamp` headers), verified against the account's public key. Includes a replay-attack guard that rejects stale timestamps.
   - Telnyx wraps event fields inside a top-level `data` object (alongside a sibling `meta` object) the handler reads `data.id`, `data.event_type`, and `data.payload` accordingly.
   - Only acts on `call.hangup` events; all other event types (`call.initiated`, `call.answered`, ...) are acknowledged with `200 OK` and ignored.
   - Filters for genuine missed-call outcomes via `hangup_cause` (currently: `no_answer`, `originator_cancel`, `call_rejected`, `timeout` **see Known Issues below, not yet confirmed against a real call**).
   - Deduplicates on the event's own `id` (Telnyx's recommended idempotency key) to prevent replayed webhook deliveries from generating redundant callbacks.
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
```

---

## API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status |
| `POST` | `/companies/` | Register a new company |
| `GET` | `/companies/{id}` | Fetch company profile |
| `POST` | `/webhooks/telephony` | Production entry point for telephony missed-call webhooks |
| `GET` | `/calls/?company_id={id}` | List all calls and structured results for a company |
| `GET` | `/calls/{call_job_id}` | Detailed view of a specific call and outcome |
| `POST` | `/documents/upload` | Upload FAQ/knowledge documents and auto-generate chunks |
| `GET` | `/documents/?company_id={id}` | List all uploaded documents for a company |
| `POST` | `/internal/dev/trigger-callback` | *Dev-only:* Trigger callback pipeline without a real phone call |

---

## Getting Started

### 1. Installation
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file based on `.env.example`:
```env
DATABASE_URL=sqlite:///./denwa.db
CALLE_API_KEY=your_calle_api_key
CALLE_BASE_URL=https://api.call-e.com
CALLE_DEFAULT_FALLBACK_REGION=US
TELNYX_PUBLIC_KEY=your_telnyx_account_public_key
WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS=300
WEBHOOK_SKIP_SIGNATURE_CHECK=false
```

> `TELNYX_PUBLIC_KEY` is found in the Telnyx Mission Control Portal under **Account Settings → Keys & Credentials → Public Key**. `WEBHOOK_SKIP_SIGNATURE_CHECK` must always be `false` outside of local dev testing.

### 3. Run the Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation will be available at **`http://localhost:8000/docs`**.

---

## Local Testing with a Real Telnyx Number (ngrok tunnel)

Telnyx cannot reach a webhook running on `127.0.0.1`, so real end-to-end testing requires a public tunnel to the local server. This is only needed for testing against a real phone call `test_webhook.py` and the `tests/` suite already validate the webhook logic fully offline.

1. **Install and authenticate ngrok** (one-time setup):
   ```bash
   ngrok config add-authtoken <your ngrok authtoken>
   ```
   Get the authtoken from [dashboard.ngrok.com](https://dashboard.ngrok.com) under "Your Authtoken".

2. **Run the backend** in one terminal (`uvicorn app.main:app --reload`), then start ngrok in a **separate** terminal:
   ```bash
   ngrok http 8000
   ```
   Copy the `https://...ngrok-free.dev` forwarding URL it prints. The free plan only allows **one active ngrok session at a time** close any other running session first, or you'll get an `authentication failed` error.

3. **Register the business number as a Company** so the webhook can route to it:
   ```bash
   curl -X POST http://127.0.0.1:8000/companies/ -H "Content-Type: application/json" -d "{\"name\":\"Test Cafe\",\"phone_number\":\"+1XXXXXXXXXX\"}"
   ```
   The phone number must exactly match the Telnyx number below.

4. **Configure Telnyx** (Mission Control Portal → Voice → Programmable Voice → Voice API Applications):
   - Create a Voice API Application (e.g. `Denwa Webhook`).
   - Set the **Webhook Event URL** to your ngrok URL + `/webhooks/telephony`, e.g.:
     `https://xxxx-xx-xx.ngrok-free.dev/webhooks/telephony`
   - Skip the Outbound Voice Profile prompt ("Assign profile later") Denwa only receives inbound events here; outbound calls happen via CALL-E, not Telnyx.
   - Under the application's **Numbers** tab, assign your real Telnyx phone number to this application.

5. **Test with a real call**: call the Telnyx number from a real phone and let it go unanswered. Watch the `uvicorn` terminal for a log line like:
   ```
   call.hangup received: hangup_cause=... call_control_id=...
   ```

---

## Running Tests

Run the full automated test suite:
```bash
python -m pytest tests/ -v
```

Run the standalone webhook signature validation:
```bash
python test_webhook.py
```

---

## 👤 Author

**Waad**