---
title: "Generating the itenium-ui API client from Forge's OpenAPI document"
date: 2026-07-13
depth: standard
format: md
topic: "Compare tools that generate a typed TypeScript API client — and ideally ready-made data-fetching hooks — from a .NET/ASP.NET Core OpenAPI (Swagger) document, in 2026. Candidates: Orval, Kubb, openapi-typescript (+ openapi-fetch), Hey API (@hey-api/openapi-ts), NSwag/NSwagStudio, openapi-generator, and the built-in Microsoft Kiota. Compare on: quality of generated types (discriminated unions, nullability, enums, DateTime handling), whether it emits TanStack Query / RTK Query / SWR hooks directly, mutation + query-key generation, MSW mock generation for tests, Zod/Valibot schema output for runtime validation and form resolvers, watch mode and CI regeneration ergonomics, monorepo (Nx) integration, maintenance health and GitHub stars, and how well it handles .NET-specific OpenAPI quirks (System.Text.Json casing, ProblemDetails error schemas, .NET 10's built-in Microsoft.AspNetCore.OpenApi document generation vs Swashbuckle). Argue the big-picture point too: if the client and its query hooks are GENERATED from the backend contract, how much does the hand-written state-management choice actually still matter? Show the concrete codegen config for the winner."
topic_raw: "Compare tools that generate a typed TypeScript API client — and ideally ready-made data-fetching hooks — from a .NET/ASP.NET Core OpenAPI (Swagger) document, in 2026. Candidates: Orval, Kubb, openapi-typescript (+ openapi-fetch), Hey API (@hey-api/openapi-ts), NSwag/NSwagStudio, openapi-generator, and the built-in Microsoft Kiota. Compare on: quality of generated types (discriminated unions, nullability, enums, DateTime handling), whether it emits TanStack Query / RTK Query / SWR hooks directly, mutation + query-key generation, MSW mock generation for tests, Zod/Valibot schema output for runtime validation and form resolvers, watch mode and CI regeneration ergonomics, monorepo (Nx) integration, maintenance health and GitHub stars, and how well it handles .NET-specific OpenAPI quirks (System.Text.Json casing, ProblemDetails error schemas, .NET 10's built-in Microsoft.AspNetCore.OpenApi document generation vs Swashbuckle). Argue the big-picture point too: if the client and its query hooks are GENERATED from the backend contract, how much does the hand-written state-management choice actually still matter? Show the concrete codegen config for the winner."
tags: [openapi, codegen, typescript, dotnet, tanstack-query, orval, nx, react]
summary: "Orval is the pick for itenium-ui: it is the only generator that emits TanStack Query hooks, query keys, MSW mocks and Zod schemas from one config — and generating the client collapses the state-management question to 'server cache + a little client state'."
citations: 30
reading_time_min: 8
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 634
issue: 2
---

