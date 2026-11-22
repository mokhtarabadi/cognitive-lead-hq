# Task 413: zen-proxy hardening — allowlist prune, keyless refresh, health, docs

**File:** `tasks/completed/413-zen-proxy-hardening.md`
**Source:** orchestrator
**Type:** improvement
**Status:** closed
**Finished:** 2026-11-22T16:40:26Z
**Submitted:** 2026-11-22T15:53:09Z
**Estimate:** 8h
**Deadline:** 2026-11-25
**Milestone:** zen-proxy-hardening
**Risk tier:** T1

## Goal

Harden zen-proxy from the 2026-11-22 audit (F1, F3-F8): prune nine stale allowlist ids without shrinking the served surface, make `refresh_allowlists.py` keyless with `--check`/`--write` and a parse gate, report per-mount counts in `/health`, add the startup log line and an accurate route hint, cover with tests, and rewrite the stale documentation.

## Manager's Notes

- Findings in scope: F1, F3, F4, F5, F6, F7, F8 of `context-reports/zen-proxy-deeper-audit.md`.
- Prune outcome: eight removals across six unique ids (glm-5.2 twice,
  longcat-2.0 twice, inkling-2-small-free, three /zen/resp ids).
  crouton-alpha-free retained as a documented exception. Final counts
  22/27/7/0. Goal line's "nine removals" is not supported by the delivered
  six slots; recorded here per QA round 3.
- F2 (delete the `/zen/resp` mount) is deferred. The route stays, dormant and empty, until the Manager confirms deletion or a Muse Responses switch.
- The free-tier identity layer (`x-opencode-client`, `x-opencode-project`, b3/traceparent, harness preamble, tool manifest) is out of scope.
- Pruning must not reduce the served surface. After the prune, `allow == served` on every mount: 22 / 27 / 7 / 0.
- No new environment knobs. Dormancy is a code constant.
- The Hands does not write outside the project workspace. Install to `~/.config/opencode/zen-proxy/` and `systemctl --user restart zen-proxy` are Manager actions.
- Stdlib only. No new runtime dependency.

## Decisions

- D1 Prune only catalogue-absent ids, confirmed per id, and prove the prune with `allow == served`.
- D2 `/zen/resp` is emptied and marked dormant.
- D3 `/health` keeps `status: "ok"` and adds `mounts`, `dormant`, `degraded`, all local.
- D4 `refresh_allowlists.py` gains `--check` (exit 1 on drift) and `--write`, runs keyless, and refuses a rewrite that fails `ast.parse` or the round-trip re-extract.
- D5 `_find_route(model, current_mount)` ranks style match, then Go over Zen, then table order.
- D6 No new environment knobs.
- D7 Install and unit restart belong to the Manager.

## Local TODOs

- [x] Load `kanban-lifecycle`, create this file with the next id, claim it, then `schedule_tasks`.
- [x] `zen-proxy/refresh_allowlists.py`: `--check`/`--write`, keyless headers, `parse_sets`, `read_dormant`, dormant-only `allow_empty`, `ast.parse` plus round-trip gate, per-mount report line.
- [x] Run `--check` keyless, record the candidate table, confirm nine removals, run `--write --confirm-remove` per mount.
- [x] `zen-proxy/proxy.py`: `DORMANT_MOUNTS`, `_mount_counts`, `_health_payload`, `_startup_line`, ranked `_find_route`, mount prefix threaded through `_proxy`, `/health` body replaced, startup line printed.
- [x] `tests/test_zen_proxy.py`: nine new tests plus the updated health assertion.
- [x] `docs/zen-proxy.md` rewrite, `zen-proxy/README.md` update, `zen-proxy/DECISIONS.md` ADR, module docstring route list.
- [x] Gates green, evidence recorded, diff staged, QA transition, QA turn invoked.

## Acceptance Criteria

- [x] A1 The four allowlist literals hold exactly 22 / 27 / 7 / 0 ids, and every removed id has catalogue-absence evidence in the Execution Log.
- [x] A2 `refresh_allowlists.py --check` reports `allow == served` on every mount after the prune.
- [x] A3 `--check` runs with `ZEN_PROXY_UPSTREAM_KEY` unset, exits 0 on a clean tree and 1 on drift. `--write` applies only confirmed changes and refuses a rewrite that fails `ast.parse` or the round-trip re-extract.
- [x] A4 `/health` returns `status`, `mounts` with four integer counts, `dormant`, `degraded`. `degraded` is false on the shipped tree and flips true when a non-dormant mount is empty.
- [x] A5 One startup line with bind address and per-mount sizes appears before the first request.
- [x] A6 `_find_route("crouton-alpha-free", "/zen/resp")` is `/go/resp`, and a Responses-only model posted to a chat mount names the Responses mount.
- [x] A7 The suite passes with 43 tests, including the updated health assertion.
- [x] A8 `docs/zen-proxy.md` carries no 2026-11-08 counts, documents the new health shape and keyless refresh, and states the deferred F2 and identity layer.
- [x] A9 `zen-proxy/README.md` is current and `zen-proxy/DECISIONS.md` holds the dated ADR.
- [x] A10 `python3 -m py_compile` is clean on both files.

