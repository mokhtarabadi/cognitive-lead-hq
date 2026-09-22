---
name: spring-boot
description: DDD, hexagonal style, and naming conventions for Spring Boot
---

# Spring Boot — Best Practices & AI-Driven Scaffolding

## AI Context & Token Optimization

1. **MapStruct for Mapping:** Never write manual DTO-to-Entity mapping code. AI agents often hallucinate field names during manual mapping. MapStruct ensures compile-time safety.
2. **Constructor Injection:** Use Lombok's `@RequiredArgsConstructor`. Field `@Autowired` obscures dependencies from the AI's static analysis.
3. **Hexagonal Boundaries:** Keep the `domain/` layer completely free of Spring/JPA annotations to ensure pure, testable Java logic.

## High-Performance Project Onboarding

Initialize any Spring Boot backend from scratch with these architectural rules:

1. **Domain-Driven Design (DDD):** Use a pure `domain` package containing entities, value objects, and repository ports (interfaces). The domain must not have adapter or framework dependencies.
2. **Hexagonal Ports & Adapters:** Inbound adapters (Controllers, DTOs) and outbound adapters (JPA Repositories, Database engines) are decoupled. Controllers depend on domain services, and domain services interact with adapters via ports.
3. **Constructor Injection:** Always use Lombok `@RequiredArgsConstructor` on classes needing dependencies. Banned: Field `@Autowired`.
4. **MapStruct Compile-Time Mapping:** Generate mappers using MapStruct `@Mapper(componentModel = "spring")`. Banned: reflection-based mapping or manually writing setter chains.
5. **Centralized Error Boundary:** Implement a single `@RestControllerAdvice` class capturing all domain-specific exceptions and mapping them to standardized HTTP responses `{ error, message, status, timestamp }`.
6. **Database Migration:** Always use Flyway or Liquibase to manage relational schemas via SQL files in `resources/db/migration`. Banned: relying on JPA `hibernate.ddl-auto=update` in production.

## Project Structure

```
src/main/java/com/company/project/
├── adapter/                   # Inbound & outbound adapters
│   ├── inbound/
│   │   ├── controller/        # REST controllers
│   │   └── dto/               # Request/response DTOs
│   └── outbound/
│       ├── repository/        # JPA / data repositories
│       └── mapper/            # MapStruct mappers
├── domain/
│   ├── entity/                # Domain entities (@Entity)
│   ├── service/               # Business logic
│   ├── exception/             # Domain exceptions
│   └── port/                  # Repository interfaces (ports)
└── common/
    ├── config/                # @Configuration classes
    ├── exception/             # Global exception handler
    └── util/                  # Utility classes

src/main/resources/
├── application.yml            # Default config
├── application-dev.yml        # Dev profile
└── application-prod.yml       # Production profile
```

## Naming Conventions

| Artifact       | Convention                 | Example                              |
| -------------- | -------------------------- | ------------------------------------ |
| Packages       | `lowercase.reverse.domain` | `com.company.project.domain.service` |
| Classes        | `PascalCase`               | `UserServiceImpl`                    |
| Methods        | `camelCase`                | `findByEmail`                        |
| REST endpoints | plural nouns, `kebab-case` | `/api/users/{id}`                    |
| Tables         | `snake_case` plural        | `user_roles`                         |
| Columns        | `snake_case`               | `created_at`                         |

## Architectural Patterns

### Domain-Driven Design (DDD)

Structure the application so that the domain is the innermost, most stable layer.

- **Domain** — Entities, value objects, domain services, repository ports. No framework annotations here (except `@Entity` where unavoidable).
- **Adapter** — Controllers, DTOs, JPA repositories, mappers. These depend on the domain, not the other way around.
- **Ports** — Interfaces in the domain layer that adapters implement. For example, a `UserRepository` interface in `domain/port/` is implemented by `JpaUserRepository` in `adapter/outbound/repository/`.

### MapStruct for Entity ↔ DTO Mapping

- Generate mapper implementations at compile time — no runtime reflection overhead.
- Keep mapping logic in dedicated `@Mapper` interfaces; never hand-write `set` calls.
- Use `@Mapping` annotations for field name differences.

