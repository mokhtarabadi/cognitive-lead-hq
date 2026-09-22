---
name: react-native-expo
description: Expo Managed Workflow, Expo Router, NativeWind, and Strict TypeScript for zero-hallucination cross-platform apps.
---

# React Native (Expo) — AI-Native Scaffolding

## AI Context & Token Optimization (Zero-Hallucination Rules)

1. **Expo Managed Workflow ONLY:** You are strictly BANNED from modifying `ios/` or `android/` native folders, `Podfile`, or `build.gradle`. Native configuration causes massive AI hallucinations. Use Expo Config plugins instead.
2. **Strict TypeScript:** Pure JavaScript is banned. All components, props, and API responses must be strongly typed.
3. **Expo Router:** Use file-based routing (`app/`). It drastically reduces navigation boilerplate.
4. **NativeWind:** Use NativeWind (Tailwind for RN) over `StyleSheet.create`. It reduces line count and token usage significantly.

## Project Structure

```text
project/
├── app/                 # Expo Router file-based routing
│   ├── (auth)/          # Authentication flow
│   ├── (tabs)/          # Tab bar layout
│   └── _layout.tsx      # Root layout / Providers
├── components/          # Reusable UI components
├── constants/           # Colors, Layout dimensions, Config
├── hooks/               # Custom React hooks
├── services/            # API clients and external services
├── store/               # Global state (Zustand)
└── assets/              # Images, fonts
```

## Naming Conventions

- **Components**: `PascalCase` (e.g., `PrimaryButton.tsx`)
- **Hooks**: `camelCase` starting with `use` (e.g., `useColorScheme.ts`)
- **Routes**: `kebab-case` or exact URL match.

## Architectural Patterns

- **Expo Router**: Use the `app/` directory for routing. Use `<Link>` from `expo-router`.
- **Styling**: NativeWind is mandatory. Keep styles inline as utility classes.
- **State**: Use `Zustand`. Avoid Redux.
- **Safe Areas**: Wrap top-level screen views in `SafeAreaView` from `react-native-safe-area-context`.

## Universal DateTime Governance

- **API Boundary:** All datetime values received from the backend are epoch ms or ISO-8601 UTC strings. Normalize to epoch ms immediately upon receipt.
- **Client Display:** Format for the user's locale using `Intl.DateTimeFormat` with `timeZone` from `expo-localization`. Never hardcode a timezone.
- **State:** Store timestamps as epoch ms (number) in Zustand stores. Only convert to localized strings in component render functions.
- **Offline Queue:** Timestamps in offline mutation queues must be epoch ms to avoid timezone dependency when the device's locale changes.

## Testing Strategies

- **Framework**: `Jest` + `@testing-library/react-native`.
- **Approach**: Test component rendering and user interactions natively.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

Scope: Expo **managed workflow** (CNG, no committed `ios/`/`android/`), **Expo Router**, **NativeWind**, **Strict TypeScript**. Verified against live npm registry dist-tags, GitHub releases, and Expo docs on **2026-09-21**. Baseline SDK: **Expo SDK 57** (`expo@57.0.24`, `react-native@0.86.3`, `react@19.2.3`).

> Version truth source of record: `expo/bundledNativeModules.json` on branch `sdk-57`. Any native package version NOT from `npx expo install` is drift.

## Required Toolchain

