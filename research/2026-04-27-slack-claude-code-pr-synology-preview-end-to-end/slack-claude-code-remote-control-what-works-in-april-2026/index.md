---
title: "Slack ↔ Claude Code remote control: what works in April 2026"
date: 2026-04-27
depth: deep
format: md
topic: "Slack ↔ Claude Code remote control"
topic_raw: "Slack ↔ Claude Code remote control"
issue: 17
tags: [claude-code, slack, chatops, agents, remote-control, mcp, devops]
summary: How Anthropic's first-party Slack integration, OSS bridges, and competing surfaces (Cursor, Codex, Devin) compare for driving Claude Code from chat — with the security patterns teams converge on.
citations: 65
reading_time_min: 9
cover: cover.svg
cost_usd: 7.99
duration_sec: 896
---

> **Decision.** If you're on Pro/Max with GitHub repos and want zero ops, use Anthropic's first-party **Claude Code in Slack** — the @mention routes to a sandboxed claude.ai/code session [[1]](https://code.claude.com/docs/en/slack). If you need GitLab, local-only repos, or to keep the runtime on your own machine and quota, deploy [chenhg5/cc-connect](https://github.com/chenhg5/cc-connect) ⭐ 6.4k (Apr 2026) [[7]](https://github.com/chenhg5/cc-connect) for a multi-platform bridge or [jeremylongshore/claude-code-slack-channel](https://github.com/jeremylongshore/claude-code-slack-channel) ⭐ 15 [[10]](https://github.com/jeremylongshore/claude-code-slack-channel) for the security-hardened pattern. If "I want to ship code from Slack" is the only requirement and Claude isn't a hard pin, **[Cursor](https://cursor.com) Background Agents** [[58]](https://cursor.com/changelog/1-1) or **[OpenAI Codex](https://openai.com/codex) Slack** [[60]](https://developers.openai.com/codex/integrations/slack) are equally credible — both run on vendor cloud VMs instead of your laptop.

## 1. The official surface: Claude Code in Slack

Anthropic launched **Claude Code in Slack** as a research preview on December 8, 2025 [[4]](https://techcrunch.com/2025/12/08/claude-code-is-coming-to-slack-and-thats-a-bigger-deal-than-it-sounds/), built on the existing **Claude for Slack** app [[1]](https://code.claude.com/docs/en/slack)[[2]](https://claude.com/claude-for-slack). Mention `@Claude` with a coding task in a channel where you've run `/invite @Claude`, and the app's intent classifier routes the request to a remote Claude Code session on the web — the Slack thread itself never executes code [[1]](https://code.claude.com/docs/en/slack). What lives in the channel is status updates, a completion summary, and Block Kit action buttons (View Session, Create PR, Retry as Code, Change Repo) [[1]](https://code.claude.com/docs/en/slack).

| Constraint | Detail |
|---|---|
| Plan | Pro / Max / Team / Enterprise with Claude Code seats [[1]](https://code.claude.com/docs/en/slack) |
| Repo support | ⚠ GitHub only — issue [#21527](https://github.com/anthropics/claude-code/issues/21527) tracks GitLab/Bitbucket [[17]](https://github.com/anthropics/claude-code/issues/21527) |
| Surface | Channels only, no DMs [[26]](https://everydayaiblog.com/claude-code-slack-integration/) |
| Output | One PR per session [[26]](https://everydayaiblog.com/claude-code-slack-integration/) |
| Runtime | Anthropic-managed sandbox under the invoking user's quota [[1]](https://code.claude.com/docs/en/slack) |
| Slack scopes | Broad "perform actions as you" across channels, conversations, workspace [[3]](https://slack.com/marketplace/A08SF47R6P4-claude) |

The Slack message *is the trigger*, not the dialog. Builder.io's review puts it bluntly: "Slack isn't the real 'dialog' surface … it's mainly to kick off the web-based Claude Code session" [[25]](https://www.builder.io/blog/claude-code-slack). Two consequences: you can't preview frontend changes from chat, and complex refactors still want the web/IDE [[25]](https://www.builder.io/blog/claude-code-slack)[[26]](https://everydayaiblog.com/claude-code-slack-integration/).

## 2. OSS bridges: which ones to actually consider

The OSS landscape splits into one clear leader, four credible mid-tier projects, and a long tail of solo experiments. Star counts as of April 2026.

| Project | ⭐ Stars | Last push | Transport | Niche |
|---|---|---|---|---|
| [chenhg5/cc-connect](https://github.com/chenhg5/cc-connect) | ⭐ 6.4k | 2026-04-27 | Socket Mode + 6 other platforms | Multi-agent (Claude Code, Cursor, Gemini, Codex) → Slack/Telegram/Discord/Feishu/DingTalk/LINE/WeChat. [[7]](https://github.com/chenhg5/cc-connect) |
| [mpociot/claude-code-slack-bot](https://github.com/mpociot/claude-code-slack-bot) | ⭐ 157 | 2025-06-27 | Socket Mode | ⚠ Single-commit repo, effectively abandoned. Streaming + MCP passthrough. [[8]](https://github.com/mpociot/claude-code-slack-bot) |
| [tomeraitz/claude-slack-bridge](https://github.com/tomeraitz/claude-slack-bridge) | ⭐ 21 | 2026-04-27 | MCP server | Human-in-the-loop pattern: Claude blocks at the kernel level until a Slack reply arrives. One Docker container serves all projects. [[9]](https://github.com/tomeraitz/claude-slack-bridge) [[16]](https://dev.to/tomeraitz/now-you-can-talk-to-claude-in-the-middle-of-the-task-506j) |
| [jeremylongshore/claude-code-slack-channel](https://github.com/jeremylongshore/claude-code-slack-channel) | ⭐ 15 | 2026-04-27 | Socket Mode + MCP stdio | Security-hardened: hash-chained audit journal, five-layer prompt-injection defense, policy-gated MCP tools. Requires Claude Code 2.1.80+. [[10]](https://github.com/jeremylongshore/claude-code-slack-channel) |
| [yuya-takeyama/cc-slack](https://github.com/yuya-takeyama/cc-slack) | ⭐ 14 | 2025-08-23 | HTTP webhooks | Go, MIT. `/cc` slash command opens a modal for working directory + initial prompt. [[11]](https://github.com/yuya-takeyama/cc-slack) |
| [41fred/claude-code-slack](https://github.com/41fred/claude-code-slack) | ⭐ 15 | 2026-02-20 | Local daemon + Railway worker | Splits Slack-facing component to a public PaaS so Claude Code stays local. Python, MIT. [[12]](https://github.com/41fred/claude-code-slack) |
| [AnandChowdhary/claude-code-slack-bot](https://github.com/AnandChowdhary/claude-code-slack-bot) | ⭐ 11 | 2025-09-04 | GitHub Action wrapper | Turns Slack feature requests into GitHub issues with auto-implementation PRs. [[13]](https://github.com/AnandChowdhary/claude-code-slack-bot) |

Stalled-but-cited: [engineers-hub-ltd/slack-claude-code-integration](https://github.com/engineers-hub-ltd-in-house-project/slack-claude-code-integration) ⭐ 11 (no commits in 10 months) [[14]](https://github.com/engineers-hub-ltd-in-house-project/slack-claude-code-integration), [106-/claude-code-slack-agent](https://github.com/106-/claude-code-slack-agent) ⭐ 1 [[15]](https://github.com/106-/claude-code-slack-agent). The recurring driver across all of them is issue #21527 — the OSS projects exist mostly to cover non-GitHub repos and local workspaces [[17]](https://github.com/anthropics/claude-code/issues/21527).

## 3. Technical patterns: how a bridge actually works

Four layers, each with a binary choice:

**Slack → bridge transport**

| Choice | When |
|---|---|
| **Socket Mode** (outbound WebSocket, no public IP) | Default for security-conscious bridges (cc-connect [[7]](https://github.com/chenhg5/cc-connect), mpociot's bot [[8]](https://github.com/mpociot/claude-code-slack-bot), claude-code-slack-channel [[10]](https://github.com/jeremylongshore/claude-code-slack-channel)). No HMAC verification needed. |
| **HTTP webhooks** (`/slack/events`, `/slack/interactive`, `/slack/commands`) | When the bridge already runs on a public URL (cc-slack [[11]](https://github.com/yuya-takeyama/cc-slack), Cloudflare Worker patterns). Requires HMAC-SHA256 signing-secret check + 300s replay window [[34]](https://docs.slack.dev/authentication/verifying-requests-from-slack/). |

**Bridge → Claude Code driver**

| Choice | Detail |
|---|---|
| **CLI headless** | `claude -p "<prompt>" --output-format stream-json --include-partial-messages` for token-by-token streaming back to Slack [[18]](https://code.claude.com/docs/en/headless). |
| **Claude Agent SDK** | Python `claude-agent-sdk` 0.1.48 ⭐ 6.6k or TypeScript `@anthropic-ai/agent-sdk` 0.2.71 ⭐ 1.3k. Same agent loop as Claude Code, embeddable in a Bolt async handler [[19]](https://platform.claude.com/docs/en/agent-sdk/overview)[[20]](https://github.com/anthropics/claude-agent-sdk-python/releases). |

**Session continuity**

Map a Slack thread `ts` → `--session-id` captured from JSON output, replay with `--resume <id>`. cc-slack auto-resumes when a user replies in the same thread [[11]](https://github.com/yuya-takeyama/cc-slack). Without this you spawn-per-message and lose all context.

**Approvals without a TTY**

| `--permission-mode` | Behaviour | Use for |
|---|---|---|
| `default` | Interactive prompts | Local terminal, useless headless |
| `acceptEdits` | Auto-accepts file edits, prompts for shell | Light unattended |
| `plan` | Plan-only, no execution | Dry-run from chat |
| `auto` | Background classifier blocks force-pushes, `curl \| bash`, IAM changes [[42]](https://www.anthropic.com/engineering/claude-code-auto-mode) | Recommended replacement for `--dangerously-skip-permissions` |
| `dontAsk` | Only pre-approved tools, fully non-interactive [[24]](https://code.claude.com/docs/en/permission-modes) | Locked-down CI / Slack bridges |
| `bypassPermissions` (= `--dangerously-skip-permissions`) | Everything except protected paths | ⚠ Isolated containers / VMs only [[24]](https://code.claude.com/docs/en/permission-modes)[[42]](https://www.anthropic.com/engineering/claude-code-auto-mode) |

The `Notification` and `PreToolUse` hooks are the two server-side wires. `Notification` fires when Claude is waiting for input or permission — community bridges use it to push "awaiting approval" or "task complete" cards into Slack via webhook `curl` [[21]](https://code.claude.com/docs/en/hooks-guide). As of March 2026, hooks support four handler types (`command`, `http`, `prompt`, `agent`) and an `async: true` flag to fire-and-forget without blocking the agent [[22]](https://smartscope.blog/en/generative-ai/claude/claude-code-hooks-guide/).

**MCP cuts both ways**

- **Slack as MCP server consumed by Claude Code** — Slack ships an official MCP server at `https://mcp.slack.com/mcp` (OAuth, HTTP transport). Install via `/plugin install slack` to give Claude search/read/send/canvas tools [[23]](https://docs.slack.dev/ai/slack-mcp-server/connect-to-claude/).
- **Claude Code reachable *via* MCP from Slack** — `tomeraitz/claude-slack-bridge` exposes an `ask_on_slack` MCP tool so Claude pauses mid-task, asks a question in Slack, and resumes when the reply lands [[9]](https://github.com/tomeraitz/claude-slack-bridge)[[16]](https://dev.to/tomeraitz/now-you-can-talk-to-claude-in-the-middle-of-the-task-506j).

## 4. Operator reality: bugs, costs, and what people complain about

Two structurally painful Anthropic-side bugs hit Slack bridges hardest:

- **Issue [#36833](https://github.com/anthropics/claude-code/issues/36833)** — `claude -p` headless silently drops Claude AI connector MCP tools (including the Slack connector). Anything `mcp__claude_ai_Slack__*` returns NOT_FOUND under cron / LaunchAgent / CI [[27]](https://github.com/anthropics/claude-code/issues/36833).
- **Issue [#30333](https://github.com/anthropics/claude-code/issues/30333)** — long-running headless SDK sessions with parallel subagents can hang because the Stop hook check finds zero hooks and never emits a `ResultMessage` line. Slack listeners stall without an error [[28]](https://github.com/anthropics/claude-code/issues/30333).

**Cost blowups** were the loudest March-2026 complaint. Max users reported 5-hour windows burned in ~90 minutes on previously-stable workloads [[29]](https://www.macrumors.com/2026/03/26/claude-code-users-rapid-rate-limit-drain-bug/), fresh sessions at 3% context returning "out of extra usage" [[31]](https://github.com/anthropics/claude-code/issues/41424), and Anthropic publicly conceded it tightened peak-hour caps such that ~7% more users now hit limits [[32]](https://www.theregister.com/2026/03/31/anthropic_claude_code_limits/). Unattended Slack-driven sessions amplify this — nobody's watching when the loop blows up.

**Latency budget for phone-from-Slack**: 200–500 ms best-case round-trip phone → relay → local box, "potentially several seconds on congested cellular" [[33]](https://blog.laozhang.ai/en/posts/remote-control-claude-code) — fine for kickoff, painful for chained approval prompts.

**The realistic away-from-desk pattern**: tmux + launchctl + 1-minute Slack polling, hand-rolled [[30]](https://samwize.com/2026/03/14/how-i-got-claude-code-to-monitor-slack-while-i-was-on-holiday/). It works, but you maintain the scaffolding.

## 5. Hardening: what you must do before pointing Slack at a code-editing agent

The 2025–2026 vulnerability disclosures make defence-in-depth non-optional:

- **CVE-2025-59536** (CVSS 8.7) — opening an attacker-controlled repo auto-fires `.claude/settings.json` hooks, auto-loads `.mcp.json` MCP servers, and can override `ANTHROPIC_BASE_URL` to ship the API key in plaintext to the attacker before any trust prompt [[37]](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/)[[38]](https://thehackernews.com/2026/02/claude-code-flaws-allow-remote-code.html).
- **CVE-2025-54794 / 54795** — path-restriction bypass and command injection [[38]](https://thehackernews.com/2026/02/claude-code-flaws-allow-remote-code.html).
- **CVE-2026-39861** (patched in 2.1.64) — sandbox escape via symlinks pointing outside the workspace [[40]](https://www.sentinelone.com/vulnerability-database/cve-2026-39861/).
- **50-subcommand deny-rule bypass** — `bashPermissions.ts` caps deny-rule evaluation at 50 piped subcommands; chain more and Claude falls back to "ask" instead of blocking [[39]](https://www.scworld.com/brief/claude-code-vulnerable-to-prompt-injection-due-to-subcommand-limit).
- **Mitiga's Slack-via-Skill worm** — a malicious Skill installed by an unsuspecting developer inherits the Slack identity, exfiltrates, and propagates. Conventional EDR/SIEM can't see what happens inside Slack [[41]](https://www.mitiga.io/blog/007-license-to-skill-p-2-slack-compromise-through-claude-code).

The converged practitioner pattern, distilled across Anthropic's docs and the hardened community bridges:

| Layer | Pattern |
|---|---|
| **Slack edge** | Prefer Socket Mode (no public URL). If using webhooks: HMAC-SHA256 verify with 300s replay window + constant-time comparison [[34]](https://docs.slack.dev/authentication/verifying-requests-from-slack/). Channel + user allow-lists; ungated messages dropped before reaching Claude [[50]](https://github.com/jeremylongshore/claude-code-slack-channel/blob/main/README.md). Tokens never in repos, minimum scopes [[35]](https://docs.slack.dev/authentication/best-practices-for-security/). |
| **Claude permission layer** | `--permission-mode auto` not `bypassPermissions` for chat-driven runs [[42]](https://www.anthropic.com/engineering/claude-code-auto-mode). ⚠ Trust verification is **disabled** under `-p` headless [[46]](https://code.claude.com/docs/en/security) — the bridge must replace it with its own gate. |
| **PreToolUse hooks** | The one enforcement layer the agent can't talk past. Deny via `permissionDecision: "deny"` or exit code 2; admins use `allowManagedHooksOnly` to lock policy [[47]](https://code.claude.com/docs/en/hooks). |
| **Sandbox** | Anthropic's secure-deployment guide formalises: `--cap-drop ALL`, `--security-opt no-new-privileges`, `--read-only`, `--network none`, mount code read-only, reach the outside world only through a Unix-socket-attached proxy that injects credentials so the agent never sees them [[48]](https://code.claude.com/docs/en/agent-sdk/secure-deployment). Seatbelt (macOS) / bubblewrap (Linux) for OS-level filesystem + network isolation [[36]](https://code.claude.com/docs/en/sandboxing). |
| **Reference implementations** | [Trail of Bits](https://www.trailofbits.com)' devcontainer ⭐ 771 ([trailofbits/claude-code-devcontainer](https://github.com/trailofbits/claude-code-devcontainer)) — ephemeral container, no production secrets, iptables default-drop egress allowlist (Anthropic / GitHub / npm / PyPI only) [[45]](https://github.com/trailofbits/claude-code-devcontainer). Docker Sandboxes (Jan 2026) escalates to per-agent microVMs with private Docker daemon [[44]](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/). |
| **Egress denylist** | Always block 169.254.169.254 + metadata.google.internal + RFC1918 ranges to neutralise the standard exfil playbook [[43]](https://www.penligent.ai/hackinglabs/ai-agents-hacking-in-2026-defending-the-new-execution-boundary/). |
| **GitHub Action mode** | Anthropic's [claude-code-action](https://github.com/anthropics/claude-code-action) ⭐ 7.3k enforces write-permission gating, env-var scrubbing, PID-namespace isolation, and `--allowedTools` minimisation — same pattern Slack bridges should mirror [[49]](https://github.com/anthropics/claude-code-action/blob/main/docs/security.md). StepSecurity flags that unlike Copilot, Claude Code's Action has *no* built-in network firewall, so runtime egress monitoring (Harden-Runner) is required, not optional [[51]](https://www.stepsecurity.io/blog/anthropics-claude-code-action-security-how-to-secure-claude-code-in-github-actions-with-harden-runner). |

## 6. Competing remote-control surfaces

Slack is one of six credible "message me, I'll ship code" surfaces. The differentiator is *where the runtime lives* and *whose quota pays*.

| Surface | Trigger | Runtime | Approval | Plan | Notes |
|---|---|---|---|---|---|
| **Claude Code in Slack** (Anthropic) | `@Claude` in channel | Anthropic cloud sandbox | Block Kit buttons; one PR per session | Pro / Max / Team / Enterprise [[1]](https://code.claude.com/docs/en/slack) | ⚠ GitHub-only [[17]](https://github.com/anthropics/claude-code/issues/21527) |
| **Claude Code Web** | Browser at claude.com/code | Anthropic cloud sandbox, YOLO mode under the hood | None per-command (`--dangerously-skip-permissions` inside the sandbox); selectable network isolation | Pro / Max [[52]](https://claude.com/blog/claude-code-on-the-web)[[53]](https://simonw.substack.com/p/claude-code-for-web-a-new-asynchronous) | "Teleport" copies session to local CLI [[53]](https://simonw.substack.com/p/claude-code-for-web-a-new-asynchronous) |
| **Claude Code Mobile** ("Remote Control") | iOS / Android app, Code tab | Anthropic cloud sandbox (same as web) | Same as web | Max ($100–200/mo); Pro to follow [[54]](https://venturebeat.com/orchestration/anthropic-just-released-a-mobile-version-of-claude-code-called-remote)[[55]](https://tessl.io/blog/anthropic-brings-claude-code-to-the-web-and-mobile/) | Phone-first PR creation |
| **GitHub Actions `@claude`** | `@claude` in PR/issue, issue assignment, scheduled prompt | Your GitHub runner, your compute bill | GitHub permissions + `--allowedTools` whitelist | API or Anthropic plan key [[56]](https://github.com/anthropics/claude-code-action) | [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) ⭐ 7.3k. Core CLI [anthropics/claude-code](https://github.com/anthropics/claude-code) ⭐ 118k [[57]](https://github.com/anthropics/claude-code) |
| **OSS Slack bridge** (community) | `@bot` / `/cc` slash command | Your laptop / your VPS / your container | DIY (Block Kit relay, hooks) | Whatever Anthropic plan you have | Only path for GitLab, local repos, non-GitHub workflows [[7]](https://github.com/chenhg5/cc-connect)[[10]](https://github.com/jeremylongshore/claude-code-slack-channel) |
| **Cursor Background Agents** | `@Cursor` in Slack (since Cursor 1.1, June 12 2025) | Cursor cloud isolated VM | Auto, opens GitHub PR | Cursor plan [[58]](https://cursor.com/changelog/1-1)[[59]](https://cursor.com/docs/integrations/slack) | Near-mirror of Claude pattern, but vendor-cloud runtime |
| **OpenAI Codex Slack** | `@Codex` in channel/thread | OpenAI cloud (codex-1, o3-tuned) | Auto; replies with merge link or "pull locally" | Plus / Pro / Business / Enterprise / Edu [[60]](https://developers.openai.com/codex/integrations/slack)[[61]](https://openai.com/index/codex-now-generally-available/) | OSS terminal sibling [openai/codex](https://github.com/openai/codex) ⭐ 78k [[62]](https://github.com/openai/codex) |
| **[Devin](https://devin.ai)** (Cognition) | `@Devin` in channel | Cognition cloud, ACU-billed | Auto; non-Devin Slack users now blocked from posting in Devin threads [[65]](https://docs.devin.ai/release-notes/2026) | $20/mo Pro entry + $2.25/ACU [[63]](https://venturebeat.com/programming-development/devin-2-0-is-here-cognition-slashes-price-of-ai-software-engineer-to-20-per-month-from-500)[[64]](https://devin.ai/pricing/) | ⚠ Real spend often $300–500/mo at usage [[66]](https://brainroad.com/devin-pricing-in-2026-real-cost-hidden-spend-and-alternatives/) |
| **[Replit](https://replit.com) Agent** | Replit Workspace (browser/IDE) | Replit cloud | IDE-side | Replit plan [[67]](https://replit.com/products/agent) | ⚠ Slack is a *data source*, not a trigger surface |

## 7. When Slack-as-trigger is actually right

Slack-as-trigger pays off when: (a) the team already lives in Slack, (b) tasks are short and well-scoped (one PR, one bug), (c) someone's near a phone or desk to triage approvals, and (d) the runtime sits behind real isolation. It's the wrong surface for long refactors, frontend work needing visual review [[25]](https://www.builder.io/blog/claude-code-slack), GitLab repos until #21527 lands [[17]](https://github.com/anthropics/claude-code/issues/21527), and any unattended cron-style automation that depends on Claude AI connector MCPs (broken under `-p` per #36833 [[27]](https://github.com/anthropics/claude-code/issues/36833)).

The pragmatic split: **first-party Claude Code in Slack for GitHub teams on Pro/Max who want zero ops**; **a hardened OSS bridge** (`cc-connect` for breadth, `claude-code-slack-channel` for security depth, `claude-slack-bridge` for the human-in-the-loop pattern) **when GitHub-only is a dealbreaker or the runtime must stay on your infrastructure**; and **Cursor / Codex / Devin** when "ship code from Slack" matters more than "must use Claude."
