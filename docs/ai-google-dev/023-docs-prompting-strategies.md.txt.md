---
title: Prompting strategies
url: https://ai.google.dev/gemini-api/docs/prompting-strategies.md.txt
source: llms
fetched_at: 2026-04-29T11:16:55.478244231-03:00
rendered_js: false
word_count: 1289
summary: This document provides an introduction to prompt design strategies, covering techniques for providing clear instructions, defining input types, setting constraints, and specifying desired output formats for generative AI models.
tags:
    - prompt-engineering
    - generative-ai
    - prompt-design
    - instruction-tuning
    - model-interaction
category: guide
optimized: true
optimized_at: 2026-04-29T12:00:00Z
---
*Prompt design* creates natural language requests that elicit accurate, high-quality responses from language models.

> [!NOTE]
> Prompt engineering is iterative. These guidelines are starting points—experiment and refine based on your use cases.

## Topic-specific prompt guides

- [[011-docs-files|Prompting with media files]]
- [[045-docs-models-gemini-2.5-flash-image|Imagen]] and [[045-docs-models-gemini-2.5-flash-image|Gemini Native Image Generation]] prompt guides
- [[033-docs-video|Video prompting]]
- [[023-docs-prompting-strategies|Prompt gallery]] with sample prompts

## Clear and specific instructions

Provide clear, specific instructions to customize model behavior—questions, step-by-step tasks, or complex scenarios.

### Input types

| **Type** | **Description** | **Example prompt** |
|---|---|---|
| Question | Model answers | What's a good name for a flower shop specializing in dried flowers? Create a list of 5 options. |
| Task | Model performs | Give me a simple list of 5 items to bring on a camping trip. |
| Entity | Model operates on | Classify: Elephant, Mouse, Snail → [large, small] |
| Completion | Model continues | Valid fields: cheeseburger, hamburger, fries, drink. Order: A burger and a drink. Output: `{ "hamburger": 1, "drink": 1 }` |

#### Partial input completion

Generative models work like advanced auto-completion. Include examples and context for the model to follow patterns:

|---|
| **Prompt:** For the given order, return a JSON object with fields cheeseburger, hamburger, fries, or drink (quantity). Order: A burger and a drink. **Output:** `{ "cheeseburger": 0, "hamburger": 1, "fries": 0, "drink": 1 }` |
| **Prompt:** Valid fields: cheeseburger, hamburger, fries, drink. Order: Give me a cheeseburger and fries. Output: `{ "cheeseburger": 1, "fries": 1 }` |

For complex JSON schemas, use [[026-docs-structured-output]] instead of natural language.

### Constraints

Specify what the model should and shouldn't do. Example: limit summary to one sentence.

|---|
| **Prompt:** Summarize in one sentence: "A quantum computer exploits quantum mechanical phenomena..." **Output:** "Exploiting quantum mechanical phenomena, quantum computers can perform calculations exponentially faster..." |

### Response format

Specify format: table, bulleted list, elevator pitch, keywords, sentence, or paragraph. Use system instructions for tone:

|---|
| **System instruction:** All questions should be answered comprehensively with details, unless the user requests concise response. **Prompt:** What is a smart way to make a business selling DVDs in 2026? |

#### Format responses with completion strategy

Start the outline format and let the model complete it:

|---|
| **Prompt:** Create an outline for an essay about hummingbirds. I. Introduction * **Output:** I. Introduction * Hook, Background, Thesis Statement... |

## Zero-shot vs few-shot prompts

- **Zero-shot:** No examples
- **Few-shot:** Include examples showing patterns, formatting, phrasing

We recommend few-shot prompts. Clear examples can replace explicit instructions.

|---
| **Prompt (zero-shot):** Choose best explanation. Question: How is snow formed? Explanation1: Detailed... Explanation2: Brief. **Answer:** Explanation1 |

|---
| **Prompt (few-shot):** Format: Question, Explanation1, Explanation2, Answer. Question: Why is sky blue? Explanation1: Rayleigh scattering... Explanation2: Due to Rayleigh effect. Answer: Explanation2. Now: Question: How is snow formed? Explanation1: Detailed... Explanation2: Brief. **Answer:** Explanation2 |

### Optimal number of examples

