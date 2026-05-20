---
title: Gemini 3.1 Flash Image Preview
url: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-image-preview.md.txt
source: llms
fetched_at: 2026-04-29T11:17:50.85628928-03:00
rendered_js: false
word_count: 224
summary: "Nano Banana 2 delivers high-quality image generation and conversational editing at mainstream pricing with low latency."
tags:
    - image-generation
    - ai-models
    - model-specifications
    - search-grounding
    - high-efficiency-inference
category: reference
optimized: true
optimized_at: '2026-04-29T14:17:12Z'
---
# Gemini 3.1 Flash Image Preview

Nano Banana 2 delivers high-quality image generation and conversational editing at mainstream pricing with low latency — the high-efficiency counterpart to [[055-docs-models-gemini-3-pro-image-preview|Gemini 3 Pro Image]], optimized for speed and high-volume use.

## Key Updates

- **Resolutions:** New 0.5K, 2K, 4K support; default 1K
- **Image Search Grounding:** Text + image search results inform generation with real-time web data (works with Thinking on/off)
- **Aspect ratios:** New 1:4, 4:1, 1:8, 8:1 options; improved adherence
- Improved quality/consistency and i18n text rendering

> [!example]
> [Try in Google AI Studio](https://aistudio.google.com?model=gemini-3.1-flash-image-preview)

> [!info]
> Full feature coverage: [Image generation](https://ai.google.dev/gemini-api/docs/image-generation)

## gemini-3.1-flash-image-preview

| Property | Description |
|---|---|
| Model code | `gemini-3.1-flash-image-preview` |
| Supported data types | **Inputs** Text and Image / PDF **Output** Image and Text |
| Token limits[^1] | **Input** 131,072 **Output** 32,768 |
| Capabilities | Audio generation ✗ · Batch API ✓ · Caching ✗ · Code execution ✗ · File search ✗ · Function calling ✗ · Grounding with Google Maps ✗ · **Image generation ✓** · Live API ✗ · Search grounding ✓ · Structured outputs ✗ · Thinking ✓ · URL context ✗ |
| Versions | `Preview: gemini-3.1-flash-image-preview` |
| Latest update | February 2026 |
| Knowledge cutoff | January 2025 |

[^1]: See [token documentation](https://ai.google.dev/gemini-api/docs/tokens)

#image-generation #ai-models #search-grounding #high-efficiency-inference