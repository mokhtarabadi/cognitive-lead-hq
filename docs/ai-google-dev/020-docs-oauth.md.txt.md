---
title: OAuth 2.0 setup for Gemini API
url: https://ai.google.dev/gemini-api/docs/oauth.md.txt
source: llms
fetched_at: 2026-04-29T11:16:51.458471363-03:00
rendered_js: false
word_count: 409
summary: This guide provides instructions for setting up OAuth 2.0 authentication for the Gemini API using Google Cloud projects and application-default-credentials.
tags:
    - gemini-api
    - oauth2
    - google-cloud
    - authentication
    - gcloud-sdk
    - api-security
    - python
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
Use OAuth 2.0 for stricter access controls beyond API keys. This guide covers a simplified setup appropriate for testing environments. For production, see [authentication and authorization](https://developers.google.com/workspace/guides/auth-overview) before [choosing credentials](https://developers.google.com/workspace/guides/create-credentials#choose_the_access_credential_that_is_right_for_you).

## Objectives

- Set up your Cloud project for OAuth
- Set up application-default-credentials
- Manage credentials in code (instead of `gcloud auth`)

## Prerequisites

- [A Google Cloud project](https://developers.google.com/workspace/guides/create-project)
- [Local installation of the gcloud CLI](https://cloud.google.com/sdk/docs/install)

## Set up your Cloud project

### 1. Enable the API

Enable the **Google Generative Language API** in the [Google Cloud console](https://console.cloud.google.com/flows/enableapi?apiid=generativelanguage.googleapis.com).

### 2. Configure the OAuth consent screen

1. Go to **Menu** > **Google Auth platform** > **Overview** ([link](https://console.developers.google.com/auth/overview)).
2. Set user type to **External** in the **Audience** section and complete the form.
3. Accept User Data Policy terms and click **Create**.
4. Skip adding scopes and click **Save and Continue**.
5. Add test users:
   - Navigate to the [Audience page](https://console.developers.google.com/auth/audience).
   - Under **Test users**, click **Add users**, enter emails, and click **Save**.

### 3. Create OAuth 2.0 client credentials

1. Go to **Menu** > **Google Auth platform** > **Clients** ([link](https://console.developers.google.com/auth/clients)).
2. Click **Create Client** > **Desktop app**.
3. Name the credential and click **Create**.
4. Click the download button to save the JSON. Rename it to `client_secret.json` and move it to your working directory.

## Set up Application Default Credentials

Convert `client_secret.json` to usable credentials:

```bash
gcloud auth application-default login \
    --client-id-file=client_secret.json \
    --scopes='https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language.retriever'
```

This places the resulting token in a well-known location for `gcloud` and client libraries.

> [!note]
> If running on Colab, include `--no-browser` and carefully follow the printed instructions (don't just click the link). Ensure your local `gcloud --version` is [latest](https://cloud.google.com/sdk/docs/release-notes) to match Colab.

```bash
gcloud auth application-default login \
    --no-browser \
    --client-id-file=client_secret.json \
    --scopes='https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/generative-language.retriever'
```

> [!warning]
> The simplified setup triggers a **"Google hasn't verified this app."** dialog. This is normal — choose **Continue**.

### Test with curl

```bash
access_token=$(gcloud auth application-default print-access-token)
project_id=<MY PROJECT ID>
curl -X GET https://generativelanguage.googleapis.com/v1/models \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${access_token}" \
    -H "x-goog-user-project: ${project_id}" | grep '"name"'
```

### Test with Python

```bash
pip install google-genai
```

```python
from google import genai

client = genai.Client()
print('Available base models:', [m.name for m in client.models.list()])
```

## Manage credentials in code

When `gcloud` is unavailable, use language-specific libraries to manage OAuth tokens in-app. See the [Drive API quickstart](https://developers.google.com/drive/api/quickstart/python) for equivalents in other languages.

### 1. Install libraries

```bash
pip install --upgrade -q google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install google-genai
```

### 2. Write the credential manager

Create `load_creds.py` to cache tokens in `token.json` and refresh them on expiry:

```python
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/generative-language.retriever']

def load_creds():
    """Converts `client_secret.json` to a credential object. Caches tokens to minimize consent screen use."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
```

### 3. Write your program

```python
import pprint
from google import genai
from load_creds import load_creds

creds = load_creds()

client = genai.Client(credentials=creds)

print()
print('Available base models:', [m.name for m in client.models.list()])
```

### 4. Run your program

```bash
python script.py
```

1. Sign in to the Google Account you set as the "Test Account" during project setup.
2. The **"Google hasn't verified this app"** dialog may appear — choose **Continue**.
3. Credentials are stored locally; you won't be prompted on subsequent runs.

> [!tip]
> For semantic retrieval setup, see [[semantic_retriever|Semantic retrieval on your text data]].
