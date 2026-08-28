"""Unit tests for risk engine, policy, orchestrator, and approval edge cases."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agents.orchestrator import ApprovalError, Orchestrator
from app.data.seed import fresh_terminal
from app.engine.policy import action_requires_approval
from app.engine.risk import assess_at_risk, score_connection


def test_late_feeder_creates_risk():
    t = fresh_terminal()
    for v in t["vessels"]:
        if v["id"] == "V-FEED-07":
            v["eta"] = "2026-08-23T23:00:00+08:00"
            v["eta_uncertainty_h"] = 2.0
    at_risk = assess_at_risk(t, affected_vessel_ids=["V-FEED-07"])
    assert len(at_risk) >= 5
    assert at_risk[0]["risk"] >= 0.4


def test_policy_gates_physical_moves():
    assert action_requires_approval("priority_restow", risk_score=0.5, has_dg=False, has_reefer=False) is True
    assert action_requires_approval("notify_internal", risk_score=0.1, has_dg=False, has_reefer=False) is False


def test_orchestrator_late_feeder_awaits_approval():
    orch = Orchestrator()
    inc = orch.start("late_feeder", auto_approve=False)
    assert inc.status.value == "awaiting_approval"
    assert inc.selected_plan_id is not None
    assert any(e.kind == "tool_call" for e in inc.trace)
    assert any(e.agent == "Critic" for e in inc.trace)
    selected = next(p for p in inc.plans if p.selected)
    assert selected.connections_saved >= 1
    ap = next(a for a in inc.approvals if a.status == "pending")
    inc2 = orch.decide(inc.id, ap.approval_id, "approved")
    assert inc2.status.value == "closed"
    saved = inc2.result.get("connections_saved", 0)
    assert saved >= 1
    assert abs(selected.connections_saved - saved) <= 2


def test_crane_outage_rejects_unsafe_plan():
    orch = Orchestrator()
    inc = orch.start("crane_outage", auto_approve=False)
    unsafe = next(p for p in inc.plans if p.plan_id == "PLAN-X")
    assert any("REJECT" in n for n in unsafe.critic_notes)
    assert inc.selected_plan_id != "PLAN-X"
    at_risk_count = len(inc.at_risk)
    assert unsafe.connections_saved <= at_risk_count


def test_uncertainty_tool_fail_uses_fallback():
    orch = Orchestrator()
    inc = orch.start("uncertainty_tool_fail", auto_approve=True)
    assert inc.metrics.get("yard_fallback") is True
    assert any(e.kind == "tool_error" for e in inc.trace)
    assert inc.status.value in {"closed", "awaiting_approval", "escalated"}


def test_reject_escalates_without_executing():
    orch = Orchestrator()
    inc = orch.start("late_feeder", auto_approve=False)
    ap = next(a for a in inc.approvals if a.status == "pending")
    wo_before = len(orch.contexts[inc.id].terminal["work_orders"])
    inc2 = orch.decide(inc.id, ap.approval_id, "rejected", note="Too aggressive")
    assert inc2.status.value == "escalated"
    assert inc2.result["status"] == "escalated"
    wo_after = len(orch.contexts[inc.id].terminal["work_orders"])
    assert wo_after == wo_before


def test_double_approve_is_idempotent():
    orch = Orchestrator()
    inc = orch.start("late_feeder", auto_approve=False)
    ap = next(a for a in inc.approvals if a.status == "pending")
    orch.decide(inc.id, ap.approval_id, "approved")
    wo_count = len(orch.contexts[inc.id].terminal["work_orders"])
    try:
        orch.decide(inc.id, ap.approval_id, "approved")
        assert False, "expected ApprovalError"
    except ApprovalError:
        pass
    assert len(orch.contexts[inc.id].terminal["work_orders"]) == wo_count


def test_invalid_decision_rejected():
    orch = Orchestrator()
    inc = orch.start("late_feeder", auto_approve=False)
    ap = next(a for a in inc.approvals if a.status == "pending")
    try:
        orch.decide(inc.id, ap.approval_id, "maybe")
        assert False, "expected ApprovalError"
    except ApprovalError as e:
        assert "Invalid decision" in str(e)


def test_all_plans_saved_within_at_risk():
    orch = Orchestrator()
    for sid in ("late_feeder", "crane_outage", "uncertainty_tool_fail"):
        inc = orch.start(sid, auto_approve=False)
        n = len(inc.at_risk)
        for p in inc.plans:
            assert p.connections_saved <= n, f"{sid} {p.plan_id} saved {p.connections_saved} > {n}"


if __name__ == "__main__":
    test_late_feeder_creates_risk()
    test_policy_gates_physical_moves()
    test_orchestrator_late_feeder_awaits_approval()
    test_crane_outage_rejects_unsafe_plan()
    test_uncertainty_tool_fail_uses_fallback()
    test_reject_escalates_without_executing()
    test_double_approve_is_idempotent()
    test_invalid_decision_rejected()
    test_all_plans_saved_within_at_risk()
    print("All tests passed.")
