---
layout: expedition
title: "Extending Claude Code: MCP, Skills, Plugins — a session-3 blueprint"
date: 2026-05-23
topic: "Design and deliver a 1–2 hour virtual deep-dive session, third in a series (prior sessions covered \"AI & security\" and \"Context/compounding/harness engineering\"), on extending coding agents — with Claude Code as the focal harness — through MCP, Skills, Plugins, and the emerging Marketplace ecosystem in 2026."
format: md
tags: [claude-code, mcp, skills, plugins, ai-security]
summary: "Session blueprint for an expert-audience deep-dive on extending Claude Code through MCP, Skills, Plugins, and the marketplaces around them — with a comparison table, live-demo recipes, and the trust-boundary callbacks a third-in-series session needs to earn its slot."
cover: cover.svg
synthesis: true
children:
  - slug: mcp-deep-dive
    title: "MCP deep-dive"
    depth: standard
    status: success
    summary: "Talk-prep brief for a 1–2 hour deep-dive on the Model Context Protocol — architecture, 2026 spec, ecosystem, security trifecta, and live-demo recipes."
    citations: 30
    reading_time_min: 10
  - slug: claude-code-skills
    title: "Claude Code Skills"
    depth: standard
    status: success
    summary: "A Skill is a Markdown file + optional bundled scripts that Claude loads on demand. Cheaper than CLAUDE.md, more discoverable than a slash command, lighter than a subagent — and now an open cross-vendor standard."
    citations: 13
    reading_time_min: 5
  - slug: plugins-the-marketplace
    title: "Plugins & the Marketplace"
    depth: standard
    status: success
    summary: "What plugins actually are, how the official + community marketplaces work, the few that earn their keep, and the trust footgun to flag in any 1–2 hour deep-dive."
    citations: 21
    reading_time_min: 10
  - slug: subagents-hooks-and-the-rest-of-the-harness
    title: "Subagents, hooks, and the rest of the harness"
    depth: ceo
    status: success
    summary: "One-page mental model for teaching Claude Code's harness: subagents (isolation), hooks (determinism), and the config substrate (skills, permissions, settings)."
    citations: 6
    reading_time_min: 2
  - slug: comparison-decision-framework
    title: "Comparison & decision framework"
    depth: ceo
    status: success
    summary: "Score candidate topics on four axes — audience fit, series continuity, speaker readiness, demo viability — with weights chosen before scoring. Skip RICE; it's product-feature shaped."
    citations: 7
    reading_time_min: 2
  - slug: session-delivery-plan
    title: "Session delivery plan"
    depth: ceo
    status: success
    summary: "A 90-minute run-of-show with 8-12 min active blocks, mid-session recap, and series-continuity callbacks tuned for the third session in a deep-dive series."
    citations: 8
    reading_time_min: 2
cost_usd: 11.19
duration_sec: 2080
citations: 85
reading_time_min: 31
issue: 57
model: "Opus 4.7"
---

## The through-line: composition, not selection

