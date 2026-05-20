---
title: Validate for graceful downgrade
url: https://ai.google.dev/gemini-api/docs/priority-inference.md.txt
source: llms
fetched_at: 2026-04-29T11:16:54.235370109-03:00
rendered_js: false
word_count: 562
summary: This document explains how to utilize the Gemini Priority API tier for business-critical workloads that require high reliability and low latency. It covers configuration requirements, the automatic graceful downgrade mechanism, and implementation best practices across various programming languages.
tags:
    - gemini-api
    - priority-tier
    - latency-optimization
    - inference
    - api-configuration
    - service-tier
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> [!warning]
> **Preview:** The Gemini Priority API is in [Preview](https://cloud.google.com/products#product-launch-stages).

The Gemini Priority API is a premium inference tier for business-critical workloads requiring lower latency and highest reliability at a premium price. Traffic is prioritized above standard and Flex tiers.

Priority inference is available to [Tier 2 & Tier 3|021-docs-optimization#about-billing](https://ai.google.dev/gemini-api/docs/billing#about-billing) users across the GenerateContent API and Interactions API endpoints.

## How to use Priority

Set the `service_tier` field in the request body to `priority`. The default tier is standard if omitted.

### Python

```python
from google import genai

client = genai.Client()

try:
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="Triage this critical customer support ticket immediately.",
        config={"service_tier": "priority"},
    )

    # Validate for graceful downgrade
    if response.sdk_http_response.headers.get("x-gemini-service-tier") == "standard":
        print("Warning: Priority limit exceeded, processed at Standard tier.")

    print(response.text)

except Exception as e:
    # Standard error handling (e.g., DEADLINE_EXCEEDED)
    print(f"Error during API call: {e}")
```

### JavaScript

```javascript
import {GoogleGenAI} from '@google/genai';

const ai = new GoogleGenAI({});

async function main() {
  try {
      const result = await ai.models.generateContent({
          model: "gemini-3-flash-preview",
          contents: "Triage this critical customer support ticket immediately.",
          config: {serviceTier: "priority"},
      });

      // Validate for graceful downgrade
      if (result.sdkHttpResponse.headers.get("x-gemini-service-tier") === "standard") {
          console.log("Warning: Priority limit exceeded, processed at Standard tier.");
      }

      console.log(result.text);

  } catch (e) {
      console.log(`Error during API call: ${e}`);
  }
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
    defer client.Close()

    resp, err := client.Models.GenerateContent(
        ctx,
        "gemini-3-flash-preview",
        genai.Text("Triage this critical customer support ticket immediately."),
        &genai.GenerateContentConfig{
            ServiceTier: "priority",
        },
    )
    if err != nil {
        log.Fatalf("Error during API call: %v", err)
    }

    // Validate for graceful downgrade
    if resp.SDKHTTPResponse.Header.Get("x-gemini-service-tier") == "standard" {
        fmt.Println("Warning: Priority limit exceeded, processed at Standard tier.")
    }

    fmt.Println(resp.Text())
}
```

### REST

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=$GEMINI_API_KEY" \
-H "Content-Type: application/json" \
-d '{
  "contents": [{
    "parts":[{"text": "Analyze user sentiment in real time"}]
  }],
  "service_tier": "priority"
}'
```

## How Priority inference works

Priority inference routes requests to high-criticality compute queues, offering predictable, fast performance for user-facing applications. Its primary mechanism is a graceful server-side downgrade to standard processing for traffic exceeding dynamic limits, ensuring application stability instead of failing requests.

| Feature | Priority | Standard | Flex | Batch |
|---|---|---|---|---|
| **Pricing** | 75-100% more than Standard | Full price | 50% discount | 50% discount |
| **Latency** | Seconds | Seconds to minutes | Minutes (1--15 min target) | Up to 24 hours |
| **Reliability** | High (Non-sheddable) | High / Medium-high | Best-effort (Sheddable) | High (for throughput) |
| **Interface** | Synchronous | Synchronous | Synchronous | Asynchronous |

### Key benefits

- **Low latency**: Designed for second response times for interactive, user-facing AI tools.
- **High reliability**: Traffic is treated with highest criticality and is strictly non-sheddable.
- **Graceful degradation**: Traffic spikes exceeding dynamic limits are automatically downgraded to Standard tier instead of failing, preventing service outages.
- **Low friction**: Uses the same synchronous `generateContent` method as standard and Flex tiers.

### Use cases

- **Interactive AI applications**: Customer service chatbots and copilots where users expect fast, consistent responses.
- **Real-time decision engines**: Systems requiring highly reliable, low-latency outcomes such as live ticket triaging or fraud detection.
- **Premium customer features**: Developers needing higher service level objectives (SLOs) for paying customers.

### Rate limits

Priority consumption holds its own rate limits even though counted towards [overall interactive traffic rate limits](https://aistudio.google.com/rate-limit). Default rate limits are **0.3x standard rate limit for Model / Tier**.

### Graceful downgrade logic

If Priority limits are exceeded due to congestion, overflow requests are **automatically and gracefully** downgraded to Standard processing instead of failing with a 503 or 429 error. Downgraded requests are billed at the standard rate, not the Priority premium rate.

### Client responsibility

- **Response monitoring**: Monitor the `x-gemini-service-tier` header in the API response to detect if requests are being frequently downgraded to `standard`.
- **Retries**: Implement retry logic with exponential backoff for standard errors such as `DEADLINE_EXCEEDED`.

## Pricing

Priority inference is priced at 75-100% more than the [standard API|117-docs-pricing](https://ai.google.dev/gemini-api/docs/pricing) and billed per token.

## Supported models

| Model | Priority inference |
|---|---|
| [Gemini 3.1 Flash-Lite Preview|041-docs-models-gemini-3.1-flash-lite-preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-preview) | ✔️ |
| [Gemini 3.1 Pro Preview|043-docs-models-gemini-3.1-pro-preview](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview) | ✔️ |
| [Gemini 3 Flash Preview](https://ai.google.dev/gemini-api/docs/models/gemini-3-flash-preview) | ✔️ |
| [Gemini 3 Pro Image Preview|055-docs-models-gemini-3-pro-image-preview](https://ai.google.dev/gemini-api/docs/models/gemini-3-pro-image-preview) | ✔️ |
| [Gemini 2.5 Pro](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-pro) | ✔️ |
| [Gemini 2.5 Flash|049-docs-models-gemini-2.5-flash](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash) | ✔️ |
| [Gemini 2.5 Flash Image|045-docs-models-gemini-2.5-flash-image](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-image) | ✔️ |
| [Gemini 2.5 Flash-Lite|047-docs-models-gemini-2.5-flash-lite](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash-lite) | ✔️ |

## What's next

Read about Gemini's other [inference and optimization|021-docs-optimization](https://ai.google.dev/gemini-api/docs/optimization) options:

- [Flex inference](https://ai.google.dev/gemini-api/docs/flex-inference) for 50% cost reduction.
- [Batch API](https://ai.google.dev/gemini-api/docs/batch-api) for asynchronous processing within 24 hours.
- [Context caching](https://ai.google.dev/gemini-api/docs/caching) for reduced input token costs.

#priority-tier #inference #latency-optimization
