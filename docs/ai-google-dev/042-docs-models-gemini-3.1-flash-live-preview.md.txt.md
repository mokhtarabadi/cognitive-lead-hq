---
title: Gemini 3.1 Flash Live Preview
url: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview.md.txt
source: llms
fetched_at: 2026-04-29T11:17:51.452466609-03:00
rendered_js: false
word_count: 355
summary: This document provides technical specifications and migration instructions for the Gemini 3.1 Flash Live Preview model, focusing on its low-latency, real-time audio-to-audio capabilities.
tags:
    - gemini-3-1-flash
    - live-api
    - real-time-ai
    - model-migration
    - audio-processing
    - multimodal-ai
category: reference
optimized: true
optimized_at: 2026-04-29T14:19:00Z
---
> [!info]
> Low-latency, audio-to-audio model optimized for real-time dialogue and voice-first AI applications with acoustic nuance detection, numeric precision, and multimodal awareness.
>
> [Try in Google AI Studio](https://aistudio.google.com/live?model=gemini-3.1-flash-live-preview)

## Documentation

See the [[003-docs-live-api-get-started-sdk|Live API guide]] for full feature coverage.

## gemini-3.1-flash-live-preview

| Property | Value |
|---|---|
| Model code | `gemini-3.1-flash-live-preview` |
| Inputs | Text, images, audio, video |
| Output | Text and audio |
| Input token limit | 131,072 |
| Output token limit | 65,536 |
| Audio generation | Supported |
| Batch API | Not supported |
| Caching | Not supported |
| Code execution | Not supported |
| File search | Not supported |
| Function calling | Supported |
| Grounding with Google Maps | Not supported |
| Image generation | Not supported |
| Live API | Supported |
| Search grounding | Supported |
| Structured outputs | Not supported |
| Thinking | Supported |
| URL context | Not supported |
| Latest update | March 2026 |
| Knowledge cutoff | January 2025 |

## Migrating from Gemini 2.5 Flash Live

When migrating from `gemini-2.5-flash-native-audio-preview-12-2025` to `gemini-3.1-flash-live-preview`:

- **Model string**: Update to `gemini-3.1-flash-live-preview`.
- **Thinking configuration**: Use `thinkingLevel` (`minimal`, `low`, `medium`, `high`) instead of `thinkingBudget`. Default is `minimal` for lowest latency. See [[027-docs-thinking|Thinking levels and budgets]].
- **Server events**: A single [`BidiGenerateContentServerContent`](https://ai.google.dev/api/live#bidigeneratecontentservercontent) event now contains multiple content parts (audio chunks, transcript). Process all parts in each event.
- **Client content**: `send_client_content` only seeds initial context history via [`initial_history_in_client_content`](https://ai.google.dev/api/live#HistoryConfig) in [`history_config`](https://ai.google.dev/api/live#BidiGenerateContentSetup). Use [`send_realtime_input`](https://ai.google.dev/api/live#bidigeneratecontentrealtimeinput) for text updates during conversation. See [Incremental content updates](https://ai.google.dev/gemini-api/docs/live-guide#incremental-updates).
- **Turn coverage**: Defaults to [`TURN_INCLUDES_AUDIO_ACTIVITY_AND_ALL_VIDEO`](https://ai.google.dev/api/live#turncoverage) instead of `TURN_INCLUDES_ONLY_ACTIVITY`. Consider sending video frames only when audio activity is detected to reduce costs.
- **Async function calling**: Not yet supported. Function calling is synchronous only — the model waits for your tool response before responding. See [Async function calling](https://ai.google.dev/gemini-api/docs/live-tools#async-function-calling).
- **Proactive audio and affective dialogue**: Not yet supported. Remove any configuration for these features. See [Proactive audio](https://ai.google.dev/gemini-api/docs/live-guide#proactive-audio) and [Affective dialogue](https://ai.google.dev/gemini-api/docs/live-guide#affective-dialog).

For a detailed feature comparison, see the [Model comparison](https://ai.google.dev/gemini-api/docs/live-guide#model-comparison) table.

#gemini-3-1-flash #live-api #real-time-ai #model-migration #audio-processing