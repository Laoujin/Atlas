---
title: "Project Health & Bus Factor: Measure and Reduce Key-Person Risk"
date: 2026-06-07
depth: standard
format: md
topic: "Project health & bus-factor"
topic_raw: "Project health & bus-factor"
issue: 198
tags: [devops, open-source, project-management, risk, security, team-health]
summary: "How to measure bus factor from git history, which frameworks track project health, and practical strategies to raise a dangerously low number — with lessons from the XZ Utils supply chain attack."
citations: 20
reading_time_min: 5
cover: cover.svg
model: "Sonnet 4.6"
cost_usd: "sub"
duration_sec: 420
cost_usd: 1.33
duration_sec: 525
model: "Sonnet 4.6"
---

> **Decision:** If your project's bus factor is 1, treat it as a P0 risk. Measure it today with `truckfactor` (pip-installable CLI) or `git-truck` (visual, `npx -y git-truck`). Track CHAOSS Contributor Absence Factor over time. Target ≥ 3 for any production-critical system. The 2024 XZ Utils attack was bus factor 1 in practice — one burned-out maintainer plus one patient attacker came within a hair of compromising SSH on every major Linux distribution [[15]](https://www.softwareseni.com/the-xz-utils-backdoor-cve-2024-3094-and-the-multi-year-social-engineering-campaign-behind-it/).

## What is Bus Factor?

