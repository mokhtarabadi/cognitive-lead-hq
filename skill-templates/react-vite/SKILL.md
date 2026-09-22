---
name: react-vite
description: React 19 SPA architecture, hooks, and Vite configuration
---

# React (Vite SPA) — Best Practices

## AI Context & Token Optimization

1. **Feature-Sliced Design (FSD):** Strictly group code by feature (e.g., `features/auth/`). This is critical for AI agents, as it keeps all related components, hooks, and APIs in a single localized directory, preventing context exhaustion from scanning global folders.
2. **Strict TypeScript:** Always define `interface Props {}` for components. Pure JS causes prop-drilling hallucinations.
3. **Zustand for State:** Avoid Redux boilerplate. Use Zustand for minimal, easily readable global state.

## Project Structure

```
src/
├── assets/              # Static assets
├── components/          # Shared, reusable UI components
│   ├── common/          # Buttons, Inputs, Modals
│   └── layout/          # Header, Sidebar
├── features/            # Feature-based modules
│   └── auth/            # Co-locate auth components, hooks, api
├── hooks/               # Global custom React hooks
├── pages/               # Route-level components
├── services/            # API clients and network calls
├── store/               # Global state (Zustand/Redux)
├── utils/               # Pure helper functions
├── App.tsx              # Main entry and Router provider
└── main.tsx             # Vite mount point
```

## Naming Conventions

- **Components**: `PascalCase` (e.g., `UserProfile.tsx`)
- **Hooks**: `camelCase` starting with `use` (e.g., `useTheme.ts`)
- **Files/Utils**: `camelCase` or `kebab-case` (e.g., `formatDate.ts`)

## Architectural Patterns

- **Feature-sliced Design**: Group code by feature (`features/auth`, `features/dashboard`) rather than by type, scaling better for large SPAs.
- **State Management**: Use `Zustand` for global UI state. Use `TanStack React Query` for server state and data fetching.
- **Strict typing**: Use TypeScript interfaces for component props (`interface ButtonProps {}`).
- **Performance**: Use `React.memo`, `useMemo`, and `useCallback` only when profiling indicates a bottleneck, not preemptively.

## Universal DateTime Governance

- **API Boundary:** Receive datetimes as epoch ms (number) or ISO-8601 UTC strings from the backend. Never parse timezone-naive date strings.
- **Client Formatting:** Use `Intl.DateTimeFormat` with explicit `timeZone` option for user-facing display. Never rely on the browser's default timezone detection alone.
- **Utilities:** Use `dayjs` with `dayjs/plugin/utc` for UTC normalization. Store all internal state as epoch ms. Only convert to localized strings at render time.
- **State:** Timestamps in Zustand stores must be epoch ms (number). Never store `Date` objects in global state.

## Testing Strategies

- **Framework**: `Vitest` + `React Testing Library`.
- **Approach**: Render components, query by accessibility roles (`getByRole`), and simulate user events using `@testing-library/user-event`.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

Stack: React 19 SPA built with Vite, Feature-Sliced Design (FSD), strict TypeScript,
Zustand for global/UI state, TanStack Query for server state, Vitest + React Testing
Library for component tests. Every command below is designed to *fail the build*
instead of silently drifting. Versions verified against npm registry `dist-tags` and
GitHub releases on 2026-09-21.

Status of the stack at review time: React 19.3.0, Vite 8.3.0 (Rolldown engine),
TypeScript 7.0.2 (native Go `tsc`) with TypeScript 6.0.2 as the typescript-eslint-
compatible engine, ESLint 10.11.0.

## Required Toolchain

