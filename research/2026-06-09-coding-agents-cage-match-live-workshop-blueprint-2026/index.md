---
layout: expedition
title: "Coding Agents Cage Match: Live Workshop Blueprint (2026)"
date: 2026-06-09
topic: "Design and run a \"Coding Agents Cage Match\" live workshop — four AI coding tools, one task, live scoring (2026)."
format: md
tags: [ai-coding, workshop, benchmarking, frontier-vs-local, live-scoring]
summary: "Complete blueprint for running a live head-to-head AI coding tool competition: task spec, team playbook, scoring rubric, debrief script, and a published comparison table — covering Claude Code, Cursor, Copilot, Codex CLI, and local-model alternatives."
cover: cover.svg
synthesis: true
children:
  - slug: tool-capabilities-and-2026-state-of-the-art
    title: "Tool capabilities and 2026 state-of-the-art"
    depth: standard
    status: success
    summary: "The seven tools that dominate AI-assisted coding in mid-2026: architectures, real benchmark scores, pricing, and a pick-your-stack guide."
    citations: 18
    reading_time_min: 6
  - slug: task-design-and-success-criteria
    title: "Task design and success criteria"
    depth: standard
    status: success
    summary: "How to design tasks and score results when comparing AI coding agents head-to-head in a timed live-audience setting."
    citations: 15
    reading_time_min: 5
  - slug: frontier-vs-local-model-shootout
    title: "Frontier vs local model shootout"
    depth: deep
    status: success
    summary: "Open weights now trail the closed frontier by ~4 months on Epoch's index and ~6 points on Artificial Analysis; here's where local wins, where frontier is still mandatory, and what the hardware costs."
    citations: 50
    reading_time_min: 8
  - slug: live-workshop-logistics-and-team-setup
    title: "Live workshop logistics and team setup"
    depth: standard
    status: success
    summary: "Run-of-show, room and network guide, and per-tool pre-event checklist for hosting a live 4-way AI coding tool competition with real-time audience scoring."
    citations: 15
    reading_time_min: 5
  - slug: debrief-and-scoring-synthesis
    title: "Debrief and scoring synthesis"
    depth: ceo
    status: success
    summary: "Structured debrief and scoring methodologies for synthesizing live workshop data into actionable comparative insights."
    citations: 5
    reading_time_min: 2
cost_usd: 8.44
duration_sec: 2268
citations: 103
reading_time_min: 26
issue: 208
model: "Sonnet 4.6"
---

The five research threads converge on three hard-won constraints that must be built into every layer of the workshop design — task, logistics, scoring, and debrief — or the results tell you nothing useful.

## Constraint 1: Published benchmarks are noise, not signal

The most important finding from the [tool capabilities](tool-capabilities-and-2026-state-of-the-art/) and [frontier-vs-local](frontier-vs-local-model-shootout/) children is that every major published number is partly contaminated. Claude Opus 4.5 scores 80.9% on SWE-bench Verified but only 45.9% on the cleaner SWE-bench Pro — a 35-point gap attributable almost entirely to training-set leakage [[1]](https://www.codeant.ai/blogs/swe-bench-scores). The honest ceiling on uncontaminated coding benchmarks is around 69% [[2]](https://www.codeant.ai/blogs/swe-bench-scores). HumanEval and MBPP are fully saturated and no longer discriminate [[3]](https://runloop.ai/blog/understanding-llm-code-benchmarks-from-humaneval-to-swe-bench). This is why the live workshop format has genuine value: a task drawn from a repo created or forked *after* all tools' training cutoffs, with a locked `tests/` directory that no agent can delete, produces a score that vendors cannot game. That single rule — **lock the tests before the clock starts** — is the cage match's core integrity mechanism [[4]](https://benchmarkingagents.com/swe-bench/).

## Constraint 2: Pass@1 variance is large; your results are directional, not definitive

A live workshop is a single trial. The [task design](task-design-and-success-criteria/) child establishes that pass@1 conflates genuine capability with luck on any single run; only pass@3 (three independent runs of the same task) separates fluky passes from reliably capable tools [[5]](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). This doesn't invalidate the workshop — it frames it correctly. The live event is the entertainment and initial signal; the post-event pass@3 sweep (each team runs again twice after the audience has left) is the publishable comparison table. Announce this structure upfront so the audience doesn't over-index on who "won" in the room.

The two axes of comparison depend on this framing differently. For the **four-tool axis** (Claude Code vs Cursor vs Copilot vs Codex CLI), the frontier models powering them are roughly comparable, so pass@1 variance matters a lot — the gap between tools may be smaller than within-tool variance. For the **frontier-vs-local axis**, the gap on hard coding tasks is about 27 points on SWE-bench (Claude Opus 4.8 at 88.6% vs the best open-weight Nemotron at 60.5%) [[6]](https://www.codeant.ai/blogs/swe-bench-scores), so a single run is likely sufficient to observe the capability difference.

## Constraint 3: Spec misalignment, not model quality, is the #1 live failure mode

41.86% of all failures in end-to-end coding agent benchmarks trace back to agents omitting critical business logic or misunderstanding requirements [[7]](https://arxiv.org/html/2602.01655v1) — not to the model being incapable. In a 30-minute live run the facilitator cannot iterate the spec; there is no second chance. The [task design](task-design-and-success-criteria/) child's SMART-spec requirements (Specific, Measurable, Achievable, Relevant, Time-bound), three explicit milestones (route defined → core tests pass → edge cases pass), and a `REQUIREMENTS.md` file already in the repo are the primary safeguards. The [logistics](live-workshop-logistics-and-team-setup/) child reinforces this from the operational side: tool assignments sent 48 hours before, subscriptions pre-authenticated the prior week, and no rehearsal on event-day morning (Claude Code's 5-hour usage-reset window can be exhausted). Together these protect against the two most common ways a workshop fails without any tool being at fault.

## Where the research leaves gaps

The [debrief child](debrief-and-scoring-synthesis/) was run at CEO depth (Haiku model) and covers scoring frameworks at a surface level — the weighted model and retrospective structure are sound, but the specific live scoring sheet format, the published comparison table template, and the debrief script tailored to AI tool tradeoffs (privacy, cost-per-token, latency) are not fully worked out there. Those artifacts need to be authored from the rubric in the [task design](task-design-and-success-criteria/) child (correctness 40%, completeness 25%, code quality 15%, edge cases 10%, speed bonus 10%) and the metrics surfaced in the [frontier-vs-local](frontier-vs-local-model-shootout/) child (latency, cost per 1M tokens, data-residency posture).

The [logistics](live-workshop-logistics-and-team-setup/) child also does not address the local-model team's hardware requirements. If a fifth team runs Qwen3-Coder-480B-A35B (the strongest single-24GB-GPU local coding model [[8]](https://github.com/QwenLM/Qwen3-Coder)) or a Llama/DeepSeek stack via Ollama, they need an RTX 4090 or Mac M3 Ultra pre-staged — not a standard conference laptop.

The open question that none of the children fully answers: **at what token volume does running a local model team become cheaper than a frontier API team for the workshop's specific task?** The [frontier-vs-local](frontier-vs-local-model-shootout/) child puts the crossover at roughly 500K tokens/day for sustained production use [[9]](https://www.sitepoint.com/local-llms-vs-cloud-api-cost-analysis-2026/), but a single 30-minute workshop session likely stays well under that — meaning local wins on privacy and latency optics, not on raw cost.
