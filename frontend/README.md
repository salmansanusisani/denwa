# Frontend

Owns: company onboarding UI, intake form, call history dashboard.

## Tasks

- [ ] Company onboarding screen — create a demo company, upload its knowledge-base file(s)/text.
- [ ] Customer intake / simulate-call trigger — button that fires the "missed call" event with a phone number.
- [ ] Call history dashboard — table of past calls: caller number, question asked, answer given, resolved,
      timestamp.
- [ ] Call detail view — click into a call for the full structured result (+ transcript link if available).
- [ ] Basic auth/login screen — can be minimal / hardcoded demo login.

## Definition of Done

- [ ] All screens built and navigable end-to-end (no dead links/buttons).
- [ ] Onboarding form sends the uploaded doc to the backend's ingestion endpoint, shows success/failure state.
- [ ] Simulate-call button triggers the intake endpoint, shows a pending/loading state until a result comes back.
- [ ] Dashboard displays real backend data (not mock) for at least one full demo run.
- [ ] Handles "no result yet" and "call failed" states without breaking.
- [ ] Tested end-to-end on the exact browser/device the demo will be shown on.

## Layout

```
src/
├── main.jsx
├── App.jsx
├── api/
│   └── client.js     # fetch wrapper, VITE_API_BASE_URL
└── pages/
    ├── Login.jsx
    ├── Onboarding.jsx
    ├── IntakeSimulate.jsx
    ├── CallHistory.jsx
    └── CallDetail.jsx
```

## Run

```bash
npm install
npm run dev
```
