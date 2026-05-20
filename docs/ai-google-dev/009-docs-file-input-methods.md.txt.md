---
title: File Input Methods
url: https://ai.google.dev/gemini-api/docs/file-input-methods.md.txt
source: llms
fetched_at: 2026-04-29T11:17:23.439938169-03:00
rendered_js: false
word_count: 648
summary: This document provides an overview of various methods for including multimedia files in Gemini API requests, covering inline data, File API uploads, and external URL references.
tags:
  - gemini-api
  - media-processing
  - file-upload
  - api-integration
  - multimodal-ai
  - data-handling
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
This guide explains how to include media files (images, audio, video, documents) in Gemini API requests across all endpoints including Batch, Interactions, and Live API.

The choice of method depends on file size, storage location, and usage frequency.

## Quick Example: Read Local File

```python
from google import genai
from google.genai import types
import pathlib

client = genai.Client()

filepath = pathlib.Path('my_local_file.pdf')

prompt = "Summarize this document"
response = client.models.generate_content(
  model="gemini-3-flash-preview",
  contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='application/pdf',
      ),
      prompt
  ]
)
print(response.text)
```

```javascript
import { GoogleGenAI } from "@google/genai";
import * as fs from 'node:fs';

const ai = new GoogleGenAI({});
const prompt = "Summarize this document";

async function main() {
    const filePath = path.join('content', 'my_local_file.pdf');

    const contents = [
        { text: prompt },
        {
            inlineData: {
                mimeType: 'application/pdf',
                data: fs.readFileSync(filePath).toString("base64")
            }
        }
    ];

    const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: contents
    });
    console.log(response.text);
}

main();
```

```bash
# Encode the local file to base64
B64_CONTENT=$(base64 -w 0 my_local_file.pdf)

curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [
      {
        "parts": [
          {"text": "Summarize this document"}
        ]
      },
      {
        "parts": [
          {
            "inlineData": {
              "mimeType": "application/pdf",
              "data": "'"${B64_CONTENT}"'"
            }
          }
        ]
      }
    ]
  }'
```

## Input Method Comparison

| Method | Best for | Max file size | Persistence |
|---|---|---|---|
| **Inline data** | Quick testing, small files, real-time applications | 100 MB per request (**50 MB for PDFs**) | None (sent with every request) |
| **File API upload** | Large files, files used multiple times | 2 GB per file, up to 20 GB per project | 48 Hours |
| **File API GCS URI registration** | Large files already in Google Cloud Storage | 2 GB per file, no overall storage limits | None (fetched per request); one-time registration grants access up to 30 days |
| **External URLs** | Public data or cloud buckets (AWS, Azure, GCS) without re-uploading | 100 MB per request | None (fetched per request) |

## Inline Data

For files under 100 MB (50 MB for PDFs), pass data directly in the request payload. Simplest method for quick tests and real-time applications.

### Fetch from a URL

```python
from google import genai
from google.genai import types
import httpx

client = genai.Client()

doc_url = "https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"
doc_data = httpx.get(doc_url).content

prompt = "Summarize this document"

response = client.models.generate_content(
  model="gemini-3-flash-preview",
  contents=[
      types.Part.from_bytes(
        data=doc_data,
        mime_type='application/pdf',
      ),
      prompt
  ]
)
print(response.text)
```

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});
const docUrl = 'https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf';
const prompt = "Summarize this document";

async function main() {
    const pdfResp = await fetch(docUrl);
      .then((response) => response.arrayBuffer());

    const contents = [
        { text: prompt },
        {
            inlineData: {
                mimeType: 'application/pdf',
                data: Buffer.from(pdfResp).toString("base64")
            }
        }
    ];

    const response = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: contents
    });
    console.log(response.text);
}

main();
```

```bash
DOC_URL="https://discovery.ucl.ac.uk/id/eprint/10089234/1/343019_3_art_0_py4t4l_convrt.pdf"
PROMPT="Summarize this document"
DISPLAY_NAME="base64_pdf"

# Download the PDF
wget -O "${DISPLAY_NAME}.pdf" "${DOC_URL}"

# Check for FreeBSD base64 and set flags accordingly
if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

# Base64 encode the PDF
ENCODED_PDF=$(base64 $B64FLAGS "${DISPLAY_NAME}.pdf")

# Generate content using the base64 encoded PDF
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"inline_data": {"mime_type": "application/pdf", "data": "'"$ENCODED_PDF"'"}},
          {"text": "'$PROMPT'"}
        ]
      }]
    }' 2> /dev/null > response.json

cat response.json
echo

