# Task 195: Machine-readable QA verdicts plus rules-first checks

**File:** `tasks/qa/195-machine-verdicts-rules-first.md`
**Source:** manager
**Type:** feature
**Status:** open

## Goal

Make autopilot fully hands-free: QA verdicts return a strict machine-readable `QA_PASSED` / `QA_REJECTED` with file-and-line cites the autopilot parses without copy-paste, and cheap deterministic rule checks (schema, budget, allowlist) run before the LLM judge.

## Manager's Notes

From the Brain self-improvement review (Task 190, live `brain_turn`), ranked R5 (strict verdicts with cites) and R7 (rules before judge). Fixed rules catch clear faults in milliseconds and spare judge tokens; strict verdicts let the hotfix step start automatically.

## Local TODOs

- [x] Define the strict verdict format (`QA_PASSED` / `QA_REJECTED` + `file:line` cites) in the QA persona behavior (fragment 06)
- [x] Add a rules-first gate: schema, budget, and allowlist checks run before any LLM judge call
- [x] Mocked unit tests for the rules gate
- [x] Rebuild system prompt from fragments if 06 changes; verify sync byte-identical

## Acceptance Criteria

- [x] A QA reply parses to a verdict + cites with a single regex
- [x] Schema/budget/allowlist violations are caught without any LLM call
- [x] Prompt sync verified byte-identical after any fragment edit

## Verification Evidence

- **Test command:** `uv run --with pytest --with "mcp==1.30.0" --with pathspec --with pyyaml python -m pytest -q` (repo root)
- **Expected result:** all tests pass, exit 0
- **Actual result:** **252 passed** (gate suite 27/27 incl. 7 round-2 residual tests; full suite, 8 pre-existing warnings), prompt round-trip `SYNC_OK` zero diff (recorded prior round, fragments untouched since)
- **Exit code:** `0`

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task. See `<hands_protocols>` for the authoritative instruction.

## Risk & Rollback

- **Risk:** Over-strict verdict regex rejects valid human-worded verdicts — keep a documented escape hatch.
- **Rollback plan:** Revert the persona-behavior diff; verdicts return to prose.

---

## Execution Log & Reasoning

