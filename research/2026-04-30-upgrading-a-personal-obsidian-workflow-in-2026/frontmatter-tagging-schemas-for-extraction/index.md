---
title: "Frontmatter and tagging schemas for extraction in Obsidian (2026)"
date: 2026-04-30
depth: deep
format: md
topic: "Frontmatter & tagging schemas for extraction"
topic_raw: "Frontmatter & tagging schemas for extraction"
issue: 49
tags: [obsidian, frontmatter, yaml, pkm, metadata, extraction, schemas, tagging]
summary: "How to design Obsidian YAML frontmatter and tag taxonomies in 2026 so external tools can reliably extract, query, and validate the metadata."
citations: 69
reading_time_min: 11
cover: cover.svg
cost_usd: 7.88
duration_sec: 920
---

> **TL;DR.** Design for **extraction first, presentation second**. Put canonical data in YAML frontmatter (Bases ignores inline `key:: value` Dataview fields [[5]]); use a `type:` discriminator [[5]] plus reusable property names (`created`, `author`, `topic`) [[13]]; keep YAML keys flat (Properties does not support nested objects [[8]]); reserve hashtags for note-state signals (`#status/active`, `#seedling`) and namespace them so Bases/Dataview can `FROM` the parent prefix [[20]] [[17]]; validate with a code-first schema (Zod for JS, Pydantic/Yamale for Python) [[35]] [[42]] [[38]]; for Markdown pipelines use **gray-matter** in JS (⭐ 4.4k) or **python-frontmatter** in Python (⭐ 412), and add **obsidiantools** (⭐ 553) when you need wikilink/tag awareness [[25]] [[24]] [[28]]. New schemas in 2026 should target Bases, not Dataview — Dataview has stagnated [[9]].

## Why the schema question matters now

Obsidian's typed-metadata story crystallised between July 2023 and October 2025. Version 1.4 (Jul 2023) introduced the Properties UI and a typed-key contract for YAML frontmatter [[1]]. Version 1.9.0 (May 2025) shipped Bases as a core plugin and finally removed the deprecated singular forms `tag`/`alias`/`cssclass`, forcing the plural list-typed `tags`/`aliases`/`cssclasses` [[2]] [[11]]. Version 1.10.0 (Oct 2025) extended Bases with card, list, and Maps views plus a public layout API for community-built views [[3]] [[10]]. Net effect: the vault now has a typed metadata layer that is queryable by Bases — but only if your YAML actually conforms.

Bases reads YAML only. Inline Dataview-style fields (`Rating:: 5` in the body) are invisible to it [[5]]. That is the single most important fact for anyone designing a 2026 schema: if you want notes to show up in a board, board filter, or Map view, the data must live in frontmatter — not in the body and not in inline fields.

## 1. Obsidian's native type system

Properties supports six built-in types plus three reserved defaults [[4]]:

| Property type | Example YAML | Notes |
|---|---|---|
| Text | `status: active` | Default; used for free-form strings and de-facto enums |
| List | `tags: [reading, ml]` | Multi-value; renders as chips |
| Number | `rating: 8` | Integers and floats; supports comparisons in Bases |
| Checkbox | `done: true` | Boolean |
| Date | `due: 2026-05-01` | ISO date; exposes `.year`, `.month`, `.day` to Dataview [[40]] |
| Date & Time | `published: 2026-04-30T09:00` | ISO datetime |
| `tags` (reserved) | `tags: [obsidian, pkm]` | List-only since 1.9 [[2]] |
| `aliases` (reserved) | `aliases: [PKM, Notes]` | List-only since 1.9 |
| `cssclasses` (reserved) | `cssclasses: [card]` | List-only since 1.9 |

Once a key is typed in any note, that type is **vault-wide** [[4]]. Renaming or retyping a key after the fact is a known pain point — see §6.

**Bases** (introduced in 1.9, stabilised in 1.10) extends this with first-class Date/DateTime arithmetic, Lists, Objects, and a Link/File type accessible through helpers like `link("Page")`, `today()`, `file.ctime`, `file.mtime`, `file.tags`, `file.size` [[41]]. Filters in Bases are graphical: a tuple of (Property, Operator, Value), composable with `and`/`or`/`not` [[6]]. Views render rows as tables, cards, lists, or maps [[10]].

Dataview infers eight types from the same YAML: Text, Number, Boolean, Date, Duration, Link, List, Object [[40]]. Wikilinks must be quoted in YAML to remain valid (`related: "[[Page Name]]"`) — bare `[[...]]` parses as a nested YAML list [[40]].

