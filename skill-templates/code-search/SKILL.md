---
name: code-search
description: Mandatory workflow for exploring the codebase and gathering context for AI Studio.
---

# Code Search & Discovery Strategy

You are the Executor. Your job is to extract codebase context so the Manager can upload it to the Orchestrator (Google AI Studio).

**CRITICAL GUARDRAIL:** You MUST NOT read, analyze, or process the generated reports yourself. You are strictly a data gatherer in this phase.

## Discovery Workflow

1. **Map the Structure:** Call the `custom_context_get_directory_tree` MCP tool on the target directory (e.g., `.`, `src/`, `packages/`).

2. **Prefer Signature Extraction Over Full Reads:** Before reading a single file body, you MUST call `custom_context_extract_signatures` on every file or directory you plan to explore. This tool uses **tree-sitter AST** (not regex) to extract structural signatures — classes, functions, methods, interfaces, enums, type aliases — across all major languages. Signature extraction costs a fraction of the tokens compared to reading the full file, and is strictly preferred for initial exploration.

3. **Target Files:** Use the directory tree AND the extracted signatures together to identify exactly which files contain the logic relevant to the Manager's request. The signatures give you a structural map of each file's exports without loading its body.

4. **Compile Report (Only When Necessary):** Call `custom_context_read_source_files` ONLY when you have already narrowed the exploration to specific files and need their full bodies for detailed analysis. For broad exploration, signatures alone are sufficient.

5. **Halt and Handover:** Once the `custom_context_read_source_files` tool returns the generated file path, **STOP**. Do NOT use your `read` tool to open the report.

6. **Output Message:** Output the following exact message to the Manager:
   > "✅ Discovery complete. I have compiled the context report here: `[INSERT_FILE_PATH]`.
   > **Manager:** Please upload this file to AI Studio for the Orchestrator's review."

---

### Vertical Slicing Strategy

When the Orchestrator requests context for a **specific feature module** (e.g., `packages/billing/`, `src/features/auth/`, `apps/web/app/dashboard/`), follow this strategy instead of scanning the entire repository:

1. **Target the Slice:** Run `custom_context_get_directory_tree` on the specific feature directory only — not the whole repo.
2. **Extract Signatures:** Run `custom_context_extract_signatures` on all files within that slice to map its structural surface without full body reads.
3. **Core SOP Files (Mandatory):** Regardless of the slice, **always** append the full text of `AGENTS.md`, `DESIGN.md`, and `docs/*.md` to the final context report. This ensures the AI Studio Brain is always grounded in the project's global rules and design system.
4. **Dependency Trace:** If the slice imports from other local modules (e.g., shared `lib/` or `core/` packages), trace and include signatures for those dependencies too.
5. **Compile:** Call `custom_context_read_source_files` only for the slice's key files and the mandatory Core SOP files.

**Why this matters:** Full-repo scans waste tokens and dilute signal. Vertical Slicing focuses the Brain on the exact feature boundaries that matter, while the mandatory Core SOP injection guarantees structural alignment with the project's architecture.

---

## Signature Extraction (`custom_context_extract_signatures`) — Details

### Why Prefer Signatures Over Full File Reads?

| Approach                           | Token Cost                          | Structural Accuracy                         | Speed                  |
| ---------------------------------- | ----------------------------------- | ------------------------------------------- | ---------------------- |
| `extract_signatures` (tree-sitter) | **Very low** — only signature lines | **High** — AST-parsed, no regex blind spots | Instant                |
| `read_source_files` (full body)    | **High** — entire file bodies       | N/A (full content)                          | Slower for large files |

For repositories with many files, extracting signatures first lets you decide which 2–3 files genuinely need full reading. This directly prevents context bloat in the AI Studio session.

### Languages Supported (Tree-Sitter AST)

| Language       | Signatures Detected                                                                |
| -------------- | ---------------------------------------------------------------------------------- |
| **Python**     | `def`, `class`                                                                     |
| **JavaScript** | `function`, `class`, `method`, `arrow function`, `generator`                       |
| **TypeScript** | `function`, `class`, `interface`, `type alias`, `enum`, `method`, `arrow function` |
| **Java**       | `method`, `class`, `interface`, `enum`, `record`                                   |
| **Kotlin**     | `fun`, `class`                                                                     |
| **Go**         | `func`, `method`, `type struct`                                                    |
| **Rust**       | `fn`, `struct`, `enum`, `trait`, `type alias`, `impl`                              |

For languages not listed above, the tool gracefully falls back to regex-based extraction (class/function/def/interface patterns).

### What Signatures Include

- **Function/method signatures:** name, parameters (including type annotations), return type, decorators if on the same line
- **Class definitions:** name, parent class/interface if on the same line
- **Interface/trait definitions:** name
- **Type aliases:** name, type expression
- **Enum definitions:** name
- **Record/struct definitions:** name
- **Multi-line parameter lists:** correctly captured until the closing `)` or opening `{`

### What Signatures Exclude (Intentionally)

- **Function/class bodies** — the body is cut off at the opening `{` or `:` to minimize token usage
- **Decorators on separate lines** — only the decorated definition line is captured
- **Comments and docstrings** — structural intent only
- **Imports and module-level variables** — these are not structural signatures

### Example Usage

```json
// Extract signatures from a single file
custom_context_extract_signatures({ "file_path": "src/services/user_service.py" })
// Returns: class UserService:, def get_user_by_id(id: int) -> User:, def create_user(data: CreateUserDTO) -> User:

// Extract signatures from multiple files
custom_context_extract_signatures({ "file_path": "src/components/Button.tsx" })
// Returns: interface ButtonProps:, const Button: React.FC<ButtonProps> =>, function handleClick():
```
