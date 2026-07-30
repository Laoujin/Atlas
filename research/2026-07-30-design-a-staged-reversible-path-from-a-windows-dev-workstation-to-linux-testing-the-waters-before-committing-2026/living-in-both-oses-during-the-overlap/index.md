---
title: "Living in both OSes: running Windows and Linux for months without your setup rotting"
date: 2026-07-30
depth: standard
format: md
topic: "Living in both OSes during the migration overlap (2026) — sharing code, credentials, dotfiles, browser state and app config between a Windows install and a Linux install without drift or a second source of truth."
topic_raw: "gradual linux migration from Windows (first testing the waters)."
tags: [linux-migration, dotfiles, dual-boot, git, secrets, devcontainers, dotnet]
summary: "One source of truth per asset class, replicated by a tool that knows the OS difference — never a shared partition and never two hand-edited copies."
citations: 37
reading_time_min: 14
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 625
issue: 14
---

> **Decision.** Every asset class gets exactly one source of truth and a *replicator* that understands the OS difference — a git remote for code, [chezmoi](https://www.chezmoi.io/) ⭐ 21k (Jul 2026) for dotfiles (the only mature manager with first-class Windows *and* templating *and* password-manager integration [[1]](https://www.chezmoi.io/comparison-table/)), a password manager for secrets, browser sync for browser state. Never a shared NTFS partition holding a git working tree [[10]](https://www.funwithlinux.net/blog/sharing-git-repo-on-ntfs-partition-between-linux-windows-dualboot/), and never a cloud-sync folder holding a `.git` directory [[16]](https://techcommunity.microsoft.com/discussions/onedriveforbusiness/onedrive-is-corrupting-my-git-repositories/3898283). If the overlap is going to be long, put the toolchain in devcontainers and the host OS mostly stops mattering [[34]](https://containers.dev/).

## The anti-pattern, stated once

Drift happens when the *same file* exists twice and both copies are editable. A shared partition looks like it solves this — one copy, two OSes — but it just moves the divergence into filesystem semantics you can't reconcile (permissions, exec bit, case, symlinks, line endings). The working rule:

**One canonical copy in a *neutral* store; each OS materialises it locally; edits go back to the canonical store, never sideways between installs.** Neutral store means a git remote, a password vault, or a sync service — not a partition mounted by both OSes.

The corollary: whenever a config genuinely *must* differ per OS (paths, fonts, terminal, keybindings), it is not two files. It is one templated file with a per-OS branch [[2]](https://www.chezmoi.io/user-guide/machines/windows/).

## Decision table

| Asset class | Source of truth | Replication | Notes |
|---|---|---|---|
| Code / repos | Git remote (GitHub, Gitea) | `git clone` **natively on each OS** into a native filesystem | Never one working tree on a shared partition [[10]](https://www.funwithlinux.net/blog/sharing-git-repo-on-ntfs-partition-between-linux-windows-dualboot/) |
| Repo-level behaviour | `.gitattributes` committed in repo | Git enforces it on both OSes | Beats per-machine `core.autocrlf` [[14]](https://blog.popekim.com/en/2025/08/28/stop-using-autocrlf.html) |
| Dotfiles | chezmoi source repo (private git) | `chezmoi apply`, templated on `.chezmoi.os` [[2]](https://www.chezmoi.io/user-guide/machines/windows/) | ⚠ Windows symlinks need dev mode |
| Machine-local git config | `~/.gitconfig` with `includeIf` [[9]](https://git-scm.com/docs/git-config) | chezmoi template writes the includes | Keeps work/personal identity split intact on both |
| Secrets / passwords | Password manager vault (1Password, Bitwarden) | CLI + agent on both OSes [[24]](https://developer.1password.com/docs/ssh/agent/) | The only truly OS-neutral secret store |
| SSH auth keys | Hardware key or vault | ⚠ **One key per install**, both enrolled [[23]](https://www.brandonchecketts.com/archives/ssh-ed25519-key-best-practices-for-2025) | Or one FIDO2 resident key you physically carry [[22]](https://developers.yubico.com/SSH/Securing_SSH_with_FIDO2.html) |
| Git host credentials | Host (GitHub/Azure DevOps) | GCM with a different backing store per OS [[18]](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/credstores.md) | Never migrate DPAPI blobs; re-auth |
| Browser state | Browser sync account | Firefox/Chrome sync, E2E-encrypted [[30]](https://www.howtogeek.com/the-best-reason-to-use-firefox-is-sync-that-actually-works/) | Passwords belong in the password manager, not the browser |
| IDE settings | VS Code Settings Sync / Rider Backup&Sync [[27]](https://code.visualstudio.com/docs/configure/settings-sync) [[28]](https://www.jetbrains.com/help/rider/Sharing_Your_IDE_Settings.html) | Vendor cloud | Machine-scoped settings deliberately don't sync [[27]](https://code.visualstudio.com/docs/configure/settings-sync) |
| Docs / media | Cloud sync (Dropbox, Syncthing) | Native client both sides | ✓ Fine — these are *files*, not repos |
| App config (Outlook, Teams) | ✗ Does not travel | Re-create per OS; Teams is web-only on Linux [[29]](https://news.itsfoss.com/microsoft-linux-app-retire/) | Accept the loss, don't fight it |
| Toolchain versions | `global.json` in repo [[33]](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json) | SDK installed per OS, version pinned by repo | Or move the whole toolchain into a devcontainer [[34]](https://containers.dev/) |

## Code and repos

**Clone natively on each OS. Sync through the remote.** This is the boring answer and it is correct.

A shared NTFS/exFAT partition is a poor home for a working tree for reasons that stack up fast. NTFS has no Unix permission model, so `git init` on an NTFS mount can fail outright with `chmod on .../.git/config.lock failed: Operation not permitted` [[11]](https://subzerodays.wordpress.com/2018/11/21/creating-git-repo-on-ntfs-in-linux/). The executable bit is not preserved, so git reports phantom modifications until you set `core.fileMode false` [[10]](https://www.funwithlinux.net/blog/sharing-git-repo-on-ntfs-partition-between-linux-windows-dualboot/) [[9]](https://git-scm.com/docs/git-config). Case-sensitivity flips between the two mounts, and a repo containing `File.txt` and `file.txt` will silently collapse one onto the other on the Windows side [[15]](https://learn.microsoft.com/en-us/azure/devops/repos/git/case-sensitivity). Symlinks need `SeCreateSymbolicLinkPrivilege` or developer mode on Windows, otherwise git stores them as plain text files [[9]](https://git-scm.com/docs/git-config). And you inherit an ownership mismatch between Windows SIDs and Linux uid/gid that you paper over with `uid=`/`gid=`/`dmask`/`fmask` mount options [[10]](https://www.funwithlinux.net/blog/sharing-git-repo-on-ntfs-partition-between-linux-windows-dualboot/).

**Driver maturity in 2026 is still not settled.** In-kernel `ntfs3` (merged in 5.15) is much faster than the FUSE-based ntfs-3g, but stability reports remain mixed — out-of-memory on large copies, hangs, and data loss, with the practical advice being to blacklist `ntfs3` and take the slower, reliable ntfs-3g [[13]](https://www.dedoimedo.com/computers/linux-ntfs-driver-reliability.html). That advice is not fringe: in January 2026 Namjae Jeon posted an "ntfs filesystem remake" series to LKML arguing `ntfs3` "still has many problems and is poorly maintained," and offering a replacement that passes 308 xfstests vs `ntfs3`'s 235 [[12]](https://lkml.iu.edu/2601.1/06496.html). Whichever way that lands, "the NTFS driver situation is being actively re-litigated in 2026" is a poor foundation for your working tree.

**If you use WSL2 as the bridge instead of a partition**, the same rule applies for the same reason: keep repos on the Linux filesystem, not under `/mnt/c`. Cross-boundary file access is 2–10× slower and git — which stats thousands of files — is the worst-affected workload [[36]](https://www.howtogeek.com/your-wsl2-projects-are-running-much-slower-because-you-put-them-on-the-windows-filesystem/) [[37]](https://github.com/microsoft/WSL/issues/4197).

**Cross-OS repo settings.** Commit a `.gitattributes` with `* text=auto` and explicit rules for binaries and shell scripts. It is the only line-ending control that lives in the repo and therefore applies identically on both installs; per-machine `core.autocrlf` cannot be enforced and is increasingly regarded as the cause rather than the cure [[14]](https://blog.popekim.com/en/2025/08/28/stop-using-autocrlf.html). Run `git add --renormalize .` once after adding it. Leave `core.fileMode` at its default `true` when the tree lives on ext4/NTFS-native — you only disable it to work around a filesystem that can't represent the bit [[9]](https://git-scm.com/docs/git-config).

**Dropbox and OneDrive: not for `.git`.** File sync and transactional VCS have incompatible atomicity assumptions; a badly timed sync cycle over git's internal files corrupts the repo, and the community verdict is that corruption is a matter of when, not if [[16]](https://techcommunity.microsoft.com/discussions/onedriveforbusiness/onedrive-is-corrupting-my-git-repositories/3898283) [[17]](https://sqlpey.com/git/git-dropbox-safe-practices/). If you want Dropbox as a *remote*, use `git-remote-dropbox`, which goes through the API rather than the desktop client's file operations [[17]](https://sqlpey.com/git/git-dropbox-safe-practices/). ⚠ Practical note for this setup: a Dropbox folder is fine for `research/`, docs and media — just not for working trees.

## Dotfiles: pick chezmoi

| Tool | ⭐ Stars | Windows | Templating per-OS | Secrets | Learning cost |
|---|---|---|---|---|---|
| [chezmoi](https://www.chezmoi.io/) | ⭐ 21k | ✓ [[1]](https://www.chezmoi.io/comparison-table/) | ✓ Go templates, `.chezmoi.os` [[2]](https://www.chezmoi.io/user-guide/machines/windows/) | ✓ Vault integration + age/gpg [[3]](https://www.chezmoi.io/user-guide/password-managers/) | Medium |
| [yadm](https://github.com/yadm-dev/yadm) | ⭐ 6.4k | ✓ [[1]](https://www.chezmoi.io/comparison-table/) | ~ `##os.Linux` alt-files only [[8]](https://biggo.com/news/202412191324_dotfile-management-tools-comparison) | ✓ encryption, ✗ vault [[1]](https://www.chezmoi.io/comparison-table/) | Low |
| [GNU Stow](https://www.gnu.org/software/stow/) | not on GitHub | ✗ needs symlinks + Perl [[4]](https://www.gnu.org/software/stow/) | ✗ | ✗ | Very low |
| Bare git repo | — | ✓ [[1]](https://www.chezmoi.io/comparison-table/) | ✗ | ✗ [[1]](https://www.chezmoi.io/comparison-table/) | Low |
| [home-manager](https://github.com/nix-community/home-manager) | ⭐ 10k | ✗ native; WSL only [[5]](https://discourse.nixos.org/t/home-manager-inside-nixos-wsl-managing-windows-configuration-files/68885) | ✓ | ✓ (sops-nix) | Very high |

**Pick chezmoi.** It is the only option in the table that clears all three bars this migration needs at once: real Windows support, per-OS templating from a *single branch*, and secrets pulled live from a password manager rather than committed [[1]](https://www.chezmoi.io/comparison-table/) [[3]](https://www.chezmoi.io/user-guide/password-managers/). The template variable `.chezmoi.os` branches Windows vs Linux, and `.chezmoi.kernel.osrelease` further distinguishes WSL by matching `microsoft` in `/proc/sys/kernel/osrelease` [[2]](https://www.chezmoi.io/user-guide/machines/windows/) — which matters if you end up with three environments (Windows, WSL, bare Linux) rather than two.

Counter-view worth knowing: on Hacker News, developers who evaluated Stow and tried chezmoi report settling on yadm for its lower ceremony [[7]](https://news.ycombinator.com/item?id=39975247); the community friction with yadm is exactly the case you'll hit — identical content that must live at *different paths* on different OSes [[8]](https://biggo.com/news/202412191324_dotfile-management-tools-comparison). That is chezmoi's home turf.

⚠ Two chezmoi-on-Windows caveats: creating symlinks requires developer mode or `SeCreateSymbolicLinkPrivilege`, and elevated setup scripts need `Start-Process -Wait` or chezmoi races ahead to the next step [[2]](https://www.chezmoi.io/user-guide/machines/windows/). Nix/home-manager is the technically strongest answer for Linux alone but has no native Windows story — it only reaches Windows through WSL, where Windows programs can't even follow the symlinks it creates [[5]](https://discourse.nixos.org/t/home-manager-inside-nixos-wsl-managing-windows-configuration-files/68885) [[6]](https://github.com/nix-community/home-manager). Wrong tool for an overlap period.

## Shell parity

PowerShell 7 runs on Linux and is the lowest-friction path if your muscle memory and scripts are PowerShell [[20]](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/unix-support?view=powershell-7.5). Keep one templated `profile.ps1` in chezmoi — the paths differ (`~/.config/powershell/profile.ps1` on Linux, `Documents\PowerShell` on Windows) but the content is one file [[20]](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/unix-support?view=powershell-7.5) [[21]](https://redmondmag.com/articles/2025/06/10/creating-a-smarter-cross-platform-powershell-profile.aspx).

What breaks on Linux, and will surface in your existing scripts [[20]](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/unix-support?view=powershell-7.5):

- No COM (`New-Object -ComObject` fails), no `Get-WinEvent`, no `Get-CimInstance`, no ActiveDirectory module
- Paths become case-sensitive — `Get-Item "Report.csv"` fails against `report.csv`
- Modules built against .NET Framework rather than .NET (Core) won't load
- Remoting over WinRM needs NTLM/Negotiate or Basic-over-HTTPS; no Kerberos

**Recommendation:** keep PowerShell as the *scripting* language on both, but don't fight to make it your Linux interactive shell — the ecosystem (completions, prompts, pipelines, man pages) is bash/zsh/fish-shaped. Put shared logic in `.ps1` files invoked from either shell, and keep the interactive aliases in a chezmoi-templated shell rc. Terminal emulator: pick a cross-platform one (WezTerm, Alacritty) so keybindings are a single config file rather than Windows Terminal JSON on one side and something else on the other.

## Credentials and secrets

**Nothing migrates.** Windows Credential Manager and DPAPI have no Linux equivalent and the blobs are machine/user-bound. The correct move is re-authentication on the Linux side, not export.

Git Credential Manager is the one component that spans both, and it does so by swapping its *backend* per OS: `wincredman` (default) or `dpapi` on Windows; `secretservice` (libsecret/GNOME Keyring, ⚠ requires a GUI session) or `gpg` (pass-compatible, requires `gpg`, `pass` and a GPG key pair) on Linux [[18]](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/credstores.md). For a headless or SSH-only Linux session the `secretservice` store won't work — `gpg`/pass is the fallback, with pinentry configured [[18]](https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/credstores.md). If you prefer git's own helper, `git-credential-libsecret` is the modern Linux choice (the old `libgnome-keyring` helper has been deprecated since 2014) [[19]](https://www.baeldung.com/linux/gnome-keyring-git-credentials-provider).

**The portable layer is a password manager, not the OS keyring.** chezmoi reads secrets from 1Password, Bitwarden (`bw`, `bws`, `rbw`) or `pass` at `apply` time, so no secret is ever committed to the dotfiles repo and both installs pull from one vault [[3]](https://www.chezmoi.io/user-guide/password-managers/). Files that must be committed can be encrypted with age or gpg instead [[3]](https://www.chezmoi.io/user-guide/password-managers/).

**SSH keys — one per install, not one shared.** Copying a private key between installs doubles its exposure and destroys your ability to say which machine leaked; per-device keys give isolation and an audit trail, and both public keys get enrolled at the host [[23]](https://www.brandonchecketts.com/archives/ssh-ed25519-key-best-practices-for-2025). Two shapes make this cheap:

- **Vault-backed agent.** The 1Password SSH agent serves keys from the vault to git/ssh without the client ever reading the private key, and runs on Windows, macOS and Linux [[24]](https://developer.1password.com/docs/ssh/agent/). ⚠ From WSL, the simplest bridge is calling Windows' `ssh.exe`; native-Linux behaviour needs npiperelay + socat.
- **Hardware key.** An `ed25519-sk` *resident* key (`ssh-keygen -O resident`, YubiKey firmware 5.2.3+ with a FIDO2 PIN) stores the credential on the token itself, so you plug in on either install and pull the handle back down — the private key never leaves the hardware [[22]](https://developers.yubico.com/SSH/Securing_SSH_with_FIDO2.html). This is the one legitimate "same key on both installs" case, because the key is physically single.

**Commit signing: use SSH, not GPG.** Git has supported `gpg.format = ssh` since 2.34, and it removes an entire GPG-agent-per-OS problem from the overlap [[25]](https://tobywf.com/2026/01/ditch-gnupg-signing-commits-with-ssh/). Set `user.signingkey` to the public key path, `commit.gpgsign true`, and `gpg.ssh.allowedSignersFile` for local verification [[25]](https://tobywf.com/2026/01/ditch-gnupg-signing-commits-with-ssh/). A FIDO2 `-sk` key can sign commits too, keeping signing and auth on the same token [[26]](https://developers.yubico.com/SSH/Securing_git_with_SSH_and_FIDO2.html).

**Per-context identity without duplication:** use `includeIf "gitdir:~/work/"` in a single `~/.gitconfig` so work vs personal signing keys and emails follow the directory, on both OSes, from one chezmoi-templated file [[9]](https://git-scm.com/docs/git-config).

## Browser and app state

Browser sync is genuinely cross-OS and end-to-end encrypted; Firefox additionally syncs *extension settings and data*, which Chrome does not [[30]](https://www.howtogeek.com/the-best-reason-to-use-firefox-is-sync-that-actually-works/). ⚠ Do not treat the browser's password store as the source of truth — Chrome and Firefox sync payloads are cryptographically incompatible, so a browser switch later strands you [[30]](https://www.howtogeek.com/the-best-reason-to-use-firefox-is-sync-that-actually-works/). The password manager is the portable layer; the browser is a client of it.

**IDE settings.** VS Code Settings Sync covers settings, keybindings, snippets, tasks, UI state, extensions and profiles; keybindings sync *per platform* by default (toggle `settingsSync.keybindingsPerPlatform` if you want them unified), and `machine`/`machine-overridable` scoped settings are deliberately excluded — which is what you want for paths and terminal profiles [[27]](https://code.visualstudio.com/docs/configure/settings-sync). Rider's Backup and Sync plugin is bundled and enabled by default, syncing themes, keymaps, code styles, live templates and the enabled-plugin list under your JetBrains Account [[28]](https://www.jetbrains.com/help/rider/Sharing_Your_IDE_Settings.html).

**What does not travel — plan for it, don't chase it.** Outlook profiles, and Teams: the classic Teams desktop client was retired on Linux in favour of a PWA [[29]](https://news.itsfoss.com/microsoft-linux-app-retire/), and there is no new-Outlook desktop client for Linux. Budget for "email and calendar happen in a browser on the Linux side" as a known cost of the overlap rather than a problem to solve.

## The .NET / TS toolchain in both places

| Concern | Windows | Linux | How to keep them aligned |
|---|---|---|---|
| SDK version | per-machine install | per-machine install | `global.json` in the repo, `rollForward: latestFeature` [[33]](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json) |
| User secrets | `%APPDATA%\Microsoft\UserSecrets\<id>\secrets.json` [[31]](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets?view=aspnetcore-10.0) | `~/.microsoft/usersecrets/<id>/secrets.json` [[31]](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets?view=aspnetcore-10.0) | ⚠ Not synced by design — re-seed from the vault |
| NuGet cache | `%userprofile%\.nuget\packages` [[32]](https://learn.microsoft.com/en-us/nuget/consume-packages/managing-the-global-packages-and-cache-folders) | `~/.nuget/packages` [[32]](https://learn.microsoft.com/en-us/nuget/consume-packages/managing-the-global-packages-and-cache-folders) | ✗ Don't share — it's a cache, let each rebuild it |

`global.json` is the single highest-leverage file here: it pins which SDK the CLI uses, requires a full version like `10.0.100`, and `rollForward` lets you accept later patches/feature bands without editing it per machine [[33]](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json). .NET 10 adds a `paths` field that can point at a repo-local SDK (`[".dotnet", "$host$"]`) plus a custom `errorMessage` — which effectively lets a repo carry its own SDK and stop caring what the host has installed [[33]](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json).

⚠ `dotnet user-secrets` is per-user, per-OS, outside the project — the ID in the `.csproj` is shared but the file is not [[31]](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets?view=aspnetcore-10.0). Treat the vault as the source and script the re-seed; don't hand-copy JSON between installs. Caches (NuGet, npm, bun) are derived state — deliberately *not* an asset class; setting `NUGET_PACKAGES` to a shared path across OSes buys nothing and risks path-encoded breakage [[32]](https://learn.microsoft.com/en-us/nuget/consume-packages/managing-the-global-packages-and-cache-folders).

## Devcontainers: the strategy that shrinks the problem

Evaluated on its merits for a *long* overlap, this is the strongest single move. `devcontainer.json` is an open specification for describing a development environment — OS, runtime, tools, extensions, services — as code, supported by a range of tools rather than one vendor [[34]](https://containers.dev/). Microsoft publishes .NET images and documents using dev containers specifically to try SDK versions without touching the host install [[35]](https://devblogs.microsoft.com/dotnet/dotnet-in-dev-container/).

What it actually buys during the migration:

- The SDK/runtime/tool set stops being per-OS state — it's in the repo, so there is nothing to keep aligned between installs [[34]](https://containers.dev/)
- Testing a new .NET version doesn't perturb either host [[35]](https://devblogs.microsoft.com/dotnet/dotnet-in-dev-container/)
- The container is Linux either way, which means your build runs on Linux semantics (case-sensitive, LF, exec bit) from day one on Windows too — you discover porting problems *before* you switch

What it doesn't buy: it does not cover dotfiles, shell, credentials, browser, or IDE settings — every other row of the decision table still applies. And on Windows it runs over WSL2, so the `/mnt/c` performance rule reappears: the repo belongs on the Linux side of the boundary [[36]](https://www.howtogeek.com/your-wsl2-projects-are-running-much-slower-because-you-put-them-on-the-windows-filesystem/).

## Anti-drift habits

- Both installs `chezmoi apply` on login. Drift shows up as a diff, not as a surprise months later [[1]](https://www.chezmoi.io/comparison-table/).
- `chezmoi diff` before any config edit, so you never edit the materialised file instead of the source [[1]](https://www.chezmoi.io/comparison-table/).
- Nothing is a source of truth unless it's in a git remote, a vault, or a sync account. If it only exists on one install, it doesn't exist.
- Every unpushed branch is drift. Push daily, even WIP.
