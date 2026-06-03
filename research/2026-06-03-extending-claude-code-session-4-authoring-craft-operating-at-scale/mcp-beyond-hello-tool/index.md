---
title: "MCP beyond \"hello tool\""
date: 2026-06-03
depth: standard
format: md
topic: "MCP beyond \"hello tool\""
topic_raw: "MCP beyond \"hello tool\""
issue: 181
tags: [mcp, model-context-protocol, agents, security, talk-prep, production, developer]
summary: "Six primitives, two transports, tool design patterns, tool-poisoning attack chains, and the 2026 production gaps — everything past the first tutorial."
citations: 19
reading_time_min: 10
cover: cover.svg
cost_usd: 1.41
duration_sec: 680
model: "Sonnet 4.6"
---

> **TL;DR** Most "hello tool" tutorials show one of six MCP primitives on one of two transports. The expert path: design tools at workflow granularity (not API-copy), deploy the three client-side primitives (sampling, elicitation, roots) for genuine agent patterns [[4]](https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip), put OAuth 2.1 in from day one [[2]](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026), and treat every tool `description` field as a prompt-injection surface. [[11]](https://www.practical-devsecops.com/mcp-tool-poisoning/)

## The full surface area

MCP has six primitives across two directions, plus an experimental Tasks extension [[1]](https://modelcontextprotocol.io/docs/learn/architecture):

**Server → client (what every tutorial shows):**

| Primitive | Caller     | Use for                                        |
|-----------|-----------|------------------------------------------------|
| Tools     | LLM/model | Actions with side effects                      |
| Resources | App/user  | Read-only context (files, DB schemas, configs) |
| Prompts   | User      | Reusable structured interaction templates      |

[t1]: https://modelcontextprotocol.io/docs/learn/architecture

The key distinction: tools are *model-controlled*, resources and prompts are *application-controlled*. [[3]](https://devblogs.microsoft.com/visualstudio/mcp-prompts-resources-sampling/) A resource is not a slow tool — it is context the host decides when to include; a prompt is a server-curated template the user invokes explicitly.

**Client → server (what most builders skip):**

| Primitive   | Server calls this to…                                                |
|-------------|----------------------------------------------------------------------|
| Sampling    | Request LLM completions without needing its own API keys             |
| Elicitation | Pause execution and collect structured user input via a native form  |
| Roots       | Learn which filesystem paths / URIs the client has scoped open       |

[t2]: https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip

"The right side — what clients expose *to* servers — is what unlocks genuinely new patterns. Server-side tools alone are just a better function-call API." [[4]](https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip)

## Transport: an architectural choice you make once

| Dimension      | stdio                              | Streamable HTTP                          |
|----------------|------------------------------------|------------------------------------------|
| Topology       | Local subprocess, one machine      | Remote, many clients per server          |
| Session model  | Inherently stateful                | Stateful today; stateless on roadmap     |
| Auth surface   | OS process isolation               | Bearer / API key / OAuth 2.1             |
| Scale          | One client per process             | Load-balanced (with sticky-session caveat)|
| Typical use    | Desktop apps, dev tooling          | SaaS integrations, multi-tenant agents   |

Streamable HTTP replaced the legacy SSE transport in the Nov 2025 spec. [[2]](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026) Current production pain: stateful sessions require sticky routing, which fights load balancers. The 2026 roadmap removes `Mcp-Session-Id` from the protocol layer so any server instance can handle any request. [[15]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)

## Lifecycle: the initialization handshake

Every MCP connection opens with capability negotiation [[1]](https://modelcontextprotocol.io/docs/learn/architecture):

```json
// client → server
{ "capabilities": { "elicitation": {}, "roots": { "listChanged": true } } }
// server → client
{ "capabilities": { "tools": { "listChanged": true }, "resources": {} } }
```

Never call a primitive the peer didn't declare. When a server advertises `tools: { listChanged: true }`, it may push `notifications/tools/list_changed` at any time — for example, when a user authenticates and gains access to additional tools. Clients must re-call `tools/list` on receipt to stay synchronized.

## Roots: scoped context without guessing

Roots are URIs (typically `file:///…` paths) the client declares so the server knows its operative working set. [[7]](https://workos.com/blog/mcp-roots-guide) They are informational, not strictly enforced at protocol level, but well-behaved servers scope all operations to declared roots. [[8]](https://modelcontextprotocol.io/specification/2025-06-18/client/roots) The filesystem reference server replaces its allowed-directories config entirely with client-provided roots; the IDE's workspace picker — not the server config — controls access. Dynamic `roots/list_changed` notifications let scope shift without reconnecting.

## Client-side primitives: what builders skip

### Sampling

Server sends `sampling/createMessage` through the client → client routes to the user's configured LLM → result returns to the server. No server-side API keys. The client retains control over model selection, cost, and audit logging. [[5]](https://medium.com/@__nagarajan__/mcp-concepts-sampling-and-elicitation-95c5c0c4df71)

```python
response = await ctx.session.create_message(
    messages=[SamplingMessage(role="user", content=TextContent(text=log_text))],
    system_prompt="Identify root causes and suggest remediation.",
    max_tokens=512,
)
```

Best fits: intent routing before dispatch, data extraction from unstructured outputs, post-call summarization, validation before destructive actions. [[4]](https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip) Avoid for real-time voice pipelines (adds 200–800ms latency).

> ⚠ The 2026-07-28 draft RC (SEP-2577) proposes deprecating sampling — servers wanting LLM access should migrate to direct provider API calls once the spec stabilises.

### Elicitation

Server sends `elicitation/create` with a JSON schema → client renders a native form → returns validated data or `decline`/`cancel`. [[6]](https://mcginniscommawill.com/posts/2026-03-25-mcp-sampling-elicitation-guide/)

```python
result = await ctx.elicit(
    "⚠️ Confirm deletion of 4,200 records",
    schema=DeletionConsent,          # Pydantic or dataclass
)
if result.action == "accept" and result.data.confirmed:
    await delete_records()
```

Use as an execution gate for destructive operations and for OAuth credential flows (URL mode). Never request passwords or API keys through form-mode elicitation — use URL-mode redirect to the auth provider. [[5]](https://medium.com/@__nagarajan__/mcp-concepts-sampling-and-elicitation-95c5c0c4df71)

**Client support — June 2026:** VS Code (GitHub Copilot) supports both. Claude Desktop and Claude Code support neither. Always check `extra.session.clientCapabilities` at runtime and provide graceful degradation. [[6]](https://mcginniscommawill.com/posts/2026-03-25-mcp-sampling-elicitation-guide/)

| Scenario                            | Use         |
|-------------------------------------|-------------|
| AI reasoning / classification       | Sampling    |
| User confirmation before action     | Elicitation |
| Structured user input (forms)       | Elicitation |
| Text generation / summarisation     | Sampling    |
| OAuth / credential entry            | Elicitation (URL mode) |

## Tool design patterns

Four patterns for managing tool surface at scale [[9]](https://www.klavis.ai/blog/less-is-more-mcp-design-patterns-for-ai-agents):

| Pattern                  | When to use                                              | Trade-off                             |
|--------------------------|----------------------------------------------------------|---------------------------------------|
| **Workflow-based**       | Known, repeated multi-step user goals                    | Less flexible; best for production    |
| **Semantic search**      | Large catalog (50+ tools) with distinct purposes         | Search quality drives accuracy        |
| **Code mode**            | Data-heavy batch ops, complex branching logic            | Sandbox security + debug complexity   |
| **Progressive discovery**| Diverse capabilities, unknown request shape at design time | One extra round-trip per stage      |

Workflow example: replace `create_project()` + `add_env_vars()` + `create_deployment()` + `add_domain()` with a single `deploy_project(repo, domain, env_vars, branch)`. Fewer tokens, fewer failure points, clearer model intent. [[9]](https://www.klavis.ai/blog/less-is-more-mcp-design-patterns-for-ai-agents)

Code mode extreme: one CRM replaced 50+ sequential tool calls (200k+ tokens) with a single `execute_code` tool in a sandbox. [[9]](https://www.klavis.ai/blog/less-is-more-mcp-design-patterns-for-ai-agents)

## Anti-patterns, ranked by blast radius

[[10]](https://www.digitalapplied.com/blog/mcp-server-anti-patterns-design-mistakes-2026-developer-guide):

| # | Anti-pattern                | Score | Why it kills you                                            | Fix                                           |
|---|----------------------------|-------|-------------------------------------------------------------|-----------------------------------------------|
| 1 | No audit gates              | 96    | Destructive tools execute immediately; irreversible         | Dry-run first; name the gate in `description` |
| 2 | Auth after build            | 90    | Retrofitting breaks every existing client                   | Decide trust boundary on day one; fail closed |
| 3 | God-tools                   | 82    | Model can't determine valid param combos; silent miscalls   | One tool per user intent, tight schema        |
| 4 | Schema over-fit             | 74    | Phrasing variation → model refuses or miscalls              | Loosen strings, tighten descriptions          |
| 5 | Missing error discrimination| 62    | Model retries identically; can't choose recovery path       | Discriminate: validation / timeout / 4xx / 5xx|
| 6 | Chatty protocols            | 54    | 200–400ms per round-trip compounds invisibly                | Collapse list-then-get into one filtered call |
| 7 | Omnibus params blob         | 46    | `options: Record<string, unknown>` → silent invalid combos  | Named optional fields                         |

"A god-tool with an under-specified schema and no audit gate is the modal production failure mode in 2026." [[10]](https://www.digitalapplied.com/blog/mcp-server-anti-patterns-design-mistakes-2026-developer-guide)

## Security: tool descriptions are the new attack surface

*(Directly extends session 1 — AI security)*

**Tool poisoning** is prompt injection via the tool manifest [[11]](https://www.practical-devsecops.com/mcp-tool-poisoning/):

1. Attacker embeds instructions inside the `description` field of a tool manifest
2. LLM treats the manifest as authoritative — it follows embedded directives as part of normal reasoning
3. Silent side effects execute alongside the legitimate tool invocation; the user sees expected output

**The Rug Pull variant:** a legitimate tool builds user trust over weeks, then the operator updates `description` with data-harvesting instructions. Since manifests aren't version-locked at install time, every subsequent session is compromised immediately. A 2026 disclosure found ~200,000 vulnerable MCP instances across IDEs, internal tools, and cloud services. [[12]](https://www.practical-devsecops.com/mcp-security-vulnerabilities/)

MCPTox benchmark (45 live servers, 353 authentic tools): popular agents showed attack success rates above 60%, highest 72%. [[13]](https://www.mdpi.com/2624-800X/6/3/84)

**Defenses** [[11]](https://www.practical-devsecops.com/mcp-tool-poisoning/):

| Defense                        | Mechanism                                                                  |
|-------------------------------|----------------------------------------------------------------------------|
| Manifest pinning + signing    | Hash all tool descriptions at baseline; verify against stored hashes at session init |
| Allowlist + version pinning   | Only connect to approved registry entries with explicit version locks      |
| Semantic content scanning     | Pre-filter descriptions through a secondary model before consumption       |
| Cross-tool call correlation   | Flag unexpected A→B invocation chains                                      |
| Least privilege per tool      | Each tool's permissions scoped to minimum required; never ambient credentials |

**OAuth 2.1 in production** [[2]](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026):

- MCP servers are **OAuth Resource Servers**; Resource Indicators (RFC 8707) are mandatory — they bind tokens to specific servers and prevent reuse across servers
- PKCE required; Dynamic Client Registration optional but common
- **Client ID Metadata Documents (CIMD)** (Nov 2025 spec): client identity is a URL pointing to a JSON document the client controls; auth servers fetch on demand — no registration database per client
- **Session-scoped authorization**: access ends when the session ends; agents cannot self-renew — a human must explicitly approve a new session

## Tasks: async without inventing a control plane

The Tasks extension (SEP-1686, experimental as of June 2026) decouples submission from result retrieval [[14]](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows):

Client adds `task: { ttl: 60000 }` to any request → server returns `taskId` immediately → client polls `tasks/get` for status or calls `tasks/result` (blocking until terminal). Result format is identical to the synchronous response.

**Five-state machine:** `working` → `completed | failed | cancelled`, or `working` → `input_required` → `working | cancelled`. Terminal states are immutable — no backward transitions during retries or network races.

Task IDs are **capability tokens**: scoped to the authorization context that created them. Every follow-up call (`tasks/get`, `tasks/result`, `tasks/cancel`) must verify ownership, or return not-found. [[14]](https://workos.com/blog/mcp-async-tasks-ai-agent-workflows)

Use Tasks when: operation may exceed transport timeout, agents need to parallelize multiple long-running calls, or multi-step human-in-the-loop flows are needed. The `input_required` state is particularly powerful — the server signals it needs more information without any custom control-plane protocol.

## 2026 roadmap: what's being fixed

[[15]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) [[16]](https://thenewstack.io/model-context-protocol-roadmap-2026/)

| Priority       | Current pain                                      | Fix                                               |
|----------------|---------------------------------------------------|---------------------------------------------------|
| Transport      | Stateful sessions fight load balancers            | Stateless Streamable HTTP; `Mcp-Method` routing   |
| Discovery      | Must connect live to learn server capabilities    | `.well-known` MCP Server Cards                    |
| Tasks          | No retry semantics; no expiry policies            | SEP-1686 lifecycle refinements                    |
| Enterprise     | No audit trails, SSO, multi-tenancy patterns      | Extensions (not core protocol changes)            |

MCP governance moved under the Linux Foundation's Agentic AI Foundation in December 2025. Working Groups (Transports, Auth, Registry) now process domain SEPs independently, with Core Maintainers retaining strategic oversight. [[2]](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026)

## Tooling

- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) ⭐ 10.0k — interactive debugger; run against any server to see raw JSON-RPC and test all three primitive types [[17]](https://github.com/modelcontextprotocol/inspector)
- [Reference servers](https://github.com/modelcontextprotocol/servers) ⭐ 87k — filesystem, git, GitHub, Slack, Postgres, memory; canonical patterns for tools, resources, and prompt implementations [[18]](https://github.com/modelcontextprotocol/servers)
- [Protocol spec repo](https://github.com/modelcontextprotocol/modelcontextprotocol) ⭐ 8.3k — SEPs live here as GitHub issues; follow open proposals to track spec direction before it ships [[19]](https://github.com/modelcontextprotocol/modelcontextprotocol)
