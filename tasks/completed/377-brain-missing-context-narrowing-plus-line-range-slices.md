# Task 377: Brain missing-context narrowing plus line-range slices

**File:** `tasks/qa/377-brain-missing-context-narrowing-plus-line-range-slices.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
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

- [ ] [375] A turn that delivers file X in full, then receives `<missing_context>X</missing_context>`, is a contract violation under the new wording.
- [ ] [375] The contract names the narrowing move explicitly (smaller path, never same whole file twice).
- [ ] [375] `lint_system_prompt_sync` passes; no hand-edits to the generated file.
- [x] [375] Only the explicitly Manager-authorized cap changes are present (`_CTX_PATHS_PER_FILE` = 150000 and `_CTX_PATHS_TOTAL` = 400000); allocator and schema behavior are unchanged.
- [ ] [376] `["f.py#L10-20"]` injects exactly lines 10–20 with a `lines x-y of N` label; `["f.py#L200-"]` injects the tail.
- [ ] [376] Out-of-range and malformed suffixes produce explicit unavailable labels, never silent drops and never exceptions.
- [ ] [376] No-suffix behavior is byte-identical to before (existing tests prove it).
- [ ] [376] Sliced text counts toward the shared total cap.
- [ ] [376] The contract names the range syntax so the Brain actually uses it.
- [ ] [376] `lint_system_prompt_sync` equivalent (`test_prompt_sync.py`) green.
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

- [ ] [375] A turn that delivers file X in full, then receives `<missing_context>X</missing_context>`, is a contract violation under the new wording.
- [ ] [375] The contract names the narrowing move explicitly (smaller path, never same whole file twice).
- [ ] [375] `lint_system_prompt_sync` passes; no hand-edits to the generated file.
- [x] [375] Only the explicitly Manager-authorized cap changes are present (`_CTX_PATHS_PER_FILE` = 150000 and `_CTX_PATHS_TOTAL` = 400000); allocator and schema behavior are unchanged.
- [ ] [376] `["f.py#L10-20"]` injects exactly lines 10–20 with a `lines x-y of N` label; `["f.py#L200-"]` injects the tail.
- [ ] [376] Out-of-range and malformed suffixes produce explicit unavailable labels, never silent drops and never exceptions.
- [ ] [376] No-suffix behavior is byte-identical to before (existing tests prove it).
- [ ] [376] Sliced text counts toward the shared total cap.
- [ ] [376] The contract names the range syntax so the Brain actually uses it.
- [ ] [376] `lint_system_prompt_sync` equivalent (`test_prompt_sync.py`) green.
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
- Global sync (Manager order, same turn): memory index read (`project-memory` skill + `architecture/zen-proxy-ownership`, `opencode_config/brain-model-routing-2026-10-24`, `workflows/global-install-upgrade`, `project/system-prompt-build-process`). Drift audit repo→`~/.config/opencode/`: only `system-prompt.md` (stale Nov 2) and `mcp-brain-bridge/server.py` differed; all other servers, skills, agents, shell-strategy in sync. Copied both via `cp`, `cmp` byte-identical. `systemctl --user restart mcp-brain.service` → active (new PID); taskless smoke `brain_turn` → SMOKE_OK on the same session thread (history preserved per Manager order). Note: smoke ran as `gpt-6-luna`, not the `muse-spark` single-model order in memory — routing drift to reconcile separately. Known caveat: the synced `server.py` carries the deferred blank-line defect live. Assumption A2: kept the file in `tasks/qa/` — the XML's Step 1 `git mv` to in-progress contradicts its Step 3 (`lint_task_file` on the qa path) and its own ban on transition tools with no move-back instructed, so in-place edit is the coherent reading.
- Python skill fallback: `root=. markers=[mcp-brain-bridge/pyproject.toml,tests/test_brain_bridge.py] matched=[] reason=review-only task metadata update; Python MCP server has no FastAPI marker; python-fastapi loaded for discipline only`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1f143a7..eccd6d5 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Brain `missing_context` narrowing rule + raised context-paths caps (Task 0375):** a planning loop stalled 3 turns re-requesting files the bridge had already delivered (truncated at the 60 KB/file cap with an explicit note). The contract only said STOP-and-list, giving the model no narrowing strategy. The rule now states: a truncation note means *partially present* — verify visible scope first, never re-request a fully-present file, narrow instead of repeating (smaller path, section, symbols). Caps raised `_CTX_PATHS_PER_FILE` 60k → 150k and `_CTX_PATHS_TOTAL` 200k → 400k (env overrides unchanged); `context_paths` also accepts `#Lstart-end` / `#Lstart-` slices, wired into both the tested helper and the live-turn path through shared parsers. System prompt rebuilt to `9.70.3` via the assembler (byte-identical except the two intended hunks); `test_prompt_sync` 22/22, `test_brain_bridge` 304/304 (incl. the exact-default pin test and 7 range tests). QA round made the contract explicit: the narrowing rule now names the `#Lstart-end` / `#Lstart-` slice forms so the Brain uses them, with a prompt-sync regression test pinning both forms and matching `docs/brain-bridge.md` documentation. QA round 2 classified malformed `#L` fragments on supported paths as explicit `bad range` labels (instead of resolution fall-through) with live-path (`_path_candidates`) regression coverage on both entry points. Bridge documentation distinguishes clamped bounds from empty and malformed ranges.
 - **Brain `context_paths` rejected source files (Task 0372):** `_ALLOWED_READ_SUFFIXES` predated the task-210 injection feature and allowed only docs/reports, so every `.java`/`.js`/`.tsx` came back `[unavailable: unsupported extension]` — byte-proven (29.5k of 87k attached). Suffix set extended to source-text languages; binaries still rejected; traversal/size/budget guards untouched. 294/294 brain-bridge tests green.
 - **Brain follow-ups (Task 0374):** truncation notes verified pre-existing in the allocator (no code change); ledger rows carry per-path attach outcomes (`path`/`status`/`chars`, leak-tested — no file text ever); monthly quota counter with stderr warning past the threshold (best-effort, never blocks a turn); end-to-end `.java` injection proven live (91,991 chars attached, 297/297 green).
 
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index ce5d05a..40ffe19 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -132,8 +132,8 @@ repo-root `.env`). Real process env wins; blank counts as unset. See
 | `BRAIN_STAGE_TIERS` | `plan:T2,review:T2,implement:T0,qa:T0,closure:T0`    |
 | `BRAIN_TASK_ATTACH_CAP` | `60000` — task-file attachment chars; blank/unset = default |
 | `BRAIN_TASK_DIFF_CAP` | `200000` — changed-hunks chars; blank/unset = default |
