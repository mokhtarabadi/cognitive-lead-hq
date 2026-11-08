# Task 0380: Fix missing_context loop on uninjectable paths (sniff fallback + no-repeat contract)

**File:** `tasks/completed/0380-missing-context-loop-uninjectable-paths.md`
**Source:** manager (2026-11-06 — ad-hoc fa: brain kept saying "context ندارم", find the bug, fix in place, no task — then task ordered for the record)
**Type:** bugfix
**Status:** closed
**Finished:** 2026-11-06T12:01:14Z
**Submitted:** 2026-11-06T11:45:39Z

## Goal

End the planning-loop stall where the Brain re-requests the same `context_paths` entry turn after turn: (1) inject text files whose suffix is not allowlisted via UTF-8/NUL sniffing instead of resolving them to zero chars, and (2) forbid re-requesting a path the bridge labeled `[unavailable: ...]`.

## Manager's Notes

Persian verbatim: "مشکل برین رو حل من ... چرا هی میگه کانتکس ندارم ... باگ و gap رو پیدا کن ... به خود برین بگو self improvement" + "موافقم و برای همه skil template ها تک تک سرچ کن و همه پسوند های موجود رو که نداریم اضافه کن ... نیاز به تسک نیست همونجا درستش کن و تستش ها رو اوکی کن و پاس کن" + "دیدم vue و setelve رو پاک کردی اوکیه تغییرتتت؟" + "الان .env.example رو میتونه بخونه؟" + "تسکش رو بساز توی repo خودش با توضیحت کاملش".

## Root cause (verified, not hypothesized)

Case: dumble 1047 Phase 3 env switches. The Hands fed `context_paths` including `.env.example#L75-100` twice (verbatim bodies per the 0378 contract). The Brain answered `missing_context` for the same path three turns in a row.

- Ledger proof (`tasks/.sessions/<ses>/../context_ledger.jsonl`, dumble repo): `.env.example#L75-100` attached with `status: unavailable:unsupported extension`, `shown_chars: 0` — twice. Bodies for all other requested paths attached WITH content (e.g. aiService slices 1–4 KB each).
- Mechanism (`mcp-brain-bridge/server.py`): `Path('.env.example').suffix` is `.example`, absent from `_ALLOWED_READ_SUFFIXES`, so both attach paths (`build_paths_attach`, `_path_candidates`) emitted `[unavailable: ... — unsupported extension]` with zero injected chars.
- Contract gap (`prompts/fragments/13-constraints.md`, No-Hallucination): `unavailable` counts as missing, and no sentence forbade re-requesting an uninjectable path — so contract-compliant re-requests looped until the Hands-side second-discovery halt fired.
- The fix was validated live: the same `.env.example#L1-2` request now injects with label `[path-injected: .env.example#L1-2 — sniffed text, unlisted extension — lines 1-2 of 3]` on BOTH entry points.

## What was implemented (2026-11-06, no task file at the time — this file is the record)

- `mcp-brain-bridge/server.py`:
  - `_ALLOWED_READ_SUFFIXES` += skill-sweep text suffixes: `sqm properties plist xcconfig strings mod sum ini cfg conf mdx csv rst fish ejs` (each found verbatim in at least one skill template: SQLDelight, Java props, iOS plist/xcconfig, go.mod/go.sum, ini, rst).
  - `_UNREADABLE_SUFFIXES` (exe/dll/so/zip/tar/gz/png/jpg/pdf/aar/keystore/…) skip sniffing outright.
  - `_sniff_text_file()`: read up to `_READ_MAX_BYTES`, reject on NUL, decode UTF-8 — text injects, anything else stays `[unavailable: unsupported extension]`.
  - Wired into BOTH `_path_candidates` (live turns) and `build_paths_attach` (helper/tests); range slicing keeps working on sniffed text and the `sniffed text, unlisted extension` note survives `#Lstart-end` slicing.
  - Incidental catch during review: `.vue`/`.svelte` were accidentally dropped by the allowlist edit and restored; verified programmatically (removed-set empty).
