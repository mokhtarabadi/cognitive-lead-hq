---
title: Turn 1: Initial request with Google Search (built-in) and getWeather (custom) tools enabled
url: https://ai.google.dev/gemini-api/docs/tool-combination.md.txt
source: llms
fetched_at: 2026-04-29T11:17:03.506734773-03:00
rendered_js: false
word_count: 431
summary: This document explains how to integrate and use both built-in tools, like Google Search, and custom function-calling tools within a single Gemini model generation workflow.
tags:
    - gemini-api
    - function-calling
    - google-search
    - agentic-workflows
    - tool-use
    - multimodal-tools
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> [!WARNING]
> **Preview:** Built-in and custom tool combinations are in [Preview](https://cloud.google.com/products#product-launch-stages) and supported for [Gemini 3](https://ai.google.dev/gemini-api/docs/models#gemini-3) models only.

Gemini combines built-in tools (e.g., `google_search`) with custom function calling in a single generation, preserving tool call context history. This enables complex agentic workflows where the model grounds itself in real-time web data before calling your business logic.

## Python

```python
from google import genai
from google.genai import types

client = genai.Client()

getWeather = {
    "name": "getWeather",
    "description": "Gets the weather for a requested city.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city and state, e.g. Utqiaġvik, Alaska",
            },
        },
        "required": ["city"],
    },
}

# Turn 1: Initial request with Google Search (built-in) and getWeather (custom) tools enabled
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="What is the northernmost city in the United States? What's the weather like there today?",
    config=types.GenerateContentConfig(
      tools=[
        types.Tool(
          google_search=types.ToolGoogleSearch(),  # Built-in tool
          function_declarations=[getWeather]       # Custom tool
        ),
      ],
      include_server_side_tool_invocations=True
    ),
)

for part in response.candidates[0].content.parts:
    if part.tool_call:
        print(f"Tool call: {part.tool_call.tool_type} (ID: {part.tool_call.id})")
    if part.tool_response:
        print(f"Tool response: {part.tool_response.tool_type} (ID: {part.tool_response.id})")
    if part.function_call:
        print(f"Function call: {part.function_call.name} (ID: {part.function_call.id})")

# Turn 2: Manually build history to circulate both tool and function context
history = [
    types.Content(
        role="user",
        parts=[types.Part(text="What is the northernmost city in the United States? What's the weather like there today?")]
    ),
    # Response from Turn 1 includes tool_call, tool_response, and thought_signatures
    response.candidates[0].content,
    # Return the function_response
    types.Content(
        role="user",
        parts=[types.Part(
            function_response=types.FunctionResponse(
                name="getWeather",
                response={"response": "Very cold. 22 degrees Fahrenheit."},
                id=response.candidates[0].content.parts[2].function_call.id
            )
        )]
    )
]

response_2 = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=history,
    config=types.GenerateContentConfig(
      tools=[
        types.Tool(
          google_search=types.ToolGoogleSearch(),
          function_declarations=[getWeather]
        ),
      ],
      include_server_side_tool_invocations=True
    ),
)

for part in response_2.candidates[0].content.parts:
    if part.text:
        print(part.text)
```

## JavaScript

```javascript
import { GoogleGenAI } from '@google/genai';

const client = new GoogleGenAI({});

const getWeather = {
    name: "getWeather",
    description: "Get the weather in a given location",
    parameters: {
        type: "OBJECT",
        properties: {
            location: {
                type: "STRING",
                description: "The city and state, e.g. San Francisco, CA"
            }
        },
        required: ["location"]
    }
};

async function run() {
    const model = client.getGenerativeModel({
        model: "gemini-3-flash-preview",
    });

    const tools = [
      { googleSearch: {} },
      { functionDeclarations: [getWeather] }
    ];
    const toolConfig = { includeServerSideToolInvocations: true };

    // Turn 1
    const result1 = await model.generateContent({
        contents: [{role: "user", parts: [{text: "What is the northernmost city in the United States? What's the weather like there today?"}]}],
        tools: tools,
        toolConfig: toolConfig,
    });

    const response1 = result1.response;

    for (const part of response1.candidates[0].content.parts) {
        if (part.toolCall) console.log(`Tool call: ${part.toolCall.toolType} (ID: ${part.toolCall.id})`);
        if (part.toolResponse) console.log(`Tool response: ${part.toolResponse.toolType} (ID: ${part.toolResponse.id})`);
        if (part.functionCall) console.log(`Function call: ${part.functionCall.name} (ID: ${part.functionCall.id})`);
    }

    const functionCallId = response1.candidates[0].content.parts.find(p => p.functionCall)?.functionCall?.id;

    // Turn 2
    const history = [
        { role: "user", parts:[{text: "What is the northernmost city in the United States? What's the weather like there today?"}] },
        response1.candidates[0].content,
        {
            role: "user",
            parts: [{
                functionResponse: {
                    name: "getWeather",
                    response: {response: "Very cold. 22 degrees Fahrenheit."},
                    id: functionCallId
                }
            }]
        }
    ];

    const result2 = await model.generateContent({
        contents: history,
        tools: tools,
        toolConfig: toolConfig,
    });

    for (const part of result2.response.candidates[0].content.parts) {
        if (part.text) console.log(part.text);
    }
}

run();
```

## Go

```go
package main

import (
    "context"
    "fmt"
    "log"
    "os"

    "github.com/google/generative-ai-go/genai"
    "google.golang.org/api/option"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, option.WithAPIKey(os.Getenv("GEMINI_API_KEY")))
    if err != nil {
        log.Exit(err)
    }
    defer client.Close()

    getWeather := &genai.FunctionDeclaration{
        Name:        "getWeather",
        Description: "Get the weather in a given location",
        Parameters: &genai.Schema{
            Type: genai.Object,
            Properties: map[string]*genai.Schema{
                "location": {
                    Type:        genai.String,
                    Description: "The city and state, e.g. San Francisco, CA",
                },
            },
            Required: []string{"location"},
        },
    }

    model := client.GenerativeModel("gemini-3-flash-preview")
    model.Tools = []*genai.Tool{
        {GoogleSearch: &genai.GoogleSearch{}},
        {FunctionDeclarations: []*genai.FunctionDeclaration{getWeather}},
    }
    ist := true
    model.ToolConfig = &genai.ToolConfig{
        IncludeServerSideToolInvocations: &ist,
    }

    chat := model.StartChat()

    // Turn 1
    prompt := genai.Text("What is the northernmost city in the United States? What's the weather like there today?")
    resp1, err := chat.SendMessage(ctx, prompt)
    if err != nil {
        log.Exitf("SendMessage failed: %v", err)
    }

    if resp1 == nil || len(resp1.Candidates) == 0 || resp1.Candidates[0].Content == nil {
        log.Exit("empty response from model")
    }

    var functionCallID string
    for _, part := range resp1.Candidates[0].Content.Parts {
        switch p := part.(type) {
        case genai.FunctionCall:
            fmt.Printf("Function call: %s (ID: %s)\n", p.Name, p.ID)
            if p.Name == "getWeather" {
                functionCallID = p.ID
            }
        case genai.ToolCallPart:
            fmt.Printf("Tool call: %s (ID: %s)\n", p.ToolType, p.ID)
        case genai.ToolResponsePart:
            fmt.Printf("Tool response: %s (ID: %s)\n", p.ToolType, p.ID)
        }
    }

    if functionCallID == "" {
        log.Exit("no getWeather function call in response")
    }

    // Turn 2
    fr := genai.FunctionResponse{
        Name: "getWeather",
        ID:   functionCallID,
        Response: map[string]any{
            "response": "Very cold. 22 degrees Fahrenheit.",
        },
    }

    resp2, err := chat.SendMessage(ctx, fr)
    if err != nil {
        log.Exitf("SendMessage for turn 2 failed: %v", err)
    }

    if resp2 == nil || len(resp2.Candidates) == 0 || resp2.Candidates[0].Content == nil {
        log.Exit("empty response from model in turn 2")
    }

    for _, part := range resp2.Candidates[0].Content.Parts {
        if txt, ok := part.(genai.Text); ok {
            fmt.Println(string(txt))
        }
    }
}
```

## REST

```bash
# Turn 1: Initial request with Google Search (built-in) and getWeather (custom) tools enabled
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
-H "Content-Type: application/json" \
-H "x-goog-api-key: $GEMINI_API_KEY" \
-d '{
  "contents": [{
    "role": "user",
    "parts": [{
      "text": "What is the northernmost city in the United States? What'\''s the weather like there today?"
    }]
  }],
  "tools": [{
    "googleSearch": {}
  }, {
    "functionDeclarations": [{
      "name": "getWeather",
      "description": "Get the weather in a given location",
      "parameters": {
          "type": "OBJECT",
          "properties": {
              "location": {
                  "type": "STRING",
                  "description": "The city and state, e.g. San Francisco, CA"
              }
          },
          "required": ["location"]
      }
    }]
  }],
  "toolConfig": {
    "includeServerSideToolInvocations": true
  }
}'

# Turn 2: Manually build history to circulate both tool and function context
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
-H "Content-Type: application/json" \
-H "x-goog-api-key: $GEMINI_API_KEY" \
-d '{
  "contents": [
    {
      "role": "user",
      "parts": [{"text": "What is the northernmost city in the United States? What'\''s the weather like there today?"}]
    },
    YOUR_CANDIDATE_CONTENT_FROM_TURN_1_RESPONSE,
    {
      "role": "user",
      "parts": [{
        "functionResponse": {
          "name": "getWeather",
          "id": "FUNCTION_CALL_ID",
          "response": {"response": "Very cold. 22 degrees Fahrenheit."}
        }
      }]
    }
  ],
  "tools": [{
    "googleSearch": {}
  }, {
    "functionDeclarations": [{
      "name": "getWeather",
      "description": "Get the weather in a given location",
      "parameters": {
          "type": "OBJECT",
          "properties": {
              "location": {
                  "type": "STRING",
                  "description": "The city and state, e.g. San Francisco, CA"
              }
          },
          "required": ["location"]
      }
    }]
  }],
  "toolConfig": {
    "includeServerSideToolInvocations": true
  }
}'
```

## How it works

Gemini 3 uses *tool context circulation* to enable built-in and custom tool combinations, preserving and exposing built-in tool context across turns.

### Enable tool combination

1. Set `include_server_side_tool_invocations` flag to `true`
2. Include `function_declarations` with built-in tools to trigger combination behavior

> [!NOTE]
> If you don't include `function_declarations`, tool context circulation still applies to built-in tools when the flag is set.

### API returns parts

| Part type | Purpose |
|-----------|---------|
| `toolCall` + `toolResponse` | Preserve context of server-side tools and their results |
| `functionCall` + `functionResponse` | Standard function calling (not unique to tool combination) |
| `executableCode` + `codeExecutionResult` | Code Execution tool (uses built-in context circulation) |

Return **all parts exactly as received** in subsequent requests to maintain context.

### Critical fields in returned parts

| Field | Found in | Description |
|-------|----------|-------------|
| `id` | All tool-related parts | Maps call to response; required in function response |
| `tool_type` | `toolCall`, `toolResponse` | Identifies specific tool (e.g., `URL_CONTEXT`, `getWeather`) |
| `thought_signature` | All parts | Encrypted context; model errors without all signatures |

### Tool-specific data

| Tool | Tool call args | Tool response |
|------|---------------|---------------|
| **GOOGLE_SEARCH** | `queries` | `search_suggestions` |
| **GOOGLE_MAPS** | `queries` | `places`, `google_maps_widget_context_token` |
| **URL_CONTEXT** | `urls` | `urls_metadata`, `retrieved_url`, `url_retrieval_status` |
| **FILE_SEARCH** | None | None |

## Example request structure

```json
{
  "model": "models/gemini-3-flash-preview",
  "contents": [{
    "parts": [{ "text": "What is the northernmost city in the United States? What's the weather like there today?" }],
    "role": "user"
  }, {
    "parts": [
      {
        "thoughtSignature": "...",
        "toolCall": {
          "toolType": "GOOGLE_SEARCH_WEB",
          "args": { "queries": ["northernmost city in the United States"] },
          "id": "a7b3k9p2"
        }
      }, {
        "thoughtSignature": "...",
        "toolResponse": {
          "toolType": "GOOGLE_SEARCH_WEB",
          "response": { "search_suggestions": "..." },
          "id": "a7b3k9p2"
        }
      }, {
        "functionCall": {
          "name": "getWeather",
          "args": { "city": "Utqiaġvik, Alaska" },
          "id": "m4q8z1v6"
        },
        "thoughtSignature": "..."
      }
    ],
    "role": "model"
  }, {
    "parts": [{
      "functionResponse": {
        "name": "getWeather",
        "response": { "response": "Very cold. 22 degrees Fahrenheit." },
        "id": "m4q8z1v6"
      }
    }],
    "role": "user"
  }],
  "tools": [
    { "functionDeclarations": [{ "name": "getWeather" }] },
    { "googleSearch": {} },
    { "codeExecution": {} }
  ],
  "toolConfig": { "includeServerSideToolInvocations": true }
}
```

## Tokens and pricing

`toolCall` and `toolResponse` parts are counted towards `prompt_token_count` in requests (not responses). Google Search is exempt—uses its own query-level pricing.

## Limitations

- Default to `VALIDATED` mode (`AUTO` not supported) when `include_server_side_tool_invocations` is enabled
- Built-in tools rely on location/time info; conflicting `system_instruction` or `function_declaration.description` may reduce effectiveness

## Supported tools

| Tool | Execution | Context Circulation |
|------|-----------|---------------------|
| [Google Search](https://ai.google.dev/gemini-api/docs/google-search) | Server-side | Supported |
| [Google Maps](https://ai.google.dev/gemini-api/docs/maps-grounding) | Server-side | Supported |
| [URL Context](https://ai.google.dev/gemini-api/docs/url-context) | Server-side | Supported |
| [File Search](https://ai.google.dev/gemini-api/docs/file-search) | Server-side | Supported |
| [Code Execution](https://ai.google.dev/gemini-api/docs/code-execution) | Server-side | Supported (uses `executableCode`/`codeExecutionResult`) |
| [Computer Use](https://ai.google.dev/gemini-api/docs/computer-use) | Client-side | Supported (uses `functionCall`/`functionResponse`) |
| [Custom functions](https://ai.google.dev/gemini-api/docs/function-calling) | Client-side | Supported (uses `functionCall`/`functionResponse`) |

#topic-tool-use #topic-agentic-workflows #topic-google-search
