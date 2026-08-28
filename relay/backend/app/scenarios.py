"""Scenario triggers for reproducible demos."""

from __future__ import annotations

from typing import Any


SCENARIOS: dict[str, dict[str, Any]] = {
    "late_feeder": {
        "id": "late_feeder",
        "title": "Feeder ETA slip threatens mainline connections",
        "description": (
            "STRAITS FEEDER 7 revises ETA by +5.5h after upstream bunching (Red Sea ripple). "
            "AEU1/TPX3 connections lose buffer — priority restow or cutoff negotiation required."
        ),
        "trigger": {
            "type": "operational_alert",
            "alert": "VESSEL_ETA_REVISED",
            "vessel_id": "V-FEED-07",
            "old_eta": "2026-08-23T09:00:00+08:00",
            "new_eta": "2026-08-23T14:30:00+08:00",
            "uncertainty_h": 1.5,
            "source": "carrier_advisory",
        },
        "setup": {"eta_vessel": "V-FEED-07", "new_eta": "2026-08-23T14:30:00+08:00", "uncertainty_h": 1.5},
        "flags": {},
    },
    "crane_outage": {
        "id": "crane_outage",
        "title": "QC-07 downtime compresses feeder workface",
        "description": (
            "QC-07 hydraulic fault on B03 (~6h repair). Workface collapses; rehandling pressure rises. "
            "Critic must reject plans that ignore crane derate (PLAN-X stress test)."
        ),
        "trigger": {
            "type": "state_change",
            "alert": "CRANE_DOWN",
            "crane_id": "QC-07",
            "eta_repair_h": 6,
            "berth_id": "B03",
        },
        "setup": {
            # Mild ETA pressure + crane down to force hard tradeoffs
            "eta_vessel": "V-FEED-07",
            "new_eta": "2026-08-23T12:30:00+08:00",
            "uncertainty_h": 1.0,
            "inflate_move_factor": 1.8,
        },
        "flags": {"qc07_down": True},
    },
    "uncertainty_tool_fail": {
        "id": "uncertainty_tool_fail",
        "title": "AIS gap + yard API failure under weather degradation",
        "description": (
            "Haze degrades AIS for IDN-FEED connections; yard inventory API returns 503. "
            "Widen uncertainty bands, retry→cache fallback, partial recovery with visible residual risk."
        ),
        "trigger": {
            "type": "process_metric",
            "alert": "AIS_QUALITY_DEGRADED",
            "vessel_id": "V-FEED-07",
            "metric": "ais_fix_age_min",
            "value": 95,
        },
        "setup": {
            "eta_vessel": "V-FEED-07",
            "new_eta": "2026-08-23T14:00:00+08:00",
            "uncertainty_h": 3.5,
            "uncertainty_boost_h": 2.5,
        },
        "flags": {"yard_api_down": True},
        "inject_tool_fail": True,
    },
}


def list_scenarios() -> list[dict[str, Any]]:
    return [
        {"id": s["id"], "title": s["title"], "description": s["description"], "trigger": s["trigger"]}
        for s in SCENARIOS.values()
    ]
