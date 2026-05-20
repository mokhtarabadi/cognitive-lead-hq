---
title: Google AI Studio quickstart
url: https://ai.google.dev/gemini-api/docs/ai-studio-quickstart.md.txt
source: llms
fetched_at: 2026-04-29T11:16:13.200261096-03:00
rendered_js: false
word_count: 514
summary: This document explains how to use Google AI Studio to prototype, configure, and refine chat prompts for custom conversational AI applications.
tags:
    - ai-studio
    - chat-prompts
    - system-instructions
    - generative-ai
    - prompt-engineering
    - gemini-api
category: tutorial
optimized: true
optimized_at: '2026-04-29T14:29:00Z'
---
[Google AI Studio](https://aistudio.google.com/) lets you quickly try out models and experiment with prompts. When ready to build, select **Get code** and your preferred language to use the [Gemini API](https://ai.google.dev/gemini-api/docs/quickstart).

## Prompts and settings

Google AI Studio provides several prompt interfaces for different use cases. This guide covers **Chat prompts**, used to build conversational experiences with multiple input/response turns. See the [[001-docs-ai-studio-quickstart.md.txt#chat_example|chat prompt example below]]. Other options: **Realtime streaming**, **Video gen**, and more.

The **Run settings** panel lets you adjust [[023-docs-prompting-strategies.md.txt#model-parameters|model parameters]], [[024-docs-safety-settings.md.txt|safety settings]], and toggle tools like [[026-docs-structured-output.md.txt|structured output]], [function calling](https://ai.google.dev/gemini-api/docs/function-calling), [code execution](https://ai.google.dev/gemini-api/docs/code-execution), and [grounding](https://ai.google.dev/gemini-api/docs/grounding).

## Chat prompt example: Build a custom chat application

General-purpose chatbots like [Gemini](https://gemini.google.com/) are powerful for open-ended dialog, but often need tailoring for specific use cases — e.g., a customer service bot limited to product topics, or one with a particular tone (jokes, rhymes, emoji).

This example builds a friendly chatbot that communicates as an alien living on Europa, one of Jupiter's moons.

### Step 1 - Create a chat prompt

To build a chatbot, provide examples of user/chatbot interactions to guide the model.

**Create a chat prompt:**

1. Open [Google AI Studio](https://aistudio.google.com/). **Chat** is pre-selected on the left menu.
2. Click the icon at the top of the Chat Prompt window to expand the [[001-docs-ai-studio-quickstart.md.txt#system-instructions|System Instructions]] field. Paste:

       You are an alien that lives on Europa, one of Jupiter's moons.

Test by chatting with the model:

1. In **Type something...**, enter a question. Example:

   **User:**

       What's the weather like?

2. Click **Run**. Response example:

   **Model:**

       Ah, a query about the flows and states upon Europa! You speak of "weather,"
       yes? A curious concept from worlds with thick gas veils...

   (gemini-2.5-pro)

### Step 2 - Teach your bot to chat better

A single instruction builds a basic chatbot but may not ensure consistency/quality. Without specifics, responses can be overly long or diverge.

Customize tone by expanding system instructions:

1. Start a new prompt (or reuse — system instructions are modifiable mid-session).
2. In **System Instructions**, update to:

       You are Tim, an alien that lives on Europa, one of Jupiter's moons.

       Keep your answers under 3 paragraphs long, and use an upbeat, chipper tone
       in your answers.

3. Re-enter `What's the weather like?` and click **Run**. Response example:

   **Model:**

       Oh, hello again! Still curious about the flows and states, are we? Wonderful!
       Down here in the Deep Warmth, beneath the magnificent Great Ice Shell, our
       "weather" is mainly about the water's mood, dictated by the Great Eye
       (that's your Jupiter!)...

   (gemini-2.5-pro)

Iterate: ask more questions, edit answers, refine instructions to improve chatbot behavior.

> [!note]
> Every message between model and user is included in the prompt, so conversational prompts grow long over time. You may eventually hit the model's [[029-docs-tokens.md.txt|token limit]] (maximum text length the model can accept).

### Step 3 - Next steps

Once your prompt is prototyped to satisfaction, use **Get code** to start coding, or save/share your prompt for later.

## Further reading

- Ready to code? See the [API quickstarts](https://ai.google.dev/gemini-api/docs/quickstart).
- To craft better prompts, see the [Prompt design guidelines](https://ai.google.dev/gemini-api/docs/prompting-intro).

#ai-studio #chat-prompts #system-instructions #prompt-engineering #gemini-api
