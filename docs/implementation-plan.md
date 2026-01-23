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
- ⏸️ Docker build deferred to Phase 6 (Cloud Native Deployment)

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

**4.0.2. Request/Response Models** ✅
- ✅ Implement Pydantic models per Section 5.3:
  - ✅ `MoveRequest` (row, col) - validation for bounds (0-2)
  - ✅ `MoveResponse` (updated state, AI move) - includes success, position, updated_game_state, ai_move_execution, error_message
  - ✅ `GameStatusResponse` (complete game state) - includes GameState, agent_status, metrics
  - ✅ `ErrorResponse` (error code, message, details) - follows Section 5.4 error response schema

**Subsection Tests** (16 tests for incremental development): ✅
- ✅ MoveRequest validation (row/col bounds 0-2)
- ✅ MoveRequest rejects invalid values (row/col < 0 or > 2)
- ✅ MoveResponse structure (success, position, updated_game_state when success=True)
- ✅ MoveResponse includes ai_move_execution when AI moved
- ✅ MoveResponse includes error_message when success=False
- ✅ MoveResponse rejects empty error_message
- ✅ MoveResponse rounds execution time to 2 decimals
- ✅ GameStatusResponse structure (game_state, agent_status, metrics)
- ✅ GameStatusResponse optional fields (agent_status, metrics can be None)
- ✅ ErrorResponse structure (status="failure", error_code, message, timestamp, details)
- ✅ ErrorResponse timestamp is ISO 8601 format
- ✅ ErrorResponse timestamp defaults to current time
- ✅ ErrorResponse status must be "failure"
- ✅ All models serialize to JSON correctly
- ✅ All models deserialize from JSON correctly

**Test Coverage**: ✅
- **Subsection Tests**: ✅ 16 tests for Phase 4.0.2 model validation and serialization
- **Test File**: ✅ `tests/integration/api/test_api_models.py`
- **Note**: Model validation tests verify Section 5.3 constraints. Actual endpoint usage covered in AC-5.4.X, AC-5.5.X, etc.

#### 4.1. Health and Readiness Endpoints

**Spec Reference**: Section 5.2 - REST API Endpoints

**4.1.1. GET /health** ✅ **COMPLETE**
- Return basic health status
- Check if API is running
- No dependencies checked

**Implementation Notes:**
- Implemented server state tracking with `_server_start_time` and `_server_shutting_down` globals
- Uptime calculated from server start time, rounded to 2 decimal places
- Shutdown state tracked in lifespan context manager
- Timestamp in ISO 8601 format with 'Z' suffix for UTC

**Subsection Tests** ✅:
- ✅ GET /health returns 200 with status="healthy" when server is running
- ✅ GET /health response includes timestamp in ISO 8601 format
- ✅ GET /health response includes uptime_seconds as float with 2 decimal precision
- ✅ GET /health response completes within 100ms
- ✅ GET /health returns 503 with status="unhealthy" when shutting down

**Test Coverage** ✅:
- **Subsection Tests**: 5 tests implemented and passing
- **Acceptance Criteria**: AC-5.1.1, AC-5.1.2, AC-5.1.3 verified (AC-5.1.4 is for failure case, tested via shutdown)
- **Test File**: `tests/integration/api/test_api_health.py`

**4.1.2. GET /ready** ✅ **COMPLETE**
- Check game engine is initialized
- Check agent system is ready
- Verify LLM providers are configured (optional in Phase 4)
- Return detailed readiness status

**Implementation Notes:**
- Implemented readiness checks: game_engine, agent_system, configuration, llm_configuration
- Game engine check: Verifies GameEngine can be instantiated and get_current_state() works
- Agent system check: Verifies AgentPipeline can be instantiated with all agents initialized
- LLM configuration check: Checks for OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY
- In Phase 4, LLM configuration is optional - returns "not_configured" but doesn't block readiness
- Returns 200 with checks object when all required checks pass (game_engine, agent_system, configuration)
- Returns 503 with errors array when any required check fails
- Note: AC-5.2.6 (game endpoints return 503 when /ready returns 503) will be tested in Phase 4.2.x

**Subsection Tests** ✅:
- ✅ GET /ready returns 200 with status="ready" when all checks pass
- ✅ GET /ready response includes checks object with game_engine status
- ✅ GET /ready response includes checks object with configuration status
- ✅ GET /ready response includes checks object with agent_system status
- ✅ GET /ready returns checks.llm_configuration="not_configured" when LLM keys missing (optional in Phase 4)
- ✅ GET /ready returns checks.llm_configuration="ok" when LLM keys configured
- ✅ GET /ready returns 503 with status="not_ready" when checks fail
- ✅ GET /ready returns 503 with errors array when checks fail

**Test Coverage** ✅:
- **Subsection Tests**: 8 tests implemented and passing
- **Acceptance Criteria**: AC-5.2.1, AC-5.2.2 verified (AC-5.2.3, AC-5.2.4, AC-5.2.5 tested; AC-5.2.6 requires game endpoints - Phase 4.2.x)
- **Test File**: `tests/integration/api/test_api_ready.py`

#### 4.2. Game Control Endpoints

**4.2.1. POST /api/game/new** ✅ **COMPLETE**
- Create new game session
- Initialize game engine
- Return game ID and initial state
- Optionally accept player symbol preference

**Implementation Notes:**
- Implemented POST /api/game/new endpoint with game session management
- Uses in-memory dictionary (`_game_sessions`) to store GameEngine instances mapped by game_id (UUID v4)
- Generates unique game_id using `uuid.uuid4()`
- Accepts optional `NewGameRequest` with `player_symbol` preference (defaults to "X")
- Determines AI symbol as opposite of player symbol
- Checks service readiness (AC-5.3.1) - returns 503 with `E_SERVICE_NOT_READY` if service not ready
- Returns `NewGameResponse` with `game_id` and initial `GameState` (MoveCount=0, empty board)
- Logs game creation event with game_id, player_symbol, and ai_symbol

**Subsection Tests** ✅:
- ✅ POST /api/game/new creates new game session and returns 200
- ✅ POST /api/game/new returns game_id in response
- ✅ POST /api/game/new returns initial GameState with MoveCount=0, empty board
- ✅ POST /api/game/new accepts optional player_symbol preference
- ✅ POST /api/game/new defaults to X for player if not specified
- ✅ POST /api/game/new returns 503 when service not ready (AC-5.3.1)

**Test Coverage** ✅:
- **Subsection Tests**: 6 tests implemented and passing
- **Acceptance Criteria**: AC-5.3.1 verified (service readiness check)
- **Test File**: `tests/integration/api/test_api_game.py`

**4.2.2. POST /api/game/move** ✅
- Accept player move (row, col)
- Validate move via game engine
- Trigger AI agent pipeline
- Return updated game state + AI move
- Handle errors per Section 5.4

**Implementation Notes** ✅:
- Implemented POST /api/game/move endpoint with move validation and AI pipeline integration
- Accepts `MoveRequest` with `game_id`, `row`, and `col`
- Validates move bounds (0-2) before game engine validation to return 400 with `E_MOVE_OUT_OF_BOUNDS`
- Uses `GameEngine.validate_move()` for comprehensive validation (bounds, cell empty, game over, turn order)
- Executes player move, then triggers `AgentPipeline.execute_pipeline()` if game is not over
- Executes AI move on the engine after pipeline completes successfully
- Returns `MoveResponse` with `updated_game_state`, `ai_move_execution`, `fallback_used`, and `total_execution_time_ms`
- Handles all error cases: 400 (invalid move), 404 (game not found), 503 (service not ready), 422 (malformed JSON), 500 (server error)
- Logs move execution events with game_id, position, player, and AI move details

**Subsection Tests** ✅:
- ✅ POST /api/game/move accepts valid MoveRequest and returns 200 (AC-5.4.1)
- ✅ POST /api/game/move validates move bounds (rejects row/col < 0 or > 2) → 400 E_MOVE_OUT_OF_BOUNDS (AC-5.4.2)
- ✅ POST /api/game/move validates cell is empty (rejects occupied cell) → 400 E_CELL_OCCUPIED (AC-5.4.3)
- ✅ POST /api/game/move validates game is not over (rejects if game ended) → 400 E_GAME_ALREADY_OVER (AC-5.4.4)
- ✅ POST /api/game/move triggers AI agent pipeline after valid player move (AC-5.4.5)
- ✅ POST /api/game/move returns MoveResponse with updated_game_state and ai_move_execution (AC-5.4.5)
- ✅ POST /api/game/move handles game win condition (sets IsGameOver=true, winner) (AC-5.4.6)
- ✅ POST /api/game/move handles malformed JSON → 422 Unprocessable Entity (AC-5.4.7)
- ✅ POST /api/game/move handles server errors → 500 with error message (AC-5.4.8)