| tool | purpose | minimum version to pin | install/availability note |
| --- | --- | --- | --- |
| Node.js | runtime for the whole gate | `24.20.0` (LTS "Krypton") | Node 20 EOL 2026-04-30; Node 26 is Current, not LTS until Oct 2026. Do NOT pin 26 yet. |
| pnpm | install + strict peer/lockfile policy | `12.5.1` | `corepack enable && corepack prepare pnpm@12.5.1 --activate`. The `+sha512…` hash is auto-generated; do not hand-edit. |
| Prettier | formatting (only formatter) | `3.9.8` | `pnpm add -D -E prettier@3.9.8`. Prettier 4 is still `4.0.0-alpha.13` — do NOT use. |
| ESLint | lint engine, flat config | `10.11.0` | ESLint 9.x EOL 2026-08-06. ESLint 10 removed `.eslintrc*` entirely. |
| typescript-eslint | typed strict rules | `8.70.1` | Peer is `typescript >=4.8.4 <6.1.0` — it does NOT accept TypeScript 7. |
| eslint-plugin-react-hooks | Rules of React + React Compiler rules | `7.1.1` | Flat presets only: `configs.flat.recommended` / `configs.flat['recommended-latest']`. Peer `eslint ^10` OK. |
| eslint-plugin-jsx-a11y | static JSX a11y rules | `6.10.2` | Peer range stops at `eslint ^9`; works on 10 but requires the peer override below (or use `eslint-plugin-jsx-a11y-x@0.2.0`). Override owner: stack skill maintainer; expiry: drop the override when upstream ships an eslint-10 peer range. |
| eslint-config-prettier | disable rules that fight Prettier | `10.1.8` | Must be the LAST entry in the flat-config array. |
| eslint-plugin-react-refresh | Vite HMR boundary safety | `0.5.7` | Peer `eslint ^9 || ^10`. |
| @vitest/eslint-plugin | no stray `.only`/`.skip`, valid `expect` | `1.6.27` | Vitest 5's official lint plugin. |
| TypeScript (compat alias) | typescript-eslint engine (explicit TS7 path) | `@typescript/typescript6@6.0.2` | Installed as the `typescript` package via `npm:` alias so the parser's peer is satisfied; TS7 runs via `node ./node_modules/typescript-7/bin/tsc` (pnpm exposes no `tsc6` bin). |
| TypeScript (native, fast) | production typecheck, `tsc` | `typescript@7.0.2` | Installed under the `typescript-7` alias; ships the native Go `tsc` (8–12x faster). |
| Steiger | FSD architecture linter (public API, cross-imports) | `steiger@0.6.0` | Plus plugin `@feature-sliced/steiger-plugin@0.7.0`; still beta — keep `--fail-on-warnings`. |
| dependency-cruiser | circular / orphan / unresolvable / layer graph | `18.4.0` | Bin is `depcruise`. Engines `^22 || ^24 || >=26`. |
| Knip | dead code + unused deps + unused exports | `6.37.0` | Requires Node `>=20.19`. Peer deps `typescript` + `@types/node`. |
| audit-ci | vulnerability gate for pnpm | `7.1.0` | Reads `pnpm audit`; config `audit-ci.jsonc`. |
| npm-check-updates | dependency currency check | `23.1.0` | `ncu` for deliberate upgrades; not a silent auto-bump. |
| Vitest | unit/component test runner | `5.0.1` | `pnpm add -D -E vitest@5.0.1`. |
| @vitest/coverage-v8 | coverage + thresholds | `5.0.1` | Must match Vitest exactly (`peer vitest@5.0.1`). |
| @testing-library/react | component tests | `16.3.3` | RTL for React 19. |
| @testing-library/user-event | realistic event simulation | `14.6.7` | Use instead of `fireEvent`. |
| @testing-library/jest-dom | DOM matchers | `7.0.1` | Import in `vitest.setup.ts`. |
| jsdom | DOM environment | `30.1.0` | Required for axe; do NOT use happy-dom (see traps). |
| axe-core | a11y engine | `4.13.0` | Direct, or via jest-axe. |
| jest-axe | axe matchers for Vitest `expect` | `11.0.0` | Framework-agnostic matchers; `vitest-axe` on npm is stale (see traps). |
| @playwright/test | end-to-end tests | `1.63.0` | `pnpm exec playwright install --with-deps chromium`. |
| @axe-core/playwright | a11y assertions in E2E (incl. color contrast) | `4.13.0` | Peer `playwright-core >= 1.0.0`. |
| Vite | build + dev server | `8.3.0` | Rolldown is the only bundler; Rollup/esbuild options are renamed/deprecated. |
| @vitejs/plugin-react | React fast-refresh (Oxc) | `6.1.1` | Peer `vite ^8`. Babel removed; React Compiler is opt-in via `reactCompilerPreset`. |
| size-limit + @size-limit/file | hard bundle budgets | `size-limit@14.0.0`, `@size-limit/file@14.0.0` | Engines include `^24.5.0`. |
| rollup-plugin-visualizer | chunk/module analysis | `7.1.1` | Peer includes `rolldown ^1` (Vite 8 compatible). |
| globals | browser globals for ESLint flat config | `17.12.0` | `languageOptions.globals: globals.browser`. |
| @eslint/js | core recommended preset | `10.0.1` | Pairs with ESLint 10. |

