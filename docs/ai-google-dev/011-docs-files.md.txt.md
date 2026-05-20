---
title: Files API
url: https://ai.google.dev/gemini-api/docs/files.md.txt
source: llms
fetched_at: 2026-04-29T11:17:25.601499117-03:00
rendered_js: false
word_count: 1763
summary: This document provides a comprehensive guide on managing media files for use with the Gemini API, covering the lifecycle operations of uploading, retrieving metadata, listing, and deleting files.
tags:
  - gemini-api
  - file-management
  - media-uploads
  - api-integration
  - multimodal-ai
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
Gemini handles text, images, audio, and other supported file types simultaneously.

## Upload a File

Use Files API when total request size exceeds 100 MB. For PDFs, limit is 50 MB.

```python
from google import genai

client = genai.Client()

myfile = client.files.upload(file="path/to/sample.mp3")

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=["Describe this audio clip", myfile]
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

async function main() {
  const myfile = await ai.files.upload({
    file: "path/to/sample.mp3",
    config: { mimeType: "audio/mpeg" },
  });

  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: createUserContent([
      createPartFromUri(myfile.uri, myfile.mimeType),
      "Describe this audio clip",
    ]),
  });
  console.log(response.text);
}

await main();
```

```go
file, err := client.Files.UploadFromPath(ctx, "path/to/sample.mp3", nil)
if err != nil {
    log.Fatal(err)
}
defer client.Files.Delete(ctx, file.Name)

resp, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", []*genai.Content{
  {
    Parts: []*genai.Part{
      genai.NewPartFromFile(*file),
      genai.NewPartFromText("Describe this audio clip"),
    },
  },
}, nil)

if err != nil {
    log.Fatal(err)
}

printResponse(resp)
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

## Get Metadata

Verify uploaded file and get metadata via `files.get`:

```python
from google import genai

client = genai.Client()

myfile = client.files.upload(file='path/to/sample.mp3')
file_name = myfile.name
myfile = client.files.get(name=file_name)
print(myfile)
```

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const myfile = await ai.files.upload({
    file: "path/to/sample.mp3",
    config: { mimeType: "audio/mpeg" },
  });

  const fileName = myfile.name;
  const fetchedFile = await ai.files.get({ name: fileName });
  console.log(fetchedFile);
}

await main();
```

```go
file, err := client.Files.UploadFromPath(ctx, "path/to/sample.mp3", nil)
if err != nil {
    log.Fatal(err)
}

gotFile, err := client.Files.Get(ctx, file.Name)
if err != nil {
    log.Fatal(err)
}
fmt.Println("Got file:", gotFile.Name)
```

```bash
# file_info.json was created in the upload example
name=$(jq ".file.name" file_info.json)
# Get the file of interest to check state
curl https://generativelanguage.googleapis.com/v1beta/files/$name \
-H "x-goog-api-key: $GEMINI_API_KEY" > file_info.json
# Print some information about the file you got
name=$(jq ".file.name" file_info.json)
echo name=$name
file_uri=$(jq ".file.uri" file_info.json)
echo file_uri=$file_uri
```

## List Uploaded Files

```python
from google import genai

client = genai.Client()

print('My files:')
for f in client.files.list():
    print(' ', f.name)
```

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const listResponse = await ai.files.list({ config: { pageSize: 10 } });
  for await (const file of listResponse) {
    console.log(file.name);
  }
}

await main();
```

```go
for file, err := range client.Files.All(ctx) {
  if err != nil {
      log.Fatal(err)
  }
  fmt.Println(file.Name)
}
```

```bash
echo "My files: "

curl "https://generativelanguage.googleapis.com/v1beta/files" \
  -H "x-goog-api-key: $GEMINI_API_KEY"
```

## Delete Uploaded Files

Files auto-delete after 48 hours. Manual deletion available:

```python
from google import genai

client = genai.Client()

myfile = client.files.upload(file='path/to/sample.mp3')
client.files.delete(name=myfile.name)
```

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const myfile = await ai.files.upload({
    file: "path/to/sample.mp3",
    config: { mimeType: "audio/mpeg" },
  });

  const fileName = myfile.name;
  await ai.files.delete({ name: fileName });
}

await main();
```

```go
file, err := client.Files.UploadFromPath(ctx, "path/to/sample.mp3", nil)
if err != nil {
    log.Fatal(err)
}
client.Files.Delete(ctx, file.Name)
```

```bash
curl --request "DELETE" https://generativelanguage.googleapis.com/v1beta/files/$name \
  -H "x-goog-api-key: $GEMINI_API_KEY"
```

## Usage Info

| Aspect | Details |
|---|---|
| **Storage per project** | Up to 20 GB |
| **Max file size** | 2 GB |
| **Retention** | 48 hours |
| **Metadata access** | Available; downloads not supported |
| **Cost** | Free in all regions where Gemini API is available |

## File Prompting Strategies

Use various data types in prompts for expanded capabilities. For example, send a photo and ask for a blog post about the meal.

