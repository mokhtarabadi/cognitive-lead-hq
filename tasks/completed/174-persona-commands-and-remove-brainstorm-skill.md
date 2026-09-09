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
**Factual Git Diff:** Stored in Commit Hash: `70ac2e09a253d8fee6a59a554e3577c091732fd3`
<!-- END_GIT_DIFF -->
