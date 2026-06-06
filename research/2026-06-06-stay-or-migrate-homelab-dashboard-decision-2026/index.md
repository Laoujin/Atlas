---
layout: expedition
title: "Stay or migrate: homelab dashboard decision 2026"
date: 2026-06-06
topic: "Stay or migrate: evidence-based dashboard recommendation for a Proxmox/Docker gitops homelab (2026)"
format: auto
tags: [homelab, dashboard, self-hosted, gitops, homepage]
summary: "Homepage wins all decisive criteria for a Proxmox/Docker gitops homelab — 6/6 target integrations, pure-YAML config-as-code, 80 MB lean footprint — with Glance as the only credible challenger to watch."
cover: cover.svg
synthesis: true
children:
  - slug: homepage-project-health-deep-dive
    title: "Homepage project health deep dive"
    depth: deep
    status: success
    summary: "Homepage is healthy and dominant on every adoption signal, but rests on a one-maintainer bus factor and an aggressively automated, maintainer-gated issue tracker."
    citations: 42
    reading_time_min: 7
  - slug: config-as-code-gitops-compatibility-matrix
    title: "Config-as-code & gitops compatibility matrix"
    depth: standard
    status: success
    summary: "Compatibility matrix across config formats (Helm, Kustomize, Jsonnet, HCL) and IaC tools (Terraform, Pulumi, Crossplane, Ansible) vs GitOps operators (Argo CD, Flux CD) — what's native, what needs a bridge, and what won't fit."
    citations: 19
    reading_time_min: 5
  - slug: integration-coverage-pi-hole-proxmox-uptime-kuma-docker-jellyfin-http-ping
    title: "Integration coverage: Pi-hole, Proxmox, Uptime Kuma, Docker, Jellyfin, HTTP/ping"
    depth: standard
    status: success
    summary: "Coverage matrix for Pi-hole, Proxmox, Uptime Kuma, Docker, Jellyfin and HTTP/ping across the three leading self-hosted dashboards — with per-widget data details and caveats."
    citations: 20
    reading_time_min: 4
  - slug: resource-footprint-auth-model-reverse-proxy-fit
    title: "Resource footprint, auth model & reverse-proxy fit"
    depth: standard
    status: success
    summary: "Homepage is lean (~50–150 MB RAM), has zero built-in auth by design, and integrates cleanly with Traefik, Caddy, and nginx via forward auth—HOMEPAGE_ALLOWED_HOSTS must list every non-localhost hostname since v1.0."
    citations: 16
    reading_time_min: 5
cost_usd: 11.61
duration_sec: 3529
citations: 97
reading_time_min: 21
issue: 193
model: "Sonnet 4.6"
---

**Stay with Homepage** — or adopt it if you haven't yet. It is the only candidate in this survey covering all six target service types (Pi-hole [[1]](https://gethomepage.dev/widgets/services/pihole/), Proxmox [[2]](https://gethomepage.dev/widgets/services/proxmox/), Uptime Kuma [[3]](https://gethomepage.dev/widgets/services/uptime-kuma/), Docker socket [[4]](https://gethomepage.dev/configs/docker/), Jellyfin [[5]](https://gethomepage.dev/widgets/services/jellyfin/), HTTP/ping [[6]](https://gethomepage.dev/configs/services/)) while also being purely YAML-file-driven, git-deployable (`git pull --ff-only && docker compose up -d`), and running at 80 MB image / 50–150 MB idle RAM [[7]](https://hub.docker.com/r/gethomepage/homepage)[[8]](https://github.com/gethomepage/homepage/discussions/6251). No other candidate scores ≥ 3/5 on all three decisive axes simultaneously. Homarr v1.x self-disqualified on two hard requirements at once: it dropped HTTP/ping and Uptime Kuma [[9]](https://github.com/ajnart/homarr/issues/814) while adding a RAM regression to 200–600 MB [[10]](https://github.com/homarr-labs/homarr/issues/3759) and shifting from YAML toward a DB/click-ops model. **Migration in:** Docker label auto-discovery (`homepage.name`, `homepage.icon`, `homepage.href`) bootstraps ~80% of a tile layout from an existing Compose stack with no manual entry [[11]](https://gethomepage.dev/configs/docker/).

