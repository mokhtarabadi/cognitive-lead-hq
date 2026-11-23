# Slice: scripts

## Duties

Maintenance tooling: docs-sync gate and system-prompt assembler/splitter. Enforces permission parity and prompt-build reproducibility.

## Files

- `check_docs_sync.py` — Docs-sync gate: repo vs global `opencode.json` permission deny-set parity plus orphan-script scan.
- `prompt-build/assemble_system_prompt.py` — Assembles `system-prompt.md` from `prompts/` in `manifest.txt` order.
- `prompt-build/split_system_prompt.py` — Splits an assembled prompt back into fragment sources.
- `format-guard.sh` — OpenCode formatter guard: dispatches Markdown/code formatting (prettier, ruff, shfmt) on `write`/`edit`/`patch` while skipping byte-sensitive artifacts (fragments, shared partials, assembled prompts, task files with injected diffs).

## Key Risks & Invariants

- Defensive shell/Python protocol: strict mode, no error masking on data commands.
- Assembler output must be byte-identical to committed `system-prompt.md` (lint gate).
- Version bump in `<system_version>` required on every prompt rebuild.
- Auto-format exclusions live in two places: `.prettierignore`, which prettier reads, and the `case` arm in `scripts/format-guard.sh`. Both directions are pinned by `test_format_guard_matches_prettierignore` and `test_prettierignore_covers_guard_arms`, so editing one without the other is a red test. The exclusion is defense in depth: these files are Prettier-stable today, and the guard keeps them that way rather than repairing them.
