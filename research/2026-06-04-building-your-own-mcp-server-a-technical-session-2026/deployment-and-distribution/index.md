---
title: "Shipping Your MCP Server: Deployment & Distribution in 2026"
date: 2026-06-04
depth: standard
format: md
topic: "Deployment & distribution of MCP servers (2026) — local stdio vs remote Streamable-HTTP, packaging (npx/uvx/Docker/DXT), the official MCP registry, and client install/config (Claude Desktop, Claude Code, VS Code, Cursor)"
topic_raw: "Deployment and distribution"
tags: [mcp, deployment, distribution, registry, mcpb, claude-code]
summary: "How you actually ship and share the MCP server you built: transport choice, packaging channels, the official registry, and client config."
citations: 16
reading_time_min: 4
---

> **Decision.** Ship a **local stdio** server when one user runs it on their own machine — publish it as an npm/PyPI package (`npx`/`uvx`) or wrap it in a `.mcpb` bundle for one-click Claude Desktop install [[1]](https://www.truefoundry.com/blog/mcp-stdio-vs-streamable-http-enterprise)[[7]](https://github.com/modelcontextprotocol/mcpb). Go **remote Streamable-HTTP** the moment many users share one instance or you need auth, audit, and horizontal scale — host it on Cloudflare Workers, a container, or a serverless platform [[1]](https://www.truefoundry.com/blog/mcp-stdio-vs-streamable-http-enterprise)[[2]](https://developers.cloudflare.com/agents/guides/remote-mcp-server/). For discovery, publish `server.json` to the **official MCP Registry** [[4]](https://modelcontextprotocol.io/registry/about) — but it only stores metadata pointing at npm/PyPI/NuGet/Docker; your code still lives in a package registry.

## Transport: where the server runs

Transport is the first deployment decision because it dictates everything downstream (hosting, auth, packaging).

| Axis              | stdio (local)                                  | Streamable HTTP (remote)                                |
| ----------------- | ---------------------------------------------- | ------------------------------------------------------- |
| Where it runs     | Subprocess on the client's machine             | A web service reachable over the network                |
| Process model     | One process per user — 50 devs × 8 servers ≈ 400 processes [[1]][1] | One process serves many clients concurrently [[1]][1] |
| Single-call latency | ~0.3–1 ms warm (p95 ~2–3 ms) [[1]][1]        | ~5–10 ms same-DC (p95 ~15–25 ms) [[1]][1]               |
| Auth              | None at transport layer (env vars only) [[1]][1] | `Authorization` header, OAuth 2.1 + PKCE [[1]][1][[2]][2] |
| Best for          | Local dev, single-user desktop tools [[3]][3]  | Team sharing, SaaS, identity/audit/RBAC/scale [[1]][1]  |

[1]: https://www.truefoundry.com/blog/mcp-stdio-vs-streamable-http-enterprise
[2]: https://developers.cloudflare.com/agents/guides/remote-mcp-server/
[3]: https://www.red-gate.com/simple-talk/ai/local-vs-remote-mcp-servers-which-should-you-choose/

Streamable HTTP (MCP spec 2025-03-26) is JSON-RPC 2.0 over a single HTTP endpoint supporting POST and GET, with optional Server-Sent Events for streaming — it replaces the deprecated HTTP+SSE transport [[3]](https://www.red-gate.com/simple-talk/ai/local-vs-remote-mcp-servers-which-should-you-choose/). The migration from stdio is mechanical: with the TypeScript SDK you swap the stdio adapter for the HTTP server adapter; tools and handlers are unchanged [[2]](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)[[1]](https://www.truefoundry.com/blog/mcp-stdio-vs-streamable-http-enterprise). The 5–10 ms HTTP overhead is rarely the dominant cost against an LLM call, so don't pick stdio for latency alone [[1]](https://www.truefoundry.com/blog/mcp-stdio-vs-streamable-http-enterprise).

### Hosting a remote server

| Option                              | Notes                                                                                  |
| ----------------------------------- | -------------------------------------------------------------------------------------- |
| [Cloudflare Workers][cf] ⭐ 3.8k     | Official template; ~0ms cold start, global edge, free tier 100K req/day; OAuth built-in [[2]][cf2][[5]][cf5] |
| Vercel / serverless functions       | Free tier; good fit if you already deploy there [[5]][cf5]                              |
| FastMCP Cloud / mcphosting.io       | Managed MCP-specific hosting, free personal tiers [[5]][cf5]                            |
| Your own container (Docker)         | Run the HTTP server behind a load balancer; full control, you own auth/scale [[6]][cf6] |

[cf]: https://github.com/cloudflare/mcp-server-cloudflare
[cf2]: https://developers.cloudflare.com/agents/guides/remote-mcp-server/
[cf5]: https://mcpplaygroundonline.com/blog/free-mcp-server-hosting-cloudflare-vercel-guide
[cf6]: https://apigene.ai/blog/host-mcp-server

For public servers you can skip auth entirely; for private ones add an `X-API-Key` header or implement OAuth 2.1 with PKCE (the MCP spec standard) [[2]](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)[[5]](https://mcpplaygroundonline.com/blog/free-mcp-server-hosting-cloudflare-vercel-guide).

## Packaging & distribution channels

A local server gets distributed as a runnable package; a remote server gets distributed as a URL. The channels:

| Channel              | How users run it                | Best for                                   | One-click? |
| -------------------- | ------------------------------- | ------------------------------------------ | ---------- |
| **npm** (`npx`)      | `npx -y your-mcp-server`        | Node/TypeScript SDK servers [[10]][n10]    | ✗ (config) |
| **PyPI** (`uvx`)     | `uvx your-mcp-server`           | Python servers [[10]][n10]                 | ✗ (config) |
| **Docker / OCI**     | `docker run your/mcp-image`     | Pinned deps, isolation, CI/CD [[4]][n4]    | ✗ (config) |
| **`.mcpb` bundle**   | Double-click → Install [[7]][n7] | End users on Claude Desktop, no runtime needed | ✓        |
| **Remote URL**       | Paste `https://…/mcp` into client | SaaS, zero-install, shared instance [[2]][n2] | ~ (deeplink) |

[n2]: https://developers.cloudflare.com/agents/guides/remote-mcp-server/
[n4]: https://modelcontextprotocol.io/registry/about
[n7]: https://github.com/modelcontextprotocol/mcpb
[n10]: https://code.visualstudio.com/docs/agent-customization/mcp-servers

`npx -y` and `uvx` are the default distribution for SDK-built servers: ship the package to npm/PyPI and the client's config just references the command. The registry's supported package types map directly to npm, PyPI, NuGet, and Docker Hub [[4]](https://modelcontextprotocol.io/registry/about).

### DXT / `.mcpb` — one-click desktop install

[Desktop Extensions][mcpb] ⭐ 1.9k bundle an entire local MCP server — including all dependencies — into a single installable package, "spiritually similar to Chrome extensions (.crx) or VS Code extensions (.vsix)" [[7]](https://github.com/modelcontextprotocol/mcpb). Note the **rename**: the format moved from `.dxt` to `.mcpb` (MCP Bundle); existing `.dxt` files still work but use `.mcpb` for new extensions [[8]](https://www.anthropic.com/engineering/desktop-extensions).

[mcpb]: https://github.com/modelcontextprotocol/mcpb

A `.mcpb` is a zip archive containing the server plus a `manifest.json` — the only required file — declaring name, tools/prompts, user configuration, and runtime requirements [[8]](https://www.anthropic.com/engineering/desktop-extensions). It eliminates the usual friction: Claude Desktop **bundles Node.js**, so users need no developer tools, and sensitive config like API keys is stored in the **OS keychain** [[8]](https://www.anthropic.com/engineering/desktop-extensions). Build it with the CLI [[9]](https://www.npmjs.com/package/@anthropic-ai/mcpb):

```bash
npm install -g @anthropic-ai/mcpb
mcpb init    # scaffold manifest.json
mcpb pack    # produce the .mcpb file
```

## Publishing to the official MCP Registry

The [official MCP Registry][reg] ⭐ 6.9k is the official centralized **metadata** repository for publicly accessible servers, backed by Anthropic, GitHub, PulseMCP, and Microsoft [[4]](https://modelcontextprotocol.io/registry/about). It is an "app store for MCP servers" but hosts **metadata only, not code** [[12]](https://github.com/modelcontextprotocol/registry) — package registries (npm, PyPI, Docker Hub) host the binaries; the registry maps a server name + version to e.g. `npm:weather-mcp` [[4]](https://modelcontextprotocol.io/registry/about). It is still **in preview** (API freeze v0.1, GA pending) and is designed to be consumed by downstream aggregators/marketplaces — not directly by host apps [[4]](https://modelcontextprotocol.io/registry/about).

[reg]: https://github.com/modelcontextprotocol/registry

Server names use **reverse-DNS namespaces** tied to verified GitHub accounts or domains, so only the legitimate owner can publish under `io.github.<username>/*` [[4]](https://modelcontextprotocol.io/registry/about). The publish flow [[11]](https://learn.microsoft.com/en-us/dotnet/ai/quickstarts/publish-mcp-registry):

1. Write a `server.json` (`name`, `version`, `packages[]` with `registryType` + `transport`, `repository`).
2. Reference the name in your package README as `<!-- mcp-name: io.github.you/server -->` so the registry can verify ownership.
3. Publish the package to npm/PyPI/NuGet/Docker.
4. Authenticate and publish the metadata:

```bash
./mcp-publisher login github          # browser code flow → unlocks io.github.<you>/*
./mcp-publisher publish .mcp/server.json
```

The registry **does not support private servers** (private networks or private package registries) — self-host your own registry implementing the OpenAPI spec for those [[4]](https://modelcontextprotocol.io/registry/about). The [GitHub MCP Registry][ghreg] will soon source its listings from the official registry [[11]](https://learn.microsoft.com/en-us/dotnet/ai/quickstarts/publish-mcp-registry).

[ghreg]: https://github.com/mcp

## Installing into clients

Every client speaks the same protocol, so a package is interchangeable — but each has its own config file and command [[13]](https://buildtolaunch.substack.com/p/mcp-setup-claude-chatgpt-vscode-cursor).

| Client             | Config file / command                                  | stdio example                                    | remote example                            |
| ------------------ | ------------------------------------------------------ | ------------------------------------------------ | ----------------------------------------- |
| **Claude Desktop** | `.mcpb` install, or `claude_desktop_config.json` [[8]][c8] | manifest-driven, no JSON edit                  | — (use `.mcpb` / connectors)              |
| **Claude Code**    | `claude mcp add` → `.mcp.json` / `~/.claude.json` [[14]][c14] | `claude mcp add --transport stdio fs -- npx -y @some/mcp` | `claude mcp add --transport http notion https://mcp.notion.com/mcp` |
| **VS Code**        | `.vscode/mcp.json` or `code --add-mcp` [[10]][c10]     | `{"command":"npx","args":["-y","@.../server"]}`  | `{"type":"http","url":"https://…/mcp"}`   |
| **Cursor**         | `.cursor/mcp.json` or "Add to Cursor" deeplink [[15]][c15][[16]][c16] | `mcpServers` block with command/args      | base64 deeplink: `cursor://anysphere.cursor-deeplink/mcp/install?name=…&config=…` |

[c8]: https://www.anthropic.com/engineering/desktop-extensions
[c10]: https://code.visualstudio.com/docs/agent-customization/mcp-servers
[c14]: https://code.claude.com/docs/en/mcp
[c15]: https://cursor.com/docs/context/mcp/install-links
[c16]: https://danywalls.com/create-one-click-mcp-installation-links-cursor-vscode

Notes for distributors:
- **Scope = sharing.** In Claude Code, `--scope project` writes `.mcp.json` at the repo root; commit it and every teammate's machine gets the same config [[14]](https://code.claude.com/docs/en/mcp). VS Code's `.vscode/mcp.json` and Cursor's `.cursor/mcp.json` work the same way [[10]](https://code.visualstudio.com/docs/agent-customization/mcp-servers)[[15]](https://cursor.com/docs/context/mcp/install-links).
- **Deeplinks** are the closest thing to one-click for editors: ship an "Add to Cursor"/"Install in VS Code" button that encodes the server config so users skip JSON editing [[16]](https://danywalls.com/create-one-click-mcp-installation-links-cursor-vscode).
- **SSE is deprecated** as of early 2026 — emit HTTP config, not SSE, for new servers [[14]](https://code.claude.com/docs/en/mcp).
- **Never hardcode secrets** in shared config; use input variables / env files [[10]](https://code.visualstudio.com/docs/agent-customization/mcp-servers).

## Practical recommendation

Build once with the TypeScript SDK ([repo][sdk] ⭐ 12.6k), then pick channels by audience: publish the npm package (works in every editor via `npx`), wrap a `.mcpb` for non-technical Claude Desktop users, and — when you outgrow per-user processes — stand up a Streamable-HTTP instance and hand out a URL plus an "Add to Cursor" deeplink. List `server.json` in the official registry so aggregators surface you [[4]](https://modelcontextprotocol.io/registry/about).

[sdk]: https://github.com/modelcontextprotocol/typescript-sdk
