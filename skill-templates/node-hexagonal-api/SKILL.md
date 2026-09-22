---
name: node-hexagonal-api
description: Hexagonal Architecture (Ports and Adapters) for TypeScript Node.js backends — strict layer boundaries, interface ports, and swappable adapters.
---

# Node.js (TypeScript) — "Max Power" Hexagonal Backend

## AI Context & Token Optimization

1. **Interfaces as Ports:** TypeScript `interface` is the port. The AI reads one interface file and knows the entire contract — no implementation archaeology.
2. **Strict Mode Always:** `strict: true` in `tsconfig.json`. `any` is banned in core and application layers; `unknown` + narrowing at adapter edges.
3. **Constructor Injection:** Explicit constructor parameters over service locators. Missing dependencies fail at composition time, not in production.

## Project Structure

```
project-root/
├── src/
│   ├── core/
│   │   ├── domain/              # Pure entities (no imports from outside core)
│   │   └── ports/
│   │       ├── inbound/         # Primary ports (e.g., UserService)
│   │       └── outbound/        # Secondary ports (e.g., UserRepository, Clock)
│   ├── application/             # Use cases implementing inbound ports
│   │   └── create-user.ts
│   ├── adapters/
│   │   ├── inbound/
│   │   │   └── http/            # Route handlers (Fastify/Express/Hono)
│   │   └── outbound/
│   │       ├── postgres/        # Prisma/TypeORM repository implementations
│   │       └── cache/           # Redis adapter
│   ├── di/
│   │   └── container.ts         # Composition root (tsyringe or manual wiring)
│   └── main.ts                  # Entry point, builds container, starts server
├── prisma/
│   └── schema.prisma            # Schema source of truth (see database-migration)
├── package.json
└── tsconfig.json                # strict: true
```

## Naming Conventions

| Artifact           | Convention              | Example                  |
| ------------------ | ----------------------- | ------------------------ |
| Port interfaces    | Nouns (`*Repository`) or role `er` nouns | `UserRepository`, `UserCreator` |
| Use cases          | Verb + entity           | `CreateUser`, `ArchiveOrder` |
| Files              | `kebab-case.ts`         | `create-user.ts`         |
| DTOs               | `*Dto` with zod/class-validator | `CreateUserDto`   |

## Architectural Patterns

**Zero-Framework Core:** `src/core` imports NOTHING from frameworks (no http lib, no ORM, no validation lib in entities). Violation fails review.
**Dependency Direction:** adapters depend on core ports; core never imports adapters. Import-lint rule or review checklist enforces it.
**DTOs at the Edge:** validate at inbound adapters (zod schemas), map to domain entities immediately. Never leak ORM models through ports.
**Clock Abstraction:** `Clock` port (`now(): Date`) in `core/ports/outbound`. Banned: `new Date()` in domain/application code — inject the clock.

## Universal DateTime Governance

- **UTC at rest:** store ISO-8601 UTC strings or epoch ms. Banned: locale-formatted date strings in storage/cache.
- **Transmit:** ISO-8601 with offset or epoch ms, matching the API contract.

## Testing Strategies

| Layer       | Test Type   | Framework / Tools              |
| ----------- | ----------- | ------------------------------ |
| Application | Unit        | `vitest` + in-memory port fakes |
| Adapters    | Integration | `vitest` + `testcontainers` (real PG/Redis) |

- Write table-driven (`it.each`) tests for all use cases against faked outbound ports.
- Inbound HTTP routes tested via supertest-style injection with the real container and faked repositories.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

### Strict Baseline

> Target: Node.js + TypeScript backend organized as Hexagonal Architecture (Ports and Adapters).
> All versions verified live against the npm registry / project release pages in 2025-2026. Pinned
> to the **strictest maintained** tool for each role. Deprecated or dormant tools are called out
> explicitly and excluded from the mandatory chain.

### Required Toolchain

