---
name: frontend-architecture-react-vite
description: React 18+ SPA architecture, hooks, and Vite configuration
---

# React (Vite SPA) — Best Practices

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

## Testing Strategies

- **Framework**: `Vitest` + `React Testing Library`.
- **Approach**: Render components, query by accessibility roles (`getByRole`), and simulate user events using `@testing-library/user-event`.
