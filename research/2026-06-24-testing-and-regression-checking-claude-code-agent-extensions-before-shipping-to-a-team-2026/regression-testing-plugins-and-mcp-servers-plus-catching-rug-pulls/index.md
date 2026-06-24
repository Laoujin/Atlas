---
title: "Regression-testing Claude Code plugins & MCP servers, and catching rug-pulls"
date: 2026-06-24
depth: deep
format: md
topic: "How to regression-test a Claude Code plugin or MCP server you maintain, and how to catch a rug-pull (a bundled dependency, skill, subagent, hook, or tool manifest silently changing behavior after install/update). Two sub-angles: (1) functional regression of a maintained MCP server/plugin — tool schemas, tool-list snapshotting, transport conformance, CI; (2) supply-chain integrity / rug-pull defense — tool-poisoning, manifest pinning, lockfiles, hashing/diffing, signing & provenance, registry developments, and what changed in 2026."
topic_raw: "How to REGRESSION-TEST a Claude Code PLUGIN or MCP SERVER you maintain, AND how to catch a RUG-PULL after install/update."
tags: [mcp, claude-code, plugins, supply-chain, testing, security, rug-pull, regression]
summary: "Two test surfaces — functional schema/contract drift and supply-chain rug-pulls — with the 2026 tooling that catches each, and an honest map of where the defenses are still missing."
citations: 49
reading_time_min: 18
cover: cover.svg
model: "Opus 4.8"
cost_usd: "sub"
duration_sec: 521
issue: 222
---

