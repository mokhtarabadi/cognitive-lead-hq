# Task 260: Responses-API reasoning budget fix, question-tool grant, and repo hygiene

**File:** `tasks/completed/260-responses-budget-question-tool-hygiene.md`
**Source:** manager
**Type:** improvement
**Status:** closed

## Goal

Ship the current working-tree change set as one reviewed unit: fix reasoning-budget starvation on both Responses-API MCP servers, grant the native OpenCode `question` tool to the cognitive executor, harden repository hygiene so env backups can never be committed, and point skills that ask the Manager at the structured question channel.

## Manager's Notes

Created on autopilot as a review vehicle for changes already implemented on disk in this session. The Manager asked for a task file built from the working tree, then routed through the autopilot cycle for a QA verdict and a Code Reviewer verdict. No new implementation is expected unless QA rejects. Standing orders apply: zero-question autopilot, consult Brain personas via `brain_turn`, RTK-first verification.

## Change Set Under Review

1. Reasoning-budget starvation fix — `mcp-brain-bridge/server.py` and `mcp-decision-server/server.py`. Reasoning tokens are billed as output and count against the output cap; `reasoning.effort` allocates a share of that cap (`xhigh`/`max` about 95%, `high` about 80%, `medium` about 50%). The old bridge defaults (`BRAIN_REASONING_EFFORT=xhigh`, `BRAIN_MAX_TOKENS=16384`) left roughly 820 tokens for visible text, so Brain replies truncated mid-sentence while the reasoning tokens were still charged.
2. Question-tool grant — `agents/cognitive-executor.md` plus `mcp-brain-bridge/capability.py`. The tool is a native OpenCode built-in that the agent had switched off; it is now allowed and registered as available.
3. Repository hygiene — `.gitignore` plus removal of a secrets-bearing env backup from the worktree.
4. Skill question-channel parity — six `skill-templates/*/SKILL.md` files.

## Local TODOs

- [x] Fix bridge defaults and add visible-token logging
- [x] Add the decision-path output cap and effort default
- [x] Add the warn-only effort-support guard
- [x] Grant the `question` tool and correct the capability registry
- [x] Harden `.gitignore` and relocate the env backup
- [x] Add manifest-aware question wording to the asking skills
- [x] Run the RTK-first targeted and full suites
- [ ] Stage, run the QA-review cycle, and close

## Acceptance Criteria

- [x] Both servers send an explicit output cap and a model-appropriate reasoning effort default: bridge `medium` with a `32768` cap, decision server `high` with a `16384` cap.
- [x] Both servers log a `visible_tokens` count (output minus reasoning) on every provider call.
- [x] The decision server warns without failing when the configured effort is outside the model's advertised set.
- [x] The `question` tool is granted to the cognitive executor and registered as available in the capability registry.
- [x] `.gitignore` ignores `.env.*` and `*.bak*` while `.env.example` stays tracked, and no secrets-bearing backup file exists inside the worktree.
- [x] Every skill template that asks the Manager points at the `question` tool when the capability manifest shows it available, with a prose fallback.
- [x] The full test suite passes with exit code 0.

## Verification Evidence

- **Test command:** rtk test uv run --with pytest --with mcp==1.30.0 --with pathspec --with pyyaml --with tree-sitter --with tree-sitter-python --with tree-sitter-javascript --with tree-sitter-typescript --with tree-sitter-go --with tree-sitter-java --with tree-sitter-rust --with tree-sitter-kotlin pytest tests/ -q
- **Expected result:** the whole suite passes with no failures.
- **Actual result:** 626 passed, 10 warnings in 4.64s (targeted bridge + decision + capability suites: 373 passed).
- **Exit code:** 0

> Verification runner rule: the `pytest tests/ -q` command above is the complete underlying test command. The first verification run used the `rtk test` prefix; the exact prefixed command is recorded above. A raw rerun is allowed only after a failed RTK run for detailed diagnostics.

## Definition of Done

The task is NOT done unless ALL of the following are true (unconditional, applies to every source type):

- [x] Build/Test/Lint pass with exit code 0
- [x] `lint_task_file` passes on the active task file
- [x] `CHANGELOG.md` updated via Parse-Then-Append
- [x] `verification-before-completion` applied and evidence recorded

> **Box-checking mandate:** During the implementation `<summary_phase>`, the Hands MUST check every `## Acceptance Criteria` and `## Definition of Done` box that is genuinely satisfied by the recorded `## Verification Evidence` — do NOT defer box-checking to a closure task.

## Risk & Rollback

- **Risk:** a wrong default changes every Brain turn; an over-broad `.gitignore` could hide a legitimate file; the capability-registry change could mark a genuinely missing tool available.
- **Rollback plan:** revert the affected files with `git checkout -- <path>` and re-run the full suite. Env rollback copies exist at `~/.config/opencode/.env.bak-20260919b` and `~/.config/opencode/.env.project.bak-20260919b`.

---

## Execution Log & Reasoning

### Context

Autopilot locked. Memory `manager/full_automatic_mode` is the authorization basis: zero clarification halts, consult Brain personas via `brain_turn`, reviewer technical approval plus `PO_REVIEW_PENDING` counts as closure approval. RTK-first verification per `workflows/rtk_first_verification`. No task file was created earlier for this work under `workflows/no_task_for_global_upgrade`; the Manager has now asked for a review vehicle, so this file records it.

### 1. Reasoning-budget root cause

OpenRouter bills reasoning tokens as output and counts them against the request output cap. The documented allocation is `max`/`xhigh` about 95 percent, `high` about 80 percent, `medium` about 50 percent, `low` about 20 percent. The bridge sent `reasoning.effort=xhigh` with `max_output_tokens=16384`, so only about 820 tokens remained for visible text. That single fact explains the truncated replies, the wasted spend, and the useless answers. A live provider probe confirmed the parameters themselves were never rejected: three real calls with the decision model and the Brain model all returned HTTP 200.

### 2. Bridge changes

- `_get_max_tokens()` default raised from `16384` to `32768`, with a docstring explaining the reasoning-token accounting.
- `_get_reasoning_effort()` default changed from `xhigh` to `medium`, the model's own advertised default.
- `_log_provider_diagnostics()` now computes and prints `visible_tokens` (output minus reasoning) on every provider call.
- `_maybe_warn_reasoning_budget()` docstring rewritten; the warning still fires when an explicit cap under `32768` meets `high` or `xhigh`.

### 3. Decision-server changes

- `_get_decision_effort()` fallback changed from `xhigh` to `high`, the DeepSeek V4.1 Flash default.
- New `_get_decision_max_tokens()` reading `DECISION_MAX_TOKENS`, default `16384`; the request body now sends `max_output_tokens` instead of leaving the ceiling to the provider.
- `_log_responses_diagnostics()` gained the same `visible_tokens` count.
- `_resolve_decision_effort()` warns without failing when the configured effort is outside the model's advertised set and coerces the value to the model's own default.

