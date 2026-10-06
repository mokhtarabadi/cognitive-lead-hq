# Slice: shared

## Duties

Shared prompt partials referenced by `<!--INCLUDE:-->` markers from fragments. Single source for blocks that must stay byte-identical across the assembled prompt.

## Files

- `validation-phase.md` — Byte-identical `<validation_phase>` block included by Hands protocols.

## Key Risks & Invariants

- Included content must stay byte-identical to every inclusion site; edit here, never duplicate.
- Assembler output must equal committed `system-prompt.md` (lint gate enforces this).
- No fragment-order logic here; ordering lives in `prompts/manifest.txt`.
