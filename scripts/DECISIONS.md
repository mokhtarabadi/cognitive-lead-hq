# Architectural Decisions: scripts

## [2026-10-24] ADR-002: Prompt split covers `night_mode` and the trailing Markdown section

- **Context:** `system-prompt.md` is a generated artifact, but `split_system_prompt.py` still knew 20 top-level tags. The prompt had since gained `<night_mode>` (tag 23) and a plain-Markdown language-policy section after the last tag, so rebuilding from fragments dropped both: the round-trip test in `tests/test_mcp_servers.py` failed with `<night_mode>` missing from the assembled output. Rebuilding also renumbered every fragment, renaming ~20 tracked files for no content change.
- **Decision:** `night_mode` joins `TOP_LEVEL_TAGS` in document order, and the trailing non-tag section is captured as a final fragment whose name comes from its first heading (`language_policy`). Filenames already present in an existing manifest are reused by their tag/slug instead of being renumbered, so a rebuild is idempotent on disk and the manifest keeps its committed names (`23-night_mode.md`, `24-language_policy.md`).
- **Consequences:** `assemble(split(system-prompt.md))` is byte-identical again (108,394 bytes at the time of the fix), a rebuild no longer silently drops a policy block, and fragment names stay stable across runs. The tail fragment has no XML tag, so the splitter now depends on the file ending with a Markdown section; adding text after it is captured, while text inserted between tagged blocks still requires a tag.
- **Rollback:** Drop the tail-capture block and the `night_mode` entry, and restore per-tag numbering; the round-trip test goes back to failing.

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).
