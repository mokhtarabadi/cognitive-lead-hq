---
name: android-kotlin
description: 100% Jetpack Compose, MVI (UDF), Hilt, and SQLDelight for token-efficient, zero-hallucination Android development.
---

# Android (Kotlin) — "Max Power" AI-Driven Architecture

## AI Context & Token Optimization (Zero-Hallucination Rules)

1. **XML IS STRICTLY BANNED:** Never generate `.xml` layout files. XML forces cross-file context mapping which causes severe UI hallucinations.
2. **100% Jetpack Compose:** Write all UI in declarative Kotlin. Break large UIs into extremely small, pure `@Composable` functions.
3. **Strict Null-Safety:** Rely entirely on Kotlin's null-safety. Do not use `!!` unless absolutely necessary.
4. **Compile-Time Safety for DB:** Use SQLDelight or Room. Do NOT use raw string SQL queries in repositories.

## Project Structure

```text
com.company.project/
├── di/                          # Hilt DI modules
├── data/                        # Data layer (SQLDelight/Room DAOs, DTOs, Repositories)
├── domain/                      # Domain layer (Pure Kotlin Models, UseCases)
└── ui/                          # Presentation layer
    ├── theme/                   # Compose theming (Color, Type, Theme)
    ├── component/               # Small, reusable, modular composables
    └── screen/                  # Feature screens and ViewModels
```

## Naming Conventions

