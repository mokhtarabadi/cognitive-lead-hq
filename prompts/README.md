# Prompts — System Prompt Source Tree

> **Runtime:** `system-prompt.md` is a **generated build artifact**, not a hand-edited source file.
> All authorial edits go into the `prompts/` source tree; regenerate via the
> assembler script before committing.

## Layout

```
prompts/
├── README.md                   # This file — the authoring workflow guide
├── manifest.txt                # Ordered list of fragment filenames (assembly order)
├── fragments/                  # One file per top-level XML tag in system-prompt.md (V9.0.0: 19 tags)
│   ├── 01-system_version.md
│   ├── 02-role.md
│   ├── 03-system_context.md
│   ├── 04-ai_objective.md
│   ├── 05-user_input_processing.md
│   ├── 06-personas.md
│   ├── 07-agent_skills_registry.md
│   ├── 08-agentic_reasoning.md
│   ├── 09-hands_protocols.md     # Contains <!--INCLUDE:--> markers
│   ├── 10-lite_mode_protocol.md
│   ├── 11-execution_workflow.md
│   ├── 12-brainstorming_protocol.md
│   ├── 13-constraints.md
│   ├── 14-solid_programming_mandate.md
│   ├── 15-universal_datetime_rules.md
│   ├── 16-immutable_financial_ledger_mandate.md
│   ├── 18-no_manual_dto_mandate.md
│   ├── 19-initialization.md
│   └── 19-communication_examples.md
└── shared/                     # Shared partials referenced by include markers
    └── validation-phase.md     # The byte-identical <validation_phase> block
```

## Authoring Workflow

1. **Edit a source fragment** in `prompts/fragments/` or a shared partial in
   `prompts/shared/`. Never edit `system-prompt.md` directly — it will be
   overwritten on the next assemble step.

2. **Reassemble** from the project root:

   ```bash
   python3 scripts/prompt-build/assemble_system_prompt.py
   ```

   This reads `prompts/manifest.txt`, concatenates the fragments in order,
   resolves any `<!--INCLUDE:path|PARAM=value-->` markers, and writes the
   result to `system-prompt.md`.

3. **Verify sync** before staging/committing:

   ```bash
   # In OpenCode, the lint MCP server exposes this tool automatically
   # (covered by the "lint_*": "allow" permission rule in opencode.json):
   ```

   Or verify manually against a temp path:

   ```bash
   python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check.md
   diff /tmp/check.md system-prompt.md   # must show zero differences
   ```

4. **Version bumps:** update `<system_version>` in
   `prompts/fragments/01-system_version.md`, then re-run the assembler.
   Every version change to `system-prompt.md` must be reflected in the fragment
   source (not by hand-editing the generated file).

## How It Works

- **`scripts/prompt-build/split_system_prompt.py`** — the disassembler. Reads
  `system-prompt.md` and splits it into the 19 top-level tags (V9.0.0). The
  `<validation_phase>` block (duplicated 3× inside the `hands_protocols`
  templates) is extracted to `prompts/shared/validation-phase.md` and each
  occurrence is replaced with an `<!--INCLUDE:...-->` marker.

- **`scripts/prompt-build/assemble_system_prompt.py`** — the assembler. Reads
  `prompts/manifest.txt`, concatenates fragments in order, resolves
  `<!--INCLUDE:path|PARAM=value-->` markers (substituting `{{PARAM}}`
  placeholders in the shared partials), and writes the assembled prompt.

- **`prompts/manifest.txt`** — a plain list of fragment filenames, one per
  line, in assembly order. Reordering this file changes the output layout.

### Include-marker format

```
<!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context-->
```

The path is relative to `prompts/`. Each `|KEY=VALUE` pair substitutes a
`{{KEY}}` placeholder in the referenced shared file.

#### Include-path safety

- Include paths must be **relative** — absolute paths are rejected by the
  assembler.
- Include paths must remain **inside `prompts/`** — parent-directory traversal
  (e.g. `../outside.md`) is rejected by the assembler with a `ValueError`.
- **Malformed or unresolved include markers** (e.g. a broken closing sequence
  like `--!>`, or a marker whose shared file is missing) cause the assembler
  to **fail loudly** with a `ValueError` naming the offending fragment — they
  never leak into the generated `system-prompt.md`.

#### Manifest-entry safety

The manifest (`prompts/manifest.txt`) is an untrusted input surface — the same
security boundary applies to its entries as to include paths:

- Manifest entries must remain **inside `prompts/fragments/`** — an entry
  that resolves outside `fragments/` (parent-directory traversal) is rejected
  by the assembler with a `ValueError`.
- **Absolute manifest paths** are rejected by the assembler — only filenames
  relative to `prompts/fragments/` are allowed.
- **Parent-directory traversal in manifest entries** (e.g. `../outside.md`)
  is rejected by the assembler with a `ValueError` naming the unsafe entry.

## Sync Verification

The lint MCP server exposes `lint_system_prompt_sync()`, which re-runs the
assembler to a temp path and compares the result to the committed
`system-prompt.md`. Run it before any commit to confirm the fragments (the
true source of truth) and the generated file are in sync.
