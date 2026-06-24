---
title: "Testing Claude Code Hooks Before Shipping to a Team"
date: 2026-06-24
depth: ceo
format: md
topic: "How to test Claude Code hooks before shipping them to a team — unit-test the scripts (sample JSON on stdin, assert exit code + JSON stdout), validate settings.json matcher wiring, verify registration via claude --debug and /hooks, plus 2026 contract changes"
topic_raw: "How to TEST CLAUDE CODE HOOKS before shipping them to a team"
tags: [claude-code, hooks, testing, ci, bats, pytest]
summary: "Hooks are plain scripts with a documented stdin/exit-code/JSON contract — the one Claude Code extension you can test with fully-deterministic CI."
citations: 6
reading_time_min: 3
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 133
issue: 222
---

> **TL;DR.** A Claude Code hook is a shell command the harness runs on a lifecycle event; it reads event JSON on stdin and answers via exit code (0 = allow, 2 = block) plus optional JSON on stdout [[1]](https://code.claude.com/docs/en/hooks). That fixed I/O contract makes hooks the **one extension type you can test with boring, fully-deterministic CI** — pipe a fixture into the script, assert the exit code and stdout. No model in the loop, no flaky output. Contrast skills/subagents, where correctness depends on the LLM. Test in three layers: (1) the script, (2) the `settings.json` wiring, (3) live registration.

## Layer 1 — Unit-test the script (the real test surface)

The hook is a process. Feed it a fixture, assert. The primitive everyone uses [[2]](https://pydevtools.com/handbook/how-to/how-to-write-claude-code-hooks-for-python-projects/):

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' \
  | .claude/hooks/block-rm.sh; echo $?   # expect 2
```

Wrap that in any process-level runner — **bats** for pure-shell hooks, **pytest** (`subprocess.run`, assert `returncode` and parse `stdout`) for Python, **jest** (`child_process`) for Node [[3]](https://mcpmarket.com/tools/skills/claude-code-hook-testing-guide). Table-drive the cases: blocked input → exit 2; allowed input → exit 0; for `PreToolUse` decisions, assert the parsed `hookSpecificOutput.permissionDecision` is `deny`/`allow`/`ask`/`defer` [[1]](https://code.claude.com/docs/en/hooks). Cover edge cases — empty stdin, malformed JSON, missing `tool_input` — because the harness will eventually send them.

**Honesty flag:** there is **no official hook-testing harness**. The closest is a community pytest/uv skill packaging subprocess + JSON-assertion patterns [[3]](https://mcpmarket.com/tools/skills/claude-code-hook-testing-guide); otherwise you wire stock bats/pytest/jest yourself. That is a feature, not a gap — it's ordinary process testing.

## Layer 2 — Validate the `settings.json` wiring

A correct script wired to the wrong matcher is a silent no-op. The matcher is a string/regex against `tool_name` (`Bash`, `Edit|Write`, `mcp__memory__.*`) [[1]](https://code.claude.com/docs/en/hooks). In CI, lint the config: assert it's valid JSON, the `matcher` regex compiles, and `command` paths resolve (prefer `${CLAUDE_PROJECT_DIR}` + exec-form `args` over shell strings) [[4]](https://www.morphllm.com/claude-code-hooks).

## Layer 3 — Verify live registration

`/hooks` lists every registered hook (event, matcher, source file) — read-only sanity check [[1]](https://code.claude.com/docs/en/hooks). `claude --debug` prints full hook input/output JSON and exit handling per fire — use it once to confirm matcher + parsing before trusting the unit suite [[5]](https://claudefa.st/blog/tools/hooks/hooks-guide).

## 2026 contract changes to retest against

| Change                                | Impact on tests                                                              |
|---------------------------------------|------------------------------------------------------------------------------|
| `permissionDecision` in `hookSpecificOutput` (`allow`/`deny`/`ask`/`defer`) | Assert the nested object, not a top-level `decision` [[1]][a]    |
| `updatedInput` / `updatedToolOutput`  | Hooks can rewrite tool args/results — snapshot the rewritten JSON [[1]][a]   |
| New handler types: `http`, `prompt`, `agent` | Only `command`/`http` are deterministic; `prompt`/`agent` put the model back in the loop — **not CI-testable** [[1]][a] |
| 30+ events, `disableAllHooks`, exec-form `args` | Re-pin event names and matcher form in fixtures [[6]](https://thepromptshelf.dev/blog/claude-code-hooks-complete-reference-2026/) |

[a]: https://code.claude.com/docs/en/hooks

Net: keep hooks `type: command`, give every hook a fixture table in CI, and the deterministic layer of your agent config ships with real regression coverage.
