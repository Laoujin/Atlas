---
layout: expedition
title: "Throwing away Windows: a replacement plan for an actual installed-software inventory"
date: 2026-07-30
topic: "Windows to Linux replacement plan for a real installed-software inventory (2026): what ports directly, what needs a substitute, and what has no answer."
format: md
tags: [linux-migration, windows, dotnet, kde-plasma, microsoft-365]
summary: "Seven angles over the 185 programs actually installed on this Legion: the desktop-environment choice is the real decision, the expected blockers (VPN, anti-cheat) are not blockers, and what genuinely breaks is administration tooling and shell integration."
cover: cover.svg
synthesis: true
citations: 15
reading_time_min: 4
children:
  - slug: net-sql-server-dev-stack-on-linux
    title: "Your .NET + SQL Server stack on Linux: what actually replaces what"
    depth: expedition
    status: success
    summary: "Rider replaces Visual Studio + ReSharper on Linux at the cost of the WinForms/WPF designers; SQL Server itself moves cleanly to a container, but SSMS has no Linux successor now that Azure Data Studio is dead."
    citations: 80
    reading_time_min: 13
  - slug: microsoft-365-onenote-outlook-teams-onedrive-on-linux
    title: "Microsoft 365 on Linux in 2026: what you actually lose"
    depth: survey
    status: success
    summary: "Office, Teams and mail are a tolerable compromise on Linux in 2026; OneDrive sync and OneNote are the two places where the gap is real."
    citations: 48
    reading_time_min: 11
  - slug: windows-only-power-user-utilities
    title: "The utility belt: per-tool Linux verdicts for a Windows power user (2026)"
    depth: survey
    status: success
    summary: "Per-tool verdicts for the Windows-only utilities in an actual installed-software inventory: most transfer cleanly, AutoHotkey and Power Automate Desktop have no single answer, and Wayland is the variable that decides the rest."
    citations: 32
    reading_time_min: 15
  - slug: multi-monitor-window-management-desktop-shell
    title: "Multi-monitor, window management and the desktop shell: replacing DisplayFusion, Fences, FancyZones and X-Rite on Linux"
    depth: survey
    status: success
    summary: "KDE Plasma 6.7 is the only Linux desktop that replaces most of DisplayFusion and FancyZones natively; Fences has no real equivalent and the X-Rite workflow becomes ArgyllCMS/DisplayCAL plus a per-screen ICC profile."
    citations: 52
    reading_time_min: 11
  - slug: gaming-steam-proton-epic-paradox-and-the-anti-cheat-wall
    title: "Gaming after the switch: your library survives, the NVIDIA App does not"
    depth: survey
    status: success
    summary: "Both installed games run under Proton — Planetfall is Gold/Deck-Playable and Fall Guys' EAC is Linux-enabled — so the only hard loss is the NVIDIA App and Game Bar tooling layer, which becomes environment variables plus MangoHud and GPU Screen Recorder."
    citations: 38
    reading_time_min: 10
  - slug: hardware-peripherals-corporate-vpn-clients
    title: "Legion hardware, peripherals and the two corporate VPNs on Linux"
    depth: recon
    status: success
    summary: "Neither corporate VPN blocks the switch — Harmony SASE ships an official Linux agent and WatchGuard is reachable with plain OpenVPN; the real losses are QuantumENGINE, Dolby, XTU and Lenovo's AI/Space bloat."
    citations: 19
    reading_time_min: 5
  - slug: escape-hatches-for-the-irreplaceable
    title: "Escape hatches for the leftovers: Wine, a VM, passthrough, or just keep the partition"
    depth: recon
    status: success
    summary: "Wine for single-window utilities, a local Windows VM for Visual Studio and SSMS, RDP for the corporate cluster — and no GPU passthrough on a muxless Legion."
    citations: 16
    reading_time_min: 4
model: "Opus 5"
cost_usd: "sub"
issue: 13
duration_sec: 1236
---

