# Task 239: opencode-init LSP formatter shape correction

**File:** `tasks/qa/239-opencode-init-shape-correction.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Land the uncommitted opencode-init shape correction: flat LSP map, named formatter map, env-not-environment, stale language-server wrapper rejection.

## Manager's Notes

Autopilot locked for this order. Work the worktree changes, verify, stage, move to qa, Brain QA + review. Close only on explicit approval word.

Worktree truth: 6 unstaged modified files — CHANGELOG.md, skill-templates/opencode-init/SKILL.md, references/examples/golden-opencode.json, references/runtime-matrix.md, scripts/validate-opencode.py, tests/test_skill_registry.py. Evidence: real runtime rejections of the `language-server` wrapper shape from apex and blowsh-mcp. Blown fuses: L2-L6 in test_skill_registry (4 pre-existing fails) stay red until this lands.

## Local TODOs

- [x] Verify validator on golden + fixtures
- [x] Run registry suite, confirm red-to-green
- [x] CHANGELOG Parse-Then-Append check
- [x] lint_task_file, stage_and_inject_diff, git mv to qa

## Acceptance Criteria

- [x] Validator accepts corrected golden, rejects wrapper shape with global-path error
- [x] tests/test_skill_registry.py fully green
- [x] CHANGELOG entry present
- [x] Diff staged, file in qa, no commit, no close

## Verification Evidence

- **Test command:** uv tool run --with mcp==1.4.1 --with pathspec --with pytest pytest tests/test_skill_registry.py -q
- **Expected result:** all pass, exit 0
- **Actual result:** registry 20 passed exit 0; validator golden exit 0, wrapper fixture exit 1 with flat-map error; CHANGELOG bullet present in worktree diff
- **Exit code:** 0 (both)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** validator over-rejects valid project files
- **Rollback plan:** worktree diff revert, no commit yet

---

## Execution Log & Reasoning

Autopilot locked for Manager order (his word is the plan). Seat Check: Senior Programmer (validator + template + tests); no UI/schema/sprint triggers — Designer/Planner/Strategist skipped with reason; QA/Reviewer judge later turns. File landed in in-progress via git-mv-fallback path (untracked). Work was already in worktree (Manager-authored correction); Hands verified, did not author: registry 20 passed, golden exit 0, wrapper rejected with flat-map error. Replayed from DEC-20260914-003 (standing autopilot), DEC-20260915-001 (fix-all via Hands).

QA verdict: VERDICT QA_PASSED with cites (SKILL:18, golden:9, matrix:10, validator:168, CHANGELOG:19, task:32); residuals R1 validator tail truncated, R2 DoD build box unchecked — R2 fixed per box-checking mandate (registry 20 passed exit 0 + lint passed), restaged.

Reviewer verdict: PO_REVIEW_PENDING (technical approval, no blocking defect). Low notes: R1 CHANGELOG bullet omits task number; R2 acceptance text says global-path error, validator emits flat-map error; R3 test hunks truncated in reviewer view; R4 CHANGELOG mentions home-config sync path. Recommendations A1-A3 logged for a future docs pass; none block. Closure needs exact words "Approved for closure" or "Close task". File stays in tasks/qa. No commit.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 38ad2a3..d08357a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -15,7 +15,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
  - **Brain sessions per project, legacy global read-through (Task 234):** `mcp-brain-bridge/loop_guard.py` gains `project_sessions_root()` (explicit override → param/`BRAIN_PROJECT_ROOT`/`BRAIN_WORKSPACE_ROOT` → cwd walk-up to a `tasks/` dir → legacy global fallback) plus `legacy_sessions_root()`; `server.py` threads an optional `project_root` through `_sessions_root`, `_transcript_path`, `_fed_context_path`, `load_history`, `append_turn`, `save/load_fed_context`, and `brain_turn` — writes always land per project under `tasks/.sessions/<id>/`, while reads fall back to the legacy global dir with a loud stderr note when the per-project file is missing. HQ folders 230-233 migrated from the global store into `tasks/.sessions/` with a sha256 manifest (`/tmp/migrate-234-manifest.json`), globals kept as fallback. 4 new offline regression tests. Full suite: **354 passed**. Hotfix: no-global-write (fallback writes reroute to `cwd/tasks/.sessions` with stderr warn), package-then-plain sibling import, per-project loop-guard hashes with legacy read fallback, per-turn sessions-root stderr line, 3 more tests (T5-T7). Full suite: **357 passed**.
   - **Review-approval relay + session-history gitignore (Task 235):** `agents/cognitive-executor.md` gains a Review-approval relay rule (technical approval → verbatim relay, file stays in qa; only the exact words "Approved for closure"/"Close task" count; Hands re-calls Brain Programmer once for a single final-closure XML and executes it exactly once) plus a relay line in the Code Reviewer roster row. `prompts/fragments/06-personas.md` Code Reviewer contract now routes closure through the relayed Programmer XML instead of emitting it directly. Shipped prompt rebuilt to 9.37.0. Global `audit-agents` skill Plugin Runtime-State rule now covers Brain session history (`tasks/.sessions/` added only after confirming the dir exists). Hotfix: relay tightened (bare-approved counts only as the next message answering the relayed question; explicit never-list incl. yes/done/okay/looks-good/emoji/silence; qa + PO_REVIEW_PENDING double-gate; single issuance with failure-only re-call; autopilot self-decision never satisfies); repo `skill-templates/audit-agents/SKILL.md` template extended too (both occurrences) so the rule ships in-repo. Second hotfix: reviewer contract mirrors the executor relay exactly (bare-approved exception + full never-list incl. okay/done/fine/looks-good/emoji-only + autopilot bar), audit clause gains a duplicate-line guard (check first, add only if missing), shipped prompt rebuilt to 9.37.2.
   - **Lean-retry state note + migrate Task 234 session (Task 236):** `mcp-brain-bridge/server.py` `_empty_output_hint` and the executor Empty-output clause gain a state-freshness sentence: a lean retry drops the bundle, so if the answer judges stale or missing context, re-run ONCE with the full bundle plus diff before escalating (proven by the 235 turn-3 stale verdict). Task 234's global transcript + fed context migrated into `tasks/.sessions/234/` with sha256-verified manifest. 4 new regression assertions (stale sentence, state line, 2 unknown fallbacks). Full suite: **357 passed**.
- - **opencode-init project-only contract (Task 237):** `skill-templates/opencode-init/` now generates project-only `opencode.json` — allowlist `$schema`, `default_agent`, `instructions`, `formatter`, `lsp` (guidance only), `permission` (ZAC denies intact); `mcp` and `plugin` are global-only (install in `~/.config/opencode/opencode.json` or a plugins dir) and are omitted on generate, rejected on validate. SKILL.md stops asking for MCP env keys/plugin choice and writes a global-install note instead; `references/runtime-matrix.md` V1 row + MCP/plugin global-only rows + formatter row; `references/examples/golden-opencode.json` drops `mcp`/`plugin`, adds `formatter: true` + `language-server` LSP example; `scripts/validate-opencode.py` rejects `mcp`/`plugin` with global-path errors, keeps ZAC/invented-value/`$schema` gates, and extends `lsp` checks (`{env:}`-only env, invented-command rejection). Validator: exit 0 on golden, exit 1 naming both keys on an mcp+plugin fixture. Known migration: pre-existing project files with inline `mcp` (incl. this repo's root `opencode.json`) now fail validation by design.
+  - **opencode-init project-only contract (Task 237):** `skill-templates/opencode-init/` now generates project-only `opencode.json` — allowlist `$schema`, `default_agent`, `instructions`, `formatter`, `lsp` (guidance only), `permission` (ZAC denies intact); `mcp` and `plugin` are global-only (install in `~/.config/opencode/opencode.json` or a plugins dir) and are omitted on generate, rejected on validate. SKILL.md stops asking for MCP env keys/plugin choice and writes a global-install note instead; `references/runtime-matrix.md` V1 row + MCP/plugin global-only rows + formatter row; `references/examples/golden-opencode.json` drops `mcp`/`plugin`, adds `formatter: true` + `language-server` LSP example; `scripts/validate-opencode.py` rejects `mcp`/`plugin` with global-path errors, keeps ZAC/invented-value/`$schema` gates, and extends `lsp` checks (`{env:}`-only env, invented-command rejection). Validator: exit 0 on golden, exit 1 naming both keys on an mcp+plugin fixture. Known migration: pre-existing project files with inline `mcp` (incl. this repo's root `opencode.json`) now fail validation by design.
+ - **opencode-init LSP/formatter shape correction:** `skill-templates/opencode-init/` enforced a stale `language-server` LSP wrapper and an ambiguous flat formatter that the real runtime (`opencode debug config` against https://opencode.ai/config.json) rejects — apex failed with `Missing key formatter.command`, blowsh-mcp with `Missing key lsp.language-server.command`. Golden file, `references/runtime-matrix.md`, SKILL.md Ground Truth/workflow/rules, and `scripts/validate-opencode.py` now emit and enforce the true shapes: LSP flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}` (`env`, never `environment`), formatter `true|false|{<name>: {command?, extensions?, environment?, disabled?}}`; the wrapper and flat-formatter fixtures fail with actionable errors. Installed copy at `~/.config/opencode/skills/opencode-init/` re-synced identical. `tests/test_skill_registry.py`: 6 stale tests rewritten (contract markers, secret-via-LSP-env, wrapper rejection, formatter named-map, mcp/plugin global-only rejection, flat-LSP positives) + 2 new tests; runnable suites **34 passed** (decision/brain suites error on pre-existing missing `mcp` module, untouched).
 
 ### Fixed
 
