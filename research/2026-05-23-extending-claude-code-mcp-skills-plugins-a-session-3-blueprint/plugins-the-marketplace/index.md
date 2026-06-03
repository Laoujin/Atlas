---
title: "Claude Code Plugins & the Marketplace — talk-prep brief"
date: 2026-05-23
depth: standard
format: md
topic: "Plugins & the Marketplace"
topic_raw: "Plugins & the Marketplace"
issue: 57
tags: [claude-code, plugins, marketplace, ecosystem, developer-tools, security]
summary: "What plugins actually are, how the official + community marketplaces work, the few that earn their keep, and the trust footgun to flag in any 1–2 hour deep-dive."
citations: 21
reading_time_min: 10
cover: cover.svg
cost_usd: 2.23
duration_sec: 402
model: "Opus 4.7"
---

> **TL;DR for the session.** A Claude Code *plugin* is a packaging unit — a directory bundling any of skills, agents, slash commands, hooks, MCP servers, LSP servers — installed via `/plugin` from a *marketplace* (a `marketplace.json` catalog hosted on GitHub or anywhere reachable). The **official** Anthropic marketplace ships automatically (~101 plugins, 33 Anthropic + 68 partner as of May 2026) [[20]](https://knightli.com/en/2026/05/23/claude-plugins-official-claude-code-plugin-directory/); the **community** marketplace is one `/plugin marketplace add` away, with submissions gated by automated safety screening [[7]](https://github.com/anthropics/claude-plugins-community). Spend ~25 min on anatomy and install flow, ~15 min on building/distributing your own, and ~15 min on the trust boundary — plugins execute arbitrary code with the user's privileges, and there is already a CVE history to point to [[13]](https://blog.checkpoint.com/research/check-point-researchers-expose-critical-claude-code-flaws/).

This brief is the third in a series (prior: AI Security, Skills). It assumes the audience already understands what a Skill is and links plugins back to the security material where natural.

## 1. What a plugin is — and isn't

Anthropic announced plugins on **9 Oct 2025** as a lightweight way to package and share the building blocks people were already cobbling together [[1]](https://claude.com/blog/claude-code-plugins). The mental model the docs push, and the line worth repeating verbatim in the talk:

> Plugins are the distribution format; skills are the content. You install plugins; you use skills. [[10]](https://www.agensi.io/learn/claude-code-plugin-marketplace-guide)

A plugin can bundle any combination of:

| Component         | Lives in                  | What it does                                                                                          |
| :---------------- | :------------------------ | :---------------------------------------------------------------------------------------------------- |
| Skills            | `skills/<name>/SKILL.md`  | Model-invoked capability with a YAML `description` Claude reads to decide when to use it [[3]][p3]    |
| Slash commands    | `commands/`               | User-invoked `/plugin-name:foo` workflows [[9]][p9]                                                   |
| Agents            | `agents/`                 | Specialised sub-agent definitions [[3]][p3]                                                           |
| Hooks             | `hooks/hooks.json`        | Event handlers — `SessionStart`, `PreToolUse`, `Stop`, etc. [[9]][p9]                                 |
| MCP servers       | `.mcp.json`               | Pre-configured external tool integrations [[9]][p9]                                                   |
| LSP servers       | `.lsp.json`               | Language-server bindings for real-time code intelligence [[3]][p3]                                    |
| Background monitors | `monitors/monitors.json` | Background `tail -F`-style watchers that push notifications into the session [[3]][p3]              |
| Default settings  | `settings.json`           | Plugin-scoped defaults; only `agent` + `subagentStatusLine` keys honoured today [[3]][p3]             |

[p3]: https://code.claude.com/docs/en/plugins
[p9]: https://github.com/anthropics/claude-code/blob/main/plugins/README.md

The whole thing is identified by `.claude-plugin/plugin.json`:

```json
{
  "name": "my-first-plugin",
  "description": "Greets the user",
  "version": "1.0.0",
  "author": { "name": "Your Name" }
}
```

Only `name` is truly required; `version` is optional but recommended — without it, every git commit counts as a new version [[3]](https://code.claude.com/docs/en/plugins).

**Common landmine to demo live:** `commands/`, `agents/`, `skills/`, `hooks/` go at the plugin **root**, not inside `.claude-plugin/`. The docs flag this explicitly [[3]](https://code.claude.com/docs/en/plugins).

## 2. The marketplaces — three tiers, one schema

A *marketplace* is just a git repo (or any URL) with a `.claude-plugin/marketplace.json` listing plugins, each with `name`, `description`, `source`, and `category` [[4]](https://code.claude.com/docs/en/plugin-marketplaces). The schema is published at `schemastore.org/claude-code-marketplace.json`.

| Tier                     | Name on disk             | Added by user?          | Curation                                                | Plugin count (May 2026)                                                                 |
| :----------------------- | :----------------------- | :---------------------- | :------------------------------------------------------ | :-------------------------------------------------------------------------------------- |
| **Official**             | `claude-plugins-official` | ✓ auto, on first launch | Anthropic's discretion; no application process [[3]][p3] | ~101 (33 Anthropic + 68 partner) [[20]][p20]                                            |
| **Community**            | `claude-community`        | ✗ manual `/plugin marketplace add` | Auto-validated + safety-screened; pinned to commit SHA [[2]][p2] | Open submission via `claude.ai/settings/plugins/submit` [[3]][p3]                       |
| **Third-party / private** | any GitHub/git/URL/path  | ✗ manual                | None — caveat emptor                                    | 2,500+ catalogued at [claudemarketplaces.com](https://claudemarketplaces.com/) [[14]][p14] |

[p2]: https://code.claude.com/docs/en/discover-plugins
[p20]: https://knightli.com/en/2026/05/23/claude-plugins-official-claude-code-plugin-directory/
[p14]: https://claudemarketplaces.com/

**Partner integrations in the official marketplace** (worth name-dropping when introducing): [GitHub](https://github.com), [GitLab](https://gitlab.com), [Atlassian](https://www.atlassian.com), [Asana](https://asana.com), [Linear](https://linear.app), [Notion](https://notion.so), [Figma](https://figma.com), [Vercel](https://vercel.com), [Firebase](https://firebase.google.com), [Supabase](https://supabase.com), [Slack](https://slack.com), [Sentry](https://sentry.io), [Stripe](https://stripe.com), [Playwright](https://playwright.dev), [Auth0](https://auth0.com), [Datadog](https://datadoghq.com), [Cloudflare](https://cloudflare.com), and an `aws-*` family (`aws-core`, `aws-amplify`, `aws-serverless`, …) [[6]](https://github.com/anthropics/claude-plugins-official/blob/main/.claude-plugin/marketplace.json) [[20]](https://knightli.com/en/2026/05/23/claude-plugins-official-claude-code-plugin-directory/).

## 3. The install flow (live-demo material)

The whole UX is one slash command:

```
/plugin                                       # opens the tabbed manager (Discover / Installed / Marketplaces / Errors)
/plugin marketplace add anthropics/claude-plugins-community
/plugin install commit-commands@claude-plugins-official
/reload-plugins                               # picks up changes without restarting
```

Three install **scopes** to call out — they map cleanly to the standard Claude Code settings tiers:

| Scope     | Persisted in                | Use it for                                              |
| :-------- | :-------------------------- | :------------------------------------------------------ |
| `user`    | `~/.claude/settings.json`   | Personal toolkit across all projects (default)          |
| `project` | `.claude/settings.json` (committed) | Team-shared via version control                  |
| `local`   | `.claude/settings.local.json` (gitignored) | "Just me, just here"                       |

For teams, the trick worth showing is `extraKnownMarketplaces` in `.claude/settings.json` — when a teammate trusts the repo folder, Claude Code prompts them to install your marketplace automatically [[2]](https://code.claude.com/docs/en/discover-plugins):

```json
{
  "extraKnownMarketplaces": {
    "my-team-tools": { "source": { "source": "github", "repo": "your-org/claude-plugins" } }
  }
}
```

**Recent UX shipped in May 2026** (mention in passing as proof the surface is still moving): v2.1.137 added type-to-filter in `/plugin` and `/skills`; v2.1.143 surfaces a **Context cost** estimate per plugin (tokens-per-turn); v2.1.144 shows last-updated; v2.1.145 shows a "Will install" section listing every component before you commit [[21]](https://releasebot.io/updates/anthropic/claude-code) [[2]](https://code.claude.com/docs/en/discover-plugins).

## 4. Plugins worth a slide

Don't recommend the whole shelf — pick the ones that earn their keep. Drawing from the official marketplace's own dev workflows [[2]](https://code.claude.com/docs/en/discover-plugins) and one of the only honest reviews [[11]](https://buildtolaunch.substack.com/p/best-claude-code-plugins-tested-review):

| Plugin                          | Marketplace                | What it gives Claude                                                | Why include it                                                                       |
| :------------------------------ | :------------------------- | :------------------------------------------------------------------ | :----------------------------------------------------------------------------------- |
| `commit-commands`               | `claude-plugins-official`  | `/commit`, `/commit-push-pr`, `/clean_gone` git skills              | Anthropic's reference example — installs cleanly, narrates well [[2]][p2]            |
| `pr-review-toolkit`             | `claude-plugins-official`  | Five parallel review agents (compliance, bugs, context, …)          | Concrete multi-agent demo without leaving the CLI [[2]][p2]                          |
| `plugin-dev`                    | `claude-plugins-official`  | `/plugin-dev:create-plugin` + agent-creator/validator/skill-reviewer | The meta-plugin; use it to live-build a plugin during the talk [[9]][p9]             |
| `agent-sdk-dev`                 | `claude-plugins-official`  | Skills/agents for building with the Claude Agent SDK                 | Bridges into your audience's own automation work [[2]][p2]                           |
| One LSP pack (`typescript-lsp` / `pyright-lsp` / `rust-analyzer-lsp`) | `claude-plugins-official` | Diagnostics + go-to-def after every edit | Single highest-leverage install for IDE-grade feedback in-terminal [[2]][p2]         |
| `security-guidance`             | `claude-plugins-official`  | `PreToolUse` hook warning on injection / XSS / eval / unsafe deserialize | Direct callback to the AI Security session [[9]][p9]                            |
| [`wshobson/agents`](https://github.com/wshobson/agents) ⭐ 36k | third-party | 80+ specialised sub-agents [[15]][p15]            | The headline community pack — but show how to inspect before installing             |
| [`davila7/claude-code-templates`](https://github.com/davila7/claude-code-templates) ⭐ 28k | third-party | Templating CLI for plugins / agents / commands [[16]][p16] | Useful as a survey of what people are actually building          |

[p15]: https://github.com/wshobson/agents
[p16]: https://github.com/davila7/claude-code-templates

Honest aside from a hands-on review: of 10 popular plugins tested, only 4 were judged "worth keeping" — and the failures were not subtle (one was off by >2× on a basic factual lookup) [[11]](https://buildtolaunch.substack.com/p/best-claude-code-plugins-tested-review). Treat the marketplace like npm, not the App Store.

## 5. Build & ship one in 10 minutes (live-code section)

The whole quickstart fits on one slide [[3]](https://code.claude.com/docs/en/plugins):

```bash
mkdir -p my-first-plugin/.claude-plugin my-first-plugin/skills/hello
cat > my-first-plugin/.claude-plugin/plugin.json <<'JSON'
{ "name": "my-first-plugin", "description": "demo", "version": "0.1.0" }
JSON
cat > my-first-plugin/skills/hello/SKILL.md <<'MD'
---
description: Greet $ARGUMENTS warmly.
---
Greet the user named "$ARGUMENTS" and ask how you can help.
MD
claude --plugin-dir ./my-first-plugin    # loads the plugin for this session only
# /my-first-plugin:hello Alex
```

Distribution path (mention, don't demo end-to-end):

1. Push the plugin into a git repo, add a `.claude-plugin/marketplace.json` next to it listing your plugins with their `source` paths.
2. Run `claude plugin validate` locally — the same check the community pipeline runs [[3]](https://code.claude.com/docs/en/plugins).
3. Either tell users `/plugin marketplace add your-org/your-repo`, or submit to community via the in-app form at [claude.ai/settings/plugins/submit](https://claude.ai/settings/plugins/submit).
4. CI auto-bumps the pinned commit SHA in the community catalog; nightly sync to `marketplace.json` [[3]](https://code.claude.com/docs/en/plugins).

**Trip-wire** worth flagging: relative paths in `marketplace.json` work only when the marketplace is added via git. If you publish a bare `marketplace.json` at an HTTPS URL, relative `source` paths silently fail to resolve [[4]](https://code.claude.com/docs/en/plugin-marketplaces).

## 6. The trust boundary — the bit that earns the slot in a security-flavoured series

This is the section that justifies plugins being slide-three after AI Security. The mechanism, in one sentence: **a plugin executes arbitrary code on the user's machine with their user privileges, just like an npm package** [[2]](https://code.claude.com/docs/en/discover-plugins). The official docs say so in a `<Warning>` box:

> Make sure you trust a plugin before installing it. Anthropic does not control what MCP servers, files, or other software are included in plugins and cannot verify that they work as intended. [[2]](https://code.claude.com/docs/en/discover-plugins)

Concrete incidents to anchor the abstraction:

| Date         | Issue                                              | What broke                                                                                          | Source                                                            |
| :----------- | :------------------------------------------------- | :-------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------- |
| Oct 2025     | **CVE-2025-59536** (CVSS 8.7, patched Oct 2025)   | RCE via hooks / MCP config in `.claude/settings.json`, *before* trust dialog appeared              | [Check Point research](https://blog.checkpoint.com/research/check-point-researchers-expose-critical-claude-code-flaws/) [[13]] |
| Jan 2026     | **CVE-2026-21852** (CVSS 5.3, patched Jan 2026)   | API key exfiltration via `ANTHROPIC_BASE_URL` override                                              | [Check Point research](https://blog.checkpoint.com/research/check-point-researchers-expose-critical-claude-code-flaws/) [[13]] |
| Apr 2026     | "TrustFall" convention                             | Cloning + opening a hostile repo could trigger code execution before any explicit consent          | [Dark Reading](https://www.darkreading.com/application-security/trustfall-exposes-claude-code-execution-risk) [[19]] |
| Q1 2026      | Marketplace **dependency hijack** (SentinelOne)    | Malicious plugin silently reroutes `pip install` to attacker-controlled mirror; persists across sessions | [SentinelOne blog](https://www.sentinelone.com/blog/marketplace-skills-and-dependency-hijack-in-claude-code/) [[12]] |

The defensive posture to recommend in the talk:

- Treat plugins like dependencies — review the source, pin versions, and prefer the official + community tiers over arbitrary GitHub URLs [[12]](https://www.sentinelone.com/blog/marketplace-skills-and-dependency-hijack-in-claude-code/).
- Use **managed marketplace restrictions** (admin-controlled allowlist) for organisations [[2]](https://code.claude.com/docs/en/discover-plugins).
- v2.1.145's "Will install" section finally shows the exact commands/agents/skills/hooks/MCP/LSP a plugin will add before you confirm — make use of it [[21]](https://releasebot.io/updates/anthropic/claude-code).
- Auto-update is on by default for official marketplaces, off for third-party. Don't blindly flip it on for community sources [[2]](https://code.claude.com/docs/en/discover-plugins).
- Disable auto-update entirely with `DISABLE_AUTOUPDATER=1`; if you want plugin updates but not Claude Code itself updating, add `FORCE_AUTOUPDATE_PLUGINS=1` [[2]](https://code.claude.com/docs/en/discover-plugins).

## 7. Suggested session shape (60–90 min)

| Block                                    | Time      | Demo to run                                                                       |
| :--------------------------------------- | :-------- | :-------------------------------------------------------------------------------- |
| 1. Why plugins exist; plugin ≠ skill      | 10 min    | Open `/plugin`, walk the four tabs                                                |
| 2. Anatomy + manifest                     | 15 min    | Inspect `commit-commands` source in the official repo                             |
| 3. Install flow + scopes                  | 10 min    | `/plugin install commit-commands@claude-plugins-official` at user scope           |
| 4. Build one live                         | 15 min    | The `mkdir → plugin.json → SKILL.md → --plugin-dir` flow from §5                  |
| 5. Distributing (marketplace.json + team) | 10 min    | Show a real-world `marketplace.json` + `extraKnownMarketplaces` setup             |
| 6. Trust boundary + CVEs                  | 15 min    | Walk through SentinelOne's hijack scenario; demo `claude --plugin-dir` sandboxing |
| 7. Q&A / picks                            | 10–15 min | Have `wshobson/agents` and `plugin-dev` ready to install on request               |

## 8. Stats and links worth name-dropping

- Official marketplace: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) ⭐ 26k (May 2026) [[5]](https://github.com/anthropics/claude-plugins-official)
- Community marketplace: [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) ⭐ 119 (May 2026) [[7]](https://github.com/anthropics/claude-plugins-community)
- Main repo: [anthropics/claude-code](https://github.com/anthropics/claude-code) ⭐ 126k (May 2026) [[8]](https://github.com/anthropics/claude-code)
- Community directory: [claudemarketplaces.com](https://claudemarketplaces.com) — 6,700+ skills, 2,500+ marketplaces, 840+ MCP servers indexed [[14]](https://claudemarketplaces.com/)
- Top community plugin set: [obra/superpowers](https://github.com/obra/superpowers) ⭐ 204k [[17]](https://github.com/obra/superpowers)
- Other major third-party: [wshobson/agents](https://github.com/wshobson/agents) ⭐ 36k [[15]](https://github.com/wshobson/agents), [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) ⭐ 28k [[16]](https://github.com/davila7/claude-code-templates)
- Plugin browsing UI: `claude.com/plugins`
- The Firecrawl "top 10 for 2026" round-up is a useful complement to the audience's homework list [[18]](https://www.firecrawl.dev/blog/best-claude-code-plugins).