- Red-green: wrote `tests/test_rules_gate.py` first (13 tests), confirmed collection ERROR (`No module named 'rules_gate'`), then implemented `scripts/qa-rules-gate/rules_gate.py` → 13/13 green.
- Gate design: `parse_verdict` uses one compiled regex each for `VERDICT:` and `CITE:` lines; `run_gate` runs parse → schema → budget → allowlist and returns QA_REJECTED without touching `judge` on any violation (Mock asserted `assert_not_called`); clean payload calls judge exactly once, or returns the parsed verdict when no judge is given. Unparseable replies become QA_REJECTED with reason "unparseable verdict" (documented escape hatch: autopilot falls back to prose, manager may override).
- Fragment 06 QA persona gained the Machine-Readable Verdict Mandate + rules-first pointer + escape hatch; version bumped 9.27.0 → 9.28.0 per AGENTS.md (system-prompt.md is generated, so the version source is `01-system_version.md`).
- Rebuilt `system-prompt.md` via the assembler (81285 bytes), round-trip check `SYNC_OK` zero diff.
- Full suite `uv run --with pytest --with "mcp<2" --with pathspec --with pyyaml python -m pytest tests/` → **232 passed** (env note: system python has no pytest; `mcp` v2 removed FastMCP so suites need `mcp<2`; memory-server tests need pyyaml — all pre-existing env gaps, unrelated to this change).
- **State-machine QA round (fresh brain turn, this session): VERDICT QA_REJECTED.** First attempt hit transport 500, retry succeeded. Brain cites V1–V6: (V1) allowlist `Path(root) in Path(path).parents` fails on relative payload paths (tests only cover absolute `/repo/...`, production payloads are relative like the task's own cited paths) → false QA_REJECTED; (V2) multiple VERDICT lines silently pass on first match instead of failing closed; (V3) no leading-space tolerance (CRLF is fine — `\s*$` covers `\r`); (V4) `judge()` return used unvalidated (None/empty/malformed); (V5) schema check top-level only; (V6) loose cite pattern (disk check: trailing punctuation actually fails closed by dropping the cite rather than accepting it — minor). Hands disk-triage: V1–V5 hold, V3 partially, V6 overstated. Hotfix XML received, scoped to `scripts/qa-rules-gate/rules_gate.py` + `tests/test_rules_gate.py` (relative-path normalize, exactly-one-verdict, whitespace tolerance, judge validation, deeper schema, +7 tests). Per state-machine rule: rejection recorded, NO reviewer round, NO autoclosure — task stays in QA awaiting hotfix decision. Rejection count: 1 (no 3rd-rejection escalation).

- **Autopilot hotfix applied (this session, per QA V1–V6):** `scripts/qa-rules-gate/rules_gate.py` — (V1) `check_allowlist` normalizes both sides with `abspath` so relative payload paths judge correctly; (V2) `parse_verdict` requires exactly ONE VERDICT line (zero or multiple → `UnparseableVerdict`, fail-closed); (V3) VERDICT/CITE regexes tolerate leading spaces/tabs; (V4) `run_gate` validates the judge return against `QA_PASSED`/`QA_REJECTED` (garbage → QA_REJECTED + `judge_called=True`); (V5) `check_schema` supports dotted nested paths; (V6) CITE regex tolerates one trailing punctuation run, stripped from the path. `tests/test_rules_gate.py` +7 tests (relative inside/escape, two-verdicts raise, leading-space parse, judge-garbage rejected, nested-schema missing, cite trailing period). Gate file 20/20, full suite **239 passed** (232 + 7), exit 0. Pending: fresh QA + reviewer via `brain_turn`.

- **Rejection-2 QA round + round-2 fix (this session):** Brain re-run returned QA_REJECTED (rejection 2 of 3) with residual findings F1–F6 + hotfix XML — but the verdict was summary-based (no diff pasted; my summary said `startswith`, real code never used it). Hands disk-triage against ACTUAL code: F1 sibling-prefix FALSE (code used `Path.parents`, boundary-safe); F3 judge-enum FALSE (exact tuple membership, stricter than prescribed normalization — applying it would LOOSEN the gate, so Step 2 deliberately NOT applied); F4 split-regex FALSE (single `findall` for count+parse, zero/two raise tests pre-exist). F2 symlink TRUE (abspath leaves symlink escapes) → FIXED: `check_allowlist` now `realpath` + `commonpath` containment with fail-closed ValueError guard; unused `pathlib.Path` import removed. +7 residual tests (sibling-prefix, symlink escape, symlink-inside passes, indented second marker, judge-None, 3-level nested + non-dict mid, version + full punct tails); unused `import os` removed from test file. Gate **27/27**, full suite **252 passed**, exit 0. Code-grounded Brain re-review (actual code pasted): **QA_PASSED** — D1 FIXED, D2/D3 REFUTED in Hands' favor, no hotfix needed. **Reviewer round (this session): PO_REVIEW_PENDING — technically approved, NOT autoclosed.** Code Reviewer confirms AC/DoD honestly marked, no scope creep, CHANGELOG Parse-Then-Append kept, no task numbers in prompt prose. But status is explicitly PO_REVIEW_PENDING with two PO checks (A1 confirm diff block in file, A2 business need for strict verdict format) and asks the Manager to reply "Approved for closure". Per goal rule (close ONLY on explicit APPROVED) this is a deferral, not an approval — task STAYS in QA awaiting Manager's approval word.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index bf30e4b..1851269 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,8 +8,8 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Added
 
-- **Token-optimization verified spike (Task 150):** Evaluated RTK 0.49.0 locally (musl binary, no global install): passing pytest suite collapses 1801 bytes / 21 lines → 44 bytes / 3 lines (**97.6% fewer bytes**, exit code preserved, 232 passed); small git outputs (±2%) not worth wrapping; `rtk diff` is a `/usr/bin/diff` wrapper (use `rtk git diff`); `rtk test` needs exact dep pins (`mcp==1.30.0` — `<` specs break as shell redirection). `headroom-ai` 0.37.0 (PyPI) and `@caveman-ai/cli` 1.3.3 (npm) registry-verified; proxy/pixel eval deferred (needs provider rewiring + manager approval). New `docs/loop-engine/configuration.md` holds the evidence table; `docs/opencode-shell-strategy.md` §8 holds the practices. Headroom/Caveman proxy integration and 10-task sprint measurement remain open follow-ups.
-- **Machine-readable QA verdicts + rules-first gate (Task 195):** QA persona (fragment 06) now ends every report with a machine verdict block (`VERDICT: QA_PASSED` / `QA_REJECTED` + `CITE: file:line` lines, single-regex parseable) with a documented escape hatch (unparseable → QA_REJECTED with reason, prose fallback, manager override). New `scripts/qa-rules-gate/rules_gate.py` runs verdict-parse, schema, budget, and allowlist checks before any LLM judge call — rule failures return QA_REJECTED without invoking the judge (Mock-asserted). 13 new mocked tests. System version 9.27.0 → 9.28.0, `system-prompt.md` rebuilt (sync-check byte-identical). Full suite: **232 passed**.
+- **Token-optimization verified spike (Task 150):** Evaluated RTK 0.49.0 locally (musl binary, no global install): passing pytest suite collapses 1801 bytes / 21 lines → 44 bytes / 3 lines (**97.6% fewer bytes**, exit code preserved, 232 passed); small git outputs (±2%) not worth wrapping; `rtk diff` is a `/usr/bin/diff` wrapper (use `rtk git diff`); `rtk test` needs exact dep pins (`mcp==1.30.0` — `<` specs break as shell redirection). `headroom-ai` 0.37.0 (PyPI) and `@caveman-ai/cli` 1.3.3 (npm) registry-verified; proxy/pixel eval deferred (needs provider rewiring + manager approval). Claim scoped to passing suites — failing-suite trimming unmeasured. New `docs/loop-engine/configuration.md` holds the evidence table (with source column: local measurement vs tool self-report); `docs/opencode-shell-strategy.md` §8 holds the practices. Headroom/Caveman proxy integration and 10-task sprint measurement remain open follow-ups.
+- **Machine-readable QA verdicts + rules-first gate (Task 195):** QA persona (fragment 06) now ends every report with a machine verdict block (`VERDICT: QA_PASSED` / `QA_REJECTED` + `CITE: file:line` lines, single-regex parseable) with a documented escape hatch (unparseable → QA_REJECTED with reason, prose fallback, manager override). New `scripts/qa-rules-gate/rules_gate.py` runs verdict-parse, schema, budget, and allowlist checks before any LLM judge call — rule failures return QA_REJECTED without invoking the judge (Mock-asserted). 20 mocked tests (relative-path allowlist, exactly-one-verdict, whitespace tolerance, judge validation, nested schema, cite punctuation). System version 9.27.0 → 9.28.0, `system-prompt.md` rebuilt (sync-check byte-identical). Full suite: **239 passed**.
 
 ### Fixed
 
diff --git a/docs/loop-engine/configuration.md b/docs/loop-engine/configuration.md
index 26b5fb7..bbde3d7 100644
--- a/docs/loop-engine/configuration.md
+++ b/docs/loop-engine/configuration.md
@@ -1,27 +1,30 @@
 # Loop Engine Configuration — Token Optimization Evidence
 
-> Verified spike measurements for Task 150 (Future R&D — Token Optimization).
+> Verified spike measurements (token-optimization R&D spike).
 > Date: 2026-09-12. Tool: RTK 0.49.0 (x86_64-unknown-linux-musl, local eval
 > binary in `/tmp`; no global install, no `rtk init -g`).
 > Byte/line counts are the hard evidence; token equivalents assume ~4 chars/token.
 
-## Verified savings (this repo, decision-server suite, 232 tests)
+## Verified savings (this repo, decision-server suite, 232 tests at measure time)
 
-| Command | Raw | Via RTK | Reduction | Exit code |
-| ------- | --- | ------- | --------- | --------- |
-| `pytest tests/ -q` (232 passed) | 1801 bytes / 21 lines | 44 bytes / 3 lines | **97.6% bytes** | preserved (0) |
-| `git status --short` (32 lines) | 1589 bytes | 1621 bytes | −2% (overhead) | n/a |
-| `git log --oneline -15` | 1218 bytes | 1696 bytes | −39% (overhead) | n/a |
-| `git diff --stat HEAD` | 1952 bytes | 1951 bytes | ~0% | n/a |
-| `rtk git diff` (2-file sample) | 5297 bytes / 48 lines | 5204 bytes / 51 lines | ~2% (reformat) | n/a |
+| Command | Raw | Via RTK | Reduction | Exit code | Source |
+| ------- | --- | ------- | --------- | --------- | ------ |
+| `pytest tests/ -q` (232 passed) | 1801 bytes / 21 lines | 44 bytes / 3 lines | **97.6% bytes** | preserved (0) | local measurement, passing suite |
+| `git status --short` (32 lines) | 1589 bytes | 1621 bytes | −2% (overhead) | n/a | local measurement |
+| `git log --oneline -15` | 1218 bytes | 1696 bytes | −39% (overhead) | n/a | local measurement |
+| `git diff --stat HEAD` | 1952 bytes | 1951 bytes | ~0% | n/a | local measurement |
+| `rtk git diff` (2-file sample) | 5297 bytes / 48 lines | 5204 bytes / 51 lines | ~2% (reformat) | n/a | local measurement |
 
 `rtk gain` self-report for the eval session: 11 commands, 1.9K tokens saved
-(41.0% blended — dominated by the test-runner wins).
+(41.0% blended — dominated by the test-runner wins; tool self-report, not
+independently verified).
 
 ## Recommendation
 
-- **Adopt Option A (RTK wrapper) for test/bash output** in agent guidance
-  (see `docs/opencode-shell-strategy.md` §8). Zero repo code changes.
+- **Adopt Option A (RTK wrapper) for passing-suite/test output** in agent
+  guidance (see `docs/opencode-shell-strategy.md` §8). Zero repo code changes.
+  Scope warning: failing-suite output is UNMEASURED — collapsing failures
+  could hide tracebacks, so keep full output on any failure.
 - **Defer Option B (Headroom proxy):** `headroom-ai` 0.37.0 verified present
   on PyPI, but proxy eval requires localhost proxy + provider URL rewiring
   in `loop-engine/loop-engine.jsonc` — follow-up task, needs manager approval.
diff --git a/docs/opencode-shell-strategy.md b/docs/opencode-shell-strategy.md
index 95adc72..9285505 100644
--- a/docs/opencode-shell-strategy.md
+++ b/docs/opencode-shell-strategy.md
@@ -152,7 +152,8 @@ manager approval). Full evidence in `docs/loop-engine/configuration.md`.
   3 lines, 97.6% fewer bytes). Exit code is preserved, so gates still
   fail the build. Prefer `rtk test <cmd>` over raw `pytest`/`cargo test`
   when only the verdict matters; use `rtk recall <id>` to pull the full
