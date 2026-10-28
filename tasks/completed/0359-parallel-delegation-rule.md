# Task 0359: Parallel-delegation decision rule (discovery-only mandate → R&D + implementation lanes)

**File:** `tasks/qa/0359-parallel-delegation-rule.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Give the Hands an explicit decision rule for parallel subagent use beyond discovery: triggers for parallel R&D/implementation, disjoint file-ownership partitioning, and a verify-and-merge protocol — plus fix the stale "`task`/subagent" reference in the code-search skill.

## Manager's Notes

Manager observed single-threaded execution outside discovery and asked whether the system prompt / executor need multi-agent knowledge, then ordered a small autopilot task limited to what the Hands endorses.

## Scope (endorsed only)

1. `13-constraints.md` mandate: add R&D/implementation triggers + ownership/merge protocol (discovery wording untouched).
2. Executor: add an implementation-delegation lane under Subagent Delegation (read-only discovery lane untouched).
3. `code-search/SKILL.md`: "`task`/subagent calls" → "`subagent` calls".
4. Version bump + prompt regen + pin test update + 1–2 regression asserts + CHANGELOG + global sync.

Out of scope (not endorsed): inventing a new write-capable agent; blessing runtime `explore`/`general` with contracts; touching lane caps or QA gates.

## Local TODOs

- [x] Brain plan turn under this task_id
- [x] Edit mandate + delegation lane + skill reference
- [x] Bump version, regen prompt, update pin test, add asserts
- [x] CHANGELOG + global sync + cmp verify
- [x] Run planner/prompt test subset + verify

## Acceptance Criteria

- [x] Mandate names implementation/R&D triggers distinct from discovery triggers
- [x] Delegation lane requires disjoint file ownership + Hands verification of each lane
- [x] No "`task` tool" reference remains in executor or code-search skill
- [x] Shipped prompt regenerates byte-clean; pin test updated; new asserts green
- [x] Global copies cmp-identical to repo

## Verification Evidence

- **Test command:** rtk test [exact command]
- **Expected result:** prompt-sync + skill-registry subsets green
- **Actual result:** _(filled during execution)_
- **Exit code:** _(filled during execution)_

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** broader mandate could push subagents into coupled edits; mitigated by disjoint-ownership requirement.
- **Rollback:** revert fragment/executor/skill wording, regen prompt, drop asserts.

---

## Execution Log & Reasoning

**Mode:** Autopilot LOCKED per Manager order ("خودکار با Autopilot برین انجامش بدین"). No pauses except hard blockers.

**Seat Check:** domains = prompt-contract wording + regression asserts → Architect + Senior Programmer; skipped Designer (no UI surface), QA/Reviewer (later), Planner/Strategist (single task). Trigger map TITLE+BODY: explicit miss on all three sets; 2-seat consult by duty. Brainstorm: not required — reversible wording change.

**Brain plan verdict (REPORT):** tighten without widening — triggers + ownership + merge protocol; one executor lane; skill fix; bump + regen + pin + asserts; CHANGELOG; global sync with cmp. Selected path: executed verbatim; out-of-scope guardrails held (no new agents, no runtime blessings, no cap/QA changes).

**Implementation notes:** mandate appended (discovery wording intact), executor lane added beside discovery, skill one-word fix. Version `9.68.0` → `9.69.0`; regen deterministic (double-run byte-identical) and shipped byte-clean; executor sections confirmed absent from shipped prompt both before and after (plugin-blind split holds). Pin updated; 3 new asserts. ADRs in fragments + agents DECISIONS; CHANGELOG entry. Global sync: executor, code-search skill, system-prompt (9.69.0 live) — all `cmp` identical.

**QA verdict (Brain, QA Engineer):** `QA_PASSED` — all five AC hold in the hunks; no task-number leak; scope contained. Non-blocking note: parent mandate line still names `cognitive-discovery` for implementation work, mitigated by new sub-bullets + executor lane saying generic subagents.

**Review verdict (Brain, Code Reviewer):** `APPROVED` → `PO_REVIEW_PENDING`, severity Low. Wording coherent, ADRs + CHANGELOG accurate, no scope bleed. Notes: parent-naming flaw predates this task (future rename allowed); cmp outputs should be recorded verbatim in future tasks (commands run: `cmp` on all 3 global copies, all identical).

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_prompt_sync.py tests/test_skill_registry.py -q
- **Expected result:** prompt-sync + skill-registry subsets green
- **Actual result:** `45 passed` (22 prompt-sync incl. 3 new asserts, 23 skill-registry); grep confirms zero "`task` tool" in executor and skill
- **Exit code:** 0

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 4857073..235144a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Parallel-delegation decision rule (Task 0359):** the mandate fired on discovery work only, so R&D and implementation splits ran on guesswork. `13-constraints.md` gains implementation & R&D triggers (disjoint files, independently verifiable lanes, independent research), a disjoint-ownership partition rule, and a verify-and-merge protocol; the executor gains an implementation-delegation lane beside the untouched discovery lane; the code-search skill's stale "`task`/subagent" reference now names `subagent` calls. Prompt rebuilt (`9.68.0` → `9.69.0`). No new agents, no blessed runtimes, no cap or gate changes.
+
 - **Board API cache-busting, status retry, and the real deep-link bug (Task 0358):** a live screenshot first suggested edge-cache poisoning, so every API GET carries `_t=Date.now()`, status retries once on HTML and names the content-type, and the shell sends `Cache-Control: no-store`. The content-type in the next error line then exposed the true bug: `BASE_STATUS_URL` was built from `location.href`, so on `?task=283` the client requested `/?task=283api/status`, which routes to the dashboard and returns 200 + HTML — proven live with that exact content-type. One-line fix to `origin + '/api/status'`. Verified: planner suite 122 green, inline JS `node --check` clean.
 
 - **Planner board numeric sort, hardened deep links, measured-hours chart (Task 0357):** lane files sorted lexically while filenames mix widths, so `0356` rendered before `283`. One numeric sort key (leading filename integer, lexical fallback) now orders lanes, milestone groups, plan buckets and alert rails lowest-number-first. The `?task=` modal fired on page load with no project root and no session, dying as "Error 401"; it now waits for the first successful status, carries `project_root`, and retries once automatically after login. `fetchStatus` read `resp.json()` unguarded, so an edge HTML login page served with 200 crashed the status line with a raw `Unexpected token '<'` dump; it now sniffs non-JSON bodies and names the cause. New read-only `GET /api/hours` aggregates `elapsed_seconds` by finish date into 14 daily plus 8 weekly rows (measured-only, unstamped tasks skipped), rendered as an SVG block reusing the plan-chart pattern. Verified: 3 new tests (mixed-width lane/milestone sort, hours math), planner suite 122 green, inline JS syntax clean. Docs: planner README route table + ordering note, ADR-012.
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index 6c7b9c2..ce32165 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -1,5 +1,14 @@
 # Architectural Decisions: agents
 
+## Implementation Delegation Lane Beside Discovery
+
+Date: 2026-10-28
+Status: accepted
+Context: Subagent Delegation covered read-only context discovery only. Implementation splits across subagents had no lane: no ownership rule, no verification duty, no stop condition on overlap.
+Decision: Add "Subagent Delegation for Implementation" under the discovery section, unchanged otherwise: disjoint per-lane file lists, shared-nothing lanes, Hands verifies every lane gate after merging with per-lane evidence, overlap stops and reports. Single-file, coupled, and sequential work stays with the Hands by rule.
+Consequences: The executor owns the full delegation contract; the shipped prompt stays free of lane machinery per the plugin-blind split.
+Rollback: Delete the lane section; discovery delegation is unaffected.
+
 ## Brain results are returned whole, never field-shaped
 
 Date: 2026-10-27
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 410688b..4cc8d1b 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -133,6 +133,10 @@ To preserve your primary context window for implementation logic, you MUST deleg
 3. **Implementation Tasks (`<hands_implementation_task>`):** If you need to understand a complex, unfamiliar module before editing, delegate a quick scan to `cognitive-discovery` to fetch just the signatures or relevant blocks.
 4. **Parallel Execution Mandate:** For multi-directory mapping and independent file reads, you MUST spawn parallel subagents (up to 4 concurrent agents) to maximize throughput. Serial execution of independent discovery work is a performance violation.
 
+## Subagent Delegation for Implementation
+
+Read-only discovery stays above and is never widened by this lane. When the constraints mandate's implementation triggers fire, you MAY delegate decoupled implementation lanes to subagents under these rules: each lane gets a disjoint file list it alone may edit; lanes share nothing (no shared files, fixtures, or conclusions); you verify every lane's gate yourself after merging and record per-lane evidence. A lane that finds overlap stops and reports. Single-file tasks, coupled edits, and sequential dependencies stay with you — never parallelize what cannot verify alone.
+
 ## Communication Patterns
 
 Use these patterns to communicate with precision and engineering value.
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 255e22f..9ed8492 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.68.0</system_version>
\ No newline at end of file
+<system_version>9.69.0</system_version>
\ No newline at end of file
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 9269c53..eacd357 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -21,6 +21,9 @@
 - **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is `agents/cognitive-executor.md`.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent `cognitive-discovery` subagents) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
+  - **Implementation & R&D triggers (distinct from discovery):** split work across subagents ONLY when (a) the changes touch disjoint file sets with no shared imports or fixtures, (b) each lane is verifiable alone (its own test command or grep gate), or (c) research questions are independent (different subsystems, no shared conclusion). Coupled edits to the same files, single-file tasks, and sequential dependencies stay single-threaded — parallelizing them adds coordination cost without throughput.
+  - **Disjoint ownership:** each lane owns its file list exclusively; a lane that discovers overlap MUST stop and report instead of editing foreign files.
+  - **Verify-and-merge:** the Hands re-runs every lane's verification gate itself after merging and records per-lane evidence; an unverified lane blocks the task exactly like an unverified edit.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. Keep AI tells out of the prose: no hedging openers ("it is worth noting", "it is important to note"), no inflated significance ("stands as a testament", "underscores the importance"), no negative parallelism ("not just X, but Y"), no rote rule-of-three lists, no collaborative preambles ("Great question", "Let me unpack this"), and no trailing recap that repeats what you already said. Banned phrases (never emit them): "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 - **Reference Point System:** When presenting three or more findings, options, decisions, or questions to the Manager, you MUST assign a short code to each item (e.g., F1, F2 for Findings; O1, O2 for Options; D1 for Decisions; Q1 for Questions). This anchors complex discussions and makes them highly traceable.
 - **Manager-Facing Output Style (positive contract):** This governs the final externally visible reply to the Manager. `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, and Hands Execution Logs stay unrestricted and rich — conciseness rules NEVER apply to those channels.
