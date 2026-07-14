---
title: "Theming, tokens and brand reach: MUI vs shadcn/ui vs Mantine vs Base UI in 2026"
date: 2026-07-14
depth: survey
format: md
topic: "Theming, design tokens and branding reach across MUI, shadcn/ui, Mantine, and Base UI 1.0 in 2026 — how far each kit bends to a custom corporate brand before it fights back. Compare the theming models: MUI's JS createTheme object + styleOverrides/slotProps + the CSS-variables mode (cssVariables: true), shadcn/ui's plain CSS custom properties + Tailwind 4 @theme (and the shadcn theming/registry story in 2026), Mantine's MantineProvider theme object + CSS variables resolver + variantColorResolver, and Base UI's \"you own all the CSS\" position. Assess for each: dark mode implementation (class vs data-attribute vs prefers-color-scheme, SSR flash-of-wrong-theme), how a design-token pipeline (Style Dictionary, Tokens Studio, W3C DTCG format) feeds the kit, whether tokens live as CSS custom properties (interoperable with Tailwind 4's @theme) or as a JS object (not interoperable), per-component override ergonomics and their escape hatches, multi-brand/white-label support, and typed theme augmentation in TypeScript. Call out concretely where each model fights a Tailwind-4-native token setup. Anchor to 2026."
topic_raw: "Decision framework: which React UI component kit should Itenium.Forge's frontend (itenium-ui) adopt in 2026 — MUI, shadcn/ui, Mantine, or Base UI 1.0? Greenfield admin console on an Nx 21 + React 19 + Vite + Tailwind 4 monorepo, TypeScript-first"
tags: [design-tokens, theming, tailwind, react, design-systems, mui, shadcn, mantine, base-ui]
summary: "On a Tailwind-4 monorepo the token substrate decides the kit: shadcn/ui and Base UI put brand tokens directly in @theme, while MUI and Mantine keep a JS theme object as the source of truth and only emit CSS variables downstream."
citations: 25
reading_time_min: 9
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 490
issue: 7
---

> **Decision.** For a Tailwind-4-native, multi-app design system (`itenium-ui`), only **shadcn/ui** and **Base UI** make the Tailwind `@theme` block the *source of truth* for brand tokens — everything else is downstream of a JS object. Since **shadcn/ui switched its default primitive to Base UI in July 2026** [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default), the two are now the same substrate with a different amount of pre-written CSS: shadcn = Base UI + an opinionated token layer you own. **Mantine** is the strongest "batteries-included" option that still emits real CSS variables, but its token *names* are Mantine's, not yours. **MUI** bends furthest to a brand and hardest against Tailwind 4: its tokens originate in a JS `createTheme` object and only *reach* CSS variables through a hand-maintained bridge file [[2]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/).

## The one question that decides it

