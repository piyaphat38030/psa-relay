# Speaker script — RELAY

**How to use this:** This is a full talk track with context and technical detail woven in. Read it a couple of times, then present in your own words — you don't need to memorise every line. Pause when you switch to the console. If the demo hiccups, say something like "let me walk through the trace from our rehearsal run" and keep going.

---

## Slide 1 — Title

"Hi everyone, we're [team name], and this is RELAY — our submission for the Agentic AI in Action track at PSA Code Sprint.

Over the past few weeks we've been trying to answer a pretty specific question: when something goes wrong in the schedule at a transshipment hub, how do you figure out which container connections are actually at risk, and what do you do about it in the next thirty minutes — without either doing nothing, or letting an AI silently move boxes around the yard.

That's what RELAY is built for. It's not a chatbot that answers questions about port operations. It's an end-to-end recovery loop — sense the problem, score the risk, generate options, stress-test them, get a human to sign off on anything serious, and then execute with a full audit trail."

---

## Slide 2 — Executive summary

"Let me give you the overview before we go into the details.

RELAY starts when an operational signal comes in — a feeder ETA revision, a crane going down, degraded AIS data, that kind of thing. From there, a set of agents works through the incident in stages: first understanding what's happened and which transshipment connections are in trouble, then generating a few recovery plans with different trade-offs, then having a critic agent challenge those plans before anything physical gets dispatched.

The part we spent the most time on is where the human sits in that loop. The competition brief is very clear that higher autonomy isn't automatically better, and when we thought about what that means in a real terminal, it came down to this: sending the wrong notification is annoying, but dispatching the wrong restow order burns crane time, blocks yard fluidity, and can make things worse. So we designed the system so that sensing, analysis, and planning run automatically, but anything that moves metal on the ground or negotiates a sailing cutoff needs an explicit planner approval before it goes live."

---

## Slide 3 — Situation (why this problem, why PSA)

"To understand why we picked this problem, it helps to know how PSA's hub actually works.

Singapore isn't primarily an import/export port in the traditional sense — according to MPA, roughly ninety percent of throughput is transshipment. Containers arrive on one vessel and need to connect to another outbound sailing, usually within a tight window. PSA also reported last year that around ninety percent of vessels were arriving off-schedule in the first half of 2024, and container rehandling was up eight percent. So schedule volatility isn't an edge case — it's the normal operating environment.

What that means in practice is that planners aren't just tracking whether a ship is late. They're tracking something we call the **connection buffer** — essentially the time gap between when a box can realistically be available in the yard and when its outbound vessel closes. When that buffer shrinks to zero or below, you're in miss territory. And it's not all boxes equally — premium cargo, reefers, and dangerous goods tend to be the ones where a miss is most expensive, both in direct cost and in customer impact.

That's the metric we built our risk engine around. Not 'is the feeder late' in isolation, but 'given this ETA slip, which specific vessel-to-vessel links are now inside the miss window, and how bad is the exposure.'"

---

## Slide 4 — Complication (why agentic AI, why not full autonomy)

"The reason this is hard today is that the information you need is spread across different systems. Vessel schedules live in one place, yard positions in another, crane availability somewhere else, and carrier communications in yet another channel. When a feeder slips five hours, a planner is mentally stitching all of that together under time pressure, often with incomplete data.

And I think with agentic AI there's a temptation to say 'just let the agent handle it end to end.' We deliberately didn't go that route. A priority restow wave across multiple yard blocks is a real physical operation — it needs crane time, it affects other vessels, and if you get it wrong you've made the situation worse. A draft notification to a carrier, on the other hand, is low risk and reversible. So we built a tiered autonomy model: the agents do the heavy cognitive work of triage and planning, but the system stops and asks a human before anything high-impact executes.

That also lines up directly with what the brief asks for — tool orchestration, state management, human oversight, and a clear execution trace. We wanted to show all of that working together, not just a language model generating a plausible-sounding paragraph."