| Artifact               | Convention         | Example            |
| ---------------------- | ------------------ | ------------------ |
| Files / Composables    | `PascalCase`       | `ProfileScreen.kt` |
| Classes / Interfaces   | `PascalCase`       | `GetUserUseCase`   |
| Functions / Properties | `camelCase`        | `getUserById`      |
| Constants              | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT`  |

## Architectural Patterns

**MVI (Model-View-Intent) + UDF:**
Every screen uses a single `ViewModel` annotated with `@HiltViewModel`. The ViewModel exposes exactly one `StateFlow<UiState>`. The View sends sealed `Intents` to the ViewModel. This eliminates race conditions and makes the reasoning traceable through a single `when(intent)` reducer block.

**Dependency Injection:**
Hilt is mandatory. Do not write manual dependency factories.

## Universal DateTime Governance

- **UTC at Rest:** Use `java.time.Instant` for all entity and DTO fields representing absolute timestamps. Store as `TEXT` (ISO-8601) or `INTEGER` (epoch ms) in SQLDelight/Room.
- **Clock Injection:** Inject `java.time.Clock` via Hilt (`@Provides @Singleton fun clock(): Clock = Clock.systemUTC()`). ViewModels and UseCases receive `Clock` via constructor. Banned: `Instant.now()`, `System.currentTimeMillis()`, `LocalDateTime.now()`.
- **API Boundary:** Transmit datetimes as epoch ms (Long) or ISO-8601 strings with offset. Parse with `Instant.parse()` or `Instant.ofEpochMilli()`. Never use `SimpleDateFormat` or `java.util.Date`.
- **UI Display:** Format for user locale using `java.time.format.DateTimeFormatter` with explicit `ZoneId`. Never use the device's default timezone implicitly.

## Testing Strategies

| Layer           | Test Type                  | Framework                     |
| --------------- | -------------------------- | ----------------------------- |
| Use cases       | Unit                       | JUnit 5 + MockK               |
| ViewModel (MVI) | Unit (Intent injection)    | JUnit 5 + Turbine (for Flows) |
| UI / Composable | Snapshot / Compose UI Test | Compose Test                  |


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

### Strict Baseline

Verified against live sources in September 2026. Suggested baseline stack: **Gradle 9.7.1**, **AGP 9.4.0**, **Kotlin 2.4.20**, **Compose BOM 2026.08.00**, **JDK 17** (toolchain), **Gradle Configuration Cache + Isolated Projects** enabled.

### Required Toolchain

| Tool | Purpose | Minimum version | Activate |
| --- | --- | --- | --- |
| Gradle | Build engine; dependency verification, locking, version catalogs, configuration cache | 9.7.1 (AGP 9.4 requires ≥9.6.0) | `gradle/wrapper/gradle-wrapper.properties`: `distributionUrl=https\://services.gradle.org/distributions/gradle-9.7.1-bin.zip` |
| Android Gradle Plugin | Android + bundled Compose lint, R8 full mode, new Variant API | 9.4.0 | `plugins { id("com.android.application") version "9.4.0" }` |
| Kotlin | Compiler strictness (`allWarningsAsErrors`, explicit API) | 2.4.20 | `plugins { kotlin("android") version "2.4.20" }` (AGP 9.4 also bundles KGP; pin explicitly) |
| Compose Compiler plugin | Compose compiler + stability reports/metrics | 2.4.20 (= Kotlin version) | `plugins { id("org.jetbrains.kotlin.plugin.compose") version "2.4.20" }` |
| Jetpack Compose BOM | Align all Compose artifacts | 2026.08.00 (Compose 1.12) | `implementation(platform("androidx.compose:compose-bom:2026.08.00"))` |
| ktlint | Kotlin formatter/linter engine (stable; 2.0.0-ALPHA-4 is preview, needs JVM 17) | 1.8.0 | Pulled by Spotless: `ktlint("1.8.0")` |
| Spotless | Format gate that **fails, never auto-fixes** in CI | 8.10.2 | `plugins { id("com.diffplug.spotless") version "8.10.2" }` |
| detekt | Kotlin static analysis; warnings-as-errors, `buildUponDefaultConfig` | 2.0.0-alpha.6 (plugin id `dev.detekt`; aligned to Kotlin 2.4/AGP 9.3). Fallback: last stable `1.23.8` only supports Kotlin 2.0.21/AGP 8.8.1 — use it only on legacy stacks, and then downgrade the Kotlin/AGP toolchain to match; never mix the alpha config with the stable binary | `plugins { id("dev.detekt") version "2.0.0-alpha.6" }` |
| detekt-compose-rules | Compose-specific static checks for detekt/ktlint | 0.6.6 (≥0.5.0 supports detekt 2.0) | `detektPlugins("io.nlopez.compose.rules:detekt:0.6.6")` |
| Android Lint | Bundled AndroidX + Compose lint checks | ships with AGP 9.4.0 | `android { lint { warningsAsErrors = true; abortOnError = true; checkAllWarnings = true } }` |
| Kover | Coverage verification gate | 0.9.9 | `plugins { id("org.jetbrains.kotlinx.kover") version "0.9.9" }` |
| Robolectric | JVM Android/Compose unit tests (fast gate) | 4.17 | `testImplementation("org.robolectric:robolectric:4.17")` + `testOptions.unitTests.isIncludeAndroidResources = true` |
| Compose UI Test | Instrumented UI gate (v2 test APIs are default from Compose 1.11) | BOM 2026.08.00 | `androidTestImplementation("androidx.compose.ui:ui-test-junit4")`, `debugImplementation("androidx.compose.ui:ui-test-manifest")` |
| SQLDelight | Compile-time SQL typing + migration verification gate | 2.4.0 | `plugins { id("app.cash.sqldelight") version "2.4.0" }` |
| Dependency Analysis (DAGP) | Unused / undeclared / mis-configured dependencies | 3.19.2 | `plugins { id("com.autonomousapps.build-health") version "3.19.2" }` |
| Gradle dependency verification | Tamper/provenance detection for every artifact + plugin | built-in (Gradle 6.2+) | `./gradlew --write-verification-metadata sha256 help` → commit `gradle/verification-metadata.xml` |
| Gradle dependency locking | Reproducible resolved versions | built-in (Gradle 4.8+) | `dependencyLocking { lockAllConfigurations() }` + `./gradlew dependencies --write-locks` |
| Gradle version catalog | Single source of dependency coordinates | built-in | `gradle/libs.versions.toml` (default catalog) |
| OSV-Scanner | Dependency CVE scan; reads `gradle.lockfile`, `buildscript-gradle.lockfile`, `gradle/verification-metadata.xml` | 2.6.0 | `osv-scanner scan source -r .` |
| OWASP dependency-check | Graded CVE gate (`failBuildOnCVSS`) | 13.0.0 | `plugins { id("org.owasp.dependencycheck") version "13.0.0" }` + `./gradlew dependencyCheckAnalyze` |
| gitleaks | Hardcoded-secret scan (must be ≥8.30.1 — CVE-2026-63728 affects <8.30.1) | 8.30.1 | `gitleaks git . --redact --exit-code 1` |
| Hilt / Dagger | DI graph validated at compile time via KSP | 2.60.1 (`androidx.hilt` 1.4.0) | `implementation("com.google.dagger:hilt-android:2.60.1")` + `ksp("com.google.dagger:hilt-compiler:2.60.1")` |
| KSP | Annotation processing (Hilt, Room, SQLDelight interop) | 2.3.11 | `plugins { id("com.google.devtools.ksp") version "2.3.11" }` |

