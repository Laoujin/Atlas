---
title: "The hard parts of React forms in 2026: arrays, conditionals, wizards, and the render budget"
date: 2026-07-13
depth: survey
format: md
topic: "Survey the hard parts of React forms in 2026 — the cases that break naive implementations: field arrays and nested/reorderable repeating groups, dynamic and conditional fields and what happens to values on unmount, cross-field dependencies and dependent async validation, multi-step wizards, and re-render behaviour on large forms — compared across React Hook Form, TanStack Form and Conform."
topic_raw: "react how to do forms in 2026"
tags: [react, forms, react-hook-form, tanstack-form, conform, performance, typescript]
summary: "Where the three mainstream React form libraries actually break on field arrays, conditional fields, dependent async validation, wizards, and 100+ field forms — with the API-level specifics that decide it."
citations: 34
reading_time_min: 10
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 804
issue: 4
---

> **TL;DR.** The three libraries differ on exactly one question that decides everything else: *where do field values live?* RHF keeps them in a mutable ref outside React and preserves them when a field unmounts [[1]](https://react-hook-form.com/docs/usefieldarray); TanStack Form keeps them in an external store and also preserves them — including stale validation errors that will block your submit [[18]](https://github.com/TanStack/form/issues/1133); Conform reads them from the DOM, so an unmounted field is a *deleted* field unless you wrap it in `PreserveBoundary` [[23]](https://conform.guide/api/react/future/PreserveBoundary). Pick RHF for big flat forms, TanStack Form for deeply dynamic ones, Conform when the server is the validator — then budget for the specific sharp edges below.

Versions as of this writing: [React Hook Form](https://react-hook-form.com) 7.81.0 ⭐ 44.8k (Jul 2026), with a v8 beta in flight [[29]](https://github.com/react-hook-form/react-hook-form); [TanStack Form](https://tanstack.com/form) 1.30.x ⭐ 6.6k (Jul 2026) [[30]](https://github.com/TanStack/form); [Conform](https://conform.guide) 1.19.4 ⭐ 2.6k (Jun 2026) [[31]](https://github.com/edmundhung/conform).

---

## 1. Field arrays and repeating groups

**The invariant nobody gets right first time: rows must be keyed by identity, not index.** RHF is the only one that hands you that identity. `useFieldArray` generates a per-row `id` and the docs are blunt about it — `key={field.id}` correct, `key={index}` incorrect [[1]](https://react-hook-form.com/docs/usefieldarray). Conform gives you `task.key` from field metadata [[19]](https://conform.guide/complex-structures). TanStack Form gives you nothing: its own array guide renders rows with ``<form.Field key={i} name={`people[${i}].name`}>`` [[9]](https://tanstack.com/form/latest/docs/framework/react/guides/arrays), and index-keying is the direct cause of issue #957, where removing item 2 from `[1,2,3,4]` in a conditionally-rendered form yields `[1,3,4,4]` [[16]](https://github.com/TanStack/form/issues/957). If you use TanStack arrays with reordering, you must carry your own `id` field on each row and key on that.

| | React Hook Form | TanStack Form | Conform |
|---|---|---|---|
| Mutators | `append` `prepend` `insert` `swap` `move` `update` `replace` `remove` [[1]](https://react-hook-form.com/docs/usefieldarray) | `pushValue` `insertValue` `removeValue` `swapValues` `moveValue` `replaceValue` `clearValues` [[9]](https://tanstack.com/form/latest/docs/framework/react/guides/arrays) | intents: `form.insert` `form.remove` `form.reorder` `form.update` via `getButtonProps()` [[20]](https://conform.guide/intent-button) |
| Stable row key | ✓ `field.id` (v7) → `field.key` (v8) [[4]](https://react-hook-form.com/migrate-v7-to-v8) | ✗ docs key by index [[9]](https://tanstack.com/form/latest/docs/framework/react/guides/arrays) | ✓ `field.key` [[19]](https://conform.guide/complex-structures) |
| Path syntax | dot only — `test.0.name`; `test[0].name` ✗ [[3]](https://react-hook-form.com/docs/useform/register) | bracket — `people[0].name` [[9]](https://tanstack.com/form/latest/docs/framework/react/guides/arrays) | bracket — `tasks[0].content` [[19]](https://conform.guide/complex-structures) |
| Arrays of primitives | ✗ v7 ("does not support flat field array"); ✓ v8 beta [[1]](https://react-hook-form.com/docs/usefieldarray)[[4]](https://react-hook-form.com/migrate-v7-to-v8) | ✓ | ✓ |
| Nested arrays | one `useFieldArray` per level, name cast `as 'test.0.keyValue'` [[2]](https://deepwiki.com/react-hook-form/react-hook-form/5.3-advanced-field-array-patterns) | `mode="array"` field nested inside a row [[9]](https://tanstack.com/form/latest/docs/framework/react/guides/arrays) | `getFieldList()` → `getFieldset()` → `getFieldList()` [[19]](https://conform.guide/complex-structures) |
| Works without JS | ✗ | ✗ | ✓ (submitter-encoded intents) [[20]](https://conform.guide/intent-button) |

**RHF's non-obvious rules**, all from the official page [[1]](https://react-hook-form.com/docs/usefieldarray): `append({})` is invalid — you must pass every default; two `useFieldArray` hooks may not share a `name`; and *don't stack mutations* (`append(); remove(0);` in one handler is a bug — do the second in a `useEffect`). Nested parent operations propagate to child arrays automatically through `control._subjects.array` [[2]](https://deepwiki.com/react-hook-form/react-hook-form/5.3-advanced-field-array-patterns).

**Drag-and-drop over *nested* arrays has a specific trap.** The common pattern of stashing a nested array's `move` in a ref breaks: appending another nested array overwrites the ref, and only the last array reorders. Keep a *list* of reorder callbacks, one per nested array instance [[32]](https://github.com/orgs/react-hook-form/discussions/9672).

**Conform's trap is the inverse of RHF's.** Its rows are re-mounted by `key` on every intent, which is what makes reorder correct — but a row containing a *controlled* widget wired through `useInputControl` will have its value reset whenever that key changes, i.e. on every insert/remove/reorder [[28]](https://conform.guide/api/react/useInputControl). Native inputs are unaffected; custom Select/Combobox components in a sortable list are not.

**v8 changes the field-array contract.** `id` → `key`, `keyName` removed, and `setValue("items", next)` no longer updates a field array — use `replace(next)` [[4]](https://react-hook-form.com/migrate-v7-to-v8). Any codebase with `keyName` or `setValue` on an array path has a migration to schedule.

---

## 2. Conditional fields, and what happens to the value on unmount

This is the single biggest behavioural fork, and it is not a preference — it falls out of the storage model.

| Default on unmount | Consequence |
|---|---|
| **RHF: value kept** (`shouldUnregister: false` is the default) | Hidden fields still submit. The "isDeveloper is false but favoriteLanguage is still in the payload" bug. Fix per-field with `register(name, { shouldUnregister: true })` [[3]](https://react-hook-form.com/docs/useform/register). |
| **TanStack: value + meta + errors kept** | Worse: a field that unmounts *while invalid* leaves its error in the store and silently blocks `handleSubmit` [[18]](https://github.com/TanStack/form/issues/1133). Escape hatch: `form.deleteField(name)` [[17]](https://github.com/TanStack/form/issues/502). |
| **Conform: value dropped** (values are read from the DOM) | The opposite failure: navigate away from step 1 and step 1's answers are gone. Fix: `<PreserveBoundary name="step-1">` from `@conform-to/react/future` [[23]](https://conform.guide/api/react/future/PreserveBoundary). |

⚠ **The RHF collision to know about:** `shouldUnregister: true` — the fix for conditional fields — is *explicitly unsupported inside `useFieldArray`*: "Field array relies on inputs being mounted and unmounted to manage its internal state — enabling `shouldUnregister` causes newly added fields to be unregistered on re-render, so their values are lost" [[1]](https://react-hook-form.com/docs/usefieldarray). `register`'s own docs repeat the warning [[3]](https://react-hook-form.com/docs/useform/register). So a repeating group whose rows contain conditional sub-fields cannot use the global switch. You strip the dead branches in a `handleSubmit` transform, or you model the row as a discriminated union and let Zod's `.transform()` drop them.

**Conditional *validation*** (not visibility) is cleanest in Conform: because the schema is rebuilt per submission-intent, `z.discriminatedUnion` on a "type" field just works, and there is no client-side state to keep in sync [[21]](https://conform.guide/api/zod/conformZodMessage). In RHF, dynamic schemas mean either swapping the resolver (which re-validates everything) or a `superRefine` that reads sibling values. In TanStack Form, put the branch in a form-level validator that writes errors onto specific paths: `{ form: 'Invalid data', fields: { 'details.email': 'An email is required' } }` [[10]](https://tanstack.com/form/latest/docs/framework/react/guides/validation).

---

## 3. Cross-field dependencies and dependent async validation

**Cross-field, synchronous.** RHF: `register("confirm", { deps: "password" })` — "validation will be triggered for the dependent inputs", but note it is "only limited to register api not trigger" [[3]](https://react-hook-form.com/docs/useform/register), so a `trigger()` from a wizard's Next button will *not* fan out to dependents. TanStack Form: `validators={{ onChangeListenTo: ['password'], onChange: ({value, fieldApi}) => ... }}` — declarative and symmetric, with the documented footgun that A↔B mutual listening loops forever [[11]](https://tanstack.com/form/latest/docs/framework/react/guides/linked-fields). Conform: no primitive needed — the whole schema re-runs on each validation intent [[22]](https://conform.guide/validation).

**Async "username taken" is where naive code dies.** The lifecycle is debounce → cancel in-flight → discard stale responses → per-field (not whole-form) revalidation → an `isValidating` flag that doesn't flicker.

- **TanStack Form is the only one with this built in**: `asyncDebounceMs={500}` per field (or `onChangeAsyncDebounceMs` per validator), sync validators gate the async one so you don't hit the network on obviously-invalid input, and `asyncAlways: true` overrides that [[10]](https://tanstack.com/form/latest/docs/framework/react/guides/validation). Their comparison table scores RHF ❓ on this row, which is honest [[26]](https://tanstack.com/form/latest/docs/comparison).
- **RHF has no built-in debounce.** Community consensus after several rounds of pain: do *not* hide the remote check inside the Zod resolver — "keep Zod for sync validation… use `setError` / `clearErrors` for the remote result", driving it from `useWatch` on that one field plus a debounce and an `AbortController` [[8]](https://github.com/orgs/react-hook-form/discussions/11942). Putting it in an async resolver is what produces the stale-error and stuck-`isValidating` reports.
- **Conform deliberately has no client async validation.** It "falls back to server validation when needed" [[22]](https://conform.guide/validation). The mechanism is worth copying even if you don't use Conform: the schema is a function of the submission `intent`. Fields not targeted by the intent emit `conformZodMessage.VALIDATION_SKIPPED` (reuse the previous result — no re-checking every field on every keystroke); a field whose async check isn't available on the client emits `VALIDATION_UNDEFINED`, which makes the client defer to the server, where the same schema runs under `parseWithZod(formData, { schema: (intent) => createSchema(intent, options), async: true })` [[21]](https://conform.guide/api/zod/conformZodMessage). One schema, no duplicated uniqueness endpoint, no client/server drift.

---

## 4. Multi-step wizards

The question is only ever "where does step state live", and each library answers differently.

**RHF — official answer: outside RHF.** The Advanced Usage wizard recipe uses one `useForm` *per route* and an external store (`little-state-machine`) as the source of truth across steps [[6]](https://react-hook-form.com/advanced-usage); community variants swap in Zustand + `persist` for refresh survival. The single-`useForm` variant also works and is more common in practice: keep all steps under one `FormProvider`, define a per-step schema object, and gate the Next button on `await trigger(stepFields)`, relying on the default `shouldUnregister: false` to hold values for unmounted steps [[34]](https://github.com/orgs/react-hook-form/discussions/4028). Some tutorials go further and drop per-step validation entirely, validating only on a final confirmation screen [[33]](https://claritydev.net/blog/advanced-multistep-forms-with-react). Note the interaction with §3: `trigger()` does not honour `deps` [[3]](https://react-hook-form.com/docs/useform/register), so cross-step dependent rules need an explicit re-trigger.

**TanStack Form — first-class.** `FormGroup` / `withFieldGroup` give each step its own validators and an `onGroupSubmit`, while values stay in the one parent store: advance the step when the group validates, and only call `form.handleSubmit()` at the end [[13]](https://tanstack.com/form/latest/docs/framework/react/guides/form-groups). This is the cleanest wizard model of the three — with the caveat from §2 that an abandoned branch's stale errors stay in the store [[18]](https://github.com/TanStack/form/issues/1133).

**Conform — the wizard is a server concern.** Steps are just conditionally rendered fieldsets of one form; because values live in the DOM they vanish on step change, so each step's fields go inside a named `PreserveBoundary` [[23]](https://conform.guide/api/react/future/PreserveBoundary), shipped in v1.17.0 [[24]](https://github.com/edmundhung/conform/releases). Per-step validation is the `validate` intent scoped to that step's field names [[20]](https://conform.guide/intent-button). Refresh-persistence is whatever your framework's session/loader gives you — which is the point of the library.

None of the three persists to `localStorage` for you. That is your `subscribe()` (RHF, renderless [[5]](https://react-hook-form.com/docs/useform/subscribe)) or `form.Subscribe` / store subscription (TanStack) plus a debounced write.

---

## 5. Re-renders and the 100+ field budget

**RHF** is uncontrolled: values sit in refs, inputs update via the DOM, nothing re-renders on keystroke. The failure mode is *subscription placement*, not the library. The canonical 100+-field bug report gets this answer from the maintainer: "Changing a field updates different form states like `dirtyFields`… which would cause your whole form to re-render due to that update subscription you made in the parent component" [[7]](https://github.com/orgs/react-hook-form/discussions/7810). Rules that follow: read `formState` in a leaf via `useFormState`, never in the form root; prefer `register` over `Controller`/`useController` (every controlled wrapper is a re-render per keystroke by construction); `subscribe()` when you need values but not a render [[5]](https://react-hook-form.com/docs/useform/subscribe); `FormProvider` re-renders its subtree, so `memo()` the rows [[6]](https://react-hook-form.com/advanced-usage). Past ~1000 rows, virtualize — and note the RHF-specific consequence: windowed rows unmount, so you need form-level `defaultValues` for them to restore on scroll-back [[6]](https://react-hook-form.com/advanced-usage).

**TanStack Form** is an external store with selector subscriptions, so scoping is automatic — in theory. Two real 2026 caveats:
- `form.Subscribe` re-renders on *every* form mutation whenever your selector returns an object or array, because the underlying `useStore` compares with `Object.is` and the selector allocates a fresh reference each time — "not just the fields the selector cares about". Open since Mar 2026; the fix is passing `shallow` [[14]](https://github.com/TanStack/form/issues/2090). Return primitives from selectors, or destructure into several `Subscribe`s.
- Mount/unmount of `<form.Field>` scales worse than linearly — a reporter measured ~1300 fields taking 10+ seconds and occasionally crashing the tab, against ~200 ms for plain inputs, calling it "worse than O(N) — something like O(N^2)" (v1.29.1, May 2026) [[15]](https://github.com/TanStack/form/issues/2150). That is the exact shape of a large dynamic form, so benchmark before committing.
- API hygiene: always pass a selector (omitting it re-renders on any state change), and prefer `form.Subscribe` for UI (it isolates the re-render to its own children) over `useSelector` (re-renders the whole component). `useStore` is deprecated in favour of `useSelector` [[12]](https://tanstack.com/form/latest/docs/framework/react/guides/reactivity).

**Conform** barely participates: the DOM holds the values, React state only holds the last validation result, so keystroke re-render cost is near zero — but every *validation* is potentially a server round-trip [[22]](https://conform.guide/validation), and huge repeating groups have their own cost on the parse side (v1.19.4 patched a DoS in `parseSubmission` triggered by "submissions with numerous repeated fields") [[24]](https://github.com/edmundhung/conform/releases).

**Measurable axes.** No public head-to-head render-count benchmark exists for these three in 2026 — the comparison articles are qualitative [[25]](https://splitforms.com/blog/best-react-form-library-2026), and TanStack's own table is a feature matrix, not a benchmark [[26]](https://tanstack.com/form/latest/docs/comparison). What *is* measured:

| Axis | RHF 7.81 | TanStack Form 1.30 | Conform 1.19 |
|---|---|---|---|
| Core bundle, min+gzip (May 2026) | ~9 kB [[25]](https://splitforms.com/blog/best-react-form-library-2026) | ~6 kB [[25]](https://splitforms.com/blog/best-react-form-library-2026) | not in that benchmark |
| + Zod | ~14 kB [[25]](https://splitforms.com/blog/best-react-form-library-2026) | ~11 kB [[25]](https://splitforms.com/blog/best-react-form-library-2026) | — |
| Re-renders per keystroke (uninstrumented field) | 0 (ref-based) [[6]](https://react-hook-form.com/advanced-usage) | 0 outside subscribers — unless a selector returns an object [[14]](https://github.com/TanStack/form/issues/2090) | 0 (DOM-backed) [[22]](https://conform.guide/validation) |
| Known super-linear cost | — | field mount/unmount, ~10 s @ 1300 fields [[15]](https://github.com/TanStack/form/issues/2150) | `parseSubmission` on many repeated fields (patched) [[24]](https://github.com/edmundhung/conform/releases) |
| Built-in async debounce | ✗ [[26]](https://tanstack.com/form/latest/docs/comparison) | ✓ `asyncDebounceMs` [[10]](https://tanstack.com/form/latest/docs/framework/react/guides/validation) | n/a — server round-trip [[22]](https://conform.guide/validation) |
| React Compiler safe | ✗ in v7, ✓ in v8 beta [[4]](https://react-hook-form.com/migrate-v7-to-v8)[[27]](https://zenn.dev/ashunar0/articles/692920ecb633fb?locale=en) | ✓ (store + `useSyncExternalStore` model) [[27]](https://zenn.dev/ashunar0/articles/692920ecb633fb?locale=en) | ✓ (no interior mutability in render) |

⚠ **The React Compiler item is the 2026 headline.** RHF v7's design — a `useRef` object mutated in place, plus a `formState` proxy whose *getters register subscriptions as a render side-effect* — is structurally incompatible with the compiler: memoized reads never invalidate, so `watch()` returns stale values and `formState.errors` stops updating; the v7 workaround is `'use no memo'` on every form component [[27]](https://zenn.dev/ashunar0/articles/692920ecb633fb?locale=en). RHF v8 beta's headline feature is exactly this: "V8 adds first-class support for the React Compiler. No additional configuration is required" [[4]](https://react-hook-form.com/migrate-v7-to-v8). If you are turning the compiler on across a large RHF v7 codebase, that is a migration, not a flag.

---

## What this means in practice

- **Repeating groups with reorder** → RHF. It is the only one that hands you a stable row identity, and `swap`/`move` propagate correctly through nested arrays [[1]](https://react-hook-form.com/docs/usefieldarray)[[2]](https://deepwiki.com/react-hook-form/react-hook-form/5.3-advanced-field-array-patterns). With TanStack, carry your own row `id` [[16]](https://github.com/TanStack/form/issues/957).
- **Conditional fields** → decide the payload contract explicitly. Every library's default is wrong for *someone*: RHF and TanStack submit ghosts, Conform loses answers. And in RHF, the ghost-field fix is unavailable inside field arrays [[1]](https://react-hook-form.com/docs/usefieldarray).
- **Dependent async validation** → TanStack if you want it declarative and debounced [[10]](https://tanstack.com/form/latest/docs/framework/react/guides/validation); RHF only with the remote check kept *outside* the resolver [[8]](https://github.com/orgs/react-hook-form/discussions/11942); Conform if you'd rather have one schema and no uniqueness endpoint [[21]](https://conform.guide/api/zod/conformZodMessage).
- **Wizards** → TanStack's `FormGroup` is the only first-class primitive [[13]](https://tanstack.com/form/latest/docs/framework/react/guides/form-groups); RHF's own docs tell you to bring a state library [[6]](https://react-hook-form.com/advanced-usage).
- **100+ fields** → RHF, with `useFormState` pushed to the leaves. Verify TanStack's mount cost against your field count first [[15]](https://github.com/TanStack/form/issues/2150).
