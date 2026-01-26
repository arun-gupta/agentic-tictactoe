---
name: si
description: Short alias for subsection-implementation. Implements a single subsection from docs/implementation-plan.md with full automation (clear context → implement → test → commit). Usage: /si 5.1.1
license: MIT
metadata:
  version: "1.0.0"
  alias_for: "subsection-implementation"
  workflow: "clear-context → read → plan → implement → test → validate → document → commit"
---

# Subsection Implementation (Short Alias)

**Alias**: This is a short version of `/subsection-implementation`

## Quick Usage

```
/si 5.1.1
```

Equivalent to:
```
/subsection-implementation 5.1.1
```

## What It Does

Implements a complete subsection from `docs/implementation-plan.md`:

1. **Clear Context** - Start fresh
2. **Read Requirements** - Load subsection from implementation plan
3. **Create Plan** - Track with TaskCreate
4. **Implement Code** - Follow project patterns
5. **Write Tests** - All subsection tests
6. **Run Quality Checks** - Linters, types, tests (must pass!)
7. **Update Documentation** - Mark complete with ✅
8. **Commit & Push** - Proper format

## Complete Workflow

For full details, see: `skills/subsection-implementation/SKILL.md`

### Step 0: Clear Context (Fresh Start)

Start with a clean slate to avoid context pollution.

### Step 1: Read Subsection Requirements

Read `docs/implementation-plan.md` for the specified subsection and extract:
- Subsection title and description
- Implementation notes
- Files to create/modify
- Subsection tests (acceptance criteria)
- Spec references

### Step 2: Create Implementation Plan

Use `TaskCreate` to track implementation tasks:
- Read and understand requirements
- Implement code changes
- Write subsection tests
- Run quality checks
- Update documentation
- Commit and push

### Step 3: Implement Code

Write production code following project patterns:
- Type hints on all functions
- Docstrings (Google style)
- Error handling with custom error codes
- Follow existing patterns

### Step 4: Write Tests

Write tests following `@skills/test-writing/SKILL.md`:
- Test file: `tests/unit/<module>/test_<component>.py`
- Test format: `def test_subsection_X_Y_Z_requirement(self) -> None:`
- Cover all subsection test cases
- Test success and error paths

### Step 5: Run Quality Checks

**CRITICAL**: All checks must pass before proceeding:
```bash
ruff check src/ tests/
black --check src/ tests/
mypy --strict --explicit-package-bases src/
pytest tests/ -v
```

### Step 6: Update Documentation

Update `docs/implementation-plan.md`:
- Add ✅ to subsection title
- Add **Implementation Notes** section
- Mark **Subsection Tests** as ✅
- Add **Test Coverage** section

### Step 7: Commit and Push

Follow `@skills/commit-format/SKILL.md`:
```
<type>(<scope>): Subsection X.Y.Z - <description>

- [Implementation details]

Tests:
- [Subsection tests added]

Files:
- [Files changed with descriptions]
```

## Quality Gates

**Before committing, all MUST be ✅:**

1. ✅ All subsection tests pass
2. ✅ All existing tests still pass
3. ✅ Linters pass (ruff, black)
4. ✅ Type checker passes (mypy --strict)
5. ✅ Documentation updated with ✅
6. ✅ Implementation notes added
7. ✅ Commit message follows format

## Examples

### Basic Usage
```
/si 5.1.1
```

### With Branch
```
/si 5.1.1 --branch feature/scout-llm
```

### Dry Run (show plan)
```
/si 5.1.1 --dry-run
```

## Common Subsections

Current phase (Phase 5 - LLM Integration):
- `/si 5.1.1` - Scout LLM Enhancement
- `/si 5.1.2` - Strategist LLM Enhancement
- `/si 5.1.3` - Executor (verify no LLM)
- `/si 5.2.1` - Environment Variables
- `/si 5.3` - Metrics and Tracking

## Skills Integration

This skill orchestrates:
- `@skills/phase-implementation/SKILL.md` - Workflow pattern
- `@skills/test-writing/SKILL.md` - Test patterns
- `@skills/commit-format/SKILL.md` - Commit format
- `@skills/error-handling/SKILL.md` - Error patterns
- `@skills/api-endpoint-implementation/SKILL.md` - API patterns
- `@skills/pre-commit-validation/SKILL.md` - Quality checks

## Troubleshooting

### "Subsection not found"
Check `docs/implementation-plan.md` for correct subsection number.

### "Prerequisites not complete"
Implement previous subsections first.

### "Tests failing"
Review requirements, fix implementation, re-run tests.

### "Quality checks failing"
Fix linting/type errors, ensure all tests pass.

## Full Documentation

For complete details, see:
- Full workflow: `skills/subsection-implementation/SKILL.md`
- All skills: `skills/README.md`
- Implementation plan: `docs/implementation-plan.md`
