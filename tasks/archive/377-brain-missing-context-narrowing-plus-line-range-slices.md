# Task 377: Brain missing-context narrowing plus line-range slices

**File:** `tasks/completed/377-brain-missing-context-narrowing-plus-line-range-slices.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-05T22:16:03Z
**Submitted:** 2026-11-05T21:39:19Z
**Started:** 2026-11-05T21:32:39Z
**Supersedes:** [375, 376]
**Meta:** true
**Created:** 2026-11-05 21:31 UTC
**Bundled:** 2 tasks

## Supersedes

This META supersedes 2 source task(s). Each one is archived to `tasks/archive/` with a `**Superseded-By:** 377-brain-missing-context-narrowing-plus-line-range-slices` marker and stays reachable via `git log --oneline --follow -- tasks/archive/<id>-*.md`:

- `375` — Teach the missing_context contract to narrow instead of re-demanding whole files
- `376` — Line-range slices for brain_turn context_paths

Execution is all-or-nothing: every line of `## Bundled Checklist (All-or-Nothing)` must pass, otherwise the whole META is `QA_REJECTED` and returns to `in-progress`. A partial close is forbidden.

## Goal

Unified execution of 2 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [375, 376] — "Brain missing-context narrowing plus line-range slices" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

> ⚠️ **Guardrail Warning:** Combined source size is 646 LOC (> 400). Unified META diff may be large and hard to review. Consider splitting into two METAs.

**Source IDs:** [375, 376]
**Next ID:** 377 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 377-brain-missing-context-narrowing-plus-line-range-slices` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 2 small related tasks together and speed up turnaround.

**Traceability:**
- Supersedes [375, 376] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 377-brain-missing-context-narrowing-plus-line-range-slices` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**
- Cap 6 per bundle — this bundle has 2 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 646 LOC (⚠️ exceeds 400 — consider split)

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 375: Teach the missing_context contract to narrow instead of re-demanding whole files

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/in-progress/0375-brain-missing-context-narrowing.md` → `tasks/archive/0375-brain-missing-context-narrowing.md` (after bundling)

**Title:** Teach the missing_context contract to narrow instead of re-demanding whole files

#### Goal (verbatim)

Stop the Brain from stalling on files it already has. When a turn delivers truncated context, the model must check visible scope first and request narrower slices — not re-demand whole files the 60 KB/file cap can never deliver in one shot.

#### Acceptance Criteria (verbatim)

- [ ] A turn that delivers file X in full, then receives `<missing_context>X</missing_context>`, is a contract violation under the new wording.
- [ ] The contract names the narrowing move explicitly (smaller path, never same whole file twice).
- [ ] `lint_system_prompt_sync` passes; no hand-edits to the generated file.
- [ ] No cap, allocator, or schema behavior changed (prove with `git diff --stat` showing only prompt + test + changelog files).

#### Local TODOs (verbatim)

- [x] Locate the fragment→system-prompt build command (`scripts/prompt-build/assemble_system_prompt.py --output <tmp>` for verification, native edits into the committed file, rebuild in place; version lives in `prompts/fragments/01-system_version.md`).
- [x] Edit the `missing_context` fragment with the narrowing rule (no task numbers in prompt prose per discipline).
- [x] Rebuild + verify byte-identical except the two intended hunks; `test_prompt_sync.py` 22/22 (incl. the version-bump gate, updated to 9.70.3).
- [x] Contract/pin tests: exact-default pin (`== 150000` / `== 400000`) + full `test_brain_bridge.py` 297/297.
- [x] Caps raised per explicit Manager order (supersedes the original no-cap-change line, recorded in Non-goals).
- [x] CHANGELOG entry (HQ repo); ADR-010 in `mcp-brain-bridge/DECISIONS.md`.

#### Risk & Rollback (verbatim)

- **Risk:** a stricter contract makes the model guess instead of asking. Mitigation: the rule only narrows *re-requests*; genuinely absent files are still listed the same way.
- **Rollback:** revert the fragment hunk + rebuild system-prompt.

#### Scope (verbatim)

1. Amend the `missing_context` contract in `prompts/fragments/13-constraints.md` (current line 6: STOP + output ONLY the tag). Add the narrowing rule: if the turn carries a truncation note, (a) verify each candidate against visible scope before listing it, (b) request narrower slices (a different, smaller path — never the same whole file twice), (c) never list a file that is fully present in visible scope.
2. Rebuild `system-prompt.md` through the repo's fragment assembly (do NOT hand-edit the generated file) and verify with the `lint_system_prompt_sync` check.
3. Add or extend a test that pins the contract wording (a prompt fixture whose reply lists a fully-visible file must fail the new rule).

#### Non-goals (caps line amended 2026-11-05 by explicit Manager order) (verbatim)

- ~~No change to caps (`_CTX_PATHS_PER_FILE` 60k, total 200k)~~ — SUPERSEDED: per-file 60k → 150k, total 200k → 400k are IN scope. Rationale in ADR: covers the observed ~181 KB artifact class with headroom while staying a fraction of the 1M input budget; narrowing remains the real fix.
- No change to the allocator, traversal guard, or suffix allowlist (0372 owns that surface and is closed).
- No change to the truncation-note wording itself — it already says "Judge visible only".
- No MCP schema change.

#### Verification Evidence (verbatim)

| Gate | Result |
|------|--------|
| Incident ledger entry | `tasks/.sessions/context_ledger.jsonl`, task_id `1039`: `paths: [{path: "context-reports/context_report_20261105_221157_4c92bf65.md", status: "truncated", chars: 60190}]`, `util_pct: 168` |
| Report head proves AGENTS.md fully inside the injected slice | first file in report, ~7.5 KB < 60,190 chars |
| `attachment_chars_remaining: 0` | hardcoded constant in the allocator (`server.py`, always 0) — NOT exhaustion evidence |
| Repro of the model failure | 3 consecutive turns under task 1039 listed `AGENTS.md` + complete `aiService.js`/`README.md`/`DECISIONS.md` despite the above |
| Fix verification | pending |

---

### Source Task 376: Line-range slices for brain_turn context_paths

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/qa/0376-context-paths-line-ranges.md` → `tasks/archive/0376-context-paths-line-ranges.md` (after bundling)

