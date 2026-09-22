---
name: ios-swiftui
description: SwiftUI, MVVM, and modern iOS app architecture
---

# iOS (SwiftUI) — Best Practices

## AI Context & Token Optimization

1. **SwiftUI Over UIKit:** Strictly ban UIKit (unless bridging is unavoidable). Declarative SwiftUI trees are vastly more token-efficient and predictable for AI generation.
2. **Modern Concurrency:** Mandate `async/await`. Avoid completion handlers and closures, which lead to "callback hell" formatting that breaks AI syntax continuity.
3. **Observable State:** Use `@Observable` (iOS 17+) to keep state management clean and localized, preventing cross-file state hallucinations.

## Project Structure

```
App/
├── App.swift            # @main struct
├── Core/                # Networking, Extensions, Utilities
├── Models/              # Data structures (Codable)
├── Views/               # SwiftUI Views
│   ├── Shared/          # Reusable components
│   └── Screens/         # Full page views
└── ViewModels/          # ObservableObjects for business logic
```

## Naming Conventions

- **Types/Structs/Classes**: `PascalCase` (e.g., `UserProfileView`)
- **Variables/Functions**: `camelCase` (e.g., `fetchUserData()`)
- **Modifiers**: Custom ViewModifiers should be `PascalCase`.

## Architectural Patterns

- **MVVM Pattern**: Separate UI (View) from business logic (ViewModel). Views should only handle layout and state binding.
- **State Management**:
  - Use `@State` for simple, local UI state.
  - Use `@StateObject` (or `@Observable` macro in iOS 17+) for ViewModels owned by the view.
  - Use `@EnvironmentObject` (or `@Environment`) for global dependency injection.
- **Networking**: Use modern `async/await` (`URLSession.shared.data(from:)`). Avoid legacy closures/completion blocks.
- **Concurrency**: Use `@MainActor` on ViewModels to ensure UI updates happen on the main thread.

## Universal DateTime Governance

- **UTC at Rest:** Store all `Date` values in UTC. Use `ISO8601DateFormatter()` with `.withInternetDateTime` and `.withFractionalSeconds` options for serialization.
- **Clock Injection:** Define a `ClockProvider` protocol with `func now() -> Date`. Default implementation returns `Date()`. Inject via `@Environment` or initializer. Banned: calling `Date()` directly in ViewModels or business logic.
- **API Boundary:** Transmit datetimes as epoch ms (Int64) or ISO-8601 UTC strings. Use `JSONEncoder.DateEncodingStrategy.millisecondsSince1970` or custom `DateFormatter`.
- **UI Display:** Format with `DateFormatter` using explicit `timeZone = TimeZone(secondsFromGMT: 0)` for server times, then convert to user's local timezone. Never mix timezone-ambiguous `Date` objects.

## Testing Strategies

- **Framework**: `XCTest` + `XCUITest`.
- **Unit Tests**: Test ViewModels independently of Views. Inject mock network clients via protocols to verify state changes.
- **UI Tests**: Use Accessibility Identifiers (`.accessibilityIdentifier("login_btn")`) to write stable UI tests.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

### Strict Baseline

> Target: Swift + SwiftUI (MVVM), Swift Package Manager + Xcode. Verified live 2026-09-21.
> Rule: every gate below must FAIL (non-zero exit) on a violation. Nothing auto-fixes in CI.

### Required Toolchain

