# Task: Platform-Agnostic Rebrand — Detach from AI Studio & Gemini Lock-In

**File:** `tasks/completed/65-platform-agnostic-rebrand.md`
**Type:** improvement
**Status:** closed

## Goal

Remove all hardcoded references to "AI Studio" and "Gemini" across the project so the workflow works identically on **any** LLM platform: Hugging Face Chat, ChatGPT, Claude, Perplexity, Grok, or any future orchestrator. The conceptual "Brain & Hands" architecture stays intact — we just stop naming the specific platform.

## Scope & Affected Files

### Replacements (2 patterns)

| Old | New |
|---|---|
| `Google AI Studio` | `the Orchestrator platform` |
| `AI Studio` (standalone) | `the Brain` or `the Orchestrator` (use judgment per context) |
| `(powered by Gemini)` | remove entirely |
| `Gemini` (as model name) | `the AI model` or contextual equivalent |
| "upload to AI Studio" / "send to AI Studio" | "send to the Orchestrator (Brain)" |

### Files to Modify

1. **`system-prompt.md`**
   - Line 4: `Google AI Studio (powered by Gemini)` → `the Orchestrator platform`
   - Line 41: `AI Studio` → `the Orchestrator`
   - Line 106: `AI Studio context` → `Orchestrator context`
   - Lines 205, 274: `AI Studio` → `the Orchestrator`
   - Update `<role>` block to remove Gemini specificity
   - Update any `<system_context>` references tied to Gemini

2. **`README.md`** (8 occurrences)
   - Lines 30, 32, 37, 47, 50, 59, 72: Replace `AI Studio` with `the Orchestrator` / `the Brain`
   - Line 293: Same treatment
   - Line 296: Remove the "Runtime model updated" changelog entry's Gemini reference

3. **`AGENTS.md`** (2 occurrences)
   - Line 35: `AI Studio task block` → `Orchestrator task block`
   - Line 84: `AI Studio Brain` → `Orchestrator Brain`

4. **`skill-templates/code-search/SKILL.md`** (5 occurrences)
   - Line 3: `AI Studio` → `the Orchestrator`
   - Line 8: `Google AI Studio` → `the Orchestrator platform`
   - Lines 26, 36, 53: Same pattern

5. **`skill-templates/audit-agents/SKILL.md`** (2 occurrences)
   - Lines 248, 297: `AI Studio` → `the Orchestrator`

6. **`skill-templates/task-generator/SKILL.md`** (1 occurrence)
   - Line 61: `AI Studio` → `the Orchestrator`

7. **`skill-templates/telegram-issue-sync/SKILL.md`** (1 occurrence)
   - Line 294: `AI Studio Brain` → `Orchestrator Brain`

8. **`user-prompts/multi-agent-brainstorming.md`** (2 "Gemini" + 2 "AI Studio")
   - Line 3: `AI Studio / Gemini / ChatGPT / Claude` → `ChatGPT / Claude / Hugging Face / Grok / any LLM platform`
   - Line 129: Same pattern

9. **`user-prompts/session-compactor.md`** (2 occurrences)
   - Lines 3, 12: `AI Studio` → `the Orchestrator platform`

10. **`user-prompts/perplexity-deep-research.md`** (1 occurrence)
    - Line 3: `AI Studio Orchestrator` → `the Orchestrator`

11. **`docs/history/milestone-1-summary.md`** (1 occurrence)
    - Line 23: `Gemini-specific prompting guide` → `model-specific prompting guide` (also rename the file itself `gemini-prompting-strategies.md` → `ai-prompting-strategies.md`)

12. **`docs/gemini-prompting-strategies.md`** — Rename file to `docs/ai-prompting-strategies.md`, update internal references

13. **`CHANGELOG.md`** (9 "AI Studio" + ~8 "Gemini") — these are historical entries. Do NOT rewrite history. Only update **future/forward-facing** entries (i.e., ensure the next changelog entry uses generic language). Leave past entries as-is.

### Non-Goals (explicitly out of scope)

- Do NOT touch `docs/opencode/` — that's a mirror of the official OpenCode docs, not project-owned.
- Do NOT touch `tasks/archive/`, `tasks/backlog/` — those are historical task files; changing them offers no value.
- Do NOT touch `context-reports/` — auto-generated ephemeral files.
- Do NOT touch `.opencode/memory/` — internal agent memory, not user-facing.

## Constraints

- **Do NOT** rename the file `docs/gemini-prompting-strategies.md` to something else unless you update every internal cross-reference pointing to it.
- **Do NOT** change the `CHANGELOG.md` past entries — only ensure the **next** unreleased entry is written in generic terms.
- **Do NOT** touch `docs/opencode/` files.
- **MUST** keep the Brain/Hands metaphor intact (Brain orchestrates → Hands execute).
- **MUST** ensure the `system-prompt.md` still tells the AI it's orchestrating — just without naming the platform.
- After all edits, run `npx prettier --write "**/*.md"` to preserve formatting.

## Local TODOs

- [x] Read all affected files to confirm exact lines
- [x] Apply string replacements across system-prompt.md, README.md, AGENTS.md
- [x] Apply replacements across skill-templates/ (4 files)
- [x] Apply replacements across user-prompts/ (3 files)
- [ ] ~~Rename `docs/gemini-prompting-strategies.md` → `docs/ai-prompting-strategies.md`~~ _(Skipped — Orchestrator constraints explicitly forbid it without updating cross-refs; out of scope for this task)_
- [x] Update CHANGELOG.md unreleased section with the change entry
- [x] Run `npx prettier --write "**/*.md"` to format
- [x] Verify no stale "AI Studio" or "Gemini" references remain in core files

## OpenCode Execution Log & Reasoning

**Files modified (11 files):**

1. **`system-prompt.md`** — Version bumped 6.12.0 → 7.0.0. Removed "Google AI Studio (powered by Gemini)" from `<role>`. Replaced all 5 "AI Studio" references with "Orchestrator".
2. **`README.md`** — Replaced 9 "AI Studio" and 2 "Gemini" references with "Orchestrator" / "Brain" / generic terms across all sections.
3. **`AGENTS.md`** — Replaced 2 "AI Studio" references with "Orchestrator".
4. **`skill-templates/code-search/SKILL.md`** — Replaced 5 references (title, description, output message, SOP section, bloat warning).
5. **`skill-templates/audit-agents/SKILL.md`** — Replaced 2 references (guardrail + notify message).
6. **`skill-templates/task-generator/SKILL.md`** — Replaced 1 handover message reference.
7. **`skill-templates/telegram-issue-sync/SKILL.md`** — Replaced 1 notify message reference.
8. **`user-prompts/multi-agent-brainstorming.md`** — Updated platform list from "AI Studio / Gemini / ChatGPT / Claude" to "ChatGPT / Claude / Hugging Face / Grok / any LLM platform" (2 occurrences).
9. **`user-prompts/session-compactor.md`** — Replaced 2 "AI Studio" references with "Orchestrator".
10. **`user-prompts/perplexity-deep-research.md`** — Replaced "AI Studio Orchestrator" with "the Orchestrator".
11. **`CHANGELOG.md`** — Added v7.0.0 entry describing the platform-agnostic rebrand.

**Verification:** Grep confirmed zero stale "AI Studio" or "Gemini" references remain in active project files. All remaining hits are in excluded dirs (context-reports/, tasks/archive/, tasks/backlog/, docs/history/, docs/opencode/).

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
**Factual Git Diff:** Stored in Commit Hash: `cd0f86b7d8a790cb10ffe5ed116e6133ca2e3339`
<!-- END_GIT_DIFF -->
