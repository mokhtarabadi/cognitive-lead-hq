# Task 423: Portable Release Skill, Omitted-Output Recovery, and Brain Orchestration Skill

**File:** `tasks/completed/423-portable-release-omitted-output-brain-skill.md`
**Source:** manager
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-24T07:57:57Z
**Submitted:** 2026-11-24T07:24:54Z
**Estimate:** 6h
**Deadline:** 2026-11-25
**Started:** 2026-11-24T06:59:43Z

## Source Context

## Goal

Make the release skill portable across harness projects, guarantee that important omitted tool output is recovered before the executor acts, and add a reusable Brain orchestration skill that explains the platform's roles, stages, and working method.

## Manager's Notes

- Verbatim request: "Two items should be addressed in a new task: 1. Is skill template versioning currently specific to our project? If so, refactor it so it can be used by all projects that use this harness. 2. Sometimes, when the output from tools called by the OpenCode agent exceeds a certain limit, it gets truncated. OpenCode has a tool called 'Read Omitted Content'; find it in your tool list to understand exactly what it does. Integrate it into the Cognitive Executor agent so that when important tool output—especially from Brain—is omitted, the agent reads the rest using the Read Omitted Content tool and doesn't miss anything. I'd also like to see whether Brain's particular way of working could be defined as a skill template describing its features, who participates, what roles it has, which roles are used for design, and how it can be used for programming, brainstorming, and other tasks."
- Research finding: `skill-templates/versioning-and-release/SKILL.md` is still harness-specific. It hard-codes `AGENTS.md`, `DESIGN.md`, `tasks/`, `system-prompt.md`, and `custom_context_*` tools at lines 60, 65-81. The portable core must remove project assumptions while an optional harness profile preserves HQ safeguards.
- Research finding: `read_omitted_content` is a real Code Mode tool: `tools.read_omitted_content({contentId: "omitted-NNNN"})`. It returns the session-cached original, possibly stale, capped at 20,000 characters with an explicit truncation notice. Use only when the original cannot be reproduced cheaply; on cache miss, re-run the source once.
- Research finding: the executor already mentions `read_omitted_content` in `agents/cognitive-executor.md:130-135`, but it lacks a mandatory decision tree for critical omitted output and does not explicitly separate cache recovery from Brain's `output_address` artifact recovery at lines 599-616.
- Research finding: Brain documentation already exists in `mcp-brain-bridge/README.md`, `docs/brain-bridge.md`, the stage manifest, and the seven persona slices. The new skill must distill those sources rather than invent a second contract.
- Scope assumption A1: all three requests become one task because they share the same harness portability, executor reliability, and skill-registry surfaces.

## Local TODOs

- [x] Audit the versioning skill and classify each rule as portable core, optional harness profile, or project-specific documentation
- [x] Refactor the versioning skill into a portable core plus optional harness profile without losing release safeguards
- [x] Add regression tests that reject HQ-only names and paths in the portable core
- [x] Add a mandatory omitted-output recovery decision tree to `agents/cognitive-executor.md`
- [x] Distinguish Smart Compact `omitted-NNNN`, Code Mode `truncated: true`, and Brain `[brain-output]` / `output_address` recovery paths
- [x] Add tests for executor recovery wording, tool signature, 20,000-character cap, stale-cache warning, and cache-miss retry
- [x] Create a `brain-orchestration` skill template grounded in the real Brain Bridge, stages, roles, gates, and output contracts
- [x] Register `brain-orchestration` in the skills registry and update skill-catalog counts and sibling docs
- [x] Keep the new skill's global copy byte-identical and exclude README/DECISIONS from the global skill directory
- [x] Bump the system-prompt version, regenerate the full prompt and all stage prompts, and pass the freshness gate
- [x] Update CHANGELOG, dated ADRs, and task evidence; deploy the regenerated artifacts without restarting services

## Acceptance Criteria

- [x] The versioning skill's portable core contains no HQ-only identifiers such as `AGENTS.md`, `DESIGN.md`, `tasks/`, `system-prompt.md`, or `custom_context_*`
- [x] Harness-specific release safeguards remain available through a clearly labeled optional profile
- [x] `agents/cognitive-executor.md` mandates recovery before acting on important omitted output and names the exact `read_omitted_content` signature
- [x] The executor distinguishes cache omission, Code Mode truncation, and Brain artifact stubbing, with one bounded retry on cache miss
- [x] A new `brain-orchestration` skill template describes features, participants, all seven roles, seat routing, stages, design, programming, brainstorming, QA, review, and closure
- [x] The Brain skill names only real tools and stages and preserves Manager approval and ZAC gates
- [x] The skill registry, template count, global copy, sibling README/DECISIONS files, and tests are synchronized
- [x] The full test suite passes with exit code 0 and fresh evidence is recorded
- [x] Full and stage prompts are regenerated, byte-checked, and deployed without a Hands-performed restart

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/ -q
- **Expected result:** all tests pass, including portability, registry, executor recovery, and Brain-skill contract checks
- **Actual result:** 1010 passed, 23 warnings. Includes portable-core, harness-profile, omitted-output recovery, Brain-skill contract, registry, stage freshness, and tool-catalog checks.
- **Exit code:** 0
- **Additional gates:** targeted 72 passed exit 0; docs-sync exit 0; freshness gate exit 0 for full plus 8 stages; all 9 artifacts at 9.95.0; full/stage/global skill `cmp` exit 0; format-guard exit 0; Brain-skill HQ-path grep exit 1; portable-authority count 1; memory rule stored and found.

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-generalizing the release skill could remove ZAC, approval, or task-tracking safeguards. A recovery loop could repeatedly fetch stale or capped content. A Brain skill could drift from the real bridge contract.
- **Rollback plan:** Restore the prior versioning skill and executor sections, remove the new skill and registry row, decrement the version marker, regenerate prompts, and re-run the full suite. Keep the optional harness profile as the authoritative HQ safeguard during rollback.