- Few examples often suffice
- Too many examples risks [overfitting](https://developers.google.com/machine-learning/glossary#overfitting)

### Consistent formatting

Maintain identical structure, XML tags, whitespace, newlines, and example splitters across few-shot examples.

## Add context

Include required information in the prompt instead of assuming the model knows it:

|---|
| **Prompt:** What should I do to fix my disconnected wifi? Light on my Google Wifi router is yellow and blinking slowly. **Response:** Generic troubleshooting info |

|---|
| **Prompt:** Answer using the text below. Respond with only the text. Question: yellow blinking light on Google Wifi. Text: Color: Slowly pulsing yellow → Network error. Check Ethernet cable... **Response:** Check that the Ethernet cable is connected to both your router and modem... |

## Break down prompts into components

1. **Break down instructions:** One prompt per instruction, choose based on user input.
2. **Chain prompts:** Sequential steps; output of one becomes input of the next.
3. **Aggregate responses:** Parallel tasks on data portions, aggregate results.

## Experiment with model parameters

| **Parameter** | **Description** |
|---|---|
| **Max output tokens** | Max tokens in response. ~100 tokens ≈ 60-80 words. |
| **Temperature** | Randomness in token selection. Lower = more deterministic. 0 = always highest probability. |
| **`topK`** | Token selection pool size. `topK=1` = greedy decoding. `topK=3` picks from 3 most probable. |
| **`topP`** | Cumulative probability cutoff. Default 0.95. |
| **`stop_sequences`** | Sequence that stops generation. Avoid sequences that appear in expected content. |

> [!NOTE]
> **Gemini 3:** Keep `temperature` at default 1.0. Setting below 1.0 may cause looping or degraded performance in math/reasoning tasks.

## Prompt iteration strategies

1. **Use different phrasing:** "How do I bake a pie?" vs "Suggest a recipe for a pie."
2. **Switch to analogous task:** "Which category does The Odyssey belong to: thriller sci-fi mythology biography" → response doesn't stay in bounds. Reframe as multiple choice.
3. **Change content order:** Try `[examples] [context] [input]` vs `[input] [examples] [context]` vs `[examples] [input] [context]`.

## Fallback responses

Fallbacks occur when prompts or responses trigger safety filters (e.g., "I'm not able to help with that..."). Try increasing temperature.

## Grounding and code execution

- [[011-docs-files|Google Search grounding]] connects to real-time web content—enable for obscure or recent facts.
- [[026-docs-structured-output|Code execution]] generates and runs Python for arithmetic, counting, calculations.

## Gemini 3

[[027-docs-thinking|Gemini 3 models]] are designed for advanced reasoning and instruction following. Best practices:

### Core prompting principles

- **Be precise and direct:** State goals clearly. Avoid overly persuasive language.
- **Use consistent structure:** XML tags (`<context>`, `<task>`) or Markdown headings. Choose one format and use it consistently.
- **Define parameters:** Explain ambiguous terms explicitly.
- **Control output verbosity:** Gemini 3 provides direct answers by default. Request conversational/detailed responses explicitly.
- **Handle multimodal inputs:** Treat text, images, audio, video as equal-class inputs.
- **Prioritize critical instructions:** Place behavioral constraints, role definitions, output format in System Instruction or start of user prompt.
- **Structure for long contexts:** Supply context first, instructions/questions at the *end*.
- **Anchor context:** After large data blocks, use "Based on the information above..."

### Gemini 3 Flash strategies

- **Current day accuracy:** Add to system instructions: "For time-sensitive queries requiring up-to-date information, you MUST follow the provided current time (date and year) in search queries. Remember it is 2026 this year."
- **Knowledge cutoff:** Add: "Your knowledge cutoff date is January 2025."
- **Grounding:** Add: "You are a strictly grounded assistant limited to the information provided in the User Context. Rely **only** on facts directly mentioned..."

### Enhancing reasoning

Gemini 2.5 and 3 series automatically generate internal "thinking" text. Simple requests like "Think very hard before answering" improve performance at extra token cost. See [[027-docs-thinking]] for detail.

### Structured prompting examples

**XML:**
```xml
<role>You are a helpful assistant.</role>
<constraints>
1. Be objective.
2. Cite sources.
</constraints>
<context>[Insert User Input Here]</context>
<task>[Insert the specific user request here]</task>
```

**Markdown:**
```markdown
# Identity
You are a senior solution architect.

# Constraints
- No external libraries allowed.
- Python 3.11+ syntax only.

# Output format
Return a single code block.
```

**Template combining best practices:**
```text
<role>You are Gemini 3, a specialized assistant for [Insert Domain]. You are precise, analytical, persistent.</role>

<instructions>
1. **Plan**: Analyze task and create step-by-step plan.
2. **Execute**: Carry out the plan.
3. **Validate**: Review output against task.
4. **Format**: Present in requested structure.
</instructions>

<constraints>
- Verbosity: [Specify Low/Medium/High]
- Tone: [Specify Formal/Casual/Technical]
</constraints>

<output_format>
1. **Executive Summary**: [Short overview]
2. **Detailed Response**: [Main content]
</output_format>

<context>[Relevant documents, code snippets, background]</context>
<task>[Specific user request]</task>
<final_instruction>Remember to think step-by-step before answering.</final_instruction>
```

## Agentic workflows

Complex agents often require configuring trade-offs between computational cost (latency, tokens) and task accuracy.

### Dimensions of agentic behavior

**Reasoning and strategy:**
- **Logical decomposition:** How thoroughly model analyzes constraints, prerequisites, order of operations
- **Problem diagnosis:** Depth of causal analysis; explore complex explanations or accept obvious answer
- **Information exhaustiveness:** Analyze every policy vs prioritize efficiency

**Execution and reliability:**
- **Adaptability:** React to new data—strictly follow plan or pivot immediately
- **Persistence and Recovery:** Self-correct errors; high persistence = higher success but higher token cost
- **Risk Assessment:** Distinguish low-risk exploratory (reads) from high-risk state changes (writes)

**Interaction and output:**
- **Ambiguity handling:** When to make assumptions vs pause for clarification
- **Verbosity:** Volume of text with tool calls—explain actions or remain silent
- **Precision and completeness:** Exact figures vs ballpark estimates

### System instruction template

```text
You are a very strong reasoner and planner. Use these critical instructions to structure your plans, thoughts, and responses.

Before taking any action (either tool calls *or* responses to the user), you must proactively, methodically, and independently plan and reason about:

1) Logical dependencies and constraints:
   1.1) Policy-based rules, mandatory prerequisites, constraints.
   1.2) Order of operations: ensure taking an action doesn't prevent a subsequent necessary action.
       1.2.1) The user may request actions in random order, but you may need to reorder operations.
   1.3) Other prerequisites (information and/or actions needed).
   1.4) Explicit user constraints or preferences.

2) Risk assessment: Will the action cause future issues?

3) Abductive reasoning:
   3.1) Look beyond immediate causes.
   3.2) Hypotheses may require multiple steps to test.
   3.3) Prioritize by likelihood, don't discard less likely prematurely.

4) Outcome evaluation: Does observation require plan changes?

5) Information availability:
   5.1) Using available tools and their capabilities
   5.2) All policies, rules, checklists, constraints
   5.3) Previous observations and conversation history
   5.4) Information only available by asking the user

6) Precision and Grounding: Quote exact applicable information when referring to policies.

7) Completeness:
   7.1) Resolve conflicts using order of importance in #1.
   7.2) Avoid premature conclusions—multiple options may be relevant.
       7.2.1) Check all information sources from #5.
       7.2.2) Consult user if uncertain about applicability.
   7.3) Review all sources to confirm relevance to current state.

8) Persistence and patience: Do not give up unless reasoning is exhausted.
   8.1) Don't be dissuaded by time or frustration.
   8.2) Intelligent persistence: On *transient* errors (retry), MUST retry unless explicit retry limit reached.

9) Inhibit your response: only take action after all reasoning is completed.
```

## Next steps

- Try writing prompts in [Google AI Studio](http://aistudio.google.com).
- Learn about [[011-docs-files|multimodal prompting]].
- Learn about image prompting with [[045-docs-models-gemini-2.5-flash-image|Nano Banana]] and [[045-docs-models-gemini-2.5-flash-image|Imagen]].
- Learn about video prompting with [[045-docs-models-gemini-2.5-flash-image|Veo]].

#prompt-engineering #generative-ai #instruction-tuning