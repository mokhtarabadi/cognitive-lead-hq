# Freebuff Documents & Always-Loaded Roles

> **Purpose of this document.** Explains how Freebuff's knowledge-file system works, how this project
> defines always-loaded roles (including the **Cognitive Executive Rule**), and how to add or edit
> them. Companion to `docs/freebuff-support.md` (extension points + port record) and the
> `freebuff-documents` skill (the editing SOP). Verified 2026-08-26 against the public source
> `github.com/CodebuffAI/freebuff`.

## 1. What Freebuff Loads

Freebuff has **no dedicated role/persona feature** — the word "persona" in its source
(`common/src/constants/agents.ts`) is only hardcoded display metadata for built-in agents. The
sanctioned way to give every session an always-present role is the **knowledge-file system**:
markdown files injected into the session's system prompt via the `KNOWLEDGE_FILES_CONTENTS`
placeholder (`packages/agent-runtime/src/templates/strings.ts`).

| Scope                        | Files (priority order)                           | Notes                                                                                                                                          |
| ---------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Home (global, EVERY session) | `~/.AGENTS.md` > `~/.CLAUDE.md`                  | `loadUserKnowledgeFiles` (`sdk/src/run-state.ts`) loads ONE file; `AGENTS.md` wins. `~/.knowledge.md` is **IGNORED** (left the priority list). |
| Project (per directory)      | `AGENTS.md` > `CLAUDE.md`, plus `*.knowledge.md` | `selectKnowledgeFilePaths` — one file per directory. Bare `knowledge.md` is **IGNORED**.                                                       |

- The priority list is hardcoded: `KNOWLEDGE_FILE_NAMES = ['AGENTS.md', 'CLAUDE.md']`
  (`common/src/constants/knowledge.ts`), matched case-insensitively.
- Selected files are injected **verbatim** into the system prompt, labeled with their paths, under
  the header _"Project instructions: Each fenced block below is one instructions file, labeled with
  its path. Follow them for the rest of the session."_
- This works on the **free tier**: knowledge files are injected into the `base3-free-*` (and
  `base2-free-*`) system prompts, so roles apply even though custom `.agents/*.ts` agents cannot be
  spawned (see `docs/freebuff-support.md` §5).

## 2. The Cognitive Executive Rule

This project ships the **Cognitive Executive Role** as an always-loaded global rule. It is defined in
the versioned source `freebuff/AGENTS.global.md` under `## Cognitive Executive Role` and installed as
`~/.AGENTS.md` — so every Freebuff session on this machine knows the role without needing to spawn
the custom agent.

