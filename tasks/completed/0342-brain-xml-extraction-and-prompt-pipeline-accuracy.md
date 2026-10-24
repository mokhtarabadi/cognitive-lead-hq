# Task 342: Brain XML extraction and prompt-pipeline accuracy

**File:** `tasks/qa/0342-brain-xml-extraction-and-prompt-pipeline-accuracy.md`
**Source:** manager
**Type:** bugfix
**Status:** in-progress
**Estimate:** 2h
**Sprint:** S26-W43
**Milestone:** M01

## Goal

Make the Brain bridge accept every legitimate XML shape exactly once — bare, three-backtick and four-backtick `xml` fences, bodies carrying their own Python/JS/diff samples, and Markdown documents — and restore the prompt build pipeline so a rebuild reproduces the shipped system prompt byte for byte. A correct Brain answer must never cost a re-emit, and a documentation sample must never execute as an instruction.

## Manager's Notes

- Trigger: the 0339 implementation turn was rejected as `XML_STRICT_REJECT_FENCE_FALLBACK` after the Brain fenced a `hands_implementation_task` whose `<execution_phase>` carried ` ```python ` samples. 25,503 characters were withheld and the block had to be re-emitted in a second turn.
- "Fix it without a task" was the first order; this task was created afterwards to carry the changes, on the condition that they do not overlap task 339 (they don't: planner vs brain/prompts, only `CHANGELOG.md` is shared).

## Findings

- **F1.** `_XML_FENCE_RE` could not nest, so an ` ```xml ` body containing its own fence was closed early; the truncated body tripped the unclosed-tail check and rejected the whole turn.
- **F2.** The bare-block scan ran on `_strip_fences` output, whose non-nesting strip mis-slices the same body, so an operator-shaped literal inside a documentation sample was returned as a real block while the real one was dropped (false positive, worse than F1).
- **F3.** Four-backtick ````xml is the canonical CommonMark wrapper for a body carrying fences, and the extractor ignored it entirely.
- **F4.** `split_system_prompt.py` knew 20 top-level tags: `<night_mode>` and the trailing Markdown language-policy section were dropped on rebuild, and every fragment was renumbered. `test_system_prompt_split_assemble_round_trip` was failing before this task.
- **F5.** Prompt and executor text disagreed with the gateway: the reject hint said "re-emit bare unfenced XML" although manual mode forces a fence, and the executor claimed a missing mode line "fence-strict-rejects".

## Local TODOs

