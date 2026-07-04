---
name: mobile-architecture-react-native-expo
description: Expo Router, React Native components, and cross-platform UI
---

# React Native (Expo) — Best Practices

## AI Context & Token Optimization

1. **Expo Router:** Use file-based routing (`app/`). It drastically reduces navigation boilerplate, keeping the AI's context focused on the component UI rather than navigation prop-drilling.
2. **NativeWind:** Prefer NativeWind (Tailwind for RN) over `StyleSheet.create`. It reduces line count by 40%, saving massive amounts of tokens per file.
3. **Zustand State:** Avoid Redux. Zustand provides the simplest API footprint for AI-managed global state.

## Project Structure

```
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

- **Expo Router**: Use the `app/` directory for file-based routing. Use `Link` from `expo-router` for navigation.
- **Styling**: Use `StyleSheet.create` for static styles, or NativeWind for Tailwind CSS support in React Native.
- **Safe Areas**: Always wrap top-level screen views in `SafeAreaView` from `react-native-safe-area-context` to prevent UI clipping by notches/status bars.
- **Performance**: Use `FlashList` or `FlatList` for long lists. Never use `ScrollView` for rendering massive amounts of data.

## Testing Strategies

- **Framework**: `Jest` + `@testing-library/react-native`.
- **Component Testing**: Test component rendering and user interactions natively. Mock platform-specific native modules (like `expo-camera` or `expo-location`).