| Tool | Purpose | Minimum version | Activate |
| --- | --- | --- | --- |
| Swift / swiftc (toolchain) | Language mode, strict concurrency, upcoming features, warnings-as-errors | Swift 6.2 (Xcode 26+); latest open-source `swift-6.4.0-RELEASE` (Sep 2026) | `xcode-select -p` pin via `.xcode-version`; `SWIFT_VERSION = 6.0` |
| SwiftLint | Lint rules + type-checked analyzer rules (AST) | 0.65.1 (2026-08-21) | `brew install swiftlint` **or** SPM plugin dep `https://github.com/realm/SwiftLint` (`.exact("0.65.1")`) |
| swift-format (Apple) | Canonical formatter; bundled in the Swift toolchain, `--strict` fails on lint warnings | 600.0.0 (Swift 6 toolchain); standalone latest 604.0.0 (2026-09-16) | bundled — `xcrun --find swift-format` / `swift format` |
| SwiftFormat (nicklockwood) | Optional richer formatter, only if swift-format is not used | 0.63.0 (2026-08-30) | `brew install swiftformat` **or** `ghcr.io/nicklockwood/swiftformat:latest` |
| xcodebuild + clang static analyzer | `analyze` (Clang analyzer) + build gates | Xcode 26+ | built in |
| `xcrun xccov` | Coverage extraction + threshold gate | Xcode 26+ | built in (`.xcresult`) |
| OSV-Scanner | Dependency vulnerability + license scanning | v2.6.0 (2026-09-14) | `brew install osv-scanner` / release binary |
| gitleaks | Secret scanning (git history + working tree) | v8.30.1 (2026-03-21) | `brew install gitleaks` |
| jq | JSON processor for `xccov` coverage extraction | 1.8.1 (2026) | `brew install jq` |
| swift-snapshot-testing | Snapshot tests for SwiftUI views/view-models | 1.19.5 (2026-09-15) | SPM `.package(url: "https://github.com/pointfreeco/swift-snapshot-testing", from: "1.19.5")` |
| Swift Testing | Modern test framework (bundled) | Swift 6.2+ / swift-testing 6.4.0 | bundled with the toolchain |
| XcodeGen | Deterministic `.xcodeproj` generation from YAML | 2.46.0 (2026-07-16) | `brew install xcodegen` |
| Tuist | Alternative project generator (Swift manifests, caching) | 4.211.x (2026) | `brew install tuist` / `mise` |
| `swift-dependency-audit` | Declared-vs-imported SPM dependency audit (unused/missing) | 2.0.8 (2025-12-30) — young, use as advisory | `brew install tonyarnold/tap/swift-dependency-audit` |

> **Advisory only — Periphery:** OSS Periphery 3.8.0 was archived 2026-08-12 (read-only). Do NOT gate on it. Use commercial `periphery.pro` open beta or a source fork as an advisory scan only.

**Discarded / not maintained (do not add):**
- **Periphery (OSS)** — archived 2026-08-12 by the author; moved to a commercial product (`periphery.pro`). The last OSS tag (3.8.0) still runs, but gets no Swift-version sync.
- **`swift package diagnose-api-breaking-changes`** — `experimental-api-diff` was promoted but is still marked experimental for production use; keep it as an advisory gate on library targets, not a hard blocker for apps.
- **xcov / slather** — depend on the legacy `.xcresult` layout; prefer native `xcrun xccov`.

### Strict Baseline Config

**`.xcode-version`** (repo root — pins the toolchain for mise/Tuist/CI):
```
26.4
```

**`Config/Strict.xcconfig`** (imported by all targets; deterministic strict settings):
```
SWIFT_VERSION = 6.0
SWIFT_STRICT_CONCURRENCY = complete
SWIFT_TREAT_WARNINGS_AS_ERRORS = YES
GCC_TREAT_WARNINGS_AS_ERRORS = YES
CLANG_WARN_DOCUMENTATION_COMMENTS = YES
CLANG_ANALYZER_LOCALIZABILITY_NONLOCALIZED = YES
ENABLE_USER_SCRIPT_SANDBOXING = YES
ENABLE_MODULE_VERIFIER = YES
DEAD_CODE_STRIPPING = YES
SWIFT_EMIT_LOC_STRINGS = YES
OTHER_SWIFT_FLAGS = $(inherited) -enable-upcoming-feature ExistentialAny -enable-upcoming-feature InternalImportsByDefault -enable-upcoming-feature MemberImportVisibility -enable-upcoming-feature InferIsolatedConformances -enable-upcoming-feature NonisolatedNonsendingByDefault -enable-upcoming-feature ImmutableWeakCaptures -warnings-as-errors
```

**`.swiftlint.yml`** (strict lint + all analyzer rules; run under `swiftlint lint` and `swiftlint analyze`):
```yaml
strict: true

analyzer_rules: # pinned for SwiftLint 0.65.1 — do not use `all` (floats)
  - capture_variable
  - explicit_self
  - typesafe_array_init
  - unused_declaration
  - unused_import

opt_in_rules: # pinned subset for 0.65.1 — expand only with reviewed additions, never `all`
  - empty_count
  - empty_string
  - force_unwrapping
  - implicitly_unwrapped_optional
  - closure_end_indentation
  - collection_alignment
  - explicit_acl
  - file_header
  - force_cast
  - force_try
  - missing_docs
  - redundant_nil_coalescing
  - vertical_whitespace
  - yoda_condition

disabled_rules:
  # owned by swift-format -> avoid double-reporting
  - trailing_whitespace
  - indentation_width
  - opening_brace
  - closure_spacing
  - comma
  - colon
  - comment_spacing
  - empty_enum_arguments
  - sorted_imports
  # policy exceptions (documented, not silent)
  - todo
  - explicit_top_level_acl
  - no_extension_access_modifier
  - no_grouping_extension
  - number_separator
  - prefixed_toplevel_constant
  - prohibited_interface_builder
  - required_deinit
  - explicit_init

line_length:
  warning: 120
  error: 160
  ignores_comments: false
  ignores_urls: false

function_body_length:
  warning: 60
  error: 100

type_body_length:
  warning: 300
  error: 400

file_length:
  warning: 500
  error: 800

identifier_name:
  min_length:
    error: 3
  excluded: [id, x, y, z, i, j, k, vm, db, ui]
```

