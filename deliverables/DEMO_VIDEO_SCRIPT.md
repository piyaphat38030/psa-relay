# Demo video script (≤10 minutes)

**Target length:** ~7:30–8:30 (leaves buffer under 10:00)  
**Format:** Screen recording + voice-over. Camera not required.

**Before recording:** Backend on port 8000, frontend on **http://localhost:5173**, header shows **System online**. Open slides 1, 3, 6, 10 in PowerPoint/Keynote.

---

## 0:00–0:20 · Slide 1 (title)

**Visual:** Slide 1 full screen.

**Say:**
"Hi — this is RELAY for PSA Code Sprint 2026, Agentic AI in Action. RELAY helps transshipment planners recover container connections when schedules break — with agentic orchestration and human approval on high-impact moves. I'll show the full workflow in the console."

---

## 0:20–0:55 · Slide 3 (situation)

**Visual:** Slide 3 full screen.

**Say:**
"Quick context: roughly ninety percent of PSA throughput is transshipment, and PSA reported ~ninety percent of vessels off-schedule in 1H 2024. What matters isn't just 'how late is the feeder' — it's the **connection buffer** between when a box can be available and when its outbound vessel closes. RELAY scores that risk and plans recovery. Details are in our deck; now the live demo."

---

## 0:55–1:05 · Console landing

**Visual:** Switch to browser — **http://localhost:5173**

**Do:**
1. Show full console for ~3 seconds (left sidebar, KPI row, main panel, trace panel).
2. **Point at** left sidebar → PSA context stats.
3. **Point at** top-right → **System online** badge.

**Say:**
"Here's the ops console. Three demo scenarios on the left — synthetic Tuas-style twin, no PSA dataset this round. API is live."

---

## 1:05–4:30 · Scenario 1 — Late feeder (main demo)

### 1:05 — Select & run

**Do:**
1. **Click** left sidebar card: **"Feeder ETA slip threatens mainline connections"** (first card — should highlight blue if not already selected).
2. **Click** top-right button: **"Run scenario — Feeder ETA slip threatens mainline connections"**.
3. Wait ~5–8 sec until status pill shows **awaiting approval** and trace stops streaming (right panel shows full event count).

**Say:**
"Late feeder scenario — ETA slips five and a half hours. I hit run; the agent pipeline starts. Phase stepper shows lifecycle; trace streams on the right."

---

### 1:30 — Trace (Sentinel + Analyst)

**Do:**
1. **Click** inside the right **Execution trace** panel.
2. **Scroll down** slowly through trace events — pause on one **tool_call** (blue left border) and one **tool_result** (green).

**Say:**
"Sentinel updates the ETA and opens the incident. Analyst calls yard and connections tools — seven boxes at risk, five-figure expected loss. Numbers come from our deterministic risk engine, not guesses. Tool calls and results are in the trace."

---

### 2:15 — At-risk table

**Do:**
1. **Scroll** main (centre) panel until **At-risk containers** table is visible.
2. Briefly **hover** over a row showing **Buffer (h)** column.

**Say:**
"Each row is a transshipment link — container, vessels, risk score, connection buffer in hours."

---

### 2:35 — Plans + Critic

**Do:**
1. **Scroll down** to **Recovery plan comparison**.
2. **Pause** on **PLAN-B** card (has **Selected** badge after run completes — if not selected yet, point at highest-scored plan).
3. **Expand** view on PLAN-X area only if visible — skip; point at critic bullet notes under PLAN-A / PLAN-B / PLAN-C.

**Say:**
"Planner generates three options simulated against the twin. PLAN-B — cutoff extension plus selective restow — wins after Critic stress-tests yard capacity and DG paths. Critic notes are on each card."

---

### 3:15 — Approval gate

**Do:**
1. **Scroll up** slightly so the amber **Approval required** box is centred on screen.

**Say:**
"System pauses here by design — notifications run automatically; restow and cutoff moves need a planner sign-off. Brief says higher autonomy isn't automatically better."

---

### 3:35 — Approve & results

**Do:**
1. **Click** **"Approve plan"** (white button inside amber box).
2. Wait ~2 sec for green **Recovery complete** banner.
3. **Scroll down** past banner → **Dispatched work orders** list.
4. **Scroll down** to **Terminal twin — Tuas Hub** section (vessels + cranes).

