---
layout: expedition
title: "Evals: How Do You Know Your AI Works? — A Session Blueprint"
date: 2026-06-04
topic: "Build a session blueprint for an Itenium AI-track technical session on evals — testing AI/LLM systems, catching prompt regressions, LLM-as-judge, golden datasets, CI integration, agent/RAG evaluation, and how to teach it as a 2h hands-on workshop or a talk (2026)."
format: md
tags: [llm-evals, ai-quality, testing, ci-cd, consultancy]
summary: "Everything to run an evals session for a client-shipping consultancy: the methodology that actually matters, the 2026 tooling shake-up, CI gates, agent/RAG specifics, and a runnable 2h lab."
cover: cover.svg
synthesis: true
model: "Opus 4.8"
duration_sec: 577
cost_usd: "sub"
children:
  - slug: eval-methodologies-metrics
    title: "Eval Methodologies & Metrics for LLM Systems: The Taxonomy, the Judge Problem, and the Statistics"
    depth: survey
    status: success
    summary: "A workshop-ready map of LLM eval metric types, the LLM-as-judge bias/calibration trap, and the small-sample statistics most teams get wrong."
    citations: 22
    reading_time_min: 9
  - slug: tooling-landscape-2026
    title: "LLM Eval Tooling Landscape 2026: A Consultancy's Decision Guide"
    depth: expedition
    status: success
    summary: "Decision-grade 2026 comparison of nine LLM eval tools across license, self-host, CI/CD, judge, agent/RAG, pricing, stars and lock-in — with pick-X-if calls for a client-shipping consultancy."
    citations: 41
    reading_time_min: 9
  - slug: evals-in-ci-cd
    title: "Wiring LLM Evals into CI/CD: gates, flaky judges, and cost budgets (2026)"
    depth: survey
    status: success
    summary: "How to run LLM eval suites in pipelines in 2026: deterministic-gates-the-judge, statistical regression gates, cost/latency budgets, caching/sampling, and concrete Promptfoo/Braintrust/DeepEval/LangSmith wiring."
    citations: 13
    reading_time_min: 9
  - slug: agent-rag-specific-evaluation
    title: "Agent & RAG Evals in 2026: Trajectories, Tool-Use, and Ragas Metrics"
    depth: survey
    status: success
    summary: "Why single-turn evals miss agent/RAG failures, and the 2026 metric stack — trajectory + tool-use correctness, pass^k reliability, and Ragas-style RAG decomposition — that catches them."
    citations: 15
    reading_time_min: 8
  - slug: workshop-session-design
    title: "Teaching Evals: A 2h Hands-On Workshop (and Talk Variant) for Expert Devs"
    depth: survey
    status: success
    summary: "A runnable 2h evals lab on DeepEval — golden set → LLM-judge → CI gate → planted regression — with timing, fixtures, and the workshop-vs-talk call."
    citations: 19
    reading_time_min: 9
---

> **Decision** — Ship this as a 2-hour, demo-driven hands-on session standardized on DeepEval, and teach *error analysis*, not tool-clicking. In 2026 the eval harness is commoditized; the methodology above it is the hard part and the thing a consultancy can actually sell.

Across all five angles one theme dominates: the eval *harness* is now a solved, commoditized layer, and the field has converged on a two-tier stack — a lightweight CI-gating framework (DeepEval, Ragas, or Promptfoo) paired with an annotation-and-dashboard platform (Braintrust, LangSmith, or Arize) [[1]](https://www.braintrust.dev/articles/deepeval-alternatives-2026). The real differentiator is the discipline above the tools: build a golden set, write a *binary* LLM-as-judge grader, and calibrate that judge against human labels via TPR/TNR rather than raw agreement [[2]](https://www.aakashg.com/ai-evals-masterclass-with-hamel-shreya/). That is the "who grades the grader" loop — and it's exactly where most client projects fly blind.

Tooling choice is unusually time-sensitive. OpenAI's acquisition of Promptfoo (9 March 2026, ~$86M; the project stays MIT) [[3]](https://openai.com/index/openai-to-acquire-promptfoo/)[[4]](https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/) turns the most-starred leader into a vendor-aligned bet — a real concern when you ship provider-neutral evaluations for clients. That tips the lab's default to DeepEval: pytest-native, CI-ready, provider-neutral (see [tooling landscape](tooling-landscape-2026/) and [workshop design](workshop-session-design/)).

The angles reinforce each other on *why* evals matter at all. The reliability math is the punchline: a 90%-reliable agent step compounds to ~57% end-to-end success over 8 steps (pass^k) [[5]](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide) — the quantitative case for the planted-regression demo and for blocking the build on a statistical gate, not a vibe (see [evals in CI/CD](evals-in-ci-cd/)). Agents and RAG also break the single-turn assumption entirely: you need trajectory and tool-use correctness, plus RAG's faithfulness / context-precision-recall decomposition against explicit thresholds [[6]](https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026), so the eval layer has to be component-aware, not just end-to-end. This is also the cleanest hook back into the wider AI track, whose RAG and MCP/agent sessions produce precisely the systems these evals are built to test.

Sharpest open question before scheduling: run it as a true hands-on lab — highest learning, highest setup-failure risk — or as a demo-driven hybrid that degrades gracefully to a talk?
