# Task 0349: Bundle META output must satisfy the canonical task lint

**File:** `tasks/qa/0349-bundle-meta-lint-parity.md`
**Source:** manager
**Type:** bug
**Status:** open

## Goal

Make `bundle_tasks` emit a META file that passes `lint_task_file` on first write: a non-empty `## Supersedes` section, and every source section that carries provenance (original message, translation, refactored prompt, code context, analysis) preserved inside the META instead of being dropped.

## Manager's Notes

Reported after bundling `282` and `334` in the Apex project. The bundle itself was correct, but the produced META failed the real linter and silently lost the source's Telegram provenance sections. Manager asked for the graph to locate the defect first, then a task, then the fix in this repository.

## Graph findings (2026-10-25)

Graph built over `mcp-context-server` (96 nodes / 143 links). `_build_meta_content` at `bundle.py:23` is the single writer of the META body; `query_graph` also surfaced ADR-010 "Bundle Hardening (ID Retry, Rollback, Validation)" and `mcp-lint-server/server.py` as the validator.

Three defects, all between the writer and the validator:

- **D1 — missing section, not just metadata.** `bundle.py:142` writes `**Supersedes:** [ids]` as a metadata line only. `_check_bundle_meta_structure` (`mcp-lint-server/server.py:529`) requires a `## Supersedes` heading with a non-empty body. Every freshly bundled META therefore fails lint until edited by hand.
- **D2 — provenance sections dropped.** `_build_meta_content` extracts only Goal, Acceptance Criteria, Local TODOs, Risk & Rollback, Manager's Notes and Blueprint Reference (`bundle.py:41-53`). Sections such as `## Original Message (Persian)`, `## English Translation`, `## Refactored Prompt`, `## Relevant Code Context`, `## AI Analysis & Opinion` and `## Source Context` are not copied, so a telegram-sourced bundle loses them from the working file (they survive only in the archive).
- **D3 — the dry-run gate disagrees with the linter.** `server.py:1404-1419` claims "All required sections present" against a list that omits `## Supersedes` and `## Bundled Checklist`, so the preview passes while the real lint fails.

## Acceptance Criteria

- [x] `_build_meta_content` emits a non-empty `## Supersedes` section naming every source task id and title.
- [x] Any `## ` section present in a source task that the bundler does not already handle is copied verbatim into that source's block, in original order, with its heading preserved.
- [x] Structural sections are never duplicated into the source block: Goal, Acceptance Criteria, Local TODOs, Risk & Rollback, Manager's Notes, Blueprint Reference, Execution Log & Reasoning, Factual Git Diff.
- [x] The dry-run required-section list includes `## Supersedes` and `## Bundled Checklist`, so the preview can never pass a file the linter rejects.
- [x] A generated META passes `lint_task_file` with no manual edit (regression test).
- [x] Existing bundle tests stay green.

## Verification Evidence

- **Test command:** `rtk test uv run pytest tests/test_bundle_tasks.py -q`
- **Expected result:** all bundle tests pass, including the new META-lint-parity and provenance-preservation tests
- **Actual result:** `22 passed in 1.28s`. The parity test imports the live `mcp-lint-server` `_check_bundle_meta_structure` and asserts a generated META returns zero issues; against the pre-fix builder it fails on the missing `## Supersedes` section. `tests/test_mcp_servers.py` also run: `87 passed in 4.84s`.
- **Exit code:** 0

## Definition of Done

The task is NOT done unless ALL of the following are true:

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

## Risk & Rollback

- **Risk:** Copying every unrecognised section can duplicate a source's `## Factual Git Diff` or `## Execution Log` into the META, inflating the file and confusing the Hands. Mitigated by an explicit structural deny-list.
- **Rollback plan:** Revert the two file changes; bundling returns to its current behaviour, where the operator patches the META by hand.

## Local TODOs

- [x] Initial codebase exploration
- [x] Add the `## Supersedes` section writer and the extra-section extractor
- [x] Align the dry-run required-section list with the linter
- [x] Add regression tests (lint parity + provenance preservation)
- [x] Verify functionality

---

## Execution Log & Reasoning

**Autopilot lock:** the Manager said "auto lock … and fix it there"; the mode is locked for this task and no approval pauses were taken except hard blockers. None occurred.

**Graph-first discovery.** Graph over `mcp-context-server` (96 nodes / 143 links) plus two `query_graph` calls. The first query seeded on `_build_meta_content` and `_find_task_file`, which placed `bundle.py`, `gitops.py`, `server.py` and the `DECISIONS.md` ADRs in one neighbourhood — enough to see the writer/validator split before reading a line. The second query surfaced ADR-010 (Bundle Hardening), which is why the fix extends that ADR series rather than inventing a new subsystem.

