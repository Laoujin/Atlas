---
title: "MUI vs shadcn/ui vs Mantine vs Base UI: the 2026 maturity and governance baseline"
date: 2026-07-14
depth: survey
format: md
topic: "Candidate profiles, maturity & governance of the four React UI component kits under evaluation for Itenium.Forge's `itenium-ui` in 2026 — MUI, shadcn/ui, Mantine, and Base UI 1.0. What each one actually IS, React 19 support, release cadence, backing organisation and funding, licensing (incl. MUI X Pro/Premium tiers), GitHub health, npm trends, and ecosystem size."
topic_raw: "Decision framework: which React UI component kit should Itenium.Forge's frontend (itenium-ui) adopt in 2026 — MUI, shadcn/ui, Mantine, or Base UI 1.0? Greenfield admin console on an Nx 21 + React 19 + Vite + Tailwind 4 monorepo, TypeScript-first"
tags: [react, ui-libraries, mui, shadcn, mantine, base-ui, governance, licensing, open-source]
summary: "The four kits are not the same category: MUI and Mantine are batteries-included libraries, shadcn/ui is a code registry, Base UI is primitives — and as of July 2026 shadcn/ui defaults to Base UI, making MUI's own primitive layer the de-facto industry standard."
citations: 31
reading_time_min: 11
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 650
issue: 7
---

