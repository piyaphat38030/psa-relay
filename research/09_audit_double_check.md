# Audit log — double-check pass (2026-08-23)

## Challenge brief vs delivery

| Requirement | Status |
|-------------|--------|
| Agentic: analyse → decide → tools → uncertainty/failure → HITL → trace | ✅ All three scenarios |
| Video ≤10 min | ⬜ User must record (`DEMO_VIDEO_SCRIPT.md`) — screen + VO OK |
| Slides ≤10 main (+ appendix OK) | ✅ 10 main + A1–A4 in `RELAY_Presentation.pptx` |
| Architecture / flow / decisions / impact / security | ✅ `ARCHITECTURE.md` + PDF |
| Higher autonomy not automatically better | ✅ Policy + slide 4 + approval tokens |

## Code health

| Check | Result |
|-------|--------|
| `pytest` (5 tests) | ✅ Pass (incl. plan≈result alignment) |
| Frontend `npm run build` | ✅ Pass |
| API `/health`, `/meta`, run+approve | ✅ Pass |
| Slide metrics vs twin | ✅ Match (7 / 7 / 5 saved) |
| Simulator undercount bug | ✅ Fixed (fleet-wide saved count) |

## Issues found & fixed this pass

1. **PLAN card vs result mismatch** — PLAN-B showed “save 2” then closed with 7. Cause: simulator only counted restow targets, not cutoff spillover. Fixed in `tools/registry.py`; test asserts |sim−actual| ≤ 2.
2. **README stale** — said feeder ETA +14h; actual scenario is +5.5h. Fixed.
3. **`docs/ARCHITECTURE.md` stale** vs deliverables copy. Synced + regenerated PDF.

## Remaining (user action)

1. Record demo video ≤10 min before **30 Aug** (screen + voice-over; no camera needed)
2. Paste public repo URL into Appendix D before upload
3. Add team name on title slide if desired
4. Register / upload via **confirmation email** link (see `SUBMISSION_GUIDE.md`)
5. Rehearse live demo 3× (`LIVE_DEMO_GUIDE.md`)

## Follow-up (2026-08-24)

Telegram clarifications applied — see `research/10_telegram_clarifications.md`.

## Intentional (not bugs)

- PLAN-A late_feeder sim saves **0** — restow alone cannot beat deep ETA slip; PLAN-B needs cutoff negotiation. Good story for judges.
- Uncertainty leaves **7 residual** at-risk — honest partial recovery.
- Synthetic twin costs — always labeled illustrative.
