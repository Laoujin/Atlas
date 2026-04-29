---
title: Research agents and deep-research tools in 2026 — what to steal for Scout
date: 2026-04-21
depth: deep
format: md
topic: "Survey of research agents / deep-research tools available in 2026 that could serve a role like Scout (my custom Claude-Code-based research engine). Compare the main options, note what's production-ready vs experimental, and flag anything I should steal ideas from."
tags: [deep-research, agents, claude-code, llm, survey]
cover: cover.svg
summary: Landscape of 2026 deep-research agents — commercial, OSS, and Claude-Code skills — plus a verified head-to-head Scout vs 199-biotech vs Weizhena and a status check on which "ideas to steal" Scout has actually shipped.
citations: 26
reading_time_min: 19
updated: 2026-04-29
---

> **Update — 2026-04-29.** Eight days later, most of the gaps this survey named are closed in [Scout](https://github.com/Laoujin/Scout) ⭐ 0 (Apr 2026) [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md): disk-persisted `citations.jsonl`, reflect-and-requery, perspective-guided outline (deep tier's "breadth heuristic"), per-source `source_type` taxonomy, GitHub-stars on every link, planner/researcher/writer split for `deep`, post-write reviewer, date-injection before querying, format auto-selection, topic sharpening, multi-angle decomposition, and bespoke per-page HTML "views" via the `scout-view-author` skill [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md)[[25]](https://github.com/Laoujin/Scout/blob/main/skills/scout/deep.md). A real head-to-head also ran on issue #7 [[26]](https://github.com/Laoujin/Scout/issues/7) — Scout vs 199-biotech vs Weizhena on the same topic — and the verdict is honest: **Scout wins on density, named picks, paste-ready code, unattended single-shot, and publication; loses on corpus breadth, epistemic honesty (no per-claim confidence, no `[uncertain]`), and re-renderability.** See the [Status of "ideas to steal"](#ideas-to-steal-for-scout-status-apr-2026) and [Head-to-head verified](#head-to-head-verified--scout-vs-199-biotech-vs-weizhena-apr-2026) sections below.

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

## Ideas to steal for Scout (status, Apr 2026)

Restructured 2026-04-29: status markers reflect what Scout has actually shipped vs what's still open. Open items first.

### Still open

1. **✗ Multi-persona critique pass before writing** — 199-biotech runs Skeptical Practitioner + Adversarial Reviewer + Implementation Engineer over the draft and surfaces unsupported claims [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill). Scout's `deep` tier has a single `scout-reviewer` sub-agent [[25]](https://github.com/Laoujin/Scout/blob/main/skills/scout/deep.md) — same shape, one persona; splitting into two-three named personas is cheap and worth doing.
2. **✗ Per-claim confidence labels (High / Med / Low) and an explicit Claims-Evidence Table** — 199-biotech appends a table mapping load-bearing claims → sources → confidence rating [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill). Scout's "no claim without URL" rule is weaker because it doesn't surface *which* claims are thinly supported. Cheapest big win flagged in the verified head-to-head below.
3. **✗ `[uncertain]` markers on unverifiable fields** (Weizhena pattern) [[18]](https://github.com/Weizhena/Deep-Research-skills) — and a tail list of the exact uncertain field paths. Honest epistemics, prompt-level change.
4. **✗ Editable analytic schema before research (`fields.yaml` style)** — Weizhena lets the user define ~50 analytic axes per item before `/research-deep` fans out [[18]](https://github.com/Weizhena/Deep-Research-skills). Scout has no equivalent lever; depth/format flags don't shape the analytic axes. Architectural lift but worth piloting on survey-shaped topics.
5. **✗ Research/render split** — Weizhena emits per-item JSON (`results/*.json`) and a `generate_report.py` that synthesizes the markdown; you can re-render against a different template without re-researching [[18]](https://github.com/Weizhena/Deep-Research-skills). Scout's `index.md` IS the artifact. The new `scout-view-author` skill is partial coverage (you can author alternate visual treatments without re-running) but the data shape is still narrative-only, not structured.
6. **✗ MCP-first search backend** — both [open_deep_research](https://github.com/langchain-ai/open_deep_research) ⭐ 11.2k (Apr 2026) [[3]](https://github.com/langchain-ai/open_deep_research) and [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) ⭐ 26.6k (Apr 2026) [[2]](https://github.com/assafelovic/gpt-researcher) standardized on MCP as the pluggable search interface — swapping Tavily / SearXNG / Exa becomes config. Scout still uses `WebSearch` + `WebFetch` + `playwright` fallback hardcoded in the skill [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md).
7. **✗ Source-type breakdown in the artifact** — derived from `citations.jsonl` (Anthropic / GH / security firms / blogs etc.). Scout already tags `source_type` per ledger entry [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md); surfacing the histogram in the artifact is a one-prompt change.
8. **✗ Methodology metadata block** — 199-biotech appends a footer naming phases, source counts, triangulation rule, persona names, validation status [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill). Cheap auditability win.
9. **✗ Claude Managed Agents as a hosting target** — if Scout outgrows the self-hosted GitHub Actions runner [[12]](https://platform.claude.com/docs/en/managed-agents/overview). Not a current pain point but the migration path is open.

### Shipped or partial

10. **✓ Disk-persisted `{claim, url}` store** — Scout writes `citations.jsonl` for `standard` and `deep`, with `n` matching every `[[n]]` in the body [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md). Schema includes `source_type`, `quote`, `github_stars`. Hard rule: every `[[n]]` has a ledger entry; every entry has a non-empty `url`.
11. **✓ Reflect-and-requery loop** — `standard` runs one explicit gap-listing + targeted requery round; `deep` does the same per researcher sub-agent plus one parent remediation round [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md)[[25]](https://github.com/Laoujin/Scout/blob/main/skills/scout/deep.md).
12. **✓ Perspective-guided outline (STORM-shaped)** — `deep.md`'s breadth heuristic enumerates the chooser / maintainer / skeptic / operator / competitor / history angles before dispatching researchers [[25]](https://github.com/Laoujin/Scout/blob/main/skills/scout/deep.md).
13. **✓ Per-source credibility taxonomy** — `official` / `peer-reviewed` / `vendor-blog` / `forum` / `news` / `wiki` tags on every ledger entry [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md).
14. **✓ Planner / researcher / writer split** — `deep` tier: parent plans + writes, researcher sub-agents fan out (max 6 concurrent), each owns its own `citations.a<N>.jsonl`, `merge_ledgers.sh` dedupes into `citations.jsonl`, parent writes from compressed researcher summaries [[25]](https://github.com/Laoujin/Scout/blob/main/skills/scout/deep.md). Each researcher gets its own 200K context so the parent never sees raw search trajectories.
15. **✓ Fetch today's date before querying** — `DATE` is injected by `run.sh`; `WebSearch` queries include the literal year [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md).
16. **◑ Auto-continuation for long reports** — sidestepped rather than solved. The researcher sub-agent split keeps the parent context small, so the 18K-word ceiling that drove 199-biotech's recursive auto-continuation [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill) hasn't been hit. Open if Scout ever wants single-page reports >18K words.
17. **◑ Re-renderability** — the new `scout-view-author` skill produces bespoke HTML "views" of an existing canonical (`<canonical>/views/<view_name>.html`) without re-running research [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md). This covers "render the same data with a different visual register" but not "edit the analytic schema and re-emit the matrix" — the canonical is still narrative, not a queryable JSON.

### Adjacent capabilities Scout shipped that weren't in the original "ideas to steal" list

18. **Topic sharpening** — pre-research LLM step proposes a tightened topic with optional decomposition for multi-angle expeditions [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md). User edits in place via GitHub Issue, then ticks Start.
19. **Decomposition with synthesis** — multi-angle topics fan out into one sub-research per angle plus a parent overview that names contradictions and dependencies between children [[25]](https://github.com/Laoujin/Scout/blob/main/skills/scout/deep.md).
20. **Format auto-selection** — `auto` heuristic picks `.md` for narrative analyses and `.html` for comparison-heavy / visual topics [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md). Neither commercial nor OSS competitor varies format by topic shape.
21. **Cost / duration in frontmatter** — `cost_usd` and `duration_sec` injected by `run.sh` after the run, surfaced on the Atlas card. Neither 199-biotech nor Weizhena exposes cost.
22. **Profile-driven localization** — `profile.yml` with `location` / `languages` / `currency` / `interests` localizes sharpening (e.g., "best ramen" → "best ramen in Ghent, EUR") [[24]](https://github.com/Laoujin/Scout/blob/main/skills/scout/SKILL.md).

## Head-to-head verified — Scout vs 199-biotech vs Weizhena (Apr 2026)

Same topic (Yolo Claude Code in Docker, [issue #7](https://github.com/Laoujin/Scout/issues/7)) [[26]](https://github.com/Laoujin/Scout/issues/7), three tools, three artifacts, all read end-to-end. Numbers below are from the verified comparison run.

### Run footprint

| Metric | Scout (`deep`) | [199-biotech](https://github.com/199-biotechnologies/claude-deep-research-skill) ⭐ 509 [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill) | [Weizhena](https://github.com/Weizhena/Deep-Research-skills) ⭐ 483 [[18]](https://github.com/Weizhena/Deep-Research-skills) |
|---|---|---|---|
| Lines | 423 | 621 | 8,901 |
| Words | 4,915 | 9,502 | 232,197 |
| Distinct citations | 77 | 34 (self-reported) | ≥150 across 75 items |
| Unique domains | 38 | not tallied | not tallied |
| Wall-clock | 18.5 min | ~25 min | ~7.5 hr (interactive, multi-phase gates) |
| API cost | $10.70 declared | not disclosed | not disclosed |
| Subscription footprint | "blip on the subscription" | comparable to Scout | **exceeded Max-$200 6-hour cap** on this single topic — required pause/resume on a fresh window |
| Artifacts | `index.md` + `outline.md` + `citations.jsonl` + 8 per-agent ledgers | `.md` + `.html` (advertised JSONL/PDF not produced) | `report.md` + `outline.yaml` + `fields.yaml` + `generate_report.py` + 75 `results/*.json` |

### Where Scout actually loses

- **Corpus breadth.** Weizhena's 75-tool sweep names tools Scout doesn't (Ona Veto, NVIDIA OpenShell, Cloudflare Outbound Workers, kubernetes-sigs/agent-sandbox, Spritz, sbox, claucker, VibePod, rivet-dev, …). On a survey-style topic, Weizhena is the right tool.
- **Incident / CVE breadth.** Weizhena cites ~9 distinct CVE/incident classes (CVE-2025-59536, CVE-2026-21852, CVE-2025-66032, CVE-2026-25725, CVE-2026-39861, Claudy Day, Mar 2026 source leak, axios RAT, LiteLLM, Ona disclosure, Adversa deny-rule bypass). Scout covers ~5; 199-biotech ~3 (and missed CVE-2025-59536 entirely).
- **Epistemic honesty.** No `[uncertain]` markers, no per-claim confidence labels, no source-type histogram in the artifact. Both competitors do better here in different ways.
- **Re-renderability.** Once a Scout run is done, the template can't change without re-researching. Weizhena lets you edit `generate_report.py` and re-render from `results/*.json`.
- **Auditability of major claims.** 199-biotech's Claims-Evidence Table maps 10 load-bearing claims → sources → High/Med/Low confidence; Scout's "no claim without URL" treats every URL-cited claim as equally weighted.
- **Methodology transparency.** 199-biotech names its 8 phases, persona names, triangulation rule, source-type breakdown. Scout has citation count + per-agent ledgers but no methodology block in the artifact.
- **Track record.** [Scout](https://github.com/Laoujin/Scout) ⭐ 0 (Apr 2026), 4 outputs total. 199-biotech (⭐ 509) and Weizhena (⭐ 483) have months of use. Failure modes that show up at scale haven't been observed yet for Scout.

### Where Scout actually wins

- **Density for a narrative reader.** 4.9k words gets to a decision faster than 9.5k or 232k.
- **Picks named with context.** "Fastest start: Docker Sandboxes. Specific toolbelt: roll your own. Multi-project: claudebox." That's what an expert who's read enough actually wants. 199-biotech recommends an architecture without comparing alternatives. Weizhena scores all 75 0–5 and lets the reader choose — more honest, less direct.
- **Paste-ready code in one place.** Complete Dockerfile + `init-firewall.sh` + `docker run` + `compose.yaml` in one read. 199-biotech splits across sections; Weizhena has snippets per-item.
- **Currency on 2026 CVEs.** Scout names CVE-2025-59536, Cyata, MCP-STDIO, Trail of Bits, Invariant. (Still behind Weizhena's depth here, but ahead of 199-biotech.)
- **Format auto-selection.** Scout's `auto` heuristic picked `.md` for this topic; neither competitor varies format by topic shape.
- **Unattended single-shot.** 18.5 min one-shot. 199-biotech ~25 min, also single-shot. Weizhena needs three human gates (`/research`, `/research-deep`, `/research-report`) — incompatible with overnight or scheduled runs.
- **Publication pipeline.** Scout lands on a public Atlas URL via GitHub Pages. The others sit on disk.
- **Cost transparency.** `cost_usd: 10.70`, `duration_sec: 1110` in frontmatter. Neither competitor exposes cost.
- **Subscription footprint.** Weizhena exceeded the Max-$200 6-hour cap on this single topic; Scout was a "blip." (User-observed, not measured rigorously.)

### Situational picks

- **"What should I do tonight?" with a developer who'll act on it** → Scout. Density + paste-ready code + named picks beats both alternatives for this shape.
- **"Map the entire landscape, score everything, let me decide"** → Weizhena on output quality. Caveat: the Max-$200 6-hour cap. Scout's `deep` (`expedition`) tier exists and is shape-similar but hasn't been benchmarked head-to-head.
- **"Polished narrative essay with audit trail"** → 199-biotech. Claims-Evidence Table + 8-phase methodology block read like a vendor white paper.
- **"Reproducibility — re-render with a new template later"** → Weizhena (only one with the data/render split).
- **"Unattended overnight runs"** → Scout or 199-biotech. Weizhena's interactive gates rule it out.

### Bottom line

Scout is **good for the use case it's designed for** — terse decision-oriented narrative with paste-ready code, single-shot, published. It is **not "best overall"** by any objective measure on this topic. Weizhena beats it on breadth, epistemics, and re-renderability. 199-biotech beats it on auditability and methodology transparency. The right benchmark is "for what shape of question?", not "which one wins?"

The cheapest large wins from this comparison: **multi-persona critique** (split today's single reviewer into 2-3 personas), **Claims-Evidence Table** (load-bearing claims → sources → High/Med/Low confidence appended after the body), **`[uncertain]` markers** (prompt-level), **source-type histogram** (one-prompt change against existing `citations.jsonl`).

## Production-ready vs experimental

| Production-ready today | Experimental / proof-of-concept |
|---|---|
| OpenAI Deep Research, Perplexity Sonar Deep Research, Gemini DR, Claude Research, Grok DeepSearch [[1]](https://learn.g2.com/deepseek-vs-grok) | smolagents Open Deep Research — context-window blow-ups, unstable demo [[16]](https://huggingface.co/blog/open-deep-research) |
| GPT-Researcher [[2]](https://github.com/assafelovic/gpt-researcher), open_deep_research [[3]](https://github.com/langchain-ai/open_deep_research), local-deep-researcher [[17]](https://github.com/langchain-ai/local-deep-researcher) | STORM — "cannot produce publication-ready articles" per authors [[5]](https://github.com/stanford-oval/storm) |
| Elicit Systematic Review [[19]](https://elicit.com/solutions/literature-review), FutureHouse Crow/Falcon/Owl [[20]](https://www.futurehouse.org/research-announcements/launching-futurehouse-platform-ai-agents) | FutureHouse Phoenix — "not as deeply benchmarked, may make more mistakes" [[20]](https://www.futurehouse.org/research-announcements/launching-futurehouse-platform-ai-agents) |
| 199-biotech Claude skill [[4]](https://github.com/199-biotechnologies/claude-deep-research-skill), Weizhena skill [[18]](https://github.com/Weizhena/Deep-Research-skills) | Claude Managed Agents — public beta, April 2026 [[12]](https://platform.claude.com/docs/en/managed-agents/overview) |