**Test Coverage** ✅:
- **Subsection Tests**: 9 tests implemented and passing
- **Acceptance Criteria**: AC-5.4.1 through AC-5.4.8 verified (8 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

**4.2.3. GET /api/game/status** ✅
- Return current game state
- Include board, move history, game over status
- Return agent insights (if available)

**Implementation Notes** ✅:
- Implemented GET /api/game/status endpoint with game status retrieval
- Accepts `game_id` as query parameter
- Looks up game session from `_game_sessions` dictionary
- Returns `GameStatusResponse` with `game_state` (required), `agent_status` (optional), and `metrics` (optional)
- `agent_status` is None in Phase 4 (async agent processing tracking will be implemented in Phase 5 with LLM integration)
- `metrics` is populated when game is completed (`is_game_over=True`), including `game_outcome`, `move_count`, `is_game_over`, and `winner`
- Handles all error cases: 404 (game not found), 503 (service not ready)
- Logs game status requests with game_id, move_count, and is_game_over status

**Subsection Tests** ✅:
- ✅ GET /api/game/status returns 200 with GameStatusResponse when game active (AC-5.5.1)
- ✅ GET /api/game/status includes current GameState (board, move_count, current_player) (AC-5.5.1)
- ✅ GET /api/game/status returns 404 when no active game exists (AC-5.5.2)
- ✅ GET /api/game/status includes agent_status when AI is processing (AC-5.5.3)
- ✅ GET /api/game/status includes metrics dictionary when game is completed (AC-5.5.4)

**Test Coverage** ✅:
- **Subsection Tests**: 5 tests implemented and passing
- **Acceptance Criteria**: AC-5.5.1 through AC-5.5.4 verified (4 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

**4.2.4. POST /api/game/reset** ✅
- Reset current game to initial state
- Clear move history
- Reinitialize agents

**Implementation Notes** ✅:
- Implemented POST /api/game/reset endpoint with game reset functionality
- Accepts `ResetGameRequest` with `game_id`
- Calls `GameEngine.reset_game()` to reset the game state to initial conditions
- Resets board to empty (all cells EMPTY), sets MoveCount=0, and CurrentPlayer=player_symbol (X)
- Clears move history (move_history will be implemented in a later phase)
- Returns `ResetGameResponse` with `game_id` (same as request) and reset `GameState`
- Keeps the same game_id (game is reset in-place, not replaced with a new game)
- Handles all error cases: 404 (game not found), 503 (service not ready)
- Logs game reset events with game_id and move_count

**Subsection Tests** ✅:
- ✅ POST /api/game/reset returns 200 with new GameState (AC-5.6.1)
- ✅ POST /api/game/reset resets board to empty (all cells EMPTY) (AC-5.6.1)
- ✅ POST /api/game/reset sets MoveCount=0 and CurrentPlayer=X (AC-5.6.1)
- ✅ POST /api/game/reset clears move_history (AC-5.6.2)
- ✅ POST /api/game/reset returns game_id (AC-5.6.3)
- ✅ POST /api/game/reset returns 404 when game not found

**Test Coverage** ✅:
- **Subsection Tests**: 6 tests implemented and passing
- **Acceptance Criteria**: AC-5.6.1 through AC-5.6.3 verified (3 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

**4.2.5. GET /api/game/history** ✅
- Return complete move history
- Include both player and AI moves
- Include timestamps and agent reasoning

**Implementation Notes** ✅:
- Created `MoveHistory` model in `src/api/models.py` with fields: `move_number`, `player`, `position`, `timestamp`, `agent_reasoning`
- Added `_move_history` dictionary to track move history per game session (in-memory)
- Modified `POST /api/game/new` to initialize empty move history for each new game
- Modified `POST /api/game/move` to record player moves and AI moves (with agent reasoning) in history
- Modified `POST /api/game/reset` to clear move history when game is reset
- Implemented `GET /api/game/history` endpoint to return array of `MoveHistory` objects in chronological order
- History is automatically in chronological order since moves are appended sequentially
- Returns 200 with empty array when no moves made
- Returns 404 when game not found
- Returns 503 when service not ready
- Handles all error cases with proper error responses

**Subsection Tests** ✅:
- ✅ GET /api/game/history returns 200 with array of MoveHistory objects (AC-5.7.1)
- ✅ GET /api/game/history returns moves in chronological order (oldest first) (AC-5.7.1)
- ✅ GET /api/game/history returns empty array when no moves made (AC-5.7.2)
- ✅ GET /api/game/history includes player, position, timestamp, move_number for each move (AC-5.7.3)
- ✅ GET /api/game/history includes AI moves with agent reasoning (if available) (AC-5.7.3)
- ✅ GET /api/game/history returns 404 when game not found

**Test Coverage** ✅:
- **Subsection Tests**: 6 tests implemented and passing
- **Acceptance Criteria**: AC-5.7.1 through AC-5.7.3 verified (3 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_game.py`

#### 4.3. Agent Status Endpoints

**Spec Reference**: Section 5.2 - Agent Status Endpoints

**4.3.1. GET /api/agents/{agent_name}/status** ✅
- Return status of each agent (idle/processing/success/failed)
- Include current processing agent
- Show elapsed time for current operation

**Implementation Notes** ✅:
- Created `AgentStatus` model in `src/api/models.py` with fields: `status`, `elapsed_time_ms`, `execution_time_ms`, `success`, `error_message`
- Added `_agent_status` dictionary to track agent status per agent (scout, strategist, executor) in-memory
- Modified `POST /api/game/move` to update agent status when pipeline executes:
  - Marks all agents as "processing" when pipeline starts
  - Updates all agents to "success" or "failed" after pipeline completes
  - Tracks execution times and error messages
- Implemented `GET /api/agents/{agent_name}/status` endpoint:
  - Returns 200 with `AgentStatus` for valid agent names (scout, strategist, executor)
  - Returns 404 for invalid agent names
  - Calculates `elapsed_time_ms` when status is "processing"
  - Returns last known status (idle/processing/success/failed) with execution details

**Subsection Tests** ✅:
- ✅ GET /api/agents/scout/status returns 200 with status="idle" when agent idle (AC-5.8.1)
- ✅ GET /api/agents/scout/status returns status="processing" with elapsed_time_ms when running (AC-5.8.2)
- ✅ GET /api/agents/strategist/status returns execution_time_ms and success=true when completed (AC-5.8.3)
- ✅ GET /api/agents/executor/status returns error_message and success=false when failed/timed out (AC-5.8.4)
- ✅ GET /api/agents/{invalid}/status returns 404 for invalid agent name (AC-5.8.5)
- ✅ Agent status is updated after pipeline execution

**Test Coverage** ✅:
- **Subsection Tests**: 6 tests implemented and passing
- **Acceptance Criteria**: AC-5.8.1 through AC-5.8.5 verified (5 official tests for final verification)
- **Test File**: `tests/integration/api/test_api_agents.py`

#### 4.4. Error Handling ✅

**Spec Reference**: Section 5.4 - Error Response Schema, Section 5.5 - HTTP Status Code Mapping

**Implementation:**
- Implement error response format per Section 5.4
- Map error codes to HTTP status codes per Section 5.5:
  - E_MOVE_OUT_OF_BOUNDS → 400 Bad Request
  - E_CELL_OCCUPIED → 400 Bad Request
  - E_GAME_ALREADY_OVER → 400 Bad Request
  - E_SERVICE_NOT_READY → 503 Service Unavailable
  - E_GAME_NOT_FOUND → 404 Not Found
  - E_INTERNAL_ERROR → 500 Internal Server Error
- Return consistent error structure with error code, message, details

**Subsection Tests** ✅:
- ✅ Error responses follow ErrorResponse schema (status="failure", error_code, message, timestamp, details)
- ✅ E_MOVE_OUT_OF_BOUNDS maps to 400 Bad Request
- ✅ E_CELL_OCCUPIED maps to 400 Bad Request
- ✅ E_GAME_ALREADY_OVER maps to 400 Bad Request
- ✅ E_SERVICE_NOT_READY maps to 503 Service Unavailable
- ✅ E_GAME_NOT_FOUND maps to 404 Not Found
- ✅ E_INTERNAL_ERROR maps to 500 Internal Server Error
- ✅ Error response timestamp is ISO 8601 format
- ✅ Error response details include field/expected/actual when applicable

**Implementation Notes** ✅:
- Implemented `_get_error_status_code()` helper function to map error codes to HTTP status codes per Section 5.5
- Updated `POST /api/game/move` endpoint to use `_get_error_status_code()` for consistent error code mapping
- Error responses follow ErrorResponse schema with status="failure", error_code, message, timestamp, and optional details
- Error code mappings match the spec: E_CELL_OCCUPIED and E_GAME_ALREADY_OVER map to 400 Bad Request (not 409 Conflict)

**Test Coverage** ✅:
- **Subsection Tests**: 8 tests implemented and passing
- **Test File**: `tests/integration/api/test_api_errors.py`
- **Note**: Error handling is tested as part of endpoint tests, and dedicated tests verify error code → HTTP status mapping

#### 4.5. API Demo Script ✅

**After Phase 4.4 completion**, add comprehensive API demo to `run_demo.sh`:

**Files to Create:**
- `scripts/play_via_api.py` - Interactive script that plays game via REST API ✅

**Demo Features:**
- Start FastAPI server (or assume it's running) ✅
- Use HTTP requests to play a complete game ✅
- Demonstrate all API endpoints: ✅
  - POST /api/game/new - Start new game ✅
  - POST /api/game/move - Make player moves ✅
  - GET /api/game/status - Check game state ✅
  - POST /api/game/reset - Reset game ✅
- Show API interactions (requests/responses) ✅
- Demonstrate error handling (invalid moves, out of bounds, occupied cells) ✅
- Display game board from API responses ✅
- Show agent analysis and move execution details ✅

**Update `run_demo.sh`:** ✅
- Add `api` option: `./run_demo.sh api` - Play game via REST API ✅
- Add to interactive menu as option 3 ✅
- Start FastAPI server if not running (or provide instructions) ✅

**Implementation Notes** ✅:
- Created `scripts/play_via_api.py` interactive script that plays a complete game via REST API
- Script uses `httpx` client to make HTTP requests to the FastAPI server
- Script demonstrates all API endpoints: POST /api/game/new, POST /api/game/move, GET /api/game/status
- Script includes error handling demonstration (out-of-bounds moves, occupied cells)
- Script displays game board and game status from API responses
- Script shows AI move execution details including position, reasoning, and execution time
- Updated `run_demo.sh` to add `api` option and include it in interactive menu as option 3
- Script checks server health and readiness before starting
- Script provides clear error messages if server is not running

**Test Coverage** ✅:
- Demo script successfully plays full game via API ✅
- Demo script handles errors gracefully (shows error responses) ✅
- Demo script demonstrates all implemented endpoints ✅
- Demo script shows proper API request/response format ✅

#### 4.6. Contract Testing ✅

**After Phase 4.5 completion**, validate API implementation matches OpenAPI specification before building LLM integration and Web UI layers.

**Status**: ✅ **COMPLETE** - All contract tests implemented and integrated into CI pipeline.

**Spec Reference**: Section 11 - Contract Tests

**Files to Create:**
- `tests/contract/__init__.py` - Contract test module
- `tests/contract/conftest.py` - Test fixtures (client, openapi_schema)
- `tests/contract/test_openapi_schema.py` - Schema structure validation
- `tests/contract/test_schemathesis_api.py` - Auto-generated API tests
- `tests/contract/test_response_contracts.py` - Response Pydantic validation

**Dependencies to Add** (in `pyproject.toml`):
- `schemathesis>=3.25.0` - Schema-based contract testing (used by Spotify, JetBrains)
- `hypothesis>=6.92.0` - Property-based testing (required by Schemathesis)

**Implementation:**
- Add pytest marker `contract` to `pyproject.toml` for selective test execution
- Validate OpenAPI schema has all endpoints documented
- Validate all response schemas are defined (ErrorResponse, GameState, etc.)
- Validate HTTP status codes are specified (201, 200, 404, 503)
- Use Schemathesis `@schema.parametrize()` to auto-generate tests from OpenAPI spec
- Validate responses deserialize to Pydantic models correctly
- Add contract test step to CI pipeline: `pytest tests/contract -v --tb=short`

**Subsection Tests**:
- OpenAPI schema has required info section (title="Agentic Tic-Tac-Toe API", version)
- OpenAPI schema documents all endpoints (/api/game/new, /health, /ready, etc.)
- Response schemas defined (ErrorResponse, GameState, MoveResponse, etc.)
- HTTP status codes specified for all endpoints (201, 200, 404, 503)
- Schemathesis validates /health endpoint responses match schema
- Schemathesis validates /ready endpoint responses match schema
- Schemathesis validates /api/game/new responses match schema
- Schemathesis validates /api/agents/{name}/status responses match schema
- NewGameResponse deserializes correctly from POST /api/game/new
- ErrorResponse deserializes correctly from 404 responses
- AgentStatus deserializes correctly from GET /api/agents/{name}/status

**Test Coverage**: ✅
- **Subsection Tests**: ✅ 11+ tests for contract validation implemented
- **Test Files**: ✅ `tests/contract/test_openapi_schema.py`, `tests/contract/test_schemathesis_api.py`, `tests/contract/test_response_contracts.py`
- **CI Integration**: ✅ Contract tests run in CI pipeline after unit/integration tests
- **Documentation**: ✅ Contract testing guide and DEVELOPMENT.md updated
- **Test Results**: ✅ 16/18 contract tests passing (7/9 Schemathesis, 4/4 schema validation, 5/5 response contracts)
- **Known Limitation**: ✅ Property-based testing edge case with optional request bodies documented (see CONTRACT_TESTING.md)
- **Note**: See [docs/guides/CONTRACT_TESTING.md](guides/CONTRACT_TESTING.md) for detailed implementation guide

**Implementation Notes** ✅:
- Added dependencies: `schemathesis>=3.25.0`, `hypothesis>=6.92.0` to `pyproject.toml`
- Added pytest marker `contract` for selective test execution
- Created contract test directory structure with fixtures and test files
- Implemented schema validation tests (OpenAPI structure, endpoints, schemas, status codes)
- Implemented Schemathesis auto-generated API tests for key endpoints
- Implemented response contract validation tests (Pydantic model deserialization)
- Added contract test step to CI pipeline (runs after main tests)
- Updated DEVELOPMENT.md with contract testing usage instructions
- Fixed OpenAPI schema to document all error responses (400, 404, 503)
- Added `extra="forbid"` to request models for strict validation
- Documented known limitation with property-based testing edge cases

**Phase 4 Deliverables:** ✅
- ✅ Complete REST API with all endpoints
- ✅ 36+ API integration tests passing
- ✅ Contract tests validating API matches OpenAPI specification (Phase 4.6) - 16/18 tests passing (known limitation documented)
- ✅ OpenAPI schema fully documented with all error responses (400, 404, 503)
- ✅ Error handling with proper HTTP status codes
- ✅ API can be tested with curl/Postman
- ✅ Game playable via API calls
- ✅ API demo script (`scripts/play_via_api.py`)

**Spec References:**
- Section 5: API Design (complete)
- Section 5.2: REST API Endpoints
- Section 5.4: Error Response Schema
- Section 5.6: HTTP Status Code Mapping
- Section 11: Contract Tests

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

**5.0.1. Provider Interface** ✅
- ✅ Define abstract `LLMProvider` interface
- ✅ Methods: `generate(prompt, model, max_tokens, temperature)`
- ✅ Return structured response with text, tokens, latency

**Subsection Tests**: ✅
- ✅ Abstract LLMProvider interface defines generate() method signature
- ✅ LLMProvider.generate() accepts prompt, model, max_tokens, temperature parameters
- ✅ LLMProvider.generate() returns structured response with text, tokens_used, latency_ms fields
- ✅ Cannot instantiate abstract LLMProvider directly (TypeError)

**5.0.2. OpenAI Provider** ✅
- ✅ Implement using `openai` SDK
- ✅ Support model: gpt-5.2
- ✅ Handle API errors and retries

**Subsection Tests**: ✅
- ✅ OpenAIProvider implements LLMProvider interface
- ✅ OpenAIProvider.generate() calls OpenAI API with correct parameters
- ✅ OpenAIProvider supports gpt-5.2 model
- ✅ OpenAIProvider handles API timeout errors (retries 3 times with exponential backoff)
- ✅ OpenAIProvider handles rate limit errors (429) with Retry-After header
- ✅ OpenAIProvider handles authentication errors (401/403) without retry
- ✅ OpenAIProvider returns structured response with text, tokens_used, latency_ms

**5.0.3. Anthropic Provider** ✅
- ✅ Implement using `anthropic` SDK
- ✅ Support Claude Haiku 4.5: claude-haiku-4-5-20251001 (fastest model with near-frontier intelligence)
- ✅ Support model alias: claude-haiku-4-5
- ✅ Claude Haiku 4.5 selected for speed and cost efficiency (per [Anthropic docs](https://platform.claude.com/docs/en/about-claude/models/overview))

**Implementation Notes:**
- Implemented AnthropicProvider following the same pattern as OpenAIProvider
- Uses Anthropic SDK's `messages.create()` API for chat completions
- Supports Claude Haiku 4.5 model (fastest model) with snapshot date and alias
- Supports retry logic with exponential backoff (1s, 2s, 4s) for timeouts and rate limits
- Handles authentication errors without retry (immediate failure)
- Returns structured LLMResponse with text, tokens_used (input + output), and latency_ms
- Token usage calculated from response.usage.input_tokens + response.usage.output_tokens

**Subsection Tests** ✅:
- ✅ AnthropicProvider implements LLMProvider interface
- ✅ AnthropicProvider.generate() calls Anthropic API with correct parameters
- ✅ AnthropicProvider supports claude-haiku-4-5-20251001 model
- ✅ AnthropicProvider supports claude-haiku-4-5 alias
- ✅ AnthropicProvider handles API timeout errors (retries 3 times with exponential backoff)
- ✅ AnthropicProvider handles rate limit errors (429) with Retry-After header
- ✅ AnthropicProvider handles authentication errors (401/403) without retry
- ✅ AnthropicProvider returns structured response with text, tokens_used, latency_ms

**Test Coverage** ✅:
- **Subsection Tests**: ✅ 13 tests implemented and passing (2 interface + 3 initialization + 4 generate + 4 error handling)
- **Test File**: ✅ `tests/unit/llm/test_anthropic_provider.py`

**5.0.4. Google Gemini Provider** ✅
- ✅ Implement using Google Generative AI SDK
- ✅ Support Gemini 3 Flash: gemini-3-flash-preview (most balanced model for speed, scale, and frontier intelligence)
- ⚠️ Note: Model alias `gemini-3-flash` is not recognized by the API - only `gemini-3-flash-preview` works
- ✅ Gemini 3 Flash recommended per [Google Gemini docs](https://ai.google.dev/gemini-api/docs/models)

**Implementation Notes:**
- Implemented GeminiProvider following the same pattern as OpenAIProvider and AnthropicProvider
- Uses Google Generative AI SDK's `GenerativeModel.generate_content()` API
- Supports Gemini 3 Flash Preview model (gemini-3-flash-preview) - most balanced model
- Supports retry logic with exponential backoff (1s, 2s, 4s) for timeouts and rate limits
- Handles authentication errors without retry (immediate failure)
- Returns structured LLMResponse with text, tokens_used (prompt + candidates), and latency_ms
- Token usage calculated from response.usage_metadata.prompt_token_count + candidates_token_count

**Known Issues:**
- ⚠️ **Issue**: `google.generativeai` package is deprecated and emits FutureWarning on import
  - **Impact**: Deprecation warning appears when importing GeminiProvider
  - **Fix**: Migrate to `google.genai` package (see https://github.com/google-gemini/deprecated-generative-ai-python)
  - **Status**: Filed as future work - no functional impact, only warning message

**Subsection Tests** ✅:
- ✅ GeminiProvider implements LLMProvider interface
- ✅ GeminiProvider.generate() calls Google Gemini API with correct parameters
- ✅ GeminiProvider supports gemini-3-flash-preview model
- ⚠️ Note: `gemini-3-flash` alias not supported by API - only `gemini-3-flash-preview` works
- ✅ GeminiProvider handles API timeout errors (retries 3 times with exponential backoff)
- ✅ GeminiProvider handles rate limit errors (429) with Retry-After header
- ✅ GeminiProvider handles authentication errors (401/403) without retry
- ✅ GeminiProvider returns structured response with text, tokens_used, latency_ms

**Test Coverage** ✅:
- **Subsection Tests**: ✅ 13 tests implemented and passing (2 interface + 3 initialization + 4 generate + 4 error handling)
- **Test File**: ✅ `tests/unit/llm/test_gemini_provider.py`

**5.0.5. Pydantic AI Implementation** ✅

**Framework Selected**: **Pydantic AI** (see Technology Stack section for selection rationale based on Section 19)

**Implementation Approach**:
- ✅ Use Pydantic AI's `Agent` class for type-safe agent definitions
- ✅ Define agents (Scout, Strategist) using Pydantic AI with Pydantic response models
- ✅ Use Pydantic AI's multi-provider support (OpenAI, Anthropic, Google Gemini)
- ✅ Leverage Pydantic AI's structured output validation for domain models (BoardAnalysis, Strategy)
- ✅ Use Pydantic AI's error handling and retry mechanisms

**Key Pydantic AI Features Used**:
- ✅ Type-safe agent definitions with Pydantic response models
- ✅ Automatic validation of LLM outputs against domain models
- ✅ Multi-provider support via provider configuration
- ✅ Built-in error handling and retry logic
- ✅ Agent workflow abstractions for Scout → Strategist coordination

**Implementation Notes**:
- Created `src/llm/pydantic_ai_agents.py` with `create_scout_agent()` and `create_strategist_agent()` functions
- Agents use `output_type` parameter to specify structured output models (BoardAnalysis, Strategy)
- Pydantic AI models read API keys from environment variables (set via `get_api_key()` from `.env` or env vars)
- Auto-selects first available provider when not specified (openai → anthropic → gemini)
- Auto-selects first model from config when not specified
- System prompts configured for each agent type (Scout for board analysis, Strategist for strategy planning)

**Subsection Tests** ✅:
- ✅ Pydantic AI Agent created with BoardAnalysis as output type (for Scout)
- ✅ Pydantic AI Agent created with Strategy as output type (for Strategist)
- ✅ Pydantic AI multi-provider support (OpenAI, Anthropic, Google Gemini via configuration)
- ✅ Auto-selects provider when not specified
- ✅ Raises error when API key missing
- ✅ Raises error when no provider configured
- ✅ Scout agent created for each provider (OpenAI, Anthropic, Gemini)
- ✅ Strategist agent created for each provider (OpenAI, Anthropic, Gemini)

**Test Coverage** ✅:
- **Subsection Tests**: ✅ 11 tests implemented and passing
- **Test File**: ✅ `tests/unit/llm/test_pydantic_ai_agents.py`
- **Note**: Pydantic AI's built-in validation, error handling, retry logic, and token tracking are tested implicitly through agent creation. Full integration testing with actual LLM calls will be done in Phase 5.1 (Agent LLM Integration).

**5.0.6. API Key Integration Testing** ✅

**Goal**: Verify that API key loading infrastructure works correctly across all LLM providers, ensuring secure and reliable key management.

**Files Created:**
- ✅ `scripts/test_api_keys.py` (executable test script)
- ✅ `docs/guides/LLM_TESTING.md` (testing guide with API key testing section)

**Implementation Notes:**
- Created comprehensive test script (`scripts/test_api_keys.py`) to verify API key infrastructure
- Tests cover the complete API key loading pipeline: `.env` file → environment variables → provider integration
- Verifies priority order: `.env` file takes precedence over environment variables
- Tests provider integration to ensure all LLM providers correctly use the centralized `_load_api_key()` method
- Distinguishes between core infrastructure tests (always run) and optional tests (real `.env` file, skipped if not present)
- Provides clear, actionable output with pass/fail/skip status for each test

**What Gets Tested:**

1. **Core Infrastructure Tests (Required)**:
   - ✅ Loading API keys from `.env` file (mocked test file)
   - ✅ Loading API keys from environment variables (when no `.env` file)
   - ✅ Priority order verification (`.env` file > environment variables)
   - ✅ Missing key handling (returns `None` gracefully)
   - ✅ Provider integration (OpenAI, Anthropic, Gemini providers use `_load_api_key()` correctly)

2. **Optional Tests**:
   - ✅ Real `.env` file loading (if `.env` file exists in project root)
   - ✅ Verification that keys from real `.env` file are actually loaded

**Test Script Usage:**
```bash
# Run all API key infrastructure tests
python scripts/test_api_keys.py
```

**Expected Output:**
- Core infrastructure tests: All must pass (required for system to work)
- Optional tests: May be skipped if `.env` file doesn't exist (not a failure)
- Clear summary showing which tests passed/failed/skipped
- Actionable guidance if tests fail (e.g., "Create .env file to test real loading")

**Subsection Tests** ✅:
- ✅ API keys load correctly from `.env` file (via `python-dotenv`)
- ✅ API keys load correctly from environment variables (fallback when no `.env`)
- ✅ Priority order: `.env` file values override environment variables
- ✅ Missing API keys return `None` (graceful handling)
- ✅ Real `.env` file loading works (if file exists in project root)
- ✅ OpenAIProvider integrates with API key loading (`_load_api_key()` method)
- ✅ AnthropicProvider integrates with API key loading (`_load_api_key()` method)
- ✅ GeminiProvider integrates with API key loading (`_load_api_key()` method)
- ✅ Providers raise appropriate `ValueError` when API keys are missing
- ✅ Error messages include provider name and environment variable name for clarity

**Test Coverage** ✅:
- **Subsection Tests**: ✅ 6 core tests + 1 optional test = 7 total tests
- **Test Script**: ✅ `scripts/test_api_keys.py` (executable, can be run independently)
- **Documentation**: ✅ `docs/guides/LLM_TESTING.md` includes API key testing section
- **Integration**: ✅ Tests verify end-to-end integration from `env_loader.py` → `LLMProvider._load_api_key()` → provider initialization

**Key Features:**
- ✅ No actual API calls made (safe to run without valid keys)
- ✅ Uses mocked `.env` files for core tests (no file system pollution)
- ✅ Tests real `.env` file if present (optional, informative)
- ✅ Verifies provider integration (ensures providers use centralized key loading)
- ✅ Clear pass/fail/skip reporting for each test
- ✅ Actionable error messages and guidance

**Related Files:**
- `src/utils/env_loader.py`: Core API key loading logic (`.env` file and environment variables)
- `src/llm/provider.py`: Base `LLMProvider` class with `_load_api_key()` method
- `src/llm/openai_provider.py`: Uses `_load_api_key()` for OpenAI API key
- `src/llm/anthropic_provider.py`: Uses `_load_api_key()` for Anthropic API key
- `src/llm/gemini_provider.py`: Uses `_load_api_key()` for Google API key
- `.env.example`: Template file showing required API key format

**Note**: This testing infrastructure ensures that API key management works correctly before attempting actual LLM API calls. It's a prerequisite for Phase 5.1 (Agent LLM Integration) where real API keys will be used.

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
- LLM providers integrated (OpenAI, Anthropic, Google)
- Scout and Strategist enhanced with LLM intelligence
- Fallback to rule-based logic still works
- Configuration supports provider switching
- Metrics tracked for all LLM calls
- API key integration testing infrastructure (5.0.6)
- Comprehensive test coverage for LLM integration (provider abstraction, agent integration, configuration, metrics, API key management)

**Spec References:**
- Section 16: LLM Integration (provider and model configuration)
- Section 19: LLM Framework Selection (comprehensive framework comparison and recommendations)
- Section 16.3: LLM Usage Patterns
- Section 12.1: LLM Provider Metadata

---

### Phase 6: Cloud Native Deployment

**Duration**: 3-4 days

**Goal**: Containerize application and deploy to Kubernetes to enable hot-swappable LLM providers and scalable agent architecture

**Why Sixth**: After LLM integration (Phase 5), cloud native deployment enables:
- **Hot-swappable LLM providers**: Switch between OpenAI, Anthropic, and Google Gemini at runtime via configuration
- **Scalable agent architecture**: Deploy agents as separate services that can scale independently
- **Dynamic provider switching**: Change LLM providers without code redeployment
- **Foundation for MCP**: Sets up infrastructure needed for distributed MCP mode (Phase 7)

**Prerequisites**: Phase 5 (LLM Integration) must be complete

#### 6.0. Docker Containerization

**Spec Reference**: Section 10 - Deployment Considerations

**Files to Create:**
- `Dockerfile` (multi-stage build)
- `.dockerignore`
- `docker-compose.yml` (local development)
- `docker-compose.prod.yml` (production)

**6.0.1. Dockerfile Implementation**

**Subsection Tests**:
- Dockerfile exists and follows multi-stage build pattern
- Dockerfile builds successfully without errors
- Docker image runs application correctly (uvicorn starts on port 8000)
- Docker image health check works (HEALTHCHECK command responds correctly)
- .dockerignore file excludes unnecessary files (.venv, __pycache__, tests, etc.)
- Docker image size is optimized (uses slim base image, multi-stage build)
- Docker image runs as non-root user (appuser)
- Dockerfile exposes correct port (8000)
- Docker image includes all required dependencies

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

**6.0.2. Docker Compose Configuration**

**Subsection Tests**:
- docker-compose.yml for local development exists and works
- docker-compose.prod.yml for production exists with correct configuration
- docker-compose up starts all services successfully
- docker-compose volumes mount correctly (src/ for hot reload, logs/)
- docker-compose environment variables are configured correctly (LLM_PROVIDER can be switched)
- docker-compose health checks work correctly
- docker-compose secrets management works (production config)
- LLM provider can be changed via environment variable without rebuilding image

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

**Create `docker-compose.prod.yml` for Production:**

```yaml
version: '3.8'

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

#### 6.1. Kubernetes Deployment

**Spec Reference**: Section 10.2 - Production Deployment

**Files to Create:**
- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/ingress.yaml`
- `k8s/configmap.yaml`
- `k8s/secrets.yaml`
- `k8s/hpa.yaml` (Horizontal Pod Autoscaler)

**6.1.1. Kubernetes Manifests**

**Subsection Tests**:
- Kubernetes manifests created (Deployment, Service, Ingress)
- ConfigMap configured for LLM provider switching (LLM_PROVIDER, LLM_MODEL)
- Secrets configured for API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
- Deployment can switch LLM provider via ConfigMap update (hot-swappable)
- Service exposes API on correct port
- Ingress configured with SSL/TLS termination
- Horizontal Pod Autoscaler configured for auto-scaling based on CPU/memory
- Deployment scales horizontally (multiple replicas)
- Rolling updates work without downtime

**Create `k8s/deployment.yaml`:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentic-tictactoe
  labels:
    app: agentic-tictactoe
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentic-tictactoe
  template:
    metadata:
      labels:
        app: agentic-tictactoe
    spec:
      containers:
      - name: api
        image: agentic-tictactoe:latest
        ports:
        - containerPort: 8000
        env:
        - name: LLM_PROVIDER
          valueFrom:
            configMapKeyRef:
              name: llm-config
              key: provider
        - name: LLM_MODEL
          valueFrom:
            configMapKeyRef:
              name: llm-config
              key: model
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: openai_api_key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: anthropic_api_key
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-secrets
              key: google_api_key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
```

**Create `k8s/configmap.yaml`** (enables hot-swappable LLM providers):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-config
data:
  provider: "openai"  # Can be changed to "anthropic" or "gemini" without redeployment
  model: "gpt-4o-mini"
```

**Create `k8s/hpa.yaml`** (Horizontal Pod Autoscaler):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agentic-tictactoe-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agentic-tictactoe
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**6.1.2. Provider Switching Strategy**

**Implementation:**
- LLM provider selection via ConfigMap (environment variable)
- Runtime provider switching without pod restart (via ConfigMap update + pod rolling update)
- Support for all three providers (OpenAI, Anthropic, Google Gemini)
- Zero-downtime provider switching using rolling updates

**Subsection Tests**:
- LLM provider can be changed by updating ConfigMap (kubectl apply -f k8s/configmap.yaml)
- ConfigMap update triggers rolling update (pods restart with new provider)
- Rolling update maintains service availability (no downtime)
- Provider switching verified via API calls (agent uses new provider)
- Multiple pods can use different providers during rolling update (eventually consistent)

#### 6.2. CI/CD Integration

**6.2.1. Docker Build in CI Pipeline**

**Update `.github/workflows/ci.yml`** to add Docker build verification:

```yaml
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

**6.2.2. Kubernetes Deployment Pipeline**

**Create `.github/workflows/deploy.yml`** for CD:

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

    - name: Login to Docker Registry
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: your-registry/agentic-tictactoe:latest,your-registry/agentic-tictactoe:${{ github.sha }}

    - name: Deploy to Kubernetes
      run: |
        # Update Kubernetes deployment with new image
        kubectl set image deployment/agentic-tictactoe api=your-registry/agentic-tictactoe:${{ github.sha }}
        kubectl rollout status deployment/agentic-tictactoe
```

**Subsection Tests**:
- CI pipeline includes Docker build job
- Docker build job runs after test job passes
- Docker build job builds image successfully
- CD pipeline pushes Docker image to registry
- CD pipeline deploys to Kubernetes cluster
- Kubernetes rolling update completes successfully
- Zero-downtime deployment verified

#### 6.3. Hot-Swappable LLM Providers

**Goal**: Enable runtime switching of LLM providers without code redeployment

**Implementation:**
- LLM provider configured via Kubernetes ConfigMap
- Application reads `LLM_PROVIDER` environment variable from ConfigMap
- ConfigMap update triggers rolling update with new provider
- All three providers (OpenAI, Anthropic, Google Gemini) supported

**Subsection Tests**:
- Application reads LLM_PROVIDER from ConfigMap environment variable
- Changing ConfigMap provider value triggers pod restart with new provider
- Rolling update maintains service availability during provider switch
- Agent uses correct LLM provider after ConfigMap update
- Provider switching logged and traceable
- API endpoints respond correctly after provider switch

**Phase 6 Deliverables:**
- Docker containerization (Dockerfile, docker-compose.yml, .dockerignore)
- Kubernetes manifests (Deployment, Service, Ingress, ConfigMap, Secrets, HPA)
- CI/CD integration (Docker build in CI, Kubernetes deployment in CD)
- Hot-swappable LLM providers via ConfigMap
- Zero-downtime deployment capability
- Comprehensive test coverage for containerization and Kubernetes deployment

**Spec References:**
- Section 10: Deployment Considerations
- Section 10.2: Production Deployment
- Section 16: LLM Integration (provider configuration)

---

### Phase 7: MCP Distributed Mode

**Duration**: 3-5 days

**Goal**: Implement distributed agent coordination using Model Context Protocol

**Why Seventh**: After cloud native deployment (Phase 6), MCP enables:
- **Distributed agent architecture**: Deploy agents as separate Kubernetes services
- **Independent agent scaling**: Scale Scout, Strategist, and Executor independently
- **Network-based agent communication**: Agents communicate via MCP protocol over HTTP
- **Hot-swappable agents**: Replace or upgrade individual agents without affecting others

**Prerequisites**: Phase 6 (Cloud Native Deployment) must be complete

**Spec Reference**: Section 15 - Agent Mode Architecture - Mode 2: Distributed MCP

**Note**: This phase builds on cloud native infrastructure. Agents can now be deployed as separate Kubernetes services, enabling true distributed architecture.

#### 7.0. MCP Protocol Implementation

**Spec Reference**: Section 15.2 - Mode 2: Distributed MCP

**Files to Create:**
- `src/mcp/protocol.py`
- `src/mcp/client.py`
- `src/mcp/server.py`
- `tests/unit/mcp/test_protocol.py`
- `tests/unit/mcp/test_client.py`
- `tests/unit/mcp/test_server.py`

**Implementation Order:**

**7.0.1. Protocol Message Definitions**
- Define JSON-RPC message structures (request, response, error)
- Implement message serialization/deserialization
- Validate JSON-RPC protocol compliance
- Error code definitions and handling

**Subsection Tests**:
- Protocol message definitions validate JSON-RPC structure
- Request messages serialize to valid JSON-RPC format
- Response messages serialize to valid JSON-RPC format
- Error messages follow JSON-RPC error specification
- Message deserialization handles invalid JSON gracefully

**7.0.2. MCP Client Implementation**
- Implement MCP client for coordinator
- HTTP transport layer for client-server communication
- Connection management (reconnection, timeouts)
- Error handling and retry logic

**Subsection Tests**:
- MCP client implements protocol correctly (JSON-RPC message format)
- MCP client serializes messages correctly (request/response)
- MCP client handles connection errors gracefully
- Connection management handles reconnection on failure
- Connection management handles connection timeouts
- HTTP transport integrates with Kubernetes service discovery

**7.0.3. MCP Server Implementation**
- Implement MCP server wrappers for agents
- HTTP endpoint handlers for MCP protocol
- Request routing to agent methods
- Response formatting according to protocol spec

**Subsection Tests**:
- MCP server handles incoming requests correctly
- MCP server formats responses according to protocol spec
- Server validates incoming JSON-RPC messages
- Server returns appropriate error codes for invalid requests
- Server handles concurrent requests correctly

**Test Coverage**:
- **Subsection Tests**: ~13 tests for Phase 7.0 incremental development (5 + 6 + 5)
- **Acceptance Criteria**: MCP Protocol Implementation (Section 15.2 - Mode 2: Distributed MCP) - protocol compliance, message serialization, transport, error handling
- **Test Files**: `tests/unit/mcp/test_protocol.py`, `tests/unit/mcp/test_client.py`, `tests/unit/mcp/test_server.py`

#### 7.1. Agent MCP Adaptation

**Spec Reference**: Section 15.2 - Mode 2: Distributed MCP

**Files to Create:**
- `src/mcp/agent_wrappers.py`
- `src/agents/coordinator_mcp.py`
- `tests/integration/test_mcp_agents.py`
- `tests/integration/test_mcp_coordinator.py`

**Implementation Order:**

**7.1.1. Scout Agent MCP Wrapper**
- Wrap Scout agent as MCP server
- Expose `analyze()` method as MCP tool
- Map MCP requests to Scout agent interface
- Return `BoardAnalysis` via MCP protocol

**Subsection Tests**:
- Scout agent MCP server exposes analyze() method as MCP tool
- Scout agent MCP server handles analyze requests correctly
- Scout agent MCP server validates input parameters (GameState)
- Scout agent MCP server returns BoardAnalysis in correct format
- Agent behavior is consistent between local mode and MCP mode (same outputs for same inputs)

**7.1.2. Strategist Agent MCP Wrapper**
- Wrap Strategist agent as MCP server
- Expose `plan()` method as MCP tool
- Map MCP requests to Strategist agent interface
- Return `Strategy` via MCP protocol

**Subsection Tests**:
- Strategist agent MCP server exposes plan() method as MCP tool
- Strategist agent MCP server handles plan requests correctly
- Strategist agent MCP server validates input parameters (BoardAnalysis)
- Strategist agent MCP server returns Strategy in correct format
- Agent behavior is consistent between local mode and MCP mode (same outputs for same inputs)

**7.1.3. Executor Agent MCP Wrapper**
- Wrap Executor agent as MCP server
- Expose `execute()` method as MCP tool
- Map MCP requests to Executor agent interface
- Return `MoveExecution` via MCP protocol

**Subsection Tests**:
- Executor agent MCP server exposes execute() method as MCP tool
- Executor agent MCP server handles execute requests correctly
- Executor agent MCP server validates input parameters (Strategy, GameState)
- Executor agent MCP server returns MoveExecution in correct format
- Agent behavior is consistent between local mode and MCP mode (same outputs for same inputs)

**7.1.4. Coordinator MCP Integration**
- Update coordinator to use MCP client for agent communication
- Implement pipeline execution via MCP protocol
- Handle MCP errors and timeouts consistently with local mode
- Maintain same pipeline flow (Scout → Strategist → Executor)

**Subsection Tests**:
- Coordinator MCP client can communicate with Scout MCP server
- Coordinator MCP client can communicate with Strategist MCP server
- Coordinator MCP client can communicate with Executor MCP server
- Distributed agent coordination works correctly (pipeline executes via MCP)
- MCP agents handle errors and timeouts consistently with local agents
- Pipeline maintains correct order (Scout → Strategist → Executor) in MCP mode

**Test Coverage**:
- **Subsection Tests**: ~17 tests for Phase 7.1 incremental development (5 + 5 + 5 + 6)
- **Acceptance Criteria**: Agent MCP Adaptation (Section 15.2) - tool exposure, request handling, behavior consistency, coordination
- **Test Files**: `tests/integration/test_mcp_agents.py`, `tests/integration/test_mcp_coordinator.py`

#### 7.2. Mode Switching

**Spec Reference**: Section 15 - Agent Mode Architecture

**Files to Create:**
- `src/agents/factory.py`
- `src/config/agent_mode.py`
- `tests/integration/test_mode_switching.py`
- `tests/integration/test_mcp_fallback.py`

**Implementation Order:**

**7.2.1. Configuration and Factory Pattern**
- Configuration: `AGENT_MODE=local` or `AGENT_MODE=mcp`
- Factory pattern to create local or MCP agents
- Same interface regardless of mode (BaseAgent)
- Agent factory selects correct implementation based on configuration

**Subsection Tests**:
- Configuration `AGENT_MODE=local` creates local agents (Scout, Strategist, Executor)
- Configuration `AGENT_MODE=mcp` creates MCP client agents
- Factory pattern creates correct agent type based on configuration
- Local agents and MCP agents implement same interface (BaseAgent)
- Factory handles invalid configuration values gracefully

**7.2.2. Fallback Strategy**
- Fallback from MCP to local mode on connection failure
- Fallback from MCP to local mode on timeout
- Fallback error handling and logging
- Preserve game state during fallback

**Subsection Tests**:
- Fallback from MCP to local mode triggers on MCP connection failure
- Fallback from MCP to local mode triggers on MCP timeout
- Fallback preserves game state (agents continue with same game state)
- Fallback logs mode change events
- Fallback error handling returns appropriate error messages

**7.2.3. Runtime Mode Switching (Optional)**
- Runtime mode switching without restart (if implemented)
- Mode switching preserves game state
- Mode switching error handling

**Subsection Tests**:
- Runtime mode switching works (if implemented, agents can switch modes without restart)
- Mode switching preserves game state (agents continue with same game state)
- Mode switching logs mode change events
- Mode switching error handling returns appropriate error messages

**Test Coverage**:
- **Subsection Tests**: ~12 tests for Phase 7.2 incremental development (5 + 5 + 4)
- **Acceptance Criteria**: Mode Switching (Section 15 - Agent Mode Architecture) - configuration-based selection, factory pattern, interface consistency, fallback, error handling
- **Test Files**: `tests/integration/test_mode_switching.py`, `tests/integration/test_mcp_fallback.py`

#### 7.3. Kubernetes Deployment for MCP Agents

**Spec Reference**: Section 10.2 - Production Deployment, Section 15.2 - Mode 2: Distributed MCP

**Files to Create:**
- `k8s/mcp-agents/scout-deployment.yaml`
- `k8s/mcp-agents/strategist-deployment.yaml`
- `k8s/mcp-agents/executor-deployment.yaml`
- `k8s/mcp-agents/scout-service.yaml`
- `k8s/mcp-agents/strategist-service.yaml`
- `k8s/mcp-agents/executor-service.yaml`
- `k8s/mcp-agents/scout-hpa.yaml`
- `k8s/mcp-agents/strategist-hpa.yaml`
- `k8s/mcp-agents/executor-hpa.yaml`
- `tests/integration/test_mcp_kubernetes.py`

**Implementation Order:**

**7.3.1. Agent Service Deployment**
- Deploy Scout, Strategist, and Executor as separate Kubernetes services
- Each agent runs as independent pod with MCP server endpoint
- Agent services expose MCP endpoints on standard ports
- Service discovery via Kubernetes DNS

**Subsection Tests**:
- Scout agent deployed as separate Kubernetes service (scout-service)
- Strategist agent deployed as separate Kubernetes service (strategist-service)
- Executor agent deployed as separate Kubernetes service (executor-service)
- Agent services expose MCP endpoints on standard ports
- Service discovery works via Kubernetes DNS (scout-service.default.svc.cluster.local)

**7.3.2. Coordinator Integration**
- Coordinator pod connects to agent services via MCP protocol
- Coordinator uses Kubernetes service discovery for agent endpoints
- Coordinator handles agent service unavailability gracefully

**Subsection Tests**:
- Coordinator connects to agent services via MCP over HTTP
- Coordinator resolves agent services via Kubernetes DNS
- Coordinator handles agent service unavailability gracefully
- Coordinator reconnects when agent services become available

**7.3.3. Scaling and Load Balancing**
- Independent scaling per agent (HorizontalPodAutoscaler for each agent service)
- Load balancing across multiple agent pods
- Agent pod restarts don't affect coordinator

**Subsection Tests**:
- Independent scaling works (can scale Scout without affecting Strategist)
- Agent services handle multiple concurrent MCP requests
- Load balancing works when multiple agent pods are running
- Agent pod restarts don't affect coordinator (reconnection handled)
- HorizontalPodAutoscaler scales agents based on CPU/memory metrics

**Test Coverage**:
- **Subsection Tests**: ~13 tests for Phase 7.3 incremental development (5 + 4 + 5)
- **Test Files**: `tests/integration/test_mcp_kubernetes.py`, `k8s/mcp-agents/` manifests

**Phase 7 Deliverables:**
- MCP protocol implementation
- Agents runnable as MCP servers
- Coordinator communicates via MCP
- Mode switching between local and MCP
- Kubernetes deployment for distributed agents
- Independent agent scaling capability
- Comprehensive test coverage for MCP protocol, agent adaptation, mode switching, and Kubernetes deployment

**Spec References:**
- Section 15: Agent Mode Architecture
- Section 15.2: Mode 2: Distributed MCP

---

### Phase 8: Web UI (User Interface Layer)

**Duration**: 4-6 days

**Goal**: Build interactive web UI for playing the game

**Why Eighth**: UI is the presentation layer. After cloud native deployment (Phase 6) and optional MCP (Phase 7), the UI provides the user-facing interface for the complete system.

**Figma Design Reference**: [Tic-Tac-Toe Design](https://www.figma.com/design/mhNp0FKIqT0mSBP8qKKvbi/Tic-Tac-Toe?node-id=2-510)

#### 8.0. UI Foundation ✅

**Status**: ✅ **COMPLETE** - Next.js + shadcn/ui initialized with zinc palette, JetBrains Mono font, and API client.

**Spec Reference**: Section 6 - Web UI Functional Requirements, docs/spec/ui-spec.md

**Files to Create:**
- `src/ui/` - React/Next.js application directory
- `src/ui/components/` - shadcn and custom components
- `src/ui/lib/api-client.ts` - API client wrapper

**Tech Stack (REQUIRED):**
- **React** with TypeScript (or Next.js)
- **shadcn/ui** - Component library (https://ui.shadcn.com/)
- **Tailwind CSS** - Styling (comes with shadcn/ui)
- **JetBrains Mono** - Font family (monospace aesthetic per Figma design)

**Required shadcn Components:**
- `npx shadcn@latest add tabs` - Main navigation (Board | Config | Metrics)
- `npx shadcn@latest add button` - New Game button
- `npx shadcn@latest add select` - Agent LLM selection dropdowns
- `npx shadcn@latest add input` - API key inputs, metrics display

**8.0.1. Design System Setup** ✅
- ✅ Initialize shadcn/ui with `npx shadcn@latest init`
- ✅ Configure zinc color palette (light theme per Figma design)
- ✅ Set up JetBrains Mono font family
- ✅ Configure Tailwind with shadcn CSS variables

**Subsection Tests**:
- ✅ shadcn/ui initialized and configured correctly
- ✅ Zinc color palette applied (zinc-100 background, zinc-700 borders)
- ✅ JetBrains Mono font family loaded and applied
- ✅ shadcn CSS variables accessible (--background, --foreground, --border, etc.)
- ✅ Tailwind CSS configured with shadcn preset

**8.0.2. API Client** ✅
- ✅ Create TypeScript wrapper for REST API
- ✅ Methods: `makeMove()`, `getGameStatus()`, `resetGame()`
- ✅ Handle errors and display to user

**Subsection Tests**:
- ✅ API client makeMove() method calls POST /api/game/move with correct parameters
- ✅ API client getGameStatus() method calls GET /api/game/status
- ✅ API client resetGame() method calls POST /api/game/reset
- ✅ API client handles 400 errors (invalid move) and displays error message
- ✅ API client handles 500 errors (server error) and displays error message
- ✅ API client handles network errors and displays user-friendly message

#### 8.1. Game Board UI ✅

**Status**: ✅ **COMPLETE** - GameBoard and Cell components implemented with all features.

**Spec Reference**: US-001, US-002, US-003, US-004, US-005 (Section 6)

**Figma Reference**: Board (node-id: 1:2770), Board Win (1:2463), Board Lost (1:2639)

**8.1.1. Display Game Board (US-001)** ✅
- ✅ Container: 640×640px with zinc-100 background and shadow
- ✅ Menu bar: shadcn Tabs (Board | Config | Metrics), Status text, "New Game" button
- ✅ Play Area: 3x3 grid centered in container
- ✅ 3x3 grid with 100×100px cells
- ✅ Cell borders: 1px solid zinc-700, rounded corners (8px)
- ✅ Move history text at bottom

**Subsection Tests**:
- ✅ Game board container renders at 640×640px
- ✅ Menu bar contains Tabs, Status, and New Game button
- ✅ Play area (3x3 grid) centered in container
- ✅ Each cell has dimensions 100px × 100px
- ✅ Cells display x, o (lowercase per Figma), or empty state correctly
- ✅ Board layout matches Figma design (node-id: 1:2770)

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 8.1.1 incremental development
- **Acceptance Criteria**: AC-US001.1 through AC-US001.3 (3 official tests for final verification)

**8.1.2. Make Player Move (US-002)** ✅
- ✅ Click handler on empty cells
- ✅ Disable board during AI turn
- ✅ Show hover effects on valid cells
- ✅ Display error messages for invalid moves

**Subsection Tests**:
- ✅ Click handler attached to empty cells only
- ✅ Clicking empty cell triggers makeMove() API call
- ✅ Board disabled (pointer-events: none) during AI turn
- ✅ Hover effect visible on valid (empty) cells
- ✅ Hover effect hidden on occupied cells
- ✅ Invalid move displays error message
- ✅ Error messages auto-dismiss after 5 seconds

**Test Coverage**:
- **Subsection Tests**: ~9 E2E/UI tests for Phase 8.1.2 incremental development
- **Acceptance Criteria**: AC-US002.1 through AC-US002.12 (12 official tests for final verification)

**8.1.3. View Last Move (US-003)** ✅
- ✅ Highlight last played cell
- ✅ Border color: highlight pink (#f72585)
- ✅ Glow effect per ui-spec.md

**Subsection Tests**:
- ✅ Last played cell highlighted with border color pink-500 (#f72585)
- ✅ Glow effect applied to last played cell
- ✅ Highlight moves to new cell when next move is made
- ✅ Highlight persists until game ends or reset

**Test Coverage**:
- **Subsection Tests**: ~4 E2E/UI tests for Phase 8.1.3 incremental development
- **Acceptance Criteria**: AC-US003.1 through AC-US003.2 (2 official tests for final verification)

**8.1.4. View Current Turn (US-004)** ✅
- ✅ Display whose turn (Player or AI)
- ✅ Status message updates for current turn
- ✅ Show move count

**Subsection Tests**:
- ✅ Turn indicator displays "Your turn" or "AI's turn" correctly
- ✅ Move count displayed and updates after each move
- ✅ Turn indicator updates when turn changes
- ✅ Turn indicator reflects correct player at game start

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 8.1.4 incremental development
- **Acceptance Criteria**: AC-US004.1 through AC-US004.8 (8 official tests for final verification)

**8.1.5. View Game Status (US-005)** ✅
- ✅ Display game over message
- ✅ Show winner (You win, AI wins, or Draw)
- ✅ Fade board when game ends

**Subsection Tests**:
- ✅ Game over message displayed when game ends
- ✅ Winner displayed correctly (You win, AI wins, or Draw)
- ✅ Board fades (opacity reduced) when game ends
- ✅ Game over message persists until reset
- ✅ Board interactions disabled when game over

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 8.1.5 incremental development
- **Acceptance Criteria**: AC-US005.1 through AC-US005.3 (3 official tests for final verification)

#### 8.2. Move History Panel

**Spec Reference**: US-006, US-007

**8.2.1. View Move History (US-006)**
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
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.2.1 incremental development
- **Acceptance Criteria**: AC-US006.1 through AC-US006.2 (2 official tests for final verification)

**8.2.2. View Move Details (US-007)**
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
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.2.2 incremental development
- **Acceptance Criteria**: AC-US007.1 through AC-US007.2 (2 official tests for final verification)

#### 8.3. Agent Insights Panel

**Spec Reference**: US-008, US-009, US-010, US-011, US-012

**8.3.1. View Agent Analysis (US-008)**
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
- **Subsection Tests**: ~7 E2E/UI tests for Phase 8.3.1 incremental development
- **Acceptance Criteria**: AC-US008.1 through AC-US008.11 (11 official tests for final verification)

**8.3.2. Processing Status (US-009, US-010)**
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
- **Subsection Tests**: ~7 E2E/UI tests for Phase 8.3.2 incremental development
- **Acceptance Criteria**: AC-US009.1 through AC-US010.1e (9 official tests for final verification)

**8.3.3. Force Fallback and Retry (US-011, US-012)**
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
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.3.3 incremental development
- **Acceptance Criteria**: AC-US011.1 through AC-US012.2 (5 official tests for final verification)

#### 8.4. Post-Game Metrics

**Spec Reference**: US-013, US-014, US-015, US-016, US-017, US-018

**8.4.1. Metrics Tab (US-013)**
- Only visible after game ends
- Tabbed interface: Summary | Performance | LLM | Communication

**Subsection Tests**:
- Metrics tab only visible after game ends (hidden during active game)
- Tabbed interface displays: Summary, Performance, LLM, Communication tabs
- Each tab displays correct content when selected
- Tab switching works correctly
- Metrics tab hidden on game reset until next game ends

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 8.4.1 incremental development
- **Acceptance Criteria**: AC-US013.1 through AC-US013.2 (2 official tests for final verification)

**8.4.2. Agent Communication (US-014)**
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
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.4.2 incremental development
- **Acceptance Criteria**: AC-US014.1 through AC-US014.3 (3 official tests for final verification)

**8.4.3. LLM Interactions (US-015)**
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
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.4.3 incremental development
- **Acceptance Criteria**: AC-US015.1 through AC-US015.6 (6 official tests for final verification)

**8.4.4. Agent Configuration (US-016)**
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
- **Subsection Tests**: ~5 E2E/UI tests for Phase 8.4.4 incremental development
- **Acceptance Criteria**: AC-US016.1 through AC-US016.4 (4 official tests for final verification)

**8.4.5. Performance Summary (US-017)**
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
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.4.5 incremental development
- **Acceptance Criteria**: AC-US017.1 through AC-US017.5 (5 official tests for final verification)

**8.4.6. Game Summary (US-018)**
- Total moves, duration, outcome
- Average move time

**Subsection Tests**:
- Game Summary tab shows total moves count
- Game duration displayed (start time to end time)
- Game outcome displayed (X wins, O wins, DRAW)
- Average move time calculated and displayed correctly
- Summary data matches actual game play

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 8.4.6 incremental development
- **Acceptance Criteria**: AC-US018.1 through AC-US018.4 (4 official tests for final verification)

#### 8.5. Configuration Panel

**Spec Reference**: US-019, US-020, US-021

**Figma Reference**: Config (node-id: 1:2239)

**8.5.1. Agent LLM Selection (US-019)**
- Three shadcn Select dropdowns for Scout, Strategist, Executor
- Each Select assigns an LLM provider to an agent
- Options: OpenAI, Anthropic, Gemini (per available providers)

**Subsection Tests**:
- Three Select components render for Scout, Strategist, Executor
- Each Select uses shadcn Select component (ui.shadcn.com/docs/components/select)
- Select dropdowns include OpenAI, Anthropic, Gemini options
- Labels display agent name (Scout, Strategist, Executor) above each Select
- Selection saved to localStorage on change
- Selection loaded from localStorage on page load

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.5.1 incremental development
- **Acceptance Criteria**: AC-US019.1 through AC-US019.3 (3 official tests for final verification)

**8.5.2. API Key Inputs (US-019, US-020)**
- Three shadcn Input fields for API keys (OpenAI, Anthropic, Gemini)
- Each input shows provider name and model name as label
- Model names: GPT-5 mini (OpenAI), Claude Opus 4.5 (Anthropic), Gemini 3 Flash (Gemini)

**Subsection Tests**:
- Three Input components render for OpenAI, Anthropic, Gemini API keys
- Each Input uses shadcn Input component (ui.shadcn.com/docs/components/input)
- Labels show provider name (bold) + model name (muted)
- Placeholder text shows "{Provider} Key"
- API keys saved securely to localStorage on blur
- API keys loaded from localStorage on page load
- Keys masked/hidden for security

**Test Coverage**:
- **Subsection Tests**: ~5 E2E/UI tests for Phase 8.5.2 incremental development
- **Acceptance Criteria**: AC-US020.1 through AC-US020.2 (2 official tests for final verification)

**8.5.3. Game Settings (US-021)**
- "New Game" button on Board tab handles game reset
- Player symbol selection (optional, can be added as Select)

**Subsection Tests**:
- New Game button clears current game and starts new game
- New Game button uses shadcn Button component (secondary variant)
- Player symbol selection (if added) allows choosing X or O
- Settings saved to localStorage
- Settings persist across sessions

**Test Coverage**:
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.5.3 incremental development
- **Acceptance Criteria**: AC-US021.1 through AC-US021.3 (3 official tests for final verification)

#### 8.6. Error Handling UI

**Spec Reference**: US-024, US-025, Section 12 - Failure Matrix

**8.6.1. Display Error Messages (US-024)**
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
- **Subsection Tests**: ~6 E2E/UI tests for Phase 8.6.1 incremental development
- **Acceptance Criteria**: AC-US024.1 through AC-US024.4 (4 official tests for final verification)

**8.6.2. Fallback Indication (US-025)**
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
- **Subsection Tests**: ~5 E2E/UI tests for Phase 8.6.2 incremental development
- **Acceptance Criteria**: AC-US025.1 through AC-US025.3 (3 official tests for final verification)

**Phase 8 Deliverables:**
- Complete web UI with all 25 user stories implemented
- **shadcn/ui** component library integration (Tabs, Button, Select, Input)
- **Figma design compliance** - UI matches Figma specification (node-id: 2-510)
- Visual design matches ui-spec.md with zinc color palette and JetBrains Mono font
- Full game playable in browser with 640×640px container

**Spec References:**
- Section 6: Web UI Functional Requirements (all 25 user stories)
- docs/spec/ui-spec.md: Visual Design Specification

---

### Phase 9: Testing and Quality Assurance

**Duration**: 3-4 days

**Goal**: System-level testing, performance validation, and resilience testing across all layers

**Why Ninth**: While TDD has been used throughout all phases (unit and integration tests written alongside features), Phase 9 focuses on:
- **System-level testing**: End-to-end scenarios that span multiple components
- **Non-functional requirements**: Performance, resilience, and scalability testing
- **Cross-cutting concerns**: Tests that require the full system to be implemented
- **Coverage audit**: Final review to ensure all acceptance criteria are covered and no gaps exist

**Note**: This phase does NOT replace TDD from previous phases. Instead, it adds system-level and non-functional testing that can only be done after all features are implemented.

**Spec Reference**: Section 11 - Testing Strategy

#### 9.0. Coverage Audit and Gap Analysis

**Target**: 100% coverage for domain models and game engine, 80%+ overall

**Purpose**: While TDD ensured tests were written during development, this phase audits coverage to identify any gaps or edge cases missed during feature implementation.

**Tasks:**
- Review all unit tests from Phases 1-8
- Generate comprehensive coverage report: `pytest --cov=src --cov-report=html`
- Identify coverage gaps (if any)
- Fill any missing edge cases or error paths
- Verify all acceptance criteria have corresponding tests
- Document coverage metrics

**Deliverable**: Coverage report showing ≥80% overall, 100% for critical paths, with gap analysis

**Subsection Tests**:
- Coverage report generated with pytest --cov=src --cov-report=html
- Domain models have 100% test coverage (Position, Board, GameState, AgentResult, etc.)
- Game engine has 100% test coverage (GameEngine, win conditions, draw conditions, move validation)
- Overall code coverage ≥80%
- All acceptance criteria have corresponding unit tests
- Coverage gaps identified and filled
- Coverage report accessible in htmlcov/index.html

#### 9.1. System Integration Tests

**Purpose**: While integration tests were written during feature development (e.g., Phase 4 API tests), this phase adds **system-level integration tests** that verify the complete system working together end-to-end.

**Files to Create:**
- `tests/integration/test_full_pipeline.py`
- `tests/integration/test_api_integration.py`

**Test Scenarios:**
- Complete game flow: Player move → AI move → repeat until win/draw (full system)
- Agent pipeline with all three agents (Scout → Strategist → Executor) with real LLM integration
- API endpoints with real game engine, agents, and LLM providers
- Error handling across layers (API → Agent → Engine → LLM)
- Cross-component state consistency

**Subsection Tests**:
- test_full_pipeline.py tests complete game flow (player move → AI move → repeat until win/draw)
- test_full_pipeline.py tests agent pipeline with all three agents (Scout → Strategist → Executor)
- test_api_integration.py tests API endpoints with real game engine and agents
- test_api_integration.py tests error handling across layers (validation → agent → execution)
- Integration tests verify state transitions across components
- Integration tests verify data flow between API, game engine, and agents

#### 9.2. End-to-End Tests

**Purpose**: E2E tests verify complete user workflows from UI through API to agents. These require the full system (including UI from Phase 8) to be implemented.

**Files to Create:**
- `tests/e2e/test_game_scenarios.py`

**Test Scenarios:**
- Player wins scenario (complete game from UI to API to agents)
- AI wins scenario (complete game with AI making winning moves)
- Draw scenario (complete game ending in draw)
- Player makes invalid move (error handling from UI to API)
- Agent timeout triggers fallback (system behavior under timeout conditions)
- LLM provider failure (system behavior when LLM is unavailable)

**Subsection Tests**:
- E2E test: Player wins scenario (player makes winning moves, AI responds, game ends with player win)
- E2E test: AI wins scenario (AI makes winning moves, player responds, game ends with AI win)
- E2E test: Draw scenario (9 moves made, no winner, game ends in draw)
- E2E test: Player makes invalid move (out of bounds, occupied cell, game over) → error displayed
- E2E test: Agent timeout triggers fallback (simulate slow agent, verify fallback move executed)
- E2E test: LLM provider failure (simulate LLM error, verify fallback to rule-based logic)

#### 9.3. Performance Tests

**Purpose**: Performance tests validate non-functional requirements that can only be measured with the complete system running. These are separate from functional TDD tests.

**Spec Reference**: Section 15 - Performance Optimization

**Files to Create:**
- `tests/performance/test_agent_timeout.py`
- `tests/performance/test_api_latency.py`
- `tests/performance/test_ui_responsiveness.py`

**Requirements:**
- Agent pipeline completes within 15s (Section 3.6)
- UI updates within 100ms of state change (AC-US023.3)
- Agent status updates within 500ms (AC-US023.4)
- API response times meet SLA requirements
- System handles concurrent users without degradation

**Subsection Tests**:
- Performance test: Agent pipeline completes within 15s (measure end-to-end pipeline execution time)
- Performance test: UI updates within 100ms of state change (measure DOM update latency)
- Performance test: Agent status updates within 500ms (measure status update propagation)
- Performance test: Move validation completes within 10ms (measure validation latency)
- Performance test: API response time < 200ms for game status endpoint (measure API latency)

#### 9.4. Resilience Tests

**Purpose**: Resilience tests verify system behavior under failure conditions. While error handling was tested during TDD, these tests verify the system's ability to recover and continue operating under various failure scenarios.

**Spec Reference**: Section 12 - Error Handling and Resilience

**Test Scenarios:**
- Network timeout (system behavior when network is slow/unavailable)
- LLM API failure (fallback mechanisms when LLM providers fail)
- Invalid API responses (malformed data handling)
- Concurrent API requests (race conditions, state consistency)
- Agent crash and recovery (system continues when agents fail)
- Resource exhaustion (memory, CPU limits)

**Subsection Tests**:
- Resilience test: Network timeout (simulate network delay, verify timeout handling and fallback)
- Resilience test: LLM API failure (simulate 500 error, verify fallback to rule-based logic)
- Resilience test: Invalid API responses (simulate malformed JSON, verify error handling)
- Resilience test: Concurrent API requests (multiple simultaneous game requests, verify no state leakage)
- Resilience test: Agent crash and recovery (simulate agent failure, verify system continues with fallback)
- Resilience test: Rate limiting (simulate 429 error, verify retry with backoff)
- Resilience test: Invalid API key (simulate 401/403, verify fallback and error messaging)

**Phase 9 Deliverables:**
- 399 tests passing (one per acceptance criterion)
- ≥80% code coverage overall
- 100% coverage on domain models and game engine
- All performance requirements met
- Resilience scenarios validated

**Spec References:**
- Section 11: Testing Strategy
- Section 15: Performance Optimization
- Section 12: Error Handling and Resilience

---

### Phase 10: Configuration and Observability

**Duration**: 2-3 days

**Goal**: Production-ready configuration, logging, and metrics

#### 10.0. Configuration Management

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
- **Subsection Tests**: ~8 tests for Phase 10.0 incremental development
- **Acceptance Criteria**: Configuration Management (Section 9) - environment support, validation, hierarchy, error handling
- **Test Files**: `tests/unit/config/test_settings.py`, `tests/integration/test_config_loading.py`

#### 10.1. Logging

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
- **Subsection Tests**: ~10 tests for Phase 10.1 incremental development
- **Acceptance Criteria**: Logging (Section 17 - Log Format Specification) - JSON format, log levels, contextual logging, rotation, retention
- **Test Files**: `tests/unit/test_logging.py`, `tests/integration/test_logging_integration.py`

#### 10.2. Metrics

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
- **Subsection Tests**: ~11 tests for Phase 10.2 incremental development
- **Acceptance Criteria**: Metrics Collection (Section 17 - Metrics Format Specification) - agent metrics, game metrics, system metrics, export formats
- **Test Files**: `tests/unit/metrics/test_collector.py`, `tests/unit/metrics/test_exporter.py`, `tests/integration/test_metrics_api.py`

#### 10.3. Health Checks

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
- **Subsection Tests**: ~8 tests for Phase 10.3 incremental development
- **Acceptance Criteria**: Health Checks (Section 10 - Deployment Considerations) - liveness, readiness, deep health checks, response times
- **Test Files**: `tests/integration/test_health_checks.py`

**Phase 10 Deliverables:**
- Configuration system supporting multiple environments
- Structured logging with JSON format
- Comprehensive metrics collection
- Health check endpoints ready for orchestration
- Comprehensive test coverage for configuration, logging, metrics, and health checks

**Spec References:**
- Section 9: Configuration Management
- Section 17: Metrics and Observability

---

### Phase 11: Documentation

**Duration**: 1-2 days

**Goal**: Complete user and developer documentation

**Note**: Docker/Kubernetes deployment is now covered in Phase 6 (Cloud Native Deployment). This phase focuses on documentation only.

#### 11.0. Documentation

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

**Subsection Tests**:
- README.md exists and contains all required sections (overview, quick start, installation, usage, configuration, API examples)
- docs/API.md exists with complete API endpoint documentation and request/response examples
- docs/DEPLOYMENT.md exists with deployment instructions (references Phase 6 for Docker/Kubernetes)
- docs/DEVELOPMENT.md exists with developer setup guide (environment setup, running tests, contributing)
- docs/ARCHITECTURE.md exists with system architecture overview (component diagrams, data flow)
- All documentation files use consistent formatting and are up-to-date
- Code examples in documentation are tested and working

**Note**: Docker and Kubernetes deployment documentation is part of Phase 6 (Cloud Native Deployment).

**Phase 11 Deliverables:**
- Complete documentation (README, API docs, deployment guide references Phase 6)
- Developer setup guide
- Architecture documentation
- All documentation files updated and consistent

**Spec References:**
- Section 1: Project Overview and Requirements
- Section 6: Web UI Functional Requirements
- Section 11: Testing Strategy

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
- Will you implement MCP mode (Phase 7)?

**Spec Coverage:**
This implementation plan covers:
- ✅ All 399 acceptance criteria
- ✅ All 25 user stories
- ✅ All technical requirements (Sections 1-13)
- ✅ All recommended technologies (Section 14.1)
- ✅ Test-driven development approach (Section 11)

Good luck with your implementation! 🚀
