/**
 * RELAY — McKinsey / executive-style deck
 * Conventions from public MBB guides (Deckary, Slideworks, SlideUplift)
 * + FAANG exec deck practice (takeaway headlines, ≤4 colors, metric exhibits)
 *
 * Storyline: SCR (Situation → Complication → Resolution) with answer-first exec summary.
 */
const pptxgen = require('pptxgenjs');
const path = require('path');

const pres = new pptxgen();
pres.defineLayout({ name: 'LAYOUT_16x9', width: 10, height: 5.625 });
pres.layout = 'LAYOUT_16x9';
pres.author = 'RELAY Team';
pres.title = 'RELAY — PSA Code Sprint 2.0';
pres.subject = 'Agentic transshipment connection continuity';

// McKinsey-like palette (public convention — not an official firm template)
const C = {
  navy: '051C2C',
  blue: '0070AD',
  blueSoft: 'E6F3FA',
  ink: '333333',
  muted: '666666',
  line: 'D9D9D9',
  gray: 'F2F2F2',
  white: 'FFFFFF',
  green: '0D7A4F',
  red: 'C00000',
};

const M = { L: 0.5, R: 0.5, T: 0.28 }; // margins
const W = 10 - M.L - M.R; // content width

function addFooter(slide, page, source) {
  slide.addText(source, {
    x: M.L, y: 5.28, w: 7.2, h: 0.22,
    fontSize: 8, fontFace: 'Calibri', color: C.muted, margin: 0,
  });
  slide.addText(`${page}`, {
    x: 9.2, y: 5.28, w: 0.5, h: 0.22,
    fontSize: 9, fontFace: 'Calibri', color: C.muted, align: 'right', margin: 0,
  });
}

function actionTitle(slide, text) {
  slide.addText(text, {
    x: M.L, y: M.T, w: W, h: 0.72,
    fontSize: 18, fontFace: 'Arial', bold: true, color: C.ink, margin: 0, valign: 'top',
  });
}

function lightBg(slide) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.white },
  });
}

function darkBg(slide) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.navy },
  });
}

function card(slide, x, y, w, h) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h, fill: { color: C.gray },
  });
}

// ─────────────────────────────────────────────
// 1. Title
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText('PSA Code Sprint 2.0  ·  Agentic AI in Action', {
    x: M.L, y: 1.55, w: W, h: 0.3,
    fontSize: 12, fontFace: 'Calibri', color: '8FB8D4', margin: 0,
  });
  s.addText('RELAY', {
    x: M.L, y: 1.95, w: W, h: 0.55,
    fontSize: 40, fontFace: 'Arial', bold: true, color: C.white, margin: 0,
  });
  s.addText('When feeder ETAs slip or cranes go down, RELAY finds at-risk transshipment\nconnections and plans recovery — with a planner in the loop before anything moves in the yard', {
    x: M.L, y: 2.6, w: 8.5, h: 0.7,
    fontSize: 16, fontFace: 'Calibri', color: 'D6E4EE', margin: 0,
  });
  s.addText('Submission deliverable  ·  Confidential', {
    x: M.L, y: 4.85, w: W, h: 0.25,
    fontSize: 11, fontFace: 'Calibri', color: '8FB8D4', margin: 0,
  });
}

// ─────────────────────────────────────────────
// 2. Executive summary (answer first)
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightBg(s);
  actionTitle(s, 'RELAY scores connection risk, runs recovery options, and waits for approval before yard moves');
  s.addText('Three things to know upfront', {
    x: M.L, y: 1.05, w: W, h: 0.28,
    fontSize: 12, fontFace: 'Calibri', color: C.blue, margin: 0,
  });

  const cols = [
    {
      n: '01',
      h: 'The problem is missed connections',
      b: 'At a transshipment hub, schedule slips push boxes past their outbound cutoff. Premium, reefer, and DG cargo tend to hurt first.',
    },
    {
      n: '02',
      h: 'Agents do the thinking; humans approve the moves',
      b: 'Six agents sense, score, plan, and critique. Restow orders and cutoff changes need an explicit planner sign-off.',
    },
    {
      n: '03',
      h: 'Working demo, not a slide deck idea',
      b: 'End-to-end console with three scenarios, tool traces, critic dissent, and fallback when APIs fail.',
    },
  ];
  cols.forEach((c, i) => {
    const x = M.L + i * 3.1;
    card(s, x, 1.5, 2.95, 3.2);
    s.addText(c.n, {
      x: x + 0.2, y: 1.7, w: 2.55, h: 0.35,
      fontSize: 20, fontFace: 'Arial', bold: true, color: C.blue, margin: 0,
    });
    s.addText(c.h, {
      x: x + 0.2, y: 2.2, w: 2.55, h: 0.7,
      fontSize: 14, fontFace: 'Arial', bold: true, color: C.ink, margin: 0,
    });
    s.addText(c.b, {
      x: x + 0.2, y: 3.0, w: 2.55, h: 1.45,
      fontSize: 12, fontFace: 'Calibri', color: C.ink, margin: 0,
    });
  });
  addFooter(s, '2', 'Source: PSA Code Sprint 2.0 brief (Agentic AI in Action); team analysis');
}

