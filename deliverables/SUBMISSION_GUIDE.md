# How to submit — PSA Code Sprint 2.0

**Deadline:** **Saturday 30 August 2026, 23:59 (Singapore time)**  
**Track:** Agentic AI in Action

---

## Where to submit

There is **no public submission link** on the website. Upload instructions are in your **registration confirmation email** (the email you received after signing up for the Code Sprint).

If you cannot find it:

1. Search inbox for **PSA Code Sprint**, **PSAC-PSACODESPRINT**, or **Agentic AI in Action**
2. Check spam / promotions
3. Email **PSAC-PSACODESPRINT@globalpsa.com** and ask for the submission upload link

The organiser (alohui) confirmed on Telegram (24 Aug): *“Instructions are in the confirmation email, please refer to it.”*

---

## What to upload (3 items)

Organisers listed these in the 27 Aug Telegram reminder:

| # | Deliverable | Our file | Status |
|---|-------------|----------|--------|
| 1 | **Demo video** (≤10 min) | `RELAY_Demo_PSA_CodeSprint.mp4` | You record — see `DEMO_VIDEO_SCRIPT.md` |
| 2 | **Presentation deck** (≤10 main slides) | `RELAY_Presentation.pptx` | Ready (10 main + appendix) |
| 3 | **Architecture write-up** — execution flow, key decisions, impact, security/safety/scalability | `ARCHITECTURE.pdf` (+ `.md`) | Ready |

**Before upload:** paste your public repo URL into slide **Appendix D**, then regenerate:

```bash
cd deliverables && node create_slides.js
```

Optional: export `RELAY_Presentation.pdf` from PowerPoint/Keynote if the upload form prefers PDF.

---

## Quick package (optional)

Bundle everything into one zip for upload or email attachment limits:

```bash
cd deliverables
./package_submission.sh
```

Output: `deliverables/RELAY_Submission_30Aug.zip` (video included only if you have already recorded it).

---

## Pre-upload checklist

- [ ] Video ≤10:00; screen + voice-over is fine (no camera required)
- [ ] Slides: main deck ≤10 slides (appendix OK)
- [ ] `ARCHITECTURE.pdf` covers flow, decisions, impact, security/safety/scalability
- [ ] Appendix D has your repo link (if sharing code)
- [ ] Team name on title slide (optional but recommended)
- [ ] Dry-run all 3 scenarios once more (`SUBMISSION_CHECKLIST.md`)

---

## After submitting

| Date | Milestone |
|------|-----------|
| **4 Sep 2026** | Shortlisted teams announced |
| **Sep–Oct** | Sprinternship with PSA mentors |
| **23 Oct 2026** | Finals at PSA Horizons |

Keep the repo and a local copy of the video — you may demo live at finals (`LIVE_DEMO_GUIDE.md`).

---

## Contacts

- **Event email:** PSAC-PSACODESPRINT@globalpsa.com  
- **Telegram:** PSA Code Sprint group (on psacodesprint.com)
