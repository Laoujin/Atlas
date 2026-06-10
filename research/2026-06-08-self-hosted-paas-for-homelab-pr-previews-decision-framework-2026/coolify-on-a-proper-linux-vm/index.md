---
title: "Coolify on a proper Linux VM: a decision framework for homelab PR-preview environments"
date: 2026-06-08
depth: deep
format: md
topic: "Coolify on a proper Linux VM"
topic_raw: "Coolify on a proper Linux VM"
issue: 200
tags: [coolify, self-hosted, paas, homelab, docker, proxmox, pr-previews]
cover: cover.svg
summary: "Coolify does native per-PR preview deploys and is the obvious homelab PaaS — but install it in a dedicated Debian VM, not an LXC or shared Docker host, and patch the Jan 2026 RCEs first."
citations: 47
reading_time_min: 9
cost_usd: 4.21
duration_sec: 423
model: "Opus 4.8"
---

> **Decision.** Want managed per-PR preview environments in your homelab with the least work? **[Coolify](https://github.com/coollabsio/coolify) ⭐ 57k (Jun 2026)** is the default pick — it and [Dokploy](https://github.com/dokploy/dokploy) ⭐ 35k (Jun 2026) are the *only* two self-hosted options with native PR previews [[37]](https://docs.dokploy.com/docs/core/comparison). But three caveats decide the build: **(1)** give it a **dedicated KVM VM**, not a Proxmox LXC and not your existing Docker host — it assumes it owns Docker, ports 80/443, and the daemon config [[1]](https://coolify.io/docs/get-started/installation)[[5]](https://proxmox.rdem-systems.com/en/blog/docker-vm-vs-lxc-proxmox/). **(2)** Run **v4.0.0-beta.445 or later** — Coolify disclosed 11 critical CVEs (CVSS up to 10.0, RCE-as-root) in January 2026 with ~52k instances exposed [[21]](https://thehackernews.com/2026/01/coolify-discloses-11-critical-flaws.html)[[22]](https://censys.com/advisory/cve-2025-64424-cve-2025-64420-cve-2025-64419). **(3)** Size for **4 GB+ RAM** and cap your previews manually — Coolify's control plane eats ~1 GB idle and previews have **no TTL or auto-expiry** [[18]](https://massivegrid.com/blog/coolify-resource-planning-multiple-apps/)[[9]](https://github.com/coollabsio/coolify/issues/9064). Prefer something that gets out of the way? **Dokploy** is the lighter, faster-idling rival; **Kamal** if you want no platform at all.

## Why this comes up: "a proper Linux VM"

Coolify's install script is **invasive by design**. It installs its own Docker Engine 24+, rewrites the Docker daemon and logging config, plants SSH keys for server management, installs CLI tools, and claims `/data/coolify` [[1]](https://coolify.io/docs/get-started/installation). The docs are blunt: *"It's best to use a fresh server for Coolify to avoid any conflicts with existing applications"* — and Docker installed via snap is explicitly unsupported [[1]](https://coolify.io/docs/get-started/installation). The official stance isn't enforced in code, but the friction is real, so "proper VM" is the right instinct.

The sharpest conflict is **ports**. Coolify has hardcoded port-80 validation: `coolify-proxy` refuses to start from the UI with *"Port 80 is in use"* even after you reconfigure it to custom ports, so coexisting with a pre-existing nginx/Traefik/Caddy on 80/443 is a documented pain point [[2]](https://github.com/coollabsio/coolify/issues/3693) ⭐ 57k. The dashboard's port 8000 *can* be moved via an upgrade-safe `docker-compose.override.yml` (keep the container port at 80, change only the host port), but **80 and 443 must stay free** for the bundled proxy if you want HTTPS [[3]](https://github.com/coollabsio/coolify/discussions/7814) ⭐ 57k. Conclusion: don't bolt Coolify onto a box already running a reverse proxy or app containers.

### Proxmox: VM, not LXC

If your homelab is Proxmox, the 2026 consensus is **KVM VM over LXC** for anything running Docker:

| Host model | Works? | Why / why not |
|---|---|---|
| **KVM VM (Debian/Ubuntu)** | ✓ recommended | Full kernel isolation, live migration, "standard Docker, no hacks"; costs ~256–512 MB extra RAM vs LXC [[5]](https://proxmox.rdem-systems.com/en/blog/docker-vm-vs-lxc-proxmox/) |
| **Privileged LXC + nesting** | ⚠ works with hacks | Needs `nesting=1,keyctl=1,fuse=1`, `lxc.apparmor.profile: unconfined`, empty `lxc.cap.drop`; lightweight and easy to migrate, but "the worst of both worlds" on isolation [[6]](https://beefb.one/posts/setting_up_coolify_in_proxmox/)[[5]](https://proxmox.rdem-systems.com/en/blog/docker-vm-vs-lxc-proxmox/) |
| **Unprivileged LXC** | ✗ broken | runc 1.2+ writes `net.ipv4.ip_unprivileged_port_start=0`, which the mapped root can't do without `CAP_NET_ADMIN`; the AppArmor probe also fails on host-root `/sys` paths [[4]](https://dev.to/mattercoder/docker-on-proxmox-lxc-what-actually-works-and-why-unprivileged-doesnt-45km) |

A dedicated Debian 12 VM sidesteps all of this. Coolify officially supports Debian 11/12, Ubuntu (all versions; non-LTS needs the manual install path), plus RHEL, SUSE, Arch, Alpine and Raspberry Pi OS 64-bit [[1]](https://coolify.io/docs/get-started/installation).

## The headline feature: per-PR preview environments

This is the reason most homelabbers reach for Coolify, and it delivers — with sharp edges.

**How it works.** Preview deploys are **off by default**; enable per-application [[7]](https://coolify.io/docs/applications/ci-cd/github/preview-deploy). Once on, every PR opened against the configured branch auto-deploys to a unique URL, and Coolify **tears the preview down automatically when the PR is merged or closed** [[7]](https://coolify.io/docs/applications/ci-cd/github/preview-deploy). Setup has three pillars:

1. **GitHub App** (recommended over plain webhooks/deploy keys) — only the App can post status comments back on the PR; it needs read access to administration + code and read/write on pull requests [[8]](https://billyle.dev/posts/adding-github-pull-request-preview-deployments-with-coolify).
2. **Wildcard DNS** — a `*` A record pointing at the server IP [[8]](https://billyle.dev/posts/adding-github-pull-request-preview-deployments-with-coolify).
3. **A URL template** accepting `{{pr_id}}` and `{{random}}`; preview env vars are isolated and never inherit production secrets [[10]](https://deepwiki.com/coollabsio/coolify/5.6-preview-deployments).

GitLab is supported through a parallel webhook path [[10]](https://deepwiki.com/coollabsio/coolify/5.6-preview-deployments). By default only repo members/collaborators trigger previews, and pre-existing PRs aren't deployed retroactively [[7]](https://coolify.io/docs/applications/ci-cd/github/preview-deploy).

**The sharp edges** — these matter more in a resource-bounded homelab than on a fat cloud box:

- **No cap, no TTL, no auto-expiry.** "Max Concurrent Builds" only limits *build* parallelism, not *running* previews — accumulating PRs can exhaust RAM/CPU and degrade production [[9]](https://github.com/coollabsio/coolify/issues/9064) ⭐ 57k. You must prune manually or via the API.
- **No automatic per-preview databases.** Unlike Vercel/Netlify/Northflank, Coolify doesn't fork or provision a fresh DB per preview; you wire that up yourself [[12]](https://northflank.com/blog/alternatives-railway-preview-environments)[[10]](https://deepwiki.com/coollabsio/coolify/5.6-preview-deployments).
- **Docker Compose container renaming.** Previews rewrite container names (`db-pr-295`, `frontend-pr-295`), which breaks hardcoded nginx upstreams and DB connection strings; the workaround is a separate DB plus env vars or `COOLIFY_BRANCH` [[11]](https://github.com/coollabsio/coolify/discussions/4708) ⭐ 57k.
- **Wildcard-TLS gotcha.** The default `{{pr_id}}.{{domain}}` produces a multi-level hostname that breaks single-level wildcard certs; switch the template to `{{pr_id}}-{{domain}}` [[8]](https://billyle.dev/posts/adding-github-pull-request-preview-deployments-with-coolify).

## What you get out of the box

Coolify v4.0.0 shipped **April 27, 2026** after ~two years in beta, with a reported 325,000+ users [[17]](https://temps.sh/blog/coolify-review-2026). It's an Apache-2.0 Laravel/PHP app orchestrated by Docker Compose, bundling Postgres, Redis, and a Soketi WebSocket server for real-time status events [[19]](https://github.com/coollabsio/coolify/blob/v4.x/CLAUDE.md) ⭐ 57k.

- **Deploy from anything:** GitHub, GitLab, Bitbucket, Gitea, via four build packs — Nixpacks (auto-detects language, generates a Dockerfile), Static, Dockerfile, and Docker Compose [[15]](https://coolify.io/docs/applications/build-packs/overview)[[20]](https://www.virtua.cloud/learn/en/concepts/coolify-vs-dokploy-self-hosted-paas).
- **One-click databases:** Postgres, MySQL, MariaDB, MongoDB, Redis, Clickhouse, KeyDB, Dragonfly — plus 280+ one-click services [[20]](https://www.virtua.cloud/learn/en/concepts/coolify-vs-dokploy-self-hosted-paas)[[13]](https://github.com/coollabsio/coolify) ⭐ 57k.
- **Reverse proxy + TLS:** Traefik or Caddy from one dashboard, with automatic Let's Encrypt provisioning and renewal per app [[16]](https://nextgrowth.ai/what-is-coolify/).
- **Multi-server:** v4 lets you add remote servers over SSH and deploy to any of them from one dashboard [[16]](https://nextgrowth.ai/what-is-coolify/).
- **Cost:** self-hosting is **free forever, no feature limits**; Coolify Cloud (managed control plane, bring-your-own servers) is $5/mo for 2 servers + $3/mo each extra [[14]](https://coolify.io/pricing).

**Sizing for a homelab.** Official minimum is 2 CPU / 2 GB RAM / 30 GB disk [[1]](https://coolify.io/docs/get-started/installation), but the control plane alone consumes ~1 GB idle, so **4 GB is the realistic floor** and 4 vCPU / 8 GB / 100 GB NVMe is the comfortable sweet spot for multi-app + preview workloads [[18]](https://massivegrid.com/blog/coolify-resource-planning-multiple-apps/).

## The skeptic's case (read this before you expose it)

Coolify's negatives are well-documented for 2025–2026 and several are serious.

- **Security — January 2026 critical disclosure.** 11 critical vulnerabilities (CVSS up to 10.0) enabling auth bypass, RCE, and root access; Censys counted ~52,650 publicly-exposed instances and warned *"the trivial nature of the exploit make active exploitation highly likely"* [[21]](https://thehackernews.com/2026/01/coolify-discloses-11-critical-flaws.html)[[22]](https://censys.com/advisory/cve-2025-64424-cve-2025-64420-cve-2025-64419). Notable CVEs among the 11 (rated up to 10.0): CVE-2025-64419 (9.7, command execution), CVE-2025-64420 (9.9, leaks the root user's private SSH key to low-privileged members), and CVE-2025-64424 (9.4, arbitrary commands by low-privileged members). Fixes land in **v4.0.0-beta.445+** [[22]](https://censys.com/advisory/cve-2025-64424-cve-2025-64420-cve-2025-64419). **Do not put the dashboard on the public internet without a VPN/tunnel and current patches.**
- **Data loss is real.** An Aug 2025 bug deletes manually-added Docker volumes when a Dockerfile service is stopped/redeployed, because *"Delete Unused Volumes"* is **on by default** [[23]](https://github.com/coollabsio/coolify/issues/6316) ⭐ 57k. Separately, a user permanently lost their Laravel `APP_KEY` because the web-UI update button isn't disabled after clicking — it re-ran the upgrade script repeatedly, yielding *"The MAC is invalid"* [[24]](https://github.com/coollabsio/coolify/discussions/3687) ⭐ 57k.
- **Proxy breakage recurs.** Malformed Traefik labels caused 502s across beta.418–434 — *"unusable for production without manual intervention after every deployment"* [[25]](https://github.com/coollabsio/coolify/issues/6877) ⭐ 57k — and a Docker 29.x API mismatch returned 503 for all apps until beta.444 [[26]](https://github.com/coollabsio/coolify/issues/7757) ⭐ 57k.
- **Stability + UX.** HN users report Docker-deployment bugs that erode trust plus unfixed random 100%-CPU spikes [[27]](https://news.ycombinator.com/item?id=43304612); a 2025 production comparison found too many clicks and full rebuilds on stop/start [[28]](https://blog.logrocket.com/dokploy-vs-coolify-production/).
- **Bus factor.** Coolify ran in production at thousands of companies while formally in beta the *entire time*, with the maintainer admitting *"it has many [bugs], but we fix them every day"* [[29]](https://wz-it.com/en/blog/coolify-v4-0-0-self-hosted-paas-heroku-alternative/). It's a small, bootstrapped, single-founder-led project [[46]](https://x.com/heyandras/status/1901894087604916396).

## Alternatives compared (for homelab PR previews)

Only Coolify and Dokploy do native PR previews; everything else needs custom CI or doesn't do them at all [[37]](https://docs.dokploy.com/docs/core/comparison)[[38]](https://getautonoma.com/blog/open-source-alternatives-vercel).

| Tool | ⭐ Stars | License | PR previews? | Compose? | Fit for this job |
|---|---|---|---|---|---|
| [Coolify][c] | ⭐ 57k | Apache-2.0 | ✓ native | ✓ | Default pick: most features, biggest catalog/community; heavier idle, the bugs above [[36]](https://api.github.com/repos/coollabsio/coolify)[[37]](https://docs.dokploy.com/docs/core/comparison) |
| [Dokploy][d] | ⭐ 35k | — | ✓ native | ✓ | Closest rival; Docker-Swarm multi-server, **lighter idle footprint**, smaller app catalog [[30]](https://api.github.com/repos/dokploy/dokploy)[[37]](https://docs.dokploy.com/docs/core/comparison)[[28]](https://blog.logrocket.com/dokploy-vs-coolify-production/) |
| [CapRover][cr] | ⭐ 15k | — | ✗ | partial | Polished but custom deploy format, no previews [[31]](https://api.github.com/repos/caprover/caprover)[[37]](https://docs.dokploy.com/docs/core/comparison) |
| [Dokku][dk] | ⭐ 32k | MIT | ✗ (plugin/manual) | ✗ | Git-push veteran, single-server; multi-env needs a plugin [[32]](https://api.github.com/repos/dokku/dokku)[[38]](https://getautonoma.com/blog/open-source-alternatives-vercel) |
| [Komodo][k] | ⭐ 11k | GPL-3.0 | ✗ | ✓ (stacks) | Rust fleet/container manager with Git build pipelines — Portainer-alt with CI/CD, not a preview PaaS [[33]](https://api.github.com/repos/moghtech/komodo)[[39]](https://chollinger.com/blog/2025/12/how-i-run-docker-services-and-deployments-with-komodo/) |
| [Portainer][p] | ⭐ 38k | Zlib | ✗ | ✓ | Container-management UI, not a deploy/preview platform [[34]](https://api.github.com/repos/portainer/portainer) |
| [Kamal][km] | ⭐ 14k | MIT | ✗ (custom CI) | n/a | 37signals SSH image-deploy tool, no web UI, no server abstraction [[35]](https://api.github.com/repos/basecamp/kamal)[[38]](https://getautonoma.com/blog/open-source-alternatives-vercel) |
| Plain Docker Compose | — | — | ✗ | ✓ | No preview automation at all [[38]](https://getautonoma.com/blog/open-source-alternatives-vercel) |

[c]: https://github.com/coollabsio/coolify
[d]: https://github.com/dokploy/dokploy
[cr]: https://github.com/caprover/caprover
[dk]: https://github.com/dokku/dokku
[k]: https://github.com/moghtech/komodo
[p]: https://github.com/portainer/portainer
[km]: https://github.com/basecamp/kamal

Install times on a Debian/Docker VM are comparable: ~30 min for Coolify (curl + UI), ~20 min for Dokku/CapRover, ~15 min for Kamal (YAML only) [[38]](https://getautonoma.com/blog/open-source-alternatives-vercel). **The real choice is Coolify vs Dokploy** — same feature, Coolify has the larger ecosystem and one-click catalog, Dokploy is leaner and stays out of the way [[28]](https://blog.logrocket.com/dokploy-vs-coolify-production/).

## Day-2 operations

- **Backups are split — and incomplete by default.** Scheduled database backups run `pg_dump`/`mysqldump`/`mongodump` on cron, stored locally and optionally pushed to S3-compatible storage (S3, MinIO, Backblaze B2, Cloudflare R2, Wasabi) [[41]](https://coolify.io/docs/knowledge-base/s3/). Coolify's *own* instance backup covers dashboard settings, its Postgres state, SSH keys at `/data/coolify/ssh/keys`, and the `APP_KEY` in `/data/coolify/source/.env` — but **explicitly not your application volume data**, which you back up manually [[40]](https://coolify.io/docs/knowledge-base/how-to/backup-restore-coolify).
- **Upgrades:** three modes — fully automatic (CDN-polled self-update), semi-automatic (UI button on notification), and manual (`curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash`). Docs insist you **back up before every upgrade** [[42]](https://coolify.io/docs/get-started/upgrade). Given the data-loss reports above, prefer manual/semi-automatic and snapshot the VM first.
- **Monitoring:** per-channel event routing to Email/SMTP/Resend, Telegram, Discord, Slack/Mattermost, Pushover, and webhooks — for deployment, backup, scheduled-task, disk-usage, and server-reachable events [[43]](https://coolify.io/docs/knowledge-base/notifications).

## How we got here

v4 is a complete ground-up rewrite (announced April 2023), moving off v3's SvelteKit/Node stack to Laravel/PHP to make it *"more professional — it is not a side-project anymore"* [[44]](https://github.com/coollabsio/coolify/discussions/1027) ⭐ 57k. The project is bootstrapped and profitable: founder Andras Bacsai reported Feb 2025 net income ~$12,900 (Coolify Cloud + donations), has declined VC, and funds via sponsors and the $5/mo Cloud tier [[46]](https://x.com/heyandras/status/1901894087604916396)[[47]](https://coolify.io/sponsorships)[[45]](https://coolify.io/docs/get-started/cloud). At ⭐ 57k stars and 325k+ users it's the clear category leader [[36]](https://api.github.com/repos/coollabsio/coolify)[[17]](https://temps.sh/blog/coolify-review-2026) — with the maturity-vs-churn tradeoff that implies.

## Bottom line

For a Debian/Docker/Proxmox homelab that wants per-PR preview environments, **Coolify in a dedicated KVM VM, patched to the latest release, behind a VPN or Cloudflare tunnel, with previews pruned manually** is the strong default. If you value low idle footprint and a tool that layers less of its own logic on top of Compose, **Dokploy** is the credible swap with the same headline feature. Everything else means writing your own preview automation.
