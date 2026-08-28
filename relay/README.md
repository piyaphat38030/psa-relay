# RELAY — Agentic Transshipment Connection Continuity

Human-in-the-loop agentic AI for **PSA Code Sprint 2.0**.

When vessel ETAs slip or terminal constraints hit, RELAY detects at-risk connections, plans recovery, stress-tests options, seeks human approval for high-impact moves, and executes with a full audit trail.

## Quick start

**Backend first** — the UI proxies API calls to port 8000.

**No pip packages required** (Python 3.11+ stdlib).

```bash
# Terminal 1 — API http://127.0.0.1:8000
cd backend
PYTHONPATH=. python3 -m app.main
```

```bash
# Terminal 2 — UI http://127.0.0.1:5173
cd frontend
npm install
npm run dev
```

The ops console shows an **API live** badge when the backend is reachable.

## Scenarios

| ID | Trigger |
|----|---------|
| `late_feeder` | Feeder ETA +5.5h (off-schedule bunching) — connection buffer collapses |
| `crane_outage` | QC-07 downtime — critic rejects unsafe PLAN-X |
| `uncertainty_tool_fail` | AIS gap + yard API 503 — retry, cache fallback, partial recovery |

## Agent loop

1. **Sentinel** — ingest trigger, update ETA, notify duty officer  
2. **Analyst** — query connections, score risk, handle tool failures  
3. **Planner** — generate PLAN-A/B/C (+ PLAN-X in crane scenario)  
4. **Critic** — dissent, adjust scores, recommend best plan  
5. **Human** — approve/reject high-impact actions  
6. **Executor + Auditor** — dispatch work orders, re-score, append trace  

Each run is synchronous (one API call) but the UI **streams the trace** for demo visibility.

## Tests

```bash
cd backend
PYTHONPATH=. python3 tests/test_core.py
```

9 tests: risk engine, policy, E2E scenarios, reject/escalate, double-approve guard, plan invariants.

## Deliverables

Slides, architecture brief, video script, and submission guide live in the parent repo:

```
../deliverables/
  RELAY_Presentation.pptx
  ARCHITECTURE.pdf
  SUBMISSION_GUIDE.md
  DEMO_VIDEO_SCRIPT.md
```

## API (selected)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Liveness |
| GET | `/api/meta` | Domain context + tool list |
| POST | `/api/incidents/run` | Run scenario (`scenario_id`, `auto_approve`) |
| POST | `/api/incidents/{id}/approvals/{apr}` | Approve or reject |
| GET | `/api/incidents/{id}/terminal` | Twin state (vessels, cranes, work orders) |
