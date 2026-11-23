# Task 403: bridge chat completions plus structured tool call routing

**File:** `tasks/completed/403-bridge-chat-completions-plus-structured-tool-call-routing.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-15T08:03:23Z
**Submitted:** 2026-11-15T07:53:21Z
**Started:** 2026-11-15T07:49:33Z
**Supersedes:** [401, 402]
**Meta:** true
**Created:** 2026-11-15 07:37 UTC
**Bundled:** 2 tasks

## Supersedes

This META supersedes 2 source task(s). Each one is archived to `tasks/archive/` with a `**Superseded-By:** 403-bridge-chat-completions-plus-structured-tool-call-routing` marker and stays reachable via `git log --oneline --follow -- tasks/archive/<id>-*.md`:

- `401` — Bridge chat completions to responses API in mcp-brain-bridge
- `402` — Structured tool-call routing for the Brain output channel

Execution is all-or-nothing: every line of `## Bundled Checklist (All-or-Nothing)` must pass, otherwise the whole META is `QA_REJECTED` and returns to `in-progress`. A partial close is forbidden.

## Goal

Unified execution of 2 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [401, 402] — "bridge chat completions plus structured tool call routing" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

> ⚠️ **Guardrail Warning:** Combined source size is 1402 LOC (> 400). Unified META diff may be large and hard to review. Consider splitting into two METAs.

**Source IDs:** [401, 402]
**Next ID:** 403 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 403-bridge-chat-completions-plus-structured-tool-call-routing` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 2 small related tasks together and speed up turnaround.

**Traceability:**

- Supersedes [401, 402] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 403-bridge-chat-completions-plus-structured-tool-call-routing` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**

- Cap 6 per bundle — this bundle has 2 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 1402 LOC (⚠️ exceeds 400 — consider split)

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 401: Bridge chat completions to responses API in mcp-brain-bridge

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/qa/401-bridge-chat-completions-to-responses-api.md` → `tasks/archive/401-bridge-chat-completions-to-responses-api.md` (after bundling)

**Title:** Bridge chat completions to responses API in mcp-brain-bridge

#### Goal (verbatim)

Enable `mcp-brain-bridge` to serve models supporting only OpenAI-compatible Chat Completions endpoints (e.g. MiniMax Flash or custom OpenAI chat providers) alongside native Responses API endpoints via an upstream mode adapter.

#### Manager's Notes (verbatim)

Direct user request: "create a task and complete task and test it to see works".
Architectural decision: Add a clean adapter / translation layer between high-level prompt assembly and HTTP transport in `mcp-brain-bridge/server.py`, configured via `BRAIN_UPSTREAM_MODE` (`responses` default, `chat_completions` optional).

#### Acceptance Criteria (verbatim)

- [x] `BRAIN_UPSTREAM_MODE` defaults to `responses`, preserving 100% backward compatibility
- [x] When `BRAIN_UPSTREAM_MODE=chat_completions`, requests are translated to `/chat/completions` schema (`messages` array, system role mapped, etc.)
- [x] Chat completions responses are parsed into valid text output and diagnostics
- [x] Offline unit tests pass with 0 failures
- [x] All code passes lint and type checks
- [ ] A real `/chat/completions` round trip is proven against a live provider endpoint — DEFERRED: no `chat_completions` provider credential exists in this environment, so the probe is blocked. Follow-up recorded in `## Risk & Rollback`.

#### Local TODOs (verbatim)

- [x] Add `BRAIN_UPSTREAM_MODE` support in `mcp-brain-bridge/server.py`
- [x] Implement translation from Responses payload to Chat Completions payload (`messages`, `model`, `max_tokens`, etc.)
- [x] Implement response parsing from Chat Completions response (`choices[0].message.content`, usage token mapping)
- [x] Add comprehensive unit tests in `tests/test_brain_bridge.py`
- [x] Run test suite with rtk and check formatting/linting
- [x] Stage diff and transition to QA

