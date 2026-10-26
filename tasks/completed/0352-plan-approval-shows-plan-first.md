# Task 0352: Plan approval must show the plan before asking

**File:** `tasks/qa/0352-plan-approval-shows-plan-first.md`
**Source:** manager
**Type:** bug
**Status:** in-progress
**Submitted:** 2026-10-26T19:34:50Z
**Estimate:** 1h
**Deadline:** 2026-10-26
**Started:** 2026-10-26T19:28:32Z

## Goal

Make every plan-approval gate present the approved plan to the Manager before the approval question appears. Today the Hands calls the `question` tool with a bare approval ask while the plan stays inside the Brain's `output`, which the Manager never sees.

## Manager's Notes

> system has a bug, it ask me for approve plan , but never show me the plan first, find it and fix automaticlly within a task and brain mode auto lock

Autopilot is LOCKED for this task: find the cause and fix it without a separate plan pause or implementation pause. ZAC holds; closure still needs the exact approval word.

## Root cause (verified in the prompt corpus)

- `agents/cognitive-executor.md` "Autopilot mode" states "In autopilot the Manager sees only Relay questions and the final verdict report", which reads as an instruction to suppress the plan body.
- The "Supervised autopilot plan approval" section says "show the Brain-approved plan to the admin" but never says where or in what order, and never says the `question` payload must carry the plan.
- "Capability Preflight" says the plan gate collects the decision "via the question tool with one narrow question and one answer slot", which pushes toward a short, plan-free question.
- The Brain Bridge state machine treats a plan `REPORT` as "triage like a review verdict"; no step says the plan text reaches the Manager.
- Net effect: the Hands emits an approval card whose body is only "Approve the plan?" and the plan lives and dies in the tool result.

## Local TODOs

- [x] Add a Plan presentation contract to the executor (chat-first, full plan, question payload carries it, bare ask forbidden)
- [x] Fix the autopilot "sees only Relay questions" sentence
- [x] Bind the plan gate wording in Capability Preflight to the plan body
- [x] Add a regression test on the executor contract in `tests/test_prompt_sync.py`
- [x] Sync the live global agent copy at `~/.config/opencode/agents/cognitive-executor.md`
- [x] Living docs: `agents/DECISIONS.md` ADR + `agents/README.md` invariant
- [x] CHANGELOG entry
- [x] Run the suite and `lint_task_file`

## Acceptance Criteria

- [x] `agents/cognitive-executor.md` carries an explicit Plan presentation contract: the plan body is written into the chat in the same turn, in full, before the `question` tool call; the question payload repeats the plan; a bare "Approve the plan?" ask is a protocol violation.
- [x] The autopilot sentence no longer claims the Manager sees only Relay questions; it names the plan as visible.
- [x] The Capability Preflight plan-gate sentence requires the full plan in the question payload instead of a bare narrow question.
- [x] A regression test in `tests/test_prompt_sync.py` asserts the contract text exists and the old suppressing sentence is absent.
- [x] The live agent copy at `~/.config/opencode/agents/cognitive-executor.md` matches the repo file byte for byte.
- [x] `agents/DECISIONS.md`, `agents/README.md`, and `CHANGELOG.md` record the change.
- [x] Full suite green and `lint_task_file` green.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** full HQ suite green including the new prompt-contract test
- **Actual result:** `735 passed, 24 warnings in 59.33s`; new `test_executor_shows_plan_before_asking_for_approval` verified red first (`AssertionError: assert 'Plan presentation contract' in ...`) then green; `diff` of the live agent copy against the repo file exits 0. QA round 1 returned `QA_PASSED` with two hardening notes, both applied and re-verified (`735 passed in 61.17s`, exit 0): the prompt gate now also asserts the question-payload sentence, the preflight binding, the REPORT-surfacing rule and the positive autopilot sentence, so a partial deletion cannot pass; the planner week test now derives the expected week from `date.today().isocalendar()` instead of the implementation helper.
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** the plan body duplicated in chat and in the question card looks redundant; accepted, because a client may render only one of the two surfaces.
- **Risk:** a very long plan makes the question card unwieldy; mitigated by requiring the chat message as the primary surface and the question body as the same text.
- **Rollback:** revert the executor paragraphs and the regression test; the previous (buggy) behaviour returns.

