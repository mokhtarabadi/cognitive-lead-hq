# Task 263: Decision server sends the whole session transcript unbounded and swallows a malformed output-token cap

**File:** `tasks/completed/263-decision-server-transcript-cap-and-cap-validation.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Make the manager-decisions MCP safe under the same discipline task 262 gave the brain bridge: bound the extraction prompt that carries the whole session transcript, and fail loudly when the configured output-token cap is malformed or non-positive instead of silently falling back to a default.

## Manager's Notes

Manager order (verbatim): "a new task need and use auto pilot baseline mode so first plan them then fix automaticall, at end extraxt my desctions from old and new tsak and save them"

This task was opened after the Manager asked whether the manager-decisions MCP is safe or needs the same changes task 262 made to the brain bridge. The audit found that most of task 262 does **not** apply, but two real gaps of the same class do.

### What does NOT need changing (audit evidence)

- No conversation history of its own. The decision server reads an existing session transcript to extract decisions; it never builds, stores, or replays a chat history.
- No `store:` and no `previous_response_id`. Its calls are single-shot and stateless, so the OpenRouter stateless limitation costs nothing here.
- No attachment machinery: no task-file attach, no diff attach, no small-file bundle, no `context_paths`. Therefore no attachment caps, no numbered parts, no resume offsets, and no wrapper-overhead pricing are needed.
- Its decision store is already append-only by design (`decisions/YYYY/MM/DEC-*.json` plus `.md` and a regenerated `INDEX.md`), so the append-only transcript work does not apply.
- Its Responses API request shape is already conformant, verified during task 262: nested `reasoning: {"effort": ...}`, explicit `max_output_tokens`, `input` as `{role, content}` items, `temperature` only when explicitly configured and never together with `reasoning`, and the documented error → refusal → `max_output_tokens` triage order.

### Gap F1 — the whole session transcript is sent with no size cap (blocking)

`mcp-decision-server/server.py` builds the extraction prompt by joining every turn of the session transcript and sends it as one user message:

```python
    prompt = (
        "Extract the MANAGER's decisions, trade-offs, and rulings from this session "
        "transcript. Preserve each ruling's verbatim quote. Reply with a JSON array; "
        ...
        "Empty array when the session holds no manager rulings.\n\n" + "\n".join(turns)
    )
    transcript_bytes = path.read_bytes()
    transcript_text = "\n".join(turns)
```

There is no size cap, no truncation marker, and no budget check between the read and the request body. A long session therefore produces an unbounded prompt — the same root cause that made the brain bridge turns time out in the issue this project just closed. The transcript archived from the previous task alone was 156 KB, and a long session can be far larger. The extraction cache bounds only how many results are remembered, never how much text is sent.

### Gap F2 — a malformed or non-positive `DECISION_MAX_TOKENS` is swallowed (blocking)

```python
def _get_decision_max_tokens() -> int:
    """Output cap for extraction turns; override via ``DECISION_MAX_TOKENS``.
    ...
    """
    try:
        return int(os.environ.get("DECISION_MAX_TOKENS", "16384").strip() or "16384")
    except ValueError:
        return 16384
```

A malformed value silently becomes 16384, and zero or a negative value is returned as-is and sent to the provider. Task 262 gave the brain bridge the opposite discipline: a malformed or non-positive cap value raises and fails the call loudly. The same file already carries that discipline on one path — the inline `BRAIN_TEMPERATURE` leg of `extract_session_decisions()` raises `ValueError` for a non-numeric and for an out-of-range value — but the separate `_get_decision_temperature()` reader silently clamped a malformed or out-of-range `DECISION_TEMPERATURE` to 1.0. The pattern to copy was already present; one reader still needed it, and the planning turn caught that.

## Local TODOs

- [x] Move this task file to `tasks/in-progress/` before writing code
- [x] Read the exact prompt-build, transcript-read, cap-reader, and request-body regions of `mcp-decision-server/server.py`
- [x] Add an env-configurable transcript cap for the extraction prompt, blank-means-unset, with the current behaviour as the documented default
- [x] Truncate the prompt at that cap with an explicit note that states what was dropped, so the extraction never silently judges a partial transcript
- [x] Make `_get_decision_max_tokens()` fail loudly on a malformed or non-positive value, matching the temperature reader's discipline
- [x] Add regression tests for both behaviours
- [x] Update the documentation surface for the new env var and the loud-failure rule (`CHANGELOG.md`; `mcp-decision-server/README.md` and `mcp-decision-server/.env.example` are absent and are skipped per the Absent-File Policy)
- [x] Run the full suite via `rtk test`
- [x] Stage via `custom_context_stage_and_inject_diff` and move to `tasks/qa/`
- [x] Extract the Manager's decisions from the old and the new task sessions and save them

## Acceptance Criteria

- [x] The extraction prompt is bounded by an env-configurable cap that defaults to the current documented behaviour, and the cap honours the blank-means-unset convention used elsewhere in the repo.
- [x] When the transcript exceeds the cap, the prompt carries an explicit truncation note stating the dropped size, so the model is never asked to extract from a silently partial transcript.
- [x] A malformed or non-positive output-token cap raises a configuration error and fails the call loudly, instead of silently falling back to a default.
- [x] The temperature reader fails loudly on a malformed or out-of-range value, matching the brain-bridge caps' discipline.
- [x] The Responses API request shape stays conformant (nested `reasoning.effort`, explicit `max_output_tokens`, `input` as role/content items, temperature never combined with reasoning).
- [x] Regression tests cover the cap default, a blank value, a valid override, a malformed value, a non-positive value, and the truncation note.
- [x] The Manager's decisions from both the old task session and this task session are extracted and saved.

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass, including the new decision-server cap and truncation regressions
- **Actual result:** `665 passed, 10 warnings in 4.96s` (baseline before this task: 660 passed). 5 new tests in `tests/test_decision_server.py` cover the transcript-cap default/blank/override and its rejection of malformed, zero and negative values; the output-token cap's default/blank/override and its rejection of malformed, zero and negative values; the temperature reader's loud rejection of malformed and out-of-range values; and a turn-level proof that an oversized transcript reaches the provider capped with an explicit `[...truncated at N chars]` marker and an unchanged request shape; 1 existing temperature test was adapted to expect the loud failure.
- **Exit code:** 0

> Verification runner rule: `uv run --with pytest --with mcp==1.30.0 ... pytest tests/ -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics. The `mcp==1.30.0` exact pin is required because `rtk test` joins its arguments unquoted, so a spec containing `<` would be misparsed as input redirection.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task.

