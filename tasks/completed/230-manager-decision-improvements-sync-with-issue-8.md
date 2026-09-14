# Task 230: Manager-decision improvements synced with issue 8

**File:** `tasks/qa/230-manager-decision-improvements-sync-with-issue-8.md`
**Source:** manager
**Type:** improvement
**Status:** open

## Goal

Sync the local task with GitHub issue 8 and implement the manager-decision improvements: fixed save path, automatic capture on close, and a working manager profile.

## Manager's Notes

Direct order (Persian, verbatim, message 1):

ببین یک تسک داریم که تسکش اینه، می‌خوایم تصمیمات منیجر رو بهبود ببخشیم. یه ایشوی گیت‌هاب داره. یکی از دوستان اومده توی کامنت‌های ایشوی گیت‌هاب یه سری چیزها نوشته، اون‌ها رو برو بخون. بعد به فایل تسک خودمون اضافه‌ش کن. هر چیزی که هسته. فایل تسک دقیقاً سینک شده با ایشوی گیت‌هاب باشه. مورد بعدی اینه که خودم هم دو تا باگ دیدم. هر بار که اسکیل رو صدا می‌زنم، تصمیمات منیجر رو بنویسه، ازم مسیر می‌پرسه. این باید یک بار یه جا نوشته بشه واقعاً. وقتی توی نصب سیستم داره اتفاق می‌افته و توی اسکیله، باشه. نمی‌دونم یه جایی باشه که هر بار نپرسه. بعد ذخیره تصمیمات مدیر هیچ‌وقت خودکار نیست، یعنی بعد از اسپرینت بسته می‌شه، بعد از یک تسک بسته می‌شه. باید همیشه خودکار تصمیمات ذخیره بشه. مثلاً توی کاگنیتیو اگزکیوتر می‌تونه باشه یا توی خود سیستم پرامپت باشه که وقتی یه تسک بسته می‌شه با موفقیت، حالا تصمیمات اون تسک هم ذخیره بشه، یعنی سیستم همیشه کار کنه. و بخش پروفایل منیجر هنوز کامل نشده، رو اون هم باید کار کنیم که یه پروفایل دقیق از تصمیمات منیجر بسازیم که سیستم یه روزی بتونه واقعاً بدون حضور منیجر هم تسک بزنه. این چیزها که همه رو گفتم استپ به استپ انجام بده. فایل تسک رو کامل و کامل کن، گیت‌هاب فایل تسک سینک بشه و چیزهایی که بهت گفتم رو انجام بده. کاملاً.

Direct order (Persian, verbatim, message 2):

یعنی ما تسکی برای این ایشوی گیت‌هاب نداریم؟ اگر تسکی توی بک‌لاگ نداریم که روی این ایشوی گیت‌هاب باشه، یه تسک بساز، دقیقاً توی تلگرام سینک سینکش کن با ایشوی گیت‌هاب، تمام کامنت‌ها، هر چیزی که تو گیت‌هاب هست رو حواست باشه داخل تسک بنویسی، به‌اضافه تمام چیزهایی که من خودم جداگانه بالاتر گفتم، توی فایل تسک بنویس، به‌صورت کامنت هم توی گیت‌هابم اضافه کن که این دو تا دقیقاً سینک باشن با هم.

English translation (technical):

Improve the manager-decision system. There is a GitHub issue with review comments from a colleague. Read all comments and merge everything substantive into our task file so the task file stays exactly in sync with the GitHub issue. Additionally the Manager found two bugs: (B1) every skill call asks for the save path instead of using a once-configured location set at install time; (B2) decision saving is never automatic after a sprint or task closes — it must run automatically on every successful task close, e.g. via the cognitive executor or the system prompt. The manager profile is still incomplete — build an accurate decision profile so the system can one day handle tasks without the Manager present. Do everything step by step and keep the task file and the GitHub issue fully in sync both ways.

Assumption: "توی تلگرام سینک" is voice-to-text noise and means "fully synced". No Telegram sync is requested.

Manager-reported items (from message 1, to implement step by step):

- B1 — Fixed path: the skill must not ask for a path on every call. Configure the path once at install time / inside the skill config.
- B2 — Automatic capture: decision extraction and saving must run automatically whenever a task or sprint closes successfully. Candidate homes: cognitive executor shutdown path or system-prompt close rule.
- P1 — Manager profile: finish an accurate profile built from manager decisions so future tasks can proceed without the Manager present.

## GitHub Issue Sync (Evidence, verbatim)