Seven angles over the 185 programs actually installed on this machine converge on one thing the per-app tables don't show: **the decision is the desktop environment, not the applications.** Two angles reached KDE Plasma independently and for unrelated reasons. Plasma 6.7 is the only shell with native per-monitor panels, per-screen wallpaper, arbitrary fractional scaling and per-screen ICC profiles — it even shipped per-screen virtual desktops after a 21-year-old request, beating Windows outright [[1]](https://kde.org/announcements/plasma/6/6.7.0/). Separately, the automation angle landed on KDE or GNOME because global hotkeys and clipboard monitoring now route through xdg-desktop-portal, and wlroots-based compositors implement that unevenly [[2]](https://copyq.readthedocs.io/en/latest/known-issues.html). And this must be a Wayland migration, not a soft landing on X11: GNOME 50 removed the X11 session in March 2026 [[3]](https://www.theregister.com/2026/03/19/gnome_50/) and Plasma 6.8 removes it in October [[4]](https://9to5linux.com/kde-plasma-6-8-desktop-environment-to-drop-the-x11-session-and-go-wayland-only).

**Both expected blockers evaporated.** The corporate VPNs are fine — Harmony SASE ships a first-party Linux agent [[5]](https://sc1.checkpoint.com/documents/Infinity_Portal/WebAdminGuides/EN/SASE-Admin-Guide/Content/Topics-SASE-AG/Devices/Download.htm) and WatchGuard itself documents connecting via a stock OpenVPN client with the Firebox profile [[6]](https://www.watchguard.com/help/docs/help-center/en-US/content/en-US/Fireware/mvpn/ssl/mvpn_ssl_ovpn_profile_c.html). The anti-cheat wall isn't in this library: Fall Guys is recorded as *Works* [[7]](https://www.gamingonlinux.com/anticheat/) and Planetfall is Deck-Playable [[8]](https://store.steampowered.com/app/718850/Age_of_Wonders_Planetfall/). Two angles corrected that premise independently.

**What breaks is administration and shell integration, not applications.** Every *authoring* tool has a Linux answer; the *administration* tools don't. Azure Data Studio retired on 28 Feb 2026 and Microsoft's own guidance is "keep SSMS for SQL Server Agent" — a Windows-only instruction [[9]](https://learn.microsoft.com/en-us/sql/tools/whats-happening-azure-data-studio?view=sql-server-ver17). Teams is likewise "not supported" with the web client as the sanctioned route [[10]](https://learn.microsoft.com/en-us/microsoftteams/teams-client-desktop-admin). The harder class is shell integration — Fences, DisplayFusion, AutoHotkey, ShareX, Ditto — where Wine offers *no* hatch at all, because there is no host Windows desktop to hook. Native replacement or drop; there is no third option.

**Three items are ordered, not optional, and they happen before the wipe.** OneNote extraction requires the OneNote desktop app to be running [[11]](https://github.com/alxnbl/onenote-md-exporter) ⭐ 1.6k (Jul 2026); the WatchGuard `.ovpn` profile must be exported from Windows; the Dolby DAX3 tuning XML must be dumped if the speaker EQ is to survive. An external clock compounds this: EWS is disabled by default in Exchange Online on 1 Oct 2026, so landing on an EWS-only mail client buys three months [[12]](https://www.computerworld.com/article/4129036/after-years-of-warnings-microsoft-is-finally-pulling-the-plug-on-ews.html) — Evolution 3.60's native Microsoft 365 Graph account type is the destination, not Thunderbird's EWS support [[13]](https://discourse.gnome.org/t/is-microsoft-365-graph-api-expected-to-be-available-in-evolution-3-60-x/36019).

⚠ One unresolved hardware risk gates everything above. On Legion laptops all external outputs are wired to the dGPU, and hybrid-mode Wayland with a dGPU-attached external display has a long tail of blank-screen reports [[14]](https://forums.developer.nvidia.com/t/ryzen-7-gtx-1660ti-blank-screen-on-external-outputs-in-hybrid-graphics-mode/157800). Live-boot Plasma 6.7 with the monitor attached and test all three BIOS graphics modes before committing — and note the fallback most people reach for is closed off here, since muxless Optimus passthrough caps a guest at 640×480 and NVIDIA refuses to form Optimus against a virtual iGPU [[15]](https://lantian.pub/en/article/modify-computer/laptop-intel-nvidia-optimus-passthrough.lantian/).

Which leaves the sharpest open question: if the honest plan keeps a Windows partition for SSMS's Agent tooling, the WinForms designers and the firmware utilities, is that a migration — or a slow dual-boot that quietly becomes permanent?
