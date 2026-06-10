---
title: "CapRover: Self-Hosted PaaS Deep Dive"
date: 2026-06-08
depth: standard
format: md
topic: "CapRover"
topic_raw: "CapRover"
issue: 200
tags: [caprover, self-hosted, paas, docker, docker-swarm, homelab, nginx]
summary: "CapRover is battle-tested and resource-light but lacks native PR preview environments and true multi-service Docker Compose support, making it a poor fit for dynamic preview workflows in 2026."
citations: 10
reading_time_min: 4
cover: cover.svg
cost_usd: 0.83
duration_sec: 388
model: "Sonnet 4.6"
---

> **TL;DR** — CapRover is the most resource-efficient self-hosted PaaS and a solid pick for stable single-container deployments on constrained hardware. **Skip it for PR preview environments**: each app tracks exactly one branch with no per-PR branching concept, and `docker-compose.yml` support covers only six fields — everything else is silently dropped. Maintained in 2026 but in slow-burn mode.

## What It Is

[CapRover](https://caprover.com/) [[2]](https://caprover.com/) ([GitHub ⭐ 15k](https://github.com/caprover/caprover) [[1]](https://github.com/caprover/caprover), Jun 2026) has been running since 2017 under the tagline "Heroku on Steroids." It wraps Docker Swarm and Nginx into a web UI + CLI, automating SSL via Let's Encrypt and serving apps on wildcard subdomains. Latest release: **v1.14.2** (May 2026), with roughly quarterly cadence [[1]](https://github.com/caprover/caprover).

## Installation & Requirements

Minimum to get started [[3]](https://caprover.com/docs/get-started.html):

- Ubuntu 22.04/24.04, Docker 25.x+ (avoid snap install)
- 1 GB RAM — 512 MB is insufficient for builds
- Ports open: 80, 443, 3000, 996, 7946, 4789, 2377
- Wildcard DNS record (`*.subdomain.yourdomain.com`)

Bootstrap is one `docker run` command; the web UI comes up at `http://SERVER_IP:3000` with password `captain42`. CLI finalizes setup with `caprover serversetup` [[3]](https://caprover.com/docs/get-started.html). Supports AMD64, ARM64, ARMv7 — runs fine in a Proxmox VM.

## Deployment Methods

| Method | Notes |
| ------ | ----- |
| `caprover deploy` CLI | Only method that surfaces build errors inline |
| Dashboard tarball upload | For testing only |
| Git webhook | One repo + **one branch** per app; POST webhook triggers rebuild |
| Rollback | Rebuild any prior image version with one click |

Webhook setup: enter the repo URL + branch in app settings, copy the generated webhook URL into GitHub/GitLab Settings → Webhooks [[4]](https://caprover.com/docs/deployment-methods.html). Every push to that branch triggers a rebuild. **There is no concept of per-PR or dynamic branch environments** — each CapRover app is permanently bound to one branch.

## Docker Compose Support

CapRover has a built-in Compose parser, but it covers only six fields [[10]](https://caprover.com/docs/docker-compose.html):

`image` · `environment` · `ports` · `volumes` · `depends_on` · `hostname`

All other Compose directives are **silently ignored** [[10]](https://caprover.com/docs/docker-compose.html). Services get renamed to `srv-captain--<name>`, requiring connection string updates. Workarounds: run Docker Compose outside CapRover on the same host and join its `captain-overlay-network`, or convert to CapRover one-click templates [[10]](https://caprover.com/docs/docker-compose.html).

The `captain-definition` file (the native format) is JSON, single-container only [[5]](https://caprover.com/docs/captain-definition-file.html):

```json
{ "schemaVersion": 2, "dockerfilePath": "./Dockerfile" }
```

No multi-service orchestration, no network declarations.

## Resource Footprint

At idle, CapRover is among the lightest options [[6]](https://massivegrid.com/blog/dokploy-vs-coolify-vs-caprover/):

| Platform                                             | CPU idle | RAM idle    | Containers |
| ---------------------------------------------------- | -------- | ----------- | ---------- |
| **CapRover** ⭐ 15k                                  | ~1–2%    | ~300–400 MB | 3–4        |
| [Dokploy](https://github.com/Dokploy/dokploy) ⭐ 35k | ~0.8%    | ~350 MB     | 3–4        |
| [Coolify](https://github.com/coollabsio/coolify) ⭐ 57k | ~5–6% | ~500–700 MB | 6–8        |

On a 1–2 GB Proxmox VM, CapRover leaves the most headroom for your actual workloads. 100M+ Docker Hub pulls reflects its production deployment footprint [[8]](https://kloudshift.net/blog/comparing-self-hostable-paas-solutions-caprover-coolify-dokploy-reviewed/).

## Strengths

- **Proven stability** — 9 years in production with mature codebase [[8]](https://kloudshift.net/blog/comparing-self-hostable-paas-solutions-caprover-coolify-dokploy-reviewed/)
- **Docker Swarm clustering** — add worker nodes from the UI; Nginx load-balances across them automatically [[2]](https://caprover.com/)
- **CLI-first workflow** — `caprover deploy` is fast; rollback with one click [[4]](https://caprover.com/docs/deployment-methods.html)
- **Scheduled Docker cleanup** — automatic image/container pruning, no manual cron needed [[8]](https://kloudshift.net/blog/comparing-self-hostable-paas-solutions-caprover-coolify-dokploy-reviewed/)
- **In-place upgrades** from the web UI, minimal downtime [[8]](https://kloudshift.net/blog/comparing-self-hostable-paas-solutions-caprover-coolify-dokploy-reviewed/)
- **Completely free** — no commercial tier or cloud upsell [[7]](https://servercompass.app/blog/best-self-hosted-paas-platforms-2026)

## Weaknesses

- **No native PR preview environments** — creating per-PR apps requires scripting GitHub Actions + CapRover API calls [[4]](https://caprover.com/docs/deployment-methods.html)
- **Broken Docker Compose support** — six fields only; everything else silently dropped [[10]](https://caprover.com/docs/docker-compose.html)
- **Dated UI** — functional but visually 2018; no database admin tools, no built-in alerting [[7]](https://servercompass.app/blog/best-self-hosted-paas-platforms-2026)
- **Slow development** — quarterly releases; community reports of Docker v29+ compatibility gaps [[9]](https://northflank.com/blog/7-best-cap-rover-alternatives-for-docker-and-kubernetes-app-hosting-in-2026)
- **Single-tenant** — no team or multi-user access management [[8]](https://kloudshift.net/blog/comparing-self-hostable-paas-solutions-caprover-coolify-dokploy-reviewed/)
- **No observability routing** — NetData integration exists but no alerting pipeline [[7]](https://servercompass.app/blog/best-self-hosted-paas-platforms-2026)

## PR Preview Environments

For **per-PR preview URLs** on CapRover, the minimum viable pattern:

1. GitHub Action on `pull_request` → calls CapRover REST API to create a new app named `pr-{number}`
2. Configures the app to track the PR branch via webhook
3. Triggers a build via the same API
4. Posts the `https://pr-{number}.yourdomain.com` URL as a PR comment
5. Second Action on `pull_request closed` → deletes the app

This is scripted infrastructure, not a platform feature. Coolify ⭐ 57k and Dokploy ⭐ 35k have more native pathways to this workflow [[6]](https://massivegrid.com/blog/dokploy-vs-coolify-vs-caprover/). If PR previews are the primary requirement, CapRover is the wrong tool.

## Decision Matrix

| Criterion | CapRover | Notes |
| --------- | -------- | ----- |
| RAM-constrained VM (1–2 GB) | ✓ | Best headroom of the three options |
| Single-container apps | ✓ | Native, fast, CLI-driven |
| Multi-service Compose stacks | ✗ | 6-field parser; use workarounds |
| PR preview environments | ✗ | Manual scripting only |
| Team access / multi-user | ✗ | Single-tenant |
| Docker Swarm clustering | ✓ | Built-in, better than Coolify's multi-server |
| Database admin UI | ✗ | Not included |
| Development velocity | ⚠ | Quarterly releases, slowing since 2024 |
