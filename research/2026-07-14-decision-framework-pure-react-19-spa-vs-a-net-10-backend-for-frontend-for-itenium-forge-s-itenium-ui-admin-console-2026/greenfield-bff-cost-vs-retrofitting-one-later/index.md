---
title: "Greenfield BFF vs retrofitting later: where the asymmetry actually is"
date: 2026-07-14
depth: survey
format: md
topic: "Greenfield BFF cost vs retrofitting one later — where the asymmetry actually is: auth wiring, cookie/CSRF and CORS posture, session store, API surface assumptions, and what parts of an in-memory-token SPA become throwaway on migration. Is \"add it later\" a real option or a one-way door?"
topic_raw: "Greenfield BFF cost vs retrofitting one later — where the asymmetry actually is: auth wiring, cookie/CSRF and CORS posture, session store, API surface assumptions, and what parts of an in-memory-token SPA become throwaway on migration. Is \"add it later\" a real option or a one-way door?"
tags: [architecture, bff, spa, dotnet, oauth, reversibility, adr]
summary: "Adding a BFF later is a two-way door — if you build the SPA with one auth module, one fetch wrapper, relative paths and no client-side JWT parsing. The one-way door is the API, not the frontend."
citations: 25
reading_time_min: 9
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 485
issue: 6
---

