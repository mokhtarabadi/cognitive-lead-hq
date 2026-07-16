# Task: Add QA Persona and Task Archiving to Roadmap

**File:** `tasks/40-add-qa-and-archiving-to-roadmap.md`
**Type:** improvement
**Status:** closed

## Goal

Append two new strategic items to the Future Architectural Roadmap in README.md — an Adversarial QA Engineer persona (#8) and a Lifecycle Task Architecture with Kanban folder structure and archiving (#9) — and log the update in CHANGELOG.md.

## Manager's Notes

- Only README.md, CHANGELOG.md, and this task file should be modified.
- Use the standard task template with `<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index a88bccd..809754b 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -9,6 +9,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ### Changed

 - **README roadmap** — Added Memory Management (Smart Note-Taking MCP & Skill) as item #7 in the Future Architectural Roadmap, describing a local `memory-mcp` server and `project-memory` agent skill for persistent context retention.
+- **README roadmap** — Added Adversarial QA Persona as item #8 and Lifecycle Task Architecture (Kanban & Archiving) as item #9 to the Future Architectural Roadmap, describing a dedicated `[QA Engineer]` persona with adversarial testing instructions and a state-based Kanban folder workflow with archiving compaction.

 ## [5.19.0] — 2026-07-15

diff --git a/README.md b/README.md
index 7f626ac..0229055 100644
--- a/README.md
+++ b/README.md
@@ -296,3 +296,8 @@ See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents mus
      - _"OpenCode, load the memory skill, see what the notes are, and follow them."_
      - _"OpenCode, call the memory skill; remember this thing I'm telling you about the database tests."_
    - **Goal:** Ensure complete, highly detailed context retention across isolated sessions without permanently bloating the core `AGENTS.md` file.
+8. **Adversarial QA Persona:** Introduce a dedicated `[QA Engineer]` persona to the `system-prompt.md`. Unlike the Code Reviewer (who checks for formatting and architectural compliance), the QA Engineer's explicit instruction is adversarial: _actively attempt to break the Senior Programmer's implementation_. It will focus on generating negative test cases, boundary tests, fuzzing scripts, and identifying race conditions, ensuring enterprise-grade stability before a task is marked complete.
+9. **Lifecycle Task Architecture (Kanban & Archiving):** Migrate the flat `tasks/` directory into a state-based Kanban folder structure to prevent context bloat and improve project tracking.
+   - **Folders:** `tasks/backlog/`, `tasks/in-progress/`, `tasks/qa/`, and `tasks/completed/`.
+   - **Workflow:** The `task-generator` skill creates tasks in `backlog/`. As the Programmer and QA personas work, the file is physically moved through the pipeline.
+   - **Compaction:** An archiving skill will periodically compress older files in the `completed/` directory into dense, single-file summaries in `docs/history/` (e.g., `milestone-1-summary.md`), keeping the active `grep` and `glob` MCP searches blazingly fast.
```

<!-- END_GIT_DIFF -->