| **Prompt** | **Response** |
|---|---|
| Write a short, engaging blog post based on this picture. It should include a description of the meal in the photo and talk about my journey meal prepping. <br /> ![Cookies](https://ai.google.dev/static/gemini-api/docs/images/image_prompt.png) | Meal prepping is a great way to save time and money, and it can also help you to eat healthier. This meal is a great example of a healthy and delicious meal that can be easily prepped ahead of time. This meal features brown rice, roasted vegetables, and chicken teriyaki. The brown rice is a healthy and complex carbohydrate that will give you sustained energy. The roasted vegetables are a great way to get your daily dose of vitamins and minerals, and the chicken teriyaki is a delicious and protein-rich option. This meal is also very easy to prepare. Simply cook the brown rice, roast the vegetables, and cook the chicken teriyaki. Once everything is cooked, divide it into meal prep containers and store them in the refrigerator. You can then grab a container and go on busy mornings! If you're looking for a healthy and delicious meal that can be easily prepped ahead of time, this meal is a great option. It's packed with nutrients and flavor, and it's sure to keep you feeling full and satisfied. Here's to healthy and delicious meal prepping! |

## Best Practices

### [Prompt design fundamentals](https://ai.google.dev/gemini-api/docs/files#specific-instructions)

- **Be specific** — Clear, concise instructions with minimal room for misinterpretation
- **Add few-shot examples** — Realistic examples to illustrate desired output
- **Break down tasks** — Divide complex tasks into manageable sub-goals
- **Specify output format** — Ask for markdown, JSON, HTML, etc.
- **Image first for single-image prompts** — Place image/video before text for single-image prompts; use natural order when interleaving images with text

### [Troubleshooting multimodal prompts](https://ai.google.dev/gemini-api/docs/files#troubleshooting)

- **Model ignores relevant parts** — Add hints about which aspects to focus on
- **Output too generic** — Ask model to describe image(s) first, or explicitly ask it to refer to what's in the image
- **Debugging** — Ask model to describe the image or explain reasoning
- **Hallucinated content** — Lower temperature or ask for shorter descriptions
- **Tuning parameters** — Experiment with temperature and top-k for creativity balance

> [!warning]
> For Gemini 3 models, keep `temperature` at default value 1.0. Setting below 1.0 may cause looping or degraded performance in complex mathematical or reasoning tasks.

## Be Specific in Your Instructions

Clear, detailed prompts get best results. Include specific requirements in the prompt.

| Prompt | Model response |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/timetable.png) Describe this image. | The image shows an airport arrivals and departures board. |

| **Updated prompt** | **Improved response** |
|---|---|
| ![Travel timetable](https://ai.google.dev/static/gemini-api/docs/images/timetable.png) Parse the time and city from the airport board shown in this image into a list. | - 10:50 Moscow - 11:05 Edinburgh - 11:05 London - 11:10 Bucharest - 11:30 Kiev - 11:35 Dublin - 11:45 East Midlands - 12:15 Sofia - 12:30 London - 12:30 Newcastle - 12:40 St Petersburg - 12:40 London - 12:45 Manchester |

## Add Few-Shot Examples

Use multiple inputs as examples. Model identifies patterns and applies relationships to new examples.

| **Prompt** | **Model response** |
|---|---|
| ![Travel timetable](https://ai.google.dev/static/gemini-api/docs/images/redeemer.png) Determine the city along with the landmark. | The landmark is the Christ the Redeemer statue in Rio de Janeiro, Brazil. |

| **Updated prompt** | **Improved response** |
|---|---|
| Determine the city along with the landmark. ![colosseum](https://ai.google.dev/static/gemini-api/docs/images/colosseum.png) | city: Rome, landmark: the Colosseum. |
| ![Forbidden City](https://ai.google.dev/static/gemini-api/docs/images/forbidden-city.png) | city: Beijing, landmark: Forbidden City |
| ![forbidden-city](https://ai.google.dev/static/gemini-api/docs/images/redeemer.png) | city: Rio de Janeiro, landmark: Christ the Redeemer statue |

## Break It Down Step-by-Step

Split complex visual understanding + reasoning tasks into smaller steps. Or ask model to "think step by step."

| Prompt | Model response |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/toilet-paper.jpg) When will I run out of toilet paper? | Soon, you only have 3 rolls left. |

| **Updated prompt** | **Improved response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/toilet-paper.jpg) 1. First, count how many toilet paper rolls are in this picture. 2. Then, determine how much toilet paper a typical person uses per day. 3. Calculate how long these rolls of toilet paper will last. | 1. There are 3 rolls of toilet paper in this picture. 2. A typical person uses about 20 sheets of toilet paper per day. 3. If each roll contains 200 sheets, then each roll will last for about 10 days. Therefore, the 3 rolls will last for about a month. |

Math problems and word problems benefit from step-by-step reasoning:

| **Prompt** | **Response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/math.jpg) What is the 4th term in the sequence? | -135 |

| **Updated prompt** | **Improved response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/math.jpg) Parse the formula in the image first. Then based on the formula, answer "what's the 4th term in the sequence?". | b(n) = b(n-1) * (-3), b(1) = 15. Working through: b(2) = -45, b(3) = 135, b(4) = -405 |

| **Updated prompt** | **Improved response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/math.jpg) What is the 4th term in the sequence? Think step by step. | First term: 15. Second term: 15 * (-3) = -45. Third term: -45 * (-3) = 135. Fourth term: 135 * (-3) = -405. |

