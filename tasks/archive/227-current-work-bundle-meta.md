# Task 227: Current-work META (220 issue-8 follow-ups + 224 roadmap trio + 225 roster + 226 task_id gate)

**File:** `tasks/completed/227-current-work-bundle-meta.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Supersedes:** [220, 224, 225, 226]
**Meta:** true

## Source Context

## Goal

Bundle every current (non-final) task into one META with all parts merged, keep a single task, carry the full worktree diff, and pass one QA + review gate.

## Manager's Notes

Manager order (Persian, 2026-09-13, verbatim): bundle ALL current tasks into one, ensure all parts merge, DELETE bundled source tasks, keep one task, inject ALL worktree changes, then QA, then code reviewer. Completed tasks (209, 210, 219) are FINAL and untouched. Sources 220 + 224 + 225 + 226 deleted per order (verbatim content preserved below).

## Bundled Checklist (All-or-Nothing)

- [220] Each follow-up has done criteria before implementation starts
- [220] Issue 8 closes after the first reviewed promotion lands
- [224] All three skill templates exist and are registered
- [224] README items 3-5 struck through as done
- [224] Full suite passes exit 0 with new contract tests
- [225] Executor carries the 7-seat roster table with triggers and duties
- [225] Load rules mirror auto_load Layers 1-2; anti-drift rule present
- [225] No behavior change: resolution stays local, no new Brain call
- [226] Suffixed ids are rejected before any session/model work
- [226] Bare numbers (incl. 01) and None one-offs still pass
- [226] Tool description states bare-number rule and history rationale

## Local TODOs

- [220] Define maturity levels L0–L3
- [220] Enforce consult-first with logging
- [220] Ship ranked retrieval with tests
- [220] Run first reviewed promotion
- [220] Verify functionality
- [224] Strike README items 3-5 as done (done)
- [224] Full suite + docs-sync + CHANGELOG (done, 317)
- [224] Brain QA + review, move to qa (done: QA_PASSED, APPROVED)
- [225] Roster section in executor (done, committed ad738af)
- [226] Numeric gate + tool description + contract tests (done, 321-green)
- [227] Inject full worktree diff below
- [227] Brain QA + review with bare numeric task_id 227

## Acceptance Criteria

- [ ] All four source parts are merged verbatim below with nothing dropped
- [ ] Full worktree diff is injected in Factual Git Diff
- [ ] Brain QA passes and Code Reviewer approves with bare numeric id 227

## Verification Evidence

- **Test command:** `uvx --with pytest --with pathspec --with mcp==1.30.0 --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-bash --with pyyaml python -m pytest tests/ -q` + `python3 scripts/check_docs_sync.py`
- **Expected result:** full suite passes; docs-sync OK
- **Actual result:** 321 passed, exit 0; docs-sync OK (orphan warn-only: fetch-opencode-docs.py, repomd)
- **Exit code:** 0

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** a source part is dropped in the merge
- **Rollback plan:** sources are preserved verbatim below; M2-style line check before QA

## Source Bundles (Verbatim Preservation)

### Source Task 220: Issue 8 follow-ups — maturity, consult-first, ranked retrieval, first promotion

## Goal

Track the deferred follow-ups of GitHub issue 8 (manager-decision skill remainder) from the team brainstorm. No implementation yet — do these in the future, in order.

## Manager's Notes

Vision (Manager, 2026-09-13): daily macro decisions (system design, architecture) across projects are stored smartly in one place; once enough accumulate and the digital identity matures, it is extracted as a working AI; then for simple to medium-hard questions the AI stops asking the Manager and follows similar past rulings instead. Current system stores well but does not reuse yet (27 records, substring search, profile never compiled, no consult gate).

Follow-ups (from brainstorm, also posted on issue 8):

1. Maturity levels L0–L3 with counts, coverage, override rate; human review gates promotion.
2. Consult-first rule: agent queries decisions and logs top-3 hits before asking the Manager; auto-follow above threshold, else escalate with search proof.
3. Ranked retrieval replacing substring search (filtered full-text first, embeddings later, with tests).
4. First reviewed promotion from the 27 live records: ruling clusters + dissent notes + expiry dates.
5. Deferred: full doppelganger runtime (unsafe at 27 records).

Risks tracked: stale auto-apply, false matches, redaction leaks, promotion drift.

## Acceptance Criteria

- [ ] Each follow-up has done criteria before implementation starts
- [ ] Issue 8 closes after the first reviewed promotion lands

## Local TODOs

- [ ] Define maturity levels L0–L3
- [ ] Enforce consult-first with logging
- [ ] Ship ranked retrieval with tests
- [ ] Run first reviewed promotion
- [ ] Verify functionality

## Risk & Rollback

- **Risk:** premature auto-follow on sparse data
- **Rollback plan:** keep human gate until maturity threshold passes; promotion is append-only

### Source Task 224: README roadmap trio META (testing-strategy, database-migration, hexagonal expansion)

## Goal

Deliver all three README roadmap items as skill templates, then strike them through in README as done.

## Manager's Notes

Manager order (Persian, verbatim core): define a META task for the 3 README items; all must be done and then removed/struck in README; fully on autopilot; research with blowsh; consult the admin-decisions skill when a decision is needed; everything clean within project standards. Project goal reminder (verbatim core): the main goal is always the strictest linter/tools that stop AI hallucination — every skill must serve it. stacks/ folder: delete only if leftover — audit verdict: LIVE (loop-engine profiles), do NOT delete.

## Bundled Checklist (All-or-Nothing)

- [221] `skill-templates/testing-strategy/SKILL.md` exists with TDD order, coverage gates, error-path rule
- [221] Registry lists the skill and consistency tests pass
- [221] Full suite passes exit 0
- [222] `skill-templates/database-migration/SKILL.md` exists with DDL ban, per-stack tool map, drift check
- [222] Registry lists the skill and consistency tests pass
- [222] Full suite passes exit 0
- [223] python-fastapi template carries a Hexagonal section with zero-framework-import rule
- [223] node-hexagonal-api template exists with ports/adapters/DI/testing rules
- [223] Registry + stacks yaml updated and consistency tests pass
- [223] Full suite passes exit 0

## Acceptance Criteria

- [x] All three skill templates exist and are registered
- [x] README items 3-5 struck through as done
- [x] Full suite passes exit 0 with new contract tests

## Local TODOs

- [221] Write testing-strategy SKILL.md + registry entry
- [221] Extend registry consistency tests
- [222] Write database-migration SKILL.md + registry entry
- [222] Extend registry consistency tests
- [223] Hexagonal section in python-fastapi template + new node-hexagonal-api template + registry + stacks yaml
- [223] Extend registry consistency tests
- [x] Strike README items 3-5 as done
- [x] Full suite + docs-sync + CHANGELOG
- [x] Brain QA + review, move to qa

## Risk & Rollback

- **Risk:** new Node template duplicates nextjs/react-vite coverage
- **Rollback plan:** node-hexagonal-api is backend-only; revert new templates + registry/yaml lines

(Inner bundles 221/222/223 live verbatim in the 224 file history; their content shipped as the three skill templates + registry/yaml lines in this worktree.)

### Source Task 225: Embed personas roster in cognitive-executor for local seat resolution

## Goal

Resolve Brain seats locally inside the executor without a Brain round-trip.

## Manager's Notes

Manager order (Persian, 2026-09-13, verbatim core): all personas must live inside cognitive-executor so seats resolve locally (sprint planning, project plans). No task file was wanted for the change itself — this record exists only for META bundling completeness. Implemented 2026-09-13: Brain one-off consult chose compact table (option A) + anti-drift rule (source file wins, same-commit update). `agents/cognitive-executor.md` gained a Personas Roster section (7-seat table + Layer 1/2 load rules + anti-drift note). Source of truth stays `prompts/fragments/06-personas.md`. Committed in ad738af (closure of META 219).

## Acceptance Criteria

- [x] Executor carries the 7-seat roster table with triggers and duties
- [x] Load rules mirror auto_load Layers 1-2; anti-drift rule present
- [x] No behavior change: resolution stays local, no new Brain call

## Local TODOs

- [x] Read personas source (06-personas.md, 64 lines)
- [x] Brain consult on compact-table vs full-embed
- [x] Append roster section to executor + docs-sync + CHANGELOG
- [x] Verify functionality

## Risk & Rollback

- **Risk:** roster drifts from personas source
- **Rollback plan:** anti-drift rule + same-commit update; revert section

### Source Task 226: Brain task_id numeric-only input validation

## Goal

Reject non-numeric Brain task_ids so per-task history never splits again.

## Manager's Notes

Manager correction (Persian, 2026-09-13, verbatim core): suffixed task ids (215qa, 215rev) split history — task number must stay a bare number, no prefix/suffix. Two jobs: (1) add input validation to the Brain MCP server rejecting non-numeric task_id; (2) rewrite the Brain tools' details/descriptions precisely (what a task is, that the id is numeric, why it must stay identical across a task's turns for history access). Implemented 2026-09-13 directly (small fix, no task file wanted at the time — this record exists only for META bundling completeness): `_TASK_NUMBER_RE` (^\\d+$) + `_require_task_number` fail-closed gate called FIRST in brain_turn; task_id tool docstring rewritten. Suite 321 passed exit 0, docs-sync OK, CHANGELOG entry added.

## Acceptance Criteria

- [x] Suffixed ids (215qa/215rev/215plan/224qa/219rev) are rejected before any session/model work
- [x] Bare numbers (incl. 01) and None one-offs still pass
- [x] Tool description states bare-number rule and history rationale

## Local TODOs

- [x] Diagnose suffix-split mechanism (allowlist regex + transcript dirs)
- [x] Migrate tests to numeric ids + 4 contract tests
- [x] Verify functionality

## Risk & Rollback

- **Risk:** legitimate callers pass suffixed ids and break
- **Rollback plan:** session dirs keyed by number; revert gate

---

## Execution Log & Reasoning

META 227 built per Manager bundle order. Sources 220 (backlog), 224 (qa), 225 + 226 (backlog) bundled verbatim above, then deleted; single task remains. 225's code change (executor roster) was already committed in ad738af; 226's change (numeric gate) plus 224's scope form the current worktree diff injected below.


## Review Verdict Note (Code Reviewer, bare task_id 227, 2026-09-13)

Status: PO_REVIEW_PENDING. Technically APPROVED, Low severity, no blocking defect, no hotfix XML.
Strengths F1-F7: digits-only gate, fail-closed FIRST in brain_turn, accept/reject/no-dir tests, 8 call sites numeric, new skills fill gaps, 321 passed exit 0.
Minor F8-F11: placeholder diff (no stage tool), unchecked lint (tool not connected), minor-bump-vs-breaking note, 01 accepted as-is.
Pre-closure hygiene A1-A3: inject real diff, run lint when tool returns, note breaking slug-reject in CHANGELOG.
Process proof: bare numeric task_id 227 kept full session history in ONE transcript (no qa/rev suffix split) — the gate works end to end.
Closure (2026-09-13, Manager: "Approved for closure"): qa→completed, status closed; commit via sanctioned MCP path (stage_and_inject_diff + commit_and_clean_task over MCP stdio).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `bb54bad35533b035a43286a2522ee85ba7a64c3d`
<!-- END_GIT_DIFF -->
