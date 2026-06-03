---
title: "Debugging MCP servers: Inspector, stderr logging, and the failure modes that kill stdio"
date: 2026-06-04
depth: standard
format: md
topic: "Debugging MCP servers — a hands-on walkthrough: official MCP Inspector, structured logging/stderr for stdio servers, inspecting stdio vs Streamable-HTTP traffic, common failure modes (handshake/init, JSON-schema mismatch, transport framing, stdout pollution), and testing against Claude Desktop, Claude Code, VS Code, Cursor"
topic_raw: "Debugging MCP servers"
tags: [mcp, debugging, mcp-inspector, stdio, streamable-http, typescript-sdk]
summary: "The Inspector is your first stop, stdout pollution is the #1 killer, and stderr is the only safe log channel for stdio servers."
citations: 12
reading_time_min: 6
model: "Opus 4.8"
duration_sec: 225
cost_usd: "sub"
cover: cover.svg
---

> **Decision.** Reach for the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) ⭐ 9.9k (Jun 2026) first — it's transport-agnostic and shows the raw JSON-RPC stream [[1]](https://modelcontextprotocol.io/docs/tools/debugging). The single most common bug is **stdout pollution**: any `console.log`/`print` on a stdio server corrupts the protocol and kills the connection — log to **stderr** only, always [[2]](https://modelcontextprotocol.io/docs/tools/debugging)[[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices). After the Inspector passes, smoke-test against the real clients (Claude Desktop, Claude Code, VS Code, Cursor) because each has its own config schema and log location [[4]](https://code.claude.com/docs/en/mcp).

## 1. MCP Inspector — what it is and how to launch

The Inspector is an interactive, transport-agnostic testing UI. It's two processes: a React web UI (MCPI) and a Node proxy (MCPP) that bridges the browser to your server over stdio, SSE, or Streamable HTTP [[5]](https://www.augmentcode.com/mcp/mcp-inspector). Runs straight from `npx`, no install [[6]](https://modelcontextprotocol.io/docs/tools/inspector):

```bash
# Your locally-built TypeScript server (stdio)
npx @modelcontextprotocol/inspector node build/index.js

# An npm-published server with args
npx -y @modelcontextprotocol/inspector npx @modelcontextprotocol/server-filesystem /Users/me/Desktop

# A remote Streamable-HTTP server
npx @modelcontextprotocol/inspector --cli https://my-mcp-server.example.com
```

