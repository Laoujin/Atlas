---
title: "What MCP Server to Build in a 2-3h Session: 7 Demo-Worthy Ideas Scored"
date: 2026-06-04
depth: standard
format: md
topic: "Shortlist of 5-8 demo-worthy MCP server ideas for an expert Java/.NET audience using the official TypeScript SDK, scored on build time, wow-factor, utility, auth complexity, and MCP primitives exercised; recommend the best 1-2 for a live session."
topic_raw: "What MCP server to build"
tags: [mcp, typescript, model-context-protocol, live-coding, ai-tooling]
summary: "Build a read-only SQLite/Postgres query server: it exercises tools + resources + prompts together, needs zero external auth, and fits a 2-3h live session for a senior audience."
citations: 16
reading_time_min: 4
---

> **Decision.** Build a **read-only database query server (SQLite or Postgres)**. It's the only single idea that naturally exercises all three core primitives — `tools` (run SQL), `resources` (expose table schemas as `schema://...` URIs), `prompts` (canned "analyze this table" templates) — needs **zero external auth** (ship a seeded `.db`), and lands inside 2-3h for a senior audience that already thinks in schemas and queries [[1]](https://github.com/jparkerweb/mcp-sqlite)[[2]](https://modelcontextprotocol.info/docs/concepts/resources/). Backup pick if you want a sampling "wow" moment: a **Hacker News digest server** that uses MCP **sampling** to make the *client's* LLM summarize stories the server fetched — a server with no LLM key of its own acting like an agent [[3]](https://workos.com/blog/mcp-sampling)[[4]](https://dev.to/agent-andy/10-free-mcp-servers-that-work-without-api-keys-tested-by-an-ai-agent-3c45).

## Why these constraints matter

A live session for Java/.NET seniors using the official [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) ⭐ 12k (Jun 2026) [[5]](https://github.com/modelcontextprotocol/typescript-sdk) needs an idea that (a) goes past the canonical "weather tool" everyone has seen [[6]](https://modelcontextprotocol.io/docs/develop/build-server), (b) shows `resources` and `prompts`, not just `tools` — most reference servers only demo tools, and the official **Everything** server is the only one that bundles all three [[7]](https://github.com/modelcontextprotocol/servers), and (c) avoids OAuth dances and infra that eat the clock. The SDK's `registerTool()` / `registerResource()` / `registerPrompt()` high-level API auto-handles capability negotiation and Zod input validation, so the primitives themselves are cheap to wire — the time goes into the *domain* behind them [[8]](https://techwithibrahim.medium.com/the-mcp-typescript-sdk-a-complete-guide-to-tools-resources-prompts-and-beyond-285c6ad05a07)[[9]](https://www.webfuse.com/mcp-cheat-sheet).

Auth is the usual time-sink. Free, keyless public APIs (Open-Meteo, Hacker News Firebase/Algolia, Wikipedia) remove that entirely [[4]](https://dev.to/agent-andy/10-free-mcp-servers-that-work-without-api-keys-tested-by-an-ai-agent-3c45)[[10]](https://github.com/nprousalidis/Open-Meteo-MCP-Server). Anything behind OAuth (Spotify, Gmail, GitHub write) costs you a token flow on stage — possible via the SDK's URL elicitation, but a poor first-session choice [[11]](https://ts.sdk.modelcontextprotocol.io/).

## Shortlist scored

Scores 1-5 (5 = best/easiest). "Primitives" = which of tools (T) / resources (R) / prompts (P) / sampling (S) / elicitation (E) the idea naturally exercises.

| Idea | Build-in-time | Wow | Utility | Auth complexity (5=none) | Primitives | Notes |
|---|---|---|---|---|---|---|
| **DB query server** (SQLite/Postgres) [[1]][a] | 5 | 4 | 5 | 5 (ship seeded `.db`) | T·R·P | Schema as resources, SQL tool read-only, "analyze table" prompts. Senior audience's home turf. |
| **HN digest + sampling** [[3]][b] [[4]][c] | 4 | 5 | 3 | 5 (keyless HN API) | T·S | Server asks *client* LLM to summarize fetched stories — the "servers can be agents" reveal. |
| **Interactive incident form (elicitation)** [[12]][d] | 4 | 5 | 4 | 5 (local) | T·E | Tool pauses mid-call to `elicitInput()` a structured form — multi-turn UX, very demo-friendly. |
| **Markdown/PDF → structured doc** [[13]][e] | 4 | 3 | 4 | 5 (local files) | T·R | Convert + expose result as a resource. Tangible output, modest wow. |
| **Git repo insights** (local repo) [[14]][f] | 3 | 4 | 5 | 5 (local git) | T·R·P | Commit/diff tools + repo file resources + "review this diff" prompt. ⚠ git edge cases eat time. |
| **Open-Meteo weather** [[10]][g] [[6]][h] | 5 | 2 | 3 | 5 (keyless) | T | The reference build — fast, but everyone's seen it. Use only as a 10-min warmup. |
| **Browser automation** (Playwright) [[15]][i] | 2 | 5 | 4 | 5 (local) | T | Highest wow, but reimplementing it is out of scope; Microsoft's server already exists. ⚠ flaky live. |

[a]: https://github.com/jparkerweb/mcp-sqlite
[b]: https://workos.com/blog/mcp-sampling
[c]: https://dev.to/agent-andy/10-free-mcp-servers-that-work-without-api-keys-tested-by-an-ai-agent-3c45
[d]: https://nickperkins.au/code/mcp-elicitations-interactive-tools/
[e]: https://dev.to/copilotkit/30-mcp-ideas-with-complete-source-code-d8e
[f]: https://github.com/modelcontextprotocol/servers
[g]: https://github.com/nprousalidis/Open-Meteo-MCP-Server
[h]: https://modelcontextprotocol.io/docs/develop/build-server
[i]: https://github.com/microsoft/playwright-mcp

GitHub stars for repos referenced above: [mcp-sqlite](https://github.com/jparkerweb/mcp-sqlite) ⭐ 107 (Jun 2026) [[1]](https://github.com/jparkerweb/mcp-sqlite); [official servers](https://github.com/modelcontextprotocol/servers) ⭐ 87k (Jun 2026) [[7]](https://github.com/modelcontextprotocol/servers); [playwright-mcp](https://github.com/microsoft/playwright-mcp) ⭐ 33k (Jun 2026) [[15]](https://github.com/microsoft/playwright-mcp); [Open-Meteo-MCP-Server](https://github.com/nprousalidis/Open-Meteo-MCP-Server) ⭐ 0 (Jun 2026) — reference only, not a popular project [[10]](https://github.com/nprousalidis/Open-Meteo-MCP-Server).

## Top pick — DB query server, session shape

A seeded SQLite database (e.g. startup-funding or Titanic sample data — both are common in existing servers) gives you a self-contained demo with no network or keys [[1]](https://github.com/jparkerweb/mcp-sqlite). The build maps cleanly onto a 2-3h arc:

1. **Tools (~45 min).** `list_tables`, `describe_table`, `query` — gate `query` to `SELECT`/`PRAGMA`/`EXPLAIN`/`WITH` only, the standard read-only safety pattern, which also seeds a good "AI safety in tools" discussion for a senior crowd [[1]](https://github.com/jparkerweb/mcp-sqlite). Zod schemas give the .NET/Java audience the familiar "DTO validation" mental model [[8]](https://techwithibrahim.medium.com/the-mcp-typescript-sdk-a-complete-guide-to-tools-resources-prompts-and-beyond-285c6ad05a07).
2. **Resources (~30 min).** Expose each table's schema at a `schema://sqlite/<table>` URI; resources are read-only context the client pulls in, distinct from tool *actions* [[2]](https://modelcontextprotocol.info/docs/concepts/resources/). This is the part most tutorials skip — showing it differentiates the session.
3. **Prompts (~20 min).** Register an `analyze-table` prompt template the user can pick from a menu, prefilled with the schema — demonstrates the third primitive that almost no demo covers [[7]](https://github.com/modelcontextprotocol/servers).
4. **Wire to a client (~20 min).** `StdioServerTransport` into Claude Desktop or any MCP client; ask "which 3 sectors raised the most in 2025?" and watch it discover schema → write SQL → answer [[6]](https://modelcontextprotocol.io/docs/develop/build-server).
5. **Buffer/stretch.** Swap SQLite for a Postgres connection string to show the same server against real infra, or add an `elicitInput()` confirmation before any expensive query.

The .NET/Java audience already has the database mental model, so cognitive load goes entirely into MCP mechanics, not the domain — exactly what you want for a first build [[8]](https://techwithibrahim.medium.com/the-mcp-typescript-sdk-a-complete-guide-to-tools-resources-prompts-and-beyond-285c6ad05a07).

## If you want one "wow" beat — add sampling

If the room is advanced and you finish the DB server early, the standout reveal is **sampling**: the server asks the *client's* LLM to do work, flipping the usual flow [[3]](https://workos.com/blog/mcp-sampling). Concretely: a `hn_digest` tool fetches top Hacker News stories (keyless `hacker-news.firebaseio.com` / Algolia endpoints) [[4]](https://dev.to/agent-andy/10-free-mcp-servers-that-work-without-api-keys-tested-by-an-ai-agent-3c45), then issues a `createMessage` sampling request so the client LLM summarizes them — the server itself holds no API key and runs no inference, yet behaves like an agent [[3]](https://workos.com/blog/mcp-sampling)[[16]](https://www.speakeasy.com/mcp/concepts/sampling). The SDK ships runnable sampling and elicitation examples (`elicitationFormExample.ts`, `elicitationUrlExample.ts`) you can crib from live [[11]](https://ts.sdk.modelcontextprotocol.io/). ⚠ Client support for sampling is uneven — verify your demo client (Claude Desktop) honors it before relying on it on stage [[16]](https://www.speakeasy.com/mcp/concepts/sampling).

## What to avoid for a first live session

- **OAuth-backed APIs** (Spotify, Gmail, GitHub write) — token flow burns stage time even with URL elicitation [[11]](https://ts.sdk.modelcontextprotocol.io/).
- **Browser automation from scratch** — highest wow but Microsoft's [playwright-mcp](https://github.com/microsoft/playwright-mcp) ⭐ 33k (Jun 2026) already does it; reimplementing is out of scope and flaky live [[15]](https://github.com/microsoft/playwright-mcp).
- **Bare weather/echo tools** — fine as a 10-minute warmup, but they don't show resources or prompts and the audience has seen them [[6]](https://modelcontextprotocol.io/docs/develop/build-server).
