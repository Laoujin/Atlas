---
title: "WhatsApp Integration Options"
date: 2026-06-09
depth: ceo
format: md
topic: "WhatsApp integration options"
topic_raw: "WhatsApp integration options"
issue: 213
tags: [messaging, api, integration, saas, self-hosted]
summary: "Meta Cloud API for scale, BSPs for features, alternatives for fast setup."
citations: 10
reading_time_min: 2
cover: cover.svg
cost_usd: 0.25
duration_sec: 102
model: "Haiku 4.5"
---

> **Decision:** Pick **Meta Cloud API** if you have dev bandwidth and want lowest cost at volume; choose a **BSP (Twilio, WATI, Gupshup)** for UI + integrations + managed operations; use **Unipile or Evolution API** for fast onboarding with minimal red tape.

## The three paths

**Meta Cloud API (official, direct)** [[1]](https://developers.facebook.com/docs/whatsapp/cloud-api/) — Fully hosted by Meta, handles 500 msgs/sec. You pay Meta per delivered message; no infrastructure cost. Requires business verification and template approval (weeks). Best for: teams with engineering resources who want lowest cost at massive scale.

**Business Solution Providers (BSPs)** [[2]](https://www.messagecentral.com/blog/whatsapp-business-api-complete-guide) — Twilio [[3]](https://www.twilio.com/en-us/whatsapp/pricing), WATI [[4]](https://www.wati.io/pricing/), Gupshup [[5]](https://codingclave.com/guides/whatsapp-api-pricing-india-2026-comparison), Infobip [[6]](https://www.infobip.com/blog/best-whatsapp-api), and dozens more sit on top of Cloud API, bundling UI, integrations, and operations. You pay markup on messages (often 15–20%) plus tooling fees. Best for: SMBs and teams needing shared inbox, flows, and CRM connectors out of the box.

**Alternatives for faster onboarding** — Unipile [[7]](https://www.unipile.com/whatsapp-api-a-complete-guide-to-integration/) uses QR-code auth (no business verification) and ships in 2–3 days. Evolution API [[8]](https://github.com/evolution-foundation/evolution-api) ⭐ 2.8k is open-source, self-hosted on your infrastructure, supporting both Baileys (free, web-based) and Cloud API backends. Best for: prototypes, dev teams, or strict-control environments.

## Provider comparison

| Provider | Model | Setup | Messaging cost | Tooling | Best for |
|----------|-------|-------|-----------------|---------|----------|
| Meta (direct) | Cloud API | Weeks (business verification) | Pay Meta directly | Build your own | Engineering-heavy, massive scale |
| Twilio | Cloud API markup | Days (if verified account exists) | $0.005/msg + Meta fee | Good SMS interop | Existing Twilio users |
| WATI | Cloud API markup | Days | ~20% markup + $49–299/mo | Shared inbox, flows | SMBs, no-code teams |
| Gupshup | Cloud API markup | Days | High-volume rates | AI chatbot, localization | India/SEA markets |
| Unipile | Alternative API | 2–3 days (QR auth) | Unknown per-message | Managed | Speed over official channel |
| Evolution API | Self-hosted or Cloud API | Hours (Docker deploy) | Backend dependent | None (DIY) | Full control, dev teams |

## Cost illustration

At 1M marketing messages/month in the US [[9]](https://respond.io/blog/whatsapp-business-api-pricing):
- **Meta direct:** ~$25k (Meta fee only)
- **Twilio:** ~$30k ($25k + $5k markup)
- **WATI:** ~$35k+ ($25k + 20% + subscription)

For India or high volume, Gupshup's flat rates typically beat percentage markups.

## On-premise (deprecated)

Meta deprecated the on-premise Business API in October 2025. Self-hosted now means: Evolution API + Cloud API backend (still pays Meta), Baileys-based free options (technical, less reliable), or Unipile's managed service. No true "self-hosted free" path to Meta's official network remains [[2]](https://www.messagecentral.com/blog/whatsapp-business-api-complete-guide).
