---
title: "Facilitation, Logistics & Failure Modes for Virtual AI-TDD Workshops"
date: 2026-06-03
depth: standard
format: md
topic: "Facilitation, logistics & failure modes"
topic_raw: "Facilitation, logistics & failure modes"
issue: 182
tags: [facilitation, workshop, virtual, TDD, AI, developer-training, expert-audience]
summary: "Practical playbook for a 90-min virtual hands-on AI-TDD workshop with expert developers: Codespaces-based env setup, pre-provisioned API keys, three facilitation roles, 60/70 hands-on split, and a 10-row failure-mode prevention table."
citations: 15
reading_time_min: 7
cover: cover.svg
cost_usd: 1.30
duration_sec: 509
model: "Sonnet 4.6"
---

> **TL;DR** — Eliminate environment setup from live time with GitHub Codespaces prebuilds [[6]](https://dev.to/bengreenberg/unlocking-github-codespaces-for-workshops-344o); pre-provision capped AI API keys per participant, not shared [[9]](https://blog.mehdio.com/p/running-an-ai-workshop-build-a-llm); assign a separate producer role so the lead never touches Zoom controls [[7]](https://www.trainingforchange.org/training_tools/facilitation-and-roles-prep-for-a-large-online-training/); run 60–70% hands-on exercises in a 90-min max session [[12]](https://www.kaizenko.com/test-driven-development-deep-dive-workshop/). Every failure mode in this domain is predictable — the table at the end is your pre-mortem checklist.

---

## Pre-Workshop Logistics

### Environment: Eliminate Setup Friction Before Day One

The single most destructive failure mode for virtual coding workshops is environment setup consuming the first 20–30 minutes of live session time [[3]](https://www.nceas.ucsb.edu/news/hands-coding-virtually). Solve it entirely in the week before.

**GitHub Codespaces (recommended)** — Commit a `.devcontainer/devcontainer.json` to the workshop repo and enable prebuilds. "As soon as someone enters the environment everything is ready to go" [[6]](https://dev.to/bengreenberg/unlocking-github-codespaces-for-workshops-344o). Participants need only a browser and a GitHub account [[13]](https://github.com/features/codespaces).

Pre-build must include, run to completion before the session:

- Language runtime + test framework (e.g. Node 22 + Vitest, Python 3.12 + pytest)
- AI copilot extension pre-authenticated (GitHub Copilot, Continue.dev, or Claude extension)
- All dependencies installed (`npm install` / `pip install`) so first `Run Test` is instant
- Sample repo with one failing test and a stub to fill in — participants arrive already on the red step

⚠ Free-tier Codespaces users have 60 hrs/month and 15 GB storage. Provide GitHub credit vouchers or use a GitHub Enterprise org to avoid mid-session compute exhaustion [[6]](https://dev.to/bengreenberg/unlocking-github-codespaces-for-workshops-344o).

**Fallback for local-only participants** — Include a `.devcontainer` so `docker compose up` produces an identical environment. Make this opt-in, not the default path.

### AI API Key Provisioning

For workshops > 10 participants, a shared key is a security risk; per-participant self-signup during the live session costs 10–20 minutes [[9]](https://blog.mehdio.com/p/running-an-ai-workshop-build-a-llm). Pre-provision individual keys with hard limits:

| Setting          | Recommended value                                    |
|------------------|------------------------------------------------------|
| Per-key budget   | $2–5 (hard cap, not soft alert)                      |
| Expiry window    | Workshop day + 24 hrs                                |
| Model allowlist  | Restrict to the model(s) used in exercises only      |
| Claims window    | Opens 1 hr before start, closes at session end       |
| Distribution     | Email link 48 hrs out; test `curl` snippet included  |

[9]: https://blog.mehdio.com/p/running-an-ai-workshop-build-a-llm

Use a key minter (OpenRouter provisioning API, Anthropic's management API, or a simple webhook against a YAML budget config) [[9]](https://blog.mehdio.com/p/running-an-ai-workshop-build-a-llm). "Pull requests are the admin UI" — store the config in the workshop repo.

### Participant Pre-Check (send 72 hrs before)

Require participants to complete this before the session — not as optional prep but as a hard gate:

- [ ] GitHub account created; Codespace opened from the workshop link; VS Code loads with test file visible
- [ ] AI extension authenticated; test: generate a "hello world" function and accept it
- [ ] AI API key claimed; test: run the provided `curl` snippet and get a valid response
- [ ] Zoom desktop client installed (browser Zoom breaks screen sharing in breakout rooms)

---

## Facilitation Roles

Three distinct roles prevent cognitive overload on the lead [[7]](https://www.trainingforchange.org/training_tools/facilitation-and-roles-prep-for-a-large-online-training/). The lead should never also operate Zoom controls — the task-switch kills pacing.

| Role          | Responsibility during the session                                                             |
|---------------|-----------------------------------------------------------------------------------------------|
| **Lead**      | Delivers content, runs exercises, timeboxes discussions, reads the room, calls breaks         |
| **Producer**  | Manages Zoom polls/breakouts, watches chat, voices chat questions to Lead, handles recordings |
| **Helper(s)** | One per breakout room of 4–6; unsticks participants, demos on their own screen only           |

[7]: https://www.trainingforchange.org/training_tools/facilitation-and-roles-prep-for-a-large-online-training/

Helpers do not need to know all the material — comfort with one exercise or tool is sufficient [[3]](https://www.nceas.ucsb.edu/news/hands-coding-virtually). Brief all three roles together for 10 minutes before the session: agree on a hand signal for "wrap up this breakout" and one for "extend by 5 min".

---

## Session Structure & Pacing

**90 minutes is the expert-audience ceiling** for synchronous virtual sessions in 2026 — attention degrades past that regardless of content quality [[5]](https://www.parallelhq.com/blog/how-to-facilitate-workshop) [[8]](https://www.edufellowship.com/blog/facilitation-workshop-design-2025/).

```
00:00–00:10  Check-in + env validation
             Everyone shares screen: "show me a passing test"
             Catches setup stragglers before exercises begin

00:10–00:20  Context frame
             Why AI-TDD? What the session won't cover.
             Explicitly name AI limitations to pre-empt expert derailment.

00:20–00:55  Exercise block 1 (35 min in breakout pairs/trios)
             Red-green cycle: write a failing test, use AI to generate
             implementation, verify, refactor. First win in < 5 min.

00:55–01:00  Break (hard stop — non-negotiable even at 5 min)

01:00–01:30  Exercise block 2 (30 min)
             Harder case: ambiguous spec, AI generates incorrect test;
             participants must catch and fix it. Demonstrates AI limits.

01:30–01:40  Debrief + parking lot resolution
             What surprised you? What would you not trust AI with?

01:40–01:50  Takeaways + Monday action
             Each person names one specific thing to try this week.
```

**Time-boxing rules** [[2]](https://voltagecontrol.com/articles/the-pitfalls-of-poor-facilitation-common-mistakes-and-how-to-avoid-them/):
- Producer runs a visible countdown (Zoom timer or shared clock URL in chat)
- Lead calls time; Producer enforces room recall
- Off-topic questions go to the **parking lot** — a shared Miro/FigJam tile where participants or Producer add threads for async follow-up [[11]](https://www.sessionlab.com/methods/parking-lot)

**60–70% of session time must be hands-on code** [[12]](https://www.kaizenko.com/test-driven-development-deep-dive-workshop/). Expert audiences disengage from lecture-mode within 15 minutes. Apply the 70/30 rule: 70% human conversation and pair coding, 30% tech interaction [[8]](https://www.edufellowship.com/blog/facilitation-workshop-design-2025/).

---

## Expert Audience Dynamics

Senior developers resist AI tooling for four documented reasons [[4]](https://www.faros.ai/blog/ai-adoption-in-senior-software-engineers):

1. **Trust/reliability** — "AI makes subtle errors on complex code"
2. **Identity threat** — "this diminishes craft and intellectual satisfaction"
3. **Complexity gap** — "it doesn't understand our architecture or constraints"
4. **Time cost** — "I don't have cycles to learn another tool"

**What works** [[4]](https://www.faros.ai/blog/ai-adoption-in-senior-software-engineers) [[1]](https://www.sessionlab.com/blog/virtual-facilitation/):
- Peer credibility over mandate: frame exercises as "here's what I tried" — peer-driven adoption is 22% more effective than top-down framing
- Explicit sandbox safety: the workshop is a protected experiment space; failures are data, not incompetence
- Concrete first win in < 5 minutes: a passing test generated with AI before skepticism can calcify

**What fails** [[4]](https://www.faros.ai/blog/ai-adoption-in-senior-software-engineers) [[10]](https://medium.com/design-bootcamp/top-7-most-common-mistakes-done-by-workshop-facilitators-a5e7588de262):
- "This is the new standard" framing — triggers identity resistance
- Skipping the "what AI does badly" discussion — experts find the gaps themselves mid-exercise and derail the group if you haven't pre-empted it
- Homogeneous breakout groups (all skeptics together, or all enthusiasts together) — moderate cognitive diversity; avoid extremes [[15]](https://stormz.me/en/blog/five-common-mistakes-when-preparing-collaborative-workshop)

**Dominant voice handling** [[5]](https://www.parallelhq.com/blog/how-to-facilitate-workshop): use silent brainstorming before group discussion to prevent groupthink; in debrief, use round-robin ("one word each before open discussion") then open the floor.

---

## Virtual-Specific Logistics

**Breakout rooms** [[14]](https://mutedeck.com/blog/2025-11-06-breakout-rooms-in-zoom/):
- Pre-assign groups; don't use random assignment (experts resent the kindergarten feel)
- 2–3 devs per room for pair/mob TDD — 4–5 max before collaboration degrades
- Mix skill levels within rooms; avoid grouping all sceptics together [[15]](https://stormz.me/en/blog/five-common-mistakes-when-preparing-collaborative-workshop)
- Helper joins each room for first 3 minutes, checks everyone has the exercise loaded, then cycles

**Screen sharing** [[3]](https://www.nceas.ucsb.edu/news/hands-coding-virtually):
- Provide a suggested layout in participant instructions: left half = Codespace, right half = Zoom
- Instruct participants to share full screen, not application window (prevents tool-switch artifacts)
- Helpers share their own screen to demonstrate; never take over a participant's keyboard

**Chat as parallel channel**: Producer answers logistics questions in chat so Lead is never interrupted. Post exercise instructions as chat text in addition to speaking them — participants still in setup miss verbal-only instructions.

---

## Failure Modes

| Failure mode                              | Impact                                                    | Prevention                                                                                                             |
|-------------------------------------------|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Environment setup in live session         | Loses 20–30 min; derails all subsequent timings           | Codespaces prebuild + mandatory pre-check 24 hrs before [[6]][6]                                                       |
| AI API key failure on day                 | Blocks all exercises; kills credibility of the workshop   | Pre-provision with expiry; day-before test `curl` snippet required to claim key [[9]][9]                               |
| Demo-heavy, hands-on-light                | Expert disengagement within 15 min                        | Hard rule: ≤7 min explanation before participants touch code; enforce in run-of-show [[2]][2]                           |
| Dominant expert hijacking discussion      | Others disengage; session follows one rabbit hole         | Parking lot + timebox; round-robin format for debrief; silent brainstorm before open floor [[5]][5]                    |
| Exercise too ambiguous                    | Participants stuck; helpers overwhelmed; pacing collapses  | Test every exercise solo end-to-end before session; embed "if stuck" hints as comments in the repo stub [[10]][10]     |
| Tool sprawl                               | Cognitive overload; participants lose their place         | One primary tool per task; introduce tools sequentially; avoid simultaneous Zoom + Miro + Slack + IDE [[3]][3]          |
| No helper in breakout rooms               | Stuck participants wait silently; frustration builds       | 1 helper per room of 4–6, briefed on exercise goals, arrives in room first 3 min [[7]][7]                              |
| Expert resistance to AI tooling           | Overt scepticism infects room culture                     | Address AI limits explicitly in context frame; use peer-champion framing; first win must be concrete [[4]][4]           |
| Overrun debrief, no synthesis time        | Participants leave with open loops                        | Hard 10-min closing slot in run-of-show; parking lot absorbs overflow; send written recap within 24 hrs [[2]][2]       |
| No break in 90-min session                | Focus degrades in last 30 min; diminishing returns         | 5-min break at the midpoint, non-negotiable even under time pressure [[10]][10]                                        |

[2]: https://voltagecontrol.com/articles/the-pitfalls-of-poor-facilitation-common-mistakes-and-how-to-avoid-them/
[3]: https://www.nceas.ucsb.edu/news/hands-coding-virtually
[4]: https://www.faros.ai/blog/ai-adoption-in-senior-software-engineers
[5]: https://www.parallelhq.com/blog/how-to-facilitate-workshop
[6]: https://dev.to/bengreenberg/unlocking-github-codespaces-for-workshops-344o
[7]: https://www.trainingforchange.org/training_tools/facilitation-and-roles-prep-for-a-large-online-training/
[9]: https://blog.mehdio.com/p/running-an-ai-workshop-build-a-llm
[10]: https://medium.com/design-bootcamp/top-7-most-common-mistakes-done-by-workshop-facilitators-a5e7588de262
