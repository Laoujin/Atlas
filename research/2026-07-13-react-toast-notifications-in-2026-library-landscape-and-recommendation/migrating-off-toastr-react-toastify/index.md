---
title: "Migrating off legacy toasts: toastr and react-toastify → Sonner"
date: 2026-07-13
depth: recon
format: md
topic: "Migrating off legacy toasts in React (2026): from jQuery-era toastr (CodeSeven/toastr) or from react-toastify to Sonner — API mapping, what must be rebuilt, promise toasts, i18n/RTL, testing fallout, and when not to migrate."
topic_raw: "react toastr 2026"
tags: [react, toast, sonner, react-toastify, toastr, migration, frontend]
summary: "toastr is dead (last commit 2018, needs jQuery) — migrate. react-toastify is alive (v11.1.0, Apr 2026) — don't churn a working integration."
citations: 12
reading_time_min: 3
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 278
issue: 3
---

> **Decision.** **From [`toastr`](https://github.com/CodeSeven/toastr): migrate now.** Last commit June 2018 ⭐ 12k (Jul 2026) [[1]](https://github.com/CodeSeven/toastr/commits/master.atom), last npm publish 2.1.4 in Dec 2017, hard `jquery >=1.12.0` dependency [[2]](https://registry.npmjs.org/toastr) — it imperatively appends DOM outside React and breaks SSR/concurrent rendering. **From [`react-toastify`](https://github.com/fkhadra/react-toastify): don't.** v11.1.0 shipped Apr 2026, actively maintained ⭐ 13k (Jul 2026) [[3]](https://github.com/fkhadra/react-toastify). A working integration is not a migration trigger. Move only if you're adopting shadcn/ui (Sonner is its default toast) or you want stacking/gestures for free — [Sonner](https://sonner.emilkowal.ski/) ⭐ 13k (Jul 2026) [[4]](https://github.com/emilkowalski/sonner), ~189M npm downloads/month vs react-toastify's ~16M [[5]](https://api.npmjs.org/downloads/point/last-month/sonner).

## API mapping

| Legacy | Sonner |
|---|---|
| `toastr.success(msg)` / `toastr.error(msg, title)` | `toast.success(msg)` / `toast.error(title, { description: msg })` [[6]](https://sonner.emilkowal.ski/toast) |
| `toastr.options = {...}` (global mutable) | `<Toaster toastOptions={{...}} />` props [[7]](https://sonner.emilkowal.ski/toaster) |
| `toast.success(msg, opts)` (toastify) | `toast.success(msg, opts)` — near 1:1 [[6]](https://sonner.emilkowal.ski/toast) |
| `toast.loading()` → `toast.update(id, {render, type})` | `const id = toast.loading(m); toast.success(m2, { id })` [[6]](https://sonner.emilkowal.ski/toast) |
| `toast.promise(p, {pending, success, error})` | `toast.promise(p, {loading, success, error})` — `pending`→`loading`; callbacks get the resolved value [[6]](https://sonner.emilkowal.ski/toast) |
| `toast.dismiss(id)`, `toast.isActive(id)` | `toast.dismiss(id)`; no `isActive` — track ids yourself |
| `<ToastContainer rtl />` | `<Toaster dir="rtl" />` (`ltr`/`rtl`/`auto`) [[7]](https://sonner.emilkowal.ski/toaster) |
| `containerId` multi-region | `<Toaster id="x" />` + `toast(m, { toasterId: 'x' })` [[7]](https://sonner.emilkowal.ski/toaster) |

## No equivalent — rebuild or drop

| react-toastify feature | Sonner reality |
|---|---|
| Progress bar (`hideProgressBar`, `progress` for manual control) [[8]](https://fkhadra.github.io/react-toastify/api/toast-container/) | ✗ none. Rebuild as custom JSX + CSS animation, or drop. |
| `transition` / `cssTransition({enter, exit, collapse})` [[9]](https://fkhadra.github.io/react-toastify/custom-animation/) | ✗ no transition API. Animations are baked in; you get `data-*` attribute CSS hooks + `classNames` only. |
| `toast.update(id, { render, type, autoClose, className })` [[10]](https://fkhadra.github.io/react-toastify/update-toast/) | Partial: re-calling `toast.<type>(msg, { id })` replaces content/type. No per-field patching, no update-transition. |
| `closeButton={MyButton}` custom component | Only `closeButton` bool + `classNames.closeButton` / `icons`. Custom → `toast.custom()`. |
| `draggable`, `pauseOnFocusLoss`, `limit`, `stacked`, `newestOnTop` | Swipe + hover-pause + stacking are default/`expand`; the fine-grained knobs are gone. |
| Full styling escape hatch | `toast.custom(<Jsx/>)` or `unstyled` — this is where custom containers land. |

## Gotchas

- ⚠ **Testing:** `toast.promise` misbehaves under Jest-mocked promises (`TypeError: n is not a function`) ⭐ 13k [[11]](https://github.com/emilkowalski/sonner/issues/435); jsdom needs a `window.matchMedia` mock or the `<Toaster/>` never renders. Sonner emits `<li data-sonner-toast>` inside an `aria-live` `<ol>` — every `getByRole('alert')`/`.Toastify__toast` selector in your suite dies.
- ⚠ **Sonner is opinionated:** no theming system beyond `theme`/`richColors`/`classNames`. Heavily branded toastify containers = rewrite, not remap.
- ⚠ **i18n:** both are string-in, so `t()` calls port unchanged, but Sonner's `action`/`cancel` labels and the close-button `aria-label` need `<Toaster>`-level translation.

## Effort

Mechanical toastify→Sonner: **0.5–1 day** for a typical app — swap imports, add `<Toaster/>`, sed the call sites, fix `pending`→`loading`. Budget **+2–4 days** if you have custom transitions, a manual progress bar, custom close buttons, or >20 toast assertions in tests. From `toastr`: same, plus dropping jQuery. The safe path both ways: a `notify.ts` wrapper module first, swap the engine behind it [[12]](https://www.pkgpulse.com/guides/react-hot-toast-vs-react-toastify-vs-sonner-2026).
