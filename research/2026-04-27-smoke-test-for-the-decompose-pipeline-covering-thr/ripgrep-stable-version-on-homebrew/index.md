---
title: ripgrep stable on Homebrew — 15.1.0
date: 2026-04-27
depth: ceo
format: md
topic: "ripgrep stable version on Homebrew"
topic_raw: "ripgrep stable version on Homebrew"
issue: 21
tags: [ripgrep, homebrew, cli, version-check]
summary: Homebrew currently pins ripgrep at 15.1.0 — same as the upstream stable release from 22 Oct 2025.
citations: 3
reading_time_min: 1
cover: cover.svg
cost_usd: 0.53
duration_sec: 74
---

> **TL;DR** — `brew install ripgrep` gives you **15.1.0** [[1]](https://formulae.brew.sh/formula/ripgrep), pinned to that version in `homebrew-core`'s formula [[2]](https://github.com/Homebrew/homebrew-core/blob/master/Formula/r/ripgrep.rb) ⭐ 15k. That matches upstream — `BurntSushi/ripgrep` ⭐ 63k tagged 15.1.0 on 22 Oct 2025 [[3]](https://github.com/BurntSushi/ripgrep/releases) ⭐ 63k, a small fix for a `--line-buffered` regression introduced in 15.0.0.

## Verify locally

```sh
brew info ripgrep   # → ripgrep: stable 15.1.0
rg --version        # → ripgrep 15.1.0
```

If `rg --version` reports older, run `brew update && brew upgrade ripgrep`. Homebrew's formula tracks upstream tags closely, so the bottle and the GitHub release should agree [[1]](https://formulae.brew.sh/formula/ripgrep)[[3]](https://github.com/BurntSushi/ripgrep/releases) ⭐ 63k.
