---
title: "Auth & session state for a React 19 SPA on Forge: kill the localStorage plan"
date: 2026-07-13
depth: ceo
format: md
topic: "Decide how a React 19 SPA should hold auth/session state against a .NET OIDC provider (Keycloak or OpenIddict) issuing JWTs in 2026: localStorage vs in-memory + httpOnly cookie refresh vs BFF, which library, where decoded identity lives, refresh/401 interceptors vs query-cache retry, and route-guard patterns."
topic_raw: "Decide how a React 19 SPA should hold auth/session state against a .NET OIDC provider (Keycloak or OpenIddict) issuing JWTs in 2026. Cover: the security verdict on storing JWTs in localStorage (the project's current stated plan) versus in-memory access token + refresh via a httpOnly SameSite cookie or the OIDC Authorization Code + PKCE + silent-refresh flow, and what OWASP and the OAuth 2.0 for Browser-Based Applications BCP actually recommend in 2026; which library to use (oidc-client-ts, react-oidc-context, keycloak-js, @axa-fr/react-oidc, or hand-rolled); where the decoded user identity (userId, roles, capabilities) should LIVE — a global store, React context, or the query cache — and why that answer is usually \"not Redux\"; token refresh and 401-retry interceptors and how they interact with a query cache's retry logic; and route-guard / capability-check patterns. Deliver a one-page decision with the concrete recommended wiring."
tags: [react, oidc, security, keycloak, dotnet, state-management]
summary: "Drop the localStorage JWT plan: use react-oidc-context with an in-memory access token, put roles/capabilities behind a /me query instead of in the token, and treat a .NET BFF as the target end-state."
citations: 11
reading_time_min: 3
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 212
issue: 2
---

> **Decision.** Delete "JWT in localStorage" from the README. Every authority says the same thing: OWASP — *"Do not store session identifiers in local storage as the data is always accessible by JavaScript"* [[1]](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html); the OAuth 2.0 for Browser-Based Apps BCP ranks architectures **BFF > token-mediating backend > browser-based public client**, and reserves the BFF for *"business applications, sensitive applications, and applications that handle personal data"* [[2]](https://www.ietf.org/archive/id/draft-ietf-oauth-browser-based-apps-26.html). Ship **Authorization Code + PKCE via [react-oidc-context](https://github.com/authts/react-oidc-context) ⭐ 1.0k, access token in memory only**, refresh token rotated (never in `localStorage`) — and plan a **.NET BFF** ([Duende.BFF](https://docs.duendesoftware.com/bff/)) as the end-state, since your backend is already ASP.NET Core.

## The verdict on localStorage

Not "less ideal" — the wrong tool. A single XSS in any dependency of an Nx monorepo exfiltrates the token instantly and silently. The BCP goes further: with JS execution, an attacker can *"inject a hidden iframe and launch a silent Authorization Code flow"* [[2]](https://www.ietf.org/archive/id/draft-ietf-oauth-browser-based-apps-26.html) — so in-memory storage is a **damage limiter, not a fix**. That is exactly why the BCP's top-ranked answer keeps tokens out of the browser: with a BFF *"there are no tokens available to extract from the browser"*, only an httpOnly `SameSite` session cookie plus a CSRF header [[3]](https://duendesoftware.com/blog/20210326-bff).

Refresh tokens: if you keep them browser-side, the AS **MUST** rotate them on every use or sender-constrain them [[2]](https://www.ietf.org/archive/id/draft-ietf-oauth-browser-based-apps-26.html) — Keycloak and OpenIddict both do rotation. Do **not** design around iframe `prompt=none` silent renew: third-party-cookie blocking killed it as a general mechanism [[4]](https://learn.microsoft.com/en-us/entra/identity-platform/reference-third-party-cookies-spas), and it only survives if the IdP is on the *same registrable domain* as the app (`auth.itenium.be` / `app.itenium.be`). Rotating refresh tokens are the sanctioned replacement [[5]](https://auth0.com/docs/secure/tokens/refresh-tokens/use-refresh-token-rotation).

## Library

| Choice | ⭐ | Verdict |
|-------------------------------------------------------------|-------|---------------------------------------------------------------------------------------------------|
| [react-oidc-context](https://github.com/authts/react-oidc-context) | 1.0k  | ✓ **Pick this.** Thin React 19 wrapper over `oidc-client-ts`; protocol-generic → Keycloak *and* OpenIddict [[6]](https://github.com/authts/react-oidc-context) |
| [oidc-client-ts](https://github.com/authts/oidc-client-ts)   | 1.9k  | ✓ The engine underneath; use directly only outside React [[7]](https://github.com/authts/oidc-client-ts) |
| [@axa-fr/react-oidc](https://github.com/AxaFrance/react-oidc) | 676   | ⚠ Service-worker token isolation — the best *pure-SPA* hardening if you refuse a BFF [[8]](https://github.com/AxaFrance/react-oidc) |
| [keycloak-js](https://github.com/keycloak/keycloak-js)       | 88    | ✗ Vendor-locked, version-pinned to the server; Keycloak itself deprecated its adapters and points at standard OIDC libraries [[9]](https://www.keycloak.org/2023/03/adapter-deprecation-update) |
| hand-rolled                                                  | —     | ✗ You would re-implement PKCE, rotation, single-flight refresh and clock skew. |

**Google/Microsoft login belongs in the IdP**, not the frontend: Keycloak identity brokering / OpenIddict external providers. Your "reusable login lib" then shrinks to config + guards + a `<Can>` component — which is the whole point.

## Where identity lives (and why not Redux)

- **Access token + `isAuthenticated`** → `AuthProvider` context from `react-oidc-context`. It is already a Context; copying it into Redux/Zustand creates a second copy that goes stale.
- **Roles & capabilities** → **not the JWT**. Your backend's own worry about token bloat resolves cleanly here: keep the JWT to `sub` + coarse roles, and serve fine-grained capabilities from `GET /me`, cached in **TanStack Query** ⭐ 50k. Capabilities are *server state* — the query cache is the correct home, and it gives you revocation without re-login (invalidate `['me']`). `ICurrentUser` stays the server-side authority; `/me` is its projection.
- **Redux** buys nothing here: there is no client-side reducer logic, no time-travel need. Zustand is only warranted if you later add genuinely client-owned session UI state (impersonation banner, tenant switcher) [[10]](https://tkdodo.eu/blog/zustand-and-react-context).

## Refresh, 401s, and query retries

Let the OIDC library own refresh (`automaticSilentRenew`) — it single-flights. The fetch wrapper reads `auth.user?.access_token` **at call time** (never captured at module scope, or you send a stale token). Then disarm the double-retry: an axios interceptor that retries on 401 *and* TanStack Query retrying 3× produces a refresh stampede [[11]](https://github.com/TanStack/query/discussions/3653).

```ts
// one place decides; TanStack never retries an auth failure
retry: (count, err) => err.status !== 401 && err.status !== 403 && count < 3
// QueryCache onError: 401 → auth.signinSilent() once → invalidateQueries(); on failure → signinRedirect()
```

## Guards

Route guard in the router's `beforeLoad`/loader (redirect on `!isAuthenticated`, `await` the `['me']` query so capabilities are present before render). Capability checks are a `<Can capability="x">` reading the `/me` cache. Both are **UX only** — enforcement stays in Forge's authorization policies [[2]](https://www.ietf.org/archive/id/draft-ietf-oauth-browser-based-apps-26.html).
