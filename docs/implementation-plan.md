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

### Phase 1: Domain Models (Foundation Layer)

**Duration**: 3-5 days

**Goal**: Implement all domain models with validation and testing, and enhance CI/CD pipeline

**Why First**: Domain models are the foundation - they're used by everything else. They have no dependencies and can be fully tested in isolation.

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

**1.2.1. AgentResult**
- Implement generic `AgentResult[T]` wrapper
- Add factory methods: `AgentResult.success()`, `AgentResult.error()`
- Track execution_time_ms, timestamp (ISO 8601), metadata
- Validate timestamp format, execution time ≥ 0
- Error codes: `E_MISSING_DATA`, `E_MISSING_ERROR_MESSAGE`, `E_INVALID_TIMESTAMP`

**Test Coverage**: AC-2.12.1 through AC-2.12.8 (8 acceptance criteria)

#### 1.3. Enhance CI/CD Pipeline

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

**Enhance Pre-commit Hooks**

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

**Enhanced Pre-commit Features:**
- ✅ All basic hooks from Phase 0 (black, ruff, file fixes) - **unchanged**
- ✅ **NEW**: Type checking with mypy (strict mode)
- ✅ **NEW**: Run tests before commit
- ✅ All checks can be skipped with `--no-verify` if needed

**Note**: Pre-commit hooks provide fast local feedback. CI/CD is the final quality gate and will catch issues even if pre-commit is skipped.

**Phase 1 Deliverables:**
- ✅ Enhanced CI/CD pipeline with coverage and type checking
- ✅ All domain models implemented with full validation
- ✅ 84 unit tests passing (100% coverage on domain layer)
- ✅ Type checking passes with mypy --strict
- ✅ Coverage reporting to Codecov
- ✅ No dependencies on other modules (pure domain logic)

**Spec References:**
- Section 2: Domain Model Design (complete)
- Section 2.1: Machine-Verifiable Schema Definitions

---

### Phase 2: Game Engine (Business Logic Layer)

**Duration**: 3-4 days

**Goal**: Implement game rules, win/draw detection, and move validation

**Why Second**: Game engine depends only on domain models. It implements pure business logic without agents or API concerns.

#### 2.0. Win Condition Detection

**Spec Reference**: Section 4.1 - Formal Game Rules - Win Conditions Enumeration

**Files to Create:**
- `src/engine/game_engine.py`
- `tests/unit/engine/test_win_conditions.py`

**Implementation:**
- Check all 8 winning lines (3 rows, 3 columns, 2 diagonals)
- Win detection MUST check all lines after each move
- Return winner symbol (X or O) or None

**Test Coverage**: AC-4.1.1.1 through AC-4.1.1.10 (10 acceptance criteria)

**Key Test Cases:**
- Row wins (3 tests)
- Column wins (3 tests)
- Diagonal wins (2 tests)
- No win conditions (2 tests)

#### 2.1. Draw Condition Detection

**Spec Reference**: Section 4.1 - Draw Conditions

**Files:**
- `src/engine/game_engine.py` (extend)
- `tests/unit/engine/test_draw_conditions.py`

**Implementation:**
- **Mandatory**: Complete draw (MoveCount=9, no winner)
- **Optional**: Inevitable draw (early detection when no winning moves remain)
- Implement inevitable draw algorithm from spec (simulate all remaining moves)

**Test Coverage**: AC-4.1.2.1 through AC-4.1.2.6 (6 acceptance criteria)

#### 2.2. Move Validation

**Spec Reference**: Section 4.1 - Illegal Move Conditions

**Files:**
- `src/engine/game_engine.py` (extend)
- `tests/unit/engine/test_move_validation.py`

**Implementation:**
- Validate position bounds (0-2)
- Check cell is empty
- Verify game is not over
- Validate player symbol (X or O)
- Check correct turn order
- Error codes: `E_MOVE_OUT_OF_BOUNDS`, `E_CELL_OCCUPIED`, `E_GAME_ALREADY_OVER`, `E_INVALID_PLAYER`, `E_INVALID_TURN`

