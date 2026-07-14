---
title: "In-memory tokens vs cookie-backed BFF sessions under XSS: what each architecture actually buys you"
date: 2026-07-14
depth: survey
format: md
topic: "In-memory tokens vs cookie-backed BFF sessions under XSS — what each architecture actually buys you when script executes in the page: token exfiltration vs session-riding, blast radius, CSP/Trusted-Types as the real mitigation, and the honest limits of httpOnly cookies."
topic_raw: "In-memory tokens vs cookie-backed BFF sessions under XSS — what each architecture actually buys you when script executes in the page: token exfiltration vs session-riding, blast radius, CSP/Trusted-Types as the real mitigation, and the honest limits of httpOnly cookies."
tags: [security, xss, bff, oauth, spa, csp, trusted-types, dotnet]
summary: "httpOnly cookies do not stop XSS — they convert silent token exfiltration into loud, tab-bound session riding. That's a real but bounded win; CSP + Trusted Types is the actual mitigation."
citations: 17
reading_time_min: 8
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 365
issue: 6
---

> **Decision.** A BFF's httpOnly cookie does **not** protect you from XSS; it converts a *silent, portable, survives-tab-close* token theft into a *loud, origin-bound, dies-with-the-tab* session ride [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26) [[3]](https://fusionauth.io/blog/backend-for-frontend-security-architecture). That is a genuine reduction in blast radius and the only reason to pick the BFF on security grounds — but the attacker still acts as the user for as long as the page is compromised [[6]](https://www.schellman.com/blog/demonstrating-impact-with-cross-site-scripting). Token storage is damage-limitation; **strict CSP + Trusted Types is the mitigation** [[7]](https://web.dev/articles/strict-csp) [[9]](https://www.uriports.com/blog/csp-trusted-types/). For a first-party internal admin console the exfiltration delta shrinks (no third-party scripts, network-restricted API, short sessions) — which makes the BFF's XSS argument, on its own, a weak reason to build one.

## The claim under interrogation

The slogan is "httpOnly cookies protect you from XSS." The precise, defensible version is much narrower: httpOnly prevents **JavaScript from reading the cookie value**. It does nothing about the browser attaching that cookie to requests the attacker's script makes: "Cookies marked with HttpOnly are still automatically included in same-origin requests made by JavaScript (such as `fetch` or `XMLHttpRequest` calls)" [[14]](https://nestenius.se/net/bff-in-asp-net-core-3-the-bff-pattern-explained/). The IETF's browser-app BCP says the same thing in threat language: under a BFF, "Proxying Requests via the User's Browser" remains possible "because the malicious browser-based code still runs within the application's origin" (§6.1.4.1.1) [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26).

Philippe De Ryck — co-author of that draft — puts the general case bluntly: "A successful XSS attack gives the attacker full control over your application code… In a nutshell, XSS means game over!" [[2]](https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html). His point is that in-memory storage is not a defence either: an attacker who controls the page can redefine `MessageChannel`, patch `fetch`/`Headers`, hook the app's own token-holding closure, or simply trigger a silent-auth flow and read the fresh token out of the response [[2]](https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html). Auth0 states the corollary flatly: "Tokens in localStorage, sessionStorage, or even JavaScript memory are all reachable by malicious scripts" [[12]](https://auth0.com/blog/things-developers-get-wrong-about-the-backend-for-frontend-pattern/).

So the honest framing is not *protected vs unprotected*. It is **two different post-compromise loss profiles**.

## What the attacker actually does, per architecture

### A. In-memory access token (React 19 SPA calling .NET APIs directly)

1. Payload executes → patches the app's HTTP layer, or reads the token from the module closure, or fires a hidden silent-renew and harvests the result [[2]](https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html).
2. `POST` the token to attacker infrastructure. Done — **one HTTP request, and the attacker is now off-origin**.
3. The token is a bearer credential: it works from the attacker's machine, from a script, from anywhere, for its full remaining lifetime [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26).
4. If a refresh token is also browser-reachable, the draft's "Persistent Token Theft" applies and the attacker keeps renewing [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26). The victim closing the tab changes nothing.

### B. httpOnly cookie + BFF (.NET 10 proxying to the APIs)