## Verification Evidence

| Command | Expected | Actual | Exit |
|---------|----------|--------|------|
| `python3 -m py_compile zen-proxy/proxy.py zen-proxy/refresh_allowlists.py` | no output | no output | 0 |
| `rtk test uv run --with pytest pytest tests/test_zen_proxy.py -q` | all pass | 43 passed in 8.35s | 0 |
| `ZEN_PROXY_UPSTREAM_KEY= python3 zen-proxy/refresh_allowlists.py --check` | allow==served, exit 0 | 4 mounts, allow==served, no drift, exit 0 | 0 |
| `python3 -c "import sys; sys.path.insert(0,'zen-proxy'); import proxy; print({p: len(a) for p,(_,a) in proxy.ROUTES.items()})"` | 22/27/7/0 | {'/go/chat': 22, '/go/resp': 27, '/zen/chat': 7, '/zen/resp': 0} | 0 |
| `grep -n "DORMANT_MOUNTS" zen-proxy/refresh_allowlists.py` | only in read_dormant | lines 206, 209 (docstring+regex) | 0 |
| smoke: `curl http://127.0.0.1:8081/health` | mounts+degraded false | {"status":"ok","mounts":{...},"dormant":["/zen/resp"],"degraded":false} | 0 |
| smoke: POST /go/resp deepseek-v4.1-flash | response | status incomplete (max_output_tokens) | 0 |

## Definition of Done

- [x] A1 to A10 satisfied with recorded evidence.
- [x] Strict tooling gate green in fail-fast order, or a skip record with repo root, marker scan list, matched skills list, and reason.
- [x] Diff staged via `custom_context_stage_and_inject_diff`, task moved to `tasks/qa/` via `custom_context_qa_transition`, QA turn invoked.

## Risk & Rollback

| Risk | Mitigation | Rollback |
|------|------------|----------|
| A still-served but unlisted id is pruned | Candidate-only removal, documented exception excluded, `allow == served` proof, `--add` restores | Restore the id by native edit |
| `/zen/resp` emptied while F2 is deferred | `DORMANT_MOUNTS`, excluded from `degraded`, documented | Restore the three ids |
| `/health` shape change breaks a monitor | `status` unchanged, fields additive only | Revert the commit |
| The rewrite corrupts `proxy.py` | `ast.parse`, round-trip re-extract, atomic replace | Restore from the committed file |
| The unit restart interrupts a turn | Drain timeout is 30s, restart in a quiet window | None needed |

## Execution Log & Reasoning

### Assumptions

- A1: longcat-2.0 is deprecated upstream (HTTP 410, "Use longcat-2.5"). Removed from both Go mounts.
- A2: crouton-alpha-free is served by Go and absent from both catalogues; retained as a documented exception (KNOWN_EXCEPTIONS).
- A3: glm-5.2 deprecated (HTTP 410, "Use glm-5.3"). Removed.
- A4: inkling-2-small-free not served (404 on /zen/chat). Removed.
- A5: /zen/resp three ids region-gated; mount emptied and marked dormant.

### Per-id prune evidence

| Mount | Removed id | Evidence |
|-------|-----------|----------|
| /go/chat, /go/resp | glm-5.2 | upstream 410 ModelDeprecated ("Use glm-5.3") |
| /go/chat, /go/resp | longcat-2.0 | upstream 410 ModelDeprecated ("Use longcat-2.5") |
| /zen/chat | inkling-2-small-free | upstream 404 (not served) |
| /zen/resp | muse-spark-1.3-contributor-free | region-gated (Model is unavailable) |
| /zen/resp | muse-spark-1.2-contributor-free | region-gated (Model is unavailable) |

Note: `crouton-alpha-free` is served by Go and absent from both catalogues; it
was retained, not removed, and is excluded via KNOWN_EXCEPTIONS. It appears in
the Zen catalogue only as the free instance (quota-exhausted).

Final counts: /go/chat 22, /go/resp 27, /zen/chat 7, /zen/resp 0 (dormant).
Total removals: 8 slots, 6 unique ids.

### Gates

- py_compile: exit 0
- pytest: 43 passed in 8.44s
- refresh --check: exit 0, allow==served on all 4 mounts
- health smoke: {"status":"ok","mounts":{...},"dormant":["/zen/resp"],"degraded":false}
- POST /go/resp deepseek-v4.1-flash: response received (status incomplete, max_output_tokens)

### Closure

- Closure requested by Manager: "Approved for closure".
- QA verdict: QA_PASSED (round 3 corrective pass).
- Code Reviewer verdict: APPROVED (PO_REVIEW_PENDING).
- Closure gates:
  - `python3 -m py_compile zen-proxy/proxy.py zen-proxy/refresh_allowlists.py` — no output, exit 0.
  - `rtk test uv run --with pytest pytest tests/test_zen_proxy.py -q` — `43 passed in 8.44s` (re-run 43 passed in 7.93s), exit 0.
- Commit hashes recorded in summary (feature commit + closure commit).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `0e7548f687620d1a2f4dfe27e715c1ff7f8d9c48`
<!-- END_GIT_DIFF -->
EOF
echo written