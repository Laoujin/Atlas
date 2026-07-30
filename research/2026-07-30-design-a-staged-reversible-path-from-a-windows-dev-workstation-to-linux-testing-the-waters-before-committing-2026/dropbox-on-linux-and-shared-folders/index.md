---
title: "Dropbox on Linux and shared folders: what actually works in 2026"
date: 2026-07-30
depth: standard
format: md
topic: "Dropbox on Linux and shared folders (2026) — official client support and filesystem restrictions, shared-folder behaviour across accounts, selective sync, case-sensitivity and symlink handling, and the alternatives (Maestral, rclone, Syncthing, dbxfs) when the official client will not do."
topic_raw: "gradual linux migration from Windows (first testing the waters)."
tags: [dropbox, linux, migration, dual-boot, sync, btrfs, git]
summary: "The official Linux client now supports btrfs/zfs/xfs, but you cannot share one Dropbox folder between a Windows and a Linux install, and code repos do not belong in Dropbox at all."
citations: 34
reading_time_min: 11
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 583
issue: 14
---

> **Decision.** Run the **official Dropbox client on Linux** — btrfs, zfs and xfs are supported filesystems in 2026, so a btrfs root is not a blocker [[1]](https://help.dropbox.com/installs/system-requirements). Do **not** try to point Windows Dropbox and Linux Dropbox at one shared partition: it is impossible, not merely unsupported [[2]](https://community.dropbox.com/en/discussion/793218/how-to-share-a-dropbox-folder-between-windows-and-linux-installs-on-the-same-pc). And **move your source repos out of Dropbox** — Dropbox is not aware of git's on-disk format and concurrent changes "can result in a corrupted Git repository" [[3]](https://github.com/anishathalye/git-remote-dropbox) ⭐ 3.1k. The obvious escape hatch closed in July 2026: Maestral, the main open-source client, is archived [[4]](https://github.com/samschott/maestral) ⭐ 3.3k.

## Filesystems: official policy in 2026

The ext4-only rule is history. Dropbox announced in August 2018 that from 7 November 2018 only ext4 would sync on Linux [[5]](https://itsfoss.com/dropbox-linux-ext4-only/), because the client stores per-file identity in extended attributes and wanted a single guaranteed xattr implementation [[6]](https://www.theregister.com/2018/08/14/dropbox_encrypted_linux_support/). It reversed course in build 77.3.127 (July 2019), restoring zfs, xfs, btrfs and eCryptFS [[7]](https://itsfoss.com/dropbox-brings-back-linux-filesystem-support/).

Current official policy — the requirement is on the **filesystem holding the Dropbox folder**, not the root filesystem [[1]](https://help.dropbox.com/installs/system-requirements):

> "A Dropbox folder on a hard drive or partition, formatted with one of the following system types: ext4, zfs, eCryptFS (back by ext4), xfs, btrfs"

| Filesystem | 2026 status | Note |
|-------------------|-------------|--------------------------------------------------|
| ext4              | ✓ official  | The reference case [[1]](https://help.dropbox.com/installs/system-requirements) |
| btrfs             | ✓ official  | Restored 2019 [[7]](https://itsfoss.com/dropbox-brings-back-linux-filesystem-support/); ⚠ snapshot caveat below |
| xfs               | ✓ official  | 64-bit only when reinstated [[7]](https://itsfoss.com/dropbox-brings-back-linux-filesystem-support/) |
| zfs               | ✓ official  | 64-bit only when reinstated [[7]](https://itsfoss.com/dropbox-brings-back-linux-filesystem-support/) |
| eCryptFS          | ✓ official  | Only when "backed by ext4" [[1]](https://help.dropbox.com/installs/system-requirements) |
| LUKS/dm-crypt home | ✓ implied  | Block-level; the visible fs is ext4/btrfs — not itself a listed type [[1]](https://help.dropbox.com/installs/system-requirements) |
| NTFS, exFAT, FAT, NFS, overlayfs, tmpfs | ✗ | Not listed → client refuses to place the folder there [[1]](https://help.dropbox.com/installs/system-requirements) |

Point the client at an unlisted filesystem and it refuses to start syncing rather than degrading — the client checks the filesystem type at the Dropbox folder path. The community workaround is [dropbox-filesystem-fix](https://github.com/dark/dropbox-filesystem-fix) ⭐ 141, an `LD_PRELOAD` shim that patches the detection call [[8]](https://github.com/dark/dropbox-filesystem-fix). Treat it as dead: the repo was archived in November 2025, is tested only up to client `89.4.278`, and its author's own advice was to switch to Maestral [[8]](https://github.com/dark/dropbox-filesystem-fix) — which is itself now archived [[4]](https://github.com/samschott/maestral) ⭐ 3.3k.

### ⚠ The btrfs snapshot conflict is real, but it is not a filesystem-support problem

btrfs is supported. The collision is with **snapshot rollback semantics**. Dropbox has no notion of "this whole tree just went back in time": rolling back a subvolume that contains `~/Dropbox` presents the client with a mass of deletions and reverted files, which it dutifully pushes upstream. In a *shared* folder that is not a local event — "If you delete a file inside a shared folder... that file disappears from the shared folder for everyone" [[9]](https://help.dropbox.com/delete-restore/delete-files). This is an inference from documented delete semantics, not a documented Dropbox statement, but the failure mode is exactly what makes it dangerous.

Mitigation: put `~/Dropbox` on its own btrfs subvolume that Timeshift/snapper do **not** snapshot, and use Dropbox's own version history / Rewind as the time machine for that tree instead [[10]](https://help.dropbox.com/delete-restore/recover-deleted-files-folders).

## Feature parity vs the Windows client

| Feature | Windows | Linux | Evidence |
|-------------------------------|---------|-------|----------|
| Smart Sync / online-only files | ✓ | ✗ | Documented for Windows 7+ and macOS 10.12+ only [[11]](https://help.dropbox.com/installs-integrations/sync-uploads/smart-sync); long-standing unanswered feature request [[12]](https://www.dropboxforum.com/discussions/101001014/when-will-online-only-files-work-on-linux/262171) |
| Selective sync | ✓ | ✓ | Per-device, folders only — you cannot exclude individual files [[13]](https://help.dropbox.com/sync/selective-sync-overview) |
| Ignore (keep local, drop from cloud) | ✓ | ✓ | `attr -s com.dropbox.ignored -V 1 <path>` [[14]](https://help.dropbox.com/sync/ignored-files) |
| CLI (`dropbox` / `dropbox.py`) | ✗ | ✓ | 13 commands incl. `status`, `filestatus`, `exclude`, `lansync`, `throttle`, `sharelink` [[15]](https://help.dropbox.com/installs/linux-commands) |
| Headless / no-GUI operation | ✗ | ✓ | Tarball + `~/.dropbox-dist/dropboxd`, link via pasted URL [[17]](https://www.techrepublic.com/article/how-to-install-and-run-dropbox-from-a-headless-linux-server/) |
| File-manager overlay icons | ✓ | ~ | `nautilus-dropbox` only; GTK4/Nautilus supported [[16]](https://github.com/dropbox/nautilus-dropbox) ⭐ 274. No official Dolphin/Thunar extension |
| Tray icon | ✓ | ~ | Requires LibAppIndicator 12.10+; "LXDE... can't be supported" [[18]](https://help.dropbox.com/installs/dropbox-desktop-app-for-linux) |
| LAN sync | ✓ | ✓ | IPv4 only — "If your network only supports IPv6, then you can't use LAN sync" [[1]](https://help.dropbox.com/installs/system-requirements) |
| ARM (Apple-silicon-style / Pi) | n/a | ✗ | "Dropbox doesn't support ARM processors for Linux" [[1]](https://help.dropbox.com/installs/system-requirements) |
| Officially supported distros | n/a | 2 | Ubuntu 18.04+ and Fedora 28+ 64-bit only [[18]](https://help.dropbox.com/installs/dropbox-desktop-app-for-linux) |

The Linux client's page carries a live warning — "The Dropbox desktop app for Linux is changing" — with dependency floors of GTK 2.24, GDK 2.24, Glib 2.40 and LibAppIndicator 12.10 (page last updated 9 February 2026) [[18]](https://help.dropbox.com/installs/dropbox-desktop-app-for-linux). Dropbox ships no systemd unit; autostart is handled by `dropbox autostart y` writing an XDG autostart entry [[15]](https://help.dropbox.com/installs/linux-commands). A user unit calling `~/.dropbox-dist/dropboxd` is the standard headless pattern [[17]](https://www.techrepublic.com/article/how-to-install-and-run-dropbox-from-a-headless-linux-server/).

**Net:** the Linux client's *sync engine* is at parity. What is missing is online-only files — which matters exactly when a shared folder is bigger than your disk.

## Shared folders on Linux

Shared folders behave identically to Windows at the account level; the Linux-specific pain is in what you cannot do about size and what you can accidentally do to collaborators.

- **Quota.** A shared folder counts against the quota of **every** member, unless all members are on the same Standard/Advanced/Enterprise team or Family plan, where it counts once [[19]](https://help.dropbox.com/storage-space/shared-folder-count-against-storage).
- **Folder larger than your disk.** With no Smart Sync on Linux [[11]](https://help.dropbox.com/installs-integrations/sync-uploads/smart-sync), selective sync is the only lever — and it is folder-granular, so a large shared folder with a few small files you need is all-or-nothing [[13]](https://help.dropbox.com/sync/selective-sync-overview). Deselecting is per-device, so your Windows install can keep the full copy [[13]](https://help.dropbox.com/sync/selective-sync-overview).
- **Deletes are global.** Edit permission means your delete is everyone's delete; permanent deletion needs folder ownership [[9]](https://help.dropbox.com/delete-restore/delete-files).
- **Conflicted copies.** Three documented causes: two people editing simultaneously, someone editing offline while another edits online, and a file left open in an auto-saving app. The loser is renamed with the editor's username, "conflicted copy" and the date [[20]](https://help.dropbox.com/organize/conflicted-copy). ⚠ A dual-booter is *two members* in this model: an editor open in Windows when you reboot into Linux produces exactly the "left open on another user's computer" case.
- **Device limit.** Dropbox Basic caps at three linked devices — a Windows install and a Linux install on one machine consume two of them [[21]](https://help.dropbox.com/account-access/computer-limit).

## Dual boot: can Windows and Linux share one Dropbox folder?

**No.** Not "unsupported" — arithmetically impossible under current policy. Windows Dropbox requires NTFS; Linux Dropbox requires one of ext4/zfs/xfs/btrfs/eCryptFS and NTFS is not on that list [[1]](https://help.dropbox.com/installs/system-requirements). Since the 2018 filesystem restrictions there is **no filesystem the two clients both accept**, which is precisely how the Dropbox community answers it [[2]](https://community.dropbox.com/en/discussion/793218/how-to-share-a-dropbox-folder-between-windows-and-linux-installs-on-the-same-pc).

The only correct dual-boot arrangement is **two independent Dropbox folders** — `C:\Users\you\Dropbox` on NTFS and `/home/you/Dropbox` on ext4/btrfs — both syncing to the same account through the cloud, and never booting one while the other has unsaved open files. Costs two device slots [[21]](https://help.dropbox.com/account-access/computer-limit) and a second full local copy.

## Source code in Dropbox: don't

Every one of these bites harder in a *shared* folder, because the blast radius includes other people.

**Symlinks.** Dropbox syncs a symlink pointing outside your Dropbox as "individual symlink files, and don't sync the files referenced by the symlink" [[22]](https://help.dropbox.com/sync/symlinks). Worse for a mixed team: Windows Dropbox does not support symlinks or junctions at all and flags them with error indicators [[22]](https://help.dropbox.com/sync/symlinks). So the classic "symlink `node_modules` outside Dropbox" trick leaves your Windows collaborator with a broken artefact in their tree.

**Case collisions.** Dropbox's namespace is case-insensitive — "you can't have a file called `Hello.doc` and one called `hello.doc`" [[24]](https://rclone.org/dropbox/). Linux filesystems are case-sensitive, so a repo containing `Makefile` and `makefile`, or a rename that only changes case, gets mangled on the way through Dropbox [[23]](https://shkspr.mobi/blog/2013/12/case-conflicts-in-dropbox-for-linux/). Also note `\ / : * ? " < > |` are restricted and names cap around 255 characters including path [[34]](https://help.dropbox.com/organize/file-names).

**`.git` corruption.** The authoritative statement comes from git-remote-dropbox's author: "The desktop client is not aware of how Git manages it's on-disk format, so if there are concurrent changes or delays in syncing, it's possible to have conflicts that result in a corrupted Git repository" [[3]](https://github.com/anishathalye/git-remote-dropbox) ⭐ 3.1k. Packfile rewrites during `gc`, `HEAD`/index churn and ref updates are all racy against a background syncer.

**Churn and watches.** `node_modules`, `bin/`, `obj/` and `.next/` generate thousands of short-lived files. Each watched directory costs one inotify watch; the historic default `max_user_watches` was 8192 and Dropbox support recommends 100000, though kernels ≥5.11 auto-scale to 1048576 on machines with ≥8 GB RAM [[25]](https://maestral.app/docs/inotify-limits).

**Exclusion is blunt.** There is no `.dropboxignore` pattern file. Selective sync is folder-granular and per-device [[13]](https://help.dropbox.com/sync/selective-sync-overview); `com.dropbox.ignored` is set per file or folder, is not pattern-based, requires the Dropbox folder in its default location, and — critically — the ignored content "will be deleted from the Dropbox server and your other devices" [[14]](https://help.dropbox.com/sync/ignored-files). ⚠ Inside a *shared* folder that means your collaborators lose it too [[9]](https://help.dropbox.com/delete-restore/delete-files).

**Recommendation:** code lives in git, hosted on a remote (GitHub/Gitea), cloned to `~/code` **outside** Dropbox on every machine. Dropbox stays for documents and for the shared folders you cannot control. If a repo genuinely must live in a Dropbox shared folder, use [git-remote-dropbox](https://github.com/anishathalye/git-remote-dropbox) ⭐ 3.1k, which talks to the Dropbox API directly and does not require the desktop client [[3]](https://github.com/anishathalye/git-remote-dropbox).

## Alternatives

| Tool | ⭐ Stars | FS freedom | Shared folders | Selective sync | Headless | Maintained (Jul 2026) | Cost |
|------|---------|-----------|----------------|----------------|----------|----------------------|------|
| Official Dropbox client | n/a | ext4/zfs/xfs/btrfs/eCryptFS [[1]](https://help.dropbox.com/installs/system-requirements) | ✓ full | ✓ folder-level [[13]](https://help.dropbox.com/sync/selective-sync-overview) | ✓ [[17]](https://www.techrepublic.com/article/how-to-install-and-run-dropbox-from-a-headless-linux-server/) | ✓ [[18]](https://help.dropbox.com/installs/dropbox-desktop-app-for-linux) | Free tier, 3 devices [[21]](https://help.dropbox.com/account-access/computer-limit) |
| [Maestral](https://maestral.app/) | ⭐ 3.3k | ✓ any (no xattr requirement) [[26]](https://maestral.app/) | ✓ syncs them, ✗ can't manage share settings [[27]](https://maestral.app/about/) | ✓ + `.mignore` gitignore patterns [[26]](https://maestral.app/) | ✓ CLI-first [[26]](https://maestral.app/) | ✗ **archived 2026-07-28** [[4]](https://github.com/samschott/maestral) | Free |
| [rclone](https://rclone.org/dropbox/) | ⭐ 58.8k | ✓ any | ✓ via `--dropbox-shared-folders` [[24]](https://rclone.org/dropbox/) | ✓ filters/paths | ✓ | ✓ | Free |
| [Syncthing](https://syncthing.net/) | ⭐ 87.1k | ✓ any | ✗ **does not touch Dropbox at all** [[29]](https://syncthing.net/) | ✓ `.stignore` | ✓ | ✓ | Free |
| [dbxfs](https://thelig.ht/code/dbxfs/) | ⭐ 690 | ✓ FUSE mount | ~ read/write mount, no sync engine [[30]](https://thelig.ht/code/dbxfs/) | n/a (nothing stored locally) | ✓ | ~ v2.0.1; GitHub mirror archived 2021 [[31]](https://github.com/rianhunter/dbxfs) | Free |
| [Insync](https://www.insynchq.com/linux) | n/a (closed source) | ✓ any | ✓ incl. Dropbox team folders [[33]](https://www.insynchq.com/linux) | ✓ | ✓ (Server plan) | ✓ commercial | $39.99 one-time per cloud account, unlimited machines [[32]](https://www.insynchq.com/pricing) |

Reading the table:

- **Maestral is out.** It was the answer to "official client won't run on my filesystem" and to the 3-device cap, but the repo was archived on 2026-07-28 with the site stating "As of June 2026, Maestral is no longer actively maintained" and warning the client works only "until certificates expire" [[26]](https://maestral.app/) [[4]](https://github.com/samschott/maestral). Do not build a migration on it.
- **rclone is a copier, not a client.** `bisync` does two-way sync but the manual is blunt: "Bisync is considered an advanced command, so use with care... or data loss can result" [[28]](https://rclone.org/bisync/), and a third party adding a file mid-run can force a full `--resync`. Dropbox-specific limits apply too: mtimes only settable by re-upload, `>10000`-file directories can't be purged directly [[24]](https://rclone.org/dropbox/). Fine for scheduled one-way backup; wrong for a live shared folder with collaborators.
- **Syncthing cannot replace Dropbox for shared folders.** It has no server — "none of your data is ever stored anywhere else other than on your computers" [[29]](https://syncthing.net/) ⭐ 87.1k. It is the right tool for *your own* machines, and useless for a folder shared with someone else's Dropbox account.
- **dbxfs is the only "online-only" answer.** A FUSE mount gives you the whole account without local disk, which is the Smart Sync gap [[30]](https://thelig.ht/code/dbxfs/) — but latency makes it unusable as a working directory, and its GitHub mirror is archived [[31]](https://github.com/rianhunter/dbxfs) ⭐ 690.
- **Insync is the paid escape hatch** for filesystem freedom plus real shared/team-folder support, at $39.99 once per cloud account with unlimited machines [[32]](https://www.insynchq.com/pricing) [[33]](https://www.insynchq.com/linux).

## Recommended arrangement

1. **Official Dropbox client on Linux.** btrfs root is fine [[1]](https://help.dropbox.com/installs/system-requirements). Stick to Ubuntu or Fedora if you want supportability [[18]](https://help.dropbox.com/installs/dropbox-desktop-app-for-linux).
2. **`~/Dropbox` on its own btrfs subvolume, excluded from Timeshift/snapper.** Snapshot rollback of a shared folder deletes files for collaborators [[9]](https://help.dropbox.com/delete-restore/delete-files); use Dropbox version history for that tree [[10]](https://help.dropbox.com/delete-restore/recover-deleted-files-folders).
3. **Two separate Dropbox folders across the dual boot**, syncing through the cloud. One shared on-disk folder is not possible [[2]](https://community.dropbox.com/en/discussion/793218/how-to-share-a-dropbox-folder-between-windows-and-linux-installs-on-the-same-pc). Budget two of the three Basic device slots [[21]](https://help.dropbox.com/account-access/computer-limit).
4. **Never leave editors open across a reboot** — that is the documented conflicted-copy trigger [[20]](https://help.dropbox.com/organize/conflicted-copy).
5. **Move all repos to `~/code`, outside Dropbox**, and push to a git remote. Case collisions [[23]](https://shkspr.mobi/blog/2013/12/case-conflicts-in-dropbox-for-linux/), broken symlinks on Windows peers [[22]](https://help.dropbox.com/sync/symlinks) and `.git` corruption [[3]](https://github.com/anishathalye/git-remote-dropbox) are all avoided at once.
6. **Selective-sync away oversized shared folders on the Linux side** while Windows keeps the full copy — it is per-device [[13]](https://help.dropbox.com/sync/selective-sync-overview). Add dbxfs as a read-mostly window onto what you excluded [[30]](https://thelig.ht/code/dbxfs/).
7. **Syncthing for `~/code` and dotfiles between your own machines** [[29]](https://syncthing.net/) ⭐ 87.1k, and a nightly `rclone` one-way copy of `~/Dropbox` to homelab storage as an independent backup [[24]](https://rclone.org/dropbox/) ⭐ 58.8k. Reserve `rclone bisync` for cases you have read the limitations section for [[28]](https://rclone.org/bisync/).
8. **Budget for Insync** only if you later need Dropbox on an unsupported filesystem or a distro Dropbox won't run on [[32]](https://www.insynchq.com/pricing).
