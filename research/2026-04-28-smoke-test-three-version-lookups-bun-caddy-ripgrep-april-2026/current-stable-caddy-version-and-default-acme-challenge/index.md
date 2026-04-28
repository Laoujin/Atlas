---
title: "Caddy: latest stable and default ACME challenge"
date: 2026-04-28
depth: ceo
format: md
topic: "Current stable Caddy version and default ACME challenge"
topic_raw: "Current stable Caddy version and default ACME challenge"
issue: 39
tags: [caddy, acme, tls, https]
summary: "Caddy v2.11.2 (Mar 6, 2026) is the latest stable; HTTP-01 and TLS-ALPN-01 are enabled by default, with Caddy adaptively learning which to prefer per host."
citations: 2
reading_time_min: 1
cover: cover.svg
cost_usd: 0.64
duration_sec: 93
---

> **TL;DR** Latest stable [Caddy](https://github.com/caddyserver/caddy) ⭐ 72k (Apr 2026) is **v2.11.2**, published **2026-03-06** [[1]](https://github.com/caddyserver/caddy/releases). The **HTTP-01** and **TLS-ALPN-01** challenges are enabled by default; **DNS-01** is opt-in because it needs DNS-provider credentials [[2]](https://caddyserver.com/docs/automatic-https).

## Default challenge selection

There is no fixed "preferred" default. Per the official docs: Caddy "chooses one at random to avoid accidental dependence on a particular challenge. Over time, it learns which challenge type is most successful and will begin to prefer it first, but will fall back to other available challenge types if necessary." [[2]](https://caddyserver.com/docs/automatic-https)

DNS-01 is the only ACME challenge type that does not auto-enable, because it requires credentials for the DNS provider [[2]](https://caddyserver.com/docs/automatic-https).

## Version note

v2.11.2 is a bug-fix/enhancement release: reverse-proxy fixes, metrics-performance work, `zstd` support in log rolling, and CVE patches in `forward_auth` and `vars_regexp` placeholder expansion [[1]](https://github.com/caddyserver/caddy/releases).
