---
name: python-fastapi
description: AI-Optimized FastAPI architecture with strict Pydantic V2 schemas and modular routing.
---

# FastAPI (Python) — AI-Native Scaffolding

## AI Context & Token Optimization

1. **Strict Type Hinting:** Python's dynamic nature causes AI hallucinations. You MUST use strict type hints (`-> dict`, `: str`) on every single function, argument, and return type.
2. **Pydantic V2 First:** Lean heavily on Pydantic. It is the most token-efficient way for an AI to understand data structures.
3. **Low Boilerplate:** FastAPI is chosen for its minimal boilerplate. Do not over-engineer abstractions. Keep dependency injection (`Depends()`) simple and localized.

## Project Structure

```
app/
├── api/                 # API routers (v1/users.py)
├── core/                # config.py (pydantic-settings BaseSettings)
├── db/                  # Database session and setup (Supabase/Postgres)
├── models/              # SQLAlchemy 2.0 Typed Models
├── schemas/             # Pydantic V2 Models (DTOs)
├── services/            # Business logic
└── main.py              # FastAPI instance
```

## Naming Conventions

| Artifact          | Convention   | Example           |
| ----------------- | ------------ | ----------------- |
| Files/Directories | `snake_case` | `user_service.py` |
| Classes           | `PascalCase` | `UserService`     |
| Functions/Methods | `snake_case` | `get_user_by_id`  |
| Variables         | `snake_case` | `current_user`    |

## Architectural Patterns

**Dependency Injection:** Use `Depends()` for database sessions (`get_db`) and authentication (`get_current_user`). Never instantiate global DB sessions in routers.
**ORM to Schema Separation:** Never return SQLAlchemy models directly from endpoints. Always return Pydantic schemas to ensure data validation and hide sensitive fields.
**Async First:** Use `async def` for endpoints and asynchronous database drivers (e.g., `asyncpg` for SQLAlchemy) to maximize throughput.

## Hexagonal Architecture (Ports & Adapters)

Ported from the Go blueprint (`go-hexagonal-grpc`). Same rules, Python idioms:

**Zero-Framework Core:** `core/` (entities + ports + use cases) imports NOTHING from FastAPI, SQLAlchemy, or Pydantic. Domain entities are plain dataclasses. Violation fails review.
**Ports as Protocols:** define inbound/outbound ports as `typing.Protocol` classes in `core/ports/` (`UserRepository`, `Clock`). Use cases implement inbound ports; adapters implement outbound ports.
**Layout:** `core/{domain,ports/inbound,ports/outbound,use_cases}` + `adapters/{inbound/api,outbound/postgres}` + `container.py` composition root (`dependency-injector` package or explicit factory functions). FastAPI routers depend ONLY on inbound port Protocols, injected via `Depends()`.
**Clock Abstraction:** reuse the `ClockProvider` above as the `Clock` outbound port. Banned: `datetime.now()` in core.
**Testing:** use-case unit tests with faked Protocol implementations (pytest); adapter integration tests with testcontainers (real Postgres).

## Universal DateTime Governance

- **Timezone-Aware Datetimes:** Use `datetime.now(timezone.utc)` exclusively. Banned: bare `datetime.now()` and `datetime.utcnow()` which produce naive datetimes.
- **Pydantic Schemas:** Use `AwareDatetime` (Pydantic V2) for all datetime fields in request/response schemas. Never use `datetime` without timezone info.
- **Clock Abstraction:** Define a `ClockProvider` class with a `def now() -> datetime` method. Inject it via `Depends()` in service layers. Banned: direct `datetime.now()` calls in domain/business logic.
- **API Format:** Transmit datetimes as ISO-8601 with offset (`2026-07-23T14:30:00+00:00`) or Unix epoch milliseconds (int).

## Testing Strategies

| Layer        | Test Type   | Framework                  | File Naming            |
| ------------ | ----------- | -------------------------- | ---------------------- |
| Service      | Unit        | Pytest                     | `test_user_service.py` |
| Route / View | Integration | Pytest + httpx AsyncClient | `test_users.py`        |


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

> Scope: FastAPI + Pydantic V2, async-first, hexagonal ports/adapters, `Clock` abstraction,
> timezone-aware datetimes (the stack already mandated by `skill-templates/python-fastapi/SKILL.md`).
> All versions verified **2026-09** against PyPI JSON and GitHub Releases API; Python target is **3.14**
> (3.14.7 current stable; 3.15.0 final lands Oct 2026 — do NOT pin 3.15 yet).

