---
title: "Picking a Linux desktop in 2026: the Windows 11 switcher's decision guide"
date: 2026-07-30
depth: survey
format: md
topic: "Which Linux desktop environment to pick in 2026, for a Windows user switching to Linux. Compare GNOME (46+/47+/48+ era), KDE Plasma 6.x, Cinnamon, XFCE, and the tiling options (Hyprland, Sway, Niri, COSMIC) on: how familiar each feels coming from Windows 11, window management and workflow ergonomics, Wayland vs X11 status in 2026 and what still breaks on Wayland (screen sharing in Teams/Slack/Zoom, remote desktop, global hotkeys, clipboard managers, NVIDIA specifics), multi-monitor and mixed-DPI setups including fractional scaling, extension/customisation model and how fragile it is across upgrades (GNOME extensions breaking on major releases vs KDE's built-in options), resource use, and touchpad/gesture quality on laptops. Also cover which distros ship which DE as their best-supported flagship, because DE quality is often distro-specific rather than upstream. Deliverable: a comparison table plus a recommendation, and an explicit statement of which DE choices are reversible versus which effectively pick your distro for you."
topic_raw: "I'm going to make the switch to Linux. The question is which Linux version should I pick? there are so many :D"
tags: [linux, desktop-environment, kde-plasma, gnome, wayland, windows-migration, cinnamon, tiling-wm]
summary: "KDE Plasma is the lowest-friction landing spot for a Windows 11 developer in 2026; X11 sessions die this year, so the real choice is which Wayland compositor's rough edges you can live with."
citations: 44
reading_time_min: 12
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 745
issue: 11
---

