---
title: "Vibe-coding tool stack for a 2-3 hour workshop on shared wifi"
date: 2026-05-23
depth: deep
format: md
topic: "Vibe-coding tool stack on shared wifi, low budget"
topic_raw: "Vibe-coding tool stack on shared wifi, low budget"
issue: 56
tags: [vibe-coding, workshop, lovable, bolt, v0, replit, claude-artifacts]
summary: "Lovable as the default with Bolt.new as the backup, hosted hotspot for wifi, $0–$50 host spend for 20 attendees, and signup done the night before."
citations: 76
reading_time_min: 11
cover: cover.svg
cost_usd: 8.75
duration_sec: 827
model: "Opus 4.7"
---

> **Decision.** Pick **[Lovable](https://lovable.dev)** as the primary tool — chat-only UI, server-side rendering, one-click publish to `*.lovable.app`, and the only vendor with a real K-12 / no-account classroom track [[2]](https://designlab.com/blog/best-vibe-coding-tools) [[7]](https://imagilabs.com/pages/lovable-imagi-hour-of-ai) [[38]](https://lovable.dev/faq/deployment/rendering) [[55]](https://docs.lovable.dev/features/publish). Keep **[Bolt.new](https://bolt.new)** warm as the backup (faster cold start, no account, but WebContainers hate locked-down laptops and Lovable has logged 314+ outages since May 2025) [[4]](https://lovable.dev/guides/bolt-vs-replit-vs-lovable) [[5]](https://www.nocode.mba/articles/bolt-ai-new-guide) [[31]](https://support.bolt.new/faqs/troubleshooting/webcontainer) [[71]](https://statusgator.com/services/lovable). Have attendees sign up **24–48 h before** the room, off the venue wifi, and bring a phone-hotspot kit. Host budget: ~$0 if you stretch free tiers, ~$50 if you pay for one shared Pro seat as fallback; the per-attendee marginal cost is zero [[27]](https://hatchworks.com/blog/gendd/cost-of-vibe-coding/) [[76]](https://theschoolhousemommy.wordpress.com/2017/12/14/vipkid-backup-plans-a-hotspot-tutorial/).

## The recommended stack at a glance

| Layer            | Primary                  | Backup                       | Why                                                                                                                                                                                                                                                                |
|------------------|--------------------------|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Build tool       | Lovable (free)           | Bolt.new (free)              | Lovable hides the file tree, ships SSR HTML (low bandwidth); Bolt boots in seconds and needs no account [[2]](https://designlab.com/blog/best-vibe-coding-tools) [[3]](https://altar.io/lovable-vs-bolt-vs-v0-vs-replit-vs-base44/) [[4]](https://lovable.dev/guides/bolt-vs-replit-vs-lovable) [[38]](https://lovable.dev/faq/deployment/rendering) |
| Identity         | Continue-with-Google     | Pre-provisioned host account | Google SSO sidesteps Claude's SMS verification gate and ChatGPT's phone-country check [[42]](https://www.calilio.com/blogs/how-to-use-claude-ai-without-a-phone-number) [[45]](https://moveo.ai/blog/countries-where-chatgpt-is-banned)                  |
| Hosting          | Built-in `*.lovable.app` | `*.bolt.host`                | Both are one-click on free tiers; no Vercel / Netlify / Cloudflare account required at workshop time [[55]](https://docs.lovable.dev/features/publish) [[58]](https://support.bolt.new/faqs/hosting) |
| Sharing          | QR code on screen        | Short link                   | Phone-camera scannable, works for grandma in the room [[67]](https://www.qrstuff.com/) [[68]](https://www.canva.com/qr-code-generator/) |
| Network plan A   | Venue wifi               | Phone hotspot                | 100+ laptops with previews + npm + Git saturate venue APs; a single instructor hotspot is the canonical fallback [[39]](https://wifit.net/wifi-and-internet-solutions-for-hackathons/) [[76]](https://theschoolhousemommy.wordpress.com/2017/12/14/vipkid-backup-plans-a-hotspot-tutorial/) |
| Network plan B   | Pre-warmed accounts      | Pre-built starter repo       | Shared NAT triggers Cloudflare Turnstile escalations and "too many sessions from 1 IP" rate limits [[50]](https://friendlycaptcha.com/insights/cloudflare-turnstile-accessibility/) [[69]](https://community.openai.com/t/i-am-the-it-admin-from-a-school-and-we-are-encounter-the-error-of-78-many-sessions-from-1-ip/270490) |

## 1. Tool shortlist — what survives contact with a non-coder

The 2026 vibe-coding field has six tools you can plausibly hand to a stranger. They are not equivalent.

| Tool                                                     | Layman-friendly | Time to first working app                                | File tree in face? | Notes                                                                                  |
|----------------------------------------------------------|:---------------:|----------------------------------------------------------|:-------------------:|----------------------------------------------------------------------------------------|
| [Lovable](https://lovable.dev)                           | ✓               | ~60 min curriculum proven for grade 6-12 [[7]](https://imagilabs.com/pages/lovable-imagi-hour-of-ai)             | ✗                  | Polished UI on first prompt; auth+DB+hosting auto-wired [[2]](https://designlab.com/blog/best-vibe-coding-tools)                                       |
| [Bolt.new](https://bolt.new)                             | ✓               | 2-4 min landing page, 8-12 min to-do app [[5]](https://www.nocode.mba/articles/bolt-ai-new-guide)                  | ✓                  | Lowest signup friction in the field; demo-grade output [[4]](https://lovable.dev/guides/bolt-vs-replit-vs-lovable)                                                |
| [v0](https://v0.app)                                     | ⚠               | Works, but assumes Vercel mental model [[1]](https://www.xda-developers.com/tried-vibe-coding-a-real-app-in-bolt-v0-and-lovable/)                            | ✗                  | UI-first, weaker on full-stack [[1]](https://www.xda-developers.com/tried-vibe-coding-a-real-app-in-bolt-v0-and-lovable/)                                                                |
| [Replit Agent](https://replit.com)                       | ✗               | IDE overwhelms non-coders [[3]](https://altar.io/lovable-vs-bolt-vs-v0-vs-replit-vs-base44/)                                  | ✓                  | Free tier near-unusable (10 checkpoints/mo, 512 MB RAM, sleep at 5 min) [[17]](https://p0stman.com/guides/replit-limitations)                  |
| [Cursor](https://cursor.com)                             | ✗               | Reviewers say "start somewhere else" [[6]](https://www.vibestack.in/blog/cursor-ai-review-2026)                            | ✓                  | Full IDE; useful later, wrong first tool [[6]](https://www.vibestack.in/blog/cursor-ai-review-2026)                                                            |
| [Claude Artifacts](https://claude.com)                   | ✓               | Runs in chat, ~70 % to shippable [[9]](https://www.glbgpt.com/resource/claude-artifacts-20-makes-app-building-simple)                                   | ✗                  | Public share lands viewers on a Claude login wall [[61]](https://www.shareduo.com/blog/claude-artifacts-not-working-for-others)                                              |

In a head-to-head non-developer test, **Lovable and v0 both shipped a working photo-booth app from a single prompt while Bolt.new failed across six attempts** — the camera feature never loaded [[1]](https://www.xda-developers.com/tried-vibe-coding-a-real-app-in-bolt-v0-and-lovable/). One facilitator who has run multiple workshops moved from Bolt to v0 to Lovable as her default classroom tool — non-coder friction was the driver [[78]](https://annaarteeva.medium.com/choosing-your-ai-prototyping-stack-lovable-v0-bolt-replit-cursor-magic-patterns-compared-9a5194f163e9). Lovable's own docs concede Bolt has the lowest *barrier* for a complete novice (no account, no config) — but Bolt's output is also the most demo-grade [[4]](https://lovable.dev/guides/bolt-vs-replit-vs-lovable).

**The trade.** Lovable produces things that look done; Bolt produces things that exist. For a 2-3 h workshop where the deliverable is a working URL to show a friend, Lovable wins; for a one-prompt-and-done warmup, Bolt is the quickest path.

## 2. Free-tier math — does this break the bank?

Short answer: no, if you plan it. Long answer:

| Tool         | Free-tier limit (May 2026)                                              | Reset             | Pro price        | Burnable in 3 h?         |
|--------------|-------------------------------------------------------------------------|-------------------|------------------|--------------------------|
| Lovable      | 5 credits/day, 30/month [[11]](https://docs.lovable.dev/introduction/plans-and-credits)                                            | Daily 00:00 UTC   | $25/mo, 100 cr [[12]](https://lovable.dev/pricing) | ⚠ Yes; one landing page = ~2 cr |
| Bolt.new     | 1M tokens/month, 300K/day hard cap [[15]](https://support.bolt.new/account-and-subscription/tokens)                                  | 1st of month, no rollover [[15]](https://support.bolt.new/account-and-subscription/tokens) | $25/mo [[16]](https://bolt.new/pricing)        | ⚠ Possible; debug loops eat tokens [[28]](https://www.banani.co/blog/bolt-new-pricing)        |
| v0           | 7 messages/day (variable), $5 monthly credits [[13]](https://v0.app/pricing) [[14]](https://community.vercel.com/t/v0-what-are-the-daily-limits-for-the-free-tier-in-v0/26935)                  | Daily / monthly   | $20/mo           | ✓ Yes; 7 msgs is one bug fix    |
| Replit Agent | 10 checkpoints/month, 512 MB RAM, repls sleep 5 min [[17]](https://p0stman.com/guides/replit-limitations)                  | Monthly           | $25/mo Core [[18]](https://replit.com/pricing)     | ✓ Yes; effectively unusable     |
| Cursor       | 2,000 completions + 50 slow premium reqs/month [[20]](https://cursor.com/pricing)                       | Monthly           | $20/mo           | ✗ Generous for one session     |
| Claude.ai    | ~15-40 messages per rolling 5 h [[22]](https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work)                                        | Rolling 5 h       | $20/mo Pro       | ⚠ Tight on heavy iteration     |
| ChatGPT      | 10 GPT-5.5 msgs / 5 h, then mini [[23]](https://help.openai.com/en/articles/11909943-gpt-5-in-chatgpt)                                       | Rolling 5 h       | $20/mo Plus      | ⚠ Tight; auto-falls back        |

**Host-pays math.** A solo vibe-coder spends $100-250/month unnoticed [[27]](https://hatchworks.com/blog/gendd/cost-of-vibe-coding/). For 20 attendees on Pro for one month, expect ~$500 (e.g. 20 × $25 Lovable). No vendor publishes a workshop SKU — group rates are extrapolated from per-seat. Cheaper paths exist:

- **Students (verified .edu).** Replit Core: $10/mo for six months [[26]](https://x.com/Replit/status/1969047938765615264). Cursor Pro: free for one year (~$240 value) [[21]](https://felloai.com/cursor-student-discount/). Verified educators get Replit free with student credits [[25]](https://replit.com/edu).
- **Multi-account chaining.** Stacking free credits across alt Google accounts violates OpenAI ToS §4(e) explicitly [[24]](https://help.openai.com/en/articles/9275245-chatgpt-free-tier-faq) and equivalent clauses on the others. Don't.
- **Host shares one Pro seat.** $25 covers the demo, the room watches the screen, attendees stay on free. Marginal per-head cost: $0.

## 3. Shared-wifi survivability

The tools split into three bandwidth tiers. Pick by your venue.

| Tool                          | First-load weight                              | After boot                            | Survives wifi drop?               |
|-------------------------------|------------------------------------------------|---------------------------------------|-----------------------------------|
| Lovable                       | Server-rendered HTML chunks (TanStack SSR) [[38]](https://lovable.dev/faq/deployment/rendering)                                  | Thin client, retries are cheap        | ✓ Each request is independent      |
| v0                            | Server-rendered, similar to Lovable            | Light                                 | ✓ Same profile                     |
| Cursor                        | Streams over HTTP/2 to *.cursor.sh [[33]](https://cursor.com/docs/troubleshooting/common-issues)                          | Persistent connection                 | ✗ Chronic weekly disconnects, IDE restart often needed [[34]](https://forum.cursor.com/t/repeated-disconnections/147418) |
| Claude Code (CLI)             | Tokens to Anthropic API; 5.5× lighter than Cursor [[36]](https://dev.to/oneinfer/cursor-and-claude-code-rate-limits-in-2026-the-shipping-wall-hidden-in-your-ai-coding-stack-2acc)  | Slim                                  | ⚠ Silently hangs spinner on drop, no error [[35]](https://github.com/anthropics/claude-code/issues/44171) ⭐ 126k                  |
| Bolt.new                      | <1 MB WASM runtime [[29]](https://changelog.com/jsparty/178), + npm dependencies                              | Runs offline once booted [[30]](https://blog.stackblitz.com/posts/introducing-webcontainers/)                | ⚠ 30 s hard boot timeout [[32]](https://github.com/stackblitz/bolt.new/issues/6945) ⭐ 16k             |
| Replit                        | Full cloud IDE, continuous sync                | Heavy                                 | ✗ Lose access during outages; tethered mode burns mobile data [[37]](https://emvigotech.com/blog/replit-challenges-pain-points/)         |
| GitHub Codespaces             | Remote VM                                      | Server-side                           | ✓ Preserves session across disconnects [[40]](https://docs.github.com/en/codespaces/about-codespaces/understanding-the-codespace-lifecycle)              |

**The Bolt trap.** Bolt's troubleshooting page admits that **ad-blockers, VPNs, and non-Chromium browsers** — all common on locked-down work/conference laptops — break the cross-origin-isolation handshake outright [[31]](https://support.bolt.new/faqs/troubleshooting/webcontainer). On a slow venue wifi the 30-second boot timeout will fire before the WebContainer initialises, with no partial-load fallback [[32]](https://github.com/stackblitz/bolt.new/issues/6945) ⭐ 16k. If you bet on Bolt, screen-test laptops before the room.

**The venue-wifi reality.** 100+ laptops doing previews, npm, Git pushes routinely saturate APs not provisioned for power users; backup hotspot kits are standard event-ops advice now [[39]](https://wifit.net/wifi-and-internet-solutions-for-hackathons/). A teacher's mobile hotspot used as a wifi-failure fallback is a pattern borrowed from VIPKid-era ESL workshops and still works [[76]](https://theschoolhousemommy.wordpress.com/2017/12/14/vipkid-backup-plans-a-hotspot-tutorial/).

## 4. Signup friction (the silent workshop killer)

Most attendee minutes lost in a vibe-coding workshop are lost at the signup screen, not the prompt.

| Tool         | Account required? | Phone SMS? | Age gate                   | Credit card? | Workshop-day verdict          |
|--------------|:-----------------:|:----------:|----------------------------|:------------:|-------------------------------|
| Bolt.new     | ✗ (free tier)     | ✗          | None at signup [[5]](https://www.nocode.mba/articles/bolt-ai-new-guide)       | ✗            | ✓ Walk-in friendly            |
| Lovable      | ✓                 | ✗ (Google SSO) | None visible            | ✗            | ✓ Walk-in friendly            |
| v0 / Vercel  | ✓                 | ✗          | None at signup            | ✗ [[47]](https://uibakery.io/blog/vercel-v0-pricing-explained-what-you-get-and-how-it-compares)        | ✓ Google/GitHub/Apple/GitLab/Bitbucket SSO [[46]](https://vercel.com/signup) |
| Cursor       | ✓                 | ✗          | None at signup            | ✗ Hobby [[48]](https://www.nxcode.io/resources/news/is-cursor-ai-free-plans-limits-worth-upgrading-2026) | ⚠ Student Pro needs 3-7 day SheerID review [[49]](https://cursor.com/students)         |
| Claude.ai    | ✓                 | ✓ (email signup) [[75]](https://support.claude.com/en/articles/8287232-verify-your-phone-number)  | **18+ enforced** [[41]](https://support.claude.com/en/articles/13117299-minimum-age-requirement-access-restriction) | ✗ | ⚠ Use Google SSO to skip SMS [[42]](https://www.calilio.com/blogs/how-to-use-claude-ai-without-a-phone-number); VoIP rejected [[43]](https://blog.laozhang.ai/en/posts/claude-verification-guide) |
| ChatGPT      | ✓                 | ✓          | 13+, parental for 13-17 [[44]](https://help.openai.com/en/articles/8313401-is-chatgpt-safe-for-all-ages)    | ✗            | ⚠ IP & phone-country dual-blocked in ~20 countries [[45]](https://moveo.ai/blog/countries-where-chatgpt-is-banned)        |

**Shared-NAT hazard.** Cloudflare Turnstile escalates challenges on shared-IP wifi; the most common silent failure is device clock skew rejecting the token [[50]](https://friendlycaptcha.com/insights/cloudflare-turnstile-accessibility/) [[51]](https://runcloud.io/blog/fix-cloudflare-captcha-failure). On a school NAT, OpenAI returns "too many sessions from 1 IP" and offers no fast support channel [[69]](https://community.openai.com/t/i-am-the-it-admin-from-a-school-and-we-are-encounter-the-error-of-78-many-sessions-from-1-ip/270490). Schools also block ChatGPT at the firewall regardless of the ToS [[53]](https://www.esparklearning.com/blog/can-students-use-chatgpt/).

**The 24-48 h pre-flight.** Established AI-coding curricula explicitly tell learners to create their accounts 24-48 hours before the room, off the venue wifi, citing 30+ minute downloads and trial-clock concerns [[52]](https://www.craftamplify.com/ai-frontend-coding/prep). Do this — it's the single highest-yield mitigation.

**Institutional escape hatch.** Universities like Harvard front a pre-provisioned "AI Sandbox" that wraps GPT/Claude/Gemini behind SSO, removing every per-student phone/age/payment gate [[54]](https://it.hms.harvard.edu/service/harvard-ai-sandbox). If your venue has anything similar, use it.

## 5. Deploy & share — fastest path to a public URL

Every recommended tool has a built-in publish button on free. Use it. Do not route attendees through Vercel/Netlify dashboards on workshop day.

| Tool                | Publish click count | URL pattern                            | Custom domain on free? | Permanence            |
|---------------------|:--------------------:|----------------------------------------|:----------------------:|-----------------------|
| Lovable             | 1                    | `[name].lovable.app` [[55]](https://docs.lovable.dev/features/publish)             | ✗ [[56]](https://lovable.dev/faq/deployment/getting-started/publish-project)                | Persistent             |
| Bolt.new            | 1                    | `*.bolt.host` [[58]](https://support.bolt.new/faqs/hosting)                      | ✗                      | Persistent + "Claim URL" path to your own Netlify [[59]](https://support.bolt.new/integrations/netlify)      |
| v0                  | 1                    | Vercel production URL [[57]](https://v0.app/docs/deployments)                  | ✗ Hobby                | Persistent; Hobby is non-commercial only [[65]](https://vercel.com/docs/plans/hobby)        |
| Replit Starter      | 1                    | `*.replit.app`                         | ✗                      | ⚠ Repls sleep at 5 min, only 10 Agent checkpoints/mo [[17]](https://p0stman.com/guides/replit-limitations) |
| Claude Artifacts    | 1                    | `claude.ai/public/artifacts/<id>` [[60]](https://support.claude.com/en/articles/9547008-publishing-and-sharing-artifacts)            | ✗                      | ⚠ Viewers see Claude login wall [[61]](https://www.shareduo.com/blog/claude-artifacts-not-working-for-others) |
| ChatGPT Canvas      | 1                    | `chatgpt.com/canvas/shared/<id>` [[62]](https://help.openai.com/en/articles/9930697-what-is-the-canvas-feature-in-chatgpt-and-how-do-i-use-it)      | ✗                      | Persistent             |

**Generic hosts as fallback** when you need to migrate the build off the generator:

| Host                                                | Free-tier limit                                       | Source                                                                          |
|-----------------------------------------------------|-------------------------------------------------------|---------------------------------------------------------------------------------|
| [Cloudflare Pages](https://pages.cloudflare.com)    | 500 builds/mo, **unlimited bandwidth**, 20-min build cap | [[63]](https://developers.cloudflare.com/pages/platform/limits/)                                                                              |
| [Netlify](https://netlify.com)                      | 300 credits/mo (15/deploy, 20/GB), pauses on overrun  | [[64]](https://www.netlify.com/pricing/)                                                                              |
| [Vercel Hobby](https://vercel.com)                  | 100 GB bandwidth, **non-commercial only**             | [[65]](https://vercel.com/docs/plans/hobby)                                                                              |
| [GitHub Pages](https://pages.github.com)            | 1 GB site, 100 GB/mo soft, **public repos + static only** | [[66]](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)                                                                              |

**Cloudflare Pages wins for workshop fallback** — unlimited bandwidth means a viral demo can't bankrupt you [[63]](https://developers.cloudflare.com/pages/platform/limits/).

**Sharing in the room.** Generate one QR per URL with QRStuff or Canva — both free, static, unlimited scans, native iOS/Android camera readable [[67]](https://www.qrstuff.com/) [[68]](https://www.canva.com/qr-code-generator/). Display on the projector; attendees scan with their own phones. Don't email links — captive-portal browsers eat them.

## 6. Failure modes seen in the wild + mitigations

These keep showing up across multiple host write-ups [[73]](https://benzatine.com/news-room/unlocking-app-creation-insights-from-a-vibe-coding-workshop) [[78]](https://annaarteeva.medium.com/choosing-your-ai-prototyping-stack-lovable-v0-bolt-replit-cursor-magic-patterns-compared-9a5194f163e9):

| Failure                                                                                                | Mitigation                                                                                          |
|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Venue wifi saturates / drops [[39]](https://wifit.net/wifi-and-internet-solutions-for-hackathons/)                                                                  | Instructor phone hotspot, cellular plan B [[76]](https://theschoolhousemommy.wordpress.com/2017/12/14/vipkid-backup-plans-a-hotspot-tutorial/)                                                                |
| Shared NAT → "too many sessions from 1 IP" [[69]](https://community.openai.com/t/i-am-the-it-admin-from-a-school-and-we-are-encounter-the-error-of-78-many-sessions-from-1-ip/270490)                                                                | Pre-warm accounts off-venue [[52]](https://www.craftamplify.com/ai-frontend-coding/prep); split between two tools                                              |
| Lovable outage (314+ logged since May 2025, recent incidents up to 10 h+) [[71]](https://statusgator.com/services/lovable)                                  | Bolt.new ready as backup; pre-built starter repo                                                    |
| Cursor SheerID "Verification Limit Exceeded" when many .edu signups [[74]](https://forum.cursor.com/t/student-verification-issues/133734)                          | Don't depend on Cursor day-of; queue verifications over a week                                      |
| Claude SMS verification rejects VoIP / no-phone attendees [[43]](https://blog.laozhang.ai/en/posts/claude-verification-guide)                                                 | Continue-with-Google bypass [[42]](https://www.calilio.com/blogs/how-to-use-claude-ai-without-a-phone-number); pre-provisioned host accounts                                                  |
| Free-tier credit exhaustion mid-build [[2]](https://designlab.com/blog/best-vibe-coding-tools)                                                                | Constrain scope to ≤1-2 prompts on Lovable; switch to Bolt for iteration                            |
| Non-coder hits paywall on first prompt (Cursor, Replit) [[70]](https://manus.im/blog/vibe-coding-tools-non-coder-review)                                            | Don't pick those for first-touch                                                                    |
| Demo collapses under real testing (no planning step) [[77]](https://medium.com/design-bootcamp/we-vibe-coded-our-way-to-nowhere-and-learned-a-lot-66ca3e9ac969)                                                   | Force 10 min of "what does the app do" before the first prompt                                      |
| Beautiful prototype, broken on second prompt [[72]](https://www.fndtns.org/blog/pejman-vibe-coding/)                                                          | Frequent commits + a forked starter template so the LLM can pin bugs to a commit                    |

The most consistent cross-host recommendation: **keep two tools warm and stay flexible** [[73]](https://benzatine.com/news-room/unlocking-app-creation-insights-from-a-vibe-coding-workshop). One facilitator who has run many sessions describes converging on Lovable as default *after* starting with Bolt and v0 — the friction with non-coders is what drove the migration [[78]](https://annaarteeva.medium.com/choosing-your-ai-prototyping-stack-lovable-v0-bolt-replit-cursor-magic-patterns-compared-9a5194f163e9).

## 7. The runbook (TL;DR for the host)

**T-48 h.**
1. Email attendees: create Lovable + Bolt.new accounts using Continue-with-Google. Include screenshots [[52]](https://www.craftamplify.com/ai-frontend-coding/prep).
2. Build one reference app in Lovable yourself; save the share URL.
3. Fork a public starter repo (any minimal Vite/React) — backup if both generators fail [[72]](https://www.fndtns.org/blog/pejman-vibe-coding/).

**T-2 h.**
1. Charge your phone. Enable hotspot. Tell venue IT how many SSIDs you need [[39]](https://wifit.net/wifi-and-internet-solutions-for-hackathons/).
2. Print 3 QR codes: Lovable login, Bolt login, the workshop's shared starter repo.

**T-0.**
1. 10 min: "what does your app do?" — forced planning step, ungoverned by LLM [[77]](https://medium.com/design-bootcamp/we-vibe-coded-our-way-to-nowhere-and-learned-a-lot-66ca3e9ac969).
2. 90 min: build in Lovable. One prompt → preview → one revision prompt. Discourage debug rabbit holes.
3. 20 min: hit Publish. Generate QR. Show your app to the person next to you.

**If wifi melts → flip to hotspot.** If Lovable is down → flip everyone to Bolt and shorten scope to "landing page". If both fail → the starter repo plus Claude Artifacts (runs inline in chat) is enough to ship something visible [[8]](https://www.mindstudio.ai/blog/what-is-claude-generative-ui-vs-canvas-artifacts).

**Total host spend.**
- **Free path:** $0. Lovable + Bolt free tiers cover one app per attendee with no iteration room.
- **Comfort path:** $25 (one Lovable Pro for the host, attendees on free) [[12]](https://lovable.dev/pricing).
- **Insurance path:** $50 (Lovable Pro + a Cloudflare Pages-backed static repo).

The $100-250/mo "vibe-coding budget" reported for solo builders [[27]](https://hatchworks.com/blog/gendd/cost-of-vibe-coding/) does **not** apply at workshop scale, because three hours of guided activity is well below a single user's monthly burn.

## 8. What this report did *not* answer

- No named-host, dollar-itemised post-mortem of a vibe-coding workshop ("I taught 20 strangers Lovable for $X") was found — workshop budgets here are extrapolated from per-seat pricing [[27]](https://hatchworks.com/blog/gendd/cost-of-vibe-coding/).
- No first-person Reddit/HN thread of a vibe-coding workshop killed specifically by conference wifi; the wifi-fail evidence is industry-vendor framing [[39]](https://wifit.net/wifi-and-internet-solutions-for-hackathons/).
- Bolt.new's *total* first-load weight including npm dependencies is not publicly documented — only the <1 MB WebContainer runtime is confirmed [[29]](https://changelog.com/jsparty/178).

If you run this workshop, write up your spend, your wifi survival rate, and what broke. Future Scout runs would pick up your post and tighten these numbers.