## Required Toolchain

| Tool                                       | Purpose                                          | Minimum version to pin | Install / availability note                                    |
| ------------------------------------------ | ------------------------------------------------ | ---------------------- | -------------------------------------------------------------- |
| `python`                                   | Runtime + toolchain pin                          | **3.14.7**             | `.python-version` = `3.14`; `requires-python = ">=3.14"`       |
| `uv`                                       | Env, lockfile, build, native audit               | **0.12.17**            | standalone installer (`astral.sh/uv`); `uv self update`        |
| `ruff`                                     | Format + lint + import sort + bandit subset      | **0.16.8**             | `uv add --dev ruff==0.16.8` (single binary, 900+ rules)        |
| `basedpyright`                             | Primary strict type checker                      | **1.40.1**             | `uv add --dev basedpyright==1.40.1` (PyPI wrapper, no Node)    |
| `mypy`                                     | Secondary checker (Pydantic plugin support)      | **2.3.1**              | `uv add --dev mypy==2.3.1`                                     |
| `semgrep`                                  | SAST / security scanning (cross-file)            | **1.177.0**            | `uv add --dev semgrep==1.177.0` (or `uvx semgrep`)             |
| `pip-audit`                                | Vulnerability audit fallback                     | **2.10.1**             | `uvx pip-audit` (only when `uv audit` unavailable)             |
| `deptry`                                   | Unused / missing / transitive dependency hygiene | **0.25.1**             | `uv add --dev deptry==0.25.1` (org moved to `osprey-oss`)      |
| `vulture`                                  | Dead-code detection                              | **2.16**               | `uv add --dev vulture==2.16`                                   |
| `import-linter`                            | Architecture / import-boundary enforcement       | **2.15**               | `uv add --dev import-linter==2.15`                             |
| `pytest`                                   | Test runner                                      | **9.1.1**              | `uv add --dev pytest==9.1.1`                                   |
| `pytest-cov` / `coverage`                  | Coverage + threshold gate                        | **7.1.0 / 7.16.1**     | `uv add --dev pytest-cov==7.1.0`                               |
| `pytest-randomly` / `pytest-xdist`         | Order shuffling + parallel flake surfacing       | **5.0.0 / 3.8.0**      | `uv add --dev pytest-randomly==5.0.0 pytest-xdist==3.8.0`     |
| `openapi-spec-validator`                   | Route / OpenAPI-map integrity                    | **0.9.0**              | `uv add --dev openapi-spec-validator==0.9.0`                   |
| `alembic`                                  | Migration drift check                            | **1.20.0**             | `uv add --dev alembic==1.20.0`                                 |
| `pydantic` / `pydantic-settings` / `fastapi` | Runtime contracts (DTOs, config, routes)      | **2.13.5 / 2.15.0 / 0.141.1** | `uv add pydantic==2.13.5 pydantic-settings==2.15.0 fastapi==0.141.1` |

**Type-checker verdict (2026).** Winner = **basedpyright** (strictest defaults: `typeCheckingMode = "all"`,
`pythonPlatform = "All"`, and **exit code 3 on invalid config**, so a mistyped key can never silently
downgrade you). Rejected **ty 0.0.82** — still `0.0.x` beta with "breaking changes … between any two
versions" (unusable for a reproducible gate). Rejected **pyright 1.1.414** — it silently ignores unknown
config keys and keeps checking at `standard` (basedpyright fixes exactly this). Keep **mypy 2.3.1** as a
secondary step only because the **Pydantic mypy plugin is still shipped and current** (`plugins =
["pydantic.mypy"]`) and adds `init_typed` / `init_forbid_extra` / `pydantic-field` checks that no other
checker offers. **pytype** (archived 2026-03-16) and **pyre-check** (archived 2026-06-26) are dead — never
recommend them.

**Lint verdict.** Winner = **ruff** (replaces flake8 + Black + isort + pyupgrade + pydocstyle + flake8-bandit).
Rejected standalone **Black 26.5.1**, **isort 9.0.1**, **flake8 7.3.0**, **pyupgrade 3.21.2** — all still
maintained but redundant. **pylint 4.0.8** rejected for this stack (ruff's `PL` rules cover it; pylint adds a
second config surface for no extra signal here).

