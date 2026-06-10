---
layout: expedition
title: "Git-native uptime monitoring for a Docker Compose + Traefik homelab (2026)"
date: 2026-06-07
topic: "Choose the git-native uptime monitor for a Docker Compose + Traefik homelab (2026)."
format: md
tags: [homelab, monitoring, gitops, gatus, uptime-kuma]
summary: "Gatus is the only candidate where the full monitor set lives in a committed YAML file — no GUI clicks, no SQLite state escaping git, 40 MB RAM. Migration from Kuma is manual but tractable; the main traps are Kuma v2's removed JSON export and Traefik's CVE-2026-44774."
cover: cover.svg
synthesis: true
children:
  - slug: project-health-bus-factor
    title: "Project health & bus-factor"
    depth: standard
    status: success
    summary: "How to measure bus factor from git history, which frameworks track project health, and practical strategies to raise a dangerously low number — with lessons from the XZ Utils supply chain attack."
    citations: 20
    reading_time_min: 5
  - slug: config-as-code-completeness
    title: "Config-as-code completeness"
    depth: standard
    status: success
    summary: "Most teams reach modular IaC for compute but leave secrets, policy, database schema, runtime config, and SaaS posture unmanaged — covering all 8 domains with pipeline enforcement is what separates Level 3 from Level 5."
    citations: 22
    reading_time_min: 8
  - slug: feature-coverage-matrix
    title: "Feature coverage matrix"
    depth: standard
    status: success
    summary: "A feature coverage matrix maps requirements or user stories to test cases — revealing which features have no automated safety net and where defect risk concentrates."
    citations: 20
    reading_time_min: 7
  - slug: operational-weight-backup-story
    title: "Operational weight & backup story"
    depth: standard
    status: success
    summary: "Operational weight is the % of engineering time lost to manual reactive work — target below 50%, reality is 30% and rising. The backup story most teams tell is fiction: 71% do no failover testing. The floor is 3-2-1-1-0."
    citations: 22
    reading_time_min: 9
  - slug: migration-from-kuma-winner-sample-config
    title: "Migration from Kuma + winner sample config"
    depth: standard
    status: success
    summary: "Gatus wins for gitops homelabs: pure YAML config, 40 MB RAM, no database. No automated migrator exists — dump Kuma's SQLite or use the Python API, then remap to Gatus endpoint format. Full sample config included for HTTP, ICMP, TCP, TLS, DNS, Discord/ntfy alerts, and Homepage widget."
    citations: 16
    reading_time_min: 8
  - slug: status-page-exposure-via-traefik
    title: "Status page exposure via Traefik"
    depth: ceo
    status: success
    summary: "Never expose Traefik's API/dashboard publicly without authentication. Default endpoints leak full configuration; use middleware, network isolation, and recent patches."
    citations: 9
    reading_time_min: 3
cost_usd: 6.35
duration_sec: 3462
citations: 109
reading_time_min: 40
issue: 198
model: "Sonnet 4.6"
---

**Verdict: [Gatus](https://github.com/TwiN/gatus) ⭐ 11.2k.** The hard requirement — monitor config lives in git, reproducible from a clean VM — eliminates four of the five candidates before any other axis matters. Uptime Kuma stores everything in SQLite via a GUI and removed its JSON export in v2 (October 2025) [[1]](https://linuxiac.com/uptime-kuma-2-0-arrives-with-mariadb-support-modern-ui-refresh/). Healthchecks (self-hosted), Statping-ng, and the Prometheus Blackbox + Alertmanager + Grafana stack all either require GUI-driven state or carry an impractical container count for a single-node homelab. Only Gatus ships with `config.yaml` as the sole source of truth, auto-reloads on change, and needs one container [[2]](https://github.com/TwiN/gatus).

**The 87k vs 11k star gap is not a health signal here.** Applying [CHAOSS Contributor Absence Factor](https://chaoss.community/kb/metrics-model-starter-project-health/) and commit-cadence criteria to both projects, Gatus is actively maintained with regular releases [[2]](https://github.com/TwiN/gatus). Kuma's star advantage reflects years of viral GUI-driven adoption among users who want the opposite of what this brief requires: zero config files. A project with 87k stars that stores its state in a UI-managed SQLite database scores worse on config-as-code completeness than a project with 11k stars that is purely YAML-driven — star count measures community size, not gitops suitability [[3]](https://chaoss.community/kb/metrics-model-oss-project-viability-community/).

**Config-as-code completeness is the decisive axis.** The config-as-code research identifies two common failure modes: state managed outside git, and secrets committed inside git. Kuma fails the first test by design. Gatus passes both: monitors are declared in `config.yaml` (in git), credentials are injected as environment variables at runtime (never committed) [[2]](https://github.com/TwiN/gatus). The result is a monitoring domain at IaC Level 4: every change is a pull request, every state is version-controlled, rollback is `git revert`.

**What you lose is concrete and manageable.** Gatus has no Docker container liveness monitor — replace with an HTTP `HEALTHCHECK` endpoint on each service Dockerfile, or point at Traefik's `/ping`. Alert providers drop from Kuma's 90+ to Gatus's 20+, but Discord, ntfy, Telegram, and email cover every realistic homelab notification path [[4]](https://botmonster.com/posts/build-status-page-self-hosted-services-gatus/). Uptime history does not transfer; enable SQLite storage (`storage: type: sqlite`) so Gatus accumulates its own history across restarts and does not reset on container rebuild [[5]](https://blog.mei-home.net/posts/k8s-migration-21-gatus/).

**Operational weight is low.** Single container, ~40 MB RAM at 50 endpoints vs Kuma's ~100 MB [[6]](https://www.homelabstarter.com/homelab-uptime-monitoring/), no separate database process, no UI-driven toil. Backup story for Gatus: the `config.yaml` is already in git; the only ephemeral asset is the SQLite uptime history file — back that up with Restic or Kopia alongside the rest of your homelab volumes. The [3-2-1-1-0 rule](operational-weight-backup-story/#3-2-1-1-0-the-modern-floor) requires one immutable copy — apply S3 Object Lock or a MinIO WORM policy to the bucket receiving your Restic snapshots.

**Traefik security is an active concern, not a hypothetical.** CVE-2026-44774 (June 5, 2026) allows a low-privileged tenant in shared Gateway API deployments to overwrite live Traefik configuration via the REST provider [[7]](https://github.com/traefik/traefik/security/advisories/GHSA-96qj-4jj5-wcjc). For a Docker Compose homelab the blast radius is smaller, but the principle stands: expose Gatus's status page via a Traefik router with ForwardAuth or BasicAuth middleware; never expose Traefik's own API port (`8080` by default) outside the Docker internal network; patch to v2.11.46+, v3.6.17+, or v3.7.1+.

The sharpest open question: Statping-ng's maintenance status was flagged as a prerequisite check before recommending it, but the sub-topics did not directly audit its commit log or issue responsiveness — if Statping-ng is in any existing stack, apply the [bus-factor tooling](project-health-bus-factor/#tools) (`npx -y git-truck`, `scorecard --repo`) before trusting it with production alert paths.