### Constructor Injection Over Field Injection

Always inject dependencies via the constructor (Lombok `@RequiredArgsConstructor` or explicit constructor). Never use `@Autowired` on fields — it makes testing and immutability harder.

### Global Exception Handling

Create a single `@RestControllerAdvice` class that catches all exceptions.

- Map domain exceptions (e.g., `UserNotFoundException`) to specific HTTP status codes.
- Return a consistent error response body (`{ error, message, status, timestamp }`).
- Log the stack trace at `ERROR` level for 5xx; `WARN` for 4xx.

## Universal DateTime Governance

- **DTOs:** `LocalDateTime` and `Date` are BANNED in API DTOs. Use `java.time.Instant` for absolute timestamps and `OffsetDateTime` for human-readable boundaries. Use `@JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ssXXX")` on `OffsetDateTime` fields.
- **Domain/Entities:** Store `java.time.Instant` in entity fields mapped to `TIMESTAMP WITH TIME ZONE` columns.
- **Clock Injection:** Inject `java.time.Clock` via constructor (`@RequiredArgsConstructor`). Never call `Instant.now()` or `LocalDateTime.now()` directly in business logic — always use `clock.instant()`.
- **API Serialization:** Configure `spring.jackson` to serialize `Instant` as epoch milliseconds and `OffsetDateTime` as ISO-8601 string with offset.

## Testing Strategies

| Layer            | Test Type   | Framework         | File Naming                |
| ---------------- | ----------- | ----------------- | -------------------------- |
| Domain service   | Unit        | JUnit 5 + Mockito | `UserServiceTest.java`     |
| Controller       | Slice test  | `@WebMvcTest`     | `UserControllerTest.java`  |
| Repository       | Slice test  | `@DataJpaTest`    | `UserRepositoryTest.java`  |
| Full integration | Integration | `@SpringBootTest` | `UserIntegrationTest.java` |

- Use `@WebMvcTest` and `@DataJpaTest` for focused tests — they bootstrap only the relevant context.
- Prefer `Mockito` for mocking; never use `PowerMock`.
- Use `Testcontainers` for database-dependent integration tests.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