## Specify Output Format

Ask for specific format (markdown, JSON, HTML):

| Prompt | Model response |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/excel-example.png) Parse the table in this image into markdown format | \| Subject \| Status \| Time \| Start date \| Due on \| \| --- \| --- \| --- \| --- \| --- \| \| Math \| Done \| 1.5 hrs \| 11/29/2023 \| 12/1/2023 \| \| Geography \| Done \| 30 min \| 12/2/2023 \| 12/4/2023 \| \| Physics \| In progress \| 2 hrs \| 12/3/2023 \| 12/5/2023 \| \| Biology \| Not started \| 6 hrs \| 11/2/2016 \| 12/6/2023 \| |

| **Prompt** | **Model response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/spanish-meal.png) Provide a list of all the following attributes: ingredients, type of cuisine, vegetarian or not, in JSON format | `{ "ingredients": ["rice", "shrimp", "clams", "mussels", "peas", "tomatoes", "onions", "garlic", "olive oil", "paprika", "salt", "pepper"], "type of cuisine": "Spanish", "vegetarian": false }` |

## Put Image First for Single-Image Prompts

While Gemini handles image and text in any order, placing a single image before text often produces better results.

## Troubleshooting Your Multimodal Prompt

### Model not drawing from relevant parts

Point out specific aspects you want focused on:

| Prompt | Model response |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/diapers.png) How many days will these diapers last a baby? | The diapers will last for 198 days before they run out. |

| **Updated prompt** | **Improved response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/diapers.png) How long will these diapers last before I run out? Use the weight shown on the box to determine the child's age, and use the total number of diapers in the box. Divide the total number by how many diapers the child goes through per day. | The box contains 198 diapers. The box states the diapers are for a child weighing 22-37 lbs. The average child in this weight range is likely between 1 and 2 years old. A 2-year-old typically goes through 6 diapers per day, therefore, the diapers will last around 33 days (198/6). |

### Output too generic

Ask model to describe images before reasoning:

| Prompt | Model response |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/packing.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/mall.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/toilet-paper.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/ocean.jpg) What is in common between these images? | All four images are examples of landscape photography. |

| **Updated prompt** | **Improved response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/packing.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/mall.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/toilet-paper.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/ocean.jpg) First, describe what's in each image in detail. What's in common between these images? | First: person packing suitcase. Second: empty hallway in shopping mall. Third: roll of toilet paper. Fourth: dark and stormy sea. All are examples of liminal spaces—places in between two other places or situations, characterized by uncertainty or ambiguity. |

Or explicitly ask to refer to what's in the images:

| **Updated prompt** | **Improved response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/packing.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/mall.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/toilet-paper.jpg) ![](https://ai.google.dev/static/gemini-api/docs/images/ocean.jpg) What is in common between these images? Refer to what's in the images in your response. | All images related to travel: packing suitcase (preparing for trip), mall hallway (shopping for trip), toilet paper (travel essential), stormy sea (encountered during travel). |

Same for creative output:

| Prompt | Model response |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/rabbit.jpg) Can you write me a poem about this image? | Little bunny, so soft and brown, Hopping through the field, up and down... |

| **Updated prompt** | **Improved response** |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/rabbit.jpg) Can you write me a descriptive and dramatic poem about this image and include the location? | Little bunny on the green, Ears so long, so keen... What do you see out there, In the distance, where you stare? Is it the ocean blue... |

### Troubleshooting which part failed

Ask model to describe the image or explain its reasoning to determine if failure is in understanding or reasoning:

| Prompt | Prompt for troubleshooting |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/tea-set.png) What's a snack I can make in 1 minute that would go well with this? | ![](https://ai.google.dev/static/gemini-api/docs/images/tea-set.png) Describe what's in this image. |

Or ask to explain reasoning:

| Prompt | Prompt for troubleshooting |
|---|---|
| ![](https://ai.google.dev/static/gemini-api/docs/images/tea-set.png) What's a snack I can make in 1 minute that would go well with this? | ![](https://ai.google.dev/static/gemini-api/docs/images/tea-set.png) What's a snack I can make in 1 minute that would go well with this? Please explain why. |

## What's Next

- Try multimodal prompts using [Google AI Studio](http://aistudio.google.com)
- See [Vision](https://ai.google.dev/gemini-api/docs/vision), [Audio](https://ai.google.dev/gemini-api/docs/audio), and [Document processing](https://ai.google.dev/gemini-api/docs/document-processing) guides
- [Prompt strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) for tuning sampling parameters