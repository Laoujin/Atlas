---
title: "A11y & primitive foundations: what MUI, shadcn/ui, Mantine and Base UI actually inherit in 2026"
date: 2026-07-14
depth: survey
format: md
topic: "Accessibility and headless primitive foundations under the four React UI component kits in 2026 — MUI, shadcn/ui, Mantine, and Base UI 1.0. Map the primitive layer each kit sits on and what that inherits: Base UI 1.0 (the MUI-team successor to Radix-style primitives, and its relationship to both Radix and MUI Core), Radix UI primitives and their maintenance status in 2026, Ark UI, and React Aria / React Spectrum as the accessibility gold standard to benchmark against. What does shadcn/ui actually inherit — and has shadcn migrated any of its registry from Radix to Base UI? What do MUI and Mantine implement themselves? Then assess evidence of real accessibility quality per kit: WCAG 2.1/2.2 AA conformance claims and third-party audits, WAI-ARIA APG pattern conformance, keyboard navigation and focus management, screen-reader testing evidence, open a11y bug backlogs, and any VPAT/ACR documentation. Distinguish vendor claims from independent evidence."
topic_raw: "Decision framework: which React UI component kit should Itenium.Forge's frontend (itenium-ui) adopt in 2026 — MUI, shadcn/ui, Mantine, or Base UI 1.0? Greenfield admin console on an Nx 21 + React 19 + Vite + Tailwind 4 monorepo, TypeScript-first"
tags: [react, accessibility, wcag, headless-ui, base-ui, radix, shadcn, mui, mantine, react-aria, design-systems]
summary: "shadcn-vs-Base-UI is a false dichotomy: since July 2026 shadcn/ui ships Base UI as its default primitive layer, so the real choice is which primitive foundation you inherit — and none of the four kits publishes a VPAT."
citations: 26
reading_time_min: 11
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 440
issue: 7
---

