# Task 131: Prevent Recurring Task-File Review Findings

**File:** `tasks/completed/131-prevent-recurring-task-file-review-findings.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Eliminate the two recurring Code Reviewer findings — unchecked AC/DoD checkboxes and closing-tag indentation drift from Prettier — by hardening the task-file lifecycle and the system-prompt build pipeline.

## Manager's Notes

- Flagged twice by the Code Reviewer (Tasks 129, 130): (1) `## Acceptance Criteria` / `## Definition of Done` boxes left unchecked until the closure pass; (2) `</...>` closing tags indented by Prettier passes, drifting into the regenerated `system-prompt.md`.
- Root causes: **R1** — no mandate to check AC/DoD boxes at implementation completion (the template only mandates the sections *exist*); **R2** — `npx prettier --write` indents closing XML tags inside fragment files and the assembler propagates the drift into the artifact.
- This is a PATCH-level process-hardening change (no new capability): bump `<system_version>` MINOR? No — PATCH (e.g., `9.2.1` → `9.2.2`; use the actual current value at read-time).

## Local TODOs

- [x] Initial codebase exploration
- [x] Phase 1: mandate AC/DoD box-checking at implementation summary phase
- [x] Phase 2: fix closing-tag indentation drift (assembler normalization or prettier config)
- [x] Bump `<system_version>` + regenerate `system-prompt.md`
- [x] Update CHANGELOG.md
- [x] Verify functionality

## Acceptance Criteria

- [x] `skill-templates/task-generator/SKILL.md` and/or `prompts/fragments/09-hands_protocols.md` mandate checking AC/DoD boxes to `- [x]` during the implementation `<summary_phase>` (not deferred to the closure task).
- [x] Closing-tag indentation drift is eliminated: regenerated `system-prompt.md` has all closing tags at column 0; a guard (assembler normalization or grep check) prevents regression.
- [x] `<system_version>` bumped (PATCH) in both `prompts/fragments/01-system_version.md` and regenerated `system-prompt.md`; `CHANGELOG.md` updated.
- [x] `git diff --stat -- 'loop-engine/' '*.py'` is empty (zero out-of-scope changes).

## Verification Evidence

