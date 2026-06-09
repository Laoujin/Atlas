---
title: "Wiring Evals into CI"
date: 2026-06-09
depth: standard
format: md
topic: "Wiring evals into CI"
topic_raw: "Wiring evals into CI"
issue: 206
tags: [evals, ci-cd, llm, testing, github-actions, promptfoo, deepeval, langfuse, regression-testing]
summary: "How to wire LLM evaluations into CI: path-scoped triggers, a layered eval pyramid, statistical delta gates, and a tool comparison across DeepEval, Promptfoo, Langfuse, and Braintrust."
citations: 18
reading_time_min: 7
cover: cover.svg
cost_usd: 1.66
duration_sec: 738
model: "Sonnet 4.6"
---

> **TL;DR** Most CI eval gates are smoke tests — tiny frozen datasets against absolute score floors where noise and signal live in the same range. Fix it with path-scoped triggers so evals run only on relevant changes, a layered eval pyramid (deterministic → LLM-as-judge) so cheap checks run first, and statistical delta gates (mean drop + Welch's t + effect size) instead of absolute floors. [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) [[2]](https://medium.com/@srinib100/your-ci-cd-pipeline-is-your-last-line-of-defence-for-llm-quality-3fef6a86208b)

## Why most CI eval gates don't work

The canonical failure mode: add a `pytest` step, call the LLM, assert average score > 0.7. This gate passes on catastrophic regressions because: [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/) [[3]](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd)

- **Too small:** 10–20 examples — too few for signal to clear LLM judge variance
- **Wrong baseline:** absolute floor without delta comparison — a silent 15% drop stays "passing"
- **Too broad:** runs on every commit, so the team disables it to cut costs
- **Uncalibrated judge:** Pearson r < 0.7 vs human labels → measuring noise, not quality [[4]](https://latitude.so/blog/ultimate-ci-cd-llm-evaluation-guide)

Model providers push silent base-model updates. Knowledge bases drift as they grow. Traffic distributions shift as real users find edge cases your test suite never imagined. [[2]](https://medium.com/@srinib100/your-ci-cd-pipeline-is-your-last-line-of-defence-for-llm-quality-3fef6a86208b) A pre-deploy snapshot gate misses all of this.

## The two-layer architecture

**Layer 1 — Pre-release gate** runs on every relevant PR. Binary: pass or block. Uses your golden dataset. Catches regressions before merge. [[2]](https://medium.com/@srinib100/your-ci-cd-pipeline-is-your-last-line-of-defence-for-llm-quality-3fef6a86208b)

**Layer 2 — Production monitoring** runs the same eval suite continuously on 5–10% of live traffic. Catches drift between releases — the thing a pre-deploy gate cannot catch. [[5]](https://aiworkflowlab.dev/article/llm-evaluation-production-automated-testing-pipelines-catch-failures)

Don't conflate them. Layer 1 without Layer 2 gives false safety; Layer 2 without Layer 1 lets regressions reach users first.

## Path-scoped triggers

Scope the workflow to paths that change model behaviour. [[6]](https://github.com/promptfoo/promptfoo-action) [[7]](https://dev.to/kuldeep_paul/a-practical-guide-to-integrating-ai-evals-into-your-cicd-pipeline-3mlb)

```yaml
on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'evals/**'
      - 'src/agent/**'
      - 'src/tools/**'
```

Add `concurrency.cancel-in-progress: true` keyed to `github.head_ref` so rapid successive pushes cancel stale competing runs rather than queuing them. [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/)

## The eval pyramid

Run cheaper layers first. A failing regex costs microseconds; a failing LLM judge costs tokens and minutes. Safety metrics block on any failure; quality metrics use delta gates. [[4]](https://latitude.so/blog/ultimate-ci-cd-llm-evaluation-guide) [[8]](https://wandb.ai/onlineinference/genai-research/reports/LLM-evaluation-Metrics-frameworks-and-best-practices--VmlldzoxMTMxNjQ4NA)

| Layer         | Examples                                    | Cost   | Block on               |
|---------------|---------------------------------------------|--------|------------------------|
| Deterministic | JSON schema, PII detection, banned phrases  | ~0     | Any failure            |
| Heuristic     | Semantic similarity, regex, length bounds   | Low    | Any failure            |
| LLM-as-judge  | Faithfulness, coherence, rubric scores      | Medium | Statistical delta gate |
| Human review  | Ambiguous cases, high-risk domains          | High   | On human flag          |

## Statistical delta gates

An absolute floor is wrong for LLM-as-judge metrics. Use a three-part test that fires only when all three conditions hold — this prevents judge noise from triggering false alarms: [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/)

1. Mean score dropped below the 7-day rolling baseline
2. Welch's t-test yields p < 0.05
3. Effect size exceeds the noise floor (~0.03 on a 0–1 normalized scale)

Simpler setups: start with an absolute floor plus a delta check. Arize Phoenix's experiments API uses `experiment.get_evaluations()['score'].mean() > 0.8` as the gate and compares against the previous run. [[18]](https://arize.com/blog/how-to-add-llm-evaluations-to-ci-cd-pipelines/) Langfuse's `experiment-action` fails the PR when the score misses a threshold measured against a **versioned** baseline, not an absolute. [[9]](https://langfuse.com/changelog/2026-05-25-experiment-ci-cd-gates)

Threshold calibration: set thresholds so they fail on genuine regressions, not on noise — a threshold that fires constantly provides no signal, while one that never fires provides false confidence. [[4]](https://latitude.so/blog/ultimate-ci-cd-llm-evaluation-guide)

## Tool comparison

Five tools with production CI/CD support, June 2026. [[17]](https://www.braintrust.dev/articles/best-ai-evals-tools-cicd-2025)

| Tool                   | ⭐ Stars | CI integration          | PR comments  | Self-host  | Best for                         |
|------------------------|---------|-------------------------|--------------|------------|----------------------------------|
| [DeepEval][de]         | 16k     | `pytest` native         | via artifact | ✓ free     | pytest-native teams              |
| [Promptfoo][pf]        | 22k     | `promptfoo-action@v1`   | ✓ native     | ✓ free     | YAML-first, red teaming          |
| [Langfuse][lf]         | 28.7k   | `experiment-action@v1`  | ✓ native     | ✓ free     | Prompt management + evals        |
| [Braintrust][bt]       | SaaS    | dedicated GitHub Action | ✓ native     | Enterprise | Experiment tracking, score diffs |
| [Arize Phoenix][ap]    | 10k     | custom Python scripts   | custom       | ✓ free     | Observability-first              |

[de]: https://deepeval.com
[pf]: https://www.promptfoo.dev
[lf]: https://langfuse.com
[bt]: https://braintrust.dev
[ap]: https://phoenix.arize.com

Star counts from GitHub API, June 2026: [[10]](https://github.com/confident-ai/deepeval) [[11]](https://github.com/promptfoo/promptfoo) [[12]](https://github.com/langfuse/langfuse) [[13]](https://github.com/Arize-ai/phoenix)

### DeepEval — pytest integration

`assert_test()` raises an assertion error when a metric falls below its threshold, blocking the CI run. Do **not** use `evaluate()` in CI — that collects results without failing the build. [[3]](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd) [[14]](https://www.confident-ai.com/docs/llm-evaluation/unit-testing-cicd)

```yaml
- name: Run evals
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: poetry run deepeval test run tests/test_llm.py -n 4
```

The `-n 4` flag parallelises across 4 workers. Add `-r 2` to repeat each case twice; combined with a 1/2 minimum-pass assertion this tolerates one flaky-judge result per case.

### Promptfoo — GitHub Action

```yaml
- uses: promptfoo/promptfoo-action@v1     # ⭐ 69 [[6]](https://github.com/promptfoo/promptfoo-action)
  with:
    openai-api-key:    ${{ secrets.OPENAI_API_KEY }}
    github-token:      ${{ secrets.GITHUB_TOKEN }}
    config:            promptfooconfig.yaml
    fail-on-threshold: 90           # block if suite pass rate < 90 %
    repeat:            3            # re-run each case 3×
    repeat-min-pass:   2            # pass if ≥ 2/3 succeed
    cache-path:        .promptfoo-cache
```

Posts a PR comment with pass/fail counts and a link to the web viewer. The `cache-path` integrates with GitHub Actions cache to skip redundant API calls between runs. [[6]](https://github.com/promptfoo/promptfoo-action)

### Langfuse — experiment gate

```yaml
- uses: langfuse/experiment-action@v1.0.0
  with:
    langfuse_public_key: ${{ secrets.LANGFUSE_PUBLIC_KEY }}
    langfuse_secret_key: ${{ secrets.LANGFUSE_SECRET_KEY }}
    langfuse_base_url:   https://cloud.langfuse.com
    github_token:        ${{ secrets.GITHUB_TOKEN }}
    experiment_path:     evals/run_experiment.py
    dataset_name:        golden-v2
    dataset_version:     "2026-05-15T00:00:00Z"
```

Blocks the PR when the experiment score drops below the threshold defined in your experiment script. Every run is tracked in Langfuse for audit trail. [[9]](https://langfuse.com/changelog/2026-05-25-experiment-ci-cd-gates)

## Dataset strategy

Quality beats quantity. Fifty expertly curated examples with clear acceptance criteria outperform 500 auto-generated ones. [[5]](https://aiworkflowlab.dev/article/llm-evaluation-production-automated-testing-pipelines-catch-failures) Build the dataset from: [[7]](https://dev.to/kuldeep_paul/a-practical-guide-to-integrating-ai-evals-into-your-cicd-pipeline-3mlb)

- **Production logs** — tag by difficulty and failure type
- **Domain-expert annotations** — 25–50 human-labeled outcome cases first, before scaling; validate metric alignment at < 5% combined false positive/negative rate [[15]](https://www.confident-ai.com/blog/the-ultimate-llm-evaluation-playbook)
- **Known regressions** — every production failure → permanent test case within 48 hours
- **Adversarial inputs** — edge cases, jailbreaks, multilingual variants

Target 100–200 cases for a blocking gate. Version the dataset alongside prompts in Git so each PR references a specific snapshot. [[4]](https://latitude.so/blog/ultimate-ci-cd-llm-evaluation-guide)

## Judge calibration

Before deploying a judge at CI scale: validate it on your domain. Target Pearson r > 0.7 between judge scores and domain-expert verdicts — below that you're measuring something, but it may not correlate with actual user experience. [[4]](https://latitude.so/blog/ultimate-ci-cd-llm-evaluation-guide)

Start with a capable model (GPT-4o class). Annotate ~50 cases with real-world outcomes, not just expected scores. Once the judge consistently agrees with expert annotations → scale to full dataset runs. [[16]](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

For structured agent output: G-Eval and DeepEval's DAG metric work well. For RAG systems: Faithfulness + Answer Relevancy are the two non-negotiables — Faithfulness catches hallucinations, Answer Relevancy catches off-topic retrievals. [[3]](https://deepeval.com/docs/evaluation-unit-testing-in-ci-cd)

## Closing the loop: canary + production monitoring

Post-merge, route 1–5% of production traffic to the new version. Score both the canary and incumbent populations with the same rubric library. If rolling-mean drift exceeds the calibrated threshold → automatic rollback. [[1]](https://futureagi.com/blog/ci-cd-llm-eval-github-actions-2026/)

Every production failure that reaches users becomes a permanent test case in the golden dataset within 48 hours. This is how the gate becomes progressively harder to fool — CI evals are not a checkpoint, they're a flywheel. [[5]](https://aiworkflowlab.dev/article/llm-evaluation-production-automated-testing-pipelines-catch-failures) [[7]](https://dev.to/kuldeep_paul/a-practical-guide-to-integrating-ai-evals-into-your-cicd-pipeline-3mlb)
