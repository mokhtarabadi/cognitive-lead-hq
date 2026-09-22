---
name: nestjs-prisma-vertical
description: NestJS, Prisma ORM, Vertical Slice Architecture, and Strict TypeScript for zero-hallucination backend development.
---

# NestJS + Prisma (Vertical Slice) — "Max Power" AI Architecture

## AI Context & Token Optimization (Zero-Hallucination Rules)

1. **Opinionated Framework:** NestJS is mandatory. Unstructured frameworks like Express are BANNED. You must use decorators (`@Controller`, `@Injectable`) and modules.
2. **Vertical Slice Architecture:** Do NOT use traditional layered architectures (global `controllers/`, `services/`). Group all files by feature (e.g., `src/features/auth/`) to localize AI context and save memory tokens.
3. **Strict TypeScript & Compile-Time Safety:** The `any` type is strictly forbidden.
4. **Prisma ORM as Source of Truth:** Raw SQL queries are BANNED. You must modify `schema.prisma`, and rely on the compiler to catch invalid database calls.
5. **Validation:** All incoming requests MUST be validated using DTOs with `class-validator` and `class-transformer`, enforced by a global `ValidationPipe` (`whitelist: true, transform: true`).

## Project Structure

```text
src/
├── main.ts                     # Application entry point
├── app.module.ts               # Root module
├── core/                       # Core infrastructure (written once)
│   ├── prisma/                 # Prisma service and module
│   ├── guards/                 # Authentication/Authorization guards
│   ├── filters/                # Global exception filters
│   └── interceptors/             # Global interceptors
└── features/                   # ⬅️ Vertical Slices (Feature Modules)
    ├── auth/
    │   ├── auth.module.ts
    │   ├── auth.controller.ts
    │   ├── auth.service.ts
    │   └── dtos/
    │       ├── login.dto.ts
    │       └── register.dto.ts
    └── users/
        ├── users.module.ts
        ├── users.controller.ts
        └── users.service.ts
```

## Naming Conventions

| Artifact          | Convention              | Example              |
| ----------------- | ----------------------- | -------------------- |
| Files             | `kebab-case` with type  | `auth.controller.ts` |
| Classes           | `PascalCase`            | `AuthController`     |
| Methods/Variables | `camelCase`             | `registerUser`       |
| Prisma Models     | `PascalCase` (Singular) | `model User`         |

## Architectural Patterns

**Dependency Injection:**
Use NestJS constructor injection exclusively.

**Prisma Workflow:**

1. Modify `prisma/schema.prisma`.
2. Never write migrations manually. Use CLI commands to generate them.
3. Inject `PrismaService` into feature services to interact with the DB. The LSP will guide you with exact types.

**Global Error Handling:**
Do not use inline `try/catch` for standard HTTP errors. Throw NestJS exceptions (`ConflictException`, `NotFoundException`) and let the global filter handle the JSON formatting.

## Universal DateTime Governance

- **Prisma Schema:** Use `DateTime` fields with `@db.Timestamptz()` in the Prisma schema to enforce UTC storage. Never use `@db.Date` or `@db.Timestamp` without timezone.
- **API DTOs (class-validator):** Use `@IsString()` for ISO-8601 strings or `@IsInt()` for epoch ms. Banned: `Date` type in DTOs (serialization is unreliable cross-timezone).
- **Clock Injection:** Create a `ClockProvider` service (`@Injectable`) wrapping `new Date()` — inject it into feature services. Never call `new Date()` or `Date.now()` directly in business logic.
- **API Format:** All API responses MUST transmit datetimes as ISO-8601 UTC strings (`2026-07-23T14:30:00.000Z`) or epoch ms (number). Never transmit naive date strings.

## Testing Strategies

