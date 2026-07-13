---
layout: expedition
title: "React toast notifications in 2026: the landscape, the a11y bill, and the server boundary"
date: 2026-07-13
topic: "Survey the React toast-notification landscape in 2026 and recommend what to reach for: the shortlist (Sonner, react-toastify, react-hot-toast, notistack, design-system natives), accessibility, Next.js App Router / RSC integration, headless primitives, and migration off legacy toastr."
format: md
tags: [react, toast, notifications, frontend, accessibility]
summary: "Sonner won the ecosystem on distribution, not merit — it is the right default, but it is polite-only, its repo is the quietest of the group, and no library solves the server boundary for you."
cover: cover.svg
synthesis: true
children:
  - slug: library-landscape-head-to-head
    title: "React toast libraries in 2026: Sonner, react-toastify, react-hot-toast, notistack and the design-system natives"
    depth: survey
    status: success
    summary: "Sonner is the 2026 default (41M weekly installs, shadcn's toast); react-toastify is the actively-released power option; react-hot-toast is the 4.7 kB minimalist; notistack is legacy."
    citations: 41
    reading_time_min: 10
  - slug: accessibility-of-toasts
    title: "Accessible toasts in React (2026): what's actually required, and which libraries deliver"
    depth: survey
    status: success
    summary: "No React toast library is accessible out of the box: the correct pattern is a pre-mounted live region plus a landmark hotkey, and only Base UI, React Aria and Radix implement it — Sonner is polite-only, react-hot-toast is unreachable by keyboard, notistack fires role=alert into a node that mounts with its own text."
    citations: 32
    reading_time_min: 12
  - slug: next-js-app-router-rsc-server-actions
    title: "Toasts in the Next.js App Router: firing client state from the server"
    depth: survey
    status: success
    summary: "No toast library ships a server entrypoint — the queue always lives in client memory, so an RSC app must serialize server-origin toasts through an action return value or a cookie; redirect() forecloses the first option."
    citations: 25
    reading_time_min: 13
  - slug: headless-primitives-vs-batteries-included
    title: "Headless toast primitives vs batteries-included: when rolling your own pays"
    depth: recon
    status: success
    summary: "Base UI Toast is the only primitive that is both stable and feature-complete in 2026; adopt Sonner unless multi-framework, deep theming, or anchored/custom-queue needs force a primitive."
    citations: 9
    reading_time_min: 2
  - slug: migrating-off-toastr-react-toastify
    title: "Migrating off legacy toasts: toastr and react-toastify → Sonner"
    depth: recon
    status: success
    summary: "toastr is dead (last commit 2018, needs jQuery) — migrate. react-toastify is alive (v11.1.0, Apr 2026) — don't churn a working integration."
    citations: 12
    reading_time_min: 3
model: "Opus 4.8"
cost_usd: "sub"
issue: 3
duration_sec: 724
---

The literal question — "is `toastr` still a thing?" — has a one-word answer: no. It last shipped in December 2017, its final commit was June 2018, and it still hard-depends on jQuery [[1]](https://registry.npmjs.org/toastr). Everything interesting is in what replaced it, and there the five angles disagree in a way worth naming.

**Distribution decided this category, not merit.** Sonner has ~41M weekly installs against react-toastify's ~4M [[2]](https://www.npmjs.com/package/sonner) — a 10× gap that is not a 10× quality gap. It exists because shadcn/ui deprecated its own Radix-based toast and now tells every user to install Sonner instead [[3]](https://ui.shadcn.com/docs/components/radix/sonner). One default in one scaffolding tool moved the whole ecosystem, and it took Radix Toast down with it: still shipping fixes as of June 2026, but abandoned by its largest consumer and slowing post-acquisition [[4]](https://www.radix-ui.com/primitives/docs/overview/releases).

**The health signal inverts the install count.** The most-installed library has the quietest repo — Sonner's last release was August 2025 — while react-toastify shipped v11.1.0 in April 2026 with CSP-nonce support and a React 19 fix [[5]](https://github.com/fkhadra/react-toastify/releases). Install count here is a lagging indicator of one scaffolding decision, not of maintenance.

**And popularity bought a real accessibility bill.** Sonner is polite-only: there is no `assertive` path in its source, so `toast.error()` never interrupts a screen reader, and it auto-dismisses at 4 s by default — which is a plain WCAG 2.2 SC 2.2.1 failure unless the user can extend it [[6]](https://www.w3.org/WAI/WCAG22/Understanding/timing-adjustable.html). The libraries that get the model right — a live region mounted *before* the message arrives [[7]](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/alert_role), a non-modal dialog for the buttons, a landmark hotkey to reach it — are Base UI and React Aria, i.e. the two nobody installs. That is the sharpest contradiction in this expedition: the recommended default and the accessible default are different libraries.

**Nobody solves the server boundary.** All three major libraries ship `"use client"` at the top of their dist bundle, so `<Toaster />` drops into an App Router layout unchanged — but none exposes a server-callable queue [[8]](https://react.dev/reference/rsc/use-client). "RSC-compatible" is table stakes and means less than it sounds: a server mutation can only *describe* a toast and hand it across, and if the action calls `redirect()` the caller unmounts before any return value arrives [[9]](https://nextjs.org/docs/app/api-reference/functions/redirect), forcing a flash-cookie round trip. React Router 7 has had `session.flash()` for this all along [[10]](https://reactrouter.com/explanation/sessions-and-cookies).

So: take Sonner, and know what you are buying. If you ship to a public sector or enterprise a11y bar, budget for the fixes — or build on [Base UI Toast](https://base-ui.com/react/components/toast), stable since December 2025 [[11]](https://base-ui.com/react/overview/releases), and write the CSS yourself. The unclosed gap is that in 2026 no React toast library offers both the ergonomics and the correct announcement model, and the W3C is still arguing about whether SC 2.2.1 even applies to toasts — issue open since 2019 [[12]](https://github.com/w3c/wcag/issues/976).
