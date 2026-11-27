# Task 430: Remove warp-proxy and psiphon-proxy Projects and All References

**File:** `tasks/backlog/430-remove-warp-and-psiphon-proxies.md`
**Source:** manager
**Type:** improvement
**Status:** backlog

## Goal

Delete the `warp-proxy/` and `psiphon-proxy/` build contexts and every live reference to them. blowsh
keeps optional proxy support, but it reads proxy settings from plain environment variables instead of
one named container backend. Documentation that only taught WARP or Psiphon is archived as history,
not kept as a current guide.

## Manager's Notes

Verbatim intent:

> "remove warp and psiphone projects and all of them refreneces in our project, blowsh support proxy
> but not need to use warp or phsionon"

Scope notes:

- Verified live references today: `warp-proxy/`, `psiphon-proxy/`, `docs/blowsh-warp-proxy.md`,
  `docs/blowsh-psiphon-proxy.md`, `docs/blowsh-proxy-options.md`, `docs/blowsh-direct-egress.md`,
  `docs/README.md`, `docs/DECISIONS.md`, `README.md`, plus memory records under
  `.opencode/memory/`.
- blowsh keeps `PROXY_TYPE` / `PROXY_HOST` / `PROXY_PORT` / `PROXY_BYPASS` support; drop only the
  container names and build contexts.
- History under `docs/history/` and completed/archived tasks is a record and must not be edited.

## Local TODOs

- [ ] Confirm no live service unit, compose file, or script depends on either proxy directory.
- [ ] Move `warp-proxy/` and `psiphon-proxy/` to an archive location with `git mv` (history stays
      reachable), or delete only after confirming nothing references them.
- [ ] Rewrite `docs/blowsh-proxy-options.md` as a generic env-driven proxy guide with no named
      backend.
- [ ] Retire `docs/blowsh-warp-proxy.md` and `docs/blowsh-psiphon-proxy.md` into history, with dated
      ADRs in `docs/DECISIONS.md` and the affected slice `DECISIONS.md`.
- [ ] Sweep live references with `$code-search` and plain grep for `warp`, `psiphon`, `socks`; fix
      each live hit.
- [ ] Refresh the memory records that named either backend.
- [ ] Break any compose or service definition that names `warp-net` / `psiphon-socks`.

## Acceptance Criteria

- [ ] Neither `warp-proxy/` nor `psiphon-proxy/` exists in the live tree; history is preserved.
- [ ] No live file (excluding `docs/history/`, `tasks/archive/`, `tasks/completed/`, and session
      transcripts) mentions WARP or Psiphon.
- [ ] blowsh proxy support is documented as env-only and still works with a generic proxy.
- [ ] Dated ADRs record the removal and the reason.
- [ ] No service unit or compose file references the removed containers.

## Verification Evidence

- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 python -m pytest tests/ -q`
- **Expected result:** the full suite passes, exit code 0; grep for the removed names returns only
  history and archive paths.
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

- **Risk:** a running blowsh container or the operator's current deployment still points at one of
  the removed containers, so egress stops after the cleanup lands.
- **Rollback plan:** restore the directories from git history and re-apply the previous container
  configuration; the build contexts are self-contained.

---

## Execution Log & Reasoning

_(The Hands: log technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