**Title:** Line-range slices for brain_turn context_paths

#### Goal (verbatim)

Let `brain_turn(context_paths=[...])` accept a line-range suffix — `path#Lstart-end` (and `path#Lstart-` for tail-to-EOF) — so a turn can pull 40 lines out of a 2000-line file instead of truncating a whole-file attach at the cap and stalling on `<missing_context>`.

#### Acceptance Criteria (verbatim)

- [ ] `["f.py#L10-20"]` injects exactly lines 10–20 with a `lines x-y of N` label; `["f.py#L200-"]` injects the tail.
- [ ] Out-of-range and malformed suffixes produce explicit unavailable labels, never silent drops and never exceptions.
- [ ] No-suffix behavior is byte-identical to before (existing tests prove it).
- [ ] Sliced text counts toward the shared total cap.
- [ ] The contract names the range syntax so the Brain actually uses it.
- [ ] `lint_system_prompt_sync` equivalent (`test_prompt_sync.py`) green.

#### Local TODOs (verbatim)

- [x] Suffix parsing + validation + slicing (`_split_line_range`, `_slice_text_lines`) wired into BOTH `build_paths_attach` and `_path_candidates` via the shared helpers.
- [x] Fragment contract line + version bump 9.70.3 + rebuild (byte-identical except the two intended hunks).
- [x] Docs table (`docs/brain-bridge.md` env rows) + ADR-010 + CHANGELOG.
- [x] Full `test_brain_bridge.py` (304 incl. 7 new range tests) + `test_prompt_sync.py` (22) green.

#### Risk & Rollback (verbatim)

- **Risk:** a `#` in a real filename collides with the fragment syntax. Mitigation: only a trailing `#L<digits>[-<digits>]` pattern is treated as a range; anything else flows through the existing path unchanged (covered by a test with a `#` in the name if the filesystem allows, else documented).
- **Rollback:** revert the parser hunk in `_path_candidates` + fragment line + version bump; ranges stop parsing and whole-file behavior is untouched.

