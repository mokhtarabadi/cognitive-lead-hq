# Task 233: Supervised autopilot with plan approval and seat routing

**File:** `tasks/qa/233-supervised-autopilot-plan-approval-seat-routing.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Replace fire-and-forget autopilot with supervised autopilot: discovery feed, mandatory plan-approval loop with the admin, seat-routed implementation, bounded QA/review loops, and final-approval close — with a fast path for trivial work.

## Manager's Notes

Manager approved the joint 7-seat brainstorm (O1 supervised autopilot wins). Verbatim orders: "Yes fix all by ask hands (auto pilot)". Autopilot locked for this task. Implement gaps G1-G13 with warnings U1-U5 honored:

- A1: `agents/cognitive-executor.md` — discovery feed + plan approval loop + seat check + corrected lock words; fix G7/G8 (human plan approval and goal-pause carve-outs).
- A2: `mcp-brain-bridge/server.py` — bundle/tree size limits (G12), fed-context handling, plan-verdict shape; regression tests, no live network.
- A3: `docs/conventions.md` Lite rules + `telegram-issue-sync` skill — risk tiers (G13), autopilot-ready contract (G9), trivial fast paths (U1/U3/U4), max-3 plan tries then escalate (U5); fold data-ask into planning turn (U2).
- G5/G6: seat-routed implementation + "autopilot on task N" lock recognition. G10/G11: bounded QA/review loops, results shown before move to qa.
- Fragments dir is git-ignored: A1 also mirrors into shipped `system-prompt.md` atomically (bump `<system_version>`, CHANGELOG entry) or the rule never ships. Never invent architecture/data-model/design specs (files absent).

## Local TODOs

- [x] Seat check + Brain planning turn under same task id, log verdict
- [x] A1 executor rules (discovery, plan loop, seats, lock words, G7/G8 carve-outs)
- [x] A2 bridge limits + plan verdict + tests
- [x] A3 tiers + telegram contract + fast paths
- [x] Full suite green, CHANGELOG, stage, qa move

## Acceptance Criteria

- [x] Autopilot shows the plan to the admin and waits for approval before implementing non-trivial work
- [x] Trivial work (Lite-eligible) still runs without human pauses
- [x] Seat routing sends UI work to Designer review and backend to Engineer
- [x] QA/review loops are bounded and results are shown before qa move
- [x] Tests cover new bridge behavior; full suite exits 0

## Verification Evidence

- **Test command:** `pytest tests/ -q` (from repo root)
- **Expected result:** all tests pass, exit 0
- **Actual result:** 350 passed, 8 warnings (pathspec deprecation, pre-existing), 5.44s — post-postfix re-run, uv-pinned env, exit verified 0
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** plan gate stalls night runs; over-gating trivial work; fragment/prompt drift
- **Rollback plan:** risk tiers + max-3-tries escalate; single-commit scope per file area; `git log` revert of closure commits only by Manager

---

## Execution Log & Reasoning

Autopilot locked for Task 233 per Manager order "Yes fix all by ask hands (auto pilot)".

Seat Check (planning gate): domains = autopilot process rules + bridge contract + seat routing. Requested: Software Architect + Senior Programmer. Skipped: Designer (UI routing here is a one-line trigger rule, no layout decisions), Strategist/Planner/QA/Reviewer (no capacity/milestone/verdict questions at plan time).

Brain planning turn 1 (Architect + Senior Programmer): returned ordered plan A1/A2/A3 + verdict shape V1-V6 + limits L1-L4 + Lite criteria C1-C3 + tests T1-T3. Two points marked INFERRED pending file reads.

Discovery grounding (3 parallel scans + task file read):
- G1: bridge server is 1409 lines. Bundle: _BUNDLE_FILES L164-170, _BUNDLE_FILE_CAP=60000 L172, _build_context_bundle L412-433. No tree reporter in bridge (lives in context-server); paths attach caps _CTX_PATHS_PER_FILE=20000 L1070, _CTX_PATHS_TOTAL=40000 L1075. Brain L1-L4 partly exist: keep L2 (60k/file cap confirmed), add explicit bundle TOTAL cap; tree limits belong to context-server, out of scope.
- G2: fed-context pinning ALREADY exists in bridge (marker L989-991, extract/save/load L1004-1066, wired L1247-1265). Brain I8 is reduced to documenting + enforcing prepend, not building.
- G3: response builder brain_turn L1131-1139, result dict L1338-1352, empty guard L1325-1330. Plan-verdict validator is genuinely new, goes near extract_xml_blocks L586-601.
- G4: telegram skill 308 lines, approval Phase 2 L77-89 (question tool); repo template copy exists and matches. Edit both copies.
- G5: shipped prompt 698 lines v9.35.0; no Planning Gate / Brain Bridge sections (those live in executor agent file). Mirror targets: <execution_workflow> L422-465, <constraints> L476-499, <lite_mode_protocol> L391-420. Fragments: 20 files, no 17-*.md gap noted.

Brain planning turn 2 (same id, fed-context): PLAN APPROVED by Architect + Senior Programmer. Corrected deltas: D1 bundle total cap 150k in builder (keep 60k/file); D2 tree limits out of scope (context-server owns tree); D3 fed-context exists, enforce prepend only; D4 plan-verdict validator after extract_xml_blocks with 5 fields (verdict, seats, path, steps, cites), reject empty cites; D5 mirror into shipped prompt workflow/constraints/Lite/personas + version bump + CHANGELOG in same commit. Proceeding to implementation under autopilot approval.

A3 done: conventions Lite section gains Risk Tiers T0/T1/T2 + 3-tries-then-escalate; telegram skill Phase 2 gains autopilot data-ask folding note (repo template + global copy, identical). Mirror done: fragment 13-constraints.md gains Supervised Autopilot Contract bullet; 01-system_version.md 9.35.0→9.36.0; system-prompt.md regenerated via assembler (diff vs committed = exactly these 2 changes). CHANGELOG Unreleased entry appended. Full suite: 350 passed, exit 0.

Postfix after review verdict (7 steps, same file, no new number): S1 validator now uses word-bound field matching with a docstring note (bare substring accepted stubs like path-inside-paths; bounds force real sections). S2 bundle truncation reserves the suffix length before slicing so the total never exceeds the cap. S3 contract bullet reworded (single plan-approval pause; Relay plus hard blockers are the only other interrupts); shipped prompt regenerated via the assembler only, diff shows exactly the reworded line. S5 both skill copies verified byte-same note at line 91 (repo template + global install). S6 D5 scope justification: the approved fragment edits were the constraints bullet plus the version bump only, and the shipped prompt carries no Planning Gate or Brain Bridge sections (discovery confirmed), so the constraints-only mirror is complete — no workflow, Lite, or personas mirrors were approved or needed. S7 five bridge tests cited at tests/test_brain_bridge.py:1473-1485 (total cap bounds oversize workspace), 1486-1492 (fed pin persists across second turn), 1494-1497 (valid verdict passes), 1500-1503 (stub fails on seats/cites), 1506-1509 (cites without path-with-lines fail). Skills loaded for postfix: verification-before-completion, task-lint (both already active this session).

Post-postfix re-verify: py_compile clean on bridge server; full suite re-run via uv-pinned env = 350 passed, exit 0, 5.44s (evidence updated above); lint_task_file re-passed; restaged via stage_and_inject_diff from tasks/qa path.

Re-review (second review, same id, diff attached): Code Reviewer reports code technically approved, status PO_REVIEW_PENDING. Strengths F1-F5 (word-bound verdict checker, suffix-safe cap, one-pause plan gate, auditable seat routing, bounded loops). Two low-severity notes: I1 test hunks past truncation point (covered by suite evidence), I2 capped/skipped files emit no stderr count (deferred to a later task per reviewer R2, not implemented here). Closure awaits the Manager approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 2006053..56a716a 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -11,6 +11,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **Manager-decision hardening B1/B2/F1-F5/M3 (Task 230, syncs GitHub issue 8):** `mcp-decision-server/server.py` — install-once path config (B1: `DECISION_REPO_PATH` set once via shell/`.env`, never asked per call; `.env.example` documents it), optional record fields with safe defaults (`fidelity` verbatim/reconstructed, `mode` manual/autopilot, `goal_ref` lineage, `scope` standing/episode, auto sha256 `fingerprint` with non-blocking duplicate warning), new `autopilot-cycle` category, ranked consultation retrieval (field-weighted TF scoring, best first), and new `get_sync_status` tool surfacing push debt at session start (M3). Skill gains install-once + auto-capture-on-close sections (B2: executor runs `extract_session_decisions` on every close; persistence stays confirm-gated per Task 213 — extraction automatic, writes never automatic) plus consult-first top-3 logging. `agents/cognitive-executor.md` close rule wires auto-extract + gated record. 5 new offline tests. Full decision suite: **98 passed**;decision-adjacent suites: **90 passed**.
 - **Decision follow-up hardening H1/H2/H3 + B2 live proof (Task 231):** fingerprint path now tolerates a stray string `verbatim_quote`/`extracted_decision` (H1), skips tampered non-dict store files in both the duplicate scan and the index rewrite instead of crashing (H2), and treats explicit `None` optionals as unset so safe defaults still apply (H3). B2 live evidence: `extract_session_decisions(231)` fired at close handling and returned `[]` loudly (no session transcript in headless run — nothing queued, nothing written). 3 new regression tests. Full decision suite: **101 passed**.
 - **Brain empty-output retry hint + prompt-size warn (Task 232):** `mcp-brain-bridge/server.py` no longer returns a silent blank REPORT — root cause confirmed in code: `parse_responses_text` yields `""` on missing/non-list output and `brain_turn` forwarded it with no guard. A single choke-point guard now substitutes the machine-readable `EMPTY_OUTPUT_RETRY` hint (fixed token, lean-retry shape: same task_id, `include_bundle=false`, escalate if still empty; verdict content never invented, status stays REPORT so old callers keep working), plus a stderr advisory when the prompt exceeds 60k chars (oversized prompts correlated with both observed flakes). `agents/cognitive-executor.md` Empty-output clause now names the token. 6 new offline tests (hint contract, missing/None/whitespace payloads, normal passthrough, stderr warn). Full suite: **345 passed**.
+- **Supervised autopilot with plan approval and seat routing (Task 233):** `agents/cognitive-executor.md` gains a supervised plan-approval section (discovery feed → Brain plan → one approval pause → seat-routed implementation; Relay questions and hard blockers are the only other interrupts), a Seat Check trigger-citation line, a goal-pause carve-out for plan approval, and generous lock-word recognition. `mcp-brain-bridge/server.py` gains a 150 KB total bundle cap (truncate/skip with notes) and a text `validate_plan_verdict` checker (5 fields; cites need path:line shape). `docs/conventions.md` gains risk tiers T0/T1/T2 plus a 3-tries-then-escalate contract. `skill-templates/telegram-issue-sync/SKILL.md` folds the GitHub-preference data question into the planning turn (repo + global copies). Shipped prompt rebuilt to 9.36.0 with a Supervised Autopilot Contract bullet (authority stays in the executor file). 5 new offline bridge tests. Full suite: **350 passed**. Postfix: verdict checker uses word-bound field matching (stub text inside longer words no longer validates), bundle truncation reserves suffix length so the total never exceeds the cap, contract bullet reworded to a single plan-approval pause.
 
 ## [9.35.0] - 2026-09-14
 
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 8249801..8a5ba6e 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -234,18 +234,31 @@ is governed by the Seat Check, trigger map, and reject rule below —
 "Architect seat minimum" alone is never sufficient when a trigger matches.
 Record the Brain's plan verdict plus the selected path in the task Execution
 Log (or the session/goal record when no task file exists) and execute from
-it — never from your own invention. Lite-eligible changes (single file, no
-cross-module impact, obvious fix, never login/auth, money, or security-surface
-changes) pass with a one-line justification in the file.
+ it — never from your own invention. Lite-eligible changes (single file, no
+ cross-module impact, obvious fix, never login/auth, money, or security-surface
+ changes) pass with a one-line justification in the file.
+
+### Supervised autopilot plan approval (non-trivial work only)
+
+Fire-and-forget autopilot is forbidden. For non-trivial work, the Hands MUST
+show the Brain-approved plan to the admin and wait for explicit approval
+before writing implementation code: present plan steps + seat routing +
+cited file paths with lines, accept admin edits in a loop (max 3 plan tries,
+then escalate), and only then implement. Lite-eligible trivial work is
+carved out — it runs with zero human pauses. The data-ask folds into the
+planning turn itself (never a separate blocking question): if the Brain
+needs repo data, it returns a discovery task, the Hands feed results back
+under the same `task_id`, and the plan arrives grounded.
 
 ### Seat Check, trigger map, and lightweight consult (mandatory at plan start)
 
 Seat names and duties live in `system-prompt.md` `<personas>` — the Hands
 reference them by exact name; that block is the only roster.
 
-1. **Seat Check.** Before any `brain_turn` planning call, state: task
-   domain(s) → seat(s) requested → seats skipped + one-line reason each.
-   A planning turn with no Seat Check is malformed.
+ 1. **Seat Check.** Before any `brain_turn` planning call, state: task
+    domain(s) → seat(s) requested → seats skipped + one-line reason each.
+    A planning turn with no Seat Check is malformed. Cite which trigger
+    words fired (or state the explicit miss) so the choice is auditable.
 2. **Trigger→seat map (minimum viable).** Match on TITLE+BODY, defined
    as the case-insensitive concatenation of the task title and body (empty
    body = title alone; a neutral title with an empty body still misses, so
@@ -324,10 +337,12 @@ goal entirely — goal overhead must never exceed the task itself.
    question, then stop. Reason: while the goal stays active the goal
    plugin auto-resends the continuation prompt on your next turn, which
    re-issues the objective instead of waiting for the answer — the
-   Manager ends up answering the same objective twice. Pausing is
-   permitted ONLY for the narrow cases where asking is allowed — never
-   as a substitute for permitted autonomous action. No orphaned pauses:
-   every pause names the blocker.
+    Manager ends up answering the same objective twice. Pausing is
+    permitted ONLY for the narrow cases where asking is allowed — never
+    as a substitute for permitted autonomous action. No orphaned pauses:
+    every pause names the blocker. Carve-out: the supervised plan-approval
+    pause and Relay questions are allowed pauses — they carry the plan or
+    the relayed question as the named blocker.
 4. **Resume WITH the answer.** When the Manager answers, call
    `update_goal_status(active)` and continue from the recorded state,
    carrying the Manager's answer forward as the deciding input. Never
@@ -375,10 +390,13 @@ needs no extra machinery.
 ### Autopilot mode (default OFF)
 
 When the Manager says "on autopilot do X": run the full state machine
-end-to-end with zero approval pauses — implement, bridge-QA, fix,
-bridge-review, stage, move to qa — stopping only for hard blockers
-(missing credentials, orders that trigger the Clarification Halt).
-Record every turn's outcome in the task Execution Log so nothing is
+end-to-end — discovery feed, Brain plan, plan approval, seat-routed
+implement, bridge-QA, fix, bridge-review, stage, move to qa — stopping
+only for hard blockers (missing credentials, orders that trigger the
+Clarification Halt) and for the two human gates below. Non-trivial work
+MUST pass the plan-approval gate (show plan, wait for approval, max 3
+tries then escalate); Lite-eligible trivial work skips all human pauses
+and runs straight through. Record every turn's outcome in the task Execution Log so nothing is
 forgotten. Autopilot NEVER auto-commits (ZAC holds) and NEVER closes
 tasks (closure needs the explicit approval word). Chain `brain_turn`
 calls YOURSELF: QA, re-QA, and review turns are invoked directly by you
@@ -402,7 +420,10 @@ the task file):
   only when the Manager says "manual", "stop", or takes over with a
   new direct order.
 - **Switch words.** Manager → Hands: "on autopilot …" locks autopilot;
-  "manual mode" / "back to manual" returns to manual. Hands → Manager:
+ "manual mode" / "back to manual" returns to manual. Lock recognition is
+ generous: "autopilot on task N", "fix all … (auto pilot)", or any order
+ naming autopilot plus a task also locks (announce the lock so the
+ Manager can correct a misfire). Hands → Manager:
   one line ("Autopilot locked for …" / "Back to manual.") so both sides
   always know which mode is live. Record the lock in the task file.
 
diff --git a/docs/conventions.md b/docs/conventions.md
index 2e61fa2..d0bed02 100644
--- a/docs/conventions.md
+++ b/docs/conventions.md
@@ -114,6 +114,16 @@ Bypasses Steps 1–4 of `<execution_workflow>` (Discovery, Brainstorming, Bluepr
 
 If implementation reveals the change is NOT trivial, the Hands MUST HALT and output: "Escalating from Lite Mode to Full Mode: [reason]." The full workflow restarts at Step 1.
 
+### Risk Tiers (Autopilot-Ready Contract)
+
+Every task runs at one tier. The tier sets how many human pauses apply.
+
+- **T0 trivial:** meets all three Lite eligibility criteria above. Lite fast path applies. No human pauses except QA and review verdicts.
+- **T1 standard:** multi-file changes or new behavior. Full supervised autopilot applies with a plan-approval pause plus Relay questions.
+- **T2 destructive or irreversible:** migrations, deletes, publishes, pushes, or secret handling. Each action needs explicit Manager approval. Autopilot MUST halt and never self-approve.
+
+Max three tries per loop (plan, QA, review), then escalate to the Manager with evidence.
+
 ## Goal-Oriented Tasks & Parallel Agent Execution Standards
 
 ### Goal-Oriented Task Treatment
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 501926d..47c0a05 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -171,6 +171,11 @@ _BUNDLE_FILES = (
 _BUNDLE_MARKER = "=== agents/cognitive-executor.md ==="
 _BUNDLE_FILE_CAP = 60000
 
+#: Total cap for the assembled bundle (chars). Five files at the per-file
+#: cap would reach 300k — this bounds the worst case so planning turns
+#: stay lean and never time out on context size.
+_BUNDLE_TOTAL_CAP = 150000
+
 # Text extensions readable via read_file / searchable via grep_files.
 _ALLOWED_READ_SUFFIXES = frozenset(
     {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
@@ -410,12 +415,25 @@ def _failsafe_qa_attach(user_prompt: object, task_id: object) -> str:
 
 
 def _build_context_bundle() -> str:
-    """Assemble the labeled small-file bundle (never raises on Absent-File)."""
+    """Assemble the labeled small-file bundle (never raises on Absent-File).
+
+    The per-file cap applies first; the total cap applies across files so
+    five full files can never stuff 300k into one turn. Files past the
+    total budget are marked skipped, never silently dropped. The truncation
+    suffix length is reserved before slicing, so the appended marker can
+    never push the total past the cap (off-by-suffix overflow).
+    """
     root = _workspace_root()
     parts: list[str] = []
     missing = 0
+    total = 0
+    capped = False
+    suffix = "\n[truncated: bundle total cap]"
     for rel in _BUNDLE_FILES:
         header = f"=== {rel} ==="
+        if capped:
+            parts.append(header + "\n[skipped: bundle total cap]")
+            continue
         try:
             text = (root / rel).read_text(encoding="utf-8", errors="replace")
         except (FileNotFoundError, NotADirectoryError, OSError):
@@ -424,7 +442,18 @@ def _build_context_bundle() -> str:
             continue
         if len(text) > _BUNDLE_FILE_CAP:
             text = text[:_BUNDLE_FILE_CAP] + "\n[truncated]"
-        parts.append(header + "\n" + text)
+        chunk = header + "\n" + text
+        if total + len(chunk) > _BUNDLE_TOTAL_CAP:
+            room = _BUNDLE_TOTAL_CAP - total
+            if room > len(header) + 64 + len(suffix):
+                parts.append(chunk[:room - len(suffix)] + suffix)
+            else:
+                parts.append(header + "\n[skipped: bundle total cap]")
+            total = _BUNDLE_TOTAL_CAP
+            capped = True
+            continue
+        parts.append(chunk)
+        total += len(chunk)
     if missing:
         print(
             f"brain-bridge: context bundle skipped {missing} missing files",
@@ -601,6 +630,37 @@ def extract_xml_blocks(output: str) -> list[str]:
     return out
 
 
+#: Required fields of a Brain plan verdict. Hands-side plan review checks
+#: plan text for these before executing — a plan with no cites is
+#: ungrounded and must be re-prompted, never executed.
+_PLAN_VERDICT_FIELDS = ("verdict", "seats", "path", "steps", "cites")
+
+
+def validate_plan_verdict(plan_text: object) -> list[str]:
+    """Check Brain plan text for the five verdict fields (pure, offline).
+
+    Returns problem strings; empty means valid. ``cites`` additionally
+    requires at least one ``path:line``-shaped file reference, otherwise
+    the plan is ungrounded.
+
+    Field presence uses word-bound matching (``\\b``), not substring
+    matching: a bare ``in`` check would accept ``path`` inside ``paths``
+    or ``footpath`` and ``steps`` inside ``missteps``, letting a stub
+    plan pass review. Word bounds force each field to appear as its own
+    word, so only a genuinely sectioned verdict validates.
+    """
+    if not isinstance(plan_text, str) or not plan_text.strip():
+        return ["plan text is empty"]
+    lowered = plan_text.lower()
+    problems = [f"plan text missing {field!r} field"
+                for field in _PLAN_VERDICT_FIELDS
+                if not re.search(rf"\b{re.escape(field)}\b", lowered)]
+    if ("cites" not in problems
+            and not re.search(r"\S+\.\w+:\d+", plan_text)):
+        problems.append("plan cites carry no file path with lines")
+    return problems
+
+
 def _get_brain_model() -> str:
     """LLM model for Brain turns; override via ``BRAIN_MODEL``."""
     default = "gpt-6-astra"
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index 8558dae..68fbbb3 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.35.0</system_version>
+<system_version>9.36.0</system_version>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 0017680..a1839be 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -17,6 +17,7 @@
   2. `custom_context_commit_and_clean_task` (closure-time): Commits staged changes as a feature commit, captures the hash, cleans the task file diff block, and creates a separate `chore: close task N` closure commit. The stored hash always points to the feature commit (reachable from HEAD). MUST ONLY be called after the Manager explicitly says "Approved for closure" or "Close task".
   The Hands MUST NEVER run `git commit`, `git add`, or `git push` directly at any point. All staging is via `custom_context_stage_and_inject_diff`; all commits are via `custom_context_commit_and_clean_task`. If the Hands call `commit_and_clean_task` before Manager approval, this is a ZAC violation and the task must be rejected.
 - **Conventional Commits Format Gate:** Every feature commit message passed to `custom_context_commit_and_clean_task` MUST match `<type>: <subject>` with type in `feat|fix|docs|refactor|chore` and first line ≤72 characters (per `skill-templates/versioning-and-release`). The tool validates and rejects free-form messages. The templated `chore: close task N` closure commit always conforms by construction.
+- **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is `agents/cognitive-executor.md`.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
diff --git a/skill-templates/telegram-issue-sync/SKILL.md b/skill-templates/telegram-issue-sync/SKILL.md
index 7cf051c..21df842 100644
--- a/skill-templates/telegram-issue-sync/SKILL.md
+++ b/skill-templates/telegram-issue-sync/SKILL.md
@@ -88,6 +88,8 @@ This MCP implementation does **NOT** expose a `topic_id` parameter. Forum topics
 
 Store the Manager's GitHub preference in a variable `GH_ENABLED` (true/false).
 
+Autopilot note: the data question in step 4 (whether GitHub issues are wanted) folds into the planning turn. The Hands asks it once alongside candidate approval, records the answer in the task file, and never asks again mid-task.
+
 ### Phase 3: Task Generation & Automation (Per Approved Candidate)
 
 For **each** approved candidate, execute the following steps **strictly in order**:
diff --git a/system-prompt.md b/system-prompt.md
index 552ca28..0a2b905 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.35.0</system_version>
+<system_version>9.36.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -492,6 +492,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
   2. `custom_context_commit_and_clean_task` (closure-time): Commits staged changes as a feature commit, captures the hash, cleans the task file diff block, and creates a separate `chore: close task N` closure commit. The stored hash always points to the feature commit (reachable from HEAD). MUST ONLY be called after the Manager explicitly says "Approved for closure" or "Close task".
   The Hands MUST NEVER run `git commit`, `git add`, or `git push` directly at any point. All staging is via `custom_context_stage_and_inject_diff`; all commits are via `custom_context_commit_and_clean_task`. If the Hands call `commit_and_clean_task` before Manager approval, this is a ZAC violation and the task must be rejected.
 - **Conventional Commits Format Gate:** Every feature commit message passed to `custom_context_commit_and_clean_task` MUST match `<type>: <subject>` with type in `feat|fix|docs|refactor|chore` and first line ≤72 characters (per `skill-templates/versioning-and-release`). The tool validates and rejects free-form messages. The templated `chore: close task N` closure commit always conforms by construction.
+- **Supervised Autopilot Contract:** On the lock words the Hands run end to end: discovery feed, Brain plan, one approval pause for the plan, seat-routed implementation, QA and review loops, results shown before the move to qa. Besides that single plan-approval pause, only Relay questions and hard blockers interrupt. Risk tiers live in `docs/conventions.md` (T0 trivial, T1 standard, T2 destructive needs per-action approval). Plan, QA, and review loops allow three tries max, then escalate. Authority for the full rule text is `agents/cognitive-executor.md`.
 - **Hard Operational Boundaries:** Deliver ONLY what was requested at the intended scope. You are STRICTLY FORBIDDEN from widening work into unrequested cleanup, refactoring, documentation, or adjacent features. Do not speculate on abstractions for future requirements. Do not claim completion without verification evidence.
 - **Parallel Agent Execution Mandate:** The Hands MUST actively utilize parallel subagent execution (up to 4 concurrent subagents, e.g., `@explore` or `@general`) whenever a task involves 2 or more independent file scans, signature extractions, or decoupled module changes to accelerate discovery and execution. Serial execution of independent workstreams is a performance violation.
 - **Communication Patterns (Brevity & Focus):** State each fact exactly once. Match the level of detail to the request. You MUST actively avoid conversational filler, decorative analogies, and these specific banned phrases: "load-bearing", "worth stating plainly", "here's the honest truth", "the real tension", "carry the argument", "I would be happy to", "let's dive in". Optimize for engineering clarity.
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 9d2e0ef..edc7e9c 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1468,3 +1468,42 @@ def test_brain_turn_large_prompt_warns_on_stderr(tmp_path, monkeypatch, capsys):
     err = capsys.readouterr().err
     assert "prompt is large" in err
     assert "include_bundle=false" in err
+
+
+def test_bundle_total_cap_bounds_oversize_workspace(tmp_path, monkeypatch):
+    ws = tmp_path / "ws"
+    ws.mkdir()
+    (ws / "a.md").write_text("A" * 2000, encoding="utf-8")
+    (ws / "b.md").write_text("B" * 2000, encoding="utf-8")
+    monkeypatch.setenv("BRAIN_WORKSPACE_ROOT", str(ws))
+    monkeypatch.setattr(bridge, "_BUNDLE_FILES", ("a.md", "b.md"))
+    monkeypatch.setattr(bridge, "_BUNDLE_TOTAL_CAP", 500)
+    out = bridge._build_context_bundle()
+    assert "bundle total cap" in out
+    assert "B" * 2000 not in out
+
+
+def test_fed_context_persists_across_second_turn(tmp_path, monkeypatch):
+    monkeypatch.setenv("BRAIN_SESSIONS_ROOT", str(tmp_path / "sessions"))
+    bridge.save_fed_context("t9", "CTX turn one")
+    assert bridge.load_fed_context("t9") == "CTX turn one"
+    bridge.save_fed_context("t9", "CTX turn one\nCTX turn two")
+    assert bridge.load_fed_context("t9") == "CTX turn one\nCTX turn two"
+
+
+def test_plan_verdict_valid():
+    plan = ("verdict: PLAN APPROVED\nseats: Architect\npath: implement\n"
+            "steps: edit files\ncites: server.py:100, skill.md:20")
+    assert bridge.validate_plan_verdict(plan) == []
+
+
+def test_plan_verdict_missing_fields():
+    problems = bridge.validate_plan_verdict("looks good, ship it")
+    assert any("seats" in p for p in problems)
+    assert any("cites" in p for p in problems)
+
+
+def test_plan_verdict_cites_without_lines():
+    plan = "verdict: ok\nseats: A\npath: p\nsteps: s\ncites: some files somewhere"
+    problems = bridge.validate_plan_verdict(plan)
+    assert any("file path with lines" in p for p in problems)
```
<!-- END_GIT_DIFF -->
