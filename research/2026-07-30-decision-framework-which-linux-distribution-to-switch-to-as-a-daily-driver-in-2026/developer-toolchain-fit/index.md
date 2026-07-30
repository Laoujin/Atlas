---
title: "Toolchain fit: which Linux distro costs least setup work for .NET 10 + TypeScript + Docker in 2026"
date: 2026-07-30
depth: survey
format: md
topic: "Developer toolchain fit across Linux distributions in 2026 for a .NET + TypeScript + Docker stack. Research how each candidate distro family (Ubuntu/Debian, Fedora, Arch, openSUSE, and atomic/immutable variants) handles: the .NET 10 SDK (official Microsoft packages vs distro-native packages vs the dotnet-install script; which distros Microsoft actually supports and where the RHEL/Fedora vs Debian package story differs), Node.js and bun/pnpm installation and version management (nvm/fnm/mise vs distro packages), Docker Engine vs Podman as the default container runtime (rootless, docker-compose compatibility, SELinux friction on Fedora/RHEL), JetBrains Rider and JetBrains Toolbox, Visual Studio Code (official repos, deb/rpm, Flatpak caveats for a dev tool), and terminal/shell setup. Compare the packaging ecosystems themselves — apt, dnf, pacman + AUR, zypper, Flatpak, Snap, Homebrew on Linux, Nix — on how quickly dev tooling arrives and how much breakage each invites. Also cover Docker/Compose and homelab tooling (Coolify CLI-style workflows, kubectl, terraform) availability. Deliverable: a table of friction points per distro family for this exact stack, plus which distro minimises setup work."
topic_raw: "I'm going to make the switch to Linux. The question is which Linux version should I pick? there are so many :D"
tags: [linux, dotnet, docker, developer-tooling, distros, packaging]
summary: "For a .NET 10 + TypeScript + Docker workstation in 2026, Ubuntu 26.04 LTS and Fedora 44 tie on setup effort and every other family costs you at least one hand-configured vendor repo."
citations: 39
reading_time_min: 15
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 677
issue: 11
---

