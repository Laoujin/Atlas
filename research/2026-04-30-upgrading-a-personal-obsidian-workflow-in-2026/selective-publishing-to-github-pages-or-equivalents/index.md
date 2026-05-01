---
title: "Selective publishing from Obsidian to GitHub Pages"
date: 2026-04-30
depth: standard
format: md
topic: "Selective publishing to GitHub Pages or equivalents"
topic_raw: "Selective publishing to GitHub Pages or equivalents"
issue: 49
tags: [obsidian, publishing, github-pages, quartz, digital-garden, static-sites]
summary: "Pick the opt-in (whitelist) frontmatter pattern over draft-style opt-out; Quartz + ExplicitPublish is the closest free match to Obsidian Publish."
citations: 17
reading_time_min: 5
cover: cover.svg
cost_usd: 2.07
duration_sec: 329
---

> **Decision.** For an Obsidian vault → public site in 2026, pick the **opt-in (whitelist) frontmatter** pattern, not draft-style opt-out — one missing `draft: true` shouldn't be the only thing between a note and the open web. Concrete picks:
> - **Default:** **Quartz** with the `ExplicitPublish` filter (`publish: true`) on GitHub Pages — closest free match to Obsidian Publish, graph + backlinks included [[1]](https://quartz.jzhao.xyz/plugins/ExplicitPublish) [[6]](https://github.com/jackyzha0/quartz).
> - **Material/docs aesthetic:** **Enveloppe** (`share: true` in Obsidian) → MkDocs Material site repo [[3]](https://github.com/Enveloppe/obsidian-enveloppe) [[15]](https://github.com/squidfunk/mkdocs-material).
> - **No-frontmatter option:** **Quartz Syncer** — pick notes from a UI in Obsidian, no per-note metadata to maintain [[9]](https://github.com/saberzero1/quartz-syncer).
> - **Pay to skip the plumbing:** **Obsidian Publish** at $96–$120/yr [[8]](https://unmarkdown.com/blog/obsidian-publish-alternatives).
>
> ⚠ **Never put your raw vault in a public repo even with a publish flag** — most SSGs (Quartz included) emit non-markdown files (PDFs, voice memos, attached images) regardless of the markdown filter [[2]](https://quartz.jzhao.xyz/features/private-pages).

## The selective-publishing patterns

Three patterns dominate, in increasing order of safety:

| Pattern | What you mark | Default state of a new note | Failure mode |
|---|---|---|---|
| **Draft opt-out** | `draft: true` ([Hugo](https://gohugo.io/), [Jekyll](https://jekyllrb.com/), [Astro](https://astro.build/)) | Public | A typo or forgotten flag publishes a note you didn't mean to share |
| **Frontmatter opt-in** | `publish: true` / `dg-publish: true` / `share: true` | Private | Forgotten flag means a note doesn't appear — annoying but safe |
| **UI-selected** | Tick a box in a publication center | Private | None at the metadata layer; only what you click moves |

[Hugo](https://gohugo.io/) natively supports `draft`, `publishDate`, `expiryDate` [[13]](https://gohugo.io/content-management/front-matter/), but those are designed for *blog scheduling*, not *what's in my private vault stays in my private vault*. For an Obsidian-style "tens of thousands of notes, publish ten" workload, the opt-in pattern is the only one that fails closed.

## Tools that implement opt-in publishing

| Tool | Repo | Flag | Hosting target | Notes |
|---|---|---|---|---|
| Quartz `ExplicitPublish` | [jackyzha0/quartz](https://github.com/jackyzha0/quartz) ⭐ 12k | `publish: true` | Any static host (GitHub Pages, Cloudflare, Netlify) | Graph view, backlinks, full-text search; Node 22+ build [[1]](https://quartz.jzhao.xyz/plugins/ExplicitPublish) [[6]](https://github.com/jackyzha0/quartz) |
| Obsidian Digital Garden | [oleeskild/obsidian-digital-garden](https://github.com/oleeskild/obsidian-digital-garden) ⭐ 2.3k | `dg-publish: true` | Vercel / Netlify (one-click) | Linked-but-unpublished notes render as "note does not exist" pages [[4]](https://github.com/oleeskild/obsidian-digital-garden) [[5]](https://dg-docs.ole.dev/) |
| Enveloppe | [Enveloppe/obsidian-enveloppe](https://github.com/Enveloppe/obsidian-enveloppe) ⭐ 887 | `share: true` | Pushes to a separate GitHub repo (Jekyll/Hugo/MkDocs/custom) via PR | Build pipeline lives in the *destination* repo; vault stays private [[3]](https://github.com/Enveloppe/obsidian-enveloppe) |
| Quartz Syncer | [saberzero1/quartz-syncer](https://github.com/saberzero1/quartz-syncer) ⭐ 121 | (UI selection, no flag) | Quartz repo on GitHub | Three-bucket publication center: Unpublished / Changed / Published [[9]](https://github.com/saberzero1/quartz-syncer) [[10]](https://saberzero1.github.io/quartz-syncer-docs/Usage-Guide) |
| Obsidian Publish | (paid SaaS) | `publish: true` (when site is opt-in) | publish.obsidian.md/your-site | $8/mo annual, $10/mo monthly; no community plugins [[8]](https://unmarkdown.com/blog/obsidian-publish-alternatives) |
| obsidian-custom-publish | [danyim/obsidian-custom-publish](https://github.com/danyim/obsidian-custom-publish) ⭐ 0 | configurable | Whatever picks up the flag | Just adds command-palette actions; bring your own pipeline [[17]](https://github.com/danyim/obsidian-custom-publish) |

MkDocs Material ([squidfunk/mkdocs-material](https://github.com/squidfunk/mkdocs-material) ⭐ 27k) and Hugo ([gohugoio/hugo](https://github.com/gohugoio/hugo) ⭐ 88k) are the obvious SSG backends but **neither has a per-page publish flag of its own**; for those you wire selective publishing at the *source* layer (Enveloppe, a custom pre-build script, or a separate folder mirror) [[14]](https://github.com/gohugoio/hugo) [[15]](https://github.com/squidfunk/mkdocs-material) [[16]](https://www.emgoto.com/obsidian-digital-garden/).

## The leak you don't see coming

Quartz documents the trap up front: *"all non-markdown files will be emitted and available publically in the final build. This includes files such as images, voice recordings, PDFs, etc."* [[2]](https://quartz.jzhao.xyz/features/private-pages). The opt-in flag only filters `.md` files. Everything else in the `content/` directory ships.

Concrete mitigations:

- **Mirror, don't host.** Keep notes in a private repo; have GitHub Actions copy only flagged content into the Quartz/SSG repo. The runtimeterror.dev write-up shows this with an `**/!(*.md)` pattern in `ignorePatterns` plus an explicit clone step [[11]](https://runtimeterror.dev/publish-silverbullet-notes-quartz/).
- **Publisher plugins, not vault sync.** Enveloppe and Quartz Syncer write only to a destination repo via API/PR — your vault never becomes the source of truth for the website [[3]](https://github.com/Enveloppe/obsidian-enveloppe) [[9]](https://github.com/saberzero1/quartz-syncer).
- **`.gitignore` the attachments folder** in the destination repo if you mirror manually.
- **Don't rely on a private source repo as a privacy boundary** for GitHub Pages itself. Free accounts can't even host Pages from a private repo; Pro/Team/Enterprise can, but the *built site* is still public unless you turn on access-controlled Pages [[12]](https://github.com/orgs/community/discussions/22817).

## Recommendation by use case

- **You want graph + backlinks like Obsidian Publish, free, on GitHub Pages.** Quartz + `ExplicitPublish`. Mirror notes into `content/` from a private vault repo via GitHub Actions [[1]](https://quartz.jzhao.xyz/plugins/ExplicitPublish) [[11]](https://runtimeterror.dev/publish-silverbullet-notes-quartz/).
- **You want a polished docs site, not a network of notes.** Enveloppe (`share: true`) → MkDocs Material in a separate repo [[3]](https://github.com/Enveloppe/obsidian-enveloppe) [[15]](https://github.com/squidfunk/mkdocs-material).
- **You hate maintaining frontmatter.** Quartz Syncer — pick notes from a UI per publish [[9]](https://github.com/saberzero1/quartz-syncer).
- **You want zero plumbing and don't mind paying.** Obsidian Publish; set the site to opt-in mode and use `publish: true` on the few notes you want exposed [[8]](https://unmarkdown.com/blog/obsidian-publish-alternatives).
- **You're already deep in [Hugo](https://gohugo.io/)/[Jekyll](https://jekyllrb.com/)/[Astro](https://astro.build/).** Don't bolt selective publishing onto the SSG itself — put a publisher plugin in front of it (Enveloppe or a frontmatter-aware mirror script). Native `draft: true` is opt-out and the wrong default for a private vault [[13]](https://gohugo.io/content-management/front-matter/) [[16]](https://www.emgoto.com/obsidian-digital-garden/).

## Self-check

Forum consensus aligns: cost-driven users settle on [Quartz](https://quartz.jzhao.xyz/), [Hugo](https://gohugo.io/) or [Jekyll](https://jekyllrb.com/) as the practical free trio, with Eleventy/Flowershow as smaller niches [[7]](https://forum.obsidian.md/t/obsidian-publish-alternatives/22886). Nothing in 2026 has displaced the opt-in frontmatter pattern as the default safe choice — and the non-markdown leak is still the single most-cited footgun.
