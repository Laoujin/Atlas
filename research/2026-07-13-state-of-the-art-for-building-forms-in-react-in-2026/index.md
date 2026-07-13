---
layout: expedition
title: "Building forms in React in 2026"
date: 2026-07-13
topic: "Survey the state of the art for building forms in React in 2026 — libraries, native primitives, validation, and the patterns that hold up on hard forms. Scope: production React apps (React 19+), TypeScript-first, both SPA and framework/server-rendered (Next.js App Router, React Router 7, TanStack Start). Compare: React's native form primitives vs dedicated form libraries; controlled vs uncontrolled; type inference quality; re-render/perf cost; maturity & maintenance state."
topic_raw: "react how to do forms in 2026"
format: md
tags: [react, forms, typescript, validation, testing]
summary: "Seven angles on the 2026 React form stack: React Hook Form still wins, React's own primitives are a submission layer and not a form layer, Standard Schema made the validator swappable, and every hard pattern reduces to one question — where do the field values live."
cover: cover.svg
citations: 280
reading_time_min: 77
synthesis: true
children:
  - slug: form-library-landscape-2026
    title: "The React form-library landscape in 2026: RHF still wins, TanStack Form is the real challenger, Formik is a zombie"
    depth: expedition
    status: success
    summary: "React Hook Form (v7.81.0, 58M weekly downloads, v8 in beta) remains the default; TanStack Form 1.33.2 is the credible challenger with a framework-agnostic core and better path types but self-admitted verbosity; Conform owns progressive-enhancement forms; Formik is a zombie and React Final Form is in maintenance limbo."
    citations: 109
    reading_time_min: 18
  - slug: react-native-form-primitives
    title: "React's native form primitives in 2026: what they replace, and what they don't"
    depth: survey
    status: success
    summary: "React's form primitives froze at 19.0 and are a submission layer, not a form layer — they own pending/error/optimistic state across the network boundary, and own nothing about the fields."
    citations: 25
    reading_time_min: 9
  - slug: validation-and-schema-layer
    title: "The validation & schema layer for React forms in 2026: Zod 4, Valibot, ArkType — and why Standard Schema changed the question"
    depth: survey
    status: success
    summary: "Standard Schema v1 turned the schema library into a swappable dependency; Zod 4 stays the default, Valibot wins the client bundle, ArkType wins raw throughput — and only one of them can own your shared client/server schema."
    citations: 33
    reading_time_min: 11
  - slug: hard-forms-arrays-wizards-conditionals-performance
    title: "The hard parts of React forms in 2026: arrays, conditionals, wizards, and the render budget"
    depth: survey
    status: success
    summary: "Where the three mainstream React form libraries actually break on field arrays, conditional fields, dependent async validation, wizards, and 100+ field forms — with the API-level specifics that decide it."
    citations: 34
    reading_time_min: 12
  - slug: ui-kit-integration
    title: "Wiring form engines into React UI kits in 2026"
    depth: recon
    status: success
    summary: "The UI kits stopped picking a form engine for you: shadcn's Field, Base UI's Field and React Aria are all engine-agnostic layout/a11y primitives, and the real cost is the per-component Controller/field.state bridge you still hand-write."
    citations: 11
    reading_time_min: 4
  - slug: testing-forms
    title: "Testing React forms in 2026: which tier catches what"
    depth: survey
    status: success
    summary: "The 2026 form-testing stack is Vitest + schema unit tests + jsdom component tests, with Browser Mode as the real middle tier and Playwright reserved for the three or four flows that actually touch the network."
    citations: 32
    reading_time_min: 11
  - slug: uploads-autosave-and-unsaved-changes
    title: "Uploads, autosave and unsaved-changes guards in React forms (2026)"
    depth: survey
    status: success
    summary: "Bytes bypass your form: the browser presigns and uploads direct-to-storage while the form only carries a key — and progress still means XHR, not fetch."
    citations: 36
    reading_time_min: 12
model: "Opus 4.8"
cost_usd: "sub"
issue: 4
duration_sec: 1548
---

