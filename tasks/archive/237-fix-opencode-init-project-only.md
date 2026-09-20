# Task 237: Fix opencode-init skill to be project-only

**File:** `tasks/completed/237-fix-opencode-init-project-only.md`
**Source:** manager
**Type:** improvement
**Status:** closed

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
- Closed after Approved for closure, moved qa to completed.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3e891501e9d42305923466406593954760ed7475`
<!-- END_GIT_DIFF -->