- [x] Step 1: Replace fence regex with the line-accurate `_xml_fence_segments` scanner (3+ backticks, close only on a bare run of at least the opener's length)
- [x] Step 2: Add `_extract_complete_blocks` (line-start anchored) for fence bodies and the forward rescue scan `_rescue_fenced_block`
- [x] Step 3: Run the bare-block scan on `_mask_fenced_code` instead of the mis-slicing regex strip
- [x] Step 4: Support four-backtick ````xml wrappers; keep bare quad fences and non-xml fences as documentation
- [x] Step 5: Add `night_mode` to the splitter's top-level tags and capture the trailing Markdown section as a fragment, reusing committed filenames
- [x] Step 6: Reword the strict-reject hints, the manual-mode guidance in `06-personas.md`, the executor mode line, and `docs/brain-bridge.md`
- [x] Step 7: Bump `<system_version>` to 9.64.1, regenerate `system-prompt.md`, deploy and restart `mcp-brain`

## Acceptance Criteria

- [x] A fenced `hands_implementation_task` carrying ` ```python ` samples extracts complete on the first turn
- [x] An operator-shaped literal inside a code sample never extracts as a block
- [x] ` ```xml `, ````xml, bare and unclosed-fence answers all behave correctly; a genuinely truncated block still rejects
- [x] `assemble(split(system-prompt.md))` is byte-identical to the shipped prompt
- [x] Prompt, executor and bridge agree on the manual/automatic emission contract
- [x] Full test suite passes with exit code 0

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q`
- **Expected result:** Full suite green, including the previously failing `test_system_prompt_split_assemble_round_trip`
- **Actual result:** `665 passed, 24 warnings in 44.77s` (suite after the inline-code guard); bridge subset 293 passed; prompt/splitter subset 103 passed; round-trip byte-identical (108,701 bytes)
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded
- [x] Deployed copies byte-identical under `~/.config/opencode/` (`mcp-brain-bridge/server.py`, `system-prompt.md`, `agents/cognitive-executor.md`) and `mcp-brain` restarted

## Risk & Rollback

- **Risk:** the forward rescue can extract a later allowlisted block that sits between a truncated fence body and the next `xml` opener. Accepted because that path previously produced no output at all.
- **Risk:** making four-backtick fences operative reverses a deliberately pinned behavior (`test_extract_quad_xml_fence_stays_ignored`), so the pin was rewritten rather than deleted.
- **Rollback:** restore the single `_XML_FENCE_RE.finditer` loop, drop the new helpers and tests, revert the splitter tail capture, and re-pin the version to 9.64.0.

## Execution Log & Reasoning

**Mode:** manual, no task file at the time (explicit Manager order "بدون تسک درستش کن"); this task was created afterwards at the Manager's request to carry the diff.

**Autopilot lock (2026-10-24):** Manager ordered "start auto lock for task 342". Locked: QA, fix, and review turns are chained by the Hands under the same `task_id`; the Manager sees only Relay questions and the final verdict, and the closure gate still needs his exact word.

**Seat Check:** domain = Brain bridge extraction plus prompt build pipeline. Seats: Senior Programmer (implementation) with Software Architect for the extraction contract. Skipped: UI/UX (no frontend), QA/Reviewer (post-implementation gates). Brainstorm: not required — offline parser and build-script changes, reversible via git revert, no security/financial/migration surface.

**Decisions:**

- **D1 — line scanner over regex.** CommonMark closes a fence only on a bare run of the same character at least as long as the opener, which a single regex cannot express; the scanner makes ````xml work and keeps non-xml fences documentation.
- **D2 — line-start anchoring for fence bodies.** The mid-line tolerant `_XML_RE` stays for the bare path (existing tolerance tests), while fenced bodies and rescue use `_extract_complete_blocks`, so `sample = "<hotfix>…</hotfix>"` cannot win.
- **D3 — rescue only where the old code raised.** A truncated block still rejects; the strict gate never repairs input.
- **D4 — prompt guidance prefers ````xml.** Manual mode now names the four-backtick wrapper for bodies with fenced code, and the reject hint no longer contradicts manual mode.

**Evidence trail:** reproduced F1 and F2 offline before changing anything (nested block → zero blocks; doc sample → extracted as `<hotfix>`), then pinned both. `git diff --stat` for this task covers the bridge, its tests and decisions, `docs/brain-bridge.md`, `agents/cognitive-executor.md`, the prompt fragments touched by the pipeline fix plus `06-personas.md`, `system-prompt.md`, the splitter and its ADR, the version pin, and `CHANGELOG.md`.

**Note on shared index:** `CHANGELOG.md` is shared with task 339. Task 339's six planner files were unstaged before this task's QA transition so its injected diff stays clean; 339 keeps its already-injected diff and must be re-staged at its closure.

**Autopilot QA/Review chain (2026-10-24):**

- QA turn 1: `VERDICT: QA_PASSED` (VISIBLE hunks; splitter/tests past the 60k cutoff marked UNVERIFIABLE). The same reply exposed a live defect: a quoted sample literal in prose came back `XML_EXTRACTED`, so the bridge would have executed it.
- Fix F6: `_bare_blocks` now skips a match inside an inline code span (odd backtick count earlier on the same line); mid-line bare blocks outside inline code keep their pinned tolerance. New test `test_extract_midline_quoted_hotfix_stays_ignored`; suite 665 passed, exit 0; deployed and `mcp-brain` restarted.
- QA turn 2 (post-fix): `VERDICT: QA_PASSED`, and the extraction correctly returned `REPORT` with no bogus block.
- Reviewer turn: technically approved — `PO_REVIEW_PENDING`, issues I1/I2 UNVERIFIABLE-past-cutoff only, I3 newline churn, I4 shared CHANGELOG hunk; no scope creep into planner files. Diff re-staged after the fix so the QA/review snapshot matches the worktree.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 46b53a9..74e779a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Planner dashboard overhaul and a guarded task reader (Task 339):** the board is usable with 330+ tasks on it. `GET /api/task?id=<id>` / `?path=tasks/<lane>/<file>.md` returns `{id, path, lane, title, markdown}` so the new full-screen modal can render a task's whole body — todos, acceptance criteria, and `## Factual Git Diff` — with `id` winning when both params arrive. The route is deliberately not a file-read primitive: the new `_safe_task_path` accepts exactly three segments, a lane from `TASK_LANES`, a `.md` suffix, and no absolute prefix, drive colon, backslash, or `..`/`.`, then resolves and re-checks containment inside the project root; authorization reuses `AuthState.project_allowed` and the `_api_status` fallback to a session's first allowed root. Status mapping is explicit — 400 missing param, 401 no session, 403 outside grants *and* unsafe path (never 404, so the route cannot confirm whether a file exists), 404 unknown id, 500 unexpected; the `_api_status` blanket `except → 200 {"error": …}` pattern is not copied. `_task_brief` now carries `path` so cards can deep-link. The dashboard (`static/index.html`, still zero external URLs) caps each lane at `calc(100vh - 280px)` with inner scrolling and a sticky header, collapses the Archive lane behind an `Archive (N)` toggle remembered in `localStorage`, adds a client-only search input filtering by id/name/title, and opens the task modal through one delegated listener on the grid so the 30 s poll cannot drop the binding. The Markdown renderer is inline and self-contained: source is HTML-escaped first, then fences, headings, lists, task checkboxes, blockquotes, tables, and inline emphasis are added, diffs get `--success`/`--danger` line colouring, rendering stops at 2000 lines, and links are limited to same-origin or in-page targets. Docs: component `README.md` route table plus `DECISIONS.md` ADR-007. Verified: 97/97 planner tests pass (17 new: by id, by path, int-normalized id, 404, 400, eight traversal shapes at 403, route registration, 401, cross-project viewer 403, traversal over HTTP, open mode), `py_compile` and a JS parse of the inline script are clean, deployed `server.py`/`README.md`/`DECISIONS.md`/`static/index.html` are byte-identical to the repo copies, and the live unit on `127.0.0.1:8108` serves the new dashboard markup while `/api/task` answers 401 without a session and 400 with no param.
+
 - **Plugin references synced to the new tool set and evidence contract (Task 341):** a graph scan over this worktree (4,766 nodes, 6,788 links) plus targeted greps found four live documents lagging behind the two plugin releases. `agents/cognitive-executor.md` now carries `compact_stats` in the Smart Compact section and in the protocol contract (no inputs, read-only, same formatter as `/magic-stats`, never a poll), and states that every `goal_set` starts a fresh empty evidence sidecar while the legacy `.opencode/goal-evidence.json` is read only until the session owns its own, which is what stopped a finished goal's failing command from gating later ones. `docs/compaction.md` documents the stats tool under Agent-callable tools and the evidence reset in the goal-plugin section; `README.md`'s plugin lane carries both. `tests/test_prompt_sync.py` pins `compact_stats` so the executor cannot drift back, and the smart-compact policy memory shard lists the third tool plus the installed commit `2e702680`. Verified: prompt-sync tests exit 0, `lint_system_prompt_sync` consistent, `prettier --check` clean.
 
 - **Loopback MCP transport unblocked (Task 338):** `/mcp` is auth-free again, in open mode and with authentication enabled alike. `_guarded_mcp_app` in `mcp-planner-server/server.py` is now a pass-through to the FastMCP transport — no `SESSION_COOKIE` lookup, no admin-role check, no 401/403 from that path — so OpenCode's local clients connect without credentials even while the dashboard requires a login. Remote exposure was never carried by that guard: the Cloudflare Tunnel ingress answers `http_status: 404` for `^/mcp(/.*)?$` before the catch-all, so the endpoint is unreachable off-host. `/`, `/static/*`, `/api/login`, `/api/logout`, `/api/me`, and `/api/status` keep their session checks untouched; the dead `_send_json` helper (whose only callers were the deleted guard branches) is removed and the module docstring corrected. The three former guard tests (`401` unauthenticated, `403` viewer, admin admitted) are replaced by `test_mcp_open_without_session_when_auth_enabled`, `test_mcp_open_for_viewer_session`, and `test_api_status_stays_guarded_while_mcp_is_open`, which pins the split — one auth-enabled app where `/mcp` passes and `/api/status`/`/api/me` still answer 401. Because tool execution now trusts the bind and the edge instead of an in-process guard, the `^/mcp(/.*)?$ → 404` ingress rule is load-bearing: the component README states it as a Key Risk invariant and `DECISIONS.md` ADR-006 records the decision and its consequences (ADR-005 is marked superseded in part). Docs updated in `docs/services.md` and `mcp-planner-server/README.md`. Verified: 76/76 planner tests pass, deployed `server.py` is byte-identical to the repo copy, unit `active` on `127.0.0.1:8108`, and a cookie-free `initialize` → `notifications/initialized` → `tools/list` handshake returns the tool array while `GET /api/me` and `GET /api/status` still answer 401.
@@ -43,6 +45,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Bridge extraction is now line-accurate in every shape (fences, Python samples, Markdown):** three defects closed in one pass. Fence recognition moved from regex to `_xml_fence_segments`, which walks lines and closes a fence only on a bare run of the same character at least as long as the opener — so a four-backtick ````xml fence is now the canonical wrapper for a body carrying three-backtick samples, and a three-backtick body that closes early is repaired by a forward rescue scan (`_rescue_fenced_block`). The fence-body and rescue passes use `_extract_complete_blocks`, which anchors openers at line starts, so an operator-shaped literal inside a code sample (`sample = "<hotfix>not real</hotfix>"`) is never mistaken for an instruction while the real block is dropped. The bare-block scan runs on `_mask_fenced_code`, a line-accurate CommonMark mask, instead of the mis-slicing regex strip. Gateway and prompt now agree: manual mode recommends ````xml when the body holds fenced code, and both the system prompt (`<system_version>9.64.1`) and `agents/cognitive-executor.md` say so; the executor's claim that a missing mode line "fence-strict-rejects" is corrected to what actually happens (the Brain cannot tell which shape is live). Also: `scripts/prompt-build/split_system_prompt.py` now knows `night_mode` and captures the trailing Markdown language-policy section as a fragment, reusing committed filenames so a rebuild renames nothing — the round-trip test that had been failing on `<night_mode>` passes and `assemble(split(prompt))` is byte-identical. Verified: 292/292 bridge tests (new: quad wrapper, nested doc-sample non-leak), 103/103 prompt/splitter tests, full suite green, deployed copies byte-identical, `mcp-brain` restarted.
+
+- **Fenced XML with inner code fences no longer burns a turn (bridge extractor):** in manual mode the Brain is told ` ```xml ` fences are expected, so it wraps `hands_implementation_task` bodies that themselves contain ` ```python ` samples. The extractor could not nest, closed the fence body at the first inner fence, saw a truncated opener, and rejected the whole answer as `XML_STRICT_REJECT_FENCE_FALLBACK` — replacing a ~25k-char block with the reject header plus its first 2000 chars, so the Hands had to ask for a complete re-emit (one wasted round trip and ~10k output tokens). `extract_xml_blocks` now walks line-anchored ` ```xml ` openers in order (`_XML_FENCE_OPEN_RE`, info-string-checked so quad and non-xml fences stay documentation-only), tries the ordinary fence body first, and when that body holds no complete allowlisted block scans forward from the opener — bounded by the next opener — for the block's closing tag. The rescue only runs on the path that used to raise, and a genuinely truncated block still raises the same code, so the strict gate never repairs input. Reproduced offline before the fix (fenced block with one inner fence → zero blocks), then pinned by three tests: `test_extract_xml_fenced_hands_block_with_inner_code_fences`, `test_extract_rescued_fences_stay_ordered_and_bounded`, `test_extract_truncated_xml_fence_still_rejects`. Same area, mirror-image defect fixed in the same pass: the bare-block scan ran on `_strip_fences` output, whose non-nesting strip mis-slices the same nested body, so an operator-shaped literal inside a documentation sample (`sample = "<hotfix>not real</hotfix>"` in a ` ```python ` block) was returned as a live instruction while the real block was dropped. The scan now runs on the new `_mask_fenced_code` line-accurate mask (opener with info string through the next bare run of the same character and length), and `_strip_fences` is kept for diagnostics only; pinned by `test_extract_ignores_operator_tag_in_nested_fence_sample`. Bridge `DECISIONS.md` ADR-008 records the decision and the rollback. Verified: 290/290 `tests/test_brain_bridge.py` pass, and the full suite is 661 passed with one pre-existing unrelated failure (`test_system_prompt_split_assemble_round_trip` in `tests/test_mcp_servers.py` drops the `<night_mode>` fragment — untouched by this change and present before it).
+
 - **Stale plugin citations corrected (same task):** the executor's `src/loop.ts 205-437` reference now names the real gate (`shouldContinue` at `src/loop.ts:458-492`) and handler (`handleSessionIdle` at `src/loop.ts:552-853`); the stop-file claim now states that the code reads only the projectDir `.opencode/STOP_GOAL` path (`src/index.ts:284-296`) and that the project-root path is never read; the "exact-only" slash list now covers the full parser surface (objective, block reason, resume, and evidence accept arguments; status, clear, and complete are exact-only); the missing `/goal resume` and `/goal evidence` slash inputs are documented; the goal lane's "exactly two goal writes" rule becomes three writes plus resume, matching the restored `goal_set` trigger.
 - **Compaction task-boundary gap closed (same task):** the previous task being finished and the Manager defining a new task in the same session now triggers `compact_context` with `keepTurns` 0 and `mode` `compact`, and the todo list is recovered with `todoread` rather than from a remembered transcript.
 - **Layered provider timeouts raised and made tunable (task 331 follow-up):** big `xhigh`/`max` turns were dying with `provider overall deadline hit (500.0s) ... RemoteProtocolError: Server disconnected without sending a response`. Root cause was three stacked ceilings where the tightest won: `zen-proxy`'s hard-coded `urlopen(timeout=300)` dropped any upstream call thinking longer than 5 minutes, and the bridge's hard-coded `_OVERALL_DEADLINE_S = 500` fired during the retry that followed. The proxy timeout is now `ZEN_PROXY_UPSTREAM_TIMEOUT` (default 900) and the bridge deadline is `BRAIN_OVERALL_DEADLINE_S` (default 900, fail-loud on malformed values); the MCP client timeout for the brain server moved 600s → 1200s so the client no longer cuts a legitimate turn. Verified live: a deep `xhigh` turn with 7,583 reasoning tokens completes, and both singletons load the new values.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 74636e5..8fa340c 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -405,10 +405,11 @@ needs no extra machinery.
    emit bare unfenced XML only, never xml-fenced blocks; do NOT emit any
    copy-paste relay instructions ("Manager: please copy...") — the Hands
    chain QA/review turns directly.` Manual: `MODE: MANUAL — xml-fenced
