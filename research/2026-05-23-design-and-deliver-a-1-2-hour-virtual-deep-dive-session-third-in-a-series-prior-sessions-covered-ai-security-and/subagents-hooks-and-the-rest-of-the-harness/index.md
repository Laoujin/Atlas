---
title: "Subagents, hooks, and the rest of the harness"
date: 2026-05-23
depth: ceo
format: md
topic: "Subagents, hooks, and the rest of the harness"
topic_raw: "Subagents, hooks, and the rest of the harness"
issue: 57
tags: [claude-code, harness, subagents, hooks, skills, talk-prep]
summary: "One-page mental model for teaching Claude Code's harness: subagents (isolation), hooks (determinism), and the config substrate (skills, permissions, settings)."
citations: 6
reading_time_min: 2
cover: cover.svg
cost_usd: 1.19
duration_sec: 219
---

> **TL;DR.** Three primitives compose the Claude Code harness. **Subagents** give you *isolation* — fresh context, scoped tools, optional cheaper model [[1]](https://code.claude.com/docs/en/sub-agents). **Hooks** give you *determinism* — shell/HTTP/MCP/prompt/agent callbacks fired at ~30 lifecycle events, with `PreToolUse` the only one that can block [[2]](https://code.claude.com/docs/en/hooks). **Settings, permissions, and skills** are the *substrate* the model runs on [[3]](https://code.claude.com/docs/en/settings)[[4]](https://code.claude.com/docs/en/skills). Teach the audience to ask: *is this a context problem, a determinism problem, or a defaults problem?* — that's how they pick the layer.

## 1. Subagents — isolation

A subagent runs in its own context window with its own system prompt, tool allowlist, and model [[1]](https://code.claude.com/docs/en/sub-agents). Reach for one when a side task would flood the main context (long search, log scrape, doc fetch) or when you keep re-spawning the same kind of worker. Built-ins: `Explore`, `Plan`, `general-purpose`. Custom subagents live in `.claude/agents/*.md` and Claude picks them by their `description` field. Cost lever: route cheap work to Haiku via `model:` in frontmatter [[1]](https://code.claude.com/docs/en/sub-agents). The community has ~100 ready-made specs at [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) ⭐ 20k (May 2026) [[5]](https://github.com/VoltAgent/awesome-claude-code-subagents) — good to crib from.

## 2. Hooks — determinism around the model

Hooks turn "best practice" into enforced rules. They are command/HTTP/MCP/prompt/agent callbacks fired on lifecycle events: `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`, `Stop`, `SubagentStop`, `PreCompact`, `FileChanged`, plus ~20 more [[2]](https://code.claude.com/docs/en/hooks). **Only `PreToolUse` blocks** — exit code 2 stops the tool call and shows stderr to Claude [[2]](https://code.claude.com/docs/en/hooks). Configured in `settings.json` under `hooks.<event>` with a tool-name matcher and an optional `if` permission rule (e.g. `Bash(rm *)`). Canonical uses: block `rm -rf`, run a linter after every Edit, inject context at `SessionStart`.

## 3. The rest — settings, permissions, skills

`settings.json` cascades across five tiers (managed > CLI > local > project > user); permission `allow`/`ask`/`deny` arrays merge across tiers, other keys override [[3]](https://code.claude.com/docs/en/settings). Permission modes (`default`, `acceptEdits`, `plan`, `auto`, `bypassPermissions`) set the session-wide posture [[3]](https://code.claude.com/docs/en/settings). **Skills** are the model-invokable cousin of subagents: a `SKILL.md` with frontmatter that Claude loads when relevant or you call as `/skill-name`; custom commands are now skills under the hood [[4]](https://code.claude.com/docs/en/skills). Skills with `context: fork` *run inside a subagent* — that's the bridge: skill = what to do, subagent = where it runs [[4]](https://code.claude.com/docs/en/skills). The community frame for the whole layered stack is "harness engineering" — turning Claude from a capable assistant into a team member that already knows the project's conventions [[6]](https://restato.github.io/blog/harness-engineering-guide-claude-code/).

## Suggested 60–90 min demo flow

| # | Demo                                                                                                                              | Reinforces                                                                                  |
|:--|:----------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------|
| 1 | Create `.claude/agents/db-explorer.md` with `tools: Read, Grep` and `model: claude-haiku-4-5`; ask main session a delegable task. | Subagent isolation + cost routing [[1]][s1]                                                 |
| 2 | Add a `PreToolUse` hook on `Bash` with `if: "Bash(rm -rf *)"` that exits 2; try to delete a file.                                 | Hook as blocking gate [[2]][s2]                                                             |
| 3 | Write `.claude/skills/commit/SKILL.md` with `allowed-tools: Bash(git *)` and `disable-model-invocation: true`; invoke `/commit`.  | Skills, pre-approved tools, user-only invocation [[4]][s4]                                  |
| 4 | Drop a project-scope `deny` rule into `.claude/settings.json`; show it overriding a user-scope `allow`.                           | Settings cascade and permission merge [[3]][s3]                                             |

[s1]: https://code.claude.com/docs/en/sub-agents
[s2]: https://code.claude.com/docs/en/hooks
[s3]: https://code.claude.com/docs/en/settings
[s4]: https://code.claude.com/docs/en/skills

## Talking points to land

- The three layers are *orthogonal*: a hook can fire on a subagent's tool call; a skill can run *inside* a subagent via `context: fork` [[4]](https://code.claude.com/docs/en/skills).
- Hooks are the *only* harness layer that runs deterministically — everything else still routes through the model's judgement [[2]](https://code.claude.com/docs/en/hooks).
- Permission merges are subtle: `deny` from any tier wins; `allow` from a higher tier doesn't override a lower-tier `deny` [[3]](https://code.claude.com/docs/en/settings).
- Subagents save tokens; skills save tokens *and* keystrokes; hooks save trust [[1]](https://code.claude.com/docs/en/sub-agents)[[2]](https://code.claude.com/docs/en/hooks)[[4]](https://code.claude.com/docs/en/skills).
