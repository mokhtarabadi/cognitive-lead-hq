# Task 323: Project-local skills visible in AGENTS.md

**File:** `tasks/qa/323-project-skills-registry.md`
**Source:** manager
**Type:** feature
**Status:** in-progress
**Project:** /home/mohammad/Develop/Projects/cognitive-lead-hq
**Priority:** High

## Goal

Project-local skills (e.g. `.opencode/skills/sop-maintenance`) visible in `AGENTS.md` via an audited Project Skills table, so the executor loads them with the same confidence as global skills.

## Problem (observed live 2026-10-17)

Project-local skills (e.g. `.opencode/skills/sop-maintenance` in this repo)
are invisible: the executor's Skill Auto-Loading Matrix only lists global
stack skills, so local skills are never loaded unless the Manager names them.
The agent cannot follow a skill it cannot see.

## Rule (owner-approved 2026-10-17)

The `audit-agents` skill template gains a mandatory condition: on every audit
it scans the project's local skill directories (`.opencode/skills/*/SKILL.md`
or equivalent) and (re)builds a **Project Skills table** inside that project's
`AGENTS.md` — one row per local skill: name, trigger (when to load), one-line
duty. Same shape as the global matrix so the executor treats both uniformly.

## Deliverable

- `audit-agents` template updated with the scan-and-table condition.
- This repo's `AGENTS.md` backfilled (proves the rule on itself).
- Sync test update.

## Local TODOs

- [x] Grounding reads (template, AGENTS, sop-maintenance, tests)
- [x] Template scan-and-table condition with two hard fails
- [x] Backfill root AGENTS.md verbatim
- [x] Sync test update (table presence, row-count match, stale-row fail)
- [x] Verify with RTK plus lint plus grep

## Acceptance Criteria

- [x] Audit without the table fails (rule enforced, not advisory).
- [x] Executor loads project-local skills with the same confidence as global ones.
- [x] Stale rows (deleted skill still listed) fail the audit.

## Definition of Done

- [x] Tests pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Brittle row-count test if local skill dirs change without AGENTS.md update (mitigated: test fails loudly by design).
- **Rollback plan:** Revert the three files via `git checkout --`.

## Execution Log & Reasoning

- Created 2026-10-17 from live miss (sop-maintenance never loaded). Owner implements.
- Seat Check: audit/template domains, no trigger words fired (explicit miss all seats), Architect minimum, single-seat plan, brainstorm not required. Brain plan approved by Manager ("Approved").
- Implemented 5 steps: read sop-maintenance SKILL.md (name plus description verbatim) plus registry test shape; template condition added in both criteria lists with two hard fails; AGENTS.md backfilled with Project Skills table (one verbatim row); sync test gained three tests (table presence, row-count match, stale-row fail) plus template-requirement test — one regex fix (blank line before table), 33 passed; no executor change per plan.
- D1: condition duplicated in both criteria lists (both enumerate required AGENTS.md contents).
- Stack-skill skip record: root=. markers=[package.json, go.mod, build.gradle.kts, pyproject.toml, vite.config] matched=[] reason="docs-only template plus registry change".

## Verification Evidence

