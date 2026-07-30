---
title: "Dual-boot Linux next to Windows in 2026 without wrecking the Windows install"
date: 2026-07-30
depth: standard
format: md
topic: "Dual-boot Linux alongside Windows without wrecking Windows (2026) — separate disk vs shared disk, Secure Boot, BitLocker and TPM, fast startup, bootloader failure and recovery, and a shared data partition."
topic_raw: "gradual linux migration from Windows (first testing the waters)."
tags: [linux, windows, dual-boot, secure-boot, bitlocker, uefi, ntfs, migration]
summary: "Buy a second NVMe, keep the two OSes ignorant of each other, and pick Linux from the firmware boot menu — the layout with the smallest blast radius on your Windows install."
citations: 30
reading_time_min: 13
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 597
issue: 14
---

> **Decision.** Put Linux on a **second physical disk**, give it its **own ESP on that disk**, and switch OSes from the **firmware boot menu (F12)** rather than from a shared boot loader — this is the only layout where "undo" means "unplug a drive". Before you touch anything: `powercfg /H off`, escrow the BitLocker recovery key, and suspend BitLocker [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows) [[3]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq). Leave Secure Boot **on** and pick a shim-signed distro — turning it off in 2026 costs you Windows Hello and a BitLocker recovery prompt, and buys you almost nothing [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows) [[4]](https://support.microsoft.com/en-us/topic/windows-secure-boot-certificate-expiration-and-ca-updates-7ff40d33-95dc-4c3c-8725-a9b95457578e).

## 1. Layout: second disk vs shrinking Windows

| | Second physical disk | Shrink Windows partition on one disk |
|---|---|---|
| Windows partition table touched | ✗ never | ✓ every time you resize |
| BitLocker recovery risk from partitioning | none | ⚠ "changes to the NTFS partition table" is a documented recovery trigger [[12]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery-overview) |
| Undo | pull the drive, or wipe it | delete partitions + extend C:, hope the recovery/OEM partitions survived |
| Can hibernate one OS and boot the other | ✓ (needs separate ESPs, which needs separate disks) [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows) | ✗ one disk → one ESP → shared ESP → corruption risk [[7]](https://wiki.archlinux.org/title/EFI_system_partition) |
| ESP size you get | whatever you create (Arch suggests 1 GiB, 4 GiB "ought to be enough") [[7]](https://wiki.archlinux.org/title/EFI_system_partition) | Windows Setup's 100 MiB (300 MiB on 4Kn drives) [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows) |
| Cost | one NVMe | free |

Forum consensus matches: separate drives avoid OEM recovery partitions and vendor RAID/Intel RST setups that confuse installers, and let you move the Linux drive to another machine later [[5]](https://forums.linuxmint.com/viewtopic.php?t=416646). The strongest version of the trick is to **physically disconnect the Windows drive while installing Linux** — the installer then cannot write boot files to the Windows ESP even if you misclick, and the Linux disk is guaranteed self-contained and bootable on its own [[6]](https://forums.tomsguide.com/threads/dual-booting-two-hard-drives.392175/post-1688539).

### ESP: shared or separate?

This is the one place the official sources disagree, so decide deliberately.

- **Arch's ESP page:** a separate ESP per OS is the *recommended* mitigation for the hibernation problem, and "most UEFIs support this as long as the ESPs reside on physically different disks" [[7]](https://wiki.archlinux.org/title/EFI_system_partition).
- **Arch's dual-boot page and Microsoft:** "An additional EFI system partition should not be created, as it may prevent Windows from booting" — the failure Microsoft documents is a second install creating a second ESP, after which the firmware boots the new one and the original Windows becomes unreachable [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows) [[2]](https://learn.microsoft.com/en-us/troubleshoot/windows-client/windows-security/cannot-boot-windows-on-primary-hard-disk-uefi).

Practical reading: Microsoft's warning is about **two Windows installs**; a Linux ESP on a second disk is the common, working configuration, but it is firmware-dependent. Install it, then immediately verify Windows still boots from a cold start *and* from the F12 menu. If your firmware only ever boots one ESP, fall back to installing Linux's loader into Windows' 100 MiB ESP — and accept that you must then fully shut down Windows, never hibernate [[7]](https://wiki.archlinux.org/title/EFI_system_partition).

There is only **one ESP per drive**, so if you want to hibernate Windows and still boot Linux, the two ESPs must be on two physical disks — no exceptions [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

## 2. Windows-side prep (do all of this before booting the installer)

**Kill Fast Startup and hibernation.** Fast Startup is hibernation wearing a "Shut Down" label: Windows writes the kernel session to disk and leaves NTFS volumes flagged as in-use. Boot Linux, mount them read-write, and Windows restores a stale image over your changes — anything from lost files to corrupted directories [[8]](https://www.makeuseof.com/windows-feature-wreck-linux-files-dual-boot-users-miss/) [[9]](https://superuser.com/questions/39532/hibernating-and-booting-into-another-os-will-my-filesystems-be-corrupted/136814#136814). The same applies to a **shared ESP**: hibernate Windows, boot Linux, and the ESP itself can be damaged [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

```
powercfg /H off
```

Then **shut down** — a reboot does not clear the flag [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows). ⚠ Windows updates have been reported to re-enable Fast Startup, so re-check it after feature updates [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

Note the asymmetry in the safety nets: `ntfs-3g` added a guard that refuses read-write mounts of a hibernated NTFS volume; **the in-kernel NTFS driver has no such safeguard** [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

**Shrinking (only if you're on one disk).** Windows Disk Management can only shrink up to the last *unmovable* file — typically `pagefile.sys`, `hiberfil.sys`, and `System Volume Information` from System Restore. Disable hibernation, disable the page file, turn off System Protection, defragment, then shrink; re-enable afterwards [[10]](https://www.winhelponline.com/blog/you-cannot-shrink-volume-beyond-point-disk-mgmt/). GParted can often shrink further than Windows will, but **not** on a BitLocker-encrypted volume — Windows itself can resize an encrypted C:, Linux tools cannot [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows). Prefer Windows' own tool for the shrink; it is the one that understands NTFS metadata it created.

## 3. BitLocker

**Assume it is on.** Windows 11 24H2 enables automatic device encryption on clean installs where the user signs in with a Microsoft or work account, across all editions including Home [[11]](https://mspoweruser.com/reminder-windows-11-24h2-enables-default-bitlocker-encryption-on-more-devices/). Arch is blunter: on preinstalled and fresh Windows 11 the C: drive "will come with BitLocker enabled by default, even if BitLocker appears disabled by searching for its name" [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

**Escrow the key first, offline.** Print or save the 48-digit recovery password somewhere that is not the machine you are about to repartition — Microsoft: "BitLocker is designed to make the encrypted drive unrecoverable without the required authentication" [[3]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq). For a personal machine it is in your Microsoft account by default; verify that, don't assume it [[3]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq).

**Suspend, don't decrypt.** `Suspend-BitLocker -MountPoint "C:"` keeps the volume encrypted but wraps the volume master key with a clear key; on resume, BitLocker **reseals to the new measurements** without ever asking for the recovery key [[3]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq). Microsoft explicitly recommends this for planned firmware/hardware changes [[12]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery-overview). Note it auto-resumes on the next reboot unless you pass `-RebootCount` [[12]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery-overview).

**What will actually trigger a recovery prompt.** From Microsoft's own list, the ones a dual-booter hits: changes to the NTFS partition table, changes to the boot manager, changing the BIOS boot device order (on TPM 1.2), UEFI firmware upgrades, installing additional UEFI drivers/applications outside Windows Update, manual changes to the Secure Boot databases, and modifying the PCRs in the TPM validation profile [[12]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery-overview) [[3]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq). Even vendor firmware/TPM updates do it on their own [[13]](https://learn.microsoft.com/en-us/troubleshoot/devices/prompted-bitlocker-recovery-key-installing-updates-surface-uefi-tpm-firmware-surface-device).

**The PCR 7 trap.** Modern BitLocker binds to PCR 7 (Secure Boot state) + PCR 11, which is *tolerant* of firmware and boot-component churn. But: "BitLocker can be prevented from binding to PCR 7 if a non-Windows OS booted prior to Windows, or if Secure Boot isn't available to the device" [[3]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq). Fall back to the PCR 0/2/4 profile and every BIOS update becomes a recovery prompt. → **Don't turn Secure Boot off, and don't re-enable BitLocker while Linux is the default boot entry.** With Secure Boot off entirely, expect the recovery screen at every Windows boot [[14]](https://github.com/Foxboron/sbctl/wiki/Linux-Windows-Dual-Boot-with-Windows-Bitlocker) ⭐ 2.2k. Arch's own warning is that Secure Boot changes made for Linux's benefit "prevent unlocking the BitLocker disk without the recovery key, leading to **permanent data loss**" if you never saved it [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

**BitLocker + LUKS on the second disk.** They are independent: BitLocker seals to the TPM for the Windows volume, LUKS lives entirely on the Linux disk and Windows cannot see it. The interaction only appears if you also seal LUKS to the TPM with `systemd-cryptenroll --tpm2-pcrs=7` — then a Secure Boot key change breaks *both* unlocks at once, and Arch notes PCR 7 requires Secure Boot active and in user mode to be meaningful [[15]](https://wiki.archlinux.org/title/Systemd-cryptenroll). For a first Linux trial, a LUKS passphrase is the lower-drama choice.

## 4. Secure Boot in 2026

**The certificate expiry, in one paragraph.** Microsoft's 2011 Secure Boot certificates are aging out on a published schedule [[4]](https://support.microsoft.com/en-us/topic/windows-secure-boot-certificate-expiration-and-ca-updates-7ff40d33-95dc-4c3c-8725-a9b95457578e):

| Expiring certificate | Expires | Replacement |
|---|---|---|
| Microsoft Corporation KEK CA 2011 | 24 Jun 2026 | Microsoft Corporation KEK 2K CA 2023 |
| Microsoft UEFI CA 2011 (third-party / shim) | 27 Jun 2026 | Microsoft UEFI CA 2023 |
| Microsoft Windows Production PCA 2011 | 19 Oct 2026 | Windows UEFI CA 2023 |

What it means for you: **nothing breaks on the date.** Expiry stops Microsoft *signing new* boot components; it does not revoke what your firmware already trusts. Microsoft: "Devices that haven't received the newer 2023 certificates will continue to start and operate normally" [[4]](https://support.microsoft.com/en-us/topic/windows-secure-boot-certificate-expiration-and-ca-updates-7ff40d33-95dc-4c3c-8725-a9b95457578e). Red Hat's guidance to Linux users is the same — "a shim signed by this key will continue to boot as long as the public certificate is not removed" — with two action items: let Windows Update or `fwupd` push the 2023 certs into your firmware db, and ⚠ **do not remove the 2011 certificate afterwards**, because current shims are dual-signed against both [[16]](https://www.redhat.com/en/blog/expiration-secure-boot-signing-certificates-2026).

**Signed out of the box.** Ubuntu (and by extension Mint/Pop) ships "a `shim` binary signed by Microsoft and a GRUB binary signed by Canonical"; Fedora and RHEL do the equivalent [[17]](https://documentation.ubuntu.com/security/security-features/platform-protections/secure-boot/) [[16]](https://www.redhat.com/en/blog/expiration-secure-boot-signing-certificates-2026). Arch does not — you sign your own with something like sbctl [[14]](https://github.com/Foxboron/sbctl/wiki/Linux-Windows-Dual-Boot-with-Windows-Bitlocker) ⭐ 2.2k. For a first rung, pick a shim-signed distro.

**NVIDIA / DKMS.** Out-of-tree modules must be signed or the kernel refuses them: "Unsigned modules aren't loaded by the kernel. Any attempt to insert them with `insmod` or `modprobe` fails" [[17]](https://documentation.ubuntu.com/security/security-features/platform-protections/secure-boot/). Ubuntu automates it — DKMS generates a machine-specific Machine Owner Key, signs the module, and prompts you once at the blue MOK-enrollment screen on the next reboot [[17]](https://documentation.ubuntu.com/security/security-features/platform-protections/secure-boot/). It's one extra reboot, not a project.

**Is disabling Secure Boot a reasonable trade?** In 2026, no — the cost landed on the Windows side. Disabling it makes a TPM-sealed BitLocker volume show the recovery screen (reversible by re-enabling), and it makes Windows **disable every Windows Hello method** — PIN, face, fingerprint, security key — across all accounts. Re-enabling Secure Boot does not restore them, and you need the actual account password to get back in [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

## 5. Bootloader choice and blast radius

| Approach | Windows ESP touched | Secure Boot out of box | Blast radius when it breaks |
|---|---|---|---|
| **Firmware boot menu only** (own ESP per disk, no cross-registration) | ✗ | depends on distro | Lowest — each OS boots independently; the other disk is unaffected |
| **systemd-boot** | ✓ if sharing ESP | ✗ (sign your own) | Low — minimal UEFI-only design; auto-detects Windows Boot Manager [[20]](https://wiki.archlinux.org/title/Systemd-boot). Recommended over GRUB/rEFInd on firmware that is loosely spec-compliant [[21]](https://wiki.cachyos.org/installation/boot_managers/) |
| **GRUB via shim** (Ubuntu/Fedora default) | ✓ | ✓ | Medium — the most-tested path, but the one the 2024 SBAT incident bricked [[18]](https://www.bleepingcomputer.com/news/microsoft/microsoft-confirms-august-updates-break-linux-boot-in-dual-boot-systems/) |
| **rEFInd** | ✓ | ✗ (sign your own) | Low-medium — auto-detects everything including Windows Boot Manager [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows) |

**The two failure modes worth designing against.**

*Windows resets the boot order.* Boot Windows once and Windows Boot Manager is back on top at the next start; `efibootmgr` reordering does not stick on some boards, and some firmware overrides efibootmgr settings outright whenever it detects Windows [[19]](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface) [[22]](https://bbs.archlinux.org/viewtopic.php?id=223304). Related: if firmware boots the fallback path `\EFI\BOOT\BOOTx64.EFI`, that file may have been overwritten with the Windows loader [[19]](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface). Fixes, in order of increasing intrusiveness: use F12 every time (zero maintenance); `bcdedit /set "{bootmgr}" path "\EFI\<path>\<app>.efi"` to chain from Windows; or a Windows startup task running `bcdedit /set "{fwbootmgr}" DEFAULT "{id}"` [[19]](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface).

*Windows updates revoke your bootloader.* August 2024's KB applied an SBAT revocation intended for old vulnerable shims; Microsoft's "dual-boot detection did not detect some customized methods of dual-booting and applied the SBAT value when it should not have been applied", leaving `Verifying shim SBAT data failed: Security Policy Violation` [[18]](https://www.bleepingcomputer.com/news/microsoft/microsoft-confirms-august-updates-break-linux-boot-in-dual-boot-systems/). This is the strongest argument for the F12/separate-disk layout: a revocation still hits you, but nothing Windows does can corrupt an ESP it never mounts.

## 6. Recovery kit and un-dual-booting

**Have ready before you start:**

- **Windows recovery media / install USB.** `Shift+F10` in Setup gives you a console with `diskpart` and `bcdboot` [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows). Note: Windows RE started manually from repair media requires the BitLocker recovery key to unlock the drive [[12]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery-overview).
- **BitLocker 48-digit key**, printed or on a phone — the pre-boot recovery screen needs it typed with the function keys [[3]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/faq).
- **A copy of the whole ESP.** It's a small FAT32 filesystem; `cp -a` it to external storage from a live USB. Cheapest insurance you will ever buy.
- **Boot-Repair live disk** — "generally reinstalls GRUB and restores access to the operating systems you had installed before the issue", and produces a Boot-Info report you can paste into a forum before letting it change anything [[23]](https://help.ubuntu.com/community/Boot-Repair).

**If you nuke the ESP**, rebuild Windows' side from the install media: `diskpart` → select the ESP → assign a letter, then `bcdboot C:\Windows /s G: /f UEFI` [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

**Un-dual-booting, in order.** Order matters — if GRUB is in the boot path, deleting the Linux partitions first leaves you with a `grub rescue>` prompt and no OS.

1. Boot Windows. Confirm it boots without the Linux loader (F12 → Windows Boot Manager directly).
2. Restore the Windows boot path if Linux owns it: `bcdboot C:\Windows /s <ESP> /f UEFI` [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).
3. `diskmgmt.msc` → delete each Linux volume → the space becomes Unallocated → *Extend Volume* on the adjacent Windows partition [[24]](https://itsfoss.com/uninstall-ubuntu-linux-windows-dual-boot/).
4. Delete the leftover `\EFI\<distro>` directory from the ESP (`mountvol` a letter to it) and drop the stale firmware entry with `bcdedit`, `efibootmgr` from a live session, or EasyUEFI [[24]](https://itsfoss.com/uninstall-ubuntu-linux-windows-dual-boot/).
5. Resume BitLocker.

With the second-disk layout, steps 2–4 collapse to "delete the firmware boot entry and reformat the drive". That is the whole point.

## 7. Sharing data between the two OSes

**Use a dedicated third partition (or the leftovers of the Linux disk), never C:.** Never point Linux at the Windows system volume for read-write work while Fast Startup exists on the machine [[8]](https://www.makeuseof.com/windows-feature-wreck-linux-files-dual-boot-users-miss/).

**NTFS driver state in 2026.** Linux now has *two* read-write NTFS drivers in tree: `ntfs3` (Paragon's, in-kernel since 5.15) and a new `ntfs` driver, formerly NTFSPLUS, merged for Linux 7.1 and derived from a rewrite of the old read-only driver [[25]](https://wiki.archlinux.org/title/NTFS) [[26]](https://www.theregister.com/2026/04/20/linux_71_new_ntfs/). Arch's verdict: "There is no objectively better driver at the moment"; the new `ntfs` is slightly faster but does not yet support Windows native symlinks (planned for 7.2) [[25]](https://wiki.archlinux.org/title/NTFS). Userspace `ntfs-3g` is slower but is still what conservative reviewers recommend for bulk data, and it is the only one of the three that refuses to read-write mount a hibernated volume [[27]](https://www.dedoimedo.com/computers/linux-ntfs-driver-reliability.html) [[1]](https://wiki.archlinux.org/title/Dual_boot_with_Windows). Expect to hit `volume is dirty and "force" flag is not set!` with `ntfs3` after an unclean Windows shutdown; `ntfsfix --clear-dirty` is the escape hatch [[25]](https://wiki.archlinux.org/title/NTFS).

**exFAT vs NTFS for the shared partition.**

| | NTFS | exFAT |
|---|---|---|
| Journaling | ✓ | ✗ |
| Linux driver churn | 3 drivers, ongoing [[25]](https://wiki.archlinux.org/title/NTFS) [[26]](https://www.theregister.com/2026/04/20/linux_71_new_ntfs/) | stable in-kernel `exfat` |
| POSIX permissions / exec bit / symlinks | ✗ (uid/gid fixed at mount) | ✗ [[29]](https://botmonster.com/self-hosting/set-up-dual-boot-linux-windows-shared-storage/) |
| Hibernation dirty-flag hazard | ✓ | lower, but still a shared-mount hazard [[9]](https://superuser.com/questions/39532/hibernating-and-booting-into-another-os-will-my-filesystems-be-corrupted/136814#136814) |

Either is fine for documents, media and build artifacts. Use `windows_names` as a mount option so Linux can't create filenames Windows will refuse to open [[25]](https://wiki.archlinux.org/title/NTFS).

**Do not put `$HOME` or a git repo there.** Neither filesystem stores POSIX permissions, so everything is owned by whatever uid/gid you set in fstab and the executable bit is gone [[29]](https://botmonster.com/self-hosting/set-up-dual-boot-linux-windows-shared-storage/). `git init` itself fails on NTFS mounts because git chmods files inside `.git/` and the driver returns an error [[28]](https://subzerodays.wordpress.com/2018/11/21/creating-git-repo-on-ntfs-in-linux/). For a .NET/TypeScript workstation this is fatal in practice — mode bits in the index, `node_modules` symlinks, and `dotnet` build outputs all depend on things NTFS does not carry. Keep repos on ext4/btrfs on the Linux side and on NTFS on the Windows side, and let the shared partition hold data, not code; symlink individual data directories out of `$HOME` into it if you want the convenience [[28]](https://subzerodays.wordpress.com/2018/11/21/creating-git-repo-on-ntfs-in-linux/).

Paragon's own driver FAQ is the reference for `ntfs3` mount options if you do go the NTFS route [[30]](https://www.paragon-software.com/home/ntfs3-driver-faq/).