| Tool | Purpose | Minimum version to pin | Install / availability note |
| --- | --- | --- | --- |
| Node.js | Runtime (LTS "Krypton") | `24.21.0` | `nodejs.org/dist`; `.nvmrc` + `engines.node`. Do NOT use 20.x (ESLint 10/RNTL 14/dep-cruiser reject it). |
| npm | Package manager + lockfile | `12.0.2` | `npm -v`; `packageManager` field + corepack. Requires Node `^22.22.2 || ^24.15.0 || >=26`. |
| expo | SDK pin (exact) | `57.0.24` | `npx expo install expo@57.0.24` — pin exact, not `^`. |
| react-native | RN runtime | `0.86.3` | SDK 57 pin (npm `latest` is `0.87.1` — DRIFT). `npx expo install react-native`. |
| react / react-dom | UI runtime | `19.2.3` | SDK 57 pin (npm `latest` is `19.3.0` — DRIFT). |
| @types/react | React types | `19.2.2` | Template pin `~19.2.2`; do not float to `19.3.x`. |
| typescript | Type-check API for lint tooling | alias `npm:@typescript/typescript6@^6.0.0` (`6.0.2`) | typescript-eslint peer is `>=4.8.4 <6.1.0`; Expo template pins `~6.0.3`. |
| typescript-7 | Fast native `tsc` (Go) | alias `npm:typescript@^7.0.2` | Provides the `tsc` binary; `typescript` alias provides the 6.x API. TS 7 stable programmatic API lands in 7.1. |
| prettier | Formatter | `3.9.8` | `npx prettier@3.9.8 --version`. Reject `4.0.0-alpha`. |
| prettier-plugin-tailwindcss | NativeWind class sorting | `0.5.14` | NativeWind 4 (Tailwind 3) requires `^0.5.11`; `0.8.x` targets Tailwind 4 — mismatch. |
| eslint | Linter | `9.39.5` | `eslint-config-expo@57.0.2` devDep is `^9.18.0`; bundled plugins peer-cap at `^9`. |
| eslint-config-expo | Expo flat config | `57.0.2` | `npx expo lint` scaffolds it; import path `eslint-config-expo/flat`. |
| typescript-eslint | Typed lint rules | `8.70.1` | `strictTypeChecked`; peer `eslint ^8.57||^9||^10`, `typescript >=4.8.4 <6.1.0`. |
| eslint-plugin-react-hooks | Hook + React Compiler rules | `7.1.1` | Ships in `eslint-config-expo`; compiler rules on by default since SDK 55. |
| eslint-plugin-react-native | RN correctness rules | `5.0.0` | peer `eslint ^3..^9`. |
| eslint-plugin-react-native-a11y | RN accessibility | `3.5.1` | Only maintained option; peer range stops at `^8` (verify at install). |
| eslint-plugin-jsx-a11y | Web/RN-web a11y | `6.10.2` | peer up to `^9`. |
| eslint-config-prettier | Disable formatting rules in ESLint | `10.1.8` | Run Prettier separately; never `eslint-plugin-prettier`. |
| dependency-cruiser | Architecture / import-boundary graph | `18.4.0` | engines `^22||^24||>=26`. |
| knip | Dead code + unused deps/exports | `6.37.0` | `knip --strict` implies `--production`. |
| expo-doctor | Project health | `1.20.4` | `npx expo-doctor@latest`. |
| eas-cli | Build/release config validation | `24.7.0` | `npm i -g eas-cli@24.7.0` or `npx eas-cli@24.7.0`. |
| lockfile-lint | Lockfile host/scheme integrity | `5.0.1` | Supports npm + yarn lockfiles ONLY (not `pnpm-lock.yaml`). |
| audit-ci | CI vuln gate with allowlist | `7.1.0` | Wraps `npm audit`; exit non-zero on high/critical. |
| @lavamoat/allow-scripts | Install-script allowlist | `5.1.0` | Optional; pairs with `.npmrc` `ignore-scripts=true`. |
| jest | Test runner | `29.7.0` | `jest-expo@57.0.5` internally targets Jest 29; RNTL 14 accepts `>=29`. |
| jest-expo | RN Jest preset | `57.0.5` | `preset: "jest-expo"`; peers `@react-native/jest-preset@^0.86.3`. |
| @testing-library/react-native | Component tests | `14.0.1` | peer `test-renderer@^1.0.0`; matchers built-in (no `@testing-library/jest-native`). |
| test-renderer | Renderer peer for RNTL 14 | `1.3.0` | `react-test-renderer` is deprecated; install `test-renderer`. |
| eslint-plugin-testing-library | Test lint rules | `7.16.2` | peer `eslint ^8.57||^9||^10`. |
| eslint-plugin-jest | Jest lint rules | `29.16.6` | peer `eslint ^8.57||^9||^10`. |
| maestro | E2E (Expo-preferred) | `2.10.0` | Installer `curl -Ls "https://get.maestro.mobile.dev" \| bash`; NOT the npm `maestro` package. |
| expo-atlas | Bundle composition | `0.4.3` | `EXPO_ATLAS=true npx expo export`. |
| nativewind | Styling | `4.2.7` | v4.2.7 adds SDK 57 support; v5 is `5.0.0-rc.0` — do NOT ship RC. |
| tailwindcss | NativeWind engine | `3.4.19` | NativeWind 4 = Tailwind 3 (`v3-lts`); Tailwind 4 is for NativeWind 5. |
| react-native-css-interop | NativeWind runtime | `0.2.7` | Pulled by `nativewind@4.2.7`. |
| babel-preset-expo | Babel preset | `57.0.12` | SDK 57 pin. |
| react-native-safe-area-context | Safe areas | `5.7.0` | SDK pin is `~5.7.0` (npm `latest` is `5.10.0` — DRIFT). |
| zustand | State (per SKILL.md) | `5.0.15` | Peer-agnostic. |

