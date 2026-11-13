# Task 399: Remove Freebuff, clean LLM.txt and memories, fix upgrade mechanism

**File:** `tasks/in-progress/399-remove-freebuff-clean-llm-and-memories.md`
**Source:** manager
**Type:** chore
**Status:** open

## Goal

Remove Freebuff from the machine entirely, clean every reference to it and to the non-existent `~/.agents` root out of `LLM.txt` and the project memories, and fix the OpenCode / OpenChamber upgrade mechanism so a future upgrade actually refreshes the whole global install (servers, skills, agents, prompts, plugins) instead of drifting.

## Manager's Notes

Manager ordered in English:

1. Remove `~/.agents` and everything not related to openchamber/opencode and our harness. The `.agents` dir in home is Freebuff-related and no longer needed.
2. Remove Freebuff entirely from the system.
3. Clean `LLM.txt` and the memories about it.
4. Clean the memories and enhance the global upgrade workflow.
5. Fix the OpenCode upgrade mechanism and the repo, plus OpenChamber, in `LLM.txt` and in the memories.

Autopilot locked for this task.

### Verified inventory (2026-11-13)

Freebuff footprint to remove:
- `freebuff@0.2.34` npm global package, binary `~/.local/share/mise/installs/node/lts/bin/freebuff` (symlink into the global `node_modules/freebuff`).
- `~/.config/manicode/` — 231M Freebuff vendor state: `freebuff/`, `freebuff-metadata.json`, `credentials.json`, `device-key.json`, `analytics-id.json`, `rg` binary, `projects/{freebuff2api,warp-fr,cognitive-lead-hq,mohammad}`, `message-history.json`, `tree-sitter.wasm`.
- `~/warp-fr/.freebuff/project-id` — Freebuff project marker inside the WARP egress project.
- `~/.AGENTS.md` (54K) + `~/.AGENTS.md.bak-20261024-0652-planner` — the V1-format global agent file installed from `freebuff/AGENTS.global.md` (Task 98). Stale duplicate of `~/.config/opencode/agents/cognitive-executor.md` (V2-native home, synced).

Keep (harness / OpenCode / OpenChamber):
- `~/.config/opencode/` (global install), `~/.config/openchamber/`, `~/.config/code-server/`, `~/.config/opencode-backups/`.
- `~/.opencode/` — the ACTIVE OpenCode v2.3.0 binary (`~/.opencode/bin/opencode`, `opencode2` shim) plus the global memory root. NOT Freebuff.
- `~/warp-fr/` itself — a Cloudflare WARP egress project, not Freebuff. Only its `.freebuff/` marker is removed.
- `docs/history/*` — archived history keeps Freebuff mentions; they are history, not live config.

`~/.agents` does NOT exist on this machine (verified). Its removal is therefore a removal of every REFERENCE to it: `LLM.txt` (the multi-root skill loop + the verification checklist) and the memory `opencode_config/skill-sources-multiple-roots.md`.

Stale memories to fix:
- `opencode_config/opencode_openchamber_versions_2026_11_02.md` — records OpenCode 2.2.5 / OpenChamber 2.6.0 (actual: 2.3.0 / 2.7.1) and claims "no OpenCode plugins" (actual: smart-compact + goal + todolist installed).
- `opencode_config/skill-sources-multiple-roots.md` — lists `~/.agents/skills` as a root to sync.
- `opencode_config/plugin_policy_magic_compact_2026_10_02.md` — plugin policy needs the goal + todolist entries.
- `workflows/global-install-upgrade.md` — needs the skills/agents sync scope (the drift trap found 2026-11-13) and the opencode/openchamber binary upgrade path.
- `workflows/upstream-upgrade-dep-sync.md` — needs the server→skills→agents→prompts→plugins refresh chain.

## Local TODOs

- [ ] Remove the Freebuff footprint (npm global package, `~/.config/manicode`, `~/warp-fr/.freebuff`, `~/.AGENTS.md` + backup)
- [ ] Rewrite `LLM.txt`: drop the `~/.agents` skill root, fix the skill sync loop, fix the OpenCode/OpenChamber upgrade path, add the skills/agents/prompts sync scope
- [ ] Rewrite the stale memories (versions, plugin policy, skill roots) and enhance the upgrade workflows
- [ ] Verify: 24 skills, 2 agents, 7 MCP servers, 6 stage prompts, plugins, services, tests
- [ ] Global smoke test

## Acceptance Criteria

- [x] No Freebuff binary, package, config, credential, or project marker remains on the machine
- [x] `~/.agents` no longer appears in `LLM.txt` or in any memory
- [x] `LLM.txt` skill sync loop syncs the real roots only and keeps the DECISIONS.md/README.md exclusion
- [x] `LLM.txt` upgrade path upgrades OpenCode and OpenChamber correctly and refreshes the whole global install (servers, skills, agents, prompts, plugins)
- [x] Memories record the current OpenCode/OpenChamber versions and the real plugin set
- [x] The global upgrade workflow covers servers, skills, agents, prompts, plugins, and the dependency sync
- [x] 24 skills globally, 2 agents globally, 7 MCP servers live, 6 stage prompts installed
- [x] All 7 MCP services active and the full test suite green
- [x] Nothing from the harness was lost (personas 7/1, prompt byte-identical)