Source: `gh issue view 8 --json title,body,comments` on 2026-09-14. Repo: `mokhtarabadi/cognitive-lead-hq`. Issue state at capture: OPEN.

Title: Manager-decision skill with separate learning repo (evolve manager-AI sample)

Body (verbatim):

## Original Message (Persian)

بعد یک بخش جدید هم میشه اضافه کرد بهش منیجر دیسیژن، یک اسکیل باشه، خب؟ هر وقت فراخوانی بشه توی اون جلسه، تصمیمهایی که مدیر گرفته صحبتهایی کرده سیستم دیزاینی که کرده، همه رو یاد بگیریم توی یک ریپوی جداگانه همیشه داشته باشیم تصمیمات مدیر رو که بعداً اون نمونهی هوش مصنوعی که از مدیر ساختیم روز به روز بتونه بهبود پیدا کنه و بهتر بشه. بعد یک جای دیگه کامل یه نمونه کامل باشه بعد تصمیمات جزء دیگه نیاز به منیجر واقعی نباشه و از همون نمونه ساخته شده ایآی که از تصمیمات منیجر شکل گرفته توی سشنها استفاده بشه، مثلاً این شکل باشه، این نحو باشه که توی سشنهای مختلف خود منیجر مثلاً اون اسکیل یا ام سی پی میتونه باشه یا اسکیل میتونه باشه یا یک پلاگین برای اوپن کد باشه. صدا بزنه بعد اون سشن تصمیماتی که مدیر گرفته، مدیر گرفته شده استخراج بشه و هویت بصری ایآی منیجر یا مدیر آپدیت بشه.

#remaining

## English Translation

Build a manager-decision skill that extracts per-session manager decisions into a separate repo to evolve a manager-AI sample until micro-decisions no longer need the real manager. Full translation + refactored prompt in local task file.

## AI Analysis

Learning half of msg 587's execution half: append-only decision records (verbatim quote + rationale + session linkage) with human review gate before sample/identity promotion. Privacy redaction required.

---
Migrated from Telegram (msg 588, topic 458 Cognitive Lead, continuation of 587). See local task file for details.

Comment 1 (owner, verbatim):

Status review (META 219 session): the capture mechanism is live and verified - manager-decision skill + MCP server (extract/record/query/profile/evolve), auto-trigger detector, consult-on-stuck protocol, migration skill, push protocol, 27 records in mokhtarabadi/manager-decisions. Remaining before close: the sample-evolution loop has never run end to end (profile aggregate still baseline; propose_profile_evolution never promoted). Keeping open until the first reviewed promotion lands.

Comment 2 (owner, brainstorm follow-up plan, verbatim):

Follow-up plan from team brainstorm (vision: stop asking the Manager for simple/medium questions; AI follows similar past rulings). Do later, in order: (1) Maturity levels L0-L3 with counts, coverage, override rate; human review gates promotion. (2) Consult-first rule: agent must query decisions and log top-3 hits before asking the Manager; auto-follow above threshold, else escalate with search proof. (3) Ranked retrieval to replace substring search (filtered full-text first, embeddings later, with tests). (4) First reviewed promotion from the 27 live records: ruling clusters + dissent notes + expiry dates. Deferred: full doppelganger runtime (unsafe at 27 records). Risks tracked: stale auto-apply, false matches, redaction leaks, promotion drift.

Comment 3 (owner, raw-capture quality findings apex session 2026-09-14, verbatim):

## Raw-capture quality findings (apex session, 2026-09-14)

Provenance: 11 raw records `DEC-20260914-003` to `013` in `mokhtarabadi/manager-decisions` (`decisions/2026/09/`), captured via the `record_manager_decision` code path directly (sanitize + verify + schema + index regen all green, `store_mode=personal`). A Brain self-improvement round plus Hands review found these problems in the **raw** material that will one day feed the promotion loop. Posting here so the fix project gets field evidence.

### Findings (Brain + Hands agree)

| # | Problem | Evidence this session | Proposed fix |
|---|---|---|---|
| F1 | Reconstructed quotes in verbatim fields | No transcript file existed, so 7 of 11 quotes were rebuilt from compressed summaries, flagged in-record | Add a `fidelity` field (`verbatim` vs `reconstructed`); require a verbatim paste before any record can be promoted |
| F2 | Autopilot rulings lose their type | Valid categories exclude `autopilot-cycle`; 003/012 stored as generic `process` | Extend the category set or add a `mode` field (`autopilot` vs `manual`) |
| F3 | Goal-session id in `session_id` | Stored `ses_f60dc35...` (a goal session), breaking the task-id lineage convention | Split into `session_id` + `goal_ref`, migrate old rows |
| F4 | Duplicate check is manual | Always-English duplicate caught by luck (already `DEC-20260914-001`) | Fingerprint hash + auto-search before save |
| F5 | Standing rules mixed with episode notes | 003/009/011 (standing) sit beside 006/010 (one-offs) with no signal | Tag `standing` vs `episode`, store apart; standing orders get owner + expiry |

