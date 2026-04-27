---
title: ripgrep on Homebrew — current stable in April 2026
date: 2026-04-27
depth: ceo
format: md
topic: "Current stable ripgrep version on Homebrew in 2026"
topic_raw: "Current stable ripgrep version on Homebrew in 2026"
issue: 20
tags: [ripgrep, homebrew, cli, version]
cover: cover.svg
summary: Homebrew ships ripgrep 15.1.0 as stable — the October 2025 line-buffering hotfix on top of the 15.0.0 major.
citations: 5
reading_time_min: 1
cost_usd: 0.54
duration_sec: 81
---

> **TL;DR** — `brew install ripgrep` gets you **15.1.0** [[1]](https://formulae.brew.sh/formula/ripgrep). That's the current `stable` pin in `homebrew-core` and matches upstream's latest tag from 22 Oct 2025 [[2]](https://github.com/BurntSushi/ripgrep/releases/tag/15.1.0). No newer release has landed since.

## What you actually get

| Field | Value |
|---|---|
| Homebrew stable | `15.1.0` [[1]](https://formulae.brew.sh/formula/ripgrep) |
| Upstream latest tag | `15.1.0`, released 2025-10-22 [[2]](https://github.com/BurntSushi/ripgrep/releases/tag/15.1.0) |
| Previous major | `15.0.0`, released 2025-10-16 [[3]](https://github.com/BurntSushi/ripgrep/releases/tag/15.0.0) |
| Runtime dep | PCRE2 10.47 [[1]](https://formulae.brew.sh/formula/ripgrep) |
| Bottles | macOS arm64 + x86_64, Linux arm64 + x86_64 [[1]](https://formulae.brew.sh/formula/ripgrep) |
| Upstream repo | [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) ⭐ 63k (Apr 2026) |

## What changed since the last 14.x

`15.0.0` was the first major in ~22 months — gitignore-matching fixes, perf work, and Jujutsu repo support [[3]](https://github.com/BurntSushi/ripgrep/releases/tag/15.0.0). `15.1.0` is a one-bug hotfix: a `--line-buffered` regression that broke `tail -f`-style pipelines, plus a hyperlink alias for Cursor [[2]](https://github.com/BurntSushi/ripgrep/releases/tag/15.1.0)[[4]](https://github.com/BurntSushi/ripgrep/blob/master/CHANGELOG.md). If you're on 15.0.0, upgrading is cheap and worth it.

## Verifying locally

```sh
brew info ripgrep   # → stable 15.1.0
rg --version        # → ripgrep 15.1.0
```

If `brew info` shows an older version, `brew update && brew upgrade ripgrep` — the formula has been at 15.1.0 in `homebrew-core` since shortly after the upstream tag [[5]](https://github.com/Homebrew/homebrew-core/blob/master/Formula/r/ripgrep.rb).
