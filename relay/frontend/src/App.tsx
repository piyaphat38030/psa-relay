import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

type Scenario = {
  id: string
  title: string
  description: string
  trigger: Record<string, unknown>
}

type DomainStat = {
  label: string
  value: string
  source: string
}

type Meta = {
  domain_context?: {
    stats: DomainStat[]
    alignment: string
    twin_label: string
  }
}

type TraceEvent = {
  ts: string
  agent: string
  kind: string
  summary: string
  detail: Record<string, unknown>
  tokens_est: number
}

type Plan = {
  plan_id: string
  title: string
  summary: string
  score: number
  critic_notes: string[]
  connections_saved: number
  residual_risk: number
  estimated_cost_usd: number
  selected: boolean
}

type Approval = {
  approval_id: string
  plan_id: string
  action_ids: string[]
  rationale: string
  status: string
}

type AtRisk = {
  container_id: string
  from_vessel: string
  to_vessel: string
  priority: string
  risk: number
  slack_hours: number
  expected_miss_cost_usd: number
  reefer: boolean
  dg: boolean
}

type WorkOrder = {
  id: string
  type: string
  status: string
  container_ids: string[]
  notes?: string
}

type TerminalTwin = {
  name: string
  vessels: { id: string; name: string; eta: string; cutoff: string; role: string }[]
  cranes: { id: string; status: string; workface: string }[]
  work_orders: WorkOrder[]
  notifications: { channel: string; audience: string; message: string }[]
  flags: Record<string, unknown>
}

type IncidentResult = {
  status: 'closed' | 'escalated'
  message?: string
  note?: string
  connections_saved?: number
  loss_avoided_usd?: number
  selected_plan?: string
  work_orders?: WorkOrder[]
  notifications?: number
}

type Incident = {
  id: string
  scenario_id: string
  title: string
  status: string
  objective: string
  at_risk: AtRisk[]
  plans: Plan[]
  selected_plan_id?: string
  approvals: Approval[]
  trace: TraceEvent[]
  metrics: {
    risk_summary?: { count: number; expected_loss_usd: number }
    post_summary?: { count: number }
    connections_saved?: number
    tokens_est_total?: number
    yard_fallback?: boolean
  }
  result?: IncidentResult
}

const API = ''

const PHASES = [
  'detected',
  'analysing',
  'planning',
  'critique',
  'awaiting_approval',
  'executing',
  'closed',
] as const

function phaseIndex(status: string | undefined): number {
  if (!status) return -1
  if (status === 'escalated') return 4
  if (status === 'failed') return -1
  const idx = PHASES.indexOf(status as (typeof PHASES)[number])
  return idx >= 0 ? idx : -1
}

function formatStatus(status: string): string {
  return status.replace(/_/g, ' ')
}

function formatTime(ts: string): string {
  try {
    const d = new Date(ts)
    return d.toLocaleTimeString('en-SG', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
  } catch {
    return ts.slice(11, 19)
  }
}

function formatUsd(n: number): string {
  return `$${Math.round(n).toLocaleString()}`
}

async function j<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let msg = await res.text()
    try {
      const parsed = JSON.parse(msg) as { error?: string }
      if (parsed.error) msg = parsed.error
    } catch {
      /* keep raw */
    }
    throw new Error(msg)
  }
  return res.json()
}

