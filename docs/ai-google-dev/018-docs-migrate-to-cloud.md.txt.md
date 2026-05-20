---
title: Gemini Developer API vs. Gemini Enterprise Agent Platform
url: https://ai.google.dev/gemini-api/docs/migrate-to-cloud.md.txt
source: llms
fetched_at: 2026-04-29T11:17:37.494812408-03:00
rendered_js: false
word_count: 249
summary: This document provides a comparison and migration guide for using the Gemini Developer API and the Gemini Enterprise Agent Platform API, highlighting their unified SDK access and implementation differences.
tags:
    - gemini-api
    - google-cloud-platform
    - generative-ai
    - api-migration
    - sdk-integration
    - enterprise-solutions
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
Two API products are available: the [[gemini-api|Gemini Developer API]] (fastest path to production) and the [Gemini Enterprise Agent Platform](https://cloud.google.com/gemini-enterprise-agent-platform/overview) (enterprise-ready controls and ecosystem).

Both are now accessible through the unified [Google Gen AI SDK](https://ai.google.dev/gemini-api/docs/libraries).

## Code comparison

### Python

Both APIs use the `google-genai` library. See [[libraries]] for installation.

**Gemini Developer API:**

```python
from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)
```

**Gemini Enterprise Agent Platform API:**

```python
from google import genai

client = genai.Client(
    vertexai=True, project='your-project-id', location='us-central1'
)

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)
```

### JavaScript / TypeScript

Both APIs use `@google/genai`. See [[libraries]] for installation.

**Gemini Developer API:**

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

main();
```

**Gemini Enterprise Agent Platform API:**

```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({
  vertexai: true,
  project: 'your_project',
  location: 'your_location',
});

async function main() {
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "Explain how AI works in a few words",
  });
  console.log(response.text);
}

main();
```

### Go

Both APIs use `google.golang.org/genai`. See [[libraries]] for installation.

**Gemini Developer API:**

```go
import (
  "context"
  "encoding/json"
  "fmt"
  "log"
  "google.golang.org/genai"
)

// Your Google API key
const apiKey = "your-api-key"

func main() {
  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
    log.Fatal(err)
  }

  result, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", genai.Text("Tell me about New York?"), nil)
}
```

**Gemini Enterprise Agent Platform API:**

```go
import (
  "context"
  "encoding/json"
  "fmt"
  "log"
  "google.golang.org/genai"
)

const project = "your-project"
const location = "some-gcp-location"

func main() {
  ctx := context.Background()
  client, err := genai.NewClient(ctx, &genai.ClientConfig{
    Project:  project,
    Location: location,
    Backend:  genai.BackendVertexAI,
  })
  if err != nil {
    log.Fatal(err)
  }

  result, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", genai.Text("Tell me about New York?"), nil)
}
```

## Migration considerations

- **Authentication:** Use Google Cloud service accounts. See the [Gemini Enterprise Agent Platform documentation](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/docs/overview).
- **Project:** Use your existing Google Cloud project or [create a new one](https://cloud.google.com/resource-manager/docs/creating-managing-projects).
- **Regions:** Supported regions may differ. See [supported regions for generative AI on Google Cloud](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/docs/learn/locations-genai).
- **Models:** Models trained in Google AI Studio must be retrained in Gemini Enterprise Agent Platform.
- **API key cleanup:** Follow security best practices and delete any unused Gemini Developer API keys.

### Delete an API key

1. Open [Google Cloud API Credentials](https://console.cloud.google.com/apis/credentials).
2. Find the API key and click **Actions**.
3. Select **Delete API key**.
4. Confirm deletion.

> [!note]
> Deletion takes a few minutes to propagate. Traffic using the deleted key is rejected after propagation.
> If you deleted a key still in production, see [`gcloud beta services api-keys undelete`](https://cloud.google.com/sdk/gcloud/reference/beta/services/api-keys/undelete).

## Next steps

See the [Generative AI on Gemini Enterprise Agent Platform overview](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/docs/multimodal/overview) to learn more.