| Layer            | Test Type | Framework                 | File Naming               |
| ---------------- | --------- | ------------------------- | ------------------------- |
| Feature Service  | Unit      | Jest + Mock Prisma        | `auth.service.spec.ts`    |
| Controller       | Unit      | Jest                      | `auth.controller.spec.ts` |
| Feature Endpoint | E2E       | Jest + Supertest + TestDB | `auth.e2e-spec.ts`        |

## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

### Strict Baseline

> Target: **NestJS 12 + Prisma 7 + TypeScript, organized as Vertical Slice Architecture**
> (`src/slices/<slice>/…`, one public `index.ts` barrel per slice).
> All versions verified live against the npm registry / official docs in Sep 2026. Pinned to the
> **strictest actively-maintained** tool for each role. Deprecated or dormant tools are named and
> excluded. Two stack-specific deviations from a plain Node service are called out inline: NestJS DI
> relies on **parameter properties + `emitDecoratorMetadata`**, and Prisma 7 requires **ESM**.

### Required Toolchain

| Tool | Purpose | Minimum version | Activate |
| --- | --- | --- | --- |
| Node.js | Runtime; LTS only | 24.x Active LTS | `printf '24\n' > .nvmrc` + `"engines": { "node": ">=24.0.0" }` |
| Corepack | Pin the package manager (`packageManager` field) | bundled in Node ≤24 (install manually on Node ≥25) | `corepack enable` + `"packageManager": "npm@11.6.0"` + `"devEngines": { "packageManager": { "name": "npm", "onFail": "error" } }` |
| TypeScript | `tsc --noEmit` type gate + parser backend for typed lint | 6.0.3 (npm `latest` is 7.0.2 — **not** a typed-lint backend, see Discarded) | `npm i -D typescript@6.0.3` |
| @typescript/native-preview (optional) | TS7 `tsgo` fast `--noEmit` gate alongside TS6 | 7.0.2 | `npm i -D @typescript/native-preview@^7` (run `tsgo --noEmit` only) |
| ESLint | Core linter, flat config only (eslintrc removed in v10) | 10.0.0 (10.11.0) | `npm i -D eslint@^10 @eslint/js@^10` |
| typescript-eslint | Type-aware rules (`strictTypeChecked` + `stylisticTypeChecked`) | 8.70.1 | `npm i -D typescript-eslint@^8` |
| eslint-plugin-n | Node correctness (`no-process-exit`, `no-missing-import`) | 18.2.2 | `npm i -D eslint-plugin-n@^18` |
| eslint-plugin-import-x | Fast `no-restricted-paths` per-file guard (maintained fork of frozen `eslint-plugin-import`) | 4.16.2 | `npm i -D eslint-plugin-import-x@^4` |
| dependency-cruiser | **Primary** slice-boundary + cycle gate on the real resolved graph | 18.4.0 | `npm i -D dependency-cruiser@^18` |
| eslint-plugin-boundaries | Secondary, in-editor boundary feedback (entity model v7) | 7.2.0 | `npm i -D eslint-plugin-boundaries@^7` |
| Prettier | Formatting, run **separately** (never merged into ESLint) | 3.9.8 | `npm i -D prettier@^3 eslint-config-prettier@^10` |
| knip | Unused files, exports, and dependencies | 6.37.0 | `npm i -D knip@^6` |
| lockfile-lint | Lockfile host/integrity policy (anti-typosquat / injection) | 5.0.1 | `npm i -D lockfile-lint@^5` |
| osv-scanner | Vulnerability scan against OSV (replaces/augments `npm audit`) | 2.5.1 | `go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest` (or the official GH Action) |
| Prisma CLI + Client | Schema, migration, and generated type gate | prisma 7.10.0 / @prisma/client 7.10.0 (v8 is in RC — see note) | `npm i -D prisma@^7.10.0` + `npm i @prisma/client@^7.10.0 @prisma/adapter-pg@^7.10.0` |
| @nestjs/testing | Nest DI test module builder | 12.0.4 | `npm i -D @nestjs/testing@^12.0.4` |
| supertest | HTTP e2e assertions against the real Nest app | 7.2.2 | `npm i -D supertest@^7 @types/supertest@^7` |
| class-validator + class-transformer | DTO contract enforcement (`whitelist`, `forbidNonWhitelisted`) | 0.15.1 / 0.5.x | `npm i class-validator@^0.15.1 class-transformer@^0.5` |
| Vitest + @vitest/coverage-v8 | Unit/integration runner with fail-on-threshold coverage | 5.0.1 | `npm i -D vitest@^5 @vitest/coverage-v8@^5` |
| type-coverage | Compile-time `any` budget gate | 2.30.1 | `npm i -D type-coverage@^2` |
| oasdiff | OpenAPI breaking-change gate (Nest `@nestjs/swagger` output) | 1.11.x | `brew install oasdiff` / `curl -fsSL …/install.sh \| sh` / GH Action |
| @nestjs/swagger | Emits `openapi.json` for the oasdiff contract gate | 12.x | `npm i @nestjs/swagger@^12` |

