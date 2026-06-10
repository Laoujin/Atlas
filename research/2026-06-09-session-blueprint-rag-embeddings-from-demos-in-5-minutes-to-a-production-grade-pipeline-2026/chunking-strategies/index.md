---
title: "Chunking Strategies for RAG Pipelines"
date: 2026-06-09
depth: standard
format: md
topic: "Chunking strategies"
topic_raw: "Chunking strategies"
issue: 207
tags: [rag, embeddings, chunking, retrieval, nlp, production]
summary: "How to choose and tune chunking strategies for production RAG: from recursive baselines to contextual retrieval, with benchmarks and a decision framework."
citations: 12
reading_time_min: 6
cover: cover.svg
cost_usd: 1.03
duration_sec: 405
model: "Sonnet 4.6"
---

> **TL;DR** — Start with recursive character splitting at 512 tokens: it outperforms semantic chunking on most benchmarks at 14× the speed [[6]](https://github.com/chonkie-inc/chonkie/blob/main/BENCHMARKS.md). Layer [Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) to cut top-20 retrieval failures by up to 67% [[5]](https://www.anthropic.com/news/contextual-retrieval). Use hierarchical (small-to-big) when you need retrieval precision *and* generation context [[8]](https://futureagi.com/blog/vector-chunking-2025/).

## Strategy Comparison

| Strategy                  | Throughput        | When to use                                    | Tooling                                     |
| ------------------------- | ----------------- | ---------------------------------------------- | ------------------------------------------- |
| Fixed-size                | Fastest           | Prototyping only; breaks semantic boundaries   | `CharacterTextSplitter` (LangChain)         |
| **Recursive character**   | **4.82 MB/s** ⭐  | General-purpose default; respects paragraph/sentence/word hierarchy | `RecursiveCharacterTextSplitter` (LangChain) |
| Token-based               | ~4.82 MB/s        | Hard token-budget limits, multilingual text    | `TokenTextSplitter` (LangChain)             |
| Sentence-based            | Medium            | Legal, news; no mid-sentence breaks            | `SentenceSplitter` (LlamaIndex)             |
| Structure-aware (MD/HTML) | Fast              | Docs, wikis — biggest retrieval gain for structured text | Unstructured.io, `MarkdownTextSplitter`     |
| Semantic                  | 0.33 MB/s (~14× slower) | Topic-dense knowledge bases where accuracy > speed | `SemanticChunker` (LangChain), `SemanticSplitterNodeParser` (LlamaIndex) |
| Late chunking             | ~token-based speed | Ambiguous cross-references, pronoun resolution | Jina AI embedding API                       |
| Hierarchical (small-to-big) | Medium          | Complex Q&A needing retrieval precision + generation context | `ParentDocumentRetriever` (LangChain)       |
| Contextual Retrieval      | Preprocessing cost | High-value production corpora                  | Claude 3 Haiku + prompt caching             |
| Agentic / LLM-decided     | 10–50× slower     | Messy structured docs (contracts, research papers) | Experimental only                           |

⭐ = recommended default [[1]](https://www.firecrawl.dev/blog/best-chunking-strategies-rag) [[9]](https://www.unsiloed.ai/blog/chunking-strategy-rag-systems-technical-implementation-guide)

## Chunk Size by Query Type

| Query type              | Size           | Notes                                          |
| ----------------------- | -------------- | ---------------------------------------------- |
| Factoid (dates, names)  | 64–256 tokens  | Smaller = higher precision for point lookups   |
| General-purpose         | 256–512 tokens | Sweet spot for most chat-style RAG             |
| Analytical / multi-hop  | 512–1024 tokens | Multi-concept reasoning needs more context    |
| Long-document QA        | 1500–2048 tokens | Pair with a strong cross-encoder reranker    |

[[2]](https://www.digitalapplied.com/blog/rag-chunking-strategies-2026-retrieval-quality-playbook) [[9]](https://www.unsiloed.ai/blog/chunking-strategy-rag-systems-technical-implementation-guide) — There is a **context cliff**: quality degrades beyond ~2,500 tokens per chunk [[11]](https://arxiv.org/abs/2601.14123).

## Key Benchmarks

- **Recursive at 512 tokens**: 69% end-to-end accuracy across 50 academic papers (Vecta, Feb 2026) [[2]](https://www.digitalapplied.com/blog/rag-chunking-strategies-2026-retrieval-quality-playbook)
- **Semantic chunking**: 54% in the same benchmark — 14.6× slower (4.82 → 0.33 MB/s) [[6]](https://github.com/chonkie-inc/chonkie/blob/main/BENCHMARKS.md)
- **LLMSemanticChunker**: 0.919 recall; **ClusterSemanticChunker**: 0.913 recall — at much higher cost [[1]](https://www.firecrawl.dev/blog/best-chunking-strategies-rag)
- **Fixed-size baseline**: context recall 0.72 (~1 in 4 queries misses relevant content) [[10]](https://towardsdatascience.com/your-chunks-failed-your-rag-in-production/)
- **Sentence window optimization**: context recall rises to 0.88, precision to 0.83 [[10]](https://towardsdatascience.com/your-chunks-failed-your-rag-in-production/)
- **Best recall gap** between strategies: up to 9% [[7]](https://weaviate.io/blog/chunking-strategies-for-rag)

## Advanced Techniques

### Late Chunking
Encodes the full document with a long-context embedding model, then derives chunk vectors by pooling the already-contextualized token embeddings — no information loss at boundaries. Yields ~3.5% relative improvement on BeIR retrieval benchmarks [[3]](https://arxiv.org/html/2409.04701v3). Gains are largest at small chunk sizes. Requires a long-context embedding model (Jina AI's API exposes this directly).

### Contextual Retrieval
Anthropic's technique: a small model (Claude 3 Haiku) generates a 50–100 token contextual description for each chunk and prepends it before embedding [[5]](https://www.anthropic.com/news/contextual-retrieval). The layered gains on top-20 retrieval failure rate:

| Layer added             | Failure rate | Reduction |
| ----------------------- | ------------ | --------- |
| Baseline                | 5.7%         | —         |
| + Contextual Embeddings | 3.7%         | 35%       |
| + Contextual BM25       | 2.9%         | 49%       |
| + Reranking             | 1.9%         | **67%**   |

Cost: ~**$1.02 per million document tokens** with prompt caching. Worth it for corpora that don't change often [[5]](https://www.anthropic.com/news/contextual-retrieval).

### Hierarchical / Small-to-Big
Index small child chunks (200–400 tokens) for retrieval precision; return their parent chunks (1500–3000 tokens) to the LLM for generation context [[8]](https://futureagi.com/blog/vector-chunking-2025/). Adds pipeline complexity (two document stores) but solves the classic trade-off between retrieval recall and generation quality. LangChain's `ParentDocumentRetriever` implements this pattern directly.

### Agentic / Propositional Chunking
An LLM identifies logical propositions and groups them into coherent retrieval units — highest-fidelity for complex implicit structure (legal contracts, research papers) but 10–50× indexing cost [[4]](https://langcopilot.com/posts/2025-10-11-document-chunking-for-rag-practical-guide). In one 2026 study, agentic chunking reached 94.5% accuracy, ~4% above fixed-token approaches. Treat as a last resort after measuring baselines.

## The Overlap Question

Conventional wisdom: 10–20% overlap prevents context loss at boundaries. Reality: a Jan 2026 arXiv study (n=Natural Questions, SPLADE retrieval) found **overlap provides no measurable retrieval benefit and only increases indexing cost** [[11]](https://arxiv.org/abs/2601.14123). Separate production analysis found up to 14.5% recall improvement with overlap in dense retriever setups [[7]](https://weaviate.io/blog/chunking-strategies-for-rag). The verdict: **treat overlap as a variable to test on your data**, not a free default.

## Decision Framework

1. **Parse first.** Layout-aware parsing (Unstructured.io, Docling) preserves tables, headers, and reading order before any splitting. Weak parsing → weak chunks regardless of strategy.
2. **Baseline.** Recursive character splitting, 512 tokens, 0–10% overlap. Measure RAGAS: context recall, context precision, faithfulness [[10]](https://towardsdatascience.com/your-chunks-failed-your-rag-in-production/).
3. **Size to query type.** If context recall is low on factoid queries → shrink to 128–256 tokens. If low on analytical queries → expand to 768–1024 tokens.
4. **Structure wins first.** If documents have headers or HTML structure, switch to structure-aware splitting before going semantic — often the biggest single gain for structured docs [[4]](https://langcopilot.com/posts/2025-10-11-document-chunking-for-rag-practical-guide).
5. **Upgrade cost-effectively.** Add Contextual Retrieval before semantic chunking: better failure reduction, one-time preprocessing cost, no inference-time latency [[5]](https://www.anthropic.com/news/contextual-retrieval).
6. **Hierarchical when precision + context both matter.** Small-to-big adds pipeline complexity but pays off for complex Q&A [[8]](https://futureagi.com/blog/vector-chunking-2025/).
7. **Semantic / agentic last.** Only after measuring a gap that justifies 14–50× ingestion cost.

> 80% of RAG failures trace to the ingestion and chunking layer — not the LLM, not the embedding model [[2]](https://www.digitalapplied.com/blog/rag-chunking-strategies-2026-retrieval-quality-playbook). The canonical production stack: 400–600 token recursive chunks → retrieve top-30–50 → rerank to top-5 with a cross-encoder.

## Tooling

| Tool                                        | Role                                                |
| ------------------------------------------- | --------------------------------------------------- |
| [Chonkie](https://github.com/chonkie-inc/chonkie) ⭐ 4.1k | Fastest Python chunking library; 32+ integrations, 56 languages [[12]](https://github.com/chonkie-inc/chonkie) |
| LangChain text splitters                    | `RecursiveCharacterTextSplitter` is the de-facto default |
| LlamaIndex `SentenceSplitter`               | Sentence-aware splits; `SemanticSplitterNodeParser` for semantic |
| Unstructured.io                             | Layout-aware PDF/HTML parsing before chunking       |
| Jina AI embeddings API                      | Late chunking via long-context encoder              |
| RAGAS                                       | Evaluation: context recall, precision, faithfulness |
