"""Terminal seed state for RELAY demos — synthetic PSA-style T/S hub."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

TERMINAL: dict[str, Any] = {
    "terminal_id": "SGSIN-TUAS-DEMO",
    "name": "Tuas Hub (Synthetic Demo Twin)",
    "timezone": "Asia/Singapore",
    "now_iso": "2026-08-23T08:00:00+08:00",
    "berths": [
        {"id": "B01", "length_m": 400, "status": "occupied", "vessel_id": "V-MAIN-01"},
        {"id": "B02", "length_m": 360, "status": "occupied", "vessel_id": "V-MAIN-02"},
        {"id": "B03", "length_m": 300, "status": "reserved", "vessel_id": "V-FEED-07"},
        {"id": "B04", "length_m": 300, "status": "free", "vessel_id": None},
    ],
    "cranes": [
        {"id": "QC-01", "berth_id": "B01", "status": "available", "moves_per_hour": 32},
        {"id": "QC-02", "berth_id": "B01", "status": "available", "moves_per_hour": 30},
        {"id": "QC-03", "berth_id": "B02", "status": "available", "moves_per_hour": 28},
        {"id": "QC-07", "berth_id": "B03", "status": "available", "moves_per_hour": 26},
    ],
    "yard_blocks": [
        {"id": "Y-A1", "util_pct": 78, "hotspot": False, "reefer_plugs_free": 40},
        {"id": "Y-A2", "util_pct": 91, "hotspot": True, "reefer_plugs_free": 6},
        {"id": "Y-B1", "util_pct": 64, "hotspot": False, "reefer_plugs_free": 55},
        {"id": "Y-C3", "util_pct": 88, "hotspot": True, "reefer_plugs_free": 12},
    ],
    "vessels": [
        {
            "id": "V-MAIN-01",
            "name": "PSA ORION",
            "service": "AEU1",
            "role": "mainline",
            "eta": "2026-08-23T06:30:00+08:00",
            "etd": "2026-08-23T22:00:00+08:00",
            "cutoff": "2026-08-23T18:00:00+08:00",
            "berth_id": "B01",
            "status": "alongside",
            "eta_uncertainty_h": 0.5,
        },
        {
            "id": "V-MAIN-02",
            "name": "PACIFIC TITAN",
            "service": "TPX3",
            "role": "mainline",
            "eta": "2026-08-23T10:00:00+08:00",
            "etd": "2026-08-24T04:00:00+08:00",
            "cutoff": "2026-08-23T22:00:00+08:00",
            "berth_id": "B02",
            "status": "inbound",
            "eta_uncertainty_h": 1.0,
        },
        {
            "id": "V-FEED-07",
            "name": "STRAITS FEEDER 7",
            "service": "IDN-FEED",
            "role": "feeder",
            "eta": "2026-08-23T09:00:00+08:00",
            "etd": "2026-08-23T17:00:00+08:00",
            "cutoff": "2026-08-23T14:00:00+08:00",
            "berth_id": "B03",
            "status": "inbound",
            "eta_uncertainty_h": 1.5,
        },
        {
            "id": "V-FEED-12",
            "name": "JAVA LINK 12",
            "service": "JKT-FEED",
            "role": "feeder",
            "eta": "2026-08-24T08:00:00+08:00",
            "etd": "2026-08-24T16:00:00+08:00",
            "cutoff": "2026-08-24T12:00:00+08:00",
            "berth_id": None,
            "status": "scheduled",
            "eta_uncertainty_h": 2.0,
        },
    ],
    "containers": [
        # Connections: FEED-07 -> MAIN-01 (tight)
        {"id": "MSCU1234567", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-01", "block": "Y-A2", "teu": 1, "priority": "premium", "reefer": False, "dg": False, "move_minutes": 45},
        {"id": "TGHU7654321", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-01", "block": "Y-A2", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 50},
        {"id": "HLCU9988776", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-01", "block": "Y-C3", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 55},
        {"id": "TEMU5544332", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-01", "block": "Y-A1", "teu": 1, "priority": "premium", "reefer": True, "dg": False, "move_minutes": 60},
        {"id": "OOLU1122334", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-02", "block": "Y-B1", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 40},
        {"id": "CMAU6677889", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-02", "block": "Y-B1", "teu": 1, "priority": "premium", "reefer": False, "dg": True, "move_minutes": 70},
        {"id": "NYKU4455667", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-02", "block": "Y-A1", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 42},
        # MAIN-02 inbound discharge connecting to FEED-12
        {"id": "FSCU2211009", "from_vessel": "V-MAIN-02", "to_vessel": "V-FEED-12", "block": "Y-C3", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 35},
        {"id": "SEGU3300112", "from_vessel": "V-MAIN-02", "to_vessel": "V-FEED-12", "block": "Y-A2", "teu": 1, "priority": "premium", "reefer": True, "dg": False, "move_minutes": 48},
        {"id": "TCNU8899001", "from_vessel": "V-MAIN-02", "to_vessel": "V-FEED-12", "block": "Y-B1", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 30},
        # Extra volume for scale story
        {"id": "EGLV1000001", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-01", "block": "Y-A2", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 52},
        {"id": "EGLV1000002", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-01", "block": "Y-C3", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 58},
        {"id": "EGLV1000003", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-01", "block": "Y-A1", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 47},
        {"id": "EGLV1000004", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-02", "block": "Y-B1", "teu": 1, "priority": "standard", "reefer": False, "dg": False, "move_minutes": 44},
        {"id": "EGLV1000005", "from_vessel": "V-FEED-07", "to_vessel": "V-MAIN-02", "block": "Y-A1", "teu": 1, "priority": "premium", "reefer": False, "dg": False, "move_minutes": 46},
    ],
    "cost_model": {
        "missed_connection_usd": 1800,
        "priority_restow_usd": 220,
        "cutoff_extension_request_usd": 0,
        "carrier_notice_usd": 0,
        "demurrage_proxy_usd_per_day": 150,
    },
    "notifications": [],
    "work_orders": [],
    "flags": {"yard_api_down": False, "qc07_down": False},
}


def fresh_terminal() -> dict[str, Any]:
    return deepcopy(TERMINAL)
