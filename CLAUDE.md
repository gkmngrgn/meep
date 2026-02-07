# CLAUDE.md

## Project Overview

Meep is a Python CLI tool for reviewing and organizing tweets from exported Twitter data archives. Built with Click, Pydantic, and SQLite.

## Development Setup

```bash
uv sync                 # Install all dependencies
```

## Common Commands

```bash
uv run meep load-data <twitter-archive.zip>   # Import Twitter archive
uv run meep analyze --keyword="..." --year=2015 --show-tweets  # Query tweets
```

## Code Quality

Pre-commit hooks enforce all style checks. Run them manually with:

```bash
pre-commit run --all-files
```

Individual tools:

```bash
# Formatting and linting
uvx ruff check --fix .
uvx ruff format .

# Type checking
uvx mypy --strict --ignore-missing-imports meep/
```

## Code Style

- **Always use `uv run`** to execute Python scripts and project commands (e.g., `uv run meep`)
- **Always use `uvx`** to run dev tools like ruff, mypy, etc.
- **Ruff** for formatting and linting (replaces black, isort)
- **mypy strict mode** — all code must have type annotations
- No trailing whitespace; files must end with a newline

## Architecture

```
meep/
  cli.py       — Click CLI commands (entry point: `run`)
  models.py    — Pydantic data models (Account, Tweet)
  database.py  — SQLite database layer with context managers
  archive.py   — Twitter ZIP archive parser
  config.py    — App configuration and paths (uses appdirs)
  printer.py   — Tweet output formatting
```

## Key Patterns

- Pydantic models for all data validation
- Context managers for database connections
- `from_row()` / `to_row()` factory methods for DB serialization
- Generators for tweet filtering
- Python 3.9+ required
