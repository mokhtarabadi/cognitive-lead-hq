---
title: Agent Skills
url: https://opencode.ai/docs/skills/
source: crawler
fetched_at: 2026-02-14T12:04:49.810178-03:00
rendered_js: false
word_count: 416
summary: This document explains how to define and manage reusable agent behaviors using SKILL.md files within the OpenCode ecosystem. It covers directory structures, metadata formatting, permission configurations, and discovery mechanics for automated skills.
tags:
    - opencode
    - agent-skills
    - skill-definition
    - configuration
    - permissions
    - metadata
category: guide
---

Define reusable behavior via SKILL.md definitions

Agent skills let OpenCode discover reusable instructions from your repo or home directory. Skills are loaded on-demand via the native `skill` tool—agents see available skills and can load the full content when needed.

* * *

## [Place files](#place-files)

Create one folder per skill name and put a `SKILL.md` inside it. OpenCode searches these locations:

- Project config: `.opencode/skills/<name>/SKILL.md`
- Global config: `~/.config/opencode/skills/<name>/SKILL.md`
- Project Claude-compatible: `.claude/skills/<name>/SKILL.md`
- Global Claude-compatible: `~/.claude/skills/<name>/SKILL.md`
- Project agent-compatible: `.agents/skills/<name>/SKILL.md`
- Global agent-compatible: `~/.agents/skills/<name>/SKILL.md`

* * *

## [Understand discovery](#understand-discovery)

For project-local paths, OpenCode walks up from your current working directory until it reaches the git worktree. It loads any matching `skills/*/SKILL.md` in `.opencode/` and any matching `.claude/skills/*/SKILL.md` or `.agents/skills/*/SKILL.md` along the way.

Global definitions are also loaded from `~/.config/opencode/skills/*/SKILL.md`, `~/.claude/skills/*/SKILL.md`, and `~/.agents/skills/*/SKILL.md`.

* * *

## [Write frontmatter](#write-frontmatter)

Each `SKILL.md` must start with YAML frontmatter. Only these fields are recognized:

- `name` (required)
- `description` (required)
- `license` (optional)
- `compatibility` (optional)
- `metadata` (optional, string-to-string map)

Unknown frontmatter fields are ignored.

* * *

## [Validate names](#validate-names)

`name` must:

- Be 1–64 characters
- Be lowercase alphanumeric with single hyphen separators
- Not start or end with `-`
- Not contain consecutive `--`
- Match the directory name that contains `SKILL.md`

Equivalent regex:

* * *

## [Follow length rules](#follow-length-rules)

`description` must be 1-1024 characters. Keep it specific enough for the agent to choose correctly.

* * *

## [Use an example](#use-an-example)

Create `.opencode/skills/git-release/SKILL.md` like this:

```

---
name: git-release
description: Create consistent releases and changelogs
license: MIT
compatibility: opencode
metadata:
audience: maintainers
workflow: github
---
## What I do
- Draft release notes from merged PRs
- Propose a version bump
- Provide a copy-pasteable `gh release create` command
## When to use me
Use this when you are preparing a tagged release.
Ask clarifying questions if the target versioning scheme is unclear.
```

* * *

OpenCode lists available skills in the `skill` tool description. Each entry includes the skill name and description:

```

<available_skills>
<skill>
<name>git-release</name>
<description>Create consistent releases and changelogs</description>
</skill>
</available_skills>
```

The agent loads a skill by calling the tool:

```

skill({ name: "git-release" })
```

* * *

## [Configure permissions](#configure-permissions)

Control which skills agents can access using pattern-based permissions in `opencode.json`:

```

{
"permission": {
"skill": {
"*": "allow",
"pr-review": "allow",
"internal-*": "deny",
"experimental-*": "ask"
}
}
}
```

PermissionBehavior`allow`Skill loads immediately`deny`Skill hidden from agent, access rejected`ask`User prompted for approval before loading

Patterns support wildcards: `internal-*` matches `internal-docs`, `internal-tools`, etc.

* * *

## [Override per agent](#override-per-agent)

Give specific agents different permissions than the global defaults.

**For custom agents** (in agent frontmatter):

```

---
permission:
skill:
"documents-*": "allow"
---
```

**For built-in agents** (in `opencode.json`):

```

{
"agent": {
"plan": {
"permission": {
"skill": {
"internal-*": "allow"
}
}
}
}
}
```

* * *

Completely disable skills for agents that shouldn’t use them:

**For custom agents**:

```

---
tools:
skill: false
---
```

**For built-in agents**:

```

{
"agent": {
"plan": {
"tools": {
"skill": false
}
}
}
}
```

When disabled, the `<available_skills>` section is omitted entirely.

* * *

## [Troubleshoot loading](#troubleshoot-loading)

If a skill does not show up:

1. Verify `SKILL.md` is spelled in all caps
2. Check that frontmatter includes `name` and `description`
3. Ensure skill names are unique across all locations
4. Check permissions—skills with `deny` are hidden from agents