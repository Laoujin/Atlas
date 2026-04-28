---
layout: expedition
title: "Slack → Claude Code → PR → Synology preview, end-to-end"
date: 2026-04-27
topic: "Design and implement an end-to-end workflow that lets the user chat with Claude Code on Slack (likely one channel per project, with a clean way to clear context between features) to spec, build, and review a feature, then on a \"go\" message produce a branch and PR and auto-deploy that branch to a per-feature subdomain like ProjectName-FeatureX.sangu.be on a Synology NAS. Cover the wiring, state, and failure modes that tie the pieces together; favor production-ready open-source components in 2026."
format: md
tags: [claude-code, slack, preview-deployments, github-actions, synology]
summary: An end-to-end blueprint for chatting a feature into Claude Code on Slack and watching it build, PR, and auto-deploy to a per-feature subdomain on a Synology NAS — wiring, correlation state, and the failure modes that bite at every joint.
cover: cover.svg
synthesis: true
children:
  - slug: slack-claude-code-remote-control-architectures-recipes-and-traps
    title: "Slack ↔ Claude Code remote control"
    depth: deep
    status: success
    summary: Four working architectures for driving Claude Code from Slack, the projects that ship each, the SDK surface they lean on, and the security/cost traps every public deploy hits.
    citations: 44
    reading_time_min: 9
  - slug: slack-claude-code-remote-control-what-works-in-april-2026
    title: "Slack ↔ Claude Code remote control (alt)"
    depth: deep
    status: success
    summary: How Anthropic's first-party Slack integration, OSS bridges, and competing surfaces (Cursor, Codex, Devin) compare for driving Claude Code from chat — with the security patterns teams converge on.
    citations: 65
    reading_time_min: 9
  - slug: branch-and-pr-automation-from-a-remote-trigger
    title: "Branch and PR automation from a remote trigger"
    depth: standard
    status: success
    summary: How to translate a remote event (Slack message, webhook, schedule, label) into a branch and pull request — transports, tokens, and the mechanics that actually push the commit.
    citations: 18
    reading_time_min: 6
  - slug: branch-and-pr-automation-from-a-remote-trigger-2
    title: "Branch and PR automation from a remote trigger (alt)"
    depth: standard
    status: success
    summary: Three patterns for turning a remote signal into a branch and a pull request — repository_dispatch + create-pull-request, issue/comment workflows, and hosted AI agents — and the GITHUB_TOKEN gotcha that bites all three.
    citations: 26
    reading_time_min: 6
  - slug: synology-preview-deployments
    title: "Synology preview deployments"
    depth: deep
    status: success
    summary: How to wire per-PR preview deployments on a Synology NAS — the building blocks, the CI/CD patterns, the orchestrator that fits, and the gotchas that bite.
    citations: 78
    reading_time_min: 10
  - slug: orchestration-and-state-tying-slack-claude-code-github-and-synology-together
    title: "Orchestration and state"
    depth: standard
    status: success
    summary: How to coordinate a Slack message → Claude Code → PR → preview-deployment pipeline — what state to keep, where to keep it, and which orchestrator (if any) earns its weight.
    citations: 28
    reading_time_min: 6
cost_usd: 34.89
duration_sec: 4249
citations: 259
reading_time_min: 46
---

> **Recommended shape.** Slack Events API → ack-and-queue worker → `repository_dispatch` into a private GitHub repo → `anthropics/claude-code-action@v1` job authenticated by a GitHub App installation token → `pull_request.opened` triggers a deploy job that SSH's into the Synology and runs `docker compose -p pr-N pull && up -d` against an image pulled from GHCR → Cloudflare Tunnel publishes `pr-N.preview.sangu.be` via a wildcard hostname. State is one row per Slack `thread_ts` in Redis or a Cloudflare Durable Object. No durable-execution engine, no Coolify, no k3s — every component pulled in must justify its weight against this minimum.

## The same auth footgun fires twice

