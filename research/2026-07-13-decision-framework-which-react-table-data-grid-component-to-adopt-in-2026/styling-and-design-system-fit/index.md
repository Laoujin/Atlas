---
title: "Styling and design-system fit: which React grid bends to your design system?"
date: 2026-07-13
depth: ceo
format: md
topic: "Styling and design-system fit for React tables in 2026: headless vs opinionated CSS vs copy-paste source, Tailwind v4 integration, theming and design-token plumbing, and the design-system lock-in of MUI X DataGrid and Mantine React Table."
topic_raw: "React which table component to use in 2026"
tags: [react, data-grid, design-systems, tailwind, theming]
summary: "If the design system is authoritative, go headless (TanStack Table, or shadcn's copy-paste wiring of it); grid-owned CSS is only worth it when you're buying AG Grid's feature set, and MUI X / Mantine grids are design-system adoptions, not component adoptions."
citations: 8
reading_time_min: 2
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 175
issue: 1
---

> **Decision.** If your design system is the source of truth, adopt [TanStack Table](https://tanstack.com/table) ⭐ 28.2k (Jul 2026) — headless, zero markup, zero CSS to override [[1]](https://www.pkgpulse.com/guides/tanstack-table-v8-vs-ag-grid-vs-mui-data-grid-2026) — and let [shadcn/ui](https://ui.shadcn.com) ⭐ 119k (Jul 2026) hand you the wiring as source you own [[2]](https://ui.shadcn.com/docs/components/radix/data-table). Take [AG Grid](https://www.ag-grid.com) ⭐ 15.5k only when you're buying its feature set and accept its DOM; its Theming API buys back most (not all) of the look [[3]](https://www.ag-grid.com/react-data-grid/theming-css/). [MUI X DataGrid](https://mui.com/x/react-data-grid/) ⭐ 5.8k and [Mantine React Table](https://www.mantine-react-table.com) ⭐ 1.1k are not component decisions — they are design-system decisions [[4]](https://www.mantine-react-table.com/docs/guides/customize-components).

## The four styling models

| Model | Library | You own | Token plumbing | Escape hatch cost |
|---|---|---|---|---|
| Headless | TanStack Table | 100% of markup + CSS [[1]](https://www.pkgpulse.com/guides/tanstack-table-v8-vs-ag-grid-vs-mui-data-grid-2026) | Native — it's your CSS | n/a (nothing to escape) |
| Copy-paste source | shadcn/ui `data-table` (TanStack under it) | The generated components, in-repo [[2]](https://ui.shadcn.com/docs/components/radix/data-table) | Tailwind tokens directly | Edit the file |
| Grid-owned CSS, variable-driven | AG Grid | Nothing; you tune ~100 `--ag-*` params [[5]](https://www.ag-grid.com/javascript-data-grid/theming-parameters/) | `--ag-background-color: var(--brand-surface)` [[3]](https://www.ag-grid.com/react-data-grid/theming-css/) | ⚠ Class-level CSS breaks: "DOM structure changes with each release" [[3]](https://www.ag-grid.com/react-data-grid/theming-css/) |
| Design-system-bound | MUI X DataGrid, Mantine React Table | Nothing; you theme the *system* [[4]](https://www.mantine-react-table.com/docs/guides/customize-components) | Through emotion + that system's theme object | Adopting the whole DS |

## Where each fights Tailwind v4

Tailwind v4's utilities live in `@layer utilities`, and **unlayered CSS beats layered CSS regardless of specificity** [[6]](https://github.com/tailwindlabs/tailwindcss/discussions/20306) ⭐ 96k. Any grid that injects runtime `<style>` tags (emotion) therefore wins over your utility classes by default → `!important` sprawl.

- **MUI X:** fixable, not free. Turn on `enableCssLayer` (`StyledEngineProvider` / `AppRouterCacheProvider`) and declare `@layer theme, base, mui, components, utilities;` — `mui` must precede `utilities` [[7]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/). This exists precisely because MUI's selectors out-specify Tailwind and forced `!important` [[8]](https://github.com/mui/material-ui/issues/44700) ⭐ 98.6k.
- **Mantine React Table:** same emotion/`sx` model, same layering problem, plus you inherit Mantine's `primaryColor`/`gray`/`dark` scales as the grid's palette [[4]](https://www.mantine-react-table.com/docs/guides/customize-components).
- **AG Grid:** cleanest of the opinionated set — `--ag-*` variables accept `var()` references to your own tokens, so dark mode is a token swap, not a theme rebuild [[3]](https://www.ag-grid.com/react-data-grid/theming-css/). The Theming API validates params and gives TS autocompletion instead of blind CSS [[5]](https://www.ag-grid.com/javascript-data-grid/theming-parameters/).
- **TanStack/shadcn:** nothing to fight. No CSS ships.

## Override cost vs build cost

Overriding AG Grid is bounded while you stay on variables and single-class selectors; it turns unbounded the moment you write structural CSS, since `position`/`overflow`/`pointer-events` are load-bearing and editing them "may break functionality" [[3]](https://www.ag-grid.com/react-data-grid/theming-css/). Building from scratch on TanStack is a fixed, front-loaded cost (rows, headers, sticky, virtualization markup) that never regresses on upgrade — which is why "design-system control matters most → TanStack" is the standing 2026 recommendation [[1]](https://www.pkgpulse.com/guides/tanstack-table-v8-vs-ag-grid-vs-mui-data-grid-2026).

**Lock-in test:** if your app is not already MUI or Mantine, their grids import a whole design system (theme object, emotion runtime, component vocabulary) to render a table. That's the real price tag [[1]](https://www.pkgpulse.com/guides/tanstack-table-v8-vs-ag-grid-vs-mui-data-grid-2026)[[4]](https://www.mantine-react-table.com/docs/guides/customize-components).
