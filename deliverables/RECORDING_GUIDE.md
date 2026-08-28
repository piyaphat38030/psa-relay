# How to record your submission video — do this

**Deadline:** 30 Aug 2026, 23:59 SGT  
**Output file:** `deliverables/RELAY_Demo_PSA_CodeSprint.mp4`

---

## Which script is the real one?

| File | When to use |
|------|-------------|
| **`DEMO_VIDEO_SCRIPT.md`** | **← USE THIS to record the submission video** (due 30 Aug) |
| `SPEAKER_SCRIPT.md` | Live talk at finals (23 Oct) — slides + optional live demo |
| `LIVE_DEMO_GUIDE.md` | Cheat sheet for finals day only — shorter cues, not for recording |

**You are recording one video**, not two. The presentation deck is a **separate upload** (PDF/PPTX). In the video you only show **4 slides as bookends**; the main content is the **ops console**.

---

## How slides + demo fit together (submission video)

```
┌─────────────────────────────────────────────────────────────┐
│  SLIDE 1 (title)          ~20 sec   voice-over              │
│  SLIDE 3 (problem)        ~35 sec   voice-over              │
├─────────────────────────────────────────────────────────────┤
│  CONSOLE — late_feeder      ~3.5 min  Run → trace → Approve │
│  CONSOLE — crane_outage     ~45 sec   Run → PLAN-X          │
│  CONSOLE — uncertainty      ~50 sec   Run → tool_error      │
├─────────────────────────────────────────────────────────────┤
│  SLIDE 6 (architecture)   ~35 sec   voice-over              │
│  SLIDE 10 (close)         ~20 sec   voice-over              │
└─────────────────────────────────────────────────────────────┘
Total: ~7:00–8:30 (under 10 min limit)
```

**Submission uploads (3 separate files):**
1. This video (MP4)
2. `RELAY_Presentation.pptx` (full deck — judges read this separately)
3. `ARCHITECTURE.pdf`

---

## Step-by-step: record today

### Step 1 — Servers (already running if you followed launch)

**Terminal 1 — API:**
```bash
cd relay/backend
PYTHONPATH=. python3 -m app.main
```

**Terminal 2 — UI:**
```bash
cd relay/frontend
npm run dev
```

Open **http://localhost:5173** — top-right should say **System online** (green badge in the navy header).

### Step 2 — Open your slides

Open `deliverables/RELAY_Presentation.pptx` in PowerPoint or Keynote.  
You only need slides **1, 3, 6, 10** during recording (know where they are).

### Step 3 — Set up screen recording

**Mac:** QuickTime → File → New Screen Recording, or **Cmd+Shift+5**  
- Record **entire screen** or the monitor with browser + slides  
- Turn on **microphone** for voice-over  
- 1080p if your tool allows it  

**Alternative:** OBS, Zoom “record screen”, Loom — any is fine per organisers.

**Before you hit Record:**
- [ ] Browser zoom **100–110%** (the UI is light/enterprise — readable at default zoom)
- [ ] Hide bookmarks bar; close Slack/notifications
- [ ] Full-screen or clean desktop
- [ ] Do one **dry run** of late_feeder (see checklist below)

### Step 4 — Record following `DEMO_VIDEO_SCRIPT.md`

Open `deliverables/DEMO_VIDEO_SCRIPT.md` on a **second screen or phone** — read the voice-over sections while recording.

**Feature checklist — you must show all of these on screen:**

| Feature | Where to show it | Scenario |
|---------|------------------|----------|
| PSA context stats | Left sidebar | Any |
| System online badge | Top bar (navy header) | Any |
| Phase stepper | Main panel after Run | late_feeder |
| Streaming execution trace | Right panel | late_feeder |
| Tool calls in trace (blue) | Scroll trace | late_feeder |
| At-risk table + connection buffer | Main panel | late_feeder |
| Three plans + critic notes | Plan cards | late_feeder |
| Human approval gate (amber box) | Main panel | late_feeder |
| Click **Approve** | Main panel | late_feeder |
| Success banner + connections saved | Green banner | late_feeder |
| Dispatched work orders | Below banner | late_feeder |
| Terminal twin (vessels, cranes) | Bottom of main panel | late_feeder |
| PLAN-X killed by Critic | Plan card + critic note | crane_outage |
| Tool error in trace (red) | Right panel | uncertainty_tool_fail |
| Yard fallback hint | Yellow hint text | uncertainty_tool_fail |
| Partial recovery (not 100%) | KPI / result | uncertainty_tool_fail |

### Step 5 — Dry run order (do once before recording)

1. **Late feeder** → Run → wait for trace to finish streaming → scroll trace → read plans → **Approve** → confirm 7 saved + work orders
2. **Crane outage** → Run → point at PLAN-X critic REJECT note → (optional approve PLAN-A)
3. **Uncertainty + tool fail** → Run → scroll to tool_error in trace → show partial at-risk

### Step 6 — Export

- Save as **`deliverables/RELAY_Demo_PSA_CodeSprint.mp4`**
- Watch once: audio clear, text readable, under 10:00

### Step 7 — Package & upload

```bash
cd deliverables
./package_submission.sh
```

Upload via link in your **registration confirmation email**:
- Video MP4
- `RELAY_Presentation.pptx`
- `ARCHITECTURE.pdf`

---

## Recording flow (minute-by-minute)

| Time | Window | Action |
|------|--------|--------|
| 0:00 | Slide 1 | Intro (~20 sec) |
| 0:20 | Slide 3 | PSA context (~35 sec) |
| 0:55 | Browser | Landing — point sidebar + System online |
| 1:05 | Browser | Late feeder → **Run scenario — Feeder ETA slip…** |
| 1:30 | Browser | Scroll execution trace (tool_call / tool_result) |
| 2:15 | Browser | At-risk table (skip if short on time) |
| 2:35 | Browser | Recovery plan comparison — PLAN-B + critic notes |
| 3:15 | Browser | Amber approval box |
| 3:35 | Browser | **Approve plan** → work orders → terminal twin |
| 4:30 | Browser | QC-07 scenario → **Run** → PLAN-X rejected |
| 5:15 | Browser | AIS/yard scenario → **Run** → tool_error in trace |
| 6:05 | Slide 6 | Architecture (~35 sec) |
| 6:40 | Slide 10 | Close (~20 sec) |

Full voice-over text: **`DEMO_VIDEO_SCRIPT.md`**

---

## If something breaks mid-recording

- API offline → restart Terminal 1 command above  
- Page blank → refresh http://localhost:5173  
- Bad take → keep recording; cut in iMovie/QuickTime later, or re-record one section  

---

## After submission (finals, 23 Oct)

Use **`SPEAKER_SCRIPT.md`** + **`LIVE_DEMO_GUIDE.md`**: present slides live, switch to console for late_feeder demo, Q&A. Same app, different format.
