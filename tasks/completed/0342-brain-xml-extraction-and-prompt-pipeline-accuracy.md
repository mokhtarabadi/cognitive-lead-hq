# Task 342: Brain XML extraction and prompt-pipeline accuracy

**File:** `tasks/completed/0342-brain-xml-extraction-and-prompt-pipeline-accuracy.md`
**Source:** manager
**Type:** bugfix
**Status:** closed
**Estimate:** 2h
**Sprint:** S26-W43
**Milestone:** M01

## Goal

Make the Brain bridge accept every legitimate XML shape exactly once — bare, three-backtick and four-backtick `xml` fences, bodies carrying their own Python/JS/diff samples, and Markdown documents — and restore the prompt build pipeline so a rebuild reproduces the shipped system prompt byte for byte. A correct Brain answer must never cost a re-emit, and a documentation sample must never execute as an instruction.

## Manager's Notes

- Trigger: the 0339 implementation turn was rejected as `XML_STRICT_REJECT_FENCE_FALLBACK` after the Brain fenced a `hands_implementation_task` whose `<execution_phase>` carried ` ```python ` samples. 25,503 characters were withheld and the block had to be re-emitted in a second turn.
- "Fix it without a task" was the first order; this task was created afterwards to carry the changes, on the condition that they do not overlap task 339 (they don't: planner vs brain/prompts, only `CHANGELOG.md` is shared).

## Findings

- **F1.** `_XML_FENCE_RE` could not nest, so an ` ```xml ` body containing its own fence was closed early; the truncated body tripped the unclosed-tail check and rejected the whole turn.
- **F2.** The bare-block scan ran on `_strip_fences` output, whose non-nesting strip mis-slices the same body, so an operator-shaped literal inside a documentation sample was returned as a real block while the real one was dropped (false positive, worse than F1).
- **F3.** Four-backtick ````xml is the canonical CommonMark wrapper for a body carrying fences, and the extractor ignored it entirely.
- **F4.** `split_system_prompt.py` knew 20 top-level tags: `<night_mode>` and the trailing Markdown language-policy section were dropped on rebuild, and every fragment was renumbered. `test_system_prompt_split_assemble_round_trip` was failing before this task.
- **F5.** Prompt and executor text disagreed with the gateway: the reject hint said "re-emit bare unfenced XML" although manual mode forces a fence, and the executor claimed a missing mode line "fence-strict-rejects".

## Local TODOs

