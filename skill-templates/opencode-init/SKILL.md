---
name: opencode-init
description: Analyze a project (or ask the user) and generate a comprehensive, correct opencode.json for it. V1 runtime shapes only; validates before writing.
---

# Skill: opencode-init

# Project OpenCode Config Generator

## Purpose

Turn project analysis into a working `opencode.json` for THAT project only.
Analyze stack files, ask the user for gaps (MCP servers, secrets, default
agent, formatter, LSP), emit V1-runtime JSON, then validate with
`scripts/validate-opencode.py` before writing. Never edit global config.
Never install plugins.

## Ground Truth (this repo's runtime — file evidence wins over public docs)

- Shape: flat V1 map. Top keys: `$schema`, `default_agent`, `instructions[]`,
  `plugin[]`, `mcp{}`, `permission{}`. The `permission` map is
  `tool-name → allow|ask|deny`, plus a `bash` sub-map of
  `command-pattern → deny` and optional scoped sub-maps
  (e.g. `external_directory`). There is NO `permissions[]` array here.
- MCP server: `{type: local, command: [...], enabled: bool, timeout: ms,
  environment?: {KEY: "{env:KEY}"}}`. Secrets travel ONLY as `{env:NAME}`
  placeholders — never literal values.
- `default_agent` must name an existing primary agent.
- Merge order: global → project root → subdir; `.opencode/*` wins.
- The public schema reference leans V2 and mismatches this runtime —
  see `references/runtime-matrix.md`. When file and docs disagree, the
  local `opencode.json` (copied at `references/examples/golden-opencode.json`) wins.

## Workflow

1. **Analyze.** Read the target project: package manifests, README, stack
   files, existing `opencode.json`/`AGENTS.md`/`.opencode/`. Record: stack,
   agents dir, MCP needs, formatter, LSP servers, plugin needs.
2. **Ask user for gaps.** Missing MCP env keys, `default_agent` choice,
   formatter/LSP choices. Ask with explicit questions; ambiguous means
   NOT answered — HALT and re-ask rather than inventing values.
3. **Generate.** Emit V1 JSON only: `$schema`, `default_agent`,
   `instructions[]` (existing doc paths only), `plugin[]` (declared only,
   never installed), `mcp{}` (local entries with `{env:}` secrets),
   `permission{}` (tool allows + full ZAC `bash` deny set).
4. **Validate, then write.** Run `scripts/validate-opencode.py <file>`.
   Zero errors required before writing to the project root. On failure,
   fix and re-run — never hand over an invalid file.

## Rules

- V1 output only. `permissions[]` arrays, V2 LSP objects, and any key the
  validator rejects are forbidden.
- ZAC deny set is mandatory in every generated file: `git add`, `git add *`,
  `git checkout`, `git checkout *`, `git commit`, `git commit *`, `git push`,
  `git push *` → `deny`.
- Secrets are `{env:NAME}` placeholders. A literal secret fails validation.
- No invented values. TODO, changeme, xxx, your-value-here, foo, bar,
  dummy, placeholder (any case) and standalone "example"/"sample" fail
  validation in `default_agent`, MCP commands and env names, plugin
  sources, `instructions`, `formatter`, `agents_dir`, `theme`, `keybinds`
  — confirm every name against the project first. `{env:NAME}`
  references are never inventions.
- Write ONLY to the target project's root `opencode.json`. Parent
  traversal (`..`), the home directory, and any global config path are
  forbidden as write destinations.
- Verify before generating: list the `agents_dir` files and confirm the
  chosen `default_agent` name exists there. A name with no file is an
  invention — ask the user instead.
- One project per run. Never touch global config. Never `git commit` the result.
