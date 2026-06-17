# Task: Create Telegram Message Export Skill

**Type:** feature
**Status:** open

## Goal

Create a new Agent Skill that exports a range of Telegram messages (text, images, voice notes) into a numbered folder and packs them into a ZIP archive.

## Manager's Notes

- Three input methods: message ID range, message link, text search
- Skill lives at `skill-templates/telegram-message-export/SKILL.md`
- Must also be installed globally at `~/.config/opencode/skills/telegram-message-export/SKILL.md`

## Local TODOs

- [x] Initial codebase exploration
- [x] Create skill-templates/telegram-message-export/SKILL.md
- [x] Install globally at ~/.config/opencode/skills/telegram-message-export/SKILL.md
- [x] Update CHANGELOG.md with 5.8.0 entry
- [x] Create this task file

## OpenCode Execution Log & Reasoning

The user requested a Telegram message extraction tool. Rather than extending the existing `telegram-issue-sync` skill (which focuses on hashtag-based issue tracking and GitHub sync), I created a new dedicated `telegram-message-export` skill with a clean, single-purpose workflow.

Key design decisions:
- **Three input methods** — message ID range, message link parsing, and text search cover all realistic use cases
- **Numbered output files** — sequential `1.txt`, `2.jpeg`, etc. are intuitive and easy to reference
- **Sidecar text files** — when a message has both media and text, both share the same number (e.g., `5.txt` describes `5.jpeg`)
- **ZIP packaging** — single archive file is easy to transfer or download

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

_(Git diff will be automatically injected here by the MCP tool. Do not edit this block manually)_

<!-- END_GIT_DIFF -->
