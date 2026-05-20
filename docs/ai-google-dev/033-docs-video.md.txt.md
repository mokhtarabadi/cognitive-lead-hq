---
title: Video Generation with Veo 3.1 via Gemini API
url: https://ai.google.dev/gemini-api/docs/video.md.txt
source: llms
fetched_at: 2026-04-29T11:17:08.459072342-03:00
rendered_js: false
word_count: 2758
summary: This document provides instructions and code examples for using the Veo 3.1 model via the Gemini API to generate high-fidelity videos from text prompts.
tags:
    - veo-3.1
    - video-generation
    - gemini-api
    - ai-models
    - text-to-video
    - machine-learning
category: tutorial
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
> [!IMPORTANT]
> We have updated our [Terms of Service](https://ai.google.dev/gemini-api/terms).

> [!info]
> For video understanding (analyzing uploaded videos), see [[032-docs-video-understanding.md.txt.md|Video understanding]].

[Veo 3.1](https://deepmind.google/models/veo/) is Google's state-of-the-art model for generating high-fidelity, 8-second 720p, 1080p or 4k videos featuring stunning realism and natively generated audio via the Gemini API. See [[117-docs-pricing.md.txt.md|pricing]] for model-specific costs.

Veo 3.1 capabilities:

- **Portrait videos**: `16:9` (landscape) or `9:16` (portrait) aspect ratios.
- **Video extension**: Extend previously generated Veo videos by up to 7 seconds, up to 20 times.
- **Frame-specific generation**: Specify the first and last frames of the output video.
- **Image-based direction**: Use up to three reference images to guide generated content.

> [!tip]
> For effective text prompts, see the [[023-docs-prompting-strategies.md.txt.md|Introduction to prompt design]] and the [Veo prompt guide](#veo-prompt-guide) section below.

## Text to video generation

### Python

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

prompt = """A close up of two people staring at a cryptic drawing on a wall, torchlight flickering.
A man murmurs, 'This must be it. That's the secret code.' The woman looks at him and whispering excitedly, 'What did you find?'"""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the generated video.
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("dialogue_example.mp4")
print("Generated video saved to dialogue_example.mp4")
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const prompt = `A close up of two people staring at a cryptic drawing on a wall, torchlight flickering.
A man murmurs, 'This must be it. That's the secret code.' The woman looks at him and whispering excitedly, 'What did you find?'`;

let operation = await ai.models.generateVideos({
    model: "veo-3.1-generate-preview",
    prompt: prompt,
});

// Poll the operation status until the video is ready.
while (!operation.done) {
    console.log("Waiting for video generation to complete...")
    await new Promise((resolve) => setTimeout(resolve, 10000));
    operation = await ai.operations.getVideosOperation({
        operation: operation,
    });
}

// Download the generated video.
ai.files.download({
    file: operation.response.generatedVideos[0].video,
    downloadPath: "dialogue_example.mp4",
});
console.log(`Generated video saved to dialogue_example.mp4`);
```

### Go

```go
package main

import (
    "context"
    "log"
    "os"
    "time"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `A close up of two people staring at a cryptic drawing on a wall, torchlight flickering.
    A man murmurs, 'This must be it. That's the secret code.' The woman looks at him and whispering excitedly, 'What did you find?'`

    operation, _ := client.Models.GenerateVideos(
        ctx,
        "veo-3.1-generate-preview",
        prompt,
        nil,
        nil,
    )

    // Poll the operation status until the video is ready.
    for !operation.Done {
        log.Println("Waiting for video generation to complete...")
        time.Sleep(10 * time.Second)
        operation, _ = client.Operations.GetVideosOperation(ctx, operation, nil)
    }

    // Download the generated video.
    video := operation.Response.GeneratedVideos[0]
    client.Files.Download(ctx, video.Video, nil)
    fname := "dialogue_example.mp4"
    _ = os.WriteFile(fname, video.Video.VideoBytes, 0644)
    log.Printf("Generated video saved to %s\n", fname)
}
```

### Java

```java
import com.google.genai.Client;
import com.google.genai.types.GenerateVideosOperation;
import com.google.genai.types.Video;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

class GenerateVideoFromText {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        String prompt = "A close up of two people staring at a cryptic drawing on a wall, torchlight flickering.\n" +
            "A man murmurs, 'This must be it. That's the secret code.' The woman looks at him and whispering excitedly, 'What did you find?'";

        GenerateVideosOperation operation =
            client.models.generateVideos("veo-3.1-generate-preview", prompt, null, null);

        // Poll the operation status until the video is ready.
        while (!operation.done().isPresent() || !operation.done().get()) {
            System.out.println("Waiting for video generation to complete...");
            Thread.sleep(10000);
            operation = client.operations.getVideosOperation(operation, null);
        }

        // Download the generated video.
        Video video = operation.response().get().generatedVideos().get().get(0).video().get();
        Path path = Paths.get("dialogue_example.mp4");
        client.files.download(video, path.toString(), null);
        if (video.videoBytes().isPresent()) {
            Files.write(path, video.videoBytes().get());
            System.out.println("Generated video saved to dialogue_example.mp4");
        }
    }
}
```

### REST

```bash
# Note: This script uses jq to parse the JSON response.
# GEMINI API Base URL
BASE_URL="https://generativelanguage.googleapis.com/v1beta"

# Send request to generate video and capture the operation name into a variable.
operation_name=$(curl -s "${BASE_URL}/models/veo-3.1-generate-preview:predictLongRunning" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X "POST" \
  -d '{
    "instances": [{
        "prompt": "A close up of two people staring at a cryptic drawing on a wall, torchlight flickering. A man murmurs, \"This must be it. That's the secret code.\" The woman looks at him and whispering excitedly, \"What did you find?\""
      }
    ]
  }' | jq -r .name)

# Poll the operation status until the video is ready
while true; do
  status_response=$(curl -s -H "x-goog-api-key: $GEMINI_API_KEY" "${BASE_URL}/${operation_name}")
  is_done=$(echo "${status_response}" | jq .done)

  if [ "${is_done}" = "true" ]; then
    video_uri=$(echo "${status_response}" | jq -r '.response.generateVideoResponse.generatedSamples[0].video.uri')
    echo "Downloading video from: ${video_uri}"
    curl -L -o dialogue_example.mp4 -H "x-goog-api-key: $GEMINI_API_KEY" "${video_uri}"
    break
  fi
  sleep 10
done
```

[Video](https://www.youtube.com/watch?v=rYj2zM5s95s)

## Control the aspect ratio

Use the `aspect_ratio` parameter to choose `16:9` (landscape, default) or `9:16` (portrait).

### Python

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

prompt = """A montage of pizza making: a chef tossing and flattening the floury dough, ladling rich red tomato sauce in a spiral, sprinkling mozzarella cheese and pepperoni, and a final shot of the bubbling golden-brown pizza, upbeat electronic music with a rhythmical beat is playing, high energy professional video."""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    config=types.GenerateVideosConfig(
      aspect_ratio="9:16",
    ),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the generated video.
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("pizza_making.mp4")
print("Generated video saved to pizza_making.mp4")
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const prompt = `A montage of pizza making: a chef tossing and flattening the floury dough, ladling rich red tomato sauce in a spiral, sprinkling mozzarella cheese and pepperoni, and a final shot of the bubbling golden-brown pizza, upbeat electronic music with a rhythmical beat is playing, high energy professional video.`;

let operation = await ai.models.generateVideos({
    model: "veo-3.1-generate-preview",
    prompt: prompt,
    config: {
      aspectRatio: "9:16",
    },
});

// Poll the operation status until the video is ready.
while (!operation.done) {
    console.log("Waiting for video generation to complete...")
    await new Promise((resolve) => setTimeout(resolve, 10000));
    operation = await ai.operations.getVideosOperation({
        operation: operation,
    });
}

// Download the generated video.
ai.files.download({
    file: operation.response.generatedVideos[0].video,
    downloadPath: "pizza_making.mp4",
});
console.log(`Generated video saved to pizza_making.mp4`);
```

### Go

```go
package main

import (
    "context"
    "log"
    "os"
    "time"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `A montage of pizza making: a chef tossing and flattening the floury dough, ladling rich red tomato sauce in a spiral, sprinkling mozzarella cheese and pepperoni, and a final shot of the bubbling golden-brown pizza, upbeat electronic music with a rhythmical beat is playing, high energy professional video.`

    videoConfig := &genai.GenerateVideosConfig{
        AspectRatio: "9:16",
    }

    operation, _ := client.Models.GenerateVideos(
        ctx,
        "veo-3.1-generate-preview",
        prompt,
        nil,
        videoConfig,
    )

    // Poll the operation status until the video is ready.
    for !operation.Done {
        log.Println("Waiting for video generation to complete...")
        time.Sleep(10 * time.Second)
        operation, _ = client.Operations.GetVideosOperation(ctx, operation, nil)
    }

    // Download the generated video.
    video := operation.Response.GeneratedVideos[0]
    client.Files.Download(ctx, video.Video, nil)
    fname := "pizza_making.mp4"
    _ = os.WriteFile(fname, video.Video.VideoBytes, 0644)
    log.Printf("Generated video saved to %s\n", fname)
}
```

### REST

```bash
# Note: This script uses jq to parse the JSON response.
# GEMINI API Base URL
BASE_URL="https://generativelanguage.googleapis.com/v1beta"

# Send request to generate video and capture the operation name into a variable.
operation_name=$(curl -s "${BASE_URL}/models/veo-3.1-generate-preview:predictLongRunning" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X "POST" \
  -d '{
    "instances": [{
        "prompt": "A montage of pizza making: a chef tossing and flattening the floury dough, ladling rich red tomato sauce in a spiral, sprinkling mozzarella cheese and pepperoni, and a final shot of the bubbling golden-brown pizza, upbeat electronic music with a rhythmical beat is playing, high energy professional video."
      }
    ],
    "parameters": {
      "aspectRatio": "9:16"
    }
  }' | jq -r .name)

# Poll the operation status until the video is ready
while true; do
  status_response=$(curl -s -H "x-goog-api-key: $GEMINI_API_KEY" "${BASE_URL}/${operation_name}")
  is_done=$(echo "${status_response}" | jq .done)

  if [ "${is_done}" = "true" ]; then
    video_uri=$(echo "${status_response}" | jq -r '.response.generateVideoResponse.generatedSamples[0].video.uri')
    echo "Downloading video from: ${video_uri}"
    curl -L -o pizza_making.mp4 -H "x-goog-api-key: $GEMINI_API_KEY" "${video_uri}"
    break
  fi
  sleep 10
done
```

[Video](https://www.youtube.com/watch?v=4-kXyNJt_yg)

## Control the resolution

Veo 3.1 generates 720p (default), 1080p, or 4k videos. Higher resolution means higher latency and cost. 4k is not available for Veo 3.1 Lite. [Video extension](#extending-veo-videos) is limited to 720p.

### Python

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

prompt = """A stunning drone view of the Grand Canyon during a flamboyant sunset that highlights the canyon's colors. The drone slowly flies towards the sun then accelerates, dives and flies inside the canyon."""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    config=types.GenerateVideosConfig(
      resolution="4k",
    ),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the generated video.
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("4k_grand_canyon.mp4")
print("Generated video saved to 4k_grand_canyon.mp4")
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const prompt = `A stunning drone view of the Grand Canyon during a flamboyant sunset that highlights the canyon's colors. The drone slowly flies towards the sun then accelerates, dives and flies inside the canyon.`;

let operation = await ai.models.generateVideos({
    model: "veo-3.1-generate-preview",
    prompt: prompt,
    config: {
      resolution: "4k",
    },
});

// Poll the operation status until the video is ready.
while (!operation.done) {
    console.log("Waiting for video generation to complete...")
    await new Promise((resolve) => setTimeout(resolve, 10000));
    operation = await ai.operations.getVideosOperation({
        operation: operation,
    });
}

// Download the generated video.
ai.files.download({
    file: operation.response.generatedVideos[0].video,
    downloadPath: "4k_grand_canyon.mp4",
});
console.log(`Generated video saved to 4k_grand_canyon.mp4`);
```

### Go

```go
package main

import (
    "context"
    "log"
    "os"
    "time"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `A stunning drone view of the Grand Canyon during a flamboyant sunset that highlights the canyon's colors. The drone slowly flies towards the sun then accelerates, dives and flies inside the canyon.`

    videoConfig := &genai.GenerateVideosConfig{
        Resolution: "4k",
    }

    operation, _ := client.Models.GenerateVideos(
        ctx,
        "veo-3.1-generate-preview",
        prompt,
        nil,
        videoConfig,
    )

    // Poll the operation status until the video is ready.
    for !operation.Done {
        log.Println("Waiting for video generation to complete...")
        time.Sleep(10 * time.Second)
        operation, _ = client.Operations.GetVideosOperation(ctx, operation, nil)
    }

    // Download the generated video.
    video := operation.Response.GeneratedVideos[0]
    client.Files.Download(ctx, video.Video, nil)
    fname := "4k_grand_canyon.mp4"
    _ = os.WriteFile(fname, video.Video.VideoBytes, 0644)
    log.Printf("Generated video saved to %s\n", fname)
}
```

### REST

```bash
# Note: This script uses jq to parse the JSON response.
# GEMINI API Base URL
BASE_URL="https://generativelanguage.googleapis.com/v1beta"

# Send request to generate video and capture the operation name into a variable.
operation_name=$(curl -s "${BASE_URL}/models/veo-3.1-generate-preview:predictLongRunning" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X "POST" \
  -d '{
    "instances": [{
        "prompt": "A stunning drone view of the Grand Canyon during a flamboyant sunset that highlights the canyon'\''s colors. The drone slowly flies towards the sun then accelerates, dives and flies inside the canyon."
      }
    ],
    "parameters": {
      "resolution": "4k"
    }
  }' | jq -r .name)

# Poll the operation status until the video is ready
while true; do
  status_response=$(curl -s -H "x-goog-api-key: $GEMINI_API_KEY" "${BASE_URL}/${operation_name}")
  is_done=$(echo "${status_response}" | jq .done)

  if [ "${is_done}" = "true" ]; then
    video_uri=$(echo "${status_response}" | jq -r '.response.generateVideoResponse.generatedSamples[0].video.uri')
    echo "Downloading video from: ${video_uri}"
    curl -L -o 4k_grand_canyon.mp4 -H "x-goog-api-key: $GEMINI_API_KEY" "${video_uri}"
    break
  fi
  sleep 10
done
```

[Video](https://www.youtube.com/watch?v=SDqEif-qtyk)

## Image to video generation

Generate an image with [[045-docs-models-gemini-2.5-flash-image.md.txt.md|Nano Banana 2]] (`gemini-3.1-flash-image-preview`), then use it as the starting frame for Veo 3.1.

### Python

```python
import time
from google import genai

client = genai.Client()

prompt = "Panning wide shot of a calico kitten sleeping in the sunshine"

# Step 1: Generate an image with Nano Banana 2.
image = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=prompt,
    config={"response_modalities":['IMAGE']}
)

# Step 2: Generate video with Veo 3.1 using the image.
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    image=image.parts[0].as_image(),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3_with_image_input.mp4")
print("Generated video saved to veo3_with_image_input.mp4")
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const prompt = "Panning wide shot of a calico kitten sleeping in the sunshine";

// Step 1: Generate an image with Nano Banana 2.
const imageResponse = await ai.models.generateContent({
  model: "gemini-3.1-flash-image-preview",
  prompt: prompt,
});

// Step 2: Generate video with Veo 3.1 using the image.
let operation = await ai.models.generateVideos({
  model: "veo-3.1-generate-preview",
  prompt: prompt,
  image: {
    imageBytes: imageResponse.generatedImages[0].image.imageBytes,
    mimeType: "image/png",
  },
});

// Poll the operation status until the video is ready.
while (!operation.done) {
  console.log("Waiting for video generation to complete...")
  await new Promise((resolve) => setTimeout(resolve, 10000));
  operation = await ai.operations.getVideosOperation({
      operation: operation,
  });
}

// Download the video.
ai.files.download({
    file: operation.response.generatedVideos[0].video,
    downloadPath: "veo3_with_image_input.mp4",
});
console.log(`Generated video saved to veo3_with_image_input.mp4`);
```

### Go

```go
package main

import (
    "context"
    "log"
    "os"
    "time"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := "Panning wide shot of a calico kitten sleeping in the sunshine"

    // Step 1: Generate an image with Nano Banana 2.
    imageResponse, err := client.Models.GenerateContent(
        ctx,
        "gemini-3.1-flash-image-preview",
        prompt,
        nil, // GenerateImagesConfig
    )
    if err != nil {
        log.Fatal(err)
    }

    // Step 2: Generate video with Veo 3.1 using the image.
    operation, err := client.Models.GenerateVideos(
        ctx,
        "veo-3.1-generate-preview",
        prompt,
        imageResponse.GeneratedImages[0].Image,
        nil, // GenerateVideosConfig
    )
    if err != nil {
        log.Fatal(err)
    }

    // Poll the operation status until the video is ready.
    for !operation.Done {
        log.Println("Waiting for video generation to complete...")
        time.Sleep(10 * time.Second)
        operation, _ = client.Operations.GetVideosOperation(ctx, operation, nil)
    }

    // Download the video.
    video := operation.Response.GeneratedVideos[0]
    client.Files.Download(ctx, video.Video, nil)
    fname := "veo3_with_image_input.mp4"
    _ = os.WriteFile(fname, video.Video.VideoBytes, 0644)
    log.Printf("Generated video saved to %s\n", fname)
}
```

### Java

```java
import com.google.genai.Client;
import com.google.genai.types.GenerateVideosOperation;
import com.google.genai.types.Image;
import com.google.genai.types.Video;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

class GenerateVideoFromImage {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        String prompt = "Panning wide shot of a calico kitten sleeping in the sunshine";

        // Step 1: Generate an image with Nano Banana 2:
        Image image = Image.fromFile("path/to/your/image.png");

        // Step 2: Generate video with Veo 3.1 using the image.
        GenerateVideosOperation operation =
            client.models.generateVideos("veo-3.1-generate-preview", prompt, image, null);

        // Poll the operation status until the video is ready.
        while (!operation.done().isPresent() || !operation.done().get()) {
          System.out.println("Waiting for video generation to complete...");
          Thread.sleep(10000);
          operation = client.operations.getVideosOperation(operation, null);
        }

        // Download the video.
        Video video = operation.response().get().generatedVideos().get().get(0).video().get();
        Path path = Paths.get("veo3_with_image_input.mp4");
        client.files.download(video, path.toString(), null);
        if (video.videoBytes().isPresent()) {
            Files.write(path, video.videoBytes().get());
            System.out.println("Generated video saved to veo3_with_image_input.mp4");
        }
    }
}
```

## Using reference images

> [!note]
> This feature is available for Veo 3.1 models only.

Provide up to 3 reference images (of a person, character, or product) to preserve the subject's appearance. These images should be generated separately with [[045-docs-models-gemini-2.5-flash-image.md.txt.md|Nano Banana]].

| `` `dress_image` `` | `` `woman_image` `` | `` `glasses_image` `` |
|---|---|---|
| ![High-fashion flamingo dress with layers of pink and fuchsia feathers](https://storage.googleapis.com/generativeai-downloads/images/flamingo.png) | ![Beautiful woman with dark hair and warm brown eyes](https://storage.googleapis.com/generativeai-downloads/images/flamingo_woman.png) | ![Whimsical pink, heart-shaped sunglasses](https://storage.googleapis.com/generativeai-downloads/images/flamingo_glasses.png) |

### Python

```python
import time
from google import genai

client = genai.Client()

prompt = "The video opens with a medium, eye-level shot of a beautiful woman with dark hair and warm brown eyes. She wears a magnificent, high-fashion flamingo dress with layers of pink and fuchsia feathers, complemented by whimsical pink, heart-shaped sunglasses. She walks with serene confidence through the crystal-clear, shallow turquoise water of a sun-drenched lagoon. The camera slowly pulls back to a medium-wide shot, revealing the breathtaking scene as the dress's long train glides and floats gracefully on the water's surface behind her."

dress_reference = types.VideoGenerationReferenceImage(
    image=dress_image,
    reference_type="asset"
)
sunglasses_reference = types.VideoGenerationReferenceImage(
    image=glasses_image,
    reference_type="asset"
)
woman_reference = types.VideoGenerationReferenceImage(
    image=woman_image,
    reference_type="asset"
)

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    config=types.GenerateVideosConfig(
      reference_images=[dress_reference, sunglasses_reference, woman_reference],
    ),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3.1_with_reference_images.mp4")
print("Generated video saved to veo3.1_with_reference_images.mp4")
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const prompt = "The video opens with a medium, eye-level shot of a beautiful woman with dark hair and warm brown eyes. She wears a magnificent, high-fashion flamingo dress with layers of pink and fuchsia feathers, complemented by whimsical pink, heart-shaped sunglasses. She walks with serene confidence through the crystal-clear, shallow turquoise water of a sun-drenched lagoon.";

// dressImage, glassesImage, womanImage generated separately with Nano Banana
const dressReference = {
    image: dressImage,
    referenceType: "asset",
};
const sunglassesReference = {
    image: glassesImage,
    referenceType: "asset",
};
const womanReference = {
    image: womanImage,
    referenceType: "asset",
};

let operation = await ai.models.generateVideos({
    model: "veo-3.1-generate-preview",
    prompt: prompt,
    config: {
        referenceImages: [
            dressReference,
            sunglassesReference,
            womanReference,
        ],
    },
});

// Poll the operation status until the video is ready.
while (!operation.done) {
    console.log("Waiting for video generation to complete...")
    await new Promise((resolve) => setTimeout(resolve, 10000));
    operation = await ai.operations.getVideosOperation({
        operation: operation,
    });
}

// Download the video.
ai.files.download({
    file: operation.response.generatedVideos[0].video,
    downloadPath: "veo3.1_with_reference_images.mp4",
});
console.log(`Generated video saved to veo3.1_with_reference_images.mp4`);
```

### Go

```go
package main

import (
    "context"
    "log"
    "os"
    "time"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `The video opens with a medium, eye-level shot of a beautiful woman with dark hair and warm brown eyes. She wears a magnificent, high-fashion flamingo dress with layers of pink and fuchsia feathers, complemented by whimsical pink, heart-shaped sunglasses. She walks with serene confidence through the crystal-clear, shallow turquoise water of a sun-drenched lagoon.`

    // dressImage, glassesImage, womanImage generated separately with Nano Banana
    var dressImage, glassesImage, womanImage *genai.Image

    dressReference := &genai.VideoGenerationReferenceImage{
        Image: dressImage,
        ReferenceType: "asset",
    }
    sunglassesReference := &genai.VideoGenerationReferenceImage{
        Image: glassesImage,
        ReferenceType: "asset",
    }
    womanReference := &genai.VideoGenerationReferenceImage{
        Image: womanImage,
        ReferenceType: "asset",
    }

    operation, _ := client.Models.GenerateVideos(
        ctx,
        "veo-3.1-generate-preview",
        prompt,
        nil,
        &genai.GenerateVideosConfig{
            ReferenceImages: []*genai.VideoGenerationReferenceImage{
                dressReference,
                sunglassesReference,
                womanReference,
            },
        },
    )

    // Poll the operation status until the video is ready.
    for !operation.Done {
        log.Println("Waiting for video generation to complete...")
        time.Sleep(10 * time.Second)
        operation, _ = client.Operations.GetVideosOperation(ctx, operation, nil)
    }

    // Download the video.
    video := operation.Response.GeneratedVideos[0]
    client.Files.Download(ctx, video.Video, nil)
    fname := "veo3.1_with_reference_images.mp4"
    _ = os.WriteFile(fname, video.Video.VideoBytes, 0644)
    log.Printf("Generated video saved to %s\n", fname)
}
```

### REST

```bash
# Note: This script uses jq to parse the JSON response.
# It assumes dress_image_base64, glasses_image_base64, and woman_image_base64
# contain base64-encoded image data.

# GEMINI API Base URL
BASE_URL="https://generativelanguage.googleapis.com/v1beta"

operation_name=$(curl -s "${BASE_URL}/models/veo-3.1-generate-preview:predictLongRunning" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X "POST" \
  -d '{
    "instances": [{
      "prompt": "The video opens with a medium, eye-level shot of a beautiful woman with dark hair and warm brown eyes.",
      "referenceImages": [
        {"image": {"inlineData": {"mimeType": "image/png", "data": "'"$dress_image_base64"'"}}, "referenceType": "asset"},
        {"image": {"inlineData": {"mimeType": "image/png", "data": "'"$glasses_image_base64"'"}}, "referenceType": "asset"},
        {"image": {"inlineData": {"mimeType": "image/png", "data": "'"$woman_image_base64"'"}}, "referenceType": "asset"}
      ]
    }],
  }' | jq -r .name)

# Poll the operation status until the video is ready
while true; do
  status_response=$(curl -s -H "x-goog-api-key: $GEMINI_API_KEY" "${BASE_URL}/${operation_name}")
  is_done=$(echo "${status_response}" | jq .done)

  if [ "${is_done}" = "true" ]; then
    video_uri=$(echo "${status_response}" | jq -r '.response.generateVideoResponse.generatedSamples[0].video.uri')
    echo "Downloading video from: ${video_uri}"
    curl -L -o veo3.1_with_reference_images.mp4 -H "x-goog-api-key: $GEMINI_API_KEY" "${video_uri}"
    break
  fi
  sleep 10
done
```

[Video](https://www.youtube.com/watch?v=Hvo89S-lgAo)

## Using first and last frames

> [!note]
> This feature is available for Veo 3.1 models only.

Create videos using interpolation by specifying the first and last frames. The `image` parameter is the starting frame; `last_frame` in the config is the ending frame.

### Python

```python
import time
from google import genai

client = genai.Client()

prompt = "A cinematic, haunting video. A ghostly woman with long white hair and a flowing dress swings gently on a rope swing beneath a massive, gnarled tree in a foggy, moonlit clearing. The fog thickens and swirls around her, and she slowly fades away, vanishing completely."

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    image=first_image,  # The starting frame
    config=types.GenerateVideosConfig(
      last_frame=last_image  # The ending frame
    ),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3.1_with_interpolation.mp4")
print("Generated video saved to veo3.1_with_interpolation.mp4")
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const prompt = "A cinematic, haunting video. A ghostly woman with long white hair and a flowing dress swings gently on a rope swing beneath a massive, gnarled tree in a foggy, moonlit clearing.";

// firstImage and lastImage generated separately with Nano Banana
let operation = await ai.models.generateVideos({
    model: "veo-3.1-generate-preview",
    prompt: prompt,
    image: firstImage,
    config: {
      lastFrame: lastImage,
    },
});

// Poll the operation status until the video is ready.
while (!operation.done) {
    console.log("Waiting for video generation to complete...")
    await new Promise((resolve) => setTimeout(resolve, 10000));
    operation = await ai.operations.getVideosOperation({
        operation: operation,
    });
}

// Download the video.
ai.files.download({
    file: operation.response.generatedVideos[0].video,
    downloadPath: "veo3.1_with_interpolation.mp4",
});
console.log(`Generated video saved to veo3.1_with_interpolation.mp4`);
```

### Go

```go
package main

import (
    "context"
    "log"
    "os"
    "time"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `A cinematic, haunting video. A ghostly woman with long white hair and a flowing dress swings gently on a rope swing beneath a massive, gnarled tree in a foggy, moonlit clearing.`

    var firstImage, lastImage *genai.Image

    operation, _ := client.Models.GenerateVideos(
        ctx,
        "veo-3.1-generate-preview",
        prompt,
        firstImage,
        &genai.GenerateVideosConfig{
            LastFrame: lastImage,
        },
    )

    // Poll the operation status until the video is ready.
    for !operation.Done {
        log.Println("Waiting for video generation to complete...")
        time.Sleep(10 * time.Second)
        operation, _ = client.Operations.GetVideosOperation(ctx, operation, nil)
    }

    // Download the video.
    video := operation.Response.GeneratedVideos[0]
    client.Files.Download(ctx, video.Video, nil)
    fname := "veo3.1_with_interpolation.mp4"
    _ = os.WriteFile(fname, video.Video.VideoBytes, 0644)
    log.Printf("Generated video saved to %s\n", fname)
}
```

### REST

```bash
# Note: This script uses jq to parse the JSON response.
# It assumes first_image_base64 and last_image_base64
# contain base64-encoded image data.

BASE_URL="https://generativelanguage.googleapis.com/v1beta"

operation_name=$(curl -s "${BASE_URL}/models/veo-3.1-generate-preview:predictLongRunning" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X "POST" \
  -d '{
    "instances": [{
      "prompt": "A cinematic, haunting video. A ghostly woman with long white hair and a flowing dress swings gently on a rope swing beneath a massive, gnarled tree in a foggy, moonlit clearing.",
      "image": {"inlineData": {"mimeType": "image/png", "data": "'"$first_image_base64"'"}},
      "lastFrame": {"inlineData": {"mimeType": "image/png", "data": "'"$last_image_base64"'"}}
    }],
  }' | jq -r .name)

# Poll the operation status until the video is ready
while true; do
  status_response=$(curl -s -H "x-goog-api-key: $GEMINI_API_KEY" "${BASE_URL}/${operation_name}")
  is_done=$(echo "${status_response}" | jq .done)

  if [ "${is_done}" = "true" ]; then
    video_uri=$(echo "${status_response}" | jq -r '.response.generateVideoResponse.generatedSamples[0].video.uri')
    echo "Downloading video from: ${video_uri}"
    curl -L -o veo3.1_with_interpolation.mp4 -H "x-goog-api-key: $GEMINI_API_KEY" "${video_uri}"
    break
  fi
  sleep 10
done
```

| `` `first_image` `` | `` `last_image` `` | *veo3.1_with_interpolation.mp4* |
|---|---|---|
| ![A ghostly woman with long white hair and a flowing dress swings gently on a rope swing](https://storage.googleapis.com/generativeai-downloads/images/ghost_girl.png) | ![The ghostly woman vanishes from the swing](https://storage.googleapis.com/generativeai-downloads/images/empty_tree.png) | ![A cinematic, haunting video of an eerie woman disappearing from a swing in the mist](https://storage.googleapis.com/generativeai-downloads/images/creepy_swing.gif) |

## Extending Veo videos

> [!note]
> This feature is available for Veo 3.1 & Veo 3.1 Fast only, not Veo 3.1 Lite.

Extend a previously generated Veo video by 7 seconds (up to 20 times), producing a combined video up to 148 seconds. The input video must be Veo-generated, up to 141 seconds long, at 9:16 or 16:9 aspect ratio and 720p resolution. Extended videos are treated as newly generated and stored for 2 days.

For prompt guidance, see the [Veo prompt guide](#prompting-for-extension).

| Prompt | Output: `butterfly_video` |
|---|---|
| An origami butterfly flaps its wings and flies out of the french doors into the garden. | ![Origami butterfly flaps its wings and flies out of the french doors into the garden.](https://storage.googleapis.com/generativeai-downloads/images/Butterfly_original.gif) |

### Python

```python
import time
from google import genai

client = genai.Client()

prompt = "Track the butterfly into the garden as it lands on an orange origami flower. A fluffy white puppy runs up and gently pats the flower."

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=operation.response.generated_videos[0].video,  # Must be from a previous generation
    prompt=prompt,
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        resolution="720p"
    ),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3.1_extension.mp4")
print("Generated video saved to veo3.1_extension.mp4")
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

const prompt = "Track the butterfly into the garden as it lands on an orange origami flower. A fluffy white puppy runs up and gently pats the flower.";

// butterflyVideo must be a video from a previous generation
let operation = await ai.models.generateVideos({
    model: "veo-3.1-generate-preview",
    video: butterflyVideo,
    prompt: prompt,
    config: {
        numberOfVideos: 1,
        resolution: "720p",
    },
});

// Poll the operation status until the video is ready.
while (!operation.done) {
    console.log("Waiting for video generation to complete...")
    await new Promise((resolve) => setTimeout(resolve, 10000));
    operation = await ai.operations.getVideosOperation({
        operation: operation,
    });
}

// Download the video.
ai.files.download({
    file: operation.response.generatedVideos[0].video,
    downloadPath: "veo3.1_extension.mp4",
});
console.log(`Generated video saved to veo3.1_extension.mp4`);
```

### Go

```go
package main

import (
    "context"
    "log"
    "os"
    "time"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `Track the butterfly into the garden as it lands on an orange origami flower. A fluffy white puppy runs up and gently pats the flower.`

    var butterflyVideo *genai.Video

    operation, _ := client.Models.GenerateVideos(
        ctx,
        "veo-3.1-generate-preview",
        prompt,
        nil,
        butterflyVideo,
        &genai.GenerateVideosConfig{
            NumberOfVideos: 1,
            Resolution:     "720p",
        },
    )

    // Poll the operation status until the video is ready.
    for !operation.Done {
        log.Println("Waiting for video generation to complete...")
        time.Sleep(10 * time.Second)
        operation, _ = client.Operations.GetVideosOperation(ctx, operation, nil)
    }

    // Download the video.
    video := operation.Response.GeneratedVideos[0]
    client.Files.Download(ctx, video.Video, nil)
    fname := "veo3.1_extension.mp4"
    _ = os.WriteFile(fname, video.Video.VideoBytes, 0644)
    log.Printf("Generated video saved to %s\n", fname)
}
```

### REST

```bash
# Note: This script uses jq to parse the JSON response.
# It assumes butterfly_video_base64 contains base64-encoded
# video data from a previous generation.

BASE_URL="https://generativelanguage.googleapis.com/v1beta"

operation_name=$(curl -s "${BASE_URL}/models/veo-3.1-generate-preview:predictLongRunning" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X "POST" \
  -d '{
    "instances": [{
      "prompt": "Track the butterfly into the garden as it lands on an orange origami flower. A fluffy white puppy runs up and gently pats the flower.",
      "video": {"inlineData": {"mimeType": "video/mp4", "data": "'"$butterfly_video_base64"'"}}
    }],
    "parameters": {
      "numberOfVideos": 1,
      "resolution": "720p"
    }
  }' | jq -r .name)

# Poll the operation status until the video is ready
while true; do
  status_response=$(curl -s -H "x-goog-api-key: $GEMINI_API_KEY" "${BASE_URL}/${operation_name}")
  is_done=$(echo "${status_response}" | jq .done)

  if [ "${is_done}" = "true" ]; then
    video_uri=$(echo "${status_response}" | jq -r '.response.generateVideoResponse.generatedSamples[0].video.uri')
    echo "Downloading video from: ${video_uri}"
    curl -L -o veo3.1_extension.mp4 -H "x-goog-api-key: $GEMINI_API_KEY" "${video_uri}"
    break
  fi
  sleep 10
done
```

[Video](https://www.youtube.com/watch?v=eSF7-_B4ciA)

For prompt writing guidance, see the [Veo prompt guide](#extend-prompt).

## Handling asynchronous operations

Video generation is a long-running operation. Poll `operation.done` until `true`, then access `operation.response`.

### Python

```python
import time
from google import genai
from google.genai import types

client = genai.Client()

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="A cinematic shot of a majestic lion in the savannah.",
)

