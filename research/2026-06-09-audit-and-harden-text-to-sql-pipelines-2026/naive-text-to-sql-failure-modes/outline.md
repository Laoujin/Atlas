Taxonomy of correctness failures in naive LLM text-to-SQL: schema linking errors, hallucinated tables/columns, join mistakes, GROUP BY/aggregation errors, ambiguity.
Benchmark evidence on the accuracy ceiling: what Spider, BIRD, and Spider 2.0 reveal about the gap between naive prompting, SOTA systems, and human performance.
Security and safety failure modes: SQL/prompt injection through natural language, destructive writes (DROP/DELETE/UPDATE), data exfiltration, and why read-only execution and least-privilege matter.
Silent semantic failures: queries that execute successfully but return wrong answers, NL ambiguity, unstated assumptions, and why these are the most dangerous in production.
Production and operator experience: real-world deployment reports, latency/cost, large/real-world schemas, dialect portability, and robustness problems with naive pipelines.
Mitigations that harden naive pipelines: schema grounding/linking, RAG over schema and values, self-correction/re-ask loops, execution-guided decoding, guardrails, and sandboxed read-only execution.
