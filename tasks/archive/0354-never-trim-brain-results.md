# Task 0354: Never trim a Brain result in Code Mode

**File:** `tasks/completed/0354-never-trim-brain-results.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-10-27T06:06:16Z
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

**Manager closure approval (2026-10-27):** "Approved for closure" via the question tool, answering the relayed PO_REVIEW_PENDING verdict. ZAC holds; closure runs only through `custom_context_commit_and_clean_task`.

**Closure:** preconditions verified, file moved with `git mv` to the completed lane, `**Status:** closed` and the `**File:**` header synced.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `b7b858ea89e9a1ae93c8479165a99ea2f707ed32`
<!-- END_GIT_DIFF -->
