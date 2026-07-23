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
4. **Tailwind Token System:** Never use arbitrary Tailwind classes (like `h-[12px]`) or inline styles. Declare custom scales inside `tailwind.config.ts` and refer to them.
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
- Use `useActionState` (or `useFormState`) for progressive enhancement.

### Tailwind UI Tokens

- Define design tokens (colors, spacing, fonts) in `tailwind.config.ts` — do not use raw CSS values.
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