> **Decision.** Default stack for a new React app in 2026: **React Hook Form 7.81** [[1]](https://registry.npmjs.org/react-hook-form) + **Zod 4** [[2]](https://www.npmjs.com/package/zod) + your UI kit's engine-agnostic `Field` primitives [[3]](https://ui.shadcn.com/docs/forms), with React's `useActionState` owning only the submit round-trip [[4]](https://react.dev/reference/react/useActionState). Reach for **TanStack Form** when you need one form core across frameworks or genuinely deep typed paths [[5]](https://tanstack.com/blog/announcing-tanstack-form-v1); reach for **Conform** when the form must work before hydration [[6]](https://conform.guide/).

The single most consequential finding is a negative one: **React's form APIs stopped moving.** Everything form-related shipped in React 19.0 (Dec 2024) — `<form action>`, `useActionState`, `useFormStatus`, `useOptimistic` [[7]](https://react.dev/blog/2024/12/05/react-19) — and 19.1/19.2 added nothing to that surface [[8]](https://react.dev/blog/2025/10/01/react-19-2). What shipped is a complete *submission* layer and an empty *form* layer: no field-level validation, no dirty tracking, no field arrays. Worse, an uncontrolled form is auto-cleared after a form action even when the action returns a validation error, and the tracking issue for it was closed as not planned [[9]](https://github.com/facebook/react/issues/31649). So the 2026 shape is **library owns the client, Action owns the wire** — and the seam between them is not well supported: pairing RHF with `useActionState` in the App Router still needs a timestamp-field hack to force state through [[10]](https://markus.oberlehner.net/blog/using-react-hook-form-with-react-19-use-action-state-and-next-js-15-app-router), and RHF's maintainers have taken no official position on Server Actions at all [[11]](https://github.com/orgs/react-hook-form/discussions/11832).

Meanwhile the layer *below* the form got commoditised. **Standard Schema** v1.1 gave every validator a common `~standard` interface [[12]](https://standardschema.dev/), and the form libraries consume it: TanStack Form natively [[13]](https://tanstack.com/form/latest/docs/framework/react/guides/validation), RHF through `@hookform/resolvers`' generic `standardSchemaResolver` [[14]](https://github.com/react-hook-form/resolvers) — even Yup 1.7 and Joi 18 now implement it [[15]](https://github.com/jquense/yup). The validator is therefore a swappable dependency at the *form* boundary, but not at the ORM/RPC boundary, which is why Zod (≈224M weekly downloads — more than React itself) stays the default for one-schema-client-and-server [[2]](https://www.npmjs.com/package/zod). Note the irony for anyone bundle-shopping: Zod at ~62 kB min+gzip dwarfs every form library it is paired with [[16]](https://bundlephobia.com/api/size?package=zod@latest), and RHF vs Formik is 12.87 vs 13.12 kB [[17]](https://bundlephobia.com/api/size?package=react-hook-form@7.81.0) — the "RHF is tiny" folklore is quoting 2022 versions.

Across the two hardest angles, one question turns out to generate all the others: **where do the field values live?** RHF keeps them in mutable refs (unmounted fields keep their value), TanStack Form in an external store (unmounted fields keep value *and* stale errors, which silently blocks submit [[18]](https://github.com/TanStack/form/issues/1133)), Conform in the DOM (unmounted means deleted, unless wrapped in `PreserveBoundary` [[19]](https://conform.guide/api/react/future/PreserveBoundary)). Conditional fields, wizards, field arrays and the re-render budget are all downstream of that one choice. The same question decides uploads: because a `File` never deep-equals itself, storing the upload key rather than the `File` is what keeps dirty-tracking sane [[20]](https://react-hook-form.com/docs/useform/formstate) — and the bytes should never travel through the form anyway (Next.js caps Server Action bodies at 1 MB [[21]](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions), and `fetch` still cannot report upload progress by design [[22]](https://jakearchibald.com/2025/fetch-streams-not-for-progress/)).

Two open risks worth naming. RHF v7 is structurally incompatible with the React Compiler, and v8-beta's headline feature is fixing exactly that [[23]](https://react-hook-form.com/migrate-v7-to-v8) — so the safe default is on a beta migration path. And the App Router still has no first-party unsaved-changes guard; the request has been open since March 2023 [[24]](https://github.com/vercel/next.js/discussions/47020), while React Router 7 and TanStack Router both solved it [[25]](https://reactrouter.com/how-to/navigation-blocking). If you are choosing a router for a form-heavy app, that gap is a real input to the decision.