## Strict Baseline Config

Create exactly these files. Every strictness switch is named.

- **`.nvmrc`** → `24.21.0`
- **`.node-version`** → `24.21.0`
- **`package.json`** →
  - `"packageManager": "npm@12.0.2"`
  - `"engines": { "node": ">=24.21.0 <25" }`
  - `"main": "expo-router/entry"` (Expo Router entry — never `index.js`)
  - `"scripts"`: `"lint": "eslint . --max-warnings=0"`, `"typecheck": "tsc --noEmit"`, `"format": "prettier --check ."`, `"arch": "depcruise --config .dependency-cruiser.cjs --output-type err app components hooks services store"`, `"deadcode": "knip --strict --reporter compact --no-progress"`, `"test": "jest --ci --coverage --runInBand"`, `"gate": "npm run format && npm run lint && npm run typecheck && npm run arch && npm run deadcode && npm run test"`
- **`.npmrc`** → `engine-strict=true`, `save-exact=true`, `ignore-scripts=true`, `audit-level=high`, `fund=false`
- **`tsconfig.json`** →
  ```json
  {
    "extends": "expo/tsconfig.base",
    "compilerOptions": {
      "strict": true,
      "noUncheckedIndexedAccess": true,
      "exactOptionalPropertyTypes": true,
      "noImplicitOverride": true,
      "noImplicitReturns": true,
      "noFallthroughCasesInSwitch": true,
      "noUnusedLocals": true,
      "noUnusedParameters": true,
      "noPropertyAccessFromIndexSignature": true,
      "useUnknownInCatchVariables": true,
      "noUncheckedSideEffectImports": true,
      "allowUnreachableCode": false,
      "allowUnusedLabels": false,
      "forceConsistentCasingInFileNames": true,
      "verbatimModuleSyntax": true,
      "isolatedModules": true,
      "moduleDetection": "force",
      "skipLibCheck": true,
      "types": ["jest", "node"]
    },
    "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts", "nativewind-env.d.ts"]
  }
  ```
  TS 7 hard requirements: `types` now defaults to `[]` (must list `jest`,`node`); `rootDir` defaults to `./`; `strict` is `true` by default; `target: "es5"` and `downlevelIteration` are hard errors.
- **`eslint.config.js`** (flat config, CommonJS) →
  - `const expoConfig = require('eslint-config-expo/flat');` + `const { defineConfig, globalIgnores } = require('eslint/config');`
  - `const tseslint = require('typescript-eslint');`
  - `module.exports = defineConfig([ globalIgnores(['dist/*','.expo/*','ios/*','android/*','coverage/*']), expoConfig, ...tseslint.configs.strictTypeChecked, ...tseslint.configs.stylisticTypeChecked, { linterOptions: { reportUnusedDisableDirectives: 'error' }, rules: { 'import/no-cycle': ['error', { maxDepth: Infinity }], 'react-hooks/react-compiler': 'error' } }, eslintConfigPrettier ]);`
  - `parserOptions.projectService: true` for typed rules (via tseslint).
