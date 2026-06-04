---
title: "Agent & RAG Evals in 2026: Trajectories, Tool-Use, and Ragas Metrics"
date: 2026-06-04
depth: standard
format: md
model: "Opus 4.8"
duration_sec: 246
cost_usd: "sub"
topic: "Evaluating agents and RAG systems specifically in 2026 — multi-step/trajectory evaluation, tool-use/function-call correctness, agentic-loop success metrics, and RAG metrics (faithfulness, answer relevancy, context precision/recall as in Ragas), component-level vs end-to-end evaluation, building eval datasets for agents/RAG, and the failure modes these catch that single-turn evals miss"
topic_raw: "Evaluating agents and RAG systems specifically in 2026 — multi-step/trajectory evaluation, tool-use/function-call correctness, agentic-loop success metrics, and RAG metrics (faithfulness, answer relevancy, context precision/recall as in Ragas), component-level vs end-to-end evaluation, building eval datasets for agents/RAG, and the failure modes these catch that single-turn evals miss"
tags: [evals, agents, rag, ragas, tool-use, llm-as-judge, trajectory-evaluation]
summary: "Why single-turn evals miss agent/RAG failures, and the 2026 metric stack — trajectory + tool-use correctness, pass^k reliability, and Ragas-style RAG decomposition — that catches them."
citations: 15
reading_time_min: 8
---

