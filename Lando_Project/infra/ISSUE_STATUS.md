# Issue Status Tracker

This file captures follow-up status for review items related to IAI prototype and deployment.

## Issue #2 — Confirm neural network prototype meets requirements

**Status:** ✅ Confirmed in repository scope.

### What was validated
- Three-layer architecture exists (`ILL -> IPS -> CLL`) in
  `Lando_Project/infra/iai_neural_network.py`.
- Escalation behavior is present via confidence threshold routing in `IAIDecisionEngine`.
- Instinct synthesis exists (`add_circuit`) after high-value CLL outcomes.
- Unit tests verify both reflex and cognition paths in `tests/test_iai_neural_network.py`.

### Current constraints
- Prototype is simulation-level and not kernel-integrated.
- Uses deterministic heuristics and simple confidence math; no hardware-timed SNN runtime.

## Issue #3 — Deployment configuration reliability (Vercel)

**Status:** 🔄 In progress (guardrails added, continue monitoring).

### Current controls
- Root `index.html` provides fallback deployment entrypoint.
- `vercel.json` rewrites all routes to `/index.html` to prevent `NOT_FOUND` on deep links.
- `package.json` now provides local verification scripts for deployment checks.

### Monitoring actions
- Verify each deployment from Vercel dashboard includes the expected fallback message.
- Confirm route rewrites after each config change.

## Issue #4 — Deployment configuration maintainability

**Status:** 🔄 In progress (documentation and tracking expanded).

### Current controls
- Expanded autoscaling operational docs in `Lando_Project/infra/README_AUTOSCALING.md`.
- Added this tracker for explicit ownership of deployment follow-ups.

### Next recommended actions
- Add a CI smoke check to validate `vercel.json` rewrite schema and root file presence.
- Add environment-specific deployment notes (Preview vs Production) and rollback procedure.
