## Project Overview

An application to organize my financial life.

Interfaces: the CLI (`financial` command from `financial/cli.py`, with a REPL), the web dashboard (`financial dashboard`: FastAPI in `financial/api/` serving the pages in `financial/web/`) and the Jupyter notebooks in `notebooks/`.

## Key Architecture Decisions

- **Only english** Namespaces, classes, functions, variables, config keys and every code aspect must be written in english. Only label strings can be written in another language
- **No leetcode** Avoid writing code intended merely for demos or Proofs of Concept (PoC); always write code for production systems. Do not confuse concise code with PoC code.
- **Do housekeeping tasks** Check for unused or inaccessible code, variables, functions, or `using` statements, and remove them in a separate commit for any feature under development.
- **Refactor duplication** Check for duplicate code and remove it in a separate commit for any feature under development.
- **Branches from main** Create branches for features, fixes, refactoring starting from the `main` branch.
- **Migrations** Never update migrations files, database updates must always be in new migration files.

## Project Structure

```
financial/
├── cli.py, settings.py, database.py, hashing.py
├── models/       # SQLAlchemy tables only: columns, relationships, simple helpers
├── services/     # business operations that use a session (categorization, adjustments, ...)
│   └── analytics/ # dashboard aggregations over the ledger (pandas), returning dataclasses
├── api/          # FastAPI app and routers: HTTP only, no business logic
├── web/          # dashboard pages: plain ES modules + ECharts, no build step
└── importers/
    ├── base.py
    ├── staging.py # inserts staged rows into transactions (shared by every importer)
    └── <source>/ # everything specific to one bank or card: importer, parsing, staging model, merge, constants, data/
tests/            # mirrors financial/; CSV fixtures in tests/data/
notebooks/        # exploratory analyses
data/             # personal statements and dumps, never versioned
```

- Business logic goes into `services/` (or the bank package), never into models, the CLI or the API routes
- API routes return the services' dataclasses directly; the web pages only format and render what the API returns
- A new bank or card is a new package under `financial/importers/`, reusing `financial/importers/staging.py` to merge
- New models must be imported in `financial/models/__init__.py` so their tables are registered

## Code Conventions
- Follow SOLID principles
- Follow REST API and MVP conventions
- Build minimal line numbers classes / functions and files
- Always extract configuration values in .env / .env_example
  - Secrets and per-environment values: `.env`, read through `financial/settings.py`
  - Library settings and business decisions: `constants.py` of the package they belong to (e.g. `financial/importers/inter/constants.py`)
- Small commits, one per feature or feature stage

## Documentation

When adding or changing features:

1. Add or update tests (unit, integration or e2e) when applicable
2. Update `README.md` if applicable
3. Update `CLAUDE.md` if the change affects development workflow, version of core tecnologies, runnig or testing scripts, core principles or architecture.

## Testing

- `pytest` runs the unit tests with coverage; it fails below 95% (`pyproject.toml`)
- Tests use a fresh in-memory SQLite database per test (`tests/conftest.py`); never point tests to a real database
- Keep SQL portable (ORM or standard SQL) so it runs on both MySQL and SQLite
- Build test transactions with `tests/factories.py`
- API routes are tested with FastAPI's `TestClient` over the same in-memory database (`tests/api/`)
- No e2e tests for the web pages for now
