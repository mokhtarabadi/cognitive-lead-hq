---
title: Gemini thinking
url: https://ai.google.dev/gemini-api/docs/thinking.md.txt
source: llms
fetched_at: 2026-04-29T11:18:05.795250274-03:00
rendered_js: false
word_count: 857
summary: This guide explains how to utilize the thinking capabilities of Gemini models via the API, including how to enable thought summaries in both standard and streaming responses.
tags:
    - gemini-api
    - reasoning-models
    - thinking-process
    - content-generation
    - thought-summaries
    - ai-integration
category: guide
optimized: true
optimized_at: 2026-04-29T12:00:00Z
---
Gemini 3 and 2.5 series models use an internal "thinking process" that improves reasoning and multi-step planning for complex tasks: coding, advanced mathematics, data analysis.

## Generating content with thinking

Use a thinking-enabled model in the `model` field:

### Python

```python
from google import genai

client = genai.Client()
prompt = "Explain the concept of Occam's Razor and provide a simple, everyday example."
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt
)

print(response.text)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const prompt = "Explain the concept of Occam's Razor...";
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: prompt,
  });
  console.log(response.text);
}

main();
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

  prompt := "Explain the concept of Occam's Razor..."
  model := "gemini-3-flash-preview"

  resp, _ := client.Models.GenerateContent(ctx, model, genai.Text(prompt), nil)
  fmt.Println(resp.Text())
}
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
 -H "x-goog-api-key: $GEMINI_API_KEY" \
 -H 'Content-Type: application/json' \
 -X POST \
 -d '{
   "contents": [{"parts": [{"text": "Explain the concept of Occam's Razor..."}]}]
 }'
```

## Thought summaries

Summarized versions of the model's raw thoughts—insight into internal reasoning. Note: thinking levels/budgets apply to raw thoughts, not summaries.

Enable with `includeThoughts: true`, then access via `response` parts checking `thought` boolean.

### Without streaming (single final summary):

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()
prompt = "What is the sum of the first 50 prime numbers?"
response = client.models.generate_content(
  model="gemini-3-flash-preview",
  contents=prompt,
  config=types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
      include_thoughts=True
    )
  )
)

for part in response.candidates[0].content.parts:
  if not part.text:
    continue
  if part.thought:
    print("Thought summary:")
    print(part.text)
    print()
  else:
    print("Answer:")
    print(part.text)
    print()
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "What is the sum of the first 50 prime numbers?",
    config: {
      thinkingConfig: {
        includeThoughts: true,
      },
    },
  });

  for (const part of response.candidates[0].content.parts) {
    if (!part.text) continue;
    else if (part.thought) {
      console.log("Thoughts summary:");
      console.log(part.text);
    } else {
      console.log("Answer:");
      console.log(part.text);
    }
  }
}

main();
```

### Go

```go
package main

import (
  "context"
  "fmt"
  "google.golang.org/genai"
)

func main() {
  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  contents := genai.Text("What is the sum of the first 50 prime numbers?")
  model := "gemini-3-flash-preview"
  resp, _ := client.Models.GenerateContent(ctx, model, contents, &genai.GenerateContentConfig{
    ThinkingConfig: &genai.ThinkingConfig{
      IncludeThoughts: true,
    },
  })

  for _, part := range resp.Candidates[0].Content.Parts {
    if part.Text != "" {
      if part.Thought {
        fmt.Println("Thoughts Summary:")
        fmt.Println(part.Text)
      } else {
        fmt.Println("Answer:")
        fmt.Println(part.Text)
      }
    }
  }
}
```

### With streaming (rolling incremental summaries):

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

prompt = """
Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue.
The person who lives in the red house owns a cat.
Bob does not live in the green house.
Carol owns a dog.
The green house is to the left of the red house.
Alice does not own a cat.
Who lives in each house, and what pet do they own?
"""

thoughts = ""
answer = ""

for chunk in client.models.generate_content_stream(
    model="gemini-3-flash-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
      thinking_config=types.ThinkingConfig(
        include_thoughts=True
      )
    )
):
  for part in chunk.candidates[0].content.parts:
    if not part.text:
      continue
    elif part.thought:
      if not thoughts:
        print("Thoughts summary:")
      print(part.text)
      thoughts += part.text
    else:
      if not answer:
        print("Answer:")
      print(part.text)
      answer += part.text
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const prompt = `Alice, Bob, and Carol each live in different houses: red, green, blue...`;

let thoughts = "";
let answer = "";

async function main() {
  const response = await ai.models.generateContentStream({
    model: "gemini-3-flash-preview",
    contents: prompt,
    config: {
      thinkingConfig: {
        includeThoughts: true,
      },
    },
  });

  for await (const chunk of response) {
    for (const part of chunk.candidates[0].content.parts) {
      if (!part.text) continue;
      else if (part.thought) {
        if (!thoughts) console.log("Thoughts summary:");
        console.log(part.text);
        thoughts += part.text;
      } else {
        if (!answer) console.log("Answer:");
        console.log(part.text);
        answer += part.text;
      }
    }
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
  "google.golang.org/genai"
)

func main() {
  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  prompt := `Alice, Bob, and Carol each live in different houses...`
  contents := genai.Text(prompt)
  model := "gemini-3-flash-preview"

  resp := client.Models.GenerateContentStream(ctx, model, contents, &genai.GenerateContentConfig{
    ThinkingConfig: &genai.ThinkingConfig{
      IncludeThoughts: true,
    },
  })

  for chunk := range resp {
    for _, part := range chunk.Candidates[0].Content.Parts {
      if len(part.Text) == 0 {
        continue
      }
      if part.Thought {
        fmt.Printf("Thought: %s\n", part.Text)
      } else {
        fmt.Printf("Answer: %s\n", part.Text)
      }
    }
  }
}
```

