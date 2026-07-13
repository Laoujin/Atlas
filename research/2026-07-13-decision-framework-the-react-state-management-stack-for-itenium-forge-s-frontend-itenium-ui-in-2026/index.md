---
layout: expedition
title: "The React state stack for Itenium.Forge in 2026: the Redux question dissolves"
date: 2026-07-13
topic: "Decision framework: the React state-management stack for Itenium.Forge's frontend (itenium-ui) in 2026 — is Redux still the answer, and if not, what replaces it? Greenfield pick for an Nx 21 + React 19 + Vite + Tailwind 4 monorepo consuming .NET 10 REST APIs (ProblemDetails, Swagger, JWT via Keycloak/OpenIddict)."
topic_raw: "React Redux in 2026 what should I use for Itenium.Forge? C:\\Users\\woute\\Dropbox\\Personal\\Programming\\UnixCode\\projects\\Itenium.Forge\\Itenium.Forge.Core"
format: md
tags: [react, state-management, frontend-architecture, tanstack, dotnet]
summary: "Six angles independently converge: don't introduce Redux — generate the client from Forge's OpenAPI, let TanStack Query own server state, let the router own filter state, and leave one small Zustand store for what remains."
cover: cover.svg
synthesis: true
children:
  - slug: is-redux-still-the-right-answer-in-2026
    title: "Is Redux still the right answer for a new React 19 app in 2026?"
    depth: survey
    status: success
    summary: "Redux is healthy but no longer the default: for a greenfield React 19 SPA talking to a REST API, TanStack Query plus a small Zustand store wins, and Redux's classic moats — devtools, time-travel, testable reducers — no longer belong to Redux alone."
    citations: 32
    reading_time_min: 11
  - slug: server-state-tanstack-query-vs-rtk-query-vs-swr-vs-route-loaders
    title: "Server-state layer for a React 19 + Vite SPA on a .NET API: TanStack Query wins"
    depth: survey
    status: success
    summary: "TanStack Query is the correct server-state layer for itenium-ui; its Register.defaultError hook makes RFC 9457 ProblemDetails a first-class typed error with no per-call generics."
    citations: 32
    reading_time_min: 11
  - slug: client-state-zustand-vs-jotai-vs-redux-toolkit-vs-plain-react
    title: "Client state after the query cache: Zustand vs Jotai vs RTK vs plain React 19"
    depth: survey
    status: success
    summary: "Once TanStack Query owns server state, the residual client state in a CRUD admin is roughly one persisted preferences store — take Zustand's vanilla createStore in a shared Nx lib and skip the rest."
    citations: 27
    reading_time_min: 8
  - slug: typed-api-clients-from-forge-openapi
    title: "Generating the itenium-ui API client from Forge's OpenAPI document"
    depth: survey
    status: success
    summary: "Orval is the pick for itenium-ui: it is the only generator that emits TanStack Query hooks, query keys, MSW mocks and Zod schemas from one config — and generating the client collapses the state-management question to 'server cache + a little client state'."
    citations: 30
    reading_time_min: 8
  - slug: routing-and-where-state-lives
    title: "The router is a state manager: TanStack Router for itenium-ui"
    depth: recon
    status: success
    summary: "For itenium-ui — a greenfield React 19 + Vite SPA with no SSR — pick TanStack Router: it is the only option that makes filters/sort/pagination typed URL state instead of Redux slices, and it composes with TanStack Query rather than competing."
    citations: 16
    reading_time_min: 3
  - slug: auth-and-session-state-against-forge-jwt-and-oidc
    title: "Auth & session state for a React 19 SPA on Forge: kill the localStorage plan"
    depth: recon
    status: success
    summary: "Drop the localStorage JWT plan: use react-oidc-context with an in-memory access token, put roles/capabilities behind a /me query instead of in the token, and treat a .NET BFF as the target end-state."
    citations: 11
    reading_time_min: 3
model: "Opus 4.8"
cost_usd: "sub"
issue: 2
duration_sec: 694
---