**Prisma major-version note (2026).** The **stable** line is **Prisma 7.10.0** (`@prisma/client@7.10.0`);
Prisma **8** is rolling out — the `prisma` CLI's `latest` dist-tag already points at **`8.0.0-rc.15`**
and the docs call v8 "the current release", but the runtime (`@prisma/orm-postgres`, `@prisma/client`)
is still `7.10.0` on `latest` with v8 only under `dev`/RC tags. Pin `^7.10.0` for a strict gate today.
v7 breaking changes that the gates below depend on: **ESM-only** (`"type": "module"`), the
`prisma-client` generator with a **required `output`**, **driver adapters required**, `prisma.config.ts`
is the new config home, **env is not auto-loaded** (`import "dotenv/config"` in the config), `migrate dev`
**no longer auto-runs `generate`**, and `migrate diff` flags changed from `--from-url`/`--to-url` to
`--from-config-datasource`/`--to-config-datasource`. Prisma 8 replaces the migrate flow with
`contract infer/emit` + `migration plan` + `db sign`/`db migrate`/`db verify`; treat that as a future
migration, not this baseline.

**Discarded / demoted (say so, do not silently use):**
- **`ts-prune`** — last npm release **0.10.3 (2021)**, dormant. Superseded by **knip** (files + exports + deps in one pass).
- **`depcheck`** — 1.4.7; its own README now says *"We strongly recommend switching to knip, a more actively maintained and feature-rich alternative."* Excluded.
- **`eslint-plugin-import`** — 2.32.0, effectively frozen and refuses modern `exports`/specifier support; use **`eslint-plugin-import-x`** (declares ESLint 8/9/10 support).
- **`eslint-plugin-prettier`** — merging Prettier into ESLint is explicitly discouraged (slow, duplicate diagnostics). Run `prettier --check` as its own gate and let **`eslint-config-prettier`** (10.1.8) only switch off conflicting stylistic rules.
- **TypeScript 7.0.2 as the typed-lint backend** — 7.x is npm `latest`, but `typescript-eslint@8` supports only up to **`<6.1.0`**; pointing `typescript` at 7 makes typed lint crash. Pin `typescript@6.0.3` for lint and run TS7 (`tsgo`) side-by-side for the fast type-check only.
- **`erasableSyntaxOnly`** — valid and strict on Node backends, but **rejected for NestJS**: it bans parameter properties (`constructor(private readonly db: PrismaService)`) which NestJS DI depends on. Leave it **off** here (it is on in the plain-Node sibling gate).
- **`madge`** — cycle/graph visualiser, dormant; cycle detection is already a `dependency-cruiser` rule.

### Strict Baseline Config

`tsconfig.json` — every strict flag; `tsc --noEmit` is the gate. NestJS deviations are marked:

