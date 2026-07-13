---
title: "The router is a state manager: TanStack Router for itenium-ui"
date: 2026-07-13
depth: ceo
format: md
topic: "Decide the router for a React 19 + Vite client-side SPA in 2026 — TanStack Router vs React Router 7 (framework vs declarative mode) vs Wouter — and explain how the router choice CONSTRAINS the state-management choice more than people expect. Cover: type-safe routes and params, typed search-params-as-state (the router as the store for filters/sorting/pagination — a large slice of an admin app's \"state\" that most people wrongly put in Redux), route loaders vs a query cache (do they compete or compose?), TanStack Router's first-class TanStack Query integration, code-splitting, auth-guarded routes / beforeLoad, file-based vs code-based routing in an Nx monorepo, SSR-neutrality (this is a pure SPA, no Next.js), bundle size, maintenance health and GitHub stars. Deliver a one-page decision: which router, and what state it should own that would otherwise leak into a global store."
topic_raw: "Decide the router for a React 19 + Vite client-side SPA in 2026 — TanStack Router vs React Router 7 (framework vs declarative mode) vs Wouter — and explain how the router choice CONSTRAINS the state-management choice more than people expect. Cover: type-safe routes and params, typed search-params-as-state (the router as the store for filters/sorting/pagination — a large slice of an admin app's \"state\" that most people wrongly put in Redux), route loaders vs a query cache (do they compete or compose?), TanStack Router's first-class TanStack Query integration, code-splitting, auth-guarded routes / beforeLoad, file-based vs code-based routing in an Nx monorepo, SSR-neutrality (this is a pure SPA, no Next.js), bundle size, maintenance health and GitHub stars. Deliver a one-page decision: which router, and what state it should own that would otherwise leak into a global store."
tags: [react, routing, tanstack-router, react-router, state-management, spa, vite, nx]
summary: "For itenium-ui — a greenfield React 19 + Vite SPA with no SSR — pick TanStack Router: it is the only option that makes filters/sort/pagination typed URL state instead of Redux slices, and it composes with TanStack Query rather than competing."
citations: 16
reading_time_min: 3
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 245
issue: 2
---

