---
layout: expedition
title: "Session blueprint: RAG & Embeddings — from demos in 5 minutes to a production-grade pipeline (2026)"
date: 2026-06-09
topic: "Session blueprint: RAG & Embeddings — from \"demos in 5 minutes\" to a production-grade pipeline (2026)."
format: md
tags: [rag, embeddings, hybrid-search, production, evaluation]
summary: "A 90–120 min expert session blueprint covering the full RAG production stack — from embedding and naive failure modes through hybrid search, reranking, hallucination guardrails, and evaluation."
cover: cover.svg
synthesis: true
children:
  - slug: corpus-embedding-indexing
    title: "Corpus embedding & indexing"
    depth: standard
    status: success
    summary: "Model selection, chunking strategies, ANN algorithms, and vector DB trade-offs for production RAG pipelines in 2026."
    citations: 22
    reading_time_min: 7
  - slug: naive-rag-failure-modes-live-demo
    title: "Naive RAG failure modes (live demo)"
    depth: ceo
    status: success
    summary: "The 7 failure modes of naive RAG systems and why retrieval—not generation—is the bottleneck."
    citations: 5
    reading_time_min: 2
  - slug: chunking-strategies
    title: "Chunking strategies"
    depth: standard
    status: success
    summary: "How to choose and tune chunking strategies for production RAG: from recursive baselines to contextual retrieval, with benchmarks and a decision framework."
    citations: 12
    reading_time_min: 6
  - slug: hybrid-search-reranking
    title: "Hybrid search & reranking"
    depth: standard
    status: success
    summary: "How to combine BM25 and dense vector search via RRF, then apply cross-encoder reranking — with model comparison tables, platform support matrix, and tuning guidance."
    citations: 22
    reading_time_min: 6
  - slug: i-don-t-know-guardrail
    title: "\"I don't know\" guardrail"
    depth: standard
    status: success
    summary: "How to make a RAG pipeline say 'I don't know' instead of hallucinating — prompt patterns, retrieval thresholds, output-scoring rails, and evaluation metrics."
    citations: 16
    reading_time_min: 5
  - slug: session-arc-live-coding-scaffold
    title: "Session arc & live-coding scaffold"
    depth: standard
    status: success
    summary: "Blueprint for a 90-minute RAG workshop: 5-minute hook demo, five escalating production layers, and a git-branch scaffold that lets participants follow along or jump to any checkpoint."
    citations: 15
    reading_time_min: 4
  - slug: rag-evaluation
    title: "RAG evaluation"
    depth: ceo
    status: success
    summary: "RAG systems require dual-stage evaluation—retrieval metrics (precision@k, recall) and generation metrics (faithfulness, hallucination). RAGAS and ARES lead the frameworks; tools like DeepEval and TruLens enable production evaluation."
    citations: 9
    reading_time_min: 2
  - slug: observability-tracing
    title: "Observability & tracing"
    depth: ceo
    status: success
    summary: "Observability is built on three pillars—traces, metrics, and logs—with distributed tracing now essential for microservices. OpenTelemetry is the vendor-neutral standard; teams adopt hybrid models combining open-source backends with SaaS platforms."
    citations: 8
    reading_time_min: 3
cost_usd: 6.31
duration_sec: 3333
citations: 109
reading_time_min: 35
issue: 207
model: "Sonnet 4.6"
---

Every fix in this session is a retrieval fix. The [naive RAG failure modes research](naive-rag-failure-modes-live-demo/) identifies seven production failure modes; six of them — semantic drift, boundary bleed, lost-in-the-middle degradation, sparse-term mismatch, missing context for ambiguous queries, and over-retrieval noise — are retrieval failures, not generation failures [[1]](naive-rag-failure-modes-live-demo/). This is the organizing principle that gives the session its arc: each subsequent layer (chunking, hybrid search, reranking, the guardrail) is not a feature addition but a targeted retrieval patch.

**The compounding cost problem must be made visible early.** [Corpus embedding & indexing](corpus-embedding-indexing/) documents a 3–4× latency spread across embedding model tiers alone [[2]](corpus-embedding-indexing/); [chunking strategies](chunking-strategies/) add preprocessing overhead that scales with corpus size; [hybrid search and reranking](hybrid-search-reranking/) introduces a cross-encoder pass that typically adds 50–200 ms per query [[3]](hybrid-search-reranking/); and the ["I don't know" guardrail](i-don-t-know-guardrail/) adds an output-scoring step on top [[4]](i-don-t-know-guardrail/). Each layer is justified in isolation, but participants leave with a system that is simply too slow to ship unless cumulative P95 latency is measured at every checkpoint. The [session arc scaffold](session-arc-live-coding-scaffold/) should wire a `time.perf_counter` block around the full pipeline from the first segment and print it after each live-coding step so the cost graph builds in front of the room [[5]](session-arc-live-coding-scaffold/).

**The contextual retrieval moment is the sharpest debate catalyst.** Anthropic's contextual retrieval technique — prepending a generated context summary to each chunk before embedding — is documented in the [chunking strategies research](chunking-strategies/) as producing step-change recall improvements [[6]](chunking-strategies/). The catch: it roughly doubles embedding cost per document and requires a prompt call per chunk at index time. For an expert audience, this is not a settled best practice; it is a trade-off that maps directly to whether the corpus is updated daily (cost matters) or indexed once (cost less so). The facilitator should surface this as an open vote: *raise your hand if your corpus ingests more than 10 000 documents per day.*

**Evaluation must precede optimization, not follow it.** The [RAG evaluation research](rag-evaluation/) and [observability research](observability-tracing/) converge on the same prescription: instrument the dual-stage metrics — retrieval precision@k and recall, generation faithfulness and hallucination rate — before any tuning begins [[7]](rag-evaluation/) [[8]](observability-tracing/). This contradicts the session arc as scaffolded, which introduces evaluation as a late segment. The facilitator fix: deploy a minimal [RAGAS](https://docs.ragas.io) harness in Segment 1 alongside the naive pipeline, then re-run it at each checkpoint. The quality graph across five stages is far more persuasive than a one-shot score at the end — and it makes the hallucination-rate drop after adding the guardrail visually undeniable.

**The "I don't know" guardrail is the only layer that touches generation.** All other layers improve what gets retrieved; the [guardrail research](i-don-t-know-guardrail/) is the only segment that intervenes *after* retrieval by scoring whether the retrieved context actually supports the answer before returning it [[9]](i-don-t-know-guardrail/). This makes it the natural final layer — but it also means it is sensitive to retrieval quality in the preceding layers. A guardrail tuned on naive retrieval will over-trigger (too many "I don't know" responses); the same threshold after hybrid search + reranking will be appropriately tight. Facilitators should run the guardrail demo *twice*: once on the naive pipeline to show false abstentions, once after reranking to show it calibrating correctly.

**The open question expert participants will ask first:** at what corpus size does an in-process vector store (FAISS, LanceDB) break down and force a managed service migration? The [corpus embedding & indexing research](corpus-embedding-indexing/) covers ANN algorithm trade-offs and managed-vs-self-hosted DB options but stops short of a concrete inflection-point benchmark [[10]](corpus-embedding-indexing/). The honest facilitator answer is: *it depends on query concurrency, not corpus size alone* — a 10 M-vector corpus served by a single-process FAISS index collapses under 50 concurrent users; a managed Qdrant or Weaviate cluster handles the same load at 100 M vectors. That framing, not a number, is the correct answer to give the room.
