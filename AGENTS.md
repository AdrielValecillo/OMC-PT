# AGENTS.md

## Purpose
- This guide is for coding agents working in this repository.
- Follow this file for day-to-day implementation defaults, quality checks, and style rules.
- When unsure, prefer minimal, correct changes that match existing project structure.

## Codebase Snapshot
- Language: Python 3.12 (`.python-version`).
- Package manager: `uv` (`pyproject.toml`, `uv.lock`).
- API framework: FastAPI.
- App entrypoint: `app/main.py` -> `app.main:app`.
- Main source root: `app/`.
- Tests root: `tests/` (currently almost empty).
- Database utility file exists: `app/db/database.py`.
- Current DB utility imports `sqlalchemy` and `python-dotenv`.
- `sqlalchemy` and `python-dotenv` are not currently declared in `pyproject.toml`.

## Repo-Specific Assistant Rules
- Cursor rules check: no `.cursor/rules/` directory found.
- Cursor rules check: no `.cursorrules` file found.
- Copilot rules check: no `.github/copilot-instructions.md` found.
- If any of those files appear later, treat them as high-priority repo instructions.

## Environment and Setup
- Create/sync environment: `uv sync`.
- Install runtime deps from lockfile: `uv sync --frozen`.
- If lockfile is intentionally updated: `uv lock` then `uv sync`.
- Local env file is expected (`.env`) and is gitignored.
- Python version should stay aligned to `3.12` unless a planned upgrade is requested.

## Run Commands
- Start dev server: `uv run uvicorn app.main:app --reload`.
- Start server on explicit host/port: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`.
- Quick import smoke check: `uv run python -c "import app.main; print('ok')"`.
- Basic syntax/build sanity: `uv run python -m compileall app tests`.
- API root check after start: `curl http://127.0.0.1:8000/`.

## Lint and Format Commands
- Current state: no lint/format tools are configured in `pyproject.toml`.
- Recommended baseline dev tools:
- `uv add --dev ruff pytest pytest-asyncio mypy sqlalchemy python-dotenv`
- Format (if ruff added): `uv run ruff format app tests`.
- Lint (if ruff added): `uv run ruff check app tests`.
- Auto-fix lint (if ruff added): `uv run ruff check app tests --fix`.
- Type check (if mypy configured): `uv run mypy app`.

## Test Commands
- Current state: there are no real test modules yet.
- Run full suite (after adding tests): `uv run pytest`.
- Verbose run: `uv run pytest -v`.
- Stop early on first failure: `uv run pytest -x`.
- Run by keyword: `uv run pytest -k "lead and create"`.
- Run a single file: `uv run pytest tests/test_leads.py`.
- Run a single test function: `uv run pytest tests/test_leads.py::test_create_lead`.
- Run a single test class method: `uv run pytest tests/test_leads.py::TestLeads::test_create_lead`.
- Run with max failures: `uv run pytest --maxfail=1`.
- Optional coverage (if pytest-cov installed): `uv run pytest --cov=app --cov-report=term-missing`.

## FastAPI Conventions
- Keep `app/main.py` focused on app creation, middleware, and router registration.
- Put endpoint handlers in `app/api/routers/` modules.
- Keep business logic in `app/services/`.
- Keep DB/session logic in `app/db/`.
- Use dependency injection for DB sessions and auth/context dependencies.
- Always declare `response_model` for non-trivial endpoints.
- Prefer async handlers for IO-bound work; keep sync handlers only when justified.
- Keep handlers thin: parse input, call service, map errors, return response.

## Imports
- Order imports in three groups: stdlib, third-party, first-party.
- Separate groups with one blank line.
- Prefer absolute imports from `app...` over fragile relative imports.
- Do not use wildcard imports.
- Keep one import per line for readability.
- Remove unused imports quickly.
- If an import is only for typing, use `if TYPE_CHECKING:` when useful.

## Formatting
- Follow PEP 8 and Black-compatible style.
- Target max line length of 88.
- Use trailing commas in multiline literals/calls.
- Prefer double quotes for consistency with common formatters.
- Keep functions short and focused.
- Avoid commented-out code and noisy inline comments.
- Add docstrings on public modules, classes, and non-obvious functions.

## Typing
- Add type hints to all new/changed function signatures.
- Include explicit return types on public functions.
- Prefer concrete types over `Any`.
- Use `X | None` over `Optional[X]` for Python 3.12 style.
- Use Pydantic models for request/response payload contracts.
- Keep schemas in `app/db/schemas/` (or a dedicated schemas package) as project grows.
- Validate external data at boundaries, not deep inside business logic.

## Naming
- Modules/files: `snake_case.py`.
- Functions/variables: `snake_case`.
- Classes: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Endpoint paths: plural nouns for collections (`/leads`), singular with IDs (`/leads/{lead_id}`).
- Use descriptive names (`lead_repository`) over abbreviations (`lr`).

## Error Handling and Validation
- Raise `HTTPException` for expected API-level errors.
- Use correct status codes (400/404/409/422/500/etc.).
- Return stable, user-safe error payloads; do not leak secrets or stack traces.
- Prefer domain-specific exceptions in services, translated to HTTP errors at router layer.
- Validate inputs with Pydantic constraints instead of ad-hoc checks where possible.
- For DB writes, ensure transaction rollback on failure.
- Handle not-found and duplicate-resource cases explicitly.

## Database Guidelines
- Use one DB session per request via dependency injection.
- Do not keep global mutable session objects.
- Keep models in `app/db/models/` and migration artifacts in a migrations folder when added.
- If using PostgreSQL, do not pass SQLite-only engine args like `check_same_thread`.
- Centralize connection string construction in one place.
- Read credentials from environment variables only.

## Testing Guidelines
- Put tests under `tests/` mirroring app structure.
- Test file pattern: `tests/test_<feature>.py`.
- Test names should describe behavior, not implementation details.
- Arrange-Act-Assert structure is preferred.
- Use fixtures for shared setup (DB session, test client, seed data).
- Include API tests for success and failure paths.
- Add regression tests for every bug fix.

## Agent Workflow Checklist
- Read `pyproject.toml` and touched modules before coding.
- Make the smallest safe change that solves the requested task.
- Run relevant checks for touched code (at least syntax/build sanity).
- If lint/test tooling is present, run it before finishing.
- Update docs when behavior, commands, or structure changes.
- Never commit `.env` or secrets.

## Definition of Done for Agent PRs
- Code runs locally with documented commands.
- New behavior is covered by tests (or a clear reason is documented).
- Lint/format/type checks pass when configured.
- Error handling paths are covered for new endpoints/services.
- Documentation stays accurate (`README.md`, this file, and examples).
