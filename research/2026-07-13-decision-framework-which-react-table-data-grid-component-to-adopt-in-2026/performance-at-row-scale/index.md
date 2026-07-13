---
title: "React tables at row scale: where the ceilings actually are"
date: 2026-07-13
depth: standard
format: md
topic: "React table/data-grid performance at row scale in 2026: virtualization strategies, DOM vs canvas rendering, measured behaviour at 10k/100k/1M rows, column virtualization cost, React re-render and memoization pitfalls, and each library's practical ceiling."
topic_raw: "React which table component to use in 2026"
tags: [react, data-grid, performance, virtualization, tanstack, ag-grid, mui-x, canvas]
summary: "Row count is almost never the constraint that breaks a React grid — update frequency, referential stability and the browser's 33.5M-pixel scroll cap are."
citations: 28
reading_time_min: 10
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 591
issue: 1
---

> **Decision.** Virtualize above ~1k rows and the row count stops mattering: every serious grid renders ~40 rows regardless of dataset size [[10]](https://www.ag-grid.com/react-data-grid/row-models/). What actually breaks is (a) **update frequency** — MUI X users hit a wall at ~10 updates/sec [[13]](https://github.com/mui/mui-x/issues/10952) while AG Grid batches ticks outside React [[12]](https://www.ag-grid.com/react-data-grid/data-update-high-frequency/); (b) **referential stability** — an inline `.filter()` on `data` puts TanStack Table into an infinite render loop [[22]](https://tanstack.com/table/v8/docs/faq); and (c) a hard **browser cap of 17.5–33.5M px on scroll-container height** [[6]](https://mui.com/x/react-data-grid/virtualization/), which makes ~500k–900k rows the ceiling for *any* natively-scrolling grid, canvas included. Past that you need a server-side row model [[11]](https://www.ag-grid.com/react-data-grid/server-side-model/) or a custom scrollbar [[9]](https://rednegra.net/blog/20260212-virtual-scroll/).

## Every 2026 grid benchmark is written by someone selling a grid

Read this before you read any number below.

| Benchmark | Author | Also ships | Winner (surprise) |
|---|---|---|---|
| [1771 Technologies](https://www.1771technologies.com/blog/performance-benchmarks) [[3]](https://www.1771technologies.com/blog/performance-benchmarks) | 1771 Technologies | LyteNyte Grid | LyteNyte |
| [Battle of the Rows](https://dev.to/revolist/battle-of-the-rows-the-limits-of-data-performance-4mcn) [[5]](https://dev.to/revolist/battle-of-the-rows-the-limits-of-data-performance-4mcn) | Revolist OU | RevoGrid | RevoGrid |
| [react-data-grid-benchmark](https://vitashev.github.io/react-data-grid-benchmark/) [[1]](https://vitashev.github.io/react-data-grid-benchmark/) | Vitashev | Ace Grid | React Data Grid ⚠ *not his own* |

They also **contradict each other**. RevoGrid measures AG Grid at 1,297 MB and a crashed tab at 400k rows [[5]](https://dev.to/revolist/battle-of-the-rows-the-limits-of-data-performance-4mcn); 1771 measures AG Grid scrolling 1M rows at 27 FPS without crashing [[3]](https://www.1771technologies.com/blog/performance-benchmarks). Both cannot be true. Trust the one that ships a reproducible fixture, a package lock, and raw samples — currently only Vitashev's, which publishes its conflict of interest in the README and still doesn't put its own grid first [[2]](https://github.com/Vitashev/react-data-grid-benchmark) ⭐ 0.

### The one reproducible table

50,000 rows × 20 fixed-width columns, 1200×600 viewport, 36px rows, sorting + filtering + two editable columns, production bundles, pinned versions [[1]](https://vitashev.github.io/react-data-grid-benchmark/):

| Grid | JS gzip | Ready (median) | Scroll settle | Mounted cells |
|---|---:|---:|---:|---:|
| [React Data Grid](https://github.com/adazzle/react-data-grid) ⭐ 7.7k | **72.3 KB** | **367.6 ms** | **21.2 ms** | 264 |
| [TanStack Table](https://tanstack.com/table) + Virtual ⭐ 28k | 78.7 KB | 369.3 ms | 21.7 ms | 444 |
| Ace Grid Core | 224.5 KB | 387.4 ms | 28.1 ms | 220 |
| [AG Grid](https://www.ag-grid.com/) Community ⭐ 15k | 358.7 KB | 443.2 ms | 29.8 ms | 360 |
| [Handsontable](https://handsontable.com/) ⭐ 22k | 380.9 KB | 872.8 ms | 49.8 ms | 198 |

MUI X Community was excluded from the ranking — its Community tier can't virtualize past 100 rows without pagination [[6]](https://mui.com/x/react-data-grid/virtualization/).

**Read:** at 50k rows the *renderer* is not the bottleneck for anyone. The 76 ms spread between fastest and slowest (ex-Handsontable) is bundle parse + init, not scrolling. Scroll settle is 21–30 ms across the board. **Nobody is slow at 50k rows.** Pick on features, not FPS, below ~100k.

## The ceiling nobody markets: the scroll-container pixel cap

This is the single most important number in the field and no vendor page leads with it.

Browsers truncate an element's height. MUI documents 17.5M px on Firefox and 33.5M px on Chrome/Edge/Safari [[6]](https://mui.com/x/react-data-grid/virtualization/); the open TanStack Virtual issue cites 33,554,400 (FF) / 33,554,428 (Chrome) [[7]](https://github.com/TanStack/virtual/issues/616) ⭐ 7.0k; a third source measures Chromium at 16,777,216 [[8]](https://dev.to/kohii/how-to-implement-virtual-scrolling-beyond-the-browsers-limit-16ol). The exact figure is engine- and version-dependent — **budget for the low end, ~16.7M px.**

Divide by row height:

| Row height | Rows at 16.7M px | Rows at 33.5M px |
|---:|---:|---:|
| 22 px | ~760k | ~1.5M |
| 32 px | ~520k | ~1.0M |
| 36 px | ~465k | ~930k |
| 56 px (Material) | ~300k | ~600k |

Beyond that the scroll container is silently clipped and **the tail of your data is unreachable** — the virtualizer does not error, it just stops. TanStack Virtual's issue is still open [[7]](https://github.com/TanStack/virtual/issues/616): a headless virtualizer ships indices and offsets, not a scrollbar, so this is explicitly your problem [[20]](https://tanstack.com/virtual/latest/docs/introduction).

Three escapes:

1. **Server-side row model.** AG Grid's SSRM demo serves 10M records and moves the constraint to your backend [[11]](https://www.ag-grid.com/react-data-grid/server-side-model/). This is the boring correct answer.
2. **Custom scrollbar.** Replace native scrolling; position rows absolutely against a synthetic scroll position [[8]](https://dev.to/kohii/how-to-implement-virtual-scrolling-beyond-the-browsers-limit-16ol).
3. **Downscaled scrollbar resolution.** [HighTable](https://rednegra.net/blog/20260212-virtual-scroll/) caps the canvas at ~8M px and switches to a `globalAnchor` + `localOffset` model above it, claiming 1-px fidelity to ~2 trillion rows at 30px [[9]](https://rednegra.net/blog/20260212-virtual-scroll/).

⚠ **Canvas does not exempt you.** Glide Data Grid uses *native* scrolling [[16]](https://grid.glideapps.com/) — same pixel cap. Canvas fixes paint cost, not scroll geometry.

## Virtualizer selection (when you're building, not buying)

Only relevant if you pair a headless table (TanStack Table, or hand-rolled) with a virtualizer. Bought grids have virtualization built in and you should not layer another on top.

| Library | Bundle | Latest | Dynamic heights | Verdict |
|---|---:|---|---|---|
| [@tanstack/react-virtual](https://tanstack.com/virtual) ⭐ 7.0k | ~5 KB [[19]](https://www.pkgpulse.com/guides/tanstack-virtual-vs-react-window-vs-react-virtuoso-2026) | 3.14.6 (Jul 2026) | `measureElement` ref | Default if you're already on TanStack Table; headless, no markup [[20]](https://tanstack.com/virtual/latest/docs/introduction) |
| [react-virtuoso](https://virtuoso.dev/) ⭐ 6.4k | ~17 KB [[19]](https://www.pkgpulse.com/guides/tanstack-virtual-vs-react-window-vs-react-virtuoso-2026) | 4.18.10 (Jun 2026) | auto, ResizeObserver | Fewest footguns; sticky groups, bidirectional infinite scroll built in |
| [react-window](https://github.com/bvaughn/react-window) ⭐ 17k | ~6 KB | 2.2.7 (Feb 2026) | `useDynamicRowHeight` (new in v2) | ⚠ Stop repeating the "abandoned, fixed-height-only" line — v2 is a full rewrite [[21]](https://github.com/bvaughn/react-window) |

All three hold 60 FPS at 100k items on modern hardware; initial render differs by single-digit milliseconds [[19]](https://www.pkgpulse.com/guides/tanstack-virtual-vs-react-window-vs-react-virtuoso-2026). **This choice is not a performance decision.** It's an API-surface decision.

Virtualization becomes worth its overhead somewhere around 50+ simultaneously-rendered rows; below that you're paying measurement cost for nothing [[24]](https://www.material-react-table.com/docs/examples/column-virtualization).

## DOM vs canvas

| | DOM (+ virtualization) | Canvas ([Glide](https://grid.glideapps.com/) ⭐ 5.3k) |
|---|---|---|
| Paint cost at scroll | Create/destroy N nodes per frame — the argument Glide makes against DOM [[15]](https://github.com/glideapps/glide-data-grid) | Repaint dirty rects; flat memory 100 rows → 10M rows [[16]](https://grid.glideapps.com/) |
| High-frequency updates | Reconciler-bound | Vendor claims 100k+ updates/sec [[16]](https://grid.glideapps.com/) — unverified by any third party |
| Text selection / Ctrl-F / translate / autofill | ✓ free | ✗ must be re-implemented [[18]](https://news.ycombinator.com/item?id=23935464) |
| Accessibility | ✓ real semantics (though pinned columns + virtualization mangle DOM order anyway) | ⚠ hidden mirror DOM; maintainers admit "none of the primary developers are accessibility users so there are likely flaws" [[15]](https://github.com/glideapps/glide-data-grid) |
| Custom cell rendering | Any React component | Constrained to their cell-renderer model |
| CSS / theming | ✓ | ✗ draw calls |

**The dealbreaker isn't architectural, it's maintenance.** `@glideapps/glide-data-grid` latest stable is **6.0.3, published 2024-02-03** — no stable release in 29 months [[17]](https://registry.npmjs.org/@glideapps/glide-data-grid). Adopting it in 2026 means owning a canvas renderer.

HN practitioner view is also less one-sided than Glide's README: canvas wins scroll and streaming, loses layout primitives, and a well-built DOM grid can close much of the gap [[18]](https://news.ycombinator.com/item?id=23935464).

## The React tax: architecture determines re-render cost

This is where the libraries genuinely diverge, and it has nothing to do with row count.

**Framework-agnostic core, React only at the edges** — AG Grid, Handsontable. Cell updates never enter the reconciler. AG Grid's `applyTransactionAsync()` coalesces streaming ticks into a single flush every 50ms by default [[12]](https://www.ag-grid.com/react-data-grid/data-update-high-frequency/). This is why AG Grid is the trading-blotter default and why the vendor benchmark still puts it at 39 FPS on cell updates against MUI's 22 [[4]](https://medium.com/1771-technologies/benchmarked-the-top-6-react-data-grids-for-performance-and-scalability-a10a6b441789).

**Pure React component tree** — MUI X Data Grid. Every cell is a React element; the grid memoizes cells but the caller must keep every non-primitive prop referentially stable or `React.memo` is defeated at the root [[14]](https://mui.com/x/react-data-grid/performance/). Users report the grid becoming "slow and nearly unusable" at ~10 row-updates/sec on a 400-row window, where their previous plain HTML table handled 100/sec [[13]](https://github.com/mui/mui-x/issues/10952) ⭐ 5.8k. ⚠ MUI X is a *display* grid at scale, not a *streaming* grid.

**Headless — you own all of it** — TanStack Table. Zero rendering, so zero built-in re-render cost, and zero built-in protection. The classic failure is referential, not algorithmic: unstable `columns`/`data` → infinite render loop, and memoizing the base array doesn't save you if you then `.filter()` inline in the props [[22]](https://tanstack.com/table/v8/docs/faq) ⭐ 28k. Note `@tanstack/react-table` is still on **8.21.3 (Apr 2025)** [[26]](https://registry.npmjs.org/@tanstack/react-table) — stable, not dead, but v9 has not landed.

### Memoization is not free

The instinct to `memo()` your way out is a trap. Material React Table's own guide is blunt: `memoMode: 'table-body'` **disables virtualization and most features**, leaving a table "mostly frozen after first render"; memoizing rows loses access to table state like `getIsSelected()` [[23]](https://www.material-react-table.com/docs/guides/memoization). Memoize the *data*, not the *render tree*.

React Compiler auto-memoizes at build time and removes the need for manual `useMemo`/`useCallback`/`React.memo` [[27]](https://react.dev/learn/react-compiler) — but it **cannot fix an unstable `data` reference produced by an inline `.filter()`**, because that's a new array by construction, not a missed memo. The compiler does not save you from the one bug that actually bites here [[22]](https://tanstack.com/table/v8/docs/faq).

## Column virtualization and wide tables

Row virtualization is table stakes; column virtualization is where wide grids quietly die. 100k rows × 100 columns is 10M cells; without dual-axis virtualization the mounted-cell count scales with column count even when rows are virtualized.

- Threshold: **don't bother under ~12–20 columns**; it pays from "dozens" upward, and the MRT reference example uses 500 [[24]](https://www.material-react-table.com/docs/examples/column-virtualization).
- MUI X overscans 150px of columns by default (`columnBufferPx`) and — the trap — **disables column virtualization entirely when dynamic row height is enabled** [[6]](https://mui.com/x/react-data-grid/virtualization/). Wide + auto-height = every column mounted.
- React Data Grid and AG Grid virtualize both axes by default; the reproducible fixture shows RDG holding 264 mounted cells against TanStack+Virtual's 444 at 20 columns [[1]](https://vitashev.github.io/react-data-grid-benchmark/).

## Practical ceilings

| Library | Comfortable | Degrades | Hard stop |
|---|---|---|---|
| **AG Grid** (client-side) | 100k+ [[10]](https://www.ag-grid.com/react-data-grid/row-models/) | ~1M: 27 FPS scroll (vendor-measured) [[3]](https://www.1771technologies.com/blog/performance-benchmarks) | browser memory / scroll cap |
| **AG Grid** (SSRM) | 10M+ [[11]](https://www.ag-grid.com/react-data-grid/server-side-model/) | — | your backend |
| **TanStack Table + Virtual** | 100k+ [[1]](https://vitashev.github.io/react-data-grid-benchmark/) | when *you* mis-memoize | scroll cap — unsolved upstream [[7]](https://github.com/TanStack/virtual/issues/616) |
| **React Data Grid** | 50k measured, leanest bundle [[1]](https://vitashev.github.io/react-data-grid-benchmark/) | — | still `7.0.0-beta` after years |
| **MUI X Data Grid** | 10k–100k display-only | ~10 updates/sec [[13]](https://github.com/mui/mui-x/issues/10952); 1M scroll ≈ 33 FPS (vendor) [[3]](https://www.1771technologies.com/blog/performance-benchmarks) | Community caps virtualization at 100 rows [[6]](https://mui.com/x/react-data-grid/virtualization/); ⚠ open 199 MB/refresh leak at 100k [[28]](https://github.com/mui/mui-x/issues/20699) |
| **Handsontable** | ≤ ~150k; docs steer you to pagination [[25]](https://handsontable.com/docs/javascript-data-grid/performance/) | 872 ms ready at 50k — 2.4× the field [[1]](https://vitashev.github.io/react-data-grid-benchmark/) | OOM crash reported at 200k–500k [[4]](https://medium.com/1771-technologies/benchmarked-the-top-6-react-data-grids-for-performance-and-scalability-a10a6b441789) and 400k [[5]](https://dev.to/revolist/battle-of-the-rows-the-limits-of-data-performance-4mcn) |
| **Glide Data Grid** | millions (vendor) [[16]](https://grid.glideapps.com/) | — | ⚠ unmaintained since Feb 2024 [[17]](https://registry.npmjs.org/@glideapps/glide-data-grid) |

## What to actually benchmark

Vendor FPS numbers on an M4 MacBook Air [[3]](https://www.1771technologies.com/blog/performance-benchmarks) tell you nothing about your users' 2019 ThinkPads. Measure these four, on your data:

1. **Mounted cell count after a scroll to the middle** — the honest proxy for virtualization quality [[1]](https://vitashev.github.io/react-data-grid-benchmark/).
2. **Updates/sec before frame drops** — the metric that separates AG Grid from MUI X [[12]](https://www.ag-grid.com/react-data-grid/data-update-high-frequency/) [[13]](https://github.com/mui/mui-x/issues/10952).
3. **`rowCount × rowHeight` vs 16.7M px** — a pure-arithmetic go/no-go on native scrolling [[8]](https://dev.to/kohii/how-to-implement-virtual-scrolling-beyond-the-browsers-limit-16ol).
4. **Heap after 5 minutes of data refresh** — an open MUI X issue leaks ~199 MB per refresh at 100k rows, reaching 4.7 GB, with retained `CellWidget` instances from `renderCell` [[28]](https://github.com/mui/mui-x/issues/20699) ⭐ 5.8k.
