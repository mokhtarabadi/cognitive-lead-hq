---
title: Logs and datasets
url: https://ai.google.dev/gemini-api/docs/logs-datasets.md.txt
source: llms
fetched_at: 2026-04-29T11:17:35.346360173-03:00
rendered_js: false
word_count: 316
summary: This guide explains how to enable and manage logging for Gemini API applications using Google AI Studio to monitor model performance and curate datasets.
tags:
    - gemini-api
    - logging-configuration
    - ai-studio
    - data-curation
    - application-monitoring
    - dataset-management
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
Enable and manage logging for Gemini API applications in Google AI Studio to monitor model behavior, debug interactions, and curate datasets.

All `GenerateContent` and `StreamGenerateContent` API calls are supported, including [[openai|OpenAI compatibility]] endpoints.

## 1. Enable logging in AI Studio

1. Open [AI Studio logs](https://aistudio.google.com/logs) and select your billing-enabled project.
2. Click the enable button to log all requests by default.

Enable or disable logging for any project at any time through AI Studio.

## 2. View logs in AI Studio

1. Go to [AI Studio](https://aistudio.google.com/logs) and select your project.
2. Logs appear in reverse chronological order.

Click any entry for a full-page view of the request/response pair: full prompt, complete response, and previous-turn context.

> [!note]
> Each project has a default storage limit of up to 1,000 logs. Unsaved logs expire after 55 days. If you reach the limit, delete existing logs to make room.

## 3. Curate and share datasets

1. Use the filter bar to narrow logs by property.
2. Select logs with checkboxes.
3. Click **Create Dataset**.
4. Name the dataset and optionally add a description.
5. Export as CSV, JSONL, or to Google Sheets.

### Dataset use cases

- **Challenge sets:** Target improvements in specific areas.
- **Sample sets:** Real-usage samples for testing another model, or edge cases for pre-deployment checks.
- **Evaluation sets:** Representative of real usage across capabilities, for comparing models or system instruction iterations.

Sharing datasets as demonstration examples helps refine models in diverse contexts and build AI systems useful across many fields.

## Next steps

- **Prototype with session history:** Use [AI Studio Build](https://aistudio.google.com/apps) to vibe-code apps with API key log history.
- **Re-run logs with the Gemini Batch API:** Use datasets for response sampling and evaluation via the [Gemini Batch API](https://github.com/google-gemini/cookbook/blob/main/examples/Datasets.ipynb).

## Compatibility

Logging is not currently supported for:

- Imagen and Veo models
- Gemini embedding model
- Inputs containing videos, GIFs, or PDFs
