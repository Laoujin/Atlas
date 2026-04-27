---
title: Current stable Bun version (2026-04-27)
date: 2026-04-27
depth: ceo
format: md
topic: "Current stable Bun version (2026)"
topic_raw: "Current stable Bun version (2026)"
issue: 18
tags: [bun, javascript-runtime, version, release]
cover: cover.svg
summary: Bun v1.3.13 (released 2026-04-20) is the current stable; no LTS line exists, so always upgrade to latest.
citations: 6
reading_time_min: 1
cost_usd: 0.71
duration_sec: 66
---

> **TL;DR** — The current stable Bun is **v1.3.13**, released **2026-04-20** [[1]](https://bun.com/blog) [[2]](https://github.com/oven-sh/bun/releases). Bun has no LTS track — `bun upgrade` to latest is the supported path [[3]](https://endoflife.date/bun) [[4]](https://bun.com/docs/guides/util/upgrade).

## Recent stable releases

| Version | Released | Highlights |
|---|---|---|
| **1.3.13** | 2026-04-20 | `bun test --parallel/--isolate/--shard/--changed`; install streams tarballs (17× less memory); 5.5× faster gzip via zlib-ng; range requests in `Bun.serve()` [[1]](https://bun.com/blog) |
| 1.3.12 | 2026-04-09 | Render Markdown in terminal (`bun ./file.md`); `Bun.WebView` headless automation; in-process `Bun.cron()`; 2.3× faster URLPattern [[1]](https://bun.com/blog) |
| 1.3.11 | 2026-03-18 | 4 MB smaller Linux binary; OS-level `Bun.cron`; Windows ARM64 support [[1]](https://bun.com/blog) |

## What you need to know

- **Repo:** [oven-sh/bun](https://github.com/oven-sh/bun) ⭐ 89k (Apr 2026) [[2]](https://github.com/oven-sh/bun/releases) — single stable line, no parallel maintenance branches.
- **Support policy:** endoflife.date notes Bun "does not have a clearly defined support policy"; only v1.x has security support, no designated LTS [[3]](https://endoflife.date/bun).
- **Upgrade:** `bun upgrade` (or re-run `curl -fsSL https://bun.sh/install | bash`); pin via `bun upgrade --canary` only if you want bleeding-edge [[4]](https://bun.com/docs/guides/util/upgrade).
- **Cadence:** roughly weekly minor bumps in the 1.3.x line through Q1–Q2 2026; release notes consistently fix 80–150 issues per drop [[1]](https://bun.com/blog).
- **Production caveat:** earlier 1.1.x had documented memory-leak reports addressed in 1.1.13 [[5]](https://www.theregister.com/2026/04/21/anthropics_bun_1113_released_with_memory_fixes/); 2026 production guides treat 1.3.x as stable but recommend pinning exact patch versions in CI [[6]](https://byteiota.com/bun-runtime-production-guide-2026-speed-vs-stability/).

## Recommendation

Pin `1.3.13` for reproducible builds; allow `^1.3` if you want patches automatically. Don't wait for an LTS — there isn't one.
