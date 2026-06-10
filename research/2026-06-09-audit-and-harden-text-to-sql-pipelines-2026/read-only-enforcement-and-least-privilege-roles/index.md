---
title: "Read-Only Enforcement and Least-Privilege Roles for Text-to-SQL Pipelines"
date: 2026-06-09
depth: standard
format: md
topic: "Read-only enforcement and least-privilege roles"
topic_raw: "Read-only enforcement and least-privilege roles"
issue: 209
tags: [security, database, postgresql, least-privilege, text-to-sql, llm, sql-injection, row-level-security]
summary: "A database-layer enforcement guide: create purpose-built read-only roles, add column/row filtering, and use read replicas as physical write boundaries for LLM-generated SQL."
citations: 25
reading_time_min: 8
cover: cover.svg
cost_usd: 1.54
duration_sec: 521
model: "Sonnet 4.6"
---

> **TL;DR** — Prompt instructions cannot enforce read-only access; only the database can [[1]](https://www.arcade.dev/blog/sql-tools-ai-agents-security/). The minimum viable setup: create a dedicated role with `SELECT` grants and nothing else, then connect the LLM pipeline with those credentials. Stack optionally: column-level grants or views to hide PII, RLS for row filtering, `postgresql_readonly=True` in SQLAlchemy as a belt-and-suspenders add-on, and a read replica as the strongest physical boundary.

---

## Why the database layer is the only real enforcement point

OWASP LLM06:2025 (Excessive Agency) calls out over-privileged database roles as a primary attack vector: an agent given write credentials when only reads are needed becomes a destructive tool the moment prompt injection lands [[2]](https://blog.alexewerlof.com/p/owasp-top-10-ai-llm-agents) [[25]](https://www.oligo.security/academy/owasp-top-10-llm-updated-2025-examples-and-mitigation-strategies). The fix is not a better system prompt. It is role-level grants [[3]](https://socfortress.medium.com/owasp-top-10-for-llm-applications-2025-7cbb304aabf0).

A session-level workaround like `SET default_transaction_read_only = on` looks appealing but is trivially bypassed: any user can issue `SET default_transaction_read_only TO off` to restore write access [[7]](https://jkatz05.com/post/postgres/postgres-read-only/) [[23]](https://postgresqlco.nf/doc/en/param/default_transaction_read_only/). Session flags are safety guards against accidental mutations, not security boundaries [[6]](https://kmoppel.github.io/2025-03-27-til-starting-in-read-only-the-easy-way/).

The enforcement stack, weakest to strongest:

| Layer                            | Mechanism                                          | Bypassable? |
|----------------------------------|----------------------------------------------------|-------------|
| Session flag                     | `SET default_transaction_read_only = on`           | ✗ Yes — any user can unset it |
| Role-level grant                 | `GRANT SELECT` only, no DML/DDL grants             | ✗ No — requires a superuser |
| Column-level grant / view        | Expose only safe columns                           | ✗ No |
| Row-Level Security               | Policy enforced by storage layer                   | ✗ No (unless `BYPASSRLS`) |
| Read replica                     | Physical standby: writes structurally impossible   | ✗ No |

---

## PostgreSQL

### Option A — pg_read_all_data (PG 14+, recommended)

```sql
CREATE ROLE llm_ro LOGIN PASSWORD 'strong-password';
GRANT pg_read_all_data TO llm_ro;
```

`pg_read_all_data` grants `SELECT` on all tables/views/sequences and `USAGE` on all schemas, including objects created by any future user [[4]](https://www.postgresql.org/docs/current/predefined-roles.html) [[5]](https://www.crunchydata.com/blog/creating-a-read-only-postgres-user). The pre-PG14 `ALTER DEFAULT PRIVILEGES` approach only covered objects created by the granting user — `pg_read_all_data` closes that gap.

⚠ `pg_read_all_data` does **not** bypass RLS policies. If you need the agent to see all rows, add `ALTER ROLE llm_ro BYPASSRLS;` only when that is explicitly required.

### Option B — explicit schema grants (PG < 14 or fine-grained control)

```sql
CREATE ROLE llm_ro LOGIN PASSWORD 'strong-password';
GRANT CONNECT ON DATABASE mydb TO llm_ro;
GRANT USAGE ON SCHEMA app TO llm_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA app TO llm_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA app GRANT SELECT ON TABLES TO llm_ro;
```

⚠ `ALTER DEFAULT PRIVILEGES` only applies to objects created by the current user. If multiple admins create tables, each must run it [[5]](https://www.crunchydata.com/blog/creating-a-read-only-postgres-user).

### Optional: per-role session default (belt-and-suspenders only)

```sql
ALTER ROLE llm_ro SET default_transaction_read_only = on;
```

This adds a redundant guard that blocks accidental writes if the role is mistakenly granted write access later. Do **not** rely on it as the sole control [[23]](https://postgresqlco.nf/doc/en/param/default_transaction_read_only/).

---

## MySQL / MariaDB

```sql
CREATE USER 'llm_ro'@'10.0.0.5' IDENTIFIED BY 'strong-password';
GRANT SELECT ON myapp.* TO 'llm_ro'@'10.0.0.5';
-- Optional: grant view inspection
GRANT SHOW VIEW ON myapp.* TO 'llm_ro'@'10.0.0.5';
FLUSH PRIVILEGES;
-- Verify
SHOW GRANTS FOR 'llm_ro'@'10.0.0.5';
```

Key points [[9]](https://oneuptime.com/blog/post/2026-03-31-mysql-create-read-only-user/view):
- Use a specific IP host rather than `%` to limit connection origins.
- Avoid `GRANT SELECT ON *.*` — it exposes `information_schema` and `mysql` system schemas.
- Separate `GRANT` statements are required per database.
- Test that `INSERT`/`UPDATE`/`DELETE` fail before deploying.

---

## SQLite

SQLite has no user/role system. Enforcement happens at connection and process level.

### URI read-only mode (simplest)

```python
import sqlite3

conn = sqlite3.connect("file:data.db?mode=ro", uri=True)
# Any write attempt raises sqlite3.OperationalError
```

[[10]](https://www.slingacademy.com/article/python-311-sqlite3-how-to-open-a-database-in-read-only-mode/)

### Authorizer callback (fine-grained)

The authorizer fires at statement *compilation* time — before execution — and is the official mechanism for restricting untrusted SQL [[11]](https://sqlite.org/c3ref/set_authorizer.html):

```python
import sqlite3

def read_only_authorizer(action, arg1, arg2, dbname, source):
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY   # blocks INSERT, UPDATE, DELETE, DROP, CREATE, …

conn = sqlite3.connect("data.db")
conn.set_authorizer(read_only_authorizer)
```

[[12]](https://www.zetcode.com/python/sqlite3-connection-set-authorizer/) The callback can be made table-aware: return `SQLITE_DENY` for `SQLITE_READ` on tables not in an allowlist, blocking cross-table access entirely.

---

## Column-level access control

Role-level `SELECT` grants exposure to every column in every table. PII columns (`ssn`, `password_hash`, `email`) should be hidden at the grant layer, not filtered by the application.

### PostgreSQL — column-level GRANT

```sql
-- Grant only safe columns; revoke table-wide access first
REVOKE SELECT ON employee FROM llm_ro;
GRANT SELECT (id, name, department, salary_band) ON employee TO llm_ro;
```

⚠ A table-level `GRANT SELECT` overrides column restrictions [[13]](https://www.enterprisedb.com/postgres-tutorials/how-implement-column-and-row-level-security-postgresql). Always revoke broad access before applying column-level grants.

### View-based column filtering (cross-database)

Create a view that exposes only safe columns, grant access to the view, and revoke table access. This works in PostgreSQL, MySQL, and SQL Server:

```sql
CREATE VIEW app.v_orders_safe AS
  SELECT id, customer_id, total_cents, status, region
  FROM orders;   -- omits payment_method, billing_address, …

GRANT SELECT ON app.v_orders_safe TO llm_ro;
REVOKE SELECT ON orders FROM llm_ro;
```

Views are also the standard column-masking approach: wrap sensitive columns in a function that returns `NULL` or a redacted string [[14]](https://hoop.dev/blog/row-level-security-and-sql-data-masking-a-guide-to-protecting-sensitive-data/) [[15]](https://kindatechnical.com/database/row-level-security-column-masking.html).

### SQL Server — schema-scoped role

```sql
CREATE ROLE role_app_read;
GRANT SELECT ON SCHEMA::app TO role_app_read;
ALTER ROLE role_app_read ADD MEMBER [llm_service_account];
-- Validate
EXECUTE AS USER = 'llm_service_account';
SELECT TOP 5 * FROM app.Orders;   -- succeeds
INSERT INTO app.Orders VALUES ();  -- fails
REVERT;
```

[[8]](https://sqlyard.com/2025/12/17/sql-server-security-best-practices/) Avoid `db_owner` and `public` role inheritance; grant `EXECUTE` on stored procedures rather than direct table access when possible.

---

## Row-Level Security

Column grants control *which columns* are visible; RLS controls *which rows*. Together they provide two-dimensional access control that survives LLM-generated `SELECT *` [[13]](https://www.enterprisedb.com/postgres-tutorials/how-implement-column-and-row-level-security-postgresql) [[24]](https://dev.to/vivekdraxlr/row-level-security-for-embedded-dashboards-a-practical-postgres-guide-bn2).

```sql
-- Restrict LLM agent to its own tenant's rows
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON orders
  FOR SELECT
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Set context per connection (before query execution)
SET LOCAL app.current_tenant_id = '3fa85f64-...';
```

[[14]](https://hoop.dev/blog/row-level-security-and-sql-data-masking-a-guide-to-protecting-sensitive-data/) RLS is enforced by the storage layer — application-level bugs or LLM prompt injection cannot bypass it [[24]](https://dev.to/vivekdraxlr/row-level-security-for-embedded-dashboards-a-practical-postgres-guide-bn2).

Also restrict region, sensitivity tier, or data classification:

```sql
CREATE POLICY region_policy ON orders
  FOR SELECT
  USING (region = current_setting('app.current_region'));

GRANT SELECT (id, customer_id, total_cents, region)
  ON orders TO llm_reporting;
```

[[1]](https://www.arcade.dev/blog/sql-tools-ai-agents-security/)

---

## Application-layer connection hardening

### SQLAlchemy (Python)

```python
from sqlalchemy import create_engine, text

# Connect with read-only credentials
engine = create_engine(
    "postgresql+psycopg2://llm_ro:pw@db-host/mydb",
    pool_pre_ping=True,
)

# Belt-and-suspenders: mark every connection READ ONLY at session level
@event.listens_for(engine, "connect")
def set_readonly(dbapi_conn, connection_record):
    with dbapi_conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only = on")

# Per-connection for one-off queries
with engine.connect() as conn:
    conn = conn.execution_options(postgresql_readonly=True)
    result = conn.execute(text("SELECT * FROM orders LIMIT 100"))
```

[[16]](https://docs.sqlalchemy.org/en/20/core/connections.html) `postgresql_readonly=True` issues `SET TRANSACTION READ ONLY` inside the connection, adding a redundant guard on top of the role's grant restrictions.

### pgBouncer connection routing

For architectures with primary + read replicas, map two virtual databases in pgBouncer — one that targets read-only standbys, one that targets the primary — and connect the LLM pipeline only to the reads pool [[17]](https://www.enterprisedb.com/blog/taking-advantage-write-only-and-read-only-connections-pgbouncer-django):

```ini
[databases]
mydb_reads  = host=replica.internal  port=5432 dbname=mydb
mydb_writes = host=primary.internal  port=5432 dbname=mydb
```

The LLM service account is provisioned only the `mydb_reads` connection string.

---

## Read replica as physical write boundary

A PostgreSQL streaming standby in hot-standby mode is structurally read-only at the storage layer: `DELETE`, `UPDATE`, `INSERT`, and DDL fail immediately because the WAL receiver owns the data files [[18]](https://rietta.com/blog/ai-sql-database-data-protection-read-replica/). No role grant, no session flag, no prompt injection can change this.

Architecture:
```
LLM pipeline
    │
    ▼
pgBouncer / read-only DSN
    │
    ▼
Read replica (hot standby) ←── WAL stream ──── Primary (write-only access)
```

Cloud equivalents: AWS RDS read replica, Google Cloud SQL read replica, Azure SQL read scale-out [[22]](https://www.mintmcp.com/blog/ai-agent-security). Route analytical/LLM queries to the replica; keep the primary credentials out of the LLM service entirely.

---

## Stored procedures as a whitelist alternative

Instead of blocking what the LLM cannot do, restrict it to only what it can do [[19]](https://erincon01.medium.com/how-to-safely-use-llms-for-text-to-sql-with-stored-procedures-ba7540067f5f): define approved stored procedures, describe them in the system prompt, and revoke direct table access:

```sql
-- Grant EXECUTE on approved procedures only
GRANT EXECUTE ON PROCEDURE get_orders_in_period TO llm_ro;
GRANT EXECUTE ON PROCEDURE get_customers_summary  TO llm_ro;
REVOKE SELECT ON ALL TABLES IN SCHEMA app FROM llm_ro;
```

The LLM fills in parameters; arbitrary table access is structurally impossible [[19]](https://erincon01.medium.com/how-to-safely-use-llms-for-text-to-sql-with-stored-procedures-ba7540067f5f). This trades query flexibility for the strongest possible whitelist control.

---

## Enforcement layer summary

| Approach                            | DB              | Bypassable | Handles future objects | Notes                                   |
|-------------------------------------|-----------------|------------|------------------------|-----------------------------------------|
| `GRANT pg_read_all_data`            | PostgreSQL 14+  | ✗ No       | ✓ Yes                  | Recommended default for PG              |
| `GRANT SELECT ON ALL TABLES`        | PostgreSQL      | ✗ No       | ✗ Partial              | Need `ALTER DEFAULT PRIVILEGES` too     |
| `GRANT SELECT ON schema.*`          | MySQL/MariaDB   | ✗ No       | ✓ Yes (schema-wide)    | Use specific host, not `%`              |
| `GRANT SELECT ON SCHEMA::app`       | SQL Server      | ✗ No       | ✓ Yes                  | Avoid `db_owner` / `public` inheritance |
| SQLite URI `?mode=ro`               | SQLite          | ✗ No       | —                      | Simplest; pair with authorizer callback |
| SQLite `set_authorizer`             | SQLite          | ✗ No       | —                      | Compile-time; table/column-aware        |
| Column-level GRANT / view           | All             | ✗ No       | ✗ Requires update      | Best for PII column hiding              |
| Row-Level Security (RLS)            | PG / SQL Server | ✗ No       | ✓ Per-policy           | Pairs with RLS context injection        |
| `SET default_transaction_read_only` | PostgreSQL      | ✓ Yes      | —                      | Safety guard only, not security         |
| Read replica (hot standby)          | PG / MySQL      | ✗ No       | —                      | Strongest physical boundary             |
| Stored procedures + REVOKE SELECT   | All             | ✗ No       | ✗ Requires update      | Highest control; lowest flexibility     |

The minimum viable configuration for a text-to-SQL pipeline: **dedicated read-only role + `GRANT pg_read_all_data` (or equivalent) + read replica if available**. Add column grants and RLS where PII or multi-tenant data is involved [[20]](https://dev.to/rakesh_tanwar_8a7d83bc8f0/best-practices-for-connecting-llms-to-sql-databases-47pn) [[21]](https://rgutierrez2004.medium.com/designing-least-privilege-for-ai-a-practical-look-at-oracle-deep-data-security-658568c00a81).
