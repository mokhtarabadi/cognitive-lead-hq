# Task 428: Rebuild `.env.example` From a Project-Wide Scan

**File:** `tasks/archive/428-rebuild-env-example-from-scan.md`
**Source:** manager
**Type:** improvement
**Status:** superseded
**Superseded-By:** `432-brain-litellm-zen-bridge-cleanup`
**Superseded-At:** `2026-11-27 09:00 UTC`

## Goal

Make `.env.example` a truthful inventory of the environment keys the project actually reads. Scan
every server, service unit, script, and doc that resolves an env var, then rebuild the file so each
key is present once, grouped by owner, and annotated with its real default and effect. Remove keys
nothing reads.

## Manager's Notes

Verbatim intent:

> "cleanup .env.example by scanning project."

Scope notes:

- The scan is the source of truth, not the current file. The present `.env.example` carries stale
  model notes, duplicated `BRAIN_MODEL` blocks, duplicated `ZEN_PROXY_UPSTREAM_TIMEOUT`, and a
  zen-proxy section that will be renamed by a sibling task in the same meta.
- A key that only exists in archived docs stays out unless live code reads it.
- Do not commit a real secret; placeholders only.

## Local TODOs

- [ ] Enumerate env reads across `mcp-*/**/*.py`, `zen-proxy/`, `scripts/`, `services/`,
      `opencode.json`, and `docs/` with a literal grep for `os.environ`, `os.getenv`, `getenv(`,
      `Environment=`, and `${VAR` patterns.
- [ ] Build a key inventory: name, owner component, default in code, documented or undocumented.
- [ ] Rewrite `.env.example` grouped by owner with one section per component and no duplicate key.
- [ ] Drop keys with no live reader; list them in the Execution Log so the removal is auditable.
- [ ] Verify every key in the file resolves in live code, and every live env read appears in the file.
- [ ] Keep the file provider-agnostic where the sibling LiteLLM task will add its keys; do not
      pre-invent keys.

## Acceptance Criteria

- [ ] Every env key read by live code appears exactly once in `.env.example`.
- [ ] No key in `.env.example` lacks a live reader (Exceptions: documented future keys explicitly
      marked commented-out with a reason).
- [ ] Sections match component names as they will exist after the zen-bridge rename.
- [ ] Each key line carries a short comment naming its default and its effect.
- [ ] No secret, token, or credential value is present.

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest python -m pytest tests/test_brain_bridge.py -q`
- **Expected result:** env-parsing tests pass, and the scan diff shows zero unread keys.
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: the first verification run MUST use the `rtk test` prefix; a raw rerun is
> allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `testing-verification` applied and evidence recorded

## Risk & Rollback

- **Risk:** a key used only in production unit files or the global install gets dropped, breaking a
  service on the next restart.
- **Rollback plan:** restore the previous `.env.example` from git history; the file is
  documentation-only and carries no runtime power by itself.

---

> **Superseded:** This task was bundled into META task `432-brain-litellm-zen-bridge-cleanup` and archived on 2026-11-27 09:00 UTC. See `tasks/backlog/432-brain-litellm-zen-bridge-cleanup.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/428-rebuild-env-example-from-scan.md`.

## Execution Log & Reasoning

_(The Hands: log technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