### 4. Question-tool grant

The `question` tool is a native OpenCode built-in. `opencode debug agent` showed the custom primary agent resolving `"question": false` while the built-in primaries resolved `true`: OpenCode applies a base `question: deny` rule and grants its own primary agents a later `allow` that wins. The agent definition now carries `question: allow`, and the capability registry moved `question` into the available set with the unavailable registry emptied. Verified live: the resolved config now reports `"question": true`.

### 5. Repository hygiene

The project `.env` backup sat in the repository root and was not ignored, so a broad `git add` could have committed secrets. It was moved out of the worktree to `~/.config/opencode/.env.project.bak-20260919b` with mode `600`, and `.gitignore` gained `.env.*` with an explicit `!.env.example` negation, plus `*.bak*`.

### 6. Skill question-channel parity

Six skill templates gained manifest-aware wording: `telegram-message-export` (its unconditional mandate replaced), `decision-migration` (both gate spots), `opencode-init`, `doc-coauthoring`, `prompt-refactor`, and `manager-decision`. `telegram-issue-sync` already carried the wording. Every changed skill is synced to the global install.

### 7. Verification

- Targeted suites: 373 passed, exit 0.
- Full suite: 626 passed, 10 warnings, exit 0.
- `py_compile` clean on both servers; global copies verified IN-SYNC.
- Live provider probe: three real calls, all HTTP 200.
- `opencode debug agent cognitive-executor` reports `"question": true`.

### Incidents

Two bridge tests failed on the first targeted run. The cause was a stale inherited `BRAIN_REASONING_EFFORT=xhigh` exported by the running daemon before this session's edits. Re-running with the stale variables cleared passed all 346 tests, and after the restart the same tests pass with no workaround.

### QA round 1 rejection and repair

The first QA turn returned `QA_REJECTED` with two risks and two test gaps, all repaired:

- R1 (high): the decision server still inherited `BRAIN_REASONING_EFFORT` before applying its own default, so a configured `xhigh` kept extraction at an effort the model does not advertise. `_maybe_warn_effort_support()` was replaced by `_resolve_decision_effort(model, effort)`, which keeps the inheritance chain but coerces an unadvertised effort to the model's own default and warns without failing; unknown models pass through untouched.
- R2 (medium): the ignore rules used `*.bak` plus `*.bak-*`, which leaves names such as `config.bak1` trackable. Both were replaced by the single `*.bak*` pattern.
- F1: the capability tests no longer proved that an explicit unavailable override can demote the newly granted tool. Added `test_unavailable_override_demotes_granted_question_tool`.
- F2: nothing covered the `visible_tokens` logging or the effort warning. Added bridge and decision-server `visible_tokens` tests plus a coercion test for `_resolve_decision_effort`.

The repair suite is green: targeted 373 passed, full 626 passed, exit 0.

### Closure authorization