diff --git a/skill-templates/opencode-init/SKILL.md b/skill-templates/opencode-init/SKILL.md
index eae74d9..e15eb15 100644
--- a/skill-templates/opencode-init/SKILL.md
+++ b/skill-templates/opencode-init/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: opencode-init
-description: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. V1 runtime shapes only; validates before writing.
+description: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. Matches https://opencode.ai/config.json shapes; validates before writing.
 ---
 
 # Skill: opencode-init
@@ -11,20 +11,31 @@ description: Analyze a project (or ask the user) and generate a comprehensive, c
 
 Turn project analysis into a working `opencode.json` for THAT project only.
 Analyze stack files, ask the user for gaps (default agent,
-formatter, LSP guidance, instructions, permissions), emit V1-runtime JSON,
+formatter, LSP guidance, instructions, permissions), emit JSON matching
+the public schema (https://opencode.ai/config.json),
 then validate with `scripts/validate-opencode.py` before writing.
 MCP servers and plugins install GLOBALLY — never emit `mcp` or `plugin`
 into the project file. Never edit global config. Never install plugins.
 
-## Ground Truth (this repo's runtime — file evidence wins over public docs)
+## Ground Truth (public schema wins — verified 2026-09-16)
 
-- Shape: flat V1 map. Project-only top keys: `$schema`, `default_agent`,
-  `instructions[]`, `formatter`, `lsp` (guidance only — enable/tune,
-  never install), `permission{}`. The `permission` map is
+- Shape: project-only top keys: `$schema`, `default_agent`,
+  `instructions[]`, `formatter`, `lsp`, `permission{}`. The `permission` map is
   `tool-name → allow|ask|deny`, plus a `bash` sub-map of
   `command-pattern → deny` and optional scoped sub-maps
   (e.g. `external_directory`). There is NO `permissions[]` array here.
   `mcp{}` and `plugin[]` are GLOBAL-only and banned from project output.
+- Formatter: `true` | `false` | named map
+  `{<name>: {command?, extensions?, environment?, disabled?}}`.
+  NEVER emit a flat `{command, extensions}` object — it fails with
+  `Missing key formatter.command`. Example:
+  `{"spotless-java": {"command": ["mvn", "spotless:apply"], "extensions": [".java"]}}`.
+- LSP: `true` | `false` | flat map
+  `{<name>: {command (required), extensions?, env?, initialization?, disabled?}}`.
+  NEVER wrap in a `language-server` key — it fails with
+  `Missing key lsp.language-server.command` because the runtime treats
+  `language-server` as a server name. LSP uses `env`, NOT `environment`.
+  Example: `{"typescript": {"command": ["typescript-language-server", "--stdio"]}}`.
 - MCP server: global-only. Shared servers live in the global config
   (`~/.config/opencode/opencode.json`) or a global plugin directory —
   project output carries NO `mcp` block. Secrets travel ONLY as
@@ -34,9 +45,10 @@ into the project file. Never edit global config. Never install plugins.
   `.opencode/*` wins. Global holds shared MCP and plugins;
   the project file holds overrides only (formatter, LSP guidance,
   instructions, permissions).
-- The public schema reference leans V2 and mismatches this runtime —
-  see `references/runtime-matrix.md`. When file and docs disagree, the
-  local `opencode.json` (copied at `references/examples/golden-opencode.json`) wins.
+- Schema authority: https://opencode.ai/config.json plus
+  `references/runtime-matrix.md`. The golden file
+  (`references/examples/golden-opencode.json`) is a known-good example
+  that MUST pass both this validator and `opencode debug config`.
 
 ## Workflow
 
@@ -49,9 +61,10 @@ into the project file. Never edit global config. Never install plugins.
    instructions/permission choices. Ask with explicit questions;
    ambiguous means NOT answered — HALT and re-ask rather than
    inventing values. Never ask for MCP env keys or plugin selection.
-3. **Generate.** Emit V1 project-only JSON: `$schema`, `default_agent`,
+3. **Generate.** Emit project-only JSON: `$schema`, `default_agent`,
    `instructions[]` (existing doc paths only), `formatter`
-   (`true`|`false`|custom command), `lsp` (guidance only),
+   (`true`|`false`|named map `{<name>: {command, extensions?, environment?, disabled?}}`),
+   `lsp` (`true`|`false`|flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}`),
    `permission{}` (tool allows + full ZAC `bash` deny set).
    Omit `mcp` and `plugin` entirely; instead write a human note naming
    the global install paths (`~/.config/opencode/opencode.json`,
@@ -62,8 +75,9 @@ into the project file. Never edit global config. Never install plugins.
 
 ## Rules
 
-- V1 project-only output. `mcp` and `plugin` keys, `permissions[]`
-  arrays, V2 LSP objects, and any key the validator rejects are forbidden.
+- Project-only output. `mcp` and `plugin` keys, `permissions[]`
+  arrays, `language-server` LSP wrappers, flat formatter objects,
+  and any key the validator rejects are forbidden.
 - Project key allowlist: `$schema`, `default_agent`, `instructions`,
   `formatter`, `lsp`, `permission`. Output keys MUST subset this list.
 - ZAC deny set is mandatory in every generated file: `git add`, `git add *`,
diff --git a/skill-templates/opencode-init/references/examples/golden-opencode.json b/skill-templates/opencode-init/references/examples/golden-opencode.json
index a7f2c36..aa483de 100644
--- a/skill-templates/opencode-init/references/examples/golden-opencode.json
+++ b/skill-templates/opencode-init/references/examples/golden-opencode.json
@@ -6,10 +6,8 @@
   ],
   "formatter": true,
   "lsp": {
-    "language-server": {
-      "typescript": {
-        "command": ["typescript-language-server", "--stdio"]
-      }
+    "typescript": {
+      "command": ["typescript-language-server", "--stdio"]
     }
   },
   "permission": {
diff --git a/skill-templates/opencode-init/references/runtime-matrix.md b/skill-templates/opencode-init/references/runtime-matrix.md
index f818a2c..f7006d7 100644
--- a/skill-templates/opencode-init/references/runtime-matrix.md
+++ b/skill-templates/opencode-init/references/runtime-matrix.md
@@ -7,8 +7,8 @@
 | Bash rules | `permission.bash = {"git commit": "deny", ...}` string map | Structured rule objects |
 | MCP | GLOBAL-ONLY — install in `~/.config/opencode/opencode.json`; banned from project output | Any `mcp{}` block in a generated project file |
 | Plugin | GLOBAL-ONLY — npm spec in global config or `.opencode/plugins/` / `~/.config/opencode/plugins/`; banned from project output | Any `plugin[]` list in a generated project file |
-| LSP (project guidance) | `language-server: {name: {command}}` map — enable/tune per project; server install stays host/global side | `enabled` + per-extension bool/object |
-| Formatter (project) | `true` (all built-ins) \| `false` (disable) \| custom `{command, extensions}` map | — |
+| LSP (project guidance) | flat map `{name: {command, extensions?, env?, initialization?, disabled?}}` — e.g. `{"typescript": {"command": [...]}}`; `true`/`false` also valid; server install stays host/global side | `language-server` wrapper (`{language-server: {name: ...}}`), `environment` (LSP uses `env`), unknown keys |
+| Formatter (project) | `true` (all built-ins) \| `false` (disable) \| named map `{<name>: {command?, extensions?, environment?, disabled?}}` — e.g. `{"spotless-java": {"command": [...], "extensions": [".java"]}}` | flat `{command, extensions}` without a name key |
 | Secrets (global scope) | `"{env:NAME}"` placeholders only — project output carries no secret-bearing blocks | Literal values (validator fails these) |
 | Plugin env (global scope) | dict `environment` with `{env:}` values only | Literal values (validator fails these) |
 
diff --git a/skill-templates/opencode-init/scripts/validate-opencode.py b/skill-templates/opencode-init/scripts/validate-opencode.py
index 1142fa5..19c5847 100644
--- a/skill-templates/opencode-init/scripts/validate-opencode.py
+++ b/skill-templates/opencode-init/scripts/validate-opencode.py
@@ -1,10 +1,18 @@
-"""Validate a generated opencode.json against the V1 PROJECT-ONLY contract.
+"""Validate a generated opencode.json against the project-only contract.
+
+Matches the public schema https://opencode.ai/config.json
+(verified 2026-09-16 via `opencode debug config`):
+
+  formatter: true | false | {<name>: {command?, extensions?,
+             environment?, disabled?}}
+  lsp:       true | false | {<name>: {command (required), extensions?,
+             env?, initialization?, disabled?} | {disabled: true}}
 
 Usage: python3 validate-opencode.py <path-to-opencode.json>
 Exit 0 = valid. Exit 1 = errors printed, one per line.
 
 Project allowlist: $schema, default_agent, instructions, formatter,
-lsp (guidance only), permission. `mcp` and `plugin` are GLOBAL-ONLY
+lsp, permission. `mcp` and `plugin` are GLOBAL-ONLY
 (installed in ~/.config/opencode/opencode.json or a plugins directory)
 and are REJECTED in project output.
 
@@ -15,10 +23,13 @@ Checks (stdlib only):
   4. ZAC bash deny set present (all 8 patterns must be "deny").
   5. Project-only keys: `mcp` and `plugin` keys rejected with a
      global-path error (shared servers/plugins belong in global config).
-  6. No literal secrets: any `lsp language-server` environment value not
+  6. No literal secrets: any lsp `env` / formatter `environment` value not
      starting with "{env:" fails (secrets travel as placeholders only).
-  7. LSP is V1-only: a `language-server` map of {name: {command: [...]}};
-     V2 `enabled`/`extensions` keys and unknown lsp keys are rejected.
+  7. LSP is a flat map of {name: {command: [...]}}; a `language-server`
+     wrapper, `enabled`, and unknown keys are rejected. `env` is the
+     only env key (LSP uses `env`, NOT `environment`).
+  7b. Formatter is true|false|named map; a flat {command, extensions}
+     object without a name key is rejected.
   8. Plugin entries forbidden: any `plugin` key fails (global-only).
   9. No invented values: TODO/changeme/xxx/your-value-here/foo/bar/dummy/
      placeholder (any case) and standalone "example"/"sample" are
@@ -150,49 +161,118 @@ def validate(cfg: dict) -> list[str]:
         )
     lsp = cfg.get("lsp")
     if lsp is not None:
-        if not isinstance(lsp, dict):
-            errors.append("lsp must be an object")
-        elif "enabled" in lsp or "extensions" in lsp:
-            errors.append(
-                "V2 lsp keys forbidden; use V1 'language-server' map"
-            )
+        if isinstance(lsp, bool):
+            pass
+        elif not isinstance(lsp, dict):
+            errors.append("lsp must be an object or boolean")
         else:
-            for lsp_name, spec in lsp.items():
-                if lsp_name != "language-server" or not isinstance(spec, dict):
-                    errors.append(
-                        "lsp allows only a V1 'language-server' map of servers"
-                    )
-                    break
-                for srv_name, srv_spec in spec.items():
+            if "language-server" in lsp:
+                errors.append(
+                    "lsp must be a flat map of servers "
+                    "(e.g. {\"typescript\": {\"command\": [...]}}); "
+                    "the 'language-server' wrapper is forbidden"
+                )
+            else:
+                for srv_name, srv_spec in lsp.items():
+                    if srv_spec == {"disabled": True}:
+                        continue
                     if not isinstance(srv_spec, dict):
                         errors.append(
-                            f"lsp language-server[{srv_name}] must be an object"
+                            f"lsp[{srv_name}] must be an object"
                         )
                         continue
+                    if "enabled" in srv_spec:
+                        errors.append(
+                            f"lsp[{srv_name}] uses unknown key 'enabled'; "
+                            "use 'disabled' instead"
+                        )
+                    if "environment" in srv_spec:
+                        errors.append(
+                            f"lsp[{srv_name}] uses unknown key 'environment'; "
+                            "LSP uses 'env'"
+                        )
+                    allowed = {"command", "extensions", "disabled", "env",
+                               "initialization"}
+                    for key in srv_spec:
+                        if key not in allowed:
+                            errors.append(
+                                f"lsp[{srv_name}] has unknown key {key!r}"
+                            )
                     cmd = srv_spec.get("command")
                     if not isinstance(cmd, list) or not cmd:
                         errors.append(
-                            f"lsp language-server[{srv_name}] needs a non-empty command list"
+                            f"lsp[{srv_name}] needs a non-empty command list"
                         )
                     elif _has_placeholder(*cmd):
                         errors.append(
-                            f"lsp language-server[{srv_name}].command looks invented"
+                            f"lsp[{srv_name}].command looks invented"
                         )
-                    env = srv_spec.get("environment", {})
+                    env = srv_spec.get("env", {})
                     if not isinstance(env, dict):
                         errors.append(
-                            f"lsp language-server[{srv_name}].environment must be an object"
+                            f"lsp[{srv_name}].env must be an object"
                         )
                     else:
                         for var, val in env.items():
                             if not isinstance(val, str) or not val.startswith("{env:"):
                                 errors.append(
-                                    f"lsp language-server[{srv_name}].environment[{var}] must be an '{{env:}}' placeholder"
+                                    f"lsp[{srv_name}].env[{var}] must be an '{{env:}}' placeholder"
                                 )
                             if isinstance(val, str) and SECRET_LIKE.search(val):
                                 errors.append(
-                                    f"lsp language-server[{srv_name}].environment[{var}] looks like a literal secret"
+                                    f"lsp[{srv_name}].env[{var}] looks like a literal secret"
                                 )
+    formatter = cfg.get("formatter")
+    if formatter is not None:
+        if isinstance(formatter, bool):
+            pass
+        elif not isinstance(formatter, dict):
+            errors.append("formatter must be an object or boolean")
+        elif "command" in formatter or "extensions" in formatter:
+            errors.append(
+                "formatter must be a named map "
+                "(e.g. {\"spotless-java\": {\"command\": [...], "
+                "\"extensions\": [\".java\"]}}); flat {command, extensions} "
+                "without a name key is forbidden"
+            )
+        else:
+            for fmt_name, fmt_spec in formatter.items():
+                if not isinstance(fmt_spec, dict):
+                    errors.append(
+                        f"formatter[{fmt_name}] must be an object"
+                    )
+                    continue
+                allowed = {"command", "extensions", "environment", "disabled"}
+                for key in fmt_spec:
+                    if key not in allowed:
+                        errors.append(
+                            f"formatter[{fmt_name}] has unknown key {key!r}"
+                        )
+                cmd = fmt_spec.get("command")
+                if cmd is not None:
+                    if not isinstance(cmd, list) or not cmd:
+                        errors.append(
+                            f"formatter[{fmt_name}].command must be a non-empty list"
+                        )
+                    elif _has_placeholder(*cmd):
+                        errors.append(
+                            f"formatter[{fmt_name}].command looks invented"
+                        )
+                env = fmt_spec.get("environment", {})
+                if not isinstance(env, dict):
+                    errors.append(
+                        f"formatter[{fmt_name}].environment must be an object"
+                    )
+                else:
+                    for var, val in env.items():
+                        if not isinstance(val, str) or not val.startswith("{env:"):
+                            errors.append(
+                                f"formatter[{fmt_name}].environment[{var}] must be an '{{env:}}' placeholder"
+                            )
+                        if isinstance(val, str) and SECRET_LIKE.search(val):
+                            errors.append(
+                                f"formatter[{fmt_name}].environment[{var}] looks like a literal secret"
+                            )
     return errors
 
 
diff --git a/tests/test_skill_registry.py b/tests/test_skill_registry.py
index c503636..43e74c6 100644
--- a/tests/test_skill_registry.py
+++ b/tests/test_skill_registry.py
@@ -134,7 +134,8 @@ def test_opencode_init_skill_contract():
     text = _template_text("opencode-init")
     for required in (
         "validate-opencode.py",
-        "V1",
+        "flat map",
+        "named map",
         "default_agent",
         "{env:",
         "git commit",
@@ -190,8 +191,8 @@ def test_validate_opencode_script():
     code, out = run(no_zac)
     assert code == 1 and "git push *" in out
     secret = json.loads(json.dumps(base))
-    first_srv = next(iter(secret["mcp"]))
-    secret["mcp"][first_srv]["environment"] = {"KEY": "sk-live-abc123"}
+    secret["lsp"] = {"pyright": {"command": ["pyright"],
+                                 "env": {"KEY": "sk-live-abc123"}}}
     code, out = run(secret)
     assert code == 1 and "placeholder" in out
 
@@ -237,43 +238,73 @@ def test_validate_lsp_v2_keys_rejected():
         assert code == 1 and "lsp" in out.lower()
 
 
+def test_validate_lsp_wrapper_rejected():
+    cfg = _fresh_golden()
+    cfg["lsp"] = {"language-server": {"typescript": {"command": ["typescript-language-server", "--stdio"]}}}
+    code, out = _run_validator(cfg)
+    assert code == 1 and "language-server" in out
+    cfg = _fresh_golden()
+    cfg["lsp"] = {"pyright": {"command": ["pyright"], "environment": {"K": "{env:K}"}}}
+    code, out = _run_validator(cfg)
+    assert code == 1 and "env" in out
+
+
 def test_validate_lsp_null_empty_and_valid():
     cfg = _fresh_golden()
-    cfg["lsp"] = {"language-server": {"py": None}}
+    cfg["lsp"] = {"py": None}
     assert _run_validator(cfg)[0] == 1
     cfg = _fresh_golden()
-    cfg["lsp"] = {"language-server": {"py": {"command": []}}}
+    cfg["lsp"] = {"py": {"command": []}}
     code, out = _run_validator(cfg)
     assert code == 1 and "command" in out.lower()
     cfg = _fresh_golden()
-    cfg["lsp"] = {"language-server": {"py": {}}}
+    cfg["lsp"] = {"py": {}}
     assert _run_validator(cfg)[0] == 1
     cfg = _fresh_golden()
-    cfg["lsp"] = {"language-server": {"pyright": {"command": ["pyright"]}}}
+    cfg["lsp"] = {"pyright": {"command": ["pyright"]}}
+    assert _run_validator(cfg) == (0, "")
+    cfg = _fresh_golden()
+    cfg["lsp"] = {"pyright": {"command": ["pyright"],
+                              "extensions": [".py"],
+                              "env": {"KEY": "{env:KEY}"}}}
+    assert _run_validator(cfg) == (0, "")
+    cfg = _fresh_golden()
+    cfg["lsp"] = {"pyright": {"disabled": True}}
+    assert _run_validator(cfg) == (0, "")
+    cfg = _fresh_golden()
+    cfg["lsp"] = True
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
     cfg["lsp"] = None
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
-    cfg["lsp"] = {"language-server": {}}
+    cfg["lsp"] = {}
     assert _run_validator(cfg) == (0, "")
 
 
-def test_validate_plugin_env_secret_rules():
+def test_validate_formatter_named_map():
     cfg = _fresh_golden()
-    cfg["plugin"] = [{"source": "my-plugin", "environment": {"KEY": "sk-live-abc123"}}]
+    cfg["formatter"] = {"command": ["mvn"], "extensions": [".java"]}
     code, out = _run_validator(cfg)
-    assert code == 1 and "plugin" in out and "secret" in out.lower()
+    assert code == 1 and "named map" in out
     cfg = _fresh_golden()
-    cfg["plugin"] = [{"source": "my-plugin", "environment": {"KEY": "{env:KEY}"}}]
+    cfg["formatter"] = {"spotless-java": {"command": ["mvn", "spotless:apply"],
+                                          "extensions": [".java"]}}
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
-    cfg["plugin"] = [{"source": "my-plugin"}]
+    cfg["formatter"] = False
     assert _run_validator(cfg) == (0, "")
+
+
+def test_validate_plugin_env_secret_rules():
+    cfg = _fresh_golden()
+    cfg["plugin"] = ["my-plugin"]
+    code, out = _run_validator(cfg)
+    assert code == 1 and "plugin" in out and "global-only" in out
     cfg = _fresh_golden()
-    cfg["plugin"] = [{"source": "my-plugin", "api_token": "x"}]
+    cfg["plugin"] = [{"source": "my-plugin", "environment": {"KEY": "{env:KEY}"}}]
     code, out = _run_validator(cfg)
-    assert code == 1 and "environment" in out.lower()
+    assert code == 1 and "plugin" in out
 
 
 def test_validate_invented_values_expanded():
@@ -297,15 +328,12 @@ def test_validate_invented_values_expanded():
     assert _run_validator(cfg) == (0, "")
 
 
-def test_validate_mcp_env_names_and_refs():
-    cfg = _fresh_golden()
-    first_srv = next(iter(cfg["mcp"]))
-    cfg["mcp"][first_srv]["environment"] = {"TODO_KEY": "{env:TODO_KEY}"}
-    assert _run_validator(cfg)[0] == 1
+def test_validate_mcp_rejected_global_only():
     cfg = _fresh_golden()
-    first_srv = next(iter(cfg["mcp"]))
-    cfg["mcp"][first_srv]["environment"] = {"KEY": "{env:FOO_PATH}"}
-    assert _run_validator(cfg) == (0, "")
+    cfg["mcp"] = {"srv": {"type": "local", "command": ["node", "server.js"],
+                          "environment": {"KEY": "{env:KEY}"}}}
+    code, out = _run_validator(cfg)
+    assert code == 1 and "global-only" in out
 
 
 def test_validate_partial_zac_rejected():
@@ -341,8 +369,9 @@ def test_validate_opencode_positives():
     del cfg["$schema"]
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
-    cfg["lsp"] = {"language-server": {"pyright": {"command": ["pyright"]}}}
+    cfg["lsp"] = {"pyright": {"command": ["pyright"]}}
     assert _run_validator(cfg) == (0, "")
     cfg = _fresh_golden()
-    cfg["plugin"] = [{"source": "my-plugin", "environment": {"KEY": "{env:KEY}"}}]
+    cfg["formatter"] = {"spotless-java": {"command": ["mvn", "spotless:apply"],
+                                          "extensions": [".java"]}}
     assert _run_validator(cfg) == (0, "")
```
<!-- END_GIT_DIFF -->