-| `BRAIN_CTX_PER_FILE_CAP` | `60000` — per `context_paths` file; blank/unset = default |
-| `BRAIN_CTX_TOTAL_CAP` | `200000` — all `context_paths` per turn; blank/unset = default |
+| `BRAIN_CTX_PER_FILE_CAP` | `150000` — per `context_paths` file; blank/unset = default |
+| `BRAIN_CTX_TOTAL_CAP` | `400000` — all `context_paths` per turn; blank/unset = default |
 | `BRAIN_INPUT_BUDGET` | `1000000` — input budget ceiling (system + prompt + history), chars |
 | `BRAIN_MODEL_WINDOW_CHARS` | `200000` — utilization monitor only, never a send cap |
 | `BRAIN_CONTEXT_WINDOW_TOKENS` | `1048576` — provider window for the pre-send guard; blank/unset = default |
@@ -193,6 +193,17 @@ Task file and diff blocks keep their stable labels:
 ```
 
 Context paths render as `[path-injected: <path>]` followed by content.
+A trailing `#Lstart-end` requests inclusive 1-based lines `start`–`end`;
+`#Lstart-` requests the tail from `start` through end-of-file
+(e.g. `mcp-brain-bridge/server.py#L3010-3060`). Starts below 1 clamp to
+line 1 and ends beyond EOF clamp to the final line. A selection starting
+past EOF or with start greater than end renders as an explicit
+`[unavailable: … — empty range]` label. A malformed trailing `#L`
+fragment on a supported readable path
+(e.g. `code.py#Lbad`) renders as an unavailable label with the
+`bad range` reason; the same fragment on an unsupported extension flows
+through to the existing unsupported-extension label, and a literal `#`
+elsewhere in a filename is never treated as a range.
 
 ## Response payload: two truncation counters (both normally zero)
 
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 2cce99f..f3edf39 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -64,3 +64,13 @@
 - **Decision:** The comment names OpenCode and other agentic clients; the example names `default.question`, the session tool that actually gates the turn.
 - **Consequences:** Server prose no longer teaches tool names the catalog cannot resolve. Comment-only change; no wire behavior touched.
 - **Rollback:** Restore the two lines from git history.
