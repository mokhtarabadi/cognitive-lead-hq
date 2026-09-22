---
name: nextjs
description: App Router, Server/Client Components, Server Actions, and Tailwind tokens for Next.js
---

# Next.js — Best Practices & AI-Driven Scaffolding

## AI Context & Token Optimization

1. **Server Actions First:** Always use Server Actions (`"use server"`) instead of manual API routes for mutations. This keeps the AI's context localized to the component/action pair, eliminating network fetching boilerplate.
2. **Strict Server/Client Boundaries:** Mark client components explicitly (`"use client"`). Keep them as leaf nodes to prevent passing complex state across the network boundary, which confuses the AI.
3. **Tailwind Design Tokens:** Never use arbitrary values (`h-[13px]`). Rely on predefined `tailwind.config.ts` tokens to ensure visual consistency across AI generations.

## Modern Next.js App Router Architecture

Scaffold Next.js single-page or hybrid apps using these principles:

1. **App Router App Layout:** Use file-based nested routing in the `app/` directory (`layout.tsx`, `page.tsx`).
2. **Strict Server/Client Boundaries:**
   - Components are Server Components by default. Fetch data, access databases, and handle security here.
   - Client Components must be annotated with `"use client"` at the top. Use them only for user interactivity (hooks, event handlers, local states). Keep them at leaf-level.
3. **Server Actions for Mutations:** Always handle form submissions and database mutations using Server Actions with the `"use server"` directive. Banned: setting up custom API routes for simple form handling.
4. **Tailwind Token System:** Never use arbitrary Tailwind classes (like `h-[12px]`) or inline styles. Declare custom scales CSS-first via `@theme` (Tailwind v4) and refer to them.
5. **A11y Semantic HTML:** Always enforce standard landmarks (`<header>`, `<main>`, `<footer/>`) and `next/image` alt tags.

## Project Structure

```
src/
├── app/                        # App Router (Next.js 13+)
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── (auth)/                 # Route group: auth pages
│   │   ├── login/
│   │   │   ├── page.tsx
│   │   │   └── login-form.tsx  # Client component
│   │   └── register/
│   │       └── page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx          # Dashboard-specific layout
│   │   ├── page.tsx
│   │   └── settings/
│   │       └── page.tsx
│   └── api/                    # API route handlers (if needed)
│       └── users/
│           └── route.ts
├── components/                 # Shared components
│   ├── ui/                     # Primitive UI components (Button, Input)
│   └── features/               # Feature-specific components
│       └── auth/
│           └── AuthGuard.tsx
├── lib/                        # Shared utilities, API clients, DB
│   ├── db.ts
│   └── utils.ts
├── actions/                    # Server Actions
│   └── auth.actions.ts
└── styles/
    └── globals.css             # Tailwind directives & custom CSS
```

## Naming Conventions

| Artifact               | Convention                               | Example                     |
| ---------------------- | ---------------------------------------- | --------------------------- |
| Directories (routes)   | `kebab-case`                             | `/user-settings/`           |
| Components             | `PascalCase`                             | `UserAvatar.tsx`            |
| Utilities / libs       | `camelCase`                              | `formatDate.ts`             |
| Server Actions         | `kebab-case` with `.action` suffix       | `auth.actions.ts`           |
| CSS classes            | Tailwind utility classes (prefer inline) | `"flex items-center gap-2"` |
| Tailwind custom tokens | `kebab-case` in `tailwind.config`        | `brand-primary`             |

## Architectural Patterns

### App Router (`app/` Directory)

- Always use the `app/` directory. The legacy `pages/` directory is deprecated.
- Use **route groups** `(group-name)` to organize routes without affecting the URL path.
- Each route segment gets its own `page.tsx` (and optionally `layout.tsx`, `loading.tsx`, `error.tsx`).

### Strict Server / Client Component Separation

- **Server Components** (default in the App Router): Fetch data, access databases, read tokens. No state, no effects, no browser APIs.
- **Client Components**: Add interactivity. Mark the file with `"use client"` at the top. Keep them as leaf components — do not fetch data directly; receive it as props from a parent server component.

