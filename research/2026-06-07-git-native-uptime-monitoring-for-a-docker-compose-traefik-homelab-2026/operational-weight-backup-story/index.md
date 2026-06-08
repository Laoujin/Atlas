---
title: "Operational Weight & Backup Story: Measuring the Hidden Tax on Your Stack"
date: 2026-06-08
depth: standard
format: md
topic: "Operational weight & backup story"
topic_raw: "Operational weight & backup story"
issue: 198
tags: [devops, sre, backup, disaster-recovery, toil, infrastructure, on-call, runbook-automation]
summary: "Operational weight is the % of engineering time lost to manual reactive work — target below 50%, reality is 30% and rising. The backup story most teams tell is fiction: 71% do no failover testing. The floor is 3-2-1-1-0."
citations: 22
reading_time_min: 9
cover: cover.svg
cost_usd: 1.63
duration_sec: 659
model: "Sonnet 4.6"
---

> **TL;DR** Operational weight = the fraction of engineering time consumed by manual, repetitive, reactive infrastructure work. Google's benchmark is &lt;50%; teams average 30% in 2026, up from 25% in 2024 — the first year-over-year rise in five years. The backup "story" most teams tell is aspirational: 71% do no failover testing, and 62% skip restoration exercises entirely. The backup floor is 3-2-1-1-0 (three copies, two media types, one off-site, one immutable, zero untested restores). Notable 2026 change: pgBackRest is now unmaintained — migrate to Barman or WAL-G.

---

## Operational Weight

### What Counts as Toil

Google's SRE workbook defines toil as operational work that is manual, repetitive, automatable, reactive, and scales linearly with the system [[1]](https://sre.google/workbook/eliminating-toil/). Six attributes identify it:

| Attribute       | Diagnostic question                                        |
| --------------- | ---------------------------------------------------------- |
| Manual          | Could software do this without human judgement?            |
| Repetitive      | Is this the third occurrence this month?                   |
| Automatable     | Has the fix been written down in a runbook?                |
| Reactive        | Did a page cause this, not a calendar?                     |
| No lasting value | Will the same symptom recur next week?                   |
| Linear scaling  | Does doubling services double this work?                   |

Work passing all six tests is pure toil. Work passing three or four still deserves a runbook and an automation ticket.

### The 50% Ceiling

