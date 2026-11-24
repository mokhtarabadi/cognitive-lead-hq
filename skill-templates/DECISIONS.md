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

## [2026-11-02] ADR-004: Brief-first candidate approval in telegram-issue-sync

- **Context:** Phase 2 asked the Manager to reply with bare numeric message IDs, which are invisible in official Telegram apps, so the Manager could not join an ID to its message and risked syncing the wrong anchor.
- **Decision:** Each `question`-tool option now leads with a brief ([YYYY-MM-DD HH:MM] sender — first 80 chars, type/topic); the numeric ID stays the machine value only, and the closing prompt asks for option numbers, names, or All, with a numbered-list manual fallback and server-side number-to-ID mapping.
- **Consequences:** The Manager picks by visible brief instead of transcribing IDs; the sync registry still keys on numeric IDs.
- **Rollback:** Restore the prior Phase 2 steps from git history.

<!-- provenance: tasks/in-progress/422-regenerate-stage-prompts-every-release.md -->

## [2026-11-24] ADR-005: Stage-artifact regeneration is conditional and project-agnostic

- **Context:** A release omitted stage-prompt regeneration and shipped stale scoped prompts. The reusable versioning skill needed to prevent the same class of omission without embedding HQ-specific paths or commands.
- **Decision:** Add a conditional rule: repositories that generate stage-scoped prompt artifacts must regenerate the full set and pass their freshness gate before deployment. Concrete commands remain in the owning repository's docs and scripts.
- **Consequences:** Downstream projects receive the safeguard only when their architecture has stage artifacts. The template stays portable and contains no HQ scaffolding.
- **Rollback:** Remove the conditional item from the versioning skill and restore the prior Phase 2 numbering.

<!-- provenance: tasks/in-progress/423-portable-release-omitted-output-brain-skill.md -->

## [2026-11-24] ADR-006: Portable release core plus optional harness profile

- **Context:** The release skill hard-coded HQ files and tools, so downstream projects inherited instructions that did not apply to their repository.
- **Decision:** Split universal release rules into a portable core and move HQ safeguards into a clearly labeled optional Harness Profile. Add a new Brain orchestration template that names the deployed runbook and stage manifest instead of HQ repository paths.
- **Consequences:** Downstream projects receive portable release and Brain guidance. Portability is test-enforced for both templates; harness safeguards remain available where required.
- **Rollback:** Restore the prior skill bodies, remove the Brain template and registry row, and delete the two portability tests.

<!-- provenance: tasks/in-progress/424-raw-first-brain-output.md -->

## [2026-11-24] ADR-007: Brain skill describes raw-first deterministic recovery

- **Context:** The portable Brain skill described pointer recovery but not the raw-before-triage guarantee or the shared deterministic helper.
- **Decision:** Add one portable sentence stating that the deployed bridge preserves raw provider text and exposes one deterministic parse helper, so rejected extraction never hides the complete answer.
- **Consequences:** Downstream users know to read the artifact and validate with the helper before re-emitting, without inheriting HQ repository paths.
- **Rollback:** Remove the added sentence and regenerate the affected skill copy.
