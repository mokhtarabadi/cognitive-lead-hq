---
title: Gemini API
url: https://ai.google.dev/gemini-api/docs.md.txt
source: llms
fetched_at: 2026-04-29T11:16:13.091002388-03:00
rendered_js: false
word_count: 293
summary: This document provides an overview of the Gemini API, showcasing multi-language code implementations and highlighting key generative AI capabilities, model options, and development tools.
tags:
    - gemini-api
    - generative-ai
    - multimodal
    - api-integration
    - developer-tools
    - machine-learning
category: api
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
# Gemini API

> [!IMPORTANT]
> We have updated our [Terms of Service](https://ai.google.dev/gemini-api/terms).

The fastest path from prompt to production with Gemini, Veo, Nano Banana, and more.

## Quick Examples

### Python

```python
from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain how AI works in a few words",
)

print(response.text)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
    const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: "Explain how AI works in a few words",
    });
    console.log(response.text);
}

await main();
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

    result, err := client.Models.GenerateContent(
        ctx,
        "gemini-3-flash-preview",
        genai.Text("Explain how AI works in a few words"),
        nil,
    )
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(result.Text())
}
```

### Java

```java
package com.example;

import com.google.genai.Client;
import com.google.genai.types.GenerateContentResponse;

public class GenerateTextFromTextInput {
    public static void main(String[] args) {
        Client client = new Client();

        GenerateContentResponse response =
            client.models.generateContent(
                "gemini-3-flash-preview",
                "Explain how AI works in a few words",
                null);

        System.out.println(response.text());
    }
}
```

### C\#

```csharp
using System.Threading.Tasks;
using Google.GenAI;
using Google.GenAI.Types;

public class GenerateContentSimpleText {
    public static async Task main() {
        var client = new Client();
        var response = await client.Models.GenerateContentAsync(
            model: "gemini-3-flash-preview", contents: "Explain how AI works in a few words"
        );
        Console.WriteLine(response.Candidates[0].Content.Parts[0].Text);
    }
}
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
        "contents": [
            {
                "parts": [
                    {
                        "text": "Explain how AI works in a few words"
                    }
                ]
            }
        ]
    }'
```

[Start building](https://ai.google.dev/gemini-api/docs/quickstart) — Follow the Quickstart guide to get an API key and make your first API call.

## Meet the Models

| Model | Description |
|---|---|
| [Gemini 3.1 Pro](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview) | Most intelligent model for multimodal understanding, reasoning, and agentic capabilities |
| [Gemini 3 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3-flash-preview) | Frontier-class performance rivaling larger models at a fraction of the cost |
| [Gemini 3.1 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-preview) | High-volume, cost-sensitive workhorse model |
| [Nano Banana 2 and Nano Banana Pro](https://ai.google.dev/gemini-api/docs/image-generation) | State-of-the-art image generation and editing |
| [Veo 3.1](https://ai.google.dev/gemini-api/docs/video) | Video generation with native audio |
| [Gemini Robotics](https://ai.google.dev/gemini-api/docs/robotics-overview) | Vision-language model for robotics and physical world reasoning |

[View all models](https://ai.google.dev/gemini-api/docs/models)

## Explore Capabilities

- **Native Image Generation** — [Generate and edit images](https://ai.google.dev/gemini-api/docs/image-generation) natively with Gemini 2.5 Flash Image
- **Long Context** — Process [millions of tokens](https://ai.google.dev/gemini-api/docs/long-context) from unstructured images, videos, and documents
- **Structured Outputs** — Constrain Gemini to respond with [JSON](https://ai.google.dev/gemini-api/docs/structured-output)
- **Function Calling** — Connect Gemini to [external APIs and tools](https://ai.google.dev/gemini-api/docs/function-calling)
- **Video Generation** — [Create video](https://ai.google.dev/gemini-api/docs/video) from text or image prompts
- **Voice Agents** — [Real-time voice applications](https://ai.google.dev/gemini-api/docs/live) with Live API
- **Tools** — Connect to [Google Search, Maps, Code Execution](https://ai.google.dev/gemini-api/docs/tools)
- **Document Understanding** — Process [up to 1000 pages](https://ai.google.dev/gemini-api/docs/document-processing) of PDFs
- **Thinking** — Improve [reasoning for complex tasks](https://ai.google.dev/gemini-api/docs/thinking)
- **Google AI Studio** — [Test prompts, manage keys](https://aistudio.google.com), monitor usage
- **Developer Community** — [Ask questions](https://discuss.ai.google.dev/c/gemini-api/4) from other developers and Google engineers
- **API Reference** — [Detailed API documentation](https://ai.google.dev/api)
- **Status** — [Check service status](https://aistudio.google.com/status)
