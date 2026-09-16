---
name: opencode-init
description: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. Matches https://opencode.ai/config.json shapes; validates before writing.
---

# Skill: opencode-init

# Project OpenCode Config Generator

## Purpose

Turn project analysis into a working `opencode.json` for THAT project only.
Analyze stack files, ask the user for gaps (default agent,
formatter, LSP guidance, instructions, permissions), emit JSON matching
the public schema (https://opencode.ai/config.json),
then validate with `scripts/validate-opencode.py` before writing.
MCP servers and plugins install GLOBALLY — never emit `mcp` or `plugin`
into the project file. Never edit global config. Never install plugins.

## Ground Truth (public schema wins — verified 2026-09-16)

- Shape: project-only top keys: `$schema`, `default_agent`,
  `instructions[]`, `formatter`, `lsp`, `permission{}`. The `permission` map is
  `tool-name → allow|ask|deny`, plus a `bash` sub-map of
  `command-pattern → deny` and optional scoped sub-maps
  (e.g. `external_directory`). There is NO `permissions[]` array here.
  `mcp{}` and `plugin[]` are GLOBAL-only and banned from project output.
- Formatter: `true` | `false` | named map
  `{<name>: {command?, extensions?, environment?, disabled?}}`.
  NEVER emit a flat `{command, extensions}` object — it fails with
  `Missing key formatter.command`. Example:
  `{"spotless-java": {"command": ["mvn", "spotless:apply"], "extensions": [".java"]}}`.
- LSP: `true` | `false` | flat map
  `{<name>: {command (required), extensions?, env?, initialization?, disabled?}}`.
  NEVER wrap in a `language-server` key — it fails with
  `Missing key lsp.language-server.command` because the runtime treats
  `language-server` as a server name. LSP uses `env`, NOT `environment`.
  Example: `{"typescript": {"command": ["typescript-language-server", "--stdio"]}}`.
- MCP server: global-only. Shared servers live in the global config
  (`~/.config/opencode/opencode.json`) or a global plugin directory —
  project output carries NO `mcp` block. Secrets travel ONLY as
  `{env:NAME}` placeholders in global scope — never literal values.
- `default_agent` must name an existing primary agent.
- Merge order: remote → global → custom → project root → subdir;
  `.opencode/*` wins. Global holds shared MCP and plugins;
  the project file holds overrides only (formatter, LSP guidance,
  instructions, permissions).
- Schema authority: https://opencode.ai/config.json plus
  `references/runtime-matrix.md`. The golden file
  (`references/examples/golden-opencode.json`) is a known-good example
  that MUST pass both this validator and `opencode debug config`.

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
3. **Generate.** Emit project-only JSON: `$schema`, `default_agent`,
   `instructions[]` (existing doc paths only), `formatter`
   (`true`|`false`|named map `{<name>: {command, extensions?, environment?, disabled?}}`),
   `lsp` (`true`|`false`|flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}`),
   `permission{}` (tool allows + full ZAC `bash` deny set).
   Omit `mcp` and `plugin` entirely; instead write a human note naming
   the global install paths (`~/.config/opencode/opencode.json`,
   `~/.config/opencode/plugins/` or `.opencode/plugins/`).
4. **Validate, then write.** Run `scripts/validate-opencode.py <file>`.
   Zero errors required before writing to the project root. On failure,
   fix and re-run — never hand over an invalid file.

## Rules

- Project-only output. `mcp` and `plugin` keys, `permissions[]`
  arrays, `language-server` LSP wrappers, flat formatter objects,
  and any key the validator rejects are forbidden.
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
