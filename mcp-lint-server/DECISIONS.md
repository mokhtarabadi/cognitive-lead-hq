# Architectural Decisions: mcp-lint-server

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-19] ADR-002: Mechanical Prose Gates (Skill Verbs, META Shape)

- **Context:** Prompt-facing prose carried skill invocations the Brain cannot execute (no skill tool, no web, no files) and bundle META files had no structural gate — both bug classes failed silently.
- **Decision:** Add `_check_unactionable_skill_verbs` (Brain-owned `prompts/fragments/` only, registry exempt, Hands-window + boundary + fence + marker exemptions) wired into `lint_markdown` (fragment-scoped) and `lint_system_prompt_sync` (per-fragment scan); add `_check_bundle_meta_structure` (META-only detection, non-META skips with pass) wired into `lint_task_file`.
- **Consequences:** Reworded fragments pass, old wording fails with file-plus-line citations; non-META task files unaffected.
- **Rollback:** Remove the two checks + wiring; prior lint behavior returns.

## [2026-10-25] ADR-003: Planner Metadata Gate

- **Context:** The Planner reads `**Estimate:**`, `**Deadline:**` and `**Depends on:**` from task headers and silently ignores a value it cannot parse — a hand-written `**Estimate:** 3 hours` simply removes the task from capacity with no error anywhere. Since no tool wrote those lines, every agent that recorded a deadline did it by hand, which is the exact failure mode that produced a task with a deadline the Planner never saw.
- **Decision:** Add `_check_planner_metadata`, wired into `lint_task_file` and `lint_all_tasks`: a present `**Estimate:**` must match `^\d+(\.\d+)?h$`, `**Deadline:**` must be `YYYY-MM-DD`, `**Depends on:**` must be a bracketed or comma-separated id list, and a duplicated key is an error (the Planner keeps the last, hiding the mistake). Absence stays valid so legacy files and non-planner projects keep passing.
- **Consequences:** A malformed header fails before staging instead of vanishing from the read model; the check is format-only and never rewrites; the paired writer is `schedule_tasks` in the Planner server, so agents have a correct path rather than a forbidden one.
- **Rollback:** Remove the check and its two call sites; prior lint behavior returns.

## [2026-10-26] ADR-005: Path-drift comparison resolves against the caller's root

- **Context:** `_check_task_file_structure` compared `Path(header).resolve()` with `Path(file_path).resolve()`, both anchored to the lint server process CWD. The server is a long-lived singleton whose CWD is its install directory, so an absolute call path never matched a relative header. `lint_all_tasks` hands the guard absolute paths for every file while headers are normally relative, which produced one false `File path mismatch` per task and made a clean batch report impossible.
- **Decision:** Add `_resolve_task_reference(path_str, root)` and a `root` parameter on `_check_task_file_structure`; relative and absolute sides both resolve against the caller's `project_root`. `lint_task_file` and `lint_all_tasks` thread their resolved `workspace_root` through. Calling the helper without a root keeps the previous CWD behaviour so direct callers and older tests are unaffected.
- **Consequences:** An absolute call and its equivalent relative call return the same verdict; the batch linter can report zero issues; a genuinely stale header in another Kanban lane still fails because both sides resolve under the same root to different files.
- **Rollback:** Drop the `root` parameter, the helper, and the two call-site arguments; CWD-based comparison returns.

## [2026-10-25] ADR-004: Task time stamps are validated, not trusted

- **Context:** the planner now measures task duration from `**Started:**`, `**Submitted:**` and `**Finished:**`. A local-time or free-text value parses to nothing, and a finish earlier than its start produces a negative duration — both silently, which is exactly the failure mode the earlier metadata gate exists to prevent.
- **Decision:** `_check_planner_metadata` validates the three stamps when present: `YYYY-MM-DDThh:mm:ssZ` only (a `+02:00` offset is rejected on purpose, because the rest of the header is UTC and mixing them makes comparisons wrong), and a `Submitted`/`Finished` earlier than `Started` is an error. Absence stays valid, so every existing task file keeps passing.
- **Consequences:** a malformed stamp fails before staging instead of producing a nonsense duration on the dashboard; the writer side already emits `Z`, so the gate only fires on hand edits.
- **Rollback:** delete the stamp block from the check; the other metadata validations are untouched.
