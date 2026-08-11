# Task 83: Update Cognitive Executor Bash Autonomy

**File:** `tasks/completed/83-update-cognitive-executor-bash-autonomy.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed

## Source Context

### Variant A: Orchestrator (`**Source:** orchestrator`)

## Goal

Replace the `cognitive-executor` agent's granular bash allowlist (`"*": "ask"` + allowlisted commands) with a full-autonomy catch-all (`"*": "allow"`) while preserving the two non-negotiable safety guards: ZAC denies (`git add*`, `git commit*`, `git push*` → `deny`) and `rm -rf*` → `ask`. Sync the updated agent to the global config directory.

## Blueprint Reference

Orchestrator `<opencode_implementation_task>` (post-closure follow-up to Task 82): enables full autonomous execution of non-git bash commands so the executor does not stop for approval on routine operations (tests, formatters, uv, ls/find, etc.), relying on the permission-layer ZAC denies and the `rm -rf` guard for safety.

## Manager's Notes

- **Last-matching-rule-wins:** the deny rules are listed AFTER the `"*": "allow"` catch-all, so ZAC remains structurally enforced despite the broad allow.
- The agent prompt body (non-interactive bash rule, workspace security, MCP-first context) is unchanged — this is purely a permission-layer relaxation.
- The Orchestrator's bash phase omits a `git mv` instruction; per ZAC the task file is created directly in `tasks/in-progress/` and no state-altering git commands are run. Staging happens exclusively via `custom_context_stage_and_inject_diff`.
- Same unreleased feature as Task 82 — no new CHANGELOG section warranted.

## Local TODOs

- [x] Replace `permission.bash` block in `agents/cognitive-executor.md` with the autonomy catch-all + guards
- [x] Sync updated agent to `~/.config/opencode/agents/cognitive-executor.md`
- [x] Verify: `"*": "allow"` present; ZAC denies present
- [x] Append "Task Lifecycle & Kanban State Enforcement" failsafe section (Orchestrator follow-up)
- [x] Append "Skill Auto-Loading Matrix" + "Direct Input (Ad-Hoc) Validation Protocol" sections (Orchestrator follow-up)
- [x] Append "Context Bootstrapping & Memory Protocol" section (Orchestrator follow-up)
- [x] Append "Subagent Delegation for Context Discovery" section (Orchestrator follow-up)
- [x] Fix duplicated `DO SAVE` line in the Memory Protocol section (Code Review finding)
- [x] Lint task file, stage via MCP tool

## Acceptance Criteria

- [x] `agents/cognitive-executor.md` bash block is `"*": "allow"` with `rm -rf*` ask and git add/commit/push deny
- [x] Global `~/.config/opencode/agents/cognitive-executor.md` is in sync
- [x] Verification grep gates pass

## Verification Evidence

- **Test command:** `rg -n '"\*": "allow"' agents/cognitive-executor.md` and `rg -n 'git commit\*' agents/cognitive-executor.md`
- **Expected result:** catch-all allow present; `git commit*` deny present
- **Actual result:** `"*": "allow"` at line 9; `git add*`/`git commit*`/`git push*` → `deny` at lines 11–13; `rm -rf*` → `ask` at line 10. Global copy synced (`cp` exit 0).
- **Exit code:** 0 (all gates)

## Risk & Rollback

- **Risk:** Broad bash allow means any non-git, non-rm command runs without approval (e.g., network installs, file modifications outside workspace). Mitigated by prompt-level workspace-security rules and the `rm -rf`/git guards.
- **Rollback plan:** restore the previous allowlist block (`"*": "ask"` + granular allows) from git history of `agents/cognitive-executor.md`.

---

## OpenCode Execution Log & Reasoning

Updated cognitive-executor bash permissions to 'allow' catch-all for full autonomous execution, preserving ZAC denies and rm -rf safety guard.

### What was done

1. **`agents/cognitive-executor.md`** — replaced the 12-line granular bash permission map (`"*": "ask"` + allowlist of git-status/log/diff, git mv tasks/*, npx prettier, pytest, npm test, uv run, ls, find) with the 5-line autonomy block: `"*": "allow"` catch-all first, then `"rm -rf*": "ask"`, then `"git add*": "deny"`, `"git commit*": "deny"`, `"git push*": "deny"`. Because opencode evaluates permission patterns **last-match-wins**, the deny rules listed after the catch-all still override it — ZAC remains structurally impossible to bypass despite full bash autonomy.
2. **Global sync** — `cp agents/cognitive-executor.md ~/.config/opencode/agents/cognitive-executor.md` so the running environment reflects the change immediately (config re-read on next opencode start).

### Architectural reasoning

- **Autonomy vs. safety trade-off:** the granular ask-by-default (Task 82) maximized human-in-the-loop approval but created friction for routine operations (test runs, formatters, package installs), which are safe and expected in every task's bash phase. The catch-all `allow` moves the executor closer to Build's fluidity while keeping the two irreversible/dangerous classes gated: destructive filesystem ops (`rm -rf` → ask) and state-altering git ops (deny).
- **Prompt-level guards remain:** the agent body still mandates non-interactive bash flags and the workspace-security rule (no terminal commands modifying files outside the project workspace; `rm -rf` only for known auto-generated dirs). Permission relaxations do not weaken those instructions.
- **Task file placement:** created directly in `tasks/in-progress/` because the Orchestrator's bash phase omitted the `git mv` instruction — per ZAC, no state-altering git commands were executed; staging is handled exclusively by `custom_context_stage_and_inject_diff`.

### ZAC compliance

No `git add`/`git commit`/`git push` executed. Only `cp` (filesystem) and read-only `rg` gates. Staging via `custom_context_stage_and_inject_diff`.

### Follow-up iteration (Orchestrator review, 2026-08-08)

Appended 'Task Lifecycle & Kanban State Enforcement' section to cognitive-executor.md to act as a failsafe against Orchestrator hallucinations regarding file moves.

- **`agents/cognitive-executor.md`** — new section (line 33 onward) codifies the deterministic kanban-move rules into the agent prompt: (1) discovery tasks → no moves; (2) implementation tasks → verify file is in `tasks/in-progress/` BEFORE writing code, and self-correct via `git mv` (or filesystem `mv` if untracked) when the Orchestrator omitted the instruction; (3) no moves during QA/Review (Orchestrator/Manager owns those transitions); (4) closure → `git mv` to `tasks/completed/`, status `closed`, then `custom_context_commit_and_clean_task`. This converts the system-prompt's CRITICAL RULE 4 from an Orchestrator-side obligation into an executor-side deterministic enforcement — directly addressing the historical kanban-mv failure class (task 47 fix-kanban-mv-bug). The rule is safe under ZAC because it only ever runs `git mv` inside `tasks/`; `git add/commit/push` remain denied at the permission layer.
- **Global sync** — `cp agents/cognitive-executor.md ~/.config/opencode/agents/cognitive-executor.md` (exit 0).
- **Verification gates:** `rg -n "Task Lifecycle & Kanban State Enforcement"` → line 33; `rg -c "git mv tasks/"` → 2 (backlog→in-progress + closure move). Exit 0.

### Follow-up iteration 2 (Orchestrator review, 2026-08-08)

Appended 'Skill Auto-Loading Matrix' and 'Direct Input (Ad-Hoc) Validation Protocol' to cognitive-executor.md to enable self-correction for missing skills and safe handling of direct Manager instructions.

- **`agents/cognitive-executor.md`** — two new sections appended:
  1. **Skill Auto-Loading Matrix** (line 48): a 14-row mapping from detected tech-stack/context to the mandatory skill (android-kotlin, flask-python, go-gin/go-hexagonal-grpc, ios-swiftui, nestjs-prisma-vertical, nextjs, python-fastapi, react-native-expo, react-vite, spring-boot, vue-nuxt, task-generator, archive-tasks, debug-instrumentation). Converts the system-prompt's "Mandatory Project Skill Loading" obligation from Orchestrator-side instruction into executor-side deterministic auto-loading — the executor scans the task context and loads the correct skill via the `skill` tool even when the `<context_phase>` omits it.
  2. **Direct Input (Ad-Hoc) Validation Protocol** (line 70): a 5-step pipeline for non-XML Manager messages — intent validation with Farsi→English translation, task-file enforcement question (Kanban vs. quick fix), matrix-based skill loading, 3-step plan with explicit "Approved" gate before writing code, and ZAC reminder. This mirrors the system-prompt's `<user_input_processing>` pipeline at the executor level.
- **Global sync** — `cp agents/cognitive-executor.md ~/.config/opencode/agents/cognitive-executor.md` (exit 0).
- **Verification gates:** `rg -n "Skill Auto-Loading Matrix"` → line 48 (+ referenced at line 76); `rg -n "Direct Input"` → line 70 (the exact-phrase gate with parentheses failed initially due to ripgrep regex group semantics — `(Ad-Hoc)` parsed as a capture group — confirmed present via plain-string search). Exit 0.

### Follow-up iteration 3 (Orchestrator review, 2026-08-08)

Appended 'Context Bootstrapping & Memory Protocol' to cognitive-executor.md to ensure persistent memory is read before implementation and strict rules are auto-saved.

- **`agents/cognitive-executor.md`** — new section (line 81): (1) **Read First (Mandatory)** — load the `project-memory` skill and `search_memory` with task keywords + tech stack before writing any code, to surface saved constraints/quirks/architectural decisions; (2) **Apply Constraints** — adhere strictly to retrieved memories, flagging contradictions to the Manager; (3) **Auto-Save Criteria (Strict)** — `store_memory` ONLY for explicit new project rules/constraints/reusable quirks (with DO SAVE / DO NOT SAVE examples), keeping task progress and transient state in the task file instead. This lifts AGENTS.md's CONTEXT BOOTSTRAPPING mandate and the project-memory skill into the executor's permanent prompt.
- **Global sync** — `cp agents/cognitive-executor.md ~/.config/opencode/agents/cognitive-executor.md` (exit 0).
- **Verification gates:** `rg -n "Context Bootstrapping & Memory Protocol"` → line 81; `search_memory` at line 85; `store_memory` at line 87; file total 89 lines. Exit 0.

### Follow-up iteration 4 (Orchestrator review, 2026-08-08)

Appended 'Subagent Delegation for Context Discovery' to cognitive-executor.md to preserve primary context window by delegating read-heavy tasks to the cognitive-discovery subagent.

- **`agents/cognitive-executor.md`** — new section (line 93): mandates delegation of heavy context-gathering to the read-only `cognitive-discovery` subagent via the `task` tool: (1) discovery tasks → always delegate, never self-read; (2) combined tasks → delegate the `<discovery_phase>` and wait for the context report before the conditional implementation phase; (3) implementation tasks → delegate quick signature/block scans for unfamiliar modules before editing. This operationalizes the code-search skill's "signature extraction over full reads" and keeps the executor's context window reserved for implementation logic.
- **Global sync** — `cp agents/cognitive-executor.md ~/.config/opencode/agents/cognitive-executor.md` (exit 0).
- **Verification gates:** `rg -n "Subagent Delegation for Context Discovery"` → line 93; all three task-type delegation rules present (lines 97–99); file total 99 lines. Exit 0.

### Follow-up iteration 5 (Code Review fix, 2026-08-08)

Fixed duplicate 'DO SAVE' line in the Memory Protocol section.

- **`agents/cognitive-executor.md`** — the "Context Bootstrapping & Memory Protocol" section contained a duplicated `DO SAVE` bullet (lines 88–89, introduced as an append artifact in a prior iteration). Removed the duplicate; the section now has exactly one `DO SAVE` line followed by the `DO NOT SAVE` line.
- **Global sync** — `cp agents/cognitive-executor.md ~/.config/opencode/agents/cognitive-executor.md` (exit 0).
- **Verification gates:** `rg -c "DO SAVE"` → 1; `rg -c "DO NOT SAVE"` → 1; file total 98 lines. Exit 0.

Task approved for closure by the Manager. Moved to completed/.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `fca636ac878af67cfefd06c4b52d497f1f395886`
<!-- END_GIT_DIFF -->
