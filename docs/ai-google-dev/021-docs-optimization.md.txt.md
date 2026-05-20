---
title: Gemini API optimization and inference
url: https://ai.google.dev/gemini-api/docs/optimization.md.txt
source: llms
fetched_at: 2026-04-29T11:17:59.319492592-03:00
rendered_js: false
word_count: 428
summary: This document outlines the various optimization tiers and features available in the Gemini API, including service tiers for synchronous inference, batch processing, and context caching, to help developers balance cost, latency, and reliability.
tags:
    - gemini-api
    - inference-optimization
    - cost-management
    - latency-optimization
    - context-caching
    - batch-processing
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
Choose the right optimization mechanism to balance speed, cost, and reliability for your workload.

## Service tier comparison

| Feature | Standard | Flex | Priority | Batch | Caching |
|---|---|---|---|---|---|
| **Pricing** | Full price | 50% discount | 75%–100% more than standard | 50% discount | 90% discount + prorated token storage |
| **Latency** | Seconds to minutes | Minutes (1–15 min target) | Seconds | Up to 24 hours | Faster time-to-first-token |
| **Reliability** | High / Medium-high | Best-effort (sheddable) | High (non-sheddable) | High (for throughput) | N/A |
| **Interface** | Synchronous | Synchronous | Synchronous | Asynchronous | Saved state |
| **Best for** | General application workflows | Non-urgent sequential chains | Production, user-facing apps | Massive datasets, offline evals | Recurring queries over same file |

## Synchronous inference tiers

Shift between reliability-optimized and cost-optimized traffic via the `service_tier` parameter.

### Standard (default)

Default for sequential content generation. Normal response times without premium queuing.

- **Reliability:** Standard criticality
- **Pricing:** Standard rates
- **Best for:** Most interactive, day-to-day applications

### Priority (latency-optimized)

Routes requests to high-criticality compute queues. Strictly non-sheddable. If you exceed dynamic limits, the system gracefully downgrades to Standard instead of failing.

- **Reliability:** Highest criticality
- **Pricing:** 75%–100% over Standard
- **Best for:** Customer chatbots, real-time fraud detection, business-critical copilots

### Flex (cost-optimized)

50% discount using opportunistic off-peak compute. Requests are sheddable during standard traffic spikes.

- **Reliability:** Non-guaranteed, sheddable
- **Pricing:** 50% of Standard (billed per token)
- **Best for:** Multi-step agentic workflows where call N+1 depends on call N, background CRM updates, offline evaluations

## Batch API (asynchronous)

Processes large request volumes at 50% standard cost using background throughput queues (target: 24-hour turnaround). Submit requests as in-line dictionaries or a JSONL input file (up to 2GB).

- **Reliability:** Sheddable with 24-hour automated retries and queuing
- **Pricing:** 50% of Standard
- **Best for:** Pre-processing massive datasets, periodic regression test suites, high-volume image or embedding generations

## Context caching

Use when a substantial initial context is referenced repeatedly by shorter requests.

| Type | Description |
|---|---|
| **Implicit** | Auto-enabled on Gemini 2.5+. Cost savings applied when requests hit existing caches based on common prompt prefixes. |
| **Explicit** | Create a cache object with a specific TTL. Refer to cached tokens in subsequent requests to avoid re-sending the full corpus. |

- **Pricing:** Billed by cache token count and storage duration (TTL)
- **Best for:** Chatbots with extensive system instructions, repetitive analysis of lengthy videos, queries against large document sets