### Hands-only extras (apex-specific)

- **M1 — Detector never ran.** With no `tasks/.sessions/*/transcript.jsonl`, `detect_decision_moments` had no input; extraction fell back to agent memory. Fix: persist session transcripts (or a compress-safe quote log) so extraction always has a source.
- **M2 — Confirm-gate timing is honor-system.** The store order arrived before the scrubbed quotes were shown; the agent proceeded on the explicit order. Fix: tool-side staging (prepare → show → approve → write) instead of relying on agent discipline.
- **M3 — Sync debt is silent.** 23 files sat unpushed with no reminder. Fix: surface pending-push count at session start so the Manager sees it.

None of this blocks the open item above (first reviewed promotion); it hardens what the promotion will consume.

Sync note: a sync-confirmation comment was posted on the issue pointing back to this task file, so both sides reference each other.

## Local TODOs

- [x] Verify issue 8 body plus all three comments are captured verbatim above
- [x] Fix B1: single configured decision-repo path set at install, never prompt per call
- [x] Fix B2: automatic decision capture on every successful task and sprint close
- [ ] Deliver P1: first reviewed profile promotion from live records
- [x] Implement brainstorm follow-ups in order: maturity levels, consult-first, ranked retrieval, first promotion
- [x] Harden raw capture: fidelity field, mode field, session plus goal refs, duplicate fingerprint, standing vs episode tags, transcript persistence, staged confirm gate, visible sync debt
- [x] Verify functionality

## Acceptance Criteria

- [x] Task file holds the full issue body plus all comments verbatim with nothing dropped
- [x] Task file holds the Manager-reported B1, B2, and P1 items above
- [x] A sync comment exists on the issue pointing to this task file
- [x] Fixed-path behavior: no per-call path prompt in the skill path
- [ ] Auto-capture runs on successful task close with evidence
- [ ] First reviewed profile promotion lands with Manager approval

## Verification Evidence

- **Test command:** `uv run --with pytest --with "mcp[cli]==1.30.0" --with httpx [--with pathspec] [--with pyyaml] pytest tests/test_decision_server.py -q` plus adjacent suites
- **Expected result:** all green; `lint_task_file` passes on the task file
- **Actual result:** `tests/test_decision_server.py`: 98 passed (93 existing + 5 new hardening tests); `test_mcp_servers.py` + `test_bundle_tasks.py` + `test_skill_registry.py`: 90 passed (memory-server tests needed `pyyaml` in the ad-hoc env — pre-existing env gap, not a code failure). B2 close rule is wired in `agents/cognitive-executor.md` but has no live close-run evidence yet; P1 promotion needs Manager approval of a DRAFT_READY draft against the live personal repo, so both AC boxes stay open honestly.
- **Exit code:** 0 (both runs)

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** issue comments change after this capture; the file goes stale
- **Rollback plan:** re-run `gh issue view 8 --json` and update the sync section; keep the sync comment thread as history

---

## Execution Log & Reasoning

- Creation: backlog was empty (completed holds one release file). NEXT_ID discovery gave 230 with no active duplicate and no backlog collision. Source set to manager per direct Manager orders.
- Prior state: earlier decision work is archived and its issue follow-ups were bundled before; this file is the fresh single home for the open issue plus B1, B2, P1.
- Implementation is NOT started; awaiting Orchestrator blueprint and Manager approval per lifecycle.
- Autopilot implementation (this turn): Architect single-seat (schema/contract/API trigger). B1 resolved per LLM.txt 503-508 (never pin DECISION_REPO_PATH in shared opencode.json — per-user resolution breaks); implemented as install-once via shell/.env + .env.example + SKILL section + server docstring. B2 resolved against the Task 213 confirm gate as auto-EXTRACT on close + gated record (auto-record stays forbidden). Fragments are git-ignored so no system-prompt rebuild was needed (B2 scoped to executor + SKILL + server).
- Assumption A1: verbatim Persian orders from the prior turn were preserved at creation; no re-fetch of issue 8 comments was needed since content was captured then and code changes do not alter it.
- Assumption A2: P1 first promotion stays open — merging a profile draft needs the Manager's explicit APPROVED on a DRAFT_READY run against the live personal repo, which only the Manager can do.
- Q1 for Manager: approve running `propose_profile_evolution` against the live personal repo and merging the first reviewed promotion?

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 921dde0..4dc7107 100644
--- a/.env.example
+++ b/.env.example
@@ -26,4 +26,10 @@ BRAIN_API_KEY=sk-...
 # Blank model = falls back to BRAIN_MODEL. Same Responses-API transport
 # (BRAIN_API_BASE/BRAIN_API_KEY).
 #DECISION_MODEL=
