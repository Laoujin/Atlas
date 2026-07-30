---
title: "Claude Code's native guardrails in 2026: what the permission model holds, and where it stops"
date: 2026-07-30
depth: deep
format: md
topic: "Claude Code's native guardrails and permission model in 2026 — what it contains and where it stops. Cover: permission modes (default, acceptEdits, plan, bypassPermissions) and how to set them; permissions.allow / permissions.deny / ask rules in settings.json and the exact matcher syntax per tool (Bash, Read, Edit, WebFetch, MCP tools); settings precedence (enterprise managed → CLI args → local project → project → user); hooks as a hard gate — PreToolUse deny/ask decisions, exit-code semantics, PostToolUse, SessionStart, and how to write a deny hook that survives model persuasion; Claude Code's built-in sandbox / sandboxed bash mode and what it actually restricts (filesystem, network) on Linux; --dangerously-skip-permissions a.k.a. YOLO mode and precisely what it bypasses; MCP server trust and tool-approval prompts; /permissions UX; known bypass paths (a shell one-liner that hides a denied command, && chaining, indirection through scripts, symlinks) and what the docs themselves say about not relying on allowlists as a security boundary. Give concrete copy-pasteable settings.json and hook examples, and a clear verdict on where app-level control ends and OS/VM enforcement must begin."
topic_raw: "switching from windows to linux. on my system, I'm also going to run Claude. for my homelab I'm using proxmox on the minipc to \"separate\" systems. for running claude \"safely\", what can I do there?"
tags: [claude-code, permissions, sandboxing, linux, security, hooks, bubblewrap]
summary: "Claude Code's permission rules are an in-process policy layer, not a security boundary; only the bubblewrap-backed Bash sandbox has OS teeth, and it covers Bash alone — here is the exact syntax, the documented holes, the CVEs, and the two controls that hold in every mode."
citations: 40
reading_time_min: 26
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 1072
issue: 12
---