```jsonc
{
  "compilerOptions": {
    "target": "es2024",
    "lib": ["es2024"],
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "moduleDetection": "force",
    "types": ["node"],
    "rootDir": "./src",
    "outDir": "./dist",

    /* NestJS: decorator metadata + DI parameter properties */
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    /* "erasableSyntaxOnly" is intentionally NOT set: NestJS DI uses parameter properties */

    /* maximum static strictness */
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitThis": true,
    "useUnknownInCatchVariables": true,
    "noPropertyAccessFromIndexSignature": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    "forceConsistentCasingInFileNames": true,

    /* module purity */
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "noUncheckedSideEffectImports": true,

    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "skipLibCheck": false
  },
  "include": ["src"],
  "exclude": ["dist", "node_modules", "generated/prisma"]
}
```

> ⚠️ `verbatimModuleSyntax` + `emitDecoratorMetadata` conflict: never write `import type { Foo }` for a
> class that is **injected** (`constructor(private foo: Foo)`), or Nest emits `Object` metadata and DI
> silently fails at boot. Because of this, the `consistent-type-imports` autofix is **disabled** below;
> the e2e boot test is the real guard.

`eslint.config.mjs` — ESLint 10 flat config, strictest type-checked presets:

```js
// @ts-check
import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';
import node from 'eslint-plugin-n';
import importX from 'eslint-plugin-import-x';
import prettier from 'eslint-config-prettier';

export default defineConfig(
  { ignores: ['dist/**', 'coverage/**', 'node_modules/**', 'generated/prisma/**', '**/*.d.ts'] },

  js.configs.recommended,

  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  {
    files: ['**/*.{ts,mts,cts}'],
    languageOptions: {
      parserOptions: {
        projectService: true,                    // typed linting; no tsconfig.eslint.json
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      '@typescript-eslint/no-floating-promises': ['error', { ignoreVoid: false }],
      '@typescript-eslint/no-misused-promises': ['error', {
        checksConditionals: true,
        checksSpreads: true,
        checksVoidReturn: { arguments: true, attributes: false, returns: true },
      }],
      '@typescript-eslint/switch-exhaustiveness-check': ['error', {
        considerDefaultExhaustiveForUnions: true,
        requireDefaultForNonUnion: true,
      }],
      '@typescript-eslint/consistent-type-imports': 'off',   // Nest DI: do NOT type-only injected classes
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/explicit-function-return-type': ['error', { allowExpressions: true }],
      'no-console': 'error',

      /* Prisma raw-query discipline: unsafe variants are banned */
      'no-restricted-properties': ['error',
        { object: 'prisma', property: '$queryRawUnsafe',   message: 'Use Prisma.sql tagged $queryRaw.' },
        { object: 'prisma', property: '$executeRawUnsafe', message: 'Use Prisma.sql tagged $executeRaw.' },
        { object: 'this',   property: '$queryRawUnsafe',   message: 'Use Prisma.sql tagged $queryRaw.' },
        { object: 'this',   property: '$executeRawUnsafe', message: 'Use Prisma.sql tagged $executeRaw.' },
      ],
    },
  },

  node.configs["flat/recommended-module"],
  importX.flatConfigs.recommended,

  prettier,   // LAST: turns off formatting rules that would fight Prettier
);
```

`.dependency-cruiser.cjs` — **the slice-boundary gate** (copy-paste; layout `src/slices/<slice>/…`):

