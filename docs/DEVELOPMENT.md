# Development Guide

This guide covers setup and workflow for developing the Agentic Tic-Tac-Toe project.

## Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd agentic-tictactoe

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Verify installation
pytest tests/
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) for collaboration guidelines and git workflow.

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

## Commit Message Conventions

Follow conventional commit format for clear, consistent commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type** (required): One of the following:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring (no functional changes)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build config, etc.)
- `perf`: Performance improvements
- `ci`: CI/CD changes

**Scope** (optional): The area of the codebase affected (e.g., `api`, `domain`, `agents`, `tests`)

**Subject** (required): Brief description (50 chars or less, imperative mood, no period)

**Body** (optional): Detailed explanation (wrap at 72 chars)

**Footer** (optional): Reference issues, breaking changes, etc.

**Examples:**

```
feat(api): add POST /api/game/new endpoint

Implement endpoint to create new game sessions with optional player symbol preference.
Returns game_id and initial game_state.

fix(domain): correct win detection logic for diagonal wins

The diagonal win check was missing the bottom-left to top-right case.
Added test coverage for all diagonal win scenarios.

docs: update DEVELOPMENT.md with commit conventions

Add commit message format guidelines to help maintain consistent commit history.

test(api): add integration tests for game status endpoint

Cover all acceptance criteria from Phase 4.2.3 including game state, agent status, and metrics.
```

**Best Practices:**
- Use imperative mood ("add" not "added" or "adds")
- First line should be clear and concise
- Reference issues in footer: `Closes #123` or `Fixes #456`
- For breaking changes, start footer with `BREAKING CHANGE:`

## Running the API Server Locally

For testing API endpoints or running the API demo:

```bash
# Start the FastAPI server
uvicorn src.api.main:app --reload

# Server will be available at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

The `run_demo.sh api` command will automatically start the server if it's not already running.

## Pre-commit Validation

Before committing, always run validation checks locally to catch issues early:

```bash
# Run all validation checks
pytest tests/ --cov=src --cov-report=term && \
black --check src/ tests/ && \
ruff check src/ tests/ && \
mypy src/ --strict --explicit-package-bases
```

See the [pre-commit-validation skill](../skills/pre-commit-validation/SKILL.md) for detailed validation guidelines.

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

## Working with Git

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd agentic-tictactoe

# Set up remote tracking (if forked)
git remote add upstream <original-repository-url>
```

### Daily Workflow

```bash
# Update your local main branch
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feat/your-feature-name

# Make changes, commit (follow commit conventions)
git add .
git commit -m "feat(scope): your commit message"

# Push and create PR
git push origin feat/your-feature-name
```

### Keeping Branches Updated

```bash
# Update your feature branch with latest main
git checkout main
git pull origin main
git checkout your-feature-branch
git rebase main  # or git merge main
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed branching strategy and PR process.

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Collaboration guidelines and git workflow
- [Implementation Plan](implementation-plan.md) - Detailed implementation guide with test coverage
- [Full Specification](spec/spec.md) - Complete system architecture and design
- [Contract Testing Guide](guides/CONTRACT_TESTING.md) - API contract testing implementation plan
