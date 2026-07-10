# Task: Update README and Future Roadmap for V5.13.0 Skills

**Type:** improvement
**Status:** closed

## Goal

Update `README.md` to reflect the newly added V5.13.0 skill templates (`go-hexagonal-grpc` and `prompt-refactor`) in the repository tree, and append two new strategic goals to the Future Architectural Roadmap.

## Manager's Notes

- The repository tree section of README.md was updated to replace old entries with the new `go-hexagonal-grpc` and `prompt-refactor` skills, and reordered alphabetically by relevance.
- Two new roadmap items were added:
  1. Automated Prompt Refactoring Pipeline — integrating the new `prompt-refactor` skill as an auto-refine pre-hook.
  2. Hexagonal Architecture Expansion — porting the strict Ports & Adapters blueprint from Go to Python (FastAPI) and TypeScript (Node.js) templates.

## Local TODOs

- [x] Initial codebase exploration
- [x] Read README.md and understand current structure
- [x] Update repository tree section in README.md with new V5.13.0 skills
- [x] Append new roadmap items 5 and 6 to Future Architectural Roadmap
- [x] Update CHANGELOG.md with patch release v5.13.1
- [x] Run prettier to verify markdown formatting
- [x] Call `custom_context_stage_and_inject_diff` to finalize

## OpenCode Execution Log & Reasoning

_(OpenCode: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

### Architectural Reasoning

**Why update the README tree immediately?** The repository structure section in README.md acts as the primary navigation map for both human developers and AI agents loading context. If the new `go-hexagonal-grpc` and `prompt-refactor` skills are not listed, agents will not discover them via `skill` tool queries or documentation scans. Keeping the tree synchronized with the actual file system is critical for discoverability.

**Why new roadmap items?** The `prompt-refactor` skill's full potential is realized when it is wired as an automatic pre-processing hook — this eliminates the weakest link in the chain: ambiguous Manager input. The Hexagonal Architecture expansion ensures that the "Max Power" constraint system is not limited to Go; Python and Node.js backends benefit equally from Ports & Adapters rigidity.

### Files Changed

1. **`README.md`** — Updated repository tree to feature `go-hexagonal-grpc` and `prompt-refactor` as top entries; appended roadmap items 5 and 6.
2. **`CHANGELOG.md`** — Added v5.13.1 patch entry.
3. **`tasks/21-update-readme-and-todos.md`** — This file.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1f1f7ae..5cc3eff 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -122,6 +122,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

 ## [Unreleased]

+## [5.13.1] — 2026-06-30
+
+### Changed
+
+- **`README.md`** — Updated repository tree to feature `go-hexagonal-grpc` and `prompt-refactor` as prominent entries; appended 2 new strategic items to the Future Architectural Roadmap (Automated Prompt Refactoring Pipeline and Hexagonal Architecture Expansion).
+
 ## [5.13.0] — 2026-06-30

 ### Added
diff --git a/README.md b/README.md
index 9babf10..88e49a6 100644
--- a/README.md
+++ b/README.md
@@ -69,15 +69,19 @@ If you have an older project using global `STATE.md` and `TODO.md` files:
 │       └── sop-maintenance/
 │           └── SKILL.md                # Native OpenCode skill for repo rules
     └── skill-templates/                    # Reusable stack blueprints (Agent Skills)
-        ├── nodejs-express/
+        ├── go-hexagonal-grpc/
         │   └── SKILL.md
-        ├── spring-boot/
+        ├── prompt-refactor/
         │   └── SKILL.md
-        ├── flask-python/
+        ├── android-kotlin/
         │   └── SKILL.md
         ├── nextjs/
         │   └── SKILL.md
-        ├── android-kotlin/
+        ├── nodejs-express/
+        │   └── SKILL.md
+        ├── spring-boot/
+        │   └── SKILL.md
+        ├── flask-python/
         │   └── SKILL.md
         ├── android-java-xml/
         │   └── SKILL.md
@@ -209,3 +213,5 @@ See `.opencode/skills/sop-maintenance/SKILL.md` for the rules that AI agents mus
 2. **Epic and Milestone Tracking:** Create an `epics/` directory and update the `task-generator` skill to link individual tasks to parent epics for better macro-level project tracking.
 3. **Dedicated `testing-strategy` Skill:** Create a template enforcing Test-Driven Development (TDD) or strict coverage thresholds, ensuring OpenCode writes tests before or alongside implementation code.
 4. **Database Migration Management:** Create a `database-migration` skill to strictly forbid direct schema alterations, forcing the use of standard migration tools (Prisma, Alembic, Flyway) for safe, repeatable deployments.
+5. **Automated Prompt Refactoring Pipeline:** Integrate the new `prompt-refactor` skill into an auto-refine pre-hook so that Manager inputs are automatically expanded into elite system prompts before code execution begins.
+6. **Hexagonal Architecture Expansion:** Port the strict Ports & Adapters blueprint from Go to our Python (FastAPI) and TypeScript (Node.js) templates to unify "Max Power" backend design patterns across all supported stacks.
```

<!-- END_GIT_DIFF -->