**Archived / deprecated / superseded in 2026 — never recommend:** `eslint-plugin-import@2.32.0`
(stale, peer stops at ESLint 9 → use `eslint-plugin-import-x`), `ts-prune@0.10.3` and
`depcheck@1.4.7` (superseded by Knip), `vitest-axe@0.1.0` (npm build 4 years old, no Vitest 5),
`better-npm-audit@3.11.0` (npm-only; use `audit-ci`), `.eslintrc*` (removed in ESLint 10),
Prettier 4 (alpha only). Biome is rejected: it cannot run type-aware `typescript-eslint` rules
or the React Compiler rules this stack depends on.

## Strict Baseline Config

Create these files at the repo root. Exact strict settings:

**`.nvmrc` / `.node-version`** — both contain the single line `24.20.0`.

**`package.json`** — pinning + script surface (all scripts fail fast). Run `corepack prepare pnpm@12.5.1 --activate` to generate the `+sha512…` hash; do not hand-edit it:
```jsonc
{
  "packageManager": "pnpm@12.5.1",
  "engines": { "node": ">=24.20.0 <25", "pnpm": ">=12.5.1" },
  "devDependencies": {
    "typescript": "npm:@typescript/typescript6@6.0.2",
    "typescript-7": "npm:typescript@7.0.2"
  },
  "pnpm": {
    "onlyBuiltDependencies": [],
    "peerDependencyRules": { "allowedVersions": { "eslint-plugin-jsx-a11y>eslint": "10" } }
  },
  "scripts": {
    "format:check": "prettier --check .",
    "lint": "eslint . --max-warnings=0 --cache",
    "typecheck": "tsc --noEmit",
    "typecheck:native": "node ./node_modules/typescript-7/bin/tsc --noEmit",
    "arch": "steiger ./src --fail-on-warnings",
    "graph": "depcruise --config .dependency-cruiser.cjs src",
    "deadcode": "knip --treat-config-hints-as-errors",
    "audit": "audit-ci --config ./audit-ci.jsonc",
    "test": "vitest run --coverage",
    "build": "vite build",
    "size": "size-limit",
    "e2e": "playwright test"
  }
}
```

**`.npmrc`** — the actual strict install policy:
```ini
strict-peer-dependencies=true
auto-install-peers=false
save-exact=true
verify-deps-before-run=true
```

**`tsconfig.json`** — TS 6/7 defaults are already strict (`strict`, `module: esnext`,
`target: es2025`), but pin them explicitly and add the non-default strict flags; also
compensate for the new `types: []` and `rootDir: .` defaults:
```jsonc
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    "useUnknownInCatchVariables": true,
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noUncheckedSideEffectImports": true,
    "forceConsistentCasingInFileNames": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "target": "es2025",
    "lib": ["ES2025", "DOM", "DOM.Iterable"],
    "types": ["vite/client"],
    "rootDir": "./src",
    "noEmit": true,
    "skipLibCheck": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```
`tsconfig.node.json` covers `vite.config.ts`, `eslint.config.mjs`, `playwright.config.ts`
with `"types": ["node"]` and `"lib": ["ES2025"]`.

