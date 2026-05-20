---
title: Using Gemini API Keys
url: https://ai.google.dev/gemini-api/docs/api-key.md.txt
source: llms
fetched_at: 2026-04-29T11:17:14.357984979-03:00
rendered_js: false
word_count: 701
summary: Create, manage, and secure Gemini API keys using Google AI Studio and Google Cloud projects.
tags:
    - api-keys
    - google-ai-studio
    - environment-variables
    - google-cloud-projects
    - authentication
    - gemini-api
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> [!WARNING]
> We have updated our [Terms of Service](https://ai.google.dev/gemini-api/terms).

Use the Gemini API requires an API key. Create and manage keys in [[005-docs-api-key|Google AI Studio]] or import projects from [[018-docs-migrate-to-cloud|Google Cloud]].

[Create or view a Gemini API Key](https://aistudio.google.com/app/apikey)

## API Keys

Manage all Gemini API Keys from the [[005-docs-api-key|Google AI Studio API Keys page]].

Connect to the Gemini API using:

- [[005-docs-api-key#set-api-env-var|Set API key as environment variable]]
- [[005-docs-api-key#provide-api-key-explicitly|Provide API key explicitly]]

For initial testing, hard code the API key temporarily (not for production). Examples are in [[005-docs-api-key#provide-api-key-explicitly|the explicit section]].

## Google Cloud Projects

[[018-docs-migrate-to-cloud|Google Cloud projects]] manage billing, collaborators, and permissions. Google AI Studio provides a lightweight interface to your Google Cloud projects.

If you have no projects, create a new one or import from Google Cloud. The **Projects** page shows keys with sufficient permission for the Gemini API. See [[005-docs-api-key#import-projects|import projects instructions]].

### Default Project

New users: after accepting Terms of Service, Google AI Studio creates a default Google Cloud Project and API Key. Rename in **Dashboard** → **Projects** → 3 dots → **Rename project**.

Existing users with Google Cloud accounts won't have a default project created.

## Import Projects

Each API key is associated with a Google Cloud project. Import projects you want via **Import Projects** dialog (search by name or project ID). For a complete list, visit [Cloud Console](https://console.cloud.google.com/).

Import steps:

1. Go to [Google AI Studio](https://aistudio.google.com).
2. Open **Dashboard** → **Projects**.
3. Select **Import projects**.
4. Search and select the project → **Import**.

After importing, go to **API Keys** page and create a key.

> [!NOTE]
> For existing users, keys are pre-populated based on last 30 days of AI Studio activity.

## Limitations

| Limit | Value |
|---|---|
| Projects created at a time | 10 |
| Keys displayed | 100 |
| Projects displayed | 50 |

Only API keys with no restrictions, or restricted to **Generative Language API**, are displayed.

For advanced management, visit [Google Cloud Console credentials](https://console.cloud.google.com/apis/credentials) to modify and restrict API keys.

## Set API Key as Environment Variable

Set `GEMINI_API_KEY` or `GOOGLE_API_KEY` — the client automatically picks it up when using [[014-docs-libraries|Google GenAI SDK]].

> [!TIP]
> Set only one variable. If both are set, `GOOGLE_API_KEY` takes precedence.

For REST API or browser-side JavaScript, provide the API key explicitly.

### Linux/macOS (Bash)

Check for `~/.bashrc`. If missing, create it:

```bash
touch ~/.bashrc
```

Add to `~/.bashrc`:

```bash
export GEMINI_API_KEY=<YOUR_API_KEY_HERE>
```

Apply changes:

```bash
source ~/.bashrc
```

### macOS (Zsh)

Check for `~/.zshrc`. If missing, create it:

```bash
touch ~/.zshrc
```

Add to `~/.zshrc`:

```bash
export GEMINI_API_KEY=<YOUR_API_KEY_HERE>
```

Apply changes:

```bash
source ~/.zshrc
```

### Windows

1. Search "Environment Variables" in taskbar.
2. Choose **System Settings**.
3. Click **Environment Variables**.
4. Under **User variables** or **System variables**, click **New...**.
5. Set variable name: `GEMINI_API_KEY`. Set value to your API key.
6. Click **OK**. Open a new terminal session.

## Provide API Key Explicitly

Use explicit API key when:

- Simple API calls with hardcoded key
- Explicit control without relying on environment variable discovery
- Environments without environment variable support (web, REST calls)

### Python

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: "YOUR_API_KEY" });

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
    client, err := genai.NewClient(ctx, &genai.ClientConfig{
        APIKey:  "YOUR_API_KEY",
        Backend: genai.BackendGeminiAPI,
    })
    if err != nil {
        log.Fatal(err)
    }

    result, err := client.Models.GenerateContent(
        ctx,
        "gemini-3-flash-preview",
        genai.Text("Explain how AI works in a few words"),
        nil,
    )
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(result.Text())
}
```

### Java

```java
package com.example;

import com.google.genai.Client;
import com.google.genai.types.GenerateContentResponse;

public class GenerateTextFromTextInput {
  public static void main(String[] args) {
    Client client = Client.builder().apiKey("YOUR_API_KEY").build();

    GenerateContentResponse response =
        client.models.generateContent(
            "gemini-3-flash-preview",
            "Explain how AI works in a few words",
            null);

    System.out.println(response.text());
  }
}
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
  -H 'Content-Type: application/json' \
  -H "x-goog-api-key: YOUR_API_KEY" \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
```

## Keep Your API Key Secure

> [!DANGER]
> Treat your API key like a password. Compromised keys allow quota usage, charges, and access to private data.

### Critical Security Rules

- **Keep keys confidential**: Never commit to source control or expose client-side.
- **Restrict access**: Limit to specific IPs, HTTP referrers, or Android/iOS apps.
- **Restrict usage**: Enable only necessary APIs per key.
- **Regular audits**: Audit and rotate keys periodically.

### Best Practices

- **Server-side calls**: Most secure approach keeps the key confidential.
- **Ephemeral tokens for client-side (Live API only)**: Lower risk, suitable for production. Review [ephemeral tokens](https://ai.google.dev/gemini-api/docs/ephemeral-tokens).
- **Add restrictions**: Limit key permissions per [API key restrictions](https://cloud.google.com/api-keys/docs/add-restrictions-api-keys#add-api-restrictions).

Review [API key best practices](https://support.google.com/googleapi/answer/6310037).

## Troubleshooting API Key Creation

**Create API key button unavailable**: "*You do not have permission to create a key in this project*"

Missing permissions:

| Permission | Allows |
|---|---|
| `resourcemanager.projects.get` | AI Studio to verify project existence |
| `apikeys.keys.create` | Generate the API key |
| `serviceusage.services.enable` | Ensure Gemini API is active |

Fix: Ask project admin to grant a role with these permissions (Project Editor or custom role).

Alternative: Create a new project not associated with an organization.