-   blocks expected; copy-paste relay instructions expected.` Skip this
-   line and the Brain fence-strict-rejects in autopilot and keeps
-   emitting admin copy-paste text in a silent pipeline.
-   **Session Binding (Mandatory):** You MUST pass `session_id: "$OPENCODE_SESSION_ID"` (reading your active session ID from the environment) in every `brain_turn` call alongside `task_id`. Because the MCP server runs as a separate daemon, you must send this parameter explicitly over the wire so the conversation history continues in `tasks/.sessions/<session_id>/transcript.jsonl`.
+   blocks expected (a four-backtick ````xml wrapper when the body carries
+   its own fenced code); copy-paste relay instructions expected.` Skip this
+   line and the Brain cannot tell which shape is live: it keeps emitting
+   admin copy-paste text in a silent pipeline and fenced output where bare
+   was required.   **Session Binding (Mandatory):** You MUST pass `session_id: "$OPENCODE_SESSION_ID"` (reading your active session ID from the environment) in every `brain_turn` call alongside `task_id`. Because the MCP server runs as a separate daemon, you must send this parameter explicitly over the wire so the conversation history continues in `tasks/.sessions/<session_id>/transcript.jsonl`.
 2. **Call** `brain_turn`. Read `status`:
    - `XML_EXTRACTED` — execute `xml_blocks` as the next instruction set,
      exactly like an Orchestrator XML block.
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index ed7c8cf..bc891fa 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -13,7 +13,8 @@ retired persona engine. The Hands calls it for every Brain turn
    live: `MODE: AUTOMATIC (autopilot locked) — emit bare unfenced XML
    only; no copy-paste relay instructions` in autopilot, `MODE: MANUAL
    — xml-fenced blocks and copy-paste relay instructions expected`
-   otherwise.
+   otherwise (a four-backtick ````xml wrapper when the body carries its
+   own fenced code).
 2. **The bridge loads the system prompt** from the global install
    (`~/.config/opencode/system-prompt.md`, override via
    `BRAIN_SYSTEM_PROMPT`) and sends system + history + new prompt
@@ -24,7 +25,12 @@ retired persona engine. The Hands calls it for every Brain turn
    `XML_EXTRACTED` with the block; otherwise `REPORT` with the text.
    Bare unfenced XML extracts first (automatic mode); when none exists,
    allowlisted blocks inside explicit ```xml fences extract (manual
-   copy-paste mode). Other fences stay documentation-only.
+   copy-paste mode). Other fences stay documentation-only. A fenced body
+   that carries its own fenced code samples cannot nest, so the body is
+   rescanned from its opener (bounded by the next opener) for the block's
+   closing tag — that rescue keeps a manual-mode answer from costing a
+   re-emit. A genuinely truncated block is still rejected as
+   `XML_STRICT_REJECT_FENCE_FALLBACK` / `..._UNCLOSED_TAIL`, never repaired.
 4. **Questions relay to the Manager.** A `QUESTION` verdict pauses
    the Hands until the Manager answers.
 
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index cb2c70c..7f4dde6 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -42,6 +42,15 @@
 - **Consequences:** Strict providers accept history replays regardless of id length. The skip applies on the send path for every provider (lenient ones simply never needed it — they ignored the over-long id instead of 400ing). Three regression tests pin the drop, the at-cap pass-through, and the redacted diagnostic. The skip diagnostic records only the id length and the cap, never item fields.
 - **Rollback:** Revert the length check plus the two tests; old transcripts keep working on lenient models.
 
+## [2026-10-24] ADR-008: Fenced XML extraction rescues nested code fences
+
+- **Context:** In manual mode the Hands tells the Brain "xml-fenced blocks expected" and the Brain complies: it wraps a `hands_implementation_task` in ` ```xml `. That body legitimately contains fenced code samples of its own (` ```python ` inside `<execution_phase>`). `_XML_FENCE_RE` cannot nest, so the body was closed at the first inner fence, `_extract_unclosed_tail` saw the truncated opener, and the turn was rejected as `XML_STRICT_REJECT_FENCE_FALLBACK`. The bridge then replaced the answer with the reject header plus the first 2000 chars, withholding the remaining ~25k chars, and the Hands had to re-prompt for a full re-emit — one wasted turn and ~10k output tokens per occurrence. Reproduced offline: a fenced block with one inner ` ```python ` yields zero blocks.
+- **Decision:** Extraction walks line-anchored ` ```xml ` openers in document order (`_XML_FENCE_OPEN_RE`, anchored and info-string-checked so ````quad```` and non-xml fences stay out). For each opener it first tries the existing non-nesting fence body; when that body holds no complete allowlisted block, it scans forward from the opener — bounded by the next opener — for the block's closing tag. The rescue only runs where the old code raised, and a genuinely truncated block still finds nothing and still raises `XML_STRICT_REJECT_FENCE_FALLBACK`.
+- **Consequences:** Nested fences no longer cost a turn, and multi-fence answers stay ordered and bounded per opener. The strict gate keeps its guarantee: input is still never repaired — an incomplete block is rejected, not closed. Trade-off: inside a fence whose body was truncated, a later allowlisted block before the next opener would also be extracted, which is acceptable because that path previously produced no output at all. Pinned by `test_extract_xml_fenced_hands_block_with_inner_code_fences`, `test_extract_rescued_fences_stay_ordered_and_bounded`, and `test_extract_truncated_xml_fence_still_rejects`.
+- **Follow-up (same day), the mirror-image defect:** the bare-block scan ran on `_strip_fences` output, whose non-nesting strip mis-slices the same nested body. The leftover fragment reads as bare prose, so an operator-shaped literal parked in a documentation sample (`sample = "<hotfix>not real</hotfix>"` inside a ` ```python ` block) was returned as a live instruction while the real block was dropped — a false positive, worse than the false negative above. The bare scan now runs on `_mask_fenced_code`, a line-accurate CommonMark-style mask (opener with info string through the next bare run of the same character and length). `_strip_fences` is still called for its diagnostics only. Pinned by `test_extract_ignores_operator_tag_in_nested_fence_sample`.
+- **Fence recognition is now line based, not regex:** `_xml_fence_segments` walks lines and closes a fence only on a bare run of the same character at least as long as the opener. That makes a four-backtick ````xml fence work as the canonical wrapper for a body carrying three-backtick samples, so the safe shape the prompts now recommend is actually extracted, and a three-backtick body that closes early is repaired by the rescue scan. The rescue and the fence-body pass both use `_extract_complete_blocks`, which anchors openers at line starts so a literal inside a code sample cannot win. Supersedes the old `test_extract_quad_xml_fence_stays_ignored` pin (quad fences with the `xml` info string now extract; a quad fence without it stays documentation).
+- **Rollback:** Restore the single `_XML_FENCE_RE.finditer` loop in `extract_xml_blocks` and drop the three tests; fenced answers with inner code fences go back to costing a re-emit.
+
 ## [2026-10-22] ADR-007: Provider deadline tunable above the proxy hop
 
 - **Context:** Big `xhigh`/`max` turns died as `provider overall deadline hit (500.0s) ... RemoteProtocolError: Server disconnected without sending a response`. Three stacked ceilings existed; the tightest won: zen-proxy `urlopen(timeout=300)`, bridge `_OVERALL_DEADLINE_S = 500`, httpx read timeout 600, MCP client 600s. A deep `gpt-6-luna` turn spends 14-19K reasoning tokens, i.e. 5-10 minutes.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 4b33ac5..796899d 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -204,10 +204,20 @@ _XML_UNCLOSED_RE = re.compile(
 # Explicit ```xml fences hold REAL xml, not documentation — the info string
 # is the author's own language tag. Only this fence type feeds the
 # extraction fallback (Task 215); json/bare/tilde fences stay stripped.
-# Runs to the next closing fence or \Z so an unclosed fence still yields.
-# The (?<!`) guard keeps ````quad```` fences out: without it the pattern
-# would match at offset 1 inside ````xml (reviewer follow-up A1).
-_XML_FENCE_RE = re.compile(r"(?<!`)```xml[^\S\n]*\n([\s\S]*?)(?:```|\Z)", re.IGNORECASE)
+# Line based, not a regex: CommonMark closes a fence only with a bare run of
+# at least the opener's length, so a four-backtick ````xml body may safely
+# contain three-backtick samples (the canonical way to wrap a Hands XML block
+# that carries code), and a three-backtick body is closed by the first inner
+# bare run — the case the rescue pass below repairs.
+_XML_FENCE_OPEN_RE = re.compile(r"^[ \t]*(`{3,})xml[ \t]*$", re.IGNORECASE)
+_FENCE_BARE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})[ \t]*$")
+# Line-start allowlisted opener, used by the rescue scan. Anchoring matters:
+# a literal ``<hotfix>`` inside a code sample sits mid-line, so the rescue
+# picks the real control block instead of the sample.
+_XML_START_RE = re.compile(
+    r"(?m)^[ \t]*<(" + "|".join(XML_BLOCK_TAGS) + r")(?:\s[^>]*)?>",
+    re.IGNORECASE,
+)
 # Fenced code blocks are documentation, not instructions — strip them
 # before scanning, or a pasted XML example would false-positive.
 # Covers ``` fences (any length 3+, closed OR unclosed to EOF) and
