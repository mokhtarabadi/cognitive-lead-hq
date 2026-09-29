# Task 278: Singleton docs, migration, upgrades, cross-platform units

**File:** `tasks/archive/278-singleton-docs-migration-upgrades.md`
**Source:** manager
**Type:** feature
**Status:** superseded
**Superseded-By:** `279-mcp-singleton-rollout`
**Superseded-At:** `2026-09-29`

## Goal

Everything documented and upgraded: new users set up the full system from LLM.txt, existing users migrate to singletons via memory, all docs/skills match opencode 2 schema, global installation current, service files exist for Linux/macOS/Windows.

## Manager's Notes

Manager order covering: (a) all docs updated with singleton changes; (b) research opencode 2 schema and full opencode.json, migrate skills to opencode 2; (c) upgrade global installation and memory; (d) LLM.txt = full setup for new users, memory workflow = migration path for existing users; (e) systemd units plus macOS/Windows equivalents, all documented; (f) blowsh (own repo task 10): stdio + http + sse all enabled by default and env-manageable, docs/readme/dockerfile updated. Assumptions: A1 `upgrade memory` = memory MCP server code currency + memory index rebuild + workflow doc update; A2 Windows supervision = scheduled-task XML + optional NSSM note (no systemd); macOS = launchd plists; A3 blowsh default ports: stdio fd + http 8107 + sse 8108 unless its task 10 says otherwise.

## Acceptance Criteria

- [ ] LLM.txt alone takes a new user from zero to 7/7 connected singletons
- [ ] Memory workflow migrates an existing stdio setup to singletons
- [ ] All repo docs/skills validated against opencode 2 schema (no v1 leftovers)
- [ ] Global installation (opencode, openchamber, npm deps) at latest, memory index rebuilt
- [ ] Service files for Linux (systemd), macOS (launchd), Windows (scheduled task) present + documented
- [ ] Blowsh supports stdio+http+sse env-managed with docs/readme/dockerfile updated in its task 10

## Verification Evidence

- **Test command:** rtk test opencode mcp list && ls services/
- **Expected result:** 7/7 connected; one service file per MCP per OS family; lint clean on all touched docs
- **Actual result:** _(The Hands fill this during execution)_
- **Exit code:** _(The Hands fill this during execution)_

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every multi-phase task):

- [ ] Build/Test/Lint pass with exit code 0
- [ ] `lint_task_file` passes on the active task file
- [ ] `CHANGELOG.md` updated via Parse-Then-Append
- [ ] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** doc edits contradict live state; upgrades break working setup; cross-platform files untestable here (Linux only)
- **Rollback plan:** config backups before any upgrade; docs are git-diffable, revert per file; mark macOS/Windows files untested-on-Linux in docs

## Phase 1: Research + upgrades

### Local TODOs

- [ ] Brain planning round under this task id
- [ ] Version check + upgrade global installation (opencode, openchamber, deps)
- [ ] Memory server currency + index rebuild
- [ ] Fetch opencode 2 MCP schema + full config reference

## Phase 2: Docs + skills migration

### Local TODOs

- [ ] LLM.txt full-setup path for new users
- [ ] Memory workflow migration path for existing users
- [ ] All docs/skills migrated to opencode 2 schema

## Phase 3: Cross-platform service files

### Local TODOs

- [ ] Linux systemd units (collect existing 6+blowsh into repo services/)
- [ ] macOS launchd plists + Windows scheduled-task XML, documented

## Phase 4: Blowsh transports (repo task 10)

### Local TODOs

- [ ] stdio+http+sse env-managed, on by default; docs/readme/dockerfile updated

> **Superseded:** This task was bundled into META task `279-mcp-singleton-rollout` and archived on 2026-09-29. See `tasks/qa/279-mcp-singleton-rollout.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/278-singleton-docs-migration-upgrades.md`.

## Execution Log & Reasoning

- 2026-09-29: Brain plan verdict (Architect, task 278): FINAL blueprint, 4 phases (P1 research+upgrades with live schema fetch, P2 LLM.txt + memory migration + 35 skill-templates sweep, P3 services/ systemd+launchd+WinXML, P4 blowsh triple-transport in its repo). Grounded in fed-context: 6 live units, no services/ dir, local opencode.json has no mcp section, versions 2.0.19/2.0.4. Assumptions: A1 memory upgrade = code+index+workflow; A2 Win = scheduled-task XML + NSSM note; A3 blowsh defaults http 8107/sse 8108. Brainstorm: not required. Open approval items: Q1 global upgrade go-ahead, Q2 NSSM or XML-only, Q3 blowsh checkout path/ports. Awaiting manager plan approval before Phase 1.

- 2026-09-29 Phase 1 done: live schema matches config; versions latest (no upgrades); backup 081813; memory + 36-skill sweep clean.
- 2026-09-29 Phase 2/3 done: services/ 6 systemd units + 6 launchd plists ({HOME} placeholder) + Windows XML template; docs/services.md; LLM.txt Step 7 remote + 7.5 singleton start; memory workflow migration section; 5 repo servers ported to singleton-capable pattern (py_compile 5/5, repo-vs-live identical). Lint: services.md/LLM.txt/workflow pass; task-file path warning is invocation artifact only. Verify: 7/7 connected, exactly 1 proc per MCP. Remaining: blowsh P4 SSE (other repo, task 10), CHANGELOG/history updates at close.
- 2026-09-29 Phase 1 DONE (approved): live schema fetched (opencode.ai/docs/mcp-servers, last updated Sep 28 2026 — local type/command-array/environment/timeout-5000-default + remote type/url/headers/oauth/timeout confirmed; matches our config). All versions already latest — opencode 2.0.19, openchamber 2.0.4, telegram 5960872 lag 0 — no upgrades needed. Global backup: opencode.json.bak-20260929-081813. Memory exists with index.md (namespaces: architecture, manager, manager-decisions, opencode_config, project, quirks, release, telegram-sync, workflows). Skill sweep: 36 dirs, no stale MCP shape (opencode-init already enforces V2 global-only mcp; python-skills uv-run hits are target-project lint gates, left alone). Stale inventory for Phase 2/3: LLM.txt stdio→remote rewrite, memory workflow migration path, services/ dir missing, no singleton port refs in docs.
- 2026-09-29 Phase 4 done (blowsh repo, task 10): `runSseServer()` added — `MCP_TRANSPORT=sse`, default 127.0.0.1:8108, stateful SSE on `/sse` + `/messages`; build 0, Docker smoke (stream 200, initialize accepted, all 5 tools listed), test container/image removed, README + CHANGELOG updated. Triple transport verified: stdio default + http 8107 + sse 8108.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