**The 2026 split:** Dataview has not received significant updates in over a year and is no longer actively developed; Bases is shipping changes regularly [[9]] and has a public roadmap covering new view types and formula expansion [[12]]. New schemas should target Bases-first; Dataview can ride on the same frontmatter for ad-hoc queries [[7]].

## 2. Schema design patterns that survive

Three patterns dominate practitioner-tested 2026 vaults.

### 2a. The `type` discriminator

A single mandatory property — almost always called `type` or `categories` — labels each note's "kind" (book, person, project, recipe, talk). Each Base then filters on this property and shows only the relevant rows [[5]]. Steph Ango's public vault is the canonical reference: he avoids folders entirely, uses a `categories` property, and maintains 50+ category-specific templates (`Book`, `Game Studio`, `Restaurant`, `Job Interview`) that share reusable property names — `created`, `author`, `genre`, `topic` — so values stay queryable across categories [[13]] [[23]].

### 2b. Flat keys, namespaced names

Properties does not support nested YAML [[8]]. Instead of:

```yaml
series:
  name: Foundation
  num: 1
```

power users write:

```yaml
series_name: Foundation
series_num: 1
```

Namespacing context-specific keys (`book_status` vs `video_status`) keeps autocomplete clean and avoids accidental type collisions across note types [[8]] [[13]]. Use snake_case rather than spaces or kebab-case — YAML parses kebab fine, but Dataview and Bases formulas treat the key as an identifier and dotted access (`row.book_status`) is more ergonomic.

### 2c. Tags as state signals, MOCs/links for topic

The most consistent advice from large-vault practitioners is to **reserve hashtags for state**, not topic [[17]]:

```
#inbox  #seedling  #evergreen          ← lifecycle
#status/active  #status/done            ← project state
#priority/p1                            ← triage
```

Topic structure goes in MOCs and links; navigation goes in folders (kept shallow, max two levels) [[16]]. Tags carry signal that is *cross-cutting* and *transient*; topic is structural and goes in stable links/properties.

Hierarchical/namespaced tags (`#project/active`, `#type/article`) are the de-facto extraction-friendly convention because Dataview can `FROM #project` and pull every child, and Bases can filter `tags contains "project/"` [[20]]. Library-of-Congress-style controlled vocabulary is the formal version of this idea, advocated by long-form forum reflections [[64]].

### 2d. Taxonomy comparison

| Approach | Strength | Weakness | Extraction friendliness |
|---|---|---|---|
| **Folder-only PARA** | Familiar; matches productivity literature | Projects/Resources collapse into each other [[19]] | ✗ folder is a string, not a queryable axis |
| **Johnny.Decimal** | Stable addresses; eliminates "where does this go" decisions; veterans pair with hierarchical tags for cross-cutting themes [[14]] | Hard ceiling at 100 IDs (10×10) [[15]] | ✓ numeric prefix is parseable, but rigid |
| **MOC (LYT)** | Spawn an MOC at 5+ notes on a topic [[18]]; folders shallow, links carry topic | Discoverability depends on link discipline | ⚠ MOC membership is implicit unless mirrored in a property |
| **Hierarchical state tags** | Cross-cutting; queryable parent/child [[20]] | Requires casing/separator hygiene [[21]] | ✓ `FROM #project` pulls all children |
| **`type` discriminator + flat YAML** (kepano) | Templates per type; one Base per type [[13]] [[23]] | Up-front template work | ✓ best for Bases; the de-facto 2026 default |

Empirically, vaults with hundreds of tags (one user reported ~400) report no slowdown — bloat is a cognitive cost, not a performance ceiling [[22]].

## 3. Schema validation: how to constrain frontmatter for extraction

Validation gives you typed extraction. Three lanes are mature in 2026.

### 3a. JS / TypeScript: Zod via Astro and Eleventy

Astro content collections are the canonical reference [[35]]:

```ts
import { defineCollection, reference, z } from 'astro:content';

const notes = defineCollection({
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    tags: z.array(z.string()),
    status: z.enum(['active', 'archived', 'done']),
    author: reference('authors'),
  }),
});
```

`z.coerce.date()` converts ISO strings to JS `Date`. `reference()` cross-validates wikilinks against another collection. Eleventy v3 exposes the same hook via `eleventyDataSchema`, and short-circuits the data cascade on a Zod failure [[36]]. **astro-editor** (⭐ 445) reads the same Zod schema and renders typed frontmatter forms — the schema doubles as both validator and authoring UI [[43]].

