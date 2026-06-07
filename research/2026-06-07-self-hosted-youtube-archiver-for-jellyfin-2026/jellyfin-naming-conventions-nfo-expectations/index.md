---
title: "Jellyfin naming conventions & NFO expectations"
date: 2026-06-07
depth: ceo
format: md
topic: "Jellyfin naming conventions & NFO expectations"
topic_raw: "Jellyfin naming conventions & NFO expectations"
issue: 194
tags: [media-server, jellyfin, metadata, nfo, file-organization]
summary: "Standard folder and file naming patterns for movies, TV, and music in Jellyfin, plus NFO sidecar metadata format and configuration."
citations: 4
reading_time_min: 2
cost_usd: 0.20
duration_sec: 66
model: "Haiku 4.5"
---

> **TL;DR:** Follow `Movie Name (Year)/Movie Name (Year).mkv` for movies [[1]](https://jellyfin.org/docs/general/server/media/movies/) and `Show Name/Season 01/Show Name - S01E01.mkv` for TV. Use NFO sidecar files (movie.nfo, tvshow.nfo, etc.) to override or supplement remote metadata; they're XML-based and take priority over online providers [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/).

## File Naming Conventions

### Movies

- **Folder structure:** `Movie Name (Year)/Movie Name (Year).mkv` [[1]](https://jellyfin.org/docs/general/server/media/movies/)
- **Year is critical:** disambiguates films with identical titles (e.g., "The Thing (1982)" vs "The Thing (2011)") [[3]](https://brainvoyage.blog/jellyfin-shows-directory-structure-guide)
- **Multiple versions:** use format `Movie Name (Year) - [version label].mkv` (note: space-hyphen-space required), e.g. `The Dark Knight (2008) - 1080p.mkv` [[1]](https://jellyfin.org/docs/general/server/media/movies/)
- **Reserved characters to avoid:** `< > : " / \ | ? *` [[1]](https://jellyfin.org/docs/general/server/media/movies/)
- **Metadata provider IDs (optional):** add TMDB or IMDb ID to improve matching: `Movie Name (Year) [tmdb-12345]` [[3]](https://brainvoyage.blog/jellyfin-shows-directory-structure-guide)

### TV Shows

- **Folder structure:** `Show Name/Season 01/Show Name - S01E01 - Episode Title.mkv` [[1]](https://jellyfin.org/docs/general/server/media/movies/)
- **Zero-padded episode numbers:** use `S01E01`, not `S1E1` [[3]](https://brainvoyage.blog/jellyfin-shows-directory-structure-guide)
- **Specials:** place in `Season 00` folder
- **Multi-episode files:** `Show Name - S01E01-E02.mkv` [[3]](https://brainvoyage.blog/jellyfin-shows-directory-structure-guide)

### Music

- **Folder structure:** `Artist Name/Album Name (Year)/01 - Track Title.flac` [[3]](https://brainvoyage.blog/jellyfin-shows-directory-structure-guide)
- **Cover art:** include `cover.jpg` in each album folder [[3]](https://brainvoyage.blog/jellyfin-shows-directory-structure-guide)

## NFO Metadata Files

NFO files are optional but powerful sidecar metadata files. Local NFO data always takes priority over remote providers like TMDb [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/).

| Media Type | NFO Filename | Location |
|---|---|---|
| Movies | `movie.nfo` or `<filename>.nfo` | Same folder as video file [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/) |
| TV Shows (series) | `tvshow.nfo` | Root show folder [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/) |
| TV Seasons | `season.nfo` | Each season folder [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/) |
| TV Episodes | `<filename>.nfo` | Same folder as episode file [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/) |
| Music Artists | `artist.nfo` | Artist folder [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/) |
| Music Albums | `album.nfo` | Album folder [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/) |

### NFO Format & Tags

NFO files use XML with standard metadata tags. Common supported tags [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/):

- **Core:** title, originaltitle, year, rating, plot, tagline, runtime
- **Credits:** director, writer, actor, studio
- **Classification:** genre, country, language, mpaa rating
- **IDs:** imdb, tmdb, tvdb (and other provider-specific IDs)
- **Images:** thumb, fanart (only the first of each type is used)

When multiple tags map to the same data (e.g., plot vs review), the last tag in the file takes priority [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/).

## Best Practices

- **Separate libraries by type:** don't mix movies and TV in a single library—Jellyfin struggles with metadata and browsing [[4]](https://diymediaserver.com/post/how-proper-organization-helps-jellyfin-automatically-fetch-metadata-and-display-content-correctly/)
- **Enable NFO Saver:** use Jellyfin's "Nfo Saver" setting to auto-write metadata changes back to NFO files for future portability [[2]](https://jellyfin.org/docs/general/server/metadata/nfo/)
- **Automate with tools:** Radarr (movies) and Sonarr (TV) automatically rename and organize files on import [[3]](https://brainvoyage.blog/jellyfin-shows-directory-structure-guide)
