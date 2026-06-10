---
title: "Session arc & live-coding scaffold"
date: 2026-06-09
depth: standard
format: md
topic: "Session arc & live-coding scaffold"
topic_raw: "Session arc & live-coding scaffold"
issue: 207
tags: [rag, live-coding, workshop, session-design, talk-prep, embeddings]
summary: "Blueprint for a 90-minute RAG workshop: 5-minute hook demo, five escalating production layers, and a git-branch scaffold that lets participants follow along or jump to any checkpoint."
citations: 15
reading_time_min: 4
cover: cover.svg
cost_usd: 1.50
duration_sec: 644
model: "Sonnet 4.6"
---

> **TL;DR** Open with a ~40-line working RAG demo in 5 minutes [[1]](https://qdrant.tech/documentation/tutorials-build-essentials/rag-deepseek/), then *break it* with real production demands — each failure becomes the next live-coding step. Script the repo as `step-00` through `step-05` git branches so anyone who falls behind does `git checkout step-0N` and rejoins instantly. Pre-script every keystroke with [Demo Time](https://demotime.show/) [[2]](https://demotime.show/) to survive stage typos.

---

## Session arc

The 90-minute structure follows the hook → crack → fix loop validated by Packt's 6-hour production RAG workshop [[3]](https://llmengg.com/rag-pipeline-workshop/) and PyCon US 2026's 3.5-hour tutorial [[4]](https://us.pycon.org/2026/schedule/presentation/56/). For a 45-minute slot: drop segments 6–7 and compress 4+5 into one "retrieval upgrades" block (15 min).

| # | Segment          | Min | Goal                                                                                         |
|---|------------------|-----|----------------------------------------------------------------------------------------------|
| 0 | Setup            |  5  | Audience clones starter repo; speaker defines RAG in one sentence                           |
| 1 | Minimal demo     | 10  | ~40 lines live-coded (Qdrant + FastEmbed + LLM); query returns an answer; audience confident |
| 2 | Reality check    |  5  | Show failing test or prod log: "80% of RAG failures trace to ingestion, not the LLM" [[5]](https://arpitbhayani.me/blogs/rag-production/) |
| 3 | Chunking         | 15  | Fixed splits → recursive/semantic; 60–70% retrieval accuracy gain [[6]](https://www.roborhythms.com/how-to-build-production-rag-pipeline-2026/) |
| 4 | Query transform  | 10  | HyDE expansion; "20–40% precision boost for one extra LLM call" [[6]](https://www.roborhythms.com/how-to-build-production-rag-pipeline-2026/) |
| 5 | Hybrid + rerank  | 15  | BM25 + vector fusion + cross-encoder; "single biggest quality improvement" [[5]](https://arpitbhayani.me/blogs/rag-production/) |
| 6 | Observability    | 10  | Chunk-level trace dict; per-chunk source attribution (*drop first if overtime*)              |
| 7 | Guardrail        | 10  | Confidence gate at 0.65; "prevent confident hallucinations from irrelevant context" [[7]](https://medium.com/@visrow/how-to-design-a-rag-pipeline-for-10-million-documents-with-zero-hallucination-live-demo-057e37bcdbf6) |
| 8 | Q&A              | 10  | Open floor                                                                                   |

### Micro-arc per segment

Each segment repeats the same three-beat pattern: **show the failure → add the fix → run one query** and let the output speak. Presenting the solution before the audience has felt the failure raises extraneous cognitive load with no benefit [[8]](https://elearningindustry.com/reducing-cognitive-load-through-scaffolding). Display a running architecture diagram at the start of each segment, highlighting the newly added component; after five additions it *is* the production system.

---

## Live-coding scaffold

### Git branch structure

Workshops at AI Coding Summit 2026 with the strongest participant ratings [[9]](https://gitnation.com/events/ai-coding-summit-2026/talks) used the same recovery pattern: participants **clone the starter repo**, speaker **codes forward**, anyone who falls behind does `git checkout step-0N` and rejoins.

| Branch              | Contains                                                                                |
|---------------------|-----------------------------------------------------------------------------------------|
| `step-00-start`     | `rag.py` skeleton with `# TODO` stubs; `requirements.txt`; `.env.example`              |
| `step-01-minimal`   | ~40-line naive RAG: Qdrant + FastEmbed [[1]](https://qdrant.tech/documentation/tutorials-build-essentials/rag-deepseek/) |
| `step-02-chunking`  | `RecursiveCharacterTextSplitter` → semantic chunker [[10]](https://shantun.medium.com/the-only-rag-tutorial-you-need-in-2026-document-loading-chunking-embeddings-retrieval-with-b313fdc473b8) |
| `step-03-hybrid`    | BM25 + vector fusion (α param); Cohere Rerank 3.5 [[11]](https://www.kapa.ai/blog/how-to-build-a-rag-pipeline-from-scratch-in-2026) |
| `step-04-query`     | HyDE query expansion via one extra LLM call [[6]](https://www.roborhythms.com/how-to-build-production-rag-pipeline-2026/) |
| `step-05-prod`      | Observability trace dict; confidence gate; incremental ingestion loop [[5]](https://arpitbhayani.me/blogs/rag-production/) [[12]](https://dataengineeracademy.com/blog/production-rag-pipeline/) |

Each branch is **self-contained**: installs cleanly, all tests pass, running `python rag.py "What is chunking?"` returns a valid answer without additional setup. That is the recovery guarantee.

### Starter repo layout

```
rag-workshop/
├── rag.py                  # pipeline file (grows each step)
├── requirements.txt        # pinned versions
├── .env.example            # QDRANT_URL, OPENAI_API_KEY, DEEPSEEK_API_KEY
├── data/                   # sample PDF corpus ≤5 MB
├── tests/
│   └── test_pipeline.py    # pytest; new assertions added each step
└── STEPS.md                # one-line diff summary per branch (put on a slide)
```

`STEPS.md` is the single most useful file for participants — one line per branch stating exactly what changed. Put it on a slide before each live-coding segment.

---

## Embedding model choice

Use a **local, no-API-key model** for the opening demo to eliminate setup friction. `BAAI/bge-small-en-v1.5` ships inside `qdrant-client[fastembed]` and runs in <100 ms per query on any laptop [[1]](https://qdrant.tech/documentation/tutorials-build-essentials/rag-deepseek/). The switch to a production model is a one-line change — a strong "what's next" beat at the end of the session.

| Model                        | Tokens  | Where          | Workshop role                               |
|------------------------------|---------|----------------|---------------------------------------------|
| [`BAAI/bge-small-en-v1.5`][bge] | 512  | Local/FastEmbed | Steps 0–2 (no API key needed)            |
| [`text-embedding-3-small`][oai] | 8 191 | OpenAI API    | Steps 3–4 (upgrade beat)                  |
| [Gemini Embedding 2][gem]       | 32 000 | Google API   | "Production" reference slide [[13]](https://milvus.io/blog/choose-embedding-model-rag-2026.md) |

[bge]: https://huggingface.co/BAAI/bge-small-en-v1.5
[oai]: https://platform.openai.com/docs/guides/embeddings
[gem]: https://ai.google.dev/gemini-api/docs/embeddings

---

## Tooling

**[Demo Time](https://demotime.show/) [[2]](https://demotime.show/)** — VS Code extension used at NDC, Microsoft Ignite, and React Summit. Script every keystroke in advance; trigger each step with one hotkey; zero typo risk under pressure. Walk through all five steps the day before the talk.

**Recovery protocol**: Keep `git log --oneline` visible on screen while coding. If a live step fails and cannot be fixed in 60 seconds, say "Let's jump to the checkpoint" and `git checkout step-0N`. Transparency is more professional than a silent panic fix.

---

## Cognitive load management

The Gradual Release of Responsibility model (I do → we do → you do) [[8]](https://elearningindustry.com/reducing-cognitive-load-through-scaffolding) [[14]](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4673075/) maps cleanly onto the two delivery modes. For a 3–6 hour workshop (e.g. PyCon US 2026 format [[4]](https://us.pycon.org/2026/schedule/presentation/56/) or LangChain-based tutorials [[15]](https://docs.langchain.com/oss/python/langchain/rag)), defer the "you do" phase until participants have seen all five layers:

| Mode             | Segments | Pattern                                                                  |
|------------------|----------|--------------------------------------------------------------------------|
| Talk (45–90 min) | 1–7      | *I do*: speaker codes, audience watches; repo published post-session     |
| Workshop (3–6 h) | 1–2      | *I do*: speaker models; audience watches                                 |
| Workshop (3–6 h) | 3–4      | *We do*: `git checkout` each branch; participants code alongside speaker |
| Workshop (3–6 h) | 5–7      | *You do*: participants code a variant; speaker reviews live              |

One new concept per segment. Maximum two new library imports per step. The running architecture diagram is the scaffolding — it shows where each new piece fits without requiring participants to hold the entire mental model unaided.