**`.swift-format`** (Apple swift-format; run under `swift format lint --strict`. Regenerate defaults for your toolchain with `swift-format dump-configuration`):
```json
{
  "version": 1,
  "lineLength": 120,
  "indentation": { "spaces": 4 },
  "tabWidth": 4,
  "maximumBlankLines": 1,
  "respectsExistingLineBreaks": true,
  "lineBreakBeforeEachArgument": false,
  "multiElementCollectionTrailingCommas": true,
  "prioritizeKeepingFunctionOutputTogether": true,
  "indentConditionalCompilationBlocks": true,
  "indentSwitchCaseLabels": false,
  "rules": {
    "AlwaysUseLowerCamelCase": true,
    "AmbiguousTrailingClosureOverload": true,
    "DoNotUseSemicolons": true,
    "NoBlockComments": true,
    "NoParensAroundConditions": true,
    "NoVoidReturnOnFunctionSignature": true,
    "OneCasePerLine": true,
    "OneVariableDeclarationPerLine": true,
    "OrderedImports": true,
    "ReturnVoidInsteadOfEmptyTuple": true,
    "UseEarlyExits": true,
    "UseShorthandTypeNames": true,
    "UseSingleLinePropertyGetter": true,
    "UseTripleSlashForDocumentationComments": true,
    "UseWhereClausesInForLoops": true,
    "ValidateDocumentationComments": false
  }
}
```

**`Package.swift`** (SPM strictness; requires tools-version 6.2 for `treatAllWarnings`/`strictMemorySafety`):
```swift
// swift-tools-version: 6.2
import PackageDescription

let strict: [SwiftSetting] = [
    .enableUpcomingFeature("ExistentialAny"),                 // SE-0335 (Swift 5.6)
    .enableUpcomingFeature("InternalImportsByDefault"),       // SE-0409 (Swift 6.0)
    .enableUpcomingFeature("MemberImportVisibility"),         // SE-0444 (Swift 6.1)
    .enableUpcomingFeature("InferIsolatedConformances"),      // SE-0470 (Swift 6.2)
    .enableUpcomingFeature("NonisolatedNonsendingByDefault"), // SE-0461 (Swift 6.2)
    .enableUpcomingFeature("ImmutableWeakCaptures"),          // SE-0481 (Swift 6.2)
    .strictMemorySafety(),                                    // PackageDescription 6.2
    .treatAllWarnings(as: .error),                            // PackageDescription 6.2
]

let package = Package(
    name: "Feature",
    platforms: [.iOS(.v18)],
    products: [.library(name: "Feature", targets: ["Feature"])],
    targets: [
        .target(name: "Feature", swiftSettings: strict),
        .testTarget(name: "FeatureTests", dependencies: ["Feature"], swiftSettings: strict),
    ]
)
```

> Swift 5 language mode only (migration window): add `.enableUpcomingFeature("StrictConcurrency")` and `.unsafeFlags(["-strict-concurrency=complete"])` (root packages only — `unsafeFlags` is rejected in dependencies).

**`.xcodegen/project.yml`** (deterministic project; commit the generated `.xcodeproj`):
```yaml
name: App
options:
  minimumXcodeGenVersion: 2.46.0
  deploymentTarget:
    iOS: "18.0"
  createIntermediateGroups: true
targets:
  App:
    type: application
    platform: iOS
    sources: [Sources/App]
    configFiles:
      Debug: Config/Strict.xcconfig
      Release: Config/Strict.xcconfig
    scheme:
      gatherCoverageData: true
      testTargets: [AppTests, AppUITests]
```

### Mandatory Gate Order

