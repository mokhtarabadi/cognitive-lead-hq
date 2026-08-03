# Task 78: Fix commit_and_clean_task orphaned hash bug

**File:** `tasks/completed/78-fix-commit-and-clean-task-orphaned-hash.md`
**Source:** manager
**Type:** bug
**Status:** closed

## Goal

Fix the `commit_and_clean_task` MCP tool in `mcp-context-server/server.py` so the commit hash stored in the task file always references a commit reachable from HEAD. The tool previously captured the hash before `git commit --amend`, which orphaned the stored commit and broke `git show <hash>` audit trails.

## Manager's Notes

- The bug was reported with reflog evidence; the same pattern exists in this repo's own history (`df48833` referenced by Task 77 is unreachable; `aa72dc7` from Task 75 is orphaned).
- Preferred fix direction: eliminate the amend entirely (two-commit flow: feature commit + `chore: close task N` closure commit). The amend-based "capture hash after amend" alternative leaves the tree dirty and still orphans H1, so it was rejected.
- The system prompt already documents the ZAC lifecycle (CRITICAL RULE 2 in `<bash_phase>`), so no system-prompt change is required for the compliance gap — that was a Zen Router project issue, not this repo.
- Deployment note: `~/.config/opencode/mcp-context-server/server.py` (global copy for other projects) is NOT modified by this task; the local `opencode.json` already points at this repo's server via `uv run mcp-context-server/server.py`.

## Local TODOs

- [x] Rewrite `commit_and_clean_task` in `mcp-context-server/server.py` — remove amend, add closure commit + idempotency guard
- [x] Fix `stage_and_inject_diff` crash on ignored `context-reports/` (negative pathspec → `git add` + `git reset` defense)
- [x] Add regression tests for both fixes
- [x] Run full test suite and verify all criteria (reachability, no amend, idempotency, staging)
- [x] Update CHANGELOG.md and close this task

## Acceptance Criteria

- [x] The hash stored in the task file equals the feature commit hash and is reachable from HEAD after `commit_and_clean_task` returns (`git merge-base --is-ancestor <hash> HEAD` succeeds).
- [x] `git show <stored_hash>` returns the diff that includes the code changes.
- [x] No commit becomes orphaned after a normal task closure (no `commit (amend)` entries in reflog).
- [x] Calling `commit_and_clean_task` twice on the same task does not create a second commit (idempotency guard).

## Verification Evidence

- **Test command:** `uv run --with "mcp>=1.0,<2.0" --with pathspec --with pyyaml --with pytest pytest tests/test_mcp_servers.py -q`
- **Expected result:** 6 tests pass, including the new `test_commit_and_clean_task_stores_reachable_hash`
- **Actual result:** `6 passed in 1.85s`
- **Exit code:** 0

## Risk & Rollback

- **Risk:** The tool now produces two commits per closure (feature + close) instead of one amended commit; commit count per closure increases, but no orphans are created and the `chore: close task N` pattern already exists in this repo's history.
- **Rollback plan:** Revert `mcp-context-server/server.py` to the previous amend-based implementation; the idempotency guard and closure-commit behavior are self-contained in the one function.

---

## OpenCode Execution Log & Reasoning

### Execution Summary

