---
title: "Which OpenAPI client generator for itenium-ui in 2026: Orval vs Hey API vs Kiota vs openapi-typescript"
date: 2026-07-14
depth: standard
format: md
topic: "Decision framework: which OpenAPI client generator to adopt for `itenium-ui` in 2026 — Orval vs Hey API vs Kiota vs openapi-typescript + openapi-fetch. Scope: generating a typed TanStack Query client from a .NET 10 Swagger/OpenAPI document using ProblemDetails for errors. Compare: one-hook-per-endpoint (Orval) vs composable queryOptions objects (the direction TanStack itself is drifting); TypeScript inference quality; ProblemDetails error typing; codegen ergonomics in an Nx 21 monorepo and CI; mutation/optimistic-update support; maintenance health and lock-in."
topic_raw: "which OpenAPI client generator for itenium-ui in 2026 — Orval, Hey API, Kiota, or openapi-typescript + openapi-fetch? Generating a typed TanStack Query client from a .NET 10 Swagger/OpenAPI document using ProblemDetails for errors. Compare: one-hook-per-endpoint (Orval) vs composable queryOptions objects (the direction TanStack itself is drifting); TypeScript inference quality; ProblemDetails error typing; codegen ergonomics in an Nx 21 monorepo and CI; mutation/optimistic-update support; maintenance health and lock-in."
tags: [openapi, typescript, tanstack-query, react, dotnet, codegen, nx]
summary: "openapi-typescript + openapi-fetch + openapi-react-query wins on every axis that matters for a .NET 10 ProblemDetails backend; Hey API is the runner-up; Orval fights TanStack's direction and Kiota's TypeScript is still in preview."
citations: 30
reading_time_min: 10
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
issue: 5
duration_sec: 1593
---

