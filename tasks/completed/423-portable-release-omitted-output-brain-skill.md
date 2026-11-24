# Task 423: Portable Release Skill, Omitted-Output Recovery, and Brain Orchestration Skill

**File:** `tasks/qa/423-portable-release-omitted-output-brain-skill.md`
**Source:** manager
**Type:** improvement
**Status:** in-progress
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
```diff
diff --git a/.opencode/memory/architecture/skill-template-portability-rule.md b/.opencode/memory/architecture/skill-template-portability-rule.md
new file mode 100644
index 0000000..46ebedf
--- /dev/null
+++ b/.opencode/memory/architecture/skill-template-portability-rule.md
@@ -0,0 +1,7 @@
+---
+tags: [architecture, skills, portability]
+---
+
+Skill templates are project-agnostic; harness-specific names belong only in an optional profile or deployed-contract wording.
+
+Rule: Skill template bodies must not hard-code harness identifiers (AGENTS.md, DESIGN.md, tasks/, system-prompt.md, custom_context_*) or HQ repository file paths (docs/brain-bridge.md, mcp-brain-bridge/README.md, prompts/stage-manifest.json). Platform concepts may be named; file locations are referenced only as the deployed runbook or deployed stage manifest. Enforced by tests/test_versioning_skill_portability.py and tests/test_brain_orchestration_skill.py. Registry prompt lines must never carry plugin literals.
diff --git a/.opencode/memory/index.md b/.opencode/memory/index.md
index 43b980f..a629b78 100644
--- a/.opencode/memory/index.md
+++ b/.opencode/memory/index.md
@@ -8,6 +8,7 @@
 | architecture | mcp-tool-output-addressing | # MCP tool output and input strings address the calling agent | mcp, tool-output, agent-facing, conventions |
 | architecture | responses_api_best_practice_audit_2026_10_21 | # Responses API best-practice audit (2026-10-21) — Brain Bridge |  |
 | architecture | responses_api_provider_diagnostics | # Responses-API servers must surface provider diagnostics |  |
+| architecture | skill-template-portability-rule | Skill templates are project-agnostic; harness-specific names belong only in an optional profile or deployed-contract ... | architecture, skills, portability |
 | architecture | zen-proxy-ownership | # zen-proxy is owned by this repo (2026-10-23) | zen-proxy, gateway, brain-provider, systemd, global-install |
 | opencode_config | blowsh_image_policy | # Blowsh image and proxy policy — two optional backends (supersedes direct-only rule) | blowsh, docker, images, opencode, proxy |
 | opencode_config | brain-deepseek-fixes-2026-11-22 | # Brain DeepSeek hardening (2026-11-22) |  |
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 665c984..366785d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -40,6 +40,25 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Prompt and workflow hardening META 417 (tasks 414/415/416):** reconciled the manual/automatic topology across both DECISIONS files, `docs/architecture.md` and the executor (superseded-note, single finalization sequence, one mode template per autonomy level, no escape-hatch OR); consolidated approval literals and ZAC into single normative blocks with per-surface actors; rebound the brainstorm panel to the Personas Roster with the multi-label carve-out; added the mandatory Context Map Before Brain Calls contract (turn classes A/B/C, audit line, forbidden shapes) to the executor, discovery agent, READMEs, `AGENTS.md` and the governance audit template; added the direct-input plan gate and Brain context-before-plan rule; removed the Template Preservation rule, the duplicate QA/review invocation, the duplicate Strict Tooling Gate sentences and the phantom `@google/design.md` lint command; verified no fragment path and no roster pointer reaches the assembled prompt (the roster is inline) and the Browser-facing prompt carries no fragment-file references. `01-system_version.md` bumped 9.90.1 to 9.92.0 (phases 1B and 2 consolidated into one cycle), `system-prompt.md` regenerated, prompt-sync suite 66 passed (44 existing + 22 new regression assertions: 14 plan-round plus 8 QA-round).
 
+## [9.95.0] - 2026-11-24
+
+### Added
+
+- Portable Harness Profile for the versioning skill, keeping universal release rules separate from Cognitive Lead safeguards.
+- `brain-orchestration` skill template describing participants, seven seats, stages, modes, approvals, context maps, and output recovery with portable deployed-contract wording.
+- Mandatory omitted-output recovery gate in the Cognitive Executor, with distinct bounded routes for Smart Compact cache omissions, Code Mode truncation, and Brain output-address stubs.
+
+### Changed
+
+- Skill registry and template catalog now list 25 templates.
+- System version bumped to 9.95.0; full prompt and all eight stage artifacts regenerated and freshness-checked.
+
+### Fixed
+
+- None (improvement task).
+
+Changed files: `skill-templates/versioning-and-release/SKILL.md`, `skill-templates/brain-orchestration/SKILL.md`, `skill-templates/README.md`, `skill-templates/DECISIONS.md`, `agents/cognitive-executor.md`, `agents/README.md`, `agents/DECISIONS.md`, `prompts/fragments/01-system_version.md`, `prompts/fragments/07-agent_skills_registry.md`, `prompts/fragments/DECISIONS.md`, `system-prompt.md`, `tests/test_versioning_skill_portability.py`, `tests/test_executor_recovery_gate.py`, `tests/test_brain_orchestration_skill.py`, `tests/test_prompt_sync.py`, `tests/README.md`, `.opencode/memory/architecture/skill-template-portability-rule.md`, `.opencode/memory/index.md`. Task 423. No commit from Hands.
+
 ## [9.94.1] - 2026-11-24
 
 ### Added
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index edaef88..f7d526b 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -240,3 +240,14 @@ Context: The executor carried two competing numeric length budgets and a duplica
 Decision: Both agent contracts now carry the Manager-Facing Concision Contract verbatim, with the executor's duplicate bullets retired and its Output Contract phrase aligned; the retired Type Drift Sentinel sentence now assigns the gate to manual review.
 Consequences: One user-facing response rule across prompt, executor, and discovery agent; internal channels and frozen pipeline strings stay comprehensive and unchanged.
 Rollback: Restore the prior bullets and final sentence from git history, decrement the version marker to 9.93.0, regenerate the prompt, and re-run both lints.
+
+<!-- provenance: tasks/in-progress/423-portable-release-omitted-output-brain-skill.md -->
+
+## Mandatory omitted-output recovery gate
+
+Date: 2026-11-24
+Status: accepted
+Context: The executor mentioned cache retrieval but did not require recovery before acting on important omitted output, and it mixed three distinct loss paths.
+Decision: Add a mandatory gate separating Smart Compact cache omission, Code Mode truncation, and Brain output-address stubbing, with bounded retries and live-file checks for cached code.
+Consequences: Important plans, verdicts, XML blocks, and evidence are recovered before use; an unrecoverable loss is logged and surfaced instead of guessed.
+Rollback: Remove the gate section and its two cross-references, then regenerate the prompt and re-run the suite.
diff --git a/agents/README.md b/agents/README.md
index 0d0f132..1564800 100644
--- a/agents/README.md
+++ b/agents/README.md
@@ -21,6 +21,7 @@ Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary execu
 - OpenUI validity gate: every `openchamber_render` program is self-checked before the call — exact component signatures, plain string or number `Table` cells, balanced brackets, no named arguments, one statement per line. An arity diagnostic is treated as a source defect, not a renderer bug.
 - Render call envelope: `openchamber_render` takes `action: "render.page"` and `parameters` as a real object, never a JSON-encoded string. The executor self-checks the envelope before the program; a `parameters: Expected object` error is rebuilt, never retried verbatim.
 - No runtime code here; changes are prompt-contract changes with system-wide effect.
+- Omitted-output recovery is mandatory: important Smart Compact, Code Mode, and Brain pointer losses use distinct bounded routes before the executor acts.
 
 ### Free-tier bash gate
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index c311ac5..fade581 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -127,7 +127,7 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
 Context is finite. Two layers of tooling keep long sessions productive — the plugin's own awareness rides on the second — and the agent's durable state lives in the task file and project memory, never only in the chat.
 
 1. **Native safety net.** OpenCode auto-compacts near the model limit: it replaces older turns with one lossy summary and keeps the most recent ~20k tokens (config: `compaction.keep.tokens`). Never depend on it to preserve working state — write the essentials to the task file as you go.
-2. **Smart Compact.** Installed globally and loaded by OpenCode. It keeps your user messages verbatim, condenses each old assistant turn, and prunes bulky tool output into a retrievable cache. It never mutates the stored transcript. Pressure is measured against a working budget, not the model ceiling: this repo pins a 200k budget with a reminder at 120k and an emergency at 160k in `.opencode/smart-compact.jsonc`. Below the reminder line it trims tool output on its own, so a tool result reading as a notice is the plugin working, and the original is one `read_omitted_content` call away. The Manager runs `/magic-compact`, `/magic-trim`, and `/magic-stats`; you cannot. What you can do: call `compact_context` yourself when context is heavy (`keepTurns` protects recent turns, `mode: "trim"` prunes tool output only), call `compact_stats` when you need to know whether a compaction reclaimed anything, and use `read_omitted_content` with its Content ID (`omitted-NNNN`) only when the pruned output cannot be reproduced cheaply. Prefer a cheap fresh run of the source tool; on a cache miss, re-run it once. Never re-run a source tool for output you can retrieve by Content ID.
+2. **Smart Compact.** Installed globally and loaded by OpenCode. It keeps your user messages verbatim, condenses each old assistant turn, and prunes bulky tool output into a retrievable cache. It never mutates the stored transcript. Pressure is measured against a working budget, not the model ceiling: this repo pins a 200k budget with a reminder at 120k and an emergency at 160k in `.opencode/smart-compact.jsonc`. Below the reminder line it trims tool output on its own, so a tool result reading as a notice is the plugin working, and the original is one `read_omitted_content` call away. The Manager runs `/magic-compact`, `/magic-trim`, and `/magic-stats`; you cannot. What you can do: call `compact_context` yourself when context is heavy (`keepTurns` protects recent turns, `mode: "trim"` prunes tool output only), call `compact_stats` when you need to know whether a compaction reclaimed anything, and use `read_omitted_content` with its Content ID (`omitted-NNNN`) only when the pruned output cannot be reproduced cheaply. Prefer a cheap fresh run of the source tool; on a cache miss, re-run it once. Never re-run a source tool for output you can retrieve by Content ID. Recovery of any important omitted output is mandatory — apply the Omitted-Output Recovery Gate section.
    Task file is the sole reconcile target. Smart Compact via `compact_context` is the sole pruning writer; native auto-compact is a lossy safety net only and is never relied on for state. After any compaction resume from the task file and re-apply pruning through the sole writer.
 
 3. **Survival contract.** Keep the task file holding: the active task id and Kanban lane, the pinned `[fed-context]` block with citations, the current persona/seat, the locked mode (manual or autopilot), the latest staged diff hash, open blockers, and the next action. Resume from that file after any compaction — never from a summary.
@@ -145,6 +145,18 @@ Context is finite. Two layers of tooling keep long sessions productive — the p
 - Goal sync rule (executor behavior, plugin untouched): Hands performs three mandatory goal writes per goal — create, evidence, complete — plus two conditional ones (block, resume), all with these exact signatures — `goal_set(title)`, `goal_block(reason)`, `goal_evidence(id, claim, files[], tests[{command, exitCode, env?}])`, `goal_complete()` (no arguments), `goal_resume()` (no arguments). WHEN: `goal_set` when an objective is defined (an XML implementation arrives or the Manager defines a new objective in chat) — the lane is unreachable without it, since no other call creates a goal; `goal_block` when blocked; `goal_evidence` then `goal_complete` at closure; `goal_resume` after a block, an interruption, or an idle-park (an `active` goal whose loop parked itself waiting on you). Evidence gate: every criterion needs one existing file inside projectDir AND every recorded test command to exit 0, else completion is blocked and the reply names the cause — `Complete blocked: <reason> — <failures>` quoting up to five concrete failures (for example `test-failed:<id>:exit=1`, `missing-file:<id>:<path>`, `test-budget:<id>`), so fix the named cause instead of guessing. A test entry may carry an optional flat `env` map of string values, merged over the host environment for that command only, which is how a proof command pins the toolchain it needs (a JDK, an SDK path) instead of smuggling it into the command string; unknown or non-string values are rejected at shape validation. The plugin executes those commands itself at completion time, so a declared `exitCode` is not proof and the gate can take minutes (300s per command, 600s total, 20-command cap) — expect a slow completion, never retry it just because it is slow. Busy lease: on `Goal is busy with another turn. Retry shortly.` retry the same call next turn. Titles that look like path escapes (`..`, a leading `/`, drive letters) are rejected — keep titles plain prose. One goal per session at `.opencode/goals/<session-id>.json` (the legacy project-scoped file is a read fallback only), with a base lease TTL of 120s extended to cover a completion proof pass; another session's goal is never yours to read, continue, or clear. No background reads or polling of goal state files. Kanban task files remain single source of truth; goal files are scratch resume pointers only. On any conflict Kanban wins. Never write a goal state or evidence file with file tools; use goal tools only with exact schemas; on corrupt state report to the human.
 - Smart Compact operations in the Compaction section above remain unchanged.
 
+## Omitted-Output Recovery Gate (mandatory)
+
+When a tool result arrives trimmed or pointered, you MUST recover important output BEFORE acting on it. Important means the payload carries a plan, an XML task block, a verdict, verification evidence, or cited file content you are about to act on. Never act on important omitted output before recovery — guessing from a stub is a protocol violation. Three loss paths, three distinct recovery routes; keep them separate and never substitute one for another.
+
+1. Smart Compact omission notice (`omitted-NNNN`). The plugin pruned bulky tool output into a session cache. Preferred route: one cheap re-run of the source tool. When a re-run is expensive, retrieve via Code Mode `execute` call `tools.read_omitted_content({contentId: "omitted-0001"})` — exact signature, the Content ID comes from the notice itself. The return is the session-cached original, possibly stale, capped at 20,000 characters with an explicit truncation notice when capped. Staleness rule: before trusting code text from a cached retrieval, cross-check the cited lines with one `grep` against the live file; on mismatch, re-run the source tool once and prefer fresh output. A missing original (cache miss) means re-run the source tool once; on second failure, record `Omission unrecovered: <contentId>` in the task Execution Log and continue or escalate — never fabricate the tail.
+
+2. Code Mode truncated return (`truncated: true` on an `execute` result). Recover by re-invoking the exact same call scoped to the missing range — re-read the exact range through the tool again, never assume the tail.
+
+3. Brain oversized-turn stub (`[brain-output]` pointer with `output_address`). Read the artifact file at `output_address` with native `read`: use `xml_blocks` when the extracted-block count is above zero, otherwise `full_output`. Never execute a pointer line. When `output_address` is absent, nothing was stubbed — the inline text is complete; act on it.
+
+Bounded-retry rule: at most two recovery attempts per omitted payload; on exhaustion, log the exact loss line and surface it in the handoff. Never re-run a source tool for output retrievable by Content ID, and never call retrieval speculatively. The three paths above are the only approved recovery routes.
+
 ## Capability Preflight (session start)
 
 Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot halts with the relay block as the named blocker. Approval collection follows the single approval rule. For closure, accept either the exact standalone Manager answer "Approved for closure" or "Close task" (case-insensitive), or either exact phrase as the answer value in an unmodified question-tool result of the form `User has answered your questions: "<question>"="<answer>"` when that result answers the immediately preceding relayed closure-approval question. Compare only the answer value, not the quoted question/header, and do not require the approval phrase to be the entire Hands message. The existing bare "approved" exception remains limited to the Manager's direct answer to that immediately preceding closure-approval question, including the exact answer value "approved" in its question-tool result. The plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval you MUST collect the decision via the question tool whose body carries the full plan text (see the Plan presentation contract), with one answer slot; at the PO_REVIEW_PENDING relay and any closure approval gate, one narrow question and one answer slot. Prose-only approval asks are forbidden because an auto-continue loop can roll past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
@@ -608,7 +620,7 @@ needs no extra machinery.
      after it: `compact_context`, a leaner prompt, and `include_bundle=false`
      exist for that. Only the runtime's own `maxOutputBytes` may cut the
      return, and it says so with `truncated: true`; then re-read the exact
-     range through the tool again, never assume the tail. If a `brain_turn`
+     range through the tool again, never assume the tail. The full decision tree for every loss path is in the Omitted-Output Recovery Gate section. If a `brain_turn`
      result carries `truncated: true`, the remainder is also recoverable
      from its `output_address` via native `read` or shell; the artifact at
      that path holds `xml_blocks` plus the full raw output.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index b6ecfab..28309e4 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.94.1</system_version>
+<system_version>9.95.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 6538f89..51c4d50 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -17,6 +17,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **database-migration**: Forbid direct schema alterations and force standard migration tools (Alembic, Prisma, Flyway) for safe, repeatable deployments.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
+- **brain-orchestration**: Explains the Brain platform's participants, seven seats, stages, modes, approval gates, context maps, and output-recovery contracts. Load when an agent or downstream project needs to understand how the Brain/Hands line works.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
diff --git a/prompts/fragments/DECISIONS.md b/prompts/fragments/DECISIONS.md
index 40ed1bc..7d7792e 100644
--- a/prompts/fragments/DECISIONS.md
+++ b/prompts/fragments/DECISIONS.md
@@ -146,3 +146,11 @@ Rollback: Restore the Brain-owned automatic-mode overrides and remove the corres
 - **Decision:** Align the discovery summary phase to the four-surface shape, naming the `Tree:` line and its role as the source of the audit line's tree slot. Add one sentence to the worked-examples preamble stating that the examples are prompt text, so their unwrapped outer blocks are not a contradiction of the four-backtick emission rule. Hold the version at 9.93.0, because a bump is owed per shipped change rather than per rebuild inside one unreleased change.
 - **Consequences:** All four manifest surfaces state one shape, and the tree path has a named home for the audit line. The worked examples stay authoritative for the placeholder ban without modelling a forbidden emission. Four residuals (I33-I36) plus one audit-line observation (I37) remain open as documentation debt.
 - **Rollback:** Restore the prior discovery summary sentence, drop the preamble paragraph, restore version 9.92.0 and regenerate.
+
+<!-- provenance: tasks/in-progress/423-portable-release-omitted-output-brain-skill.md -->
+## [2026-11-24] ADR-017: Brain orchestration becomes a portable skill
+
+- **Context:** Brain's participants, seats, stages, modes, gates, and output-recovery paths were spread across runbooks and prompt fragments, making correct use dependent on memorizing internal files.
+- **Decision:** Register a Brain orchestration skill that distills the deployed contract. Its authority wording names the deployed runbook and stage manifest rather than HQ repository paths after the portability rule check.
+- **Consequences:** Agents and downstream projects can load one skill to plan, implement, brainstorm, test, review, and close work without inventing tools or bypassing approval gates.
+- **Rollback:** Remove the registry row and template, decrement the version marker, regenerate prompts, and re-run the registry and portability tests.
diff --git a/skill-templates/DECISIONS.md b/skill-templates/DECISIONS.md
index 8afc8f1..c1528a7 100644
--- a/skill-templates/DECISIONS.md
+++ b/skill-templates/DECISIONS.md
@@ -36,3 +36,12 @@
 - **Decision:** Add a conditional rule: repositories that generate stage-scoped prompt artifacts must regenerate the full set and pass their freshness gate before deployment. Concrete commands remain in the owning repository's docs and scripts.
 - **Consequences:** Downstream projects receive the safeguard only when their architecture has stage artifacts. The template stays portable and contains no HQ scaffolding.
 - **Rollback:** Remove the conditional item from the versioning skill and restore the prior Phase 2 numbering.
+
+<!-- provenance: tasks/in-progress/423-portable-release-omitted-output-brain-skill.md -->
+
+## [2026-11-24] ADR-006: Portable release core plus optional harness profile
+
+- **Context:** The release skill hard-coded HQ files and tools, so downstream projects inherited instructions that did not apply to their repository.
+- **Decision:** Split universal release rules into a portable core and move HQ safeguards into a clearly labeled optional Harness Profile. Add a new Brain orchestration template that names the deployed runbook and stage manifest instead of HQ repository paths.
+- **Consequences:** Downstream projects receive portable release and Brain guidance. Portability is test-enforced for both templates; harness safeguards remain available where required.
+- **Rollback:** Restore the prior skill bodies, remove the Brain template and registry row, and delete the two portability tests.
diff --git a/skill-templates/README.md b/skill-templates/README.md
index 6af7a7b..2a051ca 100644
--- a/skill-templates/README.md
+++ b/skill-templates/README.md
@@ -2,11 +2,11 @@
 
 ## Duties
 
-Project-agnostic skill template catalog: source of truth copied into `.opencode/skills/` workspaces and third-party projects. Covers stacks (Android, Spring, Next.js, FastAPI, etc.), workflows (kanban-lifecycle, testing-verification, prompt-refactor), and platform bridges (Telegram, GitHub, Blowsh).
+Project-agnostic skill template catalog: source of truth copied into `.opencode/skills/` workspaces and third-party projects. Covers stacks (Android, Spring, Next.js, FastAPI, etc.), workflows (kanban-lifecycle, testing-verification, prompt-refactor), platform bridges (Brain orchestration, Telegram, GitHub, Blowsh).
 
 ## Files
 
-- `*/SKILL.md` — One directory per skill (24 templates: `android-kotlin`, `governance`, `kanban-lifecycle`, `prompt-refactor`, `testing-verification`, `telegram-suite`, and others).
+- `*/SKILL.md` — One directory per skill (25 templates: `android-kotlin`, `brain-orchestration`, `governance`, `kanban-lifecycle`, `prompt-refactor`, `testing-verification`, `telegram-suite`, and others).
 - `governance/templates/opencode-init/references/` and `governance/templates/opencode-init/scripts/` — Init scaffolding references and helpers.
 
 ## Key Risks & Invariants
@@ -14,3 +14,4 @@ Project-agnostic skill template catalog: source of truth copied into `.opencode/
 - HQ-only scaffolding (`09-hands_protocols.md` rules, prompt fragments) must never leak into project-agnostic templates.
 - Task-number references live only in code comments, CHANGELOG, task files, and HTML comments; never in prompt prose.
 - Template edits propagate to all downstream projects; keep them project-agnostic.
