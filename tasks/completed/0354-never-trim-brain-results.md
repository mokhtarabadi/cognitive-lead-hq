# Task 0354: Never trim a Brain result in Code Mode

**File:** `tasks/qa/0354-never-trim-brain-results.md`
**Source:** manager
**Type:** bug
**Status:** in-progress
**Submitted:** 2026-10-27T05:58:37Z
**Estimate:** 1h
**Deadline:** 2026-10-27
**Started:** 2026-10-27T05:55:52Z

## Goal

Remove the executor rule that tells the Hands to return a shaped subset of a `brain_turn` result, so every Brain plan, verdict and XML block always lands in the transcript verbatim.

## Manager's Notes

> why you cut or truntuate the code mode tool calling when calling brain? so brain plan cutoff! why?

> do it

## Root cause

`agents/cognitive-executor.md` Brain Bridge, Code-mode output discipline, says: "In code mode return `{status, block_count: xml_blocks.length, model}` and keep the block whole instead of printing a prefix." That sentence was written to stop the model printing a prefix of a huge XML block, but it licenses dropping the payload: a Hands that returns `{status, model, output}` loses `xml_blocks`, and one that returns `{status, model, blocks}` loses `output`. Either way the verbatim evidence is gone from the transcript and from the agent's own next turn, and nothing in the tool result flags the loss.

Observed in this session: the closure turn for the lint task returned `blocks` only, and several QA/review turns returned `output` only. No instruction was actually lost because the payload had already been executed, but the audit trail was silently thinner than the server response.

## Local TODOs

- [x] Fail-first prompt-sync test: the executor must require the whole payload and must not contain `block_count`
- [x] Replace the discipline paragraph with a return-it-whole rule
- [x] Sync the live agent copy and verify byte-identical
- [x] Living docs (`agents/README.md` invariant, `agents/DECISIONS.md` ADR) and CHANGELOG
- [x] Full suite + `lint_task_file`

## Acceptance Criteria

- [x] The executor states that every `brain_turn` result is returned whole — `status`, `output`, `xml_blocks`, and diagnostic/`truncated` fields — and that field-shaping or summarizing it is forbidden.
- [x] The size guidance points at pre-call tools (`compact_context`, leaner prompts) instead of post-call trimming.
- [x] The `block_count` return recipe is gone from the executor.
- [x] A prompt-sync test fails if the whole-payload rule disappears or `block_count` returns.
- [x] The live agent copy at `~/.config/opencode/agents/cognitive-executor.md` is byte-identical to the repo file.
- [x] Living docs and CHANGELOG updated; suite green; `lint_task_file` green.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** full suite green including the new executor rule test
- **Actual result:** `test_executor_never_trims_brain_results` failed red first (`AssertionError: assert 'always return the whole payload' in ...`), then `tests/test_prompt_sync.py` 18 passed and the full suite `738 passed in 48.68s`; `cmp` of the live agent copy against the repo file exits 0.
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** returning the whole payload on a very large turn could hit the `execute` output cap; the rule already requires re-reading with `truncated: true`, and the pre-call tools are named as the remedy.
- **Risk:** a Hands that reads "return everything" may echo a huge block twice (tool result plus chat); the rule ties the payload to the return value, and the plan presentation contract still governs what goes into chat.
- **Rollback:** restore the previous paragraph and drop the test.

---

## Execution Log & Reasoning

**What the rule said and why it existed.** The Code-mode output discipline carried one sentence written for a different failure: "return `{status, block_count: xml_blocks.length, model}` and keep the block whole instead of printing a prefix". It was there to stop the model printing a truncated head of a large XML block. As a return recipe it did the opposite of its purpose: `block_count` is a number, so the block itself never crossed into the transcript, and a turn that returned only `output` dropped `xml_blocks` while a turn returning only `blocks` dropped `output`.

**Evidence from this session.** The closure turn for the lint task returned `{status, model, blocks}`; several QA and review turns returned `{status, model, output}`. No instruction was lost because each payload was executed before the trim, but the transcript and the next turn held less than the server returned, which is exactly the audit hole the Manager spotted.

**Seat Check.** Domains: executor prompt contract for tool-result handling. Trigger words in TITLE+BODY: none of the mapped sets fired (`schema|contract|migration|quota|index`, the UI list, `flaky|race|deadlock|silent-fail|performance`), stated explicitly. Seats requested: Senior Programmer by implementation duty. Skipped: Software Architect (no schema or service contract), UI/UX Designer (no user-visible surface), QA/Reviewer (later stages). Brainstorm: not required — one paragraph plus one test, reversible.

**Planning gate.** The Manager's order is the plan: the bug report names the trim and "do it" authorises the fix. No separate Brain planning round was needed.

**Fix.** The paragraph is now a return-the-payload-whole rule: `status`, `output`, `xml_blocks` and any diagnostic or `truncated` field cross exactly as received; slicing, mapping, summarizing and field-shaping are named as forbidden; size is managed before the call with `compact_context`, a leaner prompt or `include_bundle=false`; the runtime's `maxOutputBytes` stays the only acceptable cut and still requires re-reading the exact range. The plan presentation contract still governs what enters chat, so "return it whole" does not mean echoing it twice to the Manager.