#### Risk & Rollback (verbatim)

- **Risk:** Regression in existing Responses API path.
- **Mitigation:** Default mode remains `responses`; test suite tests both modes explicitly.
- **Rollback:** Unset `BRAIN_UPSTREAM_MODE` or revert changes to `mcp-brain-bridge/server.py`.
- **R1 (open, Manager-owned):** the live probe is blocked for lack of a credential. `BRAIN_UPSTREAM_MODE=chat_completions` has never answered a real endpoint; only offline fakes prove the mapping. Provide a key plus base URL in the environment, or approve closure with the live probe recorded as a follow-up.

#### Verification Evidence (verbatim)

- **Command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q`
- **Expected result:** All test cases pass
- **Actual result:** `354 passed in 2.92s`
- **Exit code:** 0
- **Format gate:** `rtk test uv run --project mcp-brain-bridge --with ruff ruff format mcp-brain-bridge/server.py tests/test_brain_bridge.py` (exit 0)
- **Live probe status:** `Live probe STILL BLOCKED: no chat_completions provider credential in environment; escalate to Manager for a key.` `env | grep -c "MINIMAX\|OPENAI_API_KEY\|OPENROUTER"` returns `0`. URL resolution verified: `BRAIN_UPSTREAM_MODE=chat_completions uv run --project mcp-brain-bridge python -c "import sys; sys.path.insert(0,'mcp-brain-bridge'); import server; print(server._upstream_url())"` -> `https://openrouter.ai/api/v1/chat/completions` (exit 0).

---

### Source Task 402: Structured tool-call routing for the Brain output channel

**Original File:** `/home/mohammad/cognitive-lead-hq/tasks/backlog/402-structured-tool-call-routing.md` → `tasks/archive/402-structured-tool-call-routing.md` (after bundling)

**Title:** Structured tool-call routing for the Brain output channel

#### Goal (verbatim)

Give the Brain a structured tool-call channel instead of flattened text, so a consumer can dispatch a tool call programmatically rather than parse it out of prose.

#### Manager's Notes (verbatim)

Follow-up recorded during task 401 review. The chat-completions bridge currently renders a `function_call` output item as `name(arguments)` plain text in `parse_responses_text`. That is a deliberate contract for the bridge, documented in `mcp-brain-bridge/DECISIONS.md` ADR-014, and must not be changed inside task 401.

#### Acceptance Criteria (verbatim)

- [ ] A tool-call-only response is distinguishable from prose without text parsing
- [ ] Both `responses` and `chat_completions` modes produce the same structured shape
- [ ] Offline unit tests cover both modes

#### Local TODOs (verbatim)

- [ ] Define the structured output shape the Brain consumes for a tool call
- [ ] Decide whether the channel is a new return field or a parsed block
- [ ] Implement and test both upstream modes
- [ ] Update ADR-014 and the bridge README

#### Risk & Rollback (verbatim)

- **Risk:** A new output field changes what the Hands reads.
- **Mitigation:** Additive field only; the existing text channel stays unchanged.
- **Rollback:** Revert the field addition.

#### Verification Evidence (verbatim)

_Pending implementation._

---

## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [x] [401] `BRAIN_UPSTREAM_MODE` defaults to `responses`, preserving 100% backward compatibility
- [x] [401] When `BRAIN_UPSTREAM_MODE=chat_completions`, requests are translated to `/chat/completions` schema (`messages` array, system role mapped, etc.)
- [x] [401] Chat completions responses are parsed into valid text output and diagnostics
- [x] [401] Offline unit tests pass with 0 failures
- [x] [401] All code passes lint and type checks
- [ ] [401] A real `/chat/completions` round trip is proven against a live provider endpoint — DEFERRED: no `chat_completions` provider credential exists in this environment, so the probe is blocked. Follow-up recorded in `## Risk & Rollback`.
- [x] [402] A tool-call-only response is distinguishable from prose without text parsing
- [x] [402] Both `responses` and `chat_completions` modes produce the same structured shape
- [x] [402] Offline unit tests cover both modes
- [x] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [ ] Step 1: Validate META bundle — confirm all 2 source requirements are captured verbatim below
- [ ] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [ ] [401] Add `BRAIN_UPSTREAM_MODE` support in `mcp-brain-bridge/server.py`
- [ ] [401] Implement translation from Responses payload to Chat Completions payload (`messages`, `model`, `max_tokens`, etc.)
- [ ] [401] Implement response parsing from Chat Completions response (`choices[0].message.content`, usage token mapping)
- [ ] [401] Add comprehensive unit tests in `tests/test_brain_bridge.py`
- [ ] [401] Run test suite with rtk and check formatting/linting
- [ ] [401] Stage diff and transition to QA
- [x] [402] Define the structured output shape the Brain consumes for a tool call
- [x] [402] Decide whether the channel is a new return field or a parsed block
- [x] [402] Implement and test both upstream modes
- [x] [402] Update ADR-014 and the bridge README
- [x] Step 13: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [x] Step 14: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [x] [401] `BRAIN_UPSTREAM_MODE` defaults to `responses`, preserving 100% backward compatibility
- [x] [401] When `BRAIN_UPSTREAM_MODE=chat_completions`, requests are translated to `/chat/completions` schema (`messages` array, system role mapped, etc.)
- [x] [401] Chat completions responses are parsed into valid text output and diagnostics
- [x] [401] Offline unit tests pass with 0 failures
- [x] [401] All code passes lint and type checks
- [ ] [401] A real `/chat/completions` round trip is proven against a live provider endpoint — DEFERRED: no `chat_completions` provider credential exists in this environment, so the probe is blocked. Follow-up recorded in `## Risk & Rollback`.
- [x] [402] A tool-call-only response is distinguishable from prose without text parsing
- [x] [402] Both `responses` and `chat_completions` modes produce the same structured shape
- [x] [402] Offline unit tests cover both modes
- [x] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q`
- **Expected result:** all tests pass
- **Actual result:** `360 passed in 3.66s` (354 baseline + 6 new `test_tool_calls_*`)
- **Exit code:** 0
- **Format gate:** `rtk test uv run --project mcp-brain-bridge --with ruff ruff format mcp-brain-bridge/server.py tests/test_brain_bridge.py` → `2 files left unchanged`, exit 0
- **TDD RED proof:** new tests run pre-implementation → `4 failed (AttributeError), 354 deselected`
- **Ruff check note:** bare default-rule `ruff check` reports 150 pre-existing hits on unmodified HEAD (UP045 bulk across the file) — not the project's gate; the diff adds only file-convention `except Exception` guards plus one site narrowed to `(ValueError, TypeError)`
- **Lint:** `lint_task_file` on the META file → clean after header sync (`File:` backlog→in-progress) + blank-line fix
- **Live probe (401, still deferred, NOT claimed):** no `chat_completions` provider credential in this environment; Manager-owned R1 stands

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [401, 402], remove Superseded-By footer, delete or archive `tasks/backlog/403-bridge-chat-completions-plus-structured-tool-call-routing.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

### Autopilot 2026-11-15 — bundling + planning (no code written yet)