| Tool | Purpose | Minimum version | Activate |
| --- | --- | --- | --- |
| Node.js | Runtime; LTS only | 24.0.0 (24.x Active LTS "Krypton") | `.nvmrc` → `24` ; `package.json` → `"engines": { "node": ">=24.0.0" }` |
| TypeScript | `tsc --noEmit` type gate + parser backend for typed lint | 6.0.3 | `npm i -D typescript@6.0.3` |
| @typescript/native-preview (optional) | TS7 `tsgo` fast type-check *alongside* TS6; TS7 has no programmatic API yet so typed-lint tools cannot use it | 7.0.2 | `npm i -D @typescript/native-preview@^7` (run via `tsgo --noEmit` only) |
| ESLint | Core linter, flat config only (eslintrc deleted in v10) | 10.0.0 (10.4.x) | `npm i -D eslint@^10 @eslint/js@^10` |
| typescript-eslint | Type-aware rule engine (`strictTypeChecked`, `stylisticTypeChecked`) | 8.70.1 | `npm i -D typescript-eslint@^8` |
| eslint-plugin-n | Node correctness (`no-process-exit`, `no-missing-import`, deprecation) | 18.2.2 | `npm i -D eslint-plugin-n@^18` |
| dependency-cruiser | **Primary** architectural boundary + cycle enforcement on the real resolved graph | 18.4.0 | `npm i -D dependency-cruiser@^18.4` |
| eslint-plugin-boundaries | Secondary, in-editor boundary feedback (import-time, entity model v7) | 7.2.0 | `npm i -D eslint-plugin-boundaries@^7` |
| eslint-plugin-import-x (optional) | Fast per-file `no-restricted-paths` guard; maintained fork (ESLint 10 ready) | 4.16.2 | `npm i -D eslint-plugin-import-x@^4` |
| Vitest + @vitest/coverage-v8 | Unit / contract / property runner with fail-on-threshold coverage | 4.1.9 | `npm i -D vitest@^4 @vitest/coverage-v8@^4` |
| testcontainers | Real infra in contract tests (Postgres, Redis, broker) | 12.1.0 | `npm i -D testcontainers@^12` |
| fast-check | Property-based tests for core invariants | 4.9.0 | `npm i -D fast-check@^4` |
| tsd | Type-level tests (`expectType` / `expectError`) | 0.33.0 | `npm i -D tsd@^0.33` |
| @microsoft/api-extractor | Public API surface + declaration-diff gate | 7.59.1 | `npm i -D @microsoft/api-extractor@^7` |
| publint | Package `exports` / publish-metadata gate | 0.3.24 | `npm i -D publint@^0.3` |
| @arethetypeswrong/cli | Consumer-side `.d.ts` / module-resolution gate | 0.18.5 | `npm i -D @arethetypeswrong/cli@^0.18` |
| knip | Unused files, exports, and dependencies | 6.4.1 | `npm i -D knip@^6` |
| lockfile-lint | Lockfile host/integrity policy (anti-typosquat/injection) | 5.0.1 | `npm i -D lockfile-lint@^5` |
| osv-scanner | Vulnerability scan against OSV (replaces/augments `npm audit`) | 2.5.1 | `go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest` or the official GH Action / binary |
| zod (or valibot) | Strict boot-time environment schema | 4.5.4 (valibot 1.4.2) | `npm i zod@^4` |

**Discarded / demoted (say so, do not silently use):**
- **madge** — cycle/graph tool, but last npm release is **8.0.0, Aug 2024** (dormant ~2 years, download trend falling). Its only irreplaceable role, cycle detection, is already covered by dependency-cruiser's `no-circular` rule (actively maintained, minimum 18.4.0 — the `$1` backreference used below was validated on 18.4). Keep madge only for one-off visual graphs, never as a gate.
- **depcheck** — superseded by **knip** (knip covers files + exports + dependencies and is actively maintained; depcheck 1.4.7 last shipped Aug 2025 and is narrower).
- **eslint-plugin-import** — effectively frozen/refuses `exports`/specifier support; the maintained successor is **eslint-plugin-import-x**, which declares ESLint `^8.57 || ^9 || ^10`.
- **TypeScript 7.x as the typed-linting backend** — 7.0.2 is npm `latest`, but `typescript-eslint` supports only `>=4.8.4 <6.1.0`; pointing `typescript` at 7 makes typed lint crash (`ts.Extension.Cjs` undefined). Pin `typescript@6.0.3` for lint; run TS7 side-by-side via `tsgo` for speed only.

