---
title: "Query Validation and Safety Gates for Text-to-SQL Pipelines"
date: 2026-06-09
depth: standard
format: md
topic: "Query validation and safety gates"
topic_raw: "Query validation and safety gates"
issue: 209
tags: [sql, security, llm, text-to-sql, validation, safety, rag]
summary: "A five-layer defense-in-depth pipeline for validating LLM-generated SQL — from statement allowlists and AST structural checks through semantic schema binding, policy injection, and database-level enforcement — with evidence logging and emerging threat coverage."
citations: 20
reading_time_min: 8
cover: cover.svg
cost_usd: 1.33
duration_sec: 587
model: "Sonnet 4.6"
---

> **TL;DR** — Regex blocklists are bypassed by comment wrapping and Unicode tricks; a single validation layer never covers all failure classes. Chain five deterministic layers: statement-type allowlist → AST structural check → semantic schema binding → policy injection → read-only DB connection. Add a SQL Compile Gate (PARSEONLY / EXPLAIN) before execution and cryptographically-signed audit logs for SOC 2 / HIPAA. All validation must run *after* LLM generation, in code — never delegated to a second LLM call [[1]](https://arxiv.org/html/2503.05445v1) [[3]](https://timdietrich.me/blog/sql-agent-safety-architecture/).

---

## Why Single-Layer Validation Fails

Regex keyword blocklists are the most common first approach — and the most commonly bypassed. Classical SQL injection detection techniques drop from ~98% accuracy on standard benchmarks to **60%** against LLM-generated queries [[1]](https://arxiv.org/html/2503.05445v1), because comment-wrapped commands (`/* DROP */ TABLE users`), Unicode homoglyphs, and semicolon-delimited multi-statement sequences all evade pattern matching.

A 50,000-query production evaluation found a more fundamental problem: **most broken LLM queries execute successfully and return data** [[2]](https://www.usedatabrain.com/blog/llm-sql-evaluation). The failure distribution:

| Failure class              | Description                                                  | Caught by              |
| -------------------------- | ------------------------------------------------------------ | ---------------------- |
| Schema hallucination       | Column/table exists in training data, not in this DB         | Semantic binding       |
| Wrong join path            | Fabricated FK relationships between unrelated tables         | Semantic binding       |
| Missing required filter    | Omits `status='active'`, tenant\_id, date range              | Policy injection       |
| Wrong table selection      | `payments` instead of `revenue_recognition`                  | Semantic binding       |
| Unsafe statement type      | `DELETE`, `DROP`, `ALTER` generated from ambiguous intent    | Statement allowlist    |
| Syntax errors              | Unbalanced parens, invalid keywords                          | Parser / Compile Gate  |

[Source: [2]](https://www.usedatabrain.com/blog/llm-sql-evaluation)

Syntax errors — the only class reliably caught by a basic parser — are the *least common*. Intent errors masquerading as working queries are the dominant risk [[2]](https://www.usedatabrain.com/blog/llm-sql-evaluation). Each layer below targets a distinct failure class.

---

## The Five-Layer Validation Pipeline

### Layer 0 — Intent Classification (Pre-SQL)

Before generating SQL at all, classify whether the user's message warrants a database query. Off-topic, ambiguous, or malformed inputs should be refused early [[3]](https://timdietrich.me/blog/sql-agent-safety-architecture/).

The **LatentRefusal** mechanism [[4]](https://arxiv.org/abs/2601.10398) pushes this further: a lightweight probe on the LLM's *intermediate hidden activations* intercepts unanswerable or schema-mismatched queries *before* any SQL tokens are emitted. Its Tri-Residual Gated Encoder suppresses schema noise and amplifies question-schema mismatch signals, adding ~2ms overhead while achieving 88.5% refusal F1 across four benchmarks [[4]](https://arxiv.org/abs/2601.10398). The complementary "Query Carefully" [[18]](https://arxiv.org/abs/2512.21345) approach detects ambiguous queries at parse time before execution. Both gates are single-pass, pre-generation, and execution-free.

### Layer 1 — Statement-Type Allowlist

Parse the generated SQL and enforce a **default-deny** policy on statement types [[5]](https://queryshield.dev/aeo/guides/prevent-sql-injection-llm-queries):

- **Block**: `DROP`, `TRUNCATE`, `ALTER`, `GRANT`, `REVOKE`, `CREATE`, `INSERT`, `UPDATE`, `DELETE`
- **Block**: multi-statement queries (semicolon-delimited sequences)
- **Block**: stored procedure calls, `EXEC`, dynamic SQL constructors
- **Allow**: `SELECT` only (for read-only agents)

Regex is insufficient here because of the bypass patterns above. Use a real parser: [sqlglot](https://github.com/tobymao/sqlglot) ⭐ 9.3k (Jun 2026) traverses the AST to identify top-level statement type programmatically [[6]](https://github.com/tobymao/sqlglot).

### Layer 2 — AST Structural Validation

Traverse the parse tree to validate structure against what this user is authorized to see [[7]](https://lotuslabs.medium.com/text-to-sql-a-privacy-nightmare-how-to-architect-secure-enterprise-grade-text-to-sql-256615d1b59f):

- **Table allowlist**: every `FROM` / `JOIN` reference must match the user's role-scoped table set
- **Column allowlist**: every column in `SELECT`, `WHERE`, `JOIN ON`, subqueries, and CTEs must be in the user's per-role column list — catches hallucinated fields immediately
- **Sensitive column blocklist**: columns tagged PII / financial are rejected at projection level, even when buried in CTEs or derived expressions [[8]](https://www.dpriver.com/blog/text-to-sql-security-10-risks-before-production-deployment/)

```python
# Minimal example: block forbidden types, check allowed tables via sqlglot AST
import sqlglot

ALLOWED_TABLES = {"orders", "products", "customers"}
FORBIDDEN_TYPES = {
    sqlglot.exp.Drop, sqlglot.exp.Delete,
    sqlglot.exp.Update, sqlglot.exp.Insert,
}

def validate(sql: str) -> tuple[bool, str]:
    parsed = sqlglot.parse_one(sql)
    if type(parsed) in FORBIDDEN_TYPES:
        return False, f"Forbidden statement type: {type(parsed).__name__}"
    tables = {t.name.lower() for t in parsed.find_all(sqlglot.exp.Table)}
    if not tables.issubset(ALLOWED_TABLES):
        blocked = tables - ALLOWED_TABLES
        return False, f"Unauthorized tables: {blocked}"
    return True, "ok"
```

[sqlglot](https://github.com/tobymao/sqlglot) ⭐ 9.3k handles 31 SQL dialects and supports AST mutation via `transform()` [[6]](https://github.com/tobymao/sqlglot). For simpler tokenization, [sqlparse](https://github.com/andialbrecht/sqlparse) ⭐ 3.9k is lighter but is explicitly a *non-validating* parser that will miss edge-case constructs [[9]](https://github.com/andialbrecht/sqlparse). For PostgreSQL-native pipelines, `pg_query` wraps `libpg_query` for exact PG parse trees [[19]](https://pypi.org/project/pg_query/).

### Layer 3 — Semantic / Schema-Binding Validation

The AST check validates *shape*; semantic validation validates *meaning against the real schema* [[10]](https://www.dpriver.com/blog/sql-semantic-validation-for-llm-generated-queries/). A catalog-aware validator resolves every reference against live database metadata:

| Semantic check              | Error code                  | What it catches                                  |
| --------------------------- | --------------------------- | ------------------------------------------------ |
| Column resolution           | `UNKNOWN_COLUMN`            | Hallucinated fields not in current schema        |
| Ambiguity detection         | `AMBIGUOUS_COLUMN`          | Unqualified names present in multiple joined tables |
| Type compatibility          | `TYPE_MISMATCH`             | Function args with wrong types, dialect mismatches |
| Required filter enforcement | `MISSING_REQUIRED_FILTER`   | Missing tenant\_id, status, date range           |
| Join predicate check        | `CARTESIAN_JOIN`            | Many-to-many cross joins without predicates      |
| Sensitive field exposure    | `RESTRICTED_COLUMN`         | PII in projections, filters, or expressions      |

[Source: [10]](https://www.dpriver.com/blog/sql-semantic-validation-for-llm-generated-queries/)

The validator returns structured codes — `allow`, `deny`, `warn`, or `repair` — with repair hints the LLM can safely act on [[10]](https://www.dpriver.com/blog/sql-semantic-validation-for-llm-generated-queries/).

**SQL Compile Gate** — engine-native dry-run before execution [[7]](https://lotuslabs.medium.com/text-to-sql-a-privacy-nightmare-how-to-architect-secure-enterprise-grade-text-to-sql-256615d1b59f) [[11]](https://www.sqlshack.com/the-parseonly-sql-command-overview-and-examples/):

- **SQL Server**: `SET PARSEONLY ON` (parse phase only) or `SET SHOWPLAN_XML ON` (compile + plan, no execute) — validates column existence and user permissions without running the query
- **PostgreSQL / BigQuery / Snowflake**: `EXPLAIN` — rejects insane cost estimates and full scans on large tables
- Engine-native validation catches edge cases (dialect-specific syntax, permission grants) that custom parsers miss

### Layer 4 — Policy Injection

Do not trust the LLM to consistently include required business-logic filters. Mechanically rewrite the AST to inject non-negotiable constraints before execution [[7]](https://lotuslabs.medium.com/text-to-sql-a-privacy-nightmare-how-to-architect-secure-enterprise-grade-text-to-sql-256615d1b59f):

- Tenant isolation: append `WHERE tenant_id = :ctx.tenant` to every top-level query
- Time-window filters: inject `AND created_at >= :ctx.start_date`
- Status filters: add `AND status = 'active'` where schema requires it

Policies are evaluated against the **parsed AST**, never against the raw prompt text — a regex-matched `tenant_id` in the user's message is not the same as an enforced predicate in the generated SQL [[5]](https://queryshield.dev/aeo/guides/prevent-sql-injection-llm-queries). sqlglot's `transform()` API enables programmatic AST mutation that survives alias and CTE resolution [[6]](https://github.com/tobymao/sqlglot).

### Layer 5 — Database-Level Enforcement

Application layers 1–4 are the primary controls. Layer 5 is the backstop if any prior layer has a bug [[12]](https://dev.to/kowshik_jallipalli_a7e0a5/safe-text-to-sql-giving-an-agent-database-access-without-dropping-tables-or-leaking-pii-i47):

- **Read-only DB user**: `GRANT SELECT` only — cannot execute `INSERT`, `UPDATE`, `DELETE` regardless of LLM output
- **Row-Level Security**: database-enforced tenant isolation regardless of query structure (PostgreSQL RLS, SQL Server RLS) [[17]](https://querio.ai/articles/row-level-security-multi-tenant-saas-analytics)
- **Read replica**: route LLM queries to an analytics replica; production writes are physically isolated [[3]](https://timdietrich.me/blog/sql-agent-safety-architecture/)
- **Result row cap**: `LIMIT 1000` prevents resource exhaustion from missing `LIMIT` clauses [[3]](https://timdietrich.me/blog/sql-agent-safety-architecture/)

**RLS limitations** — understand the ceiling [[5]](https://queryshield.dev/aeo/guides/prevent-sql-injection-llm-queries) [[13]](https://medium.com/@instatunnel/multi-tenant-leakage-when-row-level-security-fails-in-saas-da25f40c788c): RLS cannot enforce column-level redaction on `SELECT *`, cannot block DDL statements when the user has valid grants, and has exploitable CVEs — CVE-2024-10976 (RLS bypass below subqueries in PostgreSQL) and CVE-2025-8713 (optimizer statistics leaking RLS-hidden rows) [[13]](https://medium.com/@instatunnel/multi-tenant-leakage-when-row-level-security-fails-in-saas-da25f40c788c). RLS is defense-in-depth, not the primary control.

---

## Evidence Logging

Every validation decision — accepted or rejected — must produce a **cryptographically-signed, timestamped record** [[5]](https://queryshield.dev/aeo/guides/prevent-sql-injection-llm-queries):

- User identity and role context
- Natural language input
- Generated SQL (as-generated, before policy injection)
- Policy decisions, violation codes, and repair attempts
- Final executed SQL and result row count
- Which layers accepted / rejected the query

Required for SOC 2, HIPAA, and forensic analysis. Log the LLM prompt alongside the SQL so backdoor attacks can be traced to their trigger inputs [[16]](https://medium.com/@sirigineediaditi/when-prompt-injections-meet-sql-injection-why-guardrails-are-the-prepared-statements-of-ai-260932bfb29d).

---

## Emerging Threats

### Backdoor Attacks (ToxicSQL)

The ToxicSQL framework [[14]](https://arxiv.org/abs/2503.05445) (SIGMOD 2026 [[15]](https://dl.acm.org/doi/abs/10.1145/3769762)) shows that poisoning **0.44% of training data** achieves a **79.41% attack success rate** for embedding backdoors that generate predefined malicious SQL on trigger inputs while maintaining normal behavior on clean queries [[14]](https://arxiv.org/abs/2503.05445). Stealthy semantic and character-level triggers make poisoned samples hard to detect in training pipelines.

⚠ Implication: fine-tuned models are not inherently safer than base models. Application-layer validation remains mandatory regardless of model provenance or fine-tuning source.

### Repair Loop Escapes

When generated SQL fails validation, returning the error to the LLM for repair can produce queries that *remove* safety filters to avoid the error. Mitigations [[8]](https://www.dpriver.com/blog/text-to-sql-security-10-risks-before-production-deployment/):

- Re-validate every repaired query with identical strictness — no exceptions for repair attempts
- Treat **policy violations** and **syntax errors** as separate error classes: return policy violations to the *application logic*, not to the LLM
- Cap repair iterations (2–3 max); escalate to human review if retries fail

### Schema Curation as Proactive Reduction

Validation is easier if the LLM cannot reference unauthorized objects in the first place [[7]](https://lotuslabs.medium.com/text-to-sql-a-privacy-nightmare-how-to-architect-secure-enterprise-grade-text-to-sql-256615d1b59f):

- Strip sensitive columns from DDL in the system prompt — `email`, `hashed_password`, `ssn` never appear in schema context [[12]](https://dev.to/kowshik_jallipalli_a7e0a5/safe-text-to-sql-giving-an-agent-database-access-without-dropping-tables-or-leaking-pii-i47)
- Use a vector index of table definitions tagged by access role; the model only receives schema for tables the user's role can see [[7]](https://lotuslabs.medium.com/text-to-sql-a-privacy-nightmare-how-to-architect-secure-enterprise-grade-text-to-sql-256615d1b59f)
- Never pass production row data to the LLM — only format specifications and low-cardinality vocabularies

Schema curation reduces obvious hallucinations but does not replace post-generation validation: LLMs still produce probabilistic output, and that output still requires all five layers.

---

## Tools Reference

| Library                  | AST support | Dialects        | Stars   | Best for                                          |
| ------------------------ | ----------- | --------------- | ------- | ------------------------------------------------- |
| [sqlglot][t1]            | Full        | 31 dialects     | ⭐ 9.3k | Cross-dialect traversal, mutation, type inference |
| [sqlparse][t2]           | Partial     | DB-agnostic     | ⭐ 3.9k | Lightweight tokenization; non-validating          |
| [pg\_query][t3]          | Full (PG)   | PostgreSQL only | —       | Exact PG parse tree via libpg\_query              |
| sqlfluff                 | No          | Linting only    | —       | SQL style / dialect linting, not safety gates     |

[t1]: https://github.com/tobymao/sqlglot
[t2]: https://github.com/andialbrecht/sqlparse
[t3]: https://pypi.org/project/pg_query/

---

## Implementation: Crawl → Walk → Run

Start constrained and expand based on observed patterns — the use cases you don't anticipate are the ones that will expose you [[3]](https://timdietrich.me/blog/sql-agent-safety-architecture/) [[20]](https://www.oligo.security/academy/owasp-top-10-llm-updated-2025-examples-and-mitigation-strategies):

1. **Crawl** — expose 2–3 specific business queries, hard-code allowed tables/columns, manually review generated SQL in staging for 2 weeks
2. **Walk** — expand to a role-scoped schema subset, add automated AST validation and semantic binding, enable audit logging
3. **Run** — roll out across roles with monitoring; add the SQL Compile Gate and anomaly alerts on the audit log stream

Do not skip the Crawl phase. A narrow, manually-reviewed allow-set is far safer than a broad schema with "should-be-fine" LLM constraints.