- [x] Step 1: Replace fence regex with the line-accurate `_xml_fence_segments` scanner (3+ backticks, close only on a bare run of at least the opener's length)
- [x] Step 2: Add `_extract_complete_blocks` (line-start anchored) for fence bodies and the forward rescue scan `_rescue_fenced_block`
- [x] Step 3: Run the bare-block scan on `_mask_fenced_code` instead of the mis-slicing regex strip
- [x] Step 4: Support four-backtick ````xml wrappers; keep bare quad fences and non-xml fences as documentation
- [x] Step 5: Add `night_mode` to the splitter's top-level tags and capture the trailing Markdown section as a fragment, reusing committed filenames
- [x] Step 6: Reword the strict-reject hints, the manual-mode guidance in `06-personas.md`, the executor mode line, and `docs/brain-bridge.md`
- [x] Step 7: Bump `<system_version>` to 9.64.1, regenerate `system-prompt.md`, deploy and restart `mcp-brain`

## Acceptance Criteria

- [x] A fenced `hands_implementation_task` carrying ` ```python ` samples extracts complete on the first turn
- [x] An operator-shaped literal inside a code sample never extracts as a block
- [x] ` ```xml `, ````xml, bare and unclosed-fence answers all behave correctly; a genuinely truncated block still rejects
- [x] `assemble(split(system-prompt.md))` is byte-identical to the shipped prompt
- [x] Prompt, executor and bridge agree on the manual/automatic emission contract
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** Full suite green, including the previously failing `test_system_prompt_split_assemble_round_trip`
- **Actual result:** `665 passed, 24 warnings in 44.77s` (suite after the inline-code guard); bridge subset 293 passed; prompt/splitter subset 103 passed; round-trip byte-identical (108,701 bytes)
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded
- [x] Deployed copies byte-identical under `~/.config/opencode/` (`mcp-brain-bridge/server.py`, `system-prompt.md`, `agents/cognitive-executor.md`) and `mcp-brain` restarted

## Risk & Rollback

- **Risk:** the forward rescue can extract a later allowlisted block that sits between a truncated fence body and the next `xml` opener. Accepted because that path previously produced no output at all.
- **Risk:** making four-backtick fences operative reverses a deliberately pinned behavior (`test_extract_quad_xml_fence_stays_ignored`), so the pin was rewritten rather than deleted.
- **Rollback:** restore the single `_XML_FENCE_RE.finditer` loop, drop the new helpers and tests, revert the splitter tail capture, and re-pin the version to 9.64.0.

## Execution Log & Reasoning

**Mode:** manual, no task file at the time (explicit Manager order "بدون تسک درستش کن"); this task was created afterwards at the Manager's request to carry the diff.

**Autopilot lock (2026-10-24):** Manager ordered "start auto lock for task 342". Locked: QA, fix, and review turns are chained by the Hands under the same `task_id`; the Manager sees only Relay questions and the final verdict, and the closure gate still needs his exact word.

**Seat Check:** domain = Brain bridge extraction plus prompt build pipeline. Seats: Senior Programmer (implementation) with Software Architect for the extraction contract. Skipped: UI/UX (no frontend), QA/Reviewer (post-implementation gates). Brainstorm: not required — offline parser and build-script changes, reversible via git revert, no security/financial/migration surface.

**Decisions:**

- **D1 — line scanner over regex.** CommonMark closes a fence only on a bare run of the same character at least as long as the opener, which a single regex cannot express; the scanner makes ````xml work and keeps non-xml fences documentation.
- **D2 — line-start anchoring for fence bodies.** The mid-line tolerant `_XML_RE` stays for the bare path (existing tolerance tests), while fenced bodies and rescue use `_extract_complete_blocks`, so `sample = "<hotfix>…</hotfix>"` cannot win.
- **D3 — rescue only where the old code raised.** A truncated block still rejects; the strict gate never repairs input.
- **D4 — prompt guidance prefers ````xml.** Manual mode now names the four-backtick wrapper for bodies with fenced code, and the reject hint no longer contradicts manual mode.

**Evidence trail:** reproduced F1 and F2 offline before changing anything (nested block → zero blocks; doc sample → extracted as `<hotfix>`), then pinned both. `git diff --stat` for this task covers the bridge, its tests and decisions, `docs/brain-bridge.md`, `agents/cognitive-executor.md`, the prompt fragments touched by the pipeline fix plus `06-personas.md`, `system-prompt.md`, the splitter and its ADR, the version pin, and `CHANGELOG.md`.

**Note on shared index:** `CHANGELOG.md` is shared with task 339. Task 339's six planner files were unstaged before this task's QA transition so its injected diff stays clean; 339 keeps its already-injected diff and must be re-staged at its closure.

**Autopilot QA/Review chain (2026-10-24):**

- QA turn 1: `VERDICT: QA_PASSED` (VISIBLE hunks; splitter/tests past the 60k cutoff marked UNVERIFIABLE). The same reply exposed a live defect: a quoted sample literal in prose came back `XML_EXTRACTED`, so the bridge would have executed it.
- Fix F6: `_bare_blocks` now skips a match inside an inline code span (odd backtick count earlier on the same line); mid-line bare blocks outside inline code keep their pinned tolerance. New test `test_extract_midline_quoted_hotfix_stays_ignored`; suite 665 passed, exit 0; deployed and `mcp-brain` restarted.
- QA turn 2 (post-fix): `VERDICT: QA_PASSED`, and the extraction correctly returned `REPORT` with no bogus block.
- Reviewer turn: technically approved — `PO_REVIEW_PENDING`, issues I1/I2 UNVERIFIABLE-past-cutoff only, I3 newline churn, I4 shared CHANGELOG hunk; no scope creep into planner files. Diff re-staged after the fix so the QA/review snapshot matches the worktree.
- Manager closure approval (2026-10-24), verbatim: **"Approved for closure"** (question tool, task 342 prompt).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `f0fa3090cddf3723ce332c06b9ecb1145a617ebc`
<!-- END_GIT_DIFF -->
