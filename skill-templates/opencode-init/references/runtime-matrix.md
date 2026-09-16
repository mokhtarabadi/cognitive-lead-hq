# Runtime Matrix: V1 (this repo's runtime) vs V2 (public schema)

| Area | V1 — EMIT THIS | V2 — REJECT |
| ---- | -------------- | ----------- |
| Top level (project) | `$schema`, `default_agent`, `instructions[]`, `formatter`, `lsp`, `permission{}` | `permissions[]` array; `mcp{}` and `plugin[]` (global-only) |
| Permission entries | `"tool-name": "allow\|ask\|deny"` flat map | `{permission: ..., pattern: ...}` objects |
| Bash rules | `permission.bash = {"git commit": "deny", ...}` string map | Structured rule objects |
| MCP | GLOBAL-ONLY — install in `~/.config/opencode/opencode.json`; banned from project output | Any `mcp{}` block in a generated project file |
| Plugin | GLOBAL-ONLY — npm spec in global config or `.opencode/plugins/` / `~/.config/opencode/plugins/`; banned from project output | Any `plugin[]` list in a generated project file |
| LSP (project guidance) | flat map `{name: {command, extensions?, env?, initialization?, disabled?}}` — e.g. `{"typescript": {"command": [...]}}`; `true`/`false` also valid; server install stays host/global side | `language-server` wrapper (`{language-server: {name: ...}}`), `environment` (LSP uses `env`), unknown keys |
| Formatter (project) | `true` (all built-ins) \| `false` (disable) \| named map `{<name>: {command?, extensions?, environment?, disabled?}}` — e.g. `{"spotless-java": {"command": [...], "extensions": [".java"]}}` | flat `{command, extensions}` without a name key |
| Secrets (global scope) | `"{env:NAME}"` placeholders only — project output carries no secret-bearing blocks | Literal values (validator fails these) |
| Plugin env (global scope) | dict `environment` with `{env:}` values only | Literal values (validator fails these) |

Rule: when the public schema and the local golden file disagree, the golden
file (`references/examples/golden-opencode.json`) wins. The validator
enforces this table.