---

## Execution Log & Reasoning

Brainstorm: not required — reversible, grounded work without hard-to-reverse ambiguity.
Plan verdict: XML_EXTRACTED from Senior Programmer; five-phase plan approved via question tool.
Approval (question-tool answer value): "Approved - issue task 423 (Recommended)".
Seat routing: Software Architect, Senior Programmer, QA Engineer; UI/UX Designer, Project Planner, Sprint Strategist, Code Reviewer skipped for lack of UI, capacity, priority, or review-stage decisions.
Scope assumption A1: all three Manager requests are one task because they share portability, executor reliability, and skill-registry surfaces.
Assumption A2: approved 6h estimate has no deadline, so schedule uses 2026-11-25 to satisfy the planner's required deadline field.
Assumption A3: the approved portable-core body required the label `Parallel sessions` for the Step 3 gate but did not contain that exact phrase; added the label without changing the rule.
Assumption A4: the approved Step 5 target `tests/test_versioning_release_skill.py` does not exist; replaced it with the real Conventional Commit assertions in `tests/test_mcp_servers.py`. Result: 33 passed, exit 0.
- [x] Step 1: claim task and schedule 6h
- [x] Step 2: rewrite versioning skill as portable core plus harness profile
- [x] Step 3: verify portability classification gates
- [x] Step 4: add versioning portability tests
- [x] Step 5: run portability and release/skill tests
- [x] Step 6: insert mandatory omitted-output recovery gate
- [x] Step 7: add executor cross-references and verify count
- [x] Step 8: add executor recovery tests
- [x] Step 9: run executor recovery tests
- [x] Step 10: create brain-orchestration skill
- [x] Step 11: register brain-orchestration without plugin literals
- [x] Step 12: add Brain skill contract tests
- [x] Step 13: sync skill counts to 25
- [x] Step 14: run registry and Brain skill tests
- [x] Step 15: bump system version to 9.95.0
- [x] Step 16: regenerate full and 8 stage prompts; run freshness gate
- [x] Step 17: deploy 9 prompt artifacts without restart
- [x] Step 18: sync both global skill copies
- [x] Step 19: update READMEs and ADRs with HTML-comment provenance
- [x] Step 20: add isolated 9.95.0 CHANGELOG entry
- [x] Step 21: run and record all final verification gates
Phase 1 evidence: portability tests and real Conventional Commit/skill tests 33 passed exit 0 after replacing the nonexistent approved target with `tests/test_mcp_servers.py`.
Phase 2 evidence: executor recovery tests 3 passed exit 0; gate cross-reference count 3.
Phase 3 evidence: registry/Brain-skill tests 28 passed exit 0; live `24 templates` grep exit 1; global skills shape confirmed 24 directories before adding the new skill.
Phase 4 evidence: full/stage assembly exit 0; freshness exit 0; all 9 artifacts report 9.95.0; full prompt contains `brain-orchestration` once; deployed full plus 8 stage artifacts and both global skill copies compare byte-identical exit 0; no restart performed.
Final gates: targeted 72 passed exit 0; full suite 1010 passed, 23 warnings, exit 0; docs-sync exit 0; freshness exit 0; format-guard exit 0; Brain-skill HQ-path grep exit 1; portable-authority count 1.
Memory: stored `architecture/skill-template-portability-rule`; `search_memory` returned the shard. No task progress was saved.
CHANGELOG isolation: foreign snapshot count 2; staged only the second diff hunk containing 9.95.0 via index-only `git apply --cached`; staged foreign-phrase count 0. CHANGELOG is intentionally excluded from `qa_transition.modified_files` so its isolated hunk is not overwritten.
QA round 1: QA_PASSED. No blocking defect. Non-blocking recommendations R2-R4 concern defensive test slicing, exact cross-reference count, and an explicit heading-order assertion.
Code review round 1: PO_REVIEW_PENDING — technically approved. Disclosed low deviation F1: the isolated CHANGELOG hunk was staged with index-only `git apply --cached`; outcome verified safe, foreign content excluded, no commit. Informational F2-F4 match QA test-hardening recommendations.
Manager closure approval (question-tool answer value, verbatim): "Approved for closure".
- [x] Step 22: store portability rule in project memory
Rule correction: the approved Step 10 initially hard-coded HQ repository paths in the skill template; halted and reissued with portable deployed-contract wording. Test-enforced by `tests/test_brain_orchestration_skill.py`.
Parallel-session isolation: unstaged changes in `.env.example`, `CHANGELOG.md`, `LLM.txt`, `docs/brain-bridge.md`, `docs/zen-proxy.md`, `mcp-brain-bridge/DECISIONS.md`, `mcp-brain-bridge/README.md`, and `zen-proxy/*` belong to another session and must not be edited or staged.
Baseline: `rtk test uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml pytest tests/ -q` → 998 passed, 23 warnings, exit 0, before source edits.
Discovery A: only live hard-coded count is `skill-templates/README.md:9` (`24 templates`); no numeric count assertion in `tests/test_skill_registry.py`. History mentions are immutable and out of scope.
Discovery B: global skills root is `/home/mohammad/.config/opencode/skills`; 24 per-skill directories, each with `SKILL.md` only, no README/DECISIONS.
Discovery C: deploy block is `scripts/release-9.66.0.sh:39-47`; full prompt plus eight stage artifacts are copied and compared; restart line exists but Hands must not execute it.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `5a2d334b6c567d3a9285a413e839b376560a2339`
<!-- END_GIT_DIFF -->
