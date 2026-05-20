---
title: Long context
url: https://ai.google.dev/gemini-api/docs/long-context.md.txt
source: llms
fetched_at: 2026-04-29T11:17:35.641691899-03:00
rendered_js: false
word_count: 679
summary: Gemini models support 1M+ token context windows, enabling many-shot in-context learning, native multimodal processing, and direct data provision instead of traditional RAG approaches.
tags:
    - gemini-api
    - long-context
    - multimodal-learning
    - many-shot-learning
    - context-window
    - generative-ai
category: concept
optimized: true
optimized_at: '2026-04-29T14:17:12Z'
---
# Long context

Gemini models support 1 million+ token context windows, enabling paradigms impossible with earlier models limited to 8K–128K tokens.

> [!info]
> The same code for [text generation](https://ai.google.dev/gemini-api/docs/text-generation) or [multimodal inputs](https://ai.google.dev/gemini-api/docs/vision) works without changes with long context.

For specific model context window sizes, see [Models](https://ai.google.dev/gemini-api/docs/models).

## What is a context window?

The context window is analogous to short-term memory—information passed to the model for response generation. There is a limited amount of information that can be stored, just as with human short-term memory.

## Getting started

Earlier models processed 8,000 tokens max. Gemini was the first model accepting 1 million tokens. In practice, 1 million tokens equals:

- 50,000 lines of code (80 chars/line)
- All text messages from 5 years
- 8 average-length English novels
- 200+ podcast episode transcripts

Limited context windows require dropping old messages, summarizing, RAG with vector databases, or prompt filtering. Gemini's extensive context enables a simpler approach: provide all relevant information upfront.

Gemini demonstrates powerful in-context learning—for example, learning English-to-Kalamang translation (a Papuan language with fewer than 200 speakers) using only instructional materials, achieving quality similar to human learners. This illustrates the paradigm shift from RAG to direct data provision.

## Long context use cases

### Text

Use cases for text-based long context:

- **Summarizing large corpuses** — No sliding window needed to maintain state across sections
- **Question and answering** — Historically required RAG; now feasible directly with large context
- **Agentic workflows** — Agents need sufficient context about their goal and actions to maintain reliability

[Many-shot in-context learning](https://arxiv.org/pdf/2404.11018) scales beyond single/multi-shot examples to hundreds or thousands of examples, achieving performance similar to fine-tuned models. [Context caching](https://ai.google.dev/gemini-api/docs/caching) makes this economically feasible.

### Video

Gemini's text capabilities extend to multimodal inputs (text, video, audio, images), with sustained performance for video question answering and reasoning.

Video use cases:

- Video question and answering
- Video memory (e.g., [Project Astra](https://deepmind.google/technologies/gemini/project-astra/))
- Video captioning and recommendation systems
- Content moderation and real-time processing
- Customization by analyzing video corpuses and removing irrelevant parts

> [!warning]
> Consider how [videos are processed into tokens](https://ai.google.dev/gemini-api/docs/tokens#media-token), which affects billing and usage limits.

See [Prompting with video files](https://ai.google.dev/gemini-api/docs/prompting_with_media?lang=python#prompting-with-videos).

### Audio

Gemini was the first natively multimodal LLM that understands audio directly, avoiding the latency and performance loss of chaining separate speech-to-text and text-to-text models.

Audio use cases:

- Real-time transcription and translation
- Podcast/video question and answering
- Meeting transcription and summarization
- Voice assistants

See [Prompting with audio files](https://ai.google.dev/gemini-api/docs/prompting_with_media?lang=python#prompting-with-videos).

## Optimizations

### Context caching

[Context caching](https://ai.google.dev/gemini-api/docs/caching) is the primary optimization for long context. For "chat with your data" apps where users upload multiple files, caching the files and paying per hour is far more cost-effective than repeating full context loads.

Gemini Flash input/output cost with caching is ~4x less than standard rates, providing significant savings for repeated queries against the same context.

## Limitations

Gemini models achieve high accuracy on single "needle-in-a-haystack" retrieval evals, but performance degrades with multiple needles or complex information retrieval tasks. Accuracy varies widely by context.

| Scenario | Accuracy | Requests Needed |
|----------|----------|-----------------|
| Single query | ~99% | 1 |
| 100 pieces of info @ 99% accuracy | ~99% | ~100 |

[Context caching](https://ai.google.dev/gemini-api/docs/caching) helps maintain high performance while reducing costs for repeated queries.

## FAQs

### Where is the best place to put my query in the context window?

In most cases, especially with long total context, performance improves by placing your query/question at the end of the prompt (after all other context).

### Do I lose model performance when I add more tokens?

Generally, omit unneeded tokens. However, for large chunks where you want to ask questions, the model is highly capable of extracting that information (up to 99% accuracy in many cases).

### How can I lower my cost with long-context queries?

[Context caching](https://ai.google.dev/gemini-api/docs/caching) reduces costs for reusing similar tokens/context across multiple requests.

### Does context length affect model latency?

There is fixed latency per request regardless of size, but longer queries generally have higher latency (time to first token).

#gemini-api #long-context #multimodal-learning #many-shot-learning #context-window #generative-ai
