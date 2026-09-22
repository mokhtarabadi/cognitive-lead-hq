---
name: go-hexagonal-grpc
description: Hexagonal Architecture (Ports and Adapters), gRPC, Uber Fx, and Redis caching for ultra-low latency Go backends.
---

# Go (Golang) — "Max Power" Agentic Backend Architecture

## AI Context & Token Optimization

1. **Compile-Time Dependency Injection:** Use Uber Fx. This forces explicit dependency declaration, giving the AI instant compiler feedback if a module is wired incorrectly, preventing runtime panics.
2. **gRPC Source of Truth:** Rely on `.proto` files as the absolute contract. The AI uses these to perfectly align client/server interactions.
3. **No Reflection ORMs:** Use `pgx` or `ent`. Reflection-heavy ORMs like GORM cause unpredictable runtime behaviors that confuse AI debugging workflows.

## Modern Project Initiation Guide

When scaffolding a high-performance backend (such as a sub-50ms latency Caller ID system), enforce the following strict rules to maximize AI reasoning and eliminate runtime magic:

1. **Hexagonal Architecture (Ports & Adapters):** Strictly separate the core business logic (Domain) from external concerns (gRPC, PostgreSQL, Redis). The Domain layer must have zero dependencies on external libraries.
2. **gRPC-First:** Use protocol buffers (`.proto`) as the single source of truth for all API contracts. Generate Go interfaces from proto files.
3. **Compile-Time DI:** Use **Uber Fx** or **Google Wire** for dependency injection. This forces the AI to explicitly declare dependencies, resulting in instant compile-time feedback if a dependency is missing.
4. **Caching Layer:** Implement **Redis** via the `go-redis` client for all read-heavy, low-latency lookups (e.g., spam number checks).
5. **Database:** Use **PostgreSQL** with `pgx` for raw, high-performance database interactions, or `ent` (by Facebook) if a strongly-typed ORM is required. Avoid reflection-heavy ORMs like GORM.

## Project Structure

```
project-root/
├── cmd/
│   └── server/
│       └── main.go              # Entry point, initializes Uber Fx application
├── internal/
│   ├── core/
│   │   ├── domain/              # Pure Go structs (e.g., PhoneNumber.go)
│   │   └── ports/               # Interfaces (e.g., CacheRepository, CallService)
│   ├── application/             # Use cases implementing inbound ports
│   │   └── call_service.go
│   ├── adapters/
│   │   ├── inbound/
│   │   │   └── grpc/            # gRPC handlers implementing proto generated interfaces
│   │   └── outbound/
│   │       ├── postgres/        # PostgreSQL repository implementations
│   │       └── redis/           # Redis cache repository implementations
│   └── di/                      # Uber Fx module providers
├── api/
│   └── proto/                   # .proto definition files
├── pkg/                         # Shared libraries (logging, metrics)
├── go.mod
└── Makefile                     # Protoc generation and build commands
```

## Naming Conventions

| Artifact           | Convention           | Example                     |
| ------------------ | -------------------- | --------------------------- |
| Interfaces (Ports) | Nouns ending in `er` | `CallReader`, `CacheWriter` |
| Structs            | `PascalCase`         | `CallScreeningRequest`      |
| Files              | `snake_case.go`      | `call_service.go`           |
| DI Providers       | Prefix with `New`    | `NewPostgresRepository`     |

## Architectural Patterns

### Functional Options Pattern

Use this for configuring complex structures (like external client adapters) cleanly:

```go
type Server struct { ... }
type Option func(*Server)

func WithTimeout(t time.Duration) Option {
    return func(s *Server) { s.timeout = t }
}
```

### Error Handling (Self-Healing for AI)

Never panic. Return errors explicitly. Wrap errors with context using `%w` so the AI agent reading the logs can trace the exact failure path:
`return fmt.Errorf("redis cache miss for number %s: %w", number, err)`

## Universal DateTime Governance

