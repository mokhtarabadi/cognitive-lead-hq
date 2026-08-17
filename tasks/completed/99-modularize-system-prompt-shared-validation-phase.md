# Task 99: Modularize System Prompt with Shared Validation Phase

**File:** `tasks/completed/99-modularize-system-prompt-shared-validation-phase.md`
**Source:** orchestrator
**Type:** refactor
**Status:** closed

## Goal

Extract the byte-identical `<validation_phase>` block, currently duplicated 3x across `<hands_discovery_task_template>`, `<hands_implementation_task_template>`, and `<hands_combined_task_template>` in `system-prompt.md`, into a single shared source fragment. Fully split `system-prompt.md` into per-section fragments under `prompts/fragments/` so it becomes a generated build artifact (assembled via script) rather than a hand-edited monolith. The `<summary_phase>` overlap between implementation and combined templates is explicitly OUT OF SCOPE — it is not byte-identical and requires a separate wording-reconciliation task. No text change to the final assembled `system-prompt.md` is expected or permitted; the only measurable output is a version bump (see Step 7) and improved editability of the source.

## Local TODOs

### Phase A: Task Setup

- [x] **Step 1:** Load `task-generator`, discover the next task ID (`NN`), and create `tasks/backlog/<NN>-modularize-system-prompt-shared-validation-phase.md` with the canonical template.
- [x] **Step 2:** Copy the current `system-prompt.md` to `/tmp/system-prompt.pristine.md` — the ground-truth for the Step 6 verification.

### Phase B: Fragment Extraction

- [x] **Step 3:** Write `scripts/prompt-build/split_system_prompt.py` — parse the 20 top-level tags into `prompts/fragments/<seq>-<tagname>.md`, special-case `hands_protocols` to extract the 3 `<validation_phase>` blocks into `prompts/shared/validation-phase.md` with include markers, emit `prompts/manifest.txt`.
- [x] **Step 4:** Run `split_system_prompt.py` once to generate the fragments, `prompts/manifest.txt`, and `prompts/shared/validation-phase.md`.

### Phase C: Assembler + Verification

- [x] **Step 5:** Write `scripts/prompt-build/assemble_system_prompt.py` — read `prompts/manifest.txt`, concatenate fragments in order, resolve `<!--INCLUDE:path|PARAM=value-->` markers, write to caller-specified output path.
- [x] **Step 6:** Run the assembler against a temp path, diff against `/tmp/system-prompt.pristine.md` — MUST show zero differences before proceeding.
- [x] **Step 7:** Bump `<system_version>` to the next patch version, re-run the assembler, overwrite the real `system-prompt.md`.

### Phase D: Lint Tooling + Tests

- [x] **Step 8:** Add `lint_system_prompt_sync()` to `mcp-lint-server/server.py` — re-runs the assembler and compares to the committed `system-prompt.md`.
- [x] **Step 9:** Add regression tests to `tests/test_mcp_servers.py` — round-trip byte-identity, clean sync, drift detection.

### Phase E: Docs + Memory

- [x] **Step 10:** Write `prompts/README.md` — document the generated-artifact authoring workflow.
- [x] **Step 11:** Update `README.md` repository structure tree with `prompts/` and `scripts/prompt-build/` entries.
- [x] **Step 12:** Add a status note at the top of `docs/system-prompt-modularization.md` pointing to this task.
- [x] **Step 13:** Load `project-memory` and store the `system-prompt-build-process` constraint.

### Phase F: QA Fix Round 1

- [x] **Step 1 (V1):** Add existence guard to `lint_system_prompt_sync()` / `_check_system_prompt_sync()` in `mcp-lint-server/server.py` — check `Path(system_prompt_path).is_file()` before reading, return `(False, "Error: File not found: <path>")` on missing file.
- [x] **Step 2 (V2):** In `scripts/prompt-build/assemble_system_prompt.py`, add unresolved-placeholder check after `_resolve_includes()` — raise `ValueError` with fragment filename and unresolved `{{...}}` placeholder text if any remain.
- [x] **Step 3 (V1 test):** Add `test_lint_system_prompt_sync_missing_system_prompt_file` to `tests/test_mcp_servers.py` — call `_check_system_prompt_sync(system_prompt_path=<nonexistent>)` and assert `(False, "not found")` without raising.
- [x] **Step 4 (V2 test):** Add `test_assemble_raises_on_unresolved_placeholder` to `tests/test_mcp_servers.py` — construct temp fragments/shared/manifest with unresolved `{{FOO}}`, call `assemble()`, assert `ValueError` with placeholder text.
- [x] **Step 5 (optional):** Add `test_split_halts_on_missing_top_level_tag` — strip a top-level tag from pristine copy, call `split_system_prompt()`, assert `SystemExit` via `pytest.raises(SystemExit)`.
- [x] **Step 6:** Re-run full suite (all prior 34 tests + new ones) and confirm no regressions.

### Phase G: QA Fix Round 2

