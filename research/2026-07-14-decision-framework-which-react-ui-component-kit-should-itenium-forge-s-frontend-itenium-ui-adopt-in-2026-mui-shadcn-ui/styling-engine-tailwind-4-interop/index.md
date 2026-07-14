---
title: "Styling engine and Tailwind 4 interop: which React component kit survives the cascade"
date: 2026-07-14
depth: expedition
format: md
topic: "Styling engine and Tailwind 4 interop for React UI component kits in 2026 — the central friction in choosing between MUI, shadcn/ui, Mantine, and Base UI 1.0 for a greenfield admin console already committed to Tailwind CSS 4."
topic_raw: "Decision framework: which React UI component kit should Itenium.Forge's frontend (itenium-ui) adopt in 2026 — MUI, shadcn/ui, Mantine, or Base UI 1.0? Greenfield admin console on an Nx 21 + React 19 + Vite + Tailwind 4 monorepo, TypeScript-first"
tags: [tailwind, react, css, mui, shadcn, mantine, base-ui, cascade-layers, vite, design-systems]
summary: "Tailwind 4 puts every utility inside a cascade layer, so any kit that ships unlayered CSS silently outranks it — which reframes the MUI/shadcn/Mantine/Base UI choice as a question about where each kit's styles land in the layer stack, and surfaces a bigger Nx @source tax underneath all four."
citations: 141
reading_time_min: 26
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 1691
issue: 7
---