- **`prettier.config.mjs`** → `{ singleQuote: true, trailingComma: 'all', printWidth: 100, semi: true, plugins: ['prettier-plugin-tailwindcss'], tailwindConfig: './tailwind.config.js' }`
- **`.prettierignore`** → `node_modules`, `ios`, `android`, `.expo`, `dist`, `coverage`, `package-lock.json`
- **`.dependency-cruiser.cjs`** → `forbidden` rules: `no-circular` (`severity: error`), `no-orphans`, and layer zones (`app` may import `components/hooks/services/store`; `components` may import `hooks` but NOT `services/store`; `services` must not import `app/components`). Enable `options.tsConfig.fileName: 'tsconfig.json'`.
- **`knip.json`** → `{ "entry": ["app/**/*.{ts,tsx}!", "expo-env.d.ts"], "project": ["**/*.{ts,tsx}!", "!ios/**!", "!android/**!"], "ignoreDependencies": ["@types/*", "eslint-config-expo", "prettier-plugin-tailwindcss"] }`
- **`jest.config.js`** →
  ```js
  module.exports = {
    preset: 'jest-expo',
    testMatch: ['**/*.test.{ts,tsx}'],
    collectCoverageFrom: ['app/**/*.{ts,tsx}', 'components/**/*.{ts,tsx}', 'hooks/**/*.{ts,tsx}', 'services/**/*.{ts,tsx}', '!**/*.d.ts'],
    coverageThreshold: { global: { branches: 80, functions: 80, lines: 80, statements: 80 } },
    coverageReporters: ['text-summary', 'lcov'],
    transformIgnorePatterns: ['node_modules/(?!(?:.pnpm/)?((jest-)?react-native|@react-native(-community)?|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|nativewind|react-native-css-interop|@sentry/react-native|react-native-svg))']
  };
  ```
  Do NOT add `passWithNoTests` — an empty suite must fail.
- **`app.json`** (or `app.config.ts`) → `expo.scheme` (required by Expo Router), `expo.experiments.typedRoutes: true`, `expo.experiments.reactCompiler: true`, `expo.newArchEnabled: true` (Legacy Architecture removed in SDK 55). Validate with `npx expo config`.
- **`eas.json`** → `build.development.developmentClient: true`, `build.preview.distribution: "internal"`, `build.production.autoIncrement: true`. No `releaseChannel` (removed — use `channel`).
- **`babel.config.js`** → `presets: [['babel-preset-expo', { jsxImportSource: 'nativewind' }], 'nativewind/babel']` (NativeWind 4 order).
- **`metro.config.js`** → `withNativeWind(config, { input: './global.css' })`.
- **`tailwind.config.js`** → `content: ['./app/**/*.{ts,tsx}','./components/**/*.{ts,tsx}']`, `presets: [require('nativewind/preset')]`.
- **`nativewind-env.d.ts`** → `/// <reference types="nativewind/types" />`
- **`.maestro/`** → flow YAML files; `maestro test .maestro/`.
- **`.gitignore`** → `ios/`, `android/`, `.expo/`, `dist/`, `coverage/`, `node_modules/`.

## Mandatory Gate Order

Fail-fast: each step must exit `0` before the next runs.

1. `node -e "if(process.versions.node!=='24.21.0'){console.error('node '+process.versions.node);process.exit(1)}"` — runtime pin
2. `npm ci` — frozen lockfile install (`engine-strict=true` enforces Node; `ignore-scripts=true` blocks install scripts)
3. `CI=1 npx expo install --check` — every native package matches the SDK 57 map; exits non-zero in CI on drift
4. `npx expo-doctor@latest` — app config, package.json, CNG, New Architecture health
5. `npx prettier --check .` — formatting is canonical
6. `npx eslint . --max-warnings=0` — typed lint, hook/compiler rules, a11y, `import/no-cycle`, zero warnings tolerated
7. `npx tsc --noEmit` — strict type check (TS 7 binary from the `typescript-7` alias)
8. `npx depcruise --config .dependency-cruiser.cjs --output-type err app components hooks services store` — layer boundaries + no cycles
9. `npx knip --strict --reporter compact --no-progress` — dead files/exports + unused/unlisted dependencies
10. `npx jest --ci --coverage --runInBand` — unit tests with enforced `coverageThreshold` (80% global)
11. `npx lockfile-lint --path package-lock.json --type npm --validate-https --allowed-hosts npm` — no non-registry hosts / plain-http resolutions
12. `npx audit-ci --high` (and `npm audit signatures`) — no high/critical vulns; registry provenance verified
13. `npx expo config --type public --json > /dev/null` then `npx eas-cli@24.7.0 config -p android -e production --json --non-interactive > /dev/null` — app config schema + `eas.json` schema
14. `npx expo export --platform all --output-dir dist` — production bundle must build; then `EXPO_ATLAS=true npx expo export` for size attribution
15. `maestro test .maestro/` — E2E on a booted simulator/emulator (CI lane only)

