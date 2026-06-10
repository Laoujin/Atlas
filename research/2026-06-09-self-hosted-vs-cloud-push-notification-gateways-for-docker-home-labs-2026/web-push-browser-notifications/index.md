---
title: "Web Push (Browser Notifications): How They Work"
date: 2026-06-09
depth: ceo
format: md
topic: "Web push (browser notifications)"
topic_raw: "Web push (browser notifications)"
issue: 213
tags: [web-push, notifications, service-workers, browser-api]
summary: "Web push notifications deliver asynchronous messages to browsers via the Push API and service workers, supporting modern browsers with emerging Declarative Web Push standardization."
citations: 5
reading_time_min: 2
cost_usd: 0.19
duration_sec: 58
model: "Haiku 4.5"
---

> **TL;DR**: Web push notifications let websites deliver real-time alerts to opted-in users even when the browser is closed, using service workers as background handlers. Requires HTTPS, user permission, and a push service provider. A new Declarative Web Push standard (W3C Working Draft 2026) simplifies implementation by removing the need for service worker code.

## How It Works

Web push relies on three core pieces: a service worker (background script), the Push API, and a push service provider [[1]](https://developer.mozilla.org/en-US/docs/Web/API/Push_API).

The flow is straightforward [[2]](https://www.revechat.com/blog/web-push-notifications/):

1. **User opts in** to receive notifications via browser permission prompt
2. **Browser creates a subscription** with a unique endpoint URL and encryption keys
3. **Server sends push message** to the push service (e.g., Google's FCM for Chrome)
4. **Push service delivers** the notification to the browser, queuing it if the user is offline
5. **Service worker handles** the incoming message and displays the notification

All modern browsers require HTTPS and user opt-in before any notification can be sent.

## Browser Support & Limitations

Web push works across **Chrome, Firefox, and Edge** natively [[3]](https://www.magicbell.com/blog/browser-notifications). Safari has custom support via Apple Push Notification Service (APNS), with a significant caveat: iOS users in the EU can no longer install PWAs to their home screen as of iOS 17.4, blocking Safari browser notifications for that region.

**Key implementation requirement**: Service workers must be active to intercept push events. Firefox notably can't send notifications to inactive websites, limiting reach compared to Chrome and Edge [[4]](https://izooto.com/blog/chrome-2026-web-push-update-what-it-means-for-publishers).

## Security & Practical Considerations

The subscription endpoint is a sensitive capability URL—knowledge of it alone is sufficient to send messages, so it must be stored securely server-side [[1]](https://developer.mozilla.org/en-US/docs/Web/API/Push_API). Messages are encrypted end-to-end using VAPID (Voluntary Application Server Identification) keys.

Notification format is limited: up to 70 characters for the header, 250 for the body, plus optional icons and action buttons [[2]](https://www.revechat.com/blog/web-push-notifications/).

## Emerging: Declarative Web Push (2026)

A new standard is maturing that simplifies web push: **Declarative Web Push** [[5]](https://aimtell.com/blog/state-of-declarative-web-push-2026). Instead of writing service worker code to handle push events, you send plain JSON with notification details. The browser renders it directly without executing any service worker logic.

Apple led implementation across iOS, iPadOS, and macOS. Mozilla has a positive standards position, and it's now in the W3C Push API Working Draft. The approach enables progressive enhancement—the same payload works on both supporting and non-supporting browsers, making adoption risk-free [[5]](https://aimtell.com/blog/state-of-declarative-web-push-2026).

## When to Use

Web push is ideal for time-sensitive alerts (news, messages, updates) where you need to reach users outside the browser. Tradeoffs: requires significant browser support, user opt-in friction, and infrastructure for message queuing and delivery at scale.
