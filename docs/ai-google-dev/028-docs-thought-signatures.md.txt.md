---
title: Thought Signatures
url: https://ai.google.dev/gemini-api/docs/thought-signatures.md.txt
source: llms
fetched_at: 2026-04-29T11:17:01.723604609-03:00
rendered_js: false
word_count: 1032
summary: This document explains how to handle thought signatures when using Gemini 3 models for function calling, specifically focusing on the requirement to pass these encrypted tokens back in subsequent API requests to maintain reasoning context.
tags:
    - gemini-api
    - function-calling
    - thought-signatures
    - model-reasoning
    - api-integration
    - context-management
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> [!IMPORTANT]
> Thought signatures are handled automatically when using official [Google Gen AI SDKs](https://ai.google.dev/gemini-api/docs/libraries) and appending the full model response object directly to history. **You only need to work with thought signatures directly when using the REST API**, or if manually extracting and returning parts history in multi-turn conversations.

Thought signatures are encrypted representations of the model's internal thought process that preserve reasoning context across multi-step interactions. When using thinking models (Gemini 3 and 2.5 series), the API may return a `thoughtSignature` field within content parts (e.g., `text` or `functionCall` parts).

If you receive a thought signature in a model response, pass it back exactly as received when sending conversation history in the next turn. **With Gemini 3 models, you must pass back thought signatures during function calling—failure results in a 400 validation error.** This includes the `minimal` thinking level setting for Gemini 3 Flash.

## How it works

![Function calling turns and steps diagram](https://ai.google.dev/static/gemini-api/docs/images/fc-turns.png)

- **Turn**: A single complete exchange between user and model
- **Step**: A finer-grained action within a larger process to complete a turn

> [!NOTE]
> This document focuses on function calling for Gemini 3 models. See [[027-docs-thinking|Thinking]] for discrepancies with 2.5.

Gemini 3 returns thought signatures for all model responses with a function call:

- **Parallel function calls**: First `functionCall` part has the signature
- **Sequential function calls (multi-step)**: Each function call has a signature; you must pass all back
- **No function call**: Signature appears in the last part returned

### Multi-step function calling visualization

| Turn | Step | User Request | Model Response | FunctionResponse |
|------|------|--------------|----------------|------------------|
| 1 | 1 | `request1 = user_prompt` | `FC1 + signature` | `FR1` |
| 1 | 2 | `request2 = request1 + (FC1 + signature) + FR1` | `FC2 + signature` | `FR2` |
| 1 | 3 | `request3 = request2 + (FC2 + signature) + FR2` | `text_output (no FCs)` | None |

## Signatures in function calling parts

When Gemini generates a `functionCall`, it relies on the `thought_signature` to process the tool's output correctly in the next turn.

- **Single Function Call**: The `functionCall` part contains a `thought_signature`
- **Parallel Function Calls**: `thought_signature` attaches **only to the first** `functionCall` part; subsequent parts have no signature
- **Requirement**: Return the signature in the exact part where received
- **Validation**: Strict validation enforced for all function calls within the current turn:
  - API scans history (newest to oldest) to find the most recent User message with standard content (start of current turn)
  - All model `functionCall` turns after that User message are part of the turn
  - **First** `functionCall` part in each step **must** include its `thought_signature`
  - Omitting a signature for the first `functionCall` part in any step returns a 400 error

### Error format

```
Function call <Function Call> in the <index of contents array> content block is missing a `thought_signature`.
```

Example: `Function call FC1 in the 1. content block is missing a thought_signature.`

## Sequential function calling example

User: `"Check flight status for AA100 and book a taxi 2 hours before if delayed."`

| Turn | Step | User Request | Model Response | FunctionResponse |
|------|------|--------------|----------------|------------------|
| 1 | 1 | `request1="Check flight status..."` | `FC1 ("check_flight") + signature` | `FR1` |
| 1 | 2 | `request2 = request1 + FC1 + signature + FR1` | `FC2("book_taxi") + signature` | `FR2` |
| 1 | 3 | `request3 = request2 + FC2 + signature + FR2` | `text_output (no FCs)` | `None` |

**Turn 1, Step 1 (User request)**

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "Check flight status for AA100 and book a taxi 2 hours before if delayed."
        }
      ]
    }
  ],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "check_flight",
          "description": "Gets the current status of a flight",
          "parameters": {
            "type": "object",
            "properties": {
              "flight": {
                "type": "string",
                "description": "The flight number to check"
              }
            },
            "required": ["flight"]
          }
        },
        {
          "name": "book_taxi",
          "description": "Book a taxi",
          "parameters": {
            "type": "object",
            "properties": {
              "time": {
                "type": "string",
                "description": "time to book the taxi"
              }
            },
            "required": ["time"]
          }
        }
      ]
    }
  ]
}
```

**Turn 1, Step 1 (Model response)**

```json
{
  "content": {
    "role": "model",
    "parts": [
      {
        "functionCall": {
          "name": "check_flight",
          "args": { "flight": "AA100" }
        },
        "thoughtSignature": "<Signature A>"
      }
    ]
  }
}
```

**Turn 1, Step 2 (User response - Sending tool outputs)**

```json
{
  "role": "user",
  "parts": [
    {
      "text": "Check flight status for AA100 and book a taxi 2 hours before if delayed."
    }
  ]
},
{
  "role": "model",
  "parts": [
    {
      "functionCall": {
        "name": "check_flight",
        "args": { "flight": "AA100" }
      },
      "thoughtSignature": "<Signature A>"
    }
  ]
},
{
  "role": "user",
  "parts": [
    {
      "functionResponse": {
        "name": "check_flight",
        "response": {
          "status": "delayed",
          "departure_time": "12 PM"
        }
      }
    }
  ]
}
```

**Turn 1, Step 2 (Model)**

```json
{
  "content": {
    "role": "model",
    "parts": [
      {
        "functionCall": {
          "name": "book_taxi",
          "args": { "time": "10 AM" }
        },
        "thoughtSignature": "<Signature B>"
      }
    ]
  }
}
```

**Turn 1, Step 3 (User - Sending tool output)**

Include signatures for ALL function calls (`<Signature A>` + `<Signature B>`).

```json
{
  "role": "user",
  "parts": [
    {
      "text": "Check flight status for AA100 and book a taxi 2 hours before if delayed."
    }
  ]
},
{
  "role": "model",
  "parts": [
    {
      "functionCall": {
        "name": "check_flight",
        "args": { "flight": "AA100" }
      },
      "thoughtSignature": "<Signature A>"
    }
  ]
},
{
  "role": "user",
  "parts": [
    {
      "functionResponse": {
        "name": "check_flight",
        "response": {
          "status": "delayed",
          "departure_time": "12 PM"
        }
      }
    }
  ]
},
{
  "role": "model",
  "parts": [
    {
      "functionCall": {
        "name": "book_taxi",
        "args": { "time": "10 AM" }
      },
      "thoughtSignature": "<Signature B>"
    }
  ]
},
{
  "role": "user",
  "parts": [
    {
      "functionResponse": {
        "name": "book_taxi",
        "response": { "booking_status": "success" }
      }
    }
  ]
}
```

## Parallel function calling example

User: `"Check weather in Paris and London"`

| Turn | Step | User Request | Model Response | FunctionResponse |
|------|------|--------------|----------------|------------------|
| 1 | 1 | `request1="Check weather in Paris and London"` | `FC1 ("Paris") + signature, FC2 ("London")` | `FR1` |
| 1 | 2 | `request2 = request1 + FC1 + signature + FC2` | `text_output (no FCs)` | `None` |

**Turn 1, Step 1 (User request)**

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [{ "text": "Check the weather in Paris and London." }]
    }
  ],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "get_current_temperature",
          "description": "Gets the current temperature for a given location.",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "The city name, e.g. San Francisco"
              }
            },
            "required": ["location"]
          }
        }
      ]
    }
  ]
}
```

