---
created_at: '2026-10-02T20:41:30.603312+00:00'
status: active
tags: []
updated_at: '2026-10-02T20:41:30.603327+00:00'
---

# OpenCode plugin policy — Magic Compact adopted (2026-10-02, Task 287)
Supersedes the 2026-10-01 no-plugins policy (recorded in opencode_config/opencode_v2_upgrade_2026_09_26).
- One plugin is approved and installed: magic-compact@1.2.2 (lossless manual context compaction). Global opencode.json carries plugins: ["magic-compact"].
- Native OpenCode compaction stays enabled as the safety net: compaction: {auto: true, keep: {tokens: 20000}}.
- Install on a new machine: `opencode plugin add magic-compact@1.2.2` (LLM.txt §7.7). npm proxy caveat: ~/.npmrc proxy/https-proxy lines were commented out (dead 127.0.0.1:7890; mihomo now on 8118 behind auth; direct registry works). Without this the plugin install fails with NPMInstallFailedError.
- Rollback: `opencode plugin remove magic-compact`; native compaction continues without it.
- Upstream paused in favor of Operator Memory; the pinned release remains fully functional.
- System prompt fragment 22 (<compaction_protocol>) and agents/cognitive-executor.md carry the survival contract; docs/compaction.md is the full guide.
