---
title: "Linking & note structure in Obsidian: backlinks, MOCs vs folders"
date: 2026-05-30
depth: standard
format: md
topic: "Linking & note structure: backlinks, MOCs vs folders"
topic_raw: "Linking & note structure: backlinks, MOCs vs folders"
issue: 109
tags: [obsidian, pkm, note-taking, moc, linking]
summary: "Adoption-ordered path from folder-thinking to link-thinking: one wikilink per note, then three MOCs for orphans, then ACE/PARA only if you need it."
citations: 17
reading_time_min: 6
cover: cover.svg
cost_usd: 2.18
duration_sec: 393
model: "Opus 4.7"
---

> **TL;DR / Decision.** Use **shallow folders** for true containers (Daily, Templates, Attachments), **wikilinks on every new note** as the default organising act, and **3–5 MOCs** as your navigation layer once you cross ~50–100 notes. Treat folders as "where it lives," links as "what it relates to," tags as "what state it's in." If you're forcing a perfect folder tree, you're spending energy that should be going into links. [[1]](https://obsidian.rocks/how-i-use-folders-in-obsidian/) [[2]](https://stephango.com/vault) [[3]](https://blog.shuvangkardas.com/obsidian-note-organization/)

## The five primitives, and what each one is for

These five mechanisms do different jobs. Mixing them up is the #1 source of vault paralysis for beginners.

| Primitive          | Question it answers          | Strength                                    | Cost                                          |
|--------------------|------------------------------|---------------------------------------------|-----------------------------------------------|
| **Folder**         | "Where does this live?"      | True containers, file-system clarity        | A note can only be in one — forces a choice  |
| **Wikilink** `[[ ]]`| "What does this relate to?" | No exclusive ownership, builds graph        | Requires discipline to add at write-time     |
| **Backlink**       | "Who pointed at me?"          | Free — Obsidian generates it from `[[ ]]`  | Only as good as your outgoing-link habit     |
| **Unlinked mention**| "Who said my name without linking?" | Surfaces hidden connections retroactively | Noisy if titles are too generic         |
| **MOC** (Map of Content) | "What's the index for this topic?" | Note can live in many MOCs, supports context/ordering | Manual to maintain |
| **Tag** `#status`  | "What state is this in?"     | Live queries via search / Bases / Dataview  | Bad at "aboutness" — degrades to clutter     |

Sources: folders vs links framing [[1]](https://obsidian.rocks/how-i-use-folders-in-obsidian/) [[3]](https://blog.shuvangkardas.com/obsidian-note-organization/); backlinks & unlinked mentions are official core features [[4]](https://obsidian.md/help/plugins/backlinks); MOC vs tag distinction [[5]](https://medium.com/@o.anh/obsidian-between-mocs-and-tags-8fdf7086716c) [[6]](https://forum.obsidian.md/t/whats-the-advantage-of-using-moc-vs-just-tagging/34721).

## Why "MOC vs folder" is the wrong fight

The folder vs MOC debate is really about *exclusivity*. A note about "AI in healthcare" belongs in `Health/`, `AI/`, and `Work-Projects/` simultaneously — but the file system only lets you pick one. MOCs solve this by being **notes that link to notes**, so the same source note can be referenced from `MOC-Health`, `MOC-AI`, and `MOC-Project-Acme` with no duplication [[3]](https://blog.shuvangkardas.com/obsidian-note-organization/) [[7]](https://www.dsebastien.net/2022-05-15-maps-of-content/).

Tim Miller (Obsidian Rocks) puts the limit bluntly: *"A file either is in a folder, or it isn't. You can't have a file that exists in two folders at the same time… As your project grows and changes, folders have a hard time keeping up."* [[1]](https://obsidian.rocks/how-i-use-folders-in-obsidian/)

But "no folders ever" is also wrong. Even Nick Milo — whose **LYT** (Linking Your Thinking) framework popularised MOCs — now ships the **ACE** scaffold: three top-level folders (**Atlas**, **Calendar**, **Efforts**) covering knowledge, time, and projects. Relatedness still lives in links between notes [[8]](https://forum.obsidian.md/t/the-ultimate-folder-system-a-quixotic-journey-to-ace/63483). One LYT user describes the journey: *"Learning first to get rid of a rigid folder-based system was scary but useful. And later, bringing back some folders finding a balance between the structure and flexibility was a big deal."* [[9]](https://www.linkingyourthinking.com/)

Steph Ango — Obsidian's CEO — runs ~4 folders: root (personal writing), References, Clippings, plus admin folders (Attachments, Daily, Templates). His stated rule: *"I avoid folders because many of my entries belong to more than one area of thought."* He organises with note properties and links, navigating via Quick Switcher and backlinks, not the file tree [[2]](https://stephango.com/vault).

## Adoption-ordered roadmap (beginner → confident intermediate)

The single biggest mistake is trying to design the perfect structure before you have notes in it. The community-validated order is *capture → link → emerge*, not *design → capture*.

### Phase 1 — Capture (0–30 notes): one rule

**Add at least one `[[wikilink]]` to every note before you close it.** [[10]](https://www.makeuseof.com/orphan-notes-in-obsidian-linking-system/) This single discipline prevents the orphan-note problem that breaks most vaults at the 100-note mark. If you don't know what to link to, link to a non-existent note — Obsidian shows it in muted colour and turns it into a future seed [[11]](https://obsidian.md/help/link-notes).

Don't build folders yet. Don't build MOCs yet. Don't perfect tags.

### Phase 2 — Notice the friction (30–100 notes)

Around 50–100 notes you'll hit what one practitioner calls the *"mental squeeze point — the point at which the level of disorganization became crippling."* [[10]](https://www.makeuseof.com/orphan-notes-in-obsidian-linking-system/) That feeling is the signal — not earlier — to add structure. Aidan Helfant's framing: *"think and link first"* and organise later, *"once the need becomes obvious."* [[12]](https://www.aidanhelfant.com/5-simple-levels-to-supercharging-your-learning-with-mocs-in-obsidian/)

### Phase 3 — Three MOCs (100+ notes)

Create exactly **three MOCs** covering your broadest active topics — not perfect, just three. Link every orphan you can find (use Graph View, `Ctrl/Cmd+G`, to spot them) into one of them [[10]](https://www.makeuseof.com/orphan-notes-in-obsidian-linking-system/).

A MOC is just a note containing links to other notes — *"folders on steroids,"* in dsebastien's phrasing [[7]](https://www.dsebastien.net/2022-05-15-maps-of-content/). Helfant's "Dump → Lump → Jump" process:

1. **Dump** — paste every related note link into the MOC, no order
2. **Lump** — group under headings as themes emerge
3. **Jump** — leave it for a few days, return with fresh perspective [[12]](https://www.aidanhelfant.com/5-simple-levels-to-supercharging-your-learning-with-mocs-in-obsidian/)

### Phase 4 — Backlinks become your navigation

Open the **Backlinks pane** (right sidebar). Linked Mentions shows every note that wikilinked you. **Unlinked Mentions** shows notes that mention your title in plain text but never linked — these are free connection candidates [[4]](https://obsidian.md/help/plugins/backlinks) [[13]](https://learningaloud.com/blog/2024/02/25/a-use-for-obsidian-unlinked-mentions/). The pragmatic move: name notes using terms you naturally write in prose (e.g. project codenames, recurring concepts) so unlinked mentions surface hits without effort [[13]](https://learningaloud.com/blog/2024/02/25/a-use-for-obsidian-unlinked-mentions/).

At this point you stop opening the file explorer. Navigation = Quick Switcher (`Ctrl/Cmd+O`) + backlinks + clicking through MOCs [[1]](https://obsidian.rocks/how-i-use-folders-in-obsidian/) [[2]](https://stephango.com/vault).

### Phase 5 — Add a scaffold only if you need one

Once you have several MOCs, decide if you want a top-level container system. The two mainstream choices:

| Scaffold | Folders | Best for                                | Watch out for                          |
|----------|---------|-----------------------------------------|----------------------------------------|
| **ACE** (Nick Milo) | Atlas, Calendar, Efforts | PKM-heavy users who already think in MOCs [[8]](https://forum.obsidian.md/t/the-ultimate-folder-system-a-quixotic-journey-to-ace/63483) | Requires you to internalise the STIR model |
| **PARA** (Tiago Forte) | Projects, Areas, Resources, Archives | Cross-tool productivity (Drive, Notion too) [[14]](https://aimaker.substack.com/p/para-method-tiago-forte-claude-code-obsidian-ai-productivity-os) | Fights Obsidian's graph nature — note can only live in one bucket [[15]](https://brandonkboswell.com/blog/Should-you-use-PARA-in-Obsidian) |
| **Minimal** (Steph Ango) | References, Clippings, Daily, Templates | Default for most users; lets links do the work [[2]](https://stephango.com/vault) | Requires link discipline |

Brandon Boswell's critique of PARA-in-Obsidian: *"forcing traditional folder structure is limiting the benefits of [the graph] system and creating unnecessary effort in maintenance by moving files from folder to folder."* [[15]](https://brandonkboswell.com/blog/Should-you-use-PARA-in-Obsidian) The empirical pattern from the community: **shallow** (≤ 3 levels), **few** (5–10 top-level), **functional** (not topical).

## Backlinks vs unlinked mentions: when each pays

| Feature              | Trigger                                    | Cost to maintain                  | Use it for                                       |
|----------------------|--------------------------------------------|-----------------------------------|--------------------------------------------------|
| **Linked mention**   | You wrote `[[X]]`                          | One bracket pair at write-time    | Explicit, claimed connection                     |
| **Unlinked mention** | The literal title appears anywhere as text | Zero — Obsidian indexes it        | Catching connections you didn't notice; retroactive linking [[13]](https://learningaloud.com/blog/2024/02/25/a-use-for-obsidian-unlinked-mentions/) |

Practical trick: when starting a project, create a stub note with the project's recurring proper noun as title (e.g. `Acme Migration`). Every future daily note that mentions "Acme Migration" in prose appears in the stub's Unlinked Mentions pane automatically — no link discipline required [[13]](https://learningaloud.com/blog/2024/02/25/a-use-for-obsidian-unlinked-mentions/).

## MOCs vs tags: complementary, not competing

A common beginner muddle. The clean split:

- **MOC** = a hand-curated, ordered, contextual *index page* you write commentary on. Frozen state until you update it. *"MoC lets you describe the document you are linking to, and also order and format the documents in a manner appropriate to the work at hand."* [[6]](https://forum.obsidian.md/t/whats-the-advantage-of-using-moc-vs-just-tagging/34721)
- **Tag** = a *signal* used by search/Bases/Dataview for live queries. Best for status (`#draft`, `#needs-link`), type (`#person`, `#book`), or filter dimensions. *"Tags are signals, not structure."* [[3]](https://blog.shuvangkardas.com/obsidian-note-organization/)

User Orand's pragmatic ladder: *"start with tags and only add a MOC once a particular tag area becomes large enough to warrant the extra effort."* [[6]](https://forum.obsidian.md/t/whats-the-advantage-of-using-moc-vs-just-tagging/34721)

## Common traps, and what to do instead

| Trap                                                                 | Fix                                                                                  |
|----------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| Designing the folder tree before writing notes                       | Capture first. Folders, if any, emerge from real friction [[12]](https://www.aidanhelfant.com/5-simple-levels-to-supercharging-your-learning-with-mocs-in-obsidian/) |
| Nesting folders 4+ levels deep                                       | Cap at 2–3 levels; let MOCs handle the rest [[3]](https://blog.shuvangkardas.com/obsidian-note-organization/) |
| 200 unused topic tags from week 1                                    | Delete them. Tags = status/type, not topic [[3]](https://blog.shuvangkardas.com/obsidian-note-organization/) |
| Building MOCs before you have ≥10 notes on the topic                 | Premature — you're guessing the shape. Wait for the squeeze [[12]](https://www.aidanhelfant.com/5-simple-levels-to-supercharging-your-learning-with-mocs-in-obsidian/) |
| Optimising for a pretty graph view                                   | ⚠ "Creating for the graph" leads to forced links between unrelated ideas. The graph is a side-effect, not the goal [[16]](https://www.xda-developers.com/used-obsidian-wrong-for-year-folder-setup-that-finally-clicks/) |
| Circular backlinks created just to look connected                    | Avoid Note A↔Note B loops with no semantic relationship [[17]](https://www.digestafrica.com/vintage-brief/mastering-backlinks-in-obsidian-a-comprehensive-guide-1767647451) |
| Hundreds of orphan notes from rapid capture                          | Use `#needs-link` weekly batch, prune via Graph View [[10]](https://www.makeuseof.com/orphan-notes-in-obsidian-linking-system/) |

## Concrete next moves

1. **Today**: Enable the rule — every new note gets `[[at least one link]]` before close. Add `#needs-link` for emergencies.
2. **This week**: Open Backlinks pane and read its Unlinked Mentions section for your three most-active notes. Promote any worth keeping.
3. **At ~100 notes**: Create exactly three MOCs (`MOC-<broad topic>`) and Dump→Lump→Jump every orphan into one.
4. **Only when you have ≥5 MOCs**: Decide on a scaffold (ACE / minimal / PARA). Until then, don't.
5. **Never**: Re-org folders to chase a perfect tree. Refactor links instead.
