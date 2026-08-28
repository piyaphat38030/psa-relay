# PSA Code Sprint 2.0 — Challenge Brief (Verified)

Sources: [psacodesprint.com](https://www.psacodesprint.com/), [Agentic AI in Action](https://www.psacodesprint.com/agentic-ai-in-action), Kickoff Briefing PDF (14 Aug 2026).

## What this competition actually is

**Not** a fixed problem-statement hackathon.  
**Is** an open-ended challenge: teams **identify a PSA-relevant problem** and **build an agentic AI solution** that can reason, decide, and coordinate actions toward a defined objective.

Solutions may be **advisory**, **human-in-the-loop**, or **autonomous**.  
**Higher autonomy is not automatically better.** Choose level by use case, operational risk, and available controls.

## Required agent behaviours (must demonstrate)

Solution should process inputs such as: event log, state change, operational alert, process metric, or user request — and show it can:

1. Analyse input and identify objective or issue  
2. Determine an appropriate course of action  
3. Orchestrate relevant tools, systems or workflows  
4. Handle uncertainty, incomplete information and tool failures  
5. Invoke human review, approval or escalation where appropriate  
6. Produce a clear execution trace (decisions, tool calls, approvals, actions, results, errors)

## Deliverables (submission by **30 AUG 2026, 23:59 SGT**)

1. Demonstration video ≤ **10 minutes**  
2. Presentation slides ≤ **10 slides** (**appendix allowed** — Telegram clarifications)  
3. Explanation of: architecture, execution flow, key decisions, potential impact, security / safety / scalability  

**Upload:** Link is in your **registration confirmation email** (no public URL on the website). See `deliverables/SUBMISSION_GUIDE.md`.

### Telegram clarifications (applied)

| Topic | Ruling |
|-------|--------|
| Datasets / LLM keys / credits | **Not provided** by PSA. Public data, open models, or **synthetic/sample** data OK; **state assumptions**. |
| Slide limit | **10 main**; appendix OK for architecture, stack, references, **links**. |
| Deck contents | Problem + PSA relevance; agentic AI usage; features/workflow; architecture; **data sources/assumptions**; benefits. |
| Demo video | Screen recording + voice-over OK; **camera not required**. |
| Links in PDF/deck | **Allowed** (GitHub, live demo, etc.). |
| Criteria weights | Details in kickoff briefing to team leaders — **not** confirmed equal on Telegram. |

See `research/10_telegram_clarifications.md`.

## Evaluation criteria

| Criterion | What judges look for |
|-----------|----------------------|
| **Agentic AI Design & Technical Execution** | Reasoning, decision-making, tool orchestration, state management, human oversight; **reliable end-to-end workflow**. Focus on **team-designed** decomposition/workflow/integrations — not generic platform capabilities. |
| **Innovation & Originality** | Creative, unique application of agentic AI; highly differentiated value in the domain. |
| **Scalability, Security & Responsible AI** | Scale to larger volumes; runtime/token efficiency; access controls; safety guardrails; error handling; **auditability**. |
| **Presentation & Clarity** | Clear problem, architecture, flow, decisions, business impact. |

**Weighting:** Treat all four as must-win until/unless briefing deck confirms otherwise.

## Timeline

| Date | Milestone |
|------|-----------|
| Until 30 Aug | Registration |
| 14 Aug | Kickoff / Briefing (PSA Alongside) + Innovation Centre Tour (PSA Horizons) |
| **30 Aug 2026, 23:59 SGT** | **Submission of solution** (via confirmation email link) |
| 4 Sep | Shortlisted teams announced |
| Sep–Oct | Sprinternship with PSA Biz & Tech mentors |
| 23 Oct | Finals (PSA Horizons) |

## Prizes

1st S$7,000 · 2nd S$4,000 · 3rd S$3,000 · 4th S$2,000 · 5th–8th S$500  
+ potential internship / full-time pathways.

## Eligibility

Full-time students at Singapore local secondary or tertiary institutions. Solo or team ≤ 4.

## Winning implications for design

- Must be **agentic**, not “chat UI over an LLM”.  
- Must show **tools + state + HITL + traces**.  
- Must be **PSA-domain deep** (ports / logistics / supply chain).  
- Must **justify autonomy level**.  
- Must look **production-credible**: guardrails, failures, audit, token efficiency.  
- Presentation must be executive-grade and tied to measurable ops impact.