# Alternatively, reconstruct from operation.name.
operation = types.GenerateVideosOperation(name=operation.name)

while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)

# Once done, the result is in operation.response.
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

let operation = await ai.models.generateVideos({
    model: "veo-3.1-generate-preview",
    prompt: "A cinematic shot of a majestic lion in the savannah.",
});

while (!operation.done) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    operation = await ai.operations.getVideosOperation({ operation });
}

// Once done, the result is in operation.response.
```

### Go

```go
package main

import (
    "context"
    "log"
    "time"

    "google.golang.org/genai"
)

func main() {
    ctx := context.Background()
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    operation, _ := client.Models.GenerateVideos(
        ctx,
        "veo-3.1-generate-preview",
        "A cinematic shot of a majestic lion in the savannah.",
        nil,
        nil,
    )

    for !operation.Done {
        time.Sleep(10 * time.Second)
        operation, _ = client.Operations.GetVideosOperation(ctx, operation, nil)
    }

    // Once done, the result is in operation.Response.
}
```

### Java

```java
import com.google.genai.Client;
import com.google.genai.types.GenerateVideosOperation;
import com.google.genai.types.Video;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

class HandleAsync {
    public static void main(String[] args) throws Exception {
        Client client = new Client();

        GenerateVideosOperation operation =
            client.models.generateVideos(
                "veo-3.1-generate-preview",
                "A cinematic shot of a majestic lion in the savannah.",
                null,
                null);

        while (!operation.done().isPresent() || !operation.done().get()) {
            Thread.sleep(10000);
            operation = client.operations.getVideosOperation(operation, null);
        }

        Video video = operation.response().get().generatedVideos().get().get(0).video().get();
        Path path = Paths.get("async_example.mp4");
        client.files.download(video, path.toString(), null);
        if (video.videoBytes().isPresent()) {
            Files.write(path, video.videoBytes().get());
            System.out.println("Generated video saved to async_example.mp4");
        }
    }
}
```

### REST

```bash
BASE_URL="https://generativelanguage.googleapis.com/v1beta"