// ─────────────────────────────────────────────
// 3. Situation
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightBg(s);
  actionTitle(s, 'Most PSA throughput is transshipment — and schedules are rarely on time');

  // Verified PSA context exhibit
  card(s, M.L, 1.15, W, 0.85);
  s.addText('Singapore hub context (public sources — not live PSA data)', {
    x: M.L + 0.2, y: 1.28, w: W - 0.4, h: 0.25,
    fontSize: 10, fontFace: 'Calibri', bold: true, color: C.blue, margin: 0,
  });
  s.addText('~90% throughput is transshipment (MPA 2024)   ·   ~90% vessels off-schedule in 1H 2024 (PSA)   ·   +8% container rehandling (PSA 1H 2024)', {
    x: M.L + 0.2, y: 1.55, w: W - 0.4, h: 0.35,
    fontSize: 11, fontFace: 'Calibri', color: C.ink, margin: 0,
  });

  const rows = [
    ['Trigger', 'Feeder ETA revision, quay crane downtime, AIS/yard data gaps'],
    ['Exposure', 'Connection buffer → 0: premium, reefer, and DG boxes first'],
    ['Consequence', 'Missed links → dwell, rehandle wave, network SLA damage'],
    ['Why PSA', 'The hub wins on connection reliability when things go wrong, not just berth capacity'],
  ];
  rows.forEach((r, i) => {
    const y = 2.15 + i * 0.72;
    s.addShape(pres.shapes.RECTANGLE, {
      x: M.L, y, w: 1.9, h: 0.58, fill: { color: i % 2 === 0 ? C.navy : C.blue },
    });
    s.addText(r[0], {
      x: M.L, y: y + 0.14, w: 1.9, h: 0.35,
      fontSize: 12, fontFace: 'Arial', bold: true, color: C.white, align: 'center', margin: 0,
    });
    card(s, M.L + 1.9, y, W - 1.9, 0.58);
    s.addText(r[1], {
      x: M.L + 2.15, y: y + 0.14, w: W - 2.4, h: 0.35,
      fontSize: 12, fontFace: 'Calibri', color: C.ink, margin: 0,
    });
  });
  addFooter(s, '3', 'Source: MPA 2024; Maritime Executive Jul 2024 (PSA); team synthetic twin for quantification');
}

