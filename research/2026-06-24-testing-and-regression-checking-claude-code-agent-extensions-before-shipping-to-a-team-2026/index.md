---
layout: expedition
title: "Testing & regression-checking Claude Code agent extensions before you ship them"
date: 2026-06-24
topic: "Survey: how to test and regression-check authored Claude Code agent extensions (Skills, subagents, hooks, MCP, plugins) before shipping them to a team (2026) — extension-artifact testing, not general LLM-output evaluation. Covers trigger/routing tests, snapshot/regression patterns, supply-chain rug-pull defense, and the realistic lightweight per-PR floor."
format: md
tags: [claude-code, agent-extensions, testing, ci, supply-chain]
summary: "How to prove the skill, subagent, hook, plugin, or MCP server you authored actually works before your team installs it — and where, in 2026, the tooling still runs out."
cover: cover.svg
synthesis: true
children:
  - slug: testing-an-authored-skill
    title: "Testing an authored Claude Code Skill before you ship it to a team"
    depth: survey
    status: success
    summary: "The two things to test are separable — does the description trigger, and does the body behave — and in 2026 the de-facto harness is Anthropic's skill-creator eval loop plus a with-skill/without-skill baseline; everything else is thin."
    citations: 11
    reading_time_min: 6
  - slug: smoke-testing-subagent-routing
    title: "Smoke-testing a Claude Code subagent's routing before you ship it"
    depth: survey
    status: success
    summary: "Promptfoo's claude-agent-sdk provider plus headless stream-json are the only real ways to assert subagent routing in 2026; the description field is the trigger, parent_tool_use_id is the proof."
    citations: 11
    reading_time_min: 8
  - slug: regression-testing-plugins-and-mcp-servers-plus-catching-rug-pulls
    title: "Regression-testing Claude Code plugins & MCP servers, and catching rug-pulls"
    depth: expedition
    status: success
    summary: "Two test surfaces — functional schema/contract drift and supply-chain rug-pulls — with the 2026 tooling that catches each, and an honest map of where the defenses are still missing."
    citations: 49
    reading_time_min: 18
  - slug: the-lightweight-per-pr-floor-and-concrete-ci-recipes-and-tools
    title: "The lightweight per-PR floor for testing Claude Code agent extensions"
    depth: survey
    status: success
    summary: "A small team's realistic per-PR floor for testing Claude Code skills/plugins/MCP config: deterministic schema and frontmatter linting first, one cheap headless model check second."
    citations: 17
    reading_time_min: 8
  - slug: testing-hooks
    title: "Testing Claude Code Hooks Before Shipping to a Team"
    depth: recon
    status: success
    summary: "Hooks are plain scripts with a documented stdin/exit-code/JSON contract — the one Claude Code extension you can test with fully-deterministic CI."
    citations: 6
    reading_time_min: 3
model: "Opus 4.8"
cost_usd: "sub"
issue: 222
duration_sec: 552
---

> **TL;DR.** Extension testability is a gradient, not a checkbox. **Hooks** are plain scripts with a fixed stdin/exit-code/JSON contract, so they take fully-deterministic CI (bats/pytest) [[1]](https://code.claude.com/docs/en/hooks). **Skills and subagents** are model-in-the-loop: their `description` field *is* the unit under test, and you can only gate on hit-rate over a prompt set, never a single green run [[2]](https://www.promptfoo.dev/docs/guides/test-agent-skills/). **MCP servers and plugins** add a third axis you don't author — a supply chain that can rug-pull after install [[3]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks). Nobody has a clean, purpose-built harness yet; the working stack is improvised from `claude -p`, Promptfoo, snapshot tests, and JSON-schema linters.

**The description is the test, for both skills and subagents.** Claude decides whether to fire a skill or delegate to a subagent by fuzzy-matching its `description` against the prompt [[4]](https://code.claude.com/docs/en/sub-agents) [[5]](https://mcp.directory/blog/why-your-claude-skill-isnt-activating-2026-fixes). So "does my skill trigger?" and "does the parent route to my subagent?" are the *same* test, written the same way: positive prompts that must hit, plus near-miss prompts that must route to a sibling instead. Promptfoo expresses this directly with `skill-used` / `not-skill-used` assertions [[2]](https://www.promptfoo.dev/docs/guides/test-agent-skills/); Anthropic's skill-creator upgrade (shipped **3 March 2026**) treats triggering as a false-positive/false-negative classifier and auto-tunes the description against sample prompts [[6]](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills). Both fight the same enemy: autonomous triggering is only ~50% reliable, so for must-fire workflows teams fall back to a deterministic `UserPromptSubmit` hook that calls `Use Skill()` explicitly [[7]](https://dev.to/lizechengnet/why-claude-code-skills-dont-trigger-and-how-to-fix-them-in-2026-o7h).

**Two different regression problems hide under one word.** *Functional drift* is your own artifact changing — caught by snapshotting `tools/list` and failing CI on schema diff (Bellwether [[8]](https://github.com/dotsetlabs/bellwether), the official MCP conformance suite [[9]](https://github.com/modelcontextprotocol/conformance), or FastMCP in-memory client tests [[10]](https://gofastmcp.com/development/tests)). A *rug-pull* is a dependency changing *after* you approved it — postmark-mcp behaved identically for 15 versions, then shipped a BCC backdoor in v1.0.16 [[11]](https://snyk.io/blog/malicious-mcp-server-on-npm-postmark-mcp-harvests-emails/). These need opposite defenses: hash-pinning tool descriptions and alerting on change (mcp-scan / Snyk agent-scan [[12]](https://github.com/snyk/agent-scan)), pinning servers to a `sha256` digest [[13]](https://github.com/safedep/pinner-mcp), and provenance — though provenance is not a silver bullet, since 633 malicious npm versions passed Sigstore verification with stolen certificates in **May 2026** [[14]](https://venturebeat.com/security/npm-sigstore-provenance-stolen-identity-audit-grid-2026). MCP still has no native re-approval when a tool mutates [[3]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks).

**The realistic per-PR floor is deterministic, and cheap.** Before any model call: `claude plugin validate --strict` (warnings become errors) [[15]](https://code.claude.com/docs/en/plugins-reference), JSON-schema validation of `plugin.json`/`marketplace.json` (now official on SchemaStore [[16]](https://github.com/hesreallyhim/claude-code-json-schema)), a frontmatter/SKILL.md linter, and a "does it load" smoke test via `claude -p --output-format stream-json` reading the `system/init` event's `plugin_errors` [[17]](https://code.claude.com/docs/en/headless). The CI-native linters that exist are tiny and single-maintainer — pulser [[18]](https://github.com/TheStack-ai/pulser), skill-validator [[19]](https://github.com/agent-ecosystem/skill-validator) — which is itself the finding: this is emerging, and the consolidation signal is schemas landing on SchemaStore, not a dominant tool.

**The surface itself is unstable.** 2026 broke working assertions: the `Task`→`Agent` tool rename means transcript matchers must accept both strings, and regression #17591 (open since 12 Jan 2026) has `TaskOutput` returning raw JSONL instead of the subagent summary, breaking transcript-based dispatch checks [[20]](https://github.com/anthropics/claude-code/issues/17591). The open question a small team can't escape: deterministic linting and unit-tested hooks fit neatly per-PR, but the rug-pull surface has *no* per-PR answer — the malicious change lands after install, in someone else's repo, long after your diff was green.