### Strict Baseline Config

`tsconfig.json` — every strict flag, `tsc --noEmit` is the gate:

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
    "erasableSyntaxOnly": true,

    /* emit for libs; keep type-check honest */
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "skipLibCheck": false
  },
  "include": ["src"],
  "exclude": ["dist", "node_modules"]
}
```

`eslint.config.mjs` — ESLint 10 flat config, strictest type-checked presets:

```js
// @ts-check
import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';
import node from 'eslint-plugin-n';

export default defineConfig(
  { ignores: ['dist/**', 'coverage/**', 'node_modules/**', '**/*.d.ts'] },

  js.configs.recommended,

  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,

  {
    files: ['**/*.{ts,mts,cts}'],
    languageOptions: {
      parserOptions: {
        projectService: true,               // typed linting; no tsconfig.eslint.json
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
      '@typescript-eslint/consistent-type-imports': ['error', { prefer: 'type-imports', fixStyle: 'inline-type-imports' }],
      '@typescript-eslint/no-import-type-side-effects': 'error',
      '@typescript-eslint/explicit-function-return-type': ['error', { allowExpressions: false }],
      '@typescript-eslint/no-explicit-any': 'error',
    },
  },

  node.configs["flat/recommended-module"],
);
```

`.dependency-cruiser.cjs` — **the boundary gate** (copy-paste; layout `src/core`, `src/adapters`, `src/shared`, `src/composition`):

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
      name: 'core-no-runtime-deps',
      severity: 'error',
      comment: 'domain+ports (the hexagon) must have ZERO npm runtime dependencies.',
      from: { path: '^src/core/' },
      to: { dependencyTypes: ['npm'], pathNot: '^src/core/' },
    },
    {
      name: 'core-no-node-builtins',
      severity: 'error',
      comment: 'domain+ports must not touch Node builtins (fs/net/http/crypto).',
      from: { path: '^src/core/' },
      to: { dependencyTypes: ['core'] },
    },
    {
      name: 'core-no-outward',
      severity: 'error',
      comment: 'core must never import adapters, shared infra, or the composition root.',
      from: { path: '^src/core/' },
      to: { path: '^src/(adapters|shared|composition)/' },
    },
    {
      name: 'no-cross-adapter',
      severity: 'error',
      comment: 'adapters must not import each other; collaborate through core ports.',
      from: { path: '^src/adapters/([^/]+)/' },
      to: { path: '^src/adapters/([^/]+)/', pathNot: '^src/adapters/$1/' }, // $1 validated on 18.4
    },
    {
      name: 'adapters-inward-only',
      severity: 'error',
      comment: 'adapters may import core/shared/their own folder only — never the composition root.',
      from: { path: '^src/adapters/' },
      to: { path: '^src/(?!core/|adapters/|shared/)' },
    },
    {
      name: 'shared-no-outward',
      severity: 'error',
      comment: 'shared infra must not depend on core, adapters, or composition.',
      from: { path: '^src/shared/' },
      to: { path: '^src/(core|adapters|composition)/' },
    },
    {
      name: 'no-orphans',
      severity: 'error',
      comment: 'unreferenced modules are dead code.',
      from: { orphan: true, pathNot: ['\\.d\\.ts$', '\\.test\\.ts$', '\\.spec\\.ts$', '^src/composition/'] },
      to: {},
    },
  ],
  options: {
    tsConfig: { fileName: 'tsconfig.json' },   // resolves tsconfig paths + aliases
    tsPreCompilationDeps: true,
    doNotFollow: { path: 'node_modules' },
    enhancedResolveOptions: { exportsFields: ['exports'], conditionNames: ['import', 'require', 'node', 'default'] },
    exclude: { path: ['\\.test\\.ts$', '\\.spec\\.ts$', '\\.config\\.(ts|js|mjs|cjs)$', '^dist/'] },
    includeOnly: { path: '^src/' },
  },
};
```

`knip.json` — dead code / dependency hygiene:

```jsonc
{
  "$schema": "https://unpkg.com/knip@6/schema.json",
  "entry": ["src/composition/main.ts"],
  "project": ["src/**/*.ts", "!src/**/*.test.ts", "!src/**/*.spec.ts"],
  "ignoreExportsUsedInFile": true
}
```

`vitest.config.ts` — coverage thresholds are the gate (Vitest 4 requires `coverage.include`; `coverage.all` was removed):

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts', 'test/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary'],
      include: ['src/core/**/*.ts', 'src/adapters/**/*.ts'],
      thresholds: {
        lines: 100,
        functions: 100,
        branches: 100,
        statements: 100,
        perFile: true,                         // every file, not just aggregate
        'src/core/**': { branches: 100, functions: 100, lines: 100, statements: 100 }, // the hexagon is fully covered
      },
    },
  },
});
```

Boot-time env schema (fails the process before the server listens; unit-tested):

```ts
// src/composition/config.ts
import { z } from 'zod';

