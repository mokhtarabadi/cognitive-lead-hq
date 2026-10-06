---
name: init-folder-docs
description: Scaffolds living folder docs (README.md, DECISIONS.md, and code pointers) across component directories and vertical slices in legacy or uninitialized codebases.
---

# Skill: Living Folder Docs Initializer

Use this skill to onboard existing projects to the Living Folder Docs standard by discovering component directories and scaffolding baseline documentation and code pointers.

## Scope Confinement

- Confine all file scans and generation strictly to `[PROJECT_ROOT]`.
- Never touch vendor or build directories (`node_modules/`, `.git/`, `dist/`, `build/`, `.venv/`, `vendor/`, `target/`).

## Workflow

1. **Slice Discovery:**
   - Search the repository for distinct vertical slices, modules, or domain component directories (e.g., `src/features/*`, `apps/*/src/modules/*`, `services/*`, `backend/src/*`).
   - List all discovered directory paths.

2. **Scaffold Missing Slice Docs:**
   For each discovered directory `[DIR]`:
   - **README.md:** If `[DIR]/README.md` does not exist, create it with:
     - `# Slice: [DIR_NAME]`
     - `## Duties` (Derived from contained file names and directory role)
     - `## Files` (List of contained source files with brief 1-line description)
     - `## Key Risks & Invariants` (Baseline invariants and known edge cases)
   - **DECISIONS.md:** If `[DIR]/DECISIONS.md` does not exist, create it with:
     - `# Architectural Decisions: [DIR_NAME]`
     - `## [YYYY-MM-DD] ADR-001: Initial Slice Baseline`
     - `- **Context:** Baseline documentation initialized via init-folder-docs.`
     - `- **Decision:** Adopting Living Folder Docs standard for this component.`
     - `- **Consequences:** All future structural or contract changes must be recorded here.`
     - `- **Rollback:** N/A (baseline adoption).`

3. **Inject Code Pointers:**
   - In primary source files within `[DIR]` (e.g. main service, controller, model, or entry file), inspect the first 5 lines.
   - If no sibling docs comment exists, inject the top-line comment pointer:
     - JS/TS: `// Sibling Docs: [DIR]/README.md | Decisions: [DIR]/DECISIONS.md`
     - Python/Shell: `# Sibling Docs: [DIR]/README.md | Decisions: [DIR]/DECISIONS.md`

4. **Verification & Summary:**
   - Run `git status` (read-only) to review generated files.
   - Output a concise summary listing:
     - Discovered Slices: count and paths
     - Created `README.md` files
     - Created `DECISIONS.md` files
     - Injected code pointers count
