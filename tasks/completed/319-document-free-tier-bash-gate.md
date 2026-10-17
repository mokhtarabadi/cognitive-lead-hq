# Task 319: Document free-tier bash gate in custom agents

**File:** `tasks/qa/319-document-free-tier-bash-gate.md`
**Source:** manager
**Type:** docs
**Status:** open

## Goal

Document the upstream free-tier bash gate and guard custom agents against tool-restricted 403s.

## Manager's Notes

Goal accepted: "full implmment this issue https://github.com/mokhtarabadi/cognitive-lead-hq/issues/30 using our skills and brain full auto mode." Issue 30: upstream free-tier gating is triggered by request body tool list, not headers. Any agent omitting `bash` is classified as not from within OpenCode. Suggested actions: (1) document never ship custom agent without bash for free-tier models, (2) review checklist free-tier smoke test, (3) DECISIONS.md entry with upstream links.

## Local TODOs

- [x] Gather context (agents, opencode.json, docs)
- [x] Brain plan with Seat Check
- [x] Implement docs guard
- [x] Verify (lint, grep)
- [x] Stage and move to qa

## Acceptance Criteria

- [x] Agent docs state bash requirement for free-tier models
- [x] Review checklist includes free-tier smoke test
- [x] DECISIONS.md entry records upstream behavior with links
- [x] `lint_task_file` passes

## Verification Evidence

- **Test command:** docs-only, no suite — `lint_task_file` plus grep gates; tooling gate skip: root ., markers [package.json, requirements.txt, go.mod, Cargo.toml, pom.xml], matched none, reason no stack marker found
- **Expected result:** lint passes, greps match, no task-number leak
- **Actual result:**
  - `grep -n Free-tier bash gate agents/README.md` → line 18 match, exit 0
  - `grep -n Free-tier smoke test agents/README.md` → line 23 match, exit 0
  - `grep -n Free-tier bash gate documented agents/DECISIONS.md` → line 10 match, exit 0
  - `grep -c anomalyco/opencode agents/DECISIONS.md` → 6, exit 0
  - `grep -rn 5425 agents/README.md agents/DECISIONS.md` → empty, exit 1 handled (no leak)
  - `lint_task_file` → pending (summary phase)
- **Exit code:** 0 (greps)

## Code-guard extension (same task, autopilot)

