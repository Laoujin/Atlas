---
title: "Wiring LLM Evals into CI/CD: gates, flaky judges, and cost budgets (2026)"
date: 2026-06-04
depth: standard
format: md
model: "Opus 4.8"
duration_sec: 246
cost_usd: "sub"
topic: "Wiring LLM/AI evals into CI/CD in 2026 — eval suites in pipelines (GitHub Actions and similar), regression gates and pass/fail thresholds, flaky LLM-as-judge results, cost and latency budgets per CI run, caching and sampling, block vs warn, and concrete patterns from Promptfoo, Braintrust, DeepEval/LangSmith"
topic_raw: "Wiring LLM/AI evals into CI/CD in 2026 — running eval suites in pipelines (GitHub Actions and similar), regression gates and pass/fail thresholds, handling flaky/nondeterministic LLM-as-judge results, cost and latency budgets per CI run, caching and sampling strategies, when to block the build vs warn, and concrete patterns/examples from Promptfoo, Braintrust, DeepEval/LangSmith CI integrations"
tags: [evals, ci-cd, llm, github-actions, promptfoo, braintrust, deepeval, langsmith, regression-testing]
summary: "How to run LLM eval suites in pipelines in 2026: deterministic-gates-the-judge, statistical regression gates, cost/latency budgets, caching/sampling, and concrete Promptfoo/Braintrust/DeepEval/LangSmith wiring."
citations: 13
reading_time_min: 9
---