jq ".candidates[].content.parts[].text" response.json
```

## Gemini File API

For files up to 2 GB or files used multiple times.

### Standard File Upload

```python
from google import genai
client = genai.Client()

# Upload the file
audio_file = client.files.upload(file="path/to/your/sample.mp3")
prompt = "Describe this audio clip"

# Use the uploaded file in a prompt
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[prompt, audio_file]
)
print(response.text)
```

```javascript
import {
  GoogleGenAI,
  createUserContent,
  createPartFromUri,
} from "@google/genai";

const ai = new GoogleGenAI({});
const prompt = "Describe this audio clip";

async function main() {
  const filePath = "path/to/your/sample.mp3";

  const myfile = await ai.files.upload({
    file: filePath,
    config: { mimeType: "audio/mpeg" },
  });

  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: createUserContent([
      prompt,
      createPartFromUri(myfile.uri, myfile.mimeType),
    ]),
  });
  console.log(response.text);

}
await main();
```

```bash
AUDIO_PATH="path/to/sample.mp3"
MIME_TYPE=$(file -b --mime-type "${AUDIO_PATH}")
NUM_BYTES=$(wc -c < "${AUDIO_PATH}")
DISPLAY_NAME=AUDIO

tmp_header_file=upload-header.tmp

# Initial resumable request defining metadata.
# The upload url is in the response headers dump them to a file.
curl "${BASE_URL}/upload/v1beta/files" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -D "${tmp_header_file}" \
  -H "X-Goog-Upload-Protocol: resumable" \
  -H "X-Goog-Upload-Command: start" \
  -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Header-Content-Type: ${MIME_TYPE}" \
  -H "Content-Type: application/json" \
  -d "{'file': {'display_name': '${DISPLAY_NAME}'}}" 2> /dev/null

upload_url=$(grep -i "x-goog-upload-url: " "${tmp_header_file}" | cut -d" " -f2 | tr -d "\r")
rm "${tmp_header_file}"

# Upload the actual bytes.
curl "${upload_url}" \
  -H "Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Offset: 0" \
  -H "X-Goog-Upload-Command: upload, finalize" \
  --data-binary "@${AUDIO_PATH}" 2> /dev/null > file_info.json

file_uri=$(jq ".file.uri" file_info.json)
echo file_uri=$file_uri

# Now generate content using that file
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Describe this audio clip"},
          {"file_data":{"mime_type": "${MIME_TYPE}", "file_uri": '$file_uri'}}]
        }]
      }' 2> /dev/null > response.json

cat response.json
echo

jq ".candidates[].content.parts[].text" response.json
```

### Register Google Cloud Storage Files

Register GCS files directly without downloading/re-uploading.

**1. Grant Service Agent access to each bucket:**

1. Enable Gemini API in your Google Cloud project
2. Create the Service Agent: `gcloud beta services identity create --service=generativelanguage.googleapis.com --project=<your_project>`
3. Grant the Gemini API Service Agent `Storage Object Viewer` IAM role on the storage buckets

**2. Authenticate your service:**

**Outside of Google Cloud:**

Download service account credentials:
1. Go to [Service Account console](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Select relevant service account
3. **Keys** tab → **Add key** → **Create new key** → **JSON**

```python
from google.oauth2.service_account import Credentials

GCS_READ_SCOPES = [       
  'https://www.googleapis.com/auth/devstorage.read_only',
  'https://www.googleapis.com/auth/cloud-platform'
]

SERVICE_ACCOUNT_FILE = 'service-account.json'

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=GCS_READ_SCOPES
)
```

```javascript
const { GoogleAuth } = require('google-auth-library');

const GCS_READ_SCOPES = [
  'https://www.googleapis.com/auth/devstorage.read_only',
  'https://www.googleapis.com/auth/cloud-platform'
];

const SERVICE_ACCOUNT_FILE = 'service-account.json';

const auth = new GoogleAuth({
  keyFile: SERVICE_ACCOUNT_FILE,
  scopes: GCS_READ_SCOPES
});
```

```bash
gcloud auth application-default login \
  --client-id-file=service-account.json \
  --scopes='https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/devstorage.read_only'
```

**On Google Cloud:**

For [Cloud Run](https://cloud.google.com/functions) or [Compute Engine](https://cloud.google.com/products/compute):

```python
import google.auth

GCS_READ_SCOPES = [       
  'https://www.googleapis.com/auth/devstorage.read_only',
  'https://www.googleapis.com/auth/cloud-platform'
]

credentials, project = google.auth.default(scopes=GCS_READ_SCOPES)
```

```javascript
const { GoogleAuth } = require('google-auth-library');