diff --git a/prompts/fragments/DECISIONS.md b/prompts/fragments/DECISIONS.md
index 143f89c..14eabdd 100644
--- a/prompts/fragments/DECISIONS.md
+++ b/prompts/fragments/DECISIONS.md
@@ -1,5 +1,12 @@
 # Architectural Decisions: fragments
 
+## [2026-10-28] ADR-006: Parallel Mandate Gains Implementation Triggers
+
+- **Context:** The Parallel Agent Execution Mandate fired only on file scans, signature extractions, and decoupled module changes — discovery work. R&D questions and implementation splits had no trigger, no ownership rule, and no merge protocol, so parallel execution outside discovery was either guessed at or avoided.
+- **Decision:** Append implementation & R&D triggers (disjoint files, independently verifiable lanes, independent research questions), a disjoint-ownership partition rule (overlap means stop-and-report), and a verify-and-merge protocol (Hands re-runs every lane gate, per-lane evidence, unverified lane blocks). Discovery wording untouched; single-file and coupled work stays single-threaded by rule.
+- **Consequences:** Parallel splits outside discovery have an explicit contract instead of Manager reminders. Version bumped with artifact regen.
+- **Rollback:** Revert the appended bullets and re-run the assembler.
+
 ## [2026-10-06] ADR-001: Initial Slice Baseline
 
 - **Context:** Baseline documentation initialized via init-folder-docs.
