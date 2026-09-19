---
name: decision-migration
description: Migrate a project's per-project manager decisions into the separate personal repo. Hands-invoked, dry-run-first, idempotent, append-only.
---

# Decision-Migration Skill

> Invoke this skill when the Manager says "call the migration skill" (or equivalent) inside a project. You — the Hands — perform the migration. There is no standalone script; this skill IS the migration capability.

## Purpose

Old projects keep manager decisions in their per-project `.opencode/decisions/` store. The personal repo is the authoritative personality source. This skill moves records from the former to the latter: scrubbed, verified, de-duplicated, append-only — with the Manager approving before anything is written.

## When to Invoke (Trigger)

- The Manager names this skill in any project ("migrate the decisions", "call the migration skill").
- A project is being onboarded to the personal repo for the first time.

## Migration Workflow

1. **Start the dry run at once.** On invocation, go straight to step 3 (dry run) with scope = the current project. Ask NOTHING first — no target question, no scope question, no task-file question. STOP only for the two gates below: (a) a HALT condition in step 2, (b) the batch-approval gate in step 4.
2. **Resolve endpoints (lookup, never invent).** Source = `<cwd>/.opencode/decisions` (must exist with `decisions/INDEX.md`, else HALT and report — nothing to migrate). Target personal repo, first hit wins: (i) an explicit Manager-provided value; (ii) an already-existing `DECISION_REPO_PATH` env/config key; (iii) the project's `LLM.txt` §7.11 declaration; (iv) a `<parent-of-cwd>/manager-decisions` directory — but ONLY if that directory already exists. If none resolve, HALT and ask the Manager for the target path (this is the ONLY question allowed before the dry run) — via the `question` tool when the session capability manifest shows it AVAILABLE, otherwise in prose. Never create a target directory unasked; never write to a path the Manager has not effectively confirmed — the resolved target is always printed in the dry-run table, and the batch-approval gate below is the confirmation.
3. **Dry run first (mandatory).** Read every source record. For each: run `sanitize_text` + `verify_clean` mentally via the `record_manager_decision` validation path — do NOT write. Classify: `would-migrate` / `would-skip` (ID already present in target) / `would-reject` (scrub or schema failure, with reason). The three counts must sum to the scanned total. Present the table + counts + resolved target path to the Manager and STOP (use the `question` tool when the session capability manifest shows it AVAILABLE, otherwise relay the same content in prose). No `record_manager_decision` call happens without an explicit Manager batch-approval phrase — any ambiguous reply counts as NOT approved.
3. **Migrate on approval.** For each approved `would-migrate` record: first pre-check the target for an existing identical `migrated_from` value and skip-if-exists (idempotent reruns change nothing). Then persist through `record_manager_decision` (the ONLY write path — scrub + schema + INDEX regen ride along). Carry provenance: `migrated_from: <project-name>/<original-id>` on EVERY migrated record. Never edit the source store; never edit target history in place. Prove source immutability with `git status --porcelain` before and after (source dir must show unmodified).
4. **Report.** Final counts: migrated / skipped-existing / rejected-with-reasons. Every rejected ID is listed with its reason — never dropped silently. A failed scrub/verify blocks only that record, never the batch.

## Rules

- Scrub before store, verify before write — per record, no exceptions, no batch bypass.
- Append-only on both ends: corrections are new tombstone records, never edits or deletes.
- A failed verification blocks that record and is reported — it never blocks the rest of the batch silently.
- Small runs need no task file: runs of 50 records or fewer proceed without creating one. Create a backlog task file ONLY when the source holds more than 50 records or the Manager explicitly asks.
- ZAC holds: this skill never commits, pushes, or tags. The Manager commits.
