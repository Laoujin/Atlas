---
title: "\"I Don't Know\" Guardrail for RAG Systems"
date: 2026-06-09
depth: standard
format: md
topic: "\"I don't know\" guardrail"
topic_raw: "\"I don't know\" guardrail"
issue: 207
tags: [rag, guardrails, hallucination, abstention, faithfulness, llm]
summary: "How to make a RAG pipeline say 'I don't know' instead of hallucinating — prompt patterns, retrieval thresholds, output-scoring rails, and evaluation metrics."
citations: 16
reading_time_min: 5
model: "claude-sonnet-4-6"
cost_usd: "sub"
cover: cover.svg
cost_usd: 1.82
duration_sec: 565
model: "Sonnet 4.6"
---

> **TL;DR** Abstaining is always cheaper than hallucinating: the [CRAG benchmark](https://arxiv.org/html/2406.04744v1) scores "I don't know" at 0 and wrong answers at −1. [[1]](https://arxiv.org/html/2406.04744v1) Stack the guardrail in four layers — prompt instruction, retrieval threshold, faithfulness scorer, and a dedicated rails framework — and monitor faithfulness ≥ 0.75 in production. [[9]](https://nandigamharikrishna.substack.com/p/how-to-evaluate-rag-systems-accurately)

---

## Why abstention beats hallucination

The CRAG benchmark's scoring formula makes the math explicit: correct = +1, "I don't know" = 0, wrong = −1. [[1]](https://arxiv.org/html/2406.04744v1) GPT-4 Turbo in that evaluation hallucinates 13.5% of the time but abstains 53% — trading some recall for far fewer −1 penalties. Llama 3 70B hallucinates 28.9%, paying a heavier price.

The core problem: RAG models generate confident answers even when retrieved documents don't support them. [[7]](https://arxiv.org/pdf/2509.01476) High confidence frequently accompanies hallucinated answers, making confidence alone an unreliable signal.

---

## Layer 1 — Prompt instruction (zero cost)

The cheapest guardrail is a system-prompt constraint. Every production RAG template should include a line like: [[3]](https://www.stackai.com/blog/prompt-engineering-for-rag-pipelines-the-complete-guide-to-prompt-engineering-for-retrieval-augmented-generation)

```
Use only the context retrieved below.
If the answer is not present, reply:
"I cannot find this information in the available documents."
Do NOT combine context with your training knowledge.
Do NOT provide partial answers.
```

**Add few-shot examples.** Prompt-only instructions fail at edge cases; few-shot examples of pass/fail scenarios substantially outperform instruction text alone. [[4]](https://www.qed42.com/insights/building-simple-effective-prompt-based-guardrails) Use a two-tier approach: generate examples with a capable model (GPT-4o, Claude Opus), deploy with a cheaper classifier (GPT-4o-mini, Claude Haiku).

**Add a reasoning block.** Force the model to output its reasoning before the answer. The structure: `<reasoning>` → `<response>` → `<gate: pass|fail>`. [[4]](https://www.qed42.com/insights/building-simple-effective-prompt-based-guardrails) Reasoning prevents arbitrary gate decisions and gives you an audit trail.

---

## Layer 2 — Retrieval threshold

Set a minimum cosine-similarity cutoff between the query and retrieved chunks. If no chunk clears the threshold, return "I don't know" before the LLM is called at all — zero generation cost, zero hallucination risk.

Calibration matters: too high a threshold → excessive abstention; too low → irrelevant context still reaches the model. [[7]](https://arxiv.org/pdf/2509.01476) Tune on a held-out set with Expected Calibration Error (ECE) as the metric.

The [KnowOrNot](https://github.com/govtech-responsibleai/KnowOrNot) ⭐ 28 library provides a systematic evaluation framework for out-of-knowledge-base (OOKB) robustness — build a PolicyBench-style split with in-scope and out-of-scope questions and run it against candidate thresholds. [[6]](https://arxiv.org/pdf/2505.13545) [[16]](https://github.com/govtech-responsibleai/KnowOrNot)

---

## Layer 3 — Output faithfulness scoring

Post-generation, score the answer against the retrieved context before returning it to the user.

### NeMo Guardrails self-check

[NeMo-Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) ⭐ 6.4k (Jun 2026) ships a `self_check_facts` output rail: [[5]](https://docs.nvidia.com/nemo/guardrails/latest/configure-rails/guardrail-catalog/fact-checking.html) [[13]](https://github.com/NVIDIA/NeMo-Guardrails)

```yaml
# config.yml
rails:
  output:
    flows:
      - self check facts
```

It scores the response against `$relevant_chunks` on a 0–1 scale. Responses below **0.5** are blocked and replaced with the fallback: `"I don't know the answer to that."` Trigger selectively with `$check_facts = True` on high-stakes queries to control latency. Combined with Patronus AI's Lynx model, NeMo achieves 97% hallucination detection at under 200 ms. [[5]](https://docs.nvidia.com/nemo/guardrails/latest/configure-rails/guardrail-catalog/fact-checking.html)

### RAGAS faithfulness metric

[RAGAS](https://github.com/explodinggradients/ragas) ⭐ 14.3k (Jun 2026) decomposes each answer into individual statements and checks each against retrieved chunks. [[15]](https://github.com/explodinggradients/ragas) A score of 0.6 means 40% of statements have no grounding — those are hallucinations by definition. [[9]](https://nandigamharikrishna.substack.com/p/how-to-evaluate-rag-systems-accurately) Use RAGAS in CI/CD gates; TruLens or Langfuse for production dashboards. [[10]](https://helpmetest.com/blog/evaluating-rag-with-ragas-trulens/)

### Span-level verification

The most precise approach: each generated claim is matched against a specific evidence span, and unsupported claims are flagged inline. [[2]](https://www.lakera.ai/blog/guide-to-hallucinations-in-large-language-models) More expensive but auditable — users see exactly which statements are grounded.

---

## Layer 4 — Dedicated guardrail frameworks

Two open-source options dominate: [NeMo-Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) ⭐ 6.4k [[13]] for pipeline-integrated fact-checking, and [Guardrails AI](https://github.com/guardrails-ai/guardrails) ⭐ 7.0k [[14]] for RAIL-spec validators that constrain output structure and content.

| Framework                                                  | Stars   | Abstention mechanism                              | Latency |
| ---------------------------------------------------------- | ------- | ------------------------------------------------- | ------- |
| [NeMo-Guardrails][ng]                                      | ⭐ 6.4k  | `self_check_facts` output rail, score < 0.5 block | < 200ms |
| [Guardrails AI][ga]                                        | ⭐ 7.0k  | RAIL spec validators; custom hallucination checks | varies  |
| [RAGAS][rg] (eval)                                         | ⭐ 14.3k | faithfulness metric for CI/CD gates               | offline |
| [KnowOrNot][kon]                                           | ⭐ 28    | OOKB robustness eval framework + PolicyBench      | offline |

[ng]: https://github.com/NVIDIA/NeMo-Guardrails
[ga]: https://github.com/guardrails-ai/guardrails
[rg]: https://github.com/explodinggradients/ragas
[kon]: https://github.com/govtech-responsibleai/KnowOrNot

---

## Evaluation & production monitoring

**Offline (CI/CD):** Run RAGAS faithfulness on a golden eval set at every merge. Gate on faithfulness ≥ 0.75, answer relevancy ≥ 0.8. [[9]](https://nandigamharikrishna.substack.com/p/how-to-evaluate-rag-systems-accurately)

**Online (production):** Sample 5–10% of live queries; log faithfulness and answer relevancy to TruLens or Langfuse; alert when the 7-day rolling faithfulness drops below 0.75. [[10]](https://helpmetest.com/blog/evaluating-rag-with-ragas-trulens/)

**Layered impact (estimated):**

| Guardrail combination                           | Hallucination risk reduction |
| ----------------------------------------------- | ---------------------------- |
| Prompt instruction only                         | ~31%                         |
| Prompt + retrieval threshold                    | ~52%                         |
| Prompt + threshold + faithfulness scorer        | ~68%                         |
| Full stack (all layers + human escalation path) | 71–89%                       |

[[8]](https://swiftflutter.com/reducing-ai-hallucinations-12-guardrails-that-cut-risk-immediately)

---

## The over-refusal trade-off

Aggressive guardrails create a new failure mode: over-refusal, where the system rejects answerable questions. GPT-4 Turbo's 53% abstention rate in CRAG is too high — it damages utility while chasing safety. [[1]](https://arxiv.org/html/2406.04744v1)

Calibrate by weighting **false positives** (blocked valid queries) more heavily than false negatives (allowed edge cases) when tuning thresholds — frustrated users from blocked legitimate queries erode trust faster than occasional hallucinations. [[4]](https://www.qed42.com/insights/building-simple-effective-prompt-based-guardrails)

Monitor both directions: low faithfulness → too many hallucinations; high abstention rate → over-refusal.

---

## Research frontiers (beyond prompt engineering)

**RL-based intellectual humility.** Training models with reinforcement learning to reward appropriate abstention improves calibration but risks reducing accuracy on answerable questions. [[11]](https://arxiv.org/pdf/2601.20126) Models as small as Qwen 3-4B can learn abstention behaviors with targeted RL fine-tuning.

**Three-action epistemic framework.** [PassiveQA](https://github.com/MadsDoodle/PassiveQA) [[12]](https://arxiv.org/pdf/2604.04565) extends binary answer/refuse into: **answer** / **abstain** / **clarify** — requesting context when the question is ambiguous rather than refusing outright. Finetuned via LoRA on SHARC, QuAC, and HotpotQA.

**Activation probing (CLAP).** Train lightweight classifiers on model internal activations to flag hallucinations in real time without a separate scoring LLM call — relevant when latency budgets preclude a second model pass. [[2]](https://www.lakera.ai/blog/guide-to-hallucinations-in-large-language-models)
