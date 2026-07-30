---
title: "WSL2 as rung zero — what it proves, and the exact wall it hits"
date: 2026-07-30
depth: standard
format: md
topic: "WSL2 as rung zero, and its ceiling — how far WSL2 takes a .NET/TypeScript developer toward Linux, and exactly what it hides: no real desktop, /mnt/c filesystem performance, systemd, GPU, networking, hardware and drivers."
topic_raw: "gradual linux migration from Windows (first testing the waters)."
tags: [wsl2, linux-migration, dotnet, developer-workstation, windows]
summary: "WSL2 retires every userland risk in a Linux migration and none of the machine-ownership risks; here is where the line falls in 2026."
citations: 38
reading_time_min: 7
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 577
issue: 14
---

> **Decision.** Spend 3–6 months in WSL2 to retire the *userland* risk — bash, coreutils, apt, git, Docker, `dotnet`/`bun` on Linux — because that part is genuinely identical, and WSL2 now runs a real Microsoft-built Linux 6.18 kernel with systemd[[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions)[[2]](https://github.com/microsoft/WSL2-Linux-Kernel)[[3]](https://learn.microsoft.com/en-us/windows/wsl/wsl-config). Then stop: WSL2 cannot teach you a display server, a bootloader, drivers, suspend/resume, or package-manager-owns-the-machine, and it hides the single decision that dominates day-one pain — **your repos must live on ext4, not `/mnt/c`**, which is exactly where a Dropbox-synced Windows folder puts them[[4]](https://learn.microsoft.com/en-us/windows/wsl/filesystems)[[5]](https://github.com/webbertakken/wsl-filesystem-benchmark).

## What WSL2 genuinely validates

These transfer 1:1 to bare metal. If they work here, they work there.

| Capability | 2026 status in WSL2 | Source |
|---|---|---|
| Real Linux kernel + full syscall compat | Microsoft-built kernel, current branch `linux-msft-wsl-6.18.y`, serviced by Windows Update | [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions) [[2]](https://github.com/microsoft/WSL2-Linux-Kernel) |
| bash / coreutils / apt / man pages | Unmodified distro userland | [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions) |
| systemd | ✓ since WSL 0.67.6; `[boot] systemd=true` in `/etc/wsl.conf`, then `wsl --shutdown` | [[6]](https://devblogs.microsoft.com/commandline/systemd-support-is-now-available-in-wsl/) [[3]](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) |
| Docker / containers | ✓ full syscall compat; native `wslc` container runtime in public preview since 29 Jun 2026 (WSL 2.9.3), GA targeted autumn 2026 | [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions) [[7]](https://devblogs.microsoft.com/commandline/wsl-container-is-now-available-for-public-preview/) |
| `dotnet` CLI + debugging on Linux | ✓ Visual Studio ships a WSL launch profile; the runtime is the real linux-x64 runtime | [[8]](https://learn.microsoft.com/en-us/visualstudio/debugger/debug-dotnet-core-in-wsl-2?view=vs-2022) |
| GPU compute (CUDA) | ✓ via GPU-PV and `/dev/dxg`; `nvidia-smi` works with only the **Windows** driver installed | [[9]](https://developer.nvidia.com/cuda/wsl) [[10]](https://www.cicoria.com/cuda-on-wsl2-how-it-works-how-to-set-it-up-and-a-rust-tui-to-prove-it/) |
| Linux GUI apps (WSLg) | ✓ Wayland + XWayland, Weston with an RDP backend, PulseAudio in/out, GPU accel via Mesa d3d12 | [[11]](https://github.com/microsoft/wslg) |
| Raw CPU/IO ceiling | Phoronix (15 Sep 2025, Ryzen 9 9950X3D, Ubuntu 24.04 vs bare metal): ~10–15% CPU overhead, up to ~20% on I/O | [[12]](https://www.phoronix.com/review/windows-11-wsl2-2025) [[13]](https://www.webpronews.com/microsoft-wsl2-on-windows-11-25h2-10-20-overhead-in-benchmarks/) |

WSL itself went open source at Build 2025 (MIT), so the seams are now inspectable: `wsl.exe`, `wslservice.exe`, the Linux-side `init`/`gns`/`localhost` daemons and the plan9 server[[14]](https://blogs.windows.com/windowsdeveloper/2025/05/19/the-windows-subsystem-for-linux-is-now-open-source/)[[15]](https://learn.microsoft.com/en-us/windows/wsl/opensource) — [microsoft/WSL](https://github.com/microsoft/WSL) ⭐ 33k (Jul 2026)[[16]](https://github.com/microsoft/WSL). Still closed: `lxcore.sys` (WSL1) and `p9rdr.sys`/`p9np.dll`, the `\\wsl.localhost` redirector[[15]](https://learn.microsoft.com/en-us/windows/wsl/opensource).

## The filesystem cliff — the number that decides your setup

Microsoft's own guidance: "We recommend against working across operating systems with your files… store your files in the WSL file system if you are working in a Linux command line"[[4]](https://learn.microsoft.com/en-us/windows/wsl/filesystems). The mechanism is a plan9 file server in `wslservice.exe` reached over a Hyper-V socket, one round-trip per operation[[17]](https://wsl.dev/technical-documentation/drvfs/).

| Operation | WSL ext4 (VHDX) | WSL → `/mnt/c` | Windows → `\\wsl$` |
|---|---|---|---|
| Sequential read 1 MB | 2393 MB/s | 86 MB/s | 156 MB/s |
| Sequential write 100 MB | 2827 MB/s | 294 MB/s | 10 MB/s |
| Random read | 24 554 IOPS | 725 IOPS | 1271 IOPS |
| Directory traversal | 343 338 files/s | 13 561 files/s | 28 045 files/s |

Source: [wsl-filesystem-benchmark](https://github.com/webbertakken/wsl-filesystem-benchmark) ⭐ 3 (Jul 2026)[[5]](https://github.com/webbertakken/wsl-filesystem-benchmark). Random read across the boundary is **~34× slower**; Windows→WSL writes land under 1% of native. The canonical bug, [microsoft/WSL#4197](https://github.com/microsoft/WSL/issues/4197), reports 40.4 MB/s on `/mnt` under WSL2 vs 442 MB/s under WSL1 and is **still open**[[18]](https://github.com/microsoft/WSL/issues/4197).

⚠ **2026 change:** virtiofs is now selectable (`virtiofs=true` under `[wsl2]`, kernel 6.18.26.3-1+), replacing plan9 for `/mnt/*`; a 27 May 2026 PR gave each virtio device its own DMA pool to remove the last SWIOTLB contention point. It is still opt-in — plan9 remains the default[[19]](https://www.boxofcables.dev/wsl2-per-device-swiotlb-pools-for-virtiofs-and-virtioproxy/)[[17]](https://wsl.dev/technical-documentation/drvfs/). HN reports a Hugo build at 50 s on native ext4, 75 s on virtiofs, and "3–5 m or more" on plan9 — virtiofs closes most of the gap but does not close it[[20]](https://news.ycombinator.com/item?id=48403377).

**The Dropbox trap.** A repo under `C:\Users\you\Dropbox\...` is doubly penalised: every `git status`, `dotnet build` and `node_modules` walk pays the cross-OS tax above, *and* the sync client indexes tens of thousands of dependency files it cannot exclude per-directory[[21]](https://medium.com/@bozzified/solving-painful-syncing-of-node-modules-when-using-dropbox-or-google-drive-a77c2ab0c97c). The fix is not tuning — it is `git clone` into `~/code` and letting the remote be the sync mechanism. This is a rehearsal for bare metal, where `/mnt/c` does not exist at all.

## What WSL2 structurally hides

Every row here is a real migration risk that WSL2 **cannot** retire.

| Hidden layer | What WSL2 substitutes | Why it doesn't count |
|---|---|---|
| Display server | WSLg: Weston + RDP remoting *individual windows* onto the Windows desktop | You never pick Wayland vs X11, never configure a compositor, never hit fractional-scaling or multi-monitor bugs. Running a real DE needs an XRDP hack; GNOME Shell needs 3D accel XRDP can't give, and KDE Plasma 6.8 is Wayland-only[[22]](https://wsl-ui.octasoft.co.uk/blog/wsl2-ubuntu-desktop-xrdp)[[23]](https://gist.github.com/tdcosta100/e28636c216515ca88d1f2e7a2e188912) |
| GPU drivers | `/dev/dxg` + stub `libcuda.so`/`nvidia-smi` in `/usr/lib/wsl/lib`, forwarding to the **Windows** driver | Installing a real Linux GPU driver *breaks* it. You never do DKMS, kernel-module signing, or a Nouveau→proprietary switch[[10]](https://www.cicoria.com/cuda-on-wsl2-how-it-works-how-to-set-it-up-and-a-rust-tui-to-prove-it/) |
| Kernel ownership | Microsoft-built kernel, serviced by Windows Update | No `apt`-owned kernel, no headers/module rebuild, no bad-kernel rollback[[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions) |
| Bootloader / firmware | none — VM boot | No GRUB, no Secure Boot, no UEFI, no "it doesn't boot" recovery drill |
| Suspend / resume | none — Windows sleeps, the VM doesn't notice | Surfaces only as clock skew: "the VM for the WSL Linux distro doesn't have its clock updated when the host resumes" — fix is `sudo hwclock -s`[[24]](https://stuartleeks.com/posts/fixing-clock-skew-with-wsl-2/) |
| Battery / thermal / power mgmt | Windows owns all of it | TLP, `powertop`, CPU governors, lid actions: untested |
| Peripherals | USB only via [usbipd-win](https://github.com/dorssel/usbipd-win) ⭐ 6.0k (Jul 2026), attach-by-busid, exclusive to WSL while attached; **serial ports unsupported** | No udev-rules-for-a-real-device, no printer/scanner/webcam/fingerprint reality check[[25]](https://learn.microsoft.com/en-us/windows/wsl/connect-usb)[[26]](https://github.com/dorssel/usbipd-win)[[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions) |
| Networking | NAT by default: WSL2 gets its own virtual adapter and a unique IP that changes on restart; LAN exposure needs `netsh portproxy`. `mirrored` mode fixes most of it but IPv6 `::1` is unsupported and it silently falls back to NAT on Windows builds lacking the feature | You never touch NetworkManager/systemd-networkd, `nmcli`, or Wi-Fi/VPN driver reality[[27]](https://learn.microsoft.com/en-us/windows/wsl/networking)[[28]](https://github.com/microsoft/WSL/issues/13068) |
| Init / service ownership | systemd runs, but inside a distro cgroup managed by WSL | `snapd` still doesn't work[[29]](https://github.com/microsoft/WSL/issues/9026); systemd ≥ 256 needed plain cgroup v2 support that WSL's hybrid hierarchy lacked[[30]](https://github.com/microsoft/WSL/issues/11857) |

## 2026 sharp edges worth knowing before you start

- **Memory ballooning.** The Linux page cache grows and Windows can't see it as reclaimable — Microsoft's own example shows 2 GB attributed to the VM in Windows while Linux is using 50 MB[[31]](https://devblogs.microsoft.com/commandline/memory-reclaim-in-the-windows-subsystem-for-linux-2/). `autoMemoryReclaim` now defaults to `dropCache` (was previously off); `gradual` is the gentler option[[3]](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).
- **VHDX only grows.** Default max is 1 TB and deleting files does not shrink the file. Enable `sparseVhd=true` (or `wsl --manage <distro> --set-sparse true`) — ⚠ once sparse, `Optimize-VHD` refuses to compact it, so you're committed to automatic reclaim[[3]](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)[[32]](https://www.ashn.dev/blog/2025-08-14-how-to-fix-wsl2-disk-space-bloat.html)[[33]](https://learn.microsoft.com/en-us/answers/questions/1526083/in-wsl2-with-sparse-vhd-the-storage-usage-does-not).
- **inotify does not cross the boundary.** File-watching on `/mnt/c` doesn't fire, so Vite/Angular/`dotnet watch` HMR silently dies; the workaround is polling — or, correctly, moving the repo to ext4[[34]](https://github.com/microsoft/WSL/issues/5424).
- **Case sensitivity is inverted per-tree.** Windows drives mount case-**insensitive** by default (`case=off`); ext4 is case-sensitive. Mixed-case files created in WSL become unopenable from Windows tools, and `git config core.ignorecase` disagreements produce phantom conflicts[[35]](https://learn.microsoft.com/en-us/windows/wsl/case-sensitivity).
- **cgroup v1 is gone.** WSL now isolates each distro's systemd into its own cgroup v2 hierarchy; `IsolateDistroCgroup` (default `true`) is the escape hatch for legacy v1 workloads[[36]](https://github.com/microsoft/WSL/pull/40519)[[37]](https://www.neowin.net/news/microsoft-makes-windows-subsystem-for-linux-more-stable-with-architecture-tweak/).
- **The 8-second rule.** Config edits need the VM fully stopped (`wsl --shutdown`), not just the terminal closed[[3]](https://learn.microsoft.com/en-us/windows/wsl/wsl-config).

A sane `%UserProfile%\.wslconfig` baseline for a 32 GB dev box:

```ini
[wsl2]
memory=16GB
processors=8
networkingMode=mirrored
virtiofs=true

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
hostAddressLoopback=true
```

`hostAddressLoopback` and `ignoredPorts` only apply under `mirrored`[[3]](https://learn.microsoft.com/en-us/windows/wsl/wsl-config); `virtiofs` needs kernel 6.18.26.3-1+[[19]](https://www.boxofcables.dev/wsl2-per-device-swiotlb-pools-for-virtiofs-and-virtioproxy/).

## Verdict: which risks WSL2 retires

| Migration risk | Retired by WSL2? |
|---|---|
| "Will my .NET/TS toolchain build and debug on Linux?" | ✓ |
| "Can I live in bash instead of PowerShell?" | ✓ |
| "Do my Docker/compose/homelab deploy scripts work?" | ✓ |
| "Will my ML/CUDA work run?" | ✓ (compute only) |
| "Can I package-manage my own machine?" | ✗ |
| "Will my laptop suspend, wake, and hold charge?" | ✗ |
| "Will my GPU/Wi-Fi/fingerprint/dock work?" | ✗ |
| "Which DE/compositor do I actually want?" | ✗ |
| "Can I recover an unbootable system?" | ✗ |

**Stop learning from WSL2 when** your friction stops being "how do I do X in Linux" and becomes "I want Linux to *be* the machine" — the point where WSL2 mistakes are still trivially unwound but the questions it can answer have run out[[38]](https://www.vecosys.com/wsl2-vs-dual-boot-learning-linux/). Concretely: when you have (a) all repos on ext4 with no `/mnt/c` dependency, (b) systemd units you wrote yourself, and (c) a dotfiles repo you can `git clone` onto a fresh box. At that point the next rung is a machine WSL2 can't simulate — and everything remaining on the ✗ list has to be learned on real hardware.
