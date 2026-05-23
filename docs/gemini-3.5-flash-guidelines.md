# Gemini 3.5 Flash — Prompting & Integration Guidelines

## Core Prompting Guidelines

- Be **precise, direct, and structured** in every instruction. Avoid ambiguous or open-ended phrasing.
- Use **XML-style tags consistently** for all structural delimiters (e.g., `<role>`, `<context>`, `<task>`). Do not mix markdown headings with XML tags for the same purpose.
- **Control output verbosity explicitly**: instruct the model on expected response length and format (e.g., "Answer in 1-3 sentences", "Output only the JSON object", "Be highly analytical and concise").
- Gemini 3.5 Flash excels at speed; optimize for **low-latency, high-precision** interactions by reducing prompt bloat and unnecessary context.

## Parameter Updates

- `temperature`, `top_p`, and `top_k` are **no longer recommended** for Gemini 3.x models. The default values are optimal and should not be overridden. Do not set these parameters in API calls.
- Use `thinking_level` instead of `thinking_budget`. Accepted values:
  - `minimal` — for straightforward, deterministic tasks
  - `low` — for simple reasoning
  - `medium` — for standard reasoning tasks
  - `high` — for complex multi-step reasoning
- The `thinking_budget` parameter is deprecated and should not be used.

## Strict Function Response Matching

- Every `FunctionResponse` **must** contain a matching `id` and `name` from the corresponding `FunctionCall`.
- The count of `FunctionResponse` entries must match the count of `FunctionCall` entries exactly.
- **Mismatched responses will cause empty outputs** with `finish_reason: STOP`. The API returns no useful data and no error message, making this a silent failure mode.
- Validate that each response `id` corresponds to a call `id` before sending the batch.

## Multimodal and Inline Instructions

- Place **multimodal content** (images, audio, video) *inside* the `FunctionResponse` payload, not in the system instruction or user message.
- Append **inline instructions** to the end of the response text, separated by **two newlines** from the main content. This prevents "thought leaks" where the model's chain-of-thought bleeds into the instruction parsing.
  ```
  <main content>

  <inline instruction>
  ```

## Tool Overuse Control

- When the model overuses tools (excessive parallel calls or unnecessary tool invocations), restrict the action budget via system prompt:
  - Set explicit maximums: "You may call no more than 5 tools per turn."
  - Prioritize tool categories: "Use `read` and `grep` before invoking `bash`."
  - Add cooldown instructions: "Do not call the same tool twice in a row unless the first result requires it."
- Monitor tool call frequency in logs and adjust thresholds dynamically.