> **Decision.** Do not introduce Redux. Generate the API client from Forge's OpenAPI document with **Orval**, let **TanStack Query** own server state, let **TanStack Router** own filter/sort/page state in typed URL search params, and leave **one small Zustand store** for theme, sidebar and column visibility. Redux's official FAQ still says *"don't use Redux until you have problems with vanilla React"* [[1]](https://redux.js.org/faq/general) — an admin console over a REST API does not have those problems.

## The question dissolves when you name the four kinds of state

"Which state manager" is the wrong question, and every angle reached that conclusion independently. Enumerate what `itenium-ui` actually holds and each bucket has an owner that is not a global store:

- **Server data** — nearly all of it. TanStack Query's own docs say that once async code moves into the cache, the truly global client state left over "is usually very tiny", reducing their worked example to `themeMode` and `sidebarStatus` [[2]](https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state).
- **Filters, sort, page, selected row** — the single largest fake use-case for a store. TanStack Router validates search params against a schema and type-checks every `navigate()` against it [[3]](https://tanstack.com/blog/search-params-are-state). Put them in a store instead and you get state that is not shareable, not bookmarkable, lost on refresh, with a broken back button.
- **Session and capabilities** — server state, not client state. `react-oidc-context` already exposes the token as a Context; copying it into a store creates a second copy that goes stale.
- **UI residue** — theme, sidebar, column visibility. One persisted Zustand store, ~12 lines, no Provider.

Redux is not dying — 23.6M weekly downloads and quarterly releases [[4]](https://github.com/reduxjs/redux-toolkit/releases) — but there is no bucket left for it to own. The three moats people still cite have all fallen: Zustand's `devtools` middleware gives time-travel through the same Redux DevTools extension [[5]](https://zustand.docs.pmnd.rs/reference/middlewares/devtools), and Redux's own testing guide calls its store "an **implementation detail** of the app" that in many cases needs no explicit tests [[6]](https://redux.js.org/usage/writing-tests) — so a TDD mandate is not an argument for Redux either.

## The layers compose — that is the actual finding

The pieces are not four independent picks that happen to co-exist. The router's `loader` calls `queryClient.ensureQueryData()` and the component reads the same cache with `useSuspenseQuery()`; the router is explicitly designed as "a perfect coordinator for external data fetching and caching libraries" [[7]](https://tanstack.com/router/latest/docs/framework/react/guide/external-data-loading). The typed search params *are* the query key. And Orval generates the hooks and the key factories from the OpenAPI document, so the layer you would otherwise hand-write mostly ceases to exist [[8]](https://orval.dev/docs/guides/react-query/). One custom mutator makes `ProblemDetails` the error type of every generated hook [[9]](https://orval.dev/docs/guides/custom-axios/), which is the cleanest thing Forge's RFC 7807 discipline buys the frontend.

## Two findings point back at the backend

The frontend decision is not frontend-only. First, the README's own worry — that baking capabilities into the JWT makes tokens too large — resolves by moving them out: keep the JWT to `sub` plus coarse roles and serve fine-grained capabilities from `GET /me`, cached in the query layer, which also buys revocation without re-login. Second, **stay on Swashbuckle for now**: .NET 10's built-in OpenAPI generator emits `anyOf` without a discriminator object for polymorphic types [[10]](https://github.com/dotnet/aspnetcore/issues/57982), and without a discriminator no generator can emit a TypeScript discriminated union.

## What it costs, honestly

Four new dependencies plus a codegen step, three of them from one vendor — that is real concentration risk in the TanStack family, and TanStack Router at 39.6 kB gzip is not free. Orval's generated one-hook-per-endpoint style is also on the wrong side of the ecosystem's drift toward composable `queryOptions` objects, which is the single reason to prefer Hey API instead. The security angle is the least comfortable: in-memory tokens are a damage limiter, not a fix, and the IETF's browser-apps BCP reserves its top-ranked architecture — a backend-for-frontend — for exactly the class of app Forge is built for [[11]](https://www.ietf.org/archive/id/draft-ietf-oauth-browser-based-apps-26.html). The open question this run does not settle: whether to put a .NET BFF in front of `itenium-ui` now, while the frontend is still greenfield and the migration is nearly free, or to ship the pure SPA and pay for it later.

*Two proposed angles — a dedicated pass on testing each candidate, and one on lock-in and migration cost — were offered and left unticked, so they were not researched separately; MSW/Jest coverage appears inside the codegen and client-state angles instead.*
