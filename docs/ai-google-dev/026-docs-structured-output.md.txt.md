---
title: Structured outputs
url: https://ai.google.dev/gemini-api/docs/structured-output.md.txt
source: llms
fetched_at: 2026-04-29T11:18:02.32613011-03:00
rendered_js: false
word_count: 513
summary: This document explains how to configure Gemini models to return structured JSON responses that strictly adhere to a defined schema using the Google GenAI SDKs.
tags:
    - structured-outputs
    - json-schema
    - data-extraction
    - gemini-api
    - pydantic
    - zod
    - generative-ai
category: guide
optimized: true
optimized_at: 2026-04-29T12:00:00Z
---
Configure Gemini models to generate responses adhering to a provided JSON Schema for predictable, type-safe results.

**Use cases:**
- **Data extraction:** Pull names, dates from text
- **Classification:** Classify text into predefined categories
- **Agentic workflows:** Generate structured inputs for tools/APIs

SDKs support [Pydantic](https://docs.pydantic.dev/latest/) (Python) and [Zod](https://zod.dev/) (JavaScript).

## Basic example

Extract data using JSON Schema types: `object`, `array`, `string`, `integer`.

### Python

```python
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional

class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient.")
    quantity: str = Field(description="Quantity of the ingredient, including units.")

class Recipe(BaseModel):
    recipe_name: str = Field(description="The name of the recipe.")
    prep_time_minutes: Optional[int] = Field(description="Optional time in minutes to prepare the recipe.")
    ingredients: List[Ingredient]
    instructions: List[str]

client = genai.Client()

prompt = """
Please extract the recipe from the following text.
The user wants to make delicious chocolate chip cookies.
They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
For the best part, they'll need 2 cups of semisweet chocolate chips.
First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
onto ungreased baking sheets and bake for 9 to 11 minutes.
"""

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Recipe.model_json_schema(),
    },
)

recipe = Recipe.model_validate_json(response.text)
print(recipe)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

const ingredientSchema = z.object({
  name: z.string().describe("Name of the ingredient."),
  quantity: z.string().describe("Quantity of the ingredient, including units."),
});

const recipeSchema = z.object({
  recipe_name: z.string().describe("The name of the recipe."),
  prep_time_minutes: z.number().optional().describe("Optional time in minutes to prepare the recipe."),
  ingredients: z.array(ingredientSchema),
  instructions: z.array(z.string()),
});

const ai = new GoogleGenAI({});

const prompt = `Please extract the recipe from the following text.
The user wants to make delicious chocolate chip cookies...`;

const response = await ai.models.generateContent({
  model: "gemini-3-flash-preview",
  contents: prompt,
  config: {
    responseMimeType: "application/json",
    responseJsonSchema: zodToJsonSchema(recipeSchema),
  },
});

const recipe = recipeSchema.parse(JSON.parse(response.text));
console.log(recipe);
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
    client, err := genai.NewClient(ctx, nil)
    if err != nil {
        log.Fatal(err)
    }

    prompt := `Please extract the recipe from the following text...`
    config := &genai.GenerateContentConfig{
        ResponseMIMEType: "application/json",
        ResponseJsonSchema: map[string]any{
            "type": "object",
            "properties": map[string]any{
                "recipe_name": map[string]any{"type": "string", "description": "The name of the recipe."},
                "prep_time_minutes": map[string]any{"type": "integer", "description": "Optional time in minutes."},
                "ingredients": map[string]any{
                    "type": "array",
                    "items": map[string]any{
                        "type": "object",
                        "properties": map[string]any{
                            "name": map[string]any{"type": "string", "description": "Name of the ingredient."},
                            "quantity": map[string]any{"type": "string", "description": "Quantity including units."},
                        },
                        "required": []string{"name", "quantity"},
                    },
                },
                "instructions": map[string]any{"type": "array", "items": map[string]any{"type": "string"}},
            },
            "required": []string{"recipe_name", "ingredients", "instructions"},
        },
    }

    result, err := client.Models.GenerateContent(ctx, "gemini-3-flash-preview", genai.Text(prompt), config)
    if err != nil {
        log.Fatal(err)
    }
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
      "contents": [{"parts": [{"text": "Please extract the recipe from the following text..."}]}],
      "generationConfig": {
        "responseMimeType": "application/json",
        "responseJsonSchema": {
          "type": "object",
          "properties": {
            "recipe_name": {"type": "string", "description": "The name of the recipe."},
            "prep_time_minutes": {"type": "integer", "description": "Optional time in minutes."},
            "ingredients": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "quantity": {"type": "string"}},
                "required": ["name", "quantity"]
              }
            },
            "instructions": {"type": "array", "items": {"type": "string"}}
          },
          "required": ["recipe_name", "ingredients", "instructions"]
        }
      }
    }'
```

**Example response:**
```json
{
  "recipe_name": "Delicious Chocolate Chip Cookies",
  "ingredients": [
    {"name": "all-purpose flour", "quantity": "2 and 1/4 cups"},
    {"name": "baking soda", "quantity": "1 teaspoon"},
    {"name": "salt", "quantity": "1 teaspoon"},
    {"name": "unsalted butter (softened)", "quantity": "1 cup"},
    {"name": "granulated sugar", "quantity": "3/4 cup"},
    {"name": "packed brown sugar", "quantity": "3/4 cup"},
    {"name": "vanilla extract", "quantity": "1 teaspoon"},
    {"name": "large eggs", "quantity": "2"},
    {"name": "semisweet chocolate chips", "quantity": "2 cups"}
  ],
  "instructions": [
    "Preheat the oven to 375°F (190°C).",
    "In a small bowl, whisk together the flour, baking soda, and salt.",
    "In a large bowl, cream together the butter, granulated sugar, and brown sugar until light and fluffy.",
    "Beat in the vanilla and eggs, one at a time.",
    "Gradually beat in the dry ingredients until just combined.",
    "Stir in the chocolate chips.",
    "Drop by rounded tablespoons onto ungreased baking sheets and bake for 9 to 11 minutes."
  ]
}
```

## Streaming

Stream structured outputs for improved perceived performance. Streamed chunks are valid partial JSON strings—concatenate for final object.

### Python

```python
from google import genai
from pydantic import BaseModel, Field
from typing import Literal

class Feedback(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str

client = genai.Client()
prompt = "The new UI is incredibly intuitive and visually appealing. Great job. Add a very long summary to test streaming!"

response_stream = client.models.generate_content_stream(
    model="gemini-3-flash-preview",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Feedback.model_json_schema(),
    },
)

for chunk in response_stream:
    print(chunk.candidates[0].content.parts[0].text)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

const ai = new GoogleGenAI({});
const prompt = "The new UI is incredibly intuitive and visually appealing. Great job!";

const feedbackSchema = z.object({
  sentiment: z.enum(["positive", "neutral", "negative"]),
  summary: z.string(),
});

const stream = await ai.models.generateContentStream({
  model: "gemini-3-flash-preview",
  contents: prompt,
  config: {
    responseMimeType: "application/json",
    responseJsonSchema: zodToJsonSchema(feedbackSchema),
  },
});

for await (const chunk of stream) {
  console.log(chunk.candidates[0].content.parts[0].text)
}
```

## Structured outputs with tools

> [!WARNING]
> **Preview:** Available only for Gemini 3 series models.

Combine with tools: Grounding with Google Search, URL Context, Code Execution, File Search, Function Calling.

### Python

```python
from google import genai
from pydantic import BaseModel, Field
from typing import List

class MatchResult(BaseModel):
    winner: str = Field(description="The name of the winner.")
    final_match_score: str = Field(description="The final match score.")
    scorers: List[str] = Field(description="The name of the scorer.")

client = genai.Client()

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="Search for all details for the latest Euro.",
    config={
        "tools": [
            {"google_search": {}},
            {"url_context": {}}
        ],
        "response_mime_type": "application/json",
        "response_json_schema": MatchResult.model_json_schema(),
    },
)

result = MatchResult.model_validate_json(response.text)
print(result)
```

### JavaScript

```javascript
import { GoogleGenAI } from "@google/genai";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

const ai = new GoogleGenAI({});

const matchSchema = z.object({
  winner: z.string().describe("The name of the winner."),
  final_match_score: z.string().describe("The final score."),
  scorers: z.array(z.string()).describe("The name of the scorer.")
});

async function run() {
  const response = await ai.models.generateContent({
    model: "gemini-3.1-pro-preview",
    contents: "Search for all details for the latest Euro.",
    config: {
      tools: [{ googleSearch: {} }, { urlContext: {} }],
      responseMimeType: "application/json",
      responseJsonSchema: zodToJsonSchema(matchSchema),
    },
  });

  const match = matchSchema.parse(JSON.parse(response.text));
  console.log(match);
}

run();
```

### REST

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H 'Content-Type: application/json' \
  -X POST \
  -d '{
    "contents": [{"parts": [{"text": "Search for all details for the latest Euro."}]}],
    "tools": [{"googleSearch": {}}, {"urlContext": {}}],
    "generationConfig": {
        "responseMimeType": "application/json",
        "responseJsonSchema": {
            "type": "object",
            "properties": {
                "winner": {"type": "string", "description": "The name of the winner."},
                "final_match_score": {"type": "string", "description": "The final score."},
                "scorers": {"type": "array", "items": {"type": "string"}, "description": "The name of the scorer."}
            },
            "required": ["winner", "final_match_score", "scorers"]
        }
    }
}'
```

## JSON schema support

Set `response_mime_type` to `application/json` and provide `response_json_schema`. Must be valid [JSON Schema](https://json-schema.org/). Model produces outputs in schema key order.

### Supported `type` values

- **`string`** — text
- **`number`** — floating-point
- **`integer`** — whole numbers
- **`boolean`** — true/false
- **`object`** — key-value pairs
- **`array`** — lists
- **`null`** — include in type array for nullable (e.g., `{"type": ["string", "null"]}`)

### Descriptive properties

- **`title`** — short description
- **`description`** — detailed description

### Type-specific properties

**For `object`:**
- **`properties`** — key-value schema definitions
- **`required`** — mandatory property names
- **`additionalProperties`** — allow/disallow extra properties (boolean or schema)

**For `string`:**
- **`enum`** — specific string set
- **`format`** — syntax (e.g., `date-time`, `date`, `time`)

**For `number`/`integer`:**
- **`enum`** — specific numeric values
- **`minimum`** / **`maximum`** — inclusive bounds

**For `array`:**
- **`items`** — schema for all items
- **`prefixItems`** — schemas for first N items (tuple-like)
- **`minItems`** / **`maxItems`** — item count bounds

## Model support

| Model | Structured Outputs |
|---|---|
| Gemini 3.1 Pro Preview | ✔️ |
| Gemini 3 Flash Preview | ✔️ |
| Gemini 2.5 Pro | ✔️ |
| Gemini 2.5 Flash | ✔️ |
| Gemini 2.5 Flash-Lite | ✔️ |
| Gemini 2.0 Flash | ✔️\* |
| Gemini 2.0 Flash-Lite | ✔️\* |

\* Gemini 2.0 requires `propertyOrdering` list in JSON input. Example in [cookbook](https://github.com/google-gemini/cookbook/blob/main/examples/Pdf_structured_outputs_on_invoices_and_forms.ipynb).

## Structured outputs vs. function calling

| Feature | Primary Use Case |
|---|---|
| **Structured Outputs** | Format the *final response* to the user. Extract data, classify, structure answers. |
| **Function Calling** | Take action *during* the conversation. Ask you to perform a task (e.g., "get weather") before final answer. |

## Best practices

- **Clear descriptions:** Use `description` field to guide model output
- **Strong typing:** Use specific types; `enum` for limited values
- **Prompt engineering:** Clearly state what to extract/classify
- **Validation:** Structured output guarantees syntactically correct JSON, not semantically correct—validate in application code
- **Error handling:** Handle schema-compliant outputs that don't meet business logic requirements

## Limitations

- **Schema subset:** Not all JSON Schema features supported; unsupported properties are ignored
- **Schema complexity:** Very large or deeply nested schemas may be rejected—simplify by shortening names, reducing nesting, limiting constraints

#structured-outputs #json-schema #data-extraction