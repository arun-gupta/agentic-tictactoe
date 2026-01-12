# Development Guide

This guide covers setup and workflow for developing the Agentic Tic-Tac-Toe project.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

## Development Workflow

When implementing new features:

- **Implement one sub-section at a time**: Use the implementation plan to work incrementally. There are SKILLS that will commit and push after each sub-section is completed.
- **Test coverage**: Each sub-section has test cases defined in the implementation plan. Make sure tests exist and are comprehensive. If not, use the agent to add comprehensive test coverage.
- **Run tests locally**: Always run tests locally before committing:
  ```bash
  pytest tests/                    # Run all tests
  pytest tests/unit/domain/        # Run specific test file/directory
  pytest tests/ -k "test_name"      # Run specific test by name
  ```
- **Run code quality checks locally**: Verify code quality before committing:
  ```bash
  black --check src/ tests/         # Check formatting
  ruff check src/ tests/            # Check linting
  mypy src/ --strict --explicit-package-bases  # Check types
  ```
- **Pre-commit hooks**: Pre-commit hooks run automatically on `git commit`. To run manually:
  ```bash
  pre-commit run --all-files
  ```
- **Check coverage locally**: Verify test coverage before pushing:
  ```bash
  pytest tests/ --cov=src --cov-report=html --cov-report=term
  # Open htmlcov/index.html in browser to view coverage report
  ```
- **Wait for CI**: Wait for GitHub Actions to go green after the push before making any new changes to the repo.
- **Monitor build time**: Check if the build time slows down (GitHub Actions will show this). If it does, investigate and debug the cause.
- **Update demo scripts**: Check if `run_demo.sh` can be updated to incorporate new use cases.
- **Update documentation**: Make sure `README.md` and `scripts/README.md` are updated as relevant.
- **Monitor code coverage**: Check for code coverage trends. If coverage drops, investigate and add tests to maintain or improve coverage.

## Running the API Server Locally

For testing API endpoints or running the API demo:

```bash
# Start the FastAPI server
uvicorn src.api.main:app --reload

# Server will be available at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

The `run_demo.sh api` command will automatically start the server if it's not already running.

## Pre-commit Hooks Setup

Pre-commit hooks run automatically on `git commit` to ensure code quality. To set them up:

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the git hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

**Note**: Hooks can be skipped with `git commit --no-verify` if needed, but CI will still catch issues.

## Troubleshooting

- **Import errors**: Make sure the virtual environment is activated and dependencies are installed: `pip install -e ".[dev]"`
- **Test failures**: Run tests with `-v` flag for verbose output: `pytest tests/ -v`
- **Type errors**: Run mypy on specific files: `mypy src/domain/models.py --strict --explicit-package-bases`
- **Formatting issues**: Auto-fix with `black src/ tests/` (without `--check`)
- **Linting issues**: Auto-fix many issues with `ruff check --fix src/ tests/`
- **Pre-commit hooks not running**: Run `pre-commit install` to reinstall hooks
- **Coverage not updating**: Make sure to run `pytest tests/ --cov=src` (not just `pytest tests/`)

## See Also

- [Implementation Plan](implementation-plan.md) - Detailed implementation guide with test coverage
- [Full Specification](spec/spec.md) - Complete system architecture and design
