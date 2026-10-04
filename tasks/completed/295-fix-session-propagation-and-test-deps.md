# Task 295: Fix Session ID Propagation and Test Dependencies

**File:** `tasks/qa/295-fix-session-propagation-and-test-deps.md`
**Source:** orchestrator
**Type:** bugfix
**Status:** in-progress

## Goal

Mandate explicit `session_id` argument passing in `agents/cognitive-executor.md` to fix HTTP singleton session continuity, and add `pathspec` to `mcp-brain-bridge` dependencies.

## Micro-Task Checklist (Orchestrator blueprint)

- [x] **Step 1:** Cancel and Archive Task 294. (N/A — file never scaffolded, see Assumption A1)
- [x] **Step 2:** Scaffold and Stage Task 295.
- [x] **Step 3:** Enforce Explicit Session Propagation in `agents/cognitive-executor.md`.
- [x] **Step 4:** Add `pathspec` Dependency to `mcp-brain-bridge`.
- [x] **Step 5:** Run Verification & Update Documentation.

## Local TODOs

- [x] Archive Task 294 (cancelled per Manager order) — N/A, file never existed (A1)
- [x] Explicit `session_id: "$OPENCODE_SESSION_ID"` mandate in executor state machine
- [x] `pathspec>=0.12.0` in `mcp-brain-bridge` dependencies + lockfile
- [x] RTK verification green + CHANGELOG entry under `## [9.53.0]` / `### Fixed`

## Acceptance Criteria

- [x] AC1: `agents/cognitive-executor.md` strictly instructs the agent to pass `session_id: "$OPENCODE_SESSION_ID"` in every `brain_turn` call.
- [x] AC2: `mcp-brain-bridge/pyproject.toml` dev/test dependencies include `pathspec>=0.12.0`.
- [x] AC3: Verification suite passes exit code 0.

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py tests/test_brain_preflight.py tests/test_brain_capability.py tests/test_prompt_sync.py -q`
- **Expected result:** pass, exit code 0
- **Actual result:** `327 passed in 1.30s`
- **Exit code:** 0
- **Doc sync:** `python3 scripts/check_docs_sync.py` → `docs-sync: OK`, exit 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** executor wording change is prompt-only (no runtime effect); `pathspec` addition only widens the test env.
- **Rollback plan:** revert `agents/cognitive-executor.md` hunk; remove `pathspec` from `pyproject.toml` and re-lock.

## Execution Log & Reasoning

- **Seat Check:** domains = prompt-doc fix (executor session-binding wording) + test-dependency fix (bridge `pathspec`) → Senior Programmer seat minimum; UX/security triggers absent (no layout/styling/auth/money keywords in title+body) → single-seat plan valid, no Designer/Architect consult.
- **Brainstorm:** not required — single-domain bugfix, fully reversible, no cross-disciplinary ambiguity.
- **Plan verdict:** Orchestrator blueprint present (this XML block) = approved plan; executing from it, no `brain_turn` planning round needed.
- **Validation:** `AGENTS.md` + `docs/conventions.md` read; `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md` absent → skipped gracefully per Absent-File Policy. No rule violations: `git mv` used only for Kanban transitions (permitted exception), no autonomous `git add`/`commit`/`push`.
- **Assumption A1 (Step 1 N/A):** `tasks/in-progress/294-modularize-brain-bridge-server.md` does not exist anywhere — verified via `find tasks -name "*294*"`, `git ls-files | grep 294` (empty), and empty `tasks/in-progress/` + `tasks/backlog/` listings. The 294 task file was evidently never scaffolded before the Manager's YAGNI cancel order arrived (only `tasks/.sessions/294/transcript.jsonl`, a Brain session transcript dir, exists — unrelated to Kanban state). Creating a file solely to archive it would add noise; Step 1 recorded as not-applicable, no `git mv` executed (it would fail on a missing source).
- **Implementation notes:** Step 3 replaced executor state-machine item 1 with the mandated Session Binding block (explicit `session_id: "$OPENCODE_SESSION_ID"` over the wire; prior ambient-auto-detection wording removed per blueprint). Step 4 added `"pathspec>=0.12.0"` under `[project] dependencies` and re-locked (`uv lock` → added pathspec v1.1.1 to `mcp-brain-bridge/uv.lock`). Step 5: `rtk test ...` → 327 passed, exit 0; `check_docs_sync.py` → OK. CHANGELOG `### Fixed` entry added under `## [9.53.0]`. Modified files: `agents/cognitive-executor.md`, `mcp-brain-bridge/pyproject.toml`, `mcp-brain-bridge/uv.lock`, `CHANGELOG.md`.