+
+## [2026-11-05] ADR-010: missing_context narrowing rule + raised context-paths caps
+
+- **Context:** a planning loop stalled for 3 turns re-requesting files the bridge had already delivered (truncated at the 60 KB/file cap with an explicit note). The `missing_context` contract only said STOP-and-list, giving the model no narrowing strategy, and the caps cut a ~181 KB report to 60 KB.
+- **Decision:** (1) extend the No-Hallucination rule: when a truncation note is present, the file counts as partially present — verify visible scope first, never re-request a fully-present file, and narrow (smaller path, section, symbols) instead of repeating a whole-file request. (2) Raise `_CTX_PATHS_PER_FILE` 60k -> 150k and `_CTX_PATHS_TOTAL` 200k -> 400k. The narrowing contract is the real fix; caps only reduce how often truncation fires.
+- **Consequences:** fewer truncation events on large reports; larger worst-case prompts on explicit `context_paths` turns (opt-in only). The exact-default pin test fails loudly on any silent cap drift.
+- **Incidental finding during implementation:** `build_paths_attach` (the unit-tested helper) and `_path_candidates` (the live-turn path) contain parallel loops over the same logic. The range feature was wired into both through the shared `_split_line_range` / `_slice_text_lines` helpers so they cannot drift, but the duplication itself predates this task and is left for a dedicated dedup task.
+- **Follow-up fix (QA round):** the prompt contract and this ADR now name the `#Lstart-end` / `#Lstart-` slice forms explicitly so the Brain actually uses them; `docs/brain-bridge.md` documents the same syntax in the attachment-rendering section.
+- **Follow-up fix (QA round 2):** `_split_line_range` classifies a malformed trailing `#L` fragment on a supported readable path as `bad range` instead of falling through to resolution; a live-path regression test pins sliced content and labels through `_path_candidates`, plus malformed handling on both entry points. Literal-`#` filenames (e.g. `a#b.md`) still flow through untouched.
+- **Rollback:** revert the fragment sentence + cap constants + pin test; rebuild system-prompt.md.
diff --git a/mcp-brain-bridge/README.md b/mcp-brain-bridge/README.md
index c20fcee..9a55dd4 100644
--- a/mcp-brain-bridge/README.md
+++ b/mcp-brain-bridge/README.md
@@ -13,6 +13,11 @@ Brain Bridge MCP daemon: single-tool (`brain_turn`) automation path for planning
 - `session_ledger.py` — Append-only JSONL session event ledger under `tasks/.sessions/`.
 - `pyproject.toml` / `uv.lock` — Runtime deps and lockfile (`mcp[cli]`, stdlib-first helpers).
 - `context-reports/` — Generated context output (do not hand-read; feed via MCP).