---

## Slide 5 — Resolution → **switch to console**

"Let me show you how this actually runs in the console we built.

At a high level there are six agents, each with a specific job. **Sentinel** ingests the trigger and opens the incident — updating ETAs, pulling weather context, flagging degraded AIS if relevant. **Analyst** builds the connection risk picture by calling tools against our terminal twin — yard hotspots, at-risk container queries, that sort of thing. **Planner** generates multiple recovery options and runs each through a what-if simulator so the numbers are grounded, not guessed. **Critic** stress-tests every plan and can effectively veto one that looks good on paper but fails operationally. **Executor** runs the approved actions through our tool layer. And **Auditor** makes sure everything — every decision, every tool call, every error — lands in an append-only trace.

The human planner sits between critique and execution. When a plan includes restow orders, cutoff extension requests, or holds, the system pauses and waits for an explicit approve or reject before dispatching anything."

**[Console]** Select **Late feeder** → **Run**.

"I'm going to run our first scenario now — the late feeder case. In this scenario, a feeder vessel's ETA slips by five and a half hours, which is the kind of off-schedule bunching PSA has been talking about publicly. As the agents run, you'll see the trace streaming in on the right panel — each event shows which agent acted, what kind of step it was, and what happened. That's intentional: we wanted judges to be able to follow the reasoning, not just see a final answer."

---

## Slide 6 — Architecture (while trace scrolls or on slide)

"Under the hood, we split the system into two layers that work together.

The **domain engine** is where the actual port logic lives. We implemented a deterministic risk scorer that calculates connection buffer for each transshipment box, applies priority weighting for premium, reefer, and DG cargo, and feeds into a what-if simulator that can model things like 'what happens if we restow these eight containers' or 'what if we negotiate a two-hour cutoff extension on the outbound vessel.' Those numbers are reproducible — run the same scenario twice and you get the same result. We did that on purpose because in operations you need to be able to audit the math, not just trust a model's intuition.

On top of that sits the **agent orchestrator**, which is a custom state machine we wrote ourselves — not a thin wrapper around an existing agent framework. It moves the incident through defined phases: detected, analysing, planning, critique, awaiting approval, executing, and closed. Each agent calls into a tool registry that mocks the kind of APIs you'd see in a real terminal environment — schedule updates, yard inventory, crane status, work order dispatch, carrier notifications. PSA didn't provide a dataset or API access for this round, so we built a synthetic Tuas-style terminal twin with realistic vessel, yard, and crane state. The data is ours, but the workflow and tool contracts are designed so they could plug into PORTNET-class systems in a sprinternship."

**[Console]** Scroll trace: point out Sentinel's ETA update → Analyst's at-risk query and risk summary → Planner's three options → Critic's notes on each.

"If you follow the trace here, you can see Sentinel pushing the revised ETA into the twin, then Analyst calling the connections tool and getting back seven at-risk boxes with a five-figure expected loss on our cost model. Planner then simulates three different recovery strategies, and Critic runs on each one before a recommendation is made."

---

## Slide 7 — Proof → **approval moment**

"So looking at the results for this run — we have seven containers inside the miss window, with expected loss in the five-figure range before any recovery action.

Planner generated three options. **PLAN-A** is the aggressive path — priority restow across the full at-risk set, trying to compress yard move times to beat the outbound cutoffs. **PLAN-B** takes a different approach — it negotiates a two-hour cutoff extension on the outbound vessels, which buys commercial flexibility, and then does selective restow only on the premium and reefer boxes that need physical protection. **PLAN-C** is the conservative option — hold the most hopeless connections for the next sailing rather than burning yard capacity on boxes that probably won't make it anyway.

After the critic runs, PLAN-B is selected — it has the best balance of connections saved versus cost and operational risk. And now you can see the approval gate — the yellow box in the console. The system has already executed the low-risk steps automatically, like internal notifications, but anything that would dispatch a work order or change a cutoff is blocked until a planner approves."

