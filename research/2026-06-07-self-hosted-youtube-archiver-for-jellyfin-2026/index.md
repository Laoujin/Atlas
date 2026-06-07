---
layout: expedition
title: "Self-Hosted YouTube Archiver for Jellyfin (2026)"
date: 2026-06-07
topic: "Evidence-based ranked recommendation: self-hosted YouTube archiver to replace a flaky NAS container, with Jellyfin output (2026)."
format: md
tags: [youtube, jellyfin, yt-dlp, self-hosted, authentication]
summary: "Critical auth requirements (PO tokens, Firefox-only cookies) and Jellyfin TV-show naming contracts researched; the tool comparison matrix and deploy config were not completed and require a follow-up run."
cover: cover.svg
synthesis: true
children:
  - slug: tool-feature-health-comparison-matrix
    title: "Tool feature & health comparison matrix"
    depth: standard
    status: success
    summary: "Framework for evaluating software tools on two orthogonal axes — feature completeness and project health — with measurement tooling and a worked AI coding tools example."
    citations: 20
    reading_time_min: 6
  - slug: youtube-auth-cookies-watch-later-mechanics-2026
    title: "YouTube auth, cookies & Watch-Later mechanics (2026)"
    depth: standard
    status: success
    summary: "How YouTube's cookie-based auth works in 2026: the SAPISID/SAPISIDHASH flow, PO token requirements, Chrome's app-bound encryption breaking external extraction, and Watch Later's API quirks."
    citations: 16
    reading_time_min: 4
  - slug: jellyfin-naming-conventions-nfo-expectations
    title: "Jellyfin naming conventions & NFO expectations"
    depth: ceo
    status: success
    summary: "Standard folder and file naming patterns for movies, TV, and music in Jellyfin, plus NFO sidecar metadata format and configuration."
    citations: 4
    reading_time_min: 2
  - slug: winner-deploy-config
    title: "Winner deploy config"
    depth: ceo
    status: success
    summary: "Network deployment of Winner Design requires a dedicated server, 1 Gbit/s wired bandwidth, and optional centralized rendering offload."
    citations: 3
    reading_time_min: 2
cost_usd: 3.50
duration_sec: 1491
citations: 43
reading_time_min: 14
issue: 194
model: "Sonnet 4.6"
---

Four sub-topics were commissioned; two landed squarely on target, one produced a general evaluation methodology framework instead of the actual candidate data, and one researched an entirely unrelated product (kitchen CAD software branded "Winner Design").

**What the auth child established.** YouTube's cookie-based auth chain is now the only path for third-party tools — OAuth device-code login is deprecated for non-Google clients [[1]](https://deepwiki.com/yt-dlp/yt-dlp-wiki/3.2-youtube-authentication). Since Chrome 127 (July 2024) shipped app-bound AES encryption, Firefox is the only browser whose cookies are reliably extractable by external tools [[2]](https://dev.to/osovsky/6-ways-to-get-youtube-cookies-for-yt-dlp-in-2026-only-1-works-2cnb). More critically, Proof of Origin (PO) tokens are now mandatory for all YouTube video streams — a missing or invalid token returns HTTP 403, not a graceful auth error [[3]](https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide). This means any archiver that does not run a current yt-dlp build with a PO token provider (e.g. [bgutil-ytdlp-pot-provider](https://github.com/Brainicism/bgutil-ytdlp-pot-provider) [[4]](https://github.com/Brainicism/bgutil-ytdlp-pot-provider)) will silently fail on video downloads regardless of how polished its subscription or UI features are.

**What the Jellyfin child established.** Channel-as-show output must follow `Channel Name/Season XX/Channel Name - SXXEXX.mkv` to be recognized as a TV series by Jellyfin's scanner [[5]](https://jellyfin.org/docs/general/server/media/movies/). NFO sidecar files (`tvshow.nfo` at the channel root, per-episode `.nfo`) override all remote metadata and survive library rescans [[6]](https://jellyfin.org/docs/general/server/metadata/nfo/). YouTube libraries must be type-segregated — mixing YouTube content with live TV or movies in one library degrades metadata matching [[7]](https://diymediaserver.com/post/how-proper-organization-helps-jellyfin-automatically-fetch-metadata-and-display-content-correctly/).

**The critical coupling.** A YouTube archiver must solve both problems simultaneously: auth (PO tokens + Firefox cookies) and output naming (Jellyfin TV-show structure + NFO sidecars). Tools that handle auth but produce flat output — bare yt-dlp wrappers, basic download UIs — require a separate rename and NFO layer (ytdl-sub fills this role but adds configuration complexity). Tools with native Jellyfin output mapping must be verified to also keep their yt-dlp dependency current enough for PO token support. This two-axis coupling is where the candidate comparison should turn; neither a pure download UI nor a pure metadata layer satisfies both independently.

**Watch Later is a partial-sync target at best.** The YouTube Data API v3 permits `playlistItems.list` and `playlistItems.insert` for Watch Later (`WL`) but blocks update, delete, and reorder with 403 — enforced server-side [[8]](https://www.w3tutorials.net/blog/youtube-data-api-v3-playlistitems-update-not-working-for-watch-later-playlists/). Any archiver claiming "Watch Later sync" is doing authenticated yt-dlp polling of `https://www.youtube.com/playlist?list=WL` via browser cookies, not true two-way sync. Deletions from Watch Later in the YouTube UI cannot be mirrored to the local archive automatically. Rate limits compound this: authenticated sessions cap at ~2,000 videos/hour; unauthenticated sessions at ~300 [[1]](https://deepwiki.com/yt-dlp/yt-dlp-wiki/3.2-youtube-authentication).

**Cookie rotation is the silent failure mode for subscription workflows.** Exported cookies expire in approximately two weeks; leaving an authenticated browser tab open triggers background rotation scripts that invalidate already-exported cookies [[1]](https://deepwiki.com/yt-dlp/yt-dlp-wiki/3.2-youtube-authentication). Any unattended archiver running channel subscriptions on a NAS needs a cookie-rotation strategy built in or bolted on — either scheduled Firefox cookie re-export automation or a dedicated throwaway Google account whose cookies can be refreshed without affecting the primary account.

The sharpest open question this expedition leaves unanswered: which candidates among TubeArchivist, Pinchflat, ytdl-sub, MeTube, YoutubeDL-Material, and Tartube handle PO token generation natively through their yt-dlp integration, produce Jellyfin-compatible TV-show output without a rename step, and have bus-factor > 1 with active releases in the last six months — all three simultaneously? Those three axes would determine the ranked pick; none of the four children answered them.