> **Decision.** Treat your extension as having *two* regressable surfaces. (1) **Functional contract** — snapshot `tools/list` and assert on it in CI ([Bellwether](https://github.com/dotsetlabs/bellwether) ⭐ 1 [[6]](https://github.com/dotsetlabs/bellwether), or hand-rolled with the MCP Inspector CLI [[1]](https://modelcontextprotocol.io/docs/tools/inspector) + run the official `modelcontextprotocol/conformance` GitHub Action [[3]](https://github.com/modelcontextprotocol/conformance)), and test tool *behaviour* through an in-memory client, not a chat window [[5]](https://jlowin.dev/blog/stop-vibe-testing-mcp-servers). (2) **Supply-chain integrity** — pin everything to a digest/version, hash tool descriptions and diff them on every update with [mcp-scan](https://github.com/snyk/agent-scan) ⭐ 2.6k [[28]](https://github.com/snyk/agent-scan), because MCP has *no* native re-approval when a tool's definition mutates after you approved it [[12]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks). The honest part: the integrity layer is immature — signing exists but was bypassed at scale in May 2026 [[31]](https://venturebeat.com/security/npm-sigstore-provenance-stolen-identity-audit-grid-2026), and Claude Code itself does not security-audit any plugin or MCP server you install [[43]](https://code.claude.com/docs/en/security).

## The two threat models

The question "does the plugin/MCP server I authored still do what it did before I push to my team?" splits into two failure classes that need different test machinery.

| Axis                  | Functional regression                                  | Rug-pull / supply-chain                                              |
|-----------------------|--------------------------------------------------------|---------------------------------------------------------------------|
| What breaks           | Tool schema/behaviour drifts → agent calls it wrong    | Definition or bundled code silently changes → trust → malice        |
| Trigger               | *Your* refactor, an SDK bump, a Claude Code version    | *Upstream's* update after you (or your agent) approved it           |
| Caught by             | Snapshot/contract tests, conformance, behavioural tests | Hashing+diff of manifests, pinning, provenance, scanners            |
| Native MCP support    | `tools.listChanged` notification [[10]](https://modelcontextprotocol.io/specification/2025-11-25/changelog) | None — no re-approval on tool-definition change [[12]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)[[14]](https://modelcontextprotocol-security.io/ttps/tool-poisoning/tool-mutation/) |

The two intersect: a *rug-pull is a malicious functional regression*. The same `tools/list` snapshot that catches your accidental param rename also catches an upstream description mutation — which is why the snapshot is the single highest-leverage control here [[24]](https://owasp.org/www-project-mcp-top-10/).

---

## Part 1 — Functional regression of a maintained MCP server / plugin

### 1.1 The contract surface to lock down

An MCP server's public contract is what `tools/list`, `resources/list`, and `prompts/list` return: tool names, descriptions, JSON Schemas for inputs, and (since the 2025-11-25 spec) output schemas and annotations. As of the 2025-11-25 revision, **JSON Schema 2020-12 is the default dialect** for all MCP schema definitions (SEP-1613), and request payloads were decoupled into standalone parameter schemas (SEP-1319) [[10]](https://modelcontextprotocol.io/specification/2025-11-25/changelog)[[11]](https://github.com/modelcontextprotocol/modelcontextprotocol). "A parameter renamed, a type modified, a tool removed — AI agents break silently" is the core failure mode, because nothing throws; the model just starts calling the tool wrong [[6]](https://github.com/dotsetlabs/bellwether).

### 1.2 Tools, by job

| Tool | What it tests | CI fit | Notes |
|---|---|---|---|
| [MCP Inspector](https://github.com/modelcontextprotocol/inspector) ⭐ 10k `--cli` [[2]](https://github.com/modelcontextprotocol/inspector) | Tool inventory + single tool calls; `--method tools/list`, `--tool-name`/`--tool-arg` [[1]](https://modelcontextprotocol.io/docs/tools/inspector) | ✓ scriptable | Validates output against schema via Ajv, same path as the SDK client [[1]](https://modelcontextprotocol.io/docs/tools/inspector) |
| [`modelcontextprotocol/conformance`](https://github.com/modelcontextprotocol/conformance) ⭐ 73 [[3]](https://github.com/modelcontextprotocol/conformance) | Protocol conformance: init handshake, lifecycle, tool/resource/prompt ops, OAuth flows, transport | ✓ official GitHub Action `@v0.1.11` | Has `--expected-failures` baseline for known gaps; emits JSON check files [[3]](https://github.com/modelcontextprotocol/conformance) |
| [FastMCP in-memory `Client`](https://gofastmcp.com/development/tests) [[4]](https://gofastmcp.com/development/tests) | Tool **behaviour** through the real protocol, no network | ✓ pytest, milliseconds | `Client(mcp)` direct connection; subprocess mode for STDIO isolation [[5]](https://jlowin.dev/blog/stop-vibe-testing-mcp-servers) |
| [Bellwether](https://github.com/dotsetlabs/bellwether) ⭐ 1 [[6]](https://github.com/dotsetlabs/bellwether) | Schema **drift** vs committed baseline | ✓ GitHub Action, exit codes | `init`→`check`, commit `bellwether-baseline.json`; brand-new (Show HN Jun 2026 [[7]](https://news.ycombinator.com/item?id=46846797)) |
| [PactFlow / SmartBear MCP](https://developer.smartbear.com/smartbear-mcp/docs/contract-testing-with-pactflow) [[8]](https://developer.smartbear.com/smartbear-mcp/docs/contract-testing-with-pactflow) | Consumer-driven contract testing | ✓ broker-based | Heavyweight; for teams already on Pact |

### 1.3 The pattern that does the most work: tool-list snapshotting

The cheapest, most durable regression test is a **golden snapshot of the tool manifest** committed to your repo, diffed in CI. Connect to the server, call `tools/list`, assert the exact schema against a stored JSON fixture; fail the build if a tool is added/removed, a param changes type, or a *description* is modified [[6]](https://github.com/dotsetlabs/bellwether)[[9]](https://dev.to/aws-heroes/testing-mcp-servers-the-five-gates-between-demo-and-production-2inf). FastMCP ships this via `inline-snapshot`: pytest auto-populates expected values on first run; `pytest --inline-snapshot=fix` updates them after an *intentional* change — making the snapshot diff a deliberate review gate, not a silent overwrite [[4]](https://gofastmcp.com/development/tests).

> Why descriptions matter as much as schemas: the description is part of the prompt the model reads. A description change is a behavioural change even when the JSON Schema is byte-identical — which is exactly the rug-pull vector in Part 2 [[12]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks). Snapshot the *whole* tool object, descriptions included.

### 1.4 Behaviour, not just shape — stop "vibe-testing"

Schema tests catch shape drift; they don't catch "the tool now returns wrong data." Run behavioural tests through an in-memory client so you exercise the real MCP serialization/dispatch layer without network flake — "your tests are confirming your server's behavior through the actual MCP interaction layer, without network latency" [[4]](https://gofastmcp.com/development/tests). jlowin's rule set: tests should be atomic, self-documenting, contract-focused (verify behaviour, not implementation), and refactor-friendly [[5]](https://jlowin.dev/blog/stop-vibe-testing-mcp-servers). The "Five Gates" framing (DEV/AWS Heroes): unit → contract → integration → conformance → security, each a CI gate between demo and production [[9]](https://dev.to/aws-heroes/testing-mcp-servers-the-five-gates-between-demo-and-production-2inf).

### 1.5 Does it still load across Claude Code versions? (plugins)

A plugin bundles skills, agents, hooks, MCP/LSP servers, and monitors into one versioned unit [[41]](https://code.claude.com/docs/en/plugins-reference). Two CI gates:

- **Structure validation.** `claude plugin validate ./my-plugin --strict` — `--strict` treats warnings (misspelled field, leftover field from another tool's manifest) as errors. Use it in CI to catch typos before publish even when the plugin would still load at runtime [[41]](https://code.claude.com/docs/en/plugins-reference). Anthropic ships a `plugin-validator` agent for this in `anthropics/claude-code` ⭐ 134k [[42]](https://github.com/anthropics/claude-code).
- **Version semantics are a footgun.** If `plugin.json` omits `version`, Claude Code falls back to the **git commit SHA — every commit is treated as a new version**, and the install directory name is a version string that changes on every update (which silently breaks a single root `SKILL.md` whose `name` you didn't pin) [[41]](https://code.claude.com/docs/en/plugins-reference). Always set `version` and bump it deliberately; users only receive updates when you do.

There is no public "test this plugin against three Claude Code versions" matrix runner in 2026 — you build it yourself with a version matrix in GitHub Actions invoking `claude plugin validate` plus your MCP/behavioural suite. Flag this as a genuine gap.

---

## Part 2 — Rug-pulls and supply-chain integrity

### 2.1 Anatomy of the rug-pull

A rug-pull: an MCP server (or skill/plugin) exposes benign, useful tools to earn a one-time approval, then **silently changes the tool definition, description, or behaviour after approval** — and the MCP spec has no mechanism to track tool-definition changes or force re-approval, so the agent keeps calling a tool whose meaning shifted underneath it [[12]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)[[15]](https://policylayer.com/attacks/mcp-rug-pull). Invariant Labs' original taxonomy:

- **Tool poisoning** — malicious instructions hidden in a tool description (often `<IMPORTANT>` tags), visible to the model but not the user; demoed making an `add` tool exfiltrate SSH keys [[12]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks).
- **Tool shadowing** — a poisoned tool rewrites the agent's behaviour toward *another* trusted server (e.g. forces an email tool to BCC the attacker) [[12]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks).
- **Post-approval mutation / rug-pull** — "a malicious server can change the tool description after the client has already approved it" [[12]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks)[[14]](https://modelcontextprotocol-security.io/ttps/tool-poisoning/tool-mutation/).

OWASP folds rug-pulls, schema poisoning, and shadowing under **Tool Poisoning** in the OWASP MCP Top 10 (beta in 2026, MCP01–MCP10), explicitly flagging "description drift" because users approve once and never re-review [[24]](https://owasp.org/www-project-mcp-top-10/)[[25]](https://cheatsheetseries.owasp.org/cheatsheets/MCP_Security_Cheat_Sheet.html). Reproducible PoCs live in `invariantlabs-ai/mcp-injection-experiments` ⭐ 197 [[22]](https://github.com/invariantlabs-ai/mcp-injection-experiments).

### 2.2 This is not theoretical — real 2025-2026 incidents

| Date | Incident | Mechanism | Ref / CVE |
|---|---|---|---|
| May 2025 | GitHub MCP prompt-injection | Malicious issue hijacks agent → exfiltrates private repos via a *legitimate* tool | [[20]](https://invariantlabs.ai/blog/mcp-github-vulnerability)[[21]](https://simonwillison.net/2025/May/26/github-mcp-exploited/) |
| Jul 2025 | `mcp-remote` OAuth proxy | OS command injection via crafted `authorization_endpoint`; 437k+ downloads | CVE-2025-6514 [[23]](https://authzed.com/blog/timeline-mcp-breaches) |
| Sep 2025 | **postmark-mcp** (classic rug-pull) | Benign for 15 versions (1.0.0–1.0.15), then v1.0.16 BCC'd every email to attacker; ~1,500 weekly installs | [[17]](https://snyk.io/blog/malicious-mcp-server-on-npm-postmark-mcp-harvests-emails/)[[18]](https://thehackernews.com/2025/09/first-malicious-mcp-server-found.html)[[19]](https://www.theregister.com/2025/09/29/postmark_mcp_server_code_hijacked/) |
| Oct 2025 | Smithery hosting | Path-traversal leaked builder's Docker config + Fly.io token (3,000+ apps) | CVE-2025-53967 [[23]](https://authzed.com/blog/timeline-mcp-breaches) |
| Feb 2026 | **ToxicSkills / ClawHub** | Audit of 3,984 agent skills: 36% had a vuln, 534 critical, 76 confirmed malicious payloads; 100% of malicious skills combined code + NL-instruction layers | [[26]](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) |
| Feb 2026 | Claude Code hook RCE | Malicious project files define hooks/`settings.json` that auto-run on repo open | CVE-2025-59536, CVE-2026-21852 [[45]](https://research.checkpoint.com/2026/rce-and-api-token-exfiltration-through-claude-code-project-files-cve-2025-59536/) |
| 2026 | **Hookify** (official marketplace plugin) | Reads repo rule files into the hook system's *trusted* system-message channel; 5/5 payloads leaked env vars against Opus 4.6. Anthropic closed it "working as designed" — the directory-trust dialog is the boundary | [[44]](https://pluto.security/blog/claude-extension-ecosystem-security-practitioner-guide/) |

The postmark-mcp pattern is the canonical rug-pull: **trust accrues across versions, malice ships in one**. Your defense has to be continuous, not at-install-once.

### 2.3 The defense stack

| Defense | What it catches | Strength | Limit / honesty |
|---|---|---|---|
| **Tool-description hashing** ([mcp-scan](https://github.com/snyk/agent-scan) ⭐ 2.6k Tool Pinning) [[13]](https://invariantlabs.ai/blog/introducing-mcp-scan)[[28]](https://github.com/snyk/agent-scan) | Post-approval description/schema mutation (rug-pull) | Purpose-built; `uvx mcp-scan@latest inspect`; tracks tool hashes over time across Claude Code, Cursor, Gemini CLI [[51]](https://mcpplaygroundonline.com/blog/mcp-security-tool-poisoning-owasp-top-10-mcp-scan) | Scan-mode *detects*; doesn't *prevent* in real time unless run as a gateway/proxy. Invariant acquired by Snyk Jun 2025 [[13]](https://invariantlabs.ai/blog/introducing-mcp-scan) |
| **Schema snapshot in CI** (Bellwether / FastMCP inline-snapshot) [[6]](https://github.com/dotsetlabs/bellwether)[[4]](https://gofastmcp.com/development/tests) | Drift in *your own* server + any pinned upstream you snapshot | Deterministic, free, no LLM | Only as fresh as your last CI run; not continuous monitoring [[7]](https://news.ycombinator.com/item?id=46846797) |
| **Version pinning** (npm `package-lock`, plugin `version`, MCP `dependencies` semver) [[41]](https://code.claude.com/docs/en/plugins-reference) | Surprise updates | Built-in; `{ "name": "x", "version": "~2.1.0" }` constraints | Pins the *reference*, not the *content* unless lockfile hashes |
| **Digest pinning** (`image@sha256:…`) [[40]](https://edu.chainguard.dev/chainguard/chainguard-images/how-to-use/container-image-digests/) | Tag re-push under same name | Immutable: content changes → hash changes [[38]](https://github.com/safedep/pinner-mcp) | Manual to maintain; tools: [pinner-mcp](https://github.com/safedep/pinner-mcp) ⭐ 12 [[38]](https://github.com/safedep/pinner-mcp), [dockerfile-pin](https://github.com/azu/dockerfile-pin) ⭐ 69 [[39]](https://github.com/azu/dockerfile-pin) |
| **Provenance / signing** (npm + Sigstore, trusted publishing) [[29]](https://docs.npmjs.com/generating-provenance-statements/)[[30]](https://github.blog/security/supply-chain-security/introducing-npm-package-provenance/) | "Was this built in the claimed CI from the claimed source?" | Public transparency log; `cosign`-verifiable [[32]](https://docs.npmjs.com/trusted-publishers/) | **Bypassed at scale**: May 2026, 633 malicious npm versions passed Sigstore verification via a compromised maintainer account — signing proves build provenance, not publish authorization [[31]](https://venturebeat.com/security/npm-sigstore-provenance-stolen-identity-audit-grid-2026) |
| **Registry namespace verification** (MCP Registry) [[33]](https://modelcontextprotocol.io/registry/about)[[34]](https://github.com/modelcontextprotocol/registry) | Name-squatting/impersonation | Reverse-DNS names tied to verified GitHub/DNS (`io.github.user/server`) [[35]](https://glama.ai/blog/2026-01-24-official-mcp-registry-serverjson-requirements) | Verifies *ownership of the name*, not *intent of the code* |
| **Manifest-diff on update** (Claude Code `SessionStart` hook pattern) [[41]](https://code.claude.com/docs/en/plugins-reference) | Bundled-dependency manifest changing across plugin update | Native pattern: compare bundled manifest to a copy in `${CLAUDE_PLUGIN_DATA}`, reinstall when they differ | DIY; detects dependency-manifest drift, not arbitrary code changes |

The blunt takeaway: **no single layer is sufficient, and the cryptographic layer (signing) is the weakest link precisely where people assume it's strongest** [[31]](https://venturebeat.com/security/npm-sigstore-provenance-stolen-identity-audit-grid-2026). Defense-in-depth = pin to digest + hash-diff tool manifests on every update + snapshot the contract in CI + run a scanner.

### 2.4 The native MCP signal — and why you can't lean on it

The spec defines `tools.listChanged: true` → server SHOULD send `notifications/tools/list_changed` → client SHOULD re-issue `tools/list` [[10]](https://modelcontextprotocol.io/specification/2025-11-25/changelog). That tells you the list *changed*; it carries **no re-approval gate and no integrity check** — a rug-pull can mutate a description and either fire the notification or not. Worse, the handler has been buggy in practice: a documented 2026 issue had Claude Desktop ignoring `list_changed` until a full restart [[48]](https://github.com/anthropics/claude-code/issues/13646), and Claude Code's MCP docs say it auto-refreshes on the notification [[49]](https://code.claude.com/docs/en/mcp). Treat `listChanged` as a *hint to re-hash*, not a defense.

---

## Part 3 — What changed in 2026 (flag everything)

| Change | What shipped | Why it matters for testing/integrity |
|---|---|---|
| **MCP spec 2025-11-25** | JSON Schema 2020-12 default (SEP-1613); standalone param schemas (SEP-1319); tool/resource icons (SEP-973); OIDC discovery + incremental scope consent (SEP-835); experimental tasks (SEP-1686); HTTP 403 on bad Origin [[10]](https://modelcontextprotocol.io/specification/2025-11-25/changelog) | Your schema snapshots must target 2020-12; conformance tests must cover the new lifecycle [[11]](https://github.com/modelcontextprotocol/modelcontextprotocol) |
| **Official MCP Registry** | Preview Sep 2025; API freeze v0.1 Oct 24 2025; namespace verification via GitHub/DNS/HTTP challenge; powers version pinning + install provenance [[33]](https://modelcontextprotocol.io/registry/about)[[35]](https://glama.ai/blog/2026-01-24-official-mcp-registry-serverjson-requirements) | Gives you a canonical `server.json` to pin against; GA still pending |
| **Conformance suite + GitHub Action** | `modelcontextprotocol/conformance` ⭐ 73, runnable in CI [[3]](https://github.com/modelcontextprotocol/conformance) | First *official* protocol-level regression gate |
| **Claude Code plugin marketplaces** | Official curated `claude-plugins-official` (101 plugins, Mar 2026); community marketplace passes automated screening; third-party unscreened [[46]](https://securityboulevard.com/2026/06/7-claude-code-plugins-from-the-marketplace-worth-your-time/)[[47]](https://claudemarketplaces.com/) | Anthropic "does not security-audit or manage any MCP server" and "cannot verify [plugins] work as intended" — trust is on you [[43]](https://code.claude.com/docs/en/security) |
| **Docker MCP Catalog** | Signed images + provenance + SBOMs for catalog servers [[36]](https://docs.docker.com/ai/mcp-catalog-and-toolkit/)[[37]](https://github.com/docker/mcp-registry) | A pinnable, signed distribution path for server images |
| **OWASP MCP Top 10 + Agentic Skills Top 10** | Both in 2026; rug-pull/tool-poisoning is MCP's #1 class [[24]](https://owasp.org/www-project-mcp-top-10/)[[27]](https://owasp.org/www-project-agentic-skills-top-10/) | Gives you a test checklist mapped to named risks |
| **npm trusted publishing tightened** | Post-May-2026 trusted-publisher configs must explicitly select allowed actions [[32]](https://docs.npmjs.com/trusted-publishers/) — reaction to the Sigstore-bypass wave [[31]](https://venturebeat.com/security/npm-sigstore-provenance-stolen-identity-audit-grid-2026) | Provenance is necessary, not sufficient |

---

## Part 4 — Practical checklist for shipping an extension to your team

1. **Snapshot the contract.** Commit a `tools/list` (+ resources/prompts) golden file; diff in CI. Include descriptions. Update only via explicit `--inline-snapshot=fix` / baseline bump as a reviewed change [[4]](https://gofastmcp.com/development/tests)[[6]](https://github.com/dotsetlabs/bellwether).
2. **Behavioural tests** through an in-memory `Client`, per tool: valid ranges, error paths, output shape [[5]](https://jlowin.dev/blog/stop-vibe-testing-mcp-servers).
3. **Protocol conformance** via the official Action, with an `--expected-failures` baseline for known gaps [[3]](https://github.com/modelcontextprotocol/conformance).
4. **Plugin gate:** `claude plugin validate --strict` in CI; set an explicit `version`; pin `dependencies` with semver [[41]](https://code.claude.com/docs/en/plugins-reference).
5. **Pin upstream to digests**, not tags; lockfile with hashes for every bundled dependency [[40]](https://edu.chainguard.dev/chainguard/chainguard-images/how-to-use/container-image-digests/)[[38]](https://github.com/safedep/pinner-mcp).
6. **Hash-diff on every update.** Run `mcp-scan` against your config in CI and (ideally) as a runtime gateway; add a `SessionStart` manifest-diff hook for bundled deps [[13]](https://invariantlabs.ai/blog/introducing-mcp-scan)[[41]](https://code.claude.com/docs/en/plugins-reference).
7. **Prefer signed/registry-namespaced sources**, but assume signing can be bypassed — keep the hash-diff regardless [[35]](https://glama.ai/blog/2026-01-24-official-mcp-registry-serverjson-requirements)[[31]](https://venturebeat.com/security/npm-sigstore-provenance-stolen-identity-audit-grid-2026).
8. **Least privilege + isolation** for the agent runtime (scoped tokens, one-repo-per-session, dev containers) — the GitHub-MCP heist showed broad PATs turn any legit tool into an exfil channel [[20]](https://invariantlabs.ai/blog/mcp-github-vulnerability)[[43]](https://code.claude.com/docs/en/security).

## Where the answers are genuinely missing (2026)

- **No re-approval on tool mutation** in the MCP spec or Claude Code — detection is bolt-on, not built-in [[12]](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks).
- **No cross-Claude-Code-version test matrix runner** for plugins — DIY in CI.
- **Signing ≠ authorization** — Sigstore/provenance was bypassed at scale May 2026 [[31]](https://venturebeat.com/security/npm-sigstore-provenance-stolen-identity-audit-grid-2026).
- **Detection tools are young/thin** — Bellwether is days old (⭐ 1) [[6]](https://github.com/dotsetlabs/bellwether); mcp-scan's hashing internals are under-documented [[13]](https://invariantlabs.ai/blog/introducing-mcp-scan). Skills supply chain is a confirmed active-attack frontier with no mature gatekeeper [[26]](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/).

The defensible posture isn't a product — it's the discipline: **snapshot the contract, pin to content, re-hash on every update, and never trust an install-time approval to hold.**
