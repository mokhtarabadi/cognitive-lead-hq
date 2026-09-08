# Task 169: Track Post-Sprint Working Changes

**File:** `tasks/archive/169-track-post-sprint-working-changes.md`
**Source:** manager
**Type:** improvement
**Status:** superseded
**Superseded-By:** `171-post-sprint-workspace-bundle`
**Superseded-At:** `2026-09-09`

## Source Context

## Goal

Bring the uncommitted post-sprint working changes (temperature fix, global install, install-docs sync, live smoke script) under Kanban tracking for review, verification, and staged commit.

## Manager's Notes

- Covers ad-hoc work done after Tasks 167/168 closed: PERSONA_TEMPERATURE 0.2→1.0, global install of new servers/skills/agents + `.env` backup, LLM.txt/README/memory doc sync, `scripts/smoke_test_live.py`.
- `.env` (live secrets) stays OUT of git scope — verify ignored + untracked, never stage.
- Work is already implemented and locally verified; this task exists to review, re-verify, and commit it through the normal pipeline.

<!-- These sections are unconditional per lint contract — DO NOT move back inside variants -->

## Local TODOs

- [ ] Review unstaged diff (`git status`, `git diff`) for unintended content
- [ ] Re-run full test suite and record evidence
- [ ] Verify `.env` ignored and untracked; verify no secrets in staged files
- [ ] Stage via `custom_context_stage_and_inject_diff`, move to QA, await review

## Acceptance Criteria

- [x] Every working change listed in Manager's Notes is accounted for in the diff
- [x] Full test suite passes with exit code 0
- [x] No secrets (`.env`, keys, tokens) staged or committed

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with "mcp[cli]>=1.0,<2.0" --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin -- pytest tests/ -q`
- **Expected result:** 105 passed, exit 0
- **Actual result:** `105 passed, 8 warnings in 1.24s`; `COMPILE-OK`; empty-env + empty-cwd launch proved key loads from global backup with source notice on stderr
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Accidentally staging `.env` or secret-bearing files; committing unrelated scratch content.
- **Rollback plan:** Unstage specific paths (`git reset -- <path>`); secrets committed by mistake require history rewrite + key rotation.

---

> **Superseded:** This task was bundled into META task `171-post-sprint-workspace-bundle` and archived on 2026-09-09. See `tasks/backlog/171-post-sprint-workspace-bundle.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/169-track-post-sprint-working-changes.md`.

## Execution Log & Reasoning

### Round 1 — post-sprint changes (staged earlier)

Temperature 0.2→1.0 per Gemini 3 guidance (official docs: low values risk looping/degraded reasoning; tune thinking level instead); global install of persona/decision servers + manager-decision skill + executor + `.env` backup; LLM.txt/README/memory doc sync; `scripts/smoke_test_live.py` (live Telegram + Gemini + both servers green, exit 0); fixed two smoke-script bugs (`text_content` KeyError, `server.py` module collision).

### Round 2 — QA unblocked + model switch (this round)

**R1: QA 401 diagnosis.** `dispatch_session_turn` failed with OpenRouter 401 while the key itself probed 200 — the MCP server process launched keyless. Root cause: no `environment` block on our server entries, and no file-loading fallback. Fixed both layers: (a) `environment: {env:…}` blocks added to persona + manager_decisions entries in repo AND global `opencode.json` (references only, no secrets); (b) stdlib `_load_env_files()` at each server's import (server-dir → root/global-backup → cwd `.env`, `setdefault` so real env always wins; decision server loads BEFORE `REPO_ROOT` since `DECISION_REPO_PATH` may itself come from file). Telegram-mcp comparison: it relies on `uv --directory` auto-loading its sidecar `.env` — ours no longer depends on launcher behavior at all.

**R2: Model switch.** `PERSONA_MODEL=openrouter/deepseek/deepseek-v4-flash-0731` verified (29 OpenRouter endpoints) and applied to live `.env`, `.env.example`, global `.env` backup, both server fallbacks, and test expectations; global server copies re-synced (zero drift). Temperature stays 1.0 (also DeepSeek's default); `reasoning_effort` passes through `drop_params`.

**R3: Hygiene from the failed QA residue.** The failed dispatch left `tasks/.sessions/169/transcript.jsonl` (45KB of injected context, no assistant reply) — removed, and added `tasks/.sessions/` to `.gitignore` since transcripts are runtime-only audit trail.

**Verification:** full suite `103 passed` exit 0; empty-env launch test (`env -i` + global copy) picked the key + model from file — the exact failing condition, now green; secret scan clean (`.env` unstaged, no live keys in staged diff).

### Round 3 — off-by-one in the loader (post-restart 401)

**R1: Root cause.** QA still 401'd after restart. The candidates used `server_dir.parent.parent/.env`: for repo installs that resolves to the *parent of the repo*, for global installs to `~/.config` — the real files (repo root / `~/.config/opencode/.env` backup) live at `server_dir.parent/.env`. My earlier proof passed only because the test cwd happened to hold a `.env`. Fixed to `base.parent/.env`, added a `server_dir` override for tests, and a stderr notice (`persona-server: loaded env from <path>`) so the source is visible in MCP logs.

**R2: Regression tests.** Both suites gained a parent-fallback test (fake install layout + empty cwd asserts the key loads and the returned path ends in `.env`). Full suite `105 passed`.

**R3: Proof.** `env -i` + cwd `/tmp/empty-cwd` against the global copy: `persona-server: loaded env from /home/mohammad/.config/opencode/.env`, key length verified. Global copies re-synced, zero drift.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 21cfa32..8a16904 100644
--- a/.env.example
+++ b/.env.example
@@ -13,7 +13,9 @@ OPENROUTER_API_KEY=sk-or-v1-...
 # DEEPSEEK_API_KEY=...
 
 # Persona Engine (mcp-persona-server) — light LLM holding the system prompt
-PERSONA_MODEL=openrouter/google/gemini-3.8-flash
+PERSONA_MODEL=openrouter/deepseek/deepseek-v4-flash-0731
 PERSONA_REASONING_EFFORT=high
-PERSONA_TEMPERATURE=0.2
+# Gemini 3 family: keep temperature at the 1.0 default (Google warns that
+# low values risk looping / degraded reasoning — tune thinking level instead).
+PERSONA_TEMPERATURE=1.0
 PERSONA_MAX_TOKENS=16384
\ No newline at end of file
diff --git a/.gitignore b/.gitignore
index 5178e68..4a4043a 100644
--- a/.gitignore
+++ b/.gitignore
@@ -44,4 +44,7 @@ downloads/
 
 # worktree state (owt removed 2026-09-08 — keep guards if owt reinstalled; OpenChamber worktrees are SDK-managed)
 .opencode/worktrees/
-.opencode/worktree-sessions.json
\ No newline at end of file
+.opencode/worktree-sessions.json
+
+# Persona session transcripts (runtime audit trail, never committed)
+tasks/.sessions/
\ No newline at end of file
diff --git a/.opencode/memory/workflows/global-install-upgrade.md b/.opencode/memory/workflows/global-install-upgrade.md
index 8aa646c..8d72f4a 100644
--- a/.opencode/memory/workflows/global-install-upgrade.md
+++ b/.opencode/memory/workflows/global-install-upgrade.md
@@ -1,8 +1,8 @@
 ---
-created_at: '2026-09-05T19:29:36.505824+00:00'
+created_at: '2026-09-08T22:03:15.211239+00:00'
 status: active
 tags: []
-updated_at: '2026-09-08T11:30:00+00:00'
+updated_at: '2026-09-08T22:03:15.211356+00:00'
 ---
 
 # Global Install Upgrade Workflow (OpenCode)
@@ -15,48 +15,53 @@ Updates the machine-global installations of the Cognitive Lead AI HQ (MCP server
 
 | Component      | OpenCode                                                                                                       |
 | -------------- | -------------------------------------------------------------------------------------------------------------- |
-| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint}-server/server.py`                                                |
+| MCP servers    | `~/.config/opencode/mcp-{context,memory,lint}-server/server.py` + `~/.config/opencode/mcp-persona-server/*.py` (4 modules, Task 167) + `~/.config/opencode/mcp-decision-server/*.py` (2 modules, Task 168) |
 | Telegram MCP   | `~/.config/opencode/mcp-telegram-server/` (upstream clone of chigwell/telegram-mcp — no fork) |
