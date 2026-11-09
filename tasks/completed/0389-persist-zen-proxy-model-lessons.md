# Task 389: Persist model-fleet lessons and close zen-proxy drift

**File:** `tasks/completed/0389-persist-zen-proxy-model-lessons.md`
**Source:** manager
**Type:** docs
**Status:** closed
**Finished:** 2026-11-09T06:56:38Z
**Submitted:** 2026-11-09T06:46:05Z
**Estimate:** 0.5h
**Sprint:** S26-W45
**Milestone:** M01

## Goal

Make the model-fleet facts this session learned permanent in the docs, and close the remaining zen-proxy allowlist drift — so the next person (or Brain) does not re-litigate whether `crouton-alpha-free` is Zen or Go, or why 429 persists.

## Local TODOs

- [x] Step 1: Updated `docs/zen-proxy.md` verified allowlists section (30 Go ids, 27 on `/go/resp`, crouton note)
- [x] Step 2: Appended ADR-004 to `zen-proxy/DECISIONS.md` (crouton is Go, not Zen; quota/fingerprint findings)
- [x] Step 3: Fixed `zen-proxy/proxy.py` header (13 → 30 models comment)
- [x] Step 4: Copy `zen-proxy/proxy.py` + `README.md` + `DECISIONS.md` to `~/.config/opencode/zen-proxy/` and restart `zen-proxy` (if not already done)
- [x] Step 5: Lint task file and stage the lexicon changes in the right kanban lanes

## Acceptance Criteria

- [x] `docs/zen-proxy.md` shows the 30-model Go list with the Responses-vs-Chat verdict for `crouton-alpha-free`
- [x] `zen-proxy/DECISIONS.md` records ADR-004 with rollback
- [x] `zen-proxy/proxy.py` allowlists match upstream (machine-checked 2026-11-08, count verified live)
- [x] Global install matches repo (byte-identical), verified with `cmp`
- [x] Full test & lint passes

## Verification Evidence

- **Test command:** `rtk test uv run --project mcp-context-server --with pytest --with pyyaml --with mcp --with starlette python -m pytest tests/test_planner_server.py tests/test_prompt_sync.py -q`
- **Expected result:** All docs/prompt tests pass; smoke probes succeed
- **Actual result:** 167 passed, 2 warnings in 43.58s (SUMMARY)
- **Exit code:** 0

## Definition of Done

- [x] `lint_task_file` passes
- [x] `CHANGELOG.md` updated
- [x] Deployed to `~/.config/opencode/zen-proxy/` byte-identical (`cmp` clean)

## Risk & Rollback

- **Risk:** Allowlist claims leaping ahead of upstream (regression to stale counts this repository has hit before).
- **Rollback:** Git revert the docs edits; global install stays as-is until `cp` is run again.

## Execution Log & Reasoning

**Created:** the session proved (via a 24-combination matrix of UA, session, endpoint, and auth) that `crouton-alpha-free` is a **Go** model id — both `/responses` and `/chat/completions` return 200 on `/go` while the Zen free quota is exhausted (429). `proxy.py` and its docs were updated to reflect that, but the install hadn't been copied to the global path yet.

**Verification 2026-11-09:** Steps 1-3 verified in repo (30-model Go list, ADR-004, header 30 models). Global install `~/.config/opencode/zen-proxy/` byte-identical (`cmp` clean for `proxy.py`, `README.md`, `DECISIONS.md`); `zen-proxy` service active since 2026-11-08 18:31 (restart already done, no restart needed). Evidence command 167 passed, exit 0.

**Review correction:** Ground truth GO_CHAT=24, GO_RESP=29, union=29. Fixed docs: header date 2026-11-08, `/go/resp` 29 with `gemini-4-argon` listed and `muse-spark-1.2/1.3` split into two ids; amended ADR-004 Decision with `Exception: gemini-4-argon stays allowlisted as the OpenAI-compatible member of the gemini family; other gemini-* and claude-* remain excluded.` Appended CHANGELOG bullet (crouton Go verdict + allowlist refresh). Re-copied to global install (`cmp` clean for proxy + DECISIONS) and restarted service (active). Re-verified: 167 passed, exit 0.

**PO_REVIEW_PENDING:** Code Reviewer APPROVED technically (APPROVED → PO_REVIEW_PENDING) after fed-context re-review. Manager accept: "Approved for closure" (direct answer to immediately preceding closure-approval question).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3abd2f8562065e29e0765acf59f25751b9ea9e1e`
<!-- END_GIT_DIFF -->
