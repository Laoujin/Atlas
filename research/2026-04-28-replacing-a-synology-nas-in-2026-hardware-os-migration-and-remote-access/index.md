---
layout: expedition
title: "Replacing a Synology NAS in 2026: hardware, OS, migration, and remote access"
date: 2026-04-28
topic: "Survey and decision framework for replacing a Synology NAS with an always-on home server in 2026, optimized for higher CPU/RAM headroom, a CPU with AVX2 (and ideally newer ISA extensions), a current mainline Linux kernel, and zero vendor lock-in (no custom DSM-style fork). Cover candidate hardware platforms (mini PCs like Minisforum/Beelink/ASRock, used enterprise SFF such as HP EliteDesk / Lenovo ThinkCentre / Dell OptiPlex micro, NUC-class, and custom DIY builds) compared on price/perf, idle power, RAM ceiling, NVMe and SATA capacity, ECC support, and noise; candidate OS/storage stacks (TrueNAS SCALE, Unraid, Proxmox VE, OpenMediaVault, plain Debian/Ubuntu + ZFS or mdraid, NixOS) compared on lock-in risk, kernel recency, container/VM story, and NAS feature parity with DSM; and the migration path off Synology (shares/SMB, Hyper Backup data, Docker containers, Photos/Drive equivalents, Tailscale/remote access). Produce comparison tables and end with a concrete recommended stack."
format: md
tags: [home-server, nas, synology-migration, truenas, homelab]
summary: "End-to-end framework to leave a Synology NAS in 2026: a hardware shortlist by profile, OS/storage picks scored on lock-in, a DSM migration playbook, and a default remote-access stack — converging on one concrete recommended build."
cover: cover.svg
synthesis: true
children:
  - slug: hardware-platform-shortlist-for-an-always-on-box-in-2026
    title: "Hardware platform shortlist for an always-on box in 2026"
    depth: deep
    status: success
    summary: "Five hardware categories, measured idle wattage, and a profile-by-profile shortlist for replacing a Synology NAS in 2026 — UGREEN, Aoostar, Beelink, Minisforum, Jonsbo+ASRock Rack, and the used tiny trio."
    citations: 101
    reading_time_min: 10
  - slug: os-and-storage-stack-without-lock-in
    title: "OS and storage stack without lock-in"
    depth: deep
    status: success
    summary: "Picking a NAS OS and storage stack for a 2026 self-built home server, with portability and Synology-migration cost as the primary axes."
    citations: 83
    reading_time_min: 14
  - slug: migrating-off-synology-dsm
    title: "Migrating off Synology DSM"
    depth: standard
    status: success
    summary: "How to leave DSM in 2026: where to land (TrueNAS/Unraid/Proxmox/UGREEN), how to move the data without losing it, and which open-source apps replace which DSM packages."
    citations: 35
    reading_time_min: 7
  - slug: remote-access-and-always-on-operations
    title: "Remote access and always-on operations"
    depth: standard
    status: success
    summary: "Default stack for replacing Synology QuickConnect, plus a survey of mesh VPNs, public tunnels, UPS/NUT, WoL, IP-KVM, and uptime monitoring for an always-on home server."
    citations: 27
    reading_time_min: 7
cost_usd: 25.07
duration_sec: 3024
citations: 246
reading_time_min: 38
---

