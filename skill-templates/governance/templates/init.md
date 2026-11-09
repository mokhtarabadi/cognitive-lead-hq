## Part 2: Living Folder Docs Initializer (from `init-folder-docs`)

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
     - `- **Context:** Baseline documentation initialized via governance.`
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

---

## Part 3: Project OpenCode Config Generator (from `opencode-init`)

Turn project analysis into a working `opencode.json` for THAT project only.
Analyze stack files, ask the user for gaps (default agent,
formatter, LSP guidance, instructions, permissions), emit JSON matching
the public schema (https://opencode.ai/config.json),
then validate with `scripts/validate-opencode.py` before writing.
MCP servers and plugins install GLOBALLY — never emit `mcp` or `plugin`
into the project file. Never edit global config. Never install plugins.

### Ground Truth (public schema wins)

- Shape: project-only keys: `$schema`, `default_agent`, `instructions[]`, `formatter`, `lsp`, `permission{}`. `mcp{}` and `plugin[]` are GLOBAL-only and banned from project output.
- Formatter: `true` | `false` | named map `{<name>: {command?, extensions?, environment?, disabled?}}`. NEVER emit a flat `{command, extensions}` object — it fails validation. LSP uses flat map `{<name>: {command, extensions?, env?, initialization?, disabled?}}`, NEVER a `language-server` key.
- LSP: `true` | `false` | map `{<name>: {command (required), extensions?, env?, initialization?, disabled?}}`. NEVER wrap in `language-server`; LSP uses `env`.
- Secrets travel ONLY as `{env:NAME}` placeholders in global scope — never literal values. `default_agent` must name an existing primary agent. Merge order: remote → global → custom → project root → subdir.

### Workflow

1. **Analyze.** Read manifests, README, stack files, existing `opencode.json`/`AGENTS.md`/`.opencode/`. Record stack, agents dir, formatter/LSP/instructions/permission needs. Do NOT record MCP needs or plugin choices.
2. **Ask user for gaps.** Missing `default_agent`, formatter/LSP/instructions/permission choices. Ambiguous means NOT answered — HALT and re-ask. Never ask for MCP env keys or plugin selection.
3. **Generate.** Emit project-only JSON (allowlist: `$schema`, `default_agent`, `instructions`, `formatter`, `lsp`, `permission`). Omit `mcp`/`plugin`; note global install paths instead.
4. **Validate, then write.** Run `scripts/validate-opencode.py <file>`. Zero errors required. Write ONLY to target project root `opencode.json`. One project per run. Never touch global config. Never `git commit`. ZAC deny set is mandatory in every generated file: `git add`, `git checkout`, `git commit`, `git push` → `deny`.