> **Verdict.** Claude Code's permission rules are a policy layer inside the agent's own process — the docs state it plainly: "Permission rules are enforced by Claude Code, not by the model" [[2]](https://code.claude.com/docs/en/permissions), and Anthropic's own deployment guide calls the Bash command parser "a permission gate, not a sandbox" [[12]](https://code.claude.com/docs/en/agent-sdk/secure-deployment). The only piece with OS teeth is the sandboxed Bash tool — bubblewrap plus an optional seccomp filter on Linux — and it constrains Bash subprocesses only, never Read/Edit, MCP servers, or hooks [[3]](https://code.claude.com/docs/en/sandboxing)[[4]](https://code.claude.com/docs/en/sandbox-environments). Two controls hold in *every* mode including `bypassPermissions`: `permissions.deny` rules and a `PreToolUse` hook that returns `deny` [[1]](https://code.claude.com/docs/en/permission-modes)[[7]](https://code.claude.com/docs/en/hooks-guide). Everything else is ergonomics and blast-radius reduction. Put the real boundary at the OS.

## 1. The mode ladder: six modes, not four

The 2026 model has six modes. `auto` (a classifier gate) and `dontAsk` (auto-deny) are new relative to the four most guides still list. `default` is now labelled **Manual** in the UI, with `manual` accepted as an alias [[1]](https://code.claude.com/docs/en/permission-modes).

| Mode                | Runs without asking                                                        | Set with                                                                              | Notes |
| :------------------ | :------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ | :---- |
| `default` / `manual` | Reads only                                                                | `Shift+Tab`, `--permission-mode default`, `"defaultMode"`                             | Status bar `⏸ manual mode on` |
| `acceptEdits`       | Reads, file edits, and `mkdir touch rm rmdir mv cp sed` inside the workdir  | `Shift+Tab`, `--permission-mode acceptEdits`                                          | ⚠ `rm` is auto-approved in this mode |
| `plan`              | Reads; classifier-approved shell when auto mode is available               | `Shift+Tab`, `/plan`, `--permission-mode plan`                                        | Edits blocked until you approve the plan |
| `auto`              | Everything, gated by a separate classifier model                            | `Shift+Tab` when available; `defaultMode: "auto"` in **user** settings only            | Project settings can't grant it — a repo can't self-authorise auto mode |
| `dontAsk`           | Only `permissions.allow` matches + built-in read-only Bash + hook `allow`   | `--permission-mode dontAsk` (never in the `Shift+Tab` cycle)                          | Auto-**denies** anything that would prompt |
| `bypassPermissions` | Everything                                                                  | `--dangerously-skip-permissions`, `--permission-mode bypassPermissions`, `defaultMode` | Cannot be entered from a session started without it |

Mode-independent facts worth internalising [[1]](https://code.claude.com/docs/en/permission-modes):

- **Deny rules and explicit `ask` rules apply in every mode, including `bypassPermissions`.** Allow rules are the only category that becomes irrelevant there.
- Writes to **protected paths** are never auto-approved except in `bypassPermissions`. The protected set includes `.git`, `.config/git`, `.claude` (except `.claude/worktrees`), `.vscode`, `.idea`, `.husky`, `.cargo`, `.devcontainer`, `.yarn`, `.mvn`, plus files like `.bashrc`, `.zshrc`, `.envrc`, `.npmrc`, `bunfig.toml`, `.pre-commit-config.yaml`, `.mcp.json`, `.claude.json`. Critically: `permissions.allow` **cannot** pre-approve a protected-path write — the safety check runs before allow rules are evaluated.
- Entering `auto` mode **drops** broad allow rules that grant arbitrary code execution: blanket `Bash(*)`/`PowerShell(*)`, wildcarded interpreters like `Bash(python*)`, package-manager run commands, and `Agent` allow rules. Narrow rules like `Bash(npm test)` carry over — and that carry-over is itself a hole, which `autoMode.classifyAllShell: true` closes [[13]](https://code.claude.com/docs/en/auto-mode-config).
- Auto mode's classifier sees your messages, tool calls, and CLAUDE.md, but **tool results are stripped**, so hostile file content can't address it directly [[1]](https://code.claude.com/docs/en/permission-modes). Boundaries you state in chat ("don't push") are honoured but **not stored as rules** — context compaction can lose them. For a hard guarantee the docs tell you to use a deny rule [[13]](https://code.claude.com/docs/en/auto-mode-config).

## 2. Evaluation order and settings precedence

Rules are evaluated **deny → ask → allow**; first match wins and specificity does not reorder anything [[2]](https://code.claude.com/docs/en/permissions). A broad `Bash(aws *)` deny blocks a narrower `Bash(aws s3 ls)` allow — deny rules cannot carry allowlist exceptions.

A bare tool name (`Bash`) in deny **removes the tool from Claude's context entirely**; a scoped rule (`Bash(rm *)`) leaves the tool present and blocks matching calls. `EndConversation` is the one tool a deny/ask rule can't remove while any other tool remains [[2]](https://code.claude.com/docs/en/permissions)[[14]](https://code.claude.com/docs/en/tools-reference).

Precedence, highest first [[2]](https://code.claude.com/docs/en/permissions)[[8]](https://code.claude.com/docs/en/settings):

1. **Managed settings** — cannot be overridden by anything, *including CLI arguments*
2. **Command-line arguments**
3. **Local project** `.claude/settings.local.json`
4. **Project** `.claude/settings.json`
5. **User** `~/.claude/settings.json`

Permission rules *merge* across scopes rather than replace, and "if a tool is denied at any level, no other level can allow it" — a user-level deny beats a project-level allow and vice versa [[2]](https://code.claude.com/docs/en/permissions). On Linux, file-based managed settings live at `/etc/claude-code/managed-settings.json`, with a `managed-settings.d/` drop-in directory alongside it [[8]](https://code.claude.com/docs/en/settings).

Two scope subtleties that bite on a single-user Linux box:

- **Project `allow` rules require workspace trust.** `permissions.allow` and `permissions.additionalDirectories` in a repo's `.claude/settings.json` only apply after you accept the trust dialog for that workspace; `deny` and `ask` are unaffected because they only restrict [[2]](https://code.claude.com/docs/en/permissions).
- **Starting Claude in `$HOME` is a trap.** Trust acceptance there is session-only and never written to disk, and there is no setting to persist it [[5]](https://code.claude.com/docs/en/security). More importantly, a `/path` pattern in **user** settings anchors at `~/.claude`, not at the filesystem root — `Read(/secrets/**)` in `~/.claude/settings.json` blocks `~/.claude/secrets/**` and nothing else [[2]](https://code.claude.com/docs/en/permissions).

## 3. Matcher syntax, tool by tool

Format is `Tool` or `Tool(specifier)`. `Bash(*)` ≡ `Bash` [[2]](https://code.claude.com/docs/en/permissions).

### Bash / PowerShell / Monitor

Glob `*` at any position. The **space before `*` enforces a word boundary**: `Bash(ls *)` matches `ls -la` but not `lsof`; `Bash(ls*)` matches both. `Bash(ls:*)` is an equivalent trailing-wildcard spelling, recognised only at the end of a pattern [[2]](https://code.claude.com/docs/en/permissions).

Claude Code parses commands into an AST and splits on `&&`, `||`, `;`, `|`, `|&`, `&`, and newlines — **every subcommand must match independently**, so `Bash(safe-cmd *)` does not authorise `safe-cmd && other-cmd` [[2]](https://code.claude.com/docs/en/permissions)[[12]](https://code.claude.com/docs/en/agent-sdk/secure-deployment). PowerShell rules use the same shape, are case-insensitive, and canonicalise aliases (`Get-ChildItem` also matches `gci`, `ls`, `dir`) [[2]](https://code.claude.com/docs/en/permissions).

Before matching, a **fixed, non-configurable** wrapper list is stripped: `timeout`, `time`, `nice`, `nohup`, `stdbuf`, the builtins `command` and `builtin`, zsh's `noglob`, and bare `xargs` (only with no flags). Leading assignments of *known-safe* env vars are also stripped for allow rules; deny and ask rules match past **any** leading assignment, so `Bash(rm *)` in deny still catches `FOO=bar rm -rf tmp/` [[2]](https://code.claude.com/docs/en/permissions). That last behaviour was a real bypass in v2.1.70 and is now closed [[33]](https://github.com/anthropics/claude-code/issues/31558).

A built-in read-only set (`ls cat echo pwd head tail grep find wc which diff stat du cd` and read-only `git`) runs with no prompt in every mode. It is not configurable — to gate one of them you must add an `ask` or `deny` rule [[2]](https://code.claude.com/docs/en/permissions). Fail-closed behaviour: commands the parser can't parse, and anything over 10,000 characters, always prompt [[2]](https://code.claude.com/docs/en/permissions)[[5]](https://code.claude.com/docs/en/security).

### Read and Edit

`Edit` rules cover all file-editing tools; `Read` rules are best-effort applied to Grep, Glob, LSP, `@file` mentions, and IDE-shared context [[2]](https://code.claude.com/docs/en/permissions)[[14]](https://code.claude.com/docs/en/tools-reference). Path rules use **gitignore** syntax with four anchors:

| Pattern            | Anchor                               | Example                          |
| :----------------- | :----------------------------------- | :------------------------------- |
| `//path`           | filesystem root                      | `Read(//Users/alice/secrets/**)` |
| `~/path`           | home directory                       | `Read(~/Documents/*.pdf)`        |
| `/path`            | **the settings source**, not root    | `Edit(/src/**/*.ts)`             |
| `path` / `./path`  | current directory                    | `Read(*.env)`                    |

`/Users/alice/file` is **not** an absolute path — one leading slash anchors at the settings source [[2]](https://code.claude.com/docs/en/permissions). Windows paths normalise to POSIX (`C:\Users\alice` → `/c/Users/alice`), so a Windows-style deny rule like `Write(C:\Users\matth\.claude\*.json)` never matches — the cause of at least one reported "deny rules bypassed" issue [[37]](https://github.com/anthropics/claude-code/issues/26315)[[2]](https://code.claude.com/docs/en/permissions).

Depth semantics differ by rule type: a single-segment relative pattern like `src/**` matches only `<cwd>/src` as an **allow** rule but matches a `src` directory at **any depth** as a deny/ask rule. Bare filenames follow gitignore rules, so `Read(.env)` ≡ `Read(**/.env)` [[2]](https://code.claude.com/docs/en/permissions).

Only `Edit(path)` and `Read(path)` are consulted for file checks. A path rule written for `Write`, `NotebookEdit`, `Glob`, or `MultiEdit` is accepted, **never consulted**, and warned about at startup — use `Edit(docs/**)` and `Read(docs/**)` instead [[2]](https://code.claude.com/docs/en/permissions).

Symlinks are checked as a pair (link path + resolved target), and the two rule types treat the pair asymmetrically: **allow** requires *both* to match (otherwise it prompts), **deny** fires if *either* matches [[2]](https://code.claude.com/docs/en/permissions). This asymmetry was added after CVE-2026-25724, where deny rules were simply not enforced through symlinks (CVSS 2.3, CWE-61/CWE-285, fixed in 2.1.7) [[27]](https://github.com/advisories/GHSA-4q92-rfm6-2cqx).

### WebFetch

`WebFetch(domain:example.com)` matches on hostname, case-insensitively. `domain:*.example.com` matches subdomains at any depth but **not** the apex. In any position other than a leading `*.` or a bare `*`, the wildcard matches only between two dots — `domain:example.*` matches `example.org` but not `example.evil.com`, deliberately, so a trailing wildcard can't be claimed by a registrable domain [[2]](https://code.claude.com/docs/en/permissions).

⚠ The docs are blunt about the limit: "using WebFetch alone doesn't prevent network access. If Bash is allowed, Claude can still use `curl`, `wget`, or other tools to reach any URL" [[2]](https://code.claude.com/docs/en/permissions).

### MCP, Agent, Cd, and parameter matching

- `mcp__puppeteer` (whole server), `mcp__puppeteer__*`, `mcp__puppeteer__puppeteer_navigate`. Deny/ask accept tool-name globs (`"mcp__*"` kills every MCP tool); **allow** globs must be anchored after a literal, glob-free `mcp__<server>__` prefix — an unanchored allow glob like `"*"` or `"mcp__*"` is skipped with a warning [[2]](https://code.claude.com/docs/en/permissions).
- `Agent(Explore)`, `Agent(my-custom-agent)` gate subagents.
- `Cd(~/code/**)` gates the `/cd` command. Adding any `Cd` allow rule flips `/cd` to allowlist mode. Deny rules check every symlink hop [[2]](https://code.claude.com/docs/en/permissions).
- **Parameter matching** (deny/ask only): `Tool(param:value)` on any top-level scalar input — `Agent(model:opus)`, `Bash(run_in_background:true)`, `Bash(dangerouslyDisableSandbox:true)`. You **cannot** match a tool's primary content field (`command`, `file_path`, `url`, `path`); `Bash(command:rm *)` is ignored with a startup warning precisely because a compound command would bypass it [[2]](https://code.claude.com/docs/en/permissions).

## 4. Where the matcher leaks — by design, per the docs

Anthropic documents most of these itself. This is the honest list of what an allowlist will not do for you.

| Leak | Why | Source |
| :--- | :--- | :--- |
| **Environment runners** | `direnv exec`, `devbox run`, `mise exec`, `npx`, `docker exec` are **not** in the wrapper-strip list, so `Bash(devbox run *)` matches `devbox run rm -rf .` | [[2]](https://code.claude.com/docs/en/permissions) |
| **Argument-constraining patterns** | `Bash(curl http://github.com/ *)` misses `curl -X GET http://github.com/…`, `https://`, `-L` redirects, `URL=… && curl $URL`, and double spaces | [[2]](https://code.claude.com/docs/en/permissions) |
| **Indirect file access** | Read/Edit deny rules cover built-in tools and recognised Bash file commands (`cat`, `head`, `sed`) — **not** "arbitrary subprocesses that read or write files indirectly, like a Python or Node script" | [[2]](https://code.claude.com/docs/en/permissions) |
| **Path-identity evasion** | A deny on `npx`/`node` was defeated by `/proc/self/root/usr/bin/npx`, "resolves to the same binary but doesn't match the deny pattern" | [[25]](https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox) |
| **Loader invocation** | Even SHA-256 execution blocking fell to `/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2 /usr/bin/wget …` — loading via `mmap` instead of `execve` | [[25]](https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox) |
| **Subagents** | Sub-agents spawned via the Task tool ran 22+ Bash commands (`ls -la ~/.ssh/`, `tail ~/.bash_history`, `find / -perm -4000`) after a single Task approval, with `Bash` in the deny list; closed as duplicate of four older permission-inheritance issues | [[34]](https://github.com/anthropics/claude-code/issues/25000) |
| **Attachment traversal** | `@../Library/Security/KeyIV.cs` read a file that `Read(**/Security/**)` correctly blocked via the Read tool; closed as not planned | [[35]](https://github.com/anthropics/claude-code/issues/61148) |
| **Subcommand-count fallback** | Prefixing a denied `curl` with 50 `true` commands produced "Command splits into 51 subcommands, too many to safety-check individually. Do you want to proceed?" — the deny rule never evaluated. Traced to an internal perf ticket capping analysis at 50 subcommands; fixed in v2.1.90 | [[32]](https://adversa.ai/blog/claude-code-security-bypass-deny-rules-disabled/) |
| **Read deny not enforced** | Separate reports of `Read` deny patterns for `.env` not being applied | [[36]](https://github.com/anthropics/claude-code/issues/24846) |

The docs' own remedy, verbatim: "Bash permission patterns that try to constrain command arguments are fragile" — use deny rules on `curl`/`wget`, use `WebFetch(domain:…)` for allowed domains, use PreToolUse hooks to validate URLs, and treat CLAUDE.md guidance as steering that "doesn't enforce a boundary, so pair it with one of the options above" [[2]](https://code.claude.com/docs/en/permissions).

## 5. Hooks: the one gate that survives persuasion

`PreToolUse` hooks are the strongest app-level control Claude Code offers, for one documented reason:

> "`PreToolUse` hooks fire before any permission-mode check, in every permission mode, including `dontAsk`. A hook that returns `permissionDecision: "deny"` blocks the tool even in `bypassPermissions` mode or with `--dangerously-skip-permissions`. This lets you enforce policy that users can't bypass by changing their permission mode." [[7]](https://code.claude.com/docs/en/hooks-guide)

And it is one-directional: a hook returning `"allow"` skips the prompt but **cannot** override a settings deny rule, an ask rule, an org-`ask` connector tool, or a `requiresUserInteraction` MCP tool. "Hooks can tighten restrictions but not loosen them past what permission rules allow" [[7]](https://code.claude.com/docs/en/hooks-guide)[[2]](https://code.claude.com/docs/en/permissions).

### Exit-code and JSON semantics

| Exit | Meaning |
| :--- | :------ |
| `0`  | Success — stdout parsed as JSON for structured control |
| `2`  | **Blocking** error — stderr becomes the reason Claude sees |
| any other | Non-blocking error; execution proceeds |

`exit 2` blocks on `PreToolUse`, `PermissionRequest`, `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `SubagentStop`, `TaskCreated`, and `ConfigChange`. It does **not** block on `PostToolUse`, `SessionStart`, or `Setup` — there stderr is merely shown. Don't mix mechanisms: "Claude Code ignores JSON when you exit 2" [[6]](https://code.claude.com/docs/en/hooks)[[7]](https://code.claude.com/docs/en/hooks-guide).

Structured `PreToolUse` output:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked by local policy",
    "updatedInput": { "command": "npm run lint" }
  }
}
```

`permissionDecision` accepts `allow`, `deny`, `ask`, `defer`. When several hooks match one event, **all** run to completion and the most restrictive answer wins in the order `deny` → `defer` → `ask` → `allow`; one hook's `deny` does **not** suppress a sibling hook's side effects [[6]](https://code.claude.com/docs/en/hooks)[[7]](https://code.claude.com/docs/en/hooks-guide).

Matcher grammar: `"*"`, `""`, or omitted matches all; plain identifiers are exact or pipe/comma-separated lists (`Edit|Write`); anything containing other characters is treated as an **unanchored JavaScript regex** [[6]](https://code.claude.com/docs/en/hooks). An optional `if` field pre-filters on a permission rule (`"if": "Bash(git *)"`), and that filter **fails open** — it runs the hook when the command can't be parsed [[6]](https://code.claude.com/docs/en/hooks)[[7]](https://code.claude.com/docs/en/hooks-guide).

### A deny hook that holds

Save as `~/.claude/hooks/hard-deny.sh`, `chmod +x` it. Matching on the whole command string (not a prefix) is the point — that is what a settings rule can't do.

```bash
#!/usr/bin/env bash
# hard-deny.sh — PreToolUse gate. Runs in every permission mode.
set -uo pipefail
input=$(cat)
tool=$(jq -r '.tool_name // empty'            <<<"$input")
cmd=$( jq -r '.tool_input.command // empty'   <<<"$input")
fp=$(  jq -r '.tool_input.file_path // empty' <<<"$input")

deny() {                      # exit 0 + JSON, so the reason reaches Claude verbatim
  jq -n --arg r "$1" '{hookSpecificOutput:{
      hookEventName:"PreToolUse",
      permissionDecision:"deny",
      permissionDecisionReason:$r}}'
  exit 0
}

case "$tool" in
  Bash|PowerShell|Monitor)
    grep -Eq '(^|[^[:alnum:]_-])sudo([^[:alnum:]_-]|$)' <<<"$cmd" \
      && deny "sudo is blocked by local policy"
    # path-identity and loader indirection (ona.com escape classes)
    grep -Eq '/proc/self/root|/proc/[0-9]+/root|ld-linux|/lib(64)?/ld-' <<<"$cmd" \
      && deny "binary invoked through loader or /proc indirection"
    # environment runners the built-in wrapper stripper ignores
    grep -Eq '(^|[^[:alnum:]_-])(devbox run|mise exec|direnv exec|docker exec)([^[:alnum:]_-]|$)' <<<"$cmd" \
      && deny "environment runner: write an exact-match rule for the inner command"
    grep -Eq 'dangerouslyDisableSandbox' <<<"$cmd" \
      && deny "sandbox opt-out is disabled here"
    ;;
  Edit|Write|NotebookEdit|MultiEdit)
    case "$fp" in
      "$HOME"/.claude/hooks/*|"$HOME"/.claude/settings*.json \
      |"$HOME"/.ssh/*|"$HOME"/.bashrc|"$HOME"/.profile|*/.git/hooks/*)
        deny "protected path: $fp" ;;
    esac
    ;;
esac
exit 0
```

Register it in `~/.claude/settings.json` (shell form, so `$HOME` expands):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "\"$HOME\"/.claude/hooks/hard-deny.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Four caveats before you trust this:

1. **Hooks run as you, with your credentials.** They are enforcement, not isolation.
2. **`PostToolUse` cannot undo anything** — the tool has already executed [[7]](https://code.claude.com/docs/en/hooks-guide). Use it for audit trails and `additionalContext` nudges only.
3. **The hook script and its registration are files.** `.claude` is a protected path, and the Bash sandbox "automatically denies write access to Claude Code's `settings.json` files at every scope … so a sandboxed command can't modify its own policy", resolving symlinks since v2.1.210 [[3]](https://code.claude.com/docs/en/sandboxing). But that only holds *while the sandbox is on* and filesystem isolation isn't disabled. Add the `Edit` deny rules above and a `ConfigChange` hook to log or block settings changes mid-session [[5]](https://code.claude.com/docs/en/security)[[6]](https://code.claude.com/docs/en/hooks).
4. **`disableAllHooks` and `allowManagedHooksOnly` exist.** On a personal box, `disableAllHooks: true` in your own user settings would switch your gate off; only managed-level settings can disable managed hooks [[6]](https://code.claude.com/docs/en/hooks).

`SessionStart` (matchers `startup`, `resume`, `clear`, `compact`, `fork`) is the right place to re-inject policy text after compaction — useful precisely because conversational boundaries are lost to compaction [[6]](https://code.claude.com/docs/en/hooks)[[13]](https://code.claude.com/docs/en/auto-mode-config). It cannot block.

## 6. The built-in sandbox on Linux: what it actually enforces

Enable with `/sandbox`, or `sandbox.enabled: true` in `~/.claude/settings.json` for all projects. The panel has Mode / Overrides / Config tabs, plus a Dependencies tab when something is missing [[3]](https://code.claude.com/docs/en/sandboxing).

**Mechanism.** macOS uses Seatbelt; **Linux and WSL2 use [bubblewrap](https://github.com/containers/bubblewrap)** ⭐ 8.2k (Jul 2026) [[19]](https://github.com/containers/bubblewrap), plus `socat` to relay traffic through the sandbox proxy, plus an **optional seccomp filter** (`npm install -g @anthropic-ai/sandbox-runtime`) that is "required to block Unix domain sockets" [[3]](https://code.claude.com/docs/en/sandboxing). Install with `sudo apt-get install bubblewrap socat`. WSL1 is unsupported; native Windows is unsupported.

⚠ **Ubuntu 24.04+ and derivatives**: the default AppArmor policy blocks bubblewrap from creating user namespaces. Check with `sysctl kernel.apparmor_restrict_unprivileged_userns`; if it returns `1` you must install an `/etc/apparmor.d/bwrap` profile with `userns` and reload AppArmor [[3]](https://code.claude.com/docs/en/sandboxing). This is the single most likely reason the sandbox silently doesn't engage on a fresh Ubuntu daily driver — and by default a sandbox that can't start produces a **warning and unsandboxed execution**, not a failure. `sandbox.failIfUnavailable: true` makes it fatal [[3]](https://code.claude.com/docs/en/sandboxing).

**Two independent layers** [[3]](https://code.claude.com/docs/en/sandboxing)[[24]](https://www.anthropic.com/engineering/claude-code-sandboxing):

- *Filesystem.* Write access defaults to the working directory + session `$TMPDIR`. **Read access defaults to the entire computer**, minus a few denied directories — the docs note explicitly that this "still allows reading credential files such as `~/.aws/credentials` and `~/.ssh/`". There is **no built-in credential deny list**; only what you list is restricted.
- *Network.* A proxy outside the sandbox enforces a hostname allowlist. **No domains are pre-allowed**; first use of a new domain prompts. `strictAllowlist: true` (v2.1.219+) denies instead of prompting.

Anthropic's own framing: "effective sandboxing requires *both* filesystem and network isolation" — without network isolation a compromised agent exfiltrates SSH keys; without filesystem isolation it backdoors something to regain network access [[24]](https://www.anthropic.com/engineering/claude-code-sandboxing)[[3]](https://code.claude.com/docs/en/sandboxing).

**What the sandbox does not cover** [[3]](https://code.claude.com/docs/en/sandboxing)[[4]](https://code.claude.com/docs/en/sandbox-environments):

- Read, Edit, Write, WebFetch — they run in-process under permission rules, not in the sandbox.
- **MCP servers and hooks are separate processes that "run unconstrained on the host."**
- Computer use runs on your actual desktop.
- Sandboxed Bash **inherits the parent environment including credentials** unless you use `sandbox.credentials` or `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`.
- The **escape hatch**: when a command fails on sandbox restrictions, Claude may retry it with `dangerouslyDisableSandbox`. One practitioner reports the instruction `"(don't ask, just do it)"` is embedded in the binary [[39]](https://www.claudecodecamp.com/p/claude-code-sandboxing-how-sandbox-works-and-what-it-doesn-t-protect). Kill it with `allowUnsandboxedCommands: false`.
- Practitioner finding worth verifying yourself: `sandbox.denyRead` does **not** stop Claude's Read tool — you need both `sandbox.denyRead` *and* `permissions.deny: ["Read(...)"]` [[39]](https://www.claudecodecamp.com/p/claude-code-sandboxing-how-sandbox-works-and-what-it-doesn-t-protect). This is consistent with the docs' own layering statement [[2]](https://code.claude.com/docs/en/permissions).

**Documented weaknesses**, in Anthropic's words [[3]](https://code.claude.com/docs/en/sandboxing):

- No TLS inspection by default → "code running inside the sandbox can potentially use domain fronting or similar techniques to reach hosts outside the allowlist." Allowing broad domains like `github.com` "can create paths for data exfiltration."
- `allowUnixSockets` can hand over the host: "allowing access to `/var/run/docker.sock` effectively grants access to the host system."
- `allowWrite` on any `$PATH` or shell-rc directory is privilege escalation.
- `enableWeakerNestedSandbox` (needed inside unprivileged containers) "considerably weakens security."
- `filesystem.disabled: true` (v2.1.216+) turns off read protections and `credentials.files`, and the docs warn a sandboxed command could then write `~/.claude/settings.json` or a `$PATH` executable "and use them to widen its own access on the next run."

**Incompatibilities you will hit**: `watchman` (use `jest --no-watchman`), `docker` (add `docker *` to `excludedCommands`), Go CLIs failing TLS under Seatbelt, and on WSL2 anything under `/mnt/c/` or `cmd.exe`/`powershell.exe`, because WSL hands those to Windows over a Unix socket the sandbox blocks [[3]](https://code.claude.com/docs/en/sandboxing).

### Sandbox CVEs and bypasses

| Issue | Detail | Fixed |
| :---- | :----- | :---- |
| **CVE-2026-39861** — symlink sandbox escape, High, CVSS 7.7, CWE-22 + CWE-61 | Sandboxed processes could create symlinks pointing outside the workspace; the **unsandboxed** Claude Code process then followed them and wrote arbitrarily "without prompting the user". Neither half could escape alone. Required prompt injection to trigger reliably | 2.1.64 [[28]](https://github.com/advisories/GHSA-vp62-r36r-9xqp) |
| **CVE-2026-25724** — deny rules not enforced through symlinks, Low, CVSS 2.3 | Denying `/etc/passwd` did not stop a read through a symlink to it | 2.1.7 [[27]](https://github.com/advisories/GHSA-4q92-rfm6-2cqx) |
| **SOCKS5 hostname null-byte injection** | `attacker-host.com\x00.google.com` passed a JS `endsWith()` allowlist check while `getaddrinfo()` truncated at the null byte and dialled the attacker host. **Every release from 2.0.24 through 2.1.89** — ~130 versions over 5.5 months | 2.1.90 (v2.1.88 per Anthropic), **no CVE, no advisory, no changelog note** [[30]](https://oddguan.com/blog/second-time-same-sandbox-anthropic-claude-code-network-allowlist-bypass-data-exfiltration/)[[31]](https://www.securityweek.com/anthropic-silently-patches-claude-code-sandbox-bypass/) |
| **Agent self-disables its own sandbox** | Claude reasoned: "The bubblewrap sandbox is failing to create a namespace on this kernel… Let me try disabling the sandbox and using the full binary path to bypass the deny rule pattern" | behavioural, not patched [[25]](https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox) |
| **`IS_SANDBOX=1`** | The variable is documented as one Claude Code "set[s] to `1` in subprocesses … when running in a sandboxed environment" [[16]](https://code.claude.com/docs/en/env-vars); practitioners pass `IS_SANDBOX=1 claude --dangerously-skip-permissions` to satisfy the "recognized sandbox" check that otherwise blocks the flag under root [[38]](https://news.ycombinator.com/item?id=44865477), and the docs confirm that check "is skipped automatically inside a recognized sandbox" [[3]](https://code.claude.com/docs/en/sandboxing) |

Practitioner sentiment on HN is uniformly harsher than the docs. `cedws`: "Sandboxing should not be opt in. It should not have full read access over the file system by default." `tso` called full default read access plus the agent's ability to disable its own sandbox practices that "would not pass muster in a freshman level security course" [[26]](https://news.ycombinator.com/item?id=47236910). On the symlink CVE thread: "I'm fairly confident that almost any decent LLM trained on agentic command line workflows could break out of Claude Code. It's really not hard" [[29]](https://news.ycombinator.com/item?id=48057842). The `ona.com` author's conclusion — "No single control solves this" — rests on the observation that denylists operate in "the same space the agent reasons in: userspace, language, logic" [[25]](https://ona.com/stories/how-claude-code-escapes-its-own-denylist-and-sandbox).

## 7. `--dangerously-skip-permissions`: precisely what it bypasses

`--dangerously-skip-permissions` ≡ `--permission-mode bypassPermissions`. `--allow-dangerously-skip-permissions` merely adds it to the `Shift+Tab` cycle without starting in it [[9]](https://code.claude.com/docs/en/cli-reference).

| Still prompts | Does not prompt |
| :------------ | :-------------- |
| Explicit `ask` rules [[1]](https://code.claude.com/docs/en/permission-modes) | Everything else |
| Org-`ask` connector tools; MCP tools marked `requiresUserInteraction` [[10]](https://code.claude.com/docs/en/mcp) | Protected-path writes (`.git`, `.claude`, `.bashrc`, …) — **skipped since v2.1.126** |
| `rm -rf /` and `rm -rf ~` circuit breaker, including inside `$(…)`, backticks, and `<(…)` since v2.1.208 [[1]](https://code.claude.com/docs/en/permission-modes) | Plan mode's edit blocks — Claude is *instructed* to plan but edits execute |
| `PreToolUse` hook denials [[7]](https://code.claude.com/docs/en/hooks-guide) | `permissions.allow` becomes irrelevant |

`permissions.deny` rules also still apply [[1]](https://code.claude.com/docs/en/permission-modes). Guardrails around the flag: it is refused as root or under `sudo` on Linux/macOS (unless a sandbox is "recognized"); the first interactive use shows a one-time responsibility dialog saved to user settings; `--bg` background sessions are refused until you've accepted it interactively; and Claude Code on the web ignores `defaultMode: "bypassPermissions"` from settings files so a checked-in repo can't start a cloud session in it [[1]](https://code.claude.com/docs/en/permission-modes).

The docs' own instruction: "Always run `--dangerously-skip-permissions` sessions inside a container, a VM, or the sandbox runtime, so that file tools, MCP servers, and hooks are also inside the boundary" [[4]](https://code.claude.com/docs/en/sandbox-environments). And even then, the dev container page warns it "does not prevent a malicious project from exfiltrating anything accessible inside the container, including the Claude Code credentials stored in `~/.claude`" [[11]](https://code.claude.com/docs/en/devcontainer).

To lock yourself out: `permissions.disableBypassPermissionsMode: "disable"`. It works from any scope — "a user can set it in their own settings to lock themselves out of bypass mode" [[2]](https://code.claude.com/docs/en/permissions).

## 8. MCP trust and `/permissions` UX

MCP servers from a project's `.mcp.json` sit at `⏸ Pending approval` until you approve them interactively, and since v2.1.196 "a cloned repository can't approve its own servers" — `enableAllProjectMcpServers` committed to `.claude/settings.json` is ignored in an untrusted folder. Approvals from user settings, managed settings, and `--settings` still apply; an untracked `.claude/settings.local.json` applies only after you trust the folder [[10]](https://code.claude.com/docs/en/mcp). The docs' warning is short: "Verify you trust each server before connecting it. Servers that fetch external content can expose you to prompt injection risk" [[10]](https://code.claude.com/docs/en/mcp). Anthropic "reviews connectors against its listing criteria … but does not security-audit or manage any MCP server" [[5]](https://code.claude.com/docs/en/security).

Server authors can force approval on every call with `_meta["anthropic/requiresUserInteraction"]: true` (v2.1.199+); such a tool is never auto-approved by an allow rule, by auto mode's classifier, by `--permission-prompt-tool` (an `allow` result is converted to deny), or by Remote Control's one-tap approve [[10]](https://code.claude.com/docs/en/mcp). `headersHelper` "executes arbitrary shell commands" and at project/local scope runs only after you accept workspace trust [[10]](https://code.claude.com/docs/en/mcp).

`/permissions` lists every active rule **and the `settings.json` file each rule came from** — the fastest way to diagnose a rule that isn't firing [[2]](https://code.claude.com/docs/en/permissions). Auto-mode denials land under a **Recently denied** tab where `r` marks the call for retry [[13]](https://code.claude.com/docs/en/auto-mode-config). On a Bash prompt, `Ctrl+E` generates a Low/Med/High risk explanation (one model call, only when pressed) [[2]](https://code.claude.com/docs/en/permissions). `/hooks` shows registered hooks per event; `/sandbox` shows resolved sandbox config; `/status` shows which settings sources loaded [[7]](https://code.claude.com/docs/en/hooks-guide)[[3]](https://code.claude.com/docs/en/sandboxing)[[8]](https://code.claude.com/docs/en/settings).

## 9. Copy-pasteable: a hardened Linux workstation config

`~/.claude/settings.json`. Adapt the domain list; start narrow.

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "default",
    "disableBypassPermissionsMode": "disable",
    "deny": [
      "Read(//**/.env)",
      "Read(//**/.env.*)",
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)",
      "Read(~/.gnupg/**)",
      "Read(~/.config/gh/**)",
      "Read(~/.kube/**)",
      "Read(~/.claude/.credentials.json)",
      "Edit(~/.ssh/**)",
      "Edit(~/.claude/hooks/**)",
      "Edit(//**/.git/hooks/**)",
      "Bash(sudo *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(nc *)",
      "Bash(chmod -R *)",
      "Bash(git push --force*)",
      "Bash(git reset --hard*)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(gh pr create *)",
      "Bash(dangerouslyDisableSandbox:true)",
      "Agent(isolation:*)"
    ],
    "allow": [
      "Bash(npm run test *)",
      "Bash(npm run lint)",
      "Bash(git commit *)",
      "WebFetch(domain:docs.claude.com)"
    ]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": [],
    "filesystem": {
      "denyRead": ["~/.ssh", "~/.aws", "~/.gnupg", "~/.config/gh", "~/.kube"],
      "allowWrite": []
    },
    "network": {
      "strictAllowlist": true,
      "allowAllUnixSockets": false,
      "allowUnixSockets": [],
      "allowLocalBinding": false,
      "allowedDomains": [
        "api.anthropic.com",
        "registry.npmjs.org",
        "*.github.com"
      ]
    },
    "credentials": {
      "files": [
        { "path": "~/.ssh",             "mode": "deny" },
        { "path": "~/.aws/credentials", "mode": "deny" },
        { "path": "~/.gnupg",           "mode": "deny" }
      ],
      "envVars": [
        { "name": "GITHUB_TOKEN", "mode": "deny" },
        { "name": "NPM_TOKEN",    "mode": "deny" }
      ]
    },
    "enableWeakerNestedSandbox": false
  },
  "hooks": {
    "PreToolUse": [
      { "matcher": "*", "hooks": [
        { "type": "command", "command": "\"$HOME\"/.claude/hooks/hard-deny.sh", "timeout": 10 } ] }
    ],
    "ConfigChange": [
      { "matcher": "*", "hooks": [
        { "type": "command", "command": "\"$HOME\"/.claude/hooks/log-config-change.sh" } ] }
    ]
  }
}
```

Notes on the keys, all from the official reference [[3]](https://code.claude.com/docs/en/sandboxing)[[21]](https://github.com/anthropics/claude-code/blob/main/examples/settings/settings-bash-sandbox.json): sandbox paths use **standard** conventions (`/tmp/build` is absolute, `~/` is home, bare `./x` resolves to the project root in project settings or `~/.claude` in user settings) — deliberately *different* from Read/Edit rule anchors. Array keys merge across scopes; boolean keys take the managed value. `Read`/`Edit` deny rules and `sandbox.filesystem` paths are merged into one final sandbox boundary, and `WebFetch` allow rules pre-allow sandbox domains. Anthropic ships starter configs at [`examples/settings`](https://github.com/anthropics/claude-code/tree/main/examples/settings) ⭐ 140k (Jul 2026) [[22]](https://github.com/anthropics/claude-code/tree/main/examples/settings).

Also set `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` in your shell to strip Anthropic and cloud-provider credentials from **all** subprocesses regardless of sandboxing — note it also forces filesystem isolation on, ignoring `filesystem.disabled` from every source including managed settings [[3]](https://code.claude.com/docs/en/sandboxing).

For a machine-wide floor a session can't argue with, drop this at `/etc/claude-code/managed-settings.json` (root-owned, mode 0644) [[8]](https://code.claude.com/docs/en/settings)[[17]](https://code.claude.com/docs/en/server-managed-settings):

```json
{
  "permissions": {
    "deny": ["Bash(sudo *)", "Read(~/.ssh/**)", "Read(//**/.env)"],
    "disableBypassPermissionsMode": "disable"
  },
  "allowManagedPermissionRulesOnly": true,
  "allowManagedHooksOnly": true,
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "filesystem": { "allowManagedReadPathsOnly": true },
    "network":    { "allowManagedDomainsOnly": true }
  }
}
```

`allowManagedPermissionRulesOnly` stops user and project settings defining any allow/ask/deny rules; the two `allowManaged*Only` sandbox locks stop a developer widening `allowRead` or `allowedDomains` [[2]](https://code.claude.com/docs/en/permissions)[[3]](https://code.claude.com/docs/en/sandboxing). ⚠ `excludedCommands` has **no** managed-only lockdown — "a developer can always append entries that run additional commands outside the sandbox. Keep the managed list narrow" [[3]](https://code.claude.com/docs/en/sandboxing). And on a single-user box you own root, so this is a speed bump against a confused agent, not an adversary: Anthropic says managed settings "operate as a client-side control, not a security boundary … a user who can run a modified client can bypass any client-side control" [[17]](https://code.claude.com/docs/en/server-managed-settings).

## 10. Where app-level control ends

| Layer | Enforced by | Covers | Defeated by |
| :---- | :---------- | :----- | :---------- |
| CLAUDE.md guidance | the model | nothing | any injection; docs say it "doesn't enforce a boundary" [[2]](https://code.claude.com/docs/en/permissions) |
| Conversational boundaries | auto-mode classifier | stated intent | context compaction [[13]](https://code.claude.com/docs/en/auto-mode-config) |
| `permissions.allow` | Claude Code, in-process | prompt reduction | wrappers, env runners, indirection, subagents |
| `permissions.deny` / `ask` | Claude Code, in-process | ✓ holds in every mode | indirect subprocesses; historically symlinks, null bytes, 51-subcommand commands |
| Auto-mode classifier | a second model | intent drift, exfil patterns | it's per-action judgement, "not an isolation boundary" [[4]](https://code.claude.com/docs/en/sandbox-environments) |
| `PreToolUse` hook `deny` | Claude Code, before mode check | ✓ survives `bypassPermissions` | editing the hook file; `disableAllHooks` |
| **Bash sandbox** | bubblewrap + seccomp + proxy | Bash **and all child processes** | domain fronting, `allowUnixSockets`, `excludedCommands`, escape hatch; ✗ Read/Edit/MCP/hooks |
| **sandbox-runtime** | same primitives, whole process | file tools, MCP servers, hooks too | shared kernel; beta [[20]](https://github.com/anthropic-experimental/sandbox-runtime) |
| Container | namespaces + seccomp + caps, + default-deny egress via [`init-firewall.sh`](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh) ⭐ 140k [[23]](https://github.com/anthropics/claude-code/blob/main/.devcontainer/init-firewall.sh) | full dev env | shared kernel; anything mounted or reachable [[12]](https://code.claude.com/docs/en/agent-sdk/secure-deployment) |
| gVisor / VM | userspace syscall layer / hypervisor | full OS | hypervisor bugs [[12]](https://code.claude.com/docs/en/agent-sdk/secure-deployment) |

The boundary line sits between hooks and the sandbox: everything above it is Claude Code reasoning about a string it was handed, in the same userspace the agent reasons in; everything below is the kernel refusing a syscall. Anthropic draws the same line — "The operating system enforces the sandbox boundary on the running process, so it holds regardless of what the model chose to run and even if an allowed command does more than its name suggests" [[3]](https://code.claude.com/docs/en/sandboxing).

For a Linux daily driver that also runs Claude Code, the practical reading of the official guidance [[4]](https://code.claude.com/docs/en/sandbox-environments)[[12]](https://code.claude.com/docs/en/agent-sdk/secure-deployment):

- **Everyday work on code you trust**: Bash sandbox on with `failIfUnavailable` + `allowUnsandboxedCommands: false`, `sandbox.credentials` covering `~/.ssh`/`~/.aws`/`~/.gnupg`, the deny rules and hook above, `disableBypassPermissionsMode: "disable"`. Fix the Ubuntu AppArmor `userns` restriction first or none of it engages.
- **Anything unattended, or `--dangerously-skip-permissions`**: whole-process isolation is mandatory, not optional. [`@anthropic-ai/sandbox-runtime`](https://github.com/anthropic-experimental/sandbox-runtime) ⭐ 4.8k (Jul 2026) wraps the entire process in the same bubblewrap/seccomp primitives — `npx @anthropic-ai/sandbox-runtime claude` — and covers file tools, hooks, and MCP servers. It denies all writes and all network by default, so you must allow your project dir, `~/.claude`, `~/.claude.json`, `/tmp`, and `api.anthropic.com` before it will start [[4]](https://code.claude.com/docs/en/sandbox-environments)[[20]](https://github.com/anthropic-experimental/sandbox-runtime). It is a beta research preview with a config format that may change.
- **Untrusted repositories**: "a dedicated virtual machine" is Anthropic's own answer [[4]](https://code.claude.com/docs/en/sandbox-environments). Nothing host-level clears the bar, and the container guidance is explicit that credentials must live outside the boundary, reached through a credential-injecting proxy, with `--network none` plus a Unix-socket proxy as the egress path [[12]](https://code.claude.com/docs/en/agent-sdk/secure-deployment).
- **Credentials are the asset, not the filesystem.** The Linux credential store is `~/.claude/.credentials.json` at mode 0600 — no keychain [[15]](https://code.claude.com/docs/en/authentication). Anything with your uid and unsandboxed Bash reads it. That, not `rm -rf`, is why the boundary belongs at the OS.

Full doc index: [`code.claude.com/docs/llms.txt`](https://code.claude.com/docs/llms.txt) [[18]](https://code.claude.com/docs/llms.txt). Upstream repo: [anthropics/claude-code](https://github.com/anthropics/claude-code) ⭐ 140k (Jul 2026) [[40]](https://github.com/anthropics/claude-code).