export default function App() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [meta, setMeta] = useState<Meta | null>(null)
  const [scenarioId, setScenarioId] = useState('late_feeder')
  const [incident, setIncident] = useState<Incident | null>(null)
  const [twin, setTwin] = useState<TerminalTwin | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apiOk, setApiOk] = useState<boolean | null>(null)
  const [visibleTrace, setVisibleTrace] = useState(0)
  const [showAllAtRisk, setShowAllAtRisk] = useState(false)
  const traceRef = useRef<HTMLDivElement>(null)

  const loadTwin = useCallback(async (incidentId: string) => {
    try {
      const t = await j<TerminalTwin>(`/api/incidents/${incidentId}/terminal`)
      setTwin(t)
    } catch {
      setTwin(null)
    }
  }, [])

  useEffect(() => {
    const poll = () =>
      j<{ ok: boolean }>('/api/health')
        .then(() => setApiOk(true))
        .catch(() => setApiOk(false))
    poll()
    const id = window.setInterval(poll, 8000)
    return () => window.clearInterval(id)
  }, [])

  useEffect(() => {
    if (apiOk !== true) return
    j<Scenario[]>('/api/scenarios').then(setScenarios).catch((e) => setError(String(e)))
    j<Meta>('/api/meta').then(setMeta).catch(() => {})
  }, [apiOk])

  useEffect(() => {
    if (!incident?.trace.length) {
      setVisibleTrace(0)
      return
    }
    setVisibleTrace(0)
    let i = 0
    const tick = () => {
      i += 1
      setVisibleTrace(i)
      if (i < incident.trace.length) {
        window.setTimeout(tick, 140)
      }
    }
    const start = window.setTimeout(tick, 120)
    return () => window.clearTimeout(start)
  }, [incident?.id, incident?.trace.length])

  useEffect(() => {
    if (traceRef.current && visibleTrace > 0) {
      traceRef.current.scrollTop = traceRef.current.scrollHeight
    }
  }, [visibleTrace])

  const pending = useMemo(
    () => incident?.approvals.find((a) => a.status === 'pending'),
    [incident],
  )

  const risk = incident?.metrics?.risk_summary
  const post = incident?.metrics?.post_summary
  const activePhase = phaseIndex(incident?.status)
  const isEscalated = incident?.status === 'escalated'
  const isClosed = incident?.status === 'closed'

  const atRiskVisible = showAllAtRisk ? incident?.at_risk ?? [] : (incident?.at_risk ?? []).slice(0, 10)
  const atRiskHidden = (incident?.at_risk.length ?? 0) - atRiskVisible.length

  async function runScenario() {
    setBusy(true)
    setError(null)
    setTwin(null)
    setShowAllAtRisk(false)
    try {
      const inc = await j<Incident>('/api/incidents/run', {
        method: 'POST',
        body: JSON.stringify({ scenario_id: scenarioId, auto_approve: false }),
      })
      setIncident(inc)
      void loadTwin(inc.id)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  async function decide(decision: 'approved' | 'rejected') {
    if (!incident || !pending) return
    setBusy(true)
    setError(null)
    try {
      const inc = await j<Incident>(
        `/api/incidents/${incident.id}/approvals/${pending.approval_id}`,
        {
          method: 'POST',
          body: JSON.stringify({
            decision,
            decided_by: 'ops_planner',
            note: decision === 'approved' ? 'Proceed with recovery wave' : 'Hold — escalate',
          }),
        },
      )
      setIncident(inc)
      void loadTwin(inc.id)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }

  const selectedScenario = scenarios.find((s) => s.id === scenarioId)

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">RLY</div>
          <div className="brand-text">
            <h1>RELAY</h1>
            <span>Tuas Hub · Transshipment connection continuity</span>
          </div>
        </div>
        <div className="controls">
          <span className={`health-badge ${apiOk === true ? 'ok' : apiOk === false ? 'down' : ''}`}>
            {apiOk === true ? 'System online' : apiOk === false ? 'Offline' : 'Connecting…'}
          </span>
          <button className="btn primary" disabled={busy || apiOk !== true} onClick={runScenario}>
            {busy ? 'Processing…' : `Run scenario — ${selectedScenario?.title ?? scenarioId}`}
          </button>
        </div>
      </header>

      {apiOk === false && (
        <div className="banner warn">
          Backend not reachable. Start the API:{' '}
          <code className="mono">cd relay/backend && PYTHONPATH=. python3 -m app.main</code>
        </div>
      )}

      <div className="layout">
        <aside className="sidebar">
          <h2 className="section-title">Demo scenarios</h2>
          <div className="scenario-list">
            {scenarios.map((s) => (
              <div
                key={s.id}
                className={`scenario-card ${scenarioId === s.id ? 'active' : ''}`}
                onClick={() => setScenarioId(s.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setScenarioId(s.id)}
              >
                <h3>{s.title}</h3>
                <p>{s.description}</p>
              </div>
            ))}
          </div>

          <h2 className="section-title spaced">PSA context</h2>
          <div className="context-stats">
            {meta?.domain_context?.stats.map((s) => (
              <div key={s.label} className="context-stat">
                <div className="cs-value">{s.value}</div>
                <div className="cs-label">{s.label}</div>
                <div className="cs-src">{s.source}</div>
              </div>
            ))}
          </div>
          <p className="context-note">
            {meta?.domain_context?.alignment ??
              'Connection continuity when schedules break — not a generic port chatbot.'}
          </p>
          <p className="context-note small">
            {meta?.domain_context?.twin_label ?? 'Synthetic demo twin'}
          </p>
        </aside>

        <section className="main-col">
          <div className="kpi-row">
            <div className="kpi">
              <div className="label">At-risk connections</div>
              <div className="value warn">{risk?.count ?? '—'}</div>
            </div>
            <div className="kpi">
              <div className="label">Expected loss (pre-action)</div>
              <div className="value danger">
                {risk ? formatUsd(risk.expected_loss_usd) : '—'}
              </div>
            </div>
            <div className="kpi">
              <div className="label">Connections saved</div>
              <div className="value ok">
                {isClosed ? incident?.result?.connections_saved ?? '—' : '—'}
              </div>
            </div>
            <div className="kpi">
              <div className="label">Agent compute (est.)</div>
              <div className="value muted-kpi">
                {incident?.metrics?.tokens_est_total ??
                  incident?.trace.reduce((a, t) => a + (t.tokens_est || 0), 0) ??
                  '—'}{' '}
                <span style={{ fontSize: '0.7rem' }}>tokens</span>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-head">
              <h2>Active incident</h2>
              {incident && (
                <span className={`status-pill ${incident.status}`}>
                  {formatStatus(incident.status)}
                </span>
              )}
            </div>

            {!incident && (
              <div className="empty-state">
                <p className="empty-title">No active incident</p>
                <p>
                  Select a scenario from the left panel and click Run. RELAY will detect the
                  disruption, score connection buffers, generate recovery plans, run a critique pass,
                  and pause for human approval before dispatching work orders.
                </p>
              </div>
            )}

            {incident && (
              <>
                <div
                  className={`phase-stepper ${isEscalated ? 'escalated' : ''}`}
                  aria-label="Incident phase"
                >
                  {PHASES.map((ph, i) => {
                    const stopped = isEscalated && i > 4
                    const done = !stopped && i <= activePhase
                    const active = i === activePhase && !isEscalated
                    return (
                      <div
                        key={ph}
                        className={`phase ${done ? 'done' : ''} ${active ? 'active' : ''} ${stopped ? 'stopped' : ''}`}
                      >
                        <span className="phase-dot" />
                        <span className="phase-label">{formatStatus(ph)}</span>
                      </div>
                    )
                  })}
                </div>

                <h3 className="incident-title">{incident.title}</h3>
                <p className="incident-objective">{incident.objective}</p>

                {incident.metrics.yard_fallback && (
                  <p className="hint warn-hint">
                    Yard position API degraded — analyst fell back to twin cache for container
                    locations.
                  </p>
                )}

                {pending && (
                  <div className="approval-box">
                    <p>
                      <strong>Approval required.</strong> {pending.rationale}
                    </p>
                    <div className="approval-actions">
                      <button
                        className="btn primary"
                        disabled={busy}
                        onClick={() => decide('approved')}
                      >
                        Approve plan
                      </button>
                      <button className="btn danger" disabled={busy} onClick={() => decide('rejected')}>
                        Reject &amp; escalate
                      </button>
                    </div>
                  </div>
                )}

                {isEscalated && incident.result && (
                  <div className="result-banner escalated">
                    <strong>Escalated to shift superintendent.</strong>{' '}
                    {incident.result.message}
                    {incident.result.note ? ` Note: ${incident.result.note}` : ''}
                  </div>
                )}

                {isClosed && incident.result && (
                  <div className="result-banner success">
                    <strong>Recovery complete.</strong> Saved {incident.result.connections_saved ?? 0}{' '}
                    connections, avoided {formatUsd(incident.result.loss_avoided_usd ?? 0)}
                    {post ? `, ${post.count} residual at-risk` : ''}
                    {incident.result.selected_plan ? ` (${incident.result.selected_plan})` : ''}
                  </div>
                )}

                {isClosed && (incident.result?.work_orders?.length ?? 0) > 0 && (
                  <div className="subsection">
                    <h2 className="section-title">Dispatched work orders</h2>
                    <div className="wo-list">
                      {(incident.result?.work_orders ?? []).map((wo) => (
                        <div key={wo.id} className="wo-item">
                          <span className="mono">{wo.id}</span>
                          <span>{wo.type.replace(/_/g, ' ')}</span>
                          <span className={`wo-status ${wo.status}`}>{wo.status}</span>
                          <span className="mono muted">{wo.container_ids.length} cntrs</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="subsection">
                  <h2 className="section-title">At-risk containers</h2>
                  <div className="table-wrap">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Container</th>
                          <th>Connection</th>
                          <th>Risk</th>
                          <th>Buffer (h)</th>
                          <th>Exp. loss</th>
                        </tr>
                      </thead>
                      <tbody>
                        {atRiskVisible.map((r) => (
                          <tr key={r.container_id}>
                            <td className="mono">
                              {r.container_id}
                              {r.reefer ? ' · RF' : ''}
                              {r.dg ? ' · DG' : ''}
                            </td>
                            <td className="mono">
                              {r.from_vessel} → {r.to_vessel}
                            </td>
                            <td>{r.risk.toFixed(2)}</td>
                            <td className={r.slack_hours <= 0 ? 'danger-text' : ''}>
                              {r.slack_hours}
                            </td>
                            <td>{formatUsd(r.expected_miss_cost_usd)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {atRiskHidden > 0 && (
                    <button className="btn linkish" onClick={() => setShowAllAtRisk(true)}>
                      Show {atRiskHidden} more containers
                    </button>
                  )}
                </div>

                <div className="subsection">
                  <h2 className="section-title">Recovery plan comparison</h2>
                  <div className="plans">
                    {incident.plans.map((p) => (
                      <div
                        key={p.plan_id}
                        className={`plan ${p.selected ? 'selected' : ''} ${p.plan_id === 'PLAN-X' ? 'killed' : ''}`}
                      >
                        <h3>
                          {p.plan_id} — {p.title}
                          {p.selected && <span className="plan-badge">Selected</span>}
                        </h3>
                        <div className="meta">
                          Score {p.score.toFixed(1)} · {p.connections_saved} saved ·{' '}
                          {formatUsd(p.estimated_cost_usd)} · residual risk {p.residual_risk}
                        </div>
                        <div className="summary">{p.summary}</div>
                        {p.critic_notes.length > 0 && (
                          <ul>
                            {p.critic_notes.map((n, i) => (
                              <li key={i}>{n}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {twin && (
                  <div className="subsection">
                    <h2 className="section-title">Terminal twin — {twin.name}</h2>
                    <div className="twin-grid">
                      <div className="twin-card">
                        <h4>Vessels</h4>
                        {twin.vessels.slice(0, 4).map((v) => (
                          <div key={v.id} className="twin-row">
                            <span className="mono">{v.id}</span>
                            <span>{v.role}</span>
                            <span className="mono muted">ETA {v.eta.slice(11, 16)}</span>
                          </div>
                        ))}
                      </div>
                      <div className="twin-card">
                        <h4>Cranes</h4>
                        {twin.cranes.map((c) => (
                          <div key={c.id} className="twin-row">
                            <span className="mono">{c.id}</span>
                            <span className={`crane-status ${c.status}`}>{c.status}</span>
                            <span className="muted">{c.workface}</span>
                          </div>
                        ))}
                      </div>
                      <div className="twin-card">
                        <h4>System flags</h4>
                        {Object.keys(twin.flags).length === 0 ? (
                          <span className="muted">No active flags</span>
                        ) : (
                          Object.entries(twin.flags).map(([k, v]) => (
                            <div key={k} className="twin-row">
                              <span className="mono">{k}</span>
                              <span>{String(v)}</span>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            {error && <p className="error-text">{error}</p>}
          </div>
        </section>

        <aside className="trace-panel">
          <h2 className="section-title">Execution trace</h2>
          <p className="trace-sub">
            {incident && visibleTrace < incident.trace.length
              ? `Loading events (${visibleTrace} of ${incident.trace.length})…`
              : 'Agent decisions, tool calls, approvals, and errors'}
          </p>
          <div className="trace" ref={traceRef}>
            {!incident && (
              <div className="empty-state">
                <p>Trace log will appear here after running a scenario.</p>
              </div>
            )}
            {incident?.trace.slice(0, visibleTrace).map((t, idx) => (
              <div key={`${t.ts}-${t.agent}-${idx}`} className={`trace-item ${t.kind} reveal`}>
                <div className="who">
                  <span className="ts">{formatTime(t.ts)}</span>
                  {t.agent}
                  <span className="kind"> · {t.kind}</span>
                </div>
                <div className="sum">{t.summary}</div>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  )
}
