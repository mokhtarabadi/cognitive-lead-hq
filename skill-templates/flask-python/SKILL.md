---
name: flask-python
description: Application Factory, Blueprints, SQLAlchemy, and config separation for Flask
---

# Flask (Python) — Best Practices

## Project Structure

```
project/
├── app/
│   ├── __init__.py           # Application Factory (create_app)
│   ├── config.py             # Configuration classes (Dev, Prod, Test)
│   ├── extensions.py         # Flask extensions (db, migrate, login)
│   ├── blueprints/
│   │   ├── auth/
│   │   │   ├── __init__.py   # Blueprint creation
│   │   │   ├── routes.py     # Route definitions
│   │   │   └── forms.py      # WTForms schemas
│   │   └── users/
│   │       ├── __init__.py
│   │       └── routes.py
│   ├── models/               # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/             # Business logic
│   │   └── user_service.py
│   └── templates/            # Jinja2 templates (if server-rendered)
├── tests/
│   ├── conftest.py           # Pytest fixtures (app, client, db)
│   ├── test_auth.py
│   └── test_users.py
├── .env                      # Local environment variables
├── requirements.txt
└── run.py                    # Entry point
```

## Naming Conventions

| Artifact              | Convention          | Example           |
| --------------------- | ------------------- | ----------------- |
| Files/Directories     | `snake_case`        | `user_service.py` |
| Classes               | `PascalCase`        | `UserService`     |
| Functions/Methods     | `snake_case`        | `get_user_by_id`  |
| Variables             | `snake_case`        | `current_user`    |
| Blueprint names       | plural nouns        | `users`           |
| Route prefixes        | plural `kebab-case` | `/api/users`      |
| Environment variables | `UPPER_SNAKE_CASE`  | `DATABASE_URL`    |

## Architectural Patterns

### Application Factory Pattern

Use `create_app(config_name)` in `app/__init__.py` to build the Flask instance. This allows creating different app instances for development, testing, and production without global state.

```python
def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_map[config_name])
    register_extensions(app)
    register_blueprints(app)
    return app
```

### Blueprints for Routing

Organize routes into Blueprints. Each feature domain gets its own Blueprint. Never define routes directly on the `app` instance outside of a Blueprint.

```python
users_bp = Blueprint("users", __name__, url_prefix="/api/users")
```

### SQLAlchemy ORM

- Define models in a dedicated `models/` package, not in `routes.py`.
- Use `backref` sparingly — prefer explicit `relationship` definitions.
- Use Alembic (via Flask-Migrate) for all schema migrations; never hand-write DDL.
- Keep query logic in dedicated repository functions or service methods — never inline queries in route handlers.

### Configuration Separation

Create a `config.py` with at least three classes: `Config` (base), `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`. Load the correct one via environment variable or default.

### Virtual Environment Rules

- Always use a virtual environment (venv or pipenv).
- Pin dependency versions in `requirements.txt`.
- Never commit `.venv/` or `__pycache__/` to version control.

## Universal DateTime Governance

- **Timezone-Aware Datetimes:** Use `datetime.now(timezone.utc)` exclusively. Banned: bare `datetime.now()` and `datetime.utcnow()`.
- **Clock Abstraction:** Create a `ClockProvider` class (`def now() -> datetime`) injected into services. Never call `datetime.now()` directly in business logic.
- **API Format:** Transmit datetimes as ISO-8601 with offset (`2026-07-23T14:30:00+00:00`) or Unix epoch milliseconds.

## Testing Strategies

| Layer        | Test Type   | Framework                  | File Naming            |
| ------------ | ----------- | -------------------------- | ---------------------- |
| Service      | Unit        | Pytest                     | `test_user_service.py` |
| Route / View | Integration | Pytest + Flask test client | `test_auth_routes.py`  |
| Model        | Unit        | Pytest                     | `test_user_model.py`   |

