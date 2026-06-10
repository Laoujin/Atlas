---
layout: expedition
title: "Self-Hosted PaaS for Homelab PR Previews: Decision Framework 2026"
date: 2026-06-08
topic: "Decision framework: self-hosted PaaS for homelab PR preview environments on a Debian+Docker Proxmox VM (2026) — Coolify vs roll-your-own vs alternatives."
format: md
tags: [self-hosted, paas, pr-previews, homelab, docker]
summary: "Only Coolify and Dokploy deploy PR previews natively; both bundle Traefik and demand dedicated VM isolation from your existing proxy — the full decision framework across six options on ten criteria."
cover: cover.svg
synthesis: true
children:
  - slug: coolify-on-a-proper-linux-vm
    title: "Coolify on a proper Linux VM"
    depth: deep
    status: success
    summary: "Coolify does native per-PR preview deploys and is the obvious homelab PaaS — but install it in a dedicated Debian VM, not an LXC or shared Docker host, and patch the Jan 2026 RCEs first."
    citations: 47
    reading_time_min: 9
  - slug: roll-your-own-bash-compose-wrapper
    title: "Roll-your-own bash/compose wrapper"
    depth: standard
    status: success
    summary: "A field guide to wiring up a DIY bash + docker-compose PR preview stack on a single Debian VM: triggers, deploy scripts, reverse proxy, cleanup, and when it beats Coolify."
    citations: 15
    reading_time_min: 7
  - slug: dokploy
    title: "Dokploy"
    depth: standard
    status: success
    summary: "Dokploy is a Docker-native open-source PaaS (⭐ 34.6k) with first-class PR preview deployments, Swarm-based multi-node scaling, and an AI-powered CLI/MCP server — at the cost of a mixed license model and a known memory regression."
    citations: 18
    reading_time_min: 4
  - slug: caprover
    title: "CapRover"
    depth: standard
    status: success
    summary: "CapRover is battle-tested and resource-light but lacks native PR preview environments and true multi-service Docker Compose support, making it a poor fit for dynamic preview workflows in 2026."
    citations: 10
    reading_time_min: 4
  - slug: dokku
    title: "Dokku"
    depth: standard
    status: success
    summary: "Dokku is the lightest self-hosted PaaS — 95 MB RAM idle, Heroku-compatible git-push workflow, excellent plugin ecosystem — ideal for single-server homelab but lacks native PR preview support and Docker Compose."
    citations: 12
    reading_time_min: 4
  - slug: kamal-2
    title: "Kamal 2"
    depth: ceo
    status: success
    summary: "Kamal 2 is a minimal Docker deployment tool optimized for simplicity and resource efficiency. Pick it if you need SSH-based deployments with infrastructure-as-code; pick Coolify if you want a PaaS dashboard."
    citations: 7
    reading_time_min: 2
  - slug: secrets-and-credential-handling-across-options
    title: "Secrets and credential handling across options"
    depth: ceo
    status: success
    summary: "Environment variables alone are insufficient for secrets in 2026; use a secrets manager for sensitive data and environment variables only for non-sensitive config."
    citations: 7
    reading_time_min: 2
cost_usd: 9.33
duration_sec: 2589
citations: 116
reading_time_min: 32
issue: 200
model: "Sonnet 4.6"
---

