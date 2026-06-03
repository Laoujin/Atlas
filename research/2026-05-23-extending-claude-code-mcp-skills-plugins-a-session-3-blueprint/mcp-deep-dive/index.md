---
title: "MCP Deep-Dive: Session Blueprint for a 1–2 Hour Talk"
date: 2026-05-23
depth: standard
format: md
topic: "MCP deep-dive"
topic_raw: "MCP deep-dive"
issue: 57
tags: [mcp, ai-agents, protocols, security, talk-prep]
summary: "Talk-prep brief for a 1–2 hour deep-dive on the Model Context Protocol — architecture, 2026 spec, ecosystem, security trifecta, and live-demo recipes."
citations: 30
reading_time_min: 10
cover: cover.svg
cost_usd: 2.86
duration_sec: 521
model: "Opus 4.7"
---

> **TL;DR — what to teach.** MCP is a JSON-RPC 2.0 protocol that lets any LLM host call any tool/data source through a standard wire format. Anthropic open-sourced it in Nov 2024 [[1]](https://www.anthropic.com/news/model-context-protocol); the Linux Foundation's Agentic AI Foundation now governs it [[3]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation); every major lab (Anthropic, OpenAI, Google, Microsoft, AWS) ships first-class client support, with **110M+ SDK downloads per month** [[4]](https://aaif.io/blog/mcp-is-now-enterprise-infrastructure-everything-that-happened-at-mcp-dev-summit-north-america-2026/). For a deep-dive talk, anchor on three pillars: **(1) the six primitives** (tools/resources/prompts on the server; sampling/roots/elicitation on the client), **(2) the 2025-11-25 spec + 2026-07-28 release candidate** (stateless core, MCP Apps, Tasks extension, OAuth 2.1 hardening), and **(3) the security session** — tool poisoning and the "lethal trifecta" [[22]](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/) are where this protocol is most interesting and least solved.

## Suggested agenda

| Block                      | 60-min slot | 120-min slot | What lands                                                                   |
| -------------------------- | ----------- | ------------ | ---------------------------------------------------------------------------- |
| Why MCP exists             | 5 min       | 10 min       | The N×M integration problem; pre-MCP fragmentation                           |
| Architecture & primitives  | 10 min      | 20 min       | Host / Client / Server; six primitives; capability negotiation               |
| Transports & auth          | 5 min       | 15 min       | stdio vs Streamable HTTP; OAuth 2.1 resource-server model                    |
| **Live demo 1**            | 10 min      | 15 min       | Build a FastMCP tool, wire to Claude Desktop, inspect with MCP Inspector     |
| 2026 spec changes          | 5 min       | 15 min       | Stateless core, Tasks, MCP Apps, deprecation policy                          |
| Ecosystem tour             | 5 min       | 10 min       | Servers worth knowing; the registry; supply-chain provenance                 |
| **Security** (load-bearer) | 15 min      | 25 min       | Tool poisoning, lethal trifecta, CVE timeline, host-side mitigations         |
| **Live demo 2**            | —           | 5 min        | Reproduce a tool-description injection against an unhardened host (sandbox!) |
| Q&A / outlook              | 5 min       | 5 min        | A2A vs MCP, registry monetisation, what to ship next                         |

## Origin & governance

| When        | Event                                                                                                                                                              |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 25 Nov 2024 | [Anthropic](https://www.anthropic.com) open-sources MCP (creators: David Soria Parra & Justin Spahr-Summers); reference servers for Drive, Slack, GitHub, Git, Postgres, Puppeteer [[1]](https://www.anthropic.com/news/model-context-protocol) [[2]](https://en.wikipedia.org/wiki/Model_Context_Protocol) |
| Mar 2025    | OpenAI adopts MCP across products; Sam Altman: *"people love MCP and we are excited to add support across our products"* [[12]](https://zuplo.com/blog/one-year-of-mcp) |
| Apr 2025    | Google DeepMind endorses; Hassabis: *"MCP is a good protocol and it's rapidly becoming an open standard"* [[12]](https://zuplo.com/blog/one-year-of-mcp)             |
| 25 Nov 2025 | Spec **2025-11-25** released [[5]](https://modelcontextprotocol.io/specification/2025-11-25)                                                                        |
| 9 Dec 2025  | Anthropic donates MCP to Linux Foundation's [AAIF](https://aaif.io) (Anthropic, Block, OpenAI co-founders; Google/MS/AWS/Cloudflare/Bloomberg support) [[3]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation) |
| 26 Jan 2026 | MCP Apps (SEP-1865) ships — first official extension [[26]](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)                                       |
| 2–3 Apr 2026| MCP Dev Summit NYC, ~1,200 attendees; 110M+ monthly SDK downloads reported [[4]](https://aaif.io/blog/mcp-is-now-enterprise-infrastructure-everything-that-happened-at-mcp-dev-summit-north-america-2026/) |
| 28 Jul 2026 | Final spec target for the next major release (stateless core) [[6]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)                      |

**Why the donation matters for the talk:** governance is now multi-vendor under the Linux Foundation, which is the answer to the "is this just an Anthropic thing?" question every audience asks [[3]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation).

## Architecture in one screen

Three roles, JSON-RPC 2.0 between them [[5]](https://modelcontextprotocol.io/specification/2025-11-25):

- **Host** — the LLM app (Claude Desktop, Cursor, VS Code, ChatGPT, Gemini). Initiates connections, decides what the model sees, owns user consent.
- **Client** — one per server, lives inside the host. Maintains the JSON-RPC session, negotiates capabilities.
- **Server** — the integration. A separate process (stdio) or HTTP service that exposes primitives.

Capability negotiation is explicit: client and server each advertise what they support during `initialize`, and only declared primitives become usable [[5]](https://modelcontextprotocol.io/specification/2025-11-25). MCP takes its inspiration from LSP — same "one protocol, N×M ecosystem" payoff.

## The six primitives

Server-exposed (what the model can use) and client-exposed (what the server can ask of the host):

| Direction      | Primitive    | What it is                                                                                                | Notes                                                                                            |
| -------------- | ------------ | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Server → Host  | **Tools**    | Functions the model can call (name, JSON Schema args, handler) [[5]](https://modelcontextprotocol.io/specification/2025-11-25) | The headline primitive; everything else is supporting cast                                       |
| Server → Host  | **Resources**| Readable data exposed by URI (files, DB rows, API objects) [[5]](https://modelcontextprotocol.io/specification/2025-11-25)     | Subscribable; the model or user pulls them into context                                          |
| Server → Host  | **Prompts**  | Parameterised prompt templates the user can invoke [[5]](https://modelcontextprotocol.io/specification/2025-11-25)             | Slash-commands in disguise; underused in practice                                                |
| Host → Server  | **Sampling** | Server asks the host to run an LLM completion (no server-side API key needed) [[8]](https://workos.com/blog/mcp-features-guide) | ⚠ Deprecated in draft-2026-v1; still supported ≥1 year [[9]](https://modelcontextprotocol.io/specification/draft/client/sampling) |
| Host → Server  | **Roots**    | The filesystem/URI scopes the server is allowed to see (`file://` only) [[8]](https://workos.com/blog/mcp-features-guide)      | The user's "you can look here, not there"                                                        |
| Host → Server  | **Elicitation** | Server requests structured input from the user mid-call (schema-validated form) [[8]](https://workos.com/blog/mcp-features-guide) | Fixes the "tool needs one more arg" UX gap                                                       |

Teaching tip: 90% of real-world MCP servers only implement **Tools**. Demoing the other five is what makes a deep-dive different from a tutorial.

## Transports & authorization

| Concern        | Local                          | Remote                                                                          |
| -------------- | ------------------------------ | ------------------------------------------------------------------------------- |
| Transport      | **stdio** (subprocess pipes)   | **Streamable HTTP** (single endpoint, POST + GET, optional SSE) [[10]](https://chatforest.com/guides/mcp-transports-explained/) |
| Spawned by     | Host launches as child process | Long-running HTTP service                                                       |
| Auth model     | Env vars / OS-level secrets    | OAuth 2.1 resource-server (RFC 9728 metadata, RFC 8707 resource indicators, PKCE-SHA256 mandatory) [[11]](https://modelcontextprotocol.io/specification/draft/basic/authorization) |
| Deprecated     | —                              | HTTP+SSE transport (deprecated in 2025-03-26 spec, sunsetting through 2026) [[10]](https://chatforest.com/guides/mcp-transports-explained/) |
| Demo cost      | `uv run server.py`             | Container + reverse proxy + auth server                                         |

The 2026-07-28 RC removes the requirement for sticky sessions, so a remote MCP server can finally sit behind a plain round-robin load balancer [[6]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) — a real, talk-worthy operational win.

## What's new in 2026

The next major release is dated **2026-07-28** [[6]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/). Things worth slides:

| Change                  | Why it matters                                                                                                                                                                          |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stateless protocol core | Trades session ergonomics for horizontal scale — kills the "MCP doesn't fit our load balancer" objection [[6]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) |
| Extensions framework    | Reverse-DNS-namespaced capabilities versioned separately from core; the model used by MCP Apps and Tasks [[6]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) |
| MCP Apps (SEP-1865)     | Servers can ship interactive HTML rendered in a sandboxed iframe; UI talks back via JSON-RPC so the host still owns consent/audit [[26]](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/) [[27]](https://github.com/modelcontextprotocol/ext-apps) |
| Tasks extension         | Long-running ops get explicit handles (`tasks/get`, `tasks/update`, `tasks/cancel`) — the answer to "tool calls can't take 20 minutes" [[28]](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows) |
| Auth hardening (6 SEPs) | `iss` validation, clearer credential binding, tighter OAuth/OIDC alignment [[6]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)                              |
| 12-month deprecation    | Formal lifecycle policy; ≥1 year between deprecation and removal [[6]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)                                        |

The 2026 roadmap reorganised around **priority areas** (transport, agent comms, governance, enterprise) rather than dates, with Working Groups owning delivery [[25]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/).

## Ecosystem snapshot

| Project                                                                          | What it does                                          | GitHub                                                                                                        |
| -------------------------------------------------------------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| [Reference servers](https://github.com/modelcontextprotocol/servers)             | Official monorepo: fs, fetch, git, memory, time, etc. | ⭐ 86k [[14]](https://github.com/modelcontextprotocol/servers)                                                  |
| [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)           | Community discovery index                             | ⭐ 87k [[13]](https://github.com/punkpeye/awesome-mcp-servers)                                                  |
| [Context7](https://github.com/upstash/context7)                                  | Just-in-time library docs in context                  | ⭐ 55k [[17]](https://github.com/upstash/context7)                                                              |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp)                    | Browser automation via accessibility tree (Microsoft) | ⭐ 32k [[15]](https://github.com/microsoft/playwright-mcp)                                                      |
| [GitHub MCP](https://github.com/github/github-mcp-server)                        | Repos, PRs, issues, search (GitHub-official)          | ⭐ 30k [[16]](https://github.com/github/github-mcp-server)                                                      |
| [FastMCP](https://github.com/PrefectHQ/fastmcp)                                  | Pythonic high-level framework (v3.0 Jan 2026)         | ⭐ 25k [[18]](https://github.com/PrefectHQ/fastmcp)                                                             |
| [MCP Inspector](https://github.com/modelcontextprotocol/inspector)               | Browser-based debugger; the standard live-demo tool   | ⭐ 9.8k [[29]](https://github.com/modelcontextprotocol/inspector)                                               |
| [Official registry](https://github.com/modelcontextprotocol/registry)            | Canonical metadata backbone (Anthropic/GitHub/MS/PulseMCP) | ⭐ 6.8k [[30]](https://github.com/modelcontextprotocol/registry)                                            |
| [Spec repo](https://github.com/modelcontextprotocol/modelcontextprotocol)        | SEPs, schema, governance                              | ⭐ 8.1k [[7]](https://github.com/modelcontextprotocol/modelcontextprotocol)                                     |

By 2026-05, the tracked server count is ~14k across registries [[12]](https://zuplo.com/blog/one-year-of-mcp).

## MCP vs A2A vs function calling

Don't conflate these — the audience will ask:

| Protocol         | Created by      | What it standardises                              | When to reach for it                                        |
| ---------------- | --------------- | ------------------------------------------------- | ----------------------------------------------------------- |
| Function calling | OpenAI (2023)   | Per-vendor JSON-schema tool definitions in the model API itself [[21]](https://zilliz.com/blog/function-calling-vs-mcp-vs-a2a-developers-guide-to-ai-agent-protocols) | Quick prototypes; single-model apps; no integration sprawl  |
| **MCP**          | Anthropic (2024)| Transport between LLM hosts and external **tools/data** — vendor-neutral wire format [[20]](https://www.merge.dev/blog/mcp-vs-a2a) | One integration runs across all models; agentic apps        |
| A2A              | Google (Apr 2025) | Transport between **agents** themselves (discovery, task delegation, results) [[20]](https://www.merge.dev/blog/mcp-vs-a2a) | Multi-agent systems; framework-crossing coordination        |

Punch line for the talk: MCP and A2A are **complementary layers**, not rivals — both are now AAIF projects [[3]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation).

## Security — the part you cannot skip

This is the third in a series after AI and security; lean into it. Frame the section around Simon Willison's **lethal trifecta** [[22]](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/):

> **private data + untrusted instructions + an exfiltration vector → guaranteed exposure**

MCP makes that trifecta easy to assemble accidentally. Any host that connects (a) a server reading user files with (b) a server reading external content with (c) a server that can post outbound is one tool-poisoning payload away from data egress [[22]](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/).

**Concrete incidents to walk through (pick 3–4):**

| Date     | Incident                                              | Class                             | Source                                                              |
| -------- | ----------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------- |
| Apr 2025 | WhatsApp MCP — exfiltration via tool poisoning        | Tool poisoning                    | [[23]](https://authzed.com/blog/timeline-mcp-breaches)              |
| May 2025 | GitHub MCP — malicious issue leaks private repo data  | Indirect prompt injection         | [[23]](https://authzed.com/blog/timeline-mcp-breaches)              |
| Jul 2025 | **mcp-remote CVE-2025-6514** — RCE, 437k+ downloads   | OS command injection              | [[23]](https://authzed.com/blog/timeline-mcp-breaches)              |
| Sep 2025 | Postmark MCP supply-chain — BCC of every email        | Malicious package                 | [[23]](https://authzed.com/blog/timeline-mcp-breaches)              |
| Oct 2025 | Smithery hosting breach — 3,000+ servers exposed      | Supply-chain (hosting infra)      | [[23]](https://authzed.com/blog/timeline-mcp-breaches)              |
| Apr 2026 | Core stdio config-to-exec flaw — 150M+ downloads hit  | Design-level RCE                  | [[23]](https://authzed.com/blog/timeline-mcp-breaches)              |

A 2026 internet scan found up to **~200,000 vulnerable MCP instances** exposed across IDEs, internal tools, and cloud services [[24]](https://www.practical-devsecops.com/mcp-security-vulnerabilities/) — surface that number on a slide; it lands.

**Host-side mitigations to recommend** (the spec can't enforce these, only hosts can [[5]](https://modelcontextprotocol.io/specification/2025-11-25)):

1. Treat tool descriptions and annotations as **untrusted** unless the server identity is verified [[5]](https://modelcontextprotocol.io/specification/2025-11-25).
2. Pin server versions; check the registry's provenance metadata before install [[30]](https://github.com/modelcontextprotocol/registry).
3. Per-tool consent UI, not blanket per-server approval [[5]](https://modelcontextprotocol.io/specification/2025-11-25).
4. Forbid mixing read-untrusted-content tools with read-private-data tools in the same session — the trifecta rule [[22]](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/).
5. For HTTP transports: enforce `aud`/`iss` on tokens; never accept tokens not minted for *this* server [[11]](https://modelcontextprotocol.io/specification/draft/basic/authorization).

## Live-demo recipes

| Demo                       | Stack                                                                                                            | Wow factor                                                                  |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| "Hello, tool"              | FastMCP server with one `@mcp.tool`, stdio transport, wired to Claude Desktop [[18]](https://github.com/PrefectHQ/fastmcp) [[19]](https://modelcontextprotocol.io/docs/develop/build-server) | Build-to-call in under 5 minutes                                            |
| Inspect everything         | Same server + `mcp-inspector` in browser [[29]](https://github.com/modelcontextprotocol/inspector)               | Visual JSON-RPC traffic; great for teaching primitives                      |
| Tool poisoning (sandbox!)  | Toy server whose tool description contains a hidden "exfiltrate" instruction; show the agent obeying it [[22]](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/) | The talk's most memorable 90 seconds                                        |
| Elicitation                | Tool that calls `elicitation/create` to ask the user for a missing arg mid-call [[8]](https://workos.com/blog/mcp-features-guide) | Shows the consent loop the security section was warning about               |
| MCP Apps (stretch)         | Server returning a `ui://` resource rendered in a sandboxed iframe [[27]](https://github.com/modelcontextprotocol/ext-apps) | Demonstrates 2026's most ambitious extension                                |

## Outlook — three things to watch

1. **Stateless MCP at scale** — does the 2026-07-28 RC really let MCP run on the same infra as REST APIs? Production reports from Uber/Nordstrom say "yes, with caveats" [[4]](https://aaif.io/blog/mcp-is-now-enterprise-infrastructure-everything-that-happened-at-mcp-dev-summit-north-america-2026/).
2. **Registry-as-trust-root** — official registry provenance is the only realistic answer to supply-chain attacks like Postmark and the Oura clone [[23]](https://authzed.com/blog/timeline-mcp-breaches) [[30]](https://github.com/modelcontextprotocol/registry).
3. **MCP Apps adoption** — if servers can ship trusted UI, the line between "tool" and "mini-app" blurs. Either it becomes the new agent UX or a niche [[26]](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/).