---

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 0e8d76c..6d27e2d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -41,6 +41,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 - **Bumped system prompt to 9.53.0 (Task 293):** updated prompt fragments (`01-system_version` 9.52.0 → 9.53.0; `09-hands_protocols` automatic-mode chaining now runs under the active session thread instead of the same `task_id`; `22-compaction_protocol` survival contract gains the active session ID), reassembled `system-prompt.md` (byte-verified via assembler), and updated the `test_prompt_sync` version pin. Docs synced: `docs/brain-bridge.md` (session-first history + Environment table document ambient auto-detection), `docs/services.md` (mcp-brain lists `brain_turn` as the singular exposed automation tool), `README.md` + `LLM.txt` (session-thread summaries). Purged deleted file-pull tools (`grep_files`, `read_file`) from `agents/cognitive-executor.md` (new `File context retrieval` section uses native `read`/`grep`/`glob` + `[fed-context]`) and documented ambient `OPENCODE_SESSION_ID` detection in the Brain Bridge state machine. Aligned downstream `skill-templates/audit-agents/SKILL.md` (Buffer Isolation + End-Of-Task Sequence now carry session-thread persistence, project-agnostic wording).
 
+### Fixed
+
+- **Enforced explicit `session_id` transmission (Task 295):** `agents/cognitive-executor.md` now mandates passing `session_id: "$OPENCODE_SESSION_ID"` explicitly in every `brain_turn` call so the remote HTTP singleton session thread continues in `tasks/.sessions/<session_id>/transcript.jsonl` instead of relying on ambient detection. Added `pathspec>=0.12.0` to `mcp-brain-bridge` dependencies (lockfile updated) so the test suite collects cleanly. Brain suites: **327 passed** (exit 0).
+
 ## [9.49.0] - 2026-10-01
 
 ### Added
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 12bb656..22d5075 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -398,14 +398,8 @@ needs no extra machinery.
 1. **Build** the user prompt from current machine state: the instruction
    (e.g. "QA engineer please make the adversarial testing") + the full
    active task file + any prior answers. QA and reviewer turns MUST pass
-   `include_diff=True` so the changed hunks ride along — the Brain judges
-   the actual changes, never a summary. Every `brain_turn` call passes
-   `session_id` alongside `task_id` (session-first): one thread spans
-   the whole work session, while the task file and diff still resolve
-   from `task_id`. A bare `task_id` with no `session_id` keeps the
-   legacy task-keyed transcript. When `session_id` is omitted,
-   `brain_turn` automatically detects `OPENCODE_SESSION_ID` from the
-   environment, ensuring seamless session continuity across tasks.
+   `include_diff=True`.
+   **Session Binding (Mandatory):** You MUST pass `session_id: "$OPENCODE_SESSION_ID"` (reading your active session ID from the environment) in every `brain_turn` call alongside `task_id`. Because the MCP server runs as a separate daemon, you must send this parameter explicitly over the wire so the conversation history continues in `tasks/.sessions/<session_id>/transcript.jsonl`.
 2. **Call** `brain_turn`. Read `status`:
    - `XML_EXTRACTED` — execute `xml_blocks` as the next instruction set,
      exactly like an Orchestrator XML block.
diff --git a/mcp-brain-bridge/pyproject.toml b/mcp-brain-bridge/pyproject.toml
index 2417b70..cd12fa4 100644
--- a/mcp-brain-bridge/pyproject.toml
+++ b/mcp-brain-bridge/pyproject.toml
@@ -6,4 +6,5 @@ requires-python = ">=3.10"
 dependencies = [
     "mcp[cli]>=1.0,<2.0",
     "httpx>=0.28",
+    "pathspec>=0.12.0",
 ]
diff --git a/mcp-brain-bridge/uv.lock b/mcp-brain-bridge/uv.lock
index 270c308..9e1647d 100644
--- a/mcp-brain-bridge/uv.lock
+++ b/mcp-brain-bridge/uv.lock
@@ -390,12 +390,14 @@ source = { virtual = "." }
 dependencies = [
     { name = "httpx" },
     { name = "mcp", extra = ["cli"] },
+    { name = "pathspec" },
 ]
 
 [package.metadata]
 requires-dist = [
     { name = "httpx", specifier = ">=0.28" },
     { name = "mcp", extras = ["cli"], specifier = ">=1.0,<2.0" },
+    { name = "pathspec", specifier = ">=0.12.0" },
 ]
 
 [[package]]
@@ -407,6 +409,15 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/b3/38/89ba8ad64ae25be8de66a6d463314cf1eb366222074cfda9ee839c56a4b4/mdurl-0.1.2-py3-none-any.whl", hash = "sha256:84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8", size = 9979, upload-time = "2022-08-14T12:40:09.779Z" },
 ]
 
+[[package]]
+name = "pathspec"
+version = "1.1.1"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/5a/82/42f767fc1c1143d6fd36efb827202a2d997a375e160a71eb2888a925aac1/pathspec-1.1.1.tar.gz", hash = "sha256:17db5ecd524104a120e173814c90367a96a98d07c45b2e10c2f3919fff91bf5a", size = 135180, upload-time = "2026-04-27T01:46:08.907Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/f1/d9/7fb5aa316bc299258e68c73ba3bddbc499654a07f151cba08f6153988714/pathspec-1.1.1-py3-none-any.whl", hash = "sha256:a00ce642f577bf7f473932318056212bc4f8bfdf53128c78bbd5af0b9b20b189", size = 57328, upload-time = "2026-04-27T01:46:07.06Z" },
+]
+
 [[package]]
 name = "pycparser"
 version = "3.0"
```
<!-- END_GIT_DIFF -->