**Say:**
"Approve — Executor dispatches work orders, Auditor re-scores. Seven connections saved, loss avoided shown in the banner. Twin panel shows vessel and crane state. Full trace from trigger to close."

---

## 4:30–5:15 · Scenario 2 — Crane outage

**Do:**
1. **Click** left sidebar: **"QC-07 downtime compresses feeder workface"**.
2. **Click** **"Run scenario — QC-07 downtime compresses feeder workface"**.
3. Wait for **awaiting approval** (or **closed** if you approve — approval optional here).
4. **Scroll** to **Recovery plan comparison** → **Pause on PLAN-X** card (greyed / critic notes mention crane / infeasible).

**Say:**
"Crane QC-07 is down. PLAN-X looks good on score but Critic rejects it — assumes crane capacity that doesn't exist. Feasible plan selected instead. Critic actually changes the outcome."

*(Optional: click **Approve plan** if you want to show execution — skip to save time.)*

---

## 5:15–6:05 · Scenario 3 — Uncertainty + tool fail

**Do:**
1. **Click** left sidebar: **"AIS gap + yard API failure under weather degradation"**.
2. **Click** **"Run scenario — AIS gap + yard API failure under weather degradation"**.
3. Wait for run to finish (**awaiting approval**).
4. **Click** right trace panel → **Scroll** until you find a **tool_error** event (red left border).
5. **Scroll** main panel → point at amber **Yard position API degraded** hint (if visible).
6. **Point at** KPI **At-risk connections** vs **Connections saved** (still **—** until approve — or scroll to plans showing partial save count **5**).

**Say:**
"AIS degraded, yard API throws 503 — retry then cache fallback in the trace. Reefer verify flag. Partial recovery by design — five of twelve saved, residual risk visible. Honest under bad data."

*(Skip Approve here to save time — judges see partial numbers on plan cards.)*

---

## 6:05–6:40 · Slide 6 (architecture)

**Visual:** Switch to Slide 6 full screen.

**Say:**
"Architecture: deterministic domain engine for risk and simulation; Python orchestrator state machine; React ops console. Agents orchestrate tools — engine does the math. Synthetic twin this round; same API contracts for sprinternship integration. Full detail in ARCHITECTURE.pdf."

---

## 6:40–7:00 · Slide 10 (close)

**Visual:** Slide 10 full screen.

**Say:**
"That's RELAY — agentic transshipment recovery with human gates and full audit trail. Deck, architecture doc, and code in the submission. Thanks for watching."

---

## Timing summary

| Time | Where | Action |
|------|-------|--------|
| 0:00 | Slide 1 | Voice-over |
| 0:20 | Slide 3 | Voice-over (short) |
| 0:55 | Console | Show landing, point sidebar + badge |
| 1:05 | Console | Late feeder → **Run** |
| 1:30 | Console | Scroll trace |
| 2:15 | Console | At-risk table |
| 2:35 | Console | Plans + critic |
| 3:15 | Console | Approval box |
| 3:35 | Console | **Approve** → work orders → twin |
| 4:30 | Console | Crane outage → **Run** → PLAN-X |
| 5:15 | Console | Uncertainty → **Run** → tool_error |
| 6:05 | Slide 6 | Voice-over |
| 6:40 | Slide 10 | Close |

**~7:00 minimum if you talk fast · ~8:30 comfortable pace**

---

## Pre-record checklist

- [ ] `http://localhost:5173` loads, **System online** visible
- [ ] Dry-run late feeder once end-to-end (Run → Approve → 7 saved)
- [ ] Browser zoom 100–110%, bookmarks hidden
- [ ] Slides 1, 3, 6, 10 ready to alt-tab
- [ ] Export: 1080p → `deliverables/RELAY_Demo_PSA_CodeSprint.mp4`

---

## If running long

Cut in this order:
1. Skip at-risk table scroll (2:15 block)
2. Skip terminal twin scroll (last step of 3:35)
3. Shorten Slide 3 to 30 sec
4. Skip uncertainty scenario Approve explanation — already skipped

## If something breaks

- Refresh browser; re-run backend if **Offline**
- Bad take: pause recording, redo that segment, cut in editor later
