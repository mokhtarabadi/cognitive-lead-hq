# Task 114: Loop Engine Pre-Production Audit

**File:** `tasks/completed/114-loop-engine-pre-production-audit.md`
**Source:** telegram
**Type:** improvement
**Status:** closed

## Source Context

## Goal

Perform a professional pre-production audit of the Cognitive Loop Engine (`loop-engine/`) — docs, code, tests, workflows, AI-provider extensibility, and config — and autonomously fix every finding before first real-world use.

## Original Message (Persian)

ببین میخوام ازت یک بازبینی دقیق روی لوپ انجینمون انجام بدی. من هنوز توی دنیای واقعی لوپ انجین رو تست نکردم، میخوام تمام داکیومنتهای مربوط رو بخونی، تمام کدبیس رو بخونی، همه چیزها رو بخونی، تستها رو بخونی، اگر میتونی بیشتر تستش کنی، همه چیزهاشو نگاه کنی، ورکفلوهاشو نگاه کنی، مثلاً چگونه یک کار شروع میشه و چگونه کار به پایان میرسه یا کجا ادمین نیاز داره دخالت کنه. آیا از پرووایدرهای هوش مصنوعی که الان استفاده میکنیم اوکی هست، میتونیم پرووایدرهای دیگه هم بهش اضافه کنیم در آینده یا نه، کانفیگاش مناسبه، جیسوناش مناسبه، اگزَمپلاش مناسبن، یک اینجور چیزی میخوام انجام بدی. این تسک طولانی احتمالاً چند ساعت طول بکشه. میخوام هنوز من تست نکردم لوپ انجین رو، ولی میخوام واقعاً یک ممیزی آدیت خیلی حرفهای و تمیز روش انجام بدی، قبل از پروداکشن هر چیزی که فکر میکنی هست رو خودت رفعاش کنی.

#task

## English Translation

Listen, I want you to perform a thorough review of our loop engine. I haven't tested the loop engine in the real world yet. I want you to read all the related documentation, read the entire codebase, read everything, read the tests, and if you can, test it further. Examine everything — examine its workflows, e.g., how a job starts and how a job finishes, or where the admin needs to intervene. Are the AI providers we currently use okay? Can we add other providers to it in the future or not? Are its configs appropriate, its JSON appropriate, its examples appropriate? That's the kind of thing I want you to do. This task is long — it will probably take several hours. I haven't tested the loop engine myself yet, but I want a truly professional, clean audit performed on it, and before production, fix anything you believe is wrong yourself.

#task

## Refactored Prompt

<role>
You are a Principal Systems Auditor specializing in local orchestration daemons and LLM-routing pipelines. You have authority to audit and apply minimal, evidence-bound fixes before production.
</role>

