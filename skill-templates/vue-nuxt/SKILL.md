---
name: vue-nuxt
description: Vue 3 Composition API, Nuxt 4 routing, and state management
---

# Vue 3 & Nuxt 4 — Best Practices & AI-Driven Scaffolding

## AI Context & Token Optimization

1. **Composition API & `<script setup>` Only:** Do NOT use the Options API. The Composition API is far more token-efficient and predictable for AI code generation.
2. **Auto-Imports:** Rely entirely on Nuxt's auto-imports. Explicitly importing Vue refs or components wastes tokens and causes syntax hallucinations.
3. **TypeScript Mandate:** Always use `lang="ts"`. Strongly typed props and Pinia state are required.

## Modern Nuxt 3 App Architecture

Scaffold Nuxt 3 applications using these guidelines:

1. **Composition API:** Always use `<script setup lang="ts">` with TypeScript. Banned: Options API.
2. **Auto-Imports Leverage:** Rely on Nuxt's auto-imported directory structures for `composables/`, `components/`, and core Vue APIs (`ref`, `computed`, `reactive`).
3. **State Management:** Use Pinia via `@pinia/nuxt`. Define stores using the store-factory function syntax (`defineStore('id', () => { ... })`).
4. **SSR-Safe Data Fetching:** Always use `useFetch` or `useAsyncData` to ensure data loads on the server and hydrates safely on the client. Banned: standard `axios` or bare `fetch` inside components.
5. **Form Validation:** Use Formkit or VeeValidate + Zod for robust client-side schemas.

## Project Structure

```
project/
├── assets/              # Uncompiled assets (CSS, SCSS)
├── components/          # Auto-imported Vue components
│   └── ui/              # Reusable UI elements (buttons, inputs)
├── composables/         # Auto-imported composition functions (Vue useHooks)
├── layouts/             # Shared page layouts
├── pages/               # File-based routing
├── plugins/             # Vue plugins initialized at startup
├── public/              # Static files served at root
├── server/              # Nitro API routes (Nuxt backend)
│   └── api/
├── stores/              # Pinia state management
└── nuxt.config.ts       # Main Nuxt configuration
```

## Naming Conventions

- **Components**: `PascalCase` (e.g., `UserProfile.vue`). Multi-word names are mandatory.
- **Composables**: `camelCase` starting with `use` (e.g., `useAuth.ts`).
- **Pages/Routes**: `kebab-case` (e.g., `user-settings.vue`).

## Architectural Patterns

- **Composition API**: Use `<script setup lang="ts">` exclusively. Avoid the older Options API (`data()`, `methods`).
- **Auto-imports**: Rely on Nuxt's auto-import feature for components, composables, and Vue APIs (`ref`, `computed`). Do not manually import them.
- **State Management**: Use `Pinia` for global state. Avoid Vuex.
- **Data Fetching**: Use `useFetch` or `useAsyncData` for SSR-friendly data fetching. Do not use standard `fetch` or `axios` directly in components.

## Universal DateTime Governance

- **API Boundary:** All datetimes from the backend are epoch ms or ISO-8601 UTC strings. Normalize to epoch ms in Pinia stores.
- **Client Display:** Format using `Intl.DateTimeFormat` with explicit `timeZone` in a composable (`useDateTimeFormatter`). Never rely on the browser's locale alone.
- **SSR Safety:** Use `useAsyncData` with `dayjs.utc()` for datetime parsing in server-side code. Never call `new Date()` in `setup()` without UTC normalization.
- **State:** Timestamps in Pinia stores must be epoch ms (number). Convert to localized strings only in template computed properties.

## Testing Strategies

- **Framework**: `Vitest` + `Vue Test Utils`.
- **Component Testing**: Mount components and test DOM output/emitted events.
- **E2E Testing**: Use `Playwright` or `Cypress`.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