- **UTC Storage:** All `time.Time` fields in domain structs MUST use `time.Now().UTC()`. Banned: bare `time.Now()`.
- **Clock Interface:** Define a `Clock` interface (`Now() time.Time`) in the `core/ports` package. Default implementation uses `time.Now().UTC()`. Inject via Uber Fx. Banned: calling `time.Now()` directly in application/domain code.
- **gRPC Proto:** Use `google.protobuf.Timestamp` (always UTC) in `.proto` files. Never send raw Unix ints over gRPC unless the proto explicitly defines an `int64` field for epoch ms.
- **Redis Cache:** Store epoch ms (int64) in Redis for time-based values. Never store formatted date strings in cache keys or values.

## Testing Strategies

| Layer       | Test Type   | Framework / Tools                                     |
| ----------- | ----------- | ----------------------------------------------------- |
| Application | Unit        | `testing` + `testify/assert` + `mockery` (for ports)  |
| Adapters    | Integration | `testcontainers-go` (spin up real Redis/PG in Docker) |

- Generate mocks for all interfaces in `internal/core/ports` using `mockery`.
- AI must write table-driven tests (`[]struct`) for all core business logic.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

### Strict Baseline

> **Substitute `<MODULE_PATH>`** — replace every `<MODULE_PATH>` in this file with your module path.
> Example: `github.com/acme/svc` → run `sed -i 's|<MODULE_PATH>|github.com/acme/svc|g'` after copying.
> Keep the placeholder in the shared skill; never commit a concrete module path.

Stack: Go + Hexagonal (Ports & Adapters) + gRPC/Protobuf + Uber Fx + Redis.
Verified maintained as of **2026-09-21** (live web research; abandoned tools flagged inline).

### Required Toolchain

| Tool | Purpose | Minimum version | Activate |
| --- | --- | --- | --- |
| Go toolchain | language + `-race`, `go mod tidy -diff`, `toolchain` pinning | `go1.26.5` (must be ≥ 1.26.3 / 1.25.10 to fix CVE-2026-42501) | `go get go@1.26.5 toolchain@go1.26.5` |
| buf | proto build/lint/breaking/format/codegen | `v1.72.0` (2026-07-17) | `go install github.com/bufbuild/buf/cmd/buf@v1.72.0` |
| protoc-gen-go (remote) | Go message generation | `v1.36.11` | pin `remote: buf.build/protocolbuffers/go:v1.36.11` |
| protoc-gen-go-grpc (remote) | gRPC stubs | `v1.5.1` | pin `remote: buf.build/grpc/go:v1.5.1` |
| protovalidate-go | schema-native message validation | `v1.2.0` (module moved to `buf.build/go/protovalidate`) | `go get buf.build/go/protovalidate@v1.2.0` |
| go-grpc-middleware protovalidate interceptor | server-side validation gate | `v2.3.2` | `go get github.com/grpc-ecosystem/go-grpc-middleware/v2@v2.3.2` |
| golangci-lint | aggregated Go lint gate | `v2.13.2` (2026-08-27) | `go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2` (upstream recommends binary install) |
| gofumpt | stricter `gofmt` | `v0.11.0` (2026-07-27, Go 1.26 based) | `go install mvdan.cc/gofumpt@v0.11.0` |
| gci | deterministic import grouping | `v0.14.0` (2026-02-28) | `go install github.com/daixiang0/gci@v0.14.0` |
| NilAway | nil-panic static analysis (module plugin; not bundled) | `v0.0.0-20260728022246-eeeb1603aad0` | `.custom-gcl.yml` + `golangci-lint custom` |
| go-arch-lint | architecture boundary enforcement | `v1.15.0` (2026-05-04) — or fork `vsfedorenko/go-arch-lint/v2 v2.6.0` (2026-08-22) | `go install github.com/fe3dback/go-arch-lint@v1.15.0` |
| goleak | goroutine-leak gate | `v1.3.0` | `go get go.uber.org/goleak@v1.3.0` |
| testcontainers-go | real Redis/DB in tests | `v0.44.0` | `go get github.com/testcontainers/testcontainers-go/modules/redis@v0.44.0` |
| govulncheck | reachable-vulnerability gate | `v1.7.0` (`golang.org/x/vuln`) | `go install golang.org/x/vuln/cmd/govulncheck@v1.7.0` |
| go-redis | Redis client | `v9.7.3` | `go get github.com/redis/go-redis/v9@v9.7.3` |