-| Skills (31)    | `~/.config/opencode/skills/<name>/SKILL.md`                                                                    |
-| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md`                                        |
-| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md`                                                                |
-| System prompt  | `~/.config/opencode/system-prompt.md`                                                                          |
+| Skills (32)    | `~/.config/opencode/skills/<name>/SKILL.md` (`manager-decision` since Task 168) |
+| Custom agents  | `~/.config/opencode/agents/{cognitive-executor,cognitive-discovery}.md` |
+| Shell strategy | `~/.config/opencode/opencode-shell-strategy.md` |
+| System prompt  | `~/.config/opencode/system-prompt.md` |
+| Credentials    | `~/.config/opencode/.env` (chmod 600 backup of project `.env`; project copy stays authoritative since opencode loads project env for servers) |
 
 ## Source Files (repo)
 
 - `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`
-- `skill-templates/*/` (all 31 skills — `bundle-tasks` since Task 110)
+- `mcp-persona-server/*.py` (server, dual_dispatch, session, telegram), `mcp-decision-server/*.py` (server, redactor)
+- `skill-templates/*/` (all 32 skills — `bundle-tasks` since Task 110, `manager-decision` since Task 168)
 - `agents/cognitive-executor.md`, `agents/cognitive-discovery.md`
-- `docs/opencode-shell-strategy.md`, `system-prompt.md`
+- `docs/opencode-shell-strategy.md`, `system-prompt.md`, `.env.example` (PORTRAIT for `.env`, never copy secrets into docs)
 
 ## Upgrade Steps
 
 1. **Audit drift** (diff repo vs installed):
    ```bash
    for f in mcp-context-server/server.py mcp-memory-server/server.py mcp-lint-server/server.py; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
+   for f in mcp-persona-server/dual_dispatch.py mcp-persona-server/session.py mcp-persona-server/telegram.py mcp-persona-server/server.py mcp-decision-server/redactor.py mcp-decision-server/server.py; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
    for f in agents/cognitive-executor.md agents/cognitive-discovery.md; do diff -q "$f" ~/.config/opencode/"$f" || echo "DRIFT: $f"; done
    diff -q docs/opencode-shell-strategy.md ~/.config/opencode/opencode-shell-strategy.md || echo "DRIFT: shell-strategy"
    diff -q system-prompt.md ~/.config/opencode/system-prompt.md || echo "DRIFT: system-prompt"
    for d in skill-templates/*/; do n=$(basename "$d"); diff -rq "$d" ~/.config/opencode/skills/"$n" >/dev/null 2>&1 || echo "DRIFT: opencode skill $n"; done
-    # opencode.json: repo uses relative mcp-*-server/server.py for 3 core while global uses absolute /home/... — they will ALWAYS differ by design.
+    # opencode.json: repo uses relative mcp-*-server/server.py for 5 local while global uses absolute /home/... — they will ALWAYS differ by design.
     diff -q opencode.json ~/.config/opencode/opencode.json && echo "UNEXPECTED: opencode.json identical (should differ relative vs absolute)" || echo "EXPECTED DRIFT: opencode.json relative vs absolute (check shape separately)"
     # tui.json parity (OpenCode 1 goal plugin): both repo tui.json and global ~/.config/opencode/tui.json must contain {"plugin":["@prevalentware/opencode-goal-plugin"]} — identical by design (no relative/absolute split)
     diff -q tui.json ~/.config/opencode/tui.json && echo "tui.json in sync ✓" || echo "DRIFT: tui.json"
     # goal plugin parity: both opencode.json + tui.json (global + project) must use @prevalentware/opencode-goal-plugin (not opencode-goal-plugin)
     grep -q "@prevalentware/opencode-goal-plugin" opencode.json && echo "project opencode.json plugin ✓" || echo "DRIFT: project opencode.json plugin"
     grep -q "@prevalentware/opencode-goal-plugin" ~/.config/opencode/opencode.json && echo "global opencode.json plugin ✓" || echo "DRIFT: global opencode.json plugin"
-    ```
-2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). For `opencode.json` do NOT blind copy — regenerate global with absolute paths (see `LLM.txt:7` template):
+   ```
+2. **Copy drifted files** with `cp` + `chmod +x` (only those that differ). Multi-module servers copy `*.py` (never `__pycache__/`). For `opencode.json` do NOT blind copy — regenerate global with absolute paths (see `LLM.txt:7` template):
    ```bash
    cp mcp-lint-server/server.py ~/.config/opencode/mcp-lint-server/server.py && chmod +x ~/.config/opencode/mcp-lint-server/server.py