const auth = new GoogleAuth({
  scopes: [
    'https://www.googleapis.com/auth/devstorage.read_only',
    'https://www.googleapis.com/auth/cloud-platform'
  ]
});
```

```bash
gcloud auth application-default login \
--scopes="https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/devstorage.read_only"
```

**3. File registration:**

```python
from google import genai
from google.genai.types import Part

# Note that you must provide an API key in the GEMINI_API_KEY
# environment variable, but it is unused for the registration endpoint.
client = genai.Client()

registered_gcs_files = client.files.register_files(
    uris=["gs://my_bucket/some_object.pdf", "gs://bucket2/object2.txt"],
    # Use the credentials obtained in the previous step.
    auth=credentials
)
prompt = "Summarize this file."

# call generateContent for each file
for f in registered_gcs_files.files:
  print(f.name)
  response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[Part.from_uri(
      file_uri=f.uri,
      mime_type=f.mime_type,
    ),
    prompt],
  )
  print(response.text)
```

```bash
access_token=$(gcloud auth application-default print-access-token)
project_id=$(gcloud config get-value project)
curl -X POST https://generativelanguage.googleapis.com/v1beta/files:register \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer ${access_token}" \
    -H "x-goog-user-project: ${project_id}" \
    -d '{"uris": ["gs://bucket/object1", "gs://bucket/object2"]}'
```

## External HTTP / Signed URLs

Pass publicly accessible HTTPS URLs or pre-signed URLs (S3, Azure SAS) directly. Gemini fetches content securely during processing. Ideal for files up to 100 MB.

> [!warning]
> Gemini 2.0 family of models are not supported

### Python

```python
from google import genai
from google.genai.types import Part

uri = "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf"
prompt = "Summarize this file"

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        Part.from_uri(
            file_uri=uri,
            mime_type="application/pdf",
        ),
        prompt
    ],
)
print(response.text)
```

### JavaScript

```javascript
import { GoogleGenAI, createPartFromUri } from '@google/genai';

const client = new GoogleGenAI({});

const uri = "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf";

async function main() {
  const response = await client.models.generateContent({
    model: 'gemini-3-flash-preview',
    contents: [
      // equivalent to Part.from_uri(file_uri=uri, mime_type="...")
      createPartFromUri(uri, "application/pdf"),
      "summarize this file",
    ],
  });

  console.log(response.text);
}

main();
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent \
      -H 'x-goog-api-key: $GEMINI_API_KEY' \
      -H 'Content-Type: application/json' \
      -d '{
          "contents":[
            {
              "parts":[
                {"text": "Summarize this pdf"},
                {
                  "file_data": {
                    "mime_type":"application/pdf",
                    "file_uri": "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf"
                  }
                }
              ]
            }
          ]
        }'
```

### Accessibility

Verify URLs don't require login or are behind paywalls. For private databases, ensure signed URLs have correct access permissions and expiry.

### Safety Checks

The system performs content moderation on the URL. If it fails safety checks (opted-out or paywalled content), you'll get `url_retrieval_status` of `URL_RETRIEVAL_STATUS_UNSAFE`.

## Supported Content Types

> [!info]
> This list is guidance; supported types may change based on model and tokenizer version. Unsupported types result in errors. Content retrieval currently only supports publicly accessible URLs.

### Text file types

- `text/html`, `text/css`, `text/plain`, `text/xml`, `text/csv`, `text/rtf`, `text/javascript`

### Application file types

- `application/json`, `application/pdf`

### Image file types

- `image/bmp`, `image/jpeg`, `image/png`, `image/webp`

## Best Practices

- **Choose the right method** — Inline for small transient files; File API for larger or frequently used files; External URLs for data already hosted online
- **Specify MIME Types** — Always provide correct MIME type for proper processing
- **Handle Errors** — Implement error handling for network failures, file access problems, or API errors
- **Manage GCS Permissions** — Grant Service Agent only `Storage Object Viewer` role on specific buckets
- **Signed URL Security** — Ensure appropriate expiration and limited permissions

## Limitations

- File size limits vary by method (see comparison table)
- Inline data increases request payload size
- File API uploads are temporary (48 hours)
- External URL fetching limited to 100 MB per payload
- GCS registration requires IAM setup and OAuth token management

## What's Next

- Try multimodal prompts using [Google AI Studio](http://aistudio.google.com/)
- See [Vision](https://ai.google.dev/gemini-api/docs/vision), [Audio](https://ai.google.dev/gemini-api/docs/audio), and [Document processing](https://ai.google.dev/gemini-api/docs/document-processing) guides
- [Prompt strategies](https://ai.google.dev/gemini-api/docs/prompt-strategies) for guidance on tuning sampling parameters