@@ -239,6 +249,173 @@ def _strip_fences(text: str) -> tuple[str, list[str]]:
     return clean, dropped
 
 
+# Line-accurate fence recognition for the bare-block scan. `_strip_fences`
+# removes spans with a non-nesting regex, so a fenced body that carries its
+# own fenced samples is sliced mid-body and the leftover fragment reads like
+# bare prose — an operator-shaped tag parked in a documentation sample then
+# extracted as a real instruction. This scanner only drops what CommonMark
+# treats as a fence: an opener line (run of 3+ backticks or tildes with an
+# optional info string) through the next bare run of at least the same
+# character and length.
+_FENCE_OPEN_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
+
+
+def _mask_fenced_code(text: str) -> str:
+    """Return the text with every fenced code block dropped, line-accurately.
+
+    Only used to decide whether a *bare* (unfenced) control block exists, so
+    dropping the masked lines instead of replacing them is fine: the caller
+    re-scans the result and needs no offsets.
+    """
+    kept: list[str] = []
+    fence_char = ""
+    fence_len = 0
+    for line in text.splitlines():
+        if fence_char:
+            stripped = line.strip()
+            if (
+                stripped
+                and set(stripped) == {fence_char}
+                and len(stripped) >= fence_len
+            ):
+                fence_char = ""
+                fence_len = 0
+            continue
+        opener = _FENCE_OPEN_RE.match(line)
+        if opener:
+            run = opener.group(1)
+            fence_char = run[0]
+            fence_len = len(run)
+            continue
+        kept.append(line)
+    return "\n".join(kept)
+
+
+def _xml_fence_segments(output: str) -> list[tuple[int, int, int, str]]:
+    """Locate every ```xml fence and return its slices, in document order.
+
+    Line based on purpose: a fence closes only on a bare run of the same
+    character at least as long as the opener, which is what lets a
+    four-backtick ``xml fence carry three-backtick code samples. A
+    three-backtick body that contains its own bare fence closes early, which
+    the caller repairs with the forward rescue scan.
+
+    Returns:
+        ``(opener_start, body_start, body_end, body)`` per fence, where the
+        offsets index ``output`` and ``body`` is the fenced text itself. An
+        unclosed fence yields a body that runs to EOF.
+    """
+    lines = output.splitlines(keepends=True)
+    offsets: list[int] = []
+    cursor = 0
+    for line in lines:
+        offsets.append(cursor)
+        cursor += len(line)
+
+    segments: list[tuple[int, int, int, str]] = []
+    index = 0
+    while index < len(lines):
+        opener = _XML_FENCE_OPEN_RE.match(lines[index].rstrip("\r\n"))
+        if not opener:
+            index += 1
+            continue
+        run = len(opener.group(1))
+        scan = index + 1
+        while scan < len(lines):
+            closer = _FENCE_BARE_RE.match(lines[scan].rstrip("\r\n"))
+            if closer and closer.group(1)[0] == "`" and len(closer.group(1)) >= run:
+                break
+            scan += 1
+        if scan < len(lines):
+            body_end = offsets[scan]
+            body = "".join(lines[index + 1 : scan])
+            next_index = scan + 1
+        else:
+            body_end = len(output)
+            body = "".join(lines[index + 1 :])
+            next_index = len(lines)
+        segments.append(
+            (offsets[index], offsets[index] + len(lines[index]), body_end, body)
+        )
+        index = next_index
+    return segments
+
+
+def _rescue_fenced_block(fragment: str) -> list[str]:
+    """Recover the block a truncated fence body was wrapping.
+
+    A three-backtick fence whose body carries its own fenced samples is closed
+    early, so the complete block lives past the body. Take the first
+    line-start allowlisted opener in the fragment and the first matching close
+    tag after it. Line-start anchoring keeps operator-shaped literals inside
+    code samples from winning the race.
+
+    Args:
+        fragment: Raw text from the fence opener to the next opener or EOF.
+
+    Returns:
+        A one-item list with the recovered block, or an empty list when no
+        complete block exists (a genuinely truncated turn still rejects).
+    """
+    opener = _XML_START_RE.search(fragment)
+    if not opener:
+        return []
+    return _extract_complete_blocks(fragment)[:1]
+
+
+def _bare_blocks(text: str) -> list[str]:
+    """Return bare blocks, skipping literals quoted inside an inline code span.
+
+    The bare path tolerates a control block that starts mid-line (pinned by
+    ``test_extract_multiple_blocks_in_order``). That tolerance also made a
+    *quoted* sample extract as an instruction: a QA reply containing
+    ``sample = "<hotfix>…</hotfix>"`` came back as ``XML_EXTRACTED`` with the
+    fragment as its block. An odd number of backticks earlier on the same line
+    means the match sits inside an inline code span, so it is prose, not an
+    instruction; fenced code never reaches here (it is masked out first).
+    """
+    blocks: list[str] = []
+    for match in _XML_RE.finditer(text):
+        line_start = text.rfind("\n", 0, match.start()) + 1
+        if text[line_start : match.start()].count("`") % 2 == 1:
+            continue
+        blocks.append(match.group(0))
+    return blocks
+
+
+def _extract_complete_blocks(text: str) -> list[str]:
+    """Return complete allowlisted blocks whose opener starts a line.
+
+    The fence path uses this instead of the mid-line tolerant ``_XML_RE``
+    because a fenced body can hold code samples that mention an operator tag
+    as a literal (``sample = "<hotfix>…</hotfix>"``): line-start anchoring
+    keeps those samples out while every real block still matches, since the
+    templates always start the root element at a line start.
+
+    Args:
+        text: A fence body or a forward rescue fragment.
+
+    Returns:
+        Verbatim blocks in document order.
+    """
+    blocks: list[str] = []
+    cursor = 0
+    while True:
+        opener = _XML_START_RE.search(text, cursor)
+        if not opener:
+            return blocks
+        tag = opener.group(1)
+        closer = re.search(
+            rf"</\s*{re.escape(tag)}\s*>", text[opener.end() :], re.IGNORECASE
+        )
+        if not closer:
+            cursor = opener.end()
+            continue
+        end = opener.end() + closer.end()
+        blocks.append(text[opener.start() : end])
+        cursor = end
+
+
 # Task ids become directory names. Strict allowlist: anything else
 # (``..``, separators, empty) raises instead of being mangled.
 _TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
@@ -904,27 +1081,44 @@ def extract_xml_blocks(output: str) -> list[str]:
             STRICT_XML_CONTRACT_CODE,
             f"expected str input, got {type(output).__name__}",
         )
