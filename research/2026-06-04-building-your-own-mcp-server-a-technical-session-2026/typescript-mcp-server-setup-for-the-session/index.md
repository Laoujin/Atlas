---
title: "TypeScript MCP Server: Session Quickstart + SDK Comparison"
date: 2026-06-04
depth: ceo
format: md
topic: "TypeScript MCP server setup for the session — quickstart using the official @modelcontextprotocol/sdk: minimal layout, one tool, stdio, MCP Inspector, pre-installs; plus TS vs Python vs C# SDK comparison and Java SDK maturity"
topic_raw: "TypeScript MCP server setup for the session"
tags: [mcp, typescript, sdk, quickstart, tooling]
summary: "One-page quickstart for a TypeScript MCP server over stdio with MCP Inspector, plus a TS/Python/C# SDK comparison and the Java SDK maturity line."
citations: 7
reading_time_min: 2
model: "Opus 4.8"
duration_sec: 80
cost_usd: "sub"
cover: cover.svg
---

> **Decision:** TypeScript **is** the lowest-friction live-follow for a mixed Java/.NET room. It is one of two Tier-1 official SDKs (~66M npm downloads), zero-install beyond Node, and MCP Inspector ships as a single `npx` command [[1]](https://modelcontextprotocol.io/docs/sdk) [[6]](https://github.com/modelcontextprotocol/inspector). Python ties it on maturity but adds a venv/`uv` step; C# is official and excellent but needs the .NET SDK + project scaffolding. Follow in TS, port after.

## Pre-install (tell attendees before the session)

| Need              | Version / command                              |
|-------------------|------------------------------------------------|
| Node.js           | **≥ 22.7.5** (Inspector requires it; SDK needs ≥20) [[6]](https://github.com/modelcontextprotocol/inspector) |
| Package manager   | npm (bundled) — no global installs needed      |
| Editor            | any; VS Code for inline TS types               |

## Minimal project

```bash
mkdir my-mcp && cd my-mcp && npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D @types/node typescript
```

`package.json`: add `"type": "module"` and `"scripts": { "build": "tsc" }`. `tsconfig.json`: `target` ES2022, `module`/`moduleResolution` Node16, `outDir` `./build`, `rootDir` `./src`, `strict: true` [[2]](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server-quickstart.md).

## One tool over stdio — `src/index.ts`

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "demo", version: "1.0.0" });

server.registerTool(
  "add",
  {
    title: "Add",
    description: "Add two numbers",
    inputSchema: { a: z.number(), b: z.number() },
  },
  async ({ a, b }) => ({
    content: [{ type: "text", text: String(a + b) }],
  }),
);

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("MCP server on stdio"); // ⚠ stdout carries JSON-RPC — log only to stderr
```

The stdout/stderr rule is the #1 live gotcha: any `console.log` corrupts the JSON-RPC stream and silently breaks the server [[3]](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server.md) [[2]](https://github.com/modelcontextprotocol/typescript-sdk/blob/main/docs/server-quickstart.md).

## Wire up MCP Inspector

```bash
npm run build
npx @modelcontextprotocol/inspector node build/index.js
```

UI opens at `http://localhost:6274` (proxy on `6277`); the Tools tab lists `add`, lets you fill `a`/`b` and see the response — no LLM needed [[4]](https://modelcontextprotocol.io/docs/tools/inspector) [[6]](https://github.com/modelcontextprotocol/inspector). This is the demo loop: edit tool → `npm run build` → reconnect in Inspector.

## Official SDK comparison

| SDK     | Status                    | ⭐ Stars | Live-follow friction                         |
|---------|---------------------------|---------|----------------------------------------------|
| [TypeScript][ts] | Tier-1 official    | ⭐ 12.6k | Lowest — `npm i`, run `node`, Inspector via `npx` [[1]][s] |
| [Python][py]     | Tier-1 official    | ⭐ 23.2k | Equal maturity; +venv/`uv` setup step [[1]][s] |
| [C#][cs]         | Official (Microsoft+Anthropic), v1.2 | ⭐ 4.3k | More scaffolding: .NET SDK + host builder [[5]][ms] |

[ts]: https://github.com/modelcontextprotocol/typescript-sdk
[py]: https://github.com/modelcontextprotocol/python-sdk
[cs]: https://github.com/modelcontextprotocol/csharp-sdk
[s]: https://modelcontextprotocol.io/docs/sdk
[ms]: https://developer.microsoft.com/blog/microsoft-partners-with-anthropic-to-create-official-c-sdk-for-model-context-protocol

Stars are similar size signals; all three are official and feature-complete (tools, resources, prompts, stdio + Streamable HTTP) [[1]](https://modelcontextprotocol.io/docs/sdk).

## For the Java attendees

The [official Java SDK](https://github.com/modelcontextprotocol/java-sdk) ⭐ 3.5k (Jun 2026) is **mature and production-ready**: 1.0.0 GA, maintained with Spring AI, compliant with the 2025-06-18 spec (tools/resources/prompts/sampling/elicitation, STDIO + Streamable HTTP), with Spring Boot client/server starters [[7]](https://github.com/modelcontextprotocol/java-sdk).