**Discarded / not strict enough:** `protoc-gen-validate` (PGV) — superseded by Protovalidate; keep only if migrating. `gomodguard` (v1) — deprecated since v2.12.0, use `gomodguard_v2`. Standalone `nilaway` analyzer works but is best gated through the `custom-gcl` plugin so it shares the run.

### Strict Baseline Config

File names: `buf.yaml`, `buf.gen.yaml`, `.golangci.yml`, `.custom-gcl.yml`, `.go-arch-lint.yml`, plus `internal/platform/redis.go` and test files below.

`buf.yaml` — STANDARD + both extra strict categories, and inline comment-ignores **banned**:
```yaml
version: v2
modules:
  - path: proto
lint:
  use:
    - STANDARD
    - COMMENTS        # leading comments required on every schema element
    - UNARY_RPC        # forbidden client/server streaming (delete if you need streams)
  disallow_comment_ignores: true   # no // buf:lint:ignore escape hatch in CI
  enum_zero_value_suffix: _UNSPECIFIED
  service_suffix: Service
  rpc_allow_same_request_response: false
  rpc_allow_google_protobuf_empty_requests: false
  rpc_allow_google_protobuf_empty_responses: false
breaking:
  use:
    - FILE             # strictest: source + JSON + wire compatibility
  ignore_unstable_packages: false
```
> Note: there is **no `buf format --check`**. The strict CI check is `buf format --exit-code` (add `-d` to print the diff). `--exit-code` is what turns it into a gate.

`buf.gen.yaml` — remote plugins pinned, reproducible, managed Go package:
```yaml
version: v2
clean: true
managed:
  enabled: true
  override:
    - file_option: go_package_prefix
      value: <MODULE_PATH>/gen/go
plugins:
  - remote: buf.build/protocolbuffers/go:v1.36.11
    out: gen/go
    opt: [paths=source_relative]
  - remote: buf.build/grpc/go:v1.5.1
    out: gen/go
    opt: [paths=source_relative]
inputs:
  - directory: proto
```

`.custom-gcl.yml` — build the NilAway-enabled binary (cache it by file hash):
```yaml
version: v2.13.2
plugins:
  - module: go.uber.org/nilaway
    import: go.uber.org/nilaway/cmd/gclplugin
    version: v0.0.0-20260728022246-eeeb1603aad0
```

