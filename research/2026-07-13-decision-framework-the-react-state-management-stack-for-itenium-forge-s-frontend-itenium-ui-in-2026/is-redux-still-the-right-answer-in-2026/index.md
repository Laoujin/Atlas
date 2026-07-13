---
title: "Is Redux still the right answer for a new React 19 app in 2026?"
date: 2026-07-13
depth: standard
format: md
topic: "Is Redux still the right answer for a new React 19 app in 2026? Assess Redux Toolkit (and RTK Query): current maintenance health, adoption/usage trend, what the maintainers themselves now recommend, and — concretely — the cases where Redux still genuinely wins versus where it is cargo-cult overhead."
topic_raw: "Is Redux still the right answer for a new React 19 app in 2026? Assess Redux Toolkit (and RTK Query): current maintenance health, adoption/usage trend, what the maintainers themselves now recommend, and — concretely — the cases where Redux still genuinely wins versus where it is cargo-cult overhead."
tags: [react, redux, state-management, redux-toolkit, rtk-query, tanstack-query, zustand, react-19, frontend-architecture]
summary: "Redux is healthy but no longer the default: for a greenfield React 19 SPA talking to a REST API, TanStack Query plus a small Zustand store wins, and Redux's classic moats — devtools, time-travel, testable reducers — no longer belong to Redux alone."
citations: 32
reading_time_min: 11
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 535
issue: 2
---

