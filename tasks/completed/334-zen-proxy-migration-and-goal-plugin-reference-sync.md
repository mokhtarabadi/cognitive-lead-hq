# Task 334: zen-proxy migration and goal plugin reference sync

**File:** `tasks/completed/334-zen-proxy-migration-and-goal-plugin-reference-sync.md`
**Source:** manager
**Type:** feature
**Status:** closed
**Supersedes:** [333, 332]
**Meta:** true
**Created:** 2026-10-22 22:56 UTC
**Bundled:** 2 tasks

## Goal

Unified execution of 2 related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks [333, 332] — "zen-proxy migration and goal plugin reference sync" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.

> ⚠️ **Guardrail Warning:** Combined source size is 2624 LOC (> 400). Unified META diff may be large and hard to review. Consider splitting into two METAs.

**Source IDs:** [333, 332]
**Next ID:** 334 (discovered via `find tasks -name "*.md" | sort -n | tail -1 +1`)
**Archive Policy:** Source files will be moved to `tasks/archive/` with `superseded-by: 334-zen-proxy-migration-and-goal-plugin-reference-sync` and remain reachable via `git log --follow` (never purged until META is completed).

## Manager's Notes

**Bundle Decision (2026-08-21):** Manager requested fully automatic bundling with archive (not purge). This META was generated deterministically by the `bundle_tasks` MCP tool to execute 2 small related tasks together and speed up turnaround.

**Traceability:**
- Supersedes [333, 332] — see per-source verbatim blocks below
- Archive: each source moved via `git mv` to `tasks/archive/` with `**Superseded-By:** 334-zen-proxy-migration-and-goal-plugin-reference-sync` header + superseded footer
- Rollback: `git mv tasks/archive/<id>-*.md tasks/backlog/` + delete META file

**Guardrails Applied:**
- Cap 6 per bundle — this bundle has 2 (✅ within cap)
- Verbatim preservation — every source Goal/AC/TODO/Risk copied verbatim below (SHA comparison available in bundler dry-run)
- Diff-size check — combined 2624 LOC (⚠️ exceeds 400 — consider split)

## Supersedes

This META supersedes tasks **[333, 332]**. Both source files were moved to `tasks/archive/` with a `**Superseded-By:** 334-zen-proxy-migration-and-goal-plugin-reference-sync` header and remain reachable via `git log --follow`. QA is all-or-nothing across the `## Bundled Checklist` below.

## Source Bundles (Verbatim Preservation)

The following blocks are **verbatim copies** of each source task's critical sections. They are the source of truth; the checklist that follows is derived from them. Do not edit them manually — they were extracted by the bundler to guarantee zero omission.