- **Intent validation:** clarity 5 — bundle 401+402 and drive META to finish on autopilot. Assumption A1: "auto mode" = supervised autopilot (locked, announced).
- **Bundle:** `bundle_tasks([401,402])` dry-run clean → real run created META `403-bridge-chat-completions-plus-structured-tool-call-routing` in `tasks/backlog/`; sources archived with superseded markers (staged `git mv`, uncommitted per ZAC).
- **Baseline:** 401's code is in HEAD and green — `rtk test ... tests/test_brain_bridge.py` → 354 passed. `tasks/in-progress/` empty; `tasks/qa/` holds only 0386.
- **Blocker B1 (planner circuit-breaker, NOT bypassed):** `claim_next(403)` refused — QA budget exhausted, 0386 awaits resolution in `tasks/qa/`. 403 stays in `backlog/`; no code written until claimed.
- **Seat Check (pre-planning):** backend-only additive change → Senior Programmer; skipped Architect (no layer/schema change), Designer (no UI surface), Strategist/Planner (no priority call), QA/Reviewer (chained post-implement). Brainstorm: not required — single-discipline, reversible, no cross-seat trigger.
- **Claim gate re-attempt (post-XML):** `claim_next(403)` refused again — QA budget exhausted, 0386 still in `tasks/qa/`. Blocker B1 still present. Zero code written, per XML claim gate. Autopilot parked here: the moment 0386 resolves, the loop continues with claim → steps 1–6 → gates → stage → QA transition → chained QA/review, no further approval needed (plan already Approved).
- **B1 lifted:** Manager closed 386 ("Close task" via question tool) → `git mv` to `tasks/completed/`, headers synced, `commit_and_clean_task` committed closure. Index was pre-cleaned via `unstage_files` (4 bundle paths) so the 386 commit holds only the closure; bundle renames re-staged after. `claim_next(403)` succeeded — 403 in `tasks/in-progress/`, header synced backlog→in-progress.
- **Stack-skill binding (explicit skip, per XML):** repo root markers scanned (`pyproject.toml` absent at root, `mcp-brain-bridge/pyproject.toml` present, no `package.json`/`build.gradle.kts`). No registry stack skill exactly matches a stdlib MCP bridge server; closest discipline-only candidate `python-fastapi` does not cover MCP stdio/streamable-http transport. Recorded as skip — proceeding with Python stdlib discipline. Skill loads: `kanban-lifecycle`, `testing-verification` (TDD red-green + fresh-evidence gate), `code-search`, `project-memory` (index read + `search_memory` for bridge constraints; ADR-014 carried in task file).
- **Grounding (all verified by grep before edit):** result assembly `server.py#L5097-5118`, normalized variable `resp_data` (`parse_responses_text(resp_data)` at L4903), `_build_responses_output` L5380, `parse_responses_text` L6102-6126, `json`+`os` already imported (L63/L66 — no duplicate imports). Test style: `import server as bridge` (test file L21).
- **TDD RED:** 4 new tests appended first → `4 failed (AttributeError), 354 deselected`.
- **Implementation (GREEN):** `extract_tool_calls` inserted after `_build_responses_output` (shared, both modes, never raises; scalar-JSON kept under `_value`, dict args pass through, raw always stringified); wiring hunk after result dict reads `resp_data["output"]` with mode fallback and `[]` default. `parse_responses_text` untouched. One `except` narrowed to `(ValueError, TypeError)`; the three wiring `except Exception` carry the file's "never fail a turn" convention comments (19 pre-existing BLE001 in file).
- **Docs:** ADR-014 addendum + bridge README structured-channel bullet appended.
- **Gates:** `ruff format` exit 0 (2 files unchanged); full suite `358 passed` (354+4). Bare `ruff check` reports 150 pre-existing default-rule hits on HEAD (UP045 bulk) — not the project's gate (401 passed with the same profile); my diff adds only file-convention blind-excepts, one narrowed.
- **Manager accept (closure gate):** exact answer "Approved for closure" via question tool on the PO_REVIEW_PENDING relay. Preconditions verified: file in `tasks/qa/`, log records PO_REVIEW_PENDING. Requesting Senior Programmer closure XML.
- **QA verdict: QA_PASSED.** QA Engineer adversarial pass: text channel preserved (360 green, no baseline regression), malformed inputs degrade safely, identical shape both modes, quota/status untouched. Two non-blocking polish notes (M1/M2) adopted as extra tests before review. 401 live probe out of scope (no credential).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

**Factual Git Diff:** Stored in Commit Hash: `b43b1bf17eb30f02933e4c27c0f6927ac4c821a3`
<!-- END_GIT_DIFF -->
