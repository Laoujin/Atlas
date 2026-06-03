---
title: "Operating Extensions at Scale"
date: 2026-06-03
depth: standard
format: md
topic: "Operating extensions at scale"
topic_raw: "Operating extensions at scale"
issue: 181
tags: [claude-code, mcp, skills, agent-sdk, extensions, devex, enterprise]
summary: "Token budget maths, skill routing mechanics, the six MCP primitives, headless CI patterns, and team rate-limit tables for expert developers operating Claude Code extensions at scale."
citations: 18
reading_time_min: 9
cover: cover.svg
validation_error: "exit 2 at `jq -r .result "$RESULT_JSON"` — jq: error: Could not open file /home/runner/actions-runner/_work/Scout/Scout/atlas-checkout/research/2026-06-03-fourth-session-in-a-virtual-deep-dive-series-for-an-expert-developer-audience-1-2h-virtual-prior-sessions-1-ai-security/operating-extensions-at-scale/.scout-result.json: No such file or directory"
---

> **TL;DR** Skills are the cheap scalable primitive — 30–50 tokens until invoked versus 50k+ for a five-server MCP setup [[4]](https://codersera.com/blog/claude-skills-mcp-servers-practitioner-guide-2026/). The `description` field in `SKILL.md` is the routing layer, not documentation [[5]](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices). For headless CI use `claude -p --bare`; the Agent SDK brings the same loop into Python/TypeScript [[8]](https://code.claude.com/docs/en/headless) [[9]](https://code.claude.com/docs/en/agent-sdk/overview). Budget ~$150–250/dev/month at enterprise scale and set workspace spend limits before rollout [[2]](https://code.claude.com/docs/en/costs).

## Extension taxonomy

[Claude Code](https://github.com/anthropics/claude-code) ⭐ 130k [[17]](https://github.com/anthropics/claude-code) has four distinct extension primitives with different loading costs and scopes [[1]](https://code.claude.com/docs/en/skills) [[2]](https://code.claude.com/docs/en/costs):

| Primitive   | Context cost at startup                      | How it loads                              | Best for                                |
| ----------- | -------------------------------------------- | ----------------------------------------- | --------------------------------------- |
| **Skills**  | ~100 tokens (name + description only)        | Body loads on demand when relevant        | Procedural knowledge, reusable workflows |
| **MCP**     | Up to 18k tokens/server (deferred in Jan 2026) | Full schema unless Tool Search active   | External system connectivity            |
| **Agents**  | Proportional to spawn prompt                 | Spawned on request; own context window    | Isolated subtasks, parallel work        |
| **Hooks**   | Near zero (runs outside context window)      | Shell commands at lifecycle events        | Pre/post-tool validation, audit logging |

The operative framing: **MCP is connectivity, Skills are procedural knowledge** [[4]](https://codersera.com/blog/claude-skills-mcp-servers-practitioner-guide-2026/). When you find yourself re-explaining the same workflow across sessions, that's a Skill. When Claude needs to reach a system it can't access independently, that's MCP.

## Context budget reality

### MCP token overhead

MCP injects full tool schema — name, description, all parameter definitions — into every message [[3]](https://www.jdhodges.com/blog/claude-code-mcp-server-token-costs/). Measured startup costs per server:

| MCP Server         | Tools | Startup token cost |
| ------------------ | ----: | -----------------: |
| SQLite (minimal)   |     6 |               ~385 |
| Gmail              |     7 |             ~2,640 |
| Playwright         |    22 |             ~3,442 |
| GitHub MCP         |     — |          8k–12,000 |
| Full SQLite suite  |     — |            ~13,400 |
| mcp-omnisearch     |     — |            ~14,100 |
| Jira               |     — |            ~17,000 |

The most expensive single tool in the Gmail server (`gmail_create_draft`) costs 820 tokens alone; the cheapest (`browser_close`) costs 59 [[3]](https://www.jdhodges.com/blog/claude-code-mcp-server-token-costs/). A five-server developer setup reaches 50k–66k tokens before the first user prompt [[15]](https://www.mindstudio.ai/blog/claude-code-mcp-server-token-overhead) [[3]](https://www.jdhodges.com/blog/claude-code-mcp-server-token-costs/).

### Tool Search deferral (Jan 2026)

MCP Tool Search auto-enables when tool definitions exceed **10% of the context window**. Only tool names enter context; full schemas load on demand via search [[2]](https://code.claude.com/docs/en/costs). Users report up to **95% reduction** in startup token cost [[15]](https://www.mindstudio.ai/blog/claude-code-mcp-server-token-overhead). Set `ENABLE_TOOL_SEARCH=auto:5` to lower the activation threshold to 5% for more aggressive deferral.

In one measured session: 5,900 tokens recovered from MCP tool deferral + 7,300 from system tool deferral = 13,200 tokens saved [[3]](https://www.jdhodges.com/blog/claude-code-mcp-server-token-costs/).

### Skills stay cheap at scale

Skills load only ~100 tokens at startup (name + description). Body content enters context only when Claude deems the skill relevant. Teams routinely run 20–50 Skills simultaneously with negligible overhead [[4]](https://codersera.com/blog/claude-skills-mcp-servers-practitioner-guide-2026/). Keep `SKILL.md` under 500 lines; overflow content lives in linked reference files [[5]](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## Skill authoring craft

### The description is the routing layer

Claude reads only `name` and `description` when deciding whether to load a skill. This makes the description the most operationally significant token in your skillset [[5]](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

```yaml
# Good: specific triggers; what AND when
description: >
  Extracts text and tables from PDF files, fills forms, merges documents.
  Use when working with PDF files or when the user mentions PDFs, forms,
  or document extraction.

# Bad: too vague to route correctly
description: Helps with documents
```

Rules enforced by the spec [[5]](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):
- Always **third person** ("Processes Excel files…", not "I can help…")
- Include both **what** (capability) and **when** (concrete trigger phrases, file types)
- Max 64-char name (lowercase, hyphens only); max 1,024-char description; no XML tags

If a skill isn't triggering, the root cause is almost always a vague description. Verify registration with `/plugin` [[4]](https://codersera.com/blog/claude-skills-mcp-servers-practitioner-guide-2026/).

### Invocation mode

Add an `invocation` key to frontmatter to control who fires the skill [[1]](https://code.claude.com/docs/en/skills):
- `auto` (default): Claude decides when the skill is relevant
- `user`: skill only runs when explicitly invoked via `/skill-name`

Long reference skills or rarely-needed playbooks should use `user` to prevent spurious loads.

### Progressive disclosure structure

```
my-skill/
├── SKILL.md            ← loaded on trigger (≤500 lines)
├── reference.md        ← read only when Claude follows the link
├── examples.md         ← read only when needed
└── scripts/
    └── validate.py     ← executed, not loaded — only output consumes tokens
```

SKILL.md acts as a table of contents. Scripts execute without loading source; only their output costs tokens. Keep all reference links **one level deep** from SKILL.md — nested chains (`A → B → C`) cause partial reads [[5]](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

### Degrees of freedom

Match instruction specificity to task fragility [[5]](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):

| Specificity     | When to use                                        | Example                            |
| --------------- | -------------------------------------------------- | ---------------------------------- |
| High freedom    | Multiple valid approaches; context drives choice   | Code review, analysis              |
| Medium freedom  | Preferred pattern exists; some variation OK        | Report generation                  |
| Low freedom     | Fragile sequence; consistency critical             | Database migrations, exact scripts |

### Team deployment patterns

| Scenario             | Skill encodes                            | MCP provides                   |
| -------------------- | ---------------------------------------- | ------------------------------ |
| Code review          | House style, guardrails                  | GitHub (diffs, comments)       |
| Database analysis    | Safety constraints, schema context       | Postgres                       |
| Incident response    | Regression identification, PR draft flow | Sentry + GitHub                |
| Support triage       | Classification logic                     | Slack + Linear                 |

## MCP beyond `tools/call`

Most builders only use the tool primitive. The spec defines six primitives across server- and client-side [[6]](https://workos.com/blog/mcp-features-guide):

### Server-side (server exposes to client)

**Tools** — actions with explicit user approval per call. The one everyone knows.

**Resources** — read-only data identified by URIs and MIME types (`travel://activities/{city}/{category}`). Pulled by the client; never trigger operations. Treat them like structured files the server makes queryable.

**Prompts** — version-controlled instruction templates with typed variables. Servers define them; clients fill variables and build workflows. Enables centralized prompt governance: update once, propagate everywhere.

### Client-side (client exposes to server)

These three unlock human-in-the-loop patterns that tool primitives alone can't produce [[6]](https://workos.com/blog/mcp-features-guide) [[7]](https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip):

**Sampling** — server requests an LLM completion from the client's model without needing its own API key. Users must explicitly approve the prompt before execution. Primary use: intent routing before tool dispatch — a 25-tool customer support server using Haiku to classify user intent adds ~200–800ms but removes 500 tokens of routing logic from the main agent prompt [[7]](https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip).

```
Server → sampling/create → Client (user approves) → LLM → Client → Server
```

Skip sampling for voice pipelines requiring <300ms response.

**Roots** — client declares filesystem URI boundaries the server may access during handshake. Prevents path guessing; enforces security perimeters when agents process customer-uploaded files or local knowledge bases [[7]](https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip). Listen for `RootsListChangedNotification` when workspaces switch.

**Elicitation** — server pauses execution and requests schema-validated structured input from the user via the client's UI (added in spec 2025-06-18) [[6]](https://workos.com/blog/mcp-features-guide). Replaces fragile multi-turn loops: define an enum schema, receive typed JSON back.

```json
{ "action": { "enum": ["accept", "decline", "cancel"] } }
```

⚠ Check `clientCapabilities?.elicitation` before calling and fall back gracefully when the connected client doesn't support it [[7]](https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip).

### Human-in-the-loop pattern matrix

| Pattern      | Use case                               | Latency cost |
| ------------ | -------------------------------------- | ------------ |
| Elicitation  | User confirmations, structured input   | <100ms       |
| Sampling     | Intent routing, classification         | 200–800ms    |
| Roots        | File scoping, security boundary        | None         |
| Hook system  | Ops supervisor approval workflows      | Async        |

## Headless operation & Agent SDK

### `claude -p --bare`

`--bare` skips auto-discovery of hooks, skills, plugins, MCP servers, and CLAUDE.md [[8]](https://code.claude.com/docs/en/headless). This is the recommended CI mode: identical results on any machine regardless of local developer configuration. It will become the default `-p` behavior in a future release.

```bash
# Pipe data in, text out
cat build-error.txt | claude --bare -p "explain the root cause" > output.txt

# Schema-enforced JSON output
claude --bare -p "Extract function names from auth.ts" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'

# Session continuity across invocations
session_id=$(claude -p "Start review" --output-format json | jq -r '.session_id')
claude -p "Continue with database layer" --resume "$session_id"
```

stdin is capped at 10MB; for larger inputs pass a file path in the prompt instead of piping [[8]](https://code.claude.com/docs/en/headless).

### Agent SDK

The [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) brings the same loop — tools, context, hooks, subagents, skills, MCP — into Python and TypeScript [[9]](https://code.claude.com/docs/en/agent-sdk/overview). Repos: [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) ⭐ 7.2k [[10]](https://github.com/anthropics/claude-agent-sdk-python) · [claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript) ⭐ 1.5k [[11]](https://github.com/anthropics/claude-agent-sdk-typescript)

```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Find and fix the bug in auth.py",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
):
    print(message)
```

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Find and fix the bug in auth.ts",
  options: { allowedTools: ["Read", "Edit", "Bash"] }
})) {
  if ("result" in message) console.log(message.result);
}
```

**SDK vs Managed Agents vs CLI [[9]](https://code.claude.com/docs/en/agent-sdk/overview):**

| Dimension      | CLI (`claude -p`)          | Agent SDK                     | Managed Agents                     |
| -------------- | -------------------------- | ----------------------------- | ---------------------------------- |
| Interface      | Shell                      | Python / TypeScript library   | REST API                           |
| Runs in        | Your machine               | Your process                  | Anthropic-managed sandbox          |
| Session state  | JSONL on filesystem        | JSONL on filesystem           | Anthropic-hosted event log         |
| Custom tools   | Via MCP config             | In-process callbacks          | You execute, return results        |
| Best for       | One-off scripts, local dev | Production automation, CI/CD  | Long-running async sessions        |

**June 15 2026 billing change**: Agent SDK and `claude -p` usage migrates from subscription quota to a separate monthly Agent SDK credit [[18]](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan). Plan for this now if you bill agent usage against team quotas.

### Hooks in the SDK

SDK hooks use callback functions rather than shell commands. `PostToolUse` for audit logging, `PreToolUse` for validation or output filtering [[9]](https://code.claude.com/docs/en/agent-sdk/overview):

```typescript
const logFileChange: HookCallback = async (input) => {
  const path = (input as any).tool_input?.file_path ?? "unknown";
  await appendFile("audit.log", `${new Date().toISOString()}: ${path}\n`);
  return {};
};

options: {
  permissionMode: "acceptEdits",
  hooks: { PostToolUse: [{ matcher: "Edit|Write", hooks: [logFileChange] }] }
}
```

A PreToolUse hook can filter a 10,000-line test log down to failure lines before it ever enters context — turning tens of thousands of tokens into hundreds [[2]](https://code.claude.com/docs/en/costs).

## Operating at scale

### Cost baselines

Enterprise deployments average **~$13/dev/active day**, **~$150–250/dev/month**; 90% of users stay below $30/active day [[2]](https://code.claude.com/docs/en/costs). Model choice and context size drive most variance — Sonnet for teammates and subagents, Opus for architectural decisions.

Agent teams (parallel Claude instances) use ~7× more tokens than standard sessions. Keep spawn prompts focused; clean up teams when work completes [[2]](https://code.claude.com/docs/en/costs).

### Rate limit allocation

Concurrent users are a fraction of total, so per-user TPM decreases as org size grows [[2]](https://code.claude.com/docs/en/costs):

| Team size     | TPM / user   | RPM / user  |
| ------------- | ------------ | ----------- |
| 1–5           | 200k–300k    | 5–7         |
| 5–20          | 100k–150k    | 2.5–3.5     |
| 20–50         | 50k–75k      | 1.25–1.75   |
| 50–100        | 25k–35k      | 0.62–0.87   |
| 100–500       | 15k–20k      | 0.37–0.47   |
| 500+          | 10k–15k      | 0.25–0.35   |

⚠ Live training events (large groups online simultaneously) need temporary higher allocations — the table assumes normal daily concurrency patterns.

### Spend controls

- **API plans**: workspace spend limits in the Claude Console; set a workspace rate limit to cap Claude Code's share and protect other production workloads
- **Pro/Max**: `/usage-credits` monthly cap via CLI
- **Bedrock/Vertex/Foundry**: LiteLLM for per-key cost tracking (unaffiliated, not audited by Anthropic) [[2]](https://code.claude.com/docs/en/costs)
- `/usage` command shows 24h/7d token attribution per MCP server, skill, and subagent

### Token reduction without removing capability

1. Move CLAUDE.md procedures into Skills — CLAUDE.md loads unconditionally; Skills load on demand [[2]](https://code.claude.com/docs/en/costs). Keep CLAUDE.md under 200 lines.
2. Prefer CLI tools (`gh`, `aws`, `gcloud`) over MCP where available — no per-tool schema overhead [[2]](https://code.claude.com/docs/en/costs).
3. Filter verbose tool outputs in PreToolUse hooks before they reach context.
4. Delegate log processing and test runs to subagents — verbose output stays isolated; only summary returns to main conversation.
5. Always use `--bare` in CI to prevent local developer hooks and MCPs from bleeding into pipeline runs [[8]](https://code.claude.com/docs/en/headless).

### MCP production practices

The [MCP servers registry](https://github.com/modelcontextprotocol/servers) ⭐ 87k [[14]](https://github.com/modelcontextprotocol/servers) lists community implementations. For production deployments [[13]](https://modelcontextprotocol.info/docs/best-practices/) [[16]](https://medium.com/cdata-software/the-definitive-2026-guide-to-implementing-mcp-in-enterprise-environments-d74009a17b07):

- **Single domain per server** — one clear purpose per MCP; no monolithic servers
- **Strict schemas** — typed inputs/outputs with documented side effects; schema drift is the primary cause of production tool failures
- **Circuit breakers** — graceful degradation when downstream APIs are unavailable
- **Enterprise auth** — OAuth 2.1 with re-authentication per tool call (not session-level token); route through an MCP Gateway for centralized policy enforcement and per-team audit trails [[16]](https://medium.com/cdata-software/the-definitive-2026-guide-to-implementing-mcp-in-enterprise-environments-d74009a17b07)
- **Targets** [[13]](https://modelcontextprotocol.info/docs/best-practices/): >1,000 req/s per instance · P95 <100ms · error rate <0.1% · >99.9% uptime

The 2026 MCP roadmap priorities: stateless horizontal scaling via HTTP transport evolution and `.well-known` capability discovery; Tasks primitive for agent-to-agent communication; governance via Working Groups [[12]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/).

## Debugging reference

| Symptom                             | First check                                        | Fix                                                |
| ----------------------------------- | -------------------------------------------------- | -------------------------------------------------- |
| Skill never triggers automatically  | `description` vague; missing "Use when…" phrase   | Rewrite with specific trigger phrases; verify `/plugin` |
| Skill not in slash-command list     | Not in watched skill directories                   | Check `~/.claude/skills/`, `.claude/skills/`       |
| MCP tool "not found" error          | Short tool name instead of `Server:tool_name`      | Prefix with MCP server name                        |
| 50k+ startup token burn             | Many MCPs without Tool Search deferral             | Enable Tool Search; disable unused servers via `/mcp` |
| CI builds inconsistent vs local     | Local hooks/MCPs bleeding into `claude -p`        | Add `--bare` flag                                  |
| Skill content partially loaded      | Deep reference nesting (`A → B → C`)               | Flatten all references to one level from SKILL.md  |
| Agent SDK auth failure in CI        | OAuth blocked in bare mode; API key missing        | Set `ANTHROPIC_API_KEY`; pass via `--settings`     |
| Elicitation request silently ignored | Client doesn't support elicitation               | Check `clientCapabilities?.elicitation` first      |