### Strict Baseline Config

All snippets are Kotlin DSL, ready to paste. `./gradlew spotlessCheck`, `detekt`, `lint*`, `koverVerify`, `buildHealth`, and `verifySqlDelightMigration` all fail the build on any violation. **Never run `spotlessApply` / `detekt --auto-correct` in CI.**

#### Bootstrap for fresh repos — Gradle verification

Fresh clones have no `gradle/verification-metadata.xml`. Bootstrap once before enforcing strict mode:

```bash
./gradlew --write-verification-metadata sha256,pgp help
git add gradle/verification-metadata.xml gradle/wrapper/gradle-wrapper.properties
git commit -m "chore: bootstrap Gradle verification metadata"
```

Commit the file before running `--dependency-verification strict`; otherwise the first strict invocation fails. Verify with `./gradlew --dependency-verification strict help` (exit 0, blocks hallucinated artifacts via crypto-checked allowlist).

#### `gradle/libs.versions.toml` (version catalog)

```toml
[versions]
agp = "9.4.0"
kotlin = "2.4.20"
ksp = "2.3.11"
composeBom = "2026.08.00"
detekt = "2.0.0-alpha.6"
composeRules = "0.6.6"
spotless = "8.10.2"
kover = "0.9.9"
sqldelight = "2.4.0"
hilt = "2.60.1"
androidxHilt = "1.4.0"
robolectric = "4.17"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "composeBom" }
androidx-compose-ui = { group = "androidx.compose.ui", name = "ui" }
androidx-compose-ui-test-junit4 = { group = "androidx.compose.ui", name = "ui-test-junit4" }
androidx-compose-ui-test-manifest = { group = "androidx.compose.ui", name = "ui-test-manifest" }
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }
androidx-hilt-navigation-compose = { group = "androidx.hilt", name = "hilt-navigation-compose", version.ref = "androidxHilt" }
robolectric = { group = "org.robolectric", name = "robolectric", version.ref = "robolectric" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
compose-compiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
detekt = { id = "dev.detekt", version.ref = "detekt" }
spotless = { id = "com.diffplug.spotless", version.ref = "spotless" }
kover = { id = "org.jetbrains.kotlinx.kover", version.ref = "kover" }
sqldelight = { id = "app.cash.sqldelight", version.ref = "sqldelight" }
build-health = { id = "com.autonomousapps.build-health", version = "3.19.2" }
dependency-check = { id = "org.owasp.dependencycheck", version = "13.0.0" }
```

#### Root `build.gradle.kts` — formatter, detekt, dependency hygiene

