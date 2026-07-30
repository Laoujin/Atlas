---
title: "Proxmox as the isolation boundary for Claude Code: KVM VM, not LXC"
date: 2026-07-30
depth: deep
format: md
topic: "Proxmox VE as the isolation boundary for an agentic coding CLI (2026). Decide whether to move Claude Code off the Linux daily driver and onto a dedicated guest on an existing Proxmox mini PC. Cover: KVM VM vs LXC container for this workload (privileged vs unprivileged LXC, nesting for Docker-in-LXC, what an unprivileged LXC actually protects against vs a full VM, and the documented consensus that LXC is not a security boundary against untrusted root); remote-dev wiring that keeps the workflow usable — plain SSH + tmux, VS Code Remote-SSH, JetBrains Gateway, `code tunnel`, Mosh, and running Claude Code headless/`-p` with results pulled back; how the repo gets there (git clone in the guest vs NFS/SMB/virtiofs/sshfs mount from the workstation, and the risk that a mount re-widens the blast radius); snapshots and ZFS/LVM-thin rollback as a real undo button (cost, speed, automation via `qm snapshot`/`pct snapshot`, and the caveat about snapshotting a running guest); resource sizing on a mini PC (RAM/vCPU/disk for Node + a build toolchain + a dev server, and what happens when the agent runs a heavy test suite); network segmentation with a VLAN/bridge + firewall rules at the Proxmox or OPNsense level so the guest cannot reach the rest of the LAN; where the workstation still has to be trusted (SSH agent forwarding = a hole, clipboard, X11/Wayland forwarding); and the friction verdict vs. sandboxing locally. Include a concrete build recipe (guest type, specs, provisioning steps, firewall rules, snapshot policy)."
topic_raw: "switching from windows to linux. on my system, I'm also going to run Claude. for my homelab I'm using proxmox on the minipc to \"separate\" systems. for running claude \"safely\", what can I do there?"
tags: [proxmox, lxc, kvm, claude-code, isolation, homelab, remote-development, snapshots, firewall]
summary: "Use a KVM VM, never an LXC: Proxmox's own docs say containers share the host kernel and LXC upstream says privileged containers cannot be root-safe — plus the wiring, firewall rules, snapshot policy and sizing to make a dedicated agent guest actually usable."
citations: 42
reading_time_min: 24
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 828
issue: 12
---

> **Decision.** Build a **KVM VM**, not an LXC container. Proxmox's own container docs say plainly that "Containers use the kernel of the host system. This exposes an attack surface for malicious users. In general, full virtual machines provide better isolation" [[1]](https://pve.proxmox.com/wiki/Linux_Container), LXC upstream says privileged containers "aren't and cannot be root-safe" [[2]](https://linuxcontainers.org/lxc/security/), and Anthropic's own guidance sends untrusted repositories to "a dedicated virtual machine" for "kernel-level separation" [[3]](https://code.claude.com/docs/en/sandbox-environments). Wire it up with **plain SSH + tmux as the primary interface** (Mosh if you want it to survive a suspended laptop [[21]](https://mosh.org/)) and VS Code Remote-SSH as the comfortable second. **Clone the repo inside the guest** — do not mount your workstation's home into it. Use **disk-only ZFS/LVM-thin snapshots** as the undo button; they roll back in seconds and cost almost nothing [[5]](https://pve.proxmox.com/pve-docs/chapter-pvesm.html). Enforce isolation with the **Proxmox guest-NIC firewall**, which runs host-side as iptables and therefore cannot be switched off from inside the guest [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html). Friction verdict: worth it for untrusted repos and unattended `--dangerously-skip-permissions` runs; overkill as your only environment if you spend the day in a GUI IDE.

---

## 1. Guest type: the decision table

The mini PC is a given. The only real question is what shape the guest takes.