```js
/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: 'no-circular',
      severity: 'error',
      comment: 'No dependency cycles anywhere.',
      from: {},
      to: { circular: true },
    },
    {
      name: 'no-cross-slice-imports',
      severity: 'error',
      comment: 'A slice may not import another slice except through its public index.ts barrel.',
      from: { path: '^src/slices/([^/]+)/' },
      to: {
        path: '^src/slices/(?!$1)([^/]+)/',            // $1 validated on dependency-cruiser 18.4 — proven backreference, do not expand manually unless version <18.4
        pathNot: ['^src/slices/[^/]+/index\\.ts$'],    // only the public barrel is allowed
      },
    },
    {
      name: 'no-slice-internals-from-shared',
      severity: 'error',
      comment: 'Shared/platform code must never depend on a slice.',
      from: { path: '^src/(shared|platform)/' },
      to: { path: '^src/slices/' },
    },
    {
      name: 'no-slice-to-app-root',
      severity: 'error',
      comment: 'Slices must not import the composition root (main.ts / app.module.ts).',
      from: { path: '^src/slices/' },
      to: { path: '^src/(main|app\\.module)\\.ts$' },
    },
    {
      name: 'no-orphans',
      severity: 'error',
      comment: 'Unreferenced modules are dead code.',
      from: { orphan: true, pathNot: ['\\.d\\.ts$', '\\.(spec|e2e-spec)\\.ts$', '^src/main\\.ts$'] },
      to: {},
    },
  ],
  options: {
    tsConfig: { fileName: 'tsconfig.json' },
    tsPreCompilationDeps: true,
    doNotFollow: { path: 'node_modules' },
    enhancedResolveOptions: { exportsFields: ['exports'], conditionNames: ['import', 'require', 'node', 'default'] },
    exclude: { path: ['\\.(spec|e2e-spec)\\.ts$', '\\.config\\.(ts|js|mjs|cjs)$', '^dist/', '^generated/prisma/'] },
    includeOnly: { path: '^src/' },
  },
};
```

ESLint-native alternative (in-editor, same intent) via **eslint-plugin-boundaries v7**:

```js
{
  files: ['src/slices/**/*.ts'],
  plugins: { boundaries },
  settings: {
    'boundaries/elements': [
      { type: 'slice', pattern: 'src/slices/*', capture: ['slice'] },
      { type: 'shared', pattern: 'src/shared/*' },
    ],
  },
  rules: {
    'boundaries/dependencies': [2, {
      default: 'disallow',
      policies: [
        { from: { element: { type: 'slice' } }, allow: { to: { element: { type: 'slice', filters: { slice: '{{ from.slice }}' } } } } },
        { from: { element: { type: 'slice' } }, allow: { to: { element: { type: 'shared' } } } },
      ],
    }],
  },
}
```

`knip.json` — dead code / dependency hygiene:

```jsonc
{
  "$schema": "https://unpkg.com/knip@6/schema.json",
  "entry": ["src/main.ts", "src/**/*.module.ts", "test/**/*.e2e-spec.ts"],
  "project": ["src/**/*.ts", "!generated/prisma/**"],
  "ignoreExportsUsedInFile": true,
  "ignoreDependencies": ["@prisma/client", "@nestjs/testing"]
}
```

