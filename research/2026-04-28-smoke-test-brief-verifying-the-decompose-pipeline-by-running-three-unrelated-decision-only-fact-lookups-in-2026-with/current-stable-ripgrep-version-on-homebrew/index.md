---
title: "Homebrew's current stable ripgrep: 15.1.0"
date: 2026-04-28
depth: ceo
format: md
topic: "Current stable ripgrep version on Homebrew"
topic_raw: "Current stable ripgrep version on Homebrew"
issue: 39
tags: [ripgrep, homebrew, cli-tools]
summary: "Homebrew ships ripgrep 15.1.0, unchanged since the upstream October 2024 release; install with `brew install ripgrep`."
citations: 4
reading_time_min: 1
cost_usd: 0.44
duration_sec: 62
---

> **Decision:** `brew install ripgrep` lands you on **15.1.0** [[1]](https://formulae.brew.sh/formula/ripgrep) — the same release upstream cut on 2024-10-22 [[3]](https://github.com/BurntSushi/ripgrep/releases). No newer stable has been promoted since.

## Details

- **Formula version:** `ripgrep 15.1.0`, revision 0, license `Unlicense` [[1]](https://formulae.brew.sh/formula/ripgrep). The machine-readable formula API agrees: stable URL points at `github.com/BurntSushi/ripgrep/archive/refs/tags/15.1.0.tar.gz` with SHA-256 `046fa01a…2972e8` [[2]](https://formulae.brew.sh/api/formula/ripgrep.json).
- **Bottles available:** macOS arm64 (tahoe / sequoia / sonoma), macOS x86_64 (sonoma), Linux arm64 + x86_64 [[1]](https://formulae.brew.sh/formula/ripgrep). All five mean `brew install` pulls a prebuilt binary, no Rust toolchain required.
- **Upstream parity:** GitHub releases list 15.1.0 as the latest tag; it patched a line-buffering regression introduced in 15.0.0 that broke `tail -f`-style streaming [[3]](https://github.com/BurntSushi/ripgrep/releases). The repo sits at [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) ⭐ 63k (Apr 2026) [[4]](https://github.com/BurntSushi/ripgrep).

## What this means

If your `rg --version` reports anything older than `15.1.0`, run `brew upgrade ripgrep`. If it reports newer, you're either on a HEAD build (`brew install --HEAD ripgrep`) or a non-Homebrew install — Homebrew has not bumped past 15.1.0 as of this run.