+- `context_paths` line slices: `brain_turn(context_paths=[...])` accepts
+  a trailing `#Lstart-end` (inclusive 1-based lines) or `#Lstart-` (tail
+  to EOF); out-of-range ends clamp, empty selections and malformed
+  `#L` fragments on supported paths render as explicit `[unavailable: …]`
+  labels.
 
 ## Key Risks & Invariants
 
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 6e0a41a..a0d0c05 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -3010,13 +3010,17 @@ def load_fed_context(task_id: str, project_root: Optional[str] = None) -> str:
 
 #: Default per-file cap for path-injected context (chars). Overridable via
 #: ``BRAIN_CTX_PER_FILE_CAP``. Rendering truncates with a resume marker.
-_CTX_PATHS_PER_FILE = 60000
+#: Raised 60k -> 150k (task 0375): the largest observed single artifact
+#: (~181 KB context report) was cut to 60 KB; 150 KB covers that class with
+#: headroom while staying a fraction of the 1M input budget.
+_CTX_PATHS_PER_FILE = 150000
 
 #: Default total cap across all path-injected files per turn (chars).
 #: Overridable via ``BRAIN_CTX_TOTAL_CAP``. Files past the total are
 #: skipped with an explicit skipped note — stacked files must never
-#: overflow the turn budget on their own.
-_CTX_PATHS_TOTAL = 200000
+#: overflow the turn budget on their own. Raised 200k -> 400k alongside
+#: the per-file cap so two large files plus the task attach fit one turn.
+_CTX_PATHS_TOTAL = 400000
 
 
 def _paths_base(project_root: Optional[str] = None) -> Path:
@@ -3063,8 +3067,16 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
     used = 0
     base = _paths_base(project_root)
     for rel in wanted:
+        # Same range handling as the allocator path (_path_candidates): strip
+        # `#Lstart[-end]` before resolution so the fragment breaks neither the
+        # root check nor the suffix allowlist. Both entry points share
+        # _split_line_range/_slice_text_lines so they cannot drift apart.
+        path_part, range_start, range_end, range_error = _split_line_range(rel)
+        if range_error is not None:
+            blocks.append(f"[unavailable: {rel.strip()} — bad range]")
+            continue
         try:
-            resolved = _resolve_under_root(rel, root=base)
+            resolved = _resolve_under_root(path_part, root=base)
         except ValueError:
             blocks.append(f"[unavailable: {rel.strip()} — outside workspace]")
             continue
@@ -3082,6 +3094,16 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
         if not text.strip():
             blocks.append(f"[unavailable: {rel.strip()} — empty file]")
             continue
+        open_line = f"[path-injected: {rel.strip()}]"
+        if range_start is not None:
+            sliced, lo, hi, total = _slice_text_lines(text, range_start, range_end)
+            # Empty-selection sentinel is lo == 0: a valid slice can itself
+            # be blank (sliced == ""), which must still inject.
+            if lo == 0:
+                blocks.append(f"[unavailable: {rel.strip()} — empty range]")
+                continue
+            text = sliced
+            open_line = f"[path-injected: {rel.strip()} — lines {lo}-{hi} of {total}]"
         _per_file = _ctx_paths_per_file_cap()
         _total_cap = _ctx_paths_total_cap()
         if len(text) > _per_file:
@@ -3092,7 +3114,7 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
             )
             continue
         used += len(text)
-        blocks.append(f"[path-injected: {rel.strip()}]\n{text}")
+        blocks.append(f"{open_line}\n{text}")
     if not blocks:
         return ""
     return "\n\n---\n\n".join(blocks)
@@ -3360,6 +3382,72 @@ def _inline_path_candidate(rel: str, note: str) -> dict:
     }
 
 