## Hallucination Traps to Block

| AI failure mode (very common) | Check that catches it |
| --- | --- |
| Pins `react-native@0.87.1` / `react-native@latest` (npm latest) instead of SDK 57's `0.86.3` | Step 3 `CI=1 npx expo install --check` |
| Pins `react@19.3.0` / `@types/react@19.3.0` instead of `19.2.3` / `~19.2.2` | Step 3 + Step 7 |
| Pins `react-native-safe-area-context@5.10.0`, `reanimated@4.7.0`, `worklets@0.13.0` (npm latest) instead of SDK pins `~5.7.0`, `4.5.1`, `0.10.1` | Step 3 |
| Installs `typescript@7.0.2` as `typescript` → typescript-eslint peer `>=4.8.4 <6.1.0` breaks | `npm ls typescript`; Step 6 fails to load typed config |
| TS 7 `types` defaults to `[]` → `jest`/`node` globals undefined | Step 7 (`Cannot find name 'describe'`) |
| Writes `target: "es5"` or `downlevelIteration` in tsconfig (removed in TS 7) | Step 7 hard error |
| Writes legacy `.eslintrc.json` / `ESLINT_USE_FLAT_CONFIG` instead of `eslint.config.js` | Step 6; `npx eslint --print-config app/index.tsx` |
| Imports `eslint-config-expo` (legacy) instead of `eslint-config-expo/flat` | Step 6 config resolution error |
| Adds `eslint-plugin-prettier` / `prettier/prettier` rule (deprecated pattern) | Step 5 (Prettier is the single formatter) + Step 6 |
| Pins `prettier-plugin-tailwindcss@0.8.1` with NativeWind 4 / Tailwind 3 | Step 5 plugin error; pin `0.5.14` |
| Installs `nativewind@5.0.0-rc.0` (RC) or `react-native-css` v3 | Step 3 / Step 14 build failure; pin `nativewind@4.2.7` |
| Uses `react-native-testing-library` (renamed/archived name) or `@testing-library/jest-native` (deprecated matchers) | `npm ls`; Step 10 import error |
| RNTL 14 without the `test-renderer@^1.0.0` peer (installs `react-test-renderer` instead) | Step 10 render failure |
| Recommends `ts-prune` / `depcheck` / `unimported` for dead code | Step 9 is `knip --strict`; `npm ls ts-prune depcheck` must be empty |
| Runs `expo build` / `expo publish` / global `expo-cli` (all removed) | `npx expo --help`; only `eas build` / `eas update` exist |
| Runs `npx expo prebuild` expecting an incremental native update — SDK 57 **cleans by default** | `EXPO_NO_GIT_STATUS=1`; use `npx expo prebuild --no-clean` intentionally |
| `main` set to `index.js` instead of `expo-router/entry` | Step 4 expo-doctor + Step 14 export |
| Missing `expo.scheme` (Expo Router deep links) | Step 4 expo-doctor |
| `experiments.typedRoutes` on but `.expo/types/router.d.ts` never generated in CI → `tsc` include glob misses | Step 7 must run AFTER a generation command (`npx expo start`/`npx expo export`); or the include resolves empty |
| `jest` preset `"react-native"` instead of `"jest-expo"` | Step 10 transform failures on Expo modules |
| No `coverageThreshold` → gate passes with zero tests | Step 10 (threshold breach exits non-zero) |
| `--passWithNoTests` added to silence empty suites | Step 10 flag audit; remove it |
| `eas.json` uses removed `releaseChannel` instead of `channel` | Step 13 `eas config` validation |
| `newArchEnabled: false` / third-party module without New Architecture support (Legacy removed in SDK 55) | Step 4 expo-doctor |
| Imports native code by editing `ios/`/`android/` or `Podfile` (banned by SKILL.md) | Step 8 (native dirs not in graph) + Step 4 CNG check |
| Recommends `vitest` for RN unit tests (no official Metro/RN preset) | Step 10 uses `jest-expo`; `npm ls vitest` must be empty |
| Recommends Detox for E2E (no Expo-official support, heavy native config) | Step 15 uses Maestro |

