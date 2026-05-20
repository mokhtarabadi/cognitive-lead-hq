---
title: Formatters
url: https://opencode.ai/docs/formatters
source: sitemap
fetched_at: 2026-04-17T06:32:54.833089815-03:00
rendered_js: false
word_count: 353
summary: This document explains how OpenCode handles automatic code formatting using built-in and custom formatters across various programming languages.
tags:
    - opencode
    - code-formatting
    - configuration
    - developer-tools
category: guide
---

OpenCode uses language specific formatters.

OpenCode automatically formats files after they are written or edited using language-specific formatters. This ensures that the code that is generated follows the code styles of your project.

* * *

## [Built-in](#built-in)

OpenCode comes with several built-in formatters for popular languages and frameworks. Below is a list of the formatters, supported file extensions, and commands or config options it needs.

FormatterExtensionsRequirementsair.R`air` command availablebiome.js, .jsx, .ts, .tsx, .html, .css, .md, .json, .yaml, and [more](https://biomejs.dev/)`biome.json(c)` config filecargofmt.rs`cargo fmt` command availableclang-format.c, .cpp, .h, .hpp, .ino, and [more](https://clang.llvm.org/docs/ClangFormat.html)`.clang-format` config filecljfmt.clj, .cljs, .cljc, .edn`cljfmt` command availabledart.dart`dart` command availabledfmt.d`dfmt` command availablegleam.gleam`gleam` command availablegofmt.go`gofmt` command availablehtmlbeautifier.erb, .html.erb`htmlbeautifier` command availablektlint.kt, .kts`ktlint` command availablemix.ex, .exs, .eex, .heex, .leex, .neex, .sface`mix` command availablenixfmt.nix`nixfmt` command availableocamlformat.ml, .mli`ocamlformat` command available and `.ocamlformat` config fileormolu.hs`ormolu` command availableoxfmt (Experimental).js, .jsx, .ts, .tsx`oxfmt` dependency in `package.json` and an [experimental env variable flag](https://opencode.ai/docs/cli/#experimental)pint.php`laravel/pint` dependency in `composer.json`prettier.js, .jsx, .ts, .tsx, .html, .css, .md, .json, .yaml, and [more](https://prettier.io/docs/en/index.html)`prettier` dependency in `package.json`rubocop.rb, .rake, .gemspec, .ru`rubocop` command availableruff.py, .pyi`ruff` command available with configrustfmt.rs`rustfmt` command availableshfmt.sh, .bash`shfmt` command availablestandardrb.rb, .rake, .gemspec, .ru`standardrb` command availableterraform.tf, .tfvars`terraform` command availableuv.py, .pyi`uv` command availablezig.zig, .zon`zig` command available

So if your project has `prettier` in your `package.json`, OpenCode will automatically use it.

* * *

## [How it works](#how-it-works)

When OpenCode writes or edits a file, it:

1. Checks the file extension against all enabled formatters.
2. Runs the appropriate formatter command on the file.
3. Applies the formatting changes automatically.

This process happens in the background, ensuring your code styles are maintained without any manual steps.

* * *

## [Configure](#configure)

You can customize formatters through the `formatter` section in your OpenCode config.

```json

{
"$schema": "https://opencode.ai/config.json",
"formatter": {}
}
```

Each formatter configuration supports the following:

PropertyTypeDescription`disabled`booleanSet this to `true` to disable the formatter`command`string\[]The command to run for formatting`environment`objectEnvironment variables to set when running the formatter`extensions`string\[]File extensions this formatter should handle

Let’s look at some examples.

* * *

### [Disabling formatters](#disabling-formatters)

To disable **all** formatters globally, set `formatter` to `false`:

```json

{
"$schema": "https://opencode.ai/config.json",
"formatter": false
}
```

To disable a **specific** formatter, set `disabled` to `true`:

```json

{
"$schema": "https://opencode.ai/config.json",
"formatter": {
"prettier": {
"disabled": true
}
}
}
```

* * *

### [Custom formatters](#custom-formatters)

You can override the built-in formatters or add new ones by specifying the command, environment variables, and file extensions:

```json

{
"$schema": "https://opencode.ai/config.json",
"formatter": {
"prettier": {
"command": ["npx", "prettier", "--write", "$FILE"],
"environment": {
"NODE_ENV": "development"
},
"extensions": [".js", ".ts", ".jsx", ".tsx"]
},
"custom-markdown-formatter": {
"command": ["deno", "fmt", "$FILE"],
"extensions": [".md"]
}
}
}
```

The **`$FILE` placeholder** in the command will be replaced with the path to the file being formatted.