+def _split_line_range(rel: str) -> tuple[str, object, object, object]:
+    """Split a trailing ``#L<start>[-<end>]`` range off a context path.
+
+    Returns ``(path_part, start, end, error)`` where ``start``/``end`` are
+    1-based ints (``end`` is None for the open-ended ``#Lstart-`` form and
+    ``None``/``None`` when no range suffix is present). ``error`` is a short
+    label fragment (``"bad range"``) when the fragment looks like a range
+    but does not parse — the caller turns it into an explicit unavailable
+    label, never a silent drop.
+
+    Only a *trailing* ``#L<digits>`` pattern is treated as a range, so a
+    literal ``#`` anywhere else in a filename flows through untouched.
+    A trailing ``#L`` fragment that does not parse (e.g. ``code.py#Lbad``)
+    on a path with a supported readable extension is a caller error and
+    returns the ``"bad range"`` error instead of falling through to path
+    resolution — the caller labels it explicitly, never silently drops
+    it. The same malformed fragment on an unsupported extension flows
+    through unchanged so the existing unsupported-extension label wins.
+    """
+    match = re.search(r"#L(\d+)(?:-(\d*))?$", rel)
+    if not match:
+        malformed = re.search(r"#L[^/]*$", rel)
+        if malformed:
+            from pathlib import PurePath as _PurePath
+
+            if (
+                _PurePath(rel[: malformed.start()]).suffix.lower()
+                in _ALLOWED_READ_SUFFIXES
+            ):
+                return rel, None, None, "bad range"
+        return rel, None, None, None
+    try:
+        start = int(match.group(1))
+    except (TypeError, ValueError):
+        return rel, None, None, "bad range"
+    end_raw = match.group(2)
+    if end_raw is None:
+        return rel[: match.start()], start, start, None
+    if end_raw == "":
+        return rel[: match.start()], start, None, None
+    try:
+        end = int(end_raw)
+    except (TypeError, ValueError):
+        return rel, None, None, "bad range"
+    return rel[: match.start()], start, end, None
+
+
+def _slice_text_lines(text: str, start: int, end: object) -> tuple[str, int, int, int]:
+    """Slice ``text`` to 1-based ``[start, end]`` (``end=None`` means EOF).
+
+    Clamps out-of-range ends to the file instead of failing, so a stale line
+    number from an older revision still yields the nearest content. Returns
+    ``(sliced, start, end, total)`` with the *effective* bounds, or
+    ``("", 0, 0, total)`` when the range selects nothing (start > end, or
+    start past EOF) — the caller turns that into an explicit empty-range
+    label, never a silent drop.
+    """
+    lines = text.splitlines()
+    total = len(lines)
+    lo = max(start, 1)
+    hi = total if end is None else min(end, total)
+    if lo > hi or lo > total:
+        return "", 0, 0, total
+    return "\n".join(lines[lo - 1 : hi]), lo, hi, total
+
+
 def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[dict]:
     """Full-text candidates for ``context_paths`` ('' labels kept explicit).
 
@@ -3381,8 +3469,17 @@ def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[
     out: list[dict] = []
     base = _paths_base(project_root)
     for rel in wanted:
+        # Line-range suffix: strip `#Lstart[-end]` BEFORE workspace resolution,
+        # otherwise the fragment breaks both the root check and the suffix
+        # allowlist (`file.py#L10-20` has no recognized extension).
+        path_part, range_start, range_end, range_error = _split_line_range(rel)
+        if range_error is not None:
+            out.append(
+                _inline_path_candidate(rel, f"[unavailable: {rel.strip()} — bad range]")
+            )
+            continue
         try:
-            resolved = _resolve_under_root(rel, root=base)
+            resolved = _resolve_under_root(path_part, root=base)
         except ValueError:
             out.append(
                 _inline_path_candidate(
@@ -3420,11 +3517,25 @@ def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[
                 )
             )
             continue
+        open_line = f"[path-injected: {rel.strip()}]"
+        if range_start is not None:
+            sliced, lo, hi, total = _slice_text_lines(text, range_start, range_end)
+            # Same sentinel as the helper path above: lo == 0 means no
+            # selection; a blank but valid slice still injects.
+            if lo == 0:
+                out.append(
+                    _inline_path_candidate(
+                        rel, f"[unavailable: {rel.strip()} — empty range]"
+                    )
+                )
+                continue
+            text = sliced
+            open_line = f"[path-injected: {rel.strip()} — lines {lo}-{hi} of {total}]"
         out.append(
             {
                 "kind": "context_path",
                 "path": rel.strip(),
-                "open_line": f"[path-injected: {rel.strip()}]",
+                "open_line": open_line,
                 "fence_lang": None,
                 "text": text,
                 "cap": per_file,
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index ee72fde..4dbf017 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.70.2</system_version>
+<system_version>9.70.3</system_version>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index eacd357..4e7b5d3 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -3,7 +3,7 @@
 - **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
-- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
+- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file.
 - **Tone and Demeanor**: Write as a knowledgeable colleague, not as a machine and not as a friend. Lead with the answer, then the reasoning. Keep the register professional and objective. Skip superlatives, flattery, and filler.
 - **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
   1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
diff --git a/system-prompt.md b/system-prompt.md
index b128dfc..827bd50 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.70.2</system_version>
+<system_version>9.70.3</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -499,7 +499,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 - **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
-- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
+- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file.
 - **Tone and Demeanor**: Write as a knowledgeable colleague, not as a machine and not as a friend. Lead with the answer, then the reasoning. Keep the register professional and objective. Skip superlatives, flattery, and filler.
 - **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
   1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 30d8442..e2b275e 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1654,6 +1654,117 @@ def test_paths_attach_empty_labelled(tmp_path, monkeypatch):
     assert "empty file" in out
 
 
+def test_path_candidates_line_range_slice(tmp_path, monkeypatch):
+    # QA round 2: the live-turn path must slice exactly like the helper.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text(
+        "".join(f"line {i}\n" for i in range(1, 11)), encoding="utf-8"
+    )
+    cands = bridge._path_candidates(["code.py#L3-5"])
+    assert len(cands) == 1
+    assert cands[0]["open_line"] == "[path-injected: code.py#L3-5 — lines 3-5 of 10]"
+    assert cands[0]["text"] == "line 3\nline 4\nline 5"
+
+
+def test_line_range_malformed_labelled_both_paths(tmp_path, monkeypatch):
+    # QA round 2: `code.py#Lbad` is a caller error — explicit bad-range
+    # label on both the helper and the live-turn path, never a silent drop
+    # and never a misleading resolution/extension label.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text("x = 1\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["code.py#Lbad"])
+    assert "[unavailable: code.py#Lbad — bad range]" in out
+    cands = bridge._path_candidates(["code.py#Lbad"])
+    assert len(cands) == 1
+    assert "bad range" in cands[0]["open_line"]
+
+
+def test_line_range_blank_slice_injects_both_paths(tmp_path, monkeypatch):
+    # Review round 3: a slice selecting exactly one blank line is valid
+    # content ("", lo=2), not the ("", 0, 0) empty-selection sentinel.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text("a\n\nc\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["code.py#L2-2"])
+    assert "[path-injected: code.py#L2-2 — lines 2-2 of 3]" in out
+    assert "empty range" not in out
+    cands = bridge._path_candidates(["code.py#L2-2"])
+    assert len(cands) == 1
+    assert cands[0]["open_line"] == "[path-injected: code.py#L2-2 — lines 2-2 of 3]"
+    assert cands[0]["text"] == ""
+    # The true empty selection still labels on both paths.
+    assert "empty range" in bridge.build_paths_attach(["code.py#L3-2"])
+    assert "empty range" in bridge._path_candidates(["code.py#L3-2"])[0]["open_line"]
+
+
+def test_paths_attach_line_range_slice(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text(
+        "".join(f"line {i}\n" for i in range(1, 11)), encoding="utf-8"
+    )
+    out = bridge.build_paths_attach(["code.py#L3-5"])
+    assert "[path-injected: code.py#L3-5 — lines 3-5 of 10]" in out
+    assert "line 3\nline 4\nline 5" in out
+    assert "line 2\n" not in out
+    assert "line 6\n" not in out
+
+
+def test_paths_attach_line_range_open_tail(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text(
+        "".join(f"line {i}\n" for i in range(1, 6)), encoding="utf-8"
+    )
+    out = bridge.build_paths_attach(["code.py#L4-"])
+    assert "lines 4-5 of 5" in out
+    assert "line 4\nline 5" in out
+    assert "line 3\n" not in out
+
+
+def test_paths_attach_line_range_single_line(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text("a\nb\nc\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["code.py#L2"])
+    assert "lines 2-2 of 3" in out
+    assert "\nb\n" in out or out.rstrip().endswith("b")
+
+
+def test_paths_attach_line_range_clamped(tmp_path, monkeypatch):
+    # Out-of-range ends clamp to the file instead of failing: a stale line
+    # number from an older revision still yields the nearest content.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text("a\nb\nc\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["code.py#L0-99"])
+    assert "lines 1-3 of 3" in out
+    assert "a\nb\nc" in out
+
+
+def test_paths_attach_line_range_empty_labelled(tmp_path, monkeypatch):
+    # start > end and start-past-EOF are caller errors: label, never slice.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text("a\nb\nc\n", encoding="utf-8")
+    assert "empty range" in bridge.build_paths_attach(["code.py#L3-2"])
+    assert "empty range" in bridge.build_paths_attach(["code.py#L9-12"])
+
+
+def test_paths_attach_line_range_counts_toward_total(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    monkeypatch.setattr(bridge, "_CTX_PATHS_PER_FILE", 10000)
+    monkeypatch.setattr(bridge, "_CTX_PATHS_TOTAL", 30)
+    (tmp_path / "a.py").write_text("x\n" * 50, encoding="utf-8")
+    out = bridge.build_paths_attach(["a.py#L1-10", "a.py#L11-20"])
+    # First slice (~20 chars) fits; the second exceeds the shared total.
+    assert "lines 1-10 of 50" in out
+    assert "total budget" in out
+
+
+def test_paths_attach_hash_in_filename_not_a_range(tmp_path, monkeypatch):
+    # A literal '#' elsewhere in the name must not be mistaken for a range.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "a#b.md").write_text("hash\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["a#b.md"])
+    assert "[path-injected: a#b.md]" in out
+    assert "hash" in out
+
+
 def test_paths_attach_per_file_cap(tmp_path, monkeypatch):
     _ws(tmp_path, monkeypatch)
     (tmp_path / "big.md").write_text(
@@ -3776,8 +3887,9 @@ def test_env_positive_int_override_and_guards(monkeypatch):
 def test_default_caps_meet_issue_thresholds():
     assert bridge._TASK_DIFF_CAP >= 200000
     assert bridge._TASK_ATTACH_CAP >= 60000
-    assert bridge._CTX_PATHS_PER_FILE >= 60000
-    assert bridge._CTX_PATHS_TOTAL >= 200000
+    # Pinned exact: a silent default change alters every turn's prompt budget.
+    assert bridge._CTX_PATHS_PER_FILE == 150000
+    assert bridge._CTX_PATHS_TOTAL == 400000
     assert bridge._INPUT_BUDGET >= 200000
 
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 5679f26..6574b3d 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,19 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.70.2"
+    assert shipped == "9.70.3"
+
+
+def test_shipped_prompt_documents_context_path_line_ranges():
+    """The shipped prompt must name the #L slice forms, not just narrowing.
+
+    Regression (META 377 QA round): the parser accepted `path#Lstart-end`
+    and `path#Lstart-` but the No-Hallucination contract only said "name a
+    smaller path", so the Brain was never told the slice syntax exists.
+    """
+    shipped = _read(SHIPPED)
+    assert "path#Lstart-end" in shipped
+    assert "path#Lstart-" in shipped
 
 
 def test_parallel_mandate_covers_implementation_triggers():
```
<!-- END_GIT_DIFF -->