> **Decision.** Take **openapi-typescript + openapi-fetch + openapi-react-query**. It is the only option where `useQuery().error` is *already* your `ProblemDetails` union with no wiring, where query keys are `DataTag`-branded so `setQueryData` is typed for optimistic updates [[21]](https://github.com/openapi-ts/openapi-typescript/blob/main/packages/openapi-react-query/src/index.ts), and where nothing but a `.d.ts` file lands in the diff. **Hey API** is a close runner-up and the better pick if you want named SDK functions, generated Zod validators, or a framework-agnostic client — it emits real TanStack `queryOptions()` objects and types the error channel from the spec [[13]](https://github.com/hey-api/hey-api/blob/main/examples/openapi-ts-tanstack-react-query/src/client/%40tanstack/react-query.gen.ts)[[14]](https://github.com/hey-api/hey-api/blob/main/packages/openapi-ts/src/plugins/%40tanstack/query-core/shared/use-type.ts). **Orval** is a viable-but-backward choice: it still hand-rolls option objects instead of calling TanStack's `queryOptions` helper, and its suspense options don't typecheck [[7]](https://github.com/orval-labs/orval/issues/1788). **Kiota is a reject** — Microsoft's own README marks TypeScript as *preview* [[22]](https://github.com/microsoft/kiota), and it has no TanStack story at all.

## First: your OpenAPI document is the real problem

Every generator below inherits whatever `Microsoft.AspNetCore.OpenApi` hands it. Fix the document before you pick a tool, or you will blame the tool for the backend's output.

.NET 10 defaults to **OpenAPI 3.1** with JSON Schema draft 2020-12 [[1]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0). That's good news — all four candidates read 3.1, including Orval's type-array nullability handling [[11]](https://github.com/orval-labs/orval/issues/1817) — but it comes with two live defects:

**Numbers come out as `number | string`.** ASP.NET Core's default `JsonNumberHandling.AllowReadingFromString` makes the schema honest about what it will *accept*, so an `int` is emitted as `"type": ["integer", "string"]` with a regex `pattern` [[2]](https://svrooij.io/2025/12/19/openapi-dotnet-10-number-quirk/). Every TypeScript generator faithfully reproduces that as a union, and your whole model tree rots. Fix it at the source:

```csharp
builder.Services.ConfigureHttpJsonOptions(o =>
    o.SerializerOptions.NumberHandling = JsonNumberHandling.Strict);
```

**`ProblemDetails` extensions are invisible.** The generated schema carries only the five RFC 7807 fields and no `additionalProperties`, and the ASP.NET team closed the report as *answered* rather than fixing it [[3]](https://github.com/dotnet/aspnetcore/issues/62099). So `problem.Extensions["traceId"]` will never appear in any generated type — no matter which tool you choose. If you rely on extensions, add an `IOpenApiSchemaTransformer` that widens the schema, or declare a custom error type and `ProducesProblem<MyProblem>`.

What *does* work out of the box: `ProducesProblem` / `ProducesValidationProblem` / `TypedResults.Problem` attach the response metadata [[1]](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0), which is the hook every generator's error typing hangs off. **Declare your 4xx/5xx responses on every endpoint** — an undeclared error response means every tool below falls back to `Error` or `unknown`.

## The shape question: hooks vs queryOptions

You framed this correctly. TanStack's own maintainer no longer recommends a wrapper hook per endpoint: *"There's nothing wrong with calling `useQuery` in your component directly"*, and *"Separating QueryKey from QueryFunction was a mistake"* [[4]](https://tkdodo.eu/blog/the-query-options-api). `queryOptions()` is the type-safe unit that works in `useQuery`, `useSuspenseQuery`, `prefetchQuery`, `queryClient.setQueryData` and router loaders alike [[5]](https://tanstack.com/query/v5/docs/framework/react/reference/queryOptions).

This is not a stylistic quibble — it decides what you can *do*:

Orval hands you a hook and only a hook [[6]](https://orval.dev/docs/guides/react-query/) — to prefetch in a router loader or suspend, you rebuild the options by hand. Hey API [[12]](https://heyapi.dev/openapi-ts/plugins/tanstack-query) and openapi-react-query [[20]](https://openapi-ts.dev/openapi-react-query/) hand you an object that goes anywhere TanStack accepts one:

```ts
// Orval
const { data } = useGetPetById(petId);

// Hey API — a real queryOptions() object
const { data } = useQuery(getPetByIdOptions({ path: { petId } }));
queryClient.prefetchQuery(getPetByIdOptions({ path: { petId } }));   // same object, works

// openapi-react-query — same shape, no codegen
const { data } = useQuery($api.queryOptions('get', '/pets/{petId}', { params: { path: { petId } } }));
```

Orval does emit `getXQueryOptions()` functions, but they are hand-typed `UseQueryOptions` literals rather than calls to TanStack's helper — which is why its generated suspense options **do not typecheck against `useSuspenseQuery`**. The issue asking Orval to adopt the helper is open and unassigned [[7]](https://github.com/orval-labs/orval/issues/1788). Hey API, by contrast, literally `import { queryOptions } from '@tanstack/react-query'` in its generated file [[13]](https://github.com/hey-api/hey-api/blob/main/examples/openapi-ts-tanstack-react-query/src/client/%40tanstack/react-query.gen.ts).

Adopting Orval today means adopting the pattern TanStack is drifting away from, and betting that Orval catches up.

## ProblemDetails error typing — the deciding axis

| Tool | What `error` is typed as | How it gets there |
|---|---|---|
| **openapi-fetch / openapi-react-query** | the exact union of declared 4xx/5xx bodies | `{ data, error }` discriminated union [[19]](https://openapi-ts.dev/openapi-fetch/); the `queryFn` throws the parsed body, and `TError` is inferred from it [[21]](https://github.com/openapi-ts/openapi-typescript/blob/main/packages/openapi-react-query/src/index.ts) |
| **Hey API** | the operation's generated `XError` type | `useTypeError()` resolves the operation's error symbol, falling back to `DefaultError` only when the spec declares none [[14]](https://github.com/hey-api/hey-api/blob/main/packages/openapi-ts/src/plugins/%40tanstack/query-core/shared/use-type.ts) |
| **Orval** | `ErrorType<T>` — whatever your mutator says | you hand-write `export type ErrorType<E> = AxiosError<E>` in the custom mutator [[8]](https://orval.dev/docs/guides/custom-axios/) |
| **Kiota** | thrown `ApiError` subclasses | error mapping, caught in `try/catch`; no TanStack integration to carry the type |

The openapi-fetch stack's advantage is structural: because the error is a *value* in a discriminated union rather than a thrown `unknown`, TypeScript narrows it for free. `HttpValidationProblemDetails` (with `errors: Record<string, string[]>`) and plain `ProblemDetails` land as a proper union you can switch on by `status`.

Two caveats to keep honest:

- ⚠ openapi-react-query throws the **raw body**, not an `Error` instance [[21]](https://github.com/openapi-ts/openapi-typescript/blob/main/packages/openapi-react-query/src/index.ts). `error.detail` works; `error.message` does not. A network failure still surfaces as a `TypeError` that the types don't predict — narrow before you trust it.
- Hey API used to stringify the error body into `Error.message` under `throwOnError`, which threw the typing away at runtime; reported and fixed [[15]](https://github.com/hey-api/openapi-ts/issues/1029). Worth a smoke test on your own spec.

Orval's error typing works, but it is *your* wiring, not the generator's — the `ErrorType<E>` alias is something you maintain in the mutator file.

## Comparison

| | [openapi-typescript](https://openapi-ts.dev) ⭐ 8.2k | [Hey API](https://heyapi.dev) ⭐ 5.1k | [Orval](https://orval.dev) ⭐ 6.2k | [Kiota](https://learn.microsoft.com/en-us/openapi/kiota/overview) ⭐ 3.8k |
|---|---|---|---|---|
| Client shape | `queryOptions` + hooks (runtime wrapper) [[20]](https://openapi-ts.dev/openapi-react-query/) | `queryOptions` / `mutationOptions` / `queryKey` (generated) [[12]](https://heyapi.dev/openapi-ts/plugins/tanstack-query) | one hook per endpoint [[6]](https://orval.dev/docs/guides/react-query/) | fluent request builders [[24]](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/typescript) |
| Uses TanStack's `queryOptions()` helper | ✓ | ✓ [[13]](https://github.com/hey-api/hey-api/blob/main/examples/openapi-ts-tanstack-react-query/src/client/%40tanstack/react-query.gen.ts) | ✗ [[7]](https://github.com/orval-labs/orval/issues/1788) | ✗ (no TanStack layer) |
| ProblemDetails typed on `error` | ✓ automatic | ✓ automatic [[14]](https://github.com/hey-api/hey-api/blob/main/packages/openapi-ts/src/plugins/%40tanstack/query-core/shared/use-type.ts) | ✓ via hand-written mutator [[8]](https://orval.dev/docs/guides/custom-axios/) | ✓ but you hand-carry it |
| Typed `setQueryData` (optimistic) | ✓ `DataTag` [[21]](https://github.com/openapi-ts/openapi-typescript/blob/main/packages/openapi-react-query/src/index.ts) | ✓ `setQueryData` helper generated | partial — key fn only | ✗ |
| `useSuspenseQuery` | ✓ [[20]](https://openapi-ts.dev/openapi-react-query/) | ✓ | ⚠ options don't typecheck [[7]](https://github.com/orval-labs/orval/issues/1788) | ✗ |
| Generated code in the diff | types only (one `.d.ts`) [[18]](https://openapi-ts.dev/introduction) | SDK + types + query layer | hooks + types (+ mocks) | full client tree |
| Runtime weight | 6 kB + ~1 kB [[19]](https://openapi-ts.dev/openapi-fetch/)[[20]](https://openapi-ts.dev/openapi-react-query/) | small fetch client | axios or fetch | Kiota abstractions + adapter |
| Mocks / validators | ✗ | Zod + 20+ plugins [[16]](https://github.com/hey-api/hey-api) | MSW + Faker [[9]](https://orval.dev/docs/reference/configuration/output/) | ✗ |
| Installable via bun/npm | ✓ | ✓ | ✓ | ✗ binary / Docker / `dotnet tool` [[25]](https://learn.microsoft.com/en-us/openapi/kiota/install) |
| npm downloads / week | 5.97M (`openapi-fetch`) [[28]](https://api.npmjs.org/downloads/point/last-week/openapi-fetch) | 2.88M [[29]](https://api.npmjs.org/downloads/point/last-week/@hey-api/openapi-ts) | 1.29M [[29]](https://api.npmjs.org/downloads/point/last-week/@hey-api/openapi-ts) | 47.9k (`kiota-bundle`) [[29]](https://api.npmjs.org/downloads/point/last-week/@hey-api/openapi-ts) |
| Maturity | stable | stable, MIT [[16]](https://github.com/hey-api/hey-api) | stable ⚠ RCE fixed in 7.20.0/8.0.3 [[10]](https://nvd.nist.gov/vuln/detail/CVE-2026-24132) | **TypeScript = preview** [[22]](https://github.com/microsoft/kiota) |

## Why Kiota is out

Kiota is the natural instinct for a .NET shop, and it's the wrong instinct here. Microsoft's maturity ladder defines *Preview* as "at or near the level of stable but **isn't being used to generate production API clients**" [[23]](https://learn.microsoft.com/en-us/openapi/kiota/support), and the README marks TypeScript at exactly that level [[22]](https://github.com/microsoft/kiota). The runtime libraries the generated client depends on live in a repo with **⭐ 61** [[26]](https://github.com/microsoft/kiota-typescript), and the bundle pulls ~48k weekly downloads against openapi-fetch's ~6M.

Beyond adoption, the shape is wrong for React: Kiota gives you `client.posts.byPostId(id).get()` behind a request adapter and an auth provider [[24]](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/typescript). There is no TanStack integration — you would hand-write a `queryOptions` wrapper and a query key for every endpoint, which is precisely the work you're trying to generate away. And it doesn't install from npm: your Nx CI job has to fetch a binary, run Docker, or install the .NET SDK [[25]](https://learn.microsoft.com/en-us/openapi/kiota/install).

## Nx 21 and CI

All three viable options are npm packages driven by one config file, so the Nx wiring is the same: a cacheable `generate-api` target with the OpenAPI document as its only input and the generated directory as its output. Cache hits are free; the spec changing is the only thing that reruns it.

The choice that actually matters is **generated code in git, or not**. Commit it — the diff is your review surface for backend changes, editors resolve types with no build step, and CI just verifies. Then guard drift with either a plain `bunx orval && git diff --exit-code` step, or Nx's first-class equivalent: register the codegen as a sync generator and let **`nx sync:check`** fail the build when the client is stale [[27]](https://nx.dev/docs/reference/nx-commands).

This is where the types-only approach quietly wins. openapi-typescript emits a **single `.d.ts`** [[18]](https://openapi-ts.dev/introduction). A backend change produces a diff a reviewer can actually read, instead of a few thousand lines of regenerated hooks.

## Mutations and optimistic updates

The optimistic-update path is `onMutate` → `queryClient.setQueryData(key, updater)` → rollback in `onError`. Its ergonomics come down to two things: is the key exposed, and is `setQueryData` typed?

- **openapi-react-query**: the key is `['get', '/pets/{petId}', init]`, branded `DataTag<key, data, error>` [[21]](https://github.com/openapi-ts/openapi-typescript/blob/main/packages/openapi-react-query/src/index.ts) — so `setQueryData` infers the data type *and* the error type with no generics. Invalidating by path prefix is a plain array prefix.
- **Hey API**: generates `xQueryKey()` plus `setQueryData`/`getQueryData` helpers. The key is a bespoke object (`[{ _id, baseUrl, path, query, tags }]`), so prefix invalidation runs through its tags mechanism rather than the array-prefix idiom you already know.
- **Orval**: gives you `getXQueryKey()` and the raw fetcher; `setQueryData` typing is yours to write.

## Lock-in and the escape hatch

Rank by cost-of-walking-away:

**openapi-typescript** is the cheapest exit by a wide margin. The `.d.ts` is the asset; `openapi-fetch` and `openapi-react-query` are ~7 kB of wrapper on top. Drop the TanStack binding and your types survive untouched. All three ship from one monorepo under the `openapi-ts` org [[30]](https://github.com/openapi-ts/openapi-typescript), so the binding isn't an orphan side-project — though note `openapi-react-query` is the least-used piece of the stack at ~311k weekly downloads against `openapi-fetch`'s ~6M.

**Hey API** is MIT, has real corporate usage (Vercel, PayPal, AWS), and its hosted Platform is strictly optional — `input` takes a file path or URL just as happily as a `hey-api/*` registry reference [[16]](https://github.com/hey-api/hey-api)[[17]](https://heyapi.dev/openapi-ts/get-started). Lock-in is the generated SDK call sites, which is real but mechanical to replace.

**Orval** is healthy (⭐ 6.2k, actively pushed) and its MSW + Faker mock generation is a genuine feature nobody else matches [[9]](https://orval.dev/docs/reference/configuration/output/). ⚠ It also shipped an RCE: CVE-2026-24132 (CVSS 7.7) let a malicious OpenAPI document inject TypeScript into generated mock files, fixed in 7.20.0 / 8.0.3 [[10]](https://nvd.nist.gov/vuln/detail/CVE-2026-24132). With a first-party .NET spec the threat model barely applies — but pin the patched version.

## Recommendation

For `itenium-ui`: **`openapi-typescript` + `openapi-fetch` + `openapi-react-query`**, with `JsonNumberHandling.Strict` and `ProducesProblem<T>` on every endpoint on the .NET side. You get the composable-`queryOptions` shape TanStack is converging on, a `ProblemDetails` union on `error` that needs zero wiring, typed optimistic updates via `DataTag`, and a one-file diff per backend change.

Switch to **Hey API** if any of these become true: you want generated Zod validators at the boundary, you want MSW-style mocks without adopting Orval, or you want the same client consumed from something other than React. It costs you a larger generated tree and a bespoke query-key shape; it costs you nothing on error typing.

Pick **Orval** only if generated MSW + Faker mocks are the requirement that outranks everything else — and accept that you're adopting the one-hook-per-endpoint model that TanStack's own maintainer has moved on from [[4]](https://tkdodo.eu/blog/the-query-options-api), with suspense support that doesn't currently typecheck [[7]](https://github.com/orval-labs/orval/issues/1788).