- [x] **Step 1:** In `mcp-lint-server/server.py`, widen the exception handling around the `assembler.assemble(...)` call inside `_check_system_prompt_sync()` to also catch `ValueError` (in addition to the existing `FileNotFoundError`), returning a clean `(False, f"Error: {e}")` tuple — do NOT let it propagate.
- [x] **Step 2:** Add `test_lint_system_prompt_sync_handles_unresolved_placeholder` to `tests/test_mcp_servers.py` — reuse the same temp `fragments/shared/manifest` fixture shape as `test_assemble_raises_on_unresolved_placeholder`, call `_check_system_prompt_sync()` (not `assemble()` directly), assert `(False, <message>)` without raising + message identifies placeholder.
- [x] **Step 3:** Re-run the full suite (37 prior + 1 new = 38) and confirm no regressions.
- [x] **Step 4:** Diff `mcp-lint-server/server.py` and `tests/test_mcp_servers.py` against pre-this-task state and confirm changes are present in that diff.

### Phase H: QA Fix Round 3

- [x] **Step 1:** Add failing tests in `tests/test_mcp_servers.py`: `test_assemble_rejects_path_traversal_include` (include marker reads `../outside.md`, asserts ValueError identifying unsafe path) + `test_assemble_rejects_malformed_include_marker` (malformed `<!--INCLUDE:shared/test.md|NEXT_PHASE=Context--!>`, asserts ValueError identifying fragment + malformed marker).
- [x] **Step 2:** Implement include-path safety in `scripts/prompt-build/assemble_system_prompt.py` — add `_safe_include_path(rel_path, prompts_dir)` helper rejecting absolute paths and paths resolving outside `prompts_dir`, raise ValueError, use inside `_resolve_includes()`.
- [x] **Step 3:** Implement malformed/unresolved include-marker detection in `assemble_system_prompt.py` — after `_resolve_includes()`, check for remaining literal `<!--INCLUDE:` substring, raise ValueError identifying fragment; run BEFORE the unresolved-placeholder check.
- [x] **Step 4:** Add failing tests in `tests/test_mcp_servers.py`: `test_lint_system_prompt_sync_missing_include_file` (valid-looking marker pointing to missing shared file → `(False, message)` without raising) + `test_lint_system_prompt_sync_invalid_fragments_dir_configuration` (regular file as fragments_dir → `(False, message)` without raising).
- [x] **Step 5:** Harden `_check_system_prompt_sync()` in `mcp-lint-server/server.py` — wrap assembler load, assembly, temp-file read, committed-file read, and diff generation in diagnostic handler catching `Exception` (NOT SystemExit/KeyboardInterrupt), return `(False, f"Error: {e}")`, preserve temp cleanup in `finally`.
- [x] **Step 6:** Update `prompts/README.md` — add safety note under include-marker format section (relative paths only, must stay inside `prompts/`, absolute/traversal rejected, malformed markers fail loudly).
- [x] **Step 7:** Perform read-only reference audit of `AGENTS.md`, `llm.txt`, `llms.txt` — record results under `## Verification Evidence` → `### Reference Audit`.
- [x] **Step 8:** Run all verification commands (py_compile, pytest, fresh assembler diff, lint_system_prompt_sync, reference audit) and record under `## Verification Evidence` → `### QA Fix Round 3`.

### Phase I: QA Fix Round 4

- [x] **Step 1:** Add this `Phase I: QA Fix Round 4` section under `## Local TODOs`, mirroring the task steps.
- [x] **Step 2:** Add failing tests in `tests/test_mcp_servers.py`: `test_assemble_rejects_path_traversal_manifest_entry` (manifest containing `../outside.md`, asserts ValueError identifying unsafe manifest entry) + `test_assemble_rejects_absolute_manifest_entry` (manifest containing absolute path of outside file, asserts ValueError identifying unsafe absolute entry).
- [x] **Step 3:** Add failing test `test_lint_system_prompt_sync_handles_assembler_load_failure` — monkeypatch `_load_assembler` to raise `SyntaxError("synthetic assembler load failure")`, call `_check_system_prompt_sync()`, assert `(False, message)` without raising + message identifies the load failure.
- [x] **Step 4:** Run the three new tests and confirm they FAIL for the expected reasons (do NOT proceed if any unexpectedly passes).
- [x] **Step 5:** Implement manifest-path safety in `scripts/prompt-build/assemble_system_prompt.py` — add `_safe_fragment_path(filename, fragments_dir)` helper (reject empty/absolute entries, reject paths resolving outside `fragments_dir`), raise ValueError, use inside `assemble()` before reading each fragment.
- [x] **Step 6:** Harden assembler-load exception handling in `mcp-lint-server/server.py` — keep specific `FileNotFoundError` handler, add generic `Exception` handler returning `(False, f"Error: {e}")`, do NOT catch SystemExit/KeyboardInterrupt.
- [x] **Step 7:** Re-run the three new tests and confirm they PASS.
- [x] **Step 8:** Update `prompts/README.md` — add manifest-safety note (entries must stay inside `prompts/fragments/`, absolute paths and traversal rejected). Do NOT edit `AGENTS.md`/`LLM.txt`/`llm.txt`/`llms.txt`.
- [x] **Step 9:** Run all verification commands (py_compile, full pytest, fresh assembler diff, lint_system_prompt_sync) and record under `## Verification Evidence` → `### QA Fix Round 4`.

