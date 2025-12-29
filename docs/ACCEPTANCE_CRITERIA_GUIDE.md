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

1. **Section 2: Domain Model Design**
   - Position (5 criteria)
   - Board (10 criteria)
   - Game State (10 criteria)
   - Threat (4 criteria)
   - Opportunity (4 criteria)
   - Strategic Move (5 criteria)
   - Board Analysis (9 criteria)

### 🔶 Sections Needing Acceptance Criteria

The following sections need formal acceptance criteria added:

#### **Section 2: Domain Model Design** (Remaining)

**Move Priority** (enum):
- Verify each priority level has correct numeric value (IMMEDIATE_WIN=100, BLOCK_THREAT=90, etc.)
- Verify priority ordering for decision logic

**Move Recommendation**:
- Valid creation with position, priority, confidence, reasoning
- Confidence range validation (0.0-1.0)
- Priority enum validation

**Strategy**:
- Primary move is highest priority
- Alternatives sorted by priority descending
- Risk assessment validation (low/medium/high)

**Move Execution**:
- Success status tracking
- Validation error collection
- Execution time measurement
- Priority used matches recommendation

**Agent Result** (wrapper):
- Success result creation with data
- Error result creation with message
- Execution time tracking
- Metadata attachment

#### **Section 3: Agent Architecture**

**Scout Agent**:
- Given board state, when Scout.analyze() is called, then returns BoardAnalysis
- Given empty board, when analyzed, then identifies center as strategic position
- Given opponent two-in-a-row, when analyzed, then identifies threat
- Given AI two-in-a-row, when analyzed, then identifies opportunity
- Given LLM timeout, when analyzing, then returns rule-based fallback analysis
- Given invalid board, when analyzing, then returns error with code `ERR_INVALID_BOARD`

**Strategist Agent**:
- Given BoardAnalysis with threats, when strategy created, then primary move blocks threat (priority=BLOCK_THREAT)
- Given BoardAnalysis with opportunity to win, when strategy created, then primary move takes win (priority=IMMEDIATE_WIN)
- Given BoardAnalysis with multiple moves, when strategy created, then alternatives sorted by priority
- Given no clear moves, when strategy created, then recommends center/corner with reasoning
- Given LLM timeout, when strategizing, then returns rule-based strategy

**Executor Agent**:
- Given Strategy with valid move, when executed, then validates move and returns success
- Given Strategy with invalid move (occupied cell), when executed, then returns validation error `ERR_CELL_OCCUPIED`
- Given Strategy with out-of-bounds move, when executed, then returns validation error `ERR_POSITION_OUT_OF_BOUNDS`
- Given move execution time, when completing, then records execution_time_ms
- Given validation errors, when executing, then collects all errors in validation_errors list

**Coordinator**:
- Given game state, when orchestrating move, then calls Scout → Strategist → Executor in sequence
- Given Scout failure, when orchestrating, then uses rule-based Scout fallback
- Given Strategist failure, when orchestrating, then uses Scout's top opportunity
- Given Executor failure, when orchestrating, then uses Strategist's primary move directly
- Given all agents succeed, when orchestrating, then returns final move with full reasoning chain
- Given timeout after 15 seconds, when orchestrating, then triggers fallback and completes

#### **Section 4: Game State Management**

**Win Detection**:
- Given three X's in row 0, when checking win, then returns winner='X'
- Given three O's in column 1, when checking win, then returns winner='O'
- Given three X's on main diagonal (0,0)→(1,1)→(2,2), when checking win, then returns winner='X'
- Given three O's on anti-diagonal (0,2)→(1,1)→(2,0), when checking win, then returns winner='O'
- Given no three-in-a-row, when checking win, then returns winner=None

**Draw Detection**:
- Given all 9 cells occupied and no winner, when checking draw, then returns is_draw=True
- Given 8 cells occupied and no winner, when checking draw, then returns is_draw=False

**Move Validation**:
- Given empty cell (1,1), when validating move to (1,1), then validation passes
- Given occupied cell (1,1) with 'X', when validating move to (1,1), then validation fails with `ERR_CELL_OCCUPIED`
- Given position (3,3), when validating move, then validation fails with `ERR_POSITION_OUT_OF_BOUNDS`
- Given game already over, when validating move, then validation fails with `ERR_GAME_OVER`

**Game Engine**:
- Given valid move, when make_move() called, then updates board, increments move_number, switches current_player
- Given invalid move, when make_move() called, then returns error, does not modify state
- Given new game, when reset() called, then clears board, resets move_number to 0, sets current_player to player

#### **Section 5: API Design**

For each endpoint, define:
- Valid request → expected 200 response
- Invalid request → expected 400/422 response with error code
- Missing auth → expected 401 response
- Server error → expected 500 response

**Example for POST /api/game/move**:

```markdown
**Acceptance Criteria:**
- Given valid move request `{"position": {"row": 1, "col": 1}}`, when POST /api/game/move, then returns 200 with updated game_state
- Given invalid position `{"position": {"row": 3, "col": 3}}`, when POST /api/game/move, then returns 422 with error code `ERR_POSITION_OUT_OF_BOUNDS`
- Given occupied cell `{"position": {"row": 0, "col": 0}}` where (0,0) has 'X', when POST /api/game/move, then returns 422 with error code `ERR_CELL_OCCUPIED`
- Given game over state, when POST /api/game/move, then returns 422 with error code `ERR_GAME_OVER`
- Given malformed JSON, when POST /api/game/move, then returns 400 with error code `ERR_INVALID_REQUEST`
- Given missing position field, when POST /api/game/move, then returns 422 with error code `ERR_MISSING_FIELD`
```

**Apply to all endpoints:**
- POST /api/game/new
- POST /api/game/move
- GET /api/game/status
- POST /api/game/reset
- GET /api/game/history
- GET /api/metrics/game/{game_id}
- WebSocket /ws/game

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
