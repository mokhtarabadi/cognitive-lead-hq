---
title: ACP Support
url: https://opencode.ai/docs/acp/
source: crawler
fetched_at: 2026-02-14T12:04:48.443511-03:00
rendered_js: false
word_count: 252
summary: This document explains how to integrate OpenCode into ACP-compatible editors and IDEs to enable AI coding features through standardized protocols.
tags:
    - agent-client-protocol
    - opencode
    - ide-integration
    - zed-editor
    - jetbrains
    - neovim-plugins
    - acp-setup
category: configuration
---

Use OpenCode in any ACP-compatible editor.

OpenCode supports the [Agent Client Protocol](https://agentclientprotocol.com) or (ACP), allowing you to use it directly in compatible editors and IDEs.

ACP is an open protocol that standardizes communication between code editors and AI coding agents.

* * *

## [Configure](#configure)

To use OpenCode via ACP, configure your editor to run the `opencode acp` command.

The command starts OpenCode as an ACP-compatible subprocess that communicates with your editor over JSON-RPC via stdio.

Below are examples for popular editors that support ACP.

* * *

### [Zed](#zed)

Add to your [Zed](https://zed.dev) configuration (`~/.config/zed/settings.json`):

```

{
"agent_servers": {
"OpenCode": {
"command": "opencode",
"args": ["acp"]
}
}
}
```

To open it, use the `agent: new thread` action in the **Command Palette**.

You can also bind a keyboard shortcut by editing your `keymap.json`:

```

[
{
"bindings": {
"cmd-alt-o": [
"agent::NewExternalAgentThread",
{
"agent": {
"custom": {
"name": "OpenCode",
"command": {
"command": "opencode",
"args": ["acp"]
}
}
}
}
]
}
}
]
```

* * *

### [JetBrains IDEs](#jetbrains-ides)

Add to your [JetBrains IDE](https://www.jetbrains.com/) acp.json according to the [documentation](https://www.jetbrains.com/help/ai-assistant/acp.html):

```

{
"agent_servers": {
"OpenCode": {
"command": "/absolute/path/bin/opencode",
"args": ["acp"]
}
}
}
```

To open it, use the new ‘OpenCode’ agent in the AI Chat agent selector.

* * *

### [Avante.nvim](#avantenvim)

Add to your [Avante.nvim](https://github.com/yetone/avante.nvim) configuration:

```

{
acp_providers = {
["opencode"] = {
command ="opencode",
args = { "acp" }
}
}
}
```

If you need to pass environment variables:

```

{
acp_providers = {
["opencode"] = {
command ="opencode",
args = { "acp" },
env = {
OPENCODE_API_KEY =os.getenv("OPENCODE_API_KEY")
}
}
}
}
```

* * *

### [CodeCompanion.nvim](#codecompanionnvim)

To use OpenCode as an ACP agent in [CodeCompanion.nvim](https://github.com/olimorris/codecompanion.nvim), add the following to your Neovim config:

```

require("codecompanion").setup({
interactions = {
chat = {
adapter = {
name ="opencode",
model ="claude-sonnet-4",
},
},
},
})
```

This config sets up CodeCompanion to use OpenCode as the ACP agent for chat.

If you need to pass environment variables (like `OPENCODE_API_KEY`), refer to [Configuring Adapters: Environment Variables](https://codecompanion.olimorris.dev/getting-started#setting-an-api-key) in the CodeCompanion.nvim documentation for full details.

## [Support](#support)

OpenCode works the same via ACP as it does in the terminal. All features are supported:

- Built-in tools (file operations, terminal commands, etc.)
- Custom tools and slash commands
- MCP servers configured in your OpenCode config
- Project-specific rules from `AGENTS.md`
- Custom formatters and linters
- Agents and permissions system