## Acceptance Criteria

- [x] (a) `python3 scripts/prompt-build/assemble_system_prompt.py` output is byte-identical to the pristine pre-task `system-prompt.md` except the version line.
- [x] (b) New `lint_system_prompt_sync` tool correctly reports "in sync" on the true state and correctly detects an artificially introduced fragment mutation as drift.
- [x] (c) Full pytest suite passes with new tests added.
- [x] (d) `project-memory` constraint stored.
- [x] (e) `README.md` and `prompts/README.md` document the new authoring workflow.
- [x] (f) `docs/system-prompt-modularization.md` carries a status note pointing to this task.

## Verification Evidence

- **Test command:** `python3 -m py_compile scripts/prompt-build/split_system_prompt.py scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` then `uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q`
- **Expected result:** py_compile exit 0; pytest all tests pass (exit 0); `diff /tmp/system-prompt.pristine.md /tmp/system-prompt.assembled.md` shows zero differences (pre-bump).
- **Actual result:**
  - Round-trip diff (pre-bump, Step 6): `diff /tmp/system-prompt.pristine.md /tmp/system-prompt.assembled.md` → **zero differences** (both 72,456 bytes; verified byte-identical before the version bump). `diff` exit code 0.
  - Post-bump diff (Step 7): only the `<system_version>` line differs — `<system_version>8.4.5</system_version>` → `<system_version>8.4.6</system_version>`. All 72,456 bytes identical except this single 1-byte substitution.
  - py_compile (Command 6): exit code **0** — all three files compile cleanly.
  - pytest (Command 7): **34 passed, 9 warnings** (31 original + 3 new: `test_system_prompt_split_assemble_round_trip`, `test_lint_system_prompt_sync_clean`, `test_lint_system_prompt_sync_detects_drift`), exit code **0**.
  - `lint_system_prompt_sync` on committed state: `✅ system-prompt.md is in sync with prompts/` (in_sync=True).
  - Drift detection manual verification: mutating `prompts/fragments/03-system_context.md` ("January 2025" → "January 2099") correctly produces `⚠️ DRIFT DETECTED` with a unified-diff summary.
  - **QA Fix Round 1 (new):**
    - py_compile: exit code **0** — all three files compile cleanly.
    - pytest (Command 7): **37 passed, 9 warnings** (34 prior + 3 new: `test_lint_system_prompt_sync_missing_system_prompt_file`, `test_assemble_raises_on_unresolved_placeholder`, `test_split_halts_on_missing_top_level_tag`), exit code **0**.
    - `lint_system_prompt_sync` on committed state: still `✅ system-prompt.md is in sync with prompts/` — assembled `system-prompt.md` bytes unchanged.
  - **QA Fix Round 2 (new):**
    - Test command: `python3 -m py_compile mcp-lint-server/server.py` — exit code **0**.
    - pytest: **38 passed, 9 warnings** (37 prior + 1 new `test_lint_system_prompt_sync_handles_unresolved_placeholder`), exit code **0**.
    - `lint_system_prompt_sync` on committed state: `✅ system-prompt.md is in sync with prompts/` (in_sync=True).
    - `git diff --stat mcp-lint-server/server.py tests/test_mcp_servers.py`:
      ```
       mcp-lint-server/server.py |  9 ++++++++
       tests/test_mcp_servers.py | 54 +++++++++++++++++++++++++++++++++++++++++++++++
       2 files changed, 63 insertions(+)
      ```
      The `except ValueError` catch at `mcp-lint-server/server.py:471` and the new test at `tests/test_mcp_servers.py:1583` were verified present in the working tree (Step 4 confirmation).
  - **QA Fix Round 3 (new):**
    - Test command 1 (`py_compile`): `python3 -m py_compile scripts/prompt-build/split_system_prompt.py scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` → exit code **0**.
    - Test command 2 (pytest): `uv run --with pytest ... pytest tests/ -q` → **42 passed, 9 warnings** (38 prior + 4 new: `test_assemble_rejects_path_traversal_include`, `test_assemble_rejects_malformed_include_marker`, `test_lint_system_prompt_sync_missing_include_file`, `test_lint_system_prompt_sync_invalid_fragments_dir_configuration`), exit code **0**.
    - Test command 3 (fresh current-state assembler diff): `cp system-prompt.md /tmp/system-prompt.current.md && python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/system-prompt.reassembled.md && diff -u /tmp/system-prompt.current.md /tmp/system-prompt.reassembled.md` → **no diff output, exit code 0** (byte-identical; assembled 72,456 bytes).
    - Test command 4 (MCP `lint_system_prompt_sync`): returned exactly `✅ system-prompt.md is in sync with prompts/`.
    - Test command 5 (reference audit): see `### Reference Audit` below.
- **Exit code:** 0 (pytest)

### Reference Audit

Read-only audit of the system-prompt build-process references (Step 7; NO files edited — separate documentation task required if edits are wanted):

