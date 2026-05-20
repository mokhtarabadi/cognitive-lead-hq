---
title: MCP servers
url: https://opencode.ai/docs/mcp-servers
source: crawler
fetched_at: 2026-02-14T12:04:58.715518-03:00
rendered_js: false
word_count: 1007
summary: This document explains how to integrate and configure local and remote Model Context Protocol (MCP) servers within OpenCode to extend LLM capabilities with external tools.
tags:
    - opencode
    - model-context-protocol
    - mcp-server
    - configuration
    - oauth
    - tool-integration
category: guide
---

You can add external tools to OpenCode using the *Model Context Protocol*, or MCP. OpenCode supports both local and remote servers.

Once added, MCP tools are automatically available to the LLM alongside built-in tools.

* * *

#### [Caveats](#caveats)

When you use an MCP server, it adds to the context. This can quickly add up if you have a lot of tools. So we recommend being careful with which MCP servers you use.

Certain MCP servers, like the GitHub MCP server, tend to add a lot of tokens and can easily exceed the context limit.

* * *

## [Enable](#enable)

You can define MCP servers in your [OpenCode Config](https://opencode.ai/docs/config/) under `mcp`. Add each MCP with a unique name. You can refer to that MCP by name when prompting the LLM.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"name-of-mcp-server": {
// ...
"enabled": true,
},
"name-of-other-mcp-server": {
// ...
},
},
}
```

You can also disable a server by setting `enabled` to `false`. This is useful if you want to temporarily disable a server without removing it from your config.

* * *

### [Overriding remote defaults](#overriding-remote-defaults)

Organizations can provide default MCP servers via their `.well-known/opencode` endpoint. These servers may be disabled by default, allowing users to opt-in to the ones they need.

To enable a specific server from your organization’s remote config, add it to your local config with `enabled: true`:

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"jira": {
"type": "remote",
"url": "https://jira.example.com/mcp",
"enabled": true
}
}
}
```

Your local config values override the remote defaults. See [config precedence](https://opencode.ai/docs/config#precedence-order) for more details.

* * *

## [Local](#local)

Add local MCP servers using `type` to `"local"` within the MCP object.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"my-local-mcp-server": {
"type": "local",
// Or ["bun", "x", "my-mcp-command"]
"command": ["npx", "-y", "my-mcp-command"],
"enabled": true,
"environment": {
"MY_ENV_VAR": "my_env_var_value",
},
},
},
}
```

The command is how the local MCP server is started. You can also pass in a list of environment variables as well.

For example, here’s how you can add the test [`@modelcontextprotocol/server-everything`](https://www.npmjs.com/package/@modelcontextprotocol/server-everything) MCP server.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"mcp_everything": {
"type": "local",
"command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
},
},
}
```

And to use it I can add `use the mcp_everything tool` to my prompts.

```

use the mcp_everything tool to add the number 3 and 4
```

* * *

#### [Options](#options)

Here are all the options for configuring a local MCP server.

OptionTypeRequiredDescription`type`StringYType of MCP server connection, must be `"local"`.`command`ArrayYCommand and arguments to run the MCP server.`environment`ObjectEnvironment variables to set when running the server.`enabled`BooleanEnable or disable the MCP server on startup.`timeout`NumberTimeout in ms for fetching tools from the MCP server. Defaults to 5000 (5 seconds).

* * *

## [Remote](#remote)

Add remote MCP servers by setting `type` to `"remote"`.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"my-remote-mcp": {
"type": "remote",
"url": "https://my-mcp-server.com",
"enabled": true,
"headers": {
"Authorization": "Bearer MY_API_KEY"
}
}
}
}
```

The `url` is the URL of the remote MCP server and with the `headers` option you can pass in a list of headers.

* * *

#### [Options](#options-1)

OptionTypeRequiredDescription`type`StringYType of MCP server connection, must be `"remote"`.`url`StringYURL of the remote MCP server.`enabled`BooleanEnable or disable the MCP server on startup.`headers`ObjectHeaders to send with the request.`oauth`ObjectOAuth authentication configuration. See [OAuth](#oauth) section below.`timeout`NumberTimeout in ms for fetching tools from the MCP server. Defaults to 5000 (5 seconds).

* * *

## [OAuth](#oauth)

OpenCode automatically handles OAuth authentication for remote MCP servers. When a server requires authentication, OpenCode will:

1. Detect the 401 response and initiate the OAuth flow
2. Use **Dynamic Client Registration (RFC 7591)** if supported by the server
3. Store tokens securely for future requests

* * *

### [Automatic](#automatic)

For most OAuth-enabled MCP servers, no special configuration is needed. Just configure the remote server:

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"my-oauth-server": {
"type": "remote",
"url": "https://mcp.example.com/mcp"
}
}
}
```

If the server requires authentication, OpenCode will prompt you to authenticate when you first try to use it. If not, you can [manually trigger the flow](#authenticating) with `opencode mcp auth <server-name>`.

* * *

### [Pre-registered](#pre-registered)

If you have client credentials from the MCP server provider, you can configure them:

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"my-oauth-server": {
"type": "remote",
"url": "https://mcp.example.com/mcp",
"oauth": {
"clientId": "{env:MY_MCP_CLIENT_ID}",
"clientSecret": "{env:MY_MCP_CLIENT_SECRET}",
"scope": "tools:read tools:execute"
}
}
}
}
```

* * *

### [Authenticating](#authenticating)

You can manually trigger authentication or manage credentials.

Authenticate with a specific MCP server:

```