---

## Execution Log & Reasoning

**Mode.** Autopilot LOCKED per the Manager's order ("fix automaticlly within a task and brain mode auto lock"). Standing order `manager/full_automatic_mode` (2026-09-17) plus this order authorize plan-then-implement without a separate pause. Because the bug being fixed is an approval card with no plan, this task also applies the new contract to itself: the Brain plan was reproduced in the chat before any approval step.

**Seat Check.** Domains: agent prompt contract (approval-gate ordering) plus the user-facing approval surface. Seats requested: Software Architect (whole-word trigger `contract` in the task body), UI/UX Designer (UX-intent fallback: the broken surface is the approval card; no layout keyword fired). Skipped: Senior Programmer (no runtime code change), QA/Reviewer (later stages), Planner/Strategist (no scheduling decision). Brainstorm: not required — single-file prompt-contract fix, reversible, no cross-disciplinary irreversibility.

**Brain plan verdict.** `REPORT` on the first planning turn, model `muse-spark-1.3-contributor`. Selected path: plan presentation contract in the executor, fix the suppressing autopilot sentence, bind the preflight plan gate, regression test, live sync, living docs. The Brain explicitly rejected a code-level guard in `mcp-brain-bridge` as overkill and confirmed the bridge already returns the full plan in `output`.

**Root cause (F1-F3).** F1: `agents/cognitive-executor.md:471-486` told the Hands that in autopilot "the Manager sees only Relay questions and the final verdict report" — read as a ban on showing the plan. F2: `:125` asked for "one narrow question and one answer slot" at the plan gate, with no payload requirement. F3: `:308-322` said "show the plan" with no order or surface, and `:415-419` triaged a plan `REPORT` as a verdict to file. The plan itself was never missing: `mcp-brain-bridge/server.py:4055` returns it verbatim in `output`; it was dropped at presentation time. The `question` card is rendered independently of the assistant message, so a card-only ask leaves the Manager nothing to approve.

**Fix.** Added a four-rule Plan presentation contract under Supervised autopilot plan approval (chat first in full, question repeats the plan, bare ask is a protocol bug, revision rounds print the revised plan). Reworded the autopilot sentence to name the plan as visible. Bound the Capability Preflight plan gate to the contract. Marked a plan `REPORT` as a plan to surface. Fixed nothing in the bridge on purpose: the fault was policy, not transport.

**Verification shape.** TDD: the new prompt-sync test was written first and failed on the missing contract string, which proves it guards the behaviour rather than the wording of a pre-existing paragraph. After the edit the full suite passed. The live agent copy was edited with native tools (four mirrored edits) and `diff` against the repo exits 0, so the running system carries the fix, not just the checkout.

**Adjacent defect found by the green run.** `tests/test_planner_server.py::test_plan_api_admin_only_and_persists` hardcoded the plan week as `2026-W43` while `GET /api/plan?window=week` resolves the current ISO week. It passed until the W43 to W44 rollover on 2026-10-26 and then failed with `'NoneType' object is not subscriptable`. Retargeted to `planner._plan_week_key()` so the test tracks the clock instead of a calendar guess; unrelated to this task's code path, recorded here and in the CHANGELOG because the suite could not be green otherwise.

**Assumption A1.** `Estimate: 1h` and a same-day deadline were chosen by the Hands, since the Brain plan carried no estimate and the Manager gave no size; `schedule_tasks` owns those header lines rather than a hand edit.

**QA cycle 1 (Brain).** `QA_PASSED` with four vulnerability checks (both-mode binding, transport not at fault, live sync, legitimacy of the skipped pause) and two hardening notes: the prompt gate was too narrow to catch a partial deletion, and the week repair proved itself from the implementation helper. Both were fixed before the next round, which is why the gate now asserts eight strings including the revision rule, and the week now comes from `date.today().isocalendar()`.

**QA cycle 2 (Brain).** `QA_PASSED` again, with two cosmetic notes: the revision-round rule was still unasserted and the CHANGELOG still named the helper as the week source. Both closed (ninth assertion, CHANGELOG sentence corrected) and the full suite re-ran green.