The Manager answered the closure question through the native `question` tool — the first live use of the granted channel — with the exact phrase **"Approved for closure"**. The task was moved to `tasks/completed/`, its status set to `closed`, and the staged 16-file change set committed through `custom_context_commit_and_clean_task`.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->
```diff
diff --git a/.env.example b/.env.example
index 2993414..bf2d7fc 100644
--- a/.env.example
+++ b/.env.example
@@ -14,13 +14,17 @@ BRAIN_API_KEY=sk-...
 # Brain model (Responses-API id). Blank = built-in default
 # (gpt-6-astra).
 #BRAIN_MODEL=gpt-6-astra
-# Reasoning effort sent as `reasoning.effort` (default xhigh).
-#BRAIN_REASONING_EFFORT=xhigh
+# Reasoning effort sent as `reasoning.effort` (default medium, the Luna
+# model's own default). xhigh/max can claim roughly 95% of the token cap
+# on reasoning and starve the visible answer.
+#BRAIN_REASONING_EFFORT=medium
 # System prompt override (absolute path). Blank = global install copy
 # (~/.config/opencode/system-prompt.md).
 #BRAIN_SYSTEM_PROMPT=
-# Token cap per Brain turn (default 16384).
-#BRAIN_MAX_TOKENS=16384
+# Token cap per Brain turn (default 32768). Reasoning tokens are billed as
+# output and count against this cap, so keep it well above the expected
+# reasoning length.
+#BRAIN_MAX_TOKENS=32768
 
 # Manager decisions (mcp-decision-server) — extraction model + temperature.
 # Blank model = falls back to BRAIN_MODEL. Blank base/key = fall back to
@@ -29,8 +33,13 @@ BRAIN_API_KEY=sk-...
 #DECISION_API_BASE=
 #DECISION_API_KEY=
 #DECISION_MODEL=
-# Reasoning effort sent as `reasoning.effort` (blank = BRAIN_REASONING_EFFORT).
+# Reasoning effort sent as `reasoning.effort` (default high — the DeepSeek
+# V4.1 Flash default; that model advertises only max/high/low. Blank =
+# BRAIN_REASONING_EFFORT).
 #DECISION_REASONING_EFFORT=
+# Output token cap for extraction turns (default 16384). Blank leaves the
+# provider ceiling in place.
+#DECISION_MAX_TOKENS=16384
 #DECISION_TEMPERATURE=1.0
 # Decision store path — set ONCE here or as a shell export, never per call.
 # When set, all tools resolve the personal repo silently; when blank, the
diff --git a/.gitignore b/.gitignore
index ad9e374..06927e3 100644
--- a/.gitignore
+++ b/.gitignore
@@ -29,6 +29,9 @@ node_modules/
 # Environment
 .env
 .env.local
+.env.*
+!.env.example
+*.bak*
 
 # Retired browser automation MCP artifacts
 .retired-browser-name/
diff --git a/CHANGELOG.md b/CHANGELOG.md
index f41e9b2..d61f74e 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -28,6 +28,10 @@ The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
 
 ### Fixed
 
+- **Secrets-safe repo hygiene + skill question-channel parity:** `.gitignore` now ignores `.env.*` (with an explicit `!.env.example` negation so the template stays tracked) plus `*.bak*`, and this session's project `.env` backup was moved out of the worktree to `~/.config/opencode/.env.project.bak-20260919b` — a `git add -A` can no longer sweep secrets into history. Seven skill templates that ask the Manager or user a question now point at the `question` tool when the session capability manifest shows it AVAILABLE and fall back to the prose relay otherwise: `telegram-message-export` (its unconditional mandate replaced), `decision-migration` (both gate spots), `opencode-init`, `doc-coauthoring`, `prompt-refactor`, and `manager-decision`; `telegram-issue-sync` already carried the wording. Every changed `SKILL.md` is synced to the global install (36/36 skills, zero drift, no orphans).
+
+- **Reasoning-budget starvation fixed on both Responses-API servers:** OpenRouter bills reasoning tokens as output and counts them against the output cap, and `reasoning.effort` allocates a share of that cap (`xhigh`/`max` ≈ 95%, `high` ≈ 80%, `medium` ≈ 50%). With `BRAIN_REASONING_EFFORT=xhigh` and `BRAIN_MAX_TOKENS=16384`, roughly 820 tokens were left for the visible answer, so Brain replies truncated mid-sentence while every reasoning token was still charged. Both code defaults moved: `mcp-brain-bridge/server.py` now defaults to `medium` effort and a 32768 cap, and `mcp-decision-server/server.py` defaults to `high` effort — the DeepSeek V4.1 Flash default — and sends an explicit `max_output_tokens` from the new `DECISION_MAX_TOKENS` (default 16384) instead of leaving the ceiling to the provider. Both servers now log a `visible_tokens` count (output minus reasoning) on every provider call, so starvation is measurable, and the decision server warns without failing when the configured effort is outside the model's advertised set. `.env.example` documents the new defaults. Full suite: **626 passed**.
+- **`question` tool granted to the cognitive executor (syncs GitHub issue 21):** the `question` tool is a native OpenCode built-in with a structured request contract (question text, a short header, enumerated options, optional multi-select, one answer slot), yet `opencode debug agent cognitive-executor` resolved `"question": false` while the built-in `build` and `plan` agents resolved `true`. OpenCode applies a base `question: deny` rule and grants its own primary agents a later `allow` that wins under last-matching-rule-wins; a custom primary agent inherits only the deny. `agents/cognitive-executor.md` now carries `question: allow` in its `permission` block (repo and global copies), and `mcp-brain-bridge/capability.py` was corrected accordingly: `question` moved into `AVAILABLE_EXACT`, `KNOWN_UNAVAILABLE` emptied, and the grounding docstring restated — the granted surface is the resolved agent toolset, not the `opencode.json` key list (`todowrite`, `webfetch`, and `websearch` are absent there yet granted). Until now the capability preflight classed `question` as `UNAVAILABLE_REQUIRED` and every clarification fell back to prose `Q1`/`Q2` codes; issue 21's "build it" branch was unnecessary because no custom tool had to be written. 7 capability tests rewritten to use `frobnicate` as the canonical unavailable name. Full suite: **626 passed**.
 - **Default provider base URL moved to the OpenAI API (muse-spark retirement cleanup):** `mcp-brain-bridge/server.py` `_responses_url()` and `mcp-decision-server/server.py` `_DECISION_API_BASE_DEFAULT` still defaulted to the retired local gateway `http://127.0.0.1:8081/zen/resp`; both now default to `https://api.openai.com/v1`, `.env.example` shows the same value, and the matching bridge URL test was updated. The model half needed no change: both servers already default to OpenAI's latest Astra (`gpt-6-astra`), which is the outcome archived Task 205 ordered ("drop `muse-spark-1.3-contributor-free` default everywhere, default to OpenAI latest Astra model"). The surviving `muse-spark-1.3` strings are historical CHANGELOG and memory-note records and were left intact rather than rewritten. `BRAIN_API_BASE`/`DECISION_API_BASE` overrides are unchanged, and no `.env` file was touched. Full suite: **621 passed**.
 - **`DECISION_REPO_PATH` env passthrough corrected (global config + docs):** the global `opencode.json` `manager_decisions` entry hardcoded a stale literal path in its `environment` block, so the corrected `.env` value never took effect — the decision server's import-time loader assigns a key only when it is unset, and process env outranks `.env`, making the literal authoritative. That entry now forwards `{env:DECISION_REPO_PATH}`, the same interpolation form as its sibling `{env:BRAIN_*}` and `{env:DECISION_MODEL}` keys, so the value resolves from the user environment. `LLM.txt` §7.11 no longer forbids the variable in the shared `opencode.json`: the warning now targets a hardcoded literal and blesses the `{env:...}` form. The `docs/setup.md` systemd `EnvironmentFile` example drops the obsolete `code-server` checkout path for the current one.
 - **Provider-failure diagnosis for both MCP servers (Task 259, syncs GitHub issue 20):** an empty provider turn was misreported as a transport flake. `mcp-brain-bridge/server.py` now parses and logs Responses diagnostics on every turn (`status`, `incomplete_details.reason`, `usage` incl. reasoning tokens, top-level `error`, refusal text) and attaches them to the result as `debug.provider` with stable keys (nulls when absent). The empty-output guard branches in a fixed order — provider error, refusal, `status=incomplete` with `reason=max_output_tokens`, then the generic flake — so a reasoning-budget exhaustion returns the new terminal `OUTPUT_BUDGET_EXHAUSTED` token with remediation (lower `BRAIN_REASONING_EFFORT` or raise `BRAIN_MAX_TOKENS`, recommend 32768+) instead of `EMPTY_OUTPUT_RETRY`; it is not counted as a retry and no lean retry is suggested (the same effort/cap would fail identically). Top-level errors and refusals surface verbatim. A non-breaking stderr warning fires before the provider request when high/xhigh effort runs with a cap under 32768 (the 16384 default is unchanged — no automatic bump). `mcp-decision-server/server.py` gets the same diagnostics parsing/logging and, for an empty envelope with a provider cause, raises a precise terminal error carrying `OUTPUT_BUDGET_EXHAUSTED`/`PROVIDER_ERROR`/`PROVIDER_REFUSAL` instead of the misleading `decision model returned non-JSON`; a genuine model blank keeps the old error. Both parsers are hardened against malformed provider payloads — a non-list nested `content`, non-finite usage values, and a malformed `error` object are swallowed rather than raised, so diagnosis can never itself abort the turn. 25 new tests (13 bridge, 12 decision server), end-to-end through `brain_turn`/`extract_session_decisions`. Full suite: **621 passed**.
diff --git a/agents/cognitive-executor.md b/agents/cognitive-executor.md
index 2a64942..16c6188 100644
--- a/agents/cognitive-executor.md
+++ b/agents/cognitive-executor.md
@@ -5,6 +5,7 @@ temperature: 0.1
 steps: 512
 permission:
   edit: allow
+  question: allow
   bash:
     "*": "allow"
     "rm -rf*": "ask"
diff --git a/mcp-brain-bridge/capability.py b/mcp-brain-bridge/capability.py
index 653afa0..082e4f8 100644
--- a/mcp-brain-bridge/capability.py
+++ b/mcp-brain-bridge/capability.py
@@ -12,18 +12,26 @@ of three statuses — no silent fourth state:
 - ``UNAVAILABLE_OPTIONAL`` — missing but not required: noted, skipped
   openly.
 
