---
name: go-gin
description: Idiomatic Go, Clean Architecture, and Gin routing best practices
---

# Go (Gin) — Best Practices

## AI Context & Token Optimization

1. **Explicit Error Handling:** Never `panic`. Always return errors explicitly (`%w`). This creates a traceable breadcrumb trail for AI debugging tools.
2. **Interface Isolation:** Define small interfaces at the consumer level (e.g., `UserRepository`). This makes AI-driven unit testing and mocking highly reliable.
3. **Flat Handlers:** Keep Gin handlers focused strictly on JSON parsing and HTTP codes. Offload all logic to the service layer to keep files small and token-efficient.

## Project Structure

```
project/
├── cmd/                 # Application entry points
│   └── server/
│       └── main.go
├── internal/            # Private application code
│   ├── config/          # Environment loading (viper/godotenv)
│   ├── handlers/        # Gin HTTP handlers/controllers
│   ├── models/          # Domain structs and interfaces
│   ├── repository/      # Database access layer
│   └── service/         # Business logic
├── pkg/                 # Public utility libraries (optional)
├── go.mod
└── go.sum
```

## Naming Conventions

- **Files/Directories**: `snake_case` or `lowercase` (e.g., `user_repository.go`)
- **Structs/Interfaces**: `PascalCase` for exported, `camelCase` for unexported.
- **Functions**: `PascalCase` (e.g., `CreateUser`).
- **Interfaces**: Usually end in `-er` (e.g., `UserReader`, `DataWriter`).

## Architectural Patterns

- **Clean Architecture**: `Handler -> Service -> Repository`. Handlers parse JSON and return HTTP codes. Services hold business logic. Repositories handle SQL.
- **Dependency Injection**: Pass interfaces into constructors. e.g., `func NewUserService(repo models.UserRepository) *UserService`.
- **Error Handling**: Never panic. Always return `error` as the last return value. Wrap errors with context (`fmt.Errorf("failed to fetch user: %w", err)`).
- **Goroutines**: Use carefully for background tasks; always pass `context.Context` down the call chain to handle timeouts and cancellation.

## Universal DateTime Governance

- **UTC Storage:** All `time.Time` fields MUST be stored and manipulated in UTC. Use `time.Now().UTC()` or `time.Now().In(time.UTC)` exclusively. Banned: `time.Now()` without explicit `.UTC()`.
- **Clock Interface:** Define a `Clock` interface (`Now() time.Time`) and inject it into services. Never call `time.Now()` directly in business logic.
- **API Format:** Transmit datetimes as Unix epoch seconds/milliseconds (int64) or RFC3339 strings. Use `time.RFC3339Nano` for maximum precision.
- **Database Mapping:** When reading from PostgreSQL, map `TIMESTAMPTZ` columns to `time.Time`. Never use string-based timestamp columns.

## Testing Strategies

- **Framework**: Standard `testing` package + `testify` for assertions/mocks.
- **Mocking**: Generate mocks from interfaces using `mockery` or `go.uber.org/mock` for the Repository and Service layers (`github.com/golang/mock` is archived).
- **Table-Driven Tests**: Use slice-of-structs to test multiple inputs/outputs in a single test function.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

### Strict Baseline

> **Substitute `<MODULE_PATH>`** — replace every `<MODULE_PATH>` in this file with your module path.
> Example: `example.com/app` → run `sed -i 's|<MODULE_PATH>|example.com/app|g'` after copying.
> Keep the placeholder in the shared skill; never commit a concrete module path.

Static targets for Go 1.27 + Gin (Clean Architecture, REST). Versions verified against live
releases on 2026-09-21. `golines` is **discarded**: `segmentio/golines` is a public archive
(last release v0.13.0, 2025-08-21). Use `gofumpt` + `gci` + the `lll` linter instead of a
line-wrapping formatter. `swaggo/swag` v2 is still `v2.0.0-rc6` (pre-release) — pin stable
`v1.16.6`, or prefer `oapi-codegen` (contract-first) over annotation-first `swag`.

### Required Toolchain

