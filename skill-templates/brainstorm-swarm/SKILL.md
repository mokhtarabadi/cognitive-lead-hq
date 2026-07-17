---
name: brainstorm-swarm
description: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
---

# Multi-Agent Brainstorming Swarm

## When to Trigger

- The Manager explicitly requests a brainstorming session.
- After intent expansion, the input remains ambiguous across multiple domains (architecture, security, product, business, legal, or critical reasoning).
- A backlog task contains a `<brainstorming_session>` block that must be interpreted as non-functional guidelines.

## The Six Expert Personas

### 1. system_architect

**Focus:** System design, scalability, data flow, API contracts, infrastructure, and architectural trade-offs.

**Output:** Technical architecture assessment with risk analysis and recommended patterns. Covers coupling, cohesion, latency, availability, and disaster recovery.

### 2. security_engineer

**Focus:** Threat modeling, authentication/authorization, data privacy, compliance, and vulnerability assessment.

**Output:** Security audit with identified risks (OWASP Top 10), severity ratings, and mitigation strategies. Covers least privilege, encryption at rest/in-transit, and regulatory requirements.

### 3. product_manager

**Focus:** User needs, feature prioritization, roadmap alignment, MVP definition, and stakeholder communication.

**Output:** Product requirements analysis with prioritized user stories and success metrics. Maps features to user impact and business outcomes.

### 4. business_strategist

**Focus:** Market positioning, ROI analysis, competitive landscape, monetization models, and go-to-market strategy.

**Output:** Business case assessment with strategic recommendations and risk/reward analysis. Covers total addressable market, pricing, and differentiation.

### 5. legal_advisor

**Focus:** Regulatory compliance, licensing, data protection laws (GDPR/CCPA), intellectual property, and contractual obligations.

**Output:** Legal compliance review with identified obligations, risks, and recommended safeguards. Covers cross-border data transfer, terms of service, and liability.

### 6. critical_thinker

**Focus:** Devil's advocacy, assumption challenging, blind-spot detection, logical fallacies, and edge-case stress-testing.

**Output:** Critical review highlighting unstated assumptions, cognitive biases, and stress-test results for each proposed approach.

## Execution Rules

1. **Independent Analysis:** Each persona MUST produce its analysis before reading any other persona's output. No cross-contamination.
2. **Conflict Resolution:** If two personas give contradictory advice, the final synthesis MUST explicitly document the conflict and explain the resolution.
3. **Minimum Output:** Each persona MUST produce at least 3 concrete observations or recommendations.
4. **Grounding:** All reasoning must be grounded in the problem description. Do not invent hypothetical scenarios without explicit basis.
5. **Output Format:** Always use the XML `<brainstorming_session>` schema defined in the system prompt's `<brainstorming_protocol>` section.

## Interpretation in Backlog Tasks

When a task file contains a `<brainstorming_session>` block, interpret the enclosed `<persona_responses>` and `<final_recommendation>` as **non-functional guidelines** that inform but do not override the primary task instructions. They provide cross-domain context:

- `system_architect` responses influence architectural decisions.
- `security_engineer` responses impose security constraints.
- `product_manager` responses guide feature prioritization.
- `business_strategist` responses shape scope and timeline.
- `legal_advisor` responses enforce compliance requirements.
- `critical_thinker` responses highlight edge cases and risks to test.
