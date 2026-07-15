---
layout: expedition
title: "Splitters and dockable panes in React (2026): which libraries to adopt"
date: 2026-07-16
topic: "Which React resizable-splitter and dockable-pane libraries to adopt in 2026 — for screens with multiple grids, or grids and forms side by side. Two tiers: draggable splitters and Visual Studio-style drag-and-drop docking; plus layout persistence and hosting grids/forms inside panes."
format: md
tags: [react, ui, layout, docking-layout, frontend]
summary: "Use react-resizable-panels for fixed side-by-side splits and Dockview for VS Code-style rearrangeable docking — the tradeoffs, plus how to persist layouts and host grids/forms inside panes."
cover: cover.svg
synthesis: true
children:
  - slug: resizable-split-panes-react-resizable-panels-vs-allotment
    title: "Resizable split panes in React (2026): react-resizable-panels vs Allotment"
    depth: survey
    status: success
    summary: "react-resizable-panels is the default pick for app-shell splits; reach for Allotment only when you want VS Code look-and-feel with snapping out of the box."
    citations: 14
    reading_time_min: 5
  - slug: dockable-layout-managers-dockview-vs-rc-dock-vs-flexlayout-vs-react-mosaic
    title: "Draggable VS Code-style panes in React: Dockview vs rc-dock vs FlexLayout vs react-mosaic (2026)"
    depth: expedition
    status: success
    summary: "Yes: Dockview is the default modern pick for VS Code-style pane docking in React; three real alternatives fit narrower cases."
    citations: 40
    reading_time_min: 9
  - slug: layout-persistence-and-restoration
    title: "Persisting and restoring pane layouts in React (2026)"
    depth: survey
    status: success
    summary: "How react-resizable-panels, Allotment, Dockview, rc-dock and FlexLayout serialize and restore layouts, where to persist them, and how to survive a saved layout that references a deleted panel."
    citations: 12
    reading_time_min: 7
  - slug: hosting-grids-and-forms-inside-panes
    title: "Hosting grids and forms inside resizable/dockable panes in React: the integration problems"
    depth: survey
    status: success
    summary: "Per-library patterns and pitfalls for putting AG Grid / TanStack Table and forms inside resizable and dockable panes without layout thrash or lost state."
    citations: 24
    reading_time_min: 6
model: "Opus 4.8"
cost_usd: "sub"
issue: 10
duration_sec: 563
---

> **Decision.** Two different needs, two different libraries. For fixed **grids-and-forms-side-by-side** with draggable dividers, adopt [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) — unstyled, zero-dependency, the de-facto standard [[1]](https://www.pkgpulse.com/guides/react-resizable-panels-vs-split-js-vs-allotment-2026). For **Visual Studio-style panes the user drags, tab-stacks, splits, and floats**, adopt [Dockview](https://dockview.dev/) — the one modern, actively-maintained, framework-agnostic docker [[2]](https://github.com/mathuo/dockview). You can start with the first and add the second later without ripping anything out.

The four angles converge on one architecture: a splitter for the **app shell** (regions whose boundaries move but whose contents are fixed) and, only if users need to rearrange the workspace itself, a docking layer on top. These aren't competitors — they answer different questions. "I want a grid next to a form" is a splitter problem; "I want the user to drag the form into a tab beside the grid, then pop it into its own window" is a docking problem.

**The ecosystem has consolidated, but 2026 was a year of breaking majors.** Both winners are zero-dependency and TypeScript-first, and both shipped disruptive rewrites the tutorials haven't caught up to. react-resizable-panels v4 renamed the whole public API (`PanelGroup→Group`, `PanelResizeHandle→Separator`, `data-*→aria-*`) [[3]](https://github.com/bvaughn/react-resizable-panels/blob/main/CHANGELOG.md) — enough to break shadcn/ui's Resizable [[4]](https://github.com/shadcn-ui/ui/issues/9136). Dockview v7 split its React bindings into a separate `dockview-react` package [[5]](https://dockview.dev/docs/overview/whats-new-v7/), and react-mosaic v7 moved to an n-ary tree with first-class tabs, invalidating the old "mosaic can't tab-stack" lore [[6]](https://github.com/nomcopter/react-mosaic/releases/tag/v7.0.0). Pin versions and read the changelog, not the blog posts. One rough edge remains: Dockview still has an open StrictMode double-render issue under React 19 [[7]](https://github.com/mathuo/dockview/issues/866).

**Persistence is the seam that ties the tiers together — and the one that bites.** A splitter serializes a trivial size array (`autoSaveId` + a swappable `storage` prop) [[8]](https://github.com/bvaughn/react-resizable-panels); a docker serializes a *panel tree keyed by string component name* [[9]](https://dockview.dev/docs/core/state/save/). That difference is the whole problem: when you remove a panel in a later release, a restored layout references a component that no longer exists and `fromJSON` throws, wedging the dock [[10]](https://github.com/mathuo/dockview/issues/341). Any docking deployment needs version-stamped layouts, unknown-panel pruning, and a try/catch fallback to a default — non-negotiable, not nice-to-have.

**Hosting the actual grids and forms is where naive setups break.** A grid only fills a resizing pane if every ancestor in the flex chain has `min-height: 0` [[11]](https://github.com/philipwalton/flexbugs/issues/241); let the grid own its resize response (AG Grid `flex` columns over `sizeColumnsToFit` on every resize event) [[12]](https://www.ag-grid.com/react-data-grid/column-sizing/). The sharpest trap is docking-specific: Dockview's default `onlyWhenVisible` renderer removes hidden panels from the DOM, so switching tabs **unmounts your form and loses its state** [[13]](https://dockview.dev/docs/core/panels/rendering/) — fix it with `renderer: 'always'` or by lifting form state out of the pane tree entirely.

So the open question isn't *which library* — it's **where user-controlled layout stops paying for itself**. Every docking feature you enable (float, popout, tab-stack) multiplies the persistence and unmount edge cases above. Start with fixed splits; add docking only for the screens that genuinely earn it.
