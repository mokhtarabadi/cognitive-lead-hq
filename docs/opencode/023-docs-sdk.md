---
title: SDK
url: https://opencode.ai/docs/sdk/
source: crawler
fetched_at: 2026-02-14T12:04:49.085565-03:00
rendered_js: false
word_count: 651
summary: This document provides a comprehensive guide and API reference for the opencode JS/TS SDK, detailing installation, client configuration, and the usage of type-safe server endpoints. It explains how to manage sessions, handle errors, and implement structured JSON output using JSON schemas.
tags:
    - opencode-sdk
    - typescript
    - api-reference
    - structured-output
    - json-schema
    - client-configuration
    - type-safety
category: reference
---

Type-safe JS client for opencode server.

The opencode JS/TS SDK provides a type-safe client for interacting with the server. Use it to build integrations and control opencode programmatically.

[Learn more](https://opencode.ai/docs/server) about how the server works. For examples, check out the [projects](https://opencode.ai/docs/ecosystem#projects) built by the community.

* * *

## [Install](#install)

Install the SDK from npm:

```

npminstall@opencode-ai/sdk
```

* * *

## [Create client](#create-client)

Create an instance of opencode:

```

import { createOpencode } from"@opencode-ai/sdk"
const { client } =awaitcreateOpencode()
```

This starts both a server and a client

#### [Options](#options)

OptionTypeDescriptionDefault`hostname``string`Server hostname`127.0.0.1``port``number`Server port`4096``signal``AbortSignal`Abort signal for cancellation`undefined``timeout``number`Timeout in ms for server start`5000``config``Config`Configuration object`{}`

* * *

## [Config](#config)

You can pass a configuration object to customize behavior. The instance still picks up your `opencode.json`, but you can override or add configuration inline:

```

import { createOpencode } from"@opencode-ai/sdk"
constopencode=awaitcreateOpencode({
hostname: "127.0.0.1",
port: 4096,
config: {
model: "anthropic/claude-3-5-sonnet-20241022",
},
})
console.log(`Server running at ${opencode.server.url}`)
opencode.server.close()
```

## [Client only](#client-only)

If you already have a running instance of opencode, you can create a client instance to connect to it:

```

import { createOpencodeClient } from"@opencode-ai/sdk"
constclient=createOpencodeClient({
baseUrl: "http://localhost:4096",
})
```

#### [Options](#options-1)

OptionTypeDescriptionDefault`baseUrl``string`URL of the server`http://localhost:4096``fetch``function`Custom fetch implementation`globalThis.fetch``parseAs``string`Response parsing method`auto``responseStyle``string`Return style: `data` or `fields``fields``throwOnError``boolean`Throw errors instead of return`false`

* * *

## [Types](#types)

The SDK includes TypeScript definitions for all API types. Import them directly:

```

importtype { Session, Message, Part } from"@opencode-ai/sdk"
```

All types are generated from the server’s OpenAPI specification and available in the [types file](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts).

* * *

## [Errors](#errors)

The SDK can throw errors that you can catch and handle:

```

try {
await client.session.get({ path: { id: "invalid-id" } })
} catch (error) {
console.error("Failed to get session:", (error asError).message)
}
```

* * *

## [Structured Output](#structured-output)

You can request structured JSON output from the model by specifying an `format` with a JSON schema. The model will use a `StructuredOutput` tool to return validated JSON matching your schema.

### [Basic Usage](#basic-usage)

```

constresult=await client.session.prompt({
path: { id: sessionId },
body: {
parts: [{ type: "text", text: "Research Anthropic and provide company info" }],
format: {
type: "json_schema",
schema: {
type: "object",
properties: {
company: { type: "string", description: "Company name" },
founded: { type: "number", description: "Year founded" },
products: {
type: "array",
items: { type: "string" },
description: "Main products",
},
},
required: ["company", "founded"],
},
},
},
})
// Access the structured output
console.log(result.data.info.structured_output)
// { company: "Anthropic", founded: 2021, products: ["Claude", "Claude API"] }
```

### [Output Format Types](#output-format-types)

TypeDescription`text`Default. Standard text response (no structured output)`json_schema`Returns validated JSON matching the provided schema

### [JSON Schema Format](#json-schema-format)

When using `type: 'json_schema'`, provide:

FieldTypeDescription`type``'json_schema'`Required. Specifies JSON schema mode`schema``object`Required. JSON Schema object defining the output structure`retryCount``number`Optional. Number of validation retries (default: 2)

### [Error Handling](#error-handling)

If the model fails to produce valid structured output after all retries, the response will include a `StructuredOutputError`:

```

if (result.data.info.error?.name ==="StructuredOutputError") {
console.error("Failed to produce structured output:", result.data.info.error.message)
console.error("Attempts:", result.data.info.error.retries)
}
```

### [Best Practices](#best-practices)

1. **Provide clear descriptions** in your schema properties to help the model understand what data to extract
2. **Use `required`** to specify which fields must be present
3. **Keep schemas focused** - complex nested schemas may be harder for the model to fill correctly
4. **Set appropriate `retryCount`** - increase for complex schemas, decrease for simple ones

* * *

## [APIs](#apis)

The SDK exposes all server APIs through a type-safe client.

* * *

### [Global](#global)

MethodDescriptionResponse`global.health()`Check server health and version`{ healthy: true, version: string }`

* * *

#### [Examples](#examples)

```

consthealth=await client.global.health()
console.log(health.data.version)
```

* * *

### [App](#app)

MethodDescriptionResponse`app.log()`Write a log entry`boolean``app.agents()`List all available agents[`Agent[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

* * *

#### [Examples](#examples-1)

```

// Write a log entry
await client.app.log({
body: {
service: "my-app",
level: "info",
message: "Operation completed",
},
})
// List available agents
constagents=await client.app.agents()
```

* * *

### [Project](#project)

MethodDescriptionResponse`project.list()`List all projects[`Project[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`project.current()`Get current project[`Project`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

* * *

#### [Examples](#examples-2)

```

// List all projects
constprojects=await client.project.list()
// Get current project
constcurrentProject=await client.project.current()
```

* * *

### [Path](#path)

MethodDescriptionResponse`path.get()`Get current path[`Path`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

* * *

#### [Examples](#examples-3)

```

// Get current path information
constpathInfo=await client.path.get()
```

* * *

### [Config](#config-1)

MethodDescriptionResponse`config.get()`Get config info[`Config`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`config.providers()`List providers and default models`{ providers:`[`Provider[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, default: { [key: string]: string } }`

* * *

#### [Examples](#examples-4)

```

constconfig=await client.config.get()
const { providers, default: defaults } =await client.config.providers()
```

* * *

### [Sessions](#sessions)

MethodDescriptionNotes`session.list()`List sessionsReturns [`Session[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.get({ path })`Get sessionReturns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.children({ path })`List child sessionsReturns [`Session[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.create({ body })`Create sessionReturns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.delete({ path })`Delete sessionReturns `boolean``session.update({ path, body })`Update session propertiesReturns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.init({ path, body })`Analyze app and create `AGENTS.md`Returns `boolean``session.abort({ path })`Abort a running sessionReturns `boolean``session.share({ path })`Share sessionReturns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.unshare({ path })`Unshare sessionReturns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.summarize({ path, body })`Summarize sessionReturns `boolean``session.messages({ path })`List messages in a sessionReturns `{ info:`[`Message`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:`[`Part[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}[]``session.message({ path })`Get message detailsReturns `{ info:`[`Message`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:`[`Part[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}``session.prompt({ path, body })`Send prompt message`body.noReply: true` returns UserMessage (context only). Default returns [`AssistantMessage`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts) with AI response. Supports `body.outputFormat` for [structured output](#structured-output)`session.command({ path, body })`Send command to sessionReturns `{ info:`[`AssistantMessage`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`, parts:`[`Part[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`}``session.shell({ path, body })`Run a shell commandReturns [`AssistantMessage`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.revert({ path, body })`Revert a messageReturns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`session.unrevert({ path })`Restore reverted messagesReturns [`Session`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`postSessionByIdPermissionsByPermissionId({ path, body })`Respond to a permission requestReturns `boolean`

* * *

#### [Examples](#examples-5)

```

// Create and manage sessions
constsession=await client.session.create({
body: { title: "My session" },
})
constsessions=await client.session.list()
// Send a prompt message
constresult=await client.session.prompt({
path: { id: session.id },
body: {
model: { providerID: "anthropic", modelID: "claude-3-5-sonnet-20241022" },
parts: [{ type: "text", text: "Hello!" }],
},
})
// Inject context without triggering AI response (useful for plugins)
await client.session.prompt({
path: { id: session.id },
body: {
noReply: true,
parts: [{ type: "text", text: "You are a helpful assistant." }],
},
})
```

* * *

### [Files](#files)

MethodDescriptionResponse`find.text({ query })`Search for text in filesArray of match objects with `path`, `lines`, `line_number`, `absolute_offset`, `submatches``find.files({ query })`Find files and directories by name`string[]` (paths)`find.symbols({ query })`Find workspace symbols[`Symbol[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)`file.read({ query })`Read a file`{ type: "raw" | "patch", content: string }``file.status({ query? })`Get status for tracked files[`File[]`](https://github.com/anomalyco/opencode/blob/dev/packages/sdk/js/src/gen/types.gen.ts)

`find.files` supports a few optional query fields:

- `type`: `"file"` or `"directory"`
- `directory`: override the project root for the search
- `limit`: max results (1–200)

* * *

#### [Examples](#examples-6)

```

// Search and read files
consttextResults=await client.find.text({
query: { pattern: "function.*opencode" },
})
constfiles=await client.find.files({
query: { query: "*.ts", type: "file" },
})
constdirectories=await client.find.files({
query: { query: "packages", type: "directory", limit: 20 },
})
constcontent=await client.file.read({
query: { path: "src/index.ts" },
})
```

* * *

### [TUI](#tui)

MethodDescriptionResponse`tui.appendPrompt({ body })`Append text to the prompt`boolean``tui.openHelp()`Open the help dialog`boolean``tui.openSessions()`Open the session selector`boolean``tui.openThemes()`Open the theme selector`boolean``tui.openModels()`Open the model selector`boolean``tui.submitPrompt()`Submit the current prompt`boolean``tui.clearPrompt()`Clear the prompt`boolean``tui.executeCommand({ body })`Execute a command`boolean``tui.showToast({ body })`Show toast notification`boolean`

* * *

#### [Examples](#examples-7)

```

// Control TUI interface
await client.tui.appendPrompt({
body: { text: "Add this to prompt" },
})
await client.tui.showToast({
body: { message: "Task completed", variant: "success" },
})
```

* * *

### [Auth](#auth)

MethodDescriptionResponse`auth.set({ ... })`Set authentication credentials`boolean`

* * *

#### [Examples](#examples-8)

```

await client.auth.set({
path: { id: "anthropic" },
body: { type: "api", key: "your-api-key" },
})
```

* * *

### [Events](#events)

MethodDescriptionResponse`event.subscribe()`Server-sent events streamServer-sent events stream

* * *

#### [Examples](#examples-9)

```

// Listen to real-time events
constevents=await client.event.subscribe()
forawait (consteventof events.stream) {
console.log("Event:", event.type, event.properties)
}
```