**Security verdict.** Winner = **semgrep** (cross-file, custom `semgrep.yaml`, SARIF). **Bandit 1.9.4** is
deliberately *not* a required tool because ruff's `S` rules re-implement flake8-bandit; keep it only as an
optional belt-and-suspenders step (`-lll`).

## Strict Baseline Config

Create these files (all verified keys/options as of 2026-09):

- **`pyproject.toml`** — the single source of truth for every tool below.
- **`.python-version`** — contents: `3.14`
- **`uv.lock`** — committed; never regenerated in CI.
- **`semgrep.yaml`** — local rules (banned `datetime.utcnow`, `@app.on_event`, `pydantic.v1`, etc.).
- **`whitelist.py`** — vulture false-positive allowlist (generated via `--make-whitelist`).
- **`alembic.ini`** + `migrations/env.py` — with `target_metadata = Base.metadata`.
- **`.pre-commit-config.yaml`** — optional; mirrors the gate order locally.
- **`.github/workflows/gates.yml`** — optional CI wrapper.

Exact strict keys:

```toml
# ---------------- ruff: format + lint + imports + datetime + bandit subset ----------------
[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = ["ALL"]                       # 900+ rules; see [tool.ruff.lint] ignore below
ignore = ["D203", "D213", "COM812", "ISC001", "ANN401"]  # conflicting / style-only only
fixable = ["ALL"]
unfixable = ["F401"]                   # never let autofix silently drop imports

[tool.ruff.lint.flake8-annotations]
mypy-init-return = true
allow-star-arg-any = false

[tool.ruff.lint.isort]
known-first-party = ["app", "core"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "PLR2004", "ANN"]

[tool.ruff.format]
quote-style = "double"

# ---------------- basedpyright: the strict gate (exit 3 = bad config) ---------------------
[tool.basedpyright]
typeCheckingMode = "all"               # basedpyright default; strictest rule set
pythonVersion = "3.14"
pythonPlatform = "All"
include = ["app", "core", "adapters"]
strict = ["app", "core", "adapters"]
enableTypeIgnoreComments = false       # force `basedpyright: ignore`, which is provenance-clean
reportMissingTypeStubs = "error"
reportUnnecessaryTypeIgnoreComment = "error"
reportPrivateUsage = "error"
reportUnusedImport = "error"
reportUnusedCallResult = "error"

# ---------------- mypy: Pydantic-aware secondary check --------------------------------
[tool.mypy]
strict = true
python_version = "3.14"
plugins = ["pydantic.mypy"]
warn_unused_configs = true
warn_unreachable = true
warn_unused_ignores = true
disallow_any_explicit = true           # requires init_typed + init_forbid_extra below
enable_error_code = ["deprecated"]     # PEP 702 warnings become errors
follow_imports = "silent"

[tool.pydantic-mypy]
init_typed = true
init_forbid_extra = true
warn_required_dynamic_aliases = true

# ---------------- import-linter: hexagonal layer boundaries ---------------------------
[tool.importlinter]
root_packages = ["app", "core", "adapters"]

[[tool.importlinter.contracts]]
name = "Hexagon: core imports no framework"
type = "forbidden"
source_modules = ["core"]
forbidden_modules = ["fastapi", "starlette", "sqlalchemy", "pydantic", "adapters", "app"]

[[tool.importlinter.contracts]]
name = "Layered: app -> adapters -> core"
type = "layers"
layers = ["app", "adapters", "core"]

[[tool.importlinter.contracts]]
name = "Ports are independent"
type = "independence"
modules = ["core.domain", "core.ports.inbound", "core.ports.outbound"]

# ---------------- dependency hygiene -----------------------------------------------
[tool.deptry]
extend_exclude = ["alembic/versions", "tests"]
known_first_party = ["app", "core", "adapters"]
# NOTE: --pep621-dev-dependency-groups is DEPRECATED (use optional_dependencies_dev_groups)
optional_dependencies_dev_groups = ["test", "dev"]

# ---------------- dead code ---------------------------------------------------------
[tool.vulture]
min_confidence = 100
paths = ["app", "core", "adapters", "whitelist.py"]
sort_by_size = true

# ---------------- pytest 9 strict mode (config keys, NOT addopts flags) ---------------
[tool.pytest]
minversion = "9.0"
strict = true                          # enables strict_config/markers/parametrization_ids/xfail
testpaths = ["tests"]
filterwarnings = ["error"]             # DeprecationWarning -> failure (kills FastAPI/Pydantic v1 drift)
addopts = [
  "--cov=app", "--cov=core", "--cov-branch",
  "--cov-fail-under=90",
  "-n", "auto", "--dist=loadscope",
  "--randomly-seed=random",
  "-ra", "-q",
]

[tool.coverage.run]
branch = true
source = ["app", "core", "adapters"]

[tool.coverage.report]
fail_under = 90
show_missing = true
exclude_also = ["if TYPE_CHECKING:", "raise NotImplementedError", "@(abc\\.)?abstractmethod"]

# ---------------- uv: malware + audit config -----------------------------------------
[tool.uv]
audit.malware-check = true             # refuse to install a locked malware advisory

# ---------------- optional bandit (belt-and-suspenders) -------------------------------
[tool.bandit]
exclude_dirs = ["tests", "alembic/versions"]
```

