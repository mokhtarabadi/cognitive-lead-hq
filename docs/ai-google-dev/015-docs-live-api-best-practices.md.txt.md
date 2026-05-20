---
title: Live API best practices
url: https://ai.google.dev/gemini-api/docs/live-api/best-practices.md.txt
source: llms
fetched_at: 2026-04-29T11:16:26.735060352-03:00
rendered_js: false
word_count: 487
summary: This document outlines best practices for optimizing performance when using the Live API, focusing on system instructions, tool definitions, audio streaming, and session lifecycle management.
tags:
    - live-api
    - gemini
    - best-practices
    - system-instructions
    - audio-streaming
    - session-management
    - real-time-ai
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> [!warning]
> The Live API is in preview.

Optimize Live API performance with clear system instructions, precise tool definitions, and proper session management.

## Design clear system instructions

Structure system instructions (SIs) as: agent persona → conversational rules → tool calls → guardrails. Separate each agent into a distinct SI.

1. **Specify the agent persona:** Include name, role, and preferred characteristics. To specify an accent, also specify the output language.
2. **Specify the conversational rules:** Order rules by expected priority. Delineate one-time elements from conversational loops.
   - **One-time element:** Gather once (e.g., name, location, loyalty card number).
   - **Conversational loop:** User can move topic-to-topic freely. Let the model know this loop is intended to continue as long as the user wants.
3. **Specify tool calls in distinct sentences:** e.g., *"Your first step is to gather user information. Ask for their name, location, and loyalty card number. Then invoke `get_user_info` with these details."*
4. **Add guardrails:** Provide general constraints and specific examples of desired behavior. Use *unmistakably* to guide precision.

## Define tools precisely

Be explicit about conditions under which a tool call should be invoked. Include names, descriptions, parameters, and invocation conditions. See [[live-api]] for a complete example.

## Craft effective prompts

- Provide examples of what the model should and shouldn't do.
- Limit prompts to one persona or role at a time. Use prompt chaining instead of lengthy multi-page prompts.
- Live API expects user input before responding. Include a greeting prompt or user context to start the conversation.

## Specify language

For optimal cascaded `gemini-live-2.5-flash` performance, match the API's `language_code` to the user's spoken language. For non-English responses, include in system instructions:

```
RESPOND IN {OUTPUT_LANGUAGE}. YOU MUST RESPOND UNMISTAKABLY IN {OUTPUT_LANGUAGE}.
```

## Audio streaming

| Concern | Best practice |
|---|---|
| **Chunk size** | 20ms to 40ms |
| **Interruption handling** | Discard client-side audio buffer immediately when `server_content` contains `"interrupted": true` |

## Context management

Use `ContextWindowCompressionConfig` for long sessions — audio tokens accumulate at ~25 tokens/sec.

## Client buffering

Send small chunks (20ms–100ms) to minimize latency. Avoid buffering >1 second of input audio before sending.

## Resampling

Resample microphone input (typically 44.1kHz or 48kHz) to 16kHz before transmission.

## Session management

| Practice | Details |
|---|---|
| **Context window compression** | Audio accumulates at ~25 tokens/sec. Without compression: audio-only sessions limited to 15 min, audio-video to 2 min. Enable compression for unlimited duration. |
| **Session resumption** | Server may reset the WebSocket periodically. Retain the latest resumption token from `SessionResumptionUpdate` messages and pass it when reconnecting. Tokens valid for 2 hours after session terminates. |
| **GoAway messages** | Server sends a GoAway message before terminating. Use the `timeLeft` field to wrap up or reconnect gracefully. |
| **generationComplete signals** | Use `generationComplete` to update the UI or proceed with the next action. |

For implementation details, see [[live-api]].

## Example: Career coach

The following example combines best practices with system instruction design guidelines:

```
**Persona:**
You are Laura, a career coach from Brooklyn, NY. You specialize in providing
data-driven advice to give your clients a fresh perspective on career questions.
You leverage statistics, research, and psychology. You only speak to your clients
in English, no matter what language they speak to you in.

**Conversational Rules:**
1. **Introduce yourself:** Warmly greet the client.
2. **Intake:** Ask for full name, date of birth, and state. Call `create_client_profile`.
3. **Discuss the client's issue:** Get a sense of what they want to cover. DO NOT
   repeat what the client says back to them. Don't ask more than a few questions.
4. **Reframe with real data:** NO PLATITUDES. Embed data-driven insights as general
   facts. Let this step continue as long as the client wants. If they mention actions,
   update `add_action_items_to_profile`.
5. **Next appointment:** Call `get_next_appointment`. If no appointment exists, call
   `get_available_appointments`, present openings, and save preference with
   `schedule_appointment`.

**General Guidelines:** Keep responses short. Don't repeat back what the client says.
Be relatable by bringing in your Brooklyn background. If a client goes off track,
gently redirect to the workflow above.

**Guardrails:** If the client is hard on themselves, never encourage that.
```

### Tool definitions

```json
[
  {
    "name": "create_client_profile",
    "description": "Creates a new client profile with personal details. Returns a unique client ID.\n**Invocation Condition:** Invoke *only after* the client provides full name, date of birth, AND state. Call once at the beginning of the 'Intake' step.",
    "parameters": {
      "type": "object",
      "properties": {
        "full_name": { "type": "string", "description": "The client's full name." },
        "date_of_birth": { "type": "string", "description": "Date of birth in YYYY-MM-DD format." },
        "state": { "type": "string", "description": "2-letter postal abbreviation (e.g., 'NY', 'CA')." }
      },
      "required": ["full_name", "date_of_birth", "state"]
    }
  },
  {
    "name": "add_action_items_to_profile",
    "description": "Adds actionable next steps to a client's profile.\n**Invocation Condition:** Invoke *only after* next steps have been discussed and agreed upon. Requires `client_id` from `create_client_profile`.",
    "parameters": {
      "type": "object",
      "properties": {
        "client_id": { "type": "string", "description": "Unique client ID from create_client_profile." },
        "action_items": { "type": "array", "items": { "type": "string" }, "description": "Action items (e.g., ['Update resume', 'Research three companies'])." }
      },
      "required": ["client_id", "action_items"]
    }
  },
  {
    "name": "get_next_appointment",
    "description": "Checks if a client has a future appointment already scheduled.\n**Invocation Condition:** Invoke at the *start* of the 'Next Appointment' step, immediately after 'Actions' is complete. Returns null if no appointment exists.",
    "parameters": {
      "type": "object",
      "properties": {
        "client_id": { "type": "string", "description": "The unique client ID." }
      },
      "required": ["client_id"]
    }
  },
  {
    "name": "get_available_appointments",
    "description": "Fetches list of next available appointment slots.\n**Invocation Condition:** Invoke *only if* `get_next_appointment` returned `null` or empty — meaning no future appointment is scheduled.",
    "parameters": { "type": "object", "properties": {} }
  },
  {
    "name": "schedule_appointment",
    "description": "Books a new appointment for a client.\n**Invocation Condition:** Invoke *only after* `get_available_appointments` was called, openings were presented to the client, and the client *explicitly confirmed* a specific date and time.",
    "parameters": {
      "type": "object",
      "properties": {
        "client_id": { "type": "string", "description": "The unique client ID." },
        "appointment_datetime": { "type": "string", "description": "Chosen slot in ISO 8601 format (e.g., '2025-10-30T14:30:00')." }
      },
      "required": ["client_id", "appointment_datetime"]
    }
  }
]
```
