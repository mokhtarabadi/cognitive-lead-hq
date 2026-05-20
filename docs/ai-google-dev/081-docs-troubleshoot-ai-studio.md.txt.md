---
title: Troubleshoot Google AI Studio
url: https://ai.google.dev/gemini-api/docs/troubleshoot-ai-studio.md.txt
source: llms
fetched_at: 2026-04-29T11:17:04.497944912-03:00
rendered_js: false
word_count: 137
summary: This document provides troubleshooting steps for common issues encountered in Google AI Studio, including access restrictions, content filtering, and token limit management.
tags:
    - troubleshooting
    - google-ai-studio
    - error-codes
    - safety-settings
    - token-limits
    - access-restricted
category: guide
optimized: true
optimized_at: '2026-04-29T14:17:47Z'
---
Troubleshooting steps for common Google AI Studio issues.

## Understand 403 Access Restricted errors

A **403 Access Restricted** error means your usage violates the [Terms of Service](https://ai.google.dev/terms). Common cause: you're not in a [supported region](https://ai.google.dev/available_regions).

## Resolve No Content responses

A **No Content** message appears when content is blocked. Hover over **No Content** and click **Safety** for details.

- If blocked by [[024-docs-safety-settings.md.txt|safety settings]]: review the [safety risks](https://ai.google.dev/docs/safety_guidance) for your use case, then modify the [safety settings](https://ai.google.dev/docs/safety_setting#safety_settings_in_makersuite) to influence responses.
- If blocked but not by safety settings: the query or response may violate the [Terms of Service](https://ai.google.dev/terms) or be otherwise unsupported.

## Check token usage and limits

With a prompt open, click **Text Preview** at the bottom of the screen to see current tokens used and maximum token count for the active model.

#troubleshooting #google-ai-studio #error-codes
