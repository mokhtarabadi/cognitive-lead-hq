# Task 0380: Fix missing_context loop on uninjectable paths (sniff fallback + no-repeat contract)

**File:** `tasks/qa/0380-missing-context-loop-uninjectable-paths.md`
**Source:** manager (2026-11-06 — ad-hoc fa: brain kept saying "context ندارم", find the bug, fix in place, no task — then task ordered for the record)
**Type:** bugfix
**Status:** open
**Submitted:** 2026-11-06T11:45:39Z

## Goal

End the planning-loop stall where the Brain re-requests the same `context_paths` entry turn after turn: (1) inject text files whose suffix is not allowlisted via UTF-8/NUL sniffing instead of resolving them to zero chars, and (2) forbid re-requesting a path the bridge labeled `[unavailable: ...]`.

## Manager's Notes

Persian verbatim: "مشکل برین رو حل من ... چرا هی میگه کانتکس ندارم ... باگ و gap رو پیدا کن ... به خود برین بگو self improvement" + "موافقم و برای همه skil template ها تک تک سرچ کن و همه پسوند های موجود رو که نداریم اضافه کن ... نیاز به تسک نیست همونجا درستش کن و تستش ها رو اوکی کن و پاس کن" + "دیدم vue و setelve رو پاک کردی اوکیه تغییرتتت؟" + "الان .env.example رو میتونه بخونه؟" + "تسکش رو بساز توی repo خودش با توضیحت کاملش".

## Root cause (verified, not hypothesized)

Case: dumble 1047 Phase 3 env switches. The Hands fed `context_paths` including `.env.example#L75-100` twice (verbatim bodies per the 0378 contract). The Brain answered `missing_context` for the same path three turns in a row.

- Ledger proof (`tasks/.sessions/<ses>/../context_ledger.jsonl`, dumble repo): `.env.example#L75-100` attached with `status: unavailable:unsupported extension`, `shown_chars: 0` — twice. Bodies for all other requested paths attached WITH content (e.g. aiService slices 1–4 KB each).
- Mechanism (`mcp-brain-bridge/server.py`): `Path('.env.example').suffix` is `.example`, absent from `_ALLOWED_READ_SUFFIXES`, so both attach paths (`build_paths_attach`, `_path_candidates`) emitted `[unavailable: ... — unsupported extension]` with zero injected chars.
- Contract gap (`prompts/fragments/13-constraints.md`, No-Hallucination): `unavailable` counts as missing, and no sentence forbade re-requesting an uninjectable path — so contract-compliant re-requests looped until the Hands-side second-discovery halt fired.
- The fix was validated live: the same `.env.example#L1-2` request now injects with label `[path-injected: .env.example#L1-2 — sniffed text, unlisted extension — lines 1-2 of 3]` on BOTH entry points.

## What was implemented (2026-11-06, no task file at the time — this file is the record)

- `mcp-brain-bridge/server.py`:
  - `_ALLOWED_READ_SUFFIXES` += skill-sweep text suffixes: `sqm properties plist xcconfig strings mod sum ini cfg conf mdx csv rst fish ejs` (each found verbatim in at least one skill template: SQLDelight, Java props, iOS plist/xcconfig, go.mod/go.sum, ini, rst).
  - `_UNREADABLE_SUFFIXES` (exe/dll/so/zip/tar/gz/png/jpg/pdf/aar/keystore/…) skip sniffing outright.
  - `_sniff_text_file()`: read up to `_READ_MAX_BYTES`, reject on NUL, decode UTF-8 — text injects, anything else stays `[unavailable: unsupported extension]`.
  - Wired into BOTH `_path_candidates` (live turns) and `build_paths_attach` (helper/tests); range slicing keeps working on sniffed text and the `sniffed text, unlisted extension` note survives `#Lstart-end` slicing.
  - Incidental catch during review: `.vue`/`.svelte` were accidentally dropped by the allowlist edit and restored; verified programmatically (removed-set empty).