+- Portable-core split is test-enforced for versioning and Brain orchestration: harness identifiers and HQ repository paths belong only in the labeled optional profile or deployed-contract wording.
diff --git a/skill-templates/brain-orchestration/SKILL.md b/skill-templates/brain-orchestration/SKILL.md
new file mode 100644
index 0000000..5e3161f
--- /dev/null
+++ b/skill-templates/brain-orchestration/SKILL.md
@@ -0,0 +1,37 @@
+---
+name: brain-orchestration
+description: How the Cognitive Lead Brain/Hands platform works - participants, seven seats, stages, modes, approval gates, context maps, and output-recovery contracts.
+---
+
+# Brain Orchestration
+
+## Authoritative Contract
+
+The deployed Brain Bridge runbook and stage manifest are the authoritative contract. This skill distills them for downstream harness projects. On any conflict, the deployed contract wins.
+
+## Participants
+
+- Manager: human supervisor and approval gatekeeper — approves plans, answers Relay questions, issues "Approved for closure" / "Close task" verbatim; owns remote pushes and service restarts.
+- Brain: the Cognitive Lead AI orchestrator persona set — produces plans and XML task blocks; no direct file, terminal, or web access.
+- Hands: the local Cognitive Executor agent — executes XML tasks, runs verification, stages via approved mechanisms under Zero-Autonomous-Commit (ZAC).
+- Discovery subagents: read-only context gathering, up to 4 concurrent.
+
+## The Seven Seats
+
+Software Architect (system design, contracts, roadmaps), UI/UX Designer (design system, a11y), Senior Programmer (implementation task authoring, orchestration), Project Planner (Kanban file state), Sprint Strategist (scope, capacity, MoSCoW), QA Engineer (adversarial verdicts: QA_PASSED / QA_REJECTED), Code Reviewer (blueprint and standards audit: APPROVED, APPROVED_WITH_CHANGES, REJECTED_NEEDS_FIXES, PO_REVIEW_PENDING). Design work uses Software Architect and UI/UX Designer; programming uses Senior Programmer; brainstorming convenes all seven as a report; verdicts and closure route through QA Engineer, Code Reviewer, and the Manager.
+
+## Stages and Routing
+
+brain_turn(stage=...) selects the persona-scoped system prompt from the deployed stage manifest, the single source of stage routing in harness projects. Admitted stages: plan, implement, qa, review, closure, sprint, planner, brainstorm. Manager-term aliases: "code review" maps to review, "planning" maps to plan. Unknown stages fail loud at preflight.
+
+## Working Method
+
+The 9-step production line: discovery, optional brainstorm (required only when cross-disciplinary AND hard to reverse), blueprint, Manager plan approval, implementation, adversarial QA, code review, PO closure approval, next-task transition. Every planning or verdict turn carries a verified Context-Map (tree report plus context_paths manifest); the Brain plans only from grounded context and returns missing_context otherwise. Seat Check names the requested and skipped seats before every planning turn.
+
+## Modes and Approvals
+
+Manual mode: supervised approvals, the Manager gates each handoff. Autopilot: one plan-approval pause, then chained turns; only Relay questions and hard blockers interrupt. Approval phrases match as English literals only; blanket acknowledgements never count. Approval and closure questions ride the question tool; a required tool reported unavailable pauses with the relay block.
+
+## Output Contracts
+
+Structured blocks (hands_implementation_task, hands_discovery_task, hands_combined_task, failure_report, hotfix) extract from bare XML first and from fenced XML in manual copy-paste mode; a body carrying its own fenced code wraps in four backticks. Oversized brain_turn results arrive as a pointer: the output begins with the [brain-output] marker and names the artifact at output_address; read the artifact and execute xml_blocks when the block count is above zero, otherwise full_output. Pruned or truncated tool output follows the executor's mandatory omitted-content recovery gate: a cache omission is one read_omitted_content call by Content ID or one cheap source re-run; a truncated code-mode return is re-read at the exact range; recovery is bounded to two attempts per payload.
diff --git a/skill-templates/versioning-and-release/SKILL.md b/skill-templates/versioning-and-release/SKILL.md
index 99e89a6..2c9545a 100644
--- a/skill-templates/versioning-and-release/SKILL.md
+++ b/skill-templates/versioning-and-release/SKILL.md
@@ -9,76 +9,67 @@ description: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats
 
 Enforces a strict, uniform workflow for versioning, tracking modifications, writing git history, and pushing code across all workspace projects. Every agent modifying any repository MUST strictly adhere to this protocol to prevent chaotic git history and untracked changes.
 
