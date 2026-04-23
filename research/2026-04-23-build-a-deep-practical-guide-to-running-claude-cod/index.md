---
title: "Claude Code YOLO in Docker: a 2026 reference build"
date: 2026-04-23
depth: deep
format: md
topic: "Build a deep, practical guide to running Claude Code in YOLO mode (--dangerously-skip-permissions) inside a Docker sandbox in 2026, covering container image design, skills layer, persisted auth, sandbox hardening, and comparison of community approaches, with a reference Dockerfile, compose snippet, and threat-model table."
topic_raw: "I want to run Claude Code in Yolo mode. Probably with Docker Sandbox. We need to have everything Claude typically needs installed there (python, nvm, dotnet, playwright, gh) also things to work with images, videos\n\nMaybe need some skills (ex: superpowers, how to work with Excel, Word, Powerpoint)\n\nNeed to be logged into stuff: github, claude\nAnd needs to be secure, ideally not possible for Claude to extract my secrets with"
issue: 7
tags: [claude-code, yolo, docker, sandbox, security, devcontainer, skills, hardening]
summary: Reference Dockerfile, compose snippet, hardening recipe, and threat-model table for running `claude --dangerously-skip-permissions` inside a locked-down container in 2026.
citations: 77
reading_time_min: 24
cover: cover.svg
cost_usd: 10.70
duration_sec: 1110
---

