---
title: "Cloud relays: Pushover vs Pushbullet vs Telegram bots vs Slack webhooks"
date: 2026-06-09
depth: deep
format: md
topic: "Cloud-relay services: Pushover, Pushbullet, Telegram bots, Slack webhooks"
topic_raw: "Cloud-relay services: Pushover, Pushbullet, Telegram bots, Slack webhooks"
issue: 213
tags: [notifications, pushover, pushbullet, telegram, slack, homelab, docker, cloud]
summary: "Pushover is the homelab default — one-time $5, alert-grade features, best privacy; Telegram bots are the free power option; Slack webhooks suit team labs but are deprecation-prone; Pushbullet is the laggard to avoid."
cover: cover.svg
citations: 48
reading_time_min: 10
cost_usd: 4.80
duration_sec: 483
model: "Opus 4.8"
---

> **Decision.** For a docker-native homelab, **[Pushover](https://pushover.net)** is the default pick: a one-time **$4.99 per platform** [[6]](https://pushover.net/pricing), purpose-built notification apps, emergency alerts that retry until acknowledged [[1]](https://pushover.net/api), the strongest privacy posture [[34]](https://support.pushover.net/i46-are-messages-notifications-encrypted), and 14 years under stable independent ownership [[40]](https://support.pushover.net/i45-who-runs-pushover). Pick **[Telegram bots](https://core.telegram.org/bots)** if you want **$0 forever** plus rich formatting and inline buttons, and don't mind that bot traffic is never end-to-end encrypted [[31]](https://telegram.org/faq). Pick **[Slack incoming webhooks](https://api.slack.com/messaging/webhooks)** only if your lab already lives in Slack — ⚠ legacy webhooks are flagged for removal and the free plan caps history at 90 days [[47]](https://docs.slack.dev/legacy/legacy-custom-integrations/legacy-custom-integrations-incoming-webhooks/)[[48]](https://slack.com/help/articles/27204752526611-Feature-limitations-on-the-free-version-of-Slack). **Avoid [Pushbullet](https://www.pushbullet.com)** as an alerting backend: a throttled free tier [[9]](https://beebom.com/pushbullet-alternatives/), the weakest privacy record [[37]](https://www.androidpolice.com/pushbullet-play-store-ai-based-app-compliance-notices/), and the thinnest tooling support [[18]](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/configure-telegram/).

## These are three categories, not four picks (read this first)

The biggest framing error is treating all four as interchangeable "send my phone a notification" services. They split into three delivery models:

- **Personal push apps (Pushover, Pushbullet).** Dedicated mobile/desktop apps that exist *only* to receive your notifications. Pushover is the pure case — a paid app whose sole job is displaying pushes [[1]](https://pushover.net/api). Pushbullet is a cross-device *sync* tool (SMS mirroring, file transfer) that happens to expose a push API [[2]](https://docs.pushbullet.com/).
- **Chat-bot relay (Telegram).** Your alert lands as a message inside a normal Telegram conversation with a bot you created — not a dedicated notification app [[4]](https://core.telegram.org/bots/api). You read it in the same Telegram client you use for chatting.
- **Team-chat webhook (Slack).** Your alert posts into a Slack *channel* via a secret webhook URL [[5]](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/). Built for a team's shared workspace, not a personal phone.

```
                          ┌─ Pushover ──► dedicated push app  (personal, paid)
  app / alert source ──►  ├─ Pushbullet ► sync app + push     (personal, freemium)
   (curl / Apprise /      ├─ Telegram ──► bot chat message    (chat client, free)
    Uptime Kuma / HA)     └─ Slack ─────► team channel post   (workspace, freemium)
```

This matters because it drives everything downstream: Pushover's whole product is *alert quality* (priorities, retries, custom sounds); Telegram and Slack inherit the strengths and the privacy/retention model of a chat platform you don't control.

## At a glance

| Axis                     | Pushover                       | Pushbullet                  | Telegram bot                  | Slack webhook                 |
| ------------------------ | ------------------------------ | --------------------------- | ----------------------------- | ----------------------------- |
| Model                    | Personal push app [1]          | Sync app + push [2]         | Chat-bot relay [4]            | Team-channel post [5]         |
| Cost                     | **$4.99 once / platform** [6]  | Free*/Pro $39.99/yr [8]     | **Free** [10]                 | Free*/Pro ~€8/user/mo [11]    |
| iOS app                  | ✓ dedicated [1]                | ✓ [3]                       | ✓ (Telegram app) [4]          | ✓ (Slack app) [5]             |
| Auth model               | app token + user key [1]       | access token [2]            | bot token + chat_id [4]       | secret webhook URL [5]        |
| Title / priority         | ✓ / ✓ (-2..2) [1]              | ✓ / ✗ [2]                   | ✓ / ✗ [4]                     | ✓ / ✗ [5]                     |
| Emergency retry-til-ack  | ✓ priority 2 [1]               | ✗                           | ✗                             | ✗                             |
| Rich formatting          | HTML / monospace [1]           | plain [2]                   | HTML / MarkdownV2 [4]         | Block Kit blocks [5]          |
| Buttons                  | ✗ (URL only) [1]               | ✗                           | ✓ inline keyboard [4]         | ✓ Block Kit [5]               |
| Attachments              | ✓ image ≤5 MB [1]              | ✓ file push [2]             | ✓ photo/doc [4]               | ✗ via webhook [5]             |
| Msg length cap           | 1024 chars [22]                | —                           | 4096 chars [25]               | Block Kit blocks [5]          |
| E2E encryption           | ✓ optional (v5+) [34]          | ✗                           | ✗ bots never E2E [31]         | ✗ [38]                        |
| Apprise / shoutrrr       | ✓ / ✓ [13][14]                 | ✓ / ✓ [13][14]              | ✓ / ✓ [13][14]                | ✓ / ✓ [13][14]                |
| Longevity verdict        | **stable 14 yrs** [40]         | declining [44]              | **very active** [45]          | deprecation risk [46]         |

[1]: https://pushover.net/api
[2]: https://docs.pushbullet.com/
[3]: https://github.com/caronc/apprise/wiki/Notify_pushbullet
[4]: https://core.telegram.org/bots/api
[5]: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/
[6]: https://pushover.net/pricing
[8]: https://www.androidauthority.com/pushbullet-pro-656157/
[10]: https://www.botract.com/blog/telegram-bot-cost-pricing-guide
[11]: https://slack.com/pricing
[13]: https://github.com/caronc/apprise
[14]: https://github.com/containrrr/shoutrrr/blob/main/docs/services/overview.md
[22]: https://support.pushover.net/i12-message-size-and-frequency-limitations
[25]: https://rollout.com/integration-guides/telegram-bot-api/api-essentials
[26]: https://docs.slack.dev/apis/web-api/rate-limits/
[31]: https://telegram.org/faq
[34]: https://support.pushover.net/i46-are-messages-notifications-encrypted
[38]: https://slack.com/help/articles/203457187-Customize-data-retention-in-Slack
[40]: https://support.pushover.net/i45-who-runs-pushover
[44]: https://windowsforum.com/threads/pushbullet-decline-to-phone-link-a-practical-windows-migration-guide.393652/
[45]: https://core.telegram.org/bots/api-changelog
[46]: https://docs.slack.dev/changelog/2024-09-legacy-custom-bots-classic-apps-deprecation/

\* Free tiers are constrained — see Pricing below.

## Pricing & the real total cost

| Service     | Up-front      | Recurring          | Free-tier ceiling                              | Source        |
| ----------- | ------------- | ------------------ | ---------------------------------------------- | ------------- |
| Pushover    | $4.99/platform| **none**           | 10,000 msgs/mo free, per-account [22]          | [6][22]       |
| Telegram    | none          | **none**           | ~unlimited (rate-limited, not quota'd) [10]    | [10][23]      |
| Slack       | none          | Pro ~€8/user/mo    | 90-day history, 10 app slots [48]              | [11][48]      |
| Pushbullet  | none          | Pro $39.99/yr [8]  | ~100–500 pushes/mo then throttled [9][27]      | [8][9][27]    |

[6]: https://pushover.net/pricing
[8]: https://www.androidauthority.com/pushbullet-pro-656157/
[9]: https://beebom.com/pushbullet-alternatives/
[10]: https://www.botract.com/blog/telegram-bot-cost-pricing-guide
[11]: https://slack.com/pricing
[22]: https://support.pushover.net/i12-message-size-and-frequency-limitations
[23]: https://core.telegram.org/bots/faq
[27]: https://www.androidpolice.com/2016/07/27/pushbullet-will-limit-api-based-pushes-500-per-month-free-accounts-starting-august-1/
[48]: https://slack.com/help/articles/27204752526611-Feature-limitations-on-the-free-version-of-Slack

- **Pushover — best value.** A single $4.99 one-time purchase per platform (iPhone/iPad, Android, Desktop), no subscription [[6]](https://pushover.net/pricing). Every account sends up to 10,000 messages/month free — and as of **May 1 2026** that quota is pooled *per account* across all your apps rather than per-application [[7]](https://blog.pushover.net/posts/2026/4/app-limits). A homelab realistically pays $5–10 total, once.
- **Telegram — genuinely free.** No per-message charges, no monthly API fee, no cap on the number of bots [[10]](https://www.botract.com/blog/telegram-bot-cost-pricing-guide). The only "cost" is the rate limit (below). This is the zero-budget winner.
- **Slack — free works but squeezes.** Incoming webhooks function on the Free plan but count against the **10-app integration cap**, and messages older than 90 days become inaccessible behind the paywall [[12]](https://comparetiers.com/blog/slack-free-plan-limitations-2026)[[48]](https://slack.com/help/articles/27204752526611-Feature-limitations-on-the-free-version-of-Slack). Pro is ~€8.25/user/month (~€6.75/user/month annual) [[11]](https://slack.com/pricing) — overkill for a notification sink.
- **Pushbullet — the hidden-cost option.** The free tier is throttled (sources cite ~100/month for message sending [[9]](https://beebom.com/pushbullet-alternatives/)[[42]](https://www.ghacks.net/2015/11/17/pushbullet-pro-and-free-version-limitations/), and historically 500/month for API pushes [[27]](https://www.androidpolice.com/2016/07/27/pushbullet-will-limit-api-based-pushes-500-per-month-free-accounts-starting-august-1/)), pushing you to Pro at $4.99/mo or $39.99/yr [[8]](https://www.androidauthority.com/pushbullet-pro-656157/) — i.e. it costs *more per year* than Pushover costs once.

## Homelab / Docker integration

All four are first-class in the notification dispatch layer, but coverage thins out toward Pushbullet. [Apprise](https://github.com/caronc/apprise) `⭐ 16.7k` [[13]](https://github.com/caronc/apprise) and [shoutrrr](https://github.com/containrrr/shoutrrr) `⭐ 1.6k` [[15]](https://github.com/containrrr/shoutrrr) (the engine inside [Watchtower](https://containrrr.dev/watchtower)) both support **all four** via one-line URL schemas [[13]](https://github.com/caronc/apprise)[[14]](https://github.com/containrrr/shoutrrr/blob/main/docs/services/overview.md).

| Integration            | Pushover | Pushbullet | Telegram | Slack | Source     |
| ---------------------- | :------: | :--------: | :------: | :---: | ---------- |
| Apprise URL schema     | ✓ `pover://` | ✓ `pbul://` | ✓ `tgram://` | ✓ `slack://` | [13]   |
| shoutrrr / Watchtower  | ✓        | ✓          | ✓        | ✓     | [14][19]   |
| Uptime Kuma            | ✓        | ✓          | ✓        | ✓     | [16]       |
| Home Assistant         | ✓        | ✓          | ✓        | ✓     | [17]       |
| Grafana contact point  | ✓        | **✗**      | ✓        | ✓     | [18]       |
| n8n native node        | ✓        | **✗**      | ✓        | ✓     | [20]       |

[13]: https://github.com/caronc/apprise
[14]: https://github.com/containrrr/shoutrrr/blob/main/docs/services/overview.md
[16]: https://github.com/louislam/uptime-kuma
[17]: https://www.home-assistant.io/integrations/telegram/
[18]: https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/configure-telegram/
[19]: https://containrrr.dev/watchtower/notifications/
[20]: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.pushover/

- **[Uptime Kuma](https://github.com/louislam/uptime-kuma)** `⭐ 87.8k` ships dedicated providers for all four among its 90+ channels [[16]](https://github.com/louislam/uptime-kuma).
- **[Home Assistant](https://www.home-assistant.io)** has first-class notify integrations for every one, including a rich Telegram-bot integration with send/edit/receive actions [[17]](https://www.home-assistant.io/integrations/telegram/).
- **[Grafana](https://grafana.com)** alerting and **[n8n](https://n8n.io)** both expose Pushover, Telegram and Slack as native targets but have **no Pushbullet** option [[18]](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/configure-telegram/)[[20]](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.pushover/).

**Raw `curl` from a container** — ease ranks Pushover ≈ Slack > Telegram > Pushbullet:

```bash
# Pushover — one POST, two tokens
curl -s -F "token=$APP_TOKEN" -F "user=$USER_KEY" \
     -F "message=disk 90% on nas01" https://api.pushover.net/1/messages.json   # [1]

# Slack — one secret URL, JSON body
curl -s -X POST -H 'Content-type: application/json' \
     --data '{"text":"disk 90% on nas01"}' "$SLACK_WEBHOOK_URL"                # [5]

# Telegram — needs chat_id first (see ⚠ below)
curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
     -d chat_id="$CHAT_ID" -d text="disk 90% on nas01"                        # [21]
```

[1]: https://pushover.net/api
[5]: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/
[21]: https://gist.github.com/dideler/85de4d64f66c1966788c1b2304b9caf1

⚠ **Telegram has a setup gotcha:** a bot cannot message you until you message *it* first, then you scrape the numeric `chat_id` out of a `getUpdates` call before any `sendMessage` works [[21]](https://gist.github.com/dideler/85de4d64f66c1966788c1b2304b9caf1). Pushover (paste two tokens) and Slack (paste one URL) have no such dance.

## Reliability, rate limits & message sizes

| Limit                | Pushover                  | Telegram bot               | Slack webhook            | Pushbullet            |
| -------------------- | ------------------------- | -------------------------- | ------------------------ | --------------------- |
| Throughput           | 10k msgs/mo/account [22]  | ~30 msg/s/bot [23]         | ~1 msg/s/channel [26]    | ~100–500/mo free [27] |
| Per-chat throttle    | n/a                       | ~1/s chat, 20/min group [24]| short bursts ok [26]    | header-surfaced [2]   |
| Message length       | 1024 chars [22]           | 4096 chars [25]            | Block Kit blocks [5]     | —                     |
| Over-limit response  | quota error               | HTTP 429 + `retry_after` [24]| HTTP 429 + `Retry-After` [26] | error            |
| Killer feature       | **emergency priority 2** [1]| 1000 msg/s paid broadcast [23]| — | — |

[1]: https://pushover.net/api
[2]: https://docs.pushbullet.com/
[5]: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/
[22]: https://support.pushover.net/i12-message-size-and-frequency-limitations
[23]: https://core.telegram.org/bots/faq
[24]: https://gramio.dev/rate-limits
[25]: https://rollout.com/integration-guides/telegram-bot-api/api-essentials
[26]: https://docs.slack.dev/apis/web-api/rate-limits/
[27]: https://www.androidpolice.com/2016/07/27/pushbullet-will-limit-api-based-pushes-500-per-month-free-accounts-starting-august-1/

- **Pushover's emergency priority 2** is the standout for alerting: a notification repeats until you acknowledge it — `retry` ≥ 30 s, `expire` ≤ 10,800 s (3 h), capped at 50 retries, with an optional acknowledgement callback [[1]](https://pushover.net/api). Nothing else here has it.
- **Telegram is built for throughput** — ~30 msg/s per bot globally (up to 1000/s with paid broadcasts) [[23]](https://core.telegram.org/bots/faq), but throttled to ~1 msg/s per chat and ~20/min per group, returning HTTP 429 with `retry_after` when breached [[24]](https://gramio.dev/rate-limits).
- **Slack webhooks are the tightest** — roughly 1 request/second per channel, short bursts tolerated [[26]](https://docs.slack.dev/apis/web-api/rate-limits/). Fine for alerts, bad for a chatty firehose.

**The resilience argument for using a cloud relay at all:** a monitoring system cannot reliably watch itself [[28]](https://seifrajhi.github.io/blog/securing-monitoring-stack-dead-man-switch/), so the alert path should live on infrastructure *separate* from the thing it monitors. The dead-man's-switch pattern routes an always-firing heartbeat through an external relay; when your local pipeline dies, the external service notices the silence and alerts you [[29]](https://training.promlabs.com/training/monitoring-and-debugging-prometheus/metrics-based-meta-monitoring/end-to-end-watchdog-alerts/). ⚠ The tradeoff is latency: self-hosters report third-party push can be noticeably delayed versus a local connection [[30]](https://blog.alexsguardian.net/posts/2023/09/12/selfhosting-ntfy). This is the strongest reason to keep a cloud relay in the mix even in an otherwise self-hosted lab — pair it with the self-hosted options ([covered in the companion piece](../self-hosted-gateways-ntfy-gotify-apprise/)).

## Privacy & security

Every option here means your alert content — hostnames, IPs, container names, stack traces — transits and is briefly stored on a third party's servers. The degree differs sharply.

- **Pushover — most privacy-forward.** TLS for all transport; message content is stored in plaintext only long enough to deliver, then deleted once delivery is verified (undeliverable messages purged after 21 days) [[34]](https://support.pushover.net/i46-are-messages-notifications-encrypted)[[35]](https://pushover.net/privacy). It also offers optional **client-side end-to-end encryption** (since app v5.0) that hides content even from Pushover's own servers [[34]](https://support.pushover.net/i46-are-messages-notifications-encrypted).
- **Telegram — commonly misunderstood.** Cloud Chats (private and group chats) use only server–client encryption and are explicitly **not** end-to-end encrypted; only Secret Chats add client–client E2E, and **all bot traffic runs over Cloud Chats** — so Telegram can read every bot alert [[31]](https://telegram.org/faq). Worse, a leaked **bot token grants full control**: anyone holding it can send as the bot and read chat data [[32]](https://www.gitguardian.com/remediation/telegram-bot-token), and hardcoded-token leaks have already exposed real customer PII [[33]](https://medium.com/@cameronbardin/hardcoded-secrets-strike-again-how-a-telegram-bot-token-exposed-customer-support-and-pii-cb412551239b). Treat the token like a password and revoke via BotFather if exposed.
- **Slack — admin-visible and retained.** Messages are stored server-side under admin-controlled retention policies [[38]](https://slack.com/help/articles/203457187-Customize-data-retention-in-Slack); workspace owners can export public/private channels and DMs to JSON [[39]](https://slack.com/help/articles/201658943-Export-your-workspace-data). On a workspace you don't own, "deleted" alerts may persist in compliance records beyond your control.
- **Pushbullet — weakest record.** With sync enabled it uploads SMS data, contact lists, and contact images to its servers [[36]](https://help.pushbullet.com/articles/play-store-privacy-policy/), and it has a documented history of Google Play privacy-disclosure friction over that data flow [[37]](https://www.androidpolice.com/pushbullet-play-store-ai-based-app-compliance-notices/).

**If alert payloads contain anything sensitive,** Pushover (with E2E) is the only cloud relay here that can keep content opaque to the relay operator — otherwise self-host.

## Service health & longevity (bus-factor)

| Service     | Run by                          | Momentum signal                            | Verdict           | Source     |
| ----------- | ------------------------------- | ------------------------------------------ | ----------------- | ---------- |
| Pushover    | Pushover, LLC (Chicago, indep.) | continuous since Mar 2012, quietly stable  | **low risk**      | [40][41]   |
| Telegram    | Telegram                        | Bot API 10.0 (May 2026), ~monthly releases | **low risk**      | [45]       |
| Slack       | Salesforce                      | legacy webhooks deprecated, classic apps die Nov 16 2026 | ⚠ migration risk | [46][47]   |
| Pushbullet  | Pushbullet, Inc.                | features paywalled, trust eroded → Phone Link migration | ⚠ declining | [42][44]   |

[40]: https://support.pushover.net/i45-who-runs-pushover
[41]: https://play.google.com/store/apps/details?id=net.superblock.pushover&hl=en-US
[42]: https://www.ghacks.net/2015/11/17/pushbullet-pro-and-free-version-limitations/
[44]: https://windowsforum.com/threads/pushbullet-decline-to-phone-link-a-practical-windows-migration-guide.393652/
[45]: https://core.telegram.org/bots/api-changelog
[46]: https://docs.slack.dev/changelog/2024-09-legacy-custom-bots-classic-apps-deprecation/
[47]: https://docs.slack.dev/legacy/legacy-custom-integrations/legacy-custom-integrations-incoming-webhooks/

- **Pushover — the quiet standout.** Run by Pushover, LLC (formerly named *Superblock, LLC* — the source of the misread "Superblock acquisition" rumor; it's a rename, visible in the Android package `net.superblock.pushover`), a private, self-funded Chicago company operating continuously since March 2012 [[40]](https://support.pushover.net/i45-who-runs-pushover)[[41]](https://play.google.com/store/apps/details?id=net.superblock.pushover&hl=en-US). A 14-year track record of understated reliability.
- **Telegram — healthiest by momentum.** The Bot API shipped **version 10.0 on May 8 2026**, roughly 8 versions in 13 months (1–2 month cadence) [[45]](https://core.telegram.org/bots/api-changelog) — free, actively developed, vast ecosystem.
- **Slack — real deprecation risk for hobbyists.** Legacy custom bots died March 31 2025; classic apps stop working **November 16 2026** [[46]](https://docs.slack.dev/changelog/2024-09-legacy-custom-bots-classic-apps-deprecation/); legacy incoming webhooks are explicitly flagged as "deprecated and possibly removed in the future," steering you to recreate them inside a Slack app [[47]](https://docs.slack.dev/legacy/legacy-custom-integrations/legacy-custom-integrations-incoming-webhooks/). Plan for migration churn.
- **Pushbullet — declining, not dead.** It moved long-standing free features behind a $4.99/mo Pro tier and capped free messaging [[42]](https://www.ghacks.net/2015/11/17/pushbullet-pro-and-free-version-limitations/), and Manifest-V3 friction plus paywalling drove migration toward Microsoft Phone Link [[44]](https://windowsforum.com/threads/pushbullet-decline-to-phone-link-a-practical-windows-migration-guide.393652/). It *is* still maintained — updated June 2026, with MMS added in April 2026 [[43]](https://www.appbrain.com/app/pushbullet-sms-on-pc-and-more/com.pushbullet.android) — but it has the weakest forward story of the four for alerting.

## Bottom line

- **Default homelab pick → [Pushover](https://pushover.net):** $4.99 once, dedicated apps, emergency retry-til-ack, best privacy, 14-year stability. The closest thing to "buy once, forget" in this space [[6]](https://pushover.net/pricing)[[1]](https://pushover.net/api).
- **Zero-budget power user → [Telegram bot](https://core.telegram.org/bots):** free, rich formatting + inline buttons, huge ecosystem, very active API — accept that bot traffic is not E2E and guard the token [[31]](https://telegram.org/faq)[[45]](https://core.telegram.org/bots/api-changelog).
- **Already-in-Slack team lab → [Slack webhook](https://api.slack.com/messaging/webhooks):** trivial to wire up, but budget for deprecation migrations and the 90-day free-plan ceiling [[47]](https://docs.slack.dev/legacy/legacy-custom-integrations/legacy-custom-integrations-incoming-webhooks/)[[48]](https://slack.com/help/articles/27204752526611-Feature-limitations-on-the-free-version-of-Slack).
- **Avoid for new alerting setups → [Pushbullet](https://www.pushbullet.com):** costs more per year than Pushover costs once, weakest privacy and tooling support, declining momentum [[37]](https://www.androidpolice.com/pushbullet-play-store-ai-based-app-compliance-notices/)[[44]](https://windowsforum.com/threads/pushbullet-decline-to-phone-link-a-practical-windows-migration-guide.393652/).
- **Architecture tip:** put [Apprise](https://github.com/caronc/apprise) `⭐ 16.7k` in front as your dispatch layer and target whichever relay you pick — then swapping relays later is a one-line URL change, not a rewrite [[13]](https://github.com/caronc/apprise). And keep the relay on infrastructure separate from what it monitors [[28]](https://seifrajhi.github.io/blog/securing-monitoring-stack-dead-man-switch/).