- `prompts/fragments/13-constraints.md` + rebuilt `system-prompt.md` (`9.71.0` → `9.72.0` via `scripts/prompt-build/assemble_system_prompt.py`, byte-clean: only the two intended hunks): an `[unavailable: ...]` label (anything that is NOT a truncation note) means uninjectable — never re-request the same path; proceed without it, ask for an inline paste, or escalate.
- `tests/test_brain_bridge.py`: 4 new tests (dotfile sniff, extensionless sniff, binary stays rejected, skill-sweep suffixes inject).
- `tests/test_prompt_sync.py`: version pin `9.72.0` + new contract test (unavailable-no-repeat sentence present in shipped prompt).
- `mcp-brain-bridge/DECISIONS.md`: ADR-012. `CHANGELOG.md`: entry under `[Unreleased] → Fixed`.
- Verification: full HQ suite `794 passed` (with `--with pyyaml`); `test_brain_bridge.py` + `test_prompt_sync.py` re-run green (`341 passed`) after the vue/svelte restore.

## Local TODOs

- [x] Diagnose loop with ledger evidence (0-char `.env.example` injection).
- [x] Skill-by-skill suffix sweep; extend allowlist; no removals (programmatically verified).
- [x] Sniff fallback in both attach paths; binary stays rejected.
- [x] Contract sentence in fragment; rebuild prompt (9.72.0); byte-clean diff verified.
- [x] Regression tests (bridge + prompt-sync); full suite green twice.
- [x] ADR-012 + CHANGELOG entry.
- [ ] Manager follow-up (optional, not blocking): consider the same sniff treatment for `read_source_files` bulk reports (currently `.gitignore`-aware skips like `.env*` stay skipped there — by design, different contract).

## Acceptance Criteria

- [x] `.env.example#Lx-y` injects with content on both attach entry points (proven live, not just unit-tested).
- [x] No previously allowed suffix was removed (programmatic removed-set check prints NONE).
- [x] An `[unavailable: ...]` path is never re-requested: contract sentence shipped in `system-prompt.md` 9.72.0 and pinned by test.
- [x] Full HQ suite green (`794 passed`).
- [x] `lint_task_file` passes on this task file.

## Verification Evidence

- **Test command:** `uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q` → `794 passed`; targeted `tests/test_brain_bridge.py tests/test_prompt_sync.py` → `341 passed` (after vue/svelte restore)
- **Expected result:** all green; no allowlist removals; live sniff proof
- **Actual result:** all green; removed-set `NONE`; live probe injects `.env.example` with `sniffed text, unlisted extension` label on both entry points
- **Exit code:** 0
- **QA hotfix (2026-11-06):** bounded sniff read + cap-plus-one regression test.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_brain_bridge.py -q` → `314 passed` (incl. `test_sniff_text_file_reads_only_cap_plus_one`); full `rtk test ... python -m pytest tests/ -q` → `795 passed, 24 warnings`
  - **Expected result:** focused + full green; spy asserts single read of exactly `_READ_MAX_BYTES + 1`
  - **Actual result:** green; oversized file returns `None` after one bounded read
  - **Exit code:** 0
- **QA hotfix 2 (2026-11-06):** control-character rejection.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_brain_bridge.py -q` → `314 passed` (incl. updated binary test); full `rtk test ... python -m pytest tests/ -q` → `795 passed, 24 warnings`
  - **Expected result:** focused + full green; control-byte payloads labelled unavailable
  - **Actual result:** green; nul-blob + control-blob both `[unavailable: ... — unsupported extension]`
  - **Exit code:** 0
