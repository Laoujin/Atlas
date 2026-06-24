---
title: "Smoke-testing a Claude Code subagent's routing before you ship it"
date: 2026-06-24
depth: standard
format: md
topic: "How to smoke-test a Claude Code subagent's routing before shipping to a team: verifying the parent dispatches on the right prompts, wrong prompts don't route to it, and the isolated context behaves (inputs, return shape, tool restrictions). Cover how the description drives delegation, techniques to assert dispatch (transcript/JSONL, --verbose, Agent SDK / headless claude -p structured output, OTel/hooks), and 2026 routing-test tooling."
topic_raw: "How to smoke-test a Claude Code subagent's routing before shipping it to a team."
tags: [claude-code, subagents, agent-sdk, testing, routing, promptfoo, observability]
summary: "Promptfoo's claude-agent-sdk provider plus headless stream-json are the only real ways to assert subagent routing in 2026; the description field is the trigger, parent_tool_use_id is the proof."
citations: 11
reading_time_min: 8
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 247
issue: 222
---

> **TL;DR.** There is no purpose-built "routing test runner" yet. The working recipe in 2026: drive your subagent headlessly with `claude -p --output-format stream-json --verbose` (or the Agent SDK) and assert on the `tool_use` block whose `name` is `Agent`/`Task` and its `subagent_type` [[1]](https://code.claude.com/docs/en/agent-sdk/subagents) — or, for a real test harness, use Promptfoo's `claude-agent-sdk` provider, which normalises dispatches into `metadata.toolCalls` and gives you a deterministic `skill-used` / `not-skill-used` assertion pair [[2]](https://www.promptfoo.dev/docs/providers/claude-agent-sdk/)[[3]](https://www.promptfoo.dev/docs/guides/test-agent-skills/). The `description` field is the only thing the router reads, so the routing test IS a description test [[4]](https://code.claude.com/docs/en/sub-agents). Write positive prompts, near-miss prompts that must route to a sibling, and assert both the agent you want and the ones you don't.

## What "routing works" actually decomposes into

The brief's three checks map to three different assertion surfaces:

| Check                                  | What you're really testing                          | Where the evidence lives                                              |
|----------------------------------------|-----------------------------------------------------|-----------------------------------------------------------------------|
| (a) right prompts → dispatch           | Is the `description` discoverable by the router?    | `tool_use` block, `name=Agent`, `subagent_type=<your-agent>` [[1]](https://code.claude.com/docs/en/agent-sdk/subagents) |
| (b) wrong prompts → no dispatch        | Is the `description` over-broad / stealing traffic? | absence of that `subagent_type`; a sibling's `subagent_type` instead [[3]](https://www.promptfoo.dev/docs/guides/test-agent-skills/) |
| (c) isolated context behaves           | Inputs arrived, shape returned, tools held          | the prompt string, `structured_output`, `permission_denials` [[5]](https://code.claude.com/docs/en/agent-sdk/structured-outputs)[[1]](https://code.claude.com/docs/en/agent-sdk/subagents) |

(a) and (b) are deterministic given a transcript. (c) is partly deterministic (tool restrictions, output schema) and partly probabilistic (did the model use the inputs well) — only the deterministic half is in scope here.

## The `description` is the trigger, not documentation

Claude uses each subagent's `description` to decide when to delegate; you write it so "Claude knows when to use it" [[4]](https://code.claude.com/docs/en/sub-agents). In the SDK the same field is "Natural language description of when to use this agent" and is the only routing signal besides the prompt and current context [[1]](https://code.claude.com/docs/en/agent-sdk/subagents). Three dispatch paths exist, and your smoke test must distinguish them:

- **Automatic** — the router matches the task to a `description`. This is the only path worth testing; the other two bypass the thing you're verifying.
- **Explicit by name / @-mention** — "Use the code-reviewer agent to…" bypasses automatic matching [[1]](https://code.claude.com/docs/en/agent-sdk/subagents). Useful as a *positive control* (proves the agent runs at all), useless for testing routing.
- **`general-purpose` fallback** — Claude can spawn the built-in `general-purpose` agent without you defining anything, so an absent dispatch to your agent doesn't mean no delegation happened [[1]](https://code.claude.com/docs/en/agent-sdk/subagents).

Anthropic's own troubleshooting list for "Claude not delegating" is, in effect, the failure taxonomy your smoke test should cover: `Agent` not in `allowedTools` (invocation denied), no explicit prompting, or a vague `description` [[1]](https://code.claude.com/docs/en/agent-sdk/subagents). Filesystem agents in `.claude/agents/` load **at startup only** — edit the description, restart the session, or your test runs the old one [[1]](https://code.claude.com/docs/en/agent-sdk/subagents).

## (a) Asserting the dispatch happened

### Naming caveat that breaks naive greps (2026)

The dispatch tool was renamed `Task` → `Agent` in Claude Code **v2.1.63**. Current SDKs emit `"Agent"` in `tool_use` blocks but still say `"Task"` in the `system:init` tools list and in `result.permission_denials[].tool_name` — so any assertion must match **both** strings [[1]](https://code.claude.com/docs/en/agent-sdk/subagents). As of **v2.1.172**, subagents can spawn subagents (depth-limited to 5), which means a dispatch can be nested rather than top-level [[1]](https://code.claude.com/docs/en/agent-sdk/subagents).

### Technique comparison

| Technique                              | Determinism | CI-able | What you assert on                                                              | Cost  |
|----------------------------------------|-------------|---------|---------------------------------------------------------------------------------|-------|
| Interactive `--verbose` / transcript   | manual      | ✗       | eyeball the "delegating to X" line                                              | low   |
| Headless `claude -p` stream-json + jq  | high        | ✓       | `tool_use.name ∈ {Agent,Task}`, `.input.subagent_type` [[6]](https://takopi.dev/reference/runners/claude/stream-json-cheatsheet/) | low   |
| Agent SDK message loop                 | high        | ✓       | `block.name`, `block.input.subagent_type`, `parent_tool_use_id` [[1]](https://code.claude.com/docs/en/agent-sdk/subagents) | low   |
| Promptfoo `claude-agent-sdk` provider  | high        | ✓       | `metadata.toolCalls`, `skill-used` / `not-skill-used` [[2]](https://www.promptfoo.dev/docs/providers/claude-agent-sdk/)[[3]](https://www.promptfoo.dev/docs/guides/test-agent-skills/) | med   |
| OpenTelemetry traces / hooks           | high        | ✓ (obs) | nested `claude_code.tool` span, `tool_name=Task` [[7]](https://generalanalysis.com/guides/claude-code-control-observability-opentelemetry) | infra |

### Headless: the cheapest CI gate

```bash
claude -p --output-format stream-json --verbose \
  "Refactor the auth module for clarity" \
  > run.jsonl
# stream-json REQUIRES --verbose, else you get minimal output
```

Each line is one JSON event with a `type` field [[6]](https://takopi.dev/reference/runners/claude/stream-json-cheatsheet/). Find the dispatch:

```bash
jq -c 'select(.type=="assistant") | .message.content[]
       | select(.type=="tool_use" and (.name=="Task" or .name=="Agent"))
       | {agent: .input.subagent_type}' run.jsonl
```

The `subagent_type` in the `tool_use.input` is the agent the router chose — that string is your pass/fail [[1]](https://code.claude.com/docs/en/agent-sdk/subagents)[[6]](https://takopi.dev/reference/runners/claude/stream-json-cheatsheet/). Messages produced *inside* a subagent carry `parent_tool_use_id`, so you can prove work ran in the isolated context, not the parent [[1]](https://code.claude.com/docs/en/agent-sdk/subagents).

### Agent SDK: assert in TS/Python

The SDK docs ship a near-verbatim routing probe — iterate the stream, match `block.name in ("Task","Agent")`, read `block.input.subagent_type`, and flag any message with a `parent_tool_use_id` as "running inside subagent" [[1]](https://code.claude.com/docs/en/agent-sdk/subagents). Wrap that in your test runner (xUnit/Vitest) and you have a routing assertion in the stack your team already tests with. Define the agent inline via the `agents` param so the test is self-contained and not dependent on `.claude/agents/` files [[1]](https://code.claude.com/docs/en/agent-sdk/subagents).

### Promptfoo: the closest thing to a routing-test framework

Promptfoo's `claude-agent-sdk` provider ([promptfoo](https://github.com/promptfoo/promptfoo) ⭐ 23k, Jun 2026) captures every dispatch in `response.metadata.toolCalls`; each entry has `name`, `input`, and a `parentToolUseId` that is **non-null for subagent calls** and `null` for top-level — that field alone proves a subagent ran [[2]](https://www.promptfoo.dev/docs/providers/claude-agent-sdk/)[[8]](https://github.com/promptfoo/promptfoo). By default only `tool_use`/`tool_result` blocks from the subagent surface; set `forward_subagent_text: true` to assert against the nested transcript [[2]](https://www.promptfoo.dev/docs/providers/claude-agent-sdk/). For Skills (the sibling extension type), it normalises `Skill` calls into `metadata.skillCalls` and exposes a deterministic `skill-used` assertion [[2]](https://www.promptfoo.dev/docs/providers/claude-agent-sdk/).

A JS assertion that a *specific* agent was dispatched:

```javascript
const calls = context.providerResponse?.metadata?.toolCalls || [];
return calls.some(t =>
  (t.name === 'Agent' || t.name === 'Task') &&
  t.input?.subagent_type === 'code-reviewer');
```

## (b) Asserting wrong prompts DON'T route

This is the half teams skip, and it's where an over-eager `description` does its damage — a greedy agent silently eats prompts meant for a sibling. Promptfoo's guide names the pattern directly: add near-miss prompts that *should* route to a sibling, then **assert both the agent you want and the ones you don't** [[3]](https://www.promptfoo.dev/docs/guides/test-agent-skills/).

```yaml
tests:
  - description: Eval authoring stays out of provider setup
    vars:
      request: Write a regression eval for this existing provider.
    assert:
      - type: skill-used
        value: promptfoo-evals
      - type: not-skill-used
        value: promptfoo-provider-setup
```

The same dual assertion expresses in raw `metadata.toolCalls`: assert your `subagent_type` is **absent** (or a named sibling is present) for the near-miss corpus. The guide's third layer matters too: confirm the chosen agent *changed the actual work*, not just the trace — a correct-by-accident answer from the wrong agent still fails the intent [[3]](https://www.promptfoo.dev/docs/guides/test-agent-skills/).

Build the corpus as three buckets per agent: **positive** (must dispatch), **near-miss** (must dispatch to a named sibling), **unrelated** (must not dispatch at all). Routing is probabilistic, so run each prompt N times and gate on a hit-rate, not a single pass — single-shot routing assertions are flaky by construction.

## (c) Verifying the isolated context behaves

### Inputs arrived

The **only** channel from parent to subagent is the Agent tool's prompt string — no parent history, no parent system prompt, no preloaded skills unless listed in `AgentDefinition.skills` [[1]](https://code.claude.com/docs/en/agent-sdk/subagents). So the test for "did it get what it needs" is: inspect the `tool_use.input.prompt` the parent generated and assert your required file paths / error text / IDs are literally in it. If they're not, the bug is in the *parent's* dispatch prompt, not your agent.

### Return shape

Free-form text is unassertable. Pin the contract with structured outputs: pass `outputFormat: { type: "json_schema", schema }` (TS) / `output_format` (Python); the result message then carries a validated `structured_output` field, and the SDK re-prompts on mismatch [[5]](https://code.claude.com/docs/en/agent-sdk/structured-outputs). Generate the schema from Zod (`z.toJSONSchema()`) or Pydantic (`.model_json_schema()`) so the test shares the type your code uses [[5]](https://code.claude.com/docs/en/agent-sdk/structured-outputs). On failure the result `subtype` is `error_max_structured_output_retries` — a clean red/green for "agent returned the expected shape" [[5]](https://code.claude.com/docs/en/agent-sdk/structured-outputs).

⚠ **Caveat:** structured output binds the *top-level* `query()`, which is the cleanest path when you test the agent as a **main-thread** agent. When it runs as a true subagent, assert the shape of the verbatim final message the parent receives (the Agent tool result) instead.

### Tool restrictions hold

A subagent restricted via `tools: ["Read","Grep","Glob"]` (or `disallowedTools`) should never execute Edit/Write/Bash [[1]](https://code.claude.com/docs/en/agent-sdk/subagents). Negative test: feed it a prompt that *tempts* a write and assert the result's `permission_denials` contains the blocked tool (the SDK still labels these with the legacy `Task` name) [[1]](https://code.claude.com/docs/en/agent-sdk/subagents). Belt-and-braces: a `SubagentStop` / `PostToolUse` hook can hard-fail the run if an out-of-scope tool or file write slips through, turning the policy into an enforced gate rather than a hope.

## Observability for fleet-level routing

For a shipped agent, OpenTelemetry watches routing in production, not just in CI. Set `CLAUDE_CODE_ENABLE_TELEMETRY=1`; subagent `llm_request` and tool spans nest under the parent's `claude_code.tool` span, so the whole delegation chain is one trace and a dispatch surfaces as a span with `tool_name=Task` [[7]](https://generalanalysis.com/guides/claude-code-control-observability-opentelemetry). Hooks give the same signal cheaper: a `PreToolUse`/`PostToolUse` hook keyed on `tool_name=task` fires on every dispatch and can log or block it [[7]](https://generalanalysis.com/guides/claude-code-control-observability-opentelemetry). The official observability doc covers the metrics/events/traces split [[9]](https://code.claude.com/docs/en/agent-sdk/observability). Treat this as monitoring, not a pre-ship gate — it tells you routing drifted *after* it drifted.

## Honest state of tooling, June 2026

- **No dedicated routing-test framework exists.** Promptfoo's `claude-agent-sdk` provider is the only off-the-shelf harness with first-class dispatch/skill assertions [[2]](https://www.promptfoo.dev/docs/providers/claude-agent-sdk/); everything else is you-write-the-jq. If someone claims a "subagent router unit-test tool", be skeptical.
- ⚠ **Active regression that breaks transcript-based assertions.** [anthropics/claude-code#17591](https://github.com/anthropics/claude-code/issues/17591) ([claude-code](https://github.com/anthropics/claude-code) ⭐ 134k): since **v2.0.77** (filed 12 Jan 2026, still open) `TaskOutput` returns the raw JSONL session transcript instead of the subagent's summary, flooding parent context [[10]](https://github.com/anthropics/claude-code/issues/17591). If your assertion parses `TaskOutput`, pin to ≤2.0.76 or read the dispatch from the `tool_use` block instead of the result.
- **Reverse-engineered router internals.** [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) ⭐ 11k mirrors the Agent/Task tool description and built-in subagent prompts per version — useful to see *what text the router actually matches your description against* [[11]](https://github.com/Piebald-AI/claude-code-system-prompts).
- **Routing is non-deterministic.** Every assertion above should gate on a hit-rate over N runs, with explicit positive/near-miss/unrelated buckets. A single green run is not evidence the routing is robust.
