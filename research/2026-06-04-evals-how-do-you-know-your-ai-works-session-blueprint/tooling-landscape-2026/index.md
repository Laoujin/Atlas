---
title: "LLM Eval Tooling Landscape 2026: A Consultancy's Decision Guide"
date: 2026-06-04
depth: deep
format: md
model: "Opus 4.8"
duration_sec: 298
cost_usd: "sub"
topic: "The 2026 landscape of LLM/AI eval tooling — compare Promptfoo, Braintrust, DeepEval, OpenAI Evals, LangSmith, Ragas, Inspect AI, Arize Phoenix, plus Langfuse/Evidently/Patronus/Humanloop. Axes: OSS vs commercial + license, self-host vs SaaS, CI/CD fit, dataset/experiment mgmt, LLM-as-judge, agent & RAG eval, pricing, GitHub stars, lock-in. Decision-grade table + pick-X-if for a consultancy shipping AI for clients."
topic_raw: "The 2026 landscape of LLM/AI eval tooling — compare Promptfoo, Braintrust, DeepEval (Confident AI), OpenAI Evals, LangSmith, Ragas, Inspect AI (UK AISI), Arize Phoenix, and note others worth a mention (Langfuse, Evidently AI, Patronus, Humanloop). Axes: OSS vs commercial + license, self-host vs SaaS, CI/CD fit, dataset/experiment management, LLM-as-judge support, agent & RAG eval support, pricing model, GitHub stars (⭐), and lock-in. Produce a decision-grade comparison table and a clear \"pick X if…\" recommendation for a consultancy shipping AI for clients"
tags: [llm-evals, ai-tooling, devtools, ci-cd, rag, agents, consultancy]
summary: "Decision-grade 2026 comparison of nine LLM eval tools across license, self-host, CI/CD, judge, agent/RAG, pricing, stars and lock-in — with pick-X-if calls for a client-shipping consultancy."
citations: 41
reading_time_min: 9
---