```
Server Component (fetches data) → passes data as props → Client Component (renders + interactivity)
```

### Server Actions for Mutations

- Define mutations as Server Actions in `src/actions/`.
- Use `"use server"` at the top of the action file (or inline with `"use server"` in a function).
- Server Actions eliminate the need for manual API routes for form submissions.
- Use `useActionState` for progressive enhancement (`useFormState` is deprecated since React 19).

### Tailwind UI Tokens

- Define design tokens (colors, spacing, fonts) CSS-first via `@theme` (Tailwind v4) — do not use raw CSS values.
- Use the official Tailwind CSS classes exclusively; avoid inline `style` props unless dynamic values are required.

### Accessible (a11y) Component Structure

- Every interactive element must have an accessible name (visible label, `aria-label`, or `aria-labelledby`).
- Use semantic HTML (`<nav>`, `<main>`, `<button>`, `<a>`) instead of `<div>` soup.
- All form inputs must have an associated `<label>` or `aria-label`.
- Use `next/image` for images (provides `alt` enforcement).
- Run `@axe-core/react` or the Lighthouse a11y audit on every page.

## Universal DateTime Governance

- **Server Actions / API Routes:** Process all datetimes in UTC. Use `dayjs.utc()` for parsing. Never rely on the server's local timezone.
- **Client Components:** Receive epoch ms or ISO-8601 UTC strings as props from Server Components. Format for display using `Intl.DateTimeFormat` with an explicit `timeZone` option in a `useFormatter()` hook.
- **Database (Prisma):** Use `DateTime` with `@db.Timestamptz()`. Store as UTC. Query with UTC `Date` objects only.
- **Clock Injection (Server):** In Server Actions, use a `ClockProvider` service wrapping `new Date()` for testability. Never hardcode `new Date()` in mutation logic.

## Testing Strategies

| Layer             | Test Type   | Framework                | File Naming            |
| ----------------- | ----------- | ------------------------ | ---------------------- |
| Utility functions | Unit        | Vitest                   | `utils.test.ts`        |
| Client components | Component   | Vitest + Testing Library | `UserAvatar.test.tsx`  |
| Server Actions    | Integration | Vitest                   | `auth.actions.test.ts` |
| Page rendering    | E2E         | Playwright               | `login.spec.ts`        |

- Use `@testing-library/react` with Vitest for component tests — test behavior, not implementation.
- Use `msw` (Mock Service Worker) to mock API routes in tests.
- Use Playwright for E2E testing; run against a real or preview deployment.
- Write a minimum of one accessibility test per page using `jest-axe` or Playwright's built-in a11y snapshot.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

### Strict Baseline

