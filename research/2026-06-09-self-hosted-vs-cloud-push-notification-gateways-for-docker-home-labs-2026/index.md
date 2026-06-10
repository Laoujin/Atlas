---
layout: expedition
title: "Self-hosted vs cloud push notification gateways for Docker home labs (2026)"
date: 2026-06-09
topic: "Compare self-hosted and cloud push notification gateways for Docker-native home or lab infrastructure (2026)."
format: md
tags: [notifications, docker, homelab, self-hosted, ntfy, pushover, apprise]
summary: "ntfy + Apprise is the composable self-hosted base; iOS forces a cloud relay unless you accept ntfy's APNs hop; Pushover is the pragmatic hybrid pick; WhatsApp and web push remain cloud-dependent in 2026."
cover: cover.svg
synthesis: true
children:
  - slug: self-hosted-gateways-ntfy-gotify-apprise
    title: "Self-hosted gateways: ntfy, Gotify, Apprise"
    depth: deep
    status: success
    summary: "ntfy is the feature-rich default, Gotify the dead-simple minimalist, and Apprise the routing layer that feeds both — they are complementary, not three picks for one slot."
    citations: 40
    reading_time_min: 8
  - slug: cloud-relay-services-pushover-pushbullet-telegram-bots-slack-webhooks
    title: "Cloud-relay services: Pushover, Pushbullet, Telegram bots, Slack webhooks"
    depth: deep
    status: success
    summary: "Pushover is the homelab default — one-time $5, alert-grade features, best privacy; Telegram bots are the free power option; Slack webhooks suit team labs but are deprecation-prone; Pushbullet is the laggard to avoid."
    citations: 48
    reading_time_min: 10
  - slug: docker-native-wiring-patterns
    title: "Docker-native wiring patterns"
    depth: standard
    status: success
    summary: "Five composable patterns — named bridge networks, external proxy network, socket proxy, service_healthy ordering, and secrets mounts — cover 90% of home-lab notification stack wiring."
    citations: 15
    reading_time_min: 7
  - slug: whatsapp-integration-options
    title: "WhatsApp integration options"
    depth: ceo
    status: success
    summary: "Meta Cloud API for scale, BSPs for features, alternatives for fast setup."
    citations: 10
    reading_time_min: 2
  - slug: web-push-browser-notifications
    title: "Web push (browser notifications)"
    depth: ceo
    status: success
    summary: "Web push notifications deliver asynchronous messages to browsers via the Push API and service workers, supporting modern browsers with emerging Declarative Web Push standardization."
    citations: 5
    reading_time_min: 2
cost_usd: 11.26
duration_sec: 1529
citations: 118
reading_time_min: 29
issue: 213
model: "Sonnet 4.6"
---

The most important reframe: **self-hosted and cloud relay are not competing choices — they are layers**. The common production homelab stack in 2026 is [Apprise](https://github.com/caronc/apprise) [[1]](https://github.com/caronc/apprise) as a stateless fan-out router sitting above [ntfy](https://ntfy.sh) [[2]](https://github.com/binwiederhier/ntfy) as the delivery server, with one or two cloud sinks (Pushover, Telegram) wired in as Apprise targets for mobile reach. The "vs" framing collapses once you see Apprise's `ntfy://topic/` and `pushover://token@user/` as equally valid URLs in the same config file.

**iOS is the critical architectural constraint** that every other decision flows from. Gotify has no iOS app and no credible path to one [[3]](https://heywoodlh.io/gotify-ios-notifications). ntfy ships its own iOS app but must relay through ntfy's cloud APNs bridge — your message transits ntfy.sh's servers for a moment [[4]](https://github.com/binwiederhier/ntfy/issues/1680). The only way to keep iOS delivery fully self-contained is Pushover ($4.99 one-time) [[5]](https://pushover.net/pricing) or a Telegram bot (free, but bot traffic is never end-to-end encrypted [[6]](https://telegram.org/faq)). This single constraint explains why most "pure self-host" deployments quietly add Pushover as the iOS sink.

**The Docker wiring is effectively solved.** Five composable patterns — named bridge network for same-host service groups, an external `proxy` network shared with Traefik, a socket proxy to avoid bind-mounting the Docker daemon socket, `depends_on: condition: service_healthy` for startup ordering, and `_FILE` env-var secrets — cover the overwhelming majority of notification stack configurations [[7]](https://docs.docker.com/compose/how-tos/networking/)[[8]](https://github.com/tecnativa/docker-socket-proxy). Apprise reaching ntfy by service name (`http://ntfy:80/topic`) with no published port is the canonical example of why this matters: zero host-IP coupling, zero firewall rules.

**Maintenance diverges sharply at 12 months.** ntfy and Gotify are single Go binaries with minimal runtime dependencies; a `docker pull` and restart is the entire upgrade path. Apprise is a Python package with ~143 upstream service connectors [[9]](https://deepwiki.com/caronc/apprise): every time Slack, Discord, or Telegram changes an API, a connector may drift. The practical implication is that Apprise upgrades need testing against your active sinks, not just a blind pull. Pushbullet compounds this: it is in active decline with the thinnest tooling support of any evaluated service [[10]](https://windowsforum.com/threads/pushbullet-decline-to-phone-link-a-practical-windows-migration-guide.393652/) and should be excluded from new stacks.

**WhatsApp and web push are edge cases with hard cloud floors.** Meta deprecated its on-premise Business API in October 2025 [[11]](https://www.messagecentral.com/blog/whatsapp-business-api-complete-guide) — there is no longer a self-hosted free path to WhatsApp's official network. [Evolution API](https://github.com/evolution-foundation/evolution-api) with a Baileys backend works but is brittle and terms-of-service grey. Web push requires HTTPS infrastructure, service workers, and browser opt-in; it is only worth the overhead for lab setups that already expose a browser-based dashboard to end users [[12]](https://developer.mozilla.org/en-US/docs/Web/API/Push_API).

## Recommendation by use-case profile

| Profile                        | Primary stack                                             | iOS path                         | Cost     |
| ------------------------------ | --------------------------------------------------------- | -------------------------------- | -------- |
| **Pure self-host**             | ntfy + Apprise                                            | ntfy APNs relay (data hops ntfy.sh) [[4]][r4] | Free     |
| **Hybrid (best balance)**      | ntfy + Apprise → Pushover for iOS alerts                  | Pushover dedicated app [[5]][r5]  | $5 once  |
| **No-ops / low maintenance**   | Gotify (Android/web) + Telegram bot (mobile)              | Telegram app [[6]][r6]            | Free     |
| **Team lab (shared workspace)**| Apprise → Slack webhook + ntfy for personal alerts        | Slack app (deprecation risk [[13]][r13]) | Free tier |
| **Maximum channel breadth**    | Apprise as sole dispatch layer, all sinks as Apprise URLs | Target-dependent                 | Free     |

[r4]: https://github.com/binwiederhier/ntfy/issues/1680
[r5]: https://pushover.net/pricing
[r6]: https://telegram.org/faq
[r13]: https://docs.slack.dev/changelog/2024-09-legacy-custom-bots-classic-apps-deprecation/

The open question this expedition leaves: as ntfy's feature set (ACLs, priorities, action buttons, attachments, scheduled delivery [[14]](https://docs.ntfy.sh/publish/)) continues to expand and its GitHub star count clears 30k [[2]](https://github.com/binwiederhier/ntfy), at what point does Apprise's Python overhead become unnecessary for single-sink homelab deployments — and does ntfy eventually absorb the routing layer entirely?