> **Decision (consultancy shipping AI for clients).** No single tool wins — build a **two-layer stack**: a code-first OSS eval *framework* that gates CI, plus an OSS *platform* you can self-host or run as SaaS per client.[[1]](https://www.braintrust.dev/articles/deepeval-alternatives-2026)[[37]](https://mlflow.org/top-5-agent-evaluation-frameworks/)
> - **Default pick → [DeepEval](https://deepeval.com/) ⭐ 16k + [Langfuse](https://langfuse.com/) ⭐ 28k.** Apache-2.0 pytest gating with the deepest metric set, paired with MIT self-hostable tracing/datasets you can stand up per-client with zero license cost.[[10]](https://github.com/confident-ai/deepeval)[[22]](https://github.com/langfuse/langfuse)[[39]](https://www.braintrust.dev/articles/best-self-hosted-ai-evals-tools-2026)
> - **Pick [Braintrust](https://www.braintrust.dev/) if** clients pay for a polished managed UI, stakeholder dashboards and you don't want to run infra — the strongest commercial experiment/annotation platform, $249/mo Pro, self-host only on Enterprise.[[7]](https://www.braintrust.dev/pricing)[[8]](https://www.cekura.ai/blogs/braintrust-pricing)[[28]](https://www.braintrust.dev/articles/best-promptfoo-alternatives-2026)
> - **Pick [LangSmith](https://www.langchain.com/pricing) if** the client's app is already LangChain/LangGraph — native, lowest-cost commercial entry ($39/seat) — but accept ecosystem lock-in.[[12]](https://www.langchain.com/pricing)[[36]](https://github.com/langchain-ai/langchain)
> - **Pick [Promptfoo](https://github.com/promptfoo/promptfoo) ⭐ 22k for red-teaming / security** (now OpenAI-owned, still MIT) and **[Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) ⭐ 2.2k for safety/regulated, multi-provider** capability evals.[[2]](https://openai.com/index/openai-to-acquire-promptfoo/)[[4]](https://github.com/promptfoo/promptfoo)[[17]](https://github.com/UKGovernmentBEIS/inspect_ai)
> - **Add [Ragas](https://www.ragas.io/) ⭐ 14k** when the deliverable is RAG and you want reference-free retrieval metrics.[[15]](https://github.com/vibrantlabsai/ragas)[[16]](https://www.confident-ai.com/knowledge-base/compare/best-llm-evaluation-tools)

For expert consultants the load-bearing insight isn't the tool — it's that **harness design swings published benchmark scores 10–20 points on SWE-Bench Verified**, so the real asset is *your client's golden dataset + CI gates*, and tools are interchangeable plumbing around it.[[5]](https://www.digitalapplied.com/blog/ai-agent-eval-frameworks-testing-guide-2026)[[38]](https://www.adaline.ai/blog/complete-guide-llm-ai-agent-evaluation-2026)

---

## The 2026 shape of the market

Two consolidation events reshaped the landscape this cycle:

- **OpenAI acquired Promptfoo (announced 9 Mar 2026, ~$86M)** — used by 125k devs and 25%+ of the Fortune 500. Red-teaming folds into OpenAI Frontier; the repo **stays MIT and open**.[[2]](https://openai.com/index/openai-to-acquire-promptfoo/)[[3]](https://techcrunch.com/2026/03/09/openai-acquires-promptfoo-to-secure-its-ai-agents/)[[33]](https://futurumgroup.com/insights/openai-acquires-promptfoo-gaining-25-foothold-in-fortune-500-enterprises/) For a consultancy shipping non-OpenAI models, the open caveat is vendor objectivity — pair it with an independent scorer (Inspect AI) if that matters to a client.[[34]](https://dev.to/thedailyagent/top-5-ai-agent-eval-tools-after-promptfoos-exit-576i)
- **Humanloop is gone** — acqui-hired by Anthropic (founders + ~12 staff, Aug 2025, no IP/assets), standalone platform sunset **8 Sep 2025**, tech folded into the Anthropic Console. Don't design a 2026 stack around it.[[26]](https://news.ycombinator.com/item?id=44592216)[[27]](https://techcrunch.com/2025/08/13/anthropic-nabs-humanloop-team-as-competition-for-enterprise-ai-talent-heats-up/)
- **Two OpenAI "Evals"** exist and are easy to conflate: the **OSS `openai/evals` framework** (MIT, ⭐ 19k, benchmark registry, still developed) versus the **hosted Evals platform/API**, which OpenAI has **announced for deprecation** alongside Agent Builder. Treat the hosted product as a dead end; the OSS repo is a benchmark-running tool, not a product eval platform.[[13]](https://github.com/openai/evals)[[14]](https://developers.openai.com/api/docs/deprecations)
- **Braintrust raised ~$80M Series B → ~$800M valuation (Feb 2026)** — the commercial eval-platform tier is consolidating around it and LangSmith.[[40]](https://www.confident-ai.com/knowledge-base/compare/top-braintrust-alternatives-and-competitors-compared)

## Master comparison

Stars are current as of June 2026 (GitHub API). `✓` = first-class/native, `~` = possible but not the tool's focus, `✗` = not supported.

| Tool | ⭐ Stars | OSS / License | Self-host vs SaaS | CI/CD fit | Dataset / experiment mgmt | LLM-as-judge | Agent eval | RAG eval | Pricing | Lock-in |
|---|---|---|---|---|---|---|---|---|---|---|
| [DeepEval][de] | ⭐ 16k | OSS · Apache-2.0 | Self-host (free); SaaS = Confident AI | ✓ native `deepeval test run` (pytest) | ~ via Confident AI cloud | ✓ G-Eval, DAG | ✓ task completion, tool correctness | ✓ faithfulness, ctx recall/precision | Framework free; Confident AI $19.99–49.99/user; self-host @ Team/Ent | **Low** |
| [Promptfoo][pf] | ⭐ 22k | OSS · MIT (OpenAI-owned) | Self-host / CLI; Enterprise SaaS | ✓ native GitHub Action (PR review) | ~ YAML cases, no rich UI | ✓ custom assertions | ~ red-team focus | ~ not primary | Free OSS; Enterprise on-prem | **Low** ⚠ vendor objectivity |
| [Braintrust][bt] | — (closed) | Commercial · proprietary | SaaS; self-host = Enterprise only | ✓ GitHub Action → SDK | ✓ best-in-class UI, diffs, annotation | ✓ sandboxed-Python scorers | ✓ lifecycle metrics | ~ via custom scorer | Free → **Pro $249/mo** → Ent | **Medium** |
| [LangSmith][ls] | — (closed) | Commercial · proprietary | SaaS; self-host = Enterprise add-on | ✓ native evaluator runs | ✓ trace-curated datasets | ✓ online + offline | ✓ native LangGraph | ~ general framework | Free 5k → **Plus $39/seat** → Ent | **High** (LangChain) |
| [Ragas][rg] | ⭐ 14k | OSS · Apache-2.0 | Self-host (library) | ~ wrap in pytest/CI | ✗ (metrics lib) | ~ judge-backed metrics | ~ limited | ✓ **purpose-built**, reference-free | Free | **Low** |
| [Inspect AI][ia] | ⭐ 2.2k | OSS · MIT (UK AISI) | Self-host (library + UI) | ~ bring-your-own GitHub Actions | ✓ Dataset→Task→Solver→Scorer | ✓ model-graded + custom | ✓ Docker-sandboxed agentic | ~ capability-level | Free | **Low** |
| [OpenAI Evals][oe] | ⭐ 19k | OSS · MIT | Self-host only | ~ no runner; wrap in Actions | ✓ benchmark registry | ✓ model-graded YAML | ~ Completion-Fn protocol | ✗ | Free (hosted platform deprecating) | **Low** |
| [Arize Phoenix][ph] | ⭐ 10k | OSS · **Elastic 2.0** | Self-host (free); SaaS = Arize AX | ✓ code evaluators, LLM jury | ✓ score traces in-UI | ✓ Code Evaluators, LLM jury | ✓ OTel agent spans | ✓ embedding-based | OSS free; AX Free → **AX Pro $50/mo** | **Low** (OTel-native) |
| [Langfuse][lf] | ⭐ 28k | OSS · MIT | **Self-host free, unlimited**; SaaS | ✓ SDK in CI; datasets/runs | ✓ datasets, runs, scores | ✓ LLM-as-judge templates | ✓ trace/span eval | ✓ trace eval | Self-host free; cloud $29 / $199 / $2,499 | **Low** |

[de]: https://deepeval.com/
[pf]: https://github.com/promptfoo/promptfoo
[bt]: https://www.braintrust.dev/
[ls]: https://www.langchain.com/pricing
[rg]: https://www.ragas.io/
[ia]: https://github.com/UKGovernmentBEIS/inspect_ai
[oe]: https://github.com/openai/evals
[ph]: https://arize.com/phoenix/
[lf]: https://langfuse.com/

Sources backing the cells above: DeepEval[[9]](https://www.confident-ai.com/pricing)[[10]](https://github.com/confident-ai/deepeval)[[11]](https://deepeval.com/)[[30]](https://www.confident-ai.com/knowledge-base/compare/best-ai-evaluation-tools-2026); Promptfoo[[2]](https://openai.com/index/openai-to-acquire-promptfoo/)[[4]](https://github.com/promptfoo/promptfoo)[[6]](https://inference.net/content/llm-evaluation-tools-comparison/)[[28]](https://www.braintrust.dev/articles/best-promptfoo-alternatives-2026); Braintrust[[5]](https://www.digitalapplied.com/blog/ai-agent-eval-frameworks-testing-guide-2026)[[7]](https://www.braintrust.dev/pricing)[[8]](https://www.cekura.ai/blogs/braintrust-pricing); LangSmith[[12]](https://www.langchain.com/pricing)[[35]](https://agentsapis.com/langsmith-pricing/self-hosted/)[[36]](https://github.com/langchain-ai/langchain); Ragas[[15]](https://github.com/vibrantlabsai/ragas)[[16]](https://www.confident-ai.com/knowledge-base/compare/best-llm-evaluation-tools); Inspect AI[[17]](https://github.com/UKGovernmentBEIS/inspect_ai)[[18]](https://www.confident-ai.com/knowledge-base/compare/best-ci-cd-tools-testing-ai-agents-before-production-2026); OpenAI Evals[[13]](https://github.com/openai/evals)[[14]](https://developers.openai.com/api/docs/deprecations); Phoenix[[19]](https://github.com/Arize-ai/phoenix)[[20]](https://github.com/Arize-ai/phoenix/blob/main/LICENSE)[[21]](https://costbench.com/software/ai-observability/arize-phoenix/)[[31]](https://arize.com/llm-evaluation-platforms-top-frameworks/); Langfuse[[22]](https://github.com/langfuse/langfuse)[[23]](https://langfuse.com/pricing)[[29]](https://langfuse.com/faq/all/best-braintrustdata-alternatives).

## Two axes that actually decide it

**Axis 1 — framework (CI gate) vs platform (UI + storage).** DeepEval, Promptfoo, Ragas, Inspect AI and OpenAI Evals are *frameworks*: they run in code, exit non-zero on a failed assertion, and gate a PR. Braintrust, LangSmith, Langfuse and Phoenix are *platforms*: persistent storage, dataset curation, annotation UI, production monitoring. The 2026 consensus is you want one of each, not one tool doing both badly.[[1]](https://www.braintrust.dev/articles/deepeval-alternatives-2026)[[37]](https://mlflow.org/top-5-agent-evaluation-frameworks/)

**Axis 2 — CI gating strength.** DeepEval (`deepeval test run`) and Promptfoo (PR-review GitHub Action) are the only two with *native, first-class* CI gating; everyone else gates by wrapping their SDK/API in your own GitHub Actions glue. For a consultancy whose value proposition is "we ship tested AI," that native gate is worth optimising for.[[41]](https://www.confident-ai.com/knowledge-base/compare/best-ci-cd-tools-testing-ai-agents-before-production-2026)[[18]](https://www.confident-ai.com/knowledge-base/compare/best-ci-cd-tools-testing-ai-agents-before-production-2026)

## Self-host & lock-in (the consultancy-critical column)

A consultancy hands deliverables to clients with varying data-residency rules. Self-host capability and license terms dominate.

| Capability | Free self-host? | License gotcha | Verdict for client work |
|---|---|---|---|
| [Langfuse][lf2] | ✓ unlimited, MIT | none | Best — drop on client infra, no fees[[22]](https://github.com/langfuse/langfuse)[[23]](https://langfuse.com/pricing) |
| [DeepEval][de2] | ✓ framework; SaaS UI @ Team/Ent | Apache-2.0 | Best — pure-code, runs anywhere[[9]](https://www.confident-ai.com/pricing)[[10]](https://github.com/confident-ai/deepeval) |
| [Inspect AI][ia2] / [Promptfoo][pf2] / [Ragas][rg2] | ✓ | MIT / MIT / Apache-2.0 | Best — libraries, zero lock-in[[15]](https://github.com/vibrantlabsai/ragas)[[17]](https://github.com/UKGovernmentBEIS/inspect_ai)[[4]](https://github.com/promptfoo/promptfoo) |
| [Phoenix][ph2] | ✓ no feature gates, air-gappable | **Elastic 2.0** — can't *resell* it as a hosted service | Fine for internal/client deploys; ⚠ can't white-label as your own SaaS[[20]](https://github.com/Arize-ai/phoenix/blob/main/LICENSE)[[21]](https://costbench.com/software/ai-observability/arize-phoenix/) |
| [Braintrust][bt2] | ✗ Enterprise-only | proprietary | Locked to their cloud unless client buys Enterprise[[7]](https://www.braintrust.dev/pricing)[[8]](https://www.cekura.ai/blogs/braintrust-pricing) |
| [LangSmith][ls2] | ✗ Enterprise add-on | proprietary | Enterprise custom contract; + LangChain ecosystem pull[[12]](https://www.langchain.com/pricing)[[35]](https://agentsapis.com/langsmith-pricing/self-hosted/)[[36]](https://github.com/langchain-ai/langchain) |

[lf2]: https://langfuse.com/
[de2]: https://deepeval.com/
[ia2]: https://github.com/UKGovernmentBEIS/inspect_ai
[pf2]: https://github.com/promptfoo/promptfoo
[rg2]: https://github.com/vibrantlabsai/ragas
[ph2]: https://arize.com/phoenix/
[bt2]: https://www.braintrust.dev/
[ls2]: https://www.langchain.com/pricing

Note the **ELv2 trap** for Phoenix: free to self-host for any client internally, but you may **not** offer it back as a managed/hosted service — relevant if your consultancy's product *is* a hosted eval dashboard.[[20]](https://github.com/Arize-ai/phoenix/blob/main/LICENSE) Langfuse's MIT has no such restriction, and self-hosts at ~$1/GB-month vs Braintrust's ~$3/GB — cheaper at scale.[[29]](https://langfuse.com/faq/all/best-braintrustdata-alternatives)

## Worth-a-mention tier

- **[Langfuse][lf3] ⭐ 28k** — the most-starred OSS LLMOps platform; arguably the default open observability+eval+prompt-management layer for 2026, and the strongest Braintrust alternative when self-hosting matters.[[22]](https://github.com/langfuse/langfuse)[[32]](https://futureagi.com/blog/arize-phoenix-vs-langfuse-2026) Promoted into the main table above on merit.
- **[Evidently AI][ev] ⭐ 7.6k** (Apache-2.0) — open-source eval/monitoring *building blocks*, not a turnkey review platform; reaching a dedicated tool's maturity takes real engineering investment. Pick only if you want to assemble your own.[[24]](https://github.com/evidentlyai/evidently)
- **[Patronus AI][pa]** — evaluation-first, differentiated by *proprietary judge models*: Lynx (hallucination), GLIDER (rubric scoring), Percival (agent monitoring). Niche but real when you want managed, research-grade judges instead of rolling your own.[[25]](https://galileo.ai/blog/best-ai-agent-evaluation-platforms)
- **Humanloop — dead.** Sunset 8 Sep 2025 after Anthropic acqui-hire; listed only so you don't propose it.[[26]](https://news.ycombinator.com/item?id=44592216)[[27]](https://techcrunch.com/2025/08/13/anthropic-nabs-humanloop-team-as-competition-for-enterprise-ai-talent-heats-up/)

[lf3]: https://langfuse.com/
[ev]: https://github.com/evidentlyai/evidently
[pa]: https://www.patronus.ai/

## Pick-X-if (recommendation grid for a client-shipping consultancy)

| If the client situation is… | Pick | Why |
|---|---|---|
| **Default / greenfield, data-residency varies** | DeepEval + Langfuse | Apache/MIT, self-host anywhere, native pytest gate + free unlimited platform[[10]](https://github.com/confident-ai/deepeval)[[22]](https://github.com/langfuse/langfuse)[[39]](https://www.braintrust.dev/articles/best-self-hosted-ai-evals-tools-2026) |
| **Client wants a managed, polished UI; budget OK** | Braintrust Pro | Best experiment/annotation UX, diffs, sandboxed scorers, $249/mo[[7]](https://www.braintrust.dev/pricing)[[28]](https://www.braintrust.dev/articles/best-promptfoo-alternatives-2026) |
| **App is LangChain/LangGraph** | LangSmith | Native tracing/eval, $39/seat — lowest commercial entry, accept lock-in[[12]](https://www.langchain.com/pricing)[[36]](https://github.com/langchain-ai/langchain) |
| **Security / red-team / regulated** | Promptfoo (+Inspect AI) | MIT red-teaming; add Inspect AI for vendor-independent scoring[[2]](https://openai.com/index/openai-to-acquire-promptfoo/)[[17]](https://github.com/UKGovernmentBEIS/inspect_ai)[[34]](https://dev.to/thedailyagent/top-5-ai-agent-eval-tools-after-promptfoos-exit-576i) |
| **Public-sector / safety / multi-provider capability evals** | Inspect AI | UK AISI, MIT, 200+ evals across 10+ providers, Docker sandboxing[[17]](https://github.com/UKGovernmentBEIS/inspect_ai)[[18]](https://www.confident-ai.com/knowledge-base/compare/best-ci-cd-tools-testing-ai-agents-before-production-2026) |
| **Deliverable is RAG** | Ragas (+DeepEval) | Reference-free retrieval metrics; DeepEval for agent/safety overlap[[15]](https://github.com/vibrantlabsai/ragas)[[16]](https://www.confident-ai.com/knowledge-base/compare/best-llm-evaluation-tools) |
| **Already OTel-instrumented** | Arize Phoenix | OTel-native, score traces in-UI, no SDK lock-in (mind ELv2)[[19]](https://github.com/Arize-ai/phoenix)[[31]](https://arize.com/llm-evaluation-platforms-top-frameworks/) |
| **Want managed judge models, not DIY** | Patronus AI | Proprietary Lynx/GLIDER/Percival judges[[25]](https://galileo.ai/blog/best-ai-agent-evaluation-platforms) |

**Workshop framing (2h hands-on):** demo the DeepEval pytest gate failing a PR on a regressed golden-dataset case, then push those same traces to a self-hosted Langfuse for the dashboard view — that one flow shows both axes and is reproducible on any client's infra without a license.[[1]](https://www.braintrust.dev/articles/deepeval-alternatives-2026)[[38]](https://www.adaline.ai/blog/complete-guide-llm-ai-agent-evaluation-2026)[[41]](https://www.confident-ai.com/knowledge-base/compare/best-ci-cd-tools-testing-ai-agents-before-production-2026)
