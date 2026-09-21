# Task 267: docs: manager-decisions MCP tool schemas and usage contract for agents

**File:** `tasks/completed/267-manager-decisions-mcp-tool-schemas.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Write `docs/manager-decisions.md`: the source-verified schema and usage
contract for the six `manager_decisions` MCP tools, so any agent can call
them correctly on the first try. Every claim is grounded in the server
source (`mcp-decision-server/server.py`, `redactor.py`, `detector.py`) with
`file:line` citations. Cross-link the new doc from `README.md` and
`docs/setup.md`, record the source-versus-skill divergences in a Doc drift
section marked "reported, not fixed", and log a CHANGELOG entry. This
closes GitHub issue #25.

## Manager's Notes

- Source issue: <https://github.com/mokhtarabadi/cognitive-lead-hq/issues/25>
  — the issue body already carries a draft; it is a starting point, NOT
  ground truth.
- The issue body claims the extraction model resolves as
  "`DECISION_MODEL`, else `BRAIN_MODEL`". Source-verified discovery proved
  this FALSE: `DEFAULT_DECISION_MODEL = "gpt-6-astra"` (`server.py:195`) and
  only `DECISION_MODEL` overrides it (`server.py:265-275`). `BRAIN_MODEL` is
  never read by this server. The new doc must correct this explicitly.
- Drift items are "reported, not fixed": do NOT edit `server.py`,
  `redactor.py`, `detector.py`, or any skill file in this task.
- Documentation-only change. No application code (AGENTS.md guardrail).
- Follow `sop-maintenance` (Markdown only, CHANGELOG sync, no global state
  files).
- Canonical precedent for tone and structure: `docs/brain-bridge.md`.

## Local TODOs

- [x] Re-read the six tool definitions and validation paths in `mcp-decision-server/server.py`; confirm every citation line number before writing
- [x] Write `docs/manager-decisions.md` (overview, store resolution, the six tool schemas, shared field contract, pitfalls, workflow, doc drift)
- [x] Add cross-links in `README.md` (Documentation list + repository tree) and `docs/setup.md` (MCP Servers table)
- [x] Add the `[Unreleased]` CHANGELOG entry
- [x] Run `lint_markdown` on the new doc and `lint_task_file` on this task
- [x] Run the RTK-prefixed full test suite plus `scripts/check_docs_sync.py`; record evidence

## Acceptance Criteria

- [x] `docs/manager-decisions.md` exists and documents all six tools (`extract_session_decisions`, `record_manager_decision`, `query_manager_decisions`, `get_sync_status`, `get_manager_profile`, `propose_profile_evolution`) with exact signatures, argument names and types, return shapes, side effects, and failure modes
- [x] Every factual claim carries a `file:line` citation into `mcp-decision-server/`; the issue's `BRAIN_MODEL` claim is explicitly corrected (only `DECISION_MODEL` is read, default `gpt-6-astra`)
- [x] A Doc drift section lists the source-versus-`SKILL.md` divergences as "reported, not fixed", and no server source or skill file is modified by this task
- [x] The store-resolution order, the eight-value category enum, the three optional enums (`fidelity`/`mode`/`scope`), and the six required fields are documented exactly as the source enforces them
- [x] `README.md` and `docs/setup.md` link to the new doc
- [x] `CHANGELOG.md` carries an `[Unreleased]` entry describing the new doc
- [x] The RTK-prefixed full suite exits 0; `scripts/check_docs_sync.py` reports OK; `lint_markdown` on the new doc and `lint_task_file` on this task both pass

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** all tests pass
- **Actual result:** Full suite green — `rtk test` summarized **686 passed, 10 warnings in 5.17s**. Supporting gates: `lint_markdown` on `docs/manager-decisions.md` → passed; `lint_task_file` on this task file → passed; `uv run scripts/check_docs_sync.py` → `docs-sync: OK` (two pre-existing warn-only orphan scripts: `scripts/fetch-opencode-docs.py`, `scripts/repomd`).
- **Exit code:** 0

> Verification runner rule: `uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q` is the complete underlying test command. The first verification run MUST use the `rtk test` prefix; record the exact prefixed command above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** The issue body contains an unverified claim (`BRAIN_MODEL` override) and stale references; copying it instead of re-reading source would ship a wrong contract. Separate risk: `file:line` citations rot when `server.py` changes, so every citation is re-confirmed at write time and the doc states it is pinned to the current revision.
- **Rollback plan:** Revert the single docs commit (`git revert <hash>`) — the change touches only `docs/manager-decisions.md`, `README.md`, `docs/setup.md`, and `CHANGELOG.md`, so no code or data path is affected.

---

## Execution Log & Reasoning

**Pipeline mode:** full-automatic autopilot, authorized by the stored standing
order `manager/full_automatic_mode` (set 2026-09-17) and ruling
`DEC-20260917-009`/`DEC-20260917-013` (a reviewer technical `APPROVED` with
`PO_REVIEW_PENDING` satisfies the closure gate), plus `DEC-20260920-001`
(autopilot plans through the Brain, then implements without a separate plan
approval pause). ZAC holds: nothing is committed except through the MCP tools.

**Planning gate.** Brain plan turn under `task_id=267`, `stage=plan`, seat
Software Architect (the TITLE+BODY words "schema" and "contract" fire the
`schema|contract|migration|quota|index|API design` trigger). Blueprint:
"Manager-Decisions MCP Contract Doc" — in scope F1 the new doc, F2 the README
cross-link, F3 the `docs/setup.md` cross-link, F4 the `[Unreleased]` CHANGELOG
entry; out of scope any server source, any `SKILL.md`, and any behavior change.

**Discovery.** All six tool anchors, the store-resolution helper, the
validator, the redactor and the detector were read from source with line
numbers re-confirmed immediately before writing
(`server.py` 1258/1259, 1550/1551, 1642/1643, 1745/1746, 1759/1760,
1784/1785; `mcp.run(transport="stdio")` 1821). No claim in the new page rests
on the issue body alone.

**Changes.**

1. `docs/manager-decisions.md` (new, 10 sections): purpose and scope with a
   pinned revision note; server identity and transport; store resolution
   including the fail-closed explicit-path behavior; six-tool quick reference
   plus the enum sheet; per-tool detail for all six; the shared record field
   contract; an agent pitfalls table; a recommended workflow; the doc-drift
   table; and the could-not-verify list.
2. `docs/setup.md` — the `mcp-decision-server` row in the MCP Servers table now
   links to the new page.
3. `README.md` — the Documentation list gained the new page, and the repository
   tree gained both `docs/manager-decisions.md` and the previously missing
   `mcp-decision-server/` stanza.
4. `CHANGELOG.md` — one `[Unreleased]` / `### Added` bullet describing the page,
   the correction, and the six reported-not-fixed drift items.

