---
title: Tools
url: https://opencode.ai/docs/tools
source: sitemap
fetched_at: 2026-04-17T06:45:29.473309478-03:00
rendered_js: false
word_count: 711
summary: This document outlines the built-in tools available in OpenCode and provides instructions on how to configure permissions, manage file access, and integrate external MCP servers.
tags:
    - opencode-tools
    - configuration
    - permissions
    - mcp-servers
    - automation
category: guide
---

Tools allow the LLM to perform actions in your codebase. OpenCode comes with a set of built-in tools, but you can extend it with [custom tools](https://opencode.ai/docs/custom-tools) or [MCP servers](https://opencode.ai/docs/mcp-servers).

By default, all tools are **enabled** and don’t need permission to run. You can control tool behavior through [permissions](https://opencode.ai/docs/permissions).

* * *

## [Configure](#configure)

Use the `permission` field to control tool behavior. You can allow, deny, or require approval for each tool.

```json

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

```json

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

```json

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

```json

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

```json

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

```json

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

```json

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

```json

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"glob": "allow"
}
}
```

Search for files using glob patterns like `**/*.js` or `src/**/*.ts`. Returns matching file paths sorted by modification time.

* * *

### [lsp (experimental)](#lsp-experimental)

Interact with your configured LSP servers to get code intelligence features like definitions, references, hover info, and call hierarchy.

```json

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

### [apply\_patch](#apply_patch)

Apply patches to files.

```json

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"edit": "allow"
}
}
```

This tool applies patch files to your codebase. Useful for applying diffs and patches from various sources.

When handling `tool.execute.before` or `tool.execute.after` hooks, check `input.tool === "apply_patch"` (not `"patch"`).

`apply_patch` uses `output.args.patchText` instead of `output.args.filePath`. Paths are embedded in marker lines within `patchText` and are relative to the project root (for example: `*** Add File: src/new-file.ts`, `*** Update File: src/existing.ts`, `*** Move to: src/renamed.ts`, `*** Delete File: src/obsolete.ts`).

* * *

### [skill](#skill)

Load a [skill](https://opencode.ai/docs/skills) (a `SKILL.md` file) and return its content in the conversation.

```json

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

```json

{
"$schema": "https://opencode.ai/config.json",
"permission": {
"todowrite": "allow"
}
}
```

Creates and updates task lists to track progress during complex operations. The LLM uses this to organize multi-step tasks.

* * *

### [webfetch](#webfetch)

Fetch web content.

```json

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

```json

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

```json

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

Internally, tools like `grep` and `glob` use [ripgrep](https://github.com/BurntSushi/ripgrep) under the hood. By default, ripgrep respects `.gitignore` patterns, which means files and directories listed in your `.gitignore` will be excluded from searches and listings.

* * *

### [Ignore patterns](#ignore-patterns)

To include files that would normally be ignored, create a `.ignore` file in your project root. This file can explicitly allow certain paths.

```text

!node_modules/
!dist/
!build/
```

For example, this `.ignore` file allows ripgrep to search within `node_modules/`, `dist/`, and `build/` directories even if they’re listed in `.gitignore`.