`.golangci.yml` — strict aggregator, hexagonal `depguard`, gRPC/Redis-context rules:
```yaml
version: "2"
run:
  timeout: 5m
  tests: true
linters:
  default: none
  enable:
    - asasalint
    - bodyclose
    - containedctx
    - contextcheck
    - copyloopvar
    - depguard
    - durationcheck
    - err113
    - errcheck
    - errchkjson
    - errorlint
    - exhaustive
    - fatcontext
    - forbidigo
    - forcetypeassert
    - funlen
    - gocognit
    - goconst
    - gocritic
    - gosec
    - govet
    - importas
    - ineffassign
    - makezero
    - mirror
    - musttag
    - nilerr
    - nilnesserr
    - noctx
    - nolintlint
    - nonamedreturns
    - paralleltest
    - prealloc
    - predeclared
    - protogetter
    - revive
    - rowserrcheck
    - spancheck
    - sqlclosecheck
    - staticcheck
    - testifylint
    - thelper
    - tparallel
    - unconvert
    - unparam
    - unused
    - usestdlibvars
    - usetesting
    - wastedassign
    - wrapcheck
  settings:
    govet:
      enable-all: true
      disable: [fieldalignment]   # alignment is an optimization, not a correctness gate
    errcheck:
      check-type-assertions: true
      check-blank: true
    gosec:
      excludes: [G104]            # errcheck already covers unchecked errors
    gocognit:
      min-complexity: 20
    funlen:
      lines: 60
      statements: 40
    nolintlint:
      require-explanation: true
      require-specific: true
      allow-unused: false
    protogetter:
      skip-generated-by: true
    wrapcheck:
      ignore-sigs:
        - "errors.New("
        - "fmt.Errorf("
    depguard:
      rules:
        domain-purity:
          files: ["**/internal/domain/**"]
          list-mode: strict
          allow:
            - $gostd
            - <MODULE_PATH>/internal/ports
            - <MODULE_PATH>/internal/domain
          deny:
            - { pkg: google.golang.org/grpc,         desc: "domain must define a port, never import transport" }
            - { pkg: google.golang.org/protobuf,     desc: "domain must not depend on generated protobuf types" }
            - { pkg: github.com/redis/go-redis/v9,   desc: "domain must define a cache port" }
            - { pkg: go.uber.org/fx,                 desc: "domain must not import the DI framework" }
            - { pkg: <MODULE_PATH>/internal/adapters, desc: "domain must not import adapters" }
        ports-purity:
          files: ["**/internal/ports/**"]
          list-mode: strict
          allow:
            - $gostd
            - <MODULE_PATH>/internal/domain
        app-no-transport:
          files: ["**/internal/app/**"]
          list-mode: strict
          allow:
            - $gostd
            - <MODULE_PATH>/internal/domain
            - <MODULE_PATH>/internal/ports
          deny:
            - { pkg: google.golang.org/grpc,       desc: "application layer is transport-agnostic" }
            - { pkg: github.com/redis/go-redis/v9, desc: "application talks to the port, not the client" }
        adapters-depend-on-ports:
          files: ["**/internal/adapters/**"]
          list-mode: strict
          allow:
            - $gostd
            - <MODULE_PATH>/internal/domain
            - <MODULE_PATH>/internal/ports
            - <MODULE_PATH>/internal/app
            - <MODULE_PATH>/internal/adapters
            - google.golang.org/grpc
            - google.golang.org/protobuf
            - github.com/redis/go-redis/v9
            - <MODULE_PATH>/gen/go
  exclusions:
    generated: strict
    warn-unused: true
    rules:
      - path: _test\.go
        linters: [funlen, gocognit, goconst, errcheck, dupl]
formatters:
  enable:
    - gofumpt
    - gci
  settings:
    gofumpt:
      extra-rules: true          # all extra rules (group-params, clothe-returns, ...)
    gci:
      sections:
        - standard
        - default
        - prefix(<MODULE_PATH>)
```

`.go-arch-lint.yml` — component graph; ports own the interfaces, adapters point inward:
```yaml
version: 3
workdir: internal
allow:
  depOnAnyVendor: false    # every third-party import must be explicitly allow-listed
  deepScan: true
excludeFiles:
  - "^.*_test\\.go$"
components:
  domain:        { in: domain/** }
  ports:         { in: ports/** }
  app:           { in: app/** }
  adapter-grpc:  { in: adapters/grpc/** }
  adapter-redis: { in: adapters/redis/** }
  platform:      { in: platform/** }
commonComponents:
  - platform
vendors:
  grpc:     { in: google.golang.org/grpc }
  protobuf: { in: google.golang.org/protobuf }
  redis:    { in: github.com/redis/go-redis/v9 }
  fx:       { in: go.uber.org/fx }
deps:
  domain:
    mayDependOn: [ports]
    mayNotDependOn: [app, adapter-grpc, adapter-redis, platform]
  ports:
    mayDependOn: [domain]
  app:
    mayDependOn: [domain, ports]
    canUse: [fx]
  adapter-grpc:
    mayDependOn: [domain, ports, app]
    canUse: [grpc, protobuf]
  adapter-redis:
    mayDependOn: [domain, ports]
    canUse: [redis]
```
> Stricter fork option (`github.com/vsfedorenko/go-arch-lint/v2`, Go DSL in `.go-arch-lint/arch.go`): `Interfaces(func(){ MustLiveWithConsumer() })` fails any port interface declared next to its implementation instead of its consumer. *(The v3 line of that fork dropped the `Interfaces` rule — pin v2.6.0 if you use it.)*