```kotlin
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.compose.compiler) apply false
    alias(libs.plugins.ksp) apply false
    alias(libs.plugins.hilt) apply false
    alias(libs.plugins.detekt)
    alias(libs.plugins.spotless)
    alias(libs.plugins.kover)
    alias(libs.plugins.build.health)
    alias(libs.plugins.dependency.check)
}

spotless {
    kotlin {
        target("**/*.kt")
        targetExclude("**/build/**", "**/generated/**")
        ktlint("1.8.0")
        trimTrailingWhitespace()
        endWithNewline()
    }
    kotlinGradle {
        target("**/*.gradle.kts")
        ktlint("1.8.0")
    }
}

detekt {
    toolVersion = libs.versions.detekt.get()
    buildUponDefaultConfig = true          // start from ALL default rules
    allWarningsAsErrors = true             // warnings are hard failures
    parallel = true
    config.setFrom(files("$rootDir/config/detekt/detekt.yml"))
    baseline = file("$rootDir/config/detekt/baseline.xml")
}

dependencies {
    detektPlugins("io.nlopez.compose.rules:detekt:${libs.versions.composeRules.get()}")
}

tasks.withType<dev.detekt.gradle.Detekt>().configureEach {
    reports {
        sarif.required.set(true)
        html.required.set(true)
        checkstyle.required.set(true)
    }
}

dependencyAnalysis {
    issues {
        all {
            onAny { severity("fail") }   // unused + used-transitive + wrong-config + unused processors
        }
    }
}

dependencyCheck {
    failBuildOnCVSS = 7.0f               // default 11 never fails; set a real gate
    formats = listOf("SARIF", "HTML")
    failOnError = true
}
```

#### `config/detekt/detekt.yml` — maximally strict ruleset

`buildUponDefaultConfig = true` means this file only needs to raise thresholds/turn previously-off rules on; everything omitted keeps detekt's default (already active for standard rulesets).

```yaml
build:
  maxIssues: 0                 # any issue fails the build
  weights: { complexity: 0, LongParameterList: 2, comments: 0 }

config:
  validation: true
  warningsAsErrors: true

complexity:
  active: true
  CyclomaticComplexMethod:
    active: true
    threshold: 10
  LongMethod:
    active: true
    threshold: 60
  LongParameterList:
    active: true
    functionThreshold: 5
    constructorThreshold: 7
    ignoreDefaultParameters: false
  TooManyFunctions:
    active: true
    thresholdInFiles: 15
    thresholdInClasses: 15
    thresholdInInterfaces: 15
    thresholdInObjects: 11
    thresholdInEnums: 11

style:
  active: true
  MaxLineLength:
    active: true
    maxLineLength: 120
    excludePackageStatements: false
  MagicNumber:
    active: true
  WildcardImport:
    active: true
  ReturnCount:
    active: true
    max: 2
  UnusedPrivateMember:
    active: true
  UnusedPrivateProperty:
    active: true
  ForbiddenComment:
    active: true
    comments: ['TODO:', 'FIXME:', 'STOPSHIP:']
  ExplicitApi:                # for library modules
    active: true

potential-bugs:
  active: true
  UnsafeCallOnNullableType:
    active: true
    ignoreGetters: false
  UnsafeCast:
    active: true
  CastNullableToNonNullableType:
    active: true
  NullableBooleanCheck:
    active: true

performance:
  active: true

coroutines:
  active: true
  GlobalCoroutineUsage:
    active: true
  InjectDispatcher:
    active: true
  RedundantSuspendModifier:
    active: true
  SleepInsteadOfDelay:
    active: true

naming:
  active: true
  MatchingDeclarationName:
    active: true
  FunctionNaming:
    active: true
    ignoreAnnotated: ['Composable']

Compose:
  ComposableAnnotationNaming:
    active: true
  ComposableNaming:
    active: true
  ComposableParamOrder:
    active: true
  CompositionLocalAllowlist:
    active: true
  CompositionLocalNaming:
    active: true
  ContentEmitterReturningValues:
    active: true
  ContentTrailingLambda:
    active: true
  DefaultsVisibility:
    active: true
  LambdaParameterEventTrailing:
    active: true
  LambdaParameterInRestartableEffect:
    active: true
  ModifierComposable:
    active: true
  ModifierMissing:
    active: true
  ModifierReused:
    active: true
  MultipleEmitters:
    active: true
  MutableParams:
    active: true
  PreviewAnnotationNaming:
    active: true
  PreviewNamingConvention:
    active: true
  PreviewPublic:
    active: true
  RememberMissing:
    active: true
  UnstableCollections:
    active: true
  ViewModelForwarding:
    active: true
  ViewModelInjection:
    active: true
```