> **Decision.** Two distros minimise setup work for this exact stack, for opposite reasons. **Ubuntu 26.04 LTS** — every vendor (Microsoft, Docker, JetBrains, HashiCorp, Kubernetes) tests against it first, and `.NET 10` is in the built-in feed [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision)[[38]](https://www.omgubuntu.co.uk/2025/11/ubuntu-26-04-release-schedule). **Fedora 44** — `dnf install dotnet-sdk-10.0` works out of the box, Docker Engine is officially supported, and everything is 6–18 months newer [[3]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-fedora)[[18]](https://docs.docker.com/engine/install/), at the cost of SELinux relabelling every bind mount [[21]](https://blog.ryanmartin.me/selinux-containers). **Debian 13** is the only family where Microsoft still ships .NET itself [[1]](https://learn.microsoft.com/en-us/dotnet/core/install/linux) but its Node is too old to matter. **Arch** has the freshest packages of anyone [[8]](https://archlinux.org/packages/?q=dotnet)[[20]](https://archlinux.org/packages/?q=docker) and the least vendor support. **openSUSE** and **atomic/immutable** variants both add friction that only pays off if you want what they're selling.

## The four decisions that actually matter

Coming from Windows + WSL2, most of your stack is distro-agnostic: bun, pnpm, mise, kubectl and Terraform all install from vendor scripts or vendor repos that don't care what's underneath. Four things genuinely differ per distro:

1. **Where the .NET SDK comes from** — and whether you can get a feature band other than `.1xx`.
2. **Whether the default container runtime is Docker or Podman**, and whether SELinux is between you and your bind mounts.
3. **Whether the vendors you depend on (Docker, JetBrains) list your distro as tested.**
4. **How much of your setup is a hand-written `.repo`/`.list` file** that you'll have to fix at the next release upgrade.

Everything below is organised around those.

---

## .NET 10 SDK: the packaging story is genuinely different per family

This is the part that surprises Windows developers. There is no single "Microsoft .NET repo for Linux" any more. Since .NET 9, Microsoft only publishes to `packages.microsoft.com` for distros that *don't* package .NET themselves — Azure Linux, Debian, openSUSE Leap and SLES. Alpine, CentOS Stream, Fedora, RHEL and Ubuntu ship their own builds [[1]](https://learn.microsoft.com/en-us/dotnet/core/install/linux), governed by a published selection policy [[37]](https://github.com/dotnet/core/discussions/9556) ⭐ 22k. Arch is on the "publishes its own" list too [[6]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-package-mixup).

| Distro family | Install command | Who builds it | .NET 10 today | ⚠ Friction |
|---|---|---|---|---|
| **Ubuntu 26.04 LTS** | `apt install dotnet-sdk-10.0` | Canonical, built-in feed | ✓ in built-in feed [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision) | .NET 9/8 need `ppa:dotnet/backports`; SDK is **always `.1xx` band** [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision) |
| **Ubuntu 24.04 LTS** | `apt install dotnet-sdk-10.0` | Canonical | ✓ built-in feed [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision) | .NET 9 only via backports PPA; Microsoft feed **doesn't exist** for 24.04+ [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision) |
| **Debian 13** | add `packages-microsoft-prod.deb`, then `apt install dotnet-sdk-10.0` | Microsoft [[4]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian) | ✓ all supported versions | One extra repo to register; the only family where you get **non-`.1xx` feature bands** from a package manager |
| **Fedora 43/44** | `dnf install dotnet-sdk-10.0` | Fedora/Red Hat | ✓ `10.0.110` on both [[7]](https://packages.fedoraproject.org/pkgs/dotnet10.0/dotnet-sdk-10.0/) | Microsoft explicitly warns packages can lag a .NET release [[3]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-fedora); RPM users hit `No match for argument: dotnet-sdk-10.0` for weeks after launch [[9]](https://github.com/dotnet/sdk/issues/52253) ⭐ 3.2k |
| **openSUSE Leap 16** | add MS zypper repo, `zypper install dotnet-sdk-10.0` | Microsoft [[5]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-opensuse) | ✓ | **Leap 16 only** — Tumbleweed is not a supported .NET target [[5]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-opensuse); packages depend on OpenSSL 3.x |
| **Arch** | `pacman -S dotnet-sdk` | Arch, source-built | ✓ `10.0.10.sdk110`, plus SDK 8/9/10 side by side [[8]](https://archlinux.org/packages/?q=dotnet) | Not a Microsoft-supported distro at all [[1]](https://learn.microsoft.com/en-us/dotnet/core/install/linux); `-bin` AUR packages needed for other bands |
| **Any distro** | `dotnet-install.sh` / tarball | Microsoft binaries | ✓ any version incl. previews | You install dependencies, export `DOTNET_ROOT` + `PATH`, and patch by hand; Microsoft says "for a developer or user, it's better to use a package manager" [[10]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-scripted-manual) |
| **Any distro** | `snap install dotnet-sdk` | Canonical [[11]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-snap-sdk) | ✓ | Snap confinement; fine for CLI, awkward alongside a distro install |

### The feature-band trap

Distro-built SDKs are all in the `.1xx` feature band: Ubuntu by Canonical policy [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision), Fedora at `10.0.110` [[7]](https://packages.fedoraproject.org/pkgs/dotnet10.0/dotnet-sdk-10.0/), Arch at `10.0.10.sdk110` [[8]](https://archlinux.org/packages/?q=dotnet). If a repo's `global.json` pins `10.0.2xx` or `10.0.3xx`, only Debian's Microsoft feed [[4]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian) or `dotnet-install.sh` [[10]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-scripted-manual) can satisfy it. Preview SDKs are never in any package repo [[3]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-fedora).

### The one .NET failure mode to know about

Register *two* .NET feeds and `dotnet build` starts throwing `libhostfxr.so could not be found` or `FrameworkList.xml` not found, with the tell-tale symptom of both `/usr/lib64/dotnet` and `/usr/share/dotnet` existing [[6]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-package-mixup). This bites specifically when you add `packages.microsoft.com` for **PowerShell** — which you probably will [[35]](https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu?view=powershell-7.6) — on a distro that already ships .NET. The fix is a pin: an apt `Pin-Priority: -10` fragment, or `excludepkgs=dotnet*,aspnet*,netstandard*` in the dnf repo file [[6]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-package-mixup). Set it up on day one, not after the first mystery build failure.

---

## Node, bun, pnpm: ignore the distro entirely

Distro Node is always behind and pinned for the release lifetime. Ubuntu 26.04 ships Node 22.22.1, 24.04 ships 18.19.1, 22.04 ships 12.22.9 [[12]](https://packages.ubuntu.com/search?keywords=nodejs&searchon=names&suite=all&section=all); Fedora 44 ships `nodejs22` at 22.22.2 [[13]](https://packages.fedoraproject.org/pkgs/nodejs22/nodejs22/). Neither gets you the current LTS line, and neither lets you switch per project.

This makes the JS side of your stack **completely distro-neutral**, which is good news:

| Tool | Install path that works everywhere | Notes |
|---|---|---|
| [mise](https://mise.jdx.dev) ⭐ 31k (Jul 2026) | `curl https://mise.run \| sh` → `~/.local/bin` [[15]](https://mise.jdx.dev/getting-started.html) | One tool for node, bun, terraform, kubectl via pluggable backends [[15]](https://mise.jdx.dev/getting-started.html); also in apt/yum/brew/nix/snap |
| [fnm](https://github.com/Schniz/fnm) ⭐ 26k (Jul 2026) | single Rust binary | Node only; fastest shell-hook of the three |
| [nvm](https://github.com/nvm-sh/nvm) ⭐ 94k (Jul 2026) | shell script | Node only; measurable shell-startup cost |
| [bun](https://bun.com) ⭐ 95k (Jul 2026) | `curl -fsSL https://bun.com/install \| bash` [[16]](https://bun.com/docs/installation) | Needs `unzip` and glibc ≥ 2.17; ⚠ default x64 build **requires AVX2** — pre-Haswell CPUs silently get the slower baseline build [[16]](https://bun.com/docs/installation) |
| [pnpm](https://pnpm.io) ⭐ 36k (Jul 2026) | standalone script (no Node needed) or Corepack [[17]](https://pnpm.io/installation) | Corepack/npm paths require Node ≥ 22 [[17]](https://pnpm.io/installation) |
| [NodeSource](https://github.com/nodesource/distributions) ⭐ 14k (Jul 2026) | third-party apt/dnf repo [[14]](https://github.com/nodesource/distributions) | Only worth it if you want *one* system-wide Node managed by the package manager |

Recommendation for this stack: **mise** covers node + bun + pnpm shims + kubectl + terraform in one `.tool-versions`-style config, which collapses four of the "homelab tooling" rows below into nothing.

---

## Containers: this is where distro choice actually costs you

| | Ubuntu / Debian | Fedora | openSUSE Leap | Arch | Atomic (Silverblue/Bluefin) |
|---|---|---|---|---|---|
| Docker Engine officially supported | ✓ [[18]](https://docs.docker.com/engine/install/) | ✓ [[18]](https://docs.docker.com/engine/install/) | ✗ not listed [[18]](https://docs.docker.com/engine/install/) | ✗ not listed [[18]](https://docs.docker.com/engine/install/) | ✗ (layer it yourself [[22]](https://discussion.fedoraproject.org/t/installing-docker-on-silverblue/119610)) |
| Docker Desktop officially supported | ✓ Ubuntu, Debian [[19]](https://docs.docker.com/desktop/setup/install/linux/) | ✓ [[19]](https://docs.docker.com/desktop/setup/install/linux/) | ✗ | ⚠ experimental, untested package [[19]](https://docs.docker.com/desktop/setup/install/linux/) | ✗ |
| Distro-packaged Docker | via Docker's own apt repo | via Docker's own dnf repo | `zypper` (community) | `pacman -S docker` 29.6.2 + `docker-compose` 5.3.1 [[20]](https://archlinux.org/packages/?q=docker) | Bluefin DX preinstalls docker-ce + compose + buildx [[23]](https://docs.projectbluefin.io/bluefin-dx/) |
| Default runtime shipped | Docker (after you add the repo) | **Podman** preinstalled | Podman | neither | **Podman** preinstalled |
| ⚠ SELinux bind-mount friction | none (AppArmor) | ✓ real — `:z`/`:Z` or `chcon -Rt container_file_t` needed [[21]](https://blog.ryanmartin.me/selinux-containers) | ✓ | none | ✓ |

**The Fedora/RHEL SELinux tax is the single biggest practical difference for a Docker Compose user.** Your existing `docker-compose.yml` files from the homelab will hit `permission denied` on bind mounts until every host-path volume gains a `:z` (shared) or `:Z` (private) suffix [[21]](https://blog.ryanmartin.me/selinux-containers). That's an edit to files you share with a Coolify-managed server that doesn't need them. Do not "fix" it by relabelling system directories — `:Z` on `/etc`, `/usr` or `/var/lib` breaks the host [[21]](https://blog.ryanmartin.me/selinux-containers).

Docker Desktop on Linux is mostly not worth it for this profile: it runs a KVM VM, needs GNOME/KDE/MATE, and conflicts with Docker Engine over port mapping [[19]](https://docs.docker.com/desktop/setup/install/linux/). On Linux you want Docker Engine + `docker compose` [[18]](https://docs.docker.com/engine/install/) — the same CLI your Coolify hosts run.

Podman is the better *security* default and is preinstalled on Fedora and the atomic desktops, but Compose is still Docker's home turf: you either use `podman-compose` ([containers/podman-compose](https://github.com/containers/podman-compose) ⭐ 6.2k (Jul 2026)) or point the real `docker compose` ([docker/compose](https://github.com/docker/compose) ⭐ 38k (Jul 2026)) at the Podman socket. Given your homelab already standardises on Docker Compose, **install Docker Engine and don't fight the distro default** — that's cheap on Ubuntu/Debian/Fedora [[18]](https://docs.docker.com/engine/install/) and a manual `.repo` drop plus reboot on atomic [[22]](https://discussion.fedoraproject.org/t/installing-docker-on-silverblue/119610).

---

## IDEs: Rider and VS Code

| | Rider | VS Code |
|---|---|---|
| Recommended path | [JetBrains Toolbox](https://www.jetbrains.com/toolbox-app/) tarball, unpacked to a directory you choose [[25]](https://www.jetbrains.com/help/toolbox-app/installation.html) | Official deb or rpm repo [[26]](https://code.visualstudio.com/docs/setup/linux) |
| Distros JetBrains/MS test | Ubuntu 24.04 & 26.04 LTS, Fedora 43/44, Debian 13, Amazon Linux 2023; glibc ≥ 2.28 [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) | Debian/Ubuntu (deb), RHEL/Fedora/CentOS + openSUSE/SLE (same rpm repo) [[26]](https://code.visualstudio.com/docs/setup/linux) |
| Snap | available, ⚠ JetBrains flags "performance degradation" and points you back to Toolbox [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) | official snap, auto-updates [[26]](https://code.visualstudio.com/docs/setup/linux) |
| Flatpak | exists, not the documented path [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) | ✗ **not an official channel** [[26]](https://code.visualstudio.com/docs/setup/linux) |
| Arch / Nix | AUR + Toolbox tarball | community AUR and nixpkgs builds [[26]](https://code.visualstudio.com/docs/setup/linux) |

**Do not use the VS Code Flatpak.** The sandbox can't see host toolchains, offers no easy way to install one inside it, and has no access to `/var/run/docker.sock` by default [[28]](https://bentsukun.ch/posts/vscode-flatpak/) — which kills Dev Containers, the .NET language server and every `dotnet`/`node` invocation from the integrated terminal. Developer consensus on Lobsters is blunt: it "really shouldn't be the version suggested to users" [[27]](https://lobste.rs/s/acalt2/vs_code_flatpak_is_useless). Use the deb/rpm on a conventional distro, or a Distrobox/Toolbx container on an atomic one.

Rider's supported-distro list [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) is a useful tiebreaker on its own: Ubuntu LTS, Fedora, Debian 13. openSUSE and Arch aren't on it (the tarball still runs; you're just off-menu).

---

## Packaging ecosystems: how fast, how fragile

| Ecosystem | Dev-tool freshness | Breakage risk | Best used for |
|---|---|---|---|
| **apt** (Ubuntu/Debian) | slow for language runtimes (Node 22 on 26.04 [[12]](https://packages.ubuntu.com/search?keywords=nodejs&searchon=names&suite=all&section=all)), fast for .NET on Ubuntu [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision) | low; ⚠ vendor `.list` files break on release upgrade [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision) | the OS + vendor repos everyone tests against |
| **dnf** (Fedora) | good — .NET 10 at `10.0.110` [[7]](https://packages.fedoraproject.org/pkgs/dotnet10.0/dotnet-sdk-10.0/), 6-month cadence | low-medium; ⚠ .NET packages can lag a release by weeks [[9]](https://github.com/dotnet/sdk/issues/52253) ⭐ 3.2k | current toolchains without rolling-release churn |
| **pacman + AUR** | fastest of all — Docker 29.6.2 within days [[20]](https://archlinux.org/packages/?q=docker), Ghostty in `[extra]` [[29]](https://ghostty.org/docs/install/binary) | highest; AUR `-bin` packages are third-party rebuilds of vendor binaries | people who want today's version and will read changelogs |
| **zypper** (openSUSE) | Leap is conservative; Tumbleweed is rolling but unsupported by Microsoft [[5]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-opensuse) | low on Leap | not this stack — worst vendor coverage of the five |
| **Snap** | good; official channels for VS Code [[26]](https://code.visualstudio.com/docs/setup/linux), .NET SDK [[11]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-snap-sdk), kubectl [[30]](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/) | medium; ⚠ JetBrains reports performance problems [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) | GUI apps, not toolchains |
| **Flatpak** | good for GUI apps | ⚠ actively harmful for dev tools — sandbox hides host toolchains and the Docker socket [[28]](https://bentsukun.ch/posts/vscode-flatpak/) | Slack, Spotify, browsers. Not IDEs |
| **Homebrew on Linux** ([Homebrew/brew](https://github.com/Homebrew/brew) ⭐ 49k (Jul 2026)) | very fresh for CLI tools | low; needs a system C compiler and recent glibc/gcc, single-user by design [[36]](https://docs.brew.sh/Homebrew-on-Linux) | CLI tools missing or stale in the distro, no sudo needed after install [[36]](https://docs.brew.sh/Homebrew-on-Linux) |
| **Nix / nixpkgs** ([NixOS/nixpkgs](https://github.com/NixOS/nixpkgs) ⭐ 26k (Jul 2026)) | very fresh, reproducible per-project shells [[39]](https://github.com/NixOS/nixpkgs) | low for tools, medium conceptual cost; listed by Microsoft as a third-party .NET source [[1]](https://learn.microsoft.com/en-us/dotnet/core/install/linux) | per-project pinned environments — a big learning investment while Linux itself is new to you |

Rule of thumb for this stack: **distro package manager for the OS, vendor repos for .NET/Docker/PowerShell, mise for language runtimes, Homebrew only for the odd missing CLI.** That layering is identical on Ubuntu and Fedora, which is why they tie.

---

## Homelab and infra tooling

All of this is distro-neutral or vendor-repo-driven — it does **not** discriminate between Ubuntu, Debian and Fedora, and only mildly penalises Arch/openSUSE.

| Tool | Availability |
|---|---|
| **Docker Compose** | plugin from Docker's own repo on Ubuntu/Debian/Fedora [[18]](https://docs.docker.com/engine/install/); `pacman -S docker-compose` on Arch [[20]](https://archlinux.org/packages/?q=docker) |
| **kubectl** | `pkgs.k8s.io` apt/dnf/zypper repos, pinned **per minor version** — you edit the repo URL to upgrade [[30]](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/); also curl binary, snap, brew |
| **Terraform** | HashiCorp's own apt and dnf repos [[31]](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli), which cover Ubuntu, Debian, Fedora, RHEL/CentOS and Amazon Linux only [[32]](https://www.hashicorp.com/en/blog/announcing-the-hashicorp-linux-repository) — ✗ no openSUSE, ✗ no Arch |
| **OpenTofu** ([opentofu/opentofu](https://github.com/opentofu/opentofu) ⭐ 30k (Jul 2026)) | drop-in alternative if you'd rather avoid HashiCorp's licence terms |
| **Coolify** ([coollabsio/coolify](https://github.com/coollabsio/coolify) ⭐ 60k (Jul 2026)) | server-side only; installer supports Debian- and RHEL-based hosts [[33]](https://coolify.io/docs/get-started/installation). Your workstation needs nothing but `ssh` + `docker` CLI. For IaC, a community Terraform provider covers apps, databases, servers and env vars (API disabled by default — enable it and mint a token) [[34]](https://registry.terraform.io/providers/coolify-terraform/coolify/latest/docs) |
| **PowerShell 7** | Microsoft apt/dnf/zypper repos are the preferred path [[35]](https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu?view=powershell-7.6) — ⚠ this is the repo that triggers the .NET package mix-up [[6]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-package-mixup) |

---

## Atomic / immutable variants

The pitch: the OS is an image, your tooling lives in containers or `$HOME`, and a bad update is one reboot away from being undone. The cost for this stack is concrete.

- **`rpm-ostree` layering works but is not apt.** Adding Docker CE on Silverblue means manually placing the `.repo` file in `/etc/yum.repos.d/` then `rpm-ostree install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin` — and a reboot [[22]](https://discussion.fedoraproject.org/t/installing-docker-on-silverblue/119610). Fedora community members' first answer is "use the preinstalled Podman instead" [[22]](https://discussion.fedoraproject.org/t/installing-docker-on-silverblue/119610).
- **[Bluefin](https://projectbluefin.io) ⭐ 2.6k (Jul 2026) removes most of that.** Its DX image preinstalls `docker-ce` with the Compose and Buildx plugins, Podman tooling, and VS Code with Dev Containers already wired to Docker [[23]](https://docs.projectbluefin.io/bluefin-dx/). If you want atomic, this is the version to try — it is the only atomic option where this stack is close to zero-config.
- **[Distrobox](https://github.com/89luca89/distrobox) ⭐ 13k (Jul 2026) / [Toolbx](https://github.com/containers/toolbox) ⭐ 3.4k (Jul 2026)** become mandatory, not optional: your .NET SDK, Node and CLI tools live inside a mutable container that the IDE reaches into. That's a genuinely new mental model on top of Linux itself.
- ⚠ **You inherit both the SELinux tax and the sandbox tax at once.** Podman default + SELinux enforcing [[21]](https://blog.ryanmartin.me/selinux-containers) + Flatpak-first app delivery [[28]](https://bentsukun.ch/posts/vscode-flatpak/) is three unfamiliar layers stacked while bash is still new to you.

Verdict: excellent destination, wrong starting point. Revisit in a year.

---

## Terminal and shell

Least distro-dependent part of the whole exercise, and the one where your PowerShell background matters most.

- Default shell is bash everywhere; zsh and fish are one package install on every family.
- [starship](https://github.com/starship/starship) ⭐ 59k (Jul 2026) gives a consistent prompt across bash/zsh/fish and installs from a script or every distro repo.
- [Ghostty](https://ghostty.org) ⭐ 59k (Jul 2026) is the notable distro-discriminating terminal: first-party packages for Arch `[extra]`, Alpine, Gentoo, Nix, Solus, Void and snap; Fedora needs a COPR and Ubuntu a community `.deb`; ⚠ openSUSE dropped it over Zig versioning [[29]](https://ghostty.org/docs/install/binary).
- Install PowerShell 7 from Microsoft's repo [[35]](https://learn.microsoft.com/en-us/powershell/scripting/install/install-ubuntu?view=powershell-7.6) — but pin `dotnet*` away from that repo first [[6]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-package-mixup).

---

## Master friction table

Count of things you must configure by hand for `.NET 10 + TS + Docker Compose + Rider/VS Code`:

| | Ubuntu 26.04 LTS | Debian 13 | Fedora 44 | Arch | openSUSE Leap 16 | Bluefin DX |
|---|---|---|---|---|---|---|
| .NET 10 SDK | ✓ built-in feed [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision) | +1 MS repo [[4]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian) | ✓ `dnf` [[3]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-fedora) | ✓ `pacman` [[8]](https://archlinux.org/packages/?q=dotnet) | +1 MS repo [[5]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-opensuse) | inside a container |
| Non-`.1xx` SDK band possible | ✗ [[2]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu-decision) | ✓ [[4]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian) | ✗ [[7]](https://packages.fedoraproject.org/pkgs/dotnet10.0/dotnet-sdk-10.0/) | ✗ (AUR `-bin`) [[8]](https://archlinux.org/packages/?q=dotnet) | ✓ [[5]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-opensuse) | ✓ (script in container) |
| Docker Engine | +1 vendor repo, ✓ supported [[18]](https://docs.docker.com/engine/install/) | +1 vendor repo, ✓ supported [[18]](https://docs.docker.com/engine/install/) | +1 vendor repo, ✓ supported [[18]](https://docs.docker.com/engine/install/) | ✓ `pacman`, ✗ unsupported [[20]](https://archlinux.org/packages/?q=docker) | ✗ unsupported [[18]](https://docs.docker.com/engine/install/) | ✓ preinstalled [[23]](https://docs.projectbluefin.io/bluefin-dx/) |
| Compose bind mounts work unmodified | ✓ | ✓ | ✗ needs `:z`/`:Z` [[21]](https://blog.ryanmartin.me/selinux-containers) | ✓ | ✗ | ✗ |
| Rider tested by JetBrains | ✓ [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) | ✓ [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) | ✓ [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) | ✗ | ✗ | ✓ (Fedora base) |
| VS Code official repo | ✓ deb [[26]](https://code.visualstudio.com/docs/setup/linux) | ✓ deb [[26]](https://code.visualstudio.com/docs/setup/linux) | ✓ rpm [[26]](https://code.visualstudio.com/docs/setup/linux) | ✗ AUR [[26]](https://code.visualstudio.com/docs/setup/linux) | ✓ same rpm repo [[26]](https://code.visualstudio.com/docs/setup/linux) | ✓ preinstalled [[23]](https://docs.projectbluefin.io/bluefin-dx/) |
| Terraform vendor repo | ✓ [[32]](https://www.hashicorp.com/en/blog/announcing-the-hashicorp-linux-repository) | ✓ [[32]](https://www.hashicorp.com/en/blog/announcing-the-hashicorp-linux-repository) | ✓ [[32]](https://www.hashicorp.com/en/blog/announcing-the-hashicorp-linux-repository) | ✗ AUR/mise | ✗ [[32]](https://www.hashicorp.com/en/blog/announcing-the-hashicorp-linux-repository) | ✓ |
| Node/bun/pnpm | mise, identical everywhere [[15]](https://mise.jdx.dev/getting-started.html) | — | — | — | — | — |
| ⚠ .NET mix-up risk when adding MS repo for PowerShell | high [[6]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-package-mixup) | none (same feed) | high [[6]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-package-mixup) | high [[6]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-package-mixup) | none (same feed) | contained |
| **Hand-configured repos needed** | **3** (Docker, VS Code, HashiCorp) | **4** (+MS .NET) | **3** | **0 repos, 0 vendor support** | **4, worst coverage** | **0–1** |

### How to read that

- **Ubuntu 26.04 LTS** — fewest surprises, most documentation written for it, .NET 10 with no repo at all. Pay for it with old Node in-repo (irrelevant, use mise) and a `.1xx`-only SDK.
- **Fedora 44** — same repo count, newer everything, `dnf install dotnet-sdk-10.0` on day one. Pay for it with SELinux volume flags on every Compose file and occasional .NET package lag [[9]](https://github.com/dotnet/sdk/issues/52253) ⭐ 3.2k.
- **Debian 13** — pick it if a project pins a non-`.1xx` SDK band, or if you want a Microsoft-supported .NET feed and PowerShell from the same repo with zero mix-up risk [[4]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian).
- **Arch** — freshest Docker and .NET of anyone, zero vendor support: not on Microsoft's [[1]](https://learn.microsoft.com/en-us/dotnet/core/install/linux), Docker's [[18]](https://docs.docker.com/engine/install/), JetBrains' [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) or HashiCorp's [[32]](https://www.hashicorp.com/en/blog/announcing-the-hashicorp-linux-repository) lists. When something breaks, you are the support.
- **openSUSE Leap 16** — Microsoft supports it [[5]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-opensuse) but Docker [[18]](https://docs.docker.com/engine/install/), JetBrains [[24]](https://www.jetbrains.com/help/rider/Installation_guide.html) and HashiCorp [[32]](https://www.hashicorp.com/en/blog/announcing-the-hashicorp-linux-repository) don't. Skip for this stack.
- **Bluefin DX** — the only atomic option that's nearly turnkey here [[23]](https://docs.projectbluefin.io/bluefin-dx/), but it asks you to learn Distrobox, Podman, SELinux and Flatpak simultaneously.
