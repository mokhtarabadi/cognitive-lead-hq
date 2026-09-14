# Runtime Matrix: V1 (this repo's runtime) vs V2 (public schema)

| Area | V1 — EMIT THIS | V2 — REJECT |
| ---- | -------------- | ----------- |
| Top level | `$schema`, `default_agent`, `instructions[]`, `plugin[]`, `mcp{}`, `permission{}` | `permissions[]` array |
| Permission entries | `"tool-name": "allow\|ask\|deny"` flat map | `{permission: ..., pattern: ...}` objects |
| Bash rules | `permission.bash = {"git commit": "deny", ...}` string map | Structured rule objects |
| MCP local | `{type: local, command: [...], enabled, timeout, environment?}` | Remote-first / auth-object forms |
| LSP | `language-server: {name: {command}}` map (experimental, env-gated) | `enabled` + per-extension bool/object |
| Secrets | `"{env:NAME}"` placeholders only | Literal values (validator fails these) |
| Plugin env | dict `environment` with `{env:}` values only | Literal values (validator fails these) |

Rule: when the public schema and the local golden file disagree, the golden
file (`references/examples/golden-opencode.json`) wins. The validator
enforces this table.
