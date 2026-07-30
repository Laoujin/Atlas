---
title: "Credential isolation for an agentic coding CLI on Linux"
date: 2026-07-30
depth: standard
format: md
topic: "Credential and secret isolation for an agentic coding CLI on Linux (2026). Answer: what can an agent with read access to $HOME actually reach, and how do you shrink that?"
topic_raw: "switching from windows to linux. on my system, I'm also going to run Claude. for my homelab I'm using proxmox on the minipc to \"separate\" systems. for running claude \"safely\", what can I do there?"
tags: [security, linux, claude-code, credentials, ssh, secrets-management]
summary: "An agent that can read $HOME holds your whole identity, and on Linux the keyring does not help — so give the agent its own short-lived, narrowly scoped credentials instead."
citations: 32
reading_time_min: 11
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 648
issue: 12
---

> **Decision.** Assume anything readable under `$HOME` is already exfiltrated: 2026's npm stealers sweep `~/.ssh`, `~/.aws/credentials`, `~/.kube/config` **and** `~/.claude/.credentials.json` by name [[1]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ironworm-ebpf-rootkit-npm-supply-chain-202/)[[2]](https://code.claude.com/docs/en/authentication). Moving secrets into the GNOME keyring does **not** fix this — once your login keyring is unlocked, any process running as you can ask D-Bus for every secret in it [[3]](https://github.com/swiesend/secret-service) ⭐ 38. The only durable answer is to change *what the credentials are*: give the agent its own identity (FIDO2-backed SSH key, repo-scoped fine-grained PAT), make everything else short-lived and injected at process start, and keep a revocation drill.

## 1. Inventory: what read access to `$HOME` actually buys

This is not hypothetical. Three independent 2026 campaigns published the file lists they sweep.

