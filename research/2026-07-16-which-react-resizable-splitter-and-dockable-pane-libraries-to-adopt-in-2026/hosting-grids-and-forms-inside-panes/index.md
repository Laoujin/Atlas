---
title: "Hosting grids and forms inside resizable/dockable panes in React: the integration problems"
date: 2026-07-16
depth: standard
format: md
topic: "Hosting data grids and forms inside resizable/dockable panes in React (2026) — the practical integration problems: making a grid fill a resizing pane, virtualization interplay on resize, layout thrash and re-renders on drag, nested scroll containers, and preserving form state/focus across hide/move/unmount."
topic_raw: "Screens with multiple grids, or grids and forms side by side."
tags: [react, data-grid, docking-layout, virtualization, resize]
summary: "Per-library patterns and pitfalls for putting AG Grid / TanStack Table and forms inside resizable and dockable panes without layout thrash or lost state."
citations: 24
reading_time_min: 6
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 360
issue: 10
---

> **Decision.** A grid fills a pane through an unbroken flex chain (`min-height:0` on every ancestor) plus a fixed height fallback — never percentage heights alone. Let the grid own its own resize response (AG Grid column `flex`, TanStack Virtual's `ResizeObserver`), don't drive it from the splitter's drag events. And treat a docked pane as a component that **will** unmount on tab-switch: lift form state out of the tree, or force the pane to stay mounted (Dockview `renderer: 'always'` [[8]](https://dockview.dev/docs/core/panels/rendering/)). Everything below is the detail behind those three rules.

## 1. Making a grid fill a resizing pane

A grid needs a concretely-sized box. Both major grids measure their container and virtualize against that measurement, so a container that computes to `height:0` renders an empty grid.

- **The percentage-height trap.** AG Grid resizes itself automatically when its container changes, but a percentage height only works if *every* parent up the chain also has an explicit height — otherwise the percentage resolves against `auto` and collapses to zero [[1]](https://www.ag-grid.com/react-data-grid/grid-size/). Splitter/dock libraries usually give the pane a pixel height via inline styles, which satisfies this — until you nest another flex column inside.
- **The flexbox `min-height:0` chain.** A flex item defaults to `min-height:auto` (= content size), so a scrollable grid nested in a `flex-direction:column` parent refuses to shrink and instead overflows the pane [[14]](https://github.com/philipwalton/flexbugs/issues/241). Fix: set `min-height:0` (and `min-width:0` for horizontal) on the flex item **and every flex ancestor up to the pane root** — a higher-level item left at `auto` blocks shrinking on descendants that already set `0` [[24]](https://moduscreate.com/blog/how-to-fix-overflow-issues-in-css-flex-layouts/).
- **Diagnostic.** AG Grid's own advice: put a border on the grid's div. If the border is the right size but the grid isn't, it's grid config; if the border is wrong, it's your CSS layout [[1]](https://www.ag-grid.com/react-data-grid/grid-size/).
- **`domLayout`.** Keep AG Grid on the default `normal` layout inside a pane so it scrolls internally. `autoHeight` renders every row into the DOM (no row virtualization) and degrades past ~1,000 rows — wrong choice for a resizable pane [[1]](https://www.ag-grid.com/react-data-grid/grid-size/).

## 2. Virtualization interplay when a pane resizes

### AG Grid

AG Grid virtualizes rows and columns internally and re-runs that calc on container resize by itself [[1]](https://www.ag-grid.com/react-data-grid/grid-size/). Your only real decision is **how columns react to width**:

- Prefer column **`flex`** over calling `api.sizeColumnsToFit()`. The docs explicitly warn *not* to call `sizeColumnsToFit` rapidly (e.g. on every resize tick) — it causes scrollbar flicker; `flex` gives smooth proportional sizing for free [[2]](https://www.ag-grid.com/react-data-grid/column-sizing/).
- `flex` can't coexist with `width`, respects `min/maxWidth`, and auto-disables on a column the user manually drags. Pin fixed columns with `suppressSizeToFit` [[2]](https://www.ag-grid.com/react-data-grid/column-sizing/).
- If you *must* run imperative logic on resize (e.g. hide columns below a width threshold), the `gridSizeChanged` event is the hook — but note the event/name was reworked across versions, so check your major version [[15]](https://github.com/ag-grid/ag-grid/issues/2440). Debounce it; don't call `sizeColumnsToFit` on every fire.
- **`ResizeObserver loop limit exceeded`.** AG Grid inside a resizing pane commonly surfaces this console error [[12]](https://github.com/ag-grid/ag-grid/issues/6562). It's browser back-pressure (a resize callback caused another resize), generally benign and non-user-facing — silence it in your error monitor rather than chasing a "fix" [[13]](https://trackjs.com/javascript-errors/resizeobserver-loop-limit-exceeded/).

### TanStack Table + TanStack Virtual

TanStack Table ships **no** virtualization; you bolt on TanStack Virtual (or react-window) yourself [[3]](https://tanstack.com/table/v8/docs/guide/virtualization). That means the pane-resize response is *your* responsibility:

- `useVirtualizer({ count, getScrollElement, estimateSize, overscan })` measures the scroll element. TanStack Virtual attaches a `ResizeObserver` to that element, so when the pane resizes the visible-row window recalculates automatically — provided `getScrollElement` points at the element that actually changes size [[4]](https://tanstack.com/virtual/v3/docs/api/virtualizer). The scroll container is a plain `div` with a fixed height and `overflow:auto` [[22]](https://tanstack.com/table/v8/docs/framework/react/examples/virtualized-rows).
- For dynamic row heights, wire `measureElement` per row; call `virtualizer.measure()` to force a recompute if you change estimates [[4]](https://tanstack.com/virtual/v3/docs/api/virtualizer).
- **The row-virtualization × column-resize collision.** With fixed-size row virtualization, resizing a column that rewraps cell text changes actual row heights, invalidating the virtualizer's cached offsets → rows overlap or leave gaps. There's no clean fix beyond invalidating on every drag tick (expensive) or avoiding wrap during resize [[5]](https://github.com/TanStack/table/discussions/2607).

## 3. Avoiding layout thrash and excessive re-renders on drag

Dragging a splitter fires continuously. Two failure modes: (a) synchronous layout reads/writes per event (thrash), (b) React re-rendering thousands of virtualized cells per frame.

- **Throttle to the frame, not to a timer.** Wrap resize handlers in `requestAnimationFrame` so at most one layout pass happens per painted frame; raw resize/drag events fire far faster than 60Hz [[23]](https://www.frankcode.com/blog/request-animation-frame-is-magic).
- **Prefer CSS-driven splitters.** Libraries that resize via CSS `grid-template` columns (GeoffCox/react-splitter [[19]](https://github.com/GeoffCox/react-splitter) ⭐ 52) or panel-group libs (react-resizable-panels [[18]](https://github.com/bvaughn/react-resizable-panels) ⭐ 5.3k) let the browser do the resize with zero React renders per frame — the grid just sees a new box afterward.
- **Column resize without re-rendering the body.** TanStack's official performant pattern: compute all column widths once (memoized), memoize the table body while a resize is in progress, and push widths to cells as **CSS variables** (`--col-<id>-size`) set imperatively in a `useLayoutEffect` — the browser applies new widths with zero React work per frame, hitting 60fps [[6]](https://tanstack.com/table/latest/docs/framework/react/examples/column-resizing-performant) [[7]](https://tanstack.com/table/v8/docs/guide/column-sizing).
- **Stabilise object props.** In AG Grid React, `useMemo` your `defaultColDef`/`autoSizeStrategy` — a fresh object each render churns the grid [[2]](https://www.ag-grid.com/react-data-grid/column-sizing/). In react-window [[20]](https://github.com/bvaughn/react-window) ⭐ 17k, a `useCallback` row renderer can *hurt*: changing any item prop re-renders the whole list, so pass a stable named component and data via `itemData` [[5]](https://github.com/TanStack/table/discussions/2607).

## 4. Nested scroll containers

Grids-in-panes stack scroll containers: pane → grid viewport → virtualized body. Pitfalls:

- **Single scroll owner.** Give exactly one element the vertical scroll. If both the pane wrapper and the grid scroll, drag-resize produces double scrollbars and mis-measured virtualization. Let the grid own its scroll; the pane wrapper is `overflow:hidden` with the `min-height:0` chain from §1.
- **Hidden panes measure 0.** A `ResizeObserver` on a `display:none` (or DOM-removed) element reports 0px, which resets virtualizer measurements; on re-show, rows re-measure and the layout jumps [[4]](https://tanstack.com/virtual/v3/docs/api/virtualizer). This directly motivates the docking-renderer choice in §5.
- **react-virtuoso** is explicitly built to be flexbox-safe and adapt to parent size changes, which sidesteps some manual `ResizeObserver` wiring for list/table content [[21]](https://github.com/petyosi/react-virtuoso) ⭐ 6.4k.

## 5. Preserving form state and focus across hide / move / unmount

The sharpest problem: in a docking layout ([Dockview](https://github.com/mathuo/dockview) ⭐ 3.3k [[9]](https://github.com/mathuo/dockview), FlexLayout, rc-dock), switching to another tab in the same group **unmounts** the hidden pane's React tree. React state, uncontrolled input values, scroll position, and focus all vanish.

**Two strategies, pick per pane:**

| Strategy                         | How                                                                                                                                                 | Cost                                                                            |
|----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Keep it mounted                  | Dockview `renderer: 'always'` (or per-dock `defaultRenderer`) keeps the DOM alive via `visibility:hidden`, preserving scroll + DOM state [[8]][d8]   | More memory; background timers/`rAF`/animations keep running unless you gate them via `onDidVisibilityChange` [[8]][d8] |
| Let it unmount, keep state outside | Lift form values to a store (Zustand/Redux/context) or parent; the pane re-hydrates on remount                                                     | You own serialization; focus/scroll aren't restored automatically              |

[d8]: https://dockview.dev/docs/core/panels/rendering/

- **Dockview default is destructive.** `onlyWhenVisible` (the default) removes the hidden panel from the DOM — measuring returns 0px and DOM state is lost. Switch to `'always'` for panes hosting forms or scrolled grids whose state must survive a tab-switch [[8]](https://dockview.dev/docs/core/panels/rendering/).
- **FlexLayout** preserves component state when tabs are *moved* between locations, and only re-mounts on popout when you opt in with `enableWindowReMount` [[11]](https://github.com/caplin/FlexLayout) ⭐ 1.3k. **rc-dock** [[10]](https://github.com/ticlo/rc-dock) ⭐ 812 is the other common React docker. Confirm each library's hidden-tab behaviour rather than assuming — mount/unmount policy differs.
- **React Hook Form specifics.** RHF stores values inside the inputs, so an unmounted tab-form loses them; its own FAQ says to capture submission data into local/global state for modal/tab forms rather than trusting the mounted inputs [[16]](https://react-hook-form.com/faqs). By default RHF *retains* a field's value when that input unmounts, but `shouldUnregister:true` discards it on unmount — know which you've set before relying on persistence [[17]](https://react-hook-form.com/docs/useform).
- **Focus restoration is separate.** Neither "keep mounted" nor "lift state" restores the caret/active element on re-show automatically. If focus matters, record `document.activeElement`'s field id on hide and call `.focus()` in the panel's show hook (`onShow`/`onDidVisibilityChange`) [[8]](https://dockview.dev/docs/core/panels/rendering/).

## Pitfall checklist

- ⚠ Percentage-height grid in a pane with any `auto`-height ancestor → collapses to 0. Use the `min-height:0` flex chain or a fixed px height [[1]](https://www.ag-grid.com/react-data-grid/grid-size/) [[14]](https://github.com/philipwalton/flexbugs/issues/241).
- ⚠ Calling `sizeColumnsToFit` on every resize tick → scrollbar flicker. Use column `flex` [[2]](https://www.ag-grid.com/react-data-grid/column-sizing/).
- ⚠ `ResizeObserver loop limit exceeded` from AG Grid → benign, silence in monitoring [[12]](https://github.com/ag-grid/ag-grid/issues/6562) [[13]](https://trackjs.com/javascript-errors/resizeobserver-loop-limit-exceeded/).
- ⚠ Fixed-height row virtualization + resizable wrapping columns → stale offsets, overlaps [[5]](https://github.com/TanStack/table/discussions/2607).
- ⚠ New `defaultColDef`/renderer identity each render → grid churn; memoize [[2]](https://www.ag-grid.com/react-data-grid/column-sizing/).
- ⚠ Column resize re-rendering all virtualized cells → drive widths via CSS variables, memoize the body [[6]](https://tanstack.com/table/latest/docs/framework/react/examples/column-resizing-performant) [[7]](https://tanstack.com/table/v8/docs/guide/column-sizing).
- ⚠ Docked tab-form silently loses data on tab switch → `renderer:'always'` or lift state out [[8]](https://dockview.dev/docs/core/panels/rendering/) [[16]](https://react-hook-form.com/faqs).