+## Portability Contract
+
+This skill is project-agnostic by contract. The sections below form the portable core and apply to every repository. Harness projects (workspaces shipping the Cognitive Lead platform agent files and Kanban task lanes) additionally apply the clearly labeled Harness Profile section at the end; nothing in the core depends on a specific platform's tools or file layout.
+
 ## Core Conventions
 
 ### 1. Semantic Versioning (SemVer)
 
 Format: `MAJOR.MINOR.PATCH` (e.g., `5.3.0`)
 
-- **PATCH (`0.0.1` increment):** Used for bug fixes, documentation syncs, formatting, raw text cleanups, or minor tool polishing.
-- **MINOR (`0.1.0` increment):** Used for new agent skills, new stack templates, adding major sub-components, or non-breaking architectural upgrades.
-- **MAJOR (`1.0.0` increment):** Used for complete system prompt rewrites, breaking API contract changes, or protocol schema modifications.
+- **PATCH (`0.0.1` increment):** bug fixes, documentation syncs, formatting, raw text cleanups, minor tool polishing.
+- **MINOR (`0.1.0` increment):** new agent skills, new stack templates, new sub-components, non-breaking architectural upgrades.
+- **MAJOR (`1.0.0` increment):** complete prompt/instruction rewrites, breaking contract changes, schema modifications.
 
 ### 2. Changelog Management (Keep a Changelog)
 
