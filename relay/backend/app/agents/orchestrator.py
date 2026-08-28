"""RELAY multi-agent orchestrator — custom state machine, not a thin framework wrapper."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timedelta
from typing import Any

from app.engine.policy import action_requires_approval, autonomy_rationale
from app.models import (
    ApprovalItem,
    Incident,
    IncidentStatus,
    PlanAction,
    RecoveryPlan,
    TraceEvent,
    now_iso,
    to_dict,
)
from app.scenarios import SCENARIOS
from app.tools.registry import ToolContext, ToolError, call_tool


class ApprovalError(ValueError):
    """Raised when an approval decision is invalid or no longer pending."""


class Orchestrator:
    def __init__(self) -> None:
        self.incidents: dict[str, Incident] = {}
        self.contexts: dict[str, ToolContext] = {}
        self._lock = threading.Lock()

    def get(self, incident_id: str) -> Incident:
        if incident_id not in self.incidents:
            raise KeyError(incident_id)
        return self.incidents[incident_id]

    def list_incidents(self) -> list[Incident]:
        return sorted(self.incidents.values(), key=lambda i: i.created_at, reverse=True)

    def _trace(self, incident: Incident, agent: str, kind: str, summary: str, detail: dict | None = None, tokens: int = 0) -> None:
        incident.trace.append(
            TraceEvent(
                ts=now_iso(),
                agent=agent,
                kind=kind,
                summary=summary,
                detail=detail or {},
                tokens_est=tokens,
            )
        )
        incident.updated_at = now_iso()

    def _tool(self, incident: Incident, ctx: ToolContext, agent: str, name: str, params: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        self._trace(incident, agent, "tool_call", f"Calling {name}", {"params": params})
        try:
            result = call_tool(ctx, name, params, **kwargs)
            self._trace(
                incident,
                agent,
                "tool_result",
                f"{name} ok (attempts={result.get('attempts', 1)})",
                {"result": result.get("data")},
            )
            return result["data"]
        except ToolError as e:
            self._trace(
                incident,
                agent,
                "tool_error",
                f"{name} failed: {e}",
                {"retryable": e.retryable},
            )
            raise

    def start(self, scenario_id: str, *, auto_approve: bool = False) -> Incident:
        with self._lock:
            return self._start_unlocked(scenario_id, auto_approve=auto_approve)

    def _start_unlocked(self, scenario_id: str, *, auto_approve: bool = False) -> Incident:
        if scenario_id not in SCENARIOS:
            raise ValueError(f"Unknown scenario {scenario_id}")
        scenario = SCENARIOS[scenario_id]
        ctx = ToolContext()
        # Apply scenario flags / move inflation
        ctx.terminal["flags"].update(scenario.get("flags", {}))
        setup = scenario.get("setup", {})
        if setup.get("inflate_move_factor"):
            factor = float(setup["inflate_move_factor"])
            for c in ctx.terminal["containers"]:
                if c["from_vessel"] == setup.get("eta_vessel") or c["to_vessel"] == setup.get("eta_vessel"):
                    c["move_minutes"] = int(c["move_minutes"] * factor)

        incident = Incident(
            id=f"INC-{uuid.uuid4().hex[:8].upper()}",
            scenario_id=scenario_id,
            title=scenario["title"],
            status=IncidentStatus.DETECTED,
            trigger=scenario["trigger"],
            created_at=now_iso(),
            updated_at=now_iso(),
            objective="Maximise recoverable transshipment connections under constraints; never silently execute high-impact moves.",
        )
        self.incidents[incident.id] = incident
        self.contexts[incident.id] = ctx

        self._trace(incident, "system", "state", "Incident opened", {"scenario": scenario_id})
        self._trace(
            incident,
            "Sentinel",
            "thought",
            "Operational signal received — opening continuity incident.",
            {"trigger": scenario["trigger"]},
            tokens=120,
        )

        # Phase 1: apply trigger into systems
        self._phase_sentinel(incident, ctx, setup)
        # Phase 2: analyse
        self._phase_analyst(incident, ctx, setup, scenario)
        # Phase 3: plan
        self._phase_planner(incident, ctx, setup)
        # Phase 4: critic
        self._phase_critic(incident, ctx)
        # Phase 5: request approval
        self._phase_approval_gate(incident)

        if auto_approve and incident.status == IncidentStatus.AWAITING_APPROVAL:
            for ap in incident.approvals:
                if ap.status == "pending":
                    self._decide_unlocked(incident.id, ap.approval_id, "approved", decided_by="auto_demo")

        return incident

    def _phase_sentinel(self, incident: Incident, ctx: ToolContext, setup: dict[str, Any]) -> None:
        incident.status = IncidentStatus.DETECTED
        self._trace(incident, "Sentinel", "decision", "Classify as connection-continuity risk", {"severity": "high"}, tokens=80)

        if setup.get("eta_vessel"):
            self._tool(
                incident,
                ctx,
                "Sentinel",
                "eta.update",
                {
                    "vessel_id": setup["eta_vessel"],
                    "new_eta": setup["new_eta"],
                    "uncertainty_h": setup.get("uncertainty_h", 1.5),
                },
            )

        weather = self._tool(incident, ctx, "Sentinel", "weather.get", {})
        self._trace(
            incident,
            "Sentinel",
            "thought",
            f"Weather context: {weather.get('condition')} — {weather.get('impact')}",
            tokens=60,
        )

        if incident.scenario_id == "uncertainty_tool_fail":
            ais = self._tool(
                incident,
                ctx,
                "Sentinel",
                "ais.uncertainty",
                {
                    "vessel_id": setup.get("eta_vessel", "V-MAIN-02"),
                    "last_fix_age_min": 95,
                    "uncertainty_hours": setup.get("uncertainty_h", 3.5),
                },
            )
            self._trace(
                incident,
                "Sentinel",
                "decision",
                "Degraded AIS — widen uncertainty bands before scoring connections",
                ais,
                tokens=70,
            )

        self._tool(
            incident,
            ctx,
            "Sentinel",
            "notify.send",
            {
                "channel": "internal",
                "audience": "duty_officer",
                "message": f"RELAY incident {incident.id}: {incident.title}",
            },
        )

    def _phase_analyst(self, incident: Incident, ctx: ToolContext, setup: dict[str, Any], scenario: dict[str, Any]) -> None:
        incident.status = IncidentStatus.ANALYSING
        self._trace(incident, "system", "state", "Status → analysing")
        self._trace(incident, "Analyst", "thought", "Building connection impact graph from live twin state.", tokens=90)

        affected = [setup.get("eta_vessel")] if setup.get("eta_vessel") else None
        # Crane scenario: also pull crane state
        if incident.scenario_id == "crane_outage":
            cranes = self._tool(incident, ctx, "Analyst", "crane.availability", {})
            down = [c for c in cranes["cranes"] if c["status"] == "down"]
            self._trace(incident, "Analyst", "decision", f"Crane constraint active: {[c['id'] for c in down]}", tokens=50)

        hotspots = self._tool(incident, ctx, "Analyst", "yard.hotspot_score", {})
        self._trace(
            incident,
            "Analyst",
            "metric",
            f"Yard hotspots: {[b['id'] for b in hotspots['hotspots']]}",
            tokens=40,
        )

        # Yard inventory may fail in scenario 3 — demonstrate retry/fallback
        inject = bool(scenario.get("inject_tool_fail"))
        yard_fallback = False
        if inject or ctx.terminal["flags"].get("yard_api_down"):
            try:
                # First try with require_yard path via inventory on one box
                sample = ctx.terminal["containers"][0]["id"]
                self._tool(
                    incident,
                    ctx,
                    "Analyst",
                    "yard.inventory_lookup",
                    {"container_id": sample},
                    retries=2,
                    inject_fail_once=inject,
                )
            except ToolError:
                yard_fallback = True
                self._trace(
                    incident,
                    "Analyst",
                    "decision",
                    "Yard API unavailable after retries — falling back to last-known block map in twin cache.",
                    {"fallback": "cached_block_positions"},
                    tokens=100,
                )
                # Clear flag so risk scoring can continue on twin cache
                ctx.terminal["flags"]["yard_api_down"] = False

        at_risk = self._tool(
            incident,
            ctx,
            "Analyst",
            "connections.query_at_risk",
            {
                "affected_vessel_ids": affected,
                "uncertainty_boost_h": setup.get("uncertainty_boost_h", 0),
                "risk_threshold": 0.4,
            },
        )
        incident.at_risk = at_risk["at_risk"]
        summary = at_risk["summary"]
        incident.metrics["risk_summary"] = summary
        incident.metrics["yard_fallback"] = yard_fallback
        self._trace(
            incident,
            "Analyst",
            "decision",
            f"Identified {summary['count']} at-risk connections · expected loss ${summary['expected_loss_usd']:,.0f}",
            summary,
            tokens=110,
        )

        if summary["count"] == 0:
            incident.status = IncidentStatus.CLOSED
            incident.result = {"message": "No connections above risk threshold"}
            return

    def _phase_planner(self, incident: Incident, ctx: ToolContext, setup: dict[str, Any]) -> None:
        if incident.status == IncidentStatus.CLOSED:
            return
        incident.status = IncidentStatus.PLANNING
        self._trace(incident, "system", "state", "Status → planning")
        self._trace(
            incident,
            "Planner",
            "thought",
            "Generating recovery options with deterministic simulators; LLM-style rationale attached for operators.",
            tokens=100,
        )

        ids = [r["container_id"] for r in incident.at_risk]
        premium = [r["container_id"] for r in incident.at_risk if r["priority"] == "premium" or r["reefer"]]
        affected = [setup.get("eta_vessel")] if setup.get("eta_vessel") else None
        eta_overrides = {setup["eta_vessel"]: setup["new_eta"]} if setup.get("eta_vessel") else {}

        # Plan A — Priority restow top risk set
        sim_a = self._tool(
            incident,
            ctx,
            "Planner",
            "recovery.simulate_plan",
            {
                "mode": "priority_restow",
                "container_ids": ids[:8],
                "affected_vessel_ids": affected,
                "eta_overrides": eta_overrides,
                "uncertainty_boost_h": setup.get("uncertainty_boost_h", 0),
            },
        )
        cost_a = len(ids[:8]) * ctx.terminal["cost_model"]["priority_restow_usd"]
        plan_a_actions = [
            PlanAction(
                action_id="A1",
                type="notify_internal",
                description="Brief yard planner on priority restow window",
                requires_approval=False,
                risk_score=0.1,
                estimated_connections_saved=0,
            ),
            PlanAction(
                action_id="A2",
                type="priority_restow",
                description=f"Priority restow {len(ids[:8])} at-risk boxes toward outbound cutoffs",
                container_ids=ids[:8],
                requires_approval=True,
                risk_score=0.78,
                estimated_cost_usd=cost_a,
                estimated_connections_saved=sim_a["connections_saved"],
                params={"work_type": "priority_restow"},
            ),
            PlanAction(
                action_id="A3",
                type="notify_carrier",
                description="Notify affected carriers of recovery posture",
                requires_approval=False,
                risk_score=0.2,
            ),
        ]
        plan_a = RecoveryPlan(
            plan_id="PLAN-A",
            title="Priority restow (aggressive recovery)",
            summary="Compress yard/quay move times for the highest-risk connection set to beat outbound cutoffs.",
            score=sim_a["connections_saved"] * 12 + sim_a.get("loss_avoided_usd", 0) / 400 - sim_a["residual_count"] * 1.5 + 6,
            actions=plan_a_actions,
            connections_saved=sim_a["connections_saved"],
            residual_risk=round(sim_a["residual_count"] / max(len(ids), 1), 3),
            estimated_cost_usd=cost_a,
        )

        # Plan B — Cutoff extension + selective restow
        extend_vids = list({r["to_vessel"] for r in incident.at_risk})[:2]
        sim_b = self._tool(
            incident,
            ctx,
            "Planner",
            "recovery.simulate_plan",
            {
                "mode": "priority_restow",
                "container_ids": premium or ids[:5],
                "affected_vessel_ids": affected,
                "eta_overrides": eta_overrides,
                "uncertainty_boost_h": setup.get("uncertainty_boost_h", 0),
                "cutoff_extension_h": 2,
                "extend_vessel_ids": extend_vids,
            },
        )
        cost_b = len(premium or ids[:5]) * ctx.terminal["cost_model"]["priority_restow_usd"]
        plan_b_actions = [
            PlanAction(
                action_id="B1",
                type="request_cutoff_extension",
                description=f"Request +2h cutoff flexibility on {', '.join(extend_vids)}",
                requires_approval=True,
                risk_score=0.66,
                estimated_connections_saved=max(0, sim_b["connections_saved"] - 1),
                params={"hours": 2, "vessel_ids": extend_vids},
            ),
            PlanAction(
                action_id="B2",
                type="priority_restow",
                description="Selective restow for premium/reefer only",
                container_ids=premium or ids[:5],
                requires_approval=True,
                risk_score=0.7,
                estimated_cost_usd=cost_b,
                estimated_connections_saved=sim_b["connections_saved"],
            ),
            PlanAction(
                action_id="B3",
                type="notify_carrier",
                description="Align carriers on cutoff negotiation",
                requires_approval=False,
                risk_score=0.2,
            ),
        ]
        plan_b = RecoveryPlan(
            plan_id="PLAN-B",
            title="Negotiate cutoffs + selective restow",
            summary="Buy time commercially on outbound cutoffs while physically protecting premium/reefer connections.",
            score=sim_b["connections_saved"] * 10 + sim_b.get("loss_avoided_usd", 0) / 450 - cost_b / 200 + 3,
            actions=plan_b_actions,
            connections_saved=sim_b["connections_saved"],
            residual_risk=round(sim_b["residual_count"] / max(len(ids), 1), 3),
            estimated_cost_usd=cost_b,
        )

        # Plan C — Hold subset for next vessel (safer, lower recovery)
        hold_ids = [r["container_id"] for r in incident.at_risk if r["risk"] > 0.85][:4]
        cost_c = 0
        saved_c = 0  # holding accepts miss on current link but prevents chaos
        plan_c = RecoveryPlan(
            plan_id="PLAN-C",
            title="Controlled hold to next sailing",
            summary="Accept miss on hopeless connections; hold for next vessel to protect yard fluidity and avoid futile moves.",
            score=1.5 - len(hold_ids) * 0.4,
            actions=[
                PlanAction(
                    action_id="C1",
                    type="hold_for_next_vessel",
                    description=f"Hold {len(hold_ids)} boxes for next available sailing",
                    container_ids=hold_ids,
                    requires_approval=True,
                    risk_score=0.55,
                    estimated_cost_usd=cost_c,
                    estimated_connections_saved=saved_c,
                ),
                PlanAction(
                    action_id="C2",
                    type="notify_carrier",
                    description="Advise carriers of controlled rollings",
                    requires_approval=False,
                    risk_score=0.25,
                ),
            ],
            connections_saved=saved_c,
            residual_risk=1.0,
            estimated_cost_usd=cost_c,
        )

        # Crane scenario: inject an unsafe plan for critic to kill
        if incident.scenario_id == "crane_outage":
            inflated_saves = min(sim_a["connections_saved"] + 2, len(ids))
            unsafe = RecoveryPlan(
                plan_id="PLAN-X",
                title="Full parallel restow ignoring crane loss",
                summary="Attempt to clear all at-risk boxes at normal workface rates despite QC-07 down.",
                score=inflated_saves * 12,  # looks attractive on paper
                actions=[
                    PlanAction(
                        action_id="X1",
                        type="priority_restow",
                        description="Restow all at-risk boxes without crane derate",
                        container_ids=ids,
                        requires_approval=True,
                        risk_score=0.92,
                        estimated_cost_usd=len(ids) * 220,
                        estimated_connections_saved=inflated_saves,
                    )
                ],
                connections_saved=inflated_saves,
                residual_risk=0.1,
                estimated_cost_usd=len(ids) * 220,
            )
            incident.plans = [unsafe, plan_a, plan_b, plan_c]
        else:
            incident.plans = [plan_a, plan_b, plan_c]

        for p in incident.plans:
            self._trace(
                incident,
                "Planner",
                "decision",
                f"Option {p.plan_id}: {p.title} · saved={p.connections_saved} · score={p.score:.1f}",
                to_dict(p),
                tokens=70,
            )

    def _phase_critic(self, incident: Incident, ctx: ToolContext) -> None:
        if incident.status == IncidentStatus.CLOSED or not incident.plans:
            return
        incident.status = IncidentStatus.CRITIQUE
        self._trace(incident, "system", "state", "Status → critique")
        self._trace(
            incident,
            "Critic",
            "thought",
            "Stress-testing plans for capacity lies, safety, and false precision under uncertainty.",
            tokens=90,
        )

        for plan in incident.plans:
            notes: list[str] = []
            if plan.plan_id == "PLAN-X":
                notes.append("REJECT: Assumes QC-07 capacity that does not exist — plan is operationally infeasible.")
                notes.append("Workface rate would be overstated by ~35–40%; residual risk is understated.")
                plan.score -= 50
            if plan.plan_id == "PLAN-A" and incident.scenario_id == "crane_outage":
                notes.append("Aggressive restow still viable only if scope is capped to premium/reefer subset.")
                plan.score -= 5
            if any(a.type == "priority_restow" and len(a.container_ids) > 10 for a in plan.actions):
                notes.append("WARN: Restow wave too large for hotspot blocks Y-A2/Y-C3 without staging.")
                plan.score -= 8
            if incident.metrics.get("yard_fallback") and plan.connections_saved > 0:
                notes.append("WARN: Yard positions from cache — verify plug/availability before dispatching reefers.")
                plan.score -= 3
            dg_ids = [r["container_id"] for r in incident.at_risk if r["dg"]]
            if dg_ids and any(set(a.container_ids) & set(dg_ids) for a in plan.actions if a.type == "priority_restow"):
                notes.append("DG boxes present — require segregated path approval before physical move.")
                plan.score -= 4
            if not notes:
                notes.append("No fatal flaws found; residual risk acceptable relative to expected loss.")
            plan.critic_notes = notes
            self._trace(
                incident,
                "Critic",
                "decision",
                f"Critique {plan.plan_id}: {notes[0]}",
                {"notes": notes, "adjusted_score": plan.score},
                tokens=80,
            )

        # Select best after critique
        ranked = sorted(incident.plans, key=lambda p: p.score, reverse=True)
        # Never select PLAN-X
        ranked = [p for p in ranked if p.plan_id != "PLAN-X"] or ranked
        best = ranked[0]
        for p in incident.plans:
            p.selected = p.plan_id == best.plan_id
        incident.selected_plan_id = best.plan_id
        self._trace(
            incident,
            "Critic",
            "decision",
            f"Recommend {best.plan_id} after dissent review",
            {"selected": best.plan_id, "ranking": [p.plan_id for p in ranked]},
            tokens=60,
        )

    def _phase_approval_gate(self, incident: Incident) -> None:
        if incident.status == IncidentStatus.CLOSED or not incident.selected_plan_id:
            return
        plan = next(p for p in incident.plans if p.plan_id == incident.selected_plan_id)
        gated = []
        for action in plan.actions:
            has_dg = any(r["dg"] for r in incident.at_risk if r["container_id"] in action.container_ids)
            has_reefer = any(r["reefer"] for r in incident.at_risk if r["container_id"] in action.container_ids)
            needs = action.requires_approval or action_requires_approval(
                action.type, risk_score=action.risk_score, has_dg=has_dg, has_reefer=has_reefer
            )
            action.requires_approval = needs
            if needs:
                gated.append(action)

        self._trace(
            incident,
            "Auditor",
            "thought",
            autonomy_rationale(),
            tokens=40,
        )

        if not gated:
            incident.status = IncidentStatus.EXECUTING
            self._execute(incident, approval_token="AUTO-LOW-RISK")
            return

        approval = ApprovalItem(
            approval_id=f"APR-{uuid.uuid4().hex[:6].upper()}",
            plan_id=plan.plan_id,
            action_ids=[a.action_id for a in gated],
            rationale=(
                f"High-impact actions in {plan.plan_id} require planner approval. "
                f"Expected to save {plan.connections_saved} connections at ~${plan.estimated_cost_usd:,.0f}."
            ),
            status="pending",
        )
        incident.approvals.append(approval)
        incident.status = IncidentStatus.AWAITING_APPROVAL
        self._trace(incident, "system", "state", "Status → awaiting_approval")
        self._trace(
            incident,
            "Executor",
            "approval_request",
            f"Human approval required for actions {approval.action_ids}",
            to_dict(approval),
            tokens=50,
        )

        # Still execute low-risk preamble actions
        ctx = self.contexts[incident.id]
        for action in plan.actions:
            if not action.requires_approval:
                self._run_action(incident, ctx, action, approval_token=None)

    def decide(self, incident_id: str, approval_id: str, decision: str, *, decided_by: str = "ops_planner", note: str = "") -> Incident:
        with self._lock:
            return self._decide_unlocked(incident_id, approval_id, decision, decided_by=decided_by, note=note)

    def _decide_unlocked(
        self,
        incident_id: str,
        approval_id: str,
        decision: str,
        *,
        decided_by: str = "ops_planner",
        note: str = "",
    ) -> Incident:
        if decision not in ("approved", "rejected"):
            raise ApprovalError(f"Invalid decision '{decision}' — must be approved or rejected")

        incident = self.get(incident_id)
        try:
            approval = next(a for a in incident.approvals if a.approval_id == approval_id)
        except StopIteration as e:
            raise ApprovalError(f"Approval {approval_id} not found") from e

        if approval.status != "pending":
            raise ApprovalError(f"Approval {approval_id} already {approval.status}")

        approval.status = decision
        approval.decided_by = decided_by
        approval.decided_at = now_iso()
        self._trace(
            incident,
            "Executor",
            "approval_result",
            f"Approval {approval_id} {decision} by {decided_by}",
            {"note": note},
            tokens=30,
        )

        if decision == "rejected":
            incident.status = IncidentStatus.ESCALATED
            incident.result = {
                "status": "escalated",
                "message": "Planner rejected plan — escalated to shift superintendent with dossier.",
                "note": note,
            }
            ctx = self.contexts[incident.id]
            self._tool(
                incident,
                ctx,
                "Executor",
                "notify.send",
                {
                    "channel": "internal",
                    "audience": "shift_superintendent",
                    "message": f"Incident {incident.id} escalated after rejection. Note: {note}",
                },
            )
            return incident

        incident.status = IncidentStatus.EXECUTING
        self._execute(incident, approval_token=approval_id)
        return incident

    def _execute(self, incident: Incident, *, approval_token: str) -> None:
        ctx = self.contexts[incident.id]
        plan = next(p for p in incident.plans if p.plan_id == incident.selected_plan_id)
        self._trace(incident, "system", "state", "Status → executing")
        self._trace(incident, "Executor", "thought", f"Executing approved plan {plan.plan_id}", tokens=40)

        for action in plan.actions:
            if action.requires_approval:
                self._run_action(incident, ctx, action, approval_token=approval_token)

        # Re-score after execution
        setup = SCENARIOS[incident.scenario_id].get("setup", {})
        affected = [setup.get("eta_vessel")] if setup.get("eta_vessel") else None
        post = self._tool(
            incident,
            ctx,
            "Auditor",
            "connections.query_at_risk",
            {
                "affected_vessel_ids": affected,
                "uncertainty_boost_h": setup.get("uncertainty_boost_h", 0),
                "risk_threshold": 0.4,
            },
        )
        before = incident.metrics.get("risk_summary", {})
        after = post["summary"]
        # Prefer counting boxes that left the at-risk set; also credit large loss reduction
        before_ids = {r["container_id"] for r in incident.at_risk}
        after_ids = {r["container_id"] for r in post["at_risk"]}
        saved = len(before_ids - after_ids)
        loss_avoided = max(0.0, before.get("expected_loss_usd", 0) - after.get("expected_loss_usd", 0))
        if saved == 0 and loss_avoided > 0:
            # Partial recovery: risk reduced but some boxes remain above threshold
            saved = max(1, int(round(loss_avoided / max(before.get("expected_loss_usd", 1), 1) * len(incident.at_risk))))
        tokens_total = sum(t.tokens_est for t in incident.trace)
        incident.metrics["post_summary"] = after
        incident.metrics["connections_saved"] = saved
        incident.metrics["loss_avoided_usd"] = loss_avoided
        incident.metrics["tokens_est_total"] = tokens_total
        incident.result = {
            "status": "closed",
            "connections_saved": saved,
            "loss_avoided_usd": loss_avoided,
            "selected_plan": plan.plan_id,
            "tokens_est_total": tokens_total,
            "work_orders": ctx.terminal["work_orders"],
            "notifications": len(ctx.terminal["notifications"]),
        }
        incident.status = IncidentStatus.CLOSED
        self._trace(incident, "system", "state", "Status → closed")
        self._trace(
            incident,
            "Auditor",
            "metric",
            f"Run complete: saved {saved} connections · avoided ${loss_avoided:,.0f} · tokens≈{tokens_total}",
            incident.result,
            tokens=40,
        )

    def _run_action(self, incident: Incident, ctx: ToolContext, action: PlanAction, approval_token: str | None) -> None:
        self._trace(incident, "Executor", "action", f"Run {action.action_id}: {action.type}", to_dict(action))
        if action.type in {"notify_internal", "notify_carrier"}:
            audience = "ops" if action.type == "notify_internal" else "carrier"
            self._tool(
                incident,
                ctx,
                "Executor",
                "notify.send",
                {"channel": "email", "audience": audience, "message": action.description},
            )
        elif action.type in {"priority_restow", "expedite_reefer"}:
            wo = self._tool(
                incident,
                ctx,
                "Executor",
                "workorder.draft",
                {
                    "type": "priority_restow",
                    "container_ids": action.container_ids,
                    "notes": action.description,
                },
            )
            self._tool(
                incident,
                ctx,
                "Executor",
                "workorder.dispatch",
                {"work_order_id": wo["id"], "approval_token": approval_token or "LOW-RISK"},
            )
        elif action.type == "request_cutoff_extension":
            hours = float(action.params.get("hours", 2))
            for vid in action.params.get("vessel_ids", []):
                for v in ctx.terminal["vessels"]:
                    if v["id"] == vid:
                        dt = datetime.fromisoformat(v["cutoff"]) + timedelta(hours=hours)
                        v["cutoff"] = dt.isoformat()
            self._tool(
                incident,
                ctx,
                "Executor",
                "notify.send",
                {
                    "channel": "carrier",
                    "audience": "liner_ops",
                    "message": action.description,
                },
            )
        elif action.type == "hold_for_next_vessel":
            self._tool(
                incident,
                ctx,
                "Executor",
                "workorder.draft",
                {
                    "type": "hold_for_next_vessel",
                    "container_ids": action.container_ids,
                    "notes": action.description,
                },
            )
            # Hold drafts do not auto-dispatch without explicit token in this demo
            if approval_token:
                wo = ctx.terminal["work_orders"][-1]
                self._tool(
                    incident,
                    ctx,
                    "Executor",
                    "workorder.dispatch",
                    {"work_order_id": wo["id"], "approval_token": approval_token},
                )
        elif action.type == "draft_dossier":
            self._tool(
                incident,
                ctx,
                "Executor",
                "notify.send",
                {"channel": "internal", "audience": "audit", "message": "Dossier drafted"},
            )


ORCHESTRATOR = Orchestrator()
