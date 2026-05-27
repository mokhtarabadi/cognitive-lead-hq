---
name: frontend-architecture-vue-nuxt
description: Vue 3 Composition API, Nuxt 3 routing, and state management
---

# Vue 3 & Nuxt 3 — Best Practices

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

## Testing Strategies

- **Framework**: `Vitest` + `Vue Test Utils`.
- **Component Testing**: Mount components and test DOM output/emitted events.
- **E2E Testing**: Use `Playwright` or `Cypress`.
