# Winning Choice — RELAY

## One-liner

**RELAY** is a human-in-the-loop agentic system that detects transshipment connection risk at a PSA-style hub and orchestrates recovery — from triage to approved work orders — with a full execution audit trail.

## Problem (ops reality, not buzzwords)

PSA Singapore is the world’s premier **transshipment** hub. A large share of boxes are not origin/destination cargo; they are **connections** between vessels with hard cutoffs.

When any of these hits:
- Feeder/mainline **ETA slip**
- **Crane** or berth constraint
- **Yard hotspot** / dwell spike
- Incomplete AIS / weather uncertainty

…planners must decide, under time pressure and incomplete data, which boxes to **expedite, restow, hold, or rebook** — and which moves are too costly/risky without approval.

Today that coordination is fragmented across systems and humans. Missed connections create cascading network pain far beyond one terminal.

## Objective

**Maximise recoverable connections under operational constraints while never silently executing high-impact physical moves.**

## Autonomy model (explicit, judge-facing)

| Layer | Mode | Examples |
|-------|------|----------|
| Sense & triage | **Autonomous** | Ingest alert, classify severity, pull state |
| Impact & options | **Autonomous** | Score at-risk boxes, generate plans, dissent review |
| Low-risk actions | **Autonomous** | Draft carrier notice, open incident dossier, refresh forecasts |
| High-impact actions | **Human-in-the-loop** | Priority restow, cutoff extension request, berth preference change, hazmat/reefer expedite |
| Irreversible / safety | **Escalate / block** | DG segregation conflicts, missing critical fields |

## Agent architecture (team-designed)

1. **Sentinel** — watches event stream; opens an incident when risk threshold crossed  
2. **Analyst** — builds connection-impact graph; uncertainty bands on ETA/cutoffs  
3. **Planner** — proposes ranked recovery plans using domain scoring (deterministic) + LLM rationale  
4. **Critic (Dissent)** — attacks top plan (capacity, time, cost, failure modes)  
5. **Executor** — runs approved tool calls; retries/fallbacks on tool failure  
6. **Auditor** — immutable execution trace for every decision, tool, approval, error  

Orchestrator owns **state machine** + **policy gates** (not “LLM decides everything”).

## Tool surface (mocked PSA-style systems)

- `vessel_schedule.get` / `eta.update`  
- `connections.query_at_risk`  
- `yard.inventory_lookup` / `yard.hotspot_score`  
- `crane.availability`  
- `recovery.simulate_plan` (what-if)  
- `workorder.draft` / `workorder.dispatch` (requires approval above threshold)  
- `notify.carrier` / `notify.internal`  
- `weather.get` / `ais.uncertainty`  
- Injected `tool.fail` scenarios for demos  

## Why this wins on each criterion

| Criterion | How RELAY scores |
|-----------|------------------|
| Agentic design & execution | Full E2E workflow: event → tools → state → HITL → actions → trace |
| Innovation | T/S-connection-first; hybrid domain engine + multi-agent dissent |
| Scalability / Responsible AI | Tiered autonomy; RBAC-ready approvals; token-light structured tools; audit log |
| Presentation | Control-room demo with numbers (connections saved, cost avoided, latency) |

## Non-goals (keep scope winning)

- Not a full berth optimiser  
- Not a chatbot for general Q&A  
- Not claiming live PORTNET access (use realistic mocks + clear integration path)  
- Not maximum autonomy for its own sake  

## Product surface for judges

1. **Ops Console** — live incident, agent timeline, approval queue  
2. **API + agent runtime** — reproducible scenarios  
3. **Architecture brief** — design decisions & responsible AI  
4. **≤10 McKinsey-style slides** + speaker script  
5. **≤10 min demo video script** (and runnable demo for recording)
