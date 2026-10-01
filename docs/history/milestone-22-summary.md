# Milestone 22 Summary

**Date:** 2026-10-01
**Tasks Compacted:** 9

## Source Distribution

| Source       | Count |
| ------------ | ----- |
| orchestrator | 0     |
| telegram     | 2     |
| manager      | 7     |

## Architectural Changes

This milestone completed the **singleton + OpenCode-2 consolidation** of the whole platform, then hardened the agent workflow on top of it. The mid-milestone keystone was the bundled META **279 (mcp-singleton-rollout, superseding 277–278)**, which cut every session's per-process stdio MCP fan-out (12 observed processes) over to **one supervised remote instance per server bound to `127.0.0.1`** — the 6 Python units gain `Restart=always`/`RestartSec=3` + venv-interpreter `ExecStart`, all 7 ports listen loopback-only, and the global `opencode.json` was migrated from stdio to 7 `type: remote` URLs shared across sessions and projects. Because a shared singleton loses per-session cwd context, 279 also added an **OPTIONAL `project_root` parameter to all 24 tools** (context 8, memory 6, lint 4, decision 6) with validation V1–V5, then closed the resulting cross-project contamination finding (F6/V1) by adding a `ContextVar`-backed `_project_tool` decorator that surfaces a client-visible `WARNING [project-isolation]` banner (str first-line, or an additive dict key for the decision tool) whenever the cwd fallback fires; the transport default simultaneously flipped from `stdio` to `streamable-http` (V3) while keeping explicit `stdio` working.

Task **283** then removed the machinery the singleton made obsolete: **all OpenCode plugins were eliminated** (goal, DCP/compress, retry), the rate-limit-rescue plugin (built in **282**) was archived to `archive/rate-limit-rescue/`, `docs/openchamber-tailscale.md` became `docs/openchamber.md`, and the machine was reduced to **exactly one OpenCode instance managed by `openchamber.service`** (background `opencode serve --service` disabled). It also repaired real global-install bugs found while following `LLM.txt`, documented the `.env` self-load contract, and recovered the Telegram MCP credentials from the 2026-09-29 backup.

In parallel, the **prompt/agent contract** moved through three shipped-prompt bumps. Task **280** fixed the supervised-autopilot plan-approval chain so acceptance routes back through the Brain to a Senior Programmer XML blueprint before any implementation (the defect lived in the hand-maintained `agents/cognitive-executor.md`, not the generated fragments) and moved the knowledge-cutoff line. Task **281** made the prompt **mode-aware** (single `MODE:` banner parameter per the unanimous seven-seat brainstorm, with automatic-mode overrides that suppress Manager copy-paste ferry wording in the QA/Reviewer/Hands sections). Task **276** made approval gates call the `question` tool and gave brainstorming a self-firing trigger. Task **275** was a read-only audit that cleared all five Python MCP servers as PASS on the SDK v1 pinned line (`mcp[cli]>=1.0,<2.0`, locked 1.30.0) against the current 2026-07-28 spec and Python SDK v2.2.0. Task **274** verified both plugins at full V2 standing without filing duplicate upstream issues, and Task **273** was the v9.46.0 release ceremony that archived milestone-21.

## Files Modified