Bus factor — also called truck factor, lottery factor, or circus factor — is **the minimum number of team members who must suddenly disappear before a project stalls** due to knowledge loss [[1]](https://en.wikipedia.org/wiki/Bus_factor). The concept dates to 1994 discussions about Python's sole dependence on Guido van Rossum [[12]](https://www.cesarsotovalero.net/blog/bus-factor-a-human-centered-risk-metric-in-the-software-supply-chain.html). Crucially, it counts only *irreplaceable* personnel — losing a replaceable member doesn't move the number.

| Bus factor | Risk level | Practical meaning                              |
|:----------:|:----------:|------------------------------------------------|
| 1          | Critical   | Single departure stalls the project            |
| 2          | High       | Either expert lost → immediate crisis          |
| 3–4        | Medium     | Survivable; room to improve                    |
| 5+         | Healthy    | Team absorbs departures without disruption     |

## The Industry Numbers

Empirical data is sobering. A 2015 study of 133 popular GitHub projects found [[1]](https://en.wikipedia.org/wiki/Bus_factor):

- **65% had bus factor ≤ 2**
- **Less than 10% had bus factor > 10**

Longitudinal follow-up is worse: in **16% of real projects all key engineers eventually departed**, and only **41% of those continued meaningful development** afterwards — recovery typically took up to 6 person-months, and some subsystems required complete rewrites [[18]](https://dl.acm.org/doi/10.1145/3510457.3513082).

[OpenSSF Scorecard](https://github.com/ossf/scorecard) ⭐ 5.5k (Jun 2026) requires bus factor ≥ 2 for its best practices badge [[8]](https://github.com/ossf/scorecard).

## How to Measure

### Degree of Authorship (DOA) — the standard algorithm

Introduced in a 2015 IEEE study [[14]](https://ieeexplore.ieee.org/document/7081864/), DOA scores each developer per file by weighting three factors:

1. Did they originally create the file?
2. How frequently have they modified it (last 90 days)?
3. What fraction of the file's total changes do they own?

A developer is an *author* when their DOA score exceeds 0.75 of the maximum DOA for that file [[2]](https://contributoriq.com/blog/what-is-bus-factor-how-to-calculate-measure). Bus factor = the smallest set of authors who together cover 50%+ of all files.

### Simpler proxy (good enough for most teams)

Rank contributors by lines changed. The minimum number of people whose combined contributions exceed 50% of all changed lines is a reasonable proxy [[11]](https://livablesoftware.com/calculate-bus-factor-software-project/).

**Key caveat:** project-level bus factor often masks higher concentration in critical subsystems. Analyse auth/, CI/, data-layer/ separately [[17]](https://arxiv.org/html/2401.03303v1).

## Tools

| Tool              | Stars   | Language | Install                | What it does                                              |
|-------------------|--------:|----------|------------------------|-----------------------------------------------------------|
| [git-truck][5]    | ⭐ 743  | Node     | `npx -y git-truck`     | Visual: shows who worked where/when; no cloud tracking    |
| [Truck-Factor][7] | ⭐ 239  | Java     | Shell + AWK + Java     | Academic DOA algorithm; matches peer-reviewed methodology |
| [truckfactor][6]  | ⭐ 33   | Python   | `pip install truckfactor` | CLI number: fastest path to a result                   |
| [Scorecard][8]    | ⭐ 5.5k | Go       | `scorecard --repo=URL` | 18 security checks incl. contributor diversity            |
| [Knowledge Islands][13] | — | —      | GitHub web UI          | Truck factor at project/module/file granularity           |

[5]: https://github.com/git-truck/git-truck
[6]: https://github.com/HelgeCPH/truckfactor
[7]: https://github.com/aserg-ufmg/Truck-Factor
[8]: https://github.com/ossf/scorecard
[13]: https://arxiv.org/abs/2408.08733

**Recommended starting point:** `truckfactor` for a quick number; `git-truck` to explore *which files* are concentration points and decide where to focus cross-training.

## Project Health Frameworks

### CHAOSS Starter Model

[CHAOSS](https://chaoss.community/) [[19]](https://chaoss.community/) is a Linux Foundation project defining shared metrics for open source community health. Its [Starter Project Health](https://chaoss.community/kb/metrics-model-starter-project-health/) model [[3]](https://chaoss.community/kb/metrics-model-starter-project-health/) defines four foundational metrics:

| Metric                        | What it measures                                    | Bus factor relevance            |
|-------------------------------|-----------------------------------------------------|---------------------------------|
| **Contributor Absence Factor** | Smallest number of people making 50% of contributions | Direct bus factor proxy       |
| **Time to First Response**    | Issue/PR open → first human response               | Maintainer capacity signal      |
| **Change Request Closure Ratio** | Open vs. closed PRs over a period              | Project responsiveness          |
| **Release Frequency**         | How often releases ship                             | Project maturity / momentum     |

VMware's internal guideline targets responses within two business days; declining closure ratios signal maintainer overload — an early-warning sign for bus factor collapse [[3]](https://chaoss.community/kb/metrics-model-starter-project-health/).

### CHAOSS OSS Viability Signals [[4]](https://chaoss.community/kb/metrics-model-oss-project-viability-community/)

CHAOSS's viability model adds committer trends (90% drop in 3 months = dying project), forks, and libyears (dependency freshness as a shared-maintenance proxy).

### OpenSSF Scorecard [[9]](https://scorecard.dev/)

Scorecard automates 18 checks scored 0–10, compiling into a weighted aggregate. Relevant to bus factor: the **Contributors** check flags projects where fewer than 2 distinct companies have committed recently; **Code-Review** flags whether all recent changes were reviewed by someone other than the author [[9]](https://scorecard.dev/).

## The XZ Utils Warning Shot

In March 2024, CVE-2024-3094 (CVSS 10.0) was discovered in XZ Utils, a compression library present in virtually every Linux distribution [[15]](https://www.softwareseni.com/the-xz-utils-backdoor-cve-2024-3094-and-the-multi-year-social-engineering-campaign-behind-it/). An attacker spent two years building trust, then exploited the burned-out single maintainer — exhausted and feeling unsupported — to gain co-maintainer access and insert a backdoor into OpenSSH authentication paths.

CISA's response: *"The burden of security shouldn't fall on an individual open source maintainer — companies consuming open source software must contribute back, either financially or through developer time, to ensure healthy and diverse maintainer communities resilient to burnout."* [[16]](https://www.cybersecuritydive.com/news/cisa-xz-utils-open-source-support/713196/)

A newer risk vector: "bus factor 0" — LLM-generated code that no human has read or understood — creates knowledge ownership vacuums that look like working software but carry hidden fragility [[20]](https://ericphanson.com/blog/2025/bus-factor-0/).

## How to Improve

| Strategy                              | Impact | Cost   | When to apply                    |
|---------------------------------------|:------:|:------:|----------------------------------|
| Pair programming on critical paths    | High   | Medium | Ongoing                          |
| Mandatory code review by non-author   | High   | Low    | Always                           |
| Ownership rotation (quarterly)        | High   | Medium | Planned sprint allocation        |
| Architecture decision records (ADRs)  | Medium | Low    | Before each significant design   |
| Brown-bag sessions on opaque modules  | Medium | Low    | Monthly                          |
| Designated formal backups per role    | Medium | Low    | During onboarding                |
| Cross-training budget (shadowing)     | Medium | High   | Annual planning                  |

Key principle: documentation captures *what*, but only pair programming and rotation build the tacit knowledge that actually raises bus factor [[2]](https://contributoriq.com/blog/what-is-bus-factor-how-to-calculate-measure) [[10]](https://swimm.io/learn/developer-experience/what-is-the-bus-factor-why-it-matters-and-how-to-increase-it). For open source dependencies, [Knowledge Islands](https://arxiv.org/abs/2408.08733) [[13]](https://arxiv.org/abs/2408.08733) can surface which upstream subsystems carry concentrated risk before you adopt them.

## Making It a Repeatable Practice

1. **Run monthly**: `truckfactor <repo>` and record the output in your team's metrics dashboard.
2. **Drill per-directory**: a project at bus factor 4 can still have auth/ at bus factor 1 [[17]](https://arxiv.org/html/2401.03303v1).
3. **Set a floor**: OpenSSF recommends ≥ 2 [[8]](https://github.com/ossf/scorecard); target ≥ 3 for production-critical systems.
4. **Treat maintainer burnout as a leading indicator**: contributor mood and response-time trends signal bus factor collapse before commit counts do [[4]](https://chaoss.community/kb/metrics-model-oss-project-viability-community/).
5. **Audit dependencies**: before adopting a new library, run its repo through Scorecard [[9]](https://scorecard.dev/) or check its CHAOSS Contributor Absence Factor [[3]](https://chaoss.community/kb/metrics-model-starter-project-health/) — don't inherit someone else's bus factor 1.
