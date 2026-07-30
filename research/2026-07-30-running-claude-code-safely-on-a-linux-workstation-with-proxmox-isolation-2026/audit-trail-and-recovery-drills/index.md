---
title: "Audit trail and recovery drills for an agentic coding CLI on Linux"
date: 2026-07-30
depth: ceo
format: md
topic: "Audit trail and recovery drills for an agentic coding CLI on Linux (2026). One page: how do you know what the agent did, and how do you undo it? Cover the shortest useful list — Claude Code's own session transcripts/logs and `--output-format json`, PostToolUse hooks or an OpenTelemetry exporter as a durable action log, shell-level logging (auditd, `script`, bash history with timestamps), git as the primary undo (frequent commits, `git reflog`, worktrees per task, and why an agent that can run `git` can also erase the trail), filesystem/VM snapshots (btrfs/ZFS/timeshift on the workstation, `qm`/`pct snapshot` on Proxmox) and how fast a restore actually is, and the one thing most people skip: actually rehearsing a restore before you need it. End with a 5-step drill."
topic_raw: "switching from windows to linux. on my system, I'm also going to run Claude. for my homelab I'm using proxmox on the minipc to \"separate\" systems. for running claude \"safely\", what can I do there?"
tags: [claude-code, audit-log, backup, git, proxmox, linux, observability]
summary: "Git commits are your real undo and a PostToolUse hook is your real audit log — Claude Code's own transcripts and /rewind are convenience layers that expire, miss bash, and are writable by the agent."
citations: 12
reading_time_min: 3
cover: cover.svg
model: "Opus 5"
cost_usd: "sub"
duration_sec: 268
issue: 12
---

> **Decision.** Treat **git** as the undo and a **PostToolUse hook writing outside the repo** as the audit log. Claude Code's built-ins are convenience, not evidence: transcripts are deleted after 30 days [[1]](https://code.claude.com/docs/en/sessions), and `/rewind` cannot undo anything a bash command did, nor a subagent's edits [[4]](https://code.claude.com/docs/en/checkpointing). Then rehearse one restore — "a backup you have never restored from is not a backup, it is a theory" [[12]](https://oneuptime.com/blog/post/2026-03-02-test-backup-integrity-restores-ubuntu/view).

## How you know what it did

| Layer | Gives you | Gap |
|-------------------|--------------------------------------------------------------|-----------------------------------------------------|
| Session transcript | JSONL per session at `~/.claude/projects/<project>/<id>.jsonl`; `/export` for humans [[1]](https://code.claude.com/docs/en/sessions) | 30-day retention, format is internal and breaks between releases [[1]](https://code.claude.com/docs/en/sessions) |
| `claude -p --output-format json` | Result, session ID, usage, cost of one run as parseable JSON [[1]](https://code.claude.com/docs/en/sessions) | Per-run only, not a standing log |
| `PostToolUse` hook | Hook JSON on stdin — `session_id`, `cwd`, `tool_name`, `tool_input`, `tool_result`, `transcript_path` — append it anywhere [[3]](https://code.claude.com/docs/en/hooks) | You write it; agent can `rm` it if writable |
| OpenTelemetry | `CLAUDE_CODE_ENABLE_TELEMETRY=1` + `OTEL_LOGS_EXPORTER` emits `claude_code.tool_decision` / `tool_result` / `api_request`; add `OTEL_LOG_TOOL_DETAILS=1` for actual commands and file paths [[2]](https://code.claude.com/docs/en/monitoring-usage) | Needs a collector (Loki/SigNoz) |
| auditd | `-a always,exit -F arch=b64 -S execve -k user-commands`, query `ausearch -k user-commands` [[7]](https://linuxbash.sh/post/audit-user-command-history-with-auditd-rules) | Kernel-level truth, noisy and hard to read |

Cheap extras: `HISTTIMEFORMAT` to timestamp shell history [[8]](https://www.gnu.org/software/bash/manual/html_node/Bash-Variables.html), and `script --log-timing` to make a replayable typescript of a whole session [[9]](https://man7.org/linux/man-pages/man1/script.1.html).

⚠ Send the hook/OTel log to a path the agent cannot write — a systemd-journal socket, a Loki endpoint, or a Proxmox-side collector. An audit log inside the workspace is not an audit log.

## How you undo it

**Git first.** Commit before every prompt; one worktree per task. `git reflog` recovers a bad `reset --hard` or force-push — but reachable entries expire after 90 days and unreachable ones after 30 [[5]](https://git-scm.com/docs/git-reflog). ⚠ An agent allowed to run `git` can also rewrite history: a real report had `git reset --hard` run unauthorized, destroying hours of work → "the safeguards have to be outside the model" [[6]](https://dev.to/shuicici/claude-codes-silent-git-reset-what-actually-happened-and-what-it-means-for-ai-dev-tools-3449). Deny `git reset --hard`, `git push --force`, `git clean` in permissions, and push to a remote the agent has no credentials for.

**Snapshots second.** Timeshift on btrfs is near-instant, but ⚠ **excludes `/home` by default** — where your code and `~/.claude` live [[10]](https://computingforgeeks.com/timeshift-backup-restore-linux/). On Proxmox, `qm snapshot <vmid> <name> --vmstate 1` then `qm rollback <vmid> <name>`; RAM-inclusive snapshots auto-start the VM on rollback [[11]](https://pve.proxmox.com/pve-docs/qm.1.html). Rollback is seconds-to-minutes — the cost is losing everything since the snapshot, so snapshot *before* an unattended run, not nightly.

## The 5-step drill

1. `qm snapshot 101 pre-agent --vmstate 1` before an unattended session [[11]](https://pve.proxmox.com/pve-docs/qm.1.html).
2. Let the agent do real destructive work: `rm -rf src/`, then `git reset --hard HEAD~3`.
3. Recover with git alone — `git reflog`, checkout the pre-reset SHA [[5]](https://git-scm.com/docs/git-reflog). Time it.
4. Now recover the file the agent deleted via bash, which `/rewind` cannot restore [[4]](https://code.claude.com/docs/en/checkpointing): `qm rollback 101 pre-agent` [[11]](https://pve.proxmox.com/pve-docs/qm.1.html).
5. Reconstruct *what happened* from the hook log alone, with `~/.claude/projects` deleted [[3]](https://code.claude.com/docs/en/hooks). If you can't, your audit trail is the transcript — and it expires [[1]](https://code.claude.com/docs/en/sessions).