| File | Change |
| ---- | ------ |
| `docs/history/milestone-21-summary.md` | new: 7-task compaction (266–272) (273) |
| `docs/history/milestone-22-summary.md` | new: this 9-task compaction (273 compaction output) |
| `tasks/archive/266-*.md` … `tasks/archive/272-*.md` | released tasks moved to archive (273) |
| `CHANGELOG.md` | 9.46.0 release block (273); plugin V2 entry (274); [Unreleased] entries (275–283); retry archive + 30→2 retry-delay entries (283) |
| `README.md` | plugin V2 status + `@latest (currently 3.2.0)` (274); singularity + legacy stdio pointer + never-`uv run` (279, 283) |
| `LLM.txt` | plugin V2 status §7.7 (274); singleton setup/migration/schema (279); full V2 rewrite + `.env` contract + correct §4–§5 global-install copy/seed (283) |
| `opencode.json` (global) | stdio → 7 `type: remote` loopback URLs (279); V2-native mcp.servers/permissions; blowsh timeout restored 120000 (283) |
| `~/.config/opencode/cli.json` | schema-only V2 client config (283) |
| `tui.json` (repo + global) | deleted (283) |
| `docs/services.md` | singleton units + creds/`.env` section + launchd/Windows notes (279, 283) |
| `docs/setup.md` | singleton setup + canonical full-dep suite command pointer (279, 283) |
| `docs/openchamber.md` | new: replaces deleted `docs/openchamber-tailscale.md`; managed OpenCode, no Tailscale, no plugin content (283) |
| `docs/brain-bridge.md`, `docs/telegram-setup.md` | `.env` self-load contract (283) |
| `services/mcp-{brain,context,decision,lint,memory,telegram}.service` | systemd units, `Restart=always`, loopback bind, pinned `MCP_TRANSPORT` (279) |
| `services/launchd/ai.cognitivelead.mcp-*.plist` | 6 plists; telegram `http` transport (279) |
| `services/windows/*` | Windows scheduled-task template + env notes (279) |
| `mcp-context-server/server.py` | `project_root` on 8 tools + `_project_tool` isolation banner + transport default (279) |
| `mcp-memory-server/server.py` | `project_root` on 6 tools + `_memory_dir` threading + banner + transport default (279) |
| `mcp-lint-server/server.py` | `project_root` on 4 tools + banner + transport default (279) |
| `mcp-decision-server/server.py` | `project_root` on 6 tools + `_repo_root` override + banner dict key + transport default (279) |
| `mcp-common/env.py` | persona-server mention removed (283) |
| `prompts/fragments/01-system_version.md` | 9.47.0 (276) → 9.48.0 (280) → 9.49.0 (281) |
| `prompts/fragments/03-system_context.md` | knowledge-cutoff O2 unverified marker (280) |
| `prompts/fragments/05-user_input_processing.md` | brainstorm trigger append (276) |
| `prompts/fragments/06-personas.md` | QA/Reviewer automatic-mode overrides (281) |
| `prompts/fragments/09-hands_protocols.md` | automatic-mode skip-ferry overrides in both summary blocks (281) |
| `prompts/fragments/11-execution_workflow.md` | question-tool gate Steps 3/4/8 + brainstorm auto-eval Step 2 (276) |
| `prompts/fragments/12-brainstorming_protocol.md` | brainstorm trigger + auditability append (276) |
| `prompts/fragments/19-initialization.md` | MODE declaration banner (281) |
| `agents/cognitive-executor.md` | question-tool mandate + capability preflight (276); plan-approval → Brain → Programmer XML routing fix + Seat Check (280) |
| `system-prompt.md` | regenerated each bump: 9.47.0 (276), 9.48.0 (280), 9.49.0 (281) |
| `tests/test_prompt_sync.py` | version pin 9.47.0 (276) |
| `plugins/rate-limit-rescue/{package.json,index.js,README.md,test.mjs,package-lock.json}` | new: free-tier 429 rescue + JSONL metrics (282) |
| `archive/rate-limit-rescue/` | plugin archived, removed from all configs (283) |
| `scripts/fetch-opencode-docs.py`, `scripts/repomd`, `docs/velocity.md` | orphaned files deleted (283) |
| `.opencode/{package.json,package-lock.json,node_modules,commands}`, `.pytest_cache/` | plugin-SDK leftovers deleted (283) |
| `.opencode/memory/` | 3 stale shards deleted, V2/password memories refreshed, index rebuilt (279, 283) |
| `.opencode/memory/workflows/global-install-upgrade.md` | singleton migration step, streamable-http line, decision-server list (279, 283) |
| `.gitignore` | `node_modules/` (282); goals/worktrees guards restored (283) |
| `~/.config/opencode/.env` | seeded chmod-600 + Telegram `TELEGRAM_*` recovered (283) |
| `/tmp/cognitive-lead-push-release.sh` | executable v9.46.0 push/tag/release script, strict mode (273) |

## Criteria Met