**Test Coverage**: AC-4.1.3.1 through AC-4.1.3.10 (10 acceptance criteria)

#### 2.3. Turn Order and State Transitions

**Spec Reference**: Section 4.1 - Turn Order Rules, State Transitions

**Files:**
- `src/engine/game_engine.py` (extend)
- `tests/unit/engine/test_turn_order.py`

**Implementation:**
- Turn alternation: Player (even moves) → AI (odd moves)
- Move number increments after each move
- State transitions: IN_PROGRESS → WON or DRAW
- Immutable transitions (cannot restart without reset)

**Test Coverage**: AC-4.1.4.1 through AC-4.1.4.9 (9 acceptance criteria)

#### 2.4. State Validation

**Spec Reference**: Section 4.1 - State Validation Rules

**Files:**
- `src/engine/game_engine.py` (extend)
- `tests/unit/engine/test_state_validation.py`

**Implementation:**
- Validate board consistency (symbol counts)
- Verify move number matches board state
- Check at most one winner exists
- Validate game over state is terminal

**Test Coverage**: AC-4.1.5.1 through AC-4.1.5.10 (10 acceptance criteria)

#### 2.5. Game Engine Interface

**Spec Reference**: Section 4.1 - Game Engine Interface

**Files:**
- `src/engine/game_engine.py` (finalize)
- `tests/unit/engine/test_game_engine_interface.py`

**Implementation:**
- Public API: `make_move(position, player)`, `check_winner()`, `is_game_over()`, `reset()`
- Return standardized results (success/error with codes)
- Maintain immutable game state internally
- Provide `get_game_state()` for read-only access

**Test Coverage**: AC-4.1.6.1 through AC-4.1.6.13 (13 acceptance criteria)

**Phase 2 Deliverables:**
- ✅ Complete game engine with all rules implemented
- ✅ 58 unit tests passing (100% coverage on game engine)
- ✅ Game playable without AI (human vs human via engine directly)
- ✅ All edge cases handled (invalid moves, draw detection, etc.)

**Spec References:**
- Section 4.1: Game Engine Design (complete)
- Section 4: Game State Management

---

### Phase 3: Agent System (AI Layer)

**Duration**: 5-7 days

**Goal**: Implement Scout, Strategist, and Executor agents with fallback strategies

**Why Third**: Agents depend on domain models and game engine. Start with rule-based logic, add LLM integration later.

#### 3.0. Scout Agent (Board Analysis)

**Spec Reference**: Section 3 - Agent Responsibilities - Scout Agent

**Files to Create:**
- `src/agents/scout.py`
- `src/agents/base.py` (base agent interface)
- `tests/unit/agents/test_scout.py`

**Implementation Order:**

**3.0.1. Rule-Based Threat Detection**
- Scan all 8 lines for opponent two-in-a-row + one empty
- Return `Threat` objects with blocking positions
- No LLM needed for this (pure algorithmic)

**3.0.2. Rule-Based Opportunity Detection**
- Scan all 8 lines for AI two-in-a-row + one empty
- Return `Opportunity` objects with winning positions
- Confidence = 1.0 for immediate wins

**3.0.3. Strategic Position Analysis**
- Identify center position (1,1)
- Identify corner positions (0,0), (0,2), (2,0), (2,2)
- Identify edge positions (0,1), (1,0), (1,2), (2,1)
- Return `StrategicMove` list

**3.0.4. Game Phase Detection**
- Opening: move_number 0-2
- Midgame: move_number 3-6
- Endgame: move_number 7-9

**3.0.5. Board Evaluation Score**
- Calculate evaluation based on position control
- Range: -1.0 (opponent winning) to +1.0 (AI winning)
- Simple heuristic: count potential winning lines