The sharpest divide across all six options is not feature richness or resource cost — it is **whether PR preview automation is a platform feature or something you write**. Only [Coolify](https://coolify.io/docs/applications/ci-cd/github/preview-deploy) [[1]](https://coolify.io/docs/applications/ci-cd/github/preview-deploy) and [Dokploy](https://docs.dokploy.com/docs/core/applications/preview-deployments) [[2]](https://docs.dokploy.com/docs/core/applications/preview-deployments) cross that line: both tear previews down automatically on PR close, post status comments via GitHub App, and isolate preview env vars from production secrets — without a line of custom shell. CapRover, Dokku, and Kamal all converge on the same GitHub Actions glue pattern once you bolt on PR preview support; at that point the PaaS layer stops earning its overhead relative to DIY.

**The Traefik conflict is the second major gate.** Your existing Traefik reverse proxy cannot peacefully coexist with either native-preview option on the same host: Coolify bundles its own Traefik/Caddy and hardcodes a port-80 validation check that prevents it starting alongside any pre-existing proxy [[3]](https://github.com/coollabsio/coolify/issues/3693); Dokploy installs Traefik at setup time. The resolution — a dedicated KVM VM that the PaaS fully controls [[4]](https://coolify.io/docs/get-started/installation) — adds VM sprawl but eliminates all port contention. DIY bash, Dokku, and Kamal compose cleanly with an existing Traefik via Docker labels, no port negotiation, no second proxy.

**Coolify vs Dokploy** is the only matchup that matters once you decide to use a PaaS. Coolify leads on catalog depth (280+ one-click services [[5]](https://coolify.io/docs/applications/build-packs/overview)), ecosystem size (⭐ 57k, 325k users [[6]](https://temps.sh/blog/coolify-review-2026)), and built-in secrets quality (encrypted-at-rest + Docker Build Secrets [[7]](https://coolify.io/docs/knowledge-base/environment-variables)). Dokploy leads on backup (S3 volume backups and a DB restore UI that Coolify lacks [[8]](https://getdeploying.com/guides/coolify-vs-dokploy)), a configurable max-previews cap (Coolify still has no per-app TTL or expiry [[9]](https://github.com/coollabsio/coolify/issues/9064)), and lighter idle RAM (~630 MB vs 800 MB–1.2 GB [[10]](https://contabo.com/blog/blog-coolify-vs-dokploy-comparison/)[[11]](https://github.com/Dokploy/dokploy/issues/3755)). For many homelabbers the deciding input will be Coolify's January 2026 disclosure of 11 critical CVEs (CVSS up to 10.0, including RCE-as-root and SSH key leakage to low-privileged members [[12]](https://thehackernews.com/2026/01/coolify-discloses-11-critical-flaws.html)[[13]](https://censys.com/advisory/cve-2025-64424-cve-2025-64420-cve-2025-64419)) — patched in beta.445+ / v4 GA, but a meaningful signal about the platform's security posture. The dashboard must not be internet-exposed without a VPN or Cloudflare tunnel regardless of option.

**The `GITHUB_TOKEN` footgun** documented in the 2026-04-27 Synology expedition applies to every path that uses GitHub Actions self-hosted runners for deployment: `GITHUB_TOKEN` cannot trigger downstream GitHub Actions workflows on the same repository [[14]](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication), so CI jobs that depend on `pull_request` events emitted from the runner silently never fire. This affects DIY bash, CapRover, Dokku, and Kamal — all of which rely on runner-initiated token calls. The fix (a GitHub App installation token generated in the workflow) is one-time setup overhead that Coolify and Dokploy bypass entirely: they use webhook-based GitHub App flows that GitHub recognizes as distinct from runner events and honors for downstream CI triggers.

**Secrets** is the quietest cross-cutting differentiator. Coolify's encrypted storage + Docker BuildKit secrets is the best built-in story [[7]](https://coolify.io/docs/knowledge-base/environment-variables). DIY bash, Dokku, and Kamal default to plaintext `.env` files on disk — fine for a solo homelab, a meaningful gap the moment a second person gets shell access. Layering [Infisical](https://github.com/Infisical/infisical) [[15]](https://github.com/Infisical/infisical) on any of these closes the gap but adds operational surface. CapRover and Dokku lack role-based access entirely, so even encrypted env vars are visible to all deployers.

**r/selfhosted 2026 consensus**: Coolify is the default recommendation (⭐ 57k, 325k users [[6]](https://temps.sh/blog/coolify-review-2026)); Dokploy is the rising lightweight alternative, specifically praised for native PR previews [[16]](https://www.cherryservers.com/blog/coolify-vs-dokploy); CapRover is respected for 9-year stability but in slow-burn mode [[17]](https://kloudshift.net/blog/comparing-self-hostable-paas-solutions-caprover-coolify-dokploy-reviewed/); Dokku retains a terminal-native following for its 95 MB idle footprint [[18]](https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/).

The open question this expedition doesn't close: **whether Dokploy's v0.27+ memory regression — idle RAM doubled, suspected cause identified but issue closed without a confirmed fix [[11]](https://github.com/Dokploy/dokploy/issues/3755) — gets resolved before it forces a de facto 4 GB minimum on an already headroom-constrained Proxmox VM running two apps and five to ten concurrent previews**.

---

## Comparison Table

| Option               | PR preview trigger        | Custom glue remaining                          | Traefik coexist      | GH integration             | Idle RAM       | Secrets                  | Backup / state         | Self-update              | Multi-app/env             | Maturity / consensus                                        |
|----------------------|---------------------------|------------------------------------------------|----------------------|----------------------------|----------------|--------------------------|------------------------|--------------------------|---------------------------|-------------------------------------------------------------|
| **Coolify** ⭐ 57k   | Native — GitHub App [[t1]][t1] | DB-per-preview script; TTL/expiry cron [[t2]][t2] | ❌ owns 80/443 [[t3]][t3] | Excellent — PR comments [[t1]][t1] | 800 MB–1.2 GB [[t4]][t4] | Encrypted + BuildKit [[t5]][t5] | Partial (no vols) [[t6]][t6] | 3 modes; snapshot first | ✓ full, 280 templates   | v4 GA Apr 2026; 11 CVEs Jan 2026 [[t7]][t7][[t8]][t8]       |
| **Dokploy** ⭐ 35k   | Native — webhook/GH App [[t9]][t9] | Wildcard DNS; max-preview config [[t9]][t9]    | ❌ bundles Traefik   | Good — 5 git providers     | ~630 MB+ [[t10]][t10] | Env vars              | S3 vols + DB UI [[t11]][t11] | Docker-based             | ✓ Swarm-native            | Apr 2024; memory regression v0.27+ [[t10]][t10]             |
| **DIY bash**         | GH Actions self-hosted runner [[t12]][t12] | ~200 lines bash (deploy+teardown+cron) [[t12]][t12] | ✓ labels only   | GH Actions + HMAC webhook  | ~0 MB platform | Manual .env / Docker secrets | Manual cron              | n/a                      | Manual per-repo           | Community-proven; full control [[t12]][t12]                 |
| **CapRover** ⭐ 15k  | REST API + GH Actions [[t13]][t13] | Full lifecycle: create/build/post/delete app   | ❌ owns nginx        | Webhook — one branch/app   | ~350 MB [[t14]][t14] | Basic env vars        | Manual                 | UI-driven, quarterly     | Single-tenant; Swarm clustering | 2017; slow-burn since 2024 [[t15]][t15]                |
| **Dokku** ⭐ 32k     | Community plugin (fragile) [[t16]][t16] | SSH wiring + GH Actions + plugin config   | ✓ nginx compat       | Git-push SSH               | ~95 MB [[t17]][t17] | Env vars only         | Plugin-based           | `bootstrap.sh`           | Single-server; plugin ecosystem | 2013; active MIT; 339 releases [[t17]][t17]          |
| **Kamal 2** ⭐ 14k   | Custom GH Actions + scripts | Full preview lifecycle + registry push step    | ✓ kamal-proxy        | GH Actions + Docker registry | ~0 MB platform | `.kamal/secrets` file  | None built-in          | `gem update kamal`       | Multi-server SSH          | 37signals-backed; powers HEY.com; no UI [[t18]][t18]        |

[t1]: https://coolify.io/docs/applications/ci-cd/github/preview-deploy
[t2]: https://github.com/coollabsio/coolify/issues/9064
[t3]: https://github.com/coollabsio/coolify/issues/3693
[t4]: https://contabo.com/blog/blog-coolify-vs-dokploy-comparison/
[t5]: https://coolify.io/docs/knowledge-base/environment-variables
[t6]: https://coolify.io/docs/knowledge-base/how-to/backup-restore-coolify
[t7]: https://thehackernews.com/2026/01/coolify-discloses-11-critical-flaws.html
[t8]: https://censys.com/advisory/cve-2025-64424-cve-2025-64420-cve-2025-64419
[t9]: https://docs.dokploy.com/docs/core/applications/preview-deployments
[t10]: https://github.com/Dokploy/dokploy/issues/3755
[t11]: https://getdeploying.com/guides/coolify-vs-dokploy
[t12]: https://oneuptime.com/blog/post/2026-01-30-preview-environments/view
[t13]: https://caprover.com/docs/deployment-methods.html
[t14]: https://massivegrid.com/blog/dokploy-vs-coolify-vs-caprover/
[t15]: https://kloudshift.net/blog/comparing-self-hostable-paas-solutions-caprover-coolify-dokploy-reviewed/
[t16]: https://github.com/abulte/dokku-pr-action
[t17]: https://selfhostable.dev/blog/coolify-vs-caprover-vs-dokku/
[t18]: https://dev.37signals.com/kamal-2/

---

## Remaining Custom Glue per Option

### Coolify

One-time setup: configure the GitHub App and grant it read on administration + code, read/write on pull requests [[1]](https://coolify.io/docs/applications/ci-cd/github/preview-deploy). After that, no deployment scripts. What remains:

- **Per-preview DB script** — Coolify does not provision isolated databases per preview; wire a `docker compose exec` or API call to create `preview_<pr_number>` schemas and seed from a sanitized dump.
- **TTL/expiry cron** — Coolify has no auto-expiry for running previews [[9]](https://github.com/coollabsio/coolify/issues/9064); add a cron job that calls the Coolify API to list and delete previews older than N days.
- **Wildcard TLS template** — use `{{pr_id}}-{{domain}}` (dash-separated), not `{{pr_id}}.{{domain}}` (dot-separated); the latter produces multi-level subdomains that break single-level wildcard certificates [[19]](https://billyle.dev/posts/adding-github-pull-request-preview-deployments-with-coolify).

### Dokploy

One-time setup: link a git provider, enable preview deployments, configure the max-preview cap (default: 3). What remains:

- **Wildcard DNS** — point `*.yourdomain.com` at the VM IP, or skip DNS entirely and use the built-in `preview-${appName}-${id}.traefik.me` free subdomain (no DNS change required) [[2]](https://docs.dokploy.com/docs/core/applications/preview-deployments).
- **S3 backup destination** — configure once in settings; Dokploy handles scheduling automatically.
- Nothing else. Dokploy's built-in max-preview cap and auto-cleanup on PR close mean no expiry cron is needed.

### DIY bash/compose

Estimated 200 lines across three files [[20]](https://oneuptime.com/blog/post/2026-01-30-preview-environments/view):

- `scripts/deploy.sh` — clone or fast-forward the PR branch, write per-PR `.env.preview` (project name, port formula, preview URL), run `docker compose -p pr-$N -f docker-compose.yml -f docker-compose.preview.yml up -d --build`.
- `scripts/teardown.sh` — `docker compose -p pr-$N down -v --remove-orphans && rm -rf /opt/previews/pr-$N`.
- `cron-cleanup.sh` — `find /opt/previews -maxdepth 1 -mtime +7 -exec teardown.sh {} \;` as a daily safety net.
- GitHub Actions workflow: `pull_request: [opened, synchronize, reopened, closed]` → dispatch to the self-hosted runner.
- `docker-compose.preview.yml` — Traefik labels (`traefik.http.routers.pr-$N.rule=Host(...)`) and resource limits (`memory: 512m`, `cpus: 0.5`).
- HMAC validation if using [adnanh/webhook](https://github.com/adnanh/webhook) [[21]](https://github.com/adnanh/webhook) instead of the self-hosted runner.
- GitHub App installation token in the workflow if downstream CI pipelines must trigger from PR events.

### CapRover

No native PR concept. The minimum viable glue:

- GitHub Actions job on `pull_request opened/synchronize`: call CapRover REST API to create an app named `pr-{number}`, set the branch, trigger a build, post the preview URL as a PR comment via the GitHub API.
- GitHub Actions job on `pull_request closed`: call CapRover REST API to delete the app.
- Estimated: 80–120 lines of YAML + shell (or a JavaScript Action) for the REST lifecycle [[22]](https://caprover.com/docs/deployment-methods.html).
- Wildcard DNS and SSL still require the same one-time setup as any other option.
- GitHub App installation token required for downstream CI to trigger.

### Dokku

No native PR concept. Two community paths, both incomplete [[23]](https://github.com/abulte/dokku-pr-action):

- **[dokku-pr-action](https://github.com/abulte/dokku-pr-action)**: GitHub Action that creates a Dokku app on open, redeploys on push, destroys on close. Known failure: concurrent pushes hit Dokku's deploy lock; per-preview databases unimplemented.
- **Custom lifecycle (~150 lines)**: SSH into the Dokku host from GitHub Actions, run `dokku apps:create pr-$N`, `dokku git:sync`, `dokku ps:scale web=1`, `dokku apps:destroy pr-$N` on close.
- In both cases: SSH key wired into GitHub Actions secrets, GitHub App installation token for downstream CI, and Dokku's Let's Encrypt plugin for per-app TLS.

### Kamal 2

No platform awareness of PRs at all. Full lifecycle is custom CI:

- `kamal deploy` on `pull_request opened/synchronize` — with a per-PR `config/deploy.yml` that sets a unique `app: myapp-pr-$N` and destination host.
- Registry push step in CI (Kamal requires a Docker registry; images must exist before deploy).
- `kamal remove` on `pull_request closed`.
- No management UI — all status comes from CI logs or the Docker daemon on the target server.
- Effectively equivalent scope to DIY bash, with a cleaner deployment primitive but less homelab community documentation for this pattern.

---

## Decision Rubric

**Pick Coolify** if you want the richest self-hosted PaaS (UI, monitoring, 280+ one-click services, native PR previews out of the box) and can afford to: dedicate a 4 GB+ KVM VM to it, keep it patched to the latest release, and place the dashboard behind a VPN. The DSM-installer limitation from the 2026-04-27 Synology expedition is gone — a Debian VM is the correct host and Coolify installs cleanly.

**Pick Dokploy** if native PR previews and better backup hygiene (S3 volume backups, DB restore UI) matter more than catalog depth, and if Coolify's January 2026 CVE disclosure makes you want the less-audited-but-less-targeted alternative. Verify the v0.27+ memory regression is resolved, or provision 6 GB+ to absorb it safely.

**Pick DIY bash/compose** if your existing Traefik lives on the shared Docker host and you cannot (or will not) provision a second VM, you want every layer of the preview lifecycle to be code you own and understand, and you can spend 1–2 days on initial wiring. The ongoing maintenance cost is low once the scripts stabilise.

**Pick Dokku** if absolute minimum platform RAM (95 MB) is the constraint, you have one or two small apps, and a CLI-native git-push workflow is sufficient. Use `dokku-pr-action` for previews accepting its fragility, or skip previews entirely.

**Pick CapRover** if you deploy only single-container apps, need the lowest idle RAM among GUI-having PaaSes (~350 MB), and PR preview is not a primary workflow — the full scripted lifecycle via the REST API is functional but is table stakes you write yourself.

**Pick Kamal 2** if you ship pre-built images from a Docker registry, want zero platform RAM overhead, prefer infrastructure-as-code YAML over a dashboard, and are comfortable writing the entire PR preview lifecycle in CI — there is no PaaS layer helping you here, but there is also nothing in the way.
