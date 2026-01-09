# Tic-Tac-Toe Multi-Agent Game - Implementation Plan

## Technology Stack

### Target Language: Python 3.11+

**Spec Reference**: Section 14.1 - Recommended Python Stack

### Core Frameworks and Libraries

**Web Framework:**
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI
- **Pydantic** - Data validation and settings management

**Testing:**
- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **pytest-asyncio** - Async test support

**LLM Integration:**
- **Pydantic AI** - Selected framework for this implementation (see rationale below)
- See Section 19 for comprehensive framework comparison and alternatives
- **openai** - OpenAI SDK (used by Pydantic AI for OpenAI provider)
- **anthropic** - Anthropic SDK (used by Pydantic AI for Anthropic provider)
- **google-generativeai** - Google SDK (used by Pydantic AI for Google Gemini provider)

**Framework Selection Rationale** (based on Section 19 guidance):

This implementation uses **Pydantic AI** for the following reasons (per Section 19 recommendations for this project):

1. **Type-Safe Agent Workflows**: This project uses three specialized agents (Scout, Strategist, Executor) with defined workflows. Pydantic AI provides agent workflow abstractions that align well with this architecture.

2. **Pydantic Integration**: The project extensively uses Pydantic v2 for domain models (Section 2). Pydantic AI is built by the Pydantic team and provides excellent integration with existing Pydantic models, enabling seamless type-safe structured outputs.

3. **Balanced Features**: Pydantic AI offers a good balance - more agent abstractions than Instructor (which focuses only on structured outputs), but lighter weight than LangChain (which may be overkill for this use case).

4. **Multi-Provider Support**: Pydantic AI supports multiple LLM providers (OpenAI, Anthropic, Google Gemini) as required by the specification.

5. **Modern Python**: Clean, modern API design that fits well with FastAPI and Python 3.11+ stack.

**Alternative Considered**: Instructor + LiteLLM/Direct SDKs was also recommended in Section 19. Instructor was considered for maximum type safety with minimal overhead. However, Pydantic AI was selected because:

- **Agent Definitions**: Pydantic AI provides `Agent` as a first-class concept, making it easier to define reusable agent components (Scout, Strategist) with clear interfaces
- **Structured Outputs Built-In**: While Instructor focuses solely on structured outputs, Pydantic AI combines structured outputs with agent abstractions, providing a more complete solution
- **Simpler Implementation**: With Pydantic AI, agents are defined as `Agent` instances with response models, reducing boilerplate compared to using Instructor + manual agent coordination code
- **Future Extensibility**: If agent-to-agent communication patterns evolve beyond the coordinator pattern, Pydantic AI's agent abstractions provide a foundation for more complex workflows

Note: This project uses a coordinator pattern (Section 3) where agents don't directly communicate - the coordinator orchestrates the pipeline. Pydantic AI's agent abstractions still provide value through cleaner agent definitions and structured outputs, even with coordinator-based orchestration.

**Type Safety:**
- **mypy** - Static type checker
- **pydantic** - Runtime type validation

**Development Tools:**
- **black** - Code formatter
- **ruff** - Fast linter
- **pre-commit** - Git hooks for quality checks

**Project Structure:**
```
agentic-tictactoe/
├── src/
│   ├── domain/          # Domain models (Section 2)
│   ├── engine/          # Game engine (Section 4.1)
│   ├── agents/          # AI agents (Section 3)
│   ├── api/             # REST API (Section 5)
│   ├── ui/              # Web UI (Section 6)
│   └── config/          # Configuration (Section 9)
├── tests/
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── docs/                # Documentation
├── pyproject.toml       # Python dependencies
└── README.md
```

---

## Implementation Phases

### Phase 0: Project Setup and Foundation ✅

**Duration**: 1-2 days

**Goal**: Set up project structure, dependencies, and development environment

**Status**: ✅ Complete - All tasks (0.1, 0.2, 0.3, 0.4) completed

**Tasks:**

**0.1. Initialize Python Project** ✅
- ✅ Create virtual environment: `python -m venv .venv`
- ✅ Initialize `pyproject.toml` with dependencies (Section 14.1)
- ✅ Set up development tools (black, ruff, mypy, pre-commit)
- ✅ Configure pytest with coverage settings

**0.2. Set Up Project Structure** ✅
- ✅ Create directory structure as defined in Section 7
- ✅ Add `__init__.py` files for all packages
- ✅ Create placeholder files for main modules
- ✅ Set up logging configuration (Section 17)

**0.3. Set Up Basic GitHub Actions CI Pipeline** ✅

Create `.github/workflows/ci.yml` with a **minimal** pipeline to get started:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest black ruff

    - name: Run linting (black)
      run: black --check src/ tests/ || true  # Don't fail on first run

    - name: Run linting (ruff)
      run: ruff check src/ tests/ || true  # Don't fail on first run

    - name: Run tests
      run: pytest tests/ -v || echo "No tests yet"
```

**Basic Pipeline Features:**
- ✅ Runs on every push and PR
- ✅ Sets up Python 3.11
- ✅ Installs minimal dependencies
- ✅ Runs basic linting (won't fail build initially)
- ✅ Runs tests (if any exist)
- ⏸️ No coverage reporting yet (Phase 1)
- ⏸️ No type checking yet (Phase 1)
- ⏸️ No Docker build yet (Phase 1)

**Why minimal?** This gets CI working immediately without blocking your work. You can commit code even if linting isn't perfect yet.

**0.4. Set Up Basic Pre-commit Hooks (Optional but Recommended)** ✅

Create `.pre-commit-config.yaml` with **minimal** hooks for fast local feedback:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict
```

**Install pre-commit:**
```bash
pip install pre-commit
pre-commit install
```

**Basic Pre-commit Features:**
- ✅ Auto-format code with black (runs before commit)
- ✅ Lint with ruff (auto-fixes issues)
- ✅ Remove trailing whitespace
- ✅ Fix end-of-file newlines
- ✅ Check YAML syntax
- ⏸️ No type checking yet (Phase 1)
- ⏸️ No test running yet (Phase 1)

**Note**: Pre-commit hooks can be skipped with `git commit --no-verify` if needed. CI will still catch issues.

**Acceptance Criteria (Phase 0):**
- ✅ Project builds and installs successfully
- ✅ GitHub Actions basic CI pipeline runs on push/PR
- ✅ `pytest` runs (even with no tests yet)
- ✅ `black` and `ruff` linting runs (non-blocking)
- ✅ Pre-commit hooks installed (optional, but recommended)
- ⏸️ Docker setup deferred to Phase 1
- ⏸️ Coverage reporting deferred to Phase 1
- ⏸️ Type checking deferred to Phase 1

**Spec References:**
- Section 7: Project Structure
- Section 14.1: Recommended Python Stack
- Section 11: Testing Strategy

---

### Phase 1: Domain Models (Foundation Layer) ✅

**Duration**: 3-5 days

**Goal**: Implement all domain models with validation and testing, and enhance CI/CD pipeline

**Why First**: Domain models are the foundation - they're used by everything else. They have no dependencies and can be fully tested in isolation.

**Status**: ✅ **COMPLETE** - All sub-phases (1.0, 1.1, 1.2, 1.3) implemented and tested.

#### 1.0. Core Game Entities ✅

**Spec Reference**: Section 2 - Core Game Entities

**Files to Create:**
- `src/domain/models.py`
- `tests/unit/domain/test_position.py`
- `tests/unit/domain/test_board.py`
- `tests/unit/domain/test_game_state.py`

**Implementation Order:**

**1.0.1. Position** ✅
- ✅ Implement `Position` class with row/col validation (0-2 range)
- ✅ Add immutability (frozen dataclass or Pydantic BaseModel)
- ✅ Implement `__hash__` and `__eq__` for dictionary/set usage
- ✅ Add validation for `E_POSITION_OUT_OF_BOUNDS`

**Test Coverage**: AC-2.1.1 through AC-2.1.5 (5 acceptance criteria) ✅

**1.0.2. Board** ✅
- ✅ Implement `Board` class as 3x3 grid
- ✅ Add methods: `get_cell()`, `set_cell()`, `is_empty()`, `get_empty_positions()`
- ✅ Validate board size is exactly 3x3
- ✅ Raise `E_INVALID_BOARD_SIZE` for invalid sizes

**Test Coverage**: AC-2.2.1 through AC-2.2.10 (10 acceptance criteria) ✅

**1.0.3. GameState** ✅
- ✅ Implement `GameState` with board, players, move tracking
- ✅ Add helper methods: `get_current_player()`, `get_opponent()`
- ✅ Track game over status, winner, draw
- ✅ Integrate with Board validation

**Test Coverage**: AC-2.3.1 through AC-2.3.10 (10 acceptance criteria) ✅

#### 1.1. Agent Domain Models ✅

**Spec Reference**: Section 2 - Agent Domain Models

**Files to Create:**
- `src/domain/agent_models.py` ✅
- `tests/unit/domain/test_agent_models.py` ✅

**Implementation Order:**

**1.1.1. Threat** ✅
- ✅ Implement `Threat` with position, line_type, line_index, severity
- ✅ Validate line_type is one of: 'row', 'column', 'diagonal'
- ✅ Validate line_index is 0-2
- ✅ Error codes: `E_INVALID_LINE_TYPE`, `E_INVALID_LINE_INDEX`

**Test Coverage**: AC-2.4.1 through AC-2.4.4 (4 acceptance criteria) ✅

**1.1.2. Opportunity** ✅
- ✅ Implement `Opportunity` with position, line_type, line_index, confidence
- ✅ Validate confidence is 0.0-1.0 (float)
- ✅ Error code: `E_INVALID_CONFIDENCE`

**Test Coverage**: AC-2.5.1 through AC-2.5.4 (4 acceptance criteria) ✅

**1.1.3. StrategicMove** ✅
- ✅ Implement `StrategicMove` with position, move_type, priority, reasoning
- ✅ Validate move_type is one of: 'center', 'corner', 'edge', 'fork', 'block_fork'
- ✅ Validate priority is 1-10
- ✅ Validate reasoning is non-empty string
- ✅ Error codes: `E_INVALID_MOVE_TYPE`, `E_INVALID_PRIORITY`, `E_MISSING_REASONING`

**Test Coverage**: AC-2.6.1 through AC-2.6.5 (5 acceptance criteria) ✅

**1.1.4. BoardAnalysis** ✅
- ✅ Implement `BoardAnalysis` with threats, opportunities, strategic_moves
- ✅ Add game_phase ('opening', 'midgame', 'endgame')
- ✅ Add board_evaluation_score (-1.0 to 1.0)
- ✅ Error codes: `E_INVALID_GAME_PHASE`, `E_INVALID_EVAL_SCORE`

**Test Coverage**: AC-2.7.1 through AC-2.7.9 (9 acceptance criteria) ✅

**1.1.5. MovePriority (Enum)** ✅
- ✅ Implement `MovePriority` enum with 8 levels and numeric values
- ✅ IMMEDIATE_WIN=100, BLOCK_THREAT=90, FORCE_WIN=80, etc.
- ✅ Ensure enum values are comparable (higher priority > lower priority)

**Test Coverage**: AC-2.8.1 through AC-2.8.9 (9 acceptance criteria) ✅

**1.1.6. MoveRecommendation** ✅
- ✅ Implement `MoveRecommendation` with position, priority, confidence, reasoning
- ✅ Validate all fields per constraints
- ✅ Support optional outcome_description

**Test Coverage**: AC-2.9.1 through AC-2.9.6 (6 acceptance criteria) ✅

**1.1.7. Strategy** ✅
- ✅ Implement `Strategy` with primary_move, alternatives, game_plan, risk_assessment
- ✅ Validate alternatives are sorted by priority (descending)
- ✅ Validate risk_assessment is 'low', 'medium', or 'high'
- ✅ Error codes: `E_MISSING_PRIMARY_MOVE`, `E_INVALID_RISK_LEVEL`

