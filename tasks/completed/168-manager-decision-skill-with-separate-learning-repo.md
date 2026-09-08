# Task 168: Manager-Decision Skill With Separate Learning Repo

**File:** `tasks/qa/168-manager-decision-skill-with-separate-learning-repo.md`
**Source:** telegram
**Type:** feature
**Status:** in-progress

## Source Context

## Goal

Build a manager-decision skill that extracts per-session manager decisions into a separate repo to evolve a manager-AI sample.

## Original Message (Persian)

بعد یک بخش جدید هم میشه اضافه کرد بهش منیجر دیسیژن، یک اسکیل باشه، خب؟ هر وقت فراخوانی بشه توی اون جلسه، تصمیمهایی که مدیر گرفته صحبتهایی کرده سیستم دیزاینی که کرده، همه رو یاد بگیریم توی یک ریپوی جداگانه همیشه داشته باشیم تصمیمات مدیر رو که بعداً اون نمونهی هوش مصنوعی که از مدیر ساختیم روز به روز بتونه بهبود پیدا کنه و بهتر بشه. بعد یک جای دیگه کامل یه نمونه کامل باشه بعد تصمیمات جزء دیگه نیاز به منیجر واقعی نباشه و از همون نمونه ساخته شده ایآی که از تصمیمات منیجر شکل گرفته توی سشنها استفاده بشه، مثلاً این شکل باشه، این نحو باشه که توی سشنهای مختلف خود منیجر مثلاً اون اسکیل یا ام سی پی میتونه باشه یا اسکیل میتونه باشه یا یک پلاگین برای اوپن کد باشه. صدا بزنه بعد اون سشن تصمیماتی که مدیر گرفته، مدیر گرفته شده استخراج بشه و هویت بصری ایآی منیجر یا مدیر آپدیت بشه.

#remaining

## English Translation

Then a new section can be added to it — manager decision — as a skill, okay? Whenever it is invoked in that session, the decisions the manager made, the things said, the system design done — we learn all of it and always keep the manager's decisions in a separate repo, so that later the AI sample we built from the manager can improve day by day and get better. Then somewhere else there is a complete full sample; after that, micro-decisions no longer need the real manager, and we use that built AI sample shaped from the manager's decisions in the sessions. For example it would be like this — in different sessions the manager itself, e.g., that skill or MCP, or it can be a skill or a plugin for OpenCode — it calls, then the decisions made by the manager in that session are extracted, and the visual identity of the AI manager is updated.

## Refactored Prompt

```markdown
<role>
You are an elite Knowledge Systems Architect specializing in decision-capture pipelines, skill/MCP design for OpenCode, and continual manager-AI refinement.
</role>

<system_context>
Environment: Cognitive Lead HQ + OpenCode. Requirement: a manager-decision skill (or MCP, or OpenCode plugin) invoked per session that extracts manager decisions/statements/system-designs and persists them in a separate repo, continually improving a manager-AI sample until micro-decisions no longer need the real manager. Related to Task 167 (persona commands) but scoped here to decision learning + identity update.
</system_context>

<agentic_reasoning>
Before designing, output a <reasoning_log> analyzing: (1) logical dependencies — session transcript source, extraction trigger, repo schema, sample update cadence; (2) risk assessment — privacy/leakage of manager statements, hallucinated decisions, identity drift; (3) abductive reasoning — which session signals count as decisions vs chatter; (4) precision and grounding — cite prompts/archive/17-decision_logging_mandate.md, project-memory skill, .opencode/memory structure.
</agentic_reasoning>

<constraints>
- You MUST store raw manager statements verbatim alongside extracted decisions; do NOT summarize away the source.
- You MUST define the separate repo schema (decision record fields, session linkage, versioning) before any automation.
- You MUST define the invocation contract (skill vs MCP vs plugin — pick one primary, list trade-offs).
- Do NOT auto-evolve the manager-AI sample without a review gate; identity updates require approval.
- Do NOT overlap Task 167's persona-command scope except via explicit interface.
</constraints>

<output_format>
Return: (1) repo schema + storage layout, (2) skill/MCP/plugin spec with invocation examples, (3) extraction pipeline (transcript → decisions → repo PR), (4) sample-evolution loop with review gate and identity-update rule, (5) privacy/redaction policy.
</output_format>
```

## Relevant Code Context

- `prompts/archive/17-decision_logging_mandate.md` — prior decision-logging mandate to extend.
- `.opencode/memory/*` + `project-memory` skill — existing memory shards vs new separate decision repo.
- `skill-templates/*` — template for the new manager-decision skill.
- `agents/cognitive-executor.md` — invocation point inside sessions.
- `mcp-memory-server/server.py` — existing memory MCP if MCP option chosen.

## AI Analysis & Opinion

This is the learning half of message 587's execution half: 587 moves execution into persona commands, 588 preserves the manager's judgment as training data. Recommend a decision-record schema (session id, timestamp, verbatim quote, decision, rationale, system-design refs, outcome) stored as append-only Markdown/JSON in the separate repo, with a gated promotion job that updates the manager-AI sample + visual identity. Biggest risks are privacy (manager statements persisted verbatim) and feedback loops (AI trained on its own outputs); mitigate with redaction rules and human review before sample promotion. Build after or alongside Task 167 with a shared invocation contract.

## Local TODOs

- [x] Initial codebase exploration
- [x] Define decision-repo schema and redaction policy
- [x] Verify functionality

## Acceptance Criteria

- [x] Decision-repo schema defined with verbatim-quote + linkage fields
- [x] Skill/MCP/plugin invocation contract specified with per-session example
- [x] Sample-evolution loop includes human review gate before identity update

## Verification Evidence

- **Test command:** `uv run --with pytest --with pathspec --with "mcp[cli]>=1.0,<2.0" --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin -- pytest tests/ -q` (repo root)
- **Expected result:** Full suite green: 55 pre-existing + 32 persona + 14 new decision-server tests = 101 passed; `py_compile` clean; `opencode.json` + schema JSON valid; both decision scripts exit 0 on empty repo
- **Actual result:** `101 passed, 8 warnings in 1.10s` (pre-existing pathspec notices); `COMPILE-OK`; `JSON-OK`; `validate-exit:0`; `compile-exit:0`
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Verbatim manager statements leak sensitive reasoning; auto-evolution drifts identity.
- **Rollback plan:** Keep decision repo append-only with revertible PRs; disable auto-promotion, keep manual review.

---

## Execution Log & Reasoning

Micro-task checklist (Steps 1–8, in order):

