# Core logic — first principles (every piece explained)

This is the “we actually understand it” reference. A judge asking “walk me through the math” should map here.

---

## 1. The fundamental question

For each transshipment box **c**:

> Will the box be **physically available** before the **outbound vessel cutoff**?

If no → connection miss → expected loss (reroute, dwell, SLA, rehandle).

---

## 2. Connection window math (`engine/risk.py`)

### Inputs per container

- `from_vessel` — inbound (feeder/mainline discharging the box)
- `to_vessel` — outbound (loading the box)
- `block` — yard block location
- `move_minutes` — estimated yard→quay move time
- `priority`, `reefer`, `dg` — commercial / safety weighting

### Timestamps

```
inbound_eta     = vessel ETA (or scenario override)
outbound_cutoff = hard load cutoff on outbound vessel
uncertainty_h   = sum of inbound/outbound ETA uncertainty + scenario boost
move            = move_minutes (+ HOTSPOT_PENALTY if block is hotspot)
buffer          = uncertainty_h as timedelta
ready_at        = inbound_eta + move + buffer
slack_hours     = (outbound_cutoff - ready_at) in hours
```

**Interpretation:** `slack_hours` is the industry “connection buffer”. Negative = already in miss territory.

### Risk curve (deterministic, not ML)

Piecewise mapping slack → base risk:

| slack_hours | base_risk |
|-------------|-----------|
| ≥ 6 | 0.05 |
| ≥ 3 | 0.20 |
| ≥ 1 | 0.45 |
| ≥ 0 | 0.70 |
| ≥ -3 | 0.88 |
| < -3 | 0.98 |

Then multiply by priority weights (premium 1.35×, reefer 1.15×, DG 1.25×) → `weighted_risk`.

Expected miss cost:

```
expected_miss_cost = missed_connection_usd × weight × weighted_risk
```

### Why deterministic?

- Reproducible demo
- Auditable (“show me why box X is 0.88”)
- LLM narrates; **engine owns truth** (brief asks for team-designed workflow)

---

## 3. What-if simulator (`tools/registry.py` → `recovery.simulate_plan`)

Simulates **counterfactual** before human approval:

| Mode | Effect on twin (temporary) |
|------|---------------------------|
| `priority_restow` | `move_minutes × 0.42` (floor 18 min); hotspot extra -12 min; reduce ETA uncertainty on touched inbound vessels |
| Cutoff extension | `cutoff += N hours` on selected outbound vessels |
| `expedite_reefer` | Faster moves for reefer boxes only |

Process:

1. Score **before** at-risk set for target container IDs  
2. Apply temporary mutations  
3. Re-score **after**  
4. `connections_saved` = boxes that dropped below risk threshold  
5. **Restore** twin state in `finally` block (simulation doesn’t mutate live state)

Post-approval, `workorder.dispatch` applies **real** mutations (move time reduction persists).

---

## 4. Agent responsibilities (orchestrator state machine)

```
DETECTED → ANALYSING → PLANNING → CRITIQUE → AWAITING_APPROVAL → EXECUTING → CLOSED
                                                              ↘ ESCALATED (reject)
```

| Agent | Responsibility | Not allowed to |
|-------|----------------|----------------|
| **Sentinel** | Ingest trigger, update ETA, weather/AIS context, open incident | Dispatch physical moves |
| **Analyst** | Pull crane/yard state, build at-risk list, fallback on tool fail | Select final plan |
| **Planner** | Generate PLAN-A/B/C (+ PLAN-X in crane scenario), run simulator | Bypass approval |
| **Critic** | Attack plans — capacity lies, DG path, cache uncertainty | Execute |
| **Executor** | Low-risk notify now; gated actions after token | Dispatch without token |
| **Auditor** | Trace, post-score metrics, token tally | Change plans |

Orchestrator owns transitions — **not** an LLM loop.

---

## 5. Policy gates (`engine/policy.py`)

Default: physical/commercial actions require approval.

Extra gates:

- DG present → stricter (segregated path)
- Reefer + restow → approval even if action type looks soft
- `risk_score ≥ 0.85` → approval

`workorder.dispatch` **hard-fails** without `approval_token` — not cosmetic.

---

## 6. Scenario design (why each exists)

| Scenario | Proves | Key mechanism |
|----------|--------|---------------|
| `late_feeder` | Happy path recovery | ETA slip → PLAN-B (cutoff + selective restow) wins |
| `crane_outage` | Critic dissent | PLAN-X looks good on paper → rejected (QC-07 down) |
| `uncertainty_tool_fail` | Incomplete data | Yard 503 retry → cache fallback; partial save, residual risk visible |

---

## 7. Verified demo outcomes (auto-approve run, 2026-08-23)

Plan `connections_saved` is fleet-wide (includes cutoff-extension spillover) and matches post-execute Auditor metrics.

| Scenario | At-risk | Pre-loss USD | Selected | Sim saved | Actual saved | Loss avoided |
|----------|---------|--------------|----------|-----------|--------------|--------------|
| late_feeder | 7 | 10,209 | PLAN-B | 7 | 7 | 10,209 |
| crane_outage | 7 | 6,563 | PLAN-A | 7 | 7 | 6,563 |
| uncertainty_tool_fail | 12 | 22,563 | PLAN-B | 5 | 5 | 13,111 (7 residual) |

Note: late_feeder PLAN-A (restow alone) still shows 0 recovered — ETA slip is too deep without commercial cutoff flexibility. That is intentional narrative, not a bug.

---

## 8. Token accounting

Each trace event carries `tokens_est` — illustrative efficiency narrative (~2–3k total per incident vs “dump whole terminal JSON into GPT”).

---

## 9. Integration contracts (Sprinternship)

Tool names mirror PSA-style surfaces:

- `vessel_schedule.get`, `eta.update`
- `connections.query_at_risk`
- `yard.*`, `crane.availability`
- `recovery.simulate_plan`
- `workorder.draft/dispatch`, `notify.send`

Same JSON shapes → swap mock registry for real adapters.