> Stack baseline (verified September 2026): **Java 25 LTS** (latest feature release is 27; 25 is
> the LTS and the newest version inside Spring Boot 4.1's supported range), **Spring Boot 4.1.1**
> (Spring Framework 7.0.9, Jakarta EE 11, Servlet 6.1). Released 2026-08-20.
> This section assumes the DDD + hexagonal layout and the bans already declared in
> `skill-templates/spring-boot/SKILL.md` (pure `domain/`, `@RequiredArgsConstructor`,
> MapStruct `@Mapper(componentModel="spring")`, injected `Clock`, no `LocalDateTime` in DTOs,
> Flyway/Liquibase only, no `hibernate.ddl-auto=update`). The SKILL's "Currency Baseline"
> (Boot 3.x / Java 17) is stale for 2026 and should be bumped when this gate is adopted.

## Required Toolchain

| Tool | Purpose | Minimum version to pin | Install / availability note |
| --- | --- | --- | --- |
| JDK (Temurin/Adoptium) | Runtime + compiler | **25** (LTS) | Toolchain-managed; Adoptium latest LTS = 25, latest feature = 27 (non-LTS, outside Boot 4.1 support). Reject 27. |
| Gradle | Build, locking, verification | **9.7.1** | Runs on JVM 17–26; toolchain support for 25 from 9.1.0, for 26 from 9.4.0. |
| Spring Boot | Framework | **4.1.1** | `org.springframework.boot` plugin; Maven 3.6.3+ / Gradle 8.14+/9.x. Reject 4.2.0-M1 (milestone) and 3.5.x (final 3.x line). |
| Spotless | Formatting gate | **3.10.2** | Plugin id `com.diffplug.spotless`; lib is 4.10.2 (plugin numbering differs). |
| google-java-format | Java formatter engine | **1.36.1** | Resolved by Spotless; never invoke the raw CLI (see traps). |
| Error Prone | Compile-time bug/semantic lint | **2.50.0** | Must run on JDK 21+; last JDK-17 line is 2.42.0. Pin `error_prone_core`. |
| NullAway | Nullness checker (Error Prone plugin) | **0.14.1** | Runs under Error Prone; JSpecify mode enabled. |
| JSpecify | Nullness annotations | **1.0.1** | `org.jspecify:jspecify`. Boot 4 ships JSpecify annotations; `org.springframework.lang.Nullable` is gone. |
| SpotBugs | Bytecode analysis | **4.10.4** | `com.github.spotbugs:spotbugs`. |
| find-sec-bugs | SpotBugs security detectors | **1.14.0** | `com.h3xstream.findsecbugs:findsecbugs-plugin`. Maintained, low cadence. |
| ArchUnit | Layer / hexagon / cycle rules | **1.5.0** | `com.tngtech.archunit:archunit-junit5`. Winner for hexagonal enforcement. |
| Spring Modulith | Module-cycle verification (optional) | **2.1.1** | Aligns with Boot 4.1; secondary — does not enforce layer direction. |
| osv-scanner | SCA / dependency vulnerabilities | **2.6.0** | V2 beta, OSV.dev + osv-scalibr; no NVD API key needed. |
| gitleaks | Secret scanning | **8.30.1** | Feature-complete / security-patch-only; successor is Betterleaks (see Deprecated). |
| JUnit | Test framework | **6.0.3** (Boot-managed) / 6.1.3 latest | Java 17 + Kotlin 2.1 baseline; single version for Platform/Jupiter/Vintage. |
| Testcontainers | Real-dependency integration tests | **2.0.5** | Boot 4.1 manages 2.0.5; JUnit 4 support removed; classes relocated. |
| AssertJ | Fluent assertions | **3.27.7** | Boot-managed. 4.0.0-M1 is a milestone — do not pin. |
| jqwik | Property-based tests | **1.10.1** | `net.jqwik:jqwik`. |
| PIT (pitest) | Mutation testing | **1.15.0** (Gradle plugin) / 1.30.0 core | `info.solidsoft.pitest` + `org.pitest:pitest-junit5-plugin:1.2.3`. |
| JaCoCo | Coverage thresholds | **0.8.15** | Gradle built-in `jacoco` plugin; pin tool version. |
| Flyway | Schema migration + validate | **12.4.0** | Use the Boot-managed runtime version (12.4.0), NOT latest 13.7.0. |
| Liquibase | Schema migration + validate | **5.0.3** | Use Boot-managed 5.0.3, NOT latest 5.0.4. |
| MapStruct | Compile-time DTO mapping | **1.6.3** | 1.7.0 is Beta only. Add `lombok-mapstruct-binding:0.2.0`. |
| Lombok | Boilerplate (`@RequiredArgsConstructor`) | **1.18.46** | Boot-managed; latest 1.18.48. Use Boot's managed value. |
| Mockito | Mocking | **5.23.0** | Boot-managed. PowerMock is banned (dead project). |

## Strict Baseline Config

Create these files. Each line is a setting that makes the tool strict, not advisory.

**`gradle/wrapper/gradle-wrapper.properties`** — pin the wrapper and its checksum:

```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-9.7.1-bin.zip
# Fetch the expected hash: curl -s https://services.gradle.org/distributions/gradle-9.7.1-bin.zip.sha256 | cut -d' ' -f1
distributionSha256Sum=acd53f1edaf02f1a8ff99879f8a34b302661a057d9b063ae9e35b552f804d20a
```

**`gradle/libs.versions.toml`** — single source of truth for every version above. No version
literals anywhere else; this is what makes the gate AI-auditable.

**`settings.gradle.kts`** — dependency-confusion defense (repository content filtering) plus
fail-fast on repositories that are not allowlisted:

```kotlin
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral {
            content {
                includeGroupByRegex("org\\.springframework.*"); includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("org\\.jspecify"); includeGroupByRegex("net\\.jqwik")
                includeGroupByRegex("com\\.tngtech.*"); includeGroupByRegex("org\\.owasp.*")
                includeGroupByRegex("org\\.flywaydb.*"); includeGroupByRegex("org\\.liquibase.*")
                includeGroupByRegex("org\\.testcontainers.*"); includeGroupByRegex("org\\.assertj.*")
                includeGroupByRegex("org\\.mockito.*"); includeGroupByRegex("org\\.mapstruct.*")
                includeGroupByRegex("tools\\.jackson.*"); includeGroupByRegex("com\\.fasterxml.*")
                includeGroupByRegex("io\\.micrometer.*"); includeGroupByRegex("org\\.hibernate.*")
                includeGroupByRegex("org\\.junit.*")
            }
        }
        gradlePluginPortal()
    }
}
```

**`gradle/verification-metadata.xml`** — generated, then committed; build fails on any
checksum/PGP mismatch (dependency verification, the strongest supply-chain gate):

```bash
./gradlew --write-verification-metadata sha256,pgp --write-locks help
```

**`gradle.lockfile`** — dependency locking for every configuration:

```kotlin
// in build.gradle.kts
dependencyLocking { lockAllConfigurations() }
```

**`build.gradle.kts`** — compiler + static analysis + toolchain. Key strict settings:

```kotlin
java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(25)) }
}
dependencies {
    errorprone("com.google.errorprone:error_prone_core:2.50.0")
    testImplementation("com.tngtech.archunit:archunit-junit5:1.5.0")
    testImplementation("org.jspecify:jspecify:1.0.1")
}
tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.compilerArgs.addAll(listOf(
        "--release", "25", "-Xlint:all", "-Werror", "-parameters", "-proc:full",
        "-XDcompilePolicy=simple", "--should-stop=ifError=FLOW"
    ))
    options.errorprone {
        disableWarningsInGeneratedCode.set(true)
        check("NullAway", CheckSeverity.ERROR)
        option("NullAway:AnnotatedPackages", "com.company.project")
        option("NullAway:JSpecifyMode", "true")
        option("NullAway:CheckOptionalEmptiness", "true")
    }
}
tasks.withType<Test>().configureEach { useJUnitPlatform(); failFast = true }
```

**Per-tool strict settings:**

- Spotless: `spotless { java { googleJavaFormat("1.36.1").reflowLongStrings(); removeUnusedImports(); importOrder(); formatAnnotations(); forbidWildcardImports() } }` and `check` depends on `spotlessCheck`.
- Checkstyle (if kept): `checkstyle { toolVersion = "14.1.0"; maxErrors = 0; maxWarnings = 0; configFile = file("config/checkstyle/checkstyle.xml") }`.
- PMD (if kept): `pmd { toolVersion = "7.27.0"; isIgnoreFailures = false }`.
- SpotBugs: `spotbugs { toolVersion = "4.10.4"; effort = Effort.MAX; reportLevel = Confidence.LOW; excludeFilter = file("config/spotbugs/spotbugs-exclude.xml") }`; plugin `spotbugsPlugins("com.h3xstream.findsecbugs:findsecbugs-plugin:1.14.0")`.
- JaCoCo: `tasks.jacocoTestCoverageVerification { violationRules { rule { limit { counter = "LINE"; value = "COVEREDRATIO"; minimum = "0.80".toBigDecimal() } } rule { limit { counter = "BRANCH"; value = "COVEREDRATIO"; minimum = "0.70".toBigDecimal() } } } }`.
- PIT: `pitest { mutationThreshold.set(70); failWhenNoMutations.set(true); outputFormats.set(setOf("XML","HTML")); timestampedReports.set(false) }`.
- Flyway/Liquibase: `spring.flyway.validate-on-migrate=true`; `spring.liquibase.enabled=true`; run `flywayValidate` / `liquibaseValidate` as gates.
- Config validation: every `@ConfigurationProperties` class gets `@Validated` + Jakarta `@NotNull`/`@Min`; add `org.springframework.boot:spring-boot-properties-migrator` only during upgrades.
- `.gitleaks.toml`: `[extend] useDefault = true` plus an allowlist only for test fixtures.
- `osv-scanner.toml`: `[[IgnoredVulns]]` with an `id`, `ignoreUntil`, and `reason` — no bare suppressions.
- `config/archunit/archunit.properties`: `archunit.freeze.store.default.path=archunit_store` (only if using frozen rules).

**Maven fallback (only if the org mandates it):** pin **Maven 3.9.16** via
`.mvn/wrapper/maven-wrapper.properties` (`distributionUrl=...apache-maven-3.9.16-bin.zip`,
`distributionSha256Sum=PUT_MAVEN_HASH_FETCHED_VIA_CURL_FROM_SHA512_URL_ABOVE`), set `project.build.outputTimestamp` for reproducible builds, and
use `maven-enforcer-plugin:3.6.3` with `requireUpperBoundDeps`, `dependencyConvergence`,
`banDuplicatePomDependencyVersions`, `requireReleaseDeps`, and `requireMavenVersion [3.6.3,)`.
Maven cannot natively lock/verify transitive artifacts the way Gradle does, and **Maven 4.0.0 is
still 4.0.0-rc-6 (not GA)** — that is why Gradle wins.

## Mandatory Gate Order

Run in this exact order; each step fails the build (non-zero exit) before the next is allowed.

1. `./gradlew --no-daemon --version | grep -qE '^Gradle 9\.7\.1$'`
2. `./gradlew --no-daemon spotlessCheck`
3. `./gradlew --no-daemon compileJava compileTestJava`
4. `./gradlew --no-daemon test --tests 'com.company.project.ArchitectureTest'`
5. `./gradlew --no-daemon test checkstyleMain pmdMain spotbugsMain`
6. `gitleaks git --redact --exit-code 1 --report-format sarif --report-path build/gitleaks.sarif`
7. `osv-scanner scan source --licenses -r .`
8. `./gradlew --no-daemon integrationTest`
9. `./gradlew --no-daemon jacocoTestCoverageVerification`
10. `./gradlew --no-daemon pitest`
11. `./gradlew --no-daemon flywayValidate`
12. Start the app, then check readiness: `(./gradlew --no-daemon bootRun &>/tmp/bootrun.log & echo $! > /tmp/bootrun.pid; sleep 20; curl --fail --silent http://localhost:8080/actuator/health/readiness | jq -e '.status=="UP"'; rc=$?; kill $(cat /tmp/bootrun.pid); exit $rc)` — if the app cannot start locally, treat readiness as a post-deploy check and verify it against the deployed environment instead; never pass this step without a live readiness response.

Notes: step 1 also implicitly verifies the wrapper checksum. Step 3 is the Error Prone + NullAway
gate. Step 11 exits non-zero when vulnerabilities are present by default. After the first
resolution, add `--offline` to steps 2–9 in CI to forbid surprise remote changes.

## Hallucination Traps to Block

| AI failure mode | The check that catches it |
| --- | --- |
| Writes `javax.validation.*` / `javax.persistence.*` (pre-Boot-3 memory). | Compile fails; add ArchUnit `noClasses().should().dependOnClassesThat().resideInAPackage("javax..")`. |
| Restores removed Boot mock annotations `@MockBean` / `@SpyBean`. | Compile fails in Boot 4; add `forbiddenapis`/ArchUnit ban on `org.springframework.boot.test.mock.mockito.*`. Replace with `@MockitoBean` / `@MockitoSpyBean`. |
| Uses `spring-boot-starter-web` (deprecated → `spring-boot-starter-webmvc`). | `./gradlew dependencyInsight --dependency spring-boot-starter-web`; CI fails when the deprecated starter is a direct dependency. |
| Imports Jackson 2 types (`com.fasterxml.jackson.databind.*`) under Boot 4's Jackson 3. | Compile fails; ban `com.fasterxml.jackson` via `forbiddenapis`. Boot 4 uses `tools.jackson.*`. |
| Pins Flyway 13.7.0 / Liquibase 5.0.4 while Boot 4.1.1 manages 12.4.0 / 5.0.3. | `./gradlew dependencyInsight --dependency flyway-core`; `resolutionStrategy.failOnVersionConflict()` + lockfile. |
| Adds `junit-platform-runner` / JUnit 4 rules (Testcontainers 1.x style). | Dependency resolution fails (module removed in JUnit 6, JUnit 4 dropped in Testcontainers 2.0); ban `org.junit.rules.*`. |
| Field `@Autowired` injection, violating the SKILL's constructor-injection rule. | ArchUnit `noFields().should().beAnnotatedWith(Autowired.class)`. |
| `domain/` importing Spring/JPA/adapters (hexagon inversion). | ArchUnit `onionArchitecture()` / `layeredArchitecture()` + `slices().matching("..domain.(*)..").should().beFreeOfCycles()`. |
| Calls `Instant.now()` / `LocalDateTime.now()` in business logic instead of injected `Clock`. | ArchUnit `noClasses().that().resideInAPackage("..domain..").should().callMethod(Instant.class, "now")` and the same for `LocalDateTime`. |
| Puts `LocalDateTime`/`java.util.Date` in API DTOs. | ArchUnit dependency rule scoped to `..adapter.inbound.dto..`; plus `@JsonFormat` only on `OffsetDateTime`. |
| Leaves a `@Mapper` field unmapped (manual mapping creep). | MapStruct `unmappedTargetPolicy = ReportingPolicy.ERROR` fails compilation. |
| Omits `-proc:full`; JDK 21+ emits an annotation-processing warning that `-Werror` turns into a failure. | Step 3 exits non-zero until `-proc:full` is present (do not "fix" by removing `-Werror`). |
| Invokes `google-java-format` directly; JDK 16+ throws `IllegalAccessError` without `--add-exports jdk.compiler/...`. | Always run through Spotless (`spotlessCheck`); ban raw GJF in scripts. |
| Uses gitleaks `detect` / `protect` (deprecated in 8.19). | CI script asserts `gitleaks git` / `gitleaks dir`; old subcommands are hidden and unsupported. |
| Uses PMD's pre-7 CLI (`pmd -d src -R ...`). | Run `./gradlew pmdMain`; PMD 7 uses the unified `pmd check` subcommand. |
| Enables `--enable-preview` in the release build (bytecode/runtime mismatch). | Compile the preview code in a separate source set only; `javap -verbose` minor version must be 69 (Java 25), not 65535. |

## Evidence to Record

Paste each row into the task's Verification Evidence block verbatim.

| Command | Expected result | Exit code |
| --- | --- | --- |
| `./gradlew --version` | `Gradle 9.7.1`, `Launcher JVM: 25` | 0 |
| `./gradlew spotlessCheck` | `BUILD SUCCESSFUL`, 0 reformatted files | 0 |
| `./gradlew compileJava compileTestJava` | `BUILD SUCCESSFUL`, no `error:`/`warning:` lines | 0 |
| `./gradlew test --tests '*ArchitectureTest'` | all ArchUnit rules pass; count of rules > 0 | 0 |
| `./gradlew checkstyleMain pmdMain spotbugsMain` | `BUILD SUCCESSFUL`, 0 violations | 0 |
| `./gradlew jacocoTestCoverageVerification` | `BUILD SUCCESSFUL` (line ≥ 0.80, branch ≥ 0.70) | 0 |
| `./gradlew pitest` | mutation score ≥ 70%, no "no mutations found" | 0 |
| `./gradlew flywayValidate` | `Successfully validated N migrations` | 0 |
| `gitleaks git --redact --exit-code 1` | `no leaks found` | 0 |
| `osv-scanner scan source --licenses -r .` | `No issues found` | 0 |
| `curl --fail .../actuator/health/readiness` | `{"status":"UP"}` | 0 |
| `git diff --exit-code gradle/verification-metadata.xml gradle.lockfile` | no diff after `--write-locks` | 0 |

## Archived / Deprecated / Superseded in 2026 — never recommend

- **gitleaks** — author declares the project *feature complete*; future releases are
  **security patches only**, and focus has shifted to **Betterleaks**. Keep 8.30.1 pinned for now,
  but track Betterleaks as the successor.
- **OWASP Dependency-Check** — not archived, but rejected as the primary SCA gate: since 9.0.0 it
  uses the NVD API and is **extremely slow without an NVD API key**; Sonatype OSS Index now
  requires **Sonatype Guide tokens** (enforced from Sept 2025, migration through 2026) or the
  analyzer silently disables itself. Use osv-scanner instead.
- **Maven 4.0.0** — still `4.0.0-rc-6` (not GA) in Sept 2026; do not pin. Stable Maven is 3.9.16.
- **Maven 3.8.x and older** — below Boot 4's 3.6.3 floor and unsupported; pin 3.9.16 if Maven is forced.
- **Spring Boot 3.5.x** — final 3.x line; OSS support ends and only commercial support remains. Migrate to 4.1.x.
- **JUnit 4 / Vintage-based harnesses** — JUnit 6 is the baseline; `junit-platform-runner` and
  `junit-platform-jfr` are removed, `org.junit.jupiter.migrationsupport` is deprecated for removal,
  and Testcontainers 2.0 dropped JUnit 4 entirely.
- **Undertow support** — removed from Spring Boot 4 (Servlet 6.1 baseline not met).
- **Spock integration** — removed from Spring Boot 4 (no Groovy 5 support).
- **Spring Session Hazelcast / MongoDB** — no longer managed by Boot 4 (moved to vendor projects).
- **Spring Retry dependency management** — removed from Boot 4; use Spring Framework's core retry.
- **maven-compiler-plugin 4.0.0-beta-5** — prerelease; pin the Boot-managed 3.15.0 (or 3.16.0 stable).
- **AssertJ 4.0.0-M1** — milestone; pin 3.27.7.
- **MapStruct 1.7.0-Beta2** — prerelease; pin 1.6.3.

## Breaking changes that silently fail if written from memory

- **Boot 4 starter renames:** `spring-boot-starter-web` → `spring-boot-starter-webmvc`;
  `spring-boot-starter-aop` → `spring-boot-starter-aspectj`; `spring-boot-starter-oauth2-*` →
  `spring-boot-starter-security-oauth2-*`; `spring-boot-starter-web-services` →
  `spring-boot-starter-webservices`. Flyway/Liquibase now need `spring-boot-starter-flyway` /
  `spring-boot-starter-liquibase`; health needs `spring-boot-health`.
- **Jackson 3:** package `com.fasterxml.jackson` → `tools.jackson` (annotations stay under
  `com.fasterxml.jackson.annotation`); `@JsonComponent` → `@JacksonComponent`;
  `Jackson2ObjectMapperBuilderCustomizer` → `JsonMapperBuilderCustomizer`;
  `spring.jackson.read/write.*` → `spring.jackson.json.read/write.*`.
- **JSpecify:** `org.springframework.lang.Nullable` is removed; use `org.jspecify.annotations.Nullable`.
- **`@EntityScan`** moved to `org.springframework.boot.persistence.autoconfigure.EntityScan`;
  `spring.dao.exceptiontranslation.enabled` → `spring.persistence.exceptiontranslation.enabled`.
- **Hibernate:** `hibernate-jpamodelgen` → `hibernate-processor`.
- **Optional deps** are excluded from Boot 4 uber jars; set `<includeOptional>true</includeOptional>`.
- **Classic uber-jar loader** removed; delete `<loaderImplementation>CLASSIC</loaderImplementation>`.
- **Liveness/readiness probes** are enabled by default in Boot 4; disable via
  `management.endpoint.health.probes.enabled=false`.
- **Error Prone flags:** must run on **JDK 21+** (2.42.0 is the last JDK-17 line); needs
  `-XDcompilePolicy=simple`, `--should-stop=ifError=FLOW`, and on JDK 21+
  `-XDaddTypeAnnotationsToSymbol=true`; forked/toolchain compiles additionally need the
  `--add-exports jdk.compiler/...` set.
- **osv-scanner V2:** command is `osv-scanner scan source -r <dir>` (V1 was `osv-scanner -r <dir>`);
  `fix` is experimental.
- **gitleaks:** `detect` → `git`, and `--no-git`/`--source` mapping → `dir`; both changed in v8.19.
- **PMD 7:** unified CLI `pmd check` (also `pmd cpd`, `pmd ast-dump`); ruleset paths changed.
- **Spotless 4.x lib / 3.10.2 plugin:** requires Java 17; `RemoveWildcardImportsStep` renamed to
  `ForbidWildcardImportsStep`; `googleJavaFormat` default is 1.28.0 on JVM 17, 1.30.0 on 21+, and
  at least 1.30.0 on 25+.
- **Testcontainers 2.0:** classes relocated and JUnit 4 removed; when using the Boot parent, remove
  any explicit Testcontainers 1.x BOM/version override.
- **Gradle 9:** runs on JVM 17–26 only (JVM 27 unsupported); toolchain 25 requires Gradle ≥ 9.1.0.
- **maven-pmd-plugin 3.28.0** defaults to PMD 7.17.0 — override `<pmdVersion>7.27.0</pmdVersion>`.

<!-- sources -->
- https://repo1.maven.org/maven2/org/springframework/boot/spring-boot-starter-parent/maven-metadata.xml
- https://central.sonatype.com/api/internal/browse/component/versions?filter=namespace%3Aorg.springframework.boot%2Cname%3Aspring-boot-starter-parent
- https://search.maven.org/solrsearch/select?q=g:org.springframework.boot+AND+a:spring-boot-starter-parent
- https://docs.spring.io/spring-boot/system-requirements.html
- https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
- https://repo1.maven.org/maven2/org/springframework/boot/spring-boot-dependencies/4.1.1/spring-boot-dependencies-4.1.1.pom
- https://repo1.maven.org/maven2/org/springframework/boot/spring-boot-starter-parent/4.1.1/spring-boot-starter-parent-4.1.1.pom
- https://docs.gradle.org/current/userguide/compatibility.html
- https://api.github.com/repos/gradle/gradle/releases/latest
- https://services.gradle.org/distributions/gradle-9.7.1-bin.zip.sha256
- https://errorprone.info/docs/installation
- https://raw.githubusercontent.com/diffplug/spotless/main/CHANGES.md
- https://raw.githubusercontent.com/diffplug/spotless/main/plugin-maven/CHANGES.md
- https://raw.githubusercontent.com/diffplug/spotless/main/plugin-gradle/CHANGES.md
- https://raw.githubusercontent.com/gitleaks/gitleaks/master/README.md
- https://raw.githubusercontent.com/google/osv-scanner/main/README.md
- https://raw.githubusercontent.com/dependency-check/DependencyCheck/main/README.md
- https://docs.junit.org/current/release-notes/index.html
- https://docs.pmd-code.org/pmd-doc-7.7.0/pmd_release_notes_pmd7.html
- https://checkstyle.org/
- https://checkstyle.org/release-notes.html
- https://github.com/find-sec-bugs/find-sec-bugs
- https://api.adoptium.net/v3/info/available_releases
- https://docs.github.com/en/rest/rate-limit/rate-limit (GitHub rate limit documentation; replaces raw rate_limit endpoint)
- Maven Central metadata (`https://repo1.maven.org/maven2/<group-path>/<artifact>/maven-metadata.xml`) for: spotless-maven-plugin, google-java-format, palantir-java-format, checkstyle, pmd-core, spotbugs, spotbugs-maven-plugin, findsecbugs-plugin, error_prone_core, archunit-junit5, spring-modulith-api, spring-modulith-bom, jspecify, nullaway, dependency-check-maven, dependency-check-gradle, junit-jupiter, testcontainers, assertj-core, jqwik, pitest-maven, pitest-junit5-plugin, flyway-core, flyway-maven-plugin, liquibase-core, liquibase-maven-plugin, jacoco-maven-plugin, mockito-core, mapstruct, lombok, lombok-mapstruct-binding, sonar-maven-plugin, maven-pmd-plugin, maven-checkstyle-plugin, apache-maven, maven-core, maven-wrapper, maven-enforcer-plugin, maven-toolchains-plugin, maven-dependency-plugin, maven-surefire-plugin, maven-failsafe-plugin, maven-compiler-plugin, flatten-maven-plugin, gradle-pitest-plugin

## Currency Baseline

- **Spring Boot 3.x:** Baseline Java 17+ with the `jakarta.*` namespace (never `javax.*`); enable virtual threads via `spring.threads.virtual.enabled=true` for IO-bound services.
