# Live demo guide — presentation & finals

A **live run** of RELAY during your talk often beats a pre-recorded video alone. Judges see you trust the system. Use this guide for submission video **and** 23 Oct finals if shortlisted.

**Submission video (Telegram):** screen recording + voice-over is enough — camera not required.

---

## Should you demo live?

| Option | When to use |
|--------|-------------|
| **Pre-recorded video only** | Safe submission by 30 Aug; no live risk |
| **Slides + live demo** | Shortlist / finals — **recommended** if rehearsed |
| **Hybrid (best)** | Submit video; present live at finals with same script |

Recommendation: **Record the video first** (backup). At finals, open with 2 slides, then **live late_feeder**, keep crane outage as rapid second act if time allows.

---

## 5-minute live demo script (fits inside 10-slide talk)

Speak naturally — these are full sentences you can adapt, not bullet fragments.

| Time | You do | What to say |
|------|--------|-------------|
| 0:00 | Slide 2 | "I'll start with the overview. RELAY handles transshipment connection recovery — when a schedule shock puts boxes at risk of missing their outbound vessel, the system detects that, generates recovery options, and pauses before any physical move unless a planner approves. We built it specifically around what the Agentic AI brief asks for: tools, state, human oversight, and a clear trace." |
| 0:20 | Alt-tab to console | "This is the ops console we built. On the left are our three demo scenarios and some PSA context — the transshipment share, off-schedule arrivals, rehandling increase. The main panel shows the incident, and the right panel streams the execution trace as each agent runs." |
| 0:40 | **Late feeder** → Run | "I'm going to run the late feeder scenario first. A feeder ETA slips five and a half hours, which collapses the connection buffer for several transshipment boxes. Watch the trace on the right — you'll see each agent step appear as it happens." |
| 1:00 | KPIs + stepper | "So we end up with seven containers in the miss window, and the expected loss on our cost model is in the five-figure range. The phase stepper shows where we are in the lifecycle — we've gone through detection, analysis, planning, and critique, and now we're waiting for approval." |
| 1:20 | Scroll trace | "If I scroll the trace, Sentinel pushed the ETA revision and opened the incident. Analyst called the connections tool and built the at-risk set from our risk engine — that's deterministic, so the numbers are reproducible. Planner then simulated three recovery options." |
| 1:50 | Plans | "PLAN-A is aggressive restow across the full set. PLAN-B negotiates a cutoff extension and does selective restow on premium and reefer boxes. PLAN-C holds for the next sailing. Critic ran on each, and PLAN-B was recommended." |
| 2:15 | Approval box | "This yellow box is the human gate. Low-risk notifications already went out, but restow and cutoff actions are blocked until I approve. That's the tiered autonomy model — the agents do the analysis, the planner owns the physical moves." |
| 2:35 | Approve | "I'll approve PLAN-B now." |
| 2:50 | Closed + work orders | "Executor dispatched the work orders — you can see them here — and Auditor re-scored the terminal. All seven connections recovered, full trace from start to finish." |
| 3:10 | **Crane outage** → Run | "Quick second scenario — QC-07 goes down. Planner generates PLAN-X, which looks great on score, but Critic rejects it because it assumes crane capacity that isn't there. That's the dissent agent actually changing the outcome." |
| 3:50 | Slide 10 | "That's RELAY. Happy to re-run any scenario or go deeper on the architecture. Questions?" |

Total: ~4–5 min live + ~5 min slides = comfortable 10 min.

---

## Setup checklist (day before)

```bash
# Terminal 1 — API
cd relay/backend
PYTHONPATH=. python3 -m app.main

# Terminal 2 — UI
cd relay/frontend
npm run dev
```

Verify:

```bash
curl -s http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:8000/api/scenarios | head
```

Open http://localhost:5173 — run **late_feeder** once dry; note which plan is selected (should be **PLAN-B**).

---

## Presentation-day checklist

1. **Kill stray servers** — `lsof -ti:8000 | xargs kill -9` then restart clean  
2. Browser: **110–125% zoom**, hide bookmarks, full screen  
3. **Do not** rely on Wi‑Fi for API — everything local  
4. Close Slack/notifications  
5. Have **RELAY_Presentation.pptx** open on slide 2 before starting  
6. Optional: second monitor = console, main = slides  
7. If live demo fails: “Let me show the recorded path” → play submitted video clip  

---

## What to point at (judge attention)

1. **Phase stepper** — state machine, not chat  
2. **Trace panel** — tool_call / tool_error / approval_request colors  
3. **Connection buffer (h)** column — domain metric  
4. **PLAN-X killed** in crane scenario — innovation / responsible AI  
5. **Residual at-risk** in uncertainty scenario — honest partial recovery  

---

## Tough Q&A — fuller answers you can shorten on the spot

| Question | How to answer |
|----------|----------------|
| "Is this connected to real PSA systems?" | "Not yet — we built a synthetic terminal twin because PSA didn't provide live data for this round. But the tool contracts — schedule updates, yard lookup, crane status, work order dispatch — are shaped the way we'd expect PORTNET-class APIs to work. The sprinternship would be about wiring those up for real." |
| "Why not full autonomy?" | "Because the brief says higher autonomy isn't automatically better, and more importantly because a wrong restow order has real consequences — crane time, yard congestion, knock-on delays. We let the agents do triage and planning automatically, but anything that moves boxes or changes a sailing cutoff needs a human sign-off." |
| "Where's the LLM?" | "The orchestration layer can use an LLM for operator-facing rationale, but the scoring and simulation are deterministic — same inputs give you the same risk numbers every time. We wanted the demo to be reproducible and auditable, which is what ops teams actually need." |
| "How is this different from a chatbot?" | "A chatbot gives you text. RELAY runs a state machine — it calls tools, updates terminal state, simulates recovery options, gates physical moves behind approval, and produces a trace you can audit. If you want to see whether it's agentic, follow the trace." |
| "How does this relate to the Maritime Digital Twin?" | "The digital twin is about situational awareness — where things are across the network. RELAY is what you'd run on top when something breaks — scenario simulation, plan ranking, human approval, and an audit trail of what was decided and why." |

---

## Recording tips (for submission video)

- Same script as live, but **pause 2 sec** on approval click  
- Capture trace scroll slowly — judges read text  
- Burn captions if possible  
- Export 1080p H.264 → `RELAY_Demo_PSA_CodeSprint.mp4`

---

## Rehearsal count

Minimum **3 full runs** aloud with timer:

1. Slides only (7 min)  
2. Live only (5 min)  
3. Combined (9 min max — leave 1 min buffer)