> **Decision.** Use [Orval](https://orval.dev) ⭐ 6.2k (Jul 2026) with `client: 'react-query'`: it is the only generator that emits typed hooks, query-key factories, **MSW handlers** and **Zod** schemas from a single config [[5]](https://orval.dev/docs/reference/configuration/output/) — and MSW + TDD is exactly the Jest/Testing-Library setup itenium-ui already has. [Hey API](https://heyapi.dev) ⭐ 5.1k is the runner-up and the better *architectural* fit (it emits framework-agnostic `queryOptions`/`mutationOptions` instead of hooks [[7]](https://heyapi.dev/openapi-ts/plugins/tanstack-query)) — take it if you dislike one-hook-per-endpoint. Do **not** build on `openapi-fetch`/`openapi-react-query`: their maintainer put them in **maintenance mode** for 2026 [[2]](https://github.com/openapi-ts/openapi-typescript/discussions/2559). And the big-picture point: once the client *and* its query hooks are generated, "which state manager" shrinks to "which 200-line client-state store", because TanStack Query's own docs say the leftover global client state is "usually very tiny" [[17]](https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state).

## The field, 2026

The stock 2026 advice — "types only → openapi-typescript; want everything generated → Orval; want maximum control → Kubb" [[26]](https://dev.to/nyaomaru/which-openapi-codegen-should-you-choose-openapi-typescript-vs-hey-api-vs-orval-vs-kubb-100p) [[30]](https://www.pkgpulse.com/guides/orval-vs-openapi-typescript-vs-kubb-openapi-client-2026) — is still right, but its first rung (openapi-typescript + openapi-fetch) just lost its data-fetching story (below).

| Tool | ⭐ Stars | Hooks it emits | Query keys | MSW mocks | Zod / Valibot | Verdict for Forge |
|---|---|---|---|---|---|---|
| [Orval](https://orval.dev) [[4]](https://orval.dev/docs/guides/react-query/) | ⭐ 6.2k | TanStack Query, SWR, Vue/Svelte/Solid/Angular Query | ✓ per-op factory | ✓ (MSW + Faker) | ✓ Zod (auto-detects v3/v4) | **Winner** |
| [Hey API](https://heyapi.dev) [[7]](https://heyapi.dev/openapi-ts/plugins/tanstack-query) | ⭐ 5.1k | none — emits `queryOptions` / `mutationOptions` | ✓ normalized | ✓ (plugin) | ✓ Zod + Valibot | Strong runner-up |
| [Kubb](https://kubb.dev) [[3]](https://kubb.dev/docs/5.x/guide/comparison) | ⭐ 1.8k | TanStack Query (React/Vue/Svelte/Solid) | ✓ | ✓ | ✓ | Over-engineered for 2 apps |
| [openapi-typescript](https://openapi-ts.dev) [[2]](https://github.com/openapi-ts/openapi-typescript/discussions/2559) | ⭐ 8.2k | ✗ (runtime wrapper only [[24]](https://openapi-ts.dev/openapi-react-query/)) | ✗ | ✗ | ✗ | ⚠ satellites in maintenance mode |
| [NSwag](https://github.com/RicoSuter/NSwag) ⭐ 7.3k [[13]](https://codingdroplets.com/kiota-vs-nswag-vs-refitter-dotnet-typed-api-client-2026) | ⭐ 7.3k | ✗ (classes/fetch) | ✗ | ✗ | ✗ | ⚠ partial OpenAPI 3.1 |
| [Kiota](https://learn.microsoft.com/en-us/openapi/kiota/overview) ⭐ 3.8k [[14]](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/typescript) | ⭐ 3.8k | ✗ (request builders) | ✗ | ✗ | ✗ | ⚠ TS support **in preview** |
| [openapi-generator](https://openapi-generator.tech) ⭐ 26k [[15]](https://github.com/microsoft/kiota/discussions/3966) | ⭐ 26k | ✗ | ✗ | ✗ | ✗ | Java toolchain, no React story |
| [RTK Query codegen](https://redux-toolkit.js.org/rtk-query/usage/code-generation) ⭐ 11k [[16]](https://redux-toolkit.js.org/rtk-query/usage/code-generation) | ⭐ 11k | `useQuery`/`useMutation` (`hooks: true`) | tag-based, not keys | ✗ | ✗ | Only if you already chose Redux |
| [openapi-qraft](https://github.com/OpenAPI-Qraft/openapi-qraft) [[27]](https://github.com/OpenAPI-Qraft/openapi-qraft) | ⭐ 96 | proxy-based TanStack hooks | ✓ | ✗ | ✗ | Too small to bet on |

The three "enterprise" generators (NSwag ⭐ 7.3k, Kiota ⭐ 3.8k, openapi-generator ⭐ 26k) are **not in the running for a React frontend**: none of them emits a data-fetching hook, a query key, a mock handler or a Zod schema. They give you a class with methods. You would then hand-write the entire TanStack Query layer on top — which is the exact work you are trying to delete.

## The one shift that matters this year

`openapi-fetch` + `openapi-react-query` was the fashionable 2025 answer. On 2025-12-29 its maintainer announced: *"openapi-fetch, openapi-react-query, and openapi-metadata will be put into maintenance mode and won't get future updates, so we can put 100% of efforts back into openapi-typescript."* [[2]](https://github.com/openapi-ts/openapi-typescript/discussions/2559) They still work, but building a greenfield data layer on a package that is explicitly frozen is a bad trade — especially when the alternatives are *more* capable, not less. `openapi-typescript` itself (types only) remains excellent and is worth keeping in mind as the floor.

The second shift: the ecosystem is moving from *generated hooks* to *generated options objects* — `queryOptions()` you pass to `useQuery` yourself [[1]](https://saschb2b.com/blog/typesafe-api-codegen-2026). Hey API does this [[7]](https://heyapi.dev/openapi-ts/plugins/tanstack-query); Orval still generates one `useXxx` hook per path [[4]](https://orval.dev/docs/guides/react-query/). Options objects compose better (suspense, prefetch, `useQueries`) and are framework-agnostic. This is Orval's one genuine architectural weakness, and it is the only reason to pick Hey API instead.

## Type-quality on a .NET document

| .NET quirk | What lands in the OpenAPI doc | Codegen consequence |
|---|---|---|
| `System.Text.Json` casing | Schema property names are already camelCase; the doc reflects `JsonNamingPolicy` [[11]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/include-metadata?view=aspnetcore-10.0) | **Non-issue.** No `namingConvention` gymnastics needed. (⚠ MVC `AddJsonOptions` naming policies are *not* read by the built-in generator — it reads `Http.Json.JsonOptions`.) |
| Enums | No converter → `type: integer` [[11]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/include-metadata?view=aspnetcore-10.0). With `JsonStringEnumConverter` → string enum values (⚠ and even then .NET has emitted them without a type [[12]](https://github.com/dotnet/aspnetcore/issues/61303)) | Add `JsonStringEnumConverter` **on the Forge side first**. Then Orval's `override.enumGenerationType: 'enum' \| 'const'` [[6]](https://orval.dev/docs/versions/v8/) gives real names instead of `0 \| 1 \| 2`. |
| `DateTime` | `type: string, format: date-time` | Orval `override.useDates: true` converts to real `Date` objects [[5]](https://orval.dev/docs/reference/configuration/output/). |
| `[JsonPolymorphic]` / `[JsonDerivedType]` | Swashbuckle emits `oneOf` + `discriminator`. The **built-in** .NET generator emits `anyOf` with renamed derived schemas and **no discriminator object** — open, backlogged [[9]](https://github.com/dotnet/aspnetcore/issues/57982) | ⚠ **The strongest argument to stay on Swashbuckle for now.** Without a `discriminator`, no generator can emit a TS discriminated union. Hey API only shipped real discriminated-union output in 2026 [[8]](https://github.com/hey-api/hey-api/issues/3270). |
| `ProblemDetails` (every 400/500 in Forge) | Only lands as a schema if responses are annotated (`ProducesResponseType` / `TypedResults`) [[11]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/include-metadata?view=aspnetcore-10.0); Swashbuckle has misses here [[28]](https://github.com/domaindrivendev/Swashbuckle.AspNetCore/issues/2944) | Orval's custom mutator exports an `ErrorType` alias that **overrides the error type of every generated hook** [[18]](https://orval.dev/docs/guides/custom-axios/) → one line makes `error` a `ProblemDetails` everywhere. |
| Nullability | OpenAPI 3.0 `nullable: true` | ⚠ Orval v8 had a bug emitting invalid TS for nullable-only schemas [[19]](https://github.com/orval-labs/orval/issues/3149) (fixed Mar 2026). .NET 10 emits **3.1** by default [[10]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0), where nullability is `type: [string, 'null']` — Orval v8 specifically improved 3.1 compliance [[6]](https://orval.dev/docs/versions/v8/), NSwag's 3.1 support is still partial [[13]](https://codingdroplets.com/kiota-vs-nswag-vs-refitter-dotnet-typed-api-client-2026). |

### Swashbuckle vs `Microsoft.AspNetCore.OpenApi` — does it change the pick?

**No — but it changes *when* you migrate.** Swashbuckle was dropped from the .NET template but is not deprecated, and v10 supports .NET 10 [[22]](https://codewithmukesh.com/blog/dotnet-swagger-alternatives-openapi/). Forge's `AddForgeSwagger()` is fine. The two things the built-in generator buys you:

1. **OpenAPI 3.1 by default** (3.2 in .NET 11) [[10]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0) — cleaner nullability, and Orval v8 handles it [[6]](https://orval.dev/docs/versions/v8/).
2. **Build-time document generation** via `Microsoft.Extensions.ApiDescription.Server` (the `GetDocument` MSBuild step) [[10]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0) — `dotnet build` drops `forge.json` on disk, so CI never has to boot the API to regenerate the client. That is the single biggest CI ergonomics win available here.

The thing that *blocks* migration is the missing `discriminator` on polymorphic types [[9]](https://github.com/dotnet/aspnetcore/issues/57982). If Forge has (or wants) `[JsonPolymorphic]` DTOs, stay on Swashbuckle until that's fixed, or write a document transformer to re-add the discriminator. Either way, **Orval consumes both** — the generator choice is not coupled to the document-producer choice.

## Ergonomics: watch, CI, Nx

- **Watch:** `orval --watch` regenerates on spec change. In practice, better: point `input.target` at the on-disk `forge.json` emitted by `dotnet build` and let the file watcher do the rest.
- **CI drift check:** run codegen, then fail on a dirty tree. Commit the generated code (don't `.gitignore` it) so PR diffs *show* contract changes — that is the whole point of owning both sides.
- **Nx:** wire codegen as a target with `inputs: [spec]` and `outputs: [generated dir]`; Nx caches and restores the output instead of re-running it [[21]](https://nx.dev/recipes/running-tasks/configure-outputs). Make `build`/`test` for `libs/api` `dependsOn: ["api-codegen"]`.
- **Escape hatch:** `input.override.transformer` mutates the OpenAPI document *before* validation [[23]](https://orval.dev/docs/reference/configuration/input/) — the right place to patch .NET quirks (force a discriminator, rename an operationId) without forking Forge.

⚠ Known Orval sharp edges to budget for: Zod split-mode codegen bugs [[20]](https://github.com/orval-labs/orval/issues/2933), and an empty-import bug with `enumGenerationType: 'enum'` + `$ref`'d enums (open, Apr 2026) [[25]](https://github.com/orval-labs/orval/issues/3246). Neither is a blocker; both are the tax of a code generator.

## So how much does the state-management choice still matter?

Less than the debate suggests — and that is the actual finding here.

Generate the client and you have already generated: the request functions, the response types, the **query keys**, the mutations, and the MSW handlers your tests mock against. What is left for a "state manager" is: *which tab is open, is the sidebar collapsed, what's in the form before submit, the selected rows in a grid*. TanStack Query's own docs put it plainly: after moving async code into Query, "the truly globally accessible client state that is left over ... is usually very tiny" [[17]](https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state). Practitioners in 2026 phrase the failure mode as: the mistake codebases make is treating server state like client state — dumping API responses into Redux and hand-tracking loading flags [[1]](https://saschb2b.com/blog/typesafe-api-codegen-2026).

Concretely for itenium-ui:

- Choosing **Redux Toolkit** here would mean choosing **RTK Query** (its codegen does emit hooks [[16]](https://redux-toolkit.js.org/rtk-query/usage/code-generation)), and then paying for a store, slices and a tag-invalidation model to solve a problem that TanStack Query solves with a query key. RTK's codegen is also strictly weaker: no MSW, no Zod, no query-key factory.
- Choosing **TanStack Query + Orval** means the "state management library" line item in `package.json` is *TanStack Query* ⭐ 50k, and whatever tiny thing you use for UI state (`useState` first; a 1-file Zustand store when you actually need cross-tree UI state).
- The decision that *does* still matter is **runtime validation at the boundary** — generate Zod from the same spec [[29]](https://orval.dev/docs/guides/client-with-zod/) and reuse those schemas as `react-hook-form` resolvers so the form rules and the API contract cannot drift.

The contract is the source of truth. The state library is an implementation detail of the ~10% of state that isn't in the contract.

## The config

Two Orval entries: one for the client + hooks + mocks, one for Zod. All options below are from Orval's own reference [[5]](https://orval.dev/docs/reference/configuration/output/) [[23]](https://orval.dev/docs/reference/configuration/input/) [[6]](https://orval.dev/docs/versions/v8/).

`orval.config.ts` (workspace root):

```ts
import { defineConfig } from 'orval';

const spec = './openapi/forge.json'; // emitted by `dotnet build` (Microsoft.Extensions.ApiDescription.Server)

export default defineConfig({
  forge: {
    input: {
      target: spec,
      override: {
        // Patch .NET quirks before validation: e.g. re-add the polymorphic discriminator.
        transformer: './tools/orval/forge-transformer.ts',
      },
    },
    output: {
      mode: 'tags-split',
      target: 'libs/api/src/generated/forge.ts',
      schemas: 'libs/api/src/generated/model',
      client: 'react-query',
      httpClient: 'fetch',
      clean: true,
      formatter: 'prettier',
      baseUrl: { runtime: 'import.meta.env.VITE_API_URL' },
      mock: {
        generators: [
          { type: 'msw', delay: 0, baseUrl: '/api' },
          { type: 'faker', schemas: true },
        ],
      },
      override: {
        mutator: {
          path: './libs/api/src/http/forge-fetch.ts',
          name: 'forgeFetch',
        },
        useDates: true,               // DateTime -> Date
        enumGenerationType: 'enum',   // replaces v7's useNativeEnums
        query: {
          useQuery: true,
          useMutation: true,
          signal: true,
        },
        operations: {
          // ForgePagedResult endpoints -> infinite queries, keyed on ForgePageQuery.page
          listDocuments: {
            query: { useInfinite: true, useInfiniteQueryParam: 'page' },
          },
        },
      },
    },
  },

  forgeZod: {
    input: { target: spec },
    output: {
      mode: 'tags-split',
      target: 'libs/api/src/generated/zod',
      client: 'zod',
      fileExtension: '.zod.ts',
      formatter: 'prettier',
    },
  },
});
```

`libs/api/src/http/forge-fetch.ts` — the mutator that makes **every** generated hook's error a `ProblemDetails` [[18]](https://orval.dev/docs/guides/custom-axios/):

```ts
import type { ProblemDetails } from '../generated/model';

export const forgeFetch = async <T>(
  url: string,
  init: RequestInit & { params?: Record<string, unknown> },
): Promise<T> => {
  const res = await fetch(`${import.meta.env.VITE_API_URL}${url}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init.headers },
    credentials: 'include', // JWT via httpOnly cookie; swap for an Authorization header if Keycloak returns a bearer
  });

  if (!res.ok) throw (await res.json()) as ProblemDetails; // RFC 7807, guaranteed by Forge
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
};

// Orval reads these aliases to type the hooks' TError / TBody.
export type ErrorType<_ = unknown> = ProblemDetails;
export type BodyType<T> = T;
```

Nx target (`libs/api/project.json`), cached on the spec [[21]](https://nx.dev/recipes/running-tasks/configure-outputs):

```json
{
  "targets": {
    "api-codegen": {
      "executor": "nx:run-commands",
      "options": { "command": "bunx orval --config orval.config.ts" },
      "inputs": ["{workspaceRoot}/openapi/forge.json", "{workspaceRoot}/orval.config.ts"],
      "outputs": ["{projectRoot}/src/generated"],
      "cache": true
    },
    "build": { "dependsOn": ["api-codegen"] },
    "test":  { "dependsOn": ["api-codegen"] }
  }
}
```

CI drift gate:

```bash
nx run api:api-codegen --skip-nx-cache
git diff --exit-code libs/api/src/generated
```

Tests get the MSW handlers for free — `getListDocumentsMockHandler()` and friends land next to the hooks [[5]](https://orval.dev/docs/reference/configuration/output/), so a Testing-Library test mocks the *contract*, not `fetch`. That is the TDD payoff, and it is the reason Orval beats Hey API for this specific repo.