Default ports: UI on **6274**, proxy on **6277** (override with `CLIENT_PORT` / `SERVER_PORT`) [[5]](https://www.augmentcode.com/mcp/mcp-inspector). The proxy generates a **random session bearer token** at startup and prints it; the launch URL embeds it. `DANGEROUSLY_OMIT_AUTH=true` disables it (don't) [[5]](https://www.augmentcode.com/mcp/mcp-inspector).

**The panes** [[6]](https://modelcontextprotocol.io/docs/tools/inspector):

| Pane | Use it to |
|------------------|----------------------------------------------------------------|
| Server connection | Pick transport; edit command-line args + `env` for local servers |
| Tools tab        | List tools, view input schemas, call with custom args, see results |
| Resources tab    | List resources + MIME/metadata, inspect content, test subscriptions |
| Prompts tab      | List prompt templates, view args, preview generated messages    |
| Notifications    | Watch server logs + notifications (your `notifications/message` stream lands here) |

Note the boundary: the Notifications pane shows **JSON-RPC protocol messages**, not your raw `console.log` — on stdio, stdout belongs to the protocol [[7]](https://apigene.ai/blog/how-to-test-mcp-server).

### CLI mode (CI / scripting)

Add `--cli` to skip the browser and drive the server from the shell — ideal for protocol-compliance checks in CI [[6]](https://modelcontextprotocol.io/docs/tools/inspector):

```bash
npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list
npx @modelcontextprotocol/inspector --cli node build/index.js \
  --method tools/call --tool-name search --tool-arg query=mcp
npx @modelcontextprotocol/inspector --cli node build/index.js --method resources/list
```

Python devs: `mcp dev server.py` runs the script under the Inspector automatically [[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices).

## 2. Logging: stderr is the only safe channel for stdio

For stdio servers, **everything logged to stderr is captured by the host automatically** [[2]](https://modelcontextprotocol.io/docs/tools/debugging). stdout is reserved for JSON-RPC framing — anything else corrupts the stream. In the TypeScript SDK that means `console.error(...)`, never `console.log(...)` (Python: `print(..., file=sys.stderr)`) [[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices).

For **structured logs the client can render on any transport**, send a log-message notification instead of writing to a stream [[2]](https://modelcontextprotocol.io/docs/tools/debugging):

```typescript
await server.sendLoggingMessage({ level: "info", data: "Server started successfully" });
```

MCP defines eight RFC 5424 severity levels (`debug`→`emergency`); clients set the minimum at runtime via `logging/setLevel` [[2]](https://modelcontextprotocol.io/docs/tools/debugging). Prefix each line with server name + tool/method + request ID so the Notifications pane stays parseable, e.g. `[ServerName] [tool] context: message` [[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices).

Note the asymmetry: under **Streamable HTTP, stderr is NOT captured by the client**. Use log notifications, your own server-side aggregation, or HTTP tooling (curl, DevTools Network panel) to inspect requests, `Mcp-Session-Id` headers, and SSE streams [[2]](https://modelcontextprotocol.io/docs/tools/debugging).

## 3. Inspecting traffic: stdio vs Streamable HTTP

**stdio** — the Inspector proxy is the cleanest window; it surfaces the framed JSON-RPC both ways. A healthy startup sequence: `initialize` → `notifications/initialized` → `tools/list` → `resources/list` → `prompts/list` (a server that doesn't implement resources answering with a graceful `-32601 Method not found` is normal) [[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices).

**Streamable HTTP** — reproduce exactly what a client sends with curl. It's a stateful session: `initialize` first, capture the `Mcp-Session-Id` header, replay it on every subsequent call [[8]](https://glama.ai/blog/2026-01-02-how-to-test-mcp-streamable-http-endpoints-using-c-url):

```bash
curl -s -D - -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"curl-test","version":"1.0.0"}},"id":1}' \
  "$MCP_ENDPOINT"
# grep the response headers for mcp-session-id (case-insensitive), then:
#   POST follow-ups carry  -H "Mcp-Session-Id: $SESSION_ID"  and return immediate JSON
#   a GET opens a long-lived SSE stream; DELETE terminates the session
```

The dual `Accept: application/json, text/event-stream` header is mandatory — a server may answer either inline JSON or an SSE event, and omitting one half is a common 406 [[8]](https://glama.ai/blog/2026-01-02-how-to-test-mcp-streamable-http-endpoints-using-c-url).

## 4. The failure modes that actually bite

| Failure | What you see | Root cause | Fix |
|--------------------------|--------------------------------|-----------------------------------------------|---------------------------------------------|
| **stdout pollution**     | `Unexpected token` / `Invalid JSON`; `-32000` connection closed | `console.log`/`print`/banner on stdout corrupts the JSON-RPC stream — ~43% of `-32000` cases [[9]](https://mcpplaygroundonline.com/blog/mcp-server-troubleshooting-common-errors-fix) | Move every log to stderr (`console.error`); silence chatty deps [[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices) |
| **Transport framing**    | Handshake fails, `Parse error: invalid JSON` | Server emits newline-delimited JSON while the client expects Content-Length framing (or you hand-rolled the transport) | Use the SDK's stdio transport; don't write your own framing [[10]](https://github.com/colbymchenry/codegraph/issues/172) |
| **Handshake / init**     | Connection drops right after `initialize` | `protocolVersion` (YYYY-MM-DD) mismatch, or server crashed before completing the handshake | Diff the `initialize` request/response; bump the SDK; manually run the command to catch import errors [[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices) |
| **Capability mismatch**  | `-32602 Invalid params` | Server sends a `sampling`/`elicitation` request to a client that never declared that capability | Inspect the `initialize` exchange; only use capabilities both sides negotiated [[2]](https://modelcontextprotocol.io/docs/tools/debugging) |
| **JSON-schema mismatch** | Tool silently fails / vanishes in the host UI | Wrong field names or missing properties → host silently rejects the response; or wrong arg types (`-32602`) | Validate output against the spec schema; match handler types to the tool's input schema [[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices) |
| **Config schema drift**  | Whole server entry ignored, no error | Unrecognized field (`"type":"stdio"` in a client that doesn't accept it) makes the client drop the entry | Match each client's exact config schema (see §5) [[9]](https://mcpplaygroundonline.com/blog/mcp-server-troubleshooting-common-errors-fix) |
| **Working dir / paths**  | `ENOENT`, missing files, spawn fails | stdio servers launched by a client get an undefined cwd (`/` on macOS) | Use absolute paths in config and `.env`; pass an absolute `command` [[2]](https://modelcontextprotocol.io/docs/tools/debugging) |
| **Missing env vars**     | Auth/credential errors at startup | stdio servers inherit only a limited, platform-dependent env subset | Set them explicitly in the config's `env` block [[2]](https://modelcontextprotocol.io/docs/tools/debugging) |
| **Request timeout**      | `-32001` after ~60s | Hanging external API call, deadlock, or DNS failure in a tool handler | Add explicit timeouts to every outbound call in handlers [[9]](https://mcpplaygroundonline.com/blog/mcp-server-troubleshooting-common-errors-fix) |
| **Unhandled exception**  | `-32603 Internal error` | Tool handler threw, nothing caught it | Wrap handlers in try/catch; return a structured `McpError` [[3]](https://www.mcpevals.io/blog/debugging-mcp-servers-tips-and-best-practices) |

`-32000`/`-32700`/`-32601`/`-32602`/`-32603` are standard JSON-RPC codes; `-32602 Invalid params` shows up in many contexts, so always read the `initialize` exchange before guessing [[2]](https://modelcontextprotocol.io/docs/tools/debugging).

## 5. Testing against the real clients

The Inspector proves protocol-correctness; real clients prove integration. Each has a different config schema, log location, and reload behavior [[4]](https://code.claude.com/docs/en/mcp).

**Claude Desktop** — `claude_desktop_config.json`, key is `mcpServers`. Code changes need a **full quit + reopen** (closing the window isn't enough). Logs: `~/Library/Logs/Claude` (macOS) / `%APPDATA%\Claude\logs` (Windows) — `tail -F ~/Library/Logs/Claude/mcp*.log`. Enable Chrome DevTools via `developer_settings.json` `{"allowDevTools": true}` to inspect client-side payloads in the Network panel [[2]](https://modelcontextprotocol.io/docs/tools/debugging).

**Claude Code** — add over the CLI; all flags go before the name, `--` separates Claude's flags from the server command [[4]](https://code.claude.com/docs/en/mcp):

```bash
claude mcp add --transport stdio --env API_KEY=xxx myserver -- node build/index.js
claude mcp list          # ⏸ Pending approval for project-scoped .mcp.json servers
claude mcp get myserver
# inside Claude Code:  /mcp   → tool count per server; flags servers that advertise
#                              the tools capability but expose zero tools
```

Scopes: `local` (default, `~/.claude.json`), `project` (`.mcp.json`, version-controlled, needs approval), `user` (all projects). Set startup timeout with `MCP_TIMEOUT=10000 claude`. Note stdio servers are **not** auto-reconnected (only HTTP/SSE are) [[4]](https://code.claude.com/docs/en/mcp).

**VS Code** — `.vscode/mcp.json`, top-level key is `servers` (not `mcpServers` — a frequent copy-paste trap). It supports a **dev mode** that few other clients do: a `dev.watch` glob restarts the server on file changes, and `dev.debug` attaches a debugger (Node + Python stdio only) for real breakpoints [[11]](https://code.visualstudio.com/docs/agents/reference/mcp-configuration):

```json
{
  "servers": {
    "myserver": {
      "command": "node",
      "args": ["build/index.js"],
      "dev": { "watch": "src/**/*.ts", "debug": { "type": "node" } }
    }
  }
}
```

Logs: `MCP: List Servers` → pick the server → `Show Output`, or `Show Output` from the Chat error notification. VS Code (re)starts the server whenever you add or change its config [[11]](https://code.visualstudio.com/docs/agents/reference/mcp-configuration).

**Cursor** — Settings → Tools & Integrations → New MCP Server; config uses the `mcpServers` key like Claude Desktop, not VS Code's `servers` — this schema difference is the most common cross-client breakage [[12]](https://dev.to/darkmavis1980/understanding-mcp-servers-across-different-platforms-claude-desktop-vs-vs-code-vs-cursor-4opk).

**Shortcut:** `claude mcp add-from-claude-desktop` imports Desktop's servers into Claude Code (macOS/WSL), saving a re-entry round when smoke-testing the same server across both [[4]](https://code.claude.com/docs/en/mcp).

---

scout: SDK reference — official TypeScript SDK is [`@modelcontextprotocol/typescript-sdk`](https://github.com/modelcontextprotocol/typescript-sdk) ⭐ 12.6k (Jun 2026); the spec repo is [`modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) ⭐ 8.3k.
