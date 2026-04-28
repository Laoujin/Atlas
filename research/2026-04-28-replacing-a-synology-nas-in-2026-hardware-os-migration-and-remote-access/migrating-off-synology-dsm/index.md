---
title: "Migrating off Synology DSM"
date: 2026-04-28
depth: standard
format: md
topic: "Migrating off Synology DSM"
topic_raw: "Migrating off Synology DSM"
issue: 40
tags: [synology, dsm, nas, migration, truenas, unraid, proxmox, homelab]
summary: "How to leave DSM in 2026: where to land (TrueNAS/Unraid/Proxmox/UGREEN), how to move the data without losing it, and which open-source apps replace which DSM packages."
citations: 35
reading_time_min: 7
cover: cover.svg
cost_usd: 2.70
duration_sec: 455
---

> **Decision.** Migrate if you want hardware freedom or fear another lock-in cycle; stay on DSM 7.3 if you value the polished bundle and your current box still works. Where to land: **TrueNAS SCALE** for data integrity (ZFS), **Unraid** for mixed-disk flexibility and a smooth app store, **Proxmox + TrueNAS-VM** for full-stack homelabs, **UGREEN NASync** if you want a turnkey appliance without going DIY [[14]](https://nascompares.com/guide/truenas-vs-unraid-vs-omv-in-2025/) [[18]](https://www.xda-developers.com/moving-from-my-nas-from-dsm-to-truenas-best-storage-decision-ever/) [[20]](https://www.xda-developers.com/ugreen-most-powerful-nas-exposes-synology/). Plan a **two-machine, side-by-side** transfer — never wipe SHR drives until the new system is verified.

## Why people are leaving (even after the reversal)

Synology's April 2025 policy change required Synology-branded HDDs or HCL-listed third-party drives on every 2025-Plus model; using anything else blocked storage-pool creation and disabled features [[2]](https://nascompares.com/2025/04/16/synology-2025-nas-hard-drive-and-ssd-lock-in-confirmed-bye-bye-seagate-and-wd/). After sustained backlash and reportedly poor sales, DSM 7.3 (October 2025) restored third-party 3.5″ HDD and 2.5″ SATA SSD support [[1]](https://www.tomshardware.com/pc-components/nas/synology-walks-back-controversial-compatibility-policy-for-2025-nas-units-third-party-hdd-and-ssd-support-returns-with-diskstation-manager-7-3-update) [[4]](https://overclock3d.net/news/storage/synology-backtracks-on-3rd-party-hdd-ban-as-nas-sales-plummet/). M.2 SSDs are still HCL-restricted and Synology has not committed to keeping HDD freedom on 2026 hardware [[3]](https://hostbor.com/synology-nas-blocks-hdd/).

The reversal calmed the immediate revolt, but for many long-term DSM users it confirmed the trajectory: Synology's home-consumer focus is described by community veterans as "at an all-time low" [[5]](https://www.blackvoid.club/what-does-synologys-future-look-like-2025-changes-and-beyond/), and DSM 8 has slipped past its Q4 2025 beta target with no concrete date [[35]](https://mariushosting.com/synology-next-dsm-update-will-be-8-0-7-3-or-7-2-3/). If you are reading this, you have already decided the DSM lock-in tax is too high; the rest is execution.

## Where to land — OS comparison

| Target OS | Storage model | Strength | Weakness | When to pick | ⭐ Stars |
|---|---|---|---|---|---|
| **TrueNAS SCALE** (Fangtooth 25.04+) | ZFS, single-drive RAIDZ expansion since OpenZFS 2.3 [[12]](https://www.truenas.com/blog/truenas-fangtooth-25-04/) [[13]](https://www.theregister.com/2025/01/23/openzfs_23_raid_expansion/) | Checksums, snapshots, replication, free | Steeper learning curve; demands ECC + ≥16 GB RAM realistically | Data integrity is the priority; you want enterprise-grade FS at home | — |
| **Unraid** 7 | Mixed-size parity array + optional ZFS pools | Easiest UX; best app store; mixes drive sizes | Paid licence; ZFS as plugin/secondary; weaker integrity story than TrueNAS | You buy one drive at a time, run lots of containers/VMs | — |
| **OpenMediaVault** 7 | mdadm + ext4/btrfs (DSM-like) | Lightest footprint; runs on a Pi; closest UX to DSM | Smaller plugin ecosystem; manual where DSM was guided | Reusing a low-power box; want the closest "DSM-shaped" replacement | ⭐ 6.6k |
| **Proxmox VE** + TrueNAS VM | ZFS underneath, hypervisor on top | Run NAS, Docker, VMs, k8s on one box; massive community | More moving parts; you're running two OSes | You want NAS + virtualisation + containers in one machine [[16]](https://www.xda-developers.com/ran-my-homelab-truenas-for-over-year-then-switched-to-proxmox/) [[17]](https://b3n.org/truenas-vs-proxmox/) | — |
| **UGREEN NASync** (UGOS Pro) | btrfs/ext4, Synology-style appliance | Turnkey hardware; better CPU than equivalent Synology; Docker support | App library ~25 vs DSM's 200+; younger product | You want appliance UX without DIY [[20]](https://www.xda-developers.com/ugreen-most-powerful-nas-exposes-synology/) [[21]](https://needtoknowit.com.au/blog/ugreen-ugos-pro-review-nas-software-and-ecosystem-explained/) | — |
| **TerraMaster / QNAP / Asustor** | Vendor OS | Drop-in appliance, no drive lock-in [[19]](https://www.virtualizationhowto.com/2025/04/synology-just-locked-down-your-nas-drives-heres-what-to-use-instead/) | Different vendor lock-in surfaces (QTS bugs, slower updates) | You are migrating *vendors*, not philosophy | — |

Trade-off summary: TrueNAS for the file system, Unraid for the experience, OMV for simplicity, Proxmox for headroom [[14]](https://nascompares.com/guide/truenas-vs-unraid-vs-omv-in-2025/) [[15]](https://corelab.tech/best-nas-os-comparison/).

## Data migration playbook

### 1. The core constraint

Synology drives use **mdadm + LVM + ext4 (or btrfs)** — TrueNAS uses ZFS, Unraid uses its own parity scheme, OMV uses ext4/btrfs over mdadm. **You cannot reuse the SHR pool in-place on TrueNAS or Unraid** — the disks must be wiped and re-pooled after the data is copied off [[7]](https://www.truenas.com/community/threads/how-to-migrate-hdds-from-synology.106416/). You will need either (a) a second machine running side-by-side, or (b) enough scratch storage (USB backup target, cloud, second NAS) to drain the Synology before reformatting.

OMV is the one exception: it can mount your Synology drives mostly as-is because both use the same Linux mdadm + LVM stack [[8]](https://isc.sans.edu/diary/Analyzing+Synology+Disks+on+Linux/30904) [[9]](https://aalonso.dev/blog/2024/how-to-mount-a-synology-shr1-disk-on-linux-2-disks-volume-raid1-with-lvm/). Even there, treat it as read-only data recovery, not "boot OMV on these disks."

### 2. Reading SHR on a Linux host (escape hatch)

If the DSM box won't boot, you can still rescue data. Pull the disks, attach to any Linux machine:

```bash
sudo mdadm --assemble --run /dev/md0 /dev/sdb5
sudo vgs                          # find vg1000 (or similar)
sudo mount /dev/mapper/vg1000-lv /mnt/synology
```

This works because SHR is just stacked mdadm devices under LVM [[8]](https://isc.sans.edu/diary/Analyzing+Synology+Disks+on+Linux/30904) [[9]](https://aalonso.dev/blog/2024/how-to-mount-a-synology-shr1-disk-on-linux-2-disks-volume-raid1-with-lvm/). Older kernels handle btrfs-on-SHR more reliably than current ones.

### 3. Transfer paths (DSM still booting)

| Method | Speed | Best for | Notes |
|---|---|---|---|
| **SMB mount + rsync** (target machine pulls) | Fast on GbE; ~140 MB/s reported on saturated 12-year-old hardware [[10]](https://hacktobeer.eu/posts/synunraid/) | Most users | Mount Synology share on TrueNAS/Unraid; rsync locally. Preserves metadata. [[6]](https://www.truenas.com/docs/solutions/migratingtotruenas/) [[11]](https://www.truenas.com/community/threads/whats-the-fastest-safest-and-most-reliable-way-to-transfer-from-synology-to-truenas.110465/) |
| **Hyper Backup → rsync target on TrueNAS** | Slower; can stall at 100% | Long migration window where DSM keeps running | Configure TrueNAS as rsync destination; DSM keeps backing up until cutover [[31]](https://www.truenas.com/community/threads/how-to-use-truenas-as-rsync-backup-destination-for-synology-hyper-backup.111684/) |
| **Hyper Backup → S3 (MinIO on TrueNAS)** | Fastest for many small files | Encrypted/versioned migration | Avoids ⚠ "transfer encryption" rsync incompatibility; portable backup format |
| **External USB intermediate** | Limited by USB 3 (~150–250 MB/s) | <8 TB datasets, fewest moving parts | "Just copy the data to a large external USB drive" — cited as simpler than the network dance [[10]](https://hacktobeer.eu/posts/synunraid/) |
| **Cloud (rclone via B2/S3)** | Bandwidth-limited | Off-site safety + migration in one | Add ~$6/TB-month transit cost; egress fees apply on read-back |

The canonical command on the target:

```bash
rsync -a --info=progress2 /mnt/synology-smb/ /mnt/tank/data/
```

→ run inside `tmux` so a dropped SSH session doesn't kill the transfer [[11]](https://www.truenas.com/community/threads/whats-the-fastest-safest-and-most-reliable-way-to-transfer-from-synology-to-truenas.110465/).

### 4. Cutover sequence (recommended)

1. Stand up the new OS on **separate hardware**. Don't touch the Synology drives.
2. Initial bulk rsync (days for multi-TB).
3. Verify checksums on a sample (`rsync --checksum` or `rclone check`).
4. Quiesce DSM clients, run a final delta rsync.
5. Repoint Time Machine / SMB / backup clients at the new server.
6. Run the new server **alongside** DSM for ≥2 weeks before wiping the old drives — this is your rollback insurance.
7. Only then: wipe drives, optionally reuse them in the new pool. ⚠ Synology drives often have older firmware than current Seagate/WD retail — flash before adding to a long-life pool.

Forum migration threads confirm this two-machine pattern as the default; in-place is not recommended [[34]](https://forums.unraid.net/topic/90214-migrating-from-synology-dsm-to-unraid/).

## App-by-app replacement matrix

The DSM appeal is the bundle, not any single app. Most replacements run in Docker on whatever new OS you pick — `docker compose` files turn out to be the dominant migration artifact [[32]](https://blog.zblesk.net/docker-made-migration-to-a-new-nas-easy/).

| DSM package | Best open-source replacement | Notes | ⭐ Stars |
|---|---|---|---|
| **Synology Photos** | [Immich](https://github.com/immich-app/immich) | Closest UX to Photos; mobile apps, face recognition, on-device ML [[22]](https://mariushosting.com/best-synology-photos-alternative-for-your-nas/) [[23]](https://github.com/immich-app/immich). ⚠ rapid release cadence — pin versions | ⭐ 99k |
| (alt) | [PhotoPrism](https://github.com/photoprism/photoprism) | Better metadata editing; heavier setup; for power users [[24]](https://github.com/photoprism/photoprism) | ⭐ 40k |
| **Synology Drive (sync only)** | [Seafile](https://github.com/haiwen/seafile) | Block-level sync → fastest of the bunch; Drive-replacement only [[26]](https://www.xda-developers.com/completely-uprooted-nextcloud-server-switched-seafile-instead/) | ⭐ 15k |
| **Drive + Calendar + Contacts + Office** | [Nextcloud](https://github.com/nextcloud/server) | Full Workspace replacement; heavier maintenance [[25]](https://needtoknowit.com.au/blog/nextcloud-vs-seafile-vs-synology-drive/) | ⭐ 35k |
| **Surveillance Station** | [Frigate](https://github.com/blakeblackshear/frigate) | On-device AI detection (Coral / GPU); config is YAML [[27]](https://nascompares.com/answer/synology-surveillance-station-alternative-nvr/) [[28]](https://github.com/blakeblackshear/frigate). ⚠ no GUI for camera setup | ⭐ 32k |
| (alt) | [Scrypted](https://github.com/koush/scrypted) | HomeKit Secure Video bridge; iOS-first households | ⭐ 5.7k |
| **Active Backup for Business (PC/Mac/VM)** | Proxmox Backup Server (proxmox-backup ⭐ 204 — official site is the canonical source) | Free; deduplicating; first-class VM support that ABB lacks for non-Hyper-V/VMware [[29]](https://kb.synology.com/en-ph/DSM/tutorial/back_up_restore_proxmox_vm) [[30]](https://forum.proxmox.com/threads/backup-to-nas-synology.149630/) | — |
| (alt) | Veeam Community / Restic + rclone | Community Veeam free for ≤10 workloads; Restic for *nix-shaped fleets | — |
| **Hyper Backup (NAS→cloud)** | rclone + cron, or Borg/Restic to B2/Wasabi | Tiny, fast, encrypted; replication is one bash script | — |
| **Container Manager / Docker UI** | Portainer CE | Drop-in; what most DSM "apps" already wrap [[32]](https://blog.zblesk.net/docker-made-migration-to-a-new-nas-easy/) | — |
| **Synology Office / Notes / Chat** | Nextcloud Office (Collabora), Joplin, Element | No single replacement; pick per family-of-app | — |
| **DDNS + Let's Encrypt + reverse proxy** | Caddy or Traefik | Two-line auto-TLS vs DSM's Control Panel toggles | — |
| **Time Machine target** | OpenMediaVault SMB share with `fruit:time machine = yes`, or TrueNAS native TM dataset | Both options work; TrueNAS exposes it as a checkbox [[33]](https://github.com/openmediavault/openmediavault) | — |

## Pitfalls

- **Don't expect bit-perfect feature parity.** Synology Photos' "shared spaces" model, Surveillance Station's licensing-included multi-camera workflow, and Hyper Backup's bundle-everything UX have no single-app replacement — you assemble these out of two or three OSS pieces, sometimes losing minor features.
- **Plan for app churn.** Immich ships breaking changes monthly; PhotoPrism and Frigate change schemas across majors. The DSM "App Center handles compatibility" guarantee disappears the day you migrate. Pin versions, read changelogs, schedule update windows. [[21]](https://needtoknowit.com.au/blog/ugreen-ugos-pro-review-nas-software-and-ecosystem-explained/)
- **ECC RAM matters more on ZFS** than it did on DSM's btrfs/ext4. Budget for it on TrueNAS, especially if you skipped it on Synology.
- **DSM 8 doesn't change the calculus.** Beta has slipped, rollout is 2026 at earliest, and the underlying drive-policy uncertainty remains [[35]](https://mariushosting.com/synology-next-dsm-update-will-be-8-0-7-3-or-7-2-3/) [[3]](https://hostbor.com/synology-nas-blocks-hdd/). Don't wait for DSM 8 to make this decision.
- **Backups before migration**, not during. A second copy of the data on cold storage *before* you start moving disks turns a bad weekend into a "nothing happened" weekend.
- **The home-grade DIY tax is your time.** TrueNAS's average maintenance on a stable home setup is ~1 hour/month; Synology's was closer to zero. Factor that in honestly.
