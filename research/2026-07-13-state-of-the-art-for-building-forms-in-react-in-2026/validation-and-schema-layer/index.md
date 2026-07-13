---
title: "The validation & schema layer for React forms in 2026: Zod 4, Valibot, ArkType — and why Standard Schema changed the question"
date: 2026-07-13
depth: survey
format: md
topic: "Survey the validation & schema layer for React forms in 2026 — Zod (v4+) vs Valibot vs ArkType vs Yup/Joi, and the Standard Schema spec that now lets form libraries accept any of them. Compare on: bundle size / tree-shakeability, runtime validation performance, TypeScript inference quality and compile-time cost, ecosystem adoption (which form libraries and resolvers support what), error-message customisation and i18n, and coercion/transform ergonomics for form input (strings in, typed data out). Cover the pattern that matters most in practice: sharing ONE schema across client-side field validation and server-side (Server Action / API) validation, and how each library handles that. Anchor to 2026: state current major versions. Audience: expert React/TypeScript devs. Output: comparison table + a clear recommendation."
topic_raw: "react how to do forms in 2026"
tags: [react, typescript, forms, validation, zod, valibot, arktype, standard-schema]
summary: "Standard Schema v1 turned the schema library into a swappable dependency; Zod 4 stays the default, Valibot wins the client bundle, ArkType wins raw throughput — and only one of them can own your shared client/server schema."
citations: 33
reading_time_min: 9
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 670
issue: 4
---

