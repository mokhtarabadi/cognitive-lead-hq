---
name: governance
description: Agent protocol auditing plus living folder docs scaffolding — AGENTS.md governance and README/DECISIONS baselines in one meta skill.
---

# Governance Meta Skill (slim index)

Meta skill combining **audit-agents** (project-agnostic Agent Protocol Auditor), **init-folder-docs** (Living Folder Docs Initializer), and **opencode-init** (project-only `opencode.json` generator, Part 3 of `templates/init.md`). Load one skill for governance work: audit/patch `AGENTS.md`, scaffold slice docs, or generate a project `opencode.json`. Full bodies are verbatim in `templates/` — read only the part you need.

---

## Critical Rules (no read needed)

- **Zero-Autonomous-Commit:** `git add`, `git commit`, `git checkout`, `git push` denied. Stage via `custom_context_stage_and_inject_diff`; close ONLY on exact “Approved for closure” / “Close task”.
- **Absent-File Policy:** optional `DESIGN.md`/`docs/architecture.md`/`docs/data_model.md` missing → SKIP with note, never halt. Exception: UI work requires `DESIGN.md`.
- **Decentralized tasks:** individual files in `tasks/{backlog,in-progress,qa,completed,archive}/` only. No `TODO.md`/`STATE.md`.
- **Living Folder Docs:** every slice needs sibling `README.md` + `DECISIONS.md` with code pointers; keep in sync.
- **Financial Ledger:** snapshot-on-write + `$ifNull` precedence + alerting + deep merge. **DSP:** `set -euo pipefail`, never mask with `2>/dev/null`.
- **Lite Mode / Night Mode:** deprecated. Every task follows the full workflow; no bypass. Purge if found.
- **Task numbers:** only in code comments, `CHANGELOG.md`, task files, history archives, HTML comments. Never in prompt prose.
- **Edit discipline:** native edit/file-write tools only. No python/shell/heredoc/`sed -i` edits.

## When to Read Templates

- **Audit or patch `AGENTS.md` / `docs/conventions.md`?** Read `templates/audit.md` (Target Audit Criteria, Mode 1 template, Mode 2 resolution, pitfalls).
- **Scaffold slice docs for a new module?** Read `templates/init.md` Parts 2–3 (discovery → README/DECISIONS → code pointers; project `opencode.json` generation).

Templates are authoritative; this index only summarizes. Skills registry: `prompts/fragments/07-agent_skills_registry.md`.