// ─────────────────────────────────────────────
// 4. Complication + autonomy choice
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightBg(s);
  actionTitle(s, 'Planners stitch this together manually today — full autonomy would be worse');

  // Two columns: today vs wrong answer vs right answer
  card(s, M.L, 1.2, 2.95, 3.4);
  s.addText('Today', {
    x: M.L + 0.2, y: 1.4, w: 2.55, h: 0.35,
    fontSize: 14, fontFace: 'Arial', bold: true, color: C.blue, margin: 0,
  });
  s.addText([
    { text: 'Signals live in different systems', options: { breakLine: true } },
    { text: 'Planners swivel-chair under time pressure', options: { breakLine: true } },
    { text: 'Thin audit trail on who decided what', options: { breakLine: true } },
    { text: 'Slow time-to-coordinated action', options: { breakLine: false } },
  ], {
    x: M.L + 0.2, y: 1.9, w: 2.55, h: 2.4,
    fontSize: 13, fontFace: 'Calibri', color: C.ink, bullet: true, paraSpaceAfter: 8, margin: 0,
  });

  card(s, M.L + 3.1, 1.2, 2.95, 3.4);
  s.addText('What we avoided', {
    x: M.L + 3.3, y: 1.4, w: 2.55, h: 0.35,
    fontSize: 14, fontFace: 'Arial', bold: true, color: C.red, margin: 0,
  });
  s.addText([
    { text: 'Autonomy for its own sake', options: { breakLine: true } },
    { text: 'A chatbot with no tool or approval gates', options: { breakLine: true } },
    { text: 'Silent yard moves on stale data', options: { breakLine: true } },
    { text: 'Multi-agent demo with no domain logic behind it', options: { breakLine: false } },
  ], {
    x: M.L + 3.3, y: 1.9, w: 2.55, h: 2.4,
    fontSize: 13, fontFace: 'Calibri', color: C.ink, bullet: true, paraSpaceAfter: 8, margin: 0,
  });

  card(s, M.L + 6.2, 1.2, 2.95, 3.4);
  s.addText('What we built', {
    x: M.L + 6.4, y: 1.4, w: 2.55, h: 0.35,
    fontSize: 14, fontFace: 'Arial', bold: true, color: C.green, margin: 0,
  });
  s.addText([
    { text: 'Autonomous: sense, score, plan, notify', options: { breakLine: true } },
    { text: 'HITL: restow, cutoff, hold, DG/reefer', options: { breakLine: true } },
    { text: 'Escalate: reject path + superintendent', options: { breakLine: true } },
    { text: 'Matches brief: higher autonomy ≠ better', options: { breakLine: false } },
  ], {
    x: M.L + 6.4, y: 1.9, w: 2.55, h: 2.4,
    fontSize: 13, fontFace: 'Calibri', color: C.ink, bullet: true, paraSpaceAfter: 8, margin: 0,
  });
  addFooter(s, '4', 'Source: PSA Code Sprint kickoff — “Higher autonomy is not automatically better”');
}

// ─────────────────────────────────────────────
// 5. Resolution — how RELAY works
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightBg(s);
  actionTitle(s, 'Six agents, one incident loop — scoring is deterministic, moves need approval');

  const steps = [
    ['1', 'Sense', 'Sentinel'],
    ['2', 'Score', 'Analyst'],
    ['3', 'Plan', 'Planner'],
    ['4', 'Critique', 'Critic'],
    ['5', 'Approve', 'Human'],
    ['6', 'Act', 'Executor'],
  ];
  steps.forEach((st, i) => {
    const x = M.L + i * 1.52;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.25, w: 1.4, h: 1.35, fill: { color: i === 4 ? C.blue : C.navy },
    });
    s.addText(st[0], {
      x, y: 1.4, w: 1.4, h: 0.3,
      fontSize: 16, fontFace: 'Arial', bold: true, color: C.white, align: 'center', margin: 0,
    });
    s.addText(st[1], {
      x, y: 1.75, w: 1.4, h: 0.3,
      fontSize: 13, fontFace: 'Arial', bold: true, color: C.white, align: 'center', margin: 0,
    });
    s.addText(st[2], {
      x, y: 2.15, w: 1.4, h: 0.25,
      fontSize: 11, fontFace: 'Calibri', color: 'B8D4E8', align: 'center', margin: 0,
    });
  });

  const proofs = [
    { h: 'Inputs handled', b: 'Operational alert, state change, degraded process metric' },
    { h: 'Tools orchestrated', b: 'Schedule, ETA, connections, yard, crane, simulate, work order, notify, AIS' },
    { h: 'Trace produced', b: 'Decisions, tool calls/errors, approvals, actions, metrics — append-only' },
  ];
  proofs.forEach((p, i) => {
    const x = M.L + i * 3.1;
    card(s, x, 2.95, 2.95, 1.7);
    s.addText(p.h, {
      x: x + 0.18, y: 3.15, w: 2.6, h: 0.3,
      fontSize: 13, fontFace: 'Arial', bold: true, color: C.blue, margin: 0,
    });
    s.addText(p.b, {
      x: x + 0.18, y: 3.55, w: 2.6, h: 0.85,
      fontSize: 12, fontFace: 'Calibri', color: C.ink, margin: 0,
    });
  });
  addFooter(s, '5', 'Source: RELAY runtime — custom state machine (not a thin framework wrapper)');
}

