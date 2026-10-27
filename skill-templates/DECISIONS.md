# Architectural Decisions: skill-templates

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-21] ADR-002: Telegram Message Formatting Is a Skill, Not an Inline Rule
- **Context:** The Telegram MCP server does not behave like the Bot API — `parse_mode: "Markdown"` strips code fences without creating entities, `*bold*` stays literal, payloads over 4096 characters fail with an opaque `GEN-ERR-184`, U+200C ZWNJ is dropped on the read path, and `send_message` has no `topic_id` so it lands in General. Without a shared rule, each Telegram skill re-derives (or ignores) the behavior and messages render broken.
- **Decision:** Add a dedicated `telegram-message-format` skill holding the nine binding authoring rules, the message templates, and the pre-send checklist. The two Telegram skills load it in their mandatory-skill phase; the HQ evidence document `docs/telegram-message-formatting.md` stays the reference the skill points at.
- **Consequences:** One place owns Telegram render correctness; the skill is discoverable through the agent skills registry and loadable on demand by any agent that sends a Telegram message. The template stays project-agnostic — no HQ paths, task numbers, or chat ids inside it.
- **Rollback:** Delete `skill-templates/telegram-message-format/`, remove the registry line, the skill-matrix row, and the skill references from the two Telegram skills.

## [2026-10-27] ADR-003: doc-coauthoring Goes Runtime-Neutral

- **Context:** The skill was written for another agent runtime: it named `Claude` in 22 places, `create_file`/`str_replace` for edits, Claude Artifacts for drafting, Claude-settings connectors for integrations, and `claude.ai` for reader testing. None of those exist in OpenCode sessions, so every instruction misfired.
- **Decision:** Remap to native tools: `write` creates the draft, `edit` makes every change, the `subagent` tool runs reader testing with a same-session fallback, and integrations resolve to MCP servers or pasted content. The three-stage workflow is unchanged.
- **Consequences:** The skill now executes in OpenCode without translation. A registry test fails on any reintroduced Claude-centric term.
- **Rollback:** Restore the prior SKILL.md from git history.
