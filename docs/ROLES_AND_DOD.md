# Denwa — Roles, Definition of Done & Working Agreement (condensed)

Full version: uploaded PDF "Denwa_Roles_and_DoD.pdf". Per-role task lists and DoD also live in each role's own
README (`frontend/README.md`, `backend/README.md`, `ai-ml/README.md`) so you don't have to open this file while
heads-down in one folder.

## Asking for help

```
[BLOCKED] <area> — what you were doing / what you expected / what actually happened /
what you already tried / how urgent (blocking now vs. can wait)
```

Always say what you already tried. Tag `urgent` only if it's actually blocking you right now. For CALL-E-specific
issues, check their Discord/docs first and link what you found either way. Post a one-line follow-up once
resolved.

## Suggesting an upgrade mid-build

```
[IDEA] <short title> — what it improves / effort (small/medium/large) / does it touch anyone else's part
```

Small ideas (no API/schema change): just do it, mention it after. Medium/large (new field, new endpoint, changes
another role's output): post it, get a thumbs-up from whoever it affects, before building it. Not core to the MVP
demo → log it as a stretch goal, don't build it now.

## Git workflow

- `main` is always demo-ready.
- Branch per person: `frontend/<short-task>`, `backend/<short-task>`, `ml/<short-task>`.
- `.env.example` has variable names only — real keys stay in a git-ignored local `.env`.
- Before every push to `main`: pull + resolve conflicts locally, run the code (don't just assume), check for
  secrets in the diff, tell affected roles if you touched a shared contract, write a real commit message.
- At least one other person glances at the diff before it lands on `main` — especially anything touching CALL-E
  or the shared data model.

## Milestones

1. **Foundations** — repo set up, everyone runs their part locally, CALL-E account/API key confirmed working.
2. **Core paths in isolation** — Frontend creates a company + uploads a doc. AI/ML retrieves relevant chunks for
   a test question. Backend's job queue + region resolver work standalone.
3. **End-to-end wired** — Simulate-call button → real CALL-E call placed using retrieved company data.
4. **Polish + demo rehearsal** — full demo flow run at least twice before submission.