-Every project MUST maintain a `CHANGELOG.md` file at the root. Modifications must be logged under the appropriate version header using these exact categories:
-
-- `Added` — for new features, skills, or blueprints.
-- `Changed` — for changes in existing functionality.
-- `Deprecated` — for soon-to-be-removed features.
-- `Removed` — for now-removed features.
-- `Fixed` — for any bug fixes.
-- `Security` — in case of vulnerabilities or security updates.
+Every project MUST maintain a `CHANGELOG.md` at the root, newest release first below any `[Unreleased]` section, using exact categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
 
 ### Parse-Then-Append Protocol
 
-Before inserting any entry into CHANGELOG.md:
-
-1. Read the entire file.
-2. Search for the target version header (e.g., `## [7.1.0]`).
-3. If the version header exists, search for the target category (e.g., `### Changed`) under it.
-4. If the category exists, append the new entry as a bullet under it.
-5. If the category does NOT exist, create it under the version header in the canonical order: Added, Changed, Deprecated, Removed, Fixed, Security.
-6. If the version header does NOT exist, create it at the top (below `## [Unreleased]` if present) with the required category.
-7. NEVER create a duplicate category header under the same version.
+Before inserting any entry: read the whole file; find the target version header; find the target category under it; append if both exist; create the category in canonical order if only the header exists; create the header directly below `[Unreleased]` if the header is absent; NEVER duplicate a category header under one version.
 
 ### 3. Conventional Commits
 
