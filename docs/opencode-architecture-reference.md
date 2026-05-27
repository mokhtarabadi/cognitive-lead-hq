# OpenCode Architecture Reference

## Configuration Hierarchy & Precedence

OpenCode loads configuration in the following merge order (later sources override earlier ones):

1. **Remote** — Settings fetched from a remote URL (if configured).
2. **Global** — `~/.config/opencode/opencode.json` (user-wide defaults).
3. **Custom path** — Explicit path passed via `--config` flag or `OPENCODE_CONFIG_PATH` env var.
4. **Per project** — JSON/JSONC file at the project root (e.g., `opencode.json`, `opencode.jsonc`).
5. **`.opencode/`** — Config files inside the `.opencode/` directory.
6. **Inline** — Configuration embedded in `AGENTS.md` or `SYSTEM.md` YAML frontmatter.
7. **Managed files** — `.opencode.json` auto-generated or managed by OpenCode itself.
8. **macOS MDM plist** — System-managed policy plist (macOS only).

**Formatting Notes:**

- Accepts both `.json` and `.jsonc` (JSON with Comments) formats.
- JSONC allows trailing commas and `//` or `/* */` style comments, useful for large config files with inline documentation.

---

## Permissions Engine

OpenCode uses a permission rule system to control tool access and file system operations.

### Object Syntax

```json
{
  "permissions": {
    "glob": true,
    "read": true,
    "write": ["**/*.md", "src/**"],
    "bash": false,
    "edit": ["src/**", "!src/generated/**"]
  }
}
```

### Wildcard Rules

- `true` — allow all
- `false` — deny all
- Array of glob patterns — allow matching paths only
- `!` prefix — negate/deny a pattern (used alongside allow patterns)

### Last Matching Rule Wins

Rules are evaluated in order; the **last matching rule** determines the outcome. This allows layered permissions where a broad allow can be narrowed by a later rule:

```json
{
  "permissions": {
    "write": ["**/*", "!.env", "!secrets/**"]
  }
}
```

In this example, all files are writable except `.env` and anything under `secrets/`.

### Safety Defaults

The following are blocked by default unless explicitly overridden:

| Pattern              | Default | Reason                                                  |
| -------------------- | ------- | ------------------------------------------------------- |
| `.env`               | blocked | Prevents secret leakage                                 |
| `doom_loop`          | ask     | Prompts before running potentially infinite loops       |
| `external_directory` | ask     | Prompts before accessing files outside the project root |

---

## LSP and Formatters

OpenCode auto-detects language servers and formatters based on project files:

| Language              | Detection Trigger                                | LSP / Formatter                          |
| --------------------- | ------------------------------------------------ | ---------------------------------------- |
| JavaScript/TypeScript | `package.json`, `tsconfig.json`                  | `typescript-language-server`, `prettier` |
| Python                | `pyproject.toml`, `requirements.txt`, `setup.py` | `pyright`, `ruff`                        |
| Go                    | `go.mod`                                         | `gopls`, `gofumpt`                       |
| Rust                  | `Cargo.toml`                                     | `rust-analyzer`, `rustfmt`               |
| Java/Kotlin           | `pom.xml`, `build.gradle`, `build.gradle.kts`    | `jdtls`, `kotlin-language-server`        |
| Ruby                  | `Gemfile`                                        | `solargraph`, `rubocop`                  |
| PHP                   | `composer.json`                                  | `intelephense`, `php-cs-fixer`           |
| C/C++                 | `CMakeLists.txt`, `Makefile`                     | `clangd`, `clang-format`                 |
| C#                    | `*.csproj`, `solution.sln`                       | `csharp-ls`, `dotnet-format`             |

Formatter settings are read from the project's existing config files (e.g., `.prettierrc`, `ruff.toml`, `editorconfig`). If none are found, OpenCode applies sensible defaults.

---

## Agents & Subagents

### Primary Agents

| Agent     | Mode    | Purpose                                                                |
| --------- | ------- | ---------------------------------------------------------------------- |
| **Build** | `build` | Executes implementation tasks, runs tests, writes code                 |
| **Plan**  | `plan`  | Analyzes requirements, designs architecture, asks clarifying questions |

### Subagents

| Agent       | Tool Access                    | Purpose                                   |
| ----------- | ------------------------------ | ----------------------------------------- |
| **General** | All tools                      | Complex multi-step research and execution |
| **Explore** | `read`, `glob`, `grep`, `task` | Fast codebase exploration (read-only)     |

### Multi-Turn Session Navigation

When working within agentic sessions, use the following leader keybindings:

| Binding               | Action                                     |
| --------------------- | ------------------------------------------ |
| `Leader + Left/Right` | Switch between parent and child sessions   |
| `Leader + Up/Down`    | Navigate between sibling subagent sessions |

---

## Tool Mechanics

### `apply_patch` (Critical)

The `apply_patch` tool parses **path marker lines** embedded in the `patchText` string to determine which files to modify. It does **not** use a separate `filePath` argument.

**Path marker syntax:**

```
*** Add File: <relative-path-from-project-root>
*** Update File: <relative-path-from-project-root>
```

**Example:**

```
*** Update File: src/utils/helpers.ts
@@ ... @@
-const oldCode = "foo";
+const newCode = "bar";
```

All paths are resolved **relative to the project root directory**. The tool supports:

- `*** Add File:` — Creates a new file at the specified path.
- `*** Update File:` — Applies a diff/patch to an existing file.
- Standard unified diff format (`@@ ... @@`) for the actual patch content.

### `question`

The `question` tool creates interactive multi-option prompts. Schema:

```json
{
  "name": "question",
  "arguments": {
    "questions": [
      {
        "question": "What database do you want to use?",
        "header": "Database Choice",
        "options": [
          {
            "label": "PostgreSQL",
            "description": "ACID-compliant, good for complex queries"
          },
          {
            "label": "SQLite",
            "description": "Embedded, zero-config, good for small projects"
          },
          {
            "label": "MongoDB",
            "description": "Document-based, good for flexible schemas"
          }
        ],
        "multiple": false
      }
    ]
  }
}
```

Key fields:

- `questions` — Array of question objects (supports multiple questions in one call).
- `question` — The prompt text shown to the user.
- `header` — A short label (max 30 characters) displayed as a title.
- `options` — Array of choices, each with `label` and `description`.
- `multiple` — When `true`, allows selecting more than one option.
- A "Type your own answer" option is automatically appended when `multiple` is `false`, allowing free-text input.
