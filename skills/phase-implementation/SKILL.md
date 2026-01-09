---
name: phase-implementation
description: Guides implementation of phases from the implementation plan following the established workflow pattern. Use when implementing any phase or sub-phase to ensure consistent process: read plan, create todos, implement code, write tests, mark complete, commit and push.
license: MIT
metadata:
  version: "1.0.0"
  workflow: "plan -> todos -> code -> tests -> update plan -> commit"
---

# Phase Implementation Pattern

This skill defines the standard workflow for implementing phases from `docs/implementation-plan.md`.

## Implementation Workflow

### 1. Read Implementation Plan

- Locate the phase/sub-phase in `docs/implementation-plan.md`
- Understand the requirements, acceptance criteria, and test coverage
- Identify files to create/modify
- Note any spec references

### 2. Create TODO List

Use `todo_write` tool to track implementation tasks:

```python
todo_write(merge=False, todos=[
    {'id': 'phase_X_Y_implementation', 'content': 'Implement Phase X.Y', 'status': 'in_progress'},
    {'id': 'phase_X_Y_tests', 'content': 'Write tests for Phase X.Y', 'status': 'pending'},
    {'id': 'phase_X_Y_mark_complete', 'content': 'Mark complete in implementation plan', 'status': 'pending'}
])
```

### 3. Implement Code

- Create/modify source files as specified
- Follow project conventions (type hints, docstrings, error codes)
- Use domain models from `src/domain/`
- Implement error handling with custom error codes
- Add necessary imports

### 4. Write Tests

Follow the test-writing pattern:
- Write subsection tests first (for incremental development)
- Then verify acceptance criteria (AC-X.Y.Z format)
- Use descriptive test names: `test_subsection_X_Y_Z_description`
- Add type annotations: `-> None`
- Test both success and error cases

### 5. Run Quality Checks

Before marking complete:
- Run linters: `ruff` and `black`
- Run type checker: `mypy --strict --explicit-package-bases src/`
- Run tests: `pytest tests/ -v`
- Fix any issues

### 6. Update Implementation Plan

Mark the phase as complete in `docs/implementation-plan.md`:

- Add ✅ **COMPLETE** marker to phase header
- Add **Implementation Notes** section with key details
- Mark all subsection tests with ✅
- Update **Test Coverage** section
- Update **Acceptance Criteria** status

### 7. Commit and Push

Follow commit format from `skills/commit-format/SKILL.md`:

```
feat(<scope>): Implement Phase X.Y.Z <brief description>

- [List of key implementations]
- [Key features added]

Tests:
- [List of tests added]

Files:
- [List of files changed with descriptions]

- docs/implementation-plan.md: Mark Phase X.Y.Z as complete
```

Then push to GitHub.

## Phase Types

### Domain Models (Phase 1)

- Implement Pydantic models in `src/domain/`
- Add validators for business rules
- Write unit tests in `tests/unit/domain/`
- Target: 100% coverage on domain layer

### Game Engine (Phase 2)

- Implement game logic in `src/game/engine.py`
- Write comprehensive unit tests
- Test all edge cases (win, draw, invalid moves)
- Target: 100% coverage on game engine

### Agent System (Phase 3)

- Implement agents in `src/agents/`
- Write unit tests for each agent
- Write integration tests for pipeline
- Test timeout and fallback mechanisms

### API Endpoints (Phase 4)

- Follow `skills/api-endpoint-implementation/SKILL.md`
- Create FastAPI routes in `src/api/`
- Write integration tests with TestClient
- Verify acceptance criteria

## Common Patterns

### Error Handling

- Use error codes from `src/domain/errors.py`
- Return `AgentResult` with error codes for agents
- Return HTTP status codes for API endpoints
- Follow `skills/error-handling/SKILL.md`

### Test Organization

- Unit tests: `tests/unit/<module>/test_<component>.py`
- Integration tests: `tests/integration/test_<feature>.py`
- API tests: `tests/integration/api/test_api_<endpoint>.py`

### File Structure

- Source files: `src/<module>/<component>.py`
- Test files mirror source structure
- Follow naming conventions (snake_case)

## Best Practices

1. **Start with implementation plan**: Always read the plan first
2. **Create todos**: Track progress with todo list
3. **Test-driven**: Write tests alongside implementation
4. **Incremental**: Implement one sub-phase at a time
5. **Verify AC**: Ensure acceptance criteria are met
6. **Update plan**: Mark complete immediately after implementation
7. **Commit frequently**: Commit after each completed sub-phase

## Edge Cases

### When Implementation Differs from Plan

- Update the plan to reflect actual implementation
- Document deviations in **Implementation Notes**
- Ensure acceptance criteria are still met

### When Tests Reveal Issues

- Fix issues in code before marking complete
- Update plan if requirements change
- Document lessons learned

### When Multiple Files Need Updates

- Group related changes in single commit
- Use detailed commit message with file list
- Ensure all tests pass before committing
