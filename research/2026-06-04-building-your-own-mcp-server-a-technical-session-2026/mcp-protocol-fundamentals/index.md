---
title: "MCP Protocol Fundamentals: What You Must Know to Build a Server"
date: 2026-06-04
depth: standard
format: md
topic: "MCP protocol fundamentals — transports (stdio, Streamable HTTP / SSE), the three primitives (tools, resources, prompts), the initialization handshake & lifecycle, capability negotiation, JSON-RPC message shapes, and protocol versioning. What a developer must understand to build an MCP server. Cover the current (2026) spec revision and note what changed recently."
topic_raw: "MCP protocol fundamentals"
tags: [mcp, protocol, json-rpc, llm-tooling, typescript-sdk]
summary: "The wire-level mechanics of MCP — transports, three primitives, lifecycle handshake, capability negotiation, JSON-RPC shapes, and versioning — on the current 2025-11-25 spec, with what's changing in 2026."
citations: 16
reading_time_min: 9
---

> **TL;DR.** MCP is JSON-RPC 2.0 over one of two transports — **stdio** (local subprocess) or **Streamable HTTP** (remote, one endpoint, optional SSE) [[3]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports). A server exposes three primitives — **tools** (model-controlled), **resources** (app-driven), **prompts** (user-controlled) — discovered via `*/list` and invoked via `tools/call` / `resources/read` / `prompts/get` [[5]](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)[[6]](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)[[7]](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts). Every connection opens with an `initialize` → `initialize` result → `notifications/initialized` handshake that negotiates a date-string protocol version and per-feature capabilities [[4]](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle). **Current stable spec: `2025-11-25`** [[1]](https://modelcontextprotocol.io/specification/2025-11-25). The TS SDK [[10]](https://github.com/modelcontextprotocol/typescript-sdk) ⭐ 12.6k hides most of this — but the wire contract below is what leaks through when something breaks.

## Architecture in one paragraph

MCP is host/client/server over [JSON-RPC 2.0](https://www.jsonrpc.org/specification). A **host** (the LLM app) spawns one **client** per connection; each client talks to one **server** [[1]](https://modelcontextprotocol.io/specification/2025-11-25). Connections are stateful and bidirectional: the server can call *back* into the client (sampling, elicitation, roots) during a request. Servers expose **tools / resources / prompts**; clients expose **sampling / roots / elicitation** [[1]](https://modelcontextprotocol.io/specification/2025-11-25). The spec is a TypeScript schema (`schema.ts`) that is the source of truth; the JSON Schema is generated from it [[9]](https://modelcontextprotocol.io/specification/2025-11-25/basic).

## JSON-RPC message shapes

Three message types, nothing more. The ID rules are the part that bites SDK authors [[9]](https://modelcontextprotocol.io/specification/2025-11-25/basic):

| Message      | Shape                                              | Rules                                                                 |
| ------------ | -------------------------------------------------- | --------------------------------------------------------------------- |
| Request      | `{jsonrpc, id, method, params?}`                   | `id` MUST be string/integer, **MUST NOT be `null`**, unique per session [[9]][a] |
| Result       | `{jsonrpc, id, result}`                            | same `id` as request; `result` any JSON object [[9]][a]               |
| Error        | `{jsonrpc, id, error:{code, message, data?}}`      | `code` MUST be integer; same `id` (except unreadable/malformed) [[9]][a] |
| Notification | `{jsonrpc, method, params?}`                       | **no `id`**; receiver MUST NOT reply [[9]][a]                         |

[a]: https://modelcontextprotocol.io/specification/2025-11-25/basic

**JSON-RPC batching is gone.** It was added in `2025-03-26` and removed in `2025-06-18`; do not send or expect arrays of messages on the current spec [[13]](https://finance.biggo.com/news/202506190713_MCP_Removes_Batching_Adds_OAuth_Security). (The transport doc's batch language predates the removal.)

Two MCP-specific error codes worth knowing: `-32002` resource-not-found [[6]](https://modelcontextprotocol.io/specification/2025-11-25/server/resources); the rest are standard JSON-RPC (`-32602` invalid params, `-32603` internal).

## Transports

| Axis              | stdio                                              | Streamable HTTP                                                    |
| ----------------- | -------------------------------------------------- | ----------------------------------------------------------------- |
| Topology          | Client launches server as subprocess               | Independent process, many clients                                 |
| Framing           | Newline-delimited JSON on `stdin`/`stdout`         | One HTTP endpoint, `POST` + `GET`                                 |
| Logging           | Free-form on `stderr` (any log level)              | Out of band                                                       |
| Streaming         | n/a                                                | Optional SSE (`text/event-stream`) for server→client             |
| Auth              | Credentials from **env** (not the OAuth framework) | OAuth 2.0 framework [[9]][a]                                       |
| Use when          | Local tools, CLIs, IDE plugins                     | Remote / multi-client / hosted                                    |
| Caveat            | Single-client; collapses under concurrency [[15]][b] | DNS-rebinding risk → validate `Origin` [[3]][c]                  |

[a]: https://modelcontextprotocol.io/specification/2025-11-25/basic
[b]: https://www.truefoundry.com/blog/mcp-stdio-vs-streamable-http-enterprise
[c]: https://modelcontextprotocol.io/specification/2025-03-26/basic/transports

**stdio (prefer it when you can).** Client launches the server as a subprocess; messages are JSON-RPC, newline-delimited, **MUST NOT contain embedded newlines**, and `stdout` MUST carry *only* valid MCP messages — stray `console.log` corrupts the stream [[3]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports). Put all logging on `stderr` [[8]](https://modelcontextprotocol.io/specification/2025-11-25/changelog). Clients SHOULD support stdio whenever possible [[3]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports).

**Streamable HTTP (the remote standard).** A single MCP endpoint (e.g. `https://example.com/mcp`) handling both `POST` and `GET` [[3]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports):

- **Client → server:** every JSON-RPC message is a `POST`. The `Accept` header MUST list both `application/json` and `text/event-stream` [[3]][c].
- **Response forking:** if the POST body is only responses/notifications, the server returns `202 Accepted` (no body). If it contains requests, the server returns *either* `application/json` (one object) *or* `text/event-stream` (an SSE stream that eventually yields one response per request) — the client MUST handle both [[3]][c].
- **Server → client without a request:** client `GET`s the endpoint to open an SSE stream; server returns `text/event-stream` or `405 Method Not Allowed` if it offers none [[3]][c].
- **Sessions:** server MAY return `Mcp-Session-Id` on the `InitializeResult`; if so the client MUST echo it on every later request. Missing it → `400`; terminated session → `404` (client then re-`initialize`s); client `DELETE` ends a session [[3]][c].
- **Resumability:** SSE events carry an `id`; client reconnects with `Last-Event-ID` to replay missed events on that stream [[3]][c].

[c]: https://modelcontextprotocol.io/specification/2025-03-26/basic/transports

**SSE / legacy.** The old two-endpoint **HTTP+SSE** transport (separate `GET` SSE channel + `POST` endpoint) from `2024-11-05` was *replaced* by Streamable HTTP in `2025-03-26` and is deprecated; SSE now lives *inside* Streamable HTTP as an optional streaming mode, not a separate transport [[14]](https://brightdata.com/blog/ai/sse-vs-streamable-http). For backward compat a client probes by POSTing `initialize`; a `4xx` means fall back to the old GET-an-`endpoint`-event flow [[3]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports).

**Protocol-version header (HTTP only).** After init, the client MUST send `MCP-Protocol-Version: <version>` on every request. If the header is absent and the version can't be inferred, servers default to `2025-03-26` for back-compat [[4]](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle). ⚠ A known TS-SDK quirk: if the header disagrees with the body's `protocolVersion` on `initialize`, the body wins and no error is raised [[13]](https://finance.biggo.com/news/202506190713_MCP_Removes_Batching_Adds_OAuth_Security).

## The lifecycle handshake

Three steps, always, before any feature call [[4]](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle):

```jsonc
// 1. client → server
{ "jsonrpc":"2.0", "id":1, "method":"initialize", "params":{
    "protocolVersion":"2025-11-25",
    "capabilities":{ "roots":{"listChanged":true}, "sampling":{}, "elicitation":{} },
    "clientInfo":{ "name":"ExampleClient", "version":"1.0.0" } } }

// 2. server → client (result): echoes version, declares its capabilities + serverInfo,
//    optional top-level "instructions" string the client can feed the model
{ "jsonrpc":"2.0", "id":1, "result":{
    "protocolVersion":"2025-11-25",
    "capabilities":{ "tools":{"listChanged":true}, "resources":{"subscribe":true,"listChanged":true}, "prompts":{"listChanged":true}, "logging":{} },
    "serverInfo":{ "name":"ExampleServer", "version":"1.0.0" },
    "instructions":"Optional instructions for the client" } }

// 3. client → server (notification, no id): handshake complete
{ "jsonrpc":"2.0", "method":"notifications/initialized" }
```

Rules that matter for a server author [[4]](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle):

- Before the client's `initialized` arrives, the server SHOULD send only `ping` or `logging` — no feature traffic.
- **Version negotiation:** versions are **date strings**, not semver. Client sends its latest; if the server supports it, it MUST echo the *same* string. If not, it MUST reply with another version it supports (its latest). If the client doesn't support that, it SHOULD disconnect. On an explicit error the server returns `-32602` with `data.supported` listing versions [[4]][d].
- **Shutdown** has no message — for stdio, close the child's `stdin`, then `SIGTERM`/`SIGKILL`; for HTTP, close the connection(s) [[4]][d].
- **Timeouts:** senders SHOULD time out requests and emit a `CancelledNotification`; progress notifications MAY reset the clock but a hard cap SHOULD remain [[4]][d].

[d]: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle

## Capability negotiation

You can only use a feature both sides declared at init. Declaring a capability is what *enables* its methods and notifications [[4]](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle):

| Side   | Capability      | Unlocks                                                        |
| ------ | --------------- | ------------------------------------------------------------- |
| Server | `tools`         | `tools/list`, `tools/call`; `listChanged` sub-cap [[5]][e]    |
| Server | `resources`     | `resources/list` `/read` `/templates/list`; `subscribe`, `listChanged` sub-caps [[6]][f] |
| Server | `prompts`       | `prompts/list`, `prompts/get`; `listChanged` sub-cap [[7]][g] |
| Server | `logging`       | `notifications/message` log emission [[4]][d]                 |
| Server | `completions`   | argument autocompletion [[4]][d]                              |
| Server | `tasks`         | experimental durable/async requests (new in 2025-11-25) [[8]][h] |
| Client | `roots`         | server asks for filesystem/URI boundaries [[4]][d]            |
| Client | `sampling`      | server requests an LLM completion through the client [[4]][d] |
| Client | `elicitation`   | server asks the user for structured input [[4]][d]            |

[d]: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle
[e]: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
[f]: https://modelcontextprotocol.io/specification/2025-11-25/server/resources
[g]: https://modelcontextprotocol.io/specification/2025-11-25/server/prompts
[h]: https://modelcontextprotocol.io/specification/2025-11-25/changelog

Two sub-capability flags recur: `listChanged` (server will emit `notifications/<x>/list_changed` when its catalog changes) and, for resources only, `subscribe` (per-item change notifications) [[4]](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle).

## The three primitives

The whole mental model: **who's in control** differs per primitive — that decides where your UX consent lives [[5]](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)[[6]](https://modelcontextprotocol.io/specification/2025-11-25/server/resources)[[7]](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts).

| Primitive  | Control          | List           | Invoke           | Item key fields                                  | Change signals                                   |
| ---------- | ---------------- | -------------- | ---------------- | ------------------------------------------------ | ------------------------------------------------ |
| Tools      | model-controlled | `tools/list`   | `tools/call`     | `name`, `inputSchema`, `outputSchema`, `annotations` [[5]][e] | `notifications/tools/list_changed` [[5]][e]      |
| Resources  | app-driven       | `resources/list` (+ `/templates/list`) | `resources/read` | `uri`, `name`, `mimeType` [[6]][f]   | `.../list_changed`, `.../updated` (subscribe) [[6]][f] |
| Prompts    | user-controlled  | `prompts/list` | `prompts/get`    | `name`, `arguments[]` [[7]][g]                   | `notifications/prompts/list_changed` [[7]][g]    |

[e]: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
[f]: https://modelcontextprotocol.io/specification/2025-11-25/server/resources
[g]: https://modelcontextprotocol.io/specification/2025-11-25/server/prompts

### Tools — model-controlled (the one you'll build first)

`tools/list` (paginated via `cursor`/`nextCursor`) returns Tool objects: `name` (1–128 chars, `[A-Za-z0-9_.-]`), optional `title`/`description`/`icons`, `inputSchema` (JSON Schema **object**, never `null`; use `{"type":"object","additionalProperties":false}` for no-arg tools), optional `outputSchema`, `annotations`, and `execution.taskSupport` (`forbidden`/`optional`/`required`) [[5]](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).

`tools/call` returns `content[]` (text / image / audio / `resource_link` / embedded `resource`) plus `isError` [[5]](https://modelcontextprotocol.io/specification/2025-11-25/server/tools). If you set `outputSchema`, you MUST also return `structuredContent` conforming to it — and, for back-compat, SHOULD serialize that same JSON into a `text` block [[5]](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).

⚠ **Error model is two-tier and easy to get wrong.** Unknown tool / malformed request → JSON-RPC **protocol error** (`-32602`). API failure / input-validation / business error → a normal result with **`isError: true`** so the model sees it and can self-correct. Returning a validation failure as a protocol error denies the model its retry path [[5]](https://modelcontextprotocol.io/specification/2025-11-25/server/tools). The `2025-11-25` revision explicitly reclassified input-validation errors as tool errors for this reason [[8]](https://modelcontextprotocol.io/specification/2025-11-25/changelog).

### Resources — app-driven

URI-identified context. `resources/list` and `resources/read` (returns `contents[]` with `text` or base64 `blob`); `resources/templates/list` exposes RFC 6570 `uriTemplate`s for parameterized resources [[6]](https://modelcontextprotocol.io/specification/2025-11-25/server/resources). Standard URI schemes: `https://` (only when the *client* can fetch directly), `file://`, `git://`, or custom (RFC 3986) [[6]](https://modelcontextprotocol.io/specification/2025-11-25/server/resources). With the `subscribe` sub-cap, `resources/subscribe` + `notifications/resources/updated` push per-resource change events; `listChanged` covers catalog changes [[6]](https://modelcontextprotocol.io/specification/2025-11-25/server/resources).

### Prompts — user-controlled

Reusable templated conversations, surfaced as user actions (often slash commands). `prompts/list` returns Prompt objects (`name`, `arguments[]`); `prompts/get` substitutes arguments and returns `messages[]` of `{role, content}` where content is text / image / audio / embedded resource [[7]](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts). Because prompts are user-invoked, the consent UX lives at selection, not at execution [[7]](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts).

## What changed recently (and what's next)

**Now (`2025-11-25`, current stable)** vs `2025-06-18` [[8]](https://modelcontextprotocol.io/specification/2025-11-25/changelog):

- **Tasks (experimental)** — turn any request into call-now/fetch-later with polling; states like `working`/`input_required`/`completed`/`failed`/`cancelled`. Kills fake progress spinners for long jobs [[12]](https://workos.com/blog/mcp-2025-11-25-spec-update).
- **Icons** on tools/resources/prompts/implementations (SEP-973) — `src` must be `https:`/`data:`, treated as untrusted [[9]](https://modelcontextprotocol.io/specification/2025-11-25/basic).
- **JSON Schema 2020-12** is now the default dialect when `$schema` is absent (SEP-1613) [[8]](https://modelcontextprotocol.io/specification/2025-11-25/changelog).
- **OAuth hardening** — OIDC discovery, incremental scope consent via `WWW-Authenticate`, and **Client ID Metadata Documents** replacing Dynamic Client Registration (DNS+HTTPS-anchored trust) [[8]](https://modelcontextprotocol.io/specification/2025-11-25/changelog)[[12]](https://workos.com/blog/mcp-2025-11-25-spec-update).
- **Tool-name guidance**, **SDK tiering**, and **input-validation → tool errors** clarifications [[8]](https://modelcontextprotocol.io/specification/2025-11-25/changelog).
- Earlier (`2025-06-18`): **JSON-RPC batching removed** — still gone [[13]](https://finance.biggo.com/news/202506190713_MCP_Removes_Batching_Adds_OAuth_Security).

**Next (`2026-07-28`, release candidate, RC locked May 2026, final July 2026)** — the largest revision since launch: a **stateless protocol core** that scales on ordinary HTTP infrastructure, an **Extensions framework**, promotion of **Tasks**, **MCP Apps** (server-rendered UI), and deeper OAuth/OIDC alignment [[2]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)[[16]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/). For a session today, **build against `2025-11-25`** and treat the stateless core as the near-term direction of travel. The TS SDK [[10]](https://github.com/modelcontextprotocol/typescript-sdk) ⭐ 12.6k (Jun 2026) is Tier 1, so it tracks these within the spec's validation window [[2]](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/).

## Minimum a server author must implement

1. Pick a transport — stdio for local, Streamable HTTP for remote [[3]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports).
2. Answer `initialize`: echo a supported `protocolVersion`, declare your capabilities, send `serverInfo`; wait for `notifications/initialized` [[4]](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle).
3. Implement at least one primitive's `*/list` + invoke pair, declaring its capability [[5]](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).
4. Return tool failures as `isError: true` results, not protocol errors [[5]](https://modelcontextprotocol.io/specification/2025-11-25/server/tools).
5. On Streamable HTTP: validate `Origin` (DNS-rebinding), bind localhost when local, handle `Mcp-Session-Id` and `MCP-Protocol-Version` [[3]](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)[[4]](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle).

The schema source of truth is `schema.ts` in the spec repo [[11]](https://github.com/modelcontextprotocol/modelcontextprotocol) ⭐ 8.3k — when an SDK's types and the docs disagree, the schema wins [[9]](https://modelcontextprotocol.io/specification/2025-11-25/basic).
