---
title: "Caddy in 2026: stable v2.11.2, no single ACME default"
date: 2026-04-27
depth: ceo
format: md
topic: "Current stable Caddy version and default ACME challenge type in 2026"
topic_raw: "Current stable Caddy version and default ACME challenge type in 2026"
issue: 20
tags: [caddy, acme, https, tls, web-server]
summary: Caddy 2.11.2 is the current stable release; HTTP-01 and TLS-ALPN-01 are both enabled by default and Caddy picks between them adaptively.
citations: 5
reading_time_min: 1
cover: cover.svg
cost_usd: 0.73
duration_sec: 106
---

> **TL;DR** — Latest stable [Caddy](https://github.com/caddyserver/caddy) ⭐ 72k is **v2.11.2**, released 6 March 2026 [[1]](https://endoflife.date/caddy)[[2]](https://github.com/caddyserver/caddy/releases/tag/v2.11.2). There is **no single default ACME challenge**: HTTP-01 and TLS-ALPN-01 are both enabled by default, Caddy picks one at random per certificate, then biases toward whichever has been succeeding. DNS-01 is opt-in [[3]](https://caddyserver.com/docs/automatic-https).

## Version

| Field | Value |
|---|---|
| Latest stable | **v2.11.2** [[1]](https://endoflife.date/caddy) |
| Released | 6 March 2026 [[2]](https://github.com/caddyserver/caddy/releases/tag/v2.11.2) |
| Supported lines | Only the latest release is security-supported [[1]](https://endoflife.date/caddy) |
| Repo | [caddyserver/caddy](https://github.com/caddyserver/caddy) ⭐ 72k (Apr 2026) |

The 2.11 line introduced **ACME profiles**, letting issuers offer short-lived certs — Let's Encrypt's 6-day profile is the headline use case [[4]](https://releasebot.io/updates/caddy).

## Default ACME challenge

Caddy's docs are explicit: "the first two challenge types are enabled by default" — meaning HTTP-01 (port 80) and TLS-ALPN-01 (port 443). DNS-01 stays disabled because it needs DNS-provider credentials [[3]](https://caddyserver.com/docs/automatic-https).

| Challenge | Default? | Port | Needs config? |
|---|---|---|---|
| HTTP-01 | ✓ | 80 | ✗ |
| TLS-ALPN-01 | ✓ | 443 | ✗ |
| DNS-01 | ✗ | — | ✓ (provider creds) |

When both defaults are on, Caddy "chooses one at random to avoid accidental dependence on a particular challenge", then learns which one succeeds and prefers it, falling back to the other on failure [[3]](https://caddyserver.com/docs/automatic-https). So the practical answer to "what's the default?" is: **whichever wins first in your environment** — typically TLS-ALPN-01 if port 443 is reachable, HTTP-01 if only port 80 is.

If you need wildcards or your server isn't reachable on low ports, configure DNS-01 explicitly via the `tls` directive's `dns` option [[5]](https://caddyserver.com/docs/caddyfile/directives/tls).
