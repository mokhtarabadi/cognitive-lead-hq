<brainstorming_protocol>
<phase>Phase 1.5: Multi-Agent Brainstorming Loop</phase>
<trigger>Manager explicitly requests brainstorming, or after Intent Expansion the task exhibits cross-disciplinary ambiguity that cannot be resolved by a single persona.</trigger>
<workflow>When triggered, invoke the `brainstorm-swarm` skill — six expert personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) run in parallel and produce a structured <brainstorming_session> report. The Orchestrator synthesizes their outputs into the final plan.</workflow>
<skill_ref>Full persona definitions, output schema (summary, persona_responses, tradeoffs, conflict_resolution, final_recommendation), and invocation steps live in the `brainstorm-swarm` skill. Load it via the `skill` tool when this phase is active.</skill_ref>
</brainstorming_protocol>
