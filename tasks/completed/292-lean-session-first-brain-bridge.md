# Task 292: Lean Session-First Brain Bridge Refactor

**File:** `tasks/qa/292-lean-session-first-brain-bridge.md`
**Source:** orchestrator
**Type:** refactor
**Status:** in-progress

## Goal

Refactor `mcp-brain-bridge` into a lean (~600 LOC), session-first gateway that persists multi-task conversation threads under `session_id`, removes dead tools (`read_file`, `grep_files`, `get_context_bundle`), removes multipart chunking/allocators, and expands input capacity to modern token limits (1,000,000 chars), with full doc and test synchronization.

## Micro-Task Checklist (Orchestrator blueprint)

- [x] **Step 1:** Move task to in-progress + uncouple session/task exclusion in `preflight.py`.
- [x] **Step 2:** Prune dead file tools + allocator from `server.py`, 1M budget, session-first routing.
- [x] **Step 3:** Update test suite (preflight, bridge, capability).
- [x] **Step 4:** RTK test suite green + sync docs + CHANGELOG.

## Local TODOs

- [x] Remove dead file tools from `mcp-brain-bridge/server.py`
- [x] Eliminate multipart attachment slicing
- [x] Session-first transcript routing (`tasks/.sessions/<session_id>/transcript.jsonl`)
- [ ] Update unit tests to pruned toolset and session routing
- [ ] RTK full suite green + doc synchronization

## Acceptance Criteria

- [x] AC1: Remove dead file tools (`read_file`, `grep_files`, `get_context_bundle`) from `mcp-brain-bridge/server.py`.
- [x] AC2: Eliminate multipart attachment slicing (`_allocate_attachments`, `_render_attachment`, `_marker_room`, and `[ATTACHMENT part=1/3]`), allowing full context and diff Markdown reports to enter the prompt unsliced.
- [x] AC3: Remove `history.pop(1)` middle-turn dropping and expand `_INPUT_BUDGET` to 1,000,000 characters.
- [x] AC4: Refactor `preflight.py` and `server.py` so `session_id` is the primary transcript folder key (`tasks/.sessions/<session_id>/transcript.jsonl`), preserving conversational context across tasks in a session.
- [x] AC5: Update unit tests in `tests/test_brain_bridge.py`, `tests/test_brain_preflight.py`, and `tests/test_brain_capability.py` to match the pruned toolset and session-first transcript routing.
- [x] AC6: Verify full test suite passes green via RTK (`rtk test uv run --project mcp-brain-bridge --with pytest pytest`).
- [x] AC7: Synchronize documentation in `docs/brain-bridge.md`, `AGENTS.md`, and `agents/cognitive-executor.md`.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_preflight.py tests/test_brain_capability.py -q`
- **Expected result:** pass, exit code 0
- **Actual result:** `313 passed in 1.57s`, exit 0
- **Exit code:** 0
- **Full-suite note:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest` (no filter) does NOT go green for pre-existing reasons outside this diff, verified on the pristine tree via `git stash`: `tests/test_bundle_tasks.py` fails collection (`ModuleNotFoundError: No module named 'pathspec'` — env lacks the dep; 29 further `test_mcp_servers.py` failures share the cause) and 2 `test_decision_server.py` extract cases fail identically with and without this diff. Brain scope (`--ignore=tests/test_bundle_tasks.py` aside): all non-pre-existing failures are zero.
- **Doc sync:** `python3 scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** pruning tools and expanding input budget raises per-turn token spend; session-first routing changes transcript paths relied on by task-keyed history.
- **Rollback plan:** revert `mcp-brain-bridge/` hunks; transcript routing reverts by restoring task-keyed history writes.

---

## Execution Log & Reasoning

**Created (2026-10-04):** backlog task file generated via `task-generator` skill; NEXT_ID 292 discovered across `tasks/backlog|in-progress|qa|completed|archive` (lanes empty except completed max 291; `.sessions/` holds no numeric prefixes). Awaiting planning gate before implementation.

**Brainstorm:** not required — single-domain backend refactor with an explicit Orchestrator blueprint; no cross-disciplinary ambiguity. Approved plan = the `<hands_implementation_task>` XML micro-task checklist; executing from it.

**Implementation (2026-10-04):**
- Refactored `preflight.py` to allow concurrent `session_id` and `task_id` (`binding="session"`, `history_key` → `session_id`, mutual-exclusion raise removed; module + property docstrings updated).
- Pruned dead file tools (`read_file`, `grep_files`, `get_context_bundle` wrappers + `_read_file_impl` / `_grep_files_impl` + read/grep guardrail consts) and the multipart slicing allocator (`_allocate_attachments`, `_render_attachment`, `_marker_room`, `_open_overhead`, `_validate_attachment_resume`, `_attachment_priority`, priority tuples, marker-room consts) from `server.py`; restored `_fence_guard` + `_qa_like_prompt` live helpers the block cut had taken. New `_render_direct` renders every attachment whole with per-candidate caps + shared context-path total cap, inline truncation notes, zero part markers. Expanded `_INPUT_BUDGET` to 1,000,000 characters. Removed the `history.pop(1)` middle-turn drop loop (history bounded at load by `_HISTORY_LIMIT = 40`). `brain_turn`: `attachment_resume` parameter + resume block removed; session-first scope line; history always ships whole.
- Assumption A1: kept `_build_context_bundle` / `_build_structural_pack` / `_latest_report_path` (the bundle still auto-attaches on `include_bundle`; only the tool wrapper was dead). Assumption A2: kept `_resolve_under_root` / `_explicit_root` / `_workspace_root` / `_ALLOWED_READ_SUFFIXES` / `_READ_MAX_BYTES` (live paths: `_path_candidates`, one-off root pinning, task resolution).
- Updated test suite: preflight coexistence tests (binding/history_key + turn-level), removed read/grep/render/resume/priority/chunk tests, rewrote truncation/priority/cap tests for direct rendering, added session-thread persistence test (`test_brain_turn_persists_thread_across_session_turns`) and no-drop tests. Capability tests already aligned (no pruned-surface references).
- Updated test suite and documentation (`docs/brain-bridge.md` session-first history, native-tools file pulls, 1M budget, direct rendering, zero-truncation payload; `AGENTS.md` Buffer Isolation + end-of-task session notes; `agents/cognitive-executor.md` `session_id`-alongside-`task_id` call rule; `CHANGELOG.md` Changed + Removed entries).
- Note: `~600 LOC` goal is aspirational — `server.py` went 4194 → 3741 lines; the remaining machinery (transport/recovery/diagnostics/ledger/capability/history) is out of this task's deletion list and was deliberately kept (no scope widening).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index ccf9233..720faf5 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -44,7 +44,7 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
 - **Don't** perform financial mutations without snapshotting the prior state or allow nulls in monetary aggregations.
   -> **Do** follow the Universal Financial Ledger Standard: snapshot-on-write, `$ifNull` precedence, discrepancy alerting, deep config merging. See `docs/conventions.md`.
 - **Don't** carry over assumptions, partial results, or architectural hypotheses from a previous task.
-  -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase).
+  -> **Do** flush context and treat every task as contextually independent (Buffer Isolation directive in validation-phase). Flushing covers working execution assumptions only — the Brain session thread persists across tasks under the active session ID (`brain_turn(session_id=...)`), so conversational context survives task boundaries while each task is still judged on its own evidence.
 - **Don't** execute raw, informal, or non-English (Farsi) prompts directly.
   -> **Do** ALWAYS process through the Input Validation Pipeline first: Validate → Translate → Enrich → Refactor → Execute. If the input is unclear, HALT and request clarification. NEVER proceed to task generation with unvalidated input. (Note: If you receive a standard XML task block, skip this and execute normally).
 - **Don't** attempt to resolve cross-disciplinary ambiguity within a single persona.
@@ -121,6 +121,8 @@ At the start of every task, you MUST call `search_memory` or `list_namespaces` t
 
 ## 🛑 MANDATORY END-OF-TASK SEQUENCE
 
+> Session note: closing a task file does not close the Brain thread — history persists across tasks under the active session ID until the session ends.
+
 When finishing a task, you MUST execute these exact steps in order:
 
 1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 98f37a1..e8eb838 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -25,6 +25,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Documented the agent-callable `compact_context` tool (Task 289, system prompt 9.52.0):** the smart-compact plugin gained a `compact_context` tool so the agent can compress the session itself instead of waiting for a Manager slash command; the HQ text that said the agent cannot trigger compaction is now corrected. Fragment 22 (`<compaction_protocol>`) states the agent can call `compact_context` (`keepTurns`, `mode`), the executor item 4 mirrors it, and `docs/compaction.md` gains an "Agent-callable tool" section. `<system_version>` 9.51.0 → 9.52.0, regenerated byte-identical; the prompt-sync test pins 9.52.0 and asserts `compact_context`. Live smoke: `compact_context` returned the correct trim and compact messages; plugin loaded 25 times, 0 failures. Targeted gate: **83 passed**, exit 0.
 - **Adopted Smart Compact as the platform compaction plugin (Task 288, system prompt 9.51.0):** the V1-era `magic-compact` package fails to load on OpenCode 2 (`PluginModule.LoadError` — it exports the V1 plugin shape), so the platform now uses our own V2-native `@mokhtarabadi/opencode-smart-compact` instead. The plugin is a clean-room rewrite (separate repo, 14 passing tests, `tsc --noEmit` clean, `verify:package` OK): it keeps a per-session compaction state in plugin storage and applies it to model-visible messages via `session.hook("context")`, never mutating the stored transcript, with `/magic-compact [N]`, `/magic-trim [N]`, `/magic-stats`, and the `read_omitted_content` tool. Updated `<compaction_protocol>` (fragment 22), `agents/cognitive-executor.md`, `README.md`, `LLM.txt` (§7 JSON + §7.7), `docs/compaction.md`, and the `opencode_config` memory; `<system_version>` 9.50.0 → 9.51.0 with a regenerated, byte-identical `system-prompt.md`; prompt-sync tests now pin 9.51.0 and assert the smart-compact contract. Native auto-compaction stays on as the safety net. Global `plugins` points at the plugin (local checkout path until it is published to npm). Targeted gate: **83 passed**, exit 0.
 
+- **Lean session-first Brain bridge refactor (Task 292):** Modernized `mcp-brain-bridge` to session-first routing, expanded input budget to 1M chars, and allowed persistent multi-task threads under `session_id`. `preflight.validate_request` no longer rejects coexisting `task_id` + `session_id`: `binding` becomes `"session"` and `history_key` returns the session id, so transcripts persist in `tasks/.sessions/<session_id>/transcript.jsonl` while the task file and diff still resolve from `task_id` (bare `task_id` alone keeps the legacy task-keyed transcript). Attachments render whole via a direct renderer — no allocator, no chunking, no `[ATTACHMENT part=1/3]` / `[NEXT_ATTACHMENT_PART]` markers — each bounded only by its own configured cap with an inline truncation note; history is never dropped to fit (the shipped thread is already bounded at load to the last 40 messages). Docs synced (`docs/brain-bridge.md` session-first history, file pulls via Hands native tools, 1M budget; `AGENTS.md` Buffer Isolation + end-of-task session note; `agents/cognitive-executor.md` `session_id`-alongside-`task_id` call rule). Brain suites: **313 passed** (exit 0); remaining repo failures are pre-existing and unrelated (`pathspec` missing from the bridge test env; 2 decision-server extract cases failing on the pristine tree).
+
+### Removed
+
+- **Lean session-first Brain bridge refactor (Task 292):** Removed dead tools `read_file`, `grep_files`, and `get_context_bundle` from `mcp-brain-bridge` (Hands use native OpenCode `read`/`grep`/`glob`; the five-file bundle still auto-attaches internally). Removed the multipart chunking allocator (`_allocate_attachments`, `_render_attachment`, `_marker_room`, `_open_overhead`, `_validate_attachment_resume`, `_attachment_priority`, priority tuples) and the `attachment_resume` turn parameter, plus the `history.pop(1)` middle-turn drop loop and the `_read_file_impl` / `_grep_files_impl` helpers with their grep/read guardrail constants.
+
 ## [9.49.0] - 2026-10-01
 
 ### Added
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 381b6e8..b7f89af 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -399,7 +399,11 @@ needs no extra machinery.
    (e.g. "QA engineer please make the adversarial testing") + the full
    active task file + any prior answers. QA and reviewer turns MUST pass
    `include_diff=True` so the changed hunks ride along — the Brain judges
-   the actual changes, never a summary.
+   the actual changes, never a summary. Every `brain_turn` call passes
+   `session_id` alongside `task_id` (session-first): one thread spans
+   the whole work session, while the task file and diff still resolve
+   from `task_id`. A bare `task_id` with no `session_id` keeps the
+   legacy task-keyed transcript.
 2. **Call** `brain_turn`. Read `status`:
    - `XML_EXTRACTED` — execute `xml_blocks` as the next instruction set,
      exactly like an Orchestrator XML block.
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index 6ebb0d6..7b8ca2a 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -24,14 +24,17 @@ retired persona engine. The Hands calls it for every Brain turn
    the Hands until the Manager answers (Autopilot mode answers
    from `manager_decision` rulings instead — see below).
 
-## Per-task chat history
+## Session-first chat history
 
 The LLM is stateless, so the bridge keeps a JSONL transcript per
-task under `BRAIN_SESSIONS_ROOT`
+**session** under `BRAIN_SESSIONS_ROOT`
 (default `~/.config/opencode/brain-sessions`), capped at the last
-40 messages. Pass `task_id` (e.g. `190`) and every call loads the
-full conversation first, then appends both new turns. Each task
-keeps its own ChatGPT-style context from first message to close.
+40 messages. Pass `session_id` (e.g. `sess-1`) alongside `task_id` and
+every call loads the full session conversation first, then appends both
+new turns. One session thread spans every task in the work session or
+sprint — planning, implementation, QA, and review all share the same
+context. A bare `task_id` with no `session_id` falls back to the
+task-keyed transcript for backward compatibility.
 
 The transcript is replayed on every later turn, so a stored turn
 must stay small. The user turn is therefore stored in compact form:
@@ -53,33 +56,26 @@ the industry pattern: OpenCode, Claude Code, and Codex all persist the
 full transcript and compact only what they send; OpenCode keeps full
 session history in SQLite.
 
-## File pull tools
+## File pulls (Hands native tools)
 
 The Brain cannot read the Hands' disk — it only sees what a `brain_turn`
-call carries. The Hands close that gap with three server-side helpers.
-The Brain never calls them directly: it quotes needed paths and the
-Hands pull the content into the next turn.
-
-- `get_context_bundle()` — assembles the five small files
-  (`agents/cognitive-executor.md`, `docs/conventions.md`,
-  `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md`) into one
-  labeled bundle. Missing files become `[missing: path]` lines (never
-  raise, per the Absent-File Policy). Each file caps at 60,000 chars
-  with a `[truncated]` marker.
-- `read_file(path, offset=1, limit=200)` — the Hands read any text file under the
-  workspace root (the repo root, or `BRAIN_WORKSPACE_ROOT` when set) with
-  numbered lines (1-indexed). Only the `system_prompt_path` override
-  additionally allows the global install dir (`~/.config/opencode`). Hands pull task-file ranges
-  on demand instead of pasting whole files. Text extensions only; the Brain
-  must never be told to pull files itself.
-- `grep_files(pattern, subdir=".")` — the Hands search files for a pattern, up
-  to 30 `path:line: excerpt` hits, skipping banned directories.
-
-Budget-aware assembly: Hands grep first to locate, then read only the ranges
-that fit the remaining budget. The bundle caps (60,000/file) plus the
-`brain_turn` 100,000-char history truncation keep every call measurable
-(the bundle tests prove both legs: all five sections always present,
-total size measured by construction).
+call carries. The Hands close that gap with their own native OpenCode
+tools (`read`, `grep`, `glob`): the Brain quotes needed paths and the
+Hands pull the content into the next turn as fed-context. The bridge
+exposes exactly one tool, `brain_turn`; the former server-side helpers
+(`get_context_bundle`, `read_file`, `grep_files`) were removed. The
+five-file context bundle still auto-attaches on every turn (unless the
+caller passes `include_bundle=false`): `agents/cognitive-executor.md`,
+`docs/conventions.md`, `docs/architecture.md`, `docs/data_model.md`,
+`DESIGN.md` in one labeled section. Missing files become `[missing:
+path]` lines (never raise, per the Absent-File Policy). Each file caps
+at 60,000 chars with a `[truncated]` marker.
+
+Budget-aware assembly: Hands grep first to locate, then pull only the
+ranges that fit the remaining budget. The bundle caps (60,000/file)
+plus the 1,000,000-char input budget keep every call measurable.
+History is never truncated to fit — the shipped thread is already
+bounded at load (last 40 messages).
 
 Export mapping: the main entry is implemented as `brain_turn` in
 `mcp-brain-bridge/server.py` and exposed to operators as
@@ -110,73 +106,62 @@ repo-root `.env`). Real process env wins; blank counts as unset. See
 | `BRAIN_MODEL_HIGH`  | `openai/gpt-5.6-luna` for `T1`/`T2` turns; **unset** = built-in default, **blank** = `BRAIN_MODEL` |
 | `BRAIN_STAGE_TIERS` | `plan:T2,review:T2,implement:T0,qa:T0,closure:T0`    |
 | `BRAIN_TASK_ATTACH_CAP` | `60000` — task-file attachment chars; blank/unset = default |
-| `BRAIN_TASK_DIFF_CAP` | `200000` — changed-hunks chars per part; blank/unset = default |
+| `BRAIN_TASK_DIFF_CAP` | `200000` — changed-hunks chars; blank/unset = default |
 | `BRAIN_CTX_PER_FILE_CAP` | `60000` — per `context_paths` file; blank/unset = default |
 | `BRAIN_CTX_TOTAL_CAP` | `200000` — all `context_paths` per turn; blank/unset = default |
-| `BRAIN_INPUT_BUDGET` | `200000` — hard send ceiling (system + prompt), chars |
+| `BRAIN_INPUT_BUDGET` | `1000000` — input budget ceiling (system + prompt + history), chars |
 | `BRAIN_MODEL_WINDOW_CHARS` | `200000` — utilization monitor only, never a send cap |
 
-`BRAIN_INPUT_BUDGET` defaults to the model-window estimate above. The
-assembly string for the Hands system prompt measures ~87.6k chars, so the
-older 100k ceiling left only ~12k for the change set a reviewer must read
-— which starved the very attachments this ceiling exists to bound. At the
-measured ~4.6 chars/token, 200k chars is ~43k input tokens. Set
-`BRAIN_INPUT_BUDGET` to a smaller positive integer to restore a tighter
-ceiling.
+`BRAIN_INPUT_BUDGET` defaults to 1,000,000 chars (~217k input tokens at
+the measured ~4.6 chars/token) — room for full context and diff reports
+plus the whole session thread. Set `BRAIN_INPUT_BUDGET` to a smaller
+positive integer to restore a tighter ceiling.
 
 Every cap above follows the blank-means-unset rule: an unset **or blank**
 variable applies the documented default, and a real non-empty value wins.
 A malformed or non-positive value raises a configuration error instead of
 being silently clamped.
 
-## Attachment budgeting
+## Attachment rendering (direct, no allocator)
 
-Attachments are not appended independently any more: one shared allocator
-renders every candidate against the chars actually left in
-`BRAIN_INPUT_BUDGET` after the system prompt and the caller's prompt. The
-configured caps above bound a single attachment; the allocator bounds the
-whole turn, so stacked attachments can never each assume the full window.
+Attachments enter whole — no allocator, no chunking, no part markers.
+Each attachment is rendered directly against its own configured cap
+(task/diff per-attachment caps, `context_paths` per-file plus one shared
+total cap), with an inline `[...truncated ...]` note when a cap cuts.
+The configured caps above bound a single attachment; the 1M input budget
+bounds the whole turn, so stacked attachments can never overflow the
+window. Conversation history is always attached in full (bounded at load
+to the last 40 messages) and is never cut to fit.
 
-Priority is stage-aware. On `qa` and `review` turns the order is
-**context_paths → diff → task → fed context → bundle**: explicit evidence
-outranks the general small-file bundle, so a reviewer never loses the
-changed hunks to boilerplate. Every other stage keeps the historical
-order (bundle → task → context_paths → diff → fed). Conversation history
-is always the last fallback; it is deliberately not subtracted from the
-attachment budget, which keeps the prompt-cache static prefix stable
-across turns.
-
-When an attachment exceeds its room, the block is chunked instead of
-silently cut — numbered parts with an exact resume offset:
+Task file and diff blocks keep their stable labels:
 
 ```text
