---
title: "Admin-console component coverage: what MUI, shadcn/ui, Mantine and Base UI actually ship in 2026"
date: 2026-07-14
depth: survey
format: md
topic: "Admin-console component coverage and the gap list for MUI, shadcn/ui, Mantine, and Base UI 1.0 in 2026: what ships in-box, what is paywalled, what is a community add-on, and what forces a second dependency."
topic_raw: "Decision framework: which React UI component kit should Itenium.Forge's frontend (itenium-ui) adopt in 2026 — MUI, shadcn/ui, Mantine, or Base UI 1.0? Greenfield admin console on an Nx 21 + React 19 + Vite + Tailwind 4 monorepo, TypeScript-first"
tags: [react, ui-components, mui, shadcn, mantine, base-ui, admin-console, data-grid, tanstack]
summary: "Only Mantine covers a CRUD admin console in-box with a single gap (the data grid); MUI's coverage is real but the grid features you actually need are paywalled; shadcn now defaults to Base UI, making them one choice, not two."
citations: 41
reading_time_min: 9
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 556
issue: 7
---

> **Decision.** Coverage-wise, **Mantine** is the only kit with exactly one hole — no data grid — and everything else (dates+range, tree, multi-select, dropzone, Tiptap RTE, charts, command palette, notifications, AppShell) MIT in-box [[18]](https://mantine.dev/getting-started/). **MUI** covers the most surface, but every grid feature an admin console reaches for on day two — virtualisation, column pinning, row grouping, Excel export — is behind MUI X Pro ($299/dev/yr) or Premium ($599/dev/yr) [[3]](https://mui.com/pricing/), and its DataGrid is a head-on duplicate of an already-decided TanStack Table. **shadcn/ui vs Base UI is no longer a fork in the road**: since July 2026 `shadcn init` defaults to Base UI [[13]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default), so shadcn = Base UI + Tailwind styling + a registry; raw Base UI is that minus the styled layer and the data components.

## What a CRUD admin console actually needs

Fourteen surfaces. Anything a kit doesn't ship becomes a second dependency you own, version, and theme.

Data grid (sort/filter/paginate) · grid at scale (virtualisation, column pinning, row grouping, CSV/Excel export) · forms + validation · date/time picker · date **range** picker · combobox/autocomplete (async + virtualised) · multi-select · tree view · dialogs/drawers/sheets · toasts · file upload/dropzone · charts · rich text editor · command palette · app shell (nav rail, breadcrumbs, responsive drawer).

## Coverage matrix

✓ = in-box and free · **$** = paid tier · ~ = community add-on / registry · ✗ = missing, forces a second dependency

| Need | [MUI](https://mui.com) ⭐ 99k [[36]](https://github.com/mui/material-ui) | [shadcn/ui](https://ui.shadcn.com) ⭐ 119k [[38]](https://github.com/shadcn-ui/ui) | [Mantine](https://mantine.dev) ⭐ 31k [[39]](https://github.com/mantinedev/mantine) | [Base UI](https://base-ui.com) ⭐ 10k [[37]](https://github.com/mui/base-ui) |
|---|---|---|---|---|
| Grid: sort / filter / paginate | ✓ [[4]](https://mui.com/x/introduction/licensing/) | ~ recipe over TanStack Table [[15]](https://ui.shadcn.com/docs/components/data-table) | ✗ (dumb `Table` only) [[18]](https://mantine.dev/getting-started/) | ✗ [[1]](https://base-ui.com/react/overview/quick-start) |
| Grid: row virtualisation | **$** Pro — Community capped at 100 rows [[5]](https://github.com/mui/mui-x/blob/master/docs/data/data-grid/virtualization/virtualization.md) ⭐ 5.8k | ~ DIY w/ TanStack Virtual | ✗ | ✗ |
| Grid: column pinning | **$** Pro [[6]](https://github.com/mui/mui-x/blob/master/docs/data/data-grid/column-pinning/column-pinning.md) ⭐ 5.8k | ~ DIY | ✗ | ✗ |
| Grid: row grouping + aggregation | **$** Premium [[4]](https://mui.com/x/introduction/licensing/) | ~ DIY | ✗ | ✗ |
| Grid: CSV export | ✓ [[7]](https://mui.com/x/react-data-grid/export/) | ~ DIY | ✗ | ✗ |
| Grid: Excel export | **$** Premium [[7]](https://mui.com/x/react-data-grid/export/) | ✗ | ✗ | ✗ |
| Forms + validation | ✗ (inputs only) [[11]](https://mui.com/material-ui/all-components/) | ✓ RHF / TanStack Form / Formisch wrappers [[14]](https://ui.shadcn.com/docs/components) | ✓ `@mantine/form` [[18]](https://mantine.dev/getting-started/) | ✓ `Field` / `Form` primitives [[1]](https://base-ui.com/react/overview/quick-start) |
| Date + time picker | ✓ [[4]](https://mui.com/x/introduction/licensing/) | ✓ react-day-picker [[16]](https://ui.shadcn.com/docs/components/date-picker) | ✓ `@mantine/dates` [[18]](https://mantine.dev/getting-started/) | ✗ [[1]](https://base-ui.com/react/overview/quick-start) |
| Date **range** picker | **$** Pro [[10]](https://mui.com/x/react-date-pickers/date-range-picker/) | ✓ range + presets [[16]](https://ui.shadcn.com/docs/components/date-picker) | ✓ `type="range"` [[20]](https://mantine.dev/dates/date-picker-input/) | ✗ |
| Combobox (async + virtualised) | ✓ Autocomplete [[11]](https://mui.com/material-ui/all-components/) | ✓ (Base UI Combobox / cmdk) [[14]](https://ui.shadcn.com/docs/components) | ✓ Combobox [[18]](https://mantine.dev/getting-started/) | ✓ async + `virtualized` via TanStack Virtual [[23]](https://base-ui.com/react/components/combobox) |
| Multi-select / tags input | ✓ [[11]](https://mui.com/material-ui/all-components/) | ~ registry only [[17]](https://ui.shadcn.com/docs/directory) | ✓ MultiSelect / TagsInput [[18]](https://mantine.dev/getting-started/) | ✓ Combobox `multiple` + Chips [[23]](https://base-ui.com/react/components/combobox) |
| Tree view | ✓ basic; **$** Pro for DnD, lazy load, virtualisation [[8]](https://mui.com/x/react-tree-view/) | ~ registry only [[17]](https://ui.shadcn.com/docs/directory) | ✓ `Tree` — checkboxes, DnD, lazy, virtualisation helpers [[19]](https://mantine.dev/core/tree/) | ✗ [[1]](https://base-ui.com/react/overview/quick-start) |
| Dialog / Drawer / Sheet | ✓ [[11]](https://mui.com/material-ui/all-components/) | ✓ [[14]](https://ui.shadcn.com/docs/components) | ✓ + modals manager [[18]](https://mantine.dev/getting-started/) | ✓ Dialog, AlertDialog, Drawer [[1]](https://base-ui.com/react/overview/quick-start) |
| Toasts | ⚠ Snackbar, no stacking — docs point to notistack [[12]](https://mui.com/material-ui/react-snackbar/) | ✓ Sonner [[14]](https://ui.shadcn.com/docs/components) | ✓ `@mantine/notifications` [[18]](https://mantine.dev/getting-started/) | ✓ Toast [[1]](https://base-ui.com/react/overview/quick-start) |
| File upload / dropzone | ✗ [[11]](https://mui.com/material-ui/all-components/) | ~ registry only [[17]](https://ui.shadcn.com/docs/directory) | ✓ `@mantine/dropzone` [[18]](https://mantine.dev/getting-started/) | ✗ [[1]](https://base-ui.com/react/overview/quick-start) |
| Charts | ✓ bar/line/pie/scatter/gauge; **$** Pro heatmap, funnel, sankey, zoom, export; **$** Premium candlestick + WebGL [[9]](https://mui.com/x/react-charts/) | ✓ Recharts wrapper [[14]](https://ui.shadcn.com/docs/components) | ✓ `@mantine/charts` (Recharts) [[18]](https://mantine.dev/getting-started/) | ✗ [[1]](https://base-ui.com/react/overview/quick-start) |
| Rich text editor | ✗ [[11]](https://mui.com/material-ui/all-components/) | ✗ [[14]](https://ui.shadcn.com/docs/components) | ✓ `@mantine/tiptap` [[18]](https://mantine.dev/getting-started/) | ✗ [[1]](https://base-ui.com/react/overview/quick-start) |
| Command palette | ✗ [[11]](https://mui.com/material-ui/all-components/) | ✓ Command (cmdk) [[14]](https://ui.shadcn.com/docs/components) | ✓ `@mantine/spotlight` [[18]](https://mantine.dev/getting-started/) | ✗ (Menu/Combobox primitives only) [[1]](https://base-ui.com/react/overview/quick-start) |
| App shell (nav, breadcrumbs, responsive drawer) | ✓ AppBar + Drawer + Breadcrumbs [[11]](https://mui.com/material-ui/all-components/) | ✓ Sidebar + Breadcrumb [[14]](https://ui.shadcn.com/docs/components) | ✓ AppShell + NavLink + Breadcrumbs [[18]](https://mantine.dev/getting-started/) | ✗ (primitives only; Navigation Menu, Toolbar) [[1]](https://base-ui.com/react/overview/quick-start) |

## The paywall, precisely

MUI X is the only paid surface among the four. Licences are per *concurrent developer touching front-end code*, perpetual use with 12 months of updates [[4]](https://mui.com/x/introduction/licensing/): **Pro $299/dev/yr, Premium $599/dev/yr** [[3]](https://mui.com/pricing/).

| Feature | Plan | Note |
|---|---|---|
| Row virtualisation | Pro | Community `DataGrid` "is limited to 100 rows" — column virtualisation is free [[5]](https://github.com/mui/mui-x/blob/master/docs/data/data-grid/virtualization/virtualization.md) ⭐ 5.8k |
| Column pinning, tree data, master-detail | Pro | [[6]](https://github.com/mui/mui-x/blob/master/docs/data/data-grid/column-pinning/column-pinning.md) ⭐ 5.8k, [[4]](https://mui.com/x/introduction/licensing/) |
| Row grouping + aggregation, Excel export | Premium | CSV, print and clipboard copy/paste stay free [[7]](https://mui.com/x/react-data-grid/export/) |
| Date **Range** Picker | Pro | [[10]](https://mui.com/x/react-date-pickers/date-range-picker/) |
| Tree View: DnD reorder, lazy children, virtualisation | Pro | expansion/selection/label-editing are free [[8]](https://mui.com/x/react-tree-view/) |
| Charts: heatmap, funnel, sankey, zoom/pan, export | Pro | [[9]](https://mui.com/x/react-charts/) |
| Charts: candlestick, WebGL at scale | Premium | [[9]](https://mui.com/x/react-charts/) |

⚠ Read the virtualisation row twice. A free MUI DataGrid renders fine at 100 rows and degrades past that; the moment an admin console hits a 5k-row table, the "free grid" argument evaporates → Pro, for every dev on the team, forever.

## The gap list, per kit

**Choose MUI → you must additionally adopt:** a form library (RHF + Zod; MUI ships inputs, not form state) [[11]](https://mui.com/material-ui/all-components/), [react-dropzone](https://react-dropzone.js.org) ⭐ 11k [[33]](https://github.com/react-dropzone/react-dropzone), [Tiptap](https://tiptap.dev) ⭐ 38k [[31]](https://github.com/ueberdosis/tiptap), [cmdk](https://cmdk.paco.me) ⭐ 13k [[30]](https://github.com/pacocoursey/cmdk) for the command palette, and [notistack](https://notistack.com) ⭐ 4.1k [[35]](https://github.com/iamhosseindhv/notistack) or Sonner for stacked toasts [[12]](https://mui.com/material-ui/react-snackbar/) — **plus a Pro/Premium licence** the day the grid needs virtualisation, pinning, grouping or Excel [[3]](https://mui.com/pricing/).

**Choose shadcn/ui → you must additionally adopt:** [TanStack Table](https://tanstack.com/table) ⭐ 28k [[25]](https://github.com/TanStack/table) (the data-table page is a build-your-own guide, not a component) [[15]](https://ui.shadcn.com/docs/components/data-table), [TanStack Virtual](https://tanstack.com/virtual) ⭐ 7k [[26]](https://github.com/TanStack/virtual) for long lists, Tiptap for the RTE, and community-registry code (or your own) for multi-select, tree view and dropzone [[17]](https://ui.shadcn.com/docs/directory). Nothing paid. Everything else — Sonner, cmdk, Recharts, react-day-picker, Sidebar, RHF form wrapper — is already in the box [[14]](https://ui.shadcn.com/docs/components).

**Choose Mantine → you must additionally adopt:** one thing — a table. Either [Mantine React Table](https://www.mantine-react-table.com/) ⭐ 1.1k [[40]](https://github.com/KevinVandy/mantine-react-table) (TanStack Table v8 under the hood, with virtualisation, grouping, aggregation, editing) [[21]](https://www.mantine-react-table.com/), or [Mantine DataTable](https://icflorescu.github.io/mantine-datatable/) ⭐ 1.2k [[41]](https://github.com/icflorescu/mantine-datatable) (lighter, dependency-free, no grouping) [[22]](https://icflorescu.github.io/mantine-datatable/), or TanStack Table wired directly to Mantine's `Table` primitive. Both wrappers are single-maintainer projects at ~1k stars — a bus-factor to price in. Everything else ships MIT [[18]](https://mantine.dev/getting-started/).

**Choose Base UI → you must additionally adopt:** the entire data layer and the entire styling layer. Base UI 1.0 (Dec 11 2025; v1.6.0 in June 2026) is 35 unstyled primitives [[2]](https://base-ui.com/react/overview/releases) — no table, no date picker, no charts, no tree, no dropzone, no RTE, no app shell [[1]](https://base-ui.com/react/overview/quick-start). You'd add TanStack Table, [react-day-picker](https://daypicker.dev) ⭐ 6.8k [[34]](https://github.com/gpbl/react-day-picker), [Recharts](https://recharts.org) ⭐ 27k [[32]](https://github.com/recharts/recharts), Tiptap, react-dropzone — i.e. you'd rebuild shadcn/ui by hand. Base UI's own docs point you there: shadcn "is a great place to start if you need pre-styled components with higher-level abstractions" [[1]](https://base-ui.com/react/overview/quick-start).

## shadcn and Base UI are the same choice now

Since **July 2026, `npx shadcn init` defaults to Base UI**; component pages open on the Base UI tab, Radix stays supported (`-b radix`) and is not deprecated, and every component now ships for both [[13]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default). So the real question is not "shadcn or Base UI" — it's "Base UI raw, or Base UI plus shadcn's styled Tailwind layer + registry". For a Tailwind 4 admin console, raw Base UI only makes sense if you intend to own a bespoke design system; otherwise shadcn is Base UI with the first 6 months of work done.

## Where headless wins regardless of kit

These are the de-facto answers no kit displaces — which is exactly why the house-level "React Dependencies" picks (state, forms, table, toasts) matter more than the kit choice.

| Need | De-facto library | ⭐ Stars | Why kit-independent |
|---|---|---|---|
| Table engine | [TanStack Table](https://tanstack.com/table) [[25]](https://github.com/TanStack/table) | ⭐ 28k | Powers shadcn's data-table [[15]](https://ui.shadcn.com/docs/components/data-table) and Mantine React Table [[21]](https://www.mantine-react-table.com/). v9 is beta as of June 2026 — start on v8 [[24]](https://tanstack.com/blog/tanstack-table-v9-taking-form) |
| Virtualisation | [TanStack Virtual](https://tanstack.com/virtual) [[26]](https://github.com/TanStack/virtual) | ⭐ 7k | Base UI's own Combobox virtualisation example uses it [[23]](https://base-ui.com/react/components/combobox) |
| Form state | [React Hook Form](https://react-hook-form.com) [[27]](https://github.com/react-hook-form/react-hook-form) | ⭐ 45k | shadcn's `Form` is an RHF wrapper [[14]](https://ui.shadcn.com/docs/components); MUI/Mantine/Base UI inputs all bind via `Controller` |
| Schema validation | [Zod](https://zod.dev) [[28]](https://github.com/colinhacks/zod) | ⭐ 43k | No kit ships validation |
| Toasts | [Sonner](https://sonner.emilkowal.ski) [[29]](https://github.com/emilkowalski/sonner) | ⭐ 13k | shadcn's toast *is* Sonner [[14]](https://ui.shadcn.com/docs/components) |
| Command palette | [cmdk](https://cmdk.paco.me) [[30]](https://github.com/pacocoursey/cmdk) | ⭐ 13k | Only Mantine has a first-party equivalent (Spotlight) [[18]](https://mantine.dev/getting-started/) |
| Rich text | [Tiptap](https://tiptap.dev) [[31]](https://github.com/ueberdosis/tiptap) | ⭐ 38k | Zero kits ship an RTE; Mantine only wraps Tiptap [[18]](https://mantine.dev/getting-started/) |
| Charts | [Recharts](https://recharts.org) [[32]](https://github.com/recharts/recharts) | ⭐ 27k | Both shadcn Charts [[14]](https://ui.shadcn.com/docs/components) and `@mantine/charts` are Recharts skins [[18]](https://mantine.dev/getting-started/) |

## Duplicate / conflict / complement, against the house picks

The team has already settled state, forms, table and toasts as standalone libraries. Judge each kit by how it lands against those:

| Kit | vs house table (TanStack) | vs house forms (RHF+Zod) | vs house toasts (Sonner) |
|---|---|---|---|
| MUI | ⚠ **Conflict.** DataGrid is MUI X's whole commercial value and a full replacement for TanStack Table [[4]](https://mui.com/x/introduction/licensing/). Paying $299–599/dev/yr for a grid you've already chosen not to use is the single worst outcome in this decision. | Complement (inputs bind via `Controller`) | Duplicate-ish; Snackbar can't stack anyway [[12]](https://mui.com/material-ui/react-snackbar/) |
| shadcn/ui | ✓ **Complement.** Its data-table *is* TanStack Table, styled [[15]](https://ui.shadcn.com/docs/components/data-table) | ✓ Complement — `Form` is the RHF wrapper [[14]](https://ui.shadcn.com/docs/components) | ✓ Complement — it *is* Sonner [[14]](https://ui.shadcn.com/docs/components) |
| Mantine | ✓ Complement (no grid to conflict with; MRT is TanStack Table anyway [[21]](https://www.mantine-react-table.com/)) | ⚠ Duplicate — `@mantine/form` goes unused [[18]](https://mantine.dev/getting-started/) | ⚠ Duplicate — `@mantine/notifications` goes unused [[18]](https://mantine.dev/getting-started/) |
| Base UI | ✓ Complement (ships nothing) | ✓ Complement — `Field`/`Form` are validation-agnostic [[1]](https://base-ui.com/react/overview/quick-start) | ⚠ Overlaps its own Toast primitive [[1]](https://base-ui.com/react/overview/quick-start) |

## Read this if you only read one thing

- Adopting MUI while TanStack Table is the house grid means paying for, and not using, the thing MUI sells [[3]](https://mui.com/pricing/), [[4]](https://mui.com/x/introduction/licensing/).
- Adopting Mantine means one extra dependency (a table) and two dead packages (`@mantine/form`, `@mantine/notifications`) — cheap [[18]](https://mantine.dev/getting-started/).
- Adopting shadcn/ui means adopting Base UI [[13]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) and building the grid from TanStack Table [[15]](https://ui.shadcn.com/docs/components/data-table) — which is what the house picks already said you'd do.
- Adopting raw Base UI means hand-building tree, dropzone, dates, charts and app shell that shadcn or Mantine would have handed you [[1]](https://base-ui.com/react/overview/quick-start).
