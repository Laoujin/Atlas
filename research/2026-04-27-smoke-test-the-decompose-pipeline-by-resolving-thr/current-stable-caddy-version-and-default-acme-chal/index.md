---
title: Caddy stable version and default ACME challenge (Apr 2026)
date: 2026-04-27
depth: ceo
format: md
topic: "Current stable Caddy version and default ACME challenge (2026)"
topic_raw: "Current stable Caddy version and default ACME challenge (2026)"
issue: 18
tags: [caddy, acme, https, web-server]
summary: Caddy v2.11.2 (Mar 2026) is the current stable release; HTTP-01 and TLS-ALPN-01 are enabled by default, picked at random and learned over time.
citations: 3
reading_time_min: 1
cover: cover.svg
cost_usd: 0.61
duration_sec: 78
---

> **TL;DR** — **Caddy v2.11.2** (released 6 Mar 2026) is the current stable release [[1]](https://github.com/caddyserver/caddy/releases). By default Caddy enables **two ACME challenges — HTTP-01 and TLS-ALPN-01** — and picks one at random per issuance, then learns which is most reliable and prefers it [[2]](https://caddyserver.com/docs/automatic-https). The DNS-01 challenge is opt-in and requires explicit provider config [[2]](https://caddyserver.com/docs/automatic-https).

## Quick facts

| Item | Value | Source |
|---|---|---|
| Latest stable | **v2.11.2** | [GitHub releases](https://github.com/caddyserver/caddy/releases) ⭐ 72k [[1]](https://github.com/caddyserver/caddy/releases) |
| Released | 6 Mar 2026 | [[1]](https://github.com/caddyserver/caddy/releases) |
| Prior point release | v2.11.1 (23 Feb 2026) | [[1]](https://github.com/caddyserver/caddy/releases) |
| Support policy | Only latest release supported | [endoflife.date](https://endoflife.date/caddy) [[3]](https://endoflife.date/caddy) |
| Default challenges | HTTP-01, TLS-ALPN-01 | [[2]](https://caddyserver.com/docs/automatic-https) |
| Selection | Random per issuance → learned preference, with fallback | [[2]](https://caddyserver.com/docs/automatic-https) |
| DNS-01 | Opt-in; needs provider plugin + credentials | [[2]](https://caddyserver.com/docs/automatic-https) |

## Notes

- Both default challenges need inbound reachability: HTTP-01 on **:80**, TLS-ALPN-01 on **:443** [[2]](https://caddyserver.com/docs/automatic-https). If either port is blocked or behind a proxy that terminates TLS, switch to DNS-01.
- Wildcard certs (`*.example.com`) require **DNS-01** — neither HTTP-01 nor TLS-ALPN-01 can satisfy a wildcard [[2]](https://caddyserver.com/docs/automatic-https).
- Only the latest minor receives fixes; v2.11.2 ships two CVE fixes on top of v2.11.1's six [[1]](https://github.com/caddyserver/caddy/releases). Pin to the latest patch.
