---
title: "React i18n in 2026: framework & runtime fit (React 19, RSC, Vite vs Next.js)"
date: 2026-07-15
depth: standard
format: md
topic: "Framework & runtime fit for React i18n in 2026 — how react-i18next, FormatJS/react-intl, Lingui, next-intl, Paraglide, and typesafe-i18n fit React 19, Vite SPAs, and the Next.js App Router / RSC, covering SSR, hydration, bundle size, tree-shaking, and lazy-loaded locale chunks."
topic_raw: "react dependencies which i18n to use for translations in 2026"
tags: [react, i18n, nextjs, vite, rsc, bundle-size, react-19]
summary: "next-intl or Lingui for the Next.js App Router; Paraglide or react-i18next for a Vite SPA — the split is compile-time (tree-shakeable) vs runtime-dictionary architecture."
citations: 19
reading_time_min: 6
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 284
issue: 9
---

> **Decision.** The runtime dictates the choice more than features do.
> - **Next.js App Router / RSC** → [next-intl](https://next-intl.dev) (purpose-built, `getTranslations` in async Server Components, no `use client`) [[4]](https://next-intl.dev/docs/getting-started/app-router) or [Lingui](https://lingui.dev) (same `Trans`/`useLingui` in server + client) [[8]](https://lingui.dev/tutorials/react-rsc).
> - **Vite SPA, smallest bundle** → [Paraglide](https://paraglidejs.com) — compile-time functions, tree-shaken per message, ~1 KB/locale vs i18next's 205–422 KB [[7]](https://paraglidejs.com/benchmark)[[14]](https://dropanote.de/en/blog/20250726-why-i-replaced-i18next-with-paraglide-js/).
> - **Vite SPA, maturity + ecosystem** → [react-i18next](https://react.i18next.com) — largest plugin ecosystem, but a runtime-dictionary library that ships every message in a namespace [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/).
> - **Rich ICU (plurals/dates/currency), any runtime** → [react-intl/FormatJS](https://formatjs.github.io/) — most complete `Intl` support, but the heaviest (~20 KB+) and RSC needs `use client` [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/)[[10]](https://github.com/formatjs/formatjs).

The 2026 field splits cleanly into two architectures. **Runtime-dictionary** libraries (react-i18next, react-intl) load a JSON/ICU catalog and resolve keys through a lookup layer at runtime — flexible, ecosystem-rich, but the bundle scales with the catalog and RSC needs workarounds. **Compile-time** libraries (Paraglide, Lingui, typesafe-i18n) emit typed functions ahead of time, so unused messages tree-shake away and Server Components call plain functions with no React context [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/)[[7]](https://paraglidejs.com/benchmark). React 19 itself is a non-issue — all six work with it; the real differentiators are RSC, bundle, and lazy-loading.

## react-i18next / i18next

[react-i18next](https://react.i18next.com) ⭐ 10k [[18]](https://github.com/i18next/react-i18next) (core [i18next](https://www.i18next.com) ⭐ 8.6k) is the default runtime-dictionary choice and the largest ecosystem. Client bundle is ~6 KB gzipped, plus every message in the loaded namespace [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/). SSR is mature and documented for both Node and static export [[13]](https://react.i18next.com/latest/ssr).

The friction is RSC: `useTranslation` depends on React context, which Server Components don't have, so App Router usage requires the `createInstance` pattern (or the `next-i18next` v16 wrapper offering `getT()` for server + `useT()` for client) [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/)[[2]](https://github.com/i18next/react-i18next/issues/1616). ⚠ For new App Router projects this is a shim, not a native fit [[3]](https://better-i18n.com/en/blog/nextjs-app-router-i18n-server-components/). Lazy-loading works via `i18next-http-backend` or manual dynamic `import()` of locale JSON — effective but you own the discipline of namespace splitting [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/)[[11]](https://simplelocalize.io/blog/posts/lazy-loading-resources/). **Best fit: Vite SPA and Pages Router.**

## react-intl / FormatJS

[react-intl](https://formatjs.github.io/docs/react-intl/) ⭐ 15k [[10]](https://github.com/formatjs/formatjs) has the most complete ICU MessageFormat and `Intl` support (plurals, dates, numbers, currency, relative time) and is the highest-starred repo here. That completeness costs bundle: ~20 KB+ gzipped with the full ICU runtime, the heaviest option, and it grows with ICU complexity [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/)[[15]](https://intlayer.org/blog/react-i18next-vs-react-intl-vs-intlayer).

RSC support is limited: the hook-based API needs `use client`, though `@formatjs/intl` is usable server-side [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/). It works well with Vite; lazy-loading is manual — dynamic-import the active locale's messages and pass them straight to `IntlProvider`, so the initial bundle carries one locale and others load as chunks [[11]](https://simplelocalize.io/blog/posts/lazy-loading-resources/). **Best fit: apps that genuinely need rich ICU formatting and can absorb the weight.**

## Lingui

[Lingui](https://lingui.dev) ⭐ 5.8k [[9]](https://github.com/lingui/js-lingui) is a compile-time library with a runtime around ~3 KB; a macro extracts messages so unused ones tree-shake [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/). Its standout property for 2026: the **same `Trans` and `useLingui` work identically in Server and Client Components**. On the server `useLingui` is a plain function reading a per-request `I18n` instance from React `cache`, not a hook [[8]](https://lingui.dev/tutorials/react-rsc).

RSC setup has sharp edges: configure the `linguiMacroSwcPlugin` under `experimental.swcPlugins`, and ⚠ call `setI18n()` in **every page and layout** (not just the root) because of how the App Router preserves state; static rendering needs `generateStaticParams` for all locales [[8]](https://lingui.dev/tutorials/react-rsc). Framework-agnostic, so it also fits a Vite SPA. **Best fit: teams wanting one API across RSC + client, willing to wire the macro.**

## next-intl

[next-intl](https://next-intl.dev) ⭐ 4.3k [[5]](https://github.com/amannn/next-intl) is purpose-built for the Next.js App Router and the cleanest RSC story: async Server Components use the awaitable `getTranslations`, Client Components use the `useTranslations` hook, with a request-scoped config object providing per-request locale — **no `use client` needed for server translations** [[4]](https://next-intl.dev/docs/getting-started/app-router). Bundle is ~4 KB client, and a server-only path with ahead-of-time compilation drops to ~457 B [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/). Messages load per-locale and can come from local files or a remote source [[4]](https://next-intl.dev/docs/getting-started/app-router).

The catch is scope: ⚠ it targets Next.js and is **not designed for a standalone Vite SPA** — the docs make no mention of non-Next.js usage [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/)[[4]](https://next-intl.dev/docs/getting-started/app-router). One operational note: the file-based default assumes locale files live in the repo, so translation updates ride code deployments unless you wire a remote source [[3]](https://better-i18n.com/en/blog/nextjs-app-router-i18n-server-components/). **Best fit: Next.js App Router — the reference choice.**

## Paraglide

[Paraglide](https://paraglidejs.com) ([opral/paraglide-js](https://github.com/opral/paraglide-js) ⭐ 567) [[6]](https://github.com/opral/paraglide-js) is the most aggressive compile-time approach: it compiles each message into a typed ESM function before ship, so Vite tree-shakes unused translations, keys autocomplete, and components call functions (`welcome_message()`) instead of resolving strings through a runtime layer [[7]](https://paraglidejs.com/benchmark). Because messages are pure functions with no context, RSC and SSR "just work" [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/).

Bundle is the headline: the benchmark ships **47–144 KB where i18next ships 205–422 KB**, and — critically — Paraglide's size stays flat (47 KB) as the catalog grows 200→1000 messages while i18next climbs to 414 KB, because only *used* messages ship [[7]](https://paraglidejs.com/benchmark). A real migration reported dropping ~40 KB of i18next to ~2 KB, with the only downside being TypeScript type-checking lagging when adding many keys quickly [[14]](https://dropanote.de/en/blog/20250726-why-i-replaced-i18next-with-paraglide-js/). Works across React, Next.js, SvelteKit and Vite [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/). **Best fit: Vite SPA where bundle size is the priority.**

## typesafe-i18n

[typesafe-i18n](https://typesafe-i18n.pages.dev/) ([codingcommons/typesafe-i18n](https://github.com/codingcommons/typesafe-i18n) ⭐ 2.5k) [[12]](https://github.com/codingcommons/typesafe-i18n) is codegen-first: a generator emits plain TypeScript functions with parameter-level type checking, so the shipped runtime is ~1 KB, RSC-safe (no context), and lazy-loads via generated per-locale imports [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/). ⚠ Momentum is the concern — the last major release was 2023 and it's effectively single-maintainer, so the community and Stack Overflow corpus are thin versus react-i18next [[12]](https://github.com/codingcommons/typesafe-i18n)[[19]](https://gundogmuseray.medium.com/the-definitive-guide-to-i18n-libraries-for-next-js-react-in-2026-8102c7f68a77). **Best fit: TypeScript Vite SPA teams valuing codegen + strict param checking, accepting slower upstream.**

## Comparison

| Library | ⭐ Stars | React 19 | RSC-native | SSR | Lazy-load locales | Client bundle |
|-----------------|---------|:--------:|:----------:|:---:|-------------------|---------------------------------------|
| react-i18next   | ⭐ 10k  | ✓ | ⚠ `createInstance`/wrapper | ✓ | ✓ manual (http-backend / `import()`) | ~6 KB + full namespace [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/) |
| react-intl      | ⭐ 15k  | ✓ | ⚠ needs `use client`      | ✓ | ⚠ manual dynamic import              | ~20 KB+ (ICU runtime) [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/) |
| Lingui          | ⭐ 5.8k | ✓ | ✓ (React `cache`)          | ✓ | ✓ compiled catalogs                  | ~3 KB + catalog [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/)[[8]](https://lingui.dev/tutorials/react-rsc) |
| next-intl       | ⭐ 4.3k | ✓ | ✓ `getTranslations`        | ✓ | ✓ per-locale (AOT server)            | ~4 KB / 457 B server-only [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/) |
| Paraglide       | ⭐ 567  | ✓ | ✓ pure functions           | ✓ | ✓ compile-time tree-shake            | ~1 KB/locale; 47–144 KB total [[7]](https://paraglidejs.com/benchmark) |
| typesafe-i18n   | ⭐ 2.5k | ✓ | ✓ plain TS functions       | ✓ | ✓ codegen import                     | ~1 KB + codegen [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/) |

Notes: RSC-native ✓ = usable in Server Components without `use client`; ⚠ = works but needs a workaround. In the App Router, RSC output is final HTML with **no hydration step** for server-rendered strings, so server-resolved translations ship zero translation JS — the reason RSC-native libraries win on payload [[3]](https://better-i18n.com/en/blog/nextjs-app-router-i18n-server-components/)[[16]](https://react.dev/reference/rsc/server-components).

## Guidance by runtime

**Vite SPA.** No RSC, so the axis is bundle + DX. Everything is client-side and hydrates normally. [Paraglide](https://paraglidejs.com) gives the smallest, catalog-independent bundle via compile-time tree-shaking [[7]](https://paraglidejs.com/benchmark); [react-i18next](https://react.i18next.com) gives the deepest ecosystem if you'll manage namespace splitting yourself [[1]](https://simplelocalize.io/blog/posts/the-most-popular-react-localization-libraries/); [typesafe-i18n](https://typesafe-i18n.pages.dev/) if you want codegen type-safety. Vite handles the dynamic-`import()` locale-chunk pattern natively, so lazy-loading works with all of them [[11]](https://simplelocalize.io/blog/posts/lazy-loading-resources/). Skip next-intl — it isn't built for standalone Vite [[4]](https://next-intl.dev/docs/getting-started/app-router).

**Next.js App Router.** RSC is the default in Next.js 16 and the production-standard architecture, so pick an RSC-native library to avoid `use client` bloat and ship translated HTML with no client translation payload [[3]](https://better-i18n.com/en/blog/nextjs-app-router-i18n-server-components/). [next-intl](https://next-intl.dev) is the reference choice (async `getTranslations`, request-scoped config, server-only 457 B path) [[4]](https://next-intl.dev/docs/getting-started/app-router). [Lingui](https://lingui.dev) is the alternative when you want one identical API across server + client and are fine wiring the SWC macro and per-layout `setI18n()` [[8]](https://lingui.dev/tutorials/react-rsc). Reserve react-i18next/`next-i18next` for migrating an existing Pages Router app, not greenfield [[2]](https://github.com/i18next/react-i18next/issues/1616)[[3]](https://better-i18n.com/en/blog/nextjs-app-router-i18n-server-components/). If you run Next.js as a pure client SPA (no server), the RSC advantage disappears and the Vite guidance applies [[17]](https://nextjs.org/docs/app/guides/single-page-applications).
