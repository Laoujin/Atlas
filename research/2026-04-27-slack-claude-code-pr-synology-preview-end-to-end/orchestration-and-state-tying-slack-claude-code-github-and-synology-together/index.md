---
title: "Orchestration and state: tying Slack, Claude Code, GitHub, and Synology together"
date: 2026-04-28
depth: standard
format: md
topic: "Orchestration and state"
topic_raw: "Orchestration and state"
issue: 24
tags: [orchestration, state, durable-execution, github-actions, workflow, slack]
summary: How to coordinate a Slack message → Claude Code → PR → preview-deployment pipeline — what state to keep, where to keep it, and which orchestrator (if any) earns its weight.
citations: 28
reading_time_min: 6
cover: cover.svg
cost_usd: 2.53
duration_sec: 440
---

> **Decision.** GitHub Actions is already running Claude Code [[27]](https://github.com/anthropics/claude-code-action) ⭐ 7.3k, so make Actions the orchestrator and stash correlation state in **one small key-value store keyed by Slack `thread_ts`** ([Redis](https://redis.io), [SQLite](https://www.sqlite.org), or Cloudflare Durable Object [[16]](https://developers.cloudflare.com/durable-objects/)). Reach for a durable-execution engine — **[DBOS](https://www.dbos.dev)** [[7]](https://github.com/dbos-inc/dbos-transact-ts) ⭐ 1.2k for [Postgres](https://www.postgresql.org)-only shops, **[Cloudflare Workflows](https://developers.cloudflare.com/workflows/)** [[14]](https://blog.cloudflare.com/workflows-ga-production-ready-durable-execution/) for Workers shops, **[Temporal](https://temporal.io)** [[4]](https://github.com/temporalio/temporal) ⭐ 20k only when the flow truly needs `step.waitForEvent` semantics, multi-day pauses, or fan-out beyond what Actions matrix gives you. For this pipeline (Slack → Claude → PR → Synology preview), the lightweight path wins — Claude Code's GHA jobs themselves cap at 6 h [[17]](https://docs.github.com/en/actions/reference/limits), and the human approval gate is a Slack button + `repository_dispatch`, not a multi-day suspended workflow.

## What state is actually moving

Before picking an orchestrator, name the bytes. Across this pipeline four kinds of state need to survive between steps:

| State | Lifetime | Producer | Consumer |
|---|---|---|---|
| **Correlation key** (`thread_ts` ↔ run ID ↔ branch ↔ PR # ↔ preview URL) | Until the PR closes | Slack bot at task-start | Every later step that posts back to Slack |
| **Approval status** (pending / approved / rejected) | Seconds–hours; bounded by reviewer SLA | Slack interaction handler | The runner that promotes the preview, or `repository_dispatch` |
| **Run progress** (current step, last log line, cost so far) | Job lifetime (≤6 h on hosted, ≤5 d self-hosted [[17]](https://docs.github.com/en/actions/reference/limits)) | Claude Code action steps | Slack progress messages |
| **Artifacts** (diff, screenshots, build images) | Until PR merge or 90 d retention | Claude Code action / build job | PR comments, preview deployment |

The first two need a small persistent store; the third is ephemeral and lives in the runner; the fourth uses GitHub Actions artifacts or GHCR. Every claim in the rest of this doc rolls up to one of these four.

## Two orchestrator shapes

### Shape A — GitHub Actions as the orchestrator

The default. The trigger graph already exists: `repository_dispatch` from Slack → `claude-code-action` job [[27]](https://github.com/anthropics/claude-code-action) → `peter-evans/create-pull-request` step → `pull_request` event → preview-deploy workflow → status-back-to-Slack step. State that has to outlive a single job goes into one external KV; everything else flows as job outputs and artifacts.

**Within Actions's native budget.** Job outputs cap at **1 MB per job, 50 MB per run** [[19]](https://cicube.io/blog/github-actions-outputs/) and reusable workflows can chain **10 deep** [[18]](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows) — fine for IDs and URLs, hopeless for diffs. Anything bigger goes to artifacts. Secrets do **not** auto-propagate down a `workflow_call` chain — pass each one explicitly [[18]](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows). A workflow run can total **35 days** including approval waits [[17]](https://docs.github.com/en/actions/reference/limits), but a single job is still capped at 6 h hosted / 5 d self-hosted.

**The KV store.** Pick one of three by team's existing infra:

| Store | Where it runs | Sweet spot | Notes |
|---|---|---|---|
| **Redis** | Anywhere (Synology container, Upstash, Fly) | Lots of ephemeral keys, distributed locks per Slack thread [[21]](https://redis.io/tutorials/chat-sdk-slackbot-distributed-locking/) | Leases prevent two workers replying to the same thread; TTL deletes stale state |
| **SQLite + [Litestream](https://litestream.io)** | One small VM or container | Pure simplicity, queryable history | Single-writer; not for multi-region |
| **Cloudflare Durable Object** | Cloudflare edge | Slack bot already on Workers | One DO per `thread_ts`, strongly-consistent SQLite per object [[16]](https://developers.cloudflare.com/durable-objects/) |

Slack Bolt itself ships **no durable state** [[22]](https://github.com/slackapi/bolt-js) ⭐ 2.9k — token storage, modal state, and per-thread leases are the developer's problem. That's the gap the KV fills.

### Shape B — A durable-execution engine

Worth it when the flow needs to **pause for hours, retry across process restarts, or fan out beyond the Actions matrix**. The shape: the Slack bot starts a workflow; each step (call Claude Code, open PR, build preview, await approval, promote) is a checkpoint; if the worker crashes, the engine replays from the last successful step. Every option below saves the result of every completed step so retries skip them [[1]](https://temporal.io/blog/what-is-durable-execution).

| Engine | Storage | Hosting model | Step semantics | Where it shines | ⭐ Stars |
|---|---|---|---|---|---|
| **Temporal** [[4]](https://github.com/temporalio/temporal) | Cassandra/MySQL/Postgres cluster | Managed (Temporal Cloud) or self-host cluster | Signal (async write), Query (read), Update (sync write w/ validation) [[2]](https://docs.temporal.io/handling-messages) | Mission-critical, audited, multi-language [[3]](https://devstarsj.github.io/2026/04/03/durable-execution-temporal-restate-dbos-distributed-workflows-2026/) | ⭐ 20k |
| **[Restate](https://restate.dev)** [[5]](https://github.com/restatedev/restate) | Embedded RocksDB | Single binary sidecar in front of HTTP services | Journaled handlers; no separate cluster [[3]](https://devstarsj.github.io/2026/04/03/durable-execution-temporal-restate-dbos-distributed-workflows-2026/) | Greenfield microservices, low ops | ⭐ 3.8k |
| **DBOS** [[7]](https://github.com/dbos-inc/dbos-transact-ts) | Postgres only | Library, no server | Each step + checkpoint is one Postgres transaction [[6]](https://www.dbos.dev/blog/why-postgres-durable-execution) | "Postgres is enough" shops; air-gapped on-prem | ⭐ 1.2k (TS) / ⭐ 1.3k (Py) [[8]](https://github.com/dbos-inc/dbos-transact-py) |
| **Cloudflare Workflows** [[13]](https://developers.cloudflare.com/workflows/) | Workers platform | Managed only | `step.do`, `step.sleep`, `step.sleepUntil`, `step.waitForEvent` [[15]](https://developers.cloudflare.com/workflows/build/sleeping-and-retrying/) | Already on Workers; want managed | n/a (closed) |
| **Inngest** [[9]](https://github.com/inngest/inngest) | Cloud (proprietary) or self-host single-node SQLite [[24]](https://railway.com/deploy/inngest-single-node-sqlite) | Calls into your serverless endpoints | Step-level retries; event-driven first | Event-driven backends; serverless | ⭐ 5.3k |
| **Trigger.dev v3** [[10]](https://github.com/triggerdotdev/trigger.dev) | Postgres + Redis | Cloud or self-host (Apache 2.0) | Checkpoint/resume on dedicated compute, no serverless timeout [[12]](https://medium.com/@matthieumordrel/the-ultimate-guide-to-typescript-orchestration-temporal-vs-trigger-dev-vs-inngest-and-beyond-29e1147c8f2d) | TS-first teams that want best DX | ⭐ 15k |
| **Hatchet** [[11]](https://github.com/hatchet-dev/hatchet) | Postgres | Self-host with one DB | DAGs, rate limits, concurrency keys, >100 jobs/s | High-throughput task queues | ⭐ 7.0k |
| **Windmill** [[25]](https://github.com/windmill-labs/windmill) | Postgres | Self-host single binary or Docker | One ACID statement per state transition | Internal-tools / scripts platform | ⭐ 16k |
| **Dagu** [[23]](https://dagu.sh) | None required (filesystem) | Single binary, no DB | DAGs over scripts, containers, SQL, HTTP | Cron + approvals on a homelab | ⭐ — |

**Decision shortcut.** If the team already has Postgres → DBOS or Hatchet. Already on Workers → Cloudflare Workflows. Already polyglot at scale → Temporal. Already TypeScript-everywhere → Trigger.dev. **None of those describe a Slack→Claude→PR pipeline that runs in single-digit minutes** — which is why Shape A wins for this specific pipeline.

## Where the patterns differ on human-in-the-loop

The "wait for the reviewer to click Approve" gate is the one place a durable-execution engine is qualitatively better than Actions. Compare:

| Approach | How the wait works | Time bound |
|---|---|---|
| **Actions + KV** | First job ends; Slack button → webhook → second `repository_dispatch` triggers the next workflow | Bounded by KV retention; Actions run cap is 35 d [[17]](https://docs.github.com/en/actions/reference/limits) |
| **Temporal Update / Signal** | Workflow blocks on a signal handler; Slack button → `signalWorkflow()`; replay-safe, exactly-once [[2]](https://docs.temporal.io/handling-messages) | Months — but cap at 50K events / 50 MB history; use Continue-As-New [[20]](https://temporal.io/blog/very-long-running-workflows) |
| **Cloudflare `step.waitForEvent`** | Workflow hibernates until the event is sent to the run [[15]](https://developers.cloudflare.com/workflows/build/sleeping-and-retrying/) | Cloud-managed; no server to babysit |
| **Postgres FSM** | Reviewer click writes a row; a periodic worker / `LISTEN/NOTIFY` advances state [[26]](https://blog.lawrencejones.dev/state-machines/) | As long as the DB is up |

For a homelab pipeline where the reviewer is one of two humans and replies in minutes, the Actions+KV path is the simplest correct thing. For a regulated org where the reviewer might be on PTO, durable-execution earns its complexity tax.

## State store cookbook for the lightweight path

```
KEY                                        VALUE (json)
slack:thread:{thread_ts}                   { team_id, user_id, repo, branch, run_id, pr_number, preview_url, status }
slack:lock:{thread_ts}                     "<worker-id>"          (TTL 15s, lease for processing) [[21]](https://redis.io/tutorials/chat-sdk-slackbot-distributed-locking/)
approval:{pr_number}                       { state: "pending"|"approved"|"rejected", approver, ts }
run:{run_id} → {thread_ts}                 reverse index for callbacks from Actions
```

Two endpoints close the loop: a Slack button handler that flips `approval:*` and emits `repository_dispatch`, and a `workflow_run` listener that reads `run:*` and posts to Slack. Every other piece of state stays inside one Actions run.

## Pitfalls

- **Don't use Actions outputs for diffs.** 1 MB cap [[19]](https://cicube.io/blog/github-actions-outputs/) — push diffs as artifacts and link from the PR comment.
- **Slack `thread_ts` is your only stable correlation key** before a PR exists. Generate it client-side and pass it through every dispatch payload.
- **Default `GITHUB_TOKEN` doesn't trigger downstream workflows.** Use a GitHub App installation token to push the branch, otherwise the preview deploy never runs.
- **Don't pick Temporal for a flow whose longest wait is a Slack approval.** The 50K-event / 50 MB-history cap [[20]](https://temporal.io/blog/very-long-running-workflows) is generous, but the operational tax is real and the human gate fits a row in a table [[26]](https://blog.lawrencejones.dev/state-machines/).
- **Don't double-process Slack events.** Slack retries within 3 s if no 200; a Redis lease keyed on `thread_ts` is one line and prevents two runners from racing on the same task [[21]](https://redis.io/tutorials/chat-sdk-slackbot-distributed-locking/).
- **DEEs and event logs are complements, not substitutes.** If Kafka is already in the stack, the engine handles the workflow lifecycle on top of the event log [[28]](https://www.kai-waehner.de/blog/2025/06/05/the-rise-of-the-durable-execution-engine-temporal-restate-in-an-event-driven-architecture-apache-kafka/).