-All git commit messages MUST use lowercase prefixes followed by a colon and a space, describing the change concisely (maximum 72 characters):
-
-- `feat: [description]` — for new features, skills, or blueprints.
-- `fix: [description]` — for bug fixes, syntax corrections, or logical repairs.
-- `docs: [description]` — for markdown, documentation, or README edits.
-- `refactor: [description]` — for restructuring code without changing behavior.
-- `chore: [description]` — for configurations, package updates, or tooling configs (e.g., `opencode.json`).
+All commit messages use lowercase prefixes plus colon and space, first line maximum 72 characters: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.
 
 ## Detailed Workflow
 
 ### Phase 1: Pre-Commit Quality Checks
 
-1. Before completing any task, ensure the local test suite and type-checkers have passed successfully (maximum of 3 consecutive repair attempts per strict guardrails).
-2. Ensure `AGENTS.md` and `DESIGN.md` conventions are fully respected.
-3. **Pre-Commit Verification Gate (Environment Verification, DevOps/Infra tasks only):** If the task involves deployment, Docker, CI/CD, or infrastructure changes, run ALL environment-specific verification commands (e.g., `docker login`, token scope validation, registry access checks) BEFORE proceeding to staging. If ANY check fails, HALT and output a failure report. Do NOT stage partial work.
+1. The local test suite and type-checkers pass before any completion claim (maximum 3 consecutive repair attempts; after that, halt with a failure report).
+2. The project's documented conventions are respected wherever they live (agent instruction files, design guides, contribution rules).
+3. DevOps/Infra tasks: run ALL environment-specific verification commands (registry authentication, token scope, network access) BEFORE staging. On any failure, HALT with a failure report; never stage partial work.
 
 ### Phase 2: Metadata Synchronization
 