### 3b. Python: Pydantic and Yamale

`pydantic_yaml` parses YAML directly into BaseModels with `str`-Enum subclasses for status fields, nested models, and round-tripping via `parse_yaml_raw_as()` and `to_yaml_str()` [[42]]:

```python
from enum import Enum
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_raw_as

class Status(str, Enum):
    active = "active"
    archived = "archived"
    done = "done"

class Note(BaseModel):
    title: str
    status: Status = Status.active
    tags: list[str] = []
```

For lighter-weight validation without a Python class, **Yamale** (⭐ 764) ships with `str()`, `int(min, max)`, `num()`, `bool()`, `day()` (YYYY-MM-DD), `timestamp()`, `list()`, `enum()`, `regex()`, and `include()` for reusable schemas [[38]].

### 3c. JSON Schema in the Markdown pipeline

**remark-lint-frontmatter-schema** (⭐ 73) validates YAML against a JSON Schema in a remark pipeline, supports per-file `$schema` keys, IDE underlining, and auto-fix [[37]]. **mdschema** (⭐ 62) is a lighter declarative alternative — write a small YAML file describing each field [[39]]:

```yaml
- { name: "title",  type: string }
- { name: "date",   type: date,   format: date }
- { name: "author", optional: true, format: email }
- { name: "tags",   optional: true, type: array }
```

`markdownlint-cli2` accepts a `frontMatter` regex option that *skips* the YAML block during markdown linting, so it stacks with — rather than replaces — schema validators [[44]].

### 3d. Type recipes

| Field | YAML | Notes |
|---|---|---|
| ISO date | `due: 2026-05-01` | Dataview/Bases auto-detect [[40]] [[41]] |
| Datetime | `published: 2026-04-30T09:00:00` | Bases: `today()`, `now()`, `date(...)` helpers [[41]] |
| Wikilink | `related: "[[Page Name]]"` | Quote required to keep YAML valid [[40]] |
| URL | `source: https://example.com` | Plain string |
| Enum status | `status: active` | Text type; Zod `z.enum([...])`, Pydantic `str-Enum`, Yamale `enum()` |
| Tag list | `tags: [pkm, ml]` | List type; reserved key, plural form mandatory since 1.9 [[2]] |
| Number | `rating: 8` | Number type; comparisons in Bases [[6]] |
| Boolean | `done: false` | Checkbox type |

## 4. Programmatic extraction tools

Pick by language and how much Obsidian-awareness you need.

### 4a. Generic frontmatter parsers

