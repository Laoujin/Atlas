---
title: "Client state after the query cache: Zustand vs Jotai vs RTK vs plain React 19"
date: 2026-07-13
depth: standard
format: md
topic: "Compare client-state (UI state) libraries for a React 19 + Vite + Nx SPA in 2026, on the assumption that server/REST data is already owned by a dedicated query cache: Zustand vs Jotai vs Redux Toolkit vs Valtio vs XState vs plain React (useState/useReducer/Context + React 19's useOptimistic and Actions). The core question is what is actually LEFT to manage once server state is handled — and whether a client-state library is needed at all."
topic_raw: "Compare client-state (UI state) libraries for a React 19 + Vite + Nx SPA in 2026, on the assumption that server/REST data is already owned by a dedicated query cache: Zustand vs Jotai vs Redux Toolkit vs Valtio vs XState vs plain React (useState/useReducer/Context + React 19's useOptimistic and Actions). The core question is what is actually LEFT to manage once server state is handled — and whether a client-state library is needed at all."
tags: [react, state-management, zustand, jotai, redux-toolkit, nx, typescript, testing]
summary: "Once TanStack Query owns server state, the residual client state in a CRUD admin is roughly one persisted preferences store — take Zustand's vanilla createStore in a shared Nx lib and skip the rest."
citations: 27
reading_time_min: 8
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 442
issue: 2
---