Stack: **Vue 3.5 (Composition API, `<script setup>`) + Nuxt 4.5 + Strict TypeScript**.
All versions below were read live from `registry.npmjs.org` dist-tags and official docs on **2026-09-21**; none are guessed. `latest` means the npm `latest` dist-tag on that date.

## Required Toolchain

| Tool | Purpose | Minimum version to pin | Install / availability note |
| --- | --- | --- | --- |
| Node.js | Runtime floor for every gate | `24.20.0` (LTS "Krypton") | `.nvmrc`/`.node-version`; Vitest 5 needs `^22.12 \|\| ^24 \|\| >=26`, size-limit 14 needs `^22.19 \|\| ^24.5 \|\| >=26` → Node 24 only |
| pnpm | Deterministic install | `12.5.1` | `packageManager: "pnpm@12.5.1"` + Corepack; `--frozen-lockfile` in CI |
| nuxt (CLI `@nuxt/cli`) | Framework + `nuxt prepare/typecheck/build/analyze` | `4.5.2` (CLI `3.37.0`) | binary is `nuxt`; the old `nuxi` name is legacy |
| vue | Runtime | `3.5.43` | transitive via Nuxt, pin explicitly anyway |
| typescript | Type engine used by vue-tsc + typescript-eslint | `6.0.3` — **NOT 7.0.2** | TS 7 has no stable programmatic compiler API; typescript-eslint peer is `>=4.8.4 <6.1.0`; vue-tsc 3.3.11 breaks on TS 7 |
| vue-tsc | SFC type checker for `nuxt typecheck` | `3.3.11` | `@vue/language-core@3.3.11`; peer `typescript >=5.0.0` |
| @vue/tsconfig | Base strict tsconfig | `0.9.1` | requires TS `>=5.8` |
| eslint | Linter (flat config only) | `10.11.0` | `.eslintrc` removed in v10; Node ≥20.19/22.13/24 |
| @eslint/js | Core rules preset | `10.0.1` | must match ESLint 10 major |
| @nuxt/eslint | Project-aware Nuxt flat config generator | `1.17.0` | peer `eslint ^9 \|\| ^10`; emits `.nuxt/eslint.config.mjs` |
| eslint-plugin-vue | Vue correctness rules | `10.11.0` | flat presets incl. `flat/recommended-error`; peer `vue-eslint-parser ^10.3.0` |
| vue-eslint-parser | Parser for `.vue` | `10.4.1` | peer dependency of eslint-plugin-vue v10 |
| typescript-eslint | Typed TS rules | `8.70.1` | `strictTypeChecked` + `stylisticTypeChecked`; peer eslint `^8.57 \|\| ^9 \|\| ^10` |
| prettier | Formatter | `3.9.8` | native `.vue` support, no plugin needed |
| eslint-config-prettier | Disables conflicting stylistic rules | `10.1.8` | append LAST in flat config |
| knip | Dead code + unused dependency detection | `6.37.0` | `--strict`; replaces ts-prune/depcheck |
| dependency-cruiser | Import-boundary / architecture enforcement | `18.4.0` | `.dependency-cruiser.mjs`; `tsConfig` option resolves Nuxt aliases |
| vitest | Unit + Nuxt + e2e runner | `5.0.1` | peer `vite ^6.4 \|\| ^7 \|\| ^8` |
| @vitest/coverage-v8 | Coverage provider | `5.0.1` | must equal vitest version exactly |
| @nuxt/test-utils | Nuxt runtime env + e2e helpers | `4.3.2` | peer `vitest ^4.0.2 \|\| ^5.0.0` |
| @vue/test-utils | Component mounting | `2.5.1` | peer of @nuxt/test-utils (`^2.4.2`) |
| @playwright/test | Browser / e2e driver | `1.63.0` | peer `^1.43.1` for @nuxt/test-utils |
| @axe-core/playwright | WCAG assertions in e2e | `4.13.0` | pairs with `axe-core@4.13.0` |
| eslint-plugin-vuejs-accessibility | Static a11y rules | `2.6.0` | flat preset `configs['flat/recommended']`; peer eslint `^5…^10` |
| size-limit | Bundle-size budget | `14.0.0` | pair with `@size-limit/file@14.0.0` |
| lockfile-lint | Lockfile provenance / HTTPS check | `5.0.1` | supports `--type pnpm` |
| happy-dom | DOM for unit tests | `20.14.5` | `@nuxt/test-utils` peer `>=20.0.11`; jsdom `30.1.0` is the alternative |

