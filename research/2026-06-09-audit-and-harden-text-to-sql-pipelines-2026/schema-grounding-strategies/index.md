---
title: "Schema Grounding Strategies for Text-to-SQL"
date: 2026-06-09
depth: deep
format: md
topic: "Schema grounding strategies"
topic_raw: "Schema grounding strategies"
issue: 209
tags: [text-to-sql, llm, schema-linking, rag, data-engineering]
summary: "How to stop an LLM from hallucinating columns: the layered stack of schema linking, representation, retrieval, and execution feedback that grounds text-to-SQL in a real database."
cover: cover.svg
citations: 42
reading_time_min: 11
cost_usd: 5.97
duration_sec: 558
model: "Opus 4.8"
---

> **Decision.** Schema grounding is a *stack*, not a single trick. Build it in this order: **(1)** serialize the schema as `CREATE TABLE` DDL or M-Schema with types, keys, descriptions, and a few sample values [[6]](https://arxiv.org/pdf/2308.15363)[[8]](https://arxiv.org/html/2411.08599v1); **(2)** on a small/medium DB with a strong reasoning model, **feed the whole schema** — explicit schema-linking filters can now *hurt* top models [[29]](https://arxiv.org/html/2408.07702v1); **(3)** above ~a few hundred columns, switch to embedding retrieval + pruning to fit context and kill noise [[13]](https://spider2-sql.github.io/)[[16]](https://arxiv.org/html/2510.09014); **(4)** always close the loop with **execution feedback + self-correction**, the single most reliable accuracy lever [[23]](https://arxiv.org/html/2312.11242v2). For enterprise reliability, ground on a **semantic layer**, not the raw schema — dbt reports 83% vs ~40% NL-query accuracy [[41]](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026).

## The problem: naive prompting hallucinates schema

Hand an LLM a question and a bare table dump and it will confidently reference columns that don't exist, join on the wrong keys, and miss the table that actually holds the answer. The failure scales with the database. Frontier models score **86.6% on Spider 1.0** but collapse to **10.1% (GPT-4o)** and **17.1% (o1-preview)** on Spider 2.0, whose enterprise databases routinely exceed 1,000 columns and sometimes 3,000 — most of the loss is schema-linking error over thousands of columns [[13]](https://spider2-sql.github.io/). Grounding is the set of techniques that close that gap: aligning the question to the right schema elements, presenting them in a form the model reads well, and verifying the output against the database itself.

Four layers, each catching a different failure mode:

| Layer | Grounds against | Catches | Key techniques |
|---|---|---|---|
| **Linking / selection** | which tables & columns are relevant | irrelevant context, wrong table | string match, embedding retrieval, LLM selection [[4]](https://arxiv.org/html/2408.05109v5) |
| **Representation** | how the schema is written into the prompt | misread types, missed keys/values | DDL, M-Schema, sample rows, descriptions [[6]](https://arxiv.org/pdf/2308.15363)[[8]](https://arxiv.org/html/2411.08599v1) |
| **Retrieval / pruning** | fitting large schemas in context | context overflow, top-k noise | vector search, clustering, chunking [[16]](https://arxiv.org/html/2510.09014)[[18]](https://www.mdpi.com/2076-3417/16/2/586) |
| **Validation / correction** | the generated SQL vs the live DB | hallucinated columns, runtime errors | grammar decoding, execute-and-repair, voting [[19]](https://arxiv.org/abs/2109.05093)[[23]](https://arxiv.org/html/2312.11242v2) |

## Layer 1 — Schema linking & selection

**Schema linking** aligns the natural-language question with the database elements the SQL must reference; a 2024 survey calls it "essential" and notes it became *more* critical in the LLM era because of input-length limits [[4]](https://arxiv.org/html/2408.05109v5). The field evolved through three eras [[4]](https://arxiv.org/html/2408.05109v5):

- **String matching.** The classic [RAT-SQL](https://ar5iv.labs.arxiv.org/html/1911.04942) matches question n-grams (length 1–5) against column/table names as exact / partial (subsequence) / no-match, then encodes those as directional relation labels feeding a relation-aware encoder [[1]](https://ar5iv.labs.arxiv.org/html/1911.04942).
- **Neural alignment.** Deep models learn question↔schema attention rather than relying on surface string overlap [[4]](https://arxiv.org/html/2408.05109v5).
- **LLM in-context selection.** Modern systems retrieve or have the LLM *pick* the relevant subset before generation [[4]](https://arxiv.org/html/2408.05109v5).

Why bother narrowing at all? Because feeding the full schema "introduces irrelevant context, increases token overhead, and often leads to hallucinations" [[2]](https://arxiv.org/html/2510.14296v2), and [CHESS](https://arxiv.org/html/2405.16755v1) confirms that "providing an LLM with all available information can confuse the model" [[5]](https://arxiv.org/html/2405.16755v1).

The hard part is a **recall vs. false-positive tradeoff**: miss a needed table and the query is impossible; include junk and the model gets confused. Measured: CHESS hits 97.12% recall but at 30.57% false-positive rate; RSL-SQL hits 93.28% recall at a punishing 68.23% FPR — motivating **bidirectional** (table-first ∪ column-first) retrieval to balance the two [[2]](https://arxiv.org/html/2510.14296v2). A clever inversion is [CRUSH4SQL](https://arxiv.org/abs/2311.01173): have the LLM *hallucinate* a minimal ideal schema for the question, then dense-retrieve the real elements that resemble it — scaling to 17,844-element databases with higher recall than prior retrieval [[3]](https://arxiv.org/abs/2311.01173).

### The twist: schema linking may be dying for strong models

A 2024 study provocatively titled *"The Death of Schema Linking?"* found that with strong reasoning models, **full-schema prompting reaches 94.62% EX** and explicit linking filters cause net losses — Gemini 1.5 Pro sees a *reduction* in execution accuracy when schema linking is applied, while weaker models still benefit from filtering [[29]](https://arxiv.org/html/2408.07702v1). The practical reading: schema linking is a context-management tool, not an accuracy tool per se. If your schema fits comfortably in context and your model reasons well, skip the filter. If it doesn't fit, you have no choice — proceed to Layer 3.

## Layer 2 — Schema representation

Once you know *which* elements to include, *how* you write them into the prompt measurably moves accuracy. The [DAIL-SQL](https://arxiv.org/pdf/2308.15363) study compared five question representations across four LLMs and concluded the **Code Representation** prompt (schema as SQLite `CREATE TABLE` DDL with types, primary keys, and foreign-key declarations) and the **OpenAI Demonstration** prompt are preferred — they sit closest to actual SQL, so the model translates less prose into operations [[6]](https://arxiv.org/pdf/2308.15363). The full DAIL-SQL pipeline reached **83.5% EX on Spider-dev / 86.6% on the leaderboard** with GPT-4 [[7]](https://github.com/BeachWang/DAIL-SQL) ⭐ 635.

Alibaba's [XiYan-SQL](https://arxiv.org/html/2411.08599v1) advanced the format with **M-Schema** — a semi-structured representation using special tokens for the database, `# Table`, and `Foreign Keys`, encoding each column as a tuple of *(name, data type, description, primary-key flag, example values)* [[8]](https://arxiv.org/html/2411.08599v1). Derived from MAC-SQL's schema, it is more compact than DDL yet adds explicit types, PK markings, richer descriptions pulled from the database, and refined sample-value display rules [[9]](https://www.marktechpost.com/2024/11/19/alibaba-research-introduces-xiyan-sql-a-multi-generator-ensemble-ai-framework-for-text-to-sql/). In ablation, **M-Schema beat raw DDL by an average 2.03%** across four LLMs [[27]](https://arxiv.org/html/2411.08599v2).

What to put in the schema string, and why:

| Ingredient | Why it grounds | Evidence |
|---|---|---|
| Column types + PK/FK | model picks valid joins & comparisons | Code Representation is the top format [[6]](https://arxiv.org/pdf/2308.15363) |
| A few **sample rows** per table | reveals actual values & semantics (truncate long ones) | RSL-SQL injects random rows for this [[12]](https://arxiv.org/html/2411.00073v2) |
| Column **descriptions** | maps business terms → physical columns | M-Schema's per-column description tuple [[8]](https://arxiv.org/html/2411.08599v1) |
| **External knowledge / "evidence"** | domain rules the schema can't express | biggest single swing — see below [[10]](https://bird-bench.github.io/) |

The strongest single lever in this layer is BIRD's **external-knowledge ("evidence") channel**. Supplying oracle evidence raised dev-set EX from **37.22% → 42.24% (ChatGPT)** and **46.35% → 49.15% (GPT-4)** [[10]](https://bird-bench.github.io/). The catch: that evidence is hand-written per query by domain experts, which is "not a realistic deployment scenario — a real NL-to-SQL agent must retrieve or infer the relevant domain context itself" [[11]](https://beancount.io/bean-labs/research-logs/2026/06/06/bird-benchmark-text-to-sql-real-database-gap). This is exactly the gap the semantic layer (Layer 6) exists to fill at scale.

## Layer 3 — Retrieval & pruning at scale

Naive prompting breaks on enterprise schemas because the relevant subset no longer fits in context, and even when it does, the noise tanks accuracy. The dominant fix is **coarse-to-fine** grounding.

- **Embedding retrieval.** [LitE-SQL](https://arxiv.org/html/2510.09014) pre-computes a dense vector per column (name, table, description, types, keys, sample values), stores them in ChromaDB, and retrieves the top-k≈25 columns per question — cutting latency to ~25s vs CHESS's ~84s while reaching **72.1% EX on BIRD** [[16]](https://arxiv.org/html/2510.09014). CHESS itself uses model-generated keywords, locality-sensitive hashing for approximate-nearest-neighbor value search, and a vector DB for semantic catalog search, then prunes adaptively [[5]](https://arxiv.org/html/2405.16755v1).
- **Fixed top-k is brittle.** Too small drops needed tables; too large injects noise. A RAG architecture with **hierarchical clustering** can dynamically size the returned schema instead of a static k [[18]](https://www.mdpi.com/2076-3417/16/2/586). [CRED-SQL](https://arxiv.org/html/2508.12769v1) makes this concrete: K-means clustering of column embeddings with inverse-cluster-size weighting (rare attributes score higher) lifts large-DB table recall from **0.09@1 → 0.40@1** and end-to-end accuracy ~22 points over CRUSH [[15]](https://arxiv.org/html/2508.12769v1).
- **Multi-database routing.** [LinkAlign](https://arxiv.org/html/2503.18596v4) adds a retrieve-then-debate pipeline — query rewriting to find candidate schemas, argmax LLM selection of the target DB, then multi-agent extraction — reaching **33.09% on Spider 2.0-Lite** with open-source models [[14]](https://arxiv.org/html/2503.18596v4).
- **Pruning helps even when it fits.** With oracle schema, removing 71.3% of columns raised EX from **79.3% → 86.3%** [[17]](https://arxiv.org/html/2407.03227v1). Small models (<2k-token context) can't hold large schemas at all, so they chunk schemas into parallel splits of ≤64 columns; literal **value retrieval** matches question terms against cell values (top-3 per column) so filters like `WHERE status = 'shipped'` use the real enum [[17]](https://arxiv.org/html/2407.03227v1).

## Layer 4 — Validation, execution feedback & self-correction

Even with perfect linking and representation, models emit invalid SQL. Four mechanisms catch it at progressively later stages — and they **stack**.

- **Constrained / grammar decoding** intervenes *during* generation. [PICARD](https://arxiv.org/abs/2109.05093) attaches an incremental SQL parser to the beam and rejects any token that can't extend into a valid parse — including references to non-existent tables/columns [[19]](https://arxiv.org/abs/2109.05093). It lifts T5-3B on Spider from 74.4% → **79.3% EX (dev)**, 75.1% on test [[20]](https://github.com/servicenow/picard) ⭐ 377.
- **Execution-guided decoding** conditions on partial program execution, pruning candidates that error mid-decode — 83.8% EX on WikiSQL [[25]](https://arxiv.org/abs/1807.03100).
- **Execute-and-repair loops** run after a full candidate. [MAC-SQL](https://arxiv.org/html/2312.11242v2)'s Refiner agent *executes* each candidate, captures the error message, and re-prompts to fix it — central to **59.59% on BIRD test / 86.75% Spider dev** [[23]](https://arxiv.org/html/2312.11242v2). [DIN-SQL](https://arxiv.org/pdf/2304.11015)'s correction module adds ~1.73 points on Spider dev (78.62% → 80.35%) [[22]](https://arxiv.org/html/2406.12692v1), and full DIN-SQL reaches 85.3 EX on Spider test [[21]](https://arxiv.org/pdf/2304.11015); MAGIC auto-derives the correction guideline from failure analysis to hit **85.66%** [[22]](https://arxiv.org/html/2406.12692v1).
- **Self-consistency / voting** denoises sampling variance. [CSC-SQL](https://arxiv.org/html/2505.13271) merge-revises the two most frequent candidates (73.67% BIRD private test, 32B) [[24]](https://arxiv.org/html/2505.13271); a 2026 weighted-majority-voting pipeline (SSEV) reaches 86.4% Spider test / 66.3% BIRD-dev with no ground truth [[26]](https://www.arxiv.org/abs/2601.17942).

These are complementary: grammar constraints block schema-invalid tokens, execution feedback catches semantic/runtime errors, voting cleans up variance. **Execution feedback is the most reliable lever** — it grounds against the actual database, not a representation of it.

## What benchmarks actually reward

Gains are real but increasingly model-dependent. Current **BIRD test EX leaders** (2025–26): AskData+GPT-4o **81.95%**, Agentar-Scale-SQL 81.67%, Xiaomi Text2SQL 80.83%, LongData-SQL 77.53%, SiriusAI-Text2SQL-Agent 77.03% — all using oracle external knowledge, still short of the **92.96% human baseline** [[10]](https://bird-bench.github.io/). Ablations show *where* the accuracy comes from:

- XiYan-SQL: schema linking adds ~2.15 points (57.95% → 60.10%); M-Schema adds ~2.03% over DDL [[27]](https://arxiv.org/html/2411.08599v2).
- [CHASE-SQL](https://arxiv.org/html/2410.01943v1) (73.0% BIRD test): individual generators contribute little when removed (divide-and-conquer CoT −1.24%, query-plan CoT −0.65%, synthetic examples −0.85%); the win is **candidate selection** — its fine-tuned selector beats self-consistency by 4–5 points, with an **oracle upper bound of 82.79%** showing how much is lost to selection error [[28]](https://arxiv.org/html/2410.01943v1).
- The benchmark-vs-reality gap is starkest on Spider 2.0: enterprise DBs crush baselines (GPT-4o **10.1%**, o1-preview 17.1%) and agentic leaders only now reach ~73% on Spider 2.0-Lite (DivSkill-SQL 73.13%) [[13]](https://spider2-sql.github.io/).
- Smaller RL-trained models are catching up: Snowflake's Arctic-Text2SQL-R1 tops BIRD and "wins broadly," challenging large ensemble pipelines [[30]](https://www.snowflake.com/en/engineering-blog/arctic-text2sql-r1-sql-generation-benchmark/).

**Caveat for picking a strategy from leaderboards:** Spider/BIRD hand the model the right database and (for BIRD) hand-written evidence. Real deployments have neither — which is why the production stacks below lean on retrieval and semantic layers, not just better prompting.

## Production tools & semantic layers

Open-source frameworks ground in three ways: **train-a-RAG-model** on your artifacts, **retrieve** schema at query time, or define a **semantic layer** once. Commercial warehouse-native tools have converged on the last.

| Tool | ⭐ Stars | Grounding approach |
|---|---|---|
| [LangChain][38] | ⭐ 139k | `SQLDatabase`/`SQLDatabaseChain`; manual prompt + schema filtering [[38]](https://github.com/langchain-ai/langchain) |
| [LlamaIndex][37] | ⭐ 50k | `NLSQLTableQueryEngine`; `ObjectIndex` retrieves only relevant tables to avoid overflow [[36]](https://developers.llamaindex.ai/python/examples/index_structs/struct_indices/sqlindexdemo/)[[37]](https://github.com/run-llama/llama_index) |
| [Vanna][31] | ⭐ 24k | RAG model trained on DDL + docs + example SQL; retrieves top-10 per query [[31]](https://github.com/vanna-ai/vanna)[[32]](https://qdrant.tech/documentation/frameworks/vanna-ai/) |
| [WrenAI][33] | ⭐ 15k | Open context layer; encodes schema/metrics/relationships into MDL semantic model [[33]](https://github.com/Canner/WrenAI)[[34]](https://medium.com/wrenai/why-the-semantic-layer-is-essential-for-reliable-text-to-sql-and-how-wren-ai-brings-it-to-life-c54cc0e6e4bc) |
| [Dataherald][35] | ⭐ 3.6k | Agentic: schema tools + Context Store + dynamic golden Q/SQL retrieval [[35]](https://dataherald.readthedocs.io/en/latest/text_to_sql_engine.html) |
| [DAIL-SQL][7] | ⭐ 635 | Research baseline: Code-Representation prompt + similarity-masked examples [[7]](https://github.com/BeachWang/DAIL-SQL) |

[38]: https://github.com/langchain-ai/langchain
[37]: https://github.com/run-llama/llama_index
[31]: https://github.com/vanna-ai/vanna
[33]: https://github.com/Canner/WrenAI
[35]: https://dataherald.readthedocs.io/en/latest/text_to_sql_engine.html
[7]: https://github.com/BeachWang/DAIL-SQL

**The semantic-layer consensus.** Raw schemas "lack critical knowledge like business process definitions and metrics handling," so [Snowflake Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) grounds on a **YAML semantic model** of logical tables, dimensions, facts, metrics, synonyms, and verified queries [[39]](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst). Databricks Genie grounds on Unity Catalog metadata; BigQuery Gemini on Dataform views [[40]](https://blog.agami.ai/snowflake-cortex-analyst-vs-databricks-genie-vs-bigquery-gemini-warehouse-native-ai-compared/). WrenAI's MDL defines business meaning ("total sales") once and reuses it rather than re-inferring per query [[34]](https://medium.com/wrenai/why-the-semantic-layer-is-essential-for-reliable-text-to-sql-and-how-wren-ai-brings-it-to-life-c54cc0e6e4bc). The payoff looks large, though the headline number is a vendor self-report: dbt's own blog claims **83% NL-query accuracy** backed by its metrics/dimensions ontology vs **~40%** for LLMs writing raw SQL against undecorated tables [[41]](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026). As of January 2026 the **Open Semantic Interchange (OSI)** — a vendor-neutral YAML standard backed by Snowflake, dbt Labs, Cube, Databricks, AtScale and 40+ partners — aims to make this grounding metadata portable across engines [[42]](https://atlan.com/know/best-semantic-layer-tools/).

## Putting it together — a grounding recipe

1. **Always:** serialize as DDL/M-Schema with types, PK/FK, descriptions, and a few sample values [[6]](https://arxiv.org/pdf/2308.15363)[[8]](https://arxiv.org/html/2411.08599v1).
2. **Small/medium DB + strong model:** feed the full schema; skip linking filters [[29]](https://arxiv.org/html/2408.07702v1).
3. **Large DB (>~hundreds of columns):** embedding retrieval + dynamic (not fixed-k) pruning + value retrieval [[16]](https://arxiv.org/html/2510.09014)[[18]](https://www.mdpi.com/2076-3417/16/2/586)[[17]](https://arxiv.org/html/2407.03227v1).
4. **Always:** execute the candidate, repair on error, and vote across samples [[23]](https://arxiv.org/html/2312.11242v2)[[24]](https://arxiv.org/html/2505.13271).
5. **For business reliability:** ground on a semantic layer / metadata catalog so domain rules and metric definitions live outside the prompt [[39]](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)[[41]](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026).

The through-line: **ground against the database, not against your idea of it.** Representation gets you close; execution feedback and a curated semantic layer are what make it trustworthy.
