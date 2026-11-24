---
tags: [release, prompts, stage-artifacts]
---

Every release that changes prompt fragments must regenerate both the full prompt and all stage prompts before global install.

Rule: In each release cycle, run `python3 scripts/prompt-build/assemble_system_prompt.py` and then `python3 scripts/prompt-build/assemble_system_prompt.py --stages`. Copy `system-prompt.md` and all `build/stage-prompts/system-prompt.*.md` to the global install. A release is not complete if any stage artifact is stale or lacks the current fragment delta. Reason: Brain Bridge prefers stage artifacts when present, so stale stage prompts silently bypass the new full-prompt contract. Scope: Cognitive Lead AI HQ release workflow and global install sync.
