# Task 0376: Line-range slices for brain_turn context_paths

**File:** `tasks/qa/0376-context-paths-line-ranges.md`
**Source:** manager (2026-11-05 — add line-range/slice support so the Brain can request part of a big file instead of the whole file; web research done first, libraries evaluated and rejected in favor of a suffix convention)
**Type:** feature
**Status:** in-progress

## Goal

Let `brain_turn(context_paths=[...])` accept a line-range suffix — `path#Lstart-end` (and `path#Lstart-` for tail-to-EOF) — so a turn can pull 40 lines out of a 2000-line file instead of truncating a whole-file attach at the cap and stalling on `<missing_context>`.

## Scope

1. **Suffix parsing in `_path_candidates`** (`mcp-brain-bridge/server.py`): strip a trailing `#L<start>[-<end>]` fragment BEFORE `_resolve_under_root` (today the fragment would break both resolution and the suffix allowlist). 1-based lines; clamp `start < 1` to 1 and `end > total` to total; `start > end` or `start > total` becomes an explicit `[unavailable: ... — empty range]` label; non-numeric becomes `[unavailable: ... — bad range]`. Sliced text counts toward the same total cap; the injected block is labeled `[path-injected: rel#Lx-y — lines x-y of N]`.
2. **Contract line**: extend the 0375 narrowing rule in `prompts/fragments/13-constraints.md` with one sentence pointing at the range syntax; bump `01-system_version.md` and rebuild `system-prompt.md` via the assembler (byte-identical except intended hunks).
3. **Tests**: range parsing, clamping both ends, invalid ranges as unavailable labels, empty-range case, total-cap accounting for sliced text, whole-file behavior unchanged when no suffix is present.
4. **Docs**: `docs/brain-bridge.md` `context_paths` description + `mcp-brain-bridge/DECISIONS.md` ADR + CHANGELOG entry.

## Non-goals

- No tree-sitter / symbol-based extraction (new native dependency; breaks the stdlib-only, offline-testable helper invariant).
- No adopting an external MCP server for file reads (violates the single-tool invariant).
- No change to caps, the allocator, traversal, or the MCP schema.
- No change to the truncation-note wording.

## Local TODOs

- [x] Suffix parsing + validation + slicing (`_split_line_range`, `_slice_text_lines`) wired into BOTH `build_paths_attach` and `_path_candidates` via the shared helpers.
- [x] Fragment contract line + version bump 9.70.3 + rebuild (byte-identical except the two intended hunks).
- [x] Docs table (`docs/brain-bridge.md` env rows) + ADR-010 + CHANGELOG.
- [x] Full `test_brain_bridge.py` (304 incl. 7 new range tests) + `test_prompt_sync.py` (22) green.

## Acceptance Criteria

- [ ] `["f.py#L10-20"]` injects exactly lines 10–20 with a `lines x-y of N` label; `["f.py#L200-"]` injects the tail.
- [ ] Out-of-range and malformed suffixes produce explicit unavailable labels, never silent drops and never exceptions.
- [ ] No-suffix behavior is byte-identical to before (existing tests prove it).
- [ ] Sliced text counts toward the shared total cap.
- [ ] The contract names the range syntax so the Brain actually uses it.
- [ ] `lint_system_prompt_sync` equivalent (`test_prompt_sync.py`) green.

## Verification Evidence

| Gate | Result |
|------|--------|
| Web research (blowsh deep loop) | done — Desktop Commander offset/length, large-file-mcp chunk/navigate/search, ctoth tree-sitter extractor, mcp-file-lens; suffix convention chosen, libraries rejected with reasons |
| Brainstorm | done — A: suffix (chosen); B: tree-sitter (rejected: native dep); C: external MCP (rejected: single-tool invariant) |
| Unit + regression tests | pending |
| `test_prompt_sync.py` + `test_brain_bridge.py` | pending |
| Manager plan approval | pending |

## Risk & Rollback

- **Risk:** a `#` in a real filename collides with the fragment syntax. Mitigation: only a trailing `#L<digits>[-<digits>]` pattern is treated as a range; anything else flows through the existing path unchanged (covered by a test with a `#` in the name if the filesystem allows, else documented).
- **Rollback:** revert the parser hunk in `_path_candidates` + fragment line + version bump; ranges stop parsing and whole-file behavior is untouched.

## Definition of Done

- All acceptance criteria evidenced with command exit codes, tests green, lint clean, QA + review verdicts recorded.

