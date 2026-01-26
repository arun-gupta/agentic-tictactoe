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
  ./run_tests.sh                   # Run all except contract + live LLM
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
- **Run contract tests**: Validate API implementation matches OpenAPI specification:
  ```bash
  pytest tests/contract -v -m contract        # Run only contract tests
  pytest tests/ -m "not contract"            # Run all tests except contract tests
  pytest tests/contract/ -v --tb=short       # Run contract tests with short traceback
  ```
- **Run live LLM tests (opt-in; may incur cost)**:
  ```bash
  RUN_LIVE_LLM_TESTS=1 python -m pytest -m live_llm -q
  # Optionally select providers (defaults to all that have keys configured):
  LIVE_LLM_PROVIDERS=openai,anthropic,gemini RUN_LIVE_LLM_TESTS=1 python -m pytest -m live_llm -q
  ```
- **Run LLM integration tests**:
  ```bash
  python -m pytest -m llm_integration -q
  # Skip any live LLM tests:
  python -m pytest -m "llm_integration and not live_llm" -q
  # Script wrapper:
  ./run_tests.sh --llm
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

## Contract Testing

Contract tests validate that the API implementation matches its OpenAPI specification. They ensure:
- API responses match their Pydantic model contracts
- OpenAPI schema is complete and accurate
- Breaking changes are detected early

**Running Contract Tests:**
```bash
# Run all contract tests
pytest tests/contract -v -m contract

# Run specific contract test file
pytest tests/contract/test_openapi_schema.py -v

# Run contract tests with detailed output
pytest tests/contract -v --tb=short
```

**Contract Test Types:**
- **Schema Validation**: Verifies OpenAPI schema structure and completeness
- **Auto-Generated Tests**: Uses Schemathesis to generate tests from OpenAPI spec
- **Response Validation**: Ensures API responses deserialize to Pydantic models

See [Contract Testing Guide](guides/CONTRACT_TESTING.md) for detailed implementation and usage.

## Phase 8: Web UI Setup (shadcn/ui)

Phase 8 requires **shadcn/ui** as the component library. The UI follows the Figma design specification.

**Figma Design**: [Tic-Tac-Toe Design](https://www.figma.com/design/mhNp0FKIqT0mSBP8qKKvbi/Tic-Tac-Toe?node-id=2-510)

### Setting Up shadcn/ui

```bash
# Navigate to UI directory
cd src/ui

# Initialize shadcn/ui (select defaults: TypeScript, zinc color palette)
npx shadcn@latest init

# Add required components
npx shadcn@latest add tabs      # Main navigation (Board | Config | Metrics)
npx shadcn@latest add button    # New Game button
npx shadcn@latest add select    # Agent LLM selection dropdowns
npx shadcn@latest add input     # API key inputs, metrics display
```

### Font Setup (JetBrains Mono)

Add JetBrains Mono font to your project:

```html
<!-- In index.html or layout file -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

Configure in Tailwind:
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
}
```

### Required shadcn Components

| Component | Purpose | shadcn Link |
|-----------|---------|-------------|
| Tabs | Board / Config / Metrics navigation | https://ui.shadcn.com/docs/components/tabs |
| Button | New Game button | https://ui.shadcn.com/docs/components/button |
| Select | Agent LLM selection (Scout, Strategist, Executor) | https://ui.shadcn.com/docs/components/select |
| Input | API key inputs, metrics display | https://ui.shadcn.com/docs/components/input |

### Design Specifications

- **Container**: 640×640px, zinc-100 background, shadow
- **Color Palette**: Zinc (light theme)
- **Font**: JetBrains Mono (monospace)
- **Cell Sizes**: 100×100px for game board cells
- **States**: Default, Hover, Focus, Win (green-200), Lost (red-200)

See [ui-spec.md](spec/ui-spec.md) for complete visual specifications.

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Collaboration guidelines and git workflow
- [Implementation Plan](implementation-plan.md) - Detailed implementation guide with test coverage
- [Full Specification](spec/spec.md) - Complete system architecture and design
- [UI Specification](spec/ui-spec.md) - Visual design specification with Figma integration
- [Contract Testing Guide](guides/CONTRACT_TESTING.md) - API contract testing implementation plan
