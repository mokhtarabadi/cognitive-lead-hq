---
name: audit-agents
description: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
---

# OpenCode Skill: Agent Protocol Auditor

## Target Audit Criteria

The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:

- **Mandatory First-Read Rule**: MUST explicitly command the agent to read `AGENTS.md` first before any execution. Inside it, it must route the agent to read `DESIGN.md`, `docs/architecture.md`, `docs/data_model.md`, and `docs/conventions.md` first.
- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `.opencode/skills/`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`).
- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`) as their single source of truth.
- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
- **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator.
- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 4-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool (NO COMMITS ALLOWED). 4) Notify the Manager.
- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.

---

## Core Document Templates

### 1. `architecture.md` Template

```markdown
# Architecture Overview

This document serves as a critical, living template designed to equip agents with a rapid and comprehensive understanding of the codebase's architecture, enabling efficient navigation and effective contribution from day one. Update this document as the codebase evolves.

## 1. Project Structure

[Project Root]/
├── backend/ # Contains all server-side code and APIs
│ ├── src/ # Main source code for backend services
│ │ ├── api/ # API endpoints and controllers
│ │ ├── client/ # Business logic and service implementations
│ │ ├── models/ # Database models/schemas
│ │ └── utils/ # Backend utility functions
│ ├── config/ # Backend configuration files
│ ├── tests/ # Backend unit and integration tests
│ └── Dockerfile # Dockerfile for backend deployment
├── frontend/ # Contains all client-side code for user interfaces
│ ├── src/ # Main source code for frontend applications
│ │ ├── components/ # Reusable UI components
│ │ ├── pages/ # Application pages/views
│ │ ├── assets/ # Images, fonts, and other static assets
│ │ ├── services/ # Frontend services for API interaction
│ │ └── store/ # State management (e.g., Redux, Vuex, Context API)
│ ├── public/ # Publicly accessible assets (e.g., index.html)
│ ├── tests/ # Frontend unit and E2E tests
│ └── package.json # Frontend dependencies and scripts
├── common/ # Shared code, types, and utilities used by both frontend and backend
│ ├── types/ # Shared TypeScript/interface definitions
│ └── utils/ # General utility functions
├── docs/ # Project documentation (e.g., API docs, setup guides)
├── scripts/ # Automation scripts (e.g., deployment, data seeding)
├── .github/ # GitHub Actions or other CI/CD configurations
├── .gitignore # Specifies intentionally untracked files to ignore
├── README.md # Project overview and quick start guide
└── ARCHITECTURE.md # This document

## 2. High-Level System Diagram

[User] <--> [Frontend Application] <--> [Backend Service 1] <--> [Database 1]
|
+--> [Backend Service 2] <--> [External API]

## 3. Core Components

### 3.1. Frontend

Name: [Web App, Mobile App]
Description: [Purpose, core interfaces, and roles]
Technologies: [e.g., React, Next.js, Jetpack Compose, Swift/Kotlin]
Deployment: [e.g., Vercel, Netlify, Play Store, App Store]

### 3.2. Backend Services

#### 3.2.1. Service Name 1

Name: [e.g., API Service]
Description: [Core business roles]
Technologies: [e.g., Spring Boot, Node.js Express, Go]
Deployment: [e.g., AWS ECS, Kubernetes]

## 4. Data Stores

### 4.1. Data Store 1

Name: [e.g., SQL Database]
Type: [e.g., PostgreSQL, MongoDB]
Purpose: [e.g., Account records]

## 5. External Integrations / APIs

- Service Name: [e.g., Stripe, SendGrid]
- Purpose: [e.g., Payments]
- Method: [e.g., REST, SDK]

## 6. Deployment & Infrastructure

- Provider: [e.g., AWS, GCP]
- CI/CD: [e.g., GitHub Actions]

## 7. Security Considerations

- Authentication: OAuth2/JWT
- Encryption: TLS + AES-256

## 8. Development & Testing Environment

Testing Frameworks: [e.g., Pytest, JUnit, Jest]

## 9. Future Considerations / Roadmap

[Planned changes or architectural debt]
```

### 2. DESIGN.md Template (Google Spec)

