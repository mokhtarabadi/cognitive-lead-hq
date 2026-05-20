---
title: TUI
url: https://opencode.ai/docs/tui/
source: crawler
fetched_at: 2026-02-14T12:04:42.616387-03:00
rendered_js: false
word_count: 638
summary: This document provides a comprehensive guide on using the OpenCode terminal user interface (TUI), detailing its commands, file referencing system, shell integration, and customization settings.
tags:
    - opencode
    - tui
    - cli
    - terminal-interface
    - developer-tools
    - configuration
category: guide
---

Using the OpenCode terminal user interface.

OpenCode provides an interactive terminal interface or TUI for working on your projects with an LLM.

Running OpenCode starts the TUI for the current directory.

Or you can start it for a specific working directory.

```

opencode/path/to/project
```

Once you’re in the TUI, you can prompt it with a message.

```

Give me a quick summary of the codebase.
```

* * *

## [File references](#file-references)

You can reference files in your messages using `@`. This does a fuzzy file search in the current working directory.

```

How is auth handled in @packages/functions/src/api/index.ts?
```

The content of the file is added to the conversation automatically.

* * *

## [Bash commands](#bash-commands)

Start a message with `!` to run a shell command.

The output of the command is added to the conversation as a tool result.

* * *

## [Commands](#commands)

When using the OpenCode TUI, you can type `/` followed by a command name to quickly execute actions. For example:

Most commands also have keybind using `ctrl+x` as the leader key, where `ctrl+x` is the default leader key. [Learn more](https://opencode.ai/docs/keybinds).

Here are all available slash commands:

* * *

### [connect](#connect)

Add a provider to OpenCode. Allows you to select from available providers and add their API keys.

* * *

### [compact](#compact)

Compact the current session. *Alias*: `/summarize`

**Keybind:** `ctrl+x c`

* * *

### [details](#details)

Toggle tool execution details.

**Keybind:** `ctrl+x d`

* * *

### [editor](#editor)

Open external editor for composing messages. Uses the editor set in your `EDITOR` environment variable. [Learn more](#editor-setup).

**Keybind:** `ctrl+x e`

* * *

### [exit](#exit)

Exit OpenCode. *Aliases*: `/quit`, `/q`

**Keybind:** `ctrl+x q`

* * *

### [export](#export)

Export current conversation to Markdown and open in your default editor. Uses the editor set in your `EDITOR` environment variable. [Learn more](#editor-setup).

**Keybind:** `ctrl+x x`

* * *

### [help](#help)

Show the help dialog.

**Keybind:** `ctrl+x h`

* * *

### [init](#init)

Create or update `AGENTS.md` file. [Learn more](https://opencode.ai/docs/rules).

**Keybind:** `ctrl+x i`

* * *

### [models](#models)

List available models.

**Keybind:** `ctrl+x m`

* * *

### [new](#new)

Start a new session. *Alias*: `/clear`

**Keybind:** `ctrl+x n`

* * *

### [redo](#redo)

Redo a previously undone message. Only available after using `/undo`.

Internally, this uses Git to manage the file changes. So your project **needs to be a Git repository**.

**Keybind:** `ctrl+x r`

* * *

### [sessions](#sessions)

List and switch between sessions. *Aliases*: `/resume`, `/continue`

**Keybind:** `ctrl+x l`

* * *

Share current session. [Learn more](https://opencode.ai/docs/share).

**Keybind:** `ctrl+x s`

* * *

### [themes](#themes)

List available themes.

**Keybind:** `ctrl+x t`

* * *

### [thinking](#thinking)

Toggle the visibility of thinking/reasoning blocks in the conversation. When enabled, you can see the model’s reasoning process for models that support extended thinking.

* * *

### [undo](#undo)

Undo last message in the conversation. Removes the most recent user message, all subsequent responses, and any file changes.

Internally, this uses Git to manage the file changes. So your project **needs to be a Git repository**.

**Keybind:** `ctrl+x u`

* * *

### [unshare](#unshare)

Unshare current session. [Learn more](https://opencode.ai/docs/share#un-sharing).

* * *

## [Editor setup](#editor-setup)

Both the `/editor` and `/export` commands use the editor specified in your `EDITOR` environment variable.

- [Linux/macOS](#tab-panel-4)
- [Windows (CMD)](#tab-panel-5)
- [Windows (PowerShell)](#tab-panel-6)

```

# Example for nano or vim
export EDITOR=nano
export EDITOR=vim
# For GUI editors, VS Code, Cursor, VSCodium, Windsurf, Zed, etc.
# include --wait
export EDITOR="code --wait"
```

To make it permanent, add this to your shell profile; `~/.bashrc`, `~/.zshrc`, etc.

Popular editor options include:

- `code` - Visual Studio Code
- `cursor` - Cursor
- `windsurf` - Windsurf
- `nvim` - Neovim editor
- `vim` - Vim editor
- `nano` - Nano editor
- `notepad` - Windows Notepad
- `subl` - Sublime Text

Some editors need command-line arguments to run in blocking mode. The `--wait` flag makes the editor process block until closed.

* * *

## [Configure](#configure)

You can customize TUI behavior through your OpenCode config file.

```

{
"$schema": "https://opencode.ai/config.json",
"tui": {
"scroll_speed": 3,
"scroll_acceleration": {
"enabled": true
}
}
}
```

### [Options](#options)

- `scroll_acceleration` - Enable macOS-style scroll acceleration for smooth, natural scrolling. When enabled, scroll speed increases with rapid scrolling gestures and stays precise for slower movements. **This setting takes precedence over `scroll_speed` and overrides it when enabled.**
- `scroll_speed` - Controls how fast the TUI scrolls when using scroll commands (minimum: `1`). Defaults to `3`. **Note: This is ignored if `scroll_acceleration.enabled` is set to `true`.**

* * *

## [Customization](#customization)

You can customize various aspects of the TUI view using the command palette (`ctrl+x h` or `/help`). These settings persist across restarts.

* * *

#### [Username display](#username-display)

Toggle whether your username appears in chat messages. Access this through:

- Command palette: Search for “username” or “hide username”
- The setting persists automatically and will be remembered across TUI sessions