**Test Coverage**: AC-2.10.1 through AC-2.10.7 (7 acceptance criteria) ✅

**1.1.8. MoveExecution** ✅
- ✅ Implement `MoveExecution` with position, success, validation_errors, execution_time_ms
- ✅ Support validation error list
- ✅ Track actual_priority_used
- ✅ Error code: `E_INVALID_EXECUTION_TIME`

**Test Coverage**: AC-2.11.1 through AC-2.11.7 (7 acceptance criteria) ✅

#### 1.2. Result Wrappers ✅

**Spec Reference**: Section 2 - Result Wrappers

**Files to Create:**
- `src/domain/result.py` ✅
- `tests/unit/domain/test_result.py` ✅

**1.2.1. AgentResult** ✅
- ✅ Implement generic `AgentResult[T]` wrapper
- ✅ Add factory methods: `AgentResult.success()`, `AgentResult.error()`
- ✅ Track execution_time_ms, timestamp (ISO 8601), error_code, metadata
- ✅ Validate timestamp format, execution time ≥ 0
- ✅ Error codes: `E_MISSING_DATA`, `E_MISSING_ERROR_MESSAGE`, `E_INVALID_EXECUTION_TIME`

**Test Coverage**: AC-2.12.1 through AC-2.12.8 (8 acceptance criteria) ✅

#### 1.3. Enhance CI/CD Pipeline ✅

**After implementing domain models**, upgrade the CI/CD pipeline from Phase 0 to enforce strict type checking and coverage requirements on the implemented code:

**Update `.github/workflows/ci.yml`:**

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov black ruff mypy

    - name: Run linting (black)
      run: black --check src/ tests/

    - name: Run linting (ruff)
      run: ruff check src/ tests/

    - name: Run type checking (mypy)
      run: mypy src/ --strict

    - name: Run tests with coverage
      run: pytest tests/ --cov=src --cov-report=xml --cov-report=term --cov-fail-under=80

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

**Enhanced Pipeline Features:**
- ✅ Strict type checking with mypy
- ✅ Coverage threshold enforced (80%)
- ✅ Coverage reporting to Codecov
- ✅ All checks now blocking (must pass)
- ⏸️ Docker build deferred to Phase 9 (when containerization is needed)

**Enhance Pre-commit Hooks** ✅

**Update `.pre-commit-config.yaml`** from Phase 0 by **adding** the `local` repo section with mypy and pytest hooks.

**What to Add:**

Add this new section to your existing `.pre-commit-config.yaml` file (after the `pre-commit-hooks` repo section):

```yaml
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true

      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
        args: [--strict]
```

**Complete Updated `.pre-commit-config.yaml` (for reference):**

The full file should now contain all hooks from Phase 0 **plus** the new local hooks:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-merge-conflict

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true

      - id: mypy
        name: mypy
        entry: mypy
        language: system
        types: [python]
        args: [--strict]
```

**After updating the config file:**

```bash
# Update pre-commit hooks (pulls new hook definitions)
pre-commit autoupdate