- Upstream context round: all six upstream issues fetched via gh (50627 OPEN 14 comments with shell deny-all repro; 54744 triaging — restricted subagent fails even with bash allowed, so bash is necessary but not sufficient; 53347, 53885, 52880, 49592 closed). Brain implementation plan (Programmer, 4 steps) approved by Manager ("Approved", try 1); implementation XML issued bare unfenced, executed from it.
- New `tests/test_agent_tool_gate.py` (stdlib-only frontmatter parse, two tests: free-tier agents assert bash allow with discovery exempt, discovery asserts deny edit plus bash). Repair 1: glob caught slice docs without frontmatter — restricted `_agent_files` to frontmatter-carrying definitions.
- **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_agent_tool_gate.py -q` (raw `pytest` unavailable — no binary in venvs, uv-run path used)
- **Expected result:** 2 passed, exit 0
- **Actual result:** first run 1 failed 1 passed (missing README.md plus DECISIONS.md from glob); after repair 2 passed in 0.02s, exit 0
- **Exit code:** 0
- Prose hygiene: `grep -rn 319` and `grep -rn 5425` on the test file → both empty (echo paths), no number leak; upstream numbers live only as URL refs.
- Tooling gate: docs-plus-test change, no stack blueprint applies; skip record — root ., markers [package.json, requirements.txt, go.mod, Cargo.toml, pom.xml], matched none, reason no stack marker found.
- Sibling docs: tests README plus DECISIONS describe suite generically (no per-file list to update); no slice change beyond the new test file itself.

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append

## Risk & Rollback

- **Risk:** Future agent profile drops bash and hits misleading 403 on free-tier models.
- **Rollback plan:** Revert the two agents docs hunks via `git checkout --` on those paths only.

## Execution Log & Reasoning

Autopilot locked for issue 30 implementation.
Seat Check: agent docs plus permission guard → Software Architect requested; Designer, Programmer (planning), Planner, Strategist, QA, Reviewer skipped with single-domain docs reason. Trigger map explicit miss, no UI/schema/perf hits. Brainstorm: not required — docs-only reversible single-domain change.
Brain plan verdict (Architect, stage plan): 5-step docs-guard plan approved by Manager ("Approved", try 1). Selected path: README bash note plus checklist plus DECISIONS entry with six upstream links, no permission changes, ZAC holds.
Assumption A1: issue body quoted in task notes is verbatim from gh issue view. Reason: byte output captured via gh CLI.
Implementation notes: appended bash-gate section plus smoke-test checklist to agents/README.md (no permission edits); appended accepted DECISIONS entry with six upstream refs; CHANGELOG entry under Unreleased Added; sibling agents README plus DECISIONS inspected before edits per Living Folder Docs, no other slice change.
Autopilot pipeline: re-QA not needed (first QA_PASSED, no fix loop). QA verdict: QA_PASSED (no permission drift, conditional free-tier wording, six refs, no number leak). Code Reviewer verdict: technically APPROVED, PO_REVIEW_PENDING (4 strengths, no blocking issues). File stays in tasks/qa/ until the exact closure word. Autopilot never commits or closes.
Task-number correction: file created as 5425 from a bad NEXT_ID scan (grep over full paths caught timestamp fragments); real Kanban max is 318, so renamed via git mv to 319, header updated, lint re-passed, diff re-injected. Brain history continues under the same session thread.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index e3f5abb..d4fe653 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
+- **Free-tier bash gate documented in agent docs.** `agents/README.md` now states custom agents must keep bash in the tool allowlist for free-tier models (upstream classifies by request-body tool list, 403 otherwise) plus a free-tier smoke-test checklist item; `agents/DECISIONS.md` records the accepted decision with six upstream issue refs. No permission changes.
+
+- **Agent tool gate test.** `tests/test_agent_tool_gate.py` asserts free-tier-intended agents keep bash allow (stdlib frontmatter parse, discovery exempt as deny-by-design with restricted-shape caveat); 2 passed via rtk.
+
 - **Mandatory mode line in every `brain_turn` prompt.** The executor now opens each Brain call with `MODE: AUTOMATIC (autopilot locked) — emit bare unfenced XML only; no copy-paste relay instructions` or `MODE: MANUAL — xml-fenced blocks and copy-paste relay instructions expected`, because the Brain's system prompt carries both emission shapes and cannot know which one is live. Without it the Brain fence-strict-rejects in autopilot and keeps emitting admin copy-paste text in a silent pipeline. Documented in `agents/cognitive-executor.md` (Brain Bridge state machine plus autopilot section) and `docs/brain-bridge.md`.
 
 - **AGENTS.md living-docs guardrail (audit-agents).** New Don't/Do rule requires inspecting the sibling `README.md` and `DECISIONS.md` before editing code in any component or vertical slice directory, closing the one gap found by the refreshed auditor skill; `.gitignore` verified compliant, no change.
diff --git a/agents/DECISIONS.md b/agents/DECISIONS.md
index 3b4fa2d..2deed67 100644
--- a/agents/DECISIONS.md
+++ b/agents/DECISIONS.md
@@ -6,3 +6,17 @@
 - **Decision:** Adopting Living Folder Docs standard for this component.
 - **Consequences:** All future structural or contract changes must be recorded here.
 - **Rollback:** N/A (baseline adoption).
+
+## Free-tier bash gate documented
+Date: 2026-10-17
+Status: accepted
+Context: Upstream free-tier models discriminate by request-body tool list. Agents omitting bash receive 403 FreeTierError on free-tier models.
+Decision: Document bash requirement in agent docs. Add free-tier smoke test to the review checklist. Make no permission changes.
+Consequences: Agents intended for free-tier use keep bash. Hardening uses prompts and review, not tool removal.
+Refs:
+- https://github.com/anomalyco/opencode/issues/50627
+- https://github.com/anomalyco/opencode/issues/53347
+- https://github.com/anomalyco/opencode/issues/53885
+- https://github.com/anomalyco/opencode/issues/54744
+- https://github.com/anomalyco/opencode/issues/52880
+- https://github.com/anomalyco/opencode/issues/49592
diff --git a/agents/README.md b/agents/README.md
index 0f7ec47..98b377a 100644
--- a/agents/README.md
+++ b/agents/README.md
@@ -14,3 +14,10 @@ Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary execu
 - Permission drift: executor allows edit/question, discovery denies edit/bash; never invert.
 - Persona changes must stay in sync with `system-prompt.md` fragments and `prompts/` sources.
 - No runtime code here; changes are prompt-contract changes with system-wide effect.
+
+### Free-tier bash gate
+
+Custom agents must keep bash in the tool allowlist when the agent is expected to run on a free-tier model. Upstream free-tier models classify the caller by the request-body tool list. A call without bash is treated as third-party and receives 403 FreeTierError on free-tier models. Keep bash in the list for free-tier use. Harden behavior with scoped prompts and review, not with tool removal.
+
+Review checklist addition:
+- Free-tier smoke test before release: run the agent under review with opencode run using the --agent flag on a free-tier model and confirm a normal reply with no 403. Example with a known agent: opencode run --agent cognitive-executor --prompt smoke test reply OK. Repeat for each agent file found in opencode.json.
diff --git a/tests/test_agent_tool_gate.py b/tests/test_agent_tool_gate.py
new file mode 100644
index 0000000..a41a5d2
--- /dev/null
+++ b/tests/test_agent_tool_gate.py
@@ -0,0 +1,102 @@
+# Sibling Docs: tests/README.md | Decisions: tests/DECISIONS.md
+"""Free-tier bash gate guard.
+
+Custom primary agents must keep bash in the allowlist when free-tier use is intended.
+Upstream free-tier models classify the caller by the request-body tool list; a call
+without bash is treated as outside the host and fails with FreeTierError on free models.
+
+Upstream evidence:
+- https://github.com/anomalyco/opencode/issues/50627 : shell deny-all breaks every free-tier request.
+- https://github.com/anomalyco/opencode/issues/54744 : restricted subagent shape can fail even with bash allowed.
+  Bash presence is necessary but not sufficient for restricted shapes. Docs note only, not a code fix.
+
+Exemption:
+- cognitive-discovery is a read-only subagent that denies edit plus bash by design; it is asserted as deny with reason.
+"""
+
+from pathlib import Path
+import re
+
+AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"
+READ_ONLY_EXEMPT = {"cognitive-discovery.md"}
+
+
+def _read_text(agent_path: Path) -> str:
+    """Read agent markdown as text for frontmatter parsing. Args: agent_path path to agent file. Returns: file text. Assumes UTF-8."""
+    return agent_path.read_text(encoding="utf-8")
+
+
+def _extract_frontmatter(markdown_text: str) -> str:
+    """Extract YAML frontmatter between first two triple-dash markers. Args: markdown_text full file text. Returns: frontmatter text or empty string when markers absent."""
+    # Split on lines to avoid matching body separators.
+    lines = markdown_text.splitlines()
+    # Frontmatter must start at first line.
+    if not lines or lines[0].strip() != "---":
+        return ""
+    # Find closing marker.
+    for idx in range(1, len(lines)):
+        if lines[idx].strip() == "---":
+            return "\n".join(lines[1:idx])
+    return ""
+
+
+def _permission_allows_bash(frontmatter: str) -> bool:
+    """Return True when permission block allows bash. Args: frontmatter extracted frontmatter text. Returns: True for allow, False for missing or deny."""
+    low = frontmatter.lower()
+    # Bash must be mentioned at all.
+    if "bash" not in low:
+        return False
+    # Explicit deny patterns fail closed.
+    if re.search(r"bash\s*:\s*deny", low):
+        return False
+    if re.search(r"bash.*deny\s*-\s*all", low):
+        return False
+    # Direct allow patterns pass.
+    if re.search(r"bash\s*:\s*allow", low):
+        return True
+    if re.search(r'"bash"\s*:\s*"allow', low):
+        return True
+    # Nested shape with bash key plus allow token in permission scope passes.
+    perm = low.split("permission", 1)[-1] if "permission" in low else low
+    return "allow" in perm
+
+
+def _permission_denies(frontmatter: str, tool: str) -> bool:
+    """Return True when permission block denies the named tool. Args: frontmatter extracted text; tool tool name. Returns: True for deny."""
+    low = frontmatter.lower()
+    return bool(re.search(rf"{re.escape(tool)}\s*:\s*deny", low))
+
+
+def _agent_files():
+    """List agent definition files sorted by name. Returns: sorted list of Path objects."""
+    # Only files carrying YAML frontmatter count as agent definitions; slice docs stay out.
+    return sorted(
+        p for p in AGENTS_DIR.glob("*.md") if _extract_frontmatter(_read_text(p)) != ""
+    )
+
+
+def test_free_tier_agents_keep_bash():
+    """Free-tier-intended agents must allow bash; discovery exempt is skipped here."""
+    # Collect failures for one clear assertion message.
+    missing = []
+    # Iterate every agent file to prevent silent additions without the gate.
+    for agent_path in _agent_files():
+        if agent_path.name in READ_ONLY_EXEMPT:
+            continue
+        text = _read_text(agent_path)
+        front = _extract_frontmatter(text)
+        if not _permission_allows_bash(front):
+            missing.append(agent_path.name)
+    assert not missing, f"free-tier-intended agents must allow bash, missing: {missing}"
+
+
+def test_read_only_agent_stays_deny():
+    """Read-only subagent must stay deny for edit plus bash by design."""
+    target = AGENTS_DIR / "cognitive-discovery.md"
+    assert target.exists(), "read-only discovery agent file must exist"
+    text = _read_text(target)
+    front = _extract_frontmatter(text)
+    # Discovery denies edit by design as read-only.
+    assert _permission_denies(front, "edit"), "discovery must deny edit"
+    # Discovery denies bash by design as read-only.
+    assert _permission_denies(front, "bash"), "discovery must deny bash"
```
<!-- END_GIT_DIFF -->
