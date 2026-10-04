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

## Session-first chat history

The LLM is stateless, so the bridge keeps a JSONL transcript per
**session** under `BRAIN_SESSIONS_ROOT`
(default `~/.config/opencode/brain-sessions`), capped at the last
40 messages. Pass `session_id` (e.g. `sess-1`) alongside `task_id` and
every call loads the full session conversation first, then appends both
new turns. One session thread spans every task in the work session or
sprint — planning, implementation, QA, and review all share the same
context. A bare `task_id` with no `session_id` falls back to the
task-keyed transcript for backward compatibility.

The transcript is replayed on every later turn, so a stored turn
must stay small. The user turn is therefore stored in compact form:
the caller's own prompt plus one `[stored-attachment kind=… path=…
shown_chars=… total_chars=… part=a/b]` marker line per attachment,
never the attachment bodies. Persisting the bodies made each turn
re-pay the previous turn's attachments — a single QA turn stored a
64,547-char user turn and every turn after it inherited that cost.
The wire prompt is unaffected: the full content is re-derived from
disk each turn (task file, diff, `context_paths`, bundle), so the
Brain sees the same evidence while storage stays flat.

The transcript file is append-only: every turn ever written stays on
disk. Only the load VIEW is compacted in memory — one deterministic
digest record plus the newest records — so a task keeps its full
history while the send path stays bounded. The earlier lossy rewrite
(which replaced the file with the digest) was removed. This matches
the industry pattern: OpenCode, Claude Code, and Codex all persist the
full transcript and compact only what they send; OpenCode keeps full
session history in SQLite.

## File pulls (Hands native tools)

The Brain cannot read the Hands' disk — it only sees what a `brain_turn`
call carries. The Hands close that gap with their own native OpenCode
tools (`read`, `grep`, `glob`): the Brain quotes needed paths and the
Hands pull the content into the next turn as fed-context. The bridge
exposes exactly one tool, `brain_turn`; the former server-side helpers
(`get_context_bundle`, `read_file`, `grep_files`) were removed. The
five-file context bundle still auto-attaches on every turn (unless the
caller passes `include_bundle=false`): `agents/cognitive-executor.md`,
`docs/conventions.md`, `docs/architecture.md`, `docs/data_model.md`,
`DESIGN.md` in one labeled section. Missing files become `[missing:
path]` lines (never raise, per the Absent-File Policy). Each file caps
at 60,000 chars with a `[truncated]` marker.

Budget-aware assembly: Hands grep first to locate, then pull only the
ranges that fit the remaining budget. The bundle caps (60,000/file)
plus the 1,000,000-char input budget keep every call measurable.
History is never truncated to fit — the shipped thread is already
bounded at load (last 40 messages).

Export mapping: the main entry is implemented as `brain_turn` in
`mcp-brain-bridge/server.py` and exposed to operators as
`default.brain_brain_turn`. Internal ledger checkpointing stays a private
helper and is not a public tool.

## Environment

These variables are read from the server's self-loaded `.env` (search
order `<server-dir>/.env` → `<server-dir>/../.env` → `<cwd>/.env`; for the
global install that is **`~/.config/opencode/.env`**, for repo runs the
repo-root `.env`). Real process env wins; blank counts as unset. See
`docs/services.md` §Credentials.

| Variable            | Default                                              |
| ------------------- | ---------------------------------------------------- |
| `BRAIN_API_BASE`    | _(Manager-owned endpoint, e.g. local proxy URL)_     |
| `BRAIN_API_KEY`     | _(Manager-owned, never committed)_                   |
| `BRAIN_MODEL`       | `gpt-6-astra`                   |
| `BRAIN_REASONING_EFFORT` | `medium`                                         |
| `BRAIN_MAX_TOKENS`  | `32768`                                              |
| `BRAIN_SYSTEM_PROMPT` | `~/.config/opencode/system-prompt.md`              |
| `BRAIN_SESSIONS_ROOT` | `~/.config/opencode/brain-sessions`                |
| `DECISION_MODEL`    | _(falls back to `BRAIN_MODEL` default)_              |
| `DECISION_TEMPERATURE` | `1.0`                                             |
| `BRAIN_RISK_ROUTING_ENABLED` | `true` (routing ON; set a falsy value to disable) |
| `BRAIN_MODEL_LOW`   | `deepseek/deepseek-v4.1-flash` for `T0` turns; **unset** = built-in default, **blank** = `BRAIN_MODEL` |
| `BRAIN_MODEL_HIGH`  | `openai/gpt-5.6-luna` for `T1`/`T2` turns; **unset** = built-in default, **blank** = `BRAIN_MODEL` |
| `BRAIN_STAGE_TIERS` | `plan:T2,review:T2,implement:T0,qa:T0,closure:T0`    |
| `BRAIN_TASK_ATTACH_CAP` | `60000` — task-file attachment chars; blank/unset = default |
| `BRAIN_TASK_DIFF_CAP` | `200000` — changed-hunks chars; blank/unset = default |
| `BRAIN_CTX_PER_FILE_CAP` | `60000` — per `context_paths` file; blank/unset = default |
| `BRAIN_CTX_TOTAL_CAP` | `200000` — all `context_paths` per turn; blank/unset = default |
| `BRAIN_INPUT_BUDGET` | `1000000` — input budget ceiling (system + prompt + history), chars |
| `BRAIN_MODEL_WINDOW_CHARS` | `200000` — utilization monitor only, never a send cap |

`BRAIN_INPUT_BUDGET` defaults to 1,000,000 chars (~217k input tokens at
the measured ~4.6 chars/token) — room for full context and diff reports
plus the whole session thread. Set `BRAIN_INPUT_BUDGET` to a smaller
positive integer to restore a tighter ceiling.

Every cap above follows the blank-means-unset rule: an unset **or blank**
variable applies the documented default, and a real non-empty value wins.
A malformed or non-positive value raises a configuration error instead of
being silently clamped.

## Attachment rendering (direct, no allocator)

Attachments enter whole — no allocator, no chunking, no part markers.
Each attachment is rendered directly against its own configured cap
(task/diff per-attachment caps, `context_paths` per-file plus one shared
total cap), with an inline `[...truncated ...]` note when a cap cuts.
The configured caps above bound a single attachment; the 1M input budget
bounds the whole turn, so stacked attachments can never overflow the
window. Conversation history is always attached in full (bounded at load
to the last 40 messages) and is never cut to fit.

Task file and diff blocks keep their stable labels:

```text
[task-file:200: tasks/qa/200-x.md]
```markdown
...working content (Factual Git Diff stripped)...
```
[changed-hunks:200: tasks/qa/200-x.md]
```diff
...verbatim hunks...
```
```

Context paths render as `[path-injected: <path>]` followed by content.

## Response payload: two truncation counters (both normally zero)

The result dict keeps the attachment/history loss fields for schema
stability — with direct rendering and no history dropping, both are
always empty:

- `history_turns_dropped` — always `0`: history is never cut to fit.
  `truncated_count` remains as the back-compat alias. Both are `0` on a
  capability-blocked turn.
- `attachments_truncated` — always `[]`: cap cuts are noted inline in
  the block, never as resume tokens.
- `attachment_parts` — always `[]`: no chunking, no resume metadata.
- `attachment_budget_chars` / `attachment_chars_used` /
  `attachment_chars_remaining` — used-char accounting for the turn.

A capability-blocked turn returns the same field set (with `status:
"REPORT"`), so callers never face two incompatible schemas.

## Routing

Risk-aware model routing is ON by default. The effective tier comes from
the turn `stage` unless an explicit `risk_tier` (`T0`/`T1`/`T2` per
`docs/conventions.md`) is passed to `brain_turn`, which always wins.
Stage defaults: `plan` and `review` → `T2` (high model), `implement`,
`qa` and `closure` → `T0` (low model); a missing stage maps to no tier
and falls back to `BRAIN_MODEL`, while an unknown stage is rejected by the
request preflight (`plan`, `implement`, `qa`, `review`, `closure` are the
allowed values). `T1` also routes to the high
model. Override the mapping with `BRAIN_STAGE_TIERS` (comma-separated
`stage:Tier` pairs merged onto the built-in default; unusable pairs are
ignored). Set `BRAIN_RISK_ROUTING_ENABLED` to a falsy value to disable
routing entirely — every turn then uses `BRAIN_MODEL`. Missing or invalid
tiers fail safe to `BRAIN_MODEL`. For the per-tier models the unset and
blank cases differ on purpose: leaving `BRAIN_MODEL_LOW`/`BRAIN_MODEL_HIGH`
unset applies their built-in defaults, while setting a key to a blank value
falls back to `BRAIN_MODEL`, so clearing an override never silently selects
the built-in routed model. Effort
and token behavior never change under routing. Each context-ledger row
records the selected `model` and the effective `risk_tier` (metadata only
— never prompt text, diffs, or keys).

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