> **Decision (workshop spine).** A single-turn "is the final answer good?" eval is the wrong instrument for agents and RAG. Build a **three-layer diagnostic stack**: end-to-end outcome → trajectory/path → failing component, each with its own metric and dataset [[1]](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide)[[6]](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide). For **agents**, grade the *path* (tool correctness, argument correctness, step efficiency) and measure *reliability with `pass^k`*, not just `pass@1` — a 90%-success agent is only 57% consistent over 8 runs [[7]](https://medium.com/alan/benchmarking-ai-agents-stop-trusting-headline-scores-start-measuring-trade-offs-0fdae3a418cf). For **RAG**, decompose into Ragas-style faithfulness / answer relevancy / context precision / context recall so a regression points at *retriever vs generator* [[2]](https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026)[[3]](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/). Calibrate every LLM-judge against human labels — frontier judges exceed 50% error on bias stress-tests [[8]](https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias).

## Why single-turn evals are the wrong tool here

A single-turn eval scores `input → output`. Agents and RAG are not single-turn systems: they have **trajectories, internal state, tool calls, and failure modes that unfold over time** [[4]](https://medium.com/@ai_91339/evaluating-multi-agent-systems-719a9a550ddf). Output-only scoring is blind to a specific, recurring set of failures [[6]](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide):

| Failure mode | What single-turn eval sees | What actually happened |
|---|---|---|
| **Ghost action** | Plausible "Done, I booked it." | Agent never called the booking tool; nothing changed downstream [[6]][6] |
| **Confident fabrication** | Polished, on-topic answer | Built on stale/hallucinated intermediate data [[6]][6] |
| **Interrogation loop** | Final answer eventually correct | Re-asked for info the user gave 3 turns ago [[6]][6] |
| **Budget burning** | Correct answer | 14 model completions instead of 2 → 10× cost/latency [[6]][6] |
| **Inconsistency** | One green run | Fails 1-in-2 reruns of the *same* task [[7]][7] |

[6]: https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide
[7]: https://medium.com/alan/benchmarking-ai-agents-stop-trusting-headline-scores-start-measuring-trade-offs-0fdae3a418cf

The benchmark evidence is blunt: **single-turn evaluations fail to capture agent failures that emerge across multi-step trajectories**, and failure rates climb with trajectory length, tool-selection timing, and argument construction — three modes that only surface across an action *sequence* [[5]](https://arxiv.org/pdf/2510.04550).

## The three-layer diagnostic stack

These layers form a stack: **outcome first, then path, then failing component** — when the end-to-end score drops, component scores reveal where it originated [[1]](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide). Put **component checks at tool-call spans, end-to-end checks at the root trace** [[6]](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide).

| Layer | Question | Agent metric | RAG metric |
|---|---|---|---|
| **End-to-end** | Did the task succeed? | Task Completion (LLM-judged, infers goal from input) [[1]][1] | Answer relevancy, end-to-end faithfulness [[3]][3] |
| **Trajectory / path** | Was the path right & efficient? | Tool Correctness, Step Efficiency, Plan Adherence [[1]][1] | (n/a — RAG path is the retrieve→generate spans below) |
| **Component** | Which part broke? | Argument Correctness, Handoff Correctness (per span) [[6]][6] | Context precision/recall (retriever), faithfulness (generator) [[2]][2] |

[1]: https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide
[2]: https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026
[3]: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
[6]: https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide

Key distinction for scoring fairness: **separate agent failure from infrastructure failure**. A tool timing out on a connection is *not* the agent's fault; the agent failing to call the tool, or calling it with wrong parameters, *is* [[4]](https://medium.com/@ai_91339/evaluating-multi-agent-systems-719a9a550ddf).

## Agent metrics: grade the path, not just the answer

Definitions that matter in a workshop, with whether each is deterministic or LLM-judged [[1]](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide):

| Metric | What it checks | Type |
|---|---|---|
| **Tool Correctness** | Were the *right* tools called? (selection + I/O) | Deterministic [[1]][1] |
| **Argument Correctness** | Right parameters into each tool, scored *per call* | Deterministic [[1]][1] |
| **Step Efficiency** | No redundant retries, loops, wasted calls | Deterministic or LLM-judged [[1]][1] |
| **Task Completion** | Goal inferred from input, then reasoning+tools+output graded | LLM-judged [[1]][1] |
| **Plan Adherence** | Did execution follow the intended plan/constraints? | LLM-judged [[1]][1] |

[1]: https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide

The data layer under all of this is **traces**: every span (retrieval, tool call, handoff, generation) with inputs, outputs, latency, and cost. Traces enable failure attribution to a specific span and surface unanticipated failure modes *before* you've written a formal metric for them [[1]](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide).

### Reliability: `pass^k`, not `pass@1`

The single most important 2026 framing for an agent talk. `pass@1` (or `pass@k` = "at least one of k succeeded") rewards lucky single runs. τ-bench introduced **`pass^k` = "all k attempts succeeded"**, which decays as `p^k` [[7]](https://medium.com/alan/benchmarking-ai-agents-stop-trusting-headline-scores-start-measuring-trade-offs-0fdae3a418cf):

- 90% per-run success → **57%** consistency at k=8 [[7]][7]
- On τ-bench retail, even strong function-calling agents score **`pass^8` < 25%** [[7]][7]

[7]: https://medium.com/alan/benchmarking-ai-agents-stop-trusting-headline-scores-start-measuring-trade-offs-0fdae3a418cf

Workshop takeaway: **run each eval case N times and report the all-pass rate.** A green CI run from a single execution is reliability theatre. [sierra-research/tau-bench](https://github.com/sierra-research/tau-bench) ⭐ 1.2k (Jun 2026) is the canonical tool-agent-user benchmark; its 2026 `tau2-bench` update adds voice + knowledge-retrieval domains and a dual-control framework [[7]][7].

[7]: https://medium.com/alan/benchmarking-ai-agents-stop-trusting-headline-scores-start-measuring-trade-offs-0fdae3a418cf

## RAG metrics: decompose so the regression names its own cause

The four Ragas-lineage metrics, with **2026 production thresholds** and the subsystem each indicts [[2]](https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026)[[3]](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/):

| Metric | Measures | Subsystem | Target |
|---|---|---|---|
| **Context Recall** | Did retrieval surface all relevant chunks? | Retriever [[2]][2] | ≥0.90 @ k=10 [[2]][2] |
| **Context Precision** | What fraction of retrieved chunks were useful? | Retriever (noise) [[2]][2] | ≥0.45 @ k=10 [[2]][2] |
| **Faithfulness** | Do answer claims trace to retrieved context? | Generator [[2]][2] | ≥0.90; unsafe <0.70 [[2]][2] |
| **Answer Relevancy** | Is the answer on-point for the query? | Generator/end-to-end [[3]][3] | ≥0.80 [[2]][2] |

[2]: https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026
[3]: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/

**How faithfulness is computed** (worth demoing): an LLM judge **decomposes the answer into atomic claims**, then checks whether retrieved context *supports / contradicts / is silent on* each; score = supported-claim fraction [[2]](https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026).

**Diagnostic logic** — the payoff of decomposition [[2]](https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026):

- Recall drops → retrieval problem (chunking, embedding drift, index degradation)
- Faithfulness drops, citation accuracy holds → generation/prompt issue
- Citation accuracy drops, faithfulness holds → citation-parsing/prompt-enforcement bug

This is what an opaque "the answer was bad" score can never tell you [[2]](https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026).

### Tooling

| Tool | Stars | Niche |
|---|---|---|
| [Ragas](https://github.com/explodinggradients/ragas) | ⭐ 14k | RAG metric reference impl; faithfulness/relevancy/precision/recall; LangChain/LlamaIndex native [[3]][3] |
| [DeepEval](https://github.com/confident-ai/deepeval) | ⭐ 16k | 50+ first-party agent metrics (Tool/Argument Correctness, Plan Adherence) + RAG; pytest-style [[1]][1] |
| [Opik](https://github.com/comet-ml/opik) | ⭐ 19k | Traces + evals + CI gating, self-hostable |
| [Phoenix](https://github.com/Arize-ai/phoenix) | ⭐ 10k | OpenInference tracing + eval, OTel-based |

[1]: https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide
[3]: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/

## LLM-as-judge: the grader is itself untrustworthy until calibrated

Most of the metrics above are LLM-judged, so judge reliability is load-bearing. Judges agree with humans ~85% of the time (higher than two humans agree), yet on bias stress-tests **frontier models exceed 50% error rates** [[8]](https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias). Five named biases to flag in a talk [[8]](https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias):

| Bias | Effect |
|---|---|
| **Position** | Slot A wins 10–15 pts more in pairwise [[8]][8] |
| **Verbosity** | Longer answers score higher at equal quality [[8]][8] |
| **Self-preference** | Judges score own model family 10–25% higher [[8]][8] |
| **Format** | Formatting/markdown sways the score [[8]][8] |
| **Calibration drift** | Same rubric, different distribution after a judge-model update [[8]][8] |

[8]: https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias

Mitigation: **calibrate the judge on a held-out set of human labels and track disagreement** — "otherwise you never audit the grader." Disagreements signal rubric gaps, not just model variance [[6]](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide).

## Building the eval dataset (the part teams skip)

You can't run any of the above without a dataset of cases. The 2026 default pattern: **synthetic + sampled production + human calibration, all against one metric set** [[9]](https://developers.redhat.com/articles/2026/02/23/synthetic-data-rag-evaluation-why-your-rag-system-needs-better-testing).

- **RAG:** a synthetic set is `(question, retrieved-context, ground-truth-answer)` triples, machine-generated — the default way to build RAG test sets at scale because it removes expert-annotation bottlenecks in niche/regulated domains [[9]](https://developers.redhat.com/articles/2026/02/23/synthetic-data-rag-evaluation-why-your-rag-system-needs-better-testing). Ragas ships test-set generation for exactly these triples [[3]](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/).
- **Agents:** domain experts author **"must-pass" scenarios with explicit acceptance criteria** as anchor tests; target each known failure mode directly (e.g. for a booking agent, assert the booking API was *actually invoked*, not that the reply sounds plausible) [[6]](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide)[[10]](https://www.getmaxim.ai/articles/building-a-golden-dataset-for-ai-evaluation-a-step-by-step-guide/).
- **Close the loop:** convert every production incident into a new golden so the regression is caught in CI next time [[6]](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide).

### CI / regression workflow (stacked gates)

1. **CI on every change** — automated metrics + *operating envelopes*: max steps, token budgets, wall-clock timeouts. **Fail the run when quality is fine but economics/latency are not** [[6]](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide).
2. **Pre-release** — human review of a fixed sample after any prompt/model change, focused on high-risk intents [[6]][6].
3. **Production** — monitor traces; audit flagged sessions (errors, complaints, metric drops) [[6]][6].

[6]: https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide

## Workshop / talk hooks

- **Live demo:** show the *same* RAG answer scoring high on answer-relevancy but low on faithfulness — then trace it to a stale retrieved chunk. Makes "decompose or stay blind" visceral [[2]](https://www.digitalapplied.com/blog/rag-system-metrics-recall-precision-faithfulness-2026).
- **The `pass^k` reveal:** run one agent task 8× live; watch a "90% agent" fail twice. Anchors why reliability ≠ accuracy [[7]](https://medium.com/alan/benchmarking-ai-agents-stop-trusting-headline-scores-start-measuring-trade-offs-0fdae3a418cf).
- **Ghost-action trap:** an agent that says "refund processed" with no tool call in the trace — the one-slide case for trace-based, component-level evals [[6]](https://www.confident-ai.com/blog/definitive-ai-agent-evaluation-guide).
- **Judge audit:** swap A/B order and watch the score flip — live proof of position bias, and why you calibrate graders [[8]](https://www.adaline.ai/blog/llm-as-a-judge-reliability-bias).
