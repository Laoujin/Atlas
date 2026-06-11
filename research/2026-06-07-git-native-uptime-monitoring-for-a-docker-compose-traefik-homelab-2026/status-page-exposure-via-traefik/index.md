---
title: "Status page exposure via Traefik"
date: 2026-06-08
depth: ceo
format: md
topic: "Status page exposure via Traefik"
topic_raw: "Status page exposure via Traefik"
issue: 198
tags: [traefik, reverse-proxy, security, api-exposure]
summary: "Never expose Traefik's API/dashboard publicly without authentication. Default endpoints leak full configuration; use middleware, network isolation, and recent patches."
citations: 9
reading_time_min: 3
cost_usd: 0.27
duration_sec: 81
model: "Haiku 4.5"
cover: cover.svg
---

> **Decision:** Traefik's `api@internal` service and status endpoints expose sensitive configuration details (routers, services, middleware, raw config) and should never be accessible without authentication and network isolation. Even `/ping` health-check endpoints bypass auth by design. In shared environments (e.g., Kubernetes Gateway API), verify your version is patched against CVE-2026-44774 (affects v2.11 <2.11.46, v3.6 <3.6.17, v3.7 <3.7.1).

## What Gets Exposed

Traefik's API handler publishes all configuration elements: HTTP/TCP/UDP routers, services, middlewares, EntryPoints, overview statistics, version info, and raw config dumps [[1]](https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/). In production, this is never acceptable because it leaks the entire infrastructure topology and may include sensitive data (credentials, internal service names, backend addresses) [[2]](https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/).

The `/ping` health-check endpoint is specifically excluded from authentication to allow external load-balancers and health-checkers to verify Traefik's status [[3]](https://dev.to/karvounis/advanced-traefik-configuration-tutorial-tls-dashboard-ping-metrics-authentication-and-more-4doh), creating an unauthenticated information disclosure surface if not isolated.

## Attack Vectors

**Reconnaissance:** Exposed endpoints provide attackers full visibility into routing rules, backend services, and middleware configuration, enabling targeted attacks and lateral movement [[4]](https://traefik.io/glossary/api-security).

**Configuration write access:** In Kubernetes Gateway API deployments, attackers with HTTPRoute creation permissions can exploit CVE-2026-44774 to access `rest@internal` and gain PUT access to `/api/providers/rest`, allowing live dynamic-configuration rewrites—bypassing authentication on REST provider access even when `providers.rest.insecure=false` [[5]](https://github.com/traefik/traefik/security/advisories/GHSA-96qj-4jj5-wcjc).

**Service disruption:** Misconfigured REST or metrics endpoints allow attackers to toggle routes offline or redirect traffic [[2]](https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/).

## Mitigation

1. **Never expose the API port publicly** [[2]](https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/). Keep it on internal networks only (principle of least privilege).
2. **Add authentication middleware** to `api@internal` routers: BasicAuth, DigestAuth, or ForwardAuth (OAuth2/OIDC) [[2]](https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/).
3. **Isolate health-check endpoints** on a dedicated entry point or proxy `/ping` from a public entry point without exposing the admin port [[3]](https://dev.to/karvounis/advanced-traefik-configuration-tutorial-tls-dashboard-ping-metrics-authentication-and-more-4doh).
4. **Update immediately** to patched versions if using Gateway API: v2.11.46+, v3.6.17+, or v3.7.1+ [[5]](https://github.com/traefik/traefik/security/advisories/GHSA-96qj-4jj5-wcjc).
5. **Supplement with IP allowlisting** using the IPAllowlist middleware to restrict access by source IP or CIDR range [[2]](https://doc.traefik.io/traefik/reference/install-configuration/api-dashboard/).

## Recent Vulnerabilities

Traefik Labs issued multiple security patches in 2026. Most critical: **CVE-2026-44774** (June 5, 2026) allows a low-privileged tenant in shared Gateway deployments to expose and modify the REST provider configuration without needing explicit API access, turning REST provider bypass into a privilege-escalation vulnerability [[5]](https://github.com/traefik/traefik/security/advisories/GHSA-96qj-4jj5-wcjc).

Never rely on `providers.rest.insecure=false` as the sole defense—layer authentication, network isolation, and version updates.
