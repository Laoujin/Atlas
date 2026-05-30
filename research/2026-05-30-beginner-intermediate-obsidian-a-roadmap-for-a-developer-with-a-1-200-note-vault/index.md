---
layout: expedition
title: "Beginner → intermediate Obsidian: a roadmap for a developer with a 1,200-note vault"
date: 2026-05-30
topic: "Build a practical, adoption-ordered roadmap for taking an Obsidian user from beginner to a confident intermediate level in 2026, written for an experienced software developer who is already fluent in Markdown, Git, and YAML but a beginner at Obsidian's own features, and who already maintains a large vault (~1,200 notes: a big reference collection of movies, series, books, places, and recipes, plus years of daily notes) with template and `.base` files that were set up but never actually used. Focus on the highest-leverage intermediate skills and habits worth learning next, and the order to adopt them. Stay vanilla and low-friction: explicitly skip hyper-advanced setups such as local-LLM embedding stacks, custom plugin development, and external publishing pipelines (Quartz/Obsidian Publish). For each recommended skill, give a concrete \"why it matters\" and a small first step that can be applied to the existing vault."
format: md
tags: [obsidian, pkm, roadmap, intermediate, bases]
summary: "Five chapters in adoption order — properties first to wake up the unused .base files, then a single linking rule, a five-line daily template, three MOCs, and the keyboard-first plugin pack — for a developer with a vault that already has the scaffolding but never used it."
cover: cover.svg
synthesis: true
children:
  - slug: linking-note-structure-backlinks-mocs-vs-folders
    title: "Linking & note structure: backlinks, MOCs vs folders"
    depth: standard
    status: success
    summary: "Adoption-ordered path from folder-thinking to link-thinking: one wikilink per note, then three MOCs for orphans, then ACE/PARA only if you need it."
    citations: 17
    reading_time_min: 6
  - slug: properties-tagging-for-queryable-notes
    title: "Properties & tagging for queryable notes"
    depth: standard
    status: success
    summary: "How to add structured metadata to Obsidian notes so Bases and Dataview can query them — when to reach for a property, when a tag, and the naming rules that keep both useful."
    citations: 14
    reading_time_min: 6
  - slug: bases-turn-existing-reference-notes-into-live-views
    title: "Bases: turn existing reference notes into live views"
    depth: deep
    status: success
    summary: "How to convert a folder or tag of reference notes into a live, editable, filterable view using Obsidian Bases — the .base format, the conversion workflow, ready-to-steal recipes, the formula language, and where Dataview still wins."
    citations: 42
    reading_time_min: 11
  - slug: low-friction-capture-daily-note-habits
    title: "Low-friction capture & daily-note habits"
    depth: standard
    status: success
    summary: "The smallest viable Obsidian capture loop — a five-line daily-note template, one hotkey, one mobile pathway, one weekly pass — and the order to adopt them in over four weeks."
    citations: 20
    reading_time_min: 9
  - slug: core-community-plugins-keyboard-driven-navigation
    title: "Core + community plugins & keyboard-driven navigation"
    depth: standard
    status: success
    summary: "Which core plugins to enable, the tight community-plugin starter pack, and the hotkey patterns that turn an Obsidian beginner into a keyboard-first intermediate."
    citations: 28
    reading_time_min: 6
cost_usd: 17.20
duration_sec: 2633
citations: 121
reading_time_min: 38
---

The expedition's five chapters cluster around one cross-cutting decision: **what to do first when the scaffolding already exists but has never been used.** All five recommend "habit before system," but their individual adoption orders differ — and for a 1,200-note vault with unused templates and `.base` files, that order needs reshuffling.

**Properties are the load-bearing prerequisite, not Bases.** Two chapters independently arrive at the same gating step: a `.base` file is empty until the notes it points at carry consistent YAML frontmatter [[1]](https://obsidian.md/help/bases). Bases ignores inline `key::value` Dataview metadata entirely [[2]](https://practicalpkm.com/moving-to-obsidian-bases-from-dataview/). For a vault with hundreds of reference notes and dormant `.base` files, the first move is therefore not "use the Base" but "stamp 3–4 properties (`type`, `status`, `rating`, `date`) onto one reference folder — books, films, recipes, or places — until its matching Base lights up" [[3]](https://practicalpkm.com/complete-guide-to-obsidian-properties/). The Bases chapter calls this the five-step conversion workflow; the Properties chapter calls it the four-properties-and-one-Base proof step. Same move, different vocabulary.

**Don't backfill — tag and link forward.** All five chapters converge on this. The linking chapter is explicit: re-organising folders to chase a perfect tree is Never [[4]](https://obsidian.rocks/how-i-use-folders-in-obsidian/). The properties chapter: "tag forward from the day you settle the taxonomy; old notes get tagged only when you re-open them" [[3]](https://practicalpkm.com/complete-guide-to-obsidian-properties/). The capture chapter: build the habit before the system [[5]](https://obsidian.rocks/obsidian-quick-capture/). For a 1,200-note vault, this is the single most important constraint — the temptation to retro-organise is exactly what burns the time that should go into new linking discipline.

**A real order for this specific user.** The chapters individually present linear paths; collapsed for an existing-vault, never-used-the-features developer it becomes:

1. Pick one reference folder, stamp four properties on its template, wake up the matching `.base` file [[3]](https://practicalpkm.com/complete-guide-to-obsidian-properties/).
2. Adopt the one-wikilink-before-close rule on *new* notes only [[6]](https://www.makeuseof.com/orphan-notes-in-obsidian-linking-system/).
3. Switch on the five-line daily-note template and a single capture hotkey — no Periodic Notes yet [[5]](https://obsidian.rocks/obsidian-quick-capture/).
4. Once new-note volume exposes orphans, create three MOCs over the existing reference collections, Dump → Lump → Jump [[7]](https://www.aidanhelfant.com/5-simple-levels-to-supercharging-your-learning-with-mocs-in-obsidian/).
5. Layer Quick Switcher++ and the keyboard hotkeys when the file explorer becomes the bottleneck.

**Tensions left unresolved.** The linking chapter pushes "tags are for status/type, not topic"; the properties chapter allows broad topic tags as one of three categories. Both are right at different scales: at 100 notes, restricting to status/type/topic with two tags max is wise; at 1,200 notes, topic tags are already in the wild and pruning them costs more than tolerating them. The expedition also doesn't go deep on mobile sync trade-offs (Obsidian Sync vs Obsidian Git vs Remotely Save vs Self-hosted LiveSync) — a known gap that matters once Step 3's capture hotkey extends to a phone.

The sharpest open question after all five chapters: **is the bottleneck the unused scaffold, or the daily-note habit?** If the templates and `.base` files already exist but no new notes flow in, no amount of property-stamping pays off. The Bases chapter has the proof-step; the capture chapter has the habit. Run them in parallel, not in series.