- **Test command:** `npx prettier --write "prompts/fragments/09-hands_protocols.md" "prompts/fragments/01-system_version.md" "prompts/fragments/06-personas.md" "skill-templates/task-generator/SKILL.md" "skill-templates/audit-agents/SKILL.md" "CHANGELOG.md"` then `python3 scripts/prompt-build/assemble_system_prompt.py` then `grep -rn "^\s\+</[a-zA-Z_][a-zA-Z0-9_]*>\s*$" prompts/fragments/` and `grep -n "^\s\+</[a-zA-Z_][a-zA-Z0-9_]*>\s*$" system-prompt.md` and `grep -n "<system_version>" prompts/fragments/01-system_version.md system-prompt.md` and `git diff --stat -- 'loop-engine/' '*.py'` and `uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** Prettier formats files (NOT the shared partial); assembler regenerates system-prompt.md; no drifted closing tags in fragments or artifact; version sync `9.2.2`; out-of-scope diff shows only prompt-build scripts; pytest suite green.
- **Actual result:** Prettier formatted all listed files (shared partial excluded after landmine discovery); assembler regenerated `system-prompt.md` (76225 bytes, exit 0); GREP 4 (fragments) → no matches (exit 1); GREP 5 (artifact) → no matches (exit 1); GREP 6 → `9.2.2` in both files; out-of-scope diff → only `assemble_system_prompt.py` (+29) and `split_system_prompt.py` (+7/−1), zero `loop-engine/`; pytest → **55 passed, exit 0**.
- **Exit code:** 0 (all commands; GREP 4/5 exit 1 = expected no-match)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Manager Decisions

**[2026-08-30] [D1] [ORCHESTRATOR-DETECTED]:** Chose assembler-level normalization over a Prettier-config exception for the closing-tag indentation drift.
- **Rationale:** Single point of fix per the task's own stated preference — the assembler normalizes the artifact regardless of source-fragment indentation, is self-verifying via the Step 6 exit-non-zero check, and doesn't depend on every future fragment edit going through Prettier the same way.
- **Alternatives considered:** `.prettierignore` on the fragments (rejected — fragile, easy to forget when adding new fragments).
- **Impact:** `assemble_system_prompt.py` now normalizes pure closing-tag lines to column 0 and fails loudly if any drift remains; `split_system_prompt.py`'s `_VP_BLOCK_RE` was relaxed to accept the normalized form (round-trip preserved).

**[2026-08-30] [D2] [ORCHESTRATOR-DETECTED]:** Chose to check AC/DoD boxes at implementation `<summary_phase>` rather than adding an automated `task-lint` enforcement rule.
- **Rationale:** Faster to ship, addresses the immediate recurring finding (unchecked boxes until closure).
- **Alternatives considered:** A hard `lint_task_file` failure if evidence-passing but boxes unchecked (deferred as a stronger but more invasive follow-up, not built here to avoid scope creep into the lint MCP server).
- **Impact:** `<hands_protocols>` summary phases now mandate box-checking before lint/staging; task-generator templates and audit-agents checks reference it.

**[2026-08-30] [D3] [EXECUTION-DETECTED]:** Flagged a follow-up hardening item — `npx prettier --write "**/*.md"` (the documented AGENTS.md format command) COLLAPSES `prompts/shared/validation-phase.md`, which is byte-load-bearing for the round-trip contract. Prettier must never run on it; a `.prettierignore` entry or a prettier-safe shared-partial layout is a recommended future task (not built here to stay in scope).

**[2026-08-30] [D4] [ORCHESTRATOR-DETECTED]:** Confirmed Option A — uniform column-0 closing tags is the permanent convention (Code Reviewer F1 resolution).
- **Rationale:** The Manager explicitly chose Option A after the Code Reviewer flagged that the normalization flattens ALL nested closing tags (not just top-level wrapper tags). Fragments are machine-authored and the artifact is generated — visual nesting cues on closing tags carry no functional value; Option A keeps the assembler self-check simple and the convention uniform.
- **Alternatives considered:** Option B — scope the normalization regex to only the outermost fragment-wrapper tag and restore nested-block indentation (rejected by Manager: would re-introduce the exact indentation surface that Prettier keeps drifting).
- **Impact:** Uniform column-0 closing tags is now the permanent convention for all fragments and the generated artifact; no follow-up task needed for F1. F2 (cosmetic summary_phase style inconsistency) deferred as optional cleanup; F3 (`import re`) verified present at line 40.

## Risk & Rollback

- **Risk:** Assembler normalization could alter byte-identical round-trip guarantees; prettier config change could affect unrelated formatting; scope creep into unrelated prompt sections.
- **Rollback plan:** Revert the fragment/assembler/prettier edits via the injected Git diff; restore `<system_version>`; the task file diff is the single rollback reference.

## Phase 1: Mandate AC/DoD Box-Checking at Implementation Completion

### Local TODOs

- [x] Locate the implementation `<summary_phase>` in `prompts/fragments/09-hands_protocols.md` and the canonical template in `skill-templates/task-generator/SKILL.md`
- [x] Add a mandate: Hands MUST check all `## Acceptance Criteria` and `## Definition of Done` boxes to `- [x]` (with evidence) during the implementation summary phase, not defer to closure
- [x] Update `skill-templates/audit-agents/SKILL.md` audit checks if applicable

## Phase 2: Fix Closing-Tag Indentation Drift

### Local TODOs

- [x] Inspect `scripts/prompt-build/assemble_system_prompt.py` for a normalization hook (strip leading whitespace on closing tags) OR add a prettier config/`.prettierignore` exception
- [x] Apply the chosen fix (prefer assembler normalization — single point of fix)
- [x] Regenerate `system-prompt.md` and verify all closing tags at column 0
- [x] Add a regression guard (grep check in verification)

## Execution Log & Reasoning

**Phase 1 — AC/DoD box-checking mandate (implementation-time):**
- `prompts/fragments/09-hands_protocols.md` — inserted a new step 1 in the `<hands_implementation_task_template>` `<summary_phase>` (before the lint step, renumbering 1→7): "Before calling `lint_task_file`, review every `## Acceptance Criteria` and `## Definition of Done` checkbox... Check `- [x]` any item that is genuinely satisfied by that evidence NOW... do NOT defer box-checking to a separate closure task." Applied the identical mirrored instruction in `<hands_combined_task_template>`'s implementation-success branch.
- `skill-templates/task-generator/SKILL.md` — added a one-line box-checking mandate (referencing `<hands_protocols>` as authoritative) to BOTH the single-phase and multi-phase `## Definition of Done` blocks.
- `skill-templates/audit-agents/SKILL.md` — extended the Decision Logging Mandate audit bullet (both Target Audit Criteria + Mode 2 occurrences) with: "`prompts/fragments/09-hands_protocols.md` MUST instruct the Hands to check AC/DoD boxes during the implementation `<summary_phase>`, not defer to a closure task."

