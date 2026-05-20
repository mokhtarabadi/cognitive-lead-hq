---
title: Rate limits
url: https://ai.google.dev/gemini-api/docs/rate-limits.md.txt
source: llms
fetched_at: 2026-04-29T11:16:57.565543989-03:00
rendered_js: false
word_count: 763
summary: This document explains the rate limit structure for the Gemini API, covering request metrics, usage tiers based on billing, and specific constraints for batch and priority inference jobs.
tags:
    - rate-limits
    - gemini-api
    - api-usage
    - billing-tiers
    - quota-management
category: reference
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
# Rate Limits

Rate limits regulate requests to the Gemini API, maintaining fair usage and system performance. [View active rate limits in AI Studio](https://aistudio.google.com/rate-limit?timeRange=last-28-days). See updated [Terms of Service](https://ai.google.dev/gemini-api/terms).

## Rate Limit Metrics

Rate limits are measured across three dimensions:

- **RPM** — Requests per minute
- **TPM** — Tokens per minute (input)
- **RPD** — Requests per day (resets at midnight Pacific time)

Usage is evaluated against each limit. Exceeding any triggers an error. Rate limits are applied per project, not per API key. Some models have additional limits (e.g., IPM for image generation, TPD for token-per-day). Experimental and preview models have more restrictive limits.

## Usage Tiers

Rate limits scale with your project's usage tier. Automatic upgrades occur as spending increases.

| Tier | Qualification | Spend Cap |
|---|---|---|
| **Free** | Active project or free trial | N/A |
| **Tier 1** | Set up and link active billing account | $250 |
| **Tier 2** | Paid $100 + 3 days from first successful payment | $2,000 |
| **Tier 3** | Paid $1,000 + 30 days from first successful payment | $20,000–$100,000+ |

Tier qualification criteria are generally sufficient for approval, though upgrades may be denied based on other factors.

## Priority Inference Rate Limits

Priority inference has its own limits separate from standard limits. **Default: 0.3x standard rate limit** per model and tier.

## Batch API Rate Limits

Batch API has dedicated limits separate from non-batch calls.

- **Concurrent batch requests:** 100
- **Input file size limit:** 2GB
- **File storage limit:** 20GB

### Tier 1 — Batch Enqueued Tokens per Model

| Model | Tokens |
|---|---|
| Gemini 3.1 Pro Preview | 5,000,000 |
| Gemini 3.1 Flash-Lite Preview | 10,000,000 |
| Gemini 3 Flash Preview | 3,000,000 |
| Gemini 2.5 Pro | 5,000,000 |
| Gemini 2.5 Pro TTS | 25,000 |
| Gemini 2.5 Flash | 3,000,000 |
| Gemini 2.5 Flash Preview | 3,000,000 |
| Gemini 2.5 Flash Image Preview | 3,000,000 |
| Gemini 2.5 Flash TTS | 100,000 |
| Gemini 2.5 Flash-Lite | 10,000,000 |
| Gemini 2.5 Flash-Lite Preview | 10,000,000 |
| Gemini 2.0 Flash | 10,000,000 |
| Gemini 2.0 Flash Image | 3,000,000 |
| Gemini 2.0 Flash-Lite | 10,000,000 |
| Gemini 3.1 Flash Image Preview 🍌 | 1,000,000 |
| Gemini 3 Pro Image Preview 🍌 | 2,000,000 |
| Gemini Embedding | 500,000 |

### Tier 2 — Batch Enqueued Tokens per Model

| Model | Tokens |
|---|---|
| Gemini 3.1 Pro Preview | 500,000,000 |
| Gemini 3.1 Flash-Lite Preview | 500,000,000 |
| Gemini 3.1 Flash Preview | 400,000,000 |
| Gemini 2.5 Pro | 500,000,000 |
| Gemini 2.5 Pro TTS | 100,000 |
| Gemini 2.5 Flash | 400,000,000 |
| Gemini 2.5 Flash Preview | 400,000,000 |
| Gemini 2.5 Flash Image Preview | 400,000,000 |
| Gemini 2.5 Flash TTS | 100,000 |
| Gemini 2.5 Flash-Lite | 500,000,000 |
| Gemini 2.5 Flash-Lite Preview | 500,000,000 |
| Gemini 2.0 Flash | 1,000,000,000 |
| Gemini 2.0 Flash Image | 400,000,000 |
| Gemini 2.0 Flash-Lite | 1,000,000,000 |
| Gemini 3.1 Flash Image Preview 🍌 | 250,000,000 |
| Gemini 3 Pro Image Preview 🍌 | 270,000,000 |
| Gemini Embedding | 5,000,000 |

### Tier 3 — Batch Enqueued Tokens per Model

| Model | Tokens |
|---|---|
| Gemini 3.1 Pro Preview | 1,000,000,000 |
| Gemini 3.1 Flash-Lite Preview | 1,000,000,000 |
| Gemini 3.1 Flash Preview | 1,000,000,000 |
| Gemini 2.5 Pro | 1,000,000,000 |
| Gemini 2.5 Pro TTS | 1,000,000 |
| Gemini 2.5 Flash | 1,000,000,000 |
| Gemini 2.5 Flash Preview | 1,000,000,000 |
| Gemini 2.5 Flash Image Preview | 1,000,000,000 |
| Gemini 2.5 Flash TTS | 4,000,000 |
| Gemini 2.5 Flash-Lite | 1,000,000,000 |
| Gemini 2.5 Flash-Lite Preview | 1,000,000,000 |
| Gemini 2.0 Flash | 5,000,000,000 |
| Gemini 2.0 Flash Image | 1,000,000,000 |
| Gemini 2.0 Flash-Lite | 5,000,000,000 |
| Gemini 3.1 Flash Image Preview 🍌 | 750,000,000 |
| Gemini 3 Pro Image Preview 🍌 | 1,000,000,000 |
| Gemini Embedding | 10,000,000 |

## Tier Upgrades

Set up billing in AI Studio to upgrade from Free tier. Projects meeting criteria are automatically upgraded—Free to Tier 1 is typically instant; subsequent upgrades within 10 minutes. Check tiers on the [Projects page](https://aistudio.google.com/projects).

## Request Rate Limit Increase

[Request paid tier rate limit increase](https://forms.gle/ETzX94k8jf7iSotH9). No guarantees are offered, but requests are reviewed.