> **Decision.** "shadcn/ui **vs** Base UI" is not a real choice: since **July 2026, Base UI is the default primitive layer in shadcn/ui**, with Radix kept as a supported `-b radix` opt-out and every component shipped for both [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default). So the a11y question collapses to *which primitive layer* you inherit — and there the ranking on **evidence** (not marketing) is: React Aria ≫ Base UI ≈ Radix > Mantine (self-implemented, VoiceOver-only manual testing) > MUI Core (largest a11y backlog, no compliance doc since 2019) [[10]](https://react-aria.adobe.com/quality)[[11]](https://help.mantine.dev/q/are-mantine-components-accessible)[[13]](https://github.com/mui/material-ui/issues/14187). ⚠ **No kit here ships a VPAT/ACR.** If itenium-ui ever faces procurement or EAA scrutiny, you audit it yourself regardless of which you pick.

## The primitive layer map

The kits are not peers. Two of them are *primitives*, one is a *copy-in registry over primitives*, and two *implement everything themselves*.

| Kit | Primitive layer | Who wrote the a11y behaviour | Stars | Weekly npm |
|---|---|---|---|---|
| [shadcn/ui](https://ui.shadcn.com) | **Base UI (default since Jul 2026)**; Radix via `-b radix` [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) | Base UI or Radix team — *not* shadcn | ⭐ 119k [[5]](https://github.com/shadcn-ui/ui) | n/a (copy-in) |
| [Base UI](https://base-ui.com) | *is* the primitive layer | ex-Radix + Floating UI + MUI engineers [[2]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/) | ⭐ 10.3k [[3]](https://github.com/mui/base-ui) | 6.2M (`@base-ui/react`) [[20]](https://www.npmjs.com/package/@base-ui/react) |
| [Material UI](https://mui.com/material-ui/) | **none** — self-implemented (deps: Popper, transition-group, no Base UI, no Radix) [[21]](https://www.npmjs.com/package/@mui/material) | MUI Core team | ⭐ 98.6k [[9]](https://github.com/mui/material-ui) | 7.8M [[21]](https://www.npmjs.com/package/@mui/material) |
| [Mantine](https://mantine.dev) | **none** — self-implemented (deps: only `@floating-ui/react` + `react-remove-scroll`) [[22]](https://www.npmjs.com/package/@mantine/core) | Mantine team | ⭐ 31.4k [[6]](https://github.com/mantinedev/mantine) | 1.6M [[22]](https://www.npmjs.com/package/@mantine/core) |
| [Radix Primitives](https://www.radix-ui.com/primitives) | *is* the primitive layer | Modulz → WorkOS [[4]](https://github.com/radix-ui/primitives) | ⭐ 19.1k [[4]](https://github.com/radix-ui/primitives) | 10.2M (`radix-ui`) + 66.8M (`react-dialog`) [[18]](https://www.npmjs.com/package/radix-ui) |
| [React Aria](https://react-aria.adobe.com) | *is* the primitive layer (benchmark) | Adobe [[10]](https://react-aria.adobe.com/quality) | ⭐ 15.7k [[7]](https://github.com/adobe/react-spectrum) | 7.4M (`react-aria`) [[19]](https://www.npmjs.com/package/react-aria) |
| [Ark UI](https://ark-ui.com) | Zag.js finite state machines [[24]](https://ark-ui.com/docs/overview/about) | Chakra team | ⭐ 5.3k [[8]](https://github.com/chakra-ui/ark) | 0.93M [[24]](https://ark-ui.com/docs/overview/about) |

**The load-bearing consequence:** picking shadcn/ui buys you **zero** first-party accessibility engineering. Every ARIA role, roving tabindex, focus trap and screen-reader announcement in a shadcn component comes from Base UI or Radix. What shadcn adds is *styling* — and that layer is where its a11y regressions actually live (see the audit below).

## Base UI 1.0: what it is and isn't

- Shipped stable **11 Dec 2025**, 35 accessible components, package renamed `@base-ui-components/react` → `@base-ui/react` [[2]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/). At **1.6.0** (18 Jun 2026) [[20]](https://www.npmjs.com/package/@base-ui/react).
- Built by engineers from **Radix, Floating UI, and Material UI**, but a maintainer explicitly rejects the "successor" framing: the Radix-similar API exists *"to communicate that it's easy to migrate from Radix to Base UI due to the API similarity"* [[2]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/).
- **Base UI is not "MUI Core, headless."** Material UI v9.2 has no `@base-ui` dependency at all [[21]](https://www.npmjs.com/package/@mui/material). MUI's own 2026 roadmap says *new* components (NumberField, MenuBar, PreviewCard) are being built on Base UI primitives — it is **not** a rebuild of Material UI on top of Base UI [[16]](https://mui.com/blog/2026-and-beyond/). Adopting Material UI today gives you none of Base UI's a11y work.
- Backed by *"MUI, a company with engineers, designers, and managers dedicated to the project"* — the strongest institutional-maintenance claim in this set [[2]](https://www.infoq.com/news/2026/02/baseui-v1-accessible/).

### Base UI's own a11y claims (vendor, unverified)
- *"Base UI components adhere to the WAI-ARIA Authoring Practices to provide basic keyboard accessibility out of the box."* [[12]](https://base-ui.com/react/overview/accessibility)
- *"Base UI components manage focus automatically following a user interaction."* [[12]](https://base-ui.com/react/overview/accessibility)
- *"tested on a broad spectrum of browsers, devices, platforms, screen readers, and environments"* — ⚠ **no named screen-reader/browser matrix, no WCAG conformance level claimed** [[12]](https://base-ui.com/react/overview/accessibility). Contrast with React Aria below.
- Open a11y-labelled issues: **7** [[3]](https://github.com/mui/base-ui) — small, but the library is also young.

## Is Radix stalled in 2026? No — but it's second fiddle

The "Radix is abandoned" narrative is **stale**. Evidence:

| Signal | Reading |
|---|---|
| `radix-ui` **1.6.2** published 6 Jul 2026; 1.6.3-rc as of 13 Jul 2026 [[18]](https://www.npmjs.com/package/radix-ui) | Actively released, weekly cadence |
| Repo pushed 13 Jul 2026; README still *"Maintained by @workos"* [[4]](https://github.com/radix-ui/primitives) | WorkOS stewardship intact post-Modulz acquisition |
| Chance Strickland (WorkOS) publicly the maintainer, Nov 2025 podcast [[17]](https://softwareengineeringdaily.com/2025/11/18/radix-ui-with-chance-strickland/) | Named human owner |
| 66.8M weekly downloads on `@radix-ui/react-dialog` alone [[18]](https://www.npmjs.com/package/radix-ui) | Enormous installed base; won't rot quietly |
| ⚠ *"Radix UI was acquired by WorkOS and updates have slowed for some complex components"* (Combobox, multi-select), while Base UI is *"iterating faster"* [[14]](https://www.greatfrontend.com/blog/top-headless-ui-libraries-for-react-in-2026) | Alive, but the frontier moved |
| ⚠ shadcn now defaults to Base UI; new shadcn projects pick Base UI over Radix **2:1** [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) | Mindshare has flipped |

**Verdict:** Radix is maintained, not stalled — but it is no longer where the primitive ecosystem's momentum is. Choosing Radix in a greenfield 2026 project is a defensible conservative bet, not a forward one.

## Independent accessibility evidence (the part vendors don't publish)

This is where the kits separate. Vendor claims are cheap; here is what third parties actually found.

### shadcn/ui — the styling layer *undoes* the primitive's work
A July-2026 audit by Gaurav Guha (TheFrontKit) tested the shadcn registry (Apr 2026 snapshot) with **VoiceOver/Safari, NVDA/Firefox, axe DevTools, Lighthouse, WAVE** [[15]](https://thefrontkit.com/blogs/shadcn-ui-accessibility-audit-2026). ⚠ It's a real methodology but doubles as marketing for the author's paid kit — treat the counts as indicative, not authoritative.

- **34 / 48** components pass WCAG 2.2 AA out of the box; **9** need minor fixes; **5** have gaps that *"will fail a real procurement audit"* [[15]](https://thefrontkit.com/blogs/shadcn-ui-accessibility-audit-2026).
- The headline finding is the one that matters for a Tailwind 4 project: *"The default `Button` uses `focus-visible:ring-ring/50` which renders the focus indicator at 50% opacity. In light mode against a white background, the resulting contrast ratio is **2.4:1** — below the WCAG AA threshold of 3:1 for non-text contrast."* [[15]](https://thefrontkit.com/blogs/shadcn-ui-accessibility-audit-2026)
- Five components with real gaps: **Combobox** (missing ARIA), **Data Table** (no caption/row announcements), **Context Menu**, **Chart** (Recharts SVG → empty `<svg>` to screen readers, WCAG 1.1.1 fail), **Input OTP** (paste breaks announcements) [[15]](https://thefrontkit.com/blogs/shadcn-ui-accessibility-audit-2026).

→ **This is inherited by the copy, not the dependency.** Because shadcn code lands *in your repo*, these defaults become **your** WCAG failures, and switching to the Base UI variant does not fix them — the failing `ring-ring/50` and the Recharts wrapper are shadcn's Tailwind layer, not Radix's or Base UI's. Budget an a11y sweep of the copied components on day one.

### Radix — a documented, unresolved 35-issue audit
Publicis Sapient's **Accessibility Center of Excellence** audited Radix across **VoiceOver/Safari (macOS+iOS), NVDA/Firefox, TalkBack/Chrome** and reported **35 accessibility issues** in `radix-ui/primitives#2317` — filed Aug 2023, **still open** [[23]](https://github.com/radix-ui/primitives/issues/2317). Radix's public a11y-titled open-issue count sits at **10** [[4]](https://github.com/radix-ui/primitives). The audit issue's persistence is the single best-documented independent a11y signal in this whole comparison — and it's an unflattering one.

### React Aria — the only one with a published test matrix
The benchmark, and the only library naming what it tests against [[10]](https://react-aria.adobe.com/quality):

| Screen reader | Platform / browser |
|---|---|
| VoiceOver | macOS — Safari, Chrome |
| JAWS | Windows — Firefox, Chrome |
| NVDA | Windows — Firefox, Chrome |
| VoiceOver | iOS |
| TalkBack | Android — Chrome |

Independent framing: React Aria is *"the most accessibility-rigorous option in this list"* [[14]](https://www.greatfrontend.com/blog/top-headless-ui-libraries-for-react-in-2026). ⚠ Even Adobe does **not** claim a WCAG conformance level or publish a React-Spectrum VPAT — the docs merely say WCAG *"is a good resource to reference"*, and they warn that *"automated accessibility testing tools sometimes catch false positives in React Aria"* [[10]](https://react-aria.adobe.com/quality). Its 33 open a11y-labelled issues [[7]](https://github.com/adobe/react-spectrum) reflect *scrutiny*, not weakness.

### Mantine — self-implemented, honest, thinly tested
Vendor claim [[11]](https://help.mantine.dev/q/are-mantine-components-accessible):
- *"All components that have interactive elements are tested with axe (jest-axe)"* — automated only.
- *"Mantine components are manually tested with screen readers (VoiceOver)"* — ⚠ **VoiceOver only. No NVDA, no JAWS.** That is the gap versus React Aria's five-way matrix.
- Explicit disclaimer: *"While Mantine components provide a solid foundation for accessible applications, there are still things that you need to do."*
- **0** open a11y-titled issues [[6]](https://github.com/mantinedev/mantine) and only 35 open issues total — a genuinely tidy backlog, but with no third-party audit on record it's an absence of evidence, not evidence of absence.

Mantine builds **all** widget behaviour itself on just Floating UI + `react-remove-scroll` [[22]](https://www.npmjs.com/package/@mantine/core). That means its focus traps, roving tabindex and ARIA wiring are a small team's work, unaudited externally.

### MUI Core — the weakest evidence, the biggest backlog
- **88 open accessibility-labelled issues** on `mui/material-ui` [[9]](https://github.com/mui/material-ui) — by far the largest a11y backlog in the set (Base UI: 7, Radix: 10, shadcn: 6, Mantine: 0, React Spectrum: 33).
- Conformance is a **goal, not a claim**: MUI docs say *"Level AA exceeds the basic criteria for accessibility and is a common target for most organizations, so this is what we aim to support."* [[25]](https://mui.com/x/react-tree-view/accessibility/) — aspiration, per-component, with no library-wide statement.
- The request for ADA/WCAG compliance documentation (`material-ui#14187`) has been **open since January 2019** with no maintainer position and no VPAT [[13]](https://github.com/mui/material-ui/issues/14187).
- ⚠ And MUI's 2026 engineering attention is on **Base UI**, not on Material UI's a11y debt [[16]](https://mui.com/blog/2026-and-beyond/).

## Scorecard

| | Named SR test matrix | 3rd-party audit on record | WCAG level claimed | VPAT/ACR | Open a11y issues |
|---|---|---|---|---|---|
| **React Aria** (benchmark) | ✓ 5 combos [[10]](https://react-aria.adobe.com/quality) | ✗ | ✗ ("reference") | ✗ | 33 [[7]](https://github.com/adobe/react-spectrum) |
| **Base UI** | ✗ ("broad spectrum") [[12]](https://base-ui.com/react/overview/accessibility) | ✗ | ✗ (APG adherence only) | ✗ | 7 [[3]](https://github.com/mui/base-ui) |
| **Radix** | ✗ | ✓ 35 issues, **unresolved** [[23]](https://github.com/radix-ui/primitives/issues/2317) | ✗ | ✗ | 10 [[4]](https://github.com/radix-ui/primitives) |
| **shadcn/ui** | ✗ (inherits) | ✓ 34/48 pass; focus ring 2.4:1 [[15]](https://thefrontkit.com/blogs/shadcn-ui-accessibility-audit-2026) | ✗ | ✗ | 6 [[5]](https://github.com/shadcn-ui/ui) |
| **Mantine** | ⚠ VoiceOver only [[11]](https://help.mantine.dev/q/are-mantine-components-accessible) | ✗ | ✗ (WAI-ARIA "guidelines") | ✗ | 0 [[6]](https://github.com/mantinedev/mantine) |
| **MUI Core** | ✗ | ✗ | ⚠ "aim to support" AA [[25]](https://mui.com/x/react-tree-view/accessibility/) | ✗ (open since 2019) [[13]](https://github.com/mui/material-ui/issues/14187) | 88 [[9]](https://github.com/mui/material-ui) |
| **Ark UI** | ✗ | ✗ | ✗ | ✗ | 12 total [[8]](https://github.com/chakra-ui/ark) |

**Nobody publishes a VPAT.** Adobe publishes ACRs for *products*, not for the React Aria library [[10]](https://react-aria.adobe.com/quality). If itenium-ui needs an ACR, you produce it — the kit choice only changes how much remediation precedes it.

## Ark UI, briefly

45+ headless components across React/Vue/Solid/Svelte, every component backed by a **Zag.js finite state machine** [[24]](https://ark-ui.com/docs/overview/about). Architecturally the most rigorous *behaviour* model (illegal states unrepresentable), and the only real multi-framework option. But ⭐ 5.3k and 0.93M weekly downloads [[8]](https://github.com/chakra-ui/ark)[[24]](https://ark-ui.com/docs/overview/about) — ~7× smaller than Base UI, ~11× smaller than Radix. No independent a11y evidence found. For a single-framework React admin console it buys nothing Base UI doesn't, at a fraction of the ecosystem.

## What this means for itenium-ui

1. **Don't frame it as shadcn *or* Base UI.** `shadcn init` (default) *is* shadcn-on-Base-UI as of July 2026, with a `-b radix` escape hatch and a component-by-component migration skill in the CLI [[1]](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default). Base UI docs landed in shadcn in Jan 2026 and every component was rebuilt for both libraries [[26]](https://ui.shadcn.com/docs/changelog/2026-01-base-ui).
2. **Whatever you pick, the focus-visible ring is your first bug.** shadcn's default `ring-ring/50` at 2.4:1 fails WCAG 1.4.11 in light themes [[15]](https://thefrontkit.com/blogs/shadcn-ui-accessibility-audit-2026). This is a Tailwind-token fix, not a primitive fix — and it lives in *your* repo the moment you copy the component in.
3. **Avoid shadcn's `Chart` (Recharts) if a11y matters.** No accessible alternative to the SVG; WCAG 1.1.1 fail out of the box [[15]](https://thefrontkit.com/blogs/shadcn-ui-accessibility-audit-2026). Admin consoles are chart-heavy — plan a table fallback.
4. **If a11y is a hard requirement (EAA, public-sector, enterprise procurement), React Aria Components is the only library whose testing you can actually inspect** [[10]](https://react-aria.adobe.com/quality). It is not one of your four candidates, but it is the honest benchmark — and it's a legitimate fifth option under a Tailwind design layer.
5. **MUI Core is the weakest a11y bet of the four** on evidence: 88 open a11y issues, no compliance documentation in 7 years, and a vendor whose 2026 attention is elsewhere [[9]](https://github.com/mui/material-ui)[[13]](https://github.com/mui/material-ui/issues/14187)[[16]](https://mui.com/blog/2026-and-beyond/). Its a11y is *probably* fine in practice from sheer usage volume — but "probably fine" is not an audit.
