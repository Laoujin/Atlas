---
title: "Uploads, autosave and unsaved-changes guards in React forms (2026)"
date: 2026-07-13
depth: survey
format: md
topic: "Survey file uploads, autosave, and unsaved-changes handling in React forms in 2026: upload patterns (presigned direct-to-S3/R2, multipart, resumable/tus, progress reporting, Server Actions + FormData), drag-and-drop and client-side file validation, autosave/draft persistence with useOptimistic and conflict handling, and unsaved-changes guards across React Router 7, TanStack Router and the Next.js App Router."
topic_raw: "react how to do forms in 2026"
tags: [react, forms, file-upload, autosave, react-router, nextjs, offline]
summary: "Bytes bypass your form: the browser presigns and uploads direct-to-storage while the form only carries a key — and progress still means XHR, not fetch."
citations: 36
reading_time_min: 13
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 575
issue: 4
---

> **TL;DR** — In 2026 the mainstream pattern is: the form never carries the bytes. A Server Action / API route mints a presigned URL, the browser PUTs direct to S3/R2, and the form field holds the object key. Upload progress still requires `XMLHttpRequest` — `fetch` cannot report it, by design [[1]](https://jakearchibald.com/2025/fetch-streams-not-for-progress/). Autosave is a debounce plus an `If-Match` ETag, not a merge algorithm [[28]](https://learn.microsoft.com/en-us/azure/storage/blobs/concurrency-manage). Unsaved-changes guards are solved in React Router 7 and TanStack Router, and still **not** solved in the Next.js App Router — `<Link onNavigate>` covers `<Link>` clicks only, and the request for a real navigation guard has been open since March 2023 [[7]](https://nextjs.org/docs/app/api-reference/components/link)[[9]](https://github.com/vercel/next.js/discussions/47020) ⭐ 141k.

---

## 1. Where the bytes go

Four transport shapes. Pick by file size and by whether a dropped connection must be survivable.

| Pattern | Bytes through your server | Progress | Resumable | Ceiling | Cost of entry |
|---|---|---|---|---|---|
| `multipart/form-data` → API route / Server Action | ✓ | ✗ (no browser API on the submit path) | ✗ | 1 MB default on Next Server Actions [[8]](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions) | zero |
| Presigned single `PUT` → S3/R2 | ✗ | ✓ via XHR | ✗ (restart from 0) | ~100 MiB before it's abusive [[15]](https://uppy.io/docs/aws-s3/) | one signing endpoint |
| Presigned **S3 multipart** (per-part URLs) | ✗ | ✓ per part | ✓ (retry the failed part) | 5 TiB | create/sign-part/complete endpoints [[36]](https://developers.cloudflare.com/r2/objects/upload-objects/) |
| **tus** → tusd / Supabase / Cloudflare Stream | ✓ (or a tus service) | ✓ | ✓ across page reloads & days | unbounded | a tus server [[19]](https://tus.io/protocols/resumable-upload) |

**Server Actions are the wrong pipe for real files.** The Server Action body cap is 1 MB by default, and the limit counts the raw multipart body — boundaries, part headers and every other field in the same `FormData` [[8]](https://nextjs.org/docs/app/api-reference/config/next-config-js/serverActions). Raising `serverActions.bodySizeLimit` is not enough on Next 15.5+ standalone, where an internal proxy layer applies its own `proxyClientMaxBodySize`, and large binary `FormData` has its own open failure report [[30]](https://github.com/vercel/next.js/discussions/86985) ⭐ 141k. Use the action for the *metadata round-trip* — mint the presigned URL, then accept the returned key — and let the browser move the bytes [[31]](https://uploadcare.com/blog/react-useactionstate-file-uploads/).

```
Action: presign(name, type, size)  →  { url, key }
Browser: XHR PUT url (progress events)  →  204
Action: attachToRecord(key)  →  revalidate
```

The form's registered field is a `string` key, not a `File`. That is also what makes the field trivially serialisable into a draft (§3) and what makes RHF/TanStack Form/Zod validation of "the upload" collapse into validating a string.

**R2 caveat.** R2 presigns `PUT`/`GET`/`HEAD` but explicitly does **not** support browser HTML-form multipart POST, so the S3-multipart flow must be brokered by your own Worker endpoints [[21]](https://developers.cloudflare.com/r2/api/s3/presigned-urls/). Direct browser `PUT` to any bucket needs bucket-level CORS or it dies in preflight [[22]](https://developers.cloudflare.com/r2/buckets/cors/).

### Progress: `fetch` still can't, and this is not a bug

`fetch` has no upload-progress event. Streaming a `ReadableStream` request body (which requires `duplex: 'half'` and HTTP/2 [[2]](https://developer.chrome.com/docs/capabilities/web-apis/fetch-streaming-requests)) does not fix it: you measure "when the browser pulled from my stream", which is buffering, not delivery — and if the web leans on that, browsers can never increase their buffers [[1]](https://jakearchibald.com/2025/fetch-streams-not-for-progress/). Jake Archibald's guidance is unchanged: *"If you want progress events today, the best way is to use XHR"* [[1]](https://jakearchibald.com/2025/fetch-streams-not-for-progress/). A fetch-observer API is still in the future tense.

Practical consequences: `xhr.upload.onprogress` for hand-rolled uploads; every serious library (Uppy, FilePond, tus-js-client) is XHR-based under the hood for exactly this reason. For S3 multipart you also get free coarse progress — count completed parts.

### Resumable: tus is stable, and standardisation is nearly done

tus 1.0.0 has been frozen since 2016 and is explicitly declared production-stable [[19]](https://tus.io/protocols/resumable-upload). The successor is `draft-ietf-httpbis-resumable-upload`, now at revision **11**, Standards Track, still not an RFC [[20]](https://datatracker.ietf.org/doc/draft-ietf-httpbis-resumable-upload/). ⚠ `tus-js-client` last shipped 4.3.1 in Jan 2025 — quiet, not dead; the protocol underneath it is intentionally not moving. Choose tus over S3-multipart when a *user* must be able to close the laptop and finish tomorrow; choose S3-multipart when you only need to survive a flaky packet.

---

## 2. Drag-and-drop and client-side validation

| Library | Latest | Shape | Does the upload? | ⭐ Stars | Weekly DL |
|---|---|---|---|---|---|
| [react-dropzone](https://react-dropzone.js.org/) | 17.0.0 (12 Jul 2026) [[27]](https://registry.npmjs.org/react-dropzone) | headless hook (`useDropzone`) | ✗ — hands you `File[]` [[35]](https://react-dropzone.js.org/) | ⭐ 11k (Jul 2026) | ~3.5M [[18]](https://www.pkgpulse.com/guides/uppy-vs-filepond-vs-react-dropzone-file-upload-2026) |
| [Uppy](https://uppy.io) | 5.2.x | plugins + (since 5.0) headless hooks | ✓ tus, S3, S3-multipart, Companion | ⭐ 31k (Jul 2026) | ~500K [[18]](https://www.pkgpulse.com/guides/uppy-vs-filepond-vs-react-dropzone-file-upload-2026) |
| [FilePond](https://pqina.nl/filepond/) | 4.32.x | opinionated widget | ✓ (chunking; no tus/S3 plugins) | ⭐ 16k (Jul 2026) | ~700K [[18]](https://www.pkgpulse.com/guides/uppy-vs-filepond-vs-react-dropzone-file-upload-2026) |
| [tus-js-client](https://github.com/tus/tus-js-client) | 4.3.1 (Jan 2025) | protocol client, no UI | ✓ tus only | ⭐ 2.6k (Jul 2026) | — |
| [UploadThing](https://uploadthing.com) | 7.7.x (Aug 2025) | managed service + typed client | ✓ (hosted) | ⭐ 5.2k (Jul 2026) | — |

**react-dropzone is not stale — it just churned.** Three majors landed in 2026: v15 (Feb) reset `isDragReject` after drop (use `fileRejections` / `onDropRejected` for post-drop UI), v16 dropped the UMD build and went ESM+CJS with an exports map, and v17 (12 Jul 2026) is a TypeScript rewrite requiring React ≥ 18, with `prop-types` and `defaultProps` removed [[17]](https://github.com/react-dropzone/react-dropzone/releases) ⭐ 11k. If you pinned v14 in 2024, budget an afternoon.

**Uppy 5.0** (1 Sep 2025) is the notable shift: headless components and hooks (`useDropzone`, `useFileInput`, `useWebcam`) under an `<UppyContextProvider />`, which finally lets you take Uppy's transport (tus/S3-multipart/retry) without its Dashboard UI. `@uppy/status-bar`, `@uppy/informer` and `@uppy/progress-bar` are deprecated in the process [[25]](https://uppy.io/blog/uppy-5.0/). `@uppy/aws-s3` v5 also absorbed the old `aws-s3-multipart` plugin: one plugin, `shouldUseMultipart`, default cut-over at 100 MiB [[15]](https://uppy.io/docs/aws-s3/).

**Decision:** react-dropzone + your own presign/XHR for a single avatar or a handful of attachments; Uppy 5 headless the moment you need resumability, multiple sources, or a queue of 50 files.

### Validation of files

Three tiers, and only the third one is security:

| Check | Where | What it catches | What it misses |
|---|---|---|---|
| `accept`, `maxSize`, `maxFiles` (dropzone/Uppy `restrictions`) | client, sync | wrong extension, obvious size blowout | anything renamed |
| Magic-byte sniff of the first bytes via `File.slice(0, 12).arrayBuffer()` | client, async | `payload.exe` renamed to `.png` | polyglots; prepended headers |
| Re-sniff + transcode server-side | server | everything you actually care about | — |

Client-supplied `Content-Type` and extension are attacker-controlled and must never be a security decision; magic bytes are stronger but still spoofable (prepend `%PDF-` and you pass), so server-side revalidation is mandatory [[29]](https://www.sourcery.ai/vulnerabilities/file-upload-content-type-bypass). ⚠ With presigned direct-to-S3 the object lands in your bucket *before* any server code sees it — validate on the S3 event / object-created webhook, and keep the bucket private until validation passes.

Image **dimensions** need an async check (`createImageBitmap(file)` → `.width/.height`, or an `Image` + `URL.createObjectURL`). This is asynchronous, so it belongs in a schema's async refinement or in a dropzone `validator` returning a `FileError` — not in a synchronous Zod `.refine`.

---

## 3. Autosave and drafts

### The debounce is the easy part

Both major form libraries now have first-class hooks for it. TanStack Form: form-level `listeners` with `onChangeDebounceMs` and an `onChange` that calls `formApi.handleSubmit()` when `formApi.state.isValid` [[12]](https://tanstack.com/form/v1/docs/framework/react/guides/listeners). React Hook Form: `watch()`/`useWatch` into a debounced effect, gated on `formState.isDirty`. The mature prior art is react-admin's `<AutoSave>`: 3000 ms after the last change, requires `resetOptions={{ keepDirtyValues: true }}` so the server's response doesn't stomp what the user typed during the in-flight save, and it explicitly refuses to coexist with `warnWhenUnsavedChanges` because it ships its own guard [[33]](https://marmelab.com/react-admin/AutoSave.html). That last constraint is the real design lesson: **autosave and unsaved-changes guards are the same feature**, and running both produces a dialog that fires while a save is already in flight.

Give the user a three-state indicator (`idle | saving | saved | error`) — a debounced save with no status text is indistinguishable from a broken one [[34]](https://reactuse.com/blog/react-form-handling-hooks/).

### `useOptimistic` is for actions, not for autosave state

`useOptimistic` renders the optimistic value **only while an Action is pending**, then converges with real state in the same render — no extra "clear" render — and its setter must be called inside a Transition/Action or React warns [[11]](https://react.dev/reference/react/useOptimistic). That makes it excellent for "row added, greyed out until the server confirms" and a poor fit for a long-lived autosaving text field, where the user keeps typing *during* the pending window and the optimistic value would be clobbered by `value` on settle. For autosave fields, keep the controlled input as the source of truth and use `useOptimistic` only for the discrete side-effects (the attachment chip, the "published" badge).

### Where the draft lives

| Store | Capacity | Survives crash / tab close | Stores `File`/`Blob` | Multi-device | Use when |
|---|---|---|---|---|---|
| `localStorage` | 5–10 MB, string only | ✓ | ✗ | ✗ | tiny forms; JSON-serialisable values only |
| IndexedDB (via [idb](https://github.com/jakearchibald/idb) ⭐ 7.4k / [Dexie](https://dexie.org/) ⭐ 14k) | hundreds of MB+, evictable | ✓ (unless evicted) | ✓ | ✗ | attachments in the draft; offline-first [[26]](https://www.pkgpulse.com/guides/dexie-vs-localforage-vs-idb-indexeddb-browser-storage-2026) |
| Server draft row (`status: 'draft'`) | unbounded | ✓ | via the key, not the bytes | ✓ | anything a user expects to find on their phone |

idb (~3 KB, ~20M weekly downloads) is the default wrapper; Dexie (~65 KB) earns its size when you want `useLiveQuery` reactive reads and schema versioning [[26]](https://www.pkgpulse.com/guides/dexie-vs-localforage-vs-idb-indexeddb-browser-storage-2026)[[32]](https://dexie.org/). ⚠ IndexedDB is **best-effort** storage: without `navigator.storage.persist()` the browser may evict your draft under storage pressure [[26]](https://www.pkgpulse.com/guides/dexie-vs-localforage-vs-idb-indexeddb-browser-storage-2026). Call it, and treat a local-only draft as a convenience, never as the record.

Rule of thumb: **local draft for the keystrokes, server draft for the truth.** Debounce ~500 ms to IndexedDB, ~2–3 s to the server.

### Conflict handling

For single-author forms, use HTTP optimistic concurrency, not a merge algorithm: read the ETag / `version` with the record, send it back as `If-Match` on the autosave PUT, and a stale version yields **412 Precondition Failed** rather than a silent overwrite [[28]](https://learn.microsoft.com/en-us/azure/storage/blobs/concurrency-manage). On 412 the only honest UI is *stop autosaving, tell the user, offer reload-and-lose vs. overwrite* — silently retrying with the new ETag is last-write-wins with extra steps.

CRDTs ([Yjs](https://github.com/yjs/yjs) ⭐ 22k, [Automerge](https://github.com/automerge/automerge) ⭐ 6.4k) solve a different problem — *concurrent* authors on a shared document. Reaching for them to fix a one-user autosave race is a category error.

---

## 4. Unsaved-changes guards

Two orthogonal exits: **hard navigation** (tab close, reload, typed URL) and **soft navigation** (your router). You need both, and only one of them is portable.

| | React Router 7 | TanStack Router | Next.js App Router |
|---|---|---|---|
| Block router navigation | ✓ `useBlocker(() => isDirty)` [[4]](https://reactrouter.com/how-to/navigation-blocking) | ✓ `useBlocker({ shouldBlockFn })` / `<Block>` [[6]](https://tanstack.com/router/v1/docs/framework/react/guide/navigation-blocking) | ⚠ `<Link onNavigate>` only [[7]](https://nextjs.org/docs/app/api-reference/components/link) |
| Blocks `router.push()` from code | ✓ | ✓ | ✗ |
| Blocks browser back/forward | ✓ | ✓ | ✗ |
| `beforeunload` wired in | ✗ — separate `useBeforeUnload` [[5]](https://reactrouter.com/api/hooks/useBeforeUnload) | ✓ `enableBeforeUnload` [[6]](https://tanstack.com/router/v1/docs/framework/react/guide/navigation-blocking) | ✗ — hand-roll |
| Custom modal (not `window.confirm`) | ✓ `blocker.state === "blocked"` → `proceed()` / `reset()` [[4]](https://reactrouter.com/how-to/navigation-blocking) | ✓ `withResolver` → `{ proceed, reset, status }` [[6]](https://tanstack.com/router/v1/docs/framework/react/guide/navigation-blocking) | ✗ — `onNavigate` is sync, so `window.confirm` only |
| Caveat | not available in Declarative mode [[4]](https://reactrouter.com/how-to/navigation-blocking) | — | first-party guard open since Mar 2023 [[9]](https://github.com/vercel/next.js/discussions/47020) ⭐ 141k |

**Next.js is the weak spot, and it hasn't moved.** `onNavigate` landed in v15.3.0 and gives you `preventDefault()` — but it only fires for same-origin client-side navigation *from a `<Link>` you control*; it does not see `router.push()`, browser back/forward, external URLs, or `download` links [[7]](https://nextjs.org/docs/app/api-reference/components/link). Next's own docs' "Blocking navigation" recipe is exactly that: a context + a `CustomLink` wrapper + `window.confirm` [[7]](https://nextjs.org/docs/app/api-reference/components/link). Discussion #47020 — "router events have been removed entirely" — is still open with no substantive Vercel answer [[9]](https://github.com/vercel/next.js/discussions/47020) ⭐ 141k. The community shim is [next-navigation-guard](https://github.com/LayerXcom/next-navigation-guard) ⭐ 591 (monkey-patches the App Router context; last release 0.2.0, Jun 2025) [[10]](https://github.com/LayerXcom/next-navigation-guard) — usable, but you are betting on Next's internals. If unsaved-changes fidelity is a product requirement, that is a real point on the router-choice scorecard.

**`beforeunload` is a blunt instrument and always has been.** Trigger it with `event.preventDefault()` (`returnValue = true` only for legacy Chrome/Edge < 119). You cannot set the message — browsers show a generic string. It requires **sticky activation**: if the user never interacted with the page, no dialog. And ⚠ in Firefox a registered `beforeunload` listener disqualifies the page from the bfcache, so **attach it only while dirty and remove it on save** [[3]](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event).

### Determining "dirty"

`react-hook-form`'s `isDirty` is a deep-equality compare of current values against `defaultValues` — so it self-heals when the user types a value back to its original [[13]](https://react-hook-form.com/docs/useform/formstate). Two footguns, both perennial: (a) if `defaultValues` is a new object identity each render, or fields mount before async defaults arrive, `isDirty` latches true; (b) `setValue()` without `shouldDirty: true` moves `isDirty` but not `dirtyFields`, and the two are documented as *not* in sync — `dirtyFields` is per-field, `isDirty` is whole-form [[13]](https://react-hook-form.com/docs/useform/formstate)[[14]](https://github.com/react-hook-form/react-hook-form/issues/13141) ⭐ 45k. Gate a "leave?" dialog on `isDirty`; drive a PATCH payload from `dirtyFields`. And after a successful save, `reset(savedValues)` — otherwise `isDirty` stays true forever and every navigation gets a dialog.

Files break this model: a `File` object never deep-equals its previous self. Another reason the form field should hold the returned **key**, not the `File`.

---

## 5. Offline and flaky networks

There is real prior art, and it is narrower than people hope.

- **In-flight upload survives a refresh:** Uppy's Golden Retriever restores selected files after a crash or accidental close — LocalStorage for the Uppy state, IndexedDB for files under ~5 MiB, an optional Service Worker for larger ones (transient — it does *not* survive a browser restart), 24 h default expiry, and files it can't restore are shown as "ghosts" for re-selection [[16]](https://uppy.io/docs/golden-retriever/). Combine with tus and the upload genuinely resumes; combine with a plain `PUT` and you have only saved the user the file picker.
- **Deferred form submission:** `workbox-background-sync` queues failed requests in IndexedDB and replays them on a `sync` event [[23]](https://developer.chrome.com/docs/workbox/modules/workbox-background-sync). ⚠ The Background Sync API is Chromium-only — ~77 % global, **zero** support in Safari (all versions, incl. iOS) and Firefox [[24]](https://caniuse.com/background-sync). Workbox degrades gracefully by replaying whenever the service worker next starts up [[23]](https://developer.chrome.com/docs/workbox/modules/workbox-background-sync), which in practice means "next time the user opens the tab" — acceptable for a draft sync, not for anything the user was told was submitted.
- **The portable floor:** persist the dirty form to IndexedDB on every debounce tick, retry the server save with exponential backoff while `navigator.onLine`, and show the queue state. That works everywhere, needs no service worker, and is what most teams should ship.

---

## Assembling it

```
react-hook-form / TanStack Form   ← field is a string key, not a File
  └ react-dropzone / Uppy 5 headless   ← File[] + client validation
      └ presign (Server Action)  →  XHR PUT direct to S3/R2  →  key
  └ debounce(isDirty) → IndexedDB (500ms) + server draft w/ If-Match (2–3s)
  └ useBlocker (RR7 / TanStack) + beforeunload while dirty
```

The only genuinely unsolved piece in 2026 is the Next.js App Router navigation guard. Everything else has a boring, load-bearing answer.
