---
title: "NAS OS and storage stack 2026: a portability-first survey"
date: 2026-04-28
depth: deep
format: md
topic: "OS and storage stack without lock-in"
topic_raw: "OS and storage stack without lock-in"
issue: 40
tags: [nas, truenas, unraid, openmediavault, proxmox, zfs, btrfs, snapraid, synology-migration, homelab]
summary: "Picking a NAS OS and storage stack for a 2026 self-built home server, with portability and Synology-migration cost as the primary axes."
citations: 83
reading_time_min: 14
cover: cover.svg
cost_usd: 9.03
duration_sec: 853
---

> **Decision.** Pick **TrueNAS Community Edition** on ZFS if you want the most polished single-admin snapshot/replication GUI [[2]](https://www.truenas.com/blog/truenas-community-edition-release-2504/) [[67]](https://www.truenas.com/docs/scale/scaletutorials/dataprotection/replication/) and accept periodic Apps-stack rewrites [[40]](https://forums.truenas.com/t/the-future-of-electric-eel-and-apps/5409) [[64]](https://www.truenas.com/docs/scale/24.10/gettingstarted/scalereleasenotes/). Pick **Unraid 7.x** if data portability matters most — every array disk is an independent filesystem readable on any Linux box [[42]](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/file-systems/) — and you want 2000+ pre-configured Docker apps [[73]](https://docs.unraid.net/unraid-os/manual/applications/), with the catch of a paid licence model [[4]](https://unraid.net/blog/new-pricing). Pick **OpenMediaVault 8** if you want a thin Debian veneer with full `apt` escape hatch [[47]](https://docs.openmediavault.org/en/8.x/installation/on_debian.html). Pick **plain Debian + ZFS + Cockpit + zrepl** if you already live in Linux and want zero appliance abstractions [[12]](https://cockpit-project.org/) [[77]](https://zrepl.github.io/). **ZFS** (OpenZFS 2.3+) is the default storage layer; **btrfs RAID5/6** is still officially unsafe [[26]](https://btrfs.readthedocs.io/en/latest/Status.html), **bcachefs** was removed from mainline in 6.17 [[29]](https://lwn.net/Articles/1040120/), and **SnapRAID + mergerfs** is the right pattern only for cold-ish media archives [[34]](https://thenomadcode.tech/mergerfs-snapraid-is-the-new-raid-5). Synology SHR drives mount on vanilla Linux via mdadm + LVM + btrfs [[37]](https://isc.sans.edu/diary/Analyzing%20Synology%20Disks%20on%20Linux/30904), but Hyper Backup and Active Backup repositories are DSM-only [[55]](https://www.blackvoid.club/full-bare-metal-backup-with-hyper-backup-and-dsm-7-2/) [[61]](https://kb.synology.com/en-global/DSM/help/ActiveBackup/activebackup_business_requireandlimit) — replicate the live data, don't trust the backup format.

## Why this question, why now

DSM 7.2's 2025 storage-pool drive lock-in (Synology-branded HDDs only) prompted enough sales pain that DSM 7.3 reversed it in October 2025; firmware updates and health telemetry remain first-party-only [[17]](https://nascompares.com/news/synology-reverse-the-hard-drive-policy-in-dsm-7-3-we-win/). That is the migration trigger most operators hit in 2026. The replacement candidates have meanwhile converged on a smaller, sharper set of options.

## The five OS options at a glance

| OS | License | 2025–26 cadence | Defaults | Operator profile |
|---|---|---|---|---|
| **TrueNAS Community Edition** (was Scale) | open-core, free CE [[2]](https://www.truenas.com/blog/truenas-community-edition-release-2504/) [[18]](https://linuxiac.com/truenas-responds-to-community-concerns/); optional TrueNAS Connect SSO/monitoring (Foundation free, Plus $60/yr/3 systems) [[3]](https://www.truenas.com/blog/building-a-bridge-between-community-enterprise/) | annual majors from TrueNAS 26 (beta Apr 2026) on Linux 6.18 LTS, OpenZFS 2.4 [[1]](https://www.truenas.com/blog/truenas-plans-for-2026/) | ZFS-only data, Docker Compose apps (since 24.10) [[40]](https://forums.truenas.com/t/the-future-of-electric-eel-and-apps/5409) | Wants a polished GUI, accepts opinionated stack |
| **Unraid 7.x** | paid Starter $49 / Unleashed $109 / Lifetime $249, +$36/yr for updates [[4]](https://unraid.net/blog/new-pricing) | 7.0 Jan 2025, 7.1 May, 7.2 Oct, 7.3-rc Apr 2026 [[5]](https://docs.unraid.net/unraid-os/release-notes/7.3.0/) [[6]](https://docs.unraid.net/unraid-os/release-notes/7.0.0/) | per-disk XFS/btrfs/ZFS array + parity disk(s); foreign ZFS pool import as of 7.1 [[6]](https://docs.unraid.net/unraid-os/release-notes/7.0.0/) | Mixed-size disks, lots of media, app-store ergonomics |
| **OpenMediaVault 8** "Synchrony" | GPLv3 [[8]](https://en.wikipedia.org/wiki/OpenMediaVault) | rebased on Debian 13 Trixie, 24 Dec 2025 [[7]](https://www.openmediavault.org/?p=4002); ⭐ 6.7k [[9]](https://github.com/openmediavault/openmediavault) | mdraid + ext4/xfs/btrfs by default; ZFS via plugin | Wants a Debian box with a web UI |
| **Proxmox VE 9** | AGPLv3, optional €115/CPU/yr enterprise repo [[10]](https://www.proxmox.com/en/about/company-details/press-releases/proxmox-virtual-environment-9-0) | 9.0 Aug 2025 (Debian 13, ZFS 2.3.3); 8.4 supported until Aug 2026 [[11]](https://pve.proxmox.com/wiki/Upgrade_from_8_to_9) | ZFS or LVM-thin; LXC + KVM; OCI containers since 9.1 [[76]](https://forum.proxmox.com/threads/proxmox-virtual-environment-9-1-available.176255/) | NAS as a side-effect of a hypervisor host |
| **Debian/Ubuntu + Cockpit** | Debian/GPL | rolling | whatever you build — Cockpit v346 (Sept 2025) covers RAID/LVM/LUKS/Stratis V2 [[12]](https://cockpit-project.org/) | Wants no appliance, owns every config file |

NixOS is technically viable for declarative ZFS NAS configs but its ZFS module pins to LTS kernels and the language/docs friction makes it a poor fit for casual operators [[13]](https://wiki.nixos.org/wiki/ZFS) [[14]](https://www.splitbrain.org/blog/2025-07/22-some_thoughts_on_nixos). Skip unless you already run Nix elsewhere.

### Hardware-compat footnotes that bite

Realtek RTL8125 2.5GbE NICs cap at 1G on TrueNAS's stock `r8169` driver and need an out-of-tree `r8125` driver reinstalled after every TrueNAS upgrade [[15]](https://forums.truenas.com/t/realtek-rtl8125b-driver-addition-for-future-scale-release/42986). Intel iGPU QuickSync on TrueNAS Apps relies on the `i915` kernel driver and per-app GPU surfacing for Plex/Jellyfin [[16]](https://forums.truenas.com/t/add-intel-gpu-support-to-the-incus-lxc-containers-on-25-04/39143). On plain Debian both work without ceremony.

## The storage stack layer

Choose this independently from the OS: ZFS works on TrueNAS, Unraid pools, Proxmox, OMV (plugin), and plain Debian.

| Stack | Data checksums | RAID5/6-class | Expansion | Snapshot/replication | When to pick |
|---|---|---|---|---|---|
| **ZFS** (OpenZFS 2.3/2.4) | ✓ on data + metadata | RAIDZ1/2/3 + dRAID [[25]](https://klarasystems.com/articles/openzfs-understanding-zfs-vdev-types/) | RAIDZ expansion in 2.2/2.3, single-drive at a time, multi-day reflow [[20]](https://www.theregister.com/2025/01/23/openzfs_23_raid_expansion/) [[21]](https://freebsdfoundation.org/blog/openzfs-raid-z-expansion-a-new-era-in-storage-flexibility/) | `zfs send/recv` mature, encrypted-aware [[57]](https://openzfs.github.io/openzfs-docs/man/master/8/zfs-receive.8.html) | Default for any new build |
| **btrfs** | ✓ | ⚠ RAID5/6 still "unstable, severe known problems" [[26]](https://btrfs.readthedocs.io/en/latest/Status.html); 6.19 only added experimental fixes [[27]](https://www.phoronix.com/news/Linux-6.19-Btrfs) | flexible | mature send/receive [[35]](https://btrfs.readthedocs.io/en/latest/btrfs-send.html) | Single disk or RAID1 only; this is why Synology runs btrfs **on top of** mdraid+LVM, not native btrfs RAID [[28]](https://kb.synology.com/en-nz/DSM/tutorial/What_was_the_RAID_implementation_for_Btrfs_File_System_on_SynologyNAS) [[53]](https://daltondur.st/syno_btrfs_1/) |
| **bcachefs** | ✓ | various | flexible | n/a in mainline | ✗ Removed from kernel 6.17; DKMS-only since 6.18, in "hard freeze" [[29]](https://lwn.net/Articles/1040120/) [[30]](https://www.theregister.com/2025/09/25/bcachefs_dkms_modules/). Don't put production data on it in 2026. |
| **mdadm + ext4/xfs** | ✗ no data checksums | RAID0/1/4/5/6/10 mature | grow array, online resize | LVM snapshots only (block-level) | Pick only if you layer dm-integrity below — bit rot is silently returned otherwise [[31]](https://linuxconfig.org/protecting-data-integrity-on-ext4-and-xfs-with-dm-integrity-and-luks) |
| **SnapRAID + mergerfs** | ✓ scheduled (not real-time) parity | per-file parity, mismatched disk sizes OK | drop in any drive [[33]](https://perfectmediaserver.com/02-tech-stack/snapraid/) | n/a — files live whole on one disk | Cold-ish media archives where surviving more-than-parity-disks losing only those disks' data is acceptable [[32]](https://www.snapraid.it/compare) [[34]](https://thenomadcode.tech/mergerfs-snapraid-is-the-new-raid-5) |

### ZFS RAM and ECC: kill the folklore

The "1 GB of RAM per TB of storage" rule is folklore, not OpenZFS guidance — official docs just recommend "8GB+ for best performance" and confirm ZFS runs on 2GB [[22]](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html) [[23]](https://cr0x.net/en/zfs-arc-ram-sizing/). ECC is recommended but not strictly required; co-creator Matt Ahrens has been quoted to that effect, with the caveat that ECC blocks an in-RAM bit flip from being written as a "valid" but corrupt block [[24]](https://selfhosting.sh/hardware/zfs-hardware-requirements/). RAIDZ expansion (the long-missing feature) shipped in OpenZFS 2.2 and broadly in 2.3 (Jan 2025) — pool stays online and fault-tolerant during the multi-day reflow [[19]](https://www.phoronix.com/news/OpenZFS-2.3-Released) [[20]](https://www.theregister.com/2025/01/23/openzfs_23_raid_expansion/).

## Lock-in vectors: four layers, scored

Lock-in is not one thing. Score every option on these four layers, weight them by your own exit fear:

1. **Volume layer** — can the disks be read by another OS?
2. **Identity / share** — does the SMB user database and ACL set transfer?
3. **App / container runtime** — are workloads portable, or trapped in a vendor format?
4. **System config** — can you replicate the box on different hardware from text files?

| OS | Volume | Identity / share | App/container | Config replay |
|---|---|---|---|---|
| **TrueNAS CE** | ✓ ZFS imports cleanly into Debian, gated by feature flags [[38]](https://www.truenas.com/community/threads/zfs-compatibility-between-freenas-linux.71083/) [[39]](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Feature%20Flags.html); ZoL xattrs may strip SMB metadata cross-OS [[52]](https://www.truenas.com/community/threads/switching-between-openzfs-on-ubuntu-and-truenas-core-with-the-same-drives-and-zpool.96824/) | ⚠ Samba `passdb.tdb`, manual rebuild; LDAP Samba schema removed in 24.10 [[51]](https://www.truenas.com/community/threads/migrating-samba-users.104373/) | ⚠ Apps stack rewritten 24.10 (k3s→Docker Compose), hard 1 Jun 2025 cutoff for auto-migration [[40]](https://forums.truenas.com/t/the-future-of-electric-eel-and-apps/5409) [[41]](https://www.truenas.com/blog/app-migration-deadline/) [[64]](https://www.truenas.com/docs/scale/24.10/gettingstarted/scalereleasenotes/) | ✗ no plain-text config replay |
| **Unraid** | ✓✓ each array disk = standalone XFS/ext4/btrfs/ZFS, mountable on any Linux box [[42]](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/file-systems/); the `md_unraid` driver itself is open-source and ported to Debian as NonRAID ⭐ 270 [[43]](https://github.com/qvr/nonraid) | ⚠ user db local, no schema | ✓ Docker containers portable (XML templates + appdata share); ✗ plugins are Unraid-specific [[44]](https://docs.unraid.net/unraid-os/using-unraid-to/run-docker-containers/community-applications/) | ✗ no plain-text config replay |
| **OMV** | ✓ Debian `mdadm`/LVM/btrfs underneath, readable anywhere | ⚠ Samba via OMV, configs overwritten by `omv-salt` on every commit [[45]](https://docs.openmediavault.org/en/stable/various/advset.html) [[47]](https://docs.openmediavault.org/en/8.x/installation/on_debian.html) | ✓ docker-compose plugin from omv-extras [[80]](https://wiki.omv-extras.org/doku.php?id=omv7:omv7_plugins:docker_compose) | ✗ no supported `config.xml` restore path to a fresh install [[46]](https://docs.openmediavault.org/en/stable/faq.html) |
| **Proxmox VE** | ✓ ZFS + standard LVM-thin; pools port everywhere | n/a (NAS isn't its job) | ✓ LXC standard + qcow2/VMA portable to plain KVM [[48]](https://pve.proxmox.com/wiki/Linux_Container) [[50]](https://pve.proxmox.com/wiki/Backup_and_Restore); 9.1 added native OCI [[49]](https://www.virtualizationhowto.com/2025/11/complete-guide-to-proxmox-containers-in-2025-docker-vms-lxc-and-new-oci-support/) [[76]](https://forum.proxmox.com/threads/proxmox-virtual-environment-9-1-available.176255/) | ⚠ `storage.cfg` assumptions, manual replay |
| **Debian + Cockpit** | ✓✓ you chose every layer | ✓ stock `smbpasswd`/`/etc/samba/smb.conf` | ✓ pure docker compose | ✓✓ everything is a text file you own |
| **Synology DSM (for reference)** | ✓ but ⚠ — SHR readable elsewhere via mdadm + LVM2, but kernels 5.4+ break Synology's old btrfs format; falls back to Ubuntu Bionic 4.15 [[36]](https://aalonso.dev/blog/2024/how-to-mount-a-synology-shr1-disk-on-linux-2-disks-volume-raid1-with-lvm/) [[37]](https://isc.sans.edu/diary/Analyzing%20Synology%20Disks%20on%20Linux/30904) [[53]](https://daltondur.st/syno_btrfs_1/) | ✗ DSM-locked | ✗ DSM packages, Photos/Drive/ABB DSM-only | ✗ |

The clearest portability wins: **Unraid** for the volume layer (any disk works in any Linux box), **plain Debian** for everything else. The clearest portability loss: **TrueNAS Apps**, which was rewritten in 24.10 (Cobia/Dragonfish k3s → Electric Eel Docker Compose [[64]](https://www.truenas.com/docs/scale/24.10/gettingstarted/scalereleasenotes/)); plan for periodic apps-stack rewrites and budget redeploy effort accordingly.

## Migration: getting off Synology, and between stacks

### Synology SHR → vanilla Linux (the byte-rescue play)

The disks are standard Linux: mdadm software RAID under LVM2 under btrfs/ext4 [[37]](https://isc.sans.edu/diary/Analyzing%20Synology%20Disks%20on%20Linux/30904). Documented incantation for a multi-disk SHR1 set, mounted read-only [[36]](https://aalonso.dev/blog/2024/how-to-mount-a-synology-shr1-disk-on-linux-2-disks-volume-raid1-with-lvm/) [[53]](https://daltondur.st/syno_btrfs_1/) [[54]](https://hacktobeer.eu/posts/synunraid/):

```bash
sudo mdadm --assemble --scan --force --run     # rebuild arrays
sudo vgchange -ay --activationmode partial      # bring up VG
sudo mount -o ro /dev/mapper/vg1000-lv /mnt/syn
```

Single-disk SHR1 is trivial; multi-disk is more fragile because miscalculating sub-array stripe alignment can corrupt the volume [[36]](https://aalonso.dev/blog/2024/how-to-mount-a-synology-shr1-disk-on-linux-2-disks-volume-raid1-with-lvm/). Modern kernels (5.4+) reject Synology's old btrfs format unless you fall back to an Ubuntu Bionic 4.15 kernel [[36]](https://aalonso.dev/blog/2024/how-to-mount-a-synology-shr1-disk-on-linux-2-disks-volume-raid1-with-lvm/) — keep an Ubuntu 18.04 ISO in your toolkit. A documented 2024 Synology→Unraid run saw `rsync -a --info=progress2` push ~140 MB/s through an Ubuntu VM holding the donor disk [[54]](https://hacktobeer.eu/posts/synunraid/).

### What does **not** survive

- **Hyper Backup repositories** are a proprietary deduplicated `.HBK` container, only readable by Synology Hyper Backup, HB Vault, or DSM bare-metal restore [[55]](https://www.blackvoid.club/full-bare-metal-backup-with-hyper-backup-and-dsm-7-2/). No open reader. Treat them as DSM-only.
- **Active Backup for Business** archives are similarly DSM-locked; the ABB UI can export individual files but the backup catalog cannot be ingested by TrueNAS/Unraid/OMV [[61]](https://kb.synology.com/en-global/DSM/help/ActiveBackup/activebackup_business_requireandlimit).
- **Share definitions, the SMB user database, and per-share ACLs.** TrueNAS's own third-party migration doc requires you to pre-create matching local accounts before migration so NFSv4 ACLs / Windows SDs resolve [[56]](https://www.truenas.com/docs/scale/gettingstarted/thirdpartymigration/). A community toolkit (wallacebrf/Synology-to-TrueNAS ⭐ 82 [[62]](https://github.com/wallacebrf/Synology-to-TrueNAS)) automates the SMB-pull side, but you still rebuild users by hand.

### The byte transfer itself

`rsync -aAXH` is the universal fallback (archive + ACLs + xattrs + hardlinks). Two gotchas: rsync <3.1.2 may drop NFSv4 ACLs, and Synology's bundled rsync historically ships **without** ACL/xattr support, so the pull must originate from a modern Linux side, not the Synology side [[59]](https://wiki.archlinux.org/title/Rsync). Community consensus on r/truenas is rsync over SSH inside `tmux`, or mounting Synology's SMB share read-only on TrueNAS; Hyper Backup's "rsync Single Copy" mode works but has been observed sitting at 100% for ~a week before finalizing on multi-TB sets [[60]](https://www.truenas.com/community/threads/whats-the-fastest-safest-and-most-reliable-way-to-transfer-from-synology-to-truenas.110465/).

### Between stacks (post-migration moves)

| Move | Path | Watch out |
|---|---|---|
| TrueNAS CE → Debian (or back) | `zpool export` then `zpool import` | Feature flags must match on the destination; ZoL writes Linux-style xattrs that may strip SMB metadata when crossing FreeBSD ↔ Linux; NFSv4 ACLs do not survive the trip [[39]](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Feature%20Flags.html) [[52]](https://www.truenas.com/community/threads/switching-between-openzfs-on-ubuntu-and-truenas-core-with-the-same-drives-and-zpool.96824/) |
| TrueNAS / Proxmox → Unraid pool | Unraid 7.1+ "foreign ZFS pool import" UI [[6]](https://docs.unraid.net/unraid-os/release-notes/7.0.0/) | Pool features must be compatible; Unraid array (parity) is separate, only ZFS *pools* import |
| Unraid array → another Linux box | Move individual disks, mount as XFS/btrfs [[42]](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/file-systems/); experimental NonRAID for the array driver itself [[43]](https://github.com/qvr/nonraid) | Plugins do not migrate |
| btrfs send/recv between hosts | `btrfs send | btrfs receive` | Brittle in 2025: Proxmox btrfs→btrfs migrations still fail with "cannot flip ro→rw with received_uuid set" [[63]](https://forum.proxmox.com/threads/migrate-from-local-btrfs-to-local-btrfs-does-not-work.107039/) [[58]](https://btrfs.readthedocs.io/en/latest/Send-receive.html) |
| ZFS encrypted send/recv | `zfs send -w` (raw) [[57]](https://openzfs.github.io/openzfs-docs/man/master/8/zfs-receive.8.html) | One non-raw receive permanently blocks future raw incrementals into that dataset — pick raw at the start and stay raw |

## Day-to-day operator experience

What does this look like in week 6 when a drive throws a SMART error and you're on holiday?

### Snapshots and replication

| Stack | UX |
|---|---|
| **TrueNAS CE** | First-party scheduled snapshot tasks + GUI replication tasks over SSH; auto-creates a periodic snapshot before each replication if missing [[67]](https://www.truenas.com/docs/scale/scaletutorials/dataprotection/replication/). The most polished single-admin UX of the lot. |
| **Unraid** | The parity-protected array does **not** snapshot. Snapshots only on ZFS pools or individual ZFS-formatted array drives — and ZFS-formatted array drives lose the pool's redundancy and self-healing [[70]](https://docs.unraid.net/unraid-os/advanced-configurations/optimize-storage/zfs-storage/). Replication is community user-scripts (e.g. SpaceinvaderOne's ⭐ 157 [[71]](https://github.com/SpaceinvaderOne/Unraid_ZFS_Dataset_Snapshot_and_Replications)). |
| **Proxmox** | NAS isn't its primary job: for shares run Samba on the Proxmox host or pass an HBA into a TrueNAS guest. Nested ZFS-on-ZFS (TrueNAS-VM-on-Proxmox-with-ZFS) adds compounding overhead and is warned against by the Proxmox community [[74]](https://forum.proxmox.com/threads/best-way-to-create-a-nas-with-proxmox.131234/). |
| **Debian + ZFS** | `zrepl` is the de-facto end-to-end snapshot+replication daemon — continuous service, own scheduling, resumable send/receive, pruning rules [[77]](https://zrepl.github.io/). Replaces the cron-driven `zfs-auto-snapshot` model. |
| **OMV** | Snapshot plugin, scheduled tasks via cron + Postfix [[82]](https://docs.openmediavault.org/en/latest/administration/general/notifications.html). Less polish than TrueNAS, more than a bare Debian. |

### Alerting

TrueNAS's default S.M.A.R.T./pool alert severity is **Immediately** once SMTP is configured [[68]](https://www.truenas.com/docs/scale/scaleuireference/toptoolbar/alerts/alertsettingsscreen/). OMV's notification system rides on Postfix and integrates SMART/MDADM/scheduled-task/cron-apt events but email must be manually configured under System | Notification before any alert is sent [[82]](https://docs.openmediavault.org/en/latest/administration/general/notifications.html). On Unraid, Proxmox-as-NAS, or plain Debian, the cross-stack drive-monitoring fallback is **Scrutiny** ⭐ 7.7k [[83]](https://github.com/AnalogJ/scrutiny) — a Docker container overlaying smartd with web UI, historical trend charts, real-world failure thresholds, and email/Slack/webhook/Telegram alerts.

### OS upgrades (where each one bites)

- **TrueNAS CE**: Cobia → Dragonfish broke k3s for many users [[66]](https://forums.truenas.com/t/k3s-broke-after-update-to-dragonfish-24-04-1-1/6207); 24.04 → 24.10 (Electric Eel) ripped k3s out entirely and replaced with Docker Compose [[40]](https://forums.truenas.com/t/the-future-of-electric-eel-and-apps/5409); auto-migration deadline was 1 Jun 2025, manual redeploy after [[41]](https://www.truenas.com/blog/app-migration-deadline/). Users reported all-apps-gone-after-upgrade scenarios on Cobia [[65]](https://www.truenas.com/community/threads/all-apps-gone-after-upgrade-to-cobia.113702/). TrueNAS 26's annual cadence (LTS-style on Linux 6.18) is iX's response to the apps churn [[1]](https://www.truenas.com/blog/truenas-plans-for-2026/) [[18]](https://linuxiac.com/truenas-responds-to-community-concerns/).
- **Unraid 6 → 7**: comparatively smooth; 7.1 added ZFS pool import, 7.2 enabled RAIDZ expansion, 7.3-rc Apr 2026 ships ZFS 2.4.1 + Docker v29 + TPM-based licensing [[5]](https://docs.unraid.net/unraid-os/release-notes/7.3.0/) [[6]](https://docs.unraid.net/unraid-os/release-notes/7.0.0/). The pricing change (March 2024) drew loud STH backlash — "people will flock to truenas" [[69]](https://www.servethehome.com/unraid-moves-to-annual-subscription-pricing-model/) — but the technical upgrade path itself is fine.
- **Proxmox VE 8 → 9**: standard Debian 12→13 dist-upgrade, ZFS pools import without migration; 9.1 added OCI/Docker as first-class application containers [[10]](https://www.proxmox.com/en/about/company-details/press-releases/proxmox-virtual-environment-9-0) [[76]](https://forum.proxmox.com/threads/proxmox-virtual-environment-9-1-available.176255/). 8.4 supported until Aug 2026 [[11]](https://pve.proxmox.com/wiki/Upgrade_from_8_to_9).
- **OMV 7 → 8**: reportedly breaks the docker-compose plugin — shared-folder paths get unmapped, containers disappear from the UI, requires a `fix7to8upgrade` script [[81]](https://forum.openmediavault.org/index.php?thread/58854-docker-containers-don-t-show-up-after-omv-upgrade-7-8/).
- **Plain Debian + ZFS**: the recurring footgun is unattended kernel upgrades leaving the new kernel's initrd without ZFS modules, dropping the system to an initramfs shell [[78]](https://github.com/openzfs/zfs/issues/10355). Recovery means booting a live env, importing pools read-only, then rebuilding `zfs-dkms` against the new kernel [[79]](https://aweirdimagination.net/2024/06/02/troubleshooting-zfs-upgrade/). Pin kernels or hold `zfs-dkms` updates.

### Container/VM workloads

- **TrueNAS CE Apps**: Docker Compose since 24.10 (one breaking rewrite, expect more) [[40]](https://forums.truenas.com/t/the-future-of-electric-eel-and-apps/5409) [[64]](https://www.truenas.com/docs/scale/24.10/gettingstarted/scalereleasenotes/).
- **Unraid Community Apps**: 2000+ pre-configured Docker containers from the WebGUI — by far the most beginner-friendly app store [[72]](https://www.howtogeek.com/why-i-chose-unraid-over-truenas-scale-in-2025/) [[73]](https://docs.unraid.net/unraid-os/manual/applications/).
- **Proxmox**: Docker-in-LXC requires nesting + keyctl, exposing /sys and /proc with read-write — official Proxmox docs warn this risks container breakout, recommend Docker-in-VM [[75]](https://pve.proxmox.com/wiki/Unprivileged_LXC_containers); 9.1's native OCI support is the cleaner path [[76]](https://forum.proxmox.com/threads/proxmox-virtual-environment-9-1-available.176255/).
- **OMV**: not first-party — `openmediavault-compose` plugin from omv-extras [[80]](https://wiki.omv-extras.org/doku.php?id=omv7:omv7_plugins:docker_compose).
- **Plain Debian**: bring-your-own `docker compose`, fully portable.

## Decision recipes

Map your fear to a stack:

| Your fear | Pick |
|---|---|
| "I want a Synology-class GUI for snapshots and replication, and I'll accept the apps stack changing every 18 months." | **TrueNAS Community Edition** (ZFS) [[2]](https://www.truenas.com/blog/truenas-community-edition-release-2504/) [[67]](https://www.truenas.com/docs/scale/scaletutorials/dataprotection/replication/) |
| "If the OS dies in five years, I want any disk to mount on any Linux box without thinking. Mixed-size drives. App store ergonomics." | **Unraid 7.x**; plus a small ZFS pool for snapshotted data, the array for media [[42]](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/file-systems/) [[6]](https://docs.unraid.net/unraid-os/release-notes/7.0.0/) [[73]](https://docs.unraid.net/unraid-os/manual/applications/) |
| "I want a Debian box. The web UI is a convenience, not a contract." | **OpenMediaVault 8** on mdraid+ext4, or **Debian + Cockpit** if even the OMV layer is too much [[7]](https://www.openmediavault.org/?p=4002) [[12]](https://cockpit-project.org/) [[47]](https://docs.openmediavault.org/en/8.x/installation/on_debian.html) |
| "The NAS is a side-effect of running VMs and containers." | **Proxmox VE 9** with ZFS, host-level Samba (no GUI), or HBA-passthrough into a TrueNAS guest [[10]](https://www.proxmox.com/en/about/company-details/press-releases/proxmox-virtual-environment-9-0) [[74]](https://forum.proxmox.com/threads/best-way-to-create-a-nas-with-proxmox.131234/) [[76]](https://forum.proxmox.com/threads/proxmox-virtual-environment-9-1-available.176255/) |
| "I already live in Linux. I write my own systemd units." | **Debian + ZFS + Cockpit + zrepl + Scrutiny** [[12]](https://cockpit-project.org/) [[77]](https://zrepl.github.io/) [[83]](https://github.com/AnalogJ/scrutiny) |

### Cross-cutting rules

- **Replicate live data, not backups.** Hyper Backup and ABB are DSM-only formats — you cannot recover from them on the new stack [[55]](https://www.blackvoid.club/full-bare-metal-backup-with-hyper-backup-and-dsm-7-2/) [[61]](https://kb.synology.com/en-global/DSM/help/ActiveBackup/activebackup_business_requireandlimit). Move bytes, not archives.
- **If you choose ZFS, choose raw replication from day one.** A single non-raw `zfs receive` permanently blocks future raw incrementals into that dataset [[57]](https://openzfs.github.io/openzfs-docs/man/master/8/zfs-receive.8.html).
- **Do not run nested ZFS-on-ZFS.** TrueNAS-as-VM-on-Proxmox-with-ZFS is repeatedly warned against — pass the HBA through, or run Samba on the Proxmox host [[74]](https://forum.proxmox.com/threads/best-way-to-create-a-nas-with-proxmox.131234/).
- **Btrfs RAID5/6 → don't.** Synology themselves run btrfs on top of mdraid+LVM rather than native btrfs RAID [[28]](https://kb.synology.com/en-nz/DSM/tutorial/What_was_the_RAID_implementation_for_Btrfs_File_System_on_SynologyNAS) [[53]](https://daltondur.st/syno_btrfs_1/), and the upstream status page still calls native RAID5/6 unstable in 2026 [[26]](https://btrfs.readthedocs.io/en/latest/Status.html).
- **Bcachefs is a 2027+ conversation.** DKMS-only, hard freeze, ejected from mainline — not a NAS choice in 2026 [[29]](https://lwn.net/Articles/1040120/) [[30]](https://www.theregister.com/2025/09/25/bcachefs_dkms_modules/).
- **Pin your kernel if you're on Debian + ZFS.** Unattended kernel upgrades + missing zfs-dkms = initramfs shell on next boot [[78]](https://github.com/openzfs/zfs/issues/10355) [[79]](https://aweirdimagination.net/2024/06/02/troubleshooting-zfs-upgrade/).