## Controlling thinking

Models engage dynamic thinking by default, adjusting effort based on query complexity. Use parameters to control behavior.

### Thinking levels (Gemini 3)

`thinkingLevel` parameter controls reasoning. Recommended for Gemini 3 and onwards.

| Thinking Level | 3.1 Pro | 3.1 Flash-Lite | 3 Flash | Description |
|---|---|---|---|---|
| **`minimal`** | Not supported | Supported (Default) | Supported | Minimal latency. May think very minimally for complex coding. Note: doesn't guarantee thinking is off. |
| **`low`** | Supported | Supported | Supported | Minimizes latency/cost. Simple instruction following, chat, high-throughput. |
| **`medium`** | Supported | Supported | Supported | Balanced for most tasks. |
| **`high`** | Supported (Default, Dynamic) | Supported (Dynamic) | Supported (Default, Dynamic) | Maximizes reasoning depth. Longer to first output, more carefully reasoned. |

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Provide a list of 3 famous physicists and their key contributions",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="low")
    ),
)

print(response.text)
```

### JavaScript

```javascript
import { GoogleGenAI, ThinkingLevel } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "Provide a list of 3 famous physicists...",
    config: {
      thinkingConfig: {
        thinkingLevel: ThinkingLevel.LOW,
      },
    },
  });
  console.log(response.text);
}

main();
```

### Go

```go
package main

import (
  "context"
  "fmt"
  "google.golang.org/genai"
)

func main() {
  thinkingLevelVal := "low"
  resp, _ := client.Models.GenerateContent(ctx, model, contents, &genai.GenerateContentConfig{
    ThinkingConfig: &genai.ThinkingConfig{
      ThinkingLevel: &thinkingLevelVal,
    },
  })
  fmt.Println(resp.Text())
}
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
-H "x-goog-api-key: $GEMINI_API_KEY" \
-H 'Content-Type: application/json' \
-X POST \
-d '{
  "contents": [{"parts": [{"text": "Provide a list of 3 famous physicists..."}]}],
  "generationConfig": {
    "thinkingConfig": {"thinkingLevel": "low"}
  }
}'
```

> [!NOTE]
> - Cannot disable thinking for Gemini 3.1 Pro
> - Gemini 3 Flash and Flash-Lite don't support full thinking-off; `minimal` means likely won't think
> - Default: Gemini 3 uses dynamic `"high"`
> - Gemini 2.5 series doesn't support `thinkingLevel`—use `thinkingBudget` instead

### Thinking budgets (Gemini 2.5)

`thinkingBudget` guides number of thinking tokens. Use `thinkingLevel` with Gemini 3; `thinkingBudget` for backwards compatibility.

| Model | Default | Range | Disable | Dynamic |
|---|---|---|---|---|
| **2.5 Pro** | Dynamic | `128` to `32768` | N/A (cannot) | `thinkingBudget = -1` (Default) |
| **2.5 Flash** | Dynamic | `0` to `24576` | `thinkingBudget = 0` | `thinkingBudget = -1` (Default) |
| **2.5 Flash Preview** | Dynamic | `0` to `24576` | `thinkingBudget = 0` | `thinkingBudget = -1` (Default) |
| **2.5 Flash Lite** | No thinking | `512` to `24576` | `thinkingBudget = 0` | `thinkingBudget = -1` |
| **2.5 Flash Lite Preview** | No thinking | `512` to `24576` | `thinkingBudget = 0` | `thinkingBudget = -1` |
| **Robotics-ER 1.6 Preview** | Dynamic | `0` to `24576` | `thinkingBudget = 0` | `thinkingBudget = -1` (Default) |

### Python

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Provide a list of 3 famous physicists...",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024)
        # Turn off thinking: thinking_budget=0
        # Dynamic thinking: thinking_budget=-1
    ),
)
```

### JavaScript

