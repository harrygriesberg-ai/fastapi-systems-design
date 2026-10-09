# Contributing

This repository is intentionally organized as a teaching series. Each numbered folder is a
self-contained example that can be installed and tested independently.

## Development workflow

1. Fork or clone the repository.
2. Choose the lesson you want to change.
3. Create a virtual environment inside that lesson folder.
4. Install the lesson in editable mode with development dependencies: `pip install -e ".[dev]"`.
5. Run `pytest` and `ruff check .` before opening a pull request.
6. Keep examples focused on the lesson objective. Avoid introducing infrastructure that is not
   explained in the accompanying article and README.

## Style

- Python 3.11+.
- Type hints on public functions and service boundaries.
- Pydantic models at HTTP boundaries.
- Business logic should live outside route functions.
- Tests should cover both success paths and meaningful failures.
- Never commit secrets. Add new configuration keys to `.env.example`.

## Documentation changes

If behavior changes, update both the lesson README and `ARTICLE.md`. A teaching repository is only
useful when the code and explanation stay aligned.
