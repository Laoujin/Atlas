---
title: "Gaming after the switch: your library survives, the NVIDIA App does not"
date: 2026-07-30
depth: standard
format: md
topic: "Gaming after the switch to Linux (2026): Steam/Proton, the Epic and Paradox launchers, NVIDIA drivers on a Legion laptop, and the kernel-anti-cheat titles that simply will not run."
topic_raw: "can you check what software I have on my system installed (Windows) and then do a comparison with what I could replace that software with once I throw away Windows for Linux? (for those that are not available on Linux right away)"
tags: [linux, gaming, proton, nvidia, anti-cheat]
summary: "Both installed games run under Proton — Planetfall is Gold/Deck-Playable and Fall Guys' EAC is Linux-enabled — so the only hard loss is the NVIDIA App and Game Bar tooling layer, which becomes environment variables plus MangoHud and GPU Screen Recorder."
citations: 38
reading_time_min: 10
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 1031
issue: 13
---

> **TL;DR** — Every game on this machine runs. Age of Wonders: Planetfall is ProtonDB **Gold** (trending Platinum, 95 reports) [[1]](https://www.protondb.com/api/v1/reports/summaries/718850.json) and Valve rates it **Playable** on Deck/SteamOS/Steam Machine [[2]](https://store.steampowered.com/app/718850/Age_of_Wonders_Planetfall/); Fall Guys is one of the 146-of-245 anti-cheat titles GamingOnLinux records as **Works** [[3]](https://www.gamingonlinux.com/anticheat/). The single ✗ is **the NVIDIA App** — DLSS overrides, driver-level game profiles and ShadowPlay have no GUI on Linux, only environment variables and separate tools [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html). The forward-looking blocker is what you *don't* own yet: kernel-mode anti-cheat (Riot Vanguard, EA Javelin) is structurally unrunnable, so any future purchase in that class stays a Windows purchase [[3]](https://www.gamingonlinux.com/anticheat/).

## The inventory, row by row

| Windows app/game | Linux path | Verdict | Notes |
|---|---|---|---|
| Steam 2.10.91.91 | Native Linux client + Proton | ✓ | Baseline. Proton 11.0-1 stable since 7 Jul 2026, on Wine 11.0 with DXVK 2.7 / VKD3D 1.19 [[5]](https://www.phoronix.com/news/Proton-11.0-1). Nothing to replace. |
| Age of Wonders: Planetfall | Steam + Proton | ✓ | ProtonDB Gold, trending Platinum, 95 reports [[1]](https://www.protondb.com/api/v1/reports/summaries/718850.json). Deck/SteamOS/Steam Machine = Playable; default graphics config flagged performant, startup functional on SteamOS [[2]](https://store.steampowered.com/app/718850/Age_of_Wonders_Planetfall/). Deck caveats are controller-config and small text, not rendering. |
| Paradox Launcher v2 | Proton, or bypass it | ⚠ | The Proton bug `Failed to install Paradox Launcher: exit status 1603` has been open since Aug 2019 [[6]](https://github.com/ValveSoftware/Proton/issues/2959) ⭐ 32k. Gold rating comes from reports that route *around* the launcher. Bypass with a `sed` rewrite of Proton's command line (below) [[7]](https://steamcommunity.com/sharedfiles/filedetails/?id=3064452556). |
| Epic Games Launcher 1.3.170.0 | [Heroic](https://heroicgameslauncher.com/) | ✓ | No Linux client exists. Heroic covers Epic + GOG + Amazon and manages Wine-GE/Proton-GE itself [[8]](https://heroicgameslauncher.com/) ⭐ 12k. |
| Epic Online Services 2.0.33.0 | Heroic's EOS Overlay | ⚠ | Installed once globally, then enabled **per game**, and needs DXVK plus the `corefonts` winetricks package [[9]](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/wiki/EOS-Overlay) ⭐ 12k. Friend list/achievements work; the overlay is the fiddly part. |
| Fall Guys (Mediatonic) | Heroic or legacy Steam entitlement + GE-Proton | ✓ | "Should work out of the box with no need for tweaking. Make sure to use the latest GE-Proton version." [[10]](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/wiki/Fall-Guys) ⭐ 12k. GamingOnLinux: **Works** [[3]](https://www.gamingonlinux.com/anticheat/); AreWeAntiCheatYet: **Running**, Mediatonic enabled the EAC Linux module in Mar 2022 [[11]](https://raw.githubusercontent.com/AreWeAntiCheatYet/AreWeAntiCheatYet/master/games.json). Use [GE-Proton](https://github.com/GloriousEggroll/proton-ge-custom) ⭐ 15k, not stock Proton [[12]](https://github.com/GloriousEggroll/proton-ge-custom). |
| NVIDIA Graphics Driver 596.11 | NVIDIA 595.x Linux branch | ✓ | NVIDIA pairs branches — release notes read "Version 595.71.05(Linux)/596.36(Windows)" [[13]](https://docs.nvidia.com/datacenter/tesla/tesla-release-notes-595-71-05/index.html) — so your Windows 596.x maps to Linux 595.x, i.e. you are not behind. Turing-and-newer now runs the **open** kernel modules by default [[14]](https://archlinux.org/news/nvidia-590-driver-drops-pascal-support-main-packages-switch-to-open-kernel-modules/). |
| NVIDIA App 11.0.4.148 | Env vars only | ✗ | No GUI equivalent. DLSS/Reflex/Smooth Motion are all environment variables [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html). Details below. |
| NVIDIA FrameView SDK 1.5 | [MangoHud](https://github.com/flightlessmango/MangoHud) ⭐ 8.9k | ✓ | FPS, frame times, temperatures, CPU/GPU load as a Vulkan/OpenGL overlay [[15]](https://github.com/flightlessmango/MangoHud); logs to CSV for the benchmarking half of FrameView. |
| NVIDIA PhysX System Software 9.23.1019 | Nothing to install | ✓ | PhysX is cross-platform and BSD-3 open source since Dec 2018 [[16]](https://en.wikipedia.org/wiki/PhysX); games carry their own libraries inside the Proton prefix. This redistributable has no counterpart to reinstall. |
| NVIDIACorp.NVIDIAControlPanel | `nvidia-settings` | ⚠ | Ships with the driver and is what the 595 changelog still refers to as the control panel [[17]](https://www.gamingonlinux.com/2026/03/nvidia-driver-595-58-03-released-as-the-big-new-recommended-stable-driver-for-linux/). Covers PowerMizer, resolution and sync; **no** per-game profile database. |
| Microsoft.XboxGamingOverlay / XboxIdentityProvider / XboxSpeechToTextOverlay | MangoHud + [GPU Screen Recorder](https://git.dec05eba.com/gpu-screen-recorder/about/); Xbox Cloud Gaming in a browser | ✗ | Game Bar's two real jobs split cleanly: overlay → MangoHud [[15]](https://github.com/flightlessmango/MangoHud), capture/Instant Replay → GPU Screen Recorder [[18]](https://git.dec05eba.com/gpu-screen-recorder/about/). The Xbox PC app and its identity provider have no Linux port; cloud streaming survives because xbox.com supports Edge and Chrome, both of which ship for Linux [[19]](https://support.xbox.com/en-US/help/games-apps/cloud-gaming/supported-browsers). |
| Discord 1.0.9250 | Native Linux client, or [Vesktop](https://github.com/Vencord/Vesktop) ⭐ 8.2k | ⚠ | Screen-share **with audio** on Wayland has been in Discord stable since Jan 2025, but only for apps that route via PulseAudio, and it was absent from the Flathub build [[20]](https://www.gamingonlinux.com/2025/01/discord-screen-sharing-with-audio-on-linux-wayland-is-officially-here/). If a game goes straight to PipeWire, Vesktop is the fix — Wayland screenshare with sound is its headline feature [[21]](https://github.com/Vencord/Vesktop). Install the `.deb`/`.rpm` or Vesktop, not the Flatpak. |

### The Paradox Launcher bypass

`<path to exe> %command%` does not work under Proton, because Proton's own wrapper chain *is* the command line. The working pattern rewrites that string instead [[7]](https://steamcommunity.com/sharedfiles/filedetails/?id=3064452556):

```
eval $( echo "%command%" | sed -E "s#Launcher/dowser.exe#<GameExe>.exe#g" )
```

Substitute Planetfall's own executable name for `<GameExe>`. Keep it in your notes: this is the first thing to try when a Paradox Launcher update or a Proton bump breaks startup, and it is why Planetfall's ProtonDB reports look inconsistent — half of them bypassed the launcher and half did not [[1]](https://www.protondb.com/api/v1/reports/summaries/718850.json).

## Anti-cheat: opt-in, not compatibility

The mechanism matters more than any per-game list, because it explains which future purchases are safe.

**EAC and BattlEye already run on Linux.** Epic added Easy Anti-Cheat support for Linux, macOS and Steam Deck *including Wine and Proton*, activated by the developer with a few clicks in the EOS Developer Portal [[22]](https://onlineservices.epicgames.com/news/epic-online-services-launches-anti-cheat-support-for-linux-mac-and-steam-deck). Concretely, the studio must be on EOS SDK 1.14+ and must activate a Linux client module — "Players running the game using Wine or Proton will use the Linux client module", so it also has to be tested and updated alongside Windows [[23]](https://dev.epicgames.com/docs/game-services/anti-cheat/anti-cheat-interfaces). BattlEye works the same way, opt-in via Valve [[24]](https://www.phoronix.com/news/BattlEye-Proton-Steam-Deck). → A "Broken" EAC game is a **business decision**, not a technical limit.

**Kernel-mode anti-cheat is a different category.** A Windows ring-0 driver has no Proton translation target — there is no kernel to load it into, and a user-space shim would defeat the entire threat model. That is why the vendors that went kernel-only appear as hard failures on GamingOnLinux's July 2026 list: 2XKO (Vanguard) Broken, EA SPORTS FC 27, Battlefield 2042 and F1 25 (EA Javelin) Broken [[3]](https://www.gamingonlinux.com/anticheat/).

**The numbers.** GamingOnLinux tracks 245 anti-cheat titles: 146 Works, 92 Broken, 7 needing reports [[3]](https://www.gamingonlinux.com/anticheat/). AreWeAntiCheatYet's wider 1166-game set is harsher — 642 Broken, 276 Running, 194 Supported, 52 explicitly Denied [[11]](https://raw.githubusercontent.com/AreWeAntiCheatYet/AreWeAntiCheatYet/master/games.json). Both agree on your one affected title: Fall Guys is fine [[3]](https://www.gamingonlinux.com/anticheat/)[[11]](https://raw.githubusercontent.com/AreWeAntiCheatYet/AreWeAntiCheatYet/master/games.json). Check either list *before* buying a multiplayer shooter; nothing else in this inventory is exposed.

## The Epic library: four tools, one answer

| Tool | ⭐ Stars | Handles Epic library | Scope | Fit here |
|---|---|---|---|---|
| [Heroic](https://heroicgameslauncher.com/) [[8]](https://heroicgameslauncher.com/) | ⭐ 12k | ✓ native (wraps Legendary) | Epic + GOG + Amazon, bundled Wine-GE/Proton-GE management | **Pick this.** Also the tool whose own wiki documents Fall Guys and the EOS overlay [[9]](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/wiki/EOS-Overlay)[[10]](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/wiki/Fall-Guys) |
| [Lutris](https://lutris.net/) [[25]](https://lutris.net/) | ⭐ 10k | ✓ | Steam, Epic, GOG, Humble + emulators, per-game install scripts | Keep as the second tool for anything needing a bespoke runner. Running both is normal. |
| [Bottles](https://usebottles.com/) [[26]](https://usebottles.com/) | ⭐ 8.6k | ✗ | Generic Wine-prefix manager for Windows *software* | Wrong category — it is a prefix manager, not a store client. Sibling research covers it for non-game apps. |
| [Legendary](https://github.com/legendary-gl/legendary) [[27]](https://github.com/legendary-gl/legendary) | ⭐ 5.2k | ✓ CLI only | Epic auth, install, cloud saves, EOS overlay install | Already underneath Heroic. Use it directly only for scripting. |

## NVIDIA on a hybrid Legion

**Driver branch.** Install the 595 series: 595.58.03 became the recommended stable Linux driver on 24 Mar 2026 [[17]](https://www.gamingonlinux.com/2026/03/nvidia-driver-595-58-03-released-as-the-big-new-recommended-stable-driver-for-linux/), with R595 adding Vulkan improvements, HDR work and DRI3 v1.2 over 590 [[29]](https://www.phoronix.com/review/nvidia-595-linux).

**Open vs proprietary kernel modules — decided for you.** From 590, Turing and newer transition automatically to the open kernel modules, and Pascal-and-older lost support entirely [[14]](https://archlinux.org/news/nvidia-590-driver-drops-pascal-support-main-packages-switch-to-open-kernel-modules/); distro packaging followed, with Arch's main `nvidia` packages now building the open modules [[28]](https://www.phoronix.com/news/Arch-LInux-NVIDIA-Open-Default). Any Legion new enough to carry an Intel Arc iGPU is far past Turing → take the default and stop thinking about it.

**Wayland gaming.** Usable, no longer experimental. The 590 branch raised the minimum Wayland version to 1.20 and fixed Vulkan swapchain re-creation, the stutter you see resizing a Vulkan window [[30]](https://www.phoronix.com/news/NVIDIA-590.44.01-Linux-Beta); 595 fixed kwin_wayland failing to wake displays, kernel crashes on DisplayPort MST dock disconnect, and added system-memory fallback specifically to stop Wayland desktop freezes on low VRAM [[17]](https://www.gamingonlinux.com/2026/03/nvidia-driver-595-58-03-released-as-the-big-new-recommended-stable-driver-for-linux/) — all three are laptop-and-dock failure modes.

**Frame pacing.** KDE Plasma 6.8 re-enables triple buffering by default for NVIDIA GPUs, cutting the stutter that appears when the compositor cannot align frame delivery with the display [[34]](https://linuxiac.com/kde-plasma-6-8-to-enable-triple-buffering-by-default-for-nvidia-gpus/). For per-game HDR, VRR and frame limiting independent of the desktop session, run the game inside [gamescope](https://github.com/ValveSoftware/gamescope) ⭐ 4.9k [[37]](https://github.com/ValveSoftware/gamescope) — that is the reliable route rather than fighting the host compositor.

**Hybrid graphics.** PRIME render offload keeps the dGPU idle until a game asks for it: `__NV_PRIME_RENDER_OFFLOAD=1` for Vulkan, plus `__GLX_VENDOR_LIBRARY_NAME=nvidia` for OpenGL/GLX [[31]](https://download.nvidia.com/XFree86/Linux-x86_64/590.48.01/README/primerenderoffload.html) — put those in the Steam launch options ahead of `%command%`. ⚠ **Advanced Optimus does not exist on Linux.** `vga-switcheroo` cannot express dynamic MUX switching [[33]](https://www.notebookcheck.net/Linux-gaming-laptops-may-finally-get-Nvidia-Advanced-Optimus-support-in-near-future.667413.0.html), and NVIDIA's replacement DRM-KMS user-space API is still a proposal [[32]](https://www.phoronix.com/news/NVIDIA-Dynamic-Mux-Switching). Practical consequence: choose hybrid or dGPU-direct in the Legion BIOS and reboot to change it — there is no on-the-fly switch, and G-Sync on the internal panel generally requires the dGPU-direct path. (TDP and fan curves, the Legion Space / Vantage replacement, are covered by sibling research.)

### What the NVIDIA App did that now needs a command line

NVIDIA's own Linux gaming documentation is the authority here, and it is entirely environment variables [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html):

| NVIDIA App feature | Linux equivalent |
|---|---|
| DLSS on/off per game | Automatic — Proton exposes NVAPI via bundled DXVK-NVAPI [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html) |
| DLSS override / force latest preset | `DXVK_NVAPI_DRS_NGX_DLSS_SR_OVERRIDE=on`, `..._FG_OVERRIDE=on`, or raw setting IDs via `DXVK_NVAPI_DRS_SETTINGS` [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html)[[35]](https://github.com/jp7677/dxvk-nvapi) ⭐ 641 |
| Auto-update DLSS DLLs | `PROTON_ENABLE_NGX_UPDATER=1` [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html) |
| Smooth Motion (driver-level frame gen) | `NVPRESENT_ENABLE_SMOOTH_MOTION=1`; ⚠ must not be combined with native DLSS Frame Generation [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html) |
| Reflex | Native via `VK_NV_low_latency2`; under Proton needs DXVK-NVAPI's Vulkan layer installed plus `DXVK_NVAPI_VKREFLEX=1` [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html) |
| Multi Frame Generation | Partial — DXVK-NVAPI 0.9.2 implements "limited/incomplete" Dynamic MFG and picks up R595's new DLSS settings [[36]](https://www.phoronix.com/news/DXVK-NVAPI-0.9.2-Released) |
| Driver-level per-game profile database | ✗ None. Per-game config lives in Steam launch options / Heroic per-game settings. |
| Performance overlay | MangoHud [[15]](https://github.com/flightlessmango/MangoHud) ⭐ 8.9k |
| ShadowPlay / Instant Replay | GPU Screen Recorder — NVENC, keeps only the last few minutes [[18]](https://git.dec05eba.com/gpu-screen-recorder/about/); [OBS Studio](https://github.com/obsproject/obs-studio) ⭐ 74k for streaming and manual capture [[38]](https://github.com/obsproject/obs-studio) |
| GPU utilisation reported *inside* a game | Needs `wine-nvml` installed manually — not bundled with Proton [[4]](https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/gaming.html) |

⚠ DLSS under Proton requires an NVIDIA Turing-or-newer GPU on the proprietary/open NVIDIA driver stack, and the game's `nvngx.dll`/`_nvngx.dll` must be present in the prefix's `system32` [[35]](https://github.com/jp7677/dxvk-nvapi).

## Migration order

1. Install the 595 driver with open kernel modules; verify `nvidia-settings` opens [[17]](https://www.gamingonlinux.com/2026/03/nvidia-driver-595-58-03-released-as-the-big-new-recommended-stable-driver-for-linux/).
2. Steam → enable Steam Play for all titles; test Planetfall, keep the `sed` bypass ready [[7]](https://steamcommunity.com/sharedfiles/filedetails/?id=3064452556).
3. Heroic → log into Epic, install GE-Proton, install Fall Guys [[8]](https://heroicgameslauncher.com/)[[10]](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher/wiki/Fall-Guys).
4. MangoHud + GPU Screen Recorder before you miss Game Bar [[15]](https://github.com/flightlessmango/MangoHud)[[18]](https://git.dec05eba.com/gpu-screen-recorder/about/).
5. Discord from the vendor package or Vesktop — not Flathub — if you screen-share [[20]](https://www.gamingonlinux.com/2025/01/discord-screen-sharing-with-audio-on-linux-wayland-is-officially-here/)[[21]](https://github.com/Vencord/Vesktop).
