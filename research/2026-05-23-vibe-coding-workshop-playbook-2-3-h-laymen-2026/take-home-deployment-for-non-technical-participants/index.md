---
title: "Take-home deployment for non-technical workshop participants"
date: 2026-05-23
depth: deep
format: md
topic: "Take-home deployment for non-technical participants"
topic_raw: "Take-home deployment for non-technical participants"
issue: 56
tags: [vibe-coding, workshops, deployment, lovable, bolt, replit, vercel, supabase, non-technical, education]
summary: "Picking the workshop deploy stack that survives the two-week tail — the deploy click is solved; database pauses, credit caps, and auth rot are what break the app after participants go home."
citations: 74
reading_time_min: 10
cover: cover.svg
cost_usd: 8.41
duration_sec: 500
---

> **TL;DR — Decision for a 2026 workshop facilitator.**
> Default to **[Bolt.new](https://bolt.new) + Bolt Cloud** for the workshop deploy (1M tokens/month free, no card, instant `*.bolt.host` URL, persistent DB bundled) [[4]](https://www.getaiperks.com/en/ai/bolt-new-free-tier-guide) [[5]](https://www.agentrank.tech/blog/bolt-new-hosting-review-free-deployment-fine-print) [[60]](https://bolt.new/blog/bolt-cloud). Use **[Lovable](https://lovable.dev)** if participants will iterate on phones (only platform with a polished mobile app in May 2026) [[41]](https://techcrunch.com/2026/04/28/lovable-launches-its-vibe-coding-app-on-ios-and-android/) — but pre-warn them about the 5-daily / 30-monthly credit ceiling [[44]](https://docs.lovable.dev/introduction/plans-and-credits). **Avoid Replit free** for take-home — its 5-minute sleep + 10–30s cold start makes the "show grandma" URL look broken [[8]](https://p0stman.com/guides/replit-limitations). The deploy click is solved everywhere; the actual failure point is the 7-day Supabase pause [[27]](https://supabase.com/pricing), and credentials baked into the bundle [[61]](https://vibe-eval.com/safety/lovable/) — design the take-home card around those, not around the publish flow.

## What "take-home deployment" actually means in 2026

Three distinct moments, each with different failure modes:

1. **End of session — the URL exists.** Every major vibe-coding platform now ships a one-click Publish to a free auto-subdomain with HTTPS [[5]](https://www.agentrank.tech/blog/bolt-new-hosting-review-free-deployment-fine-print) [[15]](https://docs.lovable.dev/features/custom-domain) [[16]](https://support.bolt.new/cloud/domains) [[18]](https://docs.replit.com/cloud-services/deployments/custom-domains). Solved problem.
2. **Two weeks later — friends and family open the link.** This is where free-tier sleep, Supabase 7-day pause, and authorization-inverted apps break things [[27]](https://supabase.com/pricing) [[68]](https://getautonoma.com/blog/vibe-coding-failures) [[8]](https://p0stman.com/guides/replit-limitations).
3. **Two months later — the participant wants to add a feature.** Credit caps, expired OAuth tokens, dead refresh tokens, App Store review delays [[44]](https://docs.lovable.dev/introduction/plans-and-credits) [[63]](https://blog.laozhang.ai/en/posts/openclaw-anthropic-api-key-error) [[66]](https://nango.dev/blog/google-oauth-invalid-grant-token-has-been-expired-or-revoked/) [[49]](https://9to5mac.com/2026/05/15/iphone-vibe-coding-app-ships-first-update-in-four-months-after-app-store-review-issue/).

The platform you pick at the workshop is really a bet on **2** and **3**, not **1**.

## Platform matrix — what survives the take-home test

| Platform                                                  | Free deploy URL          | Card needed | Free monthly cap                      | Sleeps?              | Custom domain on free | Bundled DB / auth                  | Refs                                |
|-----------------------------------------------------------|--------------------------|-------------|---------------------------------------|----------------------|------------------------|------------------------------------|-------------------------------------|
| [Bolt.new][bn]                                            | `*.bolt.host`            | No          | 1M tokens (~2–5 apps)                 | No                   | Paid only              | Bolt Cloud (DB+auth+storage)       | [[3]][b3] [[4]][b4] [[60]][b60]     |
| [Lovable][lv]                                             | `*.lovable.app`          | No          | 5/day, 30/month credits               | No                   | Paid only              | Lovable Cloud (auto-pauses on $0)  | [[15]][l15] [[44]][l44] [[59]][l59] |
| [v0.dev][v0]                                              | `*.vercel.app` via Hobby | No          | $5 in credits, 7 msgs/day             | No (static)          | Yes (Vercel-managed)   | None bundled                       | [[6]][v6] [[47]][v47] [[29]][v29]   |
| [Replit][rp] (free)                                       | `*.replit.app`           | No          | "Starter" usage; Agent message caps   | ✓ 5min, 10–30s cold  | Paid only              | Postgres 20GB free (Dec 2025+)     | [[8]][r8] [[18]][r18] [[57]][r57]   |
| [Create.xyz][cr] (Anything)                               | `*.created.app`          | No          | "free plan" w/ in-editor publish      | No                   | Paid only              | None bundled                       | [[12]][c12]                         |
| [Base44][b4site]                                          | `*.base44.app`           | No          | 5 msgs/day, 25/month                  | No                   | Paid only              | Bundled                            | [[11]][bf11]                        |
| [Tempo][tp]                                               | platform-hosted          | No          | 50 prompts                            | No                   | Paid only              | None (export to Vercel/Netlify)    | [[13]][t13]                         |
| [Claude Artifacts][ca]                                    | `claude.ai/public/…`     | No          | Tied to Claude plan                   | No                   | ✗ never                | None (static only)                 | [[9]][a9] [[10]][a10]               |
| [Vercel][vc] Hobby (manual)                               | `*.vercel.app`           | No          | non-commercial only                   | No                   | Yes (free attach)      | None bundled                       | [[29]][vh29] [[21]][vh21]           |
| [Netlify][nl]                                             | `*.netlify.app`          | No          | 100 GB bw / 300 build min             | No                   | Yes (free attach)      | None bundled                       | [[17]][n17] [[39]][n39]             |
| [Cloudflare Pages][cf]                                    | `*.pages.dev`            | No          | 100k req/day, no bw cap               | No (sub-5ms)         | Yes (free attach)      | None bundled                       | [[35]][cp35]                        |
| [Render][rd] (free web service)                           | `*.onrender.com`         | No          | spins down @ 15min                    | ✓ ~60s wake          | n/a                    | Free Postgres dies @ 30d           | [[30]][rd30] [[31]][rd31] [[32]][rd32] |
| [Railway][rw]                                             | n/a                      | **Yes**     | 30-day trial only                     | n/a                  | n/a                    | n/a                                | [[33]][rw33]                        |
| [Fly.io][fl]                                              | n/a                      | **Yes**     | 7-day / 2-VM-hour trial only          | n/a                  | n/a                    | n/a                                | [[34]][fl34]                        |

[bn]: https://bolt.new
[lv]: https://lovable.dev
[v0]: https://v0.dev
[rp]: https://replit.com
[cr]: https://www.create.xyz
[b4site]: https://base44.com
[tp]: https://tempo.new
[ca]: https://claude.com
[vc]: https://vercel.com
[nl]: https://www.netlify.com
[cf]: https://pages.cloudflare.com
[rd]: https://render.com
[rw]: https://railway.com
[fl]: https://fly.io
[b3]: https://support.bolt.new/faqs/hosting
[b4]: https://www.getaiperks.com/en/ai/bolt-new-free-tier-guide
[b60]: https://bolt.new/blog/bolt-cloud
[l15]: https://docs.lovable.dev/features/custom-domain
[l44]: https://docs.lovable.dev/introduction/plans-and-credits
[l59]: https://docs.lovable.dev/integrations/cloud
[v6]: https://v0.app/pricing
[v47]: https://uibakery.io/blog/vercel-v0-pricing-explained-what-you-get-and-how-it-compares
[v29]: https://vercel.com/docs/plans/hobby
[r8]: https://p0stman.com/guides/replit-limitations
[r18]: https://docs.replit.com/cloud-services/deployments/custom-domains
[r57]: https://docs.replit.com/cloud-services/storage-and-databases/sql-database
[c12]: https://www.create.xyz/docs/publish-and-share/publish
[bf11]: https://www.websitebuilderexpert.com/vibe-coding/base44-pricing/
[t13]: https://vibecoding.app/blog/tempo-review
[a9]: https://support.claude.com/en/articles/9547008-publishing-and-sharing-artifacts
[a10]: https://p0stman.com/guides/claude-artifacts-limitations
[vh29]: https://vercel.com/docs/plans/hobby
[vh21]: https://vercel.com/docs/domains/working-with-domains/add-a-domain
[n17]: https://docs.netlify.com/manage/domains/get-started-with-domains/
[n39]: https://www.netlify.com/pricing/
[cp35]: https://developers.cloudflare.com/workers/platform/pricing/
[rd30]: https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026
[rd31]: https://blog.samkiel.dev/your-render-free-tier-is-not-broken-its-just-cold
[rd32]: https://render.com/changelog/free-postgresql-instances-now-expire-after-30-days-previously-90
[rw33]: https://docs.railway.com/pricing/plans
[fl34]: https://www.saaspricepulse.com/blog/flyio-free-tier-2026

**Reading the matrix.** Pick Bolt / Lovable / v0 if the workshop pitch is "ship from a prompt" and the participant won't open a terminal. Pick Vercel / Netlify / Cloudflare Pages if a more experienced participant just wants their static site hosted — but you've already lost the "no CLI" promise. Avoid Render, Railway, and Fly.io for take-home: cold starts and forced credit cards kill the demo before friends ever see it [[31]](https://blog.samkiel.dev/your-render-free-tier-is-not-broken-its-just-cold) [[33]](https://docs.railway.com/pricing/plans) [[34]](https://www.saaspricepulse.com/blog/flyio-free-tier-2026).

## Will it still work in 6 weeks? The "show grandma" test

The biggest invisible take-home risk isn't compute — it's the database. Vercel Hobby has *no* inactivity suspension and unlimited deployment retention [[29]](https://vercel.com/docs/plans/hobby); Netlify only suspends if you blow the bandwidth quota, never on dormancy [[39]](https://www.netlify.com/pricing/); Cloudflare Workers are structurally immune because V8 isolates start in under 5ms [[35]](https://developers.cloudflare.com/workers/platform/pricing/). Compute on those is fine for years.

But the database that the app depends on is where workshop apps die quietly. The single most important fact for any facilitator:

> [Supabase](https://supabase.com) Free pauses projects after **7 days of database inactivity** [[27]](https://supabase.com/pricing). Dashboard visits don't count — only real DB queries reset the timer [[52]](https://shadhujan.medium.com/how-to-keep-supabase-free-tier-projects-active-d60fd4a17263). Data survives the pause [[53]](https://aiagencyplus.com/keep-your-supabase-free-tier-project-live-past-the-limit/), but the resume is at minimum ~30s and at worst stuck for over an hour with the unpause button failing entirely [[54]](https://github.com/orgs/supabase/discussions/38950) [[55]](https://github.com/supabase/supabase/issues/43038) (`supabase/supabase` ⭐ 103k).

A community ecosystem of cron pingers exists *only* to defeat this single behavior — [`travisvn/supabase-pause-prevention`](https://github.com/travisvn/supabase-pause-prevention) ⭐ 170 [[28]](https://github.com/travisvn/supabase-pause-prevention) is the canonical example.

### Database options ranked by "left alone for two months"

| Database                | Pauses on inactivity? | Wake time          | Data lost?               | Refs                              |
|-------------------------|-----------------------|--------------------|--------------------------|-----------------------------------|
| [Turso][td]             | ✗ always-on           | n/a                | No                       | [[38]][dt38]                      |
| [Neon][nd]              | ✓ after 5 min         | ~hundreds of ms    | No                       | [[36]][dn36]                      |
| [Replit Postgres][rpd]  | ✗ (managed Dec 2025+) | n/a                | No (20 GB free)          | [[57]][dr57]                      |
| [Supabase][sd]          | ✓ after 7 days        | ~30s typical, hours worst-case | No (but auth req'd to resume) | [[27]][ds27] [[52]][ds52] [[54]][ds54] |
| Render free Postgres    | n/a                   | n/a                | ⚠ deleted after 30d + 14d grace | [[32]][dr32]                |
| PlanetScale free        | n/a                   | n/a                | ⚠ no free tier since Apr 2024   | [[37]][dp37]                |

[td]: https://turso.tech
[nd]: https://neon.com
[rpd]: https://replit.com
[sd]: https://supabase.com
[dt38]: https://turso.tech/pricing
[dn36]: https://neon.com/docs/introduction/scale-to-zero
[dr57]: https://docs.replit.com/cloud-services/storage-and-databases/sql-database
[ds27]: https://supabase.com/pricing
[ds52]: https://shadhujan.medium.com/how-to-keep-supabase-free-tier-projects-active-d60fd4a17263
[ds54]: https://github.com/orgs/supabase/discussions/38950
[dr32]: https://render.com/changelog/free-postgresql-instances-now-expire-after-30-days-previously-90
[dp37]: https://www.codu.co/niall/no-more-free-tier-on-planetscale-here-are-free-alternatives-q4wzqcu9

**Practical recommendation for the workshop's default stack:** if you need a real DB during the session, use **Neon** (transparent scale-to-zero, no manual unpause) or **Turso** (no pause at all). If you must use Supabase because that's what the vibe-coding tool wires up by default, design the take-home card so participants know to manually resume the project after long gaps [[53]](https://aiagencyplus.com/keep-your-supabase-free-tier-project-live-past-the-limit/).

## Ephemeral filesystem — the silent data-loss trap

[Vercel](https://vercel.com) officially states SQLite cannot be used with their platform because each serverless function instance gets its own ephemeral filesystem [[56]](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel). [Replit](https://replit.com) explicitly warns that writes to a deployed Repl's local filesystem disappear on any following redeploy [[58]](https://blog.replit.com/replspace-filesystems). Both AI assistants happily generate SQLite-backed code when prompted naively — so the workshop's "Save my todos" app silently loses every entry the moment the participant edits the code and redeploys. Force the AI to use a managed DB (Bolt Cloud, Lovable Cloud, Neon, Turso) in the system prompt or initial-message scaffolding.

## Auth and credentials — the dead-link of week three

The most-cited failure pattern across 2026 writeups isn't the app crashing — it's auth quietly returning 401 [[68]](https://getautonoma.com/blog/vibe-coding-failures). Concrete take-home killers:

- **Google OAuth refresh tokens expire after 7 days** while the consent screen is in Testing mode, and after ~6 months of non-use even once published [[66]](https://nango.dev/blog/google-oauth-invalid-grant-token-has-been-expired-or-revoked/). Workshop apps almost always ship in Testing mode → guaranteed silent death by day 8.
- **[Clerk](https://clerk.com) ships separate dev/prod keys**; a common deploy failure is forgetting to swap, with no obvious error surface for a non-technical user [[65]](https://clerk.com/docs/guides/development/deployment/production). Free tier now covers 50,000 MAU so there's no cost cliff [[64]](https://supertokens.com/blog/clerk-pricing-the-complete-guide).
- **Anthropic banned subscription OAuth tokens in third-party tools on April 4, 2026** — every app that embedded a Claude subscription token instantly broke and required migration to pay-as-you-go [[63]](https://blog.laozhang.ai/en/posts/openclaw-anthropic-api-key-error). Treat any LLM-key the AI bakes into the app as a future fault.
- **[Lovable](https://lovable.dev) apps routinely embed Stripe/OpenAI/SendGrid keys in the JavaScript bundle**, where credential harvesters find them within hours [[61]](https://vibe-eval.com/safety/lovable/). In March 2026 a single vibe-coded app leaked 1.5M API keys [[62]](https://modall.ca/blog/vibe-coding-security-risks). Workshop policy: **no real keys in workshop apps** — use the platform's bundled cloud or test/throwaway keys only.
- **Authorization is often inverted** in laymen-built apps: a study of 170 Lovable apps found anonymous visitors with full access and logged-in users blocked [[68]](https://getautonoma.com/blog/vibe-coding-failures). The take-home app frequently *looks* fine on the participant's own login but breaks for the friend they share it with.

The cleanest mitigation is the bundled-cloud route: **[Lovable Cloud][lc]** ships DB, auth, storage, and AI auto-provisioned per workspace with $25/month free cloud credit and $1 AI credit; projects auto-pause when credits empty (rather than going broken) [[59]](https://docs.lovable.dev/integrations/cloud). **[Bolt Cloud][bc]** offers the same bundle with native auth (signups, logins, password resets, RBAC) baked in [[60]](https://bolt.new/blog/bolt-cloud). Either removes both the SQLite trap and the API-key-leak problem in one decision.

[lc]: https://docs.lovable.dev/integrations/cloud
[bc]: https://bolt.new/blog/bolt-cloud

## Custom domain — only worth it for the rare "I want this to look real" participant

Every platform's auto-subdomain (e.g. `gleaming-cobbler-3a8f.lovable.app`) is functional and persistent [[15]](https://docs.lovable.dev/features/custom-domain). Most workshop apps never need more — friends and family share via direct link or QR code. The fraction of participants who want a real domain split into three paths:

| Path                                      | UX for a non-tech user                                  | Cost (2026)                | Refs                                             |
|-------------------------------------------|---------------------------------------------------------|----------------------------|--------------------------------------------------|
| [Replit][rep] in-platform domain purchase | Search → buy → auto-DNS in <1 min, WHOIS privacy free   | Domain at registrar prices + Core $20/mo | [[19]][cd19] [[26]][cd26]              |
| [Vercel Domains][vd] one-click attach     | Buy in dashboard, attach in same screen, no markup      | Domain at registrar prices, free on Hobby | [[20]][cd20] [[21]][cd21]              |
| Manual attach (Netlify / Bolt / Lovable)  | ⚠ Must paste A/CNAME into registrar — DNS knowledge required | Domain only                | [[16]][cd16] [[17]][cd17] [[15]][cd15]           |
| [is-a.dev][iad] (free `*.is-a.dev`)       | Open a PR on GitHub — requires GitHub literacy          | Free                       | [[24]][cd24]                                     |
| [js.org][jso] (free `*.js.org`)           | Open a PR — JS-only projects                            | Free                       | [[25]][cd25]                                     |

[rep]: https://replit.com
[vd]: https://vercel.com/domains
[iad]: https://is-a.dev
[jso]: https://js.org
[cd19]: https://docs.replit.com/cloud-services/deployments/domain-purchasing
[cd26]: https://blog.replit.com/domain-purchasing-on-replit
[cd20]: https://vercel.com/domains
[cd21]: https://vercel.com/docs/domains/working-with-domains/add-a-domain
[cd16]: https://support.bolt.new/cloud/domains
[cd17]: https://docs.netlify.com/manage/domains/get-started-with-domains/
[cd15]: https://docs.lovable.dev/features/custom-domain
[cd24]: https://is-a.dev
[cd25]: https://github.com/js-org/js.org

For the rare participant who wants a real `.com`, point them at **[Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)** at $10.44/yr wholesale (no markup, free WHOIS privacy, free DNSSEC — but locks the domain to Cloudflare nameservers) [[22]](https://www.cloudflare.com/products/registrar/) or **[Porkbun](https://porkbun.com/products/domains)** at ~$10.91/yr with flat renewal pricing [[23]](https://porkbun.com/products/domains). Avoid registrars that show $5.98 first-year teasers — Namecheap renewal jumps to $18.48 [[23]](https://porkbun.com/products/domains).

## Two months later — can they actually iterate?

The "I forgot how to log back in" problem is essentially solved: every major tool accepts Google, GitHub, or email and shows every project on a default dashboard after sign-in [[42]](https://www.nocode.mba/articles/lovable-tutorial-google-signin). What bites instead is **how many follow-up edits a free plan permits**:

| Tool       | Free credit / message cap            | Roughly equivalent to              | Ref                              |
|------------|--------------------------------------|------------------------------------|----------------------------------|
| Bolt.new   | 1M tokens/month, 300k/day            | 2–5 small apps OR ~30 edits        | [[4]](https://www.getaiperks.com/en/ai/bolt-new-free-tier-guide)              |
| Lovable    | 5 daily / 30 monthly credits         | ~1 feature-add per day             | [[44]](https://docs.lovable.dev/introduction/plans-and-credits)              |
| v0.dev     | $5/mo credits, 7 msg/day             | ~5 small UI edits                  | [[47]](https://uibakery.io/blog/vercel-v0-pricing-explained-what-you-get-and-how-it-compares)              |
| Base44     | 5 msg/day, 25/month                  | 1 small feature/month              | [[11]](https://www.websitebuilderexpert.com/vibe-coding/base44-pricing/)              |
| Tempo      | 50 prompts (lifetime on free)        | One bigger build, then done        | [[13]](https://vibecoding.app/blog/tempo-review)              |

Version-history is the other concern, and the news is good: [Lovable's Versioning 2.0](https://lovable.dev/blog/versioning-with-lovable-two-point-zero) groups edits by date with bookmarks for milestones, restoring an older version creates a new edit card (non-destructive) [[43]](https://lovable.dev/blog/versioning-with-lovable-two-point-zero). [Bolt](https://bolt.new) preserves the live Bolt/Supabase DB when restoring earlier code [[45]](https://support.bolt.new/building/using-bolt/rollback-backup). [v0](https://v0.dev) remembers conversation context across sessions so iteration builds on prior state [[46]](https://v0.dev/faq).

**Mobile iteration shipped in 2026.** [Lovable](https://lovable.dev) launched an iOS/Android app on April 27, 2026 that syncs between phone and desktop seamlessly [[40]](https://lovable.dev/blog/mobile-app) [[41]](https://techcrunch.com/2026/04/28/lovable-launches-its-vibe-coding-app-on-ios-and-android/). [Replit Mobile Apps](https://blog.replit.com/mobile-apps) lets users build native iOS apps via Agent with QR-code Expo previews [[48]](https://blog.replit.com/mobile-apps) — though Replit's iPhone app went four months without updates in early 2026 due to an App Store review dispute [[49]](https://9to5mac.com/2026/05/15/iphone-vibe-coding-app-ships-first-update-in-four-months-after-app-store-review-issue/), a real take-home fragility.

[Replit](https://replit.com) also offers automatic redeploys on every Git push from the Version Control tab [[50]](https://www.deployhq.com/guides/replit), removing the "where is the redeploy button" question entirely.

## Designing the take-home card

Educators running 2025–2026 AI-coding workshops converge on a small set of patterns. The Berkeley ALS team explicitly committed to a *series* of follow-up workshops after one session because participants can't keep pace with tool churn alone [[70]](https://als.lbl.gov/a-world-of-vibe-coding-opportunities-at-the-als/). [Anthropic's Teach For All](https://www.anthropic.com/news/anthropic-teach-for-all) codifies the standard alumni stack: monthly office hours plus Claude Connect peer hub across 60+ countries for daily Q&A [[73]](https://www.anthropic.com/news/anthropic-teach-for-all). [Lovable's community](https://lovable.dev/community) is the template most platforms now copy: a 160K-member Discord, recurring topical office hours (e.g. Security Office Hours), and a `community@` email [[69]](https://lovable.dev/community). In-person workshop afterlife often spans Meetup + a hub site + LinkedIn rather than a single channel [[74]](https://www.meetup.com/vibe-coders-collective/) — so the card should list multiple re-entry points, not one.

Recommended content for a physical take-home card (synthesized from failure-mode writeups and platform docs; no canonical published template exists [[71]](https://buildtolaunch.substack.com/p/8-vibe-coding-mistakes-that-break-production) [[72]](https://medium.com/design-bootcamp/we-vibe-coded-our-way-to-nowhere-and-learned-a-lot-66ca3e9ac969)):

1. **Your URL** — printed verbatim, plus a QR code [[5]](https://www.agentrank.tech/blog/bolt-new-hosting-review-free-deployment-fine-print).
2. **How you signed in** — "Sign in with Google, the address ending in …" (handles the "wrong account at home" failure) [[42]](https://www.nocode.mba/articles/lovable-tutorial-google-signin).
3. **If it says 'paused' or 'unavailable'** → log into the platform dashboard and click resume; data is safe [[53]](https://aiagencyplus.com/keep-your-supabase-free-tier-project-live-past-the-limit/).
4. **If a friend says it's broken but it works for you** → most likely an auth or authorization bug; ask the AI: "anonymous users can see everything but logged-in users get nothing, fix it" [[68]](https://getautonoma.com/blog/vibe-coding-failures).
5. **Daily edit budget** — "you have X edits per day on the free plan" so they don't burn the month in a single afternoon [[44]](https://docs.lovable.dev/introduction/plans-and-credits) [[47]](https://uibakery.io/blog/vercel-v0-pricing-explained-what-you-get-and-how-it-compares).
6. **Throw-away permission** — the "permission to abandon" reframing reduces the pull on facilitator time when the prototype turns out wrong [[72]](https://medium.com/design-bootcamp/we-vibe-coded-our-way-to-nowhere-and-learned-a-lot-66ca3e9ac969).
7. **Re-entry URLs** — Discord, Meetup, office-hours schedule, facilitator email [[69]](https://lovable.dev/community) [[73]](https://www.anthropic.com/news/anthropic-teach-for-all) [[74]](https://www.meetup.com/vibe-coders-collective/).
8. **One sentence on security** — "don't put real API keys, passwords, or credit-card details into your app" [[61]](https://vibe-eval.com/safety/lovable/) [[62]](https://modall.ca/blog/vibe-coding-security-risks).

The single most-reported pain point during the workshop itself is debugging — and the proven mitigation is teaching the participant to query the AI to explain errors rather than touch the code [[67]](https://benzatine.com/news-room/unlocking-app-creation-insights-from-a-vibe-coding-workshop). Bake that into both the in-session script and the card.

## Recommendation summary

| Workshop shape                                         | Recommended platform        | Why                                                       |
|--------------------------------------------------------|-----------------------------|-----------------------------------------------------------|
| Generic 2–3 hr "ship a working app" for laymen          | Bolt.new + Bolt Cloud       | Most generous free tier, no card, persistent DB bundled, no sleep [[4]](https://www.getaiperks.com/en/ai/bolt-new-free-tier-guide) [[60]](https://bolt.new/blog/bolt-cloud) |
| Participants likely to iterate on phones afterward      | Lovable + Lovable Cloud     | Only mature mobile app in May 2026 [[41]](https://techcrunch.com/2026/04/28/lovable-launches-its-vibe-coding-app-on-ios-and-android/); accept credit ceiling tradeoff |
| UI prototyping only (no backend)                        | v0.dev → Vercel Hobby       | One-click deploy, never sleeps, custom domain free [[6]](https://v0.app/pricing) [[29]](https://vercel.com/docs/plans/hobby) |
| Static "hello world" sites for absolute beginners       | Claude Artifacts            | Zero account-creation friction for the viewer [[9]](https://support.claude.com/en/articles/9547008-publishing-and-sharing-artifacts) |
| Anything Replit-based                                   | ⚠ require Core ($20/mo)     | Free tier's sleep + custom-domain lock kills the take-home demo [[8]](https://p0stman.com/guides/replit-limitations) [[18]](https://docs.replit.com/cloud-services/deployments/custom-domains) |

The deploy click is solved. The take-home is about choosing a *platform whose free-tier failure mode is benign* — and writing a card that tells participants exactly what to do when the silent failures (Supabase pause, OAuth expiry, exhausted credits) inevitably happen.