<system_context>
Repository: cognitive-lead-hq. Audit target: the `loop-engine/` Python package — daemon.py, watcher.py, router.py, executor.py, gateway.py, qa_engine.py, state.py, models.py, loop-engine.jsonc, pyproject.toml, test_*.py — plus docs/loop-engine/* (README, setup, configuration, multi-project) and .env.example. The engine has NEVER run against real workloads; it was implemented under completed Task 101 and deferred since.
</system_context>

<agentic_reasoning>
Before each audit phase, output a <reasoning_log> covering: (1) logical dependencies between components; (2) risk assessment of any proposed fix; (3) abductive reasoning for each defect found (why does it exist, what breaks at runtime?); (4) grounding — every claim must cite file:line evidence from the codebase or test output.
</agentic_reasoning>

<execution_rules>
- You MUST trace the complete task lifecycle: watcher detection → router category/provider selection → executor invocation → gateway approval gate → qa_engine evidence review → state machine transitions (start → finish), and map every point where admin intervention is required.
- You MUST evaluate provider extensibility: can a new LLM provider be added without touching core logic? Verify against models.py ProviderConcurrency and router.py.
- You MUST cross-validate loop-engine.jsonc against the Pydantic schema in models.py (unknown keys, missing defaults, wrong types) and verify docs/examples match actual behavior.
- You MUST run the existing test suite FIRST as a baseline (`pytest loop-engine/ -v`), record results, and add characterization tests BEFORE changing any behavior.
- You MUST NOT rewrite the architecture. Minimal, surgical fixes only; every fix needs a failing test or concrete defect citation.
- You MUST NOT declare completion without exit-code-0 verification evidence.
</execution_rules>

<output_format>
Deliver an audit report with: (1) Findings table — ID / severity / file:line / description / applied fix; (2) lifecycle map incl. admin intervention points; (3) provider extensibility verdict; (4) config/JSON/examples verdicts; (5) list of applied fixes with diffs; (6) residual risks accepted without fix.
</output_format>

## Relevant Code Context

- `loop-engine/daemon.py` — entry point; `load_config()` parses `loop-engine/loop-engine.jsonc`; `process_task()` orchestrates per-task flow
- `loop-engine/models.py` — Pydantic models: `TaskState`, `LoopEngineConfig`, `CategoryConfig`, `ProviderConcurrency`, `IdleConfig`, `ApprovalConfig`
- `loop-engine/state.py` — SQLite state machine, single source of truth at `loop-engine/state/loop.db`
- `loop-engine/watcher.py` — Kanban watcher; ignores `archive`, `loop-engine`, `.git`
- `loop-engine/router.py` — `LLMRouter(config, workspace_root)` category/provider routing
- `loop-engine/executor.py` + `gateway.py` — execution and Telegram approval gate
- `loop-engine/qa_engine.py` — QA Loop Engine v2, evidence-bound, writes `loop-engine/evidence/<task-id>-<slug>/`
- `loop-engine/test_models.py`, `test_router.py`, `test_executor.py`, `test_state.py` — existing suites
- `docs/loop-engine/{README,setup,configuration,multi-project}.md` — documentation set
- `.env.example` — required API keys (env refs, never raw values)
- `tasks/completed/101-cognitive-loop-engine-proposal.md` — architectural origin (brainstorming proposal)

## AI Analysis & Opinion

- **Nature:** pre-production audit request, not a defect report. The engine has zero real-world runtime hours, so the dominant risk is untested integration paths, not individual bugs.
- **Recommended approach (staged):** (1) baseline `pytest loop-engine/` run; (2) static lifecycle trace across watcher→router→executor→gateway→qa_engine→state; (3) config/schema parity check (jsonc vs Pydantic); (4) provider abstraction review for extensibility; (5) docs/examples accuracy pass; (6) minimal fixes each backed by a characterization test; (7) full re-run.
- **Key risks:** SQLite state machine concurrency under `max_parallel_tasks > 1`; approval gateway hard-dependency on correct `chat_id`; provider API keys leaking into logs/evidence dirs; fixes without characterization tests regressing the only working path.
- **Files expected to change:** loop-engine modules where defects are confirmed, `loop-engine.jsonc` if schema gaps found, docs if behavior/docs diverge.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [x] Initial codebase exploration
- [x] Run baseline test suite (`pytest loop-engine/ -v`) and record results
- [x] Trace full task lifecycle incl. admin intervention points
- [x] Cross-validate `loop-engine.jsonc` vs `models.py` schema
- [x] Review provider extensibility (adding future providers)
- [x] Apply minimal fixes with characterization tests
- [x] Verify functionality

## Acceptance Criteria

- [x] Audit report exists covering lifecycle (start→finish→admin gates), provider extensibility, and config/JSON/examples validity — every finding cites file:line evidence
- [x] All identified defects are fixed OR explicitly documented as accepted residual risks; baseline + new tests pass with exit code 0
- [x] `docs/loop-engine/*` updated to match post-fix actual behavior

## Verification Evidence

- **Test command:** `for t in test_models.py test_state.py test_router.py test_executor.py test_audit_fixes.py; do uv run --no-project --with pydantic --with watchdog python3 $t; done` (run in `loop-engine/`)
- **Expected result:** all tests pass, exit code 0
- **Actual result:** 8+10+9+8+14 = 49 passed, 0 failed across 5 suites (baseline pre-fix: 35 passed / 0 failed)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** audit-driven fixes could regress the only known-working path of an engine that has never run in production; parallel-execution changes could corrupt SQLite state.
- **Rollback plan:** `git revert` the audit commits; no production runtime data exists yet, so no state migration is needed.

---

## Execution Log & Reasoning

**Baseline (pre-fix):** `uv run pytest` failed to build (hatchling could not detect a package — flat scripts layout). Direct runners: 35/35 tests pass (models 8, state 10, router 9, executor 8).

### Audit Findings & Fixes Applied

| ID | Severity | Location | Finding | Fix |
|----|----------|----------|---------|-----|
| F1 | High | `pyproject.toml` | hatchling build fails ("Unable to determine which files to ship") | `[tool.hatch.build.targets.wheel] bypass-selection = true` |
| F4 | Medium | `daemon.load_config` | naive `//` stripping corrupts string values containing URLs | quote-aware `strip_jsonc()` scanner |
| F8 | Critical | `daemon.main` + `watcher` callback | `asyncio.ensure_future` called from watchdog's background thread → `RuntimeError: no running event loop`; filesystem-detected tasks NEVER entered the pipeline | capture running loop; `run_coroutine_threadsafe` |
| F12 | High | `router.call_llm` | LLM failures returned as `"[LLM ERROR] …"` strings that flowed downstream as approvable plans/reports | raises `RuntimeError`; pipeline crash-guard converts to `CRASHED`; also passes `reasoning_effort` (was dead config) |
| F16 | High | `daemon._process_task` | executor statuses `timeout`/`error`/`transport_error` fell through to QA as successes; `no_progress`/`idle_stuck`/`budget_exceeded` were dead strings never produced by executor | explicit `EXEC_OK`/`EXEC_BLOCKED` classification; everything else crashes |
| F17 | Critical | `gateway.py` | `handle_callback` had NO caller — no Telegram update polling existed anywhere, so every Approve/Reject button silently timed out (1 h) to REJECTED. The engine could never pass plan approval | `_poll_loop()` polls `get_updates` while approvals pending, dispatches callbacks, answers queries |
| F19 | Low | `gateway.request_approval` | `parse_mode="Markdown"` on LLM content breaks entity parsing → whole approval request fails | parse_mode removed |
| F20 | Low | `qa_engine` docstring | evidence dir documented as `<task-id>-<slug>`, code uses `<task-id>` | docstring aligned |
| F22 | Medium | `qa_engine.run_qa/run_review` | `"PASSED" in text` false-positives when a FAILED report quotes criteria containing "approved" | first-occurrence regex `decide()` (`PASSED\|APPROVED\|READY_FOR_CLOSURE` vs `FAILED\|REJECTED\|NEEDS_WORK`) |
| F26 | Critical | `daemon` + docs | setup.md's documented launch (`cd loop-engine && python daemon.py`) resolved every relative path against the wrong CWD → silent fallback to default config with `chat_id=0` | `REPO_ROOT` anchoring: `os.chdir(REPO_ROOT)` at startup + config path resolution |

### Lifecycle Trace (audited, post-fix)

watcher detects `tasks/backlog/*.md` → registers in SQLite (`BACKLOG`) → coroutine scheduled on main loop (`PLANNING`) → router plans via category chain → plan stored → Telegram approval gate w/ live button polling (`AWAITING_APPROVAL`; reject→`BACKLOG`) → OpenCode CLI execution with transport retry (`IMPLEMENTING`) → non-complete statuses crash → QA Engineer review, evidence written, retry counter incremented on FAIL (`QA`; max 3 then `CRASHED`) → Code Reviewer (`REVIEW`; reject→`CRASHED`) → closure approval (`AWAITING_CLOSURE`; approve→`CLOSED`). Admin intervention points: plan approval, closure approval, and crash recovery (manual).

### Provider Extensibility Verdict

Adding a provider = add `"provider/model"` strings to any category + export `{PROVIDER}_API_KEY`. No core changes needed (litellm resolves prefixes; env key auto-derived in `router._resolve_model`). Limitation documented: `ProviderConcurrency` has fixed fields (new providers fall back to litellm defaults until the model is extended); `zai` relies on its Pydantic default when omitted from jsonc.

### Config/JSON/Examples Verdict

`loop-engine.jsonc` validates cleanly against the Pydantic schema (trailing commas/comments handled; `${VAR}` refs supported). Placeholder `approval.chat_id: 0` fails safe (Telegram send error → approval DENIED) but must be set before real use. Docs corrected where they described behavior that never existed (`TELEGRAM_CHAT_ID`, `.env` auto-load).

### Accepted Residual Risks (documented, not fixed)

1. QA retry re-runs PLANNING + plan approval each cycle (wasteful but bounded by `max_qa_retries=3`; redesign deferred).
2. Single shared update poller per gateway instance — concurrent approvals on multiple parallel tasks share one poll loop (acceptable at `max_parallel_tasks ≤ 4`).
3. `_parse_task_metadata` reads files immediately on creation events; editors that create-then-write may produce partial reads (restart-time `scan_existing` recovers).
4. Executor assumes `opencode run --format json` accepts prompt via stdin — unverifiable without invoking a live agent; flagged for first real-world run.
5. Closure rejection leaves state at `AWAITING_CLOSURE` though the log message says "stays in review" (cosmetic inconsistency).

### Post-Fix Verification

49/49 tests pass across 5 suites, exit 0 (14 new characterization tests in `test_audit_fixes.py` cover every fix). Files changed: `loop-engine/{pyproject.toml, daemon.py, gateway.py, router.py, qa_engine.py, test_audit_fixes.py (new)}`, `docs/loop-engine/{setup.md, configuration.md}`, `CHANGELOG.md`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `a8cc649b6bd59cf56a8b8f34adf5a5078cb05844`
<!-- END_GIT_DIFF -->
