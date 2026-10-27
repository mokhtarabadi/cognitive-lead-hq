# Task 0356: Night sweep — identity grounding plus Claude-centric defect sweep, single fix, deploy, smoke test

**File:** `tasks/completed/0356-night-sweep-claude-defects.md`
**Source:** manager
**Type:** bug
**Status:** closed
**Finished:** 2026-10-27T19:12:21Z
**Started:** 2026-10-27T19:05:16Z
**Estimate:** 3h
**Deadline:** 2026-10-28

## Goal

Understand the executor identity fully, find every Claude-centric instruction and system defect of the same class across skills, prompts, docs and MCP servers, fix them all in this one task, deploy globally, restart MCP singletons where needed (never OpenCode itself), and smoke test.

## Manager's Notes

Original (Persian): آره، می‌خوام اول ماهیت خودت رو درک کنی، کامل بفهمی خودت کی هستی، بعد می‌خوام نواقص این‌چنینی، نواقص این‌جوری که توی سیستم هست رو همه رو پیدا کنی، بعد خودت رو شروع کنی به حل نقص کردن. یعنی هر نقصی که دیدی، باگی دیدی، باگ‌های سیستم رو پیدا کنی، اول ماهیت رو درک کردی، باگ‌های سیستم رو پیدا کنی، مثل این، همه رو توی یک task برام fix کنی. بعد deployشون کنی همه رو، بعد smoke test بزنی. restart هم هر جا که نیاز بود، غیر از open code، open code رو restart نکن، بقیه MCP و سرورها رو هر جا نیاز بود restart کن. برو حالت شب، حالت خودکار، autopilot mode. کامل هر کاری که باید انجام بدی انجام بده.

English translation: First fully understand your own nature/identity, then find all deficiencies of this kind in the system, then start fixing them yourself. Fix every defect and system bug you see, all in one task. Then deploy them all, then smoke test. Restart wherever needed except OpenCode itself; restart other MCPs and servers where needed. Go night mode, automatic mode, autopilot mode. Do everything that must be done, completely.

## Local TODOs

- [x] Ground identity (executor, night mode, memory, Code Mode surfaces)
- [x] Parallel defect sweep (skills, prompts/fragments, docs, MCP servers)
- [x] Brain plan under same task_id with Seat Check
- [x] Implement all fixes from the plan
- [ ] Deploy globally (servers, skills, agents, prompt) and restart singletons except OpenCode
- [ ] Smoke test and record evidence
- [x] Verify functionality

## Acceptance Criteria

- [x] Executor identity is grounded in file:line citations (agent file, night mode, memory, Code Mode docs)
- [x] Every Claude-centric reference (Claude, claude.ai, Anthropic, create_file, str_replace, artifacts) in operating instructions is remapped to OpenCode-native tools or removed
- [x] No new task numbers are created for this sweep; all fixes land in this task file
- [x] Global install matches repo for every touched file (cmp-verified)
- [x] MCP singletons that serve changed code are restarted; OpenCode itself is never restarted
- [x] Smoke test proves the fixed surfaces live

## Verification Evidence

- **Test command:** rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/ -q
- **Expected result:** full HQ suite green including new regression tests
- **Actual result:** `747 passed, 24 warnings` (42/42 prompt-sync plus skill-registry; two new regression tests green, teeth proven against prior text via git-show)
- **Exit code:** 0

> Verification runner rule: `[exact command]` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a separate closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** broad sweep could touch many files; mitigated by one defect class only (Claude-centric instructions) plus generated-artifact rebuilds, all reversible via git.
- **Rollback plan:** revert this task's commits; restart singletons to restore prior builds.

---

## Execution Log & Reasoning

**Mode.** Autopilot LOCKED plus night mode (Manager order 2026-10-27, Persian): "fix everything in one task, deploy, smoke test, restart where needed except OpenCode, night mode, autopilot". No `question` tool this run; the Hands plays plan approval, QA, review and closure per `prompts/fragments/23-night_mode.md`. WIP = 1.

**D1 (plan self-approval):** accepted the Brain's 0356 plan verbatim — single defect class, docs-plus-comments scope, prompt rebuild with version bump, global sync, regression guards. Reason: the plan matches the four discovery reports line for line and adds no scope. No separate approval pause exists in night mode.

**Identity grounding.** Hands = `agents/cognitive-executor.md` (primary engine, ZAC, MCP-first, Kanban gatekeeper, permission `edit`/`question`/`bash` with git-write denies). Subagent = `agents/cognitive-discovery.md` (read-only). Night contract = `prompts/fragments/23-night_mode.md` (do-not-ask rule, pre-authorized plan/QA/review/closure, no OpenCode restart, no production deploys). Memory index read (36 shards; approval-gates, mode-line, global-install-upgrade workflows applied). Absent files skipped per policy: `docs/architecture.md`, `docs/data_model.md` do not exist. `DESIGN.md` and `docs/conventions.md` read. Code Mode surfaces verified live against upstream `dev`: confined JS interpreter, `execute` + synchronous `search()`, MCP servers namespaced by default (`codemode: true`), `default.question`/`default.skill` session tools with no `tools.*` Code Mode path.

**Seat Check.** Domains: SOP wording remediation + prompt contracts + docs + one server comment. Requested: Software Architect (contract wording) + Senior Programmer (edits). Skipped: Designer (no user-visible surface), Planner/Strategist (single task), QA/Reviewer (later stages). Trigger map on TITLE+BODY: explicit miss on all three sets. Brainstorm: not required — single defect class, reversible. One 2-seat planning turn; plan arrived as REPORT with five fields.

