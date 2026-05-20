---
title: LSP Servers
url: https://opencode.ai/docs/lsp/
source: crawler
fetched_at: 2026-02-14T12:04:47.9418-03:00
rendered_js: false
word_count: 421
summary: This document explains how OpenCode integrates with Language Server Protocol (LSP) servers to provide codebase diagnostics and feedback. It details the list of built-in servers, automatic detection logic, and comprehensive configuration options for customizing or adding new LSP servers.
tags:
    - lsp-integration
    - language-server-protocol
    - opencode-configuration
    - code-diagnostics
    - developer-tools
    - custom-lsp
category: configuration
---

OpenCode integrates with your LSP servers.

OpenCode integrates with your Language Server Protocol (LSP) to help the LLM interact with your codebase. It uses diagnostics to provide feedback to the LLM.

* * *

## [Built-in](#built-in)

OpenCode comes with several built-in LSP servers for popular languages:

LSP ServerExtensionsRequirementsastro.astroAuto-installs for Astro projectsbash.sh, .bash, .zsh, .kshAuto-installs bash-language-serverclangd.c, .cpp, .cc, .cxx, .c++, .h, .hpp, .hh, .hxx, .h++Auto-installs for C/C++ projectscsharp.cs`.NET SDK` installedclojure-lsp.clj, .cljs, .cljc, .edn`clojure-lsp` command availabledart.dart`dart` command availabledeno.ts, .tsx, .js, .jsx, .mjs`deno` command available (auto-detects deno.json/deno.jsonc)elixir-ls.ex, .exs`elixir` command availableeslint.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .vue`eslint` dependency in projectfsharp.fs, .fsi, .fsx, .fsscript`.NET SDK` installedgleam.gleam`gleam` command availablegopls.go`go` command availablehls.hs, .lhs`haskell-language-server-wrapper` command availablejdtls.java`Java SDK (version 21+)` installedkotlin-ls.kt, .ktsAuto-installs for Kotlin projectslua-ls.luaAuto-installs for Lua projectsnixd.nix`nixd` command availableocaml-lsp.ml, .mli`ocamllsp` command availableoxlint.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .vue, .astro, .svelte`oxlint` dependency in projectphp intelephense.phpAuto-installs for PHP projectsprisma.prisma`prisma` command availablepyright.py, .pyi`pyright` dependency installedruby-lsp (rubocop).rb, .rake, .gemspec, .ru`ruby` and `gem` commands availablerust.rs`rust-analyzer` command availablesourcekit-lsp.swift, .objc, .objcpp`swift` installed (`xcode` on macOS)svelte.svelteAuto-installs for Svelte projectsterraform.tf, .tfvarsAuto-installs from GitHub releasestinymist.typ, .typcAuto-installs from GitHub releasestypescript.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts`typescript` dependency in projectvue.vueAuto-installs for Vue projectsyaml-ls.yaml, .ymlAuto-installs Red Hat yaml-language-serverzls.zig, .zon`zig` command available

LSP servers are automatically enabled when one of the above file extensions are detected and the requirements are met.

* * *

## [How It Works](#how-it-works)

When opencode opens a file, it:

1. Checks the file extension against all enabled LSP servers.
2. Starts the appropriate LSP server if not already running.

* * *

## [Configure](#configure)

You can customize LSP servers through the `lsp` section in your opencode config.

```

{
"$schema": "https://opencode.ai/config.json",
"lsp": {}
}
```

Each LSP server supports the following:

PropertyTypeDescription`disabled`booleanSet this to `true` to disable the LSP server`command`string\[]The command to start the LSP server`extensions`string\[]File extensions this LSP server should handle`env`objectEnvironment variables to set when starting server`initialization`objectInitialization options to send to the LSP server

Let’s look at some examples.

* * *

### [Environment variables](#environment-variables)

Use the `env` property to set environment variables when starting the LSP server:

```

{
"$schema": "https://opencode.ai/config.json",
"lsp": {
"rust": {
"env": {
"RUST_LOG": "debug"
}
}
}
}
```

* * *

### [Initialization options](#initialization-options)

Use the `initialization` property to pass initialization options to the LSP server. These are server-specific settings sent during the LSP `initialize` request:

```

{
"$schema": "https://opencode.ai/config.json",
"lsp": {
"typescript": {
"initialization": {
"preferences": {
"importModuleSpecifierPreference": "relative"
}
}
}
}
}
```

* * *

### [Disabling LSP servers](#disabling-lsp-servers)

To disable **all** LSP servers globally, set `lsp` to `false`:

```

{
"$schema": "https://opencode.ai/config.json",
"lsp": false
}
```

To disable a **specific** LSP server, set `disabled` to `true`:

```

{
"$schema": "https://opencode.ai/config.json",
"lsp": {
"typescript": {
"disabled": true
}
}
}
```

* * *

### [Custom LSP servers](#custom-lsp-servers)

You can add custom LSP servers by specifying the command and file extensions:

```

{
"$schema": "https://opencode.ai/config.json",
"lsp": {
"custom-lsp": {
"command": ["custom-lsp-server", "--stdio"],
"extensions": [".custom"]
}
}
}
```

* * *

## [Additional Information](#additional-information)

### [PHP Intelephense](#php-intelephense)

PHP Intelephense offers premium features through a license key. You can provide a license key by placing (only) the key in a text file at:

- On macOS/Linux: `$HOME/intelephense/license.txt`
- On Windows: `%USERPROFILE%/intelephense/license.txt`

The file should contain only the license key with no additional content.