---
name: perplexity-research
description: Triggers a human-in-the-loop deep research cycle using the Perplexity 3-Step Framework. Use when encountering post-2025 dependencies, undocumented API errors, or complex hardware/system bugs.
---

# Perplexity Deep Research Workflow

You are an AI Agent operating with a static knowledge cutoff. When you encounter a technical problem, compiler error, or architectural question that your native knowledge or local `websearch` tool cannot confidently resolve, you MUST NOT hallucinate. You must leverage the Manager as a deep-research bridge via Perplexity.

## When to Trigger

- You hit a completely undocumented API error in a modern framework (post-2025).
- You need a comparison of newly released architectural patterns.
- A fix requires navigating complex OS/Hardware quirks (like ACPI, BIOS, or obscure Linux kernel bugs).

## The Workflow

1. **HALT Execution:** Do not attempt to guess the code fix.
2. **Generate the Query:** Formulate a highly precise, technical research query. Include exact error logs, hardware constraints, and the tech stack.
3. **Instruct the Manager:** Output the following exact message block to the user:

> 🛑 **Deep Research Required:** I have encountered an issue that requires up-to-date external context.
>
> **Manager:** Please open the `user-prompts/perplexity-deep-research.md` file. Copy the 3-Step Framework, append the exact query below to the bottom of it, and run it in a new Perplexity session. Paste the results back here.
>
> **Query to append:**
>
> ```text
> [Insert your highly technical, specific query here]
> ```

4. **Wait:** Do nothing else until the Manager returns with the Perplexity findings.