Tailwind 4 has no JS config. Design tokens are declared in CSS with `@theme`, and each theme variable *is simultaneously* a CSS custom property and a generated utility class — `--color-brand: #3f3cbb` produces `bg-brand`, `text-brand`, `border-brand` [[3]](https://tailwindcss.com/docs/theme). A plain `:root { --brand: … }` gets you the variable but **no utility**.

So the axis is: **where does the token live?**

| Kit | Token source of truth | Emits CSS custom props? | Generates Tailwind utilities from brand tokens? | Bridge needed |
|---|---|---|---|---|
| [shadcn/ui](https://ui.shadcn.com) ⭐ 119k | Your CSS file (`:root` + `@theme inline`) [[4]](https://ui.shadcn.com/docs/theming) | ✓ (native) | ✓ | none |
| [Base UI](https://base-ui.com) ⭐ 10.3k | Your CSS file — the kit has no theme at all [[5]](https://base-ui.com/react/handbook/styling) | ✓ (yours) | ✓ | none |
| [Mantine](https://mantine.dev) ⭐ 31.4k | JS `theme` object → resolver → CSS vars [[6]](https://mantine.dev/styles/css-variables/) | ✓ (`--mantine-*`) | ✗ (must re-declare in `@theme`) | thin, one-way |
| [Material UI](https://mui.com/material-ui/) ⭐ 98.6k | JS `createTheme` object → CSS vars when `cssVariables: true` [[7]](https://mui.com/material-ui/customization/css-theme-variables/configuration/) | ✓ (`--mui-*`, opt-in) | ✗ (must re-declare in `@theme`) | thick, hand-maintained [[2]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/) |

The "bridge" is the same trick in both directions — `@theme inline { --color-primary: var(--mui-palette-primary-main); }` [[2]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/) — but it means the brand palette is **defined twice**: once in TypeScript so the components see it, once in CSS so Tailwind can mint utilities. Drift is a matter of when, not if.

## The 2026 realignment you have to price in

- **Base UI 1.0 shipped 11 Dec 2025** with 35 accessible unstyled components and a maintenance commitment; the package renamed to `@base-ui/react` [[8]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/).
- **shadcn/ui made Base UI the default primitive in July 2026** — `npx shadcn init` picks Base UI, docs open on the Base UI tab, Radix stays supported [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default).
- **MUI paused Pigment CSS** (its zero-runtime CSS-in-JS successor) to concentrate on Base UI; Material UI v8 is still only "drafting and shaping" [[9]](https://mui.com/blog/2026-and-beyond/). Material UI's theming model in 2026 is therefore *the v7 model plus a CSS-variables mode*, not a rewrite.

Practical consequence for `itenium-ui`: **"shadcn/ui vs Base UI" is no longer a fork in the road** — it's a decision about how much of the token/CSS layer you write yourself versus adopt from shadcn's registry and then own.

## Per-kit token model

### shadcn/ui — tokens are the product
Semantic `background`/`foreground` pairs (`--primary` + `--primary-foreground`, `--card`, `--muted`, `--destructive`, `--border`, `--ring`, `--sidebar-*`, `--chart-1..5`), declared in `oklch()` under `:root` and re-declared under `.dark`, then exposed to Tailwind through `@theme inline` [[4]](https://ui.shadcn.com/docs/theming). A single `--radius` base derives `sm`/`md`/`lg`/`xl` via `calc()`. Adding a brand token is three lines: define under `:root` and `.dark`, add to `@theme inline`, get `bg-warning` for free [[4]](https://ui.shadcn.com/docs/theming).

Brand distribution is a first-class feature: a **registry item** carries `cssVars: { theme, light, dark }` plus raw `css` (`@layer base`, `@utility`, `@keyframes`), and item types `registry:theme` / `registry:style` exist specifically to ship a design system [[10]](https://ui.shadcn.com/docs/registry/registry-item-json). That is precisely the `itenium-ui` shape: a private registry publishing the Itenium token set + component set to N apps.

⚠ The escape hatch is also the tax: **you own the component source**, so a shadcn upgrade is a diff against files you have edited. Note also that shadcn now distinguishes *styles* from *themes* — "Rhea" (May 2026) is a denser style that adjusts component sizes/gaps directly rather than moving Tailwind's `--spacing` multiplier, explicitly so that `p-2` keeps meaning the same thing app-wide [[11]](https://ui.shadcn.com/docs/changelog/2026-05-rhea). That is the right instinct to copy for a corporate density mode.

### Base UI — no tokens, no theme, no opinion
`className` (string *or* a function of component state), state `data-attributes` (`[data-checked]`, `[data-open]`), a `style` prop, and a handful of *layout* CSS variables like `--available-height` / `--anchor-width` on Popover [[5]](https://base-ui.com/react/handbook/styling). There is no theme object, no dark mode, no color token — dark mode is whatever you write, e.g. Tailwind's `dark:` variant [[5]](https://base-ui.com/react/handbook/styling). Brand reach is unlimited because there is nothing to bend. Multi-brand is "whatever your CSS does". Typed theme augmentation is not a concept — your tokens are typed by whatever you build (or not at all).

### Mantine — JS theme, CSS-variable output
`MantineProvider` takes a theme object; `cssVariablesResolver: (theme) => ({ variables, light, dark })` lets you rewrite Mantine's variables and add your own, with automatic scheme switching [[6]](https://mantine.dev/styles/css-variables/). Mantine emits a broad, well-named surface: `--mantine-color-{name}-{0..9}`, `--mantine-spacing-*`, `--mantine-radius-*`, `--mantine-shadow-*`, `--mantine-font-*`, z-index layers [[6]](https://mantine.dev/styles/css-variables/).

Brand colors must be **10-shade tuples** — fewer and you get a TypeScript error [[12]](https://mantine.dev/theming/colors/). `generateColors` / `colorsTuple` synthesise the ramp from one hex, and `virtualColor({ name, light, dark })` maps one semantic name onto different ramps per scheme [[12]](https://mantine.dev/theming/colors/). `primaryShade: { light: 6, dark: 8 }` picks the shade per scheme [[12]](https://mantine.dev/theming/colors/).

The deepest brand hook is `theme.variantColorResolver` — a function returning `{ background, hover, color, border }` that governs how *every* color-aware component (Button, Badge, ActionIcon, ThemeIcon, Alert, Avatar) renders each variant, and can define entirely new variants [[13]](https://mantine.dev/styles/variants-sizes/). That is genuinely more expressive than MUI's per-component `styleOverrides` for the "our brand has a weird tertiary button" problem.

### Material UI — deepest bend, heaviest coupling
Three override layers in `createTheme`: `defaultProps`, `styleOverrides` keyed by slot with nested selectors, and a `variants: [{ props, style }]` array for prop-conditional styling; `ownerState` callbacks in `styleOverrides` are now discouraged in favour of `variants` [[14]](https://mui.com/material-ui/customization/theme-components/). Per-instance escape is `sx` and `slotProps`. Custom variants and custom palette colors require **TypeScript module augmentation** to typecheck [[14]](https://mui.com/material-ui/customization/theme-components/).

`cssVariables: true` turns the theme into `--mui-*` custom properties, auto-generates *channel tokens* for alpha compositing, lets you rename or drop the prefix via `cssVarPrefix`, and swaps runtime `palette.mode` checks for `theme.applyStyles()` [[7]](https://mui.com/material-ui/customization/css-theme-variables/configuration/). It's a real improvement — but the CSS variables are an **output**, not an input. Tailwind cannot see them until you write the bridge, and the token *names* are MUI's taxonomy (`palette.primary.main`), not DTCG's.

## Dark mode

| Kit | Mechanism | Default | SSR flash prevention | Tailwind `dark:` interop |
|---|---|---|---|---|
| shadcn/ui | `.dark` class on `<html>` [[4]](https://ui.shadcn.com/docs/theming) | class | Your job (e.g. `next-themes` / inline script) | ✓ native — Tailwind's default dark variant is class-based [[15]](https://tailwindcss.com/docs/dark-mode) |
| Base UI | none — you implement it [[5]](https://base-ui.com/react/handbook/styling) | — | Your job | ✓ by construction |
| Mantine | `data-mantine-color-scheme` on `<html>`, set by `MantineProvider` (CSR) or `ColorSchemeScript` (SSR); persisted in `localStorage` key `mantine-color-scheme` [[16]](https://mantine.dev/theming/color-schemes/) | data-attribute | ✓ `ColorSchemeScript` runs pre-hydration; Mantine names the failure mode "FART" (flash of inaccurate color scheme) and documents it [[17]](https://help.mantine.dev/q/color-scheme-flickering) | ⚠ needs `@custom-variant dark (&:where([data-mantine-color-scheme=dark], …))` [[15]](https://tailwindcss.com/docs/dark-mode) |
| Material UI | `colorSchemeSelector`: `media` (default) \| `class` (`.light`/`.dark`) \| `data` \| custom pattern (`.theme-%s`) [[7]](https://mui.com/material-ui/customization/css-theme-variables/configuration/) | `prefers-color-scheme` media query | ✓ `InitColorSchemeScript` (required for non-media selectors) + `suppressHydrationWarning` [[7]](https://mui.com/material-ui/customization/css-theme-variables/configuration/) | ✓ *if* you set `colorSchemeSelector: 'class'`; ✗ on the default media mode, where a Tailwind `dark:` class toggle and MUI's media query desynchronise |

⚠ **The MUI default is the trap.** Out of the box MUI keys dark mode off `prefers-color-scheme` while Tailwind keys off `.dark`. A user who toggles your app to dark gets Tailwind-styled surfaces flipping and MUI-styled surfaces not. Fix: `createTheme({ cssVariables: { colorSchemeSelector: 'class' } })`.

## Design-token pipeline (Style Dictionary / Tokens Studio / DTCG)

The **DTCG Format Module** is JSON with `$value` / `$type` / `$description`, `.tokens.json` files, `{group.token}` aliases and composite tokens [[18]](https://www.designtokens.org/TR/drafts/format/). It is still a Community Group draft — the June 2026 editor's draft carries an explicit "do not implement this version" preview banner [[18]](https://www.designtokens.org/TR/drafts/format/) — but tooling has converged anyway: **Style Dictionary v4 has first-class DTCG support** (`$value`/`$type` vs the legacy `value`/`type`; you may not mix the two in one instance) [[19]](https://styledictionary.com/info/dtcg/) ⭐ 4.7k.

Style Dictionary ships both output shapes: `css/variables` (a `:root` block of custom properties) and `javascript/es6` / `javascript/module` / TypeScript declarations [[20]](https://styledictionary.com/reference/hooks/formats/predefined/). So *every* kit here is technically feedable. The difference is how many hops:

| Kit | SD build target | Hops from `.tokens.json` to a themed component |
|---|---|---|
| shadcn/ui, Base UI | `css/variables` → hand-wrapped in `@theme` (or `@theme inline` over `:root`) | 1 — the CSS variable *is* the token *is* the utility [[3]](https://tailwindcss.com/docs/theme) |
| Mantine | `javascript/es6` → `createTheme()`; optionally `css/variables` → `cssVariablesResolver` | 2 — and colors must be re-shaped into 10-tuples [[12]](https://mantine.dev/theming/colors/) |
| Material UI | `javascript/es6` → `createTheme()` → `cssVariables: true` → hand-written `@theme inline` bridge | 3 — and the bridge is a second, manually maintained mapping [[2]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/) |

Tailwind 4 also gives the monorepo its distribution mechanism for free: a brand theme is a **plain CSS file** (`@theme { --color-itenium-500: …; }`) that any app `@import`s [[3]](https://tailwindcss.com/docs/theme). No JS package, no provider, no bundler coupling. For an Nx library publishing a design system, that is a materially simpler artifact than an exported `Theme` object.

## Per-component override ergonomics and escape hatches

| Kit | Global override | Per-instance | Ultimate escape hatch |
|---|---|---|---|
| shadcn/ui | Edit the component file — it's in your repo | `className` (Tailwind) | Total: rewrite the file. ⚠ upgrades become diffs [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) |
| Base UI | Your own CSS | `className` (string or state-fn), `style`, `data-*` state selectors [[5]](https://base-ui.com/react/handbook/styling) | Total: `render` prop swaps the element |
| Mantine | `theme.components.X.{defaultProps,classNames,styles,vars}`; `variantColorResolver` for *all* color-aware components at once [[13]](https://mantine.dev/styles/variants-sizes/) | `classNames`, `styles`, `variant`, `color` | High — but you're inside Mantine's class/variable naming |
| Material UI | `components.MuiX.{defaultProps, styleOverrides, variants}` [[14]](https://mui.com/material-ui/customization/theme-components/) | `sx`, `slotProps`, `slots` | Very high — `slots` replaces the rendered element entirely; ⚠ every layer is Emotion-generated CSS you then have to out-specify from Tailwind [[2]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/) |

## Multi-brand / white-label

| Kit | Mechanism | Verdict |
|---|---|---|
| shadcn/ui | Ship a `registry:theme` item per brand (`cssVars.theme/light/dark`) from a private registry [[10]](https://ui.shadcn.com/docs/registry/registry-item-json); or scope brands to a CSS class/attribute | ✓ Best fit — brand = a CSS file; runtime switching is a class swap |
| Base UI | Whatever CSS scoping you invent | ✓ Unlimited, ✗ zero help |
| Mantine | Multiple theme objects + `virtualColor` for scheme-dependent brands [[12]](https://mantine.dev/theming/colors/); `cssVariablesResolver` for per-brand variable sets [[6]](https://mantine.dev/styles/css-variables/) | ✓ Works; runtime brand swap re-renders the provider |
| Material UI | Nested `ThemeProvider`s; deep-merge theme objects manually (passing multiple args to `createTheme()` is legacy) [[21]](https://github.com/mui/material-ui/issues/28714); `THEME_ID`-based *theme scoping* exists mainly for coexisting with a second styling library, and MUI's own docs warn against it [[22]](https://mui.com/material-ui/integrations/theme-scoping/) | ⚠ Doable, but the palette-per-`colorSchemes` customisation path has open friction reports [[23]](https://github.com/mui/material-ui/issues/43508) |

## Typed theme augmentation

| Kit | How | Cost |
|---|---|---|
| Material UI | `declare module '@mui/material/styles'` for palette/typography; `declare module '@mui/material/Button'` + `ButtonPropsVariantOverrides` for each custom variant [[14]](https://mui.com/material-ui/customization/theme-components/) | Per-component augmentation files; verbose but genuinely typed |
| Mantine | `mantine.d.ts` augmenting `MantineThemeOther`, `MantineThemeColorsOverride` (`Record<ExtendedCustomColors, MantineColorsTuple>`), `MantineThemeSizesOverride` [[24]](https://mantine.dev/guides/typescript/) | Concise, one file, good autocomplete |
| shadcn/ui | ✗ none — tokens are CSS strings; type safety only over `cva`/`tv` variant props in code you own | Nothing to augment → nothing checks your token names |
| Base UI | ✗ none | Same |

⚠ This is the one axis where MUI and Mantine genuinely beat the CSS-variable kits: a typo in `--color-brnd` is a silent no-op in Tailwind, whereas `theme.colors.brnd` is a compile error. Mitigation for a CSS-first stack: generate a `.d.ts` of allowed token names from the same `.tokens.json` Style Dictionary build [[20]](https://styledictionary.com/reference/hooks/formats/predefined/), and lint class names.

## Where each model fights a Tailwind-4-native token setup

**Material UI** — three distinct fights: (1) tokens are born in JS, so Tailwind can't mint utilities from them without the hand-written `@theme inline` bridge listing every palette/typography/shadow token [[2]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/); (2) you must enable `enableCssLayer: true` and declare `@layer theme, base, mui, components, utilities;` or Tailwind utilities lose to Emotion's runtime styles [[2]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/); (3) the default `prefers-color-scheme` dark mode desyncs from Tailwind's `.dark` [[7]](https://mui.com/material-ui/customization/css-theme-variables/configuration/)[[15]](https://tailwindcss.com/docs/dark-mode).

**Mantine** — one fight, two chores: under Tailwind 4, Mantine's own styles win over Tailwind utilities unless the layer order is fixed (community-recommended `theme → base → mantine → components → utilities`), a regression relative to Tailwind 3 [[25]](https://github.com/orgs/mantinedev/discussions/7459); and `--mantine-color-*` variables must be re-declared inside `@theme` to become `bg-*` utilities. Mantine's dark mode is a `data-*` attribute, so Tailwind needs `@custom-variant dark` [[15]](https://tailwindcss.com/docs/dark-mode).

**shadcn/ui** — no fight; it *is* the Tailwind 4 token model. The only friction is the one it creates: styles vs themes vs `--spacing` scale (Rhea's density problem) [[11]](https://ui.shadcn.com/docs/changelog/2026-05-rhea).

**Base UI** — no fight; also no help.

## What this means for `itenium-ui`

A publishable Nx library carrying the Itenium brand, consumed by multiple apps, on Tailwind 4:

- **Brand tokens should be a CSS file** — `@theme` in a `libs/itenium-tokens` package, generated by Style Dictionary from `.tokens.json` [[19]](https://styledictionary.com/info/dtcg/)[[3]](https://tailwindcss.com/docs/theme). Every consuming app `@import`s it; no provider, no JS coupling.
- **shadcn/ui on Base UI** (its 2026 default [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default)) means one primitive layer, tokens in the currency your build already speaks, and a registry mechanism designed for exactly the "ship a branded component set to N apps" job [[10]](https://ui.shadcn.com/docs/registry/registry-item-json).
- **Mantine** is the fallback if the team wants a theme object and a large component set out of the box and will accept duplicating the token names into `@theme` plus a layer-order fix [[25]](https://github.com/orgs/mantinedev/discussions/7459).
- **MUI** buys the deepest per-component override surface and the best TypeScript story, at the price of a permanently double-maintained token definition and a cascade you have to keep negotiating with [[2]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/).