| Path | What it grants | Confirmed target |
|---|---|---|
| `~/.ssh/id_*` | Git push, server login, lateral movement | [[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html)[[6]](https://www.endorlabs.com/learn/shai-hulud-the-third-coming----inside-the-bitwarden-cli-2026-4-0-supply-chain-attack) |
| `~/.aws/credentials` | Long-lived IAM access keys | [[1]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ironworm-ebpf-rootkit-npm-supply-chain-202/)[[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html) |
| `~/.kube/config` | Cluster admin, often with embedded client certs | [[1]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ironworm-ebpf-rootkit-npm-supply-chain-202/)[[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html) |
| `~/.docker/config.json` | Registry push (base64, not encrypted) | [[1]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ironworm-ebpf-rootkit-npm-supply-chain-202/)[[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html) |
| `~/.npmrc`, `~/.pypirc` | Package publish → supply-chain pivot | [[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html)[[5]](https://safedep.io/wshu-net-npm-credential-stealer-campaign/) |
| `~/.git-credentials`, `~/.netrc`, `~/.pgpass` | Plaintext host passwords/tokens by design | [[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html) |
| `~/.config/gh/hosts.yml` | GitHub OAuth token, plaintext on keyring fallback | [[8]](https://github.com/cli/cli/issues/10108) ⭐ 46k |
| `.env` in every repo | DB URLs, Stripe keys, service tokens | [[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html)[[5]](https://safedep.io/wshu-net-npm-credential-stealer-campaign/) |
| `~/.config/*/Cookies` | Live browser sessions (bypasses MFA) | [[7]](https://gist.github.com/creachadair/937179894a24571ce9860e2475a2d2ec) |
| `~/.claude/.credentials.json` | Your Claude OAuth access + refresh token | [[1]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ironworm-ebpf-rootkit-npm-supply-chain-202/) |
| `~/.bash_history`, `~/.zsh_history` | Secrets pasted into one-off commands | [[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html) |
| `process.env` of the agent | Everything your shell profile exports | [[6]](https://www.endorlabs.com/learn/shai-hulud-the-third-coming----inside-the-bitwarden-cli-2026-4-0-supply-chain-attack) |

Two details worth internalising. IronWorm (June 2026) reads 86 environment variables plus 20+ credential paths and names the AI-CLI credential stores explicitly — `~/.claude/.credentials.json` and `~/.codex/auth.json` [[1]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ironworm-ebpf-rootkit-npm-supply-chain-202/). And the trojanned `@bitwarden/cli` 2026.4.0 (22 Apr 2026, live on npm ~90 minutes) ran seven parallel collectors, dumped the whole `process.env`, enumerated AWS Secrets Manager / SSM / GCP Secret Manager / Azure Key Vault, and specifically went after authenticated AI coding assistants [[6]](https://www.endorlabs.com/learn/shai-hulud-the-third-coming----inside-the-bitwarden-cli-2026-4-0-supply-chain-attack). Your secret manager's CLI is itself supply-chain surface.

Browser cookies deserve a note because they defeat MFA: Chromium on Linux keeps cookies in a SQLite DB with the *values* encrypted under a key held in the GNOME keyring — and older builds used the hardcoded passphrase `peanuts` [[7]](https://gist.github.com/creachadair/937179894a24571ce9860e2475a2d2ec). Encrypted-at-rest, trivially decryptable by a process that can talk to your keyring.

## 2. The Linux trap: a keyring is not a boundary

Coming from Windows, DPAPI conditions you to expect per-user-at-rest encryption. Linux's equivalent is **gnome-keyring** (or KWallet) exposed over the freedesktop **Secret Service** API on the session D-Bus. `pam_gnome_keyring` unlocks the `login` collection with your password when you log in, so it stays unlocked for the whole desktop session — and there is no per-application gate: "other applications can easily read **any** secret, if the keyring is unlocked" [[3]](https://github.com/swiesend/secret-service) ⭐ 38. D-Bus `busconfig`/`policy` controls aren't enabled by default and are spoofable anyway [[3]](https://github.com/swiesend/secret-service). This is filed as CVE-2018-19358 and *disputed* by GNOME on the grounds that untrusted apps shouldn't reach your session bus in the first place [[10]](https://nvd.nist.gov/vuln/detail/CVE-2018-19358).

→ The keyring protects against offline disk theft and other *users*. It does nothing against an agent running as you.

That reframes the git credential helper choice. Pick by *what it costs an attacker*, not by "encrypted vs not":

| Helper | Storage | Value to an agent running as you |
|---|---|---|
| `store` | plaintext `~/.git-credentials` | ✗ immediate, and it's on every stealer's path list [[4]](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html) |
| `libsecret` | Secret Service / gnome-keyring [[9]](https://git-scm.com/doc/credential-helpers) | ⚠ one D-Bus call away while unlocked [[3]](https://github.com/swiesend/secret-service) |
| `pass` (GPG) | GPG-encrypted files [[9]](https://git-scm.com/doc/credential-helpers) | ⚠ safe only if the GPG key needs a touch/PIN, not a cached agent passphrase |
| `cache` | memory, TTL only [[9]](https://git-scm.com/doc/credential-helpers) | ⚠ but the window is bounded |
| `git-credential-oauth` | generates OAuth creds, pairs with `cache` [[11]](https://github.com/hickford/git-credential-oauth) ⭐ 849 | ✓ best of the built-ins: short-lived, re-auth needs a browser |
| `ghtkn` | 8-hour GitHub App user token, keyring [[16]](https://github.com/suzuki-shunsuke/ghtkn) ⭐ 252 | ✓ short-lived *and* App-scoped |

[git-credential-oauth](https://hickford.github.io/git-credential-oauth/) is packaged in Fedora, Debian and Ubuntu and is designed to sit in front of a storage helper — configure `cache` with a timeout first, then `oauth` [[11]](https://github.com/hickford/git-credential-oauth). [ghtkn](https://github.com/suzuki-shunsuke/ghtkn) ⭐ 252 goes further: device-flow GitHub App user access tokens that expire in 8 hours, selectable per repository owner, with only a Client ID on disk — no private key, no client secret [[16]](https://github.com/suzuki-shunsuke/ghtkn).

## 3. Claude Code's own credential

| | Linux | macOS | Windows |
|---|---|---|---|
| Location | `~/.claude/.credentials.json` | Keychain (encrypted) | `%USERPROFILE%\.claude\.credentials.json` |
| Protection | file mode `0600` | Keychain ACL | profile-directory ACL |

Source: [[2]](https://code.claude.com/docs/en/authentication). `0600` stops other *users*, not other processes of yours — which is exactly the threat IronWorm exercises [[1]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ironworm-ebpf-rootkit-npm-supply-chain-202/). `CLAUDE_CONFIG_DIR` relocates the file, which is how you keep a throwaway agent identity separate from your interactive one [[2]](https://code.claude.com/docs/en/authentication).

There is no native keyring backend on Linux, but there is a supported seam: **`apiKeyHelper`**, a shell script Claude Code calls for a key, re-invoked after 5 minutes or on HTTP 401, with the interval tunable via `CLAUDE_CODE_API_KEY_HELPER_TTL_MS` [[2]](https://code.claude.com/docs/en/authentication). That is the hook for vault-issued short-lived tokens — the docs name that use case directly. It sits at position 4 in the precedence chain, below `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_API_KEY` [[2]](https://code.claude.com/docs/en/authentication).

⚠ `claude setup-token` mints a **one-year** OAuth token and prints it without saving it anywhere [[2]](https://code.claude.com/docs/en/authentication). Convenient for CI, a liability in a dotfile — if you use it, source it from a secret manager at process start, never `export` it from `.bashrc`.

## 4. Per-agent identity

**SSH.** Generate a key that exists only for the agent, and constrain it at the *server* side, where the agent can't edit the policy. `authorized_keys` options are evaluated before the key is accepted: `restrict` "disable[s] port, agent and X11 forwarding, as well as disabling PTY allocation and execution of `~/.ssh/rc`"; `from=` pins the source host; `command=` forces one command and ignores whatever the client asked for [[13]](https://man.openbsd.org/sshd.8).

```
restrict,from="10.0.0.0/24",command="/usr/local/bin/agent-git-shell" sk-ssh-ed25519@openssh.com AAAA...
```

**GitHub.** Ranked by blast radius:

| Credential | Scope | Lifetime |
|---|---|---|
| Classic PAT | all orgs you belong to + all personal repos [[14]](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) | can be set never to expire [[15]](https://www.systemshardening.com/articles/cicd/github-app-token-security/) |
| Fine-grained PAT | one owner, chosen repos, itemised permissions [[14]](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) | mandatory expiry, defaults to 1 year [[15]](https://www.systemshardening.com/articles/cicd/github-app-token-security/) |
| GitHub App installation token | subset of installed repos via `repositories`, per-permission [[15]](https://www.systemshardening.com/articles/cicd/github-app-token-security/) | **max 1 hour** [[15]](https://www.systemshardening.com/articles/cicd/github-app-token-security/) |

GitHub itself recommends fine-grained over classic "whenever possible" [[14]](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens). For a solo operator the sweet spot is a fine-grained PAT scoped to the *single repo* the agent is working in, with `contents: write` and nothing else — or ghtkn's App-backed 8-hour token if you want expiry measured in hours [[16]](https://github.com/suzuki-shunsuke/ghtkn) ⭐ 252. A separate GitHub account is heavier than it looks (it needs its own collaborator grants and 2FA) and buys little over a repo-scoped token.

**npm.** The ground already shifted: all classic npm tokens were permanently revoked on 9 Dec 2025, and new write-enabled granular tokens default to 7-day expiry with a 90-day ceiling [[18]](https://ssojet.com/news/important-npm-security-updates-token-management-and-auth-changes). Publish from CI via [trusted publishing](https://docs.npmjs.com/trusted-publishers/) (OIDC, temporary job-scoped credentials) and keep no publish token in `~/.npmrc` at all [[17]](https://docs.npmjs.com/trusted-publishers/). ⚠ IronWorm abused Trusted Publishing itself to push poisoned versions from compromised repos [[1]](https://labs.cloudsecurityalliance.org/research/csa-research-note-ironworm-ebpf-rootkit-npm-supply-chain-202/) — OIDC removes the stored token, not the need for branch protection.

## 5. The SSH agent is an exfil channel

`SSH_AUTH_SOCK` is a unix socket in `/tmp` that any process of yours can use to sign with your keys. Forward the agent to a box and that box can use your keys too [[19]](https://docs.ssh-mitm.at/user_guide/sshagent.html). Mitigations, weakest to strongest:

1. **Don't forward.** Use `ProxyJump` instead of `ForwardAgent`.
2. **`ssh-add -c`** — per-use confirmation via `ssh-askpass`, plus `-t` for a lifetime cap [[20]](https://man.openbsd.org/ssh-add.1). ⚠ askpass is *software*: malware controlling your desktop can click it for you [[19]](https://docs.ssh-mitm.at/user_guide/sshagent.html).
3. **FIDO2-backed keys** — `ed25519-sk` / `ecdsa-sk`, OpenSSH 8.2+. "The private key never leaves the hardware", a touch is always required unless explicitly disabled, and `-O verify-required` adds a PIN or fingerprint per use [[21]](https://developers.yubico.com/SSH/Securing_SSH_with_FIDO2.html).

A hardware-backed key is the one control on this page that survives full compromise of the agent's process: the agent can *request* a signature, but it cannot steal the key or fake your finger, and each use is a physical event you notice.

## 6. Inject at process start, don't persist on disk

Replace static files with a manager that hands the secret to the child process and nothing else.

| Tool | Command | Notes |
|---|---|---|
| [1Password CLI](https://www.1password.dev/cli/secrets-environment-variables/) | `op run -- <cmd>` | Resolves `op://` refs, secrets exist "only for the duration of the process" [[22]](https://www.1password.dev/cli/secrets-environment-variables/) |
| [Bitwarden Secrets Manager](https://bitwarden.com/help/secrets-manager-cli/) | `bws run` | `--no-inherit-env` starts from a clean environment [[23]](https://bitwarden.com/help/secrets-manager-cli/) |
| [Infisical](https://infisical.com) ⭐ 28k | `infisical run` | Open-source, E2E encrypted; agent injects without code changes [[24]](https://github.com/Infisical/infisical) |
| [Vault](https://developer.hashicorp.com/vault/docs/secrets/aws) | AWS secrets engine | Dynamic, time-bound AWS creds instead of static keys [[26]](https://developer.hashicorp.com/vault/docs/secrets/aws) |
| AWS IAM Identity Center | `aws configure sso` | Temporary creds only; revocation lands within the session lifetime [[25]](https://www.rhythmictech.com/blog/iam-access-keys-bad-aws-sso-good/) |

Deleting `~/.aws/credentials` in favour of `aws sso` removes one whole row from §1's table [[25]](https://www.rhythmictech.com/blog/iam-access-keys-bad-aws-sso-good/). ⚠ `--no-inherit-env` matters more than it sounds: if you `op run` the agent, the agent inherits every other secret already in your shell unless you strip it.

## 7. Keep secrets out of the transcript and telemetry

Anything the agent reads lands in its transcript, and a secret in a transcript is a secret in a support bundle. Claude Code's OTel export is redacted by default — prompt text, assistant responses, tool parameters and tool content all require an explicit `OTEL_LOG_*` opt-in [[12]](https://code.claude.com/docs/en/monitoring-usage). Leave them off; `OTEL_LOG_RAW_API_BODIES` in particular implies consent to everything the other three would reveal [[12]](https://code.claude.com/docs/en/monitoring-usage).

For the read side, deny rules use gitignore-style patterns and are evaluated before ask and allow [[27]](https://code.claude.com/docs/en/permissions):

```json
{ "permissions": { "deny": [
  "Read(//**/.env)", "Read(//**/.env.*)",
  "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(~/.kube/**)",
  "Read(~/.docker/config.json)", "Read(~/.npmrc)", "Read(~/.git-credentials)",
  "Read(~/.config/gh/**)", "Read(~/.claude/.credentials.json)"
] } }
```

⚠ Know what this is worth. Deny rules cover the built-in file tools and Bash file commands Claude Code recognises (`cat`, `head`, `tail`, `sed`) — they "don't apply to arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself" [[27]](https://code.claude.com/docs/en/permissions). It's a guardrail against accidental reads and lazy prompt injection, not a boundary. The boundary is that the secret isn't there.

Note also that running the agent as a **dedicated OS user** looks like the obvious fix and isn't: you end up hand-tuning ACLs forever to keep `.env` files out of reach [[32]](https://patrickmccanna.net/a-better-way-to-limit-claude-code-and-other-coding-agents-access-to-secrets/). Containment belongs to sandboxing/VM layers; credentials are a separate axis.

## 8. Detection and the revocation drill

- **Pre-commit:** [Gitleaks](https://github.com/gitleaks/gitleaks) ⭐ 28k — regex-based, millisecond runtime, SARIF output [[28]](https://github.com/gitleaks/gitleaks).
- **CI / history:** [TruffleHog](https://github.com/trufflesecurity/trufflehog) ⭐ 27k — verifies each hit against the issuing API and labels it verified / unverified / unknown [[29]](https://github.com/trufflesecurity/trufflehog). The 2026 consensus stack is Gitleaks at commit time, TruffleHog for depth, platform scanning behind both [[30]](https://appsecsanta.com/secret-scanning-tools/gitleaks-vs-trufflehog).
- **Server side:** GitHub push protection blocks pushes containing secrets *before* they reach the repo, covering CLI pushes, UI commits, the REST API and MCP-server interactions, and is on by default for user accounts pushing to public repos [[31]](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection).

**Rehearse revocation before you need it.** The Bitwarden remediation guidance is a usable template: rotate all in-scope credentials (GitHub PATs, npm tokens, AWS keys), audit publish logs for unexpected patch bumps, and inspect `~/.bashrc` / `~/.zshrc` for appended code [[6]](https://www.endorlabs.com/learn/shai-hulud-the-third-coming----inside-the-bitwarden-cli-2026-4-0-supply-chain-attack) — stealers persist there and via `~/.config/systemd/user` units [[5]](https://safedep.io/wshu-net-npm-credential-stealer-campaign/). Time yourself once. If revoking everything the agent could touch takes more than ten minutes, the layout below is too broad.

## 9. A minimal-privilege credential layout

| Credential | Where it lives | Lifetime |
|---|---|---|
| Git push identity | `sk-ssh-ed25519` on a hardware token; `restrict,from=` in `authorized_keys` [[13]](https://man.openbsd.org/sshd.8)[[21]](https://developers.yubico.com/SSH/Securing_SSH_with_FIDO2.html) | per-use touch |
| GitHub API | fine-grained PAT, one repo, `contents: write` only — or ghtkn App token [[14]](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)[[16]](https://github.com/suzuki-shunsuke/ghtkn) | ≤ 8 h, or shortest expiry you'll tolerate |
| Git over HTTPS | `git-credential-oauth` + `cache` with a timeout [[11]](https://github.com/hickford/git-credential-oauth) | hours |
| AWS | `aws sso` / Identity Center; no `~/.aws/credentials` [[25]](https://www.rhythmictech.com/blog/iam-access-keys-bad-aws-sso-good/) | session |
| App secrets, `.env` | secret manager, `op run` / `bws run --no-inherit-env` [[22]](https://www.1password.dev/cli/secrets-environment-variables/)[[23]](https://bitwarden.com/help/secrets-manager-cli/) | process lifetime |
| npm publish | trusted publishing (OIDC) from CI; nothing in `~/.npmrc` [[17]](https://docs.npmjs.com/trusted-publishers/) | per job |
| Claude auth | `CLAUDE_CONFIG_DIR` per identity; `apiKeyHelper` if vault-backed [[2]](https://code.claude.com/docs/en/authentication) | 5-min refresh |
| Everything else | not on the box | — |

Plus, in one line each: deny-read globs on the paths in §1 [[27]](https://code.claude.com/docs/en/permissions); no `ForwardAgent` [[19]](https://docs.ssh-mitm.at/user_guide/sshagent.html); `OTEL_LOG_*` left at their redacted defaults [[12]](https://code.claude.com/docs/en/monitoring-usage); Gitleaks in `.pre-commit-config.yaml` [[28]](https://github.com/gitleaks/gitleaks); push protection on [[31]](https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection).

The test for this layout: if the agent's process is fully compromised at 03:00, what does the attacker hold at 04:00? With the table above — one repo's contents, for under an hour, with no signing key. With a default `$HOME`, everything in §1, indefinitely.
