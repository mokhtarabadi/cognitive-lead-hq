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

1. **Resolve endpoints.** Source = `<cwd>/.opencode/decisions` (must exist with `decisions/INDEX.md`, else HALT and report — nothing to migrate). Target = `DECISION_REPO_PATH` taken ONLY from an explicit Manager-provided value or an already-existing env/config key. Empty, unset, or non-directory target = HALT. Never invent, guess, or default the target path.
2. **Dry run first (mandatory).** Read every source record. For each: run `sanitize_text` + `verify_clean` mentally via the `record_manager_decision` validation path — do NOT write. Classify: `would-migrate` / `would-skip` (ID already present in target) / `would-reject` (scrub or schema failure, with reason). The three counts must sum to the scanned total. Present the table + counts to the Manager and STOP. No `record_manager_decision` call happens without an explicit Manager batch-approval phrase — any ambiguous reply counts as NOT approved.
3. **Migrate on approval.** For each approved `would-migrate` record: first pre-check the target for an existing identical `migrated_from` value and skip-if-exists (idempotent reruns change nothing). Then persist through `record_manager_decision` (the ONLY write path — scrub + schema + INDEX regen ride along). Carry provenance: `migrated_from: <project-name>/<original-id>` on EVERY migrated record. Never edit the source store; never edit target history in place. Prove source immutability with `git status --porcelain` before and after (source dir must show unmodified).
4. **Report.** Final counts: migrated / skipped-existing / rejected-with-reasons. Every rejected ID is listed with its reason — never dropped silently. A failed scrub/verify blocks only that record, never the batch.

## Rules

- Scrub before store, verify before write — per record, no exceptions, no batch bypass.
- Append-only on both ends: corrections are new tombstone records, never edits or deletes.
- A failed verification blocks that record and is reported — it never blocks the rest of the batch silently.
- ZAC holds: this skill never commits, pushes, or tags. The Manager commits.