**Root cause confirmed:** `commit_and_clean_task` captured `git rev-parse HEAD` (H1) *before* `git commit --amend --no-edit`. The amend replaced H1 with H2, leaving the stored H1 orphaned (reachable only via reflog, ~30 days). Repo evidence: reflog shows `df48833` (referenced in Task 77's log) and `aa72dc7` are unreachable from HEAD.

**Fix (architectural reasoning):** An amend-based flow cannot satisfy both "stored hash == HEAD" and "no orphans" — writing the hash into the file before amending stores a stale hash, while capturing it after amending leaves the file edit uncommitted (dirty tree) and still orphans H1. The only clean design is a **two-commit flow**:

1. `git commit -m <message>` → feature commit H1
2. `git rev-parse HEAD` → store H1
3. Clean task file diff block → `**Factual Git Diff:** Stored in Commit Hash: H1`
4. `git add -A tasks/` (keeps the Task 47 fix for kanban moves/deletions)
5. `git commit -m "chore: close <slug>"` → closure commit; H1 stays permanently reachable as its parent

Also added:
- **Idempotency guard** (checks for existing `Stored in Commit Hash:` before the empty-staged check) — prevents double-commit on repeated calls.
- **`_derive_task_slug`** helper — builds the `chore: close task NN - <slug>` message from the task filename, matching the repo's existing close-commit convention.
- **Removed the upstream-push amend warning** — no longer applicable since the tool never amends.
- The empty-staged safety check from Task 71 is retained.

**Files modified:**
- `mcp-context-server/server.py` — rewritten `commit_and_clean_task` + new `_derive_task_slug` helper; also fixed `stage_and_inject_diff` (see below)
- `tests/test_mcp_servers.py` — added regression tests covering reachability, no-amend history, `git show` of the stored hash, idempotency, and staging with an ignored `context-reports/` dir
- `CHANGELOG.md` — [Unreleased] Fixed entry

### Second bug found & fixed (same pipeline): `stage_and_inject_diff` crash on ignored `context-reports/`

While closing this task, the MCP `stage_and_inject_diff` tool failed with exit 1:
`The following paths are ignored by one of your .gitignore files: context-reports`.

**Root cause:** the tool ran `git add . :!*.env :!*.env.* :!*.key :!*.pem :!credentials* :!secrets* :!context-reports/ :!.opencode/cache/`. When any excluded path *actually exists on disk and is ignored* (the `context-reports/` directory had accumulated reports from earlier sessions), git treats the pathspec match against the ignored path as an error and exits 1 — even though nothing is staged. This blocked every subsequent closure until the reports were deleted. (Verified: plain `git add .` exits 0; adding `--ignore-errors` does NOT suppress this error.)

**Fix:** replace the negative-pathspec `git add` with plain `git add -A .` (which already respects .gitignore) followed by defense-in-depth unstaging of sensitive patterns via `git reset -q -- <pattern>` (`*.env`, `*.key`, `*.pem`, `credentials*`, `secrets*`, `context-reports/`, `.opencode/cache/`). Verified: exit 0, correct staging, no sensitive/ignored files staged.

### Third fix: idempotency guard false-positive (self-referential diff)

After the first restart, `stage_and_inject_diff` succeeded (staging fix confirmed live), but `commit_and_clean_task` returned "Task file already cleaned" without committing. Root cause: the guard's naive substring search (`if "Stored in Commit Hash:" in existing`) matched the task file's own injected raw diff — the diff contained the guard's source line (`if "Stored in Commit Hash:" in existing:`) and the CHANGELOG mention of the phrase. The guard saw its own code and blocked the closure.

**Fix:** the guard now matches only the exact cleaned-block structure (`<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 081f427..02ec023 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -6,6 +6,11 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ## [Unreleased]
 
+### Fixed
+
+- **Orphaned commit hash bug in `commit_and_clean_task`** — The tool captured the commit hash *before* `git commit --amend`, so the hash stored in the task file pointed to a commit that became unreachable after the amend replaced it. Reworked the tool to a two-commit flow: the feature commit hash is captured and stored in the task file, then the cleaned task file is committed as a separate `chore: close task N` closure commit. The stored hash is now permanently reachable from HEAD, `git show <hash>` returns the real code diff, and no amend/orphaned commits are produced. The idempotency guard matches the exact cleaned-block structure (regex), so a raw injected diff that merely mentions "Stored in Commit Hash" (e.g. this very changelog entry or the guard's own source line) cannot false-positive and block a legitimate closure. Regression tests: `test_commit_and_clean_task_stores_reachable_hash`, `test_commit_and_clean_task_guard_no_false_positive_on_diff_mention`.
+- **`stage_and_inject_diff` crash when an ignored `context-reports/` directory exists** — the tool staged with `git add . :!...` negative pathspecs, which makes git exit 1 with "paths are ignored" whenever an excluded path actually exists on disk (the accumulated `context-reports/` reports), blocking every closure until deleted. Replaced with plain `git add -A .` (gitignore-respected) plus defense-in-depth `git reset -q -- <pattern>` for the sensitive/ignored paths. Regression test: `test_stage_and_inject_diff_with_ignored_context_reports`.
+
 ## [8.0.0] - 2026-08-04
 
 ### Added
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index acbb444..5e0eef2 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -405,13 +405,16 @@ def extract_signatures(file_path: str) -> str:
 def stage_and_inject_diff(task_file_path: str) -> str:
     """Stages current changes via Git and intelligently injects the diff into the task file's Git Diff block."""
     try:
-        # 1. Stage all changes EXCEPT known dangerous patterns
-        subprocess.run([
-            "git", "add", ".",
-            ":!*.env", ":!*.env.*", ":!*.key", ":!*.pem",
-            ":!credentials*", ":!secrets*",
-            ":!context-reports/", ":!.opencode/cache/"
-        ], check=True, capture_output=True)
+        # 1. Stage all changes. Plain `git add -A .` respects .gitignore.
+        #    Negative pathspecs (`:!...`) make `git add` fail with
+        #    "paths are ignored" whenever an ignored path (e.g.
+        #    context-reports/) exists on disk, so sensitive files are instead
+        #    unstaged afterwards via explicit reset patterns (defense-in-depth
+        #    for non-ignored secret files).
+        subprocess.run(["git", "add", "-A", "."], check=True, capture_output=True)
+        for pat in ["*.env", "*.env.*", "*.key", "*.pem", "credentials*",
+                    "secrets*", "context-reports/", ".opencode/cache/"]:
+            subprocess.run(["git", "reset", "-q", "--", pat], capture_output=True)
         
         # 2. Extract the diff (EXCLUDING the entire tasks/ directory to prevent recursive diff bloat)
         # Using git pathspec magic ':!tasks/' to ignore the entire task folder
@@ -447,53 +450,72 @@ def stage_and_inject_diff(task_file_path: str) -> str:
     except Exception as e:
         return f"❌ Error staging or updating task file: {str(e)}"
 
+def _derive_task_slug(task_file_path: str) -> str:
+    """Derives a 'task <NN> - <slug>' label from a task file name (e.g. '78-fix-bug.md' -> 'task 78 - fix bug')."""
+    name = Path(task_file_path).stem
+    parts = re.split(r"[-_]", name, maxsplit=1)
+    if len(parts) == 2 and parts[0].isdigit():
+        return f"task {parts[0]} - {parts[1].replace('-', ' ')}"
+    return f"task - {name.replace('-', ' ')}"
+
 @mcp.tool()
 def commit_and_clean_task(task_file_path: str, commit_message: str) -> str:
-    """Commits staged changes, captures the commit hash, replaces the raw diff in the task file with the hash to save space, and amends the commit to include the cleaned task file."""
+    """Commits staged changes, captures the feature commit hash, replaces the raw diff in the task file with the hash reference, and commits the cleaned task file as a separate closure commit. The stored hash always points to the feature commit, which stays reachable forever (no amend, no orphaned commits)."""
     try:
-        # 0. Safety checks before commit
+        # 0. Idempotency guard: skip if the task file was already cleaned.
+        #    Placed first so a cleaned task file short-circuits even on a clean tree.
+        #    Must match the EXACT cleaned-block structure, not a bare substring:
+        #    a raw injected diff can itself mention 'Stored in Commit Hash' (e.g.
+        #    the diff of this very guard or its CHANGELOG entry), causing a false
+        #    positive that blocks legitimate closures.
+        path = Path(task_file_path)
+        if path.is_file():
+            with open(path, 'r', encoding='utf-8') as f:
+                existing = f.read()
+            cleaned_block = re.compile(
+                r'<!-- BEGIN_GIT_DIFF -->\s*\*\*Factual Git Diff:\*\* Stored in Commit Hash: `[0-9a-f]{7,40}`\s*<!-- END_GIT_DIFF -->',
+                re.DOTALL
+            )
+            if cleaned_block.search(existing):
+                return "⚠️ Task file already cleaned (Stored in Commit Hash present). Nothing to commit."
+
+        # 0.5 Safety check before commit
         staged_check = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
         if staged_check.returncode == 0:
             return "⚠️ No staged changes to commit."
 
-        # 1. Commit staged changes
+        # 1. Commit staged changes (feature commit H1)
         subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True)
-        
-        # 2. Get the commit hash
+
+        # 2. Capture H1 — the feature commit hash. It stays reachable forever
+        #    as the parent of the closure commit (step 5). NEVER amend it.
         hash_proc = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
         commit_hash = hash_proc.stdout.strip()
-        
-        # 3. Read task file and clean diff
-        path = Path(task_file_path)
+
+        # 3. Read task file and replace raw diff with the hash reference
         if path.is_file():
             with open(path, 'r', encoding='utf-8') as f:
                 content = f.read()
-                
+
             pattern = re.compile(r'<!-- BEGIN_GIT_DIFF -->.*<!-- END_GIT_DIFF -->', re.DOTALL)
             if pattern.search(content):
                 clean_block = f"<!-- BEGIN_GIT_DIFF -->\n**Factual Git Diff:** Stored in Commit Hash: `{commit_hash}`\n<!-- END_GIT_DIFF -->"
                 new_content = pattern.sub(clean_block, content)
-                
+
                 with open(path, 'w', encoding='utf-8') as f:
                     f.write(new_content)
-                    
-                # 4. Stage the cleaned task file and amend
-                subprocess.run(["git", "add", "-A", "tasks/"], check=True, capture_output=True)
-                # Safety check: warn if amending pushed history
-                upstream_check = subprocess.run(
-                    ["git", "rev-parse", "--abbrev-ref", "@{upstream}"],
-                    capture_output=True, text=True
-                )
-                if upstream_check.returncode == 0:
-                    ahead_check = subprocess.run(
-                        ["git", "rev-list", "--count", "@{upstream}..HEAD"],
-                        capture_output=True, text=True
-                    )
-                    if int(ahead_check.stdout.strip()) > 0:
-                        print("⚠️ Warning: Amending a pushed commit. Ensure you know what you are doing.", file=sys.stderr)
-                subprocess.run(["git", "commit", "--amend", "--no-edit"], check=True, capture_output=True)
-                
-        return f"✅ Success: Code committed (Hash: {commit_hash}). Task file {task_file_path} cleaned and amended."
+
+        # 4. Stage the cleaned task file (catches moves/deletions under tasks/)
+        subprocess.run(["git", "add", "-A", "tasks/"], check=True, capture_output=True)
+
+        # 5. Commit the cleaned task file as a separate closure commit.
+        #    A plain commit (NOT --amend) keeps H1 reachable from HEAD.
+        slug = _derive_task_slug(task_file_path)
+        staged_after = subprocess.run(["git", "diff", "--staged", "--quiet"], capture_output=True)
+        if staged_after.returncode != 0:
+            subprocess.run(["git", "commit", "-m", f"chore: close {slug}"], check=True, capture_output=True, text=True)
+
+        return f"✅ Success: Code committed (Hash: `{commit_hash}`). Task file {task_file_path} cleaned; closure commit `chore: close {slug}` created on top."
     except subprocess.CalledProcessError as e:
         return f"❌ Git Error: {e.stderr}"
     except Exception as e:
diff --git a/tests/test_mcp_servers.py b/tests/test_mcp_servers.py
index ba3fbb1..7c3acf4 100644
--- a/tests/test_mcp_servers.py
+++ b/tests/test_mcp_servers.py
@@ -151,3 +151,215 @@ Test
     assert any("Acceptance Criteria" in i for i in issues), (
         "Missing section detection for Acceptance Criteria"
     )
+
+
+def test_commit_and_clean_task_stores_reachable_hash():
+    """Verify commit_and_clean_task stores a reachable commit hash (no orphaned pre-amend hash).
+
+    Regression test: the tool previously captured HEAD before `git commit --amend`,
+    so the hash written into the task file pointed to a commit that became
+    unreachable after the amend replaced it.
+    """
+    import importlib
+    import os
+    import subprocess
+    import tempfile
+
+    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
+    spec = importlib.util.spec_from_file_location("context_server_cc", server_path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+
+    with tempfile.TemporaryDirectory() as repo_dir:
+        repo = Path(repo_dir)
+
+        # Set up a git repo with a known identity
+        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
+        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
+        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
+
+        # Code change + task file with diff markers
+        (repo / "feature.py").write_text("x = 1\n")
+        task_file = repo / "tasks" / "completed" / "78-fix-bug.md"
+        task_file.parent.mkdir(parents=True)
+        task_file.write_text(
+            "# Task 78: Fix bug\n\n## Factual Git Diff\n\n"
+            "<!-- BEGIN_GIT_DIFF -->\n```diff\n+feature\n```\n<!-- END_GIT_DIFF -->\n"
+        )
+        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
+
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            result = mod.commit_and_clean_task(str(task_file), "fix: repair bug")
+        finally:
+            os.chdir(old_cwd)
+        assert "✅ Success" in result, result
+
+        # Task file must reference a commit hash
+        cleaned = task_file.read_text()
+        assert "Stored in Commit Hash:" in cleaned, "Task file should reference the commit hash"
+        stored_hash = None
+        for line in cleaned.splitlines():
+            if "Stored in Commit Hash:" in line and "`" in line:
+                stored_hash = line.split("`")[1]
+        assert stored_hash, "Could not parse stored commit hash"
+
+        # Closure commit sits on top; stored hash must still be reachable
+        head = subprocess.run(
+            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
+        ).stdout.strip()
+        assert stored_hash != head, "Closure commit should sit on top of the feature commit"
+        ancestry = subprocess.run(
+            ["git", "merge-base", "--is-ancestor", stored_hash, "HEAD"],
+            cwd=repo, capture_output=True,
+        )
+        assert ancestry.returncode == 0, f"Stored hash {stored_hash} is orphaned/unreachable"
+
+        # No amend commits in history
+        log = subprocess.run(
+            ["git", "log", "--oneline", "-3"], cwd=repo, capture_output=True, text=True
+        ).stdout
+        assert "amend" not in log, f"History must not contain amend commits:\n{log}"
+
+        # git show <stored_hash> still returns the feature diff
+        shown = subprocess.run(
+            ["git", "show", stored_hash, "--stat"], cwd=repo, capture_output=True, text=True
+        ).stdout
+        assert "feature.py" in shown, "git show <stored_hash> should return the code diff"
+
+        # Idempotency: second call must not create more commits
+        before = subprocess.run(
+            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
+        ).stdout.strip()
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            second = mod.commit_and_clean_task(str(task_file), "fix: repair bug")
+        finally:
+            os.chdir(old_cwd)
+        assert "already cleaned" in second, second
+        after = subprocess.run(
+            ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True
+        ).stdout.strip()
+        assert before == after, "Idempotency guard should prevent double commits"
+
+
+def test_commit_and_clean_task_guard_no_false_positive_on_diff_mention():
+    """The idempotency guard must NOT trigger when the raw diff merely mentions 'Stored in Commit Hash:'.
+
+    Regression test: a naive substring check matched the guard's own source line
+    (`if "Stored in Commit Hash:" in existing:`) once that diff was injected into
+    the task file, blocking the closure. The guard must only match the exact
+    cleaned-block structure between the BEGIN/END markers.
+    """
+    import importlib
+    import os
+    import subprocess
+    import tempfile
+
+    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
+    spec = importlib.util.spec_from_file_location("context_server_fp", server_path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+
+    with tempfile.TemporaryDirectory() as repo_dir:
+        repo = Path(repo_dir)
+        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
+        subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
+        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
+
+        (repo / "feature.py").write_text("x = 1\n")
+        # Raw diff that itself contains the guard's phrase AND the exact
+        # clean-block f-string literal (but with {commit_hash}, not a real hash)
+        raw_diff = (
+            "```diff\n"
+            "+            if \"Stored in Commit Hash:\" in existing:\n"
+            "+**Factual Git Diff:** Stored in Commit Hash: `{commit_hash}`\n"
+            "```\n"
+        )
+        task_file = repo / "tasks" / "79-fp-guard.md"
+        task_file.parent.mkdir()
+        task_file.write_text(
+            "# Task 79: Guard FP\n\n## Factual Git Diff\n\n"
+            "<!-- BEGIN_GIT_DIFF -->\n" + raw_diff + "<!-- END_GIT_DIFF -->\n"
+        )
+        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
+
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            result = mod.commit_and_clean_task(str(task_file), "fix: guard fp")
+        finally:
+            os.chdir(old_cwd)
+        assert "✅ Success" in result, result
+        assert "already cleaned" not in result, "Guard must not false-positive on raw diff mentions"
+
+        # The stored hash must reference the committed code (reachable, not orphaned)
+        cleaned = task_file.read_text()
+        stored_hash = None
+        for line in cleaned.splitlines():
+            if "Stored in Commit Hash:" in line and "`" in line:
+                stored_hash = line.split("`")[1]
+        assert stored_hash, "Could not parse stored commit hash"
+        ancestry = subprocess.run(
+            ["git", "merge-base", "--is-ancestor", stored_hash, "HEAD"],
+            cwd=repo, capture_output=True,
+        )
+        assert ancestry.returncode == 0, f"Stored hash {stored_hash} is orphaned/unreachable"
+
+
+def test_stage_and_inject_diff_with_ignored_context_reports():
+    """Verify stage_and_inject_diff succeeds even when an ignored context-reports/ dir exists.
+
+    Regression test: the old `git add . :!context-reports/` pathspec made git
+    fail with "The following paths are ignored..." whenever the ignored
+    directory existed on disk, blocking the entire closure flow.
+    """
+    import importlib
+    import os
+    import subprocess
+    import tempfile
+
+    server_path = Path(__file__).parent.parent / "mcp-context-server" / "server.py"
+    spec = importlib.util.spec_from_file_location("context_server_stage", server_path)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+
+    with tempfile.TemporaryDirectory() as repo_dir:
+        repo = Path(repo_dir)
+        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
+
+        # Ignored context-reports/ directory exists on disk
+        (repo / ".gitignore").write_text("context-reports/\n")
+        report_dir = repo / "context-reports"
+        report_dir.mkdir()
+        (report_dir / "context_report_x.md").write_text("ignored content\n")
+
+        # Code change + task file with diff markers
+        (repo / "feature.py").write_text("x = 1\n")
+        task_file = repo / "tasks" / "78-fix-bug.md"
+        task_file.parent.mkdir()
+        task_file.write_text(
+            "# Task 78: Fix bug\n\n## Factual Git Diff\n\n"
+            "<!-- BEGIN_GIT_DIFF -->\n<!-- END_GIT_DIFF -->\n"
+        )
+
+        old_cwd = os.getcwd()
+        os.chdir(repo)
+        try:
+            result = mod.stage_and_inject_diff(str(task_file))
+        finally:
+            os.chdir(old_cwd)
+        assert "✅ Success" in result, result
+
+        # Task file now contains the injected diff
+        assert "feature.py" in task_file.read_text(), "Diff should be injected into the task file"
+
+        # The ignored report must not be staged; the code change must be
+        staged = subprocess.run(
+            ["git", "diff", "--cached", "--name-only"], cwd=repo, capture_output=True, text=True
+        ).stdout
+        assert "feature.py" in staged, "Code change should be staged"
+        assert "context-reports" not in staged, "Ignored reports must not be staged"
+        assert "context_report_x.md" not in staged, "Report content must not be staged"
```
<!-- END_GIT_DIFF -->