**3.0.6. BoardAnalysis Assembly**
- Combine all analyses into `BoardAnalysis` object
- Return wrapped in `AgentResult.success()`
- Track execution time

**Test Coverage**: AC-3.1.1 through AC-3.1.10 (10 acceptance criteria)

**Note**: LLM integration for Scout will be added in Phase 5. For now, rule-based analysis is sufficient and allows agents to function without LLM dependency.

#### 3.1. Strategist Agent (Move Selection)

**Spec Reference**: Section 3 - Agent Responsibilities - Strategist Agent

**Files to Create:**
- `src/agents/strategist.py`
- `tests/unit/agents/test_strategist.py`

**Implementation:**

**3.1.1. Priority-Based Move Selection**
- Implement priority ordering per Section 3.5 - Move Priority System:
  1. IMMEDIATE_WIN (100) - Win on this move
  2. BLOCK_THREAT (90) - Block opponent win
  3. FORCE_WIN (80) - Create fork (two winning lines)
  4. PREVENT_FORK (70) - Block opponent fork
  5. CENTER_CONTROL (50) - Take center
  6. CORNER_CONTROL (40) - Take corner
  7. EDGE_PLAY (30) - Take edge
  8. RANDOM_VALID (10) - Any valid move

**3.1.2. Strategy Assembly**
- Convert `BoardAnalysis` into `Strategy`
- Select primary move (highest priority)
- Generate 2+ alternative moves (sorted by priority descending)
- Create game plan (string explanation)
- Assess risk level (low/medium/high)

**3.1.3. Confidence Scoring**
- Assign confidence values per priority level (spec Section 3.5)
- IMMEDIATE_WIN: confidence = 1.0
- BLOCK_THREAT: confidence = 0.95
- CENTER_CONTROL: confidence = 0.7
- etc.

**Test Coverage**: AC-3.2.1 through AC-3.2.8 (8 acceptance criteria)

#### 3.2. Executor Agent (Move Execution)

**Spec Reference**: Section 3 - Agent Responsibilities - Executor Agent

**Files to Create:**
- `src/agents/executor.py`
- `tests/unit/agents/test_executor.py`

**Implementation:**

**3.2.1. Move Validation**
- Validate recommended move from Strategist
- Check position is valid and empty
- Verify game is not over
- Collect validation errors if any

**3.2.2. Move Execution**
- Call game engine's `make_move()`
- Track execution time
- Return `MoveExecution` with success status
- Record actual priority used

**3.2.3. Fallback Handling**
- If primary move fails, try alternatives
- If all alternatives fail, select random valid move
- Always return a valid move or clear error

**Test Coverage**: AC-3.3.1 through AC-3.3.7 (7 acceptance criteria)

#### 3.3. Agent Pipeline Orchestration

**Spec Reference**: Section 3 - Agent Pipeline Flow

**Files to Create:**
- `src/agents/pipeline.py`
- `tests/integration/test_agent_pipeline.py`

**Implementation:**

**3.3.1. Pipeline Coordinator**
- Orchestrate Scout → Strategist → Executor flow
- Pass outputs between agents (typed domain models)
- Handle agent failures gracefully
- Implement timeout handling (Section 3.3)

**3.3.2. Timeout Configuration**
- Per-agent timeouts: Scout (5s), Strategist (3s), Executor (2s)
- Total pipeline timeout: 15s (Section 3.6)
- Trigger fallback after timeout

**3.3.3. Fallback Strategy**
- On Scout timeout: Use rule-based analysis only
- On Strategist timeout: Use simple priority selection
- On Executor timeout: Select random valid move
- Always produce a move within 15s (spec requirement)

**Test Coverage**: AC-3.6.1 through AC-3.6.41 (41 acceptance criteria)

**Phase 3 Deliverables:**
- ✅ All three agents implemented with rule-based logic
- ✅ Agent pipeline orchestrates Scout → Strategist → Executor
- ✅ 66 tests passing (10 Scout + 8 Strategist + 7 Executor + 41 Pipeline)
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

**4.0.1. FastAPI Application Setup**
- Create FastAPI app instance
- Configure CORS (Section 5)
- Set up exception handlers
- Configure logging middleware

**4.0.2. Request/Response Models**
- Implement Pydantic models per Section 5.3:
  - `MoveRequest` (row, col)
  - `MoveResponse` (updated state, AI move)
  - `GameStatusResponse` (complete game state)
  - `ErrorResponse` (error code, message, details)

#### 4.1. Health and Readiness Endpoints

**Spec Reference**: Section 5.2 - REST API Endpoints

**4.1.1. GET /health**
- Return basic health status
- Check if API is running
- No dependencies checked

**Test Coverage**: AC-5.1.1 through AC-5.1.4 (4 acceptance criteria)

**4.1.2. GET /ready**
- Check game engine is initialized
- Check agent system is ready
- Verify LLM providers are configured (optional in Phase 4)
- Return detailed readiness status

**Test Coverage**: AC-5.2.1 through AC-5.2.6 (6 acceptance criteria)

#### 4.2. Game Control Endpoints

**4.2.1. POST /api/game/new**
- Create new game session
- Initialize game engine
- Return game ID and initial state
- Optionally accept player symbol preference

**Test Coverage**: AC-5.3.1 through AC-5.3.3 (3 acceptance criteria)

**4.2.2. POST /api/game/move**
- Accept player move (row, col)
- Validate move via game engine
- Trigger AI agent pipeline
- Return updated game state + AI move
- Handle errors per Section 5.4

**Test Coverage**: AC-5.4.1 through AC-5.4.8 (8 acceptance criteria)

**4.2.3. GET /api/game/status**
- Return current game state
- Include board, move history, game over status
- Return agent insights (if available)

**Test Coverage**: AC-5.5.1 through AC-5.5.4 (4 acceptance criteria)

**4.2.4. POST /api/game/reset**
- Reset current game to initial state
- Clear move history
- Reinitialize agents

**Test Coverage**: AC-5.6.1 through AC-5.6.3 (3 acceptance criteria)

**4.2.5. GET /api/game/history**
- Return complete move history
- Include both player and AI moves
- Include timestamps and agent reasoning

**Test Coverage**: AC-5.7.1 through AC-5.7.3 (3 acceptance criteria)

#### 4.3. Agent Status Endpoints

**Spec Reference**: Section 5.2 - Agent Status Endpoints

**4.3.1. GET /api/agents/status**
- Return status of each agent (idle/running/success/failed)
- Include current processing agent
- Show elapsed time for current operation

**Test Coverage**: AC-5.8.1 through AC-5.8.5 (5 acceptance criteria)

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

**5.0.2. OpenAI Provider**
- Implement using `openai` SDK
- Support models: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
- Handle API errors and retries

**5.0.3. Anthropic Provider**
- Implement using `anthropic` SDK
- Support models: claude-3-5-sonnet, claude-3-opus, claude-3-haiku

**5.0.4. Google Gemini Provider**
- Implement using Google SDK
- Support models: gemini-1.5-pro, gemini-1.5-flash

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

**Test Coverage**: LLM Provider Abstraction (Section 16)
- Provider interface contract validation
- OpenAI provider implementation (model support, error handling, retries)
- Anthropic provider implementation (model support, error handling)
- Google Gemini provider implementation (model support, error handling)
- Pydantic AI structured output validation against domain models
- Error handling and retry logic
- Token usage and latency tracking

**Test Files**: `tests/unit/llm/test_providers.py`

#### 5.1. Agent LLM Integration with Pydantic AI

**Spec Reference**: Section 16.3 - LLM Usage Patterns, Section 19 (Pydantic AI framework)