> **Decision (baseline layer only).** These four are not four options in one category — they are three categories. **MUI** is a batteries-included library with a *paid* data grid: the row-grouping/aggregation/Excel-export tier an admin console actually wants costs **$599/dev/yr** [[15]](https://mui.com/pricing/). **Mantine** is the same shape but 100% MIT — with a **94% single-maintainer bus factor** [[3]](https://github.com/mantinedev/mantine) and an $18.5k/yr budget [[25]](https://opencollective.com/mantinedev). **shadcn/ui** is a code-distribution registry, not a dependency, and as of **July 2026 it initialises new projects on Base UI, not Radix** [[21]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default). **Base UI** is the primitive layer under that — MUI-staffed, built by the ex-Radix/Floating-UI team, stable since Dec 2025 [[20]](https://base-ui.com/react/overview/releases). Picking "shadcn/ui" in 2026 therefore means picking MUI's primitives with none of MUI's licensing.

## What each one actually is

| | Category | You install | You own the component code | Ships a data grid |
|---|---|---|---|---|
| [Material UI](https://mui.com) ⭐ 99k (Jul 2026) [[1]](https://github.com/mui/material-ui) | Batteries-included, styled (Material Design) | `@mui/material` runtime dep | ✗ | ✓ — but paid tiers [[16]](https://mui.com/x/introduction/licensing/) |
| [Mantine](https://mantine.dev) ⭐ 31k [[3]](https://github.com/mantinedev/mantine) | Batteries-included, styled (own design language) | `@mantine/*` runtime dep | ✗ | ✗ (no enterprise grid) |
| [shadcn/ui](https://ui.shadcn.com) ⭐ 119k [[2]](https://github.com/shadcn-ui/ui) | Code registry + CLI ("**not a component library**" [[22]](https://ui.shadcn.com/docs)) | `shadcn` CLI (devDep) → copies source in | ✓ | ✗ |
| [Base UI](https://base-ui.com) ⭐ 10k [[4]](https://github.com/mui/base-ui) | Unstyled headless primitives | `@base-ui/react` runtime dep | ✗ (but no styles to own) | ✗ |

The category collapse matters: shadcn/ui is a *delivery mechanism* whose runtime substrate is now Base UI. So "shadcn/ui vs Base UI" is not a real fork in the road — shadcn/ui is Base UI plus Tailwind styling plus a codegen CLI. The real fork is **owned code (shadcn+Base UI) vs vendored library (MUI / Mantine)**.

## The July 2026 realignment

This is the single biggest fact of the year for this decision. shadcn/ui's July 2026 changelog switched the default primitive from Radix to Base UI: `npx shadcn init` now selects Base UI; docs show Base UI examples first; Radix stays supported behind `shadcn init -b radix` and is explicitly **not deprecated** [[21]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default).

Why it happened: Radix is maintained by WorkOS post-acquisition [[5]](https://github.com/radix-ui/primitives) ⭐ 19k, and the original Radix authors left to build Base UI at MUI, alongside people from Floating UI and Material UI [[19]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/). MUI funds Base UI with dedicated engineers, designers and managers — InfoQ frames this company backing as the direct answer to post-acquisition uncertainty around Radix [[19]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/).

Net effect for Itenium.Forge: the "vendor-neutral, no-lock-in" shadcn path and the "corporate MUI" path now share a runtime maintainer. That is a *convergence*, not a conflict — but it does mean Base UI's health is now a shared risk across three of the four candidates (MUI X already depends on `@base-ui/utils` internally [[7]](https://www.npmjs.com/package/@mui/material)).

## Versions, cadence, React 19

| | Latest (14 Jul 2026) | Stable since | Cadence | React peer range | Styling engine |
|---|---|---|---|---|---|
| Material UI | **9.2.0** (3 Jul 2026) [[7]](https://www.npmjs.com/package/@mui/material) | v9 on **8 Apr 2026** [[17]](https://mui.com/blog/introducing-mui-v9/) | Monthly minors, v5/v6/v7 tags still alive | `^17 \|\| ^18 \|\| ^19` [[7]](https://www.npmjs.com/package/@mui/material) | Emotion (peer) |
| MUI X | **9.9.0** (9 Jul 2026) [[6]](https://github.com/mui/mui-x) | v9 (Apr 2026) | Weekly-to-biweekly | `^17 \|\| ^18 \|\| ^19` | Emotion via MUI |
| Mantine | **9.4.1** (28 Jun 2026) [[9]](https://www.npmjs.com/package/@mantine/core) | 9.0 on **31 Mar 2026** [[23]](https://mantine.dev/changelog/9-0-0/) | ~2-week minors | **`^19.2.0` only** [[9]](https://www.npmjs.com/package/@mantine/core) | CSS Modules + CSS vars |
| Base UI | **1.6.0** (18 Jun 2026) [[8]](https://www.npmjs.com/package/@base-ui/react) | **1.0.0 on 11 Dec 2025** [[20]](https://base-ui.com/react/overview/releases) | Monthly minors, no majors since 1.0 | `^17 \|\| ^18 \|\| ^19` [[8]](https://www.npmjs.com/package/@base-ui/react) | none (bring your own) |
| shadcn CLI | **4.13.0** (3 Jul 2026) [[10]](https://www.npmjs.com/package/shadcn) | n/a | Weekly-ish | follows your project | Tailwind |

Notes that bite:

- **Material UI skipped v8.** It went v7 → v9 to re-align its major with MUI X v9, which was already there [[17]](https://mui.com/blog/introducing-mui-v9/). Expect stale blog posts and LLM output to reference a v8 that does not exist.
- **Mantine 9 is React-19.2-or-nothing.** Its peer range is a hard `^19.2.0` — no React 18 escape hatch [[9]](https://www.npmjs.com/package/@mantine/core). Fine here (the monorepo is React 19), but it forecloses sharing components with any React 18 consumer.
- **Base UI renamed its package at 1.0**: `@base-ui-components/react` → `@base-ui/react` [[19]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/). The old scope is frozen at `1.0.0-rc.0` and still gets 400k downloads/week [[31]](https://www.npmjs.com/package/@base-ui-components/react) — a live trap for anyone copying pre-2026 snippets.
- **MUI still requires Emotion** as a peer dependency in v9 [[7]](https://www.npmjs.com/package/@mui/material). MUI's own 2026 roadmap says Emotion-independence and "better integration paths for teams using Tailwind CSS" are *future* work, and that **Pigment CSS is paused in alpha** [[18]](https://mui.com/blog/2026-and-beyond/). Take that as a commitment not yet delivered.

## Backing organisation, funding, bus factor

| | Backer | Funding model | Top contributor share | Governance risk |
|---|---|---|---|---|
| MUI / Base UI / MUI X | **MUI** (company, Paris, founded 2014, 40+ remote staff across 20+ countries) [[26]](https://mui.com/about/) | **Bootstrapped — no VC raised**; revenue from MUI X Pro/Premium licences [[27]](https://www.crunchbase.com/organization/mui-org) | `oliviertassinari` 22% (Material UI); `atomiks` 21% / `michaldudak` 11% (Base UI) [[1]](https://github.com/mui/material-ui) [[4]](https://github.com/mui/base-ui) | ⚠ Commercial pressure: free tier is the funnel for the paid grid. Products get shelved (Joy UI on hold, Toolpad unmaintained, MUI Sync dead) [[18]](https://mui.com/blog/2026-and-beyond/) |
| Mantine | **One person** — Vitaly Rtishchev [[24]](https://mantine.dev/) | Open Collective: **$18.5k/yr est. budget**, $18.4k raised total, 125 contributors [[25]](https://opencollective.com/mantinedev) | `rtivital` **94%** of top-100 contributions [[3]](https://github.com/mantinedev/mantine) | ⚠⚠ Bus factor 1, and no commercial entity behind it |
| shadcn/ui | **Vercel** — shadcn is a Vercel design engineer (joined Aug 2023); the project predates the hire and remains MIT [[28]](https://x.com/shadcn/status/1688945578439499776) [[2]](https://github.com/shadcn-ui/ui) | Vercel salary; no direct monetisation of the registry | `shadcn` **73%** of top-100 contributions [[2]](https://github.com/shadcn-ui/ui) | ⚠ Bus factor 1 on the *registry*, but ✓ near-zero on the *code you copied* — you own it |

The asymmetry is the whole point. Mantine's and shadcn's bus factors look identical on paper (one dominant human). They are not the same risk:

- If Mantine's maintainer stops, your `@mantine/core` dependency goes stale in `node_modules` and you have a fork-or-migrate problem across every screen.
- If shadcn stops, your components are **already source files in your repo**. What you lose is future registry updates and the CLI — not your app. The runtime risk transfers to Base UI, which is company-staffed.
- If MUI stops, you have neither — but MUI is a 40-person company with recurring licence revenue, so this is the least likely and most survivable.

## GitHub health (14 Jul 2026, via GitHub REST API)

| Repo | ⭐ Stars | Open issues | Opened (90d) | Closed (90d) | Backlog trend |
|---|---|---|---|---|---|
| [mantinedev/mantine](https://github.com/mantinedev/mantine) | 31k | **12** | 80 | 83 | ✓ Effectively zero-inbox |
| [mui/material-ui](https://github.com/mui/material-ui) | 99k | 1,387 | 113 | 206 | ✓ Shrinking |
| [mui/base-ui](https://github.com/mui/base-ui) | 10k | 311 | 159 | 117 | ⚠ Growing slowly (young project, post-1.0 influx) |
| [mui/mui-x](https://github.com/mui/mui-x) | 5.8k | 1,552 | — | — | ⚠ Large, but paid support is the escalation path |
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | 119k | **1,019** | 150 | **53** | ✗ Growing ~3× faster than it drains |

The star ranking and the maintenance ranking are almost inverted. shadcn/ui has the most stars of any React UI project and the worst issue-throughput ratio of the four (closes ~1 issue for every 3 opened). Mantine has a third of the stars and a **12-issue** open tracker — one person out-servicing a 119k-star project. Star count is a popularity signal, not a maintenance signal; do not let it drive this decision.

## npm downloads — and why the 2026 numbers lie

Monthly downloads, Jan 2026 → Jun 2026:

| Package | Jan 2026 | Jun 2026 | Multiple |
|---|---|---|---|
| `@mui/material` | 27.5M | **38.7M** | 1.4× [[11]](https://api.npmjs.org/downloads/point/2026-06-01:2026-06-30/@mui/material) |
| `@base-ui/react` | 1.75M | **24.9M** | **14×** [[13]](https://api.npmjs.org/downloads/point/2026-06-01:2026-06-30/@base-ui/react) |
| `shadcn` (CLI) | 3.3M | **22.1M** | 6.6× [[14]](https://api.npmjs.org/downloads/point/2026-06-01:2026-06-30/shadcn) |
| `@mantine/core` | 4.5M | **8.0M** | 1.8× [[12]](https://api.npmjs.org/downloads/point/2026-06-01:2026-06-30/@mantine/core) |
| `@radix-ui/react-dialog` (control) | 65.8M | 247M | 3.8× [[30]](https://api.npmjs.org/downloads/point/2026-06-01:2026-06-30/@radix-ui/react-dialog) |

⚠ **Read these as ratios, not as growth.** Radix's dialog primitive grew **3.8×** in five months *while being displaced as shadcn's default* — that is not adoption, that is baseline inflation (CI, mirrors, AI agents re-installing). Any absolute 2026 npm "growth" number is contaminated. What survives the noise: MUI is still the largest single library by a wide margin; Base UI outgrew everything by ~4× the inflated baseline (the shadcn default switch is doing that); Mantine grew roughly *below* baseline, i.e. it is holding, not gaining.

Survey data agrees on the shape: State of React 2025 (~2,600 respondents) puts **MUI still #1 in usage with shadcn/ui growing fast and close to overtaking it**, and notes a large share of respondents use no component library at all — the space is not settled [[29]](https://2025.stateofreact.com/en-US/libraries/component-libraries/).

## Licensing — the only hard commercial gate

Three of the four are pure MIT with nothing gated: Mantine [[3]](https://github.com/mantinedev/mantine), Base UI [[8]](https://www.npmjs.com/package/@base-ui/react), shadcn/ui [[2]](https://github.com/shadcn-ui/ui). Material UI core is MIT and "free forever" [[1]](https://github.com/mui/material-ui).

**MUI X is where the money is**, and an admin console walks straight into it [[15]](https://mui.com/pricing/) [[16]](https://mui.com/x/introduction/licensing/):

| Tier | Price/dev/yr | What you get |
|---|---|---|
| Community (MIT) | $0 | Basic Data Grid, Date Pickers, Charts, Tree View, Scheduler |
| **Pro** | **$299** | Multi-filtering, multi-sorting, column resizing, **column pinning**, date/time **range** pickers, advanced charts, tree-view drag-and-drop |
| **Premium** | **$599** | **Row grouping**, **aggregation**, **Excel export** |
| Enterprise | $1,399 | Premium + guaranteed response times, CSM; **min. 15 seats** |

Mechanics that matter for a monorepo:

- Licence is **perpetual + 12 months of maintenance**; renewals can rise up to **7%/yr** [[15]](https://mui.com/pricing/).
- Enforcement is **runtime**: `LicenseInfo.setLicenseKey()` before render. On failure the component renders a **watermark and logs a console warning in production**, not just dev [[16]](https://mui.com/x/introduction/licensing/). There is no build-time check to catch it in CI — a misconfigured env var ships a watermarked grid to users.
- Seats = concurrent developers touching front-end code that uses Pro/Premium. 30-day non-production trial without a key [[16]](https://mui.com/x/introduction/licensing/).

⚠ Practical translation for `itenium-ui`: the moment the admin console needs grouped rows or an Excel export button — table-stakes for an admin console — MUI costs **$599 × (number of front-end devs) per year, forever**. That is the single largest cost delta between the candidates, and it is the one none of the other three can charge you, because none of the other three has an enterprise grid at all. The counter-question the other angles must answer is what you pay *instead* (TanStack Table + hand-built UI, AG Grid, etc.).

## Ecosystem and community size

| | Community signals |
|---|---|
| MUI | Largest by download volume [[11]](https://api.npmjs.org/downloads/point/2026-06-01:2026-06-30/@mui/material); still #1 in State of React 2025 usage [[29]](https://2025.stateofreact.com/en-US/libraries/component-libraries/); 12 years of Stack Overflow answers (and a matching 12 years of *stale v4/v5* answers) |
| shadcn/ui | Most-starred React UI repo at 119k [[2]](https://github.com/shadcn-ui/ui); huge third-party block/template market; ships an **AI migration skill** rather than a codemod for the Base UI move [[21]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) |
| Mantine | **120+ components, 70 hooks**, 500+ contributors, 12k Discord members [[24]](https://mantine.dev/); ships `@mantine/mcp-server` for AI-agent access [[23]](https://mantine.dev/changelog/9-0-0/) |
| Base UI | **35 components at 1.0** [[19]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/), growing monthly (Drawer stable in 1.3, OTPField stable in 1.6) [[20]](https://base-ui.com/react/overview/releases); ecosystem is effectively *shadcn's* ecosystem now |

## What this baseline hands to the other angles

1. **Base UI is load-bearing for two of the four options** — it is both a standalone candidate and shadcn/ui's default runtime. Its health (10k stars, 311 open issues, MUI-funded, 7 months post-1.0) is a shared dependency, not an isolated one.
2. **MUI's Tailwind story is a roadmap item, not a shipped feature** [[18]](https://mui.com/blog/2026-and-beyond/), and Emotion is still a hard peer dep in v9 [[7]](https://www.npmjs.com/package/@mui/material) — hand this to the Tailwind-4-interop angle.
3. **Mantine is the maintenance winner and the bus-factor loser simultaneously.** Both facts are real; the risk sits entirely on one person's continued interest.
4. **The only recurring cash cost in the field is MUI X Premium at $599/dev/yr**, triggered by exactly the grid features an admin console needs — hand this to the component-coverage angle.
