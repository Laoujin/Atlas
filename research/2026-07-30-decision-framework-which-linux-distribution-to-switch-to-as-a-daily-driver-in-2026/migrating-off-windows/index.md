---
title: "Windows to Linux in 2026: what crosses over, what doesn't, and how to stage the switch"
date: 2026-07-30
depth: survey
format: md
topic: "Migrating off Windows to Linux in 2026 — what actually crosses over and what doesn't. Research: Microsoft 365/Office (web version limits, LibreOffice/OnlyOffice/WPS fidelity for real .docx/.xlsx with macros), Outlook and Teams on Linux (PWA vs native vs third-party clients, screen-share and calendar caveats), Adobe apps and the realistic substitutes, Windows-only developer and admin tools for a .NET developer (Visual Studio proper vs Rider/VS Code, SQL Server Management Studio vs Azure Data Studio/DataGrip/DBeaver, IIS-bound tooling, PowerShell 7 on Linux gaps, Windows-only vendor VPN/banking/eID tooling — including Belgian eID card readers), and the escape hatches (Wine/Bottles/Proton for productivity apps, a Windows VM under KVM/virt-manager or VirtualBox with GPU passthrough tradeoffs, Windows 365/cloud PC). Then the switch mechanics: dual-boot vs full wipe (including the shared-EFI, BitLocker, fast-startup and clock-skew pitfalls), keeping a Windows install for the one app that never ports, moving data off NTFS drives, migrating dotfiles/config/SSH-GPG keys/browser profiles, and how WSL2 experience does and does not transfer to a native Linux desktop. Deliverable: an inventory-and-substitute table plus a staged migration plan (test on live USB → dual-boot → commit) with the checkpoints that decide whether the switch sticks."
topic_raw: "I'm going to make the switch to Linux. The question is which Linux version should I pick? there are so many :D"
tags: [linux, migration, dotnet, microsoft-365, dual-boot, wine, virtualization, belgium]
summary: "Almost everything a .NET developer does crosses to Linux in 2026 — the four things that don't are desktop Office with VBA, a native Outlook with working calendar, WPF/WinForms designers, and Windows-only compliance tooling; keep a Windows partition for those and stage the switch through live USB and dual-boot before committing."
citations: 44
reading_time_min: 15
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 691
issue: 11
---

