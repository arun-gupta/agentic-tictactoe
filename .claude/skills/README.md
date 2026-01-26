# Project Skills

This directory contains Claude Code skills (slash commands) that define standardized workflows and patterns for this project.

## Available Skills

### 🚀 Subsection Implementation (Primary Workflow)

**Command**: `/subsection-implementation <number>` or `/si <number>` (short alias)

**Purpose**: Complete end-to-end implementation of a single subsection from the implementation plan.

**Usage**:
```
/si 5.1.1
```

Or the full version:
```
/subsection-implementation 5.1.1
```

**What it does**:
1. Clears context for focused work
2. Reads subsection requirements from implementation plan
3. Creates task tracking
4. Implements code following all project patterns
5. Writes comprehensive tests
6. Runs all quality checks (must pass!)
7. Updates documentation with ✅ markers
8. Commits and pushes with proper format

**Orchestrates**: All other skills below

---

### 📋 Phase Implementation

**Skill**: `phase-implementation`

**Purpose**: Standard workflow pattern for implementing features.

**Pattern**: requirements → todos → code → tests → docs → commit

**Key practices**:
- Read implementation plan first
- Track with TODOs
- Test-driven development
- One section at a time
- Update docs immediately
- Commit frequently

---

### ✅ Test Writing

**Skill**: `test-writing`

**Purpose**: Consistent test patterns and naming conventions.

**Test types**:
- Subsection tests: `test_subsection_X_Y_Z_requirement()`
- Acceptance criteria: `test_ac_X_Y_Z_requirement()`
- General tests: `test_feature_description()`

**Coverage targets**:
- Core logic: 100%
- Services: ≥90%
- API: ≥80%
- UI: ≥70%

---

### 💬 Commit Format

**Skill**: `commit-format`

**Purpose**: Conventional Commits specification for consistent git history.

**Format**:
```
<type>(<scope>): <description>

[optional body]
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `build`, `ci`, `chore`

**Example**:
```
feat(agents): Subsection 5.1.1 - Scout LLM enhancement

- Integrate Pydantic AI for board analysis
- Add LLM fallback logic

Tests:
- ✅ 8 subsection tests
```

---

### 🚨 Error Handling

**Skill**: `error-handling`

**Purpose**: Consistent error handling patterns across the codebase.

**Pattern**:
- Use custom error codes
- Return `Result[T]` types
- Proper HTTP status codes for APIs
- Descriptive error messages

---

### 🌐 API Endpoint Implementation

**Skill**: `api-endpoint-implementation`

**Purpose**: Standard patterns for FastAPI endpoints.

**Pattern**:
- Request/response models
- Error handling
- Status codes
- Integration tests
- Documentation

---

### ✅ Pre-commit Validation

**Skill**: `pre-commit-validation`

**Purpose**: Quality checks before committing.

**Checks**:
- Linters (ruff, black)
- Type checker (mypy --strict)
- Tests (pytest with coverage)
- All must pass before commit

---

### 🔀 Feature Branch PR

**Skill**: `feature-branch-pr`

**Purpose**: Creating feature branches and pull requests.

**Pattern**:
- Create feature branch
- Implement changes
- Push branch
- Create PR with description
- Reference issues

---

### 📝 Implementation Plan Updates

**Skill**: `implementation-plan-updates`

**Purpose**: Keeping implementation plan synchronized with actual work.

**Pattern**:
- Mark subsections complete with ✅
- Add Implementation Notes
- Update test coverage
- Document deviations

---

## Skill Usage

### Using a Skill

Skills are invoked with slash commands in Claude Code:

```
/skill-name arguments
```

### Skill Composition

Skills can reference and build upon each other. For example, `subsection-implementation` orchestrates:
- `phase-implementation` for workflow
- `test-writing` for test patterns
- `commit-format` for commit messages
- `error-handling` for error patterns
- `api-endpoint-implementation` for API patterns
- `pre-commit-validation` for quality checks

### Creating New Skills

To create a new skill:

1. Create directory: `skills/skill-name/`
2. Create `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: What this skill does
   license: MIT
   metadata:
     version: "1.0.0"
   ---

   # Skill content here
   ```
3. Document patterns and examples
4. Reference from other skills if needed

## Best Practices

1. **Use subsection-implementation for focused work**: Implements one subsection at a time with full quality checks
2. **Follow established patterns**: All skills define consistent approaches
3. **Quality gates matter**: Never commit without passing all checks
4. **Document as you go**: Update implementation plan immediately
5. **One subsection = one commit**: Keep changes atomic and focused

## Workflow Example

**Goal**: Implement subsection 5.1.1 (Scout LLM Enhancement)

**Command**:
```
/subsection-implementation 5.1.1
```

**Result**:
- ✅ Code implemented in `src/agents/scout.py`
- ✅ 8 subsection tests written and passing
- ✅ All quality checks pass (linters, types, tests)
- ✅ Documentation updated with ✅ markers
- ✅ Committed with proper format
- ✅ Pushed to GitHub

**Time saved**: ~15-20 minutes per subsection (no context switching, no manual quality checks, no forgotten documentation)

## Quality Standards

All skills enforce these quality standards:

- ✅ Type hints on all functions
- ✅ Docstrings (Google style)
- ✅ Error handling with custom codes
- ✅ Comprehensive test coverage
- ✅ Linters pass (ruff, black)
- ✅ Type checker passes (mypy --strict)
- ✅ All tests pass
- ✅ Documentation updated
- ✅ Conventional commit format

## Support

For questions or issues with skills:
- Review the skill's SKILL.md file for details
- Check examples in the skill documentation
- Refer to implementation plan for requirements
- Ask for clarification if patterns are unclear
