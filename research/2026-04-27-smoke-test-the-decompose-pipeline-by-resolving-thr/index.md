---
layout: expedition
title: Decompose-pipeline smoke test (2026-04-27)
date: 2026-04-27
topic: "Smoke-test the decompose pipeline by resolving three independent, decision-only micro-lookups in 2026, each backed by a single citation, and surfaced as three separate recon sub-topics that must not be expanded or merged into a single survey: (1) the current stable Bun version and its 2026 release date; (2) the current stable Caddy version and which ACME challenge type it defaults to in 2026; (3) the current stable ripgrep version available via Homebrew in 2026."
format: md
synthesis: true
citations: 13
reading_time_min: 3
children:
  - slug: current-stable-bun-version-2026
    title: Current stable Bun version (2026)
    depth: ceo
    status: success
    summary: "Bun v1.3.13 (released 2026-04-20) is the current stable; no LTS line exists, so always upgrade to latest."
    citations: 6
    reading_time_min: 1
  - slug: current-stable-caddy-version-and-default-acme-chal
    title: Current stable Caddy version and default ACME challenge (2026)
    depth: ceo
    status: success
    summary: "Caddy v2.11.2 (Mar 2026) is the current stable release; HTTP-01 and TLS-ALPN-01 are enabled by default, picked at random and learned over time."
    citations: 3
    reading_time_min: 1
  - slug: current-stable-ripgrep-via-homebrew-2026
    title: Current stable ripgrep via Homebrew (2026)
    depth: ceo
    status: success
    summary: "Homebrew ships ripgrep 15.1.0 (released Oct 2025); install with `brew install ripgrep`."
    citations: 4
    reading_time_min: 1
---

The pipeline produced three independent recon answers without merging them into a survey, satisfying the smoke-test's "must not be expanded" constraint. Each child carries its own TL;DR and citations, and none cross-references another — confirming the decomposer treats decision-only micro-lookups as terminal.

## Cross-cutting observations

**"Latest = supported" is the norm; LTS is fiction.** Bun has no LTS track and the documented upgrade path is `bun upgrade` to head [[1]](https://endoflife.date/bun); Caddy's endoflife.date entry confirms only the latest minor receives fixes [[2]](https://endoflife.date/caddy); ripgrep ships a single line with each tag superseding the previous [[3]](https://github.com/BurntSushi/ripgrep/releases). Any 2026 runbook still tracking "the LTS branch" of these three is tracking nothing — pin a specific version and own your upgrade cadence.

**Release cadence varies by 1–2 orders of magnitude.** Bun cut 1.3.11 → 1.3.12 → 1.3.13 across five weeks (18 Mar → 9 Apr → 20 Apr) [[4]](https://bun.com/blog); Caddy point-released monthly (2.11.1 on 23 Feb → 2.11.2 on 6 Mar) [[5]](https://github.com/caddyserver/caddy/releases); ripgrep's 15.0.0 → 15.1.0 spanned roughly six months to Oct 2025 [[3]](https://github.com/BurntSushi/ripgrep/releases). A "pin exact patch" policy means very different things across the three — weekly CI bumps for Bun, monthly for Caddy, near-zero churn for ripgrep.

**Pinning advice diverges accordingly.** Bun's release notes routinely fix 80–150 issues per drop, so pin exact (`1.3.13`) [[4]](https://bun.com/blog); Caddy 2.11.2 carries two CVE fixes on top of 2.11.1's six, making latest-patch mandatory [[5]](https://github.com/caddyserver/caddy/releases); ripgrep 15.1.0 has zero breaking changes vs 15.0.0 and `brew install ripgrep` is the safe default [[6]](https://formulae.brew.sh/formula/ripgrep). One contradiction worth flagging: Caddy's default ACME setup needs inbound :80 *and* :443 reachable, and only DNS-01 supports wildcards [[7]](https://caddyserver.com/docs/automatic-https) — so "Caddy just works" assumes a topology many 2026 deployments (proxied, port-restricted, wildcard-cert) don't have.

## Smoke-test observations

The spec asked for "a single citation" per child; children produced 3 (Caddy), 4 (ripgrep), and 6 (Bun). Soft divergence — the children are correctly recon-depth (single TL;DR, ≤1 min reading time) but err toward source diversity over source minimalism. If the test goal was "stays at recon depth," it passed; if it was "minimum citations," the prompt needs to bound them explicitly. All three completed; none failed or were skipped, and child slugs were sensibly truncated (`current-stable-caddy-version-and-default-acme-chal` keeps the operative noun).

## Open question

For future minimum-citation smoke-tests, should the decomposer enforce a citation cap on recon children, or is "one URL per claim" a writer-side rule that the pipeline shouldn't police?
