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
   `<hands_combined_task>`, `<failure_report>`), the bridge returns
   `XML_EXTRACTED` with the block; otherwise `REPORT` with the text.
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
call carries. Three tools close that gap:

- `get_context_bundle()` — assembles the five small files
  (`agents/cognitive-executor.md`, `docs/conventions.md`,
  `docs/architecture.md`, `docs/data_model.md`, `DESIGN.md`) into one
  labeled bundle. Missing files become `[missing: path]` lines (never
  raise, per the Absent-File Policy). Each file caps at 60,000 chars
  with a `[truncated]` marker.
- `read_file(path, offset=1, limit=200)` — reads any file under the
  workspace root with numbered lines (1-indexed). Pull task-file ranges
  on demand instead of pasting whole files.
- `grep_files(pattern, subdir=".")` — searches files for a pattern, up
  to 30 `path:line: excerpt` hits, skipping banned directories.

Budget-aware assembly: grep first to locate, then read only the ranges
that fit the remaining budget. The bundle caps (60,000/file) plus the
`brain_turn` 100,000-char history truncation keep every call measurable
(the bundle tests prove both legs: all five sections always present,
total size measured by construction).

## Environment

| Variable            | Default                                              |
| ------------------- | ---------------------------------------------------- |
| `BRAIN_API_BASE`    | _(Manager-owned endpoint, e.g. local proxy URL)_     |
| `BRAIN_API_KEY`     | _(Manager-owned, never committed)_                   |
| `BRAIN_MODEL`       | `muse-spark-1.3-contributor-free`                   |
| `BRAIN_REASONING_EFFORT` | `xhigh`                                         |
| `BRAIN_MAX_TOKENS`  | `16384`                                              |
| `BRAIN_SYSTEM_PROMPT` | `~/.config/opencode/system-prompt.md`              |
| `BRAIN_SESSIONS_ROOT` | `~/.config/opencode/brain-sessions`                |
| `DECISION_MODEL`    | _(falls back to `BRAIN_MODEL` default)_              |
| `DECISION_TEMPERATURE` | `1.0`                                             |

## Autopilot + manager-decision

Autopilot mode (default OFF) runs the full state machine with zero
approvals. It decides what the Manager would decide by consulting
past rulings via the `manager_decision` skill and the
`manager_decisions` MCP server (`mcp-decision-server/`, restored
and live). Every new ruling the Manager makes is recorded there,
so autopilot gets smarter over time.

## Verify

```bash
uv run --project mcp-brain-bridge --with pytest pytest tests/test_brain_bridge.py -q
```

Live calls need a valid `BRAIN_API_KEY` for the configured
`BRAIN_API_BASE`; without one the server returns `error` (HTTP 401
from the provider) instead of hanging.
