# Acceptance Criteria Implementation Guide

## Purpose

This document explains how to add formal, testable acceptance criteria throughout the specification to ensure every requirement can be verified through automated tests.

## Pattern: Given-When-Then

All acceptance criteria follow the **Given-When-Then** (Gherkin) format:

```
Given [initial context/state]
When [action/trigger occurs]
Then [expected outcome/assertion]
```

### Benefits

1. **Testable**: Each criterion maps directly to a test case
2. **Unambiguous**: Clear inputs and expected outputs
3. **Verifiable**: Can be automated with testing frameworks
4. **Complete**: Forces specification of edge cases and error conditions

## Examples

### ✅ Good - Testable

```markdown
**Acceptance Criteria:**
- Given row=0, col=0, when Position is created, then position is valid
- Given row=3, col=0, when Position is created, then validation error `ERR_POSITION_OUT_OF_BOUNDS` is raised
- Given Board with empty cells, when `get_empty_positions()` is called, then returns list of all (row, col) tuples where cell is empty
```

These are testable because:
- Specific inputs are defined (row=0, col=0)
- Expected outputs are clear (position is valid, error code, list of tuples)
- Can write: `assert position.is_valid() == True`
- Can write: `assert len(board.get_empty_positions()) == 9`

### ❌ Bad - Not Testable

```markdown
**Validates size**
```

This is not testable because:
- No input specified
- No output specified
- No error conditions defined
- Can't write automated test

### ❌ Bad - Vague

```markdown
**Board should work correctly**
```

This is not testable because:
- "work correctly" is subjective
- No specific behaviors defined
- No measurable outcomes

## Where to Add Acceptance Criteria

### ✅ Completed Sections

The following sections already have formal acceptance criteria:

1. **Section 2: Domain Model Design** ✅ COMPLETE (84 criteria total)
   - Position (5 criteria)
   - Board (10 criteria)
   - Game State (10 criteria)
   - Threat (4 criteria)
   - Opportunity (4 criteria)
   - Strategic Move (5 criteria)
   - Board Analysis (9 criteria)
   - Move Priority (9 criteria)
   - Move Recommendation (6 criteria)
   - Strategy (7 criteria)
   - Move Execution (7 criteria)
   - Agent Result (8 criteria)

2. **Section 3: Agent Architecture** ✅ COMPLETE (60 criteria total)
   - Scout Agent (10 criteria)
   - Strategist Agent (8 criteria)
   - Executor Agent (7 criteria)
   - Agent Interface Contract (5 criteria)
   - Move Priority System (15 criteria)
   - Agent Pipeline Flow (15 criteria)

3. **Section 4: Game State Management** ✅ COMPLETE (71 criteria total)
   - Win Conditions (10 criteria - all 8 winning lines)
   - Draw Conditions (6 criteria - complete and inevitable draw)
   - Legal Move Invariants (10 criteria - all validation rules)
   - Turn Order Rules (9 criteria - strict alternation)
   - State Validation Rules (10 criteria - all 8 validation rules)
   - Game Engine Interface (13 criteria - all methods)
   - Game State Transitions (13 criteria - all state transitions)

4. **Section 5: API Design** ✅ COMPLETE (37 criteria total)
   - POST /api/game/move (8 criteria)
   - GET /api/game/status (4 criteria)
   - POST /api/game/reset (3 criteria)
   - GET /api/game/history (3 criteria)
   - Agent Status Endpoints (5 criteria)
   - Configuration Endpoints (7 criteria)
   - MCP Protocol Endpoints (7 criteria)

### 🔶 Sections Needing Acceptance Criteria

The following sections need formal acceptance criteria added:

#### **Section 6: Web UI Functional Requirements**

User stories already have some acceptance criteria, but add more specific assertions:

**Example for US-001 (Display Game Board)**:

```markdown
**Acceptance Criteria:**
- Given game state with X at (0,0), when board is rendered, then cell (0,0) displays 'X' with color #e94560
- Given game state with O at (1,1), when board is rendered, then cell (1,1) displays 'O' with color #00adb5
- Given game state with empty cells, when board is rendered, then empty cells have background #16213e
- Given game state update, when state changes, then board re-renders within 100ms (per US-023)
- Given 3x3 grid, when rendered, then grid has cell dimensions 100px × 100px with 12px gap
```

#### **Section 12: Error Handling**

For each error in the Failure Matrix, add acceptance criteria:

**Example for LLM Timeout**:

