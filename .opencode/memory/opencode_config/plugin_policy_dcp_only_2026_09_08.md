---
created_at: '2026-09-08T08:42:52.334419+00:00'
status: active
tags: []
updated_at: '2026-09-08T08:42:52.334445+00:00'
---

2026-09-08 (Task 165): goal plugin (@prevalentware/opencode-goal-plugin) removed from all 4 opencode configs (global + repo opencode.json/tui.json → dcp-only) and worktree loader disabled (~/.config/opencode/plugins/worktree-plugin.js → .disabled). Reason: OpenChamber Session Goals replace goal-plugin; reduce proc/RAM sprawl. Re-enable: restore goal line in the 4 JSONs; mv .disabled back. Supersedes Task 126 (goal install) + Task 164 (owt install) until Manager says otherwise.