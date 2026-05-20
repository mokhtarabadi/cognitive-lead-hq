---
title: 'Zero Data Retention'
url: https://ai.google.dev/gemini-api/docs/zdr.md.txt
source: llms
fetched_at: 2026-04-29T11:17:11.923153535-03:00
rendered_js: false
word_count: 379
summary: This document explains the requirements and configuration steps necessary for developers to achieve zero data retention when using the Gemini Developer API.
tags:
    - gemini-api
    - zero-data-retention
    - data-privacy
    - security-compliance
    - data-storage
    - api-configuration
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
This page outlines "zero data retention" (ZDR) in the Gemini Developer API.

## Training restriction

For [Paid Services](https://ai.google.dev/gemini-api/terms#paid-services), Google does not use your prompts (including system instructions, cached content, and files) or responses to improve products. See the [Gemini API Terms of Service](https://ai.google.dev/gemini-api/terms).

## Customer data retention scenarios

To achieve ZDR, you must take specific actions or avoid specific features:

- **Prompt logging for abuse monitoring:** For Paid Services, Google logs prompts/responses for a limited period solely for detecting [Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy) violations. When ZDR is approved for your project, all user content and identifiable metadata (IP addresses, Google Account IDs) are cleared prior to logging. The resulting record is marked as sanitized.

- **Grounding with Google Search:** Stores prompts, contextual information, and generated output for 30 days for grounded results and search suggestions. **Cannot be disabled if you use grounding with Google Search.** See [Additional Terms of Service](https://ai.google.dev/gemini-api/terms#grounding-with-google-search).

- **Grounding with Google Maps:** Stores prompts, contextual information, and generated output for 30 days for grounded results. **Cannot be disabled if you use grounding with Google Maps.** See [Additional Terms of Service](https://ai.google.dev/gemini-api/terms).

- **Interactions API:** Manages conversation state for multi-turn turns. **By default, state storage is enabled.** To achieve ZDR, set `store` parameter to `false` in your API requests.

- **Live API:** This stateful API stores conversation state for real-time reconnection. **Do not configure `SessionResumptionConfig`** to achieve ZDR. If a session handle is generated, conversation state (text, audio, video) is retained for up to 24 hours.

- **File API Storage:** Files are stored at-rest until deleted or until they expire. File API usage is independent of ZDR logging. **Manually delete files** to ensure zero-data footprint.

- **Explicit Context Caching:** Caches large datasets (long videos, document libraries) using the `cached_content` field. Logs follow ZDR dropping policies, but cached context itself is stored with user-defined `ttl` or `expire_time`. **Do not use `cached_content`** for absolute zero-data footprint.

- **Implicit In-Memory Caching:** By default, Gemini models cache data in-memory to reduce latency and cost. This data is:
  - Strictly in RAM (not at-rest)
  - Isolated at the project level
  - Has a 24-hour TTL

  **This does not violate Zero Data Retention.**

## What's next

- [Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy)
- [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms)
- [Gemini Enterprise Agent Platform Zero Data Retention](https://cloud.google.com/gemini-enterprise-agent-platform/models/vertex-ai-zero-data-retention)