Runtime contract keys the code itself must carry:

```python
# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="forbid", validate_default=True, env_nested_delimiter="__")
```

Routes must pass `operation_id=` explicitly (FastAPI does not guarantee uniqueness) and the
`Clock` outbound port must be the only source of "now".

## Mandatory Gate Order

Run in this exact order; every step must exit `0` or the gate fails:

1. `uv lock --check`
2. `uv sync --locked --no-dev && uv sync --locked`
3. `uv run ruff format --check .`
4. `uv run ruff check --output-format=concise .`
5. `uv run basedpyright`
6. `uv run mypy app core adapters -n auto`
7. `uv run lint-imports`
8. `uv run deptry .`
9. `uv run vulture`
10. `uv run semgrep scan --config p/python --config p/owasp-top-ten --config semgrep.yaml --error --sarif --output semgrep.sarif .`
11. `uv audit`
12. `uv run python -c "import openapi_spec_validator as v; from app.main import app; s=app.openapi(); ids=[o['operationId'] for p in s['paths'].values() for o in p.values() if isinstance(o,dict) and 'operationId' in o]; assert len(ids)==len(set(ids)), f'duplicate operationId: {ids}'; v.validate(s); print(f'openapi OK: {len(s[\"paths\"])} paths')"`
13. `uv run python -c "from app.core.config import Settings; Settings(); print('settings OK')"`
14. `uv run alembic check`
15. `uv run pytest`
16. _(optional, only if a flake is suspected, never in the gate)_ `uvx --from=pytest-rerunfailures pytest --reruns 3 --only-rerun=FlakyError`

## Hallucination Traps to Block

| #  | AI failure mode (stack-specific)                                                             | Check that catches it                                                        |
| -- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 1  | `datetime.now()` / `datetime.utcnow()` in domain code (naive datetimes)                       | ruff `DTZ005` / `DTZ003`; `Clock` port + import-linter `forbidden` on core    |
| 2  | `@app.on_event("startup")` instead of `lifespan`                                              | `filterwarnings = ["error"]` (FastAPI emits `FastAPIDeprecationWarning`)      |
| 3  | `from pydantic import BaseSettings` / `validator` / `.dict()` (V1 API)                         | basedpyright `reportAttributeAccessIssue`; `filterwarnings=error`; ruff `UP`  |
| 4  | `core/` importing FastAPI/SQLAlchemy/Pydantic (hexagon broken)                                | `lint-imports` forbidden contract (compile-time, before tests)                |
| 5  | Unused `# type: ignore` left behind after a refactor                                           | basedpyright `reportUnnecessaryTypeIgnoreComment`; mypy `warn_unused_ignores`; ruff `RUF100` |
| 6  | `Any` leakage from untyped deps or `**kwargs`                                                  | basedpyright `reportAny`/`reportUnknown*` (`typeCheckingMode="all"`); mypy `disallow_any_explicit` |
| 7  | Returning SQLAlchemy models directly from endpoints                                            | `response_model=` + basedpyright arg-type; add a test asserting the schema type |
| 8  | Duplicate / missing `operation_id` (client-codegen breakage)                                   | gate step 12 (uniqueness assert + `openapi-spec-validator`)                    |
| 9  | Hallucinated FastAPI/Starlette kwargs (`response_model` on wrong decorator, bogus params)      | basedpyright `reportCallIssue`; pydantic mypy plugin (`call-arg`)               |
| 10 | Missing/misspelled env var or `extra` field silently accepted                                  | `SettingsConfigDict(extra="forbid")` + gate step 13                            |
| 11 | Stale `uv.lock` / version guessed from memory                                                  | `uv lock --check` + `uv sync --locked` (fails on drift)                        |
| 12 | A known-vulnerable or yanked/malware locked dependency                                         | `uv audit` (OSV + adverse-status) and `audit.malware-check = true`             |
| 13 | Unused or shadow dependency (`psycopg2` added but `asyncpg` used, or vice versa)               | `deptry` (DEP001 missing, DEP002 unused, DEP003 transitive, DEP004 dev)        |
| 14 | Dead branch / unreachable function kept "for later"                                            | `vulture --min-confidence 100`                                                 |
| 15 | Sync `psycopg2`/`requests` call inside `async def` (blocks the loop)                           | ruff `ASYNC` rules; `deptry` flags undeclared driver                           |
| 16 | Model change committed without an Alembic migration                                            | `alembic check` (non-zero when new upgrade ops exist)                           |
| 17 | `--strict-markers` / `--strict-config` written into pytest `addopts` (silently ignored in pytest 9) | Use `strict = true` config key; keep flags out of `addopts`              |
| 18 | `# noqa` written with a rule ID that no longer fires                                           | ruff `RUF100`                                                                  |
| 19 | Coverage threshold set in the wrong place (`[tool.coverage] fail_under` vs `--cov-fail-under`) | Gate uses `--cov-fail-under=90`; `[tool.coverage.report] fail_under` mirrors it |
| 20 | Pydantic `AwareDatetime` omitted on a datetime field                                          | basedpyright type mismatch on assignment; mypy strict + pydantic plugin        |