#### Scope (verbatim)

1. **Suffix parsing in `_path_candidates`** (`mcp-brain-bridge/server.py`): strip a trailing `#L<start>[-<end>]` fragment BEFORE `_resolve_under_root` (today the fragment would break both resolution and the suffix allowlist). 1-based lines; clamp `start < 1` to 1 and `end > total` to total; `start > end` or `start > total` becomes an explicit `[unavailable: ... — empty range]` label; non-numeric becomes `[unavailable: ... — bad range]`. Sliced text counts toward the same total cap; the injected block is labeled `[path-injected: rel#Lx-y — lines x-y of N]`.
2. **Contract line**: extend the 0375 narrowing rule in `prompts/fragments/13-constraints.md` with one sentence pointing at the range syntax; bump `01-system_version.md` and rebuild `system-prompt.md` via the assembler (byte-identical except intended hunks).
3. **Tests**: range parsing, clamping both ends, invalid ranges as unavailable labels, empty-range case, total-cap accounting for sliced text, whole-file behavior unchanged when no suffix is present.
4. **Docs**: `docs/brain-bridge.md` `context_paths` description + `mcp-brain-bridge/DECISIONS.md` ADR + CHANGELOG entry.

#### Non-goals (verbatim)

- No tree-sitter / symbol-based extraction (new native dependency; breaks the stdlib-only, offline-testable helper invariant).
- No adopting an external MCP server for file reads (violates the single-tool invariant).
- No change to caps, the allocator, traversal, or the MCP schema.
- No change to the truncation-note wording.

#### Verification Evidence (verbatim)

| Gate | Result |
|------|--------|
| Web research (blowsh deep loop) | done — Desktop Commander offset/length, large-file-mcp chunk/navigate/search, ctoth tree-sitter extractor, mcp-file-lens; suffix convention chosen, libraries rejected with reasons |
| Brainstorm | done — A: suffix (chosen); B: tree-sitter (rejected: native dep); C: external MCP (rejected: single-tool invariant) |
| Unit + regression tests | pending |
| `test_prompt_sync.py` + `test_brain_bridge.py` | pending |
| Manager plan approval | pending |

---


## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [x] [375] A turn that delivers file X in full, then receives `<missing_context>X</missing_context>`, is a contract violation under the new wording.
- [x] [375] The contract names the narrowing move explicitly (smaller path, never same whole file twice).
- [x] [375] `lint_system_prompt_sync` passes; no hand-edits to the generated file.
- [x] [375] Only the explicitly Manager-authorized cap changes are present (`_CTX_PATHS_PER_FILE` = 150000 and `_CTX_PATHS_TOTAL` = 400000); allocator and schema behavior are unchanged.
- [x] [376] `["f.py#L10-20"]` injects exactly lines 10–20 with a `lines x-y of N` label; `["f.py#L200-"]` injects the tail.
- [x] [376] Out-of-range and malformed suffixes produce explicit unavailable labels, never silent drops and never exceptions.
- [x] [376] No-suffix behavior is byte-identical to before (existing tests prove it).
- [x] [376] Sliced text counts toward the shared total cap.
- [x] [376] The contract names the range syntax so the Brain actually uses it.
- [x] [376] `lint_system_prompt_sync` equivalent (`test_prompt_sync.py`) green.
- [ ] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [ ] Step 1: Validate META bundle — confirm all 2 source requirements are captured verbatim below
- [ ] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [ ] [375] Locate the fragment→system-prompt build command (`scripts/prompt-build/assemble_system_prompt.py --output <tmp>` for verification, native edits into the committed file, rebuild in place; version lives in `prompts/fragments/01-system_version.md`).
- [ ] [375] Edit the `missing_context` fragment with the narrowing rule (no task numbers in prompt prose per discipline).
- [ ] [375] Rebuild + verify byte-identical except the two intended hunks; `test_prompt_sync.py` 22/22 (incl. the version-bump gate, updated to 9.70.3).
- [ ] [375] Contract/pin tests: exact-default pin (`== 150000` / `== 400000`) + full `test_brain_bridge.py` 297/297.
- [ ] [375] Caps raised per explicit Manager order (supersedes the original no-cap-change line, recorded in Non-goals).
- [ ] [375] CHANGELOG entry (HQ repo); ADR-010 in `mcp-brain-bridge/DECISIONS.md`.
- [ ] [376] Suffix parsing + validation + slicing (`_split_line_range`, `_slice_text_lines`) wired into BOTH `build_paths_attach` and `_path_candidates` via the shared helpers.
- [ ] [376] Fragment contract line + version bump 9.70.3 + rebuild (byte-identical except the two intended hunks).
- [ ] [376] Docs table (`docs/brain-bridge.md` env rows) + ADR-010 + CHANGELOG.
- [ ] [376] Full `test_brain_bridge.py` (304 incl. 7 new range tests) + `test_prompt_sync.py` (22) green.
- [ ] Step 13: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [ ] Step 14: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [x] [375] A turn that delivers file X in full, then receives `<missing_context>X</missing_context>`, is a contract violation under the new wording.
- [x] [375] The contract names the narrowing move explicitly (smaller path, never same whole file twice).
- [x] [375] `lint_system_prompt_sync` passes; no hand-edits to the generated file.
- [x] [375] Only the explicitly Manager-authorized cap changes are present (`_CTX_PATHS_PER_FILE` = 150000 and `_CTX_PATHS_TOTAL` = 400000); allocator and schema behavior are unchanged.
- [x] [376] `["f.py#L10-20"]` injects exactly lines 10–20 with a `lines x-y of N` label; `["f.py#L200-"]` injects the tail.
- [x] [376] Out-of-range and malformed suffixes produce explicit unavailable labels, never silent drops and never exceptions.
- [x] [376] No-suffix behavior is byte-identical to before (existing tests prove it).
- [x] [376] Sliced text counts toward the shared total cap.
- [x] [376] The contract names the range syntax so the Brain actually uses it.
- [x] [376] `lint_system_prompt_sync` equivalent (`test_prompt_sync.py`) green.
- [ ] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Verification Evidence

- **Test command:** `lint_task_file` on META file; `git log --oneline --follow -- tasks/archive/<id>-*.md | head` for archived sources; project test suite if logic changed
- **Expected result:** META lint passes; all 2 sources in `tasks/archive/` with `superseded` status; single Factual Git Diff covers all bundled changes
- **Actual result:** META lint passes; `test_brain_bridge.py` + `test_prompt_sync.py` 330/330 green (307 bridge incl. 7 range tests + live-path slice test + malformed-range test + blank-line slice test + exact-default pin 150k/400k; 23 prompt sync incl. `#L`-forms pin test). Archive files verified present with Superseded-By markers; `git log --follow` empty (no prior committed history — sources created and bundled in uncommitted state).
- **Exit code:** 0 (`uv run pytest ../tests/test_brain_bridge.py ../tests/test_prompt_sync.py -q` from `mcp-brain-bridge/`; `pyproject.toml`/`uv.lock` untouched)
- **Read-only state checks (review round 2, 2026-11-05, all exit 0 unless noted):**
  - `git status --short` → 9 modified code/docs/test files (`M`), both archive sources `AM` (staged move + header patch), META `A` in `tasks/qa/`; no commits created by Hands (HEAD still `446ecbf cleanup` per `git log -5 --oneline`).
  - `git diff --cached --name-only` → the 9 code/docs/test files + 2 archive files + META file (index matches the injected Factual Git Diff scope).
  - `git diff --name-only` (worktree) → only the 2 archive files (bundler header-patch residue on task files, excluded from the injected diff by `:!tasks/` scope; no product-file drift).
  - `test -f tasks/archive/0375-… && test -f tasks/archive/0376-…` → both present, exit 0.
  - `grep -nF '**Superseded-By:** `377-brain-missing-context-narrowing-plus-line-range-slices`' tasks/archive/0375-… tasks/archive/0376-…` → one match each, both line 7 (backticked marker form; the unbracketed reviewer pattern matches nothing by construction).
  - `git log --follow` on both archive files → empty (sources never committed; marker presence is the traceability evidence per Manager instruction).

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [375, 376], remove Superseded-By footer, delete or archive `tasks/backlog/377-brain-missing-context-narrowing-plus-line-range-slices.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

- Autopilot locked for META 377 (Manager order "auto pilot mode"). Goal set: META 377 autopilot QA to closure-ready.
- 2026-11-05: claimed 377 via `claim_next` (backlog → in-progress); injected 9-file worktree diff via `stage_and_inject_diff` (code + docs + tests; archive moves excluded from injected diff by `:!tasks/` scope).
- Verification: `uv run pytest ../tests/test_brain_bridge.py ../tests/test_prompt_sync.py -q` → 326 passed in 2.26s, exit 0. Reverted incidental `pyproject.toml`/`uv.lock` dev-dep add; worktree holds only the 9 intended files.
- Assumption A1: the staged worktree (narrowing contract + 150k/400k caps + `#L` slices in both helpers) is the unified META implementation — no new code written under 377; 375/376 diffs already cover all checklist lines.
- QA round 1 verdict: QA_REJECTED (valid) — parser accepted `#L` slices but neither the prompt contract nor `docs/brain-bridge.md` named the syntax. Hotfix applied under same task, no cap/allocator/schema change:
  - `prompts/fragments/13-constraints.md`: narrowing sentence now names `path#Lstart-end` (inclusive 1-based) and `path#Lstart-` (tail to EOF); `system-prompt.md` rebuilt via assembler (byte-identical except the one intended hunk; version stays 9.70.3 so the minor-bump pin still passes).
  - `docs/brain-bridge.md`: attachment-rendering section documents both slice forms + unavailable-label semantics.
  - `mcp-brain-bridge/DECISIONS.md`: ADR-010 follow-up line records the explicit-syntax fix (no duplicate ADR).
  - `tests/test_prompt_sync.py`: new `test_shipped_prompt_documents_context_path_line_ranges` pins both forms in shipped prompt.
  - `CHANGELOG.md`: appended QA-round clause to the existing 0375 entry (Parse-Then-Append, no duplicate section).
