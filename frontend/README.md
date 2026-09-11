# Denwa Frontend

React + Vite + TypeScript UI for **Denwa**, an AI-powered callback support system. Talks to the
FastAPI backend at `http://127.0.0.1:8000/api/v1` (override with `VITE_API_BASE_URL`).

## What is included

- **Onboarding / sign-in** — create a workspace by business number, or sign back in via
  “Find my business by phone number” and saved workspaces (localStorage).
- **Dashboard** — live missed-call activity with a real status badge per workspace.
- **Missed Calls** — list + detail; call state reflects backend `CallJob`/`CallResult`.
- **Call History** — search/filter/pagination over real results.
- **Knowledge Base** — upload FAQ/docs; chunk/embed status comes from the backend.
- **Phone Numbers / Settings** — live provider status (CALL-E, Telnyx, Groq, worker) from
  `/api/v1/internal/dev/config-status`; the Dashboard “Configure” button lands here.
- **Analytics / Team** — roadmap placeholders.
- Loading / empty / error / retry states throughout; HMR-safe root mount.

The backend worker and the RAG pipeline drive every screen — there is no mock data layer anymore.

## Run

```bash
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Notes

- The product UI intentionally does not ship a customer-facing “Simulate Missed Call” control; that
  flow stays a dev-only API (`POST /api/v1/internal/dev/trigger-callback`) and curl recipe in the
  root README.
- Sandboxes the frontend API base behind `VITE_API_BASE_URL` so it can point at a tunnel URL for
  demos without a code change.