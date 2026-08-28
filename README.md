# PSA Code Sprint 2.0 — RELAY

**Chosen project:** Agentic transshipment connection continuity (human-in-the-loop).

## Why this wins

Open-ended brief → pick a PSA-deep problem. We chose **missed connection recovery** at a T/S hub — PSA’s core identity — and built a full agentic loop with tools, critic, approvals, and audit traces.

## Quick start

```bash
# Terminal 1 — API
cd relay/backend
PYTHONPATH=. python3 -m app.main

# Terminal 2 — UI
cd relay/frontend
npm install
npm run dev
```

Open http://localhost:5173

## Deliverables (deadline **30 Aug 2026, 23:59 SGT**)

| File | What |
|------|------|
| `deliverables/RELAY_Presentation.pptx` | ≤10 main slides + appendix |
| `deliverables/ARCHITECTURE.md` / `.pdf` | Required architecture explanation |
| `deliverables/RELAY_Demo_PSA_CodeSprint.mp4` | ≤10 min demo video (you record) |
| `deliverables/SUBMISSION_GUIDE.md` | **How to upload** (confirmation email link) |
| `deliverables/SUBMISSION_CHECKLIST.md` | Final checklist |
| `deliverables/DEMO_VIDEO_SCRIPT.md` | Shot list for video |
| `deliverables/package_submission.sh` | Zip files for upload |
| `research/` | Brief, options, choice, master plan |

## Tests

```bash
cd relay/backend
PYTHONPATH=. python3 tests/test_core.py
```

## Memory / research

1. `research/00_challenge_brief.md`  
2. `research/01_option_analysis.md`  
3. `research/02_winning_choice.md`  
4. `research/03_master_plan.md`