**[Console]** Click **Approve plan**.

"When I approve here, the Executor dispatches the work orders — you can see them listed at the bottom — and the Auditor re-scores the terminal state after execution. On this run we recover all seven connections, the expected loss drops to zero, and the full trace from trigger to close is sitting there if anyone needs to review what happened and why."

**[If time]** "If we have a minute, I'll quickly show the crane outage scenario as well. In that one we deliberately inject an unsafe plan called PLAN-X that looks attractive on score — it promises to restow everything at normal workface rates. But QC-07 is down, and the Critic catches that the plan assumes crane capacity that doesn't exist. It gets rejected, and a feasible plan is selected instead. We built that scenario specifically because we wanted the critic to actually change the outcome, not just add decorative comments."

---

## Slide 8 — Responsible AI

"One thing we cared a lot about is what happens when things go wrong — because in a real terminal, things do go wrong.

Our third scenario is designed around that. AIS data is degraded, so the system widens uncertainty bands before scoring connections. The yard API throws a 503 error, and Analyst retries a couple of times before falling back to the last-known positions in the twin cache — you can see the tool error in the trace, and then the fallback decision right after it. The system keeps going, but it flags reefers for verify-before-dispatch because it knows the yard data might be stale.

We also built in escalation on rejection — if a planner says no to a plan, the incident doesn't just silently close. It notifies the shift superintendent with the full dossier. There's a tool allowlist so agents can only call registered terminal APIs, not arbitrary commands. And work order dispatch requires an approval token — you can't bypass the human gate by hitting the API directly.

In the uncertainty scenario we also leave some residual risk visible on purpose. The recovery is partial, not perfect, because we thought it was more honest to show 'we saved five of twelve under bad data' than to pretend the system magically fixed everything."

---

## Slide 9 — Path forward

"If we're fortunate enough to get shortlisted for the sprinternship, the next step for us would be shadow mode with PSA mentors — running RELAY alongside real planners to tune the risk weights, and wiring the same tool contracts to actual terminal APIs instead of our synthetic twin.

In terms of how this fits the broader ecosystem, MPA's Maritime Digital Twin — which launched earlier this year — is really about situational awareness: where vessels are, what's happening across the network. RELAY is complementary to that. It's the agentic recovery layer that sits on top when something breaks — running scenarios, ranking options, gating physical moves, and producing an audit trail that operations can actually use."

---

## Slide 10 — Close

"So that's RELAY — transshipment connection continuity with agentic orchestration and human gates on the moves that matter.

We're happy to re-run any of the three scenarios live if you'd like to see them again — the late feeder, the crane outage, or the uncertainty case with tool failure. Thank you, and we're happy to take questions."

---

## Timing guide

| Mode | Rough length |
|------|----------------|
| Slides only (this script) | ~8–9 min |
| Slides + live late_feeder demo | ~10–11 min (trim slides 8–9 if needed) |
| + crane teaser | use only if you have buffer |

---

## If the demo breaks

"If the API isn't responding, let me walk you through the trace from our rehearsal run — the logic is the same."

Then scroll a completed incident, or switch to your recorded video. Judges care that you understand what you built.

---

## Key things to explain if asked

**Connection buffer:** "It's not just ETA — it's the gap between when the box can be available and when the outbound vessel sails, minus handling time and a safety margin."

**Why deterministic scoring:** "We wanted numbers you can reproduce and audit. The agents orchestrate; the engine does the math."

**Why six agents:** "Each one has a single responsibility. The critic is separate from the planner so dissent is real, not an afterthought."

**Synthetic twin:** "PSA didn't provide live data for this round. We built sample terminal state with the same API shapes we'd use for real integration."

**No LLM required to run:** "The demo runs entirely on our Python backend with no API keys. Scoring and simulation are deterministic."