- `rtk test /home/mohammad/v2ray-to-subs/.venv/bin/pytest tests/test_skill_registry.py tests/test_prompt_sync.py -q` — expected all pass, actual 33 passed (after one regex fix), exit 0. (Repo has no local pytest; foreign venv binary used as runner only.)
- `grep -n "Project Skills" AGENTS.md skill-templates/audit-agents/SKILL.md tests/test_skill_registry.py` — hits in all three.
- `grep -n "sop-maintenance" AGENTS.md` — one row hit, wording matches source SKILL.md verbatim.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/AGENTS.md b/AGENTS.md
index a37131d..62c6f87 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -119,6 +119,12 @@ You MUST follow these skill loading rules in every session:
 - **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
 - **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`, `nodejs-express`, `python-fastapi`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.
 
+## 🛑 PROJECT SKILLS (Local, Audited)
+
+| Name | Trigger (when to load) | Duty (one line) |
+| ---- | ---------------------- | --------------- |
+| `sop-maintenance` | When modifying this SOP repository | Rules for modifying the Cognitive Lead AI SOP repository |
+
 ## 🛑 CONTEXT BOOTSTRAPPING
 
 At the start of every task, you MUST call `search_memory` or `list_namespaces` to load any hidden project quirks relevant to your domain before implementing.
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 52028cf..e74d27d 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -7,6 +7,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 ## [Unreleased]
 
 ### Added
+- **Project Skills table in AGENTS.md (Task 323):** the `audit-agents` template now mandates a scan-and-table condition on every audit (scan `.opencode/skills/*/SKILL.md`, rebuild the table with name plus trigger plus duty; missing table and stale rows fail the audit); root `AGENTS.md` backfilled with the `sop-maintenance` row; `tests/test_skill_registry.py` enforces table presence, row-count match, and stale-row failure.
+
 - **Language policy: English inside, requested language outside (Task 322):** new `prompts/fragments/24-language_policy.md` (translate-first with complexity gating, per-message detection with Persian default, English-only internals plus Brain turns, approval literals English-only) wired via `prompts/manifest.txt`; fragments 05 (clarification in requested language), 13 (Cognitive Rule plus Output Style item 6 plus Approval Literals Guard), and 20 (handoff-language line) updated; `agents/cognitive-executor.md` Direct Input plus handoff plus Negative Patterns updated with approval gates untouched; `docs/conventions.md` clarification halt aligned; both sync tests updated (pin 9.61.0, new wording asserts, approval-English test). Bumped `<system_version>` 9.60.1 to 9.61.0 with byte-identical re-assemble. Note: `split_system_prompt.py` rewrites fragments from the prompt and drops unassembled files, so round-trip verification uses assemble-twice diff, never split.
 
 - **Goal sync wording fix (Task 321 rework):** closure is now first `goal_evidence` (file citations plus passing tests) then `goal_complete`, since `goal_complete` takes no arguments. Bumped `<system_version>` 9.60.0 to 9.60.1 with byte-identical re-assemble.
diff --git a/skill-templates/audit-agents/SKILL.md b/skill-templates/audit-agents/SKILL.md
index 9cf8301..07e13d0 100644
--- a/skill-templates/audit-agents/SKILL.md
+++ b/skill-templates/audit-agents/SKILL.md
@@ -27,6 +27,7 @@ The `AGENTS.md` file MUST explicitly contain the following operational constrain
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
+- **Project Skills Table (local skills)**: On every audit, scan the project's local skill directories (`.opencode/skills/*/SKILL.md` or equivalent) and (re)build a **Project Skills** table in that project's `AGENTS.md` — one row per local skill: name, trigger (when to load), one-line duty, same column shape as the global Skill Auto-Loading Matrix. Two hard fails: audit without the Project Skills table fails, and a stale row (deleted skill still listed) fails the audit.
 - **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
 - **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
 - **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
@@ -405,6 +406,7 @@ Additionally, the `docs/conventions.md` file MUST exist and contain:
 - **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
 - **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load the `task-generator` skill before creating new task files.
 - **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct the Hands to load every available skill matching the project's tech stack before task implementation.
+- **Project Skills Table (local skills)**: On every audit, scan the project's local skill directories (`.opencode/skills/*/SKILL.md` or equivalent) and (re)build a **Project Skills** table in that project's `AGENTS.md` — one row per local skill: name, trigger (when to load), one-line duty, same column shape as the global Skill Auto-Loading Matrix. Two hard fails: audit without the Project Skills table fails, and a stale row (deleted skill still listed) fails the audit.
 - **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
 - **MCP Report Generation**: `AGENTS.md` MUST instruct agents to generate context reports (`custom_context_read_source_files`) and tree reports (`custom_context_create_tree_report` — "create a tree of the project") via the MCP server and hand the file path to the Manager instead of reading `context-reports/` files inline.
 - **Explicit Staging Contract (F5)**: Verify that the active task's `Execution Log & Reasoning` or `summary_phase` passed a `modified_files` list to `stage_and_inject_diff` — blind `git add -A .` staging is banned because it sweeps parallel-session files into unrelated commits.
diff --git a/tests/test_skill_registry.py b/tests/test_skill_registry.py
index a4b1637..ce48949 100644
--- a/tests/test_skill_registry.py
+++ b/tests/test_skill_registry.py
@@ -353,3 +353,50 @@ def test_validate_opencode_positives():
         "spotless-java": {"command": ["mvn", "spotless:apply"], "extensions": [".java"]}
     }
     assert _run_validator(cfg) == (0, "")
+
+
+def _project_skills_table_rows():
+    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
+    m = re.search(r"## .*PROJECT SKILLS.*\n\n((?:\|.*\n)+)", text)
+    assert m, "AGENTS.md has no Project Skills table"
+    return [
+        line
+        for line in m.group(1).splitlines()
+        if line.startswith("|") and "Name" not in line and "----" not in line
+    ]
+
+
+def _local_skill_names():
+    return sorted(
+        p.parent.name for p in (ROOT / ".opencode" / "skills").glob("*/SKILL.md")
+    )
+
+
+def test_audit_template_requires_project_skills_table():
+    text = (ROOT / "skill-templates" / "audit-agents" / "SKILL.md").read_text(
+        encoding="utf-8"
+    )
+    assert "Project Skills Table" in text
+    assert "stale row" in text
+
+
+def test_project_skills_table_matches_local_skill_dirs():
+    local = _local_skill_names()
+    assert local, "no local skills found to audit"
+    rows = _project_skills_table_rows()
+    assert len(rows) == len(local), (
+        f"table rows {len(rows)} != local skills {len(local)}"
+    )
+    for name in local:
+        assert any(name in row for row in rows), (
+            f"local skill missing from table: {name}"
+        )
+
+
+def test_project_skills_table_has_no_stale_rows():
+    local = set(_local_skill_names())
+    for row in _project_skills_table_rows():
+        names = re.findall(r"`([a-z0-9-]+)`", row)
+        assert names, f"table row without skill name: {row}"
+        for name in names:
+            assert name in local, f"stale row for deleted skill: {name}"
```
<!-- END_GIT_DIFF -->