> **Decision.** Wire evals as a **three-tier cascade** that runs cheapest-first: deterministic checks (schema/regex/exact-match, sub-ms, $0) gate a fine-tuned classifier, which gates a frontier LLM judge that only fires on the residual ambiguous sample [[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/)[[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/). **Block the PR** only on deterministic failures and on statistically-significant judge regressions (delta past a noise floor *and* p < 0.05); **warn** on everything inside the noise band [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/). Budget cents-per-PR by scoping to changed routes and caching LLM calls; reserve the full multi-thousand-example sweep for a nightly job, because a naive judge-on-everything PR gate can burn **$250–$2,500/run** on a 5k-example set [[14]](https://galileo.ai/blog/best-low-latency-llm-evaluation-tools). Tooling: **Promptfoo** for declarative prompt gates, **DeepEval** for pytest-native unit tests, **Braintrust/LangSmith** for hosted experiment diffs.

## The core problem: a judge in CI is a flaky test by construction

An LLM-as-judge call costs **5–50¢** and takes **100ms–3s** [[14]](https://galileo.ai/blog/best-low-latency-llm-evaluation-tools), and its verdict varies run-to-run. Treat each CI run as standalone and "you can't tell a noise-floor flake from a real regression" [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/). The 2026 consensus is **not** to pretend the judge is deterministic, but to design for variance: control judge temperature, rerun borderline cases, ensemble only high-impact decisions, and smooth scores over time [[3]](https://montecarlo.ai/blog-llm-as-judge/)[[8]](https://www.braintrust.dev/articles/what-is-llm-as-a-judge). A 30-example set yields confidence intervals of roughly **±0.07** on a 0–1 scale, so a 2-point drop is inside the noise; you need **100–200 examples per route** for a t-test to separate signal from variance [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).

## Pattern 1 — Deterministic gates the judge (the eval floor)

The cheapest and highest-signal layer is deterministic and runs first; the judge never fires on structurally-broken output [[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/).

| Tier | Checks | Latency | Cost | Role |
|------------------|----------------------------------------------------------------|-----------|--------------|----------------------------------|
| 1 Deterministic  | JSON schema, regex, exact-match, length contract, citation-presence, function-call arg validators | sub-ms    | $0           | Fail-fast floor; gates tiers 2–3 |
| 2 NLI classifier | faithfulness, claim_support, factual_consistency on CPU        | 10–50ms   | ~$0.001/call | Triage; routes ambiguous → tier 3 |
| 3 Frontier judge | open-ended rubrics (helpfulness, tone, correctness)            | 100ms–3s  | 5–50¢/call   | Only on classifier disagreement  |

Sources: [[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/) [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) [[14]](https://galileo.ai/blog/best-low-latency-llm-evaluation-tools)

Function-call argument validation is "the single highest-signal deterministic check for agents" [[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/). **Fail-fast composition:** if the response fails JSON schema, the judge does not run and the eval fails outright [[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/). Deterministic checks alone catch **30–60%** of production failures before any judge fires [[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/). The reported effect: PR-gate cost drops from ~$27 (200 examples × 9 rubrics × $0.015) to **$0.30–$0.60** [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/). ⚠ Don't apply the cascade to subjective axes (helpfulness, brand voice) where the classifier has no ground truth [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).

## Pattern 2 — Statistical regression gates, not frozen thresholds

A single absolute threshold ("fail if score < 0.8") flaps on judge noise. The 2026 pattern keeps a **rolling baseline in git** and gates on a statistical delta [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).

- A **nightly** workflow runs the full suite (500–2,000 examples) and commits updated per-rubric mean arrays back to `evals/baselines/*.json` — calibrating against production variance, not "frozen fiction" [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).
- The PR gate fires **only when all three hold**: mean dropped (`delta < 0`), change is significant (`p < 0.05` via Welch's t-test on per-example score arrays), and effect exceeds the noise floor (`|delta| >= 0.03`) [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/). Example failure: `regression: delta=-0.045, p=0.018` [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).
- Commit the **rolling 7-day** result JSON to git so a run can compare against recent history rather than a single noisy point [[3]](https://montecarlo.ai/blog-llm-as-judge/)[[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).

**Exit-code contract** keeps CI policy stable against SDK log changes — partition outcomes by code rather than grepping stdout [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/):

| Code | Meaning          | CI action                 |
|------|------------------|---------------------------|
| 0    | Pass             | Merge allowed             |
| 2    | Assertion failed | Hard-fail PR (block)      |
| 3    | Warning (--strict) | Slack notify, don't block |
| 6    | API error        | Retry with backoff        |
| 7    | Timeout          | Increase `timeout-minutes` |

Source: [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/)

## When to block vs warn

| Situation | Verdict | Why |
|-----------------------------------------------------|---------|-----------------------------------------------|
| Deterministic check fails (schema, forbidden phrase, PII, bad tool args) | **Block** | Objective, zero false-positive, cheap [[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/) |
| Safety/red-team assertion fails                     | **Block** | Non-negotiable; Promptfoo runs red-team in CI [[10]](https://github.com/promptfoo/promptfoo) |
| Judge delta significant + past noise floor          | **Block** | Real regression, not flake [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) |
| Judge delta inside noise band / single-run drop     | **Warn**  | Indistinguishable from judge variance [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) |
| Subjective axis (tone, helpfulness) small move      | **Warn**  | Smooth + monitor over time, don't hard-gate [[3]](https://montecarlo.ai/blog-llm-as-judge/) |
| API/timeout error in the eval harness               | Retry, then **warn** | Infra noise ≠ quality regression [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) |

Evals belong in CI **and** in production: run the same judge-based scorers in CI and against live traffic so version-to-version score comparisons stay meaningful [[3]](https://montecarlo.ai/blog-llm-as-judge/). Post-merge, route 1–5% of traffic to the new prompt (canary), score both populations with the same rubric library, and auto-rollback on a **2–3pp drift sustained over 15–60 min** [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).

## Cost & latency budgets per CI run

| Lever | Mechanism | Effect |
|---------------------|-----------------------------------------------------------------|------------------------------------------|
| Per-route scoping   | Matrix-shard by changed paths; fall back to full sweep only if shared paths (`src/shared/`, `evals/rubrics/`) touched | Bounds PR cost; full 1,600-example sweep stays in nightly [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) |
| Cascade / sampling  | Classifier first; judge on 30–60 ambiguous cases not 200        | 70–85% cost cut [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) |
| Caching LLM calls   | Reuse request/output across runs; Promptfoo `~/.cache/promptfoo`, Braintrust proxy `use_proxy` | Re-run unchanged tests ~free [[9]](https://www.promptfoo.dev/docs/integrations/github-action/)[[2]](https://github.com/braintrustdata/eval-action) |
| Concurrency cancel  | Cancel superseded PR runs; sub-5-min verdict target            | Keeps feedback loop tight [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) |

Reference figures: a tuned PR gate hit **4 min, $3.20**, covering 247 judge calls across 9 rubrics on 200 examples (~$0.20 deterministic+NLI, ~$3.00 frontier subset); the nightly 2,000-example run amortizes at **~$20–$30** [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/). The anti-pattern to avoid: judge-on-every-case across a 5,000-example regression set runs **$250–$2,500 per CI run** [[14]](https://galileo.ai/blog/best-low-latency-llm-evaluation-tools). On the latency side, a judge adds 1,000ms+ and can double response time, which is why the judge ships off the hot path as a span-attached eval rather than inline [[14]](https://galileo.ai/blog/best-low-latency-llm-evaluation-tools)[[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/).

## Concrete tool wiring

### Promptfoo — declarative prompt/red-team gate
[promptfoo](https://www.promptfoo.dev) ⭐ 22k (Jun 2026) [[10]](https://github.com/promptfoo/promptfoo) ships [promptfoo-action](https://github.com/promptfoo/promptfoo-action) ⭐ 69 (Jun 2026) [[7]](https://github.com/promptfoo/promptfoo-action). On a PR touching `prompts/**`, it runs a before/after eval and posts a comparison comment linking the web viewer [[9]](https://www.promptfoo.dev/docs/integrations/github-action/). Key inputs: `github-token`, `prompts` glob, `config`, `cache-path` [[9]](https://www.promptfoo.dev/docs/integrations/github-action/). Gating is either built-in (`promptfoo eval --fail-on-error`) or a jq quality-gate on the JSON output [[4]](https://www.promptfoo.dev/docs/integrations/ci-cd/):

```bash
PASS_RATE=$(jq '.results.stats.successes / (.results.stats.successes + .results.stats.failures) * 100' results.json)
if (( $(echo "$PASS_RATE < 95" | bc -l) )); then exit 1; fi
```

Output `results.junit.xml` for native CI viewers; cache via `PROMPTFOO_CACHE_PATH=~/.cache/promptfoo` + `PROMPTFOO_CACHE_TTL=86400` and `actions/cache@v4` keyed on `hashFiles('prompts/**','promptfooconfig.yaml')` [[4]](https://www.promptfoo.dev/docs/integrations/ci-cd/). Assertions mix deterministic and `llm-rubric` (model-graded) types in one declarative config [[4]](https://www.promptfoo.dev/docs/integrations/ci-cd/). Used by OpenAI and Anthropic internally [[10]](https://github.com/promptfoo/promptfoo).

### DeepEval — pytest-native unit tests
[deepeval](https://deepeval.com) ⭐ 16k (Jun 2026) [[11]](https://github.com/confident-ai/deepeval) wraps pytest: `deepeval test run test_llm_app.py`, with each test calling `assert_test(test_case, metrics=[...])` where metrics carry a per-metric threshold [[12]](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd). The command adds flags on top of pytest: `-n` (parallel processes), `-r` (repeats — rerun for variance), `-c` (cache), `-i` (ignore errors) [[12]](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd). In GitHub Actions it runs under `OPENAI_API_KEY` (judge) with optional `CONFIDENT_API_KEY` to ship results to the Confident AI platform; a metric below threshold fails the test → fails the job → blocks the PR [[12]](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd).

### Braintrust — hosted experiment diff
[braintrust eval-action](https://github.com/braintrustdata/eval-action) ⭐ 15 (Jun 2026) runs `braintrust eval` and posts a PR comment with baseline-relative scores like `0.83 (+3pp)`, flagging 🟢 improvements / 🔴 regressions [[2]](https://github.com/braintrustdata/eval-action). Inputs: `api_key`, `runtime` (`node`/`python`), `package_manager`, `use_proxy` (defaults true — sets `OPENAI_BASE_URL` to cache LLM calls), `terminate_on_failure` [[2]](https://github.com/braintrustdata/eval-action). Requires `pull-requests: write` + `contents: read` permissions to comment [[2]](https://github.com/braintrustdata/eval-action). Thresholds live in the eval code / project settings, not as action inputs; the action blocks merges when scores fall below them [[8]](https://www.braintrust.dev/articles/what-is-llm-as-a-judge).

### LangSmith — pytest/Vitest + hosted experiments
LangSmith's [evals-cicd sample](https://github.com/langchain-samples/evals-cicd/) runs `pytest -m evaluator`, calls `client.aevaluate()` against a hosted dataset with OpenEvals LLM-as-judge, and gates on a `criteria` dict like `"correctness": ">=0.8"` [[13]](https://github.com/langchain-samples/evals-cicd/). A failed threshold → pytest failure → job failure → blocked PR; `sys.exit(1)` in the eval script is all that's needed to fail the Action [[13]](https://github.com/langchain-samples/evals-cicd/). CI runs surface in the LangSmith UI under Experiments (grouped by a `ci-regression` prefix) for side-by-side run-over-run diffs [[13]](https://github.com/langchain-samples/evals-cicd/).

## Tool pick

| If you want… | Use | Notes |
|----------------------------------------------|---------------|--------------------------------------------------|
| Declarative prompt/RAG/red-team gate, no SDK | **Promptfoo** ⭐ 22k | YAML config, `--fail-on-error`, built-in caching [[10]](https://github.com/promptfoo/promptfoo)[[9]](https://www.promptfoo.dev/docs/integrations/github-action/) |
| pytest-native unit tests in an existing suite | **DeepEval** ⭐ 16k | `assert_test` + per-metric thresholds, `-r` repeats [[11]](https://github.com/confident-ai/deepeval)[[12]](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd) |
| Hosted experiment diffs + team dashboards    | **Braintrust** | PR comment with ±pp deltas, proxy caching [[2]](https://github.com/braintrustdata/eval-action) |
| Already on LangChain/LangSmith tracing       | **LangSmith** ⭐ 0.9k | `aevaluate()` + pytest, Experiments diff UI [[13]](https://github.com/langchain-samples/evals-cicd/) |

[langsmith-sdk](https://github.com/langchain-ai/langsmith-sdk) ⭐ 917 (Jun 2026) [[13]](https://github.com/langchain-samples/evals-cicd/).

## Workshop-ready takeaways

1. Layer deterministic → classifier → judge; **fail-fast** so the judge never scores broken output [[6]](https://futureagi.com/blog/deterministic-llm-evaluation-metrics-2026/).
2. Gate on a **statistical delta vs a git-committed rolling baseline**, not a frozen number; need 100–200 examples/route for the t-test [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).
3. **Block** deterministic + safety + significant judge regressions; **warn** on noise-band moves and subjective axes [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/)[[3]](https://montecarlo.ai/blog-llm-as-judge/).
4. Budget with **per-route scoping + cascade + LLM-call caching**; keep PR cost in cents and push the full sweep to a nightly job [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).
5. Use a stable **exit-code contract** so CI policy survives SDK output churn [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/).
