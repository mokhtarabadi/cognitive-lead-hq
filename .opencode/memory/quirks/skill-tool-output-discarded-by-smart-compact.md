---
tags: [skills, smart-compact, opencode]
---
# Skill output must never be discarded or pruned

`smart-compact` `pruning.discardTools` replaced every `skill` call result with "Skill contents omitted after compaction", so agents got no skill body and fell back to filesystem searches. `skill` must stay OUT of `discardTools` and INSIDE `protectedTools`. Restart OpenCode after changing it; subagents also need `skill: allow` in their permission block or they have no skill tool at all.