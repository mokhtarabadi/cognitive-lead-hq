# Slice: mcp-brain-bridge

## Duties

Brain Bridge MCP daemon: single-tool (`brain_turn`) automation path for planning, QA, and review turns, plus session ledger, loop-spin guard, capability preflight, and request preflight.

## Files

- `server.py` — MCP daemon entrypoint exposing `brain_turn` (only automation path).
- `parse_brain_output.py` — Shared deterministic Hands helper for inspecting and validating one persisted artifact without executing its XML.
- `capability.py` — Capability preflight mapping required tools to AVAILABLE/UNAVAILABLE.
- `preflight.py` — Request validation (project_root must hold `tasks/`, memory binding).
- `loop_guard.py` — Diff-hash spin guard (same hash 3x stops autopilot fix loop).
- `session_ledger.py` — Append-only JSONL session event ledger under `tasks/.sessions/`.
- Per-turn artifacts: each `brain_turn` attempts to write `tasks/.sessions/<session>/brain_outputs/<resp>_<uuid>.json` (`xml_blocks` + full raw output); the result's `output_address` points at it for truncated-tail recovery. An artifact whose serialized JSON exceeds the 5 MB session byte cap is skipped before temp-file creation and yields `output_address = None` while the turn continues. Retention is capped at 50 files / 5 MB per session, oldest-first. Artifact writes and retention pruning are serialized within the bridge process (RLock); abandoned `.tmp-` files are removed before each new write.
- `pyproject.toml` / `uv.lock` — Runtime deps and lockfile (`mcp[cli]`, stdlib-first helpers).
- `context-reports/` — Generated context output (do not hand-read; feed via MCP).
- `context_paths` line slices: `brain_turn(context_paths=[...])` accepts
  a trailing `#Lstart-end` (inclusive 1-based lines) or `#Lstart-` (tail
  to EOF); out-of-range ends clamp, empty selections and malformed
  `#L` fragments on supported paths render as explicit `[unavailable: …]`
  labels. Unlisted-suffix files sniff as text only when valid UTF-8
  without NUL or disallowed Unicode control characters (tab, LF, CR,
  form feed allowed); anything else renders `[unavailable: …]`.

## Key Risks & Invariants

- Single-tool invariant: no second tool or slash-command path may bypass `brain_turn`.
- Helpers (`capability`, `loop_guard`, `preflight`) stay stdlib-only and importable without MCP runtime so tests stay offline.
- Session ledger is append-only; never rewrite history lines.
- Request-shape evolution stays opt-in: every new Responses parameter
  ships behind a `BRAIN_SEND_*` / `BRAIN_USE_INSTRUCTIONS` switch
  defaulting to off, so default wire bytes never change silently.

## Transport: LiteLLM, No Retries

Every turn goes through `litellm.responses(model="openai/<id>", api_base=BRAIN_API_BASE)`.

- The bridge pins `num_retries=0`. A failed turn returns a `PROVIDER_ERROR`
  report; deciding whether to try again belongs to the caller.
- `BRAIN_HTTP_READ_TIMEOUT` is the only in-flight bound. There is no retry
  ladder, no backoff, no rate-limit-code classifier, and no outer deadline.
- Provider failures keep `debug.provider` with status, code, and error type so
  the caller can reason about the failure.
- `parse_responses_text` renders `function_call` items as `name(arguments)`
  text; structured tool calls remain available through `tool_calls`.

## Deployed Runtime Configuration

The current deployment keeps `muse-spark-1.3-contributor` on the Responses mount
(`BRAIN_API_BASE=http://127.0.0.1:8081/go/resp`) with
`BRAIN_MODEL_LOW=muse-spark-1.3-contributor`,
`BRAIN_MODEL_HIGH=gpt-6-luna`, `BRAIN_REASONING_EFFORT=max`, and
`BRAIN_STAGE_TIERS=qa:T2,plan:T0,review:T2,sprint:T0,brainstorm:T2,implement:T0,closure:T0,planner:T0`.
The binding timeout ladder is `ZEN_BRIDGE_UPSTREAM_TIMEOUT=900s` ≤
`BRAIN_HTTP_READ_TIMEOUT=960s` ≤ the MCP client execution timeout
(`1500000ms`). There is no outer deadline: the bridge does not retry, so the
read timeout is the only in-flight bound.

## Stage System Prompts

`brain_turn(stage=...)` selects the system prompt the Brain receives. The routing table is `prompts/stage-manifest.json` in the repository — the same file the assembler uses to generate the artifacts — so a stage is declared once and both sides agree on it. `resolve_stage_prompt_path(stage)` is pure and side-effect free: it returns the artifact path for a known stage and `None` for an unknown or empty stage.