**Code Reviewer (Brain).** Technically approved, `PO_REVIEW_PENDING`, severity Low. One note only: the `__import__("datetime")` inline import in the planner test differs from the file's top-level import style; the reviewer recommended leaving it for this task and moving it on the next edit of that file. No blocking defect. The reviewer confirmed no fragment edit and no `<system_version>` bump were due, because the Brain side already required present-then-ask and only the Hands side dropped the plan.

**Final gate state:** QA_PASSED and PO_REVIEW_PENDING recorded. Closure waits for the Manager's exact word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f07067b..57d46d7 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,6 +14,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Plan approval now shows the plan before it asks (Task 0352):** approval cards arrived with nothing to approve because the plan lived only in the Brain's `output`. The executor's autopilot sentence said the Manager "sees only Relay questions and the final verdict report", the preflight asked for "one narrow question", and nothing required the plan body to reach the chat or the `question` payload. `agents/cognitive-executor.md` now carries a Plan presentation contract — the full plan text is written into the assistant message before the `question` call, the question body repeats the same text plus one decision line, a bare "Approve the plan?" ask is a protocol bug, and revision rounds print the revised plan in full. The autopilot sentence names the plan as visible, the plan gate in Capability Preflight points at the contract, and a plan arriving as `REPORT` is marked as a plan to surface rather than a verdict to file. A regression test in `tests/test_prompt_sync.py` fails if the contract disappears or the suppressing sentence returns. The live agent copy at `~/.config/opencode/agents/cognitive-executor.md` is byte-identical to the repo file. No bridge code change: `brain_turn` already returns the plan in `output`. Adjacent repair found by the full run: `test_plan_api_admin_only_and_persists` hardcoded `2026-W43` while `GET /api/plan?window=week` reads the current ISO week, so it started failing on the W43→W44 rollover; it now derives the week from `date.today().isocalendar()` instead of a calendar guess.
+
 - **Bundle META now passes the canonical lint on first write, and keeps source provenance (Task 0349):** bundling two telegram-sourced tasks produced a META that failed `lint_task_file` immediately and silently dropped `## Original Message (Persian)`, `## English Translation`, `## Refactored Prompt` and `## Relevant Code Context` from the working file. Three mismatches between writer and validator were found through the graph over `mcp-context-server` (`_build_meta_content` as the single writer, ADR-010 as prior hardening): `bundle.py` emitted only the `**Supersedes:**` metadata line where the linter's `_check_bundle_meta_structure` requires a non-empty `## Supersedes` section; the per-source extraction copied only Goal/AC/TODOs/Risk/Manager's Notes/Blueprint, so provenance sections existed only in the archive; and the dry-run "required sections" gate in `server.py` omitted `## Supersedes` and `## Bundled Checklist`, certifying a file the real lint rejects. `_build_meta_content` now writes a `## Supersedes` section naming every source id and title plus the all-or-nothing rule, and copies every unrecognised `## ` section of a source verbatim into that source's block through the new `_extract_preserved_sections`, guarded by an explicit `_STRUCTURAL_SECTIONS` deny-list so Goal/AC/TODOs/Risk/Definition of Done/Execution Log/Git Diff never repeat; per-source `Verification Evidence` is preserved because bundled tasks carry different test commands. The dry-run list gains both linter sections. ADR-011 records the boundary. Verified: 22/22 bundle tests pass (4 new: Supersedes section, provenance preservation, dry-run list parity, and a parity gate that imports the live `mcp-lint-server` function and asserts a generated META passes it), 87/87 MCP server contract tests pass.
 
 ## [9.66.0] - 2026-10-25
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index 9a88724..b560dfb 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -1,5 +1,14 @@
 # Architectural Decisions: agents
 
