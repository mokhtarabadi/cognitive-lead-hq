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

## [2026-11-23] ADR-003: Formatter guard owns the auto-format policy

- **Context:** The project formatter was a bare `ruff format` entry whose binary was absent from PATH, so Python files were silently unformatted. Widening it to prettier, ruff and shfmt through one dispatcher fixes that, but the exclusions the guard applies and the standing `prettier --check "**/*.md"` gate were two hand-maintained lists that disagreed: the guard skipped five path classes the gate still checked.
- **Decision:** `scripts/format-guard.sh` dispatches prettier, ruff and shfmt on `write`/`edit`/`patch` and skips five byte-sensitive path classes. Prettier reads those five from `.prettierignore`. The guard cannot read that file portably in Bash, so it carries the same five classes in one `case` arm, and two assertions in `tests/test_prompt_sync.py` pin the lists against each other in both directions. The guard derives the repo root from its own location, normalizes a repo-relative `$FILE`, refuses any path that resolves outside the repo, and fails loud with a named stderr message when a dispatcher is missing.
- **Consequences:** Gate and auto-formatter cannot disagree without a red test. `prompts/fragments/*`, `prompts/shared/*`, `system-prompt.md`, `build/stage-prompts/*` and `tasks/*` are excluded from both, so their formatting is a review concern rather than a build gate. Install semantics stay asymmetric by necessity: `npx --no-install` never fetches, `uvx` does. One limitation is recorded rather than fixed: `opencode.json` invokes `bash scripts/format-guard.sh` by a repo-relative path, so the guard runs only while the formatter's working directory is the repo root.
- **Rollback:** Delete `.prettierignore`, delete this entry, restore the single `ruff-format` entry in `opencode.json`, delete the guard, and drop the parity assertions.
