# Task 09: Exclude Tasks Directory from Git Diff

**Type:** improvement
**Status:** completed

## Goal

Optimize the `stage_and_inject_diff` MCP tool to exclude the entire `tasks/` directory from the generated staged git diff output, ensuring pristine, code-focused diffs.

## Manager's Notes

- Replace individual task file pathspec exclusion with global `:!tasks/` directory exclusion.
- Clean up unused `os.path.relpath` from `diff_cmd` mapping if applicable.
- Update CHANGELOG.md.

## Local TODOs

- [x] Create tasks/09-exclude-tasks-directory-from-git-diff.md
- [x] Update mcp-context-server/server.py to use ':!tasks/' pathspec
- [x] Update CHANGELOG.md

## OpenCode Execution Log & Reasoning

- Updated `stage_and_inject_diff` in `server.py` to use `:!tasks/` in `git diff`. This ignores the entire tasks folder from the diff while still staging it for the final commit.
- Simplified the command by removing the need for dynamic relative path calculations for git diff exclusion.
- Verified the Python syntax of the custom context MCP server.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 411a5f9..17f0ccb 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -120,6 +120,12 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 - **`documentation_phase`** in `system-prompt.md` — streamlined to manual logging in task file under `OpenCode Execution Log & Reasoning`.
 - **Code Reviewer persona** — now reviews based strictly on the "Factual Git Diff" block inside the task file, with iteration instructions for rejections.

+## [Unreleased]
+
+### Changed
+
+- **`stage_and_inject_diff` MCP tool** — optimized the staged git diff command to globally exclude the entire `tasks/` directory (`:!tasks/`) instead of just the single active task file, completely eliminating task history clutter from factual codebase reviews.
+
 ## [5.5.0] — 2026-06-08

 ### Added
diff --git a/mcp-context-server/server.py b/mcp-context-server/server.py
index 3735bc0..35f573c 100755
--- a/mcp-context-server/server.py
+++ b/mcp-context-server/server.py
@@ -241,10 +241,9 @@ def stage_and_inject_diff(task_file_path: str) -> str:
         # 1. Stage all changes
         subprocess.run(["git", "add", "."], check=True, capture_output=True)

-        # 2. Extract the diff (EXCLUDING the task file itself to prevent recursive diff bloat)
-        # Using git pathspec magic ':!path' with a RELATIVE path to ignore the task file
-        rel_path = os.path.relpath(task_file_path)
-        diff_cmd = ["git", "diff", "--staged", "--", ".", f":!{rel_path}"]
+        # 2. Extract the diff (EXCLUDING the entire tasks/ directory to prevent recursive diff bloat)
+        # Using git pathspec magic ':!tasks/' to ignore the entire task folder
+        diff_cmd = ["git", "diff", "--staged", "--", ".", ":!tasks/"]
         diff_process = subprocess.run(diff_cmd, capture_output=True, text=True)
         diff_text = diff_process.stdout.strip()
```

<!-- END_GIT_DIFF -->
