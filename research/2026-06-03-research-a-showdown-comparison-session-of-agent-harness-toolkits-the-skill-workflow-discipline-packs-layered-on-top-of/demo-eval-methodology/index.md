---
title: "Demo & Eval Methodology for Agent Harness Toolkits"
date: 2026-06-03
depth: standard
format: md
topic: "Demo & eval methodology"
topic_raw: "Demo & eval methodology"
issue: 183
tags: [agent-harness, evaluation, benchmarks, methodology, llm-agents, skill-packs, demo]
summary: "How to structure a live comparison session and formal evaluation of agent harness toolkits — benchmarks, eval layers, demo modes, and scoring rubrics for skill/workflow packs."
citations: 20
reading_time_min: 6
cover: cover.svg
cost_usd: 1.89
duration_sec: 887
---

> **TL;DR** Harness engineering shifts benchmark scores 20–30+ points without changing the model [[1]](https://rapidclaw.dev/blog/ai-agent-benchmarks-2026), making the harness layer the decisive variable in any toolkit comparison. Structure a session around three task types (precise tool calls, multi-step planning, error recovery), evaluate at three levels (end-to-end / trajectory / component) [[2]](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide), and distinguish `pass@k` (solution exists?) from `pass^k` (solution is reliable?) [[3]](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Source your first 20–50 test tasks from real failures — not invented scenarios.

## Benchmark Landscape

Six public benchmarks carry signal for harness comparisons in 2026 [[1]](https://rapidclaw.dev/blog/ai-agent-benchmarks-2026) [[17]](https://arxiv.org/html/2503.16416v2):

| Benchmark           | Measures                                        | 2026 Leader                    | Key caveat                                                         |
|---------------------|-------------------------------------------------|--------------------------------|--------------------------------------------------------------------|
| SWE-bench Verified  | Code-gen agents on real GitHub issues           | Claude Opus 4.7 (87.6%)        | [[1]][bm1] Contamination confirmed — prefer BenchLM/Epoch AI scores|
| GAIA                | Multi-step reasoning + tool use (466 questions) | Claude Sonnet 4.5 (74.6%)      | [[1]][bm1] Same model: 74.6% w/ scaffold vs 44.8% bare — +30 pp   |
| TAU-bench           | Enterprise policy adherence, tool-agent-user    | —                              | [[1]][bm1] Penalises correct-but-violating answers; best prod proxy|
| WebArena            | Browser navigation across realistic sites       | Claude Mythos Preview (68.7%)  | [[1]][bm1] Human baseline ~78%; meaningful gap remains             |
| Terminal-Bench 2.0  | 89 terminal tasks: file ops, sysadmin, debug    | Harness-only: rank 30 → top 5  | [[5]][bm5] Best isolator of harness quality vs. model capability   |
| AgentBench          | 8 diverse environments, aggregated score        | —                              | [[1]][bm1] 70% aggregate can hide 0% on 2 sub-environments         |

[bm1]: https://rapidclaw.dev/blog/ai-agent-benchmarks-2026
[bm5]: https://github.com/ai-boost/awesome-harness-engineering

⚠ Berkeley researchers reward-hacked all major benchmarks by April 2026 [[16]](https://kili-technology.com/blog/ai-benchmarks-guide-the-top-evaluations-in-2026-and-why-theyre-not-enough). Prefer third-party (Epoch AI / BenchLM) evaluation scores. Run a held-out task suite built from your actual workload — leaderboard positions alone are unreliable for toolkit selection.

## Evaluation Levels

All three levels must be scored independently [[2]](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide) [[4]](https://www.braintrust.dev/articles/ai-agent-evaluation-framework). Scoring only end-to-end hides which layer regressed when a test breaks.

| Level      | What it scores                                                      | Grader type              |
|------------|---------------------------------------------------------------------|--------------------------|
| End-to-end | Did the agent accomplish the user's goal?                          | [[4]][lv4] Code / human  |
| Trajectory | Did it plan well, select correct tools, recover from errors?       | [[4]][lv4] LLM-as-judge  |
| Component  | Does each retriever, sub-agent, or tool call perform in isolation? | [[4]][lv4] Deterministic |

[lv4]: https://www.braintrust.dev/articles/ai-agent-evaluation-framework

A unified evaluation framework [[14]](https://arxiv.org/html/2605.27898v1) running tasks as instruction–tool–environment triplets under sandboxed conditions isolates environmental failures (network timeouts, anti-crawling) from genuine agent reasoning failures — up to 37.7% of apparent failures in online evaluation stem from environment, not the agent. Use offline sandbox snapshots for reproducible toolkit comparisons.

## Core Metrics

12 primary metrics across four layers, from Anthropic [[3]](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) and DeepEval [[2]](https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide):

| Layer     | Metric                | Type          | Production target           |
|-----------|-----------------------|---------------|-----------------------------|
| Tool use  | Tool correctness      | Deterministic | [[6]][mt6] > 95%            |
| Tool use  | Argument correctness  | Deterministic | [[6]][mt6] > 95%            |
| Tool use  | Step efficiency       | Deterministic | [[6]][mt6] Minimal viable   |
| Planning  | Plan quality          | LLM judge     | [[2]][mt2] Task-specific    |
| Planning  | Plan adherence        | LLM judge     | [[2]][mt2] Task-specific    |
| Output    | Task completion rate  | Code / human  | [[6]][mt6] > 90%            |
| Output    | Loop rate             | Deterministic | [[6]][mt6] 0%               |
| Safety    | Prompt injection      | Adversarial   | [[6]][mt6] 0 failures       |
| Safety    | Policy adherence      | LLM judge     | [[6]][mt6] Task-specific    |
| Retrieval | Answer relevancy      | LLM judge     | [[2]][mt2] Task-specific    |
| Retrieval | Faithfulness          | LLM judge     | [[2]][mt2] Task-specific    |
| Stats     | pass@k / pass^k       | Statistical   | [[3]][mt3] Depends on use   |

[mt6]: https://qubittool.com/blog/agent-harness-evaluation-guide
[mt2]: https://www.confident-ai.com/blog/llm-agent-evaluation-complete-guide
[mt3]: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

`pass@k` = probability of success in at least one of k runs — answers "does a solution exist?" `pass^k` = success in all k runs — answers "is it reliably repeatable?" They diverge sharply above k=3 [[3]](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Use `pass^k` for production deployment gates; `pass@k` for initial capability discovery.

## Evaluation Tooling

Six frameworks cover the eval stack for agent harnesses [[7]](https://futureagi.com/blog/agent-evaluation-frameworks-2026):

| Tool                                                       | Best for                               | Trajectory-first? | License     |
|------------------------------------------------------------|----------------------------------------|-------------------|-------------|
| [LangSmith][et-ls]                                         | LangChain/LangGraph runtimes           | ✓                 | Proprietary |
| [Future AGI][et-fagi]                                      | Mixed runtimes, OSS trajectory eval    | ✓                 | Apache 2.0  |
| [Braintrust][et-bt]                                        | Cross-functional teams, UI-first       | ✗ (bolted-on)     | SaaS        |
| [DeepEval][et18] ⭐ 16k                                    | CI-native pytest, 50+ metric library   | ✗                 | Apache 2.0  |
| [Arize Phoenix][et19] ⭐ 10k                               | OpenTelemetry / open standards         | Partial           | ELv2        |
| [OpenAI Evals][et20] ⭐ 19k                                | OpenAI-only stacks, minimal setup      | ✗                 | MIT         |

[et-ls]: https://smith.langchain.com
[et-fagi]: https://futureagi.com
[et-bt]: https://braintrust.dev
[et18]: https://github.com/confident-ai/deepeval
[et19]: https://github.com/Arize-ai/phoenix
[et20]: https://github.com/openai/evals

**Selection heuristic** [[7]](https://futureagi.com/blog/agent-evaluation-frameworks-2026): LangGraph shop → LangSmith (native trajectory semantics). Mixed runtime + OSS required → Future AGI. CI as system of record → [DeepEval](https://github.com/confident-ai/deepeval) ⭐ 16k (pytest ergonomics, 50+ metrics). Open standards required → [Arize Phoenix](https://github.com/Arize-ai/phoenix) ⭐ 10k (OTel + OpenInference). ⚠ LLM-as-judge at ~30¢/trace × 3 judges per step compounds fast — gate on deterministic checks first.

## Structuring a Live Comparison Session

Without explicit methodology, a framework showdown produces anecdotal results [[13]](https://qubittool.com/blog/ai-agent-framework-comparison-2026):

**1 — Isolate the harness layer.** Fix the model (same provider, same version, same system prompt) across all candidates. The session measures harness quality, not model capability.

**2 — Select three task categories** covering core harness responsibilities [[9]](https://medium.com/@shanewang199512/2026-agent-harness-the-game-changer-for-ai-applications-if-youre-not-the-model-you-re-the-e49722a23967):

- **Tool-call precision** — deterministically gradable (right tool, right arguments, first try)
- **Multi-step planning** — 5+ steps carrying context across turns
- **Error recovery** — chaos-inject a tool failure (500 error, malformed JSON) [[6]](https://qubittool.com/blog/agent-harness-evaluation-guide)

**3 — Declare the demo mode** upfront. Audiences tolerate pre-flight; they do not tolerate ambiguity [[8]](https://cardboard-spaceship.com/blog/google-io-2026-live-ai-demo-production-framework/):

| Mode               | Description                                              | Credibility    | Risk    |
|--------------------|----------------------------------------------------------|----------------|---------|
| Verified Live      | Real-time execution, unscripted                          | Highest        | High    |
| Constrained Live   | Real-time within controlled parameters                   | High           | Medium  |
| Pre-flight Live    | Agent ran beforehand; replayed with acknowledgment       | Medium         | Low     |
| Pre-Recorded       | Polished video, clearly labelled as such                 | Lower          | Lowest  |
| Aspirational       | Explicitly framed as future vision                       | None (current) | None    |

[dm8]: https://cardboard-spaceship.com/blog/google-io-2026-live-ai-demo-production-framework/

The 2023 Gemini video controversy is the canonical example of what happens when mode is unlabelled [[8]](https://cardboard-spaceship.com/blog/google-io-2026-live-ai-demo-production-framework/). Label the mode at the start; production discipline is itself a credibility signal.

**4 — Score at all three levels.** Capture full execution traces. Use deterministic graders for tool selection; LLM-as-judge for plan quality and recovery behaviour. Record token cost and wall-clock latency — framework choice routinely varies cost 5–6× [[1]](https://rapidclaw.dev/blog/ai-agent-benchmarks-2026).

**5 — Report per-dimension, not aggregate.** A single composite score hides failure modes [[7]](https://futureagi.com/blog/agent-evaluation-frameworks-2026). Present the breakdown table; let each dimension speak independently.

## Skill-Pack Specific Evaluation

When the comparison target is the skill/workflow/discipline-pack layer rather than the full orchestration framework:

**Utility vs. security tradeoff.** [SkillTester](https://arxiv.org/abs/2603.28815) [[10]](https://arxiv.org/pdf/2603.28815) runs an 86-task benchmark across 11 domains and finds that higher utility consistently correlates with broader permissions and greater security exposure. Score utility and security as independent axes — collapsing them into a single metric obscures the tradeoff.

**Task-adaptive rubrics.** Fixed rubrics apply generic criteria across all tasks, missing domain-specific requirements. [AdaRubric](https://arxiv.org/abs/2603.21362) [[11]](https://arxiv.org/pdf/2603.21362) generates evaluation dimensions from the task itself, improving inter-annotator agreement and producing better reward model training signals — especially important for diverse skill packs where a single rubric fails to capture domain requirements.

**Skill retrieval at scale.** As skill libraries grow, retrieval quality determines task success. [SkillFlow](https://arxiv.org/abs/2504.06188) [[12]](https://arxiv.org/pdf/2504.06188) shows embedding-based retrieval substantially outperforms keyword matching for complex queries. Track Recall@K and MRR as library size scales.

## Six Framework Comparison Dimensions

For comparing full harness frameworks, these six dimensions are the primary scoring axes [[13]](https://qubittool.com/blog/ai-agent-framework-comparison-2026):

1. **Architecture and core abstractions** — state machines vs. reactive graphs vs. role-based crews
2. **State management** — persistence, durability, human-in-the-loop checkpoints
3. **Tool integration and MCP support** — protocol compatibility, scaling tool inventories
4. **Multi-agent orchestration** — supervisor, peer, and pipeline coordination patterns
5. **Observability and debugging** — trace replay, visual state inspection
6. **Production readiness** — enterprise deployments, community maturity, licensing

No framework dominates all six. The primary trade-off axis is control vs. simplicity: CrewAI deploys multi-agent setups 40% faster but adds ~18% token overhead compared to LangGraph [[15]](https://topuzas.medium.com/the-great-ai-agent-showdown-of-2026-openai-autogen-crewai-or-langgraph-7b27a176b2a1). Report all six dimensions separately; no composite score.

## Common Pitfalls

- **Scoring final output only** → misses which trajectory step regressed [[7]](https://futureagi.com/blog/agent-evaluation-frameworks-2026)
- **Relying solely on public benchmarks** → misses your tool registry, error codes, business policy [[7]](https://futureagi.com/blog/agent-evaluation-frameworks-2026)
- **Reporting aggregate scores** → 70% overall can hide 0% on two sub-environments [[1]](https://rapidclaw.dev/blog/ai-agent-benchmarks-2026)
- **Shared state between test runs** → each trial needs a clean environment; correlated failures inflate pass rates [[3]](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- **Unlabelled demo mode** → ambiguity between live and pre-recorded destroys credibility [[8]](https://cardboard-spaceship.com/blog/google-io-2026-live-ai-demo-production-framework/)
- **Inventing test cases** → source tasks from actual bug trackers and real failures [[3]](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