- Use `pytest` as the test runner (not `unittest`).
- Use `conftest.py` to define shared fixtures (app instance, test client, database session).
- Use an in-memory SQLite database for fast test runs.
- For every Blueprint, write at least one test that validates the route returns the expected status code.


## Strict Tooling Gate (Machine-Enforced — Forced Strict Mode)

Strictest verified toolchain for this stack. Load this skill whenever the project matches the stack. Execute the gate in fail-fast order and stop on the first failure. Record the exact command, output, and exit code in the task's Verification Evidence.

### Strict Baseline

> **Substitute `<SERVICE_NAME>`** — replace every `<SERVICE_NAME>` in this file with your actual package name.
> Example: `myapp` → run `sed -i 's/<SERVICE_NAME>/myapp/g'` after copying the template.
> Keep the placeholder in the shared skill; never commit a concrete service name.
> **Placeholder guard:** CI must fail if any `<SERVICE_NAME>` remains (`grep -r "<SERVICE_NAME>" --include="*.toml" --include="*.py" && echo "FAIL: unsubstituted <SERVICE_NAME>" && exit 1`) — this blocks the template from passing the gate without substitution.

### Required Toolchain

| Tool | Purpose | Minimum version | Activate |
| --- | --- | --- | --- |
| uv | Lockfile resolution + reproducible env (replaces pip/poetry) | 0.12.17 | `uv add --dev` (uv itself via installer) |
| Ruff | Formatting + lint (replaces Black, isort, flake8, pyupgrade, flake8-bugbear/bandit subset) | 0.16.8 | `uv add --dev ruff==0.16.8` |
| Pyright | Primary static type checker, `strict` mode (98% typing-spec conformance) | 1.1.414 | `uv add --dev pyright==1.1.414` |
| mypy | Secondary/compat type checker, `--strict` | 2.3.1 | `uv add --dev mypy==2.3.1` |
| ty | Fast beta checker — advisory only, NOT a gate (53% conformance) | 0.0.82 | `uv add --dev ty==0.0.82` (advisory only — do not install as required gate dependency unless project explicitly opts in; Pyright+mypy are the gates) |
| Bandit | Python AST security scan (SAST) | 1.9.4 | `uv add --dev bandit==1.9.4` |
| Semgrep | SAST + taint tracking; Flask-specific rules | 1.177.0 | `uv add --dev semgrep==1.177.0` |
| pip-audit | CVE scan of the resolved dependency set | 2.10.1 | `uv add --dev pip-audit==2.10.1` |
| vulture | Dead-code / unreachable-code detection | 2.16 | `uv add --dev vulture==2.16` |
| deptry | Unused / undeclared / transitive dependency detection | 0.25.1 | `uv add --dev deptry==0.25.1` |
| import-linter | Architecture contracts (layers / independence / forbidden) | 2.15 | `uv add --dev import-linter==2.15` |
| pytest | Test runner with strict options | 9.1.1 | `uv add --dev pytest==9.1.1` |
| pytest-cov + coverage.py | Branch coverage + hard threshold | 7.1.0 / 7.16.1 | `uv add --dev pytest-cov==7.1.0 coverage==7.16.1` |
| pytest-randomly | Test-order randomization (order-dependence gate) | 5.0.0 | `uv add --dev pytest-randomly==5.0.0` |
| testcontainers | Real Postgres/MySQL in tests (no SQLite substitutes) | 4.15.0 | `uv add --dev "testcontainers[postgres]==4.15.0"` |
| Alembic | Migration drift gate (`alembic check`) | 1.20.0 | `uv add alembic==1.20.0` (app dep) |
| Flask | Framework + `flask --app ... routes` runtime gate | 3.1.3 | `uv add flask==3.1.3` |
| SQLAlchemy | ORM 2.0 `Mapped[]` / `DeclarativeBase` (typed, no stubs) | 2.0.54 | `uv add sqlalchemy==2.0.54` |
| jinja-multilint | Jinja filter/test-name validation (syntax always fails in strict mode) | 0.1.2 | `uv add --dev jinja-multilint==0.1.2` |
| j2lint | Jinja template style + `jinja-syntax-error` (S0) | 1.3.0 | `uv add --dev j2lint==1.3.0` |

