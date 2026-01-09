---
name: implementation-plan-updates
description: Defines the pattern for updating the implementation plan when completing phases. Use when marking phases as complete to ensure consistent documentation of implementation status, test coverage, and deliverables.
license: MIT
metadata:
  version: "1.0.0"
  file: "docs/implementation-plan.md"
---

# Implementation Plan Updates Pattern

This skill defines how to update `docs/implementation-plan.md` when completing phases.

## Update Locations

### Phase Header

Add completion marker:

```markdown
**4.1.1. GET /health** ✅ **COMPLETE**
```

### Implementation Notes Section

Add immediately after phase header:

```markdown
**Implementation Notes:**
- Implemented server state tracking with `_server_start_time` and `_server_shutting_down` globals
- Uptime calculated from server start time, rounded to 2 decimal places
- Shutdown state tracked in lifespan context manager
- Timestamp in ISO 8601 format with 'Z' suffix for UTC
```

### Subsection Tests Section

Mark each test as complete:

```markdown
**Subsection Tests** ✅:
- ✅ GET /health returns 200 with status="healthy" when server is running
- ✅ GET /health response includes timestamp in ISO 8601 format
- ✅ GET /health response includes uptime_seconds with 2 decimal precision
- ✅ GET /health response completes within 100ms
- ✅ GET /health returns 503 with status="unhealthy" when shutting down
```

### Test Coverage Section

Update with actual counts:

```markdown
**Test Coverage** ✅:
- **Subsection Tests**: 5 tests implemented and passing
- **Acceptance Criteria**: AC-5.1.1, AC-5.1.2, AC-5.1.3 verified (AC-5.1.4 is for failure case, tested via shutdown)
- **Test File**: `tests/integration/api/test_api_health.py`
```

## Update Pattern by Phase Type

### Domain Models (Phase 1)

```markdown
**1.0. Position Model** ✅ **COMPLETE**

**Implementation Notes:**
- Implemented Position as Pydantic model with row/col validation
- Added bounds checking (0-2) with error codes
- Tests cover all validation cases

**Test Coverage**: ✅
- **Subsection Tests**: 10 tests implemented
- **Acceptance Criteria**: AC-2.1.1 through AC-2.1.10 verified
- **Test File**: `tests/unit/domain/test_position.py`
```

### Game Engine (Phase 2)

```markdown
**2.1. Win Condition Detection** ✅ **COMPLETE**

**Implementation Notes:**
- Implemented check_winner() with row, column, diagonal checks
- Returns winner symbol or None
- Handles tie scenarios correctly

**Test Coverage**: ✅
- **Subsection Tests**: 10 tests implemented
- **Acceptance Criteria**: AC-4.1.1.1 through AC-4.1.1.10 verified
- **Test File**: `tests/unit/game/test_win_conditions.py`
```

### Agent System (Phase 3)

```markdown
**3.2.1. Move Validation** ✅ **COMPLETE**

**Implementation Notes:**
- Implemented _validate_move() with bounds, cell, and game state checks
- Returns list of error codes for multiple validation failures
- Used Position.model_construct() in tests to bypass Pydantic validation

**Subsection Tests** ✅:
- ✅ Validates position bounds (0-2)
- ✅ Validates cell is empty
- ✅ Validates game is not over

**Test Coverage**: ✅
- **Subsection Tests**: 3 tests implemented
- **Acceptance Criteria**: AC-3.4.1 through AC-3.4.3 verified
- **Test File**: `tests/unit/agents/test_executor.py`
```

### API Endpoints (Phase 4)

```markdown
**4.1.1. GET /health** ✅ **COMPLETE**

**Implementation Notes:**
- Implemented server state tracking with globals
- Uptime calculated from server start time
- Shutdown state tracked in lifespan context manager

**Subsection Tests** ✅:
- ✅ Returns 200 with status="healthy" when server is running
- ✅ Response includes timestamp in ISO 8601 format
- ✅ Response includes uptime_seconds with 2 decimal precision
- ✅ Response completes within 100ms
- ✅ Returns 503 with status="unhealthy" when shutting down

**Test Coverage** ✅:
- **Subsection Tests**: 5 tests implemented and passing
- **Acceptance Criteria**: AC-5.1.1, AC-5.1.2, AC-5.1.3 verified
- **Test File**: `tests/integration/api/test_api_health.py`
```

## Phase Deliverables Section

Update the "Phase X Deliverables" section at the end of each phase:

```markdown
**Phase 4 Deliverables:**
- ✅ GET /health endpoint implemented and tested
- ✅ GET /ready endpoint implemented (if complete)
- ✅ 5 API integration tests passing
- ✅ Error handling with proper HTTP status codes
- ⚠️ POST /api/game/new endpoint (in progress)
- ⚠️ POST /api/game/move endpoint (not started)
```

**Note**: Only mark deliverables as ✅ when fully complete. Use ⚠️ for in-progress items.

## Spec References

Ensure spec references are correct:

```markdown
**Spec References:**
- Section 5: API Design
- Section 5.1: Health and Readiness Endpoints
- Section 5.6: HTTP Status Code Mapping
```

## Common Update Patterns

### Adding Implementation Notes

Include:
- Key implementation decisions
- Notable patterns or approaches
- Any deviations from the plan
- Important technical details

### Updating Test Counts

- Count actual tests implemented
- Match test file names
- Note which acceptance criteria are verified
- Mention if some AC are tested indirectly

### Marking Files Complete

```markdown
**Files:**
- `src/api/main.py` ✅ (extended with /health endpoint)
- `tests/integration/api/test_api_health.py` ✅ (created with 5 tests)
```

## Best Practices

1. **Update immediately**: Mark complete right after implementation
2. **Be specific**: Include concrete details in implementation notes
3. **Accurate counts**: Ensure test counts match reality
4. **Check deliverables**: Update deliverables section carefully
5. **Verify AC**: Note which acceptance criteria are covered
6. **File paths**: Use correct relative paths from project root
7. **Consistent format**: Follow established format for consistency

## Common Mistakes to Avoid

### ❌ Don't Mark Unfinished Work

```markdown
**4.2.1. POST /api/game/new** ✅ **COMPLETE**  # WRONG - not implemented yet
```

### ❌ Don't Overcount Tests

```markdown
**Subsection Tests**: 10 tests  # WRONG - only 5 were implemented
```

### ❌ Don't Forget Deliverables

```markdown
**Phase 4 Deliverables:**
- ✅ GET /health endpoint  # Missing other endpoints status
```

### ✅ Correct Format

```markdown
**4.1.1. GET /health** ✅ **COMPLETE**

**Implementation Notes:**
- [Specific implementation details]

**Subsection Tests** ✅:
- ✅ [List of tests with checkmarks]

**Test Coverage** ✅:
- **Subsection Tests**: 5 tests implemented and passing
- **Acceptance Criteria**: AC-5.1.1, AC-5.1.2, AC-5.1.3 verified
- **Test File**: `tests/integration/api/test_api_health.py`
```

## Checklist for Updates

When marking a phase complete, ensure:

- [ ] Phase header marked with ✅ **COMPLETE**
- [ ] Implementation Notes section added
- [ ] All subsection tests marked with ✅
- [ ] Test Coverage section updated with actual counts
- [ ] Acceptance Criteria status noted
- [ ] Test file path is correct
- [ ] Phase Deliverables section updated
- [ ] Spec References are accurate
- [ ] File paths in "Files:" section are correct
