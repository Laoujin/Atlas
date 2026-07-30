---
title: "Microsoft 365 on Linux in 2026: what you actually lose"
date: 2026-07-30
depth: standard
format: md
topic: "Microsoft 365, OneNote, Outlook, Teams and OneDrive on Linux (2026): what a Windows-to-Linux switcher actually loses, and which of PWA, OnlyOffice/LibreOffice, native alternatives, or third-party sync clients closes the gap."
topic_raw: "can you check what software I have on my system installed (Windows) and then do a comparison with what I could replace that software with once I throw away Windows for Linux? (for those that are not available on Linux right away)"
tags: [linux, microsoft-365, onedrive, teams, onenote, migration]
summary: "Office, Teams and mail are a tolerable compromise on Linux in 2026; OneDrive sync and OneNote are the two places where the gap is real."
citations: 48
reading_time_min: 11
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 742
issue: 13
---

> **TL;DR** — Office-on-Linux is a **tolerable compromise**, not a solved problem and not a reason to keep Windows. Two of your installed apps have no honest replacement: **OneDrive** (no first-party client, and no Linux client offers files-on-demand [[1]](https://github.com/abraunegg/onedrive), while tenant policy can block the OSS ones outright [[2]](https://peterfalkingham.com/2026/03/04/office-365-and-linux-trying-to-use-linux-when-your-organization-is-all-in-and-locked-down-with-microsoft/)) and **OneNote** (web-only; the Obsidian importer refuses work/school accounts [[3]](https://obsidian.md/help/import/onenote)). Everything else lands: Teams is officially web/PWA-only even on Windows-adjacent terms [[4]](https://learn.microsoft.com/en-us/microsoftteams/teams-client-desktop-admin), Evolution 3.60 speaks Microsoft 365 **Graph** natively [[5]](https://discourse.gnome.org/t/is-microsoft-365-graph-api-expected-to-be-available-in-evolution-3-60-x/36019), and Excel for the web got the full Power Query editor in January 2026 [[6]](https://support.microsoft.com/en-us/office/use-power-query-in-excel-for-the-web-02652946-de70-48d8-8a34-3db96998ff5a)[[7]](https://www.acuitytraining.co.uk/news-tips/power-query-in-excel-for-the-web-whats-changed/).

## Your installed Microsoft/sync/AI stack, mapped

| Windows app (installed) | Linux replacement | Parity | Migration notes |
|---|---|---|---|
| `Microsoft 365 - en-us` + `- nl-nl` (Word/Excel/PowerPoint 16.0.20228) | [ONLYOFFICE Desktop Editors](https://github.com/ONLYOFFICE/DesktopEditors) ⭐ 5.1k + Office for the web | ⚠ | No native Office for Linux exists and won't [[8]](https://office-watch.com/2026/microsoft-office-linux/). OOXML is ONLYOFFICE's *native* format [[9]](https://api.onlyoffice.com/docs/macros/guides/getting-started/); keep LibreOffice for ODF and offline heavy lifting. VBA breaks everywhere → see fidelity section |
| `Microsoft OneNote - de-de/en-us/fr-fr/nl-nl` | OneNote for the web; [P3X OneNote](https://github.com/patrikx3/onenote) ⭐ 2.1k wrapper; migrate to Obsidian/Joplin | ⚠ | Weakest link. Export path is lossy and the official Obsidian importer is **personal-account only** [[3]](https://obsidian.md/help/import/onenote) |
| `Microsoft.OutlookForWindows` (new Outlook) | [Evolution](https://gitlab.gnome.org/GNOME/evolution) 3.60 with the "Microsoft 365" (Graph) account type [[5]](https://discourse.gnome.org/t/is-microsoft-365-graph-api-expected-to-be-available-in-evolution-3-60-x/36019); [Thunderbird](https://www.thunderbird.net/) 145+ for mail only [[10]](https://blog.thunderbird.net/2025/11/thunderbird-adds-native-microsoft-exchange-email-support/); OWA in a browser | ⚠ | New Outlook is Windows-only and Microsoft has announced nothing for Linux [[8]](https://office-watch.com/2026/microsoft-office-linux/). Pick by protocol, not by looks — EWS dies 1 Oct 2026 [[11]](https://www.computerworld.com/article/4129036/after-years-of-warnings-microsoft-is-finally-pulling-the-plug-on-ews.html) |
| `MSTeams` | Teams PWA (Edge/Chrome) [[12]](https://techcommunity.microsoft.com/blog/microsoftteamsblog/microsoft-teams-progressive-web-app-now-available-on-linux/3669846); [teams-for-linux](https://github.com/IsmaelMartinez/teams-for-linux) ⭐ 4.9k | ⚠ | "Teams is no longer supported on Linux" — Microsoft's own client matrix, updated 16 Jul 2026 [[4]](https://learn.microsoft.com/en-us/microsoftteams/teams-client-desktop-admin). Web is the supported path |
| `Microsoft Teams Meeting Add-in for Microsoft Office` 1.26 | none; schedule from Teams/OWA, or DavMail's CalDAV `online-meeting` [[13]](https://windowsforum.com/threads/davmail-6-8-adds-active-microsoft-graph-support-ready-for-ews-retirement.425710/) | ✗ | It's an Outlook-desktop COM add-in; there is no Outlook desktop on Linux [[8]](https://office-watch.com/2026/microsoft-office-linux/). Thunderbird cannot mark an invite as a Teams meeting on its own [[14]](https://support.mozilla.org/en-US/questions/1384944) |
| `Microsoft.MicrosoftOfficeHub` | `m365.cloud.microsoft` in any browser | ✓ | The Office app became the Microsoft 365 Copilot app; office.com/microsoft365.com redirect there [[15]](https://support.microsoft.com/en-us/microsoft-365-copilot/the-microsoft-365-app-transition-to-the-microsoft-365-copilot-app) |
| `Microsoft.Office.ActionsServer`, `Microsoft.OfficePushNotificationUtility` | — | ✓ | Windows-only plumbing for the Office/OneNote apps. Nothing to replace; they disappear with the suite |
| `Microsoft OneDrive` 26.123 + `Microsoft.OneDriveSync` | [abraunegg/onedrive](https://github.com/abraunegg/onedrive) ⭐ 12.7k; [rclone](https://rclone.org/onedrive/) ⭐ 59k; [onedriver](https://github.com/jstaf/onedriver) ⭐ 2.5k; Insync (paid) | ⚠ | Microsoft has never shipped a Linux client [[16]](https://www.expandrive.com/blog/onedrive-and-sharepoint-on-linux-in-2023). No files-on-demand in the OSS daemon [[1]](https://github.com/abraunegg/onedrive); budget full local disk |
| `Dropbox` 262.4 + `DropboxInc.Dropbox` | Official Dropbox for Linux | ✓ | ext4, zfs, xfs, btrfs and eCryptFS-on-ext4 are all supported now [[17]](https://help.dropbox.com/installs/system-requirements) — the 2018 ext4-only rule [[18]](https://itsfoss.com/dropbox-linux-ext4-only/) was rolled back in 2019 [[19]](https://linuxreviews.org/Dropbox_will_again_support_filesystems_beyond_ext4). ⚠ no ARM [[17]](https://help.dropbox.com/installs/system-requirements) |
| `LibreOffice 26.2.1.2` | same version, native | ✓ | 26.2 landed Feb 2026 with Excel-interop work [[20]](https://blog.documentfoundation.org/blog/2026/02/04/libreoffice-26-2-is-here/) |
| `Obsidian 1.11.5` | same version, native | ✓ | Official AppImage, .deb, snap, Flatpak, plus arm64 [[21]](https://obsidian.md/download) |
| `[Store] Claude` | Claude Desktop for Linux (beta) | ✓ | Shipped 30 Jun 2026 for Ubuntu 22.04+/Debian 12+; ⚠ no Computer Use, no dictation yet [[22]](https://www.omgubuntu.co.uk/2026/07/claude-desktop-linux-beta) |
| `Copilot` 150.0 + `Microsoft.Copilot` | browser, or the unofficial `copilot-desktop` snap | ⚠ | No official Microsoft Copilot desktop app for Linux; the snap is a community wrapper by Ken VanDine, last updated Feb 2026 [[23]](https://snapcraft.io/copilot-desktop) |

## Teams: the PWA is the supported path, and it is thinner

Microsoft's admin doc now lists Linux as ❌ "Teams is no longer supported on Linux", with Web as ✅ on Edge, Chrome, Firefox and Safari [[4]](https://learn.microsoft.com/en-us/microsoftteams/teams-client-desktop-admin). The PWA was announced as GA for Linux and is a feature of the web client, not a separate app [[12]](https://techcommunity.microsoft.com/blog/microsoftteamsblog/microsoft-teams-progressive-web-app-now-available-on-linux/3669846).

What actually breaks:

- **Screen sharing on Wayland** — needs the full stack: an xdg-desktop-portal backend for your compositor, PipeWire running, and the app pointed at the portal capture path [[24]](https://botmonster.com/self-hosting/wayland-screen-sharing-fix-video-calls-linux/). Concretely in 2026: on Ubuntu 26 + GNOME/Wayland, teams-for-linux's **snap** build fails ScreenCast ("Bind context provider failed") while the **.deb** works — snap confinement, not code [[25]](https://github.com/IsmaelMartinez/teams-for-linux/issues/2551). Community verdict: the PWA in Chrome/Edge behaves better than Electron wrappers for capture [[24]](https://botmonster.com/self-hosting/wayland-screen-sharing-fix-video-calls-linux/).
- **Background effects** — blur and the built-in set work; *uploading a custom* background is limited in the Linux PWA [[26]](https://learn.microsoft.com/en-us/answers/questions/4433162/upload-custom-background-using-web-or-pwa-on-linux), and Fedora users report background filters failing outright in the PWA [[27]](https://discussion.fedoraproject.org/t/microsoft-teams-pwa-background-filters-does-not-work/78500).
- **Notifications** — long-running Microsoft Q&A thread: silent notifications, toasts self-deleting after ~5 s, missing "meeting started" alerts [[28]](https://learn.microsoft.com/en-us/answers/questions/1116862/teams-pwa-notifications-on-linux). This is the single most-reported daily annoyance.
- **Meeting add-in** — gone. Schedule from Teams itself or OWA.

[teams-for-linux](https://github.com/IsmaelMartinez/teams-for-linux) ⭐ 4.9k (Jul 2026) buys back system notifications, tray with badges, custom backgrounds, screen sharing and multi-account profiles — but it is an Electron wrapper of the same web app, disables `contextIsolation` and sandboxing to reach the Teams DOM, and is explicitly unaffiliated with Microsoft [[29]](https://github.com/IsmaelMartinez/teams-for-linux). A first-hand 2026 report of a locked-down M365 org calls a Teams flatpak wrapper "*exactly* the same as on windows" in function [[2]](https://peterfalkingham.com/2026/03/04/office-365-and-linux-trying-to-use-linux-when-your-organization-is-all-in-and-locked-down-with-microsoft/).

## Outlook: choose by protocol, because EWS dies this October

The deadline dominates every other consideration. EWS is **disabled by default across Exchange Online tenants on 1 Oct 2026** and fully shut down 1 Apr 2027, with admin allow-lists needing to be created before end of August 2026 [[11]](https://www.computerworld.com/article/4129036/after-years-of-warnings-microsoft-is-finally-pulling-the-plug-on-ews.html)[[30]](https://techcommunity.microsoft.com/blog/exchange/retirement-of-exchange-web-services-in-exchange-online/3924440). Anything EWS-only is a client with a three-month shelf life.

| Client | Protocol to M365 | Mail | Calendar / contacts | Verdict |
|---|---|---|---|---|
| [Evolution](https://gitlab.gnome.org/GNOME/evolution) 3.60 + `evolution-ews` | **Graph** ("Microsoft 365" account type) and EWS | ✓ | ✓ | Best bet. Maintainer, 3 Jul 2026: preview status ended in the 3.52/3.56 era, "many main pain points had been fixed", ⚠ "feature parity is not complete" [[5]](https://discourse.gnome.org/t/is-microsoft-365-graph-api-expected-to-be-available-in-evolution-3-60-x/36019) |
| [Thunderbird](https://www.thunderbird.net/) 145+ | EWS shipped Nov 2025; Graph in progress | ✓ | ✗ | Exchange email is native and add-on-free [[10]](https://blog.thunderbird.net/2025/11/thunderbird-adds-native-microsoft-exchange-email-support/); Graph is "entering the final stretch toward feature parity", calendar only *planned* after that [[31]](https://blog.thunderbird.net/2026/06/thunderbird-monthly-development-digest-june-2026/)[[32]](https://roadmaps.thunderbird.net/en-US/desktop/) |
| Thunderbird + [OWL for Exchange](https://addons.thunderbird.net/en-us/thunderbird/addon/owl-for-exchange/) | EWS | ✓ | ✓ | €10/yr, syncs calendar + address book, MFA-aware [[33]](https://cylab.be/blog/463/use-thunderbird-to-fetch-your-outlook-365-emails); also surfaces Teams chat inside Thunderbird [[2]](https://peterfalkingham.com/2026/03/04/office-365-and-linux-trying-to-use-linux-when-your-organization-is-all-in-and-locked-down-with-microsoft/) |
| [Betterbird](https://www.betterbird.eu/) | inherits Thunderbird's | ⚠ | ⚠ | Stable line is still 140.13.0esr — *pre-EWS*. The 153 series exists but ships with "do not use this version in production yet" [[34]](https://www.betterbird.eu/) |
| [DavMail](https://github.com/mguessan/davmail) ⭐ 750 6.8 gateway | **Graph** or EWS → IMAP/CalDAV/LDAP | ✓ | ✓ | Graph mode now exposed in the GUI, OAuth2 mandatory so MFA/Conditional Access work, and it can auto-create Teams meetings via the CalDAV `online-meeting` setting [[13]](https://windowsforum.com/threads/davmail-6-8-adds-active-microsoft-graph-support-ready-for-ews-retirement.425710/) |
| Outlook on the web | — | ✓ | ✓ | Zero-risk fallback, officially supported in Firefox/Chrome on Linux [[8]](https://office-watch.com/2026/microsoft-office-linux/) |

One reassuring data point for third-party clients generally: Microsoft confirmed to the Thunderbird team that "approved mail clients such as Thunderbird will continue to be able to obtain user consent for permissions that were previously unavailable to third-party applications" [[31]](https://blog.thunderbird.net/2026/06/thunderbird-monthly-development-digest-june-2026/).

## OneNote: the one you should migrate off, not replace

There is no Linux client. Options, worst-to-best for a work tenant:

- **OneNote for the web** — the supported path. ⚠ local (non-cloud) notebooks are a desktop-only feature, so anything not synced to OneDrive/SharePoint has to be uploaded first [[35]](https://en.ittrip.xyz/microsoft-365/onenote-desktop-vs-web).
- **[P3X OneNote](https://github.com/patrikx3/onenote)** ⭐ 2.1k (Jul 2026) — an Electron wrapper around the same web app with locale auto-detection; still actively released in 2026 [[36]](https://github.com/patrikx3/onenote). Buys window/tray integration, not features.
- **Migrate to Obsidian** (already installed) via the official Importer — OAuth to Microsoft, notebooks → folders, pages → `.md`. ⚠ hard blocker: "Only notebooks owned by your personal account can be imported"; work/school accounts unsupported, locked sections invisible until unlocked [[3]](https://obsidian.md/help/import/onenote).
- **[onenote-md-exporter](https://github.com/alxnbl/onenote-md-exporter)** ⭐ 1.6k — the escape hatch for work notebooks: a Windows console app that drives OneNote → DOCX → Pandoc → Markdown, with Joplin and Obsidian output targets [[37]](https://github.com/alxnbl/onenote-md-exporter). **Run it before you wipe Windows** — it needs the OneNote desktop app you're about to delete.
- Known losses in any export: handwriting/ink, text tags, password-protected sections (skipped unless unlocked), and images nested in tables [[38]](https://www.file2markdown.ai/blog/onenote-to-markdown).

## OneDrive: four bad options, pick your poison

Microsoft "hasn't shipped one in 15 years and probably won't" [[16]](https://www.expandrive.com/blog/onedrive-and-sharepoint-on-linux-in-2023).

| Tool | Model | SharePoint / Teams libraries | Files-on-demand | Notes |
|---|---|---|---|---|
| [abraunegg/onedrive](https://github.com/abraunegg/onedrive) ⭐ 12.7k | sync daemon (bi-directional, or upload/download-only, `--dry-run`) | ✓ Business + SharePoint libraries + shared folders, multi-tenant Entra ID | ✗ explicitly in "what's missing" | CLI-only, no official GUI; runs on all major distros, FreeBSD/OpenBSD, Docker/Podman [[1]](https://github.com/abraunegg/onedrive) |
| [rclone](https://rclone.org/onedrive/) ⭐ 59k | on-demand copy/sync, or `mount` | ✓ | via VFS cache | ⚠ `mount` without `--vfs-cache-mode writes`/`full` breaks most apps (no random writes, no seek-on-read) [[39]](https://rclone.org/commands/rclone_mount/) |
| [onedriver](https://github.com/jstaf/onedriver) ⭐ 2.5k | FUSE filesystem, download-on-access | ⚠ limited SharePoint support [[16]](https://www.expandrive.com/blog/onedrive-and-sharepoint-on-linux-in-2023) | ✓ this is its whole point | Closest thing to Windows' behaviour; last commit Jan 2026 [[40]](https://github.com/jstaf/onedriver) |
| Insync (paid) | GUI sync | claims SharePoint + OneDrive for Business | ✗ | ⚠ conflicting evidence: Insync's own Linux page advertises OneDrive/ODB/SharePoint [[41]](https://www.insynchq.com/linux), while a competitor states "Insync used to, dropped support in 2024" [[16]](https://www.expandrive.com/blog/onedrive-and-sharepoint-on-linux-in-2023). Trial before paying |

**The real risk is not the tool, it's your tenant.** abraunegg's app registration shows as an unverified publisher and requests broad delegated scopes, which is exactly what admins block [[42]](https://github.com/abraunegg/onedrive/issues/2191). A March 2026 first-hand account: OneDrive sync "remained the major pain point — native Linux clients lack files-on-demand, and the organization blocked both popular open-source solutions from signing in" [[2]](https://peterfalkingham.com/2026/03/04/office-365-and-linux-trying-to-use-linux-when-your-organization-is-all-in-and-locked-down-with-microsoft/). Mitigations that exist in the client: Intune SSO via the Microsoft Identity Device Broker D-Bus interface, and the OAuth2 device authorisation flow for Entra ID [[43]](https://github.com/abraunegg/onedrive/blob/master/docs/usage.md). Test sign-in on day one, before you commit.

Dropbox, by contrast, is boring in the good way: official client, Ubuntu 18.04+/Fedora 28+, ext4/zfs/xfs/btrfs/eCryptFS-on-ext4, 64-bit only, no ARM [[17]](https://help.dropbox.com/installs/system-requirements).

## Office file fidelity: three tiers, and two sharp edges

| Engine | .docx/.xlsx/.pptx round-trip | VBA | Power Query |
|---|---|---|---|
| **Office for the web** | reference-perfect (it *is* Office) | ✗ "Macros do not run in a browser window"; ActiveX/form controls don't render; IRM-protected or digitally-signed workbooks won't open at all [[44]](https://support.microsoft.com/en-us/office/differences-between-using-a-workbook-in-the-browser-and-in-excel-f0dc28ed-b85d-4e1d-be6d-5878005db3b6) | ✓ full editor since Jan 2026 — view/refresh for all M365 subs, authoring for Business/Enterprise plans [[6]](https://support.microsoft.com/en-us/office/use-power-query-in-excel-for-the-web-02652946-de70-48d8-8a34-3db96998ff5a); ⚠ desktop still wins on local-file sources, the full connector library and heavy M work [[7]](https://www.acuitytraining.co.uk/news-tips/power-query-in-excel-for-the-web-whats-changed/) |
| **[ONLYOFFICE Desktop Editors](https://github.com/ONLYOFFICE/DesktopEditors)** ⭐ 5.1k | best offline OOXML fidelity — OOXML is its internal format, so .docx/.xlsx/.pptx aren't a conversion | ✗ macros are sandboxed **JavaScript** against the Document Builder API; VBA is not supported by design [[9]](https://api.onlyoffice.com/docs/macros/guides/getting-started/)[[45]](https://www.onlyoffice.com/blog/2026/02/macros-or-ai-functions-understanding-onlyoffice-tools) | ✗ |
| **LibreOffice 26.2** | good and improving: Excel 2010–365 is now the default XLSX export target, BIFF12 clipboard removes paste size limits, floating-table DOCX interop, partial OOXML chart-style round-trip [[46]](https://www.omgubuntu.co.uk/2026/02/libreoffice-26-2-new-features)[[20]](https://blog.documentfoundation.org/blog/2026/02/04/libreoffice-26-2-is-here/) | ⚠ partial: "Support for VBA is not complete, but it covers a large portion of the common usage patterns"; needs Tools ▸ Options ▸ Load/Save ▸ VBA Properties ▸ *Executable code*, and you "may have to edit the VBA code and complete the missing support with LibreOffice Basic" [[47]](https://help.libreoffice.org/latest/en-US/text/sbasic/shared/vbasupport.html) | ✗ |

Office Watch's 2026 verdict on the open-source suites is the honest one: fine for everyday documents, but "once you start dealing with complex Word layouts, large Excel models or macro-heavy files, compatibility gaps become obvious" [[8]](https://office-watch.com/2026/microsoft-office-linux/). Practical split: **ONLYOFFICE for files you exchange with Windows colleagues, LibreOffice for your own work, the web app whenever a document must come back byte-faithful.**

Two sharp edges, restated: **VBA does not survive anywhere on Linux** (partially in LibreOffice, not at all in ONLYOFFICE or the browser), and **Power Query authoring is now a web/licence question rather than a platform one** — that edge got much duller in January 2026.

## The locale angle

Your Office install is four-locale (en-us, nl-nl, de-de, fr-fr for OneNote). Nothing here is lost: LibreOffice UI and dictionaries are per-package (`libreoffice-l10n-nl`, `-fr`, `-de` on Debian/Ubuntu, `libreoffice-langpack-*` on Fedora), switchable at Tools ▸ Options ▸ Language Settings ▸ Languages [[48]](https://www.libreofficehelp.com/install-language-packs-libreoffice/). P3X OneNote added an "Auto (system)" language option for locale detection in 2026 [[36]](https://github.com/patrikx3/onenote). Office for the web follows your account language, not the OS. What you *do* lose is having four locales resident at once with per-document proofing switching — on Linux that's one UI language plus N dictionaries.

## What still argues for a Windows VM

Only three things from this angle: OneNote **export** (run onenote-md-exporter before wiping [[37]](https://github.com/alxnbl/onenote-md-exporter)), VBA-heavy workbooks, and the Teams Meeting add-in workflow if your calendar habits are built on it. None of them is a daily driver. Note the honest counter-view: Office Watch rates a Windows VM the "best for power users" option precisely because feature parity is otherwise unattainable, at the cost of a licence and the resources [[8]](https://office-watch.com/2026/microsoft-office-linux/).
