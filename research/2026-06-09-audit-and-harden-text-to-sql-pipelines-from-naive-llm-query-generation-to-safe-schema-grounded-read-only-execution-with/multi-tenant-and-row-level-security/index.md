---
title: "Multi-Tenant and Row-Level Security"
date: 2026-06-09
depth: ceo
format: md
topic: "Multi-tenant and row-level security"
topic_raw: "Multi-tenant and row-level security"
issue: 209
tags: [database, security, multi-tenant, postgres, rls]
summary: "PostgreSQL RLS is the most cost-efficient multi-tenant isolation pattern, but requires runtime session variables, non-owner roles, and rigorous testing to prevent data leaks."
citations: 5
reading_time_min: 3
cover: cover.svg
cost_usd: 0.27
duration_sec: 135
model: "Haiku 4.5"
---

> **TL;DR** PostgreSQL Row-Level Security (RLS) is the most cost-efficient multi-tenant isolation strategy—achieving 95% CPU efficiency across 1,000 tenants—but requires runtime session variables, non-owner database roles, and rigorous testing to prevent data leaks and context confusion in pooled environments.

## Three Multi-Tenant Isolation Patterns

Multi-tenant databases fall into three approaches: **shared schema** (all tenants in one schema, enforced via RLS), **schema-per-tenant** (separate schemas within one database), and **database-per-tenant** (separate databases per tenant). [[1]](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/)

Shared schema with RLS dominates for SaaS because it minimizes infrastructure cost. In 2026 benchmarks, shared schema achieved 95% CPU utilization and 85% memory efficiency across 1,000 tenants, while database-per-tenant required 300% more CPU and 200% more memory for the same scale. [[2]](https://dasroot.net/posts/2026/01/multi-tenancy-database-patterns-schema-database-row-level/)

## How RLS Works

RLS enforces data isolation by automatically appending a `WHERE` clause to every SQL query—SELECT, INSERT, UPDATE, DELETE. [[3]](https://www.crunchydata.com/blog/row-level-security-for-tenants-in-postgres) A policy compares a table column (typically `tenant_id`) to a runtime variable set per database session: `USING (tenant_id = current_setting('app.current_tenant')::UUID)`. [[1]](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/)

The application sets the tenant context when acquiring a connection from the pool: `SET LOCAL app.current_tenant = <uuid>`. This eliminates the need for one PostgreSQL user per customer, enabling connection pooling at scale. [[3]](https://www.crunchydata.com/blog/row-level-security-for-tenants-in-postgres)

## Critical Implementation Footguns

**Testing blindness:** Superusers and table owners bypass RLS by default. Testing with privileged accounts creates false confidence—policies appear to work but aren't enforced. Always test with dedicated non-owner roles and enable `FORCE ROW LEVEL SECURITY` to prevent bypasses. [[4]](https://www.bytebase.com/blog/postgres-row-level-security-footguns/)

**Context leakage:** Using `SET` instead of `SET LOCAL` with connection poolers (e.g., pgBouncer) can leak tenant context between clients. Use `SET LOCAL` within transactions to scope variables to a single request. [[4]](https://www.bytebase.com/blog/postgres-row-level-security-footguns/)

**Incomplete WITH CHECK:** Defining only the `USING` clause filters SELECTs but allows users to INSERT rows for other tenants. Always pair USING with a matching `WITH CHECK` clause for write operations. [[5]](https://www.permit.io/blog/postgres-rls-implementation-guide)

**Non-LEAKPROOF functions:** Policies using non-LEAKPROOF functions (e.g., custom aggregates) prevent index usage, forcing sequential scans and catastrophic performance degradation. [[4]](https://www.bytebase.com/blog/postgres-row-level-security-footguns/)

**Side-channel leakage:** Query response time and unique constraint violations can leak information about restricted data. Defend by scoping constraints to tenant contexts and monitoring query performance metrics. [[4]](https://www.bytebase.com/blog/postgres-row-level-security-footguns/)