Each stage ships its declared lead persona block(s) — one for qa, review, implement, closure, sprint, and planner; five for plan; seven for brainstorm — plus the full seven-seat roster and the `auto_load` Layer 3 adoption rule, so a turn can adopt another seat when the task needs it without carrying seven competing identities. One primary persona per system message is deliberate: multiple full persona blocks argue with each other and burn context on every turn.

Resolution order in `load_system_prompt`: explicit `system_prompt_path` → the stage artifact (repo copy first, then the `~/.config/opencode/` install) → `BRAIN_SYSTEM_PROMPT` → the full committed prompt. A stage artifact whose `<system_version>` differs from the current source is skipped with a stderr note and the full prompt serves; an explicit `system_prompt_path` override is never gated. A known stage whose artifact is missing on disk falls through to the full prompt with one stderr note; it never returns an empty prompt and never raises because of a stage. An unknown stage string is rejected loudly by the preflight gate (`PreflightError`) rather than silently downgraded, so a typo fails visible instead of quietly running unscoped. `preflight.ALLOWED_STAGES` accepts `plan`, `implement`, `qa`, `review`, `closure`, and `brainstorm`. A changed loader needs a Manager restart to take effect in the running singleton.

Measured artifact sizes: full 95428 bytes; plan 89690; implement 80991; qa 80140; review 80850; closure 80991; brainstorm 95428.

## Plan-Turn Sufficiency Grounding

The bridge builds its plan-turn sufficiency diagnostic from the user prompt and the rendered `fed` and `paths` slots. A non-empty server-rendered `paths` slot grounds the `no fed-context block` diagnostic through the caller-provided `has_server_paths` flag; a literal `[path-injected:]` string in user text does not count as server-rendered path context. The existing `[fed-context]` and `[pinned-fed-context]` markers remain supported by the Hands-fed context contract. This change affects the sufficiency diagnostic only and does not change the request payload or context-path limits.

Multi-project root resolution: when more than one project is active, every brain_turn call MUST pass project_root for the project that turn belongs to, or launch that project with BRAIN_PROJECT_ROOT set to that project's absolute path. Resolution order: the project_root parameter wins, then BRAIN_PROJECT_ROOT, then BRAIN_WORKSPACE_ROOT, then the bridge install directory. Reaching the install-directory fallback is a defect signal, not a feature — the bridge is a singleton on port 8105 and its install directory is shared by every project.

Resolution contract: see docs/brain-bridge.md, section Multi-Project Root Resolution.

## Oversized Output Path

Results above BRAIN_OUTPUT_INLINE_MAX arrive as pointers: the output field begins with the brain-output marker naming the artifact path (output_address), extracted XML moves to the same artifact under xml_blocks with block_count and an xml pointer line inline, and the output/xml_blocks strings keep their existing inline shape below the cap. Additive block_count and diagnostics metadata is present on every result. When no artifact address exists, nothing is stubbed. Full text under full_output, extracted blocks under xml_blocks.

## Raw Output Before Triage

The bridge captures immutable provider text before XML extraction, semantic validation, and hint or reject rewriting. The per-turn artifact persists that text under `full_output`; the inline result and replay transcript may instead carry a bounded preview plus `output_address`. Strict and semantic reject previews never replace the persisted raw text. Persistence remains best-effort: if the artifact cannot be written, `output_address` is `None`, `diagnostics.raw_persisted` is `false`, and the turn still returns its preview.

Artifacts add three fields without changing existing consumers:

- `block_count` (int): number of XML blocks retained for the turn; rejects retain zero.
- `raw_bytes` (int): UTF-8 byte length of the raw provider text.
- `diagnostics` (object):
  - `code`: strict reject code or `XML_SEMANTIC_REJECT`; `null` when no reject code applies.
  - `withheld_chars` (int): character-count gap between the raw text and the inline preview.
  - `raw_bytes` (int): UTF-8 byte length of the raw provider text.
  - `raw_persisted` (bool): whether the raw-text artifact write succeeded.

Hands inspects a persisted artifact with the shared deterministic helper from the project root:

```bash
python3 mcp-brain-bridge/parse_brain_output.py <artifact-path>
```

The helper re-parses `full_output`, applies the bridge's extraction and Hands semantic checks, and emits JSON containing `blocks`, `block_count`, `validation_problems`, and `executable`. It reports rather than executes content. Malformed, truncated, or contract-incomplete XML remains visible in the artifact but has `executable: false`; it is never repaired into an executable block. Legacy artifacts without the additive keys remain readable.

## Sprint and Planner Stages

sprint and planner are first-class stages alongside plan, implement, qa, review, closure, and brainstorm, present in the preflight enum, the routing manifest, and the stage tiers. Manager-term aliases (code review, planning) map to review and plan; the manifest description records the map. A regression test rejects any invalid stage literal in prompt-facing Markdown.
