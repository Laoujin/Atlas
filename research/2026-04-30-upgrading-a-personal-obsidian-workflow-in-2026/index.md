---
layout: expedition
title: "Upgrading a personal Obsidian workflow in 2026"
date: 2026-04-30
topic: "Research deliverable for upgrading an existing personal Obsidian workflow in 2026, covering capture, structured metadata, knowledge-base patterns, media logging, AI-assisted entry, and selective publishing — assume an expert programmer and AI-proficient user (skip 101 framing). Surface concrete plugins, patterns, and integrations that are production-ready in 2026, prefer OSS, with EUR pricing flagged where commercial. Address: (a) low-friction daily-note capture for life logging (shows, concerts, restaurants, visited friends, travel) including LLM/Claude-driven retro-fill from calendar and other passive sources, plus mobile/voice paths; (b) tagging conventions and YAML frontmatter schemas designed for later querying/extraction (Dataview, Bases, Datacore, etc.); (c) workflows to publish specific notes to GitHub Pages or equivalents (Obsidian Publish vs OSS alternatives like Quartz, Digital Garden, MkDocs pipelines); (d) improved patterns for the user's existing technical knowledge base (book reviews, architecture, AI, design) — note structure, linking, MOCs vs folders; (e) automated media tracking for books/movies/series with metadata fetch and watch/read-state lifecycle; and (f) AI plugins for in-vault retrieval, summarization, and querying. Decision-ready guidance with concrete plugin/tool names, not abstract advice."
format: md
tags: [obsidian, pkm, bases, ai-tooling, publishing]
summary: "Six-angle expedition on upgrading a personal Obsidian workflow in 2026 — capture, frontmatter schemas, technical KB patterns, media tracking, selective publishing, and in-vault AI — with Bases-first design and local-first AI as the unifying threads."
cover: cover.svg
synthesis: true
children:
  - slug: low-friction-capture-ai-assisted-backfill
    title: "Low-friction capture & AI-assisted backfill"
    depth: deep
    status: success
    summary: "How to lower capture friction across desktop, mobile, web, voice — and how to run AI tag/metadata backfill across an existing vault in 2026."
    citations: 80
    reading_time_min: 13
  - slug: frontmatter-tagging-schemas-for-extraction
    title: "Frontmatter & tagging schemas for extraction"
    depth: deep
    status: success
    summary: "How to design Obsidian YAML frontmatter and tag taxonomies in 2026 so external tools can reliably extract, query, and validate the metadata."
    citations: 69
    reading_time_min: 11
  - slug: knowledge-base-patterns-for-a-technical-vault
    title: "Knowledge-base patterns for a technical vault"
    depth: deep
    status: success
    summary: "What actually works for a technical Obsidian vault in 2026: hybrid PARA+Zettel skeleton, Properties-first metadata, daily-note capture, MOCs over deep folders, and a small high-value plugin set."
    citations: 84
    reading_time_min: 14
  - slug: automated-media-tracking-books-movies-series
    title: "Automated media tracking (books / movies / series)"
    depth: standard
    status: success
    summary: "Pick a tracking hub per medium (Hardcover for books, Simkl for film/TV), automate capture with Readwise + CrossWatch, and pull into Obsidian via Media DB or Book Search plugins."
    citations: 30
    reading_time_min: 7
  - slug: selective-publishing-to-github-pages-or-equivalents
    title: "Selective publishing to GitHub Pages or equivalents"
    depth: standard
    status: success
    summary: "Pick the opt-in (whitelist) frontmatter pattern over draft-style opt-out; Quartz + ExplicitPublish is the closest free match to Obsidian Publish."
    citations: 17
    reading_time_min: 5
  - slug: ai-plugins-for-in-vault-retrieval-summarization
    title: "AI plugins for in-vault retrieval & summarization"
    depth: standard
    status: success
    summary: "Pick Smart Connections for local-first retrieval, Copilot for polished vault chat with optional Plus tier, Smart Composer for Cursor-style edits, Khoj for cross-device self-hosted second-brain. Text Generator and the small ai-summary plugins cover dedicated summarization."
    citations: 20
    reading_time_min: 5
cost_usd: 30.66
duration_sec: 3591
citations: 300
reading_time_min: 55
---

