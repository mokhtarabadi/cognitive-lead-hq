# Task 274: Plugins full V2 status — verify latest, document, no duplicate upstream issues

**File:** `tasks/completed/274-plugins-full-v2-status-verify-latest-document-no-duplicate-upstream-issues.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Bring both OpenCode plugins to full V2 standing: verify latest V2-capable versions installed, file upstream issues only where none exist, update repo docs with exact V2 status.

## Manager's Notes

Manager order (Persian, 2026-09-26): do the needed work politely; be careful with any issue filing; update plugins that truly support V2 fully to V2; update docs as needed. Prior finding corrected during execution: goal-plugin 0.1.52 already contains full V2 adaptation (upstream PR #49 merged 2026-09-14, PR #58 merged/released 2026-09-26) — the earlier "V1-only" assessment was wrong (stale cache copy examined).

## Local TODOs

- [x] Verify installed versions via `opencode plugin list` (goal 0.1.52, dcp 3.2.0) vs npm latest
- [x] Check upstream goal-plugin repo: V2 adaptation already shipped (PR #49, #58); no issue to file
- [x] Check upstream DCP repo: V2-compat threads already open (#627, #628, #631, #632); no duplicate filing
- [x] Update README.md plugin section with exact V2 status per plugin
- [x] Update LLM.txt §7.7 with V2 status + ask-mode note + update procedure
- [x] CHANGELOG.md entry via Parse-Then-Append
- [x] Store memory `opencode_config/plugin_v2_status_2026_09_26`
- [x] Verify functionality

## Acceptance Criteria

- [x] Both plugins confirmed at latest stable with genuine V2 support (goal 0.1.52, dcp 3.2.0)
- [x] No duplicate upstream issues filed (verified existing threads first)
- [x] README.md + LLM.txt state exact V2 status, versions, and update procedure
- [x] `lint_task_file` passes on the active task file
- [x] `verification-before-completion` applied and evidence recorded

## Verification Evidence

- **Test command:** `rtk test opencode plugin list`
- **Expected result:** goal-plugin 0.1.52 + dcp 3.2.0 loaded, zero errors
- **Actual result:** `local.goal-mode.server 0.1.52` + `opencode-dcp 3.2.0` listed; npm view confirms both are latest stable (dcp betas are stale Mar/Apr experiments; goal 0.1.52 released 2026-09-26)
- **Exit code:** 0

> Verification runner rule: `opencode plugin list` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Docs overclaim V2 support if upstream regresses; mitigated by pinning exact versions + PR links
- **Rollback plan:** `git restore README.md LLM.txt CHANGELOG.md`; plugin versions untouched (no installs performed)

---

## Execution Log & Reasoning

Seat Check: single domain (docs + plugin audit) → Code Reviewer seat not needed; executor direct. `Brainstorm: not required — single-domain doc/audit task, no cross-disciplinary ambiguity`.

- Verified `opencode plugin list` → 0.1.52 + 3.2.0; npm confirms latest stable for both.
- Upstream goal-plugin: PR #49 (full V2 adaptation, beta-19425 contract, compaction context, restart recovery) merged 2026-09-14; PR #58 (V2 task recovery scoping) merged + released as 0.1.52 on 2026-09-26. No issue filed — nothing to ask.
- Upstream DCP (Opencode-DCP/opencode-dynamic-context-pruning): 20 open issues incl. active V2 threads #627 (v2 compat), #628 (/dcp-compress V2 palette), #631 (V2 setup), #632 (V2 compact tags). No duplicate filed — manager's compress flakiness matches known in-flight V2 work.
- Assumption A1: V2 host resolves npm packages at runtime (no extracted dist on disk; cache dirs metadata-only) — `plugin list` is source of truth. Reason: exhaustive find showed no dist/server.js for either plugin while list reports loaded versions.
- Docs updated: README.md plugin bullets + LLM.txt §7.7 V2 status/ask-mode/update procedure.
- Memory stored: `opencode_config/plugins_full_v2_status_2026_09_26` (no supersession — search found no prior plugin-status memory).
- Round 4 (post-verification edits): fixed `**File:**` header to in-progress path; README V2 paragraph now cites exact versions (goal 0.1.52 PR #49/#58, dcp 3.2.0, betas stale), `plugin list` as source of truth, and no-duplicate issue policy; LLM.txt §7.7 gained "Plugin V2 status" subsection; CHANGELOG [Unreleased] bullet added. Lint: task + README + LLM.txt + CHANGELOG all pass.
- Round 5 (Brain QA QA_PASSED + 2 nits fixed): added `### Added` under `[Unreleased]` (bullet no longer sits bare under the version header); README DCP bullet now reads `@latest (currently 3.2.0)` so it matches the pinned paragraph without misrepresenting the `@latest` config entry.
- Round 6 (Brain review + closure): Code Reviewer turn returned APPROVED with status PO_REVIEW_PENDING — "Code approved technically. PO, please review UX/Business logic. Reply Approved for closure to commit and finish." Relayed verbatim to Manager; Manager replied with the exact accept phrase "Approved for closure". File verified still in `tasks/qa/` before closure move.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `41e90839def94202fb1481699cdda434da80faf5`
<!-- END_GIT_DIFF -->
