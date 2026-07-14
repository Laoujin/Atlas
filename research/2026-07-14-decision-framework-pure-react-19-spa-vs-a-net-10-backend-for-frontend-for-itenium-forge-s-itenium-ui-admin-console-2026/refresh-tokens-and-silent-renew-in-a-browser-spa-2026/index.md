---
title: "Refresh tokens and silent renew in a browser SPA (2026)"
date: 2026-07-14
depth: survey
format: md
topic: "Refresh tokens and silent renew in a browser SPA (2026) — refresh-token rotation and DPoP/sender-constraining, why the iframe silent-renew pattern is dead post third-party-cookie deprecation, what a Keycloak/OpenIddict SPA can actually do, and how TanStack Query should react to a 401 or expired session in each architecture."
topic_raw: "Refresh tokens and silent renew in a browser SPA (2026) — refresh-token rotation and DPoP/sender-constraining, why the iframe silent-renew pattern is dead post third-party-cookie deprecation, what a Keycloak/OpenIddict SPA can actually do, and how TanStack Query should react to a 401 or expired session in each architecture."
tags: [oauth, oidc, keycloak, openiddict, dpop, tanstack-query, spa, bff, security]
summary: "Iframe silent renew is dead cross-site but alive same-site; refresh-token rotation works on both stacks, DPoP only really works on Keycloak, and TanStack Query needs a single-flight mutex either way."
citations: 39
reading_time_min: 12
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 704
issue: 6
---