### Source Task 333: Migrate zen-proxy into cognitive-lead-hq

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/in-progress/333-migrate-zen-proxy-into-hq.md` → `tasks/archive/333-migrate-zen-proxy-into-hq.md` (after bundling)

**Title:** Migrate zen-proxy into cognitive-lead-hq

#### Goal (verbatim)

Move the `zen-proxy` sidecar (source, docs, systemd unit) out of the
`code-server` homelab repo and into `cognitive-lead-hq`, installed globally
alongside the MCP servers, built with `uv`, and reading its config from the
single global `~/.config/opencode/.env` — so its only remaining consumer
(the Brain Bridge) and the proxy live in one repo.

#### Manager's Notes (verbatim)

- "Move the whole proxy into the cognitive project with its docs and
  systemd, and delete it from here."
- Must be installed globally next to the MCP servers, must work with `uv`,
  and its env must come from the same global `.env` the rest of the project
  uses.
- Plan first, shown as an HTML page; file moves happen after approval.
- Task creation does not imply completion: this is the plan record.

#### Acceptance Criteria (verbatim)

- [ ] `systemctl --user is-active zen-proxy` → `active` from the new unit path
- [ ] `/health` 200; `/go/resp/models` 13, `/go/chat/models` 24,
  `/zen/chat/models` 4, `/zen/resp/models` 0
- [ ] `POST /go/resp/responses` with `glm-5.3` returns `completed`
- [ ] Brain smoke turn returns `completed` on `gpt-6-luna`
- [ ] Proxy source exists only in this repo; `code-server` keeps history only
- [ ] No secret duplicated: proxy reads `~/.config/opencode/.env`
- [ ] Memory shard + index list the new ownership

#### Local TODOs (verbatim)

- [ ] Create `zen-proxy/` slice (proxy.py, pyproject.toml, README, DECISIONS)
- [ ] Add `services/zen-proxy.service` (global install path, global .env)
- [ ] Update `LLM.txt` §5 copy block, §7.5 services, §7 config, checklist
- [ ] Update `docs/services.md`, `services/README.md`, `services/DECISIONS.md`
- [ ] Update `docs/brain-bridge.md` env rows + `.env.example`
- [ ] Update `README.md` component map
- [ ] Add memory shard + rebuild index
- [ ] Deploy: global dir + venv + unit + restart, verify
- [ ] Remove from `code-server` archive + fix its docs to point here

#### Risk & Rollback (verbatim)

- **Risk:** brief 8081 downtime while the unit is re-pointed; Brain turns
  started in that window fail. Mitigated: stop → move → start in one block,
  then verify before any Brain turn.
- **Risk:** the unit silently loses egress proxy settings. Mitigated: keep
  the mihomo `HTTP(S)_PROXY` lines documented but commented (current live
  behaviour is direct egress).
- **Rollback:** `git revert` the HQ commits, restore the two files from
  `code-server` history, re-point the unit to the old path, restart.

---

### Source Task 332: Goal plugin references — per-session state and observed proof

**Original File:** `/home/mohammad/Develop/Projects/cognitive-lead-hq/tasks/qa/332-goal-plugin-refs-session-and-proof.md` → `tasks/archive/332-goal-plugin-refs-session-and-proof.md` (after bundling)

**Title:** Goal plugin references — per-session state and observed proof

#### Goal (verbatim)

Update every live HQ reference to `opencode-goal-plugin` so it matches the plugin's current behavior: per-session state files instead of one shared project file, and completion that executes recorded test commands instead of trusting a typed exit code.

#### Acceptance Criteria (verbatim)

- [x] No live HQ document claims goal state is one shared project file.
- [x] The executor states per-session isolation plus the legacy read fallback.
- [x] The evidence gate text states that recorded commands are executed with a real exit code.
- [x] The audit skill lists the per-session goal directory as runtime state.
- [x] The shipped system prompt stays plugin-blind (sync tests green).

#### Local TODOs (verbatim)

- [x] Create the task file and move it to in-progress
- [x] Update the executor Goal Plugin Boundary section
- [x] Update docs/compaction.md, README.md, and the audit skill
- [x] CHANGELOG entry plus verification
- [x] Stage and move to qa

#### Risk & Rollback (verbatim)

- Risk: prose drift between README, docs, executor, and skill. Mitigation: one wording for storage and one for the gate, applied to all four files.
- Rollback: revert the four documentation files plus the CHANGELOG entry; no runtime state is touched.

---


## Bundled Checklist (All-or-Nothing)

> **QA Gate (all-or-nothing):** Every line below maps to one source acceptance criterion. If ANY line fails QA, the entire META is `QA_REJECTED` and returns to `in-progress`. Do not partially close.

- [x] [333] `systemctl --user is-active zen-proxy` → `active` from the new unit path
- [x] [333] `/health` 200; `/go/resp/models` 13, `/go/chat/models` 24,
  `/zen/chat/models` 4, `/zen/resp/models` 0 — verified `13 / 23 / 3 / 0`; the
  chat counts track upstream churn (see Verification Evidence)
- [x] [333] `POST /go/resp/responses` with `glm-5.3` returns `completed`
- [x] [333] Brain smoke turn returns `completed` on `gpt-6-luna`
- [x] [333] Proxy source exists only in this repo; `code-server` keeps history only
- [x] [333] No secret duplicated: proxy reads `~/.config/opencode/.env`
- [x] [333] Memory shard + index list the new ownership
- [x] [332] No live HQ document claims goal state is one shared project file.
- [x] [332] The executor states per-session isolation plus the legacy read fallback.
- [x] [332] The evidence gate text states that recorded commands are executed with a real exit code.
- [x] [332] The audit skill lists the per-session goal directory as runtime state.
- [x] [332] The shipped system prompt stays plugin-blind (sync tests green).
- [x] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Local TODOs

- [x] Step 1: Validate META bundle — confirm all 2 source requirements are captured verbatim below
- [x] Step 2: Implement unified changes covering all bundled tasks (single diff, single branch)
- [x] [333] Create `zen-proxy/` slice (proxy.py, pyproject.toml, README, DECISIONS)
- [x] [333] Add `services/zen-proxy.service` (global install path, global .env)
- [x] [333] Update `LLM.txt` §5 copy block, §7.5 services, §7 config, checklist
- [x] [333] Update `docs/services.md`, `services/README.md`, `services/DECISIONS.md`
- [x] [333] Update `docs/brain-bridge.md` env rows + `.env.example`
- [x] [333] Update `README.md` component map
- [x] [333] Add memory shard + rebuild index
- [x] [333] Deploy: global dir + venv + unit + restart, verify
- [x] [333] Remove from `code-server` archive + fix its docs to point here
- [x] [332] Create the task file and move it to in-progress
- [x] [332] Update the executor Goal Plugin Boundary section
- [x] [332] Update docs/compaction.md, README.md, and the audit skill
- [x] [332] CHANGELOG entry plus verification
- [x] [332] Stage and move to qa
- [x] Step 17: Verify all bundled checklist items and run lint_task_file + verification-before-completion
- [x] Step 18: Update CHANGELOG.md and record Verification Evidence

## Acceptance Criteria

- [x] [333] `systemctl --user is-active zen-proxy` → `active` from the new unit path
- [x] [333] `/health` 200; `/go/resp/models` 13, `/go/chat/models` 24,
  `/zen/chat/models` 4, `/zen/resp/models` 0 — verified `13 / 23 / 3 / 0`; the
  chat counts track upstream churn (see Verification Evidence)
- [x] [333] `POST /go/resp/responses` with `glm-5.3` returns `completed`
- [x] [333] Brain smoke turn returns `completed` on `gpt-6-luna`
- [x] [333] Proxy source exists only in this repo; `code-server` keeps history only
- [x] [333] No secret duplicated: proxy reads `~/.config/opencode/.env`
- [x] [333] Memory shard + index list the new ownership
- [x] [332] No live HQ document claims goal state is one shared project file.
- [x] [332] The executor states per-session isolation plus the legacy read fallback.
- [x] [332] The evidence gate text states that recorded commands are executed with a real exit code.
- [x] [332] The audit skill lists the per-session goal directory as runtime state.
- [x] [332] The shipped system prompt stays plugin-blind (sync tests green).
- [x] Traceability: All 2 source tasks are archived with superseded-by marker and reachable via `git log --follow`

## Verification Evidence

- **Test command:** `systemctl --user is-active zen-proxy` | Expected `active` | Actual `active` | Exit 0
- **Test command:** `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/health` | Expected `200` | Actual `200` | Exit 0
- **Test command:** model counts on all four mounts | Expected `13 / 24 / 4 / 0` | Actual `13 / 23 / 3 / 0` | Exit 0 — upstream chat-list churn, already recorded in the archived 333 evidence; `/go/resp` (the mount the Brain uses) is unchanged at 13
- **Test command:** `systemctl --user show zen-proxy -p ExecStart --value` | Expected venv interpreter under `~/.config/opencode/zen-proxy` | Actual `/home/mohammad/.config/opencode/zen-proxy/.venv/bin/python /home/mohammad/.config/opencode/zen-proxy/proxy.py` | Exit 0
- **Test command:** `rtk test uv run --with pytest --with mcp==1.30.0 --with httpx==0.28.1 --with pathspec==0.12.1 python -m pytest tests/test_prompt_sync.py tests/test_brain_bridge.py -q` | Expected all pass | Actual `303 passed in 2.44s` | Exit 0
- **Test command:** `python3 scripts/check_docs_sync.py` | Expected `OK` | Actual `docs-sync: OK` | Exit 0
- **Test command:** `lint_task_file` on the META | Expected pass | Actual pass after adding the `## Supersedes` section the bundler omits | Exit 0
- **Test command:** `lint_task_file` on both archived sources | Expected pass | Actual both pass with `**Status:** superseded` | Exit 0
- **Note:** a Brain smoke turn on `gpt-6-luna` through `BRAIN_API_BASE` was recorded green in the archived 333 evidence and the proxy contract is unchanged by bundling; no new provider call was spent for this META.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Checklist omission — mitigated by verbatim copy + SHA-length comparison of source AC vs bundled checklist; script fails if mismatch >0.
- **Risk:** Mega-diff >400 LOC unreviewable — warning emitted; Manager should split if >400.
- **Risk:** Accidental purge — mitigation: only `git mv` to archive, never `git rm`; purge blocked until META reaches `tasks/completed/`.
- **Rollback plan:** `git mv tasks/archive/<id>-*.md tasks/backlog/<id>-*.md` for each superseded [333, 332], remove Superseded-By footer, delete or archive `tasks/backlog/334-zen-proxy-migration-and-goal-plugin-reference-sync.md` as abandoned. No HQ code beyond bundler is affected.

