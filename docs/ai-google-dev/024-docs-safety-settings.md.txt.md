---
title: Safety settings
url: https://ai.google.dev/gemini-api/docs/safety-settings.md.txt
source: llms
fetched_at: 2026-04-29T11:18:01.336231459-03:00
rendered_js: false
word_count: 467
summary: This document explains how to configure safety filters and adjust content blocking thresholds within the Gemini API to manage output appropriateness for specific use cases.
tags:
    - gemini-api
    - content-safety
    - safety-filters
    - harm-blocking
    - configuration
    - api-settings
category: guide
optimized: true
optimized_at: 2026-04-29T12:00:00Z
---
Configure safety filters and thresholds during prototyping to determine appropriate restrictions for your application. Four filter categories can be adjusted to restrict or allow content types.

> [!NOTE]
> Applications using less restrictive safety settings may be subject to review. See the [Terms of Service](https://ai.google.dev/gemini-api/terms#use-restrictions).

## Safety filters

| Category | Description |
|---|---|
| **Harassment** | Negative or harmful comments targeting identity and/or protected attributes. |
| **Hate speech** | Content that is rude, disrespectful, or profane. |
| **Sexually explicit** | References to sexual acts or other lewd content. |
| **Dangerous** | Promotes, facilitates, or encourages harmful acts. |

Categories are defined in [`HarmCategory`](https://ai.google.dev/api/rest/v1/HarmCategory). Adjust based on use case—for example, video game dialogue may allow more "Dangerous" content.

The API has built-in protections for core harms (e.g., content endangering child safety) that are always blocked and cannot be adjusted.

### Content safety filtering level

The API categorizes content probability as `HIGH`, `MEDIUM`, `LOW`, or `NEGLIGIBLE`. It blocks based on *probability* of being unsafe, not severity. Consider:

1. "The robot punched me." → Higher probability of unsafe
2. "The robot slashed me up." → Higher severity of violence

Test carefully to balance blocking for key use cases while minimizing harm.

### Safety filtering per request

Content is analyzed and assigned a safety rating (category + harm probability). Additional filters are **Off** by default—adjust only if consistently required for your application.

| Google AI Studio | API | Description |
|---|---|---|
| Off | `OFF` | Turn off safety filter |
| Block none | `BLOCK_NONE` | Always show regardless of probability |
| Block few | `BLOCK_ONLY_HIGH` | Block high probability |
| Block some | `BLOCK_MEDIUM_AND_ABOVE` | Block medium or high probability |
| Block most | `BLOCK_LOW_AND_ABOVE` | Block low, medium, or high probability |
| N/A | `HARM_BLOCK_THRESHOLD_UNSPECIFIED` | Use default threshold |

Default threshold is **Off** for Gemini 2.5 and 3 models.

See [`HarmBlockThreshold`](https://ai.google.dev/api/generate-content#harmblockthreshold) API reference.

### Safety feedback

[`generateContent`](https://ai.google.dev/api/generate-content#method:-models.generatecontent) returns safety feedback in [`GenerateContentResponse`](https://ai.google.dev/api/generate-content#generatecontentresponse):

- **Prompt feedback:** [`promptFeedback.blockReason`](https://ai.google.dev/api/generate-content#promptfeedback)—prompt was blocked
- **Response feedback:** [`Candidate.finishReason`](https://ai.google.dev/api/generate-content#candidate) and [`Candidate.safetyRatings`](https://ai.google.dev/api/generate-content#safetyratings)—response was blocked with `finishReason` = `SAFETY`

Blocked content is not returned.

## Adjust safety settings

### Google AI Studio

1. Click **Safety settings** under **Advanced settings** in the **Run settings** panel
2. Adjust sliders per safety category

> [!NOTE]
> Ensure safety settings comply with [Terms of Service](https://ai.google.dev/gemini-api/terms#use-restrictions).

A **Content blocked** message appears if content is blocked. Hover for category and probability details.

### Code examples

Set threshold for `HARM_CATEGORY_HATE_SPEECH` to `BLOCK_LOW_AND_ABOVE`:

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Some potentially unsafe prompt",
    config=types.GenerateContentConfig(
      safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
      ]
    )
)

print(response.text)
```

### Go

```go
package main

import (
    "context"
    "fmt"
    "log"
    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    config := &genai.GenerateContentConfig{
        SafetySettings: []*genai.SafetySetting{
            {
                Category:  "HARM_CATEGORY_HATE_SPEECH",
                Threshold: "BLOCK_LOW_AND_ABOVE",
            },
        },
    }

    response, err := client.Models.GenerateContent(
        ctx,
        "gemini-3-flash-preview",
        genai.Text("Some potentially unsafe prompt."),
        config,
    )
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(response.Text())
}
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const safetySettings = [
  {
    category: "HARM_CATEGORY_HATE_SPEECH",
    threshold: "BLOCK_LOW_AND_ABOVE",
  },
];

async function main() {
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "Some potentially unsafe prompt.",
    config: {
      safetySettings: safetySettings,
    },
  });
  console.log(response.text);
}

await main();
```

### Java

```java
SafetySetting hateSpeechSafety = new SafetySetting(HarmCategory.HATE_SPEECH,
    BlockThreshold.LOW_AND_ABOVE);

GenerativeModel gm = new GenerativeModel(
    "gemini-3-flash-preview",
    BuildConfig.apiKey,
    null, // generation config is optional
    Arrays.asList(hateSpeechSafety)
);

GenerativeModelFutures model = GenerativeModelFutures.from(gm);
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d '{
    "safetySettings": [
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"}
    ],
    "contents": [{
        "parts":[{
            "text": "Some potentially unsafe prompt."
        }]
    }]
}'
```

## Next steps

- [API reference](https://ai.google.dev/api) for full API details
- [Safety guidance](https://ai.google.dev/gemini-api/docs/safety-guidance) for general safety considerations
- [Jigsaw team](https://developers.google.com/perspectiveapi/s/about-the-api-score) for probability vs severity assessment
- [Perspective API](https://medium.com/jigsaw/reducing-toxicity-in-large-language-models-with-perspective-api-c31c39b7a4d7) for safety products
- [Classification example](https://ai.google.dev/examples/train_text_classifier_embeddings) to create a toxicity classifier

#gemini-api #content-safety #harm-blocking