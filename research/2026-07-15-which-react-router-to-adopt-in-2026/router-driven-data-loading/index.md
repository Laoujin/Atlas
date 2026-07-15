---
title: "Router-driven data loading in React (2026): who owns the cache?"
date: 2026-07-15
depth: survey
format: md
topic: "Router-driven data loading in React (2026): compare React Router v7 loaders/actions, TanStack Router loaders + TanStack Query, and the router-does-no-data approach (TanStack Query / RTK Query + minimal router) for a client-rendered React 19 admin SPA on a REST/OpenAPI backend."
topic_raw: "react dependencies which router to use in 2026"
tags: [react, react-router, tanstack-router, tanstack-query, rtk-query, data-loading, spa]
summary: "For a CSR-only admin SPA on a REST/OpenAPI backend, let a query library own the cache and keep the router thin — framework loaders only pay off with SSR."
citations: 12
reading_time_min: 7
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 232
issue: 8
---

> **Decision.** For a **client-rendered** React 19 admin console on a REST/OpenAPI backend, make a **query library own fetching/caching/invalidation** and keep the router thin. Framework-style `loader`/`clientLoader` route data only pays for itself with SSR/streaming, which a pure SPA doesn't have [[6]](https://github.com/remix-run/react-router/discussions/14037). Concretely: **RTK Query if you want OpenAPI codegen** and/or already run Redux [[10]](https://www.npmjs.com/package/@rtk-query/codegen-openapi); **TanStack Query** if you want the lighter footprint and best-in-class cache [[9]](https://theroadtoenterprise.com/blog/rtk-query-vs-tanstack-query). Pick the router for its *routing* (type safety, DX), not its data layer — and if it's [TanStack Router](https://github.com/TanStack/router) ⭐ 15k (Jul 2026), use loaders only to **prime the query cache**, with the router's own cache turned off [[3]](https://tkdodo.eu/blog/tan-stack-router-and-query).

## The three models

**A — Router owns the data (React Router v7 framework mode).** Routes export `loader`/`clientLoader` (and `action`); React Router fetches before the component renders, serializes the result, and hands it to the route via `useLoaderData`/`loaderData`. Mutations go through `action` + `<Form>`, after which the router **auto-revalidates every loader on the page** [[1]](https://reactrouter.com/start/framework/data-loading). The router *is* the cache.

**B — Router primes an external cache (TanStack Router + TanStack Query).** The `QueryClient` lives in router context; the `loader` calls `queryClient.ensureQueryData`/`prefetchQuery` to start the fetch early, then the component reads it with `useSuspenseQuery`. TanStack Query owns caching, dedup, and invalidation; the router only kicks fetches off in parallel and gates the Suspense boundary [[5]](https://master.dev/blog/tanstack-router-data-loading-2/)[[3]](https://tkdodo.eu/blog/tan-stack-router-and-query).

**C — Router does no data (query library + minimal router).** [Wouter](https://github.com/molefrog/wouter) ⭐ 7.9k (Jul 2026) or plain `react-router` in declarative mode just maps URL → component. All fetching/caching/mutations belong to [TanStack Query](https://github.com/TanStack/query) ⭐ 50k or RTK Query. No loaders, no route-level data contract — components request what they need.

## Who owns what

| Concern | A · [React Router](https://github.com/remix-run/react-router) ⭐ 56k loaders | B · TanStack Router + Query | C · Query lib + thin router |
|---|---|---|---|
| Fetch trigger | Route match, before render [[1]](https://reactrouter.com/start/framework/data-loading) | Loader primes, component reads [[3]](https://tkdodo.eu/blog/tan-stack-router-and-query) | Component (hook) mount |
| Cache owner | The router | TanStack Query [[3]](https://tkdodo.eu/blog/tan-stack-router-and-query) | Query lib |
| Cross-route sharing | ✗ per-route only | ✓ shared query cache | ✓ shared query cache |
| Invalidation | Auto-revalidate all loaders on mutation [[1]](https://reactrouter.com/start/framework/data-loading) | `queryClient.invalidateQueries` / tags | Tags (RTK) / keys (TSQ) |
| OpenAPI codegen | ✗ hand-wired | community (orval/openapi) | RTK Query official ✓ [[10]](https://www.npmjs.com/package/@rtk-query/codegen-openapi) |
| Pays off mainly with | SSR/streaming | either, best with SSR | CSR SPA |
| Router stars | ⭐ 56k | ⭐ 15k | ⭐ 7.9k (wouter) |

## Loaders vs a query cache: the duplication trap

The core tension in model B is that **loaders and a query cache both want to be the source of truth**. TanStack's own guidance is unambiguous: *"when using external caching libraries like TanStack Query, it's best to just turn this off completely because we'd only want one player to control caching"* — set `defaultPreloadStaleTime: 0` so the router never caches [[3]](https://tkdodo.eu/blog/tan-stack-router-and-query). TanStack Router's built-in cache is fine for *"apps that share little data between routes"* but has *"no shared caching/deduping between routes"* and *"no built-in mutation APIs"* [[2]](https://tanstack.com/router/latest/docs/framework/react/guide/data-loading) — exactly the things a data-heavy admin app needs, so you delegate them to Query.

The mental model that avoids duplication: *"Treat the loader like a simple fire-and-forget event handler that only primes our cache without actually returning any data"* — don't `await` in the loader and don't read `useLoaderData`; read via `useSuspenseQuery` so the query is "active" and eligible for GC/refetch [[3]](https://tkdodo.eu/blog/tan-stack-router-and-query). Because Query dedupes in-flight requests, `prefetchQuery` in the loader and `useSuspenseQuery` in the component latch onto **one** network request, not two [[5]](https://master.dev/blog/tanstack-router-data-loading-2/).

Trying to run **both** React Router *framework* loaders **and** TanStack Query in parallel is the anti-pattern. The maintainer read on the "is it good to use both" thread: for **CSR-only** apps, TanStack Query alone works well without framework mode; for SSR, embrace the router's loaders rather than layering Query on top — *"clean integration requires choosing one primary data-fetching strategy rather than running both in parallel"* [[6]](https://github.com/remix-run/react-router/discussions/14037).

## Race conditions & revalidation

**React Router** cancels in-flight loader/fetcher requests on interrupted navigation, mirroring the browser: *"interrupted navigations … will cancel in flight data requests and immediately process the new event"*, and for revalidation it *"will commit all 'fresh' revalidation responses and cancel any stale requests"* [[7]](https://reactrouter.com/explanation/race-conditions). This is a genuine strength — a type-ahead via `fetcher.submit` never shows results for a stale input [[7]](https://reactrouter.com/explanation/race-conditions). Caveats: v7 made loaders **re-run by default** after mutations, so you must add `shouldRevalidate` to stop unwanted refetches [[12]](https://programmingarehard.com/2026/04/11/contributing-to-react-router.html/), and fetcher revalidation still has documented race edge-cases [[8]](https://github.com/remix-run/react-router/issues/10473). Backend integrity is explicitly out of scope — cancelled requests may still hit your server [[7]](https://reactrouter.com/explanation/race-conditions).

**TanStack Query** handles the same race class structurally: keys identify data, in-flight requests dedupe, stale responses are ignored, and mutation → `invalidateQueries` (TSQ) or tag invalidation (RTK Query) is explicit and cross-route [[3]](https://tkdodo.eu/blog/tan-stack-router-and-query)[[9]](https://theroadtoenterprise.com/blog/rtk-query-vs-tanstack-query). For an admin panel, RTK Query's tag system is notably ergonomic: update a user → every query tagged with that user refetches automatically [[9]](https://theroadtoenterprise.com/blog/rtk-query-vs-tanstack-query).

## Suspense & streaming

Loader-based streaming (deferred data + `Await`, or router pending components feeding React Suspense) is a **server-rendering** feature — its value is flushing HTML while data resolves. TanStack Router's Query integration exists largely to *"automate SSR dehydration/hydration and streaming"* [[4]](https://tanstack.com/router/latest/docs/integrations/query). In a **CSR SPA there is no HTML stream**, so this benefit evaporates; you're left with client Suspense boundaries, which `useSuspenseQuery` gives you without any router loader at all [[3]](https://tkdodo.eu/blog/tan-stack-router-and-query). Waterfalls in model B are avoided by not suspending in the loader and using `useDeferredValue` to keep old UI while new data loads [[5]](https://master.dev/blog/tanstack-router-data-loading-2/).

## Recommendation for a data-heavy CSR admin SPA

1. **Query library owns the data.** On a REST/OpenAPI backend, choose **RTK Query if OpenAPI codegen matters** (official generator → fully-typed endpoints and tag invalidation) [[10]](https://www.npmjs.com/package/@rtk-query/codegen-openapi)[[9]](https://theroadtoenterprise.com/blog/rtk-query-vs-tanstack-query), else **TanStack Query** for the lighter, framework-agnostic footprint and the strongest cache [[9]](https://theroadtoenterprise.com/blog/rtk-query-vs-tanstack-query). Both command large 2026 adoption (Query ~12M weekly npm downloads) [[11]](https://byteiota.com/tanstack-2026-full-stack-revolution-with-query-router/).
2. **Don't adopt React Router *framework* loaders for a pure SPA.** With no SSR, `loader`/`clientLoader` add a second cache and a route-data contract with no streaming payoff, and v7's default revalidation becomes tuning overhead [[6]](https://github.com/remix-run/react-router/discussions/14037)[[12]](https://programmingarehard.com/2026/04/11/contributing-to-react-router.html/).
3. **Router chosen for routing, not data.** TanStack Router ⭐ 15k gives type-safe params/search you can feed straight into query keys; if you use its loaders, use them *only* to `ensureQueryData` (prime the cache) with `defaultPreloadStaleTime: 0` and read via `useSuspenseQuery` — never `useLoaderData` for the payload [[3]](https://tkdodo.eu/blog/tan-stack-router-and-query). A minimal router (wouter ⭐ 7.9k) is a fine model-C choice if you don't need loader-level prefetch.

Net: one cache, owned by the query layer; the router routes. That is the lowest-friction, lowest-duplication data-loading strategy for a client-rendered React 19 admin console.
