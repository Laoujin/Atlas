---
title: Branch and PR automation from a remote trigger
date: 2026-04-27
depth: standard
format: md
topic: "Branch and PR automation from a remote trigger"
topic_raw: "Branch and PR automation from a remote trigger"
issue: 17
tags: [github-actions, automation, ci-cd, devops, ai-agents]
summary: Three patterns for turning a remote signal into a branch and a pull request — repository_dispatch + create-pull-request, issue/comment workflows, and hosted AI agents — and the GITHUB_TOKEN gotcha that bites all three.
citations: 26
reading_time_min: 6
cover: cover.svg
cost_usd: 2.49
duration_sec: 404
---

> **Decision.** Pick by where the trigger lives.
> - **External system (webhook, cron job, other repo)** → fire `repository_dispatch` and let `peter-evans/create-pull-request` do the branch+PR work [[1]](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows) [[7]](https://github.com/peter-evans/create-pull-request).
> - **Inside GitHub (issue, label, comment)** → an `issues` or `issue_comment` workflow, optionally fan-out via `slash-command-dispatch` [[9]](https://github.com/peter-evans/slash-command-dispatch).
> - **Chat / ticket (Slack, Linear, Jira)** → hand off to a hosted agent (Copilot coding agent, Devin, Cursor, Codex Cloud) that owns the branch+PR step itself [[13]](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent) [[17]](https://devin.ai/) [[20]](https://cursor.com/blog/automations).
>
> All three hit the same gotcha: a PR opened with the default `GITHUB_TOKEN` will not trigger downstream `push`/`pull_request` workflows — you need a PAT or a GitHub App token if you want CI to run on the bot's PRs [[6]](https://docs.github.com/en/actions/security-guides/automatic-token-authentication) [[8]](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md).

## The trigger primitive

GitHub Actions exposes two remote-trigger events; everything else is a GitHub-native event you can listen for [[1]](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows).

| Trigger | Where it fires from | Branch the workflow runs from | Inputs | Notes |
|---|---|---|---|---|
| `workflow_dispatch` | UI button, `gh workflow run`, `POST /actions/workflows/{id}/dispatches` | Caller chooses (`--ref` / `ref` body field) | Up to 10 typed inputs (`string`, `boolean`, `choice`, `environment`) | The "manual button with parameters" trigger [[2]](https://docs.github.com/actions/managing-workflow-runs/manually-running-a-workflow) [[3]](https://cli.github.com/manual/gh_workflow_run) |
| `repository_dispatch` | `POST /repos/:owner/:repo/dispatches` with `event_type` + `client_payload` | ⚠ Default branch only — `ref`/branch is not selectable by the caller | Free-form `client_payload` JSON | The "external webhook" trigger; workflow file must be on default branch [[1]](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows) [[5]](https://github.com/orgs/community/discussions/24657) |
| `issues` / `issue_comment` | Activity inside GitHub | Default branch | Event payload (issue body, comment, labels) | Foundation for label-triggered, @mention, and slash-command flows [[10]](https://peterevans.dev/posts/chatops-for-github-actions/) |
| `schedule` | Cron | Default branch | None | Useful when "remote" is "time of day" |

The split matters. `workflow_dispatch` is the right choice when you control the caller and want a chosen branch + structured inputs (your own bot, an internal dashboard, a `gh` script). `repository_dispatch` is the right choice when something genuinely external posts a webhook — but the workflow lives on the default branch, period [[5]](https://github.com/orgs/community/discussions/24657). `peter-evans/repository-dispatch` ⭐ 1.2k (Apr 2026) is the standard wrapper for emitting one from inside another workflow [[4]](https://github.com/peter-evans/repository-dispatch).

## The branch + PR step

Once the workflow is running, three options open or update a PR. The first is overwhelmingly the standard.

| Tool | Mechanism | When to pick it |
|---|---|---|
| `peter-evans/create-pull-request` ⭐ 2.8k | Detects workspace changes, commits to a new branch, opens or updates a PR via REST | Default choice — handles update-existing-PR semantics, draft mode, signed commits, labels [[7]](https://github.com/peter-evans/create-pull-request) |
| `gh pr create` | One-line CLI | Single-commit, single-PR scripts where you don't need update-or-create logic |
| `actions/github-script` | JS calling Octokit | When you need bespoke API calls (e.g. cross-repo PR, complex labels, comment-on-PR) |

The action is on v8 (Apr 2026); it requires the repo-level toggle **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests** to be on, otherwise it fails with a 403 [[7]](https://github.com/peter-evans/create-pull-request).

## The token gotcha

This bites everyone exactly once: a PR pushed by `GITHUB_TOKEN` will not start `push` or `pull_request` workflows on the new branch [[6]](https://docs.github.com/en/actions/security-guides/automatic-token-authentication). GitHub does this on purpose to prevent recursive runs. The result: your bot opens a PR, but CI never runs on it, and merge gates stay grey.

Three fixes, in increasing order of cleanliness [[8]](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md):

| Fix | Trade-off |
|---|---|
| Classic PAT with `repo` + `workflow` scopes | Easiest. Tied to one user; expires; broad scope |
| Fine-grained PAT (`contents: write`, `pull-requests: write`) | Scoped to specific repos; still per-user |
| GitHub App with installation token | ✓ Per-repo install, audit-friendly, no expiry rotation pain. The recommended path |

## Issue → PR via comments and labels

The `issue_comment` event is how almost every "@mention me to fix this" workflow is built. Naive shape: one workflow listens for `issue_comment` and does the work inline. Better shape: a thin handler matches the slash command and re-emits a `repository_dispatch`, so the comment-event queue stays fast and the heavy work runs in parallel [[10]](https://peterevans.dev/posts/chatops-for-github-actions/). `peter-evans/slash-command-dispatch` ⭐ 685 (Apr 2026) packages exactly that pattern [[9]](https://github.com/peter-evans/slash-command-dispatch).

Label-triggered shape is the same idea with `issues: types: [labeled]` and a conditional on `github.event.label.name`. Common in AI-assisted flows — Aider's reference workflow tags an issue with `aider`, the action then branches and PRs against it [[22]](https://github.com/mirrajabi/aider-github-action).

## Hosted bots: dependency updates

For dependency PRs the trigger is "the dependency moved", not a human action. Two tools dominate.

| | Dependabot | Renovate ⭐ 21k |
|---|---|---|
| Trigger | Schedule + GitHub Security Advisories | Configurable schedule per dep/manager [[24]](https://docs.renovatebot.com/bot-comparison/) |
| Platforms | GitHub only (official) | GitHub, GitLab, Bitbucket, Azure DevOps, Forgejo, Gitea [[23]](https://github.com/renovatebot/renovate) |
| Monorepo grouping | ✗ One PR per dep unless `groups:` configured | ✓ Built-in preset groups monorepo packages into one PR [[24]](https://docs.renovatebot.com/bot-comparison/) |
| Setup | Built into GitHub, zero install | App install or self-host |
| Best fit | Single-repo GitHub project, want zero-config | Monorepos, multi-platform, fine-grained policy |

## Hosted AI agents: ticket → PR

These compress the whole pipeline (trigger → branch → edit → push → PR) into a single product. The differences are mostly *where the trigger lives* and *who hosts the runtime*.

| Agent | Trigger surface | Runtime | Cited |
|---|---|---|---|
| **Copilot coding agent** (GitHub) | Assign issue to Copilot; `@copilot` in PR; agents panel | Ephemeral GitHub Actions environment in your repo | [[13]](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent) [[14]](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/) |
| **Claude Code action** ⭐ 7.3k | `@claude` in issue/PR/comment, or issue assignment | Your GitHub Actions runner | [[11]](https://github.com/anthropics/claude-code-action) [[12]](https://code.claude.com/docs/en/github-actions) |
| **OpenAI Codex Cloud** ⭐ 78k | `@codex` on issue/PR; ChatGPT web app; Codex CLI | OpenAI-hosted sandbox | [[15]](https://github.com/openai/codex) [[16]](https://developers.openai.com/codex/integrations/github) |
| **Devin** | Slack mention, Linear/Jira ticket, web app | Cognition-hosted | [[17]](https://devin.ai/) [[18]](https://docs.devin.ai/release-notes/2026) |
| **Cursor background agents** | `@cursor` in PR/issue; Slack message; new Linear issue; merged GitHub PR; PagerDuty incident | Cursor-hosted | [[19]](https://docs.cursor.com/en/integrations/github) [[20]](https://cursor.com/blog/automations) |
| **Aider + GitHub Action** ⭐ 44k | Label `aider` on an issue | Your GitHub Actions runner | [[21]](https://github.com/Aider-AI/aider) [[22]](https://github.com/mirrajabi/aider-github-action) |

Two axes to weigh:

- **Runs in your CI vs hosted.** Claude Code action and Aider run on your own GitHub Actions runner — your secrets, your VPC, your bill. Copilot agent runs in *GitHub-hosted ephemeral* Actions still scoped to your repo. Devin, Cursor, Codex Cloud are external SaaS that clone your repo, do the work, and push back.
- **Trigger reach.** If the trigger source is GitHub (issue, comment, label), every option works. If it's Slack/Linear/Jira/PagerDuty, only Devin and Cursor have first-party integrations [[17]](https://devin.ai/) [[20]](https://cursor.com/blog/automations); the rest need you to bridge with a webhook → `repository_dispatch` [[1]](https://docs.github.com/actions/using-workflows/events-that-trigger-workflows).

## GitLab equivalents (one paragraph)

Same shape, different names. GitLab's `repository_dispatch` is the trigger token: `POST /projects/:id/trigger/pipeline` with a token and `ref` starts a pipeline on any branch [[25]](https://docs.gitlab.com/ci/triggers/) — strictly more flexible than `repository_dispatch` since `ref` is selectable. The PR step is `POST /projects/:id/merge_requests` against the Merge Requests API [[26]](https://docs.gitlab.com/api/merge_requests/). Renovate covers GitLab/Bitbucket/Forgejo/Gitea natively [[23]](https://github.com/renovatebot/renovate).

## A concrete example: Scout

This very repo uses two of the patterns. Open an issue tagged `scout-research` → `issues: [opened]` workflow runs sharpening and posts a checkbox-driven proposal. Tick the **Start research** checkbox → `issue_comment: [edited]` workflow on `github.event.changes.body.from` mutation runs the research and pushes to a sibling Atlas repo (separate SSH host alias). For headless invocations, the same workflow exposes `workflow_dispatch` with `topic`/`depth`/`format` inputs, so a cron job or external script can fire `gh workflow run research.yml -f topic=…`. No PR is ever opened on the source repo — the artifact lives in a downstream site repo — but the trigger fan-out (UI / issue / comment / external API) is exactly the structure described above.
