---
title: Understand and count tokens
url: https://ai.google.dev/gemini-api/docs/tokens.md.txt
source: llms
fetched_at: 2026-04-29T11:17:02.398337814-03:00
rendered_js: false
word_count: 313
summary: This document explains the concept of tokens in Gemini AI models and provides instructions on how to calculate token usage using API methods and response metadata.
tags:
    - gemini-api
    - tokenization
    - usage-tracking
    - api-integration
    - prompt-engineering
    - cost-management
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
A *token* is the granularity at which Gemini processes input and output. For Gemini models, **a token is ~4 characters; 100 tokens ≈ 60-80 English words**.

Tokens can be single characters (`z`) or whole words (`cat`). Long words are broken into several tokens. The set of all tokens is the *vocabulary*; splitting text into tokens is *tokenization*.

Billing is based on input and output token counts. See [Pricing](https://ai.google.dev/pricing) for costs.

## Count tokens

All input is tokenized: text, images, and other modalities.

| Method | What it returns |
|--------|-----------------|
| `count_tokens` API call | Input tokens only (`total_tokens`) |
| `usage_metadata` on response | Input + output tokens: `prompt_token_count`, `candidates_token_count`, `total_token_count` |
| Thinking models | Adds `thoughts_token_count` |
| Context caching | Adds `cached_content_token_count` |

### Count text tokens

#### Python

```python
from google import genai

client = genai.Client()
prompt = "The quick brown fox jumps over the lazy dog."

total_tokens = client.models.count_tokens(
    model="gemini-3-flash-preview", contents=prompt
)
print("total_tokens: ", total_tokens)

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=prompt
)
print(response.usage_metadata)
```

#### JavaScript

```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({});
const prompt = "The quick brown fox jumps over the lazy dog.";

async function main() {
  const countTokensResponse = await ai.models.countTokens({
    model: "gemini-3-flash-preview",
    contents: prompt,
  });
  console.log(countTokensResponse.totalTokens);

  const generateResponse = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: prompt,
  });
  console.log(generateResponse.usageMetadata);
}

await main();
```

#### Go

```go
ctx := context.Background()
client, err := genai.NewClient(ctx, nil)

contents := []*genai.Content{
    genai.NewContentFromText(prompt, genai.RoleUser),
}
countResp, err := client.Models.CountTokens(ctx, "gemini-3-flash-preview", contents, nil)
if err != nil {
    return err
}
fmt.Println("total_tokens:", countResp.TotalTokens)

response, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", contents, nil)
if err != nil {
    log.Fatal(err)
}
usageMetadata, err := json.MarshalIndent(response.UsageMetadata, "", "  ")
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(usageMetadata))
```

### Count multi-turn (chat) tokens

Call `count_tokens` with chat history to get total token count. Append your next message to history to estimate the next conversational turn's size.

#### Python

```python
from google import genai
from google.genai import types

client = genai.Client()

chat = client.chats.create(
    model="gemini-3-flash-preview",
    history=[
        types.Content(role="user", parts=[types.Part(text="Hi my name is Bob")]),
        types.Content(role="model", parts=[types.Part(text="Hi Bob!")]),
    ],
)

print(client.models.count_tokens(
    model="gemini-3-flash-preview", contents=chat.get_history()
))

response = chat.send_message(
    message="In one sentence, explain how a computer works to a young child."
)
print(response.usage_metadata)

# Count tokens for next turn
extra = types.UserContent(parts=[types.Part(text="What is the meaning of life?")])
history = [*chat.get_history(), extra]
print(client.models.count_tokens(model="gemini-3-flash-preview", contents=history))
```

#### JavaScript

```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({});

async function main() {
  const history = [
    { role: "user", parts: [{ text: "Hi my name is Bob" }] },
    { role: "model", parts: [{ text: "Hi Bob!" }] },
  ];
  const chat = ai.chats.create({
    model: "gemini-3-flash-preview",
    history: history,
  });

  const countTokensResponse = await ai.models.countTokens({
    model: "gemini-3-flash-preview",
    contents: chat.getHistory(),
  });
  console.log(countTokensResponse.totalTokens);

  const chatResponse = await chat.sendMessage({
    message: "In one sentence, explain how a computer works to a young child.",
  });
  console.log(chatResponse.usageMetadata);

  const extraMessage = { role: "user", parts: [{ text: "What is the meaning of life?" }] };
  const combinedHistory = [...chat.getHistory(), extraMessage];
  const combinedCountTokensResponse = await ai.models.countTokens({
    model: "gemini-3-flash-preview",
    contents: combinedHistory,
  });
  console.log("Combined history token count:", combinedCountTokensResponse.totalTokens);
}

await main();
```

#### Go

```go
ctx := context.Background()
client, err := genai.NewClient(ctx, nil)

history := []*genai.Content{
    {Role: genai.RoleUser, Parts: []*genai.Part({Text: "Hi my name is Bob"})},
    {Role: genai.RoleModel, Parts: []*genai.Part({Text: "Hi Bob!"})},
}
chat, err := client.Chats.Create(ctx, "gemini-3-flash-preview", nil, history)
if err != nil {
    log.Fatal(err)
}

firstTokenResp, err := client.Models.CountTokens(ctx, "gemini-3-flash-preview", chat.History(false), nil)
if err != nil {
    log.Fatal(err)
}
fmt.Println(firstTokenResp.TotalTokens)

resp, err := chat.SendMessage(ctx, genai.NewPartFromText("In one sentence, explain how a computer works to a young child."))
if err != nil {
    log.Fatal(err)
}
fmt.Printf("%#v\n", resp.UsageMetadata)

extra := genai.NewContentFromText("What is the meaning of life?", genai.RoleUser)
hist := chat.History(false)
hist = append(hist, extra)
secondTokenResp, err := client.Models.CountTokens(ctx, "gemini-3-flash-preview", hist, nil)
if err != nil {
    log.Fatal(err)
}
fmt.Println(secondTokenResp.TotalTokens)
```

### Count multimodal tokens

All input is tokenized: text, images, video, audio.

| Input type | Token calculation |
|------------|------------------|
| Image (both dims ≤384px) | 258 tokens |
| Image (larger) | Cropped/scaled into 768x768px tiles, each = 258 tokens |
| Video | 263 tokens/second |
| Audio | 32 tokens/second |

> [!NOTE]
> Gemini 3 models introduce `media_resolution` parameter for granular control over multimodal vision processing. See [media resolution](https://ai.google.dev/gemini-api/docs/media-resolution) guide.

#### Image files

Using File API:

##### Python

```python
from google import genai

client = genai.Client()
prompt = "Tell me about this image"
your_image_file = client.files.upload(file=media / "organ.jpg")

print(client.models.count_tokens(
    model="gemini-3-flash-preview", contents=[prompt, your_image_file]
))

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=[prompt, your_image_file]
)
print(response.usage_metadata)
```

##### JavaScript

```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({});
const prompt = "Tell me about this image";

async function main() {
  const organ = await ai.files.upload({
    file: path.join(media, "organ.jpg"),
    config: { mimeType: "image/jpeg" },
  });

  const countTokensResponse = await ai.models.countTokens({
    model: "gemini-3-flash-preview",
    contents: createUserContent([prompt, createPartFromUri(organ.uri, organ.mimeType)]),
  });
  console.log(countTokensResponse.totalTokens);

  const generateResponse = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: createUserContent([prompt, createPartFromUri(organ.uri, organ.mimeType)]),
  });
  console.log(generateResponse.usageMetadata);
}

await main();
```

##### Go

```go
ctx := context.Background()
client, err := genai.NewClient(ctx, nil)

file, err := client.Files.UploadFromPath(ctx, filepath.Join(getMedia(), "organ.jpg"), &genai.UploadFileConfig{MIMEType: "image/jpeg"})
if err != nil {
    log.Fatal(err)
}
parts := []*genai.Part{
    genai.NewPartFromText("Tell me about this image"),
    genai.NewPartFromURI(file.URI, file.MIMEType),
}
contents := []*genai.Content{genai.NewContentFromParts(parts, genai.RoleUser)}

tokenResp, err := client.Models.CountTokens(ctx, "gemini-3-flash-preview", contents, nil)
if err != nil {
    log.Fatal(err)
}
fmt.Println("Multimodal image token count:", tokenResp.TotalTokens)

response, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", contents, nil)
if err != nil {
    log.Fatal(err)
}
usageMetadata, err := json.MarshalIndent(response.UsageMetadata, "", "  ")
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(usageMetadata))
```

Using inline data:

##### Python

```python
from google import genai
import PIL.Image

client = genai.Client()
prompt = "Tell me about this image"
your_image_file = PIL.Image.open(media / "organ.jpg")

print(client.models.count_tokens(
    model="gemini-3-flash-preview", contents=[prompt, your_image_file]
))

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=[prompt, your_image_file]
)
print(response.usage_metadata)
```

##### JavaScript

```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({});
const prompt = "Tell me about this image";
const imageBuffer = fs.readFileSync(path.join(media, "organ.jpg"));
const imageBase64 = imageBuffer.toString("base64");

const contents = createUserContent([
    prompt,
    createPartFromBase64(imageBase64, "image/jpeg"),
]);

async function main() {
  const countTokensResponse = await ai.models.countTokens({
    model: "gemini-3-flash-preview",
    contents: contents,
  });
  console.log(countTokensResponse.totalTokens);

  const generateResponse = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: contents,
  });
  console.log(generateResponse.usageMetadata);
}

await main();
```

##### Go

```go
ctx := context.Background()
client, err := genai.NewClient(ctx, nil)

imageBytes, err := os.ReadFile("organ.jpg")
if err != nil {
    log.Fatalf("Failed to read image file: %v", err)
}
parts := []*genai.Part{
    genai.NewPartFromText("Tell me about this image"),
    {InlineData: &genai.Blob{MIMEType: "image/jpeg", Data: imageBytes}},
}
contents := []*genai.Content{genai.NewContentFromParts(parts, genai.RoleUser)}

tokenResp, err := client.Models.CountTokens(ctx, "gemini-3-flash-preview", contents, nil)
if err != nil {
    log.Fatal(err)
}
fmt.Println("Multimodal image token count:", tokenResp.TotalTokens)

response, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", contents, nil)
if err != nil {
    log.Fatal(err)
}
usageMetadata, err := json.MarshalIndent(response.UsageMetadata, "", "  ")
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(usageMetadata))
```

#### Video or audio files

Audio: 32 tokens/second; Video: 263 tokens/second.

##### Python

```python
from google import genai
import time

client = genai.Client()
prompt = "Tell me about this video"
your_file = client.files.upload(file=media / "Big_Buck_Bunny.mp4")

while not your_file.state or your_file.state.name != "ACTIVE":
    print("Processing video...")
    print("File state:", your_file.state)
    time.sleep(5)
    your_file = client.files.get(name=your_file.name)

print(client.models.count_tokens(
    model="gemini-3-flash-preview", contents=[prompt, your_file]
))

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=[prompt, your_file]
)
print(response.usage_metadata)
```

##### JavaScript

```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({});
const prompt = "Tell me about this video";

async function main() {
  let videoFile = await ai.files.upload({
    file: path.join(media, "Big_Buck_Bunny.mp4"),
    config: { mimeType: "video/mp4" },
  });

  while (!videoFile.state || videoFile.state.toString() !== "ACTIVE") {
    console.log("Processing video...");
    console.log("File state: ", videoFile.state);
    await sleep(5000);
    videoFile = await ai.files.get({ name: videoFile.name });
  }

  const countTokensResponse = await ai.models.countTokens({
    model: "gemini-3-flash-preview",
    contents: createUserContent([prompt, createPartFromUri(videoFile.uri, videoFile.mimeType)]),
  });
  console.log(countTokensResponse.totalTokens);

  const generateResponse = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: createUserContent([prompt, createPartFromUri(videoFile.uri, videoFile.mimeType)]),
  });
  console.log(generateResponse.usageMetadata);
}

await main();
```

##### Go

```go
ctx := context.Background()
client, err := genai.NewClient(ctx, nil)

file, err := client.Files.UploadFromPath(ctx, filepath.Join(getMedia(), "Big_Buck_Bunny.mp4"), &genai.UploadFileConfig{MIMEType: "video/mp4"})
if err != nil {
    log.Fatal(err)
}

for file.State == genai.FileStateUnspecified || file.State != genai.FileStateActive {
    fmt.Println("Processing video...")
    fmt.Println("File state:", file.State)
    time.Sleep(5 * time.Second)
    file, err = client.Files.Get(ctx, file.Name, nil)
    if err != nil {
        log.Fatal(err)
    }
}

parts := []*genai.Part{
    genai.NewPartFromText("Tell me about this video"),
    genai.NewPartFromURI(file.URI, file.MIMEType),
}
contents := []*genai.Content{genai.NewContentFromParts(parts, genai.RoleUser)}

tokenResp, err := client.Models.CountTokens(ctx, "gemini-3-flash-preview", contents, nil)
if err != nil {
    log.Fatal(err)
}
fmt.Println("Multimodal video/audio token count:", tokenResp.TotalTokens)

response, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", contents, nil)
if err != nil {
    log.Fatal(err)
}
usageMetadata, err := json.MarshalIndent(response.UsageMetadata, "", "  ")
if err != nil {
    log.Fatal(err)
}
fmt.Println(string(usageMetadata))
```

## Context windows

The context window defines maximum input and output token limits. Get size via [`models.get`](https://ai.google.dev/api/rest/v1/models/get) endpoint or [models documentation](https://ai.google.dev/gemini-api/docs/models).

### Python

```python
from google import genai

client = genai.Client()
model_info = client.models.get(model="gemini-3-flash-preview")
print(f"{model_info.input_token_limit=}")
print(f"{model_info.output_token_limit=}")
```

### JavaScript

```javascript
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({});

async function main() {
  const modelInfo = await ai.models.get({model: 'gemini-3-flash-preview'});
  console.log(modelInfo.inputTokenLimit);
  console.log(modelInfo.outputTokenLimit);
}

await main();
```

### Go

```go
ctx := context.Background()
client, err := genai.NewClient(ctx, nil)
if err != nil {
    log.Fatal(err)
}
modelInfo, err := client.ModelInfo(ctx, "models/gemini-3-flash-preview")
if err != nil {
    log.Fatal(err)
}
fmt.Println("input token limit:", modelInfo.InputTokenLimit)
fmt.Println("output token limit:", modelInfo.OutputTokenLimit)
```

#topic-tokenization #topic-cost-management #topic-api-integration