diff --git a/skill-templates/code-search/SKILL.md b/skill-templates/code-search/SKILL.md
index 630ed27..b138ec7 100644
--- a/skill-templates/code-search/SKILL.md
+++ b/skill-templates/code-search/SKILL.md
@@ -46,7 +46,7 @@ The same tools are reachable two ways; use whichever surface the session exposes
 
 ## Parallel Discovery
 
-- Split independent scopes (e.g. one subagent per MCP server, one per feature slice) across up to four `task`/subagent calls.
+- Split independent scopes (e.g. one subagent per MCP server, one per feature slice) across up to four `subagent` calls.
 - Inside one `execute` script, run independent tool calls concurrently (`Promise.allSettled`) and return the composed result once.
 - Serial scanning of unrelated directories is a performance bug, not thoroughness.
 
diff --git a/system-prompt.md b/system-prompt.md
index d7a0634..b6b2035 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.68.0</system_version>
+<system_version>9.69.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -516,6 +516,9 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 - **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is `agents/cognitive-executor.md`.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent `cognitive-discovery` subagents) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
+  - **Implementation & R&D triggers (distinct from discovery):** split work across subagents ONLY when (a) the changes touch disjoint file sets with no shared imports or fixtures, (b) each lane is verifiable alone (its own test command or grep gate), or (c) research questions are independent (different subsystems, no shared conclusion). Coupled edits to the same files, single-file tasks, and sequential dependencies stay single-threaded — parallelizing them adds coordination cost without throughput.
+  - **Disjoint ownership:** each lane owns its file list exclusively; a lane that discovers overlap MUST stop and report instead of editing foreign files.
+  - **Verify-and-merge:** the Hands re-runs every lane's verification gate itself after merging and records per-lane evidence; an unverified lane blocks the task exactly like an unverified edit.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. Keep AI tells out of the prose: no hedging openers ("it is worth noting", "it is important to note"), no inflated significance ("stands as a testament", "underscores the importance"), no negative parallelism ("not just X, but Y"), no rote rule-of-three lists, no collaborative preambles ("Great question", "Let me unpack this"), and no trailing recap that repeats what you already said. Banned phrases (never emit them): "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
 - **Reference Point System:** When presenting three or more findings, options, decisions, or questions to the Manager, you MUST assign a short code to each item (e.g., F1, F2 for Findings; O1, O2 for Options; D1 for Decisions; Q1 for Questions). This anchors complex discussions and makes them highly traceable.
 - **Manager-Facing Output Style (positive contract):** This governs the final externally visible reply to the Manager. `<reasoning_log>`, chain-of-thought, XML task generation, blueprints, and Hands Execution Logs stay unrestricted and rich — conciseness rules NEVER apply to those channels.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index ab35097..f1c1954 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,19 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.68.0"