### Required Toolchain
| Tool | Purpose | Minimum version | Activate |
| --- | --- | --- | --- |
| Next.js | framework / `next build` gate | 16.3.5 | `pnpm add next@^16.3.5 react@latest react-dom@latest` |
| React | runtime (App Router uses React 19.2 canary) | 19.2 | pulled by `next@16` |
| TypeScript | type-check (`tsc --noEmit`) | 6.0.2 (JS API) / 7.0.2 (native) | `pnpm add -D typescript@^6.0.2` (TS 7 alias in config below) |
| ESLint | lint engine (flat config only in v10; pin 9 for jsx-a11y) | 9.39.5 | `pnpm add -D eslint@^9.39.5` |
| typescript-eslint | `strictTypeChecked` + `stylisticTypeChecked` | 8.70.1 | `pnpm add -D typescript-eslint@^8.70.1` |
| @next/eslint-plugin-next | Next.js rules + core-web-vitals (use plugin directly, not `eslint-config-next`) | 16.3.5 | `pnpm add -D @next/eslint-plugin-next@^16.3.5` |
| eslint-plugin-react-hooks | Rules of Hooks + React Compiler diagnostics | 7.1.1 | `pnpm add -D eslint-plugin-react-hooks@^7.1.1` |
| eslint-plugin-jsx-a11y | strict a11y rules | 6.10.2 | `pnpm add -D eslint-plugin-jsx-a11y@^6.10.2` |
| eslint-plugin-tailwindcss | unknown/contradicting Tailwind classes | 4.4.0 | `pnpm add -D eslint-plugin-tailwindcss@^4.4.0` |
| eslint-config-prettier | disable formatting rules that fight Prettier | 10.x | `pnpm add -D eslint-config-prettier@latest` |
| Prettier | formatter (`--check` gate) | 3.x | `pnpm add -D prettier@latest` |
| prettier-plugin-tailwindcss | class sorting + duplicate removal | 0.8.1 | `pnpm add -D prettier-plugin-tailwindcss@^0.8.1` |
| babel-plugin-react-compiler | React Compiler build-time memoization | 1.0.0 | `pnpm add -D babel-plugin-react-compiler@1.0.0` |
| server-only | hard block on server-only imports in client bundles | 0.0.1 | `pnpm add server-only` |
| size-limit + @size-limit/file | hard bundle-size budget | 14.0.0 | `pnpm add -D size-limit@^14.0.0 @size-limit/file@^14.0.0` |
| @next/bundle-analyzer | Webpack bundle analysis (Turbopack uses `next experimental-analyze`) | 16.3.5 | `pnpm add -D @next/bundle-analyzer@^16.3.5` |
| Vitest + @vitest/coverage-v8 | unit tests + coverage thresholds | 5.0.1 | `pnpm add -D vitest@^5.0.1 @vitest/coverage-v8@^5.0.1` |
| @testing-library/react | component tests | 16.3.3 | `pnpm add -D @testing-library/react@^16.3.3 @testing-library/jest-dom@latest jsdom@latest` |
| @playwright/test | end-to-end | 1.63.0 | `pnpm add -D @playwright/test@^1.63.0` |
| @axe-core/playwright | automated WCAG checks in E2E | 4.13.0 | `pnpm add -D @axe-core/playwright@^4.13.0` |
| knip | unused files / exports / dependencies | 6.37.0 | `pnpm add -D knip@^6.37.0` |
| depcheck | unused-dependency cross-check (redundant with Knip) | 1.4.7 | optional: `pnpm add -D depcheck@^1.4.7` |
| madge | circular-dependency detection | 8.0.0 | `pnpm add -D madge@^8.0.0` |
| lockfile-lint | lockfile poisoning / non-HTTPS / rogue hosts | 5.0.1 | `pnpm add -D lockfile-lint@^5.0.1` |
| osv-scanner | known-vulnerability scan (OSV database) | 2.x | binary / `go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest` |
| Node.js | runtime floor (Next 16 needs ≥20.9; Knip & Tailwind plugin need ≥20.19) | 22.18.0 LTS | `.nvmrc` + `engines` + `.npmrc engine-strict=true` |

> **Compatibility notes (2025–2026).** `next lint` was **removed in Next.js 16** and `next build` **no longer runs linting**; run ESLint (or Biome) directly. Migrate with `npx @next/codemod@canary next-lint-to-eslint-cli .`. `eslint-config-next@16` peer-accepts ESLint ≥9, but it depends on `eslint-plugin-jsx-a11y@^6`, whose peer range stops at `^9` — so installing the **strict a11y set on ESLint 10 fails (`ERESOLVE`)**. Pin ESLint 9.39.x until jsx-a11y ships an ESLint 10 release, and consume `@next/eslint-plugin-next` directly. `eslint-plugin-react-compiler` is **obsolete** (compiler rules now ship in `eslint-plugin-react-hooks@≥6`). `depcheck` is retained only as an optional cross-check; **Knip supersedes it** (files + exports + deps). TS 7.0 has no JS compiler API, so type-aware linting needs the `typescript@6` alias (documented below).

### Strict Baseline Config