## Scored matrix

| Project                       | (1) Health                                      | (2) GitOps                                       | (3) Integrations                                  | (4) Footprint                                    | (5) Auth/Proxy                                   | (6) UX/Maint                                      | (7) License                   |  Σ  |
|-------------------------------|--------------------------------------------------|--------------------------------------------------|---------------------------------------------------|--------------------------------------------------|--------------------------------------------------|---------------------------------------------------|-------------------------------|-----|
| **[Homepage][hp]** ⭐ 31k      | **4** — monthly rels, bus=1 [[1]][r1]            | **5** — pure YAML files, git-native [[2]][r2]    | **5** — 6/6 target svcs [[3]][r3]                 | **4** — 80 MB img / 150 MB RAM [[4]][r4]         | **4** — fwd-auth; ALLOWED_HOSTS req [[5]][r5]    | **4** — clean UI; yaml-brittle [[6]][r6]           | **5** — MIT [[7]][r7]         | **31** |
| **[Glance][gl]** ⭐ 35k        | **5** — 35k⭐, 2024, fastest-rising [[8]][r8]   | **5** — single config.yaml [[9]][r9]             | **2** — no Pi-hole/Proxmox/UK/Jelly [[10]][r10]   | **5** — single binary, <30 MB [[11]][r11]        | **3** — reverse proxy only [[12]][r12]           | **4** — column layout, low maint [[13]][r13]       | **4** — AGPL-3.0, FOSS [[14]][r14] | **28** |
| **[Dashy][da]** ⭐ 25k         | **4** — 25k⭐, 525 cmts/90d [[15]][r15]         | **4** — YAML primary; GUI also writes [[16]][r16] | **3** — 4/6; no Jellyfin, no Docker API [[17]][r17] | **3** — ~150 MB RAM, 90 MB img [[18]][r18]     | **4** — built-in basic/LDAP/SSO [[19]][r19]     | **5** — most themes, icons, sections [[20]][r20]   | **5** — MIT [[21]][r21]       | **28** |
| **[Homarr][hm]** ⭐ 4k         | **4** — active rewrite (homarr-labs) [[22]][r22] | **2** — DB+UI; YAML export only [[23]][r23]      | **3** — 4/6; HTTP/ping & UK dropped [[24]][r24]   | **2** — 200–600 MB v1.x regress [[25]][r25]     | **5** — built-in user/role mgmt [[26]][r26]     | **5** — drag-drop, polished UI [[27]][r27]         | **5** — MIT [[28]][r28]       | **26** |
| **[Homer][ho]** ⭐ 11k         | **3** — stable, low-cadence [[29]][r29]          | **5** — static YAML, zero server state [[30]][r30] | **1** — bookmarks only, no widgets [[31]][r31]   | **5** — ~30 MB RAM, <10 MB img [[32]][r32]      | **3** — proxy only, no built-in [[33]][r33]     | **3** — clean; no live data [[34]][r34]            | **5** — Apache-2.0 [[35]][r35] | **25** |
| **[Organizr][or]** ⭐ 5.8k     | **2** — low cadence, occasional updates [[36]][r36] | **1** — DB-only; **disqualifier** [[37]][r37] | **3** — iFrame tabs, Plex focus [[38]][r38]       | **3** — moderate; PHP/nginx [[39]][r39]          | **4** — group-based fwd-auth, SSO [[40]][r40]   | **4** — tabs, highly customizable [[41]][r41]      | **5** — MIT [[42]][r42]       | **22** |
| **[Flame][fl]** ⭐ 6.4k        | **2** — low cadence, not dead [[43]][r43]        | **2** — env vars + REST API, no YAML [[44]][r44] | **1** — bookmarks + weather only [[45]][r45]      | **5** — very lean, small binary [[46]][r46]     | **2** — simple password only [[47]][r47]        | **3** — simple, limited themes [[48]][r48]         | **5** — MIT [[49]][r49]       | **20** |
| **[Heimdall][he]** ⭐ 9.2k     | **1** — stalled 7+ mo; replacements [[50]][r50] | **1** — SQLite DB; **disqualifier** [[51]][r51]  | **2** — enhanced apps, limited data [[52]][r52]   | **3** — moderate; PHP/nginx [[53]][r53]          | **2** — basic; proxy passthrough [[54]][r54]    | **3** — clean tiles, dated UI [[55]][r55]          | **4** — MIT (stalled) [[56]][r56] | **16** |