#### Module `app/build.gradle.kts` — lint, compiler strictness, coverage, R8

```kotlin
android {
    lint {
        warningsAsErrors = true        // every warning is an error
        abortOnError = true            // non-zero exit on any error
        checkAllWarnings = true        // include issues that are off-by-default
        checkDependencies = true       // lint transitive library code too
        checkReleaseBuilds = true
        baseline = file("lint-baseline.xml")   // freeze-only; see policy below
        sarifReport = true
        htmlReport = true
        absolutePaths = false
        disable += setOf("GradleDependency", "NewerVersionAvailable") // keep the rest ON
    }

    testOptions {
        unitTests.isIncludeAndroidResources = true   // Robolectric
        unitTests.isReturnDefaultValues = true
        unitTests.all { it.useJUnitPlatform() }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
            // R8 full mode is the AGP 8+/9+ default. Do NOT add android.enableR8.fullMode=false,
            // and never add -ignorewarnings (removed in AGP 8; missing classes are hard errors).
        }
    }
}

kotlin {
    compilerOptions {
        allWarningsAsErrors.set(true)
        progressiveMode.set(true)
        freeCompilerArgs.addAll(
            "-Xjsr305=strict",   // strict Java interop nullability
            // "-Xexplicit-api=strict",  // LIBRARY MODULES ONLY (see explicitApi() below)
        )
    }
    // For published/library modules only (not the app):
    // explicitApi()   // == -Xexplicit-api=strict; requires explicit visibility + return types
}

// Compose compiler stability reports (run on release; feed the review, catch unstable params)
composeCompiler {
    reportsDestination = layout.buildDirectory.dir("compose_reports")
    metricsDestination = layout.buildDirectory.dir("compose_metrics")
}

kover {
    reports {
        total {
            verify {
                rule {
                    minBound(80)   // total line coverage must be >= 80%
                    // Optional stricter bound:
                    // bound { minValue = 70; coverageUnits = CoverageUnit.LINE }
                }
            }
        }
    }
}
```

#### `gradle.properties` — global strict flags

```properties
# Dependency verification: strict is the default once verification-metadata.xml exists.
org.gradle.dependency.verification=strict
org.gradle.dependency.verification.console=verbose

# Reproducibility + strict resource/namespace behavior
android.nonTransitiveRClass=true
android.nonFinalResIds=true
android.enableJetifier=false
android.defaults.buildfeatures.buildconfig=false

# Kotlin
kotlin.code.style=official

# Do NOT add: android.enableR8.fullMode=false
# Do NOT add: android.r8.failOnMissingClasses=false
# Do NOT add: any -ignorewarnings / -dontwarn blanket in proguard-rules.pro
```

#### `settings.gradle.kts` — catalog + federated repositories

```kotlin
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("androidx.*")
                includeGroupByRegex("com\\.google.*")
            }
        }
        mavenCentral()
    }
}
```

#### SQLDelight migration gate (`app/build.gradle.kts`)

```kotlin
sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.db")
            schemaOutputDirectory.set(file("src/main/sqldelight/databases"))
            // generate<SourceSet><Db>Schema writes 1.db; verifySqlDelightMigration replays
            // every .sqm onto 1.db and fails if the result != latest schema.
        }
    }
}
```

#### Lint baseline policy

`lint-baseline.xml` and `config/detekt/baseline.xml` are **freeze-only**: a baseline may be created once to stop the build failing on pre-existing debt, but it may only shrink. CI must fail on **any new** finding. Never regenerate a baseline to silence new violations; never use `--auto-correct` to rewrite baselines.

