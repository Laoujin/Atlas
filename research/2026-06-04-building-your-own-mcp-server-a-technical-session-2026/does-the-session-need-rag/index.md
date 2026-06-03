---
title: "Does a build-your-own-MCP-server session need RAG? Cut it."
date: 2026-06-04
depth: ceo
format: md
topic: "Does a \"build your own MCP server\" session need RAG? — a one-page decision. Clarify how RAG relates to MCP, when a RAG/vector-search example strengthens vs bloats a 2–3h session, and the single smallest demo that earns its place if included."
topic_raw: "Does the session need RAG"
tags: [mcp, rag, session-design, typescript, vector-search]
summary: "Cut the vector DB from a 2–3h MCP session; a RAG tool is just a tool — show retrieval with a 30-line in-memory search instead."
citations: 7
reading_time_min: 2
---

> **Decision: CUT dedicated RAG.** RAG is not a peer concept to MCP that the session must "cover" — MCP is the transport/standard, RAG is one thing a tool can *do* behind it [[1]](https://www.merge.dev/blog/rag-vs-mcp)[[2]](https://infranodus.com/docs/mcp-vs-rag-vs-ai-agents). For expert devs on a 2–3h budget, a vector-DB demo spends 30–45 min teaching embeddings, chunking, and a Qdrant/Milvus dependency [[3]](https://github.com/qdrant/mcp-server-qdrant) — none of which is *MCP*. **If** you want to show "expose a knowledge source," do it as a single `search_docs` tool over an in-memory array with substring/keyword match. That delivers the entire conceptual payload (server exposes a retrieval capability → model calls it → grounded answer) in ~30 lines and zero infra.

## Why RAG isn't a separate topic

An MCP server *is* effectively a retrieval backend when you want it to be: **Resources** are read-only addressable data (files, DB rows, API responses) and **Tools** perform lookups/actions [[4]](https://thenewstack.io/how-to-build-rag-applications-using-model-context-protocol/). A "RAG tool" is just a Tool whose body happens to call a vector index instead of a REST API. The retrieve-then-answer shape — `search_docs` returns chunks, the model summarizes and cites — is the standard Elastic/Qdrant pattern [[3]](https://github.com/qdrant/mcp-server-qdrant), and it teaches your audience nothing new about *the protocol* over a plain `get_weather` tool. The framing your devs need: RAG and MCP are complementary layers, not alternatives — RAG fetches knowledge, MCP is how the model reaches whatever fetches it [[1]](https://www.merge.dev/blog/rag-vs-mcp)[[2]](https://infranodus.com/docs/mcp-vs-rag-vs-ai-agents).

## Include vs cut — the trade

| Option                          | Time   | Teaches MCP? | Teaches RAG plumbing | Verdict          |
|---------------------------------|--------|--------------|----------------------|------------------|
| No retrieval example            | 0      | n/a          | no                   | fine             |
| **`search_docs` over array**    | ~10 min| ✓ (one tool) | the *idea* only      | **include this** |
| Embeddings + local vector lib   | ~25 min| ✓            | chunk/embed/cosine   | only if RAG-themed audience |
| Qdrant/Milvus MCP server        | 30–45m | partly       | infra + deps         | ✗ bloat [[3]](https://github.com/qdrant/mcp-server-qdrant)[[5]](https://milvus.io/docs/milvus_and_mcp.md) |

The vector-DB route forces an external service, embedding-provider keys, and a chunking digression — all orthogonal to "build your own MCP server" and a known time sink in real implementations [[5]](https://milvus.io/docs/milvus_and_mcp.md). MCP can even *bypass* embeddings/vector search by retrieving live authoritative data on demand [[6]](https://fast.io/resources/model-context-protocol/) — so for an intro you sidestep the heaviest RAG machinery entirely.

## The smallest demo that earns its place

If you include anything, ship exactly one Tool on the official TS SDK [[7]](https://github.com/modelcontextprotocol/typescript-sdk):

```ts
const DOCS = [
  { id: "refunds", text: "Refunds are processed within 5 business days." },
  { id: "hours",   text: "Support is available 09:00–17:00 CET." },
];
server.registerTool("search_docs",
  { description: "Search the knowledge base", inputSchema: { query: z.string() } },
  async ({ query }) => {
    const hits = DOCS.filter(d => d.text.toLowerCase().includes(query.toLowerCase()));
    return { content: [{ type: "text", text: JSON.stringify(hits) }] };
  });
```

That is the whole RAG lesson for an MCP session: the server *owns a knowledge source*, the model calls in to retrieve, the answer is grounded and citable. Swap the `.filter` for a cosine search later — say so in one sentence and move on. Spend the reclaimed 30 minutes on transports (stdio vs streamable HTTP), error handling, and auth, which *are* MCP.

[[7]](https://github.com/modelcontextprotocol/typescript-sdk) ⭐ 12.6k (Jun 2026) · qdrant/mcp-server-qdrant ⭐ 1.4k · zilliztech/claude-context ⭐ 11.7k
