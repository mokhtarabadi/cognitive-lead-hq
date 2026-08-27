---
name: freebuff-documents
description: SOP for creating and editing Freebuff knowledge documents (AGENTS.md, CLAUDE.md, *.knowledge.md, ~/.AGENTS.md) and defining always-loaded roles. Use when the user asks to add, edit, or document Freebuff rules, roles, personas, or project instructions — e.g. "add a role to the global agents file", "make the agent always know X", "define a persona". Triggered in any Freebuff-runtime project (vendor: CodebuffAI, source github.com/CodebuffAI/freebuff).
---

# Freebuff Documents & Always-Loaded Roles

Freebuff has **no dedicated role/persona feature**. Its "persona" strings are hardcoded display
metadata for built-in agents only. The sanctioned way to give a session an always-present role is the
**knowledge-file system**: markdown files that Freebuff injects into every session's system prompt via
the `KNOWLEDGE_FILES_CONTENTS` placeholder. This works on the **free tier** — it is injected into
`base3-free-*` / `base2-free-*` system prompts, no `.agents/*.ts` spawn needed.

## 1. What Freebuff Loads (verified 2026-08-26 against github.com/CodebuffAI/freebuff)

| Scope                        | Files (priority order)                           | Notes                                                                                                             |
| ---------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Home (global, EVERY session) | `~/.AGENTS.md` > `~/.CLAUDE.md`                  | `loadUserKnowledgeFiles` — ONE file, `AGENTS.md` wins. `~/.knowledge.md` is **IGNORED** (left the priority list). |
| Project (per directory)      | `AGENTS.md` > `CLAUDE.md`, plus `*.knowledge.md` | One knowledge file per directory (`selectKnowledgeFilePaths`). Bare `knowledge.md` is **IGNORED**.                |

- Priority list is hardcoded: `KNOWLEDGE_FILE_NAMES = ['AGENTS.md', 'CLAUDE.md']` (case-insensitive).
- Selected files are injected verbatim into the system prompt, labeled with their paths, with the
  header: _"Project instructions: Each fenced block below is one instructions file, labeled with its
  path. Follow them for the rest of the session."_
- MCP servers (`~/.agents/mcp.json`), Skills (`~/.agents/skills/`), and custom agents
  (`~/.agents/*.ts`) are separate extension points — knowledge files are the rules/roles layer.

## 2. How to Add or Edit a Role

A role is a self-contained markdown section (identity, mission, standing duties, hard boundaries)
inside a knowledge file. Freebuff treats the whole file as instructions — no processing, no schema.

1. **Decide the scope:**
   - **Global (every project, every session):** edit the repo's versioned source
     `freebuff/AGENTS.global.md` (Cognitive Lead HQ convention) or another global rules file.
   - **Project-scoped (one repo only):** edit that repo's `AGENTS.md` / `CLAUDE.md` /
     `<name>.knowledge.md`.
2. **Write the role section** at the end of the file (or as a standalone `<name>.knowledge.md` for a
   single purpose). Keep it self-contained — identity, mission, standing duties, hard boundaries.
   Use plain Markdown. Do NOT rely on the custom `.agents/*.ts` agent prompt being present (free tier
   can't spawn it).
3. **Sync the global copy (only if you edited the versioned source):**
   ```bash
   cp freebuff/AGENTS.global.md ~/.AGENTS.md
   diff -q freebuff/AGENTS.global.md ~/.AGENTS.md   # → identical
   ```
4. **Document it** in the project: reference the role in `docs/freebuff-support.md` (or the project's
   equivalent doc) and log a `CHANGELOG.md` entry (Keep a Changelog).
5. **Verify:** confirm the target file is recognized as a knowledge file (see §4) and that the
   installed copy matches the source.

## 3. The Cognitive Executive Role (reference)

This project ships the **Cognitive Executive Role** in `freebuff/AGENTS.global.md`
(`## Cognitive Executive Role`), installed as `~/.AGENTS.md`. It distills
`freebuff/agents/cognitive-executor.ts`'s `systemPrompt` into an always-loaded form:

- **Identity & Mission** — executes `<hands_*_task>` XML blocks, gatekeeper (HALT + `⚠️ RULE
VIOLATION WARNING`), enforces the Kanban lifecycle.
- **Standing Duties** — AGENTS.md-first, skill loading, verification-before-completion,
  communication discipline (D/F/R/Q/A codes), circuit breakers, direct-input validation pipeline.
- **Hard Boundaries** — ZAC (no autonomous git add/commit/push), MCP-first context, no monolithic
  state (`TODO.md`/`STATE.md`), bash discipline.

Free-tier note: the role makes the base chat behave with Cognitive Executive discipline, but it does
NOT grant the agent's tool whitelist or `spawn_agents` (those are `.agents/*.ts`-only and blocked on
the free tier — see `docs/freebuff-support.md` §5).

## 4. Verification Snippets

```bash
# Knowledge-file recognition (mirrors Freebuff's isKnowledgeFile + home loader):
node -e '
const priority = ["agents.md", "claude.md"];
const home = (e) => e.startsWith(".") && priority.includes(e.slice(1).toLowerCase());
const proj = (f) => { const b = f.split("/").pop().toLowerCase();
  return priority.includes(b) || b.endsWith(".knowledge.md"); };
console.log("~/.AGENTS.md loaded:", home(".AGENTS.md"));          // true
console.log("~/.knowledge.md loaded:", home(".knowledge.md"));    // false (ignored!)
console.log("AGENTS.md loaded:", proj("AGENTS.md"));              // true
console.log("knowledge.md loaded:", proj("knowledge.md"));        // false (ignored!)
'
# Installed global rules match versioned source:
diff -q freebuff/AGENTS.global.md ~/.AGENTS.md
```

## 5. Conventions & Gotchas

- **`knowledge.md` / `~/.knowledge.md` are dead** — never write new rules there; the loader ignores
  them (docs from before 2026-08-26 claiming otherwise are stale).
- Keep each role section self-contained; knowledge files are injected verbatim with no further
  processing.
- Project `AGENTS.md` overrides global `~/.AGENTS.md` for that project — put project-specific rules
  in the project file, machine-wide baseline in the global file.
- After editing any `freebuff/AGENTS.global.md`, ALWAYS re-sync `~/.AGENTS.md` (step 2.3) — the
  installed copy is machine-local and not tracked by the repo.
- Skill copies must stay in sync: `skill-templates/freebuff-documents/` (source) →
  `~/.config/opencode/skills/freebuff-documents/` (OpenCode global) → `~/.agents/skills/freebuff-documents/`
  (Freebuff global).