1. **Does `AGENTS.md` exist?** ✅ Yes (repo root).
2. **Does `AGENTS.md` mention `system-prompt.md` as generated?** ❌ No — line 29-30 contains the version-bump rule ("Don't edit `system-prompt.md` without updating the version identifier... increment the version inside `<system_version>`...") but the file is NOT described as a generated build artifact.
3. **Does `AGENTS.md` mention `prompts/fragments/`, `prompts/shared/`, `assemble_system_prompt.py`, or `lint_system_prompt_sync`?** ❌ No matches for any of these.
4. **Do `llm.txt` or `llms.txt` exist?** ❌ No — `llm.txt`: FILE NOT FOUND; `llms.txt`: FILE NOT FOUND. (`LLM.txt` — capital-case — DOES exist at repo root and references `system-prompt.md` at lines 84-85, 178, 234, 251 under the pre-modularization direct-copy workflow; it does NOT mention `prompts/fragments/`, `prompts/shared/`, `assemble_system_prompt.py`, or `lint_system_prompt_sync`.)
5. **If they exist, do they mention the new prompt-build workflow?** ❌ No — neither `AGENTS.md` nor `LLM.txt` references the `prompts/` source tree, the assembler script, or the sync lint tool. This is a documentation-gap finding for a follow-up docs task (explicitly OUT OF SCOPE for this task per the Orchestrator).

### QA Fix Round 4

- **Test command 1 (`py_compile`):** `python3 -m py_compile scripts/prompt-build/split_system_prompt.py scripts/prompt-build/assemble_system_prompt.py mcp-lint-server/server.py` → exit code **0**.
- **Test command 2 (targeted new tests, BEFORE fix):** `pytest tests/test_mcp_servers.py::test_assemble_rejects_path_traversal_manifest_entry tests/test_mcp_servers.py::test_assemble_rejects_absolute_manifest_entry tests/test_mcp_servers.py::test_lint_system_prompt_sync_handles_assembler_load_failure -q` → **3 failed** (expected TDD red state — no manifest-entry validation yet; SyntaxError from `_load_assembler` monkeypatch propagated).
- **Test command 3 (targeted new tests, AFTER fix):** same command → **3 passed** (TDD green state).
- **Test command 4 (full suite):** `uv run --with pytest ... pytest tests/ -q` → **45 passed, 9 warnings** (42 prior + 3 new), exit code **0**. NOTE: an intermediate run after Step 5/6 showed 7 failures (`NameError: name '_resolve_includes' is not defined` — an editing regression where the `def _resolve_includes(...)` signature was accidentally swallowed by the `_safe_fragment_path` insertion); it was caught by the verification gate and repaired in the same round (function signature restored, full suite 45/45).
- **Test command 5 (fresh current-state assembler diff):** `cp system-prompt.md /tmp/system-prompt.current.md && python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/system-prompt.reassembled.md && diff -u /tmp/system-prompt.current.md /tmp/system-prompt.reassembled.md` → **no diff output, exit code 0** (byte-identical; assembled 72,456 bytes).
- **Test command 6 (MCP `lint_system_prompt_sync`):** returned exactly `✅ system-prompt.md is in sync with prompts/`.

## Risk & Rollback

- **Risk:** a bug in the split/assemble scripts could silently change what gets pasted into chat interfaces in future sessions, altering model behavior. Mitigation: the round-trip diff check in Step 6 is a hard gate — any unexpected difference HALTS the task before `system-prompt.md` is overwritten. Rollback: trivial, since ZAC means nothing is committed without Manager approval; discard the working tree changes if verification fails.

---

## Execution Log & Reasoning

### Architecture & Design Decisions

**1. Top-level tag parsing strategy.** `system-prompt.md` uses XML-like tags, but naive column-0 detection fails because `<brainstorming_protocol>` contains nested column-0 block tags (`<workflow>`, `<personas>`, `<output_schema>`, etc.) and `<personas>` recurs at column 0 both as a top-level tag (line 262) and nested inside `<brainstorming_protocol>` (line 560). Resolution: the 20 expected top-level tag names are listed explicitly and in document order in `TOP_LEVEL_TAGS`. For each, the script finds the first column-0 opening line `<tag>` after the previous block, then the first `^\s*</tag>\s*$` closing line (any indentation, since some nested closers like `  </operating_principles>` are indented). This deterministically isolates exactly the 20 top-level blocks and verifies their order.

**2. Separator handling.** Verified programmatically that every pair of consecutive top-level blocks is separated by exactly one blank line, and the file ends with exactly one trailing newline. Therefore: fragments are joined with `'\n\n'` and terminated with `'\n'`, reproducing the pristine structure byte-for-byte (confirmed by the round-trip diff).

**3. Fragment content.** Each fragment file contains the full block text (`<tag>` through `</tag>` inclusive, verbatim) with NO trailing newline — the assembler's `'\n\n'` join plus final `'\n'` reproduces the exact separators. Writing a trailing newline into fragment files would create a spurious blank line on reassembly.

