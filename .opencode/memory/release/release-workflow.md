---
created_at: '2026-08-17T09:55:12.993426+00:00'
status: active
tags: []
updated_at: '2026-09-03T08:15:00.000000+00:00'
---

Release workflow for cognitive-lead-hq.

Purpose: standardize future releases and prevent forgotten release gates.

Before every release:
- Load these skills: versioning-and-release, project-memory, verification-before-completion, task-lint.
- Search project memory for release constraints and prior release decisions.
- Confirm the release version against SemVer:
  - PATCH: bug fixes, docs sync, formatting, metadata-only changes.
  - MINOR: new skills, new workflow capabilities, non-breaking architectural upgrades.
  - MAJOR: breaking workflow changes or full system prompt protocol rewrites.

CHANGELOG rules:
- Use Keep a Changelog format.
- Use Parse-Then-Append: never create duplicate version headers or duplicate category headers.
- Categories: Added, Changed, Deprecated, Removed, Fixed, Security.
- The [Unreleased] section MUST be empty after a release. Move all entries under the release version header before closing the release task.
- If system-prompt.md behavior changes, bump prompts/fragments/01-system_version.md and reassemble via scripts/prompt-build/assemble_system_prompt.py.
- If the release is metadata/docs-only, the CHANGELOG entry MUST explicitly state: system-prompt.md version unchanged.

Prompt source rules:
- system-prompt.md is generated from prompts/fragments/ and prompts/shared/.
- Never hand-edit system-prompt.md.
- Before release staging, verify sync with lint_system_prompt_sync or by assembling to a temp path and diffing against system-prompt.md.

Verification gates before staging:
- lint_task_file passes for the active release task.
- lint_markdown passes for edited Markdown files.
- lint_system_prompt_sync reports in sync.
- python3 -m py_compile passes for prompt-build scripts and lint server.
- full pytest suite passes.

ZAC-safe commit rules:
- Hands MUST NOT run git add, git commit, git push, git tag, or gh release create.
- Hands stage only via custom_context_stage_and_inject_diff.
- Hands commit only via custom_context_commit_and_clean_task after explicit Manager closure approval.
- Public tag/release publication is a separate manual Manager step after closure.

Push-script generation (since v9.8.0 — Task 157):
- On every future `create release` request, Hands MUST also create an executable push script at `/tmp/cognitive-lead-push-release.sh` for manual Manager execution.
- Script MUST start with `set -euo pipefail`, detect repo root via `git rev-parse --show-toplevel`, define `VERSION="vX.Y.Z"` for the release, verify clean working tree and `gh auth status`, create annotated tag if missing (`git tag -a vX.Y.Z -m "release vX.Y.Z"`), push commits (`git push origin <branch>`) and tags (`git push origin --tags`), then create or verify GitHub Release (`gh release view vX.Y.Z` check → `gh release create vX.Y.Z --title "Cognitive Lead AI HQ vX.Y.Z" --generate-notes`), and print verification (`git ls-remote --tags origin` + `gh release view` URL).
- Script MUST be `chmod +x` and documented in the release task's Acceptance Criteria and CHANGELOG entry.
- This workflow is ZAC-compliant: Hands generate the script but never execute `git push`/`gh release create` themselves; Manager runs `/tmp/cognitive-lead-push-release.sh` manually after closure.

Memory rule:
- This memory lives at release/release-workflow.
- Future release tasks must retrieve and follow this memory before making release decisions.