> **Decision.** YOLO (`--dangerously-skip-permissions`) inside a properly isolated Docker sandbox is safer in 2026 than native Claude Code with permission prompts — *if* the sandbox has both filesystem **and** network isolation. Anthropic itself admits users approve 93% of prompts [[58]](https://www.anthropic.com/engineering/claude-code-auto-mode), and UpGuard found only 1.1% of public configs use deny/ask rules [[61]](https://www.upguard.com/blog/yolo-mode-hidden-risks-in-claude-code-permissions) — the prompt layer is theatre. Use **Docker Sandboxes** (GA Jan 2026) [[51]](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/) or **claudebox** [[52]](https://github.com/RchGrav/claudebox) if you want something turn-key; roll your own off the reference Dockerfile below if you need a specific toolbelt (Playwright + .NET + LibreOffice) or want the egress firewall pinned to your allowlist. Never mount the host Docker socket [[39]](https://opscart.com/docker-runtime-escape-why-mounting-docker-sock-is-worse-than-running-privileged-containers/), never pass `ANTHROPIC_API_KEY` as an env var [[30]](https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot/).

## The contested bit first: is YOLO-plus-sandbox actually safer?

This is the question the 2026 community has spent a year arguing about, so lead with it.

**Pro-YOLO-plus-sandbox (Willison, Anthropic engineering):** Simon Willison's "lethal trifecta" framing — private data + untrusted content + external communication [[36]](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) — says the sandbox's job is to break at least one leg of that triangle, and the only one you can reliably cut is **external comms** (deny-by-default egress). Willison's core line: *"Anyone who gets text into your LLM has full control over what tools it runs next"* [[57]](https://simonw.substack.com/p/the-lethal-trifecta-for-ai-agents) — prompts can't change that, only sandboxes can. Willison's October 2025 follow-up: *"the best sandboxes run on someone else's computer"*, and network restriction kills data exfiltration [[56]](https://simonwillison.net/2025/Oct/22/living-dangerously-with-claude/). Anthropic's engineering post agrees: effective sandboxing requires **both** filesystem and network isolation — network-only still leaks SSH keys, filesystem-only still enables escape-then-exfil [[35]](https://www.anthropic.com/engineering/claude-code-sandboxing). Anthropic's own devcontainer docs explicitly sanction `--dangerously-skip-permissions` *inside the devcontainer* because "the container's enhanced security measures (isolation and firewall rules)" carry the safety [[15]](https://code.claude.com/docs/en/devcontainer).

**Anti-YOLO (Trail of Bits, Check Point, Invariant Labs):** The incident ledger got loud in 2025–2026. Trail of Bits demonstrated prompt-injection-to-RCE against three agents including Claude Code, bypassing human approval gates [[66]](https://blog.trailofbits.com/2025/10/22/prompt-injection-to-rce-in-ai-agents/). Invariant Labs showed a GitHub-MCP agent with broad PAT access could be hijacked by a single malicious public issue and leak private repos [[63]](https://invariantlabs.ai/blog/mcp-github-vulnerability). Check Point's **CVE-2025-59536** proved a hostile `.claude/settings.json` in a cloned repo can redirect `ANTHROPIC_BASE_URL` and exfiltrate the Authorization header **before** the trust dialog renders [[31]](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/). Cyata chained three CVEs in Anthropic's own Git MCP to RCE [[64]](https://www.theregister.com/2026/01/20/anthropic_prompt_injection_flaws/), and April 2026 research called MCP's STDIO handling architecturally broken across 200k+ servers — with Anthropic declining to change it [[65]](https://www.theregister.com/2026/04/16/anthropic_mcp_design_flaw/).

**Anthropic's own docs contradict themselves:** Best Practices says YOLO requires "a sandbox without internet access", but the Devcontainer docs say firewall rules are sufficient; the GitHub issue flagging this was closed *not planned* [[60]](https://github.com/anthropics/claude-code/issues/19978). The security page still tells users to run in VMs [[59]](https://code.claude.com/docs/en/security).

**2026 synthesis** (hartphoenix, community security research): *"The sandbox is the only layer that catches novel attacks — because it doesn't need to recognize the command, it prevents the outcome. Deny rules are a friction layer, not a security boundary."* [[67]](https://gist.github.com/hartphoenix/698eb8ef8b08ad2ce6a99cf7346cd7cc). Prompts filter *known* bad commands; sandboxes bound *outcomes*. The pragmatic consensus in April 2026: run YOLO, inside a sandbox with filesystem + egress isolation, never mount the host Docker socket, never hand the container long-lived credentials.

## Threat model by hardening level

What a malicious prompt (or compromised MCP server, or poisoned `.claude/settings.json` in a cloned repo) can still do at each rung of the ladder. Rows are attacker capabilities; columns are defensive posture.

| Attacker capability | Native, prompts only | Docker + default opts | Docker + non-root, `--read-only`, cap-drop, seccomp | Docker + egress firewall allowlist | Docker + all above + Firecracker / gVisor |
|---|---|---|---|---|---|
| Destructive `rm -rf ~/` via tilde expansion [[62]](https://github.com/anthropics/claude-code/issues/10077) | ✗ hits host | ✓ contained to container | ✓ contained | ✓ contained | ✓ contained |
| Exfiltrate `ANTHROPIC_API_KEY`/`GITHUB_TOKEN` via `ps auxeww` in PR comment [[30]](https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot/) | ✗ exposed | ✗ exposed if env-passed | ✗ exposed if env-passed | ✗ if attacker endpoint is allowlisted, else ✓ blocked | ✓ if endpoint blocked |
| Redirect `ANTHROPIC_BASE_URL` via hostile `.claude/settings.json` (CVE-2025-59536) [[31]](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/) | ✗ leaks to attacker URL | ✗ leaks | ✗ leaks | ✓ blocked (attacker URL not allowlisted) | ✓ blocked |
| Steal cloud IAM creds from `169.254.169.254` [[41]](https://www.wiz.io/blog/imds-anomaly-hunting-zero-day) | ✗ reachable | ✗ reachable | ✗ reachable (default) | ✓ blocked by allowlist | ✓ blocked |
| Escape via `/var/run/docker.sock` to launch privileged sibling [[39]](https://opscart.com/docker-runtime-escape-why-mounting-docker-sock-is-worse-than-running-privileged-containers/) | n/a | ✗ if mounted — total host takeover | ✗ if mounted | ✗ if mounted | ✗ if mounted (don't mount it, ever) |
| Prompt-inject-to-RCE via MCP chain [[66]](https://blog.trailofbits.com/2025/10/22/prompt-injection-to-rce-in-ai-agents/) | ✗ runs on host | ✓ runs in container only | ✓ contained, no privilege escalation | ✓ contained, can't exfil | ✓ contained, microVM-enforced |
| Kernel CVE container escape [[40]](https://blaxel.ai/blog/container-escape) | n/a | ✗ possible | ✗ seccomp/cap-drop narrows surface | ✗ narrows surface | ✓ VM boundary holds |
| Exfiltrate SSH keys from `~/.ssh` [[35]](https://www.anthropic.com/engineering/claude-code-sandboxing) | ✗ readable | ✗ if $HOME bind-mounted | ✓ if not mounted | ✓ if not mounted | ✓ |
| Rewrite own allowlist via hostile skill/hook | ✗ | ✗ if settings.json writable | ✓ if settings.json root-owned [[38]](https://github.com/FoamoftheSea/claude-code-sandbox) | ✓ | ✓ |
| Fork-bomb / resource exhaustion | ✗ DoS host | ✗ DoS host | ✓ if `--pids-limit`, `--memory` set | ✓ | ✓ |

Legend: ✗ = attacker wins; ✓ = defense holds.

## Reference Dockerfile

Synthesis of Anthropic's minimal devcontainer [[1]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/Dockerfile) and HolyClaude's batteries-included image [[2]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/Dockerfile). Base is `node:22-bookworm-slim` — `bookworm` because Playwright officially supports Debian 12 on x86_64 and arm64 for all three browsers [[5]](https://github.com/microsoft/playwright/issues/24028), and Alpine is ruled out because Firefox/WebKit are glibc-only [[3]](https://playwright.dev/docs/docker). Expect roughly 4 GB final image with Chromium + LibreOffice + .NET in one layer [[12]](https://dev.to/coderluii/how-i-run-claude-code-in-docker-with-a-web-ui-and-headless-browser-5dko).

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:22-bookworm-slim

ARG CLAUDE_CODE_VERSION=latest
ARG DOTNET_CHANNEL=9.0
ARG UV_VERSION=0.11.7

# 1. Base system + doc conversion + media + dev tooling (Anthropic line + HolyClaude additions)
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl wget gnupg2 git gh jq ripgrep fd-find fzf zsh tmux \
      procps sudo less man-db unzip vim nano \
      iptables ipset iproute2 dnsutils aggregate \
      python3 python3-pip python3-venv \
      ffmpeg imagemagick libvips-dev \
      poppler-utils tesseract-ocr pandoc \
      libreoffice-nogui \
      libc6 libgcc-s1 libicu72 libssl3 libstdc++6 tzdata \
    && rm -rf /var/lib/apt/lists/*
# poppler-utils is required — Claude Code's Read tool silently fails on PDFs without pdftoppm [[11]]
# --no-install-recommends + rm /var/lib/apt/lists: standard Debian layer-hygiene pattern [[2]]

# 2. uv (copy static binary from distroless — Astral's recommended pattern [[8]])
COPY --from=ghcr.io/astral-sh/uv:${UV_VERSION} /uv /uvx /usr/local/bin/

# 3. Python libs for Office-format automation (system Python; add --break-system-packages for PEP 668 [[2]])
RUN pip3 install --no-cache-dir --break-system-packages \
      openpyxl python-docx python-pptx pypdf pdf2image markitdown \
      Pillow opencv-python-headless \
      playwright
# opencv-python-headless over opencv-python: no X11 deps, smaller image [[2]]

# 4. Playwright browsers + system deps (single command pulls libnss3/libasound2/libgbm/etc. [[3]])
RUN npx -y playwright@latest install --with-deps chromium firefox webkit \
    && chmod -R a+rx /ms-playwright || true
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# 5. .NET SDK 9 via Microsoft's install script (docs [[6]][[7]])
RUN curl -sSL https://dot.net/v1/dotnet-install.sh \
      | bash /dev/stdin -Channel ${DOTNET_CHANNEL} -InstallDir /usr/share/dotnet \
    && ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet
ENV DOTNET_ROOT=/usr/share/dotnet DOTNET_CLI_TELEMETRY_OPTOUT=1

# 6. Claude Code itself
RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}

# 7. Non-root user (rename baked-in node:1000 → claude, as HolyClaude does [[2]])
RUN usermod -l claude -d /home/claude -m node \
    && groupmod -n claude node \
    && mkdir -p /home/claude/.claude /workspace \
    && chown -R claude:claude /home/claude /workspace
# Sudo scoped ONLY to firewall init (pattern from FoamoftheSea [[38]])
RUN echo 'claude ALL=(root) NOPASSWD: /usr/local/bin/init-firewall.sh' > /etc/sudoers.d/claude-firewall \
    && chmod 0440 /etc/sudoers.d/claude-firewall

# 8. Egress allowlist script (Anthropic's init-firewall.sh pattern [[33]])
COPY init-firewall.sh /usr/local/bin/init-firewall.sh
RUN chmod 0755 /usr/local/bin/init-firewall.sh \
    && chown root:root /usr/local/bin/init-firewall.sh

# 9. Pre-install skills (bake-at-build pattern [[18]]; mount-at-runtime alternative documented below)
USER claude
WORKDIR /home/claude
RUN git clone --depth=1 https://github.com/obra/superpowers .claude/skills/superpowers || true

WORKDIR /workspace
ENTRYPOINT ["/bin/bash", "-lc", "sudo /usr/local/bin/init-firewall.sh && exec \"$@\"", "--"]
CMD ["claude", "--dangerously-skip-permissions"]
```

Notes:
- **nvm deliberately omitted.** `node:22-bookworm-slim` already ships a pinned Node, so the nvm PATH trap (non-interactive RUN shells don't source `~/.bashrc`) [[9]](https://github.com/nvm-sh/nvm/issues/3531) becomes irrelevant. Use nvm only if you need multi-version Node; if you must, source it in the same `RUN` line: `RUN bash -c '. $NVM_DIR/nvm.sh && nvm install 20 && nvm use 20'`.
- **.NET can be slimmer** by multi-stage-copying from `mcr.microsoft.com/dotnet/sdk:9.0-bookworm-slim` instead of running the install script [[6]](https://github.com/dotnet/dotnet-docker/blob/main/documentation/scenarios/installing-dotnet.md). The install-script path is used here to keep the Dockerfile single-stage and readable.
- **Final image size:** ~3.5–4.5 GB with Chromium + Firefox + WebKit + LibreOffice + .NET [[12]](https://dev.to/coderluii/how-i-run-claude-code-in-docker-with-a-web-ui-and-headless-browser-5dko). Drop `libreoffice-nogui` and one browser to get under 2.5 GB.

## Egress allowlist script

Adapted from Anthropic's `.devcontainer/init-firewall.sh` [[33]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh) — default-DROP on `OUTPUT`, allow loopback/DNS/established, then an ipset populated from a domain list plus GitHub CIDRs fetched live from `api.github.com/meta`. The `mfyz.com` community implementation is the canonical compose-variant [[37]](https://mfyz.com/ai-coding-agent-sandbox-container/).

```bash
#!/usr/bin/env bash
# /usr/local/bin/init-firewall.sh — runs once at container start as root.
set -euo pipefail

# Default-deny
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Loopback + established
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# DNS (needed before resolving anything else)
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# Cloud metadata endpoints: BLOCK before any other OUTPUT rules can match [[41]]
iptables -A OUTPUT -d 169.254.169.254 -j REJECT
iptables -A OUTPUT -d fd00:ec2::254 -j REJECT 2>/dev/null || true

# Allowlist (Anthropic's reference set [[33]] + common tool endpoints)
ipset create -exist allowed-domains hash:ip family inet hashsize 1024 maxelem 65536
for domain in \
    api.anthropic.com statsig.anthropic.com sentry.io \
    registry.npmjs.org pypi.org files.pythonhosted.org \
    api.github.com objects.githubusercontent.com codeload.github.com \
    ghcr.io production.cloudflare.docker.com \
    api.nuget.org dotnetcli.azureedge.net \
    playwright.azureedge.net playwright-download.prod.playwright.dev \
    marketplace.visualstudio.com ; do
  for ip in $(getent ahostsv4 "$domain" | awk '{print $1}' | sort -u); do
    ipset add -exist allowed-domains "$ip"
  done
done

# GitHub CIDRs from the horse's mouth
curl -fsSL https://api.github.com/meta \
  | jq -r '.git[], .web[], .api[]' \
  | while read -r cidr; do ipset add -exist allowed-domains "$cidr" 2>/dev/null || true; done

iptables -A OUTPUT -m set --match-set allowed-domains dst -j ACCEPT
iptables -A OUTPUT -j REJECT --reject-with icmp-admin-prohibited
```

## `docker run` / compose snippet

Minimal one-liner for ad-hoc use:

```bash
docker run --rm -it \
  --name claude-yolo \
  --hostname claude-sandbox \
  --cap-drop=ALL --cap-add=NET_ADMIN --cap-add=NET_RAW \
  --security-opt=no-new-privileges:true \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=1g \
  --tmpfs /home/claude/.cache:rw,nosuid,size=2g \
  --pids-limit=512 --memory=8g --cpus=4 \
  --user claude \
  -v claude-home:/home/claude/.claude \
  -v "$PWD":/workspace \
  -w /workspace \
  claude-yolo:latest
```

The `--cap-drop=ALL` + `--cap-add=NET_ADMIN --cap-add=NET_RAW` pattern is straight from Anthropic's devcontainer [[45]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json) — NET_ADMIN is only needed so `init-firewall.sh` can call iptables at boot; drop it after init if you want stricter posture. `--read-only` + `--tmpfs` for ephemeral scratch space is the canonical hardening recipe [[42]](https://medium.com/@makewithrex/securing-your-ai-agent-a-complete-vps-and-docker-hardening-guide-90bd5b7a0369). The `claude-home` named volume persists `~/.claude/.credentials.json` across restarts [[22]](https://code.claude.com/docs/en/authentication) — crucial because bind-mounting only `.credentials.json` doesn't survive restarts, Claude Code re-prompts for login [[23]](https://github.com/anthropics/claude-code/issues/22066). Note the `--user claude` to avoid running root inside the container [[42]](https://medium.com/@makewithrex/securing-your-ai-agent-a-complete-vps-and-docker-hardening-guide-90bd5b7a0369).

Compose equivalent, with Compose **secrets** (files under `/run/secrets/<name>`, not env vars [[29]](https://docs.docker.com/compose/how-tos/use-secrets/)):

```yaml
# compose.yaml
services:
  claude:
    build: .
    image: claude-yolo:latest
    hostname: claude-sandbox
    user: claude
    working_dir: /workspace
    read_only: true
    cap_drop: [ALL]
    cap_add: [NET_ADMIN, NET_RAW]
    security_opt:
      - no-new-privileges:true
      - seccomp=default
    pids_limit: 512
    mem_limit: 8g
    cpus: 4.0
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=1g
      - /home/claude/.cache:rw,nosuid,size=2g
    volumes:
      - claude-home:/home/claude/.claude          # OAuth creds, plugins, skills
      - ./workspace:/workspace                     # project code
      - ./data/claude-settings.json:/home/claude/.claude/settings.json:ro  # root-owned, immutable [[38]]
    secrets:
      - gh_token                                   # /run/secrets/gh_token
    environment:
      GH_TOKEN_FILE: /run/secrets/gh_token
      DISABLE_TELEMETRY: "1"
    stdin_open: true
    tty: true
    command: ["claude", "--dangerously-skip-permissions"]

volumes:
  claude-home:

secrets:
  gh_token:
    file: ./secrets/gh_token
```

Wrapper script that loads `GH_TOKEN` from the secrets file at session start (so it's never in the process environment of the main shell):

```bash
# ~/.zshrc inside the container
[ -f /run/secrets/gh_token ] && export GH_TOKEN="$(cat /run/secrets/gh_token)"
```

## The toolbelt, line by line

### Playwright

`npx playwright install --with-deps chromium firefox webkit` is the supported path and pulls every system lib automatically (libnss3, libasound2, libatk-bridge2.0, libgbm, libxkbcommon…) [[3]](https://playwright.dev/docs/docker). Microsoft's reference image (`Dockerfile.noble`) just runs `playwright-core install --with-deps` — they don't enumerate apt packages by hand either [[4]](https://github.com/microsoft/playwright/blob/main/utils/docker/Dockerfile.noble). Alpine bases are unsupported because Firefox/WebKit ship glibc-only [[3]](https://playwright.dev/docs/docker). If you only need Chromium, drop `firefox webkit` from the install line — the saved space is substantial (Firefox+WebKit together typically add several hundred MB of binaries on top of Chromium).

### .NET

Two clean paths [[6]](https://github.com/dotnet/dotnet-docker/blob/main/documentation/scenarios/installing-dotnet.md): multi-stage copy from `mcr.microsoft.com/dotnet/sdk:9.0-bookworm-slim`, or `dotnet-install.sh` into `/usr/share/dotnet`. The install-script variant requires `ca-certificates curl libc6 libgcc-s1 libicu74 libssl3t64 libstdc++6 tzdata` pre-installed — it won't pull deps itself [[7]](https://learn.microsoft.com/en-us/dotnet/core/install/linux-scripted-manual).

### Python (uv, openpyxl, python-docx, python-pptx, Pillow, opencv)

Astral's recommended uv install is `COPY --from=ghcr.io/astral-sh/uv:<version> /uv /uvx /bin/` — no curl, no certs, reproducible via tag pin [[8]](https://docs.astral.sh/uv/guides/integration/docker/). For system-Python installs on Bookworm, Debian's PEP-668 `EXTERNALLY-MANAGED` marker blocks `pip install` — `--break-system-packages` bypasses it and is what most YOLO Dockerfiles use rather than maintaining a venv just for tool libs [[2]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/Dockerfile). Prefer `opencv-python-headless` over `opencv-python` in containers — it drops the X11/GUI dependency chain, which is meaningful savings in a headless image [[2]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/Dockerfile).

### Document conversion stack

The canonical trio: **LibreOffice** (`soffice` for PPTX/DOCX → PDF), **Poppler** (`pdftoppm` for PDF → image), **Pandoc** (DOCX text extraction preserving tracked changes) [[10]](https://github.com/tfriedel/claude-office-skills/blob/main/CLAUDE.md). `poppler-utils` is the one people forget — Claude Code's Read tool silently degrades on PDFs in headless `-p` mode without `pdftoppm` [[11]](https://github.com/anthropics/claude-code/issues/29886). Add `tesseract-ocr` if you need OCR for scanned PDFs/images. On the Python side: `pypdf`, `pdf2image`, `markitdown` for high-level conversion; `openpyxl`/`python-docx`/`python-pptx` for structured writes [[10]](https://github.com/tfriedel/claude-office-skills/blob/main/CLAUDE.md).

### Image/video

`ffmpeg imagemagick libvips-dev` covers >95% of what agents reach for [[2]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/Dockerfile). Pillow + opencv-python-headless handle anything Pythonic.

### gh, git, ripgrep, jq

Standard. `ripgrep` and `fd-find` are installed by name on Debian (not `fd` — conflicts with an older package).

## Skills layer

Claude Code discovers skills from **four cascading scopes** with priority `enterprise > personal > project`, plus plugins in their own namespace [[14]](https://code.claude.com/docs/en/skills):

| Scope | Path | Visible to |
|---|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` | all your projects |
| Project | `.claude/skills/<name>/SKILL.md` | this project |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | where plugin is enabled |
| Enterprise | policy-defined | org-wide |

A skill is a directory keyed by `SKILL.md` with YAML frontmatter (`name`, `description`, `allowed-tools`, `paths`, `context`, `hooks`) — supporting templates, scripts, examples sit beside it and are loaded only when referenced [[14]](https://code.claude.com/docs/en/skills). Since v2.1.0, Claude Code hot-reloads skills: add, edit, or remove a skill inside `~/.claude/skills/`, `.claude/skills/`, or any `--add-dir` directory and it takes effect within the current session — but creating a brand-new top-level skills directory that didn't exist at session start needs a restart so the watcher can pick it up [[76]](https://claudefa.st/blog/guide/changelog).

**Skills vs MCP**: Anthropic frames Skills as **procedural knowledge** (≈30–50 tokens, loaded on demand) and MCP as **connectivity/tools** (often 50k+ tokens); Office-doc workflows use Skills, MCP comes in only when you need a live connector [[20]](https://claude.com/blog/skills-explained).

**`allowed-tools` in skill frontmatter** pre-approves a narrow tool set while the skill is active — orthogonal to `--dangerously-skip-permissions` [[14]](https://code.claude.com/docs/en/skills). YOLO bypasses session-wide; skills grant narrow pre-approvals.

### Preinstall strategies in Docker

Four patterns, ordered by reproducibility:

1. **Bake at build time** (recommended default):
   ```dockerfile
   USER claude
   RUN git clone --depth=1 https://github.com/obra/superpowers \
         /home/claude/.claude/skills/superpowers \
    && git clone --depth=1 https://github.com/anthropics/skills \
         /home/claude/.claude/skills/anthropics
   ```
   Pin via `--branch=<tag>` for reproducibility. The `awesome-claude-skills` index confirms this as the mainstream pattern [[18]](https://github.com/karanb192/awesome-claude-skills).

2. **`docker model skills --claude`** — Docker shipped this command specifically for the skills use case; writes to `~/.claude/skills` or a custom `--dest`, supports `--force` [[19]](https://docs.docker.com/reference/cli/docker/model/skills/). Handy as a Dockerfile RUN step if your skill set is on Docker's index.

3. **Plugin marketplace at runtime** — the 2026 canonical install flow for Anthropic/community skill packs:
   ```text
   # runs once per container lifetime, persists via claude-home volume
   /plugin marketplace add anthropics/skills
   /plugin install document-skills@anthropic-agent-skills   # [[16]]
   /plugin install superpowers@claude-plugins-official      # [[17]]
   ```
   The `claude-plugins-official` marketplace is auto-registered at startup [[21]](https://code.claude.com/docs/en/discover-plugins).

4. **Bind-mount the host `~/.claude/skills`** at run time — trades reproducibility for instant edits via the live hot-reload watcher [[76]](https://claudefa.st/blog/guide/changelog). Use when authoring skills; don't use in shared/CI images.

**Anthropic's first-party `anthropics/skills`** ships `docx`, `pdf`, `pptx`, `xlsx` plus example skills [[16]](https://github.com/anthropics/skills). Check the license before baking into production images: the example skills are Apache 2.0, but the document skills (`docx`, `pdf`, `pptx`, `xlsx`) ship a per-directory `LICENSE.txt` binding users to Anthropic's Consumer/Commercial Terms of Service, which prohibit extraction from Services, derivative works, redistribution, and reverse engineering [[75]](https://raw.githubusercontent.com/anthropics/skills/main/skills/docx/LICENSE.txt). **`obra/superpowers`** (Jesse Vincent) ships 20+ battle-tested skills [[18]](https://github.com/karanb192/awesome-claude-skills) and is multi-platform — also runs on Codex, Cursor, Gemini, Copilot CLI, and OpenCode [[17]](https://github.com/obra/superpowers).

## Persisted auth without leaking secrets

**Where Claude Code stores credentials** [[22]](https://code.claude.com/docs/en/authentication):

- Linux/Windows: `~/.claude/.credentials.json`, mode `0600`, or `$CLAUDE_CONFIG_DIR`.
- macOS: encrypted Keychain (irrelevant inside a Linux container).

**Auth precedence (important footgun):** `ANTHROPIC_API_KEY` beats both `apiKeyHelper` and default subscription OAuth. A stray env var silently overrides your Pro/Max login [[22]](https://code.claude.com/docs/en/authentication).

**What works in containers:**

| Pattern | Reproducible | Leak surface | Ergonomics |
|---|---|---|---|
| Mount only `.credentials.json` | no — re-prompts every restart [[23]](https://github.com/anthropics/claude-code/issues/22066) | low | broken |
| Named volume on `/home/claude/.claude` | yes | low | **recommended** |
| Setup container writes `~/.claude` once, prod mounts RO + per-run working copy [[24]](https://claude-did-this.com/claude-hub/getting-started/setup-container-guide) | yes | very low | best for fleets |
| `claude setup-token` → long-lived OAuth token (1-year), pass via `CLAUDE_CODE_OAUTH_TOKEN` | yes | medium (token is bearer) | best for CI [[22]](https://code.claude.com/docs/en/authentication) |
| `ANTHROPIC_API_KEY` as env var | yes | **highest** — `ps auxeww` dumps it [[30]](https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot/) | easy, **don't** |
| Docker Sandboxes OAuth proxy (creds never enter container) [[26]](https://docs.docker.com/ai/sandboxes/agents/claude-code/) | yes | lowest | best if you're on Docker Sandboxes |

**OAuth-in-devcontainer fails by default** — the random ephemeral callback port isn't forwarded to the host browser [[25]](https://github.com/anthropics/claude-code/issues/20793). Workarounds: pin `--callback-port` and pre-declare `forwardPorts` in `devcontainer.json`, or do OAuth once on the host and bake the `~/.claude` directory into the named volume.

**gh CLI.** Prefers system credential store, falls back to plaintext `hosts.yml`. For automation, the manual recommends **`GH_TOKEN` env var with a fine-grained PAT** [[27]](https://cli.github.com/manual/gh_auth_login) — scoped to selected repositories, minimal permissions, with an expiration date [[28]](https://github.blog/security/application-security/introducing-fine-grained-personal-access-tokens-for-github/). Never mount your host `~/.config/gh` with a classic full-scope PAT.

**Why env-var API keys are the worst option.** Beyond the auth-precedence footgun, static keys are **bearer strings with no binding to user/device/workload** — any prompt-injected process can exfiltrate and replay them without revocation trail [[32]](https://www.beyondidentity.com/resource/the-attacker-gave-claude-their-api-key-why-ai-agents-need-hardware-bound-identity). The live 2025 exploit: `ps auxeww | grep` dumped `ANTHROPIC_API_KEY` and `GITHUB_TOKEN` from the subprocess's inherited environment into a PR comment [[30]](https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot/). **CVE-2025-59536** proved even files-only auth is at risk: a malicious `.claude/settings.json` can override `ANTHROPIC_BASE_URL` *before the trust dialog renders*, leaking the Authorization header on the next request [[31]](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/) — the fix is the egress allowlist (attacker's URL isn't in it).

**Defense in depth for credentials:**
1. Never pass secrets as env vars. Use Compose secrets (`/run/secrets/<name>`, file-mounted, service-scoped [[29]](https://docs.docker.com/compose/how-tos/use-secrets/)).
2. Load from secrets file into shell env **only in your interactive shell rcfile**, so it's scoped to your session and not inherited by every subprocess.
3. Use fine-grained PATs with expiry, per-project scope [[28]](https://github.blog/security/application-security/introducing-fine-grained-personal-access-tokens-for-github/).
4. For Anthropic auth, prefer **OAuth subscription login** (Pro/Max) over API keys when possible — OAuth access tokens are short-lived (~1 hour) with a revocable refresh token, where static `ANTHROPIC_API_KEY` values never expire unless manually rotated [[77]](https://daveswift.com/claude-oauth-update/). Trade-off: OAuth's 1-hour expiry can break unattended runs, so choose deliberately.
5. Root-own `.claude/settings.json` and mount it read-only so a malicious repo's `.claude/settings.json` can't override it [[38]](https://github.com/FoamoftheSea/claude-code-sandbox).

## Sandbox hardening — what actually matters

Ordered by bang-for-buck. Every row here is a real attack prevented, not a theoretical rung.

1. **Deny-by-default egress with allowlist.** The single highest-impact control. Cuts the "external comms" leg of the lethal trifecta [[36]](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). Implementation: iptables + ipset inside the container (needs temporary NET_ADMIN at boot) [[33]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh), or an external egress proxy with SNI peek/splice (iron-proxy, Squid) [[44]](https://github.com/ironsh/iron-proxy) — avoid mitmproxy for this, it's a debugger not an enforcer.
2. **Block cloud metadata endpoints.** `169.254.169.254` and `fd00:ec2::254` — without this, a prompt injection on an EC2/GCE host steals IAM credentials in one HTTP call [[41]](https://www.wiz.io/blog/imds-anomaly-hunting-zero-day). Add `iptables -A OUTPUT -d 169.254.169.254 -j REJECT` **before** the allowlist rules.
3. **No `/var/run/docker.sock` mount.** Ever. Mounting it is **worse than `--privileged`** because the container looks clean to scanners yet can spawn unlimited new privileged containers — a one-liner owns the host [[39]](https://opscart.com/docker-runtime-escape-why-mounting-docker-sock-is-worse-than-running-privileged-containers/). Claude Code's own `/sandbox` docs explicitly warn about `allowUnixSockets` for the same reason [[34]](https://code.claude.com/docs/en/sandboxing).
4. **Non-root user.** `--user 1000:1000`, rename the baked-in `node` UID to `claude` if you're on `node:22-slim` [[2]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/Dockerfile). Sudo scoped to exactly `init-firewall.sh` only.
5. **`--cap-drop=ALL` + narrow `--cap-add`.** Keep NET_ADMIN only if you're running `init-firewall.sh` inside the container at boot; drop it immediately after, or run the firewall in a separate sidecar. Never keep CAP_SYS_ADMIN, CAP_SYS_MODULE, CAP_DAC_READ_SEARCH, or CAP_NET_RAW in a YOLO container [[40]](https://blaxel.ai/blog/container-escape).
6. **`--read-only` rootfs + tmpfs.** Immutable root prevents binary modification; `/tmp` and `~/.cache` are tmpfs. Combine with `--security-opt=no-new-privileges:true` to block setuid escalation [[42]](https://medium.com/@makewithrex/securing-your-ai-agent-a-complete-vps-and-docker-hardening-guide-90bd5b7a0369).
7. **Root-owned, read-only `claude-settings.json`.** Stops a hostile repo from rewriting the agent's own allowlist or hooks mid-session [[38]](https://github.com/FoamoftheSea/claude-code-sandbox). This is the defense against CVE-2025-59536-style attacks [[31]](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/).
8. **Resource limits.** `--pids-limit`, `--memory`, `--cpus` against fork bombs and runaway loops [[38]](https://github.com/FoamoftheSea/claude-code-sandbox).
9. **Don't bind-mount $HOME.** Per-project workspace volume only. Your `~/.ssh`, `~/.aws`, `~/.gcloud` stay on the host [[35]](https://www.anthropic.com/engineering/claude-code-sandboxing).
10. **Keep the default seccomp profile.** Docker's default profile is an allowlist that blocks ~44 syscalls out of 300+, including `keyctl`/`add_key`/`request_key` (kernel keyring isn't namespaced), `mount`/`umount`, `unshare`/`setns`, `kexec_load`, `reboot`, `ptrace`, and the `io_uring_*` family implicated in recent container escapes [[70]](https://docs.docker.com/engine/security/seccomp/). Datadog Security Labs calls it "a good level of isolation" — it blocked real-world breakouts like CVE-2022-0185 [[71]](https://securitylabs.datadoghq.com/articles/container-security-fundamentals-part-6/). Default seccomp plus `cap-drop=ALL` is the layered baseline OWASP recommends — capabilities and seccomp are complementary, not alternatives [[73]](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html). Never `--privileged` (disables seccomp regardless of any profile flag [[70]](https://docs.docker.com/engine/security/seccomp/)), and avoid `seccomp=unconfined` — it re-enables `finit_module` and friends, letting a compromised container load kernel modules if it also retains `CAP_SYS_MODULE` [[72]](https://tbhaxor.com/breakout-from-seccomp-unconfined-container/). The Docker community's guidance on the exact `SYS_PTRACE + seccomp=unconfined` combo (which HolyClaude uses, below) is to start from the default profile and remove only specific syscalls, not unconfine wholesale [[74]](https://forums.docker.com/t/security-implications-of-cap-add-sys-ptrace-security-opt-seccomp-unconfined-needed-for-rr/49816).
11. **VM-grade isolation for untrusted input.** For workloads where namespace isolation feels insufficient: **gVisor** (user-space syscall interception), **Kata Containers** (lightweight VMs), or **Firecracker microVMs** (~100–200 ms boot, KVM-enforced). Firecracker is the 2026 gold standard for untrusted AI code [[43]](https://dev.to/agentsphere/choosing-a-workspace-for-ai-agents-the-ultimate-showdown-between-gvisor-kata-and-firecracker-b10).

## Community approaches compared

| Tool | Stars (Apr 2026) | Last release | Setup | Isolation | Tool coverage | Auth UX | Uses `--dangerously-skip-permissions` | Maintenance |
|---|---|---|---|---|---|---|---|---|
| [anthropics/.devcontainer](https://github.com/anthropics/claude-code/tree/main/.devcontainer) | sub-dir | active [[13]](https://github.com/anthropics/claude-code/tree/main/.devcontainer) | devcontainer.json via VS Code | non-root + iptables allowlist + NET_ADMIN/RAW [[45]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json) | lean (no Python/browsers/Office) [[1]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/Dockerfile) | named volume `/home/node/.claude` [[45]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json) | **No** (deliberately) [[45]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/devcontainer.json) | Anthropic team, active |
| [Docker Sandboxes](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/) | product | GA Jan 2026 [[51]](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/) | `sbx run claude` one-liner [[51]](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/) | microVM + nested docker + allow/deny net [[51]](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/) | broad | OAuth proxy, no creds in container [[26]](https://docs.docker.com/ai/sandboxes/agents/claude-code/) | **Yes** (default) [[51]](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/) | Docker Inc, active |
| [HolyClaude](https://github.com/CoderLuii/HolyClaude) | ~2.1k [[46]](https://github.com/CoderLuii/HolyClaude) | 2026-04-10 [[46]](https://github.com/CoderLuii/HolyClaude) | `docker compose up -d` [[46]](https://github.com/CoderLuii/HolyClaude) | **weak** — `cap_add: [SYS_ADMIN, SYS_PTRACE]` + `seccomp=unconfined`, no `cap_drop`, no `read_only`, no Docker-level user [[68]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/docker-compose.yaml)[[69]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/docker-compose.full.yaml) | very broad (7 AI CLIs + browsers + FFmpeg) [[46]](https://github.com/CoderLuii/HolyClaude) | OAuth via web UI, bind-mount `./data/claude` [[46]](https://github.com/CoderLuii/HolyClaude) | No (defaults to `allowEdits`) [[46]](https://github.com/CoderLuii/HolyClaude) | Single dev, daily commits |
| [claudebox](https://github.com/RchGrav/claudebox) | ~1k [[52]](https://github.com/RchGrav/claudebox) | v2.0.0 Jul 2025 [[52]](https://github.com/RchGrav/claudebox) | self-extracting installer | per-project firewall allowlist, optional sudo [[52]](https://github.com/RchGrav/claudebox) | 15+ profiles (C/C++, Rust, Go, ML…) [[52]](https://github.com/RchGrav/claudebox) | per-project `~/.claudebox/<p>/.claude/` [[52]](https://github.com/RchGrav/claudebox) | **Yes** (flag) [[52]](https://github.com/RchGrav/claudebox) | Single dev |
| [container-use](https://github.com/dagger/container-use) | ~3.7k [[50]](https://github.com/dagger/container-use) | v0.4.2 Aug 2025 [[50]](https://github.com/dagger/container-use) | `cu stdio` as MCP server [[50]](https://github.com/dagger/container-use) | per-agent container + per-task git branch [[50]](https://github.com/dagger/container-use) | Dagger-defined envs | n/a (MCP add-on) | n/a (MCP add-on) | Dagger team |
| [Sculptor](https://github.com/imbue-ai/sculptor) | ~146 [[48]](https://github.com/imbue-ai/sculptor) | Sep 2025 beta [[48]](https://github.com/imbue-ai/sculptor) | Docker Desktop + installer [[49]](https://imbue.com/sculptor-announce/) | per-agent containers, Mutagen bidirectional sync [[49]](https://imbue.com/sculptor-announce/) | broad | API key now, OAuth Pro/Max coming [[48]](https://github.com/imbue-ai/sculptor) | not documented | Imbue team |
| [claude-code-sandbox](https://github.com/textcortex/claude-code-sandbox) | 308 [[47]](https://github.com/textcortex/claude-code-sandbox) | **Archived Feb 2026** [[47]](https://github.com/textcortex/claude-code-sandbox) | `npm i -g` + CLI | Docker/Podman, files copied (not mounted) [[47]](https://github.com/textcortex/claude-code-sandbox) | moderate | auto-discovers API/GH/AWS creds (risky) [[47]](https://github.com/textcortex/claude-code-sandbox) | **Yes** [[47]](https://github.com/textcortex/claude-code-sandbox) | → Spritz |
| [FoamoftheSea/claude-code-sandbox](https://github.com/FoamoftheSea/claude-code-sandbox) | small [[38]](https://github.com/FoamoftheSea/claude-code-sandbox) | active | docker run | **strong** — iptables + scoped sudo + root-owned settings + pids/mem limits [[38]](https://github.com/FoamoftheSea/claude-code-sandbox) | moderate | mounted credential dir | **Yes** [[38]](https://github.com/FoamoftheSea/claude-code-sandbox) | Single dev |
| [mfyz reference](https://mfyz.com/ai-coding-agent-sandbox-container/) | blog | blog | docker-compose [[37]](https://mfyz.com/ai-coding-agent-sandbox-container/) | NET_ADMIN boot → non-root devuser, default-deny egress [[37]](https://mfyz.com/ai-coding-agent-sandbox-container/) | moderate | mount host `~/.claude` | **Yes** [[37]](https://mfyz.com/ai-coding-agent-sandbox-container/) | Reference post |
| [E2B](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026) | cloud | — | API | Firecracker microVM, ~150ms [[53]](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026) | SDK-defined | API key | via SDK | Funded company |
| [Daytona](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026) | cloud | $24M Series A Feb 2026 [[53]](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026) | API | Docker, 27–90 ms provisioning [[53]](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026) | SDK-defined | API key | via SDK | Funded company |
| [Modal Sandbox](https://platform.claude.com/docs/en/agent-sdk/hosting) | cloud | — | SDK [[54]](https://platform.claude.com/docs/en/agent-sdk/hosting) | gVisor, dynamic definition [[53]](https://www.superagent.sh/blog/ai-code-sandbox-benchmark-2026) | SDK-defined | API key | via SDK | Funded company |

Anthropic's own **Agent SDK hosting docs** explicitly name Modal Sandbox, Cloudflare Sandboxes, Daytona, E2B, Fly Machines, and Vercel Sandbox as supported cloud runtimes [[54]](https://platform.claude.com/docs/en/agent-sdk/hosting) — if you're shipping agents to production, skip the local-Docker question entirely and pick one of those.

**Picks:**
- **Fastest start on a dev machine:** Docker Sandboxes — `sbx run claude`, OAuth proxy keeps creds out of container, microVM isolation by default [[51]](https://www.docker.com/blog/docker-sandboxes-run-claude-code-and-other-coding-agents-unsupervised-but-safely/). Only caveat: macOS/Windows as of Apr 2026, Linux coming.
- **Need a specific toolbelt (Playwright + .NET + LibreOffice + your skills) and full control:** roll your own off the reference Dockerfile above — start from Anthropic's `.devcontainer/` [[13]](https://github.com/anthropics/claude-code/tree/main/.devcontainer), add the tool layers.
- **Multi-project, per-project auth/history isolation:** claudebox [[52]](https://github.com/RchGrav/claudebox).
- **Parallel agents on separate git branches:** container-use [[50]](https://github.com/dagger/container-use) (MCP add-on, works alongside any setup above).
- **Avoid HolyClaude** for security-sensitive work — both its compose files add `SYS_ADMIN + SYS_PTRACE` capabilities and set `seccomp=unconfined`, with no `cap_drop`, no `read_only`, and no Docker-level user mapping [[68]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/docker-compose.yaml)[[69]](https://raw.githubusercontent.com/CoderLuii/HolyClaude/master/docker-compose.full.yaml). It's an AI coding **workstation**, not a sandbox.

## Native `/sandbox` vs Docker

Anthropic shipped a native `/sandbox` mode in 2025 that uses **bubblewrap** on Linux/WSL2 and **Seatbelt** on macOS, routing egress through an external proxy with a domain allowlist [[34]](https://code.claude.com/docs/en/sandboxing). Anthropic claims it cuts permission prompts 84% [[58]](https://www.anthropic.com/engineering/claude-code-auto-mode). Inside Docker, `/sandbox` requires `enableWeakerNestedSandbox` which the docs explicitly warn "considerably weakens security" — so pick **one** sandbox layer and commit:

- Native: `/sandbox` + bubblewrap, on host, no Docker involvement.
- Container: Docker (or Docker Sandboxes microVM), no nested `/sandbox`.

## Non-obvious failure modes

- **devcontainer feature overwrites your init-firewall.sh.** `ghcr.io/anthropics/devcontainer-features/claude-code` runs **after** the Dockerfile build and silently replaces `/usr/local/bin/init-firewall.sh` with its stock version, wiping your custom allowlist [[55]](https://github.com/anthropics/claude-code/issues/32113). Either don't use the feature, or re-apply your script in `postStartCommand`.
- **Auth precedence.** `ANTHROPIC_API_KEY` in env silently wins over your OAuth login. Unset it explicitly in the wrapper if you want the Pro/Max subscription path [[22]](https://code.claude.com/docs/en/authentication).
- **Poppler missing ≠ PDF read failure you can see.** Claude Code's Read tool silently degrades on PDFs without `poppler-utils` [[11]](https://github.com/anthropics/claude-code/issues/29886) — the logs are quiet. Always include it.
- **nvm PATH trap.** Each `RUN` is a fresh non-interactive shell — `~/.bashrc` never sources, `nvm use` has no effect [[9]](https://github.com/nvm-sh/nvm/issues/3531). Source in the same `RUN` line, or don't use nvm.
- **`.credentials.json`-only mount re-prompts every restart.** Mount the whole `~/.claude` directory, not the single file [[23]](https://github.com/anthropics/claude-code/issues/22066).
- **MCP STDIO architectural flaw.** April 2026 research showed MCP's STDIO handling lets unauthenticated command injection land zero-click across 200k+ servers; Anthropic declined to change it [[65]](https://www.theregister.com/2026/04/16/anthropic_mcp_design_flaw/). Audit every MCP server you connect, pin versions, don't install from untrusted README instructions.

## When NOT to use this

- **Cloud-hosted agents in prod** — use one of Anthropic's named runtimes (Modal, Cloudflare, Daytona, E2B, Fly, Vercel) [[54]](https://platform.claude.com/docs/en/agent-sdk/hosting).
- **Ephemeral CI jobs** — the build cost of this image makes it miserable. Use a prebuilt `mcr.microsoft.com/playwright` or a hosted sandbox.
- **Truly untrusted input** (random repos from the internet, unsolicited PRs) — graduate to Firecracker microVM or a hosted sandbox that already runs on one [[43]](https://dev.to/agentsphere/choosing-a-workspace-for-ai-agents-the-ultimate-showdown-between-gvisor-kata-and-firecracker-b10). Namespace isolation isn't enough against prompt-injection-weaponized kernel CVEs [[40]](https://blaxel.ai/blog/container-escape).
