---
title: "Resizable split panes in React (2026): react-resizable-panels vs Allotment"
date: 2026-07-16
depth: standard
format: md
topic: "Resizable split panes in React (2026): react-resizable-panels vs Allotment — decision framework for dividing a screen into draggable, resizable regions (grids and forms side by side), covering nested/collapsible splits, snapping, min/max constraints, imperative resize API, styling/theming, persistence hooks, TypeScript, GitHub activity, bundle size, license; with react-split-pane and re-resizable as alternatives."
topic_raw: "React libraries for resizable splitters — grids and forms side by side."
tags: [react, ui, layout, split-pane, typescript, frontend]
summary: "react-resizable-panels is the default pick for app-shell splits; reach for Allotment only when you want VS Code look-and-feel with snapping out of the box."
citations: 14
reading_time_min: 5
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 281
issue: 10
---

> **Decision.** For a grid-and-form side-by-side that needs nested/collapsible splits, min/max constraints, an imperative resize API and persistence, use **[react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) ⭐ 5.3k** — unstyled, accessible, zero-dependency, the de-facto standard [[1]](https://www.pkgpulse.com/guides/react-resizable-panels-vs-split-js-vs-allotment-2026)[[2]](https://github.com/bvaughn/react-resizable-panels). Pick **[Allotment](https://github.com/johnwalley/allotment) ⭐ 1.3k** only when you want a VS Code look-and-feel with **snap-to-zero** and styled sashes out of the box and can accept 6 transitive deps + browser-only rendering [[5]](https://github.com/johnwalley/allotment). **[react-split-pane](https://github.com/tomkp/react-split-pane) ⭐ 3.4k** got a 2026 v3 rewrite (React 19, TypeScript) — viable for simple splits but a smaller ecosystem [[8]](https://github.com/tomkp/react-split-pane)[[9]](https://www.npmjs.com/package/react-split-pane). **[re-resizable](https://github.com/bokuweb/re-resizable) ⭐ 2.7k** solves a different problem — resizing one element by its edges, not dividing siblings [[10]](https://github.com/bokuweb/re-resizable).

## Comparison

| Axis | react-resizable-panels ⭐ 5.3k | Allotment ⭐ 1.3k |
|---|---|---|
| Model | Flexbox %/px, sibling panes + handle [[1]](https://www.pkgpulse.com/guides/react-resizable-panels-vs-split-js-vs-allotment-2026) | VS Code sash engine (same codebase) [[5]](https://github.com/johnwalley/allotment) |
| Nested splits | ✓ nest `Group` in `Panel` [[2]](https://github.com/bvaughn/react-resizable-panels) | ✓ nest `<Allotment>` in a pane [[5]](https://github.com/johnwalley/allotment) |
| Collapsible | ✓ `collapsible` + `collapsedSize` [[2]](https://github.com/bvaughn/react-resizable-panels) | ✓ via `snap` / `visible` prop [[5]](https://github.com/johnwalley/allotment) |
| Snapping | ✗ none [[4]](https://github.com/bvaughn/react-resizable-panels/blob/main/CHANGELOG.md) | ✓ snap-to-zero `snap` prop [[7]](https://allotment.mulberryhousesoftware.com/) |
| Min/max | ✓ `minSize`/`maxSize`, px/%/rem [[2]](https://github.com/bvaughn/react-resizable-panels) | ✓ `minSize`/`maxSize` per pane [[5]](https://github.com/johnwalley/allotment) |
| Imperative API | ✓ `resize/collapse/expand/getSize` + Group `getLayout/setLayout` [[13]](https://react-resizable-panels.vercel.app/examples/imperative-panel-api) | ✓ ref `reset()` / `resize([sizes])` [[5]](https://github.com/johnwalley/allotment) |
| Persistence hook | `useDefaultLayout` + `defaultLayout` + `onLayoutChanged` [[4]](https://github.com/bvaughn/react-resizable-panels/blob/main/CHANGELOG.md) | manual: `onChange` → your store [[5]](https://github.com/johnwalley/allotment) |
| Styling effort | high — ships unstyled, you style handles [[2]](https://github.com/bvaughn/react-resizable-panels) | low — ships CSS + CSS vars (`--separator-border`) [[5]](https://github.com/johnwalley/allotment) |
| Keyboard / ARIA | ✓ ARIA `separator`, keyboard resize [[2]](https://github.com/bvaughn/react-resizable-panels) | weaker — sash-focused, not emphasized [[5]](https://github.com/johnwalley/allotment) |
| SSR | ✓ expanded incl. Server Components (v4) [[4]](https://github.com/bvaughn/react-resizable-panels/blob/main/CHANGELOG.md) | ✗ browser-only; Next.js needs dynamic import [[5]](https://github.com/johnwalley/allotment) |
| TypeScript | full types shipped [[2]](https://github.com/bvaughn/react-resizable-panels) | authored in TS (~83%) [[5]](https://github.com/johnwalley/allotment) |
| Bundle (gzip) | 10.8 kB, **0 deps** [[14]](https://bundlephobia.com/package/react-resizable-panels) | 9.4 kB, **6 deps** [[14]](https://bundlephobia.com/package/react-resizable-panels) |
| Latest / activity | v4.12.2, pushed Jul 2026, 3 open issues [[3]](https://www.npmjs.com/package/react-resizable-panels) | v1.20.5, last publish Dec 2025, ~100 open issues [[6]](https://www.npmjs.com/package/allotment) |
| Downloads/wk | ~33.7M (rides shadcn/ui) [[11]](https://npmtrends.com/allotment-vs-react-resizable-vs-react-split-pane-vs-react-splitter-layout) | ~171k [[6]](https://www.npmjs.com/package/allotment) |
| License | MIT [[2]](https://github.com/bvaughn/react-resizable-panels) | MIT [[5]](https://github.com/johnwalley/allotment) |

## When to pick which

**react-resizable-panels** — the default. Flexbox percentage model fits app shells and dashboards (grid on one side, form on the other), nests cleanly, and its imperative handle lets you collapse the form panel or restore a saved layout from a button [[13]](https://react-resizable-panels.vercel.app/examples/imperative-panel-api). Persistence is a hook, not magic: `useDefaultLayout` seeds `defaultLayout` and you persist via `onLayoutChanged` — more wiring than v3's one-line `autoSaveId`, but you control the storage [[4]](https://github.com/bvaughn/react-resizable-panels/blob/main/CHANGELOG.md). Cost: it ships **unstyled**, so you build the drag-handle visuals yourself [[2]](https://github.com/bvaughn/react-resizable-panels). The 33.7M weekly downloads are largely shadcn/ui's Resizable wrapper depending on it [[11]](https://npmtrends.com/allotment-vs-react-resizable-vs-react-split-pane-vs-react-splitter-layout) — if you use shadcn you already have it.

⚠ **v4 is a breaking rename.** `PanelGroup→Group`, `PanelResizeHandle→Separator`, `direction→orientation`, and internal `data-*` attributes moved to `aria-*`; shadcn/ui's Resizable broke on the bump [[12]](https://github.com/shadcn-ui/ui/issues/9136). Most tutorials still show the v3 `PanelGroup/PanelResizeHandle` API — check which major you install [[4]](https://github.com/bvaughn/react-resizable-panels/blob/main/CHANGELOG.md).

**Allotment** — reach for it when you want an IDE feel with the least CSS. It is derived from VS Code's split-view code, so styled sashes, proportional layout, snap-to-zero and double-click-to-reset all work out of the box [[5]](https://github.com/johnwalley/allotment)[[7]](https://allotment.mulberryhousesoftware.com/). Snapping is its standout feature react-resizable-panels lacks [[4]](https://github.com/bvaughn/react-resizable-panels/blob/main/CHANGELOG.md). Trade-offs: it is **browser-only** (Next.js needs `dynamic(..., { ssr:false })`), pulls 6 transitive deps, carries ~100 open issues, and shipped its last release in Dec 2025 — slower cadence than react-resizable-panels [[5]](https://github.com/johnwalley/allotment)[[6]](https://www.npmjs.com/package/allotment). "Heavier and more opinionated" than the alternatives if you only need a two-column split [[1]](https://www.pkgpulse.com/guides/react-resizable-panels-vs-split-js-vs-allotment-2026).

## Alternatives, briefly

**[react-split-pane](https://github.com/tomkp/react-split-pane) ⭐ 3.4k** — long the "legacy" answer (the abandoned 0.1.x line), it received a **v3.2.0 rewrite in Feb 2026**: React 17/18/19 peer deps, TypeScript-first, hooks-based, 3.8 kB gzip, 0 deps [[8]](https://github.com/tomkp/react-split-pane)[[9]](https://www.npmjs.com/package/react-split-pane). No longer dead, but ~201k downloads/wk and a thinner feature set (no built-in collapse/snap parity) [[11]](https://npmtrends.com/allotment-vs-react-resizable-vs-react-split-pane-vs-react-splitter-layout). Fine for a plain draggable divider; react-resizable-panels remains the safer default for anything richer.

**[re-resizable](https://github.com/bokuweb/re-resizable) ⭐ 2.7k** — **not a splitter.** It resizes a *single* element via edge/corner handles (drag a card or panel bigger), not the boundary *between* two siblings that a grid-vs-form layout needs [[10]](https://github.com/bokuweb/re-resizable). Popular (~2M downloads/wk) and maintained, but wrong tool for this job — use it for individually resizable widgets, not screen division.

Also seen: **split.js** (framework-neutral, tiny, but you supply persistence/accessibility/ergonomics yourself) [[1]](https://www.pkgpulse.com/guides/react-resizable-panels-vs-split-js-vs-allotment-2026), and newer entrants like `react-resplit`. None displace react-resizable-panels as the React default in 2026.
