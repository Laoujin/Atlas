---
layout: expedition
title: "Extending Claude Code — Session 4: Authoring Craft & Operating at Scale"
date: 2026-06-03
topic: "Fourth session in a virtual deep-dive series for an expert developer audience (1–2h, virtual). Prior sessions: (1) AI & security, (2) context / compounding / harness engineering, (3) extending Claude Code — MCP, Skills, Plugins, marketplace (a survey-level blueprint already exists). This session goes deeper on the craft of extending an agent — not *what* a skill / MCP server / plugin is (the audience knows the anatomy), but *how* to author good ones and operate them at scale."
format: md
tags: [claude-code, mcp, agent-sdk, developer-craft, security]
summary: "Expert session blueprint: description-as-interface, progressive disclosure across all three extension layers, the client-side MCP primitives builders skip, tool-poisoning as the live security thread, and the token/cost mechanics that make these choices matter at team scale."
cover: cover.svg
synthesis: true
children:
  - slug: skill-mcp-plugin-authoring-craft
    title: "Skill / MCP / plugin authoring craft"
    depth: standard
    status: success
    summary: "Expert guide to authoring Agent Skills, MCP servers, and Claude Code plugins: format specs, craft rules, security contracts, and the decision matrix between all three."
    citations: 18
    reading_time_min: 9
  - slug: operating-extensions-at-scale
    title: "Operating extensions at scale"
    depth: standard
    status: success
    summary: "Token budget maths, skill routing mechanics, the six MCP primitives, headless CI patterns, and team rate-limit tables for expert developers operating Claude Code extensions at scale."
    citations: 18
    reading_time_min: 9
  - slug: mcp-beyond-hello-tool
    title: "MCP beyond \"hello tool\""
    depth: standard
    status: success
    summary: "Six primitives, two transports, tool design patterns, tool-poisoning attack chains, and the 2026 production gaps — everything past the first tutorial."
    citations: 19
    reading_time_min: 10
  - slug: claude-agent-sdk-headless-agents
    title: "Claude Agent SDK & headless agents"
    depth: standard
    status: success
    summary: "Complete technical reference: the query() API, claude -p headless mode, subagents, hooks, dynamic workflows, and the June 15 2026 billing separation—all from official docs."
    citations: 18
    reading_time_min: 8
cost_usd: 1.75
duration_sec: 831
citations: 73
reading_time_min: 36
model: "Sonnet 4.6"
issue: 181
---

Four research threads converge on a single structural insight: **the `description` field is the universal interface contract** for every extension layer in Claude Code. It is the activation signal in `SKILL.md` [[1]](https://agentskills.io/specification), the tool-selection mechanism in MCP server schemas [[2]](https://modelcontextprotocol.io/specification/2025-11-25), and the dispatch signal for subagent auto-invocation in the Agent SDK [[3]](https://code.claude.com/docs/en/agent-sdk/subagents). Getting a description wrong is not a documentation problem — it is a routing failure that compounds across every session. The session should open here and make participants write one before the first break.

**Progressive disclosure is the architecture, not a style choice.** Skills carry ~100 tokens at startup (name + description only); the body loads only when the skill is relevant [[4]](https://codersera.com/blog/claude-skills-mcp-servers-practitioner-guide-2026/). MCP Tool Search (Jan 2026) applies the same principle to tool schemas: names enter context at startup, full definitions defer until searched — reported savings up to 95% in startup token cost [[5]](https://www.mindstudio.ai/blog/claude-code-mcp-server-token-overhead), recovering 13,200+ tokens in measured sessions [[6]](https://www.jdhodges.com/blog/claude-code-mcp-server-token-costs/). Subagent descriptions front-load the routing decision so the spawn prompt never enters context unless the parent decides to dispatch. The pattern is consistent; the session should treat it as a first-class design principle, not an optimization tip. The corollary: `CLAUDE.md` loads unconditionally; everything that can be a Skill should become one. Keep `CLAUDE.md` under 200 lines.

**The client-side MCP primitives are the session's highest-leverage underused content.** Sampling, elicitation, and roots are what the audience's mental model of MCP likely omits, because every "hello tool" tutorial shows only the three server-side primitives [[7]](https://www.channel.tel/blog/mcp-sampling-elicitation-patterns-builders-skip). Elicitation (typed execution gates, structured user input) is operationally the most valuable — replacing fragile multi-turn loops with schema-validated JSON back from a native form [[8]](https://mcginniscommawill.com/posts/2026-03-25-mcp-sampling-elicitation-guide/). However, the spec and the implementations are out of sync: elicitation shipped in the June 2025 spec, but as of June 2026 Claude Code and Claude Desktop support neither elicitation nor sampling [[9]](https://mcginniscommawill.com/posts/2026-03-25-mcp-sampling-elicitation-guide/). VS Code (GitHub Copilot) supports both. This is a live contradiction worth naming in the session. Sampling faces additional pressure: the 2026-07-28 draft RC (SEP-2577) proposes deprecating it in favour of direct provider API calls.

**The security thread from session 1 lives inside every `description` field you write or consume.** Tool poisoning is prompt injection via the tool manifest: an attacker embeds directives in a `description` field; the LLM treats the manifest as authoritative and executes the embedded instructions alongside the legitimate call, with the user seeing expected output [[10]](https://www.practical-devsecops.com/mcp-tool-poisoning/). The rug-pull variant (a trusted tool updated post-approval) is especially insidious because manifests are not version-locked at install time. The MCPTox benchmark measured attack success rates above 60% across popular agents, highest 72% [[11]](https://www.mdpi.com/2624-800X/6/3/84). A 2026 disclosure found ~200,000 vulnerable MCP instances [[12]](https://www.practical-devsecops.com/mcp-security-vulnerabilities/). The defences — manifest pinning and signing, allowlists with version locks, semantic content scanning before consumption — are the authoring craft side of the security thread. This connects directly to session 1 and makes the two sessions feel like a coherent arc.

**Headless/SDK operation has a June 15, 2026 billing boundary that teams need to plan around.** `claude -p --bare` is the correct CI invocation — `--bare` skips all local config discovery and produces identical results across machines [[13]](https://code.claude.com/docs/en/headless). It will become the default for `-p` in a future release; CI pipelines without it are running on borrowed time. The Agent SDK monthly credit ($20–$200/user depending on plan tier) separates from interactive limits on June 15 [[14]](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan). Enterprise deployments average ~$13/dev/active day, $150–250/dev/month; agent teams (parallel Claude instances) use ~7× more tokens than standard sessions [[15]](https://code.claude.com/docs/en/costs). These numbers give the audience a forcing function: token budget discipline is not academic — it is what determines whether the tooling is sustainable at team scale.

The sharpest open question this expedition leaves: the 2026 MCP roadmap removes stateful session IDs to enable stateless horizontal scaling [[16]](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/), and the Tasks extension (SEP-1686) enables async agent-to-agent communication via MCP. When agents become both MCP clients and MCP servers in the same pipeline, what does the tool-poisoning threat model look like? The defences developed for human-to-agent flows may not compose cleanly when the "user" approving a manifest is another agent.