**5.1.1. Scout LLM Enhancement (Pydantic AI)**
- Create Pydantic AI Agent with `BoardAnalysis` as response model
- Define prompt: "Analyze this Tic-Tac-Toe board..."
- Use Pydantic AI's structured output to automatically validate response against `BoardAnalysis` domain model
- Leverage Pydantic AI's built-in error handling and retry logic
- Fallback to rule-based if LLM fails/times out
- Update `src/agents/scout.py`

**5.1.2. Strategist LLM Enhancement (Pydantic AI)**
- Create Pydantic AI Agent with `Strategy` as response model
- Define prompt: "Given this analysis, recommend best move..."
- Use Pydantic AI's structured output to automatically validate response against `Strategy` domain model
- Leverage Pydantic AI's built-in error handling and retry logic
- Fallback to priority-based selection if LLM fails
- Update `src/agents/strategist.py`

**5.1.3. Executor (No LLM)**
- Executor remains rule-based (no LLM needed for validation/execution)
- Keeps execution fast and deterministic

**Test Coverage**: Agent LLM Integration (Section 16.3)
- Scout LLM enhancement (prompt engineering, response parsing, fallback)
- Strategist LLM enhancement (prompt engineering, response parsing, fallback)
- Executor remains rule-based (no LLM calls)
- Fallback to rule-based logic on LLM failure/timeout
- LLM response parsing into domain models (BoardAnalysis, Strategy)

**Test Files**: `tests/unit/agents/test_scout_llm.py`, `tests/unit/agents/test_strategist_llm.py`, `tests/integration/test_llm_fallback.py`

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

**Test Coverage**: LLM Configuration (Section 9, Section 16)
- Load provider from environment variables
- Support `.env` file for local development
- Configuration hierarchy (env vars > .env file > defaults)
- Runtime provider switching
- Model selection per provider (one model per provider constraint)
- API key validation and error handling

**Test Files**: `tests/unit/config/test_llm_config.py`

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

**Test Coverage**: LLM Metrics and Tracking (Section 12.1)
- LLM call tracking per agent (Scout, Strategist)
- Metadata recording (prompt, response, tokens, latency, model, provider)
- Game session metadata storage
- Post-game analysis data availability
- Metrics export format validation

**Test Files**: `tests/unit/metrics/test_llm_metrics.py`, `tests/integration/test_llm_tracking.py`

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

**6.0.2. API Client**
- Create JavaScript wrapper for REST API
- Methods: `makeMove()`, `getGameStatus()`, `resetGame()`
- Handle errors and display to user

#### 6.1. Game Board UI

**Spec Reference**: US-001, US-002, US-003, US-004, US-005 (Section 6)

**6.1.1. Display Game Board (US-001)**
- Render 3x3 grid with cells
- Cell dimensions: 100px × 100px
- Gap: 12px between cells
- Display X, O, or empty

**Test Coverage**: AC-US001.1 through AC-US001.3 (3 acceptance criteria)

**6.1.2. Make Player Move (US-002)**
- Click handler on empty cells
- Disable board during AI turn
- Show hover effects on valid cells
- Display error messages for invalid moves

**Test Coverage**: AC-US002.1 through AC-US002.12 (12 acceptance criteria)

