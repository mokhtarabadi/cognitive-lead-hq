---
title: Commands
url: https://opencode.ai/docs/commands
source: crawler
fetched_at: 2026-02-14T12:04:53.394676-03:00
rendered_js: false
word_count: 543
summary: This document provides instructions for creating and configuring custom commands in the OpenCode TUI to automate repetitive tasks using either Markdown or JSON files. It explains how to use prompt templates, handle arguments, and integrate shell command outputs into custom workflows.
tags:
    - custom-commands
    - opencode-tui
    - prompt-automation
    - configuration-management
    - cli-tools
    - shell-integration
category: guide
---

Create custom commands for repetitive tasks.

Custom commands let you specify a prompt you want to run when that command is executed in the TUI.

Custom commands are in addition to the built-in commands like `/init`, `/undo`, `/redo`, `/share`, `/help`. [Learn more](https://opencode.ai/docs/tui#commands).

* * *

## [Create command files](#create-command-files)

Create markdown files in the `commands/` directory to define custom commands.

Create `.opencode/commands/test.md`:

```

---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---
Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

The frontmatter defines command properties. The content becomes the template.

Use the command by typing `/` followed by the command name.

* * *

## [Configure](#configure)

You can add custom commands through the OpenCode config or by creating markdown files in the `commands/` directory.

* * *

### [JSON](#json)

Use the `command` option in your OpenCode [config](https://opencode.ai/docs/config):

```

{
"$schema": "https://opencode.ai/config.json",
"command": {
// This becomes the name of the command
"test": {
// This is the prompt that will be sent to the LLM
"template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes.",
// This is shown as the description in the TUI
"description": "Run tests with coverage",
"agent": "build",
"model": "anthropic/claude-3-5-sonnet-20241022"
}
}
}
```

Now you can run this command in the TUI:

* * *

### [Markdown](#markdown)

You can also define commands using markdown files. Place them in:

- Global: `~/.config/opencode/commands/`
- Per-project: `.opencode/commands/`

```

---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---
Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

The markdown file name becomes the command name. For example, `test.md` lets you run:

* * *

## [Prompt config](#prompt-config)

The prompts for the custom commands support several special placeholders and syntax.

* * *

### [Arguments](#arguments)

Pass arguments to commands using the `$ARGUMENTS` placeholder.

```

---
description: Create a new component
---
Create a new React component named $ARGUMENTS with TypeScript support.
Include proper typing and basic structure.
```

Run the command with arguments:

And `$ARGUMENTS` will be replaced with `Button`.

You can also access individual arguments using positional parameters:

- `$1` - First argument
- `$2` - Second argument
- `$3` - Third argument
- And so on…

For example:

```

---
description: Create a new file with content
---
Create a file named $1 in the directory $2
with the following content: $3
```

Run the command:

```

/create-fileconfig.jsonsrc"{ \"key\": \"value\" }"
```

This replaces:

- `$1` with `config.json`
- `$2` with `src`
- `$3` with `{ "key": "value" }`

* * *

### [Shell output](#shell-output)

Use *!`command`* to inject [bash command](https://opencode.ai/docs/tui#bash-commands) output into your prompt.

For example, to create a custom command that analyzes test coverage:

```

---
description: Analyze test coverage
---
Here are the current test results:
!`npm test`
Based on these results, suggest improvements to increase coverage.
```

Or to review recent changes:

```

---
description: Review recent changes
---
Recent git commits:
!`git log --oneline -10`
Review these changes and suggest any improvements.
```

Commands run in your project’s root directory and their output becomes part of the prompt.

* * *

### [File references](#file-references)

Include files in your command using `@` followed by the filename.

```

---
description: Review component
---
Review the component in @src/components/Button.tsx.
Check for performance issues and suggest improvements.
```

The file content gets included in the prompt automatically.

* * *

## [Options](#options)

Let’s look at the configuration options in detail.

* * *

### [Template](#template)

The `template` option defines the prompt that will be sent to the LLM when the command is executed.

```

{
"command": {
"test": {
"template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes."
}
}
}
```

This is a **required** config option.

* * *

### [Description](#description)

Use the `description` option to provide a brief description of what the command does.

```

{
"command": {
"test": {
"description": "Run tests with coverage"
}
}
}
```

This is shown as the description in the TUI when you type in the command.

* * *

### [Agent](#agent)

Use the `agent` config to optionally specify which [agent](https://opencode.ai/docs/agents) should execute this command. If this is a [subagent](https://opencode.ai/docs/agents/#subagents) the command will trigger a subagent invocation by default. To disable this behavior, set `subtask` to `false`.

```

{
"command": {
"review": {
"agent": "plan"
}
}
}
```

This is an **optional** config option. If not specified, defaults to your current agent.

* * *

### [Subtask](#subtask)

Use the `subtask` boolean to force the command to trigger a [subagent](https://opencode.ai/docs/agents/#subagents) invocation. This is useful if you want the command to not pollute your primary context and will **force** the agent to act as a subagent, even if `mode` is set to `primary` on the [agent](https://opencode.ai/docs/agents) configuration.

```

{
"command": {
"analyze": {
"subtask": true
}
}
}
```

This is an **optional** config option.

* * *

### [Model](#model)

Use the `model` config to override the default model for this command.

```

{
"command": {
"analyze": {
"model": "anthropic/claude-3-5-sonnet-20241022"
}
}
}
```

This is an **optional** config option.

* * *

## [Built-in](#built-in)

opencode includes several built-in commands like `/init`, `/undo`, `/redo`, `/share`, `/help`; [learn more](https://opencode.ai/docs/tui#commands).

If you define a custom command with the same name, it will override the built-in command.