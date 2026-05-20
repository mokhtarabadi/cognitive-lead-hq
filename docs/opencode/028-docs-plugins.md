---
title: Plugins
url: https://opencode.ai/docs/plugins/
source: crawler
fetched_at: 2026-02-14T12:04:50.681955-03:00
rendered_js: false
word_count: 860
summary: This document provides a comprehensive guide on extending OpenCode through plugins, covering installation methods, development structure, available event hooks, and implementation examples.
tags:
    - opencode
    - plugin-development
    - javascript
    - typescript
    - event-hooks
    - custom-tools
    - extensibility
category: guide
---

Write your own plugins to extend OpenCode.

Plugins allow you to extend OpenCode by hooking into various events and customizing behavior. You can create plugins to add new features, integrate with external services, or modify OpenCode’s default behavior.

For examples, check out the [plugins](https://opencode.ai/docs/ecosystem#plugins) created by the community.

* * *

## [Use a plugin](#use-a-plugin)

There are two ways to load plugins.

* * *

### [From local files](#from-local-files)

Place JavaScript or TypeScript files in the plugin directory.

- `.opencode/plugins/` - Project-level plugins
- `~/.config/opencode/plugins/` - Global plugins

Files in these directories are automatically loaded at startup.

* * *

### [From npm](#from-npm)

Specify npm packages in your config file.

```

{
"$schema": "https://opencode.ai/config.json",
"plugin": ["opencode-helicone-session", "opencode-wakatime", "@my-org/custom-plugin"]
}
```

Both regular and scoped npm packages are supported.

Browse available plugins in the [ecosystem](https://opencode.ai/docs/ecosystem#plugins).

* * *

### [How plugins are installed](#how-plugins-are-installed)

**npm plugins** are installed automatically using Bun at startup. Packages and their dependencies are cached in `~/.cache/opencode/node_modules/`.

**Local plugins** are loaded directly from the plugin directory. To use external packages, you must create a `package.json` within your config directory (see [Dependencies](#dependencies)), or publish the plugin to npm and [add it to your config](https://opencode.ai/docs/config#plugins).

* * *

### [Load order](#load-order)

Plugins are loaded from all sources and all hooks run in sequence. The load order is:

1. Global config (`~/.config/opencode/opencode.json`)
2. Project config (`opencode.json`)
3. Global plugin directory (`~/.config/opencode/plugins/`)
4. Project plugin directory (`.opencode/plugins/`)

Duplicate npm packages with the same name and version are loaded once. However, a local plugin and an npm plugin with similar names are both loaded separately.

* * *

## [Create a plugin](#create-a-plugin)

A plugin is a **JavaScript/TypeScript module** that exports one or more plugin functions. Each function receives a context object and returns a hooks object.

* * *

### [Dependencies](#dependencies)

Local plugins and custom tools can use external npm packages. Add a `package.json` to your config directory with the dependencies you need.

```

{
"dependencies": {
"shescape": "^2.1.0"
}
}
```

OpenCode runs `bun install` at startup to install these. Your plugins and tools can then import them.

```

import { escape } from"shescape"
exportconstMyPlugin=async (ctx) => {
return {
"tool.execute.before": async (input, output) => {
if (input.tool ==="bash") {
output.args.command =escape(output.args.command)
}
},
}
}
```

* * *

### [Basic structure](#basic-structure)

```

exportconstMyPlugin=async ({ project, client, $, directory, worktree }) => {
console.log("Plugin initialized!")
return {
// Hook implementations go here
}
}
```

The plugin function receives:

- `project`: The current project information.
- `directory`: The current working directory.
- `worktree`: The git worktree path.
- `client`: An opencode SDK client for interacting with the AI.
- `$`: Bun’s [shell API](https://bun.com/docs/runtime/shell) for executing commands.

* * *

### [TypeScript support](#typescript-support)

For TypeScript plugins, you can import types from the plugin package:

```

importtype { Plugin } from"@opencode-ai/plugin"
exportconstMyPlugin:Plugin=async ({ project, client, $, directory, worktree }) => {
return {
// Type-safe hook implementations
}
}
```

* * *

### [Events](#events)

Plugins can subscribe to events as seen below in the Examples section. Here is a list of the different events available.

#### [Command Events](#command-events)

- `command.executed`

#### [File Events](#file-events)

- `file.edited`
- `file.watcher.updated`

#### [Installation Events](#installation-events)

- `installation.updated`

#### [LSP Events](#lsp-events)

- `lsp.client.diagnostics`
- `lsp.updated`

#### [Message Events](#message-events)

- `message.part.removed`
- `message.part.updated`
- `message.removed`
- `message.updated`

#### [Permission Events](#permission-events)

- `permission.asked`
- `permission.replied`

#### [Server Events](#server-events)

- `server.connected`

#### [Session Events](#session-events)

- `session.created`
- `session.compacted`
- `session.deleted`
- `session.diff`
- `session.error`
- `session.idle`
- `session.status`
- `session.updated`

#### [Todo Events](#todo-events)

- `todo.updated`

#### [Shell Events](#shell-events)

- `shell.env`

#### [Tool Events](#tool-events)

- `tool.execute.after`
- `tool.execute.before`

#### [TUI Events](#tui-events)

- `tui.prompt.append`
- `tui.command.execute`
- `tui.toast.show`

* * *

## [Examples](#examples)

Here are some examples of plugins you can use to extend opencode.

* * *

### [Send notifications](#send-notifications)

Send notifications when certain events occur:

```

exportconstNotificationPlugin=async ({ project, client, $, directory, worktree }) => {
return {
event: async ({ event }) => {
// Send notification on session completion
if (event.type ==="session.idle") {
await$`osascript -e 'display notification "Session completed!" with title "opencode"'`
}
},
}
}
```

We are using `osascript` to run AppleScript on macOS. Here we are using it to send notifications.

* * *

### [.env protection](#env-protection)

Prevent opencode from reading `.env` files:

```

exportconstEnvProtection=async ({ project, client, $, directory, worktree }) => {
return {
"tool.execute.before": async (input, output) => {
if (input.tool ==="read"&& output.args.filePath.includes(".env")) {
thrownewError("Do not read .env files")
}
},
}
}
```

* * *

### [Inject environment variables](#inject-environment-variables)

Inject environment variables into all shell execution (AI tools and user terminals):

```

exportconstInjectEnvPlugin=async () => {
return {
"shell.env": async (input, output) => {
output.env.MY_API_KEY="secret"
output.env.PROJECT_ROOT= input.cwd
},
}
}
```

* * *

### [Custom tools](#custom-tools)

Plugins can also add custom tools to opencode:

```

import { type Plugin, tool } from"@opencode-ai/plugin"
exportconstCustomToolsPlugin:Plugin=async (ctx) => {
return {
tool: {
mytool: tool({
description: "This is a custom tool",
args: {
foo: tool.schema.string(),
},
asyncexecute(args, context) {
const { directory, worktree } = context
return`Hello ${args.foo} from ${directory} (worktree: ${worktree})`
},
}),
},
}
}
```

The `tool` helper creates a custom tool that opencode can call. It takes a Zod schema function and returns a tool definition with:

- `description`: What the tool does
- `args`: Zod schema for the tool’s arguments
- `execute`: Function that runs when the tool is called

Your custom tools will be available to opencode alongside built-in tools.

* * *

### [Logging](#logging)

Use `client.app.log()` instead of `console.log` for structured logging:

```

exportconstMyPlugin=async ({ client }) => {
await client.app.log({
body: {
service: "my-plugin",
level: "info",
message: "Plugin initialized",
extra: { foo: "bar" },
},
})
}
```

Levels: `debug`, `info`, `warn`, `error`. See [SDK documentation](https://opencode.ai/docs/sdk) for details.

* * *

### [Compaction hooks](#compaction-hooks)

Customize the context included when a session is compacted:

```

importtype { Plugin } from"@opencode-ai/plugin"
exportconstCompactionPlugin:Plugin=async (ctx) => {
return {
"experimental.session.compacting": async (input, output) => {
// Inject additional context into the compaction prompt
output.context.push(`
## Custom Context
Include any state that should persist across compaction:
- Current task status
- Important decisions made
- Files being actively worked on
`)
},
}
}
```

The `experimental.session.compacting` hook fires before the LLM generates a continuation summary. Use it to inject domain-specific context that the default compaction prompt would miss.

You can also replace the compaction prompt entirely by setting `output.prompt`:

```

importtype { Plugin } from"@opencode-ai/plugin"
exportconstCustomCompactionPlugin:Plugin=async (ctx) => {
return {
"experimental.session.compacting": async (input, output) => {
// Replace the entire compaction prompt
output.prompt =`
You are generating a continuation prompt for a multi-agent swarm session.
Summarize:
1. The current task and its status
2. Which files are being modified and by whom
3. Any blockers or dependencies between agents
4. The next steps to complete the work
Format as a structured prompt that a new agent can use to resume work.
`
},
}
}
```

When `output.prompt` is set, it completely replaces the default compaction prompt. The `output.context` array is ignored in this case.