# Denwa — AI Callback Support Agent

> When a business misses a call, Denwa reads that business's own knowledge base and has an AI voice
> agent call the customer back with the answer.

Built with [CALL-E](https://call-e.devpost.com/) outbound calling — submission for the **CALL-E:
Your Code Is Calling** hackathon.

## The problem

Businesses miss calls all day: lunch breaks, a full queue, one person doing everything. Every missed
call is a lost customer — most people don't call back. Denwa turns a missed call into a handled one:

1. A customer calls and no one picks up.
2. Denwa identifies the business and the likely topic (from that business's own uploaded docs).
3. A CALL-E voice agent calls the customer back, greets them, and answers **using only the verified
   company knowledge** — no inventing.
4. The call returns a structured result (`resolved` / `needs_human_followup`) that lands on the
   business dashboard.

Real impact for a small business: missed calls stop leaking revenue, and the agent never hallucinates
because it's pre-seeded with facts before the call starts.

## Repo layout

```
denwa/
├── frontend/     # React + Vite + TypeScript — onboarding UI, dashboard, call log     [FRONTEND]
├── backend/      # FastAPI — API gateway, job queue, region resolver, CALL-E client    [BACKEND]
├── ai-ml/        # Python — ingestion, embeddings, retrieval, task builder             [AI/ML]
└── docs/         # Architecture + roles/definition-of-done reference
```

## How it works

```
                    ┌─────────────┐     ┌──────────────┐
  missed call ─────►│  Backend    │────►│   AI / ML    │
  (webhook / demo)  │ intake API  │     │ RAG retrieve │
                    └──────┬──────┘     └──────┬───────┘
                           │ pending job       ▼
                           │            chunk → embed → top-k
                           │                   │
                           │                   ▼
                           │     task string + resultSchema (pre-seeded)
                           ▼                   │
                    ┌──────────────┐    ┌──────┴───────┐
                    │   CALL-E     │◄───│  llm condense │
                    │ places call  │    │  (Groq)      │
                    └──────┬──────┘    └──────────────┘
                           ▼
                 structured result → dashboard
```

RAG happens **before** the call is placed — CALL-E has no mid-call injection, so everything the agent
may say is pre-seeded at call creation time.

## Tech stack

| Layer | What |
|---|---|
| Frontend | React, Vite, TypeScript |
| Backend | FastAPI, SQLAlchemy, libphonenumber region resolver |
| AI/ML RAG | fastembed (ONNX, local, free) embeddings + in-memory cosine store |
| LLM condensing | Groq `openai/gpt-oss-120b` (free tier) |
| Calling | CALL-E Calls API (`createAndWait`, terminal webhooks) |
| Data model | `Company` → `Document` → `Chunk` → `CallJob` + `CallResult` |

## Getting started

```bash
# 1. Env vars — copy .env.example files; never commit real keys
cp .env.example .env                                  # root reference
cp ai-ml/.env.example ai-ml/.env                      # GROQ_API_KEY (console.groq.com)
cp backend/.env.example backend/.env                  # backend vars (incl CALLE_API_KEY)

# 2. Frontend (http://localhost:5173)
cd frontend && npm install && npm run dev

# 3. Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# 4. AI/ML — demo that chunks, embeds, retrieves and builds a call task (no backend needed)
cd ai-ml && pip install -r requirements.txt && python -m demo
```

### AI/ML demo output

`python -m demo` ingests a sample company FAQ, embeds it with fastembed (384-dim), retrieves the
relevant chunks for 5 realistic customer questions, condenses them with Groq, and returns the exact
payload the backend hands to CALL-E:

```python
{"task": "...", "result_schema": {"type": "object", "required": [...], ...}}
```

## CALL-E integration notes

- **No mid-call injection** — task + `resultSchema` are fixed when the call is created; only terminal
  webhooks (`call.completed`, `call.failed`, `call.result_validation_failed`) fire. Everything must be
  pre-seeded — this is why RAG runs before the call.
- **Supported regions** (confirmed): US, SG, MY, IN, AE, AU, CA, GB, VN, DE, JP, FR, MX, BR, ID, PH, KE.
  NG is not supported — demo call targets must use a supported region/number.
- **Budget:** every new CALL-E account gets **20 free calls**, then $0.05/call (extra calls available
  via the [request form](https://forms.gle/EPQttEZ1rkW8iq9q6)). Test-call timing is coordinated with
  the team.
- Build against the stable **Calls API** (`calle-ai==0.2.0`). Goal Runs (API 0.6) is preview-only and
  a stretch goal.

## Shared contract: CallJob / CallResult

Everyone reads from the same shape (see `docs/ARCHITECTURE.md`). Changing a field here silently breaks
another role — ping the affected owners before merging.

```
CallJob:    id, company_id, caller_number, status, created_at
CallResult: id, call_job_id, question_asked, answer_given, resolved, needs_human_followup, transcript_url
```

## Git workflow

- `main` is always demo-ready; branch per person: `frontend/<task>`, `backend/<task>`, `ml/<task>`.
- Before every push to `main`: pull + resolve conflicts, run the code, check for secrets in the diff,
  tell affected roles if a shared contract changed.
- Full process in `docs/ROLES_AND_DOD.md`.

## Team

Project owner / AI/ML in-charge, Frontend, and Backend engineers — roles and definitions of done live
in the per-folder READMEs and `docs/ROLES_AND_DOD.md`.