All four files were then reformatted with the repo's Prettier.

**Correction shipped.** The issue body's "`DECISION_MODEL`, else `BRAIN_MODEL`"
claim is false. Only `DECISION_MODEL` overrides
`DEFAULT_DECISION_MODEL = "gpt-6-astra"` (`server.py:196`, `:265-275`);
`BRAIN_MODEL` is read nowhere in `mcp-decision-server/`; the deliberate
non-fallback target is `PERSONA_MODEL` (`server.py:268`).

**Assumptions.**

- **A1** — The doc-drift items ship as "reported, not fixed" and no source or
  skill file is touched. Reason: the task's Manager's Notes and the Brain
  Blueprint both scope the change to documentation only, and AGENTS.md forbids
  widening work beyond the request.
- **A2** — The Related section points at `skill-templates/manager-decision/SKILL.md`
  rather than `.opencode/skills/manager-decision/SKILL.md`. Reason: this repo
  holds only `sop-maintenance` under `.opencode/skills/`; the manager-decision
  skill exists in-repo only as a template.
- **A3** — Citations are pinned to commit `0183433` and dated 2026-09-21 in the
  page header. Reason: line numbers shift when `server.py` changes, so the page
  states its revision rather than implying permanence.

**Verification.** `rtk test … pytest tests/ -q` → `686 passed, 10 warnings in
5.17s`, exit 0. `lint_markdown docs/manager-decisions.md` → passed.
`lint_task_file` → passed. `uv run scripts/check_docs_sync.py` → `docs-sync: OK`,
exit 0. The two orphan warnings it prints (`fetch-opencode-docs.py`,
`repomd`) are pre-existing and warn-only by design.

**Not done in this task (by scope).** No fix for any of the six drift items, no
edit to `server.py`/`redactor.py`/`detector.py`, no edit to any `SKILL.md`.

**QA (Brain, `stage=qa`).** Verdict `QA_PASSED`. The adversarial report found
no vulnerabilities, no invented claims, and no missing tests; every citation
matched the fed-context anchors; a docs-only change needs no new tests.

**Review (Brain Code Reviewer, `stage=review`).** Verdict `APPROVED`, status
`PO_REVIEW_PENDING`. Strengths F1–F7: all six tools covered with signatures and
failure modes; claims pinned to `0183433`; the `BRAIN_MODEL` error corrected in
explicit text; drift reported-not-fixed with zero source edits; cross-links in
README list, README tree, and the setup table; a clear Unreleased CHANGELOG
entry; 686 passed with `docs-sync: OK`. Single finding F8 (prettier reflow of
historic CHANGELOG/README lines) is rated Low: no fact change, no blocker, no
rework. Technical-vs-final notice recorded — code approved on technical grounds,
final closure needs the Manager approval word, relayed by the standing order.

**Closure authorization.** Stored standing order `manager/full_automatic_mode`
(2026-09-17) states "Reviewer technical APPROVED + PO_REVIEW_PENDING counts as
closure approval." Reinforced by `DEC-20260917-009` and `DEC-20260917-013`
[quality-gate], `DEC-20260919-001` [process] (close the task and the GitHub
issue one-by-one with an issue fix comment), and `DEC-20260914-003` [process].
Task Source is `manager`, not telegram, so no Telegram reply is owed. ZAC held:
no raw `git add`/`git commit`/`git push`; closure runs only through
`custom_context_commit_and_clean_task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `25de01245845eaedde599c11153fd042641261e1`
<!-- END_GIT_DIFF -->