# Reinstall hooks to pick up changes
pre-commit install --overwrite
```

**Enhanced Pre-commit Features:** ✅
- ✅ All basic hooks from Phase 0 (black, ruff, file fixes) - **unchanged**
- ✅ **NEW**: Type checking with mypy (strict mode)
- ✅ **NEW**: Run tests before commit
- ✅ All checks can be skipped with `--no-verify` if needed

**Note**: Pre-commit hooks provide fast local feedback. CI/CD is the final quality gate and will catch issues even if pre-commit is skipped.

**Phase 1 Deliverables:** ✅
- ✅ Enhanced CI/CD pipeline with coverage and type checking
- ✅ All domain models implemented with full validation
- ✅ 168 unit tests passing (92% coverage overall, 100% on domain layer)
- ✅ Type checking passes with mypy --strict
- ✅ Coverage reporting to Codecov
- ✅ No dependencies on other modules (pure domain logic)

**Spec References:**
- Section 2: Domain Model Design (complete)
- Section 2.1: Machine-Verifiable Schema Definitions

---

### Phase 2: Game Engine (Business Logic Layer) ✅

**Duration**: 3-4 days

**Goal**: Implement game rules, win/draw detection, and move validation. **Enables human vs human gameplay.**

**Why Second**: Game engine depends only on domain models. It implements pure business logic without agents or API concerns.

**Status**: ✅ **COMPLETE** - All 5 sub-tasks (2.0-2.5) implemented and tested. Game fully playable (human vs human).

#### 2.0. Win Condition Detection ✅

**Spec Reference**: Section 4.1 - Formal Game Rules - Win Conditions Enumeration

**Files to Create:**
- `src/game/engine.py` ✅
- `tests/unit/game/test_win_conditions.py` ✅

**Implementation:**
- Check all 8 winning lines (3 rows, 3 columns, 2 diagonals)
- Win detection MUST check all lines after each move
- Return winner symbol (X or O) or None

**Test Coverage**: AC-4.1.1.1 through AC-4.1.1.10 (10 acceptance criteria) ✅

**Key Test Cases:**
- Row wins (3 tests) ✅
- Column wins (3 tests) ✅
- Diagonal wins (2 tests) ✅
- No win conditions (2 tests) ✅

#### 2.1. Draw Condition Detection ✅

**Spec Reference**: Section 4.1 - Draw Conditions

**Files:**
- `src/game/engine.py` ✅ (extend)
- `tests/unit/game/test_draw_conditions.py` ✅

**Implementation:**
- ✅ **Mandatory**: Complete draw (MoveCount=9, no winner)
- ✅ **Optional**: Inevitable draw (early detection when no winning moves remain)
- ✅ Implement inevitable draw algorithm from spec (simulate all remaining moves)

**Test Coverage**: AC-4.1.2.1 through AC-4.1.2.6 (6 acceptance criteria) ✅

#### 2.2. Move Validation ✅

**Spec Reference**: Section 4.1 - Illegal Move Conditions

**Files:**
- `src/game/engine.py` ✅ (extend)
- `tests/unit/game/test_move_validation.py` ✅

**Implementation:**
- ✅ Validate position bounds (0-2)
- ✅ Check cell is empty
- ✅ Verify game is not over
- ✅ Validate player symbol (X or O)
- ✅ Check correct turn order
- ✅ Error codes: `E_MOVE_OUT_OF_BOUNDS`, `E_CELL_OCCUPIED`, `E_GAME_ALREADY_OVER`, `E_INVALID_PLAYER`, `E_INVALID_TURN`

**Test Coverage**: AC-4.1.3.1 through AC-4.1.3.10 (10 acceptance criteria) ✅

#### 2.3. Turn Order and State Transitions ✅

**Spec Reference**: Section 4.1 - Turn Order Rules, State Transitions

**Files:**
- `src/game/engine.py` ✅ (extended with make_move method)
- `tests/unit/game/test_turn_order.py` ✅

**Implementation:**
- ✅ Turn alternation: Player (even moves) → AI (odd moves)
- ✅ Move number increments after each move
- ✅ State transitions: IN_PROGRESS → WON or DRAW
- ✅ Immutable transitions (cannot restart without reset)

**Test Coverage**: AC-4.1.4.1 through AC-4.1.4.9 (9 acceptance criteria) ✅

#### 2.4. State Validation ✅

**Spec Reference**: Section 4.1 - State Validation Rules

**Files:**
- `src/game/engine.py` ✅ (extended with validate_state method)
- `tests/unit/game/test_state_validation.py` ✅

**Implementation:**
- ✅ Validate board consistency (symbol counts)
- ✅ Verify move number matches board state
- ✅ Check at most one winner exists
- ✅ Validate game over state is terminal
- ✅ Added error codes: E_INVALID_SYMBOL_BALANCE, E_MULTIPLE_WINNERS, E_WIN_NOT_FINALIZED

**Test Coverage**: AC-4.1.5.1 through AC-4.1.5.10 (10 acceptance criteria) ✅

#### 2.5. Game Engine Interface ✅

**Spec Reference**: Section 4.1 - Game Engine Interface

**Files:**
- `src/game/engine.py` ✅ (finalized with complete public API)
- `tests/unit/game/test_game_engine_interface.py` ✅

**Implementation:**
- ✅ Public API: `make_move()`, `check_winner()`, `is_game_over()`, `reset_game()`
- ✅ Additional methods: `validate_move()`, `check_draw()`, `get_available_moves()`, `get_current_state()`, `validate_state()`
- ✅ Return standardized results (success/error with codes)
- ✅ Maintain game state internally
- ✅ Provide `get_current_state()` for read-only access

**Test Coverage**: AC-4.1.6.1 through AC-4.1.6.13 (13 acceptance criteria) ✅

**Phase 2 Deliverables:**
- ✅ Complete game engine with all rules implemented
- ✅ 74 unit tests passing (100% coverage on game engine)
- ✅ Game playable without AI (human vs human via engine directly)
- ✅ All edge cases handled (invalid moves, draw detection, state validation, etc.)
- ✅ Public API finalized and tested

**Spec References:**
- Section 4.1: Game Engine Design (complete)
- Section 4: Game State Management

---

### Phase 3: Agent System (AI Layer)

**Duration**: 5-7 days

**Goal**: Implement Scout, Strategist, and Executor agents with fallback strategies. **Enables human vs AI gameplay.**

**Why Third**: Agents depend on domain models and game engine. Start with rule-based logic, add LLM integration later.

#### 3.0. Scout Agent (Board Analysis) ✅

**Spec Reference**: Section 3 - Agent Responsibilities - Scout Agent

**Files Created:**
- ✅ `src/agents/scout.py`
- ✅ `src/agents/base.py` (base agent interface)
- ✅ `tests/unit/agents/test_scout.py`

**Implementation Order:**

**3.0.1. Rule-Based Threat Detection** ✅
- ✅ Scan all 8 lines for opponent two-in-a-row + one empty
- ✅ Return `Threat` objects with blocking positions
- ✅ No LLM needed for this (pure algorithmic)

**3.0.2. Rule-Based Opportunity Detection** ✅
- ✅ Scan all 8 lines for AI two-in-a-row + one empty
- ✅ Return `Opportunity` objects with winning positions
- ✅ Confidence = 1.0 for immediate wins

**3.0.3. Strategic Position Analysis** ✅
- ✅ Identify center position (1,1)
- ✅ Identify corner positions (0,0), (0,2), (2,0), (2,2)
- ✅ Identify edge positions (0,1), (1,0), (1,2), (2,1)
- ✅ Return `StrategicMove` list

**3.0.4. Game Phase Detection** ✅
- ✅ Opening: move_number 0-2
- ✅ Midgame: move_number 3-6
- ✅ Endgame: move_number 7-9

**3.0.5. Board Evaluation Score** ✅
- ✅ Calculate evaluation based on position control
- ✅ Range: -1.0 (opponent winning) to +1.0 (AI winning)
- ✅ Simple heuristic: count potential winning lines

**3.0.6. BoardAnalysis Assembly** ✅
- ✅ Combine all analyses into `BoardAnalysis` object
- ✅ Return wrapped in `AgentResult` with success status
- ✅ Track execution time

**Test Coverage**: AC-3.1.1 through AC-3.1.10 (10 acceptance criteria)

**Note**: LLM integration for Scout will be added in Phase 5. For now, rule-based analysis is sufficient and allows agents to function without LLM dependency.

#### 3.1. Strategist Agent (Move Selection) ✅

**Spec Reference**: Section 3 - Agent Responsibilities - Strategist Agent

**Files Created:**
- ✅ `src/agents/strategist.py`
- ✅ `tests/unit/agents/test_strategist.py`

**Implementation:**

**3.1.1. Priority-Based Move Selection** ✅
- ✅ Implement priority ordering per Section 3.5 - Move Priority System:
  1. IMMEDIATE_WIN (100) - Win on this move
  2. BLOCK_THREAT (90) - Block opponent win
  3. FORCE_WIN (80) - Create fork (two winning lines)
  4. PREVENT_FORK (70) - Block opponent fork
  5. CENTER_CONTROL (50) - Take center
  6. CORNER_CONTROL (40) - Take corner
  7. EDGE_PLAY (30) - Take edge
  8. RANDOM_VALID (10) - Any valid move

**Subsection Tests** (3 tests for incremental development): ✅
- ✅ Immediate win gets highest priority
- ✅ Block threat gets second priority
- ✅ Win takes priority over blocking threat

**3.1.2. Strategy Assembly** ✅
- ✅ Convert `BoardAnalysis` into `Strategy`
- ✅ Select primary move (highest priority)
- ✅ Generate 2+ alternative moves (sorted by priority descending)
- ✅ Create game plan (string explanation)
- ✅ Assess risk level (low/medium/high)

**Subsection Tests** (4 tests for incremental development): ✅
- ✅ Strategy includes primary move recommendation
- ✅ Strategy includes alternatives sorted by priority
- ✅ Strategy includes game plan explanation
- ✅ Strategy includes risk assessment

**3.1.3. Confidence Scoring** ✅
- ✅ Assign confidence values per priority level (spec Section 3.5)
- ✅ IMMEDIATE_WIN: confidence = 1.0
- ✅ BLOCK_THREAT: confidence = 0.95
- ✅ CENTER_CONTROL: confidence = 0.7
- ✅ etc.

**Subsection Tests** (3 tests for incremental development): ✅
- ✅ Immediate win gets confidence = 1.0
- ✅ Block threat gets confidence = 0.95
- ✅ Center control gets confidence = 0.7

**Test Coverage**: ✅
- **Subsection Tests**: ✅ 10 tests (3 + 4 + 3) for incremental development and debugging
- **Acceptance Criteria**: ✅ AC-3.2.1 through AC-3.2.8 (8 official tests for final verification)
- **Total**: ✅ 18 tests for Phase 3.1 - ALL PASSING

#### 3.2. Executor Agent (Move Execution)

**Spec Reference**: Section 3 - Agent Responsibilities - Executor Agent

**Files to Create:**
- `src/agents/executor.py`
- `tests/unit/agents/test_executor.py`

**Implementation:**

**3.2.1. Move Validation** ✅
- ✅ Validate recommended move from Strategist
- ✅ Check position is valid and empty
- ✅ Verify game is not over
- ✅ Collect validation errors if any

**Subsection Tests** (3 tests for incremental development): ✅
- ✅ Validates position is within bounds (0-2)
- ✅ Validates cell is empty
- ✅ Validates game is not over

**3.2.2. Move Execution** ✅
- ✅ Call game engine's `make_move()`
- ✅ Track execution time
- ✅ Return `MoveExecution` with success status
- ✅ Record actual priority used

**Subsection Tests** (3 tests for incremental development): ✅
- ✅ Successfully executes valid move via game engine
- ✅ Tracks execution time in milliseconds
- ✅ Records actual priority used in MoveExecution

**3.2.3. Fallback Handling** ✅
- ✅ If primary move fails, try alternatives
- ✅ If all alternatives fail, select random valid move
- ✅ Always return a valid move or clear error

**Subsection Tests** (3 tests for incremental development): ✅
- ✅ Falls back to first alternative when primary move fails
- ✅ Falls back to random valid move when all alternatives fail
- ✅ Returns clear error when no valid moves available

**Test Coverage**: ✅
- **Subsection Tests**: ✅ 9 tests (3 + 3 + 3) for incremental development and debugging
- **Acceptance Criteria**: AC-3.3.1 through AC-3.3.7 (7 official tests for final verification) - TODO
- **Total**: 9 subsection tests for Phase 3.2 - ALL PASSING

#### 3.3. Agent Pipeline Orchestration

**Spec Reference**: Section 3 - Agent Pipeline Flow

**Files to Create:**
- `src/agents/pipeline.py`
- `tests/integration/test_agent_pipeline.py`

**Implementation:**

**3.3.1. Pipeline Coordinator** ✅
- ✅ Orchestrate Scout → Strategist → Executor flow
- ✅ Pass outputs between agents (typed domain models)
- ✅ Handle agent failures gracefully
- ⏸️ Implement timeout handling (Section 3.3) - Deferred to 3.3.2

**Subsection Tests** (5 tests for incremental development): ✅
- ✅ Orchestrates Scout → Strategist → Executor in correct order
- ✅ Passes BoardAnalysis from Scout to Strategist
- ✅ Passes Strategy from Strategist to Executor
- ✅ Returns final MoveExecution result
- ✅ Handles agent failures and returns error result

**3.3.2. Timeout Configuration** ✅
- ✅ Per-agent timeouts: Scout (5s), Strategist (3s), Executor (2s)
- ✅ Total pipeline timeout: 15s (Section 3.6)
- ⏸️ Trigger fallback after timeout - Deferred to 3.3.3

**Subsection Tests** (4 tests for incremental development): ✅
- ✅ Enforces Scout timeout at 5 seconds
- ✅ Enforces Strategist timeout at 3 seconds
- ✅ Enforces Executor timeout at 2 seconds
- ✅ Enforces total pipeline timeout at 15 seconds

**3.3.3. Fallback Strategy** ✅
- ✅ On Scout timeout: Use rule-based analysis only
- ✅ On Strategist timeout: Use simple priority selection
- ✅ On Executor timeout: Select random valid move
- ✅ Always produce a move within 15s (spec requirement)

**Subsection Tests** (6 tests for incremental development): ✅
- ✅ Scout timeout triggers rule-based analysis fallback
- ✅ Strategist timeout triggers priority-based selection fallback
- ✅ Executor timeout triggers random valid move fallback
- ✅ Pipeline completes within 15 seconds even with all timeouts
- ✅ Fallback strategy produces valid move
- ✅ Records which fallback was used in result metadata

**Test Coverage**:
- **Subsection Tests**: 15 tests (5 + 4 + 6) for incremental development and debugging
- **Acceptance Criteria**: AC-3.6.1 through AC-3.6.41 (41 official tests for final verification)
- **Total**: 56 tests for Phase 3.3

**Phase 3 Deliverables:**
- ✅ All three agents implemented with rule-based logic
- ✅ Agent pipeline orchestrates Scout → Strategist → Executor
- ✅ **106 tests passing**:
  - Scout: 10 tests (already complete)
  - Strategist: 18 tests (10 subsection + 8 AC)
  - Executor: 16 tests (9 subsection + 7 AC)
  - Pipeline: 56 tests (15 subsection + 41 AC)
  - Integration: 6 tests (end-to-end scenarios)
- ✅ AI can play full game using rule-based decisions (no LLM yet)
- ✅ Timeout and fallback mechanisms working

**Spec References:**
- Section 3: Agent Architecture (complete except LLM integration)
- Section 3.3: Agent Timeout Configuration
- Section 3.5: Move Priority System
- Section 3.6: Agent Pipeline Flow

---

### Phase 4: REST API Layer

**Duration**: 3-4 days

**Goal**: Implement FastAPI REST endpoints for game control and state access

**Why Fourth**: API layer orchestrates game engine and agents. Now that both work, expose them via HTTP.

#### 4.0. API Foundation

**Spec Reference**: Section 5 - API Design

**Files to Create:**
- `src/api/main.py` (FastAPI app)
- `src/api/routes.py` (endpoint definitions)
- `src/api/models.py` (request/response models)
- `src/api/errors.py` (error handling)
- `tests/integration/api/test_api.py`

**4.0.1. FastAPI Application Setup** ✅
- ✅ Create FastAPI app instance
- ✅ Configure CORS (Section 5) - allows all origins with credentials support
- ✅ Set up exception handlers (ValueError → 400, Exception → 500)
- ✅ Configure logging middleware (request/response logging with process time)
- ✅ Root endpoint (GET /) returns API information

**Subsection Tests** (10 tests for incremental development): ✅
- ✅ App instance created with correct metadata (title, description, version)
- ✅ Root endpoint returns API information
- ✅ CORS headers present in responses (access-control-allow-origin, access-control-allow-credentials)
- ✅ CORS preflight (OPTIONS) requests work
- ✅ Logging middleware adds X-Process-Time header
- ✅ ValueError exception handler returns 400 with error response format
- ✅ General Exception handler returns 500 with error response format
- ✅ Exception handlers registered in app
- ✅ OpenAPI/Swagger docs available at /docs
- ✅ OpenAPI JSON schema available at /openapi.json

**Test Coverage**: ✅
- **Subsection Tests**: ✅ 10 tests for Phase 4.0.1 foundation verification
- **Test File**: ✅ `tests/integration/api/test_api_foundation.py`
- **Note**: Foundation setup doesn't have official AC numbers (AC-5.X.Y starts at 5.1.1 for /health endpoint)

**4.0.2. Request/Response Models**
- Implement Pydantic models per Section 5.3:
  - `MoveRequest` (row, col) - validation for bounds (0-2)
  - `MoveResponse` (updated state, AI move) - includes success, position, updated_game_state, ai_move_execution, error_message
  - `GameStatusResponse` (complete game state) - includes GameState, agent_status, metrics
  - `ErrorResponse` (error code, message, details) - follows Section 5.4 error response schema

**Subsection Tests**:
- MoveRequest validation (row/col bounds 0-2)
- MoveRequest rejects invalid values (row/col < 0 or > 2)
- MoveResponse structure (success, position, updated_game_state when success=True)
- MoveResponse includes ai_move_execution when AI moved
- MoveResponse includes error_message when success=False
- GameStatusResponse structure (game_state, agent_status, metrics)
- ErrorResponse structure (status="failure", error_code, message, timestamp, details)
- ErrorResponse timestamp is ISO 8601 format
- All models serialize to JSON correctly
- All models deserialize from JSON correctly

**Test Coverage** (planned):
- **Subsection Tests**: ~10 tests for Phase 4.0.2 model validation and serialization
- **Test File**: `tests/integration/api/test_api_models.py` (or add to existing test file)
- **Note**: Model validation tests verify Section 5.3 constraints. Actual endpoint usage covered in AC-5.4.X, AC-5.5.X, etc.

#### 4.1. Health and Readiness Endpoints

**Spec Reference**: Section 5.2 - REST API Endpoints

**4.1.1. GET /health**
- Return basic health status
- Check if API is running
- No dependencies checked

**Subsection Tests**:
- GET /health returns 200 with status="healthy" when server is running
- GET /health response includes timestamp in ISO 8601 format
- GET /health response includes uptime_seconds as float with 2 decimal precision
- GET /health response completes within 100ms
- GET /health returns 503 with status="unhealthy" when shutting down (if shutdown state tracked)

**Test Coverage** (planned):
- **Subsection Tests**: ~4-5 tests for Phase 4.1.1 incremental development
- **Acceptance Criteria**: AC-5.1.1 through AC-5.1.4 (4 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_health.py`

**4.1.2. GET /ready**
- Check game engine is initialized
- Check agent system is ready
- Verify LLM providers are configured (optional in Phase 4)
- Return detailed readiness status

**Subsection Tests**:
- GET /ready returns 200 with status="ready" when all checks pass
- GET /ready response includes checks object with game_engine status
- GET /ready response includes checks object with configuration status
- GET /ready returns checks.llm_configuration="ok" when LLM keys configured (optional in Phase 4)
- GET /ready returns 503 with status="not_ready" when LLM keys missing (optional in Phase 4)
- GET /ready returns 503 with errors array when checks fail
- Game endpoints return 503 when /ready returns 503 (E_SERVICE_NOT_READY)

**Test Coverage** (planned):
- **Subsection Tests**: ~6-7 tests for Phase 4.1.2 incremental development
- **Acceptance Criteria**: AC-5.2.1 through AC-5.2.6 (6 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_ready.py`

#### 4.2. Game Control Endpoints

**4.2.1. POST /api/game/new**
- Create new game session
- Initialize game engine
- Return game ID and initial state
- Optionally accept player symbol preference

**Subsection Tests**:
- POST /api/game/new creates new game session and returns 200
- POST /api/game/new returns game_id in response
- POST /api/game/new returns initial GameState with MoveCount=0, empty board
- POST /api/game/new accepts optional player_symbol preference
- POST /api/game/new defaults to X for player if not specified

**Test Coverage** (planned):
- **Subsection Tests**: ~5 tests for Phase 4.2.1 incremental development
- **Acceptance Criteria**: AC-5.3.1 through AC-5.3.3 (3 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

**4.2.2. POST /api/game/move**
- Accept player move (row, col)
- Validate move via game engine
- Trigger AI agent pipeline
- Return updated game state + AI move
- Handle errors per Section 5.4

**Subsection Tests**:
- POST /api/game/move accepts valid MoveRequest and returns 200
- POST /api/game/move validates move bounds (rejects row/col < 0 or > 2) → 400 E_MOVE_OUT_OF_BOUNDS
- POST /api/game/move validates cell is empty (rejects occupied cell) → 400 E_CELL_OCCUPIED
- POST /api/game/move validates game is not over (rejects if game ended) → 400 E_GAME_ALREADY_OVER
- POST /api/game/move triggers AI agent pipeline after valid player move
- POST /api/game/move returns MoveResponse with updated_game_state and ai_move_execution
- POST /api/game/move handles game win condition (sets IsGameOver=true, winner)
- POST /api/game/move handles malformed JSON → 422 Unprocessable Entity
- POST /api/game/move handles server errors → 500 with error message

**Test Coverage** (planned):
- **Subsection Tests**: ~8-9 tests for Phase 4.2.2 incremental development
- **Acceptance Criteria**: AC-5.4.1 through AC-5.4.8 (8 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

**4.2.3. GET /api/game/status**
- Return current game state
- Include board, move history, game over status
- Return agent insights (if available)

**Subsection Tests**:
- GET /api/game/status returns 200 with GameStatusResponse when game active
- GET /api/game/status includes current GameState (board, move_count, current_player)
- GET /api/game/status returns 404 when no active game exists
- GET /api/game/status includes agent_status when AI is processing
- GET /api/game/status includes metrics dictionary when game is completed

**Test Coverage** (planned):
- **Subsection Tests**: ~5 tests for Phase 4.2.3 incremental development
- **Acceptance Criteria**: AC-5.5.1 through AC-5.5.4 (4 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

**4.2.4. POST /api/game/reset**
- Reset current game to initial state
- Clear move history
- Reinitialize agents

**Subsection Tests**:
- POST /api/game/reset returns 200 with new GameState
- POST /api/game/reset resets board to empty (all cells EMPTY)
- POST /api/game/reset sets MoveCount=0 and CurrentPlayer=X
- POST /api/game/reset clears move_history
- POST /api/game/reset returns new game_id

**Test Coverage** (planned):
- **Subsection Tests**: ~5 tests for Phase 4.2.4 incremental development
- **Acceptance Criteria**: AC-5.6.1 through AC-5.6.3 (3 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

**4.2.5. GET /api/game/history**
- Return complete move history
- Include both player and AI moves
- Include timestamps and agent reasoning

**Subsection Tests**:
- GET /api/game/history returns 200 with array of MoveHistory objects
- GET /api/game/history returns moves in chronological order (oldest first)
- GET /api/game/history returns empty array when no moves made
- GET /api/game/history includes player, position, timestamp, move_number for each move
- GET /api/game/history includes AI moves with agent reasoning (if available)

**Test Coverage** (planned):
- **Subsection Tests**: ~5 tests for Phase 4.2.5 incremental development
- **Acceptance Criteria**: AC-5.7.1 through AC-5.7.3 (3 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

#### 4.3. Agent Status Endpoints

**Spec Reference**: Section 5.2 - Agent Status Endpoints

**4.3.1. GET /api/agents/status**
- Return status of each agent (idle/running/success/failed)
- Include current processing agent
- Show elapsed time for current operation

**Subsection Tests**:
- GET /api/agents/scout/status returns 200 with status="idle" when agent idle
- GET /api/agents/scout/status returns status="processing" with elapsed_time_ms when running
- GET /api/agents/strategist/status returns execution_time_ms and success=true when completed
- GET /api/agents/executor/status returns error_message and success=false when failed/timed out
- GET /api/agents/{invalid}/status returns 404 for invalid agent name

**Test Coverage** (planned):
- **Subsection Tests**: ~5 tests for Phase 4.3.1 incremental development
- **Acceptance Criteria**: AC-5.8.1 through AC-5.8.5 (5 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_agents.py`

#### 4.4. Error Handling

**Spec Reference**: Section 5.4 - Error Response Schema, Section 5.5 - HTTP Status Code Mapping

**Implementation:**
- Implement error response format per Section 5.4
- Map error codes to HTTP status codes per Section 5.6:
  - E_POSITION_OUT_OF_BOUNDS → 400 Bad Request
  - E_CELL_OCCUPIED → 409 Conflict
  - E_GAME_ALREADY_OVER → 409 Conflict
  - Agent timeout → 504 Gateway Timeout
- Return consistent error structure with error code, message, details

**Subsection Tests**:
- Error responses follow ErrorResponse schema (status="failure", error_code, message, timestamp, details)
- E_MOVE_OUT_OF_BOUNDS maps to 400 Bad Request
- E_CELL_OCCUPIED maps to 409 Conflict
- E_GAME_ALREADY_OVER maps to 409 Conflict
- E_SERVICE_NOT_READY maps to 503 Service Unavailable
- Agent timeout errors map to 504 Gateway Timeout
- Error response timestamp is ISO 8601 format
- Error response details include field/expected/actual when applicable

**Test Coverage** (planned):
- **Subsection Tests**: ~7-8 tests for Phase 4.4 incremental development
- **Test File**: `tests/integration/api/test_api_errors.py` (or integrated into endpoint tests)
- **Note**: Error handling is tested as part of endpoint tests, but dedicated tests verify error code → HTTP status mapping

**Phase 4 Deliverables:**
- ✅ Complete REST API with all endpoints
- ✅ 36 API integration tests passing
- ✅ Error handling with proper HTTP status codes
- ✅ API can be tested with curl/Postman
- ✅ Game playable via API calls

**Spec References:**
- Section 5: API Design (complete)
- Section 5.2: REST API Endpoints
- Section 5.4: Error Response Schema
- Section 5.6: HTTP Status Code Mapping

---

### Phase 5: LLM Integration

**Duration**: 3-4 days

**Goal**: Integrate LLM providers for enhanced agent intelligence

**Why Fifth**: LLM integration is optional enhancement. Agents already work with rule-based logic. Now make them smarter.

#### 5.0. LLM Provider Abstraction

**Spec Reference**: Section 16 - LLM Integration

**Files to Create:**
- `src/llm/provider.py` (abstract provider interface)
- `src/llm/openai_provider.py`
- `src/llm/anthropic_provider.py`
- `src/llm/gemini_provider.py`
- `tests/unit/llm/test_providers.py`

**Implementation:**

**5.0.1. Provider Interface**
- Define abstract `LLMProvider` interface
- Methods: `generate(prompt, model, max_tokens, temperature)`
- Return structured response with text, tokens, latency

**Subsection Tests**:
- Abstract LLMProvider interface defines generate() method signature
- LLMProvider.generate() accepts prompt, model, max_tokens, temperature parameters
- LLMProvider.generate() returns structured response with text, tokens_used, latency_ms fields
- Cannot instantiate abstract LLMProvider directly (TypeError)

**5.0.2. OpenAI Provider**
- Implement using `openai` SDK
- Support models: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- Handle API errors and retries

**Subsection Tests**:
- OpenAIProvider implements LLMProvider interface
- OpenAIProvider.generate() calls OpenAI API with correct parameters
- OpenAIProvider supports gpt-4o, gpt-4o-mini, gpt-3.5-turbo models
- OpenAIProvider handles API timeout errors (retries 3 times with exponential backoff)
- OpenAIProvider handles rate limit errors (429) with Retry-After header
- OpenAIProvider handles authentication errors (401/403) without retry
- OpenAIProvider returns structured response with text, tokens_used, latency_ms

**5.0.3. Anthropic Provider**
- Implement using `anthropic` SDK
- Support models: claude-3-5-sonnet, claude-3-opus, claude-3-haiku

**Subsection Tests**:
- AnthropicProvider implements LLMProvider interface
- AnthropicProvider.generate() calls Anthropic API with correct parameters
- AnthropicProvider supports claude-3-5-sonnet, claude-3-opus, claude-3-haiku models
- AnthropicProvider handles API timeout errors (retries 3 times with exponential backoff)
- AnthropicProvider handles rate limit errors (429) with Retry-After header
- AnthropicProvider handles authentication errors (401/403) without retry
- AnthropicProvider returns structured response with text, tokens_used, latency_ms

**5.0.4. Google Gemini Provider**
- Implement using Google SDK
- Support models: gemini-1.5-pro, gemini-1.5-flash

**Subsection Tests**:
- GeminiProvider implements LLMProvider interface
- GeminiProvider.generate() calls Google Gemini API with correct parameters
- GeminiProvider supports gemini-1.5-pro, gemini-1.5-flash models
- GeminiProvider handles API timeout errors (retries 3 times with exponential backoff)
- GeminiProvider handles rate limit errors (429) with Retry-After header
- GeminiProvider handles authentication errors (401/403) without retry
- GeminiProvider returns structured response with text, tokens_used, latency_ms

**5.0.5. Pydantic AI Implementation**

**Framework Selected**: **Pydantic AI** (see Technology Stack section for selection rationale based on Section 19)

**Implementation Approach**:
- Use Pydantic AI's `Agent` class for type-safe agent definitions
- Define agents (Scout, Strategist) using Pydantic AI with Pydantic response models
- Use Pydantic AI's multi-provider support (OpenAI, Anthropic, Google Gemini)
- Leverage Pydantic AI's structured output validation for domain models (BoardAnalysis, Strategy)
- Use Pydantic AI's error handling and retry mechanisms

**Key Pydantic AI Features Used**:
- Type-safe agent definitions with Pydantic response models
- Automatic validation of LLM outputs against domain models
- Multi-provider support via provider configuration
- Built-in error handling and retry logic
- Agent workflow abstractions for Scout → Strategist coordination

**Note**: See Section 19 for comprehensive framework comparison. While Pydantic AI is selected for this implementation, the abstraction layer allows switching frameworks if needed (per Section 19 implementation strategy).

**Subsection Tests**:
- Pydantic AI Agent created with BoardAnalysis as response model (for Scout)
- Pydantic AI Agent created with Strategy as response model (for Strategist)
- Pydantic AI validates LLM output against BoardAnalysis domain model (rejects invalid structure)
- Pydantic AI validates LLM output against Strategy domain model (rejects invalid structure)
- Pydantic AI multi-provider support (OpenAI, Anthropic, Google Gemini via configuration)
- Pydantic AI error handling catches parse errors and triggers retry logic
- Pydantic AI tracks token usage and latency automatically
- Pydantic AI retry mechanism respects exponential backoff (1s, 2s, 4s)

**Test Coverage** (planned):
- **Subsection Tests**: ~20-25 tests for Phase 5.0 incremental development (4 + 7 + 7 + 7 + 8)
- **Acceptance Criteria**: LLM Provider Abstraction (Section 16) - provider contract, error handling, retry logic
- **Test Files**: `tests/unit/llm/test_providers.py`

#### 5.1. Agent LLM Integration with Pydantic AI

**Spec Reference**: Section 16.3 - LLM Usage Patterns, Section 19 (Pydantic AI framework)

**5.1.1. Scout LLM Enhancement (Pydantic AI)**
- Create Pydantic AI Agent with `BoardAnalysis` as response model
- Define prompt: "Analyze this Tic-Tac-Toe board..."
- Use Pydantic AI's structured output to automatically validate response against `BoardAnalysis` domain model
- Leverage Pydantic AI's built-in error handling and retry logic
- Fallback to rule-based if LLM fails/times out
- Update `src/agents/scout.py`

**Subsection Tests**:
- ScoutAgent.analyze() calls Pydantic AI Agent when LLM enabled
- ScoutAgent.analyze() prompts LLM with board state and game context
- ScoutAgent.analyze() receives BoardAnalysis from Pydantic AI structured output
- ScoutAgent.analyze() falls back to rule-based analysis on LLM timeout (>5s)
- ScoutAgent.analyze() falls back to rule-based analysis on LLM parse error
- ScoutAgent.analyze() falls back to rule-based analysis on LLM authentication error
- ScoutAgent.analyze() retries LLM call on timeout (3 retries with exponential backoff)
- ScoutAgent.analyze() logs LLM call metadata (prompt, response, tokens, latency, model)

**5.1.2. Strategist LLM Enhancement (Pydantic AI)**
- Create Pydantic AI Agent with `Strategy` as response model
- Define prompt: "Given this analysis, recommend best move..."
- Use Pydantic AI's structured output to automatically validate response against `Strategy` domain model
- Leverage Pydantic AI's built-in error handling and retry logic
- Fallback to priority-based selection if LLM fails
- Update `src/agents/strategist.py`

**Subsection Tests**:
- StrategistAgent.plan() calls Pydantic AI Agent when LLM enabled
- StrategistAgent.plan() prompts LLM with BoardAnalysis and game context
- StrategistAgent.plan() receives Strategy from Pydantic AI structured output
- StrategistAgent.plan() falls back to priority-based selection on LLM timeout (>5s)
- StrategistAgent.plan() falls back to priority-based selection on LLM parse error
- StrategistAgent.plan() falls back to priority-based selection on LLM authentication error
- StrategistAgent.plan() retries LLM call on timeout (3 retries with exponential backoff)
- StrategistAgent.plan() logs LLM call metadata (prompt, response, tokens, latency, model)

**5.1.3. Executor (No LLM)**
- Executor remains rule-based (no LLM needed for validation/execution)
- Keeps execution fast and deterministic

**Subsection Tests**:
- ExecutorAgent.execute() remains rule-based (no LLM calls)
- ExecutorAgent.execute() validates moves without LLM
- ExecutorAgent.execute() executes moves deterministically
- ExecutorAgent.execute() performance unaffected by LLM integration (no latency impact)

**Test Coverage** (planned):
- **Subsection Tests**: ~18 tests for Phase 5.1 incremental development (8 + 8 + 4)
- **Acceptance Criteria**: Agent LLM Integration (Section 16.3) - prompt engineering, response parsing, fallback strategies
- **Test Files**: `tests/unit/agents/test_scout_llm.py`, `tests/unit/agents/test_strategist_llm.py`, `tests/integration/test_llm_fallback.py`

#### 5.2. Configuration and Settings

**Spec Reference**: Section 9 - Configuration Management

**Files to Create:**
- `src/config/llm_config.py`
- `tests/unit/config/test_llm_config.py`

**Implementation:**
- Load LLM provider from environment variables
- Support `.env` file for local development
- Allow runtime provider switching
- Configuration hierarchy: env vars > .env file > defaults

**5.2.1. Environment Variables**
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

**Subsection Tests**:
- LLMConfig loads provider from LLM_PROVIDER environment variable
- LLMConfig loads model from LLM_MODEL environment variable
- LLMConfig loads API keys from provider-specific environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
- LLMConfig supports .env file for local development (reads .env if present)
- LLMConfig configuration hierarchy: env vars > .env file > defaults
- LLMConfig validates API key format (basic validation, not actual API check)
- LLMConfig validates provider value (must be openai, anthropic, or gemini)
- LLMConfig validates model value per provider (gpt-4o for openai, claude-3-5-sonnet for anthropic, etc.)
- LLMConfig runtime provider switching (updates provider/model without restart)
- LLMConfig returns error when required API key missing for selected provider

**Test Coverage** (planned):
- **Subsection Tests**: ~10 tests for Phase 5.2.1 incremental development
- **Acceptance Criteria**: LLM Configuration (Section 9, Section 16) - environment variables, .env support, hierarchy, validation
- **Test Files**: `tests/unit/config/test_llm_config.py`

#### 5.3. Metrics and Tracking

**Spec Reference**: Section 12.1 - LLM Provider Metadata and Experimentation Tracking

**Files to Create:**
- `src/metrics/llm_metrics.py`
- `tests/unit/metrics/test_llm_metrics.py`

**Implementation:**
- Track LLM calls per agent
- Record: prompt, response, tokens, latency, model, provider
- Store in game session metadata
- Enable post-game analysis (Section 6 - US-015)

**Subsection Tests**:
- LLMMetrics.track_call() records LLM call with agent_name, prompt, response, tokens_used, latency_ms, model, provider
- LLMMetrics.get_agent_calls(agent_name) returns all calls for specific agent (Scout, Strategist)
- LLMMetrics.get_game_session_metadata() returns aggregated metrics for current game session
- LLMMetrics stores metadata in game session (persists across game state)
- LLMMetrics export format includes all required fields (timestamp, agent, prompt, response, tokens, latency, model, provider)
- LLMMetrics tracks total tokens used per game session
- LLMMetrics tracks total LLM latency per game session
- LLMMetrics tracks LLM calls count per agent
- LLMMetrics enables post-game analysis (data available after game ends)

**Test Coverage** (planned):
- **Subsection Tests**: ~9 tests for Phase 5.3 incremental development
- **Acceptance Criteria**: LLM Metrics and Tracking (Section 12.1) - call tracking, metadata recording, session storage, export format
- **Test Files**: `tests/unit/metrics/test_llm_metrics.py`, `tests/integration/test_llm_tracking.py`

**Phase 5 Deliverables:**
- ✅ LLM providers integrated (OpenAI, Anthropic, Google)
- ✅ Scout and Strategist enhanced with LLM intelligence
- ✅ Fallback to rule-based logic still works
- ✅ Configuration supports provider switching
- ✅ Metrics tracked for all LLM calls
- ✅ Comprehensive test coverage for LLM integration (provider abstraction, agent integration, configuration, metrics)

**Spec References:**
- Section 16: LLM Integration (provider and model configuration)
- Section 19: LLM Framework Selection (comprehensive framework comparison and recommendations)
- Section 16.3: LLM Usage Patterns
- Section 12.1: LLM Provider Metadata

---

### Phase 6: Web UI (User Interface Layer)

**Duration**: 4-6 days

**Goal**: Build interactive web UI for playing the game

**Why Sixth**: UI is the final layer. All backend systems are working, now add user-facing interface.

#### 6.0. UI Foundation

**Spec Reference**: Section 6 - Web UI Functional Requirements, docs/spec/ui-spec.md

**Files to Create:**
- `src/ui/index.html`
- `src/ui/styles.css`
- `src/ui/app.js`
- `src/ui/api-client.js`

**Tech Stack:**
- Vanilla JavaScript (or React/Vue if preferred)
- CSS with design tokens from ui-spec.md
- Fetch API for REST calls

**6.0.1. Design System Setup**
- Implement color palette (ui-spec.md Section: Color Palette)
- Set up typography (SF Pro Display font)
- Define spacing scale (8px base unit)
- Create CSS variables for design tokens

**Subsection Tests**:
- CSS variables defined for color palette (primary, secondary, background, text colors)
- CSS variables defined for spacing scale (8px base unit: 8px, 16px, 24px, 32px)
- Typography uses SF Pro Display font family
- All design tokens accessible via CSS variables

**6.0.2. API Client**
- Create JavaScript wrapper for REST API
- Methods: `makeMove()`, `getGameStatus()`, `resetGame()`
- Handle errors and display to user

**Subsection Tests**:
- API client makeMove() method calls POST /api/game/move with correct parameters
- API client getGameStatus() method calls GET /api/game/status
- API client resetGame() method calls POST /api/game/reset
- API client handles 400 errors (invalid move) and displays error message
- API client handles 500 errors (server error) and displays error message
- API client handles network errors and displays user-friendly message

#### 6.1. Game Board UI

**Spec Reference**: US-001, US-002, US-003, US-004, US-005 (Section 6)

**6.1.1. Display Game Board (US-001)**
- Render 3x3 grid with cells
- Cell dimensions: 100px × 100px
- Gap: 12px between cells
- Display X, O, or empty

**Subsection Tests**:
- Game board renders 3x3 grid (9 cells total)
- Each cell has dimensions 100px × 100px
- Gap between cells is 12px
- Cells display X, O, or empty state correctly
- Board layout matches ui-spec.md design

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 6.1.1 incremental development
- **Acceptance Criteria**: AC-US001.1 through AC-US001.3 (3 official tests for final verification)

**6.1.2. Make Player Move (US-002)**
- Click handler on empty cells
- Disable board during AI turn
- Show hover effects on valid cells
- Display error messages for invalid moves

**Subsection Tests**:
- Click handler attached to empty cells only
- Clicking empty cell triggers makeMove() API call
- Board disabled (pointer-events: none) during AI turn
- Hover effect visible on valid (empty) cells
- Hover effect hidden on occupied cells
- Invalid move displays error message with shake animation
- Cell occupied error highlights occupied cell in red
- Out of bounds error displays appropriate message
- Error messages auto-dismiss after 5 seconds

**Test Coverage**:
- **Subsection Tests**: ~9 E2E/UI tests for Phase 6.1.2 incremental development
- **Acceptance Criteria**: AC-US002.1 through AC-US002.12 (12 official tests for final verification)

**6.1.3. View Last Move (US-003)**
- Highlight last played cell
- Border color: highlight pink (#f72585)
- Glow effect per ui-spec.md

**Subsection Tests**:
- Last played cell highlighted with border color #f72585
- Glow effect applied to last played cell per ui-spec.md
- Highlight moves to new cell when next move is made
- Highlight persists until game ends or reset

**Test Coverage**:
- **Subsection Tests**: ~4 E2E/UI tests for Phase 6.1.3 incremental development
- **Acceptance Criteria**: AC-US003.1 through AC-US003.2 (2 official tests for final verification)

**6.1.4. View Current Turn (US-004)**
- Display whose turn (Player or AI)
- Color-code by player symbol
- Show move count

**Subsection Tests**:
- Turn indicator displays "Player" or "AI" correctly
- Turn indicator color-coded by current player symbol (X/O)
- Move count displayed and updates after each move
- Turn indicator updates when turn changes
- Turn indicator reflects correct player at game start

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 6.1.4 incremental development
- **Acceptance Criteria**: AC-US004.1 through AC-US004.8 (8 official tests for final verification)

**6.1.5. View Game Status (US-005)**
- Display game over message
- Show winner (X, O, or DRAW)
- Fade board when game ends

**Subsection Tests**:
- Game over message displayed when game ends
- Winner displayed correctly (X wins, O wins, or DRAW)
- Board fades (opacity reduced) when game ends
- Game over message persists until reset
- Board interactions disabled when game over

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 6.1.5 incremental development
- **Acceptance Criteria**: AC-US005.1 through AC-US005.3 (3 official tests for final verification)

#### 6.2. Move History Panel

**Spec Reference**: US-006, US-007

**6.2.1. View Move History (US-006)**
- Chronological list of all moves
- Show player/AI indicator, move number, position, timestamp
- Scrollable panel (max-height: 400px)

**Subsection Tests**:
- Move history displays all moves in chronological order
- Each move entry shows player/AI indicator
- Each move entry shows move number, position (row, col), timestamp
- Move history panel scrollable when content exceeds max-height 400px
- Move history updates after each move
- Move history cleared on game reset

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.2.1 incremental development
- **Acceptance Criteria**: AC-US006.1 through AC-US006.2 (2 official tests for final verification)

**6.2.2. View Move Details (US-007)**
- Expandable move entries
- Show agent reasoning (Scout analysis, Strategist strategy, Executor details)
- Collapse/expand animation

**Subsection Tests**:
- Move entries expandable via click/tap
- Expanded entry shows Scout analysis (threats, opportunities)
- Expanded entry shows Strategist strategy (primary move, alternatives, reasoning)
- Expanded entry shows Executor details (execution time, validation status)
- Collapse/expand animation smooth and visible
- Multiple entries can be expanded simultaneously

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.2.2 incremental development
- **Acceptance Criteria**: AC-US007.1 through AC-US007.2 (2 official tests for final verification)

#### 6.3. Agent Insights Panel

**Spec Reference**: US-008, US-009, US-010, US-011, US-012

**6.3.1. View Agent Analysis (US-008)**
- Real-time agent status display
- Show threats, opportunities, recommended moves
- Three sections: Scout, Strategist, Executor

**Subsection Tests**:
- Agent insights panel displays Scout, Strategist, Executor sections
- Scout section shows threats detected (immediate wins/blocks)
- Scout section shows opportunities identified (strategic positions)
- Strategist section shows recommended moves with priority
- Executor section shows move execution status and timing
- Agent analysis updates in real-time during AI turn
- Agent analysis cleared on game reset

**Test Coverage**:
- **Subsection Tests**: ~7 E2E/UI tests for Phase 6.3.1 incremental development
- **Acceptance Criteria**: AC-US008.1 through AC-US008.11 (11 official tests for final verification)

**6.3.2. Processing Status (US-009, US-010)**
- Loading indicators while agents think
- Progressive status updates:
  - 0-2s: Simple spinner
  - 2-5s: Processing message
  - 5-10s: Progress bar with elapsed time
  - 10-15s: Warning with fallback notice
  - 15s+: Automatic fallback

**Subsection Tests**:
- Simple spinner displayed during 0-2s of agent processing
- Processing message displayed during 2-5s
- Progress bar with elapsed time displayed during 5-10s
- Warning with fallback notice displayed during 10-15s
- Automatic fallback triggered after 15s
- Processing status updates every 100ms
- Processing status cleared when agent completes

**Test Coverage**:
- **Subsection Tests**: ~7 E2E/UI tests for Phase 6.3.2 incremental development
- **Acceptance Criteria**: AC-US009.1 through AC-US010.1e (9 official tests for final verification)

**6.3.3. Force Fallback and Retry (US-011, US-012)**
- "Force Fallback" button after 10s
- "Retry" button on agent failure
- Clear explanations of fallback strategy

**Subsection Tests**:
- "Force Fallback" button appears after 10s of processing
- Clicking "Force Fallback" triggers immediate fallback move
- "Retry" button appears when agent fails
- Clicking "Retry" attempts agent processing again
- Fallback strategy explanation displayed when fallback used
- Buttons disabled during fallback/retry execution

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.3.3 incremental development
- **Acceptance Criteria**: AC-US011.1 through AC-US012.2 (5 official tests for final verification)

#### 6.4. Post-Game Metrics

**Spec Reference**: US-013, US-014, US-015, US-016, US-017, US-018

**6.4.1. Metrics Tab (US-013)**
- Only visible after game ends
- Tabbed interface: Summary | Performance | LLM | Communication

**Subsection Tests**:
- Metrics tab only visible after game ends (hidden during active game)
- Tabbed interface displays: Summary, Performance, LLM, Communication tabs
- Each tab displays correct content when selected
- Tab switching works correctly
- Metrics tab hidden on game reset until next game ends

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 6.4.1 incremental development
- **Acceptance Criteria**: AC-US013.1 through AC-US013.2 (2 official tests for final verification)

**6.4.2. Agent Communication (US-014)**
- Show request/response data for each agent call
- Display JSON with syntax highlighting

**Subsection Tests**:
- Agent Communication tab shows request/response for each agent call
- JSON data displayed with syntax highlighting
- Request shows input parameters (game state, board analysis, etc.)
- Response shows agent output (BoardAnalysis, Strategy, MoveExecution)
- Each agent (Scout, Strategist, Executor) has separate communication logs
- Communication logs in chronological order

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.4.2 incremental development
- **Acceptance Criteria**: AC-US014.1 through AC-US014.3 (3 official tests for final verification)

**6.4.3. LLM Interactions (US-015)**
- Show prompts sent to LLM
- Show LLM responses
- Display token usage, latency, model/provider

**Subsection Tests**:
- LLM Interactions tab shows prompts sent to LLM (Scout, Strategist)
- LLM Interactions tab shows LLM responses with structured output
- Token usage displayed for each LLM call (input tokens, output tokens, total)
- Latency displayed for each LLM call (in milliseconds)
- Model and provider name displayed for each LLM call
- LLM interactions only shown if LLM was used (rule-based mode shows empty)

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.4.3 incremental development
- **Acceptance Criteria**: AC-US015.1 through AC-US015.6 (6 official tests for final verification)

**6.4.4. Agent Configuration (US-016)**
- Display agent mode (local vs MCP)
- Show LLM framework used
- Show initialization details

**Subsection Tests**:
- Agent Configuration tab displays agent mode (local vs MCP/distributed)
- Agent Configuration tab shows LLM framework used (Pydantic AI, etc.)
- Agent Configuration tab shows initialization details (provider, model, timeouts)
- Configuration reflects current game session settings
- Configuration updates when settings changed during game

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 6.4.4 incremental development
- **Acceptance Criteria**: AC-US016.1 through AC-US016.4 (4 official tests for final verification)

**6.4.5. Performance Summary (US-017)**
- Per-agent execution times (min, max, avg)
- Total LLM calls and tokens
- Success/failure rates

**Subsection Tests**:
- Performance Summary tab shows per-agent execution times (Scout, Strategist, Executor)
- Execution times include min, max, average for each agent
- Total LLM calls count displayed
- Total token usage displayed (input + output tokens)
- Success/failure rates displayed for each agent
- Performance data calculated correctly from game session

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.4.5 incremental development
- **Acceptance Criteria**: AC-US017.1 through AC-US017.5 (5 official tests for final verification)

**6.4.6. Game Summary (US-018)**
- Total moves, duration, outcome
- Average move time

**Subsection Tests**:
- Game Summary tab shows total moves count
- Game duration displayed (start time to end time)
- Game outcome displayed (X wins, O wins, DRAW)
- Average move time calculated and displayed correctly
- Summary data matches actual game play

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 6.4.6 incremental development
- **Acceptance Criteria**: AC-US018.1 through AC-US018.4 (4 official tests for final verification)

#### 6.5. Configuration Panel

**Spec Reference**: US-019, US-020, US-021

**6.5.1. LLM Provider Selection (US-019)**
- Dropdown for provider (OpenAI, Anthropic, Google)
- Model name input
- Save preferences to localStorage

**Subsection Tests**:
- Provider dropdown includes OpenAI, Anthropic, Google options
- Model name input accepts valid model names per provider
- Preferences saved to localStorage on change
- Preferences loaded from localStorage on page load
- Provider/model selection persists across sessions
- Invalid model names rejected with error message

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.5.1 incremental development
- **Acceptance Criteria**: AC-US019.1 through AC-US019.3 (3 official tests for final verification)

**6.5.2. Agent Mode Selection (US-020)**
- Toggle: Local vs Distributed MCP
- LLM framework dropdown

**Subsection Tests**:
- Toggle switches between Local and Distributed MCP modes
- LLM framework dropdown displays available frameworks (Pydantic AI, etc.)
- Mode selection saved to localStorage
- Mode selection persists across sessions
- Mode change requires game reset to take effect (with confirmation)

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 6.5.2 incremental development
- **Acceptance Criteria**: AC-US020.1 through AC-US020.2 (2 official tests for final verification)

**6.5.3. Game Settings (US-021)**
- Reset game button
- Player symbol selection (X or O)
- Difficulty slider (optional)

**Subsection Tests**:
- Reset game button clears current game and starts new game
- Player symbol selection allows choosing X or O
- Player symbol selection applies to next game
- Difficulty slider (if implemented) adjusts agent behavior
- Settings saved to localStorage
- Settings persist across sessions

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.5.3 incremental development
- **Acceptance Criteria**: AC-US021.1 through AC-US021.3 (3 official tests for final verification)

#### 6.6. Error Handling UI

**Spec Reference**: US-024, US-025, Section 12 - Failure Matrix

**6.6.1. Display Error Messages (US-024)**
- Critical errors: Red modal
- Warnings: Orange/yellow badges
- Info: Blue toasts (bottom-right)
- Cell-level errors: Shake animation + red highlight

**Subsection Tests**:
- Critical errors display in red modal dialog (requires user acknowledgment)
- Warnings display as orange/yellow badges in UI
- Info messages display as blue toast notifications (bottom-right)
- Cell-level errors trigger shake animation + red highlight on affected cell
- Error messages match error codes from Failure Matrix (Section 12)
- Error messages auto-dismiss after appropriate timeout (modals require click)

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 6.6.1 incremental development
- **Acceptance Criteria**: AC-US024.1 through AC-US024.4 (4 official tests for final verification)

**6.6.2. Fallback Indication (US-025)**
- Notify user when fallback is triggered
- Explain why fallback was needed
- Show which fallback strategy was used

**Subsection Tests**:
- User notified when fallback is triggered (orange badge or toast)
- Fallback notification explains why fallback was needed (timeout, parse error, auth error, etc.)
- Fallback notification shows which strategy was used (rule-based analysis, priority-based selection, random valid move)
- Fallback indication persists until next move or game reset
- Fallback indication appears in agent insights panel

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 6.6.2 incremental development
- **Acceptance Criteria**: AC-US025.1 through AC-US025.3 (3 official tests for final verification)

**Phase 6 Deliverables:**
- ✅ Complete web UI with all 25 user stories implemented
- ✅ Responsive design (desktop-first per spec)
- ✅ All UI acceptance criteria met (104 total)
- ✅ Visual design matches ui-spec.md
- ✅ Full game playable in browser

**Spec References:**
- Section 6: Web UI Functional Requirements (all 25 user stories)
- docs/spec/ui-spec.md: Visual Design Specification

---

### Phase 7: Testing and Quality Assurance

**Duration**: 3-4 days

**Goal**: Comprehensive testing across all layers

**Spec Reference**: Section 11 - Testing Strategy

#### 7.0. Unit Test Coverage

**Target**: 100% coverage for domain models and game engine, 80%+ overall

**Tasks:**
- Review all unit tests from Phases 1-6
- Fill coverage gaps
- Ensure all acceptance criteria have corresponding tests
- Generate coverage report: `pytest --cov=src --cov-report=html`

**Deliverable**: Coverage report showing ≥80% overall, 100% for critical paths

**Subsection Tests**:
- Coverage report generated with pytest --cov=src --cov-report=html
- Domain models have 100% test coverage (Position, Board, GameState, AgentResult, etc.)
- Game engine has 100% test coverage (GameEngine, win conditions, draw conditions, move validation)
- Overall code coverage ≥80%
- All acceptance criteria have corresponding unit tests
- Coverage gaps identified and filled
- Coverage report accessible in htmlcov/index.html

#### 7.1. Integration Tests

**Files to Create:**
- `tests/integration/test_full_pipeline.py`
- `tests/integration/test_api_integration.py`

**Test Scenarios:**
- Complete game flow: Player move → AI move → repeat until win/draw
- Agent pipeline with all three agents
- API endpoints with real game engine and agents
- Error handling across layers

**Subsection Tests**:
- test_full_pipeline.py tests complete game flow (player move → AI move → repeat until win/draw)
- test_full_pipeline.py tests agent pipeline with all three agents (Scout → Strategist → Executor)
- test_api_integration.py tests API endpoints with real game engine and agents
- test_api_integration.py tests error handling across layers (validation → agent → execution)
- Integration tests verify state transitions across components
- Integration tests verify data flow between API, game engine, and agents

#### 7.2. End-to-End Tests

**Files to Create:**
- `tests/e2e/test_game_scenarios.py`

**Test Scenarios:**
- Player wins scenario
- AI wins scenario
- Draw scenario
- Player makes invalid move
- Agent timeout triggers fallback
- LLM provider failure

**Subsection Tests**:
- E2E test: Player wins scenario (player makes winning moves, AI responds, game ends with player win)
- E2E test: AI wins scenario (AI makes winning moves, player responds, game ends with AI win)
- E2E test: Draw scenario (9 moves made, no winner, game ends in draw)
- E2E test: Player makes invalid move (out of bounds, occupied cell, game over) → error displayed
- E2E test: Agent timeout triggers fallback (simulate slow agent, verify fallback move executed)
- E2E test: LLM provider failure (simulate LLM error, verify fallback to rule-based logic)

#### 7.3. Performance Tests

**Spec Reference**: Section 15 - Performance Optimization

**Files to Create:**
- `tests/performance/test_agent_timeout.py`

**Requirements:**
- Agent pipeline completes within 15s (Section 3.6)
- UI updates within 100ms of state change (AC-US023.3)
- Agent status updates within 500ms (AC-US023.4)

**Subsection Tests**:
- Performance test: Agent pipeline completes within 15s (measure end-to-end pipeline execution time)
- Performance test: UI updates within 100ms of state change (measure DOM update latency)
- Performance test: Agent status updates within 500ms (measure status update propagation)
- Performance test: Move validation completes within 10ms (measure validation latency)
- Performance test: API response time < 200ms for game status endpoint (measure API latency)

#### 7.4. Resilience Tests

**Spec Reference**: Section 12 - Error Handling and Resilience

**Test Scenarios:**
- Network timeout
- LLM API failure
- Invalid API responses
- Concurrent API requests
- Agent crash and recovery

**Subsection Tests**:
- Resilience test: Network timeout (simulate network delay, verify timeout handling and fallback)
- Resilience test: LLM API failure (simulate 500 error, verify fallback to rule-based logic)
- Resilience test: Invalid API responses (simulate malformed JSON, verify error handling)
- Resilience test: Concurrent API requests (multiple simultaneous game requests, verify no state leakage)
- Resilience test: Agent crash and recovery (simulate agent failure, verify system continues with fallback)
- Resilience test: Rate limiting (simulate 429 error, verify retry with backoff)
- Resilience test: Invalid API key (simulate 401/403, verify fallback and error messaging)

**Phase 7 Deliverables:**
- ✅ 399 tests passing (one per acceptance criterion)
- ✅ ≥80% code coverage overall
- ✅ 100% coverage on domain models and game engine
- ✅ All performance requirements met
- ✅ Resilience scenarios validated

**Spec References:**
- Section 11: Testing Strategy
- Section 15: Performance Optimization
- Section 12: Error Handling and Resilience

---

### Phase 8: Configuration and Observability

**Duration**: 2-3 days

**Goal**: Production-ready configuration, logging, and metrics

#### 8.0. Configuration Management

**Spec Reference**: Section 9 - Configuration Management

**Files to Create:**
- `src/config/settings.py`
- `.env.example`
- `config.yaml` (optional)

**Implementation:**
- Environment-based configuration (dev, staging, prod)
- Configuration validation on startup
- Support for environment variables and config files
- Hot-reload for non-critical settings

**Configuration Sections:**
- LLM provider settings
- Agent timeout values
- API server settings (host, port, CORS)
- Logging levels
- Feature flags (e.g., enable LLM, enable metrics)

**Subsection Tests**:
- Configuration loads from environment variables (LLM_PROVIDER, LLM_MODEL, etc.)
- Configuration loads from config file (YAML/JSON) if provided
- Configuration hierarchy respected (env vars > config file > defaults)
- Configuration validation on startup (invalid values rejected with clear errors)
- Environment-based configuration (dev, staging, prod) loads correct settings
- Hot-reload works for non-critical settings (logging level, feature flags)
- Configuration error handling (missing required values, invalid types)
- LLM provider settings validated (provider name, model name per provider)

**Test Coverage**:
- **Subsection Tests**: ~8 tests for Phase 8.0 incremental development
- **Acceptance Criteria**: Configuration Management (Section 9) - environment support, validation, hierarchy, error handling
- **Test Files**: `tests/unit/config/test_settings.py`, `tests/integration/test_config_loading.py`

#### 8.1. Logging

**Spec Reference**: Section 17 - Metrics and Observability - Log Format Specification

**Implementation:**
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Contextual logging (request ID, game ID, agent ID)
- Log rotation and retention

**Log Events:**
- API requests/responses
- Agent execution (start, end, duration)
- LLM calls (prompt, response, tokens)
- Errors and exceptions
- State transitions

**Subsection Tests**:
- Structured logging outputs JSON format (valid JSON per log entry)
- Log levels work correctly (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Contextual logging includes request ID, game ID, agent ID when available
- Log rotation works (log files rotated when size/age limits reached)
- Log retention policy enforced (old logs deleted after retention period)
- API request/response events logged with correct format
- Agent execution events logged (start, end, duration)
- LLM call events logged (prompt, response, tokens, latency)
- Error and exception events logged with stack traces
- State transition events logged (game state changes)

**Test Coverage**:
- **Subsection Tests**: ~10 tests for Phase 8.1 incremental development
- **Acceptance Criteria**: Logging (Section 17 - Log Format Specification) - JSON format, log levels, contextual logging, rotation, retention
- **Test Files**: `tests/unit/test_logging.py`, `tests/integration/test_logging_integration.py`

#### 8.2. Metrics

**Spec Reference**: Section 17 - Metrics Format Specification

**Files to Create:**
- `src/metrics/collector.py`
- `src/metrics/exporter.py`

**Metrics to Track:**
- **Agent Metrics** (per Section 17.1):
  - Execution time (min, max, avg, p95, p99)
  - Success/failure rates
  - Timeout counts
  - Fallback usage
- **Game Metrics** (per Section 17.2):
  - Total games played
  - Win/loss/draw counts
  - Average game duration
  - Moves per game
- **System Metrics** (per Section 17.3):
  - API request rate
  - Response times
  - Error rates
  - LLM token usage

**Export Formats:**
- JSON API endpoint: `/api/metrics`
- Prometheus format (optional)
- CloudWatch/DataDog integration (optional)

**Subsection Tests**:
- Agent metrics collected: execution time (min, max, avg, p95, p99)
- Agent metrics collected: success/failure rates per agent
- Agent metrics collected: timeout counts per agent
- Agent metrics collected: fallback usage counts per agent
- Game metrics collected: total games, win/loss/draw counts
- Game metrics collected: average game duration, moves per game
- System metrics collected: API request rate, response times, error rates
- System metrics collected: LLM token usage (total, per provider, per model)
- Metrics export via JSON API endpoint `/api/metrics` returns valid JSON
- Metrics aggregation calculates min, max, avg, p95, p99 correctly
- Metrics format complies with Section 17 specification

**Test Coverage**:
- **Subsection Tests**: ~11 tests for Phase 8.2 incremental development
- **Acceptance Criteria**: Metrics Collection (Section 17 - Metrics Format Specification) - agent metrics, game metrics, system metrics, export formats
- **Test Files**: `tests/unit/metrics/test_collector.py`, `tests/unit/metrics/test_exporter.py`, `tests/integration/test_metrics_api.py`

#### 8.3. Health Checks

**Implementation:**
- Liveness probe: `/health` (already implemented in Phase 4)
- Readiness probe: `/ready` (already implemented in Phase 4)
- Deep health check: `/health/deep` (check all dependencies)

**Subsection Tests**:
- Liveness probe `/health` returns 200 with correct response format when healthy
- Liveness probe `/health` returns 503 when unhealthy
- Readiness probe `/ready` checks game engine initialization
- Readiness probe `/ready` checks agent system readiness
- Readiness probe `/ready` checks LLM configuration (optional in Phase 4)
- Deep health check `/health/deep` validates all dependencies (game engine, agents, LLM config, metrics collector)
- Health check error scenarios handled (dependency failures return appropriate status codes)
- Health check response time < 100ms for `/health`, < 500ms for `/ready`, < 1000ms for `/health/deep`

**Test Coverage**:
- **Subsection Tests**: ~8 tests for Phase 8.3 incremental development
- **Acceptance Criteria**: Health Checks (Section 10 - Deployment Considerations) - liveness, readiness, deep health checks, response times
- **Test Files**: `tests/integration/test_health_checks.py`

**Phase 8 Deliverables:**
- ✅ Configuration system supporting multiple environments
- ✅ Structured logging with JSON format
- ✅ Comprehensive metrics collection
- ✅ Health check endpoints ready for orchestration
- ✅ Comprehensive test coverage for configuration, logging, metrics, and health checks

**Spec References:**
- Section 9: Configuration Management
- Section 17: Metrics and Observability

---

### Phase 9: Documentation and Deployment

**Duration**: 2-3 days

**Goal**: Production deployment and user documentation

#### 9.0. Documentation

**Files to Create:**
- `README.md` (update with complete usage)
- `docs/API.md` (API documentation with examples)
- `docs/DEPLOYMENT.md` (deployment guide)
- `docs/DEVELOPMENT.md` (developer setup guide)
- `docs/ARCHITECTURE.md` (system architecture overview)

**README Contents:**
- Project overview
- Quick start guide
- Installation instructions
- Running locally
- Running tests
- Configuration options
- API usage examples
- License and contributing

#### 9.1. Docker Containerization

**Spec Reference**: Section 10 - Deployment Considerations

**Create `Dockerfile`:**

```dockerfile
# Multi-stage build for minimal production image
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Create `.dockerignore`:**

```
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
.git/
.github/
*.md
tests/
.env
.env.local
```

**Create `docker-compose.yml` for Local Development:**

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - LLM_PROVIDER=${LLM_PROVIDER:-openai}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./src:/app/src  # Hot reload in development
      - ./logs:/app/logs
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Update docker-compose.yml for Production:**
```yaml
services:
  api:
    image: agentic-tictactoe:${VERSION:-latest}
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - LOG_LEVEL=INFO
      - LLM_PROVIDER=${LLM_PROVIDER}
    secrets:
      - openai_api_key
      - anthropic_api_key
      - google_api_key
    volumes:
      - ./logs:/app/logs
      - ./metrics:/app/metrics
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

secrets:
  openai_api_key:
    external: true
  anthropic_api_key:
    external: true
  google_api_key:
    external: true
```

#### 9.2. Local Deployment

**Spec Reference**: Section 10.1 - Local Development

**Setup:**
```bash
# Clone repository
git clone https://github.com/arun-gupta/agentic-tictactoe.git
cd agentic-tictactoe

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run tests
pytest

# Start API server
uvicorn src.api.main:app --reload

# Open UI in browser
open http://localhost:8000
```

#### 9.3. Production Deployment

**Spec Reference**: Section 10.2 - Production Deployment

**Deployment Options:**

**Option 1: Docker on Cloud VM**
- Deploy to AWS EC2, Google Cloud Compute, Azure VM
- Use docker-compose for orchestration
- Set up reverse proxy (Nginx)
- Configure SSL/TLS certificates

**Option 2: Kubernetes**
- Create Kubernetes manifests (Deployment, Service, Ingress)
- Deploy to EKS, GKE, or AKS
- Set up ConfigMap and Secrets for configuration
- Configure autoscaling

**Option 3: Serverless** (if applicable)
- AWS Lambda + API Gateway
- Google Cloud Run
- Limitations: May need to adjust timeout values

#### 9.4. Add Docker Build to CI Pipeline

**Update `.github/workflows/ci.yml`** to add Docker build verification:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov black ruff mypy

    - name: Run linting (black)
      run: black --check src/ tests/

    - name: Run linting (ruff)
      run: ruff check src/ tests/

    - name: Run type checking (mypy)
      run: mypy src/ --strict

    - name: Run tests with coverage
      run: pytest tests/ --cov=src --cov-report=xml --cov-report=term --cov-fail-under=80

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  docker-build:
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Build Docker image
      run: docker build -t agentic-tictactoe:${{ github.sha }} .

    - name: Test Docker image
      run: |
        docker run --rm agentic-tictactoe:${{ github.sha }} python -c "import src; print('Import successful')"
```

#### 9.5. Continuous Deployment Pipeline

**Note**: CI pipeline was enhanced above. This adds CD (deployment) pipeline.

**Files to Create:**
- `.github/workflows/deploy.yml`

**CD Pipeline:**

```yaml
name: Deploy

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v'))

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: your-dockerhub-username/agentic-tictactoe
        tags: |
          type=ref,event=branch
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Deploy to production (example)
      run: |
        # Add your deployment script here
        # Examples:
        # - SSH to server and pull new image
        # - Update Kubernetes deployment
        # - Deploy to cloud platform (AWS ECS, Google Cloud Run, etc.)
        echo "Deploy to production server"

    - name: Run smoke tests
      run: |
        # Wait for deployment
        sleep 30
        # Run basic health check
        curl -f https://your-production-url.com/health || exit 1
```

**Deployment Secrets to Add:**
- `DOCKER_USERNAME`: Docker Hub username
- `DOCKER_PASSWORD`: Docker Hub password or token
- Cloud platform credentials (if deploying to AWS/GCP/Azure)

**Phase 9 Deliverables:**
- ✅ Complete documentation (README, API docs, deployment guide)
- ✅ Docker containerization (Dockerfile, docker-compose.yml, .dockerignore)
- ✅ Docker build added to CI pipeline
- ✅ CD pipeline configured for automatic deployment
- ✅ Production deployment ready
- ✅ Monitoring and alerting set up

**Spec References:**
- Section 10: Deployment Considerations
- Section 10.1: Local Development
- Section 10.2: Production Deployment

---

### Phase 10: MCP Distributed Mode (Optional)

**Duration**: 3-5 days

**Goal**: Implement distributed agent coordination using Model Context Protocol

**Spec Reference**: Section 15 - Agent Mode Architecture - Mode 2: Distributed MCP

**Note**: This phase is optional. The system is fully functional in local mode. Implement MCP mode only if you want to explore distributed agent architecture.

#### 10.0. MCP Protocol Implementation

**Files to Create:**
- `src/mcp/client.py`
- `src/mcp/server.py`
- `src/mcp/protocol.py`
- `tests/integration/test_mcp.py`

**Implementation:**
- MCP client for coordinator
- MCP server wrappers for each agent
- Protocol message definitions (JSON-RPC)
- Transport layer (HTTP, WebSocket, or stdio)

**Test Coverage**: MCP Protocol Implementation (Section 15.2 - Mode 2: Distributed MCP)
- MCP client implementation (protocol compliance, message serialization)
- MCP server implementation (request handling, response formatting)
- Protocol message definitions (JSON-RPC validation)
- Transport layer (HTTP, WebSocket, stdio)
- Protocol error handling
- Connection management

**Test Files**: `tests/unit/mcp/test_client.py`, `tests/unit/mcp/test_server.py`, `tests/unit/mcp/test_protocol.py`

#### 10.1. Agent MCP Adaptation

**Tasks:**
- Wrap Scout agent as MCP server
- Wrap Strategist agent as MCP server
- Wrap Executor agent as MCP server
- Coordinator communicates via MCP protocol

**Test Coverage**: Agent MCP Adaptation (Section 15.2)
- Scout agent MCP server wrapper (tool exposure, request handling)
- Strategist agent MCP server wrapper (tool exposure, request handling)
- Executor agent MCP server wrapper (tool exposure, request handling)
- Coordinator MCP client communication
- Agent behavior consistency (local vs MCP mode)
- Distributed agent coordination

**Test Files**: `tests/integration/test_mcp_agents.py`, `tests/integration/test_mcp_coordinator.py`

#### 10.2. Mode Switching

**Implementation:**
- Configuration: `AGENT_MODE=local` or `AGENT_MODE=mcp`
- Factory pattern to create local or MCP agents
- Same interface regardless of mode
- Runtime mode switching (optional)

**Test Coverage**: Mode Switching (Section 15 - Agent Mode Architecture)
- Configuration-based mode selection (`AGENT_MODE=local` vs `AGENT_MODE=mcp`)
- Factory pattern implementation (local agent creation, MCP agent creation)
- Interface consistency (same interface regardless of mode)
- Runtime mode switching (if implemented)
- Fallback from MCP to local mode on failure
- Mode switching error handling

**Test Files**: `tests/integration/test_mode_switching.py`, `tests/integration/test_mcp_fallback.py`

**Phase 10 Deliverables:**
- ✅ MCP protocol implementation
- ✅ Agents runnable as MCP servers
- ✅ Coordinator communicates via MCP
- ✅ Mode switching between local and MCP
- ✅ Comprehensive test coverage for MCP protocol, agent adaptation, and mode switching

**Spec References:**
- Section 15: Agent Mode Architecture
- Section 15.2: Mode 2: Distributed MCP

---

## Testing Checklist by Phase

Use this checklist to verify each phase is complete:

### Phase 1: Domain Models
- [ ] All 84 domain model tests pass
- [ ] 100% coverage on domain layer
- [ ] `mypy` type checking passes with no errors
- [ ] All `AC-2.X.Y` acceptance criteria covered

### Phase 2: Game Engine
- [ ] All 58 game engine tests pass
- [ ] 100% coverage on game engine
- [ ] Can play full game (human vs human) via engine API
- [ ] All `AC-4.1.X.Y` acceptance criteria covered

### Phase 3: Agent System
- [ ] All 66 agent tests pass (10 + 8 + 7 + 41)
- [ ] Agent pipeline completes within 15s
- [ ] AI can make valid moves in all game states
- [ ] Fallback strategies work when primary logic fails
- [ ] All `AC-3.X.Y` acceptance criteria covered

### Phase 4: REST API
- [ ] All 36 API tests pass
- [ ] Can make moves via curl/Postman
- [ ] Error responses include correct HTTP status codes
- [ ] `/health` and `/ready` endpoints work
- [ ] All `AC-5.X.Y` acceptance criteria covered

### Phase 5: LLM Integration
- [ ] LLM provider abstraction works (all providers tested)
- [ ] Scout enhanced with LLM analysis
- [ ] Strategist enhanced with LLM recommendations
- [ ] Fallback to rule-based logic works
- [ ] Configuration supports provider switching
- [ ] LLM metrics tracked correctly
- [ ] All LLM integration tests passing (provider, agent integration, config, metrics)

### Phase 6: Web UI
- [ ] All 25 user stories implemented
- [ ] UI matches visual design spec (ui-spec.md)
- [ ] Game playable in browser
- [ ] Error messages display correctly
- [ ] All `AC-US00X.Y` acceptance criteria covered

### Phase 7: Testing & QA
- [ ] 399 tests passing (one per AC)
- [ ] ≥80% code coverage overall
- [ ] 100% coverage on domain models and game engine
- [ ] Performance requirements met (15s agent timeout, 100ms UI updates)
- [ ] E2E scenarios validated

### Phase 8: Configuration & Observability
- [ ] Configuration loads from environment variables
- [ ] Structured logging outputs JSON
- [ ] Metrics collected and exportable
- [ ] Health checks return correct status
- [ ] All configuration tests passing
- [ ] All logging tests passing
- [ ] All metrics tests passing
- [ ] All health check tests passing

### Phase 9: Documentation & Deployment
- [ ] README complete with usage examples
- [ ] Docker image builds successfully
- [ ] `docker-compose up` starts the application
- [ ] CI/CD pipeline runs on push
- [ ] Production deployment guide complete

### Phase 10: MCP Mode (Optional)
- [ ] MCP protocol implemented
- [ ] Agents runnable as MCP servers
- [ ] Mode switching works (local ↔ MCP)
- [ ] All MCP protocol tests passing
- [ ] All agent MCP adaptation tests passing
- [ ] All mode switching tests passing

---

## Estimated Timeline

**Total Duration: 28-42 days (6-8 weeks)**

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 0: Project Setup + Basic CI | 1 day | 1 day |
| Phase 1: Domain Models + Enhanced CI/CD | 3-5 days | 6 days |
| Phase 2: Game Engine | 3-4 days | 10 days |
| Phase 3: Agent System | 5-7 days | 17 days |
| Phase 4: REST API | 3-4 days | 21 days |
| Phase 5: LLM Integration | 3-4 days | 25 days |
| Phase 6: Web UI | 4-6 days | 31 days |
| Phase 7: Testing & QA | 3-4 days | 35 days |
| Phase 8: Config & Observability | 2-3 days | 38 days |
| Phase 9: Documentation & Deployment | 1-2 days | 40 days |
| Phase 10: MCP Mode (Optional) | 3-5 days | 45 days |

**Notes:**
- Timeline assumes one developer working full-time
- **Phase 0** is lightweight (1 day) - basic CI to get started quickly
- **Phase 1** includes CI/CD enhancement (coverage, type checking) + domain models
- **Phase 9** adds Docker containerization and deployment automation
- Adjust based on your experience level
- Phases 0-4 are minimum viable product (MVP) - **21 days (~3 weeks)**
- Phases 5-9 are production-ready system - **40 days (~6 weeks)**
- Phase 10 is optional enhancement

**Key Milestones:**
- ✅ Day 1: Basic CI running, can start coding immediately
- ✅ Day 6: Production-grade CI/CD (coverage, type checking) + domain models complete
- ✅ Day 10: Game engine complete, can play human vs human
- ✅ Day 21: MVP complete - API-driven game with rule-based AI
- ✅ Day 25: LLM-enhanced AI intelligence
- ✅ Day 31: Full UI with all features
- ✅ Day 40: Production-ready system

---

## Risk Mitigation

### Risk 1: LLM API Rate Limits
**Mitigation:**
- Implement exponential backoff and retry logic
- Use fallback to rule-based logic on failure
- Cache LLM responses for similar game states (optional)

### Risk 2: Agent Timeout Exceeded
**Mitigation:**
- Fallback strategies already defined in spec
- Rule-based logic works without LLM
- Progressive timeout UI keeps user informed

### Risk 3: Test Coverage Gaps
**Mitigation:**
- Write tests in parallel with implementation (TDD)
- Use acceptance criteria as test specifications
- Review coverage report after each phase

### Risk 4: Scope Creep
**Mitigation:**
- Refer to Section 1 - Non-Goals
- Stay focused on 25 user stories only
- Defer enhancements to future phases

---

## Next Steps

**Start Now:**
1. Review this implementation plan
2. Set up development environment (Phase 0)
3. Begin Phase 1: Domain Models
4. Write tests first (TDD approach)
5. Reference acceptance criteria for each test

**Questions to Consider:**
- Do you want to implement all phases or stop at MVP (Phase 4)?
- Will you implement MCP mode (Phase 10)?
- Any adjustments to the timeline based on your availability?

**Spec Coverage:**
This implementation plan covers:
- ✅ All 399 acceptance criteria
- ✅ All 25 user stories
- ✅ All technical requirements (Sections 1-13)
- ✅ All recommended technologies (Section 14.1)
- ✅ Test-driven development approach (Section 11)

Good luck with your implementation! 🚀