**Uber Fx gate** — `fx.ValidateApp` is the current recommended graph gate (no constructors or Invokes run, no side effects), and it detects cycles (`"cycle detected in dependency graph"`):
```go
func TestAppGraph(t *testing.T) {
	t.Parallel()
	require.NoError(t, fx.ValidateApp(
		module.Domain, module.Ports, module.App,
		module.AdapterGRPC, module.AdapterRedis, module.Platform,
	), "fx graph must build with no missing deps and no cycles")
}
```
Use `fxtest.New(t, ...)` + `app.RequireStart().RequireStop()` for lifecycle hooks, `fx.Annotate(..., fx.As(new(Port)))` so adapters bind to interfaces, and inside each `fx.Module` keep provide/annotate declarations together. `fx.ValidateApp` at app-assembly test time is the gate; startup smoke tests are not a substitute.

**Redis strictness** — explicit timeouts, bounded pool, and context-enabled deadlines:
```go
rdb := redis.NewClient(&redis.Options{
	Addr:                  cfg.Addr,
	DialTimeout:           2 * time.Second,
	ReadTimeout:           1 * time.Second,
	WriteTimeout:          1 * time.Second,
	PoolTimeout:           2 * time.Second,
	PoolSize:              50,  // max total connections in pool (strict cap — blocks hallucinated pool-field spellings)
	MinIdleConns:          10,
	ConnMaxIdleTime:       5 * time.Minute,
	ConnMaxLifetime:       30 * time.Minute,
	ContextTimeoutEnabled: true,   // honor ctx deadlines/deadlines
	MaxRetries:            2,
})
```
Do **not** rely on `ContextTimeoutEnabled` alone for blocking commands (`BLPOP`, `PubSub`) — go-redis cannot cancel socket reads mid-flight; bound those with the Redis command timeout as well. Every adapter method must take `ctx context.Context`; a custom `cache` port wrapper with mandatory ctx is the enforcement point, while `noctx`, `contextcheck`, `containedctx`, `fatcontext`, `spancheck` and `gosec` G118 catch regressions.

**Test gates:**
```go
func TestMain(m *testing.M) { goleak.VerifyTestMain(m) }

func TestGRPCService(t *testing.T) { // in-process full transport via bufconn
	t.Parallel()
	lis := bufconn.Listen(1 << 20)
	t.Cleanup(func() { lis.Close() })
	srv := grpc.NewServer(
		grpc.ChainUnaryInterceptor(
			protovalidate_middleware.UnaryServerInterceptor(mustValidator(t)),
			recoveryInterceptor,
		),
	)
	reflection.Register(srv) // asserted by a reflection test
	pb.RegisterSvcServer(srv, testServer(t))
	go func() { _ = srv.Serve(lis) }()
	t.Cleanup(srv.GracefulStop)

	conn, err := grpc.NewClient("passthrough:///bufconn",
		grpc.WithContextDialer(func(ctx context.Context, _ string) (net.Conn, error) { return lis.DialContext(ctx) }),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	require.NoError(t, err)
	t.Cleanup(func() { _ = conn.Close() })
	// ... assert InvalidArgument carries *errdetails.BadRequest for a malformed request
}

// Redis adapter test with a real server:
func newRedis(t *testing.T) *redis.Client {
	t.Helper()
	c, err := tcredis.Run(t.Context(), "redis:7")
	require.NoError(t, err)
	url, err := c.ConnectionString(t.Context())
	require.NoError(t, err)
	opt, err := redis.ParseURL(url)
	require.NoError(t, err)
	return redis.NewClient(opt)
}
```

### Mandatory Gate Order

