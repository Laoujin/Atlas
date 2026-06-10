---
title: "Dokku: The 95 MB Git-Push PaaS"
date: 2026-06-08
depth: standard
format: md
topic: "Dokku"
topic_raw: "Dokku"
issue: 200
tags: [dokku, paas, self-hosted, homelab, heroku, git-push, docker, debian]
summary: "Dokku is the lightest self-hosted PaaS — 95 MB RAM idle, Heroku-compatible git-push workflow, excellent plugin ecosystem — ideal for single-server homelab but lacks native PR preview support and Docker Compose."
citations: 12
reading_time_min: 4
cover: cover.svg
cost_usd: 0.90
duration_sec: 334
model: "Sonnet 4.6"
---

> **Decision**: Pick Dokku for the absolute minimum platform footprint on a single Proxmox VM (95 MB idle [[5]](https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/)) when you live in the terminal and can wire GitHub Actions for PR previews. Skip it if you need native preview environments, a web UI, or Docker Compose — Coolify covers all three out of the box.

## What Is Dokku

[Dokku](https://dokku.com/) [[2]](https://dokku.com/) is an open-source, Docker-powered PaaS — [GitHub](https://github.com/dokku/dokku) ⭐ 31.9k (Jun 2026) [[1]](https://github.com/dokku/dokku) — that replicates the Heroku git-push workflow on a single Linux server. Started in 2013, v0.38.17 shipped June 3 2026, with 339 total releases and active maintenance (Shell 54%, Go 42%, MIT licence) [[1]](https://github.com/dokku/dokku).

Core idea: `git push dokku main` triggers a build, starts the container, and updates the Nginx reverse proxy — no additional orchestration required [[4]](https://dokku.com/docs/deployment/application-deployment/).

## Deployment Workflow

```bash
# On the Dokku host — one-time setup per app
dokku apps:create myapp
dokku postgres:create mydb && dokku postgres:link mydb myapp

# On your machine
git remote add dokku dokku@host:myapp
git push dokku main          # build → run → proxy update
```

Dokku auto-detects the builder [[11]](https://dokku.com/docs/deployment/builders/herokuish-buildpacks/):

| File in repo root | Builder         |
| :---------------- | :-------------- |
| `project.toml`    | Cloud Native Buildpacks (pack-cli) |
| `Dockerfile`      | `docker build`  |
| Neither           | Herokuish (Heroku v2a buildpacks) |

Apps must expose the `PORT` environment variable to receive HTTP traffic [[4]](https://dokku.com/docs/deployment/application-deployment/).

## System Requirements

| Requirement | Value |
| :---------- | :---- |
| OS          | Ubuntu 22.04/24.04 or Debian 11+ x64 / arm64 [[3]](https://dokku.com/docs/getting-started/installation/) |
| RAM (minimum) | 1 GB (swap acceptable) [[3]](https://dokku.com/docs/getting-started/installation/) |
| Platform idle RAM | ~95 MB — no UI overhead [[5]](https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/) |
| Boot time   | ~15 s [[5]](https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/) |
| Install     | `sudo DOKKU_TAG=v0.38.17 bash bootstrap.sh` |

Debian 11+ is explicitly supported [[3]](https://dokku.com/docs/getting-started/installation/) — no workarounds needed for a Proxmox Debian VM.

## Plugin Ecosystem

Zero databases are bundled; everything is opt-in [[10]](https://dokku.com/docs/community/plugins/). Official plugins are Dokku-maintained; community plugins carry no quality guarantee.

| Category   | Official plugins |
| :--------- | :--------------- |
| Databases  | PostgreSQL, MySQL, MariaDB, MongoDB, Redis, Memcached, Elasticsearch, ClickHouse, Meilisearch, RabbitMQ |
| SSL        | [dokku-letsencrypt](https://github.com/dokku/dokku-letsencrypt) ⭐ 1.1k — auto-renewing via cron [[7]](https://github.com/dokku/dokku-letsencrypt) |
| Schedulers | Kubernetes, Nomad (as alternatives to the default Docker scheduler) |
| Monitoring | Grafana / Graphite / Statsd |
| Auth       | HTTP Auth, Maintenance mode |

Let's Encrypt setup is three commands [[7]](https://github.com/dokku/dokku-letsencrypt):

```bash
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
sudo dokku letsencrypt:cron-job --add
dokku letsencrypt:enable myapp
```

## PR Preview Environments

**No native support.** Dokku has no built-in concept of per-PR deployments [[6]](https://haloy.dev/blog/self-hosted-deployment-tools-compared). Two community options exist:

**Option A — [dokku-pr-action](https://github.com/abulte/dokku-pr-action)** [[8]](https://github.com/abulte/dokku-pr-action): GitHub Action that creates a Dokku app on PR open, redeploys on push, and destroys on close. URL pattern: `{project}-refs-pull-{pr}-merge.domain.com`. Known issues: concurrent pushes hit deploy-lock failures; linked services (databases per preview) are not fully implemented.

**Option B — [dokku-deploy-system](https://github.com/signalwire-demos/dokku-deploy-system)** [[9]](https://github.com/signalwire-demos/dokku-deploy-system): A fuller scaffold with per-PR URLs, auto-SSL, multi-database support, Trivy vulnerability scanning, and automatic cleanup on PR close. Requirements: Ubuntu 22.04, 4+ GB RAM, public domain, GitHub org setup.

Both require SSH credentials wired into GitHub Actions and all management happens via CLI — no UI to view or debug preview environments. Coolify ships this as a first-class UI feature [[5]](https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/).

## Limitations

| Limitation                 | Impact for homelab / PR previews |
| :------------------------- | :------------------------------- |
| Single-server only [[6]](https://haloy.dev/blog/self-hosted-deployment-tools-compared)         | All apps + previews share one VM; no horizontal scale |
| No web UI [[12]](https://sliplane.io/blog/dokku-self-hosted-heroku-alternative)                  | SSH required for all management; steep ops curve for new team members |
| No Docker Compose [[5]](https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/)           | Multi-container apps decomposed into separate linked Dokku services |
| No RBAC [[6]](https://haloy.dev/blog/self-hosted-deployment-tools-compared)                     | Deployers share root-equivalent SSH access |
| No native PR previews [[8]](https://github.com/abulte/dokku-pr-action)      | Custom GitHub Actions glue required; database-per-preview is fragile |
| Community plugin quality [[6]](https://haloy.dev/blog/self-hosted-deployment-tools-compared) | Some plugins unmaintained on recent Dokku versions |

## Homelab / Proxmox VM Verdict

Dokku is the right choice when:
- You want a **1 GB RAM VM** to comfortably host 3–5 small apps [[3]](https://dokku.com/docs/getting-started/installation/)
- You're **CLI-native** and comfortable with SSH-based workflows [[12]](https://sliplane.io/blog/dokku-self-hosted-heroku-alternative)
- You want **zero platform cruft** — 95 MB idle leaves maximum headroom for app containers [[5]](https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/)
- PR previews are **one-repo, one-language** and you can absorb the GitHub Actions boilerplate [[8]](https://github.com/abulte/dokku-pr-action)

Skip Dokku and reach for Coolify when:
- Team members expect a **web dashboard** for deploy status and logs
- You need **native PR preview** environments without custom glue
- Apps use **Docker Compose** (multi-container stacks) [[5]](https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/)
- You want per-preview **isolated databases** without scripting [[9]](https://github.com/signalwire-demos/dokku-deploy-system)