**Turn 1, Step 1 (Model response)**

```json
{
  "content": {
    "parts": [
      {
        "functionCall": {
          "name": "get_current_temperature",
          "args": { "location": "Paris" }
        },
        "thoughtSignature": "<Signature_A>"
      },
      {
        "functionCall": {
          "name": "get_current_temperature",
          "args": { "location": "London" }
        }
      }
    ]
  }
}
```

**Turn 1, Step 2 (User response - Sending tool outputs)**

```json
[
  { "role": "user", "parts": [{ "text": "Check the weather in Paris and London." }] },
  {
    "role": "model",
    "parts": [
      {
        "functionCall": {
          "name": "get_current_temperature",
          "args": { "city": "Paris" }
        },
        "thought_signature": "<Signature_A>"
      },
      { "functionCall": { "name": "get_current_temperature", "args": { "city": "London" } } }
    ]
  },
  {
    "role": "user",
    "parts": [
      { "functionResponse": { "name": "get_current_temperature", "response": { "temp": "15C" } } },
      { "functionResponse": { "name": "get_current_temperature", "response": { "temp": "12C" } } }
    ]
  }
]
```

## Signatures in non-functionCall parts

Gemini may return `thought_signatures` in the final part of responses without function calls.

- **Behavior**: Final content part (`text`, `inlineData`...) may contain `thought_signature`
- **Recommendation**: Returning these signatures is **recommended** for complex instruction following or simulated agentic workflows
- **Validation**: API does **not** strictly enforce validation; no blocking error if omitted, though performance may degrade