- `prompts/fragments/13-constraints.md` + rebuilt `system-prompt.md` (`9.71.0` → `9.72.0` via `scripts/prompt-build/assemble_system_prompt.py`, byte-clean: only the two intended hunks): an `[unavailable: ...]` label (anything that is NOT a truncation note) means uninjectable — never re-request the same path; proceed without it, ask for an inline paste, or escalate.
- `tests/test_brain_bridge.py`: 4 new tests (dotfile sniff, extensionless sniff, binary stays rejected, skill-sweep suffixes inject).
- `tests/test_prompt_sync.py`: version pin `9.72.0` + new contract test (unavailable-no-repeat sentence present in shipped prompt).
- `mcp-brain-bridge/DECISIONS.md`: ADR-012. `CHANGELOG.md`: entry under `[Unreleased] → Fixed`.
- Verification: full HQ suite `794 passed` (with `--with pyyaml`); `test_brain_bridge.py` + `test_prompt_sync.py` re-run green (`341 passed`) after the vue/svelte restore.

## Local TODOs

- [x] Diagnose loop with ledger evidence (0-char `.env.example` injection).
- [x] Skill-by-skill suffix sweep; extend allowlist; no removals (programmatically verified).
- [x] Sniff fallback in both attach paths; binary stays rejected.
- [x] Contract sentence in fragment; rebuild prompt (9.72.0); byte-clean diff verified.
- [x] Regression tests (bridge + prompt-sync); full suite green twice.
- [x] ADR-012 + CHANGELOG entry.
- [ ] Manager follow-up (optional, not blocking): consider the same sniff treatment for `read_source_files` bulk reports (currently `.gitignore`-aware skips like `.env*` stay skipped there — by design, different contract).

## Acceptance Criteria

- [x] `.env.example#Lx-y` injects with content on both attach entry points (proven live, not just unit-tested).
- [x] No previously allowed suffix was removed (programmatic removed-set check prints NONE).
- [x] An `[unavailable: ...]` path is never re-requested: contract sentence shipped in `system-prompt.md` 9.72.0 and pinned by test.
- [x] Full HQ suite green (`794 passed`).
- [x] `lint_task_file` passes on this task file.

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q` → `794 passed`; targeted `tests/test_brain_bridge.py tests/test_prompt_sync.py` → `341 passed` (after vue/svelte restore)
- **Expected result:** all green; no allowlist removals; live sniff proof
- **Actual result:** all green; removed-set `NONE`; live probe injects `.env.example` with `sniffed text, unlisted extension` label on both entry points
- **Exit code:** 0
- **QA hotfix (2026-11-06):** bounded sniff read + cap-plus-one regression test.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_brain_bridge.py -q` → `314 passed` (incl. `test_sniff_text_file_reads_only_cap_plus_one`); full `rtk test ... python -m pytest tests/ -q` → `795 passed, 24 warnings`
  - **Expected result:** focused + full green; spy asserts single read of exactly `_READ_MAX_BYTES + 1`
  - **Actual result:** green; oversized file returns `None` after one bounded read
  - **Exit code:** 0
- **QA hotfix 2 (2026-11-06):** control-character rejection.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_brain_bridge.py -q` → `314 passed` (incl. updated binary test); full `rtk test ... python -m pytest tests/ -q` → `795 passed, 24 warnings`
  - **Expected result:** focused + full green; control-byte payloads labelled unavailable
  - **Actual result:** green; nul-blob + control-blob both `[unavailable: ... — unsupported extension]`
  - **Exit code:** 0
- **Review hotfix (2026-11-06):** live-turn dotfile regression test.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_brain_bridge.py -q` → `315 passed` (incl. `test_path_candidates_dotfile_sniffs_text`); full `rtk test ... python -m pytest tests/ -q` → `796 passed, 24 warnings`
  - **Expected result:** focused + full green; `_path_candidates` injects `.env.example#L1-1` with sniff label
  - **Actual result:** green; candidate repr carries `sniffed text, unlisted extension` + `OPENAI_MODEL=gemma`
  - **Exit code:** 0
  - Stack-gate skip: root=. markers=[mcp-brain-bridge/pyproject.toml, Flask markers, FastAPI markers, go.mod, build.gradle.kts, Package.swift, *.xcodeproj, package.json, vite.config.*, nuxt.config.*, nest-cli.json, prisma/schema.prisma] matched=[] reason=no matching stack marker found (python-fastapi discipline-only).

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** sniffing reads unknown files up to the existing size cap — bounded by `_READ_MAX_BYTES` + per-file/total caps; binaries (incl. NUL-containing text) stay rejected.
- **Rollback:** revert `server.py` hunks + suffix list + fragment sentence; rebuild prompt (9.72.0 → 9.71.0). Worktree currently holds all changes unstaged (no task existed at implementation time); commit path is the Manager's.

