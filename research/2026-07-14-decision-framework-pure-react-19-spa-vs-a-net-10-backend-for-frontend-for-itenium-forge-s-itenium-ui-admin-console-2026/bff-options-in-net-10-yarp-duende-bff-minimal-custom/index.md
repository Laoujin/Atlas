---
title: "BFF options in .NET 10: Duende.BFF, YARP, or hand-rolled"
date: 2026-07-14
depth: expedition
format: md
topic: "BFF options in .NET 10 — YARP, Duende BFF, and a minimal custom proxy. Licensing and revenue thresholds, YARP as a transform/token-injection host, a hand-rolled minimal-API + OIDC-cookie proxy, and what .NET 10 itself now ships that shrinks the gap. Maturity, lines of code you own, upgrade burden."
topic_raw: "BFF options in .NET 10 — YARP, Duende BFF, and a minimal custom proxy. Licensing and revenue thresholds, YARP as a transform/token-injection host, a hand-rolled minimal-API + OIDC-cookie proxy, and what .NET 10 itself now ships that shrinks the gap. Maturity, lines of code you own, upgrade burden."
tags: [dotnet, bff, oidc, yarp, duende, keycloak, security, aspnetcore]
summary: "If you build a BFF for the admin console, the realistic .NET 10 choice is YARP + AddOpenIdConnect + the free Apache-2.0 Duende.AccessTokenManagement (~250 LOC you own), or Duende.BFF if you qualify for its free Community Edition; Duende.BFF's paid entry point is $5,750/yr."
citations: 50
reading_time_min: 16
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 1253
issue: 6
---