| Axis | Unprivileged LXC | Privileged LXC | KVM VM |
|---|---|---|---|
| Kernel | Shared with host [[1]](https://pve.proxmox.com/wiki/Linux_Container) | Shared with host [[1]](https://pve.proxmox.com/wiki/Linux_Container) | Own kernel [[3]](https://code.claude.com/docs/en/sandbox-environments) |
| Escape needs | A generic kernel bug; lands as an unprivileged host UID [[1]](https://pve.proxmox.com/wiki/Linux_Container) [[2]](https://linuxcontainers.org/lxc/security/) | A container-escape bug that upstream **will not treat as a CVE** [[7]](https://pve.proxmox.com/pve-docs/chapter-pct.html) | A hypervisor bug (much smaller surface) [[12]](https://northflank.com/blog/how-to-sandbox-ai-agents) |
| Vendor position for untrusted code | "full virtual machines provide better isolation" [[1]](https://pve.proxmox.com/wiki/Linux_Container) | "unsafe" per the LXC team [[7]](https://pve.proxmox.com/pve-docs/chapter-pct.html) | ✓ recommended [[3]](https://code.claude.com/docs/en/sandbox-environments) [[7]](https://pve.proxmox.com/pve-docs/chapter-pct.html) |
| Docker inside | ✗ broken on current kernels [[8]](https://dev.to/mattercoder/docker-on-proxmox-lxc-what-actually-works-and-why-unprivileged-doesnt-45km) | ⚠ works with `nesting`+`keyctl`+`fuse`, unsupported [[6]](https://forum.proxmox.com/threads/docker-in-unpriviledged-lxc-or-dedicated-vm.156369/) | ✓ plain install |
| Snapshot + rollback | ✓ `pct snapshot` [[25]](https://pve.proxmox.com/pve-docs/pct.1.html) | ✓ `pct snapshot` [[25]](https://pve.proxmox.com/pve-docs/pct.1.html) | ✓ `qm snapshot`, optional RAM state [[24]](https://pve.proxmox.com/pve-docs/qm.1.html) |
| RAM overhead | ~0 | ~0 | ~200 MB + a boot delay [[8]](https://dev.to/mattercoder/docker-on-proxmox-lxc-what-actually-works-and-why-unprivileged-doesnt-45km) |
| Host firewall applies | ✓ [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html) | ✓ [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html) | ✓ [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html) |

The ~200 MB and a couple of seconds of boot are the entire price of the VM. That is the cheapest security upgrade in this whole document.

### What an unprivileged LXC actually protects against

Worth being precise, because "unprivileged LXC is fine" is the most common homelab answer and it is *half* right.

An **unprivileged** container maps container UID 0 to a high unprivileged UID on the host (typically 100000+), so "most security issues (container escape, resource abuse, etc.) in these containers will affect a random unprivileged user, and would be a generic kernel security bug" [[1]](https://pve.proxmox.com/wiki/Linux_Container). LXC upstream calls them "safe by design" and frames residual holes as kernel bugs rather than LXC bugs [[2]](https://linuxcontainers.org/lxc/security/).

So an unprivileged LXC protects you against:

- an agent running `rm -rf /` **inside** the container — the host filesystem is untouched;
- an agent that trashes its own package tree, node toolchain, or git checkout;
- an accidentally-`chmod 777`'d file becoming a host root escalation.

It does **not** protect against:

- a **kernel-level** exploit — the guest and host are the same kernel, one bug away [[1]](https://pve.proxmox.com/wiki/Linux_Container);
- what you had to switch off to make it useful (next section);
- anything on your LAN — that is a firewall problem, not a container problem.

Proxmox forum framing is that LXC is a "semi-isolated" environment and containers "can leak or interfere with the host under extreme conditions" because they run directly on it [[41]](https://forum.proxmox.com/threads/vm-or-lxc.151626/).

### The nesting trap: Docker-in-LXC erodes the boundary you came for

Your workload is Node plus a build toolchain plus probably Docker (devcontainers, a Postgres for tests). That's where LXC collapses.

- On **unprivileged** LXC with a current Proxmox kernel, Docker does not work at all: runc 1.2+ unconditionally writes `net.ipv4.ip_unprivileged_port_start=0`, which needs `CAP_NET_ADMIN` over the namespace, and Docker's startup probe of `/sys/kernel/security/apparmor/profiles` is host-root-owned and unreachable from an unprivileged user namespace — "no configuration change can overcome this fundamental namespace limitation" [[8]](https://dev.to/mattercoder/docker-on-proxmox-lxc-what-actually-works-and-why-unprivileged-doesnt-45km).
- To make it work you go **privileged** and set `nesting=1`, `keyctl=1`, `fuse=1`, plus `lxc.apparmor.profile: unconfined` and cleared capability drops. The same author's verdict: privileged LXC Docker is "a performance choice, not security choice" — container root *is* host root with no user-namespace isolation [[8]](https://dev.to/mattercoder/docker-on-proxmox-lxc-what-actually-works-and-why-unprivileged-doesnt-45km).
- Proxmox staff on the forum, on Docker as root in an unprivileged LXC: "it can still be possible to break out of the LXC when nesting is enabled" [[9]](https://forum.proxmox.com/threads/root-docker-in-unprivileged-lxc-safe-or-not.93548/).
- And bluntly, in the Docker-in-LXC-vs-VM thread: "Don't use docker inside an lxc, this isn't really supported and might break at any time" / "For best isolation, use QEMU/KVM VMs for Docker, as it is stated in the documentation" [[6]](https://forum.proxmox.com/threads/docker-in-unpriviledged-lxc-or-dedicated-vm.156369/).
- The container chapter itself says that "for use cases demanding maximum isolation and the ability to live-migrate, nesting containers inside a Proxmox QEMU VM remains a recommended practice" [[7]](https://pve.proxmox.com/pve-docs/chapter-pct.html).

Also note FUSE: Proxmox "strongly advise[s] against" FUSE mounts inside a container because containers must be frozen for suspend/snapshot-mode backups [[1]](https://pve.proxmox.com/wiki/Linux_Container) — which directly conflicts with using snapshots as your undo button.

### Why the threat model justifies a kernel boundary at all

Two data points, both 2026, both about the failure mode that matters here — the agent executing hostile third-party code rather than the agent itself misbehaving:

- The Mastra npm compromise (17 June 2026) poisoned 140+ packages across the `mastra` / `@mastra` scopes with a typosquat of `dayjs`; a `postinstall` hook ran a 4,572-byte obfuscated dropper that disabled TLS verification, pulled a second stage, and harvested browser data, host reconnaissance, and "credentials and tokens present on developer workstations" [[14]](https://www.microsoft.com/en-us/security/blog/2026/06/17/postinstall-payload-inside-mastra-npm-supply-chain-compromise/). A single `npm install` in your agent's session is enough.
- Academic work now measures frontier-model capability at escaping container sandboxes specifically, evaluating whether models identify and exploit container misconfigurations and generate boundary-bypassing techniques [[13]](https://arxiv.org/pdf/2603.02277).

Practitioner consensus tracks this. A 2026 Hacker News survey of agent sandboxing found the field split between containers and "YOLO" with a minority on hypervisors [[11]](https://news.ycombinator.com/item?id=47185250); the "how are you sandboxing your coding agents" thread contains everything from "I use a physically separate system. i.e. DEV and PROD are completely airgapped" to "Currently I'm using docker-ized git worktrees so I can dangerously skip permissions. It's not great" [[10]](https://news.ycombinator.com/item?id=46700628). Sandbox-infrastructure vendors are explicit that standard containers are "insufficient for untrusted code" and point to microVMs (Firecracker ~125 ms boot, <5 MiB overhead per VM) for hardware-enforced isolation [[12]](https://northflank.com/blog/how-to-sandbox-ai-agents). You already own a hypervisor; you don't need Firecracker.

---

## 2. Sizing on a mini PC

Proxmox itself wants very little: minimum 1 GB RAM, recommended "2 GB for the OS and Proxmox VE services, plus designated memory for guests" [[15]](https://pve.proxmox.com/wiki/System_Requirements). The trap on a mini PC is **ZFS ARC**, the in-RAM read cache: on installs from PVE 8.1 onward it defaults to 10% of host memory clamped to 16 GiB, and the sizing rule of thumb is 2 GiB base plus 1 GiB per TiB of pool [[16]](https://pve.proxmox.com/wiki/ZFS_on_Linux). On pre-8.1 installs it may still be uncapped at 50%+ of RAM, which will quietly starve your guest — check `/etc/modprobe.d/zfs.conf` and set `options zfs zfs_arc_max=<bytes>` [[16]](https://pve.proxmox.com/wiki/ZFS_on_Linux).

| Resource | Recommendation | Why |
|---|---|---|
| vCPU | 4 cores, `cpulimit` unset | `cores` is what the guest sees; `cpulimit` caps total host CPU time as a fraction (1.0 = 100%, so 4 cores can draw up to 400%) [[17]](https://pve.proxmox.com/pve-docs/chapter-qm.html). A test suite that saturates 4 cores is exactly what you want offloaded from your desktop. |
| RAM | 8 GB fixed (min = max) | Set minimum = maximum so Proxmox allocates it directly rather than ballooning [[17]](https://pve.proxmox.com/pve-docs/chapter-qm.html). `tsc` heap scales with type surface, not code size — 61 MB on an empty project, 465 MB once `aws-sdk` types are in scope — and large projects "run very close to the node memory limit, and would frequently just go out of memory" [[42]](https://swatinem.de/blog/optimizing-tsc/). Stack a language server, jest workers and a dev server on that and 4 GB is not enough. |
| Disk | 64–100 GB, `virtio-scsi single` + IO thread, `discard=on`, `ssd=1` | Current best practice per the docs; `discard` lets the guest TRIM so thin-provisioned images shrink after the agent's `node_modules` churn [[17]](https://pve.proxmox.com/pve-docs/chapter-qm.html). |
| Storage backend | ZFS or LVM-thin | Both do native block-level snapshots; qcow2-on-directory/NFS snapshots "block a running VM" and can take minutes-to-hours on large disks [[5]](https://pve.proxmox.com/pve-docs/chapter-pvesm.html). |
| Host headroom | Leave ARC max + guest RAM + ~15% unallocated | Ballooning under host pressure can push a guest into swap or the OOM killer [[17]](https://pve.proxmox.com/pve-docs/chapter-qm.html). |

⚠ **Do not enable ballooning for this guest.** Dynamic allocation reclaims memory when host usage crosses ~80%, and the balloon driver releasing RAM mid-build is how you get a mysterious `heap out of memory` in the middle of an agent run [[17]](https://pve.proxmox.com/pve-docs/chapter-qm.html).

If you also want a **JetBrains Gateway** backend in there, budget more. JetBrains' guidance for larger projects is simply "add more CPUs and RAM. The load average indication in the IDE will tell you if an upgrade would be advisable", plus "Enabling Swap is recommended. Even on cloud instances" and local SSD storage [[20]](https://www.jetbrains.com/help/idea/prerequisites.html).

---

## 3. Remote-dev wiring: keeping it usable

This is where the plan lives or dies. Six options, ranked by how much of your trust they move into the guest.

| Wiring | Persists across disconnect | GUI editor | Extra trust surface | Verdict |
|---|---|---|---|---|
| SSH + `tmux` | ✓ (tmux) | ✗ | None beyond sshd | **Primary.** Claude Code is a TUI; this is its native habitat. |
| Mosh + `tmux` | ✓✓ (roams networks, survives laptop sleep) | ✗ | UDP 60000–61000 open to the guest [[21]](https://mosh.org/) | Add it if you close the lid mid-run. Auth is still SSH — Mosh "logs in to the server via SSH" then hands off to UDP [[21]](https://mosh.org/). |
| VS Code Remote-SSH | ✗ (server survives, UI reconnects) | ✓ | VS Code Server runs **as the user you signed in with** and workspace extensions get "full access to the source code, remote filesystem, and remote APIs" [[18]](https://code.visualstudio.com/docs/remote/faq) | Comfortable second. Needs kernel ≥ 4.18, glibc ≥ 2.28, libstdc++ ≥ 3.4.25 in the guest [[18]](https://code.visualstudio.com/docs/remote/faq). |
| `code tunnel` | ✗ | ✓ (browser) | Outbound connection to a Microsoft-hosted Azure service, GitHub/Microsoft account on both ends [[19]](https://code.visualstudio.com/docs/remote/tunnels) | ⚠ Skip on a LAN. It exists to traverse firewalls you don't have, and it adds a third-party relay plus a linked identity. |
| JetBrains Gateway | ✓ (backend persists) | ✓ | Full IDE backend in the guest; sizing per above [[20]](https://www.jetbrains.com/help/idea/prerequisites.html) | Only if Rider/IDEA is non-negotiable. Heaviest option. |
| `claude -p` headless + pull results | n/a (batch) | ✗ | None | **The unattended path.** See below. |

### The terminal-first setup, concretely

Practitioner reference point: a February 2026 write-up of exactly this shape — Claude Code driven over `mosh` + `tmux`, with shell config auto-attaching on login ("every time I SSH into the work PC, I want to land directly in a tmux session. If the session already exists, attach to it") and Claude Code's hook system firing notifications to a self-hosted ntfy on task completion, errors, and questions [[22]](https://rogs.me/2026/02/claude-code-from-the-beach-my-remote-coding-setup-with-mosh-tmux-and-ntfy/). The friction they report is mobile-specific (tmux mouse mode, phone keyboards) — from a desktop over LAN it's just a terminal.

Add to `~/.bashrc` in the guest:

```bash
# land in a persistent session on every login
if [[ -z "$TMUX" && -n "$SSH_CONNECTION" ]]; then
  tmux new-session -A -s agent
fi
```

### The headless path

For anything you'd otherwise run with `--dangerously-skip-permissions`, don't sit in front of it — drive it as a batch job and read the result:

```bash
ssh agentvm 'cd ~/src/myrepo && claude --bare -p "run the test suite and fix failures" \
  --allowedTools "Bash,Read,Edit" --output-format json' | jq -r '.result'
```

`-p`/`--print` runs the same agent loop non-interactively and exits; `--output-format json` returns the result plus session ID, usage and `total_cost_usd`; `--bare` skips auto-discovery of hooks, plugins, MCP servers and `CLAUDE.md` so the run is reproducible and only your explicit flags apply [[23]](https://code.claude.com/docs/en/headless). `--resume "$session_id"` continues a specific conversation from the same directory [[23]](https://code.claude.com/docs/en/headless).

Two useful Proxmox-side hatches that need no SSH at all, because they go **host → guest** over the QEMU guest agent channel: `qm guest exec <vmid> -- <cmd>` executes a command in the guest and `qm guest exec-status <vmid> <pid>` polls it [[24]](https://pve.proxmox.com/pve-docs/qm.1.html). For an LXC the equivalents are `pct exec` and `pct enter` [[25]](https://pve.proxmox.com/pve-docs/pct.1.html). Handy for recovery when you've firewalled yourself out.

⚠ `--dangerously-skip-permissions` is blocked when running as root on Linux, and the check is skipped only inside a *recognized* sandbox [[39]](https://code.claude.com/docs/en/sandboxing) — so provision a normal non-root user in the guest, not root.

---

## 4. Getting the repo in — and why a mount undoes the whole exercise

| Method | Blast radius | Perf on `node_modules` | Verdict |
|---|---|---|---|
| `git clone` in the guest | Only what's cloned | Native | ✓ **Do this.** |
| virtiofs directory mapping | Everything under the mapped host path, at host permissions | ⚠ community testing: "significantly slower than NFS" [[26]](https://forum.proxmox.com/threads/proxmox-8-4-virtiofs-virtiofs-shared-host-folder-for-linux-and-or-windows-guest-vms.167435/) | ✗ for source; fine for a read-only asset drop. |
| NFS from the workstation | Every exported path, writable | Best of the network options; NFS "dominated small random operations" in head-to-head testing [[27]](https://blog.jklr.org/2019/08/27/nas-performance-sshfs-nfs-smb.html) | ✗ — see below. |
| SMB | Same as NFS | Mid | ✗ |
| sshfs from the guest → workstation | Whatever that SSH account can reach | "fastest from the encrypted options" but FUSE + chatty [[27]](https://blog.jklr.org/2019/08/27/nas-performance-sshfs-nfs-smb.html) | ✗ — and it requires the guest to hold a credential *to your workstation*, the exact inversion you're trying to avoid. |
| LXC bind mount | Host directory, directly | Native | ✗ — and Proxmox: "Never bind mount system directories like `/`, `/var` or `/etc` into a container - this poses a great security risk" [[7]](https://pve.proxmox.com/pve-docs/chapter-pct.html) |

The whole point of the guest is that the agent's reachable filesystem is small and disposable. **Every mount is a hole punched back through the boundary you just built.** A writable mount of `~/projects` means a compromised agent can plant a `postinstall` hook, a `.git/hooks/pre-commit`, or an executable on your workstation's `$PATH` — Anthropic's own sandbox docs flag exactly this class of escalation for local sandboxes ("Allowing writes to directories containing executables in `$PATH`, system configuration directories, or user shell configuration files such as `.bashrc` or `.zshrc` can lead to code execution in different security contexts") [[39]](https://code.claude.com/docs/en/sandboxing).

So: **clone from the forge, not from your laptop.** Give the guest a per-repo **deploy key** — "an SSH key that grants access to a single repository", read-only by default, with the private half living on the server [[36]](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys). If the agent needs to push, use a second write-enabled deploy key or a fine-grained token scoped to that one repo. Note the documented downsides you're accepting: deploy keys have no passphrase and no expiry, so rotate them [[36]](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys).

Move results back out with `scp`/`rsync` **initiated from the workstation** (pull, don't push), or just `git push` a branch from the guest and review the diff on your side.

---

## 5. Snapshots as a real undo button

This is the biggest practical win of putting the agent on Proxmox, and it's cheap.

**Disk-only is what you want.** `qm snapshot <vmid> <snapname>` takes a snapshot; `--vmstate` additionally dumps RAM [[24]](https://pve.proxmox.com/pve-docs/qm.1.html). Skip `--vmstate`: a RAM snapshot writes a vmstate volume the size of the guest's memory — one forum user saw a ~21 GB ZFS dataset appear per snapshot regardless of how little changed on disk [[28]](https://forum.proxmox.com/threads/solved-snapshot-vm-question-ram-no-ram.82654/). It also drags the guest's clock back to snapshot time on rollback.

The tradeoff for skipping RAM: rollback is crash-consistent — "if you snapshot without dumping the RAM and you will do a rollback, it will be as if the LXC/VM encountered a power outage and crashed" [[28]](https://forum.proxmox.com/threads/solved-snapshot-vm-question-ram-no-ram.82654/). For a dev guest that's fine; a git working tree and a `node_modules` tree recover from a hard power cut. `qm rollback` also won't auto-start the guest unless you pass `--start` (RAM snapshots start automatically) [[24]](https://pve.proxmox.com/pve-docs/qm.1.html).

**Install the guest agent anyway.** With `qemu-guest-agent` running in the guest and `qm set <vmid> --agent 1` on the host, Proxmox calls `guest-fsfreeze-freeze` and `guest-fsfreeze-thaw` around the snapshot "to improve consistency" [[29]](https://pve.proxmox.com/wiki/Qemu-guest-agent). Without it you get a crash-consistent image; with it, pending writes are flushed first. It also gives you the `qm guest exec` channel [[24]](https://pve.proxmox.com/pve-docs/qm.1.html).

**Storage matters more than the flags.** ZFS and LVM-thin do snapshots natively at block level and roll back essentially instantly. qcow2 snapshots on directory/NFS/CIFS storage "block a running VM" and on large disks "may take several minutes, or in extreme cases, even hours" — the documented workaround is to snapshot with the VM shut down [[5]](https://pve.proxmox.com/pve-docs/chapter-pvesm.html). If your mini PC is on `local-lvm` (LVM-thin) or a ZFS rpool you're already fine.

### Snapshot policy

```bash
# clean baseline, right after provisioning — never delete this one
qm snapshot 210 base --description "clean toolchain, no repos"

# pre-flight before an unattended run
qm snapshot 210 "pre-$(date +%Y%m%d-%H%M)" --description "before agent run"

# undo
qm rollback 210 base --start

# housekeeping
qm listsnapshot 210
qm delsnapshot 210 pre-20260730-0900
```

Rules of thumb:

- One immutable `base` taken before any repo is cloned.
- One `pre-<timestamp>` before each unattended/`--dangerously-skip-permissions` run; delete it once you've reviewed the diff.
- Cap it at 3–4 live snapshots. Thin/CoW snapshots are cheap to create but they pin the blocks they diverge from, so a forgotten snapshot plus a churning `node_modules` is how a 100 GB thin pool fills up.
- Containers use the identical verbs: `pct snapshot`, `pct rollback --start`, `pct listsnapshot`, `pct delsnapshot` [[25]](https://pve.proxmox.com/pve-docs/pct.1.html).
- Snapshots are an undo button, **not a backup** — they live on the same pool as the guest. Backups are a sibling concern.

---

## 6. Network segmentation: the part most homelabs get wrong

Two things the agent must not be able to reach: **the rest of your LAN**, and **the Proxmox host itself** (port 8006 web UI, port 22 SSH — a foothold there is game over).

### Enforce it at the hypervisor, not in the guest

The Proxmox firewall runs as an iptables-based service on each node rather than inside the guest [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html). That's the whole reason to use it instead of `ufw` inside the VM: an agent with root in the guest can flush the guest's own rules, but it cannot touch rules enforced on the host side of the tap device.

Structure: three levels — cluster (`/etc/pve/firewall/cluster.fw`), host (`/etc/pve/nodes/<node>/host.fw`), and per-guest (`/etc/pve/firewall/<VMID>.fw`) — and it must be enabled **both** at datacenter level (`enable: 1` under `[OPTIONS]`) **and** on the individual network device; "Each virtual network device has its own firewall enable flag" [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html). Reusable rule bundles live in `[GROUP name]` security groups and address lists in `[IPSET name]`, referenced as `+setname` [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html).

### ⚠ SDN "Simple" zones are not isolation

A tempting misread of the docs: a Simple zone "will create an isolated VNet bridge", "is not linked to a physical interface, and VM traffic is only local on each the node" [[31]](https://pve.proxmox.com/wiki/Software-Defined_Network). But the forum thread on exactly this finds that Simple zones do **not** isolate guests from each other by default — "currently simple zones don't use dedicated vrf" — and that users must layer Proxmox firewall rules at datacenter/node/VM/NIC level to get real separation, typically: accept intra-subnet, accept the gateway, drop all cross-subnet [[32]](https://forum.proxmox.com/threads/isolated-private-networks-with-sdn.137131/). Treat SDN as plumbing, and the firewall as the boundary.

### Two topologies that work

**A. Firewall-only (simplest, no VLANs, no router changes).** Guest sits on your normal `vmbr0`, and a guest-level firewall does the work. `vmbr0` is just a virtual switch that connects guests to the physical network [[30]](https://pve.proxmox.com/wiki/Network_Configuration).

`/etc/pve/firewall/210.fw`:

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: DROP

[RULES]
# inbound: only your workstation, only ssh (and mosh if you use it)
IN  ACCEPT -p tcp -dport 22 -source 192.168.1.50 -log nolog
IN  ACCEPT -p udp -dport 60000:61000 -source 192.168.1.50

# outbound: DNS + the internet, but never the LAN or the host
OUT ACCEPT -p udp -dport 53 -dest 192.168.1.1
OUT REJECT -dest 192.168.1.0/24
OUT REJECT -dest 10.0.0.0/8
OUT REJECT -dest 172.16.0.0/12
OUT ACCEPT -p tcp -dport 443
OUT ACCEPT -p tcp -dport 22 -dest +forges
```

with, in `cluster.fw`:

```
[IPSET forges]
# populate from https://api.github.com/meta (the "git" ranges); re-check periodically
```

Order matters: the `REJECT` rules for RFC1918 space sit *above* the broad `ACCEPT -p tcp -dport 443`, so LAN destinations are dropped before the general egress rule can allow them. The Proxmox host's own management IP is inside `192.168.1.0/24`, so it's covered by that reject.

**B. Dedicated VLAN + OPNsense (better, if you already run OPNsense).** Make `vmbr0` VLAN-aware and tag the guest's NIC; the tag is part of the guest's network config and needs no in-guest setup [[30]](https://pve.proxmox.com/wiki/Network_Configuration):

```
auto vmbr0
iface vmbr0 inet manual
        bridge-ports eno1
        bridge-stp off
        bridge-fd 0
        bridge-vlan-aware yes
        bridge-vids 2-4094
```

Then on OPNsense: add the VLAN under *Interfaces → Other Types → VLAN*, assign and enable it, give it a static gateway IP (e.g. `192.168.99.1/24`), serve DHCP+DNS, and write interface-based rules that allow the VLAN out to the internet and block it to every other local network [[33]](https://cylab.be/blog/490/tutorial-building-isolated-network-topologies-in-proxmox). This puts the policy in one place you already audit, and it survives you forgetting to re-tick the per-NIC firewall flag.

For a **fully offline** guest — plausible for a "review this untrusted repo" throwaway — a bridge with no physical port isolates it completely, and you add internet back with NAT only if you want it [[30]](https://pve.proxmox.com/wiki/Network_Configuration) [[31]](https://pve.proxmox.com/wiki/Software-Defined_Network):

```
auto vmbr99
iface vmbr99 inet static
        address 10.99.0.1/24
        bridge-ports none
        bridge-stp off
        bridge-fd 0
```

⚠ Egress allowlisting is weaker than it looks. Claude Code's own docs note that a hostname-based proxy makes its decision "from the client-supplied hostname without inspecting TLS", so code inside can potentially use domain fronting to reach hosts outside the allowlist, and that "Allowing broad domains such as `github.com` can create paths for data exfiltration" [[39]](https://code.claude.com/docs/en/sandboxing). An IP-based Proxmox firewall rule is coarser still. Segmentation buys you *LAN* protection reliably; it does not buy you exfiltration protection.

---

## 7. Where your workstation is still trusted

The VM boundary is only as good as what you hand across it.

| Channel | Risk | Fix |
|---|---|---|
| **SSH agent forwarding** (`ssh -A`, `ForwardAgent yes`) | Anyone with root on the remote host can use the forwarded socket to authenticate as you to every other system your keys reach — no private key theft required [[35]](https://www.clockwork.com/insights/ssh-agent-hijacking/) | ✗ **Never to this guest.** Use a per-repo deploy key inside the guest instead [[36]](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys). If you must reach a third host, use `ProxyJump`, which doesn't expose your agent to the intermediate box. |
| **X11 forwarding** | In trusted mode a malicious remote can "capture keystrokes and mouse events", "inspect or manipulate other application windows", "read from or write to the clipboard and selections", and take screenshots of your display [[34]](https://goteleport.com/blog/x11-forwarding/) | Don't forward at all for a TUI workflow. If you need a GUI test browser, use `ssh -X` (untrusted, restricted by the X11 SECURITY extension) and set `ForwardX11Trusted no` in `~/.ssh/config`; never `ssh -Y` [[34]](https://goteleport.com/blog/x11-forwarding/) |
| **Wayland** | No `-Y` equivalent, which is a feature here | Prefer headless testing in the guest (`playwright` in headless mode) and pull screenshots out as files. |
| **Clipboard** | Nothing in the terminal path shares a clipboard — but noVNC/SPICE consoles do, and so does a shared X server | Use SSH, not the Proxmox console, for daily work. |
| **VS Code Server / Remote-SSH** | Runs "as the same user you used to sign in to the machine", and workspace extensions get "full access to the source code, remote filesystem, and remote APIs" [[18]](https://code.visualstudio.com/docs/remote/faq) | Acceptable — that user is inside the boundary. Just don't sign in as root, and remember extensions you install become part of the guest's attack surface. |
| **`code tunnel`** | Adds a Microsoft-hosted Azure relay and ties the guest to a GitHub/Microsoft identity [[19]](https://code.visualstudio.com/docs/remote/tunnels) | Skip on a LAN. |
| **Your credentials in the guest** | Anything you put in the guest's `~/.ssh`, `~/.aws`, `~/.npmrc`, or environment is reachable by the agent | Credential isolation is a sibling angle; the hypervisor doesn't help here. Minimum bar: nothing in that guest should be reusable anywhere else. |

---

## 8. Concrete build recipe

Target: PVE 9.x (9.2, released 21 May 2026, ships Debian 13.5, kernel 7.0, QEMU 11.0, LXC 7.0, ZFS 2.4) [[38]](https://www.proxmox.com/en/about/company-details/press-releases/proxmox-virtual-environment-9-2). Adjust IDs, IPs and storage names.

**1. Build a cloud-init template once** (VM IDs 9000+ keep templates visually separate) [[37]](https://www.virtualizationhowto.com/2025/10/proxmox-cloud-init-made-easy-automating-vm-provisioning-like-the-cloud/):

```bash
# on the Proxmox host
wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img

qm create 9000 --name ubuntu-cloud --memory 2048 --cores 2 \
  --net0 virtio,bridge=vmbr0
qm importdisk 9000 noble-server-cloudimg-amd64.img local-lvm
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --ide2 local-lvm:cloudinit --boot c --bootdisk scsi0 \
  --serial0 socket --vga serial0
qm set 9000 --ciuser dev --sshkey ~/.ssh/agentvm.pub --ipconfig0 ip=dhcp \
  --agent 1 --ciupgrade 1
qm template 9000
```

**2. Clone the agent guest and size it:**

```bash
qm clone 9000 210 --name agentvm --full
qm resize 210 scsi0 +64G
qm set 210 --cores 4 --memory 8192 --balloon 0 \
  --scsihw virtio-scsi-single --scsi0 local-lvm:vm-210-disk-0,discard=on,ssd=1,iothread=1 \
  --net0 virtio,bridge=vmbr0,firewall=1
qm start 210
```

`--balloon 0` pins the RAM instead of letting the host reclaim it mid-build [[17]](https://pve.proxmox.com/pve-docs/chapter-qm.html); `virtio-scsi-single` + `iothread` is documented current best practice, and `discard=on` keeps the thin volume from growing forever [[17]](https://pve.proxmox.com/pve-docs/chapter-qm.html).

**3. Inside the guest** (as `dev`, not root):

```bash
sudo apt update && sudo apt install -y \
  qemu-guest-agent git tmux mosh build-essential ca-certificates curl
sudo systemctl enable --now qemu-guest-agent

# node via a version manager, docker via the official repo — both plain installs in a VM
curl -fsSL https://get.docker.com | sh && sudo usermod -aG docker dev

# claude code
npm install -g @anthropic-ai/claude-code
```

⚠ Adding `dev` to the `docker` group is root-equivalent inside the guest. That's acceptable *because* the guest is the boundary — it is exactly what would be unacceptable on your workstation. Anthropic's sandbox docs make the same point about `/var/run/docker.sock`: exposing it "effectively grants access to the host system" [[39]](https://code.claude.com/docs/en/sandboxing).

**4. Firewall.** Datacenter → Firewall → Options → `enable: 1`, then write `/etc/pve/firewall/210.fw` as in §6A (note `firewall=1` was already set on `net0` in step 2 — both flags are required [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html)).

**5. Baseline snapshot, before any repo exists:**

```bash
qm snapshot 210 base --description "clean toolchain, no repos, firewalled"
```

**6. Workstation side** — `~/.ssh/config`:

```
Host agentvm
  HostName 192.168.1.210
  User dev
  IdentityFile ~/.ssh/agentvm
  IdentitiesOnly yes
  ForwardAgent no
  ForwardX11 no
  ForwardX11Trusted no
```

`ForwardAgent no` and `IdentitiesOnly yes` are the two lines that keep the boundary intact [[35]](https://www.clockwork.com/insights/ssh-agent-hijacking/) [[34]](https://goteleport.com/blog/x11-forwarding/).

**7. Repo in, via a per-repo read-only deploy key** generated *in the guest* [[36]](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/deploy_myrepo -N ""
# paste ~/.ssh/deploy_myrepo.pub into repo Settings → Deploy keys (leave write access off)
git clone git@github.com:me/myrepo.git ~/src/myrepo
```

**8. Daily driving:**

```bash
ssh agentvm            # lands in tmux via the .bashrc snippet
# → cd ~/src/myrepo && claude
```

---

## 9. Friction verdict

| | Local sandbox on the workstation | Dedicated Proxmox VM |
|---|---|---|
| Setup | Minutes (`/sandbox`, or a devcontainer) | An afternoon, once |
| Boundary strength | OS primitives; Anthropic: "Sandboxing reduces risk but is not a complete isolation boundary" [[39]](https://code.claude.com/docs/en/sandboxing) | Kernel-level separation; the recommended answer for untrusted repos [[3]](https://code.claude.com/docs/en/sandbox-environments) |
| GUI dev loop | Native | Remote-SSH; good, not identical |
| Runs heavy builds | Competes with your desktop | Offloaded — 4 dedicated vCPUs churning while you work [[17]](https://pve.proxmox.com/pve-docs/chapter-qm.html) |
| Undo | git + your own discipline | `qm rollback` in seconds [[24]](https://pve.proxmox.com/pve-docs/qm.1.html) |
| LAN exposure | Whatever your workstation can reach | Whatever you allow, enforced host-side [[4]](https://pve.proxmox.com/pve-docs/chapter-pve-firewall.html) |
| Daily friction | ~zero | One `ssh`, plus "the file isn't on this machine" moments |

**Use both.** The local sandbox is the right default for reviewing your own code with prompts you wrote. The Proxmox VM earns its keep in three specific situations: an untrusted or unfamiliar repository, an unattended run with permissions skipped, and anything that installs dependencies you haven't audited. If you're already terminal-first — and Claude Code is a TUI, so you nearly are — the marginal friction of `ssh agentvm` is smaller than the friction of a devcontainer, and you get a real rollback button that a container does not give you.

The trap to avoid is the halfway house: an LXC because it's "lighter", with `nesting` and `keyctl` on so Docker works, and `~/projects` bind-mounted in so the editor feels normal. That configuration has the operational cost of a separate machine and the security properties of running the agent locally as root [[8]](https://dev.to/mattercoder/docker-on-proxmox-lxc-what-actually-works-and-why-unprivileged-doesnt-45km) [[9]](https://forum.proxmox.com/threads/root-docker-in-unprivileged-lxc-safe-or-not.93548/). A practitioner running per-language LXC dev containers with Remote-SSH reports it works well for web and console apps [[40]](https://blog.im404.me/article/isolated-development-environments-with-proxmox-lxc) — that's a *dependency-hygiene* setup, not a security one. If the reason you're building this is that an agent runs code you didn't write, spend the 200 MB and boot the VM.