-1. If `system-prompt.md` was edited, verify that `<system_version>` at the top is bumped according to SemVer rules.
-2. Open `CHANGELOG.md` and insert a formal release entry under the new version header, categorizing your modifications correctly.
-3. Open the active task file in `tasks/` and ensure your final reasoning and files modified are accurately logged under the "Execution Log & Reasoning" section.
-4. If a release includes changes to system behavior, skills, MCP servers, task templates, or workflow rules, `system-prompt.md` version MUST be bumped.
-5. If the repository generates stage-scoped prompt artifacts, every release that changes prompt sources must regenerate the full prompt and every declared stage artifact, then pass the repository freshness gate before deployment. A release with a stale stage artifact is incomplete.
-6. If a release is metadata-only (e.g., LICENSE addition), the CHANGELOG MUST explicitly state: "system-prompt.md version unchanged."
-7. The `[Unreleased]` section MUST be empty after a release. All entries MUST be moved under the new version header.
+1. If a version identifier is embedded in project documentation, prompts, or configuration and your change affects what it covers, bump it per SemVer.
+2. Insert a formal `CHANGELOG.md` entry under the new version header via Parse-Then-Append, categorizing every modification correctly.
+3. Log final reasoning and files modified in the project's active tracking artifact (task file, board card, or equivalent).
+4. Metadata-only releases: the changelog entry MUST state the version marker is unchanged.
+5. The `[Unreleased]` section MUST be empty after a release; all entries move under the new version header.
+
+### Phase 3: Staging & Factual Diff
+
+1. Stage exactly the files this task modified, through the project's approved staging mechanism, and make the factual diff available to the reviewer.
+2. Never run raw `git add`, `git commit`, `git checkout`, or `git push`. Parallel sessions: if the shared working tree carries another session's changes to a file, stage only this task's hunks; never commit foreign content.
 
-### Phase 3: Staging & Factual Diff Injection
+### Phase 4: Commit & Push Boundaries
 
-1. Call the `custom_context_stage_and_inject_diff` MCP tool, providing the exact path to your active task file.
-2. This stages your modified codebase files and automatically injects the factual diff into your task file, ensuring the Code Reviewer has a grounded reference.
-3. Parallel sessions sharing files: if the staged diff carries another task's hunks, call `custom_context_unstage_files` with exactly those files (index-only, worktree untouched), redo your hunk-level staging, then re-run staging with `skip_add=True`. Never commit or checkout — both stay forbidden.
+1. Commit only through the project's approved commit mechanism, with a Conventional Commits message that the mechanism validates.
+2. Pushing to a remote is owner-gated: the repository owner performs it after task closure, never an autonomous agent.
 
-### Phase 4: Closure Commit via MCP (ZAC-Compliant)
+## Harness Profile (optional — Cognitive Lead harness projects only)
 
