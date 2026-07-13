---
title: "React's native form primitives in 2026: what they replace, and what they don't"
date: 2026-07-13
depth: survey
format: md
topic: "Survey React's native form primitives in 2026 — <form action={fn}>, Server Functions/Server Actions, useActionState, useFormStatus, useOptimistic, and useTransition. Establish what shipped in React 19 and what has landed since. Cover progressive enhancement, per-framework reality (Next.js App Router, React Router 7/8, TanStack Start, plain SPA/Vite), the pending/error state model, and where these primitives genuinely replace a form library."
topic_raw: "react how to do forms in 2026"
tags: [react, forms, react-19, server-actions, rsc, progressive-enhancement, nextjs, react-router, tanstack-start]
summary: "React's form primitives froze at 19.0 and are a submission layer, not a form layer — they own pending/error/optimistic state across the network boundary, and own nothing about the fields."
citations: 25
reading_time_min: 8
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 556
issue: 4
---

> **Decision.** React's native form primitives are a *submission* layer, not a *form* layer. They are complete for the round-trip — pending state, result/error state, optimistic state, and (with Server Functions) a no-JS fallback — and empty for everything that happens between the first keystroke and submit: per-field validation, dirty/touched tracking, field arrays. Use them alone for forms that are essentially "a payload and a button" (login, search, comment, one-click mutations, admin CRUD where a full server round-trip per submit is acceptable). Reach for a library the moment the *interaction* — not the submission — is the hard part [[23]](https://blog.logrocket.com/react-hook-form-vs-react-19/) [[21]](https://github.com/orgs/react-hook-form/discussions/11832) ⭐ 44.8k. The two compose, and the composition is the mainstream 2026 answer, not a compromise.

## Version anchor (July 2026)

