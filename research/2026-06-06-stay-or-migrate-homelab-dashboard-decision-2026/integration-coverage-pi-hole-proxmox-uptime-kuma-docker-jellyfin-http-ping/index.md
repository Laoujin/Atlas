---
title: "Integration coverage: Pi-hole, Proxmox, Uptime Kuma, Docker, Jellyfin, HTTP/ping"
date: 2026-06-06
depth: standard
format: md
topic: "Integration coverage: Pi-hole, Proxmox, Uptime Kuma, Docker, Jellyfin, HTTP/ping"
topic_raw: "Integration coverage: Pi-hole, Proxmox, Uptime Kuma, Docker, Jellyfin, HTTP/ping"
issue: 193
tags: [homelab, dashboard, integrations, homepage, homarr, dashy, self-hosted]
summary: "Coverage matrix for Pi-hole, Proxmox, Uptime Kuma, Docker, Jellyfin and HTTP/ping across the three leading self-hosted dashboards — with per-widget data details and caveats."
citations: 20
reading_time_min: 4
cover: cover.svg
cost_usd: 1.99
duration_sec: 833
model: "Sonnet 4.6"
---

> **TL;DR** [Homepage](https://github.com/gethomepage/homepage) ⭐ 30.5k [[8]](https://github.com/gethomepage/homepage) covers all six service types with the richest per-widget data [[1]](https://gethomepage.dev/widgets/services/). [Homarr](https://github.com/homarr-labs/homarr) ⭐ 4k [[9]](https://github.com/homarr-labs/homarr) matches on four of six but dropped HTTP/ping and Uptime Kuma in its v1.x rewrite. [Dashy](https://github.com/lissy93/dashy) ⭐ 25.3k [[15]](https://github.com/lissy93/dashy) is strongest for HTTP/ping flexibility but has no Jellyfin widget and no Docker API access [[16]](https://dashy.to/docs/widgets/).

## Coverage matrix

| Service         | [Homepage][h] ⭐ 30.5k                           | [Homarr][ho] ⭐ 4k                               | [Dashy][da] ⭐ 25.3k                              |
|-----------------|---------------------------------------------------|---------------------------------------------------|---------------------------------------------------|
| **Pi-hole**     | ✓ queries, blocked %, gravity [[2]][hpi]          | ✓ summary + on/off toggle [[11]][hopi]            | ✓ 3 widget types, v6 variants [[16]][dwi]         |
| **Proxmox**     | ✓ VMs, LXC, CPU, mem [[3]][hpx]                  | ✓ system health (PVE realm req.) [[12]][hopx]     | ✓ node / VM / container list [[16]][dwi]          |
| **Uptime Kuma** | ✓ via status-page slug [[5]][huk]                 | ✗ planned, not in v1.x [[14]][houk]               | ✓ widget (JSON issues reported) [[16]][dwi]       |
| **Docker**      | ✓ socket, CPU / mem / net stats [[6]][hdo]        | ✓ stats widget + start/stop [[10]][hodo]          | ✗ HTTP status checks only [[17]][dst]             |
| **Jellyfin**    | ✓ streams, library counts [[4]][hje]              | ✓ streams, recent media [[13]][hoje]              | ✗ no widget [[16]][dwi]                           |
| **HTTP/ping**   | ✓ ICMP ping + HTTP HEAD [[7]][hsi]                | ✗ removed in v1.x [[14]][houk]                   | ✓ codes, intervals, auth headers [[17]][dst]      |

[h]:    https://github.com/gethomepage/homepage
[ho]:   https://github.com/homarr-labs/homarr
[da]:   https://github.com/lissy93/dashy
[hpi]:  https://gethomepage.dev/widgets/services/pihole/
[hpx]:  https://gethomepage.dev/widgets/services/proxmox/
[hje]:  https://gethomepage.dev/widgets/services/jellyfin/
[huk]:  https://gethomepage.dev/widgets/services/uptime-kuma/
[hdo]:  https://gethomepage.dev/configs/docker/
[hsi]:  https://gethomepage.dev/configs/services/
[hopi]: https://homarr.dev/docs/integrations/pi-hole/
[hopx]: https://homarr.dev/docs/integrations/proxmox/
[hoje]: https://homarr.dev/docs/integrations/jellyfin/
[houk]: https://github.com/ajnart/homarr/issues/814
[hodo]: https://homarr.dev/docs/category/integrations/
[dwi]:  https://dashy.to/docs/widgets/
[dst]:  https://dashy.to/docs/status-indicators/

## Per-service notes

### Pi-hole

All three dashboards support Pi-hole. Homepage shows total queries, blocked count and %, and gravity (domains on blocklist). Supports both v5 (default) and v6 — Pi-hole v6 changed its auth endpoint and default port to 8080, requiring `version: 6` in the widget config [[2]](https://gethomepage.dev/widgets/services/pihole/).

Homarr splits this into two widgets: **DNS Hole Summary** (query stats) and **DNS Hole Controls** (toggle Pi-hole blocking on/off directly from the dashboard) [[11]](https://homarr.dev/docs/integrations/pi-hole/).

Dashy provides three separate widget types: Pi-Hole Stats (summary numbers), Pi-Hole Queries (query history chart), Pi-Hole Recent Traffic (top domains). v6-compatible variants exist for all three [[16]](https://dashy.to/docs/widgets/).

### Proxmox

Coverage is consistent across all three. Homepage reads the Proxmox API and shows running/total counts for QEMU VMs and LXC containers, plus CPU% and mem% — configurable per-node or cluster-wide. API token needs `PVEAuditor` role in `api_token_id@pam!TokenID` format [[3]](https://gethomepage.dev/widgets/services/proxmox/).

Homarr's Proxmox integration covers system health (VMs, LXC, CPU/mem). ⚠ Requires the **Proxmox VE authentication server** realm — Linux PAM auth does not work [[12]](https://homarr.dev/docs/integrations/proxmox/).

Dashy renders a node tree listing containers and VMs with per-item status dots [[16]](https://dashy.to/docs/widgets/).

### Uptime Kuma

[Uptime Kuma](https://github.com/louislam/uptime-kuma) ⭐ 87.7k (Jun 2026) exposes no full REST API, which limits how dashboards can integrate it [[20]](https://github.com/louislam/uptime-kuma).

Homepage works around this via a **status page slug**: create a status page in Uptime Kuma, then set `slug: <your-slug>` in the widget config. Returns up/down/uptime/incident counts from that page — the status page is a mandatory intermediary [[5]](https://gethomepage.dev/widgets/services/uptime-kuma/).

Homarr v0.x (ajnart/homarr ⭐ 7.2k) had HTTP status checking that covered this use case. The v1.x rewrite (homarr-labs) removed it; re-integration is on the roadmap but absent as of mid-2026 [[14]](https://github.com/ajnart/homarr/issues/814). Community workaround: [homarr-iframes](https://github.com/diogovalentte/homarr-iframes) ⭐ 114 embeds Uptime Kuma data via iFrames in any dashboard [[19]](https://github.com/diogovalentte/homarr-iframes).

Dashy ships both an `uptime-kuma` widget and an `uptime-kuma-status-page` widget, but some users report JSON parsing errors depending on the Uptime Kuma version [[16]](https://dashy.to/docs/widgets/).

### Docker

Homepage connects via the **Docker socket** (or a socket proxy for least-privilege access) and shows container status natively. Clicking a container's status badge expands per-container CPU, memory, and network stats. Auto-discovery from Docker labels is fully supported [[6]](https://gethomepage.dev/configs/docker/).

Homarr also mounts the Docker socket and provides a **Docker Stats** widget with per-container resource metrics. Unique to Homarr: you can start, stop, and restart containers directly from the dashboard [[10]](https://homarr.dev/docs/category/integrations/).

Dashy has no Docker API integration. Service tiles get HTTP status indicators (response code + time), but there is no container-stat access or auto-discovery [[17]](https://dashy.to/docs/status-indicators/).

### Jellyfin

Homepage integrates via Jellyfin API key and shows **Now Playing** sessions by default, with optional library count blocks (movies, series, episodes, songs), user info, and in-dashboard playback controls. ⚠ Jellyfin ≥ 10.12 requires `version: 2` in the widget config [[4]](https://gethomepage.dev/widgets/services/jellyfin/).

Homarr provides an **active streams** widget and a **recently added / upcoming releases** widget [[13]](https://homarr.dev/docs/integrations/jellyfin/).

Dashy has no Jellyfin widget — services can only be added as tiles with an HTTP status check [[16]](https://dashy.to/docs/widgets/).

### HTTP / Ping

Homepage provides two per-service options: `ping` (ICMP, IPv4 only; may need `iputils-ping` on the container host) and `siteMonitor` (HTTP HEAD to a URL, shows response time in ms). Both render as colored status dots on service tiles [[7]](https://gethomepage.dev/configs/services/).

Homarr v0.x had HTTP status checking; v1.x removed it and plans re-introduction [[14]](https://github.com/ajnart/homarr/issues/814).

Dashy is the most capable: HTTP status checks (response code + response time, online/offline), ICMP ping, configurable polling intervals in seconds, custom acceptable status codes, and request headers for auth-protected endpoints [[17]](https://dashy.to/docs/status-indicators/).

## Decision criteria

Per [[18]](https://selfhosting.sh/best/dashboards/), the three dashboards occupy distinct niches:

- **Homepage** — deepest widget data across all six types; YAML config-as-code; server-side rendering. Default pick if live metrics for every service type is the goal.
- **Homarr** — drag-and-drop UI, no YAML required. Covers Pi-hole / Proxmox / Docker / Jellyfin well. Wait on official HTTP/ping and Uptime Kuma support, or bridge with homarr-iframes.
- **Dashy** — richest HTTP/ping status monitoring; most visual customisation. Gaps in Jellyfin and Docker-native access make it a secondary choice if media-server or container metrics are a priority.