**What changed and why.**

1. `bundle.py` — added `_STRUCTURAL_SECTIONS` and `_extract_preserved_sections`. The deny-list is explicit rather than "everything except what I copy", because `Definition of Done` and `Execution Log & Reasoning` are boilerplate that already exist at META level and duplicating them per source would double the file for zero information. `Verification Evidence` is deliberately NOT in the deny-list: bundled tasks carry different test commands, and dropping them loses the only place that records how each half is proven.
2. `bundle.py` — `_build_meta_content` now renders a real `## Supersedes` section (id + title per source, plus the all-or-nothing sentence). The `**Supersedes:**` metadata line stays: it is machine-readable for tooling, the section is what the linter and a human read.
3. `server.py` — dry-run `required` list gains `## Supersedes` and `## Bundled Checklist`, so the preview can no longer certify a file the linter rejects. This is the defect that made the original bug invisible: the preview printed "All required sections present" while `lint_task_file` failed on the same content.
4. Tests — four added. The parity test imports `mcp-lint-server/server.py` dynamically and runs its real `_check_bundle_meta_structure` over a generated META, so the two servers can never drift again without failing the suite.

**Trailing rule kept:** shell was read-only throughout; every file change went through the native edit tool. Task file was moved with filesystem `mv` because the new file was untracked (`git mv` refuses untracked paths).

**Verification.** `22 passed` for `tests/test_bundle_tasks.py`, `87 passed` for `tests/test_mcp_servers.py`, both exit 0. The parity test is the one that would have caught the original defect: it fails against the pre-fix builder and passes now.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d05655c..a1a4932 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,7 +6,9 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
-_(nothing yet)_
+### Fixed
+
+- **Bundle META now passes the canonical lint on first write, and keeps source provenance (Task 0349):** bundling two telegram-sourced tasks produced a META that failed `lint_task_file` immediately and silently dropped `## Original Message (Persian)`, `## English Translation`, `## Refactored Prompt` and `## Relevant Code Context` from the working file. Three mismatches between writer and validator were found through the graph over `mcp-context-server` (`_build_meta_content` as the single writer, ADR-010 as prior hardening): `bundle.py` emitted only the `**Supersedes:**` metadata line where the linter's `_check_bundle_meta_structure` requires a non-empty `## Supersedes` section; the per-source extraction copied only Goal/AC/TODOs/Risk/Manager's Notes/Blueprint, so provenance sections existed only in the archive; and the dry-run "required sections" gate in `server.py` omitted `## Supersedes` and `## Bundled Checklist`, certifying a file the real lint rejects. `_build_meta_content` now writes a `## Supersedes` section naming every source id and title plus the all-or-nothing rule, and copies every unrecognised `## ` section of a source verbatim into that source's block through the new `_extract_preserved_sections`, guarded by an explicit `_STRUCTURAL_SECTIONS` deny-list so Goal/AC/TODOs/Risk/Definition of Done/Execution Log/Git Diff never repeat; per-source `Verification Evidence` is preserved because bundled tasks carry different test commands. The dry-run list gains both linter sections. ADR-011 records the boundary. Verified: 22/22 bundle tests pass (4 new: Supersedes section, provenance preservation, dry-run list parity, and a parity gate that imports the live `mcp-lint-server` function and asserts a generated META passes it), 87/87 MCP server contract tests pass.
 
 ## [9.66.0] - 2026-10-25
 
diff --git a/mcp-context-server/DECISIONS.md b/mcp-context-server/DECISIONS.md
index e2ae8f4..3a2f360 100644
--- a/mcp-context-server/DECISIONS.md
+++ b/mcp-context-server/DECISIONS.md
@@ -69,3 +69,11 @@
 - **Decision:** Rebuild META body after final ID allocation with atomic exclusive-create-plus-write; rollback restores byte-identical originals to recorded origins via `_git_mv_or_fallback` with surfaced errors; `_locate_task_file` returns distinct ok/duplicate/archived/missing states; `_next_id_collision` checks padded and bare spellings; requests enforce 2-6 tasks with explicit duplicate-input errors; extractor preserves blank-line paragraphs and strips nested boxes; checksum covers all non-empty criteria; status replacement spans the full line with Created-aligned datetime.
 - **Consequences:** Same tool surface, stricter errors, 11 new tests (red-proof first) green alongside the 7 baseline tests.
 - **Rollback:** Revert `server.py`, `gitops.py`, `bundle.py` touchpoints + tests; prior behavior returns.
