---
title: "Properties & tagging for queryable notes"
date: 2026-05-30
depth: standard
format: md
topic: "Properties & tagging for queryable notes"
topic_raw: "Properties & tagging for queryable notes"
issue: 109
tags: [obsidian, pkm, metadata, properties, tags, bases, dataview]
summary: "How to add structured metadata to Obsidian notes so Bases and Dataview can query them — when to reach for a property, when a tag, and the naming rules that keep both useful."
citations: 14
reading_time_min: 6
cover: cover.svg
cost_usd: 2.43
duration_sec: 415
model: "Opus 4.7"
---

> **Decision.** Put structured, single-value metadata (status, date, rating, author) in **Properties**; use **tags** for the 1–3 broad topics of a note plus a small set of nested status flags. Query both with **Bases** by default (core plugin in early access since Obsidian 1.9.0 in May 2025 [[1]](https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/), generally available in 1.9.10 [[14]](https://www.xda-developers.com/obsidians-new-bases-feature-replacing-notion-workflow-for-good/)); only add **Dataview** [⭐ 9.0k](https://github.com/blacksmithgu/obsidian-dataview) [[2]](https://github.com/blacksmithgu/obsidian-dataview) when you hit a wall Bases can't clear — grouping and TASK/CALENDAR/LIST views [[11]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/).

## Why this chapter exists

A vault without metadata is a folder of orphaned files: you can read each note, but you can't ask the vault questions ("show me every book I rated 4+ I haven't finished", "every meeting note from Q1 tagged `#decision`"). Properties and tags are how you make the vault queryable; Bases and Dataview are how you query it. Getting the metadata layer right at the intermediate stage saves a painful re-tagging pass later [[4]](https://practicalpkm.com/complete-guide-to-obsidian-properties/).

## What each one actually is

**Properties** are key–value metadata stored in a YAML block at the top of the note, surrounded by `---`. The Properties editor renders them above the body without showing raw YAML [[5]](https://obsidian.md/help/properties). Obsidian supports six types: `text`, `number`, `list`, `checkbox`, `date`, `date & time` — pick the type that matches what you'll filter on (a date stored as text won't sort right) [[5]](https://obsidian.md/help/properties).

**Tags** are a special property (`tags:` as a YAML list) or an inline `#tag` token in the body. Rules: alphabetical letters, digits, `_`, `-`, or `/` for nesting; at least one non-numeric character; no spaces; case-insensitive [[6]](https://obsidian.md/help/tags). Nested tags hierarchically match — `tag:#inbox` returns `#inbox`, `#inbox/to-read`, and `#inbox/processing` [[6]](https://obsidian.md/help/tags).

Note the trap: the singular `tag`, `alias`, `cssclass` keys were deprecated in Obsidian 1.4 and dropped in 1.9 — always use the plural list forms (`tags:`, `aliases:`, `cssclasses:`) [[5]](https://obsidian.md/help/properties).

## When to use which

The community consensus is that tags and properties overlap heavily — "they're both just labels you attach to your notes" [[7]](https://forum.obsidian.md/t/tags-vs-properties/111469). The pragmatic split below is what works at intermediate scale, not what's technically possible.

| Use this              | For                                                                  | Why                                                                                                  |
| --------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Property (typed)**  | `status`, `rating`, `due`, `author`, `url`, `published`, `read`      | Strong types → reliable sort and filter in Bases [[5]](https://obsidian.md/help/properties)          |
| **Property (`tags`)** | Note-level classification: `type/book`, `area/work`, `status/active` | Lives in YAML → describes the *whole* note, clean in Properties view [[8]](https://desktopcommander.app/blog/2026/01/29/how-to-use-tags-in-obsidian-markdown/) |
| **Inline `#tag`**     | Section/quote-level markers: `#quote`, `#todo`, `#question`          | Position carries meaning — flags a paragraph, not the file [[8]](https://desktopcommander.app/blog/2026/01/29/how-to-use-tags-in-obsidian-markdown/) |
| **Folder**            | The *kind* of file (literature, journal, project)                    | "Use folders for the type of files contained within them" [[9]](https://forum.obsidian.md/t/an-opinionated-reflection-on-using-folders-links-tags-and-properties/78548) |
| **Link `[[]]`**       | Navigation and "where did I use this?" — *not* discovery             | Selective links keep the graph signal-to-noise high [[9]](https://forum.obsidian.md/t/an-opinionated-reflection-on-using-folders-links-tags-and-properties/78548) |

Rules of thumb:

- If you'd ever want to **sort or compute** on it → property with the right type [[4]](https://practicalpkm.com/complete-guide-to-obsidian-properties/).
- If it's a **broad topic** ("psychology", "homelab") with potential children → tag [[9]](https://forum.obsidian.md/t/an-opinionated-reflection-on-using-folders-links-tags-and-properties/78548).
- If a value is **one of a closed set** (active/done/archived) → property (Bases filters cleanly; tags work too but pollute the tag pane) [[4]](https://practicalpkm.com/complete-guide-to-obsidian-properties/).
- If you'd want to find the line in the file, not the file itself → inline tag [[8]](https://desktopcommander.app/blog/2026/01/29/how-to-use-tags-in-obsidian-markdown/).

## Naming conventions (do this once, save yourself later)

Practical PKM's three rules survive intact for both properties and tags [[4]](https://practicalpkm.com/complete-guide-to-obsidian-properties/) [[10]](https://practicalpkm.com/how-to-use-tags-effectively/):

1. **Singular** — `rating`, not `ratings`; `#book`, not `#books`. Plurals create duplicates.
2. **Lowercase, no spaces** — `kebab-case` or `snake_case`, pick one and stick to it. `#Journal` and `#journal` are different tags in some contexts and a confusing mess in all of them.
3. **Use autocomplete** — Obsidian suggests existing property/tag names as you type; accept the suggestion instead of retyping. Misspelling = a new property silently created.

Two more, less obvious:

- **Specificity beats generality.** Separate `newsletter_status` and `video_status` properties beat one shared `status` when the allowed values differ [[4]](https://practicalpkm.com/complete-guide-to-obsidian-properties/).
- **Put defaults in your templates.** "Add them to your template files. This basically makes sure that all of the best practices are followed at once" [[4]](https://practicalpkm.com/complete-guide-to-obsidian-properties/). A book-template that pre-seeds `type: book`, `status: unread`, `rating: ` is worth more than any after-the-fact cleanup pass.

## A starting taxonomy (3 categories, stop there)

Tags proliferate faster than you can wrangle them; "resist adding more categories until you've proven these three aren't enough" [[10]](https://practicalpkm.com/how-to-use-tags-effectively/):

- **Type** — what kind of note is this? `type/book`, `type/meeting`, `type/idea`. Often overlaps with a folder; pick one home.
- **Status** — current state. `status/active`, `status/archived`, `status/inbox`. Best as a property if the values are a closed set.
- **Topic** — subject. `psychology`, `homelab`, `pkm`. The most valuable category for serendipity; the most prone to bloat.

If a candidate tag doesn't fit any of these, ask: *"how will I search for this later?"* Tags exist for retrieval; if search, links, or folders already find the note, the tag is dead weight [[10]](https://practicalpkm.com/how-to-use-tags-effectively/).

## The query layer

You need a query engine for any of this to pay off. The 2026 landscape:

| Tool                                                                                | Stars                                                                            | Speed                                                                                              | Authoring                                                                                                                | When to pick                                                                                       |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| **[Bases](https://obsidian.md/help/bases)** (core, since 1.9)                       | n/a (core)                                                                       | Renders nearly instantly even in 50k-note vaults [[11]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/) | Visual editor, `.base` file or markdown code block [[12]](https://obsidian.md/help/bases)                                | Default. Tables, cards, filters, sort, formulas [[12]](https://obsidian.md/help/bases)             |
| **[Dataview](https://github.com/blacksmithgu/obsidian-dataview)**                   | [⭐ 9.0k](https://github.com/blacksmithgu/obsidian-dataview) [[2]](https://github.com/blacksmithgu/obsidian-dataview) | Slows large vaults, esp. mobile [[3]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/)                    | DQL or JS, text-only [[3]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/)                                | Add when Bases can't: grouping, TASK/CALENDAR/LIST views, inline `key::value` parsing [[11]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/) |
| **[Datacore](https://github.com/blacksmithgu/datacore)**                            | [⭐ 2.2k](https://github.com/blacksmithgu/datacore) [[3]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/) | Faster than Dataview [[3]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/)         | React components — "arcane and cryptic to the average user" [[3]](https://obsidian.rocks/dataview-vs-datacore-vs-obsidian-bases/) | Skip at intermediate level. Power-user territory.                                                  |

⚠ Bases only reads data stored in YAML properties — inline `key::value` Dataview metadata is invisible to it [[11]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/) [[12]](https://obsidian.md/help/bases). If you've been using Dataview's `key:: value` syntax in note bodies, migrate that into proper YAML before adopting Bases [[11]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/).

## Adoption order (the practical path)

1. **Add four properties to one template.** Pick a single note type (books, meetings, projects). Add `status`, `created`, `type`, plus one type-specific field. Use the Properties UI, not raw YAML.
2. **Write one Base.** "All my active books." Filter on `type == "book"` and `status == "reading"`. Choose Table view. This is the proof that the metadata earns its keep.
3. **Tag sparingly, by category.** Start with two tags max per note, drawn from your three-category list (type/status/topic). Don't tag every note — "every note that has a tag needs to mean something" [[10]](https://practicalpkm.com/how-to-use-tags-effectively/).
4. **Extend.** Add a second template. Add a second Base. Add a third property only when you have a concrete query that needs it.
5. **Audit once a month.** Open the Tag pane. Rename duplicates with [Tag Wrangler](https://github.com/pjeby/tag-wrangler) [⭐ 899](https://github.com/pjeby/tag-wrangler) [[13]](https://github.com/pjeby/tag-wrangler) — right-click → rename propagates the change across the vault.

## Pitfalls

- **Dates as text.** Storing `2026-05-30` in a `text` property breaks sort and date math in Bases formulas. Use the `date` type [[5]](https://obsidian.md/help/properties).
- **Property sprawl from typos.** `Status: done` and `status: done` are two properties. Always accept autocomplete [[4]](https://practicalpkm.com/complete-guide-to-obsidian-properties/).
- **Tag explosion.** "Tags seem to proliferate faster than they can be wrangled in" [[10]](https://practicalpkm.com/how-to-use-tags-effectively/). The cure is restraint at creation, not pruning after.
- **Inline `key:: value` Dataview metadata.** Bases can't see it. Convert to YAML now if you plan to use Bases [[11]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/).
- **Re-tagging the past.** Don't. Tag forward from the day you settle the taxonomy; old notes get tagged only when you re-open them for unrelated reasons.