```markdown
**Acceptance Criteria:**
- Given LLM call exceeds 5s (Scout), when timeout occurs, then retries 3 times with exponential backoff (1s, 2s, 4s)
- Given 3 retries exhausted, when timeout persists, then triggers fallback strategy and logs WARNING
- Given timeout on retry attempt 2, when LLM responds, then uses response and cancels remaining retries
- Given fallback triggered, when move completed, then UI shows orange warning icon with "Using fallback" message
- Given timeout event, when logging, then includes agent_name, timeout_duration_ms, retry_count, fallback_used
```

#### **Section 13: Security**

**API Key Validation**:
- Given valid API key format, when validating, then passes validation
- Given invalid API key format, when validating, then returns error `ERR_INVALID_API_KEY`
- Given expired API key, when calling LLM, then returns error `ERR_API_KEY_EXPIRED`

**Input Sanitization**:
- Given malicious input with SQL injection attempt, when processing, then sanitizes input and logs security event
- Given XSS attempt in move reasoning, when rendering, then escapes HTML and displays safely

## Implementation Steps

### For Each Section:

1. **Identify all behaviors** mentioned in the section
2. **For each behavior**, write acceptance criteria covering:
   - Happy path (valid inputs → expected outputs)
   - Edge cases (boundary conditions)
   - Error cases (invalid inputs → specific error codes)
   - Performance requirements (timing, throughput)

3. **Use specific values**:
   - ✅ `Given row=3` (testable)
   - ❌ `Given invalid row` (vague)

4. **Use specific error codes**:
   - ✅ `then raises error ERR_POSITION_OUT_OF_BOUNDS` (testable)
   - ❌ `then raises error` (not specific enough)

5. **Use measurable assertions**:
   - ✅ `then returns list of 9 positions` (testable)
   - ❌ `then returns some positions` (vague)

### Mapping to Tests

Each acceptance criterion should map to one or more test cases:

```python
# Acceptance Criterion:
# Given row=3, col=0, when Position is created, then validation error ERR_POSITION_OUT_OF_BOUNDS is raised

def test_position_out_of_bounds_high():
    with pytest.raises(ValidationError) as exc_info:
        Position(row=3, col=0)
    assert exc_info.value.code == "ERR_POSITION_OUT_OF_BOUNDS"
    assert "row" in exc_info.value.message.lower()

# Acceptance Criterion:
# Given Board with empty cells, when get_empty_positions() is called, then returns list of all (row, col) tuples

def test_board_get_empty_positions():
    board = Board()  # Empty 3x3 board
    empty = board.get_empty_positions()
    assert len(empty) == 9
    assert (0, 0) in empty
    assert (1, 1) in empty
    assert (2, 2) in empty
```

## Test Coverage Goals

- **Domain Models**: 100% of acceptance criteria covered
- **Agent Logic**: 90%+ of acceptance criteria covered (LLM behavior may vary)
- **API Endpoints**: 100% of acceptance criteria covered
- **UI Components**: 80%+ of acceptance criteria covered (visual checks may be manual)
- **Error Handling**: 100% of Failure Matrix scenarios covered

## Tools

**Test Frameworks:**
- **pytest** (Python) - Unit and integration tests
- **Gherkin/Behave** (Python) - BDD tests using Given-When-Then directly
- **Jest** (JavaScript/TypeScript) - Frontend tests
- **Playwright** (JavaScript/TypeScript) - E2E tests

**Example with Behave (Python BDD):**

```gherkin
Feature: Position Validation
  Scenario: Create position with valid coordinates
    Given row is 0 and column is 0
    When I create a Position
    Then the position is valid

  Scenario: Create position with row out of bounds
    Given row is 3 and column is 0
    When I create a Position
    Then a ValidationError with code ERR_POSITION_OUT_OF_BOUNDS is raised
```

## Next Steps

1. Review completed sections (Position, Board, Game State, Domain Models)
2. Add acceptance criteria to remaining sections listed above
3. Ensure all error codes from Failure Matrix are covered
4. Map each criterion to at least one test case
5. Track test coverage and aim for goals listed above

## Questions?

When writing acceptance criteria, ask:
- **Can I write a test for this?** If no, make it more specific
- **What are the edge cases?** Cover boundary conditions
- **What error codes apply?** Reference Section 12 Failure Matrix
- **What are the performance requirements?** Include timing assertions from Section 6, US-023

---

**This is a living document.** Update as patterns evolve and new sections are added.