| Thing | Current | Form-relevant status |
|---|---|---|
| [React](https://react.dev) | 19.2.7 (2026-06-01); 19.2.0 was 2025-10-01 [[1]](https://react.dev/versions) | No React 20. **Zero new form APIs since 19.0** [[3]](https://react.dev/blog/2025/10/01/react-19-2) |
| [Next.js](https://nextjs.org) | 16.2.x (docs updated 2026-06-23) [[10]](https://nextjs.org/docs/app/guides/forms) | Server Actions stable; the reference implementation |
| [React Router](https://reactrouter.com) | v8, 2026-06-17; ESM-only, requires React ≥19.2.7 [[13]](https://remix.run/blog/react-router-v8) | Own `<Form>`/`action`; RSC + Server Functions still **unstable** [[12]](https://reactrouter.com/start/framework/actions) |
| [TanStack Start](https://tanstack.com/start) | v1.0 (Mar 2026), after a Sept 2025 RC [[17]](https://byteiota.com/tanstack-start-v1-0-type-safe-react-framework-2026/) [[16]](https://tanstack.com/blog/announcing-tanstack-start-v1) | Server functions are **RPC, not RSC** [[24]](https://jilles.me/tanstack-start-server-functions-how-they-work/); RSC deferred to a later 1.x |
| [@vitejs/plugin-rsc](https://github.com/vitejs/vite-plugin-react/tree/main/packages/plugin-rsc) ⭐ 1.1k | Framework-agnostic RSC bundler for Vite [[18]](https://github.com/vitejs/vite-plugin-react/tree/main/packages/plugin-rsc) | The only route to real Server Functions in a non-framework Vite app |

The headline for anyone returning to this after 2024: **nothing has moved**. Actions, `useActionState`, `useFormStatus`, `useOptimistic`, async `useTransition`, `requestFormReset` and Server Functions all landed together in React 19.0 (Dec 2024) [[2]](https://react.dev/blog/2024/12/05/react-19). 19.1 and 19.2 added `Activity`, `useEffectEvent`, Performance Tracks and partial pre-rendering — and not one form API [[3]](https://react.dev/blog/2025/10/01/react-19-2). What changed in 18 months is the *ecosystem around* the primitives, and the sharp edges people found in them.

## The primitives, precisely

Everything is one idea: **an Action is an async function running inside a Transition**. `<form action={fn}>` wraps `fn` in a Transition and hands it the `FormData` [[4]](https://react.dev/reference/react-dom/components/form). The hooks are just different windows onto that Transition.

| Primitive | Owns | Explicitly does not own |
|---|---|---|
| `<form action={fn}>` | Serialising fields → `FormData`, running `fn` in a Transition, resetting uncontrolled fields on completion [[4]](https://react.dev/reference/react-dom/components/form) | Validation, field state. Also **forces `method="POST"`** regardless of the `method` prop [[4]](https://react.dev/reference/react-dom/components/form) |
| `useActionState` | The `[state, action, isPending]` triple; queues concurrent dispatches **sequentially**, threading each result into the next call as `prevState` [[5]](https://react.dev/reference/react/useActionState) | Field-level anything. A throw inside the action cancels the queue and rethrows to the nearest Error Boundary — you must `return` errors, not throw them [[5]](https://react.dev/reference/react/useActionState) |
| `useFormStatus` | `{pending, data, method, action}` of the **parent** form — the design-system escape hatch, so a `<SubmitButton>` needs no props [[6]](https://react.dev/reference/react-dom/hooks/useFormStatus) | Returns nothing useful in the component that *renders* the form; it must be called from a child [[6]](https://react.dev/reference/react-dom/hooks/useFormStatus) |
| `useOptimistic` | Immediate UI state during an Action; **auto-reverts** to the real value when the Action settles, success or failure [[7]](https://react.dev/reference/react/useOptimistic) | The setter throws outside an Action/`startTransition` — you cannot use it as a general-purpose local state hook [[7]](https://react.dev/reference/react/useOptimistic) |
| `useTransition` (async) | The imperative form of the same thing, when there is no `<form>` — `startTransition(async () => …)` [[2]](https://react.dev/blog/2024/12/05/react-19) | Nothing form-specific; it is the substrate the others sit on |
| Server Functions (`"use server"`) | The network boundary: RPC + the no-JS fallback | Requires an **RSC-capable bundler**, and those bundler-level APIs are explicitly **not semver-stable** [[8]](https://react.dev/reference/rsc/server-functions) |

## Progressive enhancement: real, narrow, and worth less than the marketing

The claim "React forms work without JavaScript" is true under one exact configuration: a `<form action={serverFn}>` **rendered by a Server Component**, with extra args passed via `.bind()` (hidden inputs work too, but are unencoded) [[4]](https://react.dev/reference/react-dom/components/form) [[10]](https://nextjs.org/docs/app/guides/forms). React emits a real HTML form that POSTs to a Server Function endpoint; the browser handles the rest.

The moment you need to *show* a server-side validation error, you move the form into a Client Component to call `useActionState` [[10]](https://nextjs.org/docs/app/guides/forms) — and PE now requires the rarely-used third argument, `permalink`: a URL whose page renders the same component with the same action, so the no-JS POST lands somewhere that can render the error [[5]](https://react.dev/reference/react/useActionState). Almost nobody wires this up. In practice, **real-world Next.js forms with error display are not progressively enhanced**, whatever the marketing says.

Does PE still matter in 2026? The honest argument is not JS-disabled users. It is the pre-hydration window — *"Everybody has JavaScript disabled until it's loaded"* — and the tail: *"only 5% of your users have slow connections, [but] 100% of your users have slow connections 5% of the time"* [[14]](https://v2.remix.run/docs/discussion/progressive-enhancement). That argument holds. But note what it actually buys: a form that *submits* before hydration. It does not buy inline validation, optimistic UI, or a spinner. For a login box or a search field that is the whole product. For a 40-field onboarding wizard it is irrelevant — the wizard cannot function pre-hydration anyway.

⚠ Server Functions are also a live attack surface, not just a DX feature. **CVE-2025-55182** (CVSS 10.0, Dec 2025) was an *unauthenticated RCE* in React's Server Function request deserialization, hitting Next.js, React Router, Waku, Parcel RSC, `@vitejs/plugin-rsc` and rwsdk — and apps were vulnerable *even if they never defined a Server Function*, merely by using RSC [[9]](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components). Two more RSC advisories followed on 2025-12-11. Every Server Function is a public POST endpoint; authorise inside it [[10]](https://nextjs.org/docs/app/guides/forms).

## Per-framework reality

| | `<form action={fn}>` with client fn | Server Functions as form action | No-JS submit | Idiomatic pending/result API |
|---|---|---|---|---|
| **Next.js 16 App Router** | ✓ | ✓ stable, the default mutation path [[10]](https://nextjs.org/docs/app/guides/forms) | ✓ from a Server Component; ✗ once you need `useActionState` errors without a `permalink` [[5]](https://react.dev/reference/react/useActionState) | `useActionState` + `useFormStatus`. Also `next/form` for GET/search forms with prefetch [[11]](https://nextjs.org/docs/app/api-reference/components/form) |
| **React Router 8 / Remix** | ✓ (it's a react-dom feature) | ⚠ RSC + Server Functions still **unstable** in v8 [[13]](https://remix.run/blog/react-router-v8) | ✓ — but via RR's *own* `<Form>` + route `action`, which predates and bypasses React's Actions [[12]](https://reactrouter.com/start/framework/actions) | `useFetcher` (`state`, `data`, `Form`, `reset`) — a parallel, non-navigating pending/result model [[25]](https://reactrouter.com/api/hooks/useFetcher) |
| **TanStack Start 1.0** | ✓ | ⚠ not RSC Server Actions — `createServerFn` is a compiled **RPC stub** [[24]](https://jilles.me/tanstack-start-server-functions-how-they-work/) [[15]](https://tanstack.com/start/latest/docs/framework/react/guide/server-functions) | ✓ via `serverFn.url` as a plain HTML `action` [[15]](https://tanstack.com/start/latest/docs/framework/react/guide/server-functions) | `.validator(schema).handler()` + TanStack Query/Form; no `useActionState` requirement |
| **Plain SPA / Vite** | ✓ — this works, and is the underused case | ✗ without an RSC bundler; `@vitejs/plugin-rsc` ⭐ 1.1k is the framework-agnostic option [[18]](https://github.com/vitejs/vite-plugin-react/tree/main/packages/plugin-rsc) | ✗ | `useActionState` over a plain `fetch` — no server required |

Two things people get wrong here. First: **`<form action={fn}>` and `useActionState` are not RSC features.** They are `react-dom`/`react` features that work in a bare Vite SPA against any REST endpoint. `const [state, submit, pending] = useActionState(async (prev, fd) => (await api.post(fd)).error, null)` is a complete, dependency-free submit-state manager, and it is the single highest-value thing an SPA team can adopt from React 19. Second: in React Router, the *route action* — not React's `action` prop — remains the idiomatic path, and RR's `useFetcher` is a competing (older, arguably richer) implementation of the same pending/result idea [[12]](https://reactrouter.com/start/framework/actions) [[25]](https://reactrouter.com/api/hooks/useFetcher). Do not stack both.

## The pending/error model and its four sharp edges

**1. The form wipes itself on a validation error.** React resets uncontrolled fields once the action completes — including when it completes by *returning* an error. The user sees their errors under empty inputs. This was filed as a regression and **closed as not planned**: it is intended behaviour, modelled on classic MPA forms [[19]](https://github.com/facebook/react/issues/31649) ⭐ 246k. The accepted fix is to return the submitted values alongside the errors and feed them back as `defaultValue` from `useActionState`'s state [[20]](https://aurorascharff.no/posts/handling-form-validation-errors-and-resets-with-useactionstate/) — i.e. you re-implement, by hand, a thing every form library gives you for free.

**2. Errors are values, not exceptions.** Throw inside an action and React cancels every queued action and escalates to the nearest Error Boundary. Validation failures must be `return`ed [[5]](https://react.dev/reference/react/useActionState). This is fine, but it means your action's return type is a discriminated union you maintain yourself.

**3. Submissions serialise.** `useActionState` queues dispatches and threads `prevState` through them, so two rapid submits run back-to-back, not in parallel [[5]](https://react.dev/reference/react/useActionState). Correct for a single form; wrong for a list of 20 independently-togglable rows — that's `useOptimistic` + separate actions, or a fetcher-per-row.

**4. `useFormStatus` is child-only.** It exists so a design-system `<SubmitButton>` can be prop-less; it deliberately returns nothing in the component that renders the `<form>` [[6]](https://react.dev/reference/react-dom/hooks/useFormStatus). Use `useActionState`'s `isPending` there instead. (Minor: `Object.fromEntries(formData)` in Next.js drags in `$ACTION_`-prefixed protocol keys [[10]](https://nextjs.org/docs/app/guides/forms).)

## Decision table: native primitives vs. reach for a library

| Requirement | Native suffices? | Why |
|---|---|---|
| Submit → pending → success/error, one round-trip | ✓ | Exactly what `useActionState` is [[5]](https://react.dev/reference/react/useActionState) |
| Disable the submit button while in flight | ✓ | `isPending`, or `useFormStatus` in the button [[6]](https://react.dev/reference/react-dom/hooks/useFormStatus) |
| Optimistic list append / toggle / like | ✓ | `useOptimistic` auto-reverts on failure [[7]](https://react.dev/reference/react/useOptimistic) |
| Server-side validation errors rendered inline | ✓ ⚠ | Works, but you must hand-roll value repopulation to survive the auto-reset [[19]](https://github.com/facebook/react/issues/31649) ⭐ 246k [[20]](https://aurorascharff.no/posts/handling-form-validation-errors-and-resets-with-useactionstate/) |
| Works before hydration / without JS | ✓ ⚠ | Only from a Server Component, and error display then needs `permalink` [[4]](https://react.dev/reference/react-dom/components/form) [[5]](https://react.dev/reference/react/useActionState) |
| Basic required/email/pattern checks | ✓ | Native HTML constraint attributes — no React involved [[10]](https://nextjs.org/docs/app/guides/forms) |
| **Field-level validation on blur/change** | ✗ | No React API produces per-field errors before submit. Every keystroke-level check is yours to build |
| **Dirty / touched / isValid tracking** | ✗ | React tracks *submission* state, never *field* state. `useFormStatus` gives you the FormData in flight, not a diff against initial values [[6]](https://react.dev/reference/react-dom/hooks/useFormStatus) |
| **Field arrays** (add/remove/reorder rows) | ✗ | `FormData` flattens to repeated keys; there is no `useFieldArray` equivalent, and the auto-reset actively fights row-level state [[23]](https://blog.logrocket.com/react-hook-form-vs-react-19/) |
| **Cross-field / conditional validation, live** | ✗ | Round-tripping to the server per keystroke is not a UX |
| **Multi-step wizards, unsaved-changes guards** | ✗ | Requires dirty state, which does not exist [[23]](https://blog.logrocket.com/react-hook-form-vs-react-19/) |
| **Large forms (50+ fields) with per-field re-render control** | ✗ | Uncontrolled DOM inputs are cheap, but the moment you add live validation you're re-rendering by hand [[23]](https://blog.logrocket.com/react-hook-form-vs-react-19/) |

## The composition everyone actually ships

The mainstream 2026 pattern is not "pick one". It is: **library owns the client, Action owns the wire.** RHF (or TanStack Form / Conform) in `mode: 'onBlur'` for field state and instant feedback; a shared zod schema; then the Server Action re-validates with the same schema and `useActionState` carries the server result back [[22]](https://markus.oberlehner.net/blog/using-react-hook-form-with-react-19-use-action-state-and-next-js-15-app-router).

Be clear-eyed that this seam is **not** well-supported. The RHF community's own thread on React 19 catalogues the friction: `isPending` doesn't sync with RHF's `isSubmitting`, `useFormStatus` doesn't cooperate with RHF at all, and integrations rely on manual coordination [[21]](https://github.com/orgs/react-hook-form/discussions/11832) ⭐ 44.8k. The hybrid's own author calls it "hacky" and reports stale-`formData` bugs requiring a timestamp field to force freshness [[22]](https://markus.oberlehner.net/blog/using-react-hook-form-with-react-19-use-action-state-and-next-js-15-app-router). And a library-driven client form is, by construction, no longer progressively enhanced [[22]](https://markus.oberlehner.net/blog/using-react-hook-form-with-react-19-use-action-state-and-next-js-15-app-router) — the one framework-native primitive that *does* preserve PE while adding validation is Conform, which is built on top of Actions rather than beside them (covered in the form-library angle of this expedition).

The honest summary for an expert audience: React 19 solved the boring half of forms — the half that used to be four `useState`s and a `try/catch` — and shipped it as a browser-shaped API you can use in any React app, framework or not. It did not attempt the interesting half, has shipped nothing toward it in 18 months, and shows no sign of doing so [[3]](https://react.dev/blog/2025/10/01/react-19-2). Plan accordingly: adopt the primitives everywhere as the submission layer, and keep a form library for anything where the user spends real time inside the form before pressing the button.