## Verification Evidence

- **Test command:** rtk test uv run --with pytest pytest tests/test_hybrid_graph.py -q
- **Expected result:** 5 passed, exit 0
- **Actual result:** 5 passed in 0.06s
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_stage_prompts.py -q
- **Expected result:** 17 passed, exit 0
- **Actual result:** 17 passed in 1.66s
- **Exit code:** 0
- **Test command:** rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q
- **Expected result:** 854+ tests pass, exit 0
- **Actual result:** 854 passed, 24 warnings in 66.17s
- **Exit code:** 0
- **Test command:** bash /tmp/opencode/smoke-hq.sh
- **Expected result:** ALL CHECKS PASSED
- **Actual result:** ALL CHECKS PASSED (6 stage artifacts installed, plugin-blind, byte-stable, personas 7/1)
- **Exit code:** 0
- **Test command:** freebuff before/after inventory (npm ls -g | grep freebuff; test -e ~/.config/manicode; test -e ~/.opencode/bin/opencode; ls -1d ~/.config/opencode/skills/*/ | wc -l; ls ~/.config/opencode/agents/*.md | wc -l)
- **Expected result:** freebuff count 0 and manicode absent AFTER; opencode binary present; 24 skills; 2 agents
- **Actual result:** BEFORE → freebuff npm 1, binary present, manicode 231M, ~/.AGENTS.md 54180 bytes, ~/.agents absent. AFTER → freebuff npm 0, binary GONE, package GONE, manicode removed, warp-fr/.freebuff removed, ~/.AGENTS.md + backup removed; opencode v2.3.0 present, openchamber 2.7.1 present, 24 skill dirs, 2 agent files, 6 stage prompts + full prompt, 7 services active.
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `testing-verification` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Removing `~/.config/manicode` deletes Freebuff credentials that cannot be restored, and removing `~/.AGENTS.md` could break a consumer that still reads the V1 path.
- **Rollback plan:** the Freebuff npm package reinstalls from the registry (`npm install -g freebuff`); `~/.AGENTS.md` is reproduced by copying `~/.config/opencode/agents/cognitive-executor.md`; the repo changes are a plain git revert. The removal is verified by a before/after inventory so nothing is deleted unobserved.

---

## Execution Log & Reasoning

### Execution record (Hands)

**Brain gate could not run — provider quota, not a verdict.** The planning turn and one lean retry both returned `PROVIDER_ERROR` with `GoUsageLimitError` ("OpenCode Go usage limit reached (monthly, resets in 17d 20h)"), not a review verdict. Per the protocol that is a transport failure, so it was retried once lean and then escalated instead of being counted as a rejection. The work therefore executed from the Manager's explicit instruction, which is itself the plan (the Planning Gate accepts the Manager's quoted words). **Consequence: the QA and Code Reviewer chain could not run for this task.** The task stays in `tasks/in-progress/` and is not closed, so the next Brain turn can QA it when the quota resets.

**Why `~/.agents` needed no deletion.** It did not exist on this machine — verified before and after. The cleanup was therefore of every REFERENCE to it: `LLM.txt` (the multi-root skill loop and the verification checklist) and the memory `opencode_config/skill-sources-multiple-roots.md`, which had listed it as a root to sync. The memory now says: one writable global root, and if `~/.agents/skills` ever reappears, delete it rather than syncing it — two global roots was the drift that made OpenChamber list retired skills.

**Why `~/.AGENTS.md` went but `~/.opencode/` stayed.** `~/.AGENTS.md` (54K) was the Freebuff-era global agent file installed from `freebuff/AGENTS.global.md`; OpenCode V2 never read it (no reference in `opencode.json`) and it had drifted from the canonical agent. `~/.opencode/` is NOT Freebuff — it holds the ACTIVE OpenCode v2.3.0 binary (`~/.opencode/bin/opencode` plus the `opencode2` shim) and the global memory root. Removing it would have removed the editor itself.

**The copy-exclusion trap was live, not theoretical.** `cp -r skill-templates/*` and `cp agents/*.md` had already copied `DECISIONS.md` and `README.md` into `~/.config/opencode/skills/` and `~/.config/opencode/agents/`. OpenChamber counts those as fake skills and extra agents. They are now removed, and the deploy script removes them after every copy so it cannot recur.

**The upgrade mechanism was the real bug.** A binary upgrade (OpenCode installer / OpenChamber npm package) does not touch `~/.config/opencode/` at all — the servers, skills, agents, prompts and plugins are independent copies. That is why the harness drifted twice in one day: first skills+agents went stale, then the prompt did. `LLM.txt` §1 now carries the full chain (binaries → servers → venv deps → skills → agents → prompts → plugin cache purge → restart → drift audit), and the memories `global-install-upgrade` + `upstream-upgrade-dep-sync` carry the same chain with the two live traps recorded (copy exclusions, and "binary upgrade ≠ install upgrade").

**Stale memories corrected to reality.** The version shard claimed OpenCode 2.2.5 / OpenChamber 2.6.0 (actual: 2.3.0 / 2.7.1) and "no OpenCode plugins" (actual: smart-compact + goal + todolist installed). `no_task_for_global_upgrade` now separates a machine-local sync (no task file) from a change that also edits repo files (task file required) — this task is the latter.

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
