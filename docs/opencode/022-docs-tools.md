---
title: Tools
url: https://opencode.ai/docs/tools/
source: crawler
fetched_at: 2026-02-14T12:04:44.288087-03:00
rendered_js: false
word_count: 705
summary: This document describes the built-in and custom tools available in OpenCode for LLM-driven codebase interaction and provides instructions for managing their execution permissions. It serves as a comprehensive reference for file manipulation, shell execution, and external service integration via MCP servers.
tags:
    - opencode
    - llm-tools
    - built-in-tools
    - permissions-configuration
    - mcp-servers
    - codebase-interaction
    - ripgrep
category: reference
---

Tools allow the LLM to perform actions in your codebase. OpenCode comes with a set of built-in tools, but you can extend it with [custom tools](https://opencode.ai/docs/custom-tools) or [MCP servers](https://opencode.ai/docs/mcp-servers).

By default, all tools are **enabled** and don’t need permission to run. You can control tool behavior through [permissions](https://opencode.ai/docs/permissions).

* * *

## [Configure](#configure)

Use the `permission` field to control tool behavior. You can allow, deny, or require approval for each tool.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"edit": "deny",
"bash": "ask",
"webfetch": "allow"
}
}
```

You can also use wildcards to control multiple tools at once. For example, to require approval for all tools from an MCP server:

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"mymcp_*": "ask"
}
}
```

[Learn more](https://opencode.ai/docs/permissions) about configuring permissions.

* * *

## [Built-in](#built-in)

Here are all the built-in tools available in OpenCode.

* * *

### [bash](#bash)

Execute shell commands in your project environment.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"bash": "allow"
}
}
```

This tool allows the LLM to run terminal commands like `npm install`, `git status`, or any other shell command.

* * *

### [edit](#edit)

Modify existing files using exact string replacements.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"edit": "allow"
}
}
```

This tool performs precise edits to files by replacing exact text matches. It’s the primary way the LLM modifies code.

* * *

### [write](#write)

Create new files or overwrite existing ones.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"edit": "allow"
}
}
```

Use this to allow the LLM to create new files. It will overwrite existing files if they already exist.

* * *

### [read](#read)

Read file contents from your codebase.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"read": "allow"
}
}
```

This tool reads files and returns their contents. It supports reading specific line ranges for large files.

* * *

### [grep](#grep)

Search file contents using regular expressions.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"grep": "allow"
}
}
```

Fast content search across your codebase. Supports full regex syntax and file pattern filtering.

* * *

### [glob](#glob)

Find files by pattern matching.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"glob": "allow"
}
}
```

Search for files using glob patterns like `**/*.js` or `src/**/*.ts`. Returns matching file paths sorted by modification time.

* * *

### [list](#list)

List files and directories in a given path.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"list": "allow"
}
}
```

This tool lists directory contents. It accepts glob patterns to filter results.

* * *

### [lsp (experimental)](#lsp-experimental)

Interact with your configured LSP servers to get code intelligence features like definitions, references, hover info, and call hierarchy.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"lsp": "allow"
}
}
```

Supported operations include `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, and `outgoingCalls`.

To configure which LSP servers are available for your project, see [LSP Servers](https://opencode.ai/docs/lsp).

* * *

### [patch](#patch)

Apply patches to files.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"edit": "allow"
}
}
```

This tool applies patch files to your codebase. Useful for applying diffs and patches from various sources.

* * *

### [skill](#skill)

Load a [skill](https://opencode.ai/docs/skills) (a `SKILL.md` file) and return its content in the conversation.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"skill": "allow"
}
}
```

* * *

### [todowrite](#todowrite)

Manage todo lists during coding sessions.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"todowrite": "allow"
}
}
```

Creates and updates task lists to track progress during complex operations. The LLM uses this to organize multi-step tasks.

* * *

### [todoread](#todoread)

Read existing todo lists.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"todoread": "allow"
}
}
```

Reads the current todo list state. Used by the LLM to track what tasks are pending or completed.

* * *

### [webfetch](#webfetch)

Fetch web content.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"webfetch": "allow"
}
}
```

Allows the LLM to fetch and read web pages. Useful for looking up documentation or researching online resources.

* * *

### [websearch](#websearch)

Search the web for information.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"websearch": "allow"
}
}
```

Performs web searches using Exa AI to find relevant information online. Useful for researching topics, finding current events, or gathering information beyond the training data cutoff.

No API key is required — the tool connects directly to Exa AI’s hosted MCP service without authentication.

* * *

### [question](#question)

Ask the user questions during execution.

```

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"question": "allow"
}
}
```

This tool allows the LLM to ask the user questions during a task. It’s useful for:

- Gathering user preferences or requirements
- Clarifying ambiguous instructions
- Getting decisions on implementation choices
- Offering choices about what direction to take

Each question includes a header, the question text, and a list of options. Users can select from the provided options or type a custom answer. When there are multiple questions, users can navigate between them before submitting all answers.

* * *

Custom tools let you define your own functions that the LLM can call. These are defined in your config file and can execute arbitrary code.

[Learn more](https://opencode.ai/docs/custom-tools) about creating custom tools.

* * *

## [MCP servers](#mcp-servers)

MCP (Model Context Protocol) servers allow you to integrate external tools and services. This includes database access, API integrations, and third-party services.

[Learn more](https://opencode.ai/docs/mcp-servers) about configuring MCP servers.

* * *

## [Internals](#internals)

Internally, tools like `grep`, `glob`, and `list` use [ripgrep](https://github.com/BurntSushi/ripgrep) under the hood. By default, ripgrep respects `.gitignore` patterns, which means files and directories listed in your `.gitignore` will be excluded from searches and listings.

* * *

### [Ignore patterns](#ignore-patterns)

To include files that would normally be ignored, create a `.ignore` file in your project root. This file can explicitly allow certain paths.

```

!node_modules/
!dist/
!build/
```

For example, this `.ignore` file allows ripgrep to search within `node_modules/`, `dist/`, and `build/` directories even if they’re listed in `.gitignore`.