`vitest.config.ts` — coverage thresholds are the gate (Vitest 5: `coverage.include` required):

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.spec.ts', 'test/**/*.e2e-spec.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary', 'lcov'],
      include: ['src/slices/**/*.ts'],
      exclude: ['src/**/*.module.ts', 'src/**/index.ts', 'generated/prisma/**'],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 85,
        statements: 90,
        perFile: true,                          // every slice file, not just the aggregate
      },
    },
  },
});
```

`prisma.config.ts` (root, Prisma 7 shape) — env is NOT auto-loaded:

```ts
import 'dotenv/config';
import { defineConfig, env } from 'prisma/config';

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: { path: 'prisma/migrations', seed: 'tsx prisma/seed.ts' },
  datasource: { url: env('DATABASE_URL') },
});
```

DTO strictness — the global pipe (mass-assignment / unknown-field guard):

```ts
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,
  forbidNonWhitelisted: true,
  forbidUnknownValues: true,
  transform: true,
  transformOptions: { enableImplicitConversion: false },
  validationError: { target: false, value: false },
}));
```

`package.json` — single gate chain + pins:

```jsonc
{
  "type": "module",
  "engines": { "node": ">=24.0.0" },
  "packageManager": "npm@11.6.0",
  "devEngines": { "packageManager": { "name": "npm", "onFail": "error" } },
  "scripts": {
    "verify": "npm run typecheck && npm run lint && npm run arch && npm run deadcode && npm run prisma:check && npm run test && npm run types && npm run api:diff",
    "typecheck": "tsc --noEmit",
    "lint": "eslint . --max-warnings=0",
    "format:check": "prettier --check .",
    "arch": "depcruise src --config .dependency-cruiser.cjs",
    "deadcode": "knip --production --no-progress",
    "prisma:check": "prisma validate && prisma format --check && prisma migrate diff --exit-code --from-migrations prisma/migrations --to-schema prisma/schema.prisma && prisma generate && git diff --exit-code -- generated/prisma",
    "test": "vitest run --coverage",
    "types": "type-coverage --at-least 99 --strict --ignore-catch"
  }
}
```

### Mandatory Gate Order

1. `corepack enable && npm ci --ignore-scripts`  *(supply-chain: no install-time scripts)*
2. `npx lockfile-lint --path package-lock.json --type npm --validate-https --allowed-hosts npm --validate-integrity`
3. `npx osv-scanner scan -L package-lock.json --format=table`  *(or `npm audit --audit-level=high`)*
4. `npx tsc --noEmit`
5. `npx eslint . --max-warnings=0`
6. `npx depcruise src --config .dependency-cruiser.cjs`
7. `npx knip --production --no-progress`
8. `npx prisma validate`
9. `npx prisma format --check`
10. `npx prisma migrate diff --exit-code --from-migrations prisma/migrations --to-schema prisma/schema.prisma`  *(exit `2` = schema and migrations drifted)*
11. `npx prisma generate && git diff --exit-code -- generated/prisma`  *(proves the committed client matches the schema; commit `generated/prisma` for this check)*
12. `npx prisma migrate status`  *(needs a live DB service; exits `1` on pending/diverged/failed migrations)*
13. `npx vitest run --coverage`
14. `npx type-coverage --at-least 99 --strict --ignore-catch`
15. `npx oasdiff breaking openapi.baseline.json openapi.generated.json --fail-on ERR`

> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.
> (`eslint` is invoked WITHOUT `--fix`; `--max-warnings=0` makes any warning fatal.)

### Hallucination Traps to Block

- Invented Prisma model/field/relation names in queries → `prisma validate` + `prisma generate` (typed client) + `npx tsc --noEmit`; the generated client has no such member.
- A slice reaching into another slice's internals ("just import the repository") → `dependency-cruiser` `no-cross-slice-imports` (group-capture `$1`, only `index.ts` barrels allowed).
- Untyped raw SQL or SQL string concatenation → `no-restricted-properties` bans `$queryRawUnsafe`/`$executeRawUnsafe`; `strictTypeChecked`'s `no-unsafe-*` flags `any` rows; require `Prisma.sql` tagged templates.
- An unawaited `await` on a write (`prisma.user.create(...)` without `await`) silently succeeding → `@typescript-eslint/no-floating-promises` + `no-misused-promises`.
- A new status-enum member added but a `switch` handler not updated → `@typescript-eslint/switch-exhaustiveness-check` (`requireDefaultForNonUnion`, `considerDefaultExhaustiveForUnions`).
- Editing the generated Prisma client instead of `schema.prisma` → gate 11 `prisma generate && git diff --exit-code -- generated/prisma` fails on the hand-edit.
- Migration files and `schema.prisma` drifting apart (missing migration) → gate 10 `prisma migrate diff --exit-code` returns `2`.
- DTO accepts unknown/extra JSON fields (mass assignment) → global `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })`; e2e supertest asserts `400` for an unknown field.
- AI marks an **injected** provider as `import type` and breaks `emitDecoratorMetadata` → `consistent-type-imports` kept off; e2e `Test.createTestingModule(...).compile()` boot test fails loudly.
- Dead slice/export/dependency left after a refactor → `knip --production`.
- Shipping a breaking API change → `oasdiff breaking … --fail-on ERR`.

### Evidence to Record

Paste the exact command and its pass signal into Verification Evidence; all must exit `0`.

- `npx tsc --noEmit` → exit `0`, no output.
- `npx eslint . --max-warnings=0` → exit `0`, `0 problems`.
- `npx depcruise src --config .dependency-cruiser.cjs` → exit `0`, `no dependency violations found`.
- `npx knip --production --no-progress` → exit `0`, no unused files/exports/dependencies listed.
- `npx prisma validate` → exit `0`, `The schema at … is valid`.
- `npx prisma format --check` → exit `0` (no diff; unformatted schema fails).
- `npx prisma migrate diff --exit-code --from-migrations prisma/migrations --to-schema prisma/schema.prisma` → exit `0` (empty diff; `2` = drift).
- `npx prisma generate && git diff --exit-code -- generated/prisma` → exit `0` (generated client is fresh and committed).
- `npx prisma migrate status` → exit `0`, `Database schema is up to date!`.
- `npx vitest run --coverage` → exit `0`, every coverage threshold line `>= 90` and all `Test Files` passed.
- `npx type-coverage --at-least 99 --strict --ignore-catch` → exit `0`, reported `type coverage >= 99%`.
- `npx oasdiff breaking openapi.baseline.json openapi.generated.json --fail-on ERR` → exit `0`, no breaking changes.
- `npx lockfile-lint …` and `npx osv-scanner scan -L package-lock.json` → exit `0`, no host violations and **no HIGH/CRITICAL** advisories.
- E2E boot proof: `npx vitest run test/app.e2e-spec.ts` exits `0` (Nest DI module compiles; all injections resolve).

<!-- sources -->
- https://typescript-eslint.io/getting-started/typed-linting/
- https://typescript-eslint.io/users/configs/
- https://typescript-eslint.io/rules/switch-exhaustiveness-check/
- https://typescript-eslint.io/rules/no-floating-promises/
- https://typescript-eslint.io/rules/no-misused-promises/
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html
- https://www.typescriptlang.org/tsconfig/noUncheckedSideEffectImports.html
- https://www.typescriptlang.org/tsconfig/
- https://docs.bswen.com/blog/2026-02-21-typescript-60-tsconfig-defaults/
- https://eslint.org/blog/2026/02/eslint-v10.0.0-released/
- https://docs.synapsestudios.com/implementation/frameworks/nest/dependency-cruiser-config.html
- https://github.com/sverweij/dependency-cruiser
- https://github.com/javierbrea/eslint-plugin-boundaries
- https://github.com/un-ts/eslint-plugin-import-x
- https://www.prisma.io/docs/guides/upgrade-prisma-orm/v7
- https://www.prisma.io/docs/orm/reference/prisma-cli-reference
- https://www.prisma.io/docs/guides/upgrade-prisma-orm/postgresql
- https://github.com/webpro-nl/knip
- https://github.com/depcheck/depcheck
- https://github.com/lirantal/lockfile-lint
- https://google.github.io/osv-scanner/usage/
- https://github.com/oasdiff/oasdiff
- https://vitest.dev/config/coverage
- https://github.com/plantain-00/type-coverage
- https://github.com/nodejs/corepack/blob/main/README.md
- https://prettier.io/docs/integrating-with-linters
- https://registry.npmjs.org/-/package/typescript/dist-tags
- https://registry.npmjs.org/-/package/prisma/dist-tags
- https://registry.npmjs.org/-/package/@prisma/client/dist-tags
- https://registry.npmjs.org/-/package/typescript-eslint/dist-tags
- https://registry.npmjs.org/-/package/dependency-cruiser/dist-tags