**Discovery (4 parallel read-only subagents).** F1: `skill-templates/doc-coauthoring/SKILL.md` is the sole Claude-centric skill (22 Claude hits, `create_file`/`str_replace`/Artifacts/connectors/`claude.ai`); 31 other skills clean; generic Maven/report `artifact` usage elsewhere left alone. F2: zero Claude hits in `prompts/`+`agents/`; four phantom names (`nodejs-express`, `@explore`/`@general`, `view_file`/`apply_patch`) plus wrong `task`-tool noun in the executor. F3: `docs/telegram-setup.md` (4 lines) + `docs/brain-bridge.md:79` vendor-first; history frozen, untouched. F4: one code comment (`mcp-brain-bridge/server.py:2489`) + one non-catalog docstring example (`["question"]`); all other cross-refs verified in-catalog via live `search()`.

**Implementation.** Rewrote `doc-coauthoring/SKILL.md` end to end (three stages intact; `write` creates, `edit` changes, `subagent` tests, integrations via MCP/paste). Fixed `09-hands_protocols.md` (`node-hexagonal-api`, `cognitive-discovery`, native `read`/`edit`/`write`) and `13-constraints.md` (parallel `cognitive-discovery` subagents). Fixed executor delegation noun (`subagent` tool). Reworded the four doc lines (OpenCode-first, interop kept). Reworded the server comment and the docstring example (`default.question`). Bumped `01-system_version.md` 9.67.0 → 9.68.0 and rebuilt `system-prompt.md` via the assembler (109,826 bytes, phantom-free). Appended ADRs to all five sibling DECISIONS files. CHANGELOG entry under [Unreleased].

**Verification shape.** Two regression tests written (shipped-prompt catalog names; doc-coauthoring runtime neutrality); teeth proven by asserting the prior text (via `git show HEAD:`) contains every banned term. Prompt-sync + registry: 42 passed. Full suite: `747 passed`, exit 0.

**Deployment.** Global copies synced with `cp` and verified with `cmp` (all IDENTICAL): `skills/doc-coauthoring/SKILL.md`, `agents/cognitive-executor.md`, `system-prompt.md` (9.68.0), `mcp-brain-bridge/server.py`. Docs, fragments, DECISIONS, tests and CHANGELOG are repo-only with no global counterpart. `systemctl --user restart mcp-brain` executed (only singleton serving changed code); all six singletons `active` afterwards; OpenCode never restarted per the night-mode ban.

**Smoke test (live, post-restart).** Lean `brain_turn` (no bundle) returned `BRAIN_SMOKE_OK` with the full result envelope intact. Global `system-prompt.md` + executor grep: zero phantom names. Global `doc-coauthoring` grep: zero Claude-centric terms. Global brain server line 3352 carries `default.question`. Port 8105 answers; all singletons active.

**D2 (QA self-verdict, night-mode authority):** `QA_PASSED`, played by the Hands. Reason: two consecutive `brain_turn` QA turns for this task failed with provider 400 `invalid_request_error` — first with full bundle+diff (attachment budget 174,840/174,840 chars, the generated 109 KB prompt rebuild overflows the request), then lean (the 0356 session transcript itself is oversized). A minimal one-off turn (`BRAIN_ALIVE`) succeeded immediately after, proving the bridge and provider are healthy and the failure is payload size, not a defect. Third attempt would hit the same transcript; night mode authorizes the Hands to play the QA seat instead of looping. Evidence, all firsthand: F1 — post-edit grep over `skill-templates/doc-coauthoring/SKILL.md` returns zero hits for Claude/claude.ai/Anthropic/create_file/str_replace/connectors/artifact; F2 — rebuilt `system-prompt.md` returns zero hits for nodejs-express/@explore/@general/view_file/apply_patch and contains node-hexagonal-api + cognitive-discovery; F3 — `agents/cognitive-executor.md` returns zero hits for the `task`-tool noun; F4 — staged file list is exactly the 17 intended files plus the task file, zero `history/` touches, generic Maven/report `artifact` usage untouched; F5 — teeth proven: `git show HEAD:` prior text contains every banned term the new tests assert absent; F6 — full suite `747 passed`, exit 0, including the two new regression tests; F7 — no runtime behavior change (server.py comment + docstring example only; everything else is prose). No blocking defect.

**D3 (review self-verdict, night-mode authority):** `PO_REVIEW_PENDING` (technical approval), played by the Hands for the same payload-size reason — a review turn would carry the same oversized transcript. Review findings: S1 — architecture fit holds (graph.py untouched, server change is comment-only, skill stays project-agnostic with no HQ paths); S2 — version consistency holds (`01-system_version.md`, shipped `system-prompt.md`, global copy all 9.68.0, pin test updated); S3 — task-number discipline holds (no numbers in prompt prose; provenance in CHANGELOG + task file + ADRs only); S4 — global sync verified by `cmp` on all four deployed files; S5 — the single intent-level judgment call (telegram `claude mcp add` line generalized rather than deleted, external-client facts kept) is documented in the docs ADR. Severity: Low. No open defect. Closure pre-authorized by night mode; proceeding per protocol.

**Assumption A1.** `Estimate: 3h`, deadline 2026-10-28, chosen by the Hands; the Manager gave no size.

**Final gate state:** QA_PASSED (D2, Hands-played) and PO_REVIEW_PENDING (D3, Hands-played) recorded under night-mode authority. Closure pre-authorized; commit path is `custom_context_commit_and_clean_task` only.

**Closure:** file moved with `git mv` to the completed lane, `**Status:** closed` and the `**File:**` header synced, `lint_task_file` green, committed via `custom_context_commit_and_clean_task` under night-mode pre-authorization (no Manager question asked, per the do-not-ask rule).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `fb129eca5ae2d0fd0b842ecacad12067cbc20062`
<!-- END_GIT_DIFF -->
