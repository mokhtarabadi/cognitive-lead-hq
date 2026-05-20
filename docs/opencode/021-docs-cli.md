---
title: CLI
url: https://opencode.ai/docs/cli/
source: crawler
fetched_at: 2026-02-14T12:04:41.854585-03:00
rendered_js: false
word_count: 1124
summary: This document provides a comprehensive technical reference for the OpenCode CLI, detailing available commands, flags, and programmatic interaction methods. It covers session management, agent configuration, model provider authentication, and the terminal user interface.
tags:
    - opencode-cli
    - cli-reference
    - terminal-user-interface
    - session-management
    - agent-configuration
    - mcp-server
    - command-line-tools
category: reference
---

The OpenCode CLI by default starts the [TUI](https://opencode.ai/docs/tui) when run without any arguments.

But it also accepts commands as documented on this page. This allows you to interact with OpenCode programmatically.

```

opencoderun"Explain how closures work in JavaScript"
```

* * *

### [tui](#tui)

Start the OpenCode terminal user interface.

#### [Flags](#flags)

FlagShortDescription`--continue``-c`Continue the last session`--session``-s`Session ID to continue`--fork`Fork the session when continuing (use with `--continue` or `--session`)`--prompt`Prompt to use`--model``-m`Model to use in the form of provider/model`--agent`Agent to use`--port`Port to listen on`--hostname`Hostname to listen on

* * *

## [Commands](#commands)

The OpenCode CLI also has the following commands.

* * *

### [agent](#agent)

Manage agents for OpenCode.

* * *

### [attach](#attach)

Attach a terminal to an already running OpenCode backend server started via `serve` or `web` commands.

This allows using the TUI with a remote OpenCode backend. For example:

```

# Start the backend server for web/mobile access
opencodeweb--port4096--hostname0.0.0.0
# In another terminal, attach the TUI to the running backend
opencodeattachhttp://10.20.30.40:4096
```

#### [Flags](#flags-1)

FlagShortDescription`--dir`Working directory to start TUI in`--session``-s`Session ID to continue

* * *

#### [create](#create)

Create a new agent with custom configuration.

This command will guide you through creating a new agent with a custom system prompt and tool configuration.

* * *

#### [list](#list)

List all available agents.

* * *

### [auth](#auth)

Command to manage credentials and login for providers.

* * *

#### [login](#login)

OpenCode is powered by the provider list at [Models.dev](https://models.dev), so you can use `opencode auth login` to configure API keys for any provider you’d like to use. This is stored in `~/.local/share/opencode/auth.json`.

When OpenCode starts up it loads the providers from the credentials file. And if there are any keys defined in your environments or a `.env` file in your project.

* * *

#### [list](#list-1)

Lists all the authenticated providers as stored in the credentials file.

Or the short version.

* * *

#### [logout](#logout)

Logs you out of a provider by clearing it from the credentials file.

* * *

### [github](#github)

Manage the GitHub agent for repository automation.

```

opencodegithub [command]
```

* * *

#### [install](#install)

Install the GitHub agent in your repository.

This sets up the necessary GitHub Actions workflow and guides you through the configuration process. [Learn more](https://opencode.ai/docs/github).

* * *

#### [run](#run)

Run the GitHub agent. This is typically used in GitHub Actions.

##### [Flags](#flags-2)

FlagDescription`--event`GitHub mock event to run the agent for`--token`GitHub personal access token

* * *

### [mcp](#mcp)

Manage Model Context Protocol servers.

* * *

#### [add](#add)

Add an MCP server to your configuration.

This command will guide you through adding either a local or remote MCP server.

* * *

#### [list](#list-2)

List all configured MCP servers and their connection status.

Or use the short version.

* * *

#### [auth](#auth-1)

Authenticate with an OAuth-enabled MCP server.

If you don’t provide a server name, you’ll be prompted to select from available OAuth-capable servers.

You can also list OAuth-capable servers and their authentication status.

Or use the short version.

* * *

#### [logout](#logout-1)

Remove OAuth credentials for an MCP server.

```

opencodemcplogout [name]
```

* * *

#### [debug](#debug)

Debug OAuth connection issues for an MCP server.

```

opencodemcpdebug<name>
```

* * *

### [models](#models)

List all available models from configured providers.

```

opencodemodels [provider]
```

This command displays all models available across your configured providers in the format `provider/model`.

This is useful for figuring out the exact model name to use in [your config](https://opencode.ai/docs/config/).

You can optionally pass a provider ID to filter models by that provider.

```

opencodemodelsanthropic
```

#### [Flags](#flags-3)

FlagDescription`--refresh`Refresh the models cache from models.dev`--verbose`Use more verbose model output (includes metadata like costs)

Use the `--refresh` flag to update the cached model list. This is useful when new models have been added to a provider and you want to see them in OpenCode.

```

opencodemodels--refresh
```

* * *

### [run](#run-1)

Run opencode in non-interactive mode by passing a prompt directly.

This is useful for scripting, automation, or when you want a quick answer without launching the full TUI. For example.

```

opencoderunExplaintheuseofcontextinGo
```

You can also attach to a running `opencode serve` instance to avoid MCP server cold boot times on every run:

```

# Start a headless server in one terminal
opencodeserve
# In another terminal, run commands that attach to it
opencoderun--attachhttp://localhost:4096"Explain async/await in JavaScript"
```

#### [Flags](#flags-4)

FlagShortDescription`--command`The command to run, use message for args`--continue``-c`Continue the last session`--session``-s`Session ID to continue`--fork`Fork the session when continuing (use with `--continue` or `--session`)`--share`Share the session`--model``-m`Model to use in the form of provider/model`--agent`Agent to use`--file``-f`File(s) to attach to message`--format`Format: default (formatted) or json (raw JSON events)`--title`Title for the session (uses truncated prompt if no value provided)`--attach`Attach to a running opencode server (e.g., [http://localhost:4096](http://localhost:4096))`--port`Port for the local server (defaults to random port)

* * *

### [serve](#serve)

Start a headless OpenCode server for API access. Check out the [server docs](https://opencode.ai/docs/server) for the full HTTP interface.

This starts an HTTP server that provides API access to opencode functionality without the TUI interface. Set `OPENCODE_SERVER_PASSWORD` to enable HTTP basic auth (username defaults to `opencode`).

#### [Flags](#flags-5)

FlagDescription`--port`Port to listen on`--hostname`Hostname to listen on`--mdns`Enable mDNS discovery`--cors`Additional browser origin(s) to allow CORS

* * *

### [session](#session)

Manage OpenCode sessions.

```

opencodesession [command]
```

* * *

#### [list](#list-3)

List all OpenCode sessions.

##### [Flags](#flags-6)

FlagShortDescription`--max-count``-n`Limit to N most recent sessions`--format`Output format: table or json (table)

* * *

### [stats](#stats)

Show token usage and cost statistics for your OpenCode sessions.

#### [Flags](#flags-7)

FlagDescription`--days`Show stats for the last N days (all time)`--tools`Number of tools to show (all)`--models`Show model usage breakdown (hidden by default). Pass a number to show top N`--project`Filter by project (all projects, empty string: current project)

* * *

### [export](#export)

Export session data as JSON.

```

opencodeexport [sessionID]
```

If you don’t provide a session ID, you’ll be prompted to select from available sessions.

* * *

### [import](#import)

Import session data from a JSON file or OpenCode share URL.

You can import from a local file or an OpenCode share URL.

```

opencodeimportsession.json
opencodeimporthttps://opncd.ai/s/abc123
```

* * *

### [web](#web)

Start a headless OpenCode server with a web interface.

This starts an HTTP server and opens a web browser to access OpenCode through a web interface. Set `OPENCODE_SERVER_PASSWORD` to enable HTTP basic auth (username defaults to `opencode`).

#### [Flags](#flags-8)

FlagDescription`--port`Port to listen on`--hostname`Hostname to listen on`--mdns`Enable mDNS discovery`--cors`Additional browser origin(s) to allow CORS

* * *

### [acp](#acp)

Start an ACP (Agent Client Protocol) server.

This command starts an ACP server that communicates via stdin/stdout using nd-JSON.

#### [Flags](#flags-9)

FlagDescription`--cwd`Working directory`--port`Port to listen on`--hostname`Hostname to listen on

* * *

### [uninstall](#uninstall)

Uninstall OpenCode and remove all related files.

#### [Flags](#flags-10)

FlagShortDescription`--keep-config``-c`Keep configuration files`--keep-data``-d`Keep session data and snapshots`--dry-run`Show what would be removed without removing`--force``-f`Skip confirmation prompts

* * *

### [upgrade](#upgrade)

Updates opencode to the latest version or a specific version.

```

opencodeupgrade [target]
```

To upgrade to the latest version.

To upgrade to a specific version.

#### [Flags](#flags-11)

FlagShortDescription`--method``-m`The installation method that was used; curl, npm, pnpm, bun, brew

* * *

## [Global Flags](#global-flags)

The opencode CLI takes the following global flags.

FlagShortDescription`--help``-h`Display help`--version``-v`Print version number`--print-logs`Print logs to stderr`--log-level`Log level (DEBUG, INFO, WARN, ERROR)

* * *

## [Environment variables](#environment-variables)

OpenCode can be configured using environment variables.

VariableTypeDescription`OPENCODE_AUTO_SHARE`booleanAutomatically share sessions`OPENCODE_GIT_BASH_PATH`stringPath to Git Bash executable on Windows`OPENCODE_CONFIG`stringPath to config file`OPENCODE_CONFIG_DIR`stringPath to config directory`OPENCODE_CONFIG_CONTENT`stringInline json config content`OPENCODE_DISABLE_AUTOUPDATE`booleanDisable automatic update checks`OPENCODE_DISABLE_PRUNE`booleanDisable pruning of old data`OPENCODE_DISABLE_TERMINAL_TITLE`booleanDisable automatic terminal title updates`OPENCODE_PERMISSION`stringInlined json permissions config`OPENCODE_DISABLE_DEFAULT_PLUGINS`booleanDisable default plugins`OPENCODE_DISABLE_LSP_DOWNLOAD`booleanDisable automatic LSP server downloads`OPENCODE_ENABLE_EXPERIMENTAL_MODELS`booleanEnable experimental models`OPENCODE_DISABLE_AUTOCOMPACT`booleanDisable automatic context compaction`OPENCODE_DISABLE_CLAUDE_CODE`booleanDisable reading from `.claude` (prompt + skills)`OPENCODE_DISABLE_CLAUDE_CODE_PROMPT`booleanDisable reading `~/.claude/CLAUDE.md``OPENCODE_DISABLE_CLAUDE_CODE_SKILLS`booleanDisable loading `.claude/skills``OPENCODE_DISABLE_MODELS_FETCH`booleanDisable fetching models from remote sources`OPENCODE_FAKE_VCS`stringFake VCS provider for testing purposes`OPENCODE_DISABLE_FILETIME_CHECK`booleanDisable file time checking for optimization`OPENCODE_CLIENT`stringClient identifier (defaults to `cli`)`OPENCODE_ENABLE_EXA`booleanEnable Exa web search tools`OPENCODE_SERVER_PASSWORD`stringEnable basic auth for `serve`/`web``OPENCODE_SERVER_USERNAME`stringOverride basic auth username (default `opencode`)`OPENCODE_MODELS_URL`stringCustom URL for fetching models configuration

* * *

### [Experimental](#experimental)

These environment variables enable experimental features that may change or be removed.

VariableTypeDescription`OPENCODE_EXPERIMENTAL`booleanEnable all experimental features`OPENCODE_EXPERIMENTAL_ICON_DISCOVERY`booleanEnable icon discovery`OPENCODE_EXPERIMENTAL_DISABLE_COPY_ON_SELECT`booleanDisable copy on select in TUI`OPENCODE_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS`numberDefault timeout for bash commands in ms`OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX`numberMax output tokens for LLM responses`OPENCODE_EXPERIMENTAL_FILEWATCHER`booleanEnable file watcher for entire dir`OPENCODE_EXPERIMENTAL_OXFMT`booleanEnable oxfmt formatter`OPENCODE_EXPERIMENTAL_LSP_TOOL`booleanEnable experimental LSP tool`OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER`booleanDisable file watcher`OPENCODE_EXPERIMENTAL_EXA`booleanEnable experimental Exa features`OPENCODE_EXPERIMENTAL_LSP_TY`booleanEnable experimental LSP type checking`OPENCODE_EXPERIMENTAL_MARKDOWN`booleanEnable experimental markdown features`OPENCODE_EXPERIMENTAL_PLAN_MODE`booleanEnable plan mode