> **Decision.** "Add the BFF later" is a **real option, not a one-way door** — *provided* the SPA is built so the token never escapes one module. The retrofit is ~2–5 days of mostly-deleting work: the API keeps its `JwtBearer` scheme unchanged because the BFF forwards a bearer token to it [[2]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/)[[3]](https://curity.io/blog/token-handler-the-single-page-applications-new-bff/), and the SPA-side change is one HTTP-client module plus a login link [[5]](https://timdeschryver.dev/blog/lets-make-our-spa-more-secure-by-consuming-a-duende-bff-with-angular). The genuine one-way doors are elsewhere: **API endpoints that only ever spoke cookie** (BFF-local endpoints) [[4]](https://docs.duendesoftware.com/bff/fundamentals/apis/local/), **SignalR/WebSockets through the BFF** [[14]](https://github.com/DuendeArchive/Support/issues/972), and **access-token claims read in component code** [[22]](https://docs.oidc-spa.dev/resources/jwt-of-the-access-token). Build the SPA now; keep the door open with the checklist below.

## First: two different things are called "BFF"

The reversibility answer flips depending on which one you mean.

| Flavour | What it is | Reversibility |
|---|---|---|
| **Security BFF / token handler** | A thin confidential-client host that owns the OIDC flow, keeps tokens server-side, hands the browser a `HttpOnly` cookie, and proxies `/api/*` to the real API with the access token re-attached [[1]](https://duendesoftware.com/blog/20210326-bff)[[3]](https://curity.io/blog/token-handler-the-single-page-applications-new-bff/) | **Two-way door.** It adds no business logic. It can be removed as easily as added. |
| **API-shaping BFF** (Sam Newman's original) | A per-client backend that aggregates, trims and reshapes responses; business rules migrate into it [[12]](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends) | **One-way door.** Microsoft's own guidance: "Code duplication is a probable outcome", and the pattern is *not* suitable when "only one interface interacts with the backend" [[12]](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends). |

The admin-console question is almost entirely the first flavour. Most of the internet's BFF-regret literature is about the second [[13]](https://dev.to/arkhan/backend-for-frontend-bff-in-2025-still-relevant-or-outdated-5dml). Don't import that regret into this decision.

## What actually changes when a BFF arrives

Sorted by what it costs you *at retrofit time*, not by how scary it sounds.

| Thing that changes | Before (in-memory-token SPA) | After (BFF) | Retrofit verdict |
|---|---|---|---|
| **IdP client config** | Public client + PKCE, client auth OFF [[23]](https://oneuptime.com/blog/post/2026-02-02-keycloak-clients-creation/view) | Confidential client + secret, client auth ON, new redirect URIs | **Mechanical** — a toggle and two URIs in Keycloak/OpenIddict. Minutes. |
| **Token acquisition** | `oidc-client-ts` / `react-oidc-context` in the browser, silent renew, iframe/refresh plumbing | Deleted. The BFF does code exchange back-channel [[5]](https://timdeschryver.dev/blog/lets-make-our-spa-more-secure-by-consuming-a-duende-bff-with-angular) | **Throwaway — and that's a refund.** You delete a dependency and ship less JS. |
| **Login / logout UX** | `signinRedirect()` calls, callback route, silent-renew route | `<a href="/bff/login">`, `<a href="/bff/logout?sid=…">` [[6]](https://docs.duendesoftware.com/bff/fundamentals/session/management/) | **Throwaway.** Callback + silent-renew routes get deleted. |
| **Who am I / claims** | Decode the JWT client-side | `GET /bff/user` returns a claims array; one TanStack Query hook [[24]](https://wrapt.dev/blog/using-duende-bff-with-react) | **Mechanical *if* claims are read in one place. Painful if `jwtDecode()` is sprinkled through components** — and decoding the access token is discouraged anyway: it is meant to be opaque to the client [[22]](https://docs.oidc-spa.dev/resources/jwt-of-the-access-token). |
| **HTTP client** | `Authorization: Bearer …` interceptor | `credentials: 'include'` + static `X-CSRF: 1` header [[2]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/) | **Mechanical, one file** — *if* you own a fetch wrapper. The new interceptor is strictly simpler than the old one [[5]](https://timdeschryver.dev/blog/lets-make-our-spa-more-secure-by-consuming-a-duende-bff-with-angular). |
| **CORS** | Full config on the API: allowed origins, headers, preflight | Deleted. Same-origin by construction [[1]](https://duendesoftware.com/blog/20210326-bff). A CORS error post-BFF means your topology is wrong [[7]](https://docs.duendesoftware.com/bff/troubleshooting/) | **Throwaway (net negative cost).** |
| **CSRF** | Non-issue (bearer tokens aren't ambient) | Mandatory: `SameSite` cookie **plus** a custom header to force preflight [[1]](https://duendesoftware.com/blog/20210326-bff) | **Mechanical** — one header in one wrapper. But see the silent-failure trap below. |
| **API auth scheme** | `AddJwtBearer` | **Unchanged.** The BFF forwards the user's access token to the remote API [[2]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/); the token handler pattern "requires minimal changes to existing web apps or microservices" [[3]](https://curity.io/blog/token-handler-the-single-page-applications-new-bff/) | **Zero.** This is the single biggest reason the "one-way door" framing is overstated. |
| **API base URL** | `https://api.example.com` from env | `/api` relative, proxied | **Mechanical if relative; annoying if absolute URLs are baked into feature code.** |
| **Deployment topology** | Static SPA on CDN + API | BFF host serves/fronts the SPA; must be same-site — third-party cookies are now dead in every major browser [[25]](https://duendesoftware.com/blog/20260414-the-cookie-apocalypse-already-happened) | **Genuinely new work:** one more deployable, ingress rules, `vite` dev proxy for `/bff` and `/api` [[17]](https://vite.dev/config/server-options). |
| **Session store** | None | Cookie holds the tokens unless you enable server-side sessions; with >1 replica you need a shared store (EF/DB) [[8]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/) and a shared Data Protection key ring [[10]](https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/implementation/key-storage-providers)[[11]](https://duendesoftware.com/blog/20260505-beyond-localhost-multi-instance-aspnetcore-deployment-with-dotnet-10) | **Genuinely new work.** This is the real operational tax, and it is the *same* tax greenfield or retrofit. |
| **Session expiry** | Token refresh fails → re-login | BFF API endpoints return **401, not a redirect** — the SPA must handle it explicitly [[7]](https://docs.duendesoftware.com/bff/troubleshooting/) | **Mechanical** (one interceptor branch). |
| **File downloads / `<img src>` to protected endpoints** | Broken by design: `<a>` and `<img>` can't carry an `Authorization` header, so you're already writing blob/objectURL hacks [[21]](https://alphahydrae.com/2021/02/how-to-display-an-image-protected-by-header-based-authentication/) | Just works — the cookie rides along | **Throwaway (refund again).** Retrofit *deletes* the blob hack. |
| **SignalR / WebSockets** | Bearer via `accessTokenFactory`, direct to API | ⚠ WebSocket handshakes can't set custom headers → the BFF's anti-forgery check rejects them; reported falling back to long-polling [[14]](https://github.com/DuendeArchive/Support/issues/972), native support was still an open ask [[15]](https://github.com/DuendeArchive/Support/issues/762) | **Genuinely painful.** The one item where retrofit cost is real and unbounded. |

### Score

- **Throwaway (and you *want* to throw it away):** OIDC JS library, silent renew, callback routes, token storage, CORS config, download blob hacks. Deleting these is the retrofit's dividend, not its cost.
- **Mechanical:** IdP client toggle, fetch wrapper (`credentials` + `X-CSRF`), 401 branch, `/bff/user` hook, relative base URLs. Hours, not days — *if centralised*.
- **Genuinely painful:** SignalR/WebSockets through the proxy; any real-time or long-lived connection. Plus the operational build-out (extra deployable, shared key ring, session store) — which you pay **whenever** you adopt, so it is not an asymmetry at all.

## Where the "it's just one module" claim breaks

The optimistic claim — *it's one HTTP-client file plus one ASP.NET auth block* — is **true for a disciplined codebase and false for a typical one**. It breaks precisely here:

1. **`jwtDecode(token)` in components.** Roles/tenant/name pulled off the decoded access token for UI gating. Post-BFF the token doesn't exist in the browser. Every one of those call sites is a rewrite against `/bff/user` [[24]](https://wrapt.dev/blog/using-duende-bff-with-react). This is the #1 blast-radius multiplier.
2. **`getAccessToken()` reachable from app state.** Once the token is in a Zustand/Redux store or a React context, arbitrary code reads it. Every reader is a call site.
3. **Ad-hoc `fetch(url, {headers: {Authorization: ...}})`** outside the wrapper — typically in a "quick" file-upload or export feature.
4. **Absolute API URLs** compiled into feature modules instead of a single base.
5. **Browser → third-party API calls** using the same token (or a different one). The BFF can't proxy what it doesn't know about; these need their own decision.
6. **Tests** that mint a fake JWT and stuff it into `localStorage`. Under a BFF, the auth fixture is a cookie/session — MSW handlers and E2E login helpers get rewritten.
7. **Real-time**: see SignalR above.

Everything on that list is **avoidable by construction, for free, today**. That is the whole game.

## The reverse door: what a BFF costs you if you later don't want it

Symmetry check — is the BFF itself a one-way door?

- **Removing it** is easy *if* you kept it a pure security proxy: the API still validates bearer JWTs [[2]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/), so a browser SPA could go back to talking to it directly. You'd re-add CORS and an OIDC JS library. Same 2–5 days, mirrored.
- **Removing it becomes hard** the moment you use *local/embedded* BFF endpoints, which are cookie-authenticated and are explicitly aimed at "single-consumer scenarios" [[4]](https://docs.duendesoftware.com/bff/fundamentals/apis/local/). Logic that lands there is logic no other client can reach. That is where the API-shaping BFF's one-way door quietly opens.
- **A second client (mobile/CLI/service) does *not* force you off the BFF** — it forces the *API* to stay bearer-capable, which it already is under proxy mode. If you ever need one API surface serving both cookie-bearing browsers and bearer-token clients, ASP.NET Core supports listing multiple schemes and trying each in order [[16]](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/). Duende BFF v4 also collapses the "one BFF per SPA" sprawl into one host with many frontends [[19]](https://duendesoftware.com/blog/20251202-duende-bffv4-now-available-multi-frontend-opentelemetry-and-simplified-security).
- **The standing cost you can't refund:** one more service to deploy, scale, monitor and patch; an extra network hop; a shared Data Protection key ring; a session store [[12]](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends)[[8]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/). For a Duende BFF specifically, a licence — free under $1M revenue, paid above [[18]](https://docs.duendesoftware.com/general/licensing/).

**Community opinion (dev.to, summarising 2024–25 Reddit/HN threads):** *"If you're a startup, skip it. If you're at scale, it's worth it."* / *"We ended up with four different backends — the maintenance is painful."* [[13]](https://dev.to/arkhan/backend-for-frontend-bff-in-2025-still-relevant-or-outdated-5dml) — note both quotes are about the API-shaping flavour, not the token handler.

## The traps that make the retrofit *feel* expensive

All three fail **silently**, which is why teams remember the migration as painful:

- `UseBff()` placed after `UseAuthorization()` → **anti-forgery enforcement is silently disabled, no error** [[7]](https://docs.duendesoftware.com/bff/troubleshooting/).
- A typo in a YARP metadata key → **no token attached, no anti-forgery check, no warning** [[7]](https://docs.duendesoftware.com/bff/troubleshooting/).
- Enough roles/claims → the auth cookie blows past the browser's 4 KB limit and chunking papers over it until it doesn't [[9]](https://duendesoftware.com/blog/20260429-aspnet-core-cookie-size-limits). Fix: server-side sessions, so the cookie carries only a session id [[8]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/).

## Keep-the-door-open checklist (the actual deliverable)

Build the pure SPA now. Do these ten things and the later BFF retrofit is a **2–5 day, one-PR change** instead of a rewrite. Every item is free — most are just good practice anyway.

1. **One auth module.** `src/auth/` is the *only* directory that knows the word "token". Nothing imports it except the HTTP client.
2. **Never put the access token in app state.** No Redux/Zustand/context slot for it. In-memory closure inside the auth module only.
3. **No `jwtDecode` outside the auth module.** Expose a typed `useCurrentUser()` returning `{ name, roles, … }`. Its *implementation* decodes the ID token today; tomorrow it fetches `/bff/user`. Consumers never notice. Add an ESLint `no-restricted-imports` rule on `jwt-decode`.
4. **You own the fetch wrapper.** One `apiClient` file. TanStack Query calls it; components never call `fetch` directly. This is the file that swaps `Authorization` for `credentials: 'include'` + `X-CSRF: 1` [[2]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/).
5. **Relative API paths.** Always `/api/...`. Use the Vite dev proxy for local dev [[17]](https://vite.dev/config/server-options) — which is also exactly how you'll run the BFF locally later.
6. **Keep the API bearer-only and client-agnostic.** No cookie auth, no session, no CORS-origin assumptions leaking into handlers. The API must never learn that a browser is talking to it.
7. **Handle 401 centrally**, in the wrapper, as "session gone → go to login". Don't distinguish "token expired" in feature code.
8. **Deploy the SPA and API same-site from day one** (`app.example.com` / `api.example.com`, or better `example.com` + `example.com/api`). Cross-*site* is now a dead end for cookies [[25]](https://duendesoftware.com/blog/20260414-the-cookie-apocalypse-already-happened); getting the origins right up front is free and removes the only genuinely structural retrofit blocker.
9. **Test fixtures go through the auth module too.** One `loginAs(role)` helper for E2E, one MSW auth handler. Don't hand-mint JWTs into `localStorage` across 40 spec files.
10. **Decide about real-time *now*.** If SignalR is on the roadmap, that's the one item that a BFF makes materially harder [[14]](https://github.com/DuendeArchive/Support/issues/972) — either plan a direct-to-API bearer channel for it, or price the workaround in.

## Effort, in numbers a lead can act on

| Path | Cost | Blast radius |
|---|---|---|
| **BFF greenfield, now** | 2–4 days: BFF host, OIDC config, YARP routes, `/bff/user` hook, deploy pipeline + shared key ring/session store [[8]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/)[[10]](https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/implementation/key-storage-providers). Wiring a React SPA to it is <100 lines [[24]](https://wrapt.dev/blog/using-duende-bff-with-react) | New service, permanent |
| **Retrofit later, checklist followed** | 2–5 days. Files touched: `apiClient.ts`, `auth/*`, `vite.config.ts`, IdP client config, `Program.cs`, ingress. Net lines **negative** | ~6 files + 1 new project |
| **Retrofit later, checklist ignored** | 2–4 weeks. Every `jwtDecode` call site, every ad-hoc `fetch`, every test fixture, plus the SignalR problem | Whole app |
| **Never** (stay pure SPA) | 0 | — |

The asymmetry is therefore **not between greenfield and retrofit** — it's between a *disciplined* SPA and a *leaky* one. The BFF decision is a two-way door [[20]](https://thoughtbot.com/blog/one-way-vs-two-way-door-decisions); the discipline decision is the one that's hard to reverse.
