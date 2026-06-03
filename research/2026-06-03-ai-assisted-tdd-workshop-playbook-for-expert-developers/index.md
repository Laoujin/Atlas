---
layout: expedition
title: "AI-Assisted TDD Workshop Playbook for Expert Developers"
date: 2026-06-03
topic: "Design a hands-on mini-workshop on AI-assisted testing & TDD for an expert developer audience — part of the same virtual session/workshop series (1–2h). Contrast deliberately with the existing vibe-coding workshop, which targeted non-technical participants: this is for senior devs and participants must drive an agent through a real red-green-refactor loop themselves, not watch a demo."
format: md
tags: [ai-tdd, workshop-design, expert-developers, test-first, agentic-coding]
summary: "A runnable playbook for a 90-min AI-assisted TDD workshop targeting senior developers: exercise catalog, Codespaces scaffolding, facilitation roles, and honest evidence on what AI actually delivers in 2026."
cover: cover.svg
synthesis: true
children:
  - slug: ai-assisted-tdd-techniques-evidence-2026
    title: "AI-assisted TDD techniques & evidence (2026)"
    depth: standard
    status: success
    summary: "Evidence and practical techniques for integrating AI tools into TDD workflows — covering the productivity paradox, prompt patterns, test quality limits, and agentic approaches."
    citations: 22
    reading_time_min: 7
  - slug: workshop-exercises-scaffolding
    title: "Workshop exercises & scaffolding"
    depth: standard
    status: success
    summary: "Curated exercises, katas, and scaffolding patterns for a hands-on AI-assisted TDD mini-workshop targeting expert developers."
    citations: 22
    reading_time_min: 6
  - slug: facilitation-logistics-failure-modes
    title: "Facilitation, logistics & failure modes"
    depth: standard
    status: success
    summary: "Practical playbook for a 90-min virtual hands-on AI-TDD workshop with expert developers: Codespaces-based env setup, pre-provisioned API keys, three facilitation roles, 60/70 hands-on split, and a 10-row failure-mode prevention table."
    citations: 15
    reading_time_min: 7
  - slug: tooling-stack-for-the-workshop
    title: "Tooling stack for the workshop"
    depth: standard
    status: success
    summary: "Layer-by-layer stack recommendation: AI assistant (Copilot/Cursor/Cline), test framework (Vitest/pytest), infra (Codespaces devcontainer), and optional quality-demo tools — with copy-paste TDD prompts."
    citations: 20
    reading_time_min: 5
cost_usd: 6.36
duration_sec: 2564
citations: 79
reading_time_min: 25
model: "Sonnet 4.6"
---

The expedition landed on two facts that should be in the facilitator's opening frame, not buried in slides.

First, the productivity numbers are messier than vendor decks suggest. GitHub Copilot's canonical RCT [[1]](https://arxiv.org/abs/2302.06590) showed a 55.8% speedup on a bounded toy task. METR's RCT [[2]](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) ran experienced developers on their own real codebases using Cursor Pro — and measured a 19% *slowdown*. The same developers *estimated* they were 20% faster [[3]](https://arxiv.org/abs/2507.09089). That self-perception gap is the workshop's opening premise: participants are not here to be sold AI tooling; they are here to learn where structure makes AI assistance reliable instead of merely fast-feeling.

Second, AI test generators are not designed to catch bugs — they are designed to pass. Evaluation of CodiumAI CoverAgent and CoverUp found generated tests cannot detect existing bugs, actively validate faulty implementations, and structurally filter out tests that would expose bugs [[4]](https://arxiv.org/abs/2412.14137). Copilot `/tests` with no seed tests produces a 92.45% failure-or-empty rate [[5]](https://testomat.io/blog/ai-unit-testing-a-detailed-guide/). This is the vibe-coding failure mode in test clothing: AI produces coverage theater, not quality signal.

**Where all four angles converge.** The single most load-bearing constraint across the [evidence](ai-assisted-tdd-techniques-evidence-2026/), [exercises](workshop-exercises-scaffolding/), [tooling](tooling-stack-for-the-workshop/), and [facilitation](facilitation-logistics-failure-modes/) pages is five words: *"You may not modify the test file."* This redirects the model's optimization from "make it green by any means" to "write a correct implementation." It belongs on exercise sheets, in `.github/copilot-instructions.md`, and in the facilitator's opening frame. Without it, experienced developers will discover the cheat in under ten minutes and dismiss the entire loop.

**The counterintuitive TDAD finding.** The 2026 TDAD paper [[6]](https://arxiv.org/abs/2603.17973) found that adding standard TDD procedural instructions to a coding agent's prompt — without a dependency context map — *worsened* regression rates from 6.08% to 9.94%, worse than no intervention at all. With the context map, regressions dropped to 1.82%. The implication for the workshop frame: the goal is not to teach agents to *follow* TDD. It is to teach developers to *structure* AI work so tests serve as executable specifications. Procedure without context is worse than nothing; this finding should preempt any participant who asks "can't we just put TDD rules in the system prompt?"

**The vibe-coding contrast is the anchor exercise.** The [exercises page](workshop-exercises-scaffolding/) recommends a 10-minute anti-pattern demo: implement a feature without tests via AI, add a second feature, and observe architectural degradation in real time. AI coding agents never spontaneously suggest refactoring without test constraints [[7]](https://www.softwareseni.com/understanding-anti-patterns-and-quality-degradation-in-ai-generated-code/). This is the sharpest contrast with the vibe-coding workshop for non-technical audiences — expert developers internalize it from a live diff, no argument required.

**Tooling drives exercise choice, not vice versa.** Cursor's YOLO mode [[8]](https://engineering.monday.com/coding-with-cursor-heres-why-you-still-need-tdd/) runs the full test loop autonomously — useful for facilitated demos, potentially counterproductive for hands-on learning (participants watch rather than drive). The [facilitation plan](facilitation-logistics-failure-modes/) resolves this tension: Cursor for demos, Copilot or Continue.dev for participant exercises. Exercises pre-populate failing tests; participants implement with AI. This pattern eliminates the need for participants to write good test specs under time pressure while enforcing the red step structurally.

**What the TDAD dependency-map approach means in practice.** As of mid-2026, no workshop-friendly tool ships test-impact context maps out of the box. Participants will leave knowing the highest-leverage agentic TDD pattern [[6]](https://arxiv.org/abs/2603.17973) exists but cannot apply it immediately in their IDE without custom tooling. That may be the most honest outcome a 90-minute session can produce — and naming it explicitly in the closing segment is more durable than pretending the field has solved agentic TDD.
