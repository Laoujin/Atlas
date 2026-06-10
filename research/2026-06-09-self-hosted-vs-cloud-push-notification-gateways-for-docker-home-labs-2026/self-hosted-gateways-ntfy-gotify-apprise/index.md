---
title: "Self-hosted push gateways: ntfy vs Gotify vs Apprise"
date: 2026-06-09
depth: deep
format: md
topic: "Self-hosted gateways: ntfy, Gotify, Apprise"
topic_raw: "Self-hosted gateways: ntfy, Gotify, Apprise"
issue: 213
tags: [self-hosted, notifications, ntfy, gotify, apprise, homelab, docker]
summary: "ntfy is the feature-rich default, Gotify the dead-simple minimalist, and Apprise the routing layer that feeds both — they are complementary, not three picks for one slot."
cover: cover.svg
citations: 40
reading_time_min: 8
cost_usd: 4.74
duration_sec: 477
model: "Opus 4.8"
---

> **Decision.** These three don't compete for the same slot. **[ntfy](https://ntfy.sh)** [[1]](https://github.com/binwiederhier/ntfy) `⭐ 30.7k` is the feature-rich default — pick it for ACLs, priorities, attachments, action buttons, and the only credible self-hosted iOS path. **[Gotify](https://gotify.net)** [[4]](https://github.com/gotify/server) `⭐ 15.1k` is the minimalist — pick it for a 5-minute Docker install and < 50 MB RAM if Android/web-only is fine. **[Apprise](https://github.com/caronc/apprise)** [[6]](https://github.com/caronc/apprise) `⭐ 16.7k` is **not a server at all** — it's the routing layer that *sends to* ntfy, Gotify, and ~140 other services. The common homelab build is **Apprise as the dispatch fan-out + ntfy as the delivery endpoint.**

## The category split (read this first)

The single biggest misconception is that these are three interchangeable apps. They are two categories:

- **Push servers (ntfy, Gotify):** they own the full chain — a REST endpoint to publish, a message store, and *their own mobile apps* that receive. ntfy is "a simple HTTP-based pub-sub notification service" [[2]](https://ntfy.sh/); Gotify is "a simple server for sending and receiving messages in real-time per WebSocket" [[4]](https://github.com/gotify/server). Both are single Go binaries, no cloud dependency.
- **Notification router (Apprise):** a send-only library/CLI that normalizes one message out to ~143 upstream services via a common `service://creds@host/target` URL syntax [[18]](https://github.com/caronc/apprise/blob/master/README.md)[[19]](https://deepwiki.com/caronc/apprise). It has no app and never *receives* anything. Its companion [Apprise-API](https://github.com/caronc/apprise-api) [[7]](https://github.com/caronc/apprise-api) `⭐ 1.2k` wraps it as a REST microservice.

Crucially, **ntfy and Gotify are targets Apprise dispatches to** [[6]](https://github.com/caronc/apprise) — `ntfy://topic/` and `gotify://host/token` are valid Apprise URLs. So "Apprise vs ntfy" is the wrong frame; it sits a layer *above*.

```
  app / alert source ──► Apprise (route + fan-out) ──┬──► ntfy   ──► phone app
                                                     ├──► Gotify ──► phone app
                                                     ├──► email / SMS
                                                     └──► Discord / Telegram / ...
```

## At a glance

| Axis                  | ntfy                          | Gotify                       | Apprise                          |
| --------------------- | ----------------------------- | ---------------------------- | -------------------------------- |
| What it is            | Pub-sub push server [1]       | Minimal push server [4]      | Send-only router/library [18]    |
| GitHub stars          | ⭐ 30.7k [1]                   | ⭐ 15.1k [4]                  | ⭐ 16.7k [6]                      |
| Language / footprint  | Go, ~20–50 MB (est.)          | Go, **< 50 MB RAM** [14]     | Python (heavier)                 |
| Own mobile apps       | ✓ Android + iOS [2]           | ✓ Android only [5]           | ✗ none (it's a relay) [18]       |
| iOS support           | ✓ via APNs relay [20]         | ✗ no official app [38]       | n/a (sends to others)            |
| Priorities            | ✓ 1–5 [15]                    | ✓ integer [17]               | maps to target's                 |
| Tags / emoji          | ✓ [15]                        | ✗                            | passthrough                      |
| Attachments           | ✓ ≤15 MB or URL [15]          | ✗                            | ✓ file or URL [18]               |
| Action buttons        | ✓ up to 3 [15]                | ✗                            | ✗                                |
| Scheduled delivery    | ✓ `X-Delay` [15]              | ✗                            | ✗                                |
| Auth model            | Users + per-topic ACLs [11]   | App/client tokens [12]       | Config keys (stateful) [7]       |
| Targets reachable     | itself                        | itself                       | **~143 services** [19]           |
| Setup weight          | Medium (CLI users/ACL) [13]   | **Easy** (~5 env vars) [13]  | Low (stateless) or keyed [10]    |

[1]: https://github.com/binwiederhier/ntfy
[2]: https://ntfy.sh/
[4]: https://github.com/gotify/server
[5]: https://gotify.net/
[6]: https://github.com/caronc/apprise
[7]: https://github.com/caronc/apprise-api
[10]: https://docs.linuxserver.io/images/docker-apprise-api/
[11]: https://docs.ntfy.sh/config/#access-control
[12]: https://gotify.net/docs/pushmsg
[13]: https://blog.vezpi.com/en/post/notification-system-gotify-vs-ntfy/
[14]: https://oneuptime.com/blog/post/2026-02-08-how-to-run-gotify-in-docker-for-push-notifications/view
[15]: https://docs.ntfy.sh/publish/
[17]: https://github.com/gotify/server/blob/master/docs/spec.json
[18]: https://github.com/caronc/apprise/blob/master/README.md
[19]: https://deepwiki.com/caronc/apprise
[20]: https://github.com/binwiederhier/ntfy/issues/1680
[38]: https://heywoodlh.io/gotify-ios-notifications

## Docker / self-hosting experience

All three are first-class Docker citizens; the gap is setup weight.

- **Gotify — easiest.** One container, one `/app/data` volume holding the SQLite DB, images and certs; seed the admin password with `GOTIFY_DEFAULTUSER_PASS` and you're done [[9]](https://gotify.net/docs/install). A homelab head-to-head calls it an "easy installation process" against ntfy's "bit more setup" [[13]](https://blog.vezpi.com/en/post/notification-system-gotify-vs-ntfy/). As a Go binary it sits under 50 MB RAM — runs on a Pi [[14]](https://oneuptime.com/blog/post/2026-02-08-how-to-run-gotify-in-docker-for-push-notifications/view).

  ```yaml
  services:
    gotify:
      image: gotify/server
      ports: ["80:80"]
      volumes: ["./gotify-data:/app/data"]
      environment:
        GOTIFY_DEFAULTUSER_PASS: change-me
  ```

- **ntfy — more knobs.** The image deliberately ships **no** `server.yml`, so you mount your own `/etc/ntfy/server.yml` plus a `/var/cache/ntfy` volume for `cache.db` [[8]](https://docs.ntfy.sh/install/). Auth is the richest of the three: a SQLite `auth-file`, `auth-default-access: deny-all` for a private instance, admin/user roles, per-topic ACLs with wildcards, and `tk_`-prefixed tokens — all managed via `ntfy user add` / `ntfy access` / `ntfy token add` or declarative YAML [[11]](https://docs.ntfy.sh/config/#access-control). Behind a reverse proxy, set `behind-proxy: true` + `base-url`; omitting it collapses every client into one rate-limit bucket [[16]](https://docs.ntfy.sh/config/).

- **Apprise — stateless or keyed.** Run `caronc/apprise:latest` on port 8000; `APPRISE_STATEFUL_MODE` decides whether config is persisted (hash/simple/disabled) with `/config` and `/attach` volumes [[7]](https://github.com/caronc/apprise-api). [LinuxServer](https://docs.linuxserver.io/images/docker-apprise-api/) also ships a rootless PUID/PGID image [[10]](https://docs.linuxserver.io/images/docker-apprise-api/). Because it's Python, its footprint is heavier than the two Go binaries — but it's a stateless relay, so you can run it ephemerally.

## Delivery mechanisms & the iOS problem

This is where "self-hosted" gets complicated, and it's the most common real-world surprise.

- **ntfy** publishes over plain HTTP PUT/POST: five priorities via `X-Priority`, emoji tags, attachments to 15 MB, up to three action buttons, and `X-Delay` scheduled delivery [[15]](https://docs.ntfy.sh/publish/). It also doubles as a **UnifiedPush distributor** (push without Google FCM, for apps like Element/FluffyChat) [[3]](https://unifiedpush.org/users/distributors/ntfy/) and supports browser **Web Push**.
- **Gotify** is deliberately leaner: `POST /message?token=<apptoken>`, optional title/priority, an `extras` field — **no attachments, tags, or action buttons** [[12]](https://gotify.net/docs/pushmsg). It splits `appToken` (senders) from `clientToken` (receivers/management, e.g. its Android app) over a persistent WebSocket [[17]](https://github.com/gotify/server/blob/master/docs/spec.json).

**iOS is the sharpest discriminator.** Apple forbids background WebSocket connections and routes all push through APNs — so instant iOS push is impossible without a central relay [[20]](https://github.com/binwiederhier/ntfy/issues/1680). The consequences:

- **ntfy** solves it, but not purely locally: a self-hosted server sets `upstream-base-url: "https://ntfy.sh"` and forwards poll requests through ntfy.sh's APNs relay; an iOS Notification Service Extension then fetches the message body back from *your* server [[20]](https://github.com/binwiederhier/ntfy/issues/1680). So even self-hosted ntfy leans on ntfy.sh for the iOS leg. ⚠ Note a current regression: on **iOS 26.2+** ntfy notifications have no sound and can mute other apps until you make a phone call [[21]](https://docs.ntfy.sh/known-issues/).
- **Gotify** has **no official iOS app at all** — shipping one means accepting Apple's TOS and paying Apple [[38]](https://heywoodlh.io/gotify-ios-notifications). iOS users bridge through ntfy or an unofficial workaround like [mschirrmeister/gotify-ios](https://github.com/mschirrmeister/gotify-ios) `⭐ 2`, which one reviewer flags as "insecure by default" [[26]](https://github.com/mschirrmeister/gotify-ios)[[23]](https://debian.ninja/post/2025/09/23/gotify-pushover-and-ntfy-real-time-notifications/).

**If iPhones are in scope, ntfy is effectively the only self-hosted option** — and even it routes the iOS leg through ntfy.sh.

## Integration ecosystem (where Apprise earns its place)

The homelab story splits into two roles: **Apprise is the dispatch/abstraction layer; ntfy and Gotify are the delivery + app endpoints** — and Apprise sends to both, so they're complementary, not rivals [[34]](https://jellywatch.app/blog/jellyfin-notifications-ntfy-gotify-apprise-webhook-2026).

| Source tool        | ntfy                  | Gotify                | Apprise                        |
| ------------------ | --------------------- | --------------------- | ------------------------------ |
| Uptime Kuma        | ✓ native [35]         | ✓ native [35]         | ✓ native [35]                  |
| Home Assistant     | ✓ core integ. [28]    | via Apprise/REST      | ✓ `notify.NAME` 140+ svc [27]  |
| Watchtower         | via shoutrrr [30]     | ✓ shorthand [29]      | (uses shoutrrr, not Apprise)   |
| Grafana alerting   | webhook/bridge [32]   | webhook               | webhook                        |

[27]: https://www.home-assistant.io/integrations/apprise/
[28]: https://www.home-assistant.io/integrations/ntfy/
[29]: https://containrrr.dev/watchtower/notifications/
[30]: https://github.com/containrrr/watchtower/discussions/2035
[32]: https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/
[35]: https://github.com/louislam/uptime-kuma

- **[Uptime Kuma](https://github.com/louislam/uptime-kuma)** `⭐ 87.8k` exposes ntfy, Gotify, *and* Apprise as native notification providers in its UI [[35]](https://github.com/louislam/uptime-kuma).
- **Home Assistant** ships a native core ntfy integration (since 2025.05, with usage sensors) [[28]](https://www.home-assistant.io/integrations/ntfy/) *and* an Apprise integration that binds `notify.NAME` to 140+ services [[27]](https://www.home-assistant.io/integrations/apprise/).
- **[Watchtower](https://containrrr.dev/watchtower)** `⭐ 24.8k` dispatches via shoutrrr (note: *not* Apprise) — a Gotify shorthand backend [[29]](https://containrrr.dev/watchtower/notifications/) and `ntfy://ntfy.sh/topic` for ntfy [[30]](https://github.com/containrrr/watchtower/discussions/2035).
- **Grafana** alerting reaches ntfy through its generic webhook contact point [[32]](https://grafana.com/docs/grafana/latest/alerting/configure-notifications/manage-contact-points/integrations/webhook-notifier/), optionally via a small reformatting bridge [[33]](https://github.com/academo/grafana-alerting-ntfy-webhook-integration) `⭐ 34`.

ntfy's own integrations page catalogs the whole stack — Home Assistant, Uptime Kuma, Watchtower, Healthchecks, Gatus — plus Apprise as a universal bridge [[31]](https://docs.ntfy.sh/integrations/).

The takeaway: **embed Apprise (or Apprise-API) as your one notification backend, point it at ntfy/Gotify**, and every source tool only has to learn one URL syntax [[22]](https://www.xda-developers.com/reasons-use-apprise-instead-of-ntfy-gotify/).

## Project health & bus-factor

| Project | Stars     | Latest release        | Open issues | Maintainer            |
| ------- | --------- | --------------------- | ----------- | --------------------- |
| ntfy    | ⭐ 30.7k   | v2.24.0 (Jun 4 2026)  | ~311        | Philipp Heckel (solo) |
| Apprise | ⭐ 16.7k   | v1.11.0 (May 29 2026) | ~23         | Chris Caron           |
| Gotify  | ⭐ 15.1k   | v2.9.1 (Feb 28 2026)  | ~73         | Jannis Mattheis (solo)|

ntfy is the clear momentum leader on stars and release cadence [[1]](https://github.com/binwiederhier/ntfy). Both push servers are effectively **single-maintainer side projects**: Philipp Heckel runs ntfy alone on one DigitalOcean droplet and explicitly chose not to depend on it financially [[24]](https://changelog.com/podcast/562); Jannis Mattheis maintains Gotify in his free time around a full-time job, which shows in the spaced-out cadence [[25]](https://jmattheis.de/). Plan your bus-factor accordingly — though all three are open-source Go/Python you can fork.

**Operator consensus** (homelab blogs/reviews): ntfy is the rising favorite for cross-server topics, ACLs and emoji, dinged for CLI-only user management and no built-in web admin [[13]](https://blog.vezpi.com/en/post/notification-system-gotify-vs-ntfy/)[[23]](https://debian.ninja/post/2025/09/23/gotify-pushover-and-ntfy-real-time-notifications/); Gotify is praised as simple and stable but criticized for one-destination delivery and the iOS gap [[23]](https://debian.ninja/post/2025/09/23/gotify-pushover-and-ntfy-real-time-notifications/); Apprise is repeatedly framed as the universal glue you stack on top, not a competitor [[22]](https://www.xda-developers.com/reasons-use-apprise-instead-of-ntfy-gotify/).

## When to reach for a cloud gateway instead

Self-hosting isn't always the right answer. Three axes rarely point the same way:

- **iOS reach → cloud often wins.** Because of the APNs constraint above, a *fully* local push to iPhone is impossible; you're relaying through someone's server regardless [[20]](https://github.com/binwiederhier/ntfy/issues/1680). **[Pushover](https://pushover.net)** is a one-time **$4.99 per platform**, no subscription, rock-solid iOS/Android — effectively a one-time cost for a homelab and zero ops [[36]](https://pushover.net/pricing).
- **Cost → cloud is cheap at small scale.** ntfy.sh's free no-signup tier (60-request burst, then 1 req/10 s) covers most alerting [[37]](https://docs.ntfy.sh/faq/); self-hosting is "free" only if you ignore ops time.
- **Privacy → self-host wins.** Message content stays local, no rate limits or data mining [[39]](https://www.xda-developers.com/set-up-self-hosted-notification-service/). By contrast, Telegram's default Cloud Chats are stored on Telegram's servers and are **not** end-to-end encrypted [[40]](https://gemspace.com/blog/telegram-alternatives).
- **⚠ The reliability paradox.** If you self-host your monitoring *and* your push gateway on the same box, the "your box is down" alert dies with the box. Keep the alert path on different infrastructure than the thing it watches — a cloud relay (Pushover) or ntfy's hosted upstream is the hedge worth paying for [[39]](https://www.xda-developers.com/set-up-self-hosted-notification-service/).

## Bottom line

- **Android/web homelab, want power:** self-host **ntfy** → priorities, ACLs, attachments, action buttons, UnifiedPush.
- **Want the simplest possible thing, Android-only:** **Gotify** → 5-minute install, < 50 MB RAM.
- **Many source apps, many destinations:** put **Apprise** in front as the router and let it fan out to ntfy/Gotify/email/chat.
- **iPhones matter or you want zero ops:** **Pushover** (cloud, $4.99 once) — or ntfy, accepting it relays the iOS leg through ntfy.sh.
- **Most homelabs end up with two:** Apprise (or Apprise-API) as the dispatch layer + ntfy as the delivery endpoint.
