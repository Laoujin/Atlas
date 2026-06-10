---
layout: expedition
title: "Self-hosted YouTube archivers: web UI, channel watching, and liked-video sync (2026)"
date: 2026-06-09
topic: "Survey and compare self-hosted YouTube downloaders with web UI, channel watching, and liked-video sync (2026)."
format: md
tags: [self-hosted, youtube, yt-dlp, archiving, channel-monitoring]
summary: "TubeArchivist vs PinchFlat is the real decision — all six tools wrap yt-dlp, so the differentiators are UI depth, filter richness, and willingness to run Elasticsearch."
cover: cover.svg
synthesis: true
children:
  - slug: core-candidates-survey
    title: "Core candidates survey"
    depth: deep
    status: success
    summary: "Six self-hosted YouTube tools compared on web UI, channel watching, and liked-video sync — TubeArchivist vs PinchFlat is the real decision."
    citations: 38
    reading_time_min: 7
  - slug: channel-watching-and-new-upload-automation
    title: "Channel watching and new-upload automation"
    depth: deep
    status: success
    summary: "How PinchFlat, TubeArchivist, ytdl-sub, TubeSync and MeTube watch channels for new uploads — scheduling models, download filters, the RSS-vs-yt-dlp detection layer, and 2026 throttle/ban etiquette."
    citations: 41
    reading_time_min: 8
  - slug: youtube-liked-and-saved-video-sync
    title: "YouTube liked and saved video sync"
    depth: standard
    status: success
    summary: "How to sync YouTube liked videos and saved playlists to a self-hosted archive — tool comparison, cookie auth methods, and the IP-ban tradeoff."
    citations: 16
    reading_time_min: 5
cost_usd: 13.80
duration_sec: 1934
citations: 95
reading_time_min: 20
issue: 211
model: "Sonnet 4.6"
---

All six candidates wrap [yt-dlp](https://github.com/yt-dlp/yt-dlp) ⭐ 169k — so the "which tool" question is secondary to the shared infrastructure question: every project breaks together when YouTube tightens bot detection, and the February 2026 `LOGIN_REQUIRED` bot wall hit all simultaneously [[issue #15865]](https://github.com/yt-dlp/yt-dlp/issues/15865). Plan for monthly yt-dlp updates and, for unattended operation, a co-deployed [bgutil POT provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider) ⭐ 559 to mint proof-of-origin tokens on demand.

**The binary decision** confirmed across all three sub-topics: [TubeArchivist](https://github.com/tubearchivist/tubearchivist) ⭐ 8.1k vs [PinchFlat](https://github.com/kieraneglin/pinchflat) ⭐ 5.0k. These are not interchangeable — they solve different problems. TubeArchivist is a self-contained watch application: Elasticsearch full-text search across transcripts and comments, an in-browser player with watched-state tracking, and real multi-user auth. The cost is three containers at ~4 GB RAM [[docs]](https://docs.tubearchivist.com/installation/docker-compose/). PinchFlat is a single-container SQLite channel/playlist manager that feeds Jellyfin, Plex, or Kodi; it explicitly states it is "not for consuming content in-app" [[GitHub]](https://github.com/kieraneglin/pinchflat). If you already run a media server, PinchFlat slots in without duplication. If you don't and want one app for everything, TubeArchivist is the choice — and its Elasticsearch weight is the canonical reason people switch away.

**Automation depth diverges hard.** PinchFlat leads on download filtering: per-source title regex, download cutoff date, min/max duration, Shorts/livestream toggles, and a dry-run preview tab [[FAQ wiki]](https://github.com/kieraneglin/pinchflat/wiki/Frequently-Asked-Questions). TubeArchivist has none of those filters; the only lever is a per-channel page-size override to disable Shorts or livestreams globally [[channels docs]](https://docs.tubearchivist.com/channels/). For post-download automation, PinchFlat again: Apprise notifications, SponsorBlock, and per-event lifecycle scripts (bash/Python, `jq` bundled) at a single hook path [[lifecycle wiki]](https://github.com/kieraneglin/pinchflat/wiki/%5BAdvanced%5D-Custom-lifecycle-scripts). TubeSync and ytdl-sub both match PinchFlat on filter breadth, but TubeSync carries open reports of stalled and mass-skipped downloads [[issue #459]](https://github.com/meeb/tubesync/issues/459) and ytdl-sub requires YAML fluency with no browser UI.

**Liked-video sync is universally supported and universally fragile.** All candidates feed yt-dlp a browser cookie to reach the private `LL` playlist. TubeArchivist makes this smoothest — the companion extension pushes cookies with one click and immediately validates them by testing access to your Liked Videos [[app settings]](https://docs.tubearchivist.com/settings/application/). The fragility is system-level, not tool-level: Chrome 127+ (July 2024) introduced app-bound encryption that blocks all external cookie readers, leaving Firefox as the only reliable source in 2026 [[cookie guide]](https://dev.to/osovsky/6-ways-to-get-youtube-cookies-for-yt-dlp-in-2026-only-1-works-2cnb); cookies expire in roughly two weeks when used outside a browser [[PinchFlat wiki]](https://github.com/kieraneglin/pinchflat/wiki/YouTube-Cookies); and a known yt-dlp bug can return only ~11 items from a large liked playlist in a single run [[issue #8732]](https://github.com/yt-dlp/yt-dlp/issues/8732). Re-exporting Firefox cookies on a ~10-day cadence is the irreducible manual step regardless of tool choice.

**For a self-hoster who values polished UI and automation depth**: run PinchFlat + Jellyfin/Plex if you already have a media server — it wins on filter richness, lifecycle hooks, and operational simplicity. Run TubeArchivist if you want a standalone YouTube-at-home experience with in-browser playback and full-text search. The unsettled question is whether PO token enforcement stabilizes enough for genuine set-and-forget operation: right now, plan for periodic hands-on maintenance, not zero-touch.
