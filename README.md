# Cognitive Lead AI — Multi-Agent System Prompt & Technology SOPs

This repository serves as the central **Standard Operating Procedure (SOP)** for the Cognitive Lead AI multi-agent system. It contains the definitive system prompt that governs all AI agents in our pipeline, alongside battle-tested best-practice guides for every technology stack we use.

## Purpose

- **Unified Agent Instruction** — The `system-prompt.md` file is the single source of truth for agent behavior, role definitions, and decision-making protocols.
- **Stack Consistency** — The `stacks/` directory contains per-technology guides that ensure every project — whether greenfield or brownfield — follows the same high standards for structure, naming, architecture, and testing.
- **Onboarding** — New developers and AI agents should read the system prompt first, then consult the relevant stack guide before writing any code.

## How to Use This Repository

| File / Directory | When to Consult |
|---|---|
| `system-prompt.md` | At the start of every session; this defines how the AI agent operates. |
| `stacks/backend/` | Before writing any server-side code (Node.js, Spring Boot, Flask). |
| `stacks/frontend/` | Before writing any client-side code (Next.js). |
| `stacks/mobile/` | Before writing any mobile code (Android with Kotlin or Java). |
| `CHANGELOG.md` | To review what has changed between versions. |
| `TODO.md` | To see which stacks are planned for future coverage. |

## Repository Structure

```
/
├── README.md               # This file
├── AGENTS.md               # Rules for AI agents editing this repo
├── TODO.md                 # Roadmap for new stacks
├── CHANGELOG.md            # Version history
├── system-prompt.md        # Multi-agent system prompt (v3)
└── stacks/
    ├── backend/
    │   ├── nodejs-express.md
    │   ├── spring-boot.md
    │   └── flask-python.md
    ├── frontend/
    │   └── nextjs.md
    └── mobile/
        ├── android-kotlin.md
        └── android-java-xml.md
```

## Contributing

See `AGENTS.md` for the rules that AI agents must follow when modifying this repository.
