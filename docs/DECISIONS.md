# Architectural Decisions: docs

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-21] ADR-002: Telegram Message Formatting Contract Lives in `docs/`

- **Context:** The Telegram MCP's real formatting behavior (HTML preserved, Markdown fences consumed, 4096-char limit, lost ZWNJ, no `topic_id` on `send_message`) was proven empirically on 2026-10-21 and handed over as a document. It had no home in the repo, so every agent that sends a Telegram message re-derives it or ignores it.
- **Decision:** The contract is stored verbatim as `docs/telegram-message-formatting.md` (server-side facts plus a binding authoring-rules table). The agent-facing rulebook is a skill, `skill-templates/telegram-message-format/SKILL.md`, so the Hands can load it on demand; the doc stays the reference the skill points at.
- **Consequences:** Every Telegram send from a skill or a direct MCP call must load the skill and obey the 9 authoring rules. The two Telegram skills and the Hands skill matrix now name it explicitly.
- **Rollback:** Delete the skill and the doc, and remove the registry line, the skill-matrix row, and the skill references from the two Telegram skills.

## [2026-10-27] ADR-003: Setup Docs Stay Runtime-Neutral

- **Context:** `docs/telegram-setup.md` labeled callback mode "for Claude Code", listed only external MCP clients, and gave a `claude mcp add` command; `docs/brain-bridge.md` presented one vendor trio as the industry pattern. Operating docs must describe this platform first.
- **Decision:** Callback mode is labeled for agentic clients; client lists name OpenCode first with others as compatible examples; the vendor trio became "OpenCode and other agentic clients".
- **Consequences:** Setup docs no longer route the reader to another runtime. External-client interop facts are kept, not deleted.
- **Rollback:** Restore the prior wording from git history.