```markdown
# Design System Specification

---

name: custom-ui-system
colors:
primary: "#1D4ED8"
secondary: "#4B5563"
background: "#F3F4F6"
surface: "#FFFFFF"
text: "#111827"

---

## 1. Visual Theme & Atmosphere

[Rich prose outlining overall design mood, light/dark values, and whitespace philosophy]

## 2. Color Palette & Roles

- Primary foundation
- Interactive / CTAs
- Text hierarchy
- State colors (Success, error, warn)

## 3. Typography Rules

- Hierarchy (headline, body, label)
- letterSpacing, lineHeight, fontWeights

## 4. Component Stylings

- Buttons
- Cards
- Navigation
- Input fields

## 5. Layout Principles

- Spacing scales
- Breakpoints
```

---

Use this skill in two modes:

- **Phase 0 (Generation):** When `AGENTS.md` does not exist yet — generate it from the template below.
- **Audit Mode (Existing):** When `AGENTS.md` already exists — audit and patch it against the Target Audit Criteria.

---

## Mode 1: Phase 0 — Generate AGENTS.md

Use this when a project has no `AGENTS.md` yet (new project onboarding).

### Workflow

1. Read the project's existing context (package configs, README, tech stack files) to determine the project name, description, and relevant tech stack skills.
2. Generate `AGENTS.md` at the project root using the template below.
3. Fill in the `[bracketed]` placeholders with the actual project details.
4. Confirm the file was created.

### AGENTS.md Template

```markdown
# [Project Name] — Project Context Hub

## Project Overview

[Brief description of the project, its purpose, and tech stack]

## Setup & Dev Commands

- Build: [build command, e.g., npm run build]
- Test: [test command, e.g., npm test]
- Lint: [lint command, e.g., npm run lint]
- Dev: [dev server command, e.g., npm run dev]

## Actionable Guardrails (Do's & Don'ts)

- **Don't** [common anti-pattern to avoid]
  -> **Do** [preferred alternative]
- **Don't** [another anti-pattern]
  -> **Do** [preferred alternative]
- **Don't** execute Git commands like `git add`, `git commit`, or `git mv` autonomously or try to guess when to stage code.
  -> **Do** execute Git commands ONLY when explicitly instructed by an AI Studio task block. Otherwise, rely on the `custom_context_stage_and_inject_diff` MCP tool.
- **Don't** guess blindly when facing complex bugs, deadlocks, or silent timeouts.
  -> **Do** utilize the `debug-instrumentation` skill to inject strategic logs and trace the runtime execution path.

## Documentation Sync Rules

When modifying this repository, you must keep these files synchronized:

1. Active task file in `tasks/` (single source of truth for current work items)
2. `CHANGELOG.md` (Keep a Changelog format)
3. `DESIGN.md` (UI/UX design system, if modified)
4. Relevant `SKILL.md` files (if structural patterns were altered)

## 🛑 GATEKEEPER VALIDATION (HALT PROTOCOL)

You (OpenCode) are the final gatekeeper. Before executing any implementation task, you MUST evaluate the Orchestrator's instructions against this file and any referenced specs (`DESIGN.md`, `architecture.md`, etc.). If the instructions violate project rules, ignore them. HALT immediately and output a `⚠️ RULE VIOLATION WARNING` back to the Manager explaining exactly what the Orchestrator got wrong, forcing it to self-correct.

## 🛑 CORE FILE LOCATIONS

You MUST strictly adhere to these exact paths. Do not create duplicates elsewhere:

- **Global Rules:** `AGENTS.md` (Root)
- **UI/UX Specs:** `DESIGN.md` (Root)
- **Agent Skills:** `.opencode/skills/<skill-name>/SKILL.md` (Local workspace)
- **Active Tasks:** `tasks/backlog/<task-number>-<name>.md` (backlog), `tasks/in-progress/`, `tasks/qa/`, `tasks/completed/`, `tasks/archive/`

## 🛑 SKILL LOADING RULES

You MUST follow these skill loading rules in every session:

- **Task-Generator Skill:** Before creating any new task file, you MUST load the `task-generator` skill using the `skill` tool to ensure the correct template format with `<!-- BEGIN_GIT_DIFF -->` / `<!-- END_GIT_DIFF -->` markers.
- **Project Skills:** Before implementing any task, you MUST load every available skill matching the project's tech stack (e.g., `android-kotlin`, `spring-boot`, `react-vite`). If a relevant skill exists, it MUST be loaded — this enforces framework-specific conventions and architectural rules.

## 🛑 MANDATORY END-OF-TASK SEQUENCE

When finishing a task, you MUST execute these exact steps in order:

1. **Update Changelog:** You MUST insert a formal entry into CHANGELOG.md logging your modifications.
2. **Write your Summary:** Manually write your architectural reasoning, local TODO checks, and execution notes into the active `tasks/XX-task.md` file under "OpenCode Execution Log".
3. **Call MCP Tool:** Call the `custom_context_stage_and_inject_diff` MCP tool passing the task file path to automatically stage the files and inject the factual code diff. DO NOT execute any `git commit` commands afterward.
4. **Notify Manager:** Output exactly: "Task ready. Manager, please copy the contents of `tasks/XX-task.md` and send it back to the AI Studio Brain for review."
```