### Mandatory Gate Order

> **Precondition:** verify every tool in the Required Toolchain table is installed and matches its pinned minimum version (`java -version`, `./gradlew --version`, `kotlin -version`, `agp` version in `libs.versions.toml`). If any tool is missing or the wrong version, install or update it first and rerun the preflight. Do not proceed to the gates below until this check is green.

1. `./gradlew --dependency-verification strict spotlessCheck` — formatting must be clean (no auto-fix)
2. `./gradlew detekt` — static analysis, `allWarningsAsErrors`, `maxIssues: 0`
3. `./gradlew :app:lintDebug :app:lintRelease` — Android/Compose lint, warnings-as-errors
4. `./gradlew :app:compileDebugKotlin :app:compileReleaseKotlin` — Kotlin strictness (`allWarningsAsErrors`, `-Xjsr305=strict`)
5. `if grep -rq "sqldelight" --include="*.kts" . || ls app/src/main/sqldelight app/src/commonMain/sqldelight 2>/dev/null | grep -q "\.sq"; then ./gradlew verifySqlDelightMigration; else echo "SKIP verifySqlDelightMigration | no sqldelight block and no .sq/.sqm files | SQLDelight gate not applicable | exit 0 for this step only"; fi` — SQL schema/query + migration compile-time verification
6. `./gradlew testDebugUnitTest` — JUnit/JUnit5 + Robolectric unit tests
7. `./gradlew :app:connectedDebugAndroidTest` — Compose UI instrumented tests (requires emulator/device; run as a separate stage)
8. `./gradlew koverVerify` — coverage must satisfy the min-bound rule
9. `./gradlew :app:assembleRelease` — R8 full mode; fails on missing classes / broken keep rules
10. `./gradlew buildHealth` — no unused, undeclared, or mis-configured dependencies
11. `osv-scanner scan source -r .` — CVE scan over `gradle.lockfile` + `gradle/verification-metadata.xml`
12. `./gradlew dependencyCheckAnalyze` — OWASP SCA, fails at CVSS ≥ 7.0
13. `gitleaks git . --redact --exit-code 1` — hardcoded-secret scan

> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI. `--dependency-verification strict` must wrap every Gradle invocation (or keep `org.gradle.dependency.verification=strict` in `gradle.properties`). Gates 7 and 12 are still mandatory: if device emulators / NVD refresh are too slow for per-PR, defer them to a nightly/merge queue and log the deferral, but the release is blocked until that queue is green — deferral is scheduling only, never skipping. Deferred gates block `lint_task_file` and any QA transition until the nightly/merge queue is green, with the queue URL plus commit SHA plus green verdict logged in `## Verification Evidence`.

### Hallucination Traps to Block

- Invented Gradle coordinates or version numbers -> Gradle dependency verification (`gradle/verification-metadata.xml` + `--dependency-verification strict`) fails any artifact not in the crypto-checked allowlist; version-catalog accessors (`libs.*`) fail compilation for non-existent aliases.
- Fabricated SQL tables/columns/queries or schema drift -> SQLDelight's compile-time code generation (`generateSqlDelightInterface`) rejects invalid SQL, and `verifySqlDelightMigration` replays `.sqm` files and fails if they don't reconstruct the latest schema.
- Burying or silencing warnings (`@Suppress`, `-ignorewarnings`, `-dontwarn`) -> Kotlin `allWarningsAsErrors`, detekt `allWarningsAsErrors` + `build.maxIssues: 0`, Android Lint `warningsAsErrors = true`, and R8 full mode (missing classes are hard errors since AGP 8; `-ignorewarnings` is removed).
- Missing ProGuard/R8 keep rules for reflection/DI -> `./gradlew :app:assembleRelease` fails with `Missing classes detected while running R8`, naming the exact classes and pointing at `build/outputs/mapping/release/missing_rules.txt`.
- Fake or unstable Compose code -> detekt-compose-rules + bundled AndroidX Compose lint + `composeCompiler` class-stability reports (`unstable class ...`), all run before merge.
- Unsafe null handling (`!!`, unchecked casts, Java-platform nulls) -> detekt `UnsafeCallOnNullableType` / `UnsafeCast` / `CastNullableToNonNullableType` + Kotlin `-Xjsr305=strict`; Kotlin's type system rejects nullable misuse at compile time.
- Phantom coverage or untested code -> `koverVerify` min-bound rule fails the build unless measured coverage meets the threshold.
- Dependency cruft and undeclared transitives -> `buildHealth` with `onAny { severity("fail") }` rejects unused deps, used-transitive deps, wrong configurations, and unused annotation processors.
- Stale or vulnerable libraries, typosquats -> dependency locking + OSV-Scanner (reads the lockfile and verification metadata) + OWASP dependency-check at CVSS ≥ 7.0.
- Hardcoded secrets (Google API keys, keystore passwords, tokens) -> gitleaks ≥ 8.30.1 with `--exit-code 1`.