const Env = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  PORT: z.coerce.number().int().positive(),
  DATABASE_URL: z.string().url(),
});

export type Config = z.infer<typeof Env>;
export const loadConfig = (env: NodeJS.ProcessEnv = process.env): Config => Env.parse(env);
```

`package.json` scripts — the single gate chain:

```jsonc
{
  "type": "module",
  "engines": { "node": ">=24.0.0" },
  "scripts": {
    "verify": "npm run typecheck && npm run lint && npm run arch && npm run deadcode && npm run test && npm run types && npm run package"
  }
}
```

### Mandatory Gate Order

1. `npm ci --ignore-scripts`  *(npm 12 already blocks dependency install scripts; `--ignore-scripts` makes it explicit and works on npm 11)*
2. `npx lockfile-lint --path package-lock.json --type npm --allowed-hosts npm --validate-https`
3. `osv-scanner scan source -r . --licenses`
4. `npx tsc --noEmit`
5. `npx eslint . --max-warnings=0`
6. `npx depcruise src --config .dependency-cruiser.cjs`
7. `npx knip --production`
8. `npx vitest run --coverage`
9. `npx tsd`
10. `npx publint && npx attw --pack .`  *(only when the package is published)*
11. `npx api-extractor run --local`  *(only when a `.api.md` surface is maintained)*

> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.
> (`eslint` is invoked WITHOUT `--fix`; `--max-warnings=0` makes any warning fatal.)

### Hallucination Traps to Block

- Domain/core importing an ORM or web framework (Prisma, TypeORM, Express, NestJS) → `dependency-cruiser` `core-no-runtime-deps` (blocks every `dependencyTypes: ["npm"]` edge into `src/core/`).
- Adapter A importing adapter B directly instead of via a port → `dependency-cruiser` `no-cross-adapter` group-capture rule (`$1` matching).
- Floating / unawaited promise in an async handler silently swallowing failures → `@typescript-eslint/no-floating-promises`.
- Async function passed where a `void`-returning callback is expected (event emitters, `setTimeout`, `forEach`) → `@typescript-eslint/no-misused-promises` (`checksVoidReturn`).
- New union member added but a `switch` not updated → `@typescript-eslint/switch-exhaustiveness-check` (`requireDefaultForNonUnion`).
- `process.exit()` bypassing graceful shutdown (in-flight requests dropped) → `eslint-plugin-n` `n/no-process-exit`.
- Reading `process.env.X` directly (unvalidated/possibly `undefined`) → `zod`/`valibot` boot schema + `noPropertyAccessFromIndexSignature` + `noUncheckedIndexedAccess` + `useUnknownInCatchVariables`.
- Dead adapter / unused export left behind after a refactor → `knip` (files, exports, dependencies).
- `any` leaking through `catch` or library boundaries → `strictTypeChecked` (`no-unsafe-*`) + `@typescript-eslint/no-explicit-any`.
- Broken `exports`/`.d.ts` for consumers despite green local tests → `publint` + `@arethetypeswrong/cli`.
- Supply-chain code execution at install time (Shai-Hulud-class) → `npm ci --ignore-scripts` + `lockfile-lint` + `osv-scanner`.

### Evidence to Record

Paste the exact command and its pass signal into Verification Evidence; all must exit `0`.

- `npx tsc --noEmit` → exit `0`, no output.
- `npx eslint . --max-warnings=0` → exit `0`, summary `0 problems`.
- `npx depcruise src --config .dependency-cruiser.cjs` → exit `0`, output `no dependency violations found`.
- `npx knip --production` → exit `0`, no unused files/exports/dependencies listed.
- `npx vitest run --coverage` → exit `0`, every threshold line reports `>= 100` and `Test Files` all passed.
- `npx tsd` → exit `0`, no type assertion failures.
- `npx publint && npx attw --pack .` → exit `0` (publint: no errors; attw: all resolution modes `🟢`).
- `npx lockfile-lint ... && osv-scanner scan source -r . --licenses` → exit `0`, no `allowed-hosts` violations and **no HIGH/CRITICAL** advisories.
- Unit-only core test proof: `npx vitest run src/core` exits `0` with no `testcontainers`/network started (core has no I/O).
- Env failure proof: `node -e "import('./dist/composition/config.js').then(m=>m.loadConfig({}))" ; test $? -ne 0` (missing vars must throw, not boot).

<!-- sources -->
- https://typescript-eslint.io/users/configs/
- https://typescript-eslint.io/getting-started/typed-linting
- https://typescript-eslint.io/users/dependency-versions/
- https://github.com/typescript-eslint/typescript-eslint/issues/12518
- https://eslint.org/blog/2026/02/eslint-v10.0.0-released/
- https://eslint.org/docs/latest/use/migrate-to-10.0.0
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html
- https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html
- https://registry.npmjs.org/-/package/typescript/dist-tags
- https://github.com/eslint-community/eslint-plugin-n
- https://github.com/sverweij/dependency-cruiser
- https://github.com/sverweij/dependency-cruiser/blob/HEAD/doc/rules-reference.md
- https://github.com/sverweij/dependency-cruiser/blob/HEAD/doc/options-reference.md
- https://github.com/javierbrea/eslint-plugin-boundaries
- https://github.com/javierbrea/eslint-plugin-boundaries/releases/tag/v7.0.0
- https://github.com/un-ts/eslint-plugin-import-x
- https://github.com/un-ts/eslint-plugin-import-x/blob/master/docs/rules/no-restricted-paths.md
- https://vitest.dev/config/coverage
- https://vitest.dev/guide/migration/
- https://github.com/testcontainers/testcontainers-node/releases
- https://fast-check.dev/
- https://knip.dev/reference/configuration
- https://knip.dev/guides/configuring-project-files
- https://github.com/lirantal/lockfile-lint
- https://google.github.io/osv-scanner/supported-languages-and-lockfiles/
- https://github.com/google/osv-scanner/releases
- https://github.com/tsdjs/tsd
- https://www.npmjs.com/package/@microsoft/api-extractor
- https://www.pkgpulse.com/guides/publint-vs-arethetypeswrong-vs-knip-2026
- https://www.pkgpulse.com/guides/publint-vs-arethetypeswrong-vs-pkg-pr-new-package-quality-2026
- https://www.npmjs.com/package/dependency-cruiser
- https://www.npmjs.com/package/eslint-plugin-boundaries
- https://www.npmjs.com/package/eslint-plugin-n
- https://www.npmjs.com/package/madge
- https://www.npmjs.com/package/depcheck
- https://www.npmjs.com/package/lockfile-lint
- https://www.npmjs.com/package/zod
- https://www.npmjs.com/package/valibot
- https://www.npmjs.com/package/knip
- https://cve.optibot.re/blog/nodejs-24-lts-security-guide-2026
- https://github.com/nodejs/Release/issues/1161
- https://www.michal-drozd.com/en/blog/architectural-linting/
- https://github.com/fusic-toybox/architecture-as-steering
- https://docs.synapsestudios.com/implementation/frameworks/nest/dependency-cruiser-config
- https://github.com/zpratt/lousy-agents/blob/main/.dependency-cruiser.cjs

## Currency Baseline

- **Runtime:** Node 22 LTS. **Package manager:** `pnpm` (fallback `npm`). **Validation:** `zod`. **ORM:** `prisma` (migrations via `prisma migrate`, never `db push` on shared DBs).
