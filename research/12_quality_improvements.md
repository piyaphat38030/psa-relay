# Quality improvement pass (2026-08-28)

## Backend

- **Approval guards** — reject invalid decisions; block double-approve (409)
- **PLAN-X cap** — `connections_saved` cannot exceed at-risk count
- **Thread lock** on orchestrator; fixed auto_approve deadlock
- **API errors** — JSON parse, ToolError, ApprovalError with proper status codes

## Frontend

- **Staged trace stream** — events reveal ~140ms apart for demo impact
- **Terminal twin panel** — vessels, cranes, flags from `/api/incidents/{id}/terminal`
- **Work orders** — shown after successful close
- **Escalation UX** — reject no longer shows “saved 0”; proper banner
- **Phase stepper** — escalated stops at approval, not “closed”
- **API health badge** + offline banner with start command
- **At-risk expand** — “Show N more” for large sets
- **Error parsing** — shows API `error` field

## Tests

9 tests (was 5): reject, double-approve, invalid decision, plan invariants.

## Docs

- `relay/README.md` — agent loop, API table, correct deliverables path
- `.gitignore` — node_modules, dist, venv
