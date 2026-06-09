---
layout: expedition
title: "Audit and harden text-to-SQL pipelines (2026)"
date: 2026-06-09
topic: "Audit and harden text-to-SQL pipelines: from naive LLM query generation to safe, schema-grounded, read-only execution with pgvector semantic row search (2026)."
format: md
tags: [text-to-sql, postgresql, pgvector, llm-safety, schema-grounding]
summary: "A layered defense guide for text-to-SQL pipelines: schema grounding, read-only enforcement, query validation, pgvector semantic search, and the silent correctness failures that survive all of them."
cover: cover.svg
synthesis: true
children:
  - slug: naive-text-to-sql-failure-modes
    title: "Naive text-to-SQL failure modes"
    depth: deep
    status: success
    summary: "The dangerous failures aren't crashes — ~97% of wrong LLM-generated SQL executes cleanly and returns a plausible, wrong number. A field guide to the failure modes and the hardening stack that contains them."
    citations: 41
    reading_time_min: 8
  - slug: schema-grounding-strategies
    title: "Schema grounding strategies"
    depth: deep
    status: success
    summary: "How to stop an LLM from hallucinating columns: the layered stack of schema linking, representation, retrieval, and execution feedback that grounds text-to-SQL in a real database."
    citations: 42
    reading_time_min: 11
  - slug: read-only-enforcement-and-least-privilege-roles
    title: "Read-only enforcement and least-privilege roles"
    depth: standard
    status: success
    summary: "A database-layer enforcement guide: create purpose-built read-only roles, add column/row filtering, and use read replicas as physical write boundaries for LLM-generated SQL."
    citations: 25
    reading_time_min: 8
  - slug: query-validation-and-safety-gates
    title: "Query validation and safety gates"
    depth: standard
    status: success
    summary: "A five-layer defense-in-depth pipeline for validating LLM-generated SQL — from statement allowlists and AST structural checks through semantic schema binding, policy injection, and database-level enforcement — with evidence logging and emerging threat coverage."
    citations: 20
    reading_time_min: 8
  - slug: pgvector-semantic-row-search
    title: "pgvector semantic row search"
    depth: deep
    status: success
    summary: "How pgvector does nearest-neighbor row retrieval, how to index and filter it without wrecking recall, and how to use it to ground a text-to-SQL pipeline."
    citations: 40
    reading_time_min: 8
  - slug: observability-and-audit-logging
    title: "Observability and audit logging"
    depth: ceo
    status: success
    summary: "Observability helps teams debug production; audit logging proves compliance and accountability."
    citations: 7
    reading_time_min: 2
  - slug: multi-tenant-and-row-level-security
    title: "Multi-tenant and row-level security"
    depth: ceo
    status: success
    summary: "PostgreSQL RLS is the most cost-efficient multi-tenant isolation pattern, but requires runtime session variables, non-owner roles, and rigorous testing to prevent data leaks."
    citations: 5
    reading_time_min: 3
cost_usd: 19.69
duration_sec: 3172
citations: 180
reading_time_min: 48
issue: 209
model: "Sonnet 4.6"
---

The dangerous failures are silent. [Research into failure modes](naive-text-to-sql-failure-modes/) established that ~97% of wrong LLM-generated SQL executes cleanly and returns a plausible but incorrect number — crashes are not the threat model. This shapes everything downstream: every safeguard layer must operate at the **semantic** level, not just the syntactic.

**The hardening stack has a natural ordering.** Read-only role enforcement is the cheapest, most reliable boundary and should be deployed first. [Schema grounding](schema-grounding-strategies/) — preventing hallucinated tables and columns — must precede [query validation](query-validation-and-safety-gates/) (AST structural checks, allowlists) because you cannot validate references you haven't resolved. [Row-level security](multi-tenant-and-row-level-security/) and [observability](observability-and-audit-logging/) anchor the ends: RLS is a database-layer contract that no application code can override; observability is the only mechanism for detecting silent correctness failures in production.

**Schema grounding and query validation pull in opposite directions philosophically.** [Schema grounding research](schema-grounding-strategies/) favors LLM-based methods: function-calling schema injection, RAG over schema embeddings, and LLM self-reflection as a correction pass. [Query validation research](query-validation-and-safety-gates/) favors deterministic methods: SQL parsers, AST analysis, statement allowlists. The tension is real — LLM-based correction is more flexible but non-auditable; AST checks are auditable but cannot catch semantic hallucinations. A production pipeline needs both: deterministic AST checks for structural safety, LLM-mediated grounding for semantic accuracy.

**Prompt injection is the residual threat that deterministic layers cannot close.** If a user embeds SQL fragments or schema-altering phrases in their natural-language input, function-calling injection and AST validation may both pass without flagging anything. The only hard containment is the database layer — [read-only roles](read-only-enforcement-and-least-privilege-roles/) (no DML regardless of query content) and [RLS](multi-tenant-and-row-level-security/) (no cross-tenant rows regardless of WHERE clause). These are not optional optimizations; they are the backstop for everything above them.

**pgvector extends the paradigm, it doesn't replace it.** Semantic row search — embedding row content and querying by cosine similarity — answers questions that SQL cannot express compactly. The [pgvector research](pgvector-semantic-row-search/) shows that hybrid SQL+vector queries (WHERE-clause filtering combined with ANN search using HNSW or IVFFlat) are the production pattern, not pure vector retrieval. Index parameter tuning (`ef_construction`, `m`, `lists`) has a direct recall/throughput tradeoff that must be measured per workload; defaults are rarely appropriate at scale.

**Coverage gaps in this expedition.** Observability and audit logging were researched at a shallow depth (2-minute read, 7 citations). The multi-tenant/RLS angle received similarly light treatment (3-minute read, 5 citations). Both areas warrant dedicated deep-research runs — particularly around structured logging schemas for LLM query pipelines, anomaly detection over query patterns, and RLS policy testing frameworks.

The open question after all guards are in place: **semantic correctness is unverifiable without ground-truth labels.** A well-grounded, structurally valid query can silently aggregate on the wrong time window, join on the wrong key, or misinterpret an ambiguous column name. No current automated technique reliably detects this class of error at inference time — and whether LLM self-grading of result plausibility is reliable enough for production quality gates remains the most consequential unresolved question in the text-to-SQL safety literature.