> **Precondition:** verify every tool in the Required Toolchain table is installed and matches its pinned minimum version (`xcodebuild -version`, `swift --version`, `swiftlint version`, `swift-format --version`, `xcodegen --version`). If any tool is missing or the wrong version, install or update it first and rerun the check. Do not proceed to the gates below until this check is green.

```bash
# 0. Generate the project deterministically (commit the result; CI regenerates + asserts no diff)
xcodegen generate --spec .xcodegen/project.yml --project . && git diff --exit-code -- App.xcodeproj

# 1. Format gate — Apple swift-format (toolchain-bundled) — warnings are failures (required)
swift-format lint --strict --recursive Sources Tests
# Optional appendix — SwiftFormat (nicklockwood) — never run as required gate alongside Apple swift-format; both must never run together as required gates. Use only if Apple gate is disabled:
# swiftformat --lint Sources Tests

# 2. Style gate — every warning is an error
swiftlint lint --strict --config .swiftlint.yml

# 3. Build gate — Swift 6 strict concurrency + warnings-as-errors, capture compiler log
xcodebuild -project App.xcodeproj -scheme App -configuration Debug \
  -destination 'generic/platform=iOS Simulator' \
  SWIFT_TREAT_WARNINGS_AS_ERRORS=YES SWIFT_STRICT_CONCURRENCY=complete \
  clean build > xcodebuild.log 2>&1

# 4. Analyzer gate — type-checked AST rules (explicit_self, unused_declaration, unused_import, capture_variable, typesafe_array_init)
swiftlint analyze --strict --compiler-log-path xcodebuild.log

# 5. Static analyzer gate (Clang analyzer)
xcodebuild -project App.xcodeproj -scheme App -configuration Debug analyze

# 6. API-breakage gate (library/package targets only)
BASELINE=$(git describe --tags --abbrev=0 2>/dev/null || true)
if [ -z "$BASELINE" ]; then echo "SKIP: no git tags — cannot diff public API (tag a baseline release to enable this gate)"; else swift package diagnose-api-breaking-changes "$BASELINE"; fi

# 7. Dependency hygiene — declared vs imported (advisory until it stabilizes)
swift-dependency-audit --path . --fail-on-unused

# 8. Secret gate — fails on any finding
gitleaks detect --source . --redact --no-banner --exit-code 1

# 9. Vulnerability + license gate
osv-scanner scan source -r . --licenses

# 10. Test + coverage gate
xcodebuild test -project App.xcodeproj -scheme App \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -enableCodeCoverage YES -resultBundlePath Test.xcresult
COVERAGE=$(xcrun xccov view --report --json Test.xcresult | jq -r '[.targets[] | select(.name=="App.app")][0].lineCoverage // empty')
if [ -z "$COVERAGE" ] || [ "$COVERAGE" = "null" ]; then echo "FAIL coverage: App target not found in xccov report (check .xcodeproj scheme gatherCoverageData)"; exit 1; fi
awk -v c="$COVERAGE" 'BEGIN { if (c+0 < 0.80) { print "FAIL coverage "c" < 0.80"; exit 1 } }'

# 11. Thread Sanitizer gate (separate CI job)
xcodebuild test -project App.xcodeproj -scheme App \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -enableThreadSanitizer YES

# 12. Address Sanitizer gate (separate CI job)
xcodebuild test -project App.xcodeproj -scheme App \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -enableAddressSanitizer YES
```

> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.

### Hallucination Traps to Block

- AI passes a non-`Sendable` model across an actor/`@MainActor` boundary -> `SWIFT_STRICT_CONCURRENCY=complete` / `-strict-concurrency=complete` (Swift 6 mode makes it a hard error).
- AI omits `any` on protocol existentials (`let delegate: Foo`) -> `-enable-upcoming-feature ExistentialAny` forces `any Foo`.
- AI imports a module or declares a target dependency it never uses -> SwiftLint analyzer `unused_import` / `unused_declaration`, plus `swift-dependency-audit`.
- AI leaves generated scaffolding, dead VMs, or unused `@ViewBuilder` helpers -> SwiftLint analyzer `unused_declaration` (advisory only: `periphery.pro` or a fork for a full scan).
- AI force-unwraps, uses `try!`, `as!`, or implicitly unwrapped optionals -> swift-format rules `NeverForceUnwrap`/`NeverUseForceTry`/`NeverUseImplicitlyUnwrappedOptionals`; SwiftLint `force_unwrapping`/`force_cast`/`force_try`.
- AI hard-codes API keys/tokens in Swift config or `Info.plist` -> gitleaks (`--exit-code 1`, scans history + archives).
- AI pins a vulnerable package version -> osv-scanner (`Package.resolved`/`Package.swift`).
- AI ships a data race that only manifests under concurrency -> Thread Sanitizer gate (`-enableThreadSanitizer YES`).
- AI silently breaks a public package API -> `swift package diagnose-api-breaking-changes <baseline>`.