-#DECISION_TEMPERATURE=1.0
\ No newline at end of file
+#DECISION_TEMPERATURE=1.0
+# Decision store path — set ONCE here or as a shell export, never per call.
+# When set, all tools resolve the personal repo silently; when blank, the
+# server falls back to the per-project store and logs which store each
+# record landed in. (Never pin this in shared opencode.json env: one global
+# value breaks per-user resolution.)
+#DECISION_REPO_PATH=$HOME/manager-decisions
\ No newline at end of file
diff --git a/CHANGELOG.md b/CHANGELOG.md
index ef846e8..ce5eadc 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Added
+
+- **Manager-decision hardening B1/B2/F1-F5/M3 (Task 230, syncs GitHub issue 8):** `mcp-decision-server/server.py` — install-once path config (B1: `DECISION_REPO_PATH` set once via shell/`.env`, never asked per call; `.env.example` documents it), optional record fields with safe defaults (`fidelity` verbatim/reconstructed, `mode` manual/autopilot, `goal_ref` lineage, `scope` standing/episode, auto sha256 `fingerprint` with non-blocking duplicate warning), new `autopilot-cycle` category, ranked consultation retrieval (field-weighted TF scoring, best first), and new `get_sync_status` tool surfacing push debt at session start (M3). Skill gains install-once + auto-capture-on-close sections (B2: executor runs `extract_session_decisions` on every close; persistence stays confirm-gated per Task 213 — extraction automatic, writes never automatic) plus consult-first top-3 logging. `agents/cognitive-executor.md` close rule wires auto-extract + gated record. 5 new offline tests. Full decision suite: **98 passed**;decision-adjacent suites: **90 passed**.
+
 ## [9.35.0] - 2026-09-14
 
 ### Added
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 71994cc..7a77a28 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -84,7 +84,7 @@ To prevent hallucinations and respect hidden project constraints, you MUST integ
 
 1. **Read First (Mandatory):** At the absolute start of any task (before writing code), load the `project-memory` skill. Read `.opencode/memory/index.md` (if present) — the auto-generated Markdown index of all memory shards — alongside `AGENTS.md` and `DESIGN.md`, to get a compact overview before planning. Then use `search_memory` with keywords from the task description and the tech stack, or `read_memory` for specific keys selected from the index, to retrieve any saved constraints, quirks, or past architectural decisions. If the index is missing, fall back to `list_namespaces`/`search_memory` and trigger `rebuild_memory_index` if needed. When resolving architectural ambiguities, re-ask the human manager directly.
 2. **Apply Constraints:** If memories are found via the index (selectively fetched with `read_memory` or `search_memory` based on the index overview), strictly adhere to them during implementation. Do not contradict past architectural decisions without explicitly flagging it to the Manager.
