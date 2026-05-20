---
title: 'Video Understanding'
url: https://ai.google.dev/gemini-api/docs/video-understanding.md.txt
source: llms
fetched_at: 2026-04-29T11:17:09.439713933-03:00
rendered_js: false
word_count: 781
summary: This document provides an overview of how to process video content using Gemini models, detailing various input methods including the File API, Cloud Storage, and inline data for different video sizes and use cases.
tags:
    - gemini-api
    - video-processing
    - multimodal-ai
    - file-api
    - media-integration
    - developer-guide
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> To learn about video generation, see the [Veo](https://ai.google.dev/gemini-api/docs/video) guide.

Gemini models process videos for use cases that historically required domain-specific models. Capabilities include describing, segmenting, extracting information, answering questions, and referencing specific timestamps.

## Input methods

| Input method | Max size | Recommended use case |
|---|---|---|
| [[009-docs-file-input-methods\|File API]] | 20GB (paid) / 2GB (free) | Large files (100MB+), long videos (10min+), reusable files. |
| Cloud Storage Registration | 2GB (per file, no storage limits) | Large files (100MB+), long videos (10min+), persistent, reusable files. |
| Inline Data | < 100MB | Small files (<100MB), short duration (<1min), one-off inputs. |
| YouTube URLs | N/A | Public YouTube videos. |

> [!tip]
> The [[009-docs-file-input-methods\|File API]] is recommended for most use cases, especially for files larger than 100MB or when you want to reuse the file across multiple requests.

## Upload a video file

Upload via the [[011-docs-files\|Files API]], wait for processing, then use the file reference in `generateContent`.

### Python

```python
from google import genai

client = genai.Client()

myfile = client.files.upload(file="path/to/sample.mp4")

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=[myfile, "Summarize this video. Then create a quiz with an answer key based on the information in this video."]
)

print(response.text)
```

### JavaScript

```javascript
import {
  GoogleGenAI,
  createUserContent,
  createPartFromUri,
} from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const myfile = await ai.files.upload({
    file: "path/to/sample.mp4",
    config: { mimeType: "video/mp4" },
  });

  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: createUserContent([
      createPartFromUri(myfile.uri, myfile.mimeType),
      "Summarize this video. Then create a quiz with an answer key based on the information in this video.",
    ]),
  });
  console.log(response.text);
}

await main();
```

### Go

```go
uploadedFile, _ := client.Files.UploadFromPath(ctx, "path/to/sample.mp4", nil)

parts := []*genai.Part{
    genai.NewPartFromText("Summarize this video. Then create a quiz with an answer key based on the information in this video."),
    genai.NewPartFromURI(uploadedFile.URI, uploadedFile.MIMEType),
}

contents := []*genai.Content{
    genai.NewContentFromParts(parts, genai.RoleUser),
}

result, _ := client.Models.GenerateContent(
    ctx,
    "gemini-3-flash-preview",
    contents,
    nil,
)

fmt.Println(result.Text())
```

### REST

```bash
VIDEO_PATH="path/to/sample.mp4"
MIME_TYPE=$(file -b --mime-type "${VIDEO_PATH}")
NUM_BYTES=$(wc -c < "${VIDEO_PATH}")
DISPLAY_NAME=VIDEO

tmp_header_file=upload-header.tmp

echo "Starting file upload..."
curl "https://generativelanguage.googleapis.com/upload/v1beta/files" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -D ${tmp_header_file} \
  -H "X-Goog-Upload-Protocol: resumable" \
  -H "X-Goog-Upload-Command: start" \
  -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Header-Content-Type: ${MIME_TYPE}" \
  -H "Content-Type: application/json" \
  -d "{'file': {'display_name': '${DISPLAY_NAME}'}}" 2> /dev/null

upload_url=$(grep -i "x-goog-upload-url: " "${tmp_header_file}" | cut -d" " -f2 | tr -d "\r")
rm "${tmp_header_file}"

echo "Uploading video data..."
curl "${upload_url}" \
  -H "Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Offset: 0" \
  -H "X-Goog-Upload-Command: upload, finalize" \
  --data-binary "@${VIDEO_PATH}" 2> /dev/null > file_info.json

file_uri=$(jq -r ".file.uri" file_info.json)
echo file_uri=$file_uri

echo "File uploaded successfully. File URI: ${file_uri}"

# Generate content using the uploaded video file
echo "Generating content from video..."
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"file_data":{"mime_type": "'"${MIME_TYPE}"'", "file_uri": "'"${file_uri}"'"}},
          {"text": "Summarize this video. Then create a quiz with an answer key based on the information in this video."}]
        }]
      }' 2> /dev/null > response.json

jq -r ".candidates[].content.parts[].text" response.json
```

Use the [[011-docs-files\|Files API]] when total request size exceeds 20 MB, video duration is significant, or you reuse the same video in multiple prompts.

## Pass video data inline

For shorter videos under 20MB total request size, pass video data directly in the request.

### Python

```python
from google import genai
from google.genai import types

video_file_name = "/path/to/your/video.mp4"
video_bytes = open(video_file_name, 'rb').read()

client = genai.Client()
response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents=types.Content(
        parts=[
            types.Part(
                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
            ),
            types.Part(text='Please summarize the video in 3 sentences.')
        ]
    )
)
print(response.text)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

const ai = new GoogleGenAI({});
const base64VideoFile = fs.readFileSync("path/to/small-sample.mp4", {
  encoding: "base64",
});

const contents = [
  {
    inlineData: {
      mimeType: "video/mp4",
      data: base64VideoFile,
    },
  },
  { text: "Please summarize the video in 3 sentences." }
];

const response = await ai.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: contents,
});
console.log(response.text);
```

### REST

> [!note]
> If you get an `Argument list too long` error, the base64 encoding of your file might be too long for the curl command line. Use the File API method instead for larger files.

```bash
VIDEO_PATH=/path/to/your/video.mp4

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
            {
              "inline_data": {
                "mime_type":"video/mp4",
                "data": "'$(base64 $B64FLAGS $VIDEO_PATH)'"
              }
            },
            {"text": "Please summarize the video in 3 sentences."}
        ]
      }]
    }' 2> /dev/null
```

## Pass YouTube URLs

> [!warning]
> **Preview:** The YouTube URL feature is in preview and is available at no charge. Pricing and rate limits are likely to change.

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents=types.Content(
        parts=[
            types.Part(
                file_data=types.FileData(file_uri='https://www.youtube.com/watch?v=9hE5-98ZeCg')
            ),
            types.Part(text='Please summarize the video in 3 sentences.')
        ]
    )
)
print(response.text)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const contents = [
  {
    fileData: {
      fileUri: "https://www.youtube.com/watch?v=9hE5-98ZeCg",
    },
  },
  { text: "Please summarize the video in 3 sentences." }
];