## Evidence to Record

Paste into the task's Verification Evidence block:

| Exact command | Expected result | Exit code |
| --- | --- | --- |
| `uv --version` | `uv 0.12.17` or newer | `0` |
| `uv lock --check` | no output / "lockfile is up-to-date" | `0` |
| `uv sync --locked` | `Resolved …` + `Audited …` | `0` |
| `uv run ruff format --check .` | `N files already formatted` | `0` |
| `uv run ruff check .` | `All checks passed!` | `0` |
| `uv run basedpyright` | `0 errors, 0 warnings, 0 notes` | `0` |
| `uv run mypy app core adapters -n auto` | `Success: no issues found in N source files` | `0` |
| `uv run lint-imports` | `Contracts: N kept, 0 broken.` | `0` |
| `uv run deptry .` | `Success! No dependency issues found.` | `0` |
| `uv run vulture` | no output (with `whitelist.py` scanned) | `0` |
| `uv run semgrep scan --config p/python --config semgrep.yaml --error .` | `Ran N rules … 0 findings` | `0` |
| `uv audit` | `No known vulnerabilities found` | `0` |
| OpenAPI one-liner (gate step 12) | `openapi OK: N paths` | `0` |
| `uv run python -c "from app.core.config import Settings; Settings()"` | `settings OK` | `0` |
| `uv run alembic check` | `No new upgrade operations detected.` | `0` |
| `uv run pytest` | `N passed` and `Required test coverage of 90% reached` | `0` |
| Negative control: `uv run python -c "from datetime import datetime; print(datetime.utcnow())"` | ruff/pre-commit rejects the line; if run raw, Python emits `DeprecationWarning` | `1` under gate |

