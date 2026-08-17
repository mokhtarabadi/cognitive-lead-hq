---
created_at: '2026-08-16T06:51:03.566089+00:00'
status: active
tags: []
updated_at: '2026-08-16T06:51:03.566185+00:00'
---

system-prompt.md is a GENERATED build artifact, NOT a hand-edited source file.

- Source tree: prompts/fragments/ (20 per-tag fragment files, 01-system_version.md through 20-initialization.md) + prompts/shared/ (shared partials, e.g. validation-phase.md). prompts/manifest.txt lists fragments in assembly order.
- Assembler: scripts/prompt-build/assemble_system_prompt.py reads prompts/manifest.txt, concatenates fragments in order with a single blank line (joined with '\n\n', terminated with '\n'), resolves <!--INCLUDE:path|PARAM=value--> markers by substituting {{PARAM}} placeholders in shared partials, and writes to system-prompt.md by default (--output to redirect to a temp path for verification).
- Disassembler: scripts/prompt-build/split_system_prompt.py reverses the process (extracts top-level tags into fragments, extracts the 3 duplicated <validation_phase> blocks into prompts/shared/validation-phase.md with include markers).
- NEVER hand-edit system-prompt.md directly. To make a change: edit the relevant fragment in prompts/fragments/ or the shared partial in prompts/shared/, then run: python3 scripts/prompt-build/assemble_system_prompt.py
- Run lint_system_prompt_sync() (lint MCP server) or `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check.md && diff /tmp/check.md system-prompt.md` before any commit to confirm the generated file matches its source.
- Include marker format: <!--INCLUDE:shared/validation-phase.md|NEXT_PHASE=Context--> — path is relative to prompts/; params pipe-separated as KEY=VALUE; each {{KEY}} placeholder in the shared file is substituted with the value.
- The shared validation-phase.md file includes the full <validation_phase>...</validation_phase> wrapper tags and original indentation (with {{NEXT_PHASE}} placeholder) so include resolution is byte-identical — the include marker replaces the entire block inclusive of wrapper tags.
- Version bumps: update <system_version> in prompts/fragments/01-system_version.md, then re-run the assembler.