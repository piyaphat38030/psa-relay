"""Tool registry with retries, failure injection, and audit-friendly results."""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Callable

from app.data.seed import fresh_terminal
from app.engine.risk import assess_at_risk, summarise_risk, vessel_map


ToolFn = Callable[["ToolContext", dict[str, Any]], dict[str, Any]]


class ToolError(Exception):
    def __init__(self, message: str, *, retryable: bool = True):
        super().__init__(message)
        self.retryable = retryable


class ToolContext:
    def __init__(self, terminal: dict[str, Any] | None = None):
        self.terminal = terminal or fresh_terminal()
        self.call_log: list[dict[str, Any]] = []

    def reset(self) -> None:
        self.terminal = fresh_terminal()
        self.call_log = []


def _ok(data: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "data": data}


def tool_vessel_schedule_get(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    vid = params.get("vessel_id")
    vessels = ctx.terminal["vessels"]
    if vid:
        for v in vessels:
            if v["id"] == vid:
                return _ok(v)
        raise ToolError(f"Vessel {vid} not found", retryable=False)
    return _ok({"vessels": vessels})


def tool_eta_update(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    vid = params["vessel_id"]
    new_eta = params["new_eta"]
    for v in ctx.terminal["vessels"]:
        if v["id"] == vid:
            old = v["eta"]
            v["eta"] = new_eta
            if params.get("uncertainty_h") is not None:
                v["eta_uncertainty_h"] = params["uncertainty_h"]
            return _ok({"vessel_id": vid, "old_eta": old, "new_eta": new_eta})
    raise ToolError(f"Vessel {vid} not found", retryable=False)


def tool_connections_query_at_risk(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    if ctx.terminal["flags"].get("yard_api_down") and params.get("require_yard", False):
        raise ToolError("Yard inventory API 503 Service Unavailable", retryable=True)

    at_risk = assess_at_risk(
        ctx.terminal,
        affected_vessel_ids=params.get("affected_vessel_ids"),
        eta_overrides=params.get("eta_overrides"),
        uncertainty_boost_h=float(params.get("uncertainty_boost_h", 0)),
        risk_threshold=float(params.get("risk_threshold", 0.4)),
    )
    return _ok({"at_risk": at_risk, "summary": summarise_risk(at_risk)})


def tool_yard_inventory_lookup(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    if ctx.terminal["flags"].get("yard_api_down"):
        raise ToolError("Yard inventory API 503 Service Unavailable", retryable=True)
    cid = params.get("container_id")
    for c in ctx.terminal["containers"]:
        if c["id"] == cid:
            block = next(b for b in ctx.terminal["yard_blocks"] if b["id"] == c["block"])
            return _ok({"container": c, "block": block})
    raise ToolError(f"Container {cid} not found", retryable=False)


def tool_yard_hotspot_score(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    blocks = ctx.terminal["yard_blocks"]
    return _ok({"blocks": blocks, "hotspots": [b for b in blocks if b["hotspot"]]})


def tool_crane_availability(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    cranes = ctx.terminal["cranes"]
    if ctx.terminal["flags"].get("qc07_down"):
        cranes = [{**c, "status": "down"} if c["id"] == "QC-07" else c for c in cranes]
        ctx.terminal["cranes"] = cranes
    return _ok({"cranes": cranes})


def tool_recovery_simulate(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    """What-if: apply temporary move-time reductions / holds and re-score.

    Counts fleet-wide connection recovery (not only restow targets). Cutoff
    extensions spill over to every box on those vessels — matching post-execute
    Auditor re-score so plan cards stay honest in the demo.
    """
    at_risk_ids = set(params.get("container_ids", []))
    mode = params.get("mode", "priority_restow")
    eta_overrides = params.get("eta_overrides") or {}
    base_uncertainty = float(params.get("uncertainty_boost_h", 0))

    vessels = vessel_map(ctx.terminal)
    original_moves = {c["id"]: c["move_minutes"] for c in ctx.terminal["containers"]}
    unc_backup = {vid: v.get("eta_uncertainty_h", 0) for vid, v in vessels.items()}
    cutoff_backup: dict[str, str] = {}

    before = assess_at_risk(
        ctx.terminal,
        affected_vessel_ids=params.get("affected_vessel_ids"),
        eta_overrides=eta_overrides,
        uncertainty_boost_h=base_uncertainty,
        risk_threshold=0.4,
    )
    # Fleet-wide baseline (cutoff extension benefits all, not only restow set)
    before_ids = {r["container_id"] for r in before}
    before_loss = sum(r["expected_miss_cost_usd"] for r in before)

    sim_uncertainty = base_uncertainty
    try:
        for c in ctx.terminal["containers"]:
            if c["id"] not in at_risk_ids:
                continue
            if mode == "priority_restow":
                c["move_minutes"] = max(18, int(c["move_minutes"] * 0.42))
                if c.get("block") in {b["id"] for b in ctx.terminal["yard_blocks"] if b.get("hotspot")}:
                    c["move_minutes"] = max(18, c["move_minutes"] - 12)
            elif mode == "expedite_reefer" and c.get("reefer"):
                c["move_minutes"] = max(20, int(c["move_minutes"] * 0.4))

        if mode == "priority_restow":
            for vid in {c["from_vessel"] for c in ctx.terminal["containers"] if c["id"] in at_risk_ids}:
                vessels[vid]["eta_uncertainty_h"] = max(0.25, vessels[vid].get("eta_uncertainty_h", 1) * 0.45)
            sim_uncertainty = max(0.0, base_uncertainty - 1.0)

        cutoff_ext_h = float(params.get("cutoff_extension_h", 0))
        if cutoff_ext_h:
            for vid in params.get("extend_vessel_ids", []):
                if vid in vessels:
                    cutoff_backup[vid] = vessels[vid]["cutoff"]
                    dt = datetime.fromisoformat(vessels[vid]["cutoff"]) + timedelta(hours=cutoff_ext_h)
                    vessels[vid]["cutoff"] = dt.isoformat()

        rescored = assess_at_risk(
            ctx.terminal,
            affected_vessel_ids=params.get("affected_vessel_ids"),
            eta_overrides=eta_overrides,
            uncertainty_boost_h=sim_uncertainty,
            risk_threshold=0.4,
        )
        still = {r["container_id"] for r in rescored}
        saved = len([i for i in before_ids if i not in still])
        residual = list(rescored)
        after_loss = sum(r["expected_miss_cost_usd"] for r in residual)
        loss_avoided = max(0.0, before_loss - after_loss)
    finally:
        for vid, old in cutoff_backup.items():
            vessels[vid]["cutoff"] = old
        for vid, old in unc_backup.items():
            vessels[vid]["eta_uncertainty_h"] = old
        for c in ctx.terminal["containers"]:
            if c["id"] in original_moves:
                c["move_minutes"] = original_moves[c["id"]]

    return _ok(
        {
            "mode": mode,
            "connections_saved": saved,
            "loss_avoided_usd": round(loss_avoided, 2),
            "residual_at_risk": residual,
            "residual_count": len(residual),
        }
    )


def tool_workorder_draft(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    wo = {
        "id": f"WO-{len(ctx.terminal['work_orders']) + 1:04d}",
        "type": params.get("type", "priority_restow"),
        "container_ids": params.get("container_ids", []),
        "status": "draft",
        "notes": params.get("notes", ""),
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    ctx.terminal["work_orders"].append(wo)
    return _ok(wo)


def tool_workorder_dispatch(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    if not params.get("approval_token"):
        raise ToolError("Missing approval_token for dispatch", retryable=False)
    wid = params["work_order_id"]
    for wo in ctx.terminal["work_orders"]:
        if wo["id"] == wid:
            wo["status"] = "dispatched"
            wo["dispatched_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
            # Apply physical effect: reduce move times + uncertainty for restow
            if wo["type"] == "priority_restow":
                touched_vessels = set()
                for c in ctx.terminal["containers"]:
                    if c["id"] in wo["container_ids"]:
                        c["move_minutes"] = max(18, int(c["move_minutes"] * 0.42))
                        touched_vessels.add(c["from_vessel"])
                for v in ctx.terminal["vessels"]:
                    if v["id"] in touched_vessels:
                        v["eta_uncertainty_h"] = max(0.25, v.get("eta_uncertainty_h", 1) * 0.45)
            return _ok(wo)
    raise ToolError(f"Work order {wid} not found", retryable=False)


def tool_notify(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    note = {
        "id": f"N-{len(ctx.terminal['notifications']) + 1:04d}",
        "channel": params.get("channel", "internal"),
        "audience": params.get("audience", "ops"),
        "message": params.get("message", ""),
        "sent_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    ctx.terminal["notifications"].append(note)
    return _ok(note)


def tool_weather_get(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    return _ok(
        {
            "location": "Singapore Strait",
            "condition": params.get("force_condition", "haze_moderate"),
            "visibility_nm": 3.5,
            "wind_kt": 12,
            "impact": "Minor berthing delay risk; AIS gaps possible near anchorage.",
        }
    )


def tool_ais_uncertainty(ctx: ToolContext, params: dict[str, Any]) -> dict[str, Any]:
    return _ok(
        {
            "vessel_id": params.get("vessel_id"),
            "last_fix_age_min": params.get("last_fix_age_min", 95),
            "uncertainty_hours": params.get("uncertainty_hours", 3.5),
            "quality": "degraded",
        }
    )


REGISTRY: dict[str, ToolFn] = {
    "vessel_schedule.get": tool_vessel_schedule_get,
    "eta.update": tool_eta_update,
    "connections.query_at_risk": tool_connections_query_at_risk,
    "yard.inventory_lookup": tool_yard_inventory_lookup,
    "yard.hotspot_score": tool_yard_hotspot_score,
    "crane.availability": tool_crane_availability,
    "recovery.simulate_plan": tool_recovery_simulate,
    "workorder.draft": tool_workorder_draft,
    "workorder.dispatch": tool_workorder_dispatch,
    "notify.send": tool_notify,
    "weather.get": tool_weather_get,
    "ais.uncertainty": tool_ais_uncertainty,
}


def call_tool(
    ctx: ToolContext,
    name: str,
    params: dict[str, Any],
    *,
    retries: int = 2,
    inject_fail_once: bool = False,
) -> dict[str, Any]:
    if name not in REGISTRY:
        raise ToolError(f"Unknown tool {name}", retryable=False)

    attempts = 0
    last_err: Exception | None = None
    fail_budget = 1 if inject_fail_once else 0

    while attempts <= retries:
        attempts += 1
        started = time.time()
        try:
            if fail_budget > 0 and attempts == 1 and name.startswith("yard."):
                fail_budget -= 1
                raise ToolError("Injected transient yard API failure", retryable=True)
            result = REGISTRY[name](ctx, params)
            ctx.call_log.append(
                {
                    "tool": name,
                    "params": params,
                    "ok": True,
                    "attempts": attempts,
                    "latency_ms": int((time.time() - started) * 1000),
                }
            )
            return {**result, "attempts": attempts, "tool": name}
        except ToolError as e:
            last_err = e
            ctx.call_log.append(
                {
                    "tool": name,
                    "params": params,
                    "ok": False,
                    "error": str(e),
                    "attempts": attempts,
                    "retryable": e.retryable,
                    "latency_ms": int((time.time() - started) * 1000),
                }
            )
            if not e.retryable or attempts > retries:
                raise
            time.sleep(0.05)
    raise last_err or ToolError("Tool failed")