**Turn 1, Step 1 (Model response)**

```json
{
  "role": "model",
  "parts": [
    {
      "text": "I need to calculate the risk. Let me think step-by-step...",
      "thought_signature": "<Signature_C>"
    }
  ]
}
```

**Turn 2, Step 1 (User)**

```json
[
  { "role": "user", "parts": [{ "text": "What is the risk?" }] },
  {
    "role": "model",
    "parts": [
      {
        "text": "I need to calculate the risk. Let me think step-by-step..."
      }
    ]
  },
  { "role": "user", "parts": [{ "text": "Summarize it." }] }
]
```

## Signatures for OpenAI compatibility

### Sequential function calling example

**Turn 1, Step 1 (User Request)**

```json
{
  "model": "google/gemini-3.1-pro-preview",
  "messages": [
    {
      "role": "user",
      "content": "Check flight status for AA100 and book a taxi 2 hours before if delayed."
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "check_flight",
        "description": "Gets the current status of a flight",
        "parameters": {
          "type": "object",
          "properties": { "flight": { "type": "string", "description": "The flight number to check." } },
          "required": ["flight"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "book_taxi",
        "description": "Book a taxi",
        "parameters": {
          "type": "object",
          "properties": { "time": { "type": "string", "description": "time to book the taxi" } },
          "required": ["time"]
        }
      }
    }
  ]
}
```

**Turn 1, Step 1 (Model Response)**

```json
{
  "role": "model",
  "tool_calls": [
    {
      "extra_content": {
        "google": { "thought_signature": "<Signature A>" }
      },
      "function": {
        "arguments": "{\"flight\":\"AA100\"}",
        "name": "check_flight"
      },
      "id": "function-call-1",
      "type": "function"
    }
  ]
}
```

**Turn 1, Step 2 (User Response - Sending Tool Outputs)**

```json
{
  "messages": [
    { "role": "user", "content": "Check flight status for AA100..." },
    {
      "role": "model",
      "tool_calls": [
        {
          "extra_content": { "google": { "thought_signature": "<Signature A>" } },
          "function": { "arguments": "{\"flight\":\"AA100\"}", "name": "check_flight" },
          "id": "function-call-1",
          "type": "function"
        }
      ]
    },
    {
      "role": "tool",
      "name": "check_flight",
      "tool_call_id": "function-call-1",
      "content": "{\"status\":\"delayed\",\"departure_time\":\"12 PM\"}"
    }
  ]
}
```

**Turn 1, Step 2 (Model)**

```json
{
  "role": "model",
  "tool_calls": [
    {
      "extra_content": { "google": { "thought_signature": "<Signature B>" } },
      "function": { "arguments": "{\"time\":\"10 AM\"}", "name": "book_taxi" },
      "id": "function-call-2",
      "type": "function"
    }
  ]
}
```

**Turn 1, Step 3 (User - Sending Tool Output)**

Include signatures for ALL function calls (`<Signature A>` + `<Signature B>`).