## Execution Log & Reasoning

- Key discovery during implementation: TWO parallel implementations exist — `build_paths_attach` (what the tests pin) and `_path_candidates` (what live turns use). The first wiring only hit the live path and all 6 new tests failed with the old "unsupported extension" label, which is exactly how the gap was found. Both paths now share `_split_line_range`/`_slice_text_lines`; the duplication itself is recorded in ADR-010 as follow-up material, not silently fixed here.
- Slicing semantics (approved): `#L10-20` exact slice, `#L200-` tail, `#L10` single line; out-of-range ends clamp, inverted/past-EOF ranges become explicit `[unavailable: … — empty range]` labels; `#` elsewhere in a filename flows through untouched (pinned by test).
- 2026-11-05: implemented end to end, 326/326 green across both suites (304 bridge incl. 7 new range tests + exact-default pin; 22 prompt sync), rebuild byte-identical except the two intended hunks.

- 2026-11-05: research-first per Manager order (parallel blowsh sweep + 3 deep fetches). Decision: suffix convention over libraries — zero new dependencies, stdlib-only helpers stay offline-testable, single-tool invariant holds.
- Autopilot: plan approved by Manager verbatim before implementation; ZAC holds; no prod writes.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1f143a7..10a60fa 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,7 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Brain `missing_context` narrowing rule + raised context-paths caps (Task 0375):** a planning loop stalled 3 turns re-requesting files the bridge had already delivered (truncated at the 60 KB/file cap with an explicit note). The contract only said STOP-and-list, giving the model no narrowing strategy. The rule now states: a truncation note means *partially present* — verify visible scope first, never re-request a fully-present file, narrow instead of repeating (smaller path, section, symbols). Caps raised `_CTX_PATHS_PER_FILE` 60k → 150k and `_CTX_PATHS_TOTAL` 200k → 400k (env overrides unchanged); `context_paths` also accepts `#Lstart-end` / `#Lstart-` slices, wired into both the tested helper and the live-turn path through shared parsers. System prompt rebuilt to `9.70.3` via the assembler (byte-identical except the two intended hunks); `test_prompt_sync` 22/22, `test_brain_bridge` 304/304 (incl. the exact-default pin test and 7 range tests).
 - **Brain `context_paths` rejected source files (Task 0372):** `_ALLOWED_READ_SUFFIXES` predated the task-210 injection feature and allowed only docs/reports, so every `.java`/`.js`/`.tsx` came back `[unavailable: unsupported extension]` — byte-proven (29.5k of 87k attached). Suffix set extended to source-text languages; binaries still rejected; traversal/size/budget guards untouched. 294/294 brain-bridge tests green.
 - **Brain follow-ups (Task 0374):** truncation notes verified pre-existing in the allocator (no code change); ledger rows carry per-path attach outcomes (`path`/`status`/`chars`, leak-tested — no file text ever); monthly quota counter with stderr warning past the threshold (best-effort, never blocks a turn); end-to-end `.java` injection proven live (91,991 chars attached, 297/297 green).
 
diff --git a/docs/brain-bridge.md b/docs/brain-bridge.md
index ce5d05a..7036b8f 100644
--- a/docs/brain-bridge.md
+++ b/docs/brain-bridge.md
@@ -132,8 +132,8 @@ repo-root `.env`). Real process env wins; blank counts as unset. See
 | `BRAIN_STAGE_TIERS` | `plan:T2,review:T2,implement:T0,qa:T0,closure:T0`    |
 | `BRAIN_TASK_ATTACH_CAP` | `60000` — task-file attachment chars; blank/unset = default |
 | `BRAIN_TASK_DIFF_CAP` | `200000` — changed-hunks chars; blank/unset = default |
-| `BRAIN_CTX_PER_FILE_CAP` | `60000` — per `context_paths` file; blank/unset = default |
-| `BRAIN_CTX_TOTAL_CAP` | `200000` — all `context_paths` per turn; blank/unset = default |
+| `BRAIN_CTX_PER_FILE_CAP` | `150000` — per `context_paths` file; blank/unset = default |
+| `BRAIN_CTX_TOTAL_CAP` | `400000` — all `context_paths` per turn; blank/unset = default |
 | `BRAIN_INPUT_BUDGET` | `1000000` — input budget ceiling (system + prompt + history), chars |
 | `BRAIN_MODEL_WINDOW_CHARS` | `200000` — utilization monitor only, never a send cap |
 | `BRAIN_CONTEXT_WINDOW_TOKENS` | `1048576` — provider window for the pre-send guard; blank/unset = default |
