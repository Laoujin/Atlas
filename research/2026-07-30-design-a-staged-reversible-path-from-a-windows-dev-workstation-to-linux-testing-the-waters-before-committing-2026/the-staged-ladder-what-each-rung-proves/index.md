---
title: "The staged ladder: what each rung of a Windows→Linux move actually proves"
date: 2026-07-30
depth: standard
format: md
topic: "The staged ladder: what each rung proves — WSL2 → live USB → VM → dual-boot → daily driver; what each rung genuinely validates about running Linux full-time, what it structurally cannot tell you, and the rollback/commitment cost of each."
topic_raw: "gradual linux migration from Windows (first testing the waters)."
tags: [linux, migration, windows, wsl2, dual-boot, live-usb, developer-workstation]
summary: "A rung-by-rung ladder from WSL2 to full switch, with what each rung proves, what it structurally hides, the go/no-go signal, and the cost of retreating."
citations: 31
reading_time_min: 9
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 519
issue: 14
---

> **Decision.** Climb **WSL2 → live USB (one evening) → external-SSD install → daily-drive-from-the-SSD → wipe-and-commit**, and *skip the VM and skip single-disk dual-boot entirely*. WSL2 and VMs answer only "does my software run" — they are structurally blind to suspend/resume, Wi-Fi, GPU, docking and battery, which is where switchers actually fail [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions)[[2]](https://www.xda-developers.com/wsl-great-run-linux-natively-instead/). An external SSD install is the only rung that is simultaneously **full-fidelity** (real kernel, real drivers, real hardware) and **zero-commitment** — "the ability to basically press delete, and the Linux system is gone" [[3]](https://dspdev.io/en/posts/portable-linux-ssd/). Single-disk dual-boot is the worst trade on the ladder: it costs you partition surgery, BitLocker risk and bootloader fragility [[4]](https://windowsforum.com/threads/dual-boot-windows-11-and-linux-mint-safe-production-ready-setup-guide.388453)[[5]](https://www.bleepingcomputer.com/news/microsoft/microsoft-confirms-august-updates-break-linux-boot-in-dual-boot-systems/) and buys you nothing an external disk doesn't.

## The structural fact the ladder is built on

A migration asks two independent questions, and almost every "test the waters" rung answers only one:

- **(A) Does my *software and workflow* survive?** — .NET SDK, Node/TS toolchain, Docker, editors, git, shell.
- **(B) Does my *hardware and desktop* survive?** — suspend/resume, Wi-Fi/Bluetooth, GPU + external monitors, docking, fingerprint, battery, scaling, the DE itself.

Everything virtualised (WSL2, VMs) answers (A) at near-perfect fidelity and (B) at **zero** fidelity — the guest sees synthesised hardware, not yours. Everything on bare metal answers (B) and, incidentally, (A). Practitioners converge on exactly this split: *"I would strongly recommend playing around with Linux in a virtual machine first, then a spare machine if possible"* — mikeymikec, AnandTech forums, Feb 2026 [[6]](https://forums.anandtech.com/threads/should-i-switch-from-windows-to-linux-looking-for-real%E2%80%91world-opinions.2633837/).

## The ladder

| # | Rung | Proves (high confidence) | Structurally cannot tell you |
|---|---|---|---|
| 0 | **WSL2** | The whole Linux *userland* dev loop: bash, apt, git, dotnet CLI, Node, Docker, systemd units [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions) | Anything hardware or desktop. Kernel modules, custom boot, raw NIC access are blocked; USB needs `usbipd` forwarding; networking is NAT, not your LAN [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions)[[2]](https://www.xda-developers.com/wsl-great-run-linux-natively-instead/) |
| 1 | **Live USB** | Real kernel on *your* silicon: does Wi-Fi/trackpad/display/printer enumerate at all. *"I put the live USB in…and it recognized everything. Wifi. Trackpad. Touchscreen. SD card reader. Brightness."* — notposting, Feb 2026 [[6]](https://forums.anandtech.com/threads/should-i-switch-from-windows-to-linux-looking-for-real%E2%80%91world-opinions.2633837/) | Anything needing a driver install or a kernel update — persistent live media chokes on initramfs/kernel updates, so proprietary NVIDIA modules can't be tested [[7]](https://forum.endeavouros.com/t/live-usb-ventoy-user-and-missing-persistence-please-support-this-request/70462). Also: long-run stability, suspend, battery, updates |
| 2 | **VM** | Distro/DE *taste-test*, package-manager muscle memory, .NET + TS build/test/debug end-to-end | Same blind spots as WSL2, plus it actively **misleads on desktop feel** — GPU passthrough needs a second GPU and clean IOMMU groups, so the VM's compositor performance is not your compositor performance [[8]](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF) |
| 3 | **External-SSD / second-drive install** | Effectively everything: real drivers, real suspend, real docking, real battery, real updates over weeks. Windows disk untouched [[9]](https://www.ghacks.net/2025/07/11/how-to-install-linux-on-an-external-ssd/) | Only USB-bus I/O ceiling and (if external) that you're carrying a dongle. Nothing else material |
| 4 | **Dual-boot (single disk)** | Nothing rung 3 doesn't, at strictly higher risk | — |
| 5 | **Spare machine / mini PC** | Homelab-adjacent Linux, server habits, a safe blast radius | Nothing about *your* workstation's hardware — different chipset, different Wi-Fi card, different everything |
| 6 | **Full switch** | The last 10%: the workflows you only notice when there's no escape hatch | — |

### Cost, duration and signals

| # | Rung | Spend | Setup | Stay | ✓ Advance when | ✗ Retreat when | Retreat cost |
|---|---|---|---|---|---|---|---|
| 0 | WSL2 | €0 | 15 min | 2–4 weeks | Your whole build/test/run loop is in WSL and you stop opening PowerShell | Toolchain has a hard Windows dependency (WPF/WinForms designers, IIS) [[10]](https://learn.microsoft.com/en-us/answers/questions/696985/wpf-and-winforms-on-macos-and-linux) | `wsl --unregister` — seconds |
| 1 | Live USB | €10 USB | 20 min | 1 evening | Wi-Fi + display + trackpad + external monitor all come up unaided | A core device is dead (Wi-Fi chipset, GPU won't init) → check [ubuntu.com/certified](https://ubuntu.com/certified) before spending more [[11]](https://ubuntu.com/certified) | Pull the stick and reboot — the session *"doesn't alter your computer's configuration in any way"* [[12]](https://ubuntu.com/tutorials/try-ubuntu-before-you-install) |
| 2 | VM | €0 | 30 min | 0–1 week (optional) | You've picked a distro + DE | — | Delete the VM file |
| 3 | External SSD | €60–120 (1 TB NVMe + enclosure) | 1–2 h | **4–8 weeks — this is the real trial** | You have gone 2–3 weeks without booting Windows for anything but one known app | Suspend/dock/battery is unfixable after two weekends of trying | Unplug. ⚠ Only if you protected the ESP (below) |
| 4 | Dual-boot | €0 (or a 2nd internal NVMe) | 1–2 h + risk | skip | — | — | Repartition + bootloader repair; hours, with data at stake |
| 5 | Spare mini PC | €150–300 used | 1 h | parallel, indefinite | — | — | It's a separate box; zero |
| 6 | Full switch | €0 | 2 h | forever | 30 consecutive days without a Windows boot | Only a hard business blocker | Reinstall Windows from USB: half a day + restore from backup |

## Rung mechanics and rollback

### 0 — WSL2: the free 80% of the developer question

WSL2 runs a real Microsoft-built Linux kernel in a managed VM, with systemd support and full syscall compatibility [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions). For .NET and TypeScript work this is genuinely representative: `dotnet build`, `dotnet test`, Docker, Node all behave as they will natively. WSLg even runs Linux GUI apps in Windows windows [[13]](https://www.mykolaaleksandrov.dev/posts/2025/08/wsl-complete-practical-guide/), and CUDA compute works — though NVIDIA still ships profilers as preview-only there [[14]](https://docs.nvidia.com/cuda/wsl-user-guide/index.html).

What it hides is not subtle. *"Anything that involves kernel modules, low-level system configuration, or hardware access is either limited or outright blocked"*; files under `/mnt/c` cross a network-style protocol and are slow; `vmmem` competes with Windows for RAM [[2]](https://www.xda-developers.com/wsl-great-run-linux-natively-instead/). Microsoft's own docs list no serial-port support, USB only via `usbipd`, and a NAT adapter that gives the distro a new IP on every restart — a real annoyance if your homelab expects LAN-visible services [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions).

**Keep files on the ext4 side, not `/mnt/c`.** The one true signal: you stop opening PowerShell for anything but launching WSL.

### 1 — Live USB: one evening, non-negotiable

Boot it *before* buying an SSD. Test the specific list: Wi-Fi association, Bluetooth pair, external monitor over the dock/USB-C, brightness keys, audio out + mic, webcam, trackpad gestures, and — if you can — close the lid. Cross-check the model against Canonical's certified list; certification runs 500+ compatibility tests per machine [[11]](https://ubuntu.com/certified)[[15]](https://certification.canonical.com/docs/programmes/desktop/).

The hard limit: you cannot install proprietary drivers or update the kernel on persistent live media — initramfs regeneration fails, which is exactly what an NVIDIA module needs [[7]](https://forum.endeavouros.com/t/live-usb-ventoy-user-and-missing-persistence-please-support-this-request/70462). So "GPU is stuck on nouveau in the live session" is **not** a no-go signal; "Wi-Fi chipset has no driver" is.

**Rollback: zero.** Nothing on your disk changes [[12]](https://ubuntu.com/tutorials/try-ubuntu-before-you-install).

### 2 — VM: optional, and easy to over-trust

A VM is a distro/DE *shopping trip*, not a trial. The trap is judging Wayland, GNOME animations or "does it feel snappy" from inside a VM: without PCI passthrough — which needs a spare GPU dedicated to the guest and cooperative IOMMU grouping [[8]](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF) — you are benchmarking a software rasteriser. If you already did rung 0, a VM adds little. Spend the evening on rung 1 instead.

### 3 — External SSD: the rung that does the actual work

This is where the ladder pays off. A full install on a separate disk gives real drivers, real power management, real update cycles — everything a VM fakes — while *"the idea with running Linux on a separate disk is the ability to basically press delete, and the Linux system is gone"* [[3]](https://dspdev.io/en/posts/portable-linux-ssd/). Installing to external media leaves the Windows install completely intact [[9]](https://www.ghacks.net/2025/07/11/how-to-install-linux-on-an-external-ssd/).

⚠ **The one trap that turns this rung irreversible:** installers happily write the bootloader to your *internal* ESP. Then unplugging the SSD doesn't undo anything — and worse, *"the EFI partition might be overwritten."* The fix is blunt: disable the internal drives in BIOS/UEFI before installing, so the installer can only see the external disk [[16]](https://medium.com/geekculture/installing-linux-ubuntu-20-04-on-an-external-portable-ssd-and-pitfalls-to-be-aware-of-388294e701b5). Do this and retreat really is "unplug it."

Buy USB 3.2 Gen2 / NVMe-in-enclosure, not a thumb drive — the OS is bottlenecked by the disk. Practitioner consensus on duration is that a couple of days is the floor, not the target: *"use it for at least a day or 2, a week if you have the time"* — Zepp, Feb 2026 [[6]](https://forums.anandtech.com/threads/should-i-switch-from-windows-to-linux-looking-for-real%E2%80%91world-opinions.2633837/). Real trials run longer. A documented 30-day dual-boot switch found the pattern most people report: days 1–3 smooth, **week 1 is the trough** (printer drivers, Bluetooth audio latency, missing apps), then *"by week two… I stopped fighting Linux and started understanding it"* [[17]](https://windowspost.com/linux-vs-windows-experience/). Budget 4–8 weeks so you cross at least two kernel updates and one distro point-release.

**What to log during this rung** (this list, not vibes, is your go/no-go evidence):

- Suspend/resume success rate over ~30 lid-closes.
- Idle battery drain vs your Windows baseline. Expect it to be *worse* out of the box — vendor Windows drivers are OEM-tuned — and to need TLP or `auto-cpufreq` tuning to close the gap [[18]](https://informatecdigital.com/en/Linux-vs-Windows:-Which-consumes-less-battery-power-on-laptops/)[[19]](https://linrunner.de/tlp/index.html).
- Dock/undock cycles with monitors + Ethernet + peripherals.
- On NVIDIA: flicker and frame pacing under Wayland. Explicit sync landed in the compositor stack and fixed the historic tearing/flickering class of bugs [[20]](https://linuxiac.com/wayland-nvidia-explicit-sync-support/) — verify it on *your* card rather than assuming.
- **Windows-boot tally.** The single best advance signal. When it hits zero for 2–3 weeks, you're done trialling.

### 4 — Single-disk dual-boot: the rung to skip

It's the default advice and it's the wrong one. What it adds over rung 3 is risk, not information:

- **Partition surgery under BitLocker.** Suspend or decrypt BitLocker before resizing, or you're in recovery-key territory [[4]](https://windowsforum.com/threads/dual-boot-windows-11-and-linux-mint-safe-production-ready-setup-guide.388453). Users report `NTFS_FILE_SYSTEM` bugchecks from BitLocker + Ubuntu dual-boot setups [[21]](https://learn.microsoft.com/en-gb/answers/questions/5543127/bitlocker-and-dual-boot-ubuntu-windows-11-error-nt).
- **Fast Startup** leaves NTFS hibernated; mounting it from Linux corrupts it. Must be disabled [[4]](https://windowsforum.com/threads/dual-boot-windows-11-and-linux-mint-safe-production-ready-setup-guide.388453).
- **Windows can brick your bootloader.** The August 2024 SBAT update produced *"Verifying shim SBAT data failed: Security Policy Violation"* on dual-boot machines Microsoft's own detection missed [[5]](https://www.bleepingcomputer.com/news/microsoft/microsoft-confirms-august-updates-break-linux-boot-in-dual-boot-systems/); the fix took roughly nine months to ship [[22]](https://news.itsfoss.com/microsoft-fixes-linux-dual-boot/). Assume this class of event recurs.
- **Clock skew** — Windows wants localtime, Linux wants UTC; you fix it once and forget it, but it's another paper cut [[23]](https://wiki.archlinux.org/title/System_time).
- **The behavioural failure.** Every switch costs a reboot, so you stop switching and stay in Windows [[24]](https://www.howtogeek.com/you-dont-need-to-dual-boot-anymore-theres-a-better-way/)[[25]](https://www.xda-developers.com/5-pitfalls-of-dual-booting-windows-and-linux-that-i-wasnt-prepared-for/). Red Squirrel's answer to this in Feb 2026 was to buy *"an off lease mini PC you buy off Ebay"* rather than fight the reboot tax [[6]](https://forums.anandtech.com/threads/should-i-switch-from-windows-to-linux-looking-for-real%E2%80%91world-opinions.2633837/).

If your machine takes a **second internal NVMe**, that's rung 3 with better I/O and the same reversibility — take it, and still disconnect/deselect the Windows disk during install. mikeymikec: *"I'd dual-boot with each OS having its own SSD"* [[6]](https://forums.anandtech.com/threads/should-i-switch-from-windows-to-linux-looking-for-real%E2%80%91world-opinions.2633837/).

### 5 — Spare machine: a parallel track, not a rung

A used mini PC is the cheapest way to build Linux *reflexes* (systemd, journalctl, Docker Compose, reverse proxies) and it dovetails with a homelab. But it proves nothing about your workstation's hardware, so it can't substitute for rung 3. Run it alongside, not instead.

### 6 — Full switch: wipe, don't dual-boot

Commit criterion: **30 consecutive days with zero Windows boots.** The pattern shows up repeatedly — Zepp *"wiped that drive"* after a few months of not needing Windows [[6]](https://forums.anandtech.com/threads/should-i-switch-from-windows-to-linux-looking-for-real%E2%80%91world-opinions.2633837/); one writeup admits to never booting the retained 800 GB Windows partition *once* [[26]](https://dev.to/lsroot/i-deleted-windows-and-my-bootloader-299f); Xe Iaso's January 2026 note opens with *"I haven't booted into Windows in over 3 months on my tower"* [[27]](https://xeiaso.net/notes/2026/year-linux-desktop/) (835 points, 639 comments on HN — the thread is a good sanity check on how contested this still is) [[28]](https://news.ycombinator.com/item?id=46471199).

Before wiping: image the Windows disk, verify a Windows install USB boots, and confirm you have any BitLocker recovery key. That reduces the retreat cost to ~half a day. Keep a Windows VM (not a dual-boot) for the one or two apps that never ported — WPF/WinForms designers and IIS have no Linux port and Microsoft has announced none [[10]](https://learn.microsoft.com/en-us/answers/questions/696985/wpf-and-winforms-on-macos-and-linux); Rider covers the cross-platform .NET IDE gap [[29]](https://www.jetbrains.com/rider/).

## A realistic calendar

| Weeks | Rung | Deliverable |
|---|---|---|
| 1–4 | WSL2, in parallel with normal work | Full dev loop runs in Linux userland; list of Windows-only dependencies |
| 4 (one evening) | Live USB | Hardware pass/fail sheet; distro chosen |
| 5 | Buy + install to external SSD (internal disks disabled in UEFI) | Bootable, reversible, full-fidelity Linux |
| 5–12 | Daily-drive from the SSD | Suspend/battery/dock log; Windows-boot tally trending to zero |
| 13 | Decide | Wipe and commit, or retreat by unplugging |

Total elapsed: **~3 months**, of which only weeks 5–12 involve real friction. Cash: one SSD.

## Context worth knowing

The tailwind is real but modest: Windows 10 support ended 14 October 2025 [[30]](https://www.aboutchromebooks.com/windows-11-adoption-rate-statistics/), and desktop Linux has climbed from ~2.8% (2022) to ~4.7% (2025) with projections near 6% by late 2026 [[31]](https://fosspost.org/linux-market-share-statistics/). That means more recent, better-tested hardware support — not that the hardware questions have gone away. They're still the ones the ladder exists to answer.