## Evidence to Record

Paste into the task's Verification Evidence block: exact command, observed result, exit code.

| # | Command | Expected result | Exit code |
| --- | --- | --- | --- |
| 1 | `node -v` | `v24.21.0` | `0` |
| 2 | `npm ci` | `added N packages` and no `ERESOLVE`/`EBADENGINE` | `0` |
| 3 | `CI=1 npx expo install --check` | `Dependencies are up to date` (no version list) | `0` |
| 4 | `npx expo-doctor@latest` | `No issues detected` | `0` |
| 5 | `npx prettier --check .` | `All matched files use Prettier code style!` | `0` |
| 6 | `npx eslint . --max-warnings=0` | no output | `0` |
| 7 | `npx tsc --noEmit` | no output; `npx tsc --version` → `Version 7.0.2` | `0` |
| 8 | `npx depcruise --config .dependency-cruiser.cjs --output-type err app components hooks services store` | `no dependency violations found (N modules, M dependencies cruised)` | `0` |
| 9 | `npx knip --strict --reporter compact --no-progress` | `✂️ Excellent, Knip found no issues.` | `0` |
| 10 | `npx jest --ci --coverage --runInBand` | `Tests: N passed` and `Jest: "global" coverage threshold for branches (80%) met` | `0` |
| 11 | `npx lockfile-lint --path package-lock.json --type npm --validate-https --allowed-hosts npm` | `validating... no issues detected` | `0` |
| 12 | `npx audit-ci --high` | `Passed audit`; `npm audit signatures` → `verified N packages` | `0` |
| 13 | `npx expo config --type public --json > /dev/null && npx eas-cli@24.7.0 config -p android -e production --json --non-interactive > /dev/null` | valid JSON, no schema errors | `0` |
| 14 | `npx expo export --platform all --output-dir dist` | `Exported: dist`; record `du -sh dist` byte delta | `0` |
| 15 | `maestro test .maestro/` | `Flow Passed` for every flow | `0` |

