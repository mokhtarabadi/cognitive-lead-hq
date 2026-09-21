# manager-decisions MCP Server

The `manager_decisions` server is the Cognitive Lead AI memory for Manager rulings. Agents call it to consult a stored decision before paging the human, and to persist a new ruling the Manager just made.

This document is the agent-facing usage contract: server identity, store resolution, every tool signature, the shared record schema, and the failure modes. It is written so an agent can call each tool correctly on the first try.

> **Revision note (pinned).** Every factual claim below was verified against source at commit `0183433ccec9cc9252f874060df5140c4618ecb4` (2026-09-20), read on 2026-09-21. Line citations were re-derived on 2026-09-21 after two fixes landed in the working tree (see Doc Drift): the write tool's `Args` block and the extraction prompt. `mcp-decision-server/server.py` is now 1838 lines, `redactor.py` is 85 lines, `detector.py` is 149 lines. If any of these files change again, re-verify before trusting a citation.

## Purpose and Scope

In scope here:

- The six MCP tools exposed by `mcp-decision-server/server.py`, with argument names, types, return shapes, side effects, and failure modes.
- The decision store layout and how the server picks a store.
- The decision-record field contract that `record_manager_decision` enforces.
- Known divergence between this server's source and the `manager-decision` skill text, reported as-is.

Out of scope: changing server behavior. The drift reported here was found by reading the source, not by changing it. When this page was first written, no source file and no skill file was modified; two drift items (D1 and D2) were fixed afterwards and are marked as such.

## Server Identity and Transport

| Property                  | Value                                     | Source                                                        |
| ------------------------- | ----------------------------------------- | ------------------------------------------------------------- |
| Server object             | `mcp = FastMCP("ManagerDecisions")`       | `mcp-decision-server/server.py:190`                           |
| Transport                 | stdio, entered under the `__main__` guard | `mcp-decision-server/server.py:1837-1838`                     |
| Package                   | `mcp-decision-server`, version `1.0.0`    | `mcp-decision-server/pyproject.toml:2-3`                      |
| Script entry point        | none declared                             | `mcp-decision-server/pyproject.toml` (no `[project.scripts]`) |
| Launch                    | `uv run mcp-decision-server/server.py`    | `docs/setup.md:59`                                            |
| Extraction model constant | `DEFAULT_DECISION_MODEL = "gpt-6-astra"`  | `mcp-decision-server/server.py:196`                           |
| Model override env        | `DECISION_MODEL`                          | `mcp-decision-server/server.py:265-275`                       |

**Model resolution correction.** The only model override for this server is the `DECISION_MODEL` environment variable. `_get_decision_model()` reads `DECISION_MODEL` first and otherwise returns `DEFAULT_DECISION_MODEL` (`mcp-decision-server/server.py:265-275`). `BRAIN_MODEL` is **never read** by this server — grep finds no reference to it anywhere in `mcp-decision-server/`. The code deliberately does not fall back to `PERSONA_MODEL` either; the reason is recorded inline at `mcp-decision-server/server.py:268`: a stale persona model value once hijacked extraction calls and caused 401s. Sibling variables that do carry a `BRAIN_` prefix are unrelated to model choice: `BRAIN_REASONING_EFFORT` (`mcp-decision-server/server.py:288`), `BRAIN_API_KEY` (`mcp-decision-server/server.py:363`), and `BRAIN_API_BASE` (`mcp-decision-server/server.py:399`).

## Store Resolution

`_repo_root()` (`mcp-decision-server/server.py:78`) picks the decision store in a fixed order and fails closed at the end:

1. **Explicit path.** `DECISION_REPO_PATH` wins if set to a non-blank value (`mcp-decision-server/server.py:92`). The directory is created with `mkdir(parents=True, exist_ok=True)` (line 95). If creation fails, the server raises `RuntimeError` and does **not** fall back — the message names the variable and advises fixing the path or unsetting it (`mcp-decision-server/server.py:95-104`, message at line 102).
2. **Per-project fallback.** Otherwise the server walks `(Path.cwd(), INSTALL_ROOT)` and tries `base / ".opencode" / "decisions"` for each (`mcp-decision-server/server.py:106-112`). A candidate that cannot be created is skipped with `OSError` (`continue`). `INSTALL_ROOT = Path(__file__).resolve().parent.parent` (`mcp-decision-server/server.py:75`).
3. **No writable location.** Exhausting both candidates raises `RuntimeError("cannot create a decision store: no writable location found")` (`mcp-decision-server/server.py:113`).

The server tells the operator which store is live. `_active_root_info(repo)` (`mcp-decision-server/server.py:116`) returns `personal repo (DECISION_REPO_PATH set)` (line 130) or `project fallback (DECISION_REPO_PATH unset)` (line 131). `record_manager_decision` prints this to stderr as `decision-server: active store: …` (`mcp-decision-server/server.py:1604`).

Two provenance fields are stamped on every record rather than left to the caller:

- `active_root = repo.name` — the repo **display name only**, never the absolute path (`mcp-decision-server/server.py:1621`).
- `store_mode` — `"personal"` when `DECISION_REPO_PATH` is set, else `"project-fallback"` (`mcp-decision-server/server.py:1622-1624`).

Full paths stay in local stderr logs and are never written into a record.

## Six-Tool Quick Reference

All six are decorated with `@mcp.tool()` in `mcp-decision-server/server.py`.

| Tool                        | Decorator / `def` | Signature                                                                                                                                      | Returns                                                      |
| --------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `extract_session_decisions` | `:1258` / `:1259` | `(task_id: Optional[Union[int, str]] = None, transcript_path: Optional[str] = None, session_id: Optional[str] = None) -> list[dict[str, Any]]` | list of candidate decision dicts, unscrubbed and unvalidated |
| `record_manager_decision`   | `:1551` / `:1552` | `(decision: dict[str, Any]) -> str`                                                                                                            | human-readable confirmation naming the record id             |
| `query_manager_decisions`   | `:1659` / `:1660` | `(query: str, category: Optional[str] = None) -> str`                                                                                          | formatted ranked summaries, or a no-match message            |
| `get_sync_status`           | `:1762` / `:1763` | `() -> str`                                                                                                                                    | active store plus sync-debt report                           |
| `get_manager_profile`       | `:1776` / `:1777` | `() -> str`                                                                                                                                    | the profile sample text, or an explanatory message           |
| `propose_profile_evolution` | `:1801` / `:1802` | `() -> dict[str, Any]`                                                                                                                         | `{"status": "DRAFT_READY"｜"EMPTY"｜"ERROR", "draft": str}`  |

Enum sheet used across tools and records:

| Field      | Allowed values                                                                                       | Where enforced                                              |
| ---------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `category` | `architecture`, `process`, `scope`, `quality-gate`, `tooling`, `release`, `other`, `autopilot-cycle` | `mcp-decision-server/server.py:959-962`                     |
| `fidelity` | `verbatim`, `reconstructed` (default `verbatim`)                                                     | `mcp-decision-server/server.py:896-900`, default at `:1612` |
| `mode`     | `manual`, `autopilot` (default `manual`)                                                             | `mcp-decision-server/server.py:896-900`, default at `:1612` |
| `scope`    | `standing`, `episode` (default `episode`)                                                            | `mcp-decision-server/server.py:896-900`, default at `:1613` |

## Tool Details

### `extract_session_decisions`

```python
extract_session_decisions(
    task_id: Optional[Union[int, str]] = None,
    transcript_path: Optional[str] = None,
    session_id: Optional[str] = None,
) -> list[dict[str, Any]]
```

**When to call.** At the end of every session in which the Manager ruled, chose, or constrained something, before closing the task (`mcp-decision-server/server.py:1264-1294`). Feed the output into `record_manager_decision`. The output is **unscrubbed and unvalidated** — it is only a candidate list.

**Arguments.**

- `task_id` — session scope as `tasks/.sessions/{task_id}/transcript.jsonl`. A numeric value resolves the numeric path.
- `session_id` — taskless session scope, sanitized before use (`mcp-decision-server/server.py:1249`).
- `transcript_path` — explicit override, mainly for tests and replays.

**Resolution order.** `transcript_path` wins if given (`mcp-decision-server/server.py:1296-1297`). Otherwise the scope is `session_id` or `task_id`; if both are `None` the tool raises `ValueError("decision extract: pass task_id or session_id (or transcript_path for replays)")` (`mcp-decision-server/server.py:1300-1304`). Numeric scope reads `tasks/.sessions/{int}/transcript.jsonl` (`mcp-decision-server/server.py:1312-1316`); a non-numeric session id is sanitized into `tasks/.sessions/{sanitized_sid}/transcript.jsonl` (`mcp-decision-server/server.py:1305-1311`).

**Return shape.** A JSON array of candidates, each item shaped as `{"verbatim_quote": {"original": …, "english_translation": …}, "extracted_decision": {"summary": …, "category": …, "rationale": …, "alternatives": [], "tradeoffs": …}}` (extraction prompt at `mcp-decision-server/server.py:1348-1356`).

**Side effects.** One LLM call to the `DECISION_MODEL` model. Reads a transcript; writes nothing.

**Failure modes.**

- Missing transcript file → returns `[]` gracefully, before the lazy LLM import runs (`mcp-decision-server/server.py:1317-1318`).
- Present but zero-turn transcript → raises `RuntimeError` (`mcp-decision-server/server.py:1330-1334`). A broken pipeline must not be mistaken for a quiet session.
- Malformed model output → raises `RuntimeError` (`mcp-decision-server/server.py:1264-1294`).
- No scope given, or an unsafe session id → raises `ValueError` (`mcp-decision-server/server.py:1300-1304`, `:1249`).
- Oversized transcript → capped by `_get_decision_transcript_max_chars()` with an explicit `[...truncated at N chars]` marker, never silently (`mcp-decision-server/server.py:1339-1347`).

### `record_manager_decision`

```python
record_manager_decision(decision: dict[str, Any]) -> str
```

**When to call.** Immediately after extraction returns candidates, or as soon as the Manager states a ruling mid-session — do not wait for session end (`mcp-decision-server/server.py:1553-1602`).

**Pipeline.** `sanitize_text` every free-text field → `verify_clean` gate → schema validation → write `.json` + `.md` → regenerate `INDEX.md`. The scrub gate fail-closes on every root, including an explicitly configured personal repo; there is no bypass flag (`mcp-decision-server/server.py:1553-1602`).

**Argument.** A single `decision` dict. The tool fills these when absent: `decision_id` (`mcp-decision-server/server.py:1608`), `timestamp` (`:1609`), `fingerprint` (`:1617-1619`), plus hardened defaults `fidelity="verbatim"`, `mode="manual"`, `scope="episode"`, `goal_ref=""` (`:1610-1616`). An explicit `None` counts as unset for those four, so a `None` never survives as a value.

> **Note.** `project_name` is **required** and is **not** defaulted (`mcp-decision-server/server.py:873-874`, `:1608-1619`). The `Args` block documents it with the rest of the record contract (`mcp-decision-server/server.py:1576-1594`), and an omission surfaces as `ValueError: decision schema violations: missing required field: project_name`. Always pass it.

**Return shape.** A string such as `Recorded DEC-YYYYMMDD-NNN (`decisions/YYYY/MM/….json`+`.md`; index now holds N).` (`mcp-decision-server/server.py:1654-1656`). When the fingerprint matches an earlier record, the same string carries `Possible duplicate of <id> (same fingerprint) — kept as a separate record; confirm intent.` (`mcp-decision-server/server.py:1620`, `:1652-1653`).

**Side effects.** Writes `decisions/YYYY/MM/DEC-YYYYMMDD-NNN.json` with `json.dumps(indent=2, ensure_ascii=False)` (`mcp-decision-server/server.py:1631-1633`) and a companion `.md` (`:1636-1650`), regenerates `INDEX.md` (`:1651`), prints the active store to stderr (`:1604`), and reports unpushed commits (`:1654-1656`). It never commits or pushes.

**Failure modes.** Sensitive residue after sanitizing, or any schema violation, raises `ValueError` and writes **nothing** (`mcp-decision-server/server.py:1625-1627`, `:1553-1602`). An unwritable store raises `RuntimeError` from `_repo_root()` (`:113`).

### `query_manager_decisions`

```python
query_manager_decisions(query: str, category: Optional[str] = None) -> str
```

**When to call.** Automatically, **before** paging the human Manager with a question. If a past ruling covers the question, decide from the record instead of asking (`mcp-decision-server/server.py:1661-1678`). Also call it during discovery when the task touches architecture, process, scope, or quality gates.

**Arguments.**

- `query` — keyword(s). Case-insensitive ranked match over `summary` (weight 3), verbatim `original` (2), verbatim `english_translation` (2), `rationale` (2), `tradeoffs` (1), joined `alternatives` (1) (`mcp-decision-server/server.py:1730-1737`). A blank query scores every record 1, so it returns everything in the category (`:1661-1678`).
- `category` — optional filter against the eight-value enum (`mcp-decision-server/server.py:1709-1710`, `:1661-1678`).

**Return shape.** `"{n} decision(s) match:\n\n"` followed by the joined hit blocks (`mcp-decision-server/server.py:1758-1759`). Each hit block is `### <decision_id> [<category>] <summary>`, then `> <english_translation>`, then `Rationale: <rationale>` (`mcp-decision-server/server.py:1750-1753`).

**Side effects.** Pulls the store first; reads only. Never writes, commits, or pushes.

**Failure modes.** No hits → the string `No manager decisions match query='…' category=…` (`mcp-decision-server/server.py:1755-1756`). A failed pull does **not** error out: the server prints `decision-server: pull failed (…); reading local state` and serves local state so reads stay available (`mcp-decision-server/server.py:1680-1686`). Malformed record files are skipped, not fatal: non-dict records, non-dict `extracted_decision`, non-dict `verbatim_quote`, and non-list `alternatives` are all filtered before scoring (`mcp-decision-server/server.py:1693-1728`).

**No result cap.** The tool returns **every** matching record. There is no top-N limit; the literal `3` at `mcp-decision-server/server.py:1731` is the `summary` scoring weight. On a large store, expect long output.

### `get_sync_status`

```python
get_sync_status() -> str
```

**When to call.** At session start, so silent sync debt is visible before new records land (`mcp-decision-server/server.py:1764-1767`).

**Return shape.** `"{active store info}; {freshness}; {unpushed report}"` (`mcp-decision-server/server.py:1763-1773`).

**Side effects.** Read-only; never commits or pushes (ZAC holds). A failed pull degrades to local state with a stderr note rather than raising (`mcp-decision-server/server.py:1763-1773`).

### `get_manager_profile`

```python
get_manager_profile() -> str
```

**When to call.** Automatically whenever resolving an architectural ambiguity or applying a house rule — the profile is the Manager's standing judgment (`mcp-decision-server/server.py:1778-1787`).

**Return shape.** The text of `<store>/samples/manager_profile.md`, or the explanatory string `No manager profile sample exists yet.` when the sample is absent.

**Notes.** The baseline section is curated; a generated aggregate appears only from reviewed compilations. The tool never synthesizes guidance (`mcp-decision-server/server.py:1778-1787`). Cheap, read-only, no side effects. A failed pull degrades to local state (`mcp-decision-server/server.py:1777-1798`).

### `propose_profile_evolution`

```python
propose_profile_evolution() -> dict[str, Any]
```

**When to call.** Only when new recorded decisions exist that the current sample does not reflect — roughly once per sprint, never per session. Present the draft to the Manager; merge nothing without explicit approval (`mcp-decision-server/server.py:1803-1816`).

**Behavior.** Runs `scripts/compile_profile.py` in a subprocess via `subprocess.run([sys.executable, str(script), "--repo", str(repo)], capture_output=True, text=True, timeout=120)` (`mcp-decision-server/server.py:1802-1834`). Nothing is written to the sample; the draft is returned as a staged diff-like payload.

**Return shape.** A dict with `status` in `DRAFT_READY` / `EMPTY` / `ERROR` plus `draft`.

- Missing compile script → `{"status": "ERROR", "draft": "compile script missing: <path>"}`.
- Subprocess error or non-zero return code → `{"status": "ERROR", …}` with the reason.
- Empty output, or output starting `No decisions found` → `{"status": "EMPTY", …}`.
- Otherwise → `{"status": "DRAFT_READY", "draft": <text>}`.

**Failure modes.** Never raises; every failure arrives as `status: ERROR`.

## Shared Decision-Record Field Contract

`_validate_against_schema` (`mcp-decision-server/server.py:865-912`) enforces the shape below before anything is written.

**Required fields** — the tuple at `mcp-decision-server/server.py:873-874`:

