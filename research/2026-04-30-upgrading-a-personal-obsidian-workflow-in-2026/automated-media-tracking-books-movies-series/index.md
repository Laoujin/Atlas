---
title: "Automated media tracking for an Obsidian workflow (2026)"
date: 2026-04-30
depth: standard
format: md
topic: "Automated media tracking (books / movies / series)"
topic_raw: "Automated media tracking (books / movies / series)"
issue: 49
tags: [obsidian, media-tracking, automation, books, movies, tv]
summary: "Pick a tracking hub per medium (Hardcover for books, Simkl for film/TV), automate capture with Readwise + CrossWatch, and pull into Obsidian via Media DB or Book Search plugins."
citations: 30
reading_time_min: 7
cover: cover.svg
cost_usd: 2.87
duration_sec: 473
---

> **Decision.** Treat tracking as a 3-layer pipeline, not a single app.
> **Books:** Hardcover (GraphQL API [[9]](https://docs.hardcover.app/api/getting-started/)) for the catalog, Readwise [[15]](https://docs.readwise.io/readwise/docs/exporting-highlights/obsidian) for highlights → Obsidian Book Search plugin [[2]](https://github.com/anpigon/obsidian-book-search-plugin) ⭐ 685 for note creation.
> **Film/TV:** Simkl (auto-scrobble, unlimited free [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt)) as the hub, CrossWatch [[7]](https://github.com/cenodude/CrossWatch) ⭐ 568 to bridge Plex/Jellyfin → trackers, Letterboxd RSS sync [[8]](https://github.com/Fleker/letterboxd-for-obsidian) ⭐ 18 to mirror your film diary into the vault.
> **All-in-one shortcut:** if you'd rather skip external services, use the Media DB plugin [[1]](https://github.com/mProjectsCode/obsidian-media-db-plugin) ⭐ 448 — one Obsidian plugin, one search command, ten APIs.

---

## The three layers

| Layer | Job | Don't conflate with |
|---|---|---|
| **Hub** | Source of truth for "what I've consumed/want to consume" | Your Obsidian vault — vault is a *mirror*, not the master |
| **Capture** | Auto-detects activity (scrobble, highlight, finish) and pushes to the hub | Manual logging — if you have to type it, automation has failed |
| **Obsidian** | Renders metadata + your prose notes for search, linking, and Dataview dashboards [[27]](https://www.dsebastien.net/the-must-have-obsidian-plugins-for-2026/) | The hub — Obsidian is bad at lists of 1000+ books/films |

Picking these in the wrong order is the most common failure mode: people build a beautiful Obsidian Dataview dashboard, then realise nothing flows in automatically.

---

## Layer 1 — Tracking hubs

### Books

| Hub | Free tier | API | Goodreads import | Best for |
|---|---|---|---|---|
| **Hardcover** | Free, ad-free [[14]](https://bookwiseapp.com/blog/hardcover-vs-storygraph) | ✓ Free GraphQL [[9]](https://docs.hardcover.app/api/getting-started/) [[10]](https://www.emgoto.com/hardcover-book-api/) | ✓ Strong [[26]](https://yourbookfriend.com/2025/11/26/how-to-track-your-reading-in-2026-goodreads-alternatives-and-comparisons/) | Building your own pipeline; "Letterboxd for books" community |
| **StoryGraph** | Free | ✗ No public API in 2026 [[11]](https://roadmap.thestorygraph.com/features/posts/an-api); CSV export only [[12]](https://x.com/thestorygraph/status/1527600015450963969); unofficial scraper [[13]](https://pypi.org/project/storygraph-api/) | ✓ | Mood-based recs, deep stats — but a dead-end for automation |
| [**Goodreads**](https://www.goodreads.com/) | Free | ⚠ API closed for new keys since 2020 | n/a | Skip in 2026 [[26]](https://yourbookfriend.com/2025/11/26/how-to-track-your-reading-in-2026-goodreads-alternatives-and-comparisons/) |
| **Readwise** (highlights, not catalog) | $9.99/mo Full plan [[17]](https://readwise.io/pricing/reader) | ✓ Official | n/a | Kindle/Apple Books/PDF highlights → Obsidian [[15]](https://docs.readwise.io/readwise/docs/exporting-highlights/obsidian) |

→ **The 2026 split:** if you want programmatic sync, Hardcover [[10]](https://www.emgoto.com/hardcover-book-api/) is the only free hub with a real API. StoryGraph is a better *reader* but a worse *source* — its solo developer has explicitly said API is not a priority [[11]](https://roadmap.thestorygraph.com/features/posts/an-api).

### Film & TV

| Hub | Free limits | Auto-scrobble | API | 2026 catch |
|---|---|---|---|---|
| **Simkl** | Unlimited watchlist [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt) | ✓ Browser ext + Plex/Jellyfin [[24]](https://simkl.com/apps/jellyfin/) | ✓ Free REST | Best anime support via AniDB [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt) |
| [**Trakt**](https://trakt.tv/) | ⚠ 100 watchlist+collection items [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt) | Plex webhook is VIP-only [[23]](https://forums.trakt.tv/t/plex-webhook/19092) | ✓ Stable, biggest 3rd-party ecosystem | 2026 cap turned a lot of free users into Simkl users [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt) |
| **Letterboxd** | Free | ✗ Manual logging | ✗ No public API; RSS only [[8]](https://github.com/Fleker/letterboxd-for-obsidian) | Best film community + reviews [[5]](https://www.wako.app/guide/trakt-tv-alternatives) |
| **Serializd** | Free | ✗ Manual | ✗ | "Letterboxd for TV" [[5]](https://www.wako.app/guide/trakt-tv-alternatives) [[30]](https://www.achriom.com/blog/best-tv-tracking-apps/) |
| **TV Time** | Free | ✗ Manual | ✗ Closed | Social/discovery; vendor-locked [[5]](https://www.wako.app/guide/trakt-tv-alternatives) |

→ **Pick Simkl as the automation backbone.** Trakt's free 100-item cap [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt) is the headline 2026 change — if you've got a multi-year history, that's an instant disqualification. Keep Letterboxd alongside it for film *opinions* (reviews, lists), since Simkl's social side is thin [[5]](https://www.wako.app/guide/trakt-tv-alternatives).

---

## Layer 2 — Auto-capture pipelines

This is the layer most people skip and then complain that "tracking is too much work."

| Source | Sink | Tool | Notes |
|---|---|---|---|
| Plex / Jellyfin / Emby | Simkl + Trakt + AniList | **CrossWatch** [[6]](https://www.crosswatch.app/) [[7]](https://github.com/cenodude/CrossWatch) ⭐ 568 | Self-hosted Docker (`ghcr.io/cenodude/crosswatch:latest`); v0.9.18 (Apr 2026); deprecated webhooks → "Watcher" sync engine |
| Jellyfin | Simkl | Simkl Jellyfin add-on [[24]](https://simkl.com/apps/jellyfin/) | Native; pings API at e.g. 70% watched |
| Plex | Trakt | Trakt's own Plex webhook [[23]](https://forums.trakt.tv/t/plex-webhook/19092) | Requires Trakt VIP + Plex Pass |
| Plex | Trakt (legacy) | gazpachoking/trex [[29]](https://github.com/gazpachoking/trex) ⭐ 14 | ⚠ Unmaintained since Jan 2019 — avoid |
| Netflix / Hulu / Crunchyroll (browser) | Simkl | Simkl browser extension [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt) | More reliable than Trakt's Universal Scrobbler equivalent |
| Mobile (iOS/Android) | Trakt **and** Simkl | wako [[25]](https://www.wako.app/guide/best-movie-tracking-app) | Only mobile app supporting dual sync |
| Kindle / Apple Books / Pocket | Readwise → Obsidian | Readwise plugin [[15]](https://docs.readwise.io/readwise/docs/exporting-highlights/obsidian) [[16]](https://github.com/readwiseio/obsidian-readwise) ⭐ 335 | Auto-sync on app open or 1/12/24h schedule |

→ **The 2026 standard for self-hosters:** CrossWatch [[6]](https://www.crosswatch.app/). Its Watcher feature replaced webhook scripts (the project explicitly deprecated the old setup [[7]](https://github.com/cenodude/CrossWatch)) — one Docker container runs `Plex/Jellyfin/Emby ↔ Simkl/Trakt/AniList/MDBList` in any combination.

---

## Layer 3 — Pulling into Obsidian

| Plugin | What it does | API surface | Activity |
|---|---|---|---|
| **Media DB** [[1]](https://github.com/mProjectsCode/obsidian-media-db-plugin) ⭐ 448 | Single search command across movies/series/anime/manga/books/comics/games/music/wiki | TMDB, OMDb, Open Library, Jikan, MusicBrainz, Steam, VNDB, Wikipedia + more [[18]](https://www.obsidianstats.com/plugins/obsidian-media-db-plugin) | Active (Apr 2026 push) |
| **Book Search** [[2]](https://github.com/anpigon/obsidian-book-search-plugin) ⭐ 685 | Books-only, Templater-friendly, downloads covers locally [[3]](https://www.obsidianstats.com/plugins/obsidian-book-search-plugin) | Google Books + Naver | Last release Oct 2024 — slowing |
| **Letterboxd RSS Sync** [[8]](https://github.com/Fleker/letterboxd-for-obsidian) ⭐ 18 | Mirrors last 50 diary entries into one `Letterboxd Diary.md` | Letterboxd public RSS | Active (Nov 2025) |
| **Obsidian-TV-Tracker** [[19]](https://github.com/Shreshth-mehra/Obsidian-TV-Tracker) ⭐ 27 | Grid view of films/shows backed by YAML markdown files | TMDB | Active |
| **Calibre plugin** [[22]](https://github.com/caronchen/obsidian-calibre-plugin) ⭐ 190 | Browse a Calibre Content Server inside Obsidian | Calibre OPDS | ⚠ Unpushed since Sep 2023 |
| **Readwise official** [[16]](https://github.com/readwiseio/obsidian-readwise) ⭐ 335 | Highlights + book metadata from Kindle/Apple Books/etc. | Readwise | Active (Apr 2026) |
| **QuickAdd** [[20]](https://github.com/chhoumann/quickadd) ⭐ 2.2k | Macro engine — chain Book Search/Media DB/user scripts behind one hotkey [[21]](https://quickadd.obsidian.guide/docs/Examples/Macro_BookFinder) | n/a | Active |

**Choosing between Media DB and Book Search.** Media DB [[1]](https://github.com/mProjectsCode/obsidian-media-db-plugin) wins on coverage (10 APIs, one workflow [[18]](https://www.obsidianstats.com/plugins/obsidian-media-db-plugin)) and recency. Book Search [[2]](https://github.com/anpigon/obsidian-book-search-plugin) wins on book-specific polish (cover-image download, mature template variables [[3]](https://www.obsidianstats.com/plugins/obsidian-book-search-plugin)). If you're books-only, Book Search; if you want everything-in-one, Media DB.

**The render layer (independent of plugin choice).** All of the above write YAML frontmatter. Layer Dataview + Templater + QuickAdd over them [[27]](https://www.dsebastien.net/the-must-have-obsidian-plugins-for-2026/) [[20]](https://github.com/chhoumann/quickadd) and your vault becomes a queryable dashboard. christt105/media-tracker-obsidian-template [[28]](https://github.com/christt105/media-tracker-obsidian-template) ⭐ 1 is a working starter vault wiring Movie Search + Templater + QuickAdd together — useful as a reference even if you don't fork it.

---

## Anti-patterns to avoid in 2026

- **Treating Goodreads as a hub.** Their API has been closed to new keys since 2020 and 2026 reading-app reviews unanimously recommend leaving [[26]](https://yourbookfriend.com/2025/11/26/how-to-track-your-reading-in-2026-goodreads-alternatives-and-comparisons/).
- **Picking Trakt for a fresh free account.** The 100-item watchlist+collection cap [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt) breaks a multi-year backlog on day one. Existing Trakt users with paid VIP are fine; new free users should default to Simkl.
- **Manual logging of films you watched on Plex/Jellyfin.** CrossWatch [[6]](https://www.crosswatch.app/) takes ~30 minutes to set up and never asks you to type a film title again.
- **Storing the master list in Obsidian.** Obsidian is excellent for note-taking, mediocre for "give me my last 200 watched films sorted by rating across 5 services" — let the hub do that and let Obsidian mirror.
- **Relying on unmaintained scrobblers.** trex's last commit was Jan 2019 [[29]](https://github.com/gazpachoking/trex); Trakt VIP webhook or CrossWatch Watcher [[7]](https://github.com/cenodude/CrossWatch) are the live paths.
- **Building over the StoryGraph "API."** There isn't one [[11]](https://roadmap.thestorygraph.com/features/posts/an-api); the unofficial scraper [[13]](https://pypi.org/project/storygraph-api/) can break with any UI change.

---

## Three concrete 2026 stacks

**Minimalist (Obsidian-only, no external services).**
Media DB plugin [[1]](https://github.com/mProjectsCode/obsidian-media-db-plugin) ⭐ 448 + QuickAdd [[20]](https://github.com/chhoumann/quickadd) ⭐ 2.2k macro per medium + Dataview dashboards [[27]](https://www.dsebastien.net/the-must-have-obsidian-plugins-for-2026/). One free TMDB key + one free OMDb key [[18]](https://www.obsidianstats.com/plugins/obsidian-media-db-plugin). No subscription, no auto-scrobble.

**Hybrid (recommended for most).**
- Books: Hardcover hub [[9]](https://docs.hardcover.app/api/getting-started/) + Readwise highlights [[15]](https://docs.readwise.io/readwise/docs/exporting-highlights/obsidian) → Book Search plugin [[2]](https://github.com/anpigon/obsidian-book-search-plugin) for vault notes + a custom GraphQL puller from Hardcover for completed-list mirror.
- Film/TV: Simkl hub [[4]](https://docs.simkl.org/how-to-use-simkl/faq/frequently-asked-questions/simkl-alternatives/simkl-vs-trakt) + Simkl browser extension + Letterboxd for film opinions → Letterboxd RSS Sync plugin [[8]](https://github.com/Fleker/letterboxd-for-obsidian) for diary mirror; Media DB plugin for per-title metadata notes.
- Cost: $9.99/mo Readwise [[17]](https://readwise.io/pricing/reader); rest free.

**Power-user (self-hosted media server).**
- Plex/Jellyfin running locally + CrossWatch Docker [[6]](https://www.crosswatch.app/) [[7]](https://github.com/cenodude/CrossWatch) ⭐ 568 syncing to Simkl + Trakt + AniList simultaneously.
- wako [[25]](https://www.wako.app/guide/best-movie-tracking-app) on mobile for off-server scrobbles, Hardcover for books, Readwise for highlights.
- Obsidian: Media DB + Letterboxd RSS Sync + Obsidian-TV-Tracker [[19]](https://github.com/Shreshth-mehra/Obsidian-TV-Tracker) for the in-vault grid view.