The trigger across all four angles is the same: Synology's 2025-Plus drive lock-in pulled ServeTheHome's recommendation [[1]](https://www.servethehome.com/synology-lost-the-plot-with-hard-drive-locking-move/), and even though DSM 7.3 reversed the 3.5″ HDD restriction in October 2025, M.2 SSDs remain HCL-gated and the trajectory is what convinced operators to leave [[2]](https://nascompares.com/news/synology-reverse-the-hard-drive-policy-in-dsm-7-3-we-win/) [[3]](https://hostbor.com/synology-nas-blocks-hdd/).

**Hardware and OS pull in opposite directions on lock-in.** The hardware survey rewards prebuilt boxes — UGREEN DXP4800 Plus at $620 with 10GbE and BYO-OS support [[4]](https://nascompares.com/guide/truenas-on-a-ugreen-nas-installation-guide/), Aoostar WTR Max at $649-699 with 6 SATA + 5 NVMe + dual 10GbE SFP+ [[5]](https://nascompares.com/review/aoostar-wtr-max-nas-review-nas-perfection/), Beelink ME mini at $209-329 idling at 7-10W [[6]](https://www.techradar.com/computing/beelink-me-mini-nas-mini-pc-review). The OS survey scores TrueNAS Community Edition lowest on lock-in only at the **app layer**: the 24.10 k3s→Docker Compose rewrite with a hard 1 Jun 2025 auto-migration deadline [[7]](https://forums.truenas.com/t/the-future-of-electric-eel-and-apps/5409) [[8]](https://www.truenas.com/blog/app-migration-deadline/) is the clearest reminder that any appliance OS — not just DSM — eventually rewrites its app stack. Unraid wins the *volume* layer (every array disk is a standalone XFS/btrfs/ZFS filesystem, mountable on any Linux box [[9]](https://docs.unraid.net/unraid-os/using-unraid-to/manage-storage/file-systems/)) but charges a paid licence; plain Debian + ZFS + Cockpit + zrepl wins everywhere except hand-holding [[10]](https://cockpit-project.org/) [[11]](https://zrepl.github.io/).

**The migration playbook constrains hardware sizing.** All three operational children agree the cutover is **two-machine, side-by-side** [[12]](https://forums.unraid.net/topic/90214-migrating-from-synology-dsm-to-unraid/) — you cannot reuse SHR pools in-place on TrueNAS or Unraid because mdraid+LVM+btrfs disks must be wiped and re-pooled [[13]](https://www.truenas.com/community/threads/how-to-migrate-hdds-from-synology.106416/). That implies enough disk capacity on day one for the full dataset, and rules out incremental drive-swap strategies. **Hyper Backup repositories will not migrate** — they are a proprietary deduplicated `.HBK` format readable only by DSM [[14]](https://www.blackvoid.club/full-bare-metal-backup-with-hyper-backup-and-dsm-7-2/), so move *live data* over rsync-in-tmux at ~140 MB/s [[15]](https://hacktobeer.eu/posts/synunraid/), not the backup archives.

**ECC is a red herring at home.** OpenZFS docs recommend "8GB+", not the folkloric 1 GB-per-TB rule [[16]](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html), and Matt Ahrens's well-known position is that ZFS is no more ECC-dependent than any other checksumming filesystem [[17]](https://news.ycombinator.com/item?id=18480016). If your platform supports ECC (ASRock Rack B650D4U at ~$264 with onboard BMC [[18]](https://www.asrockrack.com/general/productdetail.asp?Model=B650D4U)), use it; if it doesn't, ZFS without ECC still beats ext4 without ECC.

**Concrete recommended stack — the centre of all four children:**

- **Hardware**: UGREEN DXP4800 Plus (turnkey, 4 SATA + 2 M.2, 10GbE, ~24W idle [[19]](https://www.techpowerup.com/review/ugreen-nasync-dxp4800-plus/13.html), 2-year warranty [[20]](https://nas.ugreen.com/pages/warranty)) — or DIY Jonsbo N3 + CWWK i3-N305 + 32GB DDR5 at $650-770 diskless [[21]](https://selfhosting.sh/hardware/diy-nas-build/) if you want full BYO from day one.
- **OS + storage**: TrueNAS Community Edition on ZFS, with raw `zfs send -w` replication chosen *from day one* (a single non-raw receive permanently blocks future raw incrementals [[22]](https://openzfs.github.io/openzfs-docs/man/master/8/zfs-receive.8.html)). Pick Unraid 7.x instead if mixed-size disks and a 2000+ container app store outweigh ZFS's checksum guarantees [[23]](https://docs.unraid.net/unraid-os/manual/applications/).
- **Apps**: Immich for Photos [[24]](https://github.com/immich-app/immich), Seafile for Drive [[25]](https://github.com/haiwen/seafile), Frigate for Surveillance Station [[26]](https://github.com/blakeblackshear/frigate), Proxmox Backup Server for Active Backup for Business [[27]](https://kb.synology.com/en-ph/DSM/tutorial/back_up_restore_proxmox_vm).
- **Remote access**: Tailscale as subnet router on the NAS (replaces QuickConnect, traverses CGNAT [[28]](https://tailscale.com/docs/features/subnet-routers)) + Cloudflare Tunnel for public services + NUT + Uptime Kuma + a smart plug — recurring cost ~$10/yr domain plus electricity [[29]](https://github.com/louislam/uptime-kuma).

Open questions left after all four angles: how much of the *DSM ergonomics tax* (1h/month TrueNAS maintenance vs. near-zero on DSM) the migrating operator is actually willing to absorb — and whether DSM 8 (still slipping past Q4 2025 [[30]](https://mariushosting.com/synology-next-dsm-update-will-be-8-0-7-3-or-7-2-3/)) ships anything that changes the calculus before the new hardware is bought.