[hp]: https://github.com/gethomepage/homepage
[gl]: https://github.com/glanceapp/glance
[da]: https://github.com/lissy93/dashy
[hm]: https://github.com/homarr-labs/homarr
[ho]: https://github.com/bastienwirtz/homer
[or]: https://github.com/causefx/Organizr
[fl]: https://github.com/pawelmalak/flame
[he]: https://github.com/linuxserver/Heimdall

[r1]:  https://github.com/gethomepage/homepage/releases/tag/v1.13.1
[r2]:  https://gethomepage.dev/configs/services/
[r3]:  https://gethomepage.dev/widgets/services/
[r4]:  https://hub.docker.com/r/gethomepage/homepage
[r5]:  https://gethomepage.dev/installation/
[r6]:  https://github.com/gethomepage/homepage/discussions/3650
[r7]:  https://github.com/gethomepage/homepage/blob/main/LICENSE
[r8]:  https://api.github.com/repos/glanceapp/glance
[r9]:  https://github.com/glanceapp/glance
[r10]: https://github.com/glanceapp/glance/blob/main/docs/configuration.md
[r11]: https://github.com/glanceapp/glance/releases
[r12]: https://github.com/glanceapp/glance
[r13]: https://github.com/glanceapp/glance
[r14]: https://github.com/glanceapp/glance/blob/main/LICENSE
[r15]: https://api.github.com/repos/Lissy93/dashy
[r16]: https://dashy.to/docs/
[r17]: https://dashy.to/docs/widgets/
[r18]: https://www.homelabstarter.com/homelab-dashboard-homarr-dashy/
[r19]: https://dashy.to/docs/authentication/
[r20]: https://dashy.to/docs/theming/
[r21]: https://github.com/Lissy93/dashy/blob/master/LICENSE
[r22]: https://api.github.com/repos/homarr-labs/homarr
[r23]: https://homarr.dev/docs/
[r24]: https://github.com/ajnart/homarr/issues/814
[r25]: https://github.com/homarr-labs/homarr/issues/3759
[r26]: https://homarr.dev/docs/
[r27]: https://homarr.dev/
[r28]: https://github.com/homarr-labs/homarr/blob/main/LICENSE
[r29]: https://api.github.com/repos/bastienwirtz/homer
[r30]: https://github.com/bastienwirtz/homer
[r31]: https://github.com/bastienwirtz/homer
[r32]: https://www.homelabstarter.com/homelab-dashboard-homarr-dashy/
[r33]: https://github.com/bastienwirtz/homer
[r34]: https://github.com/bastienwirtz/homer
[r35]: https://github.com/bastienwirtz/homer/blob/main/LICENSE.md
[r36]: https://api.github.com/repos/causefx/Organizr
[r37]: https://github.com/causefx/Organizr
[r38]: https://github.com/causefx/Organizr
[r39]: https://github.com/causefx/Organizr
[r40]: https://github.com/causefx/Organizr
[r41]: https://github.com/causefx/Organizr
[r42]: https://github.com/causefx/Organizr/blob/v2-master/LICENSE
[r43]: https://api.github.com/repos/pawelmalak/flame
[r44]: https://github.com/pawelmalak/flame
[r45]: https://github.com/pawelmalak/flame
[r46]: https://github.com/pawelmalak/flame
[r47]: https://github.com/pawelmalak/flame
[r48]: https://github.com/pawelmalak/flame
[r49]: https://github.com/pawelmalak/flame/blob/master/LICENSE
[r50]: https://api.github.com/repos/linuxserver/Heimdall
[r51]: https://github.com/linuxserver/Heimdall
[r52]: https://github.com/linuxserver/Heimdall
[r53]: https://www.homelabstarter.com/homelab-dashboard-homarr-dashy/
[r54]: https://github.com/linuxserver/Heimdall
[r55]: https://alternativeto.net/software/heimdall-application-dashboard/
[r56]: https://github.com/linuxserver/Heimdall/blob/main/LICENSE

