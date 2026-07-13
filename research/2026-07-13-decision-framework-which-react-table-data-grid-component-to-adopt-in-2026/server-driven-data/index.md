---
title: "Server-driven data: which React table actually does the work for you"
date: 2026-07-13
depth: standard
format: md
topic: "Server-driven data in React tables in 2026 — how TanStack Table, AG Grid SSRM, MUI X DataGrid and Mantine React Table support server-side pagination/sorting/filtering/grouping, the manual* opt-outs, TanStack Query/SWR integration, infinite scroll and cursor vs offset, RSC/App Router fit, and debounce/race pitfalls."
topic_raw: "React which table component to use in 2026"
tags: [react, data-grid, tanstack-table, ag-grid, mui-x, server-side, tanstack-query, nextjs]
summary: "AG Grid's Server-Side Row Model and MUI X's Data Source are real server-driven engines; TanStack Table only gives you manual* opt-outs and hands you the state machine."
citations: 31
reading_time_min: 8
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 553
issue: 1
---

> **Decision.** If the server owns pagination + sorting + filtering **and grouping/aggregation**, only [AG Grid](https://www.ag-grid.com/react-data-grid/server-side-model/)'s Server-Side Row Model [[12]](https://www.ag-grid.com/react-data-grid/server-side-model/) and [MUI X](https://mui.com/x/react-data-grid/server-side-data/)'s Data Source [[18]](https://mui.com/x/react-data-grid/server-side-data/) are first-class engines that fetch, cache and lazy-load for you — both paywalled at the group/aggregate tier [[13]](https://www.ag-grid.com/react-data-grid/row-models/)[[20]](https://mui.com/x/react-data-grid/server-side-data/aggregation/). [TanStack Table](https://tanstack.com/table/latest) gives you `manual*` **opt-outs**, not an engine: you own the state, the fetch, the debounce and the page-reset [[1]](https://tanstack.com/table/latest/docs/guide/pagination)[[5]](https://github.com/TanStack/table/issues/4797) — pair it with [TanStack Query](https://tanstack.com/query/latest) and it's excellent, but the wiring is yours. [Mantine React Table](https://www.mantine-react-table.com/) inherits exactly TanStack Table v8's manual model and adds nothing server-side [[24]](https://www.mantine-react-table.com/docs/guides/pagination).

## The axis that actually splits the field

There are two philosophies, and the word "supports server-side pagination" hides the difference:

- **Opt-out model** (TanStack Table, MRT): you flip `manualPagination` / `manualSorting` / `manualFiltering` and the table *stops doing the work*. It does not start doing it on the server — it just believes whatever `data` array you hand it [[1]](https://tanstack.com/table/latest/docs/guide/pagination)[[2]](https://tanstack.com/table/latest/docs/guide/column-filtering)[[3]](https://tanstack.com/table/v8/docs/guide/sorting).
- **Datasource model** (AG Grid SSRM, MUI X Data Source): you implement one `getRows(params)` callback; the grid owns the request lifecycle, block cache, scroll-triggered fetching, loading skeletons and error surface [[12]](https://www.ag-grid.com/react-data-grid/server-side-model/)[[14]](https://www.ag-grid.com/react-data-grid/server-side-model-datasource/)[[18]](https://mui.com/x/react-data-grid/server-side-data/).

## Feature matrix

| | [TanStack Table](https://github.com/TanStack/table) ⭐ 28.2k | [AG Grid](https://github.com/ag-grid/ag-grid) ⭐ 15.5k (SSRM) | [MUI X DataGrid](https://github.com/mui/mui-x) ⭐ 5.8k | [Mantine React Table](https://github.com/KevinVandy/mantine-react-table) ⭐ 1.1k |
|---|---|---|---|---|
| Server pagination | `manualPagination` + you supply `rowCount`/`pageCount` [[1]](https://tanstack.com/table/latest/docs/guide/pagination) | ✓ block-based, grid-driven [[12]](https://www.ag-grid.com/react-data-grid/server-side-model/) | ✓ `paginationMode="server"` or Data Source [[21]](https://mui.com/x/react-data-grid/pagination/) | `manualPagination` + `rowCount` [[24]](https://www.mantine-react-table.com/docs/guides/pagination) |
| Server sort/filter | `manualSorting` / `manualFiltering` [[2]](https://tanstack.com/table/latest/docs/guide/column-filtering)[[3]](https://tanstack.com/table/v8/docs/guide/sorting) | ✓ `sortModel`/`filterModel` in request, cache auto-purged [[15]](https://www.ag-grid.com/react-data-grid/infinite-scrolling/) | ✓ `sortingMode`/`filterMode="server"` [[22]](https://mui.com/x/api/data-grid/data-grid/) | same as TanStack v8 [[25]](https://github.com/KevinVandy/mantine-react-table) |
| Server grouping / aggregation | `manualGrouping` exists, but "not currently many known easy ways" [[4]](https://tanstack.com/table/latest/docs/guide/grouping) | ✓ lazy group expansion, pivot, aggregation — **Enterprise** [[13]](https://www.ag-grid.com/react-data-grid/row-models/) | ✓ `aggregationModel` + `getAggregatedValue()` — **Premium** [[20]](https://mui.com/x/react-data-grid/server-side-data/aggregation/) | ✗ inherits TanStack's gap [[4]](https://tanstack.com/table/latest/docs/guide/grouping) |
| Infinite / lazy scroll | build it: Table + Query `useInfiniteQuery` + Virtual [[7]](https://tanstack.com/table/v8/docs/framework/react/examples/virtualized-infinite-scrolling) | ✓ Infinite Row Model (free) or SSRM (Enterprise) [[13]](https://www.ag-grid.com/react-data-grid/row-models/) | ✓ `lazyLoading` prop — **Pro** [[19]](https://mui.com/x/react-data-grid/server-side-data/lazy-loading/) | ✗ build it |
| Built-in request cache | ✗ (bring TanStack Query) | ✓ block cache, `cacheBlockSize` 100, `maxBlocksInCache` LRU [[15]](https://www.ag-grid.com/react-data-grid/infinite-scrolling/) | ✓ `GridDataSourceCacheDefault`, 5-min TTL, swappable [[18]](https://mui.com/x/react-data-grid/server-side-data/) | ✗ |
| Built-in scroll debounce | ✗ | ✓ `blockLoadDebounceMillis` [[15]](https://www.ag-grid.com/react-data-grid/infinite-scrolling/) | ✓ 500 ms viewport-loading throttle [[19]](https://mui.com/x/react-data-grid/server-side-data/lazy-loading/) | ✗ |
| Renders in RSC | ✗ `'use client'` | ✗ `'use client'` — depends on `window`/`document` [[16]](https://blog.ag-grid.com/using-ag-grid-with-next-js-to-build-a-react-table/) | ✗ `'use client'` | ✗ `'use client'` |
| Cost of server mode | free (your time) | Enterprise license for SSRM [[13]](https://www.ag-grid.com/react-data-grid/row-models/) | MIT for basic Data Source [[23]](https://mui.com/blog/mui-x-v8/); Pro/Premium for lazy load + aggregation [[19]](https://mui.com/x/react-data-grid/server-side-data/lazy-loading/)[[20]](https://mui.com/x/react-data-grid/server-side-data/aggregation/) | free |

## TanStack Table: what state you actually own

`manualPagination: true` makes the table use `getPrePaginationRowModel` and "assume that the `data` that you pass in is already paginated" [[1]](https://tanstack.com/table/latest/docs/guide/pagination). You must then supply `rowCount` (the table derives `pageCount` from it) or `pageCount: -1` for unknown totals — at which point `getCanNextPage()` always returns `true` [[1]](https://tanstack.com/table/latest/docs/guide/pagination).

```tsx
const [pagination, setPagination] = useState({ pageIndex: 0, pageSize: 50 });
const [sorting, setSorting]       = useState<SortingState>([]);
const [filters, setFilters]       = useState<ColumnFiltersState>([]);

const q = useQuery({
  queryKey: ['rows', pagination, sorting, filters],   // the key IS the server query
  queryFn: () => fetchRows({ pagination, sorting, filters }),
  placeholderData: keepPreviousData,                  // no flash-to-empty on page change
});

const table = useReactTable({
  data: q.data?.rows ?? [],
  columns,
  getCoreRowModel: getCoreRowModel(),
  manualPagination: true, manualSorting: true, manualFiltering: true,
  rowCount: q.data?.total,
  state: { pagination, sorting, columnFilters: filters },
  onPaginationChange: setPagination,
  onSortingChange: setSorting,
  onColumnFiltersChange: setFilters,
});
```

Three sharp edges this snippet does **not** solve:

1. **Page reset is yours.** `autoResetPageIndex` is disabled automatically when `manualPagination` is on [[1]](https://tanstack.com/table/latest/docs/guide/pagination). Consequence: user on page 1000 types a filter → the table still requests page 1000 → empty results. Open since v8 as [issue #4797](https://github.com/TanStack/table/issues/4797) ⭐ 28.2k [[5]](https://github.com/TanStack/table/issues/4797). Wrap `setFilters`/`setSorting` so they also `setPagination(p => ({...p, pageIndex: 0}))`.
2. **Debounce is yours.** Nothing in the table batches keystrokes; naively you "perform a request with every keystroke" [[31]](https://www.robinwieruch.de/react-server-side-table/).
3. **Grouping is effectively unsupported.** `manualGrouping` exists, but the official guide states there are "not currently many known easy ways to do server-side grouping with TanStack Table. You will need to do lots of custom cell rendering to make this work" [[4]](https://tanstack.com/table/latest/docs/guide/grouping). If your table groups server-side, this alone disqualifies TanStack Table.

**v9 status:** beta since 7 June 2026, with TanStack Store-backed state, plugin-registered features and large memory/type-instantiation wins [[6]](https://tanstack.com/blog/tanstack-table-v9-taking-form). The V9 announcement says nothing about improving server-driven mode — the `manual*` opt-out philosophy is unchanged [[6]](https://tanstack.com/blog/tanstack-table-v9-taking-form). Adopting v9 in 2026 means adopting a beta.

## AG Grid SSRM: the grid owns the request

You register one datasource; the grid calls `getRows` whenever it needs a block, and the `request` carries `startRow`/`endRow`, `sortModel`, `filterModel`, `rowGroupCols`, `groupKeys`, `valueCols`, `pivotCols` [[12]](https://www.ag-grid.com/react-data-grid/server-side-model/).

```ts
const datasource: IServerSideDatasource = {
  getRows: params => {
    const res = server.getData(params.request);
    res.success ? params.success({ rowData: res.rows, rowCount: res.total }) : params.fail();
  },
};
```
[[14]](https://www.ag-grid.com/react-data-grid/server-side-model-datasource/)

What you get for free: block cache (`cacheBlockSize` default 100, `maxBlocksInCache` LRU eviction), `blockLoadDebounceMillis` to suppress fetches during fast scrolls, and automatic cache purge + refetch when sort/filter change [[15]](https://www.ag-grid.com/react-data-grid/infinite-scrolling/). The Infinite Row Model is Community, but "aggregation and grouping are not available in infinite scrolling" [[15]](https://www.ag-grid.com/react-data-grid/infinite-scrolling/) — so any grouped server table means SSRM, which is Enterprise [[13]](https://www.ag-grid.com/react-data-grid/row-models/). AG Grid's own guidance: "Server-Side Row Model is Infinite Row Model plus more. So if you are an AG Grid Enterprise customer, you should prefer Server-Side Row Model" [[13]](https://www.ag-grid.com/react-data-grid/row-models/).

⚠ **TanStack Query friction.** `getRows` is a plain callback, not a component, so you cannot call `useQuery` inside it. The working pattern is `const qc = useQueryClient()` in the component and `qc.fetchQuery({ queryKey: [...request], queryFn })` inside `getRows`, memoising the datasource with `useMemo` and putting every request param in the key [[17]](https://scientyficworld.org/how-to-integrate-react-query-with-ag-grid/). You are then running two caches (Query's and the grid's block cache) — decide which one is authoritative before you build.

## MUI X: Data Source, and the plan cliff

`GridDataSource.getRows(params)` receives `filterModel`, `sortModel`, `paginationModel`, `start`/`end`, `groupKeys`, `aggregationModel`; the grid handles caching (`GridDataSourceCacheDefault`, 5-minute TTL, chunk-split for hit rate), errors via `onDataSourceError()` (`GridGetRowsError` vs `GridUpdateRowError`), loading overlays, and `dataSourceKeepPreviousData` to hold rows during a refetch [[18]](https://mui.com/x/react-data-grid/server-side-data/). `dataSourceCache` accepts any `{get,set,clear}` object, so a TanStack `QueryClient` can back it directly [[18]](https://mui.com/x/react-data-grid/server-side-data/). `dataSourceRevalidateMs` adds background polling [[18]](https://mui.com/x/react-data-grid/server-side-data/).

The classic manual path also still exists on the **MIT** grid: `paginationMode`, `sortingMode`, `filterMode` all accept `'server'`, and `dataSource` is on the free `DataGrid` API surface [[22]](https://mui.com/x/api/data-grid/data-grid/); v8 explicitly moved the Data Source into the Community plan [[23]](https://mui.com/blog/mui-x-v8/).

Where the plan cliff bites:

| Capability | Plan |
|---|---|
| `paginationMode`/`sortingMode`/`filterMode="server"`, basic `dataSource` | Community (MIT) [[22]](https://mui.com/x/api/data-grid/data-grid/)[[23]](https://mui.com/blog/mui-x-v8/) |
| `lazyLoading` (viewport skeletons + infinite scroll) | Pro [[19]](https://mui.com/x/react-data-grid/server-side-data/lazy-loading/) |
| Server-side aggregation, row grouping, tree data | Premium [[20]](https://mui.com/x/react-data-grid/server-side-data/aggregation/) |

⚠ **Row-count trap:** "If the value `rowCount` becomes `undefined` during loading, it will reset the page to zero" — memoise it across fetches [[21]](https://mui.com/x/react-data-grid/pagination/).

**Cursor vs offset:** MUI's lazy loading picks its strategy from the count. Known `rowCount` → *viewport loading* (skeleton rows, fetch when a skeleton enters the render window, 500 ms request throttle). `rowCount = -1` or `undefined` → *infinite loading* (fetch at scroll-end, stop when the server returns nothing) [[19]](https://mui.com/x/react-data-grid/server-side-data/lazy-loading/). That maps cleanly onto offset vs cursor backends: cursor APIs cannot cheaply produce a total, so hand the grid `-1` plus `paginationMeta.hasNextPage` (or `estimatedRowCount`) [[21]](https://mui.com/x/react-data-grid/pagination/). In TanStack land, cursor pagination is `useInfiniteQuery` + `getNextPageParam` returning the server's `nextCursor` [[10]](https://tanstack.com/query/v5/docs/framework/react/guides/infinite-queries).

## The data layer: Query / SWR

TanStack Query [(⭐ 50k)](https://github.com/TanStack/query) is the default pairing for the opt-out grids. v5 **removed** `keepPreviousData` and `isPreviousData`; you now write `placeholderData: keepPreviousData` (the imported identity helper) and read `isPlaceholderData` [[9]](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5). Its value for tables: "the data from the last successful fetch is available while new data is being requested, even though the query key has changed," and swaps seamlessly on arrival [[8]](https://tanstack.com/query/latest/docs/framework/react/guides/paginated-queries) — this is what kills the page-flicker-to-empty. Gate the Next button on `isPlaceholderData || !data.hasMore` so users can't over-page into placeholder data [[8]](https://tanstack.com/query/latest/docs/framework/react/guides/paginated-queries). Infinite tables use `useInfiniteQuery` (+ `maxPages` to cap retained/refetched pages) with `@tanstack/react-virtual`; TanStack ships an official Table + Query + Virtual infinite example [[7]](https://tanstack.com/table/v8/docs/framework/react/examples/virtualized-infinite-scrolling)[[10]](https://tanstack.com/query/v5/docs/framework/react/guides/infinite-queries).

SWR does the same job with one option: `useSWR(\`/api/data?page=${page}\`, fetcher, { keepPreviousData: true })` keeps prior data across key changes [[11]](https://swr.vercel.app/docs/pagination). It has no equivalent of Query's `fetchQuery` imperative escape hatch story for grid datasources, so for AG Grid SSRM / MUI Data Source, Query is the better fit.

## Debounce ≠ race safety

React's own docs are blunt: "network responses may arrive in a different order than you sent them" — the `useEffect` + `ignore`-flag cleanup exists precisely for this, and the docs then tell you not to hand-roll it at all and to use TanStack Query or SWR [[30]](https://react.dev/reference/react/useEffect). Applied to tables:

- Debouncing a filter input only reduces *how many* requests fire. If a request outlives the debounce window, the stale response can still land last and overwrite the fresh one [[30]](https://react.dev/reference/react/useEffect)[[31]](https://www.robinwieruch.de/react-server-side-table/).
- Putting `{pagination, sorting, filters}` **into the query key** structurally removes the race: each parameter combination is a distinct cache entry, so a late response writes into *its own* key, not the visible one [[8]](https://tanstack.com/query/latest/docs/framework/react/guides/paginated-queries).
- Debounce the *state update that feeds the key*, not the fetch, and always reset `pageIndex` in the same transaction as the filter/sort change [[5]](https://github.com/TanStack/table/issues/4797).
- The datasource grids sidestep most of this: AG Grid purges and refetches on sort/filter change [[15]](https://www.ag-grid.com/react-data-grid/infinite-scrolling/) and MUI throttles viewport requests to 500 ms [[19]](https://mui.com/x/react-data-grid/server-side-data/lazy-loading/).

## RSC / App Router reality

**No grid renders in a Server Component.** All four need `'use client'`, and once a file is marked, "all of its imports and the components it directly renders are included in the client bundle" [[29]](https://nextjs.org/docs/app/getting-started/server-and-client-components). AG Grid says it outright: `ag-grid-react` "depends on some browser-specific APIs (e.g. `window`/`document`) and can not be rendered server-side" [[16]](https://blog.ag-grid.com/using-ag-grid-with-next-js-to-build-a-react-table/).

The pattern that actually works in the App Router is **URL-as-table-state**:

1. Server Component `page.tsx` parses `searchParams` (a Promise since Next 15) via `createSearchParamsCache` and passes typed page/sort/filter down without prop-drilling [[26]](https://nuqs.dev/docs/server-side).
2. It fetches server-side and streams rows into a thin `'use client'` table shell.
3. The client shell writes state back with [nuqs](https://nuqs.dev) ⭐ 10.7k `useQueryState`; `shallow: false` opts into "notifying the server (to re-render Server Components on the app router)", with `throttleMs` to rate-limit — the hook's returned state updates instantly regardless, only the URL write and server round-trip are throttled (default 50 ms; ~340 ms on Safari) [[27]](https://github.com/47ng/nuqs).

That `throttleMs` is your debounce for RSC round-trips. The canonical reference implementation is [shadcn-table](https://github.com/sadmann7/shadcn-table) ⭐ 6.2k — TanStack Table + Next.js with "server-side pagination, sorting, and filtering", Notion-style advanced filters and virtualized infinite scroll [[28]](https://github.com/sadmann7/shadcn-table). AG Grid and MUI X can live inside this too, but their state lives in the grid's own model objects, so you must serialise `sortModel`/`filterModel` into the URL yourself — the URL-state ergonomics favour the headless option.

## Verdict by shape of your server

| Your situation | Pick |
|---|---|
| Flat rows, offset or cursor paging, sort + filter, no grouping | TanStack Table + TanStack Query (`manual*` + `placeholderData: keepPreviousData`) [[1]](https://tanstack.com/table/latest/docs/guide/pagination)[[8]](https://tanstack.com/query/latest/docs/framework/react/guides/paginated-queries) |
| Table state must live in the URL / RSC + App Router | TanStack Table + nuqs; grid-model libraries fight you here [[26]](https://nuqs.dev/docs/server-side)[[28]](https://github.com/sadmann7/shadcn-table) |
| Server-side grouping, pivot, aggregation over millions of rows | AG Grid SSRM (Enterprise) [[12]](https://www.ag-grid.com/react-data-grid/server-side-model/)[[13]](https://www.ag-grid.com/react-data-grid/row-models/) |
| Already on MUI, want server grouping/aggregation without writing the engine | MUI X Data Source, Pro for lazy load, Premium for aggregation [[19]](https://mui.com/x/react-data-grid/server-side-data/lazy-loading/)[[20]](https://mui.com/x/react-data-grid/server-side-data/aggregation/) |
| Mantine design system, simple server paging | Mantine React Table — but it is a TanStack v8 wrapper with a stale release cadence (last tagged release Oct 2023) [[25]](https://github.com/KevinVandy/mantine-react-table); ⚠ no server-side story of its own |
