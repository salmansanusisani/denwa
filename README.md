# Denwa Frontend

React + TypeScript frontend foundation for Denwa — AI Callback Support Agent.

## What is included
- Responsive dashboard matching the supplied Denwa UI reference.
- Missed Calls list and Call Detail experience.
- Call History with search/filter controls and pagination UI.
- Knowledge Base document management UI.
- Responsive navigation for desktop/tablet/mobile.
- Loading/error/empty-state-ready component structure.
- Frontend-only mock view data for visual development; replace the data layer with real backend endpoints before judging/demo.

## Source-aligned scope
The implementation follows the supplied project specification: business onboarding/configuration, knowledge-base management, phone status, missed-call activity, call history/detail, follow-up, analytics and settings. The product UI does **not** add a customer-facing “Simulate Missed Call” control.

## Run
```bash
npm install
npm run dev
```

## Next integration step
Create `src/services/api.ts` and connect the screens to the agreed FastAPI contract. The frontend should consume real backend data for CallJob / CallResult states (`pending`, `in_progress`, `done`, `failed`) and preserve explicit loading, empty, error and retry states.
