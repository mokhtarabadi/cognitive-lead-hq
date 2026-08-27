<agent_skills_registry>
The following Agent Skills are available. You MUST intelligently instruct the Hands to load them via the `skill` tool when their specific capabilities or tech stack matches the project:

**Global Workflow Skills:**

- **code-search**: Mandatory workflow for exploring the codebase and gathering context for the Orchestrator.
- **task-generator**: Automatically generates decentralized task files based on manager instructions.
- **task-lint**: Validates task files and Markdown documents using the lint MCP server. Run after task creation and before task closure.
- **bundle-tasks**: Deterministic meta-task bundling — bundles 2–6 small related tasks into one META for unified execution with verbatim preservation and auto-archive. Exposed as both `scripts/bundle-tasks.py` CLI and `bundle_tasks` MCP tool (Task 110).
- **archive-tasks**: Milestone compaction skill — scans completed tasks, generates dense history summaries, and moves them to the archive.
- **migrate-kanban**: Migrates a flat tasks/ directory into the V6 Kanban folder structure (backlog, in-progress, qa, completed, archive).
- **audit-agents**: Enforces decentralized task management, UI/UX design strictness, and global state constraints within AGENTS.md.
- **brainstorm-swarm**: Orchestrates a multi-expert brainstorming session using six specialized personas (system_architect, security_engineer, product_manager, business_strategist, legal_advisor, critical_thinker) to resolve cross-disciplinary ambiguity. Outputs structured XML-tagged session reports.
- **versioning-and-release**: Standardizes Semantic Versioning (SemVer), Keep a Changelog formats, Conventional Commits, and Safe Push Protocols across all repositories.
- **debug-instrumentation**: Mandatory workflow for diagnosing complex bugs, deadlocks, race conditions, and silent failures via strategic logging and tracing.
- **prompt-refactor**: Refactors basic user prompts into elite, highly constrained, XML-tagged instructions optimized for AI agent reasoning.
- **telegram-issue-sync**: Syncs Telegram supergroup topics into local task files and GitHub issues, using embedded Python scripts for deterministic JSON state management.
- **telegram-message-export**: Intelligently exports a range of Telegram messages (text, media, voice notes) into a numbered folder, capturing reply hierarchies, and packing them into a ZIP archive.
- **design-md**: Extract a comprehensive design system (DESIGN.md) directly from frontend source code — React, Vue, Svelte, Angular, plain HTML/CSS, or any web framework. Analyzes component files, stylesheets, Tailwind configs, theme definitions, and design tokens to produce a rich, Stitch-compatible design system document.
- **doc-coauthoring**: Guide users through a structured workflow for co-authoring documentation. Use when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content.
- **project-memory**: Smart note-taking and persistent project memory. Automatically saves Manager constraints and proactively retrieves context to prevent hallucinations.
- **verification-before-completion**: Mandatory rule before claiming any task is complete, fixed, or passing.
- **perplexity-research**: Triggers a human-in-the-loop deep research cycle using the Perplexity 3-Step Framework. Use when encountering post-2025 dependencies, undocumented API errors, or complex hardware/system bugs.
- **github**: GitHub CLI (gh) workflow for pull request triage, issue management, CI/CD run analysis, and API queries.

**Stack-Specific Blueprints (Load if matching the project):**

- **android-kotlin**: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development.
- **flask-python**: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask
- **go-gin**: Idiomatic Go, Clean Architecture, and Gin routing best practices
- **go-hexagonal-grpc**: Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx, and Redis caching for ultra-low latency Go backends.
- **ios-swiftui**: SwiftUI, MVVM, and modern iOS app architecture
- **nestjs-prisma-vertical**: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development.
- **nextjs**: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js
- **python-fastapi**: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing.
- **react-native-expo**: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps.
- **react-vite**: React 18+ SPA architecture, hooks, and Vite configuration
- **spring-boot**: DDD, hexagonal style, and naming conventions for Spring Boot
- **vue-nuxt**: Vue 3 Composition API, Nuxt 3 routing, and state management
</agent_skills_registry>