> **Decision.** Install **[KDE Plasma](https://kde.org/plasma-desktop/) 6.7**. It is the only major desktop where Windows muscle memory, working global hotkeys, non-blurry scaling of legacy X11 apps and sane mixed-DPI multi-monitor all land in the same session today [[1]](https://kde.org/announcements/plasma/6/6.7.0/) [[2]](https://github.com/flatpak/xdg-desktop-portal/discussions/1368), and its customisation lives in the settings app rather than in third-party extensions that de-activate on every major upgrade [[3]](https://discourse.gnome.org/t/gnome-50-extension-review-status/34569). Take **[Cinnamon](https://projects.linuxmint.com/cinnamon/) on [Linux Mint](https://linuxmint.com/)** instead if "nothing moves under me" beats features — it is the last mainstream desktop that will still offer an X11 session in 2027 [[4]](https://www.omgubuntu.co.uk/2026/07/linux-mint-wayland-fully-supported) [[5]](https://linuxiac.com/kde-plasma-6-8-will-go-fully-wayland-ending-nearly-30-years-of-x11-sessions/). Take **[GNOME](https://www.gnome.org/)** only if you intend to adopt its keyboard-driven workflow wholesale rather than bolt Windows back onto it. Leave tiling compositors for a second session you add in month three.

## What actually changed in 2026: the X11 escape hatch closed

Every "just use X11 if Wayland breaks something" answer from 2024 is dead advice. This is the single most important fact for a switcher, because it means you can no longer defer the Wayland question.

| Desktop | X11 session in 2026 | Notes |
|---|---|---|
| GNOME 50 | ✗ gone | X11 session code removed outright (~27,540 lines cut from Mutter); you cannot log into an X11 GNOME session even if you install Xorg by hand [[6]](https://www.xda-developers.com/x11-on-gnome-is-finally-dead-as-its-newest-version-goes-all-in-on-wayland/) |
| KDE Plasma 6.7 | ✓ last one | Plasma 6.8 (due 14 Oct 2026) drops the X11 session; X11-specific code leaves Plasma Shell and System Settings too. Maintained only until early 2027 [[5]](https://linuxiac.com/kde-plasma-6-8-will-go-fully-wayland-ending-nearly-30-years-of-x11-sessions/) |
| Cinnamon | ✓ staying | Wayland loses "experimental" status in the next release and **both** sessions stay fully supported; Mint has not committed to making Wayland the default [[4]](https://www.omgubuntu.co.uk/2026/07/linux-mint-wayland-fully-supported) [[7]](https://www.phoronix.com/news/LinuxMint-Cinnamon-Wayland-Good) |
| XFCE 4.20 | ✓ staying | Its Wayland compositor `xfwl4` only hit first preview on 22 Jun 2026; X11 feature parity is explicitly *not* a goal for 4.22 [[8]](https://linuxiac.com/xfce-wayland-compositor-gets-its-first-preview-release/) [[9]](https://wiki.xfce.org/releng/wayland_roadmap) |
| COSMIC 1.x | ✗ never had one | Wayland-only by design [[10]](https://en.wikipedia.org/wiki/COSMIC_desktop) |
| Hyprland / Sway / niri | ✗ Wayland-only | — |

X11 *applications* keep working everywhere through XWayland — what disappears is the option to run your whole desktop on X11 [[6]](https://www.xda-developers.com/x11-on-gnome-is-finally-dead-as-its-newest-version-goes-all-in-on-wayland/). Distro-side, Ubuntu 26.04 LTS shipped Wayland-only GNOME in April 2026 [[11]](https://www.xda-developers.com/ubuntu-2604-is-the-first-lts-that-feels-like-it-chose-the-future-instead-of-hedging-its-bets/) [[12]](https://discourse.ubuntu.com/t/i-need-some-advice-now-that-ubuntu-is-dropping-support-for-x11-in-26-04/77161).

The reassuring number: KDE's own telemetry puts **over 95% of Plasma 6.6 users on Wayland** [[13]](https://www.phoronix.com/news/KDE-Plasma-Wayland-Ex-X11). Wayland is not the risky choice any more; it is the only choice, and it mostly works.

## Master comparison

| Desktop | Feels like Windows 11? | Wayland maturity | Customisation model | Fragile across upgrades? | Idle RAM (relative) | Touchpad gestures |
|---|---|---|---|---|---|---|
| **[KDE Plasma](https://kde.org/plasma-desktop/) 6.7** | ✓ closest — taskbar + start menu + system tray by default, and the tweaks that close the gap are all in System Settings [[14]](https://www.makeuseof.com/kde-plasma-is-linux-desktop-recommend-to-windows-users-after-tweaks/) | Best-in-class: HDR + ICC simultaneously, per-screen virtual desktops, non-blurry XWayland scaling [[1]](https://kde.org/announcements/plasma/6/6.7.0/) | Built-in. Settings app, widgets, KWin scripts | Low — features are first-party, not third-party plugins | Highest of the four mainstream DEs [[15]](https://linuxblog.io/10-best-linux-desktop-environments/) | Configurable 3/4-finger bindings in System Settings [[16]](https://community.kde.org/KDE_Visual_Design_Group/Gestures) |
| **[GNOME](https://www.gnome.org/) 50** | ✗ different paradigm — Activities overview, no taskbar, workspace-centric | Very good; fractional scaling and VRR now on by default, NVIDIA stutter fixes [[17]](https://release.gnome.org/50/) | Extensions (third-party JS) for anything off-rails | ⚠ **High** — see below | Middle [[15]](https://linuxblog.io/10-best-linux-desktop-environments/) | Best out-of-box 3-finger workspace swipe on Wayland, no config needed [[18]](https://linuxjunkies.org/guides/configure-the-touchpad-and-gestures) |
| **[Cinnamon](https://projects.linuxmint.com/cinnamon/) 6.x** ⭐ 5.5k | ✓ very — closer to Windows 7/10 than 11, but zero surprises | Newly non-experimental; multi-monitor, HiDPI, hardware accel just landed [[7]](https://www.phoronix.com/news/LinuxMint-Cinnamon-Wayland-Good) [[19]](https://9to5linux.com/linux-mints-cinnamon-6-8-desktop-environment-will-fully-support-wayland) | Applets/desklets + settings; conservative | Low | Between XFCE and GNOME [[15]](https://linuxblog.io/10-best-linux-desktop-environments/) | Weakest of the mainstream four |
| **[XFCE](https://xfce.org/) 4.20** | ~ configurable into a Windows-ish panel layout, but visibly dated | ⚠ Immature — compositor in alpha, no HDR/VRR [[8]](https://linuxiac.com/xfce-wayland-compositor-gets-its-first-preview-release/) [[20]](https://eylenburg.github.io/de_comparison.htm) | Panel plugins + settings | Very low (glacial release pace) | Lowest [[15]](https://linuxblog.io/10-best-linux-desktop-environments/) | Poor |
| **[COSMIC](https://system76.com/cosmic/) 1.x** ⭐ 6.5k | ✗ its own thing — dock + optional tiling per workspace | Wayland-native; NVIDIA explicit-sync and XWayland fractional-scaling rough edges cleaned up in 1.0.x [[10]](https://en.wikipedia.org/wiki/COSMIC_desktop) | Built-in settings, Rust, young ecosystem | Unknown — one release old | n/a | n/a |
| **[niri](https://github.com/niri-wm/niri)** ⭐ 26k / **[Hyprland](https://hypr.land/)** ⭐ 38k / **[Sway](https://swaywm.org/)** ⭐ 17k | ✗✗ no start menu, no taskbar, config is a text file | Compositor-dependent; wlroots stack lags on portals [[21]](https://michael.stapelberg.ch/posts/2026-01-04-wayland-sway-in-2026/) | Config files. Total control, nothing pre-wired | Config churn is on you (Hyprland fastest-moving) [[22]](https://www.makeuseof.com/i-used-hyprland-niri-i3-and-sway-one-of-them-clearly-won-me-over/) | Lowest of all | niri's scroll-strip is gesture-native [[23]](https://gvolpe.com/blog/niri/) |

On RAM, treat the ordering as reliable and the magnitudes as noise: a 2026 round-up puts XFCE ~1.36 GB, Cinnamon ~1.89 GB, GNOME ~2.10 GB, Plasma ~2.67 GB of total system usage [[15]](https://linuxblog.io/10-best-linux-desktop-environments/), while a per-DE measurement that subtracts base-system overhead puts all four within ~60 MB of each other [[20]](https://eylenburg.github.io/de_comparison.htm). Different methodologies, same ranking. On a dev machine with 16 GB+, this axis should not decide anything.

## What still breaks on Wayland in 2026 — and where

This is the section that matters for a working developer. The failures are compositor-specific, which is exactly why the DE choice is a Wayland-bug choice.

| Thing | Status | Detail |
|---|---|---|
| **Screen sharing (Teams/Slack/Zoom)** | ⚠ works, with sharp edges | Chromium 110+ and Firefox 130+ do PipeWire capture via the portal by default; Electron apps like Slack may need `--enable-features=WebRTCPipeWireCapturer` and show a redundant duplicate picker [[24]](https://github.com/electron/electron/issues/30652). Zoom's long-standing bug: the *first* share works, the second gives a black screen [[25]](https://community.zoom.com/meetings-2/sharing-in-wayland-works-only-the-first-time-18287). Teams as a browser PWA beats the native client here. |
| **Sharing a single window** | ⚠ compositor-dependent | Works on Plasma and GNOME; on Sway the whole monitor shows up as one shareable "window" [[21]](https://michael.stapelberg.ch/posts/2026-01-04-wayland-sway-in-2026/) |
| **Global hotkeys** (push-to-talk, clipboard tools, screenshot utilities) | ⚠ **KDE only, effectively** | Wayland forbids apps from grabbing keys directly; the replacement is the `org.freedesktop.portal.GlobalShortcuts` portal, and KDE is the only desktop with a working backend. GNOME 50 has no functional GlobalShortcuts backend; `xdg-desktop-portal-wlr` ships none at all [[2]](https://github.com/flatpak/xdg-desktop-portal/discussions/1368) [[26]](https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html) |
| **Clipboard managers** | ⚠ needs a Wayland-native tool | Generic managers can't watch the clipboard while unfocused — they only see changes from XWayland windows or when focused [[27]](https://biggo.com/news/202508230115_Clyp_Wayland_Support_Issues). Use compositor-aware tools: Plasma's built-in Klipper, or [cliphist](https://github.com/sentriz/cliphist) ⭐ 1.5k on wlroots stacks |
| **Remote desktop into the box** | ✓ GNOME wins | GNOME Remote Desktop does RDP *and* headless / pre-login remote login via GDM. KDE's KRDP shares an already-logged-in session only, with no headless support and no immediate plans, because SDDM can't do it yet [[28]](https://forum.manjaro.org/t/remote-desktop-options-for-headless-kde-plasma-on-wayland/183945). GNOME 50 added Vulkan/VA-API acceleration, HiDPI-aware scaling and Kerberos auth to it [[17]](https://release.gnome.org/50/) |
| **NVIDIA** | ⚠ the real risk factor | Explicit sync needs driver 555.58+, XWayland 24.1+ and KWin 6.1+ [[29]](https://www.phoronix.com/news/KDE-KWin-Lands-Explicit-Sync); even on the 580 series users report Plasma Wayland freezes and fd leaks [[30]](https://forums.developer.nvidia.com/t/nvidia-580-on-kde-wayland-freezes/355175). HN consensus in 2026: Wayland on AMD or Intel is a non-event, NVIDIA is where the remaining stories come from [[31]](https://news.ycombinator.com/item?id=46485989) |
| **Odd corners** | ⚠ | Wine apps get pointer-location bugs on multi-display setups; Chrome's GPU process can die after a resize on Sway; DisplayPort MST tiled monitors show up as two screens under wlroots [[21]](https://michael.stapelberg.ch/posts/2026-01-04-wayland-sway-in-2026/) [[31]](https://news.ycombinator.com/item?id=46485989) |

## Multi-monitor and mixed DPI

If you run a 4K panel next to a 1080p panel — the classic dev-desk setup — this axis alone justifies picking KDE.

- **KDE Plasma:** per-display fractional scaling with a free-form slider, no flags. Plasma 6.3 reworked fractional scaling to snap UI elements to the pixel grid; 6.4 stopped auto-selecting blurry "almost-1x" factors; 6.6.4 was still cleaning up fractional-scaling shadow/tooltip regressions [[32]](https://linuxiac.com/kde-plasma-6-6-4-released-with-wayland-kwin-and-spectacle-fixes/). Plasma 6.7 implements the experimental `xx-fractional-scale-v2` protocol for pixel-exact positioning so windows stop leaving hairline gaps on HiDPI [[33]](https://www.neowin.net/news/kde-is-getting-support-for-the-xx-fractional-scale-v2-wayland-protocol/). Crucially, KDE scales XWayland apps natively instead of rendering-then-stretching, so your legacy X11 tools aren't blurry.
- **GNOME 50:** fractional scaling is finally **on by default** (125%, 150%, …), plus VRR by default and low-latency cursor during VRR [[17]](https://release.gnome.org/50/). Before 50 this needed an experimental feature flag.
- **Cinnamon:** full HiDPI and improved multi-monitor arrived only with the current Wayland work [[19]](https://9to5linux.com/linux-mints-cinnamon-6-8-desktop-environment-will-fully-support-wayland).
- **XFCE:** no HDR, no VRR [[20]](https://eylenburg.github.io/de_comparison.htm).
- **wlroots compositors (Sway):** no XWayland scaling — every X11 app is blurry on a fractionally-scaled output [[21]](https://michael.stapelberg.ch/posts/2026-01-04-wayland-sway-in-2026/).

## Customisation fragility: the GNOME extension tax

This is not a theoretical concern and it is the strongest single argument against GNOME for someone who wants a Windows-shaped desktop.

GNOME's shell has no built-in taskbar, no built-in tray, no built-in dock-with-window-buttons. Getting those means extensions — and extensions are third-party JavaScript pinned to a shell version. On the GNOME 50 upgrade, popular system extensions including dash-to-dock and appindicator support were simply deactivated because they hadn't been updated [[34]](https://github.com/ublue-os/bluefin/issues/4561) ⭐ 2.6k. Zorin users hit a shell update on 1 Jul 2026 that left every system extension stuck in `INITIALIZED` with `canChange=false` [[35]](https://forum.zorin.com/t/all-system-extensions-broken-after-gnome-shell-update-on-2026-07-01/65996).

The structural problem is worse than "developers are slow". Extension review on extensions.gnome.org runs through **one person**: in spring 2026 that reviewer lost reliable internet access for geopolitical reasons and the queue climbed to nearly 500 pending submissions, many of them one-line `metadata.json` bumps to declare GNOME 50 compatibility [[3]](https://discourse.gnome.org/t/gnome-50-extension-review-status/34569).

KDE's equivalent features — panels, taskbar variants, tray, per-screen virtual desktops, window rules, gesture bindings — ship in the product and are release-tested with it [[1]](https://kde.org/announcements/plasma/6/6.7.0/) [[36]](https://kde.org/announcements/plasma/6/6.6.0/). You still pay for customisation, just in configuration time rather than in upgrade roulette.

## Tiling: not your first login

All four tiling options are Wayland-only and none of them hands you a discoverable desktop. As a Windows switcher you'd be relearning window management, the panel, the launcher, notifications and the display config in one week.

- **[niri](https://github.com/niri-wm/niri) ⭐ 26k** — scrollable tiling: one infinite horizontal strip per workspace instead of a split grid. Best fit for laptop-first work and the friendliest of the three to reason about, at the cost of an unfamiliar mental model and a smaller dotfiles ecosystem [[22]](https://www.makeuseof.com/i-used-hyprland-niri-i3-and-sway-one-of-them-clearly-won-me-over/) [[23]](https://gvolpe.com/blog/niri/).
- **[Hyprland](https://hypr.land) ⭐ 38k** — dynamic tiling with animations, blur, rounded corners. Most popular, fastest churn, occasional rough edges [[22]](https://www.makeuseof.com/i-used-hyprland-niri-i3-and-sway-one-of-them-clearly-won-me-over/).
- **[Sway](https://swaywm.org) ⭐ 17k** — i3 semantics on Wayland; rock-solid and lowest overhead, but the wlroots portal stack is where the 2026 gaps concentrate (no GlobalShortcuts backend, no XWayland scaling, single-window sharing broken) [[2]](https://github.com/flatpak/xdg-desktop-portal/discussions/1368) [[21]](https://michael.stapelberg.ch/posts/2026-01-04-wayland-sway-in-2026/).
- **[COSMIC](https://github.com/pop-os/cosmic-epoch) ⭐ 6.5k** — the middle path: a complete Rust desktop with optional per-workspace tiling, visual placement hints and persistent layouts, so you get tiling without giving up a panel and a settings app [[10]](https://en.wikipedia.org/wiki/COSMIC_desktop).

KDE also does tiling: KWin has built-in custom tile layouts and edge-snap zones, which covers most of what a Windows FancyZones user actually wanted.

## Distro × desktop: where each DE is a first-class citizen

DE quality really is distro-specific — the same Plasma release can be pristine or patched-to-taste depending on who packaged it.

| Desktop | Best-supported homes | Notes |
|---|---|---|
| KDE Plasma | [Fedora KDE](https://fedoraproject.org/kde/) (a full **flagship edition** since Fedora 42, shipping Plasma 6.6.4 in Fedora 44) [[37]](https://www.helpnetsecurity.com/2026/04/29/fedora-linux-44-released/) [[38]](https://fedoramagazine.org/whats-new-in-fedora-kde-plasma-desktop-44/); [KDE neon](https://neon.kde.org/) (KDE's own, newest Plasma on Ubuntu LTS); [Kubuntu](https://kubuntu.org/) (LTS cadence); openSUSE Tumbleweed; EndeavourOS [[39]](https://www.tecmint.com/kde-plasma-linux-distros/) | Fedora KDE is the "vanilla Plasma, current, still tested" pick |
| GNOME | [Ubuntu](https://ubuntu.com/) 26.04 LTS (Wayland-only) [[11]](https://www.xda-developers.com/ubuntu-2604-is-the-first-lts-that-feels-like-it-chose-the-future-instead-of-hedging-its-bets/); [Fedora Workstation](https://fedoraproject.org/workstation/) 44 with GNOME 50 [[37]](https://www.helpnetsecurity.com/2026/04/29/fedora-linux-44-released/) | Fedora ships GNOME closest to upstream; Ubuntu patches it |
| Cinnamon | **[Linux Mint](https://linuxmint.com/) only, really** — Mint develops it [[40]](https://github.com/linuxmint/cinnamon) | Mint 23, due end of 2026, is the release with full Wayland [[4]](https://www.omgubuntu.co.uk/2026/07/linux-mint-wayland-fully-supported) |
| XFCE | Xubuntu, Debian XFCE, [Zorin OS](https://zorin.com/os/) Lite, MX Linux | The choice for old hardware, not for a 2026 dev laptop |
| COSMIC | [Pop!_OS](https://pop.system76.com/) 24.04 LTS (upstream, shipped COSMIC 1.0 on 11 Dec 2025) [[10]](https://en.wikipedia.org/wiki/COSMIC_desktop); now also an official [Fedora COSMIC spin](https://fedoraproject.org/spins/cosmic/) [[41]](https://fedoraproject.org/spins/cosmic/), plus Arch, CachyOS, openSUSE TW, NixOS packages [[42]](https://www.xda-developers.com/linux-distro-cosmic/) | The distro lock-in here is weakening fast |
| Zorin desktop | [Zorin OS](https://zorin.com/os/) 18.1 only | A GNOME fork with Windows-7/10-style layouts, Wine/Bottles pre-wired and a Windows migration tool; ~1M downloads in five weeks, 78% from Windows machines [[43]](https://allthingsopen.org/articles/zorin-os-18-review-linux-distro-windows-users) [[44]](https://en.wikipedia.org/wiki/Zorin_OS) |

## Reversible vs. distro-locking — say it plainly

**Reversible (a package install and a session picker at login):** GNOME, KDE Plasma, XFCE, Sway, Hyprland, niri on Fedora, Ubuntu/Debian, Arch and openSUSE. You install the second desktop, log out, choose it from the greeter, and switch back if you hate it. ⚠ The cost is clutter, not risk: installing both GNOME and Plasma pulls in two app stacks and two sets of settings daemons, and your app menu doubles in size.

**Effectively picks your distro (a reinstall to change your mind):**

- **Cinnamon → Linux Mint.** Mint is Cinnamon's upstream [[40]](https://github.com/linuxmint/cinnamon); other packagings exist but Mint is where it's designed, tested and shipped.
- **Zorin's desktop → Zorin OS.** The layouts are the product; there is no other home for them [[44]](https://en.wikipedia.org/wiki/Zorin_OS).
- **COSMIC → Pop!_OS, softening.** Still System76's home turf, but Fedora's official spin plus Arch/openSUSE/NixOS packages make this the weakest lock-in on the list [[41]](https://fedoraproject.org/spins/cosmic/) [[42]](https://www.xda-developers.com/linux-distro-cosmic/).
- **"I need a real X11 session" → Mint or an XFCE distro.** This is the sneaky one. It isn't a desktop preference, it's a distro constraint, because GNOME has already removed X11 and Plasma removes it in October 2026 [[6]](https://www.xda-developers.com/x11-on-gnome-is-finally-dead-as-its-newest-version-goes-all-in-on-wayland/) [[5]](https://linuxiac.com/kde-plasma-6-8-will-go-fully-wayland-ending-nearly-30-years-of-x11-sessions/).

Practical consequence: choose the **distro** on release model and hardware support, and the **desktop** second — unless your desktop is one of the three above, in which case the desktop chose for you.

## The recommendation for a Windows 11 developer

**[Fedora KDE](https://fedoraproject.org/kde/) 44** (Plasma 6.6.4, a flagship edition rather than a second-class spin) [[37]](https://www.helpnetsecurity.com/2026/04/29/fedora-linux-44-released/) [[38]](https://fedoramagazine.org/whats-new-in-fedora-kde-plasma-desktop-44/), or **[Kubuntu](https://kubuntu.org/) 26.04 LTS** if you want a five-year support window over current packages [[39]](https://www.tecmint.com/kde-plasma-linux-distros/).

Why Plasma specifically, for this profile:

- Taskbar, start menu and tray are the defaults, so day one costs you nothing in muscle memory [[14]](https://www.makeuseof.com/kde-plasma-is-linux-desktop-recommend-to-windows-users-after-tweaks/).
- Global shortcuts work — the only major desktop where they do — which matters the moment you want push-to-talk in a Teams call or a system-wide screenshot key [[2]](https://github.com/flatpak/xdg-desktop-portal/discussions/1368).
- Mixed-DPI multi-monitor with non-blurry X11 apps, which is the setup that generates the most "Linux isn't ready" complaints elsewhere [[33]](https://www.neowin.net/news/kde-is-getting-support-for-the-xx-fractional-scale-v2-wayland-protocol/).
- Customisation is a settings problem, not an extension-compatibility problem, so major upgrades don't silently remove your taskbar [[3]](https://discourse.gnome.org/t/gnome-50-extension-review-status/34569).

Two caveats worth acting on before you install:

- ⚠ **If the machine has an NVIDIA GPU**, this is your dominant risk, not your desktop choice. Confirm driver 580-series or later and expect to read a forum thread or two; AMD/Intel graphics make Wayland a non-issue [[30]](https://forums.developer.nvidia.com/t/nvidia-580-on-kde-wayland-freezes/355175) [[31]](https://news.ycombinator.com/item?id=46485989).
- ⚠ **If you want to RDP into this machine from elsewhere** — plausible for a homelab owner — GNOME is currently the better desktop for it. GNOME Remote Desktop supports headless and pre-login remote login through GDM with hardware-accelerated encoding; KDE's KRDP requires an already-logged-in session and has no headless plans [[28]](https://forum.manjaro.org/t/remote-desktop-options-for-headless-kde-plasma-on-wayland/183945) [[17]](https://release.gnome.org/50/). If that's a hard requirement, either run GNOME on that box or plan on SSH plus X-forwarding-free tooling instead.

If you'd rather optimise for "boring": **Linux Mint** with Cinnamon, X11 session, and revisit in a year. You give up HDR, VRR, good gestures and global-shortcut portals, and you buy a desktop that will not change under you [[4]](https://www.omgubuntu.co.uk/2026/07/linux-mint-wayland-fully-supported) [[20]](https://eylenburg.github.io/de_comparison.htm).
