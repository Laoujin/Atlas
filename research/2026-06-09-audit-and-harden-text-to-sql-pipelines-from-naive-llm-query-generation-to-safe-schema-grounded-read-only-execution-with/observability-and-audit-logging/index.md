---
title: "Observability and audit logging: complementary but distinct practices"
date: 2026-06-09
depth: ceo
format: md
topic: "Observability and audit logging"
topic_raw: "Observability and audit logging"
issue: 209
tags: [observability, audit-logging, compliance, infrastructure]
summary: "Observability helps teams debug production; audit logging proves compliance and accountability."
citations: 7
reading_time_min: 2
cover: cover.svg
cost_usd: 0.20
duration_sec: 88
model: "Haiku 4.5"
---

> **TL;DR:** Observability (metrics, logs, traces) helps operations teams understand system behavior; audit logging (structured, immutable records of sensitive actions) satisfies compliance and supports security investigations. They are distinct practices. Observability succeeds when data directly informs decisions; audit logging succeeds when it captures who did what, when, and why in a queryable, tamper-resistant format.

## Observability: three pillars

Observability rests on [[1]](https://spacelift.io/blog/observability-best-practices) three data types: **metrics** (numerical measurements—CPU, latency, error rates), **logs** (timestamped event records), and **traces** (request journeys through distributed systems). A unified approach correlates these three via trace IDs or request IDs so a single incident maps across metrics, logs, and traces.

Best practice [[1]](https://spacelift.io/blog/observability-best-practices): align observability to business goals and KPIs, not raw data collection. Instrument applications beyond infrastructure, automate alerts while guarding against fatigue, and build observability requirements into the development pipeline from the start.

## Audit logging: compliance and accountability

Audit logs serve a different reader: regulators, auditors, and security teams. They capture sensitive operations—data access, permission changes, administrative actions—with structured fields: timestamp, principal (user/agent), action, resource, outcome. [[2]](https://rafftechnologies.com/learn/guides/application-logs-vs-audit-logs-developers) This differs sharply from observability, which measures system health.

Standards such as [[3]](https://hoop.dev/blog/the-compliance-observability-equation-audit-ready-debugging-for-modern-teams) SOC 2, ISO 27001, HIPAA, and PCI-DSS require audit trails of privileged actions. [[4]](https://docs.cloud.google.com/logging/docs/audit/best-practices) Google Cloud audit logging best practices include: enable Data Access logs strategically (disabled by default but valuable for troubleshooting), control access via IAM with least-privilege principles, define retention periods (1–3650 days), and use customer-managed encryption keys (CMEK) for sensitive environments. Monitor and route logs to central repositories (Cloud Storage, BigQuery, Pub/Sub) for long-term retention and analysis.

## Implementation patterns

For audit logs, [[5]](https://www.innopulse.io/insights-data-protection-compliance-audit-trails/) use append-only storage, restrict write permissions, separate duties (admins should not delete logs), and implement integrity controls (hashing, WORM). For microservices [[6]](https://microservices.io/patterns/observability/audit-logging.html), avoid coupling audit code to business logic—Event Sourcing offers a cleaner pattern by capturing state changes naturally without scattering audit concerns.

Use structured logging libraries (Winston, Pino) with different transports: application logs to CloudWatch/Datadog, audit logs to append-only databases. Distributed tracing tools like [[7]](https://medium.com/@saikotgire9/production-observability-audit-logging-documentation-5443190c6ae7) OpenTelemetry tie all three observability pillars together and propagate context across service boundaries.

Both observability and audit logging should be centralized, queryable, and monitored. The key distinction: observability informs operations; audit logging proves compliance.