**`eslint.config.mjs`** — flat config, typed linting via `projectService` (NOT the removed
`parserOptions.project`), strict variants, compiler rules last-but-one, Prettier last:
```js
// @ts-check
import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import tseslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import reactRefresh from 'eslint-plugin-react-refresh';
import vitest from '@vitest/eslint-plugin';
import prettier from 'eslint-config-prettier';

export default defineConfig([
  { ignores: ['dist', 'coverage', 'playwright-report', 'test-results'] },
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.strictTypeChecked,
      tseslint.configs.stylisticTypeChecked,
      reactHooks.configs.flat['recommended-latest'],   // all React Compiler rules on
      jsxA11y.flatConfigs.strict,
    ],
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    plugins: { 'react-refresh': reactRefresh },
    rules: {
      'react-refresh/only-export-components': ['error', { allowConstantExport: true }],
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unsafe-assignment': 'error',
      '@typescript-eslint/explicit-module-boundary-types': 'error',
    },
  },
  {
    files: ['src/**/*.{test,spec}.{ts,tsx}'],
    extends: [vitest.configs.recommended],
    rules: { 'vitest/no-focused-tests': 'error', 'vitest/no-disabled-tests': 'error' },
  },
  prettier, // MUST stay last
]);
```
`reactHooks.configs.flat['recommended-latest']` enables the compiler rules
`react-hooks/purity`, `/immutability`, `/refs`, `/set-state-in-effect`,
`/set-state-in-render`, `/preserve-manual-memoization`, `/static-components`,
`/incompatible-library` — use `configs.flat.recommended` instead if the compiler is off.

**`.prettierrc`** — `{ "singleQuote": true, "trailingComma": "all", "printWidth": 100 }`
plus `.prettierignore` (`dist`, `coverage`, lockfile, `playwright-report`).
Run it as `prettier --check .` — never `prettier --write` inside a gate.