> **Decision.** If `auth.itenium.be` and `admin.itenium.be` share a registrable domain, the iframe silent-renew pattern still works — the IdP is **same-site**, not third-party, so no cookie policy touches it [[5]](https://web.dev/articles/same-site-same-origin) [[6]](https://docs.oidc-spa.dev/resources/third-party-cookies-and-session-restoration). But you should not build on it anyway: the pattern is a dead end everywhere else, and rotating refresh tokens in `sessionStorage` are the actually-supported path on both Keycloak and OpenIddict [[13]](https://datatracker.ietf.org/doc/html/rfc9700) [[19]](https://kevinchalet.com/2020/10/27/openiddict-3-0-beta6-is-out/). **DPoP — the thing that makes a browser refresh token defensible — is production-ready on Keycloak 26.4+ [[20]](https://www.keycloak.org/2025/10/dpop-support-26-4) and not usable end-to-end on OpenIddict, whose resource-server stack is Bearer-only [[22]](https://github.com/openiddict/openiddict-core/issues/2483) ⭐ 5.2k.** In every architecture, TanStack Query needs a single-flight refresh mutex *below* the query layer, or ten parallel queries fire ten refreshes and rotation revokes your session [[30]](https://github.com/TanStack/query/discussions/7617) ⭐ 50k [[34]](https://dev.to/elmehdiamlou/efficient-refresh-token-implementation-with-react-query-and-axios-f8d).

## 1. Third-party cookies in 2026: not deprecated, but not reliable

Get the history right, because the 2023 narrative is wrong. Google **reversed**: on 22 Apr 2025 Anthony Chavez announced Chrome would "maintain our current approach to offering users third-party cookie choice" and **not** roll out the standalone prompt [[1]](https://privacysandbox.google.com/blog/privacy-sandbox-next-steps) [[2]](https://www.adexchanger.com/data-privacy/google-isnt-launching-a-user-choice-prompt-for-third-party-cookies-in-chrome/). Third-party cookies are alive in Chrome today, on by default [[3]](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies).

That does **not** rescue the iframe pattern, because the other half of the web already killed it — years ago and unilaterally.

| Browser | 2026 default for a **cross-site** IdP cookie in an iframe | Share [[12]](https://gs.statcounter.com/browser-market-share) |
|---|---|---|
| Safari | ✗ Blocked outright since 13.1 / iOS 13.4 (24 Mar 2020) [[4]](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/) | ~18% |
| Firefox | ✗ Partitioned per top-level site (Total Cookie Protection, ETP Standard) → IdP sees a different cookie jar [[3]](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies) | ~3% |
| Chrome (normal) | ✓ Sent [[3]](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies) | ~65% |
| Chrome (Incognito) | ✗ Blocked [[3]](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies) | — |
| Edge / Brave | ⚠ Tracker-blocking heuristics; Brave blocks by default [[3]](https://developer.mozilla.org/en-US/docs/Web/Privacy/Guides/Third-party_cookies) | ~5% / <1% |

A feature that works for 65% of users and silently fails for the rest is not a feature. That's exactly what practitioners report: opaque iframe console errors and a hard page reload when renewal fails [[28]](https://github.com/authts/oidc-client-ts/issues/1032) ⭐ 1.9k.

### The crux: same-site ≠ same-origin, and it's same-**site** that matters

A "site" is scheme + eTLD+1. `admin.itenium.be` and `auth.itenium.be` are **different origins but the same site** — "different subdomains don't matter" [[5]](https://web.dev/articles/same-site-same-origin). A cookie set by `auth.itenium.be` and read inside an iframe embedded on `admin.itenium.be` is therefore a **first-party** cookie. None of the blocking above applies. [oidc-spa](https://docs.oidc-spa.dev) states this outright: hosting app and authorization endpoint under the same registrable domain "allows iframe-based restoration, which is the preferred approach when possible"; only cross-site does the browser refuse to attach the cookies and force a full-page redirect fallback (~30% slower, with a visible flash) [[6]](https://docs.oidc-spa.dev/resources/third-party-cookies-and-session-restoration).

So the honest answer for Itenium.Forge: **if you control DNS and put Keycloak on a subdomain of the app's registrable domain, `prompt=none` in a hidden iframe still works in 2026.** If the IdP lives on `login.microsoftonline.com`, `keycloak.some-other-domain.be`, or an Azure-managed host, it's dead.

**Escape hatch for an internal console:** managed Chrome/Edge can force-allow the pair via the `CookiesAllowedForUrls` enterprise policy (`https://auth.example,https://admin.example`) [[11]](https://support.google.com/chrome/a/answer/14439269?hl=en). That works — for corp-managed devices only. Any Mac on Safari, any contractor laptop, still fails. Depending on device management to keep your auth working is a smell.

### What the vendors themselves say

- **Keycloak's own JS adapter docs**: Session Status iframe is unsupported and auto-disabled when third-party cookies are blocked; silent check-sso falls back to a redirect; "the affected adapter features **might ultimately be deprecated**" [[7]](https://www.keycloak.org/securing-apps/javascript-adapter). Concretely: `checkLoginIframe` produces phantom logouts and `silentCheckSsoRedirectUri` produces phantom logged-out states [[8]](https://skycloak.io/blog/keycloak-fedcm-third-party-cookie-deprecation/).
- **Duende** documents the same for OIDC Session Management and OIDC Silent Login, and replaces both with server-side back-channel logout in the BFF [[10]](https://docs.duendesoftware.com/identityserver/v6/bff/architecture/third-party-cookies/).
- **FedCM** is the browser-native replacement in principle. In practice Keycloak still has it as an open discussion, not a feature — "emerging and actively tracked, but not a fully supported, production-ready feature" [[8]](https://skycloak.io/blog/keycloak-fedcm-third-party-cookie-deprecation/) [[9]](https://github.com/keycloak/keycloak/discussions/20339) ⭐ 36k. Do not plan around it.
- **Storage Access API** is Apple's suggested workaround [[4]](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/), but it requires an explicit user gesture — a button click — before the iframe can read the cookie. The [oidc-client-ts](https://github.com/authts/oidc-client-ts) PoC for it is still an unmerged issue [[27]](https://github.com/authts/oidc-client-ts/issues/1735) ⭐ 1.9k. "Silent" renew that needs a click is not silent renew.

## 2. Refresh tokens in the browser: what the BCP actually demands

RFC 9700 (BCP 240, Jan 2025) is unambiguous and is *permission*, not prohibition: **"Refresh tokens for public clients MUST be sender-constrained or use refresh token rotation"** [[13]](https://datatracker.ietf.org/doc/html/rfc9700). Plus: reuse detection invalidating the whole token family, and a maximum lifetime cap regardless of use [[13]](https://datatracker.ietf.org/doc/html/rfc9700). Auth0's implementation is the canonical shape of "family revocation": replaying a redeemed refresh token revokes "all refresh tokens descending from the original refresh token issued for the client" [[15]](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation).

| Control | [Keycloak](https://www.keycloak.org) | [OpenIddict](https://documentation.openiddict.com) |
|---|---|---|
| Rotation | ✓ Realm Settings → Tokens: *Revoke Refresh Token* on, *Refresh Token Max Reuse* = 0 [[18]](https://skycloak.io/blog/session-management-in-keycloak-from-refresh-to-idle-timeouts/) | ✓ Rolling refresh tokens **on by default** since 3.0 [[19]](https://kevinchalet.com/2020/10/27/openiddict-3-0-beta6-is-out/) |
| Concurrency leeway | ✗ None; `Max Reuse` is a blunt counter [[18]](https://skycloak.io/blog/session-management-in-keycloak-from-refresh-to-idle-timeouts/) | ✓ 15 s `SetRefreshTokenReuseLeeway()` explicitly "to avoid revoking entire token chains when concurrent requests are received" [[19]](https://kevinchalet.com/2020/10/27/openiddict-3-0-beta6-is-out/) |
| Multi-tab behaviour | ⚠ Broken. Two tabs = two token families; refreshing one revokes **both** → all tabs logged out. Closed **not planned** [[16]](https://github.com/keycloak/keycloak/issues/16081) ⭐ 36k | ✓ Redeemed-marking + leeway survives it [[19]](https://kevinchalet.com/2020/10/27/openiddict-3-0-beta6-is-out/) |
| Reuse-detection soundness | ⚠ **CVE-2026-9802**: a server restart resets `startupTime`, letting *every* previously rotated refresh token be redeemed again when `revokeRefreshToken=true`. Fixes targeted at 26.4.13 / 26.6.3 / 26.7.0 [[17]](https://github.com/keycloak/keycloak/issues/49426) ⭐ 36k | (no equivalent public advisory found) |
| Lifetime caps | ✓ SSO Session Idle (30 min default), SSO Session Max (10 h default) [[18]](https://skycloak.io/blog/session-management-in-keycloak-from-refresh-to-idle-timeouts/) | ✓ Per-client token lifetimes |
| Cost of rotation | Needs revocation state in the DB (Keycloak already has it) | Needs OpenIddict **token entries persisted** — you are now running a token table with pruning |

Read the Keycloak column again. Rotation is the thing the BCP demands, and Keycloak's implementation of it has a *closed-as-not-planned* multi-tab defect [[16]](https://github.com/keycloak/keycloak/issues/16081) and a 2026 CVE in its stale-token check [[17]](https://github.com/keycloak/keycloak/issues/49426). Rotation in the browser is not a checkbox; it is an ongoing operational surface. An internal admin console where users routinely open three tabs is precisely the workload that trips it.

## 3. DPoP: real on Keycloak, half-built on OpenIddict, and theoretically weaker than it looks

RFC 9449 (Sept 2023) is the sender-constraining answer: a public client presenting a DPoP proof gets a refresh token that **MUST** be bound to that public key, and must prove possession of the same key on every use [[14]](https://datatracker.ietf.org/doc/html/rfc9449). A stolen refresh token is then worthless off-device.

| | DPoP status, mid-2026 |
|---|---|
| **Keycloak** | ✓ **Officially supported in 26.4** (preview since 23.0.0). Covers all bearer endpoints incl. Admin REST API; can bind *only* refresh tokens for public clients while leaving access tokens as bearer; `dpop_jkt` in the authorization request [[20]](https://www.keycloak.org/2025/10/dpop-support-26-4) [[21]](https://www.keycloak.org/securing-apps/dpop) |
| **OpenIddict** | ⚠ **Issuance side only.** As of June 2026 the *validation / resource-server* stack "has no DPoP support at all" — token extraction is Bearer-only, proof-of-possession validation is mTLS-only [[22]](https://github.com/openiddict/openiddict-core/issues/2483) ⭐ 5.2k. mTLS/`cnf.x5t#S256` binding is the supported path [[23]](https://documentation.openiddict.com/configuration/mutual-tls-authentication) — and mTLS is not a browser SPA option. |
| **oidc-client-ts** | ✓ Implements RFC 9449: `IndexedDbDPoPStore` holding a **non-extractable `CryptoKeyPair`**, `bind_authorization_code`, `UserManager.dpopProof()` [[25]](https://github.com/authts/oidc-client-ts/blob/main/docs/protocols/demonstrating-proof-of-possession.md) ⭐ 1.9k |
| **oidc-spa** | ✓ `dpop: "auto"` — installs `fetch`/XHR interceptors, transparent; Keycloak 26.4+ officially supported; Entra ID unsupported [[26]](https://docs.oidc-spa.dev/security-features/dpop) |

**The catch, and it is a big one.** DPoP does *not* make a browser refresh token safe from XSS. A non-extractable WebCrypto key gates exactly two operations — `exportKey()` and `wrapKey()` [[24]](https://www.infoq.com/articles/dpop-key-storage-unsolved-problem/). It does not gate `sign()`. Injected script does not need the key bytes; it calls the browser's signing function and mints proofs. RFC 9449 concedes this: with DPoP "the attacker can only abuse stolen tokens by carrying out an **online** attack, where the proofs are calculated in the user's browser" [[24]](https://www.infoq.com/articles/dpop-key-storage-unsolved-problem/). And in Firefox you can't even get that far — Firefox cannot store `CryptoKey` objects in IndexedDB, forcing extractable keys and defeating non-extractability entirely [[24]](https://www.infoq.com/articles/dpop-key-storage-unsolved-problem/).

DPoP downgrades *exfiltration + offline replay* to *online abuse for as long as the tab is open*. Real, worth having, not a solution. InfoQ's conclusion (30 Apr 2026): "The BFF pattern is the safest choice today for browser-based applications" [[24]](https://www.infoq.com/articles/dpop-key-storage-unsolved-problem/).

## 4. Concrete libraries a React 19 SPA would use

| Library | ⭐ Stars (Jul 2026) | Verdict for `itenium-ui` |
|---|---|---|
| [oidc-client-ts](https://github.com/authts/oidc-client-ts) | ⭐ 1.9k [[25]](https://github.com/authts/oidc-client-ts/blob/main/docs/protocols/demonstrating-proof-of-possession.md) | The de-facto core. Works against both Keycloak and OpenIddict. DPoP support shipped. |
| [react-oidc-context](https://github.com/authts/react-oidc-context) | ⭐ 1k [[29]](https://github.com/authts/react-oidc-context) | Thin React binding over the above. What you'd actually import. |
| [oidc-spa](https://docs.oidc-spa.dev) | ⭐ 302 [[38]](https://github.com/keycloakify/oidc-spa) | Opinionated: automatic third-party-cookie fallback, `dpop: "auto"`. Smallest ecosystem, best defaults. |
| [keycloak-js](https://github.com/keycloak/keycloak-js) | ⭐ 88 [[37]](https://github.com/keycloak/keycloak-js) | ⚠ Vendor-locked, and its two headline features (`checkLoginIframe`, `silentCheckSsoRedirectUri`) are the ones Keycloak's own docs say may be deprecated [[7]](https://www.keycloak.org/securing-apps/javascript-adapter). Avoid. |
| [@auth0/auth0-react](https://github.com/auth0/auth0-react) | ⭐ 988 [[39]](https://github.com/auth0/auth0-react) | Auth0-only. Irrelevant unless you switch IdP. |

## 5. What the BFF makes disappear — and what it makes appear

**Disappears.** The refresh token never enters the browser, so: no rotation config, no reuse-detection semantics to reason about, no multi-tab family-revocation bug [[16]](https://github.com/keycloak/keycloak/issues/16081), no DPoP key storage paradox [[24]](https://www.infoq.com/articles/dpop-key-storage-unsolved-problem/), no iframe, no third-party-cookie matrix, no `sessionStorage` XSS surface. The browser holds one HttpOnly + Secure + SameSite cookie; the BFF retrieves the access token from the server-side session and, "if it is expired or close to expiring, BFF automatically refreshes it using the refresh token" [[36]](https://docs.duendesoftware.com/bff/fundamentals/session/). Renewal stops being a frontend concern entirely.

**Appears.**
- **A server-side session store.** Encrypted-cookie sessions hit the 4 KB browser limit, and back-channel logout / server-initiated termination need server state anyway [[36]](https://docs.duendesoftware.com/bff/fundamentals/session/). That's a Redis or a table, plus its eviction, plus scale-out affinity.
- **Sliding expiration you now own.** The cookie's rolling lifetime is a policy you tune, not one Keycloak tunes for you.
- **The "your session expired" UX.** With a bearer token the SPA *knows* the expiry (it can read the JWT `exp`). With an opaque cookie it knows nothing until a request 401s. You have to build the expiry banner / re-auth modal from 401s, not from a timer.
- **Back-channel logout wiring**, which replaces the check-session iframe [[10]](https://docs.duendesoftware.com/identityserver/v6/bff/architecture/third-party-cookies/).

## 6. TanStack Query: how to actually handle the 401

The default that bites first: [TanStack Query](https://tanstack.com/query) **retries a failed query 3 times with exponential backoff** [[32]](https://tanstack.com/query/latest/docs/framework/react/guides/query-retries). A 401 is not transient. Left alone, one expired token becomes 4 requests × N queries.

```ts
new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) =>
        error instanceof HttpError && error.status === 401 ? false : failureCount < 3,
    },
  },
})
```

### Where the refresh belongs: below the query layer, not in it

TkDodo's answer to "should I use `queryCache`/`mutationCache` `onError` for token refresh?" is one line: **"I would rather use an interceptor on the API layer for that."** [[30]](https://github.com/TanStack/query/discussions/7617) ⭐ 50k. Reasons: the cache callbacks fire *after* retries, they can't transparently replay the original request, and they mix auth concerns into cache concerns. (Note also that `onError` on `useQuery` was removed in v5 — the QueryCache-level handler is what's left, and it fires once per query rather than once per observer [[33]](https://tkdodo.eu/blog/react-query-error-handling).)

### The single-flight mutex — the part everyone gets wrong

Ten queries mount, ten 401s, ten refresh calls. With rotation on, nine of them present an already-redeemed token → reuse detected → **the whole family is revoked and the user is logged out**. This is the #1 reported pitfall: a real codebase fired the refresh "around 6-10 times at once when reopening the site" [[35]](https://akhilaariyachandra.com/blog/refreshing-an-authentication-in-token-in-tanstack-query); the TanStack discussion asking how to wire `async-mutex` into this is still unanswered [[31]](https://github.com/TanStack/query/discussions/6249) ⭐ 50k. The fix is the *failed-queue* / promise-memoisation pattern — "without it, multiple simultaneous 401s would trigger multiple refresh calls, causing race conditions" [[34]](https://dev.to/elmehdiamlou/efficient-refresh-token-implementation-with-react-query-and-axios-f8d):

```ts
let inFlight: Promise<string> | null = null

// Everyone awaits the same promise; exactly one /token call leaves the tab.
function refreshOnce(): Promise<string> {
  inFlight ??= doRefresh().finally(() => { inFlight = null })
  return inFlight
}

api.interceptors.response.use(undefined, async (error) => {
  const req = error.config
  if (error.response?.status !== 401 || req._retried) throw error
  req._retried = true                        // one replay per request, or you loop forever
  try {
    const token = await refreshOnce()
    req.headers.Authorization = `Bearer ${token}`
    return api(req)
  } catch {
    queryClient.clear()
    redirectToLogin({ returnTo: location.pathname + location.search })
    throw error
  }
})
```

⚠ The mutex is per-tab. It does **not** protect you across tabs — that needs a `BroadcastChannel` or a Web Lock, and on Keycloak it doesn't help anyway because two tabs mean two token families and rotation revokes both [[16]](https://github.com/keycloak/keycloak/issues/16081).

### The two architectures diverge sharply here

| Concern | Bearer token in the SPA | Opaque cookie session (BFF) |
|---|---|---|
| 401 semantics | Ambiguous: expired access token **or** dead session | Unambiguous: the session is gone |
| Correct reaction | Try refresh → replay original request → only then log out | Hard redirect to `/bff/login?returnUrl=…` |
| Single-flight mutex | **Required** (rotation makes duplicate refreshes destructive) | Not needed in the browser — the BFF serialises it server-side [[36]](https://docs.duendesoftware.com/bff/fundamentals/session/) |
| `retry` on 401 | Must be disabled [[32]](https://tanstack.com/query/latest/docs/framework/react/guides/query-retries) | Must be disabled [[32]](https://tanstack.com/query/latest/docs/framework/react/guides/query-retries) |
| Proactive renewal | Read `exp` from the JWT, refresh at ~80% of lifetime → most 401s never happen | Can't — cookie is opaque. You learn on the 401. |
| In-flight mutations on logout | Replayable after refresh; on hard failure, serialise the mutation variables and re-run post-login | Lost. Persist optimistic mutation state (`persistQueryClient` + `MutationCache`) or accept the loss. |
| CSRF | None (bearer header) | ⚠ Cookie session → needs anti-forgery (`X-CSRF: 1` custom header + `SameSite`) |

Proactive renewal is the single biggest UX asymmetry and it favours the SPA: a bearer client can see `exp` and refresh *before* anything 401s, so the failure path is rare. A cookie client is blind and must treat every 401 as a possible session death. That's why BFF apps show "your session expired" modals and SPAs usually don't.

## 7. Where this lands for `itenium-ui`

- **Do not build on the iframe.** Even if `auth.itenium.be` makes it work today [[5]](https://web.dev/articles/same-site-same-origin) [[6]](https://docs.oidc-spa.dev/resources/third-party-cookies-and-session-restoration), it constrains your DNS forever and dies the day someone moves the IdP or fronts it with a SaaS.
- **Pure SPA is viable** — `react-oidc-context` + rotating refresh token in memory/`sessionStorage`, `retry: false` on 401, one refresh mutex. On **Keycloak**, add DPoP (26.4+) and you're aligned with BCP 240 [[13]](https://datatracker.ietf.org/doc/html/rfc9700) [[20]](https://www.keycloak.org/2025/10/dpop-support-26-4). Budget for the multi-tab rotation defect [[16]](https://github.com/keycloak/keycloak/issues/16081) and for tracking CVE-2026-9802 [[17]](https://github.com/keycloak/keycloak/issues/49426).
- **On OpenIddict, the pure SPA cannot be fully BCP-compliant today.** Rotation ✓ (with a 15 s leeway that's better than Keycloak's [[19]](https://kevinchalet.com/2020/10/27/openiddict-3-0-beta6-is-out/)), but sender-constraining ✗ — your .NET 10 resource servers can't validate a DPoP-bound token [[22]](https://github.com/openiddict/openiddict-core/issues/2483). Rotation alone technically satisfies the MUST ("sender-constrained **or** rotation" [[13]](https://datatracker.ietf.org/doc/html/rfc9700)), but you're on the weaker leg with no upgrade path until that stack lands.
- **The BFF's honest pitch is not "more secure" — it's "less to get right."** It deletes the entire cookie matrix, the mutex, the rotation semantics, and the DPoP key-storage paradox, and charges you a session store, a sliding-expiry policy, CSRF, and a worse expiry UX.