- **Review hotfix (2026-11-06):** live-turn dotfile regression test.
  - **Test command:** `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/test_brain_bridge.py -q` → `315 passed` (incl. `test_path_candidates_dotfile_sniffs_text`); full `rtk test ... python -m pytest tests/ -q` → `796 passed, 24 warnings`
  - **Expected result:** focused + full green; `_path_candidates` injects `.env.example#L1-1` with sniff label
  - **Actual result:** green; candidate repr carries `sniffed text, unlisted extension` + `OPENAI_MODEL=gemma`
  - **Exit code:** 0
  - Stack-gate skip: root=. markers=[mcp-brain-bridge/pyproject.toml, Flask markers, FastAPI markers, go.mod, build.gradle.kts, Package.swift, *.xcodeproj, package.json, vite.config.*, nuxt.config.*, nest-cli.json, prisma/schema.prisma] matched=[] reason=no matching stack marker found (python-fastapi discipline-only).

## Definition of Done

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** sniffing reads unknown files up to the existing size cap — bounded by `_READ_MAX_BYTES` + per-file/total caps; binaries (incl. NUL-containing text) stay rejected.
- **Rollback:** revert `server.py` hunks + suffix list + fragment sentence; rebuild prompt (9.72.0 → 9.71.0). Worktree currently holds all changes unstaged (no task existed at implementation time); commit path is the Manager's.

---

## Execution Log & Reasoning

- Diagnosis used the per-turn context ledger, not guesses: 0-char `.env.example` attachments + repeated identical re-requests = allowlist gap, not a model reasoning failure.
- The loop also exposed a second, already-fixed gap class (0378: prose fed-context never grounds) — this task covers only the uninjectable-path half.
- No `agents/cognitive-executor.md` changes needed: the Hands-side halt rule (second discovery request = stop) already fired correctly here.
- [2026-11-06 autopilot] Autopilot locked for 0380 (Manager: Brain autopilot to approval-for-closure). Seat Check: bugfix+contract domain → Senior Programmer (+QA/Reviewer at gates); Designer/Strategist/Planner skipped (no UX/scope/capacity surface). Brainstorm: not required — single-domain reversible bugfix, no cross-disciplinary ambiguity.
- [2026-11-06 autopilot] Verification re-run: `rtk test uv run --project mcp-brain-bridge --with pytest --with pyyaml python -m pytest tests/ -q` → `794 passed, 24 warnings`, exit 0. `lint_task_file` passed on in-progress path.
- [2026-11-06 autopilot QA hotfix] QA_REJECTED: `_sniff_text_file()` stat-then-read race could read beyond `_READ_MAX_BYTES`. Fixed with bounded `stream.read(_READ_MAX_BYTES + 1)` + `len(raw) > cap → None`; added `test_sniff_text_file_reads_only_cap_plus_one` (read-size spy). Skills loaded: project-memory, prompt-refactor, testing-strategy, verification-before-completion, task-lint, versioning-and-release; python-fastapi as closest-discipline only (stack-gate skip: root=., markers scanned, matched=[], reason=no matching stack marker found). Sibling docs read: mcp-brain-bridge README/DECISIONS present; tests README/DECISIONS present (no doc changes — no boundary/contract change). Focused `tests/test_brain_bridge.py` → `314 passed`; full suite → `795 passed, 24 warnings`, exit 0; `lint_task_file` on QA path pending re-run. Task stays in `tasks/qa/` for re-QA.
- [2026-11-06 autopilot QA hotfix 2] QA_REJECTED-2: valid-UTF-8 control-byte payloads (`\x01\x02\x03`) passed the NUL check. Fix: `unicodedata.category == "Cc"` reject except `\t\n\r\f`; binary test now covers nul-blob + control-blob with exact unavailable labels. Docs updated (ADR-012, bridge README sniff rule, CHANGELOG qualification). Focused `tests/test_brain_bridge.py` → `314 passed`; full suite → `795 passed, 24 warnings`, exit 0. Stack-gate skip: root=., markers scanned, matched=[], reason=no matching stack marker found.
- [2026-11-06 autopilot review hotfix] APPROVED_WITH_CHANGES: no test pinned dotfile sniff through `_path_candidates` (live-turn entry). Added `test_path_candidates_dotfile_sniffs_text` (test-only, no prod change). Code-search + testing-strategy loaded for this turn. Task stays in `tasks/qa/` for re-review.
- [2026-11-06 autopilot] Re-review verdict: `PO_REVIEW_PENDING` (technical verdict: `APPROVED`). Issues: none. File remains in `tasks/qa/`; closure awaits Manager's explicit `Approved for closure` / `Close task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 6d6c516..c002e82 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Context-path injection for unlisted text files + no-repeat on unavailable paths:** `.env.example` (and any dotfile/extensionless text) resolved to zero chars twice while the model re-requested it — loop broken only by the Hands-side halt. Both attach paths now sniff unlisted suffixes (valid UTF-8 without NUL or disallowed Unicode control characters injects with a `sniffed text` label — tab/LF/CR/FF allowed; known binaries stay rejected), the allowlist gains the skill-sweep text suffixes (sqm, properties, plist, xcconfig, strings, mod, sum, ini, cfg, conf, mdx, csv, rst, fish, ejs), and the No-Hallucination contract states an `[unavailable: ...]` label means uninjectable — never re-request it. The sniff read is bounded at `_READ_MAX_BYTES + 1` (no stat/read race). System prompt 9.71.0 → 9.72.0 via the assembler.
 - **Service policy text now describes the uniform all-server Code Mode routing.**
 - **Prompt-sync regression test pins the binding fed-context contract:** assertions now require the mandatory verbatim-code-or-`context_paths` clause and its mirrored retrieval rule.
 - **Prompt-facing Code Mode docs omit task-number provenance:** the current policy is stated without task IDs; provenance remains in this changelog and the task record.
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 9ccb2d6..4dac8de 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -1,5 +1,12 @@
 # Architectural Decisions: mcp-brain-bridge
 
