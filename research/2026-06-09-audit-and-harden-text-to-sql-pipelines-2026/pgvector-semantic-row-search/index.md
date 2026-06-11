---
title: "pgvector semantic row search: mechanics, indexing, and grounding text-to-SQL"
date: 2026-06-09
depth: deep
format: md
topic: "pgvector semantic row search"
topic_raw: "pgvector semantic row search"
issue: 209
tags: [pgvector, postgres, vector-search, rag, text-to-sql, embeddings]
summary: "How pgvector does nearest-neighbor row retrieval, how to index and filter it without wrecking recall, and how to use it to ground a text-to-SQL pipeline."
citations: 40
reading_time_min: 8
cost_usd: 5.06
duration_sec: 692
model: "Opus 4.8"
cover: cover.svg
---

> **Decision.** Use [pgvector](https://github.com/pgvector/pgvector) ⭐ 21.7k (Jun 2026) [[2]](https://api.github.com/repos/pgvector/pgvector) for semantic row search whenever your rows already live in Postgres [[1]](https://github.com/pgvector/pgvector) — co-locating embeddings with relational data is the whole point, since similarity search then composes with `WHERE`, `JOIN`, and full-text in one transactionally-consistent query [[23]](https://supabase.com/docs/guides/ai/vector-columns). Default to an **HNSW** index [[6]](https://supabase.com/blog/increase-performance-pgvector-hnsw), upgrade to **pgvector ≥ 0.8.0** so filtered searches don't silently under-return [[10]](https://www.postgresql.org/about/news/pgvector-080-released-2952/), and reach for a dedicated store (Qdrant, Pinecone, Milvus) or [pgvectorscale](https://github.com/timescale/pgvectorscale) ⭐ 3.0k only past ~5–10M vectors [[25]](https://www.kalviumlabs.ai/blog/vector-databases-compared-pgvector-pinecone-qdrant-weaviate/)[[9]](https://www.instaclustr.com/education/vector-database/pgvector-performance-benchmark-results-and-5-ways-to-boost-performance/). **For text-to-SQL specifically, the killer use is value linking**: embed a column's distinct values and semantic-search the user's entity against them so the LLM filters on a real stored value instead of a hallucinated one [[15]](https://arxiv.org/pdf/2510.17586).

## How semantic row search works in pgvector

pgvector adds vector column types to Postgres that store embeddings next to your rows. Four types cover the range of embedding shapes [[1]](https://github.com/pgvector/pgvector)[[3]](https://github.com/pgvector/pgvector/blob/master/CHANGELOG.md):

| Type        | Storage          | Max dims     | Indexable to | Use for                         |
| ----------- | ---------------- | ------------ | ------------ | ------------------------------- |
| `vector`    | 4 bytes/dim      | 16,000       | 2,000        | standard float embeddings       |
| `halfvec`   | 2 bytes/dim      | 16,000       | 4,000        | large embeddings, half the RAM  |
| `sparsevec` | non-zero only    | 16,000 nz    | 1,000 nz     | sparse / lexical vectors        |
| `bit`       | 1 bit/dim        | 64,000       | 64,000       | binary / quantized embeddings   |

[1]: https://github.com/pgvector/pgvector
[3]: https://github.com/pgvector/pgvector/blob/master/CHANGELOG.md
[8]: https://www.thenile.dev/blog/pgvector_myth_debunking

The column dimension must match the embedding model's output — e.g. `vector(1536)` for OpenAI `text-embedding-3-small` [[4]](https://www.instaclustr.com/education/vector-database/pgvector-key-features-tutorial-and-pros-and-cons-2026-guide/). Embeddings are generated **outside** the database: the app calls an embedding model, gets a float array back, and writes that array into the column [[4]](https://www.instaclustr.com/education/vector-database/pgvector-key-features-tutorial-and-pros-and-cons-2026-guide/)[[5]](https://supabase.com/docs/guides/database/extensions/pgvector).

Similarity is expressed with four distance operators [[1]](https://github.com/pgvector/pgvector): `<->` Euclidean/L2, `<#>` negative inner product, `<=>` cosine distance, `<+>` taxicab/L1. Nearest-neighbor retrieval is just an ordered scan with a `LIMIT` [[1]](https://github.com/pgvector/pgvector)[[5]](https://supabase.com/docs/guides/database/extensions/pgvector):

```sql
CREATE EXTENSION vector;
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(1536));
-- app inserts the model's output array:
INSERT INTO items (embedding) VALUES ('[0.12, -0.03, ...]');

-- k nearest rows to a query vector, optionally with a relational filter:
SELECT * FROM items
WHERE category_id = 123
ORDER BY embedding <=> $1::vector   -- cosine distance is the common RAG choice
LIMIT 5;
```

That `ORDER BY embedding <=> query LIMIT k` shape is the entire primitive — every higher-level RAG and text-to-SQL pattern below is built on it [[4]](https://www.instaclustr.com/education/vector-database/pgvector-key-features-tutorial-and-pros-and-cons-2026-guide/).

## Indexing: HNSW vs IVFFlat

Without an index, every query is an exact full scan. The two index types trade build cost for query quality. **HNSW is the recommended default in nearly all 2024–2026 guidance** [[6]](https://supabase.com/blog/increase-performance-pgvector-hnsw) — Supabase measured it at ~3× IVFFlat throughput on 224k 1536-dim vectors and >6× on 1M vectors at accuracy@10=0.98, even beating Qdrant on equal compute [[6]](https://supabase.com/blog/increase-performance-pgvector-hnsw).

| Axis           | HNSW                                              | IVFFlat                                            |
| -------------- | ------------------------------------------------- | -------------------------------------------------- |
| Quality        | higher recall at a given speed [[6]][[7]]         | lower, and frozen at build time [[7]]              |
| Build cost     | slow, memory-hungry [[7]]                         | fast, light [[7]]                                  |
| Build timing   | can build before data loads                       | needs representative data first (k-means) [[7]]    |
| Key knobs      | `m`, `ef_construction` (build); `ef_search` (query) | `lists` (build); `probes` (query) [[7]]          |

[6]: https://supabase.com/blog/increase-performance-pgvector-hnsw
[7]: https://neon.com/docs/ai/ai-vector-search-optimization

**HNSW knobs** [[7]](https://neon.com/docs/ai/ai-vector-search-optimization): `m` = max connections per node (default 16, useful ~12–48; higher = better recall, more memory and build time); `ef_construction` = build-time candidate list (default 64, set ≥ 2× `m`); `ef_search` = query-time candidate list (default 40, **set ≥ your `LIMIT k`** — this matters for filtering, below). **IVFFlat knobs** [[7]](https://neon.com/docs/ai/ai-vector-search-optimization): `lists` ≈ rows/1000 up to 1M rows (else √rows), `probes` starting at lists/10 or √lists.

Two hard limits to plan around: indexed `vector` columns cap at **2,000 dimensions**, which blocks indexing 3,072-dim `text-embedding-3-large` unless you switch to `halfvec` (doubles the limit to 4,000) [[8]](https://www.thenile.dev/blog/pgvector_myth_debunking). And the HNSW graph should fit in RAM — ~150GB+ for 50M 768-dim vectors — beyond which performance falls off a cliff [[9]](https://www.instaclustr.com/education/vector-database/pgvector-performance-benchmark-results-and-5-ways-to-boost-performance/). Builds run **10–50× slower** once the graph exceeds `maintenance_work_mem` [[30]](https://github.com/pgvector/pgvector/issues/969).

## Filtering and hybrid search (read this before production)

The single biggest pgvector footgun for **row** search is filtered queries. With an approximate index, the `WHERE` filter is applied **after** the index returns its `ef_search` candidate pool [[28]](https://dev.to/franckpachot/no-pre-filtering-in-pgvector-means-reduced-ann-recall-1aa1). So with the default `ef_search = 40`, a filter matching 10% of rows leaves on average **~4 rows** — and a `LIMIT 10` silently returns fewer rows than asked, even when many matching rows exist [[31]](https://www.thenile.dev/blog/pgvector-080)[[11]](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/).

**pgvector 0.8.0 (2024-10-30) fixes this with iterative index scans** [[10]](https://www.postgresql.org/about/news/pgvector-080-released-2952/): the index keeps scanning until enough rows satisfy both the distance order and the filter, bounded by `hnsw.max_scan_tuples` (default 20,000) [[31]](https://www.thenile.dev/blog/pgvector-080). Set it via `hnsw.iterative_scan`:

- `relaxed_order` — slightly out-of-order results, better recall; **the recommended default** [[12]](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/).
- `strict_order` — exact distance order; reserve for ranking-critical paths [[12]](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/).

AWS measured filtered-query recall rising from 1–10% to 100% and queries up to 9.4× faster (123.3ms → 13.1ms) with 0.8.0 on Aurora [[11]](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/). For low-cardinality filters, **partial indexes** (`CREATE INDEX ... WHERE category = 'x'`) are the alternative [[12]](https://www.dbi-services.com/blog/pgvector-a-guide-for-dba-part-2-indexes-update-march-2026/).

**Hybrid search** combines semantic and lexical matching. Add a `STORED` generated `tsvector` column with a GIN index alongside the HNSW index, run both searches, and fuse them with **reciprocal rank fusion** — `score = Σ 1/(k + rank)`, `k = 60` — over-fetching ~20 candidates per side [[13]](https://dev.to/lpossamai/building-hybrid-search-for-rag-combining-pgvector-and-full-text-search-with-reciprocal-rank-fusion-6nk). RRF combines *rankings* not raw scores, so the disparate distance/BM25 score scales never need normalizing [[14]](https://dev.to/gabrielanhaia/hybrid-search-in-100-lines-bm25-pgvector-with-rrf-merge-58cn).

## Grounding a text-to-SQL pipeline

This is the payoff for an audit-and-harden text-to-SQL context: semantic row search attacks three distinct failure modes of naive LLM SQL generation.

**1. Value linking / entity resolution — the highest-value pattern.** A naive LLM writes `WHERE company = 'Apple'` when the table actually stores `'Apple Inc.'`, producing a query that runs but returns nothing. DeepEye-SQL's *Semantic Value Retrieval* module extracts the unique values from TEXT columns — "the primary source of ambiguity and value-related hallucinations" — embeds them, and feeds the LLM a relevant subset of **real** stored values before generation [[15]](https://arxiv.org/pdf/2510.17586). The pgvector recipe: embed a categorical column's distinct values, semantic-search the user's entity against them, substitute the canonical match. The open-source [CHESS](https://github.com/ShayanTalaei/CHESS) ⭐ 273 (Jun 2026) framework does exactly this — its retriever builds LSH + vector indices per database so question keywords resolve to real cell values before generation [[37]](https://github.com/ShayanTalaei/CHESS); practitioners frame the identical problem (e.g. "online-only schools" must map to the stored code `F`) [[38]](https://medium.com/data-science-collective/how-i-solved-text-to-sql-value-linking-without-pre-embedding-thousands-of-database-samples-1d1bb86e1e10).

**2. Few-shot gold-SQL retrieval.** [Vanna.AI](https://github.com/vanna-ai/vanna) ⭐ 23.6k (Jun 2026) embeds DDL, business docs, and example SQL into a vector store, then retrieves the 10 most-similar pieces per question to build the prompt [[16]](https://github.com/vanna-ai/vanna)[[17]](https://qdrant.tech/documentation/frameworks/vanna-ai/). [DAIL-SQL](https://github.com/BeachWang/DAIL-SQL) ⭐ 635 (Jun 2026) refines this with *dual* similarity — rank by masked-question similarity, then filter by SQL-query similarity — reaching 86.6% execution accuracy on Spider (with GPT-4) [[18]](https://github.com/BeachWang/DAIL-SQL).

**3. Schema linking for large schemas.** Embed column descriptions and retrieve only the top-k relevant columns per query keyword by semantic similarity, shrinking a 200-table schema down to what the LLM actually needs [[20]](https://www.mdpi.com/2076-3417/16/2/586). LlamaIndex's `PGVectorSQLQueryEngine` shows the unified pattern — the LLM emits SQL using pgvector's `<->` operator with a `[query_vector]` placeholder, doing semantic ranking and structured `WHERE` filtering in one statement [[19]](https://developers.llamaindex.ai/python/examples/query_engine/pgvector_sql_query_engine/).

## pgvector vs dedicated vector stores

The decisive pgvector advantage for *row* search is locality: vectors are a native column, so search composes with arbitrary SQL and stays transactionally consistent — no second system to sync, one ACID transaction, one bill [[23]](https://supabase.com/docs/guides/ai/vector-columns). The 2026 consensus: **pgvector if you already run Postgres; a dedicated store only at a measurable limit** [[25]](https://www.kalviumlabs.ai/blog/vector-databases-compared-pgvector-pinecone-qdrant-weaviate/)[[24]](https://callsphere.ai/blog/vector-database-benchmarks-2026-pgvector-qdrant-weaviate-milvus-lancedb).

| Store          | Stars (Jun 2026) [[27]] | Best at                                  | Rough throughput [[24]] |
| -------------- | ----------------------- | ---------------------------------------- | ----------------------- |
| [pgvector][p]  | ⭐ 21.7k                | rows already in Postgres, SQL filters    | ~5–15K QPS              |
| [Qdrant][q]    | ⭐ 32k                  | fastest filtered search                  | ~30–80K QPS             |
| [Weaviate][w]  | ⭐ 16.3k                | built-in hybrid search                   | ~25–50K QPS             |
| [Milvus][m]    | ⭐ 44.7k                | billion-vector scale                     | 100K+ QPS               |
| Pinecone       | (managed)               | operational ease at 5M+                  | managed                 |

[p]: https://github.com/pgvector/pgvector
[q]: https://qdrant.tech
[w]: https://weaviate.io
[m]: https://milvus.io
[27]: https://github.com/timescale/pgvectorscale
[24]: https://callsphere.ai/blog/vector-database-benchmarks-2026-pgvector-qdrant-weaviate-milvus-lancedb

Treat the throughput column as order-of-magnitude only — independent benchmarks show the verdict flips with index type and scale. On 1M vectors Qdrant beat pgvector's older IVF index ~15× on throughput [[39]](https://nirantk.com/writing/pgvector-vs-qdrant/), yet on 50M vectors pgvector + pgvectorscale hit 471 QPS vs Qdrant's 41 QPS at 99% recall [[40]](https://www.firecrawl.dev/blog/best-vector-databases) — HNSW and pgvectorscale change the picture entirely.

If you want to stay in Postgres but outgrow vanilla pgvector, [pgvectorscale](https://github.com/timescale/pgvectorscale) ⭐ 3.0k (Jun 2026) adds StreamingDiskANN (disk-resident index), Statistical Binary Quantization, and label-based filtered search [[22]](https://github.com/timescale/pgvectorscale/blob/main/README.md). Tiger Data's (vendor) benchmark on 50M 768-dim vectors claims 28× lower p95 latency, 16× higher throughput, and ~75% lower cost ($835 vs $3,241/mo) than Pinecone's s1 tier at 99% recall — treat the figures as vendor-biased but directionally real [[21]](https://www.tigerdata.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost). At 100M vectors, self-hosting Qdrant/Weaviate/Milvus (~$600–1,200/mo) clearly undercuts Pinecone pods ($4,000–7,000+) [[26]](https://tensoria.fr/en/blog/vector-database-comparison).

## When pgvector breaks down (the skeptic's view)

A widely-discussed ["case against pgvector"](https://news.ycombinator.com/item?id=45798479) crystallized the production caveats [[34]](https://news.ycombinator.com/item?id=45798479):

- **Resource contention.** Vector workloads share CPU, memory, and IO with your OLTP traffic — a burst of vector queries can starve transactional queries of buffer cache and parallel workers [[35]](https://simonwillison.net/2025/Nov/3/the-case-against-pgvector/).
- **Build time at scale.** A real 40M-row/768-dim partition stalled at 29.2% after 19+ hours even at 40GB `maintenance_work_mem` [[29]](https://github.com/pgvector/pgvector/issues/822); a few million vectors can eat 10+GB RAM to build [[33]](https://alex-jacobs.com/posts/the-case-against-pgvector/).
- **Index bloat.** HNSW deletes don't reclaim space, causing bloat and recall drift over time; native sharding across nodes isn't supported [[32]](https://www.paradedb.com/learn/postgresql/pgvector-limitations).
- **Embedding freshness.** Stale embeddings silently degrade retrieval, and the real cost is coordinating backfills and observing which rows changed, not the embedding API calls [[36]](https://www.dbi-services.com/blog/rag-series-embedding-versioning-with-pgvector-why-event-driven-architecture-is-a-precondition-to-ai-data-workflows/).

Net: pgvector is the right default for semantic row search up to single-instance scale with moderate filter selectivity. Past ~5–10M vectors, or when vector load threatens your OLTP path, plan for pgvectorscale or a dedicated store [[9]](https://www.instaclustr.com/education/vector-database/pgvector-performance-benchmark-results-and-5-ways-to-boost-performance/)[[33]](https://alex-jacobs.com/posts/the-case-against-pgvector/). Note that limitation sources [[32]](https://www.paradedb.com/learn/postgresql/pgvector-limitations) come from competitors (ParadeDB) — credible on the mechanics, motivated on the conclusion.