> **Decision.** For `itenium-ui` — greenfield, React 19 + Vite SPA, REST/OpenAPI backend, no legacy store — **do not use Redux.** Take **TanStack Query** for server state [[31]](https://tanstack.com/query/latest/docs/framework/react/guides/does-this-replace-client-state) plus a small **Zustand** store for the client-state residue [[23]](https://github.com/pmndrs/zustand). Redux is *not* dying (23.6M weekly npm downloads, shipping releases [[2]](https://api.npmjs.org/downloads/point/last-week/@reduxjs/toolkit) [[8]](https://github.com/reduxjs/redux-toolkit/releases)) — but Redux's own FAQ tells you to "*not use Redux until you have problems with vanilla React*" [[1]](https://redux.js.org/faq/general), and an admin UI over a REST API does not have those problems. Reach for Redux only if you hit one of the five shapes in the *When Redux still wins* table below.

## The honest state of Redux in 2026

Redux is not abandonware and the "Redux is dead" genre is wrong. It is *shrinking in share*, which is a different thing.

| Signal | Reading | Verdict |
|---|---|---|
| Maintenance | `@reduxjs/toolkit` v2.9 (Sep 2025) → v2.10/v2.11 (Nov–Dec 2025) → **v2.12.0 (May 2026)** [[8]](https://github.com/reduxjs/redux-toolkit/releases) | ✓ Alive, ~quarterly minors, slowing |
| Who's behind it | Mark Erikson dominates the commit graph (1437 commits vs 924 / 447 / 346 for the next three) [[9]](https://github.com/reduxjs/redux-toolkit/graphs/contributors) | ⚠ Real bus-factor concentration |
| npm, weekly | RTK **23.6M** [[2]](https://api.npmjs.org/downloads/point/last-week/@reduxjs/toolkit) · Zustand **36.7M** [[3]](https://api.npmjs.org/downloads/point/last-week/zustand) · TanStack Query **61.2M** [[4]](https://api.npmjs.org/downloads/point/last-week/@tanstack/react-query) | ✗ Overtaken on both axes |
| Growth, Jun 2023 → Jun 2026 (monthly) | RTK 11.0M → 92.3M (**8.4×**) · Zustand 7.6M → 173.3M (**22.9×**) · TanStack Query 7.1M → 242.6M (**34.3×**) [[5]](https://npmtrends.com/@reduxjs/toolkit-vs-jotai-vs-mobx-vs-recoil-vs-redux-vs-zustand) | → Redux grows; the alternatives grow ~3–4× faster |
| Survey (State of React, 2023→2025) | Redux 80.5% → 75.5%; **Redux Toolkit flat at ~54%**; Zustand 28% → 50%; Jotai 13% → 19% [[7]](https://saschb2b.com/blog/react-state-management-2026) [[6]](https://2025.stateofreact.com/en-US/libraries/state-management/) | ✗ Flat is the tell — RTK stopped recruiting |
| GitHub | [redux-toolkit](https://github.com/reduxjs/redux-toolkit) ⭐ 11.2k · [zustand](https://github.com/pmndrs/zustand) ⭐ 59k · [TanStack/query](https://github.com/TanStack/query) ⭐ 50k · [jotai](https://github.com/pmndrs/jotai) ⭐ 21k (Jul 2026) [[30]](https://github.com/pmndrs/jotai) | — |

Zustand crossed Redux Toolkit on downloads during 2024–25 and the gap has widened since [[5]](https://npmtrends.com/@reduxjs/toolkit-vs-jotai-vs-mobx-vs-recoil-vs-redux-vs-zustand). The State of React 2025 flatline on RTK is the sharper signal: RTK is not losing its installed base, it is failing to win *new* projects [[6]](https://2025.stateofreact.com/en-US/libraries/state-management/). RTK Query's own 2.x/3.x roadmap remains an open maintainer-driven discussion thread rather than a shipped plan [[28]](https://github.com/reduxjs/redux-toolkit/discussions/4107) ⭐ 11.2k — the project is in maintenance-plus-increments mode, not expansion.

## What the maintainers themselves say

Two separate statements, routinely conflated:

- **"Use RTK, not hand-rolled Redux."** — "If you are writing *any* Redux logic today, you *should* be using Redux Toolkit" [[11]](https://redux.js.org/introduction/why-rtk-is-redux-today). This is a *how*, not a *whether*.
- **"You may well not need Redux at all."** — the official FAQ is blunt: "Not all apps need Redux... It's not designed to be the shortest or fastest way to write code. There are more concepts to learn, and more code to write. It also adds some indirection... a trade-off between short term and long term productivity." It then quotes Dan Abramov: *"don't use Redux until you have problems with vanilla React."* [[1]](https://redux.js.org/faq/general)

Redux's official list of when it *is* useful [[1]](https://redux.js.org/faq/general): large amounts of state needed in many places; state updated frequently; complex update logic; medium/large codebase worked on by many people; you need to see how state changed over time. Score `itenium-ui` (an admin console + a file-management app over a REST API) against that list honestly — it hits roughly none of them. Almost all of its "state" is a cache of server data, which is not what Redux is for.

## The boilerplate reality, post-RTK

RTK's own stated purpose is to fix "store setup is too complicated", "too many packages", "too much boilerplate" [[10]](https://redux-toolkit.js.org/introduction/getting-started). It genuinely did: `createSlice` killed action-type constants, the switch statement, and manual immutable spreading (Immer does it). Nobody writing RTK in 2026 is writing 2017 Redux.

But "less boilerplate than 2017 Redux" is not "no boilerplate". A minimal RTK setup is still: `configureStore` + `<Provider>` + typed `useAppDispatch`/`useAppSelector` hooks + one slice file per concern; add RTK Query and you also owe a `createApi` slice, a `baseQuery`, tag types, and store-middleware wiring. Zustand's equivalent is one `create()` call and no provider [[23]](https://github.com/pmndrs/zustand). Bundle cost tracks the ceremony: ~12 KB gzip for RTK vs ~1.2 KB for Zustand [[7]](https://saschb2b.com/blog/react-state-management-2026) — irrelevant on its own, but it is a fair proxy for how much machinery you are opting into.

For a .NET architect the framing that lands: **Redux is MediatR + an event log for the browser.** Every mutation is a named, serialisable command flowing through one dispatcher, with middleware as the pipeline. That is genuinely valuable — when you have the problem it solves. Applying it to "fetch a list of users and show it in a table" is CQRS on a CRUD form.

## The three moats that turned out not to be moats

**1. DevTools / time-travel.** This was Redux's best differentiator and it is gone. Zustand's `devtools` middleware plugs straight into the same Redux DevTools Extension: "lets you use Redux DevTools Extension without Redux and **enables time-travel debugging** of your store" [[15]](https://zustand.docs.pmnd.rs/reference/middlewares/devtools). [Redux DevTools](https://github.com/reduxjs/redux-devtools) ⭐ 14k (Jul 2026) is a separate project that Redux no longer has exclusive rights to [[27]](https://github.com/reduxjs/redux-devtools). You get named actions and a state timeline in Zustand for one extra middleware wrap. (Caveat: Redux's *action log* is richer by construction, because in Redux *everything* is an action; in Zustand you only see what you chose to name.)

**2. "Pure reducers are ideal for TDD."** Redux's own testing guide undercuts this. It says: "**Prefer writing integration tests with everything working together**... *If* needed, use basic unit tests for pure functions such as particularly complex reducers or selectors. However, in many cases, these are just implementation details that are covered by integration tests instead," and flatly, "the Redux code can be treated as an **implementation detail** of the app, without requiring explicit tests for the Redux code in many circumstances" [[16]](https://redux.js.org/usage/writing-tests). The recommended Redux test is: render the component tree with a real store and mock the network — which is *exactly* the test you would write for a Zustand store with Testing Library. A TDD mandate is not an argument for Redux.

**3. RTK Query as the data layer.** The official comparison page positions RTK Query for people who *already* pay for a Redux store ("already use Redux", "need Redux DevTools integration", "integration with the broader Redux ecosystem"), and openly concedes it "deliberately does **not** implement a cache that would deduplicate identical items" — normalisation is out of scope [[12]](https://redux-toolkit.js.org/rtk-query/comparison). RTK Query is an excellent reason to keep Redux if Redux is already there. It is a bad reason to *introduce* Redux — you would be adopting a store you don't need in order to get a cache you can have standalone. TanStack Query is the same job with 2.6× the downloads [[4]](https://api.npmjs.org/downloads/point/last-week/@tanstack/react-query) and no store tax.

## What React 19 actually took away — and what it didn't

Be precise here, because most blog posts are not.

| React 19 feature | Redux remit it erodes | Applies to a Vite SPA? |
|---|---|---|
| **Actions + `useActionState`** | pending flags, error state, form-submit thunks [[13]](https://react.dev/blog/2024/12/05/react-19) | ✓ Yes (client-only React 19) |
| **`useOptimistic`** | optimistic-update middleware + manual rollback; React reverts automatically on error [[14]](https://react.dev/reference/react/useOptimistic) [[13]](https://react.dev/blog/2024/12/05/react-19) | ✓ Yes |
| **`use()`** | reading a promise in render, with Suspense | ⚠ Yes, *but* it needs a cache to suspend against — React ships none for a client SPA. TanStack Query is that cache. |
| **Server Components / Server Actions** | the whole server-state layer | ✗ **No.** RSC needs a supporting framework/bundler [[13]](https://react.dev/blog/2024/12/05/react-19); an Nx + Vite SPA has none. |

So the popular "React 19 killed Redux" argument only *half* applies to `itenium-ui`. The mutation-side ergonomics (Actions, `useOptimistic`) are yours for free and delete the single most common reason people historically wrote thunks. The RSC half does not apply at all — which is precisely why you still need a real server-state library, and why the answer is TanStack Query rather than "React 19 handles it". TanStack Query's own docs make the boundary explicit: it is "a **server-state** library... **not a replacement for local/client state management**", and after adopting it "most of your once seemingly global state really wasn't global at all" [[31]](https://tanstack.com/query/latest/docs/framework/react/guides/does-this-replace-client-state). Practitioner estimates put server-state at 60–80% of the Redux code in a typical data-driven app [[26]](https://theroadtoenterprise.com/blog/rtk-query-vs-tanstack-query) — delete that, and what's left rarely justifies a store.

## When Redux still genuinely wins

Not nostalgia — these are real. Each row is a bar Redux must clear that lighter tools cannot.

| Shape | Why Redux actually wins | Does `itenium-ui` have it? |
|---|---|---|
| **Undo/redo over a large state tree** | The action log *is* the undo stack. [redux-undo](https://github.com/omnidan/redux-undo) ⭐ 2.9k wraps a reducer and you get undo/redo for free [[19]](https://github.com/omnidan/redux-undo). Retrofitting this onto a mutable store is a rewrite. Design tools, canvas/diagram editors, spreadsheet-likes. | ✗ |
| **Complex cross-cutting client state with many writers** | The question "when did this slice change and where did the data come from" is the one Redux was built to answer [[32]](https://redux.js.org/introduction/getting-started) [[1]](https://redux.js.org/faq/general). Collaborative editors, trading/ops dashboards, multi-step wizards whose steps mutate each other. | ✗ |
| **Logic that must run outside React** | Listener middleware / sagas react to *actions*, not components — WebSocket push, background sync, cross-cutting analytics, offline queues. Officially cited as an RTK Query advantage too [[12]](https://redux-toolkit.js.org/rtk-query/comparison). | ✗ (unless file-management grows push/upload-queue semantics — then reconsider) |
| **Heavy derived state** | Reselect's `createSelector` with a minimal store and everything else computed [[17]](https://redux.js.org/usage/deriving-data-selectors) [[18]](https://github.com/reduxjs/reselect) ⭐ 19k. ⚠ Weak moat: Reselect works fine *outside* Redux, and `useMemo` covers most cases. | ✗ |
| **Large teams needing enforced conventions** | The official [Style Guide](https://redux.js.org/style-guide/) plus `createSlice` gives you one lint-able, reviewable way to mutate state [[25]](https://redux.js.org/style-guide/). Genuinely worth it at 10+ devs on one app. | ✗ (small team, opinionated owner — you *are* the convention) |
| **Session replay / bug repro from a serialised action log** | Ship the action list from a user's session, replay it, reproduce the bug. Nothing else does this as cleanly. | ✗ |

If a future Forge frontend is an editor rather than an admin console, revisit this. Redux is the right tool for editors.

## The OpenAPI codegen question — the one real point in Redux's favour

Itenium.Forge exposes Swagger/OpenAPI, so typed-client generation is on the table, and RTK Query has a genuine first-party answer: `@rtk-query/codegen-openapi` generates a fully typed API slice with hooks straight from the schema [[20]](https://redux-toolkit.js.org/rtk-query/usage/code-generation). That is a real advantage — and it evaporates on inspection, because the non-Redux side has the same thing:

| Generator | Output | Stars |
|---|---|---|
| `@rtk-query/codegen-openapi` | typed RTK Query API slice + hooks [[20]](https://redux-toolkit.js.org/rtk-query/usage/code-generation) | (in [redux-toolkit](https://github.com/reduxjs/redux-toolkit) ⭐ 11.2k) |
| [Orval](https://github.com/orval-labs/orval) | typed **TanStack Query hooks** + MSW mocks out of the box [[21]](https://github.com/orval-labs/orval) | ⭐ 6.2k |
| [Hey API](https://github.com/hey-api/openapi-ts) | typed client + TanStack Query plugin; lighter, plugin-based [[22]](https://github.com/hey-api/openapi-ts) | ⭐ 5.1k |

Orval's built-in MSW mock generation is a direct hit on a TDD mandate: generated mocks from the same schema that generates the client. That is a *better* TDD story than RTK's codegen, not a worse one.

## Recommended stack for `itenium-ui`

1. **Server state → [TanStack Query](https://tanstack.com/query)** [[24]](https://github.com/TanStack/query) ⭐ 50k. Caching, dedup, retries, invalidation, `use()`-friendly suspense. This eats 60–80% of what people used Redux for [[26]](https://theroadtoenterprise.com/blog/rtk-query-vs-tanstack-query).
2. **Typed client → Orval or Hey API** against the Forge OpenAPI spec [[21]](https://github.com/orval-labs/orval) [[22]](https://github.com/hey-api/openapi-ts). Orval if you want the generated MSW mocks for Jest/Testing Library.
3. **Client state → [Zustand](https://github.com/pmndrs/zustand)** ⭐ 59k [[23]](https://github.com/pmndrs/zustand), with the `devtools` middleware on from day one so you keep the action timeline and time-travel [[15]](https://zustand.docs.pmnd.rs/reference/middlewares/devtools). Expect this store to be small — theme, sidebar, selection, upload queue. If it stays that small, `useState` + context may even be enough.
4. **Mutations → React 19 Actions + `useOptimistic`**, not thunks [[13]](https://react.dev/blog/2024/12/05/react-19) [[14]](https://react.dev/reference/react/useOptimistic). Pair with `react-hook-form` (as the `shadcn-admin` sibling does) and TanStack Query's `useMutation` for invalidation.
5. **Escape hatch:** if the client store ever grows past ~a dozen interdependent slices with complex update rules, Zustand ships a `redux`-style middleware — you can adopt reducer/action discipline without adopting Redux. And Reselect works standalone if derived state gets heavy [[18]](https://github.com/reduxjs/reselect).

Community sentiment matches: "Redux isn't dead, but in 2026, maybe we shouldn't be using it without thinking, like opening jQuery to create a dropdown" [[29]](https://medium.com/@mernstackdevbykevin/react-in-2026-do-you-still-need-redux-af7085e742ac).

## The one caveat worth naming

Choosing against Redux means choosing a stack whose pieces are maintained by small teams too — Zustand and Jotai are both `pmndrs`, TanStack is Tanner Linsley's org. You are not trading a bus-factor-of-one [[9]](https://github.com/reduxjs/redux-toolkit/graphs/contributors) for a bus-factor-of-many; you are trading it for a *different* small team with steeper adoption momentum. What you *do* buy is exit cost: a Zustand store is a plain hook and a few hundred lines. Ripping out Redux is a project. Ripping out Zustand is an afternoon. For a greenfield pick with genuine uncertainty about where the app lands, that asymmetry is the deciding argument.
