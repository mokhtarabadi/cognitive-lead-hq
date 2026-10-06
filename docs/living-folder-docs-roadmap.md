# Living Folder Docs: Architectural Specification & Implementation Roadmap

## 1. Objective

The Living Folder Docs system ensures that architectural knowledge, design rationales, and directory boundaries are colocated with source code in vertical slices or clean architecture component directories. By forcing synchronization across four distinct gates, decisions cannot be silently forgotten, bypassed, or overridden.

## 2. The Four Enforcement Gates

1. **Gate 1: Read Gate (Context Auto-Attach):**
   - Location: `mcp-context-server/server.py`
   - Behavior: When `read_source_files` or `extract_signatures` processes files in a component directory, it automatically resolves and attaches sibling `README.md` and `DECISIONS.md` files so the Brain always inspects existing architectural context.

2. **Gate 2: Write Gate (Agent Constraints & Task Templates):**
   - Locations: `prompts/fragments/13-constraints.md`, `prompts/fragments/09-hands_protocols.md`, `skill-templates/task-generator/`
   - Behavior: When modifying code within a slice, the agent is mandated to inspect and update sibling docs. Implementing without updating relevant ADRs triggers a rule violation warning.

3. **Gate 3: Lint Gate (Static Verification):**
   - Location: `mcp-lint-server/server.py`
   - Behavior: Introduces structural verification (`lint_folder_docs`) ensuring every component slice owns conforming `README.md` and `DECISIONS.md` files and validates top-line source code pointers.

4. **Gate 4: Review Gate (Quality & Persona Enforcement):**
   - Locations: `06-personas.md` (QA Engineer & Code Reviewer)
   - Behavior: QA rejects changes missing documented rationale or invariants. Code Reviewer rejects tasks with stale or desynchronized sibling docs. Human overrides must be recorded as dated ADRs with rollback instructions.

## 3. Touch Points & File Locations

All touch points are anchored in verified repository files:
- `docs/conventions.md`: Canonical definition of the Living Docs standard.
- `prompts/fragments/13-constraints.md`: Sibling docs reading and writing constraints.
- `prompts/fragments/09-hands_protocols.md`: Task execution phases for folder docs sync.
- `prompts/manifest.txt`: Fragment manifest for prompt assembly.
- `agents/cognitive-executor.md`: Mirrored execution rules for the Hands.
- `mcp-context-server/server.py`: Sibling doc resolution in context tools.
- `mcp-lint-server/server.py`: Sibling doc lint rule.
- `06-personas.md`: Adversarial QA and Code Reviewer inspection gates.
- Persistent Memory (`project-memory`): Synchronizing high-level Manager decisions with local slice logs.

## 4. Concrete Reference Example: `todo-app` Vertical Slice

### Directory Layout
```text
src/features/todos/
├── README.md
├── DECISIONS.md
├── todo.model.ts
├── todo.service.ts
└── todo.controller.ts
```

### `src/features/todos/README.md`
```markdown
# Slice: Todos Feature

## Duties
Handles todo creation, completion toggling, filtering, and persistent storage.

## Files
- todo.model.ts: Domain entities and validation schemas.
- todo.service.ts: Business logic, persistence interactions, and error handling.
- todo.controller.ts: HTTP route handlers and request/response mapping.

## Key Risks & Invariants
- Todos must belong to a verified tenant; never query across tenant boundaries.
- Soft-deleted items must not appear in count aggregations.
```

### `src/features/todos/DECISIONS.md`
```markdown
# Architectural Decisions: Todos Feature

## [2026-08-25] ADR-001: Soft Deletion via Sidecar DeletedAt Column
- Context: Hard deletion caused cascade failures with audit reports.
- Decision: All deletion marks deleted_at timestamp; queries filter deleted_at IS NULL.
- Consequences: Existing indexes required compound update on (tenant_id, deleted_at).
- Rollback: Revert migration 0042 and restore hard delete cascade.
```

### Code Pointer Standard (`src/features/todos/todo.service.ts`)
```typescript
// Sibling Docs: src/features/todos/README.md | Decisions: src/features/todos/DECISIONS.md
export class TodoService {
  // implementation
}
```

## 5. Phased Implementation Breakdown (Follow-Up Tasks)

- **Phase 1 (Conventions & System Prompts):** Update `docs/conventions.md`, prompt fragments `13-constraints.md` and `09-hands_protocols.md`, assemble `system-prompt.md`, and mirror in `agents/cognitive-executor.md`.
- **Phase 2 (MCP Context & Lint Tooling):** Add sibling doc auto-attachment in `mcp-context-server/server.py` and structural validation in `mcp-lint-server/server.py`.
- **Phase 3 (Task Templates & Skills):** Update `task-generator` template to mandate folder-docs checklist items.
- **Phase 4 (Persona Gates & ADR Memory Integration):** Wire QA/Reviewer adversarial gates and test the full cycle on a sample slice.