**Verification shape.** The prompt-sync test was written first and failed on the missing rule, then passed after the paragraph swap; it also asserts `block_count` never returns, so a future edit cannot quietly restore the recipe. The live agent copy was edited with the same native edit and `cmp` reports it byte-identical.

**Assumption A1.** `Estimate: 1h`, deadline today, chosen by the Hands because the Manager gave no size; written through `schedule_tasks`.

**QA cycle 1 (Brain).** `QA_PASSED` with one hardening note: the test guarded the rule's presence and the `block_count` recipe, but would still pass if the old permissive sentence ("summarize `output` only after the block has been consumed") were re-added. Closed before review — the test now asserts `exactly as received` is present and that permissive sentence is absent; prompt tests re-ran 18 passed.

**Code Reviewer (Brain).** Technically approved, `PO_REVIEW_PENDING`, severity Low. One note: the test did not pin the `truncated` re-read path. Closed by asserting `range through the tool again`. The reviewer also judged a bridge-side code guard overkill, since the server already returns the full payload and the loss was prompt policy.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index a269b4b..ffc2d3f 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,6 +14,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Brain results are returned whole from Code Mode (Task 0354):** the executor's Code-mode output discipline told the Hands to return `{status, block_count: xml_blocks.length, model}`, a recipe meant to stop it printing a truncated prefix of a large XML block. The recipe instead licensed dropping the payload — turns returning only `output` lost `xml_blocks`, turns returning only `blocks` lost `output` — so the transcript and the agent's next turn held less than the server returned even though the executed instructions were complete. The rule now says a `brain_turn` result is evidence, not a preview: return `status`, `output`, `xml_blocks` and any diagnostic/`truncated` field exactly as received, never slice, map, summarize or field-shape it, and manage size before the call with `compact_context`, a leaner prompt or `include_bundle=false`. The runtime's `maxOutputBytes` remains the only acceptable cut and announces itself with `truncated: true`. Locked by a prompt-sync test that fails if the rule disappears or `block_count` returns; the live agent copy is byte-identical to the repo.
+
 - **Lint path-drift guard resolves against the caller's root, not the server CWD (Task 0353):** `_check_task_file_structure` compared `Path(header).resolve()` with `Path(file_path).resolve()`, and both were anchored to the lint server process CWD. Because the server is a singleton started from its install directory, an absolute call path never matched a relative `**File:**` header, and `lint_all_tasks` — which passes absolute paths for every file — reported one false `File path mismatch` per task, so a clean batch was impossible. New `_resolve_task_reference(path_str, root)` plus a `root` parameter resolve both sides against the caller's `project_root`, threaded from `lint_task_file` and `lint_all_tasks`; calling the helper without a root keeps the old CWD behaviour for direct callers. Two fail-first tests cover the pure helper (absolute and relative actual paths against an explicit root, plus a genuine lane mismatch that must still fail) and `lint_all_tasks` returning `Found 0 total issues` on a temp project. Verified: 89/89 MCP server tests pass, full suite green, and a live module call reports `Scanned 6 task files. Found 0 total issues` against this repo. The running `mcp-lint` singleton still needs a restart to pick it up.
 
 - **Plan approval now shows the plan before it asks (Task 0352):** approval cards arrived with nothing to approve because the plan lived only in the Brain's `output`. The executor's autopilot sentence said the Manager "sees only Relay questions and the final verdict report", the preflight asked for "one narrow question", and nothing required the plan body to reach the chat or the `question` payload. `agents/cognitive-executor.md` now carries a Plan presentation contract — the full plan text is written into the assistant message before the `question` call, the question body repeats the same text plus one decision line, a bare "Approve the plan?" ask is a protocol bug, and revision rounds print the revised plan in full. The autopilot sentence names the plan as visible, the plan gate in Capability Preflight points at the contract, and a plan arriving as `REPORT` is marked as a plan to surface rather than a verdict to file. A regression test in `tests/test_prompt_sync.py` fails if the contract disappears or the suppressing sentence returns. The live agent copy at `~/.config/opencode/agents/cognitive-executor.md` is byte-identical to the repo file. No bridge code change: `brain_turn` already returns the plan in `output`. Adjacent repair found by the full run: `test_plan_api_admin_only_and_persists` hardcoded `2026-W43` while `GET /api/plan?window=week` reads the current ISO week, so it started failing on the W43→W44 rollover; it now derives the week from `date.today().isocalendar()` instead of a calendar guess.
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index b560dfb..66ebac4 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -1,5 +1,14 @@
 # Architectural Decisions: agents
 
