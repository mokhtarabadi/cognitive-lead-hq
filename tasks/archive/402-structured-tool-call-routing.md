# Task 402: Structured tool-call routing for the Brain output channel

**File:** `tasks/archive/402-structured-tool-call-routing.md`
**Source:** manager
**Type:** improvement
**Status:** superseded
**Superseded-By:** `403-bridge-chat-completions-plus-structured-tool-call-routing`
**Superseded-At:** `2026-11-15 08:37 UTC`
**Submitted:** 2026-11-14T08:35:00Z

## Goal

Give the Brain a structured tool-call channel instead of flattened text, so a consumer can dispatch a tool call programmatically rather than parse it out of prose.

## Manager's Notes

Follow-up recorded during task 401 review. The chat-completions bridge currently renders a `function_call` output item as `name(arguments)` plain text in `parse_responses_text`. That is a deliberate contract for the bridge, documented in `mcp-brain-bridge/DECISIONS.md` ADR-014, and must not be changed inside task 401.

## Local TODOs

- [ ] Define the structured output shape the Brain consumes for a tool call
- [ ] Decide whether the channel is a new return field or a parsed block
- [ ] Implement and test both upstream modes
- [ ] Update ADR-014 and the bridge README

## Acceptance Criteria

- [ ] A tool-call-only response is distinguishable from prose without text parsing
- [ ] Both `responses` and `chat_completions` modes produce the same structured shape
- [ ] Offline unit tests cover both modes

## Verification Evidence

_Pending implementation._

## Definition of Done

- [ ] Task file conforms to canonical V6 structure
- [ ] Verification evidence recorded with rtk
- [ ] CHANGELOG.md updated
- [ ] Staging and QA transition executed atomically

## Risk & Rollback

- **Risk:** A new output field changes what the Hands reads.
- **Mitigation:** Additive field only; the existing text channel stays unchanged.
- **Rollback:** Revert the field addition.

> **Superseded:** This task was bundled into META task `403-bridge-chat-completions-plus-structured-tool-call-routing` and archived on 2026-11-15 08:37 UTC. See `tasks/backlog/403-bridge-chat-completions-plus-structured-tool-call-routing.md` (or its Kanban successor) for the unified execution. History preserved via `git log --follow -- tasks/archive/402-structured-tool-call-routing.md`.

## Execution Log & Reasoning

_Pending._

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
<!-- END_GIT_DIFF -->
