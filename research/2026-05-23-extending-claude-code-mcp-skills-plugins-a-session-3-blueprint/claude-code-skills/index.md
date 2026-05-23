---
title: "Claude Code Skills: what they are, when to use them"
date: 2026-05-23
depth: standard
format: md
topic: "Claude Code Skills"
topic_raw: "Claude Code Skills"
issue: 57
tags: [claude-code, agent-skills, ai-tools, anthropic, mcp]
summary: "A Skill is a Markdown file + optional bundled scripts that Claude loads on demand. Cheaper than CLAUDE.md, more discoverable than a slash command, lighter than a subagent — and now an open cross-vendor standard."
citations: 13
reading_time_min: 5
cover: cover.svg
cost_usd: 2.21
duration_sec: 393
---

> **TL;DR:** A Skill is a folder with `SKILL.md` (YAML frontmatter + Markdown body) plus optional scripts and reference files. Claude reads only the name/description until a task matches, then loads the body [[1]](https://code.claude.com/docs/en/skills). Use a **Skill** when the workflow has supporting files or you want auto-invocation; a **slash command** when the prompt is one file and triggered manually; **CLAUDE.md** for always-on rules; a **subagent** when you need an isolated context window [[5]](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/). Skills are an open standard — Cursor, Copilot, Codex, Gemini CLI, OpenHands and 30+ other agents implement the same `SKILL.md` format [[9]](https://agentskills.io).

## What a Skill actually is

[Anthropic](https://www.anthropic.com) announced Agent Skills on 16 October 2025 [[3]](https://simonwillison.net/2025/Oct/16/claude-skills/) and shipped them across Claude.ai, Claude Code, and the API [[4]](https://www.infoq.com/news/2025/10/anthropic-claude-skills/). Mechanically a skill is trivial: a directory containing `SKILL.md`, optionally extended with scripts, templates, and reference docs [[1]](https://code.claude.com/docs/en/skills).

The non-trivial part is **progressive disclosure** [[2]](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills):

1. **Discovery** — at startup the model sees only `name` + `description` (a few dozen tokens per skill) [[3]](https://simonwillison.net/2025/Oct/16/claude-skills/).
2. **Activation** — when the conversation matches the description, the full `SKILL.md` body is injected.
3. **Execution** — referenced files and bundled scripts load only if the body says to read them [[9]](https://agentskills.io).

This is why the official docs describe Skills as the right home for "a section of CLAUDE.md that has grown into a procedure rather than a fact" — CLAUDE.md pays the token cost every turn, a Skill pays it only when relevant [[1]](https://code.claude.com/docs/en/skills).

## Anatomy of a SKILL.md

```yaml
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
allowed-tools: Bash(git diff *) Bash(git status *)
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks
you notice such as missing error handling, hardcoded values, or tests that need
updating. If the diff is empty, say there are no uncommitted changes.
```

This is from the official "first skill" tutorial [[1]](https://code.claude.com/docs/en/skills). Three things make it more powerful than a slash command:

- **Dynamic context** — `` !`git diff HEAD` `` runs *before* Claude sees the skill; the placeholder is replaced by the command's stdout, so the model receives the live diff already inlined.
- **Pre-approved tools** — `allowed-tools` skips the per-call permission prompt while the skill is active [[1]](https://code.claude.com/docs/en/skills).
- **Auto-invocation** — Claude picks it up when the user just says "what did I change?", no slash needed.

[Nimbalyst's practical guide](https://nimbalyst.com/blog/claude-code-skills-guide/) — make the trigger an *activation condition*, not a capability list: "Lead with the use condition. 'Use this skill when [X].' The model parses this as a triage rule." [[6]](https://nimbalyst.com/blog/claude-code-skills-guide/).

## Frontmatter fields that matter

Only `description` is technically required. The rest are levers you reach for once a skill is non-trivial [[1]](https://code.claude.com/docs/en/skills):

| Field                      | Effect                                                                                       |
| :------------------------- | :------------------------------------------------------------------------------------------- |
| `description`              | The triage line. Capped at 1,536 chars in the listing — front-load the use condition.        |
| `disable-model-invocation` | `true` means only the user can fire it. For `/deploy`, `/commit`, anything with side effects.|
| `user-invocable`           | `false` hides it from the `/` menu. For background knowledge Claude should read but you wouldn't ever type. |
| `allowed-tools`            | Pre-approves tools while active (e.g. `Bash(git add *)`).                                    |
| `context: fork`            | Runs the skill in a subagent with isolated context. Pair with `agent: Explore` or `Plan`.    |
| `paths`                    | Glob — only auto-load when working with matching files (monorepo-friendly).                  |
| `model`, `effort`          | Per-skill overrides of the session model and effort level.                                   |

## Skills vs CLAUDE.md vs slash commands vs subagents

The four customization primitives overlap. [alexop.dev's breakdown](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/) draws the cleanest lines [[5]](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/):

| Tool             | Best for                              | Invocation                          | Context cost            | Isolation       |
| :--------------- | :------------------------------------ | :---------------------------------- | :---------------------- | :-------------- |
| **CLAUDE.md**    | Always-on project rules               | Automatic at startup                | Shares main window      | None            |
| **Slash command**| Explicit, repeatable workflows        | `/name` in terminal                 | Shares main window      | None            |
| **Skill**        | Auto-applied rich workflow + files    | Auto-triggered OR `/name`           | Description always; body on demand | None (unless `context: fork`) |
| **Subagent**     | Research-heavy, multi-step, isolation | Auto-delegated or via Task tool     | Separate window         | Full isolation  |

Two practical signals to reach for Skills specifically:

1. **You need to bundle scripts or templates** — slash commands are single-file; Skills are directories [[1]](https://code.claude.com/docs/en/skills).
2. **You want Claude to invoke it without being told** — Skills are auto-triggered, slash commands are not [[5]](https://alexop.dev/posts/claude-code-customization-guide-claudemd-skills-subagents/).

As of 2026 the two systems are partially unified: an existing `.claude/commands/foo.md` still creates `/foo`, but a Skill at `.claude/skills/foo/SKILL.md` does the same thing *and* adds supporting files and auto-invocation. The Skill wins on collision [[1]](https://code.claude.com/docs/en/skills).

## Where Skills live

Storage location determines scope and precedence [[1]](https://code.claude.com/docs/en/skills):

| Scope      | Path                                          | Applies to                |
| :--------- | :-------------------------------------------- | :------------------------ |
| Enterprise | Managed settings                              | All users in org          |
| Personal   | `~/.claude/skills/<name>/SKILL.md`            | All your projects         |
| Project    | `.claude/skills/<name>/SKILL.md`              | This project only         |
| Plugin     | `<plugin>/skills/<name>/SKILL.md`             | Wherever plugin is enabled|

Enterprise > personal > project on name conflicts. Plugin skills get a `plugin-name:skill-name` namespace so they cannot collide. Project skills are picked up from every `.claude/skills/` between the repo root and the current directory — monorepos can put package-specific skills under `packages/frontend/.claude/skills/` and they activate when you edit files there [[1]](https://code.claude.com/docs/en/skills).

## Bundled skills you get for free

Claude Code ships a set of prompt-based skills in every session [[1]](https://code.claude.com/docs/en/skills):

| Skill                | What it does                                                                          |
| :------------------- | :------------------------------------------------------------------------------------ |
| `/code-review`       | Multi-pass review of changed code                                                     |
| `/security-review`   | Vulnerability scan of pending changes                                                 |
| `/debug`             | Structured debugging protocol                                                         |
| `/loop`              | Run a prompt repeatedly on a schedule or self-paced                                   |
| `/claude-api`        | Build / debug / migrate Claude API code                                               |
| `/run`               | Launch and drive your app to see a change working                                     |
| `/verify`            | Build and run the app to confirm a change does what it should                         |
| `/run-skill-generator`| Records the per-project launch recipe as a Skill so `/run` and `/verify` stop guessing|

The `/run-skill-generator` pattern is worth highlighting: it bootstraps from a clean environment, captures the install + env + launch commands that actually worked, then commits the result as a per-project Skill — converting tribal knowledge into a versioned, agent-readable recipe [[1]](https://code.claude.com/docs/en/skills).

## The ecosystem in May 2026

The format is now cross-vendor. agentskills.io lists 30+ implementations — [Cursor](https://cursor.com), [GitHub Copilot](https://github.com), VS Code, [OpenAI Codex](https://developers.openai.com/codex), [Gemini CLI](https://geminicli.com), [OpenHands](https://openhands.dev), [Goose](https://block.github.io/goose/), Tabnine, Roo Code, and others all read the same `SKILL.md` [[9]](https://agentskills.io). Anthropic's own reference repo [anthropics/skills](https://github.com/anthropics/skills) ⭐ 140k (May 2026) holds the canonical PDF, DOCX, PPTX, XLSX, creative, and enterprise skills [[8]](https://github.com/anthropics/skills).

Community marketplaces have followed:

| Marketplace                                                                                       | Focus                                                                  | Stars                |
| :------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------------- | :------------------- |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)                   | 320+ skills, 70+ commands, 30+ agents; portable to Codex / Gemini / Cursor | ⭐ 16k [[10]](https://github.com/alirezarezvani/claude-skills) |
| [daymade/claude-code-skills](https://github.com/daymade/claude-code-skills)                       | Production-hardened fork of Anthropic's skill-creator                  | ⭐ 1.1k [[11]](https://github.com/daymade/claude-code-skills) |
| [mhattingpete/claude-skills-marketplace](https://github.com/mhattingpete/claude-skills-marketplace)| Engineering workflows: git automation, test fixing, code review        | ⭐ 585 [[13]](https://github.com/mhattingpete/claude-skills-marketplace) |
| [netresearch/claude-code-marketplace](https://github.com/netresearch/claude-code-marketplace)     | `marketplace.json` catalog pointing at source repos (source-reference pattern) | ⭐ 37 [[12]](https://github.com/netresearch/claude-code-marketplace) |

[Simon Willison](https://simonwillison.net) framed the shift bluntly: "I expect we'll see a Cambrian explosion in Skills which will make this year's MCP rush look pedestrian by comparison." [[3]](https://simonwillison.net/2025/Oct/16/claude-skills/). The star counts above suggest he was right.

## ⚠ Security: the ToxicSkills problem

The same low friction that makes Skills viral makes them a supply-chain target. [Snyk's ToxicSkills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) audit of skill registries found [[7]](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/):

- **36.82%** (1,467 skills) have at least one security flaw
- **13.4%** (534) contain a critical-level issue
- **100%** of confirmed malicious skills carry malicious code patterns
- **91%** of malicious skills *also* embed prompt injection to bypass the model's own safety checks

Three attack patterns dominate: external malware downloads, base64/Unicode-obfuscated data exfiltration, and instructions that disable safety mechanisms or plant persistence. The dynamic-context feature (`` !`cmd` ``) is the worst offender: commands run **before** the model ever sees the skill content, so model-level prompt-injection defenses never get a chance to fire [[7]](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/).

Practical mitigation:
- Review every project Skill before accepting the workspace trust dialog — `allowed-tools` is granted on trust [[1]](https://code.claude.com/docs/en/skills).
- For untrusted sources, set `"disableSkillShellExecution": true` in settings to neutralize `` !`cmd` `` placeholders [[1]](https://code.claude.com/docs/en/skills).
- Prefer the source-reference distribution pattern (marketplaces that pin to upstream commits) over copy-paste [[12]](https://github.com/netresearch/claude-code-marketplace).

## When a Skill beats an MCP server

[Simon Willison](https://simonwillison.net)'s argument for why Skills may displace many MCPs: "MCP is a whole protocol specification... skills are Markdown with a tiny bit of YAML metadata and some optional scripts... almost everything I might achieve with an MCP can be handled by a CLI tool instead." [[3]](https://simonwillison.net/2025/Oct/16/claude-skills/). Anthropic's own framing is gentler — Skills "complement" MCP by teaching agents *how* to use the tools MCP exposes [[2]](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).

A useful heuristic:

- **MCP server** when you need a long-lived stateful connection (a database, a SaaS API session, an auth handshake).
- **Skill** when the operation is a shell command, a Python script, or a procedural recipe — anything where "run this CLI, read the output" is enough.

The Skill is cheaper to build, cheaper to ship, cheaper to audit, and works across every agent that reads `SKILL.md` — not just the ones with an MCP client [[9]](https://agentskills.io).
