# Task 82: Implement Cognitive Executor Agent

**File:** `tasks/completed/82-implement-cognitive-executor-agent.md`
**Source:** manager
**Type:** feature
**Status:** closed

## Goal

Create and globally install a dedicated OpenCode **`cognitive-executor`** primary agent (plus a read-only **`cognitive-discovery`** subagent) that receives and executes the Cognitive Lead AI XML task blocks (`<opencode_implementation_task>`, `<opencode_discovery_task>`, `<opencode_combined_task>`) with the full HQ protocol hard-enforced at the permission layer — ZAC (zero autonomous commits), bash discipline, MCP-first context gathering, and the canonical lint → stage-and-inject → hand-off finalization sequence — instead of relying on the default Build agent and prompt-level instructions inside each XML task.

## Blueprint Reference

OpenCode analysis session (2026-08-08): "Introducing a custom opencode agent for the Cognitive Lead workflow" — full comparison of default Build agent vs. dedicated agent (enforcement table), based on official opencode docs (docs/opencode/agents.md, permissions.md, cli.md, skills.md, tools.md), the customize-opencode skill, and the live machine inventory of `~/.config/opencode/`.

## Manager's Notes

- **Placement:** Global `~/.config/opencode/agents/cognitive-executor.md` (NOT `.opencode/agents/` — per-project only works inside cognitive-lead-hq; XML tasks execute in arbitrary target repos).
- **ZAC hard-enforcement is the core requirement:** `git add`, `git commit`, `git push` → `deny` at the agent permission layer. `git mv tasks/*` → `allow` (kanban moves), `git mv` elsewhere → `ask`. `custom_context_commit_and_clean_task` MCP tool remains the ONLY commit path, invoked only when the task explicitly authorizes closure.
- **Bash discipline:** catch-all `"*": "ask"` with allowlist: `git status*`, `git log*`, `git diff*`, `npx prettier*`, `pytest*`, `npm test*`, `uv run *`, `ls*`, `find*`. `rm -rf*` → `ask`.
- **Prompt body (~60 lines, English):** permanent protocol — read AGENTS.md first; HALT with `⚠️ RULE VIOLATION WARNING` on conflicts; use `custom_context` MCP for context reports (never native-read dumps); load skills named in the XML; finalize via `lint_task_file` → `custom_context_stage_and_inject_diff` → exact Manager hand-off message.
- **Agent frontmatter:** `mode: primary`, `model: zen_proxy_router/deepseek-v4-flash-free`, `variant: high` (zen provider supports low/medium/high reasoning variants), `temperature: 0.1`, `steps: 100`, `description` required.
- **Global config addition:** set `"default_agent": "cognitive-executor"` in `~/.config/opencode/opencode.jsonc` so opencode starts with the executor.
- **LLM.txt bootstrap:** add a step to the global auto-setup flow (LLM.txt section list) that copies `cognitive-executor.md` + `cognitive-discovery.md` from `skill-templates/`-style source into `~/.config/opencode/agents/` so new machines auto-install them.
- **Global-write awareness:** writing to `~/.config/opencode/` is outside the project worktree — opencode will raise `external_directory` approval prompts; approve them. This is platform tooling, already precedented by LLM.txt's global install steps.
- **Keep all built-in agents intact** (Build/Plan/general/explore/scout) — the executor is additive; Build stays the fallback for ad-hoc work.
- Do NOT generate application code; this task only produces opencode agent/config markdown + JSONC edits + LLM.txt step + CHANGELOG entry.

## Local TODOs

