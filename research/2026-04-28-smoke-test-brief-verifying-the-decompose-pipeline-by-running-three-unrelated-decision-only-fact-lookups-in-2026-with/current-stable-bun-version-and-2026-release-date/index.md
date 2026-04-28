---
title: "Current stable Bun: v1.3.13 (April 20, 2026)"
date: 2026-04-28
depth: ceo
format: md
topic: "Current stable Bun version and 2026 release date"
topic_raw: "Current stable Bun version and 2026 release date"
issue: 39
tags: [bun, javascript-runtime, release, version]
summary: "Bun's current stable release is v1.3.13, shipped April 20, 2026; the v1.3.x line has been the active series throughout 2026."
citations: 5
reading_time_min: 1
cover: cover.svg
cost_usd: 0.78
duration_sec: 102
---

> **TL;DR** — The current stable Bun is **v1.3.13**, released **April 20, 2026** [[1]](https://bun.com/blog/bun-v1.3.13) [[2]](https://github.com/oven-sh/bun/releases). The v1.3.x series has been the active stable line all of 2026 [[3]](https://endoflife.date/bun).

## 2026 release cadence

Bun ([oven-sh/bun](https://github.com/oven-sh/bun) ⭐ 89k) has shipped one minor patch roughly every 2–3 weeks in 2026, all on the v1.3.x line [[2]](https://github.com/oven-sh/bun/releases).

| Version | Release date | Notes |
|---|---|---|
| v1.3.13 | Apr 20, 2026 | 82 issues fixed; `bun test --parallel/--isolate/--shard/--changed`; install streams tarballs (17× less memory); 5.5× faster gzip via zlib-ng; range requests in `Bun.serve()` [[1]](https://bun.com/blog/bun-v1.3.13) |
| v1.3.12 | Apr 10, 2026 | Patch release [[2]](https://github.com/oven-sh/bun/releases) |
| v1.3.11 | Mar 18, 2026 | Patch release [[2]](https://github.com/oven-sh/bun/releases) |
| v1.3.10 | Feb 26, 2026 | Patch release [[2]](https://github.com/oven-sh/bun/releases) |
| v1.3.9  | Feb 8, 2026  | Patch release [[2]](https://github.com/oven-sh/bun/releases) |

## Caveats

- Bun has **no formally defined support policy**; only the latest version is treated as stable [[3]](https://endoflife.date/bun).
- Install / upgrade: `curl -fsSL https://bun.sh/install | bash` or `bun upgrade` [[4]](https://bun.com/docs/guides/util/upgrade).
- Bun is developed by Oven and the runtime entered 1.0 in September 2023; the 1.x series has been backwards-compatible since [[5]](https://en.wikipedia.org/wiki/Bun_(software)).