+## [2026-11-06] ADR-012: unlisted-suffix sniffing + no-repeat on unavailable paths
+
+- **Context:** a planning loop re-requested `.env.example#L75-100` three times. The suffix allowlist rejected it (`unsupported extension`, zero chars injected both times — proven in the context ledger), and the No-Hallucination contract had no rule for `[unavailable: ...]` labels, so contract-compliant re-requests looped until the Hands-side stop fired.
+- **Decision:** (1) both attach paths (`build_paths_attach`, `_path_candidates`) sniff unlisted-suffix files: valid UTF-8 without NUL or disallowed Unicode control characters injects with a `sniffed text, unlisted extension` label (tab, LF, CR, form feed stay allowed); known binary suffixes stay rejected without sniffing. (2) The contract now states an `[unavailable: ...]` label means uninjectable — never re-request the same path. (3) Allowlist gains the skill-sweep text suffixes (sqm, properties, plist, xcconfig, strings, mod, sum, ini, cfg, conf, mdx, csv, rst, fish, ejs).
+- **Consequences:** dotfiles/extensionless text inject on first ask; a genuinely unreadable path fails once instead of looping. Locks (`.lock`) and other unlisted names fall through to the same sniff gate, capped as before.
+- **Rollback:** revert the sniff branches + suffix list + fragment sentence; rebuild system-prompt.md (9.72.0 → prior).
+
 ## [2026-10-06] ADR-001: Initial Slice Baseline
 
 - **Context:** Baseline documentation initialized via init-folder-docs.
diff --git a/mcp-brain-bridge/README.md b/mcp-brain-bridge/README.md
index 3f5ae31..f2e84bd 100644
--- a/mcp-brain-bridge/README.md
+++ b/mcp-brain-bridge/README.md
@@ -17,7 +17,9 @@ Brain Bridge MCP daemon: single-tool (`brain_turn`) automation path for planning
   a trailing `#Lstart-end` (inclusive 1-based lines) or `#Lstart-` (tail
   to EOF); out-of-range ends clamp, empty selections and malformed
   `#L` fragments on supported paths render as explicit `[unavailable: …]`
