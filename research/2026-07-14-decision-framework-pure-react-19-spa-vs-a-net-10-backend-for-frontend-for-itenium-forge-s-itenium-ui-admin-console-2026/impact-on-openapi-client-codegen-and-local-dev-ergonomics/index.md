---
title: "What a BFF costs you every day: OpenAPI codegen and the local dev loop"
date: 2026-07-14
depth: survey
format: md
topic: "Impact of a BFF on OpenAPI client codegen and local dev ergonomics — does a proxying BFF break or complicate generated clients (NSwag / Kiota / openapi-typescript / orval / Hey API)? Vite dev proxy vs cookie domains, the F5 loop, hot reload, and how many processes a developer must run."
topic_raw: "Impact of a BFF on OpenAPI client codegen and local dev ergonomics — does a proxying BFF break or complicate generated clients (NSwag / Kiota / openapi-typescript / orval / Hey API)? Vite dev proxy vs cookie domains, the F5 loop, hot reload, and how many processes a developer must run."
tags: [bff, openapi, codegen, vite, dotnet, aspire, developer-experience]
summary: "A path-preserving BFF leaves OpenAPI codegen essentially untouched — the real daily cost is one extra process, a Vite proxy config, and losing Swagger UI 'Try it out'."
citations: 27
reading_time_min: 13
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 521
issue: 6
---