**Discarded / not needed (2025–2026 verification):**
- **Black** (26.5.1) — still maintained, but redundant: `ruff format` is Black-compatible and one tool covers format + lint + import sort. Not a gate.
- **flake8, isort, pyupgrade, pycodestyle, flake8-bandit** — superseded by Ruff rule families (`E/W/F/I/UP/S/B/...`). Archived/avoid.
- **SQLAlchemy mypy plugin** (`sqlalchemy.ext.mypy.plugin`) — **deprecated** and removed in SQLAlchemy 2.1; it only works up to mypy 1.10.1. Do **not** install `sqlalchemy-stubs` / `sqlalchemy2-stubs` on 2.0; `Mapped[]` + `DeclarativeBase` is PEP 484-native and works in Pyright without plugins.
- **safety** — older/less maintained than `pip-audit`; prefer pip-audit.

### Strict Baseline Config

**File: `pyproject.toml`** — locking, lint, types, tests, coverage, dead-code, deps.

```toml
[project]
requires-python = ">=3.12"

[tool.ruff]
target-version = "py312"
line-length = 100
src = ["src", "tests"]
required-version = ">=0.16"

[tool.ruff.lint]
# STRICTEST: every stable rule. Ruff auto-disables conflicting pydocstyle pairs.
select = ["ALL"]
# Documented ignore list — only formatter conflicts + genuinely subjective rules.
ignore = [
    # -- Rules that conflict with `ruff format` (Ruff docs "Formatter conflicts") --
    "W191", "E111", "E114", "E117",   # indentation handled by formatter
    "D206", "D300",                    # docstring formatting / triple quotes
    "Q000", "Q001", "Q002", "Q003",    # quote style handled by formatter
    "COM812", "COM819",                # trailing/missing comma
    "ISC001",                          # implicit str concat (formatter conflict)
    # -- Alternative docstring formats (ALL auto-disables the conflicting one) --
    "D203", "D213",
    # -- Subjective / low-signal noise, documented per project policy --
    "D100", "D104", "D107",            # missing docstrings on module/package/__init__
    "ERA001",                          # commented-out code
    "TD002", "TD003",                  # TODO author / link formatting
    "FBT001", "FBT002", "FBT003",      # boolean positional args (Flask/CLI callbacks)
    "ANN401",                          # explicit Any at third-party boundaries
    "PLR0913",                         # too many arguments (view/CLI signatures)
    "E501",                            # line length is the formatter's job
]
fixable = ["ALL"]
unfixable = ["F401", "F841"]           # unused import/local must be reviewed, not auto-deleted

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "D", "ANN", "ARG", "PLR2004", "SLF001", "T20"]
"migrations/**" = ["D", "ANN", "INP001", "E501", "T20"]
"scripts/**" = ["T20", "INP001"]
"**/__init__.py" = ["F401"]

[tool.ruff.lint.isort]
known-first-party = ["<SERVICE_NAME>"]
required-imports = ["from __future__ import annotations"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
docstring-code-format = true

# ---------------------------------------------------------------------------
# TYPE CHECKING — Pyright strict is the authority; mypy strict is the backstop.
# SQLAlchemy 2.0 typing is NATIVE (Mapped[] + DeclarativeBase): no plugin,
# no sqlalchemy-stubs / sqlalchemy2-stubs. The old mypy plugin is deprecated
# and removed in SQLAlchemy 2.1, and only works up to mypy 1.10.1.
# ---------------------------------------------------------------------------
[tool.pyright]
include = ["src", "tests"]
exclude = ["**/migrations", "**/.venv", "**/build", "**/dist"]
pythonVersion = "3.12"
venvPath = "."
venv = ".venv"
typeCheckingMode = "strict"
reportMissingTypeStubs = true
reportUnnecessaryTypeIgnoreComment = true
reportUnusedExpression = true
# strict already implies: reportUnknownMemberType, reportUnknownVariableType,
# reportUnknownParameterType, reportUnknownArgumentType, reportMissingParameterType,
# reportMissingTypeArgument, reportUntypedFunctionDecorator, reportPrivateUsage, ...

[tool.mypy]
python_version = "3.12"
strict = true
warn_unreachable = true
warn_no_return = true
plugins = []                            # intentionally empty (SQLAlchemy 2.0 needs none)
enable_error_code = ["ignore-without-code", "redundant-expr", "truthy-bool"]
exclude = ["migrations/"]

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false

# ---------------------------------------------------------------------------
# TESTS + COVERAGE
# ---------------------------------------------------------------------------
[tool.pytest.ini_options]
minversion = "8.0"
strict = true
testpaths = ["tests"]
addopts = [
    "-ra",
    "--tb=short",
    "--cov=src",
    "--cov-branch",
    "--cov-report=term-missing",
    "--cov-report=xml",
]
filterwarnings = ["error"]             # every warning is a failure
markers = [
    "integration: requires Docker/testcontainers",
    "slow: long-running",
]

[tool.coverage.run]
branch = true
source = ["src"]
parallel = true
omit = ["*/migrations/*", "*/tests/*", "*/wsgi.py"]

[tool.coverage.report]
fail_under = 90                         # ratchet upward; never set 100
show_missing = true
skip_covered = false
precision = 1
exclude_also = [
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "@(abc\\.)?abstractmethod",
    "pragma: no cover",
]

# ---------------------------------------------------------------------------
# DEAD CODE
# ---------------------------------------------------------------------------
[tool.vulture]
min_confidence = 100                   # only guaranteed-dead code fails CI
paths = ["src"]
make_whitelist = false
ignore_decorators = [
    "@app.route", "@*.route", "@*.errorhandler",
    "@*.before_request", "@*.after_request", "@*.teardown_appcontext",
    "@*.cli.command", "@*.register_blueprint",
]
ignore_names = ["create_app", "app", "application", "init_app"]

# ---------------------------------------------------------------------------
# DEPENDENCY HYGIENE
# ---------------------------------------------------------------------------
[tool.deptry]
known_first_party = ["<SERVICE_NAME>"]
extend_exclude = ["migrations", "tests", "scripts", "\\.venv", "build", "dist"]

[tool.deptry.per_rule_ignores]
# runtime-only packages that are never imported directly
DEP002 = ["gunicorn", "psycopg", "alembic"]

# ---------------------------------------------------------------------------
# SECURITY SAST
# ---------------------------------------------------------------------------
[tool.bandit]
exclude_dirs = ["tests", "migrations", ".venv"]
```

