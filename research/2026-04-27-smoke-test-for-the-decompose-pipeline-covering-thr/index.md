---
layout: expedition
title: "Decompose smoke-test: Bun, Caddy, ripgrep version snapshot"
date: 2026-04-27
topic: "Smoke-test for the decompose pipeline covering three independent micro-decisions, each decision-only with a single citation in 2026: the current stable Bun version and its 2026 release date, the current stable Caddy version and which ACME challenge type it defaults to in 2026, and the current stable ripgrep version available via Homebrew in 2026."
format: md
tags: [pipeline-smoke-test, version-snapshot, bun, caddy, ripgrep]
summary: Pipeline smoke test — three unrelated 2026 version lookups (Bun 1.3.13, Caddy 2.11.2, ripgrep 15.1.0) dispatched as independent recon, not merged.
cover: cover.svg
synthesis: true
children:
  - slug: bun-stable-version-and-2026-release-date
    title: Bun stable version and 2026 release date
    depth: ceo
    status: success
    summary: "Bun's current stable is v1.3.13, shipped April 20, 2026; six v1.3.x point releases landed in 2026 so far and no v2 has been announced."
    citations: 5
    reading_time_min: 1
  - slug: caddy-stable-version-and-default-acme-challenge
    title: Caddy stable version and default ACME challenge
    depth: ceo
    status: success
    summary: "Latest stable Caddy is v2.11.2 (Mar 2026); HTTP-01 and TLS-ALPN-01 challenges are both enabled by default, picked at random then learned."
    citations: 5
    reading_time_min: 1
  - slug: ripgrep-stable-version-on-homebrew
    title: ripgrep stable version on Homebrew
    depth: ceo
    status: success
    summary: "Homebrew currently pins ripgrep at 15.1.0 — same as the upstream stable release from 22 Oct 2025."
    citations: 3
    reading_time_min: 1
cost_usd: 2.48
duration_sec: 385
citations: 13
reading_time_min: 3
---

This run was a smoke test of the decompose path, not an investigation. The interesting signal is procedural: three unrelated micro-decisions stayed unrelated — they were dispatched as parallel recon and never folded into a unified survey, which is the behaviour the topic asked for.

**Freshness check.** All three answers come from releases shipped in the trailing six months — Bun v1.3.13 on 2026-04-20 [[1]](https://bun.com/blog/bun-v1.3.13), Caddy v2.11.2 on 2026-03-05 [[2]](https://github.com/caddyserver/caddy/releases), ripgrep 15.1.0 on 2025-10-22 [[3]](https://github.com/BurntSushi/ripgrep/releases). An April 2026 version snapshot is meaningfully current for each project, so the smoke test exercised both the dispatch and the recency-of-source paths.

**Release-governance contrast.** The three projects sit at different points on the release-cadence spectrum, which is the only cross-cutting theme worth naming. Bun has shipped six v1.3.x point releases in 2026 alone — roughly one every 2–3 weeks — and continues that cadence after Anthropic's December 2025 acquisition [[4]](https://github.com/oven-sh/bun/releases)[[5]](https://bun.com/blog). Caddy switched to an automated release pipeline starting with v2.11 and now ships smaller, more frequent patch releases [[2]](https://github.com/caddyserver/caddy/releases). ripgrep, by contrast, is a single-maintainer project where 15.1.0 has been the stable tag since October 2025 with no churn since [[3]](https://github.com/BurntSushi/ripgrep/releases); Homebrew's formula tracks the upstream tag directly [[6]](https://formulae.brew.sh/formula/ripgrep). Three different healthy-project shapes, all currently shipping the version the user is most likely to install today.

**One framing wrinkle.** The Caddy sub-question asked which ACME challenge Caddy "defaults to" — but there is no single default. Caddy enables HTTP-01 and TLS-ALPN-01 simultaneously, picks one at random per cert, then learns which one tends to succeed in the local environment and prefers it [[7]](https://caddyserver.com/docs/automatic-https). DNS-01 is opt-in because it needs provider credentials [[7]](https://caddyserver.com/docs/automatic-https). The recon agent answered the literal question without forcing a single-name answer, which is the right call but a useful pattern to note: "decision-only" framings sometimes hide a "both, with logic" reality, and the planner should not paper over that to satisfy the original framing.

**No gaps.** All three children produced non-placeholder pages with citations; nothing was skipped. The open question this run leaves behind is procedural rather than topical — when a recon angle's real answer is "it depends," should the planner upgrade it to a survey, or trust the agent to flag the nuance inline as Caddy did here?
