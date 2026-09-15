---
name: opencode-init
description: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. V1 runtime shapes only; validates before writing.
---

# Skill: opencode-init

# Project OpenCode Config Generator

## Purpose

Turn project analysis into a working `opencode.json` for THAT project only.
Analyze stack files, ask the user for gaps (default agent,
formatter, LSP guidance, instructions, permissions), emit V1-runtime JSON,
then validate with `scripts/validate-opencode.py` before writing.
MCP servers and plugins install GLOBALLY — never emit `mcp` or `plugin`
into the project file. Never edit global config. Never install plugins.

## Ground Truth (this repo's runtime — file evidence wins over public docs)

- Shape: flat V1 map. Project-only top keys: `$schema`, `default_agent`,
  `instructions[]`, `formatter`, `lsp` (guidance only — enable/tune,
  never install), `permission{}`. The `permission` map is
  `tool-name → allow|ask|deny`, plus a `bash` sub-map of
  `command-pattern → deny` and optional scoped sub-maps
  (e.g. `external_directory`). There is NO `permissions[]` array here.
  `mcp{}` and `plugin[]` are GLOBAL-only and banned from project output.
- MCP server: global-only. Shared servers live in the global config
  (`~/.config/opencode/opencode.json`) or a global plugin directory —
  project output carries NO `mcp` block. Secrets travel ONLY as
  `{env:NAME}` placeholders in global scope — never literal values.
- `default_agent` must name an existing primary agent.
- Merge order: remote → global → custom → project root → subdir;
  `.opencode/*` wins. Global holds shared MCP and plugins;
  the project file holds overrides only (formatter, LSP guidance,
  instructions, permissions).
- The public schema reference leans V2 and mismatches this runtime —
  see `references/runtime-matrix.md`. When file and docs disagree, the
  local `opencode.json` (copied at `references/examples/golden-opencode.json`) wins.

## Workflow

1. **Analyze.** Read the target project: package manifests, README, stack
   files, existing `opencode.json`/`AGENTS.md`/`.opencode/`. Record: stack,
   agents dir, formatter needs, LSP guidance needs, instructions paths,
   permission needs. Do NOT record MCP needs or plugin choices —
   those are global scope, out of this skill's output.
2. **Ask user for gaps.** Missing `default_agent` choice, formatter/LSP/
   instructions/permission choices. Ask with explicit questions;
   ambiguous means NOT answered — HALT and re-ask rather than
   inventing values. Never ask for MCP env keys or plugin selection.
3. **Generate.** Emit V1 project-only JSON: `$schema`, `default_agent`,
   `instructions[]` (existing doc paths only), `formatter`
   (`true`|`false`|custom command), `lsp` (guidance only),
   `permission{}` (tool allows + full ZAC `bash` deny set).
   Omit `mcp` and `plugin` entirely; instead write a human note naming
   the global install paths (`~/.config/opencode/opencode.json`,
   `~/.config/opencode/plugins/` or `.opencode/plugins/`).
4. **Validate, then write.** Run `scripts/validate-opencode.py <file>`.
   Zero errors required before writing to the project root. On failure,
   fix and re-run — never hand over an invalid file.

## Rules

- V1 project-only output. `mcp` and `plugin` keys, `permissions[]`
  arrays, V2 LSP objects, and any key the validator rejects are forbidden.
- Project key allowlist: `$schema`, `default_agent`, `instructions`,
  `formatter`, `lsp`, `permission`. Output keys MUST subset this list.
- ZAC deny set is mandatory in every generated file: `git add`, `git add *`,
  `git checkout`, `git checkout *`, `git commit`, `git commit *`, `git push`,
  `git push *` → `deny`.
- Secrets are `{env:NAME}` placeholders. A literal secret fails validation.
- No invented values. TODO, changeme, xxx, your-value-here, foo, bar,
  dummy, placeholder (any case) and standalone "example"/"sample" fail
  validation in `default_agent`, `instructions`, `formatter`, `lsp`,
  `agents_dir`, `theme`, `keybinds`
  — confirm every name against the project first. MCP server names,
  commands, env names, and plugin sources are global scope: they MUST
  NOT appear in project output at all (neither real nor placeholder).
- Write ONLY to the target project's root `opencode.json`. Parent
  traversal (`..`), the home directory, and any global config path are
  forbidden as write destinations.
- Verify before generating: list the `agents_dir` files and confirm the
  chosen `default_agent` name exists there. A name with no file is an
  invention — ask the user instead.
- One project per run. Never touch global config. Never `git commit` the result.