**Scoring key.** Criteria weighted for this use-case: (1) project health — commit cadence, maintainer count, trend; (2) config-as-code — fully YAML/file-driven, reproducible from git, no DB required; (3) integrations — Pi-hole, Proxmox, Uptime Kuma, Docker socket, Jellyfin, HTTP/ping; (4) footprint — image size and idle RAM; (5) auth & reverse-proxy fit — Caddy/Traefik compatibility, forward-auth, built-in auth; (6) UX/Maint — theming, ongoing maintenance burden for single admin; (7) license — permissive FOSS, no open-core paywall. Dashy and Homarr tie at 28 and 26 respectively but on different strengths — Dashy wins UX, Homarr wins auth/UX; neither covers the full integration list.

## Research gaps

**The config-as-code child went off-scope.** It researched Kubernetes GitOps operators (Argo CD, Flux, Crossplane, Terraform/HCL) rather than dashboard YAML-config models. The homelab gitops question is simpler: Homepage stores everything in plain YAML files (`services.yaml`, `docker.yaml`, `widgets.yaml`, `settings.yaml`) that are 100% file-driven and commit-idempotent. One real friction point: brittle YAML where tab/space indentation errors silently break widget rendering — a recurring complaint in Discussions [[6]](https://github.com/gethomepage/homepage/discussions/3650). The `git pull --ff-only && docker compose up -d` deploy pipeline requires nothing else.

**Glance's integration list was not assessed.** The integration-coverage child studied only Homepage, Homarr, and Dashy. Glance's widget documentation [[10]](https://github.com/glanceapp/glance/blob/main/docs/configuration.md) shows a different design philosophy (RSS, weather, GitHub stats, iframe embeds) with no first-party Pi-hole, Proxmox, Uptime Kuma, or Jellyfin widgets as of mid-2026 — hence the 2/5 integration score above is inferred from docs rather than hands-on testing.

## Bus factor and the Glance problem

These are the same risk from opposite angles. Homepage's effective bus factor is 1: @shamoon authored 32 of the last 100 human commits; the original author (@benphelps) went inactive in September 2024 [[12]](https://github.com/gethomepage/homepage/commits/main). Hobby-scale funding (~$4,912 total on Open Collective, dominated by one corporate donor [[13]](https://opencollective.com/homepage)) provides no succession buffer. Meanwhile [Glance](https://github.com/glanceapp/glance) ⭐ 35k — created 2024 and now the #1 dashboard by GitHub stars [[14]](https://api.github.com/repos/glanceapp/glance) — is architecturally leaner (single binary, sub-30 MB), fully YAML-driven, and actively developed. If its widget ecosystem reaches parity with Homepage for Pi-hole/Proxmox/Uptime Kuma/Jellyfin, the bus-factor risk becomes a migration trigger. That parity hasn't happened yet.

**Operational must-knows.** Homepage has zero built-in authentication and will never add it [[15]](https://github.com/gethomepage/homepage/discussions/529) — all auth is delegated to the reverse proxy (`forward_auth` in Caddy, middleware labels in Traefik). `HOMEPAGE_ALLOWED_HOSTS` must list every domain used to reach the container since v1.0; omitting it produces an opaque error and is the most common post-upgrade breakage [[16]](https://gethomepage.dev/installation/). Pin versions — the v1.0 jump from v0.10.9 bundled four breaking changes including mandatory host validation and Next.js 15 (drops armv7) [[17]](https://github.com/gethomepage/homepage/releases/tag/v1.0.0). Three CVEs since 2024 (latest: GHSA-rg3r-jprv-xq38, Apr 2026) confirm the proxy API is a real attack surface if exposed unauthenticated [[18]](https://github.com/gethomepage/homepage/security/advisories).

**What would change this recommendation:** Glance shipping first-party Pi-hole, Proxmox, and Uptime Kuma widgets — at which point its lead on stars, footprint, and single-binary simplicity would make it the clear successor.
