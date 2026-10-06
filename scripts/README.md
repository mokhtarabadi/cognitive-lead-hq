# Slice: scripts

## Duties

Maintenance tooling: docs-sync gate and system-prompt assembler/splitter. Enforces permission parity and prompt-build reproducibility.

## Files

- `check_docs_sync.py` — Docs-sync gate: repo vs global `opencode.json` permission deny-set parity plus orphan-script scan.
- `prompt-build/assemble_system_prompt.py` — Assembles `system-prompt.md` from `prompts/` in `manifest.txt` order.
- `prompt-build/split_system_prompt.py` — Splits an assembled prompt back into fragment sources.

## Key Risks & Invariants

- Defensive shell/Python protocol: strict mode, no error masking on data commands.
- Assembler output must be byte-identical to committed `system-prompt.md` (lint gate).
- Version bump in `<system_version>` required on every prompt rebuild.
