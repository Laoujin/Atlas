---
title: "Bun stable: v1.3.13 (Apr 2026)"
date: 2026-04-27
depth: ceo
format: md
topic: "Bun stable version + 2026 release date"
topic_raw: "Bun stable version + 2026 release date"
issue: 19
tags: [bun, javascript, runtime, release]
summary: Latest stable is Bun v1.3.13 (Apr 19, 2026); the 1.3 line shipped Oct 10, 2025 and has been iterated weekly-to-biweekly through 2026.
citations: 5
reading_time_min: 1
cover: cover.svg
cost_usd: 0.78
duration_sec: 108
---

> **TL;DR** — The current stable release is **Bun v1.3.13**, published **April 19, 2026** [[1]](https://endoflife.date/bun) [[2]](https://github.com/oven-sh/bun/releases). The 1.3 major line (full‑stack runtime, `Bun.SQL`, built‑in dev server) shipped **October 10, 2025** [[3]](https://bun.com/blog/bun-v1.3); 1.3.x has been on a roughly weekly‑to‑biweekly patch cadence since.

## 2026 release timeline

| Version | Date | Headline |
|---|---|---|
| **1.3.13** | Apr 19, 2026 | `bun test --parallel/--isolate/--shard/--changed`; install streams tarballs to disk using **17× less memory**; source maps **8× less memory** [[2]](https://github.com/oven-sh/bun/releases) |
| 1.3.12 | Apr 9, 2026 | Render Markdown via `bun ./file.md`; `Bun.WebView` headless automation; in‑process `Bun.cron()` scheduler [[2]](https://github.com/oven-sh/bun/releases) |
| 1.3.11 | Mar 18, 2026 | Native REPL; `--compile --target=browser`; TC39 ES decorators; Windows ARM64 [[2]](https://github.com/oven-sh/bun/releases) |
| 1.3.6–1.3.10 | Jan–Feb 2026 | Patch series — Node compat, memory allocator (Libpas scavenger), 5% lower baseline RSS [[2]](https://github.com/oven-sh/bun/releases) |

## Context

- **Repo:** [oven-sh/bun](https://github.com/oven-sh/bun) ⭐ 89k (Apr 2026) [[4]](https://github.com/oven-sh/bun)
- **Support policy:** endoflife.date notes Bun "does not have a clearly defined support policy"; the v1 line is marked as receiving security support [[1]](https://endoflife.date/bun).
- **1.3 vs 1.2:** 1.3 (Oct 2025) added `Bun.SQL` (MySQL/MariaDB/PostgreSQL/SQLite under one API), a built‑in Redis client, HTML‑file execution with HMR + React Fast Refresh, and isolated workspace installs as default [[3]](https://bun.com/blog/bun-v1.3). 1.2 (Jan 2025) was the "**~90% Node.js compatibility**" milestone with built‑in S3 and Postgres clients [[5]](https://socket.dev/blog/bun-1-2-released-90-node-js-compatibility-built-in-s3-object-support).

## Upgrade

```bash
bun upgrade            # → 1.3.13
curl -fsSL https://bun.sh/install | bash
```

No 1.4 / 2.0 has been announced as of April 27, 2026 — 1.3.x remains the active line [[2]](https://github.com/oven-sh/bun/releases).