| Field                | Type / shape                                                                                                                         | Source                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------- |
| `decision_id`        | `DEC-\d{8}-\d{3}`, generated when absent                                                                                             | `:879`, generated at `:753-764` / `:1608` |
| `timestamp`          | ISO string parsed via `datetime.fromisoformat(str(…).replace("Z", "+00:00"))`; generated as `datetime.now(timezone.utc).isoformat()` | `:881-884`, `:1609`                       |
| `project_name`       | present in the required tuple; **never defaulted**                                                                                   | `:873-874`, `:1608-1619`                  |
| `verbatim_quote`     | mapping with `original` and `english_translation`                                                                                    | `:873-874`, `:1348-1356`                  |
| `extracted_decision` | mapping with `summary`, `category`, `rationale`, `alternatives[]`, `tradeoffs`                                                       | `:873-874`, `:1348-1356`                  |
| `redaction_verified` | server-set `True` after the scrub gate passes                                                                                        | `:861`, `:910`                            |

**Validated enums and optional fields:**

| Field         | Rule                                         | Source                               |
| ------------- | -------------------------------------------- | ------------------------------------ |
| `category`    | must be one of the eight values              | `:959-962`, `:892-894`, `:1045`      |
| `fidelity`    | `verbatim` or `reconstructed` when present   | `:896-900`                           |
| `mode`        | `manual` or `autopilot` when present         | `:896-900`                           |
| `scope`       | `standing` or `episode` when present         | `:896-900`                           |
| `fingerprint` | `[0-9a-f]{64}` sha256, generated when absent | `:904-906`, `:767-784`, `:1617-1619` |
| `goal_ref`    | optional string                              | `:907-909`                           |

**Server-stamped provenance:** `active_root` (repo display name) and `store_mode` (`personal` / `project-fallback`) — see Store Resolution above (`mcp-decision-server/server.py:1621-1624`).

The redactor (`mcp-decision-server/redactor.py`) backs the `redaction_verified` gate. `sanitize_text` is idempotent, coerces non-strings to `str`, and maps empty input to `""` (`redactor.py:58-72`). `verify_clean` returns `False` when a sensitive pattern survives and must block the write (`redactor.py:75-85`). `REDACTION_RULES` (`redactor.py:19-43`) covers provider keys (`sk-`, `ghp_`, `AIzaSy`), Bearer tokens (with a digit gate so prose like "Bearer tokens" is untouched), private IPv4 ranges (`10/8`, `172.16/12`, `192.168/16`), and generic `password|passwd|secret|api_key|auth_token = …` assignments. `_VERIFY_RESIDUE` (`redactor.py:52-55`) reuses those rules but swaps the assignment rule for `_VERIFY_ASSIGNMENT` (`redactor.py:49-51`), which carries a `(?!\[REDACTED\])` lookahead so an already-redacted marker is not mistaken for a live secret.

## Pitfalls for Agents

| Pitfall                                                 | Correct behavior                                                                                                                                                                        |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Omitting `project_name`                                 | Always pass it. It is required and not defaulted (`mcp-decision-server/server.py:873-874`, `:1608-1619`), and the tool docstring lists it with the full record contract (`:1576-1594`). |
| `verbatim_quote` as a plain string                      | Must be a mapping with `original` and `english_translation`.                                                                                                                            |
| `extracted_decision` as a plain string                  | Must be a mapping with `summary`, `category`, `rationale`, `alternatives[]`, `tradeoffs`.                                                                                               |
| `alternatives` as a string or `None`                    | Must be a list. The query tool filters non-list `alternatives` before scoring (`mcp-decision-server/server.py:1719-1728`).                                                              |
| `tradeoffs` as a list                                   | Must be a string.                                                                                                                                                                       |
| Inventing a category                                    | The enum is closed: eight values only. `product-behavior` is invalid (`mcp-decision-server/server.py:959-962`).                                                                         |
| Paging the Manager first                                | Query stored decisions first; a past ruling may already answer it (`mcp-decision-server/server.py:1661-1678`).                                                                          |
| Expecting a short query result                          | There is no result cap (`mcp-decision-server/server.py:1758-1759`).                                                                                                                     |
| Passing `None` for `fidelity`/`mode`/`scope`/`goal_ref` | Treated as unset; the server applies `verbatim` / `manual` / `episode` / `""` (`mcp-decision-server/server.py:1610-1616`).                                                              |
| Treating auto-record as allowed                         | It is forbidden. Every persist passes the Manager confirm gate and `record_manager_decision` (`mcp-decision-server/detector.py:1-20`).                                                  |
| Expecting `propose_profile_evolution` to write          | It writes nothing; it returns a draft for approval (`mcp-decision-server/server.py:1803-1816`).                                                                                         |
| Expecting a blocked pull to break reads                 | A failed pull degrades to local state with a stderr note; reads still work (`mcp-decision-server/server.py:1680-1686`).                                                                 |