**File: `pyproject.toml` (appended) — architecture contracts.**

```toml
# ---------------------------------------------------------------------------
# ARCHITECTURE — Flask blueprint / layer boundaries
# Layers are ordered HIGH -> LOW: a higher layer may import a lower layer,
# never the reverse. `exhaustive = true` makes any unlisted new layer a failure.
# ---------------------------------------------------------------------------
[tool.importlinter]
root_packages = ["<SERVICE_NAME>"]
include_external_packages = true

[[tool.importlinter.contracts]]
name = "Flask layer hierarchy (web -> services -> repositories -> models)"
type = "layers"
layers = [
    "<SERVICE_NAME>.web",           # Blueprints, routes, request/response glue (outer)
    "<SERVICE_NAME>.services",      # application services / use cases
    "<SERVICE_NAME>.repositories",  # data access (SQLAlchemy Session)
    "<SERVICE_NAME>.models",        # SQLAlchemy declarative models (inner)
]
exhaustive = true

[[tool.importlinter.contracts]]
name = "Blueprints are mutually independent"
type = "independence"
modules = [
    "<SERVICE_NAME>.web.billing",
    "<SERVICE_NAME>.web.auth",
    "<SERVICE_NAME>.web.admin",
]

[[tool.importlinter.contracts]]
name = "Domain models never import Flask, services or web"
type = "forbidden"
source_modules = ["<SERVICE_NAME>.models"]
forbidden_modules = ["flask", "<SERVICE_NAME>.web", "<SERVICE_NAME>.services", "<SERVICE_NAME>.repositories"]
as_packages = false
unmatched_ignore_imports_alerting = "warn"

[[tool.importlinter.contracts]]
name = "Repositories never import the web layer"
type = "forbidden"
source_modules = ["<SERVICE_NAME>.repositories"]
forbidden_modules = ["<SERVICE_NAME>.web"]
as_packages = false
```

