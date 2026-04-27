---
title: ripgrep stable on Homebrew — 15.1.0
date: 2026-04-27
depth: ceo
format: md
topic: "ripgrep stable version on Homebrew"
topic_raw: "ripgrep stable version on Homebrew"
issue: 19
tags: [homebrew, ripgrep, cli, macos]
cover: cover.svg
summary: Homebrew's stable ripgrep is 15.1.0 (released 2025-10-22), matching upstream — `brew install ripgrep`.
citations: 4
reading_time_min: 1
cost_usd: 0.51
duration_sec: 69
---

> **TL;DR** — Homebrew's stable `ripgrep` is **15.1.0** [[1]](https://formulae.brew.sh/formula/ripgrep), pinned by the formula tag at the same version [[2]](https://github.com/Homebrew/homebrew-core/blob/master/Formula/r/ripgrep.rb), and matching upstream's latest release from 2025-10-22 [[3]](https://github.com/BurntSushi/ripgrep/releases). Install with `brew install ripgrep`; the binary is `rg`.

## Versions at a glance

| Source | Version | Notes |
|---|---|---|
| Homebrew stable [[1]](https://formulae.brew.sh/formula/ripgrep) | 15.1.0 | License: Unlicense; depends on PCRE2; ~76k installs / 30 days |
| Homebrew formula source [[2]](https://github.com/Homebrew/homebrew-core/blob/master/Formula/r/ripgrep.rb) | 15.1.0 | `url ".../archive/refs/tags/15.1.0.tar.gz"` |
| Upstream latest [[3]](https://github.com/BurntSushi/ripgrep/releases) ([BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) ⭐ 63k (Apr 2026)) [[4]](https://github.com/BurntSushi/ripgrep) | 15.1.0 | Released 2025-10-22 |

## Recent upstream timeline [[3]](https://github.com/BurntSushi/ripgrep/releases)

| Version | Date | Notes |
|---|---|---|
| 15.1.0 | 2025-10-22 | Fix `--line-buffered` regression from 15.0.0 (broke `tail -f` interop) |
| 15.0.0 | 2025-10-16 | Major release |
| 14.1.1 | 2024-09-09 | |
| 14.1.0 | 2024-01-06 | |

## Install

```sh
brew install ripgrep
rg --version   # ripgrep 15.1.0
```

`HEAD` build is also available (`brew install --HEAD ripgrep`) if you need pre-release upstream [[1]](https://formulae.brew.sh/formula/ripgrep).
