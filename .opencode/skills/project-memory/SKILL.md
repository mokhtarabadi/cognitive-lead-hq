---
name: project-memory
description: Smart note-taking and persistent project memory. Automatically saves Manager constraints and proactively retrieves context to prevent hallucinations.
---

# Project Memory Skill

## Purpose

This skill provides persistent, long-term memory for the project. It prevents the Manager from having to repeat project-specific rules, quirks, test commands, or architectural decisions. It uses the `mcp-memory-server` to slice notes into logical namespaces, preventing context bloat.

## When to STORE Memory (Trigger)

Whenever the Manager explicitly states a rule, preference, or architectural constraint (e.g., "For this project, always use flag X" or "Never use Prisma push"), you MUST proactively save this context.

1. Choose a logical `namespace` (e.g., `testing`, `database`, `deployment`, `quirks`).
2. Choose a concise, snake_case `key` (e.g., `prisma_migration_rule`).
3. Call the `store_memory` MCP tool with the content. Ensure `overwrite=True` if updating an existing rule.

## When to DELETE Memory (Trigger)

If the Manager explicitly states that a previous rule or constraint is no longer valid, or if supersession requires deletion:

1. **Safety Gate:** Before calling `delete_memory`, you MUST output: "⚠️ Memory deletion requested: `{namespace}/{key}`. Manager, please confirm."
2. Wait for explicit Manager approval (unless it is an automatic store-time supersession within the same namespace/key topic, which is logged as `Supersedes: {old_namespace}/{old_key}`).
3. Upon approval, call `delete_memory` with the obsolete `namespace` and `key` to prune the memory bank.

## Supersession Detection Heuristic

When storing a new memory, check if an existing memory in the same namespace covers the same topic:

1. Before calling `store_memory`, call `search_memory` with the key topic keywords.
2. If a matching memory exists, compare dates/task references.
3. If the new memory supersedes the old one (newer date, updated workflow, or explicit Manager instruction), call `delete_memory` on the old entry BEFORE storing the new one. This is the ONE allowed auto-deletion path — it only applies during store-time supersession within the same namespace and key topic. All other memory deletions require Manager approval.
4. Log the supersession in the new memory's content: `Supersedes: {old_namespace}/{old_key}`.

## Memory Index (Auto-Generated)

**Canonical location:** `.opencode/memory/index.md` — auto-generated Markdown index of all memory shards. Do not edit directly.

- **Format:** `| Namespace | Key | Summary | Tags |` Markdown table, sorted by `namespace` then `key`. `Summary` is the first non-empty content line after frontmatter, clamped to 120 chars, pipes escaped. `Tags` from frontmatter `tags:`.
- **Generation:** Atomically rebuilt after every successful `store_memory` and `delete_memory` via `build_memory_index()` (`tempfile.mkstemp(dir=MEMORY_DIR)` + `os.replace` + `fsync` dir). Handles empty store (`*No memories recorded yet.*`) and pipe-escaping. Failures are logged but never fail the parent mutation. Also exposed as `rebuild_memory_index` MCP tool for manual recovery after out-of-band file operations.
- **Workflow (Two-Step — Mandatory):**
  1. **Phase 0 — Read the index:** In the Context Phase, read `.opencode/memory/index.md` (if present) alongside `AGENTS.md`/`DESIGN.md` to get a compact overview *before* planning.
  2. **Selective fetch:** Choose relevant rows from the index, then fetch the full content via `read_memory(namespace, key)` or `search_memory(query)` — never auto-load all memories.

The index is derived state: it will be recreated automatically; do not commit it as a source of truth, and do not create `TODO.md`/`STATE.md` equivalents elsewhere.

## When to RETRIEVE Memory (Trigger)

At the start of EVERY new implementation task (during the Context Phase):

1. Identify the domain of the task (e.g., are we modifying Docker? Writing Jest tests? Editing Auth?).
2. Call `search_memory` using keywords related to that domain, OR call `list_namespaces` and then `read_memory` for specific keys.
3. Inject these retrieved constraints into your reasoning log to ensure you do not violate established project rules.