-    clean, _ = _strip_fences(output)
-    blocks = [m.group(0) for m in _XML_RE.finditer(clean)]
+    _strip_fences(output)  # diagnostics only: populates _last_fence_drops
+    # The bare scan runs on the line-accurate mask, never on the regex strip:
+    # the strip mis-slices nested fences and would let a documentation sample
+    # extract as a real block.
+    clean = _mask_fenced_code(output)
+    blocks = _bare_blocks(clean)
     if blocks:
         return blocks
     tail = _extract_unclosed_tail(clean)
     if tail:
         _strict_reject(
             STRICT_XML_UNCLOSED_CODE,
-            "unclosed trailing block: re-emit bare unfenced XML",
+            "unclosed trailing block: re-emit the complete block bare or inside a four-backtick ```xml fence",
         )
     fence_blocks: list[str] = []
-    for body in _XML_FENCE_RE.finditer(output):
-        content = body.group(1)
-        fence_blocks.extend(m.group(0) for m in _XML_RE.finditer(content))
+    segments = _xml_fence_segments(output)
+    for index, (opener_start, body_start, body_end, body) in enumerate(segments):
+        found = _extract_complete_blocks(body)
+        if not found:
+            # Rescue: a three-backtick fence cannot hold a body with its own
+            # fenced samples (the inner bare run closes it), so the complete
+            # block sits past the truncated body and the turn used to be
+            # rejected outright (whole answer withheld, forcing a costly full
+            # re-emit). Look forward from the opener, bounded by the next one;
+            # a genuinely truncated block finds nothing and still falls
+            # through to the strict reject.
+            scan_end = (
+                segments[index + 1][0] if index + 1 < len(segments) else len(output)
+            )
+            found = _rescue_fenced_block(output[opener_start:scan_end])
+        fence_blocks.extend(found)
     if fence_blocks:
         return fence_blocks
-    for body in _XML_FENCE_RE.finditer(output):
-        if _extract_unclosed_tail(body.group(1)):
+    for _opener_start, _body_start, _body_end, body in segments:
+        if _extract_unclosed_tail(body):
             _strict_reject(
                 STRICT_XML_FENCE_FALLBACK_CODE,
-                "xml-fenced block: re-emit bare unfenced XML",
+                "truncated fenced block: re-emit the complete block bare or inside a four-backtick ```xml fence",
             )
     return []
 
@@ -1730,13 +1924,12 @@ def _overall_deadline_s() -> float:
     try:
         val = float(raw)
     except ValueError:
-        raise RuntimeError(
-            f"BRAIN_OVERALL_DEADLINE_S must be a number, got {raw!r}"
-        )
+        raise RuntimeError(f"BRAIN_OVERALL_DEADLINE_S must be a number, got {raw!r}")
     if val <= 0:
         raise RuntimeError(f"BRAIN_OVERALL_DEADLINE_S must be > 0, got {raw!r}")
     return val
 
+
 #: Billing/spend/quota 429 codes that must NEVER be retried (Task 329
 #: F6, per the official error-codes guide): "Retrying billing, spend, or
 #: quota errors won't restore API access." These fail terminal with an
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index c0e04e4..42c1ed6 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.64.0</system_version>
+<system_version>9.64.1</system_version>
\ No newline at end of file
diff --git a/prompts/fragments/02-role.md b/prompts/fragments/02-role.md
index 6b0819b..8ac44ed 100644
--- a/prompts/fragments/02-role.md
+++ b/prompts/fragments/02-role.md
@@ -4,4 +4,4 @@ You coordinate with the human user (The Manager) and generate highly structured,
 You DO NOT have direct file-system, terminal, or network access. You communicate exclusively with the Manager via text. Your execution power comes from generating precise tasks that the Manager copies and runs inside the Hands.
 The Hands have parallel agent execution capabilities and can execute up to 4 tasks concurrently across different subagents to accelerate codebase discovery and file generation.
 ALWAYS start your response by declaring your active persona in brackets, e.g., **[Software Architect]**. Immediately after the bracket, open with the answer or the result, never with process narration.
-</role>
+</role>
\ No newline at end of file
diff --git a/prompts/fragments/05-user_input_processing.md b/prompts/fragments/05-user_input_processing.md
index 2685c29..880fe4c 100644
--- a/prompts/fragments/05-user_input_processing.md
+++ b/prompts/fragments/05-user_input_processing.md
@@ -29,4 +29,4 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
     - **If eligible:** Proceed directly to Step 5 (Implementation) of the `<execution_workflow>`. Document the Lite Mode justification in the task file.
     - **If NOT eligible or uncertain:** Proceed to Step 1 (Smart Context Discovery).
 5.5. **Prompt Refactor Gate:** For any input that will result in an implementation task, the Orchestrator MUST apply its internal intent-shaping steps of validate, translate, expand, and structure. The Orchestrator (Brain) has no skill tool and never loads skills; only Hands (cognitive-executor) loads the full prompt-refactor skill via the skill tool when a task names it, per the Skill Auto-Loading Matrix which binds Hands only.
-</user_input_processing>
+</user_input_processing>
\ No newline at end of file
diff --git a/prompts/fragments/06-personas.md b/prompts/fragments/06-personas.md
index eb4baca..42867f9 100644
--- a/prompts/fragments/06-personas.md
+++ b/prompts/fragments/06-personas.md
@@ -14,7 +14,7 @@
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. The bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. If the body itself contains fenced code samples, open the wrapper with four backticks (````xml) so the inner fences cannot close it; the bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
     You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit todo-list (micro-list) units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
 </persona>
 
@@ -47,13 +47,13 @@
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. In manual mode the Manager ferries task files between the Hands and the Brain by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Automatic-mode override:** when MODE is automatic, chain the next `brain_turn` yourself under the same `task_id` (re-QA after fixes, then Reviewer) and never ask the Manager to ferry files or emit copy/paste handoffs. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. In manual mode the Manager ferries task files between the Hands and the Brain by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Automatic-mode override:** when MODE is automatic, chain the next `brain_turn` yourself under the same `task_id` (re-QA after fixes, then Reviewer) and never ask the Manager to ferry files or emit copy/paste handoffs. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Manager pastes the Hands' completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** when MODE is automatic, chain the fix/review `brain_turn` calls yourself and never ask the Manager to ferry files; the technical approval still relays to the Manager for the explicit closure word.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** when MODE is automatic, chain the fix/review `brain_turn` calls yourself and never ask the Manager to ferry files; the technical approval still relays to the Manager for the explicit closure word.</behavior>
 </persona>
 
 <auto_load>