### Evidence to Record

Paste into Verification Evidence (commands + pass criterion):

1. `swift-format lint --strict --recursive Sources Tests` -> **exit 0**, zero diagnostics (Apple swift-format 604.0.0) — required gate; SwiftFormat (nicklockwood) is optional appendix only, never run alongside Apple gate as required.
2. `swiftlint lint --strict --config .swiftlint.yml` -> **exit 0**, zero warnings.
3. `xcodebuild ... build SWIFT_TREAT_WARNINGS_AS_ERRORS=YES SWIFT_STRICT_CONCURRENCY=complete > xcodebuild.log 2>&1` -> **exit 0**, no `warning:`/`error:`; record `xcodebuild -version` and `swift --version`.
4. `swiftlint analyze --strict --compiler-log-path xcodebuild.log` -> **exit 0**, zero analyzer violations.
5. `xcodebuild ... analyze` -> **exit 0**, no analyzer findings.
6. `swift package diagnose-api-breaking-changes <baseline>` (library only) -> **exit 0**, "no breaking changes".
7. `gitleaks detect --source . --redact --exit-code 1` -> **exit 0**, "no leaks found".
8. `osv-scanner scan source -r . --licenses` -> **exit 0**, no known vulnerabilities.
9. `xcodebuild test ... -enableCodeCoverage YES` + `xccov` threshold -> tests pass and line coverage >= 0.80 (paste the exact computed percentage).
10. TSan job and ASan job -> **exit 0**, zero sanitizer reports.

<!-- sources -->
- https://github.com/realm/SwiftLint/releases (SwiftLint 0.65.1) and https://github.com/realm/SwiftLint (strict/analyze/analyzer_rules)
- https://realm.github.io/SwiftLint/rule-directory.html (analyzer rules: capture_variable, explicit_self, typesafe_array_init, unused_declaration, unused_import)
- https://github.com/nicklockwood/SwiftFormat/releases (0.63.0) and https://github.com/nicklockwood/SwiftFormat (--lint exit codes)
- https://github.com/swiftlang/swift-format/releases (604.0.0) and https://github.com/swiftlang/swift-format (lint `-s/--strict`)
- https://developer.apple.com/documentation/Swift/AdoptingSwift6 (strict concurrency)
- https://www.swift.org/migration/documentation/migrationguide/ (Swift 6 language mode opt-in)
- https://github.com/treastrain/swift-upcomingfeatureflags-cheatsheet (ExistentialAny, InternalImportsByDefault, MemberImportVisibility, InferIsolatedConformances, NonisolatedNonsendingByDefault, ImmutableWeakCaptures)
- https://github.com/swiftlang/swift-package-manager/blob/main/Sources/Runtimes/PackageDescription/BuildSettings.swift (`.treatAllWarnings(as:)`, `.strictMemorySafety()`, `.enableUpcomingFeature`)
- https://github.com/swiftlang/swift-package-manager/blob/main/Sources/PackageManagerDocs/Documentation.docc/Package/PackageDiagnoseAPIBreakingChange.md
- https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early (`-enableThreadSanitizer YES`, `-enableAddressSanitizer YES`)
- https://github.com/google/osv-scanner/releases (v2.6.0)
- https://github.com/gitleaks/gitleaks/releases (v8.30.1)
- https://github.com/pointfreeco/swift-snapshot-testing/releases (1.19.5)
- https://github.com/yonaskolb/XcodeGen/releases (2.46.0) and https://github.com/tuist/tuist/releases (4.211.x)
- https://github.com/peripheryapp/periphery (archived 2026-08-12) and https://periphery.pro/a-new-chapter (commercial transition)
- https://github.com/tonyarnold/swift-dependency-audit (v2.0.8, unused/missing SPM deps)

## Currency Baseline

- **Swift 6 mode:** Enable the Swift 6 language mode (complete concurrency checking); all types crossing actor boundaries must conform to `Sendable`, with ViewModels kept `@MainActor`-isolated.