const response = await ai.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: contents,
});
console.log(response.text);
```

### Go

```go
package main

import (
  "context"
  "fmt"
  "os"
  "google.golang.org/genai"
)

func main() {
  ctx := context.Background()
  client, err := genai.NewClient(ctx, nil)
  if err != nil {
      log.Fatal(err)
  }

  parts := []*genai.Part{
      genai.NewPartFromText("Please summarize the video in 3 sentences."),
      genai.NewPartFromURI("https://www.youtube.com/watch?v=9hE5-98ZeCg","video/mp4"),
  }

  contents := []*genai.Content{
      genai.NewContentFromParts(parts, genai.RoleUser),
  }

  result, _ := client.Models.GenerateContent(
      ctx,
      "gemini-3-flash-preview",
      contents,
      nil,
  )

  fmt.Println(result.Text())
}
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
    -H "x-goog-api-key: $GEMINI_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
            {"text": "Please summarize the video in 3 sentences."},
            {
              "file_data": {
                "file_uri": "https://www.youtube.com/watch?v=9hE5-98ZeCg"
              }
            }
        ]
      }]
    }' 2> /dev/null
```

**Limitations:**

- Free tier: up to 8 hours of YouTube video per day.
- Paid tier: no limit based on video length.
- Gemini 2.5 and later: up to 10 videos per request. Earlier models: 1 video per request.
- Only public videos supported (not private or unlisted).

## Use context caching for long videos

For videos longer than 10 minutes or multiple requests against the same video, use [[027-docs-thinking|context caching]] to reduce costs and improve latency.

## Refer to timestamps in the content

Use `MM:SS` format for specific moments in videos.

### Python

```python
prompt = "What are the examples given at 00:05 and 00:10 supposed to show us?"
```

### JavaScript

```javascript
const prompt = "What are the examples given at 00:05 and 00:10 supposed to show us?";
```

### Go

```go
prompt := []*genai.Part{
    genai.NewPartFromURI(currentVideoFile.URI, currentVideoFile.MIMEType),
    genai.NewPartFromText("What are the examples given at 00:05 and " +
        "00:10 supposed to show us?"),
}
```

### REST

```bash
PROMPT="What are the examples given at 00:05 and 00:10 supposed to show us?"
```

## Extract detailed insights from video

Gemini processes both audio and visual streams. The default sampling rate is **1 frame per second (FPS)**, which may miss details in videos with rapid motion. For high-motion content, consider [[045-docs-models-gemini-2.5-flash-image|setting a custom frame rate]].

### Python

```python
prompt = "Describe the key events in this video, providing both audio and visual details. Include timestamps for salient moments."
```

### JavaScript

```javascript
const prompt = "Describe the key events in this video, providing both audio and visual details. Include timestamps for salient moments.";
```

### Go

```go
prompt := []*genai.Part{
    genai.NewPartFromURI(currentVideoFile.URI, currentVideoFile.MIMEType),
    genai.NewPartFromText("Describe the key events in this video, providing both audio and visual details. " +
  "Include timestamps for salient moments."),
}
```

### REST

```bash
PROMPT="Describe the key events in this video, providing both audio and visual details. Include timestamps for salient moments."
```

## Customize video processing

Set clipping intervals or provide custom frame rate sampling.

> [!tip]
> Video clipping and FPS are supported by all models, but quality is significantly higher from 2.5 series models.

### Set clipping intervals

Specify `videoMetadata` with start and end offsets.

### Python

```python
from google import genai
from google.genai import types