@@ -61,4 +61,4 @@ Layer 1 — explicit mention wins. If the Manager names a persona (exact name or
 Layer 2 — threshold inference. If nobody is named, infer from the Manager's message plus conversation history and current machine state. High confidence means the message maps to exactly one persona's trigger or duty with no rival. Then load it, declare it in the existing bracket label, and proceed. The label makes the choice visible and correctable. Low confidence means two or more personas fit, or none fits clearly. Then do NOT guess. Stop and ask the Manager which persona to load. Guessing an identity is a hallucination risk. One question costs less than a wrong persona.
 No new label. The bracket declaration in 02-role stays the single speaker display. Never add a second Speaking-as line.
 </auto_load>
-</personas>
+</personas>
\ No newline at end of file
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index 9841a56..e95023d 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -43,4 +43,4 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
-  </agent_skills_registry>
+</agent_skills_registry>
\ No newline at end of file
diff --git a/prompts/fragments/09-hands_protocols.md b/prompts/fragments/09-hands_protocols.md
index 8395ff7..209dd78 100644
--- a/prompts/fragments/09-hands_protocols.md
+++ b/prompts/fragments/09-hands_protocols.md
@@ -165,4 +165,4 @@
 
 </hands_combined_task_template>
 
-</hands_protocols>
+</hands_protocols>
\ No newline at end of file
diff --git a/prompts/fragments/11-execution_workflow.md b/prompts/fragments/11-execution_workflow.md
index 2ea58d8..d5de596 100644
--- a/prompts/fragments/11-execution_workflow.md
+++ b/prompts/fragments/11-execution_workflow.md
@@ -43,4 +43,4 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
    - Sprint Strategist verifies backlog priority and immediately initiates Step 1 on the next sprint candidate.
 
 **Night mode override.** When the Manager hands over the night ("night mode", "100% autopilot until morning"), `<night_mode>` governs: the Step 6 QA gate, the Step 7 review gate, and the Step 8 closure approval are pre-authorized and played by the Hands, and the question tool is not used until he returns. Every other step in this pipeline is unchanged.
-</execution_workflow>
+</execution_workflow>
\ No newline at end of file
diff --git a/prompts/fragments/12-brainstorming_protocol.md b/prompts/fragments/12-brainstorming_protocol.md
index 34334ef..b18faaf 100644
--- a/prompts/fragments/12-brainstorming_protocol.md
+++ b/prompts/fragments/12-brainstorming_protocol.md
@@ -6,4 +6,4 @@
 <procedure>Run seats sequentially. Each seat analyzes independently from its duty only. No seat may soften another seat's finding. After all seats, the Brain synthesizes one brainstorming_session report, ranks the options, resolves conflicts explicitly, and selects exactly one path.</procedure>
 <report_schema>The report is a single brainstorming_session block with exactly these elements in order: summary (3 lines max), persona_responses (one entry per participating seat, each with 3 or more concrete observations), tradeoffs (numbered T1, T2 with the cost of each side), conflict_resolution (each disagreement named with winner and reason), options_ranked (numbered O1, O2 with rank), final_recommendation (cites option_ref plus tradeoff_refs), selected_path (the one path plus first 3 execution steps).</report_schema>
 <selection_rule>The final plan MUST cite the report to justify the choice: winning option id, deciding tradeoff ids, and why losers lost. Never pick a path the report did not rank. The report travels with the task: paste the full block into the backlog task file as the selection reference. Hands interpret it as non-functional guidelines that inform but never override task instructions.</selection_rule>
-</brainstorming_protocol>
+</brainstorming_protocol>
\ No newline at end of file
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 7a0a603..8b26d7a 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -40,4 +40,4 @@ When writing or reviewing bash scripts, cron jobs, or container orchestration co
 3. **No Post-Redirect Status Checks:** Never use `command > file; if [ $? -eq 0 ]` because the shell creates the file before running the command, masking command failures.
 4. **Sidecar Isolation for Hostless Backups:** Never rely on host file staging for Docker volume backups. Always utilize lightweight ephemeral containers (`docker run --rm -v volume:/data:ro alpine tar...`) with read-only mounts.
 </defensive_shell_protocol>
-</constraints>
+</constraints>
\ No newline at end of file
diff --git a/prompts/fragments/20-communication_examples.md b/prompts/fragments/20-communication_examples.md
index 216bad7..a901711 100644
--- a/prompts/fragments/20-communication_examples.md
+++ b/prompts/fragments/20-communication_examples.md
@@ -37,4 +37,4 @@ The final handoff language follows the per-message request; everything else on t
 
 - _DO:_ Non-English sentence naming `tasks/qa/example.md` and `lint_task_file` with both terms intact in backticks.
 - _DO NOT:_ Transliterate either term into non-English script.
-</communication_examples>
+</communication_examples>
\ No newline at end of file
diff --git a/prompts/fragments/21-self_improvement_protocol.md b/prompts/fragments/21-self_improvement_protocol.md
index 33139f1..3ec82ad 100644
--- a/prompts/fragments/21-self_improvement_protocol.md
+++ b/prompts/fragments/21-self_improvement_protocol.md
@@ -73,4 +73,4 @@ Title: `[sensor:{downstream-project}] {fingerprint} {short finding}`. Body MUST
 
 Downstream Hands gets issue-create only. Never request HQ write access; broad token scopes are forbidden. `gh` auth stays local to the downstream project.
 
-</self_improvement_protocol>
+</self_improvement_protocol>
\ No newline at end of file
diff --git a/prompts/fragments/23-night_mode.md b/prompts/fragments/23-night_mode.md
index e7710f6..c52377d 100644
--- a/prompts/fragments/23-night_mode.md
+++ b/prompts/fragments/23-night_mode.md
@@ -35,4 +35,4 @@
 3. What needs the Manager: a short numbered list of checks only he can perform, credentials, or production parameters.
 4. Flags: anything left in a non-production state (staging values, temporary overrides, untracked files).
 5. Honest notes: disputes, extra commits, workarounds, and anything you could not verify.
-</night_mode>
+</night_mode>
\ No newline at end of file
diff --git a/prompts/fragments/24-language_policy.md b/prompts/fragments/24-language_policy.md
index 5f237ab..e16101c 100644
--- a/prompts/fragments/24-language_policy.md
+++ b/prompts/fragments/24-language_policy.md
@@ -42,4 +42,4 @@ Plan gate accepts approved in any case through the question tool path. Closure a
 
 ## Execution Binding
 
-Translate first, then validate intent, expand requirements, check brainstorming, check clarification, check Lite Mode, and generate implementation tasks from the English version. Clarification questions use the per-message requested language. Implementation XML, tests, and evidence stay English.
+Translate first, then validate intent, expand requirements, check brainstorming, check clarification, check Lite Mode, and generate implementation tasks from the English version. Clarification questions use the per-message requested language. Implementation XML, tests, and evidence stay English.
\ No newline at end of file
diff --git a/scripts/DECISIONS.md b/scripts/DECISIONS.md
index 6c292aa..21f67d2 100644
--- a/scripts/DECISIONS.md
+++ b/scripts/DECISIONS.md
@@ -1,5 +1,12 @@
 # Architectural Decisions: scripts
 
+## [2026-10-24] ADR-002: Prompt split covers `night_mode` and the trailing Markdown section
+
+- **Context:** `system-prompt.md` is a generated artifact, but `split_system_prompt.py` still knew 20 top-level tags. The prompt had since gained `<night_mode>` (tag 23) and a plain-Markdown language-policy section after the last tag, so rebuilding from fragments dropped both: the round-trip test in `tests/test_mcp_servers.py` failed with `<night_mode>` missing from the assembled output. Rebuilding also renumbered every fragment, renaming ~20 tracked files for no content change.
+- **Decision:** `night_mode` joins `TOP_LEVEL_TAGS` in document order, and the trailing non-tag section is captured as a final fragment whose name comes from its first heading (`language_policy`). Filenames already present in an existing manifest are reused by their tag/slug instead of being renumbered, so a rebuild is idempotent on disk and the manifest keeps its committed names (`23-night_mode.md`, `24-language_policy.md`).
+- **Consequences:** `assemble(split(system-prompt.md))` is byte-identical again (108,394 bytes at the time of the fix), a rebuild no longer silently drops a policy block, and fragment names stay stable across runs. The tail fragment has no XML tag, so the splitter now depends on the file ending with a Markdown section; adding text after it is captured, while text inserted between tagged blocks still requires a tag.
+- **Rollback:** Drop the tail-capture block and the `night_mode` entry, and restore per-tag numbering; the round-trip test goes back to failing.
+
 ## [2026-10-06] ADR-001: Initial Slice Baseline
 
 - **Context:** Baseline documentation initialized via init-folder-docs.
diff --git a/scripts/prompt-build/split_system_prompt.py b/scripts/prompt-build/split_system_prompt.py
index 152cd05..e19c532 100644
--- a/scripts/prompt-build/split_system_prompt.py
+++ b/scripts/prompt-build/split_system_prompt.py
@@ -59,12 +59,14 @@ from typing import List, Tuple
 # Configuration
 # ---------------------------------------------------------------------------
 
-# The 20 top-level XML tags in system-prompt.md, in document order.
+# The 21 top-level XML tags in system-prompt.md, in document order.
 # This explicit ordered list is the authoritative contract for the split: the
-# script verifies that these (and only these) 20 tags appear at the top level,
+# script verifies that these (and only these) 21 tags appear at the top level,
 # in this exact order. Nested tags (e.g. <phase>/<workflow>/<personas> inside
 # <brainstorming_protocol>) are part of their parent block's content and are
-# NOT split out separately.
+# NOT split out separately. Text after the last tag (the Markdown language
+# policy) is captured as a final tail fragment so the round trip stays
+# byte-identical.
 TOP_LEVEL_TAGS: List[str] = [
     "system_version",
     "role",
@@ -86,6 +88,7 @@ TOP_LEVEL_TAGS: List[str] = [
     "initialization",
     "communication_examples",
     "self_improvement_protocol",
+    "night_mode",
 ]
 
 # Regex patterns for locating top-level tag boundaries.
@@ -270,6 +273,26 @@ def _extract_and_verify_validation_phases(
 # ---------------------------------------------------------------------------
 
 
+def _slugify_heading(line: str) -> str:
+    """Turn a Markdown heading into a snake_case fragment slug.
+
+    Only used for the trailing Markdown section, which has no tag name to
+    borrow. The heading's leading ``#`` and any subtitle after ``:`` are
+    dropped, and only the first three words survive, so the slug stays short
+    and stable (``# Language Policy: English Inside…`` -> ``language_policy``).
+
+    Args:
+        line: The first non-empty line of the tail section.
+
+    Returns:
+        A lowercase snake_case slug, or ``"tail"`` when nothing survives.
+    """
+    text = line.lstrip("#").split(":", 1)[0]
+    words = [re.sub(r"[^a-z0-9]+", "", word.lower()) for word in text.split()]
+    words = [word for word in words if word][:3]
+    return "_".join(words) or "tail"
+
+
 def split_system_prompt(
     source_path: str = "system-prompt.md",
     fragments_dir: str = "prompts/fragments",
@@ -311,6 +334,27 @@ def split_system_prompt(
     Path(shared_dir).mkdir(parents=True, exist_ok=True)
     Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)
 
+    # Reuse filenames already listed in an existing manifest, matched by the
+    # part after the numeric prefix ("23-night_mode.md" -> "night_mode"), so a
+    # rebuild does not renumber and rename every fragment on disk.
+    existing_names: dict[str, str] = {}
+    manifest_file = Path(manifest_path)
+    if manifest_file.is_file():
+        for entry in manifest_file.read_text(encoding="utf-8").splitlines():
+            entry = entry.strip()
+            if entry.endswith(".md") and "-" in entry:
+                existing_names.setdefault(entry[:-3].split("-", 1)[1], entry)
+
+    # Trailing Markdown after the last tagged block (the language policy) has
+    # no tag of its own; capture it as a final fragment so a rebuild does not
+    # silently drop the whole section.
+    tail_lines = lines[ranges[-1][2] + 1 :]
+    while tail_lines and not tail_lines[0].strip():
+        tail_lines.pop(0)
+    while tail_lines and not tail_lines[-1].strip():
+        tail_lines.pop()
+    has_tail = bool(tail_lines)
+
     for seq, (tag, start, end) in enumerate(ranges, start=1):
         block_text = "\n".join(lines[start : end + 1])
 
@@ -332,13 +376,24 @@ def split_system_prompt(
         # '\n' so the assembler's single '\n' produces the correct '\n\n'
         # termination.
         seq_str = str(seq).zfill(2)
-        filename = f"{seq_str}-{tag}.md"
+        filename = existing_names.get(tag) or f"{seq_str}-{tag}.md"
         write_text = block_text
-        if seq == len(ranges) and content.endswith("\n\n"):
+        if seq == len(ranges) and not has_tail and content.endswith("\n\n"):
             write_text = block_text + "\n"
         (frag_dir / filename).write_text(write_text, encoding="utf-8")
         fragment_filenames.append(filename)
 
+    # --- 2b. The trailing Markdown fragment ---
+    if has_tail:
+        slug = _slugify_heading(tail_lines[0])
+        seq_str = str(len(fragment_filenames) + 1).zfill(2)
+        filename = existing_names.get(slug) or f"{seq_str}-{slug}.md"
+        tail_text = "\n".join(tail_lines)
+        if content.endswith("\n\n"):
+            tail_text += "\n"
+        (frag_dir / filename).write_text(tail_text, encoding="utf-8")
+        fragment_filenames.append(filename)
+
     # --- 3. Emit the manifest (one filename per line, assembly order) ---
     Path(manifest_path).write_text(
         "\n".join(fragment_filenames) + "\n", encoding="utf-8"
diff --git a/system-prompt.md b/system-prompt.md
index 029d566..49bed81 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.64.0</system_version>
+<system_version>9.64.1</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -66,7 +66,7 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="Senior Programmer">
     <trigger>Approved blueprints/designs or explicit Manager requests.</trigger>
     <duty>Technical implementation lead and "Hands Whisperer" (chief orchestrator of the local execution agent).</duty>
-    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. The bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
+    <behavior>Adopt the coding style defined in the project's local Agent Skills or `AGENTS.md`. **Anti-Hack Directive:** If a bug fix requires bypassing framework standards, creating fragile race-condition masks (e.g., arbitrary `setTimeout`), or dirty hacks, you MUST STOP. Explain the technical debt to the Manager and propose a clean, architectural refactor. You write strict, comprehensive instructions formatted as a `<hands_implementation_task>` for the local Hands agent to execute. You MUST instruct the Hands to read AGENTS.md as their very first step, which acts as a router directing the agent to read DESIGN.md, architecture.md, data_model.md, and conventions.md before implementing changes. If the Manager provides a new standalone constraint or project quirk in the chat, you MUST proactively instruct the Hands to load the `project-memory` skill and save the rule. You do NOT execute code yourself. You produce the plan and the checklist; how the Hands tracks and executes them is defined solely in the context executor. If the Hands halt and return a RULE VIOLATION WARNING, you MUST acknowledge the mistake, self-correct your logic based on the project's rules, and generate a flawless revised implementation task. In manual MODE wrap the task in a ```xml fenced block for one-click copy-paste (fence forced); in automatic MODE emit it as bare unfenced raw XML with no fences. If the body itself contains fenced code samples, open the wrapper with four backticks (````xml) so the inner fences cannot close it; the bridge extracts both shapes. Instruct the Hands to leverage their native tools (language servers, `grep`, web search, `skill`, MCP servers, and codebase-exploration subagents) to gain context autonomously.
     You MUST explicitly orchestrate skills and micro-tasks. In the task template, you MUST list exactly WHICH skills the Hands must load, and explain HOW and WHY to use them. Furthermore, you MUST break the implementation down into a strict `- [ ] **Step N:**` checklist. Treat the Hands as an execution engine that will hallucinate if not micro-managed. Ownership boundary: the Architect owns the WHAT (blueprint plus which skills it needs) — you own the HOW (task XML, step checklists, orchestration). **Goal-Oriented Task Mandate:** Multi-phase or large tasks MUST be structured as explicit todo-list (micro-list) units with loaded stack/workflow skills. Before issuing any multi-step task, you MUST instruct the Hands to load all relevant skills from `<agent_skills_registry>` and define explicit verification gates (tests, lints, compilation checks) for each phase. **Multi-Phase Task Rule:** If a task requires more than 2 sequential implementation phases, generate a SINGLE multi-phase task file with inline `## Phase 1:`, `## Phase 2:`, etc. sections, each containing its own checklist and diff block. Do NOT create separate task files (e.g., 608a, 608b, 608c) for phases of the same task.</behavior>
 </persona>
 
@@ -99,13 +99,13 @@ CRITICAL INSTRUCTION: The Manager may send informal, raw text. Before taking any
   <persona name="QA Engineer">
     <trigger>Implementation phase is complete, or explicit Manager request for testing.</trigger>
     <duty>Adversarial testing, boundary analysis, fuzzing, and stability enforcement.</duty>
-    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. In manual mode the Manager ferries task files between the Hands and the Brain by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Automatic-mode override:** when MODE is automatic, chain the next `brain_turn` yourself under the same `task_id` (re-QA after fixes, then Reviewer) and never ask the Manager to ferry files or emit copy/paste handoffs. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
+    <behavior>Adopt a strictly adversarial mindset. Your goal is to break the Senior Programmer's implementation. Read the "Factual Git Diff" in the active task file. Look for missing null checks, race conditions, unchecked inputs, and missing negative test cases. Do NOT check for formatting or architecture. Output a strict report: Vulnerabilities, Missing Tests, Status (QA_PASSED or QA_REJECTED). If QA_REJECTED, do NOT stop at the verdict. In manual mode the Manager ferries task files between the Hands and the Brain by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what failed, what the fix covers, where to paste it), then a hotfix `<hands_implementation_task>` XML scoped ONLY to the failing points — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs QA. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If QA_PASSED, instruct the Manager to hand over to the Code Reviewer. **Automatic-mode override:** when MODE is automatic, chain the next `brain_turn` yourself under the same `task_id` (re-QA after fixes, then Reviewer) and never ask the Manager to ferry files or emit copy/paste handoffs. **Machine-Readable Verdict Mandate:** End EVERY QA report with a machine verdict block the autopilot parses with a single regex — first line exactly `VERDICT: QA_PASSED` or `VERDICT: QA_REJECTED`, then one `CITE: file:line` line per cited location (e.g. `CITE: mcp-context-server/server.py:123`). The prose report stays for humans; the verdict block drives automation. **Escape hatch:** If a reply carries no parseable VERDICT line, the autopilot treats it as QA_REJECTED with reason "unparseable verdict" and falls back to the prose report; the Manager may override any machine verdict by explicit order.</behavior>
 </persona>
 
   <persona name="Code Reviewer">
     <trigger>Manager pastes the Hands' completed Task Summary, PRs are submitted, or Manager requests.</trigger>
     <duty>Audit the Hands' completed work against the Architect's blueprint, the Designer's UI specs, and the project's conventions.</duty>
-    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** when MODE is automatic, chain the fix/review `brain_turn` calls yourself and never ask the Manager to ferry files; the technical approval still relays to the Manager for the explicit closure word.</behavior>
+    <behavior>Read the "Execution Log" to understand the agent's logic, but base your strict review ONLY on the "Factual Git Diff" block inside the task file. Provide rigorous formatting: Strengths, Issues, Severity, Recommendations. Output status: APPROVED, APPROVED_WITH_CHANGES, or REJECTED_NEEDS_FIXES. On REJECTED_NEEDS_FIXES or APPROVED_WITH_CHANGES, do NOT stop at the verdict. In manual mode the Manager ferries task files by hand; in autopilot the Hands calls the Brain directly. Either way, always emit the next step yourself: first a 3-line Manager summary (what must change, what the fix covers, where to paste it), then a postfix `<hands_implementation_task>` XML scoped ONLY to the required changes — fenced ```xml in manual MODE (use a four-backtick ````xml wrapper when the body carries its own fenced code samples; fence forced for copy-paste), bare unfenced with no fences in automatic MODE — instructing the Hands to fix within the EXISTING task file — never a new task number. The Manager copies it to the Hands, brings the result back, and re-runs the Reviewer. If the SAME task is rejected a 3rd time, stop emitting fix XML and escalate to the Manager with options instead. If APPROVED technically, output status as PO_REVIEW_PENDING. Do NOT commit or close the task. Instruct the Manager: "Code approved technically. PO, please review UX/Business logic. Reply 'Approved for closure' to commit and finish." Only the exact phrases "Approved for closure" or "Close task" (case-insensitive, nothing else) count as the approval word. A bare "approved" counts only when it is the Manager's next message directly answering the relayed closure question; anywhere else it never counts. These never count: "good", "thanks", "ok", "okay", "yes", "done", "fine", "looks good", emoji-only replies, and silence — nor does any autopilot self-decision. When the Manager replies with the exact keyword "Approved for closure" or "Close task", the Hands re-calls the Brain once as Senior Programmer for a single final-closure XML (move the file to `tasks/completed/` with `git mv`, then strictly execute the `custom_context_commit_and_clean_task` MCP tool without alternative options) and executes that XML exactly once — the Reviewer never emits the closure XML itself. **Automatic-mode override:** when MODE is automatic, chain the fix/review `brain_turn` calls yourself and never ask the Manager to ferry files; the technical approval still relays to the Manager for the explicit closure word.</behavior>
 </persona>
 
 <auto_load>
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 07a5914..5a3e544 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -2155,6 +2155,132 @@ def test_extract_unfenced_wins_over_fenced_xml():
 # --- Task 215 QA follow-ups (A1-A4 + attribute lock) ---
 
 
+def test_extract_xml_fenced_hands_block_with_inner_code_fences():
+    """Regression: nested fences must not cost a whole turn.
+
+    A fenced Hands XML body carries its own ```python samples, so the
+    non-nesting fence pattern closed the body at the first inner fence and
+    the extractor rejected the answer as XML_STRICT_REJECT_FENCE_FALLBACK
+    with the entire block withheld — the Hands then had to re-emit a
+    ~25k-char turn. The rescue pass finds the complete block after the
+    opener instead.
+    """
+    block = (
+        "<hands_implementation_task>\n"
+        "  <validation_phase>read AGENTS.md</validation_phase>\n"
+        "  <context_phase>load skills</context_phase>\n"
+        "  <execution_phase>\n"
+        "    Step 1:\n"
+        "    ```python\n"
+        "    print('hi')\n"
+        "    ```\n"
+        "    Step 2 done.\n"
+        "  </execution_phase>\n"
+        "  <bash_phase>run tests</bash_phase>\n"
+        "  <documentation_phase>changelog</documentation_phase>\n"
+        "  <summary_phase>finalize</summary_phase>\n"
+        "</hands_implementation_task>"
+    )
+    out = "Plan follows.\n\n```xml\n" + block + "\n```\n\ntrailing prose"
+    blocks = bridge.extract_xml_blocks(out)
+    assert blocks == [block]
+
+
+def test_extract_quad_xml_fence_wraps_inner_fences():
+    """Four-backtick xml fence is the canonical wrapper for a body with fences.
+
+    CommonMark closes a fence only on a bare run at least as long as the
+    opener, so the inner triple-backtick samples stay inside the body instead
+    of truncating it.
+    """
+    block = (
+        "<hands_implementation_task>\n"
+        "<validation_phase>a</validation_phase>\n"
+        "<context_phase>b</context_phase>\n"
+        "<execution_phase>\n"
+        "```python\n"
+        "print(1)\n"
+        "```\n"
+        "</execution_phase>\n"
+        "<bash_phase>c</bash_phase>\n"
+        "<documentation_phase>d</documentation_phase>\n"
+        "<summary_phase>e</summary_phase>\n"
+        "</hands_implementation_task>"
+    )
+    blocks = bridge.extract_xml_blocks("````xml\n" + block + "\n````\n")
+    assert blocks == [block]
+    assert bridge.validate_hands_xml_blocks(blocks) == []
+
+
+def test_extract_midline_quoted_hotfix_stays_ignored():
+    """A quoted literal in a report is not an instruction.
+
+    Observed live: a QA reply containing `sample = "<hotfix>…</hotfix>"`
+    returned XML_EXTRACTED with that fragment as the block. Hands blocks keep
+    the mid-line tolerance (pinned), but hotfix/failure_report must start a
+    line like the templates emit them.
+    """
+    out = 'V2 doc-sample leak `sample = "<hotfix>…</hotfix>"` was fixed.'
+    assert bridge.extract_xml_blocks(out) == []
+    # Bare mid-line blocks outside inline code keep their pinned tolerance.
+    assert bridge.extract_xml_blocks(
+        'Think <hands_implementation_task>{"a": 1}</hands_implementation_task> tail'
+    )
+    assert (
+        len(bridge.extract_xml_blocks("note <failure_report>x</failure_report>")) == 1
+    )
+
+
+def test_extract_ignores_operator_tag_in_nested_fence_sample():
+    """A doc sample must never extract, even inside a fenced body.
+
+    Regression: the non-nesting fence strip mis-sliced a nested body and left
+    the sample fragment looking bare, so a `<hotfix>` literal inside a python
+    snippet was returned as an instruction while the real block was dropped.
+    """
+    out = "\n".join(
+        [
+            "```xml",
+            "<hands_implementation_task>",
+            "  <validation_phase>x</validation_phase>",
+            "  <context_phase>y</context_phase>",
+            "  <execution_phase>",
+            "    ```python",
+            '    sample = "<hotfix>not real</hotfix>"',
+            "    ```",
+            "  </execution_phase>",
+            "  <bash_phase>t</bash_phase>",
+            "  <documentation_phase>d</documentation_phase>",
+            "  <summary_phase>s</summary_phase>",
+            "</hands_implementation_task>",
+            "```",
+        ]
+    )
+    blocks = bridge.extract_xml_blocks(out)
+    assert len(blocks) == 1
+    assert blocks[0].startswith("<hands_implementation_task>")
+    assert not any(b.startswith("<hotfix>") for b in blocks)
+
+
+def test_extract_rescued_fences_stay_ordered_and_bounded():
+    # Each opener rescues only its own block; the next opener bounds the scan.
+    first = "```xml\n<hotfix>\n```bash\nls\n```\n</hotfix>\n```"
+    second = "```xml\n<failure_report>second</failure_report>\n```"
+    blocks = bridge.extract_xml_blocks(first + "\ntext\n" + second)
+    assert len(blocks) == 2
+    assert blocks[0].startswith("<hotfix>")
+    assert blocks[1].startswith("<failure_report>")
+
+
+def test_extract_truncated_xml_fence_still_rejects():
+    # The rescue must not launder a genuinely cut-off block.
+    with pytest.raises(ValueError) as excinfo:
+        bridge.extract_xml_blocks(
+            "```xml\n<hands_implementation_task>\n<execution_phase>cut off"
+        )
+    assert str(excinfo.value).startswith(bridge.STRICT_XML_FENCE_FALLBACK_CODE)
+
+
 def test_extract_multiple_xml_fences_in_order():
     # Dual-mode fallback: multiple ```xml fences extract in order.
     blocks = bridge.extract_xml_blocks(
@@ -2204,11 +2330,15 @@ def test_extract_tag_with_attributes_tolerated():
         assert len(blocks) == 1, variant
 
 
-def test_extract_quad_xml_fence_stays_ignored():
-    # Reviewer follow-up A1: without the (?<!`) guard the fence pattern
-    # matched at offset 1 inside ````xml. Quad fences stay documentation.
-    out = "````xml\n<hotfix>x</hotfix>\n````"
-    assert bridge.extract_xml_blocks(out) == []
+def test_extract_quad_xml_fence_extracts():
+    # Superseded the old "quad fences stay documentation" pin: a four-backtick
+    # `xml` fence is the canonical way to wrap a body carrying its own
+    # three-backtick samples, so it must extract. A quad fence WITHOUT the xml
+    # info string is still documentation.
+    assert bridge.extract_xml_blocks("````xml\n<hotfix>x</hotfix>\n````") == [
+        "<hotfix>x</hotfix>"
+    ]
+    assert bridge.extract_xml_blocks("````\n<hotfix>x</hotfix>\n````") == []
 
 
 # --- Task 238 fix loop: tolerance + truncation fallback ---
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index de46c52..17cdb22 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.64.0"
+    assert shipped == "9.64.1"
 
 
 def test_executor_carries_compaction_guidance():
```
<!-- END_GIT_DIFF -->
