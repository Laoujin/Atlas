---
title: "Security & Auth for MCP Servers: What to Teach Builders in 2026"
date: 2026-06-04
depth: standard
format: md
topic: "Security & auth for MCP servers (2026) — the MCP authorization spec (OAuth 2.1 resource-server model, protected-resource metadata, spec revisions) plus the threat landscape (tool poisoning, prompt injection via tool results, confused deputy, token passthrough, over-broad scopes, supply chain) with concrete mitigations."
topic_raw: "Security and auth"
tags: [mcp, security, oauth, authorization, prompt-injection, supply-chain]
summary: "The MCP auth spec makes your server an OAuth 2.1 resource server; the real danger is the agent layer — poisoned tool descriptions and injected tool results. Teach both."
citations: 18
reading_time_min: 7
---

> **TL;DR for the session.** Two layers to teach. **(1) Protocol auth is solved-ish:** since the 2025-06-18 spec your MCP server is an OAuth 2.1 *resource server* — it validates externally-issued tokens, advertises its auth server via RFC 9728 protected-resource metadata, enforces audience binding (RFC 8707), and **MUST NOT** pass tokens through to upstream APIs [[1]](https://modelcontextprotocol.io/specification/draft/basic/authorization)[[3]](https://www.descope.com/blog/post/mcp-auth-spec). **(2) The auth spec does not protect you from the agent layer** — the live 2026 threat is tool poisoning and prompt-injection-via-tool-results, where a malicious tool *description* or returned *result* hijacks the model. Anchor the session on: validate token audience, never proxy tokens, least-privilege scopes, and treat every tool description and tool result as untrusted input [[5]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)[[2]](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices).

This audience (Java/.NET devs on the official TypeScript SDK) already knows OAuth. Spend session time on **what's MCP-specific**: the resource-server reclassification, audience binding, and the agent-layer threats OAuth was never designed to stop.

## Part 1 — The MCP authorization spec

### The model: your server is an OAuth 2.1 resource server

A protected MCP server is an **OAuth 2.1 resource server** — it accepts and validates access tokens, it does *not* issue them. The authorization server is a separate role (your IdP: Entra, Auth0, Keycloak, Okta) [[1]](https://modelcontextprotocol.io/specification/draft/basic/authorization). This is the single most important framing for the session: **you are not building an OAuth server, you are protecting a resource.**

Hard requirements from the current spec, in the order a request hits them [[1]](https://modelcontextprotocol.io/specification/draft/basic/authorization):

| # | Requirement | Who | Level |
|---|-------------|-----|-------|
| 1 | Serve RFC 9728 **protected-resource metadata** (`/.well-known/oauth-protected-resource`) with an `authorization_servers` field | server | MUST |
| 2 | On missing/invalid token, return `401` with a `WWW-Authenticate` header pointing at `resource_metadata` (and ideally a `scope` hint) | server | MUST |
| 3 | Use **OAuth 2.1 + PKCE `S256`**; refuse to proceed if the AS doesn't advertise `code_challenge_methods_supported` | client | MUST |
| 4 | Send the **`resource` parameter** (RFC 8707) on every authz + token request, naming the target MCP server | client | MUST |
| 5 | **Validate the token audience** — accept only tokens issued *for this server*; reject everything else | server | MUST |
| 6 | **Never pass the inbound token through** to an upstream API; mint a separate upstream token | server | MUST NOT |

[1]: https://modelcontextprotocol.io/specification/draft/basic/authorization

Rules 5 and 6 are where most homegrown servers fail, and they're the two that close confused-deputy and audience-confusion holes (Part 2).

### What changed across spec revisions

The auth story has rewritten itself three times — attendees who read a 2025 tutorial may be implementing the wrong thing.

| Revision | What it established |
|----------|--------------------|
| **2025-03-26** | First auth flow. MCP server *was* the OAuth server; relied on hardcoded `/authorize`, `/token`, `/register` endpoints [[3]][d] |
| **2025-06-18** | The big one: **server reclassified as resource server**, AS split out. Mandated RFC 9728 metadata + RFC 8707 resource indicators; **explicitly forbade token passthrough** [[3]][d] |
| **2025-11-25** | Formalized the resource-server classification; tightened resource-indicator requirements; added Client ID Metadata Documents as the preferred client-registration path [[4]][r] |

[d]: https://www.descope.com/blog/post/mcp-auth-spec
[r]: https://dasroot.net/posts/2026/04/mcp-authorization-specification-oauth-2-1-resource-indicators/

Takeaway to say out loud: **if a tutorial has your MCP server issuing tokens or exposing `/token`, it predates June 2025 — don't follow it** [[3]](https://www.descope.com/blog/post/mcp-auth-spec).

### In the official TypeScript SDK

Concrete so the session lands. With `@modelcontextprotocol/sdk` [[11]](https://github.com/modelcontextprotocol/typescript-sdk) ⭐ 13k (Jun 2026), resource-server mode is roughly [[12]](https://nerdleveltech.com/mcp-server-typescript-oauth-streamable-http-production-tutorial)[[13]](https://ts.sdk.modelcontextprotocol.io/v2/functions/_modelcontextprotocol_express.auth_bearerAuth.requireBearerAuth.html):

- Run `StreamableHTTPServerTransport` behind Express.
- Mount `app.get("/.well-known/oauth-protected-resource", ...)` as an **anonymous** endpoint (RFC 9728).
- Wrap MCP routes in `requireBearerAuth({ verifier })` — it validates the Bearer token via an `OAuthTokenVerifier` and attaches `AuthInfo` to `req.auth`.
- In the verifier, **check the `aud` claim** equals your canonical server URI (don't skip this — the middleware won't do audience binding for you).
- Read `authInfo.scopes` **inside every tool handler** and authorize per-operation; a valid token is not authorization.

`stdio` transport is exempt from the spec — it reads credentials from the environment, so local servers don't do OAuth [[1]](https://modelcontextprotocol.io/specification/draft/basic/authorization).

## Part 2 — The threat landscape

OAuth secures the *transport*. It does nothing about the fact that an LLM reads attacker-influenced text — tool descriptions and tool results — and acts on it. This is the part of the session that earns its slot.

### Threat → mitigation table

| Threat | What happens | Mitigation to teach |
|--------|--------------|---------------------|
| **Tool poisoning** | Hidden instructions in a tool *description* (model sees full text, user sees a summary) tell the agent to read SSH keys / files and exfiltrate them [[5]][il] | Render **full** descriptions to users; pin tools by checksum/version so an approved tool can't silently change; treat descriptions as untrusted [[5]][il] |
| **Shadowing / cross-server hijack** | A malicious server's description rewrites how the agent uses a *trusted* server's tools (e.g. redirect all emails) — attacker tool never appears in the user log [[5]][il] | Isolate servers; dataflow controls between them; don't co-mount untrusted + sensitive servers in one agent [[5]][il] |
| **Prompt injection via tool results** | Returned data (ticket text, web page, DB row) carries instructions the model obeys — e.g. Supabase SQL-injection via a support ticket [[8]][pds] | Sanitize/validate tool *outputs* before they reach the model; mark them as data, not instructions; never run tools with standing high privilege [[8]][pds] |
| **Confused deputy** | Proxy server with a static upstream client ID + dynamic client registration + a consent cookie lets an attacker reuse consent and steal the auth code [[2]][bp] | Per-client consent stored server-side, checked **before** forwarding upstream; exact `redirect_uri` match; single-use `state`; `__Host-` consent cookies [[2]][bp] |
| **Token passthrough / audience confusion** | Server forwards the client's token upstream, or accepts a token minted for another service — bypasses rate limits, breaks audit trail, enables lateral use [[2]][bp] | Validate `aud`; accept only tokens issued for *this* server; mint a **separate** upstream token — never proxy the inbound one [[1]][au][[2]][bp] |
| **Over-broad scopes** | Server publishes every scope in `scopes_supported`; client requests `files:*`, `db:*` up front → huge blast radius on a stolen token [[2]][bp] | Minimal baseline scope (e.g. `mcp:tools-basic`); step-up via `WWW-Authenticate scope="…"` 403 challenges; no wildcard/omnibus scopes [[2]][bp] |
| **Supply chain (3rd-party servers)** | Installing an untrusted server = arbitrary code with client privileges; malicious startup commands, rug-pulls (CVE-2025-54136) [[2]][bp][[15]][tf] | Vet provenance; pin versions/checksums; sandbox local servers (containers, restricted FS/network); one-click installs MUST show the exact command + consent [[2]][bp] |
| **SSRF via discovery** | Malicious server returns `resource_metadata`/AS URLs pointing at `169.254.169.254` or internal hosts; client fetches them, leaks cloud creds [[2]][bp] | Enforce HTTPS; block private/link-local IP ranges; use an egress proxy; pin DNS between check and use [[2]][bp] |
| **Session hijacking** | Guessable session ID lets an attacker impersonate a user or inject events across stateful HTTP servers [[2]][bp] | Non-deterministic session IDs; **never use sessions for auth** — verify every request; bind session to `<user_id>:<session_id>` [[2]][bp] |

[il]: https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks
[pds]: https://www.practical-devsecops.com/mcp-security-vulnerabilities/
[bp]: https://modelcontextprotocol.io/specification/draft/basic/security_best_practices
[au]: https://modelcontextprotocol.io/specification/draft/basic/authorization
[tf]: https://www.truefoundry.com/blog/blog-mcp-tool-poisoning-gateway-defense

### The canonical demo to show

The **WhatsApp exfiltration** (Invariant Labs, April 2025) is the clearest single story: a benign-looking trivia/addition MCP server ships a tool description with hidden instructions; the agent — also connected to a trusted `whatsapp-mcp` server — is steered into reading the full chat history and exfiltrating it through ordinary message traffic, which DLP misses because it leaves via a legitimate channel [[6]](https://invariantlabs.ai/blog/whatsapp-mcp-exploited)[[18]](https://www.docker.com/blog/mcp-horror-stories-whatsapp-data-exfiltration-issue/). Reproducible PoCs are public [[7]](https://github.com/invariantlabs-ai/mcp-injection-experiments) ⭐ 195 (Jun 2026). OWASP now tracks this class as **MCP Tool Poisoning**, an indirect prompt-injection attack [[14]](https://owasp.org/www-community/attacks/MCP_Tool_Poisoning).

### 2026 CVEs worth naming (supply chain is real)

Early 2026 saw ~30 MCP CVEs in 60 days [[16]](https://www.heyuan110.com/posts/ai/2026-03-10-mcp-security-2026/). The ones that make the supply-chain point land:

| CVE | Component | Issue |
|-----|-----------|-------|
| **CVE-2025-49596** (CVSS 9.4) | MCP Inspector < 0.14.1 | No auth between Inspector client and proxy → unauthenticated RCE on a dev machine via a malicious website (0.0.0.0-day + CSRF chain); fixed 0.14.1 [[9]][ol] |
| **CVE-2025-6514** | `mcp-remote` | OS command injection → RCE on client via a malicious `authorization_endpoint` [[10]][az] |
| **CVE-2025-53109/53110** | Anthropic Filesystem MCP | Sandbox escape / symlink bypass → arbitrary file access [[10]][az] |
| **CVE-2025-54136** (MCPoison) | MCP tool config | Approved tool definition silently swapped after trust (rug pull) [[15]][tf] |

[ol]: https://www.oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596
[az]: https://authzed.com/blog/timeline-mcp-breaches
[tf]: https://www.truefoundry.com/blog/blog-mcp-tool-poisoning-gateway-defense

The lesson for attendees: **the tooling around your server (Inspector, `mcp-remote`, third-party servers) is attack surface too** — pin versions, read advisories, sandbox local servers.

## What every session attendee should walk away with

1. Your MCP server is an **OAuth 2.1 resource server** — validate tokens, advertise metadata (RFC 9728), don't issue tokens [[1]](https://modelcontextprotocol.io/specification/draft/basic/authorization).
2. **Validate the audience** (RFC 8707) and **never pass tokens through** — these two close the confused-deputy/audience-confusion class [[1]](https://modelcontextprotocol.io/specification/draft/basic/authorization)[[2]](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices).
3. **Least-privilege scopes**, step-up via 403 challenges, no wildcards [[2]](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices).
4. **Treat tool descriptions and tool results as untrusted input** — this is the OAuth-can't-help layer, and the one your demo should hit [[5]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)[[8]](https://www.practical-devsecops.com/mcp-security-vulnerabilities/).
5. **Sandbox and pin** third-party/local servers; check `authInfo.scopes` in every tool handler [[2]](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)[[12]](https://nerdleveltech.com/mcp-server-typescript-oauth-streamable-http-production-tutorial).