> **Decision — use [TanStack Router](https://tanstack.com/router/latest) ⭐ 15k (Jul 2026)** [[8]](https://github.com/TanStack/router), file-based routing, `autoCodeSplitting`, with TanStack Query underneath. It is the only one of the three that treats **search params as validated, typed, first-class state** [[1]](https://tanstack.com/blog/search-params-are-state)[[2]](https://tanstack.com/router/latest/docs/framework/react/guide/search-params) — which deletes the single largest fake use-case for a global store in an admin app. React Router v8 ⭐ 56k [[9]](https://github.com/remix-run/react-router) is the safe, boring default [[12]](https://www.pkgpulse.com/guides/react-router-v7-vs-tanstack-router-2026) but is built around a server you do not have; Wouter ⭐ 7.9k [[10]](https://github.com/molefrog/wouter) is a 2.6 kB `<Link>`/`<Route>` primitive that owns no state at all — for a role-guarded admin app it is under-powered.

## The constraint nobody prices in

An admin app's "global state" is mostly **filters, sort, page, page-size, selected row, view mode, date range**. Put those in Redux/Zustand and you get: not shareable, not bookmarkable, lost on refresh, back-button broken, and a second source of truth to sync with the URL. TanStack Router's position — routes declare a Zod/Valibot schema for their search params, and every `<Link>`/`navigate()` writing them is type-checked against it, with JSON-serializable nested objects and arrays, not just flat strings [[1]](https://tanstack.com/blog/search-params-are-state)[[2]](https://tanstack.com/router/latest/docs/framework/react/guide/search-params). Components subscribe with `useSearch` and re-render only on the params they read.

**Net effect on the state stack:** server state → TanStack Query; URL/filter state → the router; genuinely global client state → a small Zustand store (theme, sidebar, command palette). There is nothing left for Redux [[11]](https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state). React Router's declarative mode hands you raw `useSearchParams` (untyped strings) — the filter schema then has to live *somewhere*, and it drifts into a store.

## Loaders vs the query cache: compose, don't compete

They compose. The route `loader` calls `queryClient.ensureQueryData()`; the component reads the same cache with `useSuspenseQuery()`. Router coordinates *when* to fetch, Query owns caching/invalidation/refetch — the router is explicitly designed as "a perfect coordinator for external data fetching and caching libraries" [[3]](https://tanstack.com/router/latest/docs/framework/react/guide/external-data-loading). Typed search params are the query key. That is the whole point: **the URL is the query key is the state.**

## Scorecard

| | TanStack Router ⭐ 15k | React Router v8 ⭐ 56k | Wouter ⭐ 7.9k |
|---|---|---|---|
| Typed params **and** search params | ✓ end-to-end, schema-validated [[2]](https://tanstack.com/router/latest/docs/framework/react/guide/search-params) | params typed in framework mode via typegen; search params raw [[6]](https://reactrouter.com/start/modes) | ✗ |
| Search params as a store | ✓ core feature [[1]](https://tanstack.com/blog/search-params-are-state) | ✗ roll your own | ✗ |
| Loaders without a server | ✓ client-first [[3]](https://tanstack.com/router/latest/docs/framework/react/guide/external-data-loading) | data/framework mode only; declarative mode has no `loader` [[6]](https://reactrouter.com/start/modes) | ✗ |
| Auth guard | ✓ `beforeLoad` + router `context`, `throw redirect()`, parent guards whole subtree [[4]](https://tanstack.com/router/latest/docs/framework/react/guide/authenticated-routes) | loader-based redirect | manual |
| Code-splitting | ✓ `autoCodeSplitting` splits critical vs non-critical automatically [[5]](https://tanstack.com/router/latest/docs/framework/react/guide/code-splitting) | ✓ framework mode | manual |
| SSR-neutral | ✓ | ✓ but v8 is ESM-only, Vite 7+, framework mode assumes a build server [[7]](https://remix.run/blog/react-router-v8) | ✓ |
| gzip | 39.6 kB [[14]](https://bundlephobia.com/package/@tanstack/react-router) | 59.0 kB [[15]](https://bundlephobia.com/package/react-router) | 2.6 kB [[16]](https://bundlephobia.com/package/wouter) |

⚠ **Caveats.** (1) TanStack's read story is excellent; *writing* search params over time (composable updates, defaults, lifecycle) is still low-level and teams end up building a thin helper layer [[13]](https://github.com/TanStack/router/issues/4973) ⭐ 15k. (2) React Router has 3.8× the stars and shipped v8 in June 2026 with a yearly-major cadence and open governance [[7]](https://remix.run/blog/react-router-v8) — it is not a risky choice, it is a *mismatched* one for a pure SPA with a .NET API.

## Nx fit

Use **file-based routing** per app (`apps/itenium-ui/src/routes/**`), not code-based: `autoCodeSplitting` requires the Vite plugin and is the reason to keep the file convention [[5]](https://tanstack.com/router/latest/docs/framework/react/guide/code-splitting). The generated `routeTree.gen.ts` is per-app, so the two apps stay independent; shared route *fragments* don't belong in `libs/` — shared **components** and **search-param schemas** do. Auth guards live in one `_authenticated` layout route whose `beforeLoad` reads Keycloak roles/capabilities off the JWT in router `context` and `throw redirect()`s [[4]](https://tanstack.com/router/latest/docs/framework/react/guide/authenticated-routes); Forge capability checks are just `context.auth.can(...)` in that one place.

## What the router owns (and Redux therefore does not)

`page`, `pageSize`, `sort`, `sortDir`, `q`, `filters{}`, `dateRange`, `view`, `selectedId`, `tab`, `redirect` (post-login). Each declared once in a route's `validateSearch` schema, each type-checked at every call-site, each free in a shared link.