| Task | Acceptance Criteria | Status |
| ---- | ------------------- | ------ |
| 273 | milestone-21 compacts 266–272 + all 7 archived; CHANGELOG `[9.46.0]` moved + `[Unreleased]` empty; all gates exit 0; push script strict + executable; stale-memory report, no deletion | ✅ Met (5/5) |
| 274 | Both plugins latest stable w/ genuine V2 support; no duplicate upstream issues; README + LLM.txt exact versions; lint; verification evidence | ✅ Met (5/5) |
| 275 | All 5 servers inventoried; current web data with sources; per-server pass/flag findings; **no source code modified** | ✅ Met (4/4) |
| 276 | Approval gates use `question` tool; brainstorming self-triggers; agents + prompt consistent, sync passes; CHANGELOG + lint/suite green | ✅ Met (4/4) |
| 279 | One OS process/server; 7 MCP shared across sessions; single server + OpenChamber healthy; supervised loopback services; memory migration; opencode-2 schema clean; service files present | ✅ Met (7/12) — META all-or-nothing gate **open**: `[277]` stdio rollback revert, `[278]` fresh-user e2e, global-upgrade-at-latest, blowsh triple-transport, and commit-gated traceability boxes left unchecked (window/foreign-repo/commit-gated, documented) |
| 280 | Plan-approval routes back through Brain → Programmer XML (no direct implement-on-approve); cutoff updated to honest unverified marker + prompt regenerated; evidence recorded | ✅ Met (3/3) |
| 281 | Brainstorm report A-vs-B + Manager selection; winning option in fragments + regen, no manual ferry in automatic mode; evidence recorded | ✅ Met (3/3 AC) — DoD `lint_task_file` box left unchecked |
| 282 | Free-tier 429 runs env command + JSONL metrics + 30s retry (proven); both paths env-overridable; plugin installed globally + listed | ⚠️ Partial (2/3 AC) — global-install/listed box unchecked; DoD `CHANGELOG.md` box also unchecked |
| 283 | One OpenChamber-managed OpenCode instance; zero plugins + absent refs; retry plugin archived/unreferenced; docs aligned to V2; orphans removed; global install 7 MCP; Telegram verified both accounts | ✅ Met (7/7) |

## Individual Task Summaries

### Task 273: Release v9.46.0 with milestone-21 archive

- **Type:** feature
- **Source:** manager
- **Reasoning:** Cut v9.46.0 per the release memory: wrote `docs/history/milestone-21-summary.md` (7 files, 1054 lines, delegated to a subagent and its claims verified by grep) and `git mv`'d tasks 266–272 to `tasks/archive/`, then moved `[Unreleased]` entries under `## [9.46.0] - 2026-09-26`. All gates passed (689 tests, lint, byte-identical prompt re-assembly since `system-prompt.md` was already at 9.46.0, `check_docs_sync.py` OK); wrote `/tmp/cognitive-lead-push-release.sh` and staged via MCP. A stale-memory audit found zero stale entries. Closed on a direct Manager "close it" order (no Brain review ferry, recorded honestly), committed via `commit_and_clean_task`.