-Availability registry grounding (read 2026-09-18): the granted tool
+Availability registry grounding (read 2026-09-19): the granted tool
 surface is ``opencode.json`` ``permission`` — families
 ``custom_context_*``, ``project_memory_*``, ``lint_*``, ``blowsh_*``,
 ``telegram_*``, plus ``brain_turn``, the manager-decision tools, the
 context tools (``get_directory_tree``, ``read_source_files``,
 ``bundle_tasks``), and the native core (``task``, ``skill``,
 ``todowrite``, ``read``, ``edit``, ``write``, ``bash``, ``grep``,
-``glob``). ``question`` is absent from ``opencode.json`` AND has zero
-definitions anywhere in the repo, while two live references demand it
-(``skill-templates/telegram-issue-sync/SKILL.md:79``,
-``prompts/fragments/09-hands_protocols.md:66``) — hence
-``KNOWN_UNAVAILABLE = {'question'}``. Unknown names fail closed
+``glob``, ``question``).
+
+``question`` was previously listed in ``KNOWN_UNAVAILABLE``. The cause
+was not a missing tool: OpenCode ships ``question`` as a built-in, but
+its primary agents receive an explicit ``question: allow`` that
+overrides the base ``question: deny``, and a custom primary agent
+inherits only the deny. The agent definition now grants it explicitly
+(``agents/cognitive-executor.md`` frontmatter, ``permission: question:
+allow``), so ``question`` is part of the granted surface and
+``KNOWN_UNAVAILABLE`` is empty. Note the granted surface is the
+resolved agent toolset, not the ``opencode.json`` key list alone:
+``todowrite``, ``webfetch`` and ``websearch`` are absent from that
+block yet ARE granted. Unknown names still fail closed
 (``UNAVAILABLE_REQUIRED`` when required); the caller ``available`` /
 ``unavailable`` overrides are the documented escape hatch.
 """
@@ -69,14 +77,15 @@ AVAILABLE_EXACT = frozenset({
     "bash",
     "grep",
     "glob",
+    "question",
 })
 
 # Tools referenced by live prompts/skills but absent from the granted
 # toolset (see module docstring). Listed explicitly so the manifest can
-# name them instead of failing open on unknown names.
-KNOWN_UNAVAILABLE = frozenset({
-    "question",
-})
+# name them instead of failing open on unknown names. Empty since
+# ``question`` was granted through the cognitive-executor agent's
+# permission block.
+KNOWN_UNAVAILABLE = frozenset()
 
 # Approval-sensitive stages imply required tools even when the caller
 # does not list them: QA always needs the task linter, closure always
diff --git a/mcp-brain-bridge/server.py b/mcp-brain-bridge/server.py
index bfe746b..44f2bb2 100644
--- a/mcp-brain-bridge/server.py
+++ b/mcp-brain-bridge/server.py
@@ -1152,11 +1152,17 @@ def build_prompt_cache_split(
 
 
 def _get_max_tokens() -> int:
-    """Cap for Brain turns; override via ``BRAIN_MAX_TOKENS``."""
+    """Cap for Brain turns; override via ``BRAIN_MAX_TOKENS``.
+
+    Defaults to 32768 rather than 16384: reasoning tokens are billed as
+    output and count against this cap on most providers, so a smaller cap
+    lets high-effort reasoning starve the visible answer (blank or
+    truncated replies while the reasoning tokens are still charged).
+    """
     try:
-        return int(os.environ.get("BRAIN_MAX_TOKENS", "16384").strip() or "16384")
+        return int(os.environ.get("BRAIN_MAX_TOKENS", "32768").strip() or "32768")
     except ValueError:
-        return 16384
+        return 32768
 
 
 def _get_api_key() -> str:
@@ -2468,8 +2474,14 @@ def _responses_url() -> str:
 
 
 def _get_reasoning_effort() -> str:
-    """Reasoning effort; override via ``BRAIN_REASONING_EFFORT``."""
-    val = os.environ.get("BRAIN_REASONING_EFFORT", "xhigh").strip() or "xhigh"
+    """Reasoning effort; override via ``BRAIN_REASONING_EFFORT``.
+
+    Defaults to ``medium`` — the default the Luna model itself advertises.
+    ``xhigh`` (and ``max``) allocate roughly 95% of ``max_output_tokens`` to
+    reasoning, so a modest cap leaves almost nothing for the visible answer
+    while the reasoning tokens are still billed.
+    """
+    val = os.environ.get("BRAIN_REASONING_EFFORT", "medium").strip() or "medium"
     if not re.fullmatch(r"[\w.-]{1,64}", val):
         raise ValueError(f"bad reasoning effort: {val!r}")
     return val
@@ -2642,17 +2654,28 @@ def parse_responses_diagnostics(data: Any) -> dict:
 
 
 def _log_provider_diagnostics(diag: dict) -> None:
-    """Emit one compact diagnostics line to stderr on every turn (AC1)."""
+    """Emit one compact diagnostics line to stderr on every turn (AC1).
+
+    Includes the visible-token count (output minus reasoning). Reasoning
+    tokens are billed as output and count against ``max_output_tokens``, so
+    a near-zero visible count is the signature of a starved answer.
+    """
     usage = diag.get("usage")
     if not isinstance(usage, dict):
         usage = {}
+    out_tokens = usage.get("output_tokens")
+    reasoning_tokens = usage.get("reasoning_tokens")
+    visible_tokens: Optional[int] = None
+    if isinstance(out_tokens, int) and isinstance(reasoning_tokens, int):
+        visible_tokens = out_tokens - reasoning_tokens
     print(
         "brain-bridge: provider diag "
         f"status={diag.get('status')} "
         f"incomplete_reason={diag.get('incomplete_reason')} "
         f"input_tokens={usage.get('input_tokens')} "
-        f"output_tokens={usage.get('output_tokens')} "
-        f"reasoning_tokens={usage.get('reasoning_tokens')} "
+        f"output_tokens={out_tokens} "
+        f"reasoning_tokens={reasoning_tokens} "
+        f"visible_tokens={visible_tokens} "
         f"total_tokens={usage.get('total_tokens')} "
         f"error={diag.get('error')!r} refusal={diag.get('refusal')!r}",
         file=sys.stderr)
@@ -2706,9 +2729,12 @@ def _output_budget_hint(diag: dict, task_id: Optional[str] = None,
 def _maybe_warn_reasoning_budget(effort: str, max_tokens: int) -> None:
     """Warn (non-breaking) when high effort runs with a small cap (C6).
 
-    Reasoning tokens count against ``max_output_tokens``; the bridge keeps
-    its 16384 default in this task, so the risky combination is surfaced
-    to stderr before the provider request instead of silently failing.
+    Reasoning tokens count against ``max_output_tokens``; ``xhigh`` claims
+    roughly 95% of the cap, so a small cap leaves almost nothing for the
+    visible answer. The 32768 default keeps the risky combination out of
+    the way, but an explicit ``BRAIN_MAX_TOKENS`` can still reintroduce it,
+    so the warning fires before the provider request rather than failing
+    silently.
     """
     if effort in _HIGH_EFFORT and max_tokens < _REASONING_BUDGET_FLOOR:
         print(
diff --git a/mcp-decision-server/server.py b/mcp-decision-server/server.py
index ad1fa39..7869ad9 100644
--- a/mcp-decision-server/server.py
+++ b/mcp-decision-server/server.py
@@ -232,17 +232,71 @@ def _get_decision_model() -> str:
 def _get_decision_effort() -> str:
     """Reasoning effort for extraction; override via
     ``DECISION_REASONING_EFFORT``, falling back to
