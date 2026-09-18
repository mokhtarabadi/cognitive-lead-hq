# Brain Bridge Runbook

One MCP server (`mcp-brain-bridge/`, tool `brain_turn`) replaces the
retired persona engine. The Hands calls it for every Brain turn
(QA, review, brainstorm, questions).

## How it works

1. **Hands builds the user prompt from machine state** — e.g.
   `QA engineer please make the adversarial testing` plus the
   attached task file contents.
2. **The bridge loads the system prompt** from the global install
   (`~/.config/opencode/system-prompt.md`, override via
   `BRAIN_SYSTEM_PROMPT`) and sends system + history + new prompt
   to the LLM over the OpenAI Responses API via httpx.
3. **Output comes back raw.** When it contains a structured block
   (`<hands_implementation_task>`, `<hands_discovery_task>`,
   `<hands_combined_task>`, `<failure_report>`, `<hotfix>`), the bridge returns
   `XML_EXTRACTED` with the block; otherwise `REPORT` with the text.
   Explicit ```xml fences count as real XML: when the unfenced scan finds
   nothing, allowlist tags inside ```xml bodies still extract (other
   fences stay documentation-only).
4. **Questions relay to the Manager.** A `QUESTION` verdict pauses
   the Hands until the Manager answers (Autopilot mode answers
   from `manager_decision` rulings instead — see below).

## Per-task chat history

The LLM is stateless, so the bridge keeps a JSONL transcript per
task under `BRAIN_SESSIONS_ROOT`
(default `~/.config/opencode/brain-sessions`), capped at the last
40 messages. Pass `task_id` (e.g. `190`) and every call loads the
full conversation first, then appends both new turns. Each task
keeps its own ChatGPT-style context from first message to close.

## File pull tools

The Brain cannot read the Hands' disk — it only sees what a `brain_turn`
call carries. The Hands close that gap with three server-side helpers.
The Brain never calls them directly: it quotes needed paths and the
Hands pull the content into the next turn.

- `get_context_bundle()` — assembles the five small files
  (`agents/cognitive-executor.md`, `docs/conventions.md`,
  `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md`) into one
  labeled bundle. Missing files become `[missing: path]` lines (never
  raise, per the Absent-File Policy). Each file caps at 60,000 chars
  with a `[truncated]` marker.
- `read_file(path, offset=1, limit=200)` — the Hands read any text file under the
  workspace root (the repo root, or `BRAIN_WORKSPACE_ROOT` when set) with
  numbered lines (1-indexed). Only the `system_prompt_path` override
  additionally allows the global install dir (`~/.config/opencode`). Hands pull task-file ranges
  on demand instead of pasting whole files. Text extensions only; the Brain
  must never be told to pull files itself.
- `grep_files(pattern, subdir=".")` — the Hands search files for a pattern, up
  to 30 `path:line: excerpt` hits, skipping banned directories.

Budget-aware assembly: Hands grep first to locate, then read only the ranges
that fit the remaining budget. The bundle caps (60,000/file) plus the
`brain_turn` 100,000-char history truncation keep every call measurable
(the bundle tests prove both legs: all five sections always present,
total size measured by construction).

Export mapping: the main entry is implemented as `brain_turn` in
`mcp-brain-bridge/server.py` and exposed to operators as
`default.brain_brain_turn`. Internal ledger checkpointing stays a private
helper and is not a public tool.

## Environment

| Variable            | Default                                              |
| ------------------- | ---------------------------------------------------- |
| `BRAIN_API_BASE`    | _(Manager-owned endpoint, e.g. local proxy URL)_     |
| `BRAIN_API_KEY`     | _(Manager-owned, never committed)_                   |
| `BRAIN_MODEL`       | `gpt-6-astra`                   |
| `BRAIN_REASONING_EFFORT` | `xhigh`                                         |
| `BRAIN_MAX_TOKENS`  | `16384`                                              |
| `BRAIN_SYSTEM_PROMPT` | `~/.config/opencode/system-prompt.md`              |
| `BRAIN_SESSIONS_ROOT` | `~/.config/opencode/brain-sessions`                |
| `DECISION_MODEL`    | _(falls back to `BRAIN_MODEL` default)_              |
| `DECISION_TEMPERATURE` | `1.0`                                             |
| `BRAIN_RISK_ROUTING_ENABLED` | `false` (routing OFF = single model)      |
| `BRAIN_MODEL_LOW`   | _(blank = `BRAIN_MODEL`; used for `T0` turns)_       |
| `BRAIN_MODEL_HIGH`  | _(blank = `BRAIN_MODEL`; used for `T1`/`T2` turns)_  |

## Routing

Risk-aware model routing is OFF by default: with no flags set, every
turn uses `BRAIN_MODEL` (default `gpt-6-astra`), effort `xhigh`, and
`16384` max tokens — exactly today's behavior. To enable, set
`BRAIN_RISK_ROUTING_ENABLED=true` plus `BRAIN_MODEL_LOW` and/or
`BRAIN_MODEL_HIGH`, then pass `risk_tier` (`T0`/`T1`/`T2` per
`docs/conventions.md`) on `brain_turn`. `T0` routes to the low model,
`T1`/`T2` to the high model; missing or invalid tiers fail safe to
`BRAIN_MODEL`, as do blank per-tier overrides. Effort and token
behavior never change under routing. Each context-ledger row records
the selected `model` and the `risk_tier` (metadata only — never prompt
text, diffs, or keys).

## Prompt-cache split

Every turn computes a provider-neutral split descriptor alongside the
unchanged wire payload: the stable prefix (system prompt + bundle +
task attach) hashes to `static_prefix_sha256` (memoized per identical
static inputs — a repeat costs zero new static hashes), and everything
per-turn (user input, path/diff/failsafe appends,
fed context, shipped history) hashes to `dynamic_suffix_sha256`.
Only hashes and fixed labels travel — never prompt text, diffs, keys,
or history content. The descriptor is returned as `prompt_cache_split`
on the turn result and recorded on each context-ledger row, so repeated
turns with an identical static hash share maximal prefix bytes for any
provider-side caching. The split is logical, not a rewrite: fed context
still prepends on the wire exactly as before. Framing schema v2
length-prefixes labels as well as payloads, so NUL-bearing history
roles (caller-controlled transcript text) can never alias another
segment list's bytes; the failsafe attach hashes in its own slot,
never merged into the diff slot.

## Autopilot + manager-decision

Autopilot mode (default OFF) runs the full state machine with zero
approvals. It decides what the Manager would decide by consulting
past rulings via the `manager_decision` skill and the
`manager_decisions` MCP server (`mcp-decision-server/`, restored
and live). Every new ruling the Manager makes is recorded there,
so autopilot gets smarter over time.

## Verify

```bash
rtk test uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q
```

Live calls need a valid `BRAIN_API_KEY` for the configured
`BRAIN_API_BASE`; without one the server returns `error` (HTTP 401
from the provider) instead of hanging.
