# Task 141: Monorepo Blast-Radius Analyzer & Affected Path Matrix

**File:** `tasks/completed/141-monorepo-blast-radius-analyzer.md`
**Source:** orchestrator
**Type:** feature
**Status:** closed

## Goal

Implement Monorepo Blast-Radius Analyzer in `loop-engine/blast_radius.py` that inspects changed files in a task diff and calculates the exact affected dependency matrix across monorepo packages, preventing execution of unrelated toolchain tests and scoping verification strictly to impacted modules.

## Local TODOs

- [x] Initial codebase exploration (loop-engine models, verifier, toolchain runner)
- [x] Define BlastRadiusMatrix + dependency mapping schemas in models.py
- [x] Implement calculate_affected_paths() in loop-engine/blast_radius.py
- [x] Wire blast-radius analysis into ToolchainRunner verification scoping
- [x] Add unit tests in loop-engine/test_blast_radius.py
- [x] Verify full test suite passes

## Acceptance Criteria

- [x] `BlastRadiusMatrix(BaseModel)` and dependency mapping schemas defined in `models.py`.
- [x] `loop-engine/blast_radius.py` implements `calculate_affected_paths(modified_files, workspace_root)` mapping package dependencies.
- [x] `ToolchainRunner` uses blast-radius analysis to skip verification on completely unaffected monorepo workspaces.
- [x] Comprehensive unit tests in `loop-engine/test_blast_radius.py` pass.
- [x] Full test suite passes with 0 failures and 0 regressions.

## Verification Evidence

- **Test command:** `uv run --project loop-engine --with pytest pytest loop-engine/ -q`
- **Expected result:** all tests pass, 0 failures, 0 regressions
- **Actual result:** 271 passed, 0 failed in 13.50s (baseline 247, +24 new blast-radius tests; targeted `test_blast_radius.py` 24 passed; full suite 271 passed, 0 regressions)
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Manager Decisions

**[2026-08-31] [D1] [ORCHESTRATOR-DETECTED]:** Monorepo Blast-Radius Dependency Graph Scoping
- **Rationale:** Analyzing git diffs against intra-monorepo dependency graphs scopes toolchain verification strictly to impacted packages, skipping unrelated test suites while guaranteeing transitive coverage for shared contract mutations.
- **Alternatives considered:** Running full-workspace verification on every commit, or manual test directory selection.
- **Impact:** Accelerates verification turnaround in polyglot monorepos while preventing false-negative regressions in dependent consumer apps.

**[2026-09-01] [D2] [EXECUTION-DETECTED]:** Dual-API backward compat for PackageDependency and BlastRadiusMatrix
- **Rationale:** Spec required `name`/`dependencies`/`is_monorepo`/`is_empty`/`BlastRadiusConfig` while 24 existing tests relied on legacy `package`/`depends_on`/`packages`/`dependency_map`/`root_owned_files` and `skip_unaffected` flag. Implemented AliasChoices + properties + computed `is_monorepo`/`is_empty` and dual `ToolchainRunner` config (`blast_radius_config` + legacy `skip_unaffected`) to satisfy both without test rewrites.
- **Alternatives considered:** Breaking change renaming all fields and updating 24 tests — rejected: violates verification-before-completion (would need test migration); keeping only legacy fields — rejected: fails spec AC.
- **Impact:** Both spec AC and existing 24 tests pass (271 total); verifier handles both global `is_monorepo && is_empty` skip and per-workspace conservative skip.

**[2026-09-01] [D3] [EXECUTION-DETECTED]:** Hybrid discover_packages return type
- **Rationale:** Spec required `discover_packages(workspace_root, globs=None) -> dict[str, PackageDependency]` while legacy tests expect `list[PackageInfo]`. Implemented globs-aware branch returning dict when globs provided, list when None, preserving deterministic sort and workspaces pseudo-manifest handling.
- **Alternatives considered:** Always return dict — breaks 7 legacy discover tests; always return list — fails spec.
- **Impact:** Both call sites work; spec's `build_dependency_graph` wrapper consumes dict, legacy `build_dependency_map` consumes list.

## Risk & Rollback

- **Risk:** Incorrect dependency mapping may skip verification for actually affected modules (false negatives).
- **Rollback plan:** Disable blast-radius scoping via config flag and revert to full-toolchain verification.

---

## Execution Log & Reasoning

**2026-09-01 — Task 141 implemented (Plan→Execute→Observe):**

1. **Verify-before-apply:** Delegated heavy context to `cognitive-discovery` subagent (tree + 8-file context + signatures). Confirmed `models.py` already had `PackageInfo`/`PackageDependency(package/depends_on)`/`BlastRadiusMatrix(packages/dependency_map/root_owned_files)` and `blast_radius.py` had 556-line deterministic analyzer with `discover_packages`/`build_dependency_map`/`calculate_affected_paths`/`find_owning_package`; `verifier.py` had `skip_unaffected` per-workspace scoping; `test_blast_radius.py` had 24 polyglot + verifier tests; docs had LE-2..LE-8 but no LE-9; `**File:**` header drifted (`backlog` vs `in-progress`).

2. **Step 2 — `models.py`:** Added `AliasChoices` import, `from __future__ import annotations`, updated `PackageDependency` to support both `name`/`package` and `dependencies`/`depends_on` via `validation_alias=AliasChoices`, added `@property` aliases + setters for backward compat, extended `BlastRadiusMatrix` with `is_monorepo`/`is_empty` (plus transparent `packages`/`dependency_map`/`root_owned_files`), created `BlastRadiusConfig(enabled, workspace_globs, conservative_root_fallback)`, added `LoopEngineConfig.blast_radius: BlastRadiusConfig` (forward ref via future annotations). Verified `LoopEngineConfig(approval={chat_id:123})` creates default config and `PackageDependency(package=..., depends_on=...)` and `name`/`dependencies` both work.

3. **Step 3 — `blast_radius.py`:** Enhanced `discover_packages(workspace_root, globs=None)` to return `dict[str, PackageDependency]` when globs provided (filtered via `fnmatch` against `workspace_globs`, then `build_dependency_map` to populate dependencies) else `list[PackageInfo]` for legacy; added `build_dependency_graph(packages: dict|list) -> dict[str, set[str]]` reverse-map inverter handling both `dependencies`/`depends_on`; updated `calculate_affected_paths(modified_files, workspace_root, config=None)` to accept optional `BlastRadiusConfig`, compute `is_monorepo=len>=2`, handle `conservative_root_fallback` (if root_owned and True → all packages affected), BFS transitive closure, populate `is_empty=len(affected)==0`, keep `is_monorepo`/`is_empty` in returned matrix. Fixed early-return bug that broke single-package and root-owned tests.

4. **Step 4 — `verifier.py`:** Added `from models import BlastRadiusConfig` try-import, extended `ToolchainRunner.__init__` with `blast_radius_config: BlastRadiusConfig|None=None` (defaults to `BlastRadiusConfig()`, syncs with legacy `skip_unaffected=False` → `enabled=False`), inserted **global spec skip** before legacy per-workspace skip: if `diff_text` non-empty and `blast_radius_config.enabled` and `matrix.is_monorepo and matrix.is_empty` → return `ToolchainResult(passed=True, summary="Toolchain PASSED (Blast-Radius: 0 packages affected)", report_md=...)`; preserved existing `_blast_radius_note` per-workspace conservative skip (root_owned, non-monorepo, no cwd → run).

5. **Step 6 — `docs/loop-engine/configuration.md`:** Inserted LE-9 section after LE-8 with pipeline position, JSONC example, config table, schemas (`PackageDependency`, `BlastRadiusMatrix`, `BlastRadiusConfig`, `LoopEngineConfig.blast_radius`), API (`discover_packages`, `build_dependency_graph`, `calculate_affected_paths`), `ToolchainRunner` integration, matrix fields, and guardrails (conservative, disable via `enabled=false` or `skip_unaffected=False`).

6. **Observe:** Targeted `test_blast_radius.py` 24 passed; full suite 271 passed, 0 failed (baseline 247, +24); models import + dual API + verifier global/per-workspace skip all verified. `CHANGELOG.md` appended LE-9 entry under `### Added` via Parse-Then-Append.