<!-- sources -->
- https://pypi.org/pypi/ruff/json, https://pypi.org/pypi/basedpyright/json, https://pypi.org/pypi/mypy/json, https://pypi.org/pypi/ty/json, https://pypi.org/pypi/pyright/json, https://pypi.org/pypi/uv/json, https://pypi.org/pypi/semgrep/json, https://pypi.org/pypi/bandit/json, https://pypi.org/pypi/pip-audit/json, https://pypi.org/pypi/deptry/json, https://pypi.org/pypi/vulture/json, https://pypi.org/pypi/import-linter/json, https://pypi.org/pypi/pytest/json, https://pypi.org/pypi/pytest-cov/json, https://pypi.org/pypi/coverage/json, https://pypi.org/pypi/openapi-spec-validator/json, https://pypi.org/pypi/schemathesis/json, https://pypi.org/pypi/pre-commit/json, https://pypi.org/pypi/pydantic/json, https://pypi.org/pypi/pydantic-settings/json, https://pypi.org/pypi/fastapi/json, https://pypi.org/pypi/alembic/json
- https://api.github.com/repos/astral-sh/ruff, https://api.github.com/repos/astral-sh/ty, https://api.github.com/repos/python/mypy, https://api.github.com/repos/microsoft/pyright, https://api.github.com/repos/DetachHead/basedpyright, https://api.github.com/repos/PyCQA/bandit, https://api.github.com/repos/semgrep/semgrep, https://api.github.com/repos/pypa/pip-audit, https://api.github.com/repos/astral-sh/uv, https://api.github.com/repos/pytest-dev/pytest, https://api.github.com/repos/jendrikseipp/vulture, https://api.github.com/repos/seddonym/import-linter, https://api.github.com/repos/google/pytype, https://api.github.com/repos/facebook/pyre-check, https://api.github.com/repos/psf/black, https://api.github.com/repos/PyCQA/flake8
- https://docs.astral.sh/ruff/linter, https://docs.astral.sh/ruff/tutorial, https://docs.astral.sh/ruff/editors/setup, https://docs.astral.sh/ruff/settings
- https://docs.astral.sh/ty, https://docs.astral.sh/ty/type-checking, https://docs.astral.sh/ty/rules, https://docs.astral.sh/ty/reference/configuration/, https://docs.astral.sh/ty/reference/exit-codes/, https://astral.sh/blog/ty, https://github.com/astral-sh/ty/milestone/4
- https://docs.astral.sh/uv/concepts/projects/sync, https://docs.astral.sh/uv/reference/cli, https://astral.sh/blog/uv-audit, https://github.com/astral-sh/uv/issues/9189, https://pypi.org/project/uv-secure, https://github.com/owenlamont/uv-secure
- https://mypy-lang.org/, https://mypy.readthedocs.io/en/stable/changelog.html, https://github.com/python/mypy/issues/20726, https://github.com/python/mypy/blob/master/docs/source/command_line.rst, https://mypy-lang.blogspot.com/2026/05/mypy-20-relased.html, https://pydevtools.com/blog/mypy-2-0-parallel-type-checking
- https://docs.basedpyright.com/v1.27.0/usage/mypy-comparison, https://docs.basedpyright.com/v1.24.0/configuration/config-files, https://pypi.org/project/basedpyright/1.18.0, https://github.com/microsoft/pyright/blob/main/docs/configuration.md
- https://docs.pydantic.dev/latest/integrations/mypy/
- https://pytest.org/en/stable/changelog.html, https://docs.pytest.org/en/stable/reference/customize.html, https://github.com/pytest-dev/pytest/releases/tag/9.0.0, https://github.com/pytest-dev/pytest/issues/14442, https://docs.pytest.org/en/stable/how-to/mark.html
- https://coverage.readthedocs.io/en/latest/config.html
- https://deptry.com/usage/, https://github.com/osprey-oss/deptry
- https://raw.githubusercontent.com/jendrikseipp/vulture/main/README.md
- https://import-linter.readthedocs.io/en/stable/, https://import-linter.readthedocs.io/en/stable/contract_types/layers/
- https://bandit.readthedocs.io/en/latest/man/bandit.html, https://bandit.readthedocs.io/en/latest/config.html, https://bandit.readthedocs.io/en/latest/start.html
- https://raw.githubusercontent.com/pypa/pip-audit/main/README.md, https://pypi.org/project/pip-audit
- https://semgrep.dev/docs/cli-reference, https://docs.semgrep.dev/semgrep-ci/sample-ci-configs, https://semgrep.dev/docs/running-rules, https://docs.semgrep.dev/running-rules, https://github.com/semgrep/semgrep/blob/develop/.pre-commit-hooks.yaml
- https://alembic.sqlalchemy.org/en/latest/autogenerate.html
- https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration, https://github.com/fastapi/fastapi/blob/master/docs/en/docs/how-to/extending-openapi.md
- https://www.python.org/downloads/, https://docs.python.org/3.15/whatsnew/3.15.html, https://www.herodevs.com/blog-posts/python-end-of-life-dates-every-versions-support-timeline
- https://pydevtools.com/handbook/explanation/ruff-complete-guide/, https://pydevtools.com/handbook/how-to/how-to-use-a-uv-lockfile-for-reproducible-python-environments/, https://pydevtools.com/handbook/how-to/how-to-scan-python-dependencies-for-vulnerabilities
- https://libraries.io/pypi/pip-audit, https://github.com/tbrandenburg/flowrite/issues/23

## Currency Baseline

- **Settings + lifespan:** Import `BaseSettings` from `pydantic-settings` (not `pydantic`); manage startup/shutdown with the `lifespan` context manager (`@app.on_event` is deprecated).
