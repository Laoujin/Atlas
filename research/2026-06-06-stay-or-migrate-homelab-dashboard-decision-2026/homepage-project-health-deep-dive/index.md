---
title: "Homepage (gethomepage) Project Health Deep Dive"
date: 2026-06-06
depth: deep
format: md
topic: "Homepage project health deep dive"
topic_raw: "Homepage project health deep dive"
issue: 193
tags: [self-hosted, dashboard, open-source, project-health, homepage]
summary: "Homepage is healthy and dominant on every adoption signal, but rests on a one-maintainer bus factor and an aggressively automated, maintainer-gated issue tracker."
citations: 42
reading_time_min: 7
cover: cover.svg
cost_usd: 4.42
duration_sec: 491
model: "Opus 4.8"
---

> **Verdict.** [gethomepage/homepage](https://github.com/gethomepage/homepage) ⭐ 31k is **healthy and actively maintained** — steady monthly releases, a near-zero backlog, and the #1 or #2 spot on every adoption metric in the self-hosted dashboard category [[1]](https://api.github.com/repos/gethomepage/homepage)[[3]](https://github.com/gethomepage/homepage/releases)[[24]](https://awesome-selfhosted.net/tags/personal-dashboards.html). The two real risks are structural, not cosmetic: a **bus factor of ~1** (one maintainer, @shamoon, authored nearly all recent work and every v1.0 breaking change) [[9]](https://github.com/gethomepage/homepage/commits/main)[[15]](https://api.github.com/search/commits?q=repo:gethomepage/homepage+author:shamoon), and a **maintainer-gated support model** where the empty issue tracker is engineered by auto-closing bots, not by the absence of problems [[16]](https://img.shields.io/github/issues-raw/gethomepage/homepage.json)[[19]](https://github.com/gethomepage/homepage/blob/main/.github/workflows/issue-triage.yml). Use it with confidence; pin your version and read release notes before upgrading.

## Health scorecard

| Dimension              | Signal                                                        | Rating |
|------------------------|--------------------------------------------------------------|--------|
| Release cadence        | ~1 minor/month, latest v1.13.1 (2026-05-11) [[4]](https://github.com/gethomepage/homepage/releases/tag/v1.13.1) | ✓ Strong |
| Commit activity        | 7–18 commits/week, last push day-of-research [[10]](https://api.github.com/repos/gethomepage/homepage/stats/participation)[[1]](https://api.github.com/repos/gethomepage/homepage) | ✓ Strong |
| Adoption               | ⭐ 31k, 1M+ Docker pulls, #2 dashboard by stars [[23]](https://hub.docker.com/r/gethomepage/homepage)[[24]](https://awesome-selfhosted.net/tags/personal-dashboards.html) | ✓ Strong |
| Backlog hygiene        | 0 open issues, 1 open PR — but automated [[16]](https://img.shields.io/github/issues-raw/gethomepage/homepage.json)[[17]](https://github.com/gethomepage/homepage/pulls) | ⚠ Engineered |
| Bus factor             | Effectively 1 active human maintainer [[9]](https://github.com/gethomepage/homepage/commits/main) | ⚠ Risk |
| Funding                | ~$4.9k total raised on Open Collective [[12]](https://opencollective.com/homepage) | ⚠ Hobby-scale |
| Security track record  | 3 advisories; unauthenticated proxy by design [[33]](https://github.com/gethomepage/homepage/security/advisories)[[32]](https://www.anvilsecure.com/blog/vulnerabilities-in-homepage-dashboard.html) | ⚠ Watch |
| Governance / roadmap   | No public roadmap, no documented succession [[6]](https://gethomepage.dev/) | ✗ Absent |

## Releases: brisk, predictable, widget-driven

The project has shipped ~124 release pages since its August 2022 origin and hit its **v1.0.0 milestone on 2025-03-14** [[3]](https://github.com/gethomepage/homepage/releases)[[2]](https://github.com/gethomepage/homepage/releases/tag/v1.0.0). The major bump was semver bookkeeping for breaking changes, not a rewrite (see Risks). Post-1.0 cadence is steady at roughly one minor release per month: v1.2 (Apr 2025) → v1.5 (Sep) → v1.8 (Dec) → v1.9 (Jan 2026) → v1.13 (May 2026) [[3]](https://github.com/gethomepage/homepage/releases). The **latest is v1.13.1 (2026-05-11)**, a patch (qBittorrent v5.2 API, PBS/ntfy fixes, translations) [[4]](https://github.com/gethomepage/homepage/releases/tag/v1.13.1); the preceding v1.13.0 added an ntfy widget, Technitium DNS and Tailscale fields, and keep-alive HTTP caching [[5]](https://github.com/gethomepage/homepage/releases/tag/v1.13.0).

The work is overwhelmingly **incremental service-widget additions** — the value proposition is breadth (100+ integrations) rather than architectural evolution [[6]](https://gethomepage.dev/). There is **no published roadmap or GitHub milestones**: the docs site lists no version and no future-plans page [[6]](https://gethomepage.dev/), which is itself a governance finding.

## Maintainership: steady hands, but only one pair

Homepage started in August 2022 as a personal repo by [benphelps](https://github.com/benphelps), who moved it under the dedicated **gethomepage** org (created 2023-01-17, in v0.7.2) to spread the load and improve sustainability [[13]](https://api.github.com/orgs/gethomepage)[[35]](https://grokipedia.com/page/Homepage_dashboard). That goal is only half-met. The headline contributor count (~421) is heavily inflated by the Weblate translation bot (~3,845 contributions) and Dependabot [[7]](https://api.github.com/repos/gethomepage/homepage/contributors)[[8]](https://github.com/gethomepage/homepage/graphs/contributors). Genuine human depth is thin:

- **@shamoon** is the de facto lead: ~1,308 commits, still committing 2026-06-02 [[15]](https://api.github.com/search/commits?q=repo:gethomepage/homepage+author:shamoon).
- **@benphelps** (original author): 463 commits, but stopped at 2024-09-11 [[14]](https://api.github.com/search/commits?q=repo:gethomepage/homepage+author:benphelps).
- Across the **last 100 commits**, shamoon authored 32, Dependabot 56, github-actions 2 — every other human contributor appears exactly once [[9]](https://github.com/gethomepage/homepage/commits/main).

So the **bus factor is effectively 1**. Activity itself is healthy (7–18 commits/week) [[10]](https://api.github.com/repos/gethomepage/homepage/stats/participation), but it depends on a single person. Funding reinforces the hobby-scale picture: GitHub Sponsors, Patreon, and an Open Collective that has raised ~**$4,912 total** (~$4,783 balance) from ~30 contributors, dominated by one corporate donor, BuySellAds (~$3,869 since May 2024) [[11]](https://github.com/gethomepage/homepage/blob/main/.github/FUNDING.yml)[[12]](https://opencollective.com/homepage). Nowhere near salary scale → no documented succession plan if shamoon steps back.

## Backlog: a clean tracker, by automation not absence

On paper the backlog is pristine: **0 open / 911 closed issues** and **1 open / 1,758 closed PRs** [[16]](https://img.shields.io/github/issues-raw/gethomepage/homepage.json)[[17]](https://github.com/gethomepage/homepage/pulls) (the GitHub API's `open_issues_count: 1` simply counts that one open PR, since GitHub tallies PRs as issues) [[1]](https://api.github.com/repos/gethomepage/homepage). This is **engineered, not organic**:

- **Discussion-first gate** → the issue tracker is maintainer-only. Any issue tagged `needs-discussion` is auto-commented, closed as `not_planned`, and locked: *"only open an issue when a maintainer asks you to do so"* [[19]](https://github.com/gethomepage/homepage/blob/main/.github/workflows/issue-triage.yml).
- **Aggressive stale bot** → a daily workflow marks issues/PRs stale after just **7 days** and closes them after **14**, with **no exempt labels**, then locks threads inactive 30+ days [[18]](https://github.com/gethomepage/homepage/blob/main/.github/workflows/repo-maintenance.yml).
- **Discussions as the real funnel** → support and feature requests live in [Discussions](https://github.com/gethomepage/homepage/discussions) [[21]](https://github.com/gethomepage/homepage/discussions); the same maintenance workflow auto-closes feature requests below upvote thresholds (under 20 upvotes after 180 days, under 40 after a year) [[18]](https://github.com/gethomepage/homepage/blob/main/.github/workflows/repo-maintenance.yml).
- **Light PR gating** → a single "anti-slop" AI quality action (max 4 failures), no required linked-issue or semantic-title checks [[20]](https://github.com/gethomepage/homepage/blob/main/.github/workflows/pr-quality.yml).

The upside: maintainer time is protected and the repo never drowns in stale tickets — plausibly *why* a single maintainer can keep pace. The downside: "0 open issues" overstates support responsiveness; real friction is dispersed into Discussions where it's harder to track and easy to auto-expire ⚠.

## Adoption: front-rank, by every signal

Homepage is one of the most widely deployed self-hosted dashboards in 2026: ⭐ 31k, ~2k forks, **1M+ Docker pulls** (primary distribution is `ghcr.io/gethomepage/homepage:latest`) [[22]](https://github.com/gethomepage/homepage)[[23]](https://hub.docker.com/r/gethomepage/homepage)[[27]](https://gethomepage.dev/installation/docker/). The awesome-selfhosted personal-dashboards listing ranks it **#2 by stars (30,514 as of 2026-06-04; the ~31k figures here round the same count)** — behind only Glance, ahead of Dashy, and ~3× Heimdall [[24]](https://awesome-selfhosted.net/tags/personal-dashboards.html). Tech media treats it as a default: The New Stack calls it a *"one-stop shop for monitoring … all of the services you depend on"* [[26]](https://thenewstack.io/homepage-is-your-one-stop-shop-for-monitoring-and-viewing-all-of-the-services-you-depend-on/), and 2026 guides frame it as a *"genuine control center"* rather than a launcher [[28]](https://digitalbiztalk.com/article/building-the-ultimate-self-hosted-homepage-dashboard-in-2026). The selfh.st survey — the category's adoption barometer, 4,081 responses in 2025 — confirms a large, growing self-hosting audience for tools like it [[25]](https://selfh.st/survey/2025-results/).

## Risks: breaking changes and an unauthenticated proxy

**Breaking changes.** v1.0.0 (from v0.10.9) bundled four breaking changes — all authored by @shamoon: mandatory `HOMEPAGE_ALLOWED_HOSTS` host validation, Next.js 15 (dropping armv7), Tailwind v4 (custom-CSS rewrites), and Kubernetes Gateway API config [[2]](https://github.com/gethomepage/homepage/releases/tag/v1.0.0)[[29]](https://github.com/gethomepage/homepage/discussions/4976). The host-validation requirement **broke many reverse-proxy installs**, and users complained it shipped with thin docs and an opaque error — *"Not everyone is a dev"* [[30]](https://github.com/gethomepage/homepage/discussions/4928). An escape hatch (`HOMEPAGE_ALLOWED_HOSTS=*`) only arrived in v1.0.3 and is explicitly discouraged [[31]](https://gethomepage.dev/installation/). → Pin versions; read notes before upgrading.

**Security.** Homepage's proxy API is **unauthenticated by design** — anyone who reaches the dashboard can hit it unless it's behind an authenticated reverse proxy. Anvil Secure's audit found SSRF, path traversal (arbitrary plugin installs via PlayControl), CSRF, and API-key leakage; the maintainers fixed the worst but left broad cross-integration information disclosure unpatched, classed as *"a feature rather than a security concern"* [[32]](https://www.anvilsecure.com/blog/vulnerabilities-in-homepage-dashboard.html). Three formal advisories exist: **GHSA-24m5-7vjx-9x37** (Critical, Jun 2024), **GHSA-c4qv-fm8g-wm67** (Moderate, Aug 2025), **GHSA-rg3r-jprv-xq38** (Moderate, Apr 2026) [[33]](https://github.com/gethomepage/homepage/security/advisories). The advisory cadence shows issues *are* being found and fixed — but the design means homepage must not be exposed unauthenticated to the internet.

**Usability.** Recurring complaint: brittle YAML where indentation errors (tabs vs spaces) silently break widgets [[34]](https://github.com/gethomepage/homepage/discussions/3650).

## Competitive landscape: healthy relative to the field

Against peers, homepage's health is upper-tier — actively maintained, top-2 by stars. The field's outliers: Glance leads on stars, Dashy on commit volume, Heimdall is the clear stalled case.

| Project                  | ⭐ Stars  | Last commit | Status                                  |
|--------------------------|----------|-------------|-----------------------------------------|
| [Glance][g]              | ⭐ 35k    | 2026-05-30  | ✓ Fast-rising (created 2024)            |
| [homepage][hp]           | ⭐ 31k    | 2026-06-06  | ✓ Actively maintained                   |
| [Dashy][d]               | ⭐ 25k    | 2026-06-06  | ✓ Most commit-active (525/90d)          |
| [Heimdall][he]           | ⭐ 9.2k   | 2025-11-11  | ✗ Stalled (~7 mo, replacements advised) |
| [Flame][f]               | ⭐ 6.4k   | 2026-04-25  | ⚠ Low cadence, not dead                 |
| [Organizr][o]            | ⭐ 5.8k   | 2026-05-19  | ⚠ Occasional v2-develop updates         |
| [Homarr][hm]             | ⭐ 4.0k   | 2026-06-06  | ✓ Active rewrite (homarr-labs org)      |

[g]: https://github.com/glanceapp/glance
[hp]: https://github.com/gethomepage/homepage
[d]: https://github.com/Lissy93/dashy
[he]: https://github.com/linuxserver/Heimdall
[f]: https://github.com/pawelmalak/flame
[o]: https://github.com/causefx/Organizr
[hm]: https://github.com/homarr-labs/homarr

Sources: Glance [[39]](https://api.github.com/repos/glanceapp/glance), homepage [[1]](https://api.github.com/repos/gethomepage/homepage), Dashy [[36]](https://api.github.com/repos/Lissy93/dashy), Heimdall [[37]](https://api.github.com/repos/linuxserver/Heimdall) + replacement advice [[42]](https://alternativeto.net/software/heimdall-application-dashboard/), Flame [[40]](https://api.github.com/repos/pawelmalak/flame), Organizr [[41]](https://api.github.com/repos/causefx/Organizr), Homarr [[38]](https://api.github.com/repos/homarr-labs/homarr).

## Bottom line

Homepage scores green on the metrics most users check first — releases, activity, stars, backlog — and amber on the ones that matter for the long run: a single-maintainer bus factor [[9]](https://github.com/gethomepage/homepage/commits/main), hobby-scale funding [[12]](https://opencollective.com/homepage), and a support model that keeps the tracker clean by closing things fast [[18]](https://github.com/gethomepage/homepage/blob/main/.github/workflows/repo-maintenance.yml). None of that is disqualifying — it's the normal shape of a successful solo-led OSS project. Adopt it, but **pin versions, read release notes, keep it behind authenticated access, and have a fallback** (Glance or Dashy are the healthiest alternatives) in case the bus factor ever cashes out [[39]](https://api.github.com/repos/glanceapp/glance)[[36]](https://api.github.com/repos/Lissy93/dashy).