> **Decision.** Default to **Zod 4** — it is the only one of the four whose ecosystem (drizzle-zod, tRPC, Next.js docs, AI SDKs) covers the *whole* shared-schema path from DB row to form field [[17]](https://nextjs.org/docs/app/guides/forms) [[19]](https://abrarqasim.com/blog/valibot-vs-zod-2026-i-half-migrated-and-stopped/). Reach for **Valibot** only when the schema is client-bundled and the kilobytes are load-bearing (1.37 kB vs 17.7 kB for a login form) [[8]](https://valibot.dev/guides/comparison/). Reach for **ArkType** when you validate at high volume or want TS-syntax schemas (~4× Zod v4 throughput) [[20]](https://www.pkgpulse.com/guides/zod-v4-vs-arktype-vs-typebox-vs-valibot-2026). **Yup/Joi** are maintenance-mode choices — both now speak Standard Schema, so keep them if you have them, don't start with them [[21]](https://github.com/jquense/yup) ⭐ 23.7k [[22]](https://github.com/hapijs/joi/blob/master/API.md) ⭐ 21.2k. The 2026 twist: because [Standard Schema](https://standardschema.dev) v1 is now near-universal, picking wrong is cheap at the *form-library* boundary and expensive at the *shared-schema* boundary.

## Current versions (July 2026)

| Library | Version | ⭐ Stars | npm/week | Standard Schema |
|---|---|---|---|---|
| [Zod](https://zod.dev) | 4.4.3 [[24]](https://www.npmjs.com/package/zod) | ⭐ 43.3k | ~224M | ✓ (co-author) |
| [Valibot](https://valibot.dev) | 1.4.2 [[25]](https://www.npmjs.com/package/valibot) | ⭐ 8.8k | ~14.3M | ✓ (co-author) |
| [ArkType](https://arktype.io) | 2.2.3 [[26]](https://www.npmjs.com/package/arktype) | ⭐ 7.8k | ~1.2M | ✓ (co-author) [[11]](https://arktype.io/docs/integrations) |
| [Yup](https://github.com/jquense/yup) ⭐ 23.7k | 1.7.1 [[27]](https://www.npmjs.com/package/yup) | ⭐ 23.7k | ~10.1M | ✓ [[21]](https://github.com/jquense/yup) ⭐ 23.7k |
| [Joi](https://joi.dev) | 18.2.3 [[28]](https://www.npmjs.com/package/joi) | ⭐ 21.2k | ~17.8M | ✓ (18.x, incl. JSON Schema converter) [[22]](https://github.com/hapijs/joi/blob/master/API.md) ⭐ 21.2k |
| [`@standard-schema/spec`](https://standardschema.dev) | 1.1.0 (Dec 2025) [[3]](https://www.npmjs.com/package/@standard-schema/spec) | ⭐ 3.6k | ~69M | — |

Zod out-downloads React itself (~224M vs ~153M weekly) [[24]](https://www.npmjs.com/package/zod) — mostly transitive, but it is the datapoint that explains every ecosystem gap below.

## What Standard Schema actually standardises (and what it does not)

Standard Schema is ~60 lines of TypeScript interfaces, co-authored by the Zod, Valibot and ArkType maintainers [[1]](https://standardschema.dev/). A schema exposes a `~standard` property; a consumer calls `schema["~standard"].validate(input)` and gets `{ value }` or `{ issues }` [[16]](https://next-safe-action.dev/docs/integrations/standard-schema). No adapter, no peer dependency, no `typeschema`-style shim.

Two things fall out that matter for forms:

**1. `Issue` is deliberately thin.** The spec's issue type is `{ message: string; path?: ... }` — **no error code, no params** [[2]](https://github.com/standard-schema/standard-schema/blob/main/packages/spec/README.md) ⭐ 3.6k. → a Standard-Schema-consuming form library cannot translate or re-word your errors; **i18n must happen inside the schema library**. This is the single most under-discussed consequence of the spec.

**2. Spec v1.1 (Dec 2025) added `StandardJSONSchemaV1`** [[3]](https://www.npmjs.com/package/@standard-schema/spec) — a standardised `~standard.jsonSchema.input()/.output()` converter. Joi 18 already ships it [[22]](https://github.com/hapijs/joi/blob/master/API.md) ⭐ 21.2k; it is what will eventually let one schema drive OpenAPI, LLM tool-calling and form generation without vendor-specific `toJSONSchema` calls.

## The comparison

| | Zod 4 | Valibot 1 | ArkType 2 | Yup 1 / Joi 18 |
|---|---|---|---|---|
| **Bundle (login-form schema, gzip)** | 17.7 kB [[8]](https://valibot.dev/guides/comparison/); Zod Mini 6.88 kB | **1.37 kB** [[8]](https://valibot.dev/guides/comparison/) | ~20 kB — parser + JIT ship regardless of usage [[20]](https://www.pkgpulse.com/guides/zod-v4-vs-arktype-vs-typebox-vs-valibot-2026) | Yup ~12 kB; Joi ~145 kB, Node-oriented |
| **Tree-shakeable** | ✗ classic (method chains); ✓ via `zod/mini` [[7]](https://zod.dev/packages/mini) | ✓ by design (one function per action) [[8]](https://valibot.dev/guides/comparison/) | ✗ (monolithic runtime) | ✗ |
| **Runtime (5-field object)** | ~2M ops/s [[20]](https://www.pkgpulse.com/guides/zod-v4-vs-arktype-vs-typebox-vs-valibot-2026) — 6.5–14.7× faster than Zod 3 [[4]](https://zod.dev/v4) | ~4M ops/s [[20]](https://www.pkgpulse.com/guides/zod-v4-vs-arktype-vs-typebox-vs-valibot-2026); official docs say "midfield" [[8]](https://valibot.dev/guides/comparison/) | **~8M ops/s** [[20]](https://www.pkgpulse.com/guides/zod-v4-vs-arktype-vs-typebox-vs-valibot-2026) | Yup ≈ Zod 3 tier; ArkType claims 2000× vs Yup [[23]](https://arktype.io/) |
| **TS inference** | Excellent; `z.input`/`z.output` split [[6]](https://zod.dev/api) | Excellent; `InferInput`/`InferOutput` [[9]](https://valibot.dev/guides/pipelines/) | **1:1 with TS syntax**; string-embedded types [[23]](https://arktype.io/) | Yup ✓; **Joi cannot infer values from schema** [[14]](https://github.com/react-hook-form/resolvers) ⭐ 2.3k |
| **tsc / editor cost** | `.extend()`/`.omit()` chains: 4000ms → 400ms vs v3 [[4]](https://zod.dev/v4) | Low (plain generics) | ⚠ Highest — type-level parser; big schemas need `.scope()` to amortise [[20]](https://www.pkgpulse.com/guides/zod-v4-vs-arktype-vs-typebox-vs-valibot-2026) | Low |
| **Error customisation** | Unified `error` param; precedence schema → per-parse → `z.config()` → locale [[5]](https://zod.dev/error-customization) | `setSpecificMessage` / `setSchemaMessage` / `setGlobalMessage` [[10]](https://valibot.dev/guides/internationalization/) | `arktype/config` global, `.configure()` per type (**shallow only**) [[13]](https://arktype.io/docs/configuration) | Per-rule message strings |
| **i18n** | ✓ **40+ locales** in `zod/locales`, `z.config(de())` [[5]](https://zod.dev/error-customization) | ✓ `@valibot/i18n`, modular per-language/per-action submodules [[10]](https://valibot.dev/guides/internationalization/) | ⚠ No locales package; docs: "still a topic we're working on" [[13]](https://arktype.io/docs/configuration) | Manual |
| **Coercion for form input** | `z.coerce.*`, `z.stringbool()`, `z.preprocess()` [[6]](https://zod.dev/api) | `v.pipe(v.string(), v.toNumber())` [[29]](https://valibot.dev/api/toNumber/) [[9]](https://valibot.dev/guides/pipelines/) | `type("string.numeric.parse")`, `.pipe()`, filter/narrow [[12]](https://arktype.io/docs/expressions) | Yup coerces implicitly (⚠ lossy) |
| **JSON Schema out** | `z.toJSONSchema()` [[4]](https://zod.dev/v4) | `@valibot/to-json-schema` | ✓ bidirectional [[11]](https://arktype.io/docs/integrations) | Joi 18: spec-standard converter [[22]](https://github.com/hapijs/joi/blob/master/API.md) ⭐ 21.2k |

## Ecosystem: who accepts what

| Consumer | How it takes schemas |
|---|---|
| [React Hook Form](https://react-hook-form.com) ⭐ 44.8k | Resolver-based. `@hookform/resolvers` 5.4.0 ⭐ 2.3k ships **20** resolvers **plus** a generic `standardSchemaResolver` [[14]](https://github.com/react-hook-form/resolvers) ⭐ 2.3k [[32]](https://www.npmjs.com/package/@hookform/resolvers). ⚠ ArkType's dedicated resolver is `firstError`-only; the Standard Schema one supports `firstError \| all` [[14]](https://github.com/react-hook-form/resolvers) ⭐ 2.3k |
| [TanStack Form](https://tanstack.com/form) ⭐ 6.6k | **Native Standard Schema** — pass the schema straight into `validators.onChange`. Zod, Valibot, ArkType, Effect/Schema all work adapter-free [[15]](https://tanstack.com/form/latest/docs/framework/react/guides/validation) |
| [Conform](https://conform.guide) ⭐ 2.6k | FormData-first; `parseWithZod` (and Valibot equivalent) runs **the same schema** in `onValidate` on the client and inside the Server Action [[18]](https://conform.guide/api/zod/parseWithZod) [[30]](https://conform.guide/) |
| [next-safe-action](https://next-safe-action.dev) [[31]](https://github.com/TheEdoRan/next-safe-action) ⭐ 3k | **Standard Schema at the protocol level** — `.inputSchema()` takes any compliant schema; you can even mix Zod and Valibot across actions in one project [[16]](https://next-safe-action.dev/docs/integrations/standard-schema) |
| Next.js docs | Still hard-code Zod (`safeParse` + `flatten().fieldErrors` + `useActionState`) — and the 16.2 sample still uses the **removed v3 `invalid_type_error` option** [[17]](https://nextjs.org/docs/app/guides/forms) |
| tRPC 11 / Hono / oRPC / Drizzle | Standard Schema or per-library packages; ArkType has `drizzle-arktype`, `@hono/arktype-validator` [[11]](https://arktype.io/docs/integrations) |

The honest summary: **at the form-library boundary the choice is free; at the ORM / RPC / codegen boundary it is not.** The practitioner post that best captures 2026 reality migrated two forms to Valibot for ~18 kB gzip and ~140 ms LCP, then *stopped* — because `drizzle-valibot` lagged `drizzle-zod` on a nullable JSONB column, and the schema was shared with the DB [[19]](https://abrarqasim.com/blog/valibot-vs-zod-2026-i-half-migrated-and-stopped/).

## Strings in, typed data out

Every `<input>` yields a string. Every schema library therefore has an **input type ≠ output type** problem, and this is where most 2026 form bugs live.

**Zod.** `z.coerce.number()` is the obvious move and the wrong one for forms: its **input type is `unknown`** [[6]](https://zod.dev/api), which erases the compile-time contract with the form state. Prefer `z.string().transform(Number).pipe(z.number())` or `z.preprocess`. Then wire the three-generic form:

```ts
const schema = z.object({ age: z.coerce.number().min(18) });
// RHF holds z.input, hands you z.output in onSubmit
useForm<z.input<typeof schema>, unknown, z.output<typeof schema>>({
  resolver: standardSchemaResolver(schema),
});
```

Resolvers v5 infers both sides from the schema, so the explicit generics are only needed when you wrap `useForm` yourself [[32]](https://www.npmjs.com/package/@hookform/resolvers) [[6]](https://zod.dev/api). For checkboxes/env-ish strings, `z.stringbool()` beats hand-rolled preprocessors [[6]](https://zod.dev/api).

**Valibot.** Explicit by construction: `v.pipe(v.string(), v.toNumber(), v.minValue(18))`, with `InferInput = string` and `InferOutput = number` [[9]](https://valibot.dev/guides/pipelines/) [[29]](https://valibot.dev/api/toNumber/). Verbose, but the input/output split is impossible to get wrong.

**ArkType.** Morphs: `type("string.numeric.parse")`. The `filter`/`narrow` distinction (validate *before* vs *after* the morph) is the cleanest model of the three — a `filter` rejects a 10 MB string before you parse it, a `narrow` checks the resulting number [[12]](https://arktype.io/docs/expressions).

⚠ **TanStack Form does not hand back transformed values from validators** [[15]](https://tanstack.com/form/latest/docs/framework/react/guides/validation) — the schema validates, but you re-parse in `onSubmit` if you want the coerced output. Budget for that.

⚠ **Conform inverts this**: `parseWithZod` introspects the schema and *injects* the coercion + empty-string stripping for you, so a plain `z.number()` works against raw `FormData` [[18]](https://conform.guide/api/zod/parseWithZod). It is the only one of the three that makes FormData a first-class input.

## One schema, two runtimes

The pattern that matters: define once, validate on the field *and* in the Server Action.

```ts
// schema.ts — no 'use server', no 'use client'
export const signup = z.object({
  email: z.email(),
  age: z.coerce.number().min(18),
});

// action.ts
'use server';
export async function signupAction(_prev: State, fd: FormData) {
  const r = signup.safeParse(Object.fromEntries(fd));
  if (!r.success) return { errors: z.flattenError(r.error).fieldErrors };
  // r.data is typed z.output<typeof signup>
}
```

`z.flattenError()` / `z.treeifyError()` replace v3's `.flatten()` / `.format()`; `flattenError` yields `{ formErrors, fieldErrors }` — exactly the shape `useActionState` wants to hand back to the client [[33]](https://zod.dev/error-formatting).

How each library handles the split:

- **Zod** — one file, imported by both. Server-only refinements (uniqueness checks) go in a `.superRefine()` on a `serverSignup = signup.superRefine(...)` extension; the client imports the base. ⚠ The whole schema module lands in the client bundle, so keep DB imports out of it.
- **Valibot** — same shape, but its tree-shakeability means the client only pays for the actions it actually references [[8]](https://valibot.dev/guides/comparison/). Best-in-class here **if** your server side does not depend on the Zod-only ecosystem [[19]](https://abrarqasim.com/blog/valibot-vs-zod-2026-i-half-migrated-and-stopped/).
- **ArkType** — works, but the ~20 kB runtime lands in the client bundle regardless of schema size [[20]](https://www.pkgpulse.com/guides/zod-v4-vs-arktype-vs-typebox-vs-valibot-2026); a poor trade unless the same schemas are also doing high-volume server validation.
- **Yup/Joi** — Joi is Node-oriented and cannot infer values from a schema [[14]](https://github.com/react-hook-form/resolvers) ⭐ 2.3k, which breaks the "typed data out" half of the contract. Use for server-only validation you already own.
- **next-safe-action / Conform** — remove the boilerplate above entirely and are library-agnostic (next-safe-action via Standard Schema [[16]](https://next-safe-action.dev/docs/integrations/standard-schema), Conform via `parseWithZod`/`parseWithValibot` [[18]](https://conform.guide/api/zod/parseWithZod)).

**The one-schema pattern is what pins your choice.** Standard Schema makes the *form library* indifferent; it does nothing to make `drizzle-zod`, `zod-openapi` or the AI SDK's tool schemas indifferent. Pick the library that survives contact with your *server* stack, then live with its bundle on the client — or split deliberately (Valibot client / Zod server) and accept translating at the boundary.

## Recommendation

1. **New app, shared client+server schemas → Zod 4.** The v4 rewrite closed the two historical objections (6.5–14.7× runtime, 10× less tsc thrash on `.extend()` chains, half the bundle) [[4]](https://zod.dev/v4), it has 40+ locales built in [[5]](https://zod.dev/error-customization), and everything downstream of your form — ORM, RPC, OpenAPI, LLM tools — assumes it.
2. **Bundle-critical, client-only schemas (edge, mobile web, embeddable widget) → Valibot.** 1.37 kB vs 17.7 kB is not a rounding error [[8]](https://valibot.dev/guides/comparison/), and it pairs cleanly with Conform and TanStack Form. Use `zod/mini` [[7]](https://zod.dev/packages/mini) instead only if you refuse a second library — its DX is worse than Valibot's for the same win.
3. **High-throughput validation or TS-native schema syntax → ArkType.** ~4× Zod v4 [[20]](https://www.pkgpulse.com/guides/zod-v4-vs-arktype-vs-typebox-vs-valibot-2026). ⚠ Budget for compile-time cost on large schemas and for rolling your own i18n [[13]](https://arktype.io/docs/configuration).
4. **Yup / Joi → don't start here.** Both now implement Standard Schema [[21]](https://github.com/jquense/yup) ⭐ 23.7k [[22]](https://github.com/hapijs/joi/blob/master/API.md) ⭐ 21.2k, which means an existing Yup/Joi codebase can adopt TanStack Form or next-safe-action *without* rewriting schemas. That is a migration lifeline, not a reason to pick them.
5. **Whatever you pick, do i18n inside the schema library.** The Standard Schema `Issue` carries only `message` + `path` [[2]](https://github.com/standard-schema/standard-schema/blob/main/packages/spec/README.md) ⭐ 3.6k — a form library downstream of the spec has nothing left to translate with.
