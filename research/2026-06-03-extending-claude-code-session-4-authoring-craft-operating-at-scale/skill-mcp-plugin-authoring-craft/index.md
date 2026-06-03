---
title: "Skill / MCP / Plugin Authoring Craft"
date: 2026-06-03
depth: standard
format: md
topic: "Skill / MCP / plugin authoring craft"
topic_raw: "Skill / MCP / plugin authoring craft"
issue: 181
tags: [mcp, agent-skills, plugins, claude-code, ai-agents, developer-tools, security]
summary: "Expert guide to authoring Agent Skills, MCP servers, and Claude Code plugins: format specs, craft rules, security contracts, and the decision matrix between all three."
citations: 18
reading_time_min: 9
cover: cover.svg
model: "Sonnet 4.6"
---

> **TL;DR** Write a skill when you own the words (repeated instructions, project workflows); write an MCP server when you own the tools (external APIs, databases, filesystems); wrap both in a plugin when you need to ship. These are three different interface contracts — conflating them is the root cause of most authoring errors.

## The authoring landscape

Three distinct extension contracts coexist in 2026 AI agent tooling:

| Layer          | What it is                                      | Author                | Interface              |
| :------------- | :---------------------------------------------- | :-------------------- | :--------------------- |
| **Skill**      | Markdown instructions + optional scripts        | Prompt/workflow author | Natural-language activation or `/slash` |
| **MCP server** | JSON-RPC service exposing tools/resources/prompts | Developer            | stdio or Streamable HTTP |
| **Plugin**     | Bundle of skills + agents + hooks + MCP config  | Developer             | `/plugin install` marketplace |

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard [[1]](https://agentskills.io/specification), now implemented by 35+ tools including Cursor, GitHub Copilot, JetBrains Junie, Gemini CLI, and OpenAI Codex [[1]](https://agentskills.io/specification). MCP is an Anthropic-originated JSON-RPC protocol [[2]](https://modelcontextprotocol.io/specification/2025-11-25) with 10,000+ community servers as of mid-2026 [[3]](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026). Plugins are Claude Code's distribution wrapper for all three [[4]](https://code.claude.com/docs/en/plugins.md).

---

## Part 1 — Agent Skills

### Directory layout

A skill is a folder containing one required file [[1]](https://agentskills.io/specification):

```text
my-skill/
├── SKILL.md          # required
├── scripts/          # executable helpers
├── references/       # docs loaded on demand
└── assets/           # templates, data files
```

The folder name becomes the slash command (`/my-skill`). The frontmatter `name` field is a display label only — it does not change what you type, **except** for a plugin-root `SKILL.md` where no folder name exists [[5]](https://code.claude.com/docs/en/skills).

### Frontmatter spec

The Agent Skills standard defines [[1]](https://agentskills.io/specification):

| Field           | Required | Constraint                                                                  |
| :-------------- | :------- | :-------------------------------------------------------------------------- |
| `name`          | Yes      | 1–64 chars, lowercase + hyphens, must match parent dir name                 |
| `description`   | Yes      | 1–1024 chars; **the activation signal** — write it like an API docstring    |
| `license`       | No       | License name or bundled file reference                                      |
| `compatibility` | No       | Environment requirements (packages, tools, network)                         |
| `metadata`      | No       | Arbitrary key-value map                                                     |
| `allowed-tools` | No       | Space-separated pre-approved tool names (experimental)                      |

Claude Code extends the standard with [[5]](https://code.claude.com/docs/en/skills):

| Field                      | Purpose                                                                                     |
| :------------------------- | :------------------------------------------------------------------------------------------ |
| `when_to_use`              | Extra activation hints; appended to `description` in context listing                       |
| `argument-hint`            | Shown in autocomplete: `[issue-number]` or `[filename] [format]`                           |
| `arguments`                | Named positional args for `$name` substitution                                              |
| `disable-model-invocation` | `true` → user-only; removes skill from Claude's context entirely                            |
| `user-invocable`           | `false` → hides from `/` menu; Claude-only activation                                      |
| `disallowed-tools`         | Blocked tools while skill active; clears on next user message                               |
| `model`                    | Model override for this turn (reverts on next prompt)                                       |
| `effort`                   | `low` / `medium` / `high` / `xhigh` / `max` override                                       |
| `context`                  | `fork` → run in isolated subagent                                                           |
| `agent`                    | Which subagent type to use with `context: fork`                                             |
| `paths`                    | Glob patterns; skill auto-activates only when working with matching files                   |
| `hooks`                    | Lifecycle hooks scoped to this skill                                                        |
| `shell`                    | `bash` (default) or `powershell` for `!` blocks                                             |

### Invocation matrix

| Frontmatter                      | User `/cmd` | Claude auto-invoke | In Claude's context listing     |
| :------------------------------- | :---------- | :----------------- | :------------------------------ |
| (default)                        | ✓           | ✓                  | name + description              |
| `disable-model-invocation: true` | ✓           | ✗                  | hidden from Claude              |
| `user-invocable: false`          | ✗           | ✓                  | name + description              |

Use `disable-model-invocation: true` for anything with side effects (deploy, commit, send-slack). Use `user-invocable: false` for ambient knowledge skills that shouldn't appear as slash commands [[5]](https://code.claude.com/docs/en/skills).

### Dynamic context injection

The `` !`cmd` `` syntax runs shell commands *before* the skill reaches Claude — output is inlined in place [[5]](https://code.claude.com/docs/en/skills):

```yaml
---
name: summarize-changes
description: Summarize uncommitted changes and flag risks. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current diff
!`git diff HEAD`

Summarize the changes above in 2-3 bullets, then list risks (missing error handling, hardcoded values, missing tests).
```

Multi-line variant: fenced block opened with ` ```! `. Rules: injection runs once, does not re-scan output, and `!` must appear at line start or after whitespace — `KEY=!cmd` is left as literal text. Use `${CLAUDE_SKILL_DIR}` to reference bundled scripts portably [[5]](https://code.claude.com/docs/en/skills).

### Subagent forking

Add `context: fork` to run the skill in an isolated context. The rendered `SKILL.md` becomes the subagent's prompt; it has no access to conversation history [[5]](https://code.claude.com/docs/en/skills):

```yaml
---
name: pr-summary
description: Summarize a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## PR context
- Diff: !`gh pr diff`
- Comments: !`gh pr view --comments`
- Files: !`gh pr diff --name-only`

Summarize this PR in 3 bullets: what changed, why, and any risks.
```

`context: fork` only makes sense for explicit task skills. A skill that contains only guidelines has no actionable task — the forked subagent receives the guidelines and exits without output.

### Craft rules

1. **Description is the activation switch.** It's truncated at 1,536 chars in context; put the key use case and trigger phrases first. The agent matches descriptions to messages semantically — keyword density matters [[5]](https://code.claude.com/docs/en/skills).
2. **Keep `SKILL.md` under 500 lines.** The full body stays in context for every subsequent turn after activation. Move reference material to `references/*.md` and link from `SKILL.md` [[1]](https://agentskills.io/specification).
3. **State, don't narrate.** "Summarize in 2-3 bullets" beats "When the user asks about their changes, provide a helpful summary that highlights…"
4. **Progressive disclosure.** Agents load: (1) name + description (~100 tokens at startup), (2) full `SKILL.md` on activation (~<5000 tokens recommended), (3) supporting files on demand. Structure content at each layer [[1]](https://agentskills.io/specification).

### Scoping

| Location   | Scope            | Path                                      |
| :--------- | :--------------- | :---------------------------------------- |
| Enterprise | All org users    | Managed settings                          |
| Personal   | All your projects | `~/.claude/skills/<name>/SKILL.md`       |
| Project    | This repo        | `.claude/skills/<name>/SKILL.md`          |
| Plugin     | Where plugin enabled | `<plugin>/skills/<name>/SKILL.md`     |

Plugin skills are namespaced (`/my-plugin:hello`) — no collision with standalone skills. Project skills require workspace trust before `allowed-tools` takes effect [[5]](https://code.claude.com/docs/en/skills).

---

## Part 2 — MCP Server Authoring

### The three primitives

MCP converts n×m integrations into n+m by standardising three primitive types [[2]](https://modelcontextprotocol.io/specification/2025-11-25):

| Primitive    | Consumer        | Semantics                                   | Mutable |
| :----------- | :-------------- | :------------------------------------------ | :------ |
| **Tools**    | LLM (invoked)   | Execute actions, call APIs, run queries     | ✓       |
| **Resources**| Host / LLM (read) | URI-addressed data, config, file content  | ✗       |
| **Prompts**  | User / host     | Reusable templates, multi-step flows        | —       |

Decision heuristic: *does the AI need to do something?* → Tool. *Does it need to know something?* → Resource. *Does the user need a consistent interaction pattern?* → Prompt [[6]](https://www.getknit.dev/blog/mcp-architecture-deep-dive-tools-resources-and-prompts-explained). Resources and Prompts are the most-skipped primitives — and the biggest driver of over-using tool calls for context retrieval [[7]](https://dev.to/aws-heroes/mcp-prompts-and-resources-the-primitives-youre-not-using-3oo1).

### Transports

| Transport              | When to use                          | Auth requirement                 |
| :--------------------- | :----------------------------------- | :------------------------------- |
| `stdio`                | Local, single-client, spawned as child process | Process isolation     |
| `Streamable HTTP + SSE` | Remote, multi-client, cloud         | OAuth 2.1 + PKCE S256            |

Spec 2025-11-25 mandates OAuth 2.1 + PKCE, RFC 9728 Protected Resource Metadata, and RFC 8707 Resource Indicators for remote servers [[3]](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026). Stateless servers can now run behind a round-robin load balancer; stateful operations should mint explicit handles (a `basket_id`) that the model passes back as ordinary arguments [[13]](https://www.webfuse.com/mcp-cheat-sheet).

### Official SDKs

**Python SDK** ⭐ 23.2k — FastMCP decorator API [[8]](https://techwithibrahim.medium.com/the-mcp-typescript-sdk-a-complete-guide-to-tools-resources-prompts-and-beyond-285c6ad05a07):

```python
@app.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city. Use when the user asks about weather."""
    return f"Weather in {city}: 16°C, partly cloudy"
```

**TypeScript SDK** ⭐ 12.6k — Zod schema, type-safe [[8]](https://techwithibrahim.medium.com/the-mcp-typescript-sdk-a-complete-guide-to-tools-resources-prompts-and-beyond-285c6ad05a07):

```typescript
server.tool(
  "get_weather",
  "Get current weather for a city. Use when the user asks about weather.",
  { city: z.string().describe("City name") },
  async ({ city }) => ({ content: [{ type: "text", text: `...` }] })
);
```

The description string in both forms is what the LLM reads to decide whether to call the tool — treat it as API documentation [[6]](https://www.getknit.dev/blog/mcp-architecture-deep-dive-tools-resources-and-prompts-explained).

### Tool annotations

Four optional boolean hints in `ToolAnnotations` [[9]](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/) [[10]](https://mcpblog.dev/blog/2026-03-13-mcp-tool-annotations):

| Hint             | Default | Meaning                                            |
| :--------------- | :------ | :------------------------------------------------- |
| `readOnlyHint`   | `false` | Tool does not modify state                         |
| `destructiveHint`| `true`  | Tool may destroy or overwrite data                 |
| `idempotentHint` | `false` | Repeated identical calls produce the same result   |
| `openWorldHint`  | `true`  | Tool reaches outside local environment             |

Defaults are deliberately cautious. Clients use hints for UI decisions (confirmation dialogs, parallelism) and Claude Code uses `readOnlyHint: true` to enable concurrent dispatch. **Hints are not guarantees** — a server can misrepresent them; clients cannot trust annotations from untrusted servers [[9]](https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/).

### Tool design craft rules

1. **Description is the selection mechanism.** Include trigger phrases ("use when…"), what the tool does, and what it returns. Name alone is insufficient [[6]](https://www.getknit.dev/blog/mcp-architecture-deep-dive-tools-resources-and-prompts-explained).
2. **Always use strict JSON Schema.** Set `additionalProperties: false`. Use Zod or Pydantic — they generate the schema and validate inputs at the same time [[3]](https://workos.com/blog/everything-your-team-needs-to-know-about-mcp-in-2026).
3. **Sanitize outputs before returning.** Tool responses re-enter the LLM's context. Strip instruction-like patterns from document bodies, scraped pages, webhook payloads, and error messages [[11]](https://www.practical-devsecops.com/mcp-security-vulnerabilities/).
4. **Single-purpose servers.** One server, one domain. Mixing database tools with email tools expands blast radius when one tool is compromised [[12]](https://www.digitalapplied.com/blog/mcp-server-patterns-enterprise-ai-agents).
5. **Annotate destructive operations explicitly.** `destructiveHint: true` + `readOnlyHint: false` lets clients gate on human approval — even if these are already the defaults, stating them makes intent auditable [[10]](https://mcpblog.dev/blog/2026-03-13-mcp-tool-annotations).

### Resource design craft rules

- URI-address everything: `config://`, `user://current/settings`, `file://path` for consistent discovery [[6]](https://www.getknit.dev/blog/mcp-architecture-deep-dive-tools-resources-and-prompts-explained).
- Include `mimeType` so hosts render content correctly.
- Never allow a tool call to mutate a resource directly — design separate write tools.
- If lists can change, set `"listChanged": true` in capabilities and emit `notifications/tools/list_changed` [[13]](https://www.webfuse.com/mcp-cheat-sheet).

### Security: non-negotiables

The full MCP security spec [[14]](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices) documents seven attack classes. For server authors the most actionable:

- **Treat all tool inputs as hostile.** They arrive from an LLM, not a human. Validate with Zod/Pydantic; reject anything outside schema [[14]](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices).
- **No token passthrough.** An MCP server MUST NOT accept tokens not explicitly issued for it and forward them downstream. This is the "confused deputy" anti-pattern [[14]](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices).
- **Scope minimization.** Start with minimal scopes; elevate via targeted `WWW-Authenticate` challenges when privileged operations are first attempted. Never pre-request all scopes [[14]](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices).
- **Indirect prompt injection.** Tool responses that contain document bodies, scraped pages, or search results can carry injected instructions. Sanitize before returning [[15]](https://developer.microsoft.com/blog/protecting-against-indirect-injection-attacks-mcp).
- **Hash tool definitions on first approval.** Re-validate schema hashes before every invocation. "Rug pull" attacks change a benign tool description post-approval to redirect agent behavior [[11]](https://www.practical-devsecops.com/mcp-security-vulnerabilities/).
- **Audit log every invocation.** Redact secrets; rate-limit per client; integrate with SIEM for anomaly alerting [[16]](https://labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices-v1/).
- **SSRF for remote servers.** OAuth metadata URLs can redirect to internal resources. Block private IP ranges; enforce HTTPS; pin DNS resolution between check and use [[14]](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices).

### Testing

Use [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to browse all exposed primitives, test tool calls with custom arguments, and inspect raw JSON-RPC traffic. It catches schema mismatches and logic errors before production [[13]](https://www.webfuse.com/mcp-cheat-sheet). The [cyanheads/model-context-protocol-resources](https://github.com/cyanheads/model-context-protocol-resources) ⭐ 279 repo maintains client development guides and reference implementations [[18]](https://github.com/cyanheads/model-context-protocol-resources).

---

## Part 3 — Claude Code Plugins

### Standalone vs plugin

| | Standalone `.claude/` | Plugin |
| :--- | :--- | :--- |
| Skill name format | `/hello` | `/my-plugin:hello` |
| Best for | Personal config, project-specific, rapid iteration | Sharing, distribution, versioned releases |
| Installation | Manual copy | `/plugin install` |
| Multi-project reuse | Duplicate manually | Install once |
| Namespace conflicts | Possible | Impossible (namespaced) |

Start standalone in `.claude/` for rapid iteration; convert to a plugin when ready to share [[4]](https://code.claude.com/docs/en/plugins.md).

### Plugin directory structure

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json         # manifest; ONLY this file lives here
├── skills/<name>/SKILL.md  # → /my-plugin:<name>
├── agents/                  # custom subagent definitions
├── hooks/hooks.json         # event handlers
├── .mcp.json                # bundled MCP server configs
├── .lsp.json                # LSP server configurations
├── monitors/monitors.json   # background file/log watchers
├── bin/                     # executables injected into PATH
└── settings.json            # defaults applied when plugin enabled
```

The `.claude-plugin/` directory contains **only** `plugin.json`. Putting skills, agents, or hooks inside `.claude-plugin/` is the most common structural mistake [[4]](https://code.claude.com/docs/en/plugins.md).

### `plugin.json` schema

```json
{
  "name": "my-plugin",
  "description": "...",
  "version": "1.0.0",
  "author": { "name": "Your Name" }
}
```

`version` is optional; omit it and the commit SHA becomes the version. Set it explicitly if you want user-controlled update gates [[4]](https://code.claude.com/docs/en/plugins.md).

### Background monitors

Monitors watch logs, files, or external state and deliver each stdout line as a Claude notification [[4]](https://code.claude.com/docs/en/plugins.md):

```json
[{
  "name": "error-log",
  "command": "tail -F ./logs/error.log",
  "description": "Application error log"
}]
```

### Development workflow

```bash
# Iterate locally
claude --plugin-dir ./my-plugin

# Pick up changes without restart
/reload-plugins

# Load a pre-built archive (v2.1.128+)
claude --plugin-dir ./my-plugin.zip

# Validate before submitting
claude plugin validate
```

Two public marketplaces exist: `claude-plugins-official` (Anthropic-curated) and `claude-community` (third-party, review-gated). Submit to community review at `claude.ai/settings/plugins/submit` [[4]](https://code.claude.com/docs/en/plugins.md).

---

## Cross-cutting rules

| Rule                        | Skills                          | MCP servers                        | Plugins        |
| :-------------------------- | :------------------------------ | :--------------------------------- | :------------- |
| Description = interface     | ✓ activation signal             | ✓ tool selection signal            | ✓ marketplace discovery |
| Progressive disclosure      | 3-tier loading                  | capabilities declared on `initialize` | — |
| Side-effect gates           | `disable-model-invocation`      | `destructiveHint` + human approval | — |
| Audit / observability       | hooks                           | log every call                     | monitors |
| Scope minimization          | narrow `paths:` + `allowed-tools:` | minimal OAuth scopes            | — |
| Distribution unit           | project commit / plugin         | server binary                      | `/plugin install` |

The common failure mode across all three: **over-broad scope**. A skill that activates on everything, a tool with no JSON Schema, a plugin that grants `*` permissions — all expand blast radius for free. Narrow the activation surface, validate inputs, annotate risk [[16]](https://labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices-v1/) [[17]](https://www.truefoundry.com/blog/mcp-security-risks-best-practices).