The six angles answer six different questions, but they all converge on the same 2026 inflection point: **Bases became a core plugin in Obsidian 1.9 (May 2025) and stabilised in 1.10 (Oct 2025) with card/list/Maps views and a public layout API** [[1]](https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/), while Dataview has gone effectively unmaintained for over a year [[2]](https://medium.com/@lennart.dde/obsidian-dataview-is-dead-long-live-bases-9750e8a92877). Every recommendation in this expedition cascades from that single fact.

**The schema is the load-bearing decision.** Bases reads only YAML frontmatter — it silently ignores the inline `key:: value` Dataview idiom [[3]](https://practicalpkm.com/bases-plugin-overview/). So the upgrade order is: design typed-Properties first (a mandatory `type:` discriminator à la kepano [[4]](https://stephango.com/vault), flat keys since Properties has no nested objects [[5]](https://help.obsidian.md/properties), and plural reserved keys `tags`/`aliases`/`cssclasses` which became mandatory in 1.9 [[1]](https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/)) — then route every workflow into it. Capture writes into the schema (Web Clipper Interpreter does LLM template-fill of summary/tags/author [[6]](https://help.obsidian.md/web-clipper/interpreter); AI Tagger Universe does whole-vault batch backfill [[7]](https://github.com/niehu2018/obsidian-ai-tagger-universe)). Media tracking writes into it (Media DB, Book Search). Publishing reads it (`publish: true` is Quartz's `ExplicitPublish` filter [[8]](https://quartz.jzhao.xyz/plugins/ExplicitPublish)). AI plugins query it (Smart Connections, Copilot, Smart Composer).

**Local-first AI is the second cross-cutting thread.** Ollama + `nomic-embed-text` + [Llama 3.1 8B](https://www.llama.com/) (or [Qwen 2.5 32B](https://qwenlm.ai/) for quality) is the free backbone — it runs the AI Tagger Universe retro-fill, embeds for Smart Connections discovery, and chats through Copilot's `localhost:11434` adapter using the documented `OLLAMA_ORIGINS=app://obsidian.md*` workaround for CORS [[9]](https://github.com/logancyang/obsidian-copilot/blob/master/local_copilot.md). One subtle warning recurs: **don't double-index**. Running Smart Connections + Copilot Vault QA + Smart Composer RAG simultaneously means three separate embedding indexes over the same notes [[10]](https://forum.obsidian.md/t/alternatives-to-smart-connections/108886). Pick one chat plugin; let Smart Connections own the discovery sidebar.

**Three failure modes recur across angles.** First, **Periodic Notes is unmaintained since 2022** — migrate to Journals before automating anything calendar-shaped [[11]](https://forum.obsidian.md/t/plugin-journals/76946) (the KB and capture children disagree here; Journals is the correct 2026 pick). Second, the **selective-publish leak**: even with `publish: true`, Quartz emits all non-markdown attachments — *"images, voice recordings, PDFs"* [[12]](https://quartz.jzhao.xyz/features/private-pages). Keep the raw vault private and mirror only flagged content into the SSG repo via GitHub Actions. Third, **don't store media catalogues in Obsidian** — Hardcover (books, free GraphQL API [[13]](https://docs.hardcover.app/api/getting-started/)) and Simkl (unlimited free tier vs Trakt's new 100-item watchlist+collection cap [[14]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt)) are the master; Obsidian mirrors via Media DB or Book Search.

**Migration order for an existing vault.** (1) Write a master-schema note declaring every Property name + type [[15]](https://chughkabir.com/guide-obsidian-bases/); (2) replace Periodic Notes with Journals; (3) install the official Web Clipper, retire Omnivore/MarkDownload remnants [[16]](https://github.com/obsidianmd/obsidian-clipper); (4) stand up Ollama and run AI Tagger Universe `Generate tags for vault` over historical notes against a hand-curated taxonomy [[17]](https://www.makeuseof.com/letting-local-llm-organize-obsidian-notes/); (5) add Smart Connections (sidebar) + exactly one of Copilot/Smart Composer (chat); (6) wire Quartz with `ExplicitPublish` only after the schema is stable, since `publish: true` is the gate.

**Open questions left after all six angles.** Calendar → daily-note retro-fill (Google Calendar / iCal as a passive source for "shows attended last weekend") is not covered by any 2026 plugin in the survey — the closest match is iOS Shortcuts or a custom MCP integration via `MarkusPfundstein/mcp-obsidian`'s `patch_content` tool [[18]](https://github.com/MarkusPfundstein/mcp-obsidian). Apple Foundation Models SDK has no dedicated Obsidian wrapper yet despite Electron exposing the native API on macOS 15.1+ [[19]](https://forum.obsidian.md/t/support-apple-intelligence-writing-tools-on-desktop/84137) — an open opportunity for a 2026 plugin author.
