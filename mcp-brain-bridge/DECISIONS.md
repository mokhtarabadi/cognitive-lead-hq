# Architectural Decisions: mcp-brain-bridge

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-12] ADR-002: Dual-mode XML extraction (bare + fenced fallback)

- **Context:** Manual copy-paste mode needs forced ```xml fences; automatic MCP mode needs bare XML. The strict fence reject forced a wasted re-emit turn.
- **Decision:** Bare unfenced blocks extract first; explicit ```xml fences extract second; other fences stay documentation-only; bare unclosed tails still strict-reject.
- **Consequences:** Both modes extract without re-emit; fence-fallback tests pin extraction.
- **Rollback:** Revert extract_xml_blocks fallback hunk and fence tests to strict-reject form.