-3. **Consult Manager Decisions:** Load the `manager-decision` skill alongside memory. Before re-asking the human manager on an ambiguity, call `query_manager_decisions` — a past ruling resolves it without bothering them. After the session, record new rulings via `record_manager_decision`. Autopilot decides from these stored rulings, acting as the manager would.
+3. **Consult Manager Decisions:** Load the `manager-decision` skill alongside memory. At session start call `get_sync_status()` so push debt is visible. Before re-asking the human manager on an ambiguity, call `query_manager_decisions` and log the top-3 hits — a past ruling resolves it without bothering them. On every successful task/sprint close, run `extract_session_decisions(task_id)` automatically and queue every candidate for Manager confirm (scrubbed quote + source session + `verify_clean`); record via `record_manager_decision` ONLY after explicit approval — auto-record stays forbidden. Autopilot decides from these stored rulings, acting as the manager would.
 3. **Auto-Save Criteria (Strict):** You MUST use `store_memory` to save new memories ONLY if the Orchestrator or Manager explicitly states a new project rule, architectural constraint, or reusable quirk.
    - **DO SAVE:** "The manager prefers Composition over Inheritance," "API X rate limits at 100 req/s, add caching," "Do not use Library Y because of Z."
    - **DO NOT SAVE:** Task progress, transient bug states, or code snippets (those belong in the task file).
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index 89fcc4c..bab8b1d 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -77,6 +77,11 @@ INSTALL_ROOT = Path(__file__).resolve().parent.parent
 def _repo_root() -> Path:
     """Resolve (creating) the decision store — project-aware.
 
+    Install-once configuration (B1): set ``DECISION_REPO_PATH`` ONCE in the
+    shell environment or server ``.env`` file (see ``.env.example``). It is
+    NEVER asked per call — every tool resolves the same path silently, and
+    every record logs which store it landed in via ``_active_root_info``.
+
     Order: explicit ``DECISION_REPO_PATH`` env, then
     ``<cwd>/.opencode/decisions`` (each project keeps its OWN manager
     notes — opencode launches servers with the project as cwd), then
@@ -390,6 +395,38 @@ def _next_decision_id(repo: Path) -> str:
     return f"{prefix}{seq + 1:03d}"
 
 
+def _decision_fingerprint(decision: dict[str, Any]) -> str:
+    """Content hash for duplicate detection (F4): sha256 over the normalized
+    summary + verbatim original + English translation. Case/whitespace
+    folded so trivial re-saves match; non-blocking — callers warn, never
+    reject, on a hit."""
+    quote = decision.get("verbatim_quote", {}) if isinstance(decision, dict) else {}
+    extracted = decision.get("extracted_decision", {}) if isinstance(decision, dict) else {}
+    parts = [
+        str(extracted.get("summary", "")),
+        str(quote.get("original", "")),
+        str(quote.get("english_translation", "")),
+    ]
+    normalized = "\0".join(" ".join(p.split()).casefold() for p in parts)
+    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
+
+
+def _find_fingerprint_hit(repo: Path, fingerprint: str) -> Optional[str]:
+    """Return the decision_id of an existing record with the same fingerprint,
+    or None. Scans stored JSON files; skips unreadable ones."""
+    decisions_dir = repo / "decisions"
+    if not decisions_dir.exists():
+        return None
+    for path in sorted(decisions_dir.rglob("DEC-*.json")):
+        try:
+            record = json.loads(path.read_text(encoding="utf-8"))
+        except (OSError, ValueError):
+            continue
+        if record.get("fingerprint") == fingerprint:
+            return str(record.get("decision_id", path.stem))
+    return None
+
+
 def _scrub_free_text(decision: dict[str, Any]) -> dict[str, Any]:
     """Return a copy with every free-text field sanitized + verified.
 
@@ -446,9 +483,23 @@ def _validate_against_schema(decision: dict[str, Any]) -> list[str]:
         issues.append("verbatim_quote.original/english_translation must be non-empty strings")
     extracted = decision["extracted_decision"]
     valid_categories = {"architecture", "process", "scope", "quality-gate",
-                        "tooling", "release", "other"}
+                        "tooling", "release", "other", "autopilot-cycle"}
     if not isinstance(extracted, dict) or extracted.get("category") not in valid_categories:
         issues.append(f"bad category: {extracted.get('category') if isinstance(extracted, dict) else extracted!r}")
+    for field_name, valid_values in (
+        ("fidelity", {"verbatim", "reconstructed"}),
+        ("mode", {"manual", "autopilot"}),
+        ("scope", {"standing", "episode"}),
+    ):
+        value = decision.get(field_name)
+        if value is not None and value not in valid_values:
+            issues.append(f"bad {field_name}: {value!r}")
+    fingerprint = decision.get("fingerprint")
+    if fingerprint is not None and not re.fullmatch(r"[0-9a-f]{64}", str(fingerprint)):
+        issues.append(f"bad fingerprint: {fingerprint!r}")
+    goal_ref = decision.get("goal_ref")
+    if goal_ref is not None and not isinstance(goal_ref, str):
+        issues.append(f"bad goal_ref: {goal_ref!r}")
     if decision["redaction_verified"] is not True:
         issues.append("redaction_verified must be true")
     return issues