Google limits SRE toil to 50% of team capacity; the remaining half must go to engineering that compounds [[1]](https://sre.google/workbook/eliminating-toil/). Quarterly surveys of Google's own SREs show an actual average of 33%, with individual outliers from 0% (pure project work) to 80% [[2]](https://sre.google/sre-book/eliminating-toil/). Useful target for most teams: **below 50%, aiming toward 30%**.

In 2026 the trend reversed. Average team toil rose to ~30% (up from ~25% in 2024) [[3]](https://upstat.io/blog/toil-reduction) — the first increase in five years, despite widespread adoption of AI operations tooling [[4]](https://thegoodshell.com/on-call-rotation-best-practices/). Teams that added automation on top of uncharted manual processes automated the wrong things, or created new toil validating AI output.

### On-Call as a Lagging Indicator

On-call incident volume is a direct measure of accumulated operational debt. Google's guidance: no more than **2–3 actionable incidents per on-call shift** is a sustainable baseline [[5]](https://sre.google/workbook/on-call/). Above that threshold, the rotation is absorbing toil that should be automated away.

Healthy on-call hygiene [[6]](https://incident.io/blog/on-call-best-practices-guide-2026):

- Primary + secondary on every shift — redundancy prevents heroics
- Follow-the-sun scheduling for 24/7 global coverage
- Quarterly alert audit: any alert firing >5×/week without human action gets automated or suppressed

### DORA MTTR as Operational Health Proxy

Mean Time to Restore (MTTR) is the DORA metric most sensitive to operational maturity [[7]](https://www.gitrecap.com/blog/dora-metrics-benchmarks). Poor runbooks, absent automation, and untested recovery all surface here before they surface as an outage:

| Tier   | MTTR              | Deployment frequency  |
| ------ | ----------------- | --------------------- |
| Elite  | < 1 hour          | Multiple per day      |
| High   | < 1 day           | Daily – weekly        |
| Medium | < 1 day           | Weekly – monthly      |
| Low    | 1 day – 1 week    | Less than monthly     |

Elite and high performers reach comparable change failure rates; MTTR is what separates them.

---

## Where the Weight Accumulates

Self-hosted infrastructure carries operational overhead that managed services abstract away [[8]](https://www.opensourceforu.com/2026/05/self-hosted-vs-managed-cloud-choosing-the-right-infrastructure-for-modern-apps/). The five heaviest toil sinks:

| Category              | Examples                                          | Automatable? |
| --------------------- | ------------------------------------------------- | :----------: |
| Production interrupts | Disk cleanups, memory restarts, cert renewals     | ✓            |
| Release shepherding   | Manual deploy steps, config changes at cutover    | ✓            |
| Migrations            | One-time technology transitions, mass refactoring | Partial      |
| Security patches      | OS upgrades, CVE triage, access reviews           | Partial      |
| Capacity planning     | Reserved instance sizing, scaling events          | Partial      |

The highest-ROI automation target: **production interrupts and release shepherding** — fully automatable, highest recurrence, lowest risk to automate incorrectly.

### Runbook Automation Tools

Runbook automation converts documented recovery procedures into executable workflows triggered from your incident tooling [[21]](https://incident.io/blog/runbook-automation-tools-2026-the-complete-guide). Typical P1 MTTR without automation: 45–60 min; 12 min of that is coordination overhead alone.

| Tool                                            | Model       | Strength                                                                                                   |
| ----------------------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------- |
| [incident.io][incidentio]                       | SaaS        | Slack-native, automatic audit trail, 37% MTTR reduction (Favor case study) [[21]](https://incident.io/blog/runbook-automation-tools-2026-the-complete-guide) |
| [PagerDuty Process Automation][pagerduty-run]   | SaaS        | AI-suggested runbooks from past incident history, enterprise RBAC [[22]](https://www.pagerduty.com/platform/automation/runbook/) |
| [Rundeck][rundeck] ⭐ 6.1k                       | Self-hosted | Open-source script executor, web console, API service                                                      |

[incidentio]:    https://incident.io
[pagerduty-run]: https://www.pagerduty.com/platform/automation/runbook/
[rundeck]:       https://github.com/rundeck/rundeck

---

## The Backup Story

### 3-2-1-1-0: The Modern Floor

The classic 3-2-1 rule — three copies, two media types, one off-site — remains the starting baseline [[9]](https://objectfirst.com/guides/data-backup/3-2-1-backup-rule-and-strategy/). The expanded **3-2-1-1-0** framework adds two requirements that ransomware made non-negotiable [[10]](https://blog.barracuda.com/2026/03/31/world-backup-day--is-the-3-2-1-backup-rule-still-relevant-):

| Element            | What it means                                         | Why it matters                                          |
| ------------------ | ----------------------------------------------------- | ------------------------------------------------------- |
| 3 copies           | Production + two independent backups                  | Single copy is not a backup                             |
| 2 media types      | e.g. block storage + object storage                   | One failure mode cannot hit both                        |
| 1 off-site         | Cloud region or physical distance from primary        | Fire, flood, or rack failure protection                 |
| **1 immutable**    | S3 Object Lock / WORM policy, min 14–30 day retention | Ransomware cannot encrypt what it cannot write [[9]](https://objectfirst.com/guides/data-backup/3-2-1-backup-rule-and-strategy/) |
| **0 errors**       | Every backup tested before a crisis, not during       | An untested backup is an assumption                     |

Only **58% of organizations** use immutable storage across all their data [[9]](https://objectfirst.com/guides/data-backup/3-2-1-backup-rule-and-strategy/) — meaning 42% have no defence against admin credential compromise or ransomware that escalates to backup infrastructure.

### RTO and RPO

Write these down before choosing backup cadence. They are constraints, not aspirations:

- **RTO (Recovery Time Objective):** maximum acceptable downtime — dictates how fast you must restore
- **RPO (Recovery Point Objective):** maximum acceptable data loss measured in time — dictates how often you must back up

If your RTO is 4 hours and your last restore drill took 6 hours, you have an operational gap, not a backup.

### The Reality Gap

The gap between "we have backups" and "we can recover" is where most teams live:

- **62%** of organizations fail to do regular backup and restoration exercises [[11]](https://secureframe.com/blog/disaster-recovery-statistics)
- **71%** do no failover testing at all [[11]](https://secureframe.com/blog/disaster-recovery-statistics)
- **63%** risk reintroducing dormant malware during restoration because they skip validation [[14]](https://thinkon.com/resources/why-your-disaster-recovery-plan-needs-regular-testing/)

Most backup plans pass a documentation review and fail the first restore drill.

### Testing Cadence

Industry best practice uses a tiered cadence [[13]](https://mind-core.com/blogs/disaster-recovery/how-often-should-you-test-your-backup-and-data-recovery-plan/) — the key is that the quarterly full DR exercise uses actual timers and produces an actual measured RTO [[12]](https://cutover.com/blog/how-often-should-recovery-plans-be-tested):

| Cadence              | Scope                                                                            |
| -------------------- | -------------------------------------------------------------------------------- |
| Monthly              | Granular restore of critical systems — spot-check specific files or DB rows      |
| Quarterly            | Full DR exercise — take a service to zero, restore from backup, measure real RTO |
| After every major change | Ad-hoc validation after cloud migrations, upgrades, or security incidents    |

---

## Backup Tools by Layer

### General-Purpose (Files, Object Storage)

| Tool                      | Stars   | UI        | Recommendation                                                         |
| ------------------------- | ------- | --------- | ---------------------------------------------------------------------- |
| [Restic][restic] ⭐ 34k    | ⭐ 34k  | CLI only  | Broadest backend support, largest ecosystem [[16]](https://dev.to/selfhostingsh/restic-vs-kopia-vs-borgbackup-2lmn) |
| [Kopia][kopia] ⭐ 13.4k    | ⭐ 13.4k | Web + CLI | Faster parallel uploads, built-in repository server, granular retention [[15]](https://selfhosting.sh/compare/kopia-vs-restic/) |

[restic]: https://github.com/restic/restic
[kopia]:  https://github.com/kopia/kopia

Both use content-defined chunking (deduplication) and AES-256 encryption. Choose **Kopia** for web-based management or multi-machine central repos; choose **Restic** for broadest integrations and Borgmatic workflows.

### PostgreSQL

**pgBackRest is unmaintained as of April 2026** [[17]](https://thebuild.com/blog/2026/04/30/after-pgbackrest/) — do not use for new deployments; plan migration for existing ones. The maintainer (David Steele) has stopped work; existing installations continue to function but receive no bug fixes or security updates.

| Tool                       | Stars   | Status          | Best for                                                               |
| -------------------------- | ------- | --------------- | ---------------------------------------------------------------------- |
| pgBackRest                 | —       | ⚠ Unmaintained  | Existing installs only — plan migration                                |
| [Barman][barman] ⭐ 3.2k    | ⭐ 3.2k | Active (EDB)    | On-premises; closest functional pgBackRest replacement [[18]](https://severalnines.com/blog/automating-backups-and-disaster-recovery-in-postgresql-at-scale-pgbackrest-vs-barman/) |
| [WAL-G][wal-g] ⭐ 4.1k      | ⭐ 4.1k | Active          | Cloud / object storage + Kubernetes environments [[19]](https://dev.to/kunal_d6a8fea2309e1571ee7/pgbackrest-is-no-longer-maintained-3-postgresql-backup-tools-compared-for-production-2026-4p1c) |

[barman]: https://github.com/EnterpriseDB/barman
[wal-g]:  https://github.com/wal-g/wal-g

For migrations off pgBackRest: test the replacement tool in parallel before cutover, benchmark your actual restore times, and only switch once your measured RTO is verified [[17]](https://thebuild.com/blog/2026/04/30/after-pgbackrest/).

### Kubernetes

[Velero](https://github.com/vmware-tanzu/velero) ⭐ 10k backs up cluster state and persistent volumes as GitOps-native CRDs (`Backup`, `Restore`, `Schedule`) — backup policies are version-controlled objects alongside application manifests [[20]](https://www.plural.sh/blog/velero-backup-kubernetes-guide/). As of Velero 1.10+, the default file backend is Kopia; Restic remains available but is slower for large data volumes.

---

## Action Checklist

- [ ] Calculate your current toil %: `(hours on incidents + manual tasks) ÷ total eng hours per week`. Above 50% requires management escalation [[1]](https://sre.google/workbook/eliminating-toil/).
- [ ] Count actionable on-call alerts per shift this week. Above 3 means unresolved runbook debt [[5]](https://sre.google/workbook/on-call/).
- [ ] Write RTO and RPO for each critical service before touching backup cadence.
- [ ] Verify at least one backup copy is immutable (S3 Object Lock, MinIO WORM, or equivalent).
- [ ] Schedule a restore drill for next month — one critical service, take it to zero, time the actual recovery.
- [ ] Migrate away from pgBackRest if it is anywhere in your stack [[17]](https://thebuild.com/blog/2026/04/30/after-pgbackrest/).
