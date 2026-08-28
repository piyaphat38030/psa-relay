# Field research → what we changed

Research pass: Aug 2026. Goal: elevate RELAY from “AI-built demo” to “team that understands PSA ops”.

---

## Research sources (high signal)

| Area | Source | Takeaway applied |
|------|--------|------------------|
| PSA congestion / off-schedule | [Maritime Executive Jul 2024](https://maritime-executive.com/article/singapore-cuts-delays-to-under-two-days-but-warns-of-continuing-volatility) | Scenario narratives reference **bunching + ETA slip**, not abstract “delay” |
| T/S share | [MPA 2024 throughput release](https://www.mpa.gov.sg/media-centre/details/strong-growth-momentum-for-maritime-singapore) | Slides/deck cite **~90% transshipment** |
| MDT / digital twin | [Business Times Mar 2025](https://www.businesstimes.com.sg/singapore/singapore-debuts-digital-twin-its-port), [Straits Times](https://www.straitstimes.com/singapore/digital-twin-of-singapores-port-to-be-tested-in-second-half-of-2025) | Architecture positions RELAY as **decision layer on twin state** |
| Feeder synchronization | [SMU FVRSP paper](https://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=7760&context=sis_research) | Vocabulary: feeder/mainline sync, hub slot pressure |
| Connection buffer KPIs | [Tradlinx LSP guide](https://blogs.tradlinx.com/transshipment-rollovers-and-missed-feeders-a-prevention-guide-for-lsps/) | UI labels **connection buffer (h)** not generic “slack” |
| Cutoff discipline | [Tier2 cutoff guide](https://tier2systems.com/en/blog/cargo-cutoff-deadlines-ops-guide/) | Cutoff extension = **negotiated**, HITL, not auto |
| Yard ripple effects | [SD port disruption study 2025](https://www.sciencedirect.com/science/article/pii/S1366554525003059) | Hotspot penalty + crane scenario ripple story |
| Agentic ports landscape | PortAgent, Honeywell control-room agents, loadmaster orchestration | Differentiate: **T/S connection engine + dissent critic**, not vehicle dispatch clone |
| Competition brief | [psacodesprint.com](https://www.psacodesprint.com/agentic-ai-in-action) | Explicit autonomy rationale in trace + slides |

---

## Changes made in this pass

### Documentation
- `research/06_domain_deep_dive.md` — verified PSA context
- `research/07_core_logic_first_principles.md` — full logic map
- `deliverables/LIVE_DEMO_GUIDE.md` — presentation-day playbook

### Product / code
- Ops console: **phase stepper**, **PSA context panel** (sourced stats), **connection buffer** column label
- `/api/meta`: `domain_context` with verified public stats + RELAY positioning
- Risk engine docstring: explicit connection-window formula
- Scenarios: richer descriptions tied to real ops (rehandling, bunching, MDT-class twin)

### Deliverables
- Slides: situation slide includes **verified PSA stats** exhibit
- Speaker script: domain-credible lines + **live demo beats**
- Architecture: MDT / JIT alignment section
- Demo video script: optional **live walkthrough** segment for finals

---

## What we deliberately did NOT do (scope discipline)

- No live PORTNET / CITOS integration (would be fake claims)
- No LLM API dependency in demo path (reproducibility)
- No full berth optimizer (different problem)
- No inflated “$100M savings” — synthetic twin only

---

## Differentiation thesis (one paragraph)

RELAY wins if judges believe: **(1)** we picked the right PSA pain (connection continuity under off-schedule bunching), **(2)** we designed the autonomy model deliberately, **(3)** we can demo failure and recovery live without hiding behind slides. Field research backs every headline stat and every scenario trigger.