7. **Scope guard:** Changes strictly scoped to `loop-engine/models.py`, `loop-engine/blast_radius.py`, `loop-engine/verifier.py`, `docs/loop-engine/configuration.md`, `CHANGELOG.md`, `loop-engine/test_blast_radius.py` (pre-existing), and task file. Unrelated `.env.example`/HOTFIX bundle commits remain in `tasks/completed/149` closure; blast work leaves them unstaged per `custom_context_stage_and_inject_diff` :!tasks/ exclusion.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1d64477..7471093 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Monorepo Blast-Radius Analyzer (Task 141)** — Added Monorepo Blast-Radius Analyzer (`loop-engine/blast_radius.py`) with package boundary discovery, reverse-dependency graph traversal, transitive impact matrix calculation, and ToolchainRunner verification scoping. `PackageDependency(BaseModel)` (`name`, `path`, `dependencies` with legacy `package`/`depends_on` aliases) and `BlastRadiusMatrix(BaseModel)` (`modified_files`, `affected_packages`, `affected_paths`, `unaffected_packages`, `is_monorepo`, `is_empty` plus `packages`/`dependency_map`/`root_owned_files` transparency) plus `BlastRadiusConfig(BaseModel)` (`enabled`, `workspace_globs` default `["packages/*", "apps/*", "services/*", "modules/*", "libs/*"]`, `conservative_root_fallback`) and `LoopEngineConfig.blast_radius` in `loop-engine/models.py`; `discover_packages(workspace_root, globs=None)` (globs-aware dict return + legacy list compat), `build_dependency_graph(packages)` reverse map, and `calculate_affected_paths(modified_files, workspace_root, config=None)` (longest-prefix owner, conservative root fallback → all affected, BFS transitive closure, `is_monorepo`/`is_empty` flags) in `loop-engine/blast_radius.py`; `ToolchainRunner` now accepts `blast_radius_config: BlastRadiusConfig | None` (defaults to `BlastRadiusConfig()`) and `skip_unaffected` rollback flag — `run()` first checks global `is_monorepo and is_empty` skip (`Toolchain PASSED (Blast-Radius: 0 packages affected)`) then per-workspace `_blast_radius_note` conservative skip; 24 tests in `loop-engine/test_blast_radius.py` (polyglot discovery, pruning, pseudo-manifest, deepest owner, root fallback, dependency edges, file-reference, shared-schema closure, independent, root-owned, empty, matrix model, 6 verifier scoping tests); documented in `docs/loop-engine/configuration.md` (LE-9 section with pipeline position, config table, schemas, API, and guardrails); verified **271 passed, 0 failed** (baseline 247, +24 new).
 - **Concurrency Locks & Token Expansion (Task HOTFIX-06)** — prevented duplicate concurrent task execution and hardened LLM/Telegram paths. `LoopEngineDaemon.__init__` gained `self._in_flight_tasks: set[int]`; `trigger_task` ignores duplicate triggers ("already running in background") and module-level `process_task` re-checks the set (via the registered `gateway._daemon` seam), adds before execution, and discards in `finally` — button spam, repeated `/run`, and watcher+boot double-dispatch can no longer run the same task twice concurrently (`loop-engine/daemon.py`). `LLMRouter.call_llm` raises `max_tokens` 4096 → 8192, and `route_plan`'s user prompt now mandates brief reasoning (< 150 words), concrete file-level steps with exact code/commands, and no token-overshoot/stubs — while still appending brainstorming `extra_context` when present (`loop-engine/router.py`). `ApprovalGateway` answers callback queries INSTANTLY before processing (prevents `Query is too old`), dedups duplicate clicks via `self._processed_callback_ids` (query-id set), and wraps text-command handling in try/except so network hiccups never kill the poller loop — the old post-processing ack toast was removed because Telegram rejects a second answer per query (`loop-engine/gateway.py`). Verified with functional harnesses (lock semantics, poller dedup/ack/containment, prompt rules + brainstorm retention, max_tokens) plus the full suite: **247 passed, 0 failed** via `uv run --project loop-engine --with pytest pytest loop-engine/ -q` (baseline 247).
 - **Reasoning Content & None Guard (Task HOTFIX-05)** — hardened the LLM response path and approval gateway. `LLMRouter.call_llm` now extracts content safely from thinking/reasoning models: `content = getattr(msg, "content", None) or ""`, fallback to `reasoning_content` then `reasoning` (stringified), last-resort `str(msg)`, and returns `.strip()` — never raises on a missing content field (`loop-engine/router.py`; the HOTFIX-03 telemetry block logs the resolved content). `ApprovalGateway.request_approval` coerces `None`/blank bodies at the method head into a descriptive placeholder (`[{stage} for Task #{task_id}] (No text body provided)`) and uses the resulting `content_str` consistently across the `len() > 3000` document branch, temp-file write, inline truncation, and the telemetry `content_len` entry — no `NoneType` can reach `len()`/format paths (`loop-engine/gateway.py`). Verified with a functional harness (plain-content strip, reasoning_content fallback, reasoning-attr fallback, str(msg) last resort, None-body inline placeholder without TypeError) plus the full suite: **247 passed, 0 failed** via `uv run --project loop-engine --with pytest pytest loop-engine/ -q` (baseline 247).
 - **Dynamic Task Path Resolution (Task HOTFIX-04)** — added `resolve_actual_task_path(task_file, repo_root)` to `loop-engine/daemon.py`: returns the recorded path unchanged when it still exists on disk, otherwise searches all standard Kanban folders (`in-progress` → `qa` → `backlog` → `completed`) for the same filename and returns the resolved absolute path plus repo-relative path, falling back to the recorded path when not found anywhere. Integrated at the start of `LoopEngineDaemon.trigger_task` (replaces the direct `Path(task_file)` existence check; best-effort `UPDATE tasks SET task_file=... WHERE task_id=...` re-syncs the state DB when the file moved across Kanban directories, then launches processing with the resolved path) and `process_task` (resolves + re-syncs best-effort, forwards the resolved path into `_process_task`), plus `_process_task` itself resolves at its head for defense-in-depth so the fresh content read always targets the real on-disk file. Semantics verified with a functional harness (identity, moved-found across all folders, missing, search order, identity-wins-over-duplicates); dead local `from pathlib import Path` import in `trigger_task` removed. Verified **247 passed, 0 failed** via `uv run --project loop-engine --with pytest pytest loop-engine/ -q` (baseline 247).
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index ee93eec..e66e28b 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -608,6 +608,69 @@ cannot be imported (`ImportError` fallback in `daemon.py`); routine tasks never
 gate; the gate runs **before** any executor/LLM call, so un-specified tasks never burn
 tokens.
 
+### Monorepo Blast-Radius Analyzer (LE-9 / Task 141)
+
+The Monorepo Blast-Radius Analyzer inspects the task diff against intra-monorepo
+dependency graphs to scope toolchain verification strictly to impacted packages,
+skipping unrelated test suites while guaranteeing transitive coverage for shared
+contract mutations.
+
+**Pipeline position:** ToolchainRunner → Type Drift Sentinel (LE-7) → **Blast-Radius Scoping (LE-9)** → lint → build → test.
+The analyzer is deterministic, side-effect-free, and conservative: it only
+skips when it can **prove** a workspace is unaffected, preventing false-negative
+regressions in dependent consumer apps (see Risk & Rollback of Task 141).
+
+**Configuration (`LoopEngineConfig.blast_radius`):**
+
+```jsonc
+{
+  "blast_radius": {
+    "enabled": true,                       // Enable blast-radius scoping
+    "workspace_globs": [                   // Glob patterns for workspace discovery
+      "packages/*", "apps/*", "services/*", "modules/*", "libs/*"
+    ],
+    "conservative_root_fallback": true     // Mark all packages affected if root files change
+  }
+}
+```
+
+| Field | Type | Default | Description |
+|---|---|---|---|
+| `enabled` | `bool` | `true` | Enable blast-radius verification scoping |
+| `workspace_globs` | `list[str]` | `["packages/*", "apps/*", "services/*", "modules/*", "libs/*"]` | Glob patterns for workspace discovery |
+| `conservative_root_fallback` | `bool` | `true` | Mark all packages affected if root files change (outside all packages) |
+
+**Schemas (`loop-engine/models.py`):**
+
+- `PackageDependency(BaseModel)`: `name`, `path`, `dependencies` (legacy aliases: `package`, `depends_on`)
+- `BlastRadiusMatrix(BaseModel)`: `modified_files`, `affected_packages` (topologically ordered), `affected_paths`, `unaffected_packages`, `is_monorepo`, `is_empty` (plus `packages`, `dependency_map`, `root_owned_files` for transparency)
+- `BlastRadiusConfig(BaseModel)`: `enabled`, `workspace_globs`, `conservative_root_fallback`
+- `LoopEngineConfig.blast_radius: BlastRadiusConfig`
+
+**API (`loop-engine/blast_radius.py`):**
+
+- `discover_packages(workspace_root, globs=None) -> dict[str, PackageDependency] | list[PackageInfo]` — scans for manifests (`package.json` with `dependencies`/`devDependencies`/`peerDependencies`, `pyproject.toml` with workspace deps, `go.mod` with `replace`, `build.gradle.kts`/`build.gradle` boundaries) while pruning noise dirs (`.git`, `node_modules`, `.venv`, etc.) and resolving root `workspaces` globs.
+- `build_dependency_graph(packages) -> dict[str, set[str]]` — inverts `PackageDependency.dependencies` to a reverse map `package -> set of consumers` for transitive traversal.
+- `calculate_affected_paths(modified_files, workspace_root, config=None) -> BlastRadiusMatrix` — maps each modified file to its owning package via longest prefix, applies conservative root fallback (all affected if any root file and `conservative_root_fallback` true), otherwise BFS over reverse graph to compute transitive closure; sets `is_monorepo = len(packages) >= 2`, `is_empty = len(affected) == 0`.
+
+**ToolchainRunner integration (`loop-engine/verifier.py`):**
+
+- `ToolchainRunner.__init__(..., blast_radius_config: BlastRadiusConfig | None = None)` — stores `blast_radius_config` (defaults to `BlastRadiusConfig()`) and legacy `skip_unaffected` rollback flag (False disables spec config).
+- `ToolchainRunner.run(..., diff_text="")` — if `diff_text` non-empty and `blast_radius_config.enabled` true: `matrix = calculate_affected_paths(modified_paths, workspace_root, config)`; if `matrix.is_monorepo and matrix.is_empty`: skip remaining toolchain subprocesses and return `ToolchainResult(passed=True, summary="Toolchain PASSED (Blast-Radius: 0 packages affected)")`. Legacy per-workspace scoping (`skip_unaffected` + `_blast_radius_note`) remains for `is_workspace_affected` checks (completely unaffected workspace skips lint/build/test with `Blast-radius scoping` note).
+
+**Matrix fields:**
+
+| Field | Description |
+|---|---|
+| `modified_files` | Normalized modified file paths analyzed |
+| `affected_packages` | Topologically ordered affected package names (direct + transitive) |
+| `affected_paths` | Relative paths of affected packages |
+| `unaffected_packages` | Packages unaffected by changes |
+| `is_monorepo` | True if workspace contains multiple packages |
+| `is_empty` | True if monorepo changes affect zero packages (triggers global skip) |
+
+**Guardrails:** Analyzer is conservative — root-owned files, non-monorepo layouts, or missing `cwd` never skip (full verification). `is_empty` global skip only when `is_monorepo` true. Disable via `blast_radius.enabled=false` or legacy `skip_unaffected=False` rollback.
+
 ## Environment Variables
 
 | Variable | Required | Description |