// ─────────────────────────────────────────────
// 6. Architecture exhibit
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightBg(s);
  actionTitle(s, 'We split the maths (risk engine) from the workflow (orchestrator + agents)');

  const layers = [
    { t: 'Ops console', d: 'KPIs, at-risk table, plan compare, approval queue, live execution trace' },
    { t: 'Orchestrator', d: 'State machine: detected → analysing → planning → critique → awaiting approval → executing → closed' },
    { t: 'Domain engine', d: 'Deterministic connection risk + what-if simulator + policy gates (allowlist, approval tokens)' },
    { t: 'Twin / tools', d: 'Synthetic Tuas-style APIs we wrote — PSA provided no dataset this round. Same tool shapes we would wire to PORTNET/CITOS in a sprinternship' },
  ];
  layers.forEach((L, i) => {
    const y = 1.15 + i * 0.9;
    s.addShape(pres.shapes.RECTANGLE, {
      x: M.L, y, w: 2.3, h: 0.75, fill: { color: C.navy },
    });
    s.addText(L.t, {
      x: M.L + 0.15, y: y + 0.22, w: 2.0, h: 0.35,
      fontSize: 13, fontFace: 'Arial', bold: true, color: C.white, margin: 0,
    });
    card(s, M.L + 2.3, y, W - 2.3, 0.75);
    s.addText(L.d, {
      x: M.L + 2.5, y: y + 0.15, w: W - 2.7, h: 0.5,
      fontSize: 12, fontFace: 'Calibri', color: C.ink, margin: 0,
    });
  });
  addFooter(s, '6', 'Source: ARCHITECTURE.md · Data assumptions in Appendix A · team-designed workflow');
}

// ─────────────────────────────────────────────
// 7. Impact / proof (exhibit table — consulting-style)
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightBg(s);
  actionTitle(s, 'Demo results on our synthetic twin — one approval cycle per scenario');

  // Column headers
  const headers = ['Scenario', 'At-risk', 'Pre loss (USD)', 'Plan', 'Saved', 'Loss avoided'];
  const widths = [2.2, 0.9, 1.5, 1.3, 0.9, 1.4];
  let x = M.L;
  headers.forEach((h, i) => {
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.2, w: widths[i], h: 0.4, fill: { color: C.navy },
    });
    s.addText(h, {
      x, y: 1.28, w: widths[i], h: 0.28,
      fontSize: 10, fontFace: 'Arial', bold: true, color: C.white, align: 'center', margin: 0,
    });
    x += widths[i];
  });

  const rows = [
    ['Late feeder', '7', '10,209', 'PLAN-B', '7', '10,209'],
    ['Crane outage', '7', '6,563', 'PLAN-A', '7', '6,563'],
    ['Uncertainty + API fail', '12', '22,563', 'PLAN-B', '5', '13,111'],
  ];
  rows.forEach((r, ri) => {
    let xx = M.L;
    const y = 1.6 + ri * 0.48;
    r.forEach((cell, ci) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: xx, y, w: widths[ci], h: 0.48,
        fill: { color: ri % 2 === 0 ? C.gray : C.white },
      });
      s.addText(cell, {
        x: xx, y: y + 0.1, w: widths[ci], h: 0.28,
        fontSize: 11, fontFace: 'Calibri', bold: ci === 0 || ci === 5,
        color: ci === 5 ? C.green : C.ink, align: ci === 0 ? 'left' : 'center', margin: 0,
      });
      xx += widths[ci];
    });
  });

  card(s, M.L, 3.3, W, 1.5);
  s.addText('Note', {
    x: M.L + 0.25, y: 3.5, w: 1.2, h: 0.3,
    fontSize: 13, fontFace: 'Arial', bold: true, color: C.blue, margin: 0,
  });
  s.addText('Critic rejects PLAN-X in the crane scenario (capacity does not exist). The uncertainty run saves 5 of 12 on purpose — we show partial recovery when data is bad, not a perfect score.', {
    x: M.L + 1.5, y: 3.5, w: W - 1.9, h: 1.05,
    fontSize: 13, fontFace: 'Calibri', color: C.ink, margin: 0,
  });
  addFooter(s, '7', 'Source: RELAY synthetic twin runs (2026-08-23); illustrative — not live PORTNET data');
}

