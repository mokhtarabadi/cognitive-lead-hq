# Task: Zero-Hallucination Skill Templates Restructure

**File:** `tasks/29-zero-hallucination-skill-templates.md`
**Type:** improvement
**Status:** open

## Goal

Restructure `skill-templates/` to enforce "Zero-Hallucination" AI stacks: rewrite Android Kotlin and React Native Expo with strict opinionated rules, add NestJS Prisma Vertical template, and delete legacy unstructured skills (Node.js Express, Android Java XML).

## Manager's Notes

- Android Kotlin must enforce 100% Compose, ban XML, mandate Hilt, enforce null-safety, and require compile-time safe DB (SQLDelight/Room).
- React Native Expo must enforce Expo Managed Workflow only, ban native folder edits, mandate NativeWind, require strict TypeScript.
- NestJS Prisma Vertical must enforce Vertical Slice Architecture, NestJS decorators, Prisma ORM, and class-validator DTOs.
- Delete `skill-templates/nodejs-express` and `skill-templates/android-java-xml`.
- Update README.md stack table and CHANGELOG.md.

## Local TODOs

- [x] Initial codebase exploration
- [x] Rewrite `skill-templates/android-kotlin/SKILL.md` with zero-hallucination rules
- [x] Rewrite `skill-templates/react-native-expo/SKILL.md` with strict Expo Managed rules
- [x] Create `skill-templates/nestjs-prisma-vertical/SKILL.md`
- [x] Delete `skill-templates/nodejs-express` and `skill-templates/android-java-xml`
- [x] Update README.md stack table and repo tree
- [x] Update CHANGELOG.md
- [x] Write execution log in task file
- [x] Finalize: stage_and_inject_diff + notify

## OpenCode Execution Log & Reasoning

**Architectural Reasoning:** This task targets "zero-hallucination" by enforcing strictly opinionated, compile-time-safe frameworks. Android Kotlin now bans XML entirely (the #1 source of UI hallucinations), mandates Hilt DI, and requires SQLDelight/Room for type-safe DB access. React Native Expo bans native folder modification (the #1 source of RN hallucinations), mandates Expo Managed Workflow only, and enforces strict TypeScript. The new NestJS Prisma Vertical template introduces Vertical Slice Architecture (grouping by feature) to localize AI context, combined with Prisma's compile-time ORM guarantees. Legacy Node.js Express (unstructured) and Android Java XML (hallucination-prone) are deleted as they conflict with the "Max Power" zero-hallucination methodology.

**Changes Made:**
1. **skill-templates/android-kotlin/SKILL.md:** Complete rewrite. Description updated to "100% Jetpack Compose, MVI, Hilt, SQLDelight". Added strict XML ban, null-safety rule, compile-time DB mandate. Restructured to 4 required sections with Hilt-specific DI pattern.
2. **skill-templates/react-native-expo/SKILL.md:** Complete rewrite. Description updated to "Expo Managed Workflow, Expo Router, NativeWind, Strict TypeScript". Added banner against modifying ios/android native folders. Mandated NativeWind over StyleSheet.create.
3. **skill-templates/nestjs-prisma-vertical/SKILL.md:** Created new. Enforces NestJS decorators, Vertical Slice Architecture with `features/` grouping, Prisma ORM as source of truth, class-validator DTOs, and ban on `any` type.
4. **skill-templates/nodejs-express/SKILL.md:** Deleted (deprecated — unstructured Express causes AI hallucinations).
5. **skill-templates/android-java-xml/SKILL.md:** Deleted (deprecated — XML layouts cause AI hallucinations).
6. **README.md:** Updated stack table: removed Android Java and Node.js Express rows; added NestJS Prisma Vertical row; updated Android Kotlin and React Native Expo descriptions to emphasize strict zero-hallucination rules; updated repo structure tree.
7. **tasks/29-zero-hallucination-skill-templates.md:** Created this task file.

**Verification:** Pending manual review via stage_and_inject_diff.

## Factual Git Diff

<!-- BEGIN_GIT_DIFF -->

<!-- END_GIT_DIFF -->