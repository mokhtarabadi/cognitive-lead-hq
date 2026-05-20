---
title: Gemini 3.1 Pro Preview
url: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview.md.txt
source: llms
fetched_at: 2026-04-29T11:16:42.596163629-03:00
rendered_js: false
word_count: 256
summary: This document provides technical specifications and capability details for the Gemini 3.1 Pro Preview model, highlighting its optimizations for agentic workflows, tool usage, and performance.
tags:
    - gemini-3-1
    - ai-model
    - technical-specifications
    - agentic-workflows
    - tool-calling
    - model-performance
category: reference
optimized: true
optimized_at: 2026-04-29T14:19:00Z
---
> [!info]
> Refines the Gemini 3 Pro series with better thinking, improved token efficiency, and grounded factual consistency — optimized for software engineering and agentic workflows requiring precise tool usage and reliable multi-step execution.
>
> [Try in Google AI Studio](https://aistudio.google.com/prompts/new_chat?model=gemini-3.1-pro-preview)

## Documentation

See the [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3) for full feature coverage.

## gemini-3.1-pro-preview

| Property | Value |
|---|---|
| Model code | `gemini-3.1-pro-preview` |
| Inputs | Text, Image, Video, Audio, and PDF |
| Output | Text |
| Input token limit | 1,048,576 |
| Output token limit | 65,536 |
| Audio generation | Not supported |
| Batch API | Supported |
| Caching | Supported |
| Code execution | Supported |
| File search | Supported (AI Studio only) |
| Flex inference | Supported |
| Function calling | Supported |
| Grounding with Google Maps | Supported |
| Image generation | Not supported |
| Live API | Not supported |
| Priority inference | Supported |
| Search grounding | Supported |
| Structured outputs | Supported |
| Thinking | Supported |
| URL context | Supported |
| Latest update | February 2026 |
| Knowledge cutoff | January 2025 |

## Versions

| Version | Description |
|---|---|
| `gemini-3.1-pro-preview` | Standard preview |
| `gemini-3.1-pro-preview-customtools` | Optimized for workflows mixing bash and custom tools (e.g., `view_file`, `search_code`). Better at prioritizing custom tools. Quality may fluctuate in use cases not benefiting from such tools. |

#gemini-3-1 #ai-model #agentic-workflows #tool-calling