> **Decision.** A transparent, path-preserving BFF costs the generated client **two config lines** (`baseUrl` + `credentials: 'include'`) and the OpenAPI document is unchanged [[15]](https://openapi-ts.dev/openapi-fetch/api). The daily cost is not codegen — it's **one extra process, a four-route Vite proxy, and the loss of Swagger UI's "Try it out"** for cookie-authenticated endpoints [[11]](https://swagger.io/docs/specification/v3_0/authentication/cookie-authentication/). If the BFF starts *composing* per-screen DTOs instead of proxying, you inherit a second OpenAPI document and a merge problem — that is where it gets genuinely expensive [[2]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui).

---

## 1. Does a BFF affect OpenAPI codegen? Mostly no — until it does

Three cases, in ascending order of pain.

| BFF shape | OpenAPI doc | Generated client | Verdict |
|---|---|---|---|
| **Transparent proxy, path-preserving** (`/api/*` → API `/api/*`) | Unchanged — it's still the API's own document | Unchanged. Only `baseUrl` (now relative) and `credentials: 'include'` change | ✓ free |
| **Proxy with a prefix change** (`/api/users` → `https://api/users`) | Unchanged, but `paths` no longer match the URL the browser calls | Fix with the generator's `baseUrl` prefix — *if* the prefix is uniform | ⚠ one config line, breaks if prefixes are inconsistent |
| **Composing BFF** (aggregation, per-screen DTOs) | **Two** documents, or a merged one you must build | Two generated clients, or a document-merge step in CI | ✗ real cost |

The middle case is the one people trip over, and it is Duende BFF's *default* shape: `MapRemoteBffApiEndpoint("/api/users", new Uri("https://remoteHost/users"))` maps a local BFF path onto a *different* remote path, and forwards all sub-paths beneath it [[3]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/). The downstream API's OpenAPI document says `/users`; the browser must call `/api/users`. Duende themselves describe the underlying problem plainly: *"The server URLs in these documents represent the direct URL to the API. Clients shouldn't access the API directly but through the BFF"* [[2]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui).

The fix is trivial when the prefix is uniform — configure the BFF route as `MapRemoteBffApiEndpoint("/api", new Uri("https://remoteHost/api"))` and the paths line up again, with nothing to do in codegen. **Design the proxy to be path-preserving and this entire section evaporates.** That is a free, deliberate choice at day zero; retrofitting it later is not.

Duende ship an official **OpenAPI sample** in the BFF samples list, alongside a **YARP integration** sample and a **Separate Host for UI** sample — evidence the "how do my specs survive the proxy" question is a recognised, first-class concern rather than an edge case [[5]](https://docs.duendesoftware.com/bff/samples/).

### The composing case: merging documents

If the BFF grows its own endpoints, you need a merged document. The options, none of them free:

- **Runtime merge in the BFF.** Duende's own worked example implements an `OpenApiDocumentCombiner` that fetches multiple downstream OpenAPI documents at runtime and merges them into a single spec, plus an `OpenApiResponseTransform` that rewrites `paths` to include the BFF prefix and rewrites `servers` to point at the BFF host. The combined spec also **strips the security schemes**, because the BFF now handles auth centrally [[2]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui).
- **YARP-side aggregation.** [yarp-swagger](https://github.com/andreytreyt/yarp-swagger) ⭐ 108 (Jul 2026) reuses YARP cluster/route config to publish an aggregated Swagger document [[23]](https://github.com/andreytreyt/yarp-swagger). It works, but a 108-star project is a load-bearing dependency in your build chain — weigh that. YARP itself ([dotnet/yarp](https://github.com/dotnet/yarp) ⭐ 9.6k) ships **no** built-in OpenAPI aggregation.
- **.NET 10 document transformers.** `Microsoft.AspNetCore.OpenApi` gives you `AddDocumentTransformer` / `AddOperationTransformer` / `AddSchemaTransformer`, and a document transformer *"has access to the entire OpenAPI document"* and can mutate it [[10]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/customize-openapi?view=aspnetcore-10.0). This is the sanctioned hook for rewriting `servers`/`paths`/`components.securitySchemes` — but it only transforms *your own* app's document. It does not fetch and merge someone else's. Merging is still hand-rolled.

**Bottom line:** a proxying BFF is codegen-neutral. A composing BFF is a codegen project.

---

## 2. What the BFF adds that codegen can't reach

The BFF's management endpoints live under `/bff` and are **not in any OpenAPI document** — they're framework-provided, not app endpoints. In Duende's model the base path is configurable (`options.ManagementBasePath = "/bff"`) and the surface is small: login, logout, user, back-channel logout, silent login [[4]](https://docs.duendesoftware.com/bff/fundamentals/session/management/user/).

In practice a React SPA hand-writes exactly three calls:

| Call | Shape | Notes |
|---|---|---|
| `GET /bff/user` | Returns the claims array + `bff:logout_url`, `bff:session_expires_in`, `bff:session_state`. **401** when anonymous (or 200 + `null` if `AnonymousSessionResponse` is configured) | Requires `X-CSRF: 1` header [[4]](https://docs.duendesoftware.com/bff/fundamentals/session/management/user/) |
| `/bff/login` | Top-level **navigation**, not fetch — it 302s to the IdP | Cannot be a TanStack Query call |
| `/bff/logout?sid=…` | Top-level navigation; the `sid` comes from `/bff/user` | — |

That's on the order of 30–50 lines of TypeScript, written once. It is a real but small, bounded, one-time cost — **not** a recurring daily tax. The recurring surface stays fully generated.

Note the CSRF header requirement is not optional and it propagates: **every** `MapRemoteBffApiEndpoint` route also requires the `x-csrf` header, which combined with SameSite cookies deliberately *"triggers a CORS preflight request for cross-origin calls"* [[3]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/). So your generated client needs a global header injector too — but every generator already has that hook (it's the same hook the bearer token would have used).

---

## 3. The auth hook: does it become dead code? No — it gets simpler

Under a cookie BFF, the `Authorization: Bearer` injector every generator scaffolds is replaced by `credentials: 'include'` + a static `X-CSRF: 1` header. The hook stays; what flows through it gets **strictly simpler** — a constant instead of a token you must acquire, cache, refresh, and race-condition-proof.

| Generator | Where the cookie/CSRF config goes | Friction |
|---|---|---|
| [openapi-typescript / openapi-fetch](https://openapi-ts.dev/openapi-fetch/) ⭐ 8.2k | `createClient({ baseUrl, credentials: 'include', headers })` — *"Any valid fetch option (`headers`, `mode`, `cache`, `signal` …)"* is accepted [[15]](https://openapi-ts.dev/openapi-fetch/api) | ✓ two lines |
| [Orval](https://orval.dev) ⭐ 6.2k | `output.baseUrl` + `override.mutator` (custom fetch/axios instance) [[18]](https://orval.dev/docs/) | ✓ standard mutator |
| [Hey API](https://heyapi.dev) ⭐ 5.1k | `createClient({ baseUrl, credentials, headers })` on the fetch client [[19]](https://heyapi.dev/docs/openapi/typescript/clients/fetch) | ✓ two lines |
| [NSwag](https://github.com/RicoSuter/NSwag) ⭐ 7.3k | `useTransformOptionsMethod: true` → implement `transformOptions(RequestInit)` [[17]](https://github.com/RicoSuter/NSwag/wiki/TypeScriptClientGenerator) | ⚠ `WithCredentials = true` **does not** emit `credentials` into the Fetch-template client — open issue [[16]](https://github.com/RicoSuter/NSwag/issues/5229). Use `transformOptions`, not the setting |
| [Kiota](https://github.com/microsoft/kiota) ⭐ 3.8k | `AnonymousAuthenticationProvider` (a no-op placeholder for APIs that don't need a token [[14]](https://learn.microsoft.com/en-us/openapi/kiota/authentication)) + a **custom fetch function** | ⚠ Kiota TS has *no* way to pass fetch options out of the box; you must hand-write a fetch wrapper to set `credentials: 'include'` — open issue on [kiota-typescript](https://github.com/microsoft/kiota-typescript) ⭐ 61 [[13]](https://github.com/microsoft/kiota-typescript/issues/1817) |

Only Kiota and NSwag have sharp edges here, and both have documented workarounds. **No generator is broken by a BFF.**

One genuine *simplification*: because the BFF terminates auth, the merged/proxied spec can drop `securitySchemes` entirely [[2]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui). Meanwhile the pure-SPA path forces you to keep the bearer scheme in the document (`.NET 10` has a documented `BearerSecuritySchemeTransformer` for exactly this [[10]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/customize-openapi?view=aspnetcore-10.0)) *and* build a token-refresh interceptor in the client. Net: the BFF removes more client-side auth code than it adds.

---

## 4. .NET 10 OpenAPI: what actually shipped, and how it meets a proxy

| Feature | Status in .NET 10 | Relevance to a BFF |
|---|---|---|
| OpenAPI **3.1** documents | Default in .NET 10 (3.2 becomes the default in .NET 11) [[9]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0) | Neutral |
| **YAML** output | `app.MapOpenApi("/openapi/{documentName}.yaml")` [[9]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0) | Neutral. ⚠ YAML at **build time is not supported** ("planned for a future preview") [[9]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0) |
| **Build-time generation** (`Microsoft.Extensions.ApiDescription.Server`, `OpenApiGenerateDocuments` / `OpenApiDocumentsDirectory`) | Ships. Launches the app entrypoint with a mock server via `GetDocument.Insider` [[9]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0) | **This is the ergonomics win, and it is BFF-independent.** The spec drops to disk on `dotnet build` — codegen never has to hit a running server, so it never has to traverse the BFF or authenticate at all |
| Document / operation / schema **transformers** | Ship; document transformers can mutate the whole `OpenApiDocument` [[10]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/customize-openapi?view=aspnetcore-10.0) | The hook for rewriting `servers` to the BFF origin |
| `ShouldInclude` delegate | Per-document endpoint filtering [[9]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0) | Lets one project emit a "public" and an "internal" doc |
| `GetOrCreateSchemaAsync` + `Document.AddComponent` in transformers | New in .NET 10 [[10]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/customize-openapi?view=aspnetcore-10.0) | Makes hand-adding BFF-specific schemas to a merged doc tractable |

⚠ Build-time generation *invokes your Program.cs*. If BFF startup opens a connection to Keycloak or a DB, you must gate it: the docs recommend checking `Assembly.GetEntryAssembly()?.GetName().Name != "GetDocument.Insider"` [[9]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0). This is a genuine BFF-adjacent papercut — one more startup path to keep working.

**Verdict:** with build-time generation, the codegen pipeline never touches a live server. The BFF is invisible to it. This is the single most important .NET 10 fact for this angle.

---

## 5. The local dev loop, in painful detail

### The failure mode everyone gets wrong: it's the *scheme*, not the port

The "site" in SameSite is **scheme + eTLD+1. The port is not part of it.** `http://localhost:5173` and `http://localhost:5000` are **same-site** (different origins, but same site) [[6]](https://web.dev/articles/same-site-same-origin). So a `SameSite=Lax` cookie is *not* dropped merely because your ports differ.

What **does** kill it is schemeful same-site: since late 2019 the scheme is part of the site [[6]](https://web.dev/articles/same-site-same-origin). And the default dev configuration puts you straight into that trap:

> Vite defaults to **`http`**://localhost:5173. ASP.NET Core's dev profile defaults to **`https`**://localhost:7xxx. → `http://localhost` vs `https://localhost` are **cross-site** → the BFF's `SameSite=Lax`/`Strict` session cookie is never sent. ✗

Every working sample fixes this one of two ways, and only one of them is good:

| Dev topology | Browser sees | Cookie works | HMR | CORS needed | Verdict |
|---|---|---|---|---|---|
| **Vite proxies to BFF** (`server.proxy`) | One origin: `localhost:5173` | ✓ first-party, scheme moot | ✓ native | ✗ none | ✓ **recommended** |
| **BFF proxies to Vite** (`Microsoft.AspNetCore.SpaProxy`) | One origin: the BFF | ✓ first-party | ⚠ needs WebSocket proxying | ✗ none | ⚠ works, more moving parts |
| **Both standalone, matching schemes** (both `https`) | Two origins, same site | ✓ but needs `credentials: 'include'` + CORS w/ credentials | ✓ native | ✓ yes | ⚠ closest to prod-with-CDN |
| **Both standalone, mismatched schemes** (`http` Vite + `https` BFF) | Cross-**site** | ✗ silently dropped | ✓ | ✓ | ✗ **the trap** |
| **`SameSite=None` to force it** | Cross-site | ⚠ requires `Secure`; third-party cookie blocking in Safari/Firefox [[24]](https://docs.duendesoftware.com/bff/architecture/third-party-cookies/) | ✓ | ✓ | ✗ don't — it re-opens the CSRF surface the BFF exists to close |

### The Vite proxy config, concretely

Duende's official guidance is that same-origin hosting means *"requests from the front end to the backend will automatically include the authentication cookie and not require CORS headers"* [[1]](https://docs.duendesoftware.com/bff/architecture/ui-hosting/). The Vite dev proxy synthesises exactly that: the browser only ever talks to `localhost:5173`.

You must proxy **four** route groups, not one — a working standalone-BFF walkthrough proxies `/bff`, `/api`, `/signin-oidc`, and `/signout-callback-oidc`, all targeting the BFF at `https://localhost:7164` with `secure: false` (self-signed cert) [[8]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa).

The two OIDC callback paths are the non-obvious part and are **easy to miss**: `/bff/login` is a top-level navigation that 302s to Keycloak; Keycloak redirects back to a `redirect_uri` that must be registered as `http(s)://localhost:5173/signin-oidc` — so Vite must proxy that path back to the BFF or the login loop dead-ends. Registering the Vite origin (not the BFF's) in Keycloak is a config change devs forget.

⚠ **The BFF must be told its public origin is `:5173`.** Set `changeOrigin` in the Vite proxy and/or `ForwardedHeaders` in the BFF, or the OIDC handler builds redirect URIs against `:7164` and the login round-trip breaks.

### HMR

Vite's own docs: *"reverse proxies in front of Vite are expected to support proxying WebSocket"*, and if the HMR WebSocket can't connect, *"the client will fall back to connecting the WebSocket directly to the Vite HMR server bypassing the reverse proxies"* [[7]](https://vite.dev/config/server-options).

- **Vite-proxies-BFF:** HMR is untouched. Vite is the origin; the WebSocket is direct. ✓ **Zero HMR risk.**
- **BFF-proxies-Vite (SpaProxy):** the .NET proxy is now in front of Vite's HMR socket. It needs `ws: true`-equivalent WebSocket passthrough, or you get the fallback (which "works" but spews console errors, or fails outright behind a stricter proxy). ⚠

This asymmetry is the deciding argument: **let Vite be the proxy, not the proxied.**

### HTTPS certs

If you do go standalone-with-matching-schemes, you need Vite on HTTPS. Options: `@vitejs/plugin-basic-ssl` [[8]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa), [vite-plugin-mkcert](https://github.com/liuweiGL/vite-plugin-mkcert) ⭐ 759 (generates a locally-trusted CA) [[25]](https://github.com/liuweiGL/vite-plugin-mkcert), or export the .NET dev cert and feed it to Vite: `dotnet dev-certs https -ep localhost.pfx -p pass` [[26]](https://jmelosegui.com/posts/dotnet-dev-cert-with-vite). **With the Vite-proxies-BFF topology you can skip all of this** — `secure: false` on the proxy target is enough, because the untrusted cert is only crossed server-side, never by the browser.

### Process count

| | Pure SPA | BFF (Vite proxy) | BFF (+ Aspire) |
|---|---|---|---|
| Vite dev server | ✓ | ✓ | orchestrated |
| .NET API | ✓ | ✓ | orchestrated |
| .NET BFF | ✗ | ✓ | orchestrated |
| Keycloak (Docker) | ✓ | ✓ | orchestrated |
| **Terminals a dev runs** | **3** (`vite`, `dotnet run`, `docker compose up`) | **4** | **1** (`aspire run`) |
| CORS config in the API | ✓ required | ✗ not needed | ✗ not needed |
| Codegen needs a live server | ✗ (build-time gen) | ✗ (build-time gen) | ✗ |
| Swagger UI "Try it out" against the real auth | ✓ (paste bearer token) | ✗ see below | ✗ |
| HMR | ✓ | ✓ | ✓ |

The BFF adds **exactly one process** and **one `vite.config.ts` proxy block**. That is the whole recurring ergonomics delta on the run-the-app axis. It is far smaller than the folklore suggests — and it *removes* the CORS configuration from the API.

The F5 loop itself is unchanged: Vite still serves modules, HMR still fires, `dotnet watch` still recompiles. Nothing is added to the inner loop, because the BFF sits in the request path, not the build path.

---

## 6. The real cost: backend debugging tooling breaks

This is the underrated one, and it is where the BFF actually hurts.

**Swagger UI's "Try it out" does not work with cookie auth.** Straight from the spec docs: *"Cookie authentication is currently not supported for 'try it out' requests due to browser security restrictions"* [[11]](https://swagger.io/docs/specification/v3_0/authentication/cookie-authentication/). Swagger UI is architected as a public client that injects bearer tokens into headers — *"which a secure BFF should reject"* — and it bypasses the cookies and CSRF tokens the BFF requires [[12]](https://dzone.com/articles/swagger-ui-bff-architecture).

Concretely, a backend dev's habits under a BFF:

| Tool | Pure SPA (bearer) | Under a cookie BFF |
|---|---|---|
| Swagger UI / Scalar "Try it out" | ✓ paste a token from Keycloak | ✗ out of the box |
| `.http` file / REST Client / Postman | ✓ `Authorization: Bearer …` | ⚠ works **only if you hit the API directly**, bypassing the BFF — so you're not testing the real path |
| curl against the API port | ✓ | ⚠ same caveat |

Two fixes exist, both real work:

1. **Serve Swagger UI from the BFF's origin** and inject the CSRF header. Duende's exact recipe: `c.UseRequestInterceptor("function(request){ request.headers['X-CSRF'] = '1'; return request; }")`, combined with a proxied+transformed spec whose `servers` point at the BFF [[2]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui). Then the browser's existing BFF session cookie is used automatically, and *"users authenticate once to the BFF, then Swagger UI can explore and test all proxied APIs"*. ✓ This genuinely works.
2. **A Swagger UI plugin** that routes calls through the BFF and adds CSRF headers, treating Swagger UI as "just another frontend client" [[12]](https://dzone.com/articles/swagger-ui-bff-architecture).

Either way: **the API's Swagger UI stops being usable standalone**, and someone has to build and maintain the BFF-hosted variant. Budget half a day, once — plus the ongoing reality that backend devs must remember there are now two Swagger UIs and only one of them is honest about auth.

Mitigation worth stating: in an **internal admin console** the API is usually still directly reachable in dev, so a backend dev can keep bearer-token `.http` files for API-only iteration and only exercise the BFF path when debugging auth. The cost is the cognitive split, not a hard block.

---

## 7. Does .NET Aspire fix the multi-process problem?

Largely, yes — and by 2026 it's a mature answer, not a bet.

- `builder.AddViteApp(name: "todo-frontend", workingDirectory: "../todo-frontend").WithReference(apiService).WaitFor(apiService).WithNpmPackageInstallation()` puts the Vite dev server in the app model. Aspire injects the API's assigned address as an env var (`services__apiservice__https__0`), which `vite.config.js` reads to configure `server.proxy` — *"This eliminates CORS issues during development by proxying requests through the same origin."* [[20]](https://devblogs.microsoft.com/dotnet/new-aspire-app-with-react/)
- Keycloak is a first-class hosting integration, so it's a container Aspire starts for you rather than a separate `docker compose up` [[20]](https://devblogs.microsoft.com/dotnet/new-aspire-app-with-react/).
- One command starts everything; the dashboard gives unified logs/traces/status across frontend, BFF, API, and Keycloak [[20]](https://devblogs.microsoft.com/dotnet/new-aspire-app-with-react/).
- Aspire 13.2 (March 2026) landed 1,100+ closed issues, themed on the CLI as a first-class agent interface, a TypeScript AppHost preview, and "making local development seamless" [[21]](https://www.infoq.com/news/2026/04/aspire-13-2-release/) [[27]](https://github.com/microsoft/aspire/discussions/15662). [microsoft/aspire](https://github.com/microsoft/aspire) ⭐ 6.2k (Jul 2026).

**The cost, honestly stated:** Aspire is orchestration you now own. Community assessment in 2026: it shines when *"you have multiple services that need to communicate, shared infrastructure, a need for consistent observability, or complex local development setup"* — but *"for single-API projects with just a database, Aspire adds unnecessary overhead"* and a standard ASP.NET Core template is simpler [[22]](https://codewithmukesh.com/blog/aspire-for-dotnet-developers-deep-dive/). The same source notes the local dev experience is *"considerably more polished than the deployment experience"* as of 2026 [[22]](https://codewithmukesh.com/blog/aspire-for-dotnet-developers-deep-dive/).

For **SPA + API + BFF + Keycloak** — four processes, two of them containers — you are squarely in the "Aspire pays for itself" band. And note the key asymmetry for this decision: **Aspire helps the BFF option more than the pure-SPA option**, because it collapses precisely the multi-process cost that the BFF introduces. Adopting Aspire *neutralises the BFF's main ergonomics objection.*

---

## 8. Verdict: the daily delta

| Axis | Delta from adding a BFF |
|---|---|
| OpenAPI document | **No change** if the proxy is path-preserving [[3]](https://docs.duendesoftware.com/bff/fundamentals/apis/remote/) |
| Generated client code | **No change**. `baseUrl` becomes relative, `credentials: 'include'` + `X-CSRF: 1` added [[15]](https://openapi-ts.dev/openapi-fetch/api) |
| Codegen pipeline | **No change** — .NET 10 build-time generation writes the spec to disk; it never traverses the BFF [[9]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0) |
| Client auth code | **Simpler.** No token store, no refresh interceptor, no bearer scheme in the spec [[2]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui) |
| Hand-written client code | **+30–50 lines**, once: `/bff/user`, `/bff/login`, `/bff/logout` [[4]](https://docs.duendesoftware.com/bff/fundamentals/session/management/user/) |
| Processes to run | **+1** (3 → 4), or **→1** if you adopt Aspire [[20]](https://devblogs.microsoft.com/dotnet/new-aspire-app-with-react/) |
| `vite.config.ts` | **+1 proxy block, 4 routes** (`/bff`, `/api`, `/signin-oidc`, `/signout-callback-oidc`) [[8]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa) |
| CORS config in the API | **Removed** [[1]](https://docs.duendesoftware.com/bff/architecture/ui-hosting/) |
| HMR / F5 loop | **Unchanged** — provided Vite is the proxy, not the proxied [[7]](https://vite.dev/config/server-options) |
| HTTPS dev certs | **Not needed** with the Vite-proxy topology (`secure: false`) [[8]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa) |
| Swagger UI "Try it out" | ✗ **Breaks.** ~half a day to rebuild a BFF-hosted, CSRF-intercepting Swagger UI [[11]](https://swagger.io/docs/specification/v3_0/authentication/cookie-authentication/) [[2]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui) |
| Keycloak client config | `redirect_uri` must be the **Vite** origin in dev, not the BFF's [[8]](https://wrapt.dev/blog/standalone-duende-bff-for-any-spa) |
| Composing/aggregating BFF | ✗ **Don't** — two OpenAPI docs, a hand-rolled merger, and a 108-star dependency [[23]](https://github.com/andreytreyt/yarp-swagger) [[2]](https://duendesoftware.com/blog/20250430-managing-openapi-specifications-with-backend-for-frontend-and-swagger-ui) |

**Summed up.** The BFF's ergonomics bill is roughly: one extra process, one config block, one broken debugging tool, and a one-time ~50-line hand-written auth module. Against that, it *deletes* your CORS config and your entire client-side token-refresh machinery. For an internal admin console with a modest team, that is close to a wash — provided you make **two non-negotiable design choices at day zero**:

1. **The BFF is a path-preserving transparent proxy.** Never a composer. The moment it composes, codegen becomes a project.
2. **Vite proxies the BFF, not the reverse.** This keeps HMR native, keeps the cookie first-party, and makes the dev-cert problem disappear.

Break either rule and the "quietly free" BFF becomes the expensive one.
