# Research Report 04 — Multi-Agent Brainstorming Session

> **Purpose:** Six-persona brainstorming session analyzing which best practices Cognitive Lead AI HQ should adopt, in what order, and with what architecture.
> **Date:** 2026-08-18
> **Method:** brainstorm-swarm skill — independent persona analysis, conflict resolution, synthesized recommendation.
> **Inputs:** Reports 01–03 (competitive landscape, gap analysis, deep-dive dossier).

---

## Problem Statement

Cognitive Lead AI HQ is a documentation-only repository powering a Brain/Hands multi-agent workflow (Orchestrator + OpenCode/Freebuff executor) with 3 MCP servers, 27 skill templates, a V6 Kanban task lifecycle, and a manual QA persona loop. Research identified 15 best practices from top projects (Anthropic evals, superpowers, mem0, strands agent-sop, LangGraph, CrewAI) that HQ does not currently support. **Which practices should be adopted, in what order, and with what architecture?**

---

## Brainstorming Session Output

```xml
<brainstorming_session>
  <summary>
    The swarm converged on a phased adoption strategy: Phase 1 (foundation, low effort) — session-start hooks/bootstrap, standardized SOP format with validator, version-bump manifest, security rules, memory benchmarks; Phase 2 (differentiation, medium effort) — automated eval harness with trace recording and capability/regression split, semantic memory upgrade, multi-platform plugin manifests; Phase 3 (scale, high effort) — durable execution, observability, SOP multi-modal distribution. The eval harness is the single highest-value investment but must be built incrementally (20-50 seed tasks) and paired with trace recording from day one. Semantic memory and eval infrastructure are the two pillars that convert HQ from a prompt-distribution repo into a self-improving platform.
  </summary>

  <persona_responses>
    <response persona="system_architect">
      <analysis>
        HQ's architecture is a pipeline: system-prompt (Brain) → XML task blocks → executor (Hands) → task files → QA loop. The 15 gaps map cleanly onto this pipeline: hooks/bootstrap and trace recording attach to the executor; evals attach to the QA stage; memory attaches to the MCP layer; plugin manifests attach to distribution. The highest-leverage architectural change is making the task file the universal record: it already carries the diff (via stage_and_inject_diff); adding a transcript section (tool calls, reasoning, metrics) turns it into the eval substrate without new infrastructure. The eval harness should be a new MCP tool (eval server) rather than a Brain-side persona, because grading needs deterministic access to task files, diffs, and git state. Durable execution (checkpointing) is architecturally the most invasive change — it requires per-step state persistence in the executor protocol — and should be deferred until the eval layer proves which steps actually fail mid-execution. Multi-platform manifests are a packaging concern: a generator script (like superpowers' bump-version.sh pattern) can emit .claude-plugin/.codex-plugin/.cursor-plugin from the existing skill-templates/ without touching the core pipeline.
      </analysis>
      <recommendations>
        <item>Adopt the task file as the universal execution record: add a "Trace" section (tool calls, reasoning summary, tracked_metrics: n_turns, n_toolcalls, n_total_tokens) written by the executor at each phase — this is the substrate for evals, debugging, and observability with zero new services.</item>
        <item>Build the eval harness as a fourth MCP server (mcp-eval-server) with scenario YAML files, deterministic graders (structure, diff quality, guardrail compliance) + LLM-judge graders with isolated rubrics per dimension, and pass^k consistency across 3 trials.</item>
        <item>Implement session-start hooks as a lightweight bootstrap injected by the executor agent definition (AGENTS.md/agent files), not a runtime hook system — OpenCode/Freebuff already load instruction files at session start; the bootstrap text activates the Skill Auto-Loading Matrix automatically.</item>
        <item>Defer durable execution/checkpointing to Phase 3; first instrument failure points via trace recording, then add resume markers only where traces show real mid-execution failures.</item>
      </recommendations>
    </response>

    <response persona="security_engineer">
      <analysis>
        Three security-relevant gaps exist. First, no dedicated security rules: obviousworks ships security_rules.md with explicit guardrails against AI-generated vulnerabilities (prompt injection, secret leakage, path traversal). HQ's MCP servers already implement path-traversal guards (context server rejects escapes) and the shell strategy bans interactive commands — these patterns should be codified into a security_rules.md and lint-checked. Second, trace recording creates a new sensitive-data surface: transcripts will contain tool calls, file paths, and possibly secrets; they must be stored locally, git-ignored or sanitized before commit, and never uploaded to the Brain verbatim if they contain credentials. Third, the eval harness introduces an LLM-judge attack surface: graders must be bypass-resistant (Anthropic's explicit warning) — a task that passes by exploiting a grader loophole teaches the agent to cheat; state_check graders (verify actual environment state, not claims) are the antidote. Memory upgrade also needs scoping: mem0's User/Session/Agent scopes map to namespace isolation; auto-capture must not persist secrets — add a denylist (API keys, tokens, .env contents) to the memory server.
      </analysis>
      <recommendations>
        <item>Create docs/security_rules.md codifying: prompt-injection guardrails, secret-handling policy (never log/store API keys), path-traversal rules, and the existing shell non-interactive strategy — then add lint checks for secrets in task files and memory entries.</item>
        <item>Design trace recording with a sanitization layer: redact env vars, tokens, and private paths before traces are committed or shared; keep raw traces in a git-ignored traces/ directory.</item>
        <item>Make eval graders bypass-resistant: prefer state_check and deterministic tests over self-reported success; add an "Unknown" escape hatch to LLM judges to prevent hallucinated grades; run isolated judges per rubric dimension.</item>
        <item>Add a secret denylist to mcp-memory-server auto-capture (when adopted) so credentials are never persisted as memories.</item>
      </recommendations>
    </response>

    <response persona="product_manager">
      <analysis>
        The user of HQ is the Manager (founder) operating the Brain/Hands loop. Their pain points: (1) no way to know if the system is getting better or worse across releases — the manual QA persona is subjective; (2) skills don't auto-trigger, so quality depends on the Orchestrator remembering to name them; (3) memory is unreliable (keyword search misses context), causing repeated explanations. The highest user-visible value features are: eval harness (turns "the agent feels worse" into measurable pass rates), hooks/bootstrap (consistency without remembering), and semantic memory (fewer repeated instructions). From a roadmap perspective, the eval harness should be framed as "quality baselines for every release" — it directly supports the existing versioning/release discipline (v8.4.6 → v8.5.0) by adding a quality gate. The SOP standardization is a developer-experience win: parameterized SOPs with MUST/SHOULD/MAY constraints make task generation more deterministic, which the Manager experiences as fewer failed task executions. MVP scope: do NOT attempt all 15; ship Phase 1 (5 low-effort items) in one release cycle, measure, then Phase 2.
      </analysis>
      <recommendations>
        <item>Frame the eval harness as a release quality gate: every version bump (v8.x.y) must include eval suite results — this ties the new infrastructure to the existing changelog/versioning ritual the Manager already trusts.</item>
        <item>Prioritize hooks/bootstrap and SOP standardization as the two "consistency" features that reduce Manager supervision burden — they require zero new user workflow, only better defaults.</item>
        <item>Define success metrics for the adoption itself: (a) % of tasks passing eval suite on first QA pass, (b) % of sessions where skills auto-triggered correctly, (c) memory recall precision on a fixed 20-question benchmark.</item>
        <item>Ship in 3 phases with a release each: Phase 1 foundation (hooks, SOP format, version manifest, security rules, memory benchmarks), Phase 2 differentiation (evals + traces, semantic memory, plugin manifests), Phase 3 scale (durable execution, observability, multi-modal SOP distribution).</item>
      </recommendations>
    </response>

    <response persona="business_strategist">
      <analysis>
        HQ's moat is the Brain/Hands XML protocol + QA persona loop — no competitor ships this. The adoption strategy should defend and extend that moat. The eval harness is the moat-extender: it converts the QA loop from a persona (replicable by any prompt engineer) into an infrastructure asset (harder to replicate, measurable, improvable). Semantic memory is the retention driver: the Manager's accumulated project knowledge (100 archived tasks, memory files) becomes a compounding asset — mem0's benchmarks (LongMemEval 94.4) show what's achievable vs. keyword search. Multi-platform manifests are the distribution play: 27 skills × 14 platforms = reach; superpowers proved the market (273k stars) for exactly this. Competitive risk: if HQ doesn't adopt evals, the ecosystem (superpowers, strands) will normalize them within 12 months and HQ's QA loop will look obsolete. Cost-benefit: Phase 1 items are near-zero cost (documentation + config), Phase 2 evals are the only significant engineering investment but deliver the largest differentiation. The version-bump manifest and RELEASE-NOTES discipline (superpowers pattern) professionalize the release process — important because the repo is public (GitHub badges, LLM.txt auto-setup) and release quality is a public signal.
      </analysis>
      <recommendations>
        <item>Treat the eval harness as the strategic moat-extender: invest in it before any other Phase 2 item; it converts the QA persona into measurable infrastructure.</item>
        <item>Adopt multi-platform manifests as the distribution strategy — 27 skills × 14 platforms positions HQ as the open alternative to superpowers with a differentiator (orchestration protocol + QA loop).</item>
        <item>Adopt semantic memory as the retention/compounding play — the Manager's knowledge base is the asset; benchmark it (LongMemEval-style) to prove improvement.</item>
        <item>Professionalize releases (version-bump manifest + release notes) because the repo is public and release discipline is a visible quality signal to adopters.</item>
      </recommendations>
    </response>

    <response persona="legal_advisor">
      <analysis>
        Licensing and compliance considerations: (1) The repo is MIT-licensed; adopting patterns from superpowers (MIT), mem0 (Apache-2.0), strands (license shown), and Anthropic's article (public engineering content) is compatible, but any copied code must retain attribution — the THIRD_PARTY_NOTICES.md pattern from anthropics/skills is the right safeguard. (2) Trace recording raises data-protection concerns if the Manager's projects contain personal data (GDPR/CCPA): transcripts of tool calls may include personal data; the sanitization layer (security_engineer's recommendation) doubles as a compliance control. (3) Memory auto-capture must respect data minimization — storing only what's needed, with deletion capability (the memory server already has delete_memory; auto-capture must not bypass it). (4) If HQ publishes skills to marketplaces (Claude marketplace, npm), the marketplace terms and the plugin manifests' license fields must be accurate — superpowers' plugin.json includes license fields; ours must too. (5) The eval harness using LLM judges on task data is low-risk (no user data), but if evals ever run on real project data, a data-handling policy is needed.
      </analysis>
      <recommendations>
        <item>Add a THIRD_PARTY_NOTICES.md (anthropics/skills pattern) documenting all adopted patterns and their source licenses before any code is copied from the researched projects.</item>
        <item>Ensure trace sanitization covers personal data (not just secrets) — redact paths and content that could contain personal data when traces are committed.</item>
        <item>Keep memory deletion first-class: auto-capture (when adopted) must respect delete_memory and namespace isolation; document a retention policy for memories.</item>
        <item>Include accurate license fields in all future plugin manifests (plugin.json license, author, repository fields per superpowers' manifest shape).</item>
      </recommendations>
    </response>

    <response persona="critical_thinker">
      <analysis>
        Devil's advocacy on the core assumptions: (1) "The eval harness is the top priority" — challenge: HQ is a documentation-only repo with no product code; evals of *prompts and skills* are harder than evals of code (no unit tests to run). Anthropic's own guidance says grade output not path, and for prompt/skill evals the "output" is agent behavior — which requires running real agent sessions (superpowers' drill harness pattern). This is doable but the effort estimate must be honest: it's the most expensive item, not a quick win. (2) "Semantic memory is needed" — challenge: the Manager's memory files are small (4 files in .opencode/memory); keyword search may be sufficient at this scale. The benchmark-first approach (measure current recall on 20 questions BEFORE upgrading) prevents building infrastructure for a non-problem. (3) "Multi-platform manifests add value" — challenge: HQ's actual users are the Manager's own projects; distribution to 14 platforms is speculative until there's evidence of external adoption. The repo has 100 archived tasks but no evidence of external users. Manifests are cheap, so low risk — but don't oversell. (4) "Hooks/bootstrap is low effort" — partially true: OpenCode/Freebuff load instruction files at session start, but the bootstrap only works if the executor agent definitions (agents/*.md) are updated and the system-prompt fragment registry stays in sync — a maintenance burden that must be owned. (5) The biggest unstated assumption: that the Brain will actually USE the new artifacts. The Brain is a separate LLM session; eval reports and traces only help if the Orchestrator prompt instructs the QA persona to consume them. Without system-prompt changes, all infrastructure is decorative.
      </analysis>
      <recommendations>
        <item>Benchmark before building: measure current memory recall (20 fixed questions) and current QA pass rate BEFORE adopting evals/semantic memory — if baselines are already good, defer the expensive items.</item>
        <item>Scope the eval harness honestly: start with deterministic graders on task files (structure, diff quality, guardrail compliance — all checkable without running agents), add LLM-judge behavior evals only in Phase 2 with real agent sessions.</item>
        <item>Require system-prompt integration for every adopted practice: each item must include a fragment update (prompts/fragments/) so the Brain actually consumes the new artifacts — otherwise it's decoration.</item>
        <item>Reject the "adopt everything" impulse: 15 gaps is a wishlist; the MVP is 3 items (hooks/bootstrap, SOP format, version manifest) that can ship in one release and be measured.</item>
      </recommendations>
    </response>
  </persona_responses>

  <tradeoffs>
    <tradeoff factor="Eval harness value vs. effort">
      The swarm's strongest disagreement: system_architect and business_strategist rank evals as the top investment (moat-extender, measurable quality), while critical_thinker warns it's the most expensive item with the hardest grading problem (prompts/skills have no unit tests). Resolution: phase the eval harness — Phase 1 ships deterministic graders on task files (cheap, immediate value), Phase 2 adds LLM-judge behavior evals with real agent sessions (expensive, deferred until baselines prove need).
    </tradeoff>
    <tradeoff factor="Semantic memory vs. current scale">
      business_strategist sees memory as the compounding asset; critical_thinker notes the current memory corpus is tiny (4 files) and keyword search may suffice. Resolution: benchmark-first — measure current recall on 20 fixed questions; upgrade to semantic retrieval only if the benchmark shows a real gap.
    </tradeoff>
    <tradeoff factor="Trace recording vs. privacy/complexity">
      system_architect wants traces as the universal record; security_engineer and legal_advisor require sanitization (secrets + personal data) and local-only storage. Resolution: traces are adopted but with a mandatory sanitization layer and git-ignored raw storage — the compliance cost is accepted as a design constraint, not a blocker.
    </tradeoff>
    <tradeoff factor="Multi-platform distribution vs. evidence of demand">
      business_strategist sees 27×14 reach; critical_thinker notes no evidence of external adoption. Resolution: manifests are cheap (generator script), so adopt them opportunistically in Phase 2 — but do not invest in marketplace publishing/marketing until external adoption is observed.
    </tradeoff>
    <tradeoff factor="Speed of adoption vs. system-prompt stability">
      product_manager wants 3 phases across releases; critical_thinker demands every practice include a system-prompt fragment update. Resolution: each phase is a release with its own fragment updates and changelog entry — the existing versioning discipline (v8.x.y) is the adoption cadence.
    </tradeoff>
  </tradeoffs>

  <conflict_resolution>
    <conflict persona_1="business_strategist" persona_2="critical_thinker">
      <issue>business_strategist ranks the eval harness as the #1 strategic investment (moat-extender); critical_thinker argues it's the most expensive item with the hardest grading problem and should be deferred until baselines prove need.</issue>
      <resolution>Resolved by phasing: Phase 1 ships deterministic graders (structure, diff quality, guardrail compliance) on the existing task-file pipeline — cheap, immediate, and it establishes the baseline critical_thinker demands. Phase 2 adds LLM-judge behavior evals only if the Phase 1 baseline shows measurable quality gaps. Both personas' core concerns are satisfied: strategy gets the moat-extender, skepticism gets evidence before investment.</resolution>
    </conflict>
    <conflict persona_1="system_architect" persona_2="security_engineer">
      <issue>system_architect wants trace recording as the universal execution record (every tool call, reasoning, metric in the task file); security_engineer warns transcripts create a sensitive-data surface (secrets, paths, possibly personal data) that must not be committed or shared.</issue>
      <resolution>Resolved by a sanitization contract: raw traces live in a git-ignored traces/ directory; only sanitized summaries (redacted env vars, tokens, private paths, personal data) are written into task files. The architect's universal record is preserved; the security constraint becomes a mandatory pipeline stage rather than a blocker.</resolution>
    </conflict>
    <conflict persona_1="product_manager" persona_2="critical_thinker">
      <issue>product_manager wants all 15 gaps addressed across 3 phases with success metrics; critical_thinker warns the Brain won't consume new artifacts unless the system prompt is updated, making infrastructure decorative.</issue>
      <resolution>Resolved by the integration rule: every adopted practice MUST include a prompts/fragments/ update so the Orchestrator prompt instructs the QA persona and executor to consume the new artifacts. This makes system-prompt integration a definition-of-done for every phase item — product gets its roadmap, critical_thinker gets its consumption guarantee.</resolution>
    </conflict>
  </conflict_resolution>

  <final_recommendation>
    Adopt in three release phases, each with system-prompt fragment updates and changelog entries:
    Phase 1 (foundation, one release): (1) session-start hooks/bootstrap activating the Skill Auto-Loading Matrix, (2) standardized SOP format (Overview/Parameters/RFC 2119 constraints) + validator in mcp-lint-server, (3) .version-bump.json manifest + release-notes discipline, (4) docs/security_rules.md + secret-denylist lint checks, (5) memory benchmark suite (20 fixed questions) to establish the baseline before any memory upgrade.
    Phase 2 (differentiation, next release): (6) mcp-eval-server with deterministic graders on task files (structure, diff quality, guardrail compliance) + pass^k across 3 trials, graduating into a regression suite; (7) trace recording with sanitization layer (raw traces git-ignored, sanitized summaries in task files); (8) semantic memory upgrade (entity extraction + hybrid retrieval) ONLY if the Phase 1 benchmark shows a recall gap; (9) multi-platform plugin manifests via a generator script.
    Phase 3 (scale, conditional): (10) LLM-judge behavior evals with real agent sessions (superpowers drill-harness pattern), (11) durable execution/checkpointing only where Phase 2 traces prove mid-execution failures, (12) observability metrics (n_turns, n_toolcalls, tokens) as tracked_metrics in task files, (13) SOP multi-modal distribution (MCP prompts + skills), (14) capability vs. regression eval split with saturation monitoring, (15) eval-driven development (success criteria in every task template).
    Governing principles: benchmark before building; every practice must be consumed by the Brain (fragment updates); sanitize all traces; attribute all adopted patterns (THIRD_PARTY_NOTICES.md); keep the task file as the universal record.
  </final_recommendation>
</brainstorming_session>
```

---

## How to Use This Report

1. **For the Brain (Orchestrator):** Paste the `<brainstorming_session>` block into the Orchestrator session as non-functional guidelines for any backlog task generated from this research.
2. **For task generation:** The final recommendation maps directly to backlog tasks — one per phase item (e.g., "Implement session-start bootstrap", "Add SOP validator to mcp-lint-server").
3. **Interpretation rule:** Per AGENTS.md, `<brainstorming_session>` results are non-functional guidelines that inform but do not override primary task instructions.