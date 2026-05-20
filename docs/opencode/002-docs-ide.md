---
title: IDE
url: https://opencode.ai/docs/ide
source: sitemap
fetched_at: 2026-04-17T06:47:46.20726852-03:00
rendered_js: false
word_count: 251
summary: This document provides instructions for installing, launching, and troubleshooting OpenCode within various compatible IDEs and terminals.
tags:
    - opencode-install
    - cli-usage
    - ide-integration
    - troubleshooting-guide
    - terminal-commands
category: guide
---

OpenCode integrates with VS Code, Cursor, or any IDE that supports a terminal. Just run `opencode` in the terminal to get started.

* * *

## [Usage](#usage)

- **Quick Launch**: Use `Cmd+Esc` (Mac) or `Ctrl+Esc` (Windows/Linux) to open OpenCode in a split terminal view, or focus an existing terminal session if one is already running.
- **New Session**: Use `Cmd+Shift+Esc` (Mac) or `Ctrl+Shift+Esc` (Windows/Linux) to start a new OpenCode terminal session, even if one is already open. You can also click the OpenCode button in the UI.
- **Context Awareness**: Automatically share your current selection or tab with OpenCode.
- **File Reference Shortcuts**: Use `Cmd+Option+K` (Mac) or `Alt+Ctrl+K` (Linux/Windows) to insert file references. For example, `@File#L37-42`.

* * *

## [Installation](#installation)

To install OpenCode on VS Code and popular forks like Cursor, Windsurf, VSCodium:

1. Open VS Code
2. Open the integrated terminal
3. Run `opencode` - the extension installs automatically

If on the other hand you want to use your own IDE when you run `/editor` or `/export` from the TUI, you’ll need to set `export EDITOR="code --wait"`. [Learn more](https://opencode.ai/docs/tui/#editor-setup).

* * *

### [Manual Install](#manual-install)

Search for **OpenCode** in the Extension Marketplace and click **Install**.

* * *

### [Troubleshooting](#troubleshooting)

If the extension fails to install automatically:

- Ensure you’re running `opencode` in the integrated terminal.
- Confirm the CLI for your IDE is installed:
  
  - For VS Code: `code` command
  - For Cursor: `cursor` command
  - For Windsurf: `windsurf` command
  - For VSCodium: `codium` command
  - If not, run `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux) and search for “Shell Command: Install ‘code’ command in PATH” (or the equivalent for your IDE)
- Ensure VS Code has permission to install extensions