+## Plan approval shows the plan, not just the question
+
+Date: 2026-10-26
+Status: accepted
+Context: The Manager received approval cards with nothing to approve. The executor told the Hands that in autopilot the Manager "sees only Relay questions and the final verdict report", the preflight asked for "one narrow question", and no paragraph required the plan body — which the Brain already returns in `output` — to reach either the chat or the question payload. The plan was available and got dropped at presentation time.
+Decision: Add a Plan presentation contract to the executor: the full plan text goes into the assistant message before the `question` call, the question body repeats it, a bare ask is a protocol bug, and a revision round prints the revised plan in full before asking again. Fix the autopilot sentence so it names the plan as visible, and treat a plan that arrives as `REPORT` as a plan to surface rather than a verdict to file. Bind the preflight plan-gate sentence to the same contract. A regression test in `tests/test_prompt_sync.py` fails if the contract disappears or the suppressing sentence returns.
+Consequences: A plan-approval card can no longer arrive without the plan. The plan text is duplicated on purpose — chat plus card — because a client may render only one of the two surfaces. No bridge code change: the bridge already delivers the plan in `output`, and a code validator over UI wording would add coupling without safety.
+Rollback: Revert the executor paragraphs and the regression test; the previous behaviour returns.
+
 ## [2026-10-06] ADR-001: Initial Slice Baseline
 
 - **Context:** Baseline documentation initialized via init-folder-docs.
diff --git a/agents/README.md b/agents/README.md
index 98b377a..e8e637e 100644
--- a/agents/README.md
+++ b/agents/README.md
@@ -13,6 +13,7 @@ Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary execu
 
 - Permission drift: executor allows edit/question, discovery denies edit/bash; never invert.
 - Persona changes must stay in sync with `system-prompt.md` fragments and `prompts/` sources.
+- Plan approval surface: an approval question is only valid after the full plan body is visible in the same turn, and the question payload repeats it. A bare "Approve the plan?" ask is a protocol bug.
 - No runtime code here; changes are prompt-contract changes with system-wide effect.
 
 ### Free-tier bash gate
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index d266258..ca41bf2 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -122,7 +122,7 @@ Context is finite. Two layers keep long sessions productive, and the agent's dur
 
 ## Capability Preflight (session start)
 
-Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot halts with the relay block as the named blocker. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval, PO_REVIEW_PENDING relay, and any closure approval gate you MUST collect the decision via the question tool with one narrow question and one answer slot. Prose-only approval asks are forbidden because an auto-continue loop can roll past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
+Before approval-sensitive work (plan approval, review approval, closure), check the capability manifest: every `brain_turn` prints a `capability-manifest:` diagnostic line to stderr mapping each required tool to `AVAILABLE`, `UNAVAILABLE_REQUIRED`, or `UNAVAILABLE_OPTIONAL`. A step whose required tool is `UNAVAILABLE_REQUIRED` (for example the `question` tool) is never silently skipped. Emit the relay block the turn returned (missing tool names, stage, one narrow question, one answer slot) through the mode-appropriate channel: manual mode relays it to the Manager verbatim and pauses with the relayed question as the named blocker; autopilot halts with the relay block as the named blocker. Approval collection follows the single approval rule: closure accepts only the exact phrases "Approved for closure" or "Close task" (a bare "approved" never counts); the plan gate accepts "approved" in any case. Blanket acknowledgements ("ok", "yes", "looks good", emoji) never count as approval at any gate. At plan-approval you MUST collect the decision via the question tool whose body carries the full plan text (see the Plan presentation contract), with one answer slot; at the PO_REVIEW_PENDING relay and any closure approval gate, one narrow question and one answer slot. Prose-only approval asks are forbidden because an auto-continue loop can roll past prose. This holds in manual and autopilot. If question is UNAVAILABLE_REQUIRED, emit the relay block and pause with it as the named blocker; never skip. Only hard blockers may use prose.
 
 ## Subagent Delegation for Context Discovery
 
@@ -321,6 +321,26 @@ planning turn itself (never a separate blocking question): if the Brain
 needs repo data, it returns a discovery task, the Hands feed results back
 under the same `task_id`, and the plan arrives grounded.
 
+#### Plan presentation contract (mandatory, both modes)
+
+The Manager can only approve what he can read, and the Brain's `output`
+is invisible to him. An approval ask is therefore valid only when it
+follows a visible plan, in the same turn:
+
+1. **Chat first, in full.** Write the plan body into the assistant message
+   before calling `question`: the plan text from the Brain's `output`
+   verbatim — steps, seat routing, cited file paths with lines, risks.
+   Never a summary, never "see the task file", never only a status line or
+   a diff.
+2. **The question repeats the plan.** The `question` body carries the same
+   plan text plus the single decision line, because a client may render the
+   question card without the message above it. One answer slot only.
+3. **A bare ask is a protocol bug.** "Approve the plan?" with no plan body
+   in the chat or in the question payload is forbidden. If the plan never
+   arrived from the Brain, re-run the planning turn instead of asking.
+4. **Revision rounds keep the contract.** On a Manager edit, print the
+   revised plan in full, then ask again (max 3 tries, then escalate).
+
 ### Seat Check, trigger map, and lightweight consult (mandatory at plan start)
 
 Seat names and duties are fixed — the Hands