The four extension primitives don't compete — they nest. A **plugin** is the packaging unit; it can bundle **skills**, **subagents**, slash commands, hooks, and pre-configured **MCP servers** in one directory installed via `/plugin` ([[1]](https://claude.com/blog/claude-code-plugins), [[2]](https://www.agensi.io/learn/claude-code-plugin-marketplace-guide)). A skill with `context: fork` runs inside a **subagent** ([[3]](https://code.claude.com/docs/en/skills)). A **hook** can fire on a subagent's tool call ([[4]](https://code.claude.com/docs/en/hooks)). The deep-dive should teach the layer cake first, then the comparison table — otherwise the audience will hear four overlapping pitches and pick whichever the speaker demos last.

The cleanest mental hook from the harness brief: subagents give *isolation*, hooks give *determinism* (only `PreToolUse` blocks), the rest is *substrate* ([[4]](https://code.claude.com/docs/en/hooks), [[5]](https://code.claude.com/docs/en/sub-agents)). Ask: *context problem, determinism problem, or defaults problem?*

## The Skill-vs-MCP live wire — don't duck it

Simon Willison's framing — "I expect we'll see a Cambrian explosion in Skills which will make this year's MCP rush look pedestrian by comparison" ([[6]](https://simonwillison.net/2025/Oct/16/claude-skills/)) — is the one tension expert audiences will already be arguing about. The workable heuristic the children converged on: **MCP** when you need a long-lived stateful connection (DB session, OAuth handshake, SaaS API); **Skill** when "run this CLI, read the output" is enough; both can ship inside the same plugin. Skills are also now a *cross-vendor open standard* — Cursor, Copilot, Codex, Gemini CLI and 30+ agents read the same `SKILL.md` ([[7]](https://agentskills.io)) — so portability has flipped in their favour.

## The trust boundary is the session's reason to exist

This is session 3 in a series whose second instalment was security. Don't paper over the inheritance — every extension layer has both a high-leverage distribution mechanism *and* a fresh CVE history:

- **MCP**: 110M+ SDK downloads/month under Linux Foundation governance ([[8]](https://aaif.io/blog/mcp-is-now-enterprise-infrastructure-everything-that-happened-at-mcp-dev-summit-north-america-2026/), [[9]](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)), but `mcp-remote` CVE-2025-6514 (437k+ downloads, RCE), Postmark BCC supply-chain, Smithery breach (3,000+ servers), and a 2026 scan finding ~200,000 vulnerable instances exposed ([[10]](https://authzed.com/blog/timeline-mcp-breaches), [[11]](https://www.practical-devsecops.com/mcp-security-vulnerabilities/)).
- **Skills**: Snyk's ToxicSkills audit found **36.8% of skills with at least one flaw, 13.4% critical, 91% of malicious skills embed prompt injection to bypass safety** — and the dynamic-context `` !`cmd` `` feature runs *before* the model sees the skill, so model-level defences never fire ([[12]](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/)).
- **Plugins**: CVE-2025-59536 (RCE via hook config *before* the trust dialog), the "TrustFall" pattern (cloning a hostile repo executes code), and marketplace dependency-hijack PoCs ([[13]](https://blog.checkpoint.com/research/check-point-researchers-expose-critical-claude-code-flaws/), [[14]](https://www.darkreading.com/application-security/trustfall-exposes-claude-code-execution-risk), [[15]](https://www.sentinelone.com/blog/marketplace-skills-and-dependency-hijack-in-claude-code/)).

The unifying frame to land on a slide is Willison's **lethal trifecta** — private data + untrusted instructions + an exfiltration vector ([[16]](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/)). Every layer above makes assembling it accidentally easier.

## Shape of the 90 minutes

The delivery-plan child argues for 75 min content + 15 min buffer, 8–12 min active blocks, monologue capped at ~7 min, mid-session recap at 0:45, and a cold-open callback to sessions 1 and 2 ([[17]](https://www.getcontrast.io/learn/webinar-benchmarks), [[18]](https://webinarjam.com/blog/the-best-webinar-length-2026/)). Three live demos earn their slot: build a FastMCP tool + Inspector ([[19]](https://github.com/PrefectHQ/fastmcp), [[20]](https://github.com/modelcontextprotocol/inspector)), `mkdir → plugin.json → SKILL.md → --plugin-dir` to ship a plugin in one breath ([[21]](https://code.claude.com/docs/en/plugins)), and a sandboxed tool-poisoning reproduction ([[16]](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/)). Pre-record each as a fallback.

The decision-framework child suggests locking weights *before* scoring candidates and breaking ties on runnable-demo viability ([[22]](https://airfocus.com/blog/weighted-decision-matrix-prioritization/)) — applied here, the trust-boundary block keeps its slide count because it's the only block that compounds on the prior session's audience.

## Open question to leave on stage

With plugins as the packaging layer, MCP under Linux Foundation governance, and `SKILL.md` now a cross-vendor format, the harness boundary has moved from "what Claude Code knows" to "what the marketplace ships." The registry-as-trust-root is the only realistic answer to supply-chain attacks ([[10]](https://authzed.com/blog/timeline-mcp-breaches)), but it isn't solved yet — so the honest question to hand the audience is whether session 4 should be **agent-to-agent (A2A) coordination** ([[23]](https://www.merge.dev/blog/mcp-vs-a2a)), or a hard look at whether any of this is auditable enough to put on the critical path.
