# Contributing Guide

This guide helps developers work independently and collaborate effectively on the Agentic Tic-Tac-Toe project.

## Getting Started

1. **Fork and Clone**: Fork the repository and clone your fork
2. **Set up environment**: Follow the [Development Setup](docs/DEVELOPMENT.md#development-setup) guide
3. **Configure environment variables** (optional for Phase 4, required for Phase 5+):
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys if using LLM features
   ```
4. **Create a branch**: Create a feature branch from `main` (see [Branching Strategy](#branching-strategy))
5. **Make changes**: Implement your feature following the [Development Workflow](docs/DEVELOPMENT.md#development-workflow)
6. **Test locally**: Run all tests and quality checks before pushing
7. **Submit PR**: Open a pull request following the [PR Process](#pull-request-process)

## Branching Strategy

### Main Branch
- `main` is the primary development branch
- Always up-to-date with the latest stable code
- All features are merged into `main` via pull requests

### Feature Branches
Create feature branches from `main` for new work:

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

**Branch Naming Conventions:**
- `feat/<description>` - New features (e.g., `feat/api-game-reset`)
- `fix/<description>` - Bug fixes (e.g., `fix/win-detection-logic`)
- `docs/<description>` - Documentation updates (e.g., `docs/api-documentation`)
- `test/<description>` - Test additions/updates (e.g., `test/integration-coverage`)
- `refactor/<description>` - Code refactoring (e.g., `refactor/agent-pipeline`)

### Working Independently
- Each developer works on their own feature branch
- Keep branches focused on a single feature or fix
- Keep branches up-to-date with `main` regularly:
  ```bash
  git checkout main
  git pull origin main
  git checkout your-feature-branch
  git rebase main  # or git merge main
  ```

## Pull Request Process

### Before Creating a PR

1. **Run validation checks**: Follow the [pre-commit-validation skill](skills/pre-commit-validation/SKILL.md) to ensure all tests, formatting, linting, and type checking pass
2. **Update documentation**: Update relevant docs (README, API docs, etc.)
3. **Follow commit conventions**: Use [commit message conventions](docs/DEVELOPMENT.md#commit-message-conventions)
4. **Rebase on main**: Ensure your branch is up-to-date with `main`

### Creating a PR

1. **Push your branch**: `git push origin your-feature-branch`
2. **Open PR on GitHub**: Use the "New Pull Request" button
3. **Fill out PR template** (if available):
   - Describe what changes you made
   - Reference related issues (e.g., "Fixes #123")
   - List any breaking changes
   - Include screenshots if UI changes

### PR Requirements

- ✅ All CI checks must pass (tests, linting, type checking)
- ✅ Code coverage must not decrease
- ✅ At least one approval (if code review is required)
- ✅ No merge conflicts with `main`
- ✅ Follows code style and conventions

### PR Review Process

- Reviewers will check:
  - Code quality and style
  - Test coverage
  - Documentation updates
  - Alignment with project architecture
- Address review feedback by pushing additional commits to your branch
- Once approved, the PR can be merged (usually by the reviewer or maintainer)

## Coordinating Work

### Communication
- Use GitHub Issues to track work and coordinate
- Comment on PRs for discussions
- Update the implementation plan when starting work on a phase/section

### Avoiding Conflicts

1. **Work on different areas**: Coordinate to avoid working on the same files
2. **Keep branches small**: Smaller PRs reduce conflict likelihood
3. **Rebase regularly**: Keep your branch updated with `main` to catch conflicts early
4. **Communicate**: Let others know what you're working on

### Resolving Conflicts

If you encounter merge conflicts:

```bash
# Update your branch
git checkout main
git pull origin main
git checkout your-feature-branch
git rebase main  # or git merge main

# Resolve conflicts in affected files
# Then continue:
git add <resolved-files>
git rebase --continue  # if rebasing
# or
git commit  # if merging
```

## Development Workflow

Follow the [Development Workflow](docs/DEVELOPMENT.md#development-workflow) for:
- Running tests locally
- Code quality checks
- Pre-commit hooks
- Coverage checking

**Before committing**: Always run [pre-commit validation](skills/pre-commit-validation/SKILL.md) to ensure all quality checks pass.

## Code Standards

- **Type hints**: All code must be type-annotated
- **Tests**: All new features must include tests
- **Documentation**: Update docs for user-facing changes
- **Style**: Follow black formatting and ruff linting rules
- **Commits**: Follow [commit message conventions](docs/DEVELOPMENT.md#commit-message-conventions)

## Questions?

- Check the [Development Guide](docs/DEVELOPMENT.md) for setup and workflow
- Review the [Implementation Plan](docs/implementation-plan.md) for project structure
- Open a GitHub Issue for questions or discussions
