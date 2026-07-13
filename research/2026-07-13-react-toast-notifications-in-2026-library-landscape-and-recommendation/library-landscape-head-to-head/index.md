---
title: "React toast libraries in 2026: Sonner, react-toastify, react-hot-toast, notistack and the design-system natives"
date: 2026-07-13
depth: survey
format: md
topic: "Head-to-head comparison of the React toast/notification library landscape in 2026: Sonner, react-toastify, react-hot-toast, notistack, and design-system toast primitives (Mantine, Chakra, MUI Snackbar, shadcn/ui) — API ergonomics, promise support, bundle size, TypeScript, maintenance health, React 19 compatibility."
topic_raw: "react toastr 2026"
tags: [react, toast, notifications, sonner, react-toastify, react-hot-toast, notistack, shadcn, bundle-size]
summary: "Sonner is the 2026 default (41M weekly installs, shadcn's toast); react-toastify is the actively-released power option; react-hot-toast is the 4.7 kB minimalist; notistack is legacy."
citations: 41
reading_time_min: 10
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 618
issue: 3
---

> **Decision.** Reach for **[Sonner](https://sonner.emilkowal.ski/)** ⭐ 12.6k unless you have a reason not to — it is what `shadcn add sonner` installs, it has zero runtime dependencies, and at 41.4M weekly npm installs it is now an order of magnitude more installed than anything else in this category [[1]](https://www.npmjs.com/package/sonner) [[2]](https://ui.shadcn.com/docs/components/radix/sonner). Reach for **[react-toastify](https://fkhadra.github.io/react-toastify/)** ⭐ 13.4k when you need a deep, configurable feature surface (custom progress bars, notification centre, CSP nonce) and the most recent release cadence — v11.1.0 shipped April 2026 [[3]](https://github.com/fkhadra/react-toastify/releases). Reach for **[react-hot-toast](https://react-hot-toast.com/)** ⭐ 11k when bundle size dominates (4.7 kB gz, roughly half of everything else) [[4]](https://bundlephobia.com/package/react-hot-toast@2.6.0). If you already ship [Mantine](https://mantine.dev/x/notifications/), [Chakra v3](https://chakra-ui.com/docs/components/toast) or [Base UI](https://base-ui.com/react/components/toast), use the in-house toaster — it costs ~0 marginal bytes. **[notistack](https://notistack.com/)** ⭐ 4.1k is the one to avoid for greenfield: no npm release since January 2025 [[5]](https://www.npmjs.com/package/notistack).

All numbers below were fetched live on **2026-07-13** (npm registry, npm downloads API, Bundlephobia, GitHub). Star counts and sizes shift; the ledger records what was measured.

## At a glance

| Library | ⭐ Stars | Weekly installs | min+gzip | Runtime deps | Latest release | Open issues | React 19 |
|---|---|---|---|---|---|---|---|
| [Sonner](https://sonner.emilkowal.ski/) [[6]](https://github.com/emilkowalski/sonner) | ⭐ 12.6k | 41.4M [[1]](https://www.npmjs.com/package/sonner) | **9.2 kB** (33.4 kB min) [[7]](https://bundlephobia.com/package/sonner@2.0.7) | **0** [[1]](https://www.npmjs.com/package/sonner) | 2.0.7 — 2025-08-02 [[1]](https://www.npmjs.com/package/sonner) | 52 [[8]](https://github.com/emilkowalski/sonner/issues) | ✓ peer `^18 \|\| ^19` [[1]](https://www.npmjs.com/package/sonner) |
| [react-toastify](https://fkhadra.github.io/react-toastify/) [[9]](https://github.com/fkhadra/react-toastify) | ⭐ 13.4k | 4.0M [[10]](https://www.npmjs.com/package/react-toastify) | 9.5 kB (33.6 kB min) [[11]](https://bundlephobia.com/package/react-toastify@11.1.0) | 1 (`clsx`) [[10]](https://www.npmjs.com/package/react-toastify) | **11.1.0 — 2026-04-19** [[3]](https://github.com/fkhadra/react-toastify/releases) | 72 [[12]](https://github.com/fkhadra/react-toastify/issues) | ✓ explicit v11 fix [[13]](https://fkhadra.github.io/react-toastify/migration-v11) |
| [react-hot-toast](https://react-hot-toast.com/) [[14]](https://github.com/timolins/react-hot-toast) | ⭐ 11k | 3.4M [[15]](https://www.npmjs.com/package/react-hot-toast) | **4.7 kB** (11.9 kB min) [[4]](https://bundlephobia.com/package/react-hot-toast@2.6.0) | 2 (`goober`, `csstype`) [[15]](https://www.npmjs.com/package/react-hot-toast) | 2.6.0 — 2025-08-15 [[16]](https://github.com/timolins/react-hot-toast/releases) | ⚠ 115 [[17]](https://github.com/timolins/react-hot-toast/issues) | ✓ types fixed in 2.5.2 [[16]](https://github.com/timolins/react-hot-toast/releases) |
| [notistack](https://notistack.com/) [[18]](https://github.com/iamhosseindhv/notistack) | ⭐ 4.1k | 1.4M [[5]](https://www.npmjs.com/package/notistack) | 8.2 kB (23.4 kB min) [[19]](https://bundlephobia.com/package/notistack@3.0.2) | 2 (`clsx`, `goober`) [[5]](https://www.npmjs.com/package/notistack) | ⚠ 3.0.2 — **2025-01-18** [[5]](https://www.npmjs.com/package/notistack) | 53 [[20]](https://github.com/iamhosseindhv/notistack/issues) | ✓ peer allows `^19` [[5]](https://www.npmjs.com/package/notistack) |
| [@mantine/notifications](https://mantine.dev/x/notifications/) [[21]](https://github.com/mantinedev/mantine) | ⭐ 31k (Mantine) | 741k [[41]](https://www.npmjs.com/package/@mantine/notifications) | 5.5 kB (+ `@mantine/core`) [[22]](https://bundlephobia.com/package/@mantine/notifications) | peer: `@mantine/core` | 9.4.1 — 2026-06-28 [[22]](https://bundlephobia.com/package/@mantine/notifications) | — | ✓ |
| [Chakra UI v3 Toaster](https://chakra-ui.com/docs/components/toast) [[23]](https://github.com/chakra-ui/chakra-ui) | ⭐ 41k (Chakra) | — | part of `@chakra-ui/react` 3.36.0 (293 kB gz whole lib, tree-shaken) [[24]](https://bundlephobia.com/package/@chakra-ui/react) | Ark UI | 3.36.0 — 2026-06-10 [[24]](https://bundlephobia.com/package/@chakra-ui/react) | — | ✓ |
| [MUI Snackbar](https://mui.com/material-ui/react-snackbar/) [[25]](https://github.com/mui/material-ui) | ⭐ 99k (MUI) | — | part of `@mui/material` 9.2.0 (146.6 kB gz whole lib) [[26]](https://bundlephobia.com/package/@mui/material) | — | 9.2.0 — 2026-07-03 [[26]](https://bundlephobia.com/package/@mui/material) | — | ✓ |
| [Base UI Toast](https://base-ui.com/react/components/toast) [[27]](https://github.com/mui/base-ui) | ⭐ 10k (Base UI) | 6.2M (`@base-ui/react`) [[28]](https://www.npmjs.com/package/@base-ui/react) | part of `@base-ui/react` 1.6.0 (145 kB gz whole lib) [[28]](https://www.npmjs.com/package/@base-ui/react) | — | 1.6.0 — 2026-06-18 [[28]](https://www.npmjs.com/package/@base-ui/react) | — | ✓ |

The install gap is the headline number of 2026. Sonner is not "a bit more popular" than react-toastify — it is **~10× more installed per week** (41.4M vs 4.0M) [[1]](https://www.npmjs.com/package/sonner) [[10]](https://www.npmjs.com/package/react-toastify), because every project scaffolded through shadcn/ui ⭐ 119k pulls it in: shadcn's own `toast` component is formally deprecated in favour of Sonner [[29]](https://ui.shadcn.com/docs/components/radix/toast) [[30]](https://github.com/shadcn-ui/ui/issues/7120). Treat downloads as an *install-graph* signal, not a popularity vote — but the install graph is what determines how much Stack Overflow, LLM training data and third-party wrappers exist for a library.

## API surface and ergonomics

All four standalone libraries converge on the same shape: **mount one container component at the app root, then call an imperative `toast()` from anywhere** — no context, no prop drilling, callable from event handlers, `catch` blocks, or non-React code.

| | Container | Call site |
|---|---|---|
| Sonner | `<Toaster />` [[31]](https://sonner.emilkowal.ski/) | `toast('msg')`, `toast.success/error/warning/info/promise/custom` [[31]](https://sonner.emilkowal.ski/) |
| react-toastify | `<ToastContainer />` [[32]](https://fkhadra.github.io/react-toastify/introduction/) | `toast('msg', {...})`, `toast.success/error/…/promise` [[32]](https://fkhadra.github.io/react-toastify/introduction/) |
| react-hot-toast | `<Toaster />` [[33]](https://react-hot-toast.com/docs) | `toast()`, `toast.promise`, plus `useToaster()` / `useToasterStore()` headless hooks [[33]](https://react-hot-toast.com/docs) |
| notistack | `<SnackbarProvider>` wrapper | `enqueueSnackbar()` / `useSnackbar()` |
| Mantine | `<Notifications />` inside `MantineProvider` [[34]](https://mantine.dev/x/notifications/) | `notifications.show/hide/update/clean` [[34]](https://mantine.dev/x/notifications/) |
| Chakra v3 | `<Toaster />` + `createToaster()` [[35]](https://chakra-ui.com/docs/components/toast) | `toaster.create/update/dismiss/promise` [[35]](https://chakra-ui.com/docs/components/toast) |
| Base UI | `<Toast.Provider>` + `<Toast.Viewport>` [[36]](https://base-ui.com/react/components/toast) | `useToastManager().add/update/close/promise`, or a global manager via `Toast.createToastManager()` [[36]](https://base-ui.com/react/components/toast) |
| MUI Snackbar | none | ⚠ **declarative only** — you hold `open` state yourself [[37]](https://mui.com/material-ui/react-snackbar/) |

MUI Snackbar is the outlier and the reason notistack exists at all: it renders one snackbar bound to an `open` prop, has no queue, and the MUI docs themselves point at notistack for stacking — *"With an imperative API, notistack lets you vertically stack multiple Snackbars without having to handle their open and close states"* [[37]](https://mui.com/material-ui/react-snackbar/). If you are on MUI and want toasts, you are choosing between hand-rolling a queue, adopting notistack (see maintenance caveat below), or dropping Sonner in next to MUI — Sonner has no MUI coupling.

## Feature matrix

| Feature | Sonner | react-toastify | react-hot-toast | notistack | Mantine | Chakra v3 | Base UI |
|---|---|---|---|---|---|---|---|
| `toast.promise()` (loading→success/error) | ✓ [[31]](https://sonner.emilkowal.ski/) | ✓ [[32]](https://fkhadra.github.io/react-toastify/introduction/) | ✓ [[33]](https://react-hot-toast.com/docs) | ✗ (manual `update`) | ✗ (manual `notifications.update`) [[34]](https://mantine.dev/x/notifications/) | ✓ `toaster.promise` [[35]](https://chakra-ui.com/docs/components/toast) | ✓ `.promise()` [[36]](https://base-ui.com/react/components/toast) |
| Arbitrary JSX content | ✓ `toast.custom` [[31]](https://sonner.emilkowal.ski/) | ✓ "bring your own component" [[32]](https://fkhadra.github.io/react-toastify/introduction/) | ✓ `toast.custom` [[33]](https://react-hot-toast.com/docs) | ✓ `content` | ~ (Styles API, not free JSX) [[34]](https://mantine.dev/x/notifications/) | ✓ composable subcomponents [[35]](https://chakra-ui.com/docs/components/toast) | ✓ fully composable parts [[36]](https://base-ui.com/react/components/toast) |
| Headless / unstyled mode | ✓ headless option [[31]](https://sonner.emilkowal.ski/) | ~ (v11 simplified DOM, CSS overridable) [[13]](https://fkhadra.github.io/react-toastify/migration-v11) | ✓ `useToaster()` [[33]](https://react-hot-toast.com/docs) | ~ | ✗ | ~ | ✓ unstyled by design [[36]](https://base-ui.com/react/components/toast) |
| Visible-count cap / queue | ✓ `visibleToasts` [[31]](https://sonner.emilkowal.ski/) | ✓ `limit` [[32]](https://fkhadra.github.io/react-toastify/introduction/) | ✓ (per-type limits) | ✓ `maxSnack` | ✓ `limit` + FIFO queue + `priority` [[34]](https://mantine.dev/x/notifications/) | ✓ `max`, `overlap` [[35]](https://chakra-ui.com/docs/components/toast) | ✓ [[36]](https://base-ui.com/react/components/toast) |
| Stack-and-expand-on-hover UX | ✓ `expand` [[31]](https://sonner.emilkowal.ski/) | ✗ (list) | ✗ (list) | ✗ (list) | ✗ | ✓ `overlap` [[35]](https://chakra-ui.com/docs/components/toast) | ✓ (CSS-var stacking) [[36]](https://base-ui.com/react/components/toast) |
| Update an existing toast by id | ✓ | ✓ | ✓ | ✓ | ✓ `notifications.update` [[34]](https://mantine.dev/x/notifications/) | ✓ [[35]](https://chakra-ui.com/docs/components/toast) | ✓ (re-`add` with same id) [[36]](https://base-ui.com/react/components/toast) |
| Multiple independent toasters | ~ | ✓ (containerId) | ✓ **added in 2.6.0** [[16]](https://github.com/timolins/react-hot-toast/releases) | ✗ | ✗ | ✓ (multiple `createToaster`) [[35]](https://chakra-ui.com/docs/components/toast) | ✓ | 
| Zero CSS import needed | ✓ | ✓ **since v11 — style tag is injected** [[13]](https://fkhadra.github.io/react-toastify/migration-v11) | ✓ (goober CSS-in-JS) | ✓ (goober) | ⚠ **must import `@mantine/notifications/styles.css`** [[34]](https://mantine.dev/x/notifications/) | ✓ | ✓ (you write the CSS) |
| CSP nonce support | ~ | ✓ `nonce` prop (11.1.0) [[3]](https://github.com/fkhadra/react-toastify/releases) | ~ | ~ | ✓ (Mantine-wide) | ✓ | ✓ |
| Swipe-to-dismiss | ✓ [[31]](https://sonner.emilkowal.ski/) | ✓ (drag) [[3]](https://github.com/fkhadra/react-toastify/releases) | ✗ | ✗ | ✗ | ✓ | ✓ [[36]](https://base-ui.com/react/components/toast) |

**TypeScript.** All seven are TS-native and ship their own declarations — none needs `@types/*`. Sonner and react-hot-toast are written in TS with fully typed `toast.*` overloads; react-hot-toast explicitly swapped the deprecated global `JSX.Element` type for `React.ReactElement` in 2.5.2, which is exactly the change React 19's type packages force [[16]](https://github.com/timolins/react-hot-toast/releases). react-toastify v11 removed the `useToastContainer` / `useToast` hooks from the public surface, so old typed wrappers around them break on upgrade [[13]](https://fkhadra.github.io/react-toastify/migration-v11).

**Accessibility.** All of them render an ARIA live region, so this axis is rarely the deciding factor — but it is not free. Sonner's 4s default auto-dismiss is below what WCAG 2.2.1 (Timing Adjustable) implies for slow readers; raise the `Toaster` duration if a11y is audited [[38]](https://www.pkgpulse.com/guides/react-hot-toast-vs-react-toastify-vs-sonner-2026). react-toastify v11 added an `ariaLabel` prop and an `alt+t` keyboard shortcut to focus the notification region [[13]](https://fkhadra.github.io/react-toastify/migration-v11); Base UI Toast uses `F6` to jump to the viewport landmark and configurable `low`/`high` live-region priority [[36]](https://base-ui.com/react/components/toast). Radix's own Toast primitive has an open, unresolved report that toasts are not announced because the live region resolves to `aria-live="off"` — a reason to prefer Sonner over hand-rolled Radix toasts even inside a Radix codebase [[39]](https://github.com/radix-ui/primitives/issues/3634).

## Maintenance health — the real differentiator

| Library | Last npm release | Last commit pushed | Read |
|---|---|---|---|
| react-toastify | 2026-04-19 (11.1.0) [[3]](https://github.com/fkhadra/react-toastify/releases) | 2026-04-19 [[9]](https://github.com/fkhadra/react-toastify) | **Actively released.** Bug-fix-and-feature release only 3 months ago; 72 open issues on a 13.4k-star repo is normal load. |
| Sonner | 2025-08-02 (2.0.7) [[1]](https://www.npmjs.com/package/sonner) | 2025-12-23 [[6]](https://github.com/emilkowalski/sonner) | **Quiet but not dead.** ~11 months without a release, ~7 without a commit — feature-complete single-maintainer project, 52 open issues. ⚠ Bus factor is the risk, not bugs. |
| react-hot-toast | 2025-08-15 (2.6.0) [[16]](https://github.com/timolins/react-hot-toast/releases) | 2025-08-16 [[14]](https://github.com/timolins/react-hot-toast) | **Slow.** ⚠ 115 open issues — highest absolute count here, and the repo has been untouched for ~11 months. Snyk still grades maintenance "Sustainable" on release cadence [[40]](https://security.snyk.io/package/npm/react-hot-toast). |
| notistack | ⚠ **2025-01-18** (3.0.2) [[5]](https://www.npmjs.com/package/notistack) | 2026-03-31 [[18]](https://github.com/iamhosseindhv/notistack) | **Effectively legacy.** 18 months without a published version. It still *works* (peer deps admit React 19, v3 dropped its MUI dependency and now ships on goober), and 1.4M weekly installs are mostly existing MUI codebases. Not a greenfield pick. |
| Mantine / Chakra / MUI / Base UI | 2026-06-28 / 2026-06-10 / 2026-07-03 / 2026-06-18 [[22]](https://bundlephobia.com/package/@mantine/notifications) [[24]](https://bundlephobia.com/package/@chakra-ui/react) [[26]](https://bundlephobia.com/package/@mui/material) [[28]](https://www.npmjs.com/package/@base-ui/react) | this month | **Backed by the design system's release train** — the toaster gets maintained as long as the design system does. |

Note the inversion of the popularity narrative: the library everyone installs (Sonner) has the *quietest* repo, and the library the blogosphere calls legacy (react-toastify) has the *newest* release. Neither fact should flip your decision on its own — a toast library is a small, finished problem — but if you need a fix landed upstream this quarter, react-toastify is the one whose maintainer is currently shipping.

## Design-system natives: use them if you already pay for them

- **Mantine** — `notifications.show()` from anywhere, `limit` with a real FIFO queue and a `priority` field that can bump a notification into a visible slot ahead of older ones; `notifications.update()` covers the loading→done pattern manually since there is no `promise()` helper. ⚠ It is the only option here that silently misbehaves without a CSS import (`@mantine/notifications/styles.css`, after core styles) [[34]](https://mantine.dev/x/notifications/). +5.5 kB gz on top of `@mantine/core` [[22]](https://bundlephobia.com/package/@mantine/notifications).
- **Chakra UI v3** — `createToaster()` + `toaster.create()`; the most complete built-in of the four: `toaster.promise()`, `max`, `overlap` stacking, `pauseOnPageIdle`, composable `Title`/`Description`/`ActionTrigger` parts, built on Ark UI [[35]](https://chakra-ui.com/docs/components/toast). Sensible only if Chakra is already your system — `@chakra-ui/react` is 293 kB gz as a whole package (tree-shakeable, but the design-system tax is real) [[24]](https://bundlephobia.com/package/@chakra-ui/react).
- **MUI** — Snackbar is a controlled component, not a toast system [[37]](https://mui.com/material-ui/react-snackbar/). Pair with notistack (aging) or bolt Sonner on.
- **shadcn/ui** — there is no shadcn toast any more. The `toast` component page carries *"The toast component has been deprecated. Use the sonner component instead."* [[29]](https://ui.shadcn.com/docs/components/radix/toast), tracked in issue #7120 [[30]](https://github.com/shadcn-ui/ui/issues/7120); `sonner` is now a first-class shadcn component with a pre-themed `<Toaster />` [[2]](https://ui.shadcn.com/docs/components/radix/sonner). This single decision is what produced Sonner's install numbers.
- **Base UI** (the MUI team's headless successor to Radix) — Toast is a genuine competitor now that Base UI is stable: `useToastManager()` with `add/update/close/promise`, a `createToastManager()` for firing toasts outside React, swipe-to-dismiss, F6 landmark navigation, fully unstyled [[36]](https://base-ui.com/react/components/toast). `@base-ui/react` reached 1.6.0 in June 2026 and does 6.2M weekly installs [[28]](https://www.npmjs.com/package/@base-ui/react). Pick it when you want to own every pixel and are already headless-first; skip it if you just want a toast that looks good today.

## Reach for X when Y

| When… | Reach for |
|---|---|
| Greenfield React app, no strong design system, you want good defaults in 10 minutes | **Sonner** — 0 deps, 9.2 kB, `toast.promise`, stack-and-expand, shadcn-native [[7]](https://bundlephobia.com/package/sonner@2.0.7) [[2]](https://ui.shadcn.com/docs/components/radix/sonner) |
| You use shadcn/ui | **Sonner** — there is no alternative in-system; `toast` is deprecated [[29]](https://ui.shadcn.com/docs/components/radix/toast) |
| Bundle budget is the hard constraint (marketing site, embed, widget) | **react-hot-toast** — 4.7 kB gz, ~half of Sonner; ⚠ accept a slow-moving repo [[4]](https://bundlephobia.com/package/react-hot-toast@2.6.0) [[17]](https://github.com/timolins/react-hot-toast/issues) |
| You need deep customisation (custom progress bar, notification centre, CSP nonce, containerId routing) or you want the maintainer who is actually shipping | **react-toastify v11** [[13]](https://fkhadra.github.io/react-toastify/migration-v11) [[3]](https://github.com/fkhadra/react-toastify/releases) |
| You already ship Mantine or Chakra v3 | **the built-in toaster** — ~0 marginal bytes, matches your theme [[34]](https://mantine.dev/x/notifications/) [[35]](https://chakra-ui.com/docs/components/toast) |
| You already ship MUI | **Sonner alongside MUI**, or notistack only if you're already on it — MUI's Snackbar has no queue [[37]](https://mui.com/material-ui/react-snackbar/) |
| Headless-first codebase, you style everything | **Base UI Toast** [[36]](https://base-ui.com/react/components/toast) |
| Existing notistack codebase | Stay — it works on React 19 — but ⚠ plan a Sonner migration; no release since Jan 2025 [[5]](https://www.npmjs.com/package/notistack) |
| Greenfield + notistack | Don't. |

Migrating away from a toast library is a mechanical find-and-replace of `toast()` call sites plus one root component — the switching cost is close to zero, which is exactly why you should not agonise over this decision. Take Sonner; revisit if a constraint bites.
