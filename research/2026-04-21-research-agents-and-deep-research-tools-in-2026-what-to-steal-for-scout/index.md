---
title: Research agents and deep-research tools in 2026 — what to steal for Scout
date: 2026-04-21
depth: deep
format: md
topic: "Survey of research agents / deep-research tools available in 2026 that could serve a role like Scout (my custom Claude-Code-based research engine). Compare the main options, note what's production-ready vs experimental, and flag anything I should steal ideas from."
tags: [deep-research, agents, claude-code, llm, survey]
cover: cover.svg
summary: Landscape of 2026 deep-research agents — commercial (OpenAI, Perplexity, Gemini, Claude, Grok), OSS (GPT-Researcher, open_deep_research, STORM, smolagents), and Claude-Code skills — with a short list of ideas worth porting into Scout.
citations: 23
reading_time_min: 9
---

## TL;DR for a Scout-shaped tool

"Deep research" has become table stakes: ChatGPT, Claude, Gemini, Perplexity, and Grok all ship an agentic research feature at the $20/month tier; differentiation is now speed, depth, and citation accuracy, not whether the feature exists [[1]](https://learn.g2.com/deepseek-vs-grok). If Scout's job is a cited, reproducible, Jekyll-published artifact tied to a custom source rubric, the commercial products are poor fits (closed, no on-disk artifact, no steering hints). The interesting comparison class is OSS agents + Claude-Code-native skills.

Scout-relevant picks to steal from:

- **[GPT-Researcher](https://github.com/assafelovic/gpt-researcher)** — planner/executor/publisher split, parallel crawler, tree-shaped Deep Research mode [[2]](https://github.com/assafelovic/gpt-researcher).
- **[langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research)** — MCP-native, model-agnostic, #6 on Deep Research Bench [[3]](https://github.com/langchain-ai/open_deep_research).
- **[199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill)** — 8-phase pipeline with disk-persisted citations, multi-persona critique, auto-continuation past context windows [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).
- **[STORM](https://github.com/stanford-oval/storm)** — perspective-guided question generation; Co-STORM's human-in-the-loop turn policies [[5]](https://github.com/stanford-oval/storm).

## The landscape at a glance

| Tool | Kind | License / access | Depth mechanism | Citation rigor | Scout-fit |
|---|---|---|---|---|---|
| OpenAI Deep Research | SaaS | ChatGPT Pro/Plus | o3-tuned agent, 15–25 min runs | 87% cited accuracy [[6]](https://glasp.co/articles/deep-research-tools-compared), 26.6% HLE [[7]](https://openai.com/index/introducing-deep-research/) | low — closed, no artifact, no steering |
| Perplexity Sonar Deep Research | API + SaaS | Commercial, $2/$8 per M tok + $5/1K searches [[8]](https://pricepertoken.com/pricing-page/model/perplexity-sonar-deep-research) | Short loops, 2–3 min [[6]](https://glasp.co/articles/deep-research-tools-compared) | 94.3% Sonar Pro [[6]](https://glasp.co/articles/deep-research-tools-compared) | medium — API-driven, but opaque |
| Gemini Deep Research | SaaS | AI Pro $19.99/mo [[9]](https://screenapp.io/blog/gemini-pricing) | Gmail/Drive + web, multi-page reports [[10]](https://www.engagecoders.com/google-gemini-deep-research-workspace-integration/) | closed metric | low — Workspace-locked |
| Claude Research / Advanced | SaaS | Claude Pro/Max | Up to 45 min, hundreds of sources [[11]](https://www.anthropic.com/news/research) | closed metric | low — not programmable as artifact |
| Claude Managed Agents | API (beta, 2026-04-01) | Commercial | Harness: sandbox, tools, web [[12]](https://platform.claude.com/docs/en/managed-agents/overview) | depends on system prompt | high — could host Scout |
| Grok DeepSearch | SaaS | X Premium | Real-time X/web synthesis [[13]](https://www.tryprofound.com/blog/understanding-grok-a-comprehensive-guide-to-grok-websearch-grok-deepsearch) | closed metric | low — X-centric |
| [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) | OSS | Apache-2.0, 26.6k stars (Apr 2026) [[2]](https://github.com/assafelovic/gpt-researcher) | Planner+execution+publisher; tree Deep Research [[2]](https://github.com/assafelovic/gpt-researcher) | inline, 20+ sources | high — closest analogue |
| [open_deep_research](https://github.com/langchain-ai/open_deep_research) | OSS | MIT, 11.2k stars (Apr 2026) [[3]](https://github.com/langchain-ai/open_deep_research) | LangGraph; MCP; #6 DR Bench 0.4943 [[3]](https://github.com/langchain-ai/open_deep_research) | depends on search tool | high — swap backend |
| [STORM / Co-STORM](https://github.com/stanford-oval/storm) | OSS | MIT, 28.1k stars (Apr 2026) [[5]](https://github.com/stanford-oval/storm) | Perspective-guided Q&A [[14]](https://storm-project.stanford.edu/research/storm/) | Wikipedia-style, polished | medium — long-form only |
| [smolagents Open Deep Research](https://github.com/huggingface/smolagents) | OSS | Apache-2.0, 26.8k stars (Apr 2026) [[15]](https://github.com/huggingface/smolagents) | Code-agent; 55.15 GAIA vs OpenAI 67.36 [[16]](https://huggingface.co/blog/open-deep-research) | proof-of-concept | low — experimental |
| [local-deep-researcher](https://github.com/langchain-ai/local-deep-researcher) | OSS | MIT | Ollama/LMStudio; iterative reflect-and-requery [[17]](https://github.com/langchain-ai/local-deep-researcher) | inline markdown sources | medium — offline mode |
| [199-biotech claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) | Claude Skill | MIT, 509 stars [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill) | 8-phase; critique loop-back; auto-continue [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill) | disk-persisted citations | very high — same substrate |
| [Weizhena Deep-Research-skills](https://github.com/Weizhena/Deep-Research-skills) | Claude Skill | MIT, 483 stars [[18]](https://github.com/Weizhena/Deep-Research-skills) | Two-phase: outline + deep [[18]](https://github.com/Weizhena/Deep-Research-skills) | inline | high — HITL checkpoints |
| Elicit | SaaS (academic) | Commercial | 138M papers + 545K trials, abstract screening [[19]](https://elicit.com/solutions/literature-review) | 99.4% field-extraction accuracy [[19]](https://elicit.com/solutions/literature-review) | low — PubMed-only |
| FutureHouse (Crow/Falcon/Owl/Phoenix) | SaaS + API (science) | Commercial | Modular agents per task [[20]](https://www.futurehouse.org/research-announcements/launching-futurehouse-platform-ai-agents) | paper-grounded | low — science-only |

## Commercial "Deep Research" products

### OpenAI Deep Research
Launched February 2025 in ChatGPT Pro; powered by an o3 variant tuned for browsing and analysis; 26.6% on Humanity's Last Exam at launch — highest in its cohort [[7]](https://openai.com/index/introducing-deep-research/). Runs are the longest (15–25 min) and the reports the most essay-like [[6]](https://glasp.co/articles/deep-research-tools-compared). The sibling OSS reproduction on smolagents hits 55.15% on GAIA against OpenAI's 67.36% [[16]](https://huggingface.co/blog/open-deep-research) — so the production gap is still real, mostly in browser tooling and vision.

### Perplexity Sonar Deep Research
Only one of the "big five" with a production API, at $2/$8 input/output per million tokens on the base rate; Deep Research stacks $2/1M citation tokens, $3/1M reasoning tokens, and $5 per 1K searches — a full query typically lands around $0.41 [[8]](https://pricepertoken.com/pricing-page/model/perplexity-sonar-deep-research). Fastest of the commercial options (2–3 min) and claims 94.3% citation accuracy on Sonar Pro vs ~87% for GPT-5.2 Deep Research [[6]](https://glasp.co/articles/deep-research-tools-compared). The API is the obvious drop-in if you want to delegate the search+synth step from Scout.

### Gemini Deep Research
Lives inside Google AI Pro at $19.99/mo and differentiates on Workspace: it pulls from Gmail, Drive, and the public web simultaneously and drops multi-page reports back into Docs [[9]](https://screenapp.io/blog/gemini-pricing)[[10]](https://www.engagecoders.com/google-gemini-deep-research-workspace-integration/). Useless for a Scout-style standalone artifact unless you live in Workspace.

### Claude Research / Advanced Research
Anthropic calls it "Research" and "Advanced Research" — the latter runs up to 45 min across hundreds of sources autonomously [[11]](https://www.anthropic.com/news/research). The important thing for Scout is that Anthropic renamed the "Claude Code SDK" to "Claude Agent SDK" precisely because internal use was dominated by research, video, and note-taking — not just coding [[21]](https://www.buildfastwithai.com/blogs/claude-ai-complete-guide-2026). Claude-Code-as-research-platform is the officially sanctioned pattern.

### Claude Managed Agents (beta, Apr 2026)
Hosted agent harness released in public beta behind the `managed-agents-2026-04-01` header; it provides the sandbox, Bash, file ops, web search/fetch, and MCP servers that Scout currently gets from the local runner [[12]](https://platform.claude.com/docs/en/managed-agents/overview). If Scout ever wants cloud execution without the GitHub Actions runner, this is the migration path — and the Environment/Session/Events model maps cleanly onto "one research run = one Session."

### Grok DeepSearch
Only interesting when the topic is breaking news or social sentiment — direct X-timeline access is the one thing competitors can't match [[13]](https://www.tryprofound.com/blog/understanding-grok-a-comprehensive-guide-to-grok-websearch-grok-deepsearch). No API relevant to Scout.

## Open-source agents

### GPT-Researcher
The closest conceptual sibling to Scout, and the older one — May 2023, Apache-2.0, 26.6k stars (Apr 2026) [[2]](https://github.com/assafelovic/gpt-researcher). Architecture is a clean three-role split: **planner** generates research questions from the query, **execution agents** crawl 20+ web sources in parallel, **publisher** aggregates into the final report with inline citations [[2]](https://github.com/assafelovic/gpt-researcher). 2026 additions: a recursive Deep Research mode with tree-shaped exploration and configurable depth/breadth (~5 min, ~$0.40 per run on o3-mini), AI-generated inline illustrations via Gemini, LangSmith tracing, MCP integration, and local-document research [[2]](https://github.com/assafelovic/gpt-researcher). Production-ready.

### LangChain open_deep_research
MIT, 11.2k stars, built on LangGraph, model-agnostic via `init_chat_model()`, Tavily by default but supports native Anthropic/OpenAI web search and any MCP server [[3]](https://github.com/langchain-ai/open_deep_research). Ranked #6 on DeepResearch Bench with a 0.4943 RACE score using GPT-5 [[3]](https://github.com/langchain-ai/open_deep_research). Deployable via LangGraph Platform or Open Agent Platform. The most "configurable" of the OSS options — closest to a reference implementation.

### Stanford STORM / Co-STORM
MIT, 28.1k stars [[5]](https://github.com/stanford-oval/storm). Different shape: instead of one planner, STORM **simulates conversations between writers with different perspectives and a topic-expert LLM grounded in web sources**, then uses that transcript to build the outline [[14]](https://storm-project.stanford.edu/research/storm/). Measurably broader coverage (+10% absolute) and better organization (+25%) vs outline-then-RAG baselines [[14]](https://storm-project.stanford.edu/research/storm/). Co-STORM adds human-in-the-loop turn policies. Outputs are Wikipedia-style; Stanford explicitly warns they're not publication-ready [[5]](https://github.com/stanford-oval/storm).

### Hugging Face smolagents + Open Deep Research
Apache-2.0, 26.8k stars [[15]](https://github.com/huggingface/smolagents). Core bet: agents emit **Python code** instead of JSON tool calls, yielding ~30% fewer steps and better multimodal state handling [[16]](https://huggingface.co/blog/open-deep-research). The Open Deep Research example hit 55.15% on GAIA — a 22-point jump over JSON-based agent baselines, but still 12 points behind OpenAI Deep Research's 67.36% [[16]](https://huggingface.co/blog/open-deep-research). Still a proof-of-concept; known context-window blow-ups and demo instability [[16]](https://huggingface.co/blog/open-deep-research).

### LangChain local-deep-researcher
MIT. Fully local: any Ollama- or LMStudio-hosted model, SearXNG for search, nothing leaves the machine [[17]](https://github.com/langchain-ai/local-deep-researcher). Loop is explicit — generate query → search → summarize → **reflect for knowledge gaps** → generate next query, for a user-specified number of cycles, ending in a markdown summary with sources [[17]](https://github.com/langchain-ai/local-deep-researcher). Good reference for Scout's offline mode if that's ever on the table.

## Claude-Code-native research skills

These matter most for Scout because they share the substrate: a `.md` skill file + Markdown-only artifacts + no-lock-in.

### 199-biotechnologies/claude-deep-research-skill
MIT, 509 stars [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill). 8 phases: **Scope → Plan → Retrieve (parallel search + sub-agents) → Triangulate → Outline Refinement → Synthesize → Critique → Refine → Package** [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill). Ideas worth porting:
- **Disk-persisted citations that survive context compaction** — this is the single biggest fragility in a long Scout run [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).
- **Multi-persona critique** (Skeptical Practitioner, Adversarial Reviewer, Implementation Engineer) before the final write [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).
- **Validation loop: validate → fix → retry, max 3 cycles** with 9 structural checks plus DOI/URL hallucination detection [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).
- **Auto-continuation via recursive sub-agents for reports >18K words** [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).
- **Date fetch before searching** — so the model doesn't use stale year assumptions in queries [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).

### Weizhena/Deep-Research-skills
MIT, 483 stars [[18]](https://github.com/Weizhena/Deep-Research-skills). Two phases: outline generation (user can expand it) then deep investigation per item in parallel [[18]](https://github.com/Weizhena/Deep-Research-skills). The HITL checkpoints are the lesson — approve outline before spending tokens on investigation. Scout is autonomous, so this maps to "self-review the outline before committing," not a literal user prompt.

### Three Ways to Build Deep Research with Claude (paddo.dev)
Taxonomy for the design space itself [[22]](https://paddo.dev/blog/three-ways-deep-research-claude/):
1. **DIY recursive spawning** — ~20 lines of shell, parallel researcher instances, unlimited depth; pays in token cost and no visibility. Scout's current shape.
2. **MCP plug-and-play** — drop in DuckDuckGo, Semantic Scholar, etc.; low ceiling, big upfront context tax.
3. **Production research product** — multi-source claim verification, progress streaming, cost tracking; high engineering + maintenance.

Scout sits between (1) and (3). The direction to move is lift-specific ideas from (3) — not to become (3).

## Domain-specific agents

### Elicit
Best-in-class for academic literature, not general research. 138M papers + 545K clinical trials, PubMed/ClinicalTrials.gov search, 80% time saved on abstract screening with every screening decision backed by quote-level rationale, 99.4% data-extraction accuracy on a real German policy review [[19]](https://elicit.com/solutions/literature-review). Systematic Review reports cap at 80 papers. Ideas worth stealing: **per-claim rationale + source quote**, and **quality scoring of each source against the screening criteria**, not a binary in/out.

### FutureHouse (Crow, Falcon, Owl, Phoenix)
Scientific-discovery platform built on Claude [[23]](https://claude.com/customers/futurehouse); agents are task-specialized — Crow extracts genes/markers from papers, Falcon does background, Owl checks whether a hypothesis has already been investigated, Phoenix designs chemistry [[20]](https://www.futurehouse.org/research-announcements/launching-futurehouse-platform-ai-agents). The transferable pattern is **one agent per epistemic move** rather than one generalist — Scout already does this implicitly via Explore sub-agents, but not with distinct named roles.

## Benchmarks: what "good" means in 2026

DeepResearch Bench: 100 PhD-level tasks across 22 fields, scored on **RACE** (report quality, reference-based, adaptive criteria) and **FACT** (retrieval + citation trustworthiness) [[3]](https://github.com/langchain-ai/open_deep_research). Current top: Cellcog Max (proprietary, 56.13 overall, Mar 2026) and TrajectoryKit on GPT-OSS/GPT-5.4 (MIT, 54.92) [[3]](https://github.com/langchain-ai/open_deep_research). GAIA (general assistant benchmark) is where smolagents tops out at 55.15% against OpenAI DR's 67.36% [[16]](https://huggingface.co/blog/open-deep-research). Humanity's Last Exam is the hardest: OpenAI Deep Research scored 26.6% at launch, which was the frontier at the time [[7]](https://openai.com/index/introducing-deep-research/).

None of these benchmarks directly evaluate the thing Scout does — citation-inline markdown with per-topic source rubrics. The closest proxy is FACT's citation-trustworthiness axis.

## Ideas to steal for Scout (ranked)

1. **Disk-persisted `{claim, url}` store** that survives context compaction. Currently Scout's citations live in the model's working memory until the Write happens — a long deep run risks losing cites [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).
2. **Reflect-and-requery loop** à la local-deep-researcher: after initial synthesis, explicitly list knowledge gaps and fire a second round of searches targeting them [[17]](https://github.com/langchain-ai/local-deep-researcher). Cleaner than today's ad-hoc "did I miss anything" check.
3. **Multi-persona critique pass** before writing: Skeptical Practitioner + Adversarial Reviewer reads the draft and flags unsupported claims [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill). Pairs well with the existing "every claim has ≥1 URL" self-check.
4. **Perspective-guided outline** (STORM): before planning sub-questions, enumerate stakeholder perspectives implied by the topic and ensure the outline covers each [[14]](https://storm-project.stanford.edu/research/storm/). Especially useful for deep depth.
5. **Per-source credibility scoring** in comparison tables (Elicit pattern): not just "cite the URL" but a one-token tag — e.g., official-docs / peer-reviewed / vendor-blog / forum-consensus [[19]](https://elicit.com/solutions/literature-review). Scout already labels opinions by source; formalizing this into a taxonomy tightens it.
6. **Publisher role split**: GPT-Researcher's clean planner/executor/publisher boundary means the final writer sees only the evidence bundle, not the noisy search trajectory [[2]](https://github.com/assafelovic/gpt-researcher). In Scout terms: synthesize into a citation ledger first, write the markdown second.
7. **Auto-continuation for long reports**: Scout's `deep` mode can blow past context; the 199-biotech pattern uses recursive sub-agents to keep going past 18K words [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).
8. **Fetch today's date before querying** — trivial, prevents stale-year queries when the runtime's clock disagrees with training data [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill).
9. **MCP-first search backend**: both open_deep_research and GPT-Researcher standardized on MCP as the pluggable search interface [[3]](https://github.com/langchain-ai/open_deep_research)[[2]](https://github.com/assafelovic/gpt-researcher) — swapping Tavily / SearXNG / Exa becomes config, not code.
10. **Claude Managed Agents as a hosting target** if Scout ever outgrows GitHub Actions — the Environment/Session/Events model maps 1:1 onto research-per-run [[12]](https://platform.claude.com/docs/en/managed-agents/overview).

## Production-ready vs experimental

| Production-ready today | Experimental / proof-of-concept |
|---|---|
| OpenAI Deep Research, Perplexity Sonar Deep Research, Gemini DR, Claude Research, Grok DeepSearch [[1]](https://learn.g2.com/deepseek-vs-grok) | smolagents Open Deep Research — context-window blow-ups, unstable demo [[16]](https://huggingface.co/blog/open-deep-research) |
| GPT-Researcher [[2]](https://github.com/assafelovic/gpt-researcher), open_deep_research [[3]](https://github.com/langchain-ai/open_deep_research), local-deep-researcher [[17]](https://github.com/langchain-ai/local-deep-researcher) | STORM — "cannot produce publication-ready articles" per authors [[5]](https://github.com/stanford-oval/storm) |
| Elicit Systematic Review [[19]](https://elicit.com/solutions/literature-review), FutureHouse Crow/Falcon/Owl [[20]](https://www.futurehouse.org/research-announcements/launching-futurehouse-platform-ai-agents) | FutureHouse Phoenix — "not as deeply benchmarked, may make more mistakes" [[20]](https://www.futurehouse.org/research-announcements/launching-futurehouse-platform-ai-agents) |
| 199-biotech Claude skill [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill), Weizhena skill [[18]](https://github.com/Weizhena/Deep-Research-skills) | Claude Managed Agents — public beta, April 2026 [[12]](https://platform.claude.com/docs/en/managed-agents/overview) |
