from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class IncidentStatus(str, Enum):
    DETECTED = "detected"
    ANALYSING = "analysing"
    PLANNING = "planning"
    CRITIQUE = "critique"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    CLOSED = "closed"
    ESCALATED = "escalated"
    FAILED = "failed"


from dataclasses import dataclass, field


@dataclass
class TraceEvent:
    ts: str
    agent: str
    kind: str
    summary: str
    detail: dict[str, Any] = field(default_factory=dict)
    tokens_est: int = 0


@dataclass
class PlanAction:
    action_id: str
    type: str
    description: str
    container_ids: list[str] = field(default_factory=list)
    requires_approval: bool = False
    risk_score: float = 0.0
    estimated_cost_usd: float = 0.0
    estimated_connections_saved: int = 0
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPlan:
    plan_id: str
    title: str
    summary: str
    score: float
    actions: list[PlanAction]
    connections_saved: int
    residual_risk: float
    estimated_cost_usd: float
    critic_notes: list[str] = field(default_factory=list)
    selected: bool = False


@dataclass
class ApprovalItem:
    approval_id: str
    plan_id: str
    action_ids: list[str]
    rationale: str
    status: str = "pending"
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None


@dataclass
class Incident:
    id: str
    scenario_id: str
    title: str
    status: IncidentStatus
    trigger: dict[str, Any]
    created_at: str
    updated_at: str
    objective: str = ""
    at_risk: list[dict[str, Any]] = field(default_factory=list)
    plans: list[RecoveryPlan] = field(default_factory=list)
    selected_plan_id: Optional[str] = None
    approvals: list[ApprovalItem] = field(default_factory=list)
    trace: list[TraceEvent] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def to_dict(obj: Any) -> Any:
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: to_dict(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, list):
        return [to_dict(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj
