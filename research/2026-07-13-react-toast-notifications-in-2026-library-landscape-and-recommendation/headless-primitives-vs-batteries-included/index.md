---
title: "Headless toast primitives vs batteries-included: when rolling your own pays"
date: 2026-07-13
depth: recon
format: md
topic: "Headless toast primitives vs batteries-included toast libraries in React (2026) — when is rolling your own on a primitive worth it? Cover the primitive layer: Base UI Toast, Radix UI Toast (and its maintenance status), Ark UI / Zag.js toast, and React Aria toast hooks. Compare against Sonner / react-toastify: what you get for free vs what you must build."
topic_raw: "react toastr 2026"
tags: [react, toast, design-systems, headless-ui, accessibility]
summary: "Base UI Toast is the only primitive that is both stable and feature-complete in 2026; adopt Sonner unless multi-framework, deep theming, or anchored/custom-queue needs force a primitive."
citations: 9
reading_time_min: 2
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 226
issue: 3
---

> **Decision.** Default to [Sonner](https://sonner.emilkowal.ski/) ⭐ 12.6k (Jul 2026) — [shadcn/ui deprecated its own Radix-based toast and now tells you to use Sonner instead](https://ui.shadcn.com/docs/components/radix/toast) [[1]](https://ui.shadcn.com/docs/components/radix/toast). Build on a primitive **only** if one of the four conditions below holds — and if so, the primitive is [Base UI Toast](https://base-ui.com/react/components/toast) ⭐ 10.3k, stable since [1.0 on 11 Dec 2025](https://base-ui.com/react/overview/releases) [[2]](https://base-ui.com/react/overview/releases), or [Zag.js](https://zagjs.com/components/react/toast) / Ark UI if you ship to more than one framework [[3]](https://zagjs.com/components/react/toast).

## The primitive layer, ranked

| Primitive | Status (Jul 2026) | Free out of the box | You still build |
|---|---|---|---|
| [Base UI Toast](https://base-ui.com/react/components/toast) ⭐ 10.3k | Stable (1.0 Dec 2025, v1.6.0 Jun 2026) [[2]](https://base-ui.com/react/overview/releases) | Swipe-to-dismiss, hover/focus timer pause, stacking + limit, `aria-live` priority, F6 landmark focus, `promise()` / `update()` by id [[4]](https://base-ui.com/react/components/toast) | All CSS, animations, dismiss-button UI, per-type styling, collision boundaries [[4]](https://base-ui.com/react/components/toast) |
| [Zag.js / Ark UI](https://ark-ui.com/) ⭐ 5.2k / ⭐ 5.3k | Active, React + Vue + Solid + Svelte parity | Priority queue with `max`, pause on hover/focus/**page idle**, screen-reader wiring, `toaster.promise()` [[3]](https://zagjs.com/components/react/toast) | Same as above; swipe not documented [[3]](https://zagjs.com/components/react/toast) |
| [Radix Toast](https://www.radix-ui.com/primitives/docs/components/toast) ⭐ 19.1k | ⚠ Alive but a dead end — still shipping (30 Jun 2026 release fixed a Toast close-timer memory leak) [[5]](https://www.radix-ui.com/primitives/docs/overview/releases), yet post-WorkOS-acquisition "update velocity has slowed" and Base UI "is now the more actively maintained primitive layer" [[6]](https://www.greatfrontend.com/blog/top-headless-ui-libraries-for-react-in-2026) — and its biggest consumer dropped it [[1]](https://ui.shadcn.com/docs/components/radix/toast) | Don't start here in 2026 |
| [React Aria Toast](https://react-aria.adobe.com/Toast) ⭐ 15.7k | ✗ Still **alpha**; maintainer: "we just haven't had priority for it" [[7]](https://github.com/adobe/react-spectrum/discussions/9058) | Best-in-class a11y semantics | Everything else, on an unstable API |

Base UI is the credible successor by construction: it's built by "the creators of Radix, Material UI, and Floating UI" — Colm Tuite (Radix) included [[8]](https://base-ui.com/react/overview/about).

## What you actually pay

The hard parts — ARIA politeness levels, the queue state machine, hover-pause timers, swipe gestures, focus restoration — are **not** what you save by taking Sonner. Base UI ships all of them [[4]](https://base-ui.com/react/components/toast). What Sonner buys you is the *unglamorous* half: viewport CSS, enter/exit transitions, stack offsets, close-button markup, per-type variants. That's a day of work, not a week — and you'd write most of it anyway to hit your tokens.

## Decision rule — go primitive if ≥1 holds

1. **Multi-framework design system** → Zag.js/Ark, the only option with React/Vue/Solid/Svelte parity from one machine [[3]](https://zagjs.com/components/react/toast).
2. **Deep theming is a recurring cost.** Overriding Sonner means nullifying utility classes, and with `unstyled` "some internal elements are not directly reachable" [[9]](https://github.com/emilkowalski/sonner/issues/632).
3. **You already standardised on Base UI** elsewhere → one a11y vendor, one motion system, zero extra bundle.
4. **Anchored toasts or custom queue semantics** (positioner + arrow, priority ordering, upsert-by-id) that Sonner doesn't expose [[4]](https://base-ui.com/react/components/toast).

None of the four? Ship Sonner. A hand-rolled toast is a permanent a11y liability for a component users see for four seconds.