### Evidence to Record

Paste the exact command and its verdict into Verification Evidence. Pass criteria:

| Command | Pass criterion / artifact |
| --- | --- |
| `./gradlew --dependency-verification strict spotlessCheck` | `BUILD SUCCESSFUL`; zero Spotless violations |
| `./gradlew detekt` | `BUILD SUCCESSFUL`; `build/reports/detekt/detekt.sarif` shows 0 findings, 0 warnings |
| `./gradlew :app:lintDebug :app:lintRelease` | `BUILD SUCCESSFUL`; `build/reports/lint-results-*.sarif` with 0 errors, 0 warnings |
| `./gradlew :app:compileDebugKotlin :app:compileReleaseKotlin` | `BUILD SUCCESSFUL`; no Kotlin warnings |
| `./gradlew verifySqlDelightMigration` | `BUILD SUCCESSFUL`; migrations reconstruct the latest schema |
| `./gradlew testDebugUnitTest` | `BUILD SUCCESSFUL`; test report shows 0 failures; Robolectric tests executed |
| `./gradlew :app:connectedDebugAndroidTest` | `BUILD SUCCESSFUL`; 0 failed Compose UI tests |
| `./gradlew koverVerify` | `BUILD SUCCESSFUL`; `build/reports/kover/report.xml` line coverage ≥ 80% |
| `./gradlew :app:assembleRelease` | `BUILD SUCCESSFUL`; no `Missing classes detected while running R8` |
| `./gradlew buildHealth` | `BUILD SUCCESSFUL`; `build/reports/dependency-analysis/` has no fail-severity advice |
| `osv-scanner scan source -r .` | Exit 0; no un-ignored vulnerabilities in `gradle.lockfile` / `verification-metadata.xml` |
| `./gradlew dependencyCheckAnalyze` | `BUILD SUCCESSFUL`; no dependency with CVSS ≥ 7.0 |
| `gitleaks git . --redact --exit-code 1` | Exit 0; no secrets detected |

