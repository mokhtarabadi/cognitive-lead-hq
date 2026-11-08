# Task 0378: Brain keeps saying "context ندارم" — discovery-fed grounding gap

**File:** `tasks/completed/0378-brain-discovery-fed-grounding-gap.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-11-06T08:18:28Z
**Submitted:** 2026-11-06T08:09:34Z

## Goal

End the planning-loop stall where the Brain answers a fed discovery round with a second `<missing_context>` list: make the Hands feed verbatim file bodies (via `context_paths` and/or capped verbatim ranges inside `[fed-context]`), because prose summaries alone never satisfy the Brain's No-Hallucination + Strict Grounding rules.

## Manager's Notes

Persian verbatim: "مشکل برین رو هم حل من ... چرا هی میگه کانتکس ندارم ... باگ و gap رو پیدا کن ... به خود برین بگو self improvement ... یادت میده چطوری با هم مشکل برین رو پیدا منید و تسکش کنید ... و حلش کنید"

Translation: fix the Brain problem too — why does it keep saying it has no context; find the bug and the gap; tell the Brain itself (self-improvement); learn how to find the Brain problem together, task it, and solve it.

## Root cause (verified in repo truth, case: dumble 1046)

F1 — Hands fed prose, not bodies. `agents/cognitive-executor.md` "Discovery-fed planning" says to feed results back "with the fed context marked by a `[fed-context]` block", and the file-context line says to "pull the needed code ranges and feed them into the next turn as `[fed-context]`". Neither sentence requires verbatim bodies or `context_paths`. In the 1046 loop the Hands fed citation-style prose (`- file:line claim...`, no bodies). The Brain's No-Hallucination rule (`system-prompt.md` constraint: missing critical files → STOP + `<missing_context>`) and Strict Grounding rule (claims must rest on directly-observed content; missing info → request discovery, never guess) cannot verify prose-about-code, so the second `missing_context` was the contractually correct output — the loop mechanics did not fail, the fed material did not qualify as grounding.

F2 — `context_paths` sat unused. The bridge reads real files server-side (`mcp-brain-bridge/server.py`, `context_paths` attach with per-file/total caps, `#Lstart-end` slices, truncation notes the narrowing rule understands per ADR-010). The 1046 retry turn passed no `context_paths`. The exact tool built for this starvation was never called.

F3 — bridge pin + narrowing are healthy. The `[fed-context]` pin is saved and prepended on later turns (server.py `save_fed_context` / `load_fed_context`), and the second request correctly narrowed to ranges instead of repeating whole files. No bridge code change is indicated; the gap is purely the Hands-side feeding contract.

## Local TODOs

- [x] Amend "Discovery-fed planning" in `agents/cognitive-executor.md`: a fed retry MUST carry verbatim code (capped ranges) and/or `context_paths=[paths]`; a prose-only `[fed-context]` is a protocol violation that predicts a second `missing_context`.
- [x] Mirror the one-line rule at the file-context retrieval line (same file) so both instructions agree.
- [x] Add a regression test in `tests/test_prompt_sync.py` pinning the new contract sentences (red-first, then green).
- [x] Sync the live global agent copy (same pattern as task 0352) and verify byte-identical.
- [x] Living docs: `agents/DECISIONS.md` ADR + `agents/README.md` invariant if it names the contract.
- [x] CHANGELOG entry; full HQ suite green; `lint_task_file` green.

## Acceptance Criteria

- [ ] The executor names prose-only fed-context as a violation and mandates verbatim ranges and/or `context_paths` on the retry turn.
- [ ] The regression test fails on the old text and passes on the new text.
- [ ] Live agent copy matches the repo file byte for byte.
- [ ] Full suite green and `lint_task_file` green.

## Verification Evidence (Phase 1)

- **Test command:** `uv run --project mcp-brain-bridge --with pytest python -m pytest tests/test_prompt_sync.py -q` (new test red-first, then green) + full HQ suite
- **Expected result:** new contract test fails before the doc edit, full suite green after
- **Actual result:** new test FAILED pre-edit (`AssertionError`), `test_prompt_sync.py` 24/24 post-edit; full HQ suite `784 passed` (with `--with pyyaml`; 6 memory-server tests fail without it — pre-existing env-only `ModuleNotFoundError: No module named 'yaml'`, unrelated files); live copy `diff` exits 0
- **Exit code:** 0

## Verification Evidence (Phase 2 hotfix)

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_prompt_sync.py -q`
- **Expected result:** 24/24 green; no added task-number refs in the four files; hand-edited hunks whitespace-clean
- **Actual result:** 24/24 green (exit 0); `grep -E '^\+[^+].*(0378|0361)'` on the four-file diff → no hits; `git diff --check --cached` exit 0; plain `git diff --check` flags only lines inside the MCP-injected `BEGIN_GIT_DIFF` block (verbatim staged-diff reproduction, MCP-owned, not hand-editable — recorded, not fixed)
- **Exit code:** 0 (tests), 0 (cached check)
- **Stack-gate skip:** `root=.`, scanned `requirements*.txt`/`pyproject.toml`/`package.json`/`go.mod`/`*.sln`, `matched=[]`, `reason=no matching stack marker for this documentation-only hotfix`

## Definition of Done

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** verbatim bodies inflate the retry prompt; mitigated by existing `context_paths` caps and `#L` slices, which the contract points at instead of whole files.
- **Rollback:** revert the executor paragraphs and the regression test; the old stall behavior returns.

## Phase 2 — full codemode reversal (Manager override, appended 2026-11-06)

