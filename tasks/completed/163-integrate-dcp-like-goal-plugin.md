# Task 163: Integrate DCP Dynamic Context Pruning Like Goal Plugin

**File:** `tasks/completed/163-integrate-dcp-like-goal-plugin.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Integrate @tarquinen/opencode-dcp dynamic context pruning plugin across project + global, mirroring the @prevalentware/opencode-goal-plugin pattern (opencode.json + tui.json parity + LLM.txt + verification).

## Manager's Notes

Manager request: read https://github.com/Opencode-DCP/opencode-dynamic-context-pruning then add to project (LLM.txt + other places), create task, install globally. Approved to mirror goal-plugin setup across project and globally. DCP upstream notes development slowed, recommends Sleev for fresh starts — Manager still approved DCP. Goal-plugin pattern discovered in Task 126: plugin array in opencode.json + tui.json identical, LLM.txt §7 JSON example + TUI parity block, no system-prompt.md change.

## Local TODOs

- [x] Verify goal-plugin parity files (opencode.json, tui.json, LLM.txt §7)
- [x] Add @tarquinen/opencode-dcp to project opencode.json + tui.json plugin arrays
- [x] Update LLM.txt §7 JSON example, TUI parity block, verification checklist, DCP config docs
- [x] Install DCP globally via opencode plugin command + verify
- [x] Update CHANGELOG.md via Parse-Then-Append
- [x] Verify functionality

## Acceptance Criteria

- [x] Project opencode.json plugin array contains both @prevalentware/opencode-goal-plugin and @tarquinen/opencode-dcp
- [x] Project tui.json plugin array contains both plugins (parity with global)
- [x] LLM.txt documents DCP install, dcp.jsonc config (global + project override), commands (/dcp, /dcp-compress), verification checklist updated
- [x] Global ~/.config/opencode/opencode.json + tui.json contain both plugins
- [x] DCP installed globally and loads without opencode startup failure

## Verification Evidence

- **Test command:** `grep -q "@tarquinen/opencode-dcp" opencode.json && echo "project opencode.json DCP ✓"; grep -q "@tarquinen/opencode-dcp" tui.json && echo "project tui.json DCP ✓"; grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "global opencode.json DCP ✓"; grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json && echo "global tui.json DCP ✓"; opencode mcp list 2>&1 | head -20`
- **Expected result:** All 4 DCP checks print ✓, mcp list shows custom_context/project_memory/lint connected, opencode starts without ConfigInvalidError
- **Actual result:** All 4 DCP checks print ✓; `diff -q tui.json ~/.config/opencode/tui.json` in sync ✓; project + global JSON valid; `pytest tests/ -q` 55 passed; `opencode mcp list` shows custom_context/project_memory/lint/blowsh connected (telegram timeout pre-existing, unrelated); `~/.config/opencode/dcp.jsonc` auto-created on install
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** DCP upstream slowed, recommends Sleev; AGPL-3.0 license; plugin could break opencode startup if shape wrong; global opencode.json blind-copy breaks relative vs absolute MCP split
- **Rollback plan:** Remove @tarquinen/opencode-dcp from 4 plugin arrays, `opencode plugin remove @tarquinen/opencode-dcp` or manual JSON revert, restart opencode, verify goal plugin still loads

---

## Execution Log & Reasoning

D1: Mirrored goal-plugin pattern exactly (Task 126): plugin arrays identical project+global, no system-prompt.md change, LLM.txt §7 + verification + new §7.7 DCP docs.
D2: Used official installer `opencode plugin @tarquinen/opencode-dcp@latest --global` (exit 0) instead of manual JSON edit for global — installer reformatted global tui.json multi-line, so normalized project tui.json + opencode.json to multi-line `@latest` for `diff -q` parity.
D3: Removed stray `.opencode/opencode.json` (`{"plugin":["list"]}`) created by mistaken `opencode plugin list` invocation — `list` is not a subcommand, installer treats arg as plugin name. No other side effects.
F1: Project files changed: opencode.json (plugin +DCP), tui.json (plugin +DCP, multi-line), LLM.txt (§7 JSON, TUI block, Option A note, new §7.7, verification checklist), CHANGELOG.md Unreleased entry.
F2: Global state: ~/.config/opencode/opencode.json + tui.json both contain goal + DCP@latest, dcp.jsonc auto-created with $schema only (defaults applied automatically).
R1: Upstream slowed, recommends Sleev — documented in LLM.txt §7.7, Manager approved DCP anyway. AGPL-3.0 is usage (plugin), not vendored code.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `7a97bbb2947d3a04b49ddedb007d3ecd5b46dccc`
<!-- END_GIT_DIFF -->
