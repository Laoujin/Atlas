---
title: "The lightweight per-PR floor for testing Claude Code agent extensions"
date: 2026-06-24
depth: standard
format: md
topic: "The lightweight end of testing Claude Code agent extensions: what a small team can do per-PR without an eval platform — deterministic config checks, cheap model-in-the-loop checks, real CI recipes/repos, and the pragmatic minimum bar"
topic_raw: "The LIGHTWEIGHT END of testing Claude Code agent extensions — what a SMALL TEAM can realistically do PER-PR WITHOUT standing up a full eval platform — plus the CONCRETE TOOLS, REPOS, and CI RECIPES aimed at extension/agent-config testing"
tags: [claude-code, ci, testing, plugins, skills, mcp]
summary: "A small team's realistic per-PR floor for testing Claude Code skills/plugins/MCP config: deterministic schema and frontmatter linting first, one cheap headless model check second."
citations: 17
reading_time_min: 8
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 338
issue: 222
---

> **Decision.** For a 3-person team the realistic floor is **deterministic, no-model-call checks gated on `.claude/**` paths**: run the built-in `claude plugin validate --strict` [[2]](https://code.claude.com/docs/en/plugins-reference) on every manifest, JSON-schema-validate `plugin.json`/`marketplace.json` against the now-official SchemaStore schemas [[2]](https://code.claude.com/docs/en/plugins-reference), lint SKILL.md frontmatter with a sub-second CLI like [pulser](https://github.com/TheStack-ai/pulser) ⭐ 17 [[5]](https://github.com/TheStack-ai/pulser) or [skill-validator](https://github.com/agent-ecosystem/skill-validator) ⭐ 174 [[7]](https://github.com/agent-ecosystem/skill-validator), and add a "does it load" smoke test by parsing the `system/init` event from `claude -p --output-format stream-json` for `plugin_errors` [[1]](https://code.claude.com/docs/en/headless). Add **at most one** cheap model-in-the-loop check (a `claude -p` headless review) only after the deterministic layer is green. Standing up a full eval platform is overkill at this scale, and honestly **little is standardized yet** — the ecosystem tools are weeks-to-months old and mostly single-maintainer.

## The honest state of play (June 2026)

This is an emerging area. Anthropic ships exactly one built-in validator — `claude plugin validate` — and it is intentionally lenient: unrecognized fields are warnings, not errors, and a plugin with only those warnings still loads at runtime [[2]](https://code.claude.com/docs/en/plugins-reference). Everything past that is community tooling, most of it single-maintainer and under a year old. One community audit of 214 published skills claimed **73% had silent structural defects** [[15]](https://dev.to/thestack_ai/i-audited-214-claude-code-skills-73-were-silently-broken-2m9a) — treat the exact number as marketing, but the direction is real: nobody is linting these files, so cheap deterministic checks have a high catch rate. The good news for a small team: the *cheap* layer is where almost all the value is, and it needs no model calls, no eval harness, and no spend.

## Layer 1 — deterministic checks (no model call, the actual floor)

These run in seconds, cost nothing, and are non-flaky. This is the layer a 3-person team must adopt; the rest is optional.

### Built-in: `claude plugin validate --strict`

Ships with the CLI. Validates `plugin.json` and `marketplace.json` structure. Default mode treats unknown fields as warnings and still passes; **`--strict` promotes warnings to errors**, which is the documented intent for CI — it catches a misspelled field name or a field left over from another tool's manifest before publishing [[2]](https://code.claude.com/docs/en/plugins-reference). Wrong-typed fields (e.g. `keywords` as a string instead of an array) fail even without `--strict` [[2]](https://code.claude.com/docs/en/plugins-reference).

```bash
claude plugin validate ./my-plugin --strict   # exit non-zero on any warning
```

### JSON-schema validation of manifests and MCP defs

Official JSON Schemas for `plugin.json` and `marketplace.json` are now published on **SchemaStore**; the manifest's `$schema` field is meant to point at `https://json.schemastore.org/claude-code-plugin-manifest.json` for editor autocomplete and offline validation [[2]](https://code.claude.com/docs/en/plugins-reference). The community [hesreallyhim/claude-code-json-schema](https://github.com/hesreallyhim/claude-code-json-schema) ⭐ 6 repo that pioneered this is now **archived precisely because Anthropic's schemas shipped to SchemaStore** [[8]](https://github.com/hesreallyhim/claude-code-json-schema) — a clean signal that the official path is the one to use. Validate in CI with any standard JSON-schema validator (e.g. `ajv-cli`, `check-jsonschema`) pointed at the SchemaStore URL; the same approach covers MCP server entries in `.mcp.json`.

### SKILL.md / agent frontmatter constraints to assert

The skills doc defines the frontmatter contract you can lint against without a model [[3]](https://code.claude.com/docs/en/skills):

| Field                      | Required    | Constraint worth asserting in CI                                                            |
| :------------------------- | :---------- | :------------------------------------------------------------------------------------------ |
| `name`                     | No          | Defaults to directory name; assert it matches dir + has no spaces/path separators [[3]](https://code.claude.com/docs/en/skills) |
| `description`              | Recommended | `description` + `when_to_use` is **truncated at 1,536 chars** in the listing — flag overflow [[3]](https://code.claude.com/docs/en/skills) |
| `allowed-tools`            | No          | Space/comma string or YAML list; assert tool names are real                                 |
| `disable-model-invocation` | No          | boolean; type-check it                                                                       |
| `user-invocable`           | No          | boolean; type-check it                                                                       |

A plain YAML-parse + required-field + type-check + the 1,536-char cap covers most real defects. The pulser audit's top finding was exactly this class: unparseable YAML and empty/missing `description` [[6]](https://dev.to/thestack_ai/testing-claude-code-skills-in-ci-pulser-eval-github-action-3na9).

### "Does it load" smoke test (cheap, one short model call or none)

The headless runner emits a `system/init` event reporting `plugins` (loaded) and `plugin_errors` (each with `plugin`, `type`, `message`, including unsatisfied dependency versions and `--plugin-dir` load failures). **The docs explicitly say: "Use the plugin fields to fail CI when a plugin did not load."** [[1]](https://code.claude.com/docs/en/headless) Pattern:

```bash
claude --bare -p "ok" --plugin-dir ./my-plugin \
  --output-format stream-json --verbose \
  | jq -e 'select(.type=="system" and .subtype=="init")
           | (.plugin_errors // []) | length == 0'
```

`--bare` skips auto-discovery of hooks/skills/MCP/CLAUDE.md so you get the same result on every machine and only what you pass with `--plugin-dir`/`--mcp-config` loads [[1]](https://code.claude.com/docs/en/headless). For MCP specifically, **`--strict-mcp-config`** loads only the config file you pass and ignores `~/.claude.json`, `.mcp.json`, and managed configs — built for CI [[4]](https://github.com/anthropics/claude-code/issues/14490). ⚠ Known bug: `--strict-mcp-config` does not currently override the `disabledMcpServers` list, so a server disabled in `~/.claude.json` stays disabled in CI [[4]](https://github.com/anthropics/claude-code/issues/14490) — pin a clean `HOME` in the runner to dodge it.

### `/doctor` for local pre-flight

`claude doctor` checks API connectivity, MCP server health, hook syntax validity, and shell integration, surfacing misconfiguration before a session [[13]](https://blog.vincentqiao.com/en/posts/claude-code-doctor/). It's interactive-oriented (a developer pre-flight, not a clean CI gate), but worth a mention in the team's contributor checklist.

## Tools comparison (deterministic config/extension linters)

All of these test the *artifacts and their config*, not model output. Stars are a triage signal — most are very young, single-maintainer projects.

| Tool                                                                          | ⭐ Stars | What it checks                                                                              | Runs as                          | Source |
| :---------------------------------------------------------------------------- | :------ | :----------------------------------------------------------------------------------------- | :------------------------------- | :----- |
| `claude plugin validate --strict` (built-in)                                  | —       | `plugin.json`/`marketplace.json` structure; strict = warnings-as-errors                    | CLI, instant                     | [[2]](https://code.claude.com/docs/en/plugins-reference) |
| [pulser](https://github.com/TheStack-ai/pulser)                               | ⭐ 17   | 5 checks: YAML parse, required fields, description quality, file structure, cross-refs; ~200ms/40 skills, zero deps | CLI / GitHub Action `pulserin/pulser@v1` | [[5]](https://github.com/TheStack-ai/pulser) [[6]](https://dev.to/thestack_ai/testing-claude-code-skills-in-ci-pulser-eval-github-action-3na9) |
| [skill-validator](https://github.com/agent-ecosystem/skill-validator)         | ⭐ 174  | Spec compliance, token counts (`o200k_base`), link resolution (HEAD), file hygiene, unclosed code fences; optional LLM-judge | Go CLI / pre-commit / Actions (`--emit-annotations`, `--strict`) | [[7]](https://github.com/agent-ecosystem/skill-validator) |
| [claude-code-json-schema](https://github.com/hesreallyhim/claude-code-json-schema) | ⭐ 6 | JSON-schema for manifests — **archived**, superseded by official SchemaStore schemas       | `npx github:…` / IDE             | [[8]](https://github.com/hesreallyhim/claude-code-json-schema) |
| [agent-skills-lint](https://github.com/swarmclawai/agent-skills-lint)         | ⭐ 1    | Cross-agent skill schema (Claude/Codex/Cursor/…), name+description core + per-flavor rules  | `npx @swarmclawai/agent-skills-lint` | [[9]](https://github.com/swarmclawai/agent-skills-lint) |
| [SkillCheck](https://www.getskillcheck.com/)                                  | —       | Validates against the [Agent Skills](https://agentskills.io) standard; Pro adds anti-slop/WCAG/security | Hosted/web                       | [[16]](https://www.getskillcheck.com/) |

`agentskills.io` is the cross-tool open standard Claude Code skills follow [[3]](https://code.claude.com/docs/en/skills), so validating against it keeps a skill portable to Codex/Cursor/etc. Two takeaways: (1) **pick one frontmatter linter** — they overlap heavily; skill-validator is the most feature-complete and the only one with built-in CI annotations; pulser is the fastest zero-dep option. (2) For manifests, prefer the **built-in `validate --strict` + SchemaStore** combo over any community schema repo.

## Layer 2 — cheap model-in-the-loop, runnable per-PR

Only add this once Layer 1 is green; it costs tokens and is non-deterministic. The point is *one* lightweight headless review, not an eval suite.

- **Headless `claude -p` as a project linter.** `-p`/`--print` runs non-interactively, prints to stdout, and exits with a status code your pipeline can branch on [[1]](https://code.claude.com/docs/en/headless). Pipe the PR diff in (no Bash permission needed) and ask for structured output:

  ```bash
  git diff origin/main | claude --bare -p \
    --append-system-prompt "You review Claude Code skills. Flag skills whose description won't trigger correctly, or that reference missing files." \
    --output-format json \
    --json-schema '{"type":"object","properties":{"issues":{"type":"array","items":{"type":"string"}}},"required":["issues"]}' \
  | jq -e '.structured_output.issues | length == 0'
  ```

  `--output-format json` + `--json-schema` returns schema-conforming output in `structured_output`, and the payload includes `total_cost_usd` so you can budget per run [[1]](https://code.claude.com/docs/en/headless). Cap work with `--max-turns`.

- **`anthropics/claude-code-action`** ⭐ 8.1k is the official GitHub Action wrapping the same Agent SDK for PR/issue automation and review [[11]](https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md). Use it for a `@claude review` style pass, not as a gate.

- ⚠ **Security caveat for any PR-triggered model run.** A June 2026 disclosure showed a flaw where a single malicious issue could hijack repositories through the Claude Code GitHub Action [[14]](https://thehackernews.com/2026/06/claude-code-github-action-flaw-let-one.html). Treat untrusted PR/issue content as a prompt-injection vector: pin action versions, scope `--allowedTools` tightly (or run `--permission-mode dontAsk`), and don't grant write/secrets to runs triggered by forks.

## Concrete GitHub Actions recipes

### Deterministic gate (the one every team should copy)

```yaml
name: Lint extensions
on:
  pull_request:
    paths: ['.claude/**', '.claude-plugin/**', '.mcp.json']
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate manifests (strict)
        run: npx @anthropic-ai/claude-code plugin validate . --strict
      - name: Schema-check manifests
        run: |
          npx ajv-cli validate \
            -s https://json.schemastore.org/claude-code-plugin-manifest.json \
            -d ".claude-plugin/plugin.json"
      - name: Lint skill frontmatter
        run: npx pulser eval     # or: skill-validator check .claude/skills --strict
```

The `paths:` filter is the cost-control lever — skill linting runs only when extension files change, adding ~15s to the pipeline [[6]](https://dev.to/thestack_ai/testing-claude-code-skills-in-ci-pulser-eval-github-action-3na9). pulser also ships a one-line Action (`uses: pulserin/pulser@v1`) with exit 0 = pass, 1 = structural problems, 2 = runtime error [[6]](https://dev.to/thestack_ai/testing-claude-code-skills-in-ci-pulser-eval-github-action-3na9).

### Marketplace-scale precedent

Large community marketplaces already gate manifests this way: the [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) ⭐ 2.4k marketplace runs `claude plugin validate` over `marketplace.json` and every `plugin.json` in CI so invalid manifests can't merge [[17]](https://github.com/jeremylongshore/claude-code-plugins-plus-skills), and Anthropic's own [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) ⭐ 31k is the reference `marketplace.json` to diff your schema against [[18]](https://github.com/anthropics/claude-plugins-official). For a starting skill corpus to test tooling against, [glebis/claude-skills](https://github.com/glebis/claude-skills) ⭐ 286 is a clean small collection [[19]](https://github.com/glebis/claude-skills).

## The pragmatic minimum bar for a 3-person team

In priority order — stop wherever the budget for *maintaining* checks runs out:

1. **CI path filter on `.claude/**` + manifests** so checks run only on extension changes [[6]](https://dev.to/thestack_ai/testing-claude-code-skills-in-ci-pulser-eval-github-action-3na9). (5 min)
2. **`claude plugin validate --strict`** on every manifest [[2]](https://code.claude.com/docs/en/plugins-reference). (built-in, free)
3. **One frontmatter linter** — pulser or skill-validator — as a required check [[5]](https://github.com/TheStack-ai/pulser) [[7]](https://github.com/agent-ecosystem/skill-validator). (free, sub-second)
4. **JSON-schema validate** manifests/MCP defs against SchemaStore [[2]](https://code.claude.com/docs/en/plugins-reference). (free)
5. **"Does it load" smoke test** via `claude -p --output-format stream-json` → assert empty `plugin_errors` [[1]](https://code.claude.com/docs/en/headless). (one trivial run)
6. *(Optional, last)* **One headless `claude -p` model review** of the diff with `--json-schema` structured output [[1]](https://code.claude.com/docs/en/headless), behind the security guardrails above [[14]](https://thehackernews.com/2026/06/claude-code-github-action-flaw-let-one.html).

Steps 1–5 are deterministic, free, and non-flaky — that is the floor, and it's enough. Step 6 is the only place you spend tokens, and a small team should keep it to a single advisory check rather than a gate. Anything beyond this (golden datasets, LLM-as-judge rubrics, statistical delta gates) is the eval-platform territory this brief deliberately leaves out — note that `skill-validator`'s `score evaluate` LLM-judge mode [[7]](https://github.com/agent-ecosystem/skill-validator) is the one place a lightweight tool crosses into that space if you ever want it.