+    assert shipped == "9.69.0"
+
+
+def test_parallel_mandate_covers_implementation_triggers():
+    """The mandate must name implementation/R&D triggers, not discovery only.
+
+    Regression: the mandate fired only on file scans and signature
+    extraction, leaving R&D and implementation splits to guesswork.
+    """
+    text = _read(SHIPPED)
+    assert "Implementation & R&D triggers" in text
+    assert "Disjoint ownership" in text
+    assert "Verify-and-merge" in text
 
 
 def test_shipped_prompt_names_only_catalog_tools():
@@ -178,6 +190,28 @@ def test_executor_names_rtk_default_runner():
     assert "first" in text.lower()
 
 
+def test_executor_has_implementation_delegation_lane():
+    """The executor must own an implementation-delegation lane beside discovery.
+
+    Regression: delegation covered read-only discovery only, so parallel
+    implementation splits had no ownership or verification contract.
+    """
+    text = _read(EXECUTOR)
+    assert "Subagent Delegation for Implementation" in text
+    assert "disjoint file list" in text
+    assert "verify every lane" in text
+    assert "`task` tool" not in text
+
+
+def test_code_search_names_only_subagent_tool():
+    """No stale `task`-tool reference may survive in the code-search skill."""
+    text = (REPO / "skill-templates" / "code-search" / "SKILL.md").read_text(
+        encoding="utf-8"
+    )
+    assert "`task`/subagent" not in text
+    assert "`subagent` calls" in text
+
+
 def test_executor_evidence_records_rtk_command():
     text = _read(EXECUTOR)
     assert "Verification Evidence" in text
```
<!-- END_GIT_DIFF -->