> **Decision.** Once a query cache owns server data, the leftover global client state in a CRUD admin is *one* persisted preferences object [[1]](https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state) — theme, sidebar, column visibility. Take **[Zustand](https://zustand.docs.pmnd.rs) ⭐ 59k (Jul 2026)** [[4]](https://github.com/pmndrs/zustand), specifically `createStore` from `zustand/vanilla` in a shared `libs/state` lib: a plain object with no React import, no Provider, no context to leak across Nx boundaries, and unit-testable in Jest without rendering anything [[12]](https://zustand.docs.pmnd.rs/learn/guides/testing). Everything else — wizard drafts, toasts, auth session, feature flags — is *not* global state and should not go in the store. **Redux Toolkit** ⭐ 11k [[6]](https://github.com/reduxjs/redux-toolkit) buys time-travel devtools you will not need at this size; **Jotai** ⭐ 21k [[5]](https://github.com/pmndrs/jotai) is the credible runner-up if you later find yourself fighting selector granularity.

## 1. What is actually left

TanStack Query's own docs are blunt: after migrating async code, "the truly globally accessible client state that is left over ... is usually very tiny" — their worked example reduces a global store to `themeMode` and `sidebarStatus` [[1]](https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state). React 19 then removes another chunk: `useActionState` + `useOptimistic` absorb pending/error/rollback state for form-shaped mutations, which in a CRUD admin is most mutations [[9]](https://react.dev/blog/2024/12/05/react-19).

Mapping the seven candidates you listed against the lightest tool that actually handles them:

| Client state | Really global? | Lightest tool that handles it | Why |
|---|---|---|---|
| Theme (light/dark/system) | ✓ | **Zustand persisted store** | Cross-app, must survive reload → `persist` + `localStorage` [[14]](https://zustand.docs.pmnd.rs/reference/middlewares/persist) |
| Sidebar collapse | ✓ | **Same store** | Read by shell + a few pages; TanStack's own canonical example [[1]](https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state) |
| Table column visibility | ✓ (persisted) | **Same store**, keyed by table id | Per-user preference, survives reload. ⚠ Column *filters/sort/page* belong in the URL, not the store → [nuqs](https://nuqs.dev) ⭐ 11k [[22]](https://nuqs.dev/) [[23]](https://github.com/47ng/nuqs) |
| Multi-step wizard draft | ✗ | **`useReducer` in the wizard route** (+ `persist` only if drafts must survive reload) | Lifecycle = the wizard's. Global store → you own a reset-on-unmount bug forever |
| Toasts | ✗ | **Toast library's own imperative API** (sonner / shadcn `useToast`) | Already an external store behind the scenes; a second one is duplication |
| Auth session | ✗ | **Query cache** (`useQuery(['me'])`) + token in the OIDC client | It's server state. Keycloak/OpenIddict issues it, the server invalidates it. ⚠ The one exception: an `isAuthenticated` boolean the router guards on — that can live in the store |
| Feature flags | ✗ | **Query cache** (fetched) or Vite `import.meta.env` (build-time) | Server-owned or compile-time constant, never mutated by the UI |

Net: **one store, three fields, one middleware.** That is the entire client-state surface of an admin app in 2026. Any library evaluation that ignores this scoping will over-buy.

## 2. Scorecard

| | Boilerplate / store | TS inference | Bundle (gz) | Devtools | Re-render model | Jest w/o React | localStorage | ⭐ Stars |
|---|---|---|---|---|---|---|---|---|
| **[Zustand](https://zustand.docs.pmnd.rs)** 5.0 | ~12 lines, no Provider [[25]](https://dev.to/jsgurujobs/state-management-in-2026-zustand-vs-jotai-vs-redux-toolkit-vs-signals-2gge) | Good; needs `create<T>()(...)` curried form | **1.2 KB** [[3]](https://saschb2b.com/blog/react-state-management-2026) | Redux DevTools via `devtools` middleware (time-travel works) | Manual selectors; ⚠ `useShallow` mandatory for object selectors [[15]](https://zustand.docs.pmnd.rs/reference/migrations/migrating-to-v5) | ✓ `createStore().getState()` — zero React [[12]](https://zustand.docs.pmnd.rs/learn/guides/testing) | ✓ `persist` + `partialize` + `migrate` [[14]](https://zustand.docs.pmnd.rs/reference/middlewares/persist) | ⭐ 59k [[4]](https://github.com/pmndrs/zustand) |
| **[Jotai](https://jotai.org)** 2.20 | ~1 line per atom | Best of the group — derived atoms infer [[25]](https://dev.to/jsgurujobs/state-management-in-2026-zustand-vs-jotai-vs-redux-toolkit-vs-signals-2gge) | 3.5 KB [[3]](https://saschb2b.com/blog/react-state-management-2026) | `jotai-devtools` (separate pkg) | Automatic, per-atom dependency graph [[11]](https://jotai.org/docs/basics/comparison) | ✓ via `createStore()` + `store.get/set` [[20]](https://jotai.org/docs/guides/using-store-outside-react) | ✓ `atomWithStorage` | ⭐ 21k [[5]](https://github.com/pmndrs/jotai) |
| **[Redux Toolkit](https://redux-toolkit.js.org)** 2.12 | ~28 lines + mandatory `<Provider>` [[25]](https://dev.to/jsgurujobs/state-management-in-2026-zustand-vs-jotai-vs-redux-toolkit-vs-signals-2gge) | Good but verbose slices | **12 KB** [[3]](https://saschb2b.com/blog/react-state-management-2026) | ✓✓ Best-in-class time-travel | `createSelector` / `useSelector` | ✓ reducers are pure functions | ✗ third-party (`redux-persist`) | ⭐ 11k [[6]](https://github.com/reduxjs/redux-toolkit) |
| **[Valtio](https://valtio.dev)** 2.3 | ~5 lines, mutable | Good | 3.2 KB [[3]](https://saschb2b.com/blog/react-state-management-2026) | `devtools` util | Automatic property-access tracking (`useSnapshot` = `useSyncExternalStore` + proxy-compare) [[26]](https://blog.axlight.com/posts/how-valtio-proxy-state-works-react-part/) | ✓ proxy is a plain object | ✗ manual `subscribe` | ⭐ 10k [[7]](https://github.com/pmndrs/valtio) |
| **[XState](https://stately.ai/docs)** 5.32 | Machine definition; heaviest | Excellent (v5 rewrite) | ~15 KB+ | ✓✓ Stately inspector | Actor-scoped | ✓ machines run headless | ✗ manual | ⭐ 30k [[8]](https://github.com/statelyai/xstate) |
| **Plain React 19** | 0 | Native | **0 KB** | React DevTools only (no time-travel) | ⚠ Context re-renders *every* consumer on value change [[19]](https://react.dev/reference/react/useSyncExternalStore) | ✗ needs `renderHook` | ✗ hand-rolled `useEffect` | — |

Adoption, State of React 2025: Zustand is called out as the category leader on satisfaction and is climbing fast [[2]](https://2025.stateofreact.com/en-US/libraries/state-management/); Zustand now leads npm downloads among dedicated client-state libraries (22.6M weekly vs RTK 11.4M, Jotai 2.9M, Valtio 1.2M) [[3]](https://saschb2b.com/blog/react-state-management-2026), and RTK's volume is largely legacy projects with no reason to migrate rather than new adoption [[24]](https://www.pkgpulse.com/blog/state-of-react-state-management-2026). Recoil was archived by Meta in early 2025 — don't [[3]](https://saschb2b.com/blog/react-state-management-2026).

## 3. The Nx angle — where the store lives

This is where the choice actually gets decided, and it is the axis every generic blog post misses.

**Zustand's `createStore` (from `zustand/vanilla`) produces a plain object with `getState` / `setState` / `subscribe` and no React import at all** [[10]](https://zustand.docs.pmnd.rs/learn/getting-started/comparison). Consequences for `itenium-ui`:

- `libs/state` can be tagged `type:util` / `scope:shared` with **no React peer dependency** and no context — nothing to leak across the two apps [[17]](https://nx.dev/features/enforce-module-boundaries).
- No `<Provider>` means no ordering constraint between the app shell and the lib. RTK forces the opposite: the store is only reachable through a React context, so `libs/state` becomes a React lib that both apps must wrap themselves in [[10]](https://zustand.docs.pmnd.rs/learn/getting-started/comparison).
- Jotai is "context-first, module-second" by its own docs [[11]](https://jotai.org/docs/basics/comparison) — provider-less mode works, but per-test and per-subtree isolation pulls you back to `<Provider>` [[27]](https://jotai.org/docs/core/provider). Workable, just more machinery than you need for three fields.

**Circular-import risk.** The realistic failure is `libs/state` importing a feature lib for a type, while the feature lib imports the store. Keep `libs/state` at the bottom of the tag graph — `onlyDependOnLibsWithTags: ["type:util"]` — and the `@nx/enforce-module-boundaries` lint rule fails the PR before it lands [[17]](https://nx.dev/features/enforce-module-boundaries). ⚠ The rule is project-level only, not folder-level, so a fat `libs/state` holding both apps' state is a boundary you can't lint *inside* [[18]](https://www.stefanos-lignos.dev/posts/nx-module-boundaries).

**Shared lib vs per-app.** With two apps (`itenium-ui`, `file-management`) that ship independently, split by ownership, not by convenience:

| | Lives in |
|---|---|
| Theme, sidebar (identical semantics both apps) | `libs/state` — shared, tagged `type:util` |
| Column visibility for `file-management`'s grids | `apps/file-management` (or `libs/file-management/state`) |

A store is cheap. Two small stores in the right libs beat one god-store that forces both apps to rebuild on every change — and Nx's affected graph will reward you for it.

## 4. TDD: the store under Jest, no render

The one hard requirement. A vanilla Zustand store in a lib, and a test that never mounts a component.

```ts
// libs/state/src/lib/ui-preferences.store.ts
import { useStore } from 'zustand';
import { createStore } from 'zustand/vanilla';
import { createJSONStorage, persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark' | 'system';

export interface UiPreferences {
  theme: Theme;
  sidebarCollapsed: boolean;
  hiddenColumns: Record<string, string[]>;
  setTheme: (theme: Theme) => void;
  toggleSidebar: () => void;
  toggleColumn: (table: string, column: string) => void;
}

export const uiPreferencesStore = createStore<UiPreferences>()(
  persist(
    (set) => ({
      theme: 'system',
      sidebarCollapsed: false,
      hiddenColumns: {},
      setTheme: (theme) => set({ theme }),
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      toggleColumn: (table, column) =>
        set((s) => {
          const hidden = s.hiddenColumns[table] ?? [];
          return {
            hiddenColumns: {
              ...s.hiddenColumns,
              [table]: hidden.includes(column)
                ? hidden.filter((c) => c !== column)
                : [...hidden, column],
            },
          };
        }),
    }),
    {
      name: 'itenium.ui.preferences',
      version: 1,
      storage: createJSONStorage(() => localStorage),
      partialize: ({ theme, sidebarCollapsed, hiddenColumns }) => ({
        theme,
        sidebarCollapsed,
        hiddenColumns,
      }),
    },
  ),
);

export const useUiPreferences = <T,>(selector: (s: UiPreferences) => T): T =>
  useStore(uiPreferencesStore, selector);
```

```ts
// libs/state/src/lib/ui-preferences.store.spec.ts
import { uiPreferencesStore } from './ui-preferences.store';

const initialState = uiPreferencesStore.getInitialState();

beforeEach(() => uiPreferencesStore.setState(initialState, true));

describe('uiPreferencesStore', () => {
  it('toggles a column off, then back on', () => {
    const { toggleColumn } = uiPreferencesStore.getState();

    toggleColumn('users', 'email');
    expect(uiPreferencesStore.getState().hiddenColumns['users']).toEqual(['email']);

    toggleColumn('users', 'email');
    expect(uiPreferencesStore.getState().hiddenColumns['users']).toEqual([]);
  });

  it('notifies subscribers on theme change', () => {
    const listener = jest.fn();
    uiPreferencesStore.subscribe(listener);

    uiPreferencesStore.getState().setTheme('dark');

    expect(listener).toHaveBeenCalledTimes(1);
    expect(uiPreferencesStore.getState().theme).toBe('dark');
  });
});
```

No provider, no `renderHook`, no `act`. Two notes that are real constraints rather than restatements of the code:

- `getInitialState()` + `setState(next, true)` (the `true` = *replace*, not merge) is the reset idiom. Zustand's own Jest guide scales this to every store at once with a `__mocks__/zustand.ts` that collects reset functions and fires them in `afterEach` [[12]](https://zustand.docs.pmnd.rs/learn/guides/testing) — worth adopting the moment you have more than two stores.
- `persist` with `createJSONStorage(() => localStorage)` needs a DOM. Nx's React Jest preset already runs `jsdom`; if you ever move `libs/state` to a `node` test environment, the store construction itself will throw.

For contrast: RTK reducers are equally testable as pure functions, but you test *reducers*, not *the store* — the thunks and the wiring still need a `<Provider>`. Jotai needs `createStore()` per test and `store.get(atom)` assertions [[13]](https://jotai.org/docs/guides/testing). Plain Context needs `renderHook` with a wrapper — i.e. you cannot test your state logic without React at all.

## 5. Traps

- ⚠ **Zustand v5 + object selectors.** `useStore(store, s => ({ a: s.a, b: s.b }))` returns a new reference each render → `useSyncExternalStore` sees a change → "Maximum update depth exceeded" [[15]](https://zustand.docs.pmnd.rs/reference/migrations/migrating-to-v5). It is the single most common v5 crash [[16]](https://github.com/pmndrs/zustand/discussions/2790). Select primitives one at a time, or wrap in `useShallow`. Add an ESLint rule and it never bites twice.
- ⚠ **Don't put the wizard draft in the global store.** It has the wizard's lifecycle, not the app's. `useReducer` co-located with the route; add `persist` only if a half-finished draft must survive a reload — and then give it its own store with its own `name`, so clearing it is one `.clearStorage()` call.
- ⚠ **Context is not free.** Any change to a context value re-renders every consumer in the subtree [[19]](https://react.dev/reference/react/useSyncExternalStore) — fine for a theme that changes twice a session, wrong for anything a table touches. That is the entire reason external stores exist.
- **XState is not a competitor here, it's a scalpel.** If one wizard grows genuinely gnarly transitions, add `@xstate/store` or a machine *for that wizard* [[21]](https://stately.ai/docs/xstate-store) — it's framework-agnostic and drops into `libs/` cleanly. Adopting XState as the app's state layer for three booleans is not KISS.
- **Valtio** is fine engineering — `useSnapshot` is `useSyncExternalStore` + `proxy-compare`, so render tracking is automatic [[26]](https://blog.axlight.com/posts/how-valtio-proxy-state-works-react-part/) — but at 1.2M weekly downloads [[3]](https://saschb2b.com/blog/react-state-management-2026) and mutable semantics that fight the immutable habits of a C#/.NET architect, it buys nothing Zustand doesn't.

## 6. Verdict for `itenium-ui`

1. **TanStack Query** owns everything the Forge API returns (including `/me` and feature flags).
2. **Zustand** — one `libs/state` lib, vanilla `createStore`, `persist` middleware, tagged `type:util`, lint-fenced at the bottom of the dep graph. Add the `devtools` middleware in dev only; it speaks Redux DevTools, so you keep time-travel without the 12 KB.
3. **nuqs** ⭐ 11k when table filter/sort/page state needs to be linkable [[22]](https://nuqs.dev/) — it is state you'd otherwise wrongly put in the store.
4. **React 19 built-ins** for everything with a component's lifetime: `useState` for modals/popovers, `useReducer` for wizards, `useActionState`/`useOptimistic` for CRUD mutations [[9]](https://react.dev/blog/2024/12/05/react-19).

You could ship this app with zero state libraries — 34% of React devs use none [[2]](https://2025.stateofreact.com/en-US/libraries/state-management/) — and the honest reason not to is persistence + avoiding a theme Context that re-renders the world. That's a 1.2 KB problem, and Zustand is the 1.2 KB answer.
