---
title: "Toasts in the Next.js App Router: firing client state from the server"
date: 2026-07-13
depth: survey
format: md
topic: "Toast notifications in Next.js App Router, React Server Components and server actions (2026): useActionState + useEffect and its pitfalls, the redirect-with-toast problem, cookie flash-message queues, Toaster placement and the client boundary, and how Sonner / react-toastify / react-hot-toast behave under RSC — with React Router 7 flash sessions as contrast."
topic_raw: "react toastr 2026"
tags: [react, nextjs, app-router, rsc, server-actions, toast, sonner, react-router]
summary: "No toast library ships a server entrypoint — the queue always lives in client memory, so an RSC app must serialize server-origin toasts through an action return value or a cookie; redirect() forecloses the first option."
citations: 25
reading_time_min: 13
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 579
issue: 3
---

> **TL;DR** — Toast state is client memory in all three major libraries; none ships an RSC/server entrypoint, so a server mutation can only *describe* a toast and hand it across the boundary [[12]](https://unpkg.com/sonner@2.0.7/dist/index.mjs)[[13]](https://unpkg.com/react-hot-toast@2.6.0/dist/index.mjs)[[14]](https://unpkg.com/react-toastify@11.1.0/dist/index.mjs). Two channels exist and you pick by whether the action redirects: **no redirect** → return `{status, message, nonce}` from the action and toast in a `useEffect` guarded by the nonce (or skip `useActionState` entirely and `await` the action inside a transition — no effect, no StrictMode double-fire); **redirect** → `redirect()` throws `NEXT_REDIRECT` and unmounts the caller before any state comes back [[3]](https://nextjs.org/docs/app/api-reference/functions/redirect)[[7]](https://github.com/vercel/next.js/discussions/67660) ⭐ 141k, so set a **flash cookie before the redirect** and drain it on the next render [[9]](https://github.com/vercel/next.js/discussions/57118) ⭐ 141k[[1]](https://buildui.com/posts/toast-messages-in-react-server-components). React Router 7 has the same problem solved at framework level with `session.flash()` [[19]](https://reactrouter.com/explanation/sessions-and-cookies).

Verified against Next.js **16.2.10** (docs revision of 2026-03-03) [[3]](https://nextjs.org/docs/app/api-reference/functions/redirect). Next's own docs now call these "Server Functions"; "Server Action" is the subset passed to a form `action` prop [[4]](https://nextjs.org/docs/app/api-reference/functions/cookies).

## Why this is awkward at all

`'use client'` cuts the module graph in two: a module carrying the directive and everything it imports is bundled and evaluated on the client [[6]](https://react.dev/reference/rsc/use-client). Every toast library puts the directive at the top of its dist bundle, which means `toast()` — the imperative queue-push — is a *client reference* on the server side. You cannot call it from a Server Function; you can only return a serializable value and let a client component push it [[6]](https://react.dev/reference/rsc/use-client).

## Pattern A — `useActionState` + `useEffect`, with a nonce

`useActionState(action, initialState)` returns `[state, formAction, isPending]`; the state is whatever the action returned, redelivered through the RSC payload [[5]](https://react.dev/reference/react/useActionState).

```ts
// app/posts/actions.ts
'use server'
import { revalidatePath } from 'next/cache'

export type ActionState =
  | { status: 'success' | 'error'; message: string; at: number }
  | null

export async function savePost(
  _prev: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const title = String(formData.get('title') ?? '')
  if (!title) return { status: 'error', message: 'Title is required', at: Date.now() }

  await db.post.create({ data: { title } })
  revalidatePath('/posts')
  return { status: 'success', message: `Saved “${title}”`, at: Date.now() }
}
```

```tsx
// app/posts/post-form.tsx
'use client'
import { useActionState, useEffect, useRef } from 'react'
import { toast } from 'sonner'
import { savePost, type ActionState } from './actions'

export function PostForm() {
  const [state, formAction, isPending] = useActionState<ActionState, FormData>(savePost, null)
  const lastToasted = useRef(0)

  useEffect(() => {
    if (!state || state.at === lastToasted.current) return
    lastToasted.current = state.at
    const fire = state.status === 'success' ? toast.success : toast.error
    fire(state.message)
  }, [state])

  return (
    <form action={formAction}>
      <input name="title" />
      <button disabled={isPending}>Save</button>
    </form>
  )
}
```

The `at` field is not decoration — it is the whole pattern. Two failure modes it fixes, in opposite directions:

- **Stale re-toast.** The action calls `revalidatePath`, so the RSC payload re-renders the tree; `state` deserializes into a *new object with the same contents*, the effect's dependency changes by identity, and the old message toasts again with no new submission. Robin Wieruch: "If the component re-renders, it might show an old toast message even if no new action was triggered" [[2]](https://www.robinwieruch.de/react-server-actions-useactionstate-toast/). Reported repeatedly against Next.js [[7]](https://github.com/vercel/next.js/discussions/67660) ⭐ 141k.
- **Missing toast.** Submit the same invalid form twice and the action returns a *structurally identical* object. Without a nonce, nothing in the deps array changed → no second toast, and the user thinks the button is dead.

**StrictMode.** React deliberately runs effects setup → cleanup → setup in development [[23]](https://react.dev/reference/react/StrictMode); a naive `useEffect(() => { toast(msg) })` therefore double-toasts in dev — filed against Sonner as [issue #322](https://github.com/emilkowalski/sonner/issues/322) ⭐ 13k and closed as expected behaviour [[10]](https://github.com/emilkowalski/sonner/issues/322). The `useRef` nonce guard above happens to fix this too: refs survive StrictMode's simulated remount, so the second setup is a no-op. Production runs the effect once per mount regardless [[23]](https://react.dev/reference/react/StrictMode) — ⚠ which is exactly why the bug ships: it looks like a dev-only annoyance and the *stale re-toast* variant is not dev-only at all.

## Pattern B — skip `useActionState`, await inside a transition

If you don't need progressive enhancement, the effect is pure ceremony. `await` the action and toast in the same tick:

```tsx
'use client'
import { useTransition } from 'react'
import { toast } from 'sonner'
import { deletePost } from './actions'

export function DeleteButton({ id }: { id: string }) {
  const [isPending, startTransition] = useTransition()

  return (
    <button
      disabled={isPending}
      onClick={() =>
        startTransition(async () => {
          const res = await deletePost(id) // plain serializable result, never throws to the client
          res.ok ? toast.success('Post deleted') : toast.error(res.message)
        })
      }
    >
      Delete
    </button>
  )
}
```

No effect, no nonce, no StrictMode double-fire, no stale replay. This is the "direct promise awaiting" answer the Next.js discussion converges on [[7]](https://github.com/vercel/next.js/discussions/67660) ⭐ 141k. The cost: the button needs JS (no no-JS form fallback), and the action must not `redirect()`.

[next-safe-action](https://github.com/TheEdoRan/next-safe-action) ⭐ 3.0k packages this with typed callbacks so the toast site is declarative rather than an effect [[25]](https://github.com/TheEdoRan/next-safe-action):

```ts
const { execute } = useAction(createPost, {
  onSuccess: ({ data }) => toast.success(`Created: ${data.name}`),
  onError:   ({ error }) => toast.error(error.serverError ?? 'Invalid input'),
})
```
[[22]](https://next-safe-action.dev/docs/execute-actions/hooks/useaction)

## Pattern C — the redirect problem, and the flash cookie

`redirect()` throws a `NEXT_REDIRECT` error and terminates rendering of the segment; in a Server Action it serves a **303** [[3]](https://nextjs.org/docs/app/api-reference/functions/redirect). Consequences for toasts:

1. The action **never returns** → `useActionState` state never updates → the effect never fires [[7]](https://github.com/vercel/next.js/discussions/67660) ⭐ 141k.
2. The client component that owns the effect is unmounted by the navigation anyway.
3. Because it throws, `redirect()` must be called **outside** any `try` block — a `try/catch` around your mutation will swallow the redirect [[3]](https://nextjs.org/docs/app/api-reference/functions/redirect).

The workaround the ecosystem settled on, and the one Next's own discussion threads recommend: **set a cookie before redirecting, read it on the next render** [[9]](https://github.com/vercel/next.js/discussions/57118) ⭐ 141k[[8]](https://github.com/vercel/next.js/discussions/77389) ⭐ 141k. Cookies are the only channel that survives a 303, a hard reload, and a new tab [[1]](https://buildui.com/posts/toast-messages-in-react-server-components).

```ts
// lib/flash.ts — server-only
import 'server-only'
import { cookies } from 'next/headers'

export type Flash = { status: 'success' | 'error'; message: string }

export async function setFlash(flash: Flash) {
  const store = await cookies()
  // random name, not a fixed key: two flashes in one request must not overwrite each other
  store.set(`flash-${crypto.randomUUID()}`, JSON.stringify(flash), {
    path: '/',
    maxAge: 60,
    httpOnly: true,
    sameSite: 'lax',
  })
}

export async function readFlash() {
  const store = await cookies()
  return store
    .getAll()
    .filter((c) => c.name.startsWith('flash-') && c.value)
    .map((c) => ({ id: c.name, ...(JSON.parse(c.value) as Flash) }))
}
```

The random-suffix trick (rather than a single `flash` key) is Build UI's; it lets multiple messages queue without clobbering [[1]](https://buildui.com/posts/toast-messages-in-react-server-components).

```ts
// app/posts/actions.ts
'use server'
import { redirect } from 'next/navigation'
import { setFlash } from '@/lib/flash'

export async function createPost(formData: FormData) {
  const post = await db.post.create({ data: { title: String(formData.get('title')) } })
  await setFlash({ status: 'success', message: 'Post created' })
  redirect(`/posts/${post.id}`) // last statement — it throws
}
```

```tsx
// app/layout.tsx — stays a Server Component
import { Toaster } from 'sonner'
import { readFlash } from '@/lib/flash'
import { FlashToaster } from './flash-toaster'

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const flashes = await readFlash()
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster />
        <FlashToaster flashes={flashes} />
      </body>
    </html>
  )
}
```

```tsx
// app/flash-toaster.tsx
'use client'
import { useEffect, useRef } from 'react'
import { toast } from 'sonner'
import { clearFlash } from './flash-actions' // 'use server'

export function FlashToaster({ flashes }: { flashes: Array<{ id: string } & Flash> }) {
  const fired = useRef(new Set<string>())

  useEffect(() => {
    for (const f of flashes) {
      if (fired.current.has(f.id)) continue
      fired.current.add(f.id)
      ;(f.status === 'success' ? toast.success : toast.error)(f.message)
      void clearFlash(f.id) // must be a Server Function; see below
    }
  }, [flashes])

  return null
}
```

### The three constraints that make this pattern non-obvious

| Constraint | Why | Source |
|---|---|---|
| You cannot `cookies().delete()` while rendering a Server Component | "HTTP does not allow setting cookies after streaming starts, so you must use `.set` in a Server Function or Route Handler" — `.delete` likewise | [[4]](https://nextjs.org/docs/app/api-reference/functions/cookies) |
| → so the *drain* must be a client-triggered Server Function (or Route Handler), not part of the read | Build UI wraps the dismiss in a Server Function and hides the latency with `useOptimistic` | [[1]](https://buildui.com/posts/toast-messages-in-react-server-components) |
| ⚠ Reading `cookies()` in the root layout opts **every route** into dynamic rendering | `cookies` is a request-time API: "Using it in a layout or page will opt a route into dynamic rendering" | [[4]](https://nextjs.org/docs/app/api-reference/functions/cookies) |

That last row is the real bill for the flash pattern: a static-first app that reads flash cookies in `app/layout.tsx` is no longer static-first. Mitigation is to push the cookie read into its own `<Suspense>`-wrapped server component so only that subtree is dynamic, or to drop `httpOnly` and read the flash cookie client-side.

If the action does **not** redirect, no cookie is needed and the drain problem disappears — Next re-renders the tree in the same roundtrip and the toast can ride the return value: "After you set or delete a cookie in a Server Function, Next.js can return both the updated UI and new data in a single server roundtrip… The UI is not unmounted, but effects that depend on data coming from the server will re-run" [[4]](https://nextjs.org/docs/app/api-reference/functions/cookies). Note the second half of that sentence — it is the *stale re-toast* mechanism from Pattern A, stated in the official docs.

## Pattern D — `?toast=` search params

`redirect('/posts/1?toast=created')`, then a client component reads `useSearchParams()` and toasts. Listed as one of the three canonical options in the Next.js discussion [[8]](https://github.com/vercel/next.js/discussions/77389) ⭐ 141k. It is the worst of the four: the message is in the URL, so a refresh, a back-navigation or a shared link re-toasts — the React Router thread flags exactly this ("URL parameters: refreshes can re-trigger toasts (unreliable)") [[20]](https://github.com/remix-run/react-router/discussions/11872) ⭐ 57k. You must `router.replace()` the param away after firing, which is one more effect to get wrong. Use only when the toast text is genuinely derivable from a stable route state.

## Picking a pattern

| | Progressive enhancement | Survives `redirect()` | Survives reload / new tab | Effect needed | Main hazard |
|---|---|---|---|---|---|
| **A** `useActionState` + effect + nonce | ✓ | ✗ | ✗ | ✓ | Stale re-toast without a nonce [[2]](https://www.robinwieruch.de/react-server-actions-useactionstate-toast/) |
| **B** `await` in `startTransition` | ✗ | ✗ | ✗ | ✗ | None; needs JS [[7]](https://github.com/vercel/next.js/discussions/67660) |
| **C** flash cookie | ✓ | ✓ | ✓ | ✓ (to drain) | Dynamic-renders the layout [[4]](https://nextjs.org/docs/app/api-reference/functions/cookies) |
| **D** `?toast=` param | ✓ | ✓ | ✓ (⚠ *too* well) | ✓ | Re-toasts on refresh/share [[20]](https://github.com/remix-run/react-router/discussions/11872) |

Real apps end up with **B for in-place mutations + C for anything that redirects**. A is the default the docs nudge you toward and the one that generates the bug reports.

## The libraries under RSC

All three ship `'use client'` as the first line of their ESM bundle — verified against the published dist:

| Library | ⭐ | Version | gzip | `'use client'` in dist | `<Toaster/>` in a server layout | Server entrypoint |
|---|---|---|---|---|---|---|
| [Sonner](https://github.com/emilkowalski/sonner) | ⭐ 13k | 2.0.7 | 9.4 kB [[16]](https://bundlephobia.com/package/sonner@2.0.7) | ✓ [[12]](https://unpkg.com/sonner@2.0.7/dist/index.mjs) | ✓ "It can be placed anywhere, even in server components such as `layout.tsx`" [[11]](https://sonner.emilkowal.ski/getting-started) | ✗ |
| [react-hot-toast](https://github.com/timolins/react-hot-toast) | ⭐ 11k | 2.6.0 | 4.8 kB [[17]](https://bundlephobia.com/package/react-hot-toast@2.6.0) | ✓ [[13]](https://unpkg.com/react-hot-toast@2.6.0/dist/index.mjs) | ✓ | ✗ |
| [react-toastify](https://github.com/fkhadra/react-toastify) | ⭐ 13k | 11.1.0 | 9.7 kB [[18]](https://bundlephobia.com/package/react-toastify@11.1.0) | ✓ [[14]](https://unpkg.com/react-toastify@11.1.0/dist/index.mjs) | ✓ (v11 auto-injects its stylesheet when `<ToastContainer/>` renders) | ✗ |

Practical readings:

- **"RSC-safe" is table stakes, and it means less than it sounds.** The directive lets you drop `<Toaster />` straight into `app/layout.tsx` without hand-rolling a `'use client'` wrapper — the layout stays a Server Component and only the toaster subtree crosses into the client bundle [[6]](https://react.dev/reference/rsc/use-client). It does **not** make `toast()` callable from server code; the same module's `toast` export is a client reference.
- **Client-boundary cost is the toaster subtree, not the layout.** 4.8–9.7 kB gzip, evaluated once, no dependency drag (`react-hot-toast` has 2 deps, the others 0–1). This is not a reason to pick between them.
- **The wrapper trap is in shadcn/ui, not in Sonner.** The generated `components/ui/sonner.tsx` re-exports the Toaster wrapped in `next-themes`' `useTheme()` — and shipped *without* its own `'use client'`, producing "Attempted to call useTheme() from the server" [[15]](https://github.com/shadcn-ui/ui/issues/8173) ⭐ 119k. Re-exporting a client component from a file lacking the directive erases the boundary; the directive is per-module, not viral upward.
- **No library models a server-side queue.** Not one exposes an entrypoint you can call from `'use server'` code. Every server-origin toast in an RSC app is therefore a *serialization* problem (Patterns A–D), not a library feature — which is why the reference implementation is a blog post, not an API [[1]](https://buildui.com/posts/toast-messages-in-react-server-components).

### Hydration and SSR

The toasters render an empty container during SSR — their queue lives in a client store that is empty on the server — so the toaster itself is not a hydration-mismatch source. The mismatches come from *what you put in the toast*: server-formatted dates, locale, `Date.now()` in the message body. Next's rule applies unchanged: any value that differs between the prerender and the first client render throws `Text content does not match server-rendered HTML` [[24]](https://nextjs.org/docs/messages/react-hydration-error). Keep flash payloads as opaque strings serialized on the server; format nothing client-side.

## Contrast: React Router 7 / Remix

The same tension exists — the mutation runs on the server, the toast is client state — but the framework has a first-class channel, inherited from Rails: **session flash**. `session.flash(key, value)` writes a value that is deleted the first time it is read [[19]](https://reactrouter.com/explanation/sessions-and-cookies).

```ts
// app/routes/posts.new.tsx
export async function action({ request }: Route.ActionArgs) {
  const session = await getSession(request.headers.get('Cookie'))
  const post = await createPost(await request.formData())

  session.flash('toast', { status: 'success', message: 'Post created' })

  return redirect(`/posts/${post.id}`, {
    headers: { 'Set-Cookie': await commitSession(session) },
  })
}
```

```ts
// app/root.tsx
export async function loader({ request }: Route.LoaderArgs) {
  const session = await getSession(request.headers.get('Cookie'))
  const toast = session.get('toast')            // reading consumes it
  return data({ toast }, { headers: { 'Set-Cookie': await commitSession(session) } })
}
```

Structurally identical to Pattern C — a cookie carrying the message across a redirect — with three differences that matter:

- **Self-destructing.** The flash is consumed on read, so the "who deletes the cookie" problem that forces Next into a client-triggered Server Function [[4]](https://nextjs.org/docs/app/api-reference/functions/cookies) simply does not arise. Reload cannot re-toast [[20]](https://github.com/remix-run/react-router/discussions/11872) ⭐ 57k.
- **Explicit headers.** You must re-`commitSession` in the loader or the deletion never reaches the browser — and ⚠ the docs warn about nested routes: "When using `session.flash()` or `session.unset()`, you need to be sure no other loaders in the request are going to want to read that, otherwise you'll get race conditions… if another loader wants a flash message, use a different key" [[19]](https://reactrouter.com/explanation/sessions-and-cookies).
- **Still a `useEffect` on the client.** The root component watches `loaderData.toast` and calls `toast()`. Same StrictMode double-fire, same need for a dedupe key. [remix-toast](https://github.com/code-forge-io/remix-toast) ⭐ 262 packages the whole loop (`redirectWithSuccess`, `getToast` returning `{ toast, headers }`) for React Router v7 [[21]](https://github.com/code-forge-io/remix-toast).

Net: React Router's loader/action model gives you a *place* for server-origin UI messages; Next's RSC model gives you a return value that a redirect throws away. The Next equivalents are all reconstructions of `flash`.