```javascript
const response = await ai.models.generateContent({
  model: "gemini-2.5-flash",
  contents: "Provide a list of 3 famous physicists...",
  config: {
    thinkingConfig: {
      thinkingBudget: 1024,
      // thinkingBudget: 0  // turn off
      // thinkingBudget: -1 // dynamic
    },
  },
});
```

### Go

```go
thinkingBudgetVal := int32(1024)
resp, _ := client.Models.GenerateContent(ctx, model, contents, &genai.GenerateContentConfig{
  ThinkingConfig: &genai.ThinkingConfig{
    ThinkingBudget: &thinkingBudgetVal,
    // ThinkingBudget: int32(0)  // turn off
    // ThinkingBudget: int32(-1) // dynamic
  },
})
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
-H "x-goog-api-key: $GEMINI_API_KEY" \
-H 'Content-Type: application/json' \
-X POST \
-d '{
  "contents": [{"parts": [{"text": "Provide a list of 3 famous physicists..."}]}],
  "generationConfig": {
    "thinkingConfig": {"thinkingBudget": 1024}
  }
}'
```

Model may overflow or underflow token budget depending on prompt.

## Thought signatures

> [!IMPORTANT]
> The [Google GenAI SDK](https://ai.google.dev/gemini-api/docs/libraries) automatically handles thought signatures. Only [manage manually](https://ai.google.dev/gemini-api/docs/function-calling#thought-signatures) when modifying conversation history or using REST API.

The API is stateless—each request is independent with no access to previous turn's thought context. [028-docs-thought-signatures](Thought signatures) are encrypted representations enabling context across multi-turn interactions.

- **Gemini 2.5 models:** Return signatures when thinking enabled and request includes [function calling](https://ai.google.dev/gemini-api/docs/function-calling#thinking), specifically [function declarations](https://ai.google.dev/gemini-api/docs/function-calling#step-2)
- **Gemini 3 models:** May return signatures for all types of [parts](https://ai.google.dev/api/caching#Part)—always pass all signatures back as received (required for function calling)

**Rules:**
- Return entire response with all parts back to model in subsequent turns
- Don't concatenate parts with signatures together
- Don't merge a signature part with another part without a signature

## Pricing

> [!NOTE]
> **Summaries** available in free and paid tiers. **Thought signatures** increase input token charges when sent back.

Thinking-on response pricing = output tokens + thinking tokens. Get thinking token count from `thoughtsTokenCount`.

### Python

```python
print("Thoughts tokens:", response.usage_metadata.thoughts_token_count)
print("Output tokens:", response.usage_metadata.candidates_token_count)
```

### JavaScript

```javascript
console.log(`Thoughts tokens: ${response.usageMetadata.thoughtsTokenCount}`);
console.log(`Output tokens: ${response.usageMetadata.candidatesTokenCount}`);
```

### Go

```go
usageMetadata, _ := json.MarshalIndent(response.UsageMetadata, "", "  ")
fmt.Println("Thoughts tokens:", string(usageMetadata.thoughts_token_count))
fmt.Println("Output tokens:", string(usageMetadata.candidates_token_count))
```

Pricing is based on full thought tokens the model generates to create the summary, not just the output summary. Learn more about tokens in the [Token counting](https://ai.google.dev/gemini-api/docs/tokens) guide.

## Best practices

Follow [[023-docs-prompting-strategies|prompting guidance and best practices]] for best results.

### Debugging and steering

- **Review reasoning:** Analyze thought summaries when responses aren't expected. See how model broke down task and arrived at conclusion to correct toward right results.
- **Provide guidance in reasoning:** For lengthy output, constrain [amount of thinking](https://ai.google.dev/gemini-api/docs/thinking#set-budget) in prompt to reserve more output tokens for response.

### Task complexity

| Complexity | Thinking | Examples |
|---|---|---|
| **Easy** | Not required | "Where was DeepMind founded?", "Is this email asking for a meeting or just providing information?" |
| **Medium** | Default/Some | "Analogize photosynthesis and growing up", "Compare and contrast electric cars and hybrid cars" |
| **Hard** | Maximum | "Solve problem 1 in AIME 2025: Find sum of integer bases b > 9 for which 17~b~ divides 97~b~", "Write Python web app for real-time stock visualization with authentication" |

## Supported models, tools, and capabilities

All 3 and 2.5 series models support thinking. See [model overview](https://ai.google.dev/gemini-api/docs/models) for all capabilities.

Thinking models work with all Gemini tools and capabilities—interact with external systems, execute code, access real-time information, incorporating results into reasoning.

[Thinking cookbook examples](https://colab.sandbox.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_thinking.ipynb)

## What's next?

- [OpenAI Compatibility guide](https://ai.google.dev/gemini-api/docs/openai#thinking) for thinking coverage

#gemini-api #reasoning-models #thought-summaries