# Task 174: Add missing persona slash commands and remove brainstorm-swarm skill

**File:** `tasks/completed/174-persona-commands-and-remove-brainstorm-skill.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Create the five missing persona slash commands (architect, designer, programmer, planner, strategist) from the seven personas defined in `prompts/fragments/06-personas.md`, and delete the `skill-templates/brainstorm-swarm/` skill (superseded by the Brainstorm Facilitator persona turn + `<brainstorming_protocol>` fragment 12), updating every live reference.

## Manager's Notes

- Verbatim manager order: "create missing persona and thier commands base on @system-prompt.md and also remove @skill-templates/brainstorm-swarm/ skill becuase we have a persona no skill needed".
- Pipeline: "create task file then implemment then pass it to qa and then reviewer and finnaly ask me inside telegram". Then: "create a goal and follow until end" (goal active: Task 174 full pipeline through Telegram approval).
- The six-persona swarm scheme MUST survive: it lives in `prompts/fragments/12-brainstorming_protocol.md` and is injected into every persona turn via `system-prompt.md`. Only the skill-template wrapper + registry entries go.
- History files (`CHANGELOG.md` old entries, `tasks/archive/*`, `.opencode/memory/*`, `docs/history/*`) are immutable records — do NOT rewrite history, only append the new CHANGELOG entry.
- `system-prompt.md` is a generated artifact: edit `prompts/fragments/07-agent_skills_registry.md`, rebuild via `scripts/prompt-build/assemble_system_prompt.py`, bump `<system_version>` 9.9.0 → 9.10.0, verify with `lint_system_prompt_sync`.
- ZAC applies: no `git add`/`commit`/`push`; stage via `custom_context_stage_and_inject_diff`; `git mv` only for Kanban moves; skill deletion via filesystem `rm` (untracked files need no git mv).

## Local TODOs

- [ ] New commands: `.opencode/commands/{architect,designer,programmer,planner,strategist}.md` following `qa.md` dispatch pattern with exact persona names from 06-personas.md
- [ ] Update `.opencode/commands/brainstorm.md`: drop skill-load step, dispatch "Brainstorm Facilitator" relying on `<brainstorming_protocol>` in the system prompt
- [ ] Delete `skill-templates/brainstorm-swarm/` and global `~/.config/opencode/skills/brainstorm-swarm/`; remove line 229 tree entry in README.md
- [ ] Edit fragment 07 registry (remove brainstorm-swarm line), rebuild system-prompt.md, bump version to 9.10.0, sync-check clean
- [ ] Update `agents/cognitive-executor.md` command list (9 commands, no skill mention)
- [ ] Update `mcp-persona-server/server.py` dispatch docstring (no skill-first instruction); run pytest green
- [ ] CHANGELOG entry, execution log, lint_task_file, stage + inject diff, QA transition
- [x] QA persona turn → fixes → reviewer turn → Telegram approval gate → closure on approve
- [x] Fix 1 (persona persistence): `SESSIONS_ROOT` pinned under install root; per-task persona identity card (`load/save_persona_card`) injected every turn
- [x] Fix 2 (context protocol): `<hands_context_request>` lane (`CONTEXT_REQUEST`) + planner/architect re-dispatch loops via MCP discovery tools
- [x] Fix 3 (bottlenecks): split gate (`open_approval_gate`/`poll_approval_gate`), stage slug under 64-byte callback cap, `PERSONA_MAX_REPLAY_TURNS` cap (default 50)
- [x] Fix 4 (full prompt): lineage fallback chain (repo → cwd → global config) + stderr warning on missing files

## Acceptance Criteria

- [x] `/architect`, `/designer`, `/programmer`, `/planner`, `/strategist` command files exist and dispatch the exact persona names `Software Architect`, `UI/UX Designer`, `Senior Programmer`, `Project Planner`, `Sprint Strategist`
- [x] `/brainstorm` works without the skill (no skill-load step; references `<brainstorming_protocol>`)
- [x] Zero live references to `brainstorm-swarm` outside immutable history (grep proves: only CHANGELOG history, tasks/archive, .opencode/memory, docs/history, context-reports snapshots remain)
- [x] `lint_system_prompt_sync` reports in-sync at version 9.10.0
- [x] Full pytest suite green (120+ tests)
- [x] QA_PASSED → reviewer APPROVED → Telegram `approve` received (callback `approve:174:174-closure` pressed overnight by Mohammad Reza, consumed via offset drain 2026-09-09; queue verified empty)
- [x] Persona card persists across turns (`turn_count`, `last_status`, open question carried/cleared correctly)
- [x] `CONTEXT_REQUEST` classified with `scope`/`focus` payload; malformed blocks fall through; XML lane never claims them
- [x] Split gate posts without waiting and polls to `decided`; stage slugs keep every `callback_data` under 64 bytes
- [x] Lineage resolves from global fallback when repo/cwd lack files; missing `AGENTS.md` warns on stderr
- [x] Full pytest suite green (138 tests)

## Verification Evidence

- **Test command:** `python -m pytest tests/ -q` + `grep -rn "brainstorm-swarm" --include="*.md" --include="*.py" . | grep -v -e CHANGELOG -e tasks/archive -e .opencode/memory -e docs/history -e tasks/qa -e tasks/in-progress`
- **Expected result:** all tests pass; grep returns zero live matches
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Deleting the skill breaks `/brainstorm` consumers that preload swarm context; version bump without rebuild causes sync drift.
- **Rollback plan:** Skill template restorable from git history (`git log --all -- skill-templates/brainstorm-swarm/`); global copy resyncable from repo; system-prompt.md rebuildable from fragments at 9.9.0.

---

## Execution Log & Reasoning

**Implementation (Hands):**

- **Validation first:** read `AGENTS.md`, `docs/conventions.md`, `prompts/fragments/06-personas.md` (7 personas confirmed: Software Architect, UI/UX Designer, Senior Programmer, Project Planner, Sprint Strategist, QA Engineer, Code Reviewer). `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md` absent → skipped per Absent-File Policy. Existing commands were only `qa/reviewer/manager/brainstorm` → 5 genuinely missing. `task-generator` skill loaded; goal active (Task 174 pipeline); ID 174 confirmed (no dup, no collision).
- **Key design finding:** the six-expert swarm scheme lives in `prompts/fragments/12-brainstorming_protocol.md`, which rides inside every `dispatch_session_turn` via `system-prompt.md` — so deleting the skill loses zero capability, exactly as the Manager asserted. `persona_name` is free-form in `server.py` (no allowlist), so `Brainstorm Facilitator` keeps working with no skill preload.
- **New files:** `.opencode/commands/{architect,designer,programmer,planner,strategist}.md` — same Dual-Dispatch skeleton as `qa.md`, each with persona-specific REPORT guidance (Discovery-First, a11y/environmental checklist, Anti-Hack STOP, Kanban source-of-truth, MoSCoW/WIP pushback-is-a-pass).
- **Skill removal:** `rm -rf skill-templates/brainstorm-swarm ~/.config/opencode/skills/brainstorm-swarm` (31 template skills remain). `.opencode/commands/brainstorm.md` rewritten: skill-load step gone, pure persona turn referencing `<brainstorming_protocol>`.
- **Reference updates:** fragment `07-agent_skills_registry.md` (line dropped) → rebuilt `system-prompt.md` via `scripts/prompt-build/assemble_system_prompt.py` (75,396 bytes) → `lint_system_prompt_sync` clean; version `01-system_version.md` 9.9.0 → 9.10.0. `agents/cognitive-executor.md` command list → 9 commands. `mcp-persona-server/server.py` docstring (doc-only change). `README.md` tree pruned.
- **History discipline:** old CHANGELOG entries, `tasks/archive/*`, `.opencode/memory/*`, `docs/history/*`, and `context-reports/*` (timestamped generated snapshots) intentionally untouched — grep exclusion covers them as immutable records.
- **Test runner note:** no `pytest` binary in system python or any `uv --project` env; working command used: `uv run --project mcp-persona-server --with pytest --with pathspec pytest tests/ -q` → **120 passed**.
- **Pre-existing quirk noticed (not fixed, out of scope):** `CHANGELOG.md` already contains a released `## [9.10.0] - 2026-09-04` section while `<system_version>` was 9.9.0 until this task — release tags and prompt versions have diverged before; left alone.

**QA round 1 (QA_REJECTED) — triage + fixes (Hands):**

- **V1 (diff contamination) — ACCEPTED, fixed.** The staged Factual Git Diff swept in Task 173's orphaned staged changes (memory workflow edit, `LLM.txt` §7.7, README plugin block, CHANGELOG 173 bullet) that predated Task 174 in the working tree. Fix: saved the full 4-file orphan diff to `/tmp/task173-orphan-changes.patch` (98 lines — 173's text survives; its staged task file `tasks/qa/173-*.md` also retains its own diff block); `git reset --` unstaged all 4 files (unstage-only, no worktree loss); surgically removed ONLY the 173 hunks from `README.md` + `CHANGELOG.md` worktree (174 hunks kept). `LLM.txt` + memory workflow remain modified-but-unstaged in the worktree for Task 173's own closure. **Flag to Manager:** Task 173's docs changes are orphaned-unstaged; its closure must re-stage them (its task-file diff block is now stale by exactly those hunks).
- **V2 (grep scope) — ACCEPTED, fixed (M1).** Full file-type sweep `grep -rn brainstorm-swarm|brainstorm_swarm . --exclude-dir=.git,__pycache__,.venv,node_modules` excluding immutable records: the ONLY non-history hit is `tasks/.sessions/174/transcript.jsonl` (gitignored runtime audit trail quoting the QA instruction itself — expected). Live-config sweep (`--exclude=*.md --exclude=*.py`, all json/txt/yaml/toml/sh): CLEAN. `CHANGELOG.md` hits = line 33 (this task's own removal entry) + lines 203/574/579 (old immutable history). AC3 now proven.
- **V3 (force_xml) — DISPUTED with evidence (M2).** `mcp-persona-server/server.py:141` declares `force_xml: bool = False` with handling at lines 160/169/200-208 — the `programmer.md` suggestion ("consider `force_xml=true`") targets a real parameter; no patch needed, no unknown-kwarg risk.
- **M3:** `ls -d ~/.config/opencode/skills/brainstorm-swarm` → "No such file or directory" — global removal proven.

**QA round 1 follow-up verification (Hands, pre re-audit):**
- **V1 refined — staged set proven 174-only.** `git diff --cached --stat` + full staged hunks for `README.md`/`CHANGELOG.md` inspected: staged CHANGELOG = exactly the 2×174 hunks (Added commands entry + Removed skill entry), staged README = exactly the 174 tree prune (2 lines). QA's README/CHANGELOG contamination claim described the pre-fix state — already eliminated by the worktree surgery. Remaining scope leak was structural: pre-existing staged `tasks/qa/173-*.md` (not mine, staged during 173's own pipeline) — `git reset --` unstaged it (now untracked, content fully preserved on disk; 173 re-stages at its own closure). `/tmp/task173-orphan-changes.patch` verified present (12,486 bytes) holding 173's README/CHANGELOG hunks. **Flag to Manager (updated):** 173's closure must re-apply that patch + re-stage `LLM.txt`, memory workflow, and its task file.
- **V2 re-verified broader (round 3).** `grep -rln brainstorm-swarm|brainstorm_swarm` over py/md/json/jsonc/txt/yaml/yml/sh excluding archive/history/context-reports/sessions/174-file/memory/CHANGELOG → exit 1, **zero hits**. AC3 proven without needing the transcript carve-out.
- **V3 double-disproved.** QA claimed (a) "no such parameter" — false (`server.py:141` + doc 169 + enforcement 200-208); (b) "log claims commands pass force_xml=True" — false (log documents a *suggestion* in `programmer.md` REPORT guidance: "consider `force_xml=true` when a bare report is not actionable"; commands pass no kwargs — they are markdown instructions, and the suggestion targets a real tool parameter).

## Verification Evidence (recorded)

- **Test command:** `uv run --project mcp-persona-server --with pytest --with pathspec pytest tests/ -q`
- **Expected result:** 120 passed
- **Actual result:** `120 passed, 8 warnings in 1.98s`
- **Exit code:** 0
- **Sync check:** `lint_system_prompt_sync` → in-sync at 9.10.0
- **Live-reference grep (round 1, md/py only):** SUPERSEDED by M1 below
- **M1 comprehensive grep (round 2):** all file types, immutable records excluded → sole non-history hit is the gitignored `tasks/.sessions/174/transcript.jsonl` (quotes the QA instruction itself); live json/txt/yaml/toml/sh sweep CLEAN; CHANGELOG hits = line 33 (own 174 entry) + history lines 203/574/579
- **M2 force_xml check:** real param at `server.py:141` (+160/169/200-208); `programmer.md` suggestion valid
- **M3 global removal:** `ls -d ~/.config/opencode/skills/brainstorm-swarm` → No such file or directory
- **Block-forensics lesson (stage-tool false alarm):** naive `split('BEGIN')` verification showed 4 files + duplicate END markers — artifact, NOT corruption: `planner.md`'s hunk legitimately contains the literal text `BEGIN/END_GIT_DIFF`, and the stage tool's greedy `BEGIN..LAST-END` regex (`server.py:543`) handles exactly this. Correct verification: split on FIRST `BEGIN_GIT_DIFF` and cut at LAST `END_GIT_DIFF` (rfind) → 14/14 files, sole `LLM.txt` hit = Task 164 §7.8 history context line (space-prefixed, unmodified). Retry = byte-identical output (tool deterministic). Rule: never Naively grep/count markers inside an injected block — always rfind-anchor.
- **Extension test run (Task 174 scope growth, manager order 2026-09-09):** `138 passed, 8 warnings` — exit 0 (18 new tests total).

**Telegram gate (pending manager):** gate keyboard posted (`approve:174:174-closure`, message 58, slug-format wire-compatible with the new split gate); no press yet (manager asleep). Closure (commit via `custom_context_commit_and_clean_task`) strictly on `approve`.

**Reviewer (Code Reviewer) — APPROVED.** Evidence-pack pattern (compact greps, /tmp pack as task context — full task file exceeds persona delivery): ZAC/secrets CLEAN, WHEN TO CALL all 6 tools, version 9.10.0 single pin, blank-unset on all 6 env reads, brainstorm-swarm zero live refs (sole hit = self-referential test string). Nit (non-blocking): reviewer counted 20 defs vs declared 18 net-new — reconciled: 18 new defs + baseline 120 = 138 exact (the 2 extra lines in its window were pre-existing trailing tests). No doc change needed.

**QA round 4 on half-2 (QA_REJECTED → all fixed, Hands):**

- **Prefix collision (high) — FIXED.** `_wait_for_update` now exact-matches `data == approve/reject+prefix` (substring removed); test: awaiting `:174:planning` skips `approve:174:planning-review`, resolves `reject:174:planning`.
- **Slug collision (high) — FIXED.** `slugify_stage`: short (≤32) unchanged; long → `base[:25]-sha1[:6]`; degenerate → `gate-sha1[:6]`. Tests: shared-prefix siblings differ, `''` vs `'!!!'` differ.
- **Assert-in-production (medium) — FIXED.** Explicit `ValueError` on encoded bytes > 64; `post_approval_gate` catches `(RuntimeError, ValueError)`.
- **Pin-import-cycle (medium) — DISPUTED.** `REPO_ROOT` derives from `__file__` (never CWD), no session→server cycle, idempotent re-pin, monkeypatch hygiene — QA conceded PASS on re-verdict.
- **Truncation marker (low→residual→FIXED).** `[:1990]` overshot (1990+12=2002); now `[:2000-len(marker)]` + boundary test (3000-char question → exactly ≤2000, endswith marker). QA confirmed the math; U+2026 byte-identical in code+test (verified); guard `len<=2000` deterministic at boundary.
- **Self-caught in half-2 diff review (Hands):** first refactor passed pre-formatted text into `post_approval_gate` (double header) — fixed to raw summary + regression test (header count==1).

**QA round 3 on the extension (QA_REJECTED → triaged, Hands):**
- **Blocking-1 (no dispatch wiring) — FALSE POSITIVE with evidence.** QA received an abridged paste (server.py hunk omitted by the Hands to save tokens). Real code: `server.py:235` calls `extract_context_request(output)` and returns `CONTEXT_REQUEST`; `XML_BLOCK_RE` (`dual_dispatch.py:29`, `<(hands_[a-z_]+_task|failure_report)>`) cannot match `<hands_context_request>` (`_request` ≠ `_task`), so the XML-first order is safe. Lesson: never abridge evidence for QA — resend full verbatim hunks.
- **Blocking-2 (bare `path` in load) — FALSE POSITIVE with evidence.** Real `session.py` assigns `path = persona_card_path(...)` first (grep proves, lines 211/252); the paste condensation dropped it. Lesson stands (same as above).
- **Advisory fixes ACCEPTED + implemented:** (a) present-but-empty lineage files no longer warn "not found" (`_read_lineage_file` returns found-flag; repo-empty shadows global instead of falling through); (b) card writes are atomic (tmp + `os.replace`); torn-write resets impossible; (c) context nudge stands down after a CONTEXT_REQUEST turn ("proceed with planning on that evidence") — kills the infinite re-request loop. Race-lock (fcntl) declined: single Hands process, atomic writes suffice; corrupt-JSON default fallback kept as audit resilience.
- **Test-hygiene bug caught by the suite (Hands):** the sessions-pin test permanently repointed the module-scoped fixture at the real repo dir → later turn-count assertions failed in-suite but passed solo. Fixed with `monkeypatch.setattr` (auto-restore) + removed stray `tasks/.sessions/18{6,7,8}` residue. Rule: module-scoped fixtures are never mutated directly.

**Extension — manager-ordered persona fixes (2026-09-09, "fix automatically, I want to sleep", same file, no new task):**

- **Fix 1 (persona dies when litellm finishes) — root cause + fix.** Each turn rebuilt the persona from a bare name: `SESSIONS_ROOT` was cwd-relative at import (`session.py:28`) and never pinned, so session memory scattered with launch cwd; no durable identity existed between calls. Fix: `server.py::_pin_sessions_root()` resolves the transcript root under `REPO_ROOT` when still relative (absolute `PERSONA_SESSIONS_DIR`/test overrides respected); new `persona_card_path/load/save_persona_card` (`session.py`) keeps per-task identity (`turn_count`, `last_status`, open question — set on QUESTION, cleared on decisive outcomes); the card is injected as a system message on every turn (`build_persona_messages` step 2b), so the persona EXISTS across calls.
- **Fix 2 (planner/architect context requests) — new lane.** `dual_dispatch.extract_context_request()` parses `<hands_context_request><scope>/<focus>` (malformed → falls through; `XML_BLOCK_RE` deliberately untouched so requests never enter the execution lane); `dispatch_session_turn` returns `CONTEXT_REQUEST` with the payload; `planner.md` + `architect.md` + executor Dual-Dispatch docs now prescribe the loop: MCP discovery tools (`get_directory_tree` → `extract_signatures` → `read_source_files`) then re-dispatch with the report path. The card brief also nudges personas to emit the block instead of guessing.
- **Fix 3 (loop bottlenecks) — verified + fixed three.** (a) Gate wait (1800s) vs MCP tool timeout (~600s): waiter always killed, press lands unconsumed — split into `post_approval_gate` (send-only) + `await_gate_decision` (short re-callable windows, resume offsets), exposed as `open_approval_gate`/`poll_approval_gate`; blocking `request_admin_approval` kept as legacy. (b) 64-byte `callback_data` cap (tonight's HTTP 400): `slugify_stage()` rides the buttons, full stage text stays in the message; keyboard asserts the cap. (c) Unbounded replay: `PERSONA_MAX_REPLAY_TURNS` (default 50) with an omission marker; JSONL audit trail keeps everything.
- **Fix 4 (every persona sees the entire system prompt) — root cause + fix.** Lineage resolved only against `repo_root`; global installs (`~/.config/opencode`) ship `system-prompt.md` but NO `AGENTS.md` and NO `prompts/` dir, and misses were silent → blind personas. Fix: `_lineage_search_roots()` (repo → cwd → global config, deduped) + `_warn_missing_lineage()` to stderr naming every absent file. Residual manager action (not code): global syncs must also ship `AGENTS.md` + `prompts/fragments/06-personas.md`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index d94c413..418307f 100644
--- a/.env.example
+++ b/.env.example
@@ -23,6 +23,9 @@ DECISION_TEMPERATURE=1.0
 # reasoning on complex tasks — tune thinking level instead).
 PERSONA_TEMPERATURE=1.0
 PERSONA_MAX_TOKENS=16384
+# Transcript replay bound: newest N turns re-sent per persona call (default 50;
+# blank = default). Older turns stay in the JSONL audit trail.
+PERSONA_MAX_REPLAY_TURNS=50
 
 # Decision Learning Store — per-project notes live in <project>/.opencode/decisions
 # (auto-resolved, no setting needed). Uncomment to override with an absolute path.
diff --git a/.opencode/commands/architect.md b/.opencode/commands/architect.md
new file mode 100644
index 0000000..b75aaa1
--- /dev/null
+++ b/.opencode/commands/architect.md
@@ -0,0 +1,33 @@
+---
+description: Dispatch the Software Architect persona on the active task for system design
+---
+
+# /architect — Software Architect persona turn
+
+Invoke `dispatch_session_turn` (persona MCP server) with:
+
+- `persona_name`: `"Software Architect"`
+- `instruction`: the text following `/architect` (design target, requirements, constraints), plus the active task file body as user context
+- `task_id`: the active task number
+- `task_file_path`: the active task file path
+
+The persona holds the full system prompt, repo rules, and cumulative task
+history. Its reply is Dual-Dispatch classified:
+
+- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
+- `CONTEXT_REQUEST` — the persona refuses to roadmap from assumptions: its
+  `context_request` carries `scope` (where to look) and `focus` (what to
+  find). Run the MCP discovery tools (`custom_context_get_directory_tree`,
+  then `custom_context_extract_signatures`, then
+  `custom_context_read_source_files` on the narrowed files), then
+  re-dispatch with the generated report path as the instruction
+  (Discovery-First Mandate — satisfied with evidence, not a blank request)
+- `QUESTION` — the persona needs missing context: answer and re-dispatch
+- `REPORT` — free-form design findings: a blueprint is only final once the
+  persona has factual codebase context (Discovery-First Mandate — never let
+  it roadmap from assumptions; request a Discovery Task when context is
+  empty)
+
+Wait for the turn result before continuing the pipeline. Never treat a
+`QUESTION` as a pass. STOP and wait for Manager approval before code
+generation begins.
diff --git a/.opencode/commands/brainstorm.md b/.opencode/commands/brainstorm.md
index cf41c5b..ec8a9fa 100644
--- a/.opencode/commands/brainstorm.md
+++ b/.opencode/commands/brainstorm.md
@@ -2,17 +2,19 @@
 description: Run a multi-persona brainstorming swarm turn on the active topic
 ---
 
-# /brainstorm — brainstorm-swarm session turn
+# /brainstorm — Brainstorm Facilitator persona turn
 
-1. Load the `brainstorm-swarm` skill (six personas: system_architect,
-   security_engineer, product_manager, business_strategist, legal_advisor,
-   critical_thinker).
-2. Invoke `dispatch_session_turn` (persona MCP server) with:
-   - `persona_name`: `"Brainstorm Facilitator"`
-   - `instruction`: the text following `/brainstorm` (the ambiguous topic or
-     decision to resolve), plus the active task file body as user context
-   - `task_id`: the active task number (or `0` for topic-only sessions)
-   - `task_file_path`: the active task file path when available
-3. Classify the reply per Dual Dispatch (`XML_EXTRACTED` / `QUESTION` /
-   `REPORT`). A `REPORT` here is the structured swarm session output:
-   persist its decisions as task constraints, not as implementation.
+Invoke `dispatch_session_turn` (persona MCP server) with:
+
+- `persona_name`: `"Brainstorm Facilitator"`
+- `instruction`: the text following `/brainstorm` (the ambiguous topic or
+  decision to resolve), plus the active task file body as user context
+- `task_id`: the active task number (or `0` for topic-only sessions)
+- `task_file_path`: the active task file path when available
+
+The persona holds the full system prompt — including the six-expert scheme
+and XML output schema in `<brainstorming_protocol>` — plus repo rules and
+cumulative task history. No skill preload is needed. Classify the reply per
+Dual Dispatch (`XML_EXTRACTED` / `QUESTION` / `REPORT`). A `REPORT` here is
+the structured swarm session output: persist its decisions as task
+constraints, not as implementation.
diff --git a/.opencode/commands/designer.md b/.opencode/commands/designer.md
new file mode 100644
index 0000000..0877f8f
--- /dev/null
+++ b/.opencode/commands/designer.md
@@ -0,0 +1,26 @@
+---
+description: Dispatch the UI/UX Designer persona on the active task for visual strategy
+---
+
+# /designer — UI/UX Designer persona turn
+
+Invoke `dispatch_session_turn` (persona MCP server) with:
+
+- `persona_name`: `"UI/UX Designer"`
+- `instruction`: the text following `/designer` (screen or feature, layout
+  goal, styling constraints), plus the active task file body as user context
+- `task_id`: the active task number
+- `task_file_path`: the active task file path
+
+The persona holds the full system prompt, repo rules, and cumulative task
+history. Its reply is Dual-Dispatch classified:
+
+- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
+- `QUESTION` — the persona needs missing context: answer and re-dispatch
+- `REPORT` — visual strategy: must cover offline states, latency, Dark/Light
+  contrast, and a11y (not just the happy path), enforced through local
+  `DESIGN.md` tokens and component isolation
+
+Wait for the turn result before continuing the pipeline. Never treat a
+`QUESTION` as a pass. Do not let it hallucinate layouts — demand codebase
+context first.
diff --git a/.opencode/commands/planner.md b/.opencode/commands/planner.md
new file mode 100644
index 0000000..c3fd930
--- /dev/null
+++ b/.opencode/commands/planner.md
@@ -0,0 +1,32 @@
+---
+description: Dispatch the Project Planner persona on the active task for Kanban state
+---
+
+# /planner — Project Planner persona turn
+
+Invoke `dispatch_session_turn` (persona MCP server) with:
+
+- `persona_name`: `"Project Planner"`
+- `instruction`: the text following `/planner` (status query, milestone
+  scope, task-file operation), plus the active task file body as user context
+- `task_id`: the active task number
+- `task_file_path`: the active task file path
+
+The persona holds the full system prompt, repo rules, and cumulative task
+history. Its reply is Dual-Dispatch classified:
+
+- `XML_EXTRACTED` — a structured `<hands_*_task>` block (task-generator
+  template with `BEGIN/END_GIT_DIFF` markers, Kanban moves): execute it
+- `CONTEXT_REQUEST` — the persona is smart enough to know it lacks codebase
+  evidence: its `context_request` carries `scope` (where to look) and
+  `focus` (what to find). Run the MCP discovery tools
+  (`custom_context_get_directory_tree`, then
+  `custom_context_extract_signatures`, then `custom_context_read_source_files`
+  on the narrowed files), then re-dispatch with the generated report path
+  as the instruction. Never answer a plan from assumptions.
+- `QUESTION` — the persona needs missing context: answer and re-dispatch
+- `REPORT` — state summary: task files stay the single source of truth
+  across `backlog`, `in-progress`, `qa`, `completed`, `archive`
+
+Wait for the turn result before continuing the pipeline. Never treat a
+`QUESTION` as a pass.
diff --git a/.opencode/commands/programmer.md b/.opencode/commands/programmer.md
new file mode 100644
index 0000000..834acc6
--- /dev/null
+++ b/.opencode/commands/programmer.md
@@ -0,0 +1,28 @@
+---
+description: Dispatch the Senior Programmer persona on the active task for implementation instructions
+---
+
+# /programmer — Senior Programmer persona turn
+
+Invoke `dispatch_session_turn` (persona MCP server) with:
+
+- `persona_name`: `"Senior Programmer"`
+- `instruction`: the text following `/programmer` (approved blueprint
+  reference, implementation target, stack skills to load), plus the active
+  task file body as user context
+- `task_id`: the active task number
+- `task_file_path`: the active task file path
+
+The persona holds the full system prompt, repo rules, and cumulative task
+history. Its reply is Dual-Dispatch classified:
+
+- `XML_EXTRACTED` — a structured `<hands_implementation_task>` block with an
+  explicit skill list and `- [ ] **Step N:**` checklist: execute it
+  (consider `force_xml=true` when a bare report is not actionable)
+- `QUESTION` — the persona needs missing context: answer and re-dispatch
+- `REPORT` — free-form guidance: only accept it when it names the exact
+  skills to load and the verification gates per phase
+
+Wait for the turn result before continuing the pipeline. Never treat a
+`QUESTION` as a pass. If the persona proposes bypassing framework standards
+or fragile hacks (Anti-Hack Directive), STOP and escalate to the Manager.
diff --git a/.opencode/commands/strategist.md b/.opencode/commands/strategist.md
new file mode 100644
index 0000000..4d4f45a
--- /dev/null
+++ b/.opencode/commands/strategist.md
@@ -0,0 +1,27 @@
+---
+description: Dispatch the Sprint Strategist persona on the active task for capacity-gated planning
+---
+
+# /strategist — Sprint Strategist persona turn
+
+Invoke `dispatch_session_turn` (persona MCP server) with:
+
+- `persona_name`: `"Sprint Strategist"`
+- `instruction`: the text following `/strategist` (backlog candidates,
+  sprint goal, capacity question), plus the active task file body as user
+  context
+- `task_id`: the active task number
+- `task_file_path`: the active task file path
+
+The persona holds the full system prompt, repo rules, and cumulative task
+history. Its reply is Dual-Dispatch classified:
+
+- `XML_EXTRACTED` — a structured `<hands_*_task>` block: execute it
+- `QUESTION` — the persona needs missing context: answer and re-dispatch
+- `REPORT` — ranked sprint plan: every candidate must carry a complexity
+  estimate (S/M/L/XL), a MoSCoW tier, and WIP-limit accounting (max 3
+  concurrent). The persona may say NO with evidence — a pushback backed by
+  capacity data is a pass, not a failure
+
+Wait for the turn result before continuing the pipeline. Never treat a
+`QUESTION` as a pass.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 8b44be1..5a97e99 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -15,6 +15,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **owt worktree plugin (Task 164):** Installed `@nano-step/opencode-worktree-plugin` globally (`npm i -g` + `owt-setup install` → `~/.config/opencode/plugins/worktree-plugin.js` + 7 slash commands incl. `/init-worktree`, `/list-worktrees`, `/open-worktree`; file-based loading kept, `opencode.json`/`tui.json` untouched by design — npm spec resolves from project `node_modules` which this docs-only repo has none of, and owt is not a TUI panel plugin). Chose owt over `kdcokenny/opencode-worktree` (OCX-only, OCX not allowed) and `arturosdg/opencode-worktree` (standalone TUI). Project side: `.gitignore` guards (`.opencode/worktrees/`, `worktree-sessions.json`), new `LLM.txt` §7.8 install/commands/verify docs. Optional `owt hook --global` left disabled.
 - **Persona MCP engine replacing loop-engine (Task 167):** New stdio FastMCP server `mcp-persona-server/` (`dual_dispatch.py` XML/question classifier, `session.py` append-only JSONL transcripts + lineage projection, `telegram.py` stdlib-only Bot API approval gates, `server.py` with `dispatch_session_turn`/`get_session_summary`/`escalate_to_admin`/`request_admin_approval` tools on LiteLLM `PERSONA_MODEL`); slash commands `.opencode/commands/{qa,reviewer,manager,brainstorm}.md`; `agents/cognitive-executor.md` Persona Loop section (Implementation → QA → Review → Approval Gate → Closure + Dual Dispatch statuses); `opencode.json` `persona` entry (120s timeout for LLM turns) + tool permissions; `tests/test_persona_server.py` **28 passed**, full suite **83 passed**.
 - **Manager-decision learning repo + skill (Task 168):** New `packages/cognitive-lead-decisions/` (`schema/decision.schema.json` with verbatim-quote + linkage fields, `samples/manager_profile.md` baseline, `scripts/compile_profile.py` review-draft printer, `scripts/validate_decisions.py` dependency-free validator) and stdio FastMCP server `mcp-decision-server/` (`redactor.py` sanitize/verify engine, `server.py` with `extract_session_decisions`/`record_manager_decision`/`query_manager_decisions`/`get_manager_profile`/`propose_profile_evolution` — gated sample evolution, never auto-writes); universal `skill-templates/manager-decision/SKILL.md` (extraction/consultation/evolution workflows, per-session example); `opencode.json` `manager_decisions` entry + 5 tool permissions; executor matrix + bootstrapping consult past rulings; `tests/test_decision_server.py` **14 passed**, full suite **101 passed**.
+- **Missing persona slash commands (Task 174):** New `.opencode/commands/{architect,designer,programmer,planner,strategist}.md` dispatching the exact `06-personas.md` names (`Software Architect`, `UI/UX Designer`, `Senior Programmer`, `Project Planner`, `Sprint Strategist`) in the established `qa.md` Dual-Dispatch pattern (persona-specific REPORT guidance: Discovery-First, a11y/environmental checklist, Anti-Hack, Kanban source-of-truth, MoSCoW/WIP); `agents/cognitive-executor.md` command reference updated to all 9 commands. System prompt bumped to **9.10.0** (rebuilt from fragments, sync-check clean).
+- **Persona engine hardening, same task (Task 174 extension, manager order 2026-09-09):** (1) persona persistence — `SESSIONS_ROOT` pinned under the install root + per-task persona identity cards (`load/save_persona_card`, injected every turn), so personas survive across LiteLLM calls; (2) `<hands_context_request>` lane (`CONTEXT_REQUEST` with `scope`/`focus`) + planner/architect re-dispatch loops via MCP discovery tools; (3) bottlenecks fixed — split gate (`open_approval_gate`/`poll_approval_gate`, blocking gate kept as legacy), `slugify_stage()` keeps every `callback_data` under Telegram's 64-byte cap, `PERSONA_MAX_REPLAY_TURNS` (default 50) bounds replay; (4) lineage fallback chain (repo → cwd → global config) with stderr warnings, so every persona sees the full system prompt. Full suite **138 passed**.
 
 ### Changed
 
@@ -29,6 +31,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ### Removed
 
 - **loop-engine daemon + deploy infra (Task 167):** Deleted `loop-engine/` (48 tracked files: daemon/gateway/router/personas/qa_engine/executor/verifier/sentinel/stacks/specs/models/state/watcher + 20 test files + uv.lock) including ignored residue (`.venv`, logs, `__pycache__`), plus `deploy/cognitive-loop.service`, `deploy/docker-compose.yml`, `deploy/Dockerfile` (empty `deploy/` dir removed by git). No `.gitignore` loop rules existed. External historical mentions (`docs/history/*`, `docs/loop-engine/*`, `README.md`, archived tasks) intentionally left untouched.
+- **brainstorm-swarm skill removed, persona covers it (Task 174):** Deleted `skill-templates/brainstorm-swarm/SKILL.md` + global `~/.config/opencode/skills/brainstorm-swarm/` per Manager directive ("we have a persona, no skill needed") — the six-expert scheme and XML schema survive in `prompts/fragments/12-brainstorming_protocol.md`, injected into every `dispatch_session_turn` via `system-prompt.md`; `.opencode/commands/brainstorm.md` rewritten as a pure `Brainstorm Facilitator` persona turn (no skill preload); registry line dropped from fragment 07, `mcp-persona-server/server.py` docstring + executor reference updated, README skill tree pruned. Historical mentions (old CHANGELOG entries, `tasks/archive/*`, `.opencode/memory/*`, `docs/history/*`, `context-reports/*` snapshots) intentionally left untouched. Full suite **120 passed**.
 
 ## [9.10.0] - 2026-09-04
 
diff --git a/README.md b/README.md
index 5c07062..e4549c8 100644
--- a/README.md
+++ b/README.md
@@ -226,8 +226,6 @@ cp .env.example .env
 │   │   └── SKILL.md
 │   ├── audit-agents/                   # AGENTS.md generation & ZAC audits
 │   │   └── SKILL.md
-│   ├── brainstorm-swarm/               # Multi-persona brainstorming sessions
-│   │   └── SKILL.md
 │   ├── code-search/                    # MCP-based codebase discovery
 │   │   └── SKILL.md
 │   ├── debug-instrumentation/          # Strategic logging for complex bug diagnosis
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 970d53c..2f2be20 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -239,6 +239,12 @@ Every `dispatch_session_turn` reply carries a `status`:
   instruction set.
 - `QUESTION` — the persona needs missing context. Answer the `question`
   precisely and re-dispatch; never treat a question as a pass or a report.
+- `CONTEXT_REQUEST` — the persona (planner/architect) knows it lacks
+  codebase evidence. Its `context_request` carries `scope` and `focus`: run
+  the MCP discovery tools (`custom_context_get_directory_tree` →
+  `custom_context_extract_signatures` →
+  `custom_context_read_source_files`), then re-dispatch with the generated
+  report path as the instruction. Never let it plan from assumptions.
 - `REPORT` — free-form evaluation findings. Triage, verify, record evidence.
 - `RETRY_NEEDED` (only when you set `force_xml=true`) — re-dispatch with an
   instruction that explicitly demands a `<hands_*_task>` block.
@@ -246,9 +252,15 @@ Every `dispatch_session_turn` reply carries a `status`:
 ### Tool and command reference
 
 - MCP tools: `dispatch_session_turn`, `get_session_summary`,
-  `escalate_to_admin`, `request_admin_approval` (see `opencode.json`).
+  `escalate_to_admin`, `request_admin_approval`, `open_approval_gate`,
+  `poll_approval_gate` (see `opencode.json`). Prefer the split gate
+  (`open_approval_gate` once, then `poll_approval_gate` in short windows
+  until `"status": "decided"`): a blocking wait longer than the MCP tool
+  timeout gets killed and the manager's press lands unconsumed.
 - Slash commands: `.opencode/commands/qa.md`, `reviewer.md`, `manager.md`,
-  `brainstorm.md` (the latter loads the `brainstorm-swarm` skill first).
+  `brainstorm.md`, `architect.md`, `designer.md`, `programmer.md`,
+  `planner.md`, `strategist.md` (persona turns via `dispatch_session_turn`;
+  `manager.md` opens the Telegram approval gate).
 - Session transcripts persist append-only under
   `tasks/.sessions/{task_id}/transcript.jsonl` — the audit trail behind every
   gate decision.
diff --git a/mcp-persona-server/dual_dispatch.py b/mcp-persona-server/dual_dispatch.py
index 7498877..bc10154 100644
--- a/mcp-persona-server/dual_dispatch.py
+++ b/mcp-persona-server/dual_dispatch.py
@@ -30,6 +30,20 @@ XML_BLOCK_RE = re.compile(
     re.DOTALL,
 )
 
+# Context-request block: a planner/architect persona smart enough to know it
+# lacks codebase context emits this INSTEAD OF guessing, and the executor
+# gathers the evidence (MCP discovery tools) and re-dispatches. Deliberately
+# NOT part of XML_BLOCK_RE: it routes to the CONTEXT_REQUEST lane, never to
+# the XML_EXTRACTED execution lane.
+CONTEXT_REQUEST_RE = re.compile(
+    r"<hands_context_request\b[^>]*>([\s\S]*?)</hands_context_request>",
+    re.DOTALL,
+)
+
+# Inner fields of a context request (all optional, tolerant parsing).
+_CONTEXT_SCOPE_RE = re.compile(r"<scope\b[^>]*>([\s\S]*?)</scope>", re.DOTALL)
+_CONTEXT_FOCUS_RE = re.compile(r"<focus\b[^>]*>([\s\S]*?)</focus>", re.DOTALL)
+
 # Heuristics for "the model is asking something / needs input".
 # Applied to text AFTER all XML blocks have been stripped out.
 QUESTION_RE = re.compile(
@@ -110,6 +124,36 @@ def strip_all_xml(text: str) -> str:
     return XML_BLOCK_RE.sub("", text).strip()
 
 
+def extract_context_request(text: str) -> tuple[bool, Optional[dict[str, str]], str]:
+    """Detect and parse a ``<hands_context_request>`` block.
+
+    The planner/architect persona emits this when it needs codebase evidence
+    (directory tree, signatures, source bodies) before it can plan. The
+    executor MUST run the MCP discovery tools and re-dispatch with the
+    report — never treat the request itself as a final report.
+
+    Returns ``(found, payload, clean_text)`` where payload holds ``scope``
+    (directories/files of interest), ``focus`` (what to look for), and
+    ``raw`` (the full block verbatim). Malformed blocks (no closing tag)
+    return ``found=False`` and fall through to question/report lanes.
+    """
+    if not text:
+        return False, None, ""
+    match = CONTEXT_REQUEST_RE.search(text)
+    if match is None:
+        return False, None, text.strip()
+    inner = match.group(1) or ""
+    scope_match = _CONTEXT_SCOPE_RE.search(inner)
+    focus_match = _CONTEXT_FOCUS_RE.search(inner)
+    payload = {
+        "scope": scope_match.group(1).strip() if scope_match else "",
+        "focus": focus_match.group(1).strip() if focus_match else "",
+        "raw": match.group(0),
+    }
+    clean_text = (text[: match.start()] + text[match.end() :]).strip()
+    return True, payload, clean_text
+
+
 def is_clarification_question(text: str) -> bool:
     """Return True when ``text`` (ignoring XML) asks for missing context.
 
diff --git a/mcp-persona-server/server.py b/mcp-persona-server/server.py
index baf7493..4bc74bb 100644
--- a/mcp-persona-server/server.py
+++ b/mcp-persona-server/server.py
@@ -38,14 +38,44 @@ from typing import Any, Optional
 
 from mcp.server.fastmcp import FastMCP
 
-from dual_dispatch import extract_xml, is_clarification_question
-from session import append_turn, build_persona_messages, summarize_session
-from telegram import send_admin_question, send_approval_request
+from dual_dispatch import (
+    extract_context_request,
+    extract_xml,
+    is_clarification_question,
+)
+from session import (
+    append_turn,
+    build_persona_messages,
+    load_persona_card,
+    save_persona_card,
+    summarize_session,
+)
+from telegram import (
+    await_gate_decision,
+    post_approval_gate,
+    send_admin_question,
+    send_approval_request,
+)
 
 # Repo root resolved from this file's location so path handling works no
 # matter which cwd the stdio server is launched from.
 REPO_ROOT = Path(__file__).resolve().parent.parent
 
+# Pin the transcript root under the install root when it is still the
+# cwd-relative default ("tasks/.sessions"). Otherwise session memory
+# scatters with the launch cwd and the persona "does not exist" on the
+# next turn. Explicit overrides (absolute PERSONA_SESSIONS_DIR, tests)
+# are always respected.
+import session as _session_module  # noqa: E402
+
+
+def _pin_sessions_root() -> None:
+    """Pin the transcript root under the install root when relative."""
+    if not _session_module.SESSIONS_ROOT.is_absolute():
+        _session_module.SESSIONS_ROOT = REPO_ROOT / "tasks" / ".sessions"
+
+
+_pin_sessions_root()
 
 # Shared env loader lives in mcp-common (Task 170). Prefer the installed
 # package; fall back to the sibling source tree so plain `uv run <path>`
@@ -145,7 +175,9 @@ def dispatch_session_turn(
     WHEN TO CALL (automatic): after finishing an implementation call this
     with persona "QA Engineer"; before any approval gate call it with
     "Code Reviewer"; when a task is ambiguous or cross-disciplinary call it
-    with "Brainstorm Facilitator" (load the brainstorm-swarm skill first);
+    with "Brainstorm Facilitator" (the six-expert scheme and XML schema
+    come from <brainstorming_protocol> in the system prompt — no skill
+    preload needed);
     when stuck waiting on missing context, let the QUESTION lane guide you.
     Do NOT call this for plain file reads or deterministic checks — use
     direct tools instead.
@@ -154,10 +186,13 @@ def dispatch_session_turn(
        (progressive lineage projection via ``session.build_persona_messages``).
     2. Appends the instruction turn to ``tasks/.sessions/{task_id}/``.
     3. Calls LiteLLM (``PERSONA_MODEL``, ``PERSONA_REASONING_EFFORT``).
-    4. Dual Dispatch: XML present -> ``XML_EXTRACTED``; question -> ``QUESTION``;
-       otherwise -> ``REPORT``. With ``force_xml=True`` and no XML block, the
-       caller gets ``RETRY_NEEDED`` (re-dispatch with a stronger instruction)
-       instead of a silently unstructured answer.
+    4. Dual Dispatch: XML present -> ``XML_EXTRACTED``; context request ->
+       ``CONTEXT_REQUEST``; question -> ``QUESTION``; otherwise -> ``REPORT``.
+       With ``force_xml=True`` and no XML block, the caller gets
+       ``RETRY_NEEDED`` (re-dispatch with a stronger instruction) instead of
+       a silently unstructured answer.
+    5. Advances the persona identity card (``session.save_persona_card``)
+       so the persona persists across LiteLLM calls.
 
     Args:
         task_id: Owning task id (session scope + audit trail).
@@ -168,8 +203,9 @@ def dispatch_session_turn(
 
     Returns:
         Dict with ``status``, ``persona_name``, ``task_id``, plus either
-        ``xml_content`` (XML_EXTRACTED), ``question`` (QUESTION),
-        ``report`` (REPORT), or ``hint`` (RETRY_NEEDED).
+        ``xml_content`` (XML_EXTRACTED), ``context_request`` (CONTEXT_REQUEST),
+        ``question`` (QUESTION), ``report`` (REPORT), or ``hint``
+        (RETRY_NEEDED).
     """
     # NOTE: the task file body is injected into the LLM messages by
     # build_persona_messages below — it is deliberately NOT appended to the
@@ -188,6 +224,7 @@ def dispatch_session_turn(
 
     has_xml, xml_content, clean_text = extract_xml(output)
     if has_xml:
+        save_persona_card(task_id, persona_name, "XML_EXTRACTED")
         return {
             "status": "XML_EXTRACTED",
             "task_id": int(task_id),
@@ -195,7 +232,17 @@ def dispatch_session_turn(
             "xml_content": xml_content,
             "remainder": clean_text,
         }
+    has_ctx, ctx_payload, _ctx_clean = extract_context_request(output)
+    if has_ctx:
+        save_persona_card(task_id, persona_name, "CONTEXT_REQUEST")
+        return {
+            "status": "CONTEXT_REQUEST",
+            "task_id": int(task_id),
+            "persona_name": persona_name,
+            "context_request": ctx_payload,
+        }
     if force_xml:
+        save_persona_card(task_id, persona_name, "RETRY_NEEDED")
         return {
             "status": "RETRY_NEEDED",
             "task_id": int(task_id),
@@ -207,12 +254,21 @@ def dispatch_session_turn(
             ),
         }
     if is_clarification_question(output):
+        raw_question = (clean_text or output.strip())
+        question_cap = 2000
+        trunc_marker = "…(truncated)"
+        open_question = (
+            raw_question if len(raw_question) <= question_cap
+            else raw_question[: question_cap - len(trunc_marker)] + trunc_marker
+        )
+        save_persona_card(task_id, persona_name, "QUESTION", open_question=open_question)
         return {
             "status": "QUESTION",
             "task_id": int(task_id),
             "persona_name": persona_name,
             "question": clean_text or output.strip(),
         }
+    save_persona_card(task_id, persona_name, "REPORT")
     return {
         "status": "REPORT",
         "task_id": int(task_id),
@@ -277,5 +333,45 @@ def request_admin_approval(
     return {"task_id": int(task_id), "stage": stage, **result}
 
 
+@mcp.tool()
+def open_approval_gate(
+    task_id: int, stage: str, summary: str, task_file_path: str = ""
+) -> dict[str, Any]:
+    """Post a Telegram Approve/Reject gate WITHOUT waiting (split-gate send).
+
+    WHEN TO CALL (automatic): prefer this over ``request_admin_approval``
+    whenever the caller cannot hold one tool call open for the whole human
+    response window — a blocking wait longer than the MCP tool timeout gets
+    killed and the manager's press lands unconsumed. Post with this tool,
+    then collect the decision with ``poll_approval_gate`` in short,
+    re-callable windows until it reports ``"status": "decided"``.
+    """
+    result = post_approval_gate(task_id, stage, summary, task_file_path, None)
+    return {"task_id": int(task_id), "stage": stage, **result}
+
+
+@mcp.tool()
+def poll_approval_gate(
+    task_id: int,
+    stage: str,
+    wait_s: int = 90,
+    ask_note: bool = True,
+    start_offset: int = 0,
+) -> dict[str, Any]:
+    """Poll one short window for a posted gate's decision (split-gate wait).
+
+    WHEN TO CALL (automatic): after ``open_approval_gate``. Waits at most
+    ``wait_s`` seconds (keep it under the MCP tool timeout). Returns
+    ``"status": "timeout"`` with a resume ``start_offset`` when the manager
+    has not answered yet — call again with that offset. Returns
+    ``"status": "decided"`` with ``decision`` (``"approve"``/``"reject"``)
+    plus optional ``note`` once the manager presses a button.
+    """
+    result = await_gate_decision(
+        task_id, stage, wait_s, ask_note=ask_note, start_offset=start_offset
+    )
+    return {"task_id": int(task_id), "stage": stage, **result}
+
+
 if __name__ == "__main__":
     mcp.run(transport="stdio")
diff --git a/mcp-persona-server/session.py b/mcp-persona-server/session.py
index 557b2c0..111a4ce 100644
--- a/mcp-persona-server/session.py
+++ b/mcp-persona-server/session.py
@@ -20,6 +20,8 @@ from __future__ import annotations
 
 import json
 import os
+import re
+import sys
 from datetime import datetime, timezone
 from pathlib import Path
 from typing import Any, Optional
@@ -31,6 +33,14 @@ SESSIONS_ROOT = Path(os.environ.get("PERSONA_SESSIONS_DIR", "tasks/.sessions"))
 # are skipped silently so sessions degrade gracefully on partial checkouts.
 LINEAGE_FILES = ("system-prompt.md", "AGENTS.md")
 
+# Persona brief location (repo-root relative).
+PERSONA_BRIEF_REL = Path("prompts") / "fragments" / "06-personas.md"
+
+# Transcript replay bound: only the newest N turns are re-sent to LiteLLM so
+# long-lived tasks cannot grow requests without bound. Override via
+# ``PERSONA_MAX_REPLAY_TURNS``. Older turns stay in the JSONL audit trail.
+DEFAULT_MAX_REPLAY_TURNS = 50
+
 
 def _utc_now() -> str:
     """Current UTC time as an ISO-8601 string (used for turn timestamps)."""
@@ -121,6 +131,137 @@ def _read_repo_file(relative: str) -> Optional[str]:
         return None
 
 
+def _lineage_search_roots(repo_root: Path) -> list[Path]:
+    """Ordered roots a lineage file is resolved against.
+
+    1. ``repo_root`` — the checkout the turn runs against (normal path).
+    2. The process working directory (MCP stdio servers may be launched
+       from the project root rather than the install root).
+    3. The global OpenCode config dir (``~/.config/opencode``) — fallback
+       for global installs serving projects without vendored lineage files.
+
+    Duplicates are removed, order preserved.
+    """
+    candidates = [repo_root, Path.cwd(), Path.home() / ".config" / "opencode"]
+    roots: list[Path] = []
+    for candidate in candidates:
+        try:
+            resolved = candidate.resolve()
+        except OSError:
+            continue
+        if resolved not in roots:
+            roots.append(resolved)
+    return roots
+
+
+def _read_lineage_file(
+    name: str, repo_root: Path
+) -> tuple[Optional[str], Optional[str], bool]:
+    """Read lineage file ``name`` from the first root that holds it.
+
+    Returns ``(body, source_path, found)``. ``found`` distinguishes "file
+    exists but is empty" (no warning — nothing to project, nothing missing)
+    from "absent in every root" (caller SHOULD warn: a persona running
+    without its system prompt or repo rules is reasoning blind).
+    """
+    for root in _lineage_search_roots(repo_root):
+        try:
+            body = (root / name).read_text(encoding="utf-8")
+        except (OSError, UnicodeError):
+            continue
+        return (body if body.strip() else "", str(root / name), True)
+    return None, None, False
+
+
+def _warn_missing_lineage(missing: list[str]) -> None:
+    """Stderr warning naming lineage files no search root provided."""
+    if missing:
+        print(
+            "persona-server WARNING: lineage file(s) not found in any search "
+            f"root (repo, cwd, ~/.config/opencode): {', '.join(missing)}. "
+            "The persona turn is reasoning WITHOUT them.",
+            file=sys.stderr,
+        )
+
+
+def _get_max_replay_turns() -> int:
+    """Newest transcript turns re-sent per LiteLLM call (default 50)."""
+    try:
+        return max(1, int(os.environ.get("PERSONA_MAX_REPLAY_TURNS", "") or DEFAULT_MAX_REPLAY_TURNS))
+    except ValueError:
+        return DEFAULT_MAX_REPLAY_TURNS
+
+
+def slugify_persona_name(name: str) -> str:
+    """Filesystem-safe slug for a persona name (card filenames)."""
+    return re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-") or "persona"
+
+
+def persona_card_path(task_id: int, persona_name: str) -> Path:
+    """JSON identity card for one persona inside one task session.
+
+    The card is what makes a persona EXIST between LiteLLM calls: without
+    it every turn rebuilds the persona from scratch (name label only). With
+    it the persona carries durable identity — turn count, last outcome,
+    open questions — across the whole task.
+    """
+    return session_dir(task_id) / f"persona_{slugify_persona_name(persona_name)}.json"
+
+
+def load_persona_card(task_id: int, persona_name: str) -> dict[str, Any]:
+    """Load the persona card; defaults for a first-ever turn."""
+    path = persona_card_path(task_id, persona_name)
+    try:
+        stored = json.loads(path.read_text(encoding="utf-8"))
+        if isinstance(stored, dict):
+            return stored
+    except (OSError, UnicodeError, json.JSONDecodeError):
+        pass
+    now = _utc_now()
+    return {
+        "persona_name": persona_name,
+        "created_at": now,
+        "updated_at": now,
+        "turn_count": 0,
+        "last_status": None,
+        "open_question": None,
+    }
+
+
+def save_persona_card(
+    task_id: int,
+    persona_name: str,
+    status: str,
+    open_question: Optional[str] = None,
+) -> dict[str, Any]:
+    """Advance the persona card after one completed turn (creates it first).
+
+    Args:
+        task_id: Owning task id.
+        persona_name: Persona display name.
+        status: Dispatch outcome (``XML_EXTRACTED``/``QUESTION``/``REPORT``/...).
+        open_question: Carried forward only on ``QUESTION``; cleared by any
+            decisive outcome so stale questions never haunt later turns.
+
+    Returns:
+        The stored card dict.
+    """
+    card = load_persona_card(task_id, persona_name)
+    card["turn_count"] = int(card.get("turn_count", 0) or 0) + 1
+    card["last_status"] = status
+    card["updated_at"] = _utc_now()
+    card["open_question"] = open_question if status == "QUESTION" else None
+    # Atomic write (tmp + os.replace): concurrent Hands on the same
+    # task+persona can still lose an increment, but a torn half-written
+    # card (invalid JSON → silent default reset) is impossible.
+    path = persona_card_path(task_id, persona_name)
+    tmp_path = path.with_name(path.name + ".tmp")
+    with open(tmp_path, "w", encoding="utf-8") as fh:
+        json.dump(card, fh, ensure_ascii=False, indent=2)
+    os.replace(tmp_path, path)
+    return card
+
+
 def build_persona_messages(
     task_id: int,
     persona_name: str,
@@ -133,12 +274,19 @@ def build_persona_messages(
     Progressive lineage projection, broadest context first:
 
     1. ``system`` — global ``system-prompt.md`` + ``AGENTS.md`` (survives
-       every turn; the persona always reasons under repo rules).
+       every turn; the persona always reasons under repo rules). Files are
+       resolved against ``repo_root``, then cwd, then the global OpenCode
+       config dir; a stderr warning names any file missing everywhere.
     2. ``system`` — persona brief (``prompts/fragments/06-personas.md`` when
        present, else a minimal fallback naming the persona).
+    2b. ``system`` — persona identity card (durable per-task state: turn
+       count, last outcome, open question) so the persona EXISTS between
+       LiteLLM calls instead of being rebuilt from a bare name each turn.
     3. ``user`` — full task file body when ``task_file_path`` is given
        (cumulative task conversation / acceptance criteria).
-    4. Prior transcript turns replayed verbatim (cumulative memory).
+    4. Prior transcript turns replayed verbatim (cumulative memory),
+       capped at ``PERSONA_MAX_REPLAY_TURNS`` newest (default 50) so
+       long-lived tasks cannot grow requests without bound.
     5. ``user`` — the new instruction (most specific, last), SKIPPED when
        the replay already ends with it (dedupe: each instruction is sent
        to LiteLLM exactly once).
@@ -157,12 +305,20 @@ def build_persona_messages(
     """
     root = Path(repo_root) if repo_root is not None else Path.cwd()
 
-    # 1. Global lineage: system prompt + repo rules.
+    # 1. Global lineage: system prompt + repo rules (fallback chain).
+    # NOTE (documented, by design): the global-config root is a READ fallback
+    # so installs serving projects without vendored lineage still reason
+    # under a system prompt. First root holding the file wins — a repo copy
+    # (even empty) always shadows the global one.
+    missing: list[str] = []
     system_parts = []
     for relative in LINEAGE_FILES:
-        body = _read_repo_file(str(root / relative))
+        body, _source, found = _read_lineage_file(relative, root)
         if body:
             system_parts.append(f"# {relative}\n\n{body}")
+        elif not found:
+            missing.append(relative)
+    _warn_missing_lineage(missing)
     system_text = (
         "You are a persona of the Cognitive Lead AI multi-persona review pipeline.\n"
         "Reason strictly under the repository rules below.\n\n" + "\n\n".join(system_parts)
@@ -171,8 +327,8 @@ def build_persona_messages(
     )
     messages: list[dict[str, str]] = [{"role": "system", "content": system_text}]
 
-    # 2. Persona brief.
-    personas_body = _read_repo_file(str(root / "prompts" / "fragments" / "06-personas.md"))
+    # 2. Persona brief (fallback chain; minimal fallback names the persona).
+    personas_body, _brief_source, brief_found = _read_lineage_file(str(PERSONA_BRIEF_REL), root)
     if personas_body:
         messages.append(
             {
@@ -181,10 +337,36 @@ def build_persona_messages(
             }
         )
     else:
+        if not brief_found:
+            _warn_missing_lineage([str(PERSONA_BRIEF_REL)])
         messages.append(
             {"role": "system", "content": f"You are acting as persona: {persona_name}."}
         )
 
+    # 2b. Persona identity card — durable self across LiteLLM calls.
+    card = load_persona_card(task_id, persona_name)
+    card_lines = [
+        f"You are the persistent persona '{card.get('persona_name', persona_name)}' "
+        f"on task {task_id} (turn #{int(card.get('turn_count', 0) or 0) + 1}).",
+    ]
+    if card.get("last_status"):
+        card_lines.append(f"Your last turn ended as: {card['last_status']}.")
+    if card.get("open_question"):
+        card_lines.append(
+            "Your still-open question from the previous turn: "
+            f"{card['open_question']}"
+        )
+    card_lines.append(
+        "When you lack codebase context for planning, emit a "
+        "<hands_context_request> block (see your command brief) instead of "
+        "guessing — the executor will gather it and re-dispatch."
+        if card.get("last_status") != "CONTEXT_REQUEST"
+        else "Codebase evidence was just gathered for your last context "
+        "request — proceed with planning on that evidence instead of "
+        "requesting again."
+    )
+    messages.append({"role": "system", "content": " ".join(card_lines)})
+
     # 3. Cumulative task context.
     if task_file_path:
         task_body = _read_repo_file(task_file_path)
@@ -196,9 +378,23 @@ def build_persona_messages(
                 }
             )
 
-    # 4. Replay prior turns (LiteLLM fields only).
+    # 4. Replay prior turns (LiteLLM fields only), newest-first capped.
+    all_turns = read_transcript(task_id)
+    max_replay = _get_max_replay_turns()
+    omitted = max(0, len(all_turns) - max_replay)
+    if omitted:
+        messages.append(
+            {
+                "role": "user",
+                "content": (
+                    f"[{omitted} oldest transcript turn(s) omitted from this "
+                    "prompt by PERSONA_MAX_REPLAY_TURNS; they remain in the "
+                    "JSONL audit trail.]"
+                ),
+            }
+        )
     replayed: list[dict[str, str]] = []
-    for turn in read_transcript(task_id):
+    for turn in all_turns[-max_replay:]:
         role = turn.get("role", "user")
         if role not in ("system", "user", "assistant"):
             role = "user"
diff --git a/mcp-persona-server/telegram.py b/mcp-persona-server/telegram.py
index 46df39e..37606ff 100644
--- a/mcp-persona-server/telegram.py
+++ b/mcp-persona-server/telegram.py
@@ -23,8 +23,10 @@ without touching the network.
 
 from __future__ import annotations
 
+import hashlib
 import json
 import os
+import re
 import time
 import urllib.parse
 import urllib.request
@@ -34,6 +36,9 @@ from typing import Any, Callable, Optional
 MAX_TEXT_LEN = 3500
 # Long-poll window per getUpdates call (seconds).
 POLL_WINDOW = 25
+# Telegram caps callback_data at 64 bytes ("Bad Request: BUTTON_DATA_INVALID"
+# beyond that). Stage slugs in keyboards are budgeted well under it.
+MAX_CALLBACK_LEN = 64
 
 
 def _env(name: str, default: str = "") -> str:
@@ -76,21 +81,60 @@ def _api(
     return body
 
 
+def slugify_stage(stage: str) -> str:
+    """Callback-safe slug for a gate stage name.
+
+    ``callback_data`` is capped at 64 bytes by Telegram, so the full human
+    stage text (which stays in the message body) can never ride on the
+    buttons. The slug keeps ``approve:{task}:{slug}`` / ``reject:{task}:{slug}``
+    far under the cap while remaining human-readable in update logs.
+
+    Short stages pass through unchanged (``"QA"`` -> ``"qa"``). Long or
+    degenerate stages get a content hash suffix so two DISTINCT stages can
+    never share one slug (truncated siblings and double-``gate`` fallbacks
+    would otherwise cross-route approvals between gates of one task).
+    """
+    base = re.sub(r"[^a-z0-9]+", "-", str(stage).lower()).strip("-")
+    digest = hashlib.sha1(str(stage).encode("utf-8")).hexdigest()[:6]
+    if not base:
+        # Degenerate stage names must not all share one 'gate' slug.
+        return f"gate-{digest}"
+    if len(base) <= 32:
+        return base
+    return f"{base[:25]}-{digest}"
+
+
 def _approval_keyboard(task_id: int, stage: str) -> dict[str, Any]:
     """Inline keyboard with task/stage-scoped Approve / Reject buttons.
 
-    ``callback_data`` embeds ``{task_id}:{stage}`` (e.g. ``approve:167:QA``)
-    so concurrent gates on different tasks can never cross-accept each
-    other's button presses — the waiter filters on the expected suffix.
+    ``callback_data`` embeds ``{task_id}:{stage-slug}`` (e.g.
+    ``approve:167:qa``) so concurrent gates on different tasks can never
+    cross-accept each other's button presses — the waiter filters on the
+    expected suffix. The slug (never the raw stage text) rides the buttons
+    so long stage names cannot trip Telegram's 64-byte ``callback_data``
+    cap; the full stage text is echoed in the gate message body instead.
     """
-    return {
+    slug = slugify_stage(stage)
+    keyboard = {
         "inline_keyboard": [
             [
-                {"text": "✅ Approve", "callback_data": f"approve:{task_id}:{stage}"},
-                {"text": "❌ Reject", "callback_data": f"reject:{task_id}:{stage}"},
+                {"text": "✅ Approve", "callback_data": f"approve:{task_id}:{slug}"},
+                {"text": "❌ Reject", "callback_data": f"reject:{task_id}:{slug}"},
             ]
         ]
     }
+    # Explicit runtime guard (never bare assert: asserts vanish under
+    # ``python -O``, and an oversize payload would hang the gate on a silent
+    # Telegram rejection). Measured in encoded BYTES against the 64B cap.
+    for row in keyboard["inline_keyboard"]:
+        for button in row:
+            size = len(button["callback_data"].encode("utf-8"))
+            if size > MAX_CALLBACK_LEN:
+                raise ValueError(
+                    f"callback_data exceeds Telegram 64B cap ({size}B): "
+                    f"{button['callback_data']!r}"
+                )
+    return keyboard
 
 
 def _options_keyboard(options: list[str]) -> dict[str, Any]:
@@ -139,9 +183,12 @@ def _wait_for_update(
         chat_id: Target chat id (both callbacks and messages are filtered).
         timeout_s: Give up after this many seconds.
         transport: Test hook forwarded to ``_api``.
-        expected_action_prefix: When set (e.g. ``":167:QA"``), callbacks
-            whose data does NOT contain the prefix belong to a different
-            gate and are skipped (offset still advances past them).
+        expected_action_prefix: When set (e.g. ``":167:qa"``), ONLY the two
+            exact callbacks ``"approve"+prefix`` / ``"reject"+prefix`` are
+            accepted. Bare substring matching is deliberately NOT used: one
+            stage's slug is often a prefix of another's (``planning`` vs
+            ``planning-review``), and a substring match would let a gate
+            consume a sibling stage's decision.
         start_offset: First ``update_id`` to consider — pass the value from
             ``_discard_stale_updates`` so stale history is never replayed.
 
@@ -166,7 +213,10 @@ def _wait_for_update(
             callback_chat = callback_msg.get("chat") or {}
             if str(callback_chat.get("id", "")) == str(chat_id) and callback.get("data"):
                 data = str(callback["data"])
-                if expected_action_prefix is not None and expected_action_prefix not in data:
+                if expected_action_prefix is not None and data not in (
+                    "approve" + expected_action_prefix,
+                    "reject" + expected_action_prefix,
+                ):
                     continue  # Another gate's button — skip, keep polling.
                 # Acknowledge immediately: dismisses the Telegram loading
                 # spinner on the manager's button press.
@@ -241,12 +291,47 @@ def send_approval_request(
         return {"sent": False, "reason": "missing Telegram credentials"}
     timeout_s = int(os.environ.get("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "1800") or 1800)
 
+    # NOTE: pass the RAW summary — post_approval_gate prepends its own
+    # header/ref. Passing pre-formatted text would duplicate the header.
+    post = post_approval_gate(task_id, stage, summary, task_file_path, transport)
+    if not post.get("sent"):
+        return post
+    return await_gate_decision(
+        task_id,
+        stage,
+        timeout_s,
+        ask_note=ask_note,
+        note_timeout_s=note_timeout_s,
+        transport=transport,
+        start_offset=post["start_offset"],
+    )
+
+
+def post_approval_gate(
+    task_id: int,
+    stage: str,
+    summary: str,
+    task_file_path: str = "",
+    transport: Optional[Callable[..., dict[str, Any]]] = None,
+) -> dict[str, Any]:
+    """Post a gate keyboard WITHOUT waiting (split-gate send half).
+
+    Long blocking waits always outlive the MCP tool timeout, so the waiter
+    gets killed and the manager's press lands unconsumed. Callers that
+    cannot hold a tool call open (approval gates) post with this function
+    and collect the decision with ``await_gate_decision`` in short,
+    re-callable windows instead.
+
+    Returns ``{"sent": True, "stage_slug", "start_offset"}`` (the offset to
+    resume polling from) or ``{"sent": False, "reason"}``.
+    """
+    token = _env("TELEGRAM_BOT_TOKEN")
+    chat_id = _env("TELEGRAM_CHAT_ID")
+    if not token or not chat_id:
+        return {"sent": False, "reason": "missing Telegram credentials"}
     header = f"Task {task_id} — approval requested: {stage}\n"
     ref = f"Task file: {task_file_path}\n" if task_file_path else ""
     full_text = (header + ref + "\n" + summary).strip()
-    # Chunk oversized bodies into sequential messages (Telegram caps single
-    # messages); the inline keyboard rides on the FINAL chunk so the manager
-    # decides with the complete context above. Nothing is truncated.
     chunks = [full_text[i : i + MAX_TEXT_LEN] for i in range(0, len(full_text), MAX_TEXT_LEN)]
     try:
         # Drain the queue first: a stale Approve from a previous gate must
@@ -264,12 +349,46 @@ def send_approval_request(
             },
             transport,
         )
+        return {
+            "sent": True,
+            "task_id": int(task_id),
+            "stage": str(stage),
+            "stage_slug": slugify_stage(stage),
+            "start_offset": start_offset,
+        }
+    except (RuntimeError, ValueError) as exc:
+        return {"sent": False, "reason": str(exc)}
+
+
+def await_gate_decision(
+    task_id: int,
+    stage: str,
+    wait_s: int = 90,
+    ask_note: bool = True,
+    note_timeout_s: int = 300,
+    transport: Optional[Callable[..., dict[str, Any]]] = None,
+    start_offset: int = 0,
+) -> dict[str, Any]:
+    """Poll one short window for a posted gate's decision (split-gate wait half).
+
+    Waits at most ``wait_s`` seconds (keep it under the MCP tool timeout —
+    90s default). On ``"status": "timeout"`` the caller simply calls again
+    with the returned ``start_offset``; the manager's eventual press is
+    never lost because polling always resumes past consumed updates. On a
+    decision, the optional note flow runs exactly like the blocking gate.
+    """
+    token = _env("TELEGRAM_BOT_TOKEN")
+    chat_id = _env("TELEGRAM_CHAT_ID")
+    if not token or not chat_id:
+        return {"sent": False, "reason": "missing Telegram credentials"}
+    slug = slugify_stage(stage)
+    try:
         update = _wait_for_update(
             token,
             chat_id,
-            timeout_s,
+            wait_s,
             transport,
-            expected_action_prefix=f":{task_id}:{stage}",
+            expected_action_prefix=f":{task_id}:{slug}",
             start_offset=start_offset,
         )
         decision = _extract_answer(update)
@@ -278,11 +397,21 @@ def send_approval_request(
         )
         return {
             "sent": True,
+            "status": "decided",
             "decision": decision,
             "note": note,
             "update_id": update.get("update_id"),
+            "start_offset": int(update.get("update_id", start_offset - 1)) + 1,
         }
-    except (RuntimeError, TimeoutError) as exc:
+    except TimeoutError:
+        # Re-read the newest update id so the next window resumes cleanly
+        # past anything irrelevant that arrived meanwhile.
+        try:
+            resume = _discard_stale_updates(token, transport)
+        except RuntimeError:
+            resume = start_offset
+        return {"sent": True, "status": "timeout", "start_offset": resume}
+    except RuntimeError as exc:
         return {"sent": False, "reason": str(exc)}
 
 
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 731e769..36a16cb 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.9.0</system_version>
+<system_version>9.10.0</system_version>
diff --git a/prompts/fragments/07-agent_skills_registry.md b/prompts/fragments/07-agent_skills_registry.md
index b246723..b70123b 100644
--- a/prompts/fragments/07-agent_skills_registry.md
+++ b/prompts/fragments/07-agent_skills_registry.md
@@ -10,7 +10,6 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
 - **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
 - **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
-- **brainstorm-swarm**: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
 - **versioning-and-release**: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
 - **debug-instrumentation**: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
 - **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.
diff --git a/skill-templates/brainstorm-swarm/SKILL.md b/skill-templates/brainstorm-swarm/SKILL.md
deleted file mode 100644
index 118eb17..0000000
--- a/skill-templates/brainstorm-swarm/SKILL.md
+++ /dev/null
@@ -1,69 +0,0 @@
----
-name: brainstorm-swarm
-description: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
----
-
-# Multi-Agent Brainstorming Swarm
-
-## When to Trigger
-
-- The Manager explicitly requests a brainstorming session.
-- After intent expansion, the input remains ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning).
-- A backlog task contains a `<brainstorming_session>` block that must be interpreted as non-functional guidelines.
-
-## The Six Expert Personas
-
-### 1. system_architect
-
-**Focus:** System design, scalability, data flow, API contracts, infrastructure, and architectural trade-offs.
-
-**Output:** Technical architecture assessment with risk analysis and recommended patterns. Covers coupling, cohesion, latency, availability, and disaster recovery.
-
-### 2. security_engineer
-
-**Focus:** Threat modeling, authentication/authorization, data privacy, compliance, and vulnerability assessment.
-
-**Output:** Security audit with identified risks (OWASP Top 10), severity ratings, and mitigation strategies. Covers least privilege, encryption at rest/in-transit, and regulatory requirements.
-
-### 3. product_manager
-
-**Focus:** User needs, feature prioritization, roadmap alignment, MVP definition, and stakeholder communication.
-
-**Output:** Product requirements analysis with prioritized user stories and success metrics. Maps features to user impact and business outcomes.
-
-### 4. business_strategist
-
-**Focus:** Market positioning, ROI analysis, competitive landscape, monetization models, and go-to-market strategy.
-
-**Output:** Business case assessment with strategic recommendations and risk/reward analysis. Covers total addressable market, pricing, and differentiation.
-
-### 5. legal_advisor
-
-**Focus:** Regulatory compliance, licensing, data protection laws (GDPR/CCPA), intellectual property, and contractual obligations.
-
-**Output:** Legal compliance review with identified obligations, risks, and recommended safeguards. Covers cross-border data transfer, terms of service, and liability.
-
-### 6. critical_thinker
-
-**Focus:** Devil's advocacy, assumption challenging, blind-spot detection, logical fallacies, and edge-case stress-testing.
-
-**Output:** Critical review highlighting unstated assumptions, cognitive biases, and stress-test results for each proposed approach.
-
-## Execution Rules
-
-1. **Independent Analysis:** Each persona MUST produce its analysis before reading any other persona's output. No cross-contamination.
-2. **Conflict Resolution:** If two personas give contradictory advice, the final synthesis MUST explicitly document the conflict and explain the resolution.
-3. **Minimum Output:** Each persona MUST produce at least 3 concrete observations or recommendations.
-4. **Grounding:** All reasoning must be grounded in the problem description. Do not invent hypothetical scenarios without explicit basis.
-5. **Output Format:** Always use the XML `<brainstorming_session>` schema defined in the system prompt's `<brainstorming_protocol>` section.
-
-## Interpretation in Backlog Tasks
-
-When a task file contains a `<brainstorming_session>` block, interpret the enclosed `<persona_responses>` and `<final_recommendation>` as **non-functional guidelines** that inform but do not override the primary task instructions. They provide cross-domain context:
-
-- `system_architect` responses influence architectural decisions.
-- `security_engineer` responses impose security constraints.
-- `product_manager` responses guide feature prioritization.
-- `business_strategist` responses shape scope and timeline.
-- `legal_advisor` responses enforce compliance requirements.
-- `critical_thinker` responses highlight edge cases and risks to test.
diff --git a/system-prompt.md b/system-prompt.md
index db786b7..fa1094c 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.9.0</system_version>
+<system_version>9.10.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -119,7 +119,6 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
 - **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
 - **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
-- **brainstorm-swarm**: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
 - **versioning-and-release**: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
 - **debug-instrumentation**: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
 - **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.
diff --git a/tests/test_persona_server.py b/tests/test_persona_server.py
index 59f8883..fd4d022 100644
--- a/tests/test_persona_server.py
+++ b/tests/test_persona_server.py
@@ -374,7 +374,7 @@ def test_telegram_approval_approve_flow(server_mod, monkeypatch):
 
     def staged(method, payload):
         if method == "sendMessage":
-            queue.append(_approval_update(7, 12345, "approve:175:QA"))
+            queue.append(_approval_update(7, 12345, "approve:175:qa"))
         return base(method, payload)
 
     telegram = sys.modules["telegram"]
@@ -403,7 +403,7 @@ def test_telegram_approval_with_manager_note(server_mod, monkeypatch):
         if method == "sendMessage":
             sends.append(payload)
             if len(sends) == 1:  # Gate message → decision press.
-                queue.append(_approval_update(7, 12345, "approve:175:QA"))
+                queue.append(_approval_update(7, 12345, "approve:175:qa"))
             elif len(sends) == 2:  # Note prompt → typed note.
                 queue.append({
                     "update_id": 8,
@@ -432,7 +432,7 @@ def test_telegram_approval_note_silence_never_blocks(server_mod, monkeypatch):
     def staged(method, payload):
         if method == "sendMessage" and not queue:
             # Only the decision ever arrives; the note prompt goes unanswered.
-            queue.append(_approval_update(7, 12345, "reject:175:QA"))
+            queue.append(_approval_update(7, 12345, "reject:175:qa"))
         return base(method, payload)
 
     telegram = sys.modules["telegram"]
@@ -458,20 +458,20 @@ def test_telegram_approval_scopes_callback_and_answers_query(server_mod, monkeyp
 
     keyboard = telegram._approval_keyboard(175, "QA")
     buttons = keyboard["inline_keyboard"][0]
-    assert buttons[0]["callback_data"] == "approve:175:QA"
-    assert buttons[1]["callback_data"] == "reject:175:QA"
+    assert buttons[0]["callback_data"] == "approve:175:qa"
+    assert buttons[1]["callback_data"] == "reject:175:qa"
 
     # The fresh decision arrives after the gate message is posted.
     orig_fake = transport
     def staged(method, payload):
         if method == "sendMessage":
-            queue.append(_approval_update(9, 12345, "approve:175:QA"))
+            queue.append(_approval_update(9, 12345, "approve:175:qa"))
         return orig_fake(method, payload)
     result = telegram.send_approval_request(
         175, "QA", "All green.", transport=staged, ask_note=False
     )
     # Stale approve:100:OLD (id 3) was discarded by the offset=-1 probe;
-    # only the scoped approve:175:QA (id 9) resolved the gate.
+    # only the scoped approve:175:qa (id 9) resolved the gate.
     assert result["sent"] is True
     assert result["decision"] == "approve"
     assert result["update_id"] == 9
@@ -637,12 +637,292 @@ def test_tool_docstrings_carry_when_to_call(server_mod):
     tools = [
         server_mod.dispatch_session_turn, server_mod.get_session_summary,
         server_mod.escalate_to_admin, server_mod.request_admin_approval,
+        server_mod.open_approval_gate, server_mod.poll_approval_gate,
     ]
     for tool in tools:
         fn = tool.fn if hasattr(tool, "fn") else tool
         assert "WHEN TO CALL" in (fn.__doc__ or ""), getattr(fn, "__name__", tool)
 
 
+# --- Task 174 extension: context requests, persona cards, split gate --------
+
+CONTEXT_XML = """<hands_context_request>
+  <scope>packages/billing, src/api</scope>
+  <focus>where invoices are validated</focus>
+</hands_context_request>"""
+
+
+def test_extract_context_request_valid(dual):
+    found, payload, clean = dual.extract_context_request(
+        "Need evidence first.\n" + CONTEXT_XML + "\nWill plan after."
+    )
+    assert found is True
+    assert payload["scope"] == "packages/billing, src/api"
+    assert payload["focus"] == "where invoices are validated"
+    assert "<hands_context_request>" in payload["raw"]
+    assert "<hands_context_request>" not in clean
+
+
+def test_extract_context_request_malformed_falls_through(dual):
+    found, payload, clean = dual.extract_context_request(
+        "<hands_context_request><scope>x</scope> never closed?"
+    )
+    assert found is False
+    assert payload is None
+    # And the XML execution lane must never claim it either.
+    has_xml, _, _ = dual.extract_xml(CONTEXT_XML)
+    assert has_xml is False
+
+
+def test_dispatch_context_request_lane(server_mod, sess, monkeypatch):
+    monkeypatch.setitem(
+        sys.modules, "litellm",
+        _stub_litellm("Gathering evidence first.\n" + CONTEXT_XML),
+    )
+    call = server_mod.dispatch_session_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target(181, "Project Planner", "plan the billing refactor")
+    assert result["status"] == "CONTEXT_REQUEST"
+    assert result["context_request"]["scope"] == "packages/billing, src/api"
+    card = sess.load_persona_card(181, "Project Planner")
+    assert card["last_status"] == "CONTEXT_REQUEST"
+    assert card["turn_count"] == 1
+
+
+def test_persona_card_round_trip(sess):
+    card = sess.save_persona_card(182, "QA Engineer", "QUESTION", open_question="Which files?")
+    assert card["turn_count"] == 1
+    assert card["open_question"] == "Which files?"
+    loaded = sess.load_persona_card(182, "QA Engineer")
+    assert loaded["turn_count"] == 1
+    # A decisive outcome clears the stale open question.
+    cleared = sess.save_persona_card(182, "QA Engineer", "REPORT")
+    assert cleared["turn_count"] == 2
+    assert cleared["open_question"] is None
+
+
+def test_build_messages_injects_persona_card(sess, tmp_path):
+    sess.save_persona_card(183, "QA Engineer", "QUESTION", open_question="Which files?")
+    messages = sess.build_persona_messages(
+        183, "QA Engineer", "continue review", None, repo_root=tmp_path
+    )
+    card_msgs = [m for m in messages if "turn #2" in m.get("content", "")]
+    assert card_msgs, "persona identity card must ride every turn"
+    assert "Which files?" in card_msgs[0]["content"]
+
+
+def test_lineage_fallback_to_global_config(sess, tmp_path, monkeypatch, capsys):
+    # repo_root AND cwd hold no lineage files; the global config dir does.
+    empty_root = tmp_path / "repo"
+    empty_root.mkdir()
+    empty_cwd = tmp_path / "cwd"
+    empty_cwd.mkdir()
+    fake_home = tmp_path / "home"
+    (fake_home / ".config" / "opencode").mkdir(parents=True)
+    (fake_home / ".config" / "opencode" / "system-prompt.md").write_text(
+        "GLOBAL-FALLBACK", encoding="utf-8"
+    )
+    monkeypatch.chdir(empty_cwd)
+    monkeypatch.setenv("HOME", str(fake_home))
+    messages = sess.build_persona_messages(
+        184, "QA Engineer", "go", None, repo_root=empty_root
+    )
+    assert any("GLOBAL-FALLBACK" in m["content"] for m in messages)
+    # AGENTS.md is missing everywhere → stderr must say so (never blind).
+    assert "AGENTS.md" in capsys.readouterr().err
+
+
+def test_replay_cap_omits_oldest(sess, monkeypatch):
+    monkeypatch.setenv("PERSONA_MAX_REPLAY_TURNS", "3")
+    for i in range(5):
+        sess.append_turn(185, "user", f"instruction-{i}")
+    messages = sess.build_persona_messages(
+        185, "QA Engineer", "new work", None, repo_root=None
+    )
+    assert any("omitted" in m["content"] for m in messages)
+    assert not any(m.get("content") == "instruction-0" for m in messages)
+    assert any(m.get("content") == "instruction-4" for m in messages)
+    assert messages[-1] == {"role": "user", "content": "new work"}
+
+
+def test_stage_slug_keeps_callback_under_cap(server_mod):
+    telegram = sys.modules["telegram"]
+    long_stage = "Task 174 closure: 5 persona commands + brainstorm-swarm removal ✨"
+    slug = telegram.slugify_stage(long_stage)
+    assert len(slug.encode("utf-8")) <= 32
+    keyboard = telegram._approval_keyboard(174, long_stage)
+    for row in keyboard["inline_keyboard"]:
+        for button in row:
+            assert len(button["callback_data"].encode("utf-8")) < 64
+    assert keyboard["inline_keyboard"][0][0]["callback_data"].startswith("approve:174:")
+
+
+def test_sibling_stage_prefix_never_cross_matches(server_mod, monkeypatch):
+    # QA half-2 (high): awaiting slug "planning" must NOT consume a press
+    # for sibling stage "planning-review" — exact approve/reject match only.
+    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
+    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
+    telegram = sys.modules["telegram"]
+    queue = [
+        _approval_update(40, 12345, "approve:174:planning-review"),
+        _approval_update(41, 12345, "reject:174:planning"),
+    ]
+    calls = []
+    transport = _queue_transport(queue, calls)
+    update = telegram._wait_for_update(
+        "test-token", "12345", 10, transport,
+        expected_action_prefix=":174:planning", start_offset=0,
+    )
+    assert update["update_id"] == 41
+    assert telegram._extract_answer(update) == "reject"
+
+
+def test_distinct_long_stages_never_share_slug(server_mod):
+    telegram = sys.modules["telegram"]
+    a = telegram.slugify_stage("closure review of the persona engine loop")
+    b = telegram.slugify_stage("closure review of the persona engine docs")
+    assert a != b  # shared 32-char prefix, hash suffix disambiguates
+    assert telegram.slugify_stage("") != telegram.slugify_stage("!!!")
+    assert telegram.slugify_stage("QA") == "qa"  # short stages unchanged
+
+
+def test_second_poll_after_decision_times_out(server_mod, monkeypatch):
+    # Documented idempotency: the decision is consumed once; the caller
+    # holds it. A repeat poll with the advanced offset waits, then times out.
+    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
+    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
+    telegram = sys.modules["telegram"]
+    queue = [_approval_update(50, 12345, "approve:176:closure")]
+    calls = []
+    transport = _queue_transport(queue, calls)
+    first = telegram.await_gate_decision(
+        176, "closure", wait_s=10, ask_note=False, transport=transport
+    )
+    assert first["status"] == "decided"
+    second = telegram.await_gate_decision(
+        176, "closure", wait_s=0, ask_note=False, transport=transport,
+        start_offset=first["start_offset"],
+    )
+    assert second["status"] == "timeout"
+
+
+def test_split_gate_post_then_poll(server_mod, monkeypatch):
+    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
+    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
+    telegram = sys.modules["telegram"]
+    queue = []
+    calls = []
+    transport = _queue_transport(queue, calls)
+
+    post = telegram.post_approval_gate(176, "closure", "summary", transport=transport)
+    assert post["sent"] is True
+    assert post["stage_slug"] == "closure"
+
+    # Window 1: manager silent → timeout with a resume offset, nothing lost.
+    first = telegram.await_gate_decision(
+        176, "closure", wait_s=0, ask_note=False,
+        transport=transport, start_offset=post["start_offset"],
+    )
+    assert first["status"] == "timeout"
+
+    # Window 2: the press arrives → decided.
+    queue.append(_approval_update(21, 12345, "approve:176:closure"))
+    second = telegram.await_gate_decision(
+        176, "closure", wait_s=10, ask_note=False,
+        transport=transport, start_offset=first["start_offset"],
+    )
+    assert second["status"] == "decided"
+    assert second["decision"] == "approve"
+    assert second["update_id"] == 21
+
+
+def test_sessions_root_pinned_to_install_root(server_mod, sess, monkeypatch):
+    from pathlib import Path as _P
+
+    # Simulate a cwd-relative default (the launch-cwd scattering bug):
+    # the pin must resolve it under the install root. monkeypatch restores
+    # the fixture dir afterwards — never leak the real repo dir into later
+    # tests (stale cards there break turn-count assertions).
+    monkeypatch.setattr(sess, "SESSIONS_ROOT", _P("tasks/.sessions"))
+    server_mod._pin_sessions_root()
+    assert sess.SESSIONS_ROOT.is_absolute()
+    assert sess.SESSIONS_ROOT.name == ".sessions"
+    assert str(sess.SESSIONS_ROOT).startswith(str(server_mod.REPO_ROOT))
+
+
+def test_empty_lineage_file_warns_nothing(sess, tmp_path, monkeypatch, capsys):
+    # QA advisory: a file that EXISTS but is empty must not warn "not found".
+    (tmp_path / "system-prompt.md").write_text("   \n", encoding="utf-8")
+    empty_cwd = tmp_path / "cwd"
+    empty_cwd.mkdir()
+    fake_home = tmp_path / "home"
+    (fake_home / ".config" / "opencode").mkdir(parents=True)
+    monkeypatch.chdir(empty_cwd)
+    monkeypatch.setenv("HOME", str(fake_home))
+    sess.build_persona_messages(186, "QA Engineer", "go", None, repo_root=tmp_path)
+    err = capsys.readouterr().err
+    assert "system-prompt.md" not in err  # present-but-empty ≠ missing
+    assert "AGENTS.md" in err  # truly absent everywhere → still warns
+
+
+def test_context_nudge_gated_after_context_request(sess, tmp_path):
+    # QA advisory: after a CONTEXT_REQUEST turn the nudge must stand down,
+    # or a compliant persona re-requests forever.
+    sess.save_persona_card(187, "Project Planner", "CONTEXT_REQUEST")
+    messages = sess.build_persona_messages(
+        187, "Project Planner", "plan now", None, repo_root=tmp_path
+    )
+    card_msg = next(m for m in messages if "turn #2" in m.get("content", ""))
+    assert "proceed with planning" in card_msg["content"]
+    assert "emit a" not in card_msg["content"]
+
+
+def test_blocking_gate_sends_single_header(server_mod, monkeypatch):
+    # Regression (self-review of half-2 diff): send_approval_request must
+    # not double-prepend header/ref — post_approval_gate formats them.
+    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
+    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
+    monkeypatch.setenv("TELEGRAM_APPROVAL_TIMEOUT_SECONDS", "10")
+    telegram = sys.modules["telegram"]
+    queue = []
+    calls = []
+    base = _queue_transport(queue, calls)
+    texts = []
+
+    def staged(method, payload):
+        if method == "sendMessage":
+            texts.append(payload["text"])
+            queue.append(_approval_update(30, 12345, "approve:176:qa2"))
+        return base(method, payload)
+
+    result = telegram.send_approval_request(
+        176, "QA2", "Body here.", transport=staged, ask_note=False
+    )
+    assert result["sent"] is True
+    assert result["decision"] == "approve"
+    full = "\n".join(texts)
+    assert full.count("approval requested") == 1
+
+
+def test_open_question_truncation_bounded(server_mod, sess, monkeypatch):
+    # QA half-2 residual: truncated open_question must stay <= 2000 chars.
+    long_q = "What about " + "x" * 3000 + "?"
+    monkeypatch.setitem(sys.modules, "litellm", _stub_litellm(long_q))
+    call = server_mod.dispatch_session_turn
+    target = call.fn if hasattr(call, "fn") else call
+    result = target(189, "QA Engineer", "probe")
+    assert result["status"] == "QUESTION"
+    card = sess.load_persona_card(189, "QA Engineer")
+    assert len(card["open_question"]) <= 2000
+    assert card["open_question"].endswith("…(truncated)")
+
+
+def test_card_write_leaves_no_tmp_residue(sess):
+    sess.save_persona_card(188, "QA Engineer", "REPORT")
+    leftovers = list(sess.session_dir(188).glob("*.tmp"))
+    assert leftovers == []
+
+
 def test_telegram_empty_note_resolves_none(server_mod, monkeypatch):
     # Empty-string replies are not notes (whitespace-only included).
     telegram = sys.modules["telegram"]
@@ -681,7 +961,7 @@ def test_telegram_explicit_skip_resolves_none(server_mod, monkeypatch):
         if method == "sendMessage":
             sends.append(payload)
             if len(sends) == 1:
-                queue.append(_approval_update(7, 12345, "reject:175:QA"))
+                queue.append(_approval_update(7, 12345, "reject:175:qa"))
             elif len(sends) == 2:
                 queue.append({
                     "update_id": 8,
```
<!-- END_GIT_DIFF -->