+## Brain results are returned whole, never field-shaped
+
+Date: 2026-10-27
+Status: accepted
+Context: The Brain Bridge's Code-mode output discipline told the Hands to "return `{status, block_count: xml_blocks.length, model}` and keep the block whole instead of printing a prefix". The intent was to stop the model printing a truncated prefix of a large XML block, but the recipe licensed dropping the payload: a turn returning only `output` lost `xml_blocks`, and a turn returning only `blocks` lost `output`. The executed instructions were complete, yet the transcript and the agent's next turn held less than the server returned, so an audit could no longer see what the Brain actually said.
+Decision: Replace the paragraph with a return-the-payload-whole rule: always return `status`, `output`, `xml_blocks` and any diagnostic/`truncated` field exactly as received, never slice, map, summarize or field-shape a `brain_turn` result, and manage size before the call with `compact_context`, a leaner prompt or `include_bundle=false`. The only acceptable cut is the runtime's own `maxOutputBytes`, which announces itself with `truncated: true` and requires re-reading the exact range. A prompt-sync test fails if the rule disappears or `block_count` returns.
+Consequences: Every plan, verdict and XML block stays verbatim in the transcript, so a later turn or a reviewer can re-read it. The cost is a larger tool result per Brain turn; the pre-call tools absorb that, and the rule keeps the echo out of chat, where the plan presentation contract governs what the Manager sees.
+Rollback: Restore the previous paragraph and drop the test; the trimmed-return behaviour returns.
+
 ## Plan approval shows the plan, not just the question
 
 Date: 2026-10-26
diff --git a/agents/README.md b/agents/README.md
index e8e637e..11b464d 100644
--- a/agents/README.md
+++ b/agents/README.md
@@ -14,6 +14,7 @@ Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary execu
 - Permission drift: executor allows edit/question, discovery denies edit/bash; never invert.
 - Persona changes must stay in sync with `system-prompt.md` fragments and `prompts/` sources.
 - Plan approval surface: an approval question is only valid after the full plan body is visible in the same turn, and the question payload repeats it. A bare "Approve the plan?" ask is a protocol bug.
+- Brain results cross into the transcript whole: `status`, `output`, `xml_blocks` and diagnostic/`truncated` fields are never sliced, field-shaped or summarized on return. Size is managed before the call (`compact_context`, leaner prompt, `include_bundle=false`), never after.
 - No runtime code here; changes are prompt-contract changes with system-wide effect.
 
 ### Free-tier bash gate
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index ca41bf2..6a17cda 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -439,15 +439,18 @@ its own fenced code); copy-paste relay instructions expected.` Skip this
      dispute the rest with evidence in the task file. A plan that arrives
      as `REPORT` is a plan, not a verdict: present it in chat under the
      Plan presentation contract before asking for approval.
-     **Code-mode output discipline (never hand-trim a control payload):** the
-     `execute` runtime returns your `return` value verbatim; only the runtime's
-     own `maxOutputBytes` may cut it, and it says so with a `truncated: true`
-     flag. Never `slice`, `map`, or summarize `xml_blocks` — a cut block loses
-     instructions silently, and a head-only view is how a closure or hotfix step
-     goes missing. Read the block in full and execute from it; summarize
-     `output` only after the block has been consumed. In code mode return
-     `{status, block_count: xml_blocks.length, model}` and keep the block whole
-     instead of printing a prefix. A `truncated` flag means re-read the exact
+     **Code-mode output discipline (return the payload whole):** the
+     `execute` runtime returns your `return` value verbatim, and a
+     `brain_turn` result is evidence, not a preview. Always return the whole
+     payload — `status`, `output`, `xml_blocks`, and any diagnostic or
+     `truncated` field — exactly as received. Never `slice`, `map`,
+     summarize, or field-shape it: returning `{status, model, output}`
+     without `xml_blocks`, or the reverse, deletes the verbatim plan or
+     verdict from the transcript and from your own next turn, which is how a
+     closure or hotfix step goes missing. Manage size BEFORE the call, not
+     after it: `compact_context`, a leaner prompt, and `include_bundle=false`
+     exist for that. Only the runtime's own `maxOutputBytes` may cut the
+     return, and it says so with `truncated: true`; then re-read the exact
      range through the tool again, never assume the tail.
 3. **Relay** — any admin question inside `output` goes to the Manager
    verbatim. Feed the answer back as the next `brain_turn` user prompt.
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 473030d..06a376f 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -53,6 +53,22 @@ def test_executor_carries_compaction_guidance():
     assert "smart-compact" in text
 
 
+def test_executor_never_trims_brain_results():
+    """A brain_turn result is evidence: the Hands returns it whole, always.
+
+    Regression: the executor told the Hands to return
+    ``{status, block_count, model}``, which dropped ``output`` and
+    ``xml_blocks`` from the transcript and from the next turn.
+    """
+    text = _read(EXECUTOR)
+    assert "return the whole" in text.lower()
+    assert "payload" in text.lower()
+    assert "field-shape" in text
+    assert "exactly as received" in text
+    assert "summarize `output` only after" not in text
+    assert "block_count" not in text
+
+
 def test_executor_shows_plan_before_asking_for_approval():
     """A plan-approval ask is invalid without the plan visible to the Manager.
```
<!-- END_GIT_DIFF -->