## Recommended Workflow

1. **Session open:** call `get_sync_status` so pending push debt is visible (`mcp-decision-server/server.py:1764-1767`).
2. **Before asking the Manager:** call `query_manager_decisions` with keywords from the question. Decide from the record when a ruling covers it (`mcp-decision-server/server.py:1661-1678`).
3. **Resolving ambiguity:** call `get_manager_profile` for the standing judgment (`mcp-decision-server/server.py:1778-1787`).
4. **Mid-session ruling:** call `record_manager_decision` immediately, while the verbatim quote is still exact (`mcp-decision-server/server.py:1553-1602`).
5. **Before closing a task:** call `extract_session_decisions`, then queue each candidate through `record_manager_decision` — never persist raw extractor output (`mcp-decision-server/server.py:1264-1294`, `:1553-1602`).
6. **Roughly once per sprint:** call `propose_profile_evolution` and present the draft for approval (`mcp-decision-server/server.py:1803-1816`).

Sync is pull-before-read and pull-before-write (`_ensure_fresh`, `mcp-decision-server/server.py:168`), and the server never commits or pushes; a human or the sanctioned commit path does that.

## Doc Drift

These divergences were found in the source at commit `0183433`. Six were recorded when this page was written. Two of them — D1 and D2 — were fixed on 2026-09-21 in the write tool's `Args` block and in the extraction prompt; the other four still stand. **No skill file was changed, and no server behavior changed.**

| ID  | Drift                                                                                                                                                                                                  | Evidence                                                                                                                                         |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| D1  | **Fixed 2026-09-21.** The extraction prompt advertised only seven categories while the validator accepts eight, so the model was never told `autopilot-cycle` existed. The prompt now lists all eight. | prompt `mcp-decision-server/server.py:1353-1354` vs `_VALID_CATEGORIES` `mcp-decision-server/server.py:959-962` and the inline set at `:892-894` |
| D2  | **Fixed 2026-09-21.** `project_name` is hard-required and used to be undocumented in the tool's `Args` block. The block now lists all six required fields and the nested record shapes.                | required at `mcp-decision-server/server.py:873-874`; documented at `:1576-1594`                                                                  |
| D3  | `query_manager_decisions` has no result cap, so a large store returns full output. The literal `3` in the function is a scoring weight, not a limit.                                                   | scoring `mcp-decision-server/server.py:1730-1737`; uncapped return at `:1758-1759`                                                               |
| D4  | `_SCRUB_FIELDS` is a dead constant — defined, never referenced. The real scrub list is hardcoded in `_scrub_free_text`.                                                                                | definition `mcp-decision-server/server.py:193`; hardcoded leaves/targets at `:831-851`                                                           |
| D5  | The skill text and the tool's own guidance describe different push commands.                                                                                                                           | skill text vs the guidance carried in `get_sync_status` / `_unpushed_report` (`mcp-decision-server/server.py:177`, `:1763-1773`)                 |
| D6  | The `detector.py` module docstring cites stale `server.py` line numbers for `extract_session_decisions` and `record_manager_decision`.                                                                 | `mcp-decision-server/detector.py:1-20`; actual lines are `mcp-decision-server/server.py:1258` and `:1551`                                        |

Both fixed items were documentation-and-prompt fixes: no validation behavior changed. The eight-value category set is still duplicated, held inline in `_validate_against_schema` (`mcp-decision-server/server.py:892-893`) and again in `_VALID_CATEGORIES` (`:959-962`) instead of the validator importing the constant — a duplication that can drift independently.

## Could Not Verify

- **Generated MCP `inputSchema`.** The server was read, never executed. The JSON Schema a client derives from these signatures was not observed.
- **`migrated_from` field.** Not defined anywhere in `mcp-decision-server/`; no behavior can be documented.
- **Behavior against a diverged remote.** The stale-on-pull-failure path is documented from source (`mcp-decision-server/server.py:1680-1686`, `:1763-1773`, `:1777-1798`) but was not reproduced against a real diverged remote.

## Related

- [`docs/brain-bridge.md`](brain-bridge.md) — the Brain Bridge server that consumes these rulings in autopilot.
- [`docs/setup.md`](setup.md) — MCP server table and start commands.
- [`skill-templates/manager-decision/SKILL.md`](../skill-templates/manager-decision/SKILL.md) — the agent workflow around these tools.