operation_name=$(curl -s "${BASE_URL}/models/veo-3.1-generate-preview:predictLongRunning" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -X "POST" \
  -d '{
    "instances": [{"prompt": "A cinematic shot of a majestic lion in the savannah."}]
  }' | jq -r .name)

while true; do
  status_response=$(curl -s -H "x-goog-api-key: $GEMINI_API_KEY" "${BASE_URL}/${operation_name}")
  is_done=$(echo "${status_response}" | jq .done)

  if [ "${is_done}" = "true" ]; then
    echo "Video generation complete."
    break
  fi
  echo "Waiting for video generation to complete..."
  sleep 10
done
```

## Veo API parameters and specifications

| Parameter | Veo 3.1 & Veo 3.1 Fast | Veo 3.1 Lite | Veo 3 & Veo 3 Fast | Veo 2 |
|---|---|---|---|---|
| `prompt` (text description; supports audio cues) | `string` | `string` | `string` | `string` |
| `image` (initial image to animate) | `Image` | `Image` | `Image` | `Image` |
| `lastFrame` (final image for interpolation; requires `image`) | `Image` | `Image` | `Image` | `Image` |
| `referenceImages` (up to 3 style/content references) | `VideoGenerationReferenceImage` | n/a | n/a | n/a |
| `video` (video to extend) | `Video` (from previous generation) | n/a | n/a | n/a |
| `aspectRatio` | `"16:9"` (default), `"9:16"` | `"16:9"` (default), `"9:16"` | `"16:9"` (default), `"9:16"` | `"16:9"` (default), `"9:16"` |
| `durationSeconds` | `"4"`, `"6"`, `"8"` (*must be `"8"` for extension, reference images, 1080p, or 4k*) | `"4"`, `"6"`, `"8"` (*must be `"8"` for reference images or 1080p*) | `"4"`, `"6"`, `"8"` (*must be `"8"` for extension, reference images, 1080p, or 4k*) | `"5"`, `"6"`, `"8"` |
| `personGeneration` (region restrictions apply) | T2V & Extension: `"allow_all"` only. I2V, Interpolation, & Reference images: `"allow_adult"` only | T2V: `"allow_all"` only. I2V, Interpolation, & Reference images: `"allow_adult"` only | T2V: `"allow_all"` only. I2V: `"allow_adult"` only | T2V: `"allow_all"`, `"allow_adult"`, `"dont_allow"`. I2V: `"allow_adult"`, `"dont_allow"` |
| `resolution` | `"720p"` (default), `"1080p"` (8s only), `"4k"` (8s only). Extension: `"720p"` only | `"720p"` (default), `"1080p"` (8s only) | `"720p"` (default), `"1080p"` (16:9 only), `"4k"` (16:9 only) | Unsupported |

> [!note]
> The `seed` parameter is available for Veo 3 models. It doesn't guarantee determinism but slightly improves it.

## Model features

| Feature | Veo 3.1 & Veo 3.1 Fast | Veo 3.1 Lite | Veo 3 & Veo 3 Fast | Veo 2 |
|---|---|---|---|---|
| **Audio** (natively generated) | ✔️ Always on | ✔️ Always on | ✔️ Always on | ❌ Silent only |
| **Input modalities** | T2V, I2V, V2V | T2V, I2V | T2V, I2V | T2V, I2V |
| **Resolution** | 720p, 1080p (8s), 4k (8s). Extension: 720p only | 720p, 1080p (8s) | 720p & 1080p (16:9 only) | 720p |
| **Frame rate** | 24fps | 24fps | 24fps | 24fps |
| **Duration** | 4s, 6s, 8s (*8s only for 1080p, 4k, or reference images*) | 4s, 6s, 8s (*8s only for 1080p or reference images*) | 8s | 5–8s |
| **Videos per request** | 1 | 1 | 1 | 1 or 2 |
| **Status** | [Preview](https://ai.google.dev/gemini-api/docs/models#preview) | [Preview](https://ai.google.dev/gemini-api/docs/models#preview) | [Stable](https://ai.google.dev/gemini-api/docs/models#stable) | [Stable](https://ai.google.dev/gemini-api/docs/models#latest-stable) |

## Limitations

- **Request latency**: Min 11 seconds; Max 6 minutes during peak hours.
- **Regional limitations**: In EU, UK, CH, and MENA locations:
  - Veo 3 and 3.1: `allow_adult` only for `personGeneration`.
  - Veo 2: `dont_allow` and `allow_adult` only. Default is `dont_allow`.
- **Video retention**: Generated videos are stored for 2 days. Download within that window. Extended videos reset the storage timer.
- **Watermarking**: Videos are watermarked using [SynthID](https://deepmind.google/technologies/synthid/). Verify at the [SynthID verification platform](https://deepmind.google/science/synthid/).
- **Safety**: Videos pass through safety filters and memorization checks for privacy, copyright, and bias mitigation.
- **Audio errors**: Veo 3.1 may block generation due to audio safety filters. You are not charged for blocked videos.

## Veo prompt guide

### Safety filters

Prompts violating [terms and guidelines](https://ai.google.dev/gemini-api/docs/usage-policies#abuse-monitoring) are blocked.

### Prompt writing basics

Include these elements in your prompt:

- **Subject**: Object, person, animal, or scenery (e.g., *cityscape*, *puppies*).
- **Action**: What the subject is doing (e.g., *walking*, *running*).
- **Style**: Film style keywords (e.g., *sci-fi*, *horror film*, *film noir*, *cartoon*).
- **Camera positioning and motion** *(optional)*: Terms like *aerial view*, *dolly shot*, *worms eye*.
- **Composition** *(optional)*: *wide shot*, *close-up*, *two-shot*.
- **Focus and lens effects** *(optional)*: *shallow focus*, *wide-angle lens*.
- **Ambiance** *(optional)*: *blue tones*, *night*, *warm tones*.

> [!tip]
> Use adjectives and adverbs for descriptive language. Specify facial details as a focus (e.g., include *portrait*).

### Prompting for audio

Provide audio cues in the prompt:

- **Dialogue**: Use quotes (e.g., `"This must be the key," he murmured.`)
- **Sound Effects**: Explicitly describe sounds (e.g., *tires screeching loudly*)
- **Ambient Noise**: Describe the soundscape (e.g., *A faint, eerie hum in the background*)

| **Prompt** | **Generated output** |
|---|---|
| **Dialogue and ambience** A wide shot of a misty Pacific Northwest forest. Two exhausted hikers, a man and a woman, push through ferns when the man stops abruptly, staring at a tree. Close-up: Fresh, deep claw marks gouged into the tree's bark. Man: (Hand on his hunting knife) "That's no ordinary bear." Woman: (Voice tight with fear, scanning the woods) "Then what is it?" A rough bark, snapping twigs, footsteps on the damp earth. | ![Two people in the woods encounter signs of a bear.](https://storage.googleapis.com/generativeai-downloads/images/Scary_Bear.gif) |
| **Dialogue** Paper Cut-Out Animation. New Librarian: "Where do you keep the forbidden books?" Old Curator: "We don't. They keep us." | ![Animated librarians discussing forbidden books](https://storage.googleapis.com/generativeai-downloads/images/Library.gif) |

### Prompting with reference images

Use [[045-docs-models-gemini-2.5-flash-image.md.txt.md|Nano Banana]]-generated images as the initial frame or as style/content references.

| **Prompt** | **Generated output** |
|---|---|
| **Input image (Nano Banana)** A hyperrealistic macro photo of tiny miniature surfers riding ocean waves inside a rustic stone bathroom sink. A vintage brass faucet is running, creating the perpetual surf. | ![Tiny surfers in a bathroom sink.](https://storage.googleapis.com/generativeai-downloads/images/Sink_Surfers.png) |
| **Output video (Veo 3.1)** A surreal cinematic macro video. Tiny surfers ride perpetual waves inside a stone bathroom sink. A running vintage brass faucet generates the endless surf. | ![Tiny surfers in a bathroom sink gif.](https://storage.googleapis.com/generativeai-downloads/images/sink_surfers.gif) |

| **Prompt** | **Generated output** |
|---|---|
| **Reference image (Nano Banana)** A deep sea angler fish lurks in the dark, teeth bared, bait glowing. | ![An angler fish](https://storage.googleapis.com/generativeai-downloads/images/angler_fish.png) |
| **Reference image (Nano Banana)** A pink child's princess costume with a wand and tiara. | ![A princess costume](https://storage.googleapis.com/generativeai-downloads/images/princess_dress.png) |
| **Output video (Veo 3.1)** A silly cartoon version of the fish wearing the costume, swimming and waving the wand. | ![An angler fish wearing a princess costume](https://storage.googleapis.com/generativeai-downloads/images/angler_princess.gif) |

| **Prompt** | **Generated output** |
|---|---|
| **First image (Nano Banana)** A photorealistic front image of a ginger cat driving a red convertible racing car on the French Riviera. | ![A ginger cat driving a red convertible](https://storage.googleapis.com/generativeai-downloads/images/ginger_race_cat.jpeg) |
| **Last image (Nano Banana)** The car takes off from a cliff. | ![A ginger cat driving off a cliff](https://storage.googleapis.com/generativeai-downloads/images/race_cat_cliff.jpeg) |
| **Output video (Veo 3.1)** Optional | ![A cat drives off a cliff and takes off](https://storage.googleapis.com/generativeai-downloads/images/race_cat_cliff.gif) |

### Prompting for extension

Extend the final 1 second of the original video to continue the action. Voice cannot be effectively extended if absent from the last 1 second.

| **Prompt** | **Generated output** |
|---|---|
| **Input video (Veo 3.1)** The paraglider takes off from the top of the mountain and starts gliding down the flower-covered valleys. | ![A paraglider takes off](https://storage.googleapis.com/generativeai-downloads/images/Paraglider.gif) |
| **Extend with** Track the butterfly into the garden as it lands on an orange origami flower. | ![Paraglider descends](https://storage.googleapis.com/generativeai-downloads/images/Paraglider_Extend.gif) |

### Example prompts and output

#### Icicles

| **Prompt** | **Generated output** |
|---|---|
| Close up shot (composition) of melting icicles (subject) on a frozen rock wall (context) with cool blue tones (ambiance), zoomed in (camera motion) maintaining close-up detail of water drips (action). | ![Dripping icicles with a blue background.](https://storage.googleapis.com/generativeai-downloads/images/Icicles.gif) |

#### Man on the phone

| **Prompt** | **Generated output** |
|---|---|
| **Less detail** A close up of a desperate man in a green trench coat making a call on a rotary-style wall phone with a green neon light. | ![Man talking on the phone](https://storage.googleapis.com/generativeai-downloads/images/Desperate_Man.gif) |
| **More detail** A close-up cinematic shot follows a desperate man in a weathered green trench coat as he dials a rotary phone mounted on a gritty brick wall, bathed in the eerie glow of a green neon sign. The camera dollies in, revealing the tension in his jaw and the desperation etched on his face. Shallow depth of field focuses on his furrowed brow and the black rotary phone, blurring the background into a sea of neon colors and indistinct shadows. | ![Man talking on the phone](https://storage.googleapis.com/generativeai-downloads/images/detail_call.gif) |

#### Snow leopard

| **Prompt** | **Generated output** |
|---|---|
| **Simple** A cute creature with snow leopard-like fur is walking in winter forest, 3D cartoon style. | ![Snow leopard is lethargic](https://storage.googleapis.com/generativeai-downloads/images/snowleopard.gif) |
| **Detailed** A short 3D animated scene in a joyful cartoon style. A cute creature with snow leopard-like fur, large expressive eyes, and a friendly rounded form happily prances through a whimsical winter forest with rounded snow-covered trees, gentle falling snowflakes, and warm sunlight filtering through branches. The creature's bouncy movements and wide smile convey pure delight. | ![Snow leopard is running faster](https://storage.googleapis.com/generativeai-downloads/images/snow-run.gif) |

### Examples by writing elements

#### Subject and context

| **Prompt** | **Generated output** |
|---|---|
| An architectural rendering of a white concrete apartment building with flowing organic shapes blending with lush greenery | ![White concrete apartment building](https://storage.googleapis.com/generativeai-downloads/images/architecture.gif) |
| A satellite floating through outer space with the moon and some stars in the background. | ![Satellite floating in the atmosphere](https://storage.googleapis.com/generativeai-downloads/images/satellite.gif) |

#### Action

| **Prompt** | **Generated output** |
|---|---|
| A wide shot of a woman walking along the beach, looking content and relaxed towards the horizon at sunset. | ![Sunset at the beach](https://storage.googleapis.com/generativeai-downloads/images/sunset.gif) |

#### Style

| **Prompt** | **Generated output** |
|---|---|
| Film noir style, man and woman walk on the street, mystery, cinematic, black and white. | ![Film noir style](https://storage.googleapis.com/generativeai-downloads/images/noir.gif) |

#### Camera motion and composition

| **Prompt** | **Generated output** |
|---|---|
| A POV shot from a vintage car driving in the rain, Canada at night, cinematic. | ![POV from a vintage car](https://storage.googleapis.com/generativeai-downloads/images/car-pov.gif) |
| Extreme close-up of an eye with city reflected in it. | ![An eye with city reflected](https://storage.googleapis.com/generativeai-downloads/images/eye.gif) |

#### Ambiance

| **Prompt** | **Generated output** |
|---|---|
| A close-up of a girl holding an adorable golden retriever puppy in the park, sunlight. | ![A puppy in a young girl's arms](https://ai.google.dev/static/gemini-api/docs/video/images/ambiance_puppy.gif) |
| Cinematic close-up shot of a sad woman riding a bus in the rain, cool blue tones, sad mood. | ![A sad woman on a bus](https://ai.google.dev/static/gemini-api/docs/video/images/ambiance_sad.gif) |

### Aspect ratios

| **Prompt** | **Generated output** |
|---|---|
| **Widescreen (16:9)** A tracking drone view of a man driving a red convertible car in Palm Springs, 1970s, warm sunlight, long shadows. | ![A man driving in Palm Springs](https://ai.google.dev/static/gemini-api/docs/video/images/widescreen_palm_springs.gif) |
| **Portrait (9:16)** A smooth motion video of a majestic Hawaiian waterfall within a lush rainforest. Focus on realistic water flow, detailed foliage, and natural lighting. Capture the rushing water, misty atmosphere, and dappled sunlight filtering through the dense canopy. | ![A Hawaiian waterfall](https://ai.google.dev/static/gemini-api/docs/video/images/waterfall.gif) |

## Model versions

See [[117-docs-pricing.md.txt.md|pricing]] and [Rate limits](https://aistudio.google.com/rate-limit) for model-specific usage details.

### Veo 3.1 Preview

| Property | Value |
|---|---|
| Model code | `veo-3.1-generate-preview` |
| Supported data types | **Input** Text, Image **Output** Video with audio |
| Limits | **Text input** 1,024 tokens **Output video** 1 |
| Latest update | January 2026 |

### Veo 3.1 Fast Preview

| Property | Value |
|---|---|
| Model code | `veo-3.1-fast-generate-preview` |
| Supported data types | **Input** Text, Image **Output** Video with audio |
| Limits | **Text input** 1,024 tokens **Output video** 1 |
| Latest update | January 2026 |

### Veo 3.1 Lite Preview

| Property | Value |
|---|---|
| Model code | `veo-3.1-lite-generate-preview` |
| Supported data types | **Input** Text, image **Output** Video with audio |
| Limits | **Text input** 1,024 tokens **Output video** 1 |
| Latest update | March 2026 |

### Veo 3

| Property | Value |
|---|---|
| Model code | `veo-3.0-generate-001` |
| Supported data types | **Input** Text, Image **Output** Video with audio |
| Limits | **Text input** 1,024 tokens **Output video** 1 |
| Latest update | July 2025 |

### Veo 3 Fast

| Property | Value |
|---|---|
| Model code | `veo-3.0-fast-generate-001` |
| Supported data types | **Input** Text, Image **Output** Video with audio |
| Limits | **Text input** 1,024 tokens **Output video** 1 |
| Latest update | July 2025 |

### Veo 2

| Property | Value |
|---|---|
| Model code | `veo-2.0-generate-001` |
| Supported data types | **Input** Text, image **Output** Video |
| Limits | **Text input** N/A **Image input** Any resolution/aspect ratio up to 20MB **Output video** Up to 2 |
| Latest update | April 2025 |

Veo Fast versions optimize for speed and business use cases (e.g., programmatic ad generation, A/B testing of creative concepts, or social media content production) while maintaining audio and visual quality.

## What's next

- Experiment in the [Veo Quickstart Colab](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Veo.ipynb) or the [Veo 3.1 applet](https://aistudio.google.com/apps/bundled/veo_studio).
- Learn prompting best practices with [[023-docs-prompting-strategies.md.txt.md|Introduction to prompt design]].

#video-generation #gemini-api #veo-3.1 #text-to-video
