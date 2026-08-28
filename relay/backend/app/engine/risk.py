"""Deterministic connection-risk engine — team-designed domain logic (not LLM).

Connection window (industry: "connection buffer"):
  ready_at = inbound_ETA + yard_move + uncertainty_buffer
  slack_hours = outbound_cutoff - ready_at

Negative slack => box is inside the miss window. Scoring is piecewise on slack,
weighted by commercial/safety flags (premium, reefer, DG). See research/07.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


PRIORITY_WEIGHT = {"premium": 1.35, "standard": 1.0}
REEFER_WEIGHT = 1.15
DG_WEIGHT = 1.25
HOTSPOT_PENALTY_MIN = 15


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def vessel_map(terminal: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {v["id"]: v for v in terminal["vessels"]}


def block_map(terminal: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {b["id"]: b for b in terminal["yard_blocks"]}


def score_connection(
    container: dict[str, Any],
    terminal: dict[str, Any],
    *,
    now: datetime | None = None,
    eta_overrides: dict[str, str] | None = None,
    uncertainty_boost_h: float = 0.0,
) -> dict[str, Any]:
    vessels = vessel_map(terminal)
    blocks = block_map(terminal)
    now = now or _parse(terminal["now_iso"])
    eta_overrides = eta_overrides or {}

    inbound = vessels[container["from_vessel"]]
    outbound = vessels[container["to_vessel"]]

    inbound_eta = _parse(eta_overrides.get(inbound["id"], inbound["eta"]))
    outbound_cutoff = _parse(outbound["cutoff"])

    # Available window after inbound arrives, minus move time and uncertainty buffer
    unc_h = inbound.get("eta_uncertainty_h", 0) + outbound.get("eta_uncertainty_h", 0) + uncertainty_boost_h
    buffer = timedelta(hours=unc_h)
    move = timedelta(minutes=container["move_minutes"])
    hotspot = blocks.get(container["block"], {}).get("hotspot", False)
    if hotspot:
        move += timedelta(minutes=HOTSPOT_PENALTY_MIN)

    ready_at = inbound_eta + move + buffer
    slack_h = (outbound_cutoff - ready_at).total_seconds() / 3600.0

    # Risk: 0 safe → 1 certain miss. Negative slack = miss.
    if slack_h >= 6:
        base_risk = 0.05
    elif slack_h >= 3:
        base_risk = 0.2
    elif slack_h >= 1:
        base_risk = 0.45
    elif slack_h >= 0:
        base_risk = 0.7
    elif slack_h >= -3:
        base_risk = 0.88
    else:
        base_risk = 0.98

    weight = PRIORITY_WEIGHT.get(container["priority"], 1.0)
    if container.get("reefer"):
        weight *= REEFER_WEIGHT
    if container.get("dg"):
        weight *= DG_WEIGHT

    weighted_risk = min(1.0, base_risk * (0.85 + 0.15 * weight))
    miss_cost = terminal["cost_model"]["missed_connection_usd"] * weight

    return {
        "container_id": container["id"],
        "from_vessel": container["from_vessel"],
        "to_vessel": container["to_vessel"],
        "priority": container["priority"],
        "reefer": container.get("reefer", False),
        "dg": container.get("dg", False),
        "block": container["block"],
        "slack_hours": round(slack_h, 2),
        "risk": round(weighted_risk, 3),
        "expected_miss_cost_usd": round(miss_cost * weighted_risk, 2),
        "hotspot": hotspot,
        "inbound_eta": inbound_eta.isoformat(),
        "outbound_cutoff": outbound_cutoff.isoformat(),
        "uncertainty_hours": round(unc_h, 2),
    }


def assess_at_risk(
    terminal: dict[str, Any],
    *,
    affected_vessel_ids: list[str] | None = None,
    eta_overrides: dict[str, str] | None = None,
    uncertainty_boost_h: float = 0.0,
    risk_threshold: float = 0.4,
) -> list[dict[str, Any]]:
    scored = []
    for c in terminal["containers"]:
        if affected_vessel_ids and c["from_vessel"] not in affected_vessel_ids and c["to_vessel"] not in affected_vessel_ids:
            continue
        row = score_connection(
            c,
            terminal,
            eta_overrides=eta_overrides,
            uncertainty_boost_h=uncertainty_boost_h,
        )
        if row["risk"] >= risk_threshold:
            scored.append(row)
    scored.sort(key=lambda r: (-r["risk"], -r["expected_miss_cost_usd"]))
    return scored


def summarise_risk(at_risk: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(at_risk),
        "teu": sum(1 for _ in at_risk),
        "expected_loss_usd": round(sum(r["expected_miss_cost_usd"] for r in at_risk), 2),
        "premium": sum(1 for r in at_risk if r["priority"] == "premium"),
        "reefer": sum(1 for r in at_risk if r["reefer"]),
        "dg": sum(1 for r in at_risk if r["dg"]),
    }
