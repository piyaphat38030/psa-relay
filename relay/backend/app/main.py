from __future__ import annotations

import json
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from app.agents.orchestrator import ORCHESTRATOR, ApprovalError
from app.engine.policy import autonomy_rationale
from app.models import to_dict
from app.scenarios import list_scenarios
from app.tools.registry import REGISTRY, ToolError


class Handler(BaseHTTPRequestHandler):
    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, payload: object) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON body") from e

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            return self._json(
                200,
                {
                    "ok": True,
                    "service": "RELAY",
                    "mode": "demo_brain",
                    "incidents": len(ORCHESTRATOR.incidents),
                },
            )
        if path == "/api/meta":
            return self._json(
                200,
                {
                    "name": "RELAY",
                    "tagline": "Keep every connection — even when the schedule breaks.",
                    "autonomy": autonomy_rationale(),
                    "tools": sorted(REGISTRY.keys()),
                    "agents": ["Sentinel", "Analyst", "Planner", "Critic", "Executor", "Auditor"],
                    "domain_context": {
                        "hub": "Singapore / PSA-style transshipment hub",
                        "stats": [
                            {
                                "label": "Transshipment share",
                                "value": "~90%",
                                "source": "MPA Maritime Singapore 2024",
                            },
                            {
                                "label": "Off-schedule arrivals (1H 2024)",
                                "value": "~90%",
                                "source": "PSA / Maritime Executive Jul 2024",
                            },
                            {
                                "label": "Rehandling increase (1H 2024)",
                                "value": "+8%",
                                "source": "PSA / Maritime Executive Jul 2024",
                            },
                        ],
                        "alignment": "Agentic recovery loop on twin state — complements MPA Maritime Digital Twin scenario planning",
                        "twin_label": "Synthetic Tuas hub (not live PORTNET)",
                    },
                },
            )
        if path == "/api/scenarios":
            return self._json(200, list_scenarios())
        if path == "/api/incidents":
            return self._json(200, [to_dict(i) for i in ORCHESTRATOR.list_incidents()])
        if path.startswith("/api/incidents/") and path.endswith("/terminal"):
            incident_id = path.split("/")[3]
            ctx = ORCHESTRATOR.contexts.get(incident_id)
            if not ctx:
                return self._json(404, {"error": "Incident not found"})
            return self._json(
                200,
                {
                    "terminal_id": ctx.terminal["terminal_id"],
                    "name": ctx.terminal["name"],
                    "now_iso": ctx.terminal["now_iso"],
                    "vessels": ctx.terminal["vessels"],
                    "cranes": ctx.terminal["cranes"],
                    "yard_blocks": ctx.terminal["yard_blocks"],
                    "work_orders": ctx.terminal["work_orders"],
                    "notifications": ctx.terminal["notifications"],
                    "flags": ctx.terminal["flags"],
                    "tool_calls": ctx.call_log,
                },
            )
        if path.startswith("/api/incidents/"):
            incident_id = path.rstrip("/").split("/")[-1]
            try:
                return self._json(200, to_dict(ORCHESTRATOR.get(incident_id)))
            except KeyError:
                return self._json(404, {"error": "Incident not found"})
        return self._json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            body = self._read_json()
        except ValueError as e:
            return self._json(400, {"error": str(e)})

        if path == "/api/incidents/run":
            scenario_id = body.get("scenario_id", "late_feeder")
            auto_approve = bool(body.get("auto_approve", False))
            try:
                incident = ORCHESTRATOR.start(scenario_id, auto_approve=auto_approve)
                return self._json(200, to_dict(incident))
            except ValueError as e:
                return self._json(400, {"error": str(e)})
            except ToolError as e:
                return self._json(502, {"error": str(e), "retryable": e.retryable})
            except Exception as e:  # noqa: BLE001
                traceback.print_exc()
                return self._json(500, {"error": f"Orchestrator failed: {e}"})

        if "/approvals/" in path and path.startswith("/api/incidents/"):
            parts = path.strip("/").split("/")
            try:
                incident_id = parts[2]
                approval_id = parts[4]
            except IndexError:
                return self._json(400, {"error": "Bad path"})
            try:
                incident = ORCHESTRATOR.decide(
                    incident_id,
                    approval_id,
                    body.get("decision", "approved"),
                    decided_by=body.get("decided_by", "ops_planner"),
                    note=body.get("note", ""),
                )
                return self._json(200, to_dict(incident))
            except ApprovalError as e:
                return self._json(409, {"error": str(e)})
            except KeyError:
                return self._json(404, {"error": "Incident or approval not found"})

        return self._json(404, {"error": "Not found"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[RELAY] {self.address_string()} {fmt % args}")


def main() -> None:
    host, port = "127.0.0.1", 8000
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"RELAY API on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
