---
created_at: '2026-09-17T17:20:56.311469+00:00'
status: active
tags: []
updated_at: '2026-09-17T17:20:56.311485+00:00'
---

RTK-first verification rule (Manager order 2026-09-17, structurally wired): every test-suite verification run begins with `rtk test <underlying command>`; record the exact prefixed command and exit code in the task's Verification Evidence. A raw rerun is allowed only after a failed RTK run for detailed diagnostics. Canonical rule: prompts/fragments/09-hands_protocols.md RULE 3b; executor policy: agents/cognitive-executor.md Verification Runner section; template prescribes `rtk test [exact command]`. Proven parity: full suite passes via both raw and rtk runs, exit 0.