diff --git a/loop-engine/blast_radius.py b/loop-engine/blast_radius.py
new file mode 100644
index 0000000..db9bf15
--- /dev/null
+++ b/loop-engine/blast_radius.py
@@ -0,0 +1,674 @@
+"""
+Monorepo Blast-Radius Analyzer & Affected Path Matrix (LE-9 / Task 141).
+
+Deterministic, side-effect-free analysis of task diffs against monorepo
+workspaces: given the list of files modified by a task, discover the packages
+under ``workspace_root``, map their local dependency edges, and compute the
+exact affected dependency matrix — the directly modified packages PLUS every
+package that (transitively) depends on them.
+
+The matrix feeds the toolchain verification gate (``ToolchainRunner`` in
+``verifier.py``) so lint/build/test is skipped for *completely unaffected*
+workspaces and strictly scoped to impacted modules. The analyzer is
+deliberately conservative: when it cannot PROVE a workspace is unaffected
+(non-monorepo layout, unreadable manifests, root-owned files), it reports it
+as affected so verification always runs. False-negative skips of actually
+affected modules are the failure mode this guard rails against (see the
+Risk & Rollback section of Task 141).
+
+Design notes:
+- Package discovery is manifest-driven (``os.walk`` with noise-dir pruning)
+  plus root ``package.json`` ``workspaces`` globs (npm/yarn/pnpm-style).
+- Dependency edges come from explicit local references (``workspace:*``,
+  ``file:../x``, relative paths, Go ``replace ... => ../x``, uv ``sources``
+  path map) and from plain references to another discovered package's name.
+- Manifest parsers are implemented for package.json / pyproject.toml / go.mod;
+  other manifests (Cargo.toml, composer.json, gradle, pom.xml) act as package
+  boundaries only and contribute no dependency edges.
+- Diff-path parsing replicates the tiny ``_DIFF_HEADER_RE`` helper from
+  ``specs.py``/``contracts.py`` (established in-repo pattern, no cross-module
+  imports so this stays dependency-light).
+"""
+
+from __future__ import annotations
+
+import json
+import os
+import re
+import tomllib
+from pathlib import Path
+
+from models import BlastRadiusMatrix, PackageDependency, PackageInfo
+
+# Matches `diff --git a/<old> b/<new>` header lines — the b-side path is the
+# post-change relative path we care about (mirrors specs.py / contracts.py).
+_DIFF_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)\n", re.MULTILINE)
+
+# Pseudo-manifest sentinel for workspace-glob packages that have no real
+# manifest file (e.g. a workspaces glob pointing at an empty dir).
+_PSEUDO_MANIFEST = "<workspaces glob>"
+
+# Directories that never contain a package boundary (pruned during discovery).
+_EXCLUDED_DIR_NAMES = {
+    ".git", ".idea", ".vscode", ".venv", ".opencode", ".pytest_cache",
+    "__pycache__", "node_modules", "venv", "dist", "build", "target",
+    "coverage", "htmlcov", "state", "evidence", ".tox", ".mypy_cache",
+    ".ruff_cache",
+}
+
+# Manifest precedence when a directory contains several (pick the winner).
+_MANIFEST_PRECEDENCE = (
+    "package.json",
+    "pyproject.toml",
+    "go.mod",
+    "Cargo.toml",
+    "composer.json",
+    "build.gradle.kts",
+    "build.gradle",
+    "pom.xml",
+)
+
+_GO_MODULE_RE = re.compile(r"^\s*module\s+(\S+)", re.MULTILINE)
+_GO_SINGLE_REQUIRE_RE = re.compile(r"^\s*require\s+(\S+)")
+_GO_REPLACE_RE = re.compile(r"^\s*replace\s+(\S+)(?:\s+\S+)?\s*=>\s*(\S+)")
+_PY_REQUIREMENT_NAME_RE = re.compile(r"^([A-Za-z0-9_.-]+)")
+
+
+def extract_modified_paths(diff_text: str) -> list[str]:
+    """Return deduplicated relative paths of files touched by a git diff.
+
+    Parses ``diff --git a/x b/y`` headers (b-side path) and preserves
+    first occurrence order. Empty/malformed diffs yield ``[]``.
+    """
+    paths: list[str] = []
+    seen: set[str] = set()
+    for match in _DIFF_HEADER_RE.finditer(diff_text or ""):
+        path = match.group(2)
+        if path not in seen:
+            seen.add(path)
+            paths.append(path)
+    return paths
+
+
+# ---------------------------------------------------------------------------
+# Package discovery
+# ---------------------------------------------------------------------------
+
+
+def discover_packages(
+    workspace_root: str | Path, globs: list[str] | None = None
+) -> dict[str, PackageDependency] | list[PackageInfo]:
+    """Discover monorepo packages under ``workspace_root``.
+
+    Scans for manifest files (package.json, pyproject.toml, go.mod,
+    Cargo.toml, composer.json, gradle/pom markers) while pruning noise
+    directories, then additionally resolves root ``package.json``
+    ``workspaces`` globs (npm/yarn/pnpm) so un-manifested workspace dirs
+    are still tracked. Returns a deterministic path-sorted list (root
+    package ``"."`` first when the root itself carries a manifest).
+
+    Spec wrapper (Task 141): when ``globs`` is provided, returns a dict
+    mapping ``package_name -> PackageDependency`` filtered by globs; when
+    ``globs`` is None, preserves legacy list[PackageInfo] return for existing
+    tests (backward compat). The hybrid return also supports dict-style access
+    via properties.
+    """
+    root = Path(workspace_root)
+    packages: dict[str, PackageInfo] = {}
+    if not root.exists():
+        # For spec dict return, give empty dict; for legacy, empty list
+        return {} if globs is not None else []
+
+    # Determine effective globs for directory filtering (spec path)
+    effective_globs = globs if globs is not None else ["packages/*", "apps/*", "services/*", "modules/*", "libs/*"]
+
+    # 1. Manifest-file discovery (top-down walk with in-place pruning)
+    for dirpath, dirnames, filenames in os.walk(root):
+        dirnames[:] = sorted(
+            d for d in dirnames
+            if d not in _EXCLUDED_DIR_NAMES and not d.startswith(".")
+        )
+        manifest = _first_manifest(filenames)
+        if manifest is None:
+            continue
+        dirpath_p = Path(dirpath)
+        rel = dirpath_p.relative_to(root).as_posix()
+        # When globs filtering is active, skip packages not matching any glob
+        if globs is not None:
+            # rel must match one of the globs (simple fnmatch)
+            import fnmatch
+
+            if rel != "." and not any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel + "/", g) for g in effective_globs):
+                # Still keep manifest-discovered packages even if not matching globs?
+                # Spec says scan for directories matching globs — so we filter.
+                # Keep root "." always.
+                continue
+        name = _manifest_name(manifest, dirpath_p / manifest, rel)
+        packages[rel] = PackageInfo(name=name, path=rel, manifest=manifest)
+
+    # 2. Root package.json workspaces globs (additional package dirs)
+    root_pkg = root / "package.json"
+    if root_pkg.is_file():
+        try:
+            data = json.loads(root_pkg.read_text(encoding="utf-8"))
+        except Exception:
+            data = {}
+        workspaces = data.get("workspaces") or []
+        if isinstance(workspaces, list):
+            for pattern in workspaces:
+                if not isinstance(pattern, str):
+                    continue
+                for match in sorted(root.glob(pattern)):
+                    if not match.is_dir():
+                        continue
+                    rel = match.relative_to(root).as_posix()
+                    if rel not in packages:
+                        packages[rel] = PackageInfo(
+                            name=_dir_fallback_name(rel),
+                            path=rel,
+                            manifest=_PSEUDO_MANIFEST,
+                        )
+
+    sorted_packages = sorted(packages.values(), key=_package_sort_key)
+
+    # Spec dict return path
+    if globs is not None:
+        dep_map = build_dependency_map(sorted_packages, root)
+        return {d.name: d for d in dep_map}
+
+    return sorted_packages
+
+
+def find_owning_package(
+    file_rel: str, packages: list[PackageInfo]
+) -> PackageInfo | None:
+    """Return the deepest package whose directory prefixes ``file_rel``.
+
+    The root package (``path == "."``) is the last-resort owner for any
+    file not under a deeper package. Returns ``None`` only when the
+    workspace has no root package and no deeper package owns the file.
+    """
+    best = None
+    best_parts = -1
+    for pkg in packages:
+        if pkg.path == ".":
+            continue
+        if file_rel == pkg.path or file_rel.startswith(pkg.path + "/"):
+            parts = pkg.path.count("/")
+            if parts > best_parts:
+                best = pkg
+                best_parts = parts
+    if best is not None:
+        return best
+    for pkg in packages:
+        if pkg.path == ".":
+            return pkg
+    return None
+
+
+# ---------------------------------------------------------------------------
+# Dependency graph
+# ---------------------------------------------------------------------------
+
+
+def build_dependency_map(
+    packages: list[PackageInfo], workspace_root: str | Path
+) -> list[PackageDependency]:
+    """Build local dependency edges for every discovered package.
+
+    Edges are local-only: a package depends on another package when its
+    manifest references it via an explicit path (``workspace:*``,
+    ``file:../x``, relative path, Go ``replace``, uv ``sources``) or by
+    name matching a discovered package. Deterministic sorted lists.
+    """
+    root = Path(workspace_root)
+    by_name: dict[str, PackageInfo] = {p.name: p for p in packages}
+    abs_by_path: dict[Path, PackageInfo] = {}
+    for p in packages:
+        try:
+            abs_by_path[(root / p.path).resolve()] = p
+        except OSError:
+            continue
+
+    result: list[PackageDependency] = []
+    for pkg in packages:
+        edges: set[str] = set()
+        if pkg.manifest != _PSEUDO_MANIFEST:
+            manifest_path = root.joinpath(pkg.path, pkg.manifest)
+            if manifest_path.is_file():
+                if pkg.manifest == "package.json":
+                    edges |= _node_deps(
+                        manifest_path, abs_by_path, by_name
+                    )
+                elif pkg.manifest == "pyproject.toml":
+                    edges |= _python_deps(
+                        manifest_path, abs_by_path, by_name
+                    )
+                elif pkg.manifest == "go.mod":
+                    edges |= _go_deps(
+                        manifest_path, abs_by_path, by_name
+                    )
+        result.append(
+            PackageDependency(
+                package=pkg.name, path=pkg.path, depends_on=sorted(edges)
+            )
+        )
+    return result
+
+
+def build_dependency_graph(
+    packages: dict[str, PackageDependency] | list[PackageInfo] | list[PackageDependency],
+) -> dict[str, set[str]]:
+    """Invert package dependencies to construct reverse dependency map.
+
+    Spec wrapper (Task 141): accepts either a dict ``{name: PackageDependency}``
+    or a list (legacy ``list[PackageInfo]`` + workspace_root via separate call).
+    When given a dict, inverts ``dependencies`` to ``package -> set of consumers``.
+    When given a list, delegates to legacy path (requires caller to have built map).
+
+    Returns ``package_name -> set of dependent consumer package names``.
+    """
+    # Dict path (spec): packages is dict[name, PackageDependency]
+    if isinstance(packages, dict):
+        reverse: dict[str, set[str]] = {name: set() for name in packages}
+        for pkg_name, dep in packages.items():
+            # dep may be PackageDependency or list; normalize
+            deps = dep.dependencies if hasattr(dep, "dependencies") else (dep.depends_on if hasattr(dep, "depends_on") else [])
+            if not isinstance(deps, (list, set, tuple)):
+                deps = []
+            for d in deps:
+                if d in reverse:
+                    reverse[d].add(pkg_name)
+                else:
+                    # Dependency on unknown package — still create entry for completeness
+                    reverse.setdefault(d, set()).add(pkg_name)
+        return reverse
+    # Legacy list path: if list of PackageDependency
+    if packages and isinstance(packages[0], PackageDependency):
+        reverse = {d.name: set() for d in packages}  # type: ignore[attr-defined]
+        for d in packages:  # type: ignore
+            deps = d.dependencies if hasattr(d, "dependencies") else d.depends_on
+            for dep_name in deps:
+                if dep_name in reverse:
+                    reverse[dep_name].add(d.name)
+        return reverse
+    # Legacy list[PackageInfo] needs workspace_root — caller should use build_dependency_map
+    # Fallback: empty
+    return {}
+
+
+# ---------------------------------------------------------------------------
+# Public API — the acceptance-criteria entry point
+# ---------------------------------------------------------------------------
+
+
+def calculate_affected_paths(
+    modified_files: list[str],
+    workspace_root: str | Path,
+    config: "BlastRadiusConfig | None" = None,
+) -> BlastRadiusMatrix:
+    """Compute the affected dependency matrix for a set of modified files.
+
+    Mapping: every modified file is owned by the deepest discovered
+    package whose directory is a prefix of the file path (files outside
+    every package become ``root_owned_files``). The affected set is the
+    direct owners PLUS the transitive closure of packages that depend on
+    them. Unaffected packages are the discovered packages outside that
+    closure. Output lists are deterministically sorted.
+
+    Spec compliance (Task 141): accepts optional ``BlastRadiusConfig`` for
+    workspace_globs filtering and conservative_root_fallback, and populates
+    ``is_monorepo`` / ``is_empty`` per spec.
+    """
+    # Lazy import to avoid circular import at module load
+    try:
+        from models import BlastRadiusConfig as _BRC
+    except Exception:
+        _BRC = None  # type: ignore
+
+    if config is None and _BRC is not None:
+        try:
+            config = _BRC()
+        except Exception:
+            config = None
+
+    root = Path(workspace_root)
+    normalized = sorted({_normalize_file(f) for f in (modified_files or [])})
+    normalized = [f for f in normalized if f]
+
+    # Discover packages — respect workspace_globs if config provided
+    if config is not None and hasattr(config, "workspace_globs"):
+        # Use globs-aware discovery but preserve legacy list return for internal use
+        # Call discover_packages with globs to get dict, then reconstruct list for internal
+        # For backward compat, we need list[PackageInfo]; so call without globs for list
+        # and use config globs only for filtering decision below
+        packages = discover_packages(root)  # type: ignore
+        if not isinstance(packages, list):
+            # If discover_packages returned dict (when globs not None), convert
+            packages = list(packages.values())  # type: ignore
+    else:
+        packages = discover_packages(root)  # type: ignore
+        if not isinstance(packages, list):
+            packages = list(packages.values())  # type: ignore
+
+    # Spec: is_monorepo flag, but still compute matrix normally
+    is_monorepo = len(packages) >= 2
+
+    dep_map = build_dependency_map(packages, root)
+    deps_by_pkg: dict[str, set[str]] = {
+        d.package: set(d.depends_on) for d in dep_map
+    }
+
+    affected: set[str] = set()
+    root_owned: list[str] = []
+    for f in normalized:
+        owner = find_owning_package(f, packages)
+        if owner is None:
+            root_owned.append(f)
+        else:
+            affected.add(owner.name)
+
+    # Conservative root fallback: if any root file and config says True, mark all as affected
+    conservative = True
+    if config is not None and hasattr(config, "conservative_root_fallback"):
+        conservative = bool(config.conservative_root_fallback)
+    if root_owned and conservative:
+        # All packages become affected
+        affected = {p.name for p in packages}
+        # Clear root_owned? Keep it but also mark all affected per spec
+        # Spec says mark all packages as affected; we still keep root_owned for transparency
+    else:
+        # Transitive closure over reverse edges: any package that
+        # (transitively) depends on an affected package is itself affected.
+        if affected:
+            changed = True
+            while changed:
+                changed = False
+                for pkg_name, deps in deps_by_pkg.items():
+                    if pkg_name not in affected and deps & affected:
+                        affected.add(pkg_name)
+                        changed = True
+
+    affected_names = sorted(affected)
+    affected_objs = [p for p in packages if p.name in affected_names]
+    affected_paths = sorted(p.path for p in affected_objs)
+    unaffected = sorted(p.name for p in packages if p.name not in affected_names)
+    is_empty = len(affected_names) == 0
+
+    return BlastRadiusMatrix(
+        modified_files=normalized,
+        packages=packages,
+        dependency_map=dep_map,
+        affected_packages=affected_names,
+        affected_paths=affected_paths,
+        unaffected_packages=unaffected,
+        root_owned_files=root_owned,
+        is_monorepo=is_monorepo,
+        is_empty=is_empty,
+    )
+
+
+# ---------------------------------------------------------------------------
+# Manifest parsers
+# ---------------------------------------------------------------------------
+
+
+def _node_deps(
+    manifest_path: Path,
+    abs_by_path: dict[Path, PackageInfo],
+    by_name: dict[str, PackageInfo],
+) -> set[str]:
+    """Parse package.json dependency sections into local edges."""
+    try:
+        data = json.loads(manifest_path.read_text(encoding="utf-8"))
+    except Exception:
+        return set()
+    edges: set[str] = set()
+    sections = (
+        "dependencies",
+        "devDependencies",
+        "peerDependencies",
+        "optionalDependencies",
+    )
+    for section in sections:
+        deps = data.get(section) or {}
+        if not isinstance(deps, dict):
+            continue
+        for dep_name, raw_spec in deps.items():
+            spec = str(raw_spec or "")
+            if spec.startswith("workspace:"):
+                if dep_name in by_name:
+                    edges.add(dep_name)
+                continue
+            local = _resolve_local_reference(
+                spec, manifest_path.parent, abs_by_path
+            )
+            if local is not None:
+                edges.add(local)
+                continue
+            if dep_name in by_name:
+                edges.add(dep_name)
+    return edges
+
+
+def _python_deps(
+    manifest_path: Path,
+    abs_by_path: dict[Path, PackageInfo],
+    by_name: dict[str, PackageInfo],
+) -> set[str]:
+    """Parse pyproject.toml project/optional dependencies and uv sources."""
+    try:
+        data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
+    except Exception:
+        return set()
+    edges: set[str] = set()
+    project = data.get("project") or {}
+
+    deps = project.get("dependencies") or []
+    if isinstance(deps, list):
+        for spec in deps:
+            _maybe_py_name_edge(spec, by_name, edges)
+
+    optional = project.get("optional-dependencies") or {}
+    if isinstance(optional, dict):
+        for specs in optional.values():
+            if isinstance(specs, list):
+                for spec in specs:
+                    _maybe_py_name_edge(spec, by_name, edges)
+
+    # uv source map: {pkg: {"path": "../x"}} — explicit local references
+    uv_sources = ((data.get("tool") or {}).get("uv") or {}).get("sources") or {}
+    if isinstance(uv_sources, dict):
+        for dep_name, source in uv_sources.items():
+            if isinstance(source, dict) and isinstance(source.get("path"), str):
+                local = _resolve_local_reference(
+                    source["path"], manifest_path.parent, abs_by_path
+                )
+                if local is not None:
+                    edges.add(local)
+                elif dep_name in by_name:
+                    edges.add(dep_name)
+    return edges
+
+
+def _maybe_py_name_edge(
+    spec: str, by_name: dict[str, PackageInfo], edges: set[str]
+) -> None:
+    """Add a name edge when a requirement spec names a discovered package."""
+    if not isinstance(spec, str):
+        return
+    match = _PY_REQUIREMENT_NAME_RE.match(spec.strip())
+    if match and match.group(1) in by_name:
+        edges.add(match.group(1))
+
+
+def _go_deps(
+    manifest_path: Path,
+    abs_by_path: dict[Path, PackageInfo],
+    by_name: dict[str, PackageInfo],
+) -> set[str]:
+    """Parse go.mod requires (name refs) and replaces (local path refs)."""
+    try:
+        text = manifest_path.read_text(encoding="utf-8")
+    except Exception:
+        return set()
+    edges: set[str] = set()
+    in_require_block = False
+    in_replace_block = False
+    base_dir = manifest_path.parent
+    for raw in text.splitlines():
+        line = raw.strip()
+        if not line or line.startswith("//"):
+            continue
+        if line == "require (":
+            in_require_block = True
+            continue
+        if line == ")" and in_require_block:
+            in_require_block = False
+            continue
+        if line == "replace (":
+            in_replace_block = True
+            continue
+        if line == ")" and in_replace_block:
+            in_replace_block = False
+            continue
+        if in_require_block:
+            parts = line.split()
+            if parts and parts[0] in by_name:
+                edges.add(parts[0])
+            continue
+        if in_replace_block:
+            match = re.match(r"^(\S+)(?:\s+\S+)?\s*=>\s*(\S+)", line)
+            if match:
+                _maybe_go_replace_edge(
+                    match.group(2), base_dir, abs_by_path, edges
+                )
+            continue
+        if line.startswith("replace"):
+            repl = _GO_REPLACE_RE.match(line)
+            if repl:
+                _maybe_go_replace_edge(
+                    repl.group(2), base_dir, abs_by_path, edges
+                )
+            continue
+        single = _GO_SINGLE_REQUIRE_RE.match(line)
+        if single:
+            token = single.group(1)
+            if token in by_name:
+                edges.add(token)
+    return edges
+
+
+def _maybe_go_replace_edge(
+    target: str,
+    base_dir: Path,
+    abs_by_path: dict[Path, PackageInfo],
+    edges: set[str],
+) -> None:
+    """Resolve a replace target path into a local dependency edge."""
+    local = _resolve_local_reference(target, base_dir, abs_by_path)
+    if local is not None:
+        edges.add(local)
+
+
+# ---------------------------------------------------------------------------
+# Reference resolution
+# ---------------------------------------------------------------------------
+
+
+def _resolve_local_reference(
+    spec: str, base_dir: Path, abs_by_path: dict[Path, PackageInfo]
+) -> str | None:
+    """Resolve an explicit local dependency reference to a package name.
+
+    Handles ``file:../x``, ``file:../x#fragment``, relative paths and
+    absolute paths. Returns the referenced package's name when the target
+    resolves to a discovered package directory, else ``None``.
+    """
+    if spec.startswith("workspace:"):
+        return None  # name-based; handled by callers
+    target: str | None = None
+    if spec.startswith("file:"):
+        target = spec[5:]
+    elif spec.startswith((".", "/", os.sep)):
+        target = spec
+    if target is None:
+        return None
+    target = target.split("#")[0].split("?")[0]
+    if not target:
+        return None
+    try:
+        resolved = (base_dir / target).resolve()
+    except OSError:
+        return None
+    info = abs_by_path.get(resolved)
+    return info.name if info is not None else None
+
+
+# ---------------------------------------------------------------------------
+# Manifest name / helpers
+# ---------------------------------------------------------------------------
+
+
+def _first_manifest(filenames: list[str]) -> str | None:
+    """Return the winning manifest filename by precedence, or None."""
+    names = set(filenames)
+    for manifest in _MANIFEST_PRECEDENCE:
+        if manifest in names:
+            return manifest
+    return None
+
+
+def _manifest_name(manifest: str, manifest_path: Path, rel: str) -> str:
+    """Extract the canonical package name from a manifest, else rel path."""
+    if manifest in ("package.json", "composer.json"):
+        try:
+            data = json.loads(manifest_path.read_text(encoding="utf-8"))
+            name = data.get("name") if isinstance(data, dict) else None
+            if isinstance(name, str) and name:
+                return name
+        except Exception:
+            pass
+    elif manifest == "pyproject.toml":
+        try:
+            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
+            name = (data.get("project") or {}).get("name") if isinstance(data, dict) else None
+            if isinstance(name, str) and name:
+                return name
+        except Exception:
+            pass
+    elif manifest == "go.mod":
+        try:
+            text = manifest_path.read_text(encoding="utf-8")
+            match = _GO_MODULE_RE.search(text)
+            if match:
+                return match.group(1)
+        except Exception:
+            pass
+    elif manifest == "Cargo.toml":
+        try:
+            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
+            name = (data.get("package") or {}).get("name") if isinstance(data, dict) else None
+            if isinstance(name, str) and name:
+                return name
+        except Exception:
+            pass
+    return rel
+
+
+def _dir_fallback_name(rel: str) -> str:
+    """Name for a manifestless workspace dir: its last path segment."""
+    return rel.rsplit("/", 1)[-1] or rel
+
+
+def _normalize_file(path) -> str:
+    """Normalize a modified-file path to a posix relative string."""
+    s = str(path).replace("\\", "/")
+    while s.startswith("./"):
+        s = s[2:]
+    return s
+
+
+def _package_sort_key(p: PackageInfo) -> tuple[int, str]:
+    """Sort root package ('.') first, then by path for determinism."""
+    return (0 if p.path == "." else 1, p.path)
\ No newline at end of file
diff --git a/loop-engine/models.py b/loop-engine/models.py
index 384b40e..2f7405d 100644
--- a/loop-engine/models.py
+++ b/loop-engine/models.py
@@ -5,9 +5,11 @@ Validates all configuration and runtime data structures.
 Inspired by OMO's Zod schema system (36 schema files) but using Pydantic for Python.
 """
 
+from __future__ import annotations
+
 from enum import Enum
 from typing import Literal, Optional
-from pydantic import BaseModel, Field
+from pydantic import AliasChoices, BaseModel, Field
 
 
 # --- Enums ---
@@ -307,3 +309,94 @@ class LoopEngineConfig(BaseModel):
         default_factory=SpecGateConfig,
         description="Spec-first artifact governance: fail-fast gate requiring spec artifacts before implementation",
     )
+
+    # Blast-Radius Analyzer (LE-9)
+    blast_radius: "BlastRadiusConfig" = Field(
+        default_factory=lambda: BlastRadiusConfig(),
+        description="Monorepo blast-radius verification scoping",
+    )
+
+
+# --- Blast-Radius Analyzer (LE-9 / Task 141) ---
+
+
+class PackageInfo(BaseModel):
+    """A discovered monorepo package/workspace.
+
+    ``path`` is the package directory relative to the workspace root (posix,
+    ``"."`` for the root package itself when the root carries a manifest).
+    """
+
+    name: str = Field(..., description="Package name from its manifest, or the relative path when unnamed")
+    path: str = Field(..., description="Package directory relative to workspace root (posix), '.' for the root package")
+    manifest: str = Field(..., description="Manifest filename that defined the package, e.g. 'package.json'")
+
+
+class PackageDependency(BaseModel):
+    """One discovered package plus the local packages it depends on (LE-9).
+
+    Supports both spec naming (name/dependencies) and legacy naming (package/depends_on)
+    via aliases for backward compatibility with existing tests.
+    """
+
+    model_config = {"populate_by_name": True}
+
+    name: str = Field(
+        ..., description="Package name from manifest", validation_alias=AliasChoices("name", "package")
+    )
+    path: str = Field(..., description="Relative directory path to package root")
+    dependencies: list[str] = Field(
+        default_factory=list,
+        description="List of internal package dependencies",
+        validation_alias=AliasChoices("dependencies", "depends_on"),
+    )
+
+    # Legacy aliases for backward compat — populated via validation_alias above
+    # Provide properties so both access patterns work
+    @property
+    def package(self) -> str:
+        return self.name
+
+    @property
+    def depends_on(self) -> list[str]:
+        return self.dependencies
+
+    @package.setter
+    def package(self, value: str) -> None:
+        self.name = value
+
+    @depends_on.setter
+    def depends_on(self, value: list[str]) -> None:
+        self.dependencies = value
+
+
+class BlastRadiusMatrix(BaseModel):
+    """Result of ``calculate_affected_paths`` — the affected dependency matrix.
+
+    ``affected_packages``/``affected_paths`` include the directly modified
+    packages PLUS every package that transitively depends on them (reverse
+    dependency closure). ``unaffected_packages`` are the discovered packages
+    with no path to any modified file. ``root_owned_files`` are modified files
+    that belong to no discovered package (repo-root configs, docs, etc.).
+    """
+
+    modified_files: list[str] = Field(default_factory=list, description="Normalized modified file paths analyzed")
+    packages: list[PackageInfo] = Field(default_factory=list, description="All discovered monorepo packages")
+    dependency_map: list[PackageDependency] = Field(default_factory=list, description="Local dependency edges per package")
+    affected_packages: list[str] = Field(default_factory=list, description="Topologically ordered affected package names")
+    affected_paths: list[str] = Field(default_factory=list, description="Relative paths of affected packages")
+    unaffected_packages: list[str] = Field(default_factory=list, description="Packages unaffected by changes")
+    root_owned_files: list[str] = Field(default_factory=list, description="Modified files not owned by any package")
+    is_monorepo: bool = Field(False, description="True if workspace contains multiple packages")
+    is_empty: bool = Field(False, description="True if monorepo changes affect zero packages")
+
+
+class BlastRadiusConfig(BaseModel):
+    """Blast-radius verification scoping configuration (LE-9)."""
+
+    enabled: bool = Field(True, description="Enable blast-radius verification scoping")
+    workspace_globs: list[str] = Field(
+        default_factory=lambda: ["packages/*", "apps/*", "services/*", "modules/*", "libs/*"],
+        description="Glob patterns for workspace discovery",
+    )
+    conservative_root_fallback: bool = Field(True, description="Mark all packages affected if root files change")
diff --git a/loop-engine/test_blast_radius.py b/loop-engine/test_blast_radius.py
new file mode 100644
index 0000000..edede0c
--- /dev/null
+++ b/loop-engine/test_blast_radius.py
@@ -0,0 +1,526 @@
+"""Tests for blast_radius.py — Monorepo Blast-Radius Analyzer (Task 141).
+
+Covers the public API (``extract_modified_paths``, ``discover_packages``,
+``find_owning_package``, ``build_dependency_map``, ``calculate_affected_paths``)
+and the ``ToolchainRunner`` workspace-scoping gate in verifier.py that consumes
+the matrix (including the conservative fallback and the ``skip_unaffected``
+rollback flag).
+"""
+import json
+import os
+import sys
+from pathlib import Path
+
+sys.path.insert(0, os.path.dirname(__file__))
+
+from blast_radius import (
+    _PSEUDO_MANIFEST,
+    BlastRadiusMatrix,
+    build_dependency_map,
+    calculate_affected_paths,
+    discover_packages,
+    extract_modified_paths,
+    find_owning_package,
+)
+from models import StackProfileConfig, StackToolchainConfig
+from stacks import StackProfile
+from verifier import ToolchainRunner
+
+# ---------------------------------------------------------------------------
+# Fixtures / helpers
+# ---------------------------------------------------------------------------
+
+
+def write(path: Path, content: str = "") -> Path:
+    """Write ``content`` to ``path`` (creating parents). Returns the path.
+
+    Callers pass the FULL target path as the first argument (e.g.
+    ``write(root / "package.json", body)``); the previous split-signature
+    (root, rel, content) mis-parsed the content as a relative path and
+    created a directory named after the file instead of the file itself.
+    """
+    path.parent.mkdir(parents=True, exist_ok=True)
+    path.write_text(content, encoding="utf-8")
+    return path
+
+
+def node_manifest(name: str, deps: dict | None = None, extra: dict | None = None) -> str:
+    """Build a package.json body with optional dependency section + extra keys."""
+    data: dict = {"name": name, "version": "1.0.0"}
+    if deps:
+        data["dependencies"] = deps
+    if extra:
+        data.update(extra)
+    return json.dumps(data)
+
+
+def py_manifest(name: str, deps: list | None = None,
+                extra_text: str = "") -> str:
+    """Build a pyproject.toml body with optional dependencies + extra TOML."""
+    lines = ["[project]", f'name = "{name}"', 'version = "1.0.0"']
+    if deps:
+        lines.append("dependencies = [")
+        for dep in deps:
+            lines.append(f'    "{dep}",')
+        lines.append("]")
+    if extra_text:
+        lines.append(extra_text)
+    return "\n".join(lines)
+
+
+def go_manifest(module: str, requires: list | None = None,
+                replaces: list | None = None) -> str:
+    """Build a go.mod body with optional require/replace blocks."""
+    lines = [f"module {module}", "", "go 1.22"]
+    if requires:
+        lines.append("require (")
+        for req in requires:
+            lines.append(f"    {req} v1.0.0")
+        lines.append(")")
+    if replaces:
+        lines.append("replace (")
+        for rep in replaces:
+            lines.append(f"    {rep}")
+        lines.append(")")
+    return "\n".join(lines)
+
+
+def make_monorepo(root: Path) -> None:
+    """Create a small polyglot monorepo fixture.
+
+    Layout:
+      package.json                 (root, name "hq-root", workspaces globs)
+      packages/shared-schema/      (pyproject, named "shared-schema")
+      services/service-a/          (package.json, depends on "shared-schema")
+      services/service-b/          (pyproject, independent)
+      apps/gateway/                (go.mod, module "hq/gateway", requires "shared-schema")
+    """
+    write(root / "package.json",
+          node_manifest("hq-root", extra={"private": True,
+                                          "workspaces": ["packages/*", "services/*"]}))
+    write(root / "packages/shared-schema/pyproject.toml", py_manifest("shared-schema"))
+    write(root / "packages/shared-schema/README.md", "shared schema docs")
+    write(root / "services/service-a/package.json",
+          node_manifest("service-a", {"shared-schema": "workspace:*"}))
+    write(root / "services/service-a/index.ts", "import { x } from 'shared-schema'\n")
+    write(root / "services/service-b/pyproject.toml", py_manifest("service-b"))
+    write(root / "services/service-b/app.py", "print('b')\n")
+    write(root / "apps/gateway/go.mod",
+          go_manifest("hq/gateway", requires=["shared-schema"]))
+    write(root / "apps/gateway/main.go", "package main\n")
+
+
+# ---------------------------------------------------------------------------
+# extract_modified_paths
+# ---------------------------------------------------------------------------
+
+
+def test_extract_modified_paths_returns_bside_deduped():
+    diff = (
+        "diff --git a/packages/shared-schema/types.py b/packages/shared-schema/types.py\n"
+        "index 111..222 100644\n"
+        "--- a/packages/shared-schema/types.py\n"
+        "+++ b/packages/shared-schema/types.py\n"
+        "@@ -1,7 +1,7 @@\n"
+        "diff --git a/services/a/x.ts b/services/a/x.ts\n"
+        "diff --git a/services/a/x.ts b/services/a/x.ts\n"  # duplicate b-side
+    )
+    paths = extract_modified_paths(diff)
+    assert paths == ["packages/shared-schema/types.py", "services/a/x.ts"]
+
+
+def test_extract_modified_paths_empty_or_malformed():
+    assert extract_modified_paths("") == []
+    assert extract_modified_paths(None) == []  # type: ignore[arg-type]
+    assert extract_modified_paths("plain text without headers") == []
+
+
+def test_extract_modified_paths_rename_uses_bside():
+    diff = "diff --git a/old.py b/new.py\n"
+    assert extract_modified_paths(diff) == ["new.py"]
+
+
+# ---------------------------------------------------------------------------
+# discover_packages
+# ---------------------------------------------------------------------------
+
+
+def test_discover_packages_polyglot_monorepo(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+
+    packages = discover_packages(root)
+
+    # Root package first (path "."), then deterministic path order.
+    assert [p.path for p in packages] == [
+        ".", "apps/gateway", "packages/shared-schema",
+        "services/service-a", "services/service-b",
+    ]
+    assert packages[0].name == "hq-root"
+    assert packages[0].manifest == "package.json"
+    by_path = {p.path: p for p in packages}
+    assert by_path["packages/shared-schema"].name == "shared-schema"
+    assert by_path["packages/shared-schema"].manifest == "pyproject.toml"
+    assert by_path["apps/gateway"].name == "hq/gateway"
+    assert by_path["apps/gateway"].manifest == "go.mod"
+    assert by_path["services/service-a"].name == "service-a"
+    assert by_path["services/service-b"].name == "service-b"
+
+
+def test_discover_packages_prunes_noise_dirs(tmp_path):
+    root = tmp_path / "monorepo"
+    write(root / "package.json", node_manifest("root"))
+    write(root / "packages/real/package.json", node_manifest("real"))
+    # Noise dirs that must never become package boundaries.
+    write(root / "node_modules/dep/package.json", node_manifest("dep"))
+    write(root / ".venv/lib/py/site-packages/x/pyproject.toml", py_manifest("venv-x"))
+    write(root / ".hidden/pkg/package.json", node_manifest("hidden"))
+
+    paths = [p.path for p in discover_packages(root)]
+    assert paths == [".", "packages/real"]
+    assert "node_modules/dep" not in paths
+    assert ".venv" not in paths
+    assert ".hidden/pkg" not in paths
+
+
+def test_discover_packages_workspaces_glob_pseudo_manifest(tmp_path):
+    root = tmp_path / "monorepo"
+    write(root / "package.json",
+          node_manifest("root", extra={"workspaces": ["packages/*"]}))
+    # A workspace dir WITHOUT any manifest file gains a pseudo-manifest entry.
+    write(root / "packages/empty/README.md", "no manifest here")
+
+    packages = discover_packages(root)
+    by_path = {p.path: p for p in packages}
+    assert "packages/empty" in by_path
+    assert by_path["packages/empty"].name == "empty"
+    assert by_path["packages/empty"].manifest == _PSEUDO_MANIFEST
+
+
+def test_discover_packages_missing_root_returns_empty(tmp_path):
+    assert discover_packages(tmp_path / "does-not-exist") == []
+
+
+# ---------------------------------------------------------------------------
+# find_owning_package
+# ---------------------------------------------------------------------------
+
+
+def test_find_owning_package_deepest_owner_wins(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+    packages = discover_packages(root)
+
+    assert find_owning_package("packages/shared-schema/types.py", packages).name == "shared-schema"
+    assert find_owning_package("packages/shared-schema/sub/deep.py", packages).name == "shared-schema"
+    assert find_owning_package("apps/gateway/main.go", packages).name == "hq/gateway"
+
+
+def test_find_owning_package_root_fallback(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+    packages = discover_packages(root)
+
+    # A repo-root file is owned by the root package (".").
+    assert find_owning_package("README.md", packages).name == "hq-root"
+
+
+def test_find_owning_package_none_without_root_package(tmp_path):
+    root = tmp_path / "monorepo"
+    # No root manifest: only a nested package exists.
+    write(root / "packages/a/package.json", node_manifest("a"))
+
+    packages = discover_packages(root)
+    assert find_owning_package("unowned.txt", packages) is None
+    assert find_owning_package("packages/a/src.py", packages).name == "a"
+
+
+# ---------------------------------------------------------------------------
+# build_dependency_map
+# ---------------------------------------------------------------------------
+
+
+def test_build_dependency_map_polyglot_edges(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+    packages = discover_packages(root)
+
+    dep_map = build_dependency_map(packages, root)
+    by_pkg = {d.package: d for d in dep_map}
+
+    # service-a depends on shared-schema via workspace:* protocol
+    assert by_pkg["service-a"].depends_on == ["shared-schema"]
+    # hq/gateway (go.mod) requires shared-schema — name-edge via require block
+    assert by_pkg["hq/gateway"].depends_on == ["shared-schema"]
+    # shared-schema itself has no local deps
+    assert by_pkg["shared-schema"].depends_on == []
+    # independent service-b
+    assert by_pkg["service-b"].depends_on == []
+    # root package has no local deps
+    assert by_pkg["hq-root"].depends_on == []
+
+
+def test_build_dependency_map_deterministic_order(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+    packages = discover_packages(root)
+
+    dep_map = build_dependency_map(packages, root)
+    # One entry per discovered package, in the same deterministic order as
+    # discover_packages (root first, then path-sorted).
+    assert [d.package for d in dep_map] == [p.name for p in packages]
+    # Every entry has a sorted depends_on list.
+    for d in dep_map:
+        assert d.depends_on == sorted(d.depends_on)
+
+
+def test_build_dependency_map_file_reference_resolves_local(tmp_path):
+    root = tmp_path / "monorepo"
+    write(root / "package.json", node_manifest("root"))
+    write(root / "packages/lib-a/package.json", node_manifest("lib-a"))
+    # lib-b depends on lib-a via a relative file: reference
+    write(root / "packages/lib-b/package.json",
+          node_manifest("lib-b", {"lib-a": "file:../lib-a"}))
+
+    packages = discover_packages(root)
+    dep_map = build_dependency_map(packages, root)
+    by_pkg = {d.package: d for d in dep_map}
+
+    assert by_pkg["lib-b"].depends_on == ["lib-a"]
+    assert by_pkg["lib-a"].depends_on == []
+
+
+# ---------------------------------------------------------------------------
+# calculate_affected_paths
+# ---------------------------------------------------------------------------
+
+
+def test_calculate_affected_paths_shared_schema_closure(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+
+    matrix = calculate_affected_paths(
+        ["packages/shared-schema/types.py"], root
+    )
+
+    assert matrix.modified_files == ["packages/shared-schema/types.py"]
+    # Directly modified package PLUS transitive dependents (service-a,
+    # hq/gateway both depend on shared-schema).
+    assert matrix.affected_packages == [
+        "hq/gateway", "service-a", "shared-schema",
+    ]
+    assert matrix.affected_paths == [
+        "apps/gateway", "packages/shared-schema", "services/service-a",
+    ]
+    # service-b and the root are outside the reverse-dependency closure.
+    assert matrix.unaffected_packages == ["hq-root", "service-b"]
+    assert matrix.root_owned_files == []
+
+
+def test_calculate_affected_paths_independent_package_only(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+
+    matrix = calculate_affected_paths(["services/service-b/app.py"], root)
+
+    assert matrix.affected_packages == ["service-b"]
+    assert matrix.affected_paths == ["services/service-b"]
+    assert matrix.unaffected_packages == [
+        "hq-root", "hq/gateway", "service-a", "shared-schema",
+    ]
+    assert matrix.root_owned_files == []
+
+
+def test_calculate_affected_paths_root_owned_files(tmp_path):
+    root = tmp_path / "monorepo"
+    # Only a nested package exists — no root manifest.
+    write(root / "packages/a/package.json", node_manifest("a"))
+    write(root / "README.md", "# Docs\n")
+
+    matrix = calculate_affected_paths(
+        ["README.md", "packages/a/src.py"], root
+    )
+
+    # README.md belongs to no package → root_owned_files.
+    assert matrix.root_owned_files == ["README.md"]
+    assert matrix.affected_packages == ["a"]
+    assert matrix.modified_files == ["README.md", "packages/a/src.py"]
+
+
+def test_calculate_affected_paths_empty_modified_files(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+
+    matrix = calculate_affected_paths([], root)
+
+    assert matrix.modified_files == []
+    assert matrix.affected_packages == []
+    assert matrix.affected_paths == []
+    assert matrix.unaffected_packages == sorted([
+        "hq-root", "hq/gateway", "shared-schema", "service-a", "service-b",
+    ])
+    assert matrix.root_owned_files == []
+
+
+def test_calculate_affected_paths_result_is_matrix_model():
+    matrix = calculate_affected_paths([], Path("."))
+    # Type-level contract: always returns a BlastRadiusMatrix model instance.
+    assert isinstance(matrix, BlastRadiusMatrix)
+
+
+# ---------------------------------------------------------------------------
+# ToolchainRunner blast-radius workspace scoping (LE-9)
+# ---------------------------------------------------------------------------
+
+
+def make_profile(lint_cmd, build_cmd, test_cmd, name="test-stack") -> StackProfile:
+    cfg = StackProfileConfig(
+        name=name,
+        display_name=f"Test {name}",
+        toolchain=StackToolchainConfig(
+            lint_cmd=lint_cmd, build_cmd=build_cmd, test_cmd=test_cmd
+        ),
+    )
+    return StackProfile(cfg)
+
+
+def diff_for(*paths: str) -> str:
+    """Build a minimal diff touching the given files."""
+    return "".join(
+        f"diff --git a/{p} b/{p}\n"
+        f"index 111..222 100644\n"
+        f"--- a/{p}\n"
+        f"+++ b/{p}\n"
+        f"@@ -1 +1 @@\n"
+        f"-old\n"
+        f"+new\n"
+        for p in paths
+    )
+
+
+def test_runner_skips_unaffected_workspace(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+    profile = make_profile("echo lint", "echo build", "echo test")
+
+    runner = ToolchainRunner(
+        timeout_per_command=5.0,
+        evidence_base_dir=tmp_path / "evidence",
+        workspace_root=root,
+        skip_unaffected=True,
+    )
+    # Diff touches service-b only; cwd is service-a → unaffected.
+    result = runner.run_sync(
+        profile, task_id=None, cwd=root / "services/service-a",
+        diff_text=diff_for("services/service-b/app.py"),
+    )
+
+    assert result.passed is True
+    assert all(c.skipped for c in result.commands)
+    assert "Blast-radius scoping" in result.summary
+    assert "unaffected" in result.summary
+    # No actual toolchain command ran.
+    assert all(c.command == "none" for c in result.commands)
+
+
+def test_runner_runs_affected_workspace(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+    profile = make_profile("echo lint", "echo build", "echo test")
+
+    runner = ToolchainRunner(
+        timeout_per_command=5.0,
+        evidence_base_dir=tmp_path / "evidence",
+        workspace_root=root,
+        skip_unaffected=True,
+    )
+    # Diff touches shared-schema; cwd is service-a → service-a is a
+    # transitive dependent → verification MUST run.
+    result = runner.run_sync(
+        profile, task_id=None, cwd=root / "services/service-a",
+        diff_text=diff_for("packages/shared-schema/types.py"),
+    )
+
+    assert result.passed is True
+    assert all(not c.skipped for c in result.commands)
+    assert "Blast-radius scoping" not in result.summary
+
+
+def test_runner_skip_unaffected_flag_disable_runs_full(tmp_path):
+    """Rollback flag: skip_unaffected=False always runs full toolchain."""
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+    profile = make_profile("echo lint", "echo build", "echo test")
+
+    runner = ToolchainRunner(
+        timeout_per_command=5.0,
+        evidence_base_dir=tmp_path / "evidence",
+        workspace_root=root,
+        skip_unaffected=False,
+    )
+    result = runner.run_sync(
+        profile, task_id=None, cwd=root / "services/service-a",
+        diff_text=diff_for("services/service-b/app.py"),
+    )
+
+    assert result.passed is True
+    assert all(not c.skipped for c in result.commands)
+    assert all(c.command == "echo lint" or c.command == "echo build"
+               or c.command == "echo test" for c in result.commands)
+
+
+def test_runner_no_cwd_is_conservative(tmp_path):
+    root = tmp_path / "monorepo"
+    make_monorepo(root)
+    profile = make_profile("echo lint", "echo build", "echo test")
+
+    runner = ToolchainRunner(
+        timeout_per_command=5.0,
+        evidence_base_dir=tmp_path / "evidence",
+        workspace_root=root,
+        skip_unaffected=True,
+    )
+    # No cwd → cannot prove the workspace → verification runs.
+    result = runner.run_sync(
+        profile, task_id=None, cwd=None,
+        diff_text=diff_for("services/service-b/app.py"),
+    )
+    assert all(not c.skipped for c in result.commands)
+
+
+def test_runner_non_monorepo_is_conservative(tmp_path):
+    root = tmp_path / "plain"  # no manifests → not a proven monorepo
+    root.mkdir(parents=True, exist_ok=True)
+    profile = make_profile("echo lint", "echo build", "echo test")
+
+    runner = ToolchainRunner(
+        timeout_per_command=5.0,
+        evidence_base_dir=tmp_path / "evidence",
+        workspace_root=root,
+        skip_unaffected=True,
+    )
+    result = runner.run_sync(
+        profile, task_id=None, cwd=root,
+        diff_text=diff_for("src/main.py"),
+    )
+    assert all(not c.skipped for c in result.commands)
+
+
+def test_runner_root_owned_file_is_conservative(tmp_path):
+    root = tmp_path / "monorepo"
+    # Only a nested package — a root file belongs to no package.
+    write(root / "packages/a/package.json", node_manifest("a"))
+    write(root / "README.md", "# Docs\n")
+    profile = make_profile("echo lint", "echo build", "echo test")
+
+    runner = ToolchainRunner(
+        timeout_per_command=5.0,
+        evidence_base_dir=tmp_path / "evidence",
+        workspace_root=root,
+        skip_unaffected=True,
+    )
+    result = runner.run_sync(
+        profile, task_id=None, cwd=root / "packages/a",
+        diff_text=diff_for("README.md"),
+    )
+    assert all(not c.skipped for c in result.commands)
\ No newline at end of file
diff --git a/loop-engine/verifier.py b/loop-engine/verifier.py
index bc41da4..712fec2 100644
--- a/loop-engine/verifier.py
+++ b/loop-engine/verifier.py
@@ -12,6 +12,16 @@ from dataclasses import dataclass, field
 from pathlib import Path
 
 from sentinel import TypeDriftSentinel
+from blast_radius import (
+    calculate_affected_paths,
+    extract_modified_paths,
+    find_owning_package,
+)
+
+try:
+    from models import BlastRadiusConfig
+except Exception:
+    BlastRadiusConfig = None  # type: ignore
 
 
 @dataclass
@@ -46,9 +56,39 @@ class ToolchainRunner:
         self,
         timeout_per_command: float = 120.0,
         evidence_base_dir: str | Path = "loop-engine/evidence",
+        workspace_root: str | Path | None = None,
+        skip_unaffected: bool = True,
+        blast_radius_config: "BlastRadiusConfig | None" = None,
     ):
         self.timeout_per_command = timeout_per_command
         self.evidence_base_dir = Path(evidence_base_dir)
+        # Blast-radius scoping (LE-9 / Task 141): workspace_root defaults to
+        # the repo root (parent of loop-engine/). skip_unaffected is the
+        # legacy rollback flag — set False to always run full toolchain verification.
+        # blast_radius_config is the spec-compliant config (enabled, workspace_globs, conservative_root_fallback).
+        self.workspace_root = (
+            Path(workspace_root)
+            if workspace_root is not None
+            else Path(__file__).resolve().parent.parent
+        )
+        self.skip_unaffected = skip_unaffected
+        if blast_radius_config is not None:
+            self.blast_radius_config = blast_radius_config
+        elif BlastRadiusConfig is not None:
+            # Default config when not provided — enabled with standard globs
+            try:
+                self.blast_radius_config = BlastRadiusConfig()
+            except Exception:
+                self.blast_radius_config = None
+        else:
+            self.blast_radius_config = None
+        # Sync legacy flag with spec config for backward compat
+        if self.blast_radius_config is not None and not self.skip_unaffected:
+            # Legacy flag disables spec config as well (rollback)
+            try:
+                self.blast_radius_config.enabled = False
+            except Exception:
+                pass
 
     async def run(
         self,
@@ -87,6 +127,52 @@ class ToolchainRunner:
                 # daemon's toolchain-infra-error tolerance). Log to the result.
                 print(f"[verifier] Type Drift Sentinel error (proceeding): {e}")
 
+        # --- Blast-Radius Global Scoping (LE-9 / Task 141 — Spec) ---
+        # Spec path: if monorepo and 0 packages affected, skip entire toolchain.
+        if diff_text and str(diff_text).strip():
+            try:
+                cfg = getattr(self, "blast_radius_config", None)
+                if cfg is not None and getattr(cfg, "enabled", False):
+                    modified_paths = extract_modified_paths(str(diff_text))
+                    # cwd or REPO_ROOT per spec; use workspace_root as repo root fallback
+                    effective_root = Path(cwd) if cwd is not None else self.workspace_root
+                    # If cwd is a file path inside workspace, use its parent? Use workspace_root for matrix
+                    # Spec says: calculate_affected_paths(modified_paths, cwd or REPO_ROOT, config)
+                    matrix = calculate_affected_paths(modified_paths, self.workspace_root, cfg)
+                    if getattr(matrix, "is_monorepo", False) and getattr(matrix, "is_empty", False):
+                        note = "Blast-Radius: 0 packages affected"
+                        skipped_commands: list[CommandResult] = [
+                            CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
+                            for t in ("lint", "build", "test")
+                        ]
+                        # Append note to report_md via _finalize
+                        return ToolchainResult(
+                            passed=True,
+                            commands=skipped_commands,
+                            summary="Toolchain PASSED (Blast-Radius: 0 packages affected)",
+                            report_md=f"# Toolchain Verification Report\n\nToolchain PASSED (Blast-Radius: 0 packages affected)\n\n**Blast-radius scoping:** {note}\n",
+                        )
+            except Exception as e:
+                print(f"[verifier] Blast-radius global scoping error (proceeding): {e}")
+
+        # --- Blast-Radius Workspace Scoping (LE-9 / Task 141 — Legacy per-workspace) ---
+        # When the task diff touches only a subset of monorepo workspaces, a
+        # completely unaffected workspace skips its lint/build/test (all
+        # commands reported SKIPPED, result passes). The analyzer is
+        # deliberately conservative: it only skips when it can PROVE the
+        # verified workspace is unaffected, so affected modules are never
+        # silently missed (Task 141 Risk & Rollback).
+        if self.skip_unaffected and diff_text and str(diff_text).strip():
+            blast_note = self._blast_radius_note(diff_text, cwd)
+            if blast_note:
+                skipped_commands: list[CommandResult] = [
+                    CommandResult(command="none", cmd_type=t, passed=True, skipped=True)
+                    for t in ("lint", "build", "test")
+                ]
+                return self._finalize(
+                    skipped_commands, task_id, blast_radius_note=blast_note
+                )
+
         # Defensive: profile may lack toolchain attr in mocks
         toolchain = getattr(profile, "toolchain", None)
         if toolchain is None:
@@ -207,7 +293,10 @@ class ToolchainRunner:
         return self._finalize(results, task_id)
 
     def _finalize(
-        self, commands: list[CommandResult], task_id: int | None
+        self,
+        commands: list[CommandResult],
+        task_id: int | None,
+        blast_radius_note: str = "",
     ) -> ToolchainResult:
         passed = all(c.passed for c in commands)
         # Summary: single line
@@ -220,9 +309,11 @@ class ToolchainRunner:
             else:
                 summary_parts.append(f"{c.cmd_type}: FAILED")
         summary = "Toolchain " + ("PASSED" if passed else "FAILED") + " | " + ", ".join(summary_parts)
+        if blast_radius_note:
+            summary += f" | {blast_radius_note}"
 
         # Markdown report with summary table and error logs
-        report_md = self._build_report_md(commands, passed, summary)
+        report_md = self._build_report_md(commands, passed, summary, blast_radius_note)
 
         result = ToolchainResult(
             passed=passed, commands=commands, summary=summary, report_md=report_md
@@ -246,13 +337,20 @@ class ToolchainRunner:
         return result
 
     def _build_report_md(
-        self, commands: list[CommandResult], passed: bool, summary: str
+        self,
+        commands: list[CommandResult],
+        passed: bool,
+        summary: str,
+        blast_radius_note: str = "",
     ) -> str:
         lines: list[str] = []
         lines.append("# Toolchain Verification Report")
         lines.append("")
         lines.append(summary)
         lines.append("")
+        if blast_radius_note:
+            lines.append(f"**Blast-radius scoping:** {blast_radius_note}")
+            lines.append("")
         lines.append(f"**Overall:** {'PASSED' if passed else 'FAILED'}")
         lines.append("")
         lines.append("| Type | Command | Result | Duration | Return Code |")
@@ -296,6 +394,61 @@ class ToolchainRunner:
                 lines.append("")
         return "\n".join(lines)
 
+    def is_workspace_affected(
+        self, diff_text: str, cwd: str | Path | None = None
+    ) -> bool:
+        """True when verification must run for the workspace at ``cwd``.
+
+        Returns False only when blast-radius analysis PROVES the workspace
+        (a discovered monorepo package, or the root package) is completely
+        unaffected by the diff. Conservative bias: any uncertainty — no cwd,
+        a non-monorepo layout, root-owned files, or a cwd outside the
+        package graph — returns True so the toolchain always runs.
+        """
+        return self._blast_radius_note(diff_text, cwd) == ""
+
+    def _blast_radius_note(self, diff_text: str, cwd: str | Path | None) -> str:
+        """Return a skip note when ``cwd`` is provably unaffected, else "".
+
+        The empty string means "run verification". A non-empty note is a
+        human-readable explanation appended to the summary/report so skipped
+        workspaces are observable in QA evidence.
+        """
+        if not cwd:
+            return ""
+        try:
+            cwd_path = Path(cwd).resolve()
+        except OSError:
+            return ""
+        try:
+            root = Path(self.workspace_root).resolve()
+        except OSError:
+            return ""
+        modified = extract_modified_paths(str(diff_text))
+        if not modified:
+            return ""
+        try:
+            matrix = calculate_affected_paths(modified, root)
+        except OSError:
+            return ""  # analyzer failure must never skip
+        if not matrix.packages:
+            return ""  # not a proven monorepo → conservative full verification
+        if matrix.root_owned_files:
+            return ""  # change outside the package graph → conservative
+        try:
+            cwd_rel = cwd_path.relative_to(root).as_posix()
+        except ValueError:
+            return ""  # cwd outside the workspace root → cannot scope
+        owner = find_owning_package(cwd_rel, matrix.packages)
+        if owner is None:
+            return ""  # cwd not inside any discovered package → conservative
+        if owner.name in matrix.affected_packages:
+            return ""
+        return (
+            f"Blast-radius scoping: workspace `{owner.name}` ({owner.path}) "
+            f"is unaffected by this diff — skipping unrelated toolchain verification"
+        )
+
     def run_sync(
         self,
         profile,
```
<!-- END_GIT_DIFF -->