Manager decision: full reversal of the 0361 policy — every MCP server goes to Code Mode (`codemode: true` default), appended to THIS task (not a new one) by explicit Manager choice. Phase 1 above is untouched and stays verified as-is.

### Phase 2 TODOs

- [x] Timestamped backup of global `~/.config/opencode/opencode.json`, then remove `"codemode": false` from the six in-house servers (explicit default `true` restored)
- [x] Validate JSON + prove resolved values (six `True`, telegram unchanged)
- [x] Update `docs/services.md` policy table, `docs/setup.md`, `README.md` block, `LLM.txt` install block, memory `workflows/codemode-policy`
- [x] CHANGELOG entry; `lint_task_file` green; back to qa

### Phase 2 Acceptance Criteria

- [ ] Global config parses as JSON; all six in-house servers resolve `codemode=True`, telegram entry untouched
- [ ] All five doc/memory surfaces name the Code-Mode-for-all policy
- [ ] `lint_task_file` passes

---

## Execution Log & Reasoning

- Seat Check: single-slice prompt-contract fix (executor prose + prompt-sync test) → Senior Programmer; the word "contract" in the body names a process contract, not an API/schema contract, so no Architect seat. Brainstorm: not required — single-discipline, fully reversible doc change.
- F1 (verified `agents/cognitive-executor.md:387-400`, `system-prompt.md:502,511`, `mcp-brain-bridge/server.py:3887-3911`): Hands fed prose summaries; Brain's grounding rules cannot verify them; second `missing_context` contractually correct. F2: `context_paths` unused on the retry (server.py `build_paths_attach` + caps + `#L` slices). F3: pin + ADR-010 narrowing healthy — no bridge code change.
- Red-first: new test failed pre-edit as designed; green post-edit (24/24). Live copy synced via `cp`, `diff -q` exits 0.

## Execution Log & Reasoning (Phase 2 hotfix — QA_REJECTED → fix)

- QA rejected Phase 2 for F1: task-number provenance in four prompt-facing policy files (repo task-number discipline). Removed the IDs from `README.md`, `docs/services.md`, `docs/setup.md`, `.opencode/memory/workflows/codemode-policy.md`; policy meaning and dates unchanged; provenance stays in CHANGELOG + task record.
- Stack-gate skip: `root=.`, scanned `requirements*.txt`/`pyproject.toml`/`package.json`/`go.mod`/`*.sln`, `matched=[]`, `reason=no matching stack marker for this documentation-only hotfix` (`python-fastapi` loaded for discipline only, no FastAPI coverage claimed).

- 0378 moved qa → in-progress for the appended scope per Manager order; Phase 1 hunks untouched.
- Config: `cp` backup `opencode.json.bak-20261106-0378` beside the live file, then 6× `"codemode": false` → `"codemode": true` (explicit, auditable). `python3 json.load` proves six `True`, telegram key absent (= default true, untouched).
- Live proof: this session's Code Mode catalog refreshed in place — `brain`, `custom_context`, `lint`, `planner`, `project_memory`, `blowsh`, `telegram` all now route via `execute` (the lint call above ran through `tools.lint.lint_task_file`).
- Quirk: `test_prompt_sync.py::test_executor_has_no_code_references` still green — the new paragraphs carry only tool names and `#L` slice syntax, no file:line citations.
- Code review fix F2: strengthened the prompt-sync regression test to assert the normative MUST clause and mirrored file-context rule, preventing non-binding wording or mirror removal from passing.
- Rollback: restore the backup over `opencode.json` + revert the doc hunks; restart the session to reload the catalog.

## Autopilot QA/Review trail (ses_e503e3521ffe8bJlwT8TOIfBCP)

- QA round 1: `QA_REJECTED` (F1 task-number provenance in four prompt-facing files) → hotfix applied → re-QA: `QA_PASSED`.
- Review round 1: `APPROVED_WITH_CHANGES` (F2 weak regression assertions) → test strengthened → final review: technically `APPROVED`, `PO_REVIEW_PENDING`.
- Manager accept quote: "Approved for closure".

## Code Review Fix Checklist (F2 — APPROVED_WITH_CHANGES)

- [x] **Step 1:** Strengthened `test_executor_fed_context_requires_verbatim_or_paths` to normalize whitespace and assert the full MUST clause + mirror rule (fixed one mismatch: mirror heading is bold `**...:**` in the executor). Targeted test green.
- [x] **Step 2:** Execution-log note + CHANGELOG entry appended; `git diff --check -- tests/test_prompt_sync.py CHANGELOG.md` exit 0.
- [x] **Step 3:** Full `test_prompt_sync.py` 24/24 green; `py_compile` clean (no LSP tool in session — compile check substituted, recorded); evidence updated; lint green; diff re-injected via `stage_and_inject_diff`.

## Code Review Fix Checklist (F1 stale rationale — second review round)

- [x] **Step 1–2:** Task back to in-progress with header sync; replaced the obsolete split rationale in `docs/services.md` with the uniform-policy sentence; no other file touched.
- [x] **Step 3–4:** CHANGELOG line appended under the current `### Fixed`; fix note + evidence recorded here; stack-gate skip `root=. markers=[requirements*.txt, pyproject.toml, package.json, go.mod, *.sln] matched=[] reason=docs-only review fix`.
- [x] **Step 5–8:** Verification below; task back to qa via `qa_transition`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `e2158b71d99ee6853d60898f4664b8ceb44ece5b`
<!-- END_GIT_DIFF -->
