# Domain deep dive — transshipment connection continuity (verified)

This document captures **what actually happens** at a PSA-style hub, with sources — not generic “logistics AI” framing.

---

## 1. Why Singapore / PSA cares about *connections*, not just throughput

| Fact | Source |
|------|--------|
| ~**90%** of Singapore container throughput is **transshipment** (not origin/destination) | [MPA, Strong growth momentum for Maritime Singapore](https://www.mpa.gov.sg/media-centre/details/strong-growth-momentum-for-maritime-singapore) |
| **41.12M TEU** handled in 2024 (+5.4% YoY) | Same MPA release |
| **~90%** of containerships arrived **off-schedule** in 1H 2024 (vs 77% in 2023), largely Red Sea diversions | [Maritime Executive, Jul 2024](https://maritime-executive.com/article/singapore-cuts-delays-to-under-two-days-but-warns-of-continuing-volatility) |
| Container **rehandling** (restow/reshuffle) up **8%** in 1H 2024 — more dock time, more yard moves | Same |
| Vessel **stays on berth up 22%** vs 2023 — less slack for connections | Same |
| PSA cut average **wait to ≤2 days** by reactivating Keppel/Tanjong Pagar berths + new Tuas berths + ~1,500 hires | MOT / MPA / PSA public statements 2024–2025 |

**Implication for RELAY:** Judges at PSA live this daily. A solution framed as “chatbot for ports” loses. A solution framed as **connection-window recovery under off-schedule bunching** is immediately credible.

---

## 2. Operational vocabulary (how planners talk)

| Term | Meaning in hub ops | RELAY mapping |
|------|-------------------|---------------|
| **Mother / mainline** | Large deep-sea vessel on long-haul service | `vessel.role = mainline` |
| **Feeder** | Smaller vessel connecting regional ports to hub | `vessel.role = feeder` |
| **Service / string** | Fixed rotation (e.g. AEU1, IDN-FEED) | `vessel.service` |
| **Cutoff (CY cutoff)** | Hard deadline for a box to be available for outbound load | `vessel.cutoff` |
| **Connection window / buffer** | Time between inbound availability and outbound cutoff | `slack_hours` in risk engine |
| **Restow / rehandle / reshuffle** | Move box in yard to beat cutoff or unblock stack | `priority_restow` action |
| **Rolling / miss** | Box fails to connect; rebooked to next sailing | `hold_for_next_vessel` plan |
| **Hotspot block** | High yard util → slower moves, more reshuffles | `yard_blocks[].hotspot` |
| **Off-schedule bunching** | Multiple vessels same day vs spaced plan | Scenario trigger: ETA revision |

Academic framing: transshipment is **synchronization** between discharge and load vessels — if sync fails, cost is reroute or storage ([SMU FVRSP paper](https://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=7760&context=sis_research)).

---

## 3. What breaks connections (trigger taxonomy)

Verified / literature-aligned triggers RELAY models:

1. **Feeder ETA slip** — upstream port congestion, weather, AIS gaps  
   - Real context: Red Sea diversions → bunching → feeder/mainline misalignment  
2. **Quay crane loss** — hydraulic fault, maintenance; compresses workface  
   - Ripple: yard congestion → seaside delays ([System Dynamics port study, 2025](https://www.sciencedirect.com/science/article/pii/S1366554525003059))  
3. **Data degradation** — yard API down, stale AIS, haze  
   - Ops must widen uncertainty bands, not pretend precision  

Recovery levers (in order of realism):

| Lever | Who decides | RELAY autonomy |
|-------|-------------|----------------|
| Internal brief / dossier | Autonomous | ✓ notify_internal |
| Re-score with wider ETA bands | Autonomous | ✓ Analyst |
| Priority restow wave | **Planner** (physical) | HITL |
| Cutoff extension request | **Planner + carrier** | HITL |
| Hold for next sailing | **Planner** (accept miss) | HITL |
| Escalate to superintendent | Human reject path | ✓ |

Terminals rarely grant cutoff extensions casually ([Tier2 ops guide](https://tier2systems.com/en/blog/cargo-cutoff-deadlines-ops-guide/)) — RELAY treats them as **commercial negotiation**, not a free button.

---

## 4. PSA / MPA strategic alignment (why RELAY fits *now*)

| Initiative | Relevance to RELAY |
|------------|-------------------|
| **Maritime Digital Twin (MDT)** — launched Mar 2025, Tuas Phase 2 deployment | RELAY’s synthetic twin + what-if simulator is the **agentic decision layer on top of twin state** — same pattern MPA describes for scenario planning |
| **Just-In-Time Planning & Coordination Platform** | RELAY consumes ETA revisions / alerts — integration path is JIT event stream → Sentinel |
| **Node-to-Network** (PSA + carriers) | Cutoff negotiation + carrier notify maps to network-level recovery |
| **Smart Port / IoT / AI scenario planning** | Public PSA narrative already mentions digital twins + scenario planning ([GoComet industry summary](https://www.gocomet.com/blog/guide-to-singapore-port/)) |

RELAY is **not** claiming live PORTNET access. It is showing **the control loop** PSA would wrap around twin + TOS APIs during Sprinternship.

---

## 5. What competitors will likely build (and how we differ)

| Common hackathon pattern | Why it’s weak | RELAY counter |
|--------------------------|---------------|---------------|
| Generic multi-agent chat | No domain engine | Deterministic connection-risk + simulator |
| “Autonomous everything” | Brief explicitly warns against this | Tiered autonomy + approval tokens |
| Berth optimizer only | Misses T/S connection pain | Connection-first scoring |
| LLM-as-brain | Unreproducible demo | State machine + traced tool calls |
| No failure paths | Looks toy | Yard 503, AIS degrade, PLAN-X rejection |

---

## 6. Assumptions we checked (not guessed)

| Assumption | Verdict | Evidence |
|------------|---------|----------|
| “Higher autonomy isn’t automatically better” | **Confirmed** | [psacodesprint.com/agentic-ai-in-action](https://www.psacodesprint.com/agentic-ai-in-action) |
| Singapore is T/S-heavy | **Confirmed** | MPA ~90% transshipment |
| Off-schedule arrivals are acute | **Confirmed** | PSA 90% off-schedule 1H 2024 |
| Restow/rehandle is rising | **Confirmed** | +8% rehandling PSA 1H 2024 |
| Connection buffer matters more than port-pair averages | **Confirmed** | Tradlinx / LSP guides — track by **string + hub** |
| Cutoff extensions are rare / negotiated | **Confirmed** | Tier2, loadmaster.ai cutoff guides |
| Yard congestion ripples to seaside | **Confirmed** | 2025 SD port ripple study |

---

## 7. Numbers we use in demo (synthetic, labeled)

Cost model in twin (`seed.py`):

- Baseline expected miss cost: **USD 1,800** per connection (illustrative; premium/reefer/DG weighted up)
- Priority restow: **USD 220** per box moved

**Always label as synthetic twin** in slides and video — never imply live PSA financials.
