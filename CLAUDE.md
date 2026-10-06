## Project Overview

An application to organize my financial life.

Interfaces: the CLI (`financial/cli.py`, with a REPL) and the Jupyter notebooks in `notebooks/`.

## Key Architecture Decisions

- **Only english** Namespaces, classes, functions, variables, config keys and every code aspect must be written in english. Only label strings can be written in another language
- **No leetcode** Avoid writing code intended merely for demos or Proofs of Concept (PoC); always write code for production systems. Do not confuse concise code with PoC code.
- **Do housekeeping tasks** Check for unused or inaccessible code, variables, functions, or `using` statements, and remove them in a separate commit for any feature under development.
- **Refactor duplication** Check for duplicate code and remove it in a separate commit for any feature under development.
- **Branches from main** Create branches for features, fixes, refactoring starting from the `main` branch.
- **Migrations** Never update migrations files, database updates must always be in new migration files.

## Code Conventions
- Follow SOLID principles
- Follow REST API and MVP conventions
- Build minimal line numbers classes / functions and files
- Always extract configuration values in .env / .env_example
- Small commits, one per feature or feature stage

## Documentation

When adding or changing features:

1. Add or update tests (unit, integration or e2e) when applicable
2. Update `README.md` if applicable
3. Update `CLAUDE.md` if the change affects development workflow, version of core tecnologies, runnig or testing scripts, core principles or architecture.

## Testing

- `pytest` runs the unit tests with coverage; it fails below 95% (`.coveragerc`)
- Tests use a fresh in-memory SQLite database per test (`tests/conftest.py`); never point tests to a real database
- Keep SQL portable (ORM or standard SQL) so it runs on both MySQL and SQLite
- Build test transactions with `tests/factories.py`
- No integration or e2e tests for now: the frontend is going to change