+
+## [2026-10-25] ADR-011: META Lint Parity and Provenance Preservation
+
+- **Context:** A bundle of two telegram-sourced tasks produced a META that failed `lint_task_file` on write and lost the sources' `## Original Message (Persian)`, `## English Translation`, `## Refactored Prompt` and `## Relevant Code Context`. Three separate mismatches between writer and validator: `_build_meta_content` emitted only the `**Supersedes:**` metadata line where `_check_bundle_meta_structure` requires a non-empty `## Supersedes` section; the per-source extraction copied only Goal/AC/TODOs/Risk/Manager's Notes/Blueprint, so provenance sections vanished from the working file (archive only); and the dry-run "required sections" gate omitted `## Supersedes` and `## Bundled Checklist`, so the preview certified files the linter rejects.
+- **Decision:** `_build_meta_content` now writes a `## Supersedes` section naming every source id and title plus the all-or-nothing rule, and copies every unrecognised `## ` section of each source verbatim into that source's block via `_extract_preserved_sections`, guarded by an explicit `_STRUCTURAL_SECTIONS` deny-list (Goal, AC, TODOs, Risk, Manager's Notes, Blueprint Reference, Definition of Done, Execution Log, Git Diff, and the META's own sections). The dry-run required list gains both linter sections. `Verification Evidence` is deliberately preserved per source because test commands differ between bundled tasks.
+- **Consequences:** A freshly bundled META passes the real linter with no hand edit; telegram provenance survives in the working file; source blocks grow by the preserved sections, which is the intended cost. One new parity test imports the live linter function, so a future divergence between the two servers fails the suite.
+- **Rollback:** Revert `bundle.py` (section writer + extractor), the `server.py` required list, and the four new tests; METAs return to needing manual patching.
+
diff --git a/mcp-context-server/bundle.py b/mcp-context-server/bundle.py
index 8cd1351..ed02c2f 100644
--- a/mcp-context-server/bundle.py
+++ b/mcp-context-server/bundle.py
@@ -19,6 +19,48 @@ from gitops import (
     _verify_verbatim_checksums,
 )
 