-  labels.
+  labels. Unlisted-suffix files sniff as text only when valid UTF-8
+  without NUL or disallowed Unicode control characters (tab, LF, CR,
+  form feed allowed); anything else renders `[unavailable: …]`.
 
 ## Key Risks & Invariants
 
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 0cf41a3..05d9dbe 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -65,6 +65,7 @@ import re
 import sys
 import json
 import threading
+import unicodedata
 from pathlib import Path
 from typing import Any, Optional
 from urllib.parse import urlsplit
@@ -522,11 +523,94 @@ _ALLOWED_READ_SUFFIXES = frozenset(
         ".less",
         ".html",
         ".htm",
+        # Config / data (skill-template sweep, task 0378 follow-up).
+        ".properties",
+        ".ini",
+        ".cfg",
+        ".conf",
+        # Mobile resources (iOS skill).
+        ".plist",
+        ".strings",
+        ".xcconfig",
+        # Go modules (go skills reference go.mod/go.sum by name).
+        ".mod",
+        ".sum",
+        # SQLDelight (android-kotlin skill).
+        ".sqm",
+        # Web / docs extras referenced across skills.
+        ".mdx",
+        ".csv",
+        ".rst",
+        ".fish",
+        ".ejs",
         ".vue",
         ".svelte",
     }
 )
 
+#: Suffixes that are never sniffed for text, even when undecodable-safe:
+#: known binary containers where content sniffing would only waste I/O.
+#: Everything else unlisted falls through to the UTF-8/NUL sniff below.
+_UNREADABLE_SUFFIXES = frozenset(
+    {
+        ".exe",
+        ".dll",
+        ".so",
+        ".dylib",
+        ".bin",
+        ".zip",
+        ".tar",
+        ".gz",
+        ".tgz",
+        ".rar",
+        ".7z",
+        ".png",
+        ".jpg",
+        ".jpeg",
+        ".gif",
+        ".bmp",
+        ".webp",
+        ".ico",
+        ".mp3",
+        ".mp4",
+        ".pdf",
+        ".aar",
+        ".keystore",
+        ".jks",
+    }
+)
+
+
+def _sniff_text_file(resolved: "Path") -> Optional[str]:
+    """Best-effort bounded text read for paths with unlisted suffixes.
+
+    Dotfiles, extensionless files, and other unlisted names may contain
+    plain text. Read at most one byte beyond the configured cap so an
+    oversized file can be rejected without reading its full contents.
+    Return ``None`` for oversized, NUL-containing, unreadable, or
+    non-UTF-8 content so the caller labels the path unavailable.
+    """
+    try:
+        with resolved.open("rb") as stream:
+            raw = stream.read(_READ_MAX_BYTES + 1)
+    except OSError:
+        return None
+    if len(raw) > _READ_MAX_BYTES or b"\x00" in raw:
+        return None
+    try:
+        text = raw.decode("utf-8")
+    except UnicodeDecodeError:
+        return None
+    # Reject binary-like control payloads that are valid UTF-8 and contain
+    # no NUL. Preserve the whitespace controls routinely used in text files.
+    if any(
+        unicodedata.category(character) == "Cc" and character not in "\t\n\r\f"
+        for character in text
+    ):
+        return None
+    return text
+
+
 # Guardrail for path injection (state-machine hotfix round).
 _READ_MAX_BYTES = 2_000_000  # oversized files are refused outright
 
@@ -3090,21 +3174,35 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
         except ValueError:
             blocks.append(f"[unavailable: {rel.strip()} — outside workspace]")
             continue
+        sniffed: Optional[str] = None
+        sniff_note = ""
         if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
-            blocks.append(f"[unavailable: {rel.strip()} — unsupported extension]")
-            continue
-        try:
-            if resolved.stat().st_size > _READ_MAX_BYTES:
-                blocks.append(f"[unavailable: {rel.strip()} — file too large]")
+            # Unlisted suffix (dotfiles like `.env.example`, extensionless
+            # files like `Dockerfile`): sniff for plain text instead of
+            # refusing outright. Known binaries skip the sniff.
+            if resolved.suffix.lower() in _UNREADABLE_SUFFIXES:
+                blocks.append(f"[unavailable: {rel.strip()} — unsupported extension]")
                 continue