client = genai.Client()
response = client.models.generate_content(
    model='models/gemini-3-flash-preview',
    contents=types.Content(
        parts=[
            types.Part(
                file_data=types.FileData(file_uri='https://www.youtube.com/watch?v=XEzRZ35urlk'),
                video_metadata=types.VideoMetadata(
                    start_offset='1250s',
                    end_offset='1570s'
                )
            ),
            types.Part(text='Please summarize the video in 3 sentences.')
        ]
    )
)
```

### JavaScript

```javascript
import { GoogleGenAI } from '@google/genai';
const ai = new GoogleGenAI({});
const model = 'gemini-3-flash-preview';

async function main() {
  const contents = [
    {
      role: 'user',
      parts: [
        {
          fileData: {
            fileUri: 'https://www.youtube.com/watch?v=9hE5-98ZeCg',
            mimeType: 'video/*',
          },
          videoMetadata: {
            startOffset: '40s',
            endOffset: '80s',
          }
        },
        {
          text: 'Please summarize the video in 3 sentences.',
        },
      ],
    },
  ];

  const response = await ai.models.generateContent({
    model,
    contents,
  });

  console.log(response.text)
}

await main();
```

### Set a custom frame rate

Pass an `fps` argument to `videoMetadata`.

> [!note]
> Due to built-in per-image safety checks, the same video may get blocked at some FPS and not at others due to different extracted frames.

### Python

```python
from google import genai
from google.genai import types

video_file_name = "/path/to/your/video.mp4"
video_bytes = open(video_file_name, 'rb').read()

client = genai.Client()
response = client.models.generate_content(
    model='models/gemini-3-flash-preview',
    contents=types.Content(
        parts=[
            types.Part(
                inline_data=types.Blob(
                    data=video_bytes,
                    mime_type='video/mp4'),
                video_metadata=types.VideoMetadata(fps=5)
            ),
            types.Part(text='Please summarize the video in 3 sentences.')
        ]
    )
)
```

**Default:** 1 FPS. Use lower FPS (< 1) for long, mostly static videos (e.g., lectures). Use higher FPS for granular temporal analysis (e.g., fast-action understanding).

## Supported video formats

- `video/mp4`
- `video/mpeg`
- `video/quicktime`
- `video/avi`
- `video/x-flv`
- `video/mpg`
- `video/webm`
- `video/wmv`
- `video/3gpp`

## Technical details

- **Supported models:** All Gemini models. Models with 1M context window support videos up to 1 hour (default resolution) or 3 hours (low resolution).
- **File API processing:** Videos stored at 1 FPS, audio at 1Kbps (single channel). Timestamps added every second.
- **Token calculation (per second of video):**
  - Frames at 1 FPS: 66 tokens/frame (low resolution) or 258 tokens/frame (default)
  - Audio: 32 tokens/second
  - Metadata included
  - **Total:** ~300 tokens/second (default) or ~100 tokens/second (low resolution)
- **Media resolution:** [[045-docs-models-gemini-2.5-flash-image|Gemini 3 `media_resolution` parameter]] controls tokens per input image or video frame. Higher resolutions improve fine text/small detail recognition but increase token usage and latency.
- **Timestamp format:** Use `MM:SS` (e.g., `01:15`).

**Best practices:**

- Use only one video per prompt request.
- Place the text prompt *after* the video part in the `contents` array.
- Fast action sequences may lose detail at 1 FPS sampling. Consider slowing down such clips if necessary.

## What's next

- [[027-docs-thinking|System instructions]]: Steer model behavior with specific instructions.
- [[011-docs-files|Files API]]: Upload and manage files for Gemini.
- [[023-docs-prompting-strategies|File prompting strategies]]: Multimodal prompting with text, images, audio, and video.
- [[024-docs-safety-settings|Safety guidance]]: Limit risk from unexpected outputs.