**`tsconfig.json` — every strict flag + Next 16 requirements** (TS 6/7 already default `strict: true`; the extras below are what Next's generated config omits):

```jsonc
{
  "compilerOptions": {
    /* strict family — full set */
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noPropertyAccessFromIndexSignature": true,
    "allowUnreachableCode": false,
    "allowUnusedLabels": false,
    "useUnknownInCatchVariables": true,
    "strictBuiltinIteratorReturn": true,

    /* module / interop — bundler-grade strictness */
    "verbatimModuleSyntax": true,
    "isolatedModules": true,
    "erasableSyntaxOnly": true,
    "noUncheckedSideEffectImports": true,
    "forceConsistentCasingInFileNames": true,
    "moduleDetection": "force",
    "module": "esnext",
    "moduleResolution": "bundler",
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],

    /* Next.js requirements */
    "jsx": "preserve",
    "noEmit": true,
    "incremental": true,
    "skipLibCheck": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**`package.json` — TypeScript 7 (fast native `tsc`) alongside the TS 6 API that typescript-eslint requires** (from the official TS 7 announcement; use the simpler `"typescript": "^6.0.2"` if you don't need 7's speed):

```json
{
  "devDependencies": {
    "@typescript/native": "npm:typescript@^7.0.2",
    "typescript": "npm:@typescript/typescript6@^6.0.2"
  }
}
```

**`eslint.config.mjs` — flat config, strictTypeChecked + strict a11y + compiler diagnostics:**

```js
// eslint.config.mjs
import { defineConfig, globalIgnores } from 'eslint/config'
import tseslint from 'typescript-eslint'
import reactHooks from 'eslint-plugin-react-hooks'
import jsxA11y from 'eslint-plugin-jsx-a11y'
import next from '@next/eslint-plugin-next'
import tailwind from 'eslint-plugin-tailwindcss'
import prettier from 'eslint-config-prettier/flat'

export default defineConfig(
  globalIgnores(['.next/**', 'out/**', 'build/**', 'coverage/**', 'next-env.d.ts']),

  // 1. Type-aware TypeScript — strictest preset, uses real type info
  {
    files: ['**/*.{ts,tsx,mjs}'],
    extends: [
      ...tseslint.configs.strictTypeChecked,
      ...tseslint.configs.stylisticTypeChecked,
    ],
    languageOptions: {
      parserOptions: {
        projectService: true,                 // auto-discovers tsconfig.json
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/ban-ts-comment': [
        'error',
        { 'ts-expect-error': 'allow-with-description', minimumDescriptionLength: 10 },
      ],
    },
  },

  // 2. React / Next / a11y / Tailwind — all as ERRORS
  {
    files: ['**/*.{jsx,tsx}'],
    extends: [
      jsxA11y.flatConfigs.strict,
      tailwind.configs['flat/recommended'],
    ],
    plugins: { 'react-hooks': reactHooks, '@next/next': next },
    rules: {
      // React compiler-powered diagnostics (recommended-latest enables the full set)
      ...reactHooks.configs.flat['recommended-latest'].rules,
      'react-hooks/exhaustive-deps': 'error',     // NEVER leave this at warn
      'react-hooks/rules-of-hooks': 'error',
      // Next.js rules + Core Web Vitals promoted to errors
      ...next.configs.recommended.rules,
      ...next.configs['core-web-vitals'].rules,
      '@next/next/no-async-client-component': 'error',
      // Tailwind: unknown / contradicting classes are errors; dedup is Prettier's job
      'tailwindcss/no-custom-classname': 'error',
      'tailwindcss/no-contradicting-classname': 'error',
      'tailwindcss/enforces-shorthand': 'error',
      'tailwindcss/no-unnecessary-arbitrary-value': 'error',
    },
    settings: {
      tailwindcss: { cssConfigPath: './app/globals.css' }, // REQUIRED by the plugin
    },
  },

  // 3. Formatting is Prettier's job
  prettier,
)
```

> `eslint-plugin-tailwindcss@4` requires the shared setting **`tailwindcss.cssConfigPath`** (your Tailwind v4 CSS entry, e.g. `app/globals.css`). Rule names dropped by v4 (e.g. old `classnames-order`) are replaced; run `npx eslint --print-config src/app/page.tsx` if a rule name is rejected.

**`.prettierrc` — class sorting; plugin MUST be last; duplicates removed by default:**

```json
{
  "plugins": ["prettier-plugin-tailwindcss"],
  "tailwindStylesheet": "./app/globals.css",
  "tailwindFunctions": ["cn", "cva", "clsx", "twMerge"],
  "tailwindPreserveDuplicates": false
}
```

**Tailwind v4 content config (CSS-first; no `tailwind.config.js` needed):**

```css
/* app/globals.css */
@import "tailwindcss";
@source "../app/**/*.{ts,tsx}";
@source "../components/**/*.{ts,tsx}";
@theme { /* design tokens */ }
```

**`next.config.ts` — React Compiler + no type/lint escape hatches:**

```ts
import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  reactCompiler: true,          // stable in Next 16; requires babel-plugin-react-compiler
  cacheComponents: true,        // opt-in PPR/use cache model (replaces experimental.ppr)
  eslint: { ignoreDuringBuilds: false },          // must never be true
  typescript: { ignoreBuildErrors: false },       // must never be true
}