```json
{
  "messages": [
    { "role": "user", "content": "Check flight status for AA100..." },
    {
      "role": "model",
      "tool_calls": [
        {
          "extra_content": { "google": { "thought_signature": "<Signature A>" } },
          "function": { "arguments": "{\"flight\":\"AA100\"}", "name": "check_flight" },
          "id": "function-call-1d6a1a61-6f4f-4029-80ce-61586bd86da5",
          "type": "function"
        }
      ]
    },
    {
      "role": "tool",
      "name": "check_flight",
      "tool_call_id": "function-call-1d6a1a61-6f4f-4029-80ce-61586bd86da5",
      "content": "{\"status\":\"delayed\",\"departure_time\":\"12 PM\"}"
    },
    {
      "role": "model",
      "tool_calls": [
        {
          "extra_content": { "google": { "thought_signature": "<Signature B>" } },
          "function": { "arguments": "{\"time\":\"10 AM\"}", "name": "book_taxi" },
          "id": "function-call-65b325ba-9b40-4003-9535-8c7137b35634",
          "type": "function"
        }
      ]
    },
    {
      "role": "tool",
      "name": "book_taxi",
      "tool_call_id": "function-call-65b325ba-9b40-4003-9535-8c7137b35634",
      "content": "{\"booking_status\":\"success\"}"
    }
  ]
}
```

### Parallel function calling example

**Turn 1, Step 1 (User Request)**

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [{ "text": "Check the weather in Paris and London." }]
    }
  ],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "get_current_temperature",
          "description": "Gets the current temperature for a given location.",
          "parameters": {
            "type": "object",
            "properties": {
              "location": { "type": "string", "description": "The city name, e.g. San Francisco" }
            },
            "required": ["location"]
          }
        }
      ]
    }
  ]
}
```

**Turn 1, Step 1 (Model Response)**

```json
{
  "role": "assistant",
  "tool_calls": [
    {
      "extra_content": { "google": { "thought_signature": "<Signature A>" } },
      "function": { "arguments": "{\"location\":\"Paris\"}", "name": "get_current_temperature" },
      "id": "function-call-f3b9ecb3-d55f-4076-98c8-b13e9d1c0e01",
      "type": "function"
    },
    {
      "function": { "arguments": "{\"location\":\"London\"}", "name": "get_current_temperature" },
      "id": "function-call-335673ad-913e-42d1-bbf5-387c8ab80f44",
      "type": "function"
    }
  ]
}
```

**Turn 1, Step 2 (User Response - Sending Tool Outputs)**

```json
{
  "messages": [
    { "role": "user", "content": "Check the weather in Paris and London." },
    {
      "role": "assistant",
      "tool_calls": [
        {
          "extra_content": { "google": { "thought_signature": "<Signature A>" } },
          "function": { "arguments": "{\"location\":\"Paris\"}", "name": "get_current_temperature" },
          "id": "function-call-f3b9ecb3-d55f-4076-98c8-b13e9d1c0e01",
          "type": "function"
        },
        {
          "function": { "arguments": "{\"location\":\"London\"}", "name": "get_current_temperature" },
          "id": "function-call-335673ad-913e-42d1-bbf5-387c8ab80f44",
          "type": "function"
        }
      ]
    },
    {
      "role": "tool",
      "name": "get_current_temperature",
      "tool_call_id": "function-call-f3b9ecb3-d55f-4076-98c8-b13e9d1c0e01",
      "content": "{\"temp\":\"15C\"}"
    },
    {
      "role": "tool",
      "name": "get_current_temperature",
      "tool_call_id": "function-call-335673ad-913e-42d1-bbf5-387c8ab80f44",
      "content": "{\"temp\":\"12C\"}"
    }
  ]
}
```

## FAQs

**1. How do I transfer history from a different model to Gemini 3 with a function call part that has no associated thought signature?**

When injecting custom function call blocks cannot be avoided, use dummy signatures to skip validation:
- `"context_engineering_is_the_way_to_go"`
- `"skip_thought_signature_validator"`

**2. API returns 400 when sending interleaved parallel function calls and responses.**

Expected order: `FC1 + signature, FC2, FR1, FR2`
Wrong order: `FC1 + signature, FR1, FC2, FR2` (returns 400)

**3. During streaming without function call, I can't find the thought signature.**

The model may return the thought signature in a part with empty text content. Parse the entire request until `finish_reason` is returned.

## Thought signatures for different models

| Scenario | Gemini 3 | Gemini 2.5 |
|---------|----------|------------|
| Function calls in response | Signature on first `functionCall` part (**mandatory**) | Signature in first part regardless of type (**optional**) |
| No function calls in response | Signature on last part if model generates thought | No signature |

#topic-thought-signatures #topic-function-calling #topic-model-reasoning
