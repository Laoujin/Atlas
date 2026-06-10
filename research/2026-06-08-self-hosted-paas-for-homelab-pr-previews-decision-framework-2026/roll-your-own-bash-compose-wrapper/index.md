---
title: "Roll-Your-Own Bash/Compose Wrapper for PR Preview Environments"
date: 2026-06-08
depth: standard
format: md
topic: "Roll-your-own bash/compose wrapper"
topic_raw: "Roll-your-own bash/compose wrapper"
issue: 200
tags: [docker, docker-compose, bash, PR-preview, homelab, self-hosted, github-actions, traefik, nginx, webhook]
summary: "A field guide to wiring up a DIY bash + docker-compose PR preview stack on a single Debian VM: triggers, deploy scripts, reverse proxy, cleanup, and when it beats Coolify."
citations: 15
reading_time_min: 7
cover: cover.svg
cost_usd: 1.27
duration_sec: 455
model: "Sonnet 4.6"
---

> **TL;DR / Decision**
> Roll-your-own is fully viable on a single Debian/Docker VM and needs no PaaS. The core loop is ~150 lines of bash: a trigger (GitHub Actions self-hosted runner or [adnanh/webhook](https://github.com/adnanh/webhook) ⭐ 11.9k [[4]](https://github.com/adnanh/webhook)) fires `deploy.sh` on `pull_request` open/sync and `teardown.sh` on close. Traefik with wildcard DNS handles routing without any config-file reload. **Pick this** if you want full transparency and can spend 1–2 days on wiring. **Skip it** if you need managed database isolation, out-of-the-box HTTPS from minute one, or a UI — Coolify covers all of that at lower ops cost.

---

## How the Core Loop Works

Every PR preview system answers the same three questions:

1. **How does the server know a PR was opened/updated/closed?** → Trigger layer
2. **How does a new stack start up with a unique URL?** → Deploy script + reverse proxy
3. **How does it get torn down?** → Cleanup layer

A DIY stack gives you explicit control of all three, at the cost of assembling them yourself [[1]](https://oneuptime.com/blog/post/2026-01-30-preview-environments/view).

---

## Trigger Layer: Two Patterns

### Option A — GitHub Actions + Self-Hosted Runner (recommended entry point)

The lowest-friction wiring. No extra webhook server; GitHub orchestrates the lifecycle [[14]](https://oneuptime.com/blog/post/2025-12-20-preview-deployments-github-actions/view):

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, closed]

jobs:
  deploy:
    if: github.event.action != 'closed'
    runs-on: [self-hosted, linux]   # your Debian VM runner
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/deploy.sh ${{ github.event.pull_request.number }} ${{ github.head_ref }}

  cleanup:
    if: github.event.action == 'closed'
    runs-on: [self-hosted, linux]
    steps:
      - run: bash scripts/teardown.sh ${{ github.event.pull_request.number }}
```

The self-hosted runner ([myoung34/docker-github-actions-runner](https://github.com/myoung34/docker-github-actions-runner) ⭐ 2.3k [[13]](https://github.com/myoung34/docker-github-actions-runner)) runs in a container on the same Debian VM. It mounts `/var/run/docker.sock` so the deploy script can drive Docker on the host.

**Tradeoff:** GitHub initiates the connection outward — no open inbound ports needed. But your runner must have internet access and a GitHub token with `repo` scope.

### Option B — Standalone Webhook Server

[adnanh/webhook](https://github.com/adnanh/webhook) ⭐ 11.9k [[4]](https://github.com/adnanh/webhook) is a Go binary that listens for HTTP requests and executes shell scripts. Expose it behind Traefik or Cloudflare Tunnel; GitHub POSTs to it on PR events [[12]](https://github.com/adnanh/webhook/blob/master/docs/Hook-Examples.md).

```json
{
  "id": "pr-deploy",
  "execute-command": "/opt/preview/deploy.sh",
  "pass-arguments-to-command": [
    { "source": "payload", "name": "pull_request.number" },
    { "source": "payload", "name": "pull_request.head.ref" },
    { "source": "payload", "name": "action" }
  ],
  "trigger-rule": {
    "match": {
      "type": "payload-hmac-sha256",
      "secret": "YOUR_WEBHOOK_SECRET",
      "parameter": { "source": "header", "name": "X-Hub-Signature-256" }
    }
  }
}
```

Always validate HMAC — an open endpoint that runs shell scripts is a remote code execution vulnerability [[10]](https://theawesomegarage.com/blog/build-and-deploy-locally-using-github-actions-and-webhooks). Lighter alternatives: [staticfloat/docker-webhook](https://github.com/staticfloat/docker-webhook) ⭐ 85 [[5]](https://github.com/staticfloat/docker-webhook) (Python, simpler), [webhookd](https://www.libe.net/en/docker-webhook) [[8]](https://www.libe.net/en/docker-webhook) (bare bash path-to-script mapping) [[11]](https://blog.tymscar.com/posts/privategithubcicd/).

---

## The Deploy Script

`deploy.sh $PR_NUMBER $BRANCH`:

```bash
#!/usr/bin/env bash
set -euo pipefail
PR_NUMBER=$1
BRANCH=$2
PREVIEW_DIR="/opt/previews/pr-${PR_NUMBER}"
PROJECT="pr-${PR_NUMBER}"

# Clone or fast-forward
if [ -d "$PREVIEW_DIR/.git" ]; then
  git -C "$PREVIEW_DIR" fetch origin && git -C "$PREVIEW_DIR" checkout "$BRANCH" && git -C "$PREVIEW_DIR" pull
else
  git clone --branch "$BRANCH" git@github.com:YOUR_ORG/YOUR_REPO.git "$PREVIEW_DIR"
fi

# Write per-PR env
cat > "$PREVIEW_DIR/.env.preview" <<EOF
COMPOSE_PROJECT_NAME=${PROJECT}
APP_PORT=$((10000 + PR_NUMBER))
DATABASE_NAME=preview_${PR_NUMBER}
PREVIEW_URL=https://pr-${PR_NUMBER}.preview.example.com
EOF

cd "$PREVIEW_DIR"
docker compose -p "$PROJECT" -f docker-compose.yml -f docker-compose.preview.yml \
  --env-file .env.preview up -d --build
```

Key techniques [[1]](https://oneuptime.com/blog/post/2026-01-30-preview-environments/view) [[14]](https://oneuptime.com/blog/post/2025-12-20-preview-deployments-github-actions/view):

- **`COMPOSE_PROJECT_NAME=pr-$N`** isolates all containers, networks, and volumes for this PR so `docker compose down` only touches that PR's resources.
- **Port formula `10000 + PR_NUMBER`** gives deterministic, non-colliding ports without a port registry [[1]](https://oneuptime.com/blog/post/2026-01-30-preview-environments/view).
- **Override file** (`docker-compose.preview.yml`) applies resource limits (0.5 CPU, 512 MB RAM) and swaps hostnames without touching the main compose file [[15]](https://dev.to/ebrahimmfadae/docker-compose-setup-scripts-3mah).

`teardown.sh $PR_NUMBER`:

```bash
#!/usr/bin/env bash
set -euo pipefail
PR_NUMBER=$1
PREVIEW_DIR="/opt/previews/pr-${PR_NUMBER}"
docker compose -p "pr-${PR_NUMBER}" down -v --remove-orphans 2>/dev/null || true
rm -rf "$PREVIEW_DIR"
```

---

## Reverse Proxy: Traefik vs nginx

| | Traefik | nginx |
|---|---|---|
| Config on deploy | Docker label — no file write | Generate `.conf` + `nginx -s reload` |
| TLS | Automatic (Let's Encrypt via ACME) | `certbot certonly` per subdomain or wildcard |
| Wildcard routing | Native with `*.preview.` DNS + wildcard cert | Needs wildcard cert + `server_name ~^pr-(\d+)\.` regex |
| Learning curve | New mental model (routers/services/middlewares) | Familiar to most engineers |
| Hot-reload | Instant (watches Docker socket) | Requires `nginx -s reload` after each deploy |

Traefik is the better fit for ephemeral environments because every `docker compose up` auto-registers the preview without a config-file write [[9]](https://doc.traefik.io/traefik/reference/dynamic-configuration/docker/) [[3]](https://casparwre.de/blog/setting-up-preview-deployments/). Add these labels to `docker-compose.preview.yml`:

```yaml
services:
  app:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.pr-${PR_NUMBER}.rule=Host(`pr-${PR_NUMBER}.preview.example.com`)"
      - "traefik.http.routers.pr-${PR_NUMBER}.tls.certresolver=letsencrypt"
      - "traefik.http.services.pr-${PR_NUMBER}.loadbalancer.server.port=3000"
```

**DNS prerequisite:** a wildcard A record `*.preview.example.com → VM_IP` and a wildcard TLS certificate. Without this, every new PR requires a DNS change [[3]](https://casparwre.de/blog/setting-up-preview-deployments/).

nginx is workable if Traefik is unfamiliar — generate a `sites-enabled/pr-${PR_NUMBER}.conf` and reload. The [oneuptime.com](https://oneuptime.com/blog/post/2026-01-30-preview-environments/view) example does exactly this [[1]](https://oneuptime.com/blog/post/2026-01-30-preview-environments/view).

---

## Cleanup: The Hard Part

Three mechanisms, each catching a different failure mode [[2]](https://getautonoma.com/blog/preview-environments) [[3]](https://casparwre.de/blog/setting-up-preview-deployments/):

| Mechanism | Catches |
|---|---|
| `teardown.sh` on `pull_request: closed` | Normal PR lifecycle |
| Daily cron: `find /opt/previews -maxdepth 1 -mtime +7 -exec teardown.sh {} \;` | Stale PRs nobody closed |
| `docker system prune -f` weekly | Dangling images from failed builds |

The "destroy on PR close" event fires when PRs are merged **or** closed without merging. Long-lived branches that never get a PR, or webhook delivery failures, bypass this — the daily cron is the safety net [[2]](https://getautonoma.com/blog/preview-environments).

---

## Critical Pitfalls

| Pitfall | Impact | Mitigation |
|---|---|---|
| No HMAC validation on webhook endpoint | RCE on your VM | Always verify `X-Hub-Signature-256` [[12]](https://github.com/adnanh/webhook/blob/master/docs/Hook-Examples.md) |
| Shared production/staging DB | Data corruption across PRs | Spin a per-PR Postgres container; seed from a sanitized dump [[2]](https://getautonoma.com/blog/preview-environments) |
| No resource limits | One PR starves the host | Set `deploy.resources.limits` in the override file [[1]](https://oneuptime.com/blog/post/2026-01-30-preview-environments/view) |
| Port collisions > PR 1000 | Port `11000+` conflicts with nothing, but formula breaks for 5000+ | Fine for homelab; at scale use a dynamic port registry |
| Missing wildcard DNS/cert | Every new PR needs manual DNS update | Set up `*.preview.` record before starting |
| Leaked secrets in compose env | Credentials in `.env.preview` on disk | Mount secrets via Docker secrets or environment injection at runtime |
| Runner with docker.sock access | Privilege escalation from malicious PR code | Never run CI with host docker.sock on public repos [[10]](https://theawesomegarage.com/blog/build-and-deploy-locally-using-github-actions-and-webhooks) |

---

## Resource Footprint on a Single VM

A homelab Proxmox/Debian VM can comfortably host 10–15 simultaneous small preview environments before CPU/RAM contention becomes noticeable [[3]](https://casparwre.de/blog/setting-up-preview-deployments/). With `--memory=512m --cpus=0.5` limits per stack and a 4-vCPU/8 GB VM, that's roughly:

- **No DB per stack**: up to 20 concurrent previews
- **With Postgres per stack**: 8–10 concurrent previews (Postgres eats 100–200 MB at idle)
- **Build time**: `--build` on every push is the real bottleneck; layer caching (`DOCKER_BUILDKIT=1`, `cache_from:`) keeps incremental builds under 30 s for typical Node/Go apps

---

## Comparison: DIY vs PullPreview vs Coolify

| Dimension | DIY bash/compose | [PullPreview](https://pullpreview.com/) [[7]](https://pullpreview.com/) | Coolify |
|---|---|---|---|
| Setup time | 1–2 days | 30 min | 1–2 hours |
| Cost (software) | Free | €300/yr commercial | Free (OSS) |
| TLS | Manual cert/Traefik ACME | Caddy auto | Automatic |
| DB isolation | Manual (your script) | Manual | Manual |
| UI | None (logs only) | GitHub comment + SSH | Full web UI |
| Control | Complete | GitHub Action black box | Partial |
| Ops burden | High | Low (no server to manage) | Medium |
| Stale cleanup | Your cron | Platform policy | Automatic |
| Scales to | ~15 concurrent | Per-cloud-instance | ~50+ |

---

## The Homelab Pattern That Works

A practical single-VM setup seen in homelab communities [[6]](https://github.com/juftin/homelab) ⭐ 101 [[11]](https://blog.tymscar.com/posts/privategithubcicd/):

1. **Traefik** in a permanent compose stack with Docker socket access and wildcard cert
2. **Self-hosted GitHub Actions runner** in a container on the same VM
3. **`deploy.sh` / `teardown.sh`** checked into the target repo under `scripts/`
4. **Wildcard DNS** `*.preview.yourdomain.com → VM_IP`
5. **Cron** on the VM: `0 2 * * * /opt/preview/cron-cleanup.sh`

Total bash: ~200 lines. Total new infrastructure: one DNS record. Total dependencies: Docker, Traefik, a GitHub runner.

**When to pick this over Coolify:** you want to understand every layer, you have non-standard deployment needs (custom networking, special compose flags), or you're already comfortable operating Docker manually.

**When to pick Coolify instead:** you need a UI, you want automatic PR env creation with zero bash, or you value the managed certificate + reverse proxy + cleanup lifecycle over full control.