**6.1.3. View Last Move (US-003)**
- Highlight last played cell
- Border color: highlight pink (#f72585)
- Glow effect per ui-spec.md

**Test Coverage**: AC-US003.1 through AC-US003.2 (2 acceptance criteria)

**6.1.4. View Current Turn (US-004)**
- Display whose turn (Player or AI)
- Color-code by player symbol
- Show move count

**Test Coverage**: AC-US004.1 through AC-US004.8 (8 acceptance criteria)

**6.1.5. View Game Status (US-005)**
- Display game over message
- Show winner (X, O, or DRAW)
- Fade board when game ends

**Test Coverage**: AC-US005.1 through AC-US005.3 (3 acceptance criteria)

#### 6.2. Move History Panel

**Spec Reference**: US-006, US-007

**6.2.1. View Move History (US-006)**
- Chronological list of all moves
- Show player/AI indicator, move number, position, timestamp
- Scrollable panel (max-height: 400px)

**Test Coverage**: AC-US006.1 through AC-US006.2 (2 acceptance criteria)

**6.2.2. View Move Details (US-007)**
- Expandable move entries
- Show agent reasoning (Scout analysis, Strategist strategy, Executor details)
- Collapse/expand animation

**Test Coverage**: AC-US007.1 through AC-US007.2 (2 acceptance criteria)

#### 6.3. Agent Insights Panel

**Spec Reference**: US-008, US-009, US-010, US-011, US-012

**6.3.1. View Agent Analysis (US-008)**
- Real-time agent status display
- Show threats, opportunities, recommended moves
- Three sections: Scout, Strategist, Executor

**Test Coverage**: AC-US008.1 through AC-US008.11 (11 acceptance criteria)

**6.3.2. Processing Status (US-009, US-010)**
- Loading indicators while agents think
- Progressive status updates:
  - 0-2s: Simple spinner
  - 2-5s: Processing message
  - 5-10s: Progress bar with elapsed time
  - 10-15s: Warning with fallback notice
  - 15s+: Automatic fallback

**Test Coverage**: AC-US009.1 through AC-US010.1e (9 acceptance criteria)

**6.3.3. Force Fallback and Retry (US-011, US-012)**
- "Force Fallback" button after 10s
- "Retry" button on agent failure
- Clear explanations of fallback strategy

**Test Coverage**: AC-US011.1 through AC-US012.2 (5 acceptance criteria)

#### 6.4. Post-Game Metrics

**Spec Reference**: US-013, US-014, US-015, US-016, US-017, US-018

**6.4.1. Metrics Tab (US-013)**
- Only visible after game ends
- Tabbed interface: Summary | Performance | LLM | Communication

**Test Coverage**: AC-US013.1 through AC-US013.2 (2 acceptance criteria)

**6.4.2. Agent Communication (US-014)**
- Show request/response data for each agent call
- Display JSON with syntax highlighting

**Test Coverage**: AC-US014.1 through AC-US014.3 (3 acceptance criteria)

**6.4.3. LLM Interactions (US-015)**
- Show prompts sent to LLM
- Show LLM responses
- Display token usage, latency, model/provider

**Test Coverage**: AC-US015.1 through AC-US015.6 (6 acceptance criteria)

**6.4.4. Agent Configuration (US-016)**
- Display agent mode (local vs MCP)
- Show LLM framework used
- Show initialization details

**Test Coverage**: AC-US016.1 through AC-US016.4 (4 acceptance criteria)

**6.4.5. Performance Summary (US-017)**
- Per-agent execution times (min, max, avg)
- Total LLM calls and tokens
- Success/failure rates

**Test Coverage**: AC-US017.1 through AC-US017.5 (5 acceptance criteria)

**6.4.6. Game Summary (US-018)**
- Total moves, duration, outcome
- Average move time

**Test Coverage**: AC-US018.1 through AC-US018.4 (4 acceptance criteria)

#### 6.5. Configuration Panel

**Spec Reference**: US-019, US-020, US-021

**6.5.1. LLM Provider Selection (US-019)**
- Dropdown for provider (OpenAI, Anthropic, Google)
- Model name input
- Save preferences to localStorage

**Test Coverage**: AC-US019.1 through AC-US019.3 (3 acceptance criteria)

**6.5.2. Agent Mode Selection (US-020)**
- Toggle: Local vs Distributed MCP
- LLM framework dropdown

**Test Coverage**: AC-US020.1 through AC-US020.2 (2 acceptance criteria)

**6.5.3. Game Settings (US-021)**
- Reset game button
- Player symbol selection (X or O)
- Difficulty slider (optional)

**Test Coverage**: AC-US021.1 through AC-US021.3 (3 acceptance criteria)

#### 6.6. Error Handling UI

**Spec Reference**: US-024, US-025, Section 12 - Failure Matrix

**6.6.1. Display Error Messages (US-024)**
- Critical errors: Red modal
- Warnings: Orange/yellow badges
- Info: Blue toasts (bottom-right)
- Cell-level errors: Shake animation + red highlight

**Test Coverage**: AC-US024.1 through AC-US024.4 (4 acceptance criteria)

**6.6.2. Fallback Indication (US-025)**
- Notify user when fallback is triggered
- Explain why fallback was needed
- Show which fallback strategy was used

**Test Coverage**: AC-US025.1 through AC-US025.3 (3 acceptance criteria)

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

#### 7.1. Integration Tests

**Files to Create:**
- `tests/integration/test_full_pipeline.py`
- `tests/integration/test_api_integration.py`

**Test Scenarios:**
- Complete game flow: Player move → AI move → repeat until win/draw
- Agent pipeline with all three agents
- API endpoints with real game engine and agents
- Error handling across layers

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

#### 7.3. Performance Tests

**Spec Reference**: Section 15 - Performance Optimization

**Files to Create:**
- `tests/performance/test_agent_timeout.py`

**Requirements:**
- Agent pipeline completes within 15s (Section 3.6)
- UI updates within 100ms of state change (AC-US023.3)
- Agent status updates within 500ms (AC-US023.4)

#### 7.4. Resilience Tests

**Spec Reference**: Section 12 - Error Handling and Resilience

**Test Scenarios:**
- Network timeout
- LLM API failure
- Invalid API responses
- Concurrent API requests
- Agent crash and recovery

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

**Test Coverage**: Configuration Management (Section 9)
- Environment-based configuration (dev, staging, prod)
- Configuration validation on startup
- Environment variables support
- Config file support (YAML/JSON)
- Configuration hierarchy (env vars > config file > defaults)
- Hot-reload for non-critical settings
- Configuration error handling

**Test Files**: `tests/unit/config/test_settings.py`, `tests/integration/test_config_loading.py`

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

**Test Coverage**: Logging (Section 17 - Log Format Specification)
- Structured logging (JSON format validation)
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Contextual logging (request ID, game ID, agent ID)
- Log rotation and retention
- Log event types (API requests/responses, agent execution, LLM calls, errors, state transitions)
- Log format compliance (timestamp, level, message, context)

**Test Files**: `tests/unit/test_logging.py`, `tests/integration/test_logging_integration.py`

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

**Test Coverage**: Metrics Collection (Section 17 - Metrics Format Specification)
- Agent metrics collection (execution time, success/failure rates, timeout counts, fallback usage)
- Game metrics collection (total games, win/loss/draw counts, average duration, moves per game)
- System metrics collection (API request rate, response times, error rates, LLM token usage)
- Metrics export formats (JSON API endpoint validation)
- Metrics aggregation (min, max, avg, p95, p99)
- Metrics format compliance

**Test Files**: `tests/unit/metrics/test_collector.py`, `tests/unit/metrics/test_exporter.py`, `tests/integration/test_metrics_api.py`

#### 8.3. Health Checks

**Implementation:**
- Liveness probe: `/health` (already implemented in Phase 4)
- Readiness probe: `/ready` (already implemented in Phase 4)
- Deep health check: `/health/deep` (check all dependencies)

**Test Coverage**: Health Checks (Section 10 - Deployment Considerations)
- Liveness probe (`/health`) response format and status codes
- Readiness probe (`/ready`) dependency checking
- Deep health check (`/health/deep`) all dependencies validation
- Health check error scenarios
- Health check response time requirements

**Test Files**: `tests/integration/test_health_checks.py`

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
