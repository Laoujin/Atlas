---
layout: expedition
title: "Build Your Own MCP Server: A Technical Session Blueprint (2026)"
date: 2026-06-04
topic: "Design a technical session on building your own MCP server (2026): the protocol, what to build, workshop-vs-demo format, debugging, security, deployment, and whether RAG is needed."
format: md
tags: [mcp, model-context-protocol, ai-agents, developer-workshop, typescript]
summary: "A session blueprint for teaching devs to build an MCP server: a demo-led live build of a zero-auth TypeScript query server, with the protocol, debugging, security, deployment, and the RAG question all scoped in."
cover: cover.svg
synthesis: true
model: "Opus 4.8"
duration_sec: 495
cost_usd: "sub"
children:
  - slug: mcp-protocol-fundamentals
    title: "MCP Protocol Fundamentals: What You Must Know to Build a Server"
    depth: survey
    status: success
    summary: "The wire-level mechanics of MCP — transports, three primitives, lifecycle handshake, capability negotiation, JSON-RPC shapes, and versioning — on the current 2025-11-25 spec, with what's changing in 2026."
    citations: 16
    reading_time_min: 9
  - slug: what-mcp-server-to-build
    title: "What MCP Server to Build in a 2-3h Session: 7 Demo-Worthy Ideas Scored"
    depth: survey
    status: success
    summary: "Build a read-only SQLite/Postgres query server: it exercises tools + resources + prompts together, needs zero external auth, and fits a 2-3h live session for a senior audience."
    citations: 16
    reading_time_min: 4
  - slug: workshop-vs-demo-code-show
    title: "Workshop vs Demo for a 2–3h MCP-Server Session: A Decision Framework + Two Timeboxed Agendas"
    depth: survey
    status: success
    summary: "When to make a 2–3h MCP-server session hands-on vs watch-only, with two timeboxed agendas and a de-risking checklist for live coding."
    citations: 18
    reading_time_min: 9
  - slug: debugging-mcp-servers
    title: "Debugging MCP servers: Inspector, stderr logging, and the failure modes that kill stdio"
    depth: survey
    status: success
    summary: "The Inspector is your first stop, stdout pollution is the #1 killer, and stderr is the only safe log channel for stdio servers."
    citations: 12
    reading_time_min: 6
  - slug: does-the-session-need-rag
    title: "Does a build-your-own-MCP-server session need RAG? Cut it."
    depth: recon
    status: success
    summary: "Cut the vector DB from a 2–3h MCP session; a RAG tool is just a tool — show retrieval with a 30-line in-memory search instead."
    citations: 7
    reading_time_min: 2
  - slug: security-and-auth
    title: "Security & Auth for MCP Servers: What to Teach Builders in 2026"
    depth: survey
    status: success
    summary: "The MCP auth spec makes your server an OAuth 2.1 resource server; the real danger is the agent layer — poisoned tool descriptions and injected tool results. Teach both."
    citations: 18
    reading_time_min: 7
  - slug: deployment-and-distribution
    title: "Shipping Your MCP Server: Deployment & Distribution in 2026"
    depth: survey
    status: success
    summary: "How you actually ship and share the MCP server you built: transport choice, packaging channels, the official registry, and client config."
    citations: 16
    reading_time_min: 4
  - slug: typescript-mcp-server-setup-for-the-session
    title: "TypeScript MCP Server: Session Quickstart + SDK Comparison"
    depth: recon
    status: success
    summary: "One-page quickstart for a TypeScript MCP server over stdio with MCP Inspector, plus a TS/Python/C# SDK comparison and the Java SDK maturity line."
    citations: 7
    reading_time_min: 2
---

> **Blueprint:** Run this as a **demo-led hybrid**, not a full hands-on workshop — for a mixed Java/.NET room on a 2–3h budget, build one server live and let attendees follow at checkpoints ([hands-on vs watch-only](workshop-vs-demo-code-show/)). Build a **read-only query server** in the official TypeScript SDK: it exercises tools, resources, and prompts together and needs zero external auth ([what to build](what-mcp-server-to-build/)). **Cut RAG** as a standalone topic — it's just a tool behind MCP ([why](does-the-session-need-rag/)).

The spine of the session comes from a deliberate dependency between two angles. The recommended build — a read-only query server — is chosen precisely because it needs **no OAuth** ([the pick](what-mcp-server-to-build/)), and that is what lets the security angle be *taught as a threat model instead of built live*. MCP's real danger isn't the auth handshake but the agent layer: **tool poisoning**, where hidden instructions in a tool description the user never sees trick the agent into exfiltrating data [[3]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks). So the arc is: build something auth-free, then *discuss* the OAuth 2.1 resource-server model [[4]](https://modelcontextprotocol.io/specification/draft/basic/authorization) and poisoning as "what you must add before shipping" — not code it under time pressure.

The sharpest cross-cutting risk is that **the protocol is mid-flux**. Pin the session to the current stable revision, **2025-11-25** [[1]](https://modelcontextprotocol.io/specification/2025-11-25), and treat the **2026-07-28 release candidate** — a stateless core, Tasks, MCP Apps — as "what's coming," not something to build against [[2]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/). Teaching the RC live would date the demo within weeks.

Debugging is the connective tissue that de-risks the live build, and two findings shape every checkpoint: **stdout pollution is the #1 killer** of stdio servers — one stray `console.log` corrupts the JSON-RPC stream, so stderr is the only safe log channel — and the **MCP Inspector** is the first tool to reach for, before any real client ([debugging](debugging-mcp-servers/)). Validate each live-coding checkpoint in Inspector before wiring Claude Desktop.

Scope distribution down to **stdio/local** for the room and signpost the rest: Streamable HTTP, the official registry, and `.mcpb` one-click bundles are "where to take it next," not session material [[5]](https://modelcontextprotocol.io/registry/about). One reassurance worth stating out loud: TypeScript is the lowest-friction language to *follow live*, but **C# and Java now have official SDKs** ([SDK comparison](typescript-mcp-server-setup-for-the-session/)) — so the Java/.NET attendees can port the exact same server afterward.

Open question: does the **2026-07-28 RC** land close enough to your session date that you hedge toward its stateless model — or commit fully to 2025-11-25 and accept you're teaching a spec one revision from obsolete?
