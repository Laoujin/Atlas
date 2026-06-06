---
title: "Resource Footprint, Auth Model & Reverse-Proxy Fit"
date: 2026-06-06
depth: standard
format: md
topic: "Resource footprint, auth model & reverse-proxy fit"
topic_raw: "Resource footprint, auth model & reverse-proxy fit"
issue: 193
tags: [self-hosted, dashboard, homepage, authentication, reverse-proxy, traefik, caddy, nginx, docker]
summary: "Homepage is lean (~50–150 MB RAM), has zero built-in auth by design, and integrates cleanly with Traefik, Caddy, and nginx via forward auth—HOMEPAGE_ALLOWED_HOSTS must list every non-localhost hostname since v1.0."
citations: 16
reading_time_min: 5
cover: cover.svg
cost_usd: 2.46
duration_sec: 892
model: "Sonnet 4.6"
---

> **TL;DR.** Homepage ships as an 80 MB image [[4]](https://hub.docker.com/r/gethomepage/homepage) and uses ~50–150 MB RAM in practice [[2]](https://github.com/gethomepage/homepage/discussions/6251)[[11]](https://www.homelabstarter.com/homelab-dashboard-homarr-dashy/)—lean against every other feature-rich dashboard. It has **zero built-in authentication and will never add it** [[3]](https://github.com/gethomepage/homepage/discussions/529); all auth is delegated to the reverse proxy. Traefik with Docker labels is the tightest fit; Caddy needs one route block; nginx works with manual config. Since v1.0, `HOMEPAGE_ALLOWED_HOSTS` is required for every non-localhost hostname [[1]](https://gethomepage.dev/installation/).

---

## Resource Footprint

[Homepage](https://github.com/gethomepage/homepage) ⭐ 31k is a Next.js 15 app served by Node.js. Pages pre-render statically; widget data is fetched server-side and streamed to the browser, keeping the JS bundle small but the server process persistent.

**Dashboard RAM comparison** (steady-state, Docker):

| Dashboard                         | RAM           | Image    | Notes                                          |
|-----------------------------------|---------------|----------|------------------------------------------------|
| [Homer][homer] ⭐ 11.4k            | ~30 MB        | <10 MB   | Static HTML; no live API polling               |
| **[Homepage][hp] ⭐ 31k**          | **50–150 MB** | **80 MB**| Next.js 15, server-side widget proxying        |
| [Dashy][dashy] ⭐ 25.4k            | ~150 MB       | ~90 MB   | Vue SPA                                        |
| [Homarr][homarr] ⭐ 4k             | 200–600 MB    | ~250 MB  | v1.0 confirmed RAM regression [[12]][c12]      |

[homer]:  https://github.com/bastienwirtz/homer
[hp]:     https://github.com/gethomepage/homepage
[dashy]:  https://github.com/lissy93/dashy
[homarr]: https://github.com/homarr-labs/homarr
[c12]:    https://github.com/homarr-labs/homarr/issues/3759

[[11]](https://www.homelabstarter.com/homelab-dashboard-homarr-dashy/) CPU is negligible at idle; brief spikes during widget polling (every 30 s per service by default). A Pi 4 handles it without issue.

**Image size.** `ghcr.io/gethomepage/homepage:latest` is **80.6 MB** compressed (AMD64 + ARM64) with 1 M+ Docker Hub pulls [[4]](https://hub.docker.com/r/gethomepage/homepage). One TrueNAS deployment measured **118 MiB** RSS on a fully-configured instance (Next.js 15.5.x, ~450 ms startup) [[2]](https://github.com/gethomepage/homepage/discussions/6251)—the high end of the observed range.

**Docker socket.** Auto-discovery requires access to the Docker socket. Direct bind-mount (`/var/run/docker.sock:ro`) forces the container to run as root. The safer path is [Tecnativa/docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy) ⭐ 2.5k, which exposes a read-only subset of the API [[15]](https://github.com/Tecnativa/docker-socket-proxy)[[6]](https://gethomepage.dev/configs/docker/):

```yaml
dockerproxy:
  image: ghcr.io/tecnativa/docker-socket-proxy:latest
  environment: { CONTAINERS: 1, SERVICES: 1, TASKS: 1, POST: 0 }
  volumes: ["/var/run/docker.sock:/var/run/docker.sock:ro"]
```

Then in Homepage's `docker.yaml`:

```yaml
my-docker:
  host: dockerproxy
  port: 2375
```

---

## Auth Model

**No built-in auth—permanently.** Maintainers explicitly closed this [[3]](https://github.com/gethomepage/homepage/discussions/529):

> "AuthN / AuthZ is brutally hard to securely implement … reverse-proxies have become incredibly user-friendly."

Homepage is also a **single shared view**—no per-user dashboards or role-based visibility, so per-user ACLs would be moot regardless.

**`HOMEPAGE_ALLOWED_HOSTS`.** Mandatory since v1.0 for any non-localhost URL [[1]](https://gethomepage.dev/installation/). Guards the server-side API proxy against request-forgery. List every domain or IP:port used to reach the container—reverse proxies rewrite `Host` to the public domain, so add that domain [[16]](https://github.com/gethomepage/homepage/discussions/4971):

```
HOMEPAGE_ALLOWED_HOSTS=dashboard.home.example.com,192.168.1.10:3000
```

`localhost:3000` and `127.0.0.1:3000` are always permitted without explicit listing.

**Supported patterns:**

| Pattern                         | Proxy required        | Effort  | Notes                                                     |
|---------------------------------|-----------------------|---------|-----------------------------------------------------------|
| VPN / Tailscale                 | None                  | Low     | No public exposure; simplest security model               |
| HTTP Basic Auth                 | nginx / Caddy         | Low     | Single shared password; no MFA                            |
| Forward Auth ([Authelia][alib]) ⭐ 28k  | Traefik / Caddy | Medium  | TOTP/WebAuthn; lighter footprint than Authentik [[14]][c14] |
| Forward Auth ([Authentik][autk]) ⭐ 21.8k | Traefik / Caddy | Medium | Full OIDC + login portal; heavier baseline [[7]][c7]       |
| Cloudflare Access               | Cloudflare Tunnel     | Low     | Zero open inbound ports                                   |

[alib]: https://github.com/authelia/authelia
[autk]: https://github.com/goauthentik/authentik
[c14]:  https://www.authelia.com/blog/authelia--traefik-setup-guide/
[c7]:   https://docs.goauthentik.io/add-secure-apps/providers/proxy/server_traefik/

⚠ Homepage does **not** consume forwarded user headers (`X-Authentik-Username`, `Remote-User`, etc.) for per-user customisation—whoever passes auth sees the same dashboard [[3]](https://github.com/gethomepage/homepage/discussions/529).

---

## Reverse-Proxy Fit

Homepage listens on **port 3000** and requires WebSocket/SSE passthrough (`Upgrade: websocket`, `Connection: upgrade`) for live widget updates [[10]](https://github.com/gethomepage/homepage/discussions/1035). All three major proxies handle this cleanly.

### [Traefik](https://github.com/traefik/traefik) ⭐ 63.6k — best fit for Docker-native setups

Auto-discovers services via container labels; forward-auth middleware hooks in without extra routing configuration.

**Minimal labels (TLS + HTTPS):**

```yaml
labels:
  traefik.enable: "true"
  traefik.http.routers.homepage.rule: "Host(`dashboard.example.com`)"
  traefik.http.routers.homepage.entrypoints: "websecure"
  traefik.http.routers.homepage.tls.certresolver: "myresolver"
  traefik.http.services.homepage.loadbalancer.server.port: "3000"
```

[[5]](https://github.com/gethomepage/homepage/discussions/3256)

**Add Authentik forward auth** (one label on Homepage; middleware defined on the Authentik outpost):

```yaml
# homepage service
traefik.http.routers.homepage.middlewares: "authentik@docker"

# authentik-proxy service
traefik.http.middlewares.authentik.forwardauth.address: "http://authentik-proxy:9000/outpost.goauthentik.io/auth/traefik"
traefik.http.middlewares.authentik.forwardauth.trustForwardHeader: "true"
traefik.http.middlewares.authentik.forwardauth.authResponseHeaders: "X-authentik-username,X-authentik-groups,X-authentik-email"
```

[[7]](https://docs.goauthentik.io/add-secure-apps/providers/proxy/server_traefik/)[[13]](https://gist.github.com/LukasForst/9898e08b6290821d6ccfcd0b6ad4f376)

For Authelia instead, swap the middleware address for `http://authelia:9091/api/authz/forward-auth` and adjust `authResponseHeaders` accordingly [[14]](https://www.authelia.com/blog/authelia--traefik-setup-guide/).

### [Caddy](https://github.com/caddyserver/caddy) ⭐ 73.2k — simplest config, zero-config HTTPS

One `route` block handles auth and proxying in order [[8]](https://docs.goauthentik.io/add-secure-apps/providers/proxy/server_caddy/)[[9]](https://caddyserver.com/docs/caddyfile/directives/forward_auth):

```caddy
dashboard.example.com {
    route {
        # Authentik outpost passthrough
        reverse_proxy /outpost.goauthentik.io/* http://authentik-outpost:9000
        forward_auth http://authentik-outpost:9000 {
            uri /outpost.goauthentik.io/auth/caddy
            copy_headers X-Authentik-Username X-Authentik-Groups X-Authentik-Email X-Authentik-Name X-Authentik-Uid X-Authentik-Jwt
            trusted_proxies private_ranges
        }
        reverse_proxy homepage:3000
    }
}
```

For Authelia, replace the `forward_auth` block [[9]](https://caddyserver.com/docs/caddyfile/directives/forward_auth):

```caddy
    forward_auth authelia:9091 {
        uri /api/authz/forward-auth
        copy_headers Remote-User Remote-Groups Remote-Name Remote-Email
    }
```

⚠ `copy_headers` field names are case-sensitive in Caddy; wrong capitalisation produces empty headers [[8]](https://docs.goauthentik.io/add-secure-apps/providers/proxy/server_caddy/).

### nginx — manual, well-documented

The `Upgrade` and `Connection` headers are required; omitting them breaks real-time widget polling [[10]](https://github.com/gethomepage/homepage/discussions/1035):

```nginx
server {
    listen 443 ssl;
    server_name dashboard.example.com;
    location / {
        proxy_pass               http://homepage:3000/;
        proxy_set_header Host              $http_host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade           $http_upgrade;
        proxy_set_header Connection        "upgrade";
    }
}
```

Add `auth_basic` / `auth_basic_user_file` for htpasswd, or `auth_request` pointing to Authelia/Authentik for forward auth.

### Quick-pick

| Feature              | Traefik                    | Caddy                      | nginx                        |
|----------------------|----------------------------|----------------------------|------------------------------|
| Config style         | Docker labels              | Caddyfile                  | nginx.conf                   |
| Auto-HTTPS           | ACME cert resolver         | Built-in (zero-config)     | Manual / certbot             |
| Forward auth         | Native middleware labels   | `forward_auth` directive   | `auth_request` module        |
| Docker auto-discovery| ✓ native                   | ✗                          | ✗                            |
| K8s support          | IngressRoute CRD              | Ingress controller      | Ingress controller           |
| Homepage fit         | ✓ Excellent                | ✓ Good                     | ✓ Manual                     |