- [x] **Step 1:** `git mv tasks/backlog/168-*.md tasks/in-progress/168-*.md` (clean tree); header → `tasks/in-progress/...`, status → `in-progress`.
- [x] **Step 2:** Scaffolded `packages/cognitive-lead-decisions/` — `schema/decision.schema.json` (`decision_id` DEC-YYYYMMDD-NNN, `timestamp`, `project_name`, `verbatim_quote` original+English, `extracted_decision` summary/category/rationale/alternatives/tradeoffs, `redaction_verified`), `samples/manager_profile.md` (curated baseline: composition-over-inheritance, FastMCP-over-daemons, append-only, hard gates; generated section marked DO-NOT-EDIT), `scripts/compile_profile.py` (prints review draft to stdout, never writes the sample), `scripts/validate_decisions.py` (dependency-free structural validator, exit codes for CI).
- [x] **Step 3:** Implemented `mcp-decision-server/` — `redactor.py` (`sanitize_text` for sk-/ghp-/AIzaSy-/Bearer-/private-IP/credential patterns, `verify_clean` with a lookahead so `[REDACTED]` markers never false-positive; idempotent fixed point), `server.py` (FastMCP `ManagerDecisions`, `DECISION_REPO_PATH` with in-repo fallback; 5 tools: extract/record/query/profile/propose; lazy litellm; record path scrubs → verifies → validates → writes JSON+MD under `decisions/YYYY/MM/` → regenerates INDEX.md; propose runs the compile script in a subprocess and returns DRAFT_READY/EMPTY/ERROR without touching the sample).
- [x] **Step 4:** Created `skill-templates/manager-decision/SKILL.md` (frontmatter convention per project-memory template; triggers, extraction/consultation/evolution workflows, redaction rules, per-session invocation example; no legacy `OpenCode Execution Log` wording).
- [x] **Step 5:** Registered `manager_decisions` in `opencode.json` in repo list-form (`uv run mcp-decision-server/server.py`, 120s timeout — grounded deviation from the XML's stale `python`/`args` shape, same as Task 167) + 5 tool permission allows.
- [x] **Step 6:** `agents/cognitive-executor.md` — `manager-decision` row in the Skill Auto-Loading Matrix; Context Bootstrapping now consults `query_manager_decisions` + profile injection for architectural ambiguities.
- [x] **Step 7–8:** `tests/test_decision_server.py` — 14 tests (redactor ×5, record/validate ×4, query/profile/propose ×3, extract ×2 with stubbed litellm, all repo I/O in tmp dirs). Full suite **101 passed** (55 + 32 + 14), exit 0.

Fix during testing: `extract_session_decisions` imported litellm before the missing-transcript check, breaking its own graceful-empty contract under a bare interpreter — moved the existence check first (also cheaper at runtime).

_(The Hands: Manually log your technical changes, file edits, and architectural reasoning here BEFORE calling the MCP tool)_

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e0bf7d6..882aa57 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -14,6 +14,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **DCP dynamic context pruning like goal plugin (Task 163):** Added `@tarquinen/opencode-dcp` to `plugin` arrays in project `opencode.json` + `tui.json` (parity with global, mirrors `@prevalentware/opencode-goal-plugin` pattern from Task 126); extended `LLM.txt` §7 JSON example + TUI parity block + Option A note, new §7.7 DCP install/config/commands (`opencode plugin @tarquinen/opencode-dcp@latest --global`, `dcp.jsonc` global + `.opencode/dcp.jsonc` override, `/dcp` + `/dcp-compress`), verification checklist DCP checks. Installed globally + verified 4-way parity.
 - **owt worktree plugin (Task 164):** Installed `@nano-step/opencode-worktree-plugin` globally (`npm i -g` + `owt-setup install` → `~/.config/opencode/plugins/worktree-plugin.js` + 7 slash commands incl. `/init-worktree`, `/list-worktrees`, `/open-worktree`; file-based loading kept, `opencode.json`/`tui.json` untouched by design — npm spec resolves from project `node_modules` which this docs-only repo has none of, and owt is not a TUI panel plugin). Chose owt over `kdcokenny/opencode-worktree` (OCX-only, OCX not allowed) and `arturosdg/opencode-worktree` (standalone TUI). Project side: `.gitignore` guards (`.opencode/worktrees/`, `worktree-sessions.json`), new `LLM.txt` §7.8 install/commands/verify docs. Optional `owt hook --global` left disabled.
 - **Persona MCP engine replacing loop-engine (Task 167):** New stdio FastMCP server `mcp-persona-server/` (`dual_dispatch.py` XML/question classifier, `session.py` append-only JSONL transcripts + lineage projection, `telegram.py` stdlib-only Bot API approval gates, `server.py` with `dispatch_session_turn`/`get_session_summary`/`escalate_to_admin`/`request_admin_approval` tools on LiteLLM `PERSONA_MODEL`); slash commands `.opencode/commands/{qa,reviewer,manager,brainstorm}.md`; `agents/cognitive-executor.md` Persona Loop section (Implementation → QA → Review → Approval Gate → Closure + Dual Dispatch statuses); `opencode.json` `persona` entry (120s timeout for LLM turns) + tool permissions; `tests/test_persona_server.py` **28 passed**, full suite **83 passed**.
+- **Manager-decision learning repo + skill (Task 168):** New `packages/cognitive-lead-decisions/` (`schema/decision.schema.json` with verbatim-quote + linkage fields, `samples/manager_profile.md` baseline, `scripts/compile_profile.py` review-draft printer, `scripts/validate_decisions.py` dependency-free validator) and stdio FastMCP server `mcp-decision-server/` (`redactor.py` sanitize/verify engine, `server.py` with `extract_session_decisions`/`record_manager_decision`/`query_manager_decisions`/`get_manager_profile`/`propose_profile_evolution` — gated sample evolution, never auto-writes); universal `skill-templates/manager-decision/SKILL.md` (extraction/consultation/evolution workflows, per-session example); `opencode.json` `manager_decisions` entry + 5 tool permissions; executor matrix + bootstrapping consult past rulings; `tests/test_decision_server.py` **14 passed**, full suite **101 passed**.
 
 ### Changed
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index a2cd325..eaecdf6 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -67,6 +67,7 @@ If the Orchestrator or Manager forgets to explicitly list a skill in the `<conte
 | Creating a new task file              | `task-generator`                |
 | Closing or archiving a task           | `archive-tasks`                 |
 | Complex bug, deadlock, silent failure | `debug-instrumentation`         |
+| Manager decision capture, ruling reuse | `manager-decision`             |
 
 ## Direct Input (Ad-Hoc) Validation Protocol
 
@@ -82,7 +83,7 @@ If the Manager sends you a direct message that is NOT an XML task block (e.g., "
 
 To prevent hallucinations and respect hidden project constraints, you MUST integrate persistent memory into your execution workflow:
 
-1. **Read First (Mandatory):** At the absolute start of any task (before writing code), load the `project-memory` skill. Read `.opencode/memory/index.md` (if present) — the auto-generated Markdown index of all memory shards — alongside `AGENTS.md` and `DESIGN.md`, to get a compact overview before planning. Then use `search_memory` with keywords from the task description and the tech stack, or `read_memory` for specific keys selected from the index, to retrieve any saved constraints, quirks, or past architectural decisions. If the index is missing, fall back to `list_namespaces`/`search_memory` and trigger `rebuild_memory_index` if needed.
+1. **Read First (Mandatory):** At the absolute start of any task (before writing code), load the `project-memory` skill. Read `.opencode/memory/index.md` (if present) — the auto-generated Markdown index of all memory shards — alongside `AGENTS.md` and `DESIGN.md`, to get a compact overview before planning. Then use `search_memory` with keywords from the task description and the tech stack, or `read_memory` for specific keys selected from the index, to retrieve any saved constraints, quirks, or past architectural decisions. If the index is missing, fall back to `list_namespaces`/`search_memory` and trigger `rebuild_memory_index` if needed. When resolving architectural ambiguities, additionally consult the manager's past rulings via the `manager-decision` skill (`query_manager_decisions`, plus `get_manager_profile()` output injected into your reasoning) before re-asking the human manager.
 2. **Apply Constraints:** If memories are found via the index (selectively fetched with `read_memory` or `search_memory` based on the index overview), strictly adhere to them during implementation. Do not contradict past architectural decisions without explicitly flagging it to the Manager.
 3. **Auto-Save Criteria (Strict):** You MUST use `store_memory` to save new memories ONLY if the Orchestrator or Manager explicitly states a new project rule, architectural constraint, or reusable quirk.
    - **DO SAVE:** "The manager prefers Composition over Inheritance," "API X rate limits at 100 req/s, add caching," "Do not use Library Y because of Z."
diff --git a/mcp-decision-server/redactor.py b/mcp-decision-server/redactor.py
new file mode 100644
index 0000000..2c6e119
--- /dev/null
+++ b/mcp-decision-server/redactor.py
@@ -0,0 +1,77 @@
+"""Redaction engine for manager-decision persistence (Task 168).
+
+Every free-text field is scrubbed by `sanitize_text` BEFORE it touches the
+decision repo; `verify_clean` attests the stored text holds zero sensitive
+patterns, and its result feeds the record's `redaction_verified` flag.
+Patterns covered: provider API keys (`sk-...`, `ghp_...`, `AIzaSy...`),
+Bearer tokens, private IPv4 ranges (`10/8`, `172.16/12`, `192.168/16`),
+and generic `password = ...` / `token = ...` credential assignments.
+
+Pure standard library — deterministic and unit-testable without network.
+"""
+
+from __future__ import annotations
+
+import re
+
+# Each entry: (compiled pattern, replacement). Order matters: specific
+# provider keys first, generic credential assignments last.
+REDACTION_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
+    # OpenAI / OpenRouter style secret keys.
+    (re.compile(r"\bsk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{8,}\b"), "[REDACTED_API_KEY]"),
+    # GitHub personal access tokens.
+    (re.compile(r"\bghp_[A-Za-z0-9]{8,}\b"), "[REDACTED_GITHUB_TOKEN]"),
+    # Google API keys.
+    (re.compile(r"\bAIzaSy[A-Za-z0-9_-]{10,}\b"), "[REDACTED_GOOGLE_KEY]"),
+    # Bearer tokens (Authorization headers, config dumps).
+    (re.compile(r"\bBearer\s+[A-Za-z0-9\-._~+/=]{8,}", re.IGNORECASE), "Bearer [REDACTED]"),
+    # Private IPv4: 10/8, 172.16/12, 192.168/16 (loopback stays — harmless).
+    (re.compile(r"\b10(?:\.\d{1,3}){3}\b"), "[REDACTED_IP]"),
+    (re.compile(r"\b172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"), "[REDACTED_IP]"),
+    (re.compile(r"\b192\.168(?:\.\d{1,3}){2}\b"), "[REDACTED_IP]"),
+    # Generic credential assignments: password = "secret", token: xyz.
+    (re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*\S+"),
+     r"\1=[REDACTED]"),
+)
+
+# Detection patterns for the verify pass. Identical to REDACTION_RULES except
+# the credential-assignment pattern carries a negative lookahead so an
+# already-redacted `password=[REDACTED]` marker is NOT mistaken for a live
+# secret (otherwise verify_clean could never pass on sanitized text).
+_VERIFY_ASSIGNMENT = re.compile(
+    r"(?i)\b(password|passwd|secret|api[_-]?key|auth[_-]?token)\b\s*[:=]\s*(?!\[REDACTED\])\S+"
+)
+_VERIFY_RESIDUE: tuple[re.Pattern[str], ...] = tuple(
+    _VERIFY_ASSIGNMENT if rule is REDACTION_RULES[-1][0] else rule
+    for rule, _ in REDACTION_RULES
+)
+
+
+def sanitize_text(text: str) -> str:
+    """Scrub sensitive patterns from `text`, returning the redacted copy.
+
+    Idempotent: running it twice yields the same output (markers contain no
+    matchable secret shapes). Non-string input is coerced to str; empty
+    input returns empty.
+    """
+    if not isinstance(text, str):
+        text = str(text)
+    if not text:
+        return ""
+    scrubbed = text
+    for pattern, replacement in REDACTION_RULES:
+        scrubbed = pattern.sub(replacement, scrubbed)
+    return scrubbed
+
+
+def verify_clean(text: str) -> bool:
+    """Return True when no sensitive pattern remains in `text`.
+
+    Run on the SANITIZED text before persistence; a False result must block
+    the write (the record's `redaction_verified` stays False and the caller
+    rejects the decision). Markers like `[REDACTED_API_KEY]` never match —
+    they carry no secret-shaped content.
+    """
+    if not isinstance(text, str):
+        text = str(text)
+    return not any(pattern.search(text) for pattern in _VERIFY_RESIDUE)
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
new file mode 100644
index 0000000..80cf3f5
--- /dev/null
+++ b/mcp-decision-server/server.py
@@ -0,0 +1,373 @@
+#!/usr/bin/env -S uv run
+# /// script
+# requires-python = ">=3.10"
+# dependencies = [
+#     "mcp[cli]>=1.0,<2.0",
+#     "litellm",
+# ]
+# ///
+
+"""Manager-decision capture MCP server (Task 168).
+
+Learning half of the persona pipeline: per-session manager trade-offs and
+rulings are extracted (LiteLLM, default Gemini Flash), redacted, and
+persisted append-only into the decision repo
+(`packages/cognitive-lead-decisions/`, overridable via DECISION_REPO_PATH).
+Stored decisions feed `query_manager_decisions` (consultation) and
+`propose_profile_evolution` (gated sample updates — the script drafts, a
+human approves; this server never rewrites the sample itself).
+
+Transport: stdio FastMCP, mirroring mcp-persona-server. `litellm` is lazy so
+import and unit tests never need network or credentials.
+"""
+
+from __future__ import annotations
+
+import json
+import os
+import re
+import subprocess
+import sys
+from datetime import datetime, timezone
+from pathlib import Path
+from typing import Any, Optional
+
+from mcp.server.fastmcp import FastMCP
+
+from redactor import sanitize_text, verify_clean
+
+# Decision repo root: standalone checkout via env, else the in-repo package.
+REPO_ROOT = Path(
+    os.environ.get("DECISION_REPO_PATH", Path(__file__).resolve().parent.parent
+                   / "packages" / "cognitive-lead-decisions")
+)
+
+mcp = FastMCP("ManagerDecisions")
+
+# Free-text fields that must pass verify_clean before any write.
+_SCRUB_FIELDS = ("original", "english_translation", "summary", "rationale", "tradeoffs")
+
+
+def _repo_root() -> Path:
+    """Resolve (creating) the decision repo root."""
+    root = Path(os.environ.get("DECISION_REPO_PATH", str(REPO_ROOT)))
+    root.mkdir(parents=True, exist_ok=True)
+    return root
+
+
+def _utc_today() -> str:
+    """UTC date as YYYYMMDD for decision ids."""
+    return datetime.now(timezone.utc).strftime("%Y%m%d")
+
+
+def _next_decision_id(repo: Path) -> str:
+    """Next id of the form DEC-YYYYMMDD-NNN (daily zero-padded sequence)."""
+    prefix = f"DEC-{_utc_today()}-"
+    taken = sorted(
+        p.name for p in (repo / "decisions").rglob(f"{prefix}*.json")
+    ) if (repo / "decisions").exists() else []
+    seq = 0
+    for name in taken:
+        match = re.fullmatch(r"DEC-\d{8}-(\d{3})\.json", name)
+        if match:
+            seq = max(seq, int(match.group(1)))
+    return f"{prefix}{seq + 1:03d}"
+
+
+def _scrub_free_text(decision: dict[str, Any]) -> dict[str, Any]:
+    """Return a copy with every free-text field sanitized + verified.
+
+    Raises:
+        ValueError: If any field still holds sensitive patterns after
+            sanitizing (write must not proceed).
+    """
+    scrubbed = json.loads(json.dumps(decision))  # Deep copy via round-trip.
+    quote = scrubbed.setdefault("verbatim_quote", {})
+    extracted = scrubbed.setdefault("extracted_decision", {})
+    targets = [quote.get("original", ""), quote.get("english_translation", ""),
+               extracted.get("summary", ""), extracted.get("rationale", ""),
+               extracted.get("tradeoffs", "")]
+    cleaned = [sanitize_text(t) for t in targets]
+    if not all(verify_clean(t) for t in cleaned):
+        raise ValueError("redaction failed: sensitive patterns remain after sanitize_text")
+    (quote["original"], quote["english_translation"], extracted["summary"],
+     extracted["rationale"], extracted["tradeoffs"]) = cleaned
+    # Alternatives list items are manager-authored too — scrub each.
+    extracted["alternatives"] = [
+        sanitize_text(a) for a in extracted.get("alternatives", [])
+    ]
+    if not all(verify_clean(a) for a in extracted["alternatives"]):
+        raise ValueError("redaction failed in alternatives list")
+    scrubbed["redaction_verified"] = True
+    return scrubbed
+
+
+def _validate_against_schema(decision: dict[str, Any]) -> list[str]:
+    """Structural validation mirroring scripts/validate_decisions.py.
+
+    Kept import-light (no jsonschema dep): required fields, id shape,
+    ISO timestamp, non-empty verbatim quote, known category, and the
+    redaction_verified flag. Returns violation strings (empty = valid).
+    """
+    issues: list[str] = []
+    for field in ("decision_id", "timestamp", "project_name", "verbatim_quote",
+                  "extracted_decision", "redaction_verified"):
+        if field not in decision:
+            issues.append(f"missing required field: {field}")
+    if issues:
+        return issues
+    if not re.fullmatch(r"DEC-\d{8}-\d{3}", str(decision["decision_id"])):
+        issues.append(f"bad decision_id: {decision['decision_id']!r}")
+    try:
+        datetime.fromisoformat(str(decision["timestamp"]).replace("Z", "+00:00"))
+    except ValueError:
+        issues.append(f"bad timestamp: {decision['timestamp']!r}")
+    quote = decision["verbatim_quote"]
+    if not isinstance(quote, dict) or not all(
+        isinstance(quote.get(k), str) and quote[k].strip()
+        for k in ("original", "english_translation")
+    ):
+        issues.append("verbatim_quote.original/english_translation must be non-empty strings")
+    extracted = decision["extracted_decision"]
+    valid_categories = {"architecture", "process", "scope", "quality-gate",
+                        "tooling", "release", "other"}
+    if not isinstance(extracted, dict) or extracted.get("category") not in valid_categories:
+        issues.append(f"bad category: {extracted.get('category') if isinstance(extracted, dict) else extracted!r}")
+    if decision["redaction_verified"] is not True:
+        issues.append("redaction_verified must be true")
+    return issues
+
+
+def _index_path(repo: Path) -> Path:
+    """Markdown index listing every stored decision (regenerated on write)."""
+    return repo / "decisions" / "INDEX.md"
+
+
+def _rewrite_index(repo: Path) -> int:
+    """Regenerate INDEX.md from all stored records; return record count."""
+    rows = []
+    for path in sorted((repo / "decisions").rglob("DEC-*.json")):
+        try:
+            record = json.loads(path.read_text(encoding="utf-8"))
+        except (OSError, ValueError):
+            continue
+        extracted = record.get("extracted_decision", {})
+        rows.append(
+            f"| {record.get('decision_id')} | {extracted.get('category', '?')} | "
+            f"{extracted.get('summary', '')[:100]} | `{path.relative_to(repo).as_posix()}` |"
+        )
+    _index_path(repo).write_text(
+        "# Manager Decisions Index\n\n"
+        "> Auto-generated on every `record_manager_decision` call. Do not edit directly.\n\n"
+        "| ID | Category | Summary | Path |\n|---|---|---|---|\n"
+        + "\n".join(rows) + "\n",
+        encoding="utf-8",
+    )
+    return len(rows)
+
+
+@mcp.tool()
+def extract_session_decisions(
+    task_id: int, transcript_path: Optional[str] = None
+) -> list[dict[str, Any]]:
+    """Extract manager trade-offs/rulings from a session transcript.
+
+    Reads `transcript.jsonl` from `tasks/.sessions/{task_id}/` (or the given
+    path) and prompts the light LLM (PERSONA_MODEL) to isolate manager
+    decisions as structured objects. Raw output is returned UNSCRUBBED and
+    UNVALIDATED — callers must pass candidates through
+    `record_manager_decision` (which redacts + validates) before persistence.
+
+    Args:
+        task_id: Session scope (`tasks/.sessions/{task_id}/transcript.jsonl`).
+        transcript_path: Explicit transcript override (tests / replays).
+
+    Returns:
+        List of candidate decision dicts (may be empty when the session
+        holds no manager rulings). Never raises on missing transcripts —
+        returns [] so the pipeline degrades gracefully.
+    """
+    path = Path(transcript_path) if transcript_path else (
+        Path.cwd() / "tasks" / ".sessions" / str(int(task_id)) / "transcript.jsonl"
+    )
+    if not path.is_file():
+        return []  # Graceful path needs no LLM: check BEFORE the lazy import.
+    import litellm  # Lazy: import stays side-effect free.
+    turns: list[str] = []
+    with open(path, encoding="utf-8") as fh:
+        for line in fh:
+            line = line.strip()
+            if not line:
+                continue
+            try:
+                record = json.loads(line)
+            except json.JSONDecodeError:
+                continue
+            turns.append(f"[{record.get('role', '?')}] {record.get('content', '')}")
+    if not turns:
+        return []
+    prompt = (
+        "Extract the MANAGER's decisions, trade-offs, and rulings from this session "
+        "transcript. Preserve each ruling's verbatim quote. Reply with a JSON array; "
+        "each item: {verbatim_quote: {original, english_translation}, "
+        "extracted_decision: {summary, category, rationale, alternatives[], tradeoffs}}. "
+        "Use categories: architecture/process/scope/quality-gate/tooling/release/other. "
+        "Empty array when the session holds no manager rulings.\n\n" + "\n".join(turns)
+    )
+    response = litellm.completion(
+        model=os.environ.get("PERSONA_MODEL", "openrouter/google/gemini-3.8-flash"),
+        messages=[{"role": "user", "content": prompt}],
+        temperature=0.2,
+        drop_params=True,
+    )
+    text = str(response.choices[0].message.content or "").strip()
+    # Tolerate code-fenced replies from the model.
+    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
+    if fenced:
+        text = fenced.group(1).strip()
+    try:
+        candidates = json.loads(text)
+    except json.JSONDecodeError:
+        return []
+    return candidates if isinstance(candidates, list) else []
+
+
+@mcp.tool()
+def record_manager_decision(decision: dict[str, Any]) -> str:
+    """Redact, validate, and persist one manager decision; return its id.
+
+    Pipeline: `sanitize_text` every free-text field → `verify_clean` gate →
+    schema validation → write `decisions/YYYY/MM/DEC-*.json` + matching `.md`
+    (verbatim quote + summary for humans) → regenerate `INDEX.md`.
+
+    Args:
+        decision: Candidate object (verbatim_quote + extracted_decision;
+            decision_id/timestamp assigned here when absent).
+
+    Returns:
+        Human-readable confirmation including the decision id and paths.
+
+    Raises:
+        ValueError: On redaction failure or schema violations — nothing is
+            written in that case (append-only store stays clean).
+    """
+    repo = _repo_root()
+    scrubbed = _scrub_free_text(decision)
+    scrubbed.setdefault("decision_id", _next_decision_id(repo))
+    scrubbed.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
+    problems = _validate_against_schema(scrubbed)
+    if problems:
+        raise ValueError(f"decision schema violations: {'; '.join(problems)}")
+    date_part = scrubbed["decision_id"][4:12]  # YYYYMMDD from DEC-YYYYMMDD-NNN.
+    day_dir = repo / "decisions" / date_part[:4] / date_part[4:6]
+    day_dir.mkdir(parents=True, exist_ok=True)
+    json_path = day_dir / f"{scrubbed['decision_id']}.json"
+    json_path.write_text(json.dumps(scrubbed, ensure_ascii=False, indent=2) + "\n",
+                         encoding="utf-8")
+    quote = scrubbed["verbatim_quote"]
+    extracted = scrubbed["extracted_decision"]
+    md_path = day_dir / f"{scrubbed['decision_id']}.md"
+    md_path.write_text(
+        f"# {scrubbed['decision_id']} — {extracted.get('summary', '')}\n\n"
+        f"- Category: {extracted.get('category')}\n"
+        f"- Session: {scrubbed.get('session_id', '?')}\n"
+        f"- Project: {scrubbed.get('project_name', '?')}\n\n"
+        f"## Verbatim (original)\n\n> {quote.get('original', '')}\n\n"
+        f"## Verbatim (English)\n\n> {quote.get('english_translation', '')}\n\n"
+        f"## Rationale\n\n{extracted.get('rationale', '')}\n",
+        encoding="utf-8",
+    )
+    count = _rewrite_index(repo)
+    return (f"Recorded {scrubbed['decision_id']} "
+            f"(`{json_path.relative_to(repo)}` + `.md`; index now holds {count}).")
+
+
+@mcp.tool()
+def query_manager_decisions(query: str, category: Optional[str] = None) -> str:
+    """Search stored decisions by keyword (+ optional category).
+
+    Case-insensitive substring match over summaries, rationales, trade-offs,
+    and both verbatim-quote languages. Returns formatted summaries with
+    verbatim quotes, or a no-match message (never an error) when empty.
+
+    Args:
+        query: Keyword(s); blank returns everything in the category.
+        category: Optional category filter (see schema enum).
+    """
+    repo = _repo_root()
+    needle = (query or "").strip().lower()
+    hits: list[str] = []
+    for path in sorted((repo / "decisions").rglob("DEC-*.json")):
+        try:
+            record = json.loads(path.read_text(encoding="utf-8"))
+        except (OSError, ValueError):
+            continue
+        extracted = record.get("extracted_decision", {})
+        if category and extracted.get("category") != category:
+            continue
+        quote = record.get("verbatim_quote", {})
+        haystack = " ".join([
+            str(extracted.get("summary", "")), str(extracted.get("rationale", "")),
+            str(extracted.get("tradeoffs", "")), str(quote.get("original", "")),
+            str(quote.get("english_translation", "")),
+        ]).lower()
+        if needle and needle not in haystack:
+            continue
+        hits.append(
+            f"### {record.get('decision_id')} [{extracted.get('category')}] "
+            f"{extracted.get('summary', '')}\n"
+            f"> {quote.get('english_translation', '')}\n"
+            f"Rationale: {extracted.get('rationale', '')}"
+        )
+    if not hits:
+        return f"No manager decisions match query={query!r} category={category!r}."
+    return f"{len(hits)} decision(s) match:\n\n" + "\n\n".join(hits)
+
+
+@mcp.tool()
+def get_manager_profile() -> str:
+    """Return `samples/manager_profile.md` for agent context injection.
+
+    The baseline section is curated; the generated aggregate (if any) comes
+    from reviewed compilations only — this tool never synthesizes guidance.
+    Returns an explanatory message (not an error) when the sample is absent.
+    """
+    profile = _repo_root() / "samples" / "manager_profile.md"
+    if not profile.is_file():
+        return "No manager profile sample exists yet."
+    return profile.read_text(encoding="utf-8")
+
+
+@mcp.tool()
+def propose_profile_evolution() -> dict[str, Any]:
+    """Draft a profile update for MANAGER approval (review gate enforced).
+
+    Executes `scripts/compile_profile.py` in a subprocess and returns the
+    draft as a staged diff-like payload. NOTHING is written to the sample:
+    the manager must approve the draft before any identity update lands.
+
+    Returns:
+        Dict with `status` (`"DRAFT_READY"` / `"EMPTY"` / `"ERROR"`) and the
+        `draft` text (or reason). Never raises — failures arrive as ERROR.
+    """
+    repo = _repo_root()
+    script = repo / "scripts" / "compile_profile.py"
+    if not script.is_file():
+        return {"status": "ERROR", "draft": f"compile script missing: {script}"}
+    try:
+        completed = subprocess.run(
+            [sys.executable, str(script), "--repo", str(repo)],
+            capture_output=True, text=True, timeout=120,
+        )
+    except (OSError, subprocess.SubprocessError) as exc:
+        return {"status": "ERROR", "draft": f"compile failed: {exc}"}
+    if completed.returncode != 0:
+        return {"status": "ERROR", "draft": completed.stderr.strip() or "unknown error"}
+    draft = completed.stdout.strip()
+    if not draft or draft.startswith("No decisions found"):
+        return {"status": "EMPTY", "draft": draft or "No decisions found."}
+    return {"status": "DRAFT_READY", "draft": draft}
+
+
+if __name__ == "__main__":
+    mcp.run(transport="stdio")
diff --git a/opencode.json b/opencode.json
index d6a0575..c3443e9 100644
--- a/opencode.json
+++ b/opencode.json
@@ -30,6 +30,12 @@
       "command": ["uv", "run", "mcp-persona-server/server.py"],
       "enabled": true,
       "timeout": 120000
+    },
+    "manager_decisions": {
+      "type": "local",
+      "command": ["uv", "run", "mcp-decision-server/server.py"],
+      "enabled": true,
+      "timeout": 120000
     }
   },
   "permission": {
@@ -53,6 +59,11 @@
     "get_session_summary": "allow",
     "escalate_to_admin": "allow",
     "request_admin_approval": "allow",
+    "extract_session_decisions": "allow",
+    "record_manager_decision": "allow",
+    "query_manager_decisions": "allow",
+    "get_manager_profile": "allow",
+    "propose_profile_evolution": "allow",
     "external_directory": {
       "*": "ask",
       "/tmp/**": "allow"
diff --git a/packages/cognitive-lead-decisions/samples/manager_profile.md b/packages/cognitive-lead-decisions/samples/manager_profile.md
new file mode 100644
index 0000000..b3867d7
--- /dev/null
+++ b/packages/cognitive-lead-decisions/samples/manager_profile.md
@@ -0,0 +1,35 @@
+# Manager Profile (baseline sample — Task 168)
+
+> Living sample of the manager's judgment, aggregated from the decision repo
+> by `scripts/compile_profile.py`. NEVER hand-edit the generated sections;
+> propose changes via `propose_profile_evolution` and pass the human review
+> gate. Only this hand-written baseline section is curated directly.
+
+## Baseline behavioral guidelines
+
+- Decide in the open: state the rationale and the rejected alternatives, not just the verdict.
+- Prefer reversible decisions; mark irreversible ones explicitly and slow down for them.
+- Keep the audit trail: every ruling links to its verbatim quote and session.
+- Gate anything that learns or publishes (samples, releases, identity updates) on explicit human approval.
+- When ambiguous, ask a pointed question once — then decide and record.
+
+## Architectural preferences
+
+- **Composition over Inheritance** — flat, small modules wired explicitly.
+- **FastMCP stdio servers over background daemons** — on-demand tools beat supervised processes (see Task 167: loop-engine retired for persona commands).
+- **Append-only records** — transcripts, decisions, sessions; history is never rewritten.
+- **Stdlib first** — no new dependency without a stdlib-shaped reason.
+- **Deterministic, testable cores** — pure functions with stubbed transports; network only at the edges.
+
+## Decision heuristics
+
+1. **Hard gates stay hard.** Approval, QA, and closure gates never auto-continue on timeout or transport failure.
+2. **Precision over recall in classification.** A misrouted report is worse than an unanswered question — prefer the REPORT lane on doubt.
+3. **Scope everything shared.** Callback data, sessions, and approvals carry their owner id; foreign input is skipped, never applied.
+4. **Discard stale state at gate entry.** A previous session's button press must never resolve the current gate.
+5. **Dedupe lineage.** Each instruction reaches the model exactly once; replay is memory, not re-asking.
+6. **Fail to a message, never to silence.** Degraded transports return explanatory errors the loop can act on.
+
+## Generated aggregate (DO NOT EDIT — via compile_profile.py)
+
+_No compiled decisions yet. Run `scripts/compile_profile.py` after the first recorded decisions._
diff --git a/packages/cognitive-lead-decisions/schema/decision.schema.json b/packages/cognitive-lead-decisions/schema/decision.schema.json
new file mode 100644
index 0000000..4318af0
--- /dev/null
+++ b/packages/cognitive-lead-decisions/schema/decision.schema.json
@@ -0,0 +1,96 @@
+{
+  "$schema": "http://json-schema.org/draft-07/schema#",
+  "$id": "https://cognitive-lead-hq/packages/cognitive-lead-decisions/schema/decision.schema.json",
+  "title": "ManagerDecision",
+  "description": "Append-only record of one manager decision extracted from a session (Task 168). Raw manager statements are preserved verbatim; redaction runs before persistence and redaction_verified attests the stored text is clean.",
+  "type": "object",
+  "required": [
+    "decision_id",
+    "timestamp",
+    "project_name",
+    "verbatim_quote",
+    "extracted_decision",
+    "redaction_verified"
+  ],
+  "properties": {
+    "decision_id": {
+      "type": "string",
+      "pattern": "^DEC-[0-9]{8}-[0-9]{3}$",
+      "description": "Stable id, e.g. DEC-20260908-001. Date part is the record date, sequence is zero-padded per day."
+    },
+    "timestamp": {
+      "type": "string",
+      "format": "date-time",
+      "description": "ISO-8601 UTC timestamp of when the decision was recorded."
+    },
+    "project_name": {
+      "type": "string",
+      "minLength": 1,
+      "description": "Project the decision belongs to (e.g. cognitive-lead-hq)."
+    },
+    "session_id": {
+      "type": "string",
+      "description": "Owning session/task linkage, e.g. task id '167' or transcript path."
+    },
+    "verbatim_quote": {
+      "type": "object",
+      "description": "Original manager statements, NEVER summarized away.",
+      "required": ["original", "english_translation"],
+      "properties": {
+        "original": {
+          "type": "string",
+          "minLength": 1,
+          "description": "Verbatim manager statement in its source language."
+        },
+        "english_translation": {
+          "type": "string",
+          "minLength": 1,
+          "description": "Faithful English translation of the original."
+        }
+      },
+      "additionalProperties": false
+    },
+    "extracted_decision": {
+      "type": "object",
+      "required": ["summary", "category", "rationale"],
+      "properties": {
+        "summary": {
+          "type": "string",
+          "minLength": 1,
+          "description": "One-paragraph distilled decision."
+        },
+        "category": {
+          "type": "string",
+          "enum": [
+            "architecture",
+            "process",
+            "scope",
+            "quality-gate",
+            "tooling",
+            "release",
+            "other"
+          ]
+        },
+        "rationale": {
+          "type": "string",
+          "description": "Why the manager decided this way (as stated or inferred, marked as such)."
+        },
+        "alternatives": {
+          "type": "array",
+          "items": {"type": "string"},
+          "description": "Options the manager explicitly considered and rejected."
+        },
+        "tradeoffs": {
+          "type": "string",
+          "description": "Cost/benefit the manager accepted with this decision."
+        }
+      },
+      "additionalProperties": false
+    },
+    "redaction_verified": {
+      "type": "boolean",
+      "description": "True only when verify_clean() passed on every persisted free-text field."
+    }
+  },
+  "additionalProperties": false
+}
diff --git a/packages/cognitive-lead-decisions/scripts/compile_profile.py b/packages/cognitive-lead-decisions/scripts/compile_profile.py
new file mode 100644
index 0000000..b6c3aba
--- /dev/null
+++ b/packages/cognitive-lead-decisions/scripts/compile_profile.py
@@ -0,0 +1,84 @@
+#!/usr/bin/env python3
+"""Aggregate stored decisions into manager-profile drafts (Task 168).
+
+Reads every ``DEC-*.json`` under ``decisions/`` (repo root = this script's
+grandparent, or ``DECISION_REPO_PATH``), groups them by category, and prints
+a profile-draft section to stdout. The draft is a PROPOSAL: a human must
+review and approve it (via the MCP ``propose_profile_evolution`` tool) before
+anything lands in ``samples/manager_profile.md``. This script never writes to
+the sample itself — the review gate is structural, not conventional.
+
+Usage:
+    python scripts/compile_profile.py [--repo PATH] [--since YYYY-MM-DD]
+"""
+
+from __future__ import annotations
+
+import argparse
+import json
+import os
+import sys
+from collections import Counter
+from datetime import datetime, timezone
+from pathlib import Path
+
+REPO_ROOT = Path(os.environ.get("DECISION_REPO_PATH", Path(__file__).resolve().parent.parent))
+
+
+def load_decisions(repo: Path, since: str | None = None) -> list[dict]:
+    """Load all decision records, optionally filtered by record date."""
+    records = []
+    for path in sorted((repo / "decisions").rglob("DEC-*.json")):
+        try:
+            record = json.loads(path.read_text(encoding="utf-8"))
+        except (OSError, json.JSONDecodeError) as exc:
+            print(f"warning: skipping unreadable {path}: {exc}", file=sys.stderr)
+            continue
+        if since and record.get("decision_id", "")[4:12] < since.replace("-", ""):
+            continue
+        records.append(record)
+    return records
+
+
+def compile_draft(records: list[dict]) -> str:
+    """Render a review-ready profile draft from decision records."""
+    categories = Counter(
+        r.get("extracted_decision", {}).get("category", "other") for r in records
+    )
+    lines = [
+        f"## Profile draft — {datetime.now(timezone.utc).date().isoformat()}",
+        f"({len(records)} decisions aggregated; HUMAN REVIEW REQUIRED before merge)",
+        "",
+        "### Category distribution",
+        "",
+    ]
+    for category, count in categories.most_common():
+        lines.append(f"- {category}: {count}")
+    lines += ["", "### Recurring rationales", ""]
+    seen: set[str] = set()
+    for record in records:
+        rationale = record.get("extracted_decision", {}).get("rationale", "").strip()
+        quote = record.get("verbatim_quote", {}).get("english_translation", "").strip()
+        key = (rationale or quote)[:160]
+        if key and key not in seen:
+            seen.add(key)
+            lines.append(f"- [{record.get('decision_id')}] {key}")
+    return "\n".join(lines) + "\n"
+
+
+def main(argv: list[str] | None = None) -> int:
+    """CLI entry: parse args, print draft to stdout, exit 0 (never mutates)."""
+    parser = argparse.ArgumentParser(description="Draft a manager-profile update.")
+    parser.add_argument("--repo", default=str(REPO_ROOT))
+    parser.add_argument("--since", default=None, help="Only decisions on/after YYYY-MM-DD")
+    args = parser.parse_args(argv)
+    records = load_decisions(Path(args.repo), args.since)
+    if not records:
+        print("No decisions found — nothing to draft.")
+        return 0
+    print(compile_draft(records))
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/packages/cognitive-lead-decisions/scripts/validate_decisions.py b/packages/cognitive-lead-decisions/scripts/validate_decisions.py
new file mode 100644
index 0000000..746a32d
--- /dev/null
+++ b/packages/cognitive-lead-decisions/scripts/validate_decisions.py
@@ -0,0 +1,115 @@
+#!/usr/bin/env python3
+"""Validate decision records against the JSON schema (Task 168).
+
+ dependency-free structural validator (the schema uses only `required`,
+`type`, `enum`, `pattern`, `minLength`, `format: date-time`): walks
+``decisions/`` and reports per-file violations. Exits non-zero when any
+record is invalid so CI and the MCP `record_manager_decision` tool can gate
+on it.
+
+Usage:
+    python scripts/validate_decisions.py [--repo PATH] [--strict]
+"""
+
+from __future__ import annotations
+
+import argparse
+import json
+import os
+import re
+import sys
+from datetime import datetime
+from pathlib import Path
+
+REPO_ROOT = Path(os.environ.get("DECISION_REPO_PATH", Path(__file__).resolve().parent.parent))
+SCHEMA_NAME = "decision.schema.json"
+
+CATEGORIES = {
+    "architecture", "process", "scope", "quality-gate", "tooling", "release", "other",
+}
+ID_RE = re.compile(r"^DEC-[0-9]{8}-[0-9]{3}$")
+
+
+def _is_datetime(value: object) -> bool:
+    """Best-effort ISO-8601 check (accepts trailing Z)."""
+    if not isinstance(value, str):
+        return False
+    try:
+        datetime.fromisoformat(value.replace("Z", "+00:00"))
+        return True
+    except ValueError:
+        return False
+
+
+def validate_record(record: dict) -> list[str]:
+    """Return a list of violation strings; empty means valid."""
+    issues: list[str] = []
+    for field in ("decision_id", "timestamp", "project_name", "verbatim_quote",
+                  "extracted_decision", "redaction_verified"):
+        if field not in record:
+            issues.append(f"missing required field: {field}")
+    if issues:
+        return issues  # Structural checks below assume presence.
+    if not isinstance(record["decision_id"], str) or not ID_RE.match(record["decision_id"]):
+        issues.append(f"bad decision_id: {record['decision_id']!r} (want DEC-YYYYMMDD-NNN)")
+    if not _is_datetime(record["timestamp"]):
+        issues.append(f"bad timestamp: {record['timestamp']!r} (want ISO-8601)")
+    if not isinstance(record["project_name"], str) or not record["project_name"].strip():
+        issues.append("project_name must be a non-empty string")
+    quote = record["verbatim_quote"]
+    if not isinstance(quote, dict):
+        issues.append("verbatim_quote must be an object")
+    else:
+        for sub in ("original", "english_translation"):
+            if not isinstance(quote.get(sub), str) or not quote[sub].strip():
+                issues.append(f"verbatim_quote.{sub} must be a non-empty string")
+    decision = record["extracted_decision"]
+    if not isinstance(decision, dict):
+        issues.append("extracted_decision must be an object")
+    else:
+        for sub in ("summary", "category", "rationale"):
+            if sub not in decision:
+                issues.append(f"extracted_decision missing: {sub}")
+        if decision.get("category") not in CATEGORIES:
+            issues.append(f"bad category: {decision.get('category')!r}")
+        if "summary" in decision and (
+            not isinstance(decision["summary"], str) or not decision["summary"].strip()
+        ):
+            issues.append("extracted_decision.summary must be a non-empty string")
+    if record["redaction_verified"] is not True:
+        issues.append("redaction_verified must be true (run sanitize_text first)")
+    return issues
+
+
+def main(argv: list[str] | None = None) -> int:
+    """CLI entry: validate all records; print violations; exit code."""
+    parser = argparse.ArgumentParser(description="Validate decision records.")
+    parser.add_argument("--repo", default=str(REPO_ROOT))
+    parser.add_argument("--strict", action="store_true",
+                        help="Also fail when decisions/ holds no records.")
+    args = parser.parse_args(argv)
+    paths = sorted((Path(args.repo) / "decisions").rglob("DEC-*.json"))
+    if not paths:
+        print("No decision records found.")
+        return 1 if args.strict else 0
+    failures = 0
+    for path in paths:
+        try:
+            record = json.loads(path.read_text(encoding="utf-8"))
+        except (OSError, json.JSONDecodeError) as exc:
+            print(f"FAIL {path}: unreadable ({exc})")
+            failures += 1
+            continue
+        problems = validate_record(record) if isinstance(record, dict) else ["top-level JSON must be an object"]
+        if problems:
+            failures += 1
+            for problem in problems:
+                print(f"FAIL {path}: {problem}")
+        else:
+            print(f"OK {path}")
+    print(f"{len(paths) - failures}/{len(paths)} valid")
+    return 1 if failures else 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/skill-templates/manager-decision/SKILL.md b/skill-templates/manager-decision/SKILL.md
new file mode 100644
index 0000000..c2a9e39
--- /dev/null
+++ b/skill-templates/manager-decision/SKILL.md
@@ -0,0 +1,58 @@
+---
+name: manager-decision
+description: Capture per-session manager decisions into a separate learning repo. Extract rulings, redact secrets, consult past decisions, and evolve the manager-AI sample behind a human review gate.
+---
+
+# Manager-Decision Skill
+
+## Purpose
+
+Turns each session's manager judgment into training data. Whenever the manager makes a trade-off, ruling, or system-design call, this skill extracts it (verbatim quote + structured decision), redacts secrets, and persists it append-only in the decision repo (`packages/cognitive-lead-decisions/`, or any checkout pointed to by `DECISION_REPO_PATH`). Aggregated decisions evolve `samples/manager_profile.md` — the manager-AI sample — one reviewed promotion at a time, until micro-decisions no longer need the real manager.
+
+## When to Invoke (Trigger)
+
+- The manager states a preference, ruling, or architectural call in session ("use X over Y because…", "approved with…", "never do Z").
+- A session closes with trade-offs worth preserving (scope cuts, quality-gate verdicts, release calls).
+- An agent faces an architectural ambiguity the manager has ruled on before (consult first via `query_manager_decisions`).
+- The sample looks stale: new decisions exist that the profile does not reflect (propose evolution).
+
+Primary interface: the `manager_decisions` MCP server (5 tools). This skill is the universal wrapper so agents in ANY project invoke decision capture the same way.
+
+## Extraction Workflow
+
+1. **Source:** `extract_session_decisions(task_id)` reads `tasks/.sessions/{task_id}/transcript.jsonl` and returns candidate objects (verbatim quote + summary/category/rationale/alternatives/tradeoffs). Candidates are UNSCRUBBED — never persist them directly.
+2. **Redact:** `record_manager_decision(decision)` runs `sanitize_text` on every free-text field and blocks the write when `verify_clean` fails. Required: API keys (`sk-…`, `ghp_…`, `AIzaSy…`), Bearer tokens, private IPs (`10/8`, `172.16/12`, `192.168/16`), credential assignments.
+3. **Persist:** valid records land as `decisions/YYYY/MM/DEC-YYYYMMDD-NNN.json` + matching `.md`, and `decisions/INDEX.md` regenerates. The store is append-only — corrections are new records, never edits.
+4. **Verbatim preservation:** the manager's original statement AND its English translation are stored word-for-word alongside the extracted summary. Summarizing away the source is forbidden.
+
+## Consultation Workflow
+
+- Before re-asking the manager, call `query_manager_decisions(query, category?)`. A hit (summary + verbatim quote + rationale) resolves the ambiguity without bothering the human.
+- Inject `get_manager_profile()` output into agent reasoning when resolving architectural ambiguities (see cognitive-executor Context Bootstrapping).
+
+## Sample-Evolution Loop (Review Gate Mandatory)
+
+1. `propose_profile_evolution()` runs `scripts/compile_profile.py` and returns a `DRAFT_READY` draft (category distribution + recurring rationales). It NEVER writes to the sample.
+2. Present the draft to the manager; on `APPROVED`, merge the reviewed text into `samples/manager_profile.md` baseline-adjacent generated section.
+3. On `REJECTED`, record the rejection rationale as a decision (category `process`) so the next draft learns from it.
+4. Identity updates without approval are forbidden — auto-promotion does not exist by design.
+
+## Redaction Rules (Summary)
+
+- Scrub before store, verify before write, attest via `redaction_verified: true`.
+- Private IPs, provider keys, bearer tokens, and `password|secret|api_key = …` assignments are always redacted.
+- A failed verification blocks persistence with a `ValueError` — surface it, do not bypass it.
+
+## Invocation Example (per session)
+
+```
+# After the manager rules on the QA gate in session for task 167:
+/manager-decision extract  →  extract_session_decisions(task_id=167)
+                          →  record_manager_decision({...verbatim + category: "quality-gate"...})
+                          →  "Recorded DEC-20260908-001"
+
+# Weeks later, same ambiguity recurs:
+query_manager_decisions("QA gate retry policy", category="quality-gate")
+→  "### DEC-20260908-001 [quality-gate] … > <verbatim quote>"
+→  decide without paging the manager.
+```
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
new file mode 100644
index 0000000..c127bd8
--- /dev/null
+++ b/tests/test_decision_server.py
@@ -0,0 +1,243 @@
+"""Unit tests for mcp-decision-server (Task 168).
+
+Covers:
+- `redactor.sanitize_text` / `verify_clean`: provider keys, bearer tokens,
+  private IPs, credential assignments, idempotency, clean-text passthrough.
+- Schema validation: valid record accepted, violations rejected.
+- `record_manager_decision`: JSON + Markdown creation, daily sequencing,
+  INDEX regeneration, schema-gate rejection — all inside a tmp decision
+  repo via `DECISION_REPO_PATH` (never touches the real package).
+- `query_manager_decisions`: keyword, category filter, no-match message.
+- `get_manager_profile` / `propose_profile_evolution`: missing/empty/draft.
+- `extract_session_decisions`: missing transcript → [], stubbed-LLM parse.
+
+Run: `pytest tests/test_decision_server.py -v` (repo root).
+"""
+
+import importlib
+import json
+import shutil
+import sys
+import types
+from pathlib import Path
+
+import pytest
+
+DECISION_DIR = Path(__file__).parent.parent / "mcp-decision-server"
+REAL_SCRIPTS = (
+    Path(__file__).parent.parent
+    / "packages" / "cognitive-lead-decisions" / "scripts"
+)
+sys.path.insert(0, str(DECISION_DIR))
+
+
+def _load(name, filename):
+    spec = importlib.util.spec_from_file_location(name, DECISION_DIR / filename)
+    mod = importlib.util.module_from_spec(spec)
+    sys.modules[name] = mod
+    spec.loader.exec_module(mod)
+    return mod
+
+
+@pytest.fixture(scope="module")
+def red():
+    return _load("decision_redactor", "redactor.py")
+
+
+@pytest.fixture(scope="module")
+def srv():
+    sys.modules["redactor"] = _load("decision_redactor", "redactor.py")
+    return _load("decision_server", "server.py")
+
+
+@pytest.fixture()
+def repo(tmp_path, monkeypatch):
+    """Isolated decision repo (decisions/ + scripts/) per test."""
+    monkeypatch.setenv("DECISION_REPO_PATH", str(tmp_path))
+    (tmp_path / "decisions").mkdir()
+    shutil.copytree(REAL_SCRIPTS, tmp_path / "scripts")
+    return tmp_path
+
+
+def _candidate(**overrides):
+    base = {
+        "project_name": "cognitive-lead-hq",
+        "session_id": "168",
+        "verbatim_quote": {
+            "original": "از composition استفاده کن",
+            "english_translation": "Use composition over inheritance",
+        },
+        "extracted_decision": {
+            "summary": "Prefer composition over inheritance",
+            "category": "architecture",
+            "rationale": "Manager stated it as a standing rule",
+            "alternatives": ["deep inheritance hierarchies"],
+            "tradeoffs": "Slightly more wiring code",
+        },
+    }
+    base.update(overrides)
+    return base
+
+
+# --- redactor ---------------------------------------------------------------
+
+def test_sanitize_api_keys(red):
+    dirty = "key=sk-proj-abc123XYZ456 and ghp_0123456789abcdef plus AIzaSyB1234567890abcd"
+    clean = red.sanitize_text(dirty)
+    assert "sk-proj-abc123XYZ456" not in clean
+    assert "ghp_0123456789abcdef" not in clean
+    assert "AIzaSyB1234567890abcd" not in clean
+    assert red.verify_clean(clean) is True
+
+
+def test_sanitize_bearer_and_ips(red):
+    dirty = "Authorization: Bearer abcdef123456 sent from 10.0.3.7 via 192.168.1.1"
+    clean = red.sanitize_text(dirty)
+    assert "abcdef123456" not in clean
+    assert "10.0.3.7" not in clean and "192.168.1.1" not in clean
+    assert red.verify_clean(clean) is True
+
+
+def test_sanitize_credential_assignment(red):
+    dirty = 'config has password = "s3cr3t-hunter2" inside'
+    clean = red.sanitize_text(dirty)
+    assert "s3cr3t-hunter2" not in clean
+    assert red.verify_clean(clean) is True
+
+
+def test_verify_detects_raw_secrets(red):
+    assert red.verify_clean("token sk-live-ABCDEF123456") is False
+    assert red.verify_clean("server at 172.20.0.5") is False
+    assert red.verify_clean("password=hunter2") is False
+
+
+def test_sanitize_clean_text_passthrough_and_idempotent(red):
+    text = "Prefer composition over inheritance for testability."
+    assert red.sanitize_text(text) == text
+    assert red.verify_clean(text) is True
+    once = red.sanitize_text("key sk-proj-abc123XYZ456 here")
+    assert red.sanitize_text(once) == once  # Fixed point: markers never re-match.
+    assert red.verify_clean(once) is True
+
+
+# --- record / validate ---------------------------------------------------------
+
+def test_record_creates_json_md_and_index(srv, repo):
+    result = srv.record_manager_decision.fn(_candidate()) \
+        if hasattr(srv.record_manager_decision, "fn") else srv.record_manager_decision(_candidate())
+    assert "Recorded DEC-" in result
+    day_files = sorted((repo / "decisions").rglob("DEC-*.json"))
+    assert len(day_files) == 1
+    record = json.loads(day_files[0].read_text(encoding="utf-8"))
+    assert record["redaction_verified"] is True
+    assert record["verbatim_quote"]["original"] == "از composition استفاده کن"
+    assert day_files[0].with_suffix(".md").is_file()
+    index = (repo / "decisions" / "INDEX.md").read_text(encoding="utf-8")
+    assert record["decision_id"] in index
+
+
+def test_record_daily_sequence_increments(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    first = target(_candidate())
+    second = target(_candidate())
+    id1 = first.split("Recorded ")[1].split(" ")[0]
+    id2 = second.split("Recorded ")[1].split(" ")[0]
+    assert id1 != id2 and id1[:-3] == id2[:-3]  # Same day, next sequence.
+    assert int(id2[-3:]) == int(id1[-3:]) + 1
+
+
+def test_record_rejects_schema_violations(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    bad = _candidate()
+    bad["extracted_decision"]["category"] = "not-a-category"
+    with pytest.raises(ValueError, match="schema violations"):
+        target(bad)
+    assert list((repo / "decisions").rglob("DEC-*.json")) == []  # Nothing written.
+
+
+def test_record_scrubs_secrets_before_write(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    sneaky = _candidate()
+    sneaky["extracted_decision"]["rationale"] = "approved, key sk-proj-SECRET1234567890 ok"
+    target(sneaky)
+    stored = json.loads(next((repo / "decisions").rglob("DEC-*.json")).read_text(encoding="utf-8"))
+    assert "SECRET1234567890" not in json.dumps(stored)
+    assert stored["redaction_verified"] is True
+
+
+# --- query / profile / propose ---------------------------------------------------
+
+def _record(call, cand):
+    target = call.fn if hasattr(call, "fn") else call
+    return target(cand)
+
+
+def test_query_keyword_and_category(srv, repo):
+    _record(srv.record_manager_decision, _candidate())
+    other = _candidate()
+    other["extracted_decision"] = {
+        "summary": "QA gate needs two reviewers",
+        "category": "quality-gate",
+        "rationale": "Manager ruling after flaky release",
+        "alternatives": [],
+        "tradeoffs": "Slower merges",
+    }
+    _record(srv.record_manager_decision, other)
+    call = srv.query_manager_decisions
+    target = call.fn if hasattr(call, "fn") else call
+    assert "composition" in target("composition").lower()
+    assert "quality-gate" in target("", category="quality-gate")
+    assert "No manager decisions match" in target("zzz-no-such-thing")
+
+
+def test_get_manager_profile_missing_and_present(srv, repo, monkeypatch):
+    call = srv.get_manager_profile
+    target = call.fn if hasattr(call, "fn") else call
+    assert "No manager profile" in target()
+    samples = repo / "samples"
+    samples.mkdir()
+    (samples / "manager_profile.md").write_text("# Manager Profile\nBaseline.", encoding="utf-8")
+    assert "Baseline" in target()
+
+
+def test_propose_profile_empty_then_draft(srv, repo):
+    call = srv.propose_profile_evolution
+    target = call.fn if hasattr(call, "fn") else call
+    assert target()["status"] == "EMPTY"
+    _record(srv.record_manager_decision, _candidate())
+    ready = target()
+    assert ready["status"] == "DRAFT_READY"
+    assert "Category distribution" in ready["draft"]
+
+
+# --- extract (stubbed LLM) ---------------------------------------------------------
+
+def test_extract_missing_transcript_returns_empty(srv, tmp_path):
+    call = srv.extract_session_decisions
+    target = call.fn if hasattr(call, "fn") else call
+    assert target(424242, transcript_path=str(tmp_path / "nope.jsonl")) == []
+
+
+def test_extract_parses_stubbed_llm_json(srv, tmp_path, monkeypatch):
+    transcript = tmp_path / "transcript.jsonl"
+    transcript.write_text(
+        json.dumps({"role": "user", "content": "use composition", "name": "m",
+                    "timestamp": "2026-09-08T00:00:00+00:00"}) + "\n",
+        encoding="utf-8",
+    )
+    candidates = [{
+        "verbatim_quote": {"original": "x", "english_translation": "y"},
+        "extracted_decision": {"summary": "s", "category": "architecture",
+                               "rationale": "r", "alternatives": [], "tradeoffs": "t"},
+    }]
+    message = types.SimpleNamespace(content=json.dumps(candidates))
+    stub = types.ModuleType("litellm")
+    stub.completion = lambda **kwargs: types.SimpleNamespace(
+        choices=[types.SimpleNamespace(message=message)])
+    monkeypatch.setitem(sys.modules, "litellm", stub)
+    call = srv.extract_session_decisions
+    target = call.fn if hasattr(call, "fn") else call
+    assert target(1, transcript_path=str(transcript)) == candidates
```
<!-- END_GIT_DIFF -->
