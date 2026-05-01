---
title: "Slack ↔ Claude Code remote control: architectures, recipes, and traps"
date: 2026-04-27
depth: deep
format: md
topic: "Slack ↔ Claude Code remote control"
topic_raw: "Slack ↔ Claude Code remote control"
issue: 24
tags: [claude-code, slack, agents, mcp, devops]
cover: cover.svg
summary: Four working architectures for driving Claude Code from Slack, the projects that ship each, the SDK surface they lean on, and the security/cost traps every public deploy hits.
citations: 44
reading_time_min: 9
cost_usd: 8.22
duration_sec: 787
---

> **Decision.** If you can live with a hosted experience, use **Claude Code in Slack** [[5]](https://code.claude.com/docs/en/slack) [[23]](https://claude.com/blog/claude-code-and-slack) — Anthropic ships it, sessions run on claude.ai/code, no infra to maintain. If you need self-hosted (private repos, custom MCP, on-prem secrets), pick **chenhg5/cc-connect** ⭐ 6.4k (Apr 2026) [[12]](https://github.com/chenhg5/cc-connect) for the Socket-Mode + multi-platform path, or wire **anthropics/claude-code-action** ⭐ 7.3k [[28]](https://github.com/anthropics/claude-code-action) behind a thin Slack→GitHub-Issue shim like AnandChowdhary's bot [[8]](https://github.com/AnandChowdhary/claude-code-slack-bot) for the indirect / GitHub-Actions path. Build-it-yourself only if the use case is genuinely off-pattern — the Slack 3-second ack rule, prompt-injection from arbitrary chat input, and runaway-cost from open @-mentions [[38]](https://dev.to/deployagents/running-ai-agents-247-in-2026-local-vs-cloud-vs-managed-cost-infrastructure-deep-dive-5ab4) are all solved problems but easy to get wrong.

## The four architectures, side-by-side

| Pattern | Slack transport | Where Claude runs | Strengths | Weaknesses | Reference repo |
|---|---|---|---|---|---|
| **Managed** (Claude Code in Slack) | Anthropic-owned app | claude.ai/code session [[5]](https://code.claude.com/docs/en/slack) | Zero ops; auto intent routing; Create-PR button | Hosted only; consumer-account auth; no DMs [[5]](https://code.claude.com/docs/en/slack) | Anthropic Slack app [[24]](https://slack.com/marketplace/A08SF47R6P4-claude) |
| **Socket-Mode + local CLI** | Outbound WebSocket [[1]](https://docs.slack.dev/apis/events-api/comparing-http-socket-mode/) | Bot host runs `claude -p` | No public ingress; per-thread cwd | 10-conn cap per app [[1]](https://docs.slack.dev/apis/events-api/comparing-http-socket-mode/); workspace state to manage | chenhg5/cc-connect ⭐ 6.4k [[12]](https://github.com/chenhg5/cc-connect), mpociot ⭐ 157 [[6]](https://github.com/mpociot/claude-code-slack-bot) |
| **Indirect via GitHub Issue** | Events API webhook | GitHub Actions runner | Reuses claude-code-action; PRs natively; Cloudflare-cheap [[8]](https://github.com/AnandChowdhary/claude-code-slack-bot) | 30-min poll cap [[8]](https://github.com/AnandChowdhary/claude-code-slack-bot); GitHub-bound; no streaming tokens | AnandChowdhary/claude-code-slack-bot [[8]](https://github.com/AnandChowdhary/claude-code-slack-bot) |
| **Split worker + daemon** | Events API + git as queue | Local daemon `claude -p` | Public Slack endpoint, private compute; auto-commit per task [[41]](https://github.com/41fred/claude-code-slack) | Two services to babysit; 5 s polling latency | 41fred/claude-code-slack [[41]](https://github.com/41fred/claude-code-slack) |

The split is real and load-bearing: Slack transport (Socket Mode vs Events API) and execution location (managed cloud, bot host, GHA runner, local daemon) compose independently. Any pair is achievable; pick the pair that matches the threat model and ops tolerance.

## The Slack contract you cannot avoid

Three Slack-side rules force the architecture more than any Claude-side concern:

| Rule | Limit | Why it matters | Source |
|---|---|---|---|
| Ack within 3 s | HTTP 200 ≤ 3000 ms | Claude Code runs are minutes; you must ack-then-defer | [[2]](https://docs.slack.dev/apis/events-api/) [[4]](https://api.slack.com/interactivity/slash-commands) |
| Retry on miss | Immediate, +1 min, +5 min; subscription disabled at >95% failure / 60 min | Idempotency is mandatory; dedupe by `event_id` | [[2]](https://docs.slack.dev/apis/events-api/) |
| HMAC-SHA256 verify | `v0:ts:body`, reject ts older than 5 min | Replay-attack hardening; non-negotiable for Events API | [[3]](https://docs.slack.dev/authentication/verifying-requests-from-slack/) |
| Message length | 40,000 char hard cap, `message_truncated` warning at limit; 4,000 char recommended | Diffs and tool logs blow past this; upload as snippet | [[31]](https://docs.slack.dev/changelog/2018-truncating-really-long-messages/) |
| Socket Mode caps | 10 concurrent WS per app; not Marketplace-eligible | Blocks horizontally-scaled Marketplace listings | [[1]](https://docs.slack.dev/apis/events-api/comparing-http-socket-mode/) |

The Bolt SDKs codify the workaround as **lazy listeners** — `await ack()` first, push to queue, do the work in a separate function [[33]](https://github.com/slackapi/bolt-python/issues/34); ClaudeFluent's Slack-bot recipe names the same constraint as the single most critical timing rule [[34]](https://www.claudefluent.com/guides/claude-code-slack-bot). Even this leaks: Bolt-JS issue #1548 catalogs `operation_timeout` errors when `ack()` runs but the surrounding handler is slow under Lambda cold-start [[32]](https://github.com/slackapi/bolt-js/issues/1548). The canonical pattern is **ack synchronously → SQS / Cloudflare Queue / Redis stream → worker calls `claude -p`** [[9]](https://medium.com/@geetansh2k1/scalable-serverless-slack-bot-design-avoid-slacks-3-second-timeout-with-aws-lambda-sqs-7c91367c161d). For self-hosted Events API without a static IP, **Cloudflare Tunnel** is the 2026 default over [ngrok](https://ngrok.com) because the hostname survives restarts and avoids re-registering the Slack URL [[10]](https://www.thevshub.in/2026/01/secure-localhost-cloudflare-tunnel-guide.html).

## Claude Code's headless surface — what makes it bot-friendly

The CLI's non-interactive surface is everything a Slack bot needs and was explicitly designed for it:

| Flag | What it does | Bot use |
|---|---|---|
| `-p` / `--print` | Non-interactive run, exits when done [[19]](https://code.claude.com/docs/en/headless) | Replace REPL with one-shot |
| `--output-format stream-json` | NDJSON event stream on stdout [[19]](https://code.claude.com/docs/en/headless) | Parse line-by-line, stream to Slack |
| `--include-partial-messages` + `--verbose` | Token-level deltas [[19]](https://code.claude.com/docs/en/headless) | Edit-in-place progress messages |
| `--resume <session-id>` / `--continue` / `--fork-session` | Multi-turn over JSONL transcripts at `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl` [[21]](https://code.claude.com/docs/en/agent-sdk/sessions) | Map `thread_ts` → session ID |
| `--permission-mode <default\|acceptEdits\|plan\|auto\|dontAsk\|bypassPermissions>` | Override `defaultMode` from settings [[20]](https://code.claude.com/docs/en/cli-reference) | `bypassPermissions` for full-auto, `acceptEdits` + allowlist for safer |
| `--allowedTools "Bash(git diff *)"` | Glob-pattern tool allowlist [[20]](https://code.claude.com/docs/en/cli-reference) | Scope tools per channel |
| `--permission-prompt-tool <mcp_tool>` | Route approval requests to a named MCP tool [[20]](https://code.claude.com/docs/en/cli-reference) | Slack approval buttons via MCP |
| `--mcp-config <file\|json>` + `--strict-mcp-config` | Hermetic MCP load, ignores `~/.claude.json` [[20]](https://code.claude.com/docs/en/cli-reference) | Reproducible per-run MCP set |
| `--max-turns`, `--max-budget-usd` | Hard runtime caps [[20]](https://code.claude.com/docs/en/cli-reference) | Cost-runaway containment |
| `--bare` | Skip hook/skill/MCP/CLAUDE.md auto-discovery; require `ANTHROPIC_API_KEY` [[19]](https://code.claude.com/docs/en/headless) | Reproducible bot runs |
| `claude setup-token` | Mint long-lived OAuth token [[20]](https://code.claude.com/docs/en/cli-reference) | CI / daemon auth |

The Python `claude-agent-sdk` skips the spawn altogether: `ClaudeSDKClient` is an async context manager that auto-tracks the session, and `CanUseTool: Callable[..., Awaitable[PermissionResult]]` is the in-process equivalent of a permission prompt — it returns `PermissionResultAllow` (with optional `updated_input`) or `PermissionResultDeny` [[22]](https://platform.claude.com/docs/en/agent-sdk/python). TypeScript's `query()` exposes equivalent `continue` / `resume` / `forkSession` options on its options object [[21]](https://code.claude.com/docs/en/agent-sdk/sessions).

⚠ Session-resume gotcha: transcripts are keyed on `<encoded-cwd>` — if your worker resumes from a different working directory than the original run, you silently get a fresh session [[21]](https://code.claude.com/docs/en/agent-sdk/sessions). Pin the cwd or ship the JSONL.

## Existing projects, ranked

| Project | ⭐ Stars | Lang | Last push | Architecture | Worth it? |
|---|---|---|---|---|---|
| [chenhg5/cc-connect](https://github.com/chenhg5/cc-connect) [[12]](https://github.com/chenhg5/cc-connect) | ⭐ 6.4k | Go | 2026-04-27 | Socket Mode + multi-platform broker; admin dashboard; 10+ agents | ✓ first pick for self-hosted |
| [JessyTsui/Claude-Code-Remote](https://github.com/JessyTsui/Claude-Code-Remote) [[13]](https://github.com/JessyTsui/Claude-Code-Remote) | ⭐ 1.2k | JS | 2025-12-06 | Hook + tmux/PTY injection; Slack still TODO | ✗ no Slack yet |
| [mpociot/claude-code-slack-bot](https://github.com/mpociot/claude-code-slack-bot) [[6]](https://github.com/mpociot/claude-code-slack-bot) | ⭐ 157 | TS | 2025-06 (stale) | Socket Mode + SDK; per-thread cwd; image uploads | ⚠ audit defaults — broad-permission Slack bots are the prompt-injection target [[35]](https://www.mitiga.io/blog/007-license-to-skill-p-2-slack-compromise-through-claude-code) [[40]](https://www.truefoundry.com/blog/claude-code-prompt-injection) |
| [AnandChowdhary/claude-code-slack-bot](https://github.com/AnandChowdhary/claude-code-slack-bot) [[8]](https://github.com/AnandChowdhary/claude-code-slack-bot) | ⭐ 11 | TS | active | Cloudflare Workers → GitHub Issue → claude-code-action; Cloudflare Queue mirrors comments every 10 s for ≤ 30 min | ✓ for GHA-centric teams |
| [yuya-takeyama/cc-slack](https://github.com/yuya-takeyama/cc-slack) [[11]](https://github.com/yuya-takeyama/cc-slack) | ⭐ 14 | Go | 2025-08-23 | `/cc` slash command; multi-project | ⚠ moderately maintained |
| [dbenn8/claude-slack](https://github.com/dbenn8/claude-slack) [[14]](https://github.com/dbenn8/claude-slack) | ⭐ 22 | Py | 2026-01-31 | Bidirectional via `.claude/hooks/` + Socket Mode listener with shared response file | ✓ for Python shops |
| [jeremylongshore/claude-code-slack-channel](https://github.com/jeremylongshore/claude-code-slack-channel) [[7]](https://github.com/jeremylongshore/claude-code-slack-channel) | ⭐ 15 | TS | active | Socket Mode + MCP stdio + per-thread isolation + hash-chained audit | ✓ if security matters |
| [41fred/claude-code-slack](https://github.com/41fred/claude-code-slack) [[41]](https://github.com/41fred/claude-code-slack) | ⭐ 15 | Py | active | Split FastAPI worker (Railway) + local macOS daemon; GitHub repo as queue | ✓ for laptop-as-runner setups |
| [MattKilmer/claude-autofix-bot](https://github.com/MattKilmer/claude-autofix-bot) [[42]](https://github.com/MattKilmer/claude-autofix-bot) | ⭐ 3 | TS | active | Express + simple-git on Railway; image attachment support; opens PR back | ✓ for autofix flows |
| [tomeraitz/claude-slack-bridge](https://github.com/tomeraitz/claude-slack-bridge) [[44]](https://github.com/tomeraitz/claude-slack-bridge) | ⭐ 21 | TS | active | **Inverse**: MCP server lets a running Claude task pause and ask Slack via Unix socket | ✓ for human-in-the-loop |
| [takafu/slack-claude-bot](https://github.com/takafu/slack-claude-bot) [[15]](https://github.com/takafu/slack-claude-bot) | ⭐ 2 | TS | 2026-01-16 | Per-thread CLI spawn; injects `SLACK_BOT_TOKEN` so Claude posts via Bash+curl | ⚠ minimal but novel |
| [engineers-hub-ltd/...integration](https://github.com/engineers-hub-ltd-in-house-project/slack-claude-code-integration) [[16]](https://github.com/engineers-hub-ltd-in-house-project/slack-claude-code-integration) | ⭐ 11 | JS | 2025-06-30 | Wraps Claude Code as MCP server; `/claude` slash | ⚠ stale |
| [satetsu888/slackbot-for-claude](https://github.com/satetsu888/slackbot-for-claude) [[17]](https://github.com/satetsu888/slackbot-for-claude) | ⭐ 5 | TS | 2024-03 | Pre-Claude-Code; raw Anthropic API | ✗ abandoned |

## Anthropic's first-party paths (Apr 2026)

| Surface | Status | Trigger | Notes |
|---|---|---|---|
| **Claude Code in Slack** [[5]](https://code.claude.com/docs/en/slack) | Research preview, launched 2025-12-08 [[23]](https://claude.com/blog/claude-code-and-slack) | `@claude` mention in channel (no DMs) | Auto intent routing; runs on claude.ai/code; admin chooses Code-only vs Code+Chat; "Retry as Code" button |
| **Claude for Slack app** [[24]](https://slack.com/marketplace/A08SF47R6P4-claude) | GA marketplace app | Same Slack app surface as above | The underlying Anthropic-published app — Claude.ai chat + Claude Code routing in one [[25]](https://support.claude.com/en/articles/12461605-using-claude-in-slack) |
| **Claude Code Routines** [[26]](https://code.claude.com/docs/en/routines) | Research preview, launched 2026-04-14 | Schedule, API (`/fire` endpoint, bearer token), GitHub events | Slack is **not** a native trigger — only available as MCP connector inside the routine |
| anthropics/claude-code-action [[28]](https://github.com/anthropics/claude-code-action) ⭐ 7.3k | GA | `@claude` in GitHub comments; `issue_comment`, `pull_request_review_comment`, `issues` [[27]](https://code.claude.com/docs/en/github-actions); also `schedule`, `workflow_dispatch` [[28]](https://github.com/anthropics/claude-code-action) | Backends: Anthropic API, Bedrock, Vertex AI, Foundry [[28]](https://github.com/anthropics/claude-code-action); Slack-trigger requires user-built bridge via `repository_dispatch` |
| **Slack MCP server** (Slack-published) [[29]](https://slack.com/blog/news/mcp-real-time-search-api-now-available) | GA 2026-02-17 | Read/write Slack from Claude.ai or Claude Code | Auth gap: Claude Code requires OAuth 2.0 DCR; Slack's MCP server doesn't ship DCR → admins must hand-roll an internal app and pass `--client-id`/`--client-secret` [[36]](https://github.com/anthropics/claude-code/issues/30564) |
| `@modelcontextprotocol/server-slack` [[30]](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/slack) ⭐ 84.6k (parent) | Archived 2025-05-29 | — | Superseded by Slack's first-party MCP server |

Bottom line: Anthropic ships the front door (Claude Code in Slack) and the backend primitive (claude-code-action), but **no first-class Slack-trigger for self-hosted Claude Code**. The community fills that gap.

### Counter-argument: maybe don't ship this

A Slack ↔ Claude Code bot inherits the trust, reach, and tone of the user account it runs as [[35]](https://www.mitiga.io/blog/007-license-to-skill-p-2-slack-compromise-through-claude-code), and any workspace member who can @-mention can spend money [[38]](https://dev.to/deployagents/running-ai-agents-247-in-2026-local-vs-cloud-vs-managed-cost-infrastructure-deep-dive-5ab4). If your use case is "trigger one repo's tests from chat occasionally", a `/claude-fix` slash command shelling claude-code-action via `repository_dispatch` is much smaller surface area than a long-running bot host. Build the bot only when streaming progress, multi-turn threading, or thread-pinned context actually pay for the operational debt.

## Reference recipe: ack → queue → CLI → reply

A minimal self-hosted pipeline that satisfies every Slack constraint:

```
┌──────────────┐  Events API  ┌───────────────┐  enqueue  ┌──────────┐
│ Slack channel│─────HMAC────▶│  Slack worker │──────────▶│  Queue   │
└──────────────┘  (Cf Worker, └───────────────┘ (SQS, Cf  └──────────┘
       ▲          Lambda, etc.)│  ack ≤ 3 s    │ Queue, Redis)   │
       │                       │  add 👀 react │                 ▼
       │                       └───────────────┘          ┌──────────────┐
       │                                                   │   Worker     │
       │            chat.postMessage thread_ts             │ claude -p \  │
       └───────────────────────────────────────────────────│   --output-  │
                                                           │   format     │
                                                           │   stream-json│
                                                           └──────────────┘
```

Key choices each box:

1. **Slack worker** — Cloudflare Workers (free tier, persistent hostname [[10]](https://www.thevshub.in/2026/01/secure-localhost-cloudflare-tunnel-guide.html)) or AWS Lambda. Verify HMAC-SHA256 [[3]](https://docs.slack.dev/authentication/verifying-requests-from-slack/), reject `ts > 5 min` old, return 200, write payload to queue. Add an `eyes` reaction synchronously so users see the bot accepted the request even before the queue picks it up — AnandChowdhary's bot does this [[8]](https://github.com/AnandChowdhary/claude-code-slack-bot).
2. **Queue** — for ≤ 30 min runs, Cloudflare Queue with a 10 s poller works [[8]](https://github.com/AnandChowdhary/claude-code-slack-bot); for longer, a stateful Redis stream or git-as-queue (41fred's pattern, repo `tasks/` directory polled every 5 s [[41]](https://github.com/41fred/claude-code-slack)).
3. **Worker** — clones the repo into an ephemeral cwd, runs `claude -p --output-format stream-json --verbose --resume <session-mapped-from-thread_ts> --max-budget-usd 5 --allowedTools 'Read,Edit,Bash(git *)' "$prompt"`. Pipe stdout through a NDJSON parser → `chat.postMessage` updates on the original `thread_ts`. Cap `--max-turns` defensively.
4. **Auto-commit & push** — the 41fred daemon commits and pushes after each task automatically [[41]](https://github.com/41fred/claude-code-slack); MattKilmer/claude-autofix-bot opens a PR with simple-git + the GitHub API and links it back to the Slack thread [[42]](https://github.com/MattKilmer/claude-autofix-bot).
5. **Inject Slack context for free** — takafu/slack-claude-bot's clever shortcut: pass `SLACK_BOT_TOKEN`, `CHANNEL`, `THREAD_TS` as env into the Claude Code child process so Claude itself can use Bash+curl to post progress and reactions, no SDK plumbing needed [[15]](https://github.com/takafu/slack-claude-bot).

For the SRE / production shape, David Calvert's "Hive Ix" is <2,000 lines of Go on GCP/Kubernetes via Helm, calling `exec.Command("claude", "-p", prompt)` against Sonnet 4.5 on Vertex AI, with Atlassian + Datadog MCP servers attached for incident-response context [[43]](https://medium.com/@dotdc/building-an-agentic-slackbot-with-claude-code-eba0e472d8f4).

## Pitfalls — and what they cost

| Pitfall | What goes wrong | Mitigation |
|---|---|---|
| **3 s ack** | `operation_timeout` shown to user; partial delivery on bulk fan-outs [[32]](https://github.com/slackapi/bolt-js/issues/1548) | Lazy listeners; ack before any work [[33]](https://github.com/slackapi/bolt-python/issues/34) |
| **40k char output** | Claude diffs / `tool_use` logs truncate silently | Detect → upload as `files.upload` snippet [[31]](https://docs.slack.dev/changelog/2018-truncating-really-long-messages/) |
| **Prompt injection** | Mitiga showed a working trojanized "skill" that uses Claude Code's own Slack tools to phish coworkers from the user's account, with public-channel fallback [[35]](https://www.mitiga.io/blog/007-license-to-skill-p-2-slack-compromise-through-claude-code); same class hits Gemini CLI, Copilot via comments [[39]](https://www.securityweek.com/claude-code-gemini-cli-github-copilot-agents-vulnerable-to-prompt-injection-via-comments/) | Least-privilege MCP tools [[40]](https://www.truefoundry.com/blog/claude-code-prompt-injection); allowlist channels; never trust message text |
| **Cost runaway** | 24/7 operators report $2,000/hour from loop bugs [[38]](https://dev.to/deployagents/running-ai-agents-247-in-2026-local-vs-cloud-vs-managed-cost-infrastructure-deep-dive-5ab4); any workspace member can @-mention | `--max-budget-usd` and `--max-turns` per run; rate-limit per user_id |
| **Insecure defaults in starter bots** | Many community bots ship with broad MCP permissions and no channel allowlist; a shared working directory across a channel is a common accident — broad-permission MCP is the documented prompt-injection vector [[40]](https://www.truefoundry.com/blog/claude-code-prompt-injection) | Audit any starter repo before deploy; least-privilege MCP, allowlist channels |
| **Sandboxing skipped** | Without filesystem + network isolation, a compromised agent exfiltrates SSH keys [[37]](https://code.claude.com/docs/en/sandboxing) | Run in a fresh container per request; restrict egress |
| **OAuth DCR mismatch** | Claude Code's MCP client requires OAuth 2.0 DCR; Slack's MCP server doesn't ship it [[36]](https://github.com/anthropics/claude-code/issues/30564) | Hand-roll an internal Slack app; pass `--client-id`/`--client-secret` |
| **Session-resume cwd drift** | Resume from a different cwd silently starts a new session [[21]](https://code.claude.com/docs/en/agent-sdk/sessions) | Pin cwd; or use a `SessionStore` adapter |
| **Tool approval has no human** | Headless `claude -p` can't pop a TUI prompt | `--permission-prompt-tool <mcp>` for Slack-button approvals [[20]](https://code.claude.com/docs/en/cli-reference); or `--permission-mode acceptEdits` with tight allowlist; OpenACP demos inline approve/deny buttons [[18]](https://dev.to/tigergethigher/how-to-control-claude-code-from-telegram-discord-or-slack-self-hosted-open-source-1jk8) |

## When to pick what

→ **Hosted, GitHub-connected work** → Claude Code in Slack [[5]](https://code.claude.com/docs/en/slack). Done.

→ **Self-hosted, simple, 1 repo, behind firewall** → chenhg5/cc-connect [[12]](https://github.com/chenhg5/cc-connect) (Socket Mode, no public IP).

→ **GitHub-Actions–centric team, want PRs naturally** → AnandChowdhary's pattern [[8]](https://github.com/AnandChowdhary/claude-code-slack-bot): Slack → GH Issue → claude-code-action → comments mirrored back. The 30-min poll cap is the hard limit.

→ **Laptop is the runner, public Slack endpoint** → 41fred split-worker pattern [[41]](https://github.com/41fred/claude-code-slack), git-as-queue.

→ **Long-running runs that need human-in-the-loop** → tomeraitz/claude-slack-bridge inverted MCP [[44]](https://github.com/tomeraitz/claude-slack-bridge): Claude itself blocks on a Slack reply mid-run.

→ **Production SRE bot at scale** → Calvert's Helm/Vertex pattern [[43]](https://medium.com/@dotdc/building-an-agentic-slackbot-with-claude-code-eba0e472d8f4) — minimal Go, MCP-attached observability.

→ **Anything else** → Routines API [[26]](https://code.claude.com/docs/en/routines) for triggered runs; build a thin `repository_dispatch` bridge to claude-code-action for the chat-driven side.