## Risk & Rollback

- **Risk:** truncating the transcript could drop the exact ruling the extraction is meant to capture, so the note must be explicit and the cap generous; a too-small default would silently degrade extraction quality.
- **Risk:** making a malformed cap raise could break an existing deployment that relied on the silent fallback; the fallback was never documented, and the loud-failure rule is already the repo's stated discipline.
- **Rollback plan:** the change is confined to `mcp-decision-server/server.py`, its tests, docs, and the changelog; revert those files with `git checkout --` and re-sync the global copy.

---

## Execution Log & Reasoning

**Autopilot lock.** The Manager ordered this task on autopilot: "a new task need and use auto pilot baseline mode so first plan them then fix automaticall, at end extraxt my desctions from old and new tsak and save them". Authority to proceed without a separate plan-approval pause: that direct order plus the standing order `manager/full_automatic_mode` (2026-09-17). The plan gate is satisfied by the Brain's own step-ordered plan, because the Manager's word explicitly ordered plan-then-fix automatically.

**Planning (Brain Bridge, `task_id="263"`, stage `plan`).** Seat check: Architect + Senior Programmer (backend/tooling configuration validation plus prompt-budget work). Three turns were needed:

1. Turn 1 returned `<missing_context>mcp-decision-server/server.py</missing_context>` — the fixed small-file bundle does not carry that module.
2. Discovery feed: `custom_context_read_source_files(["mcp-decision-server/server.py"])` produced `context-reports/context_report_20260920_120403_bf05b750.md`, passed back through `context_paths` on the same `task_id`. Turn 2 then returned two questions instead of a plan.
3. Turn 3, carrying the answers, returned the step-ordered plan this log implements.

The turn-2 questions and the decisions taken as Manager-stand-in:

- **D-263-1.** The transcript cap is a character cap named `DECISION_TRANSCRIPT_MAX_CHARS`, default `131072`, blank-means-unset, positive-integer override, `ValueError` on malformed/zero/negative. It bounds the joined prompt text (`"\n".join(turns)`), not the raw bytes, because every other cap on this platform bounds characters and the thing capped is text.
- **D-263-2.** `_get_decision_temperature()` was also made to fail loudly. The planning turn found that the earlier note was only half right: the inline `BRAIN_TEMPERATURE` leg already raised, but this separate reader silently clamped a malformed or out-of-range `DECISION_TEMPERATURE` to 1.0. Leaving one silent reader while fixing the others would be incoherent, so this task covers it and the acceptance criteria were updated.

**Changes.**

- `mcp-decision-server/server.py`: added `_get_decision_transcript_max_chars()` plus the `_DECISION_TRANSCRIPT_MAX_CHARS_DEFAULT = 131072` and `_DECISION_MAX_TOKENS_DEFAULT = 16384` constants; made `_get_decision_temperature()` and `_get_decision_max_tokens()` raise `ValueError` naming the variable and the bad value instead of clamping or falling back; and in `extract_session_decisions()` moved `transcript_bytes`/`transcript_text` above the prompt, capped the joined text at the configured limit, appended `[...truncated at <dropped> chars]`, and built the prompt from the capped text. `transcript_bytes` still feeds the cache key.
- `tests/test_decision_server.py`: adapted `test_decision_temperature_default_and_overrides` to expect the loud failure, and added five regressions — transcript-cap default/blank/override, transcript-cap malformed/zero/negative, output-token default/blank/override, output-token malformed/zero/negative, and a truncation-note integration test that captures the outgoing request and proves the capped text, the exact dropped count, and an unchanged request shape.
- `CHANGELOG.md`: one `Fixed` entry under `## [Unreleased]`.