**What it contains** (distilled from `freebuff/agents/cognitive-executor.ts`'s `systemPrompt`):

- **Identity & Mission** — the agent is the Cognitive Executive: it executes `<hands_*_task>` XML
  task blocks with precision, is the final gatekeeper (HALT + `⚠️ RULE VIOLATION WARNING` on rule
  violations), and enforces the Kanban task lifecycle (`backlog → in-progress → qa → completed`).
- **Standing Duties** — AGENTS.md-first reading, skill loading (via the Skill Auto-Loading Matrix),
  verification-before-completion, communication discipline (reference-point codes D/F/R/Q/A, no
  flattery, no scope creep), circuit breakers (`⚠️ CIRCUIT BREAKER` on tool loops/drift/divergence/
  cost spirals), and the direct-input validation pipeline for ad-hoc Manager messages.
- **Hard Boundaries** — Zero-Autonomous-Commit (ZAC: never `git add`/`commit`/`push`; the only
  autonomous Git op is `git mv` for Kanban moves), MCP-first context gathering, no monolithic state
  files (`TODO.md`/`STATE.md`), and bash discipline (non-interactive flags only).

**Free-tier caveat:** the role makes the base chat behave with Cognitive Executive discipline, but it
does NOT grant the agent's tool whitelist or `spawn_agents` capability — those belong to the
`.agents/*.ts` definition, which the free tier cannot spawn (paid/credits tier required, §5 of
`docs/freebuff-support.md`).

## 3. How to Add or Edit an Always-Loaded Role

1. **Choose the scope.**
   - Global (every project, every session) → edit `freebuff/AGENTS.global.md` (this project's
     versioned source for `~/.AGENTS.md`).
   - Project-scoped (one repo) → edit that repo's `AGENTS.md` / `CLAUDE.md` / `<name>.knowledge.md`.
2. **Write a self-contained role section** (identity, mission, standing duties, hard boundaries) in
   plain Markdown. Freebuff does no processing — the file is injected verbatim.
3. **Sync the global copy** (only if you edited the versioned source):
   ```bash
   cp freebuff/AGENTS.global.md ~/.AGENTS.md
   diff -q freebuff/AGENTS.global.md ~/.AGENTS.md   # → identical
   ```
4. **Document + log** — reference the role in this doc / `docs/freebuff-support.md` and add a
   `CHANGELOG.md` entry (Keep a Changelog).
5. **Verify** — run the recognition snippet below and confirm the installed copy matches the source.

### 3.1 Installing / Reinstalling the Global Rules File (`freebuff/AGENTS.global.md` → `~/.AGENTS.md`)

Exact install procedure (also codified in the upgrade-workflow memory
`.opencode/memory/workflows/global-install-upgrade.md`):

```bash
# 1. Prerequisite — Freebuff CLI installed and current:
~/.config/manicode/freebuff --version        # → 0.0.156 (latest verified 2026-08-26)
#    (No public versioned release channel — GitHub Releases = unrelated "Codecane" staging builds.
#     Re-download from freebuff.com when a newer version is announced.)

# 2. Install / re-sync the global rules from the versioned repo source:
cp freebuff/AGENTS.global.md ~/.AGENTS.md

# 3. Mandatory verification:
diff -q freebuff/AGENTS.global.md ~/.AGENTS.md                    # → identical
 grep -c "Cognitive Executive Role (Always Loaded)" ~/.AGENTS.md   # → 1
```

- **Reinstall triggers:** first install, ANY edit to `freebuff/AGENTS.global.md`, machine reinstall,
  `LLM.txt` Step 7.5 (which installs `~/.agents/` + `~/.AGENTS.md` together).
- **Rollback:** restore the source from git (`git checkout -- freebuff/AGENTS.global.md` after
  stashing local edits) then re-`cp`; the installed copy is always a byte-copy of the source.
- The same procedure is the last step of every global upgrade cycle (`global-install-upgrade` memory:
  step 2 `cp freebuff/AGENTS.global.md ~/.AGENTS.md` + version check).

## 4. Verification

```bash
# 1. Installed global rules match the versioned source:
diff -q freebuff/AGENTS.global.md ~/.AGENTS.md && echo "IDENTICAL"

# 2. The role section is present in both:
grep -c "Cognitive Executive Role" ~/.AGENTS.md   # → 1

# 3. Knowledge-file recognition (mirrors Freebuff's loader):
node -e '
const priority = ["agents.md", "claude.md"];
const home = (e) => e.startsWith(".") && priority.includes(e.slice(1).toLowerCase());
const proj = (f) => { const b = f.split("/").pop().toLowerCase();
  return priority.includes(b) || b.endsWith(".knowledge.md"); };
console.log("~/.AGENTS.md loaded:", home(".AGENTS.md"));        // true
console.log("~/.knowledge.md loaded:", home(".knowledge.md"));  // false (ignored!)
console.log("AGENTS.md loaded:", proj("AGENTS.md"));            // true
console.log("knowledge.md loaded:", proj("knowledge.md"));      // false (ignored!)
'
```

## 5. Global + Project AGENTS Merge (both must load)

When a machine has a global `~/.AGENTS.md` AND a project has its own `AGENTS.md`, BOTH files are
loaded in every session — they merge, they do not replace each other. Verified 2026-08-26 against the
source loaders:

| Runtime  | Global (home)                                                                                       | Project (per directory)                                | Merge semantics                                                                                                                                                   |
| -------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Freebuff | `~/.AGENTS.md` > `~/.CLAUDE.md` (ONE file)                                                          | `AGENTS.md` > `CLAUDE.md`, plus `*.knowledge.md`       | Both are injected into the system prompt as separate labeled blocks (`KNOWLEDGE_FILES_CONTENTS`); on CONFLICTING rules the project file wins (higher specificity) |
| OpenCode | Global rules via `~/.config/opencode/opencode.json` `instructions` (+ `opencode-shell-strategy.md`) | `AGENTS.md` read by the agent as its entry-point rules | Both load; the project `AGENTS.md` is the agent's primary rule set and the global instructions add baseline constraints                                           |

**How to verify in any project:**

1. Freebuff — confirm both blocks appear in the session system prompt (the home file and the project
   file, each labeled with its path), and that a conflicting rule resolves to the project value.
2. OpenCode — confirm the global `instructions` file content AND the project `AGENTS.md` are both
   honored (e.g. the global ZAC rule and the project's own rules both apply).
3. Repo-level guard: `diff -q freebuff/AGENTS.global.md ~/.AGENTS.md` (global source vs installed) and
   `grep -c "Cognitive Executive Role" ~/.AGENTS.md` (role present globally) — if the project
   `AGENTS.md` re-states a rule differently, the project value wins for that project; the global file
   still applies everywhere else.

**Design rule:** machine-wide baseline (ZAC, validation pipeline, roles) belongs in `~/.AGENTS.md`;
project-specific rules belong in the project's `AGENTS.md`. Keep the two non-contradictory — the
project file may tighten or extend, never weaken, the global baseline.

## 6. Conventions & Gotchas

- **`knowledge.md` / `~/.knowledge.md` are dead names** — Freebuff's loader ignores them (verified
  2026-08-26). Any docs claiming `~/.knowledge.md` has precedence 1 are stale; the real order is
  `~/.AGENTS.md` > `~/.CLAUDE.md`.
- **Project overrides global:** a project's `AGENTS.md` takes precedence over `~/.AGENTS.md` for
  that project — put project-specific rules in the project file, machine-wide baseline in the global
  file.
- **Always re-sync `~/.AGENTS.md`** after editing `freebuff/AGENTS.global.md` — the installed copy is
  machine-local and not tracked by the repo (see `.opencode/memory/workflows/global-install-upgrade.md`).
- The editing SOP lives in the **`freebuff-documents` skill** (`skill-templates/freebuff-documents/SKILL.md`,
  synced to `~/.config/opencode/skills/` and `~/.agents/skills/`).
