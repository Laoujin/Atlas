---
title: "Escape hatches for the leftovers: Wine, a VM, passthrough, or just keep the partition"
date: 2026-07-30
depth: ceo
format: md
topic: "Escape hatches for the Windows software that has no Linux replacement (2026): Wine/Bottles/CrossOver, a Windows VM, GPU passthrough, and cloud/RDP — which hatch fits which kind of leftover, and what each costs."
topic_raw: "can you check what software I have on my system installed (Windows) and then do a comparison with what I could replace that software with once I throw away Windows for Linux? (for those that are not available on Linux right away)"
tags: [linux-migration, wine, virtualization, vfio, rdp]
summary: "Wine for single-window utilities, a local Windows VM for Visual Studio and SSMS, RDP for the corporate cluster — and no GPU passthrough on a muxless Legion."
citations: 16
reading_time_min: 4
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 336
issue: 13
---

> **Decision.** Reach for **Wine via [Bottles](https://usebottles.com)** first — it costs nothing, and the WineHQ AppDB rating tells you in minutes whether an app is the single-window Win32/.NET kind that just works [[1]](https://www.winehq.org/) [[2]](https://wiki.winehq.org/AppDB_Rating_Definitions). If it needs a Windows *service*, *filter driver*, or *Explorer integration*, skip to a **local Windows VM** — KVM/virt-manager, or VMware Workstation Pro, free for personal *and* commercial use since Broadcom's Nov 2024 change [[3]](https://knowledge.broadcom.com/external/article/368667/download-and-license-vmware-desktop-hype.html). **Do not** attempt dGPU passthrough on this laptop: muxless Optimus caps the guest at 640×480 with no Optimus handoff [[4]](https://lantian.pub/en/article/modify-computer/laptop-intel-nvidia-optimus-passthrough.lantian/). And when the leftover list is down to three things you touch monthly, **keeping a 120 GB Windows partition beats engineering any hatch at all**.

## Which hatch for which leftover

| Kind of leftover (from this inventory) | Best hatch | Why | Cost / effort |
|---|---|---|---|
| Single-window Win32 / older-.NET utility — IrfanView, Paint.NET, PDFtk, Beyond Compare | ✓ Wine in [Bottles](https://usebottles.com) ⭐ 8.6k (Jul 2026) [[5]](https://github.com/bottlesdevs/Bottles) | Wine 11 is the stable branch and this is its best-supported class [[1]](https://www.winehq.org/) | Free, ~1 h per app |
| Desktop-shell mods — Stardock Fences, DisplayFusion, AutoHotkey, ShareX, Ditto, Beyond Compare shell ext | ✗ No hatch | They hook *Explorer* and global input; a Wine prefix has no host desktop to integrate with. Replace natively or drop | Free, but it is a behaviour change |
| Firmware / kernel-driver tools — Lenovo Vantage, XTU, JBL QuantumENGINE, X-Rite Color Assistant, SENetFilter, Sandboxie | ✗ Wine → ⚠ dual boot | These are drivers, not applications. Wine has no kernel-mode driver stack | Free; boot Windows twice a year for firmware |
| Visual Studio Community 2026 + ReSharper | Windows VM (KVM/virt-manager or VMware) | Wine cannot install or usefully run Visual Studio [[6]](https://forums.linuxmint.com/viewtopic.php?t=402070) `(forum)` | Windows licence ≈$199 retail, one instance per licence [[7]](https://learn.microsoft.com/en-us/answers/questions/3846682/do-i-need-to-purchase-a-license-to-create-some-vir) + ~80 GB disk |
| SQL Server Management Studio 20 | ⚠ Wine, with binary patches | Connect, Object Explorer, Query Editor, Server Properties work; Azure connection types, SSIS/SSAS/SSRS designers, Always On dialogs and Tuning Advisor do not [[8]](https://github.com/WilhelmZA/ssms-on-wine) ⭐ 1 (Jul 2026) | Free, ~2 h, fragile — a 1-star hobby project |
| Office desktop apps + OneNote | Web/M365, else [WinApps](https://github.com/winapps-org/winapps) ⭐ 15.7k (Jul 2026) over FreeRDP [[9]](https://github.com/winapps-org/winapps) | Seamless single-window RDP beats staring at a whole VM desktop for occasional use | Free on top of a Windows box/VM you already have |
| WatchGuard SSL VPN + Check Point Harmony SASE — i.e. the Office + VPN + SSMS work cluster | Corporate VDI / RDP to a managed Windows box | VPN clients ship filter drivers; making it the employer's compliance problem is the cheapest hatch. Windows 365 list price fell 20% on 1 May 2026 to $28–56/user/mo [[10]](https://www.computerworld.com/article/1614752/windows-365-costs-how-much.html) `(news)` | Ideally €0 if employer-provided |
| Power Automate Desktop | Windows VM, or migrate flows to cloud | UI automation needs a real Windows desktop to drive | Rides on the VM you already built |
| Fall Guys (Easy Anti-Cheat) | ⚠ Proton GE / Experimental | Rated *Running*, not *Supported*; 55% of 1,166 tracked anti-cheat titles are outright broken [[11]](https://areweanticheatyet.com/) | Free, expect breakage per game patch |

## Hatch economics

- **Wine / Bottles / [Lutris](https://lutris.net) ⭐ 10.1k (Jul 2026) [[12]](https://github.com/lutris/lutris)**: free. [CrossOver](https://www.codeweavers.com) sells a support contract and pre-baked bottles, not different Wine — $74 for CrossOver+, $34/yr renewal, $494 lifetime [[13]](https://www.codeweavers.com/blog/balfour/2025/10/9/dont-panic-how-crossover-licenses-work).
- **VM plumbing**: on QEMU/SPICE, budget time for installing the SPICE guest tools for bidirectional clipboard, plus `phodav`/`spice-webdavd` inside the guest before guest→host file sharing works [[14]](https://itsfoss.com/share-files-gnome-boxes/). GNOME Boxes is the same stack with fewer knobs; virt-manager exposes the settings you will need.

## Don't bother

- **dGPU VFIO passthrough on this Legion.** Muxless means the NVIDIA chip drives no panel: guest resolution caps at 640×480, and NVIDIA's driver refuses to form Optimus with a virtual iGPU, so 3D work never migrates to the dGPU. Setup needs custom UEFI firmware, vBIOS extracted from a BIOS update, and ACPI patching; the guide's own author says do it "purely for the fun of tinkering… not for anything important" [[4]](https://lantian.pub/en/article/modify-computer/laptop-intel-nvidia-optimus-passthrough.lantian/). A Legion 5 Pro attempt bound the dGPU and got video, but Windows never recognised the RTX 3060M as NVIDIA hardware and the driver refused to load [[15]](https://forums.developer.nvidia.com/t/trying-to-get-discrete-laptop-gpu-running-in-qemu-kvm-windows/221706) `(forum)`.
- **virtio-gpu/Venus for a GUI-heavy Windows guest.** Venus Vulkan over virtio-gpu is mature for *Linux* guests; the Windows-guest OpenGL/Direct3D driver is still work in progress [[16]](https://wiki.archlinux.org/title/QEMU/Guest_graphics_acceleration). For Visual Studio, use VMware's mature Windows guest driver [[3]](https://knowledge.broadcom.com/external/article/368667/download-and-license-vmware-desktop-hype.html) or RDP into the VM rather than fighting the display path.
- **Wine for anything with a service or filter driver** — the Lenovo / JBL / X-Rite / VPN cluster. No amount of `winetricks` adds a kernel.