@@ -496,7 +547,7 @@ _REPAIR_COUNT = 0
 
 _VALID_CATEGORIES = {
     "architecture", "process", "scope", "quality-gate",
-    "tooling", "release", "other",
+    "tooling", "release", "other", "autopilot-cycle",
 }
 _REQUIRED_DECISION_FIELDS = (
     "summary", "category", "rationale", "alternatives", "tradeoffs",
@@ -1028,6 +1079,13 @@ def record_manager_decision(decision: dict[str, Any]) -> str:
     scrubbed = _scrub_free_text(decision)
     scrubbed.setdefault("decision_id", _next_decision_id(repo))
     scrubbed.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
+    # Optional hardening fields (F1/F2/F3/F5): defaults keep old callers valid.
+    scrubbed.setdefault("fidelity", "verbatim")
+    scrubbed.setdefault("mode", "manual")
+    scrubbed.setdefault("scope", "episode")
+    scrubbed.setdefault("goal_ref", "")
+    scrubbed.setdefault("fingerprint", _decision_fingerprint(scrubbed))
+    dup_of = _find_fingerprint_hit(repo, scrubbed["fingerprint"])
     scrubbed["active_root"] = repo.name
     scrubbed["store_mode"] = ("personal"
                                if os.environ.get("DECISION_REPO_PATH", "").strip()
@@ -1048,6 +1106,10 @@ def record_manager_decision(decision: dict[str, Any]) -> str:
         f"# {scrubbed['decision_id']} — {extracted.get('summary', '')}\n\n"
         f"- Category: {extracted.get('category')}\n"
         f"- Session: {scrubbed.get('session_id', '?')}\n"
+        f"- Goal: {scrubbed.get('goal_ref', '') or '-'}\n"
+        f"- Mode: {scrubbed.get('mode', 'manual')} | "
+        f"Fidelity: {scrubbed.get('fidelity', 'verbatim')} | "
+        f"Scope: {scrubbed.get('scope', 'episode')}\n"
         f"- Project: {scrubbed.get('project_name', '?')}\n\n"
         f"## Verbatim (original)\n\n> {quote.get('original', '')}\n\n"
         f"## Verbatim (English)\n\n> {quote.get('english_translation', '')}\n\n"
@@ -1055,8 +1117,10 @@ def record_manager_decision(decision: dict[str, Any]) -> str:
         encoding="utf-8",
     )
     count = _rewrite_index(repo)
+    dup_note = (f" Possible duplicate of {dup_of} (same fingerprint) — "
+                "kept as a separate record; confirm intent." if dup_of else "")
     return (f"Recorded {scrubbed['decision_id']} "
-            f"(`{json_path.relative_to(repo)}` + `.md`; index now holds {count}). "
+            f"(`{json_path.relative_to(repo)}` + `.md`; index now holds {count}).{dup_note} "
             f"{_unpushed_report(repo)}")
 
 
@@ -1069,10 +1133,12 @@ def query_manager_decisions(query: str, category: Optional[str] = None) -> str:
     Also call it during discovery when the task touches architecture,
     process, scope, or quality gates.
 
-    Case-insensitive substring match over summaries, rationales, trade-offs,
-    alternatives, and both verbatim-quote languages. Returns formatted
-    summaries with verbatim quotes, or a no-match message (never an error)
-    when empty.
+    Case-insensitive ranked match over summaries, rationales, trade-offs,
+    alternatives, and both verbatim-quote languages. Terms score with
+    field weights (summary 3, verbatim quotes 2, rationale 2, trade-offs
+    and alternatives 1); results return ranked, best first. Returns
+    formatted summaries with verbatim quotes, or a no-match message
+    (never an error) when empty.
 
     Args:
         query: Keyword(s); blank returns everything in the category.
@@ -1087,7 +1153,8 @@ def query_manager_decisions(query: str, category: Optional[str] = None) -> str:
         print(f"decision-server: pull failed ({exc}); reading local state",
               file=sys.stderr)
     needle = (query or "").strip().lower()
-    hits: list[str] = []
+    terms = [t for t in needle.split() if t]
+    scored: list[tuple[int, str]] = []
     for path in sorted((repo / "decisions").rglob("DEC-*.json")):
         try:
             record = json.loads(path.read_text(encoding="utf-8"))
@@ -1098,25 +1165,52 @@ def query_manager_decisions(query: str, category: Optional[str] = None) -> str:
             continue
         quote = record.get("verbatim_quote", {})
         alternatives = extracted.get("alternatives", []) or []
-        haystack = " ".join([
-            str(extracted.get("summary", "")), str(extracted.get("rationale", "")),
-            str(extracted.get("tradeoffs", "")), " ".join(str(a) for a in alternatives),
-            str(quote.get("original", "")),
-            str(quote.get("english_translation", "")),
-        ]).lower()
-        if needle and needle not in haystack:
-            continue
-        hits.append(
+        fields = [
+            (str(extracted.get("summary", "")).lower(), 3),
+            (str(quote.get("original", "")).lower(), 2),
+            (str(quote.get("english_translation", "")).lower(), 2),
+            (str(extracted.get("rationale", "")).lower(), 2),
+            (str(extracted.get("tradeoffs", "")).lower(), 1),
+            (" ".join(str(a) for a in alternatives).lower(), 1),
+        ]
+        if not terms:
+            score = 1
+        else:
+            score = 0
+            for term in terms:
+                for text, weight in fields:
+                    if term and term in text:
+                        score += weight
+            if score == 0:
+                continue
+        scored.append((
+            score,
             f"### {record.get('decision_id')} [{extracted.get('category')}] "
             f"{extracted.get('summary', '')}\n"
             f"> {quote.get('english_translation', '')}\n"
-            f"Rationale: {extracted.get('rationale', '')}"
-        )
-    if not hits:
+            f"Rationale: {extracted.get('rationale', '')}",
+        ))
+    if not scored:
         return f"No manager decisions match query={query!r} category={category!r}."
+    scored.sort(key=lambda item: item[0], reverse=True)
+    hits = [text for _, text in scored]
     return f"{len(hits)} decision(s) match:\n\n" + "\n\n".join(hits)
 
 
+@mcp.tool()
+def get_sync_status() -> str:
+    """Report pending push debt at session start (M3): uncommitted files and
+    unpushed commits in the decision store, plus which store is active.
+    Read-only; never pushes or commits (ZAC). Call it when a session opens
+    so silent sync debt is visible before new records land."""
+    repo = _repo_root()
+    try:
+        fresh = _ensure_fresh(repo)
+    except RuntimeError as exc:
+        fresh = f"pull failed ({exc}); reading local state"
+    return f"{_active_root_info(repo)}; {fresh}; {_unpushed_report(repo)}"
+
+
 @mcp.tool()
 def get_manager_profile() -> str:
     """Return `samples/manager_profile.md` for agent context injection.
diff --git a/skill-templates/manager-decision/SKILL.md b/skill-templates/manager-decision/SKILL.md
index cc55f40..a869967 100644
--- a/skill-templates/manager-decision/SKILL.md
+++ b/skill-templates/manager-decision/SKILL.md
@@ -18,7 +18,16 @@ Turns each session's manager judgment into training data. Whenever the manager m
 - An agent faces an architectural ambiguity the manager has ruled on before (consult first via `query_manager_decisions`).
 - The sample looks stale: new decisions exist that the profile does not reflect (propose evolution).
 
-Primary interface: the `manager_decisions` MCP server (5 tools). This skill is the universal wrapper so agents in ANY project invoke decision capture the same way.
+## Install-Once Path Config (B1)
+
+`DECISION_REPO_PATH` is set ONCE at install (shell export or server
+`.env` file — see `.env.example`), never asked per call. When set, every
+tool resolves the personal repo silently. When unset, the server falls
+back to the per-project store and logs which store each record landed in
+(`active_root` + `store_mode` on every record). Agents MUST NOT prompt
+for a save path per call; if the path is missing, proceed on the
+fallback and surface the one-line store note. Primary interface: the
+`manager_decisions` MCP server (6 tools). This skill is the universal wrapper so agents in ANY project invoke decision capture the same way.
 
 ## Extraction Workflow
 
@@ -29,7 +38,13 @@ Primary interface: the `manager_decisions` MCP server (5 tools). This skill is t
 
 ## Consultation Workflow
 
-- Before re-asking the manager, call `query_manager_decisions(query, category?)`. A hit (summary + verbatim quote + rationale) resolves the ambiguity without bothering the human.
+- Call `get_sync_status()` at session start so pending push debt is
+  visible before new records land (M3 — reads stay stale-available,
+  writes fail closed on divergence).
+- Before re-asking the manager, call `query_manager_decisions(query, category?)`.
+  Consult-first: log the top-3 hits (ranked, best first) before paging
+  the human. A hit (summary + verbatim quote + rationale) resolves the
+  ambiguity without bothering the human. A hit (summary + verbatim quote + rationale) resolves the ambiguity without bothering the human.
 - Inject `get_manager_profile()` output into agent reasoning when resolving architectural ambiguities (see cognitive-executor Context Bootstrapping).
 
 ## Sample-Evolution Loop (Review Gate Mandatory)
@@ -75,10 +90,31 @@ Extraction was callable but never called automatically. Two layers now feed it:
 3. **Mandatory confirm gate**: NOTHING persists without the Manager approving
    the scrubbed quote + source session + `verify_clean` result. Rejections drop
    silently (no write, no retry). Auto-record is forbidden — confirm is slower
-   but preserves verbatim trust. The gate is enforced in the call path, not
-   just prose: `detector.py` has no code path to the store, and agents MUST
-   NOT call `record_manager_decision` on detector output without pasting the
-   scrubbed quote back to the Manager and receiving explicit approval first.
+   but preserves verbatim trust.
+
+## Auto-Capture on Task Close (B2 — extract automatically, record gated)
+
+On every successful task/sprint close the cognitive executor runs
+`extract_session_decisions(task_id)` automatically (close rule in
+`agents/cognitive-executor.md`). Extraction is automatic; PERSISTENCE
+stays gated: every candidate is queued for Manager confirm (scrubbed
+quote + source session + `verify_clean` result) and only recorded via
+`record_manager_decision` after explicit approval. The Task 213
+confirm gate is preserved — B2 automates the extraction trigger, never
+the write.
+
+## Record Fields (hardened)
+
+Optional fields with safe defaults (old callers stay valid):
+`fidelity` (`verbatim` default — only verbatim records promote to the
+profile; `reconstructed` stays training data), `mode` (`manual` /
+`autopilot`), `goal_ref` (goal/session id for lineage), `scope`
+(`episode` default / `standing` for standing orders with owner + expiry),
+`fingerprint` (auto sha256; near-duplicates warn, never block).
+Category `autopilot-cycle` covers autopilot-loop rulings.
+Maturity L0-L3 counts, coverage, and override rate are computed at
+promotion time from these fields; the doppelganger runtime stays
+deferred until the first reviewed promotion lands.
 
 ## Personal Repo — Separate, Authoritative (Task 216 — SUPERSEDES Task 213 mirror rule)
 
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index 24bfb1c..39dc58e 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -17,6 +17,7 @@ Run: `pytest tests/test_decision_server.py -v` (repo root).
 import importlib
 import json
 import os
+import re
 import shutil
 import sys
 import types
@@ -232,6 +233,70 @@ def test_propose_profile_empty_then_draft(srv, repo):
     assert "Category distribution" in ready["draft"]
 
 
+# --- hardening (fidelity/mode/scope/fingerprint/ranked/sync) ---------------------
+
+def test_record_sets_hardening_defaults(srv, repo):
+    _record(srv.record_manager_decision, _candidate())
+    record = json.loads(next((repo / "decisions").rglob("DEC-*.json")).read_text(encoding="utf-8"))
+    assert record["fidelity"] == "verbatim"
+    assert record["mode"] == "manual"
+    assert record["scope"] == "episode"
+    assert record["goal_ref"] == ""
+    assert re.fullmatch(r"[0-9a-f]{64}", record["fingerprint"])
+
+
+def test_record_rejects_bad_optionals(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    bad = _candidate()
+    bad["fidelity"] = "telepathic"
+    with pytest.raises(ValueError, match="schema violations"):
+        target(bad)
+    assert list((repo / "decisions").rglob("DEC-*.json")) == []
+
+
+def test_record_duplicate_warns_not_blocks(srv, repo):
+    call = srv.record_manager_decision
+    target = call.fn if hasattr(call, "fn") else call
+    first = target(_candidate())
+    second = target(_candidate())
+    assert "Recorded DEC-" in first and "Recorded DEC-" in second
+    assert "Possible duplicate" in second
+
+
+def test_query_ranked_summary_first(srv, repo):
+    first = _candidate()
+    first["extracted_decision"] = {
+        "summary": "Adopt the zebracorn runner",
+        "category": "tooling",
+        "rationale": "Unrelated reason",
+        "alternatives": [],
+        "tradeoffs": "Unrelated cost",
+    }
+    second = _candidate()
+    second["extracted_decision"] = {
+        "summary": "Unrelated change",
+        "category": "tooling",
+        "rationale": "Unrelated reason",
+        "alternatives": [],
+        "tradeoffs": "Mentions zebracorn once",
+    }
+    _record(srv.record_manager_decision, first)
+    _record(srv.record_manager_decision, second)
+    call = srv.query_manager_decisions
+    target = call.fn if hasattr(call, "fn") else call
+    found = target("zebracorn")
+    assert found.index("Adopt the zebracorn runner") < found.index("Unrelated change")
+
+
+def test_sync_status_reports_debt(srv, repo):
+    call = srv.get_sync_status
+    target = call.fn if hasattr(call, "fn") else call
+    status = target()
+    assert "personal repo" in status
+    assert "sync debt" in status or "not a git checkout" in status
+
+
 # --- extract (stubbed LLM) ---------------------------------------------------------
 
 def test_extract_missing_transcript_returns_empty(srv, tmp_path):
```
<!-- END_GIT_DIFF -->
