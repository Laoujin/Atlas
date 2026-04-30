---
title: "Knowledge-base patterns for a technical vault (2026)"
date: 2026-04-30
depth: deep
format: md
topic: "Knowledge-base patterns for a technical vault"
topic_raw: "Knowledge-base patterns for a technical vault"
issue: 49
tags: [obsidian, pkm, knowledge-management, technical-notes, zettelkasten, para, bases, dataview]
summary: "What actually works for a technical Obsidian vault in 2026: hybrid PARA+Zettel skeleton, Properties-first metadata, daily-note capture, MOCs over deep folders, and a small high-value plugin set."
citations: 84
reading_time_min: 14
cover: cover.svg
cost_usd: 7.23
duration_sec: 687
---

> **TL;DR / Decision.**
> For a technical vault in 2026, run a **PARA-shaped skeleton with Zettelkasten-style atomic notes inside Areas** [[1]](https://www.stefanimhoff.de/agentic-note-taking-obsidian-claude-code/) [[2]](https://medium.com/obsidian-observer/fusing-the-two-most-powerful-note-taking-systems-in-obsidian-331d7c4fb2df), put **typed Obsidian Properties** (not inline Dataview fields) at the centre of every queryable note with a mandatory `type` discriminator [[20]](https://chughkabir.com/guide-obsidian-bases/) [[14]](https://help.obsidian.md/properties), capture into a **daily-note inbox** via QuickAdd + Web Clipper and triage in a **weekly review** [[29]](https://github.com/chhoumann/quickadd) [[24]](https://obsidian.md/clipper) [[41]](https://forum.obsidian.md/t/capture-workflows/31085), navigate by **MOCs and backlinks** rather than deep folder trees [[48]](https://www.natecue.com/en/learn/productivity/map-of-content/), and let **Bases** replace Dataview tables now that it ships in core (1.9) [[16]](https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/) [[55]](https://medium.com/@lennart.dde/obsidian-dataview-is-dead-long-live-bases-9750e8a92877). If you publish, **Quartz v4** is the closest free analogue to Obsidian Publish [[77]](https://quartz.jzhao.xyz/). ⚠ Pure Zettelkasten alone misfits technical material — split by content type (snippets, tools, runbooks) [[10]](https://forum.obsidian.md/t/developer-how-to-tech-notes/75794).

---

## 1. Pick the organisational pattern — hybrid wins

Six named systems show up in 2026 technical-vault writeups. None survives intact; the winners are hybrids, and the consensus heuristic is **structure must be earned** [[3]](https://blog.linkingyourthinking.com/notes/ace-folder-framework).

| Pattern | What it is | Fit for a technical vault | 2026 status |
|---|---|---|---|
| **PARA + Zettelkasten** | Top-level Projects/Areas/Resources/Archives, atomic notes inside | ✓ Best documented hybrid; engineer running 6k notes uses numbered `00–99` layout [[1]](https://www.stefanimhoff.de/agentic-note-taking-obsidian-claude-code/) | Dominant default [[2]](https://medium.com/obsidian-observer/fusing-the-two-most-powerful-note-taking-systems-in-obsidian-331d7c4fb2df) |
| **LYT / ACE** | Atlas (knowledge) / Calendar (time) / Efforts (action) + `+` inbox + `X` meta | ✓ Cleaner than ACCESS; topical structure pushed into MOCs not folders [[47]](https://blog.warrenweb.net/ace/) | Current LYT shipping artifact is **Ideaverse Pro** with ACE + ARC (Add/Relate/Communicate) [[46]](https://www.linkingyourthinking.com/ideaverse-pro) |
| **ACCESS** (LYT v1) | Six folders: Atlas, Calendar, Cards, Extras, Sources, Spaces | ⚠ Author called it a starting template, "not the gospel" [[4]](https://x.com/nickmilo/status/1530162446459019265) | Superseded by ACE [[3]](https://blog.linkingyourthinking.com/notes/ace-folder-framework) |
| **Johnny Decimal** | Numeric IDs (`61.14 Bill`) inside `ALPPS` folders | ⚠ Friction-as-feature for some; scaling pain past ~100 IDs/category [[5]](https://medium.com/@geetduggal/tech-habits-how-i-moved-into-my-johnny-decimal-and-obsidian-bases-system-for-organizing-notes-6bc7a00747e7) [[6]](https://forum.obsidian.md/t/q-for-those-using-johnny-decimal-system/87070) | Niche but vocal; pairs well with Bases [[5]](https://medium.com/@geetduggal/tech-habits-how-i-moved-into-my-johnny-decimal-and-obsidian-bases-system-for-organizing-notes-6bc7a00747e7) |
| **Folderless / Jellyfish** | Everything in one folder; structure via Properties + Bases | ✓ Steph Ango (Obsidian CEO) runs near-folderless vault, routes via `categories` property [[7]](https://stephango.com/vault); Jellyfish dumps all notes in one folder, organises via YAML + Dataview [[8]](https://ajy.co/how-i-organize-my-notes-in-obsidian-the-jellyfish-vault/) | Viable only with strong metadata discipline |
| **Pure Zettelkasten** | Atomic, ID-prefixed notes only; no folders | ✗ "Does not adjust very good when writing technical documents" — forum consensus [[10]](https://forum.obsidian.md/t/developer-how-to-tech-notes/75794) | Better split by content type: snippets, tools, runbooks, conceptual notes [[10]](https://forum.obsidian.md/t/developer-how-to-tech-notes/75794) |

**The recommended 2026 default for technical work:** three-layer hybrid — shallow folders (≤ 2 deep) for type separation, MOCs for navigation, tags for cross-cutting filter signals not structure [[9]](https://blog.shuvangkardas.com/obsidian-note-organization/). A widely-shared 2026 reset reduces this to five buckets — `Inbox / System / Active / Vault / Recipes` — with a Capture → Tag → Backlink workflow [[12]](https://www.xda-developers.com/used-obsidian-wrong-for-year-folder-setup-that-finally-clicks/).

⚠ **Scaling caveat.** A Zettelkasten practitioner reports the native graph view becomes unusable at ~6k notes even on an M4 Mac mini, forcing external tools like Cosmograph for actual network exploration [[13]](https://wasi0013.com/2025/09/22/data-visualization-challenge-the-struggle-to-visualize-thousands-of-zettelkasten-notes-and-how-i-solved-it/). Plan for graph-view rot, not perpetual usefulness.

---

## 2. Metadata: Properties first, Dataview-inline last

Obsidian's metadata story consolidated in 2025–26 around **typed Properties** stored in YAML frontmatter. The supported types are text, list, number, checkbox, date, and date & time — with `tags` as a special list-typed property [[14]](https://help.obsidian.md/properties). The hard schema constraint: **a property name carries one type across the entire vault** [[15]](https://deepwiki.com/obsidianmd/obsidian-help/4.3-properties-and-metadata) — decide once whether `status` is `text` or `list`, then live with it.

### Why Bases changed the calculus

The **Bases** core plugin (Obsidian 1.9, May 2025) [[16]](https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/) turned Properties into a database surface: visual editor, three-component filters (property/operator/value with and/or/not), formulas, table views, in-line cell editing that writes back to YAML, and a new `.base` file format [[17]](https://practicalpkm.com/bases-plugin-overview/) [[54]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/). Bases reads only formal Properties — **inline `key:: value` Dataview fields are ignored** [[17]](https://practicalpkm.com/bases-plugin-overview/) — which has pushed practitioners off Dataview's inline idiom onto pure YAML, also motivated by Dataview being effectively unmaintained and laggy on heavy queries [[18]](https://blacksmithgu.github.io/obsidian-dataview/annotation/add-metadata/) [[19]](https://robcoles.net/posts/dataview-and-inline-to-datacore-bases-and-yaml/). Power users in 2026 report replacing every Dataview query with a Bases table [[55]](https://medium.com/@lennart.dde/obsidian-dataview-is-dead-long-live-bases-9750e8a92877). Meta Bind is the bridge that keeps YAML values editable inline [[19]](https://robcoles.net/posts/dataview-and-inline-to-datacore-bases-and-yaml/).

### A schema that survives bit-rot

The 2026 convention for queryable technical notes:

| Property | Type | Value space (example) |
|---|---|---|
| `type` | text | `snippet`, `howto`, `reference`, `project`, `runbook`, `daily` — mandatory discriminator [[20]](https://chughkabir.com/guide-obsidian-bases/) |
| `status` | text | `seed`, `growing`, `evergreen`, `archived` (one type per name, vault-wide) [[15]](https://deepwiki.com/obsidianmd/obsidian-help/4.3-properties-and-metadata) |
| `tags` | list | plural form mandatory; `tag` (singular) deprecated as of 1.9 [[21]](https://forum.obsidian.md/t/tags-in-the-era-of-yaml-front-matter-abundance/18328) |
| `aliases`, `cssclasses` | list | plural forms; singular deprecated [[21]](https://forum.obsidian.md/t/tags-in-the-era-of-yaml-front-matter-abundance/18328) |
| `language` | text | `python`, `rust`, `bash` (free-text but autocomplete prevents drift) [[22]](https://obsidian.rocks/an-introduction-to-obsidian-properties/) |
| `source` | text or list | URL of capture origin |
| `created`, `updated` | date / datetime | ISO 8601 (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM`) for reliable sort [[21]](https://forum.obsidian.md/t/tags-in-the-era-of-yaml-front-matter-abundance/18328) |

Define these once in a **master-schema note** [[20]](https://chughkabir.com/guide-obsidian-bases/) and seed every new note from a template. Obsidian's autocomplete on existing property keys is the cheapest tool for preventing drift like `status` vs `progress` or `due_date` vs `deadline` [[22]](https://obsidian.rocks/an-introduction-to-obsidian-properties/). Bases function names moved snake_case → camelCase in 1.9.1, signalling the formula syntax is stabilising as a public schema [[23]](https://obsidian.md/changelog/2025-05-22-desktop-v1.9.1/).

---

## 3. Capture stack — daily note as universal inbox

The 2026 capture stack consolidated around a **free, official-first core**. The pattern: every input lands as a timestamped bullet in today's daily note (or in a single `Inbox/` folder), and a **weekly review** triages and routes [[41]](https://forum.obsidian.md/t/capture-workflows/31085) [[31]](https://medium.com/illumination/my-obsidian-setup-part-13-inbox-folder-quick-note-capture-workflow-5ae03407e832).

### Web and reference

| Input | Tool | Why |
|---|---|---|
| Articles, selections | **Obsidian Web Clipper** [[24]](https://obsidian.md/clipper) [[63]](https://github.com/obsidianmd/obsidian-clipper) ⭐ 4.1k (Apr 2026) | Free, official, cross-browser; template-driven metadata extraction; the 2026 update added YouTube transcript capture and a tunable Reader Mode [[42]](https://digitalbiztalk.com/article/obsidian-web-clipper-s-youtube-transcripts-reader-mode-in-2026) |
| Heavy in-line annotation | **Readwise Reader** + plugin [[26]](https://docs.readwise.io/readwise/docs/exporting-highlights/obsidian) | Append-only, Jinja2 templates; reviewers position it above the native clipper for annotation-heavy flows [[25]](https://web2md.org/blog/best-web-clipper-obsidian-ai-2026) |
| Web annotations | **Hypothes.is** plugin [[27]](https://github.com/weichenw/obsidian-hypothesis-plugin) ⭐ 270 | Syncs highlights/annotations on startup or manual trigger; Nunjucks templates |
| Academic PDFs | **PDF++** [[33]](https://github.com/RyotaUshio/obsidian-pdf-plus) ⭐ 2.2k + **Paper Clipper** [[34]](https://github.com/ras0q/obsidian-paper-clipper) ⭐ 22 | PDF++ stores highlights as Markdown backlinks (not embedded), so they survive the plugin disappearing |

### Code, terminal, screenshots

| Input | Tool | Notes |
|---|---|---|
| Code snippets | **SnippetBase** [[37]](https://forum.obsidian.md/t/new-plugin-a-code-snippet-organizer/109645) | Indexes every fenced block across the vault; filter by folder/language; search; favorites; copy-to-clipboard |
| Live terminal | **Obsidian Terminal** [[35]](https://www.blog.brightcoding.dev/2026/02/07/obsidian-terminal-the-revolutionary-shell-integration-every-developer-needs) | xterm.js, ANSI-aware, regex find, full-session export to Markdown |
| Static command + output | **Console Markdown** [[36]](https://www.obsidianstats.com/plugins/console) | Renders fenced ```` ```console ```` blocks as styled command/output panels |
| Screenshots | OS shortcut → **Fleeting Notes** [[39]](https://www.fleetingnotes.app/posts/take-annotated-screenshots-into-obsidian) → vault | Cmd+Ctrl+Shift+4 / Win+Shift+S, paste, annotate, sync |
| Re-export images | **Copy Image** [[40]](https://github.com/felipe-ds-lima/obsidian-copy-image-plugin) ⭐ 19 | Right-click image in note → clipboard, for ticket/chat re-paste |
| Obsidian internal errors | **Logstravaganza** [[38]](https://github.com/czottmann/obsidian-logstravaganza) ⭐ 46 | Proxies `console.*()` and uncaught exceptions to NDJSON, table, or code-block files |

### Triage primitives

- **QuickAdd** [[29]](https://github.com/chhoumann/quickadd) ⭐ 2.2k (Apr 2026) — single command appends a timestamped bullet to today's note, creating it if missing. The capture engine.
- **Templater + Advanced URI + Hotkeys for Templates** [[28]](https://forum.obsidian.md/t/quick-capture-mac-ios-and-inbox-processing/21808) — Mac/iOS pattern: Opt+A/D/M to archive/trash/move during inbox triage; the next note auto-opens.
- **Inbox Organiser** [[30]](https://www.obsidianstats.com/plugins/inbox-organiser) — periodic nag prompting you to file unprocessed inbox notes.
- ⚠ **Mobile capture** is the loudest pain point on r/ObsidianMD; official quick capture is on the roadmap, but most users currently bridge with Quick Draft, Fleeting Notes, or an Android home-screen widget that writes to daily notes [[32]](https://forum.obsidian.md/t/your-mobile-quick-capture-solution/102085).

Forum consensus: **capture first, organise later** — categorising at capture time kills creativity [[41]](https://forum.obsidian.md/t/capture-workflows/31085). Pair Web Clipper with Dataview/Linter/Auto Note Mover so clipped notes land in inbox, get cleaned, and surface in dashboards rather than rot unread [[43]](https://www.savemarkdown.co/blog/obsidian-plugins-web-clipping-workflow-2026).

---

## 4. Linking strategy — atomic notes, MOC navigation, tags as state

Andy Matuschak's two load-bearing rules anchor the technical end of the spectrum:

1. **Atomicity** → "only about one thing… capture the entirety of that thing… separate concerns from one another" [[44]](https://notes.andymatuschak.org/Evergreen_notes_should_be_atomic).
2. **Concept-orientation** → factor by concept rather than by author/book/event/project, so synthesis pressure surfaces cross-domain links [[45]](https://notes.andymatuschak.org/Evergreen_notes_should_be_concept-oriented).

### MOCs vs folders vs tags

| Axis | Folder | MOC | Tag |
|---|---|---|---|
| A note can belong to many | ✗ | ✓ | ✓ |
| Carries annotated commentary | ✗ | ✓ | ✗ |
| Restructure cost | rename + move | edit wikilinks | rename tag globally |
| Appears as graph node | ✗ | ✓ | ✗ (filter only) |
| Source | [[48]](https://www.natecue.com/en/learn/productivity/map-of-content/) | [[48]](https://www.natecue.com/en/learn/productivity/map-of-content/) | [[48]](https://www.natecue.com/en/learn/productivity/map-of-content/) |

Forum heuristic that tracks well in technical vaults: **folders for project/output workflows, links for PKM, tags treated skeptically** [[49]](https://forum.obsidian.md/t/folders-vs-linking-vs-tags-the-definitive-guide-extremely-short-read-this/78468). Eleanor Konik defends folders for cross-tool/automation backwards-compatibility and reserves tags for **verb-based action metadata** like `#FollowUp`, `#addmoc`, `#articleseed` [[50]](https://www.eleanorkonik.com/p/yet-another-hot-take-on-folders-versus-tags). The tags-as-status camp pushes further — `#unread`, `#idle`, `#processing`, `#shaped`, `#🌱 seedling`, `#🌲 evergreen` — because state mutates and shouldn't pollute the link graph [[51]](https://www.dsebastien.net/2022-05-17-why-and-how-to-tag-notes-in-your-pkm/).

The recommended hybrid: **tags for top-down "is-a" classification and status; topic notes/MOCs as bottom-up emergent hubs**, and don't promote a cluster into an MOC until the content density earns it ("you have to create the content before you can map it") [[52]](https://wanderloots.xyz/digital-garden/tutorials/how-i-use-tags-and-topic-notes-for-structured-and-emergent-organization/). One opposed-but-pragmatic voice: a three-year-tested workflow rejects MOCs entirely in favour of nested-tag search as the primary discovery mechanism, arguing nested tags express hierarchy that links cannot [[11]](https://forum.obsidian.md/t/an-opinionated-reflection-on-using-folders-links-tags-and-properties/78548).

⚠ Past ~2k notes manual MOC upkeep breaks. **AutoMOC** auto-imports backlinks, tagged mentions, and aliases into the open MOC; **Backlink Cache** materially speeds the Backlinks pane [[53]](https://www.navthemes.com/automatically-add-moc-links-in-obsidian-workflow-automation-tips-explained/).

---

## 5. Plugins worth installing in 2026

Bases shipped → DB Folder and the original Projects plugin are dead → the AI plugin field has two viable contenders. Stars below are current as of Apr 2026.

### Core query/data layer

| Plugin | Stars | Status | Purpose |
|---|---|---|---|
| **Bases** (core) | n/a | ✓ Shipped 1.9 [[16]](https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/) | No-code visual database; replaces Dataview tables for most users [[54]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/) [[55]](https://medium.com/@lennart.dde/obsidian-dataview-is-dead-long-live-bases-9750e8a92877) |
| **Dataview** | — | ⚠ Stagnant; keep for legacy queries [[19]](https://robcoles.net/posts/dataview-and-inline-to-datacore-bases-and-yaml/) | Inline-field queries; `key:: value`; DQL/JS [[18]](https://blacksmithgu.github.io/obsidian-dataview/annotation/add-metadata/) |
| **Datacore** | — | ⚠ Beta | React-based heir for interactive components [[54]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/) |
| **DB Folder** | ⭐ 1.4k | ✗ Archived Jul 2025 [[59]](https://github.com/RafaelGB/obsidian-db-folder) | Migrate to Bases or Datacore |

### Capture + automation

| Plugin | Stars | Purpose |
|---|---|---|
| **Templater** [[56]](https://github.com/SilentVoid13/Templater) | ⭐ 4.9k | JS-capable templating engine; actively released |
| **QuickAdd** [[29]](https://github.com/chhoumann/quickadd) | ⭐ 2.2k | Capture macros; daily-note bullet primitive |
| **Obsidian Web Clipper** [[63]](https://github.com/obsidianmd/obsidian-clipper) | ⭐ 4.1k | Official browser extension; YouTube transcripts in 2026 |
| **Linter** [[58]](https://github.com/platers/obsidian-linter) | ⭐ 1.9k | 80+ rules over YAML, headings, footnotes, spacing |
| **Excalidraw** [[57]](https://github.com/zsviczian/obsidian-excalidraw-plugin) | ⭐ 6.8k | Embedded sketches, LaTeX, OCR, script API |

### AI / semantic layer

| Plugin | Stars | Notes |
|---|---|---|
| **Smart Connections** [[61]](https://github.com/brianpetro/obsidian-smart-connections) | ⭐ 4.9k | Local-first by default (no API key); optional 100+ models |
| **Copilot** (logancyang) [[62]](https://github.com/logancyang/obsidian-copilot) | ⭐ 6.8k | Vault chat + agent mode; PDF/EPUB ingestion; diff edits in Plus tier |

### Maintenance

- **Find Orphaned Files and Broken Links** [[72]](https://www.obsidianstats.com/plugins/find-unlinked-files) — markdown report of unbacklinked notes and dangling wikilinks.
- **Broken Links** [[73]](https://www.obsidianstats.com/plugins/broken-links) — folder/file/consolidated views of links pointing to missing files, headings, blocks.
- **Nuke Orphans** [[74]](https://github.com/sandorex/nuke-orphans-plugin) ⭐ 53 — destructive cleanup of orphaned attachments; behind a confirmation prompt.
- **AutoMOC + Backlink Cache** [[53]](https://www.navthemes.com/automatically-add-moc-links-in-obsidian-workflow-automation-tips-explained/) — keep MOCs and the Backlinks pane fast at 2k+ notes.
- **Periodic Notes** [[70]](https://forum.obsidian.md/t/my-workflow-for-periodic-weekly-monthly-quarterly-yearly-reviews-in-obsidian/23310) — daily/weekly/monthly/quarterly/yearly review templates.

### Casualties to remove

| Plugin | Status |
|---|---|
| **Projects** (marcusolsson) [[60]](https://marcusolsson.dev/projects/) | Archived Jul 2025; community fork `obsmd-projects` carries it forward — replace with Bases or Datacore |

### If you're thinking of leaving Obsidian

| Tool | Stars | Best for | Trade-off |
|---|---|---|---|
| **Foam** [[64]](https://github.com/foambubble/foam) | ⭐ 17k | Devs who already live in VS Code; notes alongside source | Leans on extensions for what Obsidian gives natively |
| **SilverBullet** [[66]](https://github.com/silverbulletmd/silverbullet) | ⭐ 5.2k | Self-hosters; Lua scripting, Objects/Queries, PWA, offline-first | Web-first UX, smaller plugin pool |
| **Logseq** | — | Rapid block-outline capture | ⚠ Flat structure feels chaotic for technical reference [[65]](https://dev.to/dev_tips/obsidian-notion-logseq-the-note-taking-stack-that-doesnt-suck-for-devs-2cf7) |
| **Tana** | — | Structure-first PKM; supertags impose typed schemas on outline nodes [[67]](https://www.xda-developers.com/tana-supertags-review/) | Proprietary, no file portability |
| **Reflect** | — | Calendar-bound meeting notes; selectable GPT-4o/Claude Sonnet [[68]](https://get-alfred.ai/blog/best-ai-note-taking-apps) | $10/mo paid-only |

For developers wanting CLI integration, large-vault performance, and Git-friendly Markdown, **Obsidian still wins** — the 2026 release of an official Obsidian CLI widened the gap with Logseq for technical workflows [[69]](https://dasroot.net/posts/2026/03/obsidian-logseq-notion-pkm-systems-compared-2026/) [[65]](https://dev.to/dev_tips/obsidian-notion-logseq-the-note-taking-stack-that-doesnt-suck-for-devs-2cf7).

---

## 6. Maintenance and publishing — review cadence + hygiene + a way out

### Review cadence

The dominant pattern uses **Periodic Notes** to nest daily / weekly / monthly / quarterly / yearly review templates, where each tier rolls up the tier below [[70]](https://forum.obsidian.md/t/my-workflow-for-periodic-weekly-monthly-quarterly-yearly-reviews-in-obsidian/23310). Weekly reviews almost universally embed Dataview queries that resurface fleeting notes, unfinished tasks, and untouched material — the gardener triages instead of re-discovers [[71]](https://forum.obsidian.md/t/daily-and-weekly-reviews-dataview/17021).

### Hygiene

| Job | Plugin |
|---|---|
| Unbacklinked notes + dangling wikilinks report | Find Orphaned Files and Broken Links [[72]](https://www.obsidianstats.com/plugins/find-unlinked-files) |
| Triage links to missing files/headings/blocks | Broken Links [[73]](https://www.obsidianstats.com/plugins/broken-links) |
| Trash orphaned attachments (with confirm) | Nuke Orphans [[74]](https://github.com/sandorex/nuke-orphans-plugin) ⭐ 53 |
| Refactor practice | Matuschak evergreens (atomic, concept-oriented, rewritten over time) [[75]](https://notes.andymatuschak.org/Evergreen_notes); Maggie Appleton's progressive-summarisation loop — re-read, bold, split, re-link [[76]](https://maggieappleton.com/evergreens) |

### Publishing

| Tool | Cost | Strength | When to pick |
|---|---|---|---|
| **Quartz v4** [[77]](https://quartz.jzhao.xyz/) | free | Closest free analogue to Publish: Obsidian compat, full-text search, graph view, wikilinks, transclusions, backlinks, LaTeX, syntax highlighting, popovers, i18n | Default for free public garden; ~30–60 min initial setup [[78]](https://unmarkdown.com/blog/obsidian-publish-alternatives) |
| **Obsidian Publish** [[78]](https://unmarkdown.com/blog/obsidian-publish-alternatives) | $8–10/mo | Zero-config from inside the app | When you'll pay to skip ops |
| **Material for MkDocs** [[80]](https://squidfunk.github.io/mkdocs-material/) | free | Polished docs theme | Vault is more documentation than garden |
| **Astro Starlight** [[81]](https://starlight.astro.build/) | free | Fast docs theme on Astro framework | JS-leaning gardeners migrating from MkDocs |
| **Flowershow / Hugo / Jekyll / Eleventy / Enveloppe / Share Note** [[78]](https://unmarkdown.com/blog/obsidian-publish-alternatives) | free or $50/yr | Various trade-offs | Need a specific deployment target |

The **canonical Quartz workflow** keeps the vault as source-of-truth and gates publication via `publish: true` frontmatter using Quartz's `ExplicitPublish` filter, with attachments protected by a `public-` filename prefix [[79]](https://oliverfalvai.com/evergreen/my-quartz-+-obsidian-note-publishing-setup).

### Public gardens to study

- **Maggie Appleton's garden** [[82]](https://maggieappleton.com/garden/) — visual essays on programming, design, anthropology arranged non-linearly with categories, tags, curated imagery; the canonical "what good looks like".
- **Joel Hooks** [[83]](https://joelhooks.com/digital-garden/) — explicit non-blog frame; perpetually-edited notes.
- **best-of-digital-gardens** [[84]](https://github.com/lyz-code/best-of-digital-gardens) ⭐ 531 — ranked inventory of public second-brain sites; benchmarks for layout, linking density, update cadence.

---

## What to do in the next hour

1. Pick PARA + Zettel as skeleton; create `00 MOCs / 01 Projects / 02 Areas / 03 Resources / 04 Permanent / 05 Fleeting / 06 Daily / 07 Archives / 99 Meta` if starting fresh [[1]](https://www.stefanimhoff.de/agentic-note-taking-obsidian-claude-code/), or migrate gradually if you have an existing tree.
2. Write a master-schema note declaring every Property name + type [[20]](https://chughkabir.com/guide-obsidian-bases/); migrate a handful of inline `key:: value` fields to YAML to feed Bases [[17]](https://practicalpkm.com/bases-plugin-overview/).
3. Install QuickAdd, Web Clipper, Templater, Linter, Periodic Notes, Find Orphaned Files [[29]](https://github.com/chhoumann/quickadd) [[24]](https://obsidian.md/clipper) [[56]](https://github.com/SilentVoid13/Templater) [[58]](https://github.com/platers/obsidian-linter) [[70]](https://forum.obsidian.md/t/my-workflow-for-periodic-weekly-monthly-quarterly-yearly-reviews-in-obsidian/23310) [[72]](https://www.obsidianstats.com/plugins/find-unlinked-files); turn on Bases (core) [[16]](https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/).
4. Make the daily note your inbox; schedule a weekly-review note from a Periodic Notes template [[41]](https://forum.obsidian.md/t/capture-workflows/31085) [[71]](https://forum.obsidian.md/t/daily-and-weekly-reviews-dataview/17021).
5. Defer publishing until the vault is dense enough to prune — then Quartz v4 [[77]](https://quartz.jzhao.xyz/).
