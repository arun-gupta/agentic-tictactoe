# Agent Skills Guide

This document defines conventions and best practices for AI assistants working on this codebase.

## Commit Message Format

All commits MUST follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Format Rules

- **Type** (required): One of the types below, lowercase
- **Scope** (optional, but recommended): Area of codebase affected, lowercase, in parentheses
- **Description** (required): Short summary in imperative mood (e.g., "Add feature" not "Added feature")
- **Body** (optional): Detailed explanation, wrapped at 72 characters
- **Footer** (optional): Breaking changes or issue references

### Commit Types

- `feat`: New feature for users
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, whitespace, etc.)
- `refactor`: Code refactoring (no feature change or bug fix)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system or dependency changes
- `ci`: CI/CD configuration changes
- `chore`: Other changes (maintenance tasks, tooling, etc.)

### Project Scopes

Common scopes used in this project:

- `api`: API layer (`src/api/`)
- `game`: Game engine (`src/game/`)
- `agents`: Agent system (`src/agents/`)
- `domain`: Domain models (`src/domain/`)
- `services`: Service layer (`src/services/`)
- `ui`: UI components (`src/ui/`)
- `utils`: Utility functions (`src/utils/`)
- `tests`: Test files (`tests/`)
- `docs`: Documentation (`docs/`)
- `scripts`: Scripts (`scripts/`)
- `config`: Configuration files

### Examples

#### Feature Commits
```
feat(api): Add GET /health endpoint
feat(agents): Implement Scout agent analysis
feat(game): Add draw detection with inevitable draw logic
```

#### Fix Commits
```
fix(game): Correct turn validation for out-of-bounds moves
fix(api): Handle shutdown state in health endpoint
fix(agents): Fix timeout handling in pipeline fallback
```

#### Documentation Commits
```
docs(plan): Mark Phase 4.1.1 as complete
docs(readme): Update project status and metrics
docs(api): Add API endpoint documentation
```

#### Test Commits
```
test(api): Add integration tests for health endpoint
test(agents): Add executor fallback tests
test(game): Add comprehensive draw condition tests
```

#### Refactoring Commits
```
refactor(agents): Extract fallback logic into separate methods
refactor(domain): Simplify Board model validation
```

#### Multi-scope Commits
When changes span multiple areas, use the primary scope or omit scope:
```
feat: Implement Phase 4.1.1 with health endpoint and tests
fix: Resolve validation errors across game and agents modules
```

#### Detailed Commits (with body)
```
feat(api): Implement GET /health endpoint

- Track server start time for uptime calculation
- Track shutdown state for unhealthy status (503)
- Return status, timestamp (ISO 8601), uptime_seconds, version
- Complete within 100ms (AC-5.1.2)

Tests:
- Add 5 integration tests for health endpoint
- Test healthy status (200), timestamp format, uptime precision
- Test response time (<100ms), shutdown status (503)
- All acceptance criteria verified (AC-5.1.1, AC-5.1.2, AC-5.1.3)

Files:
- src/api/main.py: Add /health endpoint with state tracking
- tests/integration/api/test_api_health.py: Add comprehensive tests
- docs/implementation-plan.md: Mark Phase 4.1.1 as complete
```

### Phase Implementation Commits

For phase implementation commits, use this format:

```
feat(<scope>): Implement Phase X.Y.Z <brief description>

[Optional detailed description of what was implemented]

Tests:
- [List of tests added or updated]

Files:
- [List of files changed with brief description]
```

### Best Practices

1. **Be specific**: "Add health endpoint" is better than "Update API"
2. **Use imperative mood**: "Add feature" not "Added feature" or "Adds feature"
3. **Keep first line short**: < 72 characters when possible
4. **Include scope**: Helps categorize and filter commits
5. **Reference acceptance criteria**: Use AC-X.Y.Z format when applicable
6. **List files changed**: Especially useful for larger commits
7. **Group related changes**: One logical change per commit

### When to Use Each Type

- **feat**: New functionality that users/consumers will see or use
- **fix**: Correcting bugs or incorrect behavior
- **docs**: Only documentation (README, comments, plans, etc.)
- **test**: Only test files (new tests, test updates, test infrastructure)
- **refactor**: Code restructuring without changing behavior
- **chore**: Maintenance tasks, dependency updates, tooling changes

### Multiple Commits for Large Changes

For large features (e.g., implementing a full phase), you may make multiple commits:

```
feat(api): Implement Phase 4.1.1 GET /health endpoint
test(api): Add integration tests for health endpoint
docs(plan): Mark Phase 4.1.1 as complete
```

Or combine into a single detailed commit if all changes are tightly coupled.

---

**Remember**: Always use this format for consistency, better git history, and automatic changelog generation.