> **Decision.** **Duende.BFF** is the only option that ships the whole pattern (login/logout/user endpoints, CSRF, token refresh, server-side sessions, back-channel logout) — but production use needs a licence, and the cheapest listed tier is **$5,750/yr** [[1]](https://duendesoftware.com/pricing), free only under the Community Edition (<$1M revenue, <$3M capital) [[2]](https://duendesoftware.com/products/communityedition).
> - **Pick Duende.BFF** if you qualify for Community Edition, or the licence is expensable. It is the reference implementation and works against **any** OIDC provider, Keycloak included [[3]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa).
> - **Pick YARP + `AddOpenIdConnect` + `Duende.AccessTokenManagement`** (Apache-2.0, free [[4]](https://github.com/DuendeSoftware/foss)) if the licence is a blocker. This is Microsoft's own BFF recipe [[5]](https://learn.microsoft.com/en-us/aspnet/core/blazor/security/blazor-web-app-with-oidc?view=aspnetcore-10.0) — ~250 lines of security-critical code you own and upgrade forever.
> - **Pick OidcProxy.Net** (⭐ 159, LGPL-3.0) if you want a config-only OSS BFF and accept a small bus factor [[6]](https://github.com/oidcproxydotnet/OidcProxy.Net).
> - **Pick `oauth2-proxy`** (⭐ 15k) if the console already lives behind a reverse proxy and a .NET BFF is a project you don't want [[7]](https://github.com/oauth2-proxy/oauth2-proxy).
> - **Never hand-roll token refresh.** Every serious write-up says the same thing: refresh races, rotation reuse-detection and multi-instance token stores are where custom BFFs break [[8]](https://nestenius.se/net/bff-in-asp-net-core-5-automatic-token-renewal/).
>
> ⚠ .NET 10 shrank the gap but did **not** close it: the cookie handler finally returns 401 instead of a login redirect for API endpoints [[9]](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints?view=aspnetcore-10.0), but built-in OAuth refresh-token support is *still* unshipped and now sits in **.NET 11 Planning** [[10]](https://github.com/dotnet/aspnetcore/issues/8175) ⭐ 38.3k.

## The comparison

| Option | Licence / cost | LOC you own | Keycloak | OpenIddict | Server-side sessions | Token refresh | CSRF built in | Back-channel logout | Maturity | Upgrade burden | Maintainer |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [**Duende.BFF**](https://duendesoftware.com/products/bff) v4 | Commercial; free Community Edition under thresholds; trial = 5 sessions/host [[11]](https://docs.duendesoftware.com/general/licensing/) | ~50 (config only) [[3]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa) | ✓ [[3]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa) | ✓ [[50]](https://docs.duendesoftware.com/bff/fundamentals/session/handlers/) | ✓ `AddServerSideSessions()` + EF store [[12]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/) | ✓ (bundled ATM) | ✓ `X-CSRF: 1` header [[13]](https://duendesoftware.com/blog/20250325-understanding-antiforgery-in-aspnetcore) | ✓ [[12]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/) | 4.7M NuGet downloads; repo ⭐ 1.6k [[14]](https://www.nuget.org/packages/Duende.BFF) [[15]](https://github.com/DuendeSoftware/products) | ⚠ High. v4 renamed interfaces + a breaking **DB schema** change [[16]](https://docs.duendesoftware.com/bff/upgrading/bff-v3-to-v4/); 4.2.0 dropped net8/net9 [[17]](https://api.nuget.org/v3/registration5-gz-semver2/duende.bff/index.json) | Duende Software |
| [**YARP**](https://dotnet.github.io/yarp/) + OIDC + ATM | MIT (YARP) + Apache-2.0 (ATM) → **$0** [[18]](https://github.com/dotnet/yarp) [[4]](https://github.com/DuendeSoftware/foss) | ~200–400 (see audit) | ✓ | ✓ | ✗ (write an `ITicketStore`) | ✓ via ATM [[19]](https://docs.duendesoftware.com/accesstokenmanagement/) | ✗ (write it) | ✗ (write it) [[20]](https://damienbod.com/2024/09/09/implement-openid-connect-back-channel-logout-using-asp-net-core-keycloak-and-net-aspire/) | ⭐ 9.6k, 68.7M downloads [[18]](https://github.com/dotnet/yarp) [[21]](https://www.nuget.org/packages/Yarp.ReverseProxy) | Low for the libs; **you** own the glue | Microsoft (.NET Foundation) |
| **Hand-rolled** (`IHttpForwarder` / `HttpClient`) | $0 | ~250–500 | ✓ | ✓ | ✗ | ⚠ you write it — don't | ✗ | ✗ | n/a | Yours, forever | You |
| [**OidcProxy.Net**](https://github.com/oidcproxydotnet/OidcProxy.Net) | LGPL-3.0 [[6]](https://github.com/oidcproxydotnet/OidcProxy.Net) | ~20 (config) | ✓ | ✓ | ✓ (Redis) | ✓ | ✓ | partial | ⭐ 159 — small | Unknown; low bus factor | Community |
| [**oauth2-proxy**](https://oauth2-proxy.github.io/oauth2-proxy/) sidecar | MIT [[7]](https://github.com/oauth2-proxy/oauth2-proxy) | 0 (YAML) | ✓ | ✓ (generic OIDC) | ✓ Redis session store [[22]](https://oauth2-proxy.github.io/oauth2-proxy/configuration/overview) | ✓ `cookie-refresh` [[22]](https://oauth2-proxy.github.io/oauth2-proxy/configuration/overview) | ⚠ own CSRF cookie, not a BFF header | ✗ | ⭐ 15k, v7.15.3 (Jun 2026) [[7]](https://github.com/oauth2-proxy/oauth2-proxy) | Low (container tag) | oauth2-proxy org |

Stars: [dotnet/yarp](https://github.com/dotnet/yarp) ⭐ 9.6k · [DuendeSoftware/products](https://github.com/DuendeSoftware/products) ⭐ 1.6k · [oauth2-proxy](https://github.com/oauth2-proxy/oauth2-proxy) ⭐ 15k · [OidcProxy.Net](https://github.com/oidcproxydotnet/OidcProxy.Net) ⭐ 159 (Jul 2026).

## 1. Duende.BFF v4 — the reference implementation

**What the package actually gives you.** A management endpoint surface under `/bff` (`ManagementBasePath`, default `/bff`) — `/bff/login`, `/bff/logout`, `/bff/user` [[23]](https://docs.duendesoftware.com/bff/architecture/); anti-forgery enforced on API routes by requiring an `X-CSRF: 1` header (the header forces a CORS preflight for cross-origin callers, which is what actually blocks CSRF) [[13]](https://duendesoftware.com/blog/20250325-understanding-antiforgery-in-aspnetcore); remote-API proxying via `MapRemoteBffApiEndpoint("/api/users", new Uri("https://remote/users")).WithAccessToken(RequiredTokenType.User)` [[24]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/); optional server-side sessions with an EF store, which both shrinks the cookie to a session id and makes back-channel logout revocation possible [[12]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/). Tokens never reach the browser [[23]](https://docs.duendesoftware.com/bff/architecture/).

Note what the proxy *is*: **Duende.BFF's forwarder is YARP** — "It uses Microsoft YARP internally, but is much simpler to configure than YARP", shipped as the `Duende.BFF.Yarp` package [[24]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/). You are not choosing *between* Duende and YARP; you are choosing whether to buy the auth layer that sits on top of YARP.

**v4 (Dec 2, 2025)** added multi-frontend hosting (one BFF host serving several SPAs), OpenTelemetry, and auto-wiring of the middleware/endpoints [[25]](https://duendesoftware.com/blog/20251202-duende-bffv4-now-available-multi-frontend-opentelemetry-and-simplified-security). Current is **4.2.0 (2026-06-10)** [[14]](https://www.nuget.org/packages/Duende.BFF).

**Does it need Duende IdentityServer? No.** BFF drives the stock ASP.NET Core OIDC handler, which "can be configured to use **any OpenID Connect provider**" [[50]](https://docs.duendesoftware.com/bff/fundamentals/session/handlers/). The Wrapt walkthrough runs a standalone Duende BFF for a React SPA against **Keycloak in Docker**, ~50 lines in `Program.cs` (`AddBff().AddRemoteApis()`, cookie `__Host-` prefix + `SameSite=Strict`, `AddOpenIdConnect` pointed at the Keycloak realm, one `MapRemoteBffApiEndpoint`) [[3]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa). OpenIddict is just another OIDC server to it.

### Licensing — the numbers, from the source

- **Production use requires a licence.** "Duende products, except for our open source tools, require a license for production use." BFF is licensed as its own product, in two editions (Starter, Enterprise) [[11]](https://docs.duendesoftware.com/general/licensing/).
- **Trial mode is not a free tier.** BFF v4 without a key logs an error at startup and is "limited to a maximum of five (5) sessions per host"; excess sessions log an error per session. The limit is "not technically enforced" and not shared across nodes — it degrades to log noise, not an outage [[11]](https://docs.duendesoftware.com/general/licensing/).
- **Price.** The 2026 pricing page lists **Lite $5,750**, **Standard $12,500**, **Advanced $24,900** per year (billed annually), each bundling a BFF front-end quota (2 / 10 / 30 "BFF Front-Ends"); add-ons priced separately (SAML $1,500, Automatic Key Management $4,000, FAPI conformance $7,500). No EUR list price is published [[1]](https://duendesoftware.com/pricing).
- **Free path: Community Edition.** Eligibility is revenue-based and explicit: "For-profit organizations with less than **$1M USD projected annual gross revenue** and access to less than **$3M USD in capital facilities**, or non-profit organizations and registered charities with a published annual budget under $1M USD" [[2]](https://duendesoftware.com/products/communityedition). The BFF licensing docs point small orgs at the same Community Edition [[11]](https://docs.duendesoftware.com/general/licensing/).
- **"It's only an internal tool" does not make it free.** Nothing in the terms exempts internal/non-customer-facing production use — the gate is org revenue, not app audience. Community Edition also explicitly excludes redistribution and building identity infra for an end customer [[2]](https://duendesoftware.com/products/communityedition). ⚠ For a consultancy: if the console runs in *your* infra for *your* staff, you're judged on your own revenue; if it ships to a client, that client needs the licence.
- Licence validation is fully local — "no outbound network calls related to license validation" — and the same key may be used in dev/test/QA ("We do not consider the key a secret") [[11]](https://docs.duendesoftware.com/general/licensing/) [[26]](https://github.com/orgs/DuendeSoftware/discussions/557).

### Upgrade burden

⚠ The v3→v4 hop is real work: `TokenType` → `RequiredTokenType` (new namespace), `RequireAccessToken()` → `WithAccessToken()`, `IUserService` → `IUserEndpoint`, default implementations went from virtual to internal, and a **breaking database schema change** — `UserSessions.ApplicationName` renamed to `PartitionKey`, requiring all BFF instances sharing that table to move together [[16]](https://docs.duendesoftware.com/bff/upgrading/bff-v3-to-v4/). Duende also tracks the .NET train aggressively: 4.1.2 (Mar 2026) targeted net8/net9/net10; **4.2.0 (Jun 2026) targets net10.0 only** [[17]](https://api.nuget.org/v3/registration5-gz-semver2/duende.bff/index.json). On .NET 10 that's a non-issue — but it tells you the support window is short.

## 2. YARP — a proxy, not an auth solution

YARP is [`Yarp.ReverseProxy`](https://www.nuget.org/packages/Yarp.ReverseProxy) ⭐ 9.6k, MIT, 68.7M downloads, latest **2.3.0 (Feb 2025)** — no 2.4/3.0 as of Jul 2026 [[18]](https://github.com/dotnet/yarp) [[21]](https://www.nuget.org/packages/Yarp.ReverseProxy). Stable, not stagnant: in .NET 10 its docs moved into the ASP.NET Core doc set under `fundamentals/servers/yarp` [[27]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/authn-authz?view=aspnetcore-10.0).

**What it does not do:** "No authentication or authorization is performed on requests unless enabled in the route or application configuration." YARP consumes ASP.NET Core's auth primitives — you configure `AddAuthentication`/`AddOpenIdConnect`, YARP just lets you attach an `AuthorizationPolicy` per route. On flowing identity onward, the docs are blunt: OIDC "authentication process can be configured in the proxy application and will result in an authentication cookie. That cookie will flow to the destination server as a normal request header" — i.e. by default your API gets the *cookie*, not a bearer token, and swapping credential types "can be performed using custom request transforms" [[27]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/authn-authz?view=aspnetcore-10.0).

**Token injection is a transform.** `AddTransforms(ctx => ctx.AddRequestTransform(async t => { … }))` [[28]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/transforms?view=aspnetcore-10.0). Microsoft's own .NET 10 BFF sample does exactly this:

```csharp
app.MapForwarder("/weather-forecast", "https://weatherapi", transformBuilder =>
{
    transformBuilder.AddRequestTransform(async transformContext =>
    {
        var accessToken = await transformContext.HttpContext.GetTokenAsync("access_token");
        transformContext.ProxyRequest.Headers.Authorization = new("Bearer", accessToken);
    });
}).RequireAuthorization();
```
— `BlazorWebAppOidcBffAutoYarpAspire/BlazorWebAppOidc/Program.cs` [[29]](https://github.com/dotnet/blazor-samples/blob/main/10.0/BlazorWebAppOidcBffAutoYarpAspire/BlazorWebAppOidc/Program.cs) ⭐ 1.1k.

**Is there an official YARP-as-BFF sample? Yes** — `BlazorWebAppOidcBffAutoYarpAspire` in [dotnet/blazor-samples](https://github.com/dotnet/blazor-samples) ⭐ 1.1k (Jul 2026), documented on Learn as "OIDC with the Backend for Frontend (BFF) pattern with YARP and Aspire" [[5]](https://learn.microsoft.com/en-us/aspnet/core/blazor/security/blazor-web-app-with-oidc?view=aspnetcore-10.0). It is Blazor-shaped, but the BFF half (cookie + OIDC + `MapForwarder` + transform + `MapLoginAndLogout`) is framework-agnostic and transplants onto a React SPA unchanged.

**The credible free stack** is YARP for proxying + `Microsoft.AspNetCore.Authentication.OpenIdConnect` for the protocol + **`Duende.AccessTokenManagement.OpenIdConnect`** for the refresh cycle — the last is **Apache-2.0, free, no licence key**, 4.2.0 (Mar 2026), net8/9/10 [[4]](https://github.com/DuendeSoftware/foss) [[19]](https://docs.duendesoftware.com/accesstokenmanagement/) [[30]](https://api.nuget.org/v3/registration5-gz-semver2/duende.accesstokenmanagement.openidconnect/index.json). This is precisely what Tim Deschryver's YARP-BFF series lands on: hand-write `/bff/login` (challenge), `/bff/logout` (sign-out both schemes) and `/bff/user` (claims), then a `RequestTransform` calling `GetUserAccessTokenAsync()`, "because manually retrieving the token doesn't automatically handle token expiration and most importantly the refresh cycle" [[31]](https://timdeschryver.dev/blog/secure-your-yarp-bff-with-cookie-based-authentication) [[32]](https://timdeschryver.dev/blog/forwarding-authenticated-calls-to-a-downstream-api-using-yarp). Also remember `RequestHeaderRemoveTransform("Cookie")` — strip the session cookie before forwarding [[32]](https://timdeschryver.dev/blog/forwarding-authenticated-calls-to-a-downstream-api-using-yarp). With Aspire, `AddServiceDiscoveryDestinationResolver()` removes hard-coded destination URLs [[33]](https://timdeschryver.dev/blog/integrating-yarp-within-dotnet-aspire).

## 3. Minimal custom — how many lines do you actually own?

You don't even need full YARP routing: `IHttpForwarder`/`MapForwarder` is YARP's low-level direct-forwarding API — "these applications do not need … configuration discovery, routing, load balancing" — one `app.MapForwarder("/{**catch-all}", …)` plus a `HttpMessageInvoker` and you have a proxy [[34]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/direct-forwarding?view=aspnetcore-10.0). And if the SPA is served from the BFF's own `wwwroot` (damienbod's samples do this; YARP is used only in dev to front the Vite server), the whole thing is same-origin and the "proxy" is a thin `/api` passthrough [[35]](https://github.com/damienbod/bff-aspnetcore-oidc-vuejs) ⭐ 24.

**LOC audit — counted from Microsoft's own .NET 10 BFF sample:**

| File you'd own | LOC | What it does |
|---|---|---|
| `CookieOidcRefresher.cs` | 102 | refresh-token exchange at `OnValidatePrincipal`, re-validate the id_token, re-issue the cookie [[36]](https://github.com/dotnet/blazor-samples/blob/main/10.0/BlazorWebAppOidcBffAutoYarpAspire/BlazorWebAppOidc/CookieOidcRefresher.cs) |
| `CookieOidcServiceCollectionExtensions.cs` | 26 | wires the refresher, sets `SaveTokens`, adds `offline_access` |
| `LoginLogoutEndpointRouteBuilderExtensions.cs` | 46 | `/login` challenge + `/logout` sign-out |
| auth wiring inside `Program.cs` | ~40 | `AddOpenIdConnect` + `AddCookie` + `MapForwarder` + transform [[29]](https://github.com/dotnet/blazor-samples/blob/main/10.0/BlazorWebAppOidcBffAutoYarpAspire/BlazorWebAppOidc/Program.cs) |
| **Microsoft's baseline** | **~215** | and this is the *happy path* |
| + `/bff/user` endpoint, `X-CSRF` enforcement middleware | ~35 (est.) | Duende gives these free [[13]](https://duendesoftware.com/blog/20250325-understanding-antiforgery-in-aspnetcore) |
| + `ITicketStore` (server-side sessions, distributed cache) | ~80 (est.) | needed once cookies get fat [[37]](https://duendesoftware.com/blog/20260429-aspnet-core-cookie-size-limits) |
| + back-channel logout endpoint + revocation | ~60–100 (est.) | ASP.NET Core has **none** built in [[20]](https://damienbod.com/2024/09/09/implement-openid-connect-back-channel-logout-using-asp-net-core-keycloak-and-net-aspire/) |
| **Realistic total** | **~250–450** | security-critical, yours forever |

The 215-line baseline is not a strawman: `CookieOidcRefresher.cs` carries a comment pointing straight at [dotnet/aspnetcore#8175](https://github.com/dotnet/aspnetcore/issues/8175) ⭐ 38.3k — the still-open request for built-in refresh support. Microsoft ships it as *sample code you copy*, not as a package [[36]](https://github.com/dotnet/blazor-samples/blob/main/10.0/BlazorWebAppOidcBffAutoYarpAspire/BlazorWebAppOidc/CookieOidcRefresher.cs).

### What's easy to get wrong

| Pitfall | Why it bites | Evidence |
|---|---|---|
| **Refresh races** | Concurrent requests each hit the token endpoint with the same refresh token. With rotation + reuse detection (Keycloak's default posture) that can nuke the session. Microsoft's 102-line refresher has **no locking or single-flight** [[36]](https://github.com/dotnet/blazor-samples/blob/main/10.0/BlazorWebAppOidcBffAutoYarpAspire/BlazorWebAppOidc/CookieOidcRefresher.cs) | "Race conditions when multiple requests need renewal simultaneously… Token storage conflicts in multi-instance deployments… Real-world incidents have occurred where custom implementations accidentally exposed tokens to wrong users" [[8]](https://nestenius.se/net/bff-in-asp-net-core-5-automatic-token-renewal/) |
| **`SaveTokens = true` blows up the cookie** | Cookie limit ~4 KB, header limit ~8 KB; base64 JWTs + Keycloak group/role claims overflow it → HTTP 431, silent truncation, intermittent logout, WAF drops. `ChunkingCookieManager` splits at 3500 bytes but is "tactical only" | [[37]](https://duendesoftware.com/blog/20260429-aspnet-core-cookie-size-limits) |
| **The real fix is a session store** | `ITicketStore` / server-side sessions — cookie becomes an opaque key. Duende does this with one call; you write it | [[37]](https://duendesoftware.com/blog/20260429-aspnet-core-cookie-size-limits) [[12]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/) |
| **CSRF** | Cookie auth means the browser attaches credentials automatically. You need `SameSite`, `__Host-` prefix **and** a required custom header; Deschryver's otherwise-solid walkthrough simply doesn't cover antiforgery | [[13]](https://duendesoftware.com/blog/20250325-understanding-antiforgery-in-aspnetcore) [[31]](https://timdeschryver.dev/blog/secure-your-yarp-bff-with-cookie-based-authentication) |
| **Back-channel logout** | No built-in support. You implement the webhook, validate the logout token, persist to a distributed cache, and check it on every request via a cookie event handler | [[20]](https://damienbod.com/2024/09/09/implement-openid-connect-back-channel-logout-using-asp-net-core-keycloak-and-net-aspire/) |
| **401 vs 302 on proxied calls** | Historically the killer: an expired cookie turned an XHR into a 302 to Keycloak. **Fixed in .NET 10** (see below) | [[9]](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints?view=aspnetcore-10.0) |
| **Forwarding the cookie downstream** | Strip it — the API should see only `Authorization: Bearer` | [[32]](https://timdeschryver.dev/blog/forwarding-authenticated-calls-to-a-downstream-api-using-yarp) |

Nestenius's series ends by migrating the from-scratch BFF to Duende and reports the collapse: the whole custom `BffController` becomes `app.MapBffManagementEndpoints();`, the proxying becomes one line, and the custom CSRF middleware (`app.CheckForCsrfHeader()`) disappears entirely [[38]](https://nestenius.se/net/bff-in-asp-net-core-7-introducing-the-duende-bff-library/). That is the honest LOC-vs-cost exchange rate: **~250–450 lines ↔ $5,750/yr** (or $0 if Community Edition applies).

⚠ Don't use [ardalis/BFF](https://github.com/ardalis/BFF) ⭐ 6 — it's a stale fork of the archived Duende BFF repo, not a maintained alternative [[39]](https://github.com/ardalis/BFF).

## 4. What .NET 10 itself now ships

| Change | Shrinks the BFF gap? | Status |
|---|---|---|
| Cookie handler returns **401/403 instead of redirecting** for endpoints carrying the new `IApiEndpointMetadata` (auto-added to `[ApiController]`, JSON minimal APIs, `TypedResults`, SignalR). Opt out with `[AllowCookieRedirect]` or an `AppContext` switch | ✓✓ Removes the single most annoying hand-rolled-BFF hack (custom `OnRedirectToLogin` to force 401) | Shipped, **breaking** [[9]](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints?view=aspnetcore-10.0) [[40]](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0?view=aspnetcore-10.0) |
| Official **BFF-with-YARP + Aspire sample** (`BlazorWebAppOidcBffAutoYarpAspire`), plus a `MinimalApiJwt` downstream API and `Microsoft.Extensions.ServiceDiscovery.Yarp` for destination resolution | ✓ Gives you a Microsoft-blessed skeleton to copy | Shipped (docs/sample, not a package) [[5]](https://learn.microsoft.com/en-us/aspnet/core/blazor/security/blazor-web-app-with-oidc?view=aspnetcore-10.0) [[29]](https://github.com/dotnet/blazor-samples/blob/main/10.0/BlazorWebAppOidcBffAutoYarpAspire/BlazorWebAppOidc/Program.cs) |
| Auth/authz **metrics** (`aspnetcore.authentication.authenticate.duration`, sign-in/out counters) | ~ Ops nicety | Shipped [[40]](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0?view=aspnetcore-10.0) |
| **Passkeys / WebAuthn** in ASP.NET Core Identity | ✗ Irrelevant if Keycloak/OpenIddict is the IdP | Shipped [[40]](https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0?view=aspnetcore-10.0) [[41]](https://auth0.com/blog/authentication-authorization-enhancements-dotnet-10/) |
| **PAR** (RFC 9126) used automatically when the IdP advertises it (`PushedAuthorizationBehavior.UseIfAvailable`, since .NET 9) | ✓ Free hardening for the BFF's OIDC leg; Keycloak supports PAR (Entra does not) | Shipped in .NET 9, default in .NET 10 samples [[29]](https://github.com/dotnet/blazor-samples/blob/main/10.0/BlazorWebAppOidcBffAutoYarpAspire/BlazorWebAppOidc/Program.cs) |
| **OAuth 2 refresh-token support** (#8175, open since 2019) | ✗✗ The core gap. Was on the .NET 10 aspirational list; still open, now milestoned **.NET 11 Planning** | **Not shipped** [[10]](https://github.com/dotnet/aspnetcore/issues/8175) [[42]](https://github.com/dotnet/aspnetcore/issues/59443) |
| **DPoP** (#58016) — "The current option in .NET is to either use Duende libraries, or write your own" | ✗ | **Not shipped**, .NET 11 Planning [[43]](https://github.com/dotnet/aspnetcore/issues/58016) |
| A first-party **BFF package or `dotnet new bff` template** | ✗ | Does not exist. No BFF item appears anywhere in the .NET 10 auth roadmap [[42]](https://github.com/dotnet/aspnetcore/issues/59443); the "token handler pattern" remains third-party (Duende, OidcProxy.Net) [[6]](https://github.com/oidcproxydotnet/OidcProxy.Net) |
| Back-channel logout, `ITicketStore` implementation, antiforgery-for-BFF | ✗ | Still yours to write [[20]](https://damienbod.com/2024/09/09/implement-openid-connect-back-channel-logout-using-asp-net-core-keycloak-and-net-aspire/) |

**Read:** .NET 10 makes the hand-rolled BFF *pleasanter* (401s, an official sample, better metrics), not *smaller*. The two things that would actually shrink the code you own — refresh-token management and DPoP — both slipped to .NET 11 planning. Until then, "free token management" means `Duende.AccessTokenManagement` (Apache-2.0), which is a Duende library either way — you're just not paying for it [[4]](https://github.com/DuendeSoftware/foss).

## 5. The option the .NET framing misses: a sidecar OIDC proxy

If the console already sits behind an ingress, the BFF can be a container instead of a codebase.

| Tool | Stars / licence | Fit as a BFF |
|---|---|---|
| [**oauth2-proxy**](https://oauth2-proxy.github.io/oauth2-proxy/) | ⭐ 15k, MIT, v7.15.3 (Jun 2026) [[7]](https://github.com/oauth2-proxy/oauth2-proxy) | Closest thing to a drop-in BFF. Generic OIDC (Keycloak listed), Redis session store, `cookie-refresh`. ⚠ Token flow is header-shaped, not BFF-shaped: `pass-access-token` → `X-Forwarded-Access-Token`; `pass-authorization-header` sends the **ID token** as Bearer; `set-authorization-header` only helps in nginx `auth_request` mode. Your .NET API must be told which header to trust [[22]](https://oauth2-proxy.github.io/oauth2-proxy/configuration/overview) |
| [**Pomerium**](https://www.pomerium.com/) | ⭐ 4.9k, Apache-2.0, v0.32.9 (Jun 2026) [[44]](https://github.com/pomerium/pomerium) | Identity-aware proxy / zero-trust gateway. Heavier: policy engine, its own control plane. Overkill for one admin console |
| [**traefik-forward-auth**](https://github.com/thomseddon/traefik-forward-auth) | ⭐ 2.4k, MIT, v2.3.0 [[45]](https://github.com/thomseddon/traefik-forward-auth) | Gate-only. Authenticates the user, forwards identity headers — does **not** mint/refresh access tokens for a downstream API |
| Traefik `ForwardAuth` / nginx `auth_request` | built into the proxy | Primitives, not solutions: ForwardAuth "delegates authentication to an external service" [[46]](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/forwardauth/); nginx auth_request "implements client authorization based on the result of a subrequest" [[47]](https://nginx.org/en/docs/http/ngx_http_auth_request_module.html). Traefik's *own* OIDC middleware is a commercial Hub/Enterprise feature |
| Keycloak Gatekeeper / **louketo-proxy** | ⭐ 948 — **archived Dec 2020, EOL** [[48]](https://github.com/keycloak/keycloak-gatekeeper) | Dead. Community successor: [gogatekeeper](https://github.com/gogatekeeper/gatekeeper) ⭐ 318, Apache-2.0, v4.10.0 (Jun 2026) [[49]](https://github.com/gogatekeeper/gatekeeper) — alive but tiny |

**When the sidecar wins:** you already run the reverse proxy, you want zero .NET security code, and the admin console's APIs can accept a header you configure. **When it loses:** the sidecar gives you a *gate*, not a BFF — no `/bff/user` shape, CSRF is its own scheme, back-channel logout is absent, and the token it forwards may be the ID token, not a scoped access token. For an internal admin console fronting your *own* .NET APIs, the impedance mismatch usually costs more than the ~250 lines it saves.

## Verdict for `itenium-ui`

Greenfield, internal, Keycloak-or-OpenIddict, one frontend:

1. **Check Community Edition eligibility first** — it is a two-line revenue test [[2]](https://duendesoftware.com/products/communityedition), and if it passes, Duende.BFF is free, complete, and supported, and the answer is trivially Duende.
2. **If not eligible:** YARP + `AddOpenIdConnect` + `Duende.AccessTokenManagement`, copied from Microsoft's `BlazorWebAppOidcBffAutoYarpAspire` sample [[5]](https://learn.microsoft.com/en-us/aspnet/core/blazor/security/blazor-web-app-with-oidc?view=aspnetcore-10.0). Budget ~250–450 LOC, and put server-side sessions (`ITicketStore`) in from day one rather than after the first HTTP 431 [[37]](https://duendesoftware.com/blog/20260429-aspnet-core-cookie-size-limits).
3. **Serve the SPA from the BFF's own origin** (wwwroot in prod, dev-proxy in dev) — it makes SameSite/CSRF tractable and removes most of the proxy [[35]](https://github.com/damienbod/bff-aspnetcore-oidc-vuejs).
4. **$5,750/yr buys ~350 lines of security code you never write, a DB-backed session store, back-channel logout, and someone to call.** For a *single* internal console that's expensive; the same licence covers 2 front-ends and the org's other apps, so evaluate it at portfolio level, not per app [[1]](https://duendesoftware.com/pricing).