### Task 274: Plugins full V2 status — verify latest, document, no duplicate upstream issues

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Verified `opencode plugin list` → goal-plugin 0.1.52 + dcp 3.2.0, both npm-confirmed latest stable; corrected the earlier "V1-only" misread (goal PR #49/#58 already shipped full V2 adaptation). Confirmed DCP V2 threads (#627/#628/#631/#632) already open so **no duplicate issues were filed**. Updated README + LLM.txt §7.7 with exact versions and update procedure, stored memory, and closed after reviewer APPROVED + Manager "Approved for closure".

### Task 275: Audit five Python MCP servers against current web data

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Read-only audit of the 5 hand-written Python servers (8,427 LOC) against current MCP spec (2026-07-28) and Python SDK (v2.2.0 stable; v1.x maintenance, locked 1.30.0). Verdict: **all five PASS, keep as-is** — stdio + loopback is the correct local shape, `mcp>=1.0,<2.0` is the upstream-advised posture, zero dangerous patterns, no tokens, and `mcp-persona-server` is confirmed gone. No code changed. Logged subagent/brain-tool runtime deviations and a deferred one-line memory correction (Q1); Manager ordered closure with staging via tools.

### Task 276: Question-tool approval gates and brainstorming auto-load

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Encoded the approval-gates-use-`question`-tool rule into the executor capability preflight and fragment 11 Steps 3/4/8, and made brainstorming self-evaluate (fragment 11 Step 2 + fragment 12 trigger/auditability + fragment 05 + executor Seat Check). Bumped 9.46.0 → 9.47.0 and regenerated the prompt; after QA nits a hotfix restored dropped words and added unavailable-tool fallbacks. Final regen 95089 bytes, suite 689 passed; reviewer APPROVED + PO_REVIEW_PENDING, closed on "Approved for closure" and the `git mv` finished 2026-10-01 once a shell existed.

### Task 279: mcp-singleton-rollout (META, supersedes 277–278)

- **Type:** feature
- **Source:** manager
- **Reasoning:** Bundled META converting per-session stdio MCP fan-out into **6 supervised loopback singletons** (systemd/launchd/Windows units, `Restart=always`, 7 ports on `127.0.0.1`) plus global `opencode.json` → 7 `type: remote` URLs. Added OPTIONAL `project_root` to all 24 tools (V1–V5 validation), then fixed the F6/V1 isolation leak with a per-call `_project_tool` ContextVar banner and flipped the transport default (V3). Live proofs: 7/7 connected across 4 cwd contexts, 6 processes stable, 6/6 units active, rollback artifact verified. Closed on "Approved for closure" after 5 QA rounds; residuals (destructive rollback/fresh-clone/upgrades/blowsh-task-10/traceability) documented as still parked.

### Task 280: Autopilot plan-approval loop fix and Muse cutoff update

- **Type:** improvement
- **Source:** telegram
- **Reasoning:** Brainstorm/Architect root-caused the skip to `agents/cognitive-executor.md:259-267` (the hand-maintained agent, not the generated fragments): after plan approval the Hands implemented directly instead of returning through the Brain to a Senior Programmer XML. Fixed the routing and moved the cutoff to the honest "explicitly-unverified marker" (no authoritative Muse Spark 1.3 date exists), bumping 9.47.0 → 9.48.0 and rebuilding the prompt (byte-identical `cmp`). QA_PASSED + reviewer APPROVED; closed on "Approved for closure". Logged a follow-up: `lint_system_prompt_sync` ignores `project_root` for the assembler path.

### Task 281: Mode-aware system prompt (manual vs automatic) with brainstorm

- **Type:** bug
- **Source:** telegram
- **Reasoning:** A full seven-seat brainstorm unanimously chose **O1 — a single mode-parameterized prompt** over two files; Manager selected O1. Applied fragments-only edits: a `MODE:` declaration in 19-initialization and automatic-mode overrides in fragments 06 (QA/Reviewer) and 09 (both Hands summary blocks) so no Manager ferry/copy-paste instruction remains active in automatic mode; bumped 9.48.0 → 9.49.0 and rebuilt (96389 bytes, `cmp` exit 0). QA hardening added a safe `manual` default, "automatic ≡ autopilot", and a clean negative ferry grep. QA_PASSED + reviewer APPROVED; closed on approval (DoD `lint_task_file` box remains unchecked).

### Task 282: Rate-limit rescue plugin (rr rotation + 30s retry + metrics)

- **Type:** feature
- **Source:** manager
- **Reasoning:** Shipped `plugins/rate-limit-rescue/` firing **only on free-tier 429s**, using `Plugin.define` + `ctx.session.hook("retry")`. It runs the env-configured command (default `rr`), appends a JSONL metrics line, and sets a 30s retry delay. Grounding against the real `opencode.log` (which has no status code, only `AI.Error.QuotaExceeded`) forced the gate to rate-ish **and** free-ish-model instead of a `status===429` check; the hook never throws. Committed `test.mjs` (8/8) plus envelope-detail metrics. QA passed all rounds and the reviewer APPROVED; closed on approval. Global install/listing remained unchecked, and no CHANGELOG entry was made (DoD box unchecked) — the plugin was later archived in 283.

### Task 283: OpenCode V2 + OpenChamber 2 migration, plugin removal, docs audit, global install

- **Type:** improvement
- **Source:** manager
- **Reasoning:** Executed the 7-part Manager order: migrated configs to V2-native (`plugins`, `permission.shell`, `mcp.servers`, deleted `tui.json`); **removed every OpenCode plugin** and archived `rate-limit-rescue`; rewrote `docs/openchamber-tailscale.md` → `docs/openchamber.md` (Tailscale gone); deleted orphans (`fetch-opencode-docs.py`, `repomd`, `velocity.md`, plugin-SDK dirs); fixed real `LLM.txt` install bugs (all server modules + decision-server now copied, `.env` seed no longer clobbers/nests); reduced the machine to **1 OpenChamber-managed OpenCode** instance; performed the global install (7 MCP connected) and recovered/enabled Telegram (both accounts verified). Survived two QA rejections and one reviewer-found CHANGELOG truncation (restored + merged correctly, 96 release sections intact); final APPROVED + QA_PASSED, closed on "Approved for closure".
