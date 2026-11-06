# Slice: agents

## Duties

Defines the two OpenCode agent personas for the Cognitive Lead HQ: primary executor and read-only discovery subagent, including permissions, execution discipline, and Kanban rules.

## Files

- `cognitive-executor.md` — Primary execution engine persona (XML task execution, ZAC, Brain Bridge).
- `cognitive-discovery.md` — Read-only context-gathering subagent (MCP-first scans, no edits).

## Key Risks & Invariants

- Permission drift: executor allows edit/question, discovery denies edit/bash; never invert.
- Persona changes must stay in sync with `system-prompt.md` fragments and `prompts/` sources.
- Plan approval surface: an approval question is only valid after the full plan body is visible in the same turn, and the question payload repeats it. A bare "Approve the plan?" ask is a protocol bug.
- Brain results cross into the transcript whole: `status`, `output`, `xml_blocks` and diagnostic/`truncated` fields are never sliced, field-shaped or summarized on return. Size is managed before the call (`compact_context`, leaner prompt, `include_bundle=false`), never after.
- Discovery-fed grounding: a retry without verbatim code or `context_paths` predicts its own second `missing_context` — prose-only fed-context is a protocol violation.
- Context-Paths manifest invariant: every discovery report ends with a machine-readable `### Context Manifest` (`Context-Paths:` with `#Lstart-end` slices) that the executor feeds directly into `brain_turn(context_paths=[...])`.
- Code Mode execution standard: all MCP servers run under `codemode: true`; every tool call routes through `execute` as `tools.<server>.<tool>` with `project_root` on each call, and `brain_turn` results return whole.
- No runtime code here; changes are prompt-contract changes with system-wide effect.

### Free-tier bash gate

Custom agents must keep bash in the tool allowlist when the agent is expected to run on a free-tier model. Upstream free-tier models classify the caller by the request-body tool list. A call without bash is treated as third-party and receives 403 FreeTierError on free-tier models. Keep bash in the list for free-tier use. Harden behavior with scoped prompts and review, not with tool removal.

Review checklist addition:
- Free-tier smoke test before release: run the agent under review with opencode run using the --agent flag on a free-tier model and confirm a normal reply with no 403. Example with a known agent: opencode run --agent cognitive-executor --prompt smoke test reply OK. Repeat for each agent file found in opencode.json.
