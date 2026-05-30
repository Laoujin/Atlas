---
title: "Obsidian Bases: turn reference notes into live views"
date: 2026-05-30
depth: deep
format: md
topic: "Bases: turn existing reference notes into live views"
topic_raw: "Bases: turn existing reference notes into live views"
issue: 109
tags: [obsidian, bases, pkm, dataview, properties]
summary: "How to convert a folder or tag of reference notes into a live, editable, filterable view using Obsidian Bases — the .base format, the conversion workflow, ready-to-steal recipes, the formula language, and where Dataview still wins."
citations: 42
reading_time_min: 11
cover: cover.svg
cost_usd: 6.92
duration_sec: 731
---

> **TL;DR** — A [Base](https://obsidian.md/help/bases) is a YAML file that points at a folder or tag, treats every matching note's frontmatter as a row, and renders the result as a sortable, filterable, editable table or card grid [[1]](https://obsidian.md/help/bases). For an intermediate user with messy reference notes, the upgrade path is: (1) add 2-4 consistent properties to the notes you want to query, (2) `Bases: Create new base`, (3) filter by folder/tag, (4) tick the properties you want as columns, (5) save named views. It shipped in Obsidian 1.9 on **May 21, 2025** [[3]](https://www.neowin.net/news/obsidian-190-launches-with-new-file-format-footnotes-view-plugin-and-more/) and is the first-party answer to [Dataview](https://github.com/blacksmithgu/obsidian-dataview) ⭐ 9.0k (May 2026) [[8]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/) — but it only reads YAML frontmatter, not inline `key::value` or inline tasks, which is the one rewrite the migration will force [[24]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/#limitations) [[30]](https://forum.obsidian.md/t/dataview-vs-bases/113073).

## What Bases actually is

A Base is a `.base` file (YAML) that defines filters over your vault and renders the matching notes as a database-style view [[1]](https://obsidian.md/help/bases). Rows are notes; columns are YAML properties. Editing a cell writes back to that note's frontmatter, so the view is fully live in both directions [[5]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/). Bases shipped as a core plugin in Obsidian 1.9 (Desktop early access **May 21, 2025**) [[3]](https://www.neowin.net/news/obsidian-190-launches-with-new-file-format-footnotes-view-plugin-and-more/), was refined in 1.9.2 with file-level properties like `file.path`, `file.links`, `file.tags` and object-oriented chained syntax [[4]](https://obsidian.md/changelog/2025-06-05-desktop-v1.9.2/), and gained a List view plus a Bases plugin API in 1.10 [[2]](https://obsidian.md/blog/2025-obsidian-october/). Community framing: "biggest update since Properties" [[7]](https://medium.com/obsidian-observer/obsidians-new-bases-feature-is-the-biggest-update-since-properties-2aad08a102eb).

Bases is the GUI query layer over the Properties feature — every column is a frontmatter key. That means **you can't query notes that have no frontmatter**, and the first concrete adoption step for an intermediate user is usually adding 2-4 consistent properties to a folder of existing reference notes.

## The five-step conversion workflow

The mechanical click-path to turn a folder of reference notes into a live view:

1. **Stamp properties.** Open each note, use `Cmd/Ctrl+;` to add at least one shared property (e.g. `type: book`, `status: read`, `rating: 4`). The fastest mass-edit is Obsidian's Properties view in the right-hand sidebar — select multiple notes in the file explorer and set a property across all of them at once. Without consistent frontmatter, Bases has nothing to query [[24]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/#limitations).
2. **Create the base.** Command palette → `Bases: Create new base` drops a `.base` next to the active note; `Bases: Insert new base` embeds one in the current note; right-click any folder → `New base` scopes it to that folder [[9]](https://obsidian.md/help/bases/create-base).
3. **Set the global filter.** Top-right "Filters" → pick `file` → `has tag` (or `in folder`, or a property comparison). Three idioms cover 90% of cases: `file.inFolder("Books")`, `file.hasTag("book")`, `type == "book"` [[13]](https://obsidian.rocks/getting-started-with-obsidian-bases/).
4. **Pick columns.** "Properties" panel → tick the frontmatter keys you want as columns. A pragmatic starter set: `file.name`, two or three note properties, and a throwaway `file.path` you delete once the filter is right [[14]](https://got.md/obsidian-bases/).
5. **Save named views.** Click the view-name dropdown top-left → "Add view" (or `Bases: Add view`). Each view stores its own type, filters, ordering, and limit — so "All books", "To read", "5★" can coexist as tabs in one base [[10]](https://obsidian.md/help/bases/syntax).

## Anatomy of a .base file

A `.base` is YAML with five top-level keys [[10]](https://obsidian.md/help/bases/syntax):

```yaml
filters:    # global conditions applied to every view
formulas:   # custom calculated properties
properties: # display config for columns
summaries:  # custom aggregations
views:      # one or more named views (table / cards / list / map)
```

Filters compose with nested `and` / `or` / `not` blocks combining file functions (`file.hasTag()`, `file.inFolder()`, `file.hasLink()`) and property comparisons [[4]](https://obsidian.md/changelog/2025-06-05-desktop-v1.9.2/). Filters apply in two layers: a global filter selects a subset of the vault, then each view further prunes that subset [[6]](https://blog.optional.page/misc/bases/).

Bases ships four built-in view types:

| View  | Added in     | Use for                                    |
| ----- | ------------ | ------------------------------------------ |
| Table | 1.9 (May'25) | Spec-style comparisons, editable grids     |
| Cards | 1.9 (May'25) | Image-led views (books, films, recipes)    |
| List  | 1.10 (Oct'25)| Bullets / numbered indexes                 |
| Map   | 1.10 (Oct'25)| Pinned locations (needs Maps plugin) ⚠     |

Source: official Views docs [[11]](https://obsidian.md/help/bases/views). Cards take a `cover` property (wiki-link, URL, or hex colour) and a fit setting of `cover` or `contain` — that's the "gallery" pattern, there's no separate gallery view type [[12]](https://obsidian.md/help/bases/views/cards).

You can embed a Base inline with a ```` ```base ```` code fence, or transclude a standalone file with `![[Library.base]]` or `![[Library.base#5★]]` to pin a specific view [[10]](https://obsidian.md/help/bases/syntax).

## Steal these recipes

### Book library

The reference-standard public example is [uroybd/Book-Base](https://github.com/uroybd/Book-Base) ⭐ 16 (May 2026) — a full vault with six views (All Books, Queue, Published, Series Cards, By Year, Current Year) [[15]](https://github.com/uroybd/Book-Base/blob/main/Personal/Reading/Books/Index.base):

```yaml
filters:
  and:
    - file.folder.contains("Personal/Reading/Books")
    - file.ext != "base"
formulas:
  Title: link(file.path, title)
  Rating: if(rating == null, "N/A", ["⭐", rating.toString()].join(" "))
  Cover: image(cover)
```

For a simpler start, the [Practical PKM](https://practicalpkm.com/from-books-to-bases/) book-library recipe filters by folder and ships three views: a default table, a primary cards view (cover/author/rating/pages), and a "5 Star Books" cards filtered on `rating == 5` [[16]](https://practicalpkm.com/from-books-to-bases/). For yearly reading logs, the array-property pattern is `readDates.filter(value.toString().contains("2025"))` [[17]](https://tamarisk.it/tracking-reading-with-obsidian-bases).

### Project / task tracker

The canonical [forum template](https://forum.obsidian.md/t/a-bases-template-for-project-tracking-or-task-management/104249) standardises four keys — `status`, `passion` (1-5), `deadline` (datetime), `progress` (0-100) — and uses display-formula columns for emoji ratings and progress bars [[18]](https://forum.obsidian.md/t/a-bases-template-for-project-tracking-or-task-management/104249):

```yaml
status: In Progress
passion: 5
deadline: 2025-08-19T12:51:00
progress: 60
```

The companion "home base" tutorial filters by `file.tags.containsAny("projects","exam")` with priority + due-date sort [[19]](https://forum.obsidian.md/t/my-home-base-tutorial/108759).

### Meetings + people (inverse-link pattern)

Two bases hang off a `Type: Meeting` note schema with `Attendees` and `Projects` link-list properties. Inside a person's note, an embedded base filters `Type == "Meeting" AND Attendees.contains(this.file)`; inside a project's note, swap `Attendees` for `Projects` [[20]](https://effortlessacademic.com/meeting-note-template-and-base-for-organising-meetings-and-attendees-obsidian/). This is the single most useful Bases trick for intermediate users — it lights up the graph by reading existing links as data.

### Media log

[Obsidian-TV-Tracker](https://github.com/Shreshth-mehra/Obsidian-TV-Tracker) ⭐ 25 (May 2026) defines a ready-to-use movie/TV frontmatter shape — `title`, `type`, `status` (Watchlist / Watched / In Progress / Complete / Incomplete), `priority`, `rating`, `dates`, `progress`, external link — that drops straight into a Bases source schema with no rework [[21]](https://github.com/Shreshth-mehra/Obsidian-TV-Tracker).

### Recipes

The community [recipe-sheet template](https://forum.obsidian.md/t/recipe-sheet/69954) tags notes `#🍽️/recipe` and uses a multi-select `ingredients` property (curated from ~300 common ingredients via Metadata Menu) — directly portable to a Bases `ingredients.contains("garlic")` filter [[23]](https://forum.obsidian.md/t/recipe-sheet/69954).

### Daily-notes "On This Day"

A daily-notes base parses the filename as a date and exposes month/day/year as formula columns, then filters on `month == today().month && day == today().day` for a flashback view [[19]](https://forum.obsidian.md/t/my-home-base-tutorial/108759).

### Base-of-Bases home page

A cards-view index of every other base, using `file.basename + ".jpg"` as the cover-image formula, makes a visual launcher [[22]](https://forum.obsidian.md/t/bases-of-bases-with-thumbnail-images/104962).

## The formula layer — what "live" actually means

Every column can be a stored property or a computed formula [[10]](https://obsidian.md/help/bases/syntax). The formula language is small and learnable in an afternoon. Operators: arithmetic `+ - * / % ()`, comparison `== != > < >= <=`, boolean `! && ||`. Dates accept duration-string arithmetic: `date + "1M"`, `date - "2h"` [[41]](https://obsidian.md/help/bases/functions) [[4]](https://obsidian.md/changelog/2025-06-05-desktop-v1.9.2/).

Each note row exposes a `file.*` object alongside user frontmatter [[4]](https://obsidian.md/changelog/2025-06-05-desktop-v1.9.2/):

| Built-in       | What it gives you                            |
| -------------- | -------------------------------------------- |
| `file.name`    | filename (without `.md`)                     |
| `file.path`    | full vault path                              |
| `file.folder`  | parent folder path                           |
| `file.tags`    | list of tags                                 |
| `file.links`   | list of internal links                       |
| `file.ctime`   | created datetime                             |
| `file.mtime`   | last-modified datetime                       |
| `file.size`    | bytes on disk                                |

Global functions cover `if(cond, then, else?)`, `now()`, `today()`, `date()`, `duration()`, `link()`, `list()`, `min/max`, `number()`, `image()`, `icon()` [[41]](https://obsidian.md/help/bases/functions). Date values expose `.year/.month/.day/.hour`, `.format()` (formatting tokens), `.relative()` ("3 days ago"); subtracting two dates yields a Duration unwrapped via `.days` / `.hours` [[4]](https://obsidian.md/changelog/2025-06-05-desktop-v1.9.2/). Lists chain `.filter()`, `.map()`, `.reduce()`, `.contains*`, `.join()`, `.unique()`, `.sort()` [[4]](https://obsidian.md/changelog/2025-06-05-desktop-v1.9.2/).

Useful starter formulas:

| Result                | Formula                                                                  |
| --------------------- | ------------------------------------------------------------------------ |
| Overdue badge         | `if(due && status != "Done" && due < today(), "Overdue", "")`            |
| Days until due        | `((due - today()) / 86400000).round()`                                   |
| Relative edit time    | `file.mtime.relative()`                                                  |
| Group key (areas)     | `list(area).unique().sort().join(", ")`                                  |
| Rating stars          | `if(rating == null, "N/A", ["⭐", rating.toString()].join(" "))`         |
| Cover image           | `image(cover)`                                                           |

The first three from [optional.page](https://blog.optional.page/misc/bases/) [[10]](https://obsidian.md/help/bases/syntax); rating/cover from [uroybd/Book-Base](https://github.com/uroybd/Book-Base) ⭐ 16 (May 2026) [[15]](https://github.com/uroybd/Book-Base/blob/main/Personal/Reading/Books/Index.base). **Live-update gotcha:** edits made through Obsidian's properties UI re-render the open Base immediately, but plugins or external tools that write via `app.vault.modify()` can leave the metadata index stale until you run Settings → Files and Links → Rebuild Cache [[42]](https://forum.obsidian.md/t/metadata-edit-yaml-properties-update-the-content-of-the-note-but-not-the-index/110352).

## Bases vs Dataview

For users with an existing [Dataview](https://github.com/blacksmithgu/obsidian-dataview) ⭐ 9.0k (May 2026) library, the comparison is what actually drives the migration decision:

| Axis              | Bases                                       | Dataview                                       |
| ----------------- | ------------------------------------------- | ---------------------------------------------- |
| Status            | Core plugin, active dev [[a]][bs-a]         | Community, slow maint. (v0.5.70 Apr'25) [[b]][bs-b] |
| Query interface   | YAML + visual editor [[c]][bs-c]            | DQL (SQL-ish) + DataviewJS [[d]][bs-d]         |
| Cells editable    | ✓ writes back to frontmatter [[e]][bs-e]    | ✗ read-only [[d]][bs-d]                        |
| Reads inline data | ✗ frontmatter only [[f]][bs-f]              | ✓ inline `key::value` + tasks [[g]][bs-g]      |
| Performance       | Fast on large vaults [[c]][bs-c] ⚠ can stutter even on small ones [[t]][bs-t] | Noticeable lag, esp. mobile [[c]][bs-c] |
| Obsidian Publish  | ✗ planned [[h]][bs-h]                       | ✗ unsupported [[d]][bs-d]                      |
| GROUP BY          | ⚠ in development [[f]][bs-f]                | ✓ mature [[d]][bs-d]                           |
| Tasks query       | ✗ no inline tasks [[g]][bs-g]               | ✓ TASK queries [[d]][bs-d]                     |
| View types        | Table, Cards, List, Map [[i]][bs-i]         | Table, List, Task                              |

[bs-a]: https://obsidian.md/blog/2025-obsidian-october/
[bs-b]: https://github.com/blacksmithgu/obsidian-dataview
[bs-c]: https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/
[bs-d]: https://dandylyons.net/posts/goodbye-dataview-hello-obsidian-bases/
[bs-e]: https://obsidian.md/help/bases
[bs-f]: https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/#limitations
[bs-g]: https://forum.obsidian.md/t/dataview-vs-bases/113073
[bs-h]: https://obsidian.md/roadmap/
[bs-i]: https://obsidian.md/help/bases/views
[bs-t]: https://forum.obsidian.md/t/bases-is-super-slow-and-stuttery-laggy/108428

Hacker News consensus: Bases is "like 90% replacement [for Dataview] and faster", and Dataview's maintainer-blessed successor Datacore is stalled [[26]](https://news.ycombinator.com/item?id=44945532). Practical Medium: Dataview is "resting peacefully in a long-term academic sabbatical" [[28]](https://medium.com/@lennart.dde/obsidian-dataview-is-dead-long-live-bases-9750e8a92877).

**Migration path.** [Bases-Toolbox](https://github.com/Quorafind/Bases-Toolbox) ⭐ 52 (May 2026) converts Dataview `TABLE` queries (fields, aliases, FROM, WHERE, SORT, LIMIT, GROUP BY) into `.base` files — DataviewJS is explicitly unsupported [[25]](https://github.com/Quorafind/Bases-Toolbox). Practical PKM's guide adds that inline `key::value` data must first be lifted into frontmatter using the Dataview-to-Properties plugin before Bases can see it [[24]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/#limitations). **Pragmatic rule:** rebuild new dashboards in Bases, keep Dataview alive for grouped or task-heavy queries you'd otherwise have to restructure your vault to migrate.

## Known limitations and gotchas

The forum and report-card consensus as of mid-2026 — community score 4.4/5, but "still a bit of a work in progress" with a steep learning curve and weak documentation [[38]](https://practicalpkm.com/2026-obsidian-report-card/):

| Issue                                                             | Severity   | Workaround                                                |
| ----------------------------------------------------------------- | ---------- | --------------------------------------------------------- |
| No inline tasks / inline `key::value` [[j]][bs-j]                 | Structural | Restructure into per-task notes, or keep Dataview         |
| No GROUP BY yet [[k]][bs-k]                                       | Major      | Use per-view filters as a poor substitute                 |
| `date()` fails on ISO8601 + offset / `file.ctime` [[l]][bs-l]     | Bug        | Strip seconds + offset; avoid `file.ctime` formulas       |
| Horizontal scroll broken on wide tables [[m]][bs-m]               | UI         | Hide unused columns; await fix                            |
| Array-property equality filters stale [[n]][bs-n]                 | Bug        | Use `.contains()` instead of `==`                         |
| Stutter even on small vaults (~50 notes) [[o]][bs-o]              | Perf       | Disable hardware acceleration                             |
| iOS shows empty rows despite synced data [[p]][bs-p]              | Mobile     | None — open desktop                                       |
| iPad: create/duplicate view doesn't focus [[q]][bs-q]             | Mobile     | Toggle keyboard to nudge focus                            |
| Embedded base has no height limit / scroll [[r]][bs-r]            | UI         | Use `limit:` in view; await native fix                    |
| `this` rebinds inside embedded code-fence base [[s]][bs-s]        | Bug        | Use standalone `.base` + `![[file.base]]` transclusion    |
| Publish support not shipped [[h]][bs-h]                           | Roadmap    | Render externally (HTML export) or wait                   |

[bs-j]: https://forum.obsidian.md/t/bases-support-for-tasks/103074
[bs-k]: https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/#limitations
[bs-l]: https://forum.obsidian.md/t/base-formulas-date-doesnt-work-with-timestamps-that-dont-follow-a-specific-format/107329
[bs-m]: https://forum.obsidian.md/t/bases-horizontal-scrolling-doesnt-work/104298
[bs-n]: https://forum.obsidian.md/t/bug-filters-in-bases/104399
[bs-o]: https://forum.obsidian.md/t/bases-is-super-slow-and-stuttery-laggy/108428
[bs-p]: https://forum.obsidian.md/t/obsidian-base-not-show-in-iphone-ios/113673
[bs-q]: https://forum.obsidian.md/t/bases-mobile-creating-duplicating-a-view-from-the-gui-doesnt-automatically-set-the-focus-on-the-new-view/104634
[bs-r]: https://forum.obsidian.md/t/bases-limit-display-height-add-vertical-scroll-bar-when-a-base-is-embedded/106819
[bs-s]: https://blog.optional.page/misc/bases/

## Roadmap signal

The [official roadmap](https://obsidian.md/roadmap/) currently lists Kanban view as "in progress", and Calendar view + Publish support as "planned" — all three are the most-requested missing pieces from the limitations list above [[37]](https://obsidian.md/roadmap/). 1.10's Bases plugin API already lets community plugins ship custom view layouts (Maps was the proof-of-concept), so expect Gantt / timeline / chart views from the community before Obsidian ships them natively [[2]](https://obsidian.md/blog/2025-obsidian-october/).

## For an intermediate user, what to do this week

1. Pick *one* messy folder of reference notes you query mentally ("books I want to read", "side projects").
2. Add 2-4 consistent properties to those notes. Use Properties view to mass-edit.
3. Create one base on that folder with a Table view. Spend zero time on formulas.
4. Add a second named view: filtered subset (status / rating / tag).
5. Only after both views feel useful, add one formula column (start with `file.mtime.relative()` or an Overdue badge).
6. Bookmark or pin the base in your sidebar — it replaces the homepage MOC you were maintaining by hand.

The trap to avoid: building a Base before the underlying notes have consistent frontmatter. The view is downstream of the data, and the data is the work [[24]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/#limitations).
