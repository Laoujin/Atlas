How does pgvector enable semantic row search mechanically (vector types, embedding columns, distance operators, basic query patterns)?
Indexing and performance: HNSW vs IVFFlat tradeoffs, tuning parameters, recall/speed, build cost, dimension limits.
Filtered and hybrid search: combining vector similarity with SQL WHERE filters and full-text search, the filtered-vector accuracy problem, iterative index scans.
pgvector for text-to-SQL and RAG-over-structured-data: semantic retrieval of rows and column values to ground LLM SQL generation, entity/value linking.
Alternatives and comparison: pgvector vs dedicated vector DBs (Qdrant, Pinecone, Weaviate, Milvus) and vs pgvectorscale; when to pick which.
Skeptic view: limitations, scaling pitfalls, recall degradation, memory and cost gotchas in production.
