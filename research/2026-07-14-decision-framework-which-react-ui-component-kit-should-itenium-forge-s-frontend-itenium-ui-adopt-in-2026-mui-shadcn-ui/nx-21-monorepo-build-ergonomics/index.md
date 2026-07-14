---
title: "Nx 21 build ergonomics: which UI kit survives a shared itenium-ui library"
date: 2026-07-14
depth: recon
format: md
topic: "Nx 21 monorepo and build ergonomics for the four React UI component kits in 2026 — MUI, shadcn/ui, Mantine, and Base UI 1.0 — inside a Vite + React 19 + Tailwind 4 workspace where itenium-ui is a publishable/buildable library shared by multiple apps"
topic_raw: "Decision framework: which React UI component kit should Itenium.Forge's frontend (itenium-ui) adopt in 2026 — MUI, shadcn/ui, Mantine, or Base UI 1.0? Greenfield admin console on an Nx 21 + React 19 + Vite + Tailwind 4 monorepo, TypeScript-first"
tags: [nx, react, vite, tailwind, shadcn, mui, mantine, base-ui, monorepo, bundle-size]
summary: "shadcn/ui's copy-in model does work in a shared Nx library, but only if you own the plumbing: a components.json in the lib, a private registry for updates, and Tailwind 4 @source globs across the boundary."
citations: 10
reading_time_min: 3
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 201
issue: 7
---

> **Decision.** shadcn/ui in a shared Nx lib works — but the CLI is app-shaped, so you buy it with plumbing: `components.json` inside `libs/itenium-ui`, Tailwind 4 `@source` globs pointing at the lib, and a **private registry** as the update channel, since copy-in has no `npm update` [[1]](https://ui.shadcn.com/docs/monorepo)[[2]](https://pustelto.com/blog/adding-shadcnui-to-nx-monorepo/)[[5]](https://ui.shadcn.com/docs/registry). If you won't own that plumbing, Mantine is the low-friction default (CSS Modules, no Emotion runtime). MUI is the only option that actively fights a Vite + Nx setup [[6]](https://mui.com/material-ui/guides/minimizing-bundle-size/).

## The copy-in question (the one that matters)

The shadcn CLI *is* monorepo-aware: it reads a `components.json` per workspace and routes base components into the shared package while blocks land in the app [[1]](https://ui.shadcn.com/docs/monorepo). But the documented setup is **Turborepo + pnpm workspaces**; Nx is never mentioned. In practice you hit three things [[2]](https://pustelto.com/blog/adding-shadcnui-to-nx-monorepo/):

1. `shadcn init` fails against Nx's root layout — you must point it at the base config (`TS_NODE_PROJECT=tsconfig.base.json`).
2. Generated components import each other via path aliases, which **Nx's `enforce-module-boundaries` lint rule flags** even though the build is fine.
3. Tailwind 4 does not scan across the package boundary by default — the app's CSS must `@source` the lib, or components render unstyled. This exact failure is an open-ish thread on the shadcn repo for Nx + Tailwind v4 [[3]](https://github.com/shadcn-ui/ui/issues/7828) ⭐ 119k.

Two workarounds exist: `@nx-extend/shadcn-ui`, a generator that supports Nx ≥ 21 and writes components into a lib [[4]](https://www.npmjs.com/package/@nx-extend/shadcn-ui); or a **custom registry** — your own `registry.json` served privately, which the CLI can `add` from. That inverts the model: `itenium-ui` becomes the registry, apps consume it as a normal Nx lib, and upstream shadcn changes are pulled in deliberately rather than diffed by hand [[5]](https://ui.shadcn.com/docs/registry).

⚠ Copy-in never gives you semver. Updates are re-runs of `add` over a dirty tree. That is the real cost, not the CLI paths.

## Build / bundle behaviour

| Kit | Runtime CSS cost | Nx/Vite friction | RSC / SSR |
|---|---|---|---|
| [shadcn/ui](https://ui.shadcn.com) ⭐ 119k | none (Tailwind 4) | CLI is app-shaped; boundary lint noise [[2]](https://pustelto.com/blog/adding-shadcnui-to-nx-monorepo/) | ✓ (source in your repo) |
| [Base UI](https://base-ui.com) ⭐ 10k | none (unstyled) | lowest — plain ESM deps | ✓ |
| [Mantine](https://mantine.dev) ⭐ 31k | CSS Modules, zero-runtime since v7 | none | ✓ no `use client` for styling [[8]](https://www.pkgpulse.com/guides/state-of-css-in-js-2026) |
| [MUI](https://mui.com) ⭐ 99k | Emotion runtime (~21 kB min just for `@emotion/react`) [[7]](https://mantine.dev/styles/emotion/) | barrel imports slow Vite dev/rebuilds; icons up to **6× slower** via named imports [[6]](https://mui.com/material-ui/guides/minimizing-bundle-size/) | needs `use client` |

MUI's fix is not a bundler plugin — it's discipline: deep path imports (`@mui/material/Button`) enforced by `no-restricted-imports` with `^@mui/[^/]+$` [[6]](https://mui.com/material-ui/guides/minimizing-bundle-size/). Production tree-shaking is fine; the tax is dev-server cold start and rebuild time, paid on every app in the workspace.

## TypeScript & caching

Nx 21 recommends **package-manager workspaces + TS project references** over `tsconfig.base.json` paths for buildable/publishable libs: typecheck memory 6.14 GB → 945 MB, cached typecheck 186 s → 25 s [[9]](https://nx.dev/docs/concepts/typescript-project-linking). All four kits work under this, but the copy-in kits (shadcn, Base UI) put *source* inside `itenium-ui`, so every component edit invalidates the lib's Nx cache entry and rebuilds every dependent app. Mantine/MUI keep that surface in `node_modules` — smaller cache blast radius, at the price of not owning the code.

**Convergence note:** as of July 2026 `shadcn init` defaults to **Base UI**, not Radix [[10]](https://www.shadcndeck.com/blog/radix-vs-base-ui). The shadcn-vs-Base-UI axis is now "do I want the copy-in layer on top", not two different primitive libraries.
