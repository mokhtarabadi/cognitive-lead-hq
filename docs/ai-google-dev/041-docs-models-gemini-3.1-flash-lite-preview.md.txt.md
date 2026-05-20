---
title: Gemini 3.1 Flash-Lite Preview
url: https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite-preview.md.txt
source: llms
fetched_at: 2026-04-29T11:16:41.627848419-03:00
rendered_js: false
word_count: 282
summary: "Gemini 3.1 Flash-Lite is the most cost-efficient multimodal model, offering the fastest performance for high-frequency, lightweight tasks."
tags:
    - multimodal-model
    - low-latency
    - high-volume
    - model-routing
    - structured-output
    - data-extraction
category: reference
optimized: true
optimized_at: '2026-04-29T14:17:12Z'
---
# Gemini 3.1 Flash-Lite Preview

The most cost-efficient multimodal model, offering the fastest performance for high-frequency, lightweight tasks. Best for high-volume agentic tasks, simple data extraction, and extremely low-latency applications where budget and speed are the primary constraints.

> [!example]
> [Try in Google AI Studio](https://aistudio.google.com/prompts/new_chat?model=gemini-3.1-flash-lite-preview)

## gemini-3.1-flash-lite-preview

| Property | Description |
|---|---|
| Model code | `gemini-3.1-flash-lite-preview` |
| Supported data types | **Inputs** Text, Image, Video, Audio, and PDF **Output** Text |
| Token limits[^1] | **Input** 1,048,576 **Output** 65,536 |
| Capabilities | Audio generation ✗ · **Batch API ✓** · **Caching ✓** · **Code execution ✓** · Computer use ✗ · **File search ✓** · **Flex inference ✓** · **Function calling ✓** · **Grounding with Google Maps ✓** · Image generation ✗ · Live API ✗ · **Priority inference ✓** · **Search grounding ✓** · **Structured outputs ✓** · **Thinking ✓** · **URL context ✓** |
| Versions | `Preview: gemini-3.1-flash-lite-preview` |
| Latest update | March 2026 |
| Knowledge cutoff | January 2025 |

[^1]: See [token documentation](https://ai.google.dev/gemini-api/docs/tokens)

## Use Cases

- **Translation** — High-volume, cost-effective translation for chat messages, reviews, and support tickets. Use system instructions to constrain output:

```python
text = "Hey, are you down to grab some pizza later? I'm starving!"

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    config={
        "system_instruction": "Only output the translated text"
    },
    contents=f"Translate the following text to German: {text}"
)

print(response.text)
```

- **Transcription** — Process audio files directly without a separate speech-to-text pipeline:

```python
from google import genai

client = genai.Client()

# Upload audio to GenAI File API
uploaded_file = client.files.upload(file='sample.mp3')

prompt = 'Generate a transcript of the audio.'

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=[prompt, uploaded_file]
)

print(response.text)
```

- **Lightweight agentic tasks and data extraction** — Entity extraction, classification, and data processing pipelines with structured JSON output:

```python
from pydantic import BaseModel, Field

prompt = "Analyze the user review and determine the aspect, sentiment score, summary quote, and return risk"
input_text = "The boots look amazing and the leather is high quality, but they run way too small. I'm sending them back."

class ReviewAnalysis(BaseModel):
    aspect: str = Field(description="The feature mentioned (e.g., Price, Comfort, Style, Shipping)")
    summary_quote: str = Field(description="The specific phrase from the review about this aspect")
    sentiment_score: int = Field(description="1 to 5 (1=worst, 5=best)")
    is_return_risk: bool = Field(description="True if the user mentions returning the item")

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=[prompt, input_text],
    config={
        "response_mime_type": "application/json",
        "response_json_schema": ReviewAnalysis.model_json_schema(),
    },
)

print(response.text)
```

- **Document processing and summarization** — Parse PDFs and return concise summaries:

```python
import httpx

# Download a sample PDF document
doc_url = "https://storage.googleapis.com/generativeai-downloads/data/med_gemini.pdf"
doc_data = httpx.get(doc_url).content

prompt = "Summarize this document"
response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
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

- **Model routing** — Use Flash-Lite as a low-latency, low-cost classifier to route queries based on task complexity. The [Gemini CLI](https://geminicli.com/docs/core/#model-fallback) uses this pattern:

```python
FLASH_MODEL = 'flash'
PRO_MODEL = 'pro'

CLASSIFIER_SYSTEM_PROMPT = f"""
You are a specialized Task Routing AI. Your sole function is to analyze the user's request and classify its complexity. Choose between `{FLASH_MODEL}` (SIMPLE) or `{PRO_MODEL}` (COMPLEX).
1.  `{FLASH_MODEL}`: A fast, efficient model for simple, well-defined tasks.
2.  `{PRO_MODEL}`: A powerful, advanced model for complex, open-ended, or multi-step tasks.

A task is COMPLEX if it meets ONE OR MORE of the following criteria:
1.  High Operational Complexity (Est. 4+ Steps/Tool Calls)
2.  Strategic Planning and Conceptual Design
3.  High Ambiguity or Large Scope
4.  Deep Debugging and Root Cause Analysis

A task is SIMPLE if it is highly specific, bounded, and has Low Operational Complexity (Est. 1-3 tool calls).
"""

user_input = "I'm getting an error 'Cannot read property 'map' of undefined' when I click the save button. Can you fix it?"

response_schema = {
    "type": "object",
    "properties": {
        "reasoning": {
            "type": "string",
            "description": "A brief, step-by-step explanation for the model choice, referencing the rubric."
        },
        "model_choice": {
            "type": "string",
            "enum": [FLASH_MODEL, PRO_MODEL]
        }
    },
    "required": ["reasoning", "model_choice"]
}

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents=user_input,
    config={
        "system_instruction": CLASSIFIER_SYSTEM_PROMPT,
        "response_mime_type": "application/json",
        "response_json_schema": response_schema
    },
)

print(response.text)
```

- **Thinking** — Enable step-by-step reasoning for improved accuracy on complex tasks:

```python
response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents="How does AI work?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="high")
    ),
)

print(response.text)
```

#multimodal-model #low-latency #high-volume #model-routing #structured-output #data-extraction