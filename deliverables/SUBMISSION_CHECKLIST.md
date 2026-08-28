# Submission checklist — PSA Code Sprint 2.0

**Deadline: Saturday 30 August 2026, 23:59 Singapore time**

**How to submit:** Upload link is in your **registration confirmation email** (not on the public website). See `SUBMISSION_GUIDE.md`.

---

## Official clarifications (Telegram)

- PSA provides **no** datasets / LLM keys / credits → synthetic twin is correct.
- Main deck **≤10 slides**; **appendix allowed**.
- Video: **screen recording + voice-over** OK; camera not required.
- Links in slides/PDF **allowed** (put in appendix).
- Criteria weights: see kickoff briefing (not stated as equal on Telegram).

---

## Required uploads (3 items)

- [ ] **Demo video ≤10 min** — `RELAY_Demo_PSA_CodeSprint.mp4` (record per `DEMO_VIDEO_SCRIPT.md`)
- [x] **Presentation deck** — `RELAY_Presentation.pptx` (10 main + appendix A–D)
- [x] **Architecture write-up** — `ARCHITECTURE.pdf` (flow, decisions, impact, security/safety/scalability)

## Solution (working demo — for video / finals)

- [x] **Working agentic solution** — `relay/` (API + ops console)

## Supporting pack (not required for upload, keep locally)

- [x] Speaker script — `SPEAKER_SCRIPT.md`
- [x] Research memory — `research/00–11_*.md`
- [x] Live demo guide — `LIVE_DEMO_GUIDE.md`
- [x] Tests — `relay/backend/tests/test_core.py`

---

## Before upload

1. [ ] Find submission link in **confirmation email** (or email PSAC-PSACODESPRINT@globalpsa.com)
2. [ ] Record demo video (1080p, ≤10 min)
3. [ ] Paste **public repo URL** into Appendix D → `node create_slides.js`
4. [ ] Optional: team name on title slide
5. [ ] Optional: export deck to PDF
6. [ ] Run `./package_submission.sh` to zip files
7. [ ] Upload all three items before **30 Aug 23:59 SGT**

## Pre-submit dry run

```bash
# Terminal 1
cd relay/backend && PYTHONPATH=. python3 -m app.main

# Terminal 2
cd relay/frontend && npm run dev
```

1. Run all 3 scenarios; approve late feeder
2. Confirm metrics match slides (7 / 7 / 5 saved)
3. Record video per shot list
4. Upload via confirmation-email link

---

## Audit log

- 2026-08-23: code/tests/metrics — `research/09_audit_double_check.md`
- 2026-08-24: Telegram clarifications — `research/10_telegram_clarifications.md`
- 2026-08-28: Submission deadline + email upload — `research/11_submission_deadline.md`

## Judging self-score (treat all four as must-win)

| Criterion | Evidence in submission |
|-----------|------------------------|
| Agentic design & execution | State machine, 6 agents, tools, HITL, traces |
| Innovation | T/S connection continuity + critic dissent |
| Scalability & responsible AI | Policy gates, retries/fallback, token metrics, allowlist |
| Presentation & clarity | McKinsey-style deck (10+appendix) + script + live console |

## Contact

PSAC-PSACODESPRINT@globalpsa.com · Telegram group on site
