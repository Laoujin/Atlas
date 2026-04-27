---
title: Caddy stable version and default ACME challenge
date: 2026-04-27
depth: ceo
format: md
topic: "Caddy stable version and default ACME challenge"
topic_raw: "Caddy stable version and default ACME challenge"
issue: 21
tags: [caddy, acme, tls, https, web-server]
summary: Latest stable Caddy is v2.11.2 (Mar 2026); HTTP-01 and TLS-ALPN-01 challenges are both enabled by default, picked at random then learned.
citations: 5
reading_time_min: 1
cover: cover.svg
cost_usd: 0.73
duration_sec: 108
---

> **TL;DR** — Latest stable [Caddy](https://github.com/caddyserver/caddy) ⭐ 72k is **v2.11.2**, released 2026-03-05 [[1]](https://github.com/caddyserver/caddy/releases) [[2]](https://endoflife.date/caddy). Default ACME challenges: **HTTP-01 and TLS-ALPN-01 both on**; Caddy picks one at random, then learns which one succeeds and prefers it [[3]](https://caddyserver.com/docs/automatic-https). DNS-01 is **off** by default — it needs provider credentials [[3]](https://caddyserver.com/docs/automatic-https).

## Stable version

| Field | Value | Source |
|---|---|---|
| Latest stable | **v2.11.2** | [[1]](https://github.com/caddyserver/caddy/releases) |
| Released | 2026-03-05 | [[2]](https://endoflife.date/caddy) |
| Support policy | Only the latest release is supported | [[2]](https://endoflife.date/caddy) |
| Repo | [caddyserver/caddy](https://github.com/caddyserver/caddy) ⭐ 72k | [[1]](https://github.com/caddyserver/caddy/releases) |

v2.11 was the first release on the team's new automated release process; 2.11.2 ships bug fixes plus two CVE patches (forward-auth identity injection, vars_regexp placeholder expansion) [[1]](https://github.com/caddyserver/caddy/releases).

## Default ACME challenges

| Challenge | Default | Why |
|---|---|---|
| HTTP-01 | ✓ on | No config needed; needs port 80 reachable [[3]](https://caddyserver.com/docs/automatic-https) |
| TLS-ALPN-01 | ✓ on | No config needed; needs port 443 reachable [[3]](https://caddyserver.com/docs/automatic-https) |
| DNS-01 | ✗ off | Requires DNS-provider credentials — opt-in via the `dns` issuer config [[4]](https://caddyserver.com/docs/caddyfile/directives/tls) |

**Selection logic:** "If multiple challenges are enabled, Caddy chooses one at random to avoid accidental dependence on a particular challenge. Over time, it learns which challenge type is most successful and will begin to prefer it first, but will fall back to other available challenge types if necessary." [[3]](https://caddyserver.com/docs/automatic-https)

Underlying ACME logic lives in [caddyserver/certmagic](https://github.com/caddyserver/certmagic) [[5]](https://github.com/caddyserver/certmagic), which Caddy embeds.

## Practical notes

- If the box can't open :80 or :443 to the public internet → enable DNS-01 explicitly; otherwise issuance will fail [[3]](https://caddyserver.com/docs/automatic-https).
- New in 2.11: **ACME profiles** (e.g. Let's Encrypt 6-day certs), a global DNS-provider option, and wildcards-by-default for subdomains [[1]](https://github.com/caddyserver/caddy/releases).
