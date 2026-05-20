---
title: Gemini API Libraries
url: https://ai.google.dev/gemini-api/docs/libraries.md.txt
source: llms
fetched_at: 2026-04-29T11:17:29.18422021-03:00
rendered_js: false
word_count: 307
summary: Overview of the Google GenAI SDK for building Gemini API applications with installation instructions and migration guidance.
tags:
    - gemini-api
    - google-genai-sdk
    - sdk-installation
    - api-migration
    - software-development
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> [!WARNING]
> We have updated our [Terms of Service](https://ai.google.dev/gemini-api/terms).

Use the **Google GenAI SDK** — official, production-ready libraries in General Availability. Used in all official documentation and examples.

> [!NOTE]
> Migrate from legacy libraries to Google GenAI SDK for latest features like [[015-docs-live-api-best-practices|Live API]] and [[033-docs-video|Veo]]. Legacy libraries deprecated November 30, 2025.

For new users, follow the [[001-docs-ai-studio-quickstart|quickstart guide]].

## Installation

### Python

- Library: [`google-genai`](https://pypi.org/project/google-genai)
- GitHub: [googleapis/python-genai](https://github.com/googleapis/python-genai)
- Install: `pip install google-genai`

### JavaScript

- Library: [`@google/genai`](https://www.npmjs.com/package/@google/genai)
- GitHub: [googleapis/js-genai](https://github.com/googleapis/js-genai)
- Install: `npm install @google/genai`

### Go

- Library: [`google.golang.org/genai`](https://pkg.go.dev/google.golang.org/genai)
- GitHub: [googleapis/go-genai](https://github.com/googleapis/go-genai)
- Install: `go get google.golang.org/genai`

### Java

- Library: `google-genai`
- GitHub: [googleapis/java-genai](https://github.com/googleapis/java-genai)

**Maven:**

```xml
<dependencies>
  <dependency>
    <groupId>com.google.genai</groupId>
    <artifactId>google-genai</artifactId>
    <version>1.0.0</version>
  </dependency>
</dependencies>
```

### C#

- Library: `Google.GenAI`
- GitHub: [googleapis/dotnet-genai](https://googleapis.github.io/dotnet-genai/)
- Install: `dotnet add package Google.GenAI`

## General Availability

The Google GenAI SDK reached GA across all supported platforms (May 2025). Libraries are stable, fully supported for production, actively maintained, and provide access to latest features with best performance.

Migrate from legacy libraries to access latest features.

## Migration from Legacy Libraries

Migrate to the new libraries per [[018-docs-migrate-to-cloud|migration guide]].

> [!DANGER]
> Legacy libraries don't support recent features (Live API, Veo) and are deprecated as of November 30, 2025.

| Language | Legacy Library | Status | Recommended Library |
|---|---|---|---|
| **Python** | [deprecated-generative-ai-python](https://github.com/google-gemini/deprecated-generative-ai-python) | Not actively maintained | [python-genai](https://github.com/googleapis/python-genai) |
| **JavaScript/TypeScript** | [generative-ai-js](https://github.com/google-gemini/generative-ai-js) | Not actively maintained | [js-genai](https://github.com/googleapis/js-genai) |
| **Go** | [generative-ai-go](https://github.com/google/generative-ai-go) | Not actively maintained | [go-genai](https://github.com/googleapis/go-genai) |
| **Dart/Flutter** | [google_generative_ai](https://pub.dev/packages/google_generative_ai/install) | Not actively maintained | [Genkit Dart](https://genkit.dev/docs/dart/get-started/) or [Firebase AI Logic](https://pub.dev/packages/firebase_ai) |
| **Swift** | [generative-ai-swift](https://github.com/google/generative-ai-swift) | Not actively maintained | [Firebase AI Logic](https://firebase.google.com/products/firebase-ai-logic) |
| **Android** | [generative-ai-android](https://github.com/google-gemini/generative-ai-android) | Not actively maintained | [Firebase AI Logic](https://firebase.google.com/products/firebase-ai-logic) |

> [!NOTE]
> **Java developers**: No legacy Google-provided Java SDK existed. Start directly with the new library per the [[014-docs-libraries#install|installation section]].