| Tool | Lang | ⭐ Stars | Notes |
|---|---|---|---|
| [gray-matter](https://github.com/jonschlinkert/gray-matter) | JS | ⭐ 4.4k | De-facto JS parser; YAML/JSON/TOML/Coffee + custom engines; used by Astro, Gatsby, VitePress, TinaCMS, Netlify [[25]]. ⚠ recent issues: js-yaml prototype-pollution via bundled dep (#178, Nov 2025), ESM/Vite SSR `is not a function` regression (#181, Feb 2026), invalid-frontmatter mis-cached (#166, #174) [[26]] |
| [python-frontmatter](https://github.com/eyeseast/python-frontmatter) | Python | ⭐ 412 | Pluggable handlers (YAML/JSON/TOML); v1.1.0 (Jan 2024); BOM gotcha — open files with `utf-8-sig` [[24]] |
| [remark-frontmatter](https://github.com/remarkjs/remark-frontmatter) | JS | ⭐ 320 | v5.0.0; ⚠ only recognises the **fence** — does NOT parse the YAML body. Compose with `vfile-matter` or `remark-mdx-frontmatter` to get usable metadata [[27]] |
| [gray_matter (Rust)](https://crates.io/crates/gray_matter) | Rust | – | Port of jonschlinkert's; YAML/JSON/TOML + custom engines [[33]] |
| [fronma](https://github.com/r7kamura/fronma) | Rust | ⭐ 8 | Typed; YAML default, TOML/JSON behind cargo features for build-size control [[34]] |

### 4b. Obsidian-aware extractors

| Tool | Lang | ⭐ Stars | Notes |
|---|---|---|---|
| [obsidiantools](https://github.com/mfarragher/obsidiantools) | Python | ⭐ 553 | v0.11.0 (Jul 2025); wraps python-frontmatter; exposes `vault.get_front_matter`, `vault.get_tags`, NetworkX graph; tag extractor strips code blocks, escaped `\#`, wikilink `[[note#header]]` headers [[28]] [[29]]; returns top tag of nested chains by default; falls back to empty dict on invalid YAML |
| [obsidian-export](https://github.com/zoni/obsidian-export) | Rust | ⭐ 1.3k | v25.3.0 (Mar 2025); CLI/library; `--frontmatter=always\|never`, `--skip-tags`/`--only-tags`; ⚠ errors on mutual `[[A]]<->[[B]]` embeds unless `--no-recursive-embeds` [[30]] |
| [py-obsidianmd / pyomd](https://github.com/selimrbd/py-obsidianmd) | Python | ⭐ 312 | The only library that round-trips between YAML and Dataview inline `key:: value` fields; ⚠ no tagged release; explicit "back up your vault" warning [[31]] |

**The inline-fields trap.** Dataview defines two metadata channels — YAML frontmatter and inline `key:: value` (or `[key:: value]`) [[32]]. A frontmatter-only extractor will silently miss the inline class. If your vault uses Dataview inline fields, you need either obsidiantools / pyomd or a one-time migration pass that hoists everything into YAML.

### 4c. Pipeline gotchas

- **BOM.** python-frontmatter recommends `utf-8-sig` for files written by Windows tools [[24]].
- **Cached invalid frontmatter.** gray-matter's open issues show files with broken YAML being silently cached as parsed [[26]] — fail loudly in your pipeline.
- **remark-frontmatter doesn't parse.** Forgetting `vfile-matter` is a common Astro/MDX pipeline bug [[27]].
- **Tag dual location.** Tags can live in `tags:` YAML *and* inline `#hashtag`. Bases sees only the YAML form [[5]]; obsidiantools' tag extractor merges both [[28]].

## 5. AI-assisted tagging and frontmatter (2025-2026)

Three patterns are converging.

### 5a. In-vault plugins that write YAML directly

| Plugin | ⭐ Stars | Pattern |
|---|---|---|
| [AI Tagger Universe](https://github.com/niehu2018/obsidian-ai-tagger-universe) | ⭐ 84 | 15+ providers (Ollama, LM Studio, OpenAI, Claude, Gemini, Mistral); hybrid mode matches existing tags before suggesting new ones; configurable hierarchical depth (1-3 levels) and naming convention (kebab/snake-case) [[45]] |
| [Auto Tag](https://github.com/CtrlAltFocus/obsidian-plugin-auto-tag) | ⭐ 66 | OpenAI-only; analyses full note or selection; creates frontmatter when missing [[56]] |
| Metadata Auto Classifier | – | OpenAI; surfaces both tags and arbitrary frontmatter fields via on-demand commands [[55]] |
| [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections) | ⭐ 4.9k | Embeddings-first, not tag-generation; bulk metadata edits are Connect Pro only [[47]] |
| [Obsidian Copilot](https://github.com/logancyang/obsidian-copilot) | ⭐ 6.8k | Chat-with-vault; frontmatter is read-context only — issue [#1471](https://github.com/logancyang/obsidian-copilot/issues/1471) explicitly requests YAML-tag-aware indexing [[48]] [[49]] |
| [Frontmatter Generator](https://github.com/HananoshikaYomaru/Obsidian-Frontmatter-Generator) | ⭐ 46 | Non-LLM but structured: JSON / JS-expression templates auto-populate YAML on save; increasingly used as a deterministic validation layer beneath LLM output [[54]] |

### 5b. Retrieval-augmented taxonomy (the dominant 2026 pattern)

The trick is to constrain the LLM against an existing taxonomy, not let it invent fresh tags. A documented 2025 workflow uses Gemma 3 12B via LM Studio plus AI Tagger Universe pointed at a hand-curated `Tag List` note in the vault root, then chains Auto Note Mover to file by tag [[46]]. Standalone Python scripts replicate this — read the vault's tag set first, send to LLM as system context, then write back [[57]].

The widely-shared canonical example is Karan Sharma's Claude-API script (mrkaran.dev): walks notes, asks Claude to extract/infer `title`, `categories`, `tags`, `status`, `priority`, parses the JSON/YAML response, merges back while **preferring existing fields over generated ones** [[51]]. The author argues the LLM beats keyword tagging because it infers semantic context (a BTRFS-on-Arch note auto-tags `linux/filesystem/arch` even with no keyword match).

### 5c. MCP-mediated agents

[MarkusPfundstein/mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian) (⭐ 3.5k) exposes a `patch_content` tool that lets Claude insert text relative to a frontmatter field via the Obsidian Local REST API — targeted metadata edits rather than full-note rewrites [[53]]. **MCPVault** (rebranded `@bitbonsai/mcpvault` after Obsidian's March 2026 trademark request) provides AST-aware YAML preservation so unmodified fields keep original formatting, plus a `list_all_tags` tool that scans frontmatter and inline `#hashtags` with occurrence counts — a foundation for taxonomy-aware tagging via Claude [[52]]. **AI Knowledge Filler** (Feb 2026) ships a system prompt that turns Claude Projects, GPT custom instructions, or a CLI into a deterministic generator of vault-ready files with validated YAML, fixed heading hierarchy, WikiLinks, and domain classification across 30+ domains [[50]].

## 6. Failure modes and concrete remedies

Real-user reports converge on five recurring failures.

| Failure mode | Symptom | Remedy |
|---|---|---|
| **Tag explosion** | Tagging every noun (`#glue`, `#wood`, `#saw`) → noise > signal | Tag sparingly (3–5 high-level per note); lowercase + singular; lean on autocomplete [[58]] |
| **Granularity ambiguity** | Should this be `#dog`, `#dogs`, `#pets`, `#mammals`? | Controlled vocabulary (Library-of-Congress style) + autocomplete enforcement [[61]] [[64]] |
| **Frontmatter sprawl** | 200+ stale property fields from imports/plugins; no native bulk cleanup [[62]] | Multi-page feature request still open [[68]]; current workaround is ripgrep + `sd` or external Python script [[69]] |
| **Metadata rot from platform changes** | The 2023 Properties rollout broke existing tag-bearing frontmatter [[66]]; users report phantom tag bloat [[67]] | Pin Obsidian version before bulk migrations; keep frontmatter schema in version control |
| **Breaking renames** | Tag Wrangler renames are irreversible; can silently merge tags (losing provenance); partial-fail under sync [[63]] | Backup vault before every rename; pause sync; spot-check after |
| **Bloat-then-restart cycle** | Recurring "I deleted everything and started over" posts [[59]] | Drop influencer-driven elaborate frameworks; minimal daily journal + search outperforms them [[60]] |
| **Tag dual-location collisions** | Same concept tagged in YAML `tags:` and inline `#hashtag`; Bases sees only YAML [[5]], Dataview sees both [[32]], frontmatter-only extractors miss the inline class | Pick one channel per tag-purpose; if dual, run a one-time hoist from inline → YAML using pyomd or a script [[31]] |

A 2024 reflection from a long-time user crystallises the working separation: **frontmatter for objective minutiae** (URLs, dates, author, series) — **inline `#tags` for sentence/section-level markup** — **transition tags into stable typed fields once usage patterns stabilise** [[64]] [[65]]. That last move is exactly what Properties + Bases is designed for.

## 7. Putting it together: a 2026 reference schema

A working starting point for a personal vault, designed for extraction:

```yaml
---
type: book                           # discriminator (Bases filter axis)
title: "Foundation"
author: "Isaac Asimov"               # reusable across categories [[13]]
created: 2026-04-30                  # Date type
updated: 2026-04-30T09:00            # Date & Time type
status: active                       # Text type, Zod enum-validated
tags: [scifi, classic]               # List type, plural form mandatory [[2]]
related: ["[[Foundation and Empire]]"]  # quoted wikilink [[40]]
source: https://en.wikipedia.org/wiki/Foundation_(Asimov_novel)
rating: 9                            # Number
done: false                          # Checkbox
series_name: "Foundation"            # flat keys; no nesting [[8]]
series_num: 1
---
```

Inline state tags below the YAML, lifecycle/triage only [[17]] [[20]]:

```
#status/active #priority/p2
```

Pair it with:

- A Zod or Pydantic schema for the `type: book` shape (and one per other type) [[35]] [[42]].
- A Bases view filtered by `type = "book"` [[5]] [[6]].
- A taxonomy "Tag List" note that AI taggers must respect [[46]].
- python-frontmatter or gray-matter for downstream extraction [[24]] [[25]]; obsidiantools when you need wikilink/inline-tag awareness [[28]].
- Validation in CI via remark-lint-frontmatter-schema or Yamale [[37]] [[38]].
- Migrate ad-hoc tags into typed properties only once their usage pattern is stable [[65]].

The schema is the contract — Bases queries it, Dataview queries it, Zod/Pydantic validates it, AI taggers must respect it, and external scripts can extract it without surprises.