**Assumptions.** A1 — the documentation step is limited to `CHANGELOG.md`: `mcp-decision-server/README.md` and `mcp-decision-server/.env.example` do not exist, and the Absent-File Policy forbids halting. A2 — the truncation marker wording `[...truncated at N chars]` was chosen to match the brain-bridge marker style.

**Verification.** `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` → `665 passed, 10 warnings in 4.96s`, exit code 0 (baseline before this task: 660 passed). Focused run on `tests/test_decision_server.py` → `149 passed`, exit code 0.

**Review round 1 — `REJECTED_NEEDS_FIXES`; the documentation gap is closed.**

The Code Reviewer seat rejected the first submission on one blocking finding, and it was right.

**F1 — blocking, fixed.** The change set documented nothing for operators. `DECISION_TRANSCRIPT_MAX_CHARS` existed only in code and tests, so an operator could not learn the variable, its default, its blank behaviour, its validation rule, or what the truncation marker means. Documentation was an explicit deliverable of this task, so the omission was a real gap rather than a nit.

The fix updates the EXISTING environment template rather than inventing a new file: the repo-root `.env.example` DECISION_ block now documents all three validated contracts in one place — `DECISION_MAX_TOKENS` (default 16384, positive integer, `ValueError` naming the variable on a malformed, zero or negative value), `DECISION_TEMPERATURE` (default 1.0, inclusive 0.0-2.0, `ValueError` on a malformed or out-of-range value), and the new `DECISION_TRANSCRIPT_MAX_CHARS` (default 131072, blank-means-unset, positive integer, `ValueError` on a malformed, zero or negative value) together with the `[...truncated at N chars]` marker and the fact that N is the DROPPED character count, not the retained size. `mcp-decision-server/README.md` and `mcp-decision-server/.env.example` remain absent, so the repo-root template is the applicable existing location.

**Note on the reviewer's XML.** The reviewer's `hands_implementation_task` block failed the bridge's semantic gate (`missing required <documentation_phase> element`), so it arrived as prose under an `[xml-semantic-reject]` prefix with `xml_blocks` empty. Only its prose intent was executed; the malformed XML was not treated as a contract.

**Non-blocking observations carried forward, no change made.** The cache key hashes the raw transcript bytes while the prompt carries capped text (not triggerable inside one process, because the cap is an environment constant); the marker wording reads as "cut to N" although it reports the dropped count, which matches the task contract; and `DECISION_TEMPERATURE` is only read when `BRAIN_TEMPERATURE` is also set, which is pre-existing behaviour outside this task's scope.

**Verification after the fix.** `rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` → `665 passed, 10 warnings in 5.03s`, exit code 0.

**Review round 2 — `APPROVED`; `PO_REVIEW_PENDING`.**

The re-review confirmed the round-1 documentation defect is closed and approved the change set. The reviewer's closing lines, verbatim:

> **Review Status: `APPROVED`**
>
> **`PO_REVIEW_PENDING`** — Code approved technically. PO, please review UX/Business logic. Reply "Approved for closure" to commit and finish.

It cited the operator documentation at `.env.example:40-55` (`DECISION_MAX_TOKENS` default 16384 with positive-value validation, `DECISION_TEMPERATURE` default 1.0 with the inclusive 0.0-2.0 range, `DECISION_TRANSCRIPT_MAX_CHARS` default 131072 with blank-means-unset and positive-integer validation), the code regions `mcp-decision-server/server.py:213-230` (the new cap reader), `:234-254` (the loud temperature reader), `:298-321` (the loud output-token reader) and `:1296-1310` (the cap applied before prompt construction, with the marker reporting the exact dropped count at `:1300-1305` and the raw bytes still feeding the cache key at `:1296`), the regressions at `tests/test_decision_server.py:451-510` and `:612-681`, and the changelog at `CHANGELOG.md:33-34`. It recorded the QA observations as non-blocking and noted that the focused run passed `149` and the full suite passed `665 passed, 10 warnings` with exit code 0.

**Manager approval.** The Manager replied with the exact closure phrase: "Approved for closure". Closure proceeded on that word, because the reviewer returned `APPROVED` with `PO_REVIEW_PENDING`, every acceptance criterion is verified, and the full suite is green.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `937724016edb6faab60f322564cc8d354649255a`
<!-- END_GIT_DIFF -->