**File: `tests/test_contract_runtime.py` — Flask runtime correctness gates.**

```python
from __future__ import annotations

import json
from pathlib import Path

from <SERVICE_NAME> import create_app

SNAPSHOT = Path(__file__).parent / "snapshots" / "url_map.json"


def _url_map_snapshot(app) -> list[list[str]]:
    return sorted(
        [rule.rule, ",".join(sorted(rule.methods or [])), rule.endpoint]
        for rule in app.url_map.iter_rules()
    )


def test_app_factory_imports_and_registers_routes() -> None:
    app = create_app()
    assert len(list(app.url_map.iter_rules())) > 1
    assert "static" in {r.endpoint for r in app.url_map.iter_rules()}


def test_url_map_matches_snapshot() -> None:
    current = _url_map_snapshot(create_app())
    assert SNAPSHOT.exists(), "missing url_map snapshot; generate with --snapshot"
    assert current == json.loads(SNAPSHOT.read_text()), (
        "URL map changed: review route additions/removals, then regenerate snapshot"
    )


def test_every_template_compiles() -> None:
    app = create_app()
    with app.app_context():
        env = app.jinja_env
        for name in env.list_templates():
            env.get_template(name)          # raises TemplateSyntaxError on failure
```

Generate the snapshot once and commit it:

```bash
uv run python -c "import json,pathlib;from <SERVICE_NAME> import create_app;a=create_app();p=pathlib.Path('tests/snapshots/url_map.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(sorted([[r.rule,','.join(sorted(r.methods or [])),r.endpoint] for r in a.url_map.iter_rules()]),indent=2))"
```

### Mandatory Gate Order

0. `! grep -r "<SERVICE_NAME>" --include="*.toml" --include="*.py" .` — placeholder guard: fail if any `<SERVICE_NAME>` remains unsubstituted (substitute first via `sed -i 's/<SERVICE_NAME>/myapp/g'`).
1. `uv lock --check`
2. `uv sync --locked`
3. `uv run ruff format --check .`
4. `uv run ruff check .`
5. `uv run pyright`
6. `uv run mypy src`
7. `uv run lint-imports`
8. `uv run bandit -c pyproject.toml -r src -lll -iii`
9. `uv run semgrep --config p/python --config p/flask --config p/owasp-top-ten --error --strict --metrics=off`
10. `uv run jinja-multilint --mode strict templates/`
11. `uv run j2lint templates/`
12. `uv run deptry .`
13. `uv run pip-audit --locked --strict`
14. `uv run vulture`
15. `uv run python -c "from <SERVICE_NAME> import create_app; app = create_app(); assert len(list(app.url_map.iter_rules())) > 1"`
16. `uv run flask --app <SERVICE_NAME>:create_app routes`
17. `uv run pytest tests/test_contract_runtime.py -p no:randomly -q`
18. `uv run pytest -p randomly --cov=src --cov-branch --cov-fail-under=90`
19. `uv run alembic upgrade head && uv run alembic check`
20. `uv run pip check`

