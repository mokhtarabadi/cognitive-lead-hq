# Task 398: English bridge and hybrid code-search

**File:** `tasks/completed/398-english-bridge-and-hybrid-code-search.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Started:** 2026-11-12T22:03:15Z
**Finished:** 2026-11-12T22:03:15Z
**Submitted:** 2026-11-12T21:48:00Z

## Goal

Make the harness English-only between Hands and Brain and make every code search use the new hybrid graph-vector system so docs, tasks, archive, code and comments are found in one hop.

## Manager's Notes

Manager ordered in English (autopilot locked):

1. You and Brain must ALWAYS talk in English even if the user talks in non-English. Translate every non-English user input to technical English, fix typos, then execute. No Persian (or any non-English) inside the Brain bridge.
2. Enhance the `code-search` skill and the discovery agents (`cognitive-discovery`) to use the new `mcp-context-server` hybrid system (`graph.py` comment nodes + `vector.py` fastembed/Chroma + `server.py` RRF fuse). The discovery lane is the primary consumer of that system, so it must be the first to benefit.

When finished: sync changes globally (all MCP servers + stage prompts to `~/.config/opencode`) and prove with a real hybrid retrieval test across docs, tasks, archived tasks and comments.

Lock: autopilot locked for this task (announced, followed to the end, never asking except hard blockers and Relay questions).

## Local TODOs

- [x] Harden the English bridge: `prompts/fragments/05-user_input_processing.md` + `prompts/fragments/24-language_policy.md` + `mcp-brain-bridge/server.py` prompt path
- [x] Enhance `code-search` skill to mandate hybrid graph-vector tools
- [x] Enhance `cognitive-discovery` agent instructions to use hybrid tools
- [x] Globally sync (all MCP servers + stage prompts) and restart
- [x] Real hybrid retrieval test across docs/tasks/archive/comments

## Acceptance Criteria

- [x] Every Brain prompt that ships from the repo is English-only (no Persian literal, no non-English example that leaks into the model)
- [x] Non-English user input is translated to technical English before any plan or discovery turn
- [x] `code-search` skill text names the hybrid tools (`graph.py` comment nodes, `vector.py` fastembed/Chroma, `server.py` RRF) and the caps (384-d, 512/50, 30, 2000, k=60)
- [x] `cognitive-discovery` instructions require `custom_context` hybrid tools as MCP-first, not native read
- [x] Hybrid retrieval test finds a doc, a live task, an archived task and a comment
- [x] Global install carries the new English bridge + hybrid skill and the restarted Brain serves it
- [x] Full test suite green and no persona lost

## Verification Evidence

- **Test command:** rtk test uv run --with pytest pytest tests/test_hybrid_graph.py -q
- **Expected result:** 5 passed, exit 0
- **Actual result:** 5 passed in 0.10s
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_stage_prompts.py -q
- **Expected result:** 17 passed, exit 0
- **Actual result:** 17 passed in 0.96s
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q
- **Expected result:** 854+ tests pass, exit 0
- **Actual result:** 854 passed, 24 warnings in 56.15s
- **Exit code:** 0
- **Test command:** bash /tmp/opencode/smoke-hq.sh
- **Expected result:** ALL CHECKS PASSED
- **Actual result:** ALL CHECKS PASSED (7 personas / 1 qa persona, 603518 total, persona 7/1 intact)
- **Exit code:** 0
- **Test command:** rtk test custom_context_query_graph hybrid (doc:"architecture data model" + live:"lean hybrid graph" + archived:"archived task 0385" + comment:"handle lease on exit") -q
- **Expected result:** 4 HIT (one per surface)
- **Actual result:** 4 HIT (doc HIT, live task HIT, archived HIT, comment HIT via comment node + RRF k=60)
- **Exit code:** 0
- **Test command:** grep -c '<persona name=' system-prompt.md && grep -c '<persona name=' build/stage-prompts/system-prompt.qa.md && grep -P "[\x{0600}-\x{06FF}]" system-prompt.md | wc -l (outside quoted)
- **Expected result:** 7 / 1 / 0 outside quoted (English-only)
- **Actual result:** 7 / 1 / 0 outside quoted (the single quoted Persian trigger "کار امروز رو شروع کنیم" inside quotes is evidence, not Brain output)
- **Exit code:** 0
- **Test command:** openchamber_render native check (skill executor always renders 3+ items via openui-lang Stack/Table and speaks simple fluent English)
- **Expected result:** render path enforced in agents/cognitive-executor.md, code-search skill keeps MCP-first hybrid without output format
- **Actual result:** verified via grep + file read: executor has Output Contract simple fluent English via openchamber_render, code-search has no Output Format section
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Forcing English-only could drop a user-provided Persian code comment or identifier that must be preserved verbatim.
- **Rollback plan:** The English bridge is data wording inside skill fragments and prompt fragments: revert those two fragments and rebuild the prompt. The hybrid skill text is additive — revert is deleting the added `hybrid` section, no data migration.

---

## Execution Log & Reasoning

Harnened English bridge by appending the invariant to 05 + 24; enhanced code-search skill with 6-step hybrid workflow mentioning graph comment nodes 80/50, vector 512/50 2000, RRF k=60 and caps; enhanced cognitive-discovery to require custom_context hybrid as MCP-first. Globally synced via assemble + rsync to ~/.config/opencode and restart verified via smoke. Hybrid proof 4 HIT via query_graph demonstrates doc/live/archived/comment retrieval without losing persona 7/1.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `6a29e57e61aa2f3650eaead70d92e0aae14d5731`
<!-- END_GIT_DIFF -->
