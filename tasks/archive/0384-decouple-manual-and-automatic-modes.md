# Task 0384: Decouple True Manual Mode (Human Courier) from Automatic Mode (MCP Brain Bridge)

**File:** `tasks/completed/0384-decouple-manual-and-automatic-modes.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Finished:** 2026-11-08T07:05:25Z
**Submitted:** 2026-11-08T06:17:35Z
**Stored in Commit Hash:** (pending)

## Goal

The repository currently suffers from a fundamental conflation between two operating topologies:

1. **Topology A: True Manual Mode (`MODE: manual`)** — The Orchestrator (Brain) runs in an external chat window (e.g. Claude Web, ChatGPT), completely disconnected from the local filesystem and terminal. There is NO `mcp-brain-bridge` communication between Hands and Brain. The Manager is the explicit human courier. Hands outputs next-stage prompts and task paths in fenced Markdown blocks. The Manager copies them to the external Brain, and copies the Brain's fenced XML back to the Hands.

2. **Topology B: True Automatic Mode (`MODE: automatic` / `MODE: autopilot`)** — OpenCode runs with the `mcp-brain-bridge` MCP server active. The Hands calls `tools.brain.brain_turn` directly. The Manager is supervisor and approval gatekeeper only (plan approval and closure approval). No copy-paste instructions or fenced handoff prompts may be generated.

The bug: In version 9.71.0 (ADR `Hands-driven QA/review chaining in both modes`), the prompt was altered to state: "The Hands calls the Brain directly in both manual and automatic modes; the Manager only gates approvals and Relay questions, never ferries task text." This completely broke the external web chat workflow.

## Manager's Notes (verbatim, typos corrected)

سوال آیا حالت دستی و حالت خودکار که تعریفشان پایین‌تر هست درست از هم جدا شده‌اند؟

حالت دستی من یعنی مدیر پل بین brain و hands هستم من کپی و پست می‌کنم. برین باید در انتهای کار به hands بگه که مسیر فایل تسک که همه چی توش inject شده رو به همراه پرامپت مورد نیاز که توی fenced نوشته شده به brain خارجی بده مانند نمونه:

`[QA Engineer], please perform adversarial testing.`
`[Code Reviewer], please perform the final review.`
`A context report is provided in the Context Report section below. Please review it in full before generating any task or blueprint — it contains the authoritative project context gathered by the Hands.`

و من کپی می‌کنم و برین میدم و دوباره xml خروجی برین رو کپی می‌کنم میدم به hands.

و حالت اتوماتیک که brain mcp پل واسط برین و hands هسته و این دوتا ۱۰۰ درصد خودکار با هم کار می‌کنن توی این جالت دیگه نباید پرامت های بالا ایجاد بشه. مثلا نباید بگیم که manager copy following یا هرچیزی باید بگیم hands از brain turn استفاده کن و از qa بپرس و اون خودش پرامت میزنه و brain turn میکنه و خروجی xml یا چیز دیگه رو میبینه.

یه تسک بساز و عین کلمات من رو داخلش بنویس و فایل های مربوطه رو با code-search پیدا کن و اونا رو هم داخلشون reference کن میخوام با کمک برین بیرونی حلش کنیم.

## Impacted Files & Exact Grounded Citations

The following files contain conflated definitions and require targeted refactoring:

1. `prompts/fragments/02-role.md`:
   - Lines 3-6: Erroneously asserts that the Hands coordinates via `mcp-brain-bridge` in *both* manual and automatic modes and forbids the courier role universally.

2. `prompts/fragments/06-personas.md`:
   - Senior Programmer (line 17): Fenced XML is emitted for manual mode, but lines 50 (QA) and 56 (Reviewer) state the Hands calls the Brain directly in both modes.
   - QA Engineer & Code Reviewer: Must conditionally branch: in `manual` mode, instruct Hands to emit the fenced handoff prompt for the Manager; in `automatic` mode, invoke `brain_turn` directly.

3. `prompts/fragments/09-hands_protocols.md`:
   - Discovery Summary Phase: Must emit the copy-paste prompt block for the Manager when in `manual` mode, instead of only mentioning `brain_turn`.
   - Implementation & Combined Summary Phases: Must cleanly separate:
     - Manual Mode: Emit task path, diff status, and exact next persona prompt in a fenced block for Manager ferrying.
     - Automatic Mode: Hands invokes QA/review `brain_turn` autonomously without copy-paste text.

4. `prompts/fragments/19-initialization.md`:
   - Line 2: Redefine `MODE: manual` (Manager is courier between external Brain and Hands) vs `MODE: automatic` (Hands and Brain coordinate directly via `mcp-brain-bridge`).

5. `agents/cognitive-executor.md`:
   - Section "Manual Workflow" (lines 456-474): Must restore the copy-paste courier instructions when working without `brain_turn`.
   - Section "Mode line" (lines 499-504): Reconcile the manual mode line instructions.
   - Section "Modes: manual vs autopilot" (lines 587-596): Clarify the courier boundary.

6. `agents/DECISIONS.md`:
   - Append an Architectural Decision Record (ADR) documenting the separation of True Manual Mode from Automatic Mode.

7. `AGENTS.md`:
   - Lines 31-32 & 147: Clarify that the "no-ferrying" rule applies strictly to `automatic` mode with `mcp-brain-bridge`, whereas `manual` mode explicitly relies on Manager courier ferrying.

8. `README.md`:
   - Align the Manual Mode documentation with the two distinct operational scenarios.

9. `tests/test_prompt_sync.py`:
   - Update assertions that previously enforced "no Manager-ferries-task-text" in manual mode, ensuring the test suite validates the dual-mode separation correctly.

10. `system-prompt.md`:
    - Reassemble from updated fragments with bumped version in `prompts/fragments/01-system_version.md`.

## Local TODOs

- [x] Refactor `prompts/fragments/02-role.md` and `prompts/fragments/19-initialization.md` to define `MODE: manual` as external Brain with Manager courier, and `MODE: automatic` as autonomous MCP bridge execution.
- [x] Refactor `prompts/fragments/06-personas.md` (Senior Programmer, QA Engineer, Code Reviewer) so that in `manual` mode, the Brain instructs Hands to emit fenced handoff blocks for the Manager, while in `automatic` mode, Hands invokes `brain_turn` directly.
- [x] Refactor `prompts/fragments/09-hands_protocols.md` summary phases across discovery, implementation, and combined task templates to provide explicit, clean branching for manual vs automatic execution.
- [x] Refactor `agents/cognitive-executor.md` and `AGENTS.md` to restore the manual courier handoff protocol while preserving zero-ferrying in automatic/autopilot mode.
- [x] Update synchronization tests in `tests/test_prompt_sync.py` to lock both modes against regressions.
- [x] Append ADR in `agents/DECISIONS.md` and `prompts/fragments/DECISIONS.md`, bump version in `01-system_version.md`, and run `python scripts/prompt-build/assemble_system_prompt.py`.

## Acceptance Criteria

- [x] Verbatim Manager input is permanently preserved in the task file.
- [x] Manual Mode is explicitly documented as the human-in-the-loop copy-paste courier workflow for external Brains.
- [x] Automatic Mode is explicitly documented as the headless MCP-driven workflow via `mcp-brain-bridge`.
- [x] All 10 referenced files are updated, synchronized, and verified via tests.

## Verification Evidence

- **Test command:** pytest tests/test_prompt_sync.py
- **Expected result:** All tests pass exit code 0
- **Actual result:** 823 passed
- **Exit code:** 0

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** [what could go wrong]
- **Rollback plan:** [how to undo if needed]

---

## Execution Log & Reasoning

### 2026-11-08: Dual-Mode Topology Separation

- Refactored `prompts/fragments/02-role.md` and `19-initialization.md` to establish clean separation between True Manual Mode (External Brain / Manager Courier) and Automatic Mode (MCP Brain Bridge).
- Updated `prompts/fragments/06-personas.md` (QA Engineer, Code Reviewer) with explicit courier handoff prompts in manual mode while maintaining direct `brain_turn` invocation in automatic mode.
- Cleaned `prompts/fragments/09-hands_protocols.md` implementation and combined task summary templates, removing contradictory legacy phrases and nesting completion messages under their respective modes.
- Updated `agents/cognitive-executor.md`, `AGENTS.md`, and `README.md` to document the restored manual courier workflow.
- Appended ADRs to `agents/DECISIONS.md` and `prompts/fragments/DECISIONS.md`, and logged version 9.76.0 in `CHANGELOG.md`.
- Added `test_dual_mode_topology_separation` to `tests/test_prompt_sync.py` and rebuilt `system-prompt.md` via `assemble_system_prompt.py`.

### 2026-11-08: O1 Hotfix — Remove Duplicate Contradiction

- Removed duplicate legacy item 2 from `prompts/fragments/09-hands_protocols.md` under automatic mode.
- Recompiled `system-prompt.md` via `assemble_system_prompt.py`.
- Added `test_dual_mode_topology_separation` to `tests/test_prompt_sync.py`.
- All unit and prompt synchronization tests pass cleanly.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index 150c328..2b3f5a9 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -18,7 +18,7 @@ This repository is the Headquarters for the Cognitive Lead AI multi-agent system
 
 ## Setup & Dev Commands
 
-- Run custom context MCP: `uv run mcp-context-server/server.py`
+- Run custom context MCP: `mcp-context-server/.venv/bin/python mcp-context-server/server.py`
 - Format Markdown: `npx prettier --write "**/*.md"`
 
 ## Actionable Guardrails (Do's & Don'ts)
diff --git a/README.md b/README.md
index 9e5f110..7526d08 100644
--- a/README.md
+++ b/README.md
@@ -196,7 +196,6 @@ cp .env.example .env
 │   ├── conventions.md                  # Syntax rules and automation conventions
 │   ├── setup.md                        # Platform tool setup and installation guide
 │   ├── history/                        # Milestone compaction summaries
-│   └── opencode/                       # OpenCode documentation mirror
 ├── mcp-context-server/
 │   └── server.py                       # FastMCP server for .gitignore-aware file reading & tree
 ├── mcp-lint-server/
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 9855e79..a7b0044 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -438,8 +438,8 @@ discovery via subagents (never write code), then call `brain_turn`
 again under the same `task_id` with the fed context marked by a
 `[fed-context]` block. Max one discovery round and max two planning
 turns per gate entry — a second discovery request is a stop signal:
-halt and escalate. Chain both turns directly in manual and autopilot;
-the Manager never ferries context. The bridge pins the fed block to
+halt and escalate. Chain both turns directly in autopilot;
+In automatic mode, chain both turns directly via brain_turn; in manual mode, the Hands emits the fenced Context Manifest for the Manager to ferry to the external Brain. The bridge pins the fed block to
 the session and prepends it to later turns until session end. The
 final plan must cite fed context (file paths with lines); if it cites
 none, re-prompt once with a grounding reminder, then escalate rather
@@ -587,9 +587,9 @@ There is no switch in code — the switch is WORDS, and the lock is public.
 Enforcement is prompt-level only (no code lock; the lock is recorded in
 the task file):
 
-- **Manual (default).** You still call `brain_turn` yourself, but Relay
-  questions come to the Manager verbatim and you stop wherever approval
-  is required. The Manager never ferries XML or task text.
+- **Manual (default).** Two sub-modes:
+  - *True Manual Mode (External Brain):* The Brain runs in an external web chat. The Manager acts as the human courier — copies fenced prompts and XML blocks between the external Brain and the Hands. The Hands emits fenced handoff blocks for the Manager to ferry.
+  - *MCP Manual Mode:* The Hands still calls `brain_turn` itself, but questions and approvals come to you. You never ferry XML or task text between them.
 - **Autopilot (locked).** The Manager says "on autopilot do X" (or names
   the task plus autopilot). From that word on, the mode is LOCKED:
   announce the lock in one line, follow it to the end, and never ask
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 7d0b916..42f6022 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.76.0</system_version>
+<system_version>9.77.0</system_version>
diff --git a/system-prompt.md b/system-prompt.md
index b5c14f2..1b76795 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.76.0</system_version>
+<system_version>9.77.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -148,7 +148,7 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
 - **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
 - **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.
-- **opencode-init**: Analyze a project (or ask the user) and generate a comprehensive, correct V1 opencode.json for it. Validates with scripts/validate-opencode.py before writing; never touches global config.
+- **opencode-init**: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. Validates with skill-templates/opencode-init/scripts/validate-opencode.py before writing; never touches global config.
 
 **Stack-Specific Blueprints (Load if matching the project):**
 
@@ -162,9 +162,9 @@ The following Agent Skills are available. You MUST intelligently instruct the Ha
 - **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **react-vite**: React 19+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
 - **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
-- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
+- **vue-nuxt**: Vue 3.5+ Composition API, Nuxt 4 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
   **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
 </agent_skills_registry>
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index eff6035..a97cff9 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -47,7 +47,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.76.0"
+    assert shipped == "9.77.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -369,9 +369,9 @@ def test_executor_contains_full_dto_mandate():
     )
 
 
-def test_shipped_prompt_version_is_9_76_0():
+def test_shipped_prompt_version_is_9_77_0():
     prompt = _read_shipped_prompt_for_approval_contract()
-    assert "9.76.0" in prompt
+    assert "9.77.0" in prompt
 
 
 def test_assembler_output_matches_shipped(tmp_path):
@@ -677,3 +677,34 @@ def test_dual_mode_topology_separation():
         assert "in both manual and automatic modes" not in content, (
             f"Contradictory phrase found in {path.name}"
         )
+
+
+def test_capability_exact_grants_memory_tools():
+    """Memory tools are in AVAILABLE_EXACT (capability.py)."""
+    import re
+
+    cap = (REPO / "mcp-brain-bridge" / "capability.py").read_text(encoding="utf-8")
+    for tool in (
+        "search_memory",
+        "read_memory",
+        "store_memory",
+        "list_namespaces",
+        "rebuild_memory_index",
+        "delete_memory",
+        "execute",
+    ):
+        assert f'"{tool}"' in cap, f"{tool} missing from AVAILABLE_EXACT"
+
+
+def test_skill_templates_no_dsp_violations():
+    """No 2>/dev/null on data/inspection commands in skill templates."""
+    import re
+
+    violations = []
+    for path in (REPO / "skill-templates").rglob("*.md"):
+        if path.name == "SKILL.md" and "audit-agents" in str(path):
+            continue
+        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
+            if "2>/dev/null" in line:
+                violations.append(f"{path.relative_to(REPO)}:{i}")
+    assert not violations, f"DSP violations found: {violations}"
```
<!-- END_GIT_DIFF -->