- Archive traceability: both `tasks/archive/0375-…md` and `tasks/archive/0376-…md` exist with `Superseded-By: 377-…` marker (grep count 1 each); `git log --follow` returns no rows — the sources were created and bundled within uncommitted worktree state, so there is no prior committed history to follow. Nothing to roll back to; marker presence is the traceability evidence.
- Re-verification round 2: `uv run pytest ../tests/test_brain_bridge.py ../tests/test_prompt_sync.py -q` (from `mcp-brain-bridge/`) → 329 passed, exit 0 (306 bridge + 23 sync). `pyproject.toml`/`uv.lock` untouched.
- QA round 2 verdict: QA_REJECTED (valid) — (F1) no test exercised the live-turn `_path_candidates` slice path; (F2) `_split_line_range` only matched numeric suffixes so `code.py#Lbad` fell through to resolution instead of the `bad range` label the scope requires. Hotfix applied under same task, no cap/allocator/schema change:
  - `mcp-brain-bridge/server.py`: `_split_line_range` now returns `bad range` for a trailing malformed `#L` fragment when the pre-suffix path has a supported readable extension; unsupported extensions and literal-`#` names (e.g. `a#b.md`) flow through unchanged (existing tests prove it).
  - `tests/test_brain_bridge.py`: new `test_path_candidates_line_range_slice` (live path: exact `open_line` + `text`) and `test_line_range_malformed_labelled_both_paths` (`code.py#Lbad` → `bad range` on both entry points).
  - `docs/brain-bridge.md` + `mcp-brain-bridge/README.md`: malformed-`#L` classification documented; ADR-010 round-2 follow-up line; CHANGELOG clause appended (Parse-Then-Append).
