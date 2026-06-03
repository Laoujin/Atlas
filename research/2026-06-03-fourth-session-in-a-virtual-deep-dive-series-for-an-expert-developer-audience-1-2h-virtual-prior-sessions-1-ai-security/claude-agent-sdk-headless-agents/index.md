---
title: "Claude Agent SDK & Headless Agents"
date: 2026-06-03
depth: standard
format: md
topic: "Claude Agent SDK & headless agents"
topic_raw: "Claude Agent SDK & headless agents"
issue: 181
tags: [claude, agent-sdk, headless, anthropic, workflow, subagents, mcp, developer-tools]
summary: "Complete technical reference: the query() API, claude -p headless mode, subagents, hooks, dynamic workflows, and the June 15 2026 billing separation—all from official docs."
citations: 18
reading_time_min: 8
cover: cover.svg
validation_error: "jq: error: Could not open file /home/runner/actions-runner/_work/Scout/Scout/atlas-checkout/research/2026-06-03-fourth-session-in-a-virtual-deep-dive-series-for-an-expert-developer-audience-1-2h-virtual-prior-sessions-1-ai-security/claude-agent-sdk-headless-agents/.scout-result.json: No such file or directory;"
---

> **TL;DR:** The Claude Agent SDK (renamed from Claude Code SDK) gives you Claude's full agentic loop—built-in tools, subagents, hooks, MCP, sessions—as a Python or TypeScript library running in your own process [[1]](https://code.claude.com/docs/en/agent-sdk/overview). Use `claude -p` for one-shot CLI tasks; use `query()` for programmatic control with structured output. Starting June 15, 2026, all headless/SDK usage draws from a separate monthly credit ($20–$200 by plan), separate from interactive limits [[13]](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan).

## What it is