**4. Validation-phase shared file (design decision vs. task's canonical text).** The task specifies the `<validation_phase>` block (duplicated 3× in `hands_protocols`) be extracted into `prompts/shared/validation-phase.md` with `{{NEXT_PHASE}}` as a placeholder, and each occurrence replaced by an `<!--INCLUDE:...-->` marker that replaces the ENTIRE `<validation_phase>...</validation_phase>` block (inclusive of wrapper tags). The task's canonical content omits the wrapper tags and indentation for readability. However, the **hard acceptance criterion (a)** requires byte-identical reassembly. Since the include marker replaces the whole block (including the `  <validation_phase>` and `  </validation_phase>` wrapper lines and their 2/4-space indentation), the shared file MUST reproduce the full block verbatim (wrappers + indentation) with only the phase name parameterized. The split script extracts the actual block bytes from the file and substitutes `{{NEXT_PHASE}}` for the phase name, guaranteeing the shared file's content matches the original block exactly. Verified: the three block occurrences are byte-identical except the final line's phase name (Context/Context/Discovery).

**5. Assembler include resolution.** The `<!--INCLUDE:path|PARAM=value-->` format is resolved by reading the shared file (path relative to `prompts/`), substituting each `{{PARAM}}` placeholder with its value, and replacing the marker text with the result. The shared file content is inserted AS-IS (no stripping) so indentation and wrapper tags are preserved.

**6. Version bump workflow.** The `<system_version>` tag lives in fragment `01-system_version.md`. The version is bumped there (8.4.5 → 8.4.6) and the assembler regenerates `system-prompt.md`. The round-trip gate (Step 6) was run BEFORE the bump and passed with zero differences; the post-bump diff confirms only the version line changed.

**7. Lint tool design.** `lint_system_prompt_sync()` imports the assembler via `importlib` (no package dependency, matching the test-file import pattern), assembles to a temp file, and diffs against the committed `system-prompt.md`. An internal `_check_system_prompt_sync(...)` helper accepts custom paths for testability (the round-trip and drift tests use temp directories). Covered by the existing `"lint_*": "allow"` permission rule in `opencode.json` — no permissions change needed.

### Tag Boundaries Used for Extraction

The 20 top-level tags and their line ranges (1-indexed) in the pristine `system-prompt.md`:

| #  | Tag                          | Lines    |
|----|------------------------------|----------|
| 1  | system_version               | 1–1      |
| 2  | role                         | 3–10     |
| 3  | system_context               | 12–15    |
| 4  | manager_profile              | 17–163   |
| 5  | ai_objective                 | 165–167  |
| 6  | operating_principles         | 169–180  |
| 7  | delegation_strategy          | 182–184  |
| 8  | challenge_policy             | 186–188  |
| 9  | leadership_and_language_protocol | 190–198 |
| 10 | agent_skills_registry        | 200–237  |
| 11 | user_input_processing        | 239–260  |
| 12 | personas                     | 262–315  |
| 13 | agentic_reasoning            | 317–363  |
| 14 | hands_protocols              | 365–531  |
| 15 | execution_workflow           | 533–552  |
| 16 | brainstorming_protocol       | 554–606  |
| 17 | constraints                  | 608–626  |
| 18 | solid_programming_mandate    | 628–645  |
| 19 | universal_datetime_rules     | 647–668  |
| 20 | initialization               | 670–672  |

### Validation-Phase Verification

All 3 `<validation_phase>` block occurrences are byte-identical except the final line's phase name:
- Occurrence 1 (inside `<hands_discovery_task_template>`): "proceed to the **Context** Phase."
- Occurrence 2 (inside `<hands_implementation_task_template>`): "proceed to the **Context** Phase."
- Occurrence 3 (inside `<hands_combined_task_template>`): "proceed to the **Discovery** Phase."

This matches the task's expectation exactly (two "Context", one "Discovery"). The shared file preserves the full block (with `  <validation_phase>` / `  </validation_phase>` wrapper tags and 2/4-space indentation) with `{{NEXT_PHASE}}` substituting the phase name. Include markers in `prompts/fragments/14-hands_protocols.md` (lines 6, 40 = `NEXT_PHASE=Context`; line 110 = `NEXT_PHASE=Discovery`).

### Round-Trip Diff Result

```
Pre-bump:  diff /tmp/system-prompt.pristine.md /tmp/system-prompt.assembled.md → (no output, identical)  [exit 0]
Post-bump: diff /tmp/system-prompt.pristine.md system-prompt.md →
  1c1
  < <system_version>8.4.5</system_version>
  ---
  > <system_version>8.4.6</system_version>
  [exit 1 — expected; only the version line differs]
```

### Files Created

- `scripts/prompt-build/split_system_prompt.py` — disassembler (parses 20 top-level tags, extracts validation-phase shared partial).
- `scripts/prompt-build/assemble_system_prompt.py` — assembler (reads manifest, concatenates fragments, resolves include markers).
- `prompts/fragments/01-system_version.md` … `20-initialization.md` (20 files).
- `prompts/shared/validation-phase.md` — shared partial with `{{NEXT_PHASE}}` placeholder.
- `prompts/manifest.txt` — ordered fragment list.
- `prompts/README.md` — authoring workflow guide.

### Files Modified

- `system-prompt.md` — regenerated (version 8.4.5 → 8.4.6; byte-identical otherwise).
- `prompts/fragments/01-system_version.md` — version bumped.
- `mcp-lint-server/server.py` — added `lint_system_prompt_sync()` tool + `_check_system_prompt_sync()` helper + `_load_assembler()` helper.
- `tests/test_mcp_servers.py` — added 3 regression tests (34 total).
- `README.md` — updated repo structure tree, system-prompt.md description, and "Customizing for Yourself" section.
- `docs/system-prompt-modularization.md` — added status note pointing to Task 99.
- `CHANGELOG.md` — added v8.4.6 entry.

### QA Fix Round 1 (V1 + V2)

**V1 — Missing `system-prompt.md` file guard in `_check_system_prompt_sync()`.**  
QA finding: `_check_system_prompt_sync()` called `Path(system_prompt_path).read_text()` without first checking `Path(system_prompt_path).is_file()`. If the file was missing (e.g., in a test scenario or if accidentally deleted), a raw `FileNotFoundError` would propagate out of the function, crashing the lint tool instead of returning a clean `(False, "Error: File not found: ...")` tuple. This violated the established pattern in the same file — `lint_markdown()` and `lint_task_file()` both guard with `if not path.is_file(): return f"Error: File not found: {file_path}"` before reading.  
Fix: Added an existence guard at the start of `_check_system_prompt_sync()` that mirrors the existing pattern — `if not sp_path.is_file(): return False, f"Error: File not found: {system_prompt_path}"`. Regression test `test_lint_system_prompt_sync_missing_system_prompt_file` verifies the guard returns `(False, "not found")` without raising.

**V2 — Silent pass-through of unresolved `{{PLACEHOLDER}}` in `assemble_system_prompt.py`.**  
QA finding: After `_resolve_includes()` substituted known `{{PARAM}}` placeholders, any remaining `{{PLACEHOLDER}}` (e.g., from a shared partial whose parameter was never supplied by an include marker) would pass through silently. The assembled `system-prompt.md` would contain literal `{{FOO}}` text — a silent data corruption.  
Fix: Added a per-fragment post-resolution scan using regex `\{\{[A-Z_][A-Z0-9_]*\}\}`. If any unresolved placeholder remains, `assemble()` raises `ValueError` naming the fragment and the offending placeholder (e.g., `"Unresolved placeholder {{FOO}} in fragment 01-test.md — an include marker is missing a required PARAM."`). This is a loud, named failure rather than silent corruption. Regression test `test_assemble_raises_on_unresolved_placeholder` constructs a temp fragment with an unresolved `{{FOO}}` and asserts the `ValueError` with the placeholder name.

**Step 5 (optional) — Split halts on missing top-level tag.**  
Added regression test `test_split_halts_on_missing_top_level_tag`: strips `<ai_objective>...</ai_objective>` from a pristine `system-prompt.md` copy, runs `split_system_prompt()`, and asserts `SystemExit` with code 1 (the `_halt()` contract). This guards against a future regression where a missing top-level tag would be silently skipped instead of halting.

All three new regression tests pass (34 → 37 total). `lint_system_prompt_sync` still reports clean — the assembled `system-prompt.md` is byte-identical to before the fix round (only the version line differs from the pre-task pristine file).

### Files Modified (QA Fix Round 1)

- `mcp-lint-server/server.py` — added existence guard in `_check_system_prompt_sync()`.
- `scripts/prompt-build/assemble_system_prompt.py` — added unresolved-placeholder check in `assemble()`.
- `tests/test_mcp_servers.py` — added 3 regression tests (`test_lint_system_prompt_sync_missing_system_prompt_file`, `test_assemble_raises_on_unresolved_placeholder`, `test_split_halts_on_missing_top_level_tag`).
- `CHANGELOG.md` — updated v8.4.6 entry with QA Fix Round 1 fixes.

### QA Fix Round 2 (ValueError catch composition gap)

**The finding (empirically reproduced, then reconfirmed).** The QA Engineer
reported that `_check_system_prompt_sync()` still had a composition gap: while
round 1 made `assemble()` raise `ValueError` for an unresolved placeholder (a
loud, named failure for CLI/direct callers), the lint server's
`_check_system_prompt_sync()` only caught `FileNotFoundError` around the
`assembler.assemble(...)` call. If the fragment tree contained an unresolved
`{{PLACEHOLDER}}`, the `ValueError` would propagate out of the diagnostic tool
and crash the lint tool. The finding was empirically reproduced by running
`_check_system_prompt_sync()` against a temp fragments/shared/manifest tree
with an unresolved `{{FOO}}` — the `ValueError` propagated. The state was
reconfirmed as unaddressed after a full round-trip where no change was applied
to the file (identical working-tree diff for `mcp-lint-server/server.py`).

**The fix (one line + comment + regression test).** In `mcp-lint-server/server.py`,
widened the exception handling around `assembler.assemble(...)` inside
`_check_system_prompt_sync()` to also catch `ValueError`, returning a clean
`(False, f"Error: {e}")` tuple. The `FileNotFoundError` branch keeps its exact
wording (`"Error: Fragment or manifest file not found: ..."`). Because this is
a diagnostic tool that must degrade gracefully, catching the intentional
`ValueError` from the assembler's placeholder guard and surfacing it as an
error string (still naming the offending fragment + placeholder) is the correct
behavior — it does NOT change `assemble()`'s own loud behavior for CLI callers.

**Regression test added.** `test_lint_system_prompt_sync_handles_unresolved_placeholder`
reuses the same temp fixture shape as `test_assemble_raises_on_unresolved_placeholder`
(a fragment with an include marker + a shared partial with unresolved `{{FOO}}`),
but calls `_check_system_prompt_sync()` and asserts it returns `(False, <message>)`
without raising, and that the message identifies the placeholder.

Full suite: **38 passed** (37 prior + 1 new), exit code 0. `lint_system_prompt_sync`
still reports `✅ in sync` — the assembled `system-prompt.md` bytes are unchanged.

### Files Modified (QA Fix Round 2)

- `mcp-lint-server/server.py` — widened exception handling in `_check_system_prompt_sync()` to catch `ValueError` (in addition to `FileNotFoundError`).
- `tests/test_mcp_servers.py` — added `test_lint_system_prompt_sync_handles_unresolved_placeholder`.
- `CHANGELOG.md` — updated v8.4.6 entry with QA Fix Round 2 fixes.

### QA Fix Round 3 (include-path safety, malformed markers, lint diagnostics)

**1. Path-traversal fix (`_safe_include_path`).** The assembler's include
markers were resolved as `prompts_dir / rel_path` with no containment check.
A marker like `<!--INCLUDE:../outside.md-->` would resolve to a sibling of
`prompts/` and read an arbitrary file from outside the prompt source tree. The
new private helper `_safe_include_path(rel_path, prompts_dir)` enforces the
security boundary:
- **Absolute include paths are rejected outright** — only relative paths are
  part of the include API.
- The candidate is resolved via `Path.resolve()` (collapsing `..` segments,
  symlinks, redundant separators).
- The resolved path MUST remain inside the resolved `prompts_dir` — otherwise
  `ValueError` is raised naming the offending include path. This mirrors the
  path-traversal-prevention pattern already used by the `custom_context` MCP
  server. The helper is invoked at the top of `_resolve_includes()` before any
  file read.

**2. Malformed/unresolved include-marker detection.** A marker with a broken
closing sequence (e.g. `<!--INCLUDE:shared/test.md|NEXT_PHASE=Context--!>`)
does not match `_INCLUDE_RE`, so `_resolve_includes()` cannot resolve it and
the literal marker text would silently leak into the generated
`system-prompt.md`. After `_resolve_includes()` returns for each fragment, the
assembler now checks for the literal substring `<!--INCLUDE:`; if found it
raises `ValueError` identifying the fragment and stating the marker is
unresolved/malformed. This check runs BEFORE the unresolved-placeholder check
so a marker problem is diagnosed as such rather than misreported as a missing
placeholder parameter.

**3. Lint diagnostic exception hardening.** `_check_system_prompt_sync()` is a
diagnostic tool exposed over the MCP lint server — it must never crash with an
unhandled exception. Round 2 caught `FileNotFoundError` + `ValueError` around
the assembler call, but other failure modes could still propagate: a regular
file passed as `fragments_dir` raises `NotADirectoryError`; a missing shared
include file raises `FileNotFoundError` on read; a permission error or any
other unexpected exception from assembly, temp-file reading, committed-file
reading, or diff generation would crash the server. The function now wraps the
whole post-guard region in a broad `except Exception` (which deliberately does
NOT catch `SystemExit`/`KeyboardInterrupt`, since both derive from
`BaseException`) returning `(False, f"Error: {e}")`, with temporary-file
cleanup preserved in the `finally` block. The two specific
`FileNotFoundError`/`ValueError` clauses keep their exact message wording;
`assemble()` itself is NOT weakened — it still fails loudly for direct CLI
callers.

**4. New regression tests (4 added; 38 → 42 total).**
- `test_assemble_rejects_path_traversal_include` — temp prompt tree with
  `outside.md` outside `prompts/`, fragment with `<!--INCLUDE:../outside.md-->`;
  asserts `ValueError` naming the unsafe path.
- `test_assemble_rejects_malformed_include_marker` — fragment with
  `<!--INCLUDE:shared/test.md|NEXT_PHASE=Context--!>`; asserts `ValueError`
  identifying the fragment + malformed/unresolved marker.
- `test_lint_system_prompt_sync_missing_include_file` — valid-looking marker
  pointing to a non-existent shared file; asserts `(False, message)` without
  raising and that the message identifies the missing file/include failure.
- `test_lint_system_prompt_sync_invalid_fragments_dir_configuration` — a
  regular file passed as `fragments_dir`; asserts `(False, message)` without
  raising.

**5. Reference-audit results (read-only).** `AGENTS.md` exists and contains
the `system-prompt.md` version-bump rule but does NOT describe the file as a
generated artifact and does NOT mention `prompts/fragments/`,
`prompts/shared/`, `assemble_system_prompt.py`, or `lint_system_prompt_sync`.
`llm.txt` and `llms.txt` do NOT exist; the capital-case `LLM.txt` exists but
references only the pre-modularization direct-copy workflow. This is a
documentation gap recorded for a separate follow-up docs task — explicitly OUT
OF SCOPE here per the Orchestrator.

**6. Verification summary.** py_compile exit 0; pytest 42/42 exit 0; fresh
assembler diff exit 0 (byte-identical, 72,456 bytes); `lint_system_prompt_sync`
returns `✅ system-prompt.md is in sync with prompts/`.

### Files Modified (QA Fix Round 3)

- `scripts/prompt-build/assemble_system_prompt.py` — added `_safe_include_path()` + malformed-marker detection guard.
- `mcp-lint-server/server.py` — hardened `_check_system_prompt_sync()` with broad `except Exception` diagnostic handler.
- `tests/test_mcp_servers.py` — added 4 regression tests (38 → 42).
- `prompts/README.md` — added include-path safety note.
- `CHANGELOG.md` — updated v8.4.6 entry with QA Fix Round 3 fixes.

### QA Fix Round 4 (manifest-path safety, assembler-load hardening)

**1. Manifest-path traversal fix (`_safe_fragment_path`).** The assembler read
fragment files via `frag_dir / filename` with no containment check on manifest
entries. A manifest entry like `../outside.md` — or an absolute path to an
arbitrary host file — would resolve outside `prompts/fragments/` and be read
and inlined into the generated `system-prompt.md`. The new private helper
`_safe_fragment_path(filename, fragments_dir)` enforces the same trust
boundary that round 3 added for include paths:
- Empty manifest entries (after stripping) are rejected — a blank manifest line
  is a configuration error, not something to silently skip.
- Absolute manifest entries are rejected — the manifest API only contains
  filenames relative to `fragments_dir`.
- The candidate is resolved via `Path.resolve()` (collapsing `..`, symlinks,
  redundant separators) and MUST remain inside the resolved `fragments_dir` —
  otherwise `ValueError` names the unsafe entry. The helper is invoked inside
  `assemble()` before every fragment read.

**2. Manifest as an untrusted input surface.** The manifest is machine-authored
(from skills, user paste operations, generated content) and is therefore an
untrusted input surface, exactly like include markers. The docstring/comments
on `_safe_fragment_path` document this threat model explicitly so a future
editor does not strip the guard as redundant.

**3. Assembler-load exception hardening.** `_load_assembler()` dynamically
executes Python source from `scripts/prompt-build/assemble_system_prompt.py`
via importlib. If that file is corrupted or edited into a broken state,
`exec_module()` can raise `SyntaxError`/`IndentationError`/`ImportError` — not
just `FileNotFoundError`. The lint server's `_check_system_prompt_sync()` now
keeps the specific `FileNotFoundError` handler (preserving its exact message)
and adds a generic `except Exception` handler returning `(False, f"Error: {e}")`
for all other load failures. `except Exception` deliberately does NOT catch
`SystemExit`/`KeyboardInterrupt` (both derive from `BaseException`).

**4. New regression tests (3 added; 42 → 45 total).**
- `test_assemble_rejects_path_traversal_manifest_entry` — manifest with
  `../outside.md`; asserts `ValueError` naming the unsafe manifest entry.
- `test_assemble_rejects_absolute_manifest_entry` — manifest with the absolute
  path of a file outside `fragments/`; asserts `ValueError` naming the unsafe
  absolute entry.
- `test_lint_system_prompt_sync_handles_assembler_load_failure` — monkeypatches
  `_load_assembler` to raise `SyntaxError("synthetic assembler load failure")`;
  asserts `(False, message)` without raising and that the message identifies
  the load failure.

**5. TDD flow honored.** All 3 new tests were run BEFORE the fix and confirmed
FAILING (red), then re-run after the fix and confirmed PASSING (green).

**6. Regression caught by the verification gate.** After Steps 5–6 the full
suite reported 7 failures (`NameError: name '_resolve_includes' is not
defined`) — the `_safe_fragment_path` insertion had accidentally swallowed the
`def _resolve_includes(...)` function signature, leaving its docstring dangling.
Caught by `verification-before-completion`; the signature line was restored and
the full suite re-passed 45/45. This is exactly why the gate exists.

**7. Verification summary.** py_compile exit 0; targeted tests 3/3 failed
pre-fix → 3/3 passed post-fix; full suite 45/45 exit 0; fresh assembler diff
exit 0 (byte-identical, 72,456 bytes); `lint_system_prompt_sync` returns
`✅ system-prompt.md is in sync with prompts/`. The assembled `system-prompt.md`
bytes were NOT changed by this round.

### Files Modified (QA Fix Round 4)

- `scripts/prompt-build/assemble_system_prompt.py` — added `_safe_fragment_path()`; used inside `assemble()` before each fragment read.
- `mcp-lint-server/server.py` — hardened `_load_assembler()` exception handling with generic `Exception` handler.
- `tests/test_mcp_servers.py` — added 3 regression tests (42 → 45).
- `prompts/README.md` — added manifest-entry safety note.
- `CHANGELOG.md` — updated v8.4.6 entry with QA Fix Round 4 fixes.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `cb1c423d2fd9c709b4a60ea4bc35fc272900f277`
<!-- END_GIT_DIFF -->