+# Sections the bundler already models explicitly, plus structural tail sections
+# that belong to the META itself. Anything else in a source task is provenance
+# (original message, translation, refactored prompt, code context, analysis)
+# and MUST travel into the META verbatim — the archive is not a substitute for
+# the working file.
+_STRUCTURAL_SECTIONS = frozenset(
+    {
+        "Goal",
+        "Acceptance Criteria",
+        "Local TODOs",
+        "Risk & Rollback",
+        "Manager's Notes",
+        "Blueprint Reference",
+        "Definition of Done",
+        "Execution Log & Reasoning",
+        "Factual Git Diff",
+        "Supersedes",
+        "Bundled Checklist (All-or-Nothing)",
+        "Source Bundles (Verbatim Preservation)",
+    }
+)
+
+
+def _extract_preserved_sections(content: str) -> list[tuple[str, str]]:
+    """Return every `## ` section the bundler does not copy on its own.
+
+    Order follows the source file. A trailing horizontal rule is stripped so
+    the copied body does not carry the source's section separator.
+    """
+    headings = list(re.finditer(r"^## (.+)$", content, re.MULTILINE))
+    preserved: list[tuple[str, str]] = []
+    for index, match in enumerate(headings):
+        heading = match.group(1).strip()
+        if heading in _STRUCTURAL_SECTIONS:
+            continue
+        end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
+        body = content[match.end() : end]
+        body = re.sub(r"\n---\s*$", "", body.rstrip()).strip()
+        if body:
+            preserved.append((heading, body))
+    return preserved
+
 
 def _build_meta_content(
     meta_id: int,
@@ -93,6 +135,9 @@ def _build_meta_content(
         if risk:
             block += "#### Risk & Rollback (verbatim)\n\n"
             block += f"{risk}\n\n"
+        for heading, body in _extract_preserved_sections(content):
+            block += f"#### {heading} (verbatim)\n\n"
+            block += f"{body}\n\n"
         block += "---\n\n"
         per_source_blocks.append(block)
     seen_todos: set[str] = set()
@@ -133,6 +178,22 @@ def _build_meta_content(
             f"> ⚠️ **Guardrail Warning:** Combined source size is {total_loc} LOC (> {DIFF_SIZE_WARNING_THRESHOLD}). "
             f"Unified META diff may be large and hard to review. Consider splitting into two METAs.\n\n"
         )
+    # The linter requires a non-empty `## Supersedes` section, not just the
+    # `**Supersedes:**` metadata line. Emitting both keeps the header machine
+    # readable and the body human readable, and a fresh META now passes
+    # lint_task_file without a hand edit.
+    supersedes_lines = "".join(
+        f"- `{sid}` — {stitle}\n" for sid, _path, _content, stitle in source_data
+    )
+    supersedes_section = (
+        f"## Supersedes\n\n"
+        f"This META supersedes {len(source_data)} source task(s). Each one is archived to "
+        f"`tasks/archive/` with a `**Superseded-By:** {meta_id_str}-{meta_slug}` marker and stays "
+        f"reachable via `git log --oneline --follow -- tasks/archive/<id>-*.md`:\n\n"
+        f"{supersedes_lines}\n"
+        f"Execution is all-or-nothing: every line of `## Bundled Checklist (All-or-Nothing)` must pass, "
+        f"otherwise the whole META is `QA_REJECTED` and returns to `in-progress`. A partial close is forbidden.\n\n"
+    )
     content = (
         f"{title_line}\n\n"
         f"**File:** `{file_header}`\n"
@@ -143,6 +204,7 @@ def _build_meta_content(
         f"**Meta:** true\n"
         f"**Created:** {timestamp}\n"
         f"**Bundled:** {len(source_data)} tasks\n\n"
+        f"{supersedes_section}"
         f"## Goal\n\n"
         f'Unified execution of {len(source_data)} related small tasks as a single META task to eliminate sequential overhead. This META bundles tasks {_format_task_id_list(source_ids)} — "{meta_title}" — into one branch, one diff, and one QA gate (all-or-nothing). Every requirement below is preserved **verbatim** from its source task; no summarization or omission is allowed.\n\n'
         f"{warning_note}**Source IDs:** {_format_task_id_list(source_ids)}\n"
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index b2513ef..d53c54c 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -1403,6 +1403,8 @@ def bundle_tasks(
             lines.append(f"\n   ... {len(meta_content.splitlines()) - 40} more lines")
             required = [
                 "## Goal",
+                "## Supersedes",
+                "## Bundled Checklist",
                 "## Local TODOs",
                 "## Acceptance Criteria",
                 "## Verification Evidence",
diff --git a/tests/test_bundle_tasks.py b/tests/test_bundle_tasks.py
index 3834ecd..f05f714 100644
--- a/tests/test_bundle_tasks.py
+++ b/tests/test_bundle_tasks.py
@@ -604,3 +604,165 @@ def test_patch_multiword_status(tmp_tasks: Path):
     assert "progress" not in [line for line in text.splitlines() if "Status" in line][0]
     created_fmt = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", text)
     assert created_fmt, f"Superseded-At must match Created datetime format:\n{text}"
+
+
+# ---------------------------------------------------------------------------
+# META lint parity + provenance preservation
+# ---------------------------------------------------------------------------
+
+
+def _telegram_style_source(
+    tasks: Path, task_id: str, title: str, raw_text: str
+) -> Tuple[str, Path, str, str]:
+    """A telegram-sourced task carrying the sections the bundler used to drop."""
+    padded = f"{int(task_id):02d}"
+    filename = f"{padded}-{title.lower().replace(' ', '-')}.md"
+    path = tasks / "backlog" / filename
+    content = (
+        f"# Task {task_id}: {title}\n"
+        f"\n"
+        f"**File:** `tasks/backlog/{filename}`\n"
+        f"**Source:** telegram\n"
+        f"**Type:** bug\n"
+        f"**Status:** open\n"
+        f"\n"
+        f"## Goal\n"
+        f"\n"
+        f"Goal for {title}.\n"
+        f"\n"
+        f"## Original Message (Persian)\n"
+        f"\n"
+        f"{raw_text}\n"
+        f"\n"
+        f"## English Translation\n"
+        f"\n"
+        f"Translation for {title}.\n"
+        f"\n"
+        f"## Refactored Prompt\n"
+        f"\n"
+        f"<role>role for {title}</role>\n"
+        f"\n"
+        f"## Relevant Code Context\n"
+        f"\n"
+        f"- `src/sample.py` — sample pointer\n"
+        f"\n"
+        f"## Local TODOs\n"
+        f"\n"
+        f"- [ ] Step 1\n"
+        f"\n"
+        f"## Acceptance Criteria\n"
+        f"\n"
+        f"- [ ] Criterion for {title}\n"
+        f"\n"
+        f"## Verification Evidence\n"
+        f"\n"
+        f"- **Test command:** pytest\n"
+        f"\n"
+        f"## Definition of Done\n"
+        f"\n"
+        f"- [ ] Build/Test/Lint pass\n"
+        f"\n"
+        f"## Risk & Rollback\n"
+        f"\n"
+        f"- **Risk:** none\n"
+        f"- **Rollback plan:** revert\n"
+        f"\n"
+        f"---\n"
+        f"\n"
+        f"## Execution Log & Reasoning\n"
+        f"\n"
+        f"_(fill)_\n"
+        f"\n"
+        f"## Factual Git Diff\n"
+        f"\n"
+        f"<!-- BEGIN_GIT_DIFF -->\n"
+        f"\n"
+        f"<!-- END_GIT_DIFF -->\n"
+    )
+    path.write_text(content, encoding="utf-8")
+    return (task_id, path, content, title)
+
+
+def test_meta_carries_supersedes_section(tmp_tasks: Path):
+    """The linter wants a `## Supersedes` section, not only metadata."""
+    s1 = _telegram_style_source(tmp_tasks, "51", "first source", "متن اول")
+    s2 = _telegram_style_source(tmp_tasks, "52", "second source", "متن دوم")
+
+    meta = _build_meta_content(
+        90, "sample-bundle", "sample bundle", ["51", "52"], [s1, s2]
+    )
+
+    body = extract_section(meta, "Supersedes")
+    assert body, f"`## Supersedes` must be non-empty:\n{meta[:800]}"
+    assert "`51`" in body and "`52`" in body, f"source ids missing from body:\n{body}"
+    assert "first source" in body and "second source" in body, (
+        f"source titles missing from body:\n{body}"
+    )
+
+
+def test_meta_preserves_provenance_sections(tmp_tasks: Path):
+    """Provenance sections travel into the META; structural ones do not repeat."""
+    s1 = _telegram_style_source(tmp_tasks, "53", "provenance one", "سلام دنیا")
+    s2 = _telegram_style_source(tmp_tasks, "54", "provenance two", "پایان متن")
+
+    meta = _build_meta_content(
+        91, "provenance-bundle", "provenance bundle", ["53", "54"], [s1, s2]
+    )
+
+    assert "#### Original Message (Persian) (verbatim)" in meta, (
+        "original message section must be preserved"
+    )
+    assert "سلام دنیا" in meta and "پایان متن" in meta, "raw text must survive verbatim"
+    assert "#### English Translation (verbatim)" in meta, (
+        "translation must be preserved"
+    )
+    assert "#### Refactored Prompt (verbatim)" in meta, (
+        "refactored prompt must be preserved"
+    )
+    assert "#### Relevant Code Context (verbatim)" in meta, (
+        "code context must be preserved"
+    )
+    assert "<role>role for provenance one</role>" in meta, "prompt body must survive"
+
+    # Structural sections belong to the META only, never inside a source block.
+    assert "#### Goal (verbatim)" in meta
+    assert "#### Acceptance Criteria (verbatim)" in meta
+    assert "#### Verification Evidence (verbatim)" in meta, (
+        "per-source test commands must be preserved"
+    )
+    for structural in (
+        "#### Execution Log & Reasoning (verbatim)",
+        "#### Factual Git Diff (verbatim)",
+        "#### Definition of Done (verbatim)",
+    ):
+        assert structural not in meta, f"{structural} must not be duplicated"
+
+
+def test_dry_run_required_sections_match_linter():
+    """The preview gate must demand the same sections the linter enforces."""
+    import inspect
+
+    source = inspect.getsource(_bundler.bundle_tasks)
+    assert '"## Supersedes"' in source, "dry-run required list must include Supersedes"
+    assert '"## Bundled Checklist"' in source, (
+        "dry-run required list must include the bundled checklist"
+    )
+
+
+def test_generated_meta_passes_real_linter(tmp_tasks: Path):
+    """Parity gate: the real linter must accept a freshly generated META."""
+    lint_spec = importlib.util.spec_from_file_location(
+        "hq_lint_server",
+        PROJECT_ROOT / "mcp-lint-server" / "server.py",
+    )
+    lint_mod = importlib.util.module_from_spec(lint_spec)
+    lint_spec.loader.exec_module(lint_mod)
+
+    s1 = _telegram_style_source(tmp_tasks, "55", "lint parity one", "متن")
+    s2 = _telegram_style_source(tmp_tasks, "56", "lint parity two", "متن دوم")
+    meta = _build_meta_content(
+        92, "lint-parity-bundle", "lint parity bundle", ["55", "56"], [s1, s2]
+    )
+
+    issues = lint_mod._check_bundle_meta_structure(meta, "tasks/backlog/92-x.md")
+    assert issues == [], f"freshly generated META fails the real linter: {issues}"
```
<!-- END_GIT_DIFF -->
