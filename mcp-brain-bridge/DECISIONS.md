# Architectural Decisions: mcp-brain-bridge

## [2026-10-06] ADR-001: Initial Slice Baseline

- **Context:** Baseline documentation initialized via init-folder-docs.
- **Decision:** Adopting Living Folder Docs standard for this component.
- **Consequences:** All future structural or contract changes must be recorded here.
- **Rollback:** N/A (baseline adoption).

## [2026-10-12] ADR-002: Dual-mode XML extraction (bare + fenced fallback)

- **Context:** Manual copy-paste mode needs forced ```xml fences; automatic MCP mode needs bare XML. The strict fence reject forced a wasted re-emit turn.
- **Decision:** Bare unfenced blocks extract first; explicit ```xml fences extract second; other fences stay documentation-only; bare unclosed tails still strict-reject.
- **Consequences:** Both modes extract without re-emit; fence-fallback tests pin extraction.
- **Rollback:** Revert extract_xml_blocks fallback hunk and fence tests to strict-reject form.

## [2026-10-12] ADR-003: Pre-send token budget guard

- **Context:** A 943718-token output reservation plus ~106K input tokens exceeded the 1048576-token provider window as a hard 400 with no retry.
- **Decision:** Estimate input as chars divided by four, add live reserved output, compare against window minus margin; trim oldest history, then diffs and context, then bundle; persistent over-budget returns a BRAIN_BUDGET_OVER REPORT hint and skips the provider.
- **Consequences:** Oversize turns fail gracefully with numbers; 128K and 256K caps with xhigh keep working inside the window.
- **Rollback:** Revert the guard hunk plus hint helper plus eight tests.

## [2026-10-21] ADR-004: Responses API best-practice alignment

- **Context:** The 2026-10-21 audit found ten drifts from current official Responses practice in the single provider call site: no `store`, dropped reasoning items and `phase`, no `truncation`, no cache key, unread response `model`, retried billing 429s, raw-exception fatal 4xx, an effort ladder that could raise effort, silent token-cap fallback, and a role-form system prompt.
- **Decision:** Fix all ten behind per-parameter env switches defaulting to off (all six new wire parameters probed HTTP 200 against the live gateway first); validate effort against the official vocabulary; parse `error.code`/`error.type` with terminal billing codes; read `response.model`/`cached_tokens` into diagnostics; replay reasoning items and `phase` from version-tolerant transcripts; return structured REPORTs on fatal transport errors; fail loud on malformed numeric config.
- **Consequences:** Default wire bytes are unchanged until operators opt in; diagnostics expose model substitution and cache hits; transcripts stay backward compatible.
- **Rollback:** One-function revert of the request builder plus switch-off; diagnostics parser is pure and separately testable.
