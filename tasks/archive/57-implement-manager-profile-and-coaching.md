# Task: Implement Manager Profile & Coaching Protocol

**File:** `tasks/in-progress/57-implement-manager-profile-and-coaching.md`
**Type:** feature
**Status:** closed

## Goal

Introduce a `<manager_profile>` block and `<leadership_and_language_protocol>` into `system-prompt.md` to give the AI deep context about the Manager's background and transform it into an Executive Coach and English Tutor. Update `README.md`, `LLM.txt`, and `CHANGELOG.md` to document this V6.7.0 release.

## Manager's Notes

- Version bump: 6.6.0 → 6.7.0
- The Manager profile defines Mohammad's background (self-taught, Linux/Android expert, transitioning from solo dev to PO/Leadership)
- Coaching protocol covers: vocabulary keyword assistance, English grammar/phonetic corrections, and ruthless soft-skills feedback during sprint retrospectives
- All four files need patches: `system-prompt.md`, `README.md`, `LLM.txt`, `CHANGELOG.md`

## Local TODOs

- [x] **Step 1:** Create task file in `tasks/backlog/`
- [x] **Step 2:** Move task to `tasks/in-progress/`
- [x] **Step 3:** Patch `system-prompt.md` — bump version to 6.7.0, inject `<manager_profile>` and `<leadership_and_language_protocol>`
- [x] **Step 4:** Patch `README.md` — document Manager Profile & AI Coaching section under Quick Start, add Key V6.7 Changes
- [x] **Step 5:** Patch `LLM.txt` — add Section 4 for profile customization, renumber subsequent sections (4→5, 5→6, 6→7)
- [x] **Step 6:** Patch `CHANGELOG.md` — add V6.7.0 release entry
- [x] **Bash Phase:** Format all patched files with prettier
- [x] **Documentation Phase:** Log reasoning in "OpenCode Execution Log & Reasoning"
- [x] **Summary Phase:** Call MCP tool, notify Manager

## OpenCode Execution Log & Reasoning

## Architectural Reasoning

This feature adds a Manager Profile + Coaching Protocol (V6.7.0) to transform the AI from a pure Orchestrator into an Executive Coach that understands the Manager's background and actively tutors English/leadership skills.

## Files Modified

1. **`system-prompt.md`** — Bumped `<system_version>` from 6.6.0 to 6.7.0. Inserted `<manager_profile>` block (Mohammad's background, tech expertise, career trajectory, coaching needs) and `<leadership_and_language_protocol>` (vocabulary assistant, English corrections with Persian phonetics, ruthless sprint retro feedback). Both injected between `</system_context>` and `<agent_skills_registry>`.

2. **`README.md`** — Added "Manager Profile & AI Coaching" section under the Quick Start area explaining the coaching features and how to customize. Added "Key V6.7 Changes" section before Contributing with a changelog summary.

3. **`LLM.txt`** — Added new Section 4 "Customize the Manager Profile" instructing setup agents to advise users to edit the `<manager_profile>` block. Renumbered sections 4→5 (MCP Server), 5→6 (Platform Setup), 6→7 (Verification). Updated cross-reference in Section 1 from "Section 4" to "Section 6".

4. **`CHANGELOG.md`** — Inserted `[6.7.0] — 2026-07-19` release entry with Added categories documenting Manager Profile, Leadership & Language Coaching (with sub-items), and Setup Integration.

## Key Decisions

- Placed the profile and protocol between `</system_context>` and `<agent_skills_registry>` so the AI reads the Manager's context before processing skill rules — this ensures coaching behavior is active from the start of every response.
- Used `<manager_profile>` as a standalone XML tag (not nested) for clarity and easy discoverability by users who want to customize it.
- The protocol explicitly preserves technical workflow — coaching notes are appended at the end (via `> 💡 **Coach's Note:**` blockquote), never interrupting the primary technical output.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `3f0012b561a9edc5fb7fbdd824fb69fb470e7720`
<!-- END_GIT_DIFF -->
