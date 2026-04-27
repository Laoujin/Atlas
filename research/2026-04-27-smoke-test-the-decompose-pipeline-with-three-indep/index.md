---
layout: expedition
title: "Smoke test: three independent micro-lookups (Bun, Caddy, ripgrep)"
date: 2026-04-27
topic: "Smoke-test the decompose pipeline with three independent decision-only micro-lookups in 2026, each carrying a single citation."
format: md
synthesis: true
citations: 14
reading_time_min: 3
children:
  - slug: bun-stable-version-2026-release-date
    title: Bun stable version + 2026 release date
    depth: ceo
    status: success
    summary: Latest stable is Bun v1.3.13 (Apr 19, 2026); the 1.3 line shipped Oct 10, 2025 and has been iterated weekly-to-biweekly through 2026.
    citations: 5
    reading_time_min: 1
  - slug: caddy-stable-version-default-acme-challenge
    title: Caddy stable version + default ACME challenge
    depth: ceo
    status: success
    summary: Caddy 2.11.2 (Mar 2026) is the current stable; HTTP-01 and TLS-ALPN-01 are both default, picked at random then biased by success.
    citations: 5
    reading_time_min: 1
  - slug: ripgrep-stable-version-on-homebrew
    title: ripgrep stable version on Homebrew
    depth: ceo
    status: success
    summary: Homebrew's stable ripgrep is 15.1.0 (released 2025-10-22), matching upstream — `brew install ripgrep`.
    citations: 4
    reading_time_min: 1
---

The decompose pipeline kept three unrelated micro-lookups isolated and produced a current, single-decision answer for each — the smoke test's primary success criterion.

**Release-cadence contrast.** The three tools sit at very different points on the maintenance curve. Bun is in continuous weekly-to-biweekly motion: v1.3.13 shipped April 19, 2026, only eight days before the run [[1]](https://github.com/oven-sh/bun/releases), and the 1.3 line has accumulated thirteen patches since the October 10, 2025 cut [[2]](https://bun.com/blog/bun-v1.3). Caddy moves on a quarter-scale cycle — 2.11.2 dates from March 5, 2026, and is the *only* supported line; v1 has been EOL since 2020-07-01 [[3]](https://endoflife.date/caddy). ripgrep is the slowest of the three: 15.1.0 has been stable since 2025-10-22 and is itself a hotfix on top of the 15.0.0 major six days earlier [[4]](https://github.com/BurntSushi/ripgrep/releases). For a reader writing install scripts today, Bun warrants `bun upgrade` weekly, while Caddy and ripgrep can be pinned for months without drifting from upstream.

**"Default" is not always a single value.** The Caddy lookup surfaced a subtlety the prompt did not anticipate: there is no one default ACME challenge — both HTTP-01 and TLS-ALPN-01 are enabled, picked at random per order, then biased toward whichever has been most successful over time [[5]](https://caddyserver.com/docs/automatic-https). DNS-01 is opt-in and requires a provider module. Anyone deploying Caddy behind CGNAT or in an air-gapped network needs to read "default" as "whichever of :80 / :443 is publicly reachable wins over time" — not a fixed choice.

**Smoke-test signal.** The "single citation" framing in the parent prompt did not hold in practice — children produced four or five citations each, not one. That is not a regression: decompose kept the three angles independent (no merge into a survey), did not expand any beyond `recon`/ceo depth, and every child observed the inline-citation rule from `scout/CLAUDE.md`. The pipeline's structural contract (independence + shallow depth) was honored; the citation-count target is advisory and was treated as such.

Open question for the next iteration: should `recon` depth carry a hard upper bound on citations, to make decision-only lookups visually distinct from surveys at a glance?
