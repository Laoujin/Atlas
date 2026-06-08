---
title: "Dokploy: Self-Hosted PaaS for Docker-Native Deployments"
date: 2026-06-08
depth: standard
format: md
topic: "Dokploy"
topic_raw: "Dokploy"
issue: 200
tags: [dokploy, self-hosted, paas, docker, docker-swarm, preview-deployments, homelab]
summary: "Dokploy is a Docker-native open-source PaaS (⭐ 34.6k) with first-class PR preview deployments, Swarm-based multi-node scaling, and an AI-powered CLI/MCP server — at the cost of a mixed license model and a known memory regression."
citations: 18
reading_time_min: 4
cover: cover.svg
cost_usd: 0.98
duration_sec: 345
model: "Sonnet 4.6"
---

> **TL;DR** — Pick Dokploy if PR preview environments, Docker Swarm clustering, or a cleaner multi-server UX are the priority. Its native preview deployment support is the most cited reason to choose it over Coolify in 2026. The trade-offs: a mixed Apache 2.0/proprietary license, a smaller template catalog, and a memory regression in recent builds that can push idle usage past 630 MB. Core self-hosted functionality is free forever. [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments) [[9]](https://www.cherryservers.com/blog/coolify-vs-dokploy) [[4]](https://dokploy.com/blog/we-are-updating-dokploys-open-source-license)

## What is Dokploy

[Dokploy](https://dokploy.com/) ⭐ 34.6k (Jun 2026) is an open-source PaaS launched April 2024 as a self-hostable alternative to Vercel, Netlify, and Heroku. [[1]](https://github.com/Dokploy/dokploy) It wraps Docker Compose and Docker Swarm with a Next.js/TypeScript dashboard, Traefik reverse proxy, and an auto-generated REST API. As of v0.29.7 (June 2, 2026) it has 160+ releases across two years of rapid development. [[18]](https://github.com/Dokploy/dokploy/releases)

## Core Features

| Category              | Details                                                                                         |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| **Build methods**     | Nixpacks, Heroku Buildpacks, Paketo Buildpacks, Dockerfile, Docker Compose [[2]](https://dokploy.com/) |
| **Languages**         | Any (Node.js, PHP, Python, Go, Ruby, etc.) via Nixpacks/Buildpacks                              |
| **Databases**         | MySQL, PostgreSQL, MongoDB, MariaDB, LibSQL, Redis; automated S3 backups + volume backups [[2]](https://dokploy.com/) |
| **Git providers**     | GitHub, GitLab, Bitbucket, Gitea, Git Generic (5 total) [[12]](https://dokploy.com/dokploy-vs-coolify) |
| **SSL**               | Automatic Let's Encrypt via Traefik                                                             |
| **Multi-server**      | Docker Swarm clusters; replica management built-in [[2]](https://dokploy.com/)                   |
| **Monitoring**        | Real-time CPU/memory/network; alerting enabled by default [[12]](https://dokploy.com/dokploy-vs-coolify) |
| **Access control**    | RBAC (Admin/Developer roles from Startup tier); 2FA [[7]](https://dokploy.com/pricing)          |
| **AI (v0.29.0)**      | MCP server (508 tools / 49 categories), CLI (449 commands), AI log analysis [[5]](https://dokploy.com/blog/v0-29-0-ai-powered-debugging-mcp-server-cli-shared-git-providers) |

## PR Preview Deployments

Preview deployments are Dokploy's clearest differentiator in the homelab/PR-workflow context. [[9]](https://www.cherryservers.com/blog/coolify-vs-dokploy)

**How it works:**
- Triggered automatically when a PR is opened against the configured target branch [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments)
- Redeploys on every new commit to the PR; cleans up on merge or close [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments)
- Default URL pattern: `preview-${appName}-${uniqueId}.traefik.me` (free, no DNS setup needed) [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments)
- Custom wildcard domain: point `*.yourdomain.com` → server IP and configure in app settings [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments)
- Label filtering: only trigger previews for PRs bearing specific labels [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments)
- Max previews per app is configurable (default 3) [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments)
- Inherits production app's security rules and redirects [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments)

**Caveat:** Only available for apps using a Git provider (GitHub/GitLab/Bitbucket/Gitea) — direct Docker image deployments do not get previews. [[3]](https://docs.dokploy.com/docs/core/applications/preview-deployments)

## Resource Requirements & Known Issues

Minimum recommended: 2 GB RAM, 1 CPU, 30 GB disk. [[9]](https://www.cherryservers.com/blog/coolify-vs-dokploy) In practice, idle footprint is non-trivial:

| Condition                  | Dokploy container RAM |
| -------------------------- | --------------------- |
| Fresh install (pre-v0.27)  | ~464 MiB              |
| v0.27.1+ (regression)      | ~630–640 MiB          |
| Full stack (+ n8n + PG)    | 1.1–1.3 GB total      |

A memory regression introduced in v0.27.1 roughly doubled idle usage — suspected cause: health checks spawning a `curl` process every 10 seconds (~360/hr) for database queries. [[11]](https://github.com/Dokploy/dokploy/issues/3755) The GitHub issue was closed without a confirmed fix. On a 2 GB Proxmox VM with one app and a database, this leaves limited headroom; 4 GB is the practical minimum for comfortable single-node use.

**Proxmox-specific note:** The install script detects LXC containers and applies `--endpoint-mode dnsrr` automatically for Docker Swarm compatibility. Finalize your server's IP before running the installer — changing the host IP after Swarm initialization breaks the cluster. [[16]](https://flicksfix.com/posts/docker-swarm-cluster/)

## AI Features (v0.29.0)

Two new surfaces in the June 2026 release: [[5]](https://dokploy.com/blog/v0-29-0-ai-powered-debugging-mcp-server-cli-shared-git-providers)

- **AI log analysis** — on deploy failure, trigger analysis from the dashboard to get a summary of errors and remediation steps.
- **MCP server** — 508 auto-generated tools covering the full Dokploy API; works with Claude Desktop, Cursor, VS Code, Windsurf, Zed.
- **CLI** — 449 commands for terminal-driven management and CI/CD pipelines.

These are generated from the OpenAPI spec, so they track the API surface automatically. Dokploy added this shortly after Coolify shipped its own MCP server in May 2026. [[14]](https://nextgrowth.ai/coolify-vs-dokploy/)

## Licensing

| Component        | License                | Practical effect                              |
| ---------------- | ---------------------- | --------------------------------------------- |
| Core codebase    | Apache 2.0             | Free to use, modify, redistribute, resell     |
| Enterprise tier  | Proprietary/source-available | Requires paid access for SSO, white-labeling, HA, advanced monitoring |

Dokploy committed that no existing features will migrate to the paid tier. [[4]](https://dokploy.com/blog/we-are-updating-dokploys-open-source-license) Coolify, by contrast, is 100% Apache 2.0. [[10]](https://getdeploying.com/guides/coolify-vs-dokploy) For homelab use the distinction is largely academic — all core deployment and preview features are free.

## Pricing (Managed Cloud)

Self-hosted: free. Managed cloud tiers if you want hosting offloaded: [[7]](https://dokploy.com/pricing)

| Tier       | Price            | Servers | Orgs | Notes                          |
| ---------- | ---------------- | ------- | ---- | ------------------------------ |
| Hobby      | $4.50/mo         | 1       | 1    | 2 environments, 1 user         |
| Startup    | $15/mo           | 3       | 3    | Unlimited envs, RBAC, 2FA      |
| Enterprise | Custom           | ∞       | ∞    | SSO/SAML, audit logs, SLA      |

Extra servers: $4.50/mo each. Annual billing: 20% discount.

## Dokploy vs Coolify at a Glance

| Dimension                    | Dokploy                          | Coolify                          |
| ---------------------------- | -------------------------------- | -------------------------------- |
| **GitHub stars**             | ⭐ 34.6k                         | ⭐ 55.7k                         |
| **One-click templates**      | Limited (~dozens)                | 280+                             |
| **PR preview deployments**   | ✓ Native                        | Partial (requires config) [[9]](https://www.cherryservers.com/blog/coolify-vs-dokploy) |
| **Docker Swarm**             | ✓ Native, init on install       | ✓ Supported                     |
| **Idle RAM (platform)**      | ~630 MB (v0.27+) [[11]](https://github.com/Dokploy/dokploy/issues/3755) | ~800 MB–1.2 GB [[8]](https://contabo.com/blog/blog-coolify-vs-dokploy-comparison/) |
| **License**                  | Apache 2.0 + proprietary         | 100% Apache 2.0 [[10]](https://getdeploying.com/guides/coolify-vs-dokploy) |
| **MCP server**               | ✓ v0.29.0 (508 tools) [[5]](https://dokploy.com/blog/v0-29-0-ai-powered-debugging-mcp-server-cli-shared-git-providers) | ✓ v4.0 May 2026 [[14]](https://nextgrowth.ai/coolify-vs-dokploy/) |
| **ARM support**              | ⚠ Not officially documented     | ✓ Native [[9]](https://www.cherryservers.com/blog/coolify-vs-dokploy) |
| **DB restore via UI**        | ✓                               | Manual                           |
| **S3 volume backups**        | ✓                               | ✗ [[10]](https://getdeploying.com/guides/coolify-vs-dokploy) |
| **Git providers**            | 5 (incl. Generic)               | 4 [[12]](https://dokploy.com/dokploy-vs-coolify) |
| **Community age**            | April 2024                       | 2022                             |

## Pros & Cons

**Pros:**
- Native PR preview deployments with auto cleanup — best-in-class for this use case [[9]](https://www.cherryservers.com/blog/coolify-vs-dokploy)
- Docker Swarm initialized at install time; multi-node expansion is low-friction [[17]](https://massivegrid.com/blog/dokploy-vs-coolify-vs-caprover/)
- 5 Git providers including generic Git; good for self-hosted Gitea setups [[12]](https://dokploy.com/dokploy-vs-coolify)
- S3 volume backups and database restore UI [[10]](https://getdeploying.com/guides/coolify-vs-dokploy)
- Rapid release cadence (160+ releases in 2 years) [[18]](https://github.com/Dokploy/dokploy/releases)
- AI log analysis and MCP server as of v0.29.0 [[5]](https://dokploy.com/blog/v0-29-0-ai-powered-debugging-mcp-server-cli-shared-git-providers)

**Cons:**
- Memory regression since v0.27.1 — idle footprint 630+ MiB, unstable on 2 GB servers [[11]](https://github.com/Dokploy/dokploy/issues/3755)
- Mixed Apache 2.0/proprietary license (enterprise features gated) [[4]](https://dokploy.com/blog/we-are-updating-dokploys-open-source-license)
- Smaller template catalog vs Coolify's 280+ one-click services [[8]](https://contabo.com/blog/blog-coolify-vs-dokploy-comparison/)
- Smaller community (34.6k vs 55.7k stars); younger project [[14]](https://nextgrowth.ai/coolify-vs-dokploy/)
- Docker familiarity assumed; not beginner-friendly [[15]](https://www.vyomcloud.com/blog/dokploy-review-2026-pros-and-cons/)
- ARM architecture not officially documented [[9]](https://www.cherryservers.com/blog/coolify-vs-dokploy)
- Swarm-only scaling (no Kubernetes path) [[17]](https://massivegrid.com/blog/dokploy-vs-coolify-vs-caprover/)

## Community & Activity

- ⭐ 34.6k stars, 2,584 forks (April 2024 → June 2026 = ~2 years) [[1]](https://github.com/Dokploy/dokploy)
- 160+ releases; v0.29.7 shipped June 2, 2026 [[18]](https://github.com/Dokploy/dokploy/releases)
- 141 open PRs, 450 open issues as of June 2026 — active but backlog is growing [[1]](https://github.com/Dokploy/dokploy)
- 7.5M+ Docker Hub pulls claimed [[1]](https://github.com/Dokploy/dokploy)