-1. NEVER run raw `git commit` or `git push` — autonomous agents are forbidden from both (Zero-Autonomous-Commit). Call the `custom_context_commit_and_clean_task` MCP tool with your active task file path and a Conventional Commit message.
-   _Example message:_ `docs: finalize versioning skill template`
-2. The tool validates the message (type in `feat|fix|docs|refactor|chore`, first line ≤72 chars) and rejects free-form text — fix the message and retry, never bypass.
-3. Pushing to the remote repository is Manager-owned. The Manager runs `git push origin main` (or the active branch) manually after task closure.
+Apply this section only in workspaces that ship the platform agent files and Kanban lanes.
+
+1. Read `AGENTS.md` as the entry point and respect `DESIGN.md` conventions in full.
+2. The active task file lives in `tasks/`; record final reasoning under its "Execution Log & Reasoning" section.
+3. If `system-prompt.md` was edited, verify `<system_version>` at the top is bumped per SemVer.
+4. If a release changes system behavior, skills, MCP servers, task templates, or workflow rules, the `system-prompt.md` version MUST be bumped.
+5. If the repository generates stage-scoped prompt artifacts, every release that changes prompt sources must regenerate the full prompt and every declared stage artifact, then pass the repository freshness gate before deployment. A release with a stale stage artifact is incomplete.
+6. Stage via the `custom_context_stage_and_inject_diff` MCP tool with the active task file path; it stages the code and injects the factual diff. Parallel sessions: if the staged diff carries another task's hunks, call `custom_context_unstage_files` with exactly those files (index-only, worktree untouched), redo hunk-level staging, then re-run staging with `skip_add=True`. Never commit or checkout — both stay forbidden.
+7. Closure commits go ONLY through the `custom_context_commit_and_clean_task` MCP tool (ZAC-compliant), with a message whose type is in `feat|fix|docs|refactor|chore` and first line at most 72 characters; the tool rejects free-form text — fix the message, never bypass.
+8. Service restarts after a prompt deploy are owner-gated: the Manager performs them; an agent never restarts the running services.
diff --git a/system-prompt.md b/system-prompt.md
index 5818090..41097d8 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.94.1</system_version>
+<system_version>9.95.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -132,6 +132,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **database-migration**: Forbid direct schema alterations and force standard migration tools (Alembic, Prisma, Flyway) for safe, repeatable deployments.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
+- **brain-orchestration**: Explains the Brain platform's participants, seven seats, stages, modes, approval gates, context maps, and output-recovery contracts. Load when an agent or downstream project needs to understand how the Brain/Hands line works.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
diff --git a/tests/README.md b/tests/README.md
index 5cbce55..e10dd2b 100644
--- a/tests/README.md
+++ b/tests/README.md
@@ -11,6 +11,9 @@ Offline-only verification suite for the HQ platform: Brain Bridge turns, capabil
 - `test_brain_diff_attach.py` — Diff attachment on QA/reviewer turns.
 - `test_bundle_tasks.py` — META bundling, verbatim preservation, auto-archive moves.
 - `test_prompt_sync.py` — Assembled prompt equals committed `system-prompt.md` (rtk mandate included).
+- `test_versioning_skill_portability.py` — Rejects harness literals in the portable release core and preserves the optional profile.
+- `test_executor_recovery_gate.py` — Pins mandatory recovery for omitted, truncated, and Brain-pointered output.
+- `test_brain_orchestration_skill.py` — Pins Brain participants, seats, stages, gates, and portable authority wording.
 - `test_stage_prompts.py` — Stage routing, runtime freshness fallback, assembler freshness gate, and release ordering.
 - `test_session_lifecycle.py` / `test_loop_guard.py` — Session ledger lifecycle and spin-guard hashing.
 - `test_mcp_servers.py` / `test_skill_registry.py` / `test_input_validation_pipeline.py` — Server contracts, registry, input pipeline.