1. Payload executes → cannot read the cookie [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26), cannot see an access token (there isn't one in the browser) [[11]](https://docs.duendesoftware.com/bff/), cannot start a new OAuth flow to mint one because "the BFF is a confidential client" (§6.1.3.1) [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26).
2. So it **rides the session instead**: it issues same-origin `fetch()` calls to the BFF, which attaches the cookie, exchanges it for the real access token server-side, and forwards the call. A pentester's version of this: "requests are first loaded through an external script and then sent from the local context of the user's browser… Using XHR, an attacker can make the victim perform any action within the application" [[6]](https://www.schellman.com/blog/demonstrating-impact-with-cross-site-scripting).
3. Anti-CSRF adds nothing here — same-origin script reads the response bodies and lifts the token: "you can create a new variable — `ctoken` — and set the value to the HTTP response we just made" [[6]](https://www.schellman.com/blog/demonstrating-impact-with-cross-site-scripting). Duende's own CSRF defence is a required custom header [[11]](https://docs.duendesoftware.com/bff/) — trivially set by same-origin JS. Microsoft's MSRC catalogues this exact composition as "XSS + CSRF → injected script triggers state-changing requests in authenticated user session" [[5]](https://www.microsoft.com/en-us/msrc/blog/2025/11/weaponizing-cross-site-scripting-when-one-bug-isnt-enough).
4. **But**: everything must happen through the victim's browser, through your BFF, while the tab is open. "The attacker can make requests to your BFF while the user's browser is open. But they can't exfiltrate tokens for offline use" [[3]](https://fusionauth.io/blog/backend-for-frontend-security-architecture).

## The threat delta

| Property under an executing XSS payload | In-memory token (SPA→API) | localStorage / sessionStorage token | httpOnly cookie + BFF |
|---|---|---|---|
| Credential readable by script | ✓ (patch app code / silent-renew) [[2]](https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html) | ✓ trivially, one line [[4]](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html) | ✗ [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26) |
| Credential exfiltrable off-origin | ✓ [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26) | ✓ [[4]](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html) | ✗ [[3]](https://fusionauth.io/blog/backend-for-frontend-security-architecture) |
| Attacker can act as the user | ✓ | ✓ | ✓ — session riding [[6]](https://www.schellman.com/blog/demonstrating-impact-with-cross-site-scripting) |
| Attack survives the tab closing | ✓ (token TTL, or ∞ with a stolen refresh token) [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26) | ✓ | ✗ — script dies with the page [[3]](https://fusionauth.io/blog/backend-for-frontend-security-architecture) |
| Attack survives page reload | ✗ (unless the injection is stored/persistent) | ✓ (payload can re-read persisted token) | ✗ (unless stored XSS) |
| Attacker can mint *new* tokens | ✓ silent-renew in a hidden iframe [[2]](https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html) | ✓ | ✗ — confidential client [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26) |
| Refresh token in JS reach | depends (⚠ often yes) | ⚠ often yes [[16]](https://news.ycombinator.com/item?id=42427169) | ✗ — never leaves the server [[11]](https://docs.duendesoftware.com/bff/) |
| Revocation actually works | ✗ signed JWT is valid until expiry | ✗ | ✓ "Server can forcibly end sessions" [[11]](https://docs.duendesoftware.com/bff/) |
| Every attacker request is server-observable | ✗ (off-origin use is invisible to you) | ✗ | ✓ (all traffic transits the BFF) [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26) |
| Attack noise | **silent** — one beacon, then quiet | silent | **loud** — N authenticated calls through your own logs |
| Cross-tab / cross-device reuse | ✓ | ✓ | ✗ |

`sessionStorage` vs `localStorage` is a rounding error in this table: both are "always accessible by JavaScript" and "a single Cross Site Scripting can be used to steal all the data in these objects" [[4]](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html). OWASP's preference for `sessionStorage` — "available only to that window/tab until the window is closed" [[4]](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html) — is about *persistence*, not about XSS. In-memory is one further notch: it strips persistence *and* the trivial one-liner read, forcing the attacker to hook the app's own code [[2]](https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html) — real friction against dumb commodity payloads, zero friction against anyone targeting *your* app.

## Where the BFF genuinely wins

- **No bearer credential in JS reach, ever.** "Server-side only — browser never sees tokens" [[11]](https://docs.duendesoftware.com/bff/); the draft rules out both Single-Execution and Persistent Token Theft for this architecture [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26).
- **Revocation is real.** Kill the server-side session and the attacker is out — instantly, not "in 15 minutes when the JWT expires" [[11]](https://docs.duendesoftware.com/bff/).
- **Blast radius is contained to your origin.** No lateral use of the token against other APIs or from the attacker's own infrastructure [[3]](https://fusionauth.io/blog/backend-for-frontend-security-architecture).
- **Supply-chain, not just injected `<script>`.** The Sept 2025 npm compromise (`debug`, `chalk`, ~2B weekly downloads) proved malicious dependency code "can steal *anything* accessible to JavaScript"; FusionAuth's argument is that had those attackers gone for "OAuth tokens in `localStorage` instead of crypto wallets, millions of user sessions would have been compromised" [[3]](https://fusionauth.io/blog/backend-for-frontend-security-architecture). This is the strongest pro-BFF argument, because a strict CSP does **not** stop a trojaned first-party bundle.
- **Forensics.** Because every attacker action must transit the BFF as an authenticated request [[1]](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps-26), you can see it, rate-limit it, and kill it. Exfiltrated-token abuse happens somewhere you are not looking.

## Where it does not win

- The attacker **is** the user for the duration of the compromised page [[6]](https://www.schellman.com/blog/demonstrating-impact-with-cross-site-scripting). For an admin console, "everything the admin can do" is the whole point of the console. If the payload can create a user, grant a role, or plant a webhook in the first 400 ms, the tab-lifetime bound buys you nothing.
- Anti-CSRF, `SameSite`, custom headers — all bypassed by same-origin script [[5]](https://www.microsoft.com/en-us/msrc/blog/2025/11/weaponizing-cross-site-scripting-when-one-bug-isnt-enough) [[6]](https://www.schellman.com/blog/demonstrating-impact-with-cross-site-scripting).
- Vendors overclaim. Duende's marketing says XSS means "there is no risk of the attacker stealing the access tokens" [[15]](https://duendesoftware.com/learn/how-bff-helps-secure-single-page-applications) — true and narrow; read past the headline to the docs, which concede session hijacking is "very difficult to completely protect against" [[11]](https://docs.duendesoftware.com/bff/). Auth0's honest line: "BFF shifts the security boundary. It doesn't eliminate it" [[12]](https://auth0.com/blog/things-developers-get-wrong-about-the-backend-for-frontend-pattern/).

**Contrarian, r/HN:** in the Keycloak/Angular/BFF thread, `horsawlarway` dismisses the whole security case — "All it does is add a marginal level of complexity… still completely hacked" — and argues the real BFF benefits are API consolidation and token-scope reduction, not XSS defence [[13]](https://news.ycombinator.com/item?id=42829315). The counter-view in the same discussion space (`unscaled`): "HttpOnly cookies ARE better in terms of security. Storing Refresh Tokens in local storage is only recommended for low-security use cases" [[16]](https://news.ycombinator.com/item?id=42427169). Both are right about different things — the disagreement is really about whether *bounded* compromise is worth an architecture.

## CSP and Trusted Types: the actual mitigation

If XSS is game over regardless of storage [[2]](https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html), the money goes into not having XSS.

- **Strict CSP** (nonce/hash + `strict-dynamic`) blocks "untrusted inline scripts like inline event handlers or `javascript:` URIs" [[7]](https://web.dev/articles/strict-csp). It exists because allowlist CSP failed empirically: Google's internet-scale study found **94.68% of script-limiting policies ineffective** and 99.34% of CSP-deploying hosts getting "little to no benefit against XSS" [[8]](https://research.google/pubs/csp-is-dead-long-live-csp-on-the-insecurity-of-whitelists-and-the-future-of-content-security-policy/). ⚠ If you deploy an allowlist CSP and call it done, you have deployed nothing.
- **Strict CSP's own holes**, per web.dev: injection into the body or `src` of a nonced script, injection into locations of dynamically-created `script` nodes, AngularJS template injection, and `unsafe-eval` sinks [[7]](https://web.dev/articles/strict-csp). It is script-*loading* control; it does not close DOM sinks.
- **Trusted Types** does close them: `require-trusted-types-for 'script'` "instructs user agents to control the data passed to DOM XSS sink functions" [[10]](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/require-trusted-types-for), blocking "risky injection points (like `.innerHTML`) from using unvalidated string values" [[17]](https://developer.chrome.com/docs/lighthouse/best-practices/trusted-types-xss). **This is the 2026 news**: Safari 26 (Sept 2025) and Firefox (Feb 2026) shipped it, so Trusted Types reached Baseline — "it now works across all major browsers" [[9]](https://www.uriports.com/blog/csp-trusted-types/). React apps are near-compliant already; `dangerouslySetInnerHTML` is the sink you must route through a policy.
- ⚠ **Trusted Types is not magic either**: `createHTML: (input) => input` is a technically valid, entirely useless policy — "the browser enforces the mechanism, but what happens inside the funnel is entirely your responsibility" [[9]](https://www.uriports.com/blog/csp-trusted-types/).
- **The counter-argument to "CSP is the real fix":** CSP is a *policy on scripts the browser loads*. It cannot distinguish your trojaned npm dependency from your own code — the nonced bundle executes with full privilege [[3]](https://fusionauth.io/blog/backend-for-frontend-security-architecture). Against 2025-style supply-chain compromise, CSP is not the mitigation and the BFF's "nothing to steal" property is doing genuine work. Microsoft's framing is the right one: "Because attacks are composable, defenses must be layered. Treat XSS as a gateway risk, not a standalone bug" [[5]](https://www.microsoft.com/en-us/msrc/blog/2025/11/weaponizing-cross-site-scripting-when-one-bug-isnt-enough).

## Calibration for a first-party internal admin console

The published guidance is written for public consumer SPAs. Adjust honestly for `itenium-ui`:

| Factor | Effect on the BFF's XSS argument |
|---|---|
| Single-origin, first-party, no third-party ad/analytics/tag-manager scripts | ⚠ **Weakens it.** The dominant real-world XSS vector (untrusted third-party script) is absent, and strict CSP is *achievable* here in a way it is not on a marketing site [[7]](https://web.dev/articles/strict-csp) |
| React 19 + no `dangerouslySetInnerHTML` + Trusted Types now Baseline | Weakens it. The DOM-sink class of XSS is closable at low cost [[9]](https://www.uriports.com/blog/csp-trusted-types/) [[10]](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/require-trusted-types-for) |
| Admin privileges = high per-action impact | Neutral. Session riding is enough to do maximum damage; the BFF bounds *duration*, not *authority* [[6]](https://www.schellman.com/blog/demonstrating-impact-with-cross-site-scripting) |
| APIs reachable only from the corporate network / VPN | ⚠ **Weakens the exfiltration delta specifically.** A stolen bearer token used from attacker infrastructure fails at the network boundary — the attacker is pushed back into session riding anyway, which is exactly what the BFF was buying you |
| npm supply chain | ⚠ **Strengthens it, and this is the one that survives every other mitigation** [[3]](https://fusionauth.io/blog/backend-for-frontend-security-architecture) |
| Small user population, internal auditing, ability to force logout | Strengthens it slightly — server-side revocation is actually operable here [[11]](https://docs.duendesoftware.com/bff/) |

**Net (contested, and the evidence does not settle it):** for an internet-exposed console the BFF's XSS story is strong. For a network-restricted internal console with a strict CSP and Trusted Types, the incremental XSS benefit over an in-memory token is *narrow* — it reduces to supply-chain resilience and instant revocation. Those are real, but they are a much smaller claim than "httpOnly protects you from XSS," and they should be weighed against the BFF's cost rather than treated as a security trump card. Do not buy a BFF *for XSS* and then skip the CSP; the ordering that the sources support is: eliminate XSS first, then choose storage as damage-limitation [[2]](https://pragmaticwebsecurity.com/articles/oauthoidc/localstorage-xss.html) [[12]](https://auth0.com/blog/things-developers-get-wrong-about-the-backend-for-frontend-pattern/).
