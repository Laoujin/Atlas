---
layout: expedition
title: "Smoke test: three version lookups (Bun, Caddy, ripgrep) — April 2026"
date: 2026-04-28
topic: "Smoke-test brief verifying the decompose pipeline by running three unrelated, decision-only fact lookups in 2026 with one citation each: (1) the current stable Bun version and its 2026 release date, (2) the current stable Caddy version and which ACME challenge type it defaults to in 2026, and (3) the current stable ripgrep version available via Homebrew in 2026. These are unrelated fact lookups — don't merge them into one survey. Each sub-topic stays as a (recon) micro-decision with a single citation; do not expand any of them."
format: md
tags: [smoke-test, version-check, bun, caddy, ripgrep]
summary: "Pipeline smoke test bundling three unrelated version-of-record lookups: Bun 1.3.13, Caddy 2.11.2, ripgrep 15.1.0."
cover: cover.svg
synthesis: true
children:
  - slug: current-stable-bun-version-and-2026-release-date
    title: "Current stable Bun version and 2026 release date"
    depth: ceo
    status: success
    summary: "Bun's current stable release is v1.3.13, shipped April 20, 2026; the v1.3.x line has been the active series throughout 2026."
    citations: 5
    reading_time_min: 1
  - slug: current-stable-caddy-version-and-default-acme-challenge
    title: "Current stable Caddy version and default ACME challenge"
    depth: ceo
    status: success
    summary: "Caddy v2.11.2 (Mar 6, 2026) is the latest stable; HTTP-01 and TLS-ALPN-01 are enabled by default, with Caddy adaptively learning which to prefer per host."
    citations: 2
    reading_time_min: 1
  - slug: current-stable-ripgrep-version-on-homebrew
    title: "Current stable ripgrep version on Homebrew"
    depth: ceo
    status: success
    summary: "Homebrew ships ripgrep 15.1.0, unchanged since the upstream October 2024 release; install with `brew install ripgrep`."
    citations: 4
    reading_time_min: 1
cost_usd: 2.23
duration_sec: 340
citations: 11
reading_time_min: 3
---

This expedition is a pipeline smoke test, not a coherent survey: three unrelated micro-lookups bundled to confirm the decomposer can run independent recon children to completion. All three returned, so the pipeline is healthy. The rest of this note is the only thing the bundle is good for — observing what differs across the three answers.

**"Stable" means three different things here.** Bun ships a new patch every 2–3 weeks on the v1.3.x line (v1.3.9 → v1.3.13 spans Feb 8 → Apr 20, 2026) and explicitly has *no formal support policy* — only the latest tag is "stable" [[1]](https://endoflife.date/bun). Caddy v2.11.2 (2026-03-06) is a conventional bug-fix-plus-CVE-patch release on a long-running 2.x line [[2]](https://github.com/caddyserver/caddy/releases). ripgrep 15.1.0 has been frozen since 2024-10-22 — 18 months without an upstream cut [[3]](https://github.com/BurntSushi/ripgrep/releases). A version comparison across these three projects is meaningless without that context: a Bun install older than two months is stale, while a ripgrep install older than 18 months is current.

**Distribution lag is only visible where upstream moves.** Homebrew's ripgrep formula matches upstream exactly because upstream hasn't moved [[4]](https://formulae.brew.sh/formula/ripgrep) — this run can't tell us how fast Homebrew tracks an *active* project. If the smoke test were rerun in six months against an actively-released Homebrew formula (e.g., Bun via `brew install bun`), the lag question would have a real answer; today it's a tautology.

**Defaults vs. user choice.** The Caddy lookup is the only one that asked about behaviour rather than a number, and the answer is non-obvious: Caddy enables both HTTP-01 and TLS-ALPN-01 by default and *picks at random initially*, then adapts per host based on observed success [[5]](https://caddyserver.com/docs/automatic-https). DNS-01 is opt-in only because it needs provider credentials. None of this is a "default value" in the version-string sense; it's a runtime policy. The decomposer treated it correctly as a single recon child, which is the small-but-real signal this smoke test was built to capture.

**Open question.** The pipeline ran three children that have nothing to do with each other and produced a synthesis that mostly observes that fact. Is bundling unrelated lookups under one parent ever the right shape — or should the orchestrator detect "no shared axis" and route each child to its own top-level expedition instead?