**Rejected / superseded — never recommend:**
- `tsc` alone as Vue type checker — cannot parse `.vue`; use `vue-tsc` via `nuxt typecheck`.
- **TypeScript 7.0.2 with any Vue tooling** — `vue-tsc` fails `Cannot find module 'typescript/lib/tsc'` (vuejs/language-tools #6156); typescript-eslint caps at `<6.1.0`.
- `typescript-native-bridge` (`6.0.3-bridge.17.tsgo.7.0.2`) — unofficial pre-release bridge for TS7; not a stable gate dependency.
- **Golar** `0.1.10` — pre-1.0 (0.x), `golar.config.ts` marked `golar/unstable`; `nuxt typecheck --checker golar` is only an opt-in. Do not use as the gate checker.
- `ts-prune` `0.10.3` (last publish 2021) — unmaintained; superseded by knip.
- `depcheck` `1.4.7` (last publish 2023-10) — blind to Nuxt auto-imports/SFCs; superseded by knip.
- `vitest-axe` `0.1.0` (last publish 2022) — abandoned; use `@axe-core/playwright` or `axe-core` directly.
- `@nuxt/a11y` `1.0.0-alpha.1` — alpha DevTools module, API will change; never a CI gate.
- Biome `2.5.14` / oxlint `1.85.0` / oxfmt `0.70.0` — no full `eslint-plugin-vue` parity (oxc issue #15761); cannot run typescript-eslint typed rules.
- `@nuxtjs/axios` `5.13.6` — Nuxt-2-era; use `$fetch`/`useFetch`.
- Cypress — rejected in favor of Playwright (first-class with `@nuxt/test-utils`).
- `.eslintrc.*` any format — removed in ESLint 10.

## Strict Baseline Config

Create exactly these files at project root. Every setting below is load-bearing.

**`package.json`** (pinning + scripts)
```json
{
  "type": "module",
  "packageManager": "pnpm@12.5.1",
  "engines": { "node": ">=24.20.0", "pnpm": ">=12.5.1" },
  "scripts": {
    "prepare": "nuxt prepare",
    "format:check": "prettier --check .",
    "lint": "eslint . --max-warnings 0 --report-unused-disable-directives",
    "lint:fix": "eslint . --fix",
    "deadcode": "knip --strict",
    "boundaries": "depcruise --config .dependency-cruiser.mjs app server shared",
    "typecheck": "nuxt typecheck --checker vue-tsc",
    "test": "vitest run",
    "test:cov": "vitest run --coverage",
    "e2e": "playwright test",
    "build": "nuxt build",
    "size": "size-limit",
    "audit": "pnpm audit --audit-level=high"
  }
}
```

**`.nvmrc`** = `24.20.0` · **`.node-version`** = `24.20.0`

**`.npmrc`** (exact pins, no silent engine skips)
```ini
save-exact=true
engine-strict=true
strict-peer-dependencies=true
```

**`nuxt.config.ts`** (turn every checker on; strict is opt-out here)
```ts
export default defineNuxtConfig({
  modules: ['@nuxt/eslint', '@nuxt/test-utils/module'], // add '@pinia/nuxt' here only together with pinned `pinia` + `@pinia/nuxt` dependencies (same major); never list a module that package.json does not pin
  eslint: { checker: true, config: { stylistic: false } },
  typescript: {
    typeCheck: true,
    strict: true,
    tsConfig: {
      compilerOptions: {
        noUncheckedIndexedAccess: true,
        exactOptionalPropertyTypes: true,
        noImplicitOverride: true,
        noFallthroughCasesInSwitch: true,
        noUnusedLocals: true,
        noUnusedParameters: true,
        verbatimModuleSyntax: true,
        isolatedModules: true
      }
    }
  }
})
```
> Do **not** hand-edit root `tsconfig.json`; Nuxt generates `.nuxt/tsconfig.app.json`, `.nuxt/tsconfig.server.json`, `.nuxt/tsconfig.shared.json`, `.nuxt/tsconfig.node.json` via project references. Extend only through `typescript.tsConfig`.

**`eslint.config.mjs`** (single flat config; Nuxt-aware, then hard-locked)
```js
import withNuxt from './.nuxt/eslint.config.mjs'
import vue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'
import vueA11y from 'eslint-plugin-vuejs-accessibility'
import prettier from 'eslint-config-prettier'

export default withNuxt(
  ...vue.configs['flat/recommended-error'],
  ...vueA11y.configs['flat/recommended'],
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  {
    files: ['**/*.{ts,vue}'],
    languageOptions: { parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname } },
    rules: {
      'vue/component-api-style': ['error', ['script-setup']],
      'vue/block-lang': ['error', { script: { lang: 'ts' } }],
      'vue/block-order': ['error', { order: ['script', 'template', 'style'] }],
      'vue/define-macros-order': ['error', { order: ['defineOptions', 'defineProps', 'defineEmits', 'defineSlots'] }],
      'vue/define-props-declaration': ['error', 'type-based'],
      'vue/define-emits-declaration': ['error', 'type-based'],
      'vue/no-import-compiler-macros': 'error',
      'vue/no-ref-as-operand': 'error',
      'vue/no-mutating-props': 'error',
      'vue/no-setup-props-reactivity-loss': 'error',
      'vue/no-watch-after-await': 'error',
      'vue/no-lifecycle-after-await': 'error',
      'vue/require-explicit-emits': 'error',
      'vue/multi-word-component-names': 'error',
      'nuxt/prefer-import-meta': 'error',
      'no-console': 'error',
      'no-restricted-globals': ['error', { name: 'fetch', message: 'Use useFetch/$fetch in Nuxt.' }],
      'no-restricted-imports': ['error', { paths: [{ name: 'axios', message: 'Banned: use useFetch/$fetch.' }] }],
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/no-unsafe-assignment': 'error'
    }
  },
  prettier
)
```

**`.prettierrc.json`** = `{ "semi": false, "singleQuote": true, "printWidth": 100, "vueIndentScriptAndStyle": false }` · **`.prettierignore`** = `node_modules`, `.nuxt`, `.output`, `dist`, `pnpm-lock.yaml`

**`knip.jsonc`** (Nuxt entry roots)
```jsonc
{
  "entry": ["nuxt.config.ts", "app/app.vue", "server/**/*.ts", "app/plugins/*.ts"],
  "project": ["**/*.{ts,vue}"],
  "ignoreExportsUsedInFile": true,
  "ignoreDependencies": ["@nuxt/test-utils", "@nuxt/eslint", "happy-dom"]
}
```

**`.dependency-cruiser.mjs`** (Nuxt layers / composables / components boundaries)
```js
export default {
  forbidden: [
    { name: 'no-circular', severity: 'error', from: {}, to: { circular: true } },
    { name: 'no-server-to-app', severity: 'error', from: { path: '^server/' }, to: { path: '^app/' } },
    { name: 'no-app-to-server', severity: 'error', from: { path: '^app/' }, to: { path: '^server/' } },
    { name: 'shared-is-leaf', severity: 'error', from: { path: '^shared/' }, to: { path: '^(app|server)/' } },
    { name: 'components-not-pages', severity: 'error', from: { path: '^app/components/' }, to: { path: '^app/pages/' } },
    { name: 'no-orphans', severity: 'warn', from: { orphan: true, pathNot: ['\\.(d|config|test|spec)\\.(ts|js)$'] }, to: {} }
  ],
  options: {
    tsConfig: { fileName: '.nuxt/tsconfig.app.json' },
    tsPreCompilationDeps: true,
    doNotFollow: { path: 'node_modules' },
    exclude: { path: '(node_modules|\\.output|\\.nuxt|coverage)' }
  }
}
```

**`vitest.config.ts`** (projects + coverage gate; Vitest 5 shape)
```ts
import { defineConfig } from 'vitest/config'
import { defineVitestProject } from '@nuxt/test-utils/config'

export default defineConfig({
  test: {
    projects: [
      { test: { name: 'unit', include: ['test/unit/**/*.{test,spec}.ts'], environment: 'node' } },
      await defineVitestProject({ test: { name: 'nuxt', include: ['test/nuxt/**/*.{test,spec}.ts'], environment: 'nuxt' } }),
      { test: { name: 'e2e', include: ['test/e2e/**/*.{test,spec}.ts'], environment: 'node' } }
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary'],
      include: ['app/**/*.{ts,vue}', 'shared/**/*.ts', 'server/**/*.ts'],
      exclude: ['**/*.d.ts', 'app/pages/**'],
      thresholds: { lines: 90, functions: 90, branches: 85, statements: 90, perFile: true }
    }
  }
})
```

**`playwright.config.ts`** — `testDir: './test/e2e-browser'`, `use: { baseURL: 'http://localhost:3000' }`, `webServer: { command: 'nuxt build && nuxt preview', url: 'http://localhost:3000', reuseExistingServer: !process.env.CI }`.

**`test/e2e-browser/hydration.spec.ts`** — attach `page.on('console', …)`, collect messages matching `/hydration|mismatch/i`, assert the array is empty.
**`test/e2e-browser/a11y.spec.ts`** — `new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()`; assert `violations.length === 0`.

**`.size-limit.json`**
```json
[
  { "name": "client entry", "path": ".output/public/_nuxt/entry-*.js", "limit": "180 kB", "gzip": true },
  { "name": "all client JS", "path": ".output/public/_nuxt/*.js", "limit": "450 kB" }
]
```

## Mandatory Gate Order

Fail-fast: cheapest/deterministic gates first, network/browser/build gates last. Run each line as one command; a non-zero exit stops the pipeline.

1. `corepack enable && pnpm install --frozen-lockfile`
2. `pnpm exec nuxt prepare`
3. `pnpm exec prettier --check .`
4. `pnpm exec eslint . --max-warnings 0 --report-unused-disable-directives`
5. `pnpm exec knip --strict`
6. `pnpm exec depcruise --config .dependency-cruiser.mjs app server shared`
7. `pnpm exec nuxt typecheck --checker vue-tsc`
8. `pnpm exec lockfile-lint --path pnpm-lock.yaml --type pnpm --allowed-hosts npm --validate-https`
9. `pnpm audit --audit-level=high`
10. `pnpm exec vitest run --coverage`
11. `pnpm exec playwright test`
12. `pnpm exec nuxt build`
13. `pnpm exec size-limit`
14. `pnpm exec nuxt analyze --no-serve`

Optional maintenance (not part of the blocking chain): `pnpm exec vitest doctor`, `pnpm exec ncu --format group` (`npm-check-updates@23.1.0`), `pnpm exec nuxt upgrade --channel stable`.

## Hallucination Traps to Block

| AI failure mode (stack-specific) | Check that catches it |
| --- | --- |
| Writes Options API (`export default { data() {} }`) | `vue/component-api-style: ['error',['script-setup']]` + `vue/no-deprecated-data-object-declaration` |
| Omits `lang="ts"` on `<script setup>` | `vue/block-lang` with `{ script: { lang: 'ts' } }` |
| Imports compiler macros (`import { defineProps } from 'vue'`) | `vue/no-import-compiler-macros` (new in eslint-plugin-vue v10) |
| Uses `count + 1` instead of `count.value` | `vue/no-ref-as-operand` |
| Mutates props (`props.x = …`) | `vue/no-mutating-props` |
| Destructures props and loses reactivity | `vue/no-setup-props-reactivity-loss` |
| `await` before registering `watch`/lifecycle hooks | `vue/no-watch-after-await` / `vue/no-lifecycle-after-await` |
| Uses `process.client` / `process.server` | `nuxt/prefer-import-meta` (`import.meta.client`) |
| Calls bare `fetch` or `axios` inside a component | `no-restricted-globals` (fetch) + `no-restricted-imports` (axios) |
| Any + unchecked promise drift | `@typescript-eslint/no-explicit-any`, `no-floating-promises`, `no-unsafe-assignment` via `strictTypeChecked` |
| Wall-clock / locale content rendered during SSR | Playwright hydration spec fails on `/mismatch/i` console output; use `NuxtTime`/`useState`/`useCookie` |
| Browser API (`localStorage`, `window`) read in `setup()` | Playwright hydration spec + `nuxt typecheck` (DOM lib absent on server context) |
| Missing/wrong auto-import (typo'd composable) | `nuxt prepare` + `nuxt typecheck` against `.nuxt/imports.d.ts` |
| Imports `server/` code into `app/`, or deep-imports a page from a component | `depcruise` rules `no-app-to-server`, `components-not-pages`, `shared-is-leaf` |
| Dead exports / unused deps / unused files accumulate | `knip --strict` |
| Lockfile resolves to a non-HTTPS or unexpected registry | `lockfile-lint --validate-https --allowed-hosts npm` |
| TypeScript 7 accidentally installed (e.g. `npm i -D typescript@latest`) | `nuxt typecheck` fails (`Cannot find module 'typescript/lib/tsc'`); `.npmrc save-exact` + pinned `6.0.3` prevents it |
| Writes old flag `eslint . --ext .ts,.vue` | Flat config ignores `--ext`; the script uses `eslint .` — `--ext` must never appear |
| Adds `.eslintrc.json` "for compatibility" | ESLint 10 errors; only `eslint.config.mjs` is honoured |
| Writes `nuxi upgrade --check` / `nuxt doctor` | Both flags/commands do not exist: `nuxt upgrade` has only `--channel`, and there is no `nuxt doctor` (use `vitest doctor`) |
| Uses Vitest 3-style `workspace` / `experimental.fsModuleCache` | Vitest 5 requires `test.projects` and top-level `fsModuleCache`; old keys are ignored → silent no-op |
| Scatters `new Date()` / `Intl` without explicit timeZone | Playwright hydration spec + review against the SKILL's `useDateTimeFormatter` rule |
| Over-budget client bundle sneaks in | `size-limit` exits non-zero when a budget is exceeded |

## Evidence to Record

Paste into the task's Verification Evidence block; include raw output and exit code (`echo $?`) for each.

| # | Command | Expected result | Exit |
| --- | --- | --- | --- |
| 1 | `node -v && pnpm -v` | `v24.20.0`, `12.5.1` | `0` |
| 2 | `pnpm install --frozen-lockfile` | "Lockfile is up to date"; no `ERR_PNPM_OUTDATED_LOCKFILE` | `0` |
| 3 | `pnpm exec lockfile-lint --path pnpm-lock.yaml --type pnpm --allowed-hosts npm --validate-https` | no violations printed | `0` |
| 4 | `pnpm audit --audit-level=high` | `No known vulnerabilities found` | `0` |
| 5 | `pnpm exec prettier --check .` | `All matched files use Prettier code style!` | `0` |
| 6 | `pnpm exec eslint . --max-warnings 0 --report-unused-disable-directives` | no output (zero errors, zero warnings) | `0` |
| 7 | `pnpm exec knip --strict` | no unused files/exports/deps | `0` |
| 8 | `pnpm exec depcruise --config .dependency-cruiser.mjs app server shared` | `no dependency violations found (N modules, M dependencies cruised)` | `0` |
| 9 | `pnpm exec nuxt typecheck --checker vue-tsc` | `Process exited with code 0`; no TS errors | `0` |
| 10 | `pnpm exec vitest run --coverage` | tests pass; `Coverage for lines/functions/branches/statements` all ≥ thresholds | `0` |
| 11 | `pnpm exec playwright test` | all specs pass, including 0 axe violations and 0 hydration messages | `0` |
| 12 | `pnpm exec nuxt build` | `✔ Client built` + `✔ Server built`; no type-check errors | `0` |
| 13 | `pnpm exec size-limit` | every budget `Size limit` line under its limit | `0` |
| 14 | `pnpm exec nuxt analyze --no-serve` | analysis JSON written; no build failure | `0` |
| 15 | `pnpm exec vue-tsc --version` | `3.3.11` (proves TS 6 engine, not TS 7) | `0` |

<!-- sources -->
- https://nuxt.com/docs/4.x/guide/concepts/code-style
- https://nuxt.com/docs/4.x/api/commands/typecheck
- https://nuxt.com/docs/4.x/api/commands/upgrade
- https://nuxt.com/docs/4.x/api/commands/analyze
- https://nuxt.com/docs/4.x/getting-started/testing
- https://nuxt.com/docs/4.x/guide/best-practices/hydration
- https://nuxt.com/docs/4.x/guide/best-practices/accessibility
- https://nuxt.com/docs/guide/concepts/typescript (Nuxt TypeScript concepts; project references, `typescript.typeCheck`, strict default)
- https://eslint.nuxt.com/packages/module
- https://eslint.nuxt.com/packages/config
- https://eslint.nuxtjs.org.cn/packages/plugin (`nuxt/prefer-import-meta`)
- https://eslint.vuejs.org/user-guide/
- https://eslint.vuejs.org/rules/
- https://newreleases.io/project/npm/eslint-plugin-vue/release/10.0.0
- https://eslint.org/docs/latest/use/migrate-to-10.0.0
- https://eslint.org/blog/2026/02/eslint-v10.0.0-released/
- https://typescript-eslint.io/getting-started/typed-linting
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- https://github.com/vuejs/language-tools/issues/6156
- https://github.com/vuejs/language-tools/discussions/6121
- https://golar.dev/modes/typecheck/
- https://github.com/NikhilVerma/vue-tsgo
- https://vitest.dev/blog/vitest-5.html
- https://vitest.dev/guide/cli
- https://vitest.dev/config/coverage
- https://github.com/sverweij/dependency-cruiser
- https://github.com/sverweij/dependency-cruiser/blob/main/doc/options-reference.md
- https://knip.dev/
- https://github.com/vuejs/tsconfig
- https://github.com/nuxt/a11y
- https://github.com/chaance/vitest-axe
- https://github.com/snyk-labs/lockfile-lint
- https://vue-a11y.github.io/eslint-plugin-vuejs-accessibility/
- https://unpkg.com/eslint-plugin-vuejs-accessibility@2.6.0/dist/index.js (verified `configs['flat/recommended']`)
- https://nodejs.org/dist/index.json (Node LTS "Krypton" v24.20.0)
- registry.npmjs.org package metadata for: nuxt, vue, eslint, eslint-plugin-vue, typescript-eslint, vue-tsc, typescript, @nuxt/eslint, vitest, @nuxt/test-utils, @vue/test-utils, prettier, knip, dependency-cruiser, @vitest/coverage-v8, @playwright/test, @axe-core/playwright, vitest-axe, size-limit, nuxi, eslint-plugin-vuejs-accessibility, typescript-native-bridge, golar, ts-prune, depcheck, pnpm

## Currency Baseline

- **Nuxt 4 (current major):** Scaffold with the `app/` directory layout (`app/components`, `app/pages`) and shared types in `shared/`; Nuxt 3 is end-of-life, so do not pin new work to v3 conventions.
