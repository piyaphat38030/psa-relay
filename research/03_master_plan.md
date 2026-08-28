# Master Plan — Build, Prove, Deliver (to 30 Aug)

## North star

Ship a **working, demoable, judge-proof** RELAY system + polished deliverables that dominate all four evaluation axes.

## Workstreams

### W1 — Domain & data (foundation)
- [ ] Synthetic terminal snapshot: vessels, berths, yard blocks, connections, reefers/DG flags  
- [ ] 3 canned disruption scenarios (late feeder, crane outage, ETA uncertainty + tool failure)  
- [ ] Deterministic **connection risk engine** (cutoff slack, move time, priority weights)

### W2 — Agentic runtime
- [ ] State machine: `IDLE → DETECTED → ANALYSING → PLANNING → CRITIQUE → AWAITING_APPROVAL → EXECUTING → CLOSED`  
- [ ] Six agent roles with structured outputs  
- [ ] Tool registry with retries, timeouts, failure injection  
- [ ] Policy engine: risk score → autonomy gate  
- [ ] Append-only execution trace (JSONL + API)  
- [ ] Demo mode (no API key) + optional live LLM mode

### W3 — Product UI
- [ ] Control room: terminal pulse, active incident, agent feed, plan comparison, approve/reject  
- [ ] Trace viewer (decisions / tools / approvals / errors)  
- [ ] Impact KPI strip: at-risk TEU, recoverable, estimated cost avoided, time-to-plan

### W4 — Hardening (Responsible AI)
- [ ] Input validation & schema constraints  
- [ ] Action allowlist; high-impact requires human token  
- [ ] Tool failure path in Scenario C  
- [ ] Token/cost accounting per run  
- [ ] README security & scalability section mirrored in architecture doc

### W5 — Deliverables
- [ ] Architecture explanation (markdown + PDF if needed)  
- [ ] ≤10 slides (McKinsey action-title style)  
- [ ] Non-AI-sounding speaker script  
- [ ] Demo video script + shot list  
- [ ] Submission checklist

## Scenario pack (for video + judging)

| ID | Trigger | What it proves |
|----|---------|----------------|
| S1 Late Feeder | ETA +14h on feeder | Full happy-path agentic loop + HITL restow |
| S2 Crane Outage | QC-07 down 6h | Multi-constraint replan; critic rejects unsafe plan |
| S3 Uncertainty + Tool Fail | AIS gap + yard API 503 | Uncertainty handling + fallback + escalation |

## Tech stack (chosen for speed + control)

- **Backend:** Python 3 + FastAPI + Pydantic  
- **Orchestration:** Custom (not thin LangChain wrapper) — shows team design  
- **Frontend:** Vite + React + TypeScript  
- **Storage:** SQLite (incidents, traces, approvals)  
- **LLM:** Optional OpenAI-compatible; **deterministic demo brain** always available  

## Definition of Done

1. `docker` or one-command local run boots UI + API  
2. Scenario S1–S3 complete end-to-end with visible traces  
3. Human can approve/reject and see executor effects  
4. Architecture doc + slides + script ready  
5. Self-test suite covers risk engine, policy gates, tool failure  

## Improvement pass (after first cut)

1. Tighten critic so it changes the winning plan at least once in S2  
2. Add cost model ($/missed connection, demurrage-style) for slide impact  
3. Visual polish: dark ops aesthetic, no generic purple-AI look  
4. Cut any feature that doesn’t serve a judging criterion  

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Looks like generic multi-agent demo | Lead with T/S domain engine + PSA narrative |
| LLM flaky in live demo | Demo brain default; LLM optional |
| Scope creep | Freeze tools list; only 3 scenarios |
| Thin HITL | Approval queue is first-class UI, not an afterthought |