export default nextConfig
```

**`size-limit` budget (Next 16 removed `First Load JS` from build output, so budget it explicitly) — `.size-limit.json`:**

```json
[
  {
    "name": "next-client-chunks",
    "path": ".next/static/chunks/**/*.js",
    "limit": "200 kB"
  }
]
```

**`vitest.config.ts` — coverage thresholds (positive = minimum %, negative = max uncovered):**

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['app/**', 'components/**', 'lib/**'],
      exclude: ['**/*.test.*', '**/*.spec.*', '**/*.d.ts'],
      thresholds: {
        statements: 90,
        branches: 85,
        functions: 90,
        lines: 90,
        perFile: true,
      },
    },
  },
})
```

**`knip.json` — dead files / exports / dependencies:**

```json
{
  "$schema": "https://unpkg.com/knip@6/schema.json",
  "entry": ["app/**/{page,layout,route,error,loading,not-found}.{ts,tsx}", "proxy.ts", "next.config.ts", "playwright.config.ts"],
  "project": ["**/*.{ts,tsx}"],
  "ignore": ["**/*.d.ts"],
  "ignoreDependencies": ["@types/*"]
}
```

**`playwright` a11y fixture — WCAG 2.1 A/AA as a hard failure:**

```ts
// tests/axe-test.ts
import { test as base } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

export const test = base.extend<{ makeAxeBuilder: () => AxeBuilder }>({
  makeAxeBuilder: async ({ page }, use) => {
    await use(() =>
      new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']),
    )
  },
})
export { expect } from '@playwright/test'
```

**Node pinning — `.nvmrc` + `package.json` + `.npmrc`:**

```
22.18.0
```

```json
{ "engines": { "node": ">=22.18.0 <23" }, "packageManager": "pnpm@10.0.0" }
```

```
# .npmrc
engine-strict=true
```

### Mandatory Gate Order
1. `npx tsc --noEmit`
2. `npx eslint . --max-warnings=0`
3. `npx prettier --check .`
4. `npx knip`
5. `npx madge --circular --extensions ts,tsx app`
6. `npx vitest run --coverage`
7. `npx next build`
8. `npx size-limit`
9. `npx playwright test`
10. `pnpm exec lockfile-lint --path pnpm-lock.yaml --type pnpm --allowed-hosts npm --validate-https`
11. `osv-scanner scan source -r . --licenses`

> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.

### Hallucination Traps to Block
- Invented/deprecated Next.js APIs and sync `params`/`searchParams`/`cookies()` -> `tsc --noEmit` against Next 16 async request APIs (`await props.params`) + generated `PageProps<'/route'>` / `LayoutProps<'/route'>` / `RouteContext` types from `next typegen`.
- `useState`/`useEffect`/event handlers used without a `'use client'` boundary, or an `async` Client Component -> `next build` (hard error) + `@next/next/no-async-client-component`.
- Server-only module (DB client, secrets) imported into a Client Component -> `import 'server-only'` (build-time throw) + Next `taint` API (`experimental.taint`) for sensitive values.
- Suppressing type errors with `any`, `as`, or `@ts-ignore` -> `@typescript-eslint/no-explicit-any` + the `no-unsafe-*` rules from `strictTypeChecked` + `ban-ts-comment` (description required).
- Stale closures / missing effect deps / setState-in-effect / ref reads during render -> `react-hooks/exhaustive-deps` (error), `react-hooks/set-state-in-effect`, `react-hooks/refs`, `react-hooks/purity`.
- Illegal render-time mutation or broken manual memoization -> `react-hooks/immutability`, `react-hooks/preserve-manual-memoization`, `react-hooks/set-state-in-render`.
- Non-existent, duplicate, or contradicting Tailwind utilities -> `tailwindcss/no-custom-classname`, `tailwindcss/no-contradicting-classname`; duplicates stripped by `prettier-plugin-tailwindcss` (`preserveDuplicates: false`).
- Bloat from a newly added dependency -> `size-limit` (hard kB budget over `.next/static/chunks/**/*.js`).
- Circular imports that crash only at runtime -> `madge --circular`.
- Dead files / unused exports / unused dependencies -> `knip`.
- Lockfile-poisoned or vulnerable dependencies -> `lockfile-lint` + `osv-scanner`.
- Inaccessible UI (unlabeled controls, `div` with `onClick`, missing `alt`) -> `jsx-a11y` strict + `@axe-core/playwright` (`violations` must equal `[]`).