---

## Mode 2: Audit & Patch Existing AGENTS.md

### 🛑 STRICT EXECUTION RULES (Priority 1)

1. **Primary Source of Truth**: You MUST read `AGENTS.md` at the project root using local file read tools.
2. **Read-Only First**: Evaluate the contents of `AGENTS.md` against the Target Audit Criteria before attempting any file modifications.
3. **Immutable Formatting**: If patching is required, maintain the exact Markdown list structure, headers, and spacing of the existing file.

### Target Audit Criteria

The `AGENTS.md` file MUST explicitly contain the following operational constraints, ideally within a `Task Management & OpenCode Rules` section:

- **Core File Locations**: MUST explicitly list paths for `AGENTS.md`, `DESIGN.md`, `.opencode/skills/`, and the 5 Kanban directories (`tasks/backlog`, `tasks/in-progress`, `tasks/qa`, `tasks/completed`, `tasks/archive`).
- **Decentralized Task Management**: Agents MUST strictly use decentralized, individual task files in the `tasks/` directory as their single source of truth.
- **No Monolithic State**: Agents are strictly forbidden from creating `TODO.md` or `STATE.md`.
- **Zero-Autonomous-Commit**: Agents MUST be strictly forbidden from executing Git commands autonomously; they may only run Git commands when explicitly instructed by the Orchestrator.
- **Mandatory End-Of-Task Sequence**: MUST explicitly mandate a 4-step completion process: 1) Update CHANGELOG.md. 2) Write manual reasoning in the task file. 3) Call the `custom_context_stage_and_inject_diff` MCP tool (NO COMMITS ALLOWED). 4) Notify the Manager.
- **UI/UX Enforcement**: Any UI/UX changes MUST enforce the guidelines defined in the project's `DESIGN.md`.
- **Task-Generator Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load the `task-generator` skill before creating new task files.
- **Project Skill Loading**: `AGENTS.md` MUST explicitly instruct OpenCode to load every available skill matching the project's tech stack before task implementation.
- **Complex Debugging**: Agents MUST be instructed not to guess blindly on complex bugs, but instead utilize the `debug-instrumentation` skill.
- **Gatekeeper Validation (Halt Protocol)**: Agents MUST be instructed to evaluate tasks against project rules and HALT with a warning if the Orchestrator provides non-compliant instructions.

### Resolution Protocol

1. **Evaluation**: Compare the active `AGENTS.md` text against the Target Audit Criteria.
2. **Patching**: If any constraints are missing, ambiguous, or incorrect, use the `apply_patch` tool to inject the exact missing rules.
3. **Halt on Success**: If the file already complies 100%, DO NOT execute any write operations.

### Summary Phase

Upon completion, output a strict, formatted summary for the Manager:

### Agent Audit Summary

**Audit Status:** [PASSED | FIXED]
**Violations Found:** [List of missing/incorrect rules, or "None"]
**Actions Taken:** [Description of the patch applied, or "File already compliant"]