---

## Execution Log & Reasoning

- Diagnosis used the per-turn context ledger, not guesses: 0-char `.env.example` attachments + repeated identical re-requests = allowlist gap, not a model reasoning failure.
- The loop also exposed a second, already-fixed gap class (0378: prose fed-context never grounds) — this task covers only the uninjectable-path half.
- No `agents/cognitive-executor.md` changes needed: the Hands-side halt rule (second discovery request = stop) already fired correctly here.
- [2026-11-06 autopilot] Autopilot locked for 0380 (Manager: Brain autopilot to approval-for-closure). Seat Check: bugfix+contract domain → Senior Programmer (+QA/Reviewer at gates); Designer/Strategist/Planner skipped (no UX/scope/capacity surface). Brainstorm: not required — single-domain reversible bugfix, no cross-disciplinary ambiguity.
- [2026-11-06 autopilot] Verification re-run: `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q` → `794 passed, 24 warnings`, exit 0. `lint_task_file` passed on in-progress path.
- [2026-11-06 autopilot QA hotfix] QA_REJECTED: `_sniff_text_file()` stat-then-read race could read beyond `_READ_MAX_BYTES`. Fixed with bounded `stream.read(_READ_MAX_BYTES + 1)` + `len(raw) > cap → None`; added `test_sniff_text_file_reads_only_cap_plus_one` (read-size spy). Skills loaded: project-memory, prompt-refactor, testing-strategy, verification-before-completion, task-lint, versioning-and-release; python-fastapi as closest-discipline only (stack-gate skip: root=., markers scanned, matched=[], reason=no matching stack marker found). Sibling docs read: mcp-brain-bridge README/DECISIONS present; tests README/DECISIONS present (no doc changes — no boundary/contract change). Focused `tests/test_brain_bridge.py` → `314 passed`; full suite → `795 passed, 24 warnings`, exit 0; `lint_task_file` on QA path pending re-run. Task stays in `tasks/qa/` for re-QA.
- [2026-11-06 autopilot QA hotfix 2] QA_REJECTED-2: valid-UTF-8 control-byte payloads (`\x01\x02\x03`) passed the NUL check. Fix: `unicodedata.category == "Cc"` reject except `\t\n\r\f`; binary test now covers nul-blob + control-blob with exact unavailable labels. Docs updated (ADR-012, bridge README sniff rule, CHANGELOG qualification). Focused `tests/test_brain_bridge.py` → `314 passed`; full suite → `795 passed, 24 warnings`, exit 0. Stack-gate skip: root=., markers scanned, matched=[], reason=no matching stack marker found.
- [2026-11-06 autopilot review hotfix] APPROVED_WITH_CHANGES: no test pinned dotfile sniff through `_path_candidates` (live-turn entry). Added `test_path_candidates_dotfile_sniffs_text` (test-only, no prod change). Code-search + testing-strategy loaded for this turn. Task stays in `tasks/qa/` for re-review.
- [2026-11-06 autopilot] Re-review verdict: `PO_REVIEW_PENDING` (technical verdict: `APPROVED`). Issues: none. File remains in `tasks/qa/`; closure awaits Manager's explicit `Approved for closure` / `Close task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `353d819449e314ad661f73c2cea6b26b171635ef`
<!-- END_GIT_DIFF -->