| Tool | Purpose | Minimum version | Activate |
| --- | --- | --- | --- |
| Go toolchain | Compiler, `go vet`, `go test`, `go mod` | 1.27.0 (pin 1.27.1) | `go.mod`: `go 1.27.0` + `toolchain go1.27.1` |
| gofumpt | Strictest superset of gofmt | v0.12.0 | `go install mvdan.cc/gofumpt@v0.12.0` |
| gci | Deterministic import grouping/order | v0.14.0 | `go install github.com/daixiang0/gci@v0.14.0` |
| golangci-lint | Linter runner, v2 schema | v2.13.2 | `go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2` |
| staticcheck | Advanced static analysis (standalone) | 2026.2.1 (module v0.8.1) | `go install honnef.co/go/tools/cmd/staticcheck@v0.8.1` |
| govulncheck | Known-CVE reachability scan | v1.8.0 | `go install golang.org/x/vuln/cmd/govulncheck@v1.8.0` |
| nilaway | Inter-procedural nil-safety | commit acb8859b (2026-09-18) | `go install go.uber.org/nilaway/cmd/nilaway@acb8859b` |
| deadcode | Unreachable-function detection (RTA) | x/tools v0.50.0 | `go install golang.org/x/tools/cmd/deadcode@v0.50.0` |
| go-arch-lint | Layer/dependency-direction enforcement | v1.19.0 | `go install github.com/fe3dback/go-arch-lint@v1.19.0` |
| gotestsum | Machine-readable test gate output | v1.13.0 | `go install gotest.tools/gotestsum@v1.13.0` |
| go-test-coverage | Coverage-threshold gate | v2.19.0 | `go install github.com/vladopajic/go-test-coverage/v2@v2.19.0` |
| goleak | Goroutine-leak gate in tests | v1.3.0 | `go get go.uber.org/goleak@v1.3.0` |
| testify | Assertions / suites | v1.12.1 | `go get github.com/stretchr/testify@v1.12.1` |
| testifylint | testify misuse linter (via golangci-lint) | v1.6.4 | bundled by golangci-lint |
| validator | Gin request validation engine | v10.30.5 | `go get github.com/go-playground/validator/v10@v10.30.5` |
| gin | HTTP router/framework | v1.12.0 | `go get github.com/gin-gonic/gin@v1.12.0` |
| oapi-codegen | Contract-first OpenAPI → Go (Gin + strict) | v2.8.0 | `go install github.com/oapi-codegen/oapi-codegen/v2/cmd/oapi-codegen@v2.8.0` |
| oasdiff | Breaking-change gate between OpenAPI revisions | v1.32.1 | `go install github.com/oasdiff/oasdiff@v1.32.1` |

### Strict Baseline Config

Files: `.golangci.yml`, `.go-arch-lint.yml`, `.testcoverage.yml`, `oapi-codegen.yaml`, `go.mod` policy.

`.golangci.yml` (v2 schema — note the required `version: "2"` and the separate `formatters` block):

```yaml
version: "2"

run:
  timeout: 5m
  go: "1.27"
  modules-download-mode: readonly
  tests: true
  issues-exit-code: 2

linters:
  default: none
  enable:
    - govet
    - staticcheck
    - errcheck
    - gosec
    - revive
    - gocritic
    - exhaustive
    - bodyclose
    - noctx
    - sqlclosecheck
    - rowserrcheck
    - wrapcheck
    - errorlint
    - nilerr
    - nilnesserr
    - ineffassign
    - unused
    - misspell
    - prealloc
    - nestif
    - cyclop
    - dupl
    - goconst
    - godot
    - depguard
    - forbidigo
    - testifylint
    - nilnil
    - contextcheck
    - durationcheck
    - errname
    - thelper
    - tparallel
    - nolintlint
    - containedctx
    - unparam
    - unconvert
    - wastedassign
    - whitespace
    - copyloopvar
    - makezero
    - lll
    - paralleltest
    - usetesting
    - perfsprint
    - mirror
    - gochecknoinits
    - err113
  settings:
    govet:
      enable:
        - nilness
        - shadow
    cyclop:
      max-complexity: 10
    dupl:
      threshold: 100
    nestif:
      min-complexity: 4
    goconst:
      min-len: 2
      min-occurrences: 3
    gocritic:
      enabled-tags:
        - diagnostic
        - experimental
        - opinionated
        - performance
        - style
      disabled-checks:
        - dupImport
        - whyNoLint
    godot:
      scope: declarations
      period: true
    exhaustive:
      check:
        - switch
        - map
      default-signifies-exhaustive: false
    errorlint:
      errorf: true
      asserts: true
      comparison: true
    nilnil:
      detect-opposite: true
    testifylint:
      enable-all: true
    nolintlint:
      allow-unused: false
      require-explanation: true
      require-specific: true
    forbidigo:
      forbid:
        - pattern: ^print(ln)?$
        - pattern: ^fmt\.Print.*$
          msg: Do not commit print statements; use structured logging.
        - pattern: ^log\.(Fatal|Panic).*$
          msg: Do not terminate inside library layers; return an error.
        - pattern: ^panic$
          msg: Return an error instead of panicking.
    depguard:
      rules:
        domain-purity:
          files:
            - "**/internal/domain/**"
          list-mode: strict
          allow:
            - $gostd
            - <MODULE_PATH>/internal/domain
          deny:
            - pkg: github.com/gin-gonic/gin
              desc: domain must not depend on the HTTP delivery layer
            - pkg: net/http
              desc: domain must not depend on net/http
            - pkg: gorm.io/
              desc: domain must not depend on the ORM
            - pkg: database/sql
              desc: domain must not depend on database/sql
            - pkg: <MODULE_PATH>/internal/infrastructure
              desc: domain must not depend on infrastructure
            - pkg: <MODULE_PATH>/internal/delivery
              desc: domain must not depend on delivery
        usecase-purity:
          files:
            - "**/internal/usecase/**"
          list-mode: strict
          allow:
            - $gostd
            - <MODULE_PATH>/internal/domain
            - <MODULE_PATH>/internal/usecase
            - <MODULE_PATH>/pkg
          deny:
            - pkg: github.com/gin-gonic/gin
              desc: use cases must not depend on the delivery layer
            - pkg: net/http
              desc: use cases must not depend on net/http
            - pkg: gorm.io/
              desc: use cases must depend on repository interfaces, not the ORM
            - pkg: <MODULE_PATH>/internal/delivery
              desc: use cases must not depend on delivery
  exclusions:
    generated: strict
    warn-unused: true
    rules:
      - path: _test\.go
        linters:
          - err113
          - dupl
          - gosec
          - wrapcheck

formatters:
  enable:
    - gofumpt
    - gci
  settings:
    gofumpt:
      module-path: <MODULE_PATH>
      extra:
        group-params: true
        clothe-returns: true
        balance-calls: true
    gci:
      sections:
        - standard
        - default
        - prefix(<MODULE_PATH>)
      custom-order: true

issues:
  max-issues-per-linter: 0
  max-same-issues: 0

severity:
  default: error
```