diff --git a/tests/test_brain_orchestration_skill.py b/tests/test_brain_orchestration_skill.py
new file mode 100644
index 0000000..8d0d9a4
--- /dev/null
+++ b/tests/test_brain_orchestration_skill.py
@@ -0,0 +1,87 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""Contract gate for the brain-orchestration skill template (Task 423).
+
+The skill must describe the platform without hard-coding HQ repository
+paths: the portable-authority rule from the versioning-skill split applies
+here too (skill-templates README portability invariant).
+"""
+
+import re
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parent.parent
+SKILL = ROOT / "skill-templates" / "brain-orchestration" / "SKILL.md"
+REGISTRY = ROOT / "prompts" / "fragments" / "07-agent_skills_registry.md"
+
+
+def test_frontmatter_name_matches_dir():
+    text = SKILL.read_text(encoding="utf-8")
+    assert re.search(r"^name: brain-orchestration$", text, re.MULTILINE)
+
+
+def test_registry_lists_skill_without_plugin_literals():
+    reg = REGISTRY.read_text(encoding="utf-8")
+    line = next(
+        l for l in reg.splitlines() if l.startswith("- **brain-orchestration**")
+    )
+    for banned in (
+        "read_omitted_content",
+        "compact_context",
+        "goal_set",
+        "smart-compact",
+    ):
+        assert banned not in line, f"plugin literal in registry line: {banned}"
+
+
+def test_skill_covers_participants_seats_stages_gates():
+    text = SKILL.read_text(encoding="utf-8")
+    for token in (
+        "Manager",
+        "Brain",
+        "Hands",
+        "Software Architect",
+        "UI/UX Designer",
+        "Senior Programmer",
+        "Project Planner",
+        "Sprint Strategist",
+        "QA Engineer",
+        "Code Reviewer",
+        "brain_turn",
+        "plan",
+        "implement",
+        "qa",
+        "review",
+        "closure",
+        "sprint",
+        "planner",
+        "brainstorm",
+        "Approved for closure",
+        "Zero-Autonomous-Commit",
+        "[brain-output]",
+        "output_address",
+        "read_omitted_content",
+        "Context-Map",
+        "Seat Check",
+    ):
+        assert token in text, f"platform contract element missing from skill: {token}"
+
+
+def test_skill_uses_portable_authority_wording():
+    text = SKILL.read_text(encoding="utf-8")
+    for token in (
+        "deployed Brain Bridge runbook",
+        "stage manifest",
+        "authoritative contract",
+        "On any conflict, the deployed contract wins",
+    ):
+        assert token in text, f"portable-authority wording missing: {token}"
+
+
+def test_skill_hard_codes_no_hq_repository_paths():
+    text = SKILL.read_text(encoding="utf-8")
+    for banned in (
+        "docs/brain-bridge.md",
+        "mcp-brain-bridge/README.md",
+        "prompts/stage-manifest.json",
+    ):
+        assert banned not in text, f"HQ repository path leaked into template: {banned}"
diff --git a/tests/test_executor_recovery_gate.py b/tests/test_executor_recovery_gate.py
new file mode 100644
index 0000000..7472a28
--- /dev/null
+++ b/tests/test_executor_recovery_gate.py
@@ -0,0 +1,47 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""Mandatory omitted-output recovery gate in the executor (Task 423)."""
+
+from pathlib import Path
+
+EXECUTOR = Path(__file__).resolve().parent.parent / "agents" / "cognitive-executor.md"
+
+REQUIRED = [
+    "## Omitted-Output Recovery Gate (mandatory)",
+    "Never act on important omitted output before recovery",
+    'tools.read_omitted_content({contentId: "omitted-0001"})',
+    "capped at 20,000 characters",
+    "possibly stale",
+    "re-run the source tool once",
+    "Smart Compact omission notice (`omitted-NNNN`)",
+    "Code Mode truncated return (`truncated: true`",
+    "Brain oversized-turn stub (`[brain-output]` pointer with `output_address`)",
+    "Bounded-retry rule: at most two recovery attempts",
+    "never assume the tail",
+]
+
+
+def test_recovery_gate_text():
+    text = EXECUTOR.read_text(encoding="utf-8")
+    for token in REQUIRED:
+        assert token in text, f"recovery contract text missing: {token}"
+
+
+def test_gate_is_cross_referenced_from_compaction_and_codemode():
+    text = EXECUTOR.read_text(encoding="utf-8")
+    assert text.count("Omitted-Output Recovery Gate") >= 3, (
+        "gate must be named once plus referenced from the compaction and code-mode sections"
+    )
+
+
+def test_three_paths_stay_distinct():
+    text = EXECUTOR.read_text(encoding="utf-8")
+    gate_start = text.index("## Omitted-Output Recovery Gate")
+    gate = text[
+        gate_start : text.index("## Capability Preflight (session start)", gate_start)
+    ]
+    for ordered in (
+        "1. Smart Compact omission notice",
+        "2. Code Mode truncated return",
+        "3. Brain oversized-turn stub",
+    ):
+        assert ordered in gate, f"numbered route missing: {ordered}"
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 9372587..fa3c182 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -48,7 +48,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.94.1"
+    assert shipped == "9.95.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -373,9 +373,9 @@ def test_executor_contains_full_dto_mandate():
     )
 
 
-def test_shipped_prompt_version_is_9_94_1():
+def test_shipped_prompt_version_is_9_95_0():
     prompt = _read_shipped_prompt_for_approval_contract()
-    assert "9.94.1" in prompt
+    assert "9.95.0" in prompt
 
 
 def test_openui_validity_gate_in_executor_and_fragment():
diff --git a/tests/test_versioning_skill_portability.py b/tests/test_versioning_skill_portability.py
new file mode 100644
index 0000000..624eabe
--- /dev/null
+++ b/tests/test_versioning_skill_portability.py
@@ -0,0 +1,82 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""Portable-core regression gate for the versioning skill (Task 423, code comment provenance only).
+
+The skill template must stay project-agnostic: harness-specific names live
+only in the clearly labeled Harness Profile section at the file end.
+"""
+
+import re
+from pathlib import Path
+
+SKILL = (
+    Path(__file__).resolve().parent.parent
+    / "skill-templates"
+    / "versioning-and-release"
+    / "SKILL.md"
+)
+FORBIDDEN_IN_CORE = [
+    "AGENTS.md",
+    "DESIGN.md",
+    "tasks/",
+    "system-prompt.md",
+    "custom_context_",
+]
+
+
+def _split(text: str):
+    m = re.search(r"^## Harness Profile", text, re.MULTILINE)
+    assert m, "missing clearly labeled Harness Profile section"
+    return text[: m.start()], text[m.start() :]
+
+
+def _skill_text():
+    return SKILL.read_text(encoding="utf-8")
+
+
+def test_portable_core_has_no_harness_literals():
+    core, _ = _split(_skill_text())
+    offenders = [token for token in FORBIDDEN_IN_CORE if token in core]
+    assert offenders == [], f"harness literals leaked into portable core: {offenders}"
+
+
+def test_harness_profile_preserves_all_safeguards():
+    _, profile = _split(_skill_text())
+    for required in (
+        "AGENTS.md",
+        "DESIGN.md",
+        "system-prompt.md",
+        "tasks/",
+        "custom_context_stage_and_inject_diff",
+        "custom_context_unstage_files",
+        "custom_context_commit_and_clean_task",
+        "skip_add=True",
+        "owner-gated",
+    ):
+        assert required in profile, (
+            f"release safeguard missing from Harness Profile: {required}"
+        )
+
+
+def test_core_keeps_universal_release_rules():
+    core, _ = _split(_skill_text())
+    for required in (
+        "MAJOR.MINOR.PATCH",
+        "Parse-Then-Append",
+        "Conventional Commits",
+        "feat:",
+        "fix:",
+        "docs:",
+        "refactor:",
+        "chore:",
+        "72 characters",
+        "[Unreleased]",
+    ):
+        assert required in core, f"portable rule missing from core: {required}"
+
+
+def test_core_commit_and_push_are_mechanism_gated():
+    core, _ = _split(_skill_text())
+    assert (
+        "Never run raw `git add`, `git commit`, `git checkout`, or `git push`" in core
+    )
+    assert "Pushing to a remote is owner-gated" in core
```
<!-- END_GIT_DIFF -->
