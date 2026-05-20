---
title: Send content...
url: https://ai.google.dev/gemini-api/docs/live-api/get-started-sdk.md.txt
source: llms
fetched_at: 2026-04-29T11:16:29.791755304-03:00
rendered_js: false
word_count: 355
summary: This guide provides instructions for integrating and using the Gemini Live API with the Google GenAI SDK to enable real-time, bidirectional multimodal communication via WebSockets.
tags:
    - gemini-api
    - real-time-ai
    - multimodal
    - web-sockets
    - sdk-integration
    - function-calling
category: guide
optimized: true
optimized_at: '2026-04-29T14:29:00Z'
---
The Gemini Live API enables real-time, bidirectional interaction with Gemini models via WebSockets — supporting audio, video, and text inputs plus native audio outputs. This guide covers integration using the Google GenAI SDK on your server.

[Try the Live API in Google AI Studio](https://aistudio.google.com/live) [Clone the example app from GitHub](https://github.com/google-gemini/gemini-live-api-examples/tree/main/gemini-live-genai-python-sdk) [[038-docs-coding-agents.md.txt|Use coding agent skills]]

## Overview

The Gemini Live API uses WebSockets for real-time communication. The `google-genai` SDK provides a high-level async interface for managing connections.

Key concepts:

- **Session**: A persistent connection to the model.
- **Config**: Setting up modalities (audio/text), voice, and system instructions.
- **Real-time Input**: Sending audio and video frames as blobs.

## Connecting to the Live API

Start a Live API session with an API key:

### Python

```python
import asyncio
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

model = "gemini-3.1-flash-live-preview"
config = {"response_modalities": ["AUDIO"]}

async def main():
    async with client.aio.live.connect(model=model, config=config) as session:
        print("Session started")
        # Send content...

if __name__ == "__main__":
    asyncio.run(main())
```

### JavaScript

```js
import { GoogleGenAI, Modality } from '@google/genai';

const ai = new GoogleGenAI({ apiKey: "YOUR_API_KEY"});
const model = 'gemini-3.1-flash-live-preview';
const config = { responseModalities: [Modality.AUDIO] };

async function main() {

  const session = await ai.live.connect({
    model: model,
    callbacks: {
      onopen: function () {
        console.debug('Opened');
      },
      onmessage: function (message) {
        console.debug(message);
      },
      onerror: function (e) {
        console.debug('Error:', e.message);
      },
      onclose: function (e) {
        console.debug('Close:', e.reason);
      },
    },
    config: config,
  });

  console.debug("Session started");
  // Send content...

  session.close();
}

main();
```

## Sending text

Send text using `send_realtime_input` (Python) or `sendRealtimeInput` (JavaScript).

### Python

```python
await session.send_realtime_input(text="Hello, how are you?")
```

### JavaScript

```js
session.sendRealtimeInput({
  text: 'Hello, how are you?'
});
```

## Sending audio

Send audio as raw PCM data (16-bit PCM, 16kHz, little-endian).

### Python

```python
# Assuming 'chunk' is your raw PCM audio bytes
await session.send_realtime_input(
    audio=types.Blob(
        data=chunk,
        mime_type="audio/pcm;rate=16000"
    )
)
```

### JavaScript

```js
// Assuming 'chunk' is a Buffer of raw PCM audio
session.sendRealtimeInput({
  audio: {
    data: chunk.toString('base64'),
    mimeType: 'audio/pcm;rate=16000'
  }
});
```

For client-side audio capture, see the end-to-end example on [GitHub](https://github.com/google-gemini/gemini-live-api-examples/blob/main/gemini-live-genai-python-sdk/frontend/media-handler.js#L31-L70).

## Sending video

Send video frames as individual images (JPEG or PNG) at max 1 frame/second.

### Python

```python
# Assuming 'frame' is your JPEG-encoded image bytes
await session.send_realtime_input(
    video=types.Blob(
        data=frame,
        mime_type="image/jpeg"
    )
)
```

### JavaScript

```js
// Assuming 'frame' is a Buffer of JPEG-encoded image data
session.sendRealtimeInput({
  video: {
    data: frame.toString('base64'),
    mimeType: 'image/jpeg'
  }
});
```

For client-side video capture, see the end-to-end example on [GitHub](https://github.com/google-gemini/gemini-live-api-examples/blob/main/gemini-live-genai-python-sdk/frontend/media-handler.js#L84-L120).

## Receiving audio

Model audio responses arrive as data chunks.

### Python

```python
async for response in session.receive():
    if response.server_content and response.server_content.model_turn:
        for part in response.server_content.model_turn.parts:
            if part.inline_data:
                audio_data = part.inline_data.data
                # Process or play the audio data
```

### JavaScript

```js
// Inside the onmessage callback
const content = response.serverContent;
if (content?.modelTurn?.parts) {
  for (const part of content.modelTurn.parts) {
    if (part.inlineData) {
      const audioData = part.inlineData.data;
      // Process or play audioData (base64 encoded string)
    }
  }
}
```

See the example app on GitHub to learn how to [receive audio on your server](https://github.com/google-gemini/gemini-live-api-examples/blob/main/gemini-live-genai-python-sdk/gemini_live.py#L86-L98) and [play it in the browser](https://github.com/google-gemini/gemini-live-api-examples/blob/main/gemini-live-genai-python-sdk/frontend/media-handler.js#L145-L174).

## Receiving text

Transcriptions for user input and model output are available in server content.

### Python

```python
async for response in session.receive():
    content = response.server_content
    if content:
        if content.input_transcription:
            print(f"User: {content.input_transcription.text}")
        if content.output_transcription:
            print(f"Gemini: {content.output_transcription.text}")
```

### JavaScript

```js
// Inside the onmessage callback
const content = response.serverContent;
if (content?.inputTranscription) {
  console.log('User:', content.inputTranscription.text);
}
if (content?.outputTranscription) {
  console.log('Gemini:', content.outputTranscription.text);
}
```

## Handling tool calls

The API supports tool calling (function calling). When the model requests a tool call, execute the function and send the response back.

### Python

```python
async for response in session.receive():
    if response.tool_call:
        function_responses = []
        for fc in response.tool_call.function_calls:
            # 1. Execute the function locally
            result = my_tool_function(**fc.args)

            # 2. Prepare the response
            function_responses.append(types.FunctionResponse(
                name=fc.name,
                id=fc.id,
                response={"result": result}
            ))

        # 3. Send the tool response back to the session
        await session.send_tool_response(function_responses=function_responses)
```

### JavaScript

```js
// Inside the onmessage callback
if (response.toolCall) {
  const functionResponses = [];
  for (const fc of response.toolCall.functionCalls) {
    const result = myToolFunction(fc.args);
    functionResponses.push({
      name: fc.name,
      id: fc.id,
      response: { result }
    });
  }
  session.sendToolResponse({ functionResponses });
}
```

## What's next

- Read the full Live API [Capabilities](https://ai.google.dev/gemini-api/docs/live-guide) guide for key capabilities and configurations (Voice Activity Detection, native audio features).
- Read the [Tool use](https://ai.google.dev/gemini-api/docs/live-tools) guide to integrate Live API with tools and function calling.
- Read the [Session management](https://ai.google.dev/gemini-api/docs/live-session) guide for managing long-running conversations.
- Read the [[020-docs-oauth.md.txt|Ephemeral tokens]] guide for secure authentication in client-to-server applications.
- For WebSockets API details, see the [WebSockets API reference](https://ai.google.dev/api/live).

#gemini-api #real-time-ai #multimodal #web-sockets #sdk-integration
