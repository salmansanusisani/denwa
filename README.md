# Denwa — AI Callback Support Agent

Built on the [CALL-E](https://call-e.devpost.com/?ref_feature=challenge&ref_medium=discover) outbound calling
platform. When a business misses a call, Denwa reads that business's own knowledge base and has an AI voice
agent call the customer back to answer their question.

Full design docs: `docs/ARCHITECTURE.md` and `docs/ROLES_AND_DOD.md` (source PDFs, condensed).

## Repo layout

```
denwa/
├── frontend/     # React (Vite) — onboarding UI, intake trigger, dashboard      [FRONTEND owns]
├── backend/      # FastAPI — API gateway, queue, region resolver, CALL-E client [BACKEND owns]
├── ai-ml/        # Python — ingestion, embeddings, retriever, task builder      [AI/ML owns]
└── docs/         # Architecture + roles/DoD reference
```

Each folder has its own README with that role's task list and Definition of Done, copied straight out of the
planning docs so nobody has to go dig through a PDF mid-build.

## Branch naming

`frontend/<short-task>`, `backend/<short-task>`, `ml/<short-task>` — e.g. `backend/calle-integration`.
`main` is always demo-ready. See `docs/ROLES_AND_DOD.md` Section 6 for the full pre-push checklist.

## Shared contract: CallJob / CallResult

Everyone reads from the same shape (see `docs/ARCHITECTURE.md` Section 5). If you change a field here, ping the
other roles it affects before merging — this is the one thing that will break someone else's build silently.

```
CallJob:    id, company_id, caller_number, status, created_at
CallResult: id, call_job_id, question_asked, answer_given, resolved, needs_human_followup, transcript_url
```

## Env vars

Copy `.env.example` to `.env` in `backend/` and `ai-ml/` and fill in real values. Never commit `.env`.

## Getting started

```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# AI/ML (used as a library by backend/worker, or run standalone for testing)
cd ai-ml && pip install -r requirements.txt

# Frontend
cd frontend && npm install && npm run dev
```

## Shared CALL-E call budget

20 free calls on the team account, then $0.05/call. Post in the group before making a real test call.
