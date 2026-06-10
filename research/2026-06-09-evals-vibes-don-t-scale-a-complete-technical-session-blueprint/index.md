---
layout: expedition
title: "Evals — Vibes Don't Scale: A Complete Technical Session Blueprint"
date: 2026-06-09
topic: "Build and deliver a technical session: \"Evals — Vibes Don't Scale\" (2026)"
format: md
tags: [llm-evals, ci-integration, golden-dataset, grading-rubrics, session-blueprint]
summary: "A complete session blueprint for expert developers covering golden datasets, LLM-as-judge validation, CI delta gates, and a live regression demo that catches what vibe checks miss."
cover: cover.svg
synthesis: true
children:
  - slug: golden-dataset-construction
    title: "Golden dataset construction"
    depth: deep
    status: success
    summary: "How to build, label, size, and maintain a golden dataset — the curated ground-truth set that turns LLM evals from vibes into measurable signal."
    citations: 37
    reading_time_min: 7
  - slug: llm-as-judge-grader-design
    title: "LLM-as-judge grader design"
    depth: deep
    status: success
    summary: "How to design an LLM-as-judge grader: pick a grading mode, write a binary decomposed rubric, neutralize the bias catalogue, and validate against human labels before you trust a single score."
    citations: 44
    reading_time_min: 9
  - slug: eval-framework-landscape-2026
    title: "Eval framework landscape 2026"
    depth: deep
    status: success
    summary: "The 2026 LLM-eval landscape, mapped: open-source libraries vs hosted platforms, scoring methods and their biases, agent/RAG evals, and how teams gate eval suites in CI."
    citations: 63
    reading_time_min: 10
  - slug: wiring-evals-into-ci
    title: "Wiring evals into CI"
    depth: standard
    status: success
    summary: "How to wire LLM evaluations into CI: path-scoped triggers, a layered eval pyramid, statistical delta gates, and a tool comparison across DeepEval, Promptfoo, Langfuse, and Braintrust."
    citations: 18
    reading_time_min: 7
  - slug: live-regression-demo-design
    title: "Live regression demo design"
    depth: standard
    status: success
    summary: "How to design a 3-minute live regression demo that converts skeptics: the right scenario, promptfoo as the demo tool, cached responses for reliability, and scripted keypresses via Demo Time."
    citations: 15
    reading_time_min: 5
  - slug: eval-security-and-data-governance
    title: "Eval security and data governance"
    depth: ceo
    status: success
    summary: "Model evaluation systems face adversarial attack risks, privacy leakage through data memorization, and regulatory compliance pressures requiring explicit data governance frameworks."
    citations: 8
    reading_time_min: 2
  - slug: metrics-beyond-accuracy
    title: "Metrics beyond accuracy"
    depth: ceo
    status: success
    summary: "Accuracy hides failures on imbalanced data and across subpopulations. Match your metric to your use case: Precision/Recall for trade-offs, F1 for imbalance, PR-AUC for rare positives, and task-specific metrics for AI agents."
    citations: 7
    reading_time_min: 2
cost_usd: 16.59
duration_sec: 3137
citations: 192
reading_time_min: 42
issue: 206
model: "Sonnet 4.6"
---

The seven threads converge on one claim: **the bottleneck in LLM evaluation is not tooling, it's validation discipline** [[1]](https://hamel.dev/blog/posts/evals/index.html). Any of the eight viable open-source libraries can run your suite; none of them will tell you whether the suite is measuring what you think it is.

**The dependency chain is strict.** Golden dataset first — you need ~246 examples for 95% confidence at ±5% margin [[2]](https://dev.to/gabrielanhaia/eval-set-sizing-the-statistical-power-math-behind-llm-ab-tests-4gpc), and "20 examples" can't move a launch decision. Then validate the judge against those human labels using TPR/TNR, not accuracy [[3]](https://hamel.dev/blog/posts/evals-faq/) — a judge that always predicts "pass" can score 90% accuracy while catching zero real failures. Only then can CI gates be meaningful: use statistical delta gates (mean drop + Welch's t + effect size) rather than absolute score floors [[4]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).

Two pieces of practitioner consensus cut across every angle and should anchor the session's prescriptions: **(1) binary pass/fail beats Likert scales**, both for ground-truth labeling [[3]](https://hamel.dev/blog/posts/evals-faq/) and for judge rubrics [[5]](https://hamel.dev/blog/posts/evals-faq/why-do-you-recommend-binary-passfail-evaluations-instead-of-1-5-ratings-likert-scales.html) — the gap between a 3 and a 4 is subjective, and annotators default to the middle to avoid hard calls; **(2) decompose vague rubrics into specific binary checks** — "is this response good?" is unjudgeable; "does the response name the correct refund policy?" is not [[6]](https://www.promptfoo.dev/docs/guides/llm-as-a-judge/).

**The bias catalogue is systematically underestimated.** Position bias alone causes 20–40% of close-pair pairwise verdicts to flip on swap [[7]](https://arxiv.org/html/2306.05685v4). A verbosity padding attack fooled Claude-v1 and GPT-3.5 **91.3%** of the time [[7]](https://arxiv.org/html/2306.05685v4). The mitigation is cheap: run pairwise in both orders, count only consistent wins, and judge with a different model family than the one under test [[8]](https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias). Few teams do this. It costs nothing to add as a concrete session recommendation.

**A governance note for tool selection:** Promptfoo — the most-starred CI-gating library at ⭐22k and the natural choice for the demo — was acquired by OpenAI in March 2026 [[9]](https://genai.qa/blog/promptfoo-vs-deepeval/). Teams evaluating Anthropic, Llama, or Gemini models should factor vendor alignment into their toolchain; DeepEval (⭐16k, Python/pytest) and Inspect AI (UK AISI, reproducible safety evals) are mature alternatives with independent governance.

**Security is a pre-condition, not a footnote.** Eval pipelines are themselves an attack surface: LLM judges are susceptible to adversarial inputs, prompt injection, and token-level exploits [[10]](https://arxiv.org/pdf/2603.29403). The EU AI Act's high-risk AI provisions take effect August 2026, mandating eval data lineage documentation [[11]](https://atlan.com/know/data-governance/for-ai/). If eval data contains production traces, consent provenance is required before it can legally leave your boundary for a cloud eval service.

**The live demo closes the talk's thesis.** The 3-act arc — vibe check, innocent edit, eval catches it — passes the "I would have done that" test: every developer in the room has shipped a well-intentioned wording change that silently altered behavior elsewhere [[12]](https://futureagi.com/blog/prompt-regression-testing-2026/). Promptfoo with `--cache` keeps the demo deterministic on conference Wi-Fi; a 60-second pre-recorded fallback is the cheapest insurance policy in live demo design [[13]](https://dev.to/measuredco/how-to-do-great-live-demos-and-why-theyre-important-to-get-right-24lc).

The question none of the seven angles fully closes: **how do you know when your rubric has converged?** EvalGen names the paradox — you need criteria to grade outputs, but grading outputs is what reveals the criteria [[14]](https://arxiv.org/abs/2404.12272) — and operationalizes it via human-grading cycles, but the stopping condition remains heuristic. The honest answer for an expert audience: validate TPR/TNR across two annotation rounds on fresh data; if the numbers are stable, you're as converged as you can be without more human labels. Nobody has shipped a better answer yet.
