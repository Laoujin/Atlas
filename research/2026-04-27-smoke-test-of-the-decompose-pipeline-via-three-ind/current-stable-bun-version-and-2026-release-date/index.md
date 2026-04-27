---
title: Bun stable version and 2026 release timeline
date: 2026-04-27
depth: ceo
format: md
topic: "Current stable Bun version and 2026 release date"
topic_raw: "Current stable Bun version and 2026 release date"
issue: 20
tags: [bun, javascript-runtime, releases]
cover: cover.svg
summary: Bun v1.3.13 is the current stable release, shipped 2026-04-20; no LTS — rolling latest-is-greatest.
citations: 4
reading_time_min: 1
cost_usd: 0.64
duration_sec: 78
---

> **TL;DR** — Current stable is **Bun v1.3.13**, released **2026-04-20** [[1]](https://bun.com/blog). Upgrade with `bun upgrade`. There is no LTS branch — Bun ships a single rolling line, with v1 still on "security support" per endoflife.date [[2]](https://endoflife.date/bun).

## 2026 release timeline

| Version | Date | Highlights |
|---|---|---|
| 1.3.13 | 2026-04-20 | `bun test --parallel`, `--isolate`, `--shard`, `--changed` [[1]](https://bun.com/blog) |
| 1.3.12 | 2026-04-09 | `Bun.WebView` headless browser automation; render markdown in terminal via `bun ./file.md` [[1]](https://bun.com/blog) |
| 1.3.11 | 2026-03-18 | 4 MB smaller on Linux; `Bun.cron` for OS-level cron jobs [[1]](https://bun.com/blog) |
| 1.3.10 | 2026-02-26 | New native REPL; `--compile --target=browser` for self-contained HTML [[1]](https://bun.com/blog) |
| 1.3.9  | 2026-02-08 | Run multiple scripts with `--parallel` or `--sequential` [[1]](https://bun.com/blog) |
| 1.3.8  | 2026-01-29 | `Bun.markdown` builtin CommonMark parser [[1]](https://bun.com/blog) |

Tags on GitHub mirror the blog dates [[3]](https://github.com/oven-sh/bun/releases) ⭐ 89k.

## Support model

endoflife.date notes "Bun does not have a clearly defined support policy" and lists a single active series — v1, originally released 2023-09-07, still receiving security support [[2]](https://endoflife.date/bun). No parallel LTS line; the latest 1.3.x is the recommended target. Bun 1.3 is the headline cycle of 2026 — full-stack capabilities, built-in database clients, zero-config frontend dev with HMR + React Fast Refresh [[4]](https://www.infoq.com/news/2026/01/bun-v3-1-release/).

## Install / upgrade

```sh
curl -fsSL https://bun.sh/install | bash   # fresh install
bun upgrade                                # in-place to 1.3.13
```