+   cp mcp-persona-server/*.py ~/.config/opencode/mcp-persona-server/ && chmod +x ~/.config/opencode/mcp-persona-server/server.py
+   cp mcp-decision-server/*.py ~/.config/opencode/mcp-decision-server/ && chmod +x ~/.config/opencode/mcp-decision-server/server.py
    cp system-prompt.md ~/.config/opencode/system-prompt.md
    cp skill-templates/task-generator/SKILL.md ~/.config/opencode/skills/task-generator/SKILL.md
-   # global opencode.json — regenerate with absolute $HOME for 5 MCPs (custom_context, project_memory, lint, blowsh docker, telegram uv --directory ...), do not cp repo's relative version
+   # global opencode.json — regenerate with absolute $HOME for 7 MCPs (custom_context, project_memory, lint, persona, manager_decisions, blowsh docker, telegram uv --directory ...), do not cp repo's relative version
    ```
 3. **Re-verify** with the same diff commands — expect no DRIFT output except the expected `opencode.json` relative vs absolute.
 4. **Smoke-test** servers launch and run the full test suite:
    ```bash
-   opencode mcp list  # should show ✓ connected for custom_context, project_memory, lint
+   opencode mcp list  # should show ✓ connected for all 7: custom_context, project_memory, lint, persona, manager_decisions (+ blowsh, telegram)
    uv run --with pytest --with 'mcp[cli]>=1.0,<2.0' --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
    ```
 
@@ -95,9 +100,12 @@ The installed copy at `~/.config/opencode/mcp-telegram-server` is a git clone of
 - The `lint` MCP server gains new tools when updated (e.g. `lint_system_prompt_sync`) — check `grep -c "lint_system_prompt_sync" ~/.config/opencode/mcp-lint-server/server.py` after sync (≥1).
 - Skills must be synced to `~/.config/opencode/skills/`.
 - Agent ports: `.md` for OpenCode (`agents/`).
-- `opencode.json` permission `bundle_tasks: allow` is required for the `bundle_tasks` MCP tool (added Task 110).
-- **Project vs Global `opencode.json` (Option A 2026-08-25):** Repo `opencode.json` uses **relative** `mcp-context-server/server.py` etc for 3 core — `opencode mcp list` inside clone shows `✓ connected`; literal `$HOME/...` in repo's `command` breaks. Global `~/.config/opencode/opencode.json` must use **absolute** `$HOME/.config/opencode/...` for all 5. `blowsh`/`telegram` stay `enabled:false` in repo (require global install) vs `enabled:true` in global. `diff opencode.json` will always differ — verify shape, not identity.
+- `opencode.json` permission `bundle_tasks: allow` is required for the `bundle_tasks` MCP tool (added Task 110); persona/decision tool allows (`dispatch_session_turn`, `record_manager_decision`, …) since Tasks 167/168.
+- **Project vs Global `opencode.json` (Option A 2026-08-25):** Repo `opencode.json` uses **relative** `mcp-*-server/server.py` for 5 local servers — `opencode mcp list` inside clone shows `✓ connected`; literal `$HOME/...` in repo's `command` breaks. Global `~/.config/opencode/opencode.json` must use **absolute** `$HOME/.config/opencode/...` for all 7. `blowsh`/`telegram` stay `enabled:false` in repo (require global install) vs `enabled:true` in global. `diff opencode.json` will always differ — verify shape, not identity.
   - **Update 2026-08-25 (Manager-approved):** repo now OMITS the `blowsh`/`telegram` blocks entirely so they inherit the working global definitions in-project.
   - **Update 2026-09-03:** Telegram MCP used fork `mokhtarabadi/telegram-mcp` (`fork` remote) — `main` = upstream chigwell `main` (7842b91) + `fix/allowed-root-automkdir-and-topic-filter` (c83a54e). Upstream sync via `fork` rebase. Installed tracked `fork/main`.
   - **Update 2026-09-05:** Telegram MCP fast-forwarded `3c37edb` → `7623e6b` (v3.2.31). Upstream PRs #206, #207, #210. PR #201 already in upstream — `merge --ff-only` + `push fork main`. Tests: 476 passed.
   - **Update 2026-09-08:** Per Manager directive, Telegram MCP switched from fork to **upstream chigwell/telegram-mcp directly** — `fork` remote removed (`git remote remove fork`), `origin` = https://github.com/chigwell/telegram-mcp.git only. Installed `main` now tracks `origin/main` at `c9460f8` (v3.2.32, PR #213 forward-routing). Fork patch already upstreamed (3c37edb ancestor of origin/main verified). Tests: 506 passed. No fork push needed.
+  - **Update 2026-09-08 (Tasks 167/168):** persona + manager_decisions MCP servers installed globally (absolute paths, 120s timeouts); `manager-decision` skill synced (32 total); executor agent synced; project `.env` backed up to `~/.config/opencode/.env` (chmod 600).
+
+Supersedes: workflows/global-install-upgrade (prior revision: 31 skills, 5 MCPs).
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 882aa57..5b85fb2 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -19,6 +19,9 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ### Changed
 
 - **Persona engine variables (Task 167):** `.env.example` gains `PERSONA_MODEL=openrouter/google/gemini-3.8-flash`, `PERSONA_REASONING_EFFORT=high`, `PERSONA_TEMPERATURE=0.2`, `PERSONA_MAX_TOKENS=16384`, `TELEGRAM_CHAT_ID`, `TELEGRAM_APPROVAL_TIMEOUT_SECONDS=1800`; retired `LOOP_ENGINE_DEBUG` with the daemon.
+- **Persona temperature 0.2 → 1.0 (Gemini 3 guidance):** Google's Gemini 3 docs strongly recommend the 1.0 temperature default — low values risk looping and degraded reasoning on complex tasks (tune thinking level instead). Updated `.env.example`, live `.env`, `mcp-persona-server/server.py` fallback, and persona-server tests.
+- **Install docs synced for 7-server system:** `LLM.txt` §4/§5/§7/checklist (persona + manager_decisions entries, 32 skills, 7 MCP entries), `README.md` (retired-daemon section rewritten to Persona Engine + Decision Learning, repo tree updated), and `global-install-upgrade` memory (locations, drift audit, smoke for 7 servers, `.env` backup note).
+- **Persona model → DeepSeek V4 Flash + self-loading env:** `PERSONA_MODEL=openrouter/deepseek/deepseek-v4-flash-0731` (verified 29 OpenRouter endpoints) across `.env`/`.env.example`/server fallbacks/tests; both MCP servers gained a stdlib `_load_env_files()` (server-dir → repo/global-root → cwd `.env`, never overriding real env) after diagnosing that OpenCode launched them keyless (401) — plus `environment: {env:…}` blocks in repo + global `opencode.json`; `tasks/.sessions/` gitignored (transcripts are runtime-only).
 
 ### Removed
 
diff --git a/LLM.txt b/LLM.txt
index e933646..8c5813c 100644
--- a/LLM.txt
+++ b/LLM.txt
@@ -82,6 +82,8 @@ Create the global OpenCode directories:
 mkdir -p ~/.config/opencode/mcp-context-server
 mkdir -p ~/.config/opencode/mcp-memory-server
 mkdir -p ~/.config/opencode/mcp-lint-server
+mkdir -p ~/.config/opencode/mcp-persona-server
+mkdir -p ~/.config/opencode/mcp-decision-server
 mkdir -p ~/.config/opencode/skills
 ```
 
@@ -89,15 +91,19 @@ mkdir -p ~/.config/opencode/skills
 
 ## 5. Copy MCP Servers and Make Them Executable
 
-Copy both MCP server scripts from the cloned repo:
+Copy the MCP server scripts from the cloned repo (persona ships 4 modules, decision ships 2):
 
 ```bash
 cp /tmp/cognitive-lead-hq/mcp-context-server/server.py ~/.config/opencode/mcp-context-server/
 cp /tmp/cognitive-lead-hq/mcp-memory-server/server.py ~/.config/opencode/mcp-memory-server/
 cp /tmp/cognitive-lead-hq/mcp-lint-server/server.py ~/.config/opencode/mcp-lint-server/
+cp /tmp/cognitive-lead-hq/mcp-persona-server/*.py ~/.config/opencode/mcp-persona-server/
+cp /tmp/cognitive-lead-hq/mcp-decision-server/*.py ~/.config/opencode/mcp-decision-server/
 chmod +x ~/.config/opencode/mcp-context-server/server.py
 chmod +x ~/.config/opencode/mcp-memory-server/server.py
 chmod +x ~/.config/opencode/mcp-lint-server/server.py
+chmod +x ~/.config/opencode/mcp-persona-server/server.py
+chmod +x ~/.config/opencode/mcp-decision-server/server.py
 
 # Preserve system-prompt.md globally for the user's Orchestrator
 cp /tmp/cognitive-lead-hq/system-prompt.md ~/.config/opencode/system-prompt.md
@@ -116,7 +122,7 @@ Copy all reusable skills from `skill-templates/` into the global OpenCode skills
 cp -r /tmp/cognitive-lead-hq/skill-templates/* ~/.config/opencode/skills/
 ```
 
-After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **31 skills** (`bundle-tasks` since Task 110, `github` since Task 121).
+After this, the skills will be available via `/help` from any directory. `skill-templates/` contains **32 skills** (`bundle-tasks` since Task 110, `github` since Task 121, `manager-decision` since Task 168).
 
 ### 6.1. (Optional) Bundle CLI Script — Only If You Want `uv run scripts/bundle-tasks.py`
 
@@ -150,7 +156,7 @@ After this, the `cognitive-executor` will be available as a primary agent, enfor
 
 ## 7. Configure Global opencode.json (with Absolute Paths)
 
-Create or update `~/.config/opencode/opencode.json`. You MUST use **absolute paths** in the `command` array — resolve the `~` to the full home directory path discovered in Step 3. Since 2026-08-25 the project ships **5 MCP servers** (3 core + `blowsh` browsing + `telegram` account routing); the previous browser automation MCP has been retired — use `blowsh` for JS-heavy browsing.
+Create or update `~/.config/opencode/opencode.json`. You MUST use **absolute paths** in the `command` array — resolve the `~` to the full home directory path discovered in Step 3. Since 2026-09-08 the project ships **7 MCP servers** (3 core + `persona` dispatch + `manager_decisions` learning + `blowsh` browsing + `telegram` account routing); the previous browser automation MCP has been retired — use `blowsh` for JS-heavy browsing.
 
 Write the following JSON (replace `$HOME` with the actual home directory path, and adjust the `telegram` `--directory` if you cloned `telegram-mcp` elsewhere):
 
@@ -179,6 +185,18 @@ Write the following JSON (replace `$HOME` with the actual home directory path, a
       "enabled": true,
       "timeout": 15000
     },
+    "persona": {
+      "type": "local",
+      "command": ["uv", "run", "$HOME/.config/opencode/mcp-persona-server/server.py"],
+      "enabled": true,
+      "timeout": 120000
+    },
+    "manager_decisions": {
+      "type": "local",
+      "command": ["uv", "run", "$HOME/.config/opencode/mcp-decision-server/server.py"],
+      "enabled": true,
+      "timeout": 120000
+    },
     "blowsh": {
       "type": "local",
       "command": ["docker", "run", "--rm", "-i", "ghcr.io/mokhtarabadi/blowsh-mcp:latest"],
@@ -209,6 +227,15 @@ Write the following JSON (replace `$HOME` with the actual home directory path, a
     "bundle_tasks": "allow",
     "blowsh_*": "allow",
     "telegram_*": "allow",
+    "dispatch_session_turn": "allow",
+    "get_session_summary": "allow",
+    "escalate_to_admin": "allow",
+    "request_admin_approval": "allow",
+    "extract_session_decisions": "allow",
+    "record_manager_decision": "allow",
+    "query_manager_decisions": "allow",
+    "get_manager_profile": "allow",
+    "propose_profile_evolution": "allow",
     "external_directory": {
       "*": "ask",
       "/tmp/**": "allow"
@@ -235,7 +262,7 @@ OpenCode 1 reads `plugin` from **both** `opencode.json` (server/tools) and `tui.
 
 **Important:** Replace `$HOME` with the actual absolute path resolved in Step 3 (e.g., `/home/alice` or `/Users/alice`). This is critical — MCP servers will NOT work with relative paths or `~` in the global config because OpenCode may be invoked from any working directory.
 
-> **Project vs Global `opencode.json` + `tui.json` (Option A fix 2026-08-25, updated 2026-08-28 for @prevalentware, 2026-09-05 for @tarquinen/opencode-dcp):** The **repo's** `opencode.json` (committed) intentionally uses **relative** paths for the 3 core servers — `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py` — so `opencode mcp list` inside the clone shows `✓ connected` without shell expansion (verified `uv run $HOME/...` fails with `No such file or directory`). Using literal `$HOME` in the repo's `command` array breaks local launches because OpenCode does not expand env vars. The **global** `~/.config/opencode/opencode.json` (created here) **must** use absolute paths as in the JSON above. `plugin` arrays (goal + DCP) are **identical** in project and global by design — no relative/absolute split for plugins. `blowsh` (docker) and `telegram` stay `enabled:false` with `$HOME` placeholders in the repo (they require the global install at `~/.config/opencode/mcp-telegram-server/`), while the global enables them `true` with absolute roots. New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff -q opencode.json ~/.config/opencode/opencode.json` will always differ (relative vs absolute) by design; verify project shows `uv run mcp-*-server/server.py` and global shows `/home/...`. Verify parity with `diff -q tui.json ~/.config/opencode/tui.json && echo "tui.json in sync ✓"` and `grep -q "@tarquinen/opencode-dcp" opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "DCP plugin both ✓"`.
+> **Project vs Global `opencode.json` + `tui.json` (Option A fix 2026-08-25, updated 2026-08-28 for @prevalentware, 2026-09-05 for @tarquinen/opencode-dcp, 2026-09-08 for persona + manager_decisions):** The **repo's** `opencode.json` (committed) intentionally uses **relative** paths for the 5 local servers — `mcp-context-server/server.py`, `mcp-memory-server/server.py`, `mcp-lint-server/server.py`, `mcp-persona-server/server.py`, `mcp-decision-server/server.py` — so `opencode mcp list` inside the clone shows `✓ connected` without shell expansion (verified `uv run $HOME/...` fails with `No such file or directory`). Using literal `$HOME` in the repo's `command` array breaks local launches because OpenCode does not expand env vars. The **global** `~/.config/opencode/opencode.json` (created here) **must** use absolute paths as in the JSON above. `plugin` arrays (goal + DCP) are **identical** in project and global by design — no relative/absolute split for plugins. `blowsh` (docker) and `telegram` stay `enabled:false` with `$HOME` placeholders in the repo (they require the global install at `~/.config/opencode/mcp-telegram-server/`), while the global enables them `true` with absolute roots. New installations and `global-install-upgrade` (Step 5 in `.opencode/memory/workflows/global-install-upgrade.md`) must keep this split — `diff -q opencode.json ~/.config/opencode/opencode.json` will always differ (relative vs absolute) by design; verify project shows `uv run mcp-*-server/server.py` and global shows `/home/...`. Verify parity with `diff -q tui.json ~/.config/opencode/tui.json && echo "tui.json in sync ✓"` and `grep -q "@tarquinen/opencode-dcp" opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && echo "DCP plugin both ✓"`.
 
 **Telegram is optional but auto-configured:** the entry above points at `~/.config/opencode/mcp-telegram-server` (installed in the opencode config dir per global-install-upgrade, absolute path required) with two allowed roots (`/tmp/telegram-mcp` for temp state + `~/.config/opencode/mcp-telegram-server/downloads` for exported media). If you cloned elsewhere, update the `--directory` and the trailing roots — keep them inside `$HOME` or `/tmp` and ensure `telegram_download_media` can write there. The server is installed in Step 7.6 even before you have API credentials; it stays idle (no `TELEGRAM_SESSION_STRING`) until you finish 7.6. For Docker blowsh no host binary is needed — `docker pull ghcr.io/mokhtarabadi/blowsh-mcp:latest` on first `fetch_web` run.
 
@@ -243,7 +270,7 @@ OpenCode 1 reads `plugin` from **both** `opencode.json` (server/tools) and `tui.
 
 ## 7.6. (Optional but Recommended) Install Telegram + Blowsh Prerequisites
 
-These two servers extend the core 3 with external browsing and Telegram account control. Skip `telegram` if you do not use Telegram; skip `blowsh` if you cannot run Docker.
+These two servers extend the core 5 with external browsing and Telegram account control. Skip `telegram` if you do not use Telegram; skip `blowsh` if you cannot run Docker.
 
 ### Telegram prerequisites
 
@@ -444,10 +471,12 @@ After completing all steps, verify:
 - [ ] `~/.config/opencode/mcp-context-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-memory-server/server.py` exists and is executable
 - [ ] `~/.config/opencode/mcp-lint-server/server.py` exists and is executable
-- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` (31 skills total)
+- [ ] `~/.config/opencode/mcp-persona-server/server.py` exists and is executable (multi-file: `dual_dispatch.py`, `session.py`, `telegram.py` alongside)
+- [ ] `~/.config/opencode/mcp-decision-server/server.py` exists and is executable (`redactor.py` alongside)
+- [ ] Skills are installed under `~/.config/opencode/skills/` (at least one subfolder exists) — should include `bundle-tasks` and `manager-decision` (32 skills total)
 - [ ] `~/.config/opencode/agents/cognitive-executor.md` exists
 - [ ] `~/.config/opencode/agents/cognitive-discovery.md` exists
-- [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 5 `mcp` entries (`custom_context`, `project_memory`, `lint`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*` permissions, no former browser entry
+- [ ] `~/.config/opencode/opencode.json` exists with **absolute paths** (not `~` or relative paths) and 7 `mcp` entries (`custom_context`, `project_memory`, `lint`, `persona`, `manager_decisions`, `blowsh`, `telegram`) + `blowsh_*`/`telegram_*`/persona/decision-tool permissions, no former browser entry
 - [ ] `~/.config/opencode/opencode.json` + `tui.json` `plugin` arrays contain both `@prevalentware/opencode-goal-plugin` and `@tarquinen/opencode-dcp` (`grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/opencode.json && grep -q "@tarquinen/opencode-dcp" ~/.config/opencode/tui.json`); project `opencode.json` + `tui.json` match (`diff -q tui.json ~/.config/opencode/tui.json`)
 - [ ] DCP loads: `opencode plugin list` shows `@tarquinen/opencode-dcp`, `/dcp` panel opens, `~/.config/opencode/dcp.jsonc` created on first run (project `.opencode/dcp.jsonc` overrides if present)
 - [ ] worktrees: OpenChamber native via sidebar/dialog (`https://docs.openchamber.dev/worktrees/`) — no `owt` required; if owt reinstalled, `owt help` + `~/.config/opencode/plugins/worktree-plugin.js` + `/init-worktree` after restart
@@ -465,6 +494,8 @@ After completing all steps, verify:
   uv run ~/.config/opencode/mcp-context-server/server.py &
   uv run ~/.config/opencode/mcp-memory-server/server.py &
   uv run ~/.config/opencode/mcp-lint-server/server.py &
+  uv run ~/.config/opencode/mcp-persona-server/server.py &
+  uv run ~/.config/opencode/mcp-decision-server/server.py &
   ```
 
 ---
diff --git a/README.md b/README.md
index 354cf7e..038a27d 100644
--- a/README.md
+++ b/README.md
@@ -123,49 +123,47 @@ The repository includes a standalone web tool at `tools/prompt-composer/index.ht
 
 ---
 
-## 🤖 Cognitive Loop Engine
+## 🤖 Persona Engine + Decision Learning
 
-The **Cognitive Loop Engine** is a local orchestration daemon that eliminates the manual copy-paste workflow between the Orchestrator (Brain) and OpenCode (Hands). It routes tasks to LLM APIs, invokes execution programmatically, and maintains Manager approval gates via Telegram.
+The **Persona Engine** (Tasks 167–168) replaced the retired loop-engine daemon with on-demand persona turns: OpenCode itself calls personas (`/qa`, `/reviewer`, `/manager`, `/brainstorm`) backed by a light LLM holding the full system prompt, with Telegram Approve/Reject hard gates. The **Decision Learning** side captures per-session manager rulings into a separate append-only repo that evolves the manager-AI sample behind human review.
 
 ### What It Does
 
 ```
-Manager creates task → Daemon detects → AI plans → Telegram approval →
-OpenCode executes → QA reviews → Telegram closure → Done
+Manager creates task → Executor implements → /qa adversarial review →
+/reviewer standards audit → Telegram approval → Closure →
+Decisions extracted → Learning repo → Sample evolves (review-gated)
 ```
 
 ### Quick Start
 
 ```bash
-# 1. Install dependencies
-cd loop-engine
-uv venv .venv
-source .venv/bin/activate
-uv pip install pydantic litellm watchdog python-telegram-bot
-
-# 2. Configure
-cp ../.env.example ../.env
-# Edit .env with your API keys
-
-# 3. Start
-python daemon.py
+# 1. Configure
+cp .env.example .env
+# Edit .env with your keys (OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
+
+# 2. Register servers (global install, absolute paths) or use the repo opencode.json locally
+# mcp-persona-server + mcp-decision-server run via `uv run` stdio FastMCP, zero-install deps
+
+# 3. Invoke in OpenCode
+# /qa → adversarial testing → /reviewer → audit → /manager → approval gate
 ```
 
 ### Features
 
-- **Category-based model routing** — quick→kimi, deep→gpt-5.6, visual→opus-5
-- **Telegram approval gateway** — Inline keyboard Approve/Reject
+- **Persona slash commands** — `/qa`, `/reviewer`, `/manager`, `/brainstorm`, each with Dual Dispatch classification (`XML_EXTRACTED` / `QUESTION` / `REPORT`)
+- **Telegram approval gateway** — task/stage-scoped inline keyboard Approve/Reject with stale-press discard
 - **Auto-continue** — Goal Plugin handles idle detection and continuation
 - **Evidence-bound QA** — No evidence = no commit
-- **SQLite state machine** — Crash recovery, task tracking
-- **Multi-project support** — One bot, Topics per project
+- **Append-only session transcripts** — `tasks/.sessions/{id}/transcript.jsonl`, the audit trail behind every gate
+- **Manager-decision learning repo** — verbatim quotes + redaction + review-gated sample evolution
 
 ### Documentation
 
-- [Architecture Overview](docs/loop-engine/README.md)
-- [Setup Guide](docs/loop-engine/setup.md)
-- [Configuration Reference](docs/loop-engine/configuration.md)
-- [Multi-Project Guide](docs/loop-engine/multi-project.md)
+- [Manager-Decision Skill](skill-templates/manager-decision/SKILL.md)
+- [Cognitive Executor Agent](agents/cognitive-executor.md) (Persona Loop section)
+- [Setup Guide](docs/setup.md)
+- Historical loop-engine docs remain under `docs/loop-engine/` for reference (daemon retired in Task 167).
 
 ---
 
@@ -196,17 +194,15 @@ python daemon.py
 │   └── server.py                       # FastMCP server for task file linting
 ├── mcp-memory-server/
 │   └── server.py                       # FastMCP server for persistent project memory
-├── loop-engine/                         # Cognitive Loop Engine daemon
-│   ├── daemon.py                        # Main entry point
-│   ├── models.py                        # Pydantic config validation
-│   ├── state.py                         # SQLite state machine
-│   ├── watcher.py                       # Kanban filesystem observer
-│   ├── router.py                        # LLM category routing
-│   ├── executor.py                      # Goal Plugin delegation
-│   ├── gateway.py                       # Telegram approval gateway
-│   ├── qa_engine.py                     # Evidence-bound QA
-│   ├── loop-engine.jsonc                # Configuration file
-│   └── pyproject.toml                   # Python dependencies
+├── mcp-persona-server/                 # Persona dispatch engine (Task 167)
+│   ├── server.py                       # FastMCP `PersonaServer`: dispatch/summary/approval tools
+│   ├── dual_dispatch.py                # XML vs question classifier
+│   ├── session.py                      # Append-only JSONL transcripts + lineage projection
+│   └── telegram.py                     # Scoped Approve/Reject gates over Bot API
+├── mcp-decision-server/                # Manager-decision learning (Task 168)
+│   ├── server.py                       # FastMCP `ManagerDecisions`: extract/record/query/profile/propose
+│   └── redactor.py                     # Secret scrubbing + verify gate
+├── packages/cognitive-lead-decisions/  # Separate learning repo (DEC-*.json, profile sample, scripts)
 ├── prompts/                            # System prompt source tree (fragments + shared partials)
 │   ├── README.md                       # Authoring workflow guide
 │   ├── manifest.txt                    # Ordered fragment list (assembly order)
@@ -411,6 +407,8 @@ Best if you want this codebase exploration tool available in _every_ terminal di
 
 _(Note: Replace `/Users/<YOUR_USER>` with your actual home directory path)._
 
+> Full HQ install (all 7 MCP servers — context, memory, lint, persona, decisions, blowsh, telegram — plus 32 skills and both agents) is documented in `LLM.txt` §4–§7 and the `global-install-upgrade` memory workflow, not here; the steps above cover only the standalone context server for third-party projects.
+
 ### How It Works
 
 1. `opencode.json` configures the custom context server as a local MCP server.
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index 80cf3f5..7847707 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -36,6 +36,61 @@ from mcp.server.fastmcp import FastMCP
 
 from redactor import sanitize_text, verify_clean
 
+
+def _load_env_files(server_dir: Optional[Path] = None) -> Optional[str]:
+    """Load `.env` files explicitly (stdlib parser, no dependency).
+
+    Must run BEFORE `REPO_ROOT` is computed below, since `DECISION_REPO_PATH`
+    itself may come from a file. Search order (first file holding a key wins
+    via setdefault; real process environment always wins over every file):
+    `<server-dir>/.env`, then `<server-dir>/../.env` (repo root, or the
+    `~/.config/opencode/.env` backup for global installs), then `<cwd>/.env`.
+
+    Args:
+        server_dir: Override for tests (defaults to this file's directory).
+
+    Returns:
+        Path of the first `.env` file actually loaded, or None.
+    """
+    base = Path(server_dir).resolve() if server_dir is not None else Path(__file__).resolve().parent
+    candidates = [base / ".env", base.parent / ".env", Path.cwd() / ".env"]
+    seen: set[Path] = set()
+    first_loaded: Optional[str] = None
+    for path in candidates:
+        try:
+            resolved = path.resolve()
+        except OSError:
+            continue
+        if resolved in seen or not resolved.is_file():
+            continue
+        seen.add(resolved)
+        try:
+            text = resolved.read_text(encoding="utf-8")
+        except (OSError, UnicodeError):
+            continue
+        for line in text.splitlines():
+            line = line.strip()
+            if not line or line.startswith("#") or "=" not in line:
+                continue
+            key, _, value = line.partition("=")
+            key = key.strip()
+            if key.startswith("export "):
+                key = key[len("export ") :].strip()
+            if not key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
+                continue
+            value = value.strip()
+            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
+                value = value[1:-1]
+            if first_loaded is None and key not in os.environ:
+                first_loaded = str(resolved)
+            os.environ.setdefault(key, value)
+    if first_loaded is not None:
+        print(f"decision-server: loaded env from {first_loaded}", file=sys.stderr)
+    return first_loaded
+
+
+_load_env_files()
+
 # Decision repo root: standalone checkout via env, else the in-repo package.
 REPO_ROOT = Path(
     os.environ.get("DECISION_REPO_PATH", Path(__file__).resolve().parent.parent
@@ -215,7 +270,7 @@ def extract_session_decisions(
         "Empty array when the session holds no manager rulings.\n\n" + "\n".join(turns)
     )
     response = litellm.completion(
-        model=os.environ.get("PERSONA_MODEL", "openrouter/google/gemini-3.8-flash"),
+        model=os.environ.get("PERSONA_MODEL", "openrouter/deepseek/deepseek-v4-flash-0731"),
         messages=[{"role": "user", "content": prompt}],
         temperature=0.2,
         drop_params=True,
diff --git a/mcp-persona-server/server.py b/mcp-persona-server/server.py
index 4419cf1..d4f97ee 100644
--- a/mcp-persona-server/server.py
+++ b/mcp-persona-server/server.py
@@ -31,6 +31,8 @@ Transport: stdio FastMCP, mirroring mcp-context-server / mcp-memory-server.
 from __future__ import annotations
 
 import os
+import re
+import sys
 from pathlib import Path
 from typing import Any, Optional
 
@@ -44,13 +46,69 @@ from telegram import send_admin_question, send_approval_request
 # matter which cwd the stdio server is launched from.
 REPO_ROOT = Path(__file__).resolve().parent.parent
 
+
+def _load_env_files(server_dir: Optional[Path] = None) -> Optional[str]:
+    """Load `.env` files explicitly (stdlib parser, no dependency).
+
+    Search order (first file holding a key wins via setdefault; real
+    process environment always wins over every file):
+    1. `<server-dir>/.env` (sidecar, mirrors telegram-mcp layout).
+    2. `<server-dir>/../.env` — repo root for repo installs, or the
+       `~/.config/opencode/.env` backup for global installs.
+    3. `<cwd>/.env` (project root when opencode launches us in a project).
+
+    Args:
+        server_dir: Override for tests (defaults to this file's directory).
+
+    Returns:
+        Path of the first `.env` file actually loaded, or None.
+    """
+    base = Path(server_dir).resolve() if server_dir is not None else Path(__file__).resolve().parent
+    candidates = [base / ".env", base.parent / ".env", Path.cwd() / ".env"]
+    seen: set[Path] = set()
+    first_loaded: Optional[str] = None
+    for path in candidates:
+        try:
+            resolved = path.resolve()
+        except OSError:
+            continue
+        if resolved in seen or not resolved.is_file():
+            continue
+        seen.add(resolved)
+        try:
+            text = resolved.read_text(encoding="utf-8")
+        except (OSError, UnicodeError):
+            continue
+        for line in text.splitlines():
+            line = line.strip()
+            if not line or line.startswith("#") or "=" not in line:
+                continue
+            key, _, value = line.partition("=")
+            key = key.strip()
+            if key.startswith("export "):
+                key = key[len("export ") :].strip()
+            if not key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
+                continue
+            value = value.strip()
+            if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
+                value = value[1:-1]
+            if first_loaded is None and key not in os.environ:
+                first_loaded = str(resolved)
+            os.environ.setdefault(key, value)
+    if first_loaded is not None:
+        print(f"persona-server: loaded env from {first_loaded}", file=sys.stderr)
+    return first_loaded
+
+
+_load_env_files()
+
 mcp = FastMCP("PersonaServer")
 
 
 def _get_persona_model() -> str:
     """LLM model for persona turns; override via ``PERSONA_MODEL``."""
-    return os.environ.get("PERSONA_MODEL", "openrouter/google/gemini-3.8-flash").strip() or (
-        "openrouter/google/gemini-3.8-flash"
+    return os.environ.get("PERSONA_MODEL", "openrouter/deepseek/deepseek-v4-flash-0731").strip() or (
+        "openrouter/deepseek/deepseek-v4-flash-0731"
     )
 
 
@@ -62,11 +120,15 @@ def _get_reasoning_effort() -> str:
 
 
 def _get_temperature() -> float:
-    """Sampling temperature; override via ``PERSONA_TEMPERATURE`` (default 0.2)."""
+    """Sampling temperature; override via ``PERSONA_TEMPERATURE`` (default 1.0).
+
+    Gemini 3 family guidance: keep the 1.0 default; low values risk looping
+    and degraded reasoning on complex tasks. Tune reasoning effort instead.
+    """
     try:
-        return float(os.environ.get("PERSONA_TEMPERATURE", "0.2") or 0.2)
+        return float(os.environ.get("PERSONA_TEMPERATURE", "1.0") or 1.0)
     except ValueError:
-        return 0.2
+        return 1.0
 
 
 def _get_max_tokens() -> int:
diff --git a/opencode.json b/opencode.json
index c3443e9..adb3d0e 100644
--- a/opencode.json
+++ b/opencode.json
@@ -29,13 +29,27 @@
       "type": "local",
       "command": ["uv", "run", "mcp-persona-server/server.py"],
       "enabled": true,
-      "timeout": 120000
+      "timeout": 120000,
+      "environment": {
+        "OPENROUTER_API_KEY": "{env:OPENROUTER_API_KEY}",
+        "PERSONA_MODEL": "{env:PERSONA_MODEL}",
+        "PERSONA_REASONING_EFFORT": "{env:PERSONA_REASONING_EFFORT}",
+        "PERSONA_TEMPERATURE": "{env:PERSONA_TEMPERATURE}",
+        "PERSONA_MAX_TOKENS": "{env:PERSONA_MAX_TOKENS}",
+        "TELEGRAM_BOT_TOKEN": "{env:TELEGRAM_BOT_TOKEN}",
+        "TELEGRAM_CHAT_ID": "{env:TELEGRAM_CHAT_ID}",
+        "TELEGRAM_APPROVAL_TIMEOUT_SECONDS": "{env:TELEGRAM_APPROVAL_TIMEOUT_SECONDS}"
+      }
     },
     "manager_decisions": {
       "type": "local",
       "command": ["uv", "run", "mcp-decision-server/server.py"],
       "enabled": true,
-      "timeout": 120000
+      "timeout": 120000,
+      "environment": {
+        "OPENROUTER_API_KEY": "{env:OPENROUTER_API_KEY}",
+        "PERSONA_MODEL": "{env:PERSONA_MODEL}"
+      }
     }
   },
   "permission": {
diff --git a/scripts/smoke_test_live.py b/scripts/smoke_test_live.py
new file mode 100644
index 0000000..cf7bef8
--- /dev/null
+++ b/scripts/smoke_test_live.py
@@ -0,0 +1,165 @@
+"""Live smoke test for mcp-persona-server and mcp-decision-server (Task 167/168).
+
+Reads credentials ONLY from `.env` (never hardcodes secrets). Exit 0 means
+all four live checks passed; any failure raises with a clear message.
+
+Usage (repo root):
+    uv run --with litellm --with python-dotenv --with "mcp[cli]>=1.0,<2.0" \\
+        python scripts/smoke_test_live.py
+"""
+
+from __future__ import annotations
+
+import json
+import os
+import sys
+import urllib.request
+from pathlib import Path
+
+from dotenv import load_dotenv
+
+load_dotenv()
+
+REPO_ROOT = Path(__file__).resolve().parent.parent
+os.chdir(REPO_ROOT)
+
+
+def _excerpt(turn_result: dict) -> str:
+    """Status-aware excerpt: real dispatch statuses carry no 'text_content'."""
+    status = turn_result.get("status", "?")
+    body = (
+        turn_result.get("report")
+        or turn_result.get("question")
+        or turn_result.get("hint")
+        or turn_result.get("remainder")
+        or (turn_result.get("xml_content") or "")[:500]
+    )
+    return f"[{status}] {str(body)[:150]}"
+
+
+def check_telegram() -> None:
+    """[1/4] Bot identity + real greeting ping to the manager chat."""
+    print("\n[1/4] Verifying Telegram Bot API...")
+    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
+    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
+    assert token and chat_id, "TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID missing from .env"
+    with urllib.request.urlopen(
+        urllib.request.Request(
+            f"https://api.telegram.org/bot{token}/getMe",
+            headers={"User-Agent": "CognitiveLead/1.0"},
+        ),
+        timeout=15,
+    ) as resp:
+        username = json.loads(resp.read().decode())["result"]["username"]
+    print(f"  PASS Bot connected: @{username}")
+    payload = json.dumps({
+        "chat_id": chat_id,
+        "text": "Cognitive Lead AI System Online! "
+                "Both mcp-persona-server and mcp-decision-server are active and verified.",
+    }).encode("utf-8")
+    with urllib.request.urlopen(
+        urllib.request.Request(
+            f"https://api.telegram.org/bot{token}/sendMessage",
+            data=payload,
+            headers={"Content-Type": "application/json", "User-Agent": "CognitiveLead/1.0"},
+        ),
+        timeout=15,
+    ):
+        pass
+    print(f"  PASS Test ping delivered to chat_id={chat_id}")
+
+
+def check_llm() -> None:
+    """[2/4] Light-model round trip via OpenRouter."""
+    print("\n[2/4] Verifying Gemini 3.8 Flash via OpenRouter...")
+    import litellm  # Lazy: only needed for the live path.
+
+    model = os.environ.get("PERSONA_MODEL", "openrouter/google/gemini-3.8-flash")
+    response = litellm.completion(
+        model=model,
+        messages=[{"role": "user", "content": "Respond with the single word: CONFIRMED"}],
+        temperature=0.1,
+        drop_params=True,
+    )
+    reply = str(response.choices[0].message.content or "").strip()
+    assert reply, "Empty model reply"
+    print(f"  PASS Model response: {reply}")
+
+
+def check_persona_dispatch() -> None:
+    """[3/4] Real persona turn (writes a scratch transcript under task 999)."""
+    print("\n[3/4] Testing mcp-persona-server dispatch turn...")
+    sys.path.insert(0, str((REPO_ROOT / "mcp-persona-server").resolve()))
+    from server import dispatch_session_turn  # noqa: E402
+
+    call = dispatch_session_turn.fn if hasattr(dispatch_session_turn, "fn") else dispatch_session_turn
+    result = call(
+        task_id=999,
+        persona_name="Software Architect",
+        instruction="Confirm system architecture status in one sentence.",
+    )
+    assert result.get("status") in ("XML_EXTRACTED", "QUESTION", "REPORT", "RETRY_NEEDED"), result
+    print(f"  PASS Status: {result['status']}")
+    print(f"  PASS Persona excerpt: {_excerpt(result)}...")
+
+
+def check_decision_store() -> None:
+    """[4/4] Record + query a smoke decision in the configured repo."""
+    print("\n[4/4] Testing mcp-decision-server storage & query...")
+    # NOTE: both servers are named server.py — import by path under a unique
+    # module name instead of plain `from server import ...`, which would
+    # resolve to the already-imported persona server via sys.modules.
+    import importlib.util
+
+    decision_dir = (REPO_ROOT / "mcp-decision-server").resolve()
+    sys.path.insert(0, str(decision_dir))
+    spec = importlib.util.spec_from_file_location(
+        "decision_server_live", decision_dir / "server.py"
+    )
+    decision_mod = importlib.util.module_from_spec(spec)
+    sys.modules["decision_server_live"] = decision_mod
+    spec.loader.exec_module(decision_mod)
+    record_manager_decision = decision_mod.record_manager_decision
+    query_manager_decisions = decision_mod.query_manager_decisions
+
+    rec = record_manager_decision.fn if hasattr(record_manager_decision, "fn") else record_manager_decision
+    qry = query_manager_decisions.fn if hasattr(query_manager_decisions, "fn") else query_manager_decisions
+    sample = {
+        "project_name": "cognitive-lead-hq",
+        "session_id": "999",
+        "verbatim_quote": {
+            "original": "تست زنده سیستم با جمینای و تلگرام انجام شد",
+            "english_translation": "Live system test with Gemini and Telegram completed successfully",
+        },
+        "extracted_decision": {
+            "summary": "Live smoke verification of FastMCP servers",
+            "category": "tooling",
+            "rationale": "Verify bot and OpenRouter credentials",
+            "alternatives": [],
+            "tradeoffs": "None",
+        },
+    }
+    confirmation = rec(sample)
+    print(f"  PASS {confirmation}")
+    matches = qry("Gemini")
+    assert "DEC-" in matches, f"Query missed the recorded decision: {matches[:200]}"
+    print(f"  PASS Query match verified: {matches[:100]}...")
+
+
+def main() -> int:
+    """Run all four live checks in order; return exit code."""
+    print("=" * 60)
+    print("  Cognitive Lead AI — Live System Verification")
+    print("=" * 60)
+    check_telegram()
+    check_llm()
+    check_persona_dispatch()
+    check_decision_store()
+    print("\n" + "=" * 60)
+    print("  ALL LIVE TESTS PASSED SUCCESSFULLY! (Exit 0)")
+    print("=" * 60)
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index c127bd8..2dd112b 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -16,6 +16,7 @@ Run: `pytest tests/test_decision_server.py -v` (repo root).
 
 import importlib
 import json
+import os
 import shutil
 import sys
 import types
@@ -241,3 +242,31 @@ def test_extract_parses_stubbed_llm_json(srv, tmp_path, monkeypatch):
     call = srv.extract_session_decisions
     target = call.fn if hasattr(call, "fn") else call
     assert target(1, transcript_path=str(transcript)) == candidates
+
+
+def test_load_env_files_from_cwd_and_never_overrides(srv, tmp_path, monkeypatch):
+    (tmp_path / ".env").write_text(
+        "DECISION_TEST_PROBE=probe-value-456\n", encoding="utf-8"
+    )
+    monkeypatch.chdir(tmp_path)
+    monkeypatch.delenv("DECISION_TEST_PROBE", raising=False)
+    srv._load_env_files()
+    assert os.environ.get("DECISION_TEST_PROBE") == "probe-value-456"
+    monkeypatch.setenv("DECISION_TEST_PROBE", "keep-me")
+    srv._load_env_files()
+    assert os.environ.get("DECISION_TEST_PROBE") == "keep-me"
+
+
+def test_load_env_files_parent_fallback_without_cwd(srv, tmp_path, monkeypatch):
+    # Same regression as persona server: no cwd .env → install-root .env.
+    fake_root = tmp_path / "install"
+    fake_server = fake_root / "mcp-decision-server"
+    fake_server.mkdir(parents=True)
+    (fake_root / ".env").write_text("DECISION_PARENT_PROBE=from-parent\n", encoding="utf-8")
+    empty_cwd = tmp_path / "elsewhere"
+    empty_cwd.mkdir()
+    monkeypatch.chdir(empty_cwd)
+    monkeypatch.delenv("DECISION_PARENT_PROBE", raising=False)
+    loaded = srv._load_env_files(server_dir=fake_server)
+    assert loaded is not None and loaded.endswith(".env")
+    assert os.environ.get("DECISION_PARENT_PROBE") == "from-parent"
diff --git a/tests/test_persona_server.py b/tests/test_persona_server.py
index ce8b171..a097736 100644
--- a/tests/test_persona_server.py
+++ b/tests/test_persona_server.py
@@ -17,6 +17,7 @@ Run: ``pytest tests/test_persona_server.py -v`` (repo root).
 
 import importlib
 import json
+import os
 import sys
 import types
 from pathlib import Path
@@ -241,9 +242,9 @@ def test_env_fallback_defaults(server_mod, monkeypatch):
         "PERSONA_MAX_TOKENS",
     ):
         monkeypatch.delenv(var, raising=False)
-    assert server_mod._get_persona_model() == "openrouter/google/gemini-3.8-flash"
+    assert server_mod._get_persona_model() == "openrouter/deepseek/deepseek-v4-flash-0731"
     assert server_mod._get_reasoning_effort() == "high"
-    assert server_mod._get_temperature() == 0.2
+    assert server_mod._get_temperature() == 1.0
     assert server_mod._get_max_tokens() == 16384
 
 
@@ -261,7 +262,7 @@ def test_env_overrides_respected(server_mod, monkeypatch):
 def test_env_invalid_numeric_falls_back(server_mod, monkeypatch):
     monkeypatch.setenv("PERSONA_TEMPERATURE", "not-a-float")
     monkeypatch.setenv("PERSONA_MAX_TOKENS", "not-an-int")
-    assert server_mod._get_temperature() == 0.2
+    assert server_mod._get_temperature() == 1.0
     assert server_mod._get_max_tokens() == 16384
 
 
@@ -483,3 +484,38 @@ def test_session_lineage_no_duplicate_instruction(sess, tmp_path):
         180, "QA Engineer", "do the other thing", None, repo_root=tmp_path
     )
     assert messages2[-1] == {"role": "user", "content": "do the other thing"}
+
+
+def test_load_env_files_from_cwd_and_never_overrides(server_mod, tmp_path, monkeypatch):
+    (tmp_path / ".env").write_text(
+        "# comment\nPERSONA_TEST_PROBE=probe-value-123\n"
+        "QUOTED='spaced value'\nMALFORMED-LINE\n",
+        encoding="utf-8",
+    )
+    monkeypatch.chdir(tmp_path)
+    monkeypatch.delenv("PERSONA_TEST_PROBE", raising=False)
+    monkeypatch.delenv("QUOTED", raising=False)
+    server_mod._load_env_files()
+    assert os.environ.get("PERSONA_TEST_PROBE") == "probe-value-123"
+    assert os.environ.get("QUOTED") == "spaced value"
+    # Real process env always wins: files never override it.
+    monkeypatch.setenv("PERSONA_TEST_PROBE", "keep-me")
+    server_mod._load_env_files()
+    assert os.environ.get("PERSONA_TEST_PROBE") == "keep-me"
+
+
+def test_load_env_files_parent_fallback_without_cwd(server_mod, tmp_path, monkeypatch):
+    # Regression: opencode may launch servers with a cwd that holds no .env
+    # (this exact gap caused the post-restart 401). The file next to the
+    # install root (<server-dir>/../.env) must still be found.
+    fake_root = tmp_path / "install"
+    fake_server = fake_root / "mcp-persona-server"
+    fake_server.mkdir(parents=True)
+    (fake_root / ".env").write_text("PERSONA_PARENT_PROBE=from-parent\n", encoding="utf-8")
+    empty_cwd = tmp_path / "elsewhere"
+    empty_cwd.mkdir()
+    monkeypatch.chdir(empty_cwd)
+    monkeypatch.delenv("PERSONA_PARENT_PROBE", raising=False)
+    loaded = server_mod._load_env_files(server_dir=fake_server)
+    assert loaded is not None and loaded.endswith(".env")
+    assert os.environ.get("PERSONA_PARENT_PROBE") == "from-parent"
```
<!-- END_GIT_DIFF -->