// ─────────────────────────────────────────────
// 8. Responsible AI / failure
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightBg(s);
  actionTitle(s, 'When tools fail or data is stale, RELAY retries, falls back, or escalates');

  const grid = [
    ['Retry', 'Retryable tool errors re-attempt with backoff; every attempt is traced'],
    ['Fallback', 'Yard API 503 → last-known twin cache; reefers flagged verify-before-dispatch'],
    ['Widen bands', 'Degraded AIS increases ETA uncertainty before scoring'],
    ['Escalate', 'Planner rejection notifies shift superintendent with dossier'],
    ['Allowlist', 'No free-form shell/SQL — only registered tools'],
    ['Tokens', 'Dispatch of high-impact work orders requires approval_token'],
  ];
  grid.forEach((g, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = M.L + col * 3.1;
    const y = 1.2 + row * 1.75;
    card(s, x, y, 2.95, 1.55);
    s.addText(g[0], {
      x: x + 0.18, y: y + 0.2, w: 2.6, h: 0.3,
      fontSize: 14, fontFace: 'Arial', bold: true, color: C.blue, margin: 0,
    });
    s.addText(g[1], {
      x: x + 0.18, y: y + 0.6, w: 2.6, h: 0.75,
      fontSize: 12, fontFace: 'Calibri', color: C.ink, margin: 0,
    });
  });
  addFooter(s, '8', 'Source: Brief criteria — Scalability, Security and Responsible AI');
}

// ─────────────────────────────────────────────
// 9. Path forward
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  lightBg(s);
  actionTitle(s, 'Next step: shadow mode with PSA mentors, then real terminal APIs');

  // Timeline style
  const phases = [
    { p: 'Now', t: 'Demo twin', d: 'Working console + 3 scenarios + audited traces for shortlisting' },
    { p: 'Sep–Oct', t: 'Sprinternship', d: 'Shadow-mode with PSA mentors; tune risk weights with planners' },
    { p: 'Next', t: 'Integrate', d: 'PORTNET / CITOS-class APIs, SSO/RBAC, production audit sink' },
  ];
  phases.forEach((ph, i) => {
    const x = M.L + i * 3.1;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.3, w: 2.95, h: 0.45, fill: { color: C.navy },
    });
    s.addText(ph.p, {
      x, y: 1.38, w: 2.95, h: 0.3,
      fontSize: 13, fontFace: 'Arial', bold: true, color: C.white, align: 'center', margin: 0,
    });
    card(s, x, 1.75, 2.95, 2.7);
    s.addText(ph.t, {
      x: x + 0.2, y: 2.05, w: 2.55, h: 0.4,
      fontSize: 16, fontFace: 'Arial', bold: true, color: C.ink, margin: 0,
    });
    s.addText(ph.d, {
      x: x + 0.2, y: 2.6, w: 2.55, h: 1.5,
      fontSize: 13, fontFace: 'Calibri', color: C.ink, margin: 0,
    });
  });
  addFooter(s, '9', 'Source: Competition timeline (shortlist 4 Sep; Sprinternship Sep–Oct; Finals 23 Oct)');
}

// ─────────────────────────────────────────────
// 10. Close — criteria map
// ─────────────────────────────────────────────
{
  const s = pres.addSlide();
  darkBg(s);
  s.addText('RELAY — connection recovery with human gates and a full audit trail', {
    x: M.L, y: 0.55, w: W, h: 0.7,
    fontSize: 18, fontFace: 'Arial', bold: true, color: C.white, margin: 0,
  });

  const map = [
    ['Agentic design & execution', 'E2E state machine, tools, HITL, traces'],
    ['Innovation & originality', 'T/S-first problem + dissent critic + hybrid engine'],
    ['Scalability & responsible AI', 'Allowlist, gates, fallback, token accounting'],
    ['Presentation & clarity', 'Ops console + this deck + architecture brief'],
  ];
  map.forEach((m, i) => {
    const y = 1.5 + i * 0.7;
    s.addText(m[0], {
      x: M.L, y, w: 4.2, h: 0.45,
      fontSize: 14, fontFace: 'Arial', bold: true, color: '8FB8D4', margin: 0,
    });
    s.addText(m[1], {
      x: 4.8, y, w: 4.7, h: 0.45,
      fontSize: 14, fontFace: 'Calibri', color: C.white, margin: 0,
    });
  });
  s.addText('Questions — or re-run late feeder / crane outage live in the ops console.', {
    x: M.L, y: 4.7, w: W, h: 0.3,
    fontSize: 13, fontFace: 'Calibri', color: '8FB8D4', margin: 0,
  });
}