<!-- sources -->
- https://registry.npmjs.org/-/package/expo/dist-tags
- https://registry.npmjs.org/-/package/react-native/dist-tags
- https://registry.npmjs.org/-/package/react/dist-tags
- https://registry.npmjs.org/-/package/@types/react/dist-tags
- https://registry.npmjs.org/-/package/typescript/dist-tags
- https://registry.npmjs.org/-/package/@typescript/typescript6/dist-tags
- https://registry.npmjs.org/-/package/eslint/dist-tags
- https://registry.npmjs.org/-/package/eslint-config-expo/dist-tags
- https://registry.npmjs.org/-/package/typescript-eslint/dist-tags
- https://registry.npmjs.org/-/package/prettier/dist-tags
- https://registry.npmjs.org/-/package/prettier-plugin-tailwindcss/dist-tags
- https://registry.npmjs.org/-/package/jest/dist-tags
- https://registry.npmjs.org/-/package/jest-expo/dist-tags
- https://registry.npmjs.org/-/package/@testing-library/react-native/dist-tags
- https://registry.npmjs.org/-/package/test-renderer/dist-tags
- https://registry.npmjs.org/-/package/@testing-library/jest-native/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-react-hooks/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-react-native/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-react-native-a11y/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-jsx-a11y/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-import/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-import-x/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-boundaries/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-testing-library/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-jest/dist-tags
- https://registry.npmjs.org/-/package/eslint-config-prettier/dist-tags
- https://registry.npmjs.org/-/package/dependency-cruiser/dist-tags
- https://registry.npmjs.org/-/package/knip/dist-tags
- https://registry.npmjs.org/-/package/depcheck/dist-tags
- https://registry.npmjs.org/-/package/ts-prune/dist-tags
- https://registry.npmjs.org/-/package/expo-doctor/dist-tags
- https://registry.npmjs.org/-/package/eas-cli/dist-tags
- https://registry.npmjs.org/-/package/expo-atlas/dist-tags
- https://registry.npmjs.org/-/package/lockfile-lint/dist-tags
- https://registry.npmjs.org/-/package/audit-ci/dist-tags
- https://registry.npmjs.org/-/package/@lavamoat/allow-scripts/dist-tags
- https://registry.npmjs.org/-/package/sherif/dist-tags
- https://registry.npmjs.org/-/package/syncpack/dist-tags
- https://registry.npmjs.org/-/package/nativewind/dist-tags
- https://registry.npmjs.org/-/package/tailwindcss/dist-tags
- https://registry.npmjs.org/-/package/react-native-css-interop/dist-tags
- https://registry.npmjs.org/-/package/babel-preset-expo/dist-tags
- https://registry.npmjs.org/-/package/vitest/dist-tags
- https://registry.npmjs.org/-/package/oxlint/dist-tags
- https://registry.npmjs.org/-/package/@biomejs/biome/dist-tags
- https://registry.npmjs.org/-/package/pnpm/dist-tags
- https://registry.npmjs.org/-/package/npm/dist-tags
- https://registry.npmjs.org/-/package/bun/dist-tags
- https://registry.npmjs.org/-/package/detox/dist-tags
- https://registry.npmjs.org/-/package/eslint-plugin-expo/dist-tags
- https://registry.npmjs.org/-/package/babel-plugin-react-compiler/dist-tags
- https://registry.npmjs.org/-/package/react-compiler-healthcheck/dist-tags
- https://registry.npmjs.org/expo/latest
- https://registry.npmjs.org/eslint-config-expo/57.0.2
- https://registry.npmjs.org/typescript-eslint/latest
- https://registry.npmjs.org/@typescript-eslint%2Feslint-plugin/8.70.1
- https://registry.npmjs.org/eslint-plugin-import/2.32.0
- https://registry.npmjs.org/eslint-plugin-react/latest
- https://registry.npmjs.org/@testing-library/react-native/14.0.1
- https://registry.npmjs.org/jest-expo/57.0.5
- https://registry.npmjs.org/expo-template-default/latest
- https://registry.npmjs.org/expo-template-default/57.0.26
- https://raw.githubusercontent.com/expo/expo/sdk-57/packages/expo/bundledNativeModules.json
- https://raw.githubusercontent.com/expo/expo/sdk-57/packages/eslint-config-expo/package.json
- https://docs.expo.dev/more/expo-cli.md
- https://docs.expo.dev/guides/using-eslint.md
- https://docs.expo.dev/guides/typescript.md
- https://docs.expo.dev/develop/unit-testing.md
- https://docs.expo.dev/develop/tools.md
- https://docs.expo.dev/build/eas-json.md
- https://docs.expo.dev/eas/cli.md
- https://docs.expo.dev/guides/react-compiler.md
- https://docs.expo.dev/guides/analyzing-bundles.md
- https://docs.expo.dev/router/reference/typed-routes.md
- https://docs.expo.dev/tutorial/cicd/e2e-tests.md
- https://expo.dev/changelog/sdk-57
- https://eslint.org/docs/latest/use/migrate-to-10.0.0
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-rc/
- https://www.nativewind.dev/docs/getting-started/installation
- https://knip.dev/features/production-mode
- https://raw.githubusercontent.com/sverweij/dependency-cruiser/main/doc/cli.md
- https://raw.githubusercontent.com/lirantal/lockfile-lint/master/packages/lockfile-lint/README.md
- https://github.com/mobile-dev-inc/maestro/releases.atom
- https://nodejs.org/dist/index.json

## Currency Baseline

- **New Architecture default:** Target the React Native New Architecture (Fabric/TurboModules), default in current Expo SDKs; verify third-party native modules support it (or ship a config plugin) before adopting.
