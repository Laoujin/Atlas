---
layout: expedition
title: "Pure React 19 SPA or a .NET 10 BFF? A decision framework for an internal admin console"
date: 2026-07-14
topic: "Decision framework: pure React 19 SPA vs a .NET 10 backend-for-frontend for Itenium.Forge's itenium-ui admin console (2026). React 19 + Vite SPA consuming .NET 10 REST APIs, JWT via Keycloak/OpenIddict, TanStack Query for server state. Compare in-memory tokens vs cookie-based BFF sessions under XSS; refresh-token handling and silent renew; the cost of adding a BFF now while greenfield vs retrofitting later; impact on OpenAPI client codegen and local dev ergonomics; what BFF options exist in .NET 10 (YARP, Duende BFF, minimal custom)."
format: md
tags: [architecture, bff, dotnet, react, oauth, security]
summary: "Ship the SPA, not the BFF — but build it so the BFF is a 2–5 day retrofit, because the IETF names business apps explicitly and the supply-chain argument is the one that survives scrutiny."
cover: cover.svg
citations: 166
reading_time_min: 65
synthesis: true
children:
  - slug: in-memory-tokens-vs-cookie-backed-bff-sessions-under-xss
    title: "In-memory tokens vs cookie-backed BFF sessions under XSS: what each architecture actually buys you"
    depth: survey
    status: success
    summary: "httpOnly cookies do not stop XSS — they convert silent token exfiltration into loud, tab-bound session riding. That's a real but bounded win; CSP + Trusted Types is the actual mitigation."
    citations: 17
    reading_time_min: 8
  - slug: does-the-ietf-browser-based-apps-bcp-apply-to-an-internal-admin-console
    title: "Does the IETF browser-based-apps BCP apply to an internal admin console?"
    depth: recon
    status: success
    summary: "The BCP names \"business applications\" in its strongest recommendation, so an internal console is in scope — but the ranking is a security/simplicity trade-off, not a normative MUST."
    citations: 8
    reading_time_min: 4
  - slug: refresh-tokens-and-silent-renew-in-a-browser-spa-2026
    title: "Refresh tokens and silent renew in a browser SPA (2026)"
    depth: survey
    status: success
    summary: "Iframe silent renew is dead cross-site but alive same-site; refresh-token rotation works on both stacks, DPoP only really works on Keycloak, and TanStack Query needs a single-flight mutex either way."
    citations: 39
    reading_time_min: 12
  - slug: greenfield-bff-cost-vs-retrofitting-one-later
    title: "Greenfield BFF vs retrofitting later: where the asymmetry actually is"
    depth: survey
    status: success
    summary: "Adding a BFF later is a two-way door — if you build the SPA with one auth module, one fetch wrapper, relative paths and no client-side JWT parsing. The one-way door is the API, not the frontend."
    citations: 25
    reading_time_min: 9
  - slug: impact-on-openapi-client-codegen-and-local-dev-ergonomics
    title: "What a BFF costs you every day: OpenAPI codegen and the local dev loop"
    depth: survey
    status: success
    summary: "A path-preserving BFF leaves OpenAPI codegen essentially untouched — the real daily cost is one extra process, a Vite proxy config, and losing Swagger UI 'Try it out'."
    citations: 27
    reading_time_min: 13
  - slug: bff-options-in-net-10-yarp-duende-bff-minimal-custom
    title: "BFF options in .NET 10: Duende.BFF, YARP, or hand-rolled"
    depth: expedition
    status: success
    summary: "If you build a BFF, the realistic .NET 10 choice is YARP + AddOpenIdConnect + the free Apache-2.0 Duende.AccessTokenManagement (~250 LOC you own), or Duende.BFF if you qualify for its free Community Edition; Duende.BFF's paid entry point is $5,750/yr."
    citations: 50
    reading_time_min: 16
model: "Opus 4.8"
cost_usd: "sub"
issue: 6
duration_sec: 1400
---