> **Decision.** With Tailwind 4 non-negotiable, the styling axis ranks: **shadcn/ui on Base UI** (no competing cascade — its components are Tailwind classes, and since July 2026 shadcn's default primitive *is* Base UI [[16]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default)); **Mantine** (a 3-line layer declaration and you're done [[69]](https://mantine.dev/styles/mantine-styles/)); **MUI** (works, but needs an opt-in `enableCssLayer` on every entry point and still ships Emotion's runtime alongside Tailwind [[8]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/)). Pigment CSS — MUI's zero-runtime escape from Emotion — is **officially on hold in alpha** [[2]](https://mui.com/blog/2026-and-beyond/); MUI v9 still runs on Emotion and lists "remove dependency on Emotion" under *What's next* [[3]](https://mui.com/blog/introducing-material-ui-v9/). **The real Tailwind 4 tax on this stack is not the kit at all — it's Nx**: `@tailwindcss/vite` only scans the app directory, so classes in your `libs/**` emit nothing until you hand-write `@source` directives, and Nx has publicly decided *not* to build native Tailwind 4 support [[110]](https://nx.dev/docs/technologies/react/guides/using-tailwind-css-in-react)[[116]](https://github.com/nrwl/nx/discussions/29810).

---

## 1. The one mechanic that decides everything

Tailwind v4's entry stylesheet is four lines [[98]](https://github.com/tailwindlabs/tailwindcss/blob/main/packages/tailwindcss/index.css) ⭐ 96k:

```css
@layer theme, base, components, utilities;
@import './theme.css'     layer(theme);      /* @theme tokens → CSS vars */
@import './preflight.css' layer(base);       /* the reset */
@import './utilities.css' layer(utilities);  /* every utility */
```

Every Tailwind utility now lives **inside** a named cascade layer. Per the CSS cascade spec, a normal (non-`!important`) declaration **outside** any layer beats a normal declaration **inside** any layer, regardless of specificity, source order, or layer order — only `!important` or a different origin reverses it [[99]](https://developer.mozilla.org/en-US/docs/Web/CSS/@layer).

> **Any component kit whose CSS is unlayered silently outranks every Tailwind 4 utility.** `className="p-0"` on the kit's button does nothing. This *worked* in Tailwind v3, which had no layers.

A Tailwind collaborator confirms the mechanism in the Mantine bug thread: *"Tailwind utility classes are now in cascade layers, which have lower precedence than rules not in any layer"* [[74]](https://github.com/tailwindlabs/tailwindcss/discussions/15832) ⭐ 96k. It is not MUI-specific — Livewire's Flux kit hit the identical bug [[33]](https://github.com/livewire/flux/issues/783) ⭐ 954 — and the December 2024 thread *"Tailwind 4.0 not usable with any system that provides its own styles"* is still unanswered by the core team [[26]](https://github.com/tailwindlabs/tailwindcss/discussions/15466) ⭐ 96k, as is the July 2026 successor [[25]](https://github.com/tailwindlabs/tailwindcss/discussions/20306) ⭐ 96k. A 2026 explainer walks the cascade rule through generically [[37]](https://medium.com/@kazzywiz7/the-tailwind-v4-css-rule-that-silently-overrides-your-utilities-d72e185627ac).

The inversion matters for triage. Under v3 the folk wisdom was "MUI's Emotion specificity beats my utilities, add `!important`". Under v4, specificity is not the mechanism — the *layer boundary* is, and cranking specificity won't help. Most MUI+Tailwind advice online is v3-era and diagnoses the wrong cause.

### The three fixes, ranked

| Fix | How | Cost |
|-----------------------------|-----------------------------------------------------------------------------------|-----------------------------------------------------|
| **(a) Layer the third party** | `@import "lib.css" layer(lib);` + `@layer theme, base, lib, components, utilities;` [[100]](https://developer.mozilla.org/en-US/docs/Web/CSS/@import) | Clean. Needs the kit to cooperate (or be `@import`-able at all). |
| **(b) Un-layer the utilities** | Expand the import and drop `layer()` on `utilities.css` — utilities go back to specificity+source-order parity with vendor CSS [[27]](https://github.com/tailwindlabs/tailwindcss/discussions/15866) ⭐ 96k | Gives up the whole point of v4's layer model. |
| **(c) Nuke it** | `@import "tailwindcss" important;` marks all utilities `!important` (layered `!important` beats unlayered `!important`) [[28]](https://github.com/tailwindlabs/tailwindcss/discussions/17994) ⭐ 96k; per-class is now the **suffix** `bg-red-500!`, not v3's prefix `!bg-red-500` [[103]](https://tailwindcss.com/docs/styling-with-utility-classes) | Works, poisons every utility, breaks `sx`/inline overrides. |

Fix (a) is the only one a greenfield project should accept. The rest of this artifact is really the question: *does your kit make fix (a) available, and how much ceremony does it cost?*

### Preflight

Tailwind v4's reset zeroes all margins/padding, sets `box-sizing: border-box; border: 0 solid`, unstyles `h1`–`h6`, `list-style: none` on lists, `display: block` on media [[30]](https://tailwindcss.com/docs/preflight). It lives in `@layer base` — so **once a kit is in a layer above `base` (mantine, mui), preflight is a non-issue and you should not disable it**; the layer order already subsumes the conflict. Preflight only bites when the kit is unlayered, and an unlayered kit was already winning anyway. **There is no `corePlugins: { preflight: false }` in v4** — `corePlugins` is gone entirely [[29]](https://tailwindcss.com/docs/upgrade-guide). You disable preflight by expanding the import and omitting that one line [[30]](https://tailwindcss.com/docs/preflight). Every "disable preflight to fix your component library" post older than 2025 is now wrong on the mechanism *and* on the config.

Also breaking in v4 and worth knowing before you blame the kit: default border colour changed from `gray-200` to `currentColor`, placeholders are text-colour at 50%, and `button` gets `cursor: default` [[29]](https://tailwindcss.com/docs/upgrade-guide).

---

## 2. MUI: Pigment CSS is dead in the water; layers are the actual answer

### Pigment CSS status: on hold, not abandoned, not usable

The repo's own description reads *"⚠️ 𝐀𝐥𝐩𝐡𝐚 𝐩𝐡𝐚𝐬𝐞, currently, on hold"* [[1]](https://github.com/mui/pigment-css) ⭐ 1.1k. It is not archived. It is also not moving. MUI's 1 January 2026 roadmap post is unambiguous: *"Pigment CSS remains in alpha phase and is currently on hold… Pigment CSS is not being developed at the moment. While we still believe in the potential of the ideas behind it, progressing further would require a different approach."* Resources went to Base UI instead [[2]](https://mui.com/blog/2026-and-beyond/).

The release history tells the same story without the diplomacy: v0.0.30 in January 2025 → **a 16-month gap** → v0.0.31 in May 2026, a maintenance-only bump (Next.js 16 support) [[6]](https://github.com/mui/pigment-css/releases) ⭐ 1.1k. Never left `0.0.x`. The community's long-running "Status of project" discussion is the place people go to ask [[20]](https://github.com/mui/pigment-css/discussions/249) ⭐ 1.1k, and the open MUI issue *"What is the way forward for styling @ mui?"* captures the frustration: *"mui7 out last week is still sticking with emotion… no proper release / upgrade path yet for pigment"* [[7]](https://github.com/mui/material-ui/issues/45759) ⭐ 98k.

**Verdict:** treat Pigment CSS as unavailable. Do not plan around it.

### What MUI shipped instead: v9, still on Emotion

MUI **skipped v8**: v7.0.0 (Mar 2025) → **v9.0.0 (Apr 2026)** → 9.2.0 (3 Jul 2026), with no 8.x on npm at all [[4]](https://registry.npmjs.org/@mui/material) — note MUI's own January 2026 roadmap was still calling the next major "v8" [[2]](https://mui.com/blog/2026-and-beyond/). Emotion is still the engine — `@mui/styled-engine@9.1.1` hard-depends on `@emotion/cache`, `@emotion/serialize` and `@emotion/sheet` [[5]](https://registry.npmjs.org/@mui/styled-engine), and the docs still say Emotion is the default [[21]](https://mui.com/material-ui/integrations/styled-components/). The v9 launch blog lists **"Remove dependency on Emotion" under *What's next*** — i.e. not done [[3]](https://mui.com/blog/introducing-material-ui-v9/) — and the v9 migration guide contains zero styling-engine breaking changes [[13]](https://mui.com/material-ui/migration/upgrade-to-v9/). Emotion itself is maintained but slow-moving [[22]](https://github.com/emotion-js/emotion) ⭐ 18k, with downloads flat (10M → 9.1M weekly, 2023→2026, propped up by MUI) while Tailwind doubled to 12M [[18]](https://www.pkgpulse.com/guides/state-of-css-in-js-2026) *(secondary aggregator — weak evidence, directionally consistent)*.

MUI's own perf claims for v9 are modest: ~3% bundle reduction vs v7, and up to 30% faster `sx` for heavy `sx` usage [[3]](https://mui.com/blog/introducing-material-ui-v9/).

### The real MUI+Tailwind 4 story: `enableCssLayer`

MUI *did* solve the cascade problem — properly, first-party, and it's good. Issue #44700 is the origin: *"some components have higher CSS specificity than (0,1,0) so Tailwind CSS could not be used without `!important`… Tailwind v4 is using native CSS layer so Material UI won't be able to override it without a configurable layer"* [[10]](https://github.com/mui/material-ui/issues/44700) ⭐ 98k. Users were reporting plain `m-2` silently doing nothing [[24]](https://github.com/mui/material-ui/issues/45096) ⭐ 98k. Maintainer siriwatknp shipped `enableCssLayer` on `StyledEngineProvider` (merged Mar 2025, backported to v6.x) [[19]](https://github.com/mui/material-ui/pull/45428) ⭐ 98k, and MUI now has a **first-party Tailwind v4 integration page** [[8]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/):

```tsx
<StyledEngineProvider enableCssLayer>
  <GlobalStyles styles="@layer theme, base, mui, components, utilities;" />
  {/* app */}
</StyledEngineProvider>
```

Emotion can't be `@import`ed — it injects `<style>` tags at runtime — so this provider flag is the only *supported* way to get MUI into a layer (MUI got there by writing a Stylis plugin against Emotion's cache, a mechanism anyone building their own `createCache` could in principle copy). A `modularCssLayers` option goes further, splitting output into `mui.global`, `mui.components`, `mui.theme`, `mui.custom`, `mui.sx` [[9]](https://mui.com/material-ui/customization/css-layers/). MUI even ships an agent skill encoding the recipe, which additionally requires `createTheme({ cssVariables: true })` so `--mui-*` tokens map into Tailwind's `@theme` [[11]](https://github.com/mui/material-ui/blob/master/skills/material-ui-tailwind/AGENTS.md) ⭐ 98k. On the theming side, `CssVarsProvider` was folded into `ThemeProvider`; you now just pass `cssVariables: true` [[12]](https://mui.com/material-ui/customization/css-theme-variables/usage/).

### What's left to hate

1. **It's opt-in, per entry point.** Miss `enableCssLayer` on any provider (SSR cache, test harness, Storybook, a lazily-mounted portal root) and utilities silently lose again. MUI's own verification step is manual: confirm *"the layer order correctly by checking the DevTools styles tab. The mui layer should come before the utilities layer."* [[8]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/)
2. **`modularCssLayers` is a footgun on existing apps.** MUI explicitly warns that enabling it causes *"unexpected changes to the look and feel of the UI"* because theme overrides that previously lost now win [[9]](https://mui.com/material-ui/customization/css-layers/). Greenfield dodges this.
3. **The old docs are still live and now actively misleading.** `guides/interoperability` still prescribes `injectFirst`, `corePlugins: { preflight: false }` and `important: '#root'` [[23]](https://mui.com/material-ui/guides/interoperability/) — all three are dead under v4 [[29]](https://tailwindcss.com/docs/upgrade-guide). `injectFirst` only reorders `<head>`; it is **irrelevant** once layers are involved.
4. **You ship two styling systems.** Emotion's runtime + Tailwind's build output. React's own docs discourage the model: *"We don't recommend runtime `<style>` tag injection… Runtime injection forces the browser to recalculate the styles a lot more often… The first problem is not solvable"* [[108]](https://react.dev/reference/react/useInsertionEffect). One measured case study: a component at 54.3ms → 27.7ms (~48% faster) purely from removing Emotion [[107]](https://dev.to/srmagura/why-were-breaking-up-wiht-css-in-js-4g9b) *(single component, 2022 — directional, not a benchmark suite)*.
5. **Emotion has no generic layer support.** MUI got layers by writing its own Stylis plugin. If you reach for raw Emotion or styled-components anywhere else in the app, you get none of it: the Emotion request is open since Nov 2023 [[31]](https://github.com/emotion-js/emotion/issues/3134) ⭐ 18k and styled-components has the same hole [[32]](https://github.com/styled-components/styled-components/issues/3950) ⭐ 41k.

**Field reports.** A 2025 production postmortem: *"components misaligned, text sizes changed, layouts distorted… Material UI's Emotion-generated styles had higher CSS specificity, overriding Tailwind utilities even when explicitly applied"* [[35]](https://dev.to/shankarjatin/when-tailwind-breaks-in-production-how-environment-differences-material-ui-style-conflicts-1p64). The long-running community thread on MUI+Tailwind has respondents simply advising a Tailwind-native kit instead [[34]](https://github.com/tailwindlabs/tailwindcss/discussions/11464) ⭐ 96k, and 2026 comparisons frame the two as competing philosophies rather than complementary layers [[38]](https://dev.to/wafa_bergaoui/tailwind-css-vs-mui-vs-ant-design-which-one-should-you-choose-in-2026-3pjb).

**Steelman.** Infinum's frontend handbook treats coexistence as a supported, boring practice: Tailwind for layout/spacing, MUI theme for stateful styles, CSS-variables theming on the MUI side [[36]](https://infinum.com/handbook/frontend/react/tailwind/best-practices). It works. It is just the only one of the four options where "does my utility class apply?" is a question you have to keep asking.

---

## 3. shadcn/ui: no styling engine at all, which is the point

There is no cascade problem, because the components carry no CSS of their own — they are Tailwind utility classes in TSX that the CLI copies into your repo. `cn()` is literally `twMerge(clsx(inputs))` [[46]](https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/new-york-v4/lib/utils.ts) ⭐ 119k. Variants come from class-variance-authority; the Button in `main` today still imports `cva` and uses v4's `size-*` utility (`icon: "size-9"`) rather than paired `w-*`/`h-*` [[47]](https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/new-york-v4/ui/button.tsx) ⭐ 119k. No Emotion, no theme provider, no runtime. (With one 2026 asterisk — see immediately below.)

### ⚠ Correction: shadcn is no longer zero-dependency, and it *does* ship CSS

The received wisdom ("shadcn is not a dependency, it's just files you own") stopped being true in 2026. The npm package `shadcn` (v4.13.0) exports `"./tailwind.css": "./dist/tailwind.css"` [[130]](https://registry.npmjs.org/shadcn/latest), the manual-install page now tells you to `pnpm add shadcn` [[119]](https://ui.shadcn.com/docs/installation/manual), and the May 2026 changelog is explicit: *"When you run `init`, it adds `@import "shadcn/tailwind.css"` to your global CSS file"* [[129]](https://ui.shadcn.com/docs/changelog/2026-05-shadcn-eject). The real `globals.css` in shadcn's own repo carries that import [[49]](https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/app/globals.css) ⭐ 119k, and by June 2026 new primitives *ship through* the package rather than being copied [[16]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default). There is a community backlash thread — *"Why does shadcn components suddenly depend on npm i shadcn"* [[132]](https://github.com/shadcn-ui/ui/discussions/9243) ⭐ 119k.

**How bad is it for the cascade? Not bad.** The shipped file is ~16 KB and contains accordion `@keyframes`, nine `@custom-variant data-*` declarations, and a few `@utility` definitions (`no-scrollbar`, `scroll-fade`, `shimmer`) — **no colour tokens, no `:root`/`.dark` block, no component rules** [[131]](https://cdn.jsdelivr.net/npm/shadcn/dist/tailwind.css). It's Tailwind *source* (variants and utilities), not competing CSS: it compiles into Tailwind's own layers, so the unlayered-wins problem from §1 does not apply. And `shadcn eject` *"inlines shadcn/tailwind.css into your global CSS file and removes the shadcn dependency"* [[129]](https://ui.shadcn.com/docs/changelog/2026-05-shadcn-eject) — the escape hatch is one command.

So: **"shadcn ships no CSS" is now false; "shadcn ships nothing that fights Tailwind" is still true.** Only the second one was ever load-bearing.

### What Tailwind 4 changed for shadcn

`tailwind.config.js` is gone; `components.json`'s `tailwind.config` field must be left **blank** for v4 [[53]](https://ui.shadcn.com/docs/components-json). Theming moved into CSS [[39]](https://ui.shadcn.com/docs/tailwind-v4):

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";
@custom-variant dark (&:is(.dark *));
@theme inline { --color-background: var(--background); /* … */ }
```

The migration's sharp edges [[39]](https://ui.shadcn.com/docs/tailwind-v4)[[62]](https://zippystarter.com/blog/guides/migrating-tailwind3-to-tailwind4-with-shadcn):
- Colours converted **HSL → OKLCH**; you must hoist `:root`/`.dark` **out of** `@layer base` and drop the `hsl(var(--x))` wrapper, because `@theme inline` inlines the variable.
- `tailwindcss-animate` → `tw-animate-css`.
- Every primitive gained a `data-slot` attribute; `forwardRef` removed for React 19.
- Utility renames bite existing code: `shadow-sm`→`shadow-xs`, `rounded-sm`→`rounded-xs`, `ring`→`ring-3`, `outline-none`→`outline-hidden`, all `*-opacity-*` removed.

**Dependency gotcha:** you need **tailwind-merge v3** (3.6.0, May 2026) [[44]](https://github.com/dcastil/tailwind-merge) ⭐ 5.7k. v3 dropped Tailwind v3 support entirely, renamed theme scales to v4 namespaces, changed prefix syntax `'tw-'`→`'tw'` and dropped `validators.isLength` [[43]](https://github.com/dcastil/tailwind-merge/blob/main/docs/changelog/v2-to-v3-migration.md) ⭐ 5.7k. Running tailwind-merge v2 against v4 classes means conflict resolution **silently mis-resolves** — no error, just wrong classes surviving. Tailwind itself is at 4.3.2; the v3 line is frozen at 3.4.19 under `v3-lts` [[52]](https://registry.npmjs.org/tailwindcss).

**⚠ Two stale dependencies on the recommended path.** `class-variance-authority` stable is still **0.7.1, published 2024-11-26** — ~20 months old — and that's what shadcn depends on (`^0.7.1`) [[50]](https://registry.npmjs.org/class-variance-authority). Development moved to the `cva` package, still at `1.0.0-beta.7` after 2+ years of beta; the repo is alive but quiet [[65]](https://github.com/joe-bell/cva) ⭐ 6.9k. The alternative is tailwind-variants 3.2.2 (Nov 2025), which adds slots and bundles tailwind-merge [[51]](https://registry.npmjs.org/tailwind-variants). Since shadcn code lives in *your* repo, swapping cva out is a local refactor, not a fork — the copy-in model paying off.

The second is worse and less discussed: **`tw-animate-css`, now a required dependency [[119]](https://ui.shadcn.com/docs/installation/manual), is a solo project** — Wombosvideo/Luca Bosin, ⭐ 781, 90 of ~99 commits by the owner, last push Feb 2026 [[120]](https://github.com/Wombosvideo/tw-animate-css) ⭐ 781 — with **no stable release since v1.4.0 (Sep 2025)** and a breaking v2.0.0 still pending, despite ~35.5M weekly downloads [[122]](https://registry.npmjs.org/tw-animate-css). Its predecessor `tailwindcss-animate` is effectively dead (last publish Aug 2023, repo last pushed Jul 2024) [[121]](https://github.com/jamiebuilds/tailwindcss-animate) ⭐ 3k. Apply the same bus-factor scrutiny here that Mantine's 176-star Tailwind preset (§4) deserves — this one is on the *recommended* path.

### The July 2026 pivot: Base UI is now shadcn's default

*"Starting today, Base UI is the default component library in shadcn/ui… Radix is not being deprecated… Base UI is stable. It's at 1.6.0 with 6M+ weekly downloads… Projects created on shadcn/create now pick Base UI over Radix 2 to 1."* [[16]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) Base UI had been a selectable primitive since December 2025 [[88]](https://ui.shadcn.com/docs/changelog/2026-01-base-ui); `shadcn init -b radix` still keeps Radix, and every component ships for both. February 2026 had already collapsed the dozens of `@radix-ui/react-*` packages into a single `radix-ui` package via `shadcn migrate radix` [[42]](https://ui.shadcn.com/docs/changelog/2026-02-radix-ui). Radix's repo is still pushing daily [[64]](https://github.com/radix-ui/primitives) ⭐ 19k — but the governance backdrop is that **Radix was acquired by WorkOS and "updates have slowed for some components," leaving Base UI as the more actively maintained primitive layer** [[89]](https://www.greatfrontend.com/blog/top-headless-ui-libraries-for-react-in-2026). That, not stars, is the reason the default flipped.

**This collapses two of your four candidates into one path.** "shadcn/ui" and "Base UI" are no longer distinct choices on the styling axis — shadcn *is* the pre-styled Tailwind layer over Base UI. Third parties agree: Shadcnblocks switched via a one-liner in `components.json` [[91]](https://www.shadcnblocks.com/blog/introducing-base-ui-and-component-styles), and basecn.dev exists as a shadcn-shaped collection built on Base UI [[92]](https://basecn.dev/docs/get-started/migrating-from-radix-ui).

⚠ The Radix→Base UI migration is delivered as **an AI skill, not a codemod** (`pnpm dlx skills add shadcn/ui`, one commit per component) [[16]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) — because it isn't mechanical: `asChild` becomes `render`, positioning moves to `@floating-ui/react` [[97]](https://shadcnstudio.com/blog/migrate-from-radix-ui-to-base-ui/). Greenfield sidesteps this entirely by starting on Base UI.

### Vite wiring

`@tailwindcss/vite` in `vite.config`, an `@`→`./src` alias, and paths in **both** `tsconfig.json` and `tsconfig.app.json` — no PostCSS, no Tailwind config [[54]](https://ui.shadcn.com/docs/installation/vite). The commonest failure mode (styling silently broken after install on Vite + v4) is documented in discussion #6797 [[61]](https://github.com/shadcn-ui/ui/discussions/6797) ⭐ 119k. Monorepo support is Turborepo-shaped: `apps/web` + `packages/ui`, one `components.json` per workspace with matching `style`/`iconLibrary`/`baseColor` [[55]](https://ui.shadcn.com/docs/monorepo) — **Nx is not a documented target** (see §6). CLI is at 4.13.0 [[45]](https://registry.npmjs.org/shadcn); CLI v4 (Mar 2026) added `--dry-run`/`--diff`/`--view`, `shadcn info`, presets, `--monorepo`, `--base radix|base-ui`, and `registry:base` for shipping a whole design system in one install [[41]](https://ui.shadcn.com/docs/changelog/2026-03-cli-v4). Registries are decentralised, namespaced, auth-capable [[57]](https://ui.shadcn.com/docs/registry/namespace), with an MCP server exposing them to agents [[56]](https://ui.shadcn.com/docs/mcp). Full changelog: [[40]](https://ui.shadcn.com/docs/changelog).

### The honest complaints

The HN thread on the Base UI default (5 Jul 2026, 282 points, 165 comments) is a live referendum on the copy-in model [[58]](https://news.ycombinator.com/item?id=48791328):

- *"The copy paste approach may be easily modifiable but creates new problems - ie now there is an upgrade ai agent for something that should just be ticking up a version number"*
- *"The copy paste approach is just a plain bad idea"*
- *"every app that use shadcn use 100% same. I still have to figure how people differentiate their brand"*

Counterweight, from an engineer who migrated a large app off MUI: *"With MaterialUI we had to update EVERYTHING to their new APIs… With shadcn we can be selective."* [[58]](https://news.ycombinator.com/item?id=48791328) A January 2026 HN comment is the sharpest anti-shadcn take: *"The biggest mistake I did in 2025 was picking shadcn… Then I saw the radio component. Second red flag."* [[59]](https://news.ycombinator.com/item?id=46690996) On Tailwind-4-specific pain, the representative issue is the OKLCH conversion wrecking custom themes — *"The new color changes made some of my custom themed UI to be extremely ugly"*, closed as not-planned [[60]](https://github.com/shadcn-ui/ui/issues/6920) ⭐ 119k. The repo carries 2,108 open issues against 119k stars [[63]](https://github.com/shadcn-ui/ui) ⭐ 119k. It pins react 19.2.3, `@base-ui/react` 1.6.0, radix-ui ^1.4.3 [[48]](https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/package.json).

---

## 4. Mantine: solved, but the solution lives in a GitHub discussion

Latest is `@mantine/core` **9.4.1** (28 Jun 2026) [[66]](https://registry.npmjs.org/@mantine/core); 9.0.0 landed 31 Mar 2026 [[67]](https://mantine.dev/changelog/9-0-0/) and the 8→9 migration guide lists **no** breaking changes to PostCSS or cascade layers [[68]](https://mantine.dev/guides/8x-to-9x/). The styling architecture has been stable since v7 (2023).

**Architecture:** CSS Modules + CSS custom properties. `postcss-preset-mantine` supplies `light-dark()`, `rem()`/`em()` and `@mixin hover`/`smaller-than`/`larger-than` [[71]](https://mantine.dev/styles/postcss-preset/) — and it's only needed for *your own* CSS modules; Mantine's shipped CSS is pre-compiled. It's at 1.18.0, last published Jun 2025 — stable and low-churn [[72]](https://registry.npmjs.org/postcss-preset-mantine). Theming is pure CSS variables (`--mantine-color-red-6`, 10 shades per colour, `cssVariablesResolver`) [[79]](https://mantine.dev/styles/css-variables/), and the Styles API `classNames` prop targets every inner element — the seam through which Tailwind utilities get injected [[80]](https://mantine.dev/styles/styles-api/).

**Mantine cooperates with layers out of the box.** Every `@mantine/*` package ships a parallel `styles.layer.css` wrapping all rules in `@layer mantine` [[69]](https://mantine.dev/styles/mantine-styles/). The whole fix is three lines [[75]](https://github.com/orgs/mantinedev/discussions/7459) ⭐ 31k:

```css
@layer theme, base, mantine, components, utilities;
@import 'tailwindcss';
@import '@mantine/core/styles.layer.css';
```

Layer order does all the work: `mantine` sits *after* `base` (so preflight can't nuke Mantine) and *before* `utilities` (so `className="p-4"` on a Mantine Button wins). You do **not** disable preflight — layer ordering subsumes it. Mantine's own reset (`margin: 0` on body, `box-sizing: border-box`, form-element font inheritance) [[70]](https://mantine.dev/styles/global-styles/) still double-applies with preflight, but harmlessly once layered.

**⚠ There is no official "Usage with Tailwind" page on mantine.dev.** The FAQ answer is thin and predates v4: *"Usually it is enough to disable preflight to prevent global styles from affecting Mantine components"*, otherwise "follow one of the guides in the GitHub discussion" [[73]](https://help.mantine.dev/q/third-party-styles). That's a real documentation gap — the correct recipe is folklore in discussion #7459 [[75]](https://github.com/orgs/mantinedev/discussions/7459) ⭐ 31k, and the v3-era advice the FAQ still gives is the *wrong fix for the wrong cause* under v4 [[74]](https://github.com/tailwindlabs/tailwindcss/discussions/15832) ⭐ 96k.

**PostCSS vs `@tailwindcss/vite`: they compose.** This is the question most likely to worry an Nx+Vite team, and the answer is reassuring. Vite auto-applies any valid `postcss.config.*` to **all** imported CSS, independent of which Vite plugins are loaded [[105]](https://vite.dev/guide/features). So `@tailwindcss/vite` (Lightning-CSS, no PostCSS) [[106]](https://tailwindcss.com/docs/installation/using-vite) runs its own pass while your `postcss.config.cjs` with `postcss-preset-mantine` runs on your CSS modules. A user in #7459 confirms it in practice: *"Note: I'm using Vite with the `@tailwindcss/vite` plugin"* [[75]](https://github.com/orgs/mantinedev/discussions/7459) ⭐ 31k. Next.js users instead stack both in one PostCSS config [[78]](https://medium.com/@stanykhay29/how-to-set-up-next-js-with-mantine-ui-and-tailwind-css-v4-for-ssr-safe-dark-mode-dea0a1be31b0). Pick **one** Tailwind integration — `@tailwindcss/vite` *or* `@tailwindcss/postcss`, never both; the Vite install guide uses the plugin alone [[106]](https://tailwindcss.com/docs/installation/using-vite).

⚠ One caveat Tailwind itself raises: it **recommends against** combining CSS Modules with Tailwind, because each module compiles separately (50 CSS modules = 50 Tailwind runs) and modules can't see `@theme` unless you add `@reference "../app.css";` [[104]](https://tailwindcss.com/docs/compatibility). Mantine's model *is* CSS Modules. You can keep them disjoint (Mantine's modules pre-compiled, yours Tailwind-free) — but if you want Tailwind utilities *inside* your own `.module.css`, you're in the configuration Tailwind explicitly discourages.

**Community bridge:** `tailwind-preset-mantine` automates the layer order and maps Mantine tokens into Tailwind's `@theme` in one `@import` [[76]](https://github.com/Songkeys/tailwind-preset-mantine) ⭐ 176, at 4.1.0 (Jun 2026) [[77]](https://registry.npmjs.org/tailwind-preset-mantine). Actively maintained — but single-maintainer at 176 stars is a real bus-factor risk for a production admin console.

---

## 5. Base UI 1.0: zero CSS, and you write all of it

Base UI **v1.0.0 shipped 11 December 2025** with 35 unstyled components and a package rename to `@base-ui/react` [[14]](https://base-ui.com/react/overview/releases)[[82]](https://github.com/mui/base-ui/releases) ⭐ 10k. Cadence since is roughly monthly, up to 1.6.0 (Jun 2026) [[96]](https://base-ui.com/react/overview/releases/v1-6-0). InfoQ's February 2026 coverage is press lag, not the ship date [[17]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/). The team narrative checks out — *"From the creators of Radix, Material UI, and Floating UI"* [[83]](https://base-ui.com/react/overview/about), a collaboration under MUI rather than a corporate merger — and MUI has confirmed MUI Base is deprecated in its favour [[2]](https://mui.com/blog/2026-and-beyond/).

**Styling: zero CSS, confirmed.** *"Base UI components are unstyled, don't bundle CSS, and are compatible with Tailwind, CSS Modules, CSS-in-JS, or any other styling solution you prefer."* [[81]](https://base-ui.com/react/handbook/styling) Four hooks: `className` accepting a **string or a function of component state**, `style` likewise, **data attributes**, and **CSS variables**. Select alone exposes `data-popup-open`, `data-open`, `data-closed`, `data-side`, `data-align`, `data-highlighted`, `data-selected`, `data-disabled`, `data-placeholder`, `data-starting-style`, `data-ending-style`, plus positioner vars `--anchor-width`, `--available-height`, `--transform-origin` [[84]](https://base-ui.com/react/components/select). Every part takes a `render` prop (the replacement for Radix's `asChild`) [[97]](https://shadcnstudio.com/blog/migrate-from-radix-ui-to-base-ui/).

**The Tailwind 4 fit is unusually clean, and needs no plugin** [[86]](https://base-ui.com/react/overview/quick-start). Tailwind 4 supports bare boolean data variants — `data-open:`, `data-disabled:`, `data-highlighted:` map 1:1 onto Base UI's flag attributes — plus `data-[side=top]:` for valued ones [[87]](https://tailwindcss.com/docs/hover-focus-and-other-states). `--available-height` drops straight into `max-h-[var(--available-height)]`. ⚠ Caveat: base-ui.com's own component docs use **CSS Modules, not Tailwind**; only the Styling handbook page shows a Tailwind example [[81]](https://base-ui.com/react/handbook/styling)[[84]](https://base-ui.com/react/components/select).

**The cost is real and unavoidable.** You write every button, every dialog, every tooltip — no CSS whatsoever, no colour schemes, no themes, no pre-built patterns [[90]](https://tailkits.com/blog/base-ui-vs-shadcn-ui-vs-radix-ui-comparison/). Concretely: **Combobox has 26 separately styleable parts** (Root, Input, InputGroup, Chips, Chip, ChipRemove, List, Portal, Backdrop, Positioner, Popup, Arrow, Status, Empty, Collection, Row, Item, ItemIndicator, Group, GroupLabel, Separator…) [[85]](https://base-ui.com/react/components/combobox). And there is **no Table or DataGrid** in the component list at all — an admin console on bare Base UI means building the grid yourself or bolting on TanStack Table (component coverage is out of scope here; the styling *effort* is the point).

**Which is exactly why you shouldn't take Base UI bare.** The pre-styled Tailwind layer over Base UI already exists, is maintained, and is now mainstream: it's shadcn/ui [[16]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default). "Base UI vs shadcn/ui" is a false binary in July 2026 — shadcn ships the same Tailwind class layer over both primitives, and *"the components look and behave the same way. Only the underlying implementation changes."* [[88]](https://ui.shadcn.com/docs/changelog/2026-01-base-ui)

**Headless field, styling axis only.** All five ship unstyled primitives; the differentiator is maintenance [[89]](https://www.greatfrontend.com/blog/top-headless-ui-libraries-for-react-in-2026):

| Primitive        | ⭐ Stars | Health (Jul 2026)                                    |
|------------------|---------|------------------------------------------------------|
| [Base UI](https://base-ui.com)          | ⭐ 10k  | 1.6.0, monthly releases, pushed 2026-07-14 [[15]](https://github.com/mui/base-ui) |
| [Radix Primitives](https://www.radix-ui.com) | ⭐ 19k  | Still active, pushed 2026-07-13 [[64]](https://github.com/radix-ui/primitives) |
| [Headless UI](https://headlessui.com)      | ⭐ 29k  | ⚠ Last push 2026-04-13 — 3 months stale [[93]](https://github.com/tailwindlabs/headlessui) |
| [Ark UI](https://ark-ui.com)           | ⭐ 5.3k | Active, multi-framework [[94]](https://github.com/chakra-ui/ark) |
| [React Aria Components](https://react-spectrum.adobe.com/react-aria/) | ⭐ 16k | Active inside adobe/react-spectrum [[95]](https://github.com/adobe/react-spectrum) |

Developer reaction to Base UI itself is warm — *"found the primitives very pleasant to work with"* — with the sharpest HN criticism aimed at shadcn's copy-paste model, not at Base UI [[58]](https://news.ycombinator.com/item?id=48791328).

---

## 6. The Nx tax — bigger than the kit choice

This is kit-independent and it will bite on day one, so it belongs here rather than in a build-ergonomics footnote.

Tailwind 4 replaced `content: [...]` globs with automatic detection: it walks from the CWD and **ignores everything in `.gitignore`, everything in `node_modules`, and all CSS/lock/binary files** [[109]](https://tailwindcss.com/docs/detecting-classes-in-source-files). With `@tailwindcss/vite`, the scan root collapses to the app. Nx's own React guide says it outright: *"Tailwind CSS v4 automatically detects classes from source files. However, with the Vite plugin, scanning only covers the app directory"* [[110]](https://nx.dev/docs/technologies/react/guides/using-tailwind-css-in-react). The consequence for an `itenium-ui` library: **classes that appear only in `libs/**` emit zero CSS** — Nx's blog calls it *"styles defined in your packages won't be included in the final bundle, leading to missing styles and broken layouts"* [[111]](https://nx.dev/blog/setup-tailwind-4-npm-workspace). The upstream issue has been known since March 2024 [[112]](https://github.com/tailwindlabs/tailwindcss/issues/13136) ⭐ 96k and recurs constantly [[113]](https://github.com/tailwindlabs/tailwindcss/discussions/18770) ⭐ 96k, including the nastiest variant — utilities present in dev, **missing in the production build** [[114]](https://github.com/tailwindlabs/tailwindcss/discussions/17905) ⭐ 96k — and an Nx-specific thread [[115]](https://github.com/tailwindlabs/tailwindcss/discussions/15886) ⭐ 96k.

The fix is `@source`, whose paths are relative to the **CSS file**, not the CWD [[109]](https://tailwindcss.com/docs/detecting-classes-in-source-files):

```css
/* apps/admin/src/styles.css */
@import 'tailwindcss';
@source "../../../libs/ui";
@source "../../../libs/shared";
```

⚠ **Nx has decided not to solve this natively.** Discussion #29810 (open since Jan 2025; Nx 21 still scaffolded Tailwind 3.x configs) was answered in Feb 2026 by Nx core's Juri Strumpflohner: Nx will *disable* its native Tailwind integration and defer to the official Tailwind guides plus a community sync generator [[116]](https://github.com/nrwl/nx/discussions/29810) ⭐ 27k. Nx ships blog guides instead [[117]](https://nx.dev/blog/setup-tailwind-4-angular-nx-workspace) and a reference repo [[128]](https://github.com/juristr/tailwind4-vite-npm-workspaces) ⭐ 6. Hand-maintained `@source` lists rot as the graph grows; the answer is **`@juristr/nx-tailwind-sync`** (0.0.9, Feb 2026), an Nx sync generator that walks the project graph and rewrites the `@source` block from transitive deps on `nx build` [[118]](https://www.npmjs.com/package/@juristr/nx-tailwind-sync) — a *sole-maintainer, 0.0.x* package on the critical path of your build. Two further gotchas: a library must export its CSS in `package.json` (`"./styles": "./dist/styles/index.css"`) and the app must import it, or nothing applies at all [[111]](https://nx.dev/blog/setup-tailwind-4-npm-workspace); and libs using `@apply` in their own stylesheets need `@reference` [[110]](https://nx.dev/docs/technologies/react/guides/using-tailwind-css-in-react).

**This cost is identical for all four kits** — it's a Tailwind-in-a-monorepo problem, not a kit problem. But it inverts the intuition that "shadcn is the zero-config option": on Nx, *nothing* is zero-config.

### Browser floor

Tailwind 4 requires **Safari 16.4+, Chrome 111+, Firefox 128+** [[123]](https://github.com/tailwindlabs/tailwindcss/discussions/18270) ⭐ 96k, driven by `@property` (Baseline only since July 2024 [[127]](https://developer.mozilla.org/en-US/docs/Web/CSS/@property); Firefox 128 is the first Firefox to ship it [[124]](https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/128)) and `color-mix()` (Chrome 111, March 2023 [[126]](https://developer.chrome.com/blog/new-in-chrome-111); Baseline May 2023 [[125]](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/color-mix)). For an internal admin console this is normally fine — but it's the one fact that could invalidate "Tailwind 4 is non-negotiable" if the client fleet is locked to older Safari. MUI and Mantine carry no such floor on their own.

## 7. Dark mode: one toggle, three different wirings

An admin console needs a theme toggle, and this is a pure styling-engine question that the kit docs mostly duck. **Tailwind 4 has no built-in class-based dark mode** — you declare the variant yourself, against a class or a data attribute [[133]](https://tailwindcss.com/docs/dark-mode). Every kit must then be wired to the *same* signal or you get two half-working toggles.

| Kit | Signal it keys off | Wiring to share one toggle |
|---|---|---|
| **shadcn/ui** | `.dark` class on `<html>` | None needed — `@custom-variant dark (&:is(.dark *));` is plain Tailwind, and shadcn's tokens override under the same `.dark` [[141]](https://github.com/shadcn-ui/ui/discussions/6840) ⭐ 119k |
| **Base UI** | ✗ none — no CSS, no theme | Nothing to sync [[86]](https://base-ui.com/react/overview/quick-start) |
| **MUI** | `prefers-color-scheme` by default | ⚠ Must set `cssVariables: { colorSchemeSelector: 'class' }` → emits `.light`/`.dark` [[134]](https://raw.githubusercontent.com/mui/material-ui/master/docs/data/material/customization/css-theme-variables/configuration.md) ⭐ 98k; accepts `'media' \| 'class' \| 'data' \| string` [[135]](https://mui.com/system/experimental-api/css-theme-variables/); `InitColorSchemeScript`'s `attribute` must match [[136]](https://mui.com/material-ui/react-init-color-scheme-script/) |
| **Mantine** | `data-mantine-color-scheme` on `<html>`, not configurable [[139]](https://mantine.dev/theming/color-schemes/) | ⚠ Invert it — bend Tailwind to Mantine: `@custom-variant dark (&:where([data-mantine-color-scheme=dark], [data-mantine-color-scheme=dark] *));` [[140]](https://github.com/orgs/mantinedev/discussions/1672) ⭐ 31k |

⚠ **MUI's official Tailwind v4 page covers cascade layers and says nothing about dark mode** [[8]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/) — so the `colorSchemeSelector` step is a trap you find by hitting it. The symptom is on file: *"Is there any way to apply the Tailwind's `dark:` class prefix?"* [[137]](https://github.com/mui/material-ui/issues/41511) ⭐ 98k, and a toggle that fails to update `[data-mui-color-scheme]`, mis-styling everything [[138]](https://github.com/mui/material-ui/issues/38575) ⭐ 98k. Mantine's recipe is community-sourced, not on mantine.dev.

**Ranking on this axis is the same as everywhere else:** shadcn 0 steps, Base UI 0, MUI 2 (selector + init script), Mantine 1 (but you rewrite Tailwind's variant, which is the kind of thing a future dev will not expect).

## 8. Scorecard: where each kit's CSS lands

| Kit | ⭐ Stars | Ships CSS? | Where it lands in Tailwind 4's layer stack | Fix required | Runtime cost |
|---|---|---|---|---|---|
| [**shadcn/ui**](https://ui.shadcn.com) | ⭐ 119k [[63]](https://github.com/shadcn-ui/ui) | ✗ — the components *are* Tailwind classes [[47]](https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/v4/registry/new-york-v4/ui/button.tsx) ⭐ 119k | `utilities` — same layer as everything else | None | Zero |
| [**Base UI**](https://base-ui.com) | ⭐ 10k [[15]](https://github.com/mui/base-ui) | ✗ — zero CSS [[81]](https://base-ui.com/react/handbook/styling) | n/a — you own all of it | None | Zero |
| [**Mantine**](https://mantine.dev) | ⭐ 31k [[75]](https://github.com/orgs/mantinedev/discussions/7459) | ✓ CSS Modules, pre-compiled | ✗ unlayered by default → **beats utilities**; ✓ `@layer mantine` via `styles.layer.css` [[69]](https://mantine.dev/styles/mantine-styles/) | 3-line layer declaration [[75]](https://github.com/orgs/mantinedev/discussions/7459) ⭐ 31k | Zero |
| [**MUI**](https://mui.com/material-ui/) | ⭐ 98k [[7]](https://github.com/mui/material-ui/issues/45759) | ✓ Emotion, injected at runtime [[5]](https://registry.npmjs.org/@mui/styled-engine) | ✗ unlayered → **beats utilities**; ✓ `@layer mui` via `enableCssLayer` [[8]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/) | Provider flag on **every** entry point + layer string + `cssVariables: true` [[11]](https://github.com/mui/material-ui/blob/master/skills/material-ui-tailwind/AGENTS.md) ⭐ 98k | ⚠ Emotion runtime; React discourages runtime `<style>` injection [[108]](https://react.dev/reference/react/useInsertionEffect) |

Preflight is not a differentiator once layers are set up: for Mantine and MUI the kit sits above `@layer base`, so the reset loses and you leave preflight on [[30]](https://tailwindcss.com/docs/preflight). Mantine's own reset [[70]](https://mantine.dev/styles/global-styles/) double-applies harmlessly; MUI's `CssBaseline` lands in `mui.global` and likewise wins over preflight [[9]](https://mui.com/material-ui/customization/css-layers/).

**Build wiring, in one line each.** shadcn/Base UI: `@tailwindcss/vite`, no PostCSS [[54]](https://ui.shadcn.com/docs/installation/vite). Mantine: `@tailwindcss/vite` **plus** a `postcss.config.cjs` — Vite runs both [[105]](https://vite.dev/guide/features). MUI: `@tailwindcss/vite`, plus provider config in React, plus a live `<GlobalStyles>` layer declaration [[8]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/). The Vite plugin exists because it skips PostCSS: full build 378ms → 100ms, incremental-no-new-CSS 35ms → **192µs** [[101]](https://tailwindcss.com/blog/tailwindcss-v4). Tailwind v4 is itself a Lightning-CSS-based build tool that bundles `@import`, so Sass/Less/Stylus are out entirely [[104]](https://tailwindcss.com/docs/compatibility). Custom utilities are now `@utility name {}`, not `@layer utilities {}` [[102]](https://tailwindcss.com/docs/adding-custom-styles).

---

## 9. What this means for a greenfield Nx + Vite + Tailwind 4 admin console

**On the styling axis alone, shadcn/ui on Base UI is the answer.** Not because the others are broken — MUI and Mantine both have *working* Tailwind 4 recipes — but because it is the only option where the recipe is "nothing": no layer declaration, no provider flag, no colour-scheme selector, no reset negotiation.

The counterweights, honestly stated:

- **shadcn's copy-in model is genuinely contested**, and 2026 muddied it further: it now ships a real npm dependency with a real CSS file [[130]](https://registry.npmjs.org/shadcn/latest), and "upgrade" is an AI skill rather than a version bump [[58]](https://news.ycombinator.com/item?id=48791328). `shadcn eject` buys the old model back [[129]](https://ui.shadcn.com/docs/changelog/2026-05-shadcn-eject).
- **Two solo-maintained packages sit on the recommended path**: `tw-animate-css` [[120]](https://github.com/Wombosvideo/tw-animate-css) ⭐ 781 and a 20-month-stale cva [[50]](https://registry.npmjs.org/class-variance-authority). Both are replaceable locally because the code is yours — that is the copy-in model's actual dividend.
- **Base UI has no DataGrid** [[85]](https://base-ui.com/react/components/combobox), and an admin console needs one. This is the single likeliest reason to overturn the recommendation: MUI X's DataGrid is the field's strongest, and if the console leans on it you may choose to pay the `enableCssLayer` tax deliberately. (Its Pro/Premium licensing is a separate axis, out of scope here.)
- **Mantine is the strongest fallback** for batteries-included components without Emotion: zero runtime, a 3-line layer declaration, and a `classNames` Styles API that takes Tailwind utilities on every inner element [[80]](https://mantine.dev/styles/styles-api/). Its weakness is documentation, not architecture.
- **The Nx `@source` tax is unavoidable and kit-independent** [[110]](https://nx.dev/docs/technologies/react/guides/using-tailwind-css-in-react). Budget for it regardless of which kit wins.

**Do not** plan around Pigment CSS [[2]](https://mui.com/blog/2026-and-beyond/). **Do not** follow any MUI+Tailwind guide that mentions `corePlugins` or `injectFirst` [[23]](https://mui.com/material-ui/guides/interoperability/)[[29]](https://tailwindcss.com/docs/upgrade-guide). **Do** pin tailwind-merge v3 on day one [[43]](https://github.com/dcastil/tailwind-merge/blob/main/docs/changelog/v2-to-v3-migration.md), and wire `@source` before you write a single component [[109]](https://tailwindcss.com/docs/detecting-classes-in-source-files).
