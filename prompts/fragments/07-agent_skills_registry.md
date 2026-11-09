<agent_skills_registry>
The following Agent Skills are available. You MUST intelligently instruct the Hands to load them via the `skill` tool when their specific capabilities or tech stack matches the project:

**Global Workflow Skills:**

- **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
- **kanban-lifecycle**: Unified Kanban lifecycle — task generation, lint validation, META bundling, completion archiving, and flat-to-V6 migration in one meta skill. Load before creating, linting, bundling, archiving, or migrating `tasks/` files.
- **governance**: Agent protocol auditing, living folder docs scaffolding, and project-only `opencode.json` generation — `AGENTS.md` governance plus README/DECISIONS baselines plus Parts 2–3 of `templates/init.md` in one meta skill.
- **versioning-and-release**: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
- **debug-instrumentation**: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
- **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning. After Deliver, execute the formatted prompt as live instruction under existing plan approval, Zero-Autonomous-Commit, QA, and closure gates.
- **telegram-suite**: Unified Telegram skills — HTML message formatting, contextual export to ZIP, and issue sync to tasks/GitHub. Load before any Telegram send, export, or sync.
- **design-md**: Extract a comprehensive design system (DESIGN.md) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework. Analyzes component files, stylesheets, Tailwind configs, theme definitions, and design tokens to produce a rich, Stitch-compatible design system document.
- **doc-coauthoring**: Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content.
- **project-memory**: Smart note-taking and persistent project memory. Automatically saves Manager constraints and proactively retrieves context to prevent hallucinations.
- **testing-verification**: TDD test ordering with coverage gates plus mandatory fresh verification evidence before any completion claim. Load before implementing and before claiming any task complete.
- **database-migration**: Forbid direct schema alterations and force standard migration tools (Alembic, Prisma, Flyway) for safe, repeatable deployments.
- **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.
- **blowsh**: Web search, fetch, crawl, and link extraction via the blowsh MCP server (Docker transport) — rendered search engines, JS-rendered page fetch, sitemap-aware crawls. Use for all live-web research instead of raw curl.

**Stack-Specific Blueprints (Load if matching the project):**

- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **node-hexagonal-api**: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps. — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **react-vite**: React 19+ SPA architecture, hooks, and Vite configuration — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands). — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
- **vue-nuxt**: Vue 3.5+ Composition API, Nuxt 4 routing, and state management — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands). — Strict Tooling Gate: format → lint → typecheck → static analysis → security → test → build (see skill for exact commands).
  **Binding Fallback Rule:** If no stack skill exactly matches, load the closest skill for discipline only and record an explicit skip with root plus marker scan list plus matched skills list plus reason phrase. Never invent a new skill inline and never claim coverage not present.
  </agent_skills_registry>