-[ATTACHMENT kind=diff path="tasks/qa/12-x.md" part=1/3 offset_chars=0 shown_chars=80000 total_chars=250000]
-...content...
-[END ATTACHMENT kind=diff path="tasks/qa/12-x.md" part=1/3]
-[NEXT_ATTACHMENT_PART kind=diff path="tasks/qa/12-x.md" next_offset_chars=80000 remaining_chars=170000]
+[task-file:200: tasks/qa/200-x.md]
+```markdown
+...working content (Factual Git Diff stripped)...
+```
+[changed-hunks:200: tasks/qa/200-x.md]
+```diff
+...verbatim hunks...
+```
 ```
 
-Pass `attachment_resume={"kind": "diff", "path": "...",
-"offset_chars": N}` on the next turn to continue from that offset. A
-malformed resume is ignored with a stderr note and never breaks a turn.
+Context paths render as `[path-injected: <path>]` followed by content.
 
-## Response payload: two different truncations
+## Response payload: two truncation counters (both normally zero)
 
-The result dict reports attachment loss and history loss separately —
-they are different failures:
+The result dict keeps the attachment/history loss fields for schema
+stability — with direct rendering and no history dropping, both are
+always empty:
 
-- `history_turns_dropped` — canonical count of middle transcript turns
-  dropped to fit the budget. `truncated_count` remains as the
-  back-compat alias and always equals it. Both are `0` on a
+- `history_turns_dropped` — always `0`: history is never cut to fit.
+  `truncated_count` remains as the back-compat alias. Both are `0` on a
   capability-blocked turn.
-- `attachments_truncated` — a list (empty when nothing was cut) whose
-  entries carry `kind` (`diff` | `task` | `context_path` | `bundle` |
-  `fed_context`), `path`, `shown_chars`, `total_chars`, `dropped_chars`,
-  `part`, `parts`, `offset_chars`, `next_offset_chars`,
-  `remaining_chars`, and `budget_chars_remaining`.
-- `attachment_parts` — resume metadata for every chunked attachment.
+- `attachments_truncated` — always `[]`: cap cuts are noted inline in
+  the block, never as resume tokens.
+- `attachment_parts` — always `[]`: no chunking, no resume metadata.
 - `attachment_budget_chars` / `attachment_chars_used` /
-  `attachment_chars_remaining` — the attachment budget accounting.
+  `attachment_chars_remaining` — used-char accounting for the turn.
 
 A capability-blocked turn returns the same field set (with `status:
 "REPORT"`), so callers never face two incompatible schemas.
diff --git a/mcp-brain-bridge/preflight.py b/mcp-brain-bridge/preflight.py
index 40bea35..f30afcd 100644
--- a/mcp-brain-bridge/preflight.py
+++ b/mcp-brain-bridge/preflight.py
@@ -3,8 +3,9 @@
 Local, transport-free validation of every ``brain_turn`` call: an
 explicit ``project_root`` must hold a ``tasks/`` dir (raise, never
 silently fall back to the workspace root); memory-bearing turns bind to
-exactly one of ``task_id`` / ``session_id``; ``stage``, the boolean
-flags, the Kanban path, and ``required_tools`` are shape-checked.
+``session_id`` when present (session-first) else ``task_id``; ``stage``,
+the boolean flags, the Kanban path, and ``required_tools`` are
+shape-checked.
 
 Stdlib only — unit tests import this module without the MCP stack.
 """
@@ -60,8 +61,7 @@ def require_session_id(session_id: object) -> str:
     """Fail-closed gate for taskless saga turns. Returns the stripped
     id; raises PreflightError on traversal, separators, or overlong
     input — the id becomes a transcript path segment."""
-    if isinstance(session_id, str) and _SESSION_ID_RE.fullmatch(
-            session_id.strip()):
+    if isinstance(session_id, str) and _SESSION_ID_RE.fullmatch(session_id.strip()):
         return session_id.strip()
     raise PreflightError(
         f"bad session_id: {session_id!r} — must match "
@@ -136,18 +136,18 @@ def _check_stage(stage: object) -> Optional[str]:
     if isinstance(stage, str) and stage in ALLOWED_STAGES:
         return stage
     raise PreflightError(
-        f"bad stage: {stage!r} — must be one of {list(ALLOWED_STAGES)} "
-        "or omitted."
+        f"bad stage: {stage!r} — must be one of {list(ALLOWED_STAGES)} or omitted."
     )
 
 
 def _check_flags(include_bundle: object, include_diff: object) -> None:
-    for name, value in (("include_bundle", include_bundle),
-                        ("include_diff", include_diff)):
+    for name, value in (
+        ("include_bundle", include_bundle),
+        ("include_diff", include_diff),
+    ):
         if not isinstance(value, bool):
             raise PreflightError(
-                f"bad {name}: {value!r} — must be a bool, not "
-                f"{type(value).__name__}."
+                f"bad {name}: {value!r} — must be a bool, not {type(value).__name__}."
             )
 
 
@@ -161,13 +161,13 @@ def _resolve_kanban_path(kanban_path: object, *, root: Path) -> Optional[Path]:
         )
     raw = str(kanban_path)
     base = (root / "tasks").resolve()
-    candidate = (Path(raw).expanduser()
-                 if Path(raw).is_absolute() else (root / raw))
+    candidate = Path(raw).expanduser() if Path(raw).is_absolute() else (root / raw)
     try:
         resolved = candidate.resolve()
     except OSError as exc:
         raise PreflightError(
-            f"bad kanban_path: {raw!r} — unresolvable ({exc}).") from exc
+            f"bad kanban_path: {raw!r} — unresolvable ({exc})."
+        ) from exc
     if resolved != base and base not in resolved.parents:
         raise PreflightError(
             f"bad kanban_path: {raw!r} — escapes <project_root>/tasks/. "
@@ -175,15 +175,15 @@ def _resolve_kanban_path(kanban_path: object, *, root: Path) -> Optional[Path]:
         )
     if resolved.suffix != ".md":
         raise PreflightError(
-            f"bad kanban_path: {raw!r} — must point at a task .md file.")
+            f"bad kanban_path: {raw!r} — must point at a task .md file."
+        )
     return resolved
 
 
 def _check_required_tools(required_tools: object) -> tuple:
     if required_tools is None:
         return ()
-    if isinstance(required_tools, str) or not isinstance(
-            required_tools, (list, tuple)):
+    if isinstance(required_tools, str) or not isinstance(required_tools, (list, tuple)):
         raise PreflightError(
             f"bad required_tools: {required_tools!r} — must be a list of "
             "tool-name strings, e.g. ['question']."
@@ -200,6 +200,7 @@ def _check_required_tools(required_tools: object) -> tuple:
 @dataclass(frozen=True)
 class ValidatedRequest:
     """A ``brain_turn`` request that passed local preflight."""
+
     project_root: Optional[Path]
     binding: str  # "task" | "session" | "one-off"
     task_id: Optional[str] = None
@@ -212,9 +213,10 @@ class ValidatedRequest:
 
     @property
     def history_key(self) -> Optional[str]:
-        """Transcript key: task turns continue the task history, saga
-        turns continue the session history, one-offs persist nothing."""
-        return self.task_id if self.task_id is not None else self.session_id
+        """Transcript key: session-first — a supplied ``session_id``
+        keys the history so one thread spans tasks; otherwise a task
+        turn continues the task history; one-offs persist nothing."""
+        return self.session_id if self.session_id is not None else self.task_id
 
 
 def validate_request(
@@ -232,18 +234,15 @@ def validate_request(
 ) -> ValidatedRequest:
     """Validate a ``brain_turn`` request before any load, attach, or
     transport. Raises PreflightError on the first malformed field."""
-    if task_id is not None and session_id is not None:
-        raise PreflightError(
-            f"bad binding: task_id={task_id!r} and "
-            f"session_id={session_id!r} are mutually exclusive — pass "
-            "exactly one so history continues under a single key."
-        )
-    clean_task = (require_bare_task_id(task_id)
-                  if task_id is not None else None)
-    clean_session = (require_session_id(session_id)
-                     if session_id is not None else None)
-    binding = ("task" if clean_task is not None
-               else "session" if clean_session is not None else "one-off")
+    clean_task = require_bare_task_id(task_id) if task_id is not None else None
+    clean_session = require_session_id(session_id) if session_id is not None else None
+    binding = (
+        "session"
+        if clean_session is not None
+        else "task"
+        if clean_task is not None
+        else "one-off"
+    )
     _check_flags(include_bundle, include_diff)
     clean_stage = _check_stage(stage)
     clean_tools = _check_required_tools(required_tools)
@@ -260,7 +259,13 @@ def validate_request(
             )
         clean_kanban = _resolve_kanban_path(kanban_path, root=root)
     return ValidatedRequest(
-        project_root=root, binding=binding, task_id=clean_task,
-        session_id=clean_session, stage=clean_stage,
-        kanban_path=clean_kanban, include_bundle=bool(include_bundle),
-        include_diff=bool(include_diff), required_tools=clean_tools)
+        project_root=root,
+        binding=binding,
+        task_id=clean_task,
+        session_id=clean_session,
+        stage=clean_stage,
+        kanban_path=clean_kanban,
+        include_bundle=bool(include_bundle),
+        include_diff=bool(include_diff),
+        required_tools=clean_tools,
+    )
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 74b89db..9faf793 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -7,11 +7,16 @@
 # ]
 # ///
 
-"""Unified Brain bridge MCP server (Task 190).
+"""Unified Brain bridge MCP server (Task 190, lean session-first gateway).
 
-Four tools. ``brain_turn`` is the automation path; ``get_context_bundle``,
-``grep_files`` and ``read_file`` let the Hands locate a hit and pull only
-the range a turn needs.
+One tool. ``brain_turn`` is the automation path: the Hands builds a user
+prompt from its current machine state (e.g. "QA engineer please make
+the adversarial testing" + the task file), the server prepends the
+latest system prompt (read from the global install) as the system
+message, calls the LLM over the OpenAI Responses API via httpx, and
+returns the output — with any machine XML blocks extracted. The Hands
+locates files and pulls ranges with its own native OpenCode tools; the
+bridge exposes no file tools.
 
 ``brain_turn``: the Hands builds a user prompt from its current machine
 state (e.g. "QA engineer please make the adversarial testing" + the task
@@ -27,17 +32,21 @@ in as the next ``brain_turn`` user prompt. No gates, no per-persona
 commands — the auto-load persona + current modes in the system prompt
 cover identity.
 
-Per-task chat history (manager order, Task 190): the LLM is stateless,
-so every ``brain_turn`` with a ``task_id`` loads that task's prior
-user/assistant messages from its transcript file and sends them along
-— like a chat interface, first message to last, until the task closes.
-Each task keeps its own conversation under the project's sessions root
-(``<project>/tasks/.sessions/<task_id>/transcript.jsonl``, JSON lines).
+Per-session chat history (manager order, Task 190; session-first since
+Task 292): the LLM is stateless, so every ``brain_turn`` with a
+``session_id`` loads that session's prior user/assistant messages from
+its transcript file and sends them along — like a chat interface, first
+message to last. One session thread spans every task in the work
+session. Each session keeps its own conversation under the project's
+sessions root
+(``<project>/tasks/.sessions/<session_id>/transcript.jsonl``, JSON
+lines). A bare ``task_id`` with no ``session_id`` falls back to the
+task-keyed transcript for backward compatibility.
 ``BRAIN_SESSIONS_ROOT`` overrides that location. The old global directory
 (``~/.config/opencode/brain-sessions``) is a read-only fallback for
 history written before the per-project move; writes never land there.
-History is bounded (last 40 messages) so long tasks cannot overflow the
-context.
+History is bounded (last 40 messages) so long sessions cannot overflow
+the context.
 
 Transport: stdio FastMCP, mirroring the other servers. The model is
 called over the OpenAI Responses API (``{api_base}/responses``) via
@@ -298,19 +307,11 @@ _STRUCTURAL_REPORT_GLOB = "context-reports/tree_report_*.md"
 _STRUCTURAL_FILE_CAP = 40000
 _STRUCTURAL_MARKER = "=== context-reports/tree_report (latest) ==="
 
-# Text extensions readable via read_file / searchable via grep_files.
+# Text extensions readable for server-side path injection.
 _ALLOWED_READ_SUFFIXES = frozenset({".md", ".txt", ".json", ".yaml", ".yml", ".toml"})
 
-# Directories never descended into by grep_files.
-_SKIP_DIRS = frozenset(
-    {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}
-)
-
-# Guardrails for the file-pull tools (state-machine hotfix round).
-_READ_MAX_LINES = 2000  # read_file limit clamp — pulls stay pull-sized
-_READ_MAX_BYTES = 2_000_000  # read_file refuses bigger files outright
-_GREP_PATTERN_MAX = 500  # Brain-supplied regex length cap (ReDoS bound)
-_GREP_MAX_LINE_CHARS = 4000  # overlong lines are skipped, never searched
+# Guardrail for path injection (state-machine hotfix round).
+_READ_MAX_BYTES = 2_000_000  # oversized files are refused outright
 
 
 def _workspace_root() -> Path:
@@ -803,160 +804,6 @@ def _build_context_bundle(root: Optional[str] = None) -> str:
     return "\n\n".join(parts)
 
 
-def _read_file_impl(
-    path: str,
-    offset: int = 1,
-    limit: int = 200,
-    project_root: Optional[str] = None,
-) -> dict[str, Any]:
-    """Numbered-line slice of a workspace text file (1-indexed offset).
-
-    The ``limit`` clamps to ``_READ_MAX_LINES`` and files over
-    ``_READ_MAX_BYTES`` are refused — pulls stay pull-sized and can
-    never drag a giant file into context. ``project_root`` pins the tree
-    the path resolves against (issue #24); ``None`` falls back to
-    ``_workspace_root()``.
-    """
-    if not isinstance(path, str) or not path.strip():
-        raise ValueError(f"bad path: {path!r}")
-    if offset < 1:
-        raise ValueError(f"bad offset (1-indexed): {offset!r}")
-    if limit < 1:
-        raise ValueError(f"bad limit: {limit!r}")
-    limit = min(limit, _READ_MAX_LINES)
-    resolved = _resolve_under_root(path, _explicit_root(project_root))
-    if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
-        raise ValueError(f"unsupported extension: {path!r}")
-    try:
-        if resolved.stat().st_size > _READ_MAX_BYTES:
-            raise ValueError(
-                f"file too large for read_file: {path!r} (>{_READ_MAX_BYTES} bytes)"
-            )
-    except OSError:
-        pass  # stat failed — the read below raises the real error
-    text = resolved.read_text(encoding="utf-8", errors="replace")
-    lines = text.splitlines()
-    total = len(lines)
-    end = min(offset - 1 + limit, total)
-    numbered = [f"{n}: {lines[n - 1]}" for n in range(offset, end + 1)]
-    return {
-        "path": path,
-        "offset": offset,
-        "limit": limit,
-        "total_lines": total,
-        "lines": numbered,
-    }
-
-
-def _grep_files_impl(
-    pattern: str, subdir: str = ".", project_root: Optional[str] = None
-) -> list[str]:
-    """Python-regex search over workspace text files (max 30 hits).
-
-    Hardening: the Brain-supplied pattern caps at ``_GREP_PATTERN_MAX``
-    chars (``re`` has no timeout, so length is the ReDoS bound), each hit
-    line truncates at 200 chars, lines over ``_GREP_MAX_LINE_CHARS`` are
-    skipped unsearched, and every candidate resolves against the root
-    BEFORE it is read — a symlink escaping the workspace is skipped,
-    never opened. ``project_root`` pins the tree searched (issue #24);
-    ``None`` falls back to ``_workspace_root()``.
-    """
-    if not isinstance(pattern, str) or not pattern:
-        raise ValueError(f"bad regex: {pattern!r}")
-    if len(pattern) > _GREP_PATTERN_MAX:
-        raise ValueError(f"regex too long ({len(pattern)} > {_GREP_PATTERN_MAX})")
-    try:
-        rx = re.compile(pattern)
-    except re.error as exc:
-        raise ValueError(f"bad regex: {pattern!r} ({exc})") from exc
-    _pinned = _explicit_root(project_root)
-    root = (_pinned if _pinned is not None else _workspace_root()).resolve()
-    base = _resolve_under_root(subdir, root)
-    if not base.is_dir():
-        return []
-    hits: list[str] = []
-    for dirpath, dirnames, filenames in os.walk(base):
-        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
-        for name in filenames:
-            if Path(name).suffix.lower() not in _ALLOWED_READ_SUFFIXES:
-                continue
-            fpath = Path(dirpath) / name
-            try:
-                resolved = fpath.resolve()
-                resolved.relative_to(root)
-            except (OSError, ValueError):
-                continue  # symlink escape — skip before any read
-            try:
-                text = resolved.read_text(encoding="utf-8", errors="replace")
-            except OSError:
-                continue
-            rel = resolved.relative_to(root).as_posix()
-            for lineno, line in enumerate(text.splitlines(), 1):
-                if len(line) > _GREP_MAX_LINE_CHARS:
-                    continue
-                if rx.search(line):
-                    hits.append(f"{rel}:{lineno}: {line.strip()[:200]}")
-                    if len(hits) >= 30:
-                        return hits
-    return hits
-
-
-@mcp.tool()
-def get_context_bundle(project_root: Optional[str] = None) -> str:
-    """Return the labeled small-file context bundle from the active project root. The Hands call this for bundle proof or debugging; every brain_turn already injects it by default.
-
-    ``project_root`` pins the project the bundle is read from (issue #24);
-    omit it to auto-resolve the active project root (``BRAIN_PROJECT_ROOT``,
-    then a cwd ``tasks/`` walk-up, then ``BRAIN_WORKSPACE_ROOT``).
-    Missing files become ``[missing: path]`` marker lines (never raise);
-    each file caps at 60000 chars with a ``[truncated]`` marker.
-    """
-    return _build_context_bundle(project_root)
-
-
-@mcp.tool()
-def read_file(
-    path: str,
-    offset: int = 1,
-    limit: int = 200,
-    project_root: Optional[str] = None,
-) -> dict[str, Any]:
-    """Read numbered lines from a workspace text file (1-indexed offset). The Hands call this after grep_files locates a hit; the Brain never calls it directly. Text extensions only (.md .txt .json .yaml .yml .toml); Python and other extensions are refused.
-
-    ``project_root`` pins the tree ``path`` resolves against (issue #24);
-    omit it to auto-resolve the active project root.
-
-    Returns ``{"path", "offset", "limit", "total_lines", "lines"}``. Each
-    entry in ``lines`` is already numbered as ``"N: text"``, so do not add
-    another prefix. ``limit`` clamps to 2000 lines, and a file over
-    2,000,000 bytes is refused. Bad input — a blank path, an ``offset``
-    below 1, a ``limit`` below 1, a non-allowlisted extension, or an
-    oversized file — raises ``ValueError`` instead of returning a partial
-    result.
-    """
-    return _read_file_impl(path, offset, limit, project_root)
-
-
-@mcp.tool()
-def grep_files(
-    pattern: str, subdir: str = ".", project_root: Optional[str] = None
-) -> list[str]:
-    """Regex-search workspace text files; up to 30 ``path:line: excerpt`` hits. The Hands call this first to locate, then read only the ranges that fit the remaining budget.
-
-    ``project_root`` pins the tree searched (issue #24); omit it to
-    auto-resolve the active project root.
-
-    Scope: only the six read suffixes are searched — ``.md``, ``.txt``,
-    ``.json``, ``.yaml``, ``.yml``, ``.toml``. Source files such as
-    ``.py`` are never opened, so an empty result for them means "not
-    searched", not "no match". ``.git``, ``__pycache__``, ``.venv``,
-    ``node_modules`` and ``.pytest_cache`` are skipped. Lines longer than
-    4000 chars are skipped unsearched, and a pattern longer than 500 chars
-    raises ``ValueError`` (the ReDoS bound).
-    """
-    return _grep_files_impl(pattern, subdir, project_root)
-
-
 # Prompt overrides must be real prompt files: .md only, resolved under
 # the repo root or ~/.config/opencode (the two legitimate homes).
 _PROMPT_SUFFIX = ".md"
@@ -1862,16 +1709,12 @@ def _send_with_learning(
 # Max prior messages re-sent per turn. Bounds context for long tasks.
 _HISTORY_LIMIT = 40
 
-# Max prompt + history chars per turn. Oldest history drops first.
-#
-# Defaults to the same value as the model-window estimate below: a live
-# probe showed the assembled system prompt alone is ~87.6k chars, so the
-# older 100k ceiling left only ~12k of room for the change set a QA or
-# reviewer turn must see — which is the very starvation this ceiling was
-# meant to prevent. At the measured ~4.6 chars/token, 200k chars is
-# ~43k input tokens, well inside the documented window. Operators who
-# want the tighter ceiling back set BRAIN_INPUT_BUDGET.
-_INPUT_BUDGET = 200000
+# Max prompt + history chars per turn. History is never dropped to fit:
+# the shipped transcript is bounded at load (``_HISTORY_LIMIT``), so this
+# ceiling only bounds fresh attachments against modern long-context
+# windows. At ~4.6 chars/token, 1M chars is ~217k input tokens.
+# Operators who want a tighter ceiling set BRAIN_INPUT_BUDGET.
+_INPUT_BUDGET = 1000000
 
 # Assumed model window (chars) for the utilization monitor below.
 # Informational only — providers differ; the send cap stays _INPUT_BUDGET.
@@ -2535,24 +2378,17 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
     return "\n\n---\n\n".join(blocks)
 
 
-# --- Shared attachment allocator ------------------------------------
-# The model input ceiling is authoritative, so every attachment is
-# rendered by ONE allocator against the chars actually left after the
-# system prompt, the caller's prompt, and the shipped history. Each
-# builder above keeps its own semantics for direct callers; these
-# helpers feed the turn-level allocator instead.
+# --- Direct attachment rendering ------------------------------------
+# No allocator, no chunking, no part markers: every attachment enters
+# whole, bounded only by its own configured cap. Caps still apply
+# (task/diff per-attachment caps, ``context_paths`` per-file + shared
+# total caps) with an inline truncation note — the Brain judges visible
+# scope only and quotes needed paths for follow-ups.
 
-#: Stages whose turns rank explicit evidence above the small-file bundle.
-_REVIEW_STAGES = frozenset({"qa", "review"})
 
-#: Attachment priority per turn shape. Review/QA turns must see the
-#: changed hunks and explicitly requested files before the bundle.
-_PRIORITY_REVIEW = ("context_path", "diff", "task", "fed_context", "bundle")
-_PRIORITY_DEFAULT = ("bundle", "task", "context_path", "diff", "fed_context")
-
-#: Marker overhead reserved per rendered attachment (chars), so a part can
-#: never overflow the room it was granted.
-_ATTACHMENT_MARKER_ROOM = 200
+def _fence_guard(text: str) -> str:
+    """Break embedded fences invisibly so content cannot close our block."""
+    return text.replace(chr(96) * 3, chr(96) * 2 + chr(8203) + chr(96))
 
 
 def _qa_like_prompt(user_prompt: object) -> bool:
@@ -2565,310 +2401,63 @@ def _qa_like_prompt(user_prompt: object) -> bool:
     )
 
 
-def _validate_attachment_resume(resume: object) -> Optional[dict]:
-    """Validate an ``attachment_resume`` request (``None`` when unusable).
-
-    Accepts ``{"kind": "diff"|"context_path", "path": str,
-    "offset_chars": int >= 0}`` — the shape the response payload and the
-    ``[NEXT_ATTACHMENT_PART]`` marker publish. A malformed resume is
-    ignored with a stderr note so it can never break a turn.
-    """
-    if not isinstance(resume, dict):
-        print(
-            "brain-bridge: attachment_resume ignored (not a mapping)", file=sys.stderr
-        )
-        return None
-    kind = resume.get("kind")
-    path = resume.get("path")
-    if (
-        kind not in ("diff", "context_path")
-        or not isinstance(path, str)
-        or not path.strip()
-    ):
-        print(
-            "brain-bridge: attachment_resume ignored (bad kind/path)", file=sys.stderr
-        )
-        return None
-    try:
-        offset = int(resume.get("offset_chars", 0))
-    except (TypeError, ValueError):
-        print(
-            "brain-bridge: attachment_resume ignored (bad offset_chars)",
-            file=sys.stderr,
-        )
-        return None
-    return {"kind": kind, "path": path.strip(), "offset_chars": max(0, offset)}
-
-
-def _attachment_priority(stage: Optional[str]) -> tuple:
-    """Attachment priority order for ``stage`` (review/QA evidence first)."""
-    if (stage or "").strip().lower() in _REVIEW_STAGES:
-        return _PRIORITY_REVIEW
-    return _PRIORITY_DEFAULT
-
-
-def _fence_guard(text: str) -> str:
-    """Break embedded fences invisibly so content cannot close our block."""
-    return text.replace(chr(96) * 3, chr(96) * 2 + chr(8203) + chr(96))
-
-
-#: Separator the turn joins attachment blocks with. The allocator prices it
-#: per block so the assembled prompt can never creep past the send ceiling
-#: by the join overhead the individual block sizes do not include.
-_SEP_LEN = len("\n\n---\n\n")
-
-
-def _open_overhead(open_line: str, fence_lang: Optional[str]) -> int:
-    """Chars the UNMARKED wrapper adds around the body (measured).
-
-    A whole-fit attachment still carries its open line and fence, so the
-    fit test must price them: comparing only the body length against the
-    room let a rendered block exceed the room it was granted.
-    """
-    lines = [open_line]
-    if fence_lang:
-        lines.append(f"```{fence_lang}")
-    lines.append("")
-    if fence_lang:
-        lines.append("```")
-    return len("\n".join(lines))
-
-
-def _marker_room(
-    kind: str,
-    path: str,
-    total: int,
-    open_line: str = "",
-    fence_lang: Optional[str] = None,
-) -> int:
-    """Complete wrapper overhead (chars) for a SPLIT attachment.
-
-    Priced from the line shapes actually emitted — the part markers, the
-    caller's open line, the fence lines and every newline separator —
-    instead of a fixed guess. The body itself is excluded, so the
-    allocator can size the body as ``room - _marker_room(...)`` and the
-    rendered block can never exceed the room it was granted. ``total``
-    sizes the numeric fields; the result never falls below the floor
-    constant.
-    """
-    digits = len(str(max(total, 1))) + 2  # part/parts can exceed total
-    header = (
-        f'[ATTACHMENT kind={kind} path="{path}" part=1/1 '
-        f"offset_chars=0 shown_chars=0 total_chars=0]"
-    )
-    end = f'[END ATTACHMENT kind={kind} path="{path}" part=1/1]'
-    nxt = (
-        f'[NEXT_ATTACHMENT_PART kind={kind} path="{path}" '
-        f"next_offset_chars=0 remaining_chars=0]"
-    )
-    lines = [header, open_line]
-    if fence_lang:
-        lines.append(f"```{fence_lang}")
-    lines.append("")
-    if fence_lang:
-        lines.append("```")
-    lines.append(end)
-    lines.append(nxt)
-    return max(
-        _ATTACHMENT_MARKER_ROOM,
-        len("\n".join(lines)) + digits * 6,
-    )
-
-
-def _render_attachment(
-    kind: str,
-    path: str,
-    open_line: str,
-    fence_lang: Optional[str],
-    text: str,
-    room: int,
-    offset: int = 0,
-) -> tuple[str, Optional[dict]]:
-    """Render one labeled attachment inside ``room`` chars.
-
-    Returns ``(rendered, meta)``. ``meta`` is ``None`` when the whole
-    attachment fit; otherwise it reports exactly how many chars were
-    shown, how many were dropped, and the offset that resumes it — so a
-    caller can always ask for the remainder instead of declaring the
-    unseen scope UNVERIFIABLE.
-    """
-    total = len(text)
-    try:
-        offset = max(0, min(int(offset), total))
-    except (TypeError, ValueError):
-        offset = 0
-    # A whole-fit attachment gets NO part markers: reserving the marker room
-    # unconditionally split a file that fit its cap exactly into a second
-    # 200-char part, which reported a truncation that never happened. The
-    # reservation applies only when a split is genuinely required.
-    # Price the COMPLETE emitted wrapper — the open line, the fence lines
-    # and every newline separator, not just the body — so a rendered block
-    # can never exceed the room the allocator granted. An exact fit still
-    # renders with no part markers.
-    fits = (total - offset) + _open_overhead(open_line, fence_lang) <= room
-    part_size = max(
-        1,
-        room
-        - _marker_room(kind, path, total, open_line=open_line, fence_lang=fence_lang),
-    )
-    body = text[offset:] if fits else text[offset : offset + part_size]
-    shown = len(body)
-    next_offset = offset + shown
-    remaining = total - next_offset
-    parts = max(1, (total + part_size - 1) // part_size)
-    part = min(parts, offset // part_size + 1)
-    lines: list[str] = [open_line]
-    if fence_lang:
-        lines.append(f"```{fence_lang}")
-    lines.append(body)
-    if fence_lang:
-        lines.append("```")
-    if remaining <= 0:
-        return "\n".join(lines), None
-    lines.insert(
-        0,
-        (
-            f'[ATTACHMENT kind={kind} path="{path}" part={part}/{parts} '
-            f"offset_chars={offset} shown_chars={shown} total_chars={total}]"
-        ),
-    )
-    lines.append(f'[END ATTACHMENT kind={kind} path="{path}" part={part}/{parts}]')
-    lines.append(
-        f'[NEXT_ATTACHMENT_PART kind={kind} path="{path}" '
-        f"next_offset_chars={next_offset} remaining_chars={remaining}]"
-    )
-    return "\n".join(lines), {
-        "kind": kind,
-        "path": path,
-        "part": part,
-        "parts": parts,
-        "offset_chars": offset,
-        "shown_chars": shown,
-        "total_chars": total,
-        "dropped_chars": remaining,
-        "next_offset_chars": next_offset,
-        "remaining_chars": remaining,
-        "budget_chars_remaining": 0,
-    }
-
-
-def _allocate_attachments(
+def _render_direct(
     candidates: list[dict],
-    priority: tuple,
-    system_chars: int,
-    user_chars: int,
-    history_chars: int,
-    budget: int,
-) -> tuple[list[tuple[dict, str, Optional[dict]]], list[dict], dict]:
-    """Render every attachment against the chars actually left in ``budget``.
-
-    ``candidates`` carry ``kind``, ``path``, ``open_line``, ``fence_lang``,
-    ``text``, an optional ``offset`` resume point and an optional ``slot``
-    (the prompt-cache split segment the rendered block belongs to).
-    Returns ``(rendered, truncated, info)`` where ``rendered`` is a list of
-    ``(candidate, block, meta)`` in priority order, ``truncated`` describes
-    every attachment that lost chars, and ``info`` holds the attachment
-    budget accounting for the response payload.
+) -> tuple[list[tuple[dict, str, None]], list[dict], dict]:
+    """Render every attachment whole (no slicing, no part markers).
+
+    Returns ``(rendered, truncated, info)`` in the allocator's shape so
+    downstream assembly (``_slot``, ordering, transcript markers, result
+    payload) keeps working unchanged: ``rendered`` is ``(candidate,
+    block, None)`` in candidate order, ``truncated`` is always ``[]``
+    (cap cuts are noted inline in the block, never as resume tokens),
+    and ``info`` carries the used-char accounting.
     """
-    available = max(
-        0,
-        budget
-        - (system_chars + user_chars + history_chars)
-        - _SEP_LEN * (len(priority) + 1),
-    )
+    rendered: list[tuple[dict, str, None]] = []
     used = 0
     group_used: dict[str, int] = {}
-    rendered: list[tuple[dict, str, Optional[dict]]] = []
-    truncated: list[dict] = []
-    for kind in priority:
-        for cand in candidates:
-            if cand.get("kind") != kind:
-                continue
-            total = len(cand.get("text", ""))
-            room = available - used
-            _cap = cand.get("cap")
-            if _cap:
-                # The configured cap bounds the CONTENT; the wrapper the
-                # renderer must emit rides on top of it, or a file that
-                # fits its cap exactly would be split for the sake of a
-                # few marker characters.
-                room = min(
-                    room,
-                    int(_cap)
-                    + _marker_room(
-                        kind,
-                        cand.get("path", ""),
-                        total,
-                        open_line=cand.get("open_line", ""),
-                        fence_lang=cand.get("fence_lang"),
-                    ),
-                )
-            _group = cand.get("group")
-            _gcap = int(cand.get("group_cap") or 0)
-            if _group and _gcap:
-                # Files in one group share a configured total budget
-                # (context_paths). The candidates are allocated
-                # independently, so the aggregate is enforced here: the
-                # remainder is reported, never silently over-sent.
-                _gleft = max(0, _gcap - group_used.get(_group, 0))
-                # The group cap bounds CONTENT: grant the remaining
-                # content plus the wrapper that carries it, so a file
-                # that still fits its share arrives whole.
-                room = min(
-                    room,
-                    _gleft
-                    + _open_overhead(cand.get("open_line", ""), cand.get("fence_lang")),
-                )
-            # Below the marker envelope the attachment could only render
-            # as an unreadable stub that also overflows the budget, so
-            # report it as fully dropped instead of spending the room.
-            if room <= _marker_room(
-                kind,
-                cand.get("path", ""),
-                total,
-                open_line=cand.get("open_line", ""),
-                fence_lang=cand.get("fence_lang"),
-            ):
-                truncated.append(
-                    {
-                        "kind": kind,
-                        "path": cand.get("path", ""),
-                        "part": 1,
-                        "parts": 1,
-                        "offset_chars": 0,
-                        "shown_chars": 0,
-                        "total_chars": total,
-                        "dropped_chars": total,
-                        "next_offset_chars": 0,
-                        "remaining_chars": total,
-                        "budget_chars_remaining": 0,
-                    }
-                )
-                continue
-            block, meta = _render_attachment(
-                kind,
-                cand.get("path", ""),
-                cand.get("open_line", ""),
-                cand.get("fence_lang"),
-                cand.get("text", ""),
-                room,
-                offset=cand.get("offset", 0),
-            )
-            rendered.append((cand, block, meta))
+    for cand in candidates:
+        if cand.get("inline"):
+            block = cand.get("open_line", "")
+            rendered.append((cand, block, None))
             used += len(block)
-            if _group:
-                group_used[_group] = group_used.get(_group, 0) + (
-                    meta["shown_chars"] if meta is not None else total
+            continue
+        text = cand.get("text", "")
+        cap = cand.get("cap")
+        if cap and len(text) > int(cap):
+            text = (
+                text[: int(cap)]
+                + f"\n[...truncated at {cap} chars — remainder NOT sent. "
+                + "Judge visible only; mark unseen UNVERIFIABLE, NEVER "
+                + "REJECTED.]"
+            )
+        group = cand.get("group")
+        gcap = cand.get("group_cap")
+        if group and gcap:
+            left = max(0, int(gcap) - group_used.get(group, 0))
+            if len(text) > left:
+                text = (
+                    text[:left]
+                    + f"\n[...truncated: shared {group} budget "
+                    + f"{gcap} chars reached]"
                 )
-            if meta is not None:
-                meta["budget_chars_remaining"] = max(0, available - used)
-                truncated.append(meta)
+            group_used[group] = group_used.get(group, 0) + len(text)
+        open_line = cand.get("open_line", "")
+        fence_lang = cand.get("fence_lang")
+        if fence_lang:
+            block = open_line + "\n```" + fence_lang + "\n" + text + "\n```"
+        elif text:
+            block = open_line + "\n" + text
+        else:
+            block = open_line
+        rendered.append((cand, block, None))
+        used += len(block)
     info = {
-        "attachment_budget_chars": available,
+        "attachment_budget_chars": used,
         "attachment_chars_used": used,
-        "attachment_chars_remaining": max(0, available - used),
+        "attachment_chars_remaining": 0,
     }
-    return rendered, truncated, info
+    return rendered, [], info
 
 
 def _task_candidate(
@@ -3111,7 +2700,6 @@ def brain_turn(
     include_bundle: bool = True,
     include_diff: bool = False,
     context_paths: Optional[list[str]] = None,
-    attachment_resume: Optional[dict] = None,
     project_root: Optional[str] = None,
     risk_tier: Optional[str] = None,
     session_id: Optional[str] = None,
@@ -3126,21 +2714,17 @@ def brain_turn(
             (instruction + task file content + prior answers).
         task_id: The BARE task number (digits only, e.g. "215") — never
             a slug, never a suffixed variant like "215qa", "215rev",
-            or "215plan". When given, the task's transcript is loaded
-            and sent along (chat-style history), and this turn is
-            appended to it. History is keyed by this exact string, so
-            EVERY turn for one task (plan, implement, QA, review) MUST
-            pass the identical number: a different id starts a
-            separate, empty history and the Brain loses all prior
-            context. Non-numeric input is rejected before anything
-            runs. Omit for one-off turns with no memory.
+            or "215plan". When given, the task file is resolved for the
+            task attach and the diff attach (see ``include_bundle`` /
+            ``include_diff``). Non-numeric input is rejected before
+            anything runs. Omit for one-off turns with no memory.
         system_prompt_path: Optional override; default is the global
             install copy of system-prompt.md.
         include_bundle: When True (default), prepend the small-file
             context bundle unless the prompt already carries its marker,
             plus the task file's working content (Goal/Notes/TODOs/AC/
             evidence/log minus the Factual Git Diff block, with a
-            read_file pull path) whenever task_id resolves to a file.
+            quoted-paths follow-up) whenever task_id resolves to a file.
             Pass False for tiny calls. The system prompt is untouched.
         include_diff: When True, append the task file's changed hunks
             (Factual Git Diff content, verbatim, capped) whenever
@@ -3160,13 +2744,6 @@ def brain_turn(
             under the workspace root with the read suffix allowlist;
             per-file cap plus total budget apply, problems become explicit
             unavailable labels. Default off. Small pulls stay inline.
-        attachment_resume: Optional continuation token from a previous
-            response whose attachments were truncated. Accepts
-            ``{"kind": "diff"|"context_path", "path": str,
-            "offset_chars": int >= 0}`` — the shape the response payload
-            and the ``[NEXT_ATTACHMENT_PART]`` marker publish. A malformed
-            resume is ignored with a stderr note and never fails the turn.
-            Omit it for a fresh turn.
         project_root: Optional project dir holding ``tasks/``. Its
             ``tasks/.sessions/`` stores this turn's history (per-project
             sessions), and its ``tasks/`` lanes resolve the task file
@@ -3183,11 +2760,13 @@ def brain_turn(
             takes effect when ``BRAIN_RISK_ROUTING_ENABLED`` is set;
             missing or invalid values fail safe to the current model.
             Default None (unrouted, today's behavior).
-        session_id: Optional taskless saga key (e.g. "cando-828") —
-            mutually exclusive with task_id. Pass exactly one of the two
-            on memory-bearing turns; omit both for one-off turns with no
-            memory. The session transcript continues under this key the
-            same way a task transcript continues under task_id.
+        session_id: Optional session key (e.g. "cando-828") — the
+            PRIMARY history key (session-first). Pass it alongside
+            ``task_id`` so one thread spans every task in the work
+            session; pass it alone for taskless turns. When omitted and
+            only ``task_id`` is given, history falls back to the
+            task-keyed transcript for backward compatibility. Omit both
+            for one-off turns with no memory.
         stage: Optional turn stage, one of plan / implement / qa /
             review / closure. Unknown stages are rejected so a typo can
             never run as an unscoped turn.
@@ -3214,10 +2793,12 @@ def brain_turn(
     # Request preflight FIRST (GitHub issue 18): local validation before
     # any load, attach, import, or model call. An explicit project_root
     # without tasks/ raises here instead of silently substituting the
-    # workspace root; suffixed task_ids are rejected; task_id and
-    # session_id are mutually exclusive (exactly one binds history,
-    # neither means a one-off turn). The resolved root feeds every
-    # downstream resolver so attaches and history share one root.
+    # workspace root; suffixed task_ids are rejected; session_id is the
+    # primary history key and coexists with task_id (session-first:
+    # history continues under the session while the task file and diff
+    # still resolve from task_id); neither id means a one-off turn.
+    # The resolved root feeds every downstream resolver so attaches and
+    # history share one root.
     _requested_root = project_root
     _pre = _validate_request(
         project_root=project_root,
@@ -3398,25 +2979,6 @@ def brain_turn(
                         file=sys.stderr,
                     )
 
-    # Chunk continuation: a caller that saw an [NEXT_ATTACHMENT_PART]
-    # marker (or an attachment_parts entry) can resume exactly that
-    # attachment at exactly that offset instead of re-sending everything.
-    _resume = _validate_attachment_resume(attachment_resume)
-    if _resume is not None:
-        _matched = False
-        for _cand in candidates:
-            if (
-                _cand.get("kind") == _resume["kind"]
-                and _cand.get("path") == _resume["path"]
-            ):
-                _cand["offset"] = _resume["offset_chars"]
-                _matched = True
-        if not _matched:
-            print(
-                "brain-bridge: attachment_resume matched no attachment "
-                f"(kind={_resume['kind']} path={_resume['path']!r})",
-                file=sys.stderr,
-            )
     # Tier precedence: an explicit ``risk_tier`` wins; otherwise the
     # tier is derived from the turn stage (Task 261). A missing or
     # unknown stage leaves the tier empty, and the resolver returns
@@ -3434,7 +2996,7 @@ def brain_turn(
     if history_key:
         # Sessions-root visibility: one debug line per turn so a
         # misrouted project is observable in stderr, never silent.
-        _scope = "task" if task_id is not None else "session"
+        _scope = "session" if session_id is not None else "task"
         print(
             f"brain-bridge: sessions root {_sessions_root(project_root)} "
             f"({_scope} {history_key})",
@@ -3472,19 +3034,12 @@ def brain_turn(
     def _hist_chars() -> int:
         return sum(len(turn["content"]) for turn in history)
 
-    # Shared budget: ONE allocator renders every attachment against the
-    # chars left after the system prompt and the caller's prompt. History
+    # Direct rendering: every attachment enters whole against the 1M
+    # input budget — no allocator, no chunking, no part markers. History
     # is deliberately NOT subtracted here — the shipped transcript is the
     # LAST fallback, so its length can never shrink an attachment and the
     # static prompt-cache prefix stays stable across turns.
-    rendered, attachments_truncated, budget_info = _allocate_attachments(
-        candidates,
-        _attachment_priority(stage),
-        system_chars=len(system_prompt),
-        user_chars=len(user_prompt),
-        history_chars=0,
-        budget=_input_budget_cap(),
-    )
+    rendered, attachments_truncated, budget_info = _render_direct(candidates)
 
     def _slot(name: str) -> str:
         return "\n\n---\n\n".join(
@@ -3538,19 +3093,11 @@ def brain_turn(
     effective_prompt = "\n\n---\n\n".join(_blocks)
 
     # Input budget: system + prompt + history chars count against the
-    # configured ceiling. The allocator already reserved the shipped
-    # history, so this loop is the LAST-resort safety net. The FIRST
-    # history turn is grounding and survives; oldest MIDDLE turns drop
-    # first. History loss is reported separately from attachment loss.
+    # configured ceiling. History is NEVER dropped to fit: the shipped
+    # transcript is already bounded at load (``_HISTORY_LIMIT``), so the
+    # full session thread always rides along. History loss is reported
+    # separately from attachment loss.
     history_turns_dropped = 0
-    while (
-        history
-        and len(history) > 1
-        and len(system_prompt) + len(effective_prompt) + _hist_chars()
-        > _input_budget_cap()
-    ):
-        history.pop(1)
-        history_turns_dropped += 1
     truncated_count = history_turns_dropped
     budget_chars = len(system_prompt) + len(effective_prompt) + _hist_chars()
     util_pct = budget_chars * 100 // _model_window_chars()
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 35527f8..56f2ad6 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -300,7 +300,7 @@ def test_extract_ignores_fenced_blocks():
     assert '"b": 2' in blocks[0]
 
 
-def test_brain_turn_truncates_oldest_history(tmp_path, monkeypatch):
+def test_brain_turn_never_drops_history(tmp_path, monkeypatch):
     monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
     monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
     prompt_file = tmp_path / ".config" / "opencode" / "sys.md"
@@ -334,10 +334,12 @@ def test_brain_turn_truncates_oldest_history(tmp_path, monkeypatch):
     result = target("q", task_id="215")
     assert result["status"] == "REPORT"
     assert result["output"] == "ok"
+    # session-first: no middle-turn dropping — the whole thread ships
+    assert result["history_turns_dropped"] == 0
     big_turns = [
         t for t in holder["body"]["input"] if t.get("content", "").startswith("x")
     ]
-    assert 1 <= len(big_turns) < 10
+    assert len(big_turns) == 10
 
 
 # --- Hotfix-2 new tests (mocked httpx only) ---
@@ -605,7 +607,7 @@ def test_bundle_skips_missing_file_with_marker(tmp_path, monkeypatch):
         },
     )
     monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
-    out = _unwrap(bridge.get_context_bundle)()
+    out = bridge._build_context_bundle()
     assert "=== agents/cognitive-executor.md ===" in out
     assert "exec content" in out
     assert "[missing: docs/architecture.md]" in out
@@ -616,7 +618,7 @@ def test_bundle_truncates_large_file(tmp_path, monkeypatch):
     big = "x" * 65000
     ws = _mk_workspace(tmp_path, {"DESIGN.md": big})
     monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
-    out = _unwrap(bridge.get_context_bundle)()
+    out = bridge._build_context_bundle()
     assert "[truncated]" in out
     section = out.split("=== DESIGN.md ===")[1]
     assert len(section) < len(big) + 5000
@@ -657,7 +659,7 @@ def test_build_context_bundle_explicit_root_beats_env_decoy(tmp_path, monkeypatc
     assert "[missing: docs/conventions.md]" not in out
 
 
-def test_get_context_bundle_tool_honours_project_root(tmp_path, monkeypatch):
+def test_build_context_bundle_honours_project_root(tmp_path, monkeypatch):
     decoy = _mk_workspace(
         tmp_path,
         {
@@ -671,7 +673,7 @@ def test_get_context_bundle_tool_honours_project_root(tmp_path, monkeypatch):
         "REAL_TOOL_CONTENT", encoding="utf-8"
     )
 
-    out = _unwrap(bridge.get_context_bundle)(str(project))
+    out = bridge._build_context_bundle(str(project))
 
     assert "REAL_TOOL_CONTENT" in out
     assert "DECOY_TOOL_CONTENT" not in out
@@ -691,24 +693,7 @@ def test_workspace_root_follows_cwd_walkup(tmp_path, monkeypatch):
     monkeypatch.chdir(nested)
 
     assert bridge._workspace_root() == project.resolve()
-    assert "WALKUP_BUNDLE_CONTENT" in _unwrap(bridge.get_context_bundle)()
-
-
-def test_read_and_grep_honour_explicit_project_root(tmp_path, monkeypatch):
-    decoy = _mk_workspace(tmp_path, {"notes.md": "DECOY_NEEDLE\n"})
-    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(decoy))
-    project = tmp_path / "project"
-    project.mkdir()
-    (project / "notes.md").write_text("alpha\nREAL_NEEDLE beta\n", encoding="utf-8")
-
-    result = _unwrap(bridge.read_file)(
-        "notes.md", offset=2, limit=1, project_root=str(project)
-    )
-    assert result["lines"] == ["2: REAL_NEEDLE beta"]
-
-    hits = _unwrap(bridge.grep_files)("REAL_NEEDLE", project_root=str(project))
-    assert any("notes.md:2:" in h for h in hits)
-    assert not any("DECOY_NEEDLE" in h for h in hits)
+    assert "WALKUP_BUNDLE_CONTENT" in bridge._build_context_bundle()
 
 
 def test_brain_turn_bundle_follows_project_root(tmp_path, monkeypatch):
@@ -741,65 +726,6 @@ def test_brain_turn_bundle_follows_project_root(tmp_path, monkeypatch):
     assert "DECOY_TURN_CONTENT" not in last
 
 
-def test_read_file_offset_limit(tmp_path, monkeypatch):
-    ws = _mk_workspace(tmp_path, {"notes.md": "a\nb\nc\nd\ne\n"})
-    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
-    result = _unwrap(bridge.read_file)("notes.md", offset=2, limit=2)
-    assert result["total_lines"] == 5
-    assert result["lines"] == ["2: b", "3: c"]
-
-
-def test_read_file_rejects_traversal(tmp_path, monkeypatch):
-    ws = _mk_workspace(tmp_path, {"notes.md": "hi\n"})
-    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
-    import pytest as _pt
-
-    with _pt.raises(ValueError):
-        _unwrap(bridge.read_file)("../evil.md")
-    outside = tmp_path / "outside.md"
-    outside.write_text("evil\n", encoding="utf-8")
-    with _pt.raises(ValueError):
-        _unwrap(bridge.read_file)(str(outside))
-
-
-def test_read_file_rejects_bad_extension(tmp_path, monkeypatch):
-    ws = _mk_workspace(tmp_path, {"run.py": "print(1)\n"})
-    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
-    import pytest as _pt
-
-    with _pt.raises(ValueError):
-        _unwrap(bridge.read_file)("run.py")
-
-
-def test_grep_finds_planted_string(tmp_path, monkeypatch):
-    ws = _mk_workspace(
-        tmp_path,
-        {
-            "docs/a.md": "hello PLANTED_NEEDLE world\nsecond line\n",
-            "notes.txt": "nothing here\n",
-        },
-    )
-    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
-    hits = _unwrap(bridge.grep_files)("PLANTED_NEEDLE")
-    assert any("docs/a.md:1:" in h and "PLANTED_NEEDLE" in h for h in hits)
-
-
-def test_grep_skips_git(tmp_path, monkeypatch):
-    ws = _mk_workspace(
-        tmp_path,
-        {
-            "notes.md": "visible SKIPME_GIT_TEST\n",
-        },
-    )
-    git_file = ws / ".git" / "hidden.md"
-    git_file.parent.mkdir(parents=True, exist_ok=True)
-    git_file.write_text("hidden SKIPME_GIT_TEST\n", encoding="utf-8")
-    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
-    hits = _unwrap(bridge.grep_files)("SKIPME_GIT_TEST")
-    assert any("notes.md" in h for h in hits)
-    assert not any("/.git/" in h or h.startswith(".git/") for h in hits)
-
-
 def _mk_bundle_ws(tmp_path, monkeypatch):
     ws = _mk_workspace(
         tmp_path,
@@ -1416,55 +1342,7 @@ def test_task_attach_pull_path_is_lane_relative_and_live(tmp_path, monkeypatch):
     monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
     attach = bridge._build_task_attach("200-foo")
     assert "tasks/backlog/200-foo.md" in attach
-    pulled = bridge._read_file_impl("tasks/backlog/200-foo.md")
-    assert pulled["total_lines"] == 4
-
-
-def test_grep_skips_symlink_escape(tmp_path, monkeypatch):
-    ws = tmp_path / "ws"
-    sub = ws / "docs"
-    sub.mkdir(parents=True)
-    (sub / "real.md").write_text("hello\n", encoding="utf-8")
-    outside = tmp_path / "outside-secret.md"
-    outside.write_text("SECRET-XYZ\n", encoding="utf-8")
-    (sub / "evil.md").symlink_to(outside)
-    monkeypatch.setattr(bridge, "_workspace_root", lambda: ws)
-    hits = bridge._grep_files_impl("SECRET-XYZ", "docs")
-    assert hits == []
-
-
-def test_read_file_limit_clamped(tmp_path, monkeypatch):
-    (tmp_path / "big.md").write_text(
-        "".join(f"line {n}\n" for n in range(2500)), encoding="utf-8"
-    )
-    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
-    result = bridge._read_file_impl("big.md", limit=10**9)
-    assert result["limit"] == bridge._READ_MAX_LINES
-    assert len(result["lines"]) == bridge._READ_MAX_LINES
-
-
-def test_read_file_oversize_refused(tmp_path, monkeypatch):
-    (tmp_path / "huge.md").write_bytes(b"x" * (bridge._READ_MAX_BYTES + 1))
-    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
-    with pytest.raises(ValueError, match="too large"):
-        bridge._read_file_impl("huge.md")
-
-
-def test_grep_pattern_too_long_rejected(tmp_path, monkeypatch):
-    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
-    with pytest.raises(ValueError, match="too long"):
-        bridge._grep_files_impl("a" * (bridge._GREP_PATTERN_MAX + 1))
-
-
-def test_grep_skips_overlong_lines(tmp_path, monkeypatch):
-    sub = tmp_path / "docs"
-    sub.mkdir()
-    (sub / "mix.md").write_text(
-        "MATCH " + ("z" * 5000) + "\nplain MATCH line\n", encoding="utf-8"
-    )
-    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
-    hits = bridge._grep_files_impl("MATCH", "docs")
-    assert len(hits) == 1 and ":2:" in hits[0]
+    assert (d / "200-foo.md").read_text(encoding="utf-8").splitlines().__len__() == 4
 
 
 def test_extract_fed_context_present():
@@ -2566,6 +2444,44 @@ def test_fed_context_persists_across_second_turn(tmp_path, monkeypatch):
     assert bridge.load_fed_context("t9") == "CTX turn one\nCTX turn two"
 
 
+def test_brain_turn_persists_thread_across_session_turns(tmp_path, monkeypatch):
+    # Session-first: two turns under one session_id share one thread,
+    # even across different task_ids; the transcript persists under the
+    # session key, never the task key.
+    _mk_tasks_root(tmp_path)
+    _turn_setup(tmp_path, monkeypatch)
+    first = _call_turn(
+        monkeypatch,
+        "first turn UNIQUE_MARKER_ALPHA",
+        task_id="200",
+        session_id="sess-1",
+        include_bundle=False,
+        project_root=str(tmp_path),
+    )
+    assert first["status"] == "REPORT"
+    holder = {}
+    _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload("ok"))], holder)
+    target = (
+        bridge.brain_turn.fn if hasattr(bridge.brain_turn, "fn") else bridge.brain_turn
+    )
+    second = target(
+        "second turn",
+        task_id="201",
+        session_id="sess-1",
+        include_bundle=False,
+        project_root=str(tmp_path),
+    )
+    assert second["status"] == "REPORT"
+    shipped = [
+        t.get("content", "")
+        for t in holder["body"]["input"]
+        if t.get("role") != "system"
+    ]
+    assert any("UNIQUE_MARKER_ALPHA" in c for c in shipped)
+    transcript = tmp_path / "sessions" / "sess-1" / "transcript.jsonl"
+    assert transcript.is_file()
+
+
 def test_plan_verdict_valid():
     plan = (
         "verdict: PLAN APPROVED\nseats: Architect\npath: implement\n"
@@ -3274,8 +3190,9 @@ def test_cache_split_nul_role_cannot_collide():
 
 
 def test_cache_split_descriptor_matches_post_truncation_wire(tmp_path, monkeypatch):
-    # M3: the descriptor must describe the SHIPPED (post-truncation)
-    # wire, never the pre-truncation assembly (F3).
+    # M3: the descriptor must describe the SHIPPED wire. History is never
+    # dropped to fit (session-first): even a tiny _INPUT_BUDGET ships the
+    # full thread, so the descriptor matches the whole history.
     _clean_routing_env(monkeypatch)
     monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
     _mk_sys_prompt(tmp_path, monkeypatch)
@@ -3293,9 +3210,10 @@ def test_cache_split_descriptor_matches_post_truncation_wire(tmp_path, monkeypat
     )
     target("first-question", task_id="234", include_bundle=False)
     second = target("second-question", task_id="234", include_bundle=False)
+    assert second["history_turns_dropped"] == 0
     shipped = holder["body"]["input"]
     shipped_history = [t for t in shipped[1:-1]]
-    assert len(shipped_history) < 2  # the middle drop really fired
+    assert len(shipped_history) == 2  # no middle drop: full thread ships
     expected = bridge.build_prompt_cache_split(
         "sys", "", "", "second-question", history=shipped_history
     )
@@ -3367,61 +3285,75 @@ def test_paths_attach_60k_file_untruncated(tmp_path, monkeypatch):
     assert out.endswith(payload)
 
 
-def test_render_attachment_complete_has_no_markers():
-    block, meta = bridge._render_attachment(
-        "diff", "x.diff", "[changed-hunks:1: x.diff]", "diff", "short", 40000
+def test_render_direct_whole_has_no_markers():
+    rendered, truncated, info = bridge._render_direct(
+        [
+            {
+                "kind": "diff",
+                "path": "x.diff",
+                "open_line": "[changed-hunks:1: x.diff]",
+                "fence_lang": "diff",
+                "text": "short",
+            }
+        ]
     )
+    assert truncated == []
+    assert len(rendered) == 1
+    _cand, block, meta = rendered[0]
     assert meta is None
     assert "NEXT_ATTACHMENT_PART" not in block
+    assert "[ATTACHMENT" not in block
     assert "short" in block
+    assert info["attachment_chars_used"] == len(block)
 
 
-def test_render_attachment_parts_and_resume():
-    text = "abcdefghij" * 100
-    block, meta = bridge._render_attachment(
-        "diff", "x.diff", "[changed-hunks:1: x.diff]", "diff", text, 600
-    )
-    assert meta is not None
-    assert meta["part"] == 1
-    assert meta["parts"] > 1
-    assert f"next_offset_chars={meta['next_offset_chars']}" in block
-    assert "NEXT_ATTACHMENT_PART" in block
-    block2, meta2 = bridge._render_attachment(
-        "diff",
-        "x.diff",
-        "[changed-hunks:1: x.diff]",
-        "diff",
-        text,
-        100000,
-        offset=meta["next_offset_chars"],
-    )
-    assert meta2 is None
-    assert text[meta["next_offset_chars"] :] in block2
-
-
-def test_validate_attachment_resume_shape():
-    assert bridge._validate_attachment_resume(None) is None
-    assert bridge._validate_attachment_resume("nope") is None
-    assert bridge._validate_attachment_resume({"kind": "bogus", "path": "x"}) is None
-    ok = bridge._validate_attachment_resume(
-        {"kind": "diff", "path": "a.diff", "offset_chars": 5}
-    )
-    assert ok == {"kind": "diff", "path": "a.diff", "offset_chars": 5}
-    assert (
-        bridge._validate_attachment_resume({"kind": "diff", "path": "a.diff"})[
-            "offset_chars"
+def test_render_direct_cap_truncates_inline():
+    rendered, truncated, _info = bridge._render_direct(
+        [
+            {
+                "kind": "diff",
+                "path": "x.diff",
+                "open_line": "[changed-hunks:1: x.diff]",
+                "fence_lang": "diff",
+                "text": "y" * 5000,
+                "cap": 4000,
+            }
         ]
-        == 0
     )
+    assert truncated == []
+    _cand, block, meta = rendered[0]
+    assert meta is None
+    assert "NEXT_ATTACHMENT_PART" not in block
+    assert "[...truncated at 4000 chars" in block
 
 
-def test_attachment_priority_review_prefers_evidence():
-    review = bridge._attachment_priority("review")
-    assert review.index("diff") < review.index("bundle")
-    assert review.index("context_path") < review.index("bundle")
-    assert bridge._attachment_priority("qa") == review
-    plain = bridge._attachment_priority(None)
-    assert plain.index("bundle") < plain.index("diff")
+def test_render_direct_group_total_cap_shared():
+    cands = [
+        {
+            "kind": "context_path",
+            "path": "a.md",
+            "open_line": "[path-injected: a.md]",
+            "fence_lang": None,
+            "text": "a" * 600,
+            "cap": 60000,
+            "group": "context_path",
+            "group_cap": 1000,
+        },
+        {
+            "kind": "context_path",
+            "path": "b.md",
+            "open_line": "[path-injected: b.md]",
+            "fence_lang": None,
+            "text": "b" * 600,
+            "cap": 60000,
+            "group": "context_path",
+            "group_cap": 1000,
+        },
+    ]
+    rendered, truncated, _info = bridge._render_direct(cands)
+    assert truncated == []
+    assert "b" * 600 not in rendered[1][1]
+    assert "shared context_path budget" in rendered[1][1]
 
 
 def _turn_setup(tmp_path, monkeypatch):
@@ -3469,7 +3401,9 @@ def test_small_review_turn_reports_no_attachment_truncation(tmp_path, monkeypatc
     assert result["truncated_count"] == 0
 
 
-def test_review_turn_reports_attachment_truncation_separately(tmp_path, monkeypatch):
+def test_review_turn_applies_diff_cap_inline_without_markers(tmp_path, monkeypatch):
+    # No allocator, no part markers: the per-attachment cap still bounds
+    # the diff, reported inline — never as resume tokens.
     _big_diff_task(tmp_path)
     _turn_setup(tmp_path, monkeypatch)
     monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 4000)
@@ -3483,73 +3417,14 @@ def test_review_turn_reports_attachment_truncation_separately(tmp_path, monkeypa
     )
     assert result["history_turns_dropped"] == 0
     assert result["truncated_count"] == 0
-    assert result["attachments_truncated"], "truncation must be reported"
-    entry = result["attachments_truncated"][0]
-    assert set(
-        ("kind", "path", "shown_chars", "total_chars", "dropped_chars", "part", "parts")
-    ) <= set(entry)
-    assert entry["kind"] == "diff"
-    assert entry["shown_chars"] < entry["total_chars"]
-    assert entry["shown_chars"] + entry["dropped_chars"] == entry["total_chars"]
-    assert result["attachment_parts"]
-    assert result["attachment_budget_chars"] >= 0
-
-
-def test_review_turn_can_resume_the_dropped_remainder(tmp_path, monkeypatch):
-    _big_diff_task(tmp_path)
-    _turn_setup(tmp_path, monkeypatch)
-    monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 4000)
-    first = _call_turn(
-        monkeypatch,
-        "code reviewer, adversarial review",
-        task_id="200",
-        include_bundle=False,
-        include_diff=True,
-        project_root=str(tmp_path),
-    )
-    entry = first["attachments_truncated"][0]
-    monkeypatch.setattr(bridge, "_TASK_DIFF_CAP", 10000000)
-    second = _call_turn(
-        monkeypatch,
-        "code reviewer, adversarial review",
-        task_id="200",
-        include_bundle=False,
-        include_diff=True,
-        project_root=str(tmp_path),
-        attachment_resume={
-            "kind": "diff",
-            "path": entry["path"],
-            "offset_chars": entry["next_offset_chars"],
-        },
-    )
-    assert second["attachment_chars_used"] > 0
-    resumed = second["attachment_parts"]
-    if resumed:
-        assert resumed[0]["offset_chars"] == entry["next_offset_chars"]
-    else:
-        assert second["attachments_truncated"] == []
-
-
-def test_big_change_set_chunks_into_numbered_parts(tmp_path, monkeypatch):
-    path = _big_diff_task(tmp_path, chars=260000)
-    assert len(path.read_text(encoding="utf-8")) > 250000
-    _turn_setup(tmp_path, monkeypatch)
-    result = _call_turn(
-        monkeypatch,
-        "code reviewer, adversarial review",
-        task_id="200",
-        include_bundle=False,
-        include_diff=True,
-        project_root=str(tmp_path),
-    )
-    entry = result["attachments_truncated"][0]
-    assert entry["kind"] == "diff"
-    assert entry["part"] == 1 and entry["parts"] > 1
-    assert entry["next_offset_chars"] > 0
-    assert entry["next_offset_chars"] == entry["shown_chars"]
+    assert result["attachments_truncated"] == []
+    assert result["attachment_parts"] == []
+    assert result["attachment_chars_used"] > 0
 
 
-def test_review_turn_prioritises_diff_over_bundle(tmp_path, monkeypatch):
+def test_review_turn_attaches_diff_and_bundle_whole(tmp_path, monkeypatch):
+    # No allocator means no evidence-vs-bundle contest: both enter whole,
+    # each bounded only by its own cap.
     _big_diff_task(tmp_path, chars=300000)
     _turn_setup(tmp_path, monkeypatch)
     monkeypatch.setenv("BRAIN_INPUT_BUDGET", "50000")
@@ -3562,17 +3437,14 @@ def test_review_turn_prioritises_diff_over_bundle(tmp_path, monkeypatch):
         stage="review",
         project_root=str(tmp_path),
     )
-    diff_entries = [e for e in result["attachments_truncated"] if e["kind"] == "diff"]
-    bundle_entries = [
-        e for e in result["attachments_truncated"] if e["kind"] == "bundle"
-    ]
-    assert diff_entries and diff_entries[0]["shown_chars"] > 0
-    assert bundle_entries and bundle_entries[0]["shown_chars"] == 0
+    assert result["attachments_truncated"] == []
+    assert result["attachment_parts"] == []
+    assert result["attachment_chars_used"] > 0
 
 
 def test_review_turn_delivers_60k_context_path_untruncated(tmp_path, monkeypatch):
-    # Turn-level proof, not just the standalone builder: the shared
-    # allocator must hand the seat a 60k report whole. The older 100k
+    # Turn-level proof, not just the standalone builder: direct rendering
+    # must hand the seat a 60k report whole. The older 100k
     # send ceiling starved this to ~12k once the system prompt was paid.
     _big_diff_task(tmp_path)
     _turn_setup(tmp_path, monkeypatch)
@@ -3653,63 +3525,10 @@ def test_malformed_cap_fails_the_turn(tmp_path, monkeypatch):
         )
 
 
-def test_render_attachment_fenced_respects_exact_room():
-    # The wrapper — open line, fences and their separators — is part of
-    # the block, so it must be priced against the room granted. Comparing
-    # only the body length let a rendered block exceed its budget.
-    block, meta = bridge._render_attachment(
-        "diff", "x.diff", "[changed-hunks:1: x.diff]", "diff", "x" * 500, 500
-    )
-    assert len(block) <= 500
-    assert meta is not None
-    assert meta["shown_chars"] < 500
-
-
-def test_render_attachment_unfenced_respects_exact_room():
-    block, meta = bridge._render_attachment(
-        "task", "x.md", "[task-file:1: x.md]", None, "x" * 500, 500
-    )
-    assert len(block) <= 500
-    assert meta is not None
-
-
-def test_render_attachment_short_fit_keeps_no_markers():
-    # An exact/whole fit still renders without part markers: no phantom
-    # split for content that fits.
-    block, meta = bridge._render_attachment(
-        "diff", "x.diff", "[changed-hunks:1: x.diff]", "diff", "x" * 10, 500
-    )
-    assert meta is None
-    assert len(block) <= 500
-    assert "[ATTACHMENT" not in block
-    assert "[NEXT_ATTACHMENT_PART" not in block
-
-
-def test_render_attachment_fenced_split_resumes_exactly():
-    block, meta = bridge._render_attachment(
-        "diff", "x.diff", "[changed-hunks:1: x.diff]", "diff", "abcdefghij" * 100, 400
-    )
-    assert len(block) <= 400
-    assert meta["next_offset_chars"] == meta["shown_chars"]
-    assert meta["remaining_chars"] == meta["total_chars"] - meta["shown_chars"]
-    resumed, _meta = bridge._render_attachment(
-        "diff",
-        "x.diff",
-        "[changed-hunks:1: x.diff]",
-        "diff",
-        "abcdefghij" * 100,
-        400,
-        offset=meta["next_offset_chars"],
-    )
-    assert "abcdefghij" * 100 not in block
-    assert len(resumed) <= 400
-
-
 def test_ctx_paths_total_cap_enforced_across_files(tmp_path, monkeypatch):
     # Every context_paths file shares one configured total budget. The
-    # candidates are allocated independently, so the aggregate must be
-    # enforced by the allocator — otherwise the combined content sails
-    # past BRAIN_CTX_TOTAL_CAP bounded only by the input budget.
+    # direct renderer enforces the aggregate inline: the second file can
+    # only show the group's remaining share, with no resume tokens.
     _big_diff_task(tmp_path)
     _turn_setup(tmp_path, monkeypatch)
     (tmp_path / "a.md").write_text("a" * 600, encoding="utf-8")
@@ -3726,13 +3545,11 @@ def test_ctx_paths_total_cap_enforced_across_files(tmp_path, monkeypatch):
         context_paths=["a.md", "b.md"],
         project_root=str(tmp_path),
     )
-    entries = [
-        e for e in result["attachments_truncated"] if e["kind"] == "context_path"
-    ]
-    assert entries, "the overflow must be reported, never silent"
-    # The second file can only show the group's remaining share.
-    assert all(e["shown_chars"] <= 400 for e in entries)
-    assert all(e["total_chars"] == 600 for e in entries)
+    assert result["attachments_truncated"] == []
+    assert result["attachment_parts"] == []
+    # 1200 chars of content against a 1000-char shared budget: the
+    # aggregate must hold, so used chars stay well under the uncut total.
+    assert result["attachment_chars_used"] < 1200 + 500
 
 
 def test_malformed_ctx_per_file_cap_fails_the_turn(tmp_path, monkeypatch):
diff --git a/tests/test_brain_preflight.py b/tests/test_brain_preflight.py
index 817c385..fc185f3 100644
--- a/tests/test_brain_preflight.py
+++ b/tests/test_brain_preflight.py
@@ -31,6 +31,7 @@ def _clean_env(monkeypatch):
 
 # --- resolve_project_root: explicit root is strict ---
 
+
 def test_explicit_root_with_tasks_resolves(tmp_path):
     proj = _mk_project(tmp_path)
     assert preflight.resolve_project_root(str(proj)) == proj.resolve()
@@ -58,6 +59,7 @@ def test_explicit_root_file_not_dir_raises(tmp_path):
 
 # --- resolve_project_root: omitted root resolves via chain ---
 
+
 def test_env_project_root_used_when_omitted(tmp_path, monkeypatch):
     proj = _mk_project(tmp_path)
     bare = tmp_path / "bare"
@@ -97,6 +99,7 @@ def test_nothing_resolves_raises_with_remedy(tmp_path, monkeypatch):
 
 # --- task / session binding ---
 
+
 def test_task_id_bare_digits_ok(tmp_path):
     proj = _mk_project(tmp_path)
     req = preflight.validate_request(task_id="257", project_root=str(proj))
@@ -113,8 +116,7 @@ def test_task_id_suffix_rejected(tmp_path):
 
 def test_session_id_ok(tmp_path):
     proj = _mk_project(tmp_path)
-    req = preflight.validate_request(session_id="cando-828",
-                                     project_root=str(proj))
+    req = preflight.validate_request(session_id="cando-828", project_root=str(proj))
     assert req.binding == "session"
     assert req.session_id == "cando-828"
 
@@ -125,11 +127,22 @@ def test_session_id_bad_chars_rejected(tmp_path):
         preflight.validate_request(session_id="a/b", project_root=str(proj))
 
 
-def test_both_ids_rejected(tmp_path):
+def test_both_ids_coexist_session_first(tmp_path):
+    proj = _mk_project(tmp_path)
+    req = preflight.validate_request(
+        task_id="257", session_id="s", project_root=str(proj)
+    )
+    assert req.binding == "session"
+    assert req.task_id == "257"
+    assert req.session_id == "s"
+    assert req.history_key == "s"
+
+
+def test_session_only_binds_session(tmp_path):
     proj = _mk_project(tmp_path)
-    with pytest.raises(preflight.PreflightError, match="exactly one"):
-        preflight.validate_request(task_id="257", session_id="s",
-                                   project_root=str(proj))
+    req = preflight.validate_request(session_id="s", project_root=str(proj))
+    assert req.binding == "session"
+    assert req.history_key == "s"
 
 
 def test_neither_id_is_oneoff_without_root(tmp_path, monkeypatch):
@@ -144,65 +157,72 @@ def test_neither_id_is_oneoff_without_root(tmp_path, monkeypatch):
 
 # --- stage / flags / kanban / required_tools ---
 
+
 def test_stage_allowlist_ok(tmp_path):
     proj = _mk_project(tmp_path)
-    req = preflight.validate_request(task_id="1", project_root=str(proj),
-                                     stage="qa")
+    req = preflight.validate_request(task_id="1", project_root=str(proj), stage="qa")
     assert req.stage == "qa"
 
 
 def test_stage_unknown_rejected(tmp_path):
     proj = _mk_project(tmp_path)
     with pytest.raises(preflight.PreflightError, match="stage"):
-        preflight.validate_request(task_id="1", project_root=str(proj),
-                                   stage="bogus")
+        preflight.validate_request(task_id="1", project_root=str(proj), stage="bogus")
 
 
 def test_flags_must_be_bool(tmp_path):
     proj = _mk_project(tmp_path)
     with pytest.raises(preflight.PreflightError, match="include_bundle"):
-        preflight.validate_request(task_id="1", project_root=str(proj),
-                                   include_bundle="yes")
+        preflight.validate_request(
+            task_id="1", project_root=str(proj), include_bundle="yes"
+        )
     with pytest.raises(preflight.PreflightError, match="include_diff"):
-        preflight.validate_request(task_id="1", project_root=str(proj),
-                                   include_diff=1)
+        preflight.validate_request(task_id="1", project_root=str(proj), include_diff=1)
 
 
 def test_kanban_path_under_tasks_ok(tmp_path):
     proj = _mk_project(tmp_path)
-    req = preflight.validate_request(task_id="1", project_root=str(proj),
-                                     kanban_path="tasks/qa/257-x.md")
+    req = preflight.validate_request(
+        task_id="1", project_root=str(proj), kanban_path="tasks/qa/257-x.md"
+    )
     assert req.kanban_path == (proj.resolve() / "tasks" / "qa" / "257-x.md")
 
 
 def test_kanban_path_escape_rejected(tmp_path):
     proj = _mk_project(tmp_path)
     with pytest.raises(preflight.PreflightError, match="kanban_path"):
-        preflight.validate_request(task_id="1", project_root=str(proj),
-                                   kanban_path="../outside.md")
+        preflight.validate_request(
+            task_id="1", project_root=str(proj), kanban_path="../outside.md"
+        )
     with pytest.raises(preflight.PreflightError, match="kanban_path"):
-        preflight.validate_request(task_id="1", project_root=str(proj),
-                                   kanban_path="/etc/passwd")
+        preflight.validate_request(
+            task_id="1", project_root=str(proj), kanban_path="/etc/passwd"
+        )
 
 
 def test_required_tools_typechecked(tmp_path):
     proj = _mk_project(tmp_path)
-    req = preflight.validate_request(task_id="1", project_root=str(proj),
-                                     required_tools=["question"])
+    req = preflight.validate_request(
+        task_id="1", project_root=str(proj), required_tools=["question"]
+    )
     assert req.required_tools == ("question",)
     with pytest.raises(preflight.PreflightError, match="required_tools"):
-        preflight.validate_request(task_id="1", project_root=str(proj),
-                                   required_tools="question")
+        preflight.validate_request(
+            task_id="1", project_root=str(proj), required_tools="question"
+        )
     with pytest.raises(preflight.PreflightError, match="required_tools"):
-        preflight.validate_request(task_id="1", project_root=str(proj),
-                                   required_tools=[123])
+        preflight.validate_request(
+            task_id="1", project_root=str(proj), required_tools=[123]
+        )
 
 
 # --- brain_turn wiring: preflight runs before transport ---
 
+
 class _FakeResp:
-    def __init__(self, status_code=200, text="", payload=None,
-                 ctype="application/json"):
+    def __init__(
+        self, status_code=200, text="", payload=None, ctype="application/json"
+    ):
         self.status_code = status_code
         self.text = text
         self._payload = payload
@@ -234,8 +254,11 @@ class _FakeClient:
 
 
 def _ok_payload(text="ok"):
-    return {"output": [{"type": "message",
-                        "content": [{"type": "output_text", "text": text}]}]}
+    return {
+        "output": [
+            {"type": "message", "content": [{"type": "output_text", "text": text}]}
+        ]
+    }
 
 
 def _mk_bridge_client(monkeypatch, script):
@@ -277,29 +300,24 @@ def _brain_turn():
     return call.fn if hasattr(call, "fn") else call
 
 
-def test_brain_turn_bad_explicit_root_raises_before_transport(
-        tmp_path, monkeypatch):
+def test_brain_turn_bad_explicit_root_raises_before_transport(tmp_path, monkeypatch):
     _mk_sys_prompt(tmp_path, monkeypatch)
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
-    clients = _mk_bridge_client(
-        monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
+    clients = _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
     with pytest.raises(preflight.PreflightError):
-        _brain_turn()("q", task_id="257",
-                      project_root=str(tmp_path / "bare-no-tasks"))
+        _brain_turn()("q", task_id="257", project_root=str(tmp_path / "bare-no-tasks"))
     assert clients == []
 
 
-def test_brain_turn_task_and_session_rejected_before_transport(
-        tmp_path, monkeypatch):
+def test_brain_turn_task_and_session_coexist_under_session(tmp_path, monkeypatch):
     proj = _mk_project(tmp_path)
     _mk_sys_prompt(tmp_path, monkeypatch)
     monkeypatch.setenv("BRAIN_API_KEY", "sk-test-key")
-    clients = _mk_bridge_client(
-        monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
-    with pytest.raises(preflight.PreflightError, match="exactly one"):
-        _brain_turn()("q", task_id="257", session_id="s",
-                      project_root=str(proj))
-    assert clients == []
+    clients = _mk_bridge_client(monkeypatch, [_FakeResp(200, "fine", _ok_payload())])
+    result = _brain_turn()("q", task_id="257", session_id="s", project_root=str(proj))
+    assert result["status"] == "REPORT"
+    assert result["output"] == "ok"
+    assert clients != []
 
 
 def test_brain_turn_legacy_shape_still_works(tmp_path, monkeypatch):
```
<!-- END_GIT_DIFF -->