> **Decision.** Build the SPA now. Do **not** build the BFF yet — but build the SPA so that adding one is a 2–5 day change, and treat that discipline as non-negotiable rather than aspirational. The retrofit is a two-way door precisely because the API never changes: a BFF forwards a bearer token to it, so `AddJwtBearer` stays exactly as it is [[1]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/)[[2]](https://curity.io/blog/token-handler-the-single-page-applications-new-bff/).

## The two arguments that actually decide this

**The "it's internal, the BCP isn't about us" defence fails.** The draft's strongest sentence names the case to its face: the BFF architecture is *"strongly recommended for business applications, sensitive applications, and applications that handle personal data"* [[3]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-27). Its threat model assumes only that attacker code runs in your origin — nothing about public users or consumer scale. But the same document prices its own advice honestly, presenting the patterns as *"a different trade-off between security and simplicity"* in decreasing order of security [[4]](https://www.ietf.org/archive/id/draft-ietf-oauth-browser-based-apps-27.html), and attaches no RFC 2119 keyword. It is at revision -27, IESG-approved, in the RFC Editor queue. So: a strong prior, not a mandate.

**The security win is real but bounded, and smaller than the marketing.** A BFF does not stop XSS; it converts *silent, off-origin, outlives-the-tab token exfiltration* into *loud, tab-bound session riding* through your own logs, where you can see it and kill the session [[5]](https://fusionauth.io/blog/backend-for-frontend-security-architecture). For an admin console that distinction matters less than elsewhere — if the payload can grant itself a role in the first 400 ms, the tab-lifetime bound bought you nothing. Auth0's framing is the honest one: *"BFF shifts the security boundary. It doesn't eliminate it"* [[6]](https://auth0.com/blog/things-developers-get-wrong-about-the-backend-for-frontend-pattern/).

Which leaves **supply chain as the one pro-BFF argument that survives all six angles**. Strict CSP plus Trusted Types — now Baseline, with Firefox shipping in Feb 2026 [[7]](https://www.uriports.com/blog/csp-trusted-types/) — genuinely closes injected-script XSS, and allowlist CSP without them is near-worthless (Google measured 94.68% of script-limiting policies as ineffective) [[8]](https://research.google/pubs/csp-is-dead-long-live-csp-on-the-insecurity-of-whitelists-and-the-future-of-content-security-policy/). But CSP cannot distinguish your trojaned npm dependency from your own code: the nonced bundle executes with full privilege. Against a September-2025-style compromise, "there is no token in the browser to steal" is doing work that no CSP can do [[5]](https://fusionauth.io/blog/backend-for-frontend-security-architecture).

## What the angles say to each other

A **DNS choice, not a security choice, moves the needle most.** Iframe silent renew is not dead — it is dead *cross-site*. `auth.itenium.be` and `admin.itenium.be` are different origins but the **same site**, so the IdP cookie is first-party and `prompt=none` still works in 2026 [[9]](https://docs.oidc-spa.dev/resources/third-party-cookies-and-session-restoration)[[10]](https://web.dev/articles/same-site-same-origin). Put Keycloak on a subdomain of the app's registrable domain and the pure-SPA path stays cheap; put it on a foreign host and the SPA's renewal story degrades into full-page redirects, which is where the BFF starts winning on ergonomics rather than on security.

**The costs are not where people expect.** Codegen is a non-issue: a path-preserving proxy leaves the OpenAPI document and the generated client untouched — only `baseUrl` and `credentials: 'include'` change. Only a *composing* BFF turns codegen into a project, and Duende's default `MapRemoteBffApiEndpoint` shape is what quietly creates that problem [[11]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui). The genuine operational tax is the session store and a shared Data Protection key ring once you run more than one replica [[12]](https://docs.duendesoftware.com/bff/fundamentals/session/server-side-sessions/) — and you pay that whenever you adopt, so it is not an asymmetry at all. Which means the honest cost comparison is *not* "BFF now vs BFF later"; it is "BFF ever vs never".

**The one unbounded retrofit is real-time.** SignalR and WebSockets through a BFF are the single genuinely painful item: a WebSocket handshake cannot set the anti-forgery header the BFF requires, and teams report falling back to long-polling [[13]](https://github.com/DuendeArchive/Support/issues/972). If `itenium-ui` will carry live updates, decide before you build — that is the one place where "later" is expensive.

## If and when you build it

Duende.BFF is the reference implementation, works against any OIDC provider including Keycloak, and is ~50 lines of config — but production use needs a licence, listed at **$5,750/yr** for Lite, free only under the Community Edition's *<$1M revenue* threshold; "it's just an internal tool" does **not** qualify you, because the gate is org revenue, not app audience [[14]](https://duendesoftware.com/pricing)[[15]](https://duendesoftware.com/products/communityedition). The free path is **YARP + `AddOpenIdConnect` + `Duende.AccessTokenManagement`** (Apache-2.0) — which is Microsoft's own documented recipe, at the price of ~250 lines of security-critical code you own forever [[16]](https://github.com/DuendeSoftware/foss). Note that you are not choosing *between* Duende and YARP: Duende.BFF's forwarder **is** YARP. You are choosing whether to buy the auth layer on top of it. .NET 10 narrowed the gap — the cookie handler now returns 401 instead of a login redirect for API endpoints [[17]](https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints?view=aspnetcore-10.0) — but first-party OAuth refresh-token support is *still* unshipped and has slipped to .NET 11 planning [[18]](https://github.com/dotnet/aspnetcore/issues/8175).

## What would change the call

Revisit the moment any of these become true: the console needs real-time; it starts handling customer PII or becomes reachable from outside the corporate perimeter; a second client (mobile, native, a partner integration) appears and wants bearer tokens anyway; or a supply-chain incident lands close enough to make "nothing in the browser to steal" worth $5,750 a year. Absent those, the marginal security a BFF buys an internal console is the *tail* of the risk — offline replay and refresh-token abuse — not the body of it, and the body is what a hardened CSP and Trusted Types actually address.

The sharpest open question is not whether the BFF is worth it, but whether the discipline it depends on will hold: the entire 2–5 day retrofit estimate rests on nobody ever calling `jwtDecode()` in a component or reaching for `getAccessToken()` from app state. Every team that missed that estimate missed it there.