> Run in order, stop on the first non-zero exit. Warnings are errors; do not auto-fix in CI. `pip-audit --strict` fails if dependency collection itself fails on any package; `semgrep --error` exits 1 on any finding and `--strict` exits 3 on invalid target syntax. Keep `pytest-randomly` enabled in CI (order-dependence is a real defect); the only place to use `-p no:randomly` is a local reproduction/bisect, and reproductions should prefer `--randomly-seed=last`.

### Hallucination Traps to Block

- Invented route/endpoint or broken blueprint registration -> `flask --app <SERVICE_NAME>:create_app routes` + URL-map snapshot test + import-linter `independence`/`forbidden`.
- Model changed without an Alembic revision -> `alembic upgrade head && alembic check` (non-zero on pending ops) — catch before "Target database is not up to date" in prod.
- SQLAlchemy 1.x-style `declarative_base()` / untyped `Column()` in code that claims to be 2.0 -> Pyright `strict` + mypy `--strict` against `Mapped[...]` / `DeclarativeBase` (the old mypy plugin is deprecated/removed, so it cannot rescue this).
- Template referencing an undefined variable, filter, or endpoint -> `env.get_template()` compile test + jinja-multilint `--mode strict` + `j2lint` (S0 jinja-syntax-error).
- Fabricated/undeclared dependency (import with no matching lock entry) -> `deptry` DEP001/DEP003 and `uv sync --locked` failing on lock drift.
- Dead or orphaned view/service function presented as wired up -> Ruff `F401/F841` + `vulture --min-confidence 100`.
- SQL injection / command injection via `request.args` reaching `execute()` or `subprocess` -> Semgrep `p/flask` taint rules + Bandit `-lll` (`B608`, `B602`).
- Tests that only pass in file order (hidden shared DB/session state) -> `pytest-randomly` order shuffling + `filterwarnings = ["error"]` + transaction-rollback DB fixture.
- `Any` erasing a type hole, or `# type: ignore` hiding a real error -> mypy `strict` (`disallow_any_generics`, `disallow_untyped_defs`) + Pyright `reportUnnecessaryTypeIgnoreComment`.
- Hallucinated "hardcoded" URL instead of `url_for()` -> jinja-multilint / pytest-jinja-check hardcoded-route detection.

### Evidence to Record

Paste the command and its pass criterion (all must be green):

| Command | Pass criterion |
| --- | --- |
| `uv lock --check && uv sync --locked` | exit 0; `uv.lock` unchanged by the run |
| `uv run ruff format --check . && uv run ruff check .` | exit 0, `All checks passed!` / no reformatted files |
| `uv run pyright` | `0 errors` |
| `uv run mypy src` | `Success: no issues found` |
| `uv run lint-imports` | `Contracts: N kept, 0 broken` |
| `uv run bandit -c pyproject.toml -r src -lll -iii` | no HIGH severity, no HIGH confidence findings |
| `uv run semgrep ... --error --strict` | exit 0 (no ERROR findings, no invalid syntax) |
| `uv run jinja-multilint --mode strict templates/` | exit 0, no unknown filter/test errors |
| `uv run j2lint templates/` | exit 0, no S0 jinja-syntax-error |
| `uv run pip-audit --locked --strict` | `No known vulnerabilities found` |
| `uv run deptry .` | `Success! No dependency issues found.` |
| `uv run vulture` | no output, exit 0 |
| `uv run flask --app <SERVICE_NAME>:create_app routes` | non-empty route table, exit 0 |
| `uv run pytest -p randomly --cov=src --cov-branch --cov-fail-under=90` | all tests pass; `coverage: total >= 90%` |
| `uv run alembic upgrade head && uv run alembic check` | `No new upgrade operations detected.` |
| `uv run pip check` | `No broken requirements found.` |

Record the URL-map snapshot diff (if any) and the pytest-randomly seed printed at run start; the seed is required to reproduce any order-dependent failure.