- [x] Initial codebase exploration: confirm global dirs (`~/.config/opencode/`), existing `opencode.json`/`opencode.jsonc`, absence of `agents/` dir
- [x] Create `agents/` in repo root with `cognitive-executor.md` + `cognitive-discovery.md` source files
- [x] Write `cognitive-executor.md` (frontmatter + permission matrix + protocol body per Manager's Notes)
- [x] Write `cognitive-discovery.md` (read-only subagent using custom_context MCP)
- [x] Add `"default_agent": "cognitive-executor"` to `~/.config/opencode/opencode.jsonc`
- [x] Add global-install step for both agents to `LLM.txt` (and mirror source files into the repo for distribution)
- [x] Verify with `opencode agent list`
- [x] Update CHANGELOG.md (Parse-Then-Append, `### Added` under `[Unreleased]`)
- [x] Lint task file, stage via MCP tool

## Acceptance Criteria

- [x] `~/.config/opencode/agents/cognitive-executor.md` exists with `mode: primary` and ZAC deny rules (`git commit*`, `git add*`, `git push*` → deny)
- [x] `~/.config/opencode/agents/cognitive-discovery.md` exists as read-only subagent
- [x] `default_agent: cognitive-executor` present in global `opencode.jsonc`
- [x] `opencode agent list` shows both new agents
- [x] LLM.txt contains a bootstrap step installing both agent files globally
- [x] CHANGELOG.md has the feature entry under `[Unreleased]` → `### Added`

## Verification Evidence

- **Test command:** `ls ~/.config/opencode/agents/ && opencode agent list` and `rg -n "default_agent" ~/.config/opencode/opencode.jsonc`
- **Expected result:** both `.md` agent files listed; `cognitive-executor` present in `opencode agent list`; `default_agent` key set in jsonc
- **Actual result:** `cognitive-executor.md` + `cognitive-discovery.md` copied to `~/.config/opencode/agents/`; `opencode agent list` shows `cognitive-executor (primary)` and `cognitive-discovery (subagent)` with full permission matrices (ZAC denies `git add*`/`git commit*`/`git push*` → deny, bash catch-all `ask`); `rg` found `"default_agent": "cognitive-executor"` at `~/.config/opencode/opencode.jsonc:3`
- **Exit code:** 0 (both commands)

## Risk & Rollback

- **Risk:** Malformed agent frontmatter breaks opencode startup (config is validated strictly; unknown fields are silently routed to `options`). `default_agent` must point to a non-hidden primary agent.
- **Rollback plan:** delete `~/.config/opencode/agents/` files and remove `default_agent` key from `opencode.jsonc`; built-in agents are unaffected. If opencode fails to start, use `OPENCODE_DISABLE_PROJECT_CONFIG=1` / `OPENCODE_CONFIG` escape hatches to recover.

---

## OpenCode Execution Log & Reasoning

Implemented the Cognitive Executor Agent feature — two global OpenCode agents, `default_agent` config, LLM.txt bootstrap step, README docs, and CHANGELOG entry.

### What was done

1. **`agents/cognitive-executor.md`** (repo source) → copied to `~/.config/opencode/agents/`. Primary agent, `temperature: 0.1`, `steps: 100`. Permission layer hard-enforces: `git add*`/`git commit*`/`git push*` → **deny** (ZAC is now structurally impossible, not just prompt-instructed), bash catch-all `"*": "ask"` with allowlist (`git status/log/diff`, `git mv tasks/*`, `npx prettier`, `pytest`, `npm test`, `uv run`, `ls`, `find`), `rm -rf*` → ask, `external_directory` → ask. Body = the permanent Core Protocol: AGENTS.md first, HALT on violations, MCP-first context, skill loading, ZAC, exact finalization sequence (lint → stage_and_inject_diff → hand-off).
2. **`agents/cognitive-discovery.md`** → global. Read-only subagent (`edit: deny`, `bash: deny`) for `custom_context` MCP-based context compilation.
3. **`LLM.txt`** — new section 6.5 "Install Custom Agents Globally" (mkdir + cp both agents from the cloned repo) + 2 new checklist items in Section 10.
4. **`README.md`** — new "## Custom OpenCode Agents" section after "Global Skills Deployment" with `opencode --agent cognitive-executor` usage.
5. **`~/.config/opencode/opencode.jsonc`** — added `"default_agent": "cognitive-executor"` right after `$schema` (line 3). Note: the Orchestrator instructed `apply_patch`, but the target is outside the workspace root and apply_patch path markers are workspace-relative; used the Edit tool instead (same `edit` permission gate). The Orchestrator deliberately omitted `model`/`variant` from the frontmatter (inherit from global config default) — deviates from the Manager's Notes but is a valid orchestration choice; the executor inherits the global default model.
6. **`CHANGELOG.md`** — Parse-Then-Append: created `### Added` under `[Unreleased]` (did not exist) and appended the feature entry.

### Architectural reasoning

- **Enforcement at the permission layer beats prompt compliance.** Every prior ZAC violation (tasks 16, 78) happened because ZAC was a prompt rule. Now `git add/commit/push` are denied by the permission engine itself — the model literally cannot invoke them.
- **Ask-by-default bash** converts the strict approval loop from prose into runtime behavior: anything not explicitly allowlisted stops for the Manager's approval.
- **Global placement** (`~/.config/opencode/agents/`) means the agents load in every target product repo where the XML tasks execute — not just this HQ repo (per-project `.opencode/agents/` would not).
- **`default_agent`** makes the executor the startup agent, so the Manager no longer has to remember to switch via Tab.

### ZAC compliance

The bash phase's `git mv tasks/backlog/... tasks/in-progress/...` failed (`fatal: not under version control`, exit 128) because task file 82 was created this session and never committed. Used the repository's documented fallback (plain filesystem `mv`, per CHANGELOG 6.1.0 / task 81 precedent) — a filesystem operation, not a git command. The rename is captured by `custom_context_stage_and_inject_diff` (`git add -A`). No commits executed.

### QA fix iteration (2026-08-08, post-QA review)

1. **`agents/cognitive-executor.md`** — Core Protocol item 6 rewritten into "Finalization & Closure Sequence": staging path (`lint_task_file` → `custom_context_stage_and_inject_diff`) separated from the closure path (`git commit` STRICTLY FORBIDDEN; `custom_context_commit_and_clean_task` MCP tool is the ONLY commit path, only after explicit Manager authorization keywords). This closes the earlier ambiguity where the agent prompt did not mention the closure tool, which the commit-lifecycle rules (system-prompt `<constraints>` Commit Lifecycle Rule, ZAC) require. Synced to `~/.config/opencode/agents/cognitive-executor.md` so the live environment reflects the fix immediately.
2. **`LLM.txt`** — Section 7's global `opencode.json` bootstrap JSON now includes `"default_agent": "cognitive-executor"` right after `$schema`, so fresh machines auto-configure the executor as the default primary agent (matches the manual global config set during the initial implementation).
3. No new CHANGELOG entry — QA fix on the same unreleased feature; the existing `[Unreleased]` → `### Added` entry covers it.

Task approved for closure by the Manager. Moved to completed/.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `908011d3bd4924521a70be56cc43d9dde614a545`
<!-- END_GIT_DIFF -->
