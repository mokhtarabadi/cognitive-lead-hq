---
created_at: '2026-09-14T19:20:54.893748+00:00'
status: active
tags: []
updated_at: '2026-11-13T00:00:00.000000+00:00'
---

Global install **syncs** run WITHOUT a task file: Manager order 2026-09-14 — execute `workflows/global-install-upgrade` directly on the machine, then tell the Manager to restart OpenCode so the new server code/skills load. Task-file tracking adds no value for a machine-local copy of unchanged repo content.

**Refined 2026-11-13 (Task 399):** the no-task rule applies only to a SYNC of already-committed repo content. Anything that also CHANGES repo files — editing `LLM.txt`, rewriting memories, changing a skill, adding or removing an install target — is ordinary repository work and DOES need a task file with the normal AC/DoD/evidence gates. The dividing line is "did the repo change?", not "did the machine change?".

A cleanup that removes machine-local assets (here: the Freebuff footprint — npm global package, `~/.config/manicode/`, a stale V1 `~/.AGENTS.md`) is a sync-plus-change task when it also rewrites the install instructions; the destructive part is authorized by the Manager's explicit order and is recorded in the task file with a before/after inventory so nothing is deleted unobserved.