// ═════════════════════════════════════════════
// APPENDIX (allowed — main deck remains 10)
// Telegram clarification 2026-08: “excluding appendix”
// ═════════════════════════════════════════════

function appendixBanner(slide, label) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.22, fill: { color: C.blue },
  });
  slide.addText(label, {
    x: M.L, y: 0.02, w: W, h: 0.18,
    fontSize: 9, fontFace: 'Calibri', bold: true, color: C.white, margin: 0,
  });
}

// A1 — Data sources & assumptions (explicitly required by clarifications)
{
  const s = pres.addSlide();
  lightBg(s);
  appendixBanner(s, 'APPENDIX A  ·  Data sources & assumptions');
  actionTitle(s, 'We built a synthetic terminal twin — PSA did not provide data or LLM access');

  const blocks = [
    {
      h: 'What we built',
      b: 'Team-authored sample data: vessels, ETAs, yard blocks, crane states, T/S boxes, miss-cost model. Deterministic risk + simulate engines — no external LLM required at runtime.',
    },
    {
      h: 'Public context only',
      b: 'MPA / PSA public figures (~90% T/S; ~90% off-schedule 1H24; +8% rehandling) frame the problem. They are not live operational feeds.',
    },
    {
      h: 'Assumptions (stated)',
      b: 'Connection buffer = mother ETA − feeder ETA − handling − safety margin. Miss cost illustrative. Approval tokens required for restow / cutoff / hold. Tool failures are injected on purpose in scenario 3.',
    },
    {
      h: 'Integration path',
      b: 'Same tool contracts intended for PORTNET® / CITOS-class APIs in Sprinternship. Twin is a stand-in, not a claim of production data access.',
    },
  ];
  blocks.forEach((b, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = M.L + col * 4.65;
    const y = 1.15 + row * 1.85;
    card(s, x, y, 4.45, 1.7);
    s.addText(b.h, {
      x: x + 0.2, y: y + 0.2, w: 4.05, h: 0.3,
      fontSize: 13, fontFace: 'Arial', bold: true, color: C.blue, margin: 0,
    });
    s.addText(b.b, {
      x: x + 0.2, y: y + 0.55, w: 4.05, h: 1.0,
      fontSize: 12, fontFace: 'Calibri', color: C.ink, margin: 0,
    });
  });
  addFooter(s, 'A1', 'Source: PSA Code Sprint Telegram clarifications — synthetic/sample data allowed; assumptions must be stated');
}

// A2 — Tech stack
{
  const s = pres.addSlide();
  lightBg(s);
  appendixBanner(s, 'APPENDIX B  ·  Technical stack');
  actionTitle(s, 'Stack: Python stdlib backend, React console, no paid API keys to run the demo');

  const stack = [
    ['Layer', 'Choice', 'Why'],
    ['Orchestrator', 'Python 3 stdlib HTTP + dataclasses', 'No FastAPI/pydantic; runs without pip; portable demo'],
    ['Domain engine', 'Deterministic risk + simulate', 'Auditable; LLM optional for narration only'],
    ['Tools', 'Allowlisted mock APIs', 'Retries, fallback cache, failure injection'],
    ['Ops console', 'React + Vite + TypeScript', 'Approval UX, phase stepper, live trace'],
    ['Tests', 'unittest / pytest-compatible', 'Plan≈result alignment; scenario regression'],
  ];
  stack.forEach((r, ri) => {
    let xx = M.L;
    const widths = [2.0, 3.6, 3.4];
    const y = 1.15 + ri * 0.55;
    r.forEach((cell, ci) => {
      s.addShape(pres.shapes.RECTANGLE, {
        x: xx, y, w: widths[ci], h: 0.55,
        fill: { color: ri === 0 ? C.navy : ri % 2 === 0 ? C.gray : C.white },
      });
      s.addText(cell, {
        x: xx + 0.1, y: y + 0.14, w: widths[ci] - 0.2, h: 0.3,
        fontSize: 11, fontFace: ri === 0 ? 'Arial' : 'Calibri',
        bold: ri === 0 || ci === 0, color: ri === 0 ? C.white : C.ink, margin: 0,
      });
      xx += widths[ci];
    });
  });
  addFooter(s, 'A2', 'Source: relay/README.md · No PSA LLM credits / API keys required');
}