-  output on failure.
+  output on failure. Scope warning: failing-suite output is UNMEASURED —
+  keep full output on any failure, never collapse it.
 - **Small git outputs: skip the wrapper.** `git status`, short `git log`,
   and `git diff --stat` are already compact — RTK adds ~1–2% header
   overhead there. Reserve `rtk git ...` for large diffs and long logs.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 34fc957..475f079 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -145,6 +145,12 @@ _SKIP_DIRS = frozenset(
     {".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"}
 )
 
+# Guardrails for the file-pull tools (state-machine hotfix round).
+_READ_MAX_LINES = 2000        # read_file limit clamp — pulls stay pull-sized
+_READ_MAX_BYTES = 2_000_000   # read_file refuses bigger files outright
+_GREP_PATTERN_MAX = 500       # Brain-supplied regex length cap (ReDoS bound)
+_GREP_MAX_LINE_CHARS = 4000   # overlong lines are skipped, never searched
+
 
 def _workspace_root() -> Path:
     """Repo root for context reads; override via ``BRAIN_WORKSPACE_ROOT``."""
@@ -266,7 +272,11 @@ def _build_task_attach(task_id: str) -> str:
         if path is None:
             return ""
         text = path.read_text(encoding="utf-8", errors="replace")
-        rel = path.name
+        try:
+            rel = path.resolve().relative_to(
+                _workspace_root().resolve()).as_posix()
+        except (OSError, ValueError):
+            rel = path.name
         cleaned, _omitted, _truncated = _strip_task_diff(text, rel)
         if len(cleaned) > _TASK_ATTACH_CAP:
             cleaned = (
@@ -311,16 +321,29 @@ def _build_context_bundle() -> str:
 
 
 def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, Any]:
-    """Numbered-line slice of a workspace text file (1-indexed offset)."""
+    """Numbered-line slice of a workspace text file (1-indexed offset).
+
+    The ``limit`` clamps to ``_READ_MAX_LINES`` and files over
+    ``_READ_MAX_BYTES`` are refused — pulls stay pull-sized and can
+    never drag a giant file into context.
+    """
     if not isinstance(path, str) or not path.strip():
         raise ValueError(f"bad path: {path!r}")
     if offset < 1:
         raise ValueError(f"bad offset (1-indexed): {offset!r}")
     if limit < 1:
         raise ValueError(f"bad limit: {limit!r}")
+    limit = min(limit, _READ_MAX_LINES)
     resolved = _resolve_under_root(path)
     if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
         raise ValueError(f"unsupported extension: {path!r}")
+    try:
+        if resolved.stat().st_size > _READ_MAX_BYTES:
+            raise ValueError(
+                f"file too large for read_file: {path!r} "
+                f"(>{_READ_MAX_BYTES} bytes)")
+    except OSError:
+        pass  # stat failed — the read below raises the real error
     text = resolved.read_text(encoding="utf-8", errors="replace")
     lines = text.splitlines()
     total = len(lines)
@@ -336,7 +359,20 @@ def _read_file_impl(path: str, offset: int = 1, limit: int = 200) -> dict[str, A
 
 
 def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
-    """Python-regex search over workspace text files (max 30 hits)."""
+    """Python-regex search over workspace text files (max 30 hits).
+
+    Hardening: the Brain-supplied pattern caps at ``_GREP_PATTERN_MAX``
+    chars (``re`` has no timeout, so length is the ReDoS bound), each hit
+    line truncates at 200 chars, lines over ``_GREP_MAX_LINE_CHARS`` are
+    skipped unsearched, and every candidate resolves against the root
+    BEFORE it is read — a symlink escaping the workspace is skipped,
+    never opened.
+    """
+    if not isinstance(pattern, str) or not pattern:
+        raise ValueError(f"bad regex: {pattern!r}")
+    if len(pattern) > _GREP_PATTERN_MAX:
+        raise ValueError(
+            f"regex too long ({len(pattern)} > {_GREP_PATTERN_MAX})")
     try:
         rx = re.compile(pattern)
     except re.error as exc:
@@ -353,11 +389,18 @@ def _grep_files_impl(pattern: str, subdir: str = ".") -> list[str]:
                 continue
             fpath = Path(dirpath) / name
             try:
-                text = fpath.read_text(encoding="utf-8", errors="replace")
+                resolved = fpath.resolve()
+                resolved.relative_to(root)
+            except (OSError, ValueError):
+                continue  # symlink escape — skip before any read
+            try:
+                text = resolved.read_text(encoding="utf-8", errors="replace")
             except OSError:
                 continue
-            rel = fpath.resolve().relative_to(root).as_posix()
+            rel = resolved.relative_to(root).as_posix()
             for lineno, line in enumerate(text.splitlines(), 1):
+                if len(line) > _GREP_MAX_LINE_CHARS:
+                    continue
                 if rx.search(line):
                     hits.append(f"{rel}:{lineno}: {line.strip()[:200]}")
                     if len(hits) >= 30:
diff --git a/scripts/qa-rules-gate/rules_gate.py b/scripts/qa-rules-gate/rules_gate.py
index 7e773fc..17b63df 100644
--- a/scripts/qa-rules-gate/rules_gate.py
+++ b/scripts/qa-rules-gate/rules_gate.py
@@ -16,13 +16,17 @@ UnparseableVerdict — the autopilot treats that as QA_REJECTED with reason
 
 from __future__ import annotations
 
+import os
 import re
 from dataclasses import dataclass, field
-from pathlib import Path
 from typing import Callable
 
-_VERDICT_RE = re.compile(r"^VERDICT:\s*(QA_PASSED|QA_REJECTED)\s*$", re.MULTILINE)
-_CITE_RE = re.compile(r"^CITE:\s*(\S+):(\d+)\s*$", re.MULTILINE)
+_VERDICT_RE = re.compile(
+    r"^[ \t]*VERDICT:[ \t]*(QA_PASSED|QA_REJECTED)[ \t]*$", re.MULTILINE
+)
+_CITE_RE = re.compile(r"^[ \t]*CITE:[ \t]*(\S+):(\d+)[.,;:!?]*[ \t]*$", re.MULTILINE)
+_VALID_JUDGE_VERDICTS = ("QA_PASSED", "QA_REJECTED")
+_CITE_TRAILING_PUNCT = ".,;:!?"
 
 
 class UnparseableVerdict(ValueError):
@@ -39,22 +43,46 @@ class GateResult:
 def parse_verdict(reply: str) -> tuple[str, list[tuple[str, int]]]:
     """Parse a QA reply into (verdict, [(file, line), ...]) with one regex each.
 
+    Fail-closed: exactly ONE VERDICT line must be present — zero or
+    multiple lines raise. Leading spaces/tabs are tolerated; CRLF is
+    covered by the trailing blank match. Trailing punctuation on a cite
+    path (e.g. ``foo.py:12.``) is stripped, never accepted.
+
     Raises:
-        UnparseableVerdict: if no VERDICT line is present.
+        UnparseableVerdict: if there is not exactly one VERDICT line.
     """
-    match = _VERDICT_RE.search(reply)
-    if not match:
+    matches = _VERDICT_RE.findall(reply)
+    if len(matches) != 1:
         raise UnparseableVerdict(
-            "No machine-readable VERDICT line (expected "
-            "'VERDICT: QA_PASSED' or 'VERDICT: QA_REJECTED')."
+            f"Expected exactly one VERDICT line, found {len(matches)} "
+            "(expected 'VERDICT: QA_PASSED' or 'VERDICT: QA_REJECTED')."
         )
-    cites = [(path, int(line)) for path, line in _CITE_RE.findall(reply)]
-    return match.group(1), cites
+    cites = [
+        (path.rstrip(_CITE_TRAILING_PUNCT), int(line))
+        for path, line in _CITE_RE.findall(reply)
+    ]
+    return matches[0], cites
+
+
+def _lookup_dotted(record: dict, dotted: str) -> bool:
+    """True when a dotted path (``a.b.c``) resolves through nested dicts."""
+    current: object = record
+    for part in dotted.split("."):
+        if not isinstance(current, dict) or part not in current:
+            return False
+        current = current[part]
+    return True
 
 
 def check_schema(record: dict, required: list[str]) -> list[str]:
-    """Missing required fields → one violation string each."""
-    return [f"missing field: {name}" for name in required if name not in record]
+    """Missing required fields → one violation string each.
+
+    Entries may use dotted paths (``verdict.payload``) to require nested
+    keys, not just top-level ones.
+    """
+    return [
+        f"missing field: {name}" for name in required if not _lookup_dotted(record, name)
+    ]
 
 
 def check_budget(used: int, limit: int) -> list[str]:
@@ -65,13 +93,28 @@ def check_budget(used: int, limit: int) -> list[str]:
 
 
 def check_allowlist(paths: list[str], roots: list[str]) -> list[str]:
-    """Paths escaping every allowed root → one violation string each."""
+    """Paths escaping every allowed root → one violation string each.
+
+    Both sides are normalized with ``realpath`` (resolves ``..`` AND
+    symlinks — ``abspath`` alone leaves symlink escapes open) and
+    containment is enforced with ``commonpath``, so sibling-prefix
+    paths (``/allow-evil`` vs root ``/allow``) never match.
+    Relative payload paths (the production shape) are resolved against
+    the process CWD before comparison.
+    """
+    norm_roots = [os.path.realpath(root) for root in roots]
     violations = []
     for path in paths:
-        if not any(
-            Path(path) == Path(root) or Path(root) in Path(path).parents
-            for root in roots
-        ):
+        norm_path = os.path.realpath(path)
+        try:
+            inside = any(
+                norm_path == norm_root
+                or os.path.commonpath([norm_path, norm_root]) == norm_root
+                for norm_root in norm_roots
+            )
+        except ValueError:
+            inside = False  # e.g. different drives — fail closed
+        if not inside:
             violations.append(f"path outside allowlist: {path}")
     return violations
 
@@ -112,7 +155,14 @@ def run_gate(
     if violations:
         return GateResult(verdict="QA_REJECTED", violations=violations)
     if judge is not None:
+        judge_verdict = judge()
+        if judge_verdict not in _VALID_JUDGE_VERDICTS:
+            return GateResult(
+                verdict="QA_REJECTED",
+                violations=[f"invalid judge verdict: {judge_verdict!r}"],
+                judge_called=True,
+            )
         return GateResult(
-            verdict=judge(), violations=[], judge_called=True
+            verdict=judge_verdict, violations=[], judge_called=True
         )
     return GateResult(verdict=verdict, violations=[])
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 1c2aba1..746a0d3 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1088,3 +1088,61 @@ def test_task_attach_truncation_has_pull_path(tmp_path, monkeypatch):
     attach = bridge._build_task_attach("200-foo")
     assert "read_file(" in attach and "200-foo.md" in attach
     assert len(attach) < 30000
+
+
+def test_task_attach_pull_path_is_lane_relative_and_live(tmp_path, monkeypatch):
+    d = tmp_path / "tasks" / "backlog"
+    d.mkdir(parents=True, exist_ok=True)
+    (d / "200-foo.md").write_text(
+        "# T\n<!-- BEGIN_GIT_DIFF -->\nx\n<!-- END_GIT_DIFF -->\n",
+        encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    attach = bridge._build_task_attach("200-foo")
+    assert "tasks/backlog/200-foo.md" in attach
+    pulled = bridge._read_file_impl("tasks/backlog/200-foo.md")
+    assert pulled["total_lines"] == 4
+
+
+def test_grep_skips_symlink_escape(tmp_path, monkeypatch):
+    ws = tmp_path / "ws"
+    sub = ws / "docs"
+    sub.mkdir(parents=True)
+    (sub / "real.md").write_text("hello\n", encoding="utf-8")
+    outside = tmp_path / "outside-secret.md"
+    outside.write_text("SECRET-XYZ\n", encoding="utf-8")
+    (sub / "evil.md").symlink_to(outside)
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: ws)
+    hits = bridge._grep_files_impl("SECRET-XYZ", "docs")
+    assert hits == []
+
+
+def test_read_file_limit_clamped(tmp_path, monkeypatch):
+    (tmp_path / "big.md").write_text(
+        "".join(f"line {n}\n" for n in range(2500)), encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    result = bridge._read_file_impl("big.md", limit=10 ** 9)
+    assert result["limit"] == bridge._READ_MAX_LINES
+    assert len(result["lines"]) == bridge._READ_MAX_LINES
+
+
+def test_read_file_oversize_refused(tmp_path, monkeypatch):
+    (tmp_path / "huge.md").write_bytes(b"x" * (bridge._READ_MAX_BYTES + 1))
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    with pytest.raises(ValueError, match="too large"):
+        bridge._read_file_impl("huge.md")
+
+
+def test_grep_pattern_too_long_rejected(tmp_path, monkeypatch):
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    with pytest.raises(ValueError, match="too long"):
+        bridge._grep_files_impl("a" * (bridge._GREP_PATTERN_MAX + 1))
+
+
+def test_grep_skips_overlong_lines(tmp_path, monkeypatch):
+    sub = tmp_path / "docs"
+    sub.mkdir()
+    (sub / "mix.md").write_text(
+        "MATCH " + ("z" * 5000) + "\nplain MATCH line\n", encoding="utf-8")
+    monkeypatch.setattr(bridge, "_workspace_root", lambda: tmp_path)
+    hits = bridge._grep_files_impl("MATCH", "docs")
+    assert len(hits) == 1 and ":2:" in hits[0]
diff --git a/tests/test_rules_gate.py b/tests/test_rules_gate.py
index 2ceb3d0..fefc856 100644
--- a/tests/test_rules_gate.py
+++ b/tests/test_rules_gate.py
@@ -127,3 +127,115 @@ def test_gate_clean_no_judge_passes():
     )
     assert result.verdict == "QA_PASSED"
     assert result.judge_called is False
+
+
+def test_allowlist_relative_inside():
+    assert check_allowlist(["a/b.py"], roots=["."]) == []
+
+
+def test_allowlist_relative_escape(tmp_path, monkeypatch):
+    sub = tmp_path / "sub"
+    sub.mkdir()
+    monkeypatch.chdir(sub)
+    assert check_allowlist(["../evil.py"], roots=["."]) != []
+
+
+def test_parse_two_verdicts_raise():
+    reply = "VERDICT: QA_PASSED\nSome prose.\nVERDICT: QA_REJECTED\n"
+    with pytest.raises(UnparseableVerdict):
+        parse_verdict(reply)
+
+
+def test_parse_leading_space_verdict():
+    verdict, _ = parse_verdict("  VERDICT: QA_PASSED  \n")
+    assert verdict == "QA_PASSED"
+
+
+def test_gate_judge_garbage_rejected():
+    judge = Mock(return_value="MAYBE")
+    result = run_gate(
+        {"verdict_reply": PASSED_REPLY, "paths": []},
+        required=[],
+        budget=(0, 1_000_000),
+        allowlist_roots=["/repo"],
+        judge=judge,
+    )
+    assert result.verdict == "QA_REJECTED"
+    assert result.judge_called is True
+    assert any("invalid judge verdict" in v for v in result.violations)
+
+
+def test_schema_nested_missing():
+    assert check_schema({"a": {"b": 1}}, required=["a.b", "a.c"]) == [
+        "missing field: a.c"
+    ]
+
+
+def test_parse_cite_trailing_period():
+    verdict, cites = parse_verdict("CITE: foo.py:12.\nVERDICT: QA_PASSED\n")
+    assert verdict == "QA_PASSED"
+    assert cites == [("foo.py", 12)]
+
+
+def test_allowlist_sibling_prefix_rejected():
+    violations = check_allowlist(
+        ["/repo/allow-evil/x.py"], roots=["/repo/allow"]
+    )
+    assert violations == ["path outside allowlist: /repo/allow-evil/x.py"]
+
+
+def test_allowlist_symlink_escape_rejected(tmp_path):
+    allowed = tmp_path / "allowed"
+    allowed.mkdir()
+    secret = tmp_path / "secret.txt"
+    secret.write_text("top secret")
+    link = allowed / "link.py"
+    link.symlink_to(secret)
+    assert check_allowlist([str(link)], roots=[str(allowed)]) == [
+        f"path outside allowlist: {link}"
+    ]
+
+
+def test_allowlist_symlink_inside_passes(tmp_path):
+    allowed = tmp_path / "allowed"
+    allowed.mkdir()
+    real = allowed / "real.py"
+    real.write_text("x = 1")
+    link = allowed / "link.py"
+    link.symlink_to(real)
+    assert check_allowlist([str(link)], roots=[str(allowed)]) == []
+
+
+def test_parse_indented_second_marker_raises():
+    reply = "VERDICT: QA_PASSED\n  VERDICT: QA_REJECTED\n"
+    with pytest.raises(UnparseableVerdict):
+        parse_verdict(reply)
+
+
+def test_gate_judge_none_rejected():
+    judge = Mock(return_value=None)
+    result = run_gate(
+        {"verdict_reply": PASSED_REPLY, "paths": []},
+        required=[],
+        budget=(0, 1_000_000),
+        allowlist_roots=["/repo"],
+        judge=judge,
+    )
+    assert result.verdict == "QA_REJECTED"
+    assert result.judge_called is True
+    assert any("invalid judge verdict" in v for v in result.violations)
+
+
+def test_schema_deep_nested_and_nondict_mid():
+    assert check_schema({"a": {"b": {"c": 1}}}, required=["a.b.c"]) == []
+    assert check_schema({"a": {"b": {"c": 1}}}, required=["a.b.d"]) == [
+        "missing field: a.b.d"
+    ]
+    assert check_schema({"a": 5}, required=["a.b"]) == ["missing field: a.b"]
+
+
+def test_parse_cite_version_and_all_punct_tails():
+    reply = "CITE: pkg/v1.2:34\nCITE: foo.py:12.,;:!?\nVERDICT: QA_PASSED\n"
+    verdict, cites = parse_verdict(reply)
+    assert verdict == "QA_PASSED"
+    assert cites == [("pkg/v1.2", 34), ("foo.py", 12)]
```
<!-- END_GIT_DIFF -->