> **Decision.** For a .NET/TypeScript developer, the *toolchain* crosses over almost completely in 2026 — Rider, VS Code + MSSQL extension, SQL Server in Docker, PowerShell 7 all run natively [[1]](https://learn.microsoft.com/en-us/sql/tools/whats-happening-azure-data-studio)[[2]](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/quickstart-install-docker?view=sql-server-ver17). What does **not** cross is the *Microsoft office-worker layer*: there is no desktop Office for Linux, so no VBA and no offline Excel [[3]](https://learn.microsoft.com/en-ca/answers/questions/5891967/microsoft-office-on-linux)[[4]](https://learn.microsoft.com/en-us/answers/questions/5825752/office-365-web-vs-computer-program); no native Outlook with a working calendar [[5]](https://blog.thunderbird.net/2025/11/thunderbird-adds-native-microsoft-exchange-email-support/); no WPF/WinForms designers [[6]](https://www.jetbrains.com/rider/compare/rider-vs-visual-studio/); and, in Belgium specifically, eID works but breaks the moment your browser is a Snap or Flatpak [[7]](https://eid.belgium.be/en/faq/why-it-not-possible-use-eid-software-snap-andor-flatpak). Keep a small Windows partition for exactly those, and stage the move: live USB → dual-boot for 4 weeks → commit.

## 1. Inventory and substitutes

Rated by what actually happens when you try, not by feature-list parity. ✓ = drop-in. ⚠ = works with a caveat you will hit. ✗ = does not cross; needs an escape hatch.

### Office and documents

| Windows tool | Linux substitute | Verdict |
|---|---|---|
| Word / Excel / PowerPoint (desktop) | [Microsoft 365 for the web](https://www.microsoft365.com) — the only officially supported route; there is no native Linux client [[3]](https://learn.microsoft.com/en-ca/answers/questions/5891967/microsoft-office-on-linux) | ⚠ no VBA, no add-ins, no offline, degrades on large workbooks [[4]](https://learn.microsoft.com/en-us/answers/questions/5825752/office-365-web-vs-computer-program) |
| .docx / .xlsx round-trip fidelity | [OnlyOffice Desktop Editors](https://www.onlyoffice.com/desktop.aspx) ⭐ 5.1k — OOXML is its *native* internal format, not an import filter [[8]](https://itsfoss.com/comparison/libreoffice-vs-onlyoffice/)[[9]](https://github.com/ONLYOFFICE/DesktopEditors) | ✓ best fidelity for files you exchange with Windows colleagues |
| .odf-first editing, PDF, everything else | [LibreOffice](https://www.libreoffice.org) | ✓ but OOXML is a conversion, so complex styling and layout drift [[8]](https://itsfoss.com/comparison/libreoffice-vs-onlyoffice/) |
| Excel VBA macros | LibreOffice `Tools ▸ Macros ▸ Convert Microsoft Office Macros`, plus the `Option VBASupport 1` compatibility mode [[10]](https://help.libreoffice.org/latest/en-US/text/sbasic/shared/vbasupport.html) | ✗ partial by design — anything touching the Excel object model, ActiveX or `Application.` internals fails. OnlyOffice doesn't even try: its macros are JavaScript [[8]](https://itsfoss.com/comparison/libreoffice-vs-onlyoffice/) |
| Power Query / Power Pivot | none | ✗ no equivalent; move the ETL into Python/pandas or SQL, which you already write |

**Practical rule:** documents you *author* → OnlyOffice. Documents with macros or Power Query that someone else owns → Windows VM or a Cloud PC. Don't try to port a business-critical macro workbook; it is the single most common reason a switch reverses.

### Communication

| Windows tool | Linux substitute | Verdict |
|---|---|---|
| Teams desktop | Teams **PWA** — Microsoft retired the Linux Electron client in December 2022 and made the PWA the supported path [[11]](https://uwaterloo.ca/microsoft-365/blog/teams-linux-retirement-teams-desktop-app-linux-and-new)[[12]](https://techcommunity.microsoft.com/blog/microsoftteamsblog/microsoft-teams-progressive-web-app-now-available-on-linux/3669846) | ⚠ PWA install is Edge/Chrome only — not Firefox [[12]](https://techcommunity.microsoft.com/blog/microsoftteamsblog/microsoft-teams-progressive-web-app-now-available-on-linux/3669846) |
| Teams screen sharing | PipeWire + `xdg-desktop-portal` under Wayland | ⚠ **the** recurring Linux-Teams failure. Missing/misconfigured portals → the share picker is empty or the browser crashes; Wayland-vs-Xorg session choice changes the outcome [[13]](https://learn.microsoft.com/en-us/answers/questions/4415327/fixed-screen-sharing-on-ubuntu-is-not-working-team). Test this on day one, not week three |
| Outlook (mail) | [Thunderbird](https://www.thunderbird.net) 145+ speaks EWS natively with OAuth2 for M365 [[5]](https://blog.thunderbird.net/2025/11/thunderbird-adds-native-microsoft-exchange-email-support/)[[14]](https://www.theregister.com/2025/11/20/thunderbird_microsoft_exchange_support/) | ⚠ **and on a clock** — see below |
| Outlook (calendar + contacts) | nothing native | ✗ Thunderbird's Exchange support is mail-only; calendar and address book are "on the roadmap", Graph is "not yet implemented" [[5]](https://blog.thunderbird.net/2025/11/thunderbird-adds-native-microsoft-exchange-email-support/). Use Outlook Web |

⚠ **The EWS trap.** Thunderbird's native Exchange support rides on EWS, and Microsoft starts blocking EWS in Exchange Online on **1 October 2026**, with full retirement in **April 2027**; F1/F3/Kiosk licences were cut off from 1 March 2026 [[15]](https://techcommunity.microsoft.com/blog/exchange/introducing-ewsallowedappids-preparing-for-the-final-phase-of-ews-retirement/4529471). Thunderbird's Graph backend is not shipped yet [[5]](https://blog.thunderbird.net/2025/11/thunderbird-adds-native-microsoft-exchange-email-support/). If your mail is in M365, plan on **Outlook Web as the primary client** and treat Thunderbird as a bonus that may stop working inside 12 months. On-premises Exchange is unaffected [[15]](https://techcommunity.microsoft.com/blog/exchange/introducing-ewsallowedappids-preparing-for-the-final-phase-of-ews-retirement/4529471).

### .NET and database tooling

| Windows tool | Linux substitute | Verdict |
|---|---|---|
| Visual Studio (Windows-only) | [JetBrains Rider](https://www.jetbrains.com/rider/) — runs on Linux, ships .NET 10 / C# 14 support | ✓ for ASP.NET, libraries, tests, containers [[6]](https://www.jetbrains.com/rider/compare/rider-vs-visual-studio/); free for non-commercial use, commercial licence still required for work [[16]](https://sales.jetbrains.com/hc/en-gb/articles/18950890312210-The-free-non-commercial-licensing-FAQ) |
| VS designers for WPF/WinForms | none | ✗ Rider edits XAML but has no visual designers [[6]](https://www.jetbrains.com/rider/compare/rider-vs-visual-studio/); WPF/WinForms apps *only run* on Windows regardless [[17]](https://learn.microsoft.com/en-us/answers/questions/696985/wpf-and-winforms-on-macos-and-linux). `EnableWindowsTargeting=true` lets CI *build* them on Linux — it does not let you run or design them |
| WPF app you must keep maintaining | [Avalonia](https://avaloniaui.net/) for new work; [Avalonia XPF](https://docs.avaloniaui.net/xpf/getting-started) for lifting an existing WPF app cross-platform | ⚠ XPF is commercial and a port, not a recompile |
| Azure Data Studio | **retired 28 February 2026** — no updates, no security fixes [[1]](https://learn.microsoft.com/en-us/sql/tools/whats-happening-azure-data-studio) | ✗ do not build on it |
| SSMS query/schema work | VS Code + [MSSQL extension](https://marketplace.visualstudio.com/items?itemName=ms-mssql.mssql): schema compare, schema designer, DACPAC/BACPAC, Query Profiler, SQL projects open unconverted [[1]](https://learn.microsoft.com/en-us/sql/tools/whats-happening-azure-data-studio) | ✓ this is Microsoft's own designated replacement |
| SSMS SQL Server Agent + full admin | none — Microsoft explicitly keeps Agent and "classic administration" in SSMS, which is Windows-only [[1]](https://learn.microsoft.com/en-us/sql/tools/whats-happening-azure-data-studio) | ✗ **the real SQL gap.** Job scheduling → RDP, VM, or T-SQL against `msdb` |
| Multi-engine SQL client | [DBeaver](https://dbeaver.io), [DataGrip](https://www.jetbrains.com/datagrip/), [Beekeeper Studio](https://www.beekeeperstudio.io) — all cross-platform [[18]](https://www.beekeeperstudio.io/blog/sql-server-management-studio-alternatives-free) | ✓ |
| Local SQL Server instance | SQL Server in Docker — supported on Linux hosts with x86-64 CPUs [[2]](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/quickstart-install-docker?view=sql-server-ver17) | ✓ **better than Windows.** ⚠ x86-64 only; ARM and emulation (QEMU/Rosetta/Prism) are untested and unsupported [[2]](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/quickstart-install-docker?view=sql-server-ver17) |
| IIS + `inetmgr` | Kestrel behind nginx/Caddy, or just your existing Docker Compose | ✓ you already run Coolify; this is the direction the platform moved anyway |
| PowerShell 5.1 scripts | PowerShell 7 runs natively on Linux | ⚠ `Get-WmiObject` was removed in PS 6+, and the CIM cmdlets that replaced it were never ported to non-Windows [[19]](https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/07-working-with-wmi). Anything WMI/CIM, registry, `ActiveDirectory`, or COM stays on Windows |
| .NET Framework 4.x projects | none | ✗ Framework targets don't build or run on Linux. Legacy Framework work = Windows VM |

### Creative and compliance

| Windows tool | Linux substitute | Verdict |
|---|---|---|
| Photoshop | [Photopea](https://www.photopea.com) (browser, best PSD fidelity of the free tools), [GIMP](https://www.gimp.org), [Krita](https://krita.org) for illustration [[20]](https://www.xda-developers.com/forget-gimp-krita-photopeafree-editor-closest-photoshop-replacement/) | ⚠ fine for dev-adjacent work, not for a print/agency workflow |
| Affinity Photo/Designer/Publisher | Canva made Affinity free and unified in 2025 [[21]](https://en.wikipedia.org/wiki/Affinity_(software)); Linux is community-only — an unofficial Affinity v3 AppImage that bundles Wine [[22]](https://www.omgubuntu.co.uk/2026/01/run-affinity-linux-ubuntu-appimage), or [AffinityOnLinux](https://github.com/seapear/AffinityOnLinux) ⭐ 1.7k via Bottles/Lutris/Heroic [[23]](https://github.com/seapear/AffinityOnLinux) | ⚠ unsupported by the vendor; treat as a nice-to-have |
| Premiere / After Effects / Acrobat Pro | DaVinci Resolve (native Linux) / nothing / Okular+`qpdf` | ✗ for AE and Acrobat Pro's forms & redaction |
| Corporate SSL VPN | [OpenConnect](https://www.infradead.org/openconnect/) covers Cisco AnyConnect, Palo Alto GlobalProtect, Fortinet FortiGate and F5 protocols [[24]](https://www.infradead.org/openconnect/); [GlobalProtect-openconnect](https://github.com/yuezk/GlobalProtect-openconnect) ⭐ 2.2k adds SSO/MFA/YubiKey with a GUI [[25]](https://github.com/yuezk/GlobalProtect-openconnect) | ⚠ works, but it's a reimplementation — if your security team requires the vendor client with posture checking, you lose |
| Belgian eID card reader | Official `eid-mw` + `eid-viewer` packages via `eid-archive`, supported on Debian 12/13, Ubuntu 24.04/26.04 LTS, Mint 21.3/22.3, Fedora 43/44, RHEL 10 + Rocky/Alma, openSUSE Leap 16 [[26]](https://eid.belgium.be/en/linux-eid-software-installation) | ✓ officially supported — **on those distros** |
| eID in the browser | Firefox/Chrome loading `libbeidpkcs11.so` | ✗ **Belgian-specific landmine:** eID cannot work with a Snap or Flatpak browser — sandbox confinement blocks the PKCS#11 module [[7]](https://eid.belgium.be/en/faq/why-it-not-possible-use-eid-software-snap-andor-flatpak). On Ubuntu, Firefox is a Snap by default, so eID is broken out of the box. Fix = install a `.deb`/native browser |
| Banking / itsme | itsme activates via your bank app, or with eID + card reader if the bank doesn't offer in-app activation [[27]](https://www.itsme-id.com/en-be/get-started) | ✓ activate itsme **while still on Windows** — then most Belgian banking is browser + phone and the reader becomes a fallback |

Card readers themselves are almost always CCID-class and need no vendor driver — the software stack (`pcscd` + `eid-mw`) is what matters [[26]](https://eid.belgium.be/en/linux-eid-software-installation).

## 2. Escape hatches, ranked by what they actually cost

| Hatch | Good for | Cost / caveat |
|---|---|---|
| **Web app** (M365 web, Outlook Web, Photopea) | 80% of the office layer | Free, zero maintenance, no offline, no macros [[4]](https://learn.microsoft.com/en-us/answers/questions/5825752/office-365-web-vs-computer-program) |
| **Wine / Bottles / CrossOver** | Office **2016 and older**, Affinity, small vendor utilities | ✗ **Office 365 / 2021 / 2024 don't work reliably** — click-to-run installers defeat Wine, and Outlook/OneDrive/OneNote components are broken or absent [[28]](https://gist.github.com/eylenburg/38e5da371b7fedc0662198efc66be57b) |
| **WinApps / WinBoat** (Windows VM + RemoteApp over FreeRDP) | modern Office, Access, any single stubborn Windows app | Individual Windows app windows appear on your Linux desktop with MIME/menu integration — far higher compatibility than Wine, at the price of running a Windows VM [[29]](https://www.theregister.com/software/2026/02/14/contain-your-windows-apps-inside-linux-windows/4334445) |
| **Full VM under KVM/virt-manager** | Visual Studio proper, SSMS, .NET Framework, anything with posture-checked VPN | Best hypervisor on Linux: VirtIO drivers, low overhead, real PCI passthrough. VirtualBox's 3D/passthrough is markedly weaker [[30]](https://wiki.gentoo.org/wiki/GPU_passthrough_with_virt-manager,_QEMU,_and_KVM) |
| **GPU passthrough (VFIO)** | near-native graphics in the VM | Single-GPU passthrough works but *takes your GPU away from the host* while the VM runs — the Linux desktop goes dark and comes back on shutdown [[31]](https://www.musabase.com/2025/05/single-gpu-passthrough-on-vm.html). Fiddly IOMMU/vBIOS setup. Only worth it for GPU-bound Windows work |
| **Windows 365 Cloud PC** | the compliance/legacy app you touch monthly | Reachable from any HTML5 browser on Linux, no client needed [[32]](https://learn.microsoft.com/en-us/windows-365/end-user-access-cloud-pc). Business tiers run roughly $28–$56/user/month after the May 2026 price cut; Enterprise starts near $31 and scales past $120 [[33]](https://www.aguidetocloud.com/licensing/windows-365/) |
| **Keep a Windows partition** | everything above, at zero recurring cost | Windows 11 is fine. If the machine is on Windows 10, note support ended 14 October 2025 — consumer ESU (free with settings sync, 1,000 Rewards points, or $30) runs until the programme closes 12 October 2027 [[34]](https://www.microsoft.com/en-us/windows/extended-security-updates) |

**For this reader's profile the honest answer is: dual-boot Windows for Visual Studio designers + SSMS Agent + macro workbooks, and don't bother with GPU passthrough.**

## 3. Switch mechanics: dual-boot vs full wipe

Dual-boot, for the first 4–8 weeks, always. The pitfalls are known and all avoidable:

| Pitfall | What happens | Fix |
|---|---|---|
| **BitLocker** | Windows 11 24H2 can auto-enable BitLocker even on Home. Repartitioning or a bootloader change triggers a recovery-key prompt [[35]](https://windowsforum.com/threads/2026-dual-boot-windows-and-linux-setup-uefi-bitlocker-secure-boot-guide.421374/) | **Print the recovery key. Suspend or disable BitLocker before you touch partitions.** |
| **Fast Startup / hibernation** | Windows leaves NTFS in a hibernated state; Linux refuses read-write mounts. Worse, hibernating one OS then booting the other can *damage a shared EFI System Partition* [[36]](https://wiki.archlinux.org/title/Dual_boot_with_Windows) | Disable Fast Startup in Windows. Never hibernate in a dual-boot setup |
| **Undersized ESP** | Windows ships a ~100 MB ESP; GRUB/systemd-boot + a couple of kernels and initramfs images fill it | Target ≥ 260 MiB (512 MB is comfortable) [[37]](https://www.ctrl.blog/entry/esp-size-guide.html)[[36]](https://wiki.archlinux.org/title/Dual_boot_with_Windows). Reuse the existing ESP — **never reformat it** |
| **Install order** | Windows installers overwrite the bootloader and don't detect Linux; Linux installers detect Windows and chain-load it | Windows first, Linux second [[36]](https://wiki.archlinux.org/title/Dual_boot_with_Windows) |
| **Clock skew** | Linux writes UTC to the RTC, Windows reads it as local time → your clock jumps 1–2 hours every reboot | `timedatectl set-local-rtc 1` on Linux, or set Windows to UTC via registry [[38]](https://itsfoss.com/wrong-time-dual-boot/). Fix it once or it will erode your patience daily |
| **Secure Boot** | third-party kernel modules (NVIDIA, VirtualBox) need signing under Secure Boot [[35]](https://windowsforum.com/threads/2026-dual-boot-windows-and-linux-setup-uefi-bitlocker-secure-boot-guide.421374/) | Enroll a MOK key during install, or disable Secure Boot — but disabling it also disables BitLocker's TPM unseal |

## 4. Data, filesystems, and identity

**NTFS.** The in-kernel `ntfs3` driver has a track record of freezes and corruption; the mature choice is `ntfs-3g` — slower, safe [[39]](https://www.dedoimedo.com/computers/linux-ntfs-driver-reliability.html). Use NTFS for *reading your old data*, not as a daily-driver filesystem. For a shared partition, exFAT has native read-write kernel support and works on both sides [[40]](https://en.wikipedia.org/wiki/ExFAT) — but it carries no POSIX permissions or extended attributes, which matters next.

⚠ **Dropbox is the sharpest constraint in this whole migration.** The Linux client relies on extended attributes to track files and supports only unencrypted **ext4** for the sync folder [[41]](https://linux.slashdot.org/story/18/08/10/2120248/dropbox-is-dropping-support-for-all-linux-file-systems-except-unencrypted-ext4). Consequences:

- Your Dropbox folder **cannot** live on NTFS, exFAT, or btrfs/ZFS. If you were planning btrfs snapshots, Dropbox is a reason to keep at least one ext4 volume.
- ext4 *inside* a LUKS container is fine — LUKS is block-level and invisible to Dropbox [[41]](https://linux.slashdot.org/story/18/08/10/2120248/dropbox-is-dropping-support-for-all-linux-file-systems-except-unencrypted-ext4). ext4's own file-based encryption (`fscrypt`) is not.
- The client also needs an AppIndicator-capable tray; GNOME needs an extension [[42]](https://help.dropbox.com/installs/dropbox-desktop-app-for-linux).

**Identity and config**, in order:

1. **SSH keys** — copy `~/.ssh`, then `chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_*`. Wrong permissions are the #1 "my key doesn't work" cause on Linux.
2. **GPG** — `gpg --export-secret-keys --armor` on Windows, `gpg --import` on Linux, then `gpg --edit-key <id> trust`. Don't copy `private-keys-v1.d` between versions; export/import.
3. **Browser profiles** — sign in to Firefox Sync / Chrome sync rather than copying profile directories across OSes. On Ubuntu, install a **non-Snap** Firefox if you need eID [[7]](https://eid.belgium.be/en/faq/why-it-not-possible-use-eid-software-snap-andor-flatpak).
4. **Dotfiles** — this is the moment to put them in a git repo with a bootstrap script; you'll run it at least twice during a staged migration.
5. **itsme + 2FA + password manager** — verify recovery on your phone *before* wiping anything [[27]](https://www.itsme-id.com/en-be/get-started).

## 5. WSL2 experience: what transfers and what doesn't

| Transfers cleanly | Doesn't transfer |
|---|---|
| bash, coreutils, package managers, `apt`/`dnf` muscle memory | Desktop stack: display server (X11 vs Wayland), compositor, portals, audio (PipeWire), theming — WSL2 taught you none of it |
| Docker, compose, CLI-driven workflows — and they get **faster**: container start ~0.3s native vs ~1.2s on WSL2, container filesystem ops 3–5× faster [[43]](https://dasroot.net/posts/2026/04/wsl2-vs-native-linux-developer-experience-comparison/) | Hardware: printers, Bluetooth, webcam, sleep/resume, fingerprint readers, external monitor hotplug, GPU drivers |
| Shell scripting, ssh, git, editors | Networking model — WSL2 defaults to NAT and is isolated from the host stack; native Linux gives you bridged/host networking and real interfaces [[44]](https://msendpointmgr.com/2025/12/15/managing-native-linux-vs-wsl-1-2-a-technical-comparison-for-windows-admins/) |
| Comfort with the CLI generally | USB/GPU passthrough, kernel modules, init-system and system-wide config tinkering [[43]](https://dasroot.net/posts/2026/04/wsl2-vs-native-linux-developer-experience-comparison/) |

WSL2 makes you competent at *the Linux userland* and leaves you a beginner at *the Linux desktop*. Budget your learning time accordingly: the surprises will all be graphical, audio, or power-management, not shell.

## 6. Staged migration plan with go/no-go checkpoints

### Stage 0 — Inventory (½ day, still on Windows)

List every app you opened in the last 90 days. Mark each ✓/⚠/✗ against §1. Anything ✗ must have a named hatch from §2 before you proceed. Print the BitLocker recovery key. Activate itsme. Push dotfiles to git.

### Stage 1 — Live USB (2 evenings, zero risk)

Boot the candidate distro from USB without installing. This tests *hardware*, which is the failure mode you cannot fix later.

**Gate 1 — all must pass, or change distro/kernel version:**

- [ ] Wi-Fi and Bluetooth work without hunting for firmware
- [ ] External monitor + correct resolution/refresh; laptop scaling readable
- [ ] Suspend and resume, twice (lid close, lid open)
- [ ] Audio out **and** mic in, headset switching
- [ ] **Teams PWA screen share picks up a window and a full screen** [[13]](https://learn.microsoft.com/en-us/answers/questions/4415327/fixed-screen-sharing-on-ubuntu-is-not-working-team)
- [ ] Webcam in a browser call
- [ ] Trackpad gestures, fn-keys (brightness, volume)

### Stage 2 — Dual-boot (4 weeks, reversible)

Shrink Windows from *inside Windows* (Disk Management), leave ≥ 80 GB for Linux + a separate `/home`. Suspend BitLocker, disable Fast Startup, reuse the ESP, install Linux second [[36]](https://wiki.archlinux.org/title/Dual_boot_with_Windows)[[35]](https://windowsforum.com/threads/2026-dual-boot-windows-and-linux-setup-uefi-bitlocker-secure-boot-guide.421374/). Fix the RTC immediately [[38]](https://itsfoss.com/wrong-time-dual-boot/). Put `/home` (or at least the Dropbox folder) on ext4 [[41]](https://linux.slashdot.org/story/18/08/10/2120248/dropbox-is-dropping-support-for-all-linux-file-systems-except-unencrypted-ext4).

Then do **real work** on Linux, and log every reboot into Windows and why.

**Gate 2 — the checkpoints that decide whether it sticks:**

- [ ] Full .NET solution builds, tests run, debugger hits breakpoints in Rider
- [ ] Docker + Coolify deploys work end-to-end
- [ ] SQL Server container up, MSSQL extension connects, schema compare works [[1]](https://learn.microsoft.com/en-us/sql/tools/whats-happening-azure-data-studio)[[2]](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/quickstart-install-docker?view=sql-server-ver17)
- [ ] Corporate VPN connects and stays up through a sleep cycle [[24]](https://www.infradead.org/openconnect/)
- [ ] eID reads your card in a **non-sandboxed** browser; a real government/bank flow completes [[26]](https://eid.belgium.be/en/linux-eid-software-installation)[[7]](https://eid.belgium.be/en/faq/why-it-not-possible-use-eid-software-snap-andor-flatpak)
- [ ] Dropbox reports "Up to date", not a filesystem warning [[41]](https://linux.slashdot.org/story/18/08/10/2120248/dropbox-is-dropping-support-for-all-linux-file-systems-except-unencrypted-ext4)
- [ ] You joined a Teams meeting, shared a screen, and presented — twice
- [ ] Printing/scanning works if you need it
- [ ] **Windows reboot log ≤ 2 in the final week**, and every entry maps to a known ✗ item

Fail on any of the first six → fix or abandon; those are not things you learn to live with. Reboots > 2/week for reasons that *aren't* on your ✗ list → the switch is not ready.

### Stage 3 — Commit (after Gate 2)

Don't wipe Windows. Shrink it to ~80–120 GB, keep it for VS designers, SSMS Agent, macro workbooks, and any posture-checked VPN, and give Linux the rest. Convert one of the reclaimed NTFS partitions to ext4/btrfs once you've verified the data is elsewhere [[39]](https://www.dedoimedo.com/computers/linux-ntfs-driver-reliability.html). If you find yourself booting Windows less than monthly after three months, convert it to a KVM guest and reclaim the disk [[30]](https://wiki.gentoo.org/wiki/GPU_passthrough_with_virt-manager,_QEMU,_and_KVM) — a VM you can snapshot beats a partition you have to reboot into.

**Rollback trigger:** if at any point you're spending more than ~2 hours/week fighting the desktop rather than working, go back to Windows for the quarter and retry after the next LTS/kernel release. The migration is cheap to repeat and expensive to force.
