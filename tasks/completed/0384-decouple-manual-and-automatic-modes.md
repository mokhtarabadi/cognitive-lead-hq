# Task 0384: Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)

**File:** `tasks/completed/0384-decouple-manual-and-automatic-modes.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-08T07:05:25Z
**Submitted:** 2026-11-08T06:17:35Z

## Goal

The repository currently suffers from a fundamental conflation between two operating topologies:

1. **Topology A: True Manual Mode (`MODE: manual`)** — The Orchestrator (Brain) runs in an external chat window (e.g. Claude Web, ChatGPT), completely disconnected from the local filesystem and terminal. There is NO `mcp-brain-bridge` communication between Hands and Brain. The Manager is the explicit human courier. Hands outputs next-stage prompts and task paths in fenced Markdown blocks. The Manager copies them to the external Brain, and copies the Brain's fenced XML back to the Hands.

2. **Topology B: True Automatic Mode (`MODE: automatic` / `MODE: autopilot`)** — OpenCode runs with the `mcp-brain-bridge` MCP server active. The Hands calls `tools.brain.brain_turn` directly. The Manager is supervisor and approval gatekeeper only (plan approval and closure approval). No copy-paste instructions or fenced handoff prompts may be generated.

The bug: In version 9.71.0 (ADR `Hands-driven QA/review chaining in both modes`), the prompt was altered to state: "The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text." This completely broke the external web chat workflow.

## Manager's Notes (verbatim, typos corrected)

سوال آیا حالت دستی و حالت خودکار که تعریفشان پایین‌تر هست درست از هم جدا شده‌اند؟

حالت دستی من یعنی مدیر پل بین brain و hands هستم من کپی و پست می‌کنم. برین باید در انتهای کار به hands بگه که مسیر فایل تسک که همه چی توش inject شده رو به همراه پرامپت مورد نیاز که توی fenced نوشته شده به brain خارجی بده مانند نمونه:

`[QA Engineer], please perform adversarial testing.`
`[Code Reviewer], please perform the final review.`
`A context report is provided in the Context Report section below. Please review it in full before generating any task or blueprint — it contains the authoritative project context gathered by the Hands.`

و من کپی می‌کنم و برین میدم و دوباره xml خروجی برین رو کپی می‌کنم میدم به hands.

و حالت اتوماتیک که brain mcp پل واسط برین و hands هسته و این دوتا ۱۰۰ درصد خودکار با هم کار می‌کنن توی این جالت دیگه نباید پرامت های بالا ایجاد بشه. مثلا نباید بگیم که manager copy following یا هرچیزی باید بگیم hands از brain turn استفاده کن و از qa بپرس و اون خودش پرامت میزنه و brain turn میکنه و خروجی xml یا چیز دیگه رو میبینه.

یه تسک بساز و عین کلمات من رو داخلش بنویس و فایل های مربوطه رو با code-search پیدا کن و اونا رو هم داخلشون reference کن میخوام با کمک برین بیرونی حلش کنیم.

## Impacted Files & Exact Grounded Citations

The following files contain conflated definitions and require targeted refactoring:

1. `prompts/fragments/02-role.md`:
   - Lines 3-6: Erroneously asserts that the Hands coordinates via `mcp-brain-bridge` in *both* manual and automatic modes and forbids the courier role universally.

2. `prompts/fragments/06-personas.md`:
   - Senior Programmer (line 17): Fenced XML is emitted for manual mode, but lines 50 (QA) and 56 (Reviewer) state the Hands calls the Brain directly in both modes.
   - QA Engineer & Code Reviewer: Must conditionally branch: in `manual` mode, instruct Hands to emit the fenced handoff prompt for the Manager; in `automatic` mode, invoke `brain_turn` directly.

3. `prompts/fragments/09-hands_protocols.md`:
   - Discovery Summary Phase: Must emit the copy-paste prompt block for the Manager when in `manual` mode, instead of only mentioning `brain_turn`.
   - Implementation & Combined Summary Phases: Must cleanly separate:
     - Manual Mode: Emit task path, diff status, and exact next persona prompt in a fenced block for Manager ferrying.
     - Automatic Mode: Hands invokes QA/review `brain_turn` autonomously without copy-paste text.

4. `prompts/fragments/19-initialization.md`:
   - Line 2: Redefine `MODE: manual` (Manager is courier between external Brain and Hands) vs `MODE: automatic` (Hands and Brain coordinate directly via `mcp-brain-bridge`).

5. `agents/cognitive-executor.md`:
   - Section "Manual Workflow" (lines 456-474): Must restore the copy-paste courier instructions when working without `brain_turn`.
   - Section "Mode line" (lines 499-504): Reconcile the manual mode line instructions.
   - Section "Modes: manual vs autopilot" (lines 587-596): Clarify the courier boundary.

6. `agents/DECISIONS.md`:
   - Append an Architectural Decision Record (ADR) documenting the separation of True Manual Mode from Automatic Mode.

7. `AGENTS.md`:
   - Lines 31-32 & 147: Clarify that the "no-ferrying" rule applies strictly to `automatic` mode with `mcp-brain-bridge`, whereas `manual` mode explicitly relies on Manager courier ferrying.

8. `README.md`:
   - Align the Manual Mode documentation with the two distinct operational scenarios.

9. `tests/test_prompt_sync.py`:
   - Update assertions that previously enforced "no Manager-ferries-task-text" in manual mode, ensuring the test suite validates the dual-mode separation correctly.

10. `system-prompt.md`:
    - Reassemble from updated fragments with bumped version in `prompts/fragments/01-system_version.md`.

## Local TODOs

- [ ] Refactor `prompts/fragments/02-role.md` and `prompts/fragments/19-initialization.md` to define `MODE: manual` as external Brain with Manager courier, and `MODE: automatic` as autonomous MCP bridge execution.
- [ ] Refactor `prompts/fragments/06-personas.md` (Senior Programmer, QA Engineer, Code Reviewer) so that in `manual` mode, the Brain instructs Hands to emit fenced handoff blocks for the Manager, while in `automatic` mode, Hands invokes `brain_turn` directly.
- [ ] Refactor `prompts/fragments/09-hands_protocols.md` summary phases across discovery, implementation, and combined task templates to provide explicit, clean branching for manual vs automatic execution.
- [ ] Refactor `agents/cognitive-executor.md` and `AGENTS.md` to restore the manual courier handoff protocol while preserving zero-ferrying in automatic/autopilot mode.
- [ ] Update synchronization tests in `tests/test_prompt_sync.py` to lock both modes against regressions.
- [ ] Append ADR in `agents/DECISIONS.md` and `prompts/fragments/DECISIONS.md`, bump version in `01-system_version.md`, and run `python scripts/prompt-build/assemble_system_prompt.py`.

## Acceptance Criteria

- [x] Verbatim Manager input is permanently preserved in the task file.
- [x] Manual Mode is explicitly documented as the human-in-the-loop copy-paste courier workflow for external Brains.
- [x] Automatic Mode is explicitly documented as the headless MCP-driven workflow via `mcp-brain-bridge`.
- [x] All 10 referenced files are updated, synchronized, and verified via tests.

## Verification Evidence

- **Test command:** pytest tests/test_prompt_sync.py
- **Expected result:** All tests pass exit code 0
- **Actual result:** 823 passed
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** [what could go wrong]
- **Rollback plan:** [how to undo if needed]

---

## Execution Log & Reasoning

### 2026-11-08: Dual-Mode Topology Separation

- Refactored `prompts/fragments/02-role.md` and `19-initialization.md` to establish clean separation between True Manual Mode (External Brain / Manager Courier) and Automatic Mode (MCP Brain Bridge).
- Updated `prompts/fragments/06-personas.md` (QA Engineer, Code Reviewer) with explicit courier handoff prompts in manual mode while maintaining direct `brain_turn` invocation in automatic mode.
- Cleaned `prompts/fragments/09-hands_protocols.md` implementation and combined task summary templates, removing contradictory legacy phrases and nesting completion messages under their respective modes.
- Updated `agents/cognitive-executor.md`, `AGENTS.md`, and `README.md` to document the restored manual courier workflow.
- Appended ADRs to `agents/DECISIONS.md` and `prompts/fragments/DECISIONS.md`, and logged version 9.76.0 in `CHANGELOG.md`.
- Added `test_dual_mode_topology_separation` to `tests/test_prompt_sync.py` and rebuilt `system-prompt.md` via `assemble_system_prompt.py`.

### 2026-11-08: O1 Hotfix — Remove Duplicate Contradiction

- Removed duplicate legacy item 2 from `prompts/fragments/09-hands_protocols.md` under automatic mode.
- Recompiled `system-prompt.md` via `assemble_system_prompt.py`.
- Added `test_dual_mode_topology_separation` to `tests/test_prompt_sync.py`.
- All unit and prompt synchronization tests pass cleanly.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `765e52bd5054f858b242604915a7da221ffd6e1c`
<!-- END_GIT_DIFF -->