opencodemcpauthmy-oauth-server
```

List all MCP servers and their auth status:

Remove stored credentials:

```

opencodemcplogoutmy-oauth-server
```

The `mcp auth` command will open your browser for authorization. After you authorize, OpenCode will store the tokens securely in `~/.local/share/opencode/mcp-auth.json`.

* * *

#### [Disabling OAuth](#disabling-oauth)

If you want to disable automatic OAuth for a server (e.g., for servers that use API keys instead), set `oauth` to `false`:

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"my-api-key-server": {
"type": "remote",
"url": "https://mcp.example.com/mcp",
"oauth": false,
"headers": {
"Authorization": "Bearer {env:MY_API_KEY}"
}
}
}
}
```

* * *

#### [OAuth Options](#oauth-options)

OptionTypeDescription`oauth`Object | falseOAuth config object, or `false` to disable OAuth auto-detection.`clientId`StringOAuth client ID. If not provided, dynamic client registration will be attempted.`clientSecret`StringOAuth client secret, if required by the authorization server.`scope`StringOAuth scopes to request during authorization.

#### [Debugging](#debugging)

If a remote MCP server is failing to authenticate, you can diagnose issues with:

```

# View auth status for all OAuth-capable servers
opencodemcpauthlist
# Debug connection and OAuth flow for a specific server
opencodemcpdebugmy-oauth-server
```

The `mcp debug` command shows the current auth status, tests HTTP connectivity, and attempts the OAuth discovery flow.

* * *

## [Manage](#manage)

Your MCPs are available as tools in OpenCode, alongside built-in tools. So you can manage them through the OpenCode config like any other tool.

* * *

### [Global](#global)

This means that you can enable or disable them globally.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"my-mcp-foo": {
"type": "local",
"command": ["bun", "x", "my-mcp-command-foo"]
},
"my-mcp-bar": {
"type": "local",
"command": ["bun", "x", "my-mcp-command-bar"]
}
},
"tools": {
"my-mcp-foo": false
}
}
```

We can also use a glob pattern to disable all matching MCPs.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"my-mcp-foo": {
"type": "local",
"command": ["bun", "x", "my-mcp-command-foo"]
},
"my-mcp-bar": {
"type": "local",
"command": ["bun", "x", "my-mcp-command-bar"]
}
},
"tools": {
"my-mcp*": false
}
}
```

Here we are using the glob pattern `my-mcp*` to disable all MCPs.

* * *

### [Per agent](#per-agent)

If you have a large number of MCP servers you may want to only enable them per agent and disable them globally. To do this:

1. Disable it as a tool globally.
2. In your [agent config](https://opencode.ai/docs/agents#tools), enable the MCP server as a tool.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"my-mcp": {
"type": "local",
"command": ["bun", "x", "my-mcp-command"],
"enabled": true
}
},
"tools": {
"my-mcp*": false
},
"agent": {
"my-agent": {
"tools": {
"my-mcp*": true
}
}
}
}
```

* * *

#### [Glob patterns](#glob-patterns)

The glob pattern uses simple regex globbing patterns:

- `*` matches zero or more of any character (e.g., `"my-mcp*"` matches `my-mcp_search`, `my-mcp_list`, etc.)
- `?` matches exactly one character
- All other characters match literally

* * *

## [Examples](#examples)

Below are examples of some common MCP servers. You can submit a PR if you want to document other servers.

* * *

### [Sentry](#sentry)

Add the [Sentry MCP server](https://mcp.sentry.dev) to interact with your Sentry projects and issues.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"sentry": {
"type": "remote",
"url": "https://mcp.sentry.dev/mcp",
"oauth": {}
}
}
}
```

After adding the configuration, authenticate with Sentry:

This will open a browser window to complete the OAuth flow and connect OpenCode to your Sentry account.

Once authenticated, you can use Sentry tools in your prompts to query issues, projects, and error data.

```

Show me the latest unresolved issues in my project. use sentry
```

* * *

### [Context7](#context7)

Add the [Context7 MCP server](https://github.com/upstash/context7) to search through docs.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"context7": {
"type": "remote",
"url": "https://mcp.context7.com/mcp"
}
}
}
```

If you have signed up for a free account, you can use your API key and get higher rate-limits.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"context7": {
"type": "remote",
"url": "https://mcp.context7.com/mcp",
"headers": {
"CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}"
}
}
}
}
```

Here we are assuming that you have the `CONTEXT7_API_KEY` environment variable set.

Add `use context7` to your prompts to use Context7 MCP server.

```

Configure a Cloudflare Worker script to cache JSON API responses for five minutes. use context7
```

Alternatively, you can add something like this to your [AGENTS.md](https://opencode.ai/docs/rules/).

```

When you need to search docs, use `context7` tools.
```

* * *

### [Grep by Vercel](#grep-by-vercel)

Add the [Grep by Vercel](https://grep.app) MCP server to search through code snippets on GitHub.

```

{
"$schema": "https://opencode.ai/config.json",
"mcp": {
"gh_grep": {
"type": "remote",
"url": "https://mcp.grep.app"
}
}
}
```

Since we named our MCP server `gh_grep`, you can add `use the gh_grep tool` to your prompts to get the agent to use it.

```

What's the right way to set a custom domain in an SST Astro component? use the gh_grep tool
```

Alternatively, you can add something like this to your [AGENTS.md](https://opencode.ai/docs/rules/).

```

If you are unsure how to do something, use `gh_grep` to search code examples from GitHub.
```