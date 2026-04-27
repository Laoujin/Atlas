---
title: Current stable ripgrep via Homebrew (April 2026)
date: 2026-04-27
depth: ceo
format: md
topic: "Current stable ripgrep via Homebrew (2026)"
topic_raw: "Current stable ripgrep via Homebrew (2026)"
issue: 18
tags: [ripgrep, homebrew, cli, search-tools]
summary: Homebrew ships ripgrep 15.1.0 (released Oct 2025); install with `brew install ripgrep`.
citations: 4
reading_time_min: 1
cover: cover.svg
cost_usd: 0.61
duration_sec: 98
---

> **TL;DR** — `brew install ripgrep` gets you **15.1.0** [[1]](https://formulae.brew.sh/formula/ripgrep), the current stable cut, released **Oct 22, 2025** [[2]](https://github.com/BurntSushi/ripgrep/releases). It's a bug-fix point release over 15.0.0 with no breaking changes, so existing scripts and `rg` invocations continue to work [[3]](https://github.com/BurntSushi/ripgrep/blob/master/CHANGELOG.md).

## Install

```sh
brew install ripgrep   # binary is `rg`
```

The formula pulls `pcre2` (10.47) at runtime; `asciidoctor`, `pkgconf`, and `rust` are build-time deps only and aren't installed when Homebrew uses the bottle [[1]](https://formulae.brew.sh/formula/ripgrep). Bottles exist for both Apple Silicon and Intel macOS plus Linux [[1]](https://formulae.brew.sh/formula/ripgrep).

## What 15.1.0 actually changes

| Item | Detail |
|---|---|
| Bug fix | Line-buffering regression from 15.0.0: output could lag, and `tail -f` pipelines misbehaved even with `--line-buffered` [[3]](https://github.com/BurntSushi/ripgrep/blob/master/CHANGELOG.md) |
| Feature | Hyperlink alias for the Cursor editor (`--hyperlink-format=cursor`) [[3]](https://github.com/BurntSushi/ripgrep/blob/master/CHANGELOG.md) |
| Breaking changes | None [[3]](https://github.com/BurntSushi/ripgrep/blob/master/CHANGELOG.md) |

If you upgraded to 15.0.0 and noticed `rg | tail -f` or live-pipe behaviour breaking, 15.1.0 is the fix — pin to it rather than rolling back [[2]](https://github.com/BurntSushi/ripgrep/releases).

## Verify after install

```sh
rg --version   # → ripgrep 15.1.0
brew info ripgrep
```

The upstream repo [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) ⭐ 63k (Apr 2026) is the source of truth for releases [[4]](https://github.com/BurntSushi/ripgrep) — Homebrew typically lands new tags within a day or two of release, so if `brew info` shows older than 15.1.0, run `brew update` first.
