# Input Validation Pipeline Test

**How to use:** Copy the block below and paste it into your Orchestrator session to test the input processing pipeline with a sample raw input.

## Test Prompt

```
Process the following raw input through the complete Input Validation Pipeline:
1. Validate (typos, clarity, completeness)
2. Translate to English
3. Enrich with edge cases and constraints
4. Refactor into elite XML spec
5. Present the result for approval

RAW INPUT:
[PASTE YOUR RAW FARSI/ENGLISH INPUT HERE]
```

## Expected Behavior

- If the input is clear: The pipeline should translate, enrich, refactor, and present for approval.
- If the input is unclear: The pipeline should HALT and ask for clarification.
- If the input has typos: The pipeline should correct them and note the corrections.
