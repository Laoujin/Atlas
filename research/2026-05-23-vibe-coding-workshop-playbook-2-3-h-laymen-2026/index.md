---
layout: expedition
title: "Vibe coding workshop playbook (2-3 h, laymen, 2026)"
date: 2026-05-23
topic: "Design a complete playbook for running a 2-3 hour vibe coding workshop in 2026 that lets laymen ship a small working app, covering app ideas, tool stack on shared wifi, the ChatGPT-refine → Lovable-build prompting workflow, take-home deployment paths, and facilitation logistics."
format: md
tags: [vibe-coding, workshop, lovable, chatgpt, playbook]
summary: "A facilitator's full playbook for a 2-3 h vibe coding workshop: shortlist of laymen-shippable apps, a Lovable/Bolt stack costed in EUR for shared wifi, a ChatGPT-refine → Lovable-build prompting drill, and a take-home path that survives the two-week tail."
cover: cover.svg
synthesis: true
children:
  - slug: workshop-scale-app-ideas-for-laymen
    title: "Workshop-scale app ideas for laymen"
    depth: deep
    status: success
    summary: "Five reliable app-idea menus that a non-developer can ship in 2-3 hours with an AI builder, plus the failure modes to swap out."
    citations: 58
    reading_time_min: 16
  - slug: vibe-coding-tool-stack-on-shared-wifi-low-budget
    title: "Vibe-coding tool stack on shared wifi, low budget"
    depth: deep
    status: success
    summary: "Lovable as the default with Bolt.new as the backup, hosted hotspot for wifi, $0–$50 host spend for 20 attendees, and signup done the night before."
    citations: 76
    reading_time_min: 11
  - slug: prompting-workflow-chatgpt-refine-lovable-build
    title: "Prompting workflow: ChatGPT-refine → Lovable-build"
    depth: standard
    status: success
    summary: "A two-step workshop recipe — plan a structured PRD in ChatGPT (free, no credits burned), then paste it once into Lovable's Agent mode to seed the build."
    citations: 17
    reading_time_min: 7
  - slug: take-home-deployment-for-non-technical-participants
    title: "Take-home deployment for non-technical participants"
    depth: deep
    status: success
    summary: "Picking the workshop deploy stack that survives the two-week tail — the deploy click is solved; database pauses, credit caps, and auth rot are what break the app after participants go home."
    citations: 74
    reading_time_min: 10
  - slug: facilitation-logistics-and-failure-modes
    title: "Facilitation logistics and failure modes"
    depth: ceo
    status: success
    summary: "The pre-flight checklist, room/tool fallbacks, and the failure modes that actually sink 2-3 hour vibe coding workshops."
    citations: 7
    reading_time_min: 2
cost_usd: 31.26
duration_sec: 2831
citations: 232
reading_time_min: 46
---

> **One-page playbook.** Lock scope to *one screen, one user, no auth, localStorage-or-bundled-cloud* [[1]](https://www.dyad.sh/blog/vibe-coding-project-ideas) [[2]](https://calvinjku.medium.com/it-took-me-three-months-to-vibe-code-a-simple-pomodoro-app-a5bd57eee144). Default tool is **[Lovable](https://lovable.dev)** with **[Bolt.new](https://bolt.new)** as the warm backup [[3]](https://designlab.com/blog/best-vibe-coding-tools) [[4]](https://lovable.dev/guides/bolt-vs-replit-vs-lovable). Spend 30 min refining a PRD in ChatGPT (free, no credits burned), then paste once into Lovable Agent mode [[5]](https://docs.lovable.dev/tips-tricks/chatgpt-app) [[6]](https://docs.lovable.dev/prompting/prompting-one). Sign-ups happen 24-48 h *before* the room, off the venue wifi, with a phone hotspot in reserve [[7]](https://www.craftamplify.com/ai-frontend-coding/prep) [[8]](https://wifit.net/wifi-and-internet-solutions-for-hackathons/). Take-home failures are not the deploy click — they are **the Supabase 7-day pause** [[9]](https://supabase.com/pricing) and **OAuth refresh-token expiry on day 8** [[10]](https://nango.dev/blog/google-oauth-invalid-grant-token-has-been-expired-or-revoked/); the printed take-home card should pre-empt both. Host budget for 20 attendees: ~€0 free-path, ~€23 (≈$25) comfort-path with one shared Lovable Pro seat [[11]](https://lovable.dev/pricing).

## The cross-cutting picks

Across the four research angles, four decisions repeat — they are the spine of the workshop:

1. **Scope is the lever, not the tool.** The [app-ideas survey](workshop-scale-app-ideas-for-laymen/) and [tool-stack survey](vibe-coding-tool-stack-on-shared-wifi-low-budget/) independently land on the same constraint: marketplaces, OAuth login, payments, native iOS, and real-time multiplayer all blow the 2-3 h budget regardless of which builder you pick [[12]](https://www.sharetribe.com/academy/can-you-vibe-code-a-marketplace/) [[13]](https://medium.com/@a_kill_/pt-1-2-vibe-coding-my-way-to-the-app-store-539d90accc45). Cut to a single-user, single-screen rectangle and the builder choice almost stops mattering [[14]](https://justinmckelvey.com/blog/vibe-coding-examples).

2. **Lovable + Bolt is the redundant pair.** Lovable wins on "looks done" and SSR-light bandwidth [[15]](https://lovable.dev/faq/deployment/rendering); Bolt wins on signup friction and walk-in attendees [[16]](https://www.nocode.mba/articles/bolt-ai-new-guide). They fail in opposite ways too — Lovable has logged 314+ outages since May 2025 [[17]](https://statusgator.com/services/lovable), Bolt's WebContainers break on ad-blockers, VPNs, and non-Chromium browsers [[18]](https://support.bolt.new/faqs/troubleshooting/webcontainer). Keep both warm.

3. **Plan in ChatGPT, build in Lovable — physical separation enforces the rule.** Lovable's free tier is 5 daily / 30 monthly credits [[19]](https://docs.lovable.dev/introduction/plans-and-credits) — a 20-person cohort has ~600/month to share, ~2/attendee for a landing page and ~0.5 per surgical edit [[20]](https://www.banani.co/blog/lovable-pricing-and-credits). Refining in ChatGPT first is *free* and pre-empts the "vague prompt → vague app → debug-loop credit burn" cycle [[5]](https://docs.lovable.dev/tips-tricks/chatgpt-app). Drill Lovable's edit template — *"Change [X] to [Y]. Keep [everything else]."* — and the three-strike rule (revert after two failed corrections) [[6]](https://docs.lovable.dev/prompting/prompting-one) [[21]](https://www.lowcode.agency/blog/lovable-prompting-guide).

4. **The take-home card is the most under-built artifact.** Every child page touches this and the conclusion converges: the URL exists at minute 145, but [Supabase pauses after 7 days of DB inactivity](take-home-deployment-for-non-technical-participants/) [[9]](https://supabase.com/pricing), Google OAuth refresh tokens die after 7 days in Testing mode [[10]](https://nango.dev/blog/google-oauth-invalid-grant-token-has-been-expired-or-revoked/), and Lovable apps regularly leak API keys baked into the JS bundle [[22]](https://vibe-eval.com/safety/lovable/). Bundled clouds (Bolt Cloud, Lovable Cloud) sidestep the SQLite-on-Vercel data-loss trap [[23]](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel) [[24]](https://bolt.new/blog/bolt-cloud) — but the printed card still needs the "if it says paused, click resume; data is safe" sentence [[25]](https://aiagencyplus.com/keep-your-supabase-free-tier-project-live-past-the-limit/).

## Where the angles pull against each other

The deploy angle and the tool angle disagree on the *default*. The [tool stack research](vibe-coding-tool-stack-on-shared-wifi-low-budget/) puts Lovable first on workshop-day UX (chat-only, polished output, classroom track) [[26]](https://imagilabs.com/pages/lovable-imagi-hour-of-ai); the [take-home deployment research](take-home-deployment-for-non-technical-participants/) puts Bolt.new + Bolt Cloud first on the *two-month* horizon (1M tokens/month, no sleep, bundled DB, no card) [[27]](https://www.getaiperks.com/en/ai/bolt-new-free-tier-guide) [[24]](https://bolt.new/blog/bolt-cloud). Resolution: use Lovable in-room for the planning-to-build UX win, but pick the bundled-cloud path inside Lovable (Lovable Cloud auto-pauses on $0 rather than going broken [[28]](https://docs.lovable.dev/integrations/cloud)) — and reserve Bolt + Bolt Cloud for the participants who explicitly want a longer-lived URL on a more generous free tier.

## The open questions

No first-person, dollar-itemised post-mortem of a vibe-coding workshop killed by conference wifi was found — wifi guidance is industry-vendor framing, not a primary write-up [[8]](https://wifit.net/wifi-and-internet-solutions-for-hackathons/). No published template for the take-home card exists either; the recommended contents are synthesised from failure-mode posts [[29]](https://buildtolaunch.substack.com/p/8-vibe-coding-mistakes-that-break-production) [[30]](https://medium.com/design-bootcamp/we-vibe-coded-our-way-to-nowhere-and-learned-a-lot-66ca3e9ac969). If you run this playbook, the highest-value thing you can publish is a post-mortem with **spend in EUR, wifi survival rate, and the percentage of URLs still live at day 14** — that is the gap a future Scout run would close.
