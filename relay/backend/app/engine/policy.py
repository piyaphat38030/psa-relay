"""Autonomy / approval policy — higher autonomy is NOT always better."""

from __future__ import annotations

from typing import Any


# Action types and whether they need a human by default
ACTION_POLICY: dict[str, dict[str, Any]] = {
    "notify_internal": {"requires_approval": False, "base_risk": 0.1},
    "notify_carrier": {"requires_approval": False, "base_risk": 0.2},
    "draft_dossier": {"requires_approval": False, "base_risk": 0.05},
    "refresh_forecast": {"requires_approval": False, "base_risk": 0.05},
    "priority_restow": {"requires_approval": True, "base_risk": 0.75},
    "request_cutoff_extension": {"requires_approval": True, "base_risk": 0.65},
    "hold_for_next_vessel": {"requires_approval": True, "base_risk": 0.55},
    "expedite_reefer": {"requires_approval": True, "base_risk": 0.8},
    "block_dg_move": {"requires_approval": True, "base_risk": 0.95},
}


def action_requires_approval(action_type: str, *, risk_score: float, has_dg: bool, has_reefer: bool) -> bool:
    policy = ACTION_POLICY.get(action_type, {"requires_approval": True, "base_risk": 0.7})
    if policy["requires_approval"]:
        return True
    if has_dg and action_type not in {"notify_internal", "draft_dossier", "block_dg_move"}:
        return True
    if risk_score >= 0.85:
        return True
    if has_reefer and action_type in {"priority_restow", "expedite_reefer"}:
        return True
    return False


def autonomy_rationale() -> str:
    return (
        "RELAY runs sense/triage/planning autonomously, but gates physical and commercial "
        "moves behind human approval. High autonomy is reserved for low-reversibility-cost "
        "actions (notices, dossiers, forecasts). This matches PSA operational risk: a wrong "
        "restow is expensive; a wrong notification is cheap."
    )