`.go-arch-lint.yml` (executable layer direction, independent of depguard):

```yaml
version: 3
workdir: internal
allow:
  depOnAnyVendor: false
components:
  delivery:    { in: delivery/** }
  usecase:     { in: usecase/** }
  repository:  { in: infrastructure/persistence/** }
  domain:      { in: domain/** }
commonComponents:
  - domain
deps:
  delivery:
    mayDependOn:
      - usecase
  usecase:
    mayDependOn:
      - repository
  repository:
    mayDependOn:
      - domain
```

`go.mod` toolchain policy + reproducibility:

```go
module <MODULE_PATH>

go 1.27.0

toolchain go1.27.1
```

`.testcoverage.yml`:

```yaml
profile: coverage.out
threshold:
  total: 80
  package: 75
  file: 70
```

`oapi-codegen.yaml` (Gin + strict server, contract-first):

```yaml
package: api
generate:
  gin-server: true
  strict-server: true
  models: true
  embedded-spec: true
output: internal/delivery/http/api/generated.gen.go
```

Strict Gin bootstrap (validator opt-in to v11 behaviour + reject unknown JSON fields):

```go
import (
	"reflect"

	"github.com/gin-gonic/gin/binding"
	"github.com/go-playground/validator/v10"
)

func installStrictValidator() error {
	v, ok := binding.Validator.Engine().(*validator.Validate)
	if !ok {
		return errors.New("gin binding validator engine is not *validator.Validate")
	}
	v.Validate = validator.New(validator.WithRequiredStructEnabled())
	v.Validate.RegisterTagNameFunc(func(fld reflect.StructField) string {
		return fld.Tag.Get("json")
	})
	return nil
}

// Request DTOs use strict binding tags:
//   type CreateUserRequest struct {
//       Name  string `json:"name"  binding:"required,min=1,max=64"`
//       Email string `json:"email" binding:"required,email"`
//   }
```

### Mandatory Gate Order

0. `! grep -r "<MODULE_PATH>" --include="*.yml" --include="*.yaml" --include="*.go" --include="go.mod" .` — placeholder guard: fail if any `<MODULE_PATH>` remains unsubstituted (substitute first via `sed -i 's|<MODULE_PATH>|example.com/app|g'`).
1. `gofumpt -l .` (must print nothing)
2. `golangci-lint fmt --diff` (gofumpt + gci; must print nothing)
3. `go vet ./...`
4. `golangci-lint run --timeout=5m ./...`
5. `staticcheck ./...`
6. `nilaway ./...`
7. `govulncheck ./...`
8. `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml`
9. `go build ./...`
10. `go mod verify`
11. `go mod tidy -diff` (exits non-zero if go.mod/go.sum would change)
12. `gotestsum --format=testname -- -race -shuffle=on -count=1 -covermode=atomic -coverprofile=coverage.out -coverpkg=./... ./...`
13. `go-test-coverage --config .testcoverage.yml`
14. `deadcode -test ./...`
15. `if test -f api/openapi.yaml; then oapi-codegen -config oapi-codegen.yaml api/openapi.yaml && git diff --exit-code -- internal/delivery/http/api/generated.gen.go; else echo "SKIP oapi-codegen | no api/openapi.yaml present | contract-first gates not applicable | exit 0 for this step only"; fi`
16. `if test -f api/openapi.yaml && test -f api/openapi.base.yaml; then oasdiff breaking --fail-on WARN api/openapi.base.yaml api/openapi.yaml; else echo "SKIP oasdiff | no api/openapi.yaml or api/openapi.base.yaml present | breaking-change gate not applicable | exit 0 for this step only"; fi`

> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI.
> Steps 1–2 are check-only (`gofumpt -l`, `fmt --diff`) — CI never rewrites source. Regeneration
> (step 15) is the only write, and its staleness is proven by `git diff --exit-code`.

### Hallucination Traps to Block

- Unclosed HTTP response bodies from `gin`/`http.Get` -> `bodyclose`.
- Dropped errors, unwrapped cross-package errors, `%v` instead of `%w` -> `errcheck`, `errorlint`, `wrapcheck`.
- Context never propagated / stored on a struct / wrong parent context -> `noctx`, `contextcheck`, `containedctx`.
- `switch` over a domain enum silently missing a new variant -> `exhaustive` (with `default-signifies-exhaustive: false`).
- `sql.Rows`/`Stmt` leaks and unchecked `Rows.Err()` -> `sqlclosecheck`, `rowserrcheck`.
- Architectural decay: domain/usecase importing Gin, GORM, or `net/http` -> `depguard` rules + `go-arch-lint`.
- `return nil, nil`, swallowed errors, nil-map/nil-pointer derefs -> `nilnil`, `nilerr`, `nilnesserr`, `nilaway`.
- Stale generated API code or a silent breaking API change -> regenerate + `git diff --exit-code`, `oasdiff breaking --fail-on WARN`.
- Vulnerable transitive dependency introduced by an AI-suggested import -> `govulncheck` (reachability-based).
- Goroutine leaks or wrong testify assertions in generated tests -> `goleak`, `testifylint`.

### Evidence to Record

Paste the exact commands and observed pass criteria into Verification Evidence:

1. `gofumpt -l .` and `golangci-lint fmt --diff` -> **empty output**, exit 0.
2. `golangci-lint run --timeout=5m ./...` -> exit 0, `0 issues` (severity default = error, exit code 2 on any issue).
3. `staticcheck ./...` and `nilaway ./...` -> exit 0, no diagnostics.
4. `govulncheck ./...` -> `No vulnerabilities found`, exit 0.
5. `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml` -> exit 0 (no layer violations).
6. `go build ./... && go mod verify && go mod tidy -diff` -> all exit 0, no diff.
7. `gotestsum ... -- -race -shuffle=on -count=1 -coverprofile=coverage.out ...` -> `-race` clean, all tests pass; then `go-test-coverage --config .testcoverage.yml` -> exit 0 (total ≥ 80%).
8. `deadcode -test ./...` -> empty report (or documented allowlist).
9. `oapi-codegen ... && git diff --exit-code` -> no diff; `oasdiff breaking --fail-on WARN` -> exit 0.
10. Capture the toolchain prove-out: `go version` = `go1.27.1`, `GOTOOLCHAIN=local` set in CI (fail rather than silently download a different toolchain).

<!-- sources -->
- https://golangci-lint.run/docs/configuration/file/
- https://golangci-lint.run/docs/linters/
- https://golangci-lint.run/docs/configuration/cli/
- https://github.com/golangci/golangci-lint/releases/tag/v2.13.2
- https://github.com/golangci/golangci-lint/blob/main/.golangci.yml
- https://github.com/golangci/golangci-lint/blob/main/.golangci.reference.yml
- https://github.com/mvdan/gofumpt
- https://github.com/daixiang0/gci
- https://github.com/segmentio/golines
- https://github.com/dominikh/go-tools
- https://github.com/golang/vuln
- https://github.com/uber-go/nilaway
- https://pkg.go.dev/golang.org/x/tools/cmd/deadcode
- https://github.com/fe3dback/go-arch-lint
- https://github.com/gotestyourself/gotestsum
- https://github.com/vladopajic/go-test-coverage
- https://github.com/uber-go/goleak
- https://github.com/Antonboom/testifylint
- https://go.dev/doc/toolchain
- https://github.com/oapi-codegen/oapi-codegen
- https://github.com/oasdiff/oasdiff
- https://github.com/go-playground/validator
- https://github.com/gin-gonic/gin

## Currency Baseline

- **Standard observability:** Prefer stdlib `log/slog` for structured logging; pin a recent Go toolchain in `go.mod`.