// A3 — Agent responsibilities
{
  const s = pres.addSlide();
  lightBg(s);
  appendixBanner(s, 'APPENDIX C  ·  Agent roles & workflow');
  actionTitle(s, 'One job per agent — Critic can say no; Executor cannot skip approval');

  const agents = [
    ['Sentinel', 'Ingest trigger; open incident; snapshot twin state'],
    ['Analyst', 'Call schedule/ETA/connections; score connection buffer risk'],
    ['Planner', 'Generate PLAN-A/B/C(+X); simulate saved boxes & cost'],
    ['Critic', 'Kill infeasible plans (e.g. PLAN-X); surface residual risk'],
    ['Human', 'Approve / reject high-impact actions (restow, cutoff, hold)'],
    ['Executor', 'Dispatch allowlisted tools only with approval_token'],
    ['Auditor', 'Append-only trace: decisions, tools, errors, metrics'],
  ];
  agents.forEach((a, i) => {
    const y = 1.1 + i * 0.52;
    s.addShape(pres.shapes.RECTANGLE, {
      x: M.L, y, w: 1.9, h: 0.45, fill: { color: i === 4 ? C.blue : C.navy },
    });
    s.addText(a[0], {
      x: M.L, y: y + 0.1, w: 1.9, h: 0.28,
      fontSize: 12, fontFace: 'Arial', bold: true, color: C.white, align: 'center', margin: 0,
    });
    card(s, M.L + 1.9, y, W - 1.9, 0.45);
    s.addText(a[1], {
      x: M.L + 2.1, y: y + 0.1, w: W - 2.3, h: 0.28,
      fontSize: 12, fontFace: 'Calibri', color: C.ink, margin: 0,
    });
  });
  addFooter(s, 'A3', 'Source: relay/backend/app/agents/orchestrator.py');
}

// A4 — Links & references
{
  const s = pres.addSlide();
  lightBg(s);
  appendixBanner(s, 'APPENDIX D  ·  Links & references (hyperlinks allowed per organisers)');
  actionTitle(s, 'Submission files and links — update repo URL before upload');

  const links = [
    {
      label: 'Solution repo',
      text: 'GitHub / Cursor repo — paste public URL before submit',
      url: 'https://github.com/',
    },
    {
      label: 'Architecture brief',
      text: 'ARCHITECTURE.pdf — upload with submission (flow, decisions, impact, security)',
      url: null,
    },
    {
      label: 'Local demo',
      text: 'API :8000 · Console :5173 — see relay/README.md quick start',
      url: null,
    },
    {
      label: 'Submit by',
      text: '30 Aug 2026, 23:59 SGT — upload link in registration confirmation email',
      url: null,
    },
  ];
  links.forEach((L, i) => {
    const y = 1.2 + i * 0.7;
    s.addShape(pres.shapes.RECTANGLE, {
      x: M.L, y, w: 2.2, h: 0.55, fill: { color: C.navy },
    });
    s.addText(L.label, {
      x: M.L + 0.1, y: y + 0.14, w: 2.0, h: 0.3,
      fontSize: 12, fontFace: 'Arial', bold: true, color: C.white, margin: 0,
    });
    card(s, M.L + 2.2, y, W - 2.2, 0.55);
    const opts = {
      x: M.L + 2.4, y: y + 0.14, w: W - 2.6, h: 0.3,
      fontSize: 12, fontFace: 'Calibri', color: L.url ? C.blue : C.ink, margin: 0,
    };
    if (L.url) opts.hyperlink = { url: L.url, tooltip: L.url };
    s.addText(L.text, opts);
  });

  s.addText('Public refs: MPA Maritime Singapore 2024 · Maritime Executive (PSA 1H 2024 ops) · Kickoff briefing 14 Aug · Telegram submission clarifications', {
    x: M.L, y: 4.2, w: W, h: 0.55,
    fontSize: 11, fontFace: 'Calibri', color: C.muted, margin: 0,
  });
  addFooter(s, 'A4', 'Source: Organiser reminder 27 Aug — submit via confirmation email before 30 Aug 23:59 SGT');
}

const out = path.join(__dirname, 'RELAY_Presentation.pptx');
pres.writeFile({ fileName: out }).then(() => {
  console.log('Wrote', out);
}).catch((e) => {
  console.error(e);
  process.exit(1);
});