Renamed from "Claude Code SDK" in late 2025, the Agent SDK packages the same engine as [Claude Code](https://github.com/anthropics/claude-code) ⭐ 130k (Jun 2026) as an embeddable library [[15]](https://github.com/anthropics/claude-code). The fundamental design principle: **Gather Context → Take Action → Verify Work → Repeat** — the same loop an expert programmer follows, delegated to Claude [[2]](https://claude.com/blog/building-agents-with-the-claude-agent-sdk).

The key distinction from the [Anthropic Client SDK](https://platform.claude.com/docs/en/api/client-sdks): the Client SDK hands you raw message objects and requires you to implement the tool loop; the Agent SDK handles that loop autonomously [[1]](https://code.claude.com/docs/en/agent-sdk/overview).

```python
# Client SDK: you implement the tool loop
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# Agent SDK: Claude handles tools autonomously
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

## Installation

```bash
pip install claude-agent-sdk          # Python 3.10+
npm install @anthropic-ai/claude-agent-sdk   # bundles native binary; no separate Claude Code install
```

Set `ANTHROPIC_API_KEY` (or configure Bedrock/Vertex/Foundry env vars). Third-party cloud provider support: set `CLAUDE_CODE_USE_BEDROCK=1`, `CLAUDE_CODE_USE_VERTEX=1`, or `CLAUDE_CODE_USE_FOUNDRY=1` with the respective provider credentials [[1]](https://code.claude.com/docs/en/agent-sdk/overview).

- [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) ⭐ 7.2k [[3]](https://github.com/anthropics/claude-agent-sdk-python)
- [anthropics/claude-agent-sdk-typescript](https://github.com/anthropics/claude-agent-sdk-typescript) ⭐ 1.5k [[4]](https://github.com/anthropics/claude-agent-sdk-typescript)

## Headless CLI: `claude -p`

The `-p` / `--print` flag makes Claude Code non-interactive — one turn, stdout output, exits [[5]](https://code.claude.com/docs/en/headless).

```bash
# Basic question
claude -p "What does the auth module do?"

# Pipe data in, redirect out (stdin capped at 10MB as of v2.1.128)
cat build-error.txt | claude -p 'explain the root cause concisely' > output.txt

# Structured JSON output with schema enforcement
claude -p "Extract function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}'

# CI-safe: bare mode, no config discovery, no permission prompts
claude --bare -p "Run tests and summarize failures" \
  --allowedTools "Bash,Read" \
  --permission-mode acceptEdits

# Stream tokens in real time (NDJSON)
claude -p "Write a migration plan" --output-format stream-json \
  --verbose --include-partial-messages \
  | jq -rj 'select(.type=="stream_event" and .event.delta.type?=="text_delta") | .event.delta.text'
```

Key flags [[5]](https://code.claude.com/docs/en/headless):

| Flag                              | Effect                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------- |
| `--bare`                          | Skips hooks, skills, MCP servers, CLAUDE.md, memory — identical across machines |
| `--allowedTools "Read,Edit,Bash"` | Auto-approve named tools; no permission prompt                                  |
| `--permission-mode acceptEdits`   | Auto-approve file writes; still prompts for shell/network calls                 |
| `--permission-mode dontAsk`       | Never prompt — blocks anything not in allowlist; safe for locked-down CI        |
| `--output-format json`            | Returns `{result, session_id, total_cost_usd, ...}` — parseable with `jq`      |
| `--output-format stream-json`     | NDJSON token stream; filter with `jq` for live display                          |
| `--append-system-prompt "..."`    | Extend the system prompt without replacing Claude Code's defaults               |
| `--continue` / `--resume <id>`    | Continue most recent or a specific past session                                 |
| `--settings <file-or-json>`       | Load settings explicitly (useful in `--bare` mode where auto-discovery is off)  |

⚠ `--bare` will become the default for `-p` in a future release. Without it, a hook in any contributor's `~/.claude` or an MCP server in `.mcp.json` will silently execute in your CI [[5]](https://code.claude.com/docs/en/headless).

## Programmatic: `query()`

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
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

`query()` yields typed message objects. The final `ResultMessage` carries `result`, `session_id`, `total_cost_usd`, and `subtype` (`success` / `error_max_turns` / `error_max_budget_usd`). For multi-turn conversations, use Python's `ClaudeSDKClient` (tracks session state automatically across `client.query()` calls) or TypeScript's `continue: true` option [[12]](https://code.claude.com/docs/en/agent-sdk/sessions).

## Built-in tools

No tool execution code required — these ship with the SDK [[1]](https://code.claude.com/docs/en/agent-sdk/overview):

| Tool             | What it does                                                        |
| ---------------- | ------------------------------------------------------------------- |
| `Read`           | Read any file in the working directory                              |
| `Write`          | Create new files                                                    |
| `Edit`           | Precise edits to existing files (diff-based)                        |
| `Bash`           | Terminal commands, scripts, git operations                          |
| `Glob`           | Find files by pattern (`**/*.ts`, `src/**/*.py`)                    |
| `Grep`           | Regex search across file contents                                   |
| `Monitor`        | Watch a background script; react to each output line as an event   |
| `WebSearch`      | Live web search                                                     |
| `WebFetch`       | Fetch and parse web page content                                    |
| `AskUserQuestion`| Prompt the user with structured multiple-choice options             |
| `Agent`          | Spawn a subagent (include in `allowedTools` to auto-approve)        |
| `Workflow`       | Launch a dynamic workflow script (TypeScript SDK v0.3.149+)         |

## Subagents

Subagents run in fresh context windows, isolating intermediate work from the parent and enabling parallelism [[6]](https://code.claude.com/docs/en/agent-sdk/subagents):

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob", "Agent"],
    agents={
        "code-reviewer": AgentDefinition(
            description="Use for quality, security, and maintainability reviews.",
            prompt="You are a code review specialist. Find security vulnerabilities and quality issues.",
            tools=["Read", "Grep", "Glob"],  # read-only restriction
            model="opus",                    # per-agent model override
        ),
        "test-runner": AgentDefinition(
            description="Use for test execution and coverage analysis.",
            prompt="Run tests and summarize failures concisely.",
            tools=["Bash", "Read", "Grep"],
            background=True,                 # non-blocking: parent continues immediately
        ),
    },
)
```

The `description` field drives automatic invocation — Claude selects subagents based on it. Mention a subagent by name in the prompt to force invocation. **Critical constraint: subagents cannot spawn their own subagents** — don't include `Agent` in a subagent's `tools` list [[6]](https://code.claude.com/docs/en/agent-sdk/subagents).

`AgentDefinition` fields of note:

| Field          | Purpose                                                                          |
| -------------- | -------------------------------------------------------------------------------- |
| `model`        | Per-agent alias (`"opus"`, `"sonnet"`, `"haiku"`) or full model ID              |
| `background`   | Non-blocking; parent continues while subagent runs                               |
| `maxTurns`     | Stop after N agentic turns                                                       |
| `effort`       | Reasoning effort: `low`, `medium`, `high`, `xhigh`, `max`                       |
| `permissionMode` | Override permission mode for this subagent only                               |
| `mcpServers`   | Subagent-specific MCP servers (subset of parent's, or new ones)                  |
| `skills`       | Skills to preload into this subagent's context at startup                        |

Common tool combinations [[6]](https://code.claude.com/docs/en/agent-sdk/subagents):

| Use case             | Tools                                     |
| -------------------- | ----------------------------------------- |
| Read-only analysis   | `Read`, `Grep`, `Glob`                    |
| Test execution       | `Bash`, `Read`, `Grep`                    |
| Code modification    | `Read`, `Edit`, `Write`, `Grep`, `Glob`   |
| Full access          | Omit `tools` field — inherits all         |

Reference implementations in [anthropics/claude-agent-sdk-demos](https://github.com/anthropics/claude-agent-sdk-demos) ⭐ 2.5k: multi-agent research system, branding assistant, spreadsheet agent, resume generator [[7]](https://github.com/anthropics/claude-agent-sdk-demos).

## Dynamic Workflows

For jobs coordinating dozens to hundreds of agents (codebase audits, large migrations, cross-checked research), the `Workflow` tool moves orchestration into a JavaScript script the runtime executes outside the conversation context [[8]](https://code.claude.com/docs/en/workflows):

```javascript
export const meta = {
  name: "api-auth-audit",
  description: "Audit every API endpoint for missing auth checks",
  phases: [{ title: "Scan" }, { title: "Verify" }],
};

const FINDING = { type: "object", properties: {
  endpoint: { type: "string" },
  missing_auth: { type: "boolean" },
  details: { type: "string" }
}, required: ["endpoint", "missing_auth"] };

phase("Scan");
const findings = await pipeline(
  endpoints,   // list discovered earlier
  e => agent(`Check ${e} for missing authentication`, { phase: "Scan", schema: FINDING }),
  f => f?.missing_auth
    ? agent(`Adversarially verify: is ${f.endpoint} really unprotected?`, {
        phase: "Verify", label: `verify:${f.endpoint}`
      })
    : null
);
return findings.filter(Boolean);
```

Script primitives [[8]](https://code.claude.com/docs/en/workflows):

| Primitive              | Semantics                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------- |
| `agent(prompt, opts)`  | Spawn one agent; returns string or typed object (when `schema` provided)               |
| `pipeline(items, ...stages)` | No barrier between stages — item A in stage 3 while item B is still in stage 1  |
| `parallel(thunks)`     | Barrier: awaits all before returning — use only when cross-item context needed         |
| `phase(title)`         | Group subsequent agents in the `/workflows` progress view                              |
| `log(message)`         | Emit a narrator line above the progress tree                                           |
| `budget`               | `{total, spent(), remaining()}` — scale agent count to a token budget                 |

Runtime constraints: up to 16 concurrent agents (fewer on limited-CPU machines), 1,000 agents total per run, runs are resumable within the same session [[8]](https://code.claude.com/docs/en/workflows).

Trigger methods: include `ultracode` keyword in your prompt, say "use a workflow" / "run a workflow" in your own words, or set `/effort ultracode` for automatic workflow planning across the session [[18]](https://code.claude.com/docs/en/workflows). `Workflow` is available in TypeScript Agent SDK v0.3.149+; include it in `allowedTools` to auto-approve.

## Hooks

Hooks are callback functions registered on agent events — block, modify, audit, or react without changing application logic [[9]](https://code.claude.com/docs/en/agent-sdk/hooks):

```python
async def protect_env_files(input_data, tool_use_id, context):
    file_path = input_data["tool_input"].get("file_path", "")
    if file_path.endswith(".env"):
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Cannot modify .env files",
        }}
    return {}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]}
)
```

Available hooks [[9]](https://code.claude.com/docs/en/agent-sdk/hooks):

| Hook                            | Python | TypeScript | Fires when                                              |
| ------------------------------- | :----: | :--------: | ------------------------------------------------------- |
| `PreToolUse`                    | ✓      | ✓          | Tool call about to execute — block, modify, or defer    |
| `PostToolUse`                   | ✓      | ✓          | Tool returned — inject context or replace output        |
| `PostToolUseFailure`            | ✓      | ✓          | Tool execution failed                                   |
| `PostToolBatch`                 | ✗      | ✓          | Full batch resolved — inject context once per batch     |
| `SubagentStart` / `SubagentStop`| ✓      | ✓          | Subagent spawned / completed                            |
| `PreCompact`                    | ✓      | ✓          | Conversation about to be summarized                     |
| `Notification`                  | ✓      | ✓          | Agent status events — forward to Slack, PagerDuty       |
| `PermissionRequest`             | ✓      | ✓          | Permission dialog would appear — custom handling        |
| `UserPromptSubmit`              | ✓      | ✓          | Prompt submission — inject additional context           |
| `MessageDisplay`                | ✗      | ✓          | Assistant message completes — redact/reformat display   |
| `SessionStart` / `SessionEnd`   | ✗ (SDK)| ✓          | Session lifecycle [[17]](https://code.claude.com/docs/en/agent-sdk/hooks) |

Multiple `PreToolUse` hooks run in parallel; `deny` wins over all other decisions [[9]](https://code.claude.com/docs/en/agent-sdk/hooks). Return `{}` to allow without change. Return `{async_: True, asyncTimeout: 30000}` (Python) / `{async: true}` (TypeScript) for fire-and-forget side effects (logging, webhooks) where the hook must not block the agent.

Matchers: exact tool name (`"Write"`), pipe-separated list (`"Write|Edit"`), regex (`"^mcp__"` matches all MCP tools), or omitted (matches all events of that type).

## Sessions

Sessions persist to `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`. Three continuation modes [[12]](https://code.claude.com/docs/en/agent-sdk/sessions):

| Mode       | How to use                              | When                                           |
| ---------- | --------------------------------------- | ---------------------------------------------- |
| `continue` | `continue=True` / `continue: true`      | Most recent session; no ID tracking needed     |
| `resume`   | `resume=session_id`                     | Specific session; required for multi-user apps |
| `fork`     | `fork_session=True` / `forkSession: true` | New branch from a session; original unchanged  |

Sessions store conversation history only — not filesystem state. For filesystem snapshots, use file checkpointing. To resume across machines (CI workers, containers), either ship the JSONL file to the same `cwd`-encoded path or extract the relevant results into the next prompt explicitly [[12]](https://code.claude.com/docs/en/agent-sdk/sessions).

TypeScript-only: `persistSession: false` keeps the session in memory only — useful for stateless single-turn tasks that should leave no disk artifacts.

## MCP Integration

Connect to external systems without custom auth or API management [[1]](https://code.claude.com/docs/en/agent-sdk/overview):

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]},
        "github":     {"command": "npx", "args": ["@modelcontextprotocol/server-github"]},
    }
)
```

The [MCP servers registry](https://github.com/modelcontextprotocol/servers) ⭐ 87k covers databases, browsers, Slack, GitHub, Asana, and hundreds more [[16]](https://github.com/modelcontextprotocol/servers). MCP tools are named `mcp__<server>__<action>` and can be targeted in hooks with the `^mcp__` regex matcher. Subagents can receive per-agent MCP server subsets via `AgentDefinition.mcpServers`.

## GitHub Actions

[anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) ⭐ 7.8k powers `@claude` mentions in PR/issue comments and scheduled automation [[11]](https://code.claude.com/docs/en/github-actions) [[14]](https://github.com/anthropics/claude-code-action):

```yaml
# .github/workflows/claude.yml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    prompt: "Review for security vulnerabilities"
    claude_args: "--max-turns 10 --model claude-opus-4-8"
```

All CLI flags pass via `claude_args`. Enterprise cloud: set `use_bedrock: "true"` + AWS OIDC, or `use_vertex: "true"` + GCP Workload Identity Federation for data-residency compliance [[11]](https://code.claude.com/docs/en/github-actions). GitHub Actions usage counts against the Agent SDK monthly credit (see Billing below).

Quick setup: run `/install-github-app` in Claude Code to configure the GitHub App and repository secrets automatically.

## SDK vs CLI vs Managed Agents

| | Agent SDK (`query()`) | CLI (`claude -p`) | Managed Agents (beta) |
|---|---|---|---|
| **Runs in**       | Your process          | Your process / CI runner | Anthropic-managed sandbox |
| **Interface**     | Python / TypeScript   | Shell command            | REST API                  |
| **Tool loop**     | SDK handles automatically | SDK handles automatically | Anthropic handles      |
| **Session state** | JSONL on your filesystem | JSONL on your filesystem | Anthropic-hosted       |
| **Custom tools**  | In-process functions  | Not directly             | You execute, return results |
| **Structured output** | `schema` option   | `--json-schema` flag     | SSE event stream          |
| **Subagents**     | `agents` param + `Agent` tool | Not directly  | Via Managed Agents API    |
| **Workflows**     | `Workflow` tool (TS v0.3.149+) | `ultracode` keyword | — |
| **Best for**      | Production automation, custom apps | Scripts, CI one-shot tasks | Long-running async, no-infra |

The typical progression: prototype with `query()` locally → automate via `claude -p` in CI → move long-running async sessions to Managed Agents when you don't want to operate sandbox infrastructure [[10]](https://platform.claude.com/docs/en/managed-agents/overview).

## Billing — June 15, 2026

Starting June 15, 2026, headless/SDK usage separates from interactive usage into a dedicated monthly credit [[13]](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan):

| Plan                     | Monthly SDK credit |
| ------------------------ | ------------------ |
| Pro                      | $20                |
| Max 5x                   | $100               |
| Max 20x                  | $200               |
| Team Standard seats      | $20                |
| Team Premium seats       | $100               |
| Enterprise Premium seats | $200               |

**Counts against credit:** `query()` API, `claude -p`, GitHub Actions integration, third-party apps authenticating via Agent SDK.

**Does not count:** Interactive Claude Code (TUI/IDE extensions), web/desktop/mobile chat.

Credits are per-user, refresh monthly, don't carry over. When exhausted, usage flows to API-rate usage credits at standard token rates. Interactive usage limits are unchanged.
