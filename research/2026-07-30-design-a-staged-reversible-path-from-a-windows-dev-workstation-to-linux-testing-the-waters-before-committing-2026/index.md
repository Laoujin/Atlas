---
layout: expedition
title: "Testing the waters: a staged, reversible path from a Windows dev workstation to Linux"
date: 2026-07-30
topic: "Design a staged, reversible path from a Windows dev workstation to Linux — testing the waters before committing (2026). Scope: gradual migration on a developer workstation (.NET/C# and TypeScript, homelab alongside), emphasising trial rungs you can retreat from rather than a big-bang switch. Compare: fidelity of each trial rung vs commitment/reversibility cost, setup effort, and hardware spend. Output: a rung-by-rung migration ladder with go/no-go criteria per rung, plus the mechanics and rollback path for each."
topic_raw: "gradual linux migration from Windows (first testing the waters)."
format: md
tags: [linux, windows, migration, developer-workstation, dual-boot]
summary: "Climb WSL2 → live USB → external-SSD install → commit, skip dual-boot entirely, and decide on tickable criteria against a pre-committed rollback date."
cover: cover.svg
synthesis: true
children:
  - slug: the-staged-ladder-what-each-rung-proves
    title: "The staged ladder: what each rung of a Windows→Linux move actually proves"
    depth: survey
    status: success
    summary: "A rung-by-rung ladder from WSL2 to full switch, with what each rung proves, what it structurally hides, the go/no-go signal, and the cost of retreating."
    citations: 31
    reading_time_min: 9
  - slug: wsl2-as-rung-zero-and-its-ceiling
    title: "WSL2 as rung zero — what it proves, and the exact wall it hits"
    depth: survey
    status: success
    summary: "WSL2 retires every userland risk in a Linux migration and none of the machine-ownership risks; here is where the line falls in 2026."
    citations: 38
    reading_time_min: 7
  - slug: dual-boot-without-wrecking-windows
    title: "Dual-boot Linux next to Windows in 2026 without wrecking the Windows install"
    depth: survey
    status: success
    summary: "Buy a second NVMe, keep the two OSes ignorant of each other, and pick Linux from the firmware boot menu — the layout with the smallest blast radius on your Windows install."
    citations: 30
    reading_time_min: 13
  - slug: dropbox-on-linux-and-shared-folders
    title: "Dropbox on Linux and shared folders: what actually works in 2026"
    depth: survey
    status: success
    summary: "The official Linux client now supports btrfs/zfs/xfs, but you cannot share one Dropbox folder between a Windows and a Linux install, and code repos do not belong in Dropbox at all."
    citations: 34
    reading_time_min: 11
  - slug: trial-hardware-and-vm-paths
    title: "Trial hardware and VM paths for evaluating Linux before you commit (2026)"
    depth: survey
    status: success
    summary: "Live USB first (€10, 15 minutes, proves your actual hardware), then a full install on an external NVMe SSD (€90–150) — everything else is a detour."
    citations: 45
    reading_time_min: 12
  - slug: living-in-both-oses-during-the-overlap
    title: "Living in both OSes: running Windows and Linux for months without your setup rotting"
    depth: survey
    status: success
    summary: "One source of truth per asset class, replicated by a tool that knows the OS difference — never a shared partition and never two hand-edited copies."
    citations: 37
    reading_time_min: 14
  - slug: exit-criteria-and-the-blocker-inventory
    title: "Exit criteria and the blocker inventory: decide the Linux switch on evidence, not vibes"
    depth: recon
    status: success
    summary: "A fill-in blocker inventory plus tickable go/no-go criteria and a pre-committed rollback date for a Windows-to-Linux workstation trial."
    citations: 8
    reading_time_min: 3
model: "Opus 5"
cost_usd: "sub"
issue: 14
duration_sec: 738
---

Seven angles, one spine: **a migration asks two independent questions, and almost every "try Linux safely" option answers only one.** Does your *software* survive — .NET SDK, Node/TS, Docker, git, shell? And does your *machine* survive — suspend/resume, Wi-Fi, GPU, docking, battery, the desktop itself? Everything virtualised answers the first at near-perfect fidelity and the second at zero: WSL2 blocks kernel modules, routes USB through `usbipd`, and hands you a NAT adapter with a fresh IP each restart [[1]](https://learn.microsoft.com/en-us/windows/wsl/compare-versions). A live USB inverts it — 15 minutes, €10, and it tells you whether *your* Wi-Fi and dock enumerate at all [[2]](https://ubuntu.com/tutorials/try-ubuntu-before-you-install).

That split produces a convergent recommendation the angles reached independently: **WSL2 → live USB → full install on an external NVMe SSD → commit**, with dual-boot skipped. The external SSD is the only rung that is simultaneously full-fidelity and zero-commitment — real kernel, real drivers, real four-week trial, and undo means unplugging [[3]](https://www.ghacks.net/2025/07/11/how-to-install-linux-on-an-external-ssd/). Single-disk dual-boot buys nothing it doesn't, at the price of partition surgery, a documented BitLocker recovery trigger [[4]](https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery-overview), and Windows updates that have broken Linux boot before [[5]](https://www.bleepingcomputer.com/news/microsoft/microsoft-confirms-august-updates-break-linux-boot-in-dual-boot-systems/). If you do want Linux inside the chassis, the dual-boot angle's layout — second physical disk, its own ESP, F12 to switch, Secure Boot left on — is the version with the smallest blast radius [[6]](https://wiki.archlinux.org/title/Dual_boot_with_Windows).

**Where the angles disagree:** how long to sit on WSL2. The WSL2 deep-dive argues 3–6 months to fully retire userland risk; the ladder says 2–4 weeks, because WSL2 cannot start answering the hardware question and time spent there is time the real risk stays untested. Take the shorter number if your hardware is unknown, the longer one if it's on Ubuntu's certified list [[7]](https://ubuntu.com/certified).

**The theme that repeats three times, from three directions:** a git working tree belongs on a native Linux filesystem owned by one OS. Under `/mnt/c` it is ~34× slower on random reads [[8]](https://github.com/webbertakken/wsl-filesystem-benchmark). On a shared NTFS partition it loses the exec bit, case-sensitivity and symlinks — and the in-kernel `ntfs3` driver is being actively re-litigated on LKML in 2026 [[9]](https://lkml.iu.edu/2601.1/06496.html). In a sync folder, concurrent changes "can result in a corrupted Git repository" [[10]](https://github.com/anishathalye/git-remote-dropbox). Same rule, three failure modes.

One correction worth flagging: Dropbox's ext4-only rule ended in 2019 — btrfs, zfs and xfs are officially supported [[11]](https://help.dropbox.com/installs/system-requirements), so btrfs snapshots are not blocked. The real hazard is subtler: rolling back a subvolume containing `~/Dropbox` looks like mass deletion to the client, and in a *shared* folder deletions propagate to everyone [[12]](https://help.dropbox.com/delete-restore/delete-files). Keep `~/Dropbox` on a subvolume Timeshift doesn't touch. And you cannot point Windows Dropbox and Linux Dropbox at one partition — the overlap needs two linked installs [[13]](https://community.dropbox.com/en/discussion/793218/how-to-share-a-dropbox-folder-between-windows-and-linux-installs-on-the-same-pc).

The sharpest open question none of this resolves: whether *your specific machine* suspends, docks and drives external displays cleanly. That is empirical, it costs one evening and a USB stick, and every downstream decision is gated on it.
