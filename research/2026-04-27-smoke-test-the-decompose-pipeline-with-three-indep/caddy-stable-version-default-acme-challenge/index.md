---
title: "Caddy stable version + default ACME challenge"
date: 2026-04-27
depth: ceo
format: md
topic: "Caddy stable version + default ACME challenge"
topic_raw: "Caddy stable version + default ACME challenge"
issue: 19
tags: [caddy, acme, https, web-server]
summary: Caddy 2.11.2 (Mar 2026) is the current stable; HTTP-01 and TLS-ALPN-01 are both default, picked at random then biased by success.
citations: 5
reading_time_min: 1
cover: cover.svg
cost_usd: 0.62
duration_sec: 87
---

> **TL;DR** — Run **Caddy 2.11.2** (released 2026-03-05, the only supported line) [[1]](https://endoflife.date/caddy)[[2]](https://github.com/caddyserver/caddy/releases). The default ACME issuance flow enables **both HTTP-01 and TLS-ALPN-01** challenges; Caddy picks one **at random** per order, then over time biases toward whichever has been most successful [[3]](https://caddyserver.com/docs/automatic-https). The DNS-01 challenge is **not** on by default — you must wire in a DNS provider module [[3]](https://caddyserver.com/docs/automatic-https).

## Stable version

| | |
|---|---|
| Latest stable | **2.11.2** [[2]](https://github.com/caddyserver/caddy/releases) |
| Released | 2026-03-05 [[1]](https://endoflife.date/caddy) |
| Supported lines | Only v2 (latest only); v1 EOL 2020-07-01 [[1]](https://endoflife.date/caddy) |
| Repo | [caddyserver/caddy](https://github.com/caddyserver/caddy) ⭐ 71k (Apr 2026) |

The 2.11 line was the first release cut by the maintainer team's automated process without the original author in the loop, and introduced experimental ACME profiles (e.g. Let's Encrypt 6-day certs) and wildcard-by-default for subdomains [[4]](https://calmops.com/network/caddy-web-server-automatic-https-2026/).

## Default ACME challenge

Caddy enables two challenges out of the box [[3]](https://caddyserver.com/docs/automatic-https):

| Challenge | Port needed | Default? | Notes |
|---|---|---|---|
| **HTTP-01** | 80 inbound | ✓ | DNS lookup → fetch token over `:80` |
| **TLS-ALPN-01** | 443 inbound | ✓ | DNS lookup → TLS handshake on `:443` with ALPN `acme-tls/1` |
| **DNS-01** | — | ✗ | Requires a DNS provider module + credentials [[3]](https://caddyserver.com/docs/automatic-https) |

Selection rule, verbatim from the docs: *"If multiple challenges are enabled, Caddy chooses one at random to avoid accidental dependence on a particular challenge. Over time, it learns which challenge type is most successful and will begin to prefer it first, but will fall back to other available challenge types if necessary."* [[3]](https://caddyserver.com/docs/automatic-https)

→ Practical implication: if only **one** of `:80`/`:443` is reachable from the public internet, leave both on — Caddy will fail the unreachable one and learn to prefer the other. If **neither** is publicly reachable (private network, behind CGNAT), switch to DNS-01 explicitly via the `tls` directive's `dns` option [[5]](https://caddyserver.com/docs/caddyfile/directives/tls).
