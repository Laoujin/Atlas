# Schema grounding strategies — outline

1. Schema linking / schema selection: techniques to identify the relevant tables and columns for a question (string match, embedding retrieval, LLM-based selection) and why grounding to the right schema subset matters.
2. Schema representation & serialization formats fed to the LLM: DDL (CREATE TABLE) vs M-Schema vs JSON/markdown, role of sample values, column descriptions, foreign-key hints, and the "external knowledge"/evidence channel.
3. Schema pruning & retrieval at scale for large/enterprise databases: embedding-based column/table filtering, RAG over schema, hierarchical selection, handling 100s–1000s of tables within context limits.
4. Validation, execution feedback & self-correction as grounding: constrained/grammar decoding, executing candidate SQL and re-prompting on error, self-consistency, schema-aware decoding.
5. Benchmark evidence: what schema-grounding techniques actually move accuracy on Spider, BIRD, Spider 2.0 — ablations and current SOTA numbers (2024–2026).
6. Production tools, frameworks & patterns: Vanna, LangChain/LlamaIndex SQL, DAIL-SQL, semantic layers/metadata catalogs, and commercial text-to-SQL grounding approaches.
