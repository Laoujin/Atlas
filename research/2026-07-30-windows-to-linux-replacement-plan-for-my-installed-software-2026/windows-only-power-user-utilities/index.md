---
title: "The utility belt: per-tool Linux verdicts for a Windows power user (2026)"
date: 2026-07-30
depth: standard
format: md
topic: "Linux replacements for a Windows power user's utility belt (2026): PowerToys, AutoHotkey, Ditto, ShareX, WinDirStat, Sandboxie, IrfanView, Paint.NET, Notepad++ and friends — a per-tool verdict, not a blanket recommendation."
topic_raw: "can you check what software I have on my system installed (Windows) and then do a comparison with what I could replace that software with once I throw away Windows for Linux? (for those that are not available on Linux right away)"
tags: [linux, windows, migration, powertoys, autohotkey, wayland, utilities]
summary: "Per-tool verdicts for the Windows-only utilities in an actual installed-software inventory: most transfer cleanly, AutoHotkey and Power Automate Desktop have no single answer, and Wayland is the variable that decides the rest."
citations: 32
reading_time_min: 15
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 885
issue: 13
---

> **TL;DR** — Of the 40-odd Windows-only utilities in your inventory, most have a straight or better Linux counterpart: 7-Zip ships an official Linux build [[17]](https://www.7-zip.org/download.html), CopyQ beats Ditto [[15]](https://copyq.readthedocs.io/en/latest/known-issues.html), QDirStat is WinDirStat's direct descendant [[16]](https://github.com/shundhammer/qdirstat/issues/97) ⭐ 2.5k, KDE Connect beats Phone Link [[24]](https://www.howtogeek.com/forget-microsoft-phone-link-use-this-app-instead/), and PDFtk still runs as `pdftk-java` [[19]](https://opensource.com/article/21/12/edit-pdf-linux-pdftk). Three things force a real workflow change: **ShareX** (you assemble it from 3–4 tools), **Sandboxie** (Firejail/bubblewrap sandbox *by profile*, not by transparently shadowing an installed app) [[25]](https://havenmessenger.com/blog/posts/linux-sandboxing-tools/), and **1Password** (fine, but never install the Flatpak — it loses system unlock and the SSH agent) [[20]](https://support.1password.com/install-linux/). Two have **no real answer**: **AutoHotkey** — community consensus in 2026 is still that you replace it with 3–5 separate projects and accept that window automation is desktop-specific [[2]](https://lemmy.world/post/35105871) — and **Power Automate Desktop**, which is Windows-MSI/Store-only with no Linux build at all [[18]](https://learn.microsoft.com/en-us/power-automate/desktop-flows/install).

Everything below is scoped to what is actually installed on the machine. The display server is the hidden variable in half of these rows: GNOME 50 removed the X11 session in March 2026 [[12]](https://www.theregister.com/2026/03/19/gnome_50/) and Plasma 6.8 drops it in October 2026 [[13]](https://9to5linux.com/kde-plasma-6-8-desktop-environment-to-drop-the-x11-session-and-go-wayland-only), so "just use X11" is no longer a migration strategy on a mainstream desktop.

## Main table

| Windows app (installed) | Linux replacement | Parity | Migration notes |
|---|---|:--:|---|
| [PowerToys](https://learn.microsoft.com/en-us/windows/powertoys/) 0.97.1 ⭐ 137k | no single package — see per-module table | ⚠ | 30 utilities [[1]](https://learn.microsoft.com/en-us/windows/powertoys/); ~2/3 are native features on Linux, the rest need a named tool |
| [AutoHotkey](https://www.autohotkey.com/) 2.0.19 | [keyd](https://github.com/rvaiya/keyd) ⭐ 5.8k + [keymapper](https://github.com/houmain/keymapper) ⭐ 1.1k + [Espanso](https://espanso.org) ⭐ 14k + compositor keybinds | ✗ | No single replacement exists; see the dedicated section [[2]](https://lemmy.world/post/35105871) |
| Microsoft.PowerAutomateDesktop | [Robot Framework](https://robotframework.org) ⭐ 12k, [UI.Vision RPA](https://ui.vision/rpa), [Actiona](https://actiona.tools) ⭐ 727, [n8n](https://n8n.io) ⭐ 199k (cloud/API flows only) | ✗ | Windows MSI/Store only, needs Windows Desktop .NET [[18]](https://learn.microsoft.com/en-us/power-automate/desktop-flows/install). Nothing on Linux does record-and-replay UI automation over arbitrary GUI apps at PAD's level [[31]](https://ui.vision/rpa) |
| [Ditto](https://ditto-cp.sourceforge.io/) 3.25 | [CopyQ](https://github.com/hluk/CopyQ) ⭐ 12k | ✓ | Superset of Ditto (scripting, tabs, item commands). ⚠ On Wayland: global shortcuts need `xdg-desktop-portal`, GNOME needs the CopyQ Shell extension, and modifier/mouse-position queries don't work [[15]](https://copyq.readthedocs.io/en/latest/known-issues.html). Minimal alternatives: [cliphist](https://github.com/sentriz/cliphist) ⭐ 1.5k, [clipse](https://github.com/savedra1/clipse) ⭐ 1.0k |
| [ShareX](https://getsharex.com) 21.0 ⭐ 39k | [Flameshot](https://flameshot.org) ⭐ 31k **or** `grim`+`slurp`+[Satty](https://github.com/Satty-org/Satty) ⭐ 2.3k; [ksnip](https://github.com/ksnip/ksnip) ⭐ 3.3k; + [Kooha](https://github.com/SeaDve/Kooha) ⭐ 3.5k / [OBS](https://obsproject.com) ⭐ 74k for video | ⚠ | The single biggest workflow loss. Nothing bundles capture + annotate + OCR + custom-uploader + history. Flameshot's own docs enumerate Wayland breakage (repeat portal prompts on GNOME, multi-monitor overlay bugs, shortcuts not firing) and say "We cannot do anything about it!" [[14]](https://flameshot.org/docs/guide/wayland-help/). Custom uploaders become a shell script |
| Microsoft.ScreenSketch (Snipping Tool) | [Spectacle](https://apps.kde.org/spectacle/) (KDE) / GNOME Screenshot | ✓ | Both are Wayland-native and portal-based; Spectacle also records screen |
| [WinDirStat](https://windirstat.net) 2.2.2 | [QDirStat](https://github.com/shundhammer/qdirstat) ⭐ 2.5k; [Filelight](https://apps.kde.org/filelight/) (KDE); Baobab (GNOME); [gdu](https://github.com/dundee/gdu) ⭐ 5.9k / [dust](https://github.com/bootandy/dust) ⭐ 12k / [dua](https://github.com/Byron/dua-cli) ⭐ 6.1k in the terminal | ✓ | QDirStat is the KDirStat/WinDirStat lineage with the same treemap [[16]](https://github.com/shundhammer/qdirstat/issues/97). Bonus: [Czkawka](https://github.com/qarmin/czkawka) ⭐ 32k for duplicate hunting |
| [Sandboxie](https://sandboxie-plus.com) 5.71.9 ⭐ 19k | [Firejail](https://github.com/netblue30/firejail) ⭐ 7.6k; [bubblewrap](https://github.com/containers/bubblewrap) ⭐ 8.2k; [Flatpak](https://flatpak.org) ⭐ 5.0k + portals | ⚠ | Windows-only, kernel-driver based [[32]](https://github.com/sandboxie-plus/Sandboxie). Model differs: Sandboxie shadows writes of an already-installed app and lets you discard them; Firejail applies a namespace/seccomp *profile* at launch, bubblewrap ships no ready-made profiles, and Flatpak only confines Flatpak-installed apps [[25]](https://havenmessenger.com/blog/posts/linux-sandboxing-tools/). "Run this .exe throwaway and delete the changes" has no direct equivalent |
| [IrfanView](https://www.irfanview.com) 4.73 | [XnView MP](https://www.xnview.com/en/xnviewmp/) (closest, closed-source); [nomacs](https://github.com/nomacs/nomacs) ⭐ 3.1k; [qView](https://github.com/jurplel/qView) ⭐ 3.4k / [qimgv](https://github.com/easymodo/qimgv) ⭐ 3.1k for pure speed; [ImageMagick](https://imagemagick.org) ⭐ 17k for batch | ⚠ | XnView MP is the only one matching IrfanView's format breadth + batch converter in one GUI [[26]](https://alternativeto.net/software/irfanview/?platform=linux). Expect to move batch conversion to `magick mogrify` |
| [Paint.NET](https://getpaint.net) 5.1.11 | [Pinta](https://github.com/PintaProject/Pinta) ⭐ 3.8k; [Krita](https://krita.org); [GIMP](https://gimp.org) | ⚠ | Pinta is explicitly the Paint.NET-shaped option (layers, effects, low ceiling) [[27]](https://alternativeto.net/software/paintnet/?platform=linux). Paint.NET plugins (.dll) don't port |
| Microsoft.Paint | [Drawing](https://apps.gnome.org/Drawing/) / [KolourPaint](https://apps.kde.org/kolourpaint/) | ✓ | Same scope, same speed |
| Microsoft.Windows.Photos | [Loupe](https://apps.gnome.org/Loupe/) / [Gwenview](https://apps.kde.org/gwenview/) / [gThumb](https://apps.gnome.org/gThumb/) | ✓ | gThumb also covers tagging + batch rename/convert [[26]](https://alternativeto.net/software/irfanview/?platform=linux) |
| Microsoft.RawImageExtension | LibRaw / [darktable](https://darktable.org) / [RawTherapee](https://rawtherapee.com) | ✓ | RAW decoding is a library on Linux, not a shell extension — thumbnailers pick it up automatically |
| [Notepad++](https://notepad-plus-plus.org) 8.9.1 ⭐ 29k (+ Store pkg) | [Kate](https://apps.kde.org/kate/); [Notepadqq](https://github.com/notepadqq/notepadqq) ⭐ 2.3k; [VSCodium](https://github.com/VSCodium/vscodium) ⭐ 33k | ⚠ | No official Linux build; the Wine/Snap package is an unofficial third-party effort [[22]](https://itsfoss.com/notepad-alternatives-for-linux/). Kate is the honest upgrade (multi-cursor, LSP, sessions); Notepadqq is the nostalgia option. NPP plugins don't port |
| Microsoft.WindowsNotepad | GNOME Text Editor / Kate | ✓ | — |
| [7-Zip](https://www.7-zip.org) 25.01 ⭐ 3.6k | official `7zz` 26.02 for Linux; `p7zip`; [Ark](https://apps.kde.org/ark/) / File Roller GUI | ✓ | Upstream ships x86-64/x86/arm64/arm console builds [[17]](https://www.7-zip.org/download.html) — same engine, same switches. Only the Explorer context menu is gone (file managers have their own) |
| [PDFtk](https://www.pdflabs.com/tools/pdftk-server/) / PDFtk Server 2.02 | `pdftk-java`; [qpdf](https://github.com/qpdf/qpdf) ⭐ 5.3k; `poppler-utils` (`pdfunite`, `pdfseparate`, `pdftotext`); [PDF Arranger](https://github.com/pdfarranger/pdfarranger) ⭐ 5.7k GUI | ✓ | `pdftk-java` keeps the CLI verbatim, so existing scripts survive [[19]](https://opensource.com/article/21/12/edit-pdf-linux-pdftk); qpdf is the better long-term target for structural edits |
| Clipchamp | [Kdenlive](https://kdenlive.org); [Shotcut](https://github.com/mltframework/shotcut) ⭐ 15k; [OpenShot](https://openshot.org) | ✓ | All three exceed Clipchamp's ceiling [[29]](https://www.linuxtoday.com/blog/best-free-and-open-source-alternatives-to-microsoft-clipchamp/); you lose the stock-library/templates layer |
| Microsoft.WindowsSoundRecorder | [Sound Recorder](https://apps.gnome.org/SoundRecorder/) / [Audacity](https://github.com/audacity/audacity) ⭐ 17k | ✓ | — |
| Microsoft.CommandPalette | [rofi](https://github.com/davatorium/rofi) ⭐ 16k (X11) / [Ulauncher](https://github.com/Ulauncher/ulauncher) ⭐ 4.5k / [Albert](https://github.com/albertlauncher/albert) ⭐ 8.0k / [Walker](https://github.com/abenz1267/walker) ⭐ 2.9k (Wayland) | ✓ | Albert is the closest plugin-model match to PowerToys Run/Command Palette [[28]](https://www.howtogeek.com/786985/linux-alternatives-for-windows-powertoys/); Walker/`fuzzel` if you go wlroots |
| Microsoft.WindowsTerminal | [Ghostty](https://ghostty.org) ⭐ 59k; [WezTerm](https://github.com/wezterm/wezterm) ⭐ 28k; [kitty](https://github.com/kovidgoyal/kitty) ⭐ 34k | ✓ | Strictly better. WezTerm keeps the config-as-code + multiplexer model closest to WT profiles |
| Microsoft.YourPhone / MicrosoftWindows.CrossDevice | [KDE Connect](https://kdeconnect.kde.org) / [GSConnect](https://github.com/GSConnect/gnome-shell-extension-gsconnect) ⭐ 3.7k | ✓ | LAN-only, no cloud account; adds bidirectional clipboard, remote input, run-command, presenter mode [[24]](https://www.howtogeek.com/forget-microsoft-phone-link-use-this-app-instead/) |
| Smart Connect (Motorola) 8.0 | KDE Connect | ⚠ | Vendor-specific desktop-mode/app-streaming from the Moto stack has no Linux client; KDE Connect covers notifications, files, clipboard, media, remote input [[24]](https://www.howtogeek.com/forget-microsoft-phone-link-use-this-app-instead/) |
| [1Password](https://1password.com) 8.12 | 1Password for Linux (deb/rpm/AUR/tar.gz) | ⚠ | Full desktop client with system-authentication unlock via user password, fingerprint/biometrics or security key [[21]](https://support.1password.com/system-authentication-linux/). **Use the deb/rpm, not the Flatpak** — Flatpak loses system authentication, the SSH agent, and unified app↔browser unlock [[20]](https://support.1password.com/install-linux/) |
| Microsoft.Windows.DevHome | nothing to migrate | ⚠ | It is a dashboard over winget/WSL/GitHub. The Linux analogue is declarative env config (Nix, `mise`, devcontainers), not an app |
| MicrosoftCorporationII.QuickAssist | [RustDesk](https://rustdesk.com) ⭐ 119k | ⚠ | Wayland capture via PipeWire + XDG portal with a remembered consent dialog, multi-monitor since 1.4.3, permanent password for unattended access [[23]](https://rustdesk.com/blog/rustdesk-for-linux/). Pre-login/headless needs a virtual-display setup — no "send a 6-digit code to a stranger" flow out of the box |
| Microsoft.SecHealthUI / McAfeeWPSSparsePackage | drop both; ClamAV only if you scan files for Windows peers | ⚠ | ClamAV is a signature scanner with no behavioural analysis, memory scanning or response — it is not a Defender replacement [[30]](https://linuxsecurity.com/news/vendors-products/what-is-clamav) |

## PowerToys, per module

The installed 0.97.1 build plus the three shell-extension packages (FileLocksmith, ImageResizer, PowerRename) covers 30 utilities [[1]](https://learn.microsoft.com/en-us/windows/powertoys/). FancyZones / Workspaces / Grab And Move are window management — covered elsewhere in this expedition. The rest:

| PowerToys module | Linux equivalent | Parity | Notes |
|---|---|:--:|---|
| PowerToys Run | [Albert](https://github.com/albertlauncher/albert) ⭐ 8.0k / [Ulauncher](https://github.com/Ulauncher/ulauncher) ⭐ 4.5k / [rofi](https://github.com/davatorium/rofi) ⭐ 16k | ✓ | Albert has the same plugin/calculator/web-search model [[28]](https://www.howtogeek.com/786985/linux-alternatives-for-windows-powertoys/) |
| PowerRename (shell ext) | [KRename](https://apps.kde.org/krename/), Thunar Bulk Rename, `gThumb`; [rnr](https://github.com/ismaelgv/rnr) ⭐ 590 CLI | ✓ | Regex + preview + undo all present; `rnr` has dry-run and undo scripts |
| ImageResizer (shell ext) | Nautilus/Nemo/Dolphin service menus over [ImageMagick](https://imagemagick.org) ⭐ 17k; [Converseen](https://converseen.fasterland.net) | ✓ | You write a one-line `.desktop` action once |
| FileLocksmith (shell ext) | `lsof` / `fuser -v` | ✓ | No GUI, but Linux rarely blocks deletes on open handles — the *problem* mostly disappears |
| Text Extractor (OCR) | [NormCap](https://github.com/dynobo/normcap) ⭐ 2.7k; [Frog](https://github.com/TenderOwl/Frog) ⭐ 893 | ⚠ | NormCap is the direct analogue [[28]](https://www.howtogeek.com/786985/linux-alternatives-for-windows-powertoys/); on GNOME/Wayland any screen-grab tool inherits the portal permission prompt problem [[14]](https://flameshot.org/docs/guide/wayland-help/) |
| Color Picker | `gpick`, `gcolor3`, [KColorChooser](https://apps.kde.org/kcolorchooser/), `hyprpicker` | ⚠ | X11 pickers grab pixels freely; on Wayland use the compositor-native picker (`hyprpicker`, Plasma's) [[28]](https://www.howtogeek.com/786985/linux-alternatives-for-windows-powertoys/) |
| Advanced Paste | [CopyQ](https://github.com/hluk/CopyQ) ⭐ 12k item commands | ⚠ | Paste-as-plain-text and format conversion are scriptable in CopyQ; the AI-transform path is absent |
| Awake | `systemd-inhibit`, `caffeine-ng`, Plasma/GNOME "keep awake" | ✓ | — |
| Always On Top | compositor keybind (KWin, GNOME extension, `hyprctl`) | ✓ | Built into every WM |
| Peek | GNOME Sushi / Dolphin preview / `ranger`+`ueberzug` | ✓ | — |
| Quick Accent | XKB compose key / `ibus` | ✓ | Native input-method feature; no helper app |
| Screen Ruler | [KRuler](https://apps.kde.org/kruler/), `xrestop`-style GNOME extensions | ⚠ | KRuler is X11-oriented; on Wayland measurement tools are compositor-dependent |
| Mouse utilities (Find My Mouse, Highlighter, Crosshairs) | GNOME/Plasma accessibility: locate-pointer, click highlight, crosshair overlays | ⚠ | Distributed across accessibility settings, not one panel |
| Mouse Without Borders | [Deskflow](https://github.com/deskflow/deskflow) ⭐ 28k / [Input Leap](https://github.com/input-leap/input-leap) ⭐ 8.4k | ⚠ | Cross-machine KVM must inject input, so on Wayland it goes through the portal/libei route rather than raw X grabs [[10]](http://who-t.blogspot.com/2026/07/libei-integrations-in-xdg-remotedesktop.html) |
| Keyboard Manager | [keyd](https://github.com/rvaiya/keyd) ⭐ 5.8k / [kanata](https://github.com/jtroo/kanata) ⭐ 7.7k | ✓ | Strictly more capable (layers, tap-hold, per-device) [[3]](https://github.com/rvaiya/keyd) |
| ZoomIt | [Gromit-MPX](https://github.com/bk138/gromit-mpx) ⭐ 1.4k, Plasma zoom effect, [Kooha](https://github.com/SeaDve/Kooha) ⭐ 3.5k | ⚠ | Zoom + annotate + record in one hotkey has no single equivalent |
| Crop And Lock | — | ✗ | Niche; nothing reproduces the interactive cropped-thumbnail window |

## AutoHotkey: the one with no answer

AHK is four products in one: a hotkey daemon, a key remapper, a text expander, and a scripting language with window/GUI/COM automation. Linux splits these across layers, and the layer determines whether it survives Wayland.

**Layer 1 — kernel input (`evdev`/`uinput`). Display-server independent, so Wayland-proof.**

| Tool | ⭐ | What it covers | Caveats |
|---|--:|---|---|
| [keyd](https://github.com/rvaiya/keyd) | 5.8k | Layers, tap-hold, oneshot mods, macros, per-device, app-specific | Reads raw evdev and synthesises via uinput — works under X, Wayland and even a bare VT [[3]](https://github.com/rvaiya/keyd). Linux-only; needs a root daemon |
| [kanata](https://github.com/jtroo/kanata) | 7.7k | Same plus mouse output, chords, cross-platform config you can reuse on Windows | Needs `/dev/*` access (avoid-sudo recipes exist); unicode output leans on `ibus` and is inconsistent, rapid key events can misfire [[4]](https://github.com/jtroo/kanata/blob/main/docs/platform-known-issues.adoc) |
| [keymapper](https://github.com/houmain/keymapper) | 1.1k | **The closest thing to AHK's mental model** — per-application context rules keyed on window title/class/process | Wayland context awareness requires the compositor to tell keymapper what's focused: automatic on wlroots, otherwise via its GNOME Shell extension or KWin script; process `path` may be unavailable on Wayland [[5]](https://github.com/houmain/keymapper) |
| [kmonad](https://github.com/kmonad/kmonad) | 5.0k | QMK-style layers | Older, fewer features than kanata; kanata was inspired by it |
| [xremap](https://github.com/xremap/xremap) | 2.1k | App-specific remapping, Wayland-aware | Needs a compositor-specific feature flag per DE |

**Layer 2 — text expansion.** [Espanso](https://espanso.org) ⭐ 14k is the real answer and it is genuinely good (triggers, forms, shell/script extensions, package registry). It ships *separate X11 and Wayland builds*; the Wayland one is still labelled experimental, requires `setcap cap_dac_override+p`, needs non-US layouts declared explicitly, app-specific config only works on KDE-Wayland if you also install [kdotool](https://github.com/jinliu/kdotool) ⭐ 378, and a newly plugged keyboard requires `espanso restart` [[6]](https://espanso.org/docs/install/linux/).

**Layer 3 — scripted GUI automation. This is where AHK dies.**

- [AutoKey](https://github.com/autokey/autokey) ⭐ 3.9k is the historical AHK-for-Linux (Python scripting + phrase expansion + window ops) but it "is a Xorg application and will not function in a Wayland session" [[7]](https://github.com/autokey/autokey/issues/1061). The only Wayland-capable variant is the [autokey-wayland](https://github.com/dlk3/autokey-wayland) fork ⭐ 27 — GNOME-only, KDE "planned" [[8]](https://github.com/dlk3/autokey-wayland). A 27-star fork is not a foundation for your automation.
- Input synthesis: [xdotool](https://github.com/jordansissel/xdotool) ⭐ 3.8k is X11-only by construction. On Wayland you get [ydotool](https://github.com/ReimuNotMoe/ydotool) ⭐ 2.3k, which "uses the uinput framework of Linux kernel to emulate an input device" instead of sending X events — so it types and clicks anywhere, but its daemon "requires root permissions" and it has no window query/manipulation commands at all [[9]](https://github.com/ReimuNotMoe/ydotool). [wtype](https://github.com/atx/wtype) ⭐ 549 types via `virtual-keyboard-unstable-v1`, which GNOME does not implement.
- Hotkey daemons: [sxhkd](https://github.com/baskerville/sxhkd) ⭐ 3.0k (X11 only), [swhkd](https://github.com/waycrate/swhkd) ⭐ 854 (Wayland, privileged daemon). In practice you bind hotkeys in the compositor's own config instead.
- GUI-flow automation: [Actiona](https://actiona.tools) ⭐ 727 is the closest visual macro tool, but it descends from the X11 automation stack.

**What Wayland makes structurally impossible.** Wayland has no equivalent of `XGrabKey`/`XTestFakeInput`: a client cannot read the keyboard while unfocused, cannot enumerate or move other clients' windows, and cannot inject synthetic input. Everything must go through a broker:

- Input injection → the XDG **RemoteDesktop** / **InputCapture** portals backed by **libei**, integrated since portal 1.17 with persistent authorisation since 1.21, which means "clients using XDG portals now work with any compositor that implements the portal, with no need for GNOME/KDE-specific APIs" [[10]](http://who-t.blogspot.com/2026/07/libei-integrations-in-xdg-remotedesktop.html). But it is *consent-gated* and text/gesture/tablet support is still being added [[10]](http://who-t.blogspot.com/2026/07/libei-integrations-in-xdg-remotedesktop.html).
- Global hotkeys → the **GlobalShortcuts** portal, whose coverage is still patchy: wlroots' `xdg-desktop-portal-wlr` ships no implementation at all, so registration outright fails on Niri/Sway/River [[11]](https://github.com/aaddrick/claude-desktop-debian/blob/main/docs/learnings/wayland-global-shortcuts-portal.md).
- Window manipulation → nothing portable. As the r/Linux-adjacent Lemmy consensus puts it: "you won't find a single alternative, but you'll have to find multiple projects for specific features… Window automation is DE/WM specific" [[2]](https://lemmy.world/post/35105871).

**Recommended stack:** `keyd` (or `kanata` if you want one config across both OSes) for remaps and layers → `keymapper` if you need per-app rules → Espanso for text → compositor keybinds calling shell scripts for everything AHK's scripting language did. Accept that pixel-hunting/window-poking macros do not port; rewrite them against CLIs and D-Bus instead.

## The Wayland tax

Still X11-only or degraded in 2026, among the tools above — relevant because GNOME 50 [[12]](https://www.theregister.com/2026/03/19/gnome_50/) and Plasma 6.8 [[13]](https://9to5linux.com/kde-plasma-6-8-desktop-environment-to-drop-the-x11-session-and-go-wayland-only) no longer offer an X11 session:

| Tool | Status on Wayland |
|---|---|
| AutoKey (upstream) ⭐ 3.9k | ✗ Will not function in a Wayland session [[7]](https://github.com/autokey/autokey/issues/1061) |
| xdotool ⭐ 3.8k | ✗ X11 protocol by definition; only affects XWayland clients |
| sxhkd ⭐ 3.0k | ✗ X11 key grabs |
| Flameshot ⭐ 31k | ⚠ Portal-dependent; documented GNOME permission-prompt loops, multi-monitor overlay and hotkey failures [[14]](https://flameshot.org/docs/guide/wayland-help/) |
| Espanso ⭐ 14k | ⚠ Separate experimental Wayland build; setcap, layout declaration, keyboard-hotplug restarts, app-specific config only via kdotool on KDE [[6]](https://espanso.org/docs/install/linux/) |
| CopyQ ⭐ 12k | ⚠ Needs portal for shortcuts, Shell extension on GNOME; modifier/mouse queries unavailable [[15]](https://copyq.readthedocs.io/en/latest/known-issues.html) |
| ydotool ⭐ 2.3k | ⚠ Works, but root daemon and no window operations [[9]](https://github.com/ReimuNotMoe/ydotool) |
| wtype ⭐ 549 | ⚠ Requires `virtual-keyboard-unstable-v1`, absent on GNOME |
| keymapper ⭐ 1.1k | ⚠ Context rules need a per-compositor bridge; process path may be unavailable [[5]](https://github.com/houmain/keymapper) |
| keyd ⭐ 5.8k / kanata ⭐ 7.7k / Espanso's input layer | ✓ Below the display server entirely [[3]](https://github.com/rvaiya/keyd) |

Practical consequence: **pick KDE Plasma or GNOME, not a wlroots compositor**, if input automation matters — the portal implementations you depend on are missing on wlroots [[11]](https://github.com/aaddrick/claude-desktop-debian/blob/main/docs/learnings/wayland-global-shortcuts-portal.md).

## Already native / trivially replaced

No research needed for these — they are OS features or one-line installs on Linux:

- **7-Zip** → official upstream `7zz` binary, identical CLI [[17]](https://www.7-zip.org/download.html)
- **PowerToys Hosts File Editor** → `/etc/hosts` in any editor · **Environment Variables** → shell rc / `systemd` environment.d · **Registry Preview** → no registry exists · **Command Not Found** → `command-not-found` ships with Debian/Ubuntu and Fedora · **Shortcut Guide** → DE keyboard-shortcut settings · **File Explorer add-ons** (preview/thumbnails) → thumbnailers are system-wide · **New+** (templates) → `~/Templates` · **Light Switch** → GNOME/Plasma scheduled night/dark theme · **Power Display** → `ddcutil` / Plasma brightness applet
- **Snipping Tool** → Spectacle / GNOME Screenshot · **Paint** → Drawing/KolourPaint · **Photos** → Loupe/Gwenview · **Notepad** → GNOME Text Editor/Kate · **Sound Recorder** → GNOME Sound Recorder · **Windows Terminal** → Ghostty/WezTerm/kitty · **RAW extension** → LibRaw, already in every thumbnailer
- **Clipboard plumbing** → `wl-clipboard` ⭐ 2.4k (`wl-copy`/`wl-paste`) replaces the clip.exe/PowerShell dance
- **Windows Security / McAfee** → uninstall, don't replace [[30]](https://linuxsecurity.com/news/vendors-products/what-is-clamav)
