---
title: "Observability & tracing: Three pillars and distributed tracing in 2026"
date: 2026-06-09
depth: ceo
format: md
topic: "Observability & tracing"
topic_raw: "Observability & tracing"
issue: 207
tags: [observability, tracing, microservices, OpenTelemetry, distributed-systems]
summary: "Observability is built on three pillars—traces, metrics, and logs—with distributed tracing now essential for microservices. OpenTelemetry is the vendor-neutral standard; teams adopt hybrid models combining open-source backends with SaaS platforms."
citations: 8
reading_time_min: 3
cost_usd: 0.19
duration_sec: 68
model: "Haiku 4.5"
---

> **TL;DR:** Observability enables understanding systems through external signals without knowing internals. The three pillars—traces, metrics, and logs—work together to diagnose performance and failures. Distributed tracing maps request journeys across microservices, and [[1]](https://opentelemetry.io/) OpenTelemetry provides the vendor-neutral API standard backed by CNCF. Choose between open-source backends (Jaeger, Zipkin) and commercial platforms (Datadog, New Relic), or combine both for a hybrid approach.

## What is Observability?

[[1]](https://opentelemetry.io/docs/concepts/observability-primer/) Observability "lets you understand a system from the outside by asking questions about that system without knowing its inner workings." It requires proper instrumentation—applications must emit signals—so external tools can infer internal behavior. The opposite of observability is a black box where failures and slowdowns are invisible until they cascade into user-facing incidents.

## The Three Pillars

Observability rests on three signal types: [[2]](https://spacelift.io/blog/observability-best-practices)

- **Traces** record request paths through distributed systems, showing the complete journey from entry to response.
- **Metrics** are numeric aggregations (CPU, latency percentiles, error rates) measured over time, enabling alerting and trend analysis.
- **Logs** are timestamped messages emitted by services, useful for detail-level debugging.

A mature observability program collects all three and correlates them to answer questions like "Why did this request fail?" or "Which service caused the slowdown?"

## Distributed Tracing

[[3]](https://uptrace.dev/opentelemetry/distributed-tracing) Distributed tracing "tracks a request's complete journey across microservices, databases, and external services." A trace is a tree of spans—individual operations with duration, status, and metadata. A shared trace ID links all spans across service boundaries, allowing a single request to be followed from frontend through database and back.

Benefits include [[3]](https://uptrace.dev/opentelemetry/distributed-tracing) performance visibility (which service caused latency), dependency discovery (automatic service topology), and failure diagnosis (complete chain of failures).

## OpenTelemetry: The Vendor-Neutral Standard

[[1]](https://opentelemetry.io/) OpenTelemetry is a CNCF-backed open-source observability framework providing vendor-neutral APIs and SDKs for 12+ languages. It automatically captures traces and metrics from applications and forwards them to any backend (Datadog, Jaeger, Tempo, CloudWatch, etc.), avoiding lock-in.

[[4]](https://www.logicmonitor.com/blog/observability-ai-trends-2026) OpenTelemetry adoption is "non-negotiable for future-proofing," with growing support for AI/LLM observability via semantic conventions for agent spans, tool calls, and token metrics.

## Tools Landscape

The tracing market splits into philosophies:

**Open Source:** [[5]](https://signoz.io/blog/datadog-vs-jaeger/) Jaeger (CNCF, originally built by Uber) and Zipkin (Twitter, 2012) are free but require self-hosting and operational overhead. Jaeger integrates natively with OpenTelemetry.

**Commercial:** [[5]](https://signoz.io/blog/datadog-vs-jaeger/) Datadog APM ($36–48/host/month) unifies traces, logs, metrics, and error tracking in one SaaS platform, trading infrastructure cost for ease of use.

**Hybrid trend:** [[5]](https://signoz.io/blog/datadog-vs-jaeger/) Many teams now adopt open-source backends (cost control) layered with SaaS tooling (developer experience), balancing expense and capability.
