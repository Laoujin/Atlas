---
title: "Persisting and restoring pane layouts in React (2026)"
date: 2026-07-16
depth: standard
format: md
topic: "Persisting and restoring user-arranged pane layouts in React apps (2026). How the main splitter/docking libraries serialize layout state and restore it across sessions: JSON model shape, where to persist (localStorage vs backend), per-user server-side persistence, and the migration/versioning problem when the panel set changes between releases."
topic_raw: "Saving and restoring pane layouts across sessions."
tags: [react, layout, persistence, docking, splitters, versioning]
summary: "How react-resizable-panels, Allotment, Dockview, rc-dock and FlexLayout serialize and restore layouts, where to persist them, and how to survive a saved layout that references a deleted panel."
citations: 12
reading_time_min: 7
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 263
issue: 10
---

> **Decision.** Two problem classes, two answers. **Splitters** (just pane *sizes*): use [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) `autoSaveId` — zero-code localStorage, swap the `storage` prop for a backend adapter when you need per-user sync [[1]](https://github.com/bvaughn/react-resizable-panels)[[2]](https://app.unpkg.com/react-resizable-panels@2.0.19/files/README.md). **Docking** (tabs, groups, arrangement): [Dockview](https://dockview.dev) `toJSON`/`fromJSON`, [rc-dock](https://github.com/ticlo/rc-dock) `saveLayout`/`loadLayout`, or [FlexLayout](https://github.com/caplin/FlexLayout) `Model.toJson`/`fromJson` [[3]](https://dockview.dev/docs/core/state/save/)[[8]](https://github.com/ticlo/rc-dock)[[9]](https://github.com/caplin/FlexLayout/blob/master/README.md). For docking, **always wrap `fromJSON` in a version check + a prune-unknown-panels pass + a try/catch default fallback** — these libraries reference panels by string name and throw (or wedge) when a saved layout names a panel you've since deleted [[5]](https://dockview.dev/docs/core/state/load/)[[6]](https://github.com/mathuo/dockview/issues/341).

## The two problem shapes

Persisting a **splitter** means persisting an array of numbers (pane sizes). Persisting a **docking** layout means persisting a *tree*: which panels exist, how they're grouped into tabsets, their split geometry, and which is active. The docking case is where all the hard problems (registry drift, versioning) live.

## JSON model shape per library

| Library | ⭐ Stars | Serialize / restore | What the payload contains |
|---|---|---|---|
| [react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) | ⭐ 5.3k | `autoSaveId` (auto) or `onLayout` + `storage` | Array of size **percentages**, keyed by sorted panel IDs [[1]](https://github.com/bvaughn/react-resizable-panels)[[2]](https://app.unpkg.com/react-resizable-panels@2.0.19/files/README.md) |
| [Allotment](https://github.com/johnwalley/allotment) | ⭐ 1.3k | `onChange(sizes)` → you store; `defaultSizes` / `ref.resize()` to restore | Array of **numbers** (pixel sizes) [[10]](https://github.com/johnwalley/allotment) |
| [Dockview](https://dockview.dev) | ⭐ 3.3k | `api.toJSON()` / `api.fromJSON()` | `SerializedDockview`: `{ grid: { root, width, height, orientation }, panels, activeGroup }` [[3]](https://dockview.dev/docs/core/state/save/)[[11]](https://dockview.dev/docs/api/dockview/overview/) |
| [rc-dock](https://github.com/ticlo/rc-dock) | ⭐ 812 | `saveLayout()` / `loadLayout()` | Box/panel/tab tree; tabs stored as **IDs only**, content rehydrated via `loadTab` [[8]](https://github.com/ticlo/rc-dock) |
| [FlexLayout](https://github.com/caplin/FlexLayout) | ⭐ 1.3k | `model.toJson()` / `Model.fromJson()` | `{ global, layout: row/tabset/tab, borders, subLayouts }`; tab weights are proportional [[9]](https://github.com/caplin/FlexLayout/blob/master/README.md) |

The unifying trait for all three docking libraries: **a tab/panel node stores a component *name* (a string), not the component**. Restoration is a lookup — the name is resolved against a registry (`components` map in Dockview, `loadTab` in rc-dock, the `factory` function in FlexLayout) to produce the actual React element [[9]](https://github.com/caplin/FlexLayout/blob/master/README.md)[[12]](https://dockview.dev/docs/core/panels/register/)[[8]](https://github.com/ticlo/rc-dock). That indirection is exactly what breaks across releases (see Versioning below).

### Splitters: the size array

react-resizable-panels serializes to localStorage under the key `react-resizable-panels:<autoSaveId>` with no code beyond the prop [[13]](https://viprasol.com/blog/react-resizable-panels/):

```jsx
<PanelGroup autoSaveId="ide-layout" direction="horizontal">
  <Panel id="sources" order={1} defaultSize={25}><Sources /></Panel>
  <PanelResizeHandle />
  <Panel id="viewer" order={2}><Viewer /></Panel>
</PanelGroup>
```

When panels are conditionally rendered, give each `Panel` a stable `id` **and** `order` so the persisted array maps back to the right pane [[2]](https://app.unpkg.com/react-resizable-panels@2.0.19/files/README.md). Allotment has no built-in persistence — you wire `onChange` (debounced) to your store and restore with `defaultSizes` or an imperative `ref.current.resize([...])` [[10]](https://github.com/johnwalley/allotment).

### Docking: capture on change

All three docking libraries expose a change event so you can autosave without a save button — Dockview `onDidLayoutChange`, FlexLayout `onModelChange`, rc-dock `onLayoutChange` [[3]](https://dockview.dev/docs/core/state/save/)[[9]](https://github.com/caplin/FlexLayout/blob/master/README.md):

```ts
api.onDidLayoutChange(() => {
  localStorage.setItem('dock', JSON.stringify(api.toJSON()));
});
```

## Where to persist

| Target | Use when | Trade-offs |
|---|---|---|
| **localStorage** | Single-device convenience, no auth | Per-browser, lost on cache clear; SSR hydration flash [[1]](https://github.com/bvaughn/react-resizable-panels) |
| **Cookie** | You SSR and want zero flash | Server reads the cookie and sets `defaultSize`/`defaultLayout` before paint; react-resizable-panels ships a cookie-storage pattern for this [[13]](https://viprasol.com/blog/react-resizable-panels/)[[1]](https://github.com/bvaughn/react-resizable-panels) |
| **Backend / user profile** | Cross-device sync, per-user layouts, teams | Needs auth + an API round-trip; debounce writes; handle offline |

The SSR flash is real: the server renders the *default* layout, then client JS swaps in the localStorage layout on mount. A cookie (readable server-side) removes the flash because the server already knows the persisted sizes [[1]](https://github.com/bvaughn/react-resizable-panels).

## Per-user server-side persistence

The clean seam is a **storage adapter**. react-resizable-panels' `storage` prop takes any object matching:

```ts
interface PanelGroupStorage {
  getItem: (name: string) => string;
  setItem: (name: string, value: string) => void;
}
```

Both methods are **synchronous** [[2]](https://app.unpkg.com/react-resizable-panels@2.0.19/files/README.md), so a backend adapter keeps an in-memory cache that a debounced `PATCH /me/layout` flushes:

```ts
const backendStorage: PanelGroupStorage = {
  getItem: (k) => cache[k] ?? '',
  setItem: (k, v) => { cache[k] = v; queueFlush(k, v); }, // debounced PUT
};
// <PanelGroup autoSaveId="ide" storage={backendStorage}>
```

For docking libraries there's no storage prop — you own the plumbing: hydrate the layout from `GET /me/layout` before mounting the dock (render a default until it resolves), and push `toJSON()` output on the change event through a debounced writer. Store one row per `(userId, layoutKey)` with the serialized JSON in a `jsonb`/`nvarchar(max)` column plus a `schema_version` integer (below).

## The versioning / migration problem

This is the failure mode that bites in production. A saved layout is a snapshot of the panel set **as it was when saved**. Ship a release that renames or removes a panel, and a returning user's stored layout now references a panel name your registry no longer knows.

- **Dockview** throws on an unknown component name, and historically wedged so badly that even `api.clear()` failed — you had to manually wipe localStorage. The maintainer calls invalid component names "the single most likely form of layout corruption" [[6]](https://github.com/mathuo/dockview/issues/341). Modern Dockview resets gracefully on a bad `fromJSON`, but *your* app still has to catch the error and supply a default [[5]](https://dockview.dev/docs/core/state/load/).
- **react-resizable-panels**: changing the number of panels makes the stored size array stale; the fix is to **bump `autoSaveId`** (e.g. `"ide-v2"`) or clear the old key on startup [[13]](https://viprasol.com/blog/react-resizable-panels/).
- **FlexLayout / rc-dock**: an orphaned tab node routes to a `factory`/`loadTab` call with a name that has no mapping — a blank or broken tab unless you handle the miss [[9]](https://github.com/caplin/FlexLayout/blob/master/README.md)[[8]](https://github.com/ticlo/rc-dock).

None of these libraries validate a saved layout against your *current* panel registry for you. You must.

### Concrete patterns (cheapest → most robust)

1. **Bump the key / version stamp.** Wrap every payload: `{ schemaVersion: 3, layout }`. On load, if `schemaVersion !== CURRENT`, discard and use the default. Coarse — throws away *all* customization on any change — but a two-line safety net [[13]](https://viprasol.com/blog/react-resizable-panels/).
2. **Migrate.** Keep ordered migration functions `v1→v2→v3` that rewrite the JSON (rename a component, drop a node) before it reaches `fromJSON`. Preserves user arrangement across renames; the standard redux-persist-style approach.
3. **Prune-unknown (the robust default).** Before restoring, walk the serialized tree and delete any panel/tab whose component name isn't in your current registry; collapse now-empty tabsets. Then feed the sanitized tree to `fromJSON`. This survives *unanticipated* drift, not just versions you migrated:

```ts
function sanitize(saved, knownNames: Set<string>) {
  const panels = Object.fromEntries(
    Object.entries(saved.panels).filter(([, p]) => knownNames.has(p.contentComponent))
  );
  return prunePanelRefs({ ...saved, panels }, new Set(Object.keys(panels)));
}
```

4. **try/catch with default fallback (always, as the last line):**

```ts
try {
  api.fromJSON(sanitize(migrate(saved), knownNames));
} catch {
  localStorage.removeItem('dock');   // or clear the backend row
  api.fromJSON(DEFAULT_LAYOUT);
}
```

## Recommended approach

- **Splitter-only UIs:** react-resizable-panels ⭐ 5.3k with `autoSaveId`. Stable `id`+`order` on every `Panel`. Go to a cookie-backed `storage` if you SSR, a backend adapter if you need per-user sync [[1]](https://github.com/bvaughn/react-resizable-panels)[[2]](https://app.unpkg.com/react-resizable-panels@2.0.19/files/README.md).
- **Docking UIs:** pick Dockview ⭐ 3.3k for the richest API and framework wrappers [[3]](https://dockview.dev/docs/core/state/save/)[[7]](https://portalzine.de/docker-layouts-with-goldenlayout/). Persist `{ schemaVersion, payload }` per user server-side. On restore run **version-gate → migrate → prune-unknown → `fromJSON` in try/catch → default fallback**, in that order. The prune pass plus the try/catch are non-negotiable: they are what stop a single deleted panel from bricking a returning user's whole workspace [[6]](https://github.com/mathuo/dockview/issues/341)[[5]](https://dockview.dev/docs/core/state/load/).
- **Don't** store the size array or layout tree without a version stamp. The day you restructure panels, unstamped payloads are landmines.
