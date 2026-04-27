---
title: "Bun stable: v1.3.13 (April 20, 2026)"
date: 2026-04-27
depth: ceo
format: md
topic: "Bun stable version and 2026 release date"
topic_raw: "Bun stable version and 2026 release date"
issue: 21
tags: [bun, javascript, runtime, releases]
summary: Bun's current stable is v1.3.13, shipped April 20, 2026; six v1.3.x point releases landed in 2026 so far and no v2 has been announced.
citations: 5
reading_time_min: 1
cover: cover.svg
cost_usd: 0.79
duration_sec: 110
---

> **TL;DR** — Latest stable is **Bun v1.3.13**, released **April 20, 2026** [[1]](https://bun.com/blog/bun-v1.3.13)[[2]](https://endoflife.date/bun). Still on the 1.3 line; no v2 announced. Cadence in 2026 has been ~one point release every 2–3 weeks.

## 2026 release timeline

| Version | Released | Headline |
|---|---|---|
| 1.3.13 | Apr 20, 2026 | `bun test --isolate / --parallel / --shard / --changed`; source maps use up to 8× less memory; gzip up to 5.5× faster via zlib-ng; `bun install` streams tarballs (17× less memory); SHA3 in WebCrypto [[1]](https://bun.com/blog/bun-v1.3.13) |
| 1.3.12 | Apr 9, 2026 | point release [[3]](https://github.com/oven-sh/bun/releases) |
| 1.3.11 | Mar 18, 2026 | point release [[3]](https://github.com/oven-sh/bun/releases) |
| 1.3.10 | Feb 26, 2026 | native REPL, `--compile --target=browser`, TC39 ES decorators, Windows ARM64 [[3]](https://github.com/oven-sh/bun/releases) |
| 1.3.9 | Feb 8, 2026 | `--parallel` / `--sequential` script runner, ESM bytecode compilation [[3]](https://github.com/oven-sh/bun/releases) |
| 1.3.8 | Jan 29, 2026 | `Bun.markdown` builtin parser, `bun build --metafile-md` [[3]](https://github.com/oven-sh/bun/releases) |

## Context

- Repo: [oven-sh/bun](https://github.com/oven-sh/bun) ⭐ 89k (Apr 2026) [[4]](https://github.com/oven-sh/bun).
- Bun was acquired by Anthropic on December 2, 2025; the project remains open source under the same release line [[5]](https://bun.com/blog).
- `endoflife.date` tracks only the v1 major and lists 1.3.13 (Apr 19, 2026) as the latest — one day off from the GitHub tag (Apr 20) [[2]](https://endoflife.date/bun)[[3]](https://github.com/oven-sh/bun/releases).
- No v2.0 roadmap has been published; all 2026 work has shipped on the 1.3 line.

## Upgrade

```sh
bun upgrade
```