-            text = resolved.read_text(encoding="utf-8", errors="replace")
+            sniffed = _sniff_text_file(resolved)
+            if sniffed is None:
+                blocks.append(f"[unavailable: {rel.strip()} — unsupported extension]")
+                continue
+            sniff_note = " — sniffed text, unlisted extension"
+        try:
+            if sniffed is None:
+                if resolved.stat().st_size > _READ_MAX_BYTES:
+                    blocks.append(f"[unavailable: {rel.strip()} — file too large]")
+                    continue
+                text = resolved.read_text(encoding="utf-8", errors="replace")
+            else:
+                text = sniffed
         except OSError:
             blocks.append(f"[unavailable: {rel.strip()} — unreadable]")
             continue
         if not text.strip():
             blocks.append(f"[unavailable: {rel.strip()} — empty file]")
             continue
-        open_line = f"[path-injected: {rel.strip()}]"
+        open_line = f"[path-injected: {rel.strip()}{sniff_note}]"
         if range_start is not None:
             sliced, lo, hi, total = _slice_text_lines(text, range_start, range_end)
             # Empty-selection sentinel is lo == 0: a valid slice can itself
@@ -3113,7 +3211,7 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
                 blocks.append(f"[unavailable: {rel.strip()} — empty range]")
                 continue
             text = sliced
-            open_line = f"[path-injected: {rel.strip()} — lines {lo}-{hi} of {total}]"
+            open_line = f"[path-injected: {rel.strip()}{sniff_note} — lines {lo}-{hi} of {total}]"
         _per_file = _ctx_paths_per_file_cap()
         _total_cap = _ctx_paths_total_cap()
         if len(text) > _per_file:
@@ -3497,22 +3595,33 @@ def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[
                 )
             )
             continue
+        sniffed: Optional[str] = None
+        sniff_note = ""
         if resolved.suffix.lower() not in _ALLOWED_READ_SUFFIXES:
-            out.append(
-                _inline_path_candidate(
-                    rel, f"[unavailable: {rel.strip()} — unsupported extension]"
-                )
-            )
-            continue
-        try:
-            if resolved.stat().st_size > _READ_MAX_BYTES:
+            # Same sniff fallback as the helper path: dotfiles and
+            # extensionless text inject; known binaries stay rejected.
+            if resolved.suffix.lower() not in _UNREADABLE_SUFFIXES:
+                sniffed = _sniff_text_file(resolved)
+            if sniffed is None:
                 out.append(
                     _inline_path_candidate(
-                        rel, f"[unavailable: {rel.strip()} — file too large]"
+                        rel, f"[unavailable: {rel.strip()} — unsupported extension]"
                     )
                 )
                 continue
-            text = resolved.read_text(encoding="utf-8", errors="replace")
+            sniff_note = " — sniffed text, unlisted extension"
+        try:
+            if sniffed is None:
+                if resolved.stat().st_size > _READ_MAX_BYTES:
+                    out.append(
+                        _inline_path_candidate(
+                            rel, f"[unavailable: {rel.strip()} — file too large]"
+                        )
+                    )
+                    continue
+                text = resolved.read_text(encoding="utf-8", errors="replace")
+            else:
+                text = sniffed
         except OSError:
             out.append(
                 _inline_path_candidate(
@@ -3527,7 +3636,7 @@ def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[
                 )
             )
             continue
-        open_line = f"[path-injected: {rel.strip()}]"
+        open_line = f"[path-injected: {rel.strip()}{sniff_note}]"
         if range_start is not None:
             sliced, lo, hi, total = _slice_text_lines(text, range_start, range_end)
             # Same sentinel as the helper path above: lo == 0 means no
@@ -3540,7 +3649,7 @@ def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[
                 )
                 continue
             text = sliced
-            open_line = f"[path-injected: {rel.strip()} — lines {lo}-{hi} of {total}]"
+            open_line = f"[path-injected: {rel.strip()}{sniff_note} — lines {lo}-{hi} of {total}]"
         out.append(
             {
                 "kind": "context_path",
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index a202f25..d75719f 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.71.0</system_version>
+<system_version>9.72.0</system_version>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index 2242f40..e2df92b 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -3,7 +3,7 @@
 - **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
-- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file.
+- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file. An `[unavailable: ...]` label (unsupported extension, outside workspace, unreadable, bad range — anything that is NOT a truncation note) means that path cannot be injected: never re-request the same path. Either proceed without it, ask the Hands for an inline paste of the exact lines needed, or escalate.
 - **Tone and Demeanor**: Write as a knowledgeable colleague, not as a machine and not as a friend. Lead with the answer, then the reasoning. Keep the register professional and objective. Skip superlatives, flattery, and filler.
 - **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
   1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
diff --git a/system-prompt.md b/system-prompt.md
index 6425679..2718577 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.71.0</system_version>
+<system_version>9.72.0</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -494,7 +494,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 - **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
-- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file.
+- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need. For file slices, use `path#Lstart-end` for inclusive 1-based line ranges or `path#Lstart-` for the tail through end-of-file. An `[unavailable: ...]` label (unsupported extension, outside workspace, unreadable, bad range — anything that is NOT a truncation note) means that path cannot be injected: never re-request the same path. Either proceed without it, ask the Hands for an inline paste of the exact lines needed, or escalate.
 - **Tone and Demeanor**: Write as a knowledgeable colleague, not as a machine and not as a friend. Lead with the answer, then the reasoning. Keep the register professional and objective. Skip superlatives, flattery, and filler.
 - **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
   1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 540cb92..f8b636c 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1641,6 +1641,115 @@ def test_paths_attach_source_suffixes_inject(tmp_path, monkeypatch):
     assert "class A {}" in out
 
 
+def test_paths_attach_skill_sweep_suffixes_inject(tmp_path, monkeypatch):
+    # Skill-template sweep: SQLDelight, Java props, iOS plist/xcconfig/strings,
+    # Go modules, ini/cfg/conf, mdx/csv/rst/fish/ejs must inject as text.
+    _ws(tmp_path, monkeypatch)
+    files = {
+        "q.sqm": "CREATE TABLE t(id INTEGER);\n",
+        "a.properties": "k=v\n",
+        "Info.plist": "<plist/>\n",
+        "Strict.xcconfig": "SETTING = YES\n",
+        "Localizable.strings": '"k" = "v";\n',
+        "go.mod": "module x\n",
+        "go.sum": "h1:abc=\n",
+        "s.ini": "a=b\n",
+        "s.cfg": "a=b\n",
+        "s.conf": "a=b\n",
+        "p.mdx": "# t\n",
+        "d.csv": "a,b\n",
+        "r.rst": "T\n=\n",
+        "f.fish": "echo hi\n",
+        "v.ejs": "<%= x %>\n",
+    }
+    for name, body in files.items():
+        (tmp_path / name).write_text(body, encoding="utf-8")
+    out = bridge.build_paths_attach(sorted(files))
+    for name, body in files.items():
+        assert f"[path-injected: {name}]" in out, name
+        assert body.strip() in out, name
+
+
+def test_paths_attach_dotfile_sniffs_text(tmp_path, monkeypatch):
+    # The 1046-loop root cause: `.env.example` resolved to zero chars.
+    # Unlisted-but-text names must inject via the sniff fallback.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / ".env.example").write_text(
+        "OPENAI_MODEL=gemma\nOPENAI_HTTP_PROXY=\n", encoding="utf-8"
+    )
+    out = bridge.build_paths_attach([".env.example#L1-1"])
+    assert "sniffed text, unlisted extension" in out
+    assert "OPENAI_MODEL=gemma" in out
+
+
+def test_path_candidates_dotfile_sniffs_text(tmp_path, monkeypatch):
+    """The live-turn candidate entry point injects unlisted dotfile text."""
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / ".env.example").write_text(
+        "OPENAI_MODEL=gemma\nOPENAI_HTTP_PROXY=\n", encoding="utf-8"
+    )
+
+    candidates = bridge._path_candidates([".env.example#L1-1"])
+
+    assert len(candidates) == 1
+    candidate = repr(candidates[0])
+    assert "sniffed text, unlisted extension" in candidate
+    assert "OPENAI_MODEL=gemma" in candidate
+
+
+def test_paths_attach_extensionless_sniffs_text(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "Dockerfile").write_text("FROM x\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["Dockerfile"])
+    assert "sniffed text, unlisted extension" in out
+    assert "FROM x" in out
+
+
+def test_paths_attach_binary_stays_rejected(tmp_path, monkeypatch):
+    """Reject NUL, undecodable, and valid-UTF-8 control-byte payloads."""
+    _ws(tmp_path, monkeypatch)
+    binaries = {
+        "nul-blob": b"\x00\x01binary\xff",
+        "control-blob": b"\x01\x02\x03",
+    }
+
+    for name, payload in binaries.items():
+        (tmp_path / name).write_bytes(payload)
+        out = bridge.build_paths_attach([name])
+        assert f"[unavailable: {name} — unsupported extension]" in out
+
+
+def test_sniff_text_file_reads_only_cap_plus_one(tmp_path, monkeypatch):
+    """The unlisted-suffix sniff must not read an oversized file fully."""
+    path = tmp_path / "payload.unknown"
+    path.write_bytes(b"x" * (bridge._READ_MAX_BYTES + 10))
+    requested_sizes = []
+    original_open = bridge.Path.open
+
+    def tracked_open(target, *args, **kwargs):
+        stream = original_open(target, *args, **kwargs)
+        if target != path:
+            return stream
+
+        class ReadSpy:
+            def __enter__(self):
+                return self
+
+            def __exit__(self, exc_type, exc, traceback):
+                return stream.__exit__(exc_type, exc, traceback)
+
+            def read(self, size=-1):
+                requested_sizes.append(size)
+                return stream.read(size)
+
+        return ReadSpy()
+
+    monkeypatch.setattr(bridge.Path, "open", tracked_open)
+
+    assert bridge._sniff_text_file(path) is None
+    assert requested_sizes == [bridge._READ_MAX_BYTES + 1]
+
+
 def test_paths_attach_missing_labelled(tmp_path, monkeypatch):
     _ws(tmp_path, monkeypatch)
     out = bridge.build_paths_attach(["gone.md"])
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 9573a63..a8e9323 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -47,7 +47,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.71.0"
+    assert shipped == "9.72.0"
 
 
 def test_shipped_prompt_documents_context_path_line_ranges():
@@ -62,6 +62,20 @@ def test_shipped_prompt_documents_context_path_line_ranges():
     assert "path#Lstart-" in shipped
 
 
+def test_shipped_prompt_bans_rerequesting_unavailable_paths():
+    """An [unavailable] label must end the loop, not restart it.
+
+    Regression (1046-loop): `.env.example` is not injectable (unlisted
+    suffix, pre-sniff). The bridge labeled it `[unavailable: ...
+    unsupported extension]` twice and the model re-requested the same
+    path twice — the contract only banned re-requesting *visible*
+    content, never uninjectable paths.
+    """
+    shipped = _read(SHIPPED)
+    assert "never re-request the same path" in shipped
+    assert "[unavailable: ...]" in shipped
+
+
 def test_parallel_mandate_covers_implementation_triggers():
     """The mandate must name implementation/R&D triggers, not discovery only.
```
<!-- END_GIT_DIFF -->
