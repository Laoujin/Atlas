---
title: "Docker-Native Wiring Patterns for Home Lab Notification Stacks"
date: 2026-06-09
depth: standard
format: md
topic: "Docker-native wiring patterns"
topic_raw: "Docker-native wiring patterns"
issue: 213
tags: [docker, networking, traefik, home-lab, ntfy, gotify, apprise, compose]
summary: "Five composable patterns — named bridge networks, external proxy network, socket proxy, service_healthy ordering, and secrets mounts — cover 90% of home-lab notification stack wiring."
citations: 15
reading_time_min: 7
cover: cover.svg
cost_usd: 1.02
duration_sec: 310
model: "Sonnet 4.6"
---

> **TL;DR** Use a **named custom bridge** for same-host service groups, an **external `proxy` network** shared with Traefik for TLS termination, and a **socket proxy** to avoid bind-mounting the Docker socket directly into Traefik. Wire startup order with `depends_on: condition: service_healthy` and keep tokens out of environment variables with the `_FILE` secret convention. These five patterns compose cleanly for ntfy, Gotify, and Apprise stacks. [[2]](https://docs.docker.com/compose/how-tos/networking/) [[3]](https://docs.docker.com/guides/traefik/) [[6]](https://github.com/tecnativa/docker-socket-proxy)

---

## Pattern 1 — Network driver selection

Docker ships seven drivers [[1]](https://docs.docker.com/engine/network/drivers/). For a home lab notification stack, three matter:

| Driver    | Use case                                                                       | Home lab example                           |
| --------- | ------------------------------------------------------------------------------ | ------------------------------------------ |
| `bridge`  | Default; single-host container groups; DNS by service name                     | Apprise + ntfy on the same host            |
| `macvlan` | Container needs its own LAN IP/MAC; no NAT [[11]](https://www.virtualizationhowto.com/2025/07/docker-networking-tutorial-bridge-vs-macvlan-vs-overlay-for-home-labs/) | Zigbee2MQTT, VoIP adapters                 |
| `host`    | Container binds directly to host ports; zero NAT overhead                      | IoT listener that must see LAN broadcasts  |

`overlay` is Swarm-only; `none` is for maximum isolation. For everything else, `bridge` is correct.

---

## Pattern 2 — Named custom networks (same-host service grouping)

Compose auto-creates a `<project>_default` bridge [[2]](https://docs.docker.com/compose/how-tos/networking/). Services on it resolve each other by **service name** via Docker's internal DNS at `127.0.0.11`. Use a named network when you want explicit topology control:

```yaml
# docker-compose.yml for your notification stack
networks:
  notify-internal:  # no public egress, containers talk by name

services:
  ntfy:
    image: binwiederhier/ntfy:latest
    networks: [notify-internal]

  apprise:
    image: caronc/apprise:latest
    networks: [notify-internal]
    environment:
      # Apprise reaches ntfy by service name — no host IP or port mapping needed
      NTFY_URL: "http://ntfy:80"
```

Apprise → ntfy URL is `http://ntfy:80/your-topic` [[9]](https://jellywatch.app/blog/jellyfin-notifications-ntfy-gotify-apprise-webhook-2026). No published port is required for internal traffic. The service name `ntfy` resolves to the container's IP on the shared network [[12]](https://oneuptime.com/blog/post/2026-01-16-docker-compose-service-discovery/view).

---

## Pattern 3 — External `proxy` network for Traefik TLS termination

Traefik typically lives in its own Compose project. The standard pattern is one pre-created external network that Traefik and every back-end service both join [[10]](https://oneuptime.com/blog/post/2026-01-25-communication-between-docker-compose-projects/view):

```bash
# Run once; must exist before any compose up
docker network create proxy
```

**Traefik project** (`traefik/docker-compose.yml`):
```yaml
networks:
  proxy:
    external: true

services:
  traefik:
    image: traefik:v3
    networks: [proxy]
    ports: ["80:80", "443:443"]
```

**Notification project** (`notify/docker-compose.yml`):
```yaml
networks:
  notify-internal:        # intra-stack; no external access
  proxy:
    external: true        # joins the shared Traefik network

services:
  ntfy:
    image: binwiederhier/ntfy:latest
    networks: [notify-internal, proxy]   # bridges both networks
    labels:
      - traefik.enable=true
      - traefik.http.routers.ntfy.rule=Host(`ntfy.home.example.com`)
      - traefik.http.routers.ntfy.entrypoints=websecure
      - traefik.http.routers.ntfy.tls.certresolver=letsencrypt
      - traefik.http.services.ntfy.loadbalancer.server.port=80
      - traefik.docker.network=proxy     # required when container has >1 network
```

ntfy also needs `behind-proxy: true` in `server.yml` for correct IP extraction [[13]](https://aalderink.nl/2024/09/21/ntfy-notifications/). Apprise stays on `notify-internal` only — no need to expose it to the proxy layer.

---

## Pattern 4 — Socket proxy (security hardening for Traefik)

Bind-mounting `/var/run/docker.sock` directly into Traefik is root-equivalent access to the host [[6]](https://github.com/tecnativa/docker-socket-proxy). Replace it with [Tecnativa/docker-socket-proxy](https://github.com/tecnativa/docker-socket-proxy) ⭐ 6.1k, an HAProxy-based filter that returns `403` for disallowed endpoints.

```yaml
# traefik/docker-compose.yml (extended)
networks:
  socket-net:     # isolated; only socket-proxy + traefik
  proxy:
    external: true

services:
  socket-proxy:
    image: tecnativa/docker-socket-proxy
    restart: unless-stopped
    networks: [socket-net]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      CONTAINERS: 1   # Traefik only needs read access to containers
      NETWORKS: 1
      # EVERYTHING ELSE defaults to 0 (denied)

  traefik:
    image: traefik:v3
    restart: unless-stopped
    networks: [socket-net, proxy]
    command:
      - --providers.docker=true
      - --providers.docker.endpoint=tcp://socket-proxy:2375  # TCP, not socket mount
      - --providers.docker.exposedbydefault=false
      - --entrypoints.websecure.address=:443
    ports: ["80:80", "443:443"]
    depends_on: [socket-proxy]
```

`socket-net` is never exposed outside the host. `socket-proxy` never joins the `proxy` network — Traefik is the only service that talks to it [[7]](https://github.com/PythonicAccountant/traefik-docker-socket-proxy-docker-compose-example).

---

## Pattern 5 — `service_healthy` startup ordering

`depends_on: started` (the default) checks only that the container process launched, not that the service is accepting connections. Use `service_healthy` when one service must be fully ready before another starts [[4]](https://docs.docker.com/compose/how-tos/startup-order/):

```yaml
services:
  ntfy:
    image: binwiederhier/ntfy:latest
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:80/v1/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s   # grace period before first check

  apprise:
    image: caronc/apprise:latest
    depends_on:
      ntfy:
        condition: service_healthy  # waits for ntfy's healthcheck to pass
        restart: true               # restart apprise if ntfy restarts
```

`start_period` prevents false-unhealthy on slow-starting containers. If ntfy never becomes healthy, Apprise queues indefinitely — set `start_period` generously for cold-start hardware [[8]](https://oneuptime.com/blog/post/2026-02-08-how-to-run-ntfy-in-docker-for-push-notifications/view).

---

## Pattern 6 — Secrets and credentials

Two common wiring mistakes: hardcoding tokens in compose files, and confusing `env_file:` with `.env` [[14]](https://docs.docker.com/compose/how-tos/environment-variables/best-practices/):

| Mechanism           | Where it lands                         | Use for                                 |
| ------------------- | -------------------------------------- | --------------------------------------- |
| `env_file:`         | Inside the container's environment     | Non-sensitive config (TZ, ports)        |
| `.env` file         | Compose-file interpolation **only**    | Build-time variables (`${VERSION}`)     |
| `secrets:` + `_FILE` | `/run/secrets/<name>` (tmpfs mount)   | API tokens, passwords, webhook secrets  |

```yaml
secrets:
  ntfy_token:
    file: ./secrets/ntfy_token.txt

services:
  apprise:
    image: caronc/apprise:latest
    secrets: [ntfy_token]
    environment:
      # Many images read <VAR>_FILE and load the secret from disk
      NTFY_TOKEN_FILE: /run/secrets/ntfy_token
```

Secrets are mounted as an in-memory tmpfs, not persisted on disk in the container, and are not visible in `docker inspect` environment output [[5]](https://docs.docker.com/compose/how-tos/use-secrets/). For Gotify's application token in Apprise, the URL pattern is `gotify://host:port/TOKEN` — keep the token in a secret, not inline in the Apprise config YAML [[15]](https://thomaswildetech.com/blog/2026/01/05/the-holy-grail-of-self-hosted-notifications/).

---

## Full reference: ntfy + Apprise + Traefik

Putting all patterns together in a single-file reference:

```yaml
# notify/docker-compose.yml
networks:
  notify-internal: {}
  proxy:
    external: true

secrets:
  ntfy_token:
    file: ./secrets/ntfy_token.txt

services:
  ntfy:
    image: binwiederhier/ntfy:latest
    restart: unless-stopped
    command: serve
    networks: [notify-internal, proxy]
    volumes:
      - ntfy-cache:/var/cache/ntfy
      - ntfy-auth:/var/lib/ntfy
      - ./ntfy/server.yml:/etc/ntfy/server.yml:ro
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:80/v1/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s
    labels:
      - traefik.enable=true
      - traefik.docker.network=proxy
      - traefik.http.routers.ntfy.rule=Host(`ntfy.home.example.com`)
      - traefik.http.routers.ntfy.entrypoints=websecure
      - traefik.http.routers.ntfy.tls.certresolver=letsencrypt
      - traefik.http.services.ntfy.loadbalancer.server.port=80

  apprise:
    image: caronc/apprise:latest
    restart: unless-stopped
    networks: [notify-internal]   # internal only; Traefik not needed
    secrets: [ntfy_token]
    environment:
      APPRISE_STATEFUL_MODE: simple
      NTFY_URL: "http://ntfy:80"  # DNS by service name; no host port required
    depends_on:
      ntfy:
        condition: service_healthy
        restart: true
    volumes:
      - ./apprise/config:/config

volumes:
  ntfy-cache:
  ntfy-auth:
```

Key decisions visible in this file:
- `ntfy` bridges both networks; `apprise` stays internal-only.
- `traefik.docker.network=proxy` is required because ntfy has two network attachments [[3]](https://docs.docker.com/guides/traefik/).
- Token never appears in plaintext — consumed via secret mount.
- Healthcheck gates Apprise startup; `restart: true` propagates ntfy restarts downstream.
