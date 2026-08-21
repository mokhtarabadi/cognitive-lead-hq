---
created_at: '2026-08-21T11:02:31.731049+00:00'
status: active
tags: []
updated_at: '2026-08-21T11:02:31.731066+00:00'
---

# Brain + Hands Architecture Decision — 2026-08-21

**Decision:** Keep hybrid Brain/Hands. REJECT full decoupling to 100% OpenCode.

- Brain: Gemini 1.5 Pro via Google AI Studio (paid) — responsible for planning, prompt-refactor, brainstorm-swarm, Kanban orchestration
- Hands: OpenCode with muse-spark-1.2-contributor-free — responsible for execution, QA sub-agents can run internally via `task` tool but planning stays on Brain
- Rationale: Small free model degrades 20-40% on planning/review quality (context window, reasoning). Execution is fine on free model, orchestration is not.

**Meta-Task Bundle Decision:**
- APPROVED for full automatic implementation with Archive (not purge)
- Cap 5-6 tasks per META, verbatim requirement preservation, single diff, single QA gate, all-or-nothing
- Originals move via `git mv` to `tasks/archive/` with `superseded-by: META-NN` marker, history preserved via `git log --follow`
- Implemented via `scripts/bundle-tasks.py` + task-generator skill extension (Task 110)
- Related: Task 101 Loop Engine remains deferred
