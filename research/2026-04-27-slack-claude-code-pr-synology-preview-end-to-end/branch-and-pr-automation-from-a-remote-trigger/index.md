---
title: Branch and PR automation from a remote trigger
date: 2026-04-28
depth: standard
format: md
topic: "Branch and PR automation from a remote trigger"
topic_raw: "Branch and PR automation from a remote trigger"
issue: 24
tags: [github-actions, automation, pull-requests, webhooks, claude-code]
summary: How to translate a remote event (Slack message, webhook, schedule, label) into a branch and pull request — transports, tokens, and the mechanics that actually push the commit.
citations: 18
reading_time_min: 6
cover: cover.svg
cost_usd: 2.42
duration_sec: 375
---

> **Decision.** For a Slack/chat → PR pipeline, fire a `repository_dispatch` from your bot, run the work on a GitHub-hosted (or self-hosted) runner, and let `anthropics/claude-code-action` [[6]](https://github.com/anthropics/claude-code-action) ⭐ 7.3k or `peter-evans/create-pull-request` [[1]](https://github.com/peter-evans/create-pull-request) ⭐ 2.8k push the branch and open the PR. **Auth via a custom GitHub App token, not the default `GITHUB_TOKEN`** — otherwise downstream CI on the PR will not run [[2]](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md). For non-AI workflows (issue → scaffold branch, dependency bump), the same shape works with `gh pr create` or `peter-evans/create-pull-request` directly.

## The four moving parts

Any "remote thing happens → branch + PR" pipeline factors into four decisions. Pick once per layer; everything else follows.

| Layer | Question | Common answers |
|---|---|---|
| **Transport** | How does the external event reach GitHub? | `repository_dispatch` API call · `workflow_dispatch` · GitHub App webhook · scheduled cron · label/comment event |
| **Compute** | Where does the branch+PR work execute? | GitHub-hosted runner · self-hosted runner · external server (Probot/Lambda/your bot) |
| **Auth** | What token signs the push and PR? | `GITHUB_TOKEN` · classic PAT · fine-grained PAT · GitHub App installation token |
| **PR mechanics** | What actually creates the branch and PR? | `peter-evans/create-pull-request` · `gh pr create` · Octokit (`octokit-plugin-create-pull-request`) · the Claude/Copilot coding agent itself |

## Transport: how the trigger gets in

| Transport | Best for | Branch it runs on | Payload limit | Notes |
|---|---|---|---|---|
| `repository_dispatch` API | External services (Slack bot, Linear, your own webhook receiver) firing into a repo | Default branch only [[3]](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows) | 65,535 chars / 10 top-level props in `client_payload` [[3]](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows) | Since Sep 2022, `GITHUB_TOKEN` can fire it from inside another workflow [[4]](https://github.blog/changelog/2022-09-08-github-actions-use-github_token-with-workflow_dispatch-and-repository_dispatch/) |
| `workflow_dispatch` | Operator hits "Run workflow" or a script targets a specific workflow | Any ref you specify [[3]](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows) | 25 typed inputs, 65,535 chars total [[3]](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows) | Inputs are typed (string/choice/boolean); `repository_dispatch` is opaque JSON |
| GitHub App webhook → external server | High-volume, multi-repo bots (Renovate, Probot apps) | N/A — the bot drives `git push` and the PR API itself | Full webhook payload | Bot manages its own auth and rate limits |
| Schedule (`cron`) | Periodic scans (dependency bumps, dead-link sweeps) | Default branch | n/a | [Renovate](https://www.mend.io/renovate/)'s primary mode [[11]](https://github.com/renovatebot/renovate) ⭐ 21k |
| Issue / label / comment event | In-GitHub IssueOps — `/cib`, `@claude implement …`, label `ai-scaffold` | The repo's branches | n/a | The native IssueOps pattern [[8]](https://github.blog/engineering/issueops-automate-ci-cd-and-more-with-github-issues-and-actions/) |

`peter-evans/repository-dispatch` [[13]](https://github.com/peter-evans/repository-dispatch) ⭐ 1.2k is the de-facto wrapper for firing a dispatch from inside one workflow into another.

## Compute: where the branch+PR work runs

| Surface | When to pick it | Tradeoffs |
|---|---|---|
| GitHub-hosted runner | Default. Stateless, ephemeral, free quota for public repos. | 6 h job timeout; no access to your private network. |
| Self-hosted runner | Work needs your VPC, internal package registries, or longer wall-clock than 6 h. Copilot coding agent gained this in Oct 2025 [[17]](https://github.blog/changelog/2025-10-28-copilot-coding-agent-now-supports-self-hosted-runners/). | ⚠ Public-repo PRs from forks can run code on your runner — keep these on GitHub-hosted only. |
| External server ([Probot](https://probot.github.io), Lambda, your own bot) | Long-lived bots like Renovate, or when the trigger is not a GitHub event at all. | You own auth, retries, rate-limit handling. Probot [[9]](https://github.com/probot/probot) ⭐ 9.5k handles the webhook-event-emitter shape; Octokit handles the Tree/Commit API for actual pushes [[18]](https://github.com/gr2m/octokit-plugin-create-pull-request) ⭐ 114. |

## Auth: the one footgun everyone hits

The default `GITHUB_TOKEN` looks fine until you notice **CI never runs on the PRs your automation opens**. From peter-evans's own concepts doc [[2]](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md):

> Pull requests created with the default token "cannot trigger other workflows."

Documented in community threads going back years [[5]](https://github.com/orgs/community/discussions/65321). Pick one of these instead:

| Token | Triggers downstream workflows? | Scoping | Recommended for |
|---|---|---|---|
| `GITHUB_TOKEN` (default) | ✗ on PR creation; ✓ for `repository_dispatch`/`workflow_dispatch` since 2022 [[4]](https://github.blog/changelog/2022-09-08-github-actions-use-github_token-with-workflow_dispatch-and-repository_dispatch/) | Auto-scoped to current repo | Trigger fan-out only; never for the PR push itself |
| Classic PAT | ✓ | Coarse — repo or org-wide | Quick PoC; the user account becomes the PR author |
| Fine-grained PAT | ✓ | Per-repo, scoped permissions | One-off bots where a GitHub App is overkill |
| GitHub App installation token (via `actions/create-github-app-token` [[14]](https://github.com/actions/create-github-app-token) ⭐ 796) | ✓ | Per-repo, per-permission, ephemeral (1 h) | **Default choice for production.** Branded bot identity, rotates automatically. |

Anthropic's docs make the same call: their troubleshooting section literally lists "Ensure you're using the GitHub App or custom app (not Actions user)" as the fix when CI does not run on Claude's commits [[7]](https://code.claude.com/docs/en/github-actions).

## PR mechanics: what pushes the branch

| Tool | Shape | Stars / source | Best fit |
|---|---|---|---|
| `peter-evans/create-pull-request` | Action step. Diffs the workspace, commits to a branch, opens/updates a PR. v8.1.1 (Apr 2026), needs `contents: write` + `pull-requests: write` [[1]](https://github.com/peter-evans/create-pull-request) | ⭐ 2.8k | The default for "I have an Actions workflow that mutates files; turn that into a PR." |
| `gh pr create` | CLI step. You drive `git checkout -b` / `git push` yourself, then `gh pr create --fill` [[15]](https://cli.github.com/manual/gh_pr_create). | official | Scripts that already use git directly; non-interactive automation. |
| `anthropics/claude-code-action@v1` | Agentic — Claude itself decides on edits, runs `git`, opens the PR via the action's plumbing [[7]](https://code.claude.com/docs/en/github-actions). | ⭐ 7.3k [[6]](https://github.com/anthropics/claude-code-action) | Issue-to-PR with @claude trigger, or any prompt-driven flow. |
| `octokit-plugin-create-pull-request` | Node library. Builds the tree/commits via the GitHub API — no `git` binary needed [[18]](https://github.com/gr2m/octokit-plugin-create-pull-request). | ⭐ 114 | Probot apps and serverless webhook receivers, where shelling out to git is awkward. |
| `robvanderleek/create-issue-branch` | Probot app + Action. Creates `issue-15-fix_nasty_bug` branch on assign or `/cib` comment; can also open the PR on label [[10]](https://probot.github.io/apps/create-issue-branch/). | ⭐ 346 | The "scaffold a branch from an issue" half of the flow, without writing it yourself. |
| Renovate | Long-running external bot that scans on a schedule and opens PRs across GitHub/GitLab/Bitbucket/Azure DevOps [[11]](https://github.com/renovatebot/renovate). | ⭐ 21k | Reference architecture for "many repos, many PRs, no in-repo workflow per repo." |
| Copilot coding agent | Asynchronous background agent that opens a draft PR, edits in the background, then requests review [[17]](https://github.blog/changelog/2025-10-28-copilot-coding-agent-now-supports-self-hosted-runners/). | official | When the trigger is a GitHub Issue assigned to Copilot and you want a managed agent surface. |

## End-to-end shapes worth copying

### Shape A — Slack message → PR (chat-driven coding)

1. Slack slash-command (or thread reaction) hits your bot.
2. Bot fires `POST /repos/{owner}/{repo}/dispatches` with `event_type: "slack-claude"` and `client_payload: { user, thread_ts, prompt, channel }`.
3. A workflow `on: repository_dispatch: types: [slack-claude]` runs `actions/create-github-app-token`, then `anthropics/claude-code-action@v1` with `prompt: ${{ github.event.client_payload.prompt }}`.
4. Claude edits files, the action commits, pushes a `claude/<thread-ts>` branch, opens the PR. Because the push is signed with a GitHub App token, downstream CI runs [[2]](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md).
5. Bot watches `pull_request.opened` (or polls `gh pr view`) and posts the PR URL back to the Slack thread.

Kilo for Slack [[16]](https://venturebeat.com/technology/kilo-launches-ai-powered-slack-bot-that-ships-code-from-a-chat-message) is the productized version of exactly this loop.

### Shape B — Issue label → scaffold branch + draft PR

1. User opens an issue, adds label `ai-scaffold`.
2. Workflow `on: issues: types: [labeled]` with `if: github.event.label.name == 'ai-scaffold'`.
3. `robvanderleek/create-issue-branch` [[10]](https://probot.github.io/apps/create-issue-branch/) creates `issue-{N}-{slug}` branch and (configured) opens a draft PR.
4. Optional: chain a `claude-code-action` step on `pull_request.opened` to populate the branch with a first-pass implementation.

This is the IssueOps pattern [[8]](https://github.blog/engineering/issueops-automate-ci-cd-and-more-with-github-issues-and-actions/) — the audit trail (label, branch, PR, comments) all lives inside GitHub.

### Shape C — Scheduled scan → many PRs

1. Renovate (or a custom workflow on `schedule:`) scans the repo on cron.
2. Each finding gets its own branch and PR, opened against the configured base branch [[11]](https://github.com/renovatebot/renovate).
3. Use `peter-evans/create-pull-request` with `branch-suffix: random` [[1]](https://github.com/peter-evans/create-pull-request) to avoid colliding branches when several findings open in parallel.

## Pitfalls

- **`pull_request_target` + checkout of fork code is a known repo-takeover pattern** [[12]](https://securitylab.github.com/resources/github-actions-preventing-pwn-requests/). If your branch+PR automation must run on contributions from forks, treat the fork's HEAD as untrusted: don't check it out into a job that has write tokens, and split the job into a sandboxed read-only stage and a privileged write-stage that operates only on data you've validated.
- `repository_dispatch` only runs workflows on the **default branch** [[3]](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows) — committing your dispatch handler on a feature branch and watching nothing fire is the most common mis-step.
- The "create or update" PR branch needs to exist on a remote — `peter-evans/create-pull-request` will not work for events that check out a commit (e.g. `release`, `pull_request`) without an explicit `base` input [[2]](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md).
- Self-hosted runners on public repos are dangerous because PRs from forks can execute on your hardware [[17]](https://github.blog/changelog/2025-10-28-copilot-coding-agent-now-supports-self-hosted-runners/). Keep automation that requires self-hosted runners in private repos, or gate it behind label-based triggers that maintainers add manually.

## Recommendation matrix

| If the trigger is… | …and the work is… | Pick |
|---|---|---|
| Slack thread / external chat | LLM-driven code edits | `repository_dispatch` → `claude-code-action@v1` [[6]](https://github.com/anthropics/claude-code-action) ⭐ 7.3k |
| GitHub Issue with `@claude` mention | LLM-driven code edits | Native claude-code-action `issue_comment` trigger [[7]](https://code.claude.com/docs/en/github-actions) |
| GitHub Issue assignment / label | Deterministic scaffolding | `create-issue-branch` [[10]](https://probot.github.io/apps/create-issue-branch/) ⭐ 346 |
| Cron / schedule | Dependency or content sweep | Renovate [[11]](https://github.com/renovatebot/renovate) ⭐ 21k or workflow + `peter-evans/create-pull-request` [[1]](https://github.com/peter-evans/create-pull-request) ⭐ 2.8k |
| Webhook from non-GitHub source ([Linear](https://linear.app), [Sentry](https://sentry.io)) | Custom logic | Probot app [[9]](https://github.com/probot/probot) ⭐ 9.5k + `octokit-plugin-create-pull-request` [[18]](https://github.com/gr2m/octokit-plugin-create-pull-request) ⭐ 114 |
| Anything | Anything in production | Mint a GitHub App installation token via `actions/create-github-app-token` [[14]](https://github.com/actions/create-github-app-token) ⭐ 796 — never the default `GITHUB_TOKEN` for the actual PR push [[2]](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md) |