<!-- sources -->
- https://docs.astral.sh/ruff/linter/ (ALL selector, rule precedence, formatter-conflict rules)
- https://docs.astral.sh/ruff/configuration/ (select/ignore/extend-select, per-file-ignores)
- https://docs.astral.sh/ruff/settings/
- https://docs.astral.sh/ruff/rules/missing-type-self/ (ANN101 removed — do not list in ignore)
- https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md (removed rules ANN101/ANN102/E999/PD901/UP038)
- https://pydevtools.com/handbook/how-to/how-to-configure-recommended-ruff-defaults/
- https://pydevtools.com/handbook/how-to/how-to-configure-mypy-strict-mode/ (`strict = true` flag set)
- https://www.danilchenko.dev/posts/ty-vs-mypy-vs-pyright/ (Pyright 98% vs mypy 58% vs ty 53% conformance)
- https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html (mypy plugin deprecated, removed in 2.1; Mapped[] is native)
- https://docs.sqlalchemy.org/en/latest/orm/declarative_styles.html (DeclarativeBase supersedes declarative_base)
- https://bandit.readthedocs.io/en/latest/man/bandit.html (`-lll` HIGH severity, `-iii` HIGH confidence)
- https://github.com/pypa/pip-audit (`--strict`, `--require-hashes`, `--locked`)
- https://github.com/jendrikseipp/vulture (min-confidence, pyproject `[tool.vulture]`)
- https://deptry.com/usage/ (DEP001–DEP005, per_rule_ignores, known_first_party)
- https://github.com/osprey-oss/deptry (rules DEP001 missing / DEP002 unused / DEP003 transitive / DEP004 dev)
- https://docs.semgrep.dev/cli-reference (`--error` exit 1, `--strict` exit 3)
- https://semgrep.dev/p/flask and https://github.com/semgrep/semgrep-rules (Flask taint rules)
- https://import-linter.readthedocs.io/en/stable/contract_types/layers/ (layers, containers, exhaustive)
- https://import-linter.readthedocs.io/en/stable/contract_types/forbidden/ (forbidden, as_packages, include_external_packages)
- https://kokonatt.com/blog/modular-boundaries-import-linter/ (hexagonal contracts, independence/protected/acyclic_siblings)
- https://pytest-cov.readthedocs.io/en/latest/config.html (`--cov-fail-under`, `--cov-branch`)
- https://qaskills.sh/blog/pytest-coverage-pytest-cov-guide-2026 (branch coverage, fail_under, combine)
- https://github.com/pytest-dev/pytest-randomly (seed, `--randomly-seed=last`, `-p no:randomly`)
- https://github.com/aristanetworks/j2lint (S0 jinja-syntax-error, CI)
- https://pypi.org/project/jinja-multilint/ (--mode strict, unknown filter/test = error)
- https://jinja.palletsprojects.com/en/stable/api/ (`compile_templates(..., ignore_errors=False)`)
- https://flask.palletsprojects.com/en/stable/cli/ (`flask --app ... routes` factory discovery)
- https://flask.palletsprojects.com/en/stable/testing/ (app factory fixtures, test_client)
- https://flask.palletsprojects.com/en/stable/blueprints/ (blueprint boundaries)
- https://alembic.sqlalchemy.org/en/latest/autogenerate.html (`alembic check` CI drift gate)
- https://docs.docker.com/guides/testcontainers-python-getting-started/ (testcontainers + pytest)
- https://qaskills.sh/blog/testcontainers-python-pytest-integration-guide (Postgres + Alembic + SQLAlchemy fixtures)
- https://docs.astral.sh/uv/concepts/projects/sync/ (`--locked` vs `--frozen`, `uv lock --check`)
- https://pydevtools.com/handbook/how-to/how-to-use-a-uv-lockfile-for-reproducible-python-environments/

## Currency Baseline

- **Flask 3.x baseline:** Target Flask 3.x with Flask-SQLAlchemy 3 and SQLAlchemy 2.0-style typed models.