<!-- sources -->
- https://github.com/diffplug/spotless & https://plugins.gradle.org/plugin/com.diffplug.spotless (Spotless 8.10.2)
- https://plugins.gradle.org/search?term=ktlint (ktlint Gradle plugins; `org.jlleitschuh.gradle.ktlint` 14.2.0, `io.github.usefulness.ktlint-gradle-plugin` 0.14.0)
- https://github.com/ktlint/ktlint/releases (ktlint 1.8.0 stable, 2.0.0-ALPHA-4; JVM 17 requirement)
- https://github.com/detekt/detekt/releases & https://detekt.dev/docs/introduction/compatibility (detekt 2.0.0-alpha.6; 1.23.8 last stable)
- https://detekt.dev/docs/introduction/migration (detekt 2.0 plugin id `dev.detekt`, coordinates `dev.detekt:*`, min JDK 17/Kotlin 2.4/AGP 8.2.2)
- https://mrmans0n.github.io/compose-rules/detekt/ (compose-rules 0.6.6; detekt 2.0 support matrix)
- https://developer.android.com/reference/tools/gradle-api/8.9/com/android/build/api/dsl/Lint (lint DSL: warningsAsErrors/abortOnError/checkAllWarnings/checkDependencies)
- https://developer.android.com/build/releases/agp-9-4-0-release-notes (AGP 9.4.0, Gradle 9.6.0, API 37)
- https://developer.android.com/build/releases/gradle-plugin-roadmap (AGP 10 / new Variant API migration)
- https://developer.android.com/agents/skills/performance/r8-analyzer/references/CONFIGURATION (R8 full mode default AGP 8+)
- https://issuetracker.google.com/issues/243342123 (AGP 8 removed `-ignorewarnings`; missing classes are errors)
- https://kotlinlang.org/docs/gradle-compiler-options.html & https://kotlinlang.org/api/kotlin-gradle-plugin/ (allWarningsAsErrors, explicitApi / `-Xexplicit-api=strict`)
- https://github.com/JetBrains/kotlin/releases (Kotlin 2.4.20)
- https://github.com/Kotlin/kotlinx-kover/releases & https://kotlin.github.io/kotlinx-kover/gradle-plugin/ (Kover 0.9.9 verification rules)
- https://github.com/autonomousapps/dependency-analysis-gradle-plugin & https://plugins.gradle.org/plugin/com.autonomousapps.dependency-analysis (DAGP 3.19.2, `severity("fail")`)
- https://docs.gradle.org/current/userguide/dependency_verification.html (verification metadata, strict mode)
- https://docs.gradle.org/current/userguide/dependency_locking.html (lockAllConfigurations, `--write-locks`)
- https://docs.gradle.org/current/userguide/version_catalogs.html (version catalog TOML)
- https://gradle.org/releases/ (Gradle 9.7.1)
- https://github.com/google/osv-scanner & https://google.github.io/osv-scanner/supported-languages-and-lockfiles/ (OSV-Scanner 2.x; Gradle lockfile + verification-metadata support)
- https://github.com/dependency-check/dependency-check-gradle & https://dependency-check.github.io/DependencyCheck/dependency-check-gradle/configuration.html (dependency-check 13.0.0, failBuildOnCVSS)
- https://github.com/gitleaks/gitleaks & https://www.vulncheck.com/advisories/gitleaks-secret-exfiltration-via-non-hermetic-sprig-template-functions-in-report-template-feature (gitleaks 8.30.1 fixes CVE-2026-63728)
- https://github.com/cashapp/sqldelight/releases & https://sqldelight.github.io/sqldelight/2.4.0/android_sqlite/migrations/ (SQLDelight 2.4.0, verifySqlDelightMigration)
- https://github.com/robolectric/robolectric/releases (Robolectric 4.17)
- https://developer.android.com/develop/ui/compose/bom (Compose BOM 2026.08.00)
- https://developer.android.com/reference/kotlin/androidx/compose/ui/test/junit4/package-summary (Compose v2 test APIs; createAndroidComposeRule)
- https://developer.android.com/jetpack/androidx/releases/hilt & https://mvnrepository.com/artifact/com.google.dagger/hilt-android (Hilt 2.60.1; androidx.hilt 1.4.0)
- https://kotlinlang.org/docs/whatsnew2420.html & https://whatsnew.fyi/product/ksp/latest (Kotlin 2.4.20; KSP 2.3.11)
- https://mvnrepository.com/artifact/io.gitlab.arturbosch.detekt/detekt-gradle-plugin (detekt artifact history)

## Currency Baseline

- **KSP codegen + Compose BOM:** Use KSP (never KAPT) for Room/Hilt processors, and pin Compose artifacts via the Compose BOM.
- **Edge-to-edge:** Call `enableEdgeToEdge()`; Android 15 enforces edge-to-edge, so never hardcode system-bar insets.