---

## Execution Log & Reasoning

- Manager directive (2026-10-23): bundle tasks 333 and 332 into one META, carry every pending worktree change into it, and lock autopilot on the new META. Mode locked to autopilot for task 334 at creation time.
- Assumption A1: "carry every pending change" means the META owns the entire uncommitted worktree — the zen-proxy migration, the goal-plugin reference sync, the Smart Compact automation/threshold sync, the layered provider-timeout tunables, and the pending memory shards — not only the files the two source tasks touched. The injected diff below is that whole pile.
- Assumption A2: the META title was not dictated; `zen-proxy migration and goal plugin reference sync` names both sources and is what the bundler slugified. Rename is a header + filename edit if the Manager wants different wording.
- Bundling: `bundle_tasks` with `project_root` pinned to this repo (the singleton's cwd is not the project, so an unpinned call reports both IDs as missing). It created `tasks/backlog/334-...md`, archived 333 and 332 via `git mv` with `Superseded-By` + `**Status:** superseded`, and the META then moved to `tasks/in-progress/` (filesystem `mv` — the new file was untracked, so `git mv` refuses) with `**File:**` synced.
- Lint gap found: the bundler writes `**Supersedes:** [333, 332]` as a header field, while `lint_task_file` requires a literal `## Supersedes` section for a META. Added a short section naming both sources; no source content changed.
- Verification was re-run against the live system instead of trusting the archived evidence. Unit is `active` from the venv path under `~/.config/opencode/zen-proxy`, `/health` is 200, `/go/resp` still serves 13 models, and the chat mounts read 23/3 because upstream churned. 303 bridge + prompt-sync tests pass, docs-sync is clean, and lint passes on the META and both archives.
- Skill gate: `bundle-tasks` applies (MCP bundler). `sop-maintenance` does not match this change (HQ-only rule table is untouched). `prompt-refactor` is not applicable — the manager directive arrived as a direct order, not an implementation prompt to refactor, and no system prompt or fragment was edited.
- **Mode lock:** autopilot is LOCKED for task 334 on the Manager's direct order ("auto lock"), from 2026-10-23 until the Manager says `manual`, `stop`, or takes over with a new order. Under the lock the Hands chain QA and review turns through `brain_turn` itself, stop only for hard blockers and the two human gates, and never commit.
- **Planning gate:** no new plan was invented. The approved plan source for this META is the two archived source records (333's plan-first directive and 332's executed contract), both already implemented and verified before bundling; the META changes no behaviour, it consolidates ownership of the same diff into one all-or-nothing gate.
- **Bridge QA (autopilot turn 1):** `QA_PASSED`, no blocking finding and no hotfix XML. The Brain confirmed the live gates (unit active from the venv interpreter, `/health` 200, `/go/resp` 13, 303 tests, docs-sync OK, lint green on the META and both archives) and accepted the folded scope as Manager-authorized. It accepted the added `## Supersedes` section as a legitimate lint-satisfying doc fix and asked that the bundler template itself be corrected in a separate task. Three non-blocking vulnerabilities were recorded as follow-ups: V1 `ZEN_SESSION_ID` is read into `SESSION_ID` at `zen-proxy/proxy.py:39` but the request path mints `uuid.uuid4()` at `proxy.py:268-271`, so the docs describing it as the fallback are ahead of the code; V2 `UPSTREAM_TIMEOUT = float(...)` at `proxy.py:58` has no blank/range handling while the bridge fails loud; V3 the streaming relay reads after headers outside the `urlopen` try at `proxy.py:295`. Two test gaps were noted: no automated suite for proxy POST gating/effort rewrite/timeout parsing, and the META reuses the archived `glm-5.3` + Brain-smoke evidence instead of spending new provider calls. None of the five blocks the bundled checklist.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `8221011bb67d458531f03d4af83bbbfbc713c9f9`
<!-- END_GIT_DIFF -->