0. `! grep -r "<MODULE_PATH>" --include="*.yml" --include="*.yaml" --include="*.go" --include="go.mod" --include="buf.gen.yaml" .` — placeholder guard: fail if any `<MODULE_PATH>` remains unsubstituted (substitute first via `sed -i 's|<MODULE_PATH>|github.com/acme/svc|g'`).
1. `go mod verify`
2. `go mod tidy -diff`            # fails if go.mod/go.sum are not tidy; never mutate in CI
3. `test -z "$(gofumpt -l .)"`    # unformatted files -> non-empty -> fail
4. `test -z "$(gci diff --section standard --section default --section 'Prefix(<MODULE_PATH>)' ./...)"`
5. `buf format --exit-code`
6. `buf lint`
7. `git fetch --unshallow origin main 2>/dev/null || git fetch --depth 0 origin main 2>/dev/null || true; buf breaking --against '.git#branch=main'`  # requires full history; CI must clone with --fetch-depth 0 or full history — the .git#branch shorthand fails on shallow clones without this fetch
8. `buf generate --clean && git --no-pager diff --exit-code -- gen/`   # generated-code drift gate
9. `test -x ./custom-gcl && [ \"$(sha256sum .custom-gcl.yml | cut -d' ' -f1)\" = \"$(cat .custom-gcl.sha 2>/dev/null || echo)\" ] || (golangci-lint custom && sha256sum .custom-gcl.yml | cut -d' ' -f1 > .custom-gcl.sha)`  # bootstrap: build NilAway binary per .custom-gcl.yml (expected ./custom-gcl), cache by file hash before lint
   `./custom-gcl run ./...`       # golangci-lint + NilAway, warnings are errors
10. `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml`
11. `go build ./...`
12. `go vet ./...`
13. `go test -race -shuffle=on -count=1 ./...`
14. `go test -race -shuffle=on -count=1 -tags=integration -covermode=atomic -coverpkg=./... -coverprofile=cover.out ./...`
15. `test "$(go tool cover -func=cover.out | tail -1 | awk '{gsub("%","",$NF); print int($NF)}')" -ge 90`
16. `govulncheck ./...`

> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI. (Step 15 is a portable 90% gate; `github.com/vladopajic/go-test-coverage` is an optional richer alternative.)

### Hallucination Traps to Block

- **Invented/renamed proto fields or changed field types** → `buf breaking --against '.git#branch=main'` with `breaking.use: [FILE]`.
- **Domain/application importing a framework (gRPC, Redis, Fx, protobuf)** → `depguard` `domain-purity` / `app-no-transport` (strict list-mode) + `go-arch-lint deps` + `mayNotDependOn`.
- **Context dropped from Redis/gRPC/DB calls** → `noctx`, `contextcheck`, `containedctx`, `gosec` G118 (`fatcontext`/`spancheck` as backup).
- **Swallowed or unwrapped errors across boundaries** → `errcheck` (`check-blank`), `errorlint`, `wrapcheck`, `err113`.
- **Fx graph with missing provides or dependency cycles** → `fx.ValidateApp(...)` test asserts `"cycle detected in dependency graph"` / missing-type errors before `fxtest` lifecycle.
- **Hand-edited stubs or stale generated code** → step 8 `buf generate --clean && git diff --exit-code -- gen/`; `protogetter` forbids direct proto field access.
- **Nil-pointer regressions in adapters/handlers** → NilAway plugin (`./custom-gcl run`).
- **Leaked goroutines / unclosed Redis or gRPC servers in tests** → `goleak.VerifyTestMain` + `t.Cleanup` on `bufconn` listener, server, container, and client.
- **Unpinned toolchain/plugins or vulnerable deps** → `go.mod toolchain` pin + pinned remote plugin tags + `govulncheck ./...` (reachable findings fail).

### Evidence to Record

