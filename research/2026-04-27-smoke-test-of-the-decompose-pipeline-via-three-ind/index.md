---
layout: expedition
title: "Decompose smoke-test: three 2026 stable-version lookups"
date: 2026-04-27
topic: "Smoke-test of the decompose pipeline via three independent, decision-only micro-lookups in 2026 — current stable Bun, Caddy, and ripgrep"
format: md
tags: [smoke-test, version-lookup, releases, stable, 2026]
summary: Three unrelated recon-depth lookups (Bun, Caddy, ripgrep stable in 2026) — pipeline returned three clean single-fact answers; the cross-cut is support-model and release cadence.
synthesis: true
children:
  - slug: current-stable-bun-version-and-2026-release-date
    title: Current stable Bun version and 2026 release date
    depth: ceo
    status: success
    summary: Bun v1.3.13 is the current stable release, shipped 2026-04-20; no LTS — rolling latest-is-greatest.
    citations: 4
    reading_time_min: 1
  - slug: current-stable-caddy-version-and-default-acme-chal
    title: Current stable Caddy version and default ACME challenge type in 2026
    depth: ceo
    status: success
    summary: Caddy 2.11.2 is the current stable release; HTTP-01 and TLS-ALPN-01 are both enabled by default and Caddy picks between them adaptively.
    citations: 5
    reading_time_min: 1
  - slug: current-stable-ripgrep-version-on-homebrew-in-2026
    title: Current stable ripgrep version on Homebrew in 2026
    depth: ceo
    status: success
    summary: Homebrew ships ripgrep 15.1.0 as stable — the October 2025 line-buffering hotfix on top of the 15.0.0 major.
    citations: 5
    reading_time_min: 1
cost_usd: 2.27
duration_sec: 334
citations: 14
reading_time_min: 3
---

This run was a deliberate smoke-test: three unrelated "current stable in 2026" micro-lookups, each pinned at recon depth so the planner couldn't merge or expand them. All three resolved to single-fact answers with inline citations on the first pass; the pipeline behaved.

The one substantive cross-cut is **support model**. Bun and Caddy converge: endoflife.date notes "Bun does not have a clearly defined support policy" and tracks a single active series [[1]](https://endoflife.date/bun), and the same source flags Caddy as "Only the latest release is security-supported" [[2]](https://endoflife.date/caddy). ripgrep shares the single-line model in practice — Homebrew's `stable` pin tracks whatever upstream tagged last [[3]](https://formulae.brew.sh/formula/ripgrep). For a 2026 stack pinned to "latest stable," there is no defensive fallback to a still-supported older line in any of these three.

**Cadence**, however, diverges sharply. Bun ships roughly every 1–2 weeks — six 1.3.x point releases between 2026-01-29 and 2026-04-20 [[4]](https://bun.com/blog). Caddy ships months apart; the current 2.11.2 landed 2026-03-06 [[5]](https://github.com/caddyserver/caddy/releases/tag/v2.11.2). ripgrep ships when there's a bug worth fixing — 15.1.0 on 2025-10-22 [[6]](https://github.com/BurntSushi/ripgrep/releases/tag/15.1.0) and nothing since. Operationally that means Bun upgrades need a rolling test plan, Caddy upgrades are a quarterly-ish event, and ripgrep upgrades are rare and low-risk.

One pipeline-level question worth flagging: when "default" is genuinely ambiguous — Caddy enables HTTP-01 **and** TLS-ALPN-01 and picks adaptively per certificate [[7]](https://caddyserver.com/docs/automatic-https) — the recon child correctly refused to collapse to a single value. A future smoke-test should confirm the planner doesn't punish that honesty by retrying with a forced single-answer prompt.