- Python skill fallback: `root=. markers=[mcp-brain-bridge/pyproject.toml,tests/test_brain_bridge.py] matched=[] reason=Python MCP server has no FastAPI marker; python-fastapi loaded for Python discipline only`.
- Review round 1 verdict: APPROVED_WITH_CHANGES (I1, valid) — `docs/brain-bridge.md` said out-of-range suffixes produce unavailable labels, but `_slice_text_lines` clamps (only past-EOF-start and start>end yield `empty range`). Docs-only correction, no parser/test/prompt change: sentence now states clamp-then-empty-range semantics; CHANGELOG clause appended.
- Review round 2 verdict: APPROVED_WITH_CHANGES (I1 blocking + I2 verification gap, both valid) — (I1) the derived Bundled Checklist + Acceptance Criteria still said "no cap changes" while the diff carries the Manager-authorized 150k/400k defaults. Fixed by replacing exactly those two derived lines with the evidence-checkable authorized-cap criterion (checked: pin test asserts exact values, 329 green); the verbatim Source Task 375 block is untouched. Traceability boxes stay unchecked: markers verified present (line 7, both files) but `git log --follow` is empty, so the "reachable via" half of that line is not evidence-backed. (I2) recorded the read-only `git status` / cached / worktree / log / archive-marker outputs above.
- Review round 3 verdict: REJECTED_NEEDS_FIXES (genuine defect, reviewer escalated with O1/O2). Blank-line slice (`code.py#Lx` selecting exactly one empty line) yields `""` text and both callers misclassified via `if not sliced` as `empty range`. Manager chose O1 (2026-11-05): goal resumed, 377 moved qa→in-progress, scoped repair applied — both callers now test the effective-bounds sentinel (`lo == 0`) instead of text falsiness, so blank-but-valid slices inject while true empty selections still label. Added `test_line_range_blank_slice_injects_both_paths` (blank slice injects with `lines 2-2 of 3` label on both entry points; `L3-2` still labels). No prompt/docs/cap/schema change.
- Re-verification O1: `uv run pytest ../tests/test_brain_bridge.py ../tests/test_prompt_sync.py -q` (from `mcp-brain-bridge/`) → 330 passed, exit 0 (307 bridge + 23 sync). `pyproject.toml`/`uv.lock` untouched.
- Review round 4 verdict: APPROVED technically — PO_REVIEW_PENDING (no issues; cites `server.py:3099/3522`, `test_brain_bridge.py:1682`). Fixed `server.py` re-synced to global install (`cmp` byte-identical) and `mcp-brain.service` restarted → active; the live brain now serves the approved code including the blank-line fix.
- Closure: Manager answered the relayed PO_REVIEW_PENDING question with exactly "Approved for closure" (question-tool record), then authorized the standard closure sequence directly with "Execute standard closure" after the bridge literal-gate refused to emit closure XML (it counts the auto-attached task bundle as "additional content", so a bare-phrase turn can never pass through `brain_turn`; two attempts logged, no further retries). File verified in `tasks/qa/` with PO_REVIEW_PENDING in this log before closing.
- Global sync (Manager order, same turn): memory index read (`project-memory` skill + `architecture/zen-proxy-ownership`, `opencode_config/brain-model-routing-2026-10-24`, `workflows/global-install-upgrade`, `project/system-prompt-build-process`). Drift audit repo→`~/.config/opencode/`: only `system-prompt.md` (stale Nov 2) and `mcp-brain-bridge/server.py` differed; all other servers, skills, agents, shell-strategy in sync. Copied both via `cp`, `cmp` byte-identical. `systemctl --user restart mcp-brain.service` → active (new PID); taskless smoke `brain_turn` → SMOKE_OK on the same session thread (history preserved per Manager order). Note: smoke ran as `gpt-6-luna`, not the `muse-spark` single-model order in memory — routing drift to reconcile separately. Known caveat: the synced `server.py` carries the deferred blank-line defect live. Assumption A2: kept the file in `tasks/qa/` — the XML's Step 1 `git mv` to in-progress contradicts its Step 3 (`lint_task_file` on the qa path) and its own ban on transition tools with no move-back instructed, so in-place edit is the coherent reading.
- Python skill fallback: `root=. markers=[mcp-brain-bridge/pyproject.toml,tests/test_brain_bridge.py] matched=[] reason=review-only task metadata update; Python MCP server has no FastAPI marker; python-fastapi loaded for discipline only`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `02ce1d03b77f1c4411fc3777a44632f262316ce0`
<!-- END_GIT_DIFF -->