**`steiger.config.ts`** — FSD-native rules; keep warnings fatal:
```ts
import { defineConfig } from 'steiger';
import fsd from '@feature-sliced/steiger-plugin';
export default defineConfig([...fsd.configs.recommended]);
```
Run `steiger ./src --fail-on-warnings`. This enforces `fsd/public-api` (every slice must
export through `index.ts`), `fsd/forbidden-imports` (no imports from higher layers, no
cross-imports between same-layer slices), `fsd/no-public-api-sidestep` (no deep imports
into a slice's internals), `fsd/no-reserved-folder-names`, `fsd/insignificant-slice`.

**`.dependency-cruiser.cjs`** — graph hygiene that Steiger does not cover:
```js
module.exports = {
  forbidden: [
    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
    { name: 'no-orphans', severity: 'error', from: { orphan: true }, to: {} },
    { name: 'not-to-unresolvable', severity: 'error', from: {}, to: { couldNotResolve: true } },
  ],
  options: {
    tsConfig: { fileName: 'tsconfig.json' },
    doNotFollow: { path: 'node_modules' },
    tsPreCompilationDeps: true,
  },
};
```
Run `depcruise --config .dependency-cruiser.cjs src`.

**`knip.json`** — dead code + unused deps; make the FSD public API the entry points:
```jsonc
{
  "entry": ["src/main.tsx", "src/app/**/index.ts"],
  "project": ["src/**/*.{ts,tsx}"],
  "ignoreDependencies": [],
  "rules": { "files": "error", "dependencies": "error", "unlisted": "error", "exports": "error", "types": "error" }
}
```
Run `knip --treat-config-hints-as-errors`. Do NOT use `--strict` on a single-package SPA —
it flips production mode and stops reporting unused `devDependencies`.

**`vitest.config.ts`** — Vitest 5, jsdom (axe-safe), thresholds are the gate:
```ts
import { defineConfig } from 'vitest/config';
export default defineConfig({
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    globals: true,
    restoreMocks: true,
    clearMocks: true,
    unstubGlobals: true,
    coverage: {
      provider: 'v8',
      include: ['src/**/*.{ts,tsx}'],
      exclude: ['src/**/*.d.ts', 'src/main.tsx', 'src/**/index.ts'],
      reporter: ['text', 'lcov'],
      thresholds: {
        lines: 85, functions: 85, branches: 80, statements: 85,
        perFile: { lines: 70, functions: 70, branches: 60, statements: 70 },
      },
    },
  },
});
```
**`vitest.setup.ts`** — `import '@testing-library/jest-dom/vitest';` then
`import { toHaveNoViolations } from 'jest-axe'; expect.extend(toHaveNoViolations);`
Component tests use `@testing-library/react` + `@testing-library/user-event` and query by
role (`getByRole`, `findByRole`); a11y assertions call `axe(container)` from `jest-axe`.

**`playwright.config.ts`** — `forbidOnly: !!process.env.CI`, `retries: process.env.CI ? 2 : 0`,
`workers: process.env.CI ? 1 : undefined`, `use: { trace: 'on-first-retry' }`,
`webServer: { command: 'vite preview --port 4173', url: 'http://localhost:4173' }`.
E2E a11y uses `AxeBuilder` from `@axe-core/playwright`.

**`size-limit.config.mjs`** — hard budgets, checked after `vite build`:
```js
export default [
  { path: 'dist/assets/index-*.js', limit: '180 kB', gzip: true },
  { path: 'dist/assets/*.css', limit: '40 kB', gzip: true },
];
```

**`audit-ci.jsonc`**:
```jsonc
{ "package-manager": "pnpm", "audit-level": "high", "allowlist": [], "report-type": "important" }
```

**`vite.config.ts`** — Vite 8 names (see traps), analyzer, no sourcemaps in prod:
```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';
export default defineConfig({
  plugins: [react(), visualizer({ filename: 'dist/stats.html', gzipSize: true, brotliSize: true })],
  build: {
    sourcemap: false,
    chunkSizeWarningLimit: 500,
    rolldownOptions: { output: { manualChunks: (id) => (id.includes('node_modules') ? 'vendor' : undefined) } },
  },
});
```

## Mandatory Gate Order

Fail-fast, cheapest first. Run each as its own CI step so the first failure stops the chain.

1. `corepack enable && node --version && pnpm --version` — preflight; expect `v24.20.0` / `12.5.1`.
2. `pnpm install --frozen-lockfile --strict-peer-dependencies` — immutable install; fails on drift or phantom peers.
3. `pnpm exec lockfile-lint --path pnpm-lock.yaml --type pnpm --allowed-hosts npm --validate-https` — lockfile provenance and HTTPS check; fails on non-HTTPS or unexpected registry.
4. `pnpm exec prettier --check .`
5. `pnpm exec eslint . --max-warnings=0 --cache`
6. `pnpm exec tsc --noEmit` — TypeScript 6.0.2 parity check (same engine typescript-eslint uses; the `typescript` package is the v6 alias so the parser peer `>=4.8.4 <6.1.0` resolves).
7. `node ./node_modules/typescript-7/bin/tsc --noEmit` — TypeScript 7 native typecheck (fast; explicit path into the aliased `typescript-7` package because pnpm exposes no `tsc6` bin).
8. `pnpm exec steiger ./src --fail-on-warnings`
9. `pnpm exec depcruise --config .dependency-cruiser.cjs src`
10. `pnpm exec knip --treat-config-hints-as-errors`
11. `pnpm exec audit-ci --config ./audit-ci.jsonc`
12. `pnpm exec vitest run --coverage`
13. `pnpm exec vite build`
14. `pnpm exec size-limit`
15. `pnpm exec playwright test`
16. `pnpm dlx npm-check-updates@23.1.0 --errorLevel 1` — optional currency report (non-blocking owner).

## Hallucination Traps to Block

Concrete failure modes an AI generates on this exact stack, and the gate step that catches each:

| Trap (what an AI writes from stale memory) | Why it is wrong in 2026 | Caught by |
| --- | --- | --- |
| `"typescript": "^5.x"` or `"^7.0.2"` in devDependencies | typescript-eslint 8.70.1 peer is `>=4.8.4 <6.1.0`; TS 7 support issue #12518 was closed *not planned*. TS 7 breaks the typed-lint program (`getWatchProgramsForProjects`). | Step 2 (peer resolution) and Step 4 (parser crash) |
| Running only `tsc --noEmit` and assuming lint covers types | Vite 8 does not typecheck on `vite build`; type errors ship silently. | Steps 5 + 6 before build |
| `.eslintrc.json` / `"eslintConfig"` in package.json / `--ext .ts` | Legacy config was removed in ESLint 10; `--ext` was removed with flat config. | Step 4 fails immediately |
| `parserOptions: { project: true }` | Deprecated for typed linting; current form is `parserOptions.projectService: true`. | Step 4 (type-aware rules silently stop firing if mis-set) |
| `setupFilesAfterEach`, `eslint-env mocks`, `--rulesdir` | Removed/erroring in ESLint 10. | Step 4 |
| `build.rollupOptions` / `transformWithEsbuild` / `esbuild: {}` in Vite config | Renamed in Vite 8: `build.rolldownOptions`, `transformWithOxc`, `oxc: {}`. Old names warn (and will be removed); `worker.rollupOptions` → `worker.rolldownOptions`. | Step 12 (deprecation warning + build) |
| Object-form `manualChunks: { vendor: [...] }` | Rolldown does not support the object form — only the function form. | Step 12 (build error) |
| `import { x } from '@/features/auth/ui/LoginForm'` (deep slice import) | Violates FSD public API and `no-public-api-sidestep`. | Step 7 |
| `features/cart` importing `features/product` | Same-layer cross-import violates the FSD import rule. | Step 7 (`fsd/forbidden-imports`) |
| Component test env set to `happy-dom` | axe-core's `Node.prototype.isConnected` check breaks under happy-dom, so a11y assertions pass vacuously. | Step 11 with `environment: 'jsdom'` |
| Importing `vitest-axe` and calling `.toHaveNoViolations()` | npm `vitest-axe` is `0.1.0` (4 years old); matchers may be undefined → tests pass without asserting. | Step 11 (`jest-axe` + explicit `expect.extend`) |
| Fake timers left on around `axe()` | axe times out when `setTimeout` is mocked; results become empty and pass. | Step 11 (axe assertions) |
| `@testing-library/react` queried by `container.querySelector` | Bypasses a11y roles and hides broken markup. | Step 4 (`jsx-a11y`) + Step 11 (role queries). |
| `expect(true).toBe(true)` / snapshot-only tests to raise coverage | Coverage thresholds measure lines executed, not assertions; per-file thresholds limit the damage. | Step 11 (`coverage.thresholds.perFile`) |
| `tsconfig` relying on `types` auto-loading all `@types/*` | TypeScript 6.0 changed `types` default to `[]`; globals vanish (`process`, `describe`) without an explicit list. | Steps 5 + 6 |
| `"outDir": "dist"` without `"rootDir": "./src"` | TS 6.0 defaults `rootDir` to the tsconfig dir → emit lands in `dist/src/`. | Step 5/6 emit paths, build smoke |
| `moduleResolution: "node"`, `target: "es5"`, `assert { type: 'json' }` | ES5 deprecated; `assert` replaced by `with` in TS 6/7; `node` resolution deprecated. | Steps 5 + 6 |
| Adding a dep to `package.json` without installing, or leaving `let x` unused | Drift between manifest and code. | Step 9 (`knip` `unlisted`, `dependencies`, `exports`) |
| Committing `pnpm-lock.yaml` changes while `strict-peer-dependencies=false` | Phantom/duplicated packages, non-reproducible CI. | Step 2 |
| `size-limit` config pointing at `dist/index.js` after a Vite rename | Budgets silently check a non-existent file. | Step 13 (size-limit errors on missing path) |
| `playwright test` without `forbidOnly` | A committed `.only` skips the rest of the suite and CI stays green. | Step 14 (`forbidOnly: !!process.env.CI`) |

## Evidence to Record

Paste the raw command output into the task's Verification Evidence block. Every row is a
separate gate; `$?` must be `0` for PASS.

| Gate | Exact command | Expected result | Exit code |
| --- | --- | --- | --- |
| Install | `pnpm install --frozen-lockfile --strict-peer-dependencies` | `Lockfile is up to date` / `Done`; no peer errors | 0 |
| Format | `pnpm exec prettier --check .` | `All matched files use Prettier code style!` | 0 |
| Lint | `pnpm exec eslint . --max-warnings=0 --cache` | no output; zero warnings | 0 |
| Typecheck (TS6) | `pnpm exec tsc --noEmit` | no diagnostics | 0 |
| Typecheck (TS7) | `node ./node_modules/typescript-7/bin/tsc --noEmit` | no diagnostics | 0 |
| FSD | `pnpm exec steiger ./src --fail-on-warnings` | `✔ No problems found` (0 errors, 0 warnings) | 0 |
| Graph | `pnpm exec depcruise --config .dependency-cruiser.cjs src` | `no dependency violations found` | 0 |
| Dead code | `pnpm exec knip --treat-config-hints-as-errors` | `No issues found` | 0 |
| Vulns | `pnpm exec audit-ci --config ./audit-ci.jsonc` | no advisories at/above `high` | 0 |
| Unit + coverage | `pnpm exec vitest run --coverage` | all suites pass; coverage table ≥ thresholds | 0 |
| Build | `pnpm exec vite build` | `built in <n>ms`; `dist/index.html` + hashed assets exist | 0 |
| Budgets | `pnpm exec size-limit` | each entry `Size limit: Passed` | 0 |
| E2E | `pnpm exec playwright test` | `N passed` (no skipped-only run) | 0 |

Record also: `node --version` (`v24.20.0`), `pnpm --version` (`12.5.1`), and
`pnpm exec tsc --version` (`Version 6.0.2`). If any gate is intentionally waived, record
the waiver, the owner, and an expiry date in the task file.

<!-- sources -->
- npm registry dist-tags (`https://registry.npmjs.org/-/package/<pkg>/dist-tags`) and `https://registry.npmjs.org/<pkg>/latest` for every pinned package
- GitHub Releases API (`https://api.github.com/repos/<owner>/<repo>/releases/latest`) for TypeScript, ESLint, typescript-eslint, Vite, Vitest, Playwright, Knip, eslint-plugin-boundaries, Prettier, Node
- TypeScript 7: https://devblogs.microsoft.com/typescript/announcing-typescript-7-0 , https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-rc , https://www.infoq.com/news/2026/08/typescript-7-released
- TypeScript 6.0 breaking changes: https://devblogs.microsoft.com/typescript/announcing-typescript-6-0 , https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html
- typescript-eslint TS7 gap: https://github.com/typescript-eslint/typescript-eslint/issues/12518 , https://github.com/typescript-eslint/typescript-eslint/releases , https://typescript-eslint.io/users/configs , https://typescript-eslint.io/linting/typed-linting/
- ESLint 10: https://eslint.org/blog/2026/02/eslint-v10.0.0-released , https://eslint.org/docs/latest/use/migrate-to-10.0.0 , https://eslint.org/blog/2026/06/eslint-v10.6.0-released , https://eslint.org/docs/latest/versions/
- react-hooks v7 flat/compiler configs: https://github.com/react/react/tree/main/packages/eslint-plugin-react-hooks , https://github.com/facebook/react/blob/main/packages/eslint-plugin-react-hooks/CHANGELOG.md
- jsx-a11y ESLint 10: https://github.com/jsx-eslint/eslint-plugin-jsx-a11y , https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/issues/1075 , https://dev.to/booyaka101/eslint-plugin-jsx-a11y-says-it-doesnt-support-eslint-10-it-does-380f
- eslint-plugin-import replacement: https://github.com/un-ts/eslint-plugin-import-x , https://github.com/e18e/module-replacements/blob/main/docs/modules/eslint-plugin-import.md
- FSD import rules: https://feature-sliced.design/docs/guides/issues/cross-imports , https://github.com/feature-sliced/steiger , https://github.com/feature-sliced/steiger/blob/master/packages/steiger-plugin-fsd/src/forbidden-imports/README.md
- dependency-cruiser rules: https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md
- Knip: https://knip.dev/overview/getting-started , https://knip.dev/reference/cli
- Supply chain: https://github.com/IBM/audit-ci , https://github.com/lirantal/lockfile-lint (pnpm FAQ) , https://github.com/jeemok/better-npm-audit , https://pnpm.io/npmrc
- Vitest 5 + coverage: https://vitest.dev/config/coverage , https://vitest.dev/guide/migration , https://traceary.com/vitest
- Accessibility in tests: https://github.com/chaance/vitest-axe , https://github.com/nickcolley/jest-axe , https://www.javascript-testing.com/component-integration-testing-frameworks/accessibility-testing-for-components/automating-axe-accessibility-checks-in-vitest
- Playwright 1.63.0: https://github.com/microsoft/playwright/releases
- Vite 8: https://vite.dev/blog/announcing-vite8 , https://vite.dev/blog/announcing-vite8-1 , https://vite.dev/config/build-options , https://github.com/vitejs/vite/blob/main/packages/vite/CHANGELOG.md
- Node LTS: https://nodejs.org/en/blog/release , https://endoflife.date/nodejs
- Bundle budgets: https://github.com/ai/size-limit , https://github.com/btd/rollup-plugin-visualizer

## Currency Baseline

- **React 19:** Baseline React 19 (`useActionState`, `useOptimistic`, ref-as-prop); with React Compiler v1.0 available, keep manual `memo`/`useMemo`/`useCallback` to profiled bottlenecks only.