@@ -416,7 +436,9 @@ its own fenced code); copy-paste relay instructions expected.` Skip this
    - `XML_EXTRACTED` — execute `xml_blocks` as the next instruction set,
      exactly like an Orchestrator XML block.
    - `REPORT` — triage like a review verdict: fix what reproduces,
-     dispute the rest with evidence in the task file.
+     dispute the rest with evidence in the task file. A plan that arrives
+     as `REPORT` is a plan, not a verdict: present it in chat under the
+     Plan presentation contract before asking for approval.
      **Code-mode output discipline (never hand-trim a control payload):** the
      `execute` runtime returns your `return` value verbatim; only the runtime's
      own `maxOutputBytes` may cut it, and it says so with a `truncated: true`
@@ -480,8 +502,9 @@ forgotten. Autopilot NEVER auto-commits (ZAC holds) and NEVER closes
 tasks (closure needs the explicit approval word). Chain `brain_turn`
 calls YOURSELF: QA, re-QA, and review turns are invoked directly by you
 with the same `task_id` — never paste XML or task text for the Manager
-to ferry back. In autopilot the Manager sees only Relay questions and
-the final verdict report. Ferrying work through the Manager is a bug.
+to ferry back. In autopilot the Manager sees the full plan at the approval
+gate, Relay questions, and the final verdict report. Ferrying work through
+the Manager is a bug.
 Every chained turn carries the AUTOMATIC mode line from Build, so the
 Brain emits bare XML and never writes copy-paste relay text.
 
diff --git a/tests/test_planner_server.py b/tests/test_planner_server.py
index 8c4cba3..07fe217 100644
--- a/tests/test_planner_server.py
+++ b/tests/test_planner_server.py
@@ -1061,14 +1061,16 @@ def test_week_plan_validation_errors(tmp_path):
 def test_plan_api_admin_only_and_persists(open_client, tmp_path, monkeypatch):
     monkeypatch.setenv("PLANNER_PROJECT_ROOT", str(tmp_path))
     _write_task(tmp_path, "backlog", 53, "Saved", estimate=1)
+    week_dt = __import__("datetime").date.today().isocalendar()
+    week = f"{week_dt[0]}-W{week_dt[1]:02d}"
     resp = open_client.post(
         "/api/plan",
-        json={"week": "2026-W43", "deadline_edits": {"053": "2026-10-26"}},
+        json={"week": week, "deadline_edits": {"053": "2026-10-26"}},
     )
     assert resp.status_code == 200
     assert resp.json()["deadline_edits"]["053"] == "2026-10-26"
     status = open_client.get("/api/plan", params={"window": "week"}).json()
-    assert status["plan"]["week"] == "2026-W43"
+    assert status["plan"]["week"] == week
 
 
 def test_plan_api_viewer_cannot_save(auth_client):
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index d70194f..473030d 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -53,6 +53,25 @@ def test_executor_carries_compaction_guidance():
     assert "smart-compact" in text
 
 
+def test_executor_shows_plan_before_asking_for_approval():
+    """A plan-approval ask is invalid without the plan visible to the Manager.
+
+    Regression: the executor told the Hands that in autopilot the Manager
+    sees only Relay questions, and to collect plan approval with one narrow
+    question, so the approval card arrived with no plan body to approve.
+    """
+    text = _read(EXECUTOR)
+    assert "Plan presentation contract" in text
+    assert "before calling `question`" in text
+    assert "The `question` body carries the same" in text
+    assert "carries the full plan text" in text
+    assert "is a plan, not a verdict" in text
+    assert "sees the full plan at the approval" in text
+    assert "bare ask is a protocol bug" in text
+    assert "Revision rounds keep the contract" in text
+    assert "sees only Relay questions" not in text
+
+
 def test_shipped_prompt_is_plugin_blind():
     """The system prompt carries no plugin knowledge (separation).
```
<!-- END_GIT_DIFF -->
