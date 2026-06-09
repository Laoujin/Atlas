---
title: "YouTube Liked & Saved Video Sync"
date: 2026-06-09
depth: standard
format: md
topic: "YouTube liked and saved video sync"
topic_raw: "YouTube liked and saved video sync"
issue: 211
tags: [youtube, liked-videos, sync, yt-dlp, self-hosted, authentication, cookies]
summary: "How to sync YouTube liked videos and saved playlists to a self-hosted archive — tool comparison, cookie auth methods, and the IP-ban tradeoff."
citations: 16
reading_time_min: 5
cover: cover.svg
cost_usd: 1.45
duration_sec: 393
model: "Sonnet 4.6"
---

> **TL;DR** — [TubeArchivist](https://github.com/tubearchivist/tubearchivist) ⭐ 8.1k is the best turnkey option: import a Firefox cookie once via its companion extension and liked videos / Watch Later become ordinary subscribed playlists [[1]](https://docs.tubearchivist.com/settings/application/). For CLI-only use, `yt-dlp --cookies-from-browser firefox --download-archive archive.txt "https://www.youtube.com/playlist?list=LL"` does incremental sync but needs cookie refresh every ~2 weeks [[3]](https://github.com/yt-dlp/yt-dlp) [[4]](https://dev.to/osovsky/6-ways-to-get-youtube-cookies-for-yt-dlp-in-2026-only-1-works-2cnb). ⚠ All cookie-based sync carries an IP-ban risk — yt-dlp itself now flags this [[7]](https://github.com/kieraneglin/pinchflat/wiki/YouTube-Cookies).

## The core challenge

YouTube's Liked Videos (`?list=LL`) and Watch Later (`?list=WL`) are private playlists — no public URL, no unauthenticated access. Every tool ultimately passes browser cookies to yt-dlp [[3]](https://github.com/yt-dlp/yt-dlp), which accesses YouTube via the InnerTube API [[16]](https://ostechnix.com/yt-dlp-tutorial/). That means two recurring headaches:

1. **Cookie extraction**: Only Firefox works reliably in 2026. Chrome 127+ (July 2024) introduced app-bound encryption that blocks all external cookie readers [[4]](https://dev.to/osovsky/6-ways-to-get-youtube-cookies-for-yt-dlp-in-2026-only-1-works-2cnb). OAuth and bearer-token approaches don't work with yt-dlp's InnerTube path [[16]](https://ostechnix.com/yt-dlp-tutorial/).
2. **Cookie lifespan**: YouTube expires cookies in approximately two weeks when used outside a browser [[7]](https://github.com/kieraneglin/pinchflat/wiki/YouTube-Cookies) [[16]](https://ostechnix.com/yt-dlp-tutorial/). Re-exporting Firefox cookies is a recurring manual step unless automated.

Additionally, yt-dlp has a known, unresolved bug where the liked playlist sometimes returns only ~11 items instead of the full list — YouTube's dynamic pagination isn't always fully traversed [[5]](https://github.com/yt-dlp/yt-dlp/issues/8732). Running the command multiple times (with `--download-archive`) usually recovers the full set.

## Tool comparison

| Tool | Liked ✓/✗ | Watch Later ✓/✗ | Auth method        | Auto-sync | Notes |
|------|-----------|-----------------|--------------------|-----------|-------|
| [TubeArchivist][ta] ⭐ 8.1k | ✓ | ✓ | Cookie (ext or paste) | ✓ | Becomes a regular subscribed playlist [[1]](https://docs.tubearchivist.com/settings/application/) |
| [Pinchflat][pf] ⭐ 5.0k | ✓ | ✓ | `cookies.txt` | ✓ | Per-source cookie behavior; ⚠ IP ban risk [[7]](https://github.com/kieraneglin/pinchflat/wiki/YouTube-Cookies) |
| [yt-dlp][ytdlp] ⭐ 169k | ✓ | ✓ | `--cookies-from-browser` | Via cron | Partial-items bug [[5]](https://github.com/yt-dlp/yt-dlp/issues/8732); manual cookie refresh [[4]](https://dev.to/osovsky/6-ways-to-get-youtube-cookies-for-yt-dlp-in-2026-only-1-works-2cnb) |
| [ytdl-sub][yts] ⭐ 2.8k | ✓ | ✓ | `cookiefile` passthrough | Via cron | No dedicated liked-videos UI [[9]](https://github.com/jmbannon/ytdl-sub) |
| [Syncify][sy] ⭐ 77 | ✓ | ✓ | `cookies.txt` | ✓ | Scheduled sync; not liked-specific [[8]](https://github.com/TheWicklowWolf/Syncify) |
| [ytm-yld][ytmy] ⭐ 6 | ✓ (YTM only) | ✗ | OAuth (ytmusicapi) | Manual | YouTube Music liked songs only; deletes removed tracks [[11]](https://github.com/pepershukov/ytm-yld) |

[ta]: https://github.com/tubearchivist/tubearchivist
[pf]: https://github.com/kieraneglin/pinchflat
[ytdlp]: https://github.com/yt-dlp/yt-dlp
[yts]: https://github.com/jmbannon/ytdl-sub
[sy]: https://github.com/TheWicklowWolf/Syncify
[ytmy]: https://github.com/pepershukov/ytm-yld

## TubeArchivist — recommended for liked/saved sync

[TubeArchivist](https://github.com/tubearchivist/tubearchivist) ⭐ 8.1k [[2]](https://github.com/tubearchivist/tubearchivist) has the best UX for this use case. The [Companion browser extension](https://github.com/tubearchivist/browser-extension) ⭐ 256 (Firefox and Chrome) pushes your cookies directly into TubeArchivist with one click [[15]](https://github.com/tubearchivist/browser-extension). Once imported, liked videos and Watch Later are treated identically to any other playlist subscription [[10]](https://docs.tubearchivist.com/playlists/):

- Add the liked videos URL (`https://www.youtube.com/playlist?list=LL`) as a playlist subscription
- Enable periodic rescan in settings → TubeArchivist pulls new likes automatically
- A single cookie is shared across all TubeArchivist users on the instance

**Validation**: TubeArchivist considers a cookie valid only if yt-dlp can successfully access the private liked playlist — so you know immediately if auth has expired [[1]](https://docs.tubearchivist.com/settings/application/).

## Pinchflat — flexible with caveats

[Pinchflat](https://github.com/kieraneglin/pinchflat) ⭐ 5.0k [[6]](https://github.com/kieraneglin/pinchflat) supports cookies via a `cookies.txt` file placed in the config directory. Three behaviors are configurable per source [[7]](https://github.com/kieraneglin/pinchflat/wiki/YouTube-Cookies):

- **Disabled** — never uses cookies
- **When Needed** — tries without cookies first, retries with them on failure
- **All Operations** — cookies on every request

⚠ As of 2026, yt-dlp's own documentation warns that YouTube cookies can trigger IP bans and recommends users "proceed at their own risk" [[7]](https://github.com/kieraneglin/pinchflat/wiki/YouTube-Cookies).

## yt-dlp CLI — incremental sync pattern

For a cron-driven setup, the standard command [[13]](https://mintlify.wiki/yt-dlp/yt-dlp/guides/playlists) [[14]](https://www.tglyn.ch/blog/youtube_download_for_djs/):

```bash
yt-dlp \
  --cookies-from-browser firefox \
  --download-archive ~/yt-liked.txt \
  --limit-rate 5M \
  --sleep-interval 5 --max-sleep-interval 15 \
  "https://www.youtube.com/playlist?list=LL"
```

The `--download-archive` flag appends each downloaded video ID; subsequent runs skip already-archived items [[13]](https://mintlify.wiki/yt-dlp/yt-dlp/guides/playlists). Rate-limiting flags (`--limit-rate`, `--sleep-interval`) reduce ban risk for unattended jobs [[14]](https://www.tglyn.ch/blog/youtube_download_for_djs/).

**Watch Later** uses the same pattern with `?list=WL`.

> Note: the partial-items bug [[5]](https://github.com/yt-dlp/yt-dlp/issues/8732) means a single run may not fetch all liked videos. Running the command 2–3 times in sequence (archive prevents re-downloads) usually recovers the full list.

## YouTube Music liked songs (separate path)

YouTube Music liked songs are a distinct dataset from YouTube liked videos. [ytm-yld](https://github.com/pepershukov/ytm-yld) ⭐ 6 [[11]](https://github.com/pepershukov/ytm-yld) uses OAuth via `ytmusicapi` — no cookies needed, no IP-ban risk — and syncs the `Your Likes` playlist with local deletion of removed tracks. The tradeoff: it's YTMusic-only, not the main YouTube feed.

## Cookie refresh strategy

Since cookies expire in ~2 weeks [[7]](https://github.com/kieraneglin/pinchflat/wiki/YouTube-Cookies) [[4]](https://dev.to/osovsky/6-ways-to-get-youtube-cookies-for-yt-dlp-in-2026-only-1-works-2cnb), schedule refresh before expiry:

1. Open Firefox, log into YouTube
2. Re-export cookies (browser extension, or manual Netscape export)
3. Re-import into TubeArchivist / overwrite `cookies.txt` in Pinchflat/Syncify
4. Validate in TubeArchivist settings

Automating this export is theoretically possible via a Firefox profile query script, but cookie misuse risks account bans — manual re-import is the safer cadence [[4]](https://dev.to/osovsky/6-ways-to-get-youtube-cookies-for-yt-dlp-in-2026-only-1-works-2cnb) [[12]](https://github.com/yt-dlp/yt-dlp/issues/518).
