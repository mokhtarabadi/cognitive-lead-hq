# Task 263: Decision server sends the whole session transcript unbounded and swallows a malformed output-token cap

**File:** `tasks/qa/263-decision-server-transcript-cap-and-cap-validation.md`
**Source:** manager
**Type:** bug
**Status:** open

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
- [ ] Extract the Manager's decisions from the old and the new task sessions and save them

## Acceptance Criteria

- [x] The extraction prompt is bounded by an env-configurable cap that defaults to the current documented behaviour, and the cap honours the blank-means-unset convention used elsewhere in the repo.
- [x] When the transcript exceeds the cap, the prompt carries an explicit truncation note stating the dropped size, so the model is never asked to extract from a silently partial transcript.
- [x] A malformed or non-positive output-token cap raises a configuration error and fails the call loudly, instead of silently falling back to a default.
- [x] The temperature reader fails loudly on a malformed or out-of-range value, matching the brain-bridge caps' discipline.
- [x] The Responses API request shape stays conformant (nested `reasoning.effort`, explicit `max_output_tokens`, `input` as role/content items, temperature never combined with reasoning).
- [x] Regression tests cover the cap default, a blank value, a valid override, a malformed value, a non-positive value, and the truncation note.
- [ ] The Manager's decisions from both the old task session and this task session are extracted and saved.

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

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index b930362..3574e99 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -30,6 +30,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Decision server bounds the transcript prompt and fails loudly on a bad config value (Task 263):** the extraction call joined the whole session transcript into its prompt with no ceiling, so a long session produced an unbounded request — the same starvation class as issue 23 — and two config readers silently papered over a bad setting instead of reporting it. `extract_session_decisions()` now caps the joined transcript at `DECISION_TRANSCRIPT_MAX_CHARS` (default 131072 characters, blank-means-unset) BEFORE the prompt is built, keeping the first N characters and appending `[...truncated at <dropped> chars]` so the caller learns exactly how much was dropped; `transcript_bytes` stays the raw file content used by the cache key. `_get_decision_max_tokens()` (default 16384) and `_get_decision_temperature()` (default 1.0, range 0.0-2.0) now raise `ValueError` naming the variable and the bad value instead of falling back to 16384 or clamping to 1.0. The Responses request shape is unchanged (`model`, `input`, `max_output_tokens`, plus either `temperature` or nested `reasoning.effort`). 5 new tests. Full suite: **665 passed**.
 - **Brain Bridge sees the whole change set: configurable caps + one shared budget (Task 262, syncs GitHub issue 23):** the bridge appended every attachment against its own hard-coded constant, so a reviewer lost the hunks to boilerplate and every seat reported `[...truncated …]` mid-file. Four module defaults moved (`_TASK_ATTACH_CAP` 12000→60000, `_TASK_DIFF_CAP` 20000→200000, `_CTX_PATHS_PER_FILE` 20000→60000, `_CTX_PATHS_TOTAL` 40000→200000) and six caps gained blank-means-unset env overrides (`BRAIN_TASK_ATTACH_CAP`, `BRAIN_TASK_DIFF_CAP`, `BRAIN_CTX_PER_FILE_CAP`, `BRAIN_CTX_TOTAL_CAP`, `BRAIN_INPUT_BUDGET`, `BRAIN_MODEL_WINDOW_CHARS`) resolved at call time through the new `_env_positive_int`, which rejects malformed or non-positive values instead of clamping; `_INPUT_BUDGET` moves 100000→200000 because a live probe showed the assembled system prompt alone is ~87.6k chars, leaving the older ceiling only ~12k for the change set (200k chars is ~43k input tokens at the measured ~4.6 chars/token). The independent append sequence in `brain_turn` is replaced by one shared allocator that renders candidates against the chars actually left after the system prompt and the caller's prompt; `qa`/`review` turns rank context_paths → diff → task → fed context → bundle so explicit evidence outranks the small-file bundle, while history stays the last fallback and is deliberately excluded from the attachment budget (that keeps the static prompt-cache prefix stable across turns). Over-budget attachments chunk into numbered parts with an exact resume offset (`[ATTACHMENT kind=… part=1/3 …]` / `[NEXT_ATTACHMENT_PART … next_offset_chars=…]`) and the new `attachment_resume={"kind","path","offset_chars"}` argument continues them; a malformed resume is ignored with a stderr note. The result payload now splits the two failure modes: `history_turns_dropped` is canonical with `truncated_count` kept as the back-compat alias, and `attachments_truncated` (always a list; entries carry `kind`/`path`/`shown_chars`/`total_chars`/`dropped_chars`/`part`/`parts`) reports attachment loss alongside `attachment_parts`, `attachment_budget_chars`, `attachment_chars_used`, and `attachment_chars_remaining`; the capability-blocked early return carries the same field set. The three standalone builders keep their truncating behaviour for direct callers. `docs/brain-bridge.md` gains the new env-table rows and sections on the allocator, the priority order, the part/resume contract, and the two-truncation payload. The stored transcript no longer keeps the assembled prompt: each user turn is persisted with a compact `[stored-attachment kind=… path=… shown_chars=… total_chars=… part=a/b]` marker per segment instead of the attachment bodies, because every later turn replays the transcript — persisting the bodies made each turn re-pay the previous turn's attachment cost (one QA turn stored a 64,547-char user turn and every turn after it inherited it). The wire prompt is unchanged: attachments are re-derived from disk each turn, so only storage shrinks. The transcript file itself is append-only: every turn ever written stays on disk, and only the load VIEW is compacted in memory (one deterministic digest record plus the newest records), so a task keeps its full history while the send path stays bounded — the lossy rewrite helpers were removed. 27 new tests (cap readers, 60 KB file untruncated at both the builder and the turn level, part numbering + resume, priority order, separate reporting, chunk numbering, review-over-bundle precedence, compact transcript storage, append-only transcript storage) plus 2 regressions in `tests/test_brain_diff_attach.py` for the diff extractor (a `<!-- END_GIT_DIFF -->` marker inside a diff body no longer ends extraction, so a change set that edits the bridge's own marker constants is delivered whole), 3 loud-failure regressions proving a malformed or non-positive cap environment value fails the turn instead of being reported as an unavailable attachment, and 3 existing tests re-pinned to explicit caps. A malformed cap env value is now read outside the candidate guards so the configuration error propagates, and the part-marker reservation is measured from the lines actually emitted (`_marker_room`) instead of a fixed constant, so the running attachment total can no longer exceed the budget. The wrapper a rendered attachment emits (its open line, fence lines and separators, not just the part markers) is now priced against the room the allocator granted, so a block can never be longer than its budget, and the configured per-file cap bounds the CONTENT with the wrapper riding on top — a file that fits its cap exactly still arrives whole. Every `context_paths` file also shares one configured total budget (`BRAIN_CTX_TOTAL_CAP`), enforced across the whole group by the allocator with the overflow reported rather than silently sent, and a malformed or non-positive path cap fails the turn loudly like the task and diff caps do. Full suite: **660 passed**.
 
 - **Secrets-safe repo hygiene + skill question-channel parity:** `.gitignore` now ignores `.env.*` (with an explicit `!.env.example` negation so the template stays tracked) plus `*.bak*`, and this session's project `.env` backup was moved out of the worktree to `~/.config/opencode/.env.project.bak-20260919b` — a `git add -A` can no longer sweep secrets into history. Seven skill templates that ask the Manager or user a question now point at the `question` tool when the session capability manifest shows it AVAILABLE and fall back to the prose relay otherwise: `telegram-message-export` (its unconditional mandate replaced), `decision-migration` (both gate spots), `opencode-init`, `doc-coauthoring`, `prompt-refactor`, and `manager-decision`; `telegram-issue-sync` already carried the wording. Every changed `SKILL.md` is synced to the global install (36/36 skills, zero drift, no orphans).
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index 7869ad9..1907de7 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -202,18 +202,63 @@ PROVIDER_ERROR = "PROVIDER_ERROR"
 PROVIDER_REFUSAL = "PROVIDER_REFUSAL"
 
 
+#: Default character cap for the joined session transcript sent to the model.
+_DECISION_TRANSCRIPT_MAX_CHARS_DEFAULT = 131072
+
+#: Default output-token ceiling for extraction turns.
+_DECISION_MAX_TOKENS_DEFAULT = 16384
+
+
+def _get_decision_transcript_max_chars() -> int:
+    """Character cap for the session transcript sent to the model.
+
+    Override via ``DECISION_TRANSCRIPT_MAX_CHARS`` (default 131072). Blank
+    means unset — the default wins. A malformed, zero, or negative value
+    raises instead of letting an unbounded prompt reach the provider: an
+    oversized transcript is the exact failure this cap exists to bound.
+    """
+    raw = os.environ.get("DECISION_TRANSCRIPT_MAX_CHARS", "").strip()
+    if not raw:
+        return _DECISION_TRANSCRIPT_MAX_CHARS_DEFAULT
+    try:
+        value = int(raw)
+    except ValueError:
+        raise ValueError(
+            f"DECISION_TRANSCRIPT_MAX_CHARS={raw!r} is not an integer; "
+            "set a positive integer or leave it blank"
+        )
+    if value <= 0:
+        raise ValueError(
+            f"DECISION_TRANSCRIPT_MAX_CHARS={value} must be positive"
+        )
+    return value
+
+
 def _get_decision_temperature() -> float:
     """Extraction sampling temperature; override via ``DECISION_TEMPERATURE``.
 
     Defaults to 1.0 (matches the house temperature policy; the old hardcoded
-    0.2 was a Gemini-era leftover). Out-of-range or unparsable values clamp
-    to 1.0 instead of crashing a live turn.
+    0.2 was a Gemini-era leftover). Blank means unset — the default wins. A
+    malformed or out-of-range value raises instead of being clamped: a bad
+    configuration must fail loudly, never be silently replaced by a default
+    the operator did not choose.
     """
+    raw = os.environ.get("DECISION_TEMPERATURE", "").strip()
+    if not raw:
+        return 1.0
     try:
-        value = float(os.environ.get("DECISION_TEMPERATURE", "1.0") or 1.0)
+        value = float(raw)
     except ValueError:
-        return 1.0
-    return value if 0.0 <= value <= 2.0 else 1.0
+        raise ValueError(
+            f"DECISION_TEMPERATURE={raw!r} is not a number; "
+            "set a value between 0.0 and 2.0 or leave it blank"
+        )
+    if not 0.0 <= value <= 2.0:
+        raise ValueError(
+            f"DECISION_TEMPERATURE={raw!r} is out of range; "
+            "use 0.0-2.0 or leave it blank"
+        )
+    return value
 
 
 def _get_decision_model() -> str:
@@ -253,12 +298,23 @@ def _get_decision_max_tokens() -> int:
     The extraction call used to send no cap at all, leaving the ceiling to
     the provider. Reasoning tokens are billed as output and count against
     this cap on most providers, so an explicit value keeps the cost and the
-    truncation boundary predictable.
+    truncation boundary predictable. Blank means unset — the default wins.
+    A malformed, zero, or negative value raises instead of silently falling
+    back, so a bad configuration can never masquerade as the default.
     """
+    raw = os.environ.get("DECISION_MAX_TOKENS", "").strip()
+    if not raw:
+        return _DECISION_MAX_TOKENS_DEFAULT
     try:
-        return int(os.environ.get("DECISION_MAX_TOKENS", "16384").strip() or "16384")
+        value = int(raw)
     except ValueError:
-        return 16384
+        raise ValueError(
+            f"DECISION_MAX_TOKENS={raw!r} is not an integer; "
+            "set a positive integer or leave it blank"
+        )
+    if value <= 0:
+        raise ValueError(f"DECISION_MAX_TOKENS={value} must be positive")
+    return value
 
 
 #: Advertised reasoning-effort support for the models this server ships a
@@ -1234,16 +1290,27 @@ def extract_session_decisions(
             f"decision transcript {path} exists but holds zero turns — "
             f"refusing to treat a broken pipeline as 'no rulings'"
         )
+    # The transcript is sent whole, so an oversized session produced an
+    # unbounded prompt — the exact starvation this cap exists to bound.
+    # Cap the joined text BEFORE the prompt is built and report the
+    # dropped size, never silently.
+    transcript_bytes = path.read_bytes()
+    transcript_text = "\n".join(turns)
+    _max_chars = _get_decision_transcript_max_chars()
+    if len(transcript_text) > _max_chars:
+        dropped_chars = len(transcript_text) - _max_chars
+        transcript_text = (
+            transcript_text[:_max_chars]
+            + f"\n[...truncated at {dropped_chars} chars]"
+        )
     prompt = (
         "Extract the MANAGER's decisions, trade-offs, and rulings from this session "
         "transcript. Preserve each ruling's verbatim quote. Reply with a JSON array; "
         "each item: {verbatim_quote: {original, english_translation}, "
         "extracted_decision: {summary, category, rationale, alternatives[], tradeoffs}}. "
         "Use categories: architecture/process/scope/quality-gate/tooling/release/other. "
-        "Empty array when the session holds no manager rulings.\n\n" + "\n".join(turns)
+        "Empty array when the session holds no manager rulings.\n\n" + transcript_text
     )
-    transcript_bytes = path.read_bytes()
-    transcript_text = "\n".join(turns)
     effort = _get_decision_effort()  # Validated always; sent when no explicit temp.
     # Temperature-vs-effort rule (mirrors the Brain bridge): an explicitly
     # set temperature wins (temperature sent, effort dropped — Responses
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index 290bd63..e8f0d50 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -448,6 +448,77 @@ def test_extract_parses_stubbed_llm_json(srv, tmp_path, monkeypatch):
     assert target(1, transcript_path=str(transcript)) == candidates
 
 
+def test_extract_truncates_oversized_transcript_with_note(
+        srv, tmp_path, monkeypatch):
+    # The transcript is sent whole, so an oversized session produced an
+    # unbounded prompt — the exact starvation the cap exists to bound. The
+    # prompt now carries the capped text plus an explicit dropped count.
+    lines = [
+        json.dumps({"role": "user", "content": "x" * 40}) for _ in range(5)
+    ]
+    transcript = tmp_path / "transcript.jsonl"
+    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
+    joined = "\n".join(f"[user] {'x' * 40}" for _ in range(5))
+    monkeypatch.setenv("DECISION_TRANSCRIPT_MAX_CHARS", "20")
+
+    captured: dict = {}
+    stub_resp = types.SimpleNamespace(
+        status_code=200, text="stub", headers={},
+        raise_for_status=lambda: None,
+        json=lambda: {
+            "output": [
+                {"type": "message",
+                 "content": [{"type": "output_text", "text": "[]"}]}
+            ]
+        },
+    )
+
+    class _FakeClient:
+        def __init__(self, *a, **k):
+            pass
+
+        def __enter__(self):
+            return self
+
+        def __exit__(self, *a):
+            return False
+
+        def post(self, *a, **k):
+            captured["kwargs"] = k
+            return stub_resp
+
+    stub = types.ModuleType("httpx")
+    stub.Client = _FakeClient
+    stub.TimeoutException = type("TimeoutException", (Exception,), {})
+    stub.TransportError = type("TransportError", (Exception,), {})
+
+    class _Timeout:
+        def __init__(self, *a, **k):
+            pass
+
+    stub.Timeout = _Timeout
+    monkeypatch.setitem(sys.modules, "httpx", stub)
+    call = srv.extract_session_decisions
+    target = call.fn if hasattr(call, "fn") else call
+    assert target(1, transcript_path=str(transcript)) == []
+
+    kwargs = captured["kwargs"]
+    sent = kwargs.get("json")
+    if sent is None:
+        raw = kwargs.get("content")
+        sent = json.loads(raw) if isinstance(raw, (str, bytes)) else None
+    assert isinstance(sent, dict), kwargs
+    # The request shape is unchanged: the same core fields, nothing new.
+    assert {"model", "input", "max_output_tokens"} <= set(sent)
+    assert set(sent) <= {"model", "input", "max_output_tokens",
+                         "reasoning", "temperature"}
+    content = sent["input"][0]["content"]
+    dropped = len(joined) - 20
+    assert f"[...truncated at {dropped} chars]" in content
+    # The uncapped tail never reached the provider.
+    assert content.count("x" * 40) == 0
+
+
 def test_load_env_files_from_cwd_and_never_overrides(srv, tmp_path, monkeypatch):
     (tmp_path / ".env").write_text(
         "DECISION_TEST_PROBE=probe-value-456\n", encoding="utf-8"
@@ -541,10 +612,54 @@ def test_decision_temperature_default_and_overrides(srv, monkeypatch):
     assert srv._get_decision_temperature() == 1.0
     monkeypatch.setenv("DECISION_TEMPERATURE", "0.2")
     assert srv._get_decision_temperature() == 0.2
-    monkeypatch.setenv("DECISION_TEMPERATURE", "not-a-float")
+    # Blank means unset: the default wins.
+    monkeypatch.setenv("DECISION_TEMPERATURE", "")
     assert srv._get_decision_temperature() == 1.0
-    monkeypatch.setenv("DECISION_TEMPERATURE", "9.9")
-    assert srv._get_decision_temperature() == 1.0  # Clamped, never crashes.
+    # A bad configuration fails loudly instead of being clamped away.
+    for bad in ("not-a-float", "9.9", "-0.5"):
+        monkeypatch.setenv("DECISION_TEMPERATURE", bad)
+        with pytest.raises(ValueError) as err:
+            srv._get_decision_temperature()
+        assert "DECISION_TEMPERATURE" in str(err.value)
+
+
+def test_decision_transcript_max_chars_default_blank_and_override(
+        srv, monkeypatch):
+    # Blank means unset: the documented default wins.
+    monkeypatch.delenv("DECISION_TRANSCRIPT_MAX_CHARS", raising=False)
+    assert srv._get_decision_transcript_max_chars() == 131072
+    monkeypatch.setenv("DECISION_TRANSCRIPT_MAX_CHARS", "")
+    assert srv._get_decision_transcript_max_chars() == 131072
+    monkeypatch.setenv("DECISION_TRANSCRIPT_MAX_CHARS", "4096")
+    assert srv._get_decision_transcript_max_chars() == 4096
+
+
+def test_decision_transcript_max_chars_rejects_bad_values(srv, monkeypatch):
+    # An oversized transcript is exactly what this cap exists to bound, so
+    # a bad configuration must fail loudly rather than fall back.
+    for bad in ("abc", "0", "-5"):
+        monkeypatch.setenv("DECISION_TRANSCRIPT_MAX_CHARS", bad)
+        with pytest.raises(ValueError) as err:
+            srv._get_decision_transcript_max_chars()
+        assert "DECISION_TRANSCRIPT_MAX_CHARS" in str(err.value)
+
+
+def test_decision_max_tokens_default_blank_and_override(srv, monkeypatch):
+    monkeypatch.delenv("DECISION_MAX_TOKENS", raising=False)
+    assert srv._get_decision_max_tokens() == 16384
+    monkeypatch.setenv("DECISION_MAX_TOKENS", "")
+    assert srv._get_decision_max_tokens() == 16384
+    monkeypatch.setenv("DECISION_MAX_TOKENS", "2048")
+    assert srv._get_decision_max_tokens() == 2048
+
+
+def test_decision_max_tokens_rejects_bad_values(srv, monkeypatch):
+    # Previously a malformed value silently fell back to 16384.
+    for bad in ("abc", "0", "-1"):
+        monkeypatch.setenv("DECISION_MAX_TOKENS", bad)
+        with pytest.raises(ValueError) as err:
+            srv._get_decision_max_tokens()
+        assert "DECISION_MAX_TOKENS" in str(err.value)
 
 
 def test_repo_root_falls_back_when_cwd_blocked(srv, tmp_path, monkeypatch):
```
<!-- END_GIT_DIFF -->
