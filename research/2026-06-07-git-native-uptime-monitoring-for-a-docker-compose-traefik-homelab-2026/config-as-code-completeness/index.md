---
title: "Config-as-Code Completeness: The 8 Domains Most Teams Leave Behind"
date: 2026-06-08
depth: standard
format: md
topic: "Config-as-code completeness"
topic_raw: "Config-as-code completeness"
issue: 198
tags: [devops, infrastructure-as-code, gitops, configuration-management, policy-as-code, secrets-management, platform-engineering, database-migrations]
summary: "Most teams reach modular IaC for compute but leave secrets, policy, database schema, runtime config, and SaaS posture unmanaged — covering all 8 domains with pipeline enforcement is what separates Level 3 from Level 5."
citations: 22
reading_time_min: 8
cover: cover.svg
cost_usd: 2.21
duration_sec: 964
model: "Sonnet 4.6"
---

> **TL;DR** Most teams reach modular IaC for compute resources (Level 3 maturity) but leave 4–5 config domains entirely unmanaged. Full completeness requires encoding all 8 domains as code with pre-production enforcement in each. The hardest gaps: only 13% of orgs have any compliance automation [[14]](https://www.wiz.io/academy/compliance/compliance-as-code), and 97% had a confirmed breach or near-miss from misconfiguration in the past year [[15]](https://www.reach.security/blog/what-is-configuration-drift-5-best-practices-for-your-teams-security-posture). Start with the domain that most affects your blast radius.

## The 8 Domains

"Everything as code" is a family of practices [[1]](https://octopus.com/blog/what-is-everything-as-code), not one practice. Most implementations cover one or two domains and assume that is completeness.

| Domain                    | What it covers                                      | Key tools                                       | Common gap                                      |
| ------------------------- | --------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------- |
| Infrastructure            | Compute, storage, networking primitives             | [Terraform][tf] ⭐ 48.6k, [Pulumi][pulumi] ⭐ 25.3k | State on laptops; no remote locking             |
| Configuration management  | OS packages, middleware settings, runtime OS state  | Ansible, Chef, Puppet                           | Runbooks not yet converted to playbooks         |
| Secrets                   | API keys, certs, DB passwords, OIDC tokens          | [Vault][vault] ⭐ 35.7k, [External Secrets][eso] ⭐ 6.7k | Stored as CI environment variables              |
| Policy & compliance       | Security rules, cost guardrails, regulatory controls | [OPA][opa] ⭐ 11.8k, [Checkov][checkov] ⭐ 8.8k, Sentinel | Only post-deploy; pre-commit absent             |
| Database schema           | Tables, indexes, stored procedures, migrations      | [Atlas][atlas] ⭐ 8.5k, [Flyway][flyway] ⭐ 9.8k, [Liquibase][lb] ⭐ 5.5k | Treated as a DBA manual step outside GitOps    |
| App config & feature flags | Runtime settings, toggles, env vars, rate limits   | [Unleash][unleash] ⭐ 13.6k, LaunchDarkly, ConfigCat | Managed in vendor UIs with no Git history       |
| Pipelines                 | Build, test, deploy workflow definitions            | GitHub Actions, Jenkins, CircleCI               | Inconsistent definitions across teams           |
| SaaS posture              | M365, Salesforce, GitHub, Okta tenant configuration | SSPM tools, Terraform SaaS providers            | No code representation at all                   |

[tf]:     https://github.com/hashicorp/terraform
[pulumi]: https://github.com/pulumi/pulumi
[vault]:  https://github.com/hashicorp/vault
[eso]:    https://github.com/external-secrets/external-secrets
[opa]:    https://github.com/open-policy-agent/opa
[checkov]:https://github.com/bridgecrewio/checkov
[atlas]:  https://github.com/ariga/atlas
[flyway]: https://github.com/flyway/flyway
[lb]:     https://github.com/liquibase/liquibase
[unleash]:https://github.com/Unleash/unleash

## IaC Maturity: Where Teams Actually Are

The most reliable level diagnostic is a single question: *"When was production infrastructure last changed from a developer's machine without a pull request?"* [[12]](https://www.askantech.com/infrastructure-as-code-maturity-terraform-policy-driven-automation/) Recent answers place most teams at Level 2, regardless of how much Terraform they've written.

| Level | Name                  | Defining characteristic                                    | Common failure mode                                            |
| ----- | --------------------- | ---------------------------------------------------------- | -------------------------------------------------------------- |
| 1     | Manual                | Console + runbooks; nothing in code                        | Not reproducible; single points of failure                     |
| 2     | Basic IaC             | Terraform files exist; state on laptops; no locking        | `apply` from developer machines; "works on my machine" drifts  |
| 3     | Modular + VCS         | Remote state, branching, reusable modules                  | Copy-paste across envs; unstable module interfaces; no scanning |
| 4     | Pipeline-driven       | All changes via CI/CD; plans reviewed in PRs               | Long-lived CI secrets; plan/apply divergence; no OIDC         |
| 5     | Policy-driven self-service | Compliance as code; app teams provision independently | Alert fatigue; compliance teams isolated from code             |

The most common plateau is Level 2 disguised as Level 3: state files live on developer laptops despite version-controlled code, provider versions are unpinned, and production applies happen locally [[12]](https://www.askantech.com/infrastructure-as-code-maturity-terraform-policy-driven-automation/). Level 4→5 requires encoding security policies as code (OPA/Sentinel) and building infrastructure catalogues (Backstage, Port) so application teams can provision without blocking on the platform team [[12]](https://www.askantech.com/infrastructure-as-code-maturity-terraform-policy-driven-automation/) [[13]](https://www.kenmuse.com/blog/defining-an-infrastructure-as-code-maturity-model/).

## The 5 Hardest Gaps

### 1. Secrets

96% of organizations report secrets scattered across code, configuration files, and multiple environments [[16]](https://cycode.com/blog/secrets-management-best-practices/). GitGuardian's 2026 State of Secrets Sprawl found nearly 29 million new secrets exposed on public GitHub in 2025 — up 34% year-over-year — with CI/CD configuration files among the primary exposure vectors [[17]](https://www.akeyless.io/blog/the-hidden-risks-of-secrets-management-in-ci-cd-pipelines/).

The correct model: no secrets in Git, ever [[18]](https://softwaremill.com/system-as-a-code-introduction-to-gitops/). [Vault](https://github.com/hashicorp/vault) ⭐ 35.7k [[4]](https://github.com/hashicorp/vault) centralizes credentials with dynamic issuance and fine-grained audit. [External Secrets Operator](https://github.com/external-secrets/external-secrets) ⭐ 6.7k [[5]](https://github.com/external-secrets/external-secrets) syncs from Vault, AWS Secrets Manager, or Azure Key Vault into Kubernetes Secrets without the credential touching Git. At Level 4, the remaining gap is usually long-lived CI keys: replace with OIDC federation so the pipeline authenticates with a short-lived token rather than a stored credential [[12]](https://www.askantech.com/infrastructure-as-code-maturity-terraform-policy-driven-automation/).

### 2. Policy & Compliance

Only 13% of organizations use compliance-as-code; more than half still rely entirely on manual audits [[14]](https://www.wiz.io/academy/compliance/compliance-as-code). A complete policy stack runs at four layers [[19]](https://spacelift.io/blog/policy-as-code-tools):

| Layer            | Stage              | Tools                                                    |
| ---------------- | ------------------ | -------------------------------------------------------- |
| Misconfig scan   | Pre-commit / PR    | [Checkov][checkov2] ⭐ 8.8k, [Trivy][trivy] ⭐ 36.1k          |
| Plan gate        | Pipeline (pre-apply)| Sentinel (HCP Terraform), Spacelift                      |
| Admission control| Cluster apply time | [Kyverno][kyverno] ⭐ 7.8k, [Gatekeeper][gk] ⭐ 4.2k        |
| Org guardrails   | Cloud org-level    | AWS SCPs, Azure Policy, GCP Org Policy                   |

[checkov2]: https://github.com/bridgecrewio/checkov
[trivy]:    https://github.com/aquasecurity/trivy
[kyverno]:  https://github.com/kyverno/kyverno
[gk]:       https://github.com/open-policy-agent/gatekeeper

[OPA](https://github.com/open-policy-agent/opa) ⭐ 11.8k [[6]](https://github.com/open-policy-agent/opa) (Rego) is the cross-layer policy engine; most orgs deploy only one layer, leaving the others as blind spots [[19]](https://spacelift.io/blog/policy-as-code-tools).

The translation bottleneck: converting regulatory language ("appropriate safeguards") into binary, testable rules requires both compliance and infrastructure expertise — ownership that rarely sits in one team [[14]](https://www.wiz.io/academy/compliance/compliance-as-code).

### 3. Database Schema

Schema changes that bypass GitOps break auditability and cannot be safely rolled back [[23]](https://www.bytebase.com/blog/top-database-schema-change-tool-evolution/). Three approaches dominate:

| Tool                    | Approach                                   | Stars   |
| ----------------------- | ------------------------------------------ | ------- |
| [Flyway][flyway2]       | Migration-file (ordered SQL scripts)       | ⭐ 9.8k  |
| [Liquibase][lb2]        | Migration-file (XML/SQL, enterprise audit) | ⭐ 5.5k  |
| [Atlas][atlas2]         | Schema-based declarative (diff + generate) | ⭐ 8.5k  |

[flyway2]: https://github.com/flyway/flyway
[lb2]:     https://github.com/liquibase/liquibase
[atlas2]:  https://github.com/ariga/atlas

[Atlas](https://atlasgo.io) takes the same mental model as Terraform: declare desired schema state, Atlas computes the migration diff automatically [[24]](https://atlasgo.io/atlas-vs-others). For GitOps integration, run migrations as Kubernetes `Job` resources (init containers) before the application deployment rolls out [[25]](https://oneuptime.com/blog/post/2026-03-13-handle-database-schema-migrations-flux-cd/view).

### 4. Runtime Application Config & Feature Flags

Infrastructure-as-code manages servers. It does not manage what your application reads at runtime — environment variables, connection strings, toggle values, rate limits. These are a separate config plane [[26]](https://configu.com/blog/what-is-configuration-as-code-cac-and-5-tips-for-success/).

Failure mode: feature flags and runtime config live in vendor admin UIs with no Git representation, no diff history, and no review process. A flag misconfigured in production is as impactful as a misconfigured Terraform resource and harder to audit.

Complete runtime config-as-code requires [[26]](https://configu.com/blog/what-is-configuration-as-code-cac-and-5-tips-for-success/):
- Feature flags declared as code and applied via API (ConfigCat + Terraform [[27]](https://configcat.com/blog/2024/11/20/using-configcat-with-gitops/); [Unleash](https://github.com/Unleash/unleash) ⭐ 13.6k [[11]](https://github.com/Unleash/unleash) self-hosted with GitOps reconciliation)
- Environment-specific values isolated — no production credentials shared to staging
- Immutable production: all config changes flow through a reviewed pipeline, never applied directly

### 5. SaaS Posture

Every SaaS tool in your stack — M365, Salesforce, GitHub, Okta, Slack — has configuration that can drift: MFA disabled for vendor accounts, sharing settings widened, OAuth scopes silently expanded by a new product feature [[28]](https://www.nudgesecurity.com/saas-security-glossary/configuration-drift). Unlike IaC, these configs have no native code representation; they live in individual vendor admin consoles.

"SaaS multiplies the configuration surface in ways that traditional infrastructure tools weren't designed to handle" [[28]](https://www.nudgesecurity.com/saas-security-glossary/configuration-drift). A GitOps repo can describe an ArgoCD application; it cannot describe what sharing settings apply to your Salesforce org.

Current approaches (ordered by coverage):
- **Terraform SaaS providers** (GitHub, PagerDuty, Datadog, Okta) — use IaC where the vendor exposes an API; the most complete option
- **GitOps for RBAC** — encode GitHub team memberships and Okta group assignments as code, reconcile on schedule
- **SSPM tools** (Defender for Cloud Apps, DoControl) — detect drift after the fact via API polling; not config-as-code but the closest fallback for vendor-locked surfaces

The 100:10:1 developer-to-platform-to-security ratio (DORA research [[29]](https://www.hashicorp.com/en/blog/everything-as-code-for-your-security-lifecycle)) makes manual SaaS config review unsustainable at any scale. SSPM automation is the current best available practice for surfaces that don't expose a Terraform provider.

## Completeness Diagnostic

Five questions to locate your gaps:

1. **Secrets** — Can every secret your application uses be traced to a rotation log in Vault or equivalent? If any live as CI environment variables or `.env` files, secrets is incomplete.
2. **Policy** — Do IaC pull requests fail automatically when a security rule is violated? If a misconfigured S3 bucket (public ACL, no encryption) would pass code review undetected, the policy layer is missing.
3. **Schema** — Does every schema change go through a reviewed migration file in version control? If a DBA can `ALTER TABLE` in production without a Git commit, schema is incomplete.
4. **Runtime config** — Is there a Git-traceable history for every feature flag state change in production? If not, this domain is outside your config-as-code boundary.
5. **SaaS posture** — Can you programmatically answer when your GitHub organisation's base permissions last changed? "I'd have to check manually" means this domain is unmanaged.

## What Completeness Actually Looks Like

The Google SRE Workbook [[30]](https://sre.google/workbook/configuration-design/) defines a complete configuration system by property rather than by toolchain:

- **Philosophy**: every option connects to an operator goal, not an internal implementation detail
- **Mechanics**: semantic validation, syntax linting, version control, change-ownership tracking
- **Safety**: gradual rollout capability, rollback path, safeguards against losing operator control
- **Usability**: tooling that makes correct configs easy and incorrect configs visible

The anti-pattern across all domains: tight coupling of user-facing config syntax to internal data structures. It prevents evolution and makes migration painful — the same problem that static YAML-heavy Kubernetes configs exhibit as cluster complexity grows, where hidden interdependencies between config generators create behaviour that is impossible to trace [[31]](https://news.ycombinator.com/item?id=22787332).

Completeness is not a destination. It is the set of domains where a change to production requires a pull request.