Both arms of the pipeline have a "default token quietly breaks the next stage" trap. On the Slack side, Claude Code's MCP client requires OAuth 2.0 Dynamic Client Registration which Slack's first-party MCP server does not ship — admins must hand-roll an internal Slack app and pass `--client-id`/`--client-secret` ([slack-claude-code-remote-control/](slack-claude-code-remote-control-architectures-recipes-and-traps/), source [[github.com/anthropics/claude-code/issues/30564]](https://github.com/anthropics/claude-code/issues/30564)). On the GitHub side, the default `GITHUB_TOKEN` opens the PR fine but **downstream CI never runs on it**, so the preview-deploy workflow silently never fires ([branch-and-pr-automation-from-a-remote-trigger/](branch-and-pr-automation-from-a-remote-trigger/), source [[peter-evans/create-pull-request docs]](https://github.com/peter-evans/create-pull-request/blob/main/docs/concepts-guidelines.md)). Mint the token via `actions/create-github-app-token` for every push that should trigger anything downstream.

## `thread_ts` is the only stable correlation key

Before a PR exists, nothing else identifies the work. Generate `thread_ts` once at the Slack ingress, pass it through every `repository_dispatch` payload, and stash `slack:thread:{thread_ts} → {run_id, branch, pr_number, preview_url, status}` in one small KV ([orchestration-and-state/](orchestration-and-state-tying-slack-claude-code-github-and-synology-together/)). The same key carries through to the preview subdomain (`pr-N.preview.sangu.be` once the PR exists, `feature-{slug-of-thread}` before that). This is also how the "go" message lands — the Slack button's interaction handler reads the row and emits the second `repository_dispatch` to promote.

## "Clean context between features" is a cwd contract

The user's instinct to clear context per feature aligns with a Claude Code gotcha worth pinning down: headless transcripts are keyed on `<encoded-cwd>`, so a worker that resumes from a different directory than the original run silently starts a fresh session ([slack-claude-code-remote-control/](slack-claude-code-remote-control-architectures-recipes-and-traps/), source [[code.claude.com agent-sdk/sessions]](https://code.claude.com/docs/en/agent-sdk/sessions)). One cwd per Slack thread (clone repo to `/tmp/<thread_ts>/`) gives per-feature isolation *and* per-thread continuation for free. `--fork-session` makes the per-feature split explicit when the user wants to branch a thread.

## The Synology layer is where the integration risk lives

Three of the four child reports describe well-trodden ground. The fourth notes that **no public end-to-end Synology preview-deployment write-up exists in 2026** ([synology-preview-deployments/](synology-preview-deployments/)) — Container Manager ships Docker 24.0.2 (unsupported by upstream since June 2024, source [[xda-developers]](https://www.xda-developers.com/synology-container-manager-outdated/)), Coolify's installer fails on DSM ([[coollabsio/coolify#3166]](https://github.com/coollabsio/coolify/discussions/3166)), and Dokploy breaks against DSM's older daemon ([[Dokploy#3888]](https://github.com/Dokploy/dokploy/issues/3888)). The minimum-viable stack is **Cloudflare Tunnel + wildcard hostname + GHCR + SSH + a bash wrapper around `docker compose -p pr-N`**, plus a Task Scheduler cron for `docker system prune` and a BTRFS snapshot quota so previews don't eat the volume. PR-close → teardown is `pull_request.closed` → `docker compose -p pr-N down -v`. Self-hosted runners stay on private repos ([[docs.github.com secure-use]](https://docs.github.com/en/actions/reference/security/secure-use)).

## The unresolved question worth answering before building

Synology research is blunt: if previews must be reachable by external reviewers on a public repo with reliable uptime, **don't host them on a NAS** — a $5/mo VPS or Cloudflare Pages free tier is structurally better suited ([synology-preview-deployments/](synology-preview-deployments/), source [[simplehomelab]](https://www.simplehomelab.com/udms-02-hardware-nas-minipc-vps/)). The user's `sangu.be` design reads as internal-only previews, which is fine — but the audience question (who clicks the URL?) decides whether the NAS is the right home for this at all.