Paste the exact command and the observed result for each gate:
- `go mod verify` → pass criterion: `all modules verified` (exit 0).
- `go mod tidy -diff` → pass criterion: empty output (exit 0).
- `buf lint` / `buf breaking --against '.git#branch=main'` → pass criterion: no violations printed (exit 0); include the `buf.yaml` `lint.use`/`breaking.use` values in the log.
- `buf generate --clean && git --no-pager diff --exit-code -- gen/` → pass criterion: zero diff.
- `./custom-gcl run ./...` → pass criterion: `0 issues` and exit 0 (record the custom-gcl hash + NilAway version).
- `go-arch-lint check --project-path . --arch-file .go-arch-lint.yml` → pass criterion: exit 0; paste the `go-arch-lint mapping` output showing component→package assignment.
- `go test ... -race -shuffle=on -count=1 ./...` → pass criterion: `ok` for every package and no `DATA RACE`.
- coverage → pass criterion: `go tool cover -func=cover.out | tail -1` total ≥ 90%.
- `govulncheck ./...` → pass criterion: `No vulnerabilities found` (or only non-reachable findings explicitly listed as informational).
- Fx → `fx.ValidateApp` returns `nil`; goleak → no leaked-goroutine failure.

<!-- sources -->
- https://buf.build/docs/lint/rules/ — STANDARD/BASIC/MINIMAL + COMMENTS + UNARY_RPC categories
- https://buf.build/docs/lint/usage/ — `buf.yaml` v2 lint keys, `disallow_comment_ignores`
- https://buf.build/docs/format/usage/ and https://buf.build/docs/reference/cli/buf/format/ — `--exit-code` (no `--check`)
- https://buf.build/docs/bsr/remote-plugins/ and https://buf.build/docs/bsr/remote-plugins/usage/ — pinned remote plugins, `protocolbuffers/go`, `grpc/go`
- https://github.com/bufbuild/buf/blob/main/README.md — buf v1.72.0, `breaking` FILE/PACKAGE/WIRE_JSON/WIRE
- https://protovalidate.com/quickstart/grpc-go/ — Protovalidate gRPC interceptor quickstart
- https://pkg.go.dev/buf.build/go/protovalidate@v0.14.0 (module history to v1.2.0) and https://pkg.go.dev/github.com/grpc-ecosystem/go-grpc-middleware/v2/interceptors/protovalidate
- https://github.com/golangci/golangci-lint/releases/tag/v2.13.2 and https://golangci-lint.run/docs/configuration/file/ — v2 config schema
- https://golangci-lint.run/docs/linters/configuration/ — depguard `list-mode: strict`, gosec G118/G120 codes
- https://pkg.go.dev/github.com/daixiang0/gci@v0.14.0 and https://github.com/mvdan/gofumpt/releases/tag/v0.11.0
- https://github.com/uber-go/nilaway — module plugin into golangci-lint (`.custom-gcl.yml`)
- https://github.com/fe3dback/go-arch-lint — v1.15.0 (2026-05-04); https://github.com/vsfedorenko/go-arch-lint — Go DSL fork, `MustLiveWithConsumer`, v2.6.0
- https://github.com/uber-go/fx/blob/master/app_test.go — `ValidateApp` cycle/missing-dep behavior; https://pkg.go.dev/go.uber.org/fx
- https://github.com/redis/go-redis/blob/v9.7.0/options.go and https://redis.uptrace.dev/guide/go-redis-debugging.html — timeout/pool/context semantics
- https://pkg.go.dev/github.com/testcontainers/testcontainers-go/modules/redis@v0.43.0 (v0.44.0 release train) and https://golang.testcontainers.org/modules/redis/
- https://github.com/uber-go/goleak and https://pkg.go.dev/google.golang.org/grpc/test/bufconn
- https://pkg.go.dev/golang.org/x/vuln@v1.7.0 (govulncheck) and https://tip.golang.org/doc/tutorial/govulncheck
- https://go.dev/doc/toolchain and https://nvd.nist.gov/vuln/detail/CVE-2026-42501 — toolchain pinning + required patch level
- https://go.dev/doc/devel/release — Go 1.26.x minor releases

## Currency Baseline

- **Proto toolchain:** Generate code with `buf` (`buf generate`) and validate contracts with `protovalidate` (`protoc-gen-validate` is archived); keep `.proto` files as the single source of truth.
