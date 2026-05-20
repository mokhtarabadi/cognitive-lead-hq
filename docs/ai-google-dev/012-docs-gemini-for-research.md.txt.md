---
title: Accelerate Discovery with Gemini for Research
url: https://ai.google.dev/gemini-api/docs/gemini-for-research.md.txt
source: llms
fetched_at: 2026-04-29T11:17:27.633703893-03:00
rendered_js: false
word_count: 394
summary: Utilize Gemini API for scientific research with multimodal, long-context capabilities and academic grant support.
tags:
    - gemini-api
    - academic-research
    - multimodal-ai
    - long-context
    - ai-development
    - research-grants
category: guide
optimized: true
optimized_at: 2026-04-29T00:00:00Z
---
# Accelerate Discovery with Gemini for Research

[Get a Gemini API Key](https://aistudio.google.com/apikey)

Gemini models advance foundational research across disciplines.

| Capability | Use Case |
|---|---|
| **Analyze and control outputs** | Use `CitationMetadata` to examine responses, configure `responseSchema`, `topP`, `topK`. See [API reference](https://ai.google.dev/api/generate-content). |
| **Multimodal inputs** | Process images, audio, videos. See [Vision](https://ai.google.dev/gemini-api/docs/vision). |
| **Long-context** | 1-million-token context window on Gemini 3.0 Flash and Pro. See [Long context](https://ai.google.dev/gemini-api/docs/long-context). |
| **Grow with Google** | API and AI Studio for production. Gemini Enterprise Agent Platform for Google Cloud infrastructure. |

Google provides API credits for scientists and academic researchers via the [[012-docs-gemini-for-research#gemini-academic-program|Gemini Academic Program]].

## Get Started

### Python

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="How large is the universe?",
)

print(response.text)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});

async function main() {
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: "How large is the universe?",
  });
  console.log(response.text);
}

await main();
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "contents": [{
      "parts":[{"text": "How large is the universe?"}]
    }]
  }'
```

## Featured Research

![](https://ai.google.dev/static/site-assets/images/diyi-yang.png) "Our research investigates Gemini as a visual language model (VLM) and its agentic behaviors in diverse environments from robustness and safety perspectives. We evaluated Gemini's robustness against distractions such as pop-up windows when VLM agents perform computer tasks, and have leveraged Gemini to analyze social interaction, temporal events as well as risk factors based on video input."

[Diyi Yang - Stanford](https://cs.stanford.edu/~diyiy/)

![](https://ai.google.dev/static/site-assets/images/lerrel-pinto.png) "Gemini Pro and Flash, with their long context window, have been helping us in OK-Robot, our open-vocabulary mobile manipulation project. Gemini enables complex natural language queries and commands over the robot's 'memory': in this case, previous observations made by the robot over a long operation duration. Mahi Shafiullah and I are also using Gemini to decompose tasks into code that the robot can execute in the real world."

[Lerrel Pinto - NYU](https://www.lerrelpinto.com/)

## Gemini Academic Program

Qualified academic researchers (faculty, staff, PhD students) in [supported countries](https://ai.google.dev/gemini-api/docs/available-regions) can apply for Gemini API credits and higher rate limits.

### Research Areas of Interest

- **Evaluations and benchmarks**: Community-endorsed evaluation methods for factuality, safety, instruction following, reasoning, and planning.
- **Accelerating scientific discovery**: AI in interdisciplinary research (rare/neglected diseases, experimental biology, materials science, sustainability).
- **Embodiment and interactions**: LLM investigation in embodied AI, ambient interactions, robotics, human-computer interaction.
- **Emergent capabilities**: New agentic capabilities for reasoning and planning, expanding during inference (e.g., using Gemini Flash).
- **Multimodal interaction and understanding**: Gaps and opportunities for multimodal foundational models in analysis, reasoning, and planning.

### Eligibility

- Individuals (faculty, researchers, or equivalent) affiliated with a valid academic institution or research organization.
- API access and credits granted/removed at Google's discretion.
- Applications reviewed monthly.

### Apply

[Apply now](https://forms.ggle/HMviQstU8PxC5iCt5)