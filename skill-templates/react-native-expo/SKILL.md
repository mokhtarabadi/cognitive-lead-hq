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
