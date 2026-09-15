# Task 237: Fix opencode-init skill to be project-only

**File:** `tasks/qa/237-fix-opencode-init-project-only.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Make the opencode-init skill generate project-only opencode.json (formatter, LSP guidance, instructions, permissions); MCP servers and plugins install globally.

## Manager's Notes

Persian request translated: fix opencode-init skill so it only sees the project. Everything shared (MCP servers, plugins) must be installed globally. Inside the project config only project-specific items remain (formatter, LSP guidance, instructions, permissions). Evidence: skill-templates/opencode-init/SKILL.md (70 lines, V1-only, currently asks/emits MCP/secrets/agent/formatter/LSP/plugin), references/runtime-matrix.md, references/examples/golden-opencode.json, scripts/validate-opencode.py (267 lines), repo opencode.json vs global config. Official docs confirmed: config precedence remote<global<custom<project<.opencode<inline<managed; global holds providers/models/permissions, project holds overrides; MCP global vs project; plugins via npm auto-install Bun cache or .opencode/plugins vs ~/.config/opencode/plugins; formatter true/false/custom; LSP disabled by default, enable via lsp true.

## Local TODOs

- [ ] Inspect SKILL.md, runtime-matrix.md, golden-opencode.json, validate-opencode.py and repo opencode.json
- [ ] Define project-only top-level key allowlist vs global-only keys (mcp, plugin handling)
- [ ] Update SKILL.md workflow/rules to stop asking/emitting MCP servers and plugins into project config
- [ ] Sync runtime-matrix.md, golden-opencode.json, validate-opencode.py with the project-only contract
- [ ] Verify with validator and lint_task_file, update CHANGELOG.md

## Acceptance Criteria

- [x] Generated project opencode.json contains only project-specific items (formatter, LSP guidance, instructions, permissions, plus schema/agent pointer as decided)
- [x] Skill no longer emits project-level MCP servers or plugins; global install path is documented instead
- [x] SKILL.md, runtime-matrix.md, golden-opencode.json, validate-opencode.py are mutually consistent
- [x] `scripts/validate-opencode.py` passes on the golden file and rejects global-only keys in project output
- [x] `lint_task_file` passes on the active task file and CHANGELOG.md is updated

## Verification Evidence

- **Test command:** `python3 skill-templates/opencode-init/scripts/validate-opencode.py skill-templates/opencode-init/references/examples/golden-opencode.json`
- **Expected result:** exit 0 on the updated golden file; non-zero with clear error on a fixture containing mcp/plugin
- **Actual result:** golden exit 0; mcp+plugin fixture exit 1 naming both keys with global-path errors; `py_compile` OK; golden JSON parses; repo root opencode.json fails by design (pre-existing inline mcp, documented migration)
- **Exit code:** 0 (golden), 1 (negative fixture, expected)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Validator or golden drift breaks existing generated configs; global-vs-project split contradicts V1 runtime expectations elsewhere.
- **Rollback plan:** `git mv` task file back through Kanban; revert skill-templates/opencode-init files to pre-change HEAD via `git show HEAD:<path>`.

---

## Execution Log & Reasoning

- Autopilot locked for Task 237 per Manager order ("create task and on autopilot do it"). Mode: autopilot. Blocker on pause: awaiting plan approval.
- Seat Check: domains = config generation, schema/contract split → Software Architect (triggers fired: schema, contract). Skipped: Designer (no UI), Programmer (post-plan), QA/Reviewer (later stages).
- Discovery (1 round, 3 parallel subagents, read-only): all 8 target files exist; tree/read_source_files MCP tools blocked by workspace guard (logged Q1/R1); signatures report at context-reports/signatures_report_20260915_205016_dac3a78a.md.
- Brain plan verdict (Software Architect, same task_id 237): project allowlist = $schema, default_agent, instructions, formatter, lsp (guidance only), permission w/ ZAC denies; mcp + plugin banned from project output (omit on generate, reject on validate, global-install note instead). Edits: A1 SKILL.md L12-16/L20-24/L36-45/L64-66; A2 runtime-matrix.md V1 row + mcp/plugin global-only rows; A3 golden-opencode.json remove mcp/plugin, add formatter + lsp example; A4 validate-opencode.py allowlist check rejecting mcp/plugin; A5 CHANGELOG Parse-Then-Append. Verification V1-V4.
- Assumption A1: validator rejects (not warns on) mcp/plugin — stricter gate catches regressions; Manager can downgrade to warn on approval reply.
- Approved by Manager ("Approved"). Implementation A1-A4 per plan: SKILL.md purpose/Ground Truth/workflow/rules → project-only (no MCP/plugin questions or emit, global-install note, key allowlist); runtime-matrix.md V1 project row + MCP/plugin global-only rows + formatter row, LSP clarified as enable/tune; golden-opencode.json removed mcp/plugin blocks, added formatter:true + language-server LSP example, permission/ZAC intact; validate-opencode.py rejects mcp/plugin with global-path errors, keeps ZAC/invented-value/$schema gates, extends lsp env+command checks, drops SECRET_KEY_NAME dead const. CHANGELOG Parse-Then-Append under [Unreleased]. Known migration (logged as Risk): repo root opencode.json + any old project file with inline mcp now fails validation by design; HQ root file out of scope (skill generates for other projects).
- Bridge QA (same task_id 237, include_diff=true): verdict QA_PASSED — F1 allowlist identical across SKILL/matrix/validator/golden, F2 validator accepts golden + rejects mcp/plugin, F3 LSP language-server map agrees, F4 no dead refs + compile OK; R1-R2 non-blocking (root-config migration, unknown-key coverage).
- Bridge review (same task_id 237, include_diff=true): technical approval PO_REVIEW_PENDING — F1-F5 plan fidelity per file, scope clean (SECRET_KEY_NAME drop pre-declared), box-checking honest, ZAC holds, docs synced; one Low note (validator body truncated in hunk view, evidence compensates). Relayed verbatim to Manager; file held in tasks/qa/.
- Manager accept quote: "Approved for closure". Closing per relay rule (single closure XML, executed once).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 47af6fb..1e1f13a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,7 +14,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Supervised autopilot with plan approval and seat routing (Task 233):** `agents/cognitive-executor.md` gains a supervised plan-approval section (discovery feed → Brain plan → one approval pause → seat-routed implementation; Relay questions and hard blockers are the only other interrupts), a Seat Check trigger-citation line, a goal-pause carve-out for plan approval, and generous lock-word recognition. `mcp-brain-bridge/server.py` gains a 150 KB total bundle cap (truncate/skip with notes) and a text `validate_plan_verdict` checker (5 fields; cites need path:line shape). `docs/conventions.md` gains risk tiers T0/T1/T2 plus a 3-tries-then-escalate contract. `skill-templates/telegram-issue-sync/SKILL.md` folds the GitHub-preference data question into the planning turn (repo + global copies). Shipped prompt rebuilt to 9.36.0 with a Supervised Autopilot Contract bullet (authority stays in the executor file). 5 new offline bridge tests. Full suite: **350 passed**. Postfix: verdict checker uses word-bound field matching (stub text inside longer words no longer validates), bundle truncation reserves suffix length so the total never exceeds the cap, contract bullet reworded to a single plan-approval pause.
  - **Brain sessions per project, legacy global read-through (Task 234):** `mcp-brain-bridge/loop_guard.py` gains `project_sessions_root()` (explicit override → param/`BRAIN_PROJECT_ROOT`/`BRAIN_WORKSPACE_ROOT` → cwd walk-up to a `tasks/` dir → legacy global fallback) plus `legacy_sessions_root()`; `server.py` threads an optional `project_root` through `_sessions_root`, `_transcript_path`, `_fed_context_path`, `load_history`, `append_turn`, `save/load_fed_context`, and `brain_turn` — writes always land per project under `tasks/.sessions/<id>/`, while reads fall back to the legacy global dir with a loud stderr note when the per-project file is missing. HQ folders 230-233 migrated from the global store into `tasks/.sessions/` with a sha256 manifest (`/tmp/migrate-234-manifest.json`), globals kept as fallback. 4 new offline regression tests. Full suite: **354 passed**. Hotfix: no-global-write (fallback writes reroute to `cwd/tasks/.sessions` with stderr warn), package-then-plain sibling import, per-project loop-guard hashes with legacy read fallback, per-turn sessions-root stderr line, 3 more tests (T5-T7). Full suite: **357 passed**.
   - **Review-approval relay + session-history gitignore (Task 235):** `agents/cognitive-executor.md` gains a Review-approval relay rule (technical approval → verbatim relay, file stays in qa; only the exact words "Approved for closure"/"Close task" count; Hands re-calls Brain Programmer once for a single final-closure XML and executes it exactly once) plus a relay line in the Code Reviewer roster row. `prompts/fragments/06-personas.md` Code Reviewer contract now routes closure through the relayed Programmer XML instead of emitting it directly. Shipped prompt rebuilt to 9.37.0. Global `audit-agents` skill Plugin Runtime-State rule now covers Brain session history (`tasks/.sessions/` added only after confirming the dir exists). Hotfix: relay tightened (bare-approved counts only as the next message answering the relayed question; explicit never-list incl. yes/done/okay/looks-good/emoji/silence; qa + PO_REVIEW_PENDING double-gate; single issuance with failure-only re-call; autopilot self-decision never satisfies); repo `skill-templates/audit-agents/SKILL.md` template extended too (both occurrences) so the rule ships in-repo. Second hotfix: reviewer contract mirrors the executor relay exactly (bare-approved exception + full never-list incl. okay/done/fine/looks-good/emoji-only + autopilot bar), audit clause gains a duplicate-line guard (check first, add only if missing), shipped prompt rebuilt to 9.37.2.
- - **Lean-retry state note + migrate Task 234 session (Task 236):** `mcp-brain-bridge/server.py` `_empty_output_hint` and the executor Empty-output clause gain a state-freshness sentence: a lean retry drops the bundle, so if the answer judges stale or missing context, re-run ONCE with the full bundle plus diff before escalating (proven by the 235 turn-3 stale verdict). Task 234's global transcript + fed context migrated into `tasks/.sessions/234/` with sha256-verified manifest. 4 new regression assertions (stale sentence, state line, 2 unknown fallbacks). Full suite: **357 passed**.
+  - **Lean-retry state note + migrate Task 234 session (Task 236):** `mcp-brain-bridge/server.py` `_empty_output_hint` and the executor Empty-output clause gain a state-freshness sentence: a lean retry drops the bundle, so if the answer judges stale or missing context, re-run ONCE with the full bundle plus diff before escalating (proven by the 235 turn-3 stale verdict). Task 234's global transcript + fed context migrated into `tasks/.sessions/234/` with sha256-verified manifest. 4 new regression assertions (stale sentence, state line, 2 unknown fallbacks). Full suite: **357 passed**.
+ - **opencode-init project-only contract (Task 237):** `skill-templates/opencode-init/` now generates project-only `opencode.json` — allowlist `$schema`, `default_agent`, `instructions`, `formatter`, `lsp` (guidance only), `permission` (ZAC denies intact); `mcp` and `plugin` are global-only (install in `~/.config/opencode/opencode.json` or a plugins dir) and are omitted on generate, rejected on validate. SKILL.md stops asking for MCP env keys/plugin choice and writes a global-install note instead; `references/runtime-matrix.md` V1 row + MCP/plugin global-only rows + formatter row; `references/examples/golden-opencode.json` drops `mcp`/`plugin`, adds `formatter: true` + `language-server` LSP example; `scripts/validate-opencode.py` rejects `mcp`/`plugin` with global-path errors, keeps ZAC/invented-value/`$schema` gates, and extends `lsp` checks (`{env:}`-only env, invented-command rejection). Validator: exit 0 on golden, exit 1 naming both keys on an mcp+plugin fixture. Known migration: pre-existing project files with inline `mcp` (incl. this repo's root `opencode.json`) now fail validation by design.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/skill-templates/opencode-init/SKILL.md b/skill-templates/opencode-init/SKILL.md
index fde5407..eae74d9 100644
--- a/skill-templates/opencode-init/SKILL.md
+++ b/skill-templates/opencode-init/SKILL.md
@@ -10,23 +10,30 @@ description: Analyze a project (or ask the user) and generate a comprehensive, c
 ## Purpose
 
 Turn project analysis into a working `opencode.json` for THAT project only.
-Analyze stack files, ask the user for gaps (MCP servers, secrets, default
-agent, formatter, LSP), emit V1-runtime JSON, then validate with
-`scripts/validate-opencode.py` before writing. Never edit global config.
-Never install plugins.
+Analyze stack files, ask the user for gaps (default agent,
+formatter, LSP guidance, instructions, permissions), emit V1-runtime JSON,
+then validate with `scripts/validate-opencode.py` before writing.
+MCP servers and plugins install GLOBALLY — never emit `mcp` or `plugin`
+into the project file. Never edit global config. Never install plugins.
 
 ## Ground Truth (this repo's runtime — file evidence wins over public docs)
 
-- Shape: flat V1 map. Top keys: `$schema`, `default_agent`, `instructions[]`,
-  `plugin[]`, `mcp{}`, `permission{}`. The `permission` map is
+- Shape: flat V1 map. Project-only top keys: `$schema`, `default_agent`,
+  `instructions[]`, `formatter`, `lsp` (guidance only — enable/tune,
+  never install), `permission{}`. The `permission` map is
   `tool-name → allow|ask|deny`, plus a `bash` sub-map of
   `command-pattern → deny` and optional scoped sub-maps
   (e.g. `external_directory`). There is NO `permissions[]` array here.
-- MCP server: `{type: local, command: [...], enabled: bool, timeout: ms,
-  environment?: {KEY: "{env:KEY}"}}`. Secrets travel ONLY as `{env:NAME}`
-  placeholders — never literal values.
+  `mcp{}` and `plugin[]` are GLOBAL-only and banned from project output.
+- MCP server: global-only. Shared servers live in the global config
+  (`~/.config/opencode/opencode.json`) or a global plugin directory —
+  project output carries NO `mcp` block. Secrets travel ONLY as
+  `{env:NAME}` placeholders in global scope — never literal values.
 - `default_agent` must name an existing primary agent.
-- Merge order: global → project root → subdir; `.opencode/*` wins.
+- Merge order: remote → global → custom → project root → subdir;
+  `.opencode/*` wins. Global holds shared MCP and plugins;
+  the project file holds overrides only (formatter, LSP guidance,
+  instructions, permissions).
 - The public schema reference leans V2 and mismatches this runtime —
   see `references/runtime-matrix.md`. When file and docs disagree, the
   local `opencode.json` (copied at `references/examples/golden-opencode.json`) wins.
@@ -35,32 +42,41 @@ Never install plugins.
 
 1. **Analyze.** Read the target project: package manifests, README, stack
    files, existing `opencode.json`/`AGENTS.md`/`.opencode/`. Record: stack,
-   agents dir, MCP needs, formatter, LSP servers, plugin needs.
-2. **Ask user for gaps.** Missing MCP env keys, `default_agent` choice,
-   formatter/LSP choices. Ask with explicit questions; ambiguous means
-   NOT answered — HALT and re-ask rather than inventing values.
-3. **Generate.** Emit V1 JSON only: `$schema`, `default_agent`,
-   `instructions[]` (existing doc paths only), `plugin[]` (declared only,
-   never installed), `mcp{}` (local entries with `{env:}` secrets),
+   agents dir, formatter needs, LSP guidance needs, instructions paths,
+   permission needs. Do NOT record MCP needs or plugin choices —
+   those are global scope, out of this skill's output.
+2. **Ask user for gaps.** Missing `default_agent` choice, formatter/LSP/
+   instructions/permission choices. Ask with explicit questions;
+   ambiguous means NOT answered — HALT and re-ask rather than
+   inventing values. Never ask for MCP env keys or plugin selection.
+3. **Generate.** Emit V1 project-only JSON: `$schema`, `default_agent`,
+   `instructions[]` (existing doc paths only), `formatter`
+   (`true`|`false`|custom command), `lsp` (guidance only),
    `permission{}` (tool allows + full ZAC `bash` deny set).
+   Omit `mcp` and `plugin` entirely; instead write a human note naming
+   the global install paths (`~/.config/opencode/opencode.json`,
+   `~/.config/opencode/plugins/` or `.opencode/plugins/`).
 4. **Validate, then write.** Run `scripts/validate-opencode.py <file>`.
    Zero errors required before writing to the project root. On failure,
    fix and re-run — never hand over an invalid file.
 
 ## Rules
 
-- V1 output only. `permissions[]` arrays, V2 LSP objects, and any key the
-  validator rejects are forbidden.
+- V1 project-only output. `mcp` and `plugin` keys, `permissions[]`
+  arrays, V2 LSP objects, and any key the validator rejects are forbidden.
+- Project key allowlist: `$schema`, `default_agent`, `instructions`,
+  `formatter`, `lsp`, `permission`. Output keys MUST subset this list.
 - ZAC deny set is mandatory in every generated file: `git add`, `git add *`,
   `git checkout`, `git checkout *`, `git commit`, `git commit *`, `git push`,
   `git push *` → `deny`.
 - Secrets are `{env:NAME}` placeholders. A literal secret fails validation.
 - No invented values. TODO, changeme, xxx, your-value-here, foo, bar,
   dummy, placeholder (any case) and standalone "example"/"sample" fail
-  validation in `default_agent`, MCP commands and env names, plugin
-  sources, `instructions`, `formatter`, `agents_dir`, `theme`, `keybinds`
-  — confirm every name against the project first. `{env:NAME}`
-  references are never inventions.
+  validation in `default_agent`, `instructions`, `formatter`, `lsp`,
+  `agents_dir`, `theme`, `keybinds`
+  — confirm every name against the project first. MCP server names,
+  commands, env names, and plugin sources are global scope: they MUST
+  NOT appear in project output at all (neither real nor placeholder).
 - Write ONLY to the target project's root `opencode.json`. Parent
   traversal (`..`), the home directory, and any global config path are
   forbidden as write destinations.
diff --git a/skill-templates/opencode-init/references/examples/golden-opencode.json b/skill-templates/opencode-init/references/examples/golden-opencode.json
index fadb637..a7f2c36 100644
--- a/skill-templates/opencode-init/references/examples/golden-opencode.json
+++ b/skill-templates/opencode-init/references/examples/golden-opencode.json
@@ -4,81 +4,11 @@
   "instructions": [
     "docs/opencode-shell-strategy.md"
   ],
-  "plugin": [
-    "@prevalentware/opencode-goal-plugin",
-    "@tarquinen/opencode-dcp@latest"
-  ],
-  "mcp": {
-    "custom_context": {
-      "type": "local",
-      "command": [
-        "uv",
-        "run",
-        "--project",
-        "mcp-context-server",
-        "mcp-context-server/server.py"
-      ],
-      "enabled": true,
-      "timeout": 15000
-    },
-    "project_memory": {
-      "type": "local",
-      "command": [
-        "uv",
-        "run",
-        "--project",
-        "mcp-memory-server",
-        "mcp-memory-server/server.py"
-      ],
-      "enabled": true,
-      "timeout": 15000
-    },
-    "lint": {
-      "type": "local",
-      "command": [
-        "uv",
-        "run",
-        "--project",
-        "mcp-lint-server",
-        "mcp-lint-server/server.py"
-      ],
-      "enabled": true,
-      "timeout": 15000
-    },
-    "brain": {
-      "type": "local",
-      "command": [
-        "uv",
-        "run",
-        "--project",
-        "mcp-brain-bridge",
-        "mcp-brain-bridge/server.py"
-      ],
-      "enabled": true,
-      "timeout": 600000,
-      "environment": {
-        "BRAIN_API_BASE": "{env:BRAIN_API_BASE}",
-        "BRAIN_API_KEY": "{env:BRAIN_API_KEY}",
-        "BRAIN_MODEL": "{env:BRAIN_MODEL}"
-      }
-    },
-    "manager_decisions": {
-      "type": "local",
-      "command": [
-        "uv",
-        "run",
-        "--project",
-        "mcp-decision-server",
-        "mcp-decision-server/server.py"
-      ],
-      "enabled": true,
-      "timeout": 600000,
-      "environment": {
-        "BRAIN_API_BASE": "{env:BRAIN_API_BASE}",
-        "BRAIN_API_KEY": "{env:BRAIN_API_KEY}",
-        "BRAIN_MODEL": "{env:BRAIN_MODEL}",
-        "DECISION_MODEL": "{env:DECISION_MODEL}",
-        "DECISION_TEMPERATURE": "{env:DECISION_TEMPERATURE}"
+  "formatter": true,
+  "lsp": {
+    "language-server": {
+      "typescript": {
+        "command": ["typescript-language-server", "--stdio"]
       }
     }
   },
diff --git a/skill-templates/opencode-init/references/runtime-matrix.md b/skill-templates/opencode-init/references/runtime-matrix.md
index 176007a..f818a2c 100644
--- a/skill-templates/opencode-init/references/runtime-matrix.md
+++ b/skill-templates/opencode-init/references/runtime-matrix.md
@@ -2,13 +2,15 @@
 
 | Area | V1 — EMIT THIS | V2 — REJECT |
 | ---- | -------------- | ----------- |
-| Top level | `$schema`, `default_agent`, `instructions[]`, `plugin[]`, `mcp{}`, `permission{}` | `permissions[]` array |
+| Top level (project) | `$schema`, `default_agent`, `instructions[]`, `formatter`, `lsp`, `permission{}` | `permissions[]` array; `mcp{}` and `plugin[]` (global-only) |
 | Permission entries | `"tool-name": "allow\|ask\|deny"` flat map | `{permission: ..., pattern: ...}` objects |
 | Bash rules | `permission.bash = {"git commit": "deny", ...}` string map | Structured rule objects |
-| MCP local | `{type: local, command: [...], enabled, timeout, environment?}` | Remote-first / auth-object forms |
-| LSP | `language-server: {name: {command}}` map (experimental, env-gated) | `enabled` + per-extension bool/object |
-| Secrets | `"{env:NAME}"` placeholders only | Literal values (validator fails these) |
-| Plugin env | dict `environment` with `{env:}` values only | Literal values (validator fails these) |
+| MCP | GLOBAL-ONLY — install in `~/.config/opencode/opencode.json`; banned from project output | Any `mcp{}` block in a generated project file |
+| Plugin | GLOBAL-ONLY — npm spec in global config or `.opencode/plugins/` / `~/.config/opencode/plugins/`; banned from project output | Any `plugin[]` list in a generated project file |
+| LSP (project guidance) | `language-server: {name: {command}}` map — enable/tune per project; server install stays host/global side | `enabled` + per-extension bool/object |
+| Formatter (project) | `true` (all built-ins) \| `false` (disable) \| custom `{command, extensions}` map | — |
+| Secrets (global scope) | `"{env:NAME}"` placeholders only — project output carries no secret-bearing blocks | Literal values (validator fails these) |
+| Plugin env (global scope) | dict `environment` with `{env:}` values only | Literal values (validator fails these) |
 
 Rule: when the public schema and the local golden file disagree, the golden
 file (`references/examples/golden-opencode.json`) wins. The validator
diff --git a/skill-templates/opencode-init/scripts/validate-opencode.py b/skill-templates/opencode-init/scripts/validate-opencode.py
index a265747..1142fa5 100644
--- a/skill-templates/opencode-init/scripts/validate-opencode.py
+++ b/skill-templates/opencode-init/scripts/validate-opencode.py
@@ -1,24 +1,29 @@
-"""Validate a generated opencode.json against the V1 runtime contract.
+"""Validate a generated opencode.json against the V1 PROJECT-ONLY contract.
 
 Usage: python3 validate-opencode.py <path-to-opencode.json>
 Exit 0 = valid. Exit 1 = errors printed, one per line.
 
+Project allowlist: $schema, default_agent, instructions, formatter,
+lsp (guidance only), permission. `mcp` and `plugin` are GLOBAL-ONLY
+(installed in ~/.config/opencode/opencode.json or a plugins directory)
+and are REJECTED in project output.
+
 Checks (stdlib only):
   1. File parses as JSON (rejects trailing commas, bad types).
-  2. Top-level shape: default_agent non-empty; mcp/permission objects.
+  2. Top-level shape: default_agent non-empty; permission object present.
   3. V1 permission form: flat string map; V2 `permissions[]` array rejected.
   4. ZAC bash deny set present (all 8 patterns must be "deny").
-  5. Each MCP server: type/command/enabled/timeout present, correct types.
-  6. No literal secrets: any environment value not starting with "{env:"
-     fails (secrets travel as placeholders only).
+  5. Project-only keys: `mcp` and `plugin` keys rejected with a
+     global-path error (shared servers/plugins belong in global config).
+  6. No literal secrets: any `lsp language-server` environment value not
+     starting with "{env:" fails (secrets travel as placeholders only).
   7. LSP is V1-only: a `language-server` map of {name: {command: [...]}};
      V2 `enabled`/`extensions` keys and unknown lsp keys are rejected.
-  8. Plugin entries are strings or dicts; dict environments obey the same
-     {env:} + literal-secret rule as MCP environments.
+  8. Plugin entries forbidden: any `plugin` key fails (global-only).
   9. No invented values: TODO/changeme/xxx/your-value-here/foo/bar/dummy/
      placeholder (any case) and standalone "example"/"sample" are
-     rejected in default_agent, MCP commands and env names, plugin
-     sources, instructions, formatter, agents_dir, theme, keybinds.
+     rejected in default_agent, instructions, formatter, lsp commands,
+     agents_dir, theme, keybinds.
      "{env:}" references are never treated as invented.
   10. Optional `$schema` must be a string when present.
 """
@@ -44,12 +49,6 @@ SECRET_LIKE = re.compile(
     r"(sk-|ghp_|gho_|AIza|xox|-----BEGIN |^[A-Za-z0-9+/]{32,}={0,2}$)"
 )
 
-# Secret-like KEY names. An env-less plugin entry naming one of these has
-# nowhere safe to store the value, so it must declare an environment.
-SECRET_KEY_NAME = re.compile(
-    r"(token|password|passwd|secret|api[-_]?key|auth)", re.IGNORECASE
-)
-
 # Invented-value markers. Bare substrings are unambiguous placeholders;
 # "example"/"sample" need a word edge so only standalone words trip them
 # ("examples", "samples", "sampling", "exemplary" pass; hyphenated
@@ -118,38 +117,11 @@ def validate(cfg: dict) -> list[str]:
             for pattern in ZAC_DENIES:
                 if bash.get(pattern) != "deny":
                     errors.append(f"permission.bash[{pattern!r}] must be 'deny'")
-    mcp = cfg.get("mcp")
-    if not isinstance(mcp, dict):
-        errors.append("mcp must be an object of server entries")
-    else:
-        for name, srv in mcp.items():
-            if not isinstance(srv, dict):
-                errors.append(f"mcp[{name}] must be an object")
-                continue
-            for key, typ in (("type", str), ("command", list), ("enabled", bool), ("timeout", int)):
-                if not isinstance(srv.get(key), typ):
-                    errors.append(f"mcp[{name}].{key} must be {typ.__name__}")
-            if _has_placeholder(*srv.get("command", [])):
-                errors.append(
-                    f"mcp[{name}].command looks invented; use real paths/commands"
-                )
-            env = srv.get("environment", {})
-            if not isinstance(env, dict):
-                errors.append(f"mcp[{name}].environment must be an object")
-                continue
-            for var, val in env.items():
-                if not isinstance(val, str) or not val.startswith("{env:"):
-                    errors.append(
-                        f"mcp[{name}].environment[{var}] must be an '{{env:}}' placeholder"
-                    )
-                if _has_placeholder(var):
-                    errors.append(
-                        f"mcp[{name}].environment var name looks invented"
-                    )
-                if isinstance(val, str) and SECRET_LIKE.search(val):
-                    errors.append(
-                        f"mcp[{name}].environment[{var}] looks like a literal secret"
-                    )
+    if "mcp" in cfg:
+        errors.append(
+            "mcp is global-only (install in ~/.config/opencode/opencode.json); "
+            "remove it from project output"
+        )
     invented_scope = {
         "instructions": cfg.get("instructions"),
         "formatter": cfg.get("formatter"),
@@ -171,53 +143,11 @@ def validate(cfg: dict) -> list[str]:
             errors.append(
                 f"{field} looks invented; use project-declared values"
             )
-    plugins = cfg.get("plugin")
-    if plugins is not None:
-        if not isinstance(plugins, list):
-            errors.append("plugin must be a list of entries")
-        else:
-            for entry in plugins:
-                if isinstance(entry, str):
-                    if _has_placeholder(entry):
-                        errors.append(
-                            "plugin entry looks invented; use a declared plugin"
-                        )
-                    continue
-                if not isinstance(entry, dict):
-                    errors.append("plugin entries must be strings or objects")
-                    continue
-                if _has_placeholder(entry.get("source"), entry.get("command")):
-                    errors.append(
-                        "plugin entry looks invented; use a declared plugin"
-                    )
-                if "environment" not in entry:
-                    # Env-less entries are fine unless they name secret-like
-                    # keys with nowhere safe to store the value.
-                    for key in entry:
-                        if isinstance(key, str) and SECRET_KEY_NAME.search(key):
-                            errors.append(
-                                "plugin entry names a secret-like key without "
-                                "environment; use an {env:} placeholder"
-                            )
-                            break
-                    continue
-                env = entry.get("environment")
-                if not isinstance(env, dict):
-                    errors.append("plugin environment must be an object")
-                    continue
-                for var, val in env.items():
-                    if not isinstance(val, str) or not val.startswith("{env:"):
-                        errors.append(
-                            f"plugin.environment[{var}] must be an '{{env:}}' placeholder"
-                        )
-                    if _has_placeholder(var):
-                        errors.append(
-                            "plugin.environment var name looks invented"
-                        )
-                    if isinstance(val, str) and SECRET_LIKE.search(val):
-                        errors.append(
-                            f"plugin.environment[{var}] looks like a literal secret"
-                        )
+    if "plugin" in cfg:
+        errors.append(
+            "plugin is global-only (declare in ~/.config/opencode/opencode.json "
+            "or a plugins directory); remove it from project output"
+        )
     lsp = cfg.get("lsp")
     if lsp is not None:
         if not isinstance(lsp, dict):
@@ -244,6 +174,25 @@ def validate(cfg: dict) -> list[str]:
                         errors.append(
                             f"lsp language-server[{srv_name}] needs a non-empty command list"
                         )
+                    elif _has_placeholder(*cmd):
+                        errors.append(
+                            f"lsp language-server[{srv_name}].command looks invented"
+                        )
+                    env = srv_spec.get("environment", {})
+                    if not isinstance(env, dict):
+                        errors.append(
+                            f"lsp language-server[{srv_name}].environment must be an object"
+                        )
+                    else:
+                        for var, val in env.items():
+                            if not isinstance(val, str) or not val.startswith("{env:"):
+                                errors.append(
+                                    f"lsp language-server[{srv_name}].environment[{var}] must be an '{{env:}}' placeholder"
+                                )
+                            if isinstance(val, str) and SECRET_LIKE.search(val):
+                                errors.append(
+                                    f"lsp language-server[{srv_name}].environment[{var}] looks like a literal secret"
+                                )
     return errors
```
<!-- END_GIT_DIFF -->
