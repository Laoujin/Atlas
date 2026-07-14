---
layout: expedition
title: "Which React UI component kit should itenium-ui adopt in 2026?"
date: 2026-07-14
topic: "Decision framework: which React UI component kit should Itenium.Forge's frontend (itenium-ui) adopt in 2026 — MUI, shadcn/ui, Mantine, or Base UI 1.0? Greenfield admin console on an Nx 21 + React 19 + Vite + Tailwind 4 monorepo, TypeScript-first."
format: md
tags: [react, ui-components, design-systems, tailwind, decision-framework]
summary: "Four candidates turned out to be three, then two: shadcn/ui now ships Base UI by default, so the real question is whether a Tailwind-4 monorepo should own its component code or vendor a library that must be talked out of overriding its own utilities."
cover: cover.svg
synthesis: true
citations: 16
reading_time_min: 3
children:
  - slug: candidate-profiles-maturity-governance
    title: "MUI vs shadcn/ui vs Mantine vs Base UI: the 2026 maturity and governance baseline"
    depth: survey
    status: success
    summary: "The four kits are not the same category: MUI and Mantine are batteries-included libraries, shadcn/ui is a code registry, Base UI is primitives — and as of July 2026 shadcn/ui defaults to Base UI, making MUI's own primitive layer the de-facto industry standard."
    citations: 31
    reading_time_min: 11
  - slug: styling-engine-tailwind-4-interop
    title: "Styling engine and Tailwind 4 interop: which React component kit survives the cascade"
    depth: expedition
    status: success
    summary: "Tailwind 4 puts every utility inside a cascade layer, so any kit that ships unlayered CSS silently outranks it — which reframes the MUI/shadcn/Mantine/Base UI choice as a question about where each kit's styles land in the layer stack, and surfaces a bigger Nx @source tax underneath all four."
    citations: 141
    reading_time_min: 26
  - slug: admin-console-component-coverage-the-gap-list
    title: "Admin-console component coverage: what MUI, shadcn/ui, Mantine and Base UI actually ship in 2026"
    depth: survey
    status: success
    summary: "Only Mantine covers a CRUD admin console in-box with a single gap (the data grid); MUI's coverage is real but the grid features you actually need are paywalled; shadcn now defaults to Base UI, making them one choice, not two."
    citations: 41
    reading_time_min: 9
  - slug: accessibility-headless-primitive-foundations
    title: "A11y & primitive foundations: what MUI, shadcn/ui, Mantine and Base UI actually inherit in 2026"
    depth: survey
    status: success
    summary: "shadcn-vs-Base-UI is a false dichotomy: since July 2026 shadcn/ui ships Base UI as its default primitive layer, so the real choice is which primitive foundation you inherit — and none of the four kits publishes a VPAT."
    citations: 26
    reading_time_min: 11
  - slug: theming-design-tokens-branding-reach
    title: "Theming, tokens and brand reach: MUI vs shadcn/ui vs Mantine vs Base UI in 2026"
    depth: survey
    status: success
    summary: "On a Tailwind-4 monorepo the token substrate decides the kit: shadcn/ui and Base UI put brand tokens directly in @theme, while MUI and Mantine keep a JS theme object as the source of truth and only emit CSS variables downstream."
    citations: 25
    reading_time_min: 9
  - slug: nx-21-monorepo-build-ergonomics
    title: "Nx 21 build ergonomics: which UI kit survives a shared itenium-ui library"
    depth: recon
    status: success
    summary: "shadcn/ui's copy-in model does work in a shared Nx library, but only if you own the plumbing: a components.json in the lib, a private registry for updates, and Tailwind 4 @source globs across the boundary."
    citations: 10
    reading_time_min: 3
model: "Opus 4.8"
cost_usd: "sub"
issue: 7
duration_sec: 1710
---

> **Decision.** Adopt **shadcn/ui on Base UI** for `itenium-ui`. It is the only candidate that costs nothing in cascade negotiation, nothing in token duplication, and nothing in license fees — and the three sibling decisions this series already made (TanStack Table, React Hook Form, a standalone toast) are its native idiom rather than a duplication of it. Take **Mantine** instead if the team would rather trade brand precision for 120 components it never has to write. Do not take MUI on this stack.

The four-way question collapsed while the research ran. In **July 2026 `shadcn init` began defaulting to Base UI** rather than Radix [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default), a change every one of the six angles independently rediscovered. "shadcn/ui vs Base UI 1.0" is therefore not a choice: shadcn *is* a pre-styled Tailwind layer over Base UI [[2]](https://base-ui.com/react/overview/releases), and the honest fork is **owned code vs vendored library**.

What decides that fork is the cascade. Tailwind 4 places every utility inside a named layer [[3]](https://github.com/tailwindlabs/tailwindcss/blob/main/packages/tailwindcss/index.css), and per the CSS spec unlayered author styles beat layered ones unconditionally [[4]](https://developer.mozilla.org/en-US/docs/Web/CSS/@layer). So MUI's runtime-injected Emotion CSS and Mantine's default `styles.css` both *silently outrank* the utilities you write [[5]](https://github.com/tailwindlabs/tailwindcss/discussions/20306) — a real, shipped-to-production failure mode [[6]](https://github.com/mui/material-ui/issues/45096). Both kits offer an opt-in fix (MUI's first-party `enableCssLayer` integration [[7]](https://mui.com/material-ui/integrations/tailwindcss/tailwindcss-v4/), Mantine's parallel `styles.layer.css` [[8]](https://mantine.dev/styles/mantine-styles/)), so this is a tax, not a wall. shadcn-on-Base-UI simply never levies it.

The same asymmetry reappears one level up. shadcn and Base UI put brand tokens directly in Tailwind's `@theme`, where a CSS variable *is* the token *is* the utility [[9]](https://ui.shadcn.com/docs/theming); MUI and Mantine keep a JS theme object as the source of truth and emit CSS variables downstream, leaving a hand-maintained bridge and a permanently double-defined palette. For a publishable design-system library carrying the Itenium brand, that duplication is the whole job done twice.

MUI fails on a third axis too. Emotion is still a hard dependency in v9, and **Pigment CSS — the zero-runtime escape — is officially paused in alpha** [[10]](https://mui.com/blog/2026-and-beyond/); do not plan around it. Meanwhile the grid features an admin console actually needs (row virtualisation, column pinning, grouping, Excel export) sit behind MUI X Pro/Premium at **$299–599/dev/yr** [[11]](https://mui.com/pricing/) [[12]](https://mui.com/x/introduction/licensing/) — paying to duplicate the TanStack Table this series already chose.

Two honest counterweights. Mantine is the best-maintained project in the field by a distance: **⭐ 31k against a 12-issue open tracker** [[13]](https://github.com/mantinedev/mantine), where shadcn/ui carries 1,019 and closes roughly one issue for every three opened [[14]](https://github.com/shadcn-ui/ui), and MUI has an accessibility backlog open since 2019 [[15]](https://github.com/mui/material-ui/issues/14187). Stars and maintenance health are close to inverted here. And the copy-in model has a governance cost Nx makes worse: shared-lib components need a private registry to receive updates at all, and Tailwind 4 emits **zero CSS for `libs/**` until you hand-write `@source` directives** [[16]](https://nx.dev/docs/technologies/react/guides/using-tailwind-css-in-react) — a tax that lands on all four candidates equally and is the largest single piece of plumbing in this decision.

Which leaves the sharpest open question: Base UI is now load-bearing for two of the four options *and* is maintained by MUI the company. Choosing shadcn to avoid MUI's styling engine still routes the runtime through MUI's engineers — and nobody in this field ships a VPAT.
