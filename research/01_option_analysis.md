# Project Option Analysis — What Could We Build?

Scoring (1–5) against judging criteria and “wow / win” potential.  
Assumption: ~7 days to a demo-ready E2E product for 30 Aug submission.

## Options considered

### A. Transshipment Connection Continuity Agent (**RELAY**)
**Problem:** When a mainline/feeder ETA slips or a yard/crane constraint appears, connecting boxes risk missing onward vessels — core risk for the world’s largest T/S hub.  
**Agentic fit:** Alert → impact graph → recovery options → tool orchestration → HITL for costly moves → audit trace.  
**Scores:** Design 5 · Innovation 5 · Responsible 5 · Present 5 · Buildability 4 · Wow 5  
**Risk:** Needs credible domain model (connections, dwell, cutoffs).

### B. Berth Bunching / Congestion Cascade Responder
**Problem:** Vessel bunching after Red Sea / schedule recovery overwhelms berths and yards.  
**Agentic fit:** Strong multi-resource replan story.  
**Scores:** Design 4 · Innovation 3 · Responsible 4 · Present 4 · Buildability 3 · Wow 4  
**Risk:** Crowded theme; overlaps generic “port congestion AI”; harder to fake berth optimiser convincingly.

### C. PORTNET / L2 Incident Intelligence Agent
**Problem:** Duty officers triage EDI/API/vessel-advice failures.  
**Scores:** Design 4 · Innovation 2 · Responsible 4 · Present 3 · Buildability 4 · Wow 3  
**Risk:** Done in 2025 (PORTALIS). Low originality.

### D. Conversational Global Network Assistant
**Problem:** “What-if” for network disruptions.  
**Scores:** Design 3 · Innovation 2 · Responsible 3 · Present 3 · Buildability 4 · Wow 2  
**Risk:** 2025 theme (PORTUS AI). Looks like chatbot.

### E. Empty Repositioning / Equipment Balancing Agent
**Problem:** Empties imbalance across network.  
**Scores:** Design 3 · Innovation 3 · Responsible 4 · Present 3 · Buildability 3 · Wow 2  
**Risk:** Slow demo; weak visceral stake.

### F. Crane Downtime Workface Recovery Agent
**Problem:** QC outage mid-operation; reassign gangs/AGVs/stacks.  
**Scores:** Design 4 · Innovation 3 · Responsible 4 · Present 4 · Buildability 3 · Wow 4  
**Risk:** Narrower story; less unique to PSA’s T/S identity.

### G. Gate / Haulage Appointment Conflict Agent
**Problem:** Truck appointment clashes with yard hotspots (PORTNET API angle).  
**Scores:** Design 3 · Innovation 3 · Responsible 4 · Present 3 · Buildability 3 · Wow 3  
**Risk:** Less dramatic; more B2B admin than ops control room.

### H. Carbon / Green Power Scheduling Agent
**Problem:** Reefer power + berth energy under constraints.  
**Scores:** Design 3 · Innovation 4 · Responsible 4 · Present 3 · Buildability 3 · Wow 3  
**Risk:** Soft ops urgency; harder “execution” demo.

### I. Dangerous Goods Exception Orchestrator
**Problem:** DG segregation / permit conflicts blocking moves.  
**Scores:** Design 4 · Innovation 4 · Responsible 5 · Present 4 · Buildability 3 · Wow 4  
**Risk:** Safety-critical; autonomy story is almost all HITL; domain data harder.

### J. Multi-Port “Node to Network” Exception Bus
**Problem:** Coordinate exceptions across PSA global terminals.  
**Scores:** Design 4 · Innovation 4 · Responsible 4 · Present 4 · Buildability 2 · Wow 5  
**Risk:** Scope explosion in 7 days; shallow integrations.

## Comparative matrix

| Option | PSA-specific | Agentic depth | Differentiated vs 2025 | Demo drama | 7-day build |
|--------|--------------|---------------|------------------------|------------|-------------|
| A RELAY T/S | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★ |
| B Bunching | ★★★★ | ★★★★ | ★★ | ★★★★ | ★★★ |
| C L2 Incident | ★★★★ | ★★★★ | ★ | ★★★ | ★★★★ |
| D Chat network | ★★★ | ★★ | ★ | ★★ | ★★★★ |
| F Crane recovery | ★★★★ | ★★★★ | ★★★ | ★★★★ | ★★★ |
| I DG exceptions | ★★★★ | ★★★★ | ★★★★ | ★★★ | ★★★ |
| J Multi-port | ★★★★★ | ★★★★ | ★★★★ | ★★★★ | ★★ |

## Decision

**Choose A — RELAY (Transshipment Connection Continuity).**

Why this beats the field for *winning*:
1. **Only PSA can own this story** — T/S is Singapore/PSA’s identity, not a generic logistics chatbot.  
2. Maps **1:1 to every mandatory agent behaviour**.  
3. Natural **HITL** for expensive physical moves (judges reward appropriate autonomy).  
4. Hybrid **deterministic risk engine + LLM orchestration** shows *team design*, not platform magic.  
5. Live control-room UI + execution trace = presentation/demo killer.  
6. Clear $ impact narrative (missed connections → cascading network delay, dwell, customer SLA).

**Stretch differentiator (built into design):** a **Dissent/Critic agent** that stress-tests the top plan before human approval — rare in student demos, signals responsible AI.