**Phase 2 — Closing-tag indentation drift (assembler normalization):**
- **Pre-existing assembler structure (read in full, 363 lines):** `assemble()` reads `prompts/manifest.txt`, validates each fragment path against the `fragments/` security boundary (`_safe_fragment_path`), resolves `<!--INCLUDE:...-->` markers (`_resolve_includes` with `_safe_include_path` path-traversal guard), runs two loud guards (unresolved include marker, unresolved `{{PLACEHOLDER}}`), strips trailing newlines per fragment, joins with `"\n\n".join(parts) + "\n"` (line 325), and writes to `output_path` (line 330).
- **Step 5 (assembler normalization):** inserted between the join and the write — `_CLOSING_TAG_ONLY_RE = re.compile(r"^\s*(</[a-zA-Z_][a-zA-Z0-9_]*>)\s*$")`; every matching line is replaced by `match.group(1)` (the bare tag at column 0). Single-point fix: the artifact is normalized regardless of source-fragment indentation.
- **Step 6 (self-check):** immediately after normalization, `_DRIFTED_CLOSING_TAG_RE = re.compile(r"^\s+</[a-zA-Z_][a-zA-Z0-9_]*>\s*$")` scans the final content; any remaining indented pure closing tag raises `ValueError` naming the offending line (exit non-zero) instead of silently writing a drifted artifact.
- **Step 7 (source-fragment cleanup):** applied the same regex to `prompts/fragments/06-personas.md` (9 closing-tag lines: `</persona>` ×7, `</behavior>` ×1, plus idempotent column-0 hits), `prompts/fragments/09-hands_protocols.md` (18 lines), and `prompts/shared/validation-phase.md` (1 line: `</validation_phase>`). Verified `grep -rn "^\s\+</..." prompts/fragments/ prompts/shared/` → zero matches.
- **Step 8 (round-trip verification):** `git diff` on the fragments confirmed ONLY whitespace on pure-closing-tag lines changed, no content shifted. The round-trip test initially FAILED after the normalization because `split_system_prompt.py`'s `_VP_BLOCK_RE` hardcoded the `</validation_phase>` closing tag at 2-space indent — **fixed the splitter** (in-scope consequence of the assembler change): relaxed the closing tag to `\s*</validation_phase>` so it accepts both pre- and post-normalization forms. Round-trip + sync tests then passed.
- **Prettier landmine discovered:** running `npx prettier --write` on `prompts/shared/validation-phase.md` COLLAPSES the entire file (removes the 2-space wrapper indentation, collapses multi-line content into single lines, drops the no-trailing-newline structure) — this shared partial is byte-load-bearing for the round-trip contract. Restored it to the correct structure (2-space `<validation_phase>`, 4-space content, column-0 `</validation_phase>`, no trailing newline). **Prettier must NEVER be run on `prompts/shared/validation-phase.md`.** Flagged as a follow-up hardening item (see Manager Decisions D2).

**Phase 3 — Version + regenerate:**
- `prompts/fragments/01-system_version.md` — bumped `<system_version>` 9.2.1 → 9.2.2 (PATCH).
- Regenerated `system-prompt.md` via the patched assembler (76225 bytes, exit 0). Verified: GREP 4 (fragments) empty, GREP 5 (artifact) empty, GREP 6 version sync `9.2.2` in both.
- **Tests:** `uv run --with pytest ... pytest tests/ -q` → **55 passed, exit 0** (round-trip + lint-sync + all MCP tests green).
- **Out-of-scope:** `git diff --stat -- 'loop-engine/' '*.py'` → only `scripts/prompt-build/assemble_system_prompt.py` (+29) and `scripts/prompt-build/split_system_prompt.py` (+7/−1) — both in scope; zero `loop-engine/` changes.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `7fbb87de742e96df6386c2ee25adc193d0270e41`
<!-- END_GIT_DIFF -->