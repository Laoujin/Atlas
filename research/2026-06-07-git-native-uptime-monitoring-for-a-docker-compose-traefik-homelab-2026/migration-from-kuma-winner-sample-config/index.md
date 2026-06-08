---
title: "Migrating from Uptime Kuma to Gatus: Step-by-Step + Sample Config"
date: 2026-06-08
depth: standard
format: md
topic: "Migration from Kuma + winner sample config"
topic_raw: "Migration from Kuma + winner sample config"
issue: 198
tags: [homelab, monitoring, uptime, gatus, uptime-kuma, gitops, self-hosted, config-as-code, migration]
summary: "Gatus wins for gitops homelabs: pure YAML config, 40 MB RAM, no database. No automated migrator exists — dump Kuma's SQLite or use the Python API, then remap to Gatus endpoint format. Full sample config included for HTTP, ICMP, TCP, TLS, DNS, Discord/ntfy alerts, and Homepage widget."
citations: 16
reading_time_min: 8
cover: cover.svg
cost_usd: 1.86
duration_sec: 698
model: "Sonnet 4.6"
---

> **TL;DR** [Gatus](https://github.com/TwiN/gatus) ⭐ 11.2k is the config-as-code winner: monitoring lives in a single `config.yaml` you commit to git — no database, no UI clicks, no drift [[1]](https://github.com/TwiN/gatus). [Uptime Kuma](https://github.com/louislam/uptime-kuma) ⭐ 87.7k [[11]](https://github.com/louislam/uptime-kuma) is the larger community project but stores everything in SQLite behind a GUI — no YAML export, no git history. **Migration is manual**: Kuma v1 has a JSON export in Settings; Kuma v2 (October 2025+) removed it [[10]](https://linuxiac.com/uptime-kuma-2-0-arrives-with-mariadb-support-modern-ui-refresh/) — use the SQLite query below or the Python API library [[12]](https://uptime-kuma-api.readthedocs.io/en/latest/api.html). The full `config.yaml` sample covers HTTP/HTTPS, ICMP ping, TCP port, TLS cert, DNS, Discord + ntfy alerting, and Homepage dashboard widget integration.

---

## Why Gatus for This Stack

The paired dashboard research chose [Homepage](https://gethomepage.dev) ⭐ 31k because it is pure-YAML and git-deployable. Gatus completes the picture:

| Axis                   | [Uptime Kuma](https://github.com/louislam/uptime-kuma) ⭐ 87.7k | [Gatus](https://github.com/TwiN/gatus) ⭐ 11.2k       |
| ---------------------- | --------------------------------------------------------------- | ----------------------------------------------------- |
| Config method          | Web UI → SQLite                                                 | `config.yaml` → git [[1]](https://github.com/TwiN/gatus) |
| RAM (50 endpoints)     | ~100 MB [[2]](https://www.homelabstarter.com/homelab-uptime-monitoring/) | ~40 MB [[5]](https://botmonster.com/posts/build-status-page-self-hosted-services-gatus/) |
| Prometheus `/metrics`  | No native                                                       | `metrics: true` in config [[1]](https://github.com/TwiN/gatus) |
| Homepage widget        | ✓ via Kuma widget                                               | ✓ native `type: gatus` [[4]](https://gethomepage.dev/widgets/services/gatus/) |
| Alerting providers     | 90+ [[6]](https://betterstack.com/community/comparisons/uptime-kuma-alternative/) | 20+ [[5]](https://botmonster.com/posts/build-status-page-self-hosted-services-gatus/) |
| Monitor types          | 15+ (Docker, Steam…)                                            | 8 (HTTP/TCP/ICMP/DNS/WS/gRPC/SSH/STARTTLS)            |
| License                | MIT                                                             | Apache-2.0                                            |
| Config version control | ✗                                                               | ✓                                                     |

The gitops tradeoff is the deciding factor: any change to monitoring is a PR, diff, and rollback-able commit — not a GUI click that leaves no audit trail [[7]](https://ramnode.com/guides/series/monitoring/gatus).

### What you lose

- **Historical uptime data**: Gatus resets history on restart unless SQLite storage is enabled [[3]](https://blog.mei-home.net/posts/k8s-migration-21-gatus/) — existing Kuma history does not transfer.
- **Docker container monitor type**: Kuma can watch container liveness; Gatus cannot — replace with an HTTP healthcheck endpoint (add `HEALTHCHECK` to your Dockerfile or check Traefik's `/ping`).
- **GUI monitor management**: Add/edit/delete = edit `config.yaml`, Gatus auto-reloads on change.
- **Notification providers**: 70 Kuma providers have no Gatus equivalent (e.g. Pushbullet, Splunk On-Call) — Discord, Slack, ntfy, Telegram, PagerDuty, and email cover most homelab needs.

---

## Migration Procedure

### Step 1 — Export monitors from Kuma

**Kuma v1** (before October 2025): Settings → Export → downloads `backup.json` with `monitors[]` and `notificationList[]`.

**Kuma v2** (October 2025+): JSON export was removed [[9]](https://github.com/louislam/uptime-kuma/issues/6045). Backup = copy `/app/data/` [[8]](https://deepwiki.com/louislam/uptime-kuma/11-data-management-and-backup). Dump monitors from SQLite:

```bash
sqlite3 /path/to/uptime-kuma/data/kuma.db \
  "SELECT name, type, url, hostname, port, dns_resolve_server, keyword \
   FROM monitor ORDER BY name;"
```

Or use the Python API library [[12]](https://uptime-kuma-api.readthedocs.io/en/latest/api.html) against a running instance:

```bash
pip install uptime-kuma-api
python3 - <<'EOF'
from uptime_kuma_api import UptimeKumaApi
api = UptimeKumaApi("http://localhost:3001")
api.login("admin", "your-password")
for m in api.get_monitors():
    print(f"{m['name']:30s}  type={m['type']:12s}  url={m.get('url', m.get('hostname',''))}")
api.disconnect()
EOF
```

### Step 2 — Map Kuma monitor types to Gatus endpoints

| Kuma `type`       | Kuma key fields                  | Gatus `url` format         | Required conditions                                         |
| ----------------- | -------------------------------- | -------------------------- | ----------------------------------------------------------- |
| `http`            | `url`                            | `https://…`                | `[STATUS] == 200`                                           |
| `ping`            | `hostname`                       | `icmp://hostname`          | `[CONNECTED] == true`                                       |
| `tcp`             | `hostname` + `port`              | `tcp://hostname:port`      | `[CONNECTED] == true`                                       |
| `dns`             | `hostname` + `dns_resolve_server`| IP of the DNS server       | + `dns:` block with `query-name` + `[DNS_RCODE] == NOERROR` |
| `keyword`         | `url` + `keyword`                | `https://…`                | `[BODY] == pat(*keyword*)`                                  |
| `push`            | n/a (Kuma receives)              | `external-endpoints` block | push via bearer token + API call [[1]](https://github.com/TwiN/gatus) |
| certificate check | host (implicit in HTTP check)    | `https://…`                | `[CERTIFICATE_EXPIRATION] > 240h`                           |

### Step 3 — Run Gatus alongside Kuma

Keep Kuma running during cutover. Start Gatus on port `8081` and verify all checks go green. Run in parallel for 24–48 hours to confirm alert thresholds are tuned.

### Step 4 — Switch the Homepage widget

One-line change in `services.yaml` — see [Homepage widget](#homepage-widget) section below.

### Step 5 — Decommission Kuma

Stop the Kuma container and volume. Historical uptime data is not portable.

---

## Full Sample `config.yaml`

Covers the six target service types from the integration matrix (Pi-hole, Proxmox, Uptime-style HTTP checks, Docker-adjacent TCP, Jellyfin, and HTTP/ping). Secrets are read from environment variables — never commit credentials [[7]](https://ramnode.com/guides/series/monitoring/gatus)[[13]](https://raw.githubusercontent.com/TwiN/gatus/master/.examples/docker-compose-sqlite-storage/config/config.yaml).

```yaml
# ─────────────────────────────────────────────────────────────────────────────
# Gatus homelab config — mount read-only at /config/config.yaml
# ─────────────────────────────────────────────────────────────────────────────

metrics: true          # Prometheus /metrics endpoint

storage:
  type: sqlite
  path: /data/gatus.db  # persistent uptime history across restarts

web:
  port: 8080

security:
  basic:
    username: "${GATUS_USER}"
    password-bcrypt-base64: "${GATUS_PASS_BCRYPT}"  # bcryptpw -cost=10 yourpass | base64

# ── Alerting ──────────────────────────────────────────────────────────────────
alerting:
  discord:
    webhook-url: "${DISCORD_WEBHOOK_URL}"
    default-alert:
      failure-threshold: 3      # 3 consecutive failures → alert
      success-threshold: 2      # 2 consecutive successes → auto-resolve
      send-on-resolved: true

  ntfy:
    topic: "homelab-alerts"
    url: "https://ntfy.sh"      # swap for self-hosted ntfy URL
    priority: 4                 # 1=min … 5=max
    default-alert:
      failure-threshold: 3
      send-on-resolved: true

# ── Endpoints ─────────────────────────────────────────────────────────────────
endpoints:

  # HTTP / HTTPS checks
  - name: jellyfin
    group: media
    url: "https://jellyfin.example.com/health"
    interval: 2m
    conditions:
      - "[STATUS] == 200"
      - "[RESPONSE_TIME] < 3000"
    alerts:
      - type: discord
      - type: ntfy

  - name: nextcloud
    group: storage
    url: "https://nextcloud.example.com/status.php"
    interval: 2m
    conditions:
      - "[STATUS] == 200"
      - "[BODY].installed == true"
      - "[RESPONSE_TIME] < 5000"
    alerts:
      - type: discord

  - name: home-assistant
    group: automation
    url: "https://ha.example.com/api/"
    interval: 1m
    headers:
      Authorization: "Bearer ${HA_TOKEN}"
    conditions:
      - "[STATUS] == 200"
    alerts:
      - type: ntfy
        failure-threshold: 2   # HA has flaky brief restarts — tighter threshold

  # TLS certificate expiry
  - name: cert-nextcloud
    group: certs
    url: "https://nextcloud.example.com"
    interval: 6h
    conditions:
      - "[STATUS] == 200"
      - "[CERTIFICATE_EXPIRATION] > 240h"   # alert 10 days before expiry
    alerts:
      - type: discord

  - name: cert-jellyfin
    group: certs
    url: "https://jellyfin.example.com"
    interval: 6h
    conditions:
      - "[STATUS] == 200"
      - "[CERTIFICATE_EXPIRATION] > 240h"
    alerts:
      - type: discord

  # ICMP ping — infra nodes
  - name: proxmox
    group: infra
    url: "icmp://proxmox.lan"
    interval: 30s
    conditions:
      - "[CONNECTED] == true"
    alerts:
      - type: ntfy
        failure-threshold: 2

  - name: pi-hole
    group: infra
    url: "icmp://pihole.lan"
    interval: 30s
    conditions:
      - "[CONNECTED] == true"
    alerts:
      - type: ntfy

  - name: nas
    group: infra
    url: "icmp://nas.lan"
    interval: 1m
    conditions:
      - "[CONNECTED] == true"
    alerts:
      - type: discord

  # TCP port checks — services without HTTP healthcheck endpoints
  - name: postgres
    group: databases
    url: "tcp://postgres.lan:5432"
    interval: 1m
    conditions:
      - "[CONNECTED] == true"
    alerts:
      - type: discord

  - name: redis
    group: databases
    url: "tcp://redis.lan:6379"
    interval: 1m
    conditions:
      - "[CONNECTED] == true"
    alerts:
      - type: discord

  # DNS resolution — verify Pi-hole is resolving LAN names
  - name: pihole-resolves-lan
    group: infra
    url: "192.168.1.53"                     # Pi-hole as DNS server
    interval: 5m
    dns:
      query-name: "proxmox.lan"
      query-type: "A"
    conditions:
      - "[BODY] == 192.168.1.10"            # expected A record
      - "[DNS_RCODE] == NOERROR"
    alerts:
      - type: discord

  # Keyword / body content check
  - name: grafana-login
    group: monitoring
    url: "https://grafana.example.com/login"
    interval: 5m
    conditions:
      - "[STATUS] == 200"
      - "[BODY] == pat(*grafana*)"          # page must contain 'grafana'
    alerts:
      - type: discord
```

---

## `docker-compose.yml`

```yaml
services:
  gatus:
    image: twinproduction/gatus:stable
    container_name: gatus
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - ./config.yaml:/config/config.yaml:ro   # read-only
      - gatus-data:/data                        # SQLite persistence
    environment:
      GATUS_CONFIG_PATH: /config/config.yaml
      DISCORD_WEBHOOK_URL: "${DISCORD_WEBHOOK_URL}"
      GATUS_USER: "${GATUS_USER}"
      GATUS_PASS_BCRYPT: "${GATUS_PASS_BCRYPT}"
      HA_TOKEN: "${HA_TOKEN}"
    cap_add:
      - NET_RAW          # required for ICMP ping checks [[3]](https://blog.mei-home.net/posts/k8s-migration-21-gatus/)
    sysctls:
      - net.ipv4.ping_group_range=0 2147483647

volumes:
  gatus-data:
```

Gatus auto-reloads when `config.yaml` changes on disk — no container restart needed [[1]](https://github.com/TwiN/gatus).

---

## Homepage Widget

Replace the Uptime Kuma widget in `services.yaml` with [[4]](https://gethomepage.dev/widgets/services/gatus/):

```yaml
- Monitoring:
    - Gatus:
        href: https://status.example.com
        icon: gatus.svg
        widget:
          type: gatus
          url: http://gatus:8080    # container name if on the same Docker network
          fields: ["up", "down", "uptime"]
```

Available fields: `up` (service count online), `down` (service count offline), `uptime` (7-day percentage).

---

## Prometheus + Grafana (optional)

`metrics: true` in `config.yaml` exposes `/metrics`. Add a Prometheus scrape job [[15]](https://raw.githubusercontent.com/TwiN/gatus/master/.examples/docker-compose-grafana-prometheus/config/config.yaml):

```yaml
# prometheus.yml
scrape_configs:
  - job_name: gatus
    static_configs:
      - targets: ["gatus:8080"]
```

Key exported metrics: `gatus_results_total{name,group,success}` and `gatus_results_duration_ms`. Import the community Grafana dashboard (ID `20232`) for state timelines and response-time history. This replaces the history you lose from Kuma if you choose not to enable SQLite — Prometheus becomes the long-term store [[3]](https://blog.mei-home.net/posts/k8s-migration-21-gatus/).

---

## Reflect

**What remains manual** after migration:
- No tool converts Kuma monitor JSON → Gatus YAML automatically. The SQLite query above is the fastest extraction path; ~20 monitors takes ~30 minutes to remap.
- Alert notification credentials (Discord webhook, ntfy topic, Telegram bot token) must be re-entered as environment variables — they are not stored in Kuma's exportable format in v2 [[8]](https://deepwiki.com/louislam/uptime-kuma/11-data-management-and-backup)[[9]](https://github.com/louislam/uptime-kuma/issues/6045).
- Kuma's `keyword` monitor with case-sensitive matching maps to `pat(*keyword*)` in Gatus, but Gatus does not support regex — complex patterns need a dedicated `/health` endpoint in the service [[1]](https://github.com/TwiN/gatus).
