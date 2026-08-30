---
created_at: '2026-08-30T10:50:00.000000+00:00'
status: active
tags: []
updated_at: '2026-08-30T10:50:00.000000+00:00'
---

# Fragment-Edit → Regenerate Workflow (Task 129, 2026-08-30)

Verified end-to-end workflow for editing `prompts/fragments/` and keeping `system-prompt.md` in sync. Future tasks touching fragments MUST follow this exact sequence:

1. **Edit the fragment** in `prompts/fragments/` (or shared partial in `prompts/shared/`). NEVER hand-edit `system-prompt.md` directly — it is a GENERATED build artifact.
2. **Bump version** in `prompts/fragments/01-system_version.md` (SemVer: PATCH for bugfix/docs, MINOR for additive non-breaking mandate extensions, MAJOR for rewrites/breaking changes).
3. **Format** the edited Markdown files: `npx prettier --write <files>` (run BEFORE regeneration so the assembled artifact reflects formatted fragments).
4. **Regenerate**: `python3 scripts/prompt-build/assemble_system_prompt.py` (reads `prompts/manifest.txt`, concatenates fragments, resolves `<!--INCLUDE:...-->` markers, writes `system-prompt.md`).
5. **Verify**:
   - `grep -n "<system_version>" prompts/fragments/01-system_version.md system-prompt.md` — both MUST show the SAME bumped version.
   - `grep -n "<new-section-name>" system-prompt.md` — the new content MUST be present in the assembled artifact.
   - `git diff --stat -- 'loop-engine/' '*.py'` — MUST be empty (zero out-of-scope changes).
   - Optionally `lint_system_prompt_sync()` (lint MCP server) or `python3 scripts/prompt-build/assemble_system_prompt.py --output /tmp/check.md && diff /tmp/check.md system-prompt.md` before commit.
6. **Sync docs**: update `CHANGELOG.md` (Parse-Then-Append under the new version header), the active task file, and any affected skill templates/audit checks.

Task 129 applied this workflow: 9 files edited + `system-prompt.md` regenerated (75261 bytes), `<system_version>` 9.1.0 → 9.2.0, `## Decision Detection Responsibility` verified at line 600, zero out-of-scope changes.