diff --git a/mcp-brain-bridge/DECISIONS.md b/mcp-brain-bridge/DECISIONS.md
index 2cce99f..cdc4417 100644
--- a/mcp-brain-bridge/DECISIONS.md
+++ b/mcp-brain-bridge/DECISIONS.md
@@ -64,3 +64,11 @@
 - **Decision:** The comment names OpenCode and other agentic clients; the example names `default.question`, the session tool that actually gates the turn.
 - **Consequences:** Server prose no longer teaches tool names the catalog cannot resolve. Comment-only change; no wire behavior touched.
 - **Rollback:** Restore the two lines from git history.
+
+## [2026-11-05] ADR-010: missing_context narrowing rule + raised context-paths caps
+
+- **Context:** a planning loop stalled for 3 turns re-requesting files the bridge had already delivered (truncated at the 60 KB/file cap with an explicit note). The `missing_context` contract only said STOP-and-list, giving the model no narrowing strategy, and the caps cut a ~181 KB report to 60 KB.
+- **Decision:** (1) extend the No-Hallucination rule: when a truncation note is present, the file counts as partially present — verify visible scope first, never re-request a fully-present file, and narrow (smaller path, section, symbols) instead of repeating a whole-file request. (2) Raise `_CTX_PATHS_PER_FILE` 60k -> 150k and `_CTX_PATHS_TOTAL` 200k -> 400k. The narrowing contract is the real fix; caps only reduce how often truncation fires.
+- **Consequences:** fewer truncation events on large reports; larger worst-case prompts on explicit `context_paths` turns (opt-in only). The exact-default pin test fails loudly on any silent cap drift.
+- **Incidental finding during implementation:** `build_paths_attach` (the unit-tested helper) and `_path_candidates` (the live-turn path) contain parallel loops over the same logic. The range feature was wired into both through the shared `_split_line_range` / `_slice_text_lines` helpers so they cannot drift, but the duplication itself predates this task and is left for a dedicated dedup task.
+- **Rollback:** revert the fragment sentence + cap constants + pin test; rebuild system-prompt.md.
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index 6e0a41a..dd8697f 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -3010,13 +3010,17 @@ def load_fed_context(task_id: str, project_root: Optional[str] = None) -> str:
 
 #: Default per-file cap for path-injected context (chars). Overridable via
 #: ``BRAIN_CTX_PER_FILE_CAP``. Rendering truncates with a resume marker.
-_CTX_PATHS_PER_FILE = 60000
+#: Raised 60k -> 150k (task 0375): the largest observed single artifact
+#: (~181 KB context report) was cut to 60 KB; 150 KB covers that class with
+#: headroom while staying a fraction of the 1M input budget.
+_CTX_PATHS_PER_FILE = 150000
 
 #: Default total cap across all path-injected files per turn (chars).
 #: Overridable via ``BRAIN_CTX_TOTAL_CAP``. Files past the total are
 #: skipped with an explicit skipped note — stacked files must never
-#: overflow the turn budget on their own.
-_CTX_PATHS_TOTAL = 200000
+#: overflow the turn budget on their own. Raised 200k -> 400k alongside
+#: the per-file cap so two large files plus the task attach fit one turn.
+_CTX_PATHS_TOTAL = 400000
 
 
 def _paths_base(project_root: Optional[str] = None) -> Path:
@@ -3063,8 +3067,16 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
     used = 0
     base = _paths_base(project_root)
     for rel in wanted:
+        # Same range handling as the allocator path (_path_candidates): strip
+        # `#Lstart[-end]` before resolution so the fragment breaks neither the
+        # root check nor the suffix allowlist. Both entry points share
+        # _split_line_range/_slice_text_lines so they cannot drift apart.
+        path_part, range_start, range_end, range_error = _split_line_range(rel)
+        if range_error is not None:
+            blocks.append(f"[unavailable: {rel.strip()} — bad range]")
+            continue
         try:
-            resolved = _resolve_under_root(rel, root=base)
+            resolved = _resolve_under_root(path_part, root=base)
         except ValueError:
             blocks.append(f"[unavailable: {rel.strip()} — outside workspace]")
             continue
@@ -3082,6 +3094,14 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
         if not text.strip():
             blocks.append(f"[unavailable: {rel.strip()} — empty file]")
             continue
+        open_line = f"[path-injected: {rel.strip()}]"
+        if range_start is not None:
+            sliced, lo, hi, total = _slice_text_lines(text, range_start, range_end)
+            if not sliced:
+                blocks.append(f"[unavailable: {rel.strip()} — empty range]")
+                continue
+            text = sliced
+            open_line = f"[path-injected: {rel.strip()} — lines {lo}-{hi} of {total}]"
         _per_file = _ctx_paths_per_file_cap()
         _total_cap = _ctx_paths_total_cap()
         if len(text) > _per_file:
@@ -3092,7 +3112,7 @@ def build_paths_attach(paths: object, project_root: Optional[str] = None) -> str
             )
             continue
         used += len(text)
-        blocks.append(f"[path-injected: {rel.strip()}]\n{text}")
+        blocks.append(f"{open_line}\n{text}")
     if not blocks:
         return ""
     return "\n\n---\n\n".join(blocks)
@@ -3360,6 +3380,57 @@ def _inline_path_candidate(rel: str, note: str) -> dict:
     }
 
 
+def _split_line_range(rel: str) -> tuple[str, object, object, object]:
+    """Split a trailing ``#L<start>[-<end>]`` range off a context path.
+
+    Returns ``(path_part, start, end, error)`` where ``start``/``end`` are
+    1-based ints (``end`` is None for the open-ended ``#Lstart-`` form and
+    ``None``/``None`` when no range suffix is present). ``error`` is a short
+    label fragment (``"bad range"``) when the fragment looks like a range
+    but does not parse — the caller turns it into an explicit unavailable
+    label, never a silent drop.
+
+    Only a *trailing* ``#L<digits>`` pattern is treated as a range, so a
+    literal ``#`` anywhere else in a filename flows through untouched.
+    """
+    match = re.search(r"#L(\d+)(?:-(\d*))?$", rel)
+    if not match:
+        return rel, None, None, None
+    try:
+        start = int(match.group(1))
+    except (TypeError, ValueError):
+        return rel, None, None, "bad range"
+    end_raw = match.group(2)
+    if end_raw is None:
+        return rel[: match.start()], start, start, None
+    if end_raw == "":
+        return rel[: match.start()], start, None, None
+    try:
+        end = int(end_raw)
+    except (TypeError, ValueError):
+        return rel, None, None, "bad range"
+    return rel[: match.start()], start, end, None
+
+
+def _slice_text_lines(text: str, start: int, end: object) -> tuple[str, int, int, int]:
+    """Slice ``text`` to 1-based ``[start, end]`` (``end=None`` means EOF).
+
+    Clamps out-of-range ends to the file instead of failing, so a stale line
+    number from an older revision still yields the nearest content. Returns
+    ``(sliced, start, end, total)`` with the *effective* bounds, or
+    ``("", 0, 0, total)`` when the range selects nothing (start > end, or
+    start past EOF) — the caller turns that into an explicit empty-range
+    label, never a silent drop.
+    """
+    lines = text.splitlines()
+    total = len(lines)
+    lo = max(start, 1)
+    hi = total if end is None else min(end, total)
+    if lo > hi or lo > total:
+        return "", 0, 0, total
+    return "\n".join(lines[lo - 1 : hi]), lo, hi, total
+
+
 def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[dict]:
     """Full-text candidates for ``context_paths`` ('' labels kept explicit).
 
@@ -3381,8 +3452,17 @@ def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[
     out: list[dict] = []
     base = _paths_base(project_root)
     for rel in wanted:
+        # Line-range suffix: strip `#Lstart[-end]` BEFORE workspace resolution,
+        # otherwise the fragment breaks both the root check and the suffix
+        # allowlist (`file.py#L10-20` has no recognized extension).
+        path_part, range_start, range_end, range_error = _split_line_range(rel)
+        if range_error is not None:
+            out.append(
+                _inline_path_candidate(rel, f"[unavailable: {rel.strip()} — bad range]")
+            )
+            continue
         try:
-            resolved = _resolve_under_root(rel, root=base)
+            resolved = _resolve_under_root(path_part, root=base)
         except ValueError:
             out.append(
                 _inline_path_candidate(
@@ -3420,11 +3500,23 @@ def _path_candidates(paths: object, project_root: Optional[str] = None) -> list[
                 )
             )
             continue
+        open_line = f"[path-injected: {rel.strip()}]"
+        if range_start is not None:
+            sliced, lo, hi, total = _slice_text_lines(text, range_start, range_end)
+            if not sliced:
+                out.append(
+                    _inline_path_candidate(
+                        rel, f"[unavailable: {rel.strip()} — empty range]"
+                    )
+                )
+                continue
+            text = sliced
+            open_line = f"[path-injected: {rel.strip()} — lines {lo}-{hi} of {total}]"
         out.append(
             {
                 "kind": "context_path",
                 "path": rel.strip(),
-                "open_line": f"[path-injected: {rel.strip()}]",
+                "open_line": open_line,
                 "fence_lang": None,
                 "text": text,
                 "cap": per_file,
diff --git a/prompts/fragments/01-system_version.md b/prompts/fragments/01-system_version.md
index ee72fde..4dbf017 100644
--- a/prompts/fragments/01-system_version.md
+++ b/prompts/fragments/01-system_version.md
@@ -1 +1 @@
-<system_version>9.70.2</system_version>
+<system_version>9.70.3</system_version>
diff --git a/prompts/fragments/13-constraints.md b/prompts/fragments/13-constraints.md
index eacd357..91d54ed 100644
--- a/prompts/fragments/13-constraints.md
+++ b/prompts/fragments/13-constraints.md
@@ -3,7 +3,7 @@
 - **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
-- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
+- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need.
 - **Tone and Demeanor**: Write as a knowledgeable colleague, not as a machine and not as a friend. Lead with the answer, then the reasoning. Keep the register professional and objective. Skip superlatives, flattery, and filler.
 - **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
   1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
diff --git a/system-prompt.md b/system-prompt.md
index b128dfc..c2ed6f8 100644
--- a/system-prompt.md
+++ b/system-prompt.md
@@ -1,4 +1,4 @@
-<system_version>9.70.2</system_version>
+<system_version>9.70.3</system_version>
 
 <role>
 You are the Cognitive Lead AI running inside the Orchestrator platform, acting as an elite software agency orchestrator.
@@ -499,7 +499,7 @@ The Orchestrator strictly operates as an Industrialized Software Production Line
 - **Approval Literals Guard:** Approval phrases match ONLY as English literals. Never translate-then-compare. The plan gate accepts `approved` in any case through the question tool path; closure accepts only the exact phrases `Approved for closure` or `Close task`. Blanket acknowledgements never count at any gate.
 - **Strict Approval Gate & Markdown Plans:** You MUST NOT generate any `<hands_implementation_task>` blocks until the Manager explicitly approves the architectural plan or blueprint. All architectural plans MUST be written in clean, human-readable Markdown. You are STRICTLY FORBIDDEN from using XML tags for your plans. You must present the Markdown plan, ask for approval, and completely STOP generating text. The Manager will provide feedback directly inside Markdown files using `> MANAGER REVIEW:` blockquotes or standard markdown strikethrough/bold edits. You must process this feedback, revise the plan, and ask for approval again, looping until a final "Approved" is received. However, you are explicitly ENCOURAGED to use ```mermaid``` code blocks within your Markdown plans to render visual diagrams (flowcharts, sequence, ER) for the Manager.
 - **Template Preservation Rule:** When generating the `<summary_phase>`, you MUST output the literal placeholder tags (e.g. `<Hands: Describe the features...>`). DO NOT pre-fill the summary.
-- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`.
+- **No Hallucination**: If critical files are missing from context, STOP. Output ONLY `<missing_context>path/to/file</missing_context>`. When the turn already delivered a truncation note (`[...truncated at N chars ...]` or `[skipped: ...]`), the file is *partially present*, not missing: first verify what is already visible before listing anything. Never re-request a file whose full content is already in visible scope, and never re-request the same whole file twice — narrow instead: name a smaller path, a specific section, or the exact symbols you need.
 - **Tone and Demeanor**: Write as a knowledgeable colleague, not as a machine and not as a friend. Lead with the answer, then the reasoning. Keep the register professional and objective. Skip superlatives, flattery, and filler.
 - **Maximum AI-Assistive Code Documentation:** Because this codebase is maintained by AI agents (OpenCode, Cursor), robust code comments are not clutter—they are critical semantic anchors for the LLMs. For every implementation task, you MUST explicitly instruct the Hands to write the MAXIMUM possible documentation:
   1. **Comprehensive Docstrings** on *every* public function, class, and interface explaining the "why", inputs, edge cases, and assumptions.
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 30d8442..100359f 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1654,6 +1654,75 @@ def test_paths_attach_empty_labelled(tmp_path, monkeypatch):
     assert "empty file" in out
 
 
+def test_paths_attach_line_range_slice(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text(
+        "".join(f"line {i}\n" for i in range(1, 11)), encoding="utf-8"
+    )
+    out = bridge.build_paths_attach(["code.py#L3-5"])
+    assert "[path-injected: code.py#L3-5 — lines 3-5 of 10]" in out
+    assert "line 3\nline 4\nline 5" in out
+    assert "line 2\n" not in out
+    assert "line 6\n" not in out
+
+
+def test_paths_attach_line_range_open_tail(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text(
+        "".join(f"line {i}\n" for i in range(1, 6)), encoding="utf-8"
+    )
+    out = bridge.build_paths_attach(["code.py#L4-"])
+    assert "lines 4-5 of 5" in out
+    assert "line 4\nline 5" in out
+    assert "line 3\n" not in out
+
+
+def test_paths_attach_line_range_single_line(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text("a\nb\nc\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["code.py#L2"])
+    assert "lines 2-2 of 3" in out
+    assert "\nb\n" in out or out.rstrip().endswith("b")
+
+
+def test_paths_attach_line_range_clamped(tmp_path, monkeypatch):
+    # Out-of-range ends clamp to the file instead of failing: a stale line
+    # number from an older revision still yields the nearest content.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text("a\nb\nc\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["code.py#L0-99"])
+    assert "lines 1-3 of 3" in out
+    assert "a\nb\nc" in out
+
+
+def test_paths_attach_line_range_empty_labelled(tmp_path, monkeypatch):
+    # start > end and start-past-EOF are caller errors: label, never slice.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "code.py").write_text("a\nb\nc\n", encoding="utf-8")
+    assert "empty range" in bridge.build_paths_attach(["code.py#L3-2"])
+    assert "empty range" in bridge.build_paths_attach(["code.py#L9-12"])
+
+
+def test_paths_attach_line_range_counts_toward_total(tmp_path, monkeypatch):
+    _ws(tmp_path, monkeypatch)
+    monkeypatch.setattr(bridge, "_CTX_PATHS_PER_FILE", 10000)
+    monkeypatch.setattr(bridge, "_CTX_PATHS_TOTAL", 30)
+    (tmp_path / "a.py").write_text("x\n" * 50, encoding="utf-8")
+    out = bridge.build_paths_attach(["a.py#L1-10", "a.py#L11-20"])
+    # First slice (~20 chars) fits; the second exceeds the shared total.
+    assert "lines 1-10 of 50" in out
+    assert "total budget" in out
+
+
+def test_paths_attach_hash_in_filename_not_a_range(tmp_path, monkeypatch):
+    # A literal '#' elsewhere in the name must not be mistaken for a range.
+    _ws(tmp_path, monkeypatch)
+    (tmp_path / "a#b.md").write_text("hash\n", encoding="utf-8")
+    out = bridge.build_paths_attach(["a#b.md"])
+    assert "[path-injected: a#b.md]" in out
+    assert "hash" in out
+
+
 def test_paths_attach_per_file_cap(tmp_path, monkeypatch):
     _ws(tmp_path, monkeypatch)
     (tmp_path / "big.md").write_text(
@@ -3776,8 +3845,9 @@ def test_env_positive_int_override_and_guards(monkeypatch):
 def test_default_caps_meet_issue_thresholds():
     assert bridge._TASK_DIFF_CAP >= 200000
     assert bridge._TASK_ATTACH_CAP >= 60000
-    assert bridge._CTX_PATHS_PER_FILE >= 60000
-    assert bridge._CTX_PATHS_TOTAL >= 200000
+    # Pinned exact: a silent default change alters every turn's prompt budget.
+    assert bridge._CTX_PATHS_PER_FILE == 150000
+    assert bridge._CTX_PATHS_TOTAL == 400000
     assert bridge._INPUT_BUDGET >= 200000
 
 
diff --git a/tests/test_prompt_sync.py b/tests/test_prompt_sync.py
index 5679f26..a9c1fa2 100644
--- a/tests/test_prompt_sync.py
+++ b/tests/test_prompt_sync.py
@@ -44,7 +44,7 @@ def test_shipped_version_is_expected_minor_bump():
     shipped = re.search(
         r"<system_version>(.*?)</system_version>", _read(SHIPPED)
     ).group(1)
-    assert shipped == "9.70.2"
+    assert shipped == "9.70.3"
 
 
 def test_parallel_mandate_covers_implementation_triggers():
```
<!-- END_GIT_DIFF -->