-    ``BRAIN_REASONING_EFFORT``."""
+    ``BRAIN_REASONING_EFFORT``.
+
+    Defaults to ``high`` — the effort ``deepseek/deepseek-v4.1-flash``
+    advertises as its own default (it supports only ``max``/``high``/``low``).
+    """
     val = (
         os.environ.get("DECISION_REASONING_EFFORT", "").strip()
-        or os.environ.get("BRAIN_REASONING_EFFORT", "xhigh").strip()
-        or "xhigh"
+        or os.environ.get("BRAIN_REASONING_EFFORT", "high").strip()
+        or "high"
     )
     if not re.fullmatch(r"[\w.-]{1,64}", val):
         raise ValueError(f"bad reasoning effort: {val!r}")
     return val
 
 
+def _get_decision_max_tokens() -> int:
+    """Output cap for extraction turns; override via ``DECISION_MAX_TOKENS``.
+
+    The extraction call used to send no cap at all, leaving the ceiling to
+    the provider. Reasoning tokens are billed as output and count against
+    this cap on most providers, so an explicit value keeps the cost and the
+    truncation boundary predictable.
+    """
+    try:
+        return int(os.environ.get("DECISION_MAX_TOKENS", "16384").strip() or "16384")
+    except ValueError:
+        return 16384
+
+
+#: Advertised reasoning-effort support for the models this server ships a
+#: default for. A missing entry means "unknown model" and the guard stays
+#: silent — it must never block a call, only keep an unadvertised setting
+#: from reaching the provider.
+_KNOWN_EFFORT_SUPPORT: dict[str, frozenset[str]] = {
+    # DeepSeek V4.1 Flash advertises only max/high/low (its own default is high).
+    "deepseek/deepseek-v4.1-flash": frozenset({"max", "high", "low"}),
+}
+
+#: Effort used when the configured value is not advertised by the model.
+#: Mirrors each model's own default.
+_KNOWN_EFFORT_DEFAULTS: dict[str, str] = {
+    "deepseek/deepseek-v4.1-flash": "high",
+}
+
+
+def _resolve_decision_effort(model: str, effort: str) -> str:
+    """Return an effort the model advertises, coercing when it does not.
+
+    ``DECISION_REASONING_EFFORT`` falls back to the shared
+    ``BRAIN_REASONING_EFFORT``, and the Brain and decision models advertise
+    different effort sets, so a value that suits one can be unadvertised for
+    the other. When that happens the model's own default is used instead and
+    a warning is printed; the call itself is never blocked.
+    """
+    supported = _KNOWN_EFFORT_SUPPORT.get(model)
+    if supported is None or effort in supported:
+        return effort
+    fallback = _KNOWN_EFFORT_DEFAULTS.get(model, effort)
+    print(
+        f"decision-server: warning: reasoning effort {effort!r} is not among "
+        f"{sorted(supported)} advertised by {model!r}; using {fallback!r}.",
+        file=sys.stderr)
+    return fallback
+
+
 def _get_api_key() -> str:
     """Provider key: ``DECISION_API_KEY`` first, ``BRAIN_API_KEY`` as
     fallback. Fail-closed: an empty key cannot authenticate, so raise
@@ -520,17 +574,29 @@ def _responses_diagnostics(data: Any) -> dict:
 
 
 def _log_responses_diagnostics(diag: dict) -> None:
-    """Emit one compact diagnostics line to stderr on every provider call."""
+    """Emit one compact diagnostics line to stderr on every provider call.
+
+    Includes the visible-token count (output minus reasoning). A near-zero
+    visible count is the signature of a reasoning trace that consumed the
+    whole output budget, which is what makes an answer come back blank or
+    truncated while the reasoning tokens are still billed.
+    """
     usage = diag.get("usage")
     if not isinstance(usage, dict):
         usage = {}
+    out_tokens = usage.get("output_tokens")
+    reasoning_tokens = usage.get("reasoning_tokens")
+    visible_tokens: Optional[int] = None
+    if isinstance(out_tokens, int) and isinstance(reasoning_tokens, int):
+        visible_tokens = out_tokens - reasoning_tokens
     print(
         "decision-server: provider diag "
         f"status={diag.get('status')} "
         f"incomplete_reason={diag.get('incomplete_reason')} "
         f"input_tokens={usage.get('input_tokens')} "
-        f"output_tokens={usage.get('output_tokens')} "
-        f"reasoning_tokens={usage.get('reasoning_tokens')} "
+        f"output_tokens={out_tokens} "
+        f"reasoning_tokens={reasoning_tokens} "
+        f"visible_tokens={visible_tokens} "
         f"total_tokens={usage.get('total_tokens')} "
         f"error={diag.get('error')!r} refusal={diag.get('refusal')!r}",
         file=sys.stderr)
@@ -1235,9 +1301,14 @@ def extract_session_decisions(
             return copy.deepcopy(hit)
     import httpx  # Lazy: import stays side-effect free.
     api_base = _get_api_base()
+    effort = _resolve_decision_effort(model, effort)
     body: dict[str, Any] = {
         "model": model,
         "input": [{"role": "user", "content": prompt}],
+        # Reasoning tokens are billed as output and count against this cap
+        # on most providers, so send an explicit ceiling instead of leaving
+        # the whole budget to the provider default.
+        "max_output_tokens": _get_decision_max_tokens(),
     }
     if raw_brain_temp or raw_decision_temp:
         body["temperature"] = temp_to_send
diff --git a/skill-templates/decision-migration/SKILL.md b/skill-templates/decision-migration/SKILL.md
index 87079ed..53ff132 100644
--- a/skill-templates/decision-migration/SKILL.md
+++ b/skill-templates/decision-migration/SKILL.md
@@ -19,8 +19,8 @@ Old projects keep manager decisions in their per-project `.opencode/decisions/`
 ## Migration Workflow
 
 1. **Start the dry run at once.** On invocation, go straight to step 3 (dry run) with scope = the current project. Ask NOTHING first — no target question, no scope question, no task-file question. STOP only for the two gates below: (a) a HALT condition in step 2, (b) the batch-approval gate in step 4.
-2. **Resolve endpoints (lookup, never invent).** Source = `<cwd>/.opencode/decisions` (must exist with `decisions/INDEX.md`, else HALT and report — nothing to migrate). Target personal repo, first hit wins: (i) an explicit Manager-provided value; (ii) an already-existing `DECISION_REPO_PATH` env/config key; (iii) the project's `LLM.txt` §7.11 declaration; (iv) a `<parent-of-cwd>/manager-decisions` directory — but ONLY if that directory already exists. If none resolve, HALT and ask the Manager for the target path (this is the ONLY question allowed before the dry run). Never create a target directory unasked; never write to a path the Manager has not effectively confirmed — the resolved target is always printed in the dry-run table, and the batch-approval gate below is the confirmation.
-3. **Dry run first (mandatory).** Read every source record. For each: run `sanitize_text` + `verify_clean` mentally via the `record_manager_decision` validation path — do NOT write. Classify: `would-migrate` / `would-skip` (ID already present in target) / `would-reject` (scrub or schema failure, with reason). The three counts must sum to the scanned total. Present the table + counts + resolved target path to the Manager and STOP. No `record_manager_decision` call happens without an explicit Manager batch-approval phrase — any ambiguous reply counts as NOT approved.
+2. **Resolve endpoints (lookup, never invent).** Source = `<cwd>/.opencode/decisions` (must exist with `decisions/INDEX.md`, else HALT and report — nothing to migrate). Target personal repo, first hit wins: (i) an explicit Manager-provided value; (ii) an already-existing `DECISION_REPO_PATH` env/config key; (iii) the project's `LLM.txt` §7.11 declaration; (iv) a `<parent-of-cwd>/manager-decisions` directory — but ONLY if that directory already exists. If none resolve, HALT and ask the Manager for the target path (this is the ONLY question allowed before the dry run) — via the `question` tool when the session capability manifest shows it AVAILABLE, otherwise in prose. Never create a target directory unasked; never write to a path the Manager has not effectively confirmed — the resolved target is always printed in the dry-run table, and the batch-approval gate below is the confirmation.
+3. **Dry run first (mandatory).** Read every source record. For each: run `sanitize_text` + `verify_clean` mentally via the `record_manager_decision` validation path — do NOT write. Classify: `would-migrate` / `would-skip` (ID already present in target) / `would-reject` (scrub or schema failure, with reason). The three counts must sum to the scanned total. Present the table + counts + resolved target path to the Manager and STOP (use the `question` tool when the session capability manifest shows it AVAILABLE, otherwise relay the same content in prose). No `record_manager_decision` call happens without an explicit Manager batch-approval phrase — any ambiguous reply counts as NOT approved.
 3. **Migrate on approval.** For each approved `would-migrate` record: first pre-check the target for an existing identical `migrated_from` value and skip-if-exists (idempotent reruns change nothing). Then persist through `record_manager_decision` (the ONLY write path — scrub + schema + INDEX regen ride along). Carry provenance: `migrated_from: <project-name>/<original-id>` on EVERY migrated record. Never edit the source store; never edit target history in place. Prove source immutability with `git status --porcelain` before and after (source dir must show unmodified).
 4. **Report.** Final counts: migrated / skipped-existing / rejected-with-reasons. Every rejected ID is listed with its reason — never dropped silently. A failed scrub/verify blocks only that record, never the batch.
 
diff --git a/skill-templates/doc-coauthoring/SKILL.md b/skill-templates/doc-coauthoring/SKILL.md
index 3d21e27..e73315e 100644
--- a/skill-templates/doc-coauthoring/SKILL.md
+++ b/skill-templates/doc-coauthoring/SKILL.md
@@ -86,7 +86,7 @@ Inform them clarifying questions will be asked once they've done their initial d
 
 - If user mentions entities/projects that are unknown:
   - Ask if connected tools should be searched to learn more
-  - Wait for user confirmation before searching
+  - Wait for user confirmation before searching (via the `question` tool when the session capability manifest shows it AVAILABLE, otherwise in prose)
 
 - As user provides context, track what's being learned and what's still unclear
 
diff --git a/skill-templates/manager-decision/SKILL.md b/skill-templates/manager-decision/SKILL.md
index 2a556f0..5c3de2e 100644
--- a/skill-templates/manager-decision/SKILL.md
+++ b/skill-templates/manager-decision/SKILL.md
@@ -50,7 +50,7 @@ fallback and surface the one-line store note. Primary interface: the
 ## Sample-Evolution Loop (Review Gate Mandatory)
 
 1. `propose_profile_evolution()` runs `scripts/compile_profile.py` and returns a `DRAFT_READY` draft (category distribution + recurring rationales). It NEVER writes to the sample.
-2. Present the draft to the manager; on `APPROVED`, merge the reviewed text into `samples/manager_profile.md` baseline-adjacent generated section.
+2. Present the draft to the manager (via the `question` tool when the session capability manifest shows it AVAILABLE, otherwise in prose); on `APPROVED`, merge the reviewed text into `samples/manager_profile.md` baseline-adjacent generated section.
 3. On `REJECTED`, record the rejection rationale as a decision (category `process`) so the next draft learns from it.
 4. Identity updates without approval are forbidden — auto-promotion does not exist by design.
 
diff --git a/skill-templates/opencode-init/SKILL.md b/skill-templates/opencode-init/SKILL.md
index e15eb15..fddb888 100644
--- a/skill-templates/opencode-init/SKILL.md
+++ b/skill-templates/opencode-init/SKILL.md
@@ -14,6 +14,8 @@ Analyze stack files, ask the user for gaps (default agent,
 formatter, LSP guidance, instructions, permissions), emit JSON matching
 the public schema (https://opencode.ai/config.json),
 then validate with `scripts/validate-opencode.py` before writing.
+For every gap question, use the `question` tool when the session capability
+manifest shows it AVAILABLE; otherwise relay the same question in prose.
 MCP servers and plugins install GLOBALLY — never emit `mcp` or `plugin`
 into the project file. Never edit global config. Never install plugins.
 
diff --git a/skill-templates/prompt-refactor/SKILL.md b/skill-templates/prompt-refactor/SKILL.md
index 2956fce..5a8278b 100644
--- a/skill-templates/prompt-refactor/SKILL.md
+++ b/skill-templates/prompt-refactor/SKILL.md
@@ -44,7 +44,7 @@ Provide the exact XML or JSON structure the AI must use to reply, ensuring it ca
 Before translating or refactoring, scan the raw input for:
 
 1. **Obvious typos** — Correct them silently. Log corrections in the output.
-2. **Hallucinated/nonsensical words** — If a word has no meaning in context, flag it and ask the Manager for clarification.
+2. **Hallucinated/nonsensical words** — If a word has no meaning in context, flag it and ask the Manager for clarification (via the `question` tool when the session capability manifest shows it AVAILABLE, otherwise in prose).
 3. **Ambiguity score** — Rate the input clarity from 1 to 5. If below 3, HALT and request clarification before proceeding.
 
 Output a brief correction note at the top of your response:
diff --git a/skill-templates/telegram-message-export/SKILL.md b/skill-templates/telegram-message-export/SKILL.md
index 89eabf6..f598d82 100644
--- a/skill-templates/telegram-message-export/SKILL.md
+++ b/skill-templates/telegram-message-export/SKILL.md
@@ -17,7 +17,7 @@ Determine the exact `[from_id, to_id]` range. If the Manager provided a text sni
 
 1. Call `telegram_get_history` and filter to keep messages where `id >= from_id` and `id <= to_id`.
 2. Sort the filtered messages strictly by `id` in ascending order.
-3. If the range spans more than 200 messages, use the `question` tool to ask for confirmation before proceeding to avoid rate limits.
+3. If the range spans more than 200 messages, ask for confirmation before proceeding to avoid rate limits. Use the `question` tool when the session capability manifest shows it AVAILABLE; otherwise relay the same question in prose and wait for the answer.
 
 ## Phase 2: Extraction & Sidecar Generation
 
diff --git a/tests/test_brain_bridge.py b/tests/test_brain_bridge.py
index 1bcda59..b8d7916 100644
--- a/tests/test_brain_bridge.py
+++ b/tests/test_brain_bridge.py
@@ -1869,6 +1869,38 @@ def test_output_budget_hint_contract():
     assert "reasoning=18" in hint
 
 
+def test_log_provider_diagnostics_reports_visible_tokens(capsys):
+    """The diag line exposes the visible-token count (output minus reasoning).
+
+    A near-zero value there is the signature of a reasoning trace that ate
+    the whole output budget, so the field is the measurement the budget fix
+    relies on.
+    """
+    bridge._log_provider_diagnostics({
+        "status": "completed",
+        "incomplete_reason": None,
+        "usage": {"input_tokens": 10, "output_tokens": 100,
+                  "reasoning_tokens": 90, "total_tokens": 110},
+        "error": None,
+        "refusal": None,
+    })
+    err = capsys.readouterr().err
+    assert "visible_tokens=10" in err
+    assert "reasoning_tokens=90" in err
+
+
+def test_log_provider_diagnostics_visible_tokens_none_without_usage(capsys):
+    """Missing usage must not crash or invent a visible count."""
+    bridge._log_provider_diagnostics({
+        "status": "incomplete",
+        "incomplete_reason": "max_output_tokens",
+        "usage": {},
+        "error": None,
+        "refusal": None,
+    })
+    assert "visible_tokens=None" in capsys.readouterr().err
+
+
 def test_brain_turn_budget_exhaustion_is_terminal(tmp_path, monkeypatch, capsys):
     payload = {
         "status": "incomplete",
@@ -2245,8 +2277,8 @@ def test_routing_disabled_by_default_preserves_behavior(tmp_path, monkeypatch):
     result, holder = _run_turn_capture(monkeypatch, tmp_path, _ok_payload("ok"))
     assert result["output"] == "ok"
     assert holder["body"]["model"] == "gpt-6-astra"
-    assert holder["body"]["reasoning"] == {"effort": "xhigh"}
-    assert holder["body"]["max_output_tokens"] == 16384
+    assert holder["body"]["reasoning"] == {"effort": "medium"}
+    assert holder["body"]["max_output_tokens"] == 32768
     # Disabled + explicit tier: wiring must stay on the default model.
     result, holder = _run_turn_capture(
         monkeypatch, tmp_path, _ok_payload("ok"), task_id="233",
@@ -2292,8 +2324,8 @@ def test_routed_body_uses_selected_model(tmp_path, monkeypatch):
     assert result["output"] == "ok"
     assert result["model"] == "low-m"
     assert holder["body"]["model"] == "low-m"
-    assert holder["body"]["reasoning"] == {"effort": "xhigh"}
-    assert holder["body"]["max_output_tokens"] == 16384
+    assert holder["body"]["reasoning"] == {"effort": "medium"}
+    assert holder["body"]["max_output_tokens"] == 32768
     result, holder = _run_turn_capture(
         monkeypatch, tmp_path, _ok_payload("ok"), task_id="233",
         risk_tier="T2")
diff --git a/tests/test_brain_capability.py b/tests/test_brain_capability.py
index e11ca1f..234f3a1 100644
--- a/tests/test_brain_capability.py
+++ b/tests/test_brain_capability.py
@@ -32,16 +32,14 @@ def test_all_available_tools_report_available():
                         "brain_turn": "AVAILABLE"}
 
 
-def test_question_tool_required_is_unavailable_required():
+def test_question_tool_is_available():
     manifest = capability.build_manifest(
         referenced=["question"], required=["question"])
-    assert manifest == {"question": "UNAVAILABLE_REQUIRED"}
+    assert manifest == {"question": "AVAILABLE"}
 
 
-def test_question_tool_optional_is_unavailable_optional():
-    manifest = capability.build_manifest(
-        referenced=["question"], required=[])
-    assert manifest == {"question": "UNAVAILABLE_OPTIONAL"}
+def test_known_unavailable_registry_is_empty():
+    assert capability.KNOWN_UNAVAILABLE == frozenset()
 
 
 def test_unknown_required_tool_fails_closed():
@@ -58,9 +56,9 @@ def test_unknown_optional_tool_is_unavailable_optional():
 
 def test_caller_available_override_wins():
     manifest = capability.build_manifest(
-        referenced=["question"], required=["question"],
-        available={"question"})
-    assert manifest == {"question": "AVAILABLE"}
+        referenced=["frobnicate"], required=["frobnicate"],
+        available={"frobnicate"})
+    assert manifest == {"frobnicate": "AVAILABLE"}
 
 
 def test_caller_unavailable_override_marks_required():
@@ -70,12 +68,24 @@ def test_caller_unavailable_override_marks_required():
     assert manifest == {"lint_task_file": "UNAVAILABLE_REQUIRED"}
 
 
+def test_unavailable_override_demotes_granted_question_tool():
+    """An explicit unavailable override still demotes a granted tool.
+
+    `question` is in `AVAILABLE_EXACT` now, so this pins the override path
+    for a registry-available name rather than an unknown one.
+    """
+    manifest = capability.build_manifest(
+        referenced=["question"], required=["question"],
+        unavailable={"question"})
+    assert manifest == {"question": "UNAVAILABLE_REQUIRED"}
+
+
 def test_only_three_statuses_exist():
     assert capability.STATUSES == (
         "AVAILABLE", "UNAVAILABLE_REQUIRED", "UNAVAILABLE_OPTIONAL")
     manifest = capability.build_manifest(
         referenced=["brain_turn", "question", "frobnicate"],
-        required=["question", "frobnicate"])
+        required=["frobnicate"])
     assert set(manifest.values()) <= set(capability.STATUSES)
 
 
@@ -83,10 +93,10 @@ def test_internal_registry_name_never_emitted_as_status():
     manifest = capability.build_manifest(
         referenced=["brain_turn", "question", "frobnicate",
                     "lint_task_file"],
-        required=["brain_turn", "question", "frobnicate",
-                  "lint_task_file"])
+        required=["brain_turn", "frobnicate", "lint_task_file"])
     assert "KNOWN_UNAVAILABLE" not in manifest.values()
-    assert manifest["question"] == "UNAVAILABLE_REQUIRED"
+    assert manifest["frobnicate"] == "UNAVAILABLE_REQUIRED"
+    assert manifest["question"] == "AVAILABLE"
 
 
 def test_empty_referenced_gives_empty_manifest():
@@ -97,26 +107,27 @@ def test_empty_referenced_gives_empty_manifest():
 
 def test_gate_passes_with_no_missing_required():
     manifest = capability.build_manifest(
-        referenced=["lint_task_file", "question"], required=["lint_task_file"])
+        referenced=["lint_task_file", "frobnicate"],
+        required=["lint_task_file"])
     assert capability.gate(manifest, stage="qa") is None
 
 
 def test_gate_raises_naming_missing_tools():
     manifest = capability.build_manifest(
-        referenced=["question"], required=["question"])
+        referenced=["frobnicate"], required=["frobnicate"])
     with pytest.raises(capability.CapabilityBlockedError) as exc:
         capability.gate(manifest, stage="review")
-    assert "question" in str(exc.value)
+    assert "frobnicate" in str(exc.value)
     assert "review" in str(exc.value)
 
 
 def test_gate_error_carries_relay_block():
     manifest = capability.build_manifest(
-        referenced=["question"], required=["question"])
+        referenced=["frobnicate"], required=["frobnicate"])
     with pytest.raises(capability.CapabilityBlockedError) as exc:
         capability.gate(manifest, stage="review")
     block = capability.format_relay_block(exc.value)
-    assert "question" in block
+    assert "frobnicate" in block
     assert "review" in block
 
 
@@ -229,9 +240,9 @@ def test_brain_turn_missing_required_returns_non_verdict_report(
     call = bridge.brain_turn
     target = call.fn if hasattr(call, "fn") else call
     result = target("review this", task_id="257", project_root=str(proj),
-                    stage="review", required_tools=["question"])
+                    stage="review", required_tools=["frobnicate"])
     assert result["status"] == "REPORT"
-    assert "question" in result["output"]
+    assert "frobnicate" in result["output"]
     for verdict in ("QA_PASSED", "QA_REJECTED", "VERDICT:",
                     "PO_REVIEW_PENDING", "APPROVED"):
         assert verdict not in result["output"]
diff --git a/tests/test_decision_server.py b/tests/test_decision_server.py
index b397525..290bd63 100644
--- a/tests/test_decision_server.py
+++ b/tests/test_decision_server.py
@@ -833,7 +833,8 @@ def test_temperature_pinned_zero_unless_set(srv, tmp_path, monkeypatch):
     _stub_capture(_decision_resp(200, "fine", envelope))
     _extract(srv)(7, transcript_path=str(transcript))
     assert "temperature" not in seen["body"]
-    assert seen["body"]["reasoning"] == {"effort": "xhigh"}
+    assert seen["body"]["reasoning"] == {"effort": "high"}
+    assert seen["body"]["max_output_tokens"] == 16384
     assert "reasoning_effort" not in seen["body"]
     srv._EXTRACT_CACHE.clear()
     monkeypatch.setenv("BRAIN_TEMPERATURE", "0.7")
@@ -932,7 +933,8 @@ def test_extract_repeat_determinism_five_times(srv, tmp_path, monkeypatch, capsy
     assert calls["n"] == 1  # Cache serves repeats: exactly one HTTP hit.
     blobs = [json.dumps(r, sort_keys=True) for r in results]
     assert all(b == blobs[0] for b in blobs)  # Byte-identical 5x.
-    assert calls["bodies"][0]["reasoning"] == {"effort": "xhigh"}  # Max-effort default.
+    assert calls["bodies"][0]["reasoning"] == {"effort": "high"}  # Model-default effort.
+    assert calls["bodies"][0]["max_output_tokens"] == 16384
     assert capsys.readouterr().err.count("cache hit") == 4
 
 
@@ -1095,7 +1097,8 @@ def test_extract_temp_wire_default_zero(srv, tmp_path, monkeypatch):
                   seen)
     _extract(srv)(21, transcript_path=str(transcript))
     assert "temperature" not in seen[0]
-    assert seen[0]["reasoning"] == {"effort": "xhigh"}
+    assert seen[0]["reasoning"] == {"effort": "high"}
+    assert seen[0]["max_output_tokens"] == 16384
     assert "reasoning_effort" not in seen[0]
 
 
@@ -1115,6 +1118,36 @@ def test_extract_override_wins_and_key_changes(srv, tmp_path, monkeypatch):
             != srv._extract_cache_key(raw, "m", 0.0))
 
 
+def test_log_responses_diagnostics_reports_visible_tokens(srv, capsys):
+    """The diag line exposes the visible-token count (output minus reasoning)."""
+    srv._log_responses_diagnostics({
+        "status": "completed",
+        "incomplete_reason": None,
+        "usage": {"input_tokens": 10, "output_tokens": 100,
+                  "reasoning_tokens": 90, "total_tokens": 110},
+        "error": None,
+        "refusal": None,
+    })
+    err = capsys.readouterr().err
+    assert "visible_tokens=10" in err
+    assert "reasoning_tokens=90" in err
+
+
+def test_resolve_decision_effort_coerces_unadvertised(srv, capsys):
+    """An effort the model does not advertise is coerced to its default.
+
+    The decision effort falls back to the shared `BRAIN_REASONING_EFFORT`,
+    and the Brain model advertises `xhigh` while DeepSeek V4.1 Flash does
+    not, so the inherited value must not reach the provider unchanged.
+    """
+    assert srv._resolve_decision_effort("deepseek/deepseek-v4.1-flash", "high") == "high"
+    assert srv._resolve_decision_effort("deepseek/deepseek-v4.1-flash", "xhigh") == "high"
+    assert "not among" in capsys.readouterr().err
+    # Unknown models keep the configured value and warn about nothing.
+    assert srv._resolve_decision_effort("unknown/model", "xhigh") == "xhigh"
+    assert capsys.readouterr().err == ""
+
+
 def test_extract_effort_absent_both_legs(srv, tmp_path, monkeypatch):
     transcript = tmp_path / "transcript.jsonl"
     _write_min_transcript(transcript)
@@ -1133,7 +1166,7 @@ def test_extract_effort_absent_both_legs(srv, tmp_path, monkeypatch):
         body = seen[-1]
         if temp is None:
             assert "temperature" not in body
-            assert body["reasoning"] == {"effort": "xhigh"}
+            assert body["reasoning"] == {"effort": "high"}
         else:
             assert body["temperature"] == 0.7
             assert "reasoning" not in body
```
<!-- END_GIT_DIFF -->