### Evidence to Record
Paste the raw output of each gate and the exact command that produced it:
- `npx tsc --noEmit` — exit code `0`, no diagnostics.
- `npx eslint . --max-warnings=0` — exit code `0`; "0 problems" (warnings are failures).
- `npx prettier --check .` — "All matched files use Prettier code style!".
- `npx knip` — exit code `0`; no unused files/exports/dependencies reported.
- `npx madge --circular --extensions ts,tsx app` — exit code `0`, no cycles (madge exits non-zero when a cycle exists).
- `npx vitest run --coverage` — all tests pass and coverage meets/exceeds `statements 90 / branches 85 / functions 90 / lines 90` (per-file).
- `npx next build` — "Compiled successfully"; zero errors/warnings; `typescript.ignoreBuildErrors` and `eslint.ignoreDuringBuilds` are `false`.
- `npx size-limit` — every entry under its `limit` (e.g. ≤ `200 kB` Brotli).
- `npx playwright test` — all pass; axe scan asserts `accessibilityScanResults.violations` `toEqual([])`; visual snapshots match within `maxDiffPixelRatio: 0.01`.
- `npx lockfile-lint ...` — no output ("file passes").
- `osv-scanner scan source -r . --licenses` — no vulnerabilities at/above the agreed severity threshold.

<!-- sources -->
- https://nextjs.org/docs/app/api-reference/config/eslint
- https://nextjs.org/docs/app/guides/upgrading/version-16
- https://nextjs.org/blog/next-16
- https://nextjs.org/docs/app/api-reference/config/typescript
- https://nextjs.org/docs/app/guides/package-bundling
- https://nextjs.org/docs/app/guides/production-checklist
- https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/
- https://www.typescriptlang.org/tsconfig/
- https://typescript-eslint.io/users/configs/
- https://react.dev/blog/2025/10/07/react-compiler-1
- https://react.dev/reference/eslint-plugin-react-hooks
- https://raw.githubusercontent.com/facebook/react/main/packages/eslint-plugin-react-hooks/README.md
- https://github.com/jsx-eslint/eslint-plugin-jsx-a11y
- https://registry.npmjs.org/eslint-plugin-jsx-a11y/latest
- https://registry.npmjs.org/eslint-config-next/16.3.3
- https://chris.lu/web_development/tutorials/next-js-16-linting-setup-eslint-10-flat-config
- https://github.com/francoismassart/eslint-plugin-tailwindcss
- https://github.com/tailwindlabs/prettier-plugin-tailwindcss
- https://knip.dev/overview/getting-started
- https://knip.dev/overview/configuration
- https://github.com/ai/size-limit
- https://playwright.dev/docs/accessibility-testing
- https://vitest.dev/config/coverage
- https://github.com/google/osv-scanner
- https://github.com/lirantal/lockfile-lint
- https://github.com/pahen/madge

## Currency Baseline

- **No default cache (Next 15+):** `fetch`, `GET` route handlers, and client navigations are not cached unless opted in (`cache: 'force-cache'`, `revalidate`, or a `fetchCache` segment config). Never assume caching by default.
