# Tic-Tac-Toe Multi-Agent Game Specification

## Document Structure

This specification is organized into two parts:

**Part I: Core Specification (Sections 1-13)** - Normative requirements defining **what** the system must do. These are framework-agnostic functional requirements that serve as a long-lived contract.

**Part II: Implementation Guidance (Sections 14-20)** - Non-normative guidance on **how** to implement the system. These recommendations may evolve as technologies change.

---

# PART I: CORE SPECIFICATION (NORMATIVE)

## 1. System Overview

### Purpose
A Tic-Tac-Toe game between a human player and an AI opponent. The AI uses three specialized agents (Scout, Strategist, Executor) to make moves. The application is built API-first, with all communication API-driven. Players interact via a web-based UI that communicates with the backend through the API layer. The system supports both local execution and distributed coordination.

### Core Requirements

**Functional Requirements:**
- **Game Rules**: Standard Tic-Tac-Toe rules (3x3 grid, three in a row to win, draw detection)
- **Multi-Agent AI**: Three specialized agents collaborate to make moves (Scout → Strategist → Executor)
- **API-First Design**: All operations exposed via API; UI is a client
- **Move Validation**: All moves validated for bounds, cell availability, and game rules
- **State Management**: Game state tracked and persisted throughout gameplay
- **Error Handling**: Graceful degradation when agents or services fail

**Non-Functional Requirements:**
- **Type Safety**: Strongly-typed domain models with validation
- **Statelessness**: Agents are stateless; all context provided via inputs
- **Observability**: Metrics, logging, and monitoring for all operations
- **Configuration**: Behavior controlled through configuration, not code
- **Extensibility**: Well-defined interfaces for adding features or agents
- **Performance**: Agent pipeline completes within 15 seconds per move
- **Resilience**: System continues operating despite individual component failures

### Design Principles

**Architectural Foundations:**
- **API-First Design**: All communication is API-driven; UI and other clients communicate exclusively through the API layer
- **Domain-Driven Design**: Clear domain models separate from infrastructure
- **Separation of Concerns**: Game logic, agent logic, and UI are independent
- **Clean Interfaces**: Agents communicate via domain models, not raw data structures
- **Transport Abstraction**: Communication protocols are abstracted from business logic

**Implementation Standards:**
- **Testability**: All requirements MUST be specified using Given-When-Then acceptance criteria format, enabling direct mapping to automated tests. Each criterion MUST specify exact inputs, actions, and measurable expected outcomes.
- **DRY (Don't Repeat Yourself)**: Code reuse through shared utilities, common patterns, and well-defined interfaces
- **Convention over Configuration (CoC)**: Sensible defaults reduce configuration burden; explicit configuration only when defaults are insufficient

**Operational Principles:**
- **Configuration over Code**: Behavior controlled through config files, environment variables, and command-line arguments
- **Hot-swappability**: LLM providers and models can be changed via configuration without code changes
- **Mode Interchangeability**: Agents can switch between local and distributed modes at runtime
- **Graceful Degradation**: System continues operating with fallback strategies when components fail

### Non-Goals

This section explicitly defines what is **out of scope** for this project to prevent scope creep and maintain focus:

**Game Variants:**
- ❌ Different board sizes (4x4, 5x5, etc.)
- ❌ Alternative game rules (Connect Four, Gomoku, etc.)
- ❌ 3D Tic-Tac-Toe or other variants
- ❌ Multiple simultaneous games

**Multiplayer Features:**
- ❌ Human vs Human mode
- ❌ AI vs AI tournaments (except for experimentation/testing)
- ❌ Multiplayer lobbies or matchmaking
- ❌ Real-time spectator mode
- ❌ Chat or social features

**User Management:**
- ❌ User authentication and accounts
- ❌ User profiles and avatars
- ❌ Friend lists or social connections
- ❌ Leaderboards or rankings
- ❌ Achievement systems

**Advanced AI Features:**
- ❌ Machine learning model training (use pre-trained LLMs only)
- ❌ Reinforcement learning or self-play
- ❌ Neural network visualization
- ❌ AI difficulty levels (agents always play optimally)
- ❌ Personalized AI behavior based on player patterns

**Mobile & Desktop Apps:**
- ❌ Native mobile applications (iOS/Android)
- ❌ Desktop applications (Electron, etc.)
- ❌ Mobile-optimized responsive design (web UI is desktop-first)
- ❌ Offline play capability

**Enterprise Features:**
- ❌ Multi-tenancy support
- ❌ Role-based access control (RBAC)
- ❌ Audit logging for compliance
- ❌ SLA guarantees or uptime requirements
- ❌ High availability / disaster recovery

**Monetization:**
- ❌ Payment processing
- ❌ Subscription models
- ❌ In-app purchases
- ❌ Advertising integration

**Internationalization:**
- ❌ Multi-language support (English only)
- ❌ Localization for different regions
- ❌ Right-to-left (RTL) language support

**Advanced Analytics:**
- ❌ Real-time analytics dashboards
- ❌ Predictive analytics or forecasting
- ❌ Business intelligence integrations
- ❌ Data warehouse integration (beyond basic export)

**Scope Boundaries:**

While the system supports experimentation and metrics tracking, the focus is on:
- ✅ Single-player human vs AI gameplay
- ✅ Standard 3x3 Tic-Tac-Toe rules only
- ✅ Web-based UI for desktop browsers
- ✅ Demonstrating multi-agent LLM coordination
- ✅ Basic experiment tracking for cost/performance optimization
- ✅ API-first architecture for extensibility

**Future Consideration:**

Features marked as non-goals may be reconsidered in future versions if there is clear demand and they align with the project's educational and demonstration purposes. However, they are explicitly out of scope for the initial release.

---

## 2. Domain Model Design

### Core Game Entities

**Position**: Represents a board cell with row and column (0-2). Immutable and hashable.

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `row` | integer | 0 ≤ row ≤ 2 | `E_POSITION_OUT_OF_BOUNDS` | Given row=3 or row=-1, when Position created, then reject with E_POSITION_OUT_OF_BOUNDS |
| `col` | integer | 0 ≤ col ≤ 2 | `E_POSITION_OUT_OF_BOUNDS` | Given col=3 or col=-1, when Position created, then reject with E_POSITION_OUT_OF_BOUNDS |

**Acceptance Criteria:**
- Given row=0, col=0, when Position is created, then position is valid
- Given row=3, col=0, when Position is created, then validation error `ERR_POSITION_OUT_OF_BOUNDS` is raised
- Given row=-1, col=0, when Position is created, then validation error `ERR_POSITION_OUT_OF_BOUNDS` is raised
- Given Position(row=1, col=2), when hashed, then produces consistent hash value for use in dictionaries/sets
- Given Position(row=1, col=2) and Position(row=1, col=2), when compared, then positions are equal

**Board**: A 3x3 grid of symbols (X, O, or empty). Board MUST provide methods: `get_cell(position)` returns symbol at position, `set_cell(position, symbol)` sets symbol at position, `is_empty(position)` returns boolean, `get_empty_positions()` returns list of Position objects. Board MUST validate size is exactly 3x3.

**Acceptance Criteria:**
- Given a 3x3 board structure, when Board is created, then board is valid
- Given a 2x2 board structure, when Board is created, then validation error `ERR_INVALID_BOARD_SIZE` is raised
- Given a 4x4 board structure, when Board is created, then validation error `ERR_INVALID_BOARD_SIZE` is raised
- Given Board with empty cells, when `get_empty_positions()` is called, then returns list of all (row, col) tuples where cell is empty
- Given Board with all cells occupied, when `get_empty_positions()` is called, then returns empty list
- Given Position(1, 1) and symbol 'X', when `set_cell(position, 'X')` is called, then cell at (1, 1) contains 'X'
- Given Position(1, 1), when `get_cell(position)` is called, then returns current symbol ('X', 'O', or EMPTY)
- Given Position(3, 3), when `get_cell(position)` is called, then raises error `ERR_POSITION_OUT_OF_BOUNDS`
- Given Position(1, 1) with no symbol set, when `is_empty(position)` is called, then returns True
- Given Position(1, 1) with 'X' set, when `is_empty(position)` is called, then returns False

**Game State**: Complete game state including:
- Current board
- Current player (player or AI)
- Move number
- Player and AI symbols
- Game over status
- Winner (if any)
- Draw status

GameState MUST provide helper methods: `get_current_player()` returns player symbol (X or O) based on move_number (even=player, odd=AI), `get_opponent()` returns the opposite symbol.

**Acceptance Criteria:**
- Given valid Board, player='X', AI='O', when GameState is created, then game state is valid with move_number=0
- Given GameState with move_number=0, when `get_current_player()` is called, then returns player symbol 'X'
- Given GameState with move_number=1, when `get_current_player()` is called, then returns AI symbol 'O'
- Given GameState with three X's in a row, when game state is evaluated, then `is_game_over=True` and `winner='X'`
- Given GameState with three O's in a column, when game state is evaluated, then `is_game_over=True` and `winner='O'`
- Given GameState with three X's on diagonal, when game state is evaluated, then `is_game_over=True` and `winner='X'`
- Given GameState with all 9 cells occupied and no winner, when game state is evaluated, then `is_game_over=True` and `is_draw=True`
- Given GameState with 5 moves and no winner, when game state is evaluated, then `is_game_over=False`
- Given GameState with player='X', when `get_opponent()` is called, then returns 'O'
- Given invalid board (size ≠ 3x3), when GameState is created, then validation error `ERR_INVALID_BOARD_SIZE` is raised

### Agent Domain Models

**Threat**: Represents an immediate threat where the opponent will win on next move if not blocked. Threat MUST contain: position (Position object), line_type (string: 'row', 'column', or 'diagonal'), line_index (integer 0-2), severity (string: always 'critical' for Tic-Tac-Toe).

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `position` | Position | Position.row in [0,2], Position.col in [0,2] | `E_POSITION_OUT_OF_BOUNDS` | Given position with row=3 or col=3, when Threat created, then reject with E_POSITION_OUT_OF_BOUNDS |
| `line_type` | string | Must be one of: 'row', 'column', 'diagonal' | `E_INVALID_LINE_TYPE` | Given line_type='invalid', when Threat created, then reject with E_INVALID_LINE_TYPE |
| `line_index` | integer | 0 ≤ line_index ≤ 2 | `E_INVALID_LINE_INDEX` | Given line_index=3 or line_index=-1, when Threat created, then reject with E_INVALID_LINE_INDEX |
| `severity` | string | Must be 'critical' | N/A | Always 'critical' for Tic-Tac-Toe (no validation needed) |

**Acceptance Criteria:**
- Given opponent has two O's in row 0 with position (0,2) empty, when Threat is created, then `position=(0,2)`, `line_type='row'`, `line_index=0`, `severity='critical'`
- Given opponent has two O's in column 1, when Threat is created, then `line_type='column'` and `line_index=1`
- Given opponent has two O's on main diagonal, when Threat is created, then `line_type='diagonal'` and `line_index=0`
- Given threat with invalid position (3, 3), when Threat is created, then validation error `ERR_POSITION_OUT_OF_BOUNDS` is raised

**Opportunity**: Represents a winning opportunity where AI can win on this move. Opportunity MUST contain: position (Position object), line_type (string: 'row', 'column', or 'diagonal'), line_index (integer 0-2), confidence (float 0.0 to 1.0).

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `position` | Position | Position.row in [0,2], Position.col in [0,2] | `E_POSITION_OUT_OF_BOUNDS` | Given position with row=3 or col=3, when Opportunity created, then reject with E_POSITION_OUT_OF_BOUNDS |
| `line_type` | string | Must be one of: 'row', 'column', 'diagonal' | `E_INVALID_LINE_TYPE` | Given line_type='invalid', when Opportunity created, then reject with E_INVALID_LINE_TYPE |
| `line_index` | integer | 0 ≤ line_index ≤ 2 | `E_INVALID_LINE_INDEX` | Given line_index=3 or line_index=-1, when Opportunity created, then reject with E_INVALID_LINE_INDEX |
| `confidence` | float | 0.0 ≤ confidence ≤ 1.0, precision: 2 decimal places | `E_INVALID_CONFIDENCE` | Given confidence=1.5 or confidence=-0.1, when Opportunity created, then reject with E_INVALID_CONFIDENCE |

**Acceptance Criteria:**
- Given AI has two X's in row 1 with position (1,2) empty, when Opportunity is created, then `position=(1,2)`, `line_type='row'`, `line_index=1`, `confidence=1.0`
- Given AI has one X in center with corners available, when Opportunity is created for fork, then `confidence >= 0.7`
- Given confidence value 1.5, when Opportunity is created, then validation error `ERR_INVALID_CONFIDENCE` is raised (must be 0.0-1.0)
- Given confidence value -0.1, when Opportunity is created, then validation error `ERR_INVALID_CONFIDENCE` is raised

**Strategic Move**: A position recommendation with position, move type (center/corner/edge/fork/block_fork), priority (1-10 numeric value), and reasoning (required string explanation).

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `position` | Position | Position.row in [0,2], Position.col in [0,2] | `E_POSITION_OUT_OF_BOUNDS` | Given position with row=3 or col=3, when StrategicMove created, then reject with E_POSITION_OUT_OF_BOUNDS |
| `move_type` | string | Must be one of: 'center', 'corner', 'edge', 'fork', 'block_fork' | `E_INVALID_MOVE_TYPE` | Given move_type='invalid', when StrategicMove created, then reject with E_INVALID_MOVE_TYPE |
| `priority` | integer | 1 ≤ priority ≤ 10 | `E_INVALID_PRIORITY` | Given priority=11 or priority=0, when StrategicMove created, then reject with E_INVALID_PRIORITY |
| `reasoning` | string | Required, non-empty (length > 0), max length 1000 characters | `E_MISSING_REASONING` | Given reasoning='' or reasoning=null, when StrategicMove created, then reject with E_MISSING_REASONING |

**Acceptance Criteria:**
- Given empty board, when StrategicMove for center is created, then `position=(1,1)`, `move_type='center'`, `priority >= 8`
- Given move_type='corner', when StrategicMove is created, then position is one of: (0,0), (0,2), (2,0), (2,2)
- Given move_type='edge', when StrategicMove is created, then position is one of: (0,1), (1,0), (1,2), (2,1)
- Given priority value 11, when StrategicMove is created, then validation error `ERR_INVALID_PRIORITY` is raised (must be 1-10)
- Given priority value 0, when StrategicMove is created, then validation error `ERR_INVALID_PRIORITY` is raised

**Board Analysis**: Scout agent output containing:
- List of threats
- List of opportunities
- List of strategic moves
- Human-readable analysis
- Game phase (opening/midgame/endgame)
- Board evaluation score (-1.0 to 1.0)

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `threats` | list[Threat] | List of Threat objects, may be empty | N/A | List validation (each Threat must pass Threat constraints) |
| `opportunities` | list[Opportunity] | List of Opportunity objects, may be empty | N/A | List validation (each Opportunity must pass Opportunity constraints) |
| `strategic_moves` | list[StrategicMove] | List of StrategicMove objects, may be empty | N/A | List validation (each StrategicMove must pass StrategicMove constraints) |
| `game_phase` | string | Must be one of: 'opening', 'midgame', 'endgame' | `E_INVALID_GAME_PHASE` | Given game_phase='invalid', when BoardAnalysis created, then reject with E_INVALID_GAME_PHASE |
| `board_evaluation_score` | float | -1.0 ≤ board_evaluation_score ≤ 1.0, precision: 2 decimal places | `E_INVALID_EVAL_SCORE` | Given board_evaluation_score=1.5 or board_evaluation_score=-1.5, when BoardAnalysis created, then reject with E_INVALID_EVAL_SCORE |

**Acceptance Criteria:**
- Given board with opponent about to win, when BoardAnalysis is created, then `threats` list contains at least one Threat
- Given board with AI about to win, when BoardAnalysis is created, then `opportunities` list contains at least one Opportunity with winning position
- Given empty board (move 0-2), when BoardAnalysis is created, then `game_phase='opening'`
- Given board with 3-6 moves, when BoardAnalysis is created, then `game_phase='midgame'`
- Given board with 7-9 moves, when BoardAnalysis is created, then `game_phase='endgame'`
- Given board evaluation score 1.5, when BoardAnalysis is created, then validation error `ERR_INVALID_EVAL_SCORE` is raised (must be -1.0 to 1.0)
- Given favorable board for AI, when BoardAnalysis is created, then `board_evaluation_score > 0.0`
- Given favorable board for opponent, when BoardAnalysis is created, then `board_evaluation_score < 0.0`
- Given balanced board, when BoardAnalysis is created, then `board_evaluation_score ≈ 0.0` (within ±0.2)

**Move Priority**: Enum defining priority levels for move recommendations with numeric values (see Priority System below for details):
- IMMEDIATE_WIN (priority: 100) - AI has exactly 2 symbols in a line with exactly 1 empty cell (will win on this move)
- BLOCK_THREAT (priority: 90) - Opponent has exactly 2 symbols in a line with exactly 1 empty cell (must block to prevent opponent win)
- FORCE_WIN (priority: 80) - Move creates exactly 2 unblocked lines each containing 2 AI symbols (fork that guarantees eventual win)
- PREVENT_FORK (priority: 70) - Move blocks opponent from creating exactly 2 unblocked lines each containing 2 opponent symbols (prevents opponent fork)
- CENTER_CONTROL (priority: 50) - Take center position (1,1) when available and no moves with priority >50 exist
- CORNER_CONTROL (priority: 40) - Take corner position (0,0/0,2/2,0/2,2) when available and no moves with priority >40 exist
- EDGE_PLAY (priority: 30) - Take edge position (0,1/1,0/1,2/2,1) when available and no moves with priority >30 exist
- RANDOM_VALID (priority: 10) - Any valid empty cell when no strategic patterns detected (fallback)

**Acceptance Criteria:**
- Given MovePriority.IMMEDIATE_WIN, when accessed, then numeric value equals 100
- Given MovePriority.BLOCK_THREAT, when accessed, then numeric value equals 90
- Given MovePriority.FORCE_WIN, when accessed, then numeric value equals 80
- Given MovePriority.PREVENT_FORK, when accessed, then numeric value equals 70
- Given MovePriority.CENTER_CONTROL, when accessed, then numeric value equals 50
- Given MovePriority.CORNER_CONTROL, when accessed, then numeric value equals 40
- Given MovePriority.EDGE_PLAY, when accessed, then numeric value equals 30
- Given MovePriority.RANDOM_VALID, when accessed, then numeric value equals 10
- Given two moves with IMMEDIATE_WIN (100) and BLOCK_THREAT (90), when comparing priorities, then IMMEDIATE_WIN > BLOCK_THREAT

**Move Recommendation**: Strategist output with position (required Position), priority (required MovePriority enum), confidence (required 0.0-1.0), reasoning (required string), and outcome_description (optional string describing what this move achieves).

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `position` | Position | Required, Position.row in [0,2], Position.col in [0,2] | `E_POSITION_OUT_OF_BOUNDS` | Given position with row=3 or col=3, when MoveRecommendation created, then reject with E_POSITION_OUT_OF_BOUNDS |
| `priority` | MovePriority enum | Required, must be valid MovePriority enum value | `E_INVALID_PRIORITY` | Given priority=invalid_enum_value, when MoveRecommendation created, then reject with E_INVALID_PRIORITY |
| `confidence` | float | Required, 0.0 ≤ confidence ≤ 1.0, precision: 2 decimal places | `E_INVALID_CONFIDENCE` | Given confidence=1.5 or confidence=-0.1, when MoveRecommendation created, then reject with E_INVALID_CONFIDENCE |
| `reasoning` | string | Required, non-empty (length > 0), max length 1000 characters | `E_MISSING_REASONING` | Given reasoning='' or reasoning=null, when MoveRecommendation created, then reject with E_MISSING_REASONING |
| `outcome_description` | string | Optional, if present: max length 500 characters | N/A | Optional field (no validation if absent) |

**Acceptance Criteria:**
- Given position (1,1), priority IMMEDIATE_WIN, confidence 1.0, when MoveRecommendation is created, then recommendation is valid
- Given confidence value 1.5, when MoveRecommendation is created, then validation error `ERR_INVALID_CONFIDENCE` is raised (must be 0.0-1.0)
- Given confidence value -0.1, when MoveRecommendation is created, then validation error `ERR_INVALID_CONFIDENCE` is raised
- Given invalid position (3,3), when MoveRecommendation is created, then validation error `ERR_POSITION_OUT_OF_BOUNDS` is raised
- Given priority IMMEDIATE_WIN and empty reasoning, when MoveRecommendation is created, then validation error `ERR_MISSING_REASONING` is raised
- Given high-priority move (IMMEDIATE_WIN), when comparing with low-priority move (EDGE_PLAY), then high-priority move ranks higher

**Strategy**: Strategist output containing:
- Primary move recommendation (highest priority)
- Alternative move recommendations (sorted by priority descending)
- Overall game plan
- Risk assessment (low/medium/high)

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `primary_move` | MoveRecommendation | Required, must pass MoveRecommendation constraints | `E_MISSING_PRIMARY_MOVE` | Given primary_move=null or primary_move missing, when Strategy created, then reject with E_MISSING_PRIMARY_MOVE |
| `alternatives` | list[MoveRecommendation] | Optional, if present: list sorted by priority descending, each must pass MoveRecommendation constraints | N/A | List validation (each MoveRecommendation must pass MoveRecommendation constraints) |
| `game_plan` | string | Required, non-empty (length > 0), max length 2000 characters | `E_MISSING_GAME_PLAN` | Given game_plan='' or game_plan=null, when Strategy created, then reject with E_MISSING_GAME_PLAN |
| `risk_assessment` | string | Required, must be one of: 'low', 'medium', 'high' | `E_INVALID_RISK_LEVEL` | Given risk_assessment='invalid', when Strategy created, then reject with E_INVALID_RISK_LEVEL |

**Acceptance Criteria:**
- Given multiple move recommendations, when Strategy is created, then primary_move has highest priority among all recommendations
- Given alternatives with priorities [80, 50, 40], when Strategy is created, then alternatives list is sorted [80, 50, 40] (descending)
- Given alternatives with priorities [40, 80, 50], when Strategy is created, then alternatives list is sorted [80, 50, 40] (descending)
- Given risk_assessment='low', when Strategy is created, then risk_assessment is 'low'
- Given risk_assessment='invalid', when Strategy is created, then validation error `ERR_INVALID_RISK_LEVEL` is raised (must be low/medium/high)
- Given empty alternatives list and primary move, when Strategy is created, then strategy is valid (alternatives optional)
- Given no primary move, when Strategy is created, then validation error `ERR_MISSING_PRIMARY_MOVE` is raised

**Move Execution**: Executor output with position, success status, validation errors, execution time, reasoning, and actual priority used.

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `position` | Position | Required if success=True, Position.row in [0,2], Position.col in [0,2] | `E_POSITION_OUT_OF_BOUNDS` | Given position with row=3 or col=3, when MoveExecution created, then reject with E_POSITION_OUT_OF_BOUNDS |
| `success` | boolean | Required, must be true or false | N/A | Boolean validation (no error code needed) |
| `validation_errors` | list[string] | Optional, if present: list of error codes (E_CELL_OCCUPIED, E_POSITION_OUT_OF_BOUNDS, E_GAME_ALREADY_OVER) | N/A | List validation (each error code must be valid error code enum value) |
| `execution_time_ms` | float | Required, execution_time_ms ≥ 0.0, precision: 2 decimal places | `E_INVALID_EXECUTION_TIME` | Given execution_time_ms=-1.0, when MoveExecution created, then reject with E_INVALID_EXECUTION_TIME |
| `reasoning` | string | Required, non-empty (length > 0), max length 1000 characters | `E_MISSING_REASONING` | Given reasoning='' or reasoning=null, when MoveExecution created, then reject with E_MISSING_REASONING |
| `actual_priority_used` | MovePriority enum | Optional, if present: must be valid MovePriority enum value | `E_INVALID_PRIORITY` | Given actual_priority_used=invalid_enum_value, when MoveExecution created, then reject with E_INVALID_PRIORITY |

**Acceptance Criteria:**
- Given valid move execution, when MoveExecution is created, then success=True, validation_errors=empty list
- Given invalid move (cell occupied), when MoveExecution is created, then success=False, validation_errors contains `ERR_CELL_OCCUPIED`
- Given invalid move (out of bounds), when MoveExecution is created, then success=False, validation_errors contains `ERR_POSITION_OUT_OF_BOUNDS`
- Given multiple validation errors, when MoveExecution is created, then validation_errors list contains all error codes
- Given execution time 1234ms, when MoveExecution is created, then execution_time_ms=1234
- Given negative execution time, when MoveExecution is created, then validation error `ERR_INVALID_EXECUTION_TIME` is raised
- Given priority used differs from recommended, when MoveExecution is created, then actual_priority_used reflects priority that was executed

### Result Wrappers

**Agent Result**: Generic wrapper for agent outputs containing:
- Domain data (typed)
- Success/failure status
- Error message (if failed)
- Execution time in milliseconds
- Timestamp
- Optional metadata dictionary

AgentResult MUST provide factory methods: `AgentResult.success(data, execution_time_ms, metadata)` returns AgentResult with success=True, `AgentResult.error(error_message, execution_time_ms, metadata)` returns AgentResult with success=False.

**Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `success` | boolean | Required, must be true or false | N/A | Boolean validation (no error code needed) |
| `data` | object (typed) | Required if success=True, type depends on agent (BoardAnalysis, Strategy, or MoveExecution) | `E_MISSING_DATA` | Given success=True and data=null or data missing, when AgentResult created, then reject with E_MISSING_DATA |
| `error_code` | string | Required if success=False, must be valid error code enum value (E_* prefix pattern) | N/A | String validation (must match error code enum) |
| `error_message` | string | Required if success=False, non-empty (length > 0), max length 500 characters | `E_MISSING_ERROR_MESSAGE` | Given success=False and error_message='' or error_message=null, when AgentResult created, then reject with E_MISSING_ERROR_MESSAGE |
| `execution_time_ms` | float | Required, execution_time_ms ≥ 0.0, precision: 2 decimal places | `E_INVALID_EXECUTION_TIME` | Given execution_time_ms=-1.0, when AgentResult created, then reject with E_INVALID_EXECUTION_TIME |
| `timestamp` | string | Required, ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ), UTC timezone | `E_INVALID_TIMESTAMP` | Given timestamp='invalid' or wrong format, when AgentResult created, then reject with E_INVALID_TIMESTAMP |
| `metadata` | object | Optional, if present: key-value pairs, max 50 keys, each value max 200 characters | N/A | Object validation (optional field, no error code if absent) |

**Acceptance Criteria:**
- Given successful agent output with data, when AgentResult.success() is called, then success=True, error_message=None, data is populated
- Given failed agent execution, when AgentResult.error() is called, then success=False, error_message is populated, data=None
- Given execution time 2500ms, when AgentResult is created, then execution_time_ms=2500
- Given negative execution time, when AgentResult is created, then validation error `ERR_INVALID_EXECUTION_TIME` is raised
- Given timestamp, when AgentResult is created, then timestamp is ISO 8601 format (e.g., "2025-01-15T10:30:00Z")
- Given metadata dictionary {"model": "gpt-4o", "provider": "openai"}, when AgentResult is created, then metadata contains both key-value pairs
- Given success result without data, when AgentResult.success() is called, then validation error `ERR_MISSING_DATA` is raised
- Given error result without error_message, when AgentResult.error() is called, then validation error `ERR_MISSING_ERROR_MESSAGE` is raised

---

## 2.1 Machine-Verifiable Schema Definitions

**Complete schema definitions are maintained in [schemas.md](./schemas.md)** to keep this specification document concise.

### Schema Summary

The following domain models have formal JSON Schema (OpenAPI 3.1) definitions for machine verification, code generation, and automated validation:

**Core Game Schemas**:
- `Position`: Cell position on 3x3 board (row, col)
- `Board`: 3x3 matrix of cell states (EMPTY, X, O)
- `GameState`: Complete game state with board, players, move history, timestamps, metadata

**Agent Analysis Schemas**:
- `Threat`: Immediate threat where opponent can win
- `Opportunity`: Winning opportunity for current player
- `StrategicMove`: Strategic position recommendation
- `BoardAnalysis`: Scout agent output with threats, opportunities, strategic moves

**Agent Strategy Schemas**:
- `MovePriority`: 8-level priority enum (IMMEDIATE_WIN=100 to RANDOM_VALID=10)
- `MoveRecommendation`: Move with priority, confidence, reasoning
- `Strategy`: Strategist output with primary/alternative moves, game plan, risk assessment

**Agent Execution Schemas**:
- `ValidationError`: Move validation error details with error codes
- `MoveExecution`: Executor output with execution details and validation results

**Result Wrapper Schema**:
- `AgentResult`: Generic wrapper for agent outputs with success/error/timing

**API Request/Response Schemas**:
- `MoveRequest`: Player move request (row, col)
- `MoveResponse`: Move response with updated state and AI move
- `GameStatusResponse`: Complete game status including agents and metrics
- `ErrorResponse`: Standard error response for all API errors (error codes and HTTP status mappings defined in Section 5)

### Schema Usage Requirements

**Validation Requirements**:
1. All schemas MUST validate input/output data at runtime
2. Invalid data MUST be rejected with clear error messages referencing schema violations
3. Schema violations MUST include field name, expected type/constraint, and actual value
4. Implementations SHOULD generate types/classes from these schemas

**Code Generation**:
- JSON Schema can generate: TypeScript interfaces, Java classes, Go structs, C# classes, Python models
- OpenAPI generators: Swagger Codegen, OpenAPI Generator, Postman
- Validation libraries: AJV (JavaScript), go-playground/validator (Go), jsonschema (Python), System.Text.Json (C#)

**Schema Evolution**:
- Backward-compatible changes: Add optional fields, relax constraints
- Breaking changes: Remove fields, change types, tighten constraints
- Version schemas when making breaking changes
- Maintain migration documentation

---

## 3. Agent Architecture

### Agent Responsibilities

**Scout Agent**: Analyzes the board to identify:
- Immediate threats (opponent has exactly 2 symbols in a line with exactly 1 empty cell - will win next move if not blocked)
- Winning opportunities (AI has exactly 2 symbols in a line with exactly 1 empty cell - will win on this move)
- Strategic positions (center position (1,1), corner positions (0,0/0,2/2,0/2,2), edge positions (0,1/1,0/1,2/2,1))
- Game phase assessment (opening: 0-2 moves, midgame: 3-6 moves, endgame: 7-9 moves)
- Board evaluation score (float -1.0 to 1.0, where >0 favors AI, <0 favors opponent, ≈0 is balanced)

**Implementation Requirements**:
- Scout MUST first check for immediate wins/blocks using rule-based logic (checking all lines for 2 symbols + 1 empty)
- When rule-based checks find immediate win or block, Scout MUST list it in opportunities/threats with confidence ≥ 0.9 without calling LLM
- When rule-based checks find no immediate win/block, Scout MUST call LLM for strategic analysis
- Scout MUST always return BoardAnalysis containing at minimum: threats list, opportunities list, strategic_moves list (may be empty), game_phase, board_evaluation_score

**Acceptance Criteria:**
- Given board with opponent two-in-a-row, when Scout.analyze() is called, then BoardAnalysis contains Threat with blocking position
- Given board with AI two-in-a-row, when Scout.analyze() is called, then BoardAnalysis contains Opportunity with winning position
- Given empty board, when Scout.analyze() is called, then BoardAnalysis recommends center position (1,1) as StrategicMove
- Given board with 0-2 moves, when Scout.analyze() is called, then game_phase='opening'
- Given board with 3-6 moves, when Scout.analyze() is called, then game_phase='midgame'
- Given board with 7-9 moves, when Scout.analyze() is called, then game_phase='endgame'
- Given LLM timeout (>5s), when Scout.analyze() is called, then returns rule-based BoardAnalysis (fallback)
- Given invalid board (size ≠ 3x3), when Scout.analyze() is called, then returns AgentResult.error() with code `ERR_INVALID_BOARD`
- Given favorable AI board position, when Scout.analyze() is called, then board_evaluation_score > 0.0
- Given execution time, when Scout.analyze() completes, then AgentResult.execution_time_ms is recorded

**Strategist Agent**: Converts Scout analysis into a strategy:
- Strategist MUST select moves in this priority order (highest to lowest):
  1. Winning moves (IMMEDIATE_WIN, priority 100)
  2. Blocking opponent win (BLOCK_THREAT, priority 90)
  3. Creating fork (FORCE_WIN, priority 80)
  4. Blocking fork (PREVENT_FORK, priority 70)
  5. Center position (CENTER_CONTROL, priority 50)
  6. Corner position (CORNER_CONTROL, priority 40)
  7. Edge position (EDGE_PLAY, priority 30)
  8. Any valid move (RANDOM_VALID, priority 10)
- Strategist MUST output exactly one primary move (highest priority) and at least two alternative moves (next highest priorities), all sorted by priority descending
- Strategist MUST assign confidence scores (0.0-1.0) to each move based on Move Priority System confidence values
- Strategist MUST provide game_plan (string) and risk_assessment (low/medium/high) for the strategy

**Acceptance Criteria:**
- Given BoardAnalysis with Threat, when Strategist.plan() is called, then primary_move blocks threat with priority=BLOCK_THREAT (90)
- Given BoardAnalysis with Opportunity to win, when Strategist.plan() is called, then primary_move takes win with priority=IMMEDIATE_WIN (100)
- Given BoardAnalysis with both Threat and Opportunity, when Strategist.plan() is called, then primary_move takes win (IMMEDIATE_WIN > BLOCK_THREAT)
- Given BoardAnalysis with multiple strategic positions, when Strategist.plan() is called, then alternatives list sorted by priority descending
- Given BoardAnalysis with no clear moves, when Strategist.plan() is called, then recommends center/corner with reasoning
- Given LLM timeout (>5s), when Strategist.plan() is called, then returns rule-based Strategy using Scout's highest priority opportunity
- Given empty BoardAnalysis (no threats/opportunities), when Strategist.plan() is called, then returns Strategy with CENTER_CONTROL priority
- Given execution time, when Strategist.plan() completes, then AgentResult.execution_time_ms is recorded

**Executor Agent**: Executes the recommended move:
- Executor MUST validate move (bounds check: row/col in range 0-2, empty cell check, game rules: game not over)
- Executor MUST execute move if validation passes
- Executor MUST return MoveExecution with success=False and validation_errors list if validation fails
- Executor MUST return MoveExecution with execution_time_ms (milliseconds) and actual_priority_used (MovePriority enum value)

**Acceptance Criteria:**
- Given Strategy with valid move (empty cell, in bounds), when Executor.execute() is called, then returns MoveExecution with success=True
- Given Strategy with occupied cell move, when Executor.execute() is called, then returns MoveExecution with success=False, validation_errors contains `ERR_CELL_OCCUPIED`
- Given Strategy with out-of-bounds move (3,3), when Executor.execute() is called, then returns MoveExecution with success=False, validation_errors contains `ERR_POSITION_OUT_OF_BOUNDS`
- Given Strategy with game-over state, when Executor.execute() is called, then returns MoveExecution with success=False, validation_errors contains `ERR_GAME_OVER`
- Given multiple validation errors, when Executor.execute() is called, then MoveExecution.validation_errors contains all error codes
- Given execution time, when Executor.execute() completes, then MoveExecution.execution_time_ms is recorded
- Given valid move execution, when Executor.execute() completes, then MoveExecution.actual_priority_used matches Strategy.primary_move.priority

### Agent Interface Contract

All agents implement a protocol with a single primary method:
- Scout: analyze method takes GameState, returns AgentResult containing BoardAnalysis
- Strategist: plan method takes GameState and BoardAnalysis, returns AgentResult containing Strategy
- Executor: execute method takes GameState and Strategy, returns AgentResult containing MoveExecution

Agents are stateless; all context comes from inputs. Results include execution metadata (timing, success/failure).

**Acceptance Criteria:**
- Given GameState input, when any agent method is called, then agent does not modify GameState (stateless)
- Given repeated calls with same GameState, when agent method is called, then returns consistent results (deterministic for rule-based checks, LLM-based responses may vary but MUST follow same priority rules)
- Given AgentResult output, when method completes, then AgentResult contains execution_time_ms, timestamp, success status
- Given agent method failure, when error occurs, then returns AgentResult.error() with error message and code
- Given agent method success, when completed, then returns AgentResult.success() with typed domain data (BoardAnalysis/Strategy/MoveExecution)

### Agent Timeout Configuration

**Per-Agent Timeouts**:
- **Scout Agent**: 5 seconds (rule-based fallback available)
- **Strategist Agent**: 5 seconds (uses Scout's best opportunity as fallback)
- **Executor Agent**: 3 seconds (direct move execution, minimal processing)
- **Total Pipeline Timeout**: 15 seconds (sum of all agents + 2s buffer)

**Timeout Behavior**:
- At 2 seconds: Show loading spinner with "AI is thinking..."
- At 5 seconds: Update message to "AI is analyzing carefully..." and show progress bar
- At 10 seconds: Update message to "Taking longer than usual, preparing fallback..."
- At timeout: Execute fallback strategy and show completion message

**Configuration**:
- Timeout values configurable via config file
- Different timeouts for local mode (5s/5s/3s) vs distributed MCP mode (10s/10s/5s)

### Move Priority System

The Move Priority System defines a strict ordering for move selection with numeric priority values and clear decision rules:

**Priority Levels (Descending Order)**:

1. **IMMEDIATE_WIN (100)**: AI has exactly 2 symbols in a line with exactly 1 empty cell remaining in that line
   - Detection: MUST check all 8 lines (3 rows, 3 columns, 2 diagonals) for pattern: 2 AI symbols + 1 empty cell
   - Action: MUST select this move (highest priority)
   - Confidence: 1.0 (guaranteed win if move is made)
   - Example: AI has X at (0,0) and (0,1), MUST play (0,2) to win

2. **BLOCK_THREAT (90)**: Opponent has exactly 2 symbols in a line with exactly 1 empty cell remaining in that line
   - Detection: MUST check all 8 lines for pattern: 2 opponent symbols + 1 empty cell
   - Action: MUST block this position (defensive, prevents opponent win)
   - Confidence: 1.0 (necessary move to prevent immediate loss)
   - Example: Opponent has O at (1,0) and (1,1), MUST play (1,2) to block

3. **FORCE_WIN (80)**: Move creates a fork (exactly 2 unblocked lines each containing 2 AI symbols after the move)
   - Detection: MUST check if move results in 2 distinct lines each with 2 AI symbols + 1 empty (after move)
   - Action: MUST select this move (opponent can block only 1 line, AI will win on next move)
   - Confidence: 0.95 (guarantees win within 2 moves)
   - Example: Play corner (0,0) when it creates diagonal threats on both main diagonal and anti-diagonal

4. **PREVENT_FORK (70)**: Move blocks opponent from creating a fork (exactly 2 unblocked lines each containing 2 opponent symbols simultaneously)
   - Detection: MUST check if opponent's potential next move would create exactly 2 distinct lines each with 2 opponent symbols + 1 empty
   - Action: MUST block the position that would allow opponent fork, or force opponent to defend instead of attacking
   - Confidence: 0.85 (prevents opponent advantage)
   - Example: Block opponent's second corner when they hold opposite corner

5. **CENTER_CONTROL (50)**: Take center position (1,1)
   - Detection: MUST check if center (1,1) is empty and no moves with priority >50 exist
   - Action: MUST select center position (1,1) which participates in 4 lines (row 1, column 1, main diagonal, anti-diagonal)
   - Confidence: 0.75 (strong opening/midgame)
   - Example: First move or early game when center available

6. **CORNER_CONTROL (40)**: Take corner position (0,0 / 0,2 / 2,0 / 2,2)
   - Detection: MUST check if any corner is empty and no moves with priority >40 exist
   - Action: MUST select corner position which participates in 3 lines each (1 row, 1 column, 1 diagonal)
   - Confidence: 0.60 (solid strategic position)
   - Example: Opening move or when center taken

7. **EDGE_PLAY (30)**: Take edge position (0,1 / 1,0 / 1,2 / 2,1)
   - Detection: MUST check if any edge is empty and no moves with priority >30 exist
   - Action: MUST select edge position which participates in 2 lines each (1 row or 1 column only, no diagonal)
   - Confidence: 0.40 (weaker position)
   - Example: Most corners and center taken

8. **RANDOM_VALID (10)**: Any valid empty cell (fallback when no strategic patterns detected)
   - Detection: MUST check if no strategic patterns (priorities 100-30) are found
   - Action: MUST pick any available empty cell (deterministic selection: first empty position in order 0,0 < 0,1 < ... < 2,2)
   - Confidence: 0.20 (minimal strategic value)
   - Example: Backup when analysis fails

**Decision Algorithm**:

```
1. Scout identifies all opportunities and threats
2. Strategist evaluates each possible move:
   a. Check for IMMEDIATE_WIN (priority 100)
   b. Check for BLOCK_THREAT (priority 90)
   c. Check for FORCE_WIN (priority 80)
   d. Check for PREVENT_FORK (priority 70)
   e. Check for CENTER_CONTROL (priority 50)
   f. Check for CORNER_CONTROL (priority 40)
   g. Check for EDGE_PLAY (priority 30)
   h. Fallback to RANDOM_VALID (priority 10)
3. Select move with highest priority value
4. If multiple moves have same priority, use confidence score as tiebreaker
5. If still tied, prefer moves in this order: center > corners > edges
```

**Tie-Breaking Rules**:
1. Higher numeric priority always wins
2. Same priority → higher confidence score
3. Same confidence → position preference (center > corner > edge)
4. Same position type → prefer positions that participate in more open lines
5. Final tiebreaker → deterministic position ordering (0,0 < 0,1 < 0,2 < 1,0...)

**Validation**:
- All moves MUST be validated before recommendation (bounds check: row/col in range 0-2, empty cell check)
- Invalid moves (occupied, out of bounds) MUST be automatically filtered (excluded from recommendation list)
- If highest priority move is invalid, Strategist MUST try next highest valid priority
- Executor MUST perform final validation before execution (bounds, empty cell, game not over)

**Acceptance Criteria:**
- Given AI has 2 symbols in a line with 1 empty cell, when evaluating moves, then IMMEDIATE_WIN (100) is assigned to that position
- Given opponent has 2 symbols in a line with 1 empty cell, when evaluating moves, then BLOCK_THREAT (90) is assigned to blocking position
- Given move creates 2 unblocked winning lines simultaneously, when evaluating moves, then FORCE_WIN (80) is assigned
- Given opponent's move would create 2 winning threats, when evaluating moves, then PREVENT_FORK (70) is assigned to blocking position
- Given center (1,1) is empty and no threats/wins exist, when evaluating moves, then CENTER_CONTROL (50) is assigned to (1,1)
- Given corner (0,0/0,2/2,0/2,2) is empty and no higher priorities exist, when evaluating moves, then CORNER_CONTROL (40) is assigned
- Given edge (0,1/1,0/1,2/2,1) is empty and no higher priorities exist, when evaluating moves, then EDGE_PLAY (30) is assigned
- Given no strategic pattern detected, when evaluating moves, then RANDOM_VALID (10) is assigned to any empty cell
- Given multiple moves with same priority, when selecting move, then move with higher confidence score is selected
- Given multiple moves with same priority and confidence, when selecting move, then center > corner > edge preference is applied
- Given two corners with same priority, when selecting move, then corner with more open lines is preferred
- Given all tiebreakers equal, when selecting move, then deterministic position ordering (0,0 < 0,1 < ... < 2,2) is applied
- Given occupied cell, when filtering moves, then cell is excluded from recommendations
- Given out-of-bounds position, when filtering moves, then position is excluded from recommendations
- Given highest priority move is invalid, when selecting move, then next highest valid priority is selected

### Agent Pipeline Flow

The coordinator MUST execute a deterministic sequential pipeline with exact rules for every branch. All decision points and fallback strategies are defined below.

#### Pipeline Entry Point

**Step 0: Pre-flight Validation**
- Given GameState with board size ≠ 3×3, when pipeline starts, then pipeline MUST return error without calling any agents, error_code=`E_INVALID_BOARD_SIZE`
- Given GameState with is_game_over=True, when pipeline starts, then pipeline MUST return error without calling any agents, error_code=`E_GAME_ALREADY_OVER`
- Given valid GameState, when pipeline starts, then proceed to Step 1

#### Step 1: Convert Game State
- Coordinator MUST convert current game state to GameState domain model
- Given conversion fails, when GameState creation fails, then pipeline MUST return error, error_code=`E_STATE_CORRUPTED`
- Given conversion succeeds, when GameState is created, then proceed to Step 2

#### Step 2: Scout Analysis

**Step 2.1: Call Scout Agent**
- Coordinator MUST call `Scout.analyze(GameState)` with timeout of 5 seconds (local mode) or 10 seconds (distributed mode)
- Coordinator MUST record start_time before calling Scout

**Step 2.2: Handle Scout Success**
- Given Scout returns `AgentResult.success=True` AND `AgentResult.data` contains valid `BoardAnalysis`, when Scout succeeds, then:
  - Store BoardAnalysis from AgentResult.data
  - Record execution_time_ms from AgentResult.execution_time_ms
  - Proceed to Step 3

**Step 2.3: Handle Scout Failure - Timeout**
- Given Scout call exceeds timeout (5s local / 10s distributed), when timeout occurs, then:
  - Coordinator MUST retry Scout.analyze() up to 3 times with exponential backoff (1s, 2s, 4s delays)
  - Given all 3 retries timeout, when retries exhausted, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 1: Rule-Based BoardAnalysis** (see below)
    - Log error with error_code=`E_LLM_TIMEOUT`, agent_name="scout", retry_count=3
    - Proceed to Step 3 with rule-based BoardAnalysis

**Step 2.4: Handle Scout Failure - Parse Error**
- Given Scout returns `AgentResult.success=False` AND error_code=`E_LLM_PARSE_ERROR`, when parse error occurs, then:
  - Coordinator MUST retry Scout.analyze() up to 2 times with prompt refinement
  - Given all 2 retries fail with parse error, when retries exhausted, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 1: Rule-Based BoardAnalysis** (see below)
    - Log error with error_code=`E_LLM_PARSE_ERROR`, agent_name="scout", retry_count=2
    - Proceed to Step 3 with rule-based BoardAnalysis

**Step 2.5: Handle Scout Failure - Other Errors**
- Given Scout returns `AgentResult.success=False` AND error_code NOT in {`E_LLM_TIMEOUT`, `E_LLM_PARSE_ERROR`}, when Scout fails, then:
  - Coordinator MUST retry Scout.analyze() exactly 1 time with same inputs
  - Given retry fails, when second failure occurs, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 1: Rule-Based BoardAnalysis** (see below)
    - Log error with error_code=`E_SCOUT_FAILED`, agent_name="scout", retry_count=1, original_error_code from AgentResult
    - Proceed to Step 3 with rule-based BoardAnalysis

**Fallback Rule Set 1: Rule-Based BoardAnalysis**
When Scout fails, coordinator MUST generate BoardAnalysis using exactly these rules in priority order:
1. **Check for Immediate Win**: Scan all 8 lines (3 rows, 3 columns, 2 diagonals) for AI having exactly 2 symbols and 1 empty cell. If found, add Opportunity with position=empty_cell, confidence=0.95, priority=IMMEDIATE_WIN (100)
2. **Check for Block**: Scan all 8 lines for opponent having exactly 2 symbols and 1 empty cell. If found, add Threat with position=empty_cell, severity='critical', and add Opportunity with position=empty_cell, confidence=0.90, priority=BLOCK_THREAT (90)
3. **Check for Center**: If center (1,1) is empty, add StrategicMove with position=(1,1), move_type='center', priority=50, confidence=0.75
4. **Check for Corner**: If any corner (0,0), (0,2), (2,0), (2,2) is empty, add StrategicMove with position=first_available_corner (in order 0,0 < 0,2 < 2,0 < 2,2), move_type='corner', priority=40, confidence=0.60
5. **Default to Any Empty**: If no strategic moves found, select first empty cell in order (0,0 < 0,1 < 0,2 < 1,0 < 1,1 < 1,2 < 2,0 < 2,1 < 2,2), add StrategicMove with priority=10, confidence=0.20
- BoardAnalysis MUST contain: threats list (may be empty), opportunities list (may be empty), strategic_moves list (must contain at least 1 move), game_phase calculated from move_count (0-2=opening, 3-6=midgame, 7-9=endgame), board_evaluation_score=0.0 (neutral)

#### Step 3: Strategist Planning

**Step 3.1: Call Strategist Agent**
- Coordinator MUST call `Strategist.plan(GameState, BoardAnalysis)` with timeout of 5 seconds (local mode) or 10 seconds (distributed mode)
- Coordinator MUST record start_time before calling Strategist

**Step 3.2: Handle Strategist Success**
- Given Strategist returns `AgentResult.success=True` AND `AgentResult.data` contains valid `Strategy` with primary_move, when Strategist succeeds, then:
  - Validate Strategy.primary_move.position is valid (bounds 0-2, cell is empty in current GameState)
  - Given Strategy.primary_move is invalid, when validation fails, then:
    - Execute **Fallback Rule Set 2: Scout Opportunity Fallback** (see below)
    - Log warning: primary_move invalid, using Scout opportunity
    - Proceed to Step 4 with fallback move
  - Given Strategy.primary_move is valid, when validation succeeds, then:
    - Store Strategy from AgentResult.data
    - Record execution_time_ms from AgentResult.execution_time_ms
    - Proceed to Step 4

**Step 3.3: Handle Strategist Failure - Timeout**
- Given Strategist call exceeds timeout (5s local / 10s distributed), when timeout occurs, then:
  - Coordinator MUST retry Strategist.plan() up to 3 times with exponential backoff (1s, 2s, 4s delays)
  - Given all 3 retries timeout, when retries exhausted, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 2: Scout Opportunity Fallback** (see below)
    - Log error with error_code=`E_LLM_TIMEOUT`, agent_name="strategist", retry_count=3
    - Proceed to Step 4 with fallback move

**Step 3.4: Handle Strategist Failure - Parse Error**
- Given Strategist returns `AgentResult.success=False` AND error_code=`E_LLM_PARSE_ERROR`, when parse error occurs, then:
  - Coordinator MUST retry Strategist.plan() up to 2 times with prompt refinement
  - Given all 2 retries fail with parse error, when retries exhausted, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 2: Scout Opportunity Fallback** (see below)
    - Log error with error_code=`E_LLM_PARSE_ERROR`, agent_name="strategist", retry_count=2
    - Proceed to Step 4 with fallback move

**Step 3.5: Handle Strategist Failure - Other Errors**
- Given Strategist returns `AgentResult.success=False` AND error_code NOT in {`E_LLM_TIMEOUT`, `E_LLM_PARSE_ERROR`}, when Strategist fails, then:
  - Coordinator MUST retry Strategist.plan() exactly 1 time with same inputs
  - Given retry fails, when second failure occurs, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 2: Scout Opportunity Fallback** (see below)
    - Log error with error_code=`E_STRATEGIST_FAILED`, agent_name="strategist", retry_count=1, original_error_code from AgentResult
    - Proceed to Step 4 with fallback move

**Fallback Rule Set 2: Scout Opportunity Fallback**
When Strategist fails, coordinator MUST select move from BoardAnalysis using exactly these rules in priority order:
1. **Highest Priority Opportunity**: If opportunities list is non-empty, select opportunity with highest priority (IMMEDIATE_WIN=100 > BLOCK_THREAT=90). If multiple opportunities have same priority, select one with highest confidence. If multiple have same priority and confidence, select first in list order.
2. **Highest Priority Strategic Move**: If opportunities list is empty and strategic_moves list is non-empty, select strategic_move with highest priority. If multiple strategic_moves have same priority, select one with highest confidence. If multiple have same priority and confidence, apply tiebreaker: center (1,1) > corner (0,0/0,2/2,0/2,2) > edge (0,1/1,0/1,2/2,1). If still tied, select first in position order (0,0 < 0,1 < ... < 2,2).
3. **First Empty Cell**: If both opportunities and strategic_moves lists are empty, select first empty cell in position order (0,0 < 0,1 < 0,2 < 1,0 < 1,1 < 1,2 < 2,0 < 2,1 < 2,2)
- Create Strategy object with primary_move=selected_move, alternatives=[], game_plan="Fallback: Using Scout analysis", risk_assessment="medium"
- Validate selected move position is valid (bounds 0-2, cell is empty). If invalid, select next valid position from same priority level, or proceed to next priority level.

#### Step 4: Executor Execution

**Step 4.1: Call Executor Agent**
- Coordinator MUST call `Executor.execute(GameState, Strategy)` with timeout of 3 seconds (local mode) or 5 seconds (distributed mode)
- Coordinator MUST record start_time before calling Executor

**Step 4.2: Handle Executor Success**
- Given Executor returns `AgentResult.success=True` AND `AgentResult.data` contains valid `MoveExecution` with success=True AND valid position, when Executor succeeds, then:
  - Validate MoveExecution.position is valid (bounds 0-2, cell is empty in current GameState)
  - Given MoveExecution.position is invalid, when validation fails, then:
    - Execute **Fallback Rule Set 3: Strategist Primary Move Fallback** (see below)
    - Log warning: Executor move invalid, using Strategist primary move
    - Proceed to Step 5 with fallback move
  - Given MoveExecution.position is valid, when validation succeeds, then:
    - Store MoveExecution from AgentResult.data
    - Record execution_time_ms from AgentResult.execution_time_ms
    - Extract position from MoveExecution.position
    - Proceed to Step 5

**Step 4.3: Handle Executor Failure - Timeout**
- Given Executor call exceeds timeout (3s local / 5s distributed), when timeout occurs, then:
  - Coordinator MUST retry Executor.execute() up to 3 times with exponential backoff (1s, 2s, 4s delays)
  - Given all 3 retries timeout, when retries exhausted, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 3: Strategist Primary Move Fallback** (see below)
    - Log error with error_code=`E_LLM_TIMEOUT`, agent_name="executor", retry_count=3
    - Proceed to Step 5 with fallback move

**Step 4.4: Handle Executor Failure - Parse Error**
- Given Executor returns `AgentResult.success=False` AND error_code=`E_LLM_PARSE_ERROR`, when parse error occurs, then:
  - Coordinator MUST retry Executor.execute() up to 2 times with prompt refinement
  - Given all 2 retries fail with parse error, when retries exhausted, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 3: Strategist Primary Move Fallback** (see below)
    - Log error with error_code=`E_LLM_PARSE_ERROR`, agent_name="executor", retry_count=2
    - Proceed to Step 5 with fallback move

**Step 4.5: Handle Executor Failure - Validation Error**
- Given Executor returns `AgentResult.success=True` AND `MoveExecution.success=False` with validation_errors, when Executor reports validation failure, then:
  - Check validation_errors list for error codes: `E_CELL_OCCUPIED`, `E_POSITION_OUT_OF_BOUNDS`
  - If validation_errors contains `E_CELL_OCCUPIED` OR `E_POSITION_OUT_OF_BOUNDS`, then:
    - Execute **Fallback Rule Set 3: Strategist Primary Move Fallback** (see below)
    - Log warning: Executor validation failed, using Strategist primary move
    - Proceed to Step 5 with fallback move

**Step 4.6: Handle Executor Failure - Other Errors**
- Given Executor returns `AgentResult.success=False` AND error_code NOT in {`E_LLM_TIMEOUT`, `E_LLM_PARSE_ERROR`}, when Executor fails, then:
  - Coordinator MUST retry Executor.execute() exactly 1 time with same inputs
  - Given retry fails, when second failure occurs, then:
    - Set fallback_active=True
    - Execute **Fallback Rule Set 3: Strategist Primary Move Fallback** (see below)
    - Log error with error_code=`E_EXECUTOR_FAILED`, agent_name="executor", retry_count=1, original_error_code from AgentResult
    - Proceed to Step 5 with fallback move

**Fallback Rule Set 3: Strategist Primary Move Fallback**
When Executor fails, coordinator MUST use Strategist's primary move with basic validation:
1. **Extract Primary Move**: Get Strategy.primary_move.position
2. **Validate Position**: Check bounds (row in 0-2, col in 0-2) AND check cell is empty in current GameState
3. **Given Primary Move is Valid**: When validation passes, use Strategy.primary_move.position as final move position
4. **Given Primary Move is Invalid**: When validation fails (occupied or out-of-bounds), then:
   - Check Strategy.alternatives list for first valid alternative move (bounds check AND empty cell check)
   - Given valid alternative found, when alternative is valid, use alternative move position
   - Given no valid alternatives, when all alternatives are invalid, select first empty cell in position order (0,0 < 0,1 < ... < 2,2)
5. Create MoveExecution object with position=selected_position, success=True, actual_priority_used=Strategy.primary_move.priority, validation_errors=[]

#### Step 5: Apply Move to Game Engine

**Step 5.1: Final Position Validation**
- Coordinator MUST validate final position before applying:
  - Position bounds: row in range 0-2, col in range 0-2
  - Cell is empty in current GameState.board
  - GameState.is_game_over=False

**Step 5.2: Handle Validation Failure**
- Given final position fails validation, when validation fails, then:
  - Pipeline MUST return error, error_code=`E_MOVE_OUT_OF_BOUNDS` (if bounds invalid) OR `E_CELL_OCCUPIED` (if cell occupied) OR `E_GAME_ALREADY_OVER` (if game over)
  - Pipeline MUST NOT apply move to game engine
  - Pipeline MUST NOT increment move_count
  - Pipeline MUST return error response to caller

**Step 5.3: Apply Move**
- Given final position passes validation, when validation succeeds, then:
  - Coordinator MUST call `game_engine.make_move(position, ai_symbol)`
  - Coordinator MUST check make_move return value for success
  - Given make_move returns success, when move applied, then:
    - Record move in move_history
    - Increment move_count
    - Update GameState
    - Proceed to Step 6
  - Given make_move returns failure, when move fails, then:
    - Pipeline MUST return error with error_code from make_move (typically `E_CELL_OCCUPIED` or `E_MOVE_OUT_OF_BOUNDS`)
    - Pipeline MUST return error response to caller

#### Step 6: Return Result

**Step 6.1: Build Success Response**
- Given move applied successfully, when pipeline completes, then:
  - Build MoveResponse with:
    - success=True
    - position=applied_move_position
    - updated_game_state=current GameState after move
    - ai_move_execution=MoveExecution object (from Executor or fallback)
    - fallback_used=fallback_active flag
    - total_execution_time_ms=sum of all agent execution times + coordinator overhead
  - Return MoveResponse to caller

**Step 6.2: Pipeline Timeout Check**
- Given pipeline total execution time exceeds 15 seconds, when timeout check occurs, then:
  - Pipeline MUST abort current agent call (if in progress)
  - Execute fastest available fallback:
    - If at Step 2-3: Execute Fallback Rule Set 1, then Fallback Rule Set 2, proceed to Step 5
    - If at Step 4: Execute Fallback Rule Set 3, proceed to Step 5
  - Log warning with error_code=`E_LLM_TIMEOUT`, message="Pipeline exceeded 15s timeout, using fallback"
  - Continue with fallback move application

#### Pipeline Summary

The pipeline MUST execute in exactly this order: Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6

Each step MUST validate conditions before proceeding. Each failure branch MUST execute the specified fallback rule set. All error codes MUST match the Error Code Enum (Section 5). All retry policies MUST follow the counts and delays specified above.

**Acceptance Criteria:**

**Pre-flight Validation:**
- Given GameState with board size ≠ 3×3, when pipeline starts, then returns error without calling agents, error_code=`E_INVALID_BOARD_SIZE`
- Given GameState with is_game_over=True, when pipeline starts, then returns error without calling agents, error_code=`E_GAME_ALREADY_OVER`
- Given valid GameState, when pipeline starts, then proceeds to Step 1

**Scout Analysis Success:**
- Given Scout returns AgentResult.success=True with valid BoardAnalysis, when Scout succeeds, then BoardAnalysis is stored and pipeline proceeds to Step 3
- Given Scout.analyze() completes within timeout, when Scout succeeds, then execution_time_ms is recorded

**Scout Failure - Timeout:**
- Given Scout call exceeds 5s timeout (local mode), when timeout occurs, then retries up to 3 times with exponential backoff (1s, 2s, 4s delays)
- Given all 3 Scout retries timeout, when retries exhausted, then executes Fallback Rule Set 1 (rule-based BoardAnalysis), sets fallback_active=True, logs error_code=`E_LLM_TIMEOUT`, agent_name="scout", retry_count=3
- Given Scout timeout on retry attempt 2, when Scout responds successfully, then uses Scout response, cancels remaining retries, proceeds to Step 3

**Scout Failure - Parse Error:**
- Given Scout returns error_code=`E_LLM_PARSE_ERROR`, when parse error occurs, then retries up to 2 times with prompt refinement
- Given all 2 Scout retries fail with parse error, when retries exhausted, then executes Fallback Rule Set 1, sets fallback_active=True, logs error_code=`E_LLM_PARSE_ERROR`, agent_name="scout", retry_count=2

**Scout Failure - Other Errors:**
- Given Scout returns AgentResult.success=False with error_code NOT in {`E_LLM_TIMEOUT`, `E_LLM_PARSE_ERROR`}, when Scout fails, then retries exactly 1 time with same inputs
- Given Scout retry fails, when second failure occurs, then executes Fallback Rule Set 1, sets fallback_active=True, logs error_code=`E_SCOUT_FAILED`, agent_name="scout", retry_count=1

**Fallback Rule Set 1:**
- Given Scout fails, when Fallback Rule Set 1 executes, then BoardAnalysis contains: opportunities list with IMMEDIATE_WIN (priority 100) if AI has 2-in-a-row, threats/opportunities list with BLOCK_THREAT (priority 90) if opponent has 2-in-a-row, strategic_moves list with center (1,1) priority 50 if center is empty, strategic_moves list with corner priority 40 if corners available, at least 1 strategic_move (may be priority 10 fallback)
- Given empty board, when Fallback Rule Set 1 executes, then strategic_moves contains center (1,1) with priority 50, confidence 0.75

**Strategist Planning Success:**
- Given Strategist returns AgentResult.success=True with valid Strategy containing primary_move, when Strategist succeeds, then Strategy.primary_move.position is validated (bounds 0-2, cell is empty)
- Given Strategist.primary_move is valid, when validation succeeds, then Strategy is stored and pipeline proceeds to Step 4
- Given Strategist.primary_move is invalid (occupied or out-of-bounds), when validation fails, then executes Fallback Rule Set 2 (Scout opportunity fallback), logs warning, proceeds to Step 4

**Strategist Failure - Timeout:**
- Given Strategist call exceeds 5s timeout (local mode), when timeout occurs, then retries up to 3 times with exponential backoff (1s, 2s, 4s delays)
- Given all 3 Strategist retries timeout, when retries exhausted, then executes Fallback Rule Set 2, sets fallback_active=True, logs error_code=`E_LLM_TIMEOUT`, agent_name="strategist", retry_count=3

**Strategist Failure - Other Errors:**
- Given Strategist returns AgentResult.success=False, when Strategist fails, then retries exactly 1 time with same inputs
- Given Strategist retry fails, when second failure occurs, then executes Fallback Rule Set 2, sets fallback_active=True, logs error_code=`E_STRATEGIST_FAILED`, agent_name="strategist", retry_count=1

**Fallback Rule Set 2:**
- Given Strategist fails, when Fallback Rule Set 2 executes, then selects highest priority opportunity from BoardAnalysis.opportunities (IMMEDIATE_WIN=100 > BLOCK_THREAT=90). If multiple opportunities have same priority, selects one with highest confidence. If opportunities list is empty, selects highest priority strategic_move from BoardAnalysis.strategic_moves
- Given BoardAnalysis has no opportunities or strategic_moves, when Fallback Rule Set 2 executes, then selects first empty cell in position order (0,0 < 0,1 < ... < 2,2)
- Given Fallback Rule Set 2 selects move, when move is selected, then creates Strategy with primary_move=selected_move, alternatives=[], game_plan="Fallback: Using Scout analysis", risk_assessment="medium"

**Executor Execution Success:**
- Given Executor returns AgentResult.success=True with MoveExecution.success=True and valid position, when Executor succeeds, then MoveExecution.position is validated (bounds 0-2, cell is empty)
- Given Executor.position is valid, when validation succeeds, then position is extracted and pipeline proceeds to Step 5

**Executor Failure - Validation Error:**
- Given Executor returns MoveExecution.success=False with validation_errors containing `E_CELL_OCCUPIED` or `E_POSITION_OUT_OF_BOUNDS`, when Executor reports validation failure, then executes Fallback Rule Set 3, logs warning, proceeds to Step 5

**Executor Failure - Timeout:**
- Given Executor call exceeds 3s timeout (local mode), when timeout occurs, then retries up to 3 times with exponential backoff (1s, 2s, 4s delays)
- Given all 3 Executor retries timeout, when retries exhausted, then executes Fallback Rule Set 3, sets fallback_active=True, logs error_code=`E_LLM_TIMEOUT`, agent_name="executor", retry_count=3

**Executor Failure - Other Errors:**
- Given Executor returns AgentResult.success=False, when Executor fails, then retries exactly 1 time with same inputs
- Given Executor retry fails, when second failure occurs, then executes Fallback Rule Set 3, sets fallback_active=True, logs error_code=`E_EXECUTOR_FAILED`, agent_name="executor", retry_count=1

**Fallback Rule Set 3:**
- Given Executor fails, when Fallback Rule Set 3 executes, then extracts Strategy.primary_move.position and validates (bounds 0-2, cell is empty)
- Given Strategy.primary_move is valid, when validation passes, then uses Strategy.primary_move.position as final move position
- Given Strategy.primary_move is invalid, when validation fails, then checks Strategy.alternatives list for first valid alternative (bounds AND empty cell check)
- Given valid alternative found, when alternative is valid, then uses alternative move position
- Given no valid alternatives, when all alternatives are invalid, then selects first empty cell in position order (0,0 < 0,1 < ... < 2,2)

**Move Application:**
- Given final position passes validation (bounds 0-2, cell is empty, game not over), when validation succeeds, then calls game_engine.make_move(position, ai_symbol)
- Given make_move returns success, when move is applied, then move is recorded in move_history, move_count is incremented, GameState is updated
- Given final position fails validation, when validation fails, then pipeline returns error with error_code=`E_MOVE_OUT_OF_BOUNDS` (if bounds invalid) OR `E_CELL_OCCUPIED` (if occupied) OR `E_GAME_ALREADY_OVER` (if game over), move is NOT applied

**Pipeline Timeout:**
- Given pipeline total execution time exceeds 15 seconds, when timeout check occurs, then pipeline aborts current agent call, executes fastest available fallback (Fallback Rule Set 1/2/3 based on current step), logs warning with error_code=`E_LLM_TIMEOUT`, continues with fallback move application

**Response Building:**
- Given pipeline completes successfully, when move is applied, then returns MoveResponse with success=True, position=applied_move_position, updated_game_state, ai_move_execution, fallback_used=fallback_active flag, total_execution_time_ms=sum of all agent execution times

---

## 4. Game State Management

### State Model

Game state is a pure data model representing the complete state of a Tic-Tac-Toe game at any point in time. It is independent of the game engine, agents, UI, and transport layers, enabling state persistence, auditing, and concurrent games.

**GameState Properties**:
- `game_id`: Unique identifier (UUID v4)
- `board`: Current 3x3 board configuration
- `current_player`: Whose turn it is (X or O)
- `move_count`: Number of moves made (0-9)
- `player_symbol`: Human player's symbol (X or O)
- `ai_symbol`: AI player's symbol (X or O)
- `is_game_over`: Boolean indicating if game has ended
- `winner`: Winner symbol (X, O, DRAW, or null if ongoing)
- `move_history`: Chronological list of all moves with timestamps
- `created_at`: Game creation timestamp (ISO 8601)
- `updated_at`: Last update timestamp (ISO 8601)
- `metadata`: Optional metadata (agent config, experiment ID, etc.)

**AI Processing State** (transient, not persisted):
- `active_agent`: Currently active agent (scout, strategist, executor, or null)
- `processing_start_time`: When current agent started processing
- `last_error`: Last error encountered (code, message, timestamp)
- `fallback_active`: Whether fallback strategy is currently active

### Game State Machine

The game progresses through a series of well-defined states:

**State Enumeration**:

| State | Description | Valid Transitions | Entry Condition |
|-------|-------------|-------------------|-----------------|
| `NEW` | Game initialized, no moves made | → IN_PROGRESS | Game created, board empty, move_count = 0 |
| `PLAYER_TURN` | Waiting for player input | → AI_TURN, → ERROR | current_player = player_symbol, !is_game_over |
| `AI_TURN` | AI processing move | → AI_SCOUT, → ERROR | current_player = ai_symbol, !is_game_over |
| `AI_SCOUT` | Scout analyzing board | → AI_STRATEGIST, → FALLBACK, → ERROR | AI_TURN entered, Scout invoked |
| `AI_STRATEGIST` | Strategist planning move | → AI_EXECUTOR, → FALLBACK, → ERROR | Scout completed, Strategist invoked |
| `AI_EXECUTOR` | Executor making move | → PLAYER_TURN, → COMPLETED, → FALLBACK, → ERROR | Strategist completed, Executor invoked |
| `FALLBACK` | Using fallback strategy | → PLAYER_TURN, → COMPLETED, → ERROR | Agent timeout/failure occurred |
| `ERROR` | Recoverable error occurred | → PLAYER_TURN, → AI_TURN, → COMPLETED | Validation error, retryable failure |
| `COMPLETED` | Game over (win/draw) | (terminal state) | winner ≠ null OR is_game_over = true |

**State Transitions**:

```
NEW
 ↓
PLAYER_TURN ←→ AI_TURN → AI_SCOUT → AI_STRATEGIST → AI_EXECUTOR
 ↓              ↓          ↓           ↓              ↓
ERROR ←────────┴──────────┴───────────┴──────────────┘
 ↓                                                      ↓
FALLBACK ─────────────────────────────────────────────→ COMPLETED
```

**State Invariants**:

1. **NEW → PLAYER_TURN**: IF player_symbol = X THEN first transition is to PLAYER_TURN
2. **NEW → AI_TURN**: IF ai_symbol = X THEN first transition is to AI_TURN
3. **Turn Alternation**: PLAYER_TURN and AI_TURN must alternate (unless error/fallback)
4. **Agent Sequence**: AI agent states must execute in order: SCOUT → STRATEGIST → EXECUTOR
5. **Terminal State**: COMPLETED is terminal; no transitions allowed after entering
6. **Game Over Condition**: IF winner ≠ null THEN state MUST be COMPLETED
7. **Move Count**: move_count MUST increment by 1 on each successful move
8. **Turn Consistency**: current_player MUST match state (PLAYER_TURN → player_symbol, AI_TURN → ai_symbol)

### State Persistence

**Storage Requirements**:
- Game state MUST be persisted after each move
- State MUST include complete move history
- State MUST be recoverable after system restart
- State MUST support concurrent games (multiple game_id instances)

**Storage Implementations**:
- **In-Memory**: Dictionary/Map keyed by game_id (development, single game)
- **File System**: JSON files in `data/games/{game_id}.json` (simple persistence)
- **Database**: Table with game_id as primary key (production, multiple games)

**State Serialization**:
- State MUST be serializable to JSON (see Section 2.1 GameState Schema)
- All timestamps MUST use ISO 8601 format
- Board MUST serialize as 3x3 array of strings (EMPTY, X, O)
- Move history MUST preserve chronological order

### State Validation

Before persisting or transitioning state, validate:

1. **Schema Validation**: State conforms to GameState JSON Schema (Section 2.1)
2. **State Invariants**: All 8 state validation rules satisfied (Section 4.1)
3. **Transition Validity**: Transition is allowed from current state
4. **Move History Consistency**: move_count matches move_history length
5. **Winner Consistency**: winner value matches board configuration

### State Access Patterns

**Single Source of Truth**:
- Game engine maintains authoritative state
- All layers (agents, API, UI) read from game engine
- Only game engine MUST modify state (via public methods: make_move, reset_game)

**State Queries**:
```
// Read-only state access
state = game_engine.get_current_state()  // Returns GameState copy

// State checks
is_player_turn = game_engine.is_player_turn()
is_game_over = game_engine.is_game_over()
winner = game_engine.get_winner()
available_moves = game_engine.get_available_moves()
```

**State Mutations** (only via game engine):
```
// Mutate state through engine methods
result = game_engine.make_move(position, player)
game_engine.reset_game()
```

### Benefits of State Extraction

1. **Separation of Concerns**: State is independent of game logic, agents, and UI
2. **Testability**: State MUST be testable independently; implementations MUST support mock states for engine tests
3. **Persistence**: Easy to save/load/replay games
4. **Auditing**: Complete history of all state changes
5. **Concurrent Games**: Multiple independent game instances
6. **State Migration**: Easy to evolve state schema over time
7. **Debugging**: Snapshot state at any point for analysis

---

## 4.1 Game Engine Design

### Core Responsibilities

**Game Rules Enforcement**: Validates moves (bounds, empty cell), checks for wins (rows, columns, diagonals), detects draws, manages turn order.

**State Management**: Maintains game state (Section 4), tracks move history, manages player turns, updates game over status.

**Move Application**: Applies validated moves, updates board, switches players, increments move counter, checks for game end.

### Formal Game Rules

#### Board State Definition

**Board Representation**: 3x3 grid with cells indexed (row, col) where both row and col ∈ {0, 1, 2}

**Cell States**: Each cell MUST be in exactly one of three states:
- EMPTY: No symbol placed
- X: Player X's symbol
- O: Player O's symbol

**Game State**: Tuple (Board, CurrentPlayer, MoveCount, IsGameOver, Winner)
- Board: 3×3 matrix of cell states
- CurrentPlayer: X or O
- MoveCount: Integer ∈ [0, 9]
- IsGameOver: Boolean
- Winner: X | O | DRAW | NULL

#### Win Conditions Enumeration

A player wins when they have three of their symbols in any of these 8 winning lines:

| Line Type | Positions | Condition |
|-----------|-----------|-----------|
| Row 0 | (0,0), (0,1), (0,2) | All three cells contain same symbol |
| Row 1 | (1,0), (1,1), (1,2) | All three cells contain same symbol |
| Row 2 | (2,0), (2,1), (2,2) | All three cells contain same symbol |
| Col 0 | (0,0), (1,0), (2,0) | All three cells contain same symbol |
| Col 1 | (0,1), (1,1), (2,1) | All three cells contain same symbol |
| Col 2 | (0,2), (1,2), (2,2) | All three cells contain same symbol |
| Diagonal (main) | (0,0), (1,1), (2,2) | All three cells contain same symbol |
| Diagonal (anti) | (0,2), (1,1), (2,0) | All three cells contain same symbol |

**Win Detection Algorithm**: After each move, check all 8 lines for three matching symbols.

**Acceptance Criteria:**
- Given board with X at (0,0), (0,1), (0,2), when checking win, then winner=X (Row 0)
- Given board with O at (1,0), (1,1), (1,2), when checking win, then winner=O (Row 1)
- Given board with X at (2,0), (2,1), (2,2), when checking win, then winner=X (Row 2)
- Given board with O at (0,0), (1,0), (2,0), when checking win, then winner=O (Col 0)
- Given board with X at (0,1), (1,1), (2,1), when checking win, then winner=X (Col 1)
- Given board with O at (0,2), (1,2), (2,2), when checking win, then winner=O (Col 2)
- Given board with X at (0,0), (1,1), (2,2), when checking win, then winner=X (Diagonal main)
- Given board with O at (0,2), (1,1), (2,0), when checking win, then winner=O (Diagonal anti)
- Given board with 2 X's and 1 O in any line, when checking win, then winner=None (no win)
- Given move completes winning line, when win detection runs, then IsGameOver=true and Winner is set immediately

#### Draw Conditions

A draw MUST be declared in exactly two scenarios:

**1. Complete Draw (Mandatory Detection)**:
- All 9 cells are occupied (MoveCount = 9)
- AND no player has achieved a winning line
- This MUST be detected and enforced

**2. Inevitable Draw (Optional Early Detection)**:
- MoveCount ≥ 7
- AND at least one empty cell remains
- AND no player can achieve a winning line regardless of remaining moves (both players checked for all remaining empty cells)
- Implementation SHOULD detect this early (before move 9) when possible for better UX, but MUST detect by move 9

**Inevitable Draw Detection Algorithm**:

Implementation MUST execute this algorithm:
For each empty cell position P (in order 0,0 to 2,2):
1. MUST temporarily place current player's symbol at P (simulate move without modifying actual board)
2. MUST check if this creates a winning line (check all 8 lines for 3 symbols)
3. MUST temporarily place opponent's symbol at P (simulate opponent move)
4. MUST check if this creates a winning line (check all 8 lines for 3 symbols)
5. MUST repeat steps 1-4 for all remaining empty cells

If NO empty cell (after checking all remaining empty cells) allows either player to win (complete a line with 3 symbols):
- Declare draw immediately (inevitable draw)
- Set IsGameOver = true, Winner = DRAW

**Inevitable Draw Examples**:

Example 1 (Move 8 - inevitable draw):
```
X | O | X
---------
O | X | O
---------
O | X | ?
```
Last cell (2,2): Placing X or O cannot complete any line → Inevitable draw

Example 2 (Move 7 - game continues):
```
X | O | X
---------
O | X | ?
---------
O | ? | ?
```
Cell (1,2): Placing X completes column 2 → Game continues (X can still win)

**Implementation Notes**:
- Inevitable draw detection is OPTIONAL but RECOMMENDED for better UX
- If not implemented, use complete draw detection (MoveCount = 9)
- Inevitable draw typically occurs at MoveCount ∈ {7, 8, 9}
- More complex to implement but prevents meaningless final moves

**Acceptance Criteria:**
- Given MoveCount=9 and no winning line exists, when checking draw, then Winner=DRAW and IsGameOver=true (mandatory complete draw)
- Given MoveCount=8 and no empty cell allows any player to win, when checking inevitable draw, then Winner=DRAW and IsGameOver=true (optional)
- Given MoveCount=7 and at least one empty cell allows a win, when checking draw, then game continues (no draw yet)
- Given MoveCount<9 and winning moves remain, when checking draw, then Winner=None and IsGameOver=false
- Given board state matching Example 1 (inevitable draw at move 8), when checking draw, then Winner=DRAW
- Given board state matching Example 2 (winnable at move 7), when checking draw, then Winner=None

#### Illegal Move Conditions

A move is illegal if ANY of the following conditions are true:

| Condition | Description | Error Code |
|-----------|-------------|------------|
| Out of Bounds | row < 0 OR row > 2 OR col < 0 OR col > 2 | `MOVE_OUT_OF_BOUNDS` |
| Cell Occupied | Board[row][col] ≠ EMPTY | `MOVE_OCCUPIED` |
| Game Over | IsGameOver = true | `GAME_ALREADY_OVER` |
| Invalid Player | Player symbol is not X or O | `E_INVALID_PLAYER` |
| Wrong Turn | Player ≠ CurrentPlayer | `E_INVALID_TURN` |

#### Legal Move Invariants

A move at position (row, col) by player P is legal if and only if ALL of the following are true:
1. 0 ≤ row ≤ 2
2. 0 ≤ col ≤ 2
3. Board[row][col] = EMPTY
4. IsGameOver = false
5. P = CurrentPlayer
6. P ∈ {X, O}

**Acceptance Criteria:**
- Given row=-1, col=1, when validating move, then error=`E_MOVE_OUT_OF_BOUNDS`
- Given row=3, col=1, when validating move, then error=`E_MOVE_OUT_OF_BOUNDS`
- Given row=1, col=-1, when validating move, then error=`E_MOVE_OUT_OF_BOUNDS`
- Given row=1, col=3, when validating move, then error=`E_MOVE_OUT_OF_BOUNDS`
- Given Board[1][1]=X, when attempting move at (1,1), then error=`E_CELL_OCCUPIED`
- Given IsGameOver=true, when attempting move, then error=`E_GAME_ALREADY_OVER`
- Given player='Z', when validating move, then error=`E_INVALID_PLAYER`
- Given CurrentPlayer=X and attempting move with player=O, when validating move, then error=`WRONG_TURN`
- Given row=1, col=1, Board[1][1]=EMPTY, IsGameOver=false, player=CurrentPlayer, when validating move, then move is legal (no error)
- Given all 6 invariants satisfied, when validating move, then returns success and allows move execution

#### Game State Transitions

**Precondition → Action → Postcondition Table**:

| Initial State | Action | Preconditions | Postconditions | Notes |
|---------------|--------|---------------|----------------|-------|
| Empty board | Start game | MoveCount = 0 | CurrentPlayer = X, IsGameOver = false | X always starts |
| In progress | Make legal move | Move is legal (see invariants) | Board updated, CurrentPlayer switches, MoveCount++, check win/draw | Normal gameplay |
| In progress | Make illegal move | Any illegal condition met | State unchanged, error returned | Game continues |
| In progress | Win detected | Move completes winning line | IsGameOver = true, Winner = CurrentPlayer | Game ends |
| In progress | Complete draw detected | MoveCount = 9 AND no winner | IsGameOver = true, Winner = DRAW | Game ends |
| In progress | Inevitable draw detected | MoveCount ≥ 7 AND no winning moves remain | IsGameOver = true, Winner = DRAW | Early draw (optional) |
| Game over | Attempt move | IsGameOver = true | State unchanged, error returned | No moves allowed |
| Any state | Reset game | None | MoveCount = 0, Board = all EMPTY, CurrentPlayer = X, IsGameOver = false, Winner = NULL | Fresh start |

#### Turn Order Rules

**Strict Alternation**:
1. X moves first (move 1)
2. O moves second (move 2)
3. X moves third (move 3)
4. Pattern continues: X on odd moves, O on even moves
5. After each valid move: CurrentPlayer = (CurrentPlayer = X) ? O : X

**Turn Verification**: Before accepting a move, verify:
```
IF MoveCount is even THEN CurrentPlayer MUST be X
IF MoveCount is odd THEN CurrentPlayer MUST be O
```

**Acceptance Criteria:**
- Given MoveCount=0 (new game), when starting game, then CurrentPlayer=X
- Given MoveCount=0 and CurrentPlayer=X, when X makes move, then MoveCount=1 and CurrentPlayer=O
- Given MoveCount=1 and CurrentPlayer=O, when O makes move, then MoveCount=2 and CurrentPlayer=X
- Given MoveCount=2 (even), when verifying turn, then CurrentPlayer=X
- Given MoveCount=3 (odd), when verifying turn, then CurrentPlayer=O
- Given MoveCount=4 (even), when verifying turn, then CurrentPlayer=X
- Given MoveCount=5 (odd), when verifying turn, then CurrentPlayer=O
- Given valid move by CurrentPlayer, when move completes, then CurrentPlayer switches to opponent
- Given X attempts move when CurrentPlayer=O, when validating turn, then error=`WRONG_TURN`

#### Game Termination Conditions

The game terminates when ANY of these conditions become true:

| Condition | Winner Value | IsGameOver | MoveCount Range | Detection |
|-----------|--------------|------------|-----------------|-----------|
| X completes a line | X | true | [5, 9] (min 5 moves for X) | Mandatory |
| O completes a line | O | true | [6, 9] (min 6 moves for O) | Mandatory |
| All cells filled, no winner | DRAW | true | 9 | Mandatory |
| Inevitable draw (no winning moves remain) | DRAW | true | [7, 8, 9] | Optional |

**Minimum Moves to Win**:
- X can win earliest on move 5 (X plays moves 1, 3, 5)
- O can win earliest on move 6 (O plays moves 2, 4, 6)

**Earliest Possible Draw**:
- Complete draw: move 9 (guaranteed)
- Inevitable draw: move 7 (if implemented, rare but possible)

#### State Validation Rules

A valid game state must satisfy ALL of the following:

1. **Symbol Balance**: |count(X) - count(O)| ≤ 1
2. **Move Consistency**: IF count(X) = count(O) THEN CurrentPlayer = X
3. **Move Consistency**: IF count(X) = count(O) + 1 THEN CurrentPlayer = O
4. **Win Uniqueness**: At most one player can have a winning line
5. **Win Finality**: IF winner detected THEN IsGameOver = true
6. **Draw Finality (Complete)**: IF MoveCount = 9 AND no winner THEN Winner = DRAW
7. **Draw Finality (Inevitable)**: IF no winning moves remain AND MoveCount ≥ 7 THEN Winner = DRAW (if implemented)
8. **No Post-Termination Moves**: IF IsGameOver = true on move N THEN no symbols placed after move N

**Acceptance Criteria:**
- Given count(X)=5 and count(O)=3, when validating state, then error=`ERR_INVALID_SYMBOL_BALANCE` (|5-3|=2 > 1)
- Given count(X)=3 and count(O)=3, when validating state, then CurrentPlayer must be X
- Given count(X)=4 and count(O)=3, when validating state, then CurrentPlayer must be O
- Given count(X)=3, count(O)=3, CurrentPlayer=O, when validating state, then error=`ERR_INVALID_TURN_ORDER`
- Given board with X winning line and O winning line, when validating state, then error=`ERR_MULTIPLE_WINNERS`
- Given winner=X detected, when validating state, then IsGameOver must be true
- Given winner=X and IsGameOver=false, when validating state, then error=`ERR_WIN_NOT_FINALIZED`
- Given MoveCount=9 and no winner, when validating state, then Winner must be DRAW
- Given IsGameOver=true on move 5 with winner=X, when checking board, then symbols at moves 6-9 must not exist
- Given valid state satisfying all 8 rules, when validating state, then validation passes with no errors

### Game Engine Interface

The engine exposes methods to:
- Make a move (position and player) - returns success/failure with error code
- Check for winner - returns player or None (checks all 8 lines)
- Check for draw - returns boolean (MoveCount = 9 AND no winner)
- Get available moves - returns list of empty positions
- Validate move - returns boolean and error code if invalid
- Reset game - clears state to initial conditions
- Get current state - returns GameState domain model

The engine is stateless regarding agent coordination; it only manages game rules and state.

**Acceptance Criteria:**
- Given valid position (1,1) and player=X (CurrentPlayer), when make_move() is called, then returns success and board updated
- Given invalid position (3,3), when make_move() is called, then returns failure with error code `E_MOVE_OUT_OF_BOUNDS`
- Given occupied position, when make_move() is called, then returns failure with error code `E_CELL_OCCUPIED`
- Given board with winning line for X, when check_winner() is called, then returns X
- Given board with no winning lines, when check_winner() is called, then returns None
- Given MoveCount=9 and no winner, when check_draw() is called, then returns true
- Given MoveCount<9, when check_draw() is called, then returns false
- Given board with 5 empty cells, when get_available_moves() is called, then returns list of 5 Position objects
- Given board with all cells occupied, when get_available_moves() is called, then returns empty list
- Given valid move, when validate_move() is called, then returns true with no error code
- Given invalid move, when validate_move() is called, then returns false with specific error code
- Given game in progress, when reset_game() is called, then MoveCount=0, Board=all EMPTY, CurrentPlayer=X, IsGameOver=false
- Given any game state, when get_current_state() is called, then returns complete GameState domain model with all properties

---

## 5. API Design

### Transport Abstraction

The application is designed with a layered architecture that separates transport mechanisms from business logic, enabling future extensibility:

**Architecture Layers**:
1. **Game Engine Layer**: Core game logic, rules, and state management (transport-agnostic)
2. **Agent Coordination Layer**: Agent pipeline orchestration and LLM integration (transport-agnostic)
3. **Service Layer**: Business logic orchestration and domain model operations (transport-agnostic)
4. **Transport Layer**: Protocol-specific implementations (REST, WebSocket, GraphQL, CLI, etc.)

**Current Implementation**:
- **Primary Transport**: REST API (HTTP/JSON)
- **Primary Client**: Streamlit Web UI

**Design Principles for Transport Abstraction**:
- **Domain models** (GameState, BoardAnalysis, Strategy, etc.) are transport-agnostic strongly-typed models
- **Service interfaces** define business operations independent of transport protocol
- **Transport adapters** translate protocol-specific requests/responses to/from domain models
- **Client libraries** can be generated from domain models for any transport

**Future Transport Options**:

| Transport Type | Use Case | Implementation Notes |
|----------------|----------|---------------------|
| **WebSocket** | Real-time updates, live game streaming | Add WebSocket endpoints wrapping existing service layer; push game state changes via events |
| **GraphQL** | Flexible queries, mobile clients | GraphQL schema generated from domain models; resolvers call service layer |
| **gRPC** | High-performance inter-service communication | Protocol buffer definitions from domain models; service stubs wrap business logic |
| **CLI** | Command-line interface, automation | CLI commands invoke service layer directly; text-based output rendering |
| **Server-Sent Events (SSE)** | One-way real-time updates | SSE endpoints for game state streaming; lighter than WebSocket |
| **Message Queue** | Asynchronous game processing | Pub/sub for game events; message handlers invoke service layer |

**Extending for New Transports**:

To add a new transport (e.g., WebSocket):

1. **Create Transport Adapter**: Implement WebSocket handlers that:
   - Parse incoming messages into domain models (MoveRequest, etc.)
   - Call existing service layer methods
   - Serialize domain models (MoveResponse, etc.) into WebSocket messages

2. **Maintain Service Layer**: No changes needed to:
   - Game engine logic
   - Agent coordination
   - Domain models
   - Business rules

3. **Add Client Support**: Generate client library if needed:
   - Use domain models for type safety
   - Implement transport-specific connection logic
   - Maintain consistent API semantics

**Service Layer Interface** (Transport-Agnostic):

```
interface GameService {
    make_move(game_state: GameState, position: Position) -> MoveResponse
    get_status() -> GameStatusResponse
    reset_game() -> GameState
    get_history() -> List<MoveHistory>
}

interface AgentService {
    get_agent_status(agent_id: string) -> AgentStatusResponse
    get_agent_metrics(agent_id: string) -> MetricsResponse
}
```

**Benefits of Transport Abstraction**:
- Add new client types without modifying game logic
- Support multiple concurrent transports (REST + WebSocket + CLI)
- Consistent behavior across all transport mechanisms
- Easier testing (test service layer independently of transport)
- Future-proof architecture for evolving client needs

### REST API Endpoints

**Game Management**:
- POST /api/game/move - Make a player move (row, col), returns MoveResponse with game state and AI move
- GET /api/game/status - Get current game status including game state, agent status, and metrics
- POST /api/game/reset - Reset game to initial state
- GET /api/game/history - Get move history

**Acceptance Criteria for POST /api/game/move:**
- Given valid MoveRequest with row=1, col=1, player=X, when POST /api/game/move, then returns 200 with MoveResponse containing updated GameState
- Given invalid MoveRequest with row=3, col=1, when POST /api/game/move, then returns 400 with error_code `E_MOVE_OUT_OF_BOUNDS` and error response schema (status="failure", error_code, message, timestamp, details)
- Given MoveRequest for occupied cell, when POST /api/game/move, then returns 400 with error_code `E_CELL_OCCUPIED` and error response schema
- Given MoveRequest when game is over, when POST /api/game/move, then returns 400 with error_code `E_GAME_ALREADY_OVER` and error response schema
- Given valid player move that doesn't end game, when POST /api/game/move, then response includes AI move execution details
- Given valid player move that completes winning line, when POST /api/game/move, then response has IsGameOver=true and winner set
- Given malformed JSON in request body, when POST /api/game/move, then returns 422 Unprocessable Entity
- Given server error during processing, when POST /api/game/move, then returns 500 with error message

**Acceptance Criteria for GET /api/game/status:**
- Given active game, when GET /api/game/status, then returns 200 with GameStatusResponse containing current GameState
- Given no active game, when GET /api/game/status, then returns 404 Not Found
- Given game with active AI processing, when GET /api/game/status, then response includes agent_status with active_agent field
- Given completed game, when GET /api/game/status, then response includes metrics dictionary with game outcome

**Acceptance Criteria for POST /api/game/reset:**
- Given any game state, when POST /api/game/reset, then returns 200 with new GameState (MoveCount=0, Board=EMPTY, CurrentPlayer=X)
- Given game with move history, when POST /api/game/reset, then move_history is cleared
- Given game reset completes, when POST /api/game/reset, then response includes game_id for new game

**Acceptance Criteria for GET /api/game/history:**
- Given game with 5 moves, when GET /api/game/history, then returns 200 with array of 5 MoveHistory objects in chronological order
- Given game with no moves, when GET /api/game/history, then returns 200 with empty array
- Given each move in history, when GET /api/game/history, then each entry includes: player, position, timestamp, move_number

**Agent Status**:
- GET /api/agents/scout/status - Get Scout agent status and metrics
- GET /api/agents/strategist/status - Get Strategist agent status and metrics
- GET /api/agents/executor/status - Get Executor agent status and metrics

**Acceptance Criteria for Agent Status Endpoints:**
- Given agent is idle, when GET /api/agents/{agent}/status, then returns 200 with status="idle"
- Given agent is processing, when GET /api/agents/{agent}/status, then returns 200 with status="processing" and elapsed_time_ms
- Given agent completed successfully, when GET /api/agents/{agent}/status, then response includes execution_time_ms and success=true
- Given agent failed/timed out, when GET /api/agents/{agent}/status, then response includes error_message and success=false
- Given invalid agent name, when GET /api/agents/{invalid}/status, then returns 404 Not Found

**MCP Protocol** (optional, for distributed mode):
- POST /mcp/{agent_id}/tools/list - List available tools for agent
- POST /mcp/{agent_id}/tools/call - Call a tool on an agent
- GET /mcp/{agent_id}/resources/{resource_id} - Get agent resource

**Configuration** (optional, for programmatic model management):
- GET /api/config/models - Get current LLM model configuration (provider, model name, parameters)
- GET /api/config/models/available - List available models per provider
- POST /api/config/models - Update LLM model configuration (requires game reset to take effect)

**Note**: Model configuration is primarily managed through the UI Configuration Panel, config files, environment variables, or command-line arguments. Configuration API endpoints are optional and primarily useful for programmatic control, external system integration, or observability. Changing models via API should require a game reset to ensure consistency, as model changes affect agent behavior mid-game.

**Acceptance Criteria for Configuration Endpoints:**
- Given valid configuration, when GET /api/config/models, then returns 200 with current provider, model names for all 3 agents
- Given no configuration set, when GET /api/config/models, then returns 200 with default configuration from Section 9
- Given when GET /api/config/models/available, then returns 200 with list of available models grouped by provider (OpenAI, Anthropic, Google)
- Given valid ModelConfigRequest, when POST /api/config/models, then returns 200 with updated configuration and warning about game reset
- Given invalid provider name, when POST /api/config/models, then returns 400 with error `ERR_INVALID_PROVIDER`
- Given invalid model name for provider, when POST /api/config/models, then returns 400 with error `ERR_INVALID_MODEL`
- Given active game in progress, when POST /api/config/models, then returns 409 Conflict with message "Game reset required"

### Request/Response Models

**MoveRequest**: Contains row and column integers (0-2).

**MoveRequest Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `row` | integer | Required, 0 ≤ row ≤ 2 | `E_MOVE_OUT_OF_BOUNDS` | Given row=3 or row=-1, when MoveRequest validated, then reject with E_MOVE_OUT_OF_BOUNDS |
| `col` | integer | Required, 0 ≤ col ≤ 2 | `E_MOVE_OUT_OF_BOUNDS` | Given col=3 or col=-1, when MoveRequest validated, then reject with E_MOVE_OUT_OF_BOUNDS |

**MoveResponse**: Contains success status, position (if successful), updated GameState, AI move execution details (if AI moved), and error message (if failed).

**MoveResponse Data Type Constraints:**

| Field | Type | Constraints | Error Code | Test |
|-------|------|-------------|------------|------|
| `success` | boolean | Required, must be true or false | N/A | Boolean validation (no error code needed) |
| `position` | Position | Required if success=True, must pass Position constraints | N/A | Position validation (uses E_POSITION_OUT_OF_BOUNDS) |
| `updated_game_state` | GameState | Required if success=True, must pass GameState constraints | N/A | GameState validation (uses E_INVALID_BOARD_SIZE, etc.) |
| `ai_move_execution` | MoveExecution | Optional (present if AI moved), must pass MoveExecution constraints | N/A | MoveExecution validation |
| `error_message` | string | Required if success=False, non-empty (length > 0), max length 500 characters | N/A | String validation |
| `fallback_used` | boolean | Optional, if present: must be true or false | N/A | Boolean validation (optional field) |
| `total_execution_time_ms` | float | Optional, if present: total_execution_time_ms ≥ 0.0, precision: 2 decimal places | N/A | Float validation (optional field) |

**GameStatusResponse**: Contains current GameState, agent status dictionary, and metrics dictionary.

All API requests and responses must use strongly-typed, validated models. Implementation approach (typed classes, interfaces, records, etc.) determined by technology stack choice in Section 14.

### Error Response Schema

All API error responses MUST follow the JSON Schema defined in [schemas.md ErrorResponse Schema](./schemas.md#errorresponse-schema).

**Error Response Summary**:
- `status` (string, required): Always "failure" for error responses
- `error_code` (string, required): Error code enum value (see Error Code Enum below)
- `message` (string, required): Human-readable error message
- `timestamp` (string, required): ISO 8601 timestamp (UTC) when error occurred
- `details` (object, optional): Additional error context (field name, expected value, actual value, etc.)

### Error Code Enum

All error codes MUST be defined as enum values. Error codes are organized by category:

**Move Validation Errors**:
- `E_MOVE_OUT_OF_BOUNDS` - Position row/col not in range 0-2
- `E_CELL_OCCUPIED` - Cell at position already contains a symbol
- `E_GAME_ALREADY_OVER` - Attempted move when game is over (IsGameOver=true)
- `E_INVALID_TURN` - Move attempted by wrong player (not current player's turn)
- `E_INVALID_PLAYER` - Player symbol is not X or O

**Game State Errors**:
- `E_GAME_NOT_FOUND` - No active game exists (404)
- `E_STATE_CORRUPTED` - Game state is invalid or corrupted
- `E_INVALID_BOARD_SIZE` - Board size is not 3x3
- `E_INVALID_SYMBOL_BALANCE` - Symbol count imbalance (|count(X) - count(O)| > 1)
- `E_MULTIPLE_WINNERS` - Both players have winning lines (invalid state)
- `E_WIN_NOT_FINALIZED` - Winner set but IsGameOver=false (invalid state)

**Domain Model Validation Errors**:
- `E_POSITION_OUT_OF_BOUNDS` - Position coordinates out of valid range (0-2)
- `E_INVALID_BOARD_SIZE` - Board size validation failed
- `E_INVALID_CONFIDENCE` - Confidence value not in range 0.0-1.0
- `E_INVALID_PRIORITY` - Priority value not in range 1-10
- `E_INVALID_EVAL_SCORE` - Board evaluation score not in range -1.0 to 1.0
- `E_INVALID_RISK_LEVEL` - Risk assessment not one of: low, medium, high
- `E_INVALID_LINE_TYPE` - Line type not one of: 'row', 'column', 'diagonal'
- `E_INVALID_LINE_INDEX` - Line index not in range 0-2
- `E_INVALID_MOVE_TYPE` - Move type not one of: 'center', 'corner', 'edge', 'fork', 'block_fork'
- `E_INVALID_GAME_PHASE` - Game phase not one of: 'opening', 'midgame', 'endgame'
- `E_MISSING_REASONING` - Required reasoning field is empty
- `E_MISSING_PRIMARY_MOVE` - Strategy missing required primary move
- `E_MISSING_DATA` - AgentResult missing required data field
- `E_MISSING_ERROR_MESSAGE` - AgentResult.error() missing error_message
- `E_MISSING_GAME_PLAN` - Strategy missing required game_plan field
- `E_INVALID_EXECUTION_TIME` - Execution time is negative
- `E_INVALID_TIMESTAMP` - Timestamp not in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)

**API Request Errors**:
- `E_API_MALFORMED` - Request body is malformed JSON or missing required fields
- `E_INVALID_PROVIDER` - LLM provider name is invalid (not OpenAI, Anthropic, Google, Ollama)
- `E_INVALID_MODEL` - Model name is invalid for specified provider
- `E_GAME_RESET_REQUIRED` - Configuration change requires game reset (409 Conflict)

**Agent Errors** (internal, may be returned in agent_status):
- `E_SCOUT_FAILED` - Scout agent execution failed
- `E_STRATEGIST_FAILED` - Strategist agent execution failed
- `E_EXECUTOR_FAILED` - Executor agent execution failed
- `E_LLM_TIMEOUT` - LLM API call exceeded timeout (Scout: 5s, Strategist: 5s, Executor: 3s)
- `E_LLM_PARSE_ERROR` - LLM response could not be parsed
- `E_LLM_RATE_LIMIT` - LLM API rate limit exceeded
- `E_LLM_AUTH_ERROR` - LLM API authentication failed (invalid API key)

**System Errors**:
- `E_MCP_CONN_FAILED` - MCP connection failed
- `E_MCP_TIMEOUT` - MCP agent call timed out
- `E_NETWORK_ERROR` - Network connection error
- `E_CONFIG_ERROR` - Configuration error
- `E_SCHEMA_VALIDATION_ERROR` - Schema validation failed

### HTTP Status Code Mapping

Error codes MUST map to HTTP status codes as follows:

| HTTP Status | Error Codes | When Thrown |
|-------------|-------------|-------------|
| **400 Bad Request** | `E_MOVE_OUT_OF_BOUNDS`, `E_CELL_OCCUPIED`, `E_GAME_ALREADY_OVER`, `E_INVALID_TURN`, `E_INVALID_PLAYER`, `E_INVALID_PROVIDER`, `E_INVALID_MODEL`, `E_API_MALFORMED` | Client error: invalid request data or game rules violation |
| **404 Not Found** | `E_GAME_NOT_FOUND` | Resource not found (no active game, invalid agent name) |
| **409 Conflict** | `E_GAME_RESET_REQUIRED` | Operation requires game reset (configuration change during active game) |
| **422 Unprocessable Entity** | `E_POSITION_OUT_OF_BOUNDS`, `E_INVALID_BOARD_SIZE`, `E_INVALID_CONFIDENCE`, `E_INVALID_PRIORITY`, `E_INVALID_EVAL_SCORE`, `E_INVALID_RISK_LEVEL`, `E_MISSING_REASONING`, `E_MISSING_PRIMARY_MOVE`, `E_SCHEMA_VALIDATION_ERROR` | Request is well-formed but contains semantic validation errors |
| **500 Internal Server Error** | `E_STATE_CORRUPTED`, `E_SCOUT_FAILED`, `E_STRATEGIST_FAILED`, `E_EXECUTOR_FAILED`, `E_LLM_TIMEOUT`, `E_LLM_PARSE_ERROR`, `E_LLM_RATE_LIMIT`, `E_LLM_AUTH_ERROR`, `E_MCP_CONN_FAILED`, `E_MCP_TIMEOUT`, `E_NETWORK_ERROR`, `E_CONFIG_ERROR` | Server-side error (agent failures, LLM errors, system errors) |

### Error Response Examples

**Example 1: Invalid Move - Cell Occupied**
```json
{
  "status": "failure",
  "error_code": "E_CELL_OCCUPIED",
  "message": "Cell (1,2) is already occupied",
  "timestamp": "2025-12-28T15:22:34Z",
  "details": {
    "field": "position",
    "expected": "empty cell",
    "actual": "cell contains 'X'",
    "position": {"row": 1, "col": 2}
  }
}
```
HTTP Status: 400 Bad Request

**Example 2: Invalid Move - Out of Bounds**
```json
{
  "status": "failure",
  "error_code": "E_MOVE_OUT_OF_BOUNDS",
  "message": "Position out of bounds (0-2 only)",
  "timestamp": "2025-12-28T15:22:35Z",
  "details": {
    "field": "position",
    "expected": "row and col in range 0-2",
    "actual": {"row": 3, "col": 1}
  }
}
```
HTTP Status: 400 Bad Request

**Example 3: Game Already Over**
```json
{
  "status": "failure",
  "error_code": "E_GAME_ALREADY_OVER",
  "message": "Game is already over. Winner: X",
  "timestamp": "2025-12-28T15:22:36Z",
  "details": {
    "game_state": {
      "is_game_over": true,
      "winner": "X",
      "move_count": 5
    }
  }
}
```
HTTP Status: 400 Bad Request

**Example 4: Game Not Found**
```json
{
  "status": "failure",
  "error_code": "E_GAME_NOT_FOUND",
  "message": "No active game found",
  "timestamp": "2025-12-28T15:22:37Z"
}
```
HTTP Status: 404 Not Found

**Example 5: Malformed Request**
```json
{
  "status": "failure",
  "error_code": "E_API_MALFORMED",
  "message": "Invalid request: missing required field 'row'",
  "timestamp": "2025-12-28T15:22:38Z",
  "details": {
    "field": "row",
    "expected": "integer in range 0-2",
    "actual": "missing"
  }
}
```
HTTP Status: 400 Bad Request

**Example 6: LLM Timeout (Internal Error)**
```json
{
  "status": "failure",
  "error_code": "E_LLM_TIMEOUT",
  "message": "AI is taking longer than expected. Using quick analysis...",
  "timestamp": "2025-12-28T15:22:39Z",
  "details": {
    "agent": "scout",
    "timeout_duration_ms": 5000,
    "retry_count": 3,
    "fallback_used": true
  }
}
```
HTTP Status: 500 Internal Server Error (Note: This error is typically handled internally with fallback, but may be returned in agent_status)

**Example 7: Schema Validation Error**
```json
{
  "status": "failure",
  "error_code": "E_SCHEMA_VALIDATION_ERROR",
  "message": "Invalid confidence value: must be 0.0-1.0",
  "timestamp": "2025-12-28T15:22:40Z",
  "details": {
    "field": "confidence",
    "expected": "float in range 0.0-1.0",
    "actual": 1.5
  }
}
```
HTTP Status: 422 Unprocessable Entity

### Error Code Usage Rules

1. **All API error responses MUST include**: status="failure", error_code, message, timestamp
2. **Error codes MUST be from the Error Code Enum** (no custom error codes)
3. **HTTP status codes MUST match the mapping table** above
4. **Details field is optional** but SHOULD be included when it provides useful context (field name, expected/actual values)
5. **Error messages MUST be human-readable** and user-friendly (non-technical language for client-facing errors)
6. **Internal agent errors** (E_SCOUT_FAILED, E_LLM_TIMEOUT, etc.) are typically handled with fallbacks and not returned to client, but may appear in agent_status responses

---

## 6. Web UI Functional Requirements

This section defines **what** the UI must do (functional requirements). Visual design specifications (colors, animations, layouts, typography, spacing) will be provided separately as Figma designs.

### User Stories: Game Board

**US-001: Display Game Board**
- As a player, I MUST see a 3x3 grid representing the game board
- The board MUST display current cell states (EMPTY, X, or O)
- The board MUST update immediately when game state changes

**US-002: Make Player Move**
- As a player, I MUST be able to click any empty cell to make a move
- The UI MUST disable the board during AI turn
- The UI MUST show validation errors for invalid moves (occupied cell, out of bounds)

**Acceptance Criteria for Board Interaction:**

**Click Handling on Empty Cells:**
- Given game is waiting for player input (CurrentPlayer=player_symbol, IsGameOver=false), when player clicks empty cell at position (row, col), then UI MUST send POST /api/game/move request with row and col, board MUST be disabled (opacity=0.6, cursor=not-allowed) during API call, board MUST re-enable after response received
- Given empty cell at (1,1), when player clicks cell, then click event MUST be processed, API request MUST be sent within 50ms of click, cell MUST show loading indicator (spinner or pulse animation) until response received

**Click Handling on Occupied Cells (Guard):**
- Given game is waiting for player input (CurrentPlayer=player_symbol, IsGameOver=false), when player clicks non-empty cell (cell contains 'X' or 'O'), then click MUST be ignored (no API request sent), UI MUST display toast notification with message="Cell occupied", severity="warning", toast MUST auto-dismiss after 3 seconds, board state MUST remain unchanged
- Given occupied cell at (0,0) with 'X', when player clicks cell, then no POST /api/game/move request is sent, toast notification appears within 100ms, toast shows warning icon and "Cell occupied" message

**Click Handling During AI Turn (Guard):**
- Given game is in AI turn (CurrentPlayer=ai_symbol OR active_agent is not null), when player clicks any cell (empty or occupied), then click MUST be ignored (no API request sent), board MUST remain disabled (opacity=0.6, cursor=not-allowed), no toast notification shown
- Given AI is processing (active_agent="scout" or "strategist" or "executor"), when player clicks cell at (1,1), then no POST /api/game/move request is sent, board remains disabled, no visual feedback for click

**Click Handling When Game Over (Guard):**
- Given game is over (IsGameOver=true), when player clicks any cell, then click MUST be ignored (no API request sent), board MUST remain disabled (opacity=0.6, cursor=not-allowed), no toast notification shown
- Given game over with winner='X', when player clicks cell at (1,1), then no POST /api/game/move request is sent, board remains disabled

**API Error Handling:**
- Given player clicks empty cell, when POST /api/game/move returns 400 with error_code=`E_CELL_OCCUPIED`, then UI MUST display toast notification with message="Cell already occupied", severity="error", toast MUST auto-dismiss after 5 seconds, board MUST re-enable (opacity=1.0, cursor=pointer)
- Given player clicks empty cell, when POST /api/game/move returns 400 with error_code=`E_MOVE_OUT_OF_BOUNDS`, then UI MUST display toast notification with message="Position out of bounds (0-2 only)", severity="error", toast MUST auto-dismiss after 5 seconds
- Given player clicks empty cell, when POST /api/game/move returns 400 with error_code=`E_GAME_ALREADY_OVER`, then UI MUST display toast notification with message="Game is already over", severity="info", toast MUST auto-dismiss after 5 seconds
- Given player clicks empty cell, when POST /api/game/move returns 500 (server error), then UI MUST display toast notification with message="Server error. Please try again.", severity="error", toast MUST auto-dismiss after 5 seconds, board MUST re-enable

**US-003: View Last Move**
- As a player, I MUST see which move was made most recently
- The last move indicator MUST update after each player or AI move

**US-004: View Current Turn**
- As a player, I MUST know whose turn it is (player or AI)
- The current turn indicator MUST update after each move

**Acceptance Criteria for Current Turn Indicator:**

**Visibility and Accuracy:**
- Given game is active (IsGameOver=false), when board is rendered, then current turn indicator MUST be visible (display not 'none', opacity=1.0), indicator MUST show correct player symbol ('X' or 'O') matching CurrentPlayer from GameState, indicator MUST be visible within 100ms after board render completes
- Given CurrentPlayer='X', when board is rendered, then turn indicator displays "X's Turn" or "Player X's Turn" with color #e94560 (Player X color), indicator is visible within 100ms
- Given CurrentPlayer='O', when board is rendered, then turn indicator displays "O's Turn" or "AI's Turn" with color #00adb5 (Player O/AI color), indicator is visible within 100ms

**Update Timing:**
- Given player makes move, when POST /api/game/move returns success with updated GameState, then current turn indicator MUST update to show new CurrentPlayer within 100ms of response received, indicator MUST reflect AI turn (CurrentPlayer=ai_symbol) immediately
- Given AI makes move, when game state updates (CurrentPlayer switches to player_symbol), then current turn indicator MUST update to show player turn within 100ms of state update, indicator MUST reflect player turn (CurrentPlayer=player_symbol) immediately

**Game Over State:**
- Given game is over (IsGameOver=true), when board is rendered, then current turn indicator MUST display "Game Over" or winner message ("X Wins", "O Wins", "Draw"), indicator MUST be visible, turn indicator MUST NOT show "X's Turn" or "O's Turn" when game is over
- Given game over with winner='X', when board is rendered, then turn indicator displays "X Wins" with color #e94560, indicator is visible within 100ms

**State Consistency:**
- Given CurrentPlayer='X' from GameState, when turn indicator is displayed, then indicator text MUST match CurrentPlayer exactly, indicator color MUST match player symbol color (#e94560 for X, #00adb5 for O), indicator MUST NOT show stale/previous turn information

**US-005: View Game Status**
- As a player, I MUST see the current move number
- As a player, I MUST see if the game is over
- As a player, I MUST see who won (X, O, or DRAW) when game ends

### User Stories: Move History

**US-006: View Move History**
- As a player, I MUST see a chronological list of all moves made
- Each move entry MUST show: player/AI indicator, move number, position, timestamp

**US-007: View Move Details**
- As a player, I MUST be able to expand any move to see agent reasoning
- Agent reasoning MUST show Scout analysis, Strategist strategy, and Executor execution details

### User Stories: Agent Insights

**US-008: View Agent Analysis**
- As a player, I MUST see real-time Scout analysis (threats, opportunities, strategic moves)
- As a player, I MUST see real-time Strategist strategy (recommended move, reasoning, priority)
- As a player, I MUST see real-time Executor execution (validation, success status, timing)

**Acceptance Criteria for Agent Insights Panel:**

**Scout Agent Metrics Panel (Required Fields):**
- Given Scout agent completes analysis, when Agent Insights Panel displays Scout metrics, then panel MUST show execution_time (float, precision: 2 decimal places, unit: milliseconds), panel MUST show confidence (float, 0.0-1.0, precision: 2 decimal places) from highest priority opportunity or strategic move, panel MUST show priority (integer, 1-10 or enum value) from highest priority move, panel MUST NOT show optional fields as empty/null (only required fields displayed)
- Given Scout returns BoardAnalysis with opportunities list containing priority=100, confidence=0.95, when Scout metrics panel is displayed, then execution_time is shown (e.g., "1234.56 ms"), confidence is shown (e.g., "0.95"), priority is shown (e.g., "100" or "IMMEDIATE_WIN"), no optional/empty fields are displayed

**Strategist Agent Metrics Panel (Required Fields):**
- Given Strategist agent completes planning, when Agent Insights Panel displays Strategist metrics, then panel MUST show execution_time (float, precision: 2 decimal places, unit: milliseconds), panel MUST show confidence (float, 0.0-1.0, precision: 2 decimal places) from primary_move, panel MUST show priority (integer, 1-10 or enum value) from primary_move, panel MUST NOT show optional fields as empty/null (only required fields displayed)
- Given Strategist returns Strategy with primary_move.priority=90, primary_move.confidence=0.90, when Strategist metrics panel is displayed, then execution_time is shown (e.g., "2345.67 ms"), confidence is shown (e.g., "0.90"), priority is shown (e.g., "90" or "BLOCK_THREAT"), no optional/empty fields are displayed

**Executor Agent Metrics Panel (Required Fields):**
- Given Executor agent completes execution, when Agent Insights Panel displays Executor metrics, then panel MUST show execution_time (float, precision: 2 decimal places, unit: milliseconds), panel MUST show confidence (float, 0.0-1.0, precision: 2 decimal places) from MoveExecution (if available), panel MUST show priority (integer, 1-10 or enum value) from actual_priority_used, panel MUST NOT show optional fields as empty/null (only required fields displayed)
- Given Executor returns MoveExecution with actual_priority_used=80, execution_time_ms=567.89, when Executor metrics panel is displayed, then execution_time is shown (e.g., "567.89 ms"), priority is shown (e.g., "80" or "FORCE_WIN"), confidence is shown if available from MoveExecution, no optional/empty fields are displayed

**Panel Visibility:**
- Given agent is processing (active_agent="scout" or "strategist" or "executor"), when Agent Insights Panel is displayed, then panel for active agent MUST be visible (display not 'none'), panel MUST show loading indicator (spinner or progress bar), panel MUST show "Processing..." or agent name with "Processing" status
- Given all agents completed, when Agent Insights Panel is displayed, then all three agent panels (Scout, Strategist, Executor) MUST be visible, each panel MUST show required fields (execution_time, confidence, priority), panels MUST NOT show loading indicators

**Field Format Requirements:**
- Given execution_time=1234.567, when displayed in metrics panel, then value MUST be formatted as "1234.57 ms" (2 decimal places, unit suffix)
- Given confidence=0.95, when displayed in metrics panel, then value MUST be formatted as "0.95" or "95%" (2 decimal places or percentage)
- Given priority=100, when displayed in metrics panel, then value MUST be formatted as "100" or "IMMEDIATE_WIN" (numeric or enum name)

**US-009: View Agent Processing Status**
- As a player, I MUST see which agent is currently active
- As a player, I MUST see loading indication while agents are processing
- As a player, I MUST see estimated time remaining for AI move

**US-010: View Agent Timeout Progress**
- As a player, I MUST see progressive status updates as processing time increases:
  - At 0-2s: Basic loading indication
  - At 2-5s: Processing indication
  - At 5-10s: Detailed progress with elapsed time
  - At 10-15s: Warning indication with fallback preparation notice
  - At 15s+: Automatic fallback execution with explanation

**US-011: Force Agent Fallback**
- As a player, I MUST be able to force fallback after 10 seconds of waiting
- The UI MUST provide a "Force Fallback" action
- The UI MUST explain what fallback strategy will be used

**US-012: Retry Failed Agent**
- As a player, I MUST be able to retry with a different model when agent fails
- The UI MUST provide retry options on agent timeout/failure

### User Stories: Post-Game Metrics

**US-013: View Metrics After Game**
- As a player, I MUST be able to view detailed metrics after game completion
- Metrics MUST only be available/displayed when game is over (win, loss, or draw)

**US-014: View Agent Communication**
- As a player, I MUST see coordinator requests to each agent
- As a player, I MUST see agent responses and results
- As a player, I MUST see input/output data structures for each agent call

**US-015: View LLM Interactions**
- As a player, I MUST see LLM API calls made by each agent
- As a player, I MUST see request prompts sent to LLM
- As a player, I MUST see LLM responses received
- As a player, I MUST see token usage per LLM call
- As a player, I MUST see response times for each LLM interaction
- As a player, I MUST see model/provider information for each call

**US-016: View Agent Configuration**
- As a player, I MUST see agent mode used (local or distributed MCP)
- As a player, I MUST see LLM framework used
- As a player, I MUST see agent initialization details
- As a player, I MUST see mode switching events (if any)

**US-017: View Performance Summary**
- As a player, I MUST see per-agent execution times (min, max, average)
- As a player, I MUST see total LLM calls per agent
- As a player, I MUST see total token usage
- As a player, I MUST see success/failure rates
- As a player, I MUST see error details (if any)

**US-018: View Game Summary**
- As a player, I MUST see total moves
- As a player, I MUST see game duration
- As a player, I MUST see win/loss/draw outcome
- As a player, I MUST see average move time

### User Stories: Configuration

**US-019: Select LLM Provider and Model**
- As a player, I MUST be able to select LLM provider (OpenAI, Anthropic, Google Gemini)
- As a player, I MUST be able to select model name
- My LLM preferences MUST be saved and restored in future sessions

**US-020: Select Agent Mode**
- As a player, I MUST be able to toggle between local mode and distributed MCP mode
- As a player, I MUST be able to select LLM framework (LangChain, LiteLLM, Instructor, Direct SDKs)

**US-021: Configure Game Settings**
- As a player, I MUST be able to reset the game
- As a player, I MUST be able to change player symbol (X or O)
- As a player, I SHOULD be able to adjust difficulty (if implemented)

### User Stories: Real-Time Updates

**US-022: Automatic State Updates**
- As a player, the UI MUST update automatically when I make a move
- As a player, the UI MUST update automatically when AI makes a move
- As a player, the UI MUST update automatically when game state changes
- As a player, the UI MUST update automatically when agent metrics update

**US-023: Performance Requirements**
- The UI MUST prevent unnecessary re-renders
- The UI MUST maintain user context across updates
- Board updates MUST be reflected within 100ms of state change
- Agent status updates MUST be reflected within 500ms

### User Stories: Error Handling

**US-024: Display Error Messages**
- As a player, I MUST see clear error messages for invalid moves
- As a player, I MUST see error messages for agent failures
- As a player, I MUST see error messages for network issues
- Error messages MUST follow the Failure Matrix specifications (Section 12)

**US-025: Fallback Indication**
- As a player, I MUST be notified when fallback strategies are used
- As a player, I MUST understand why fallback was triggered
- As a player, I MUST see which fallback strategy was applied

### Definition of Done

All user stories (US-001 through US-025) are considered complete when they meet the following criteria:

**Functional Requirements:**
- ✅ Feature works as described in the user story
- ✅ All edge cases handled per error handling specification (Section 12)
- ✅ API integration tested and working
- ✅ Unit tests written and passing
- ✅ Integration tests cover user workflows

**Visual Requirements:**
- ✅ Implementation matches ui-spec.md specifications exactly
  - Colors from design system (Section: Color Palette)
  - Typography follows specified font families, sizes, and weights
  - Spacing uses 8px grid system (Section: Spacing)
  - Border radius matches specifications (6px, 12px, 16px)
  - Shadows follow elevation system (Section: Shadows)
  - Animations match specified keyframes and timing
- ✅ Component states properly styled (hover, active, disabled, error, success)
- ✅ Visual regression tests pass (if implemented)
- ✅ Designer approval obtained (code review or sign-off)

**Quality Requirements:**
- ✅ Code review completed and approved
- ✅ No console errors or warnings in browser
- ✅ No accessibility violations (WCAG 2.1 Level AA guidelines)
- ✅ Performance requirements met (Section 6, US-023)
  - Board updates within 100ms
  - Agent status updates within 500ms
- ✅ Cross-browser testing completed (Chrome, Firefox, Safari)

**Documentation Requirements:**
- ✅ Code comments added for complex logic
- ✅ API endpoints documented (if new endpoints added)
- ✅ Configuration changes documented (if applicable)

**Verification Methods:**

1. **Manual Testing:**
   - Test user story acceptance criteria
   - Visual comparison with ui-spec.md and preview files
   - Test all interactive states (hover, click, focus)
   - Test error scenarios from Failure Matrix (Section 12)

2. **Automated Testing:**
   - Unit tests for component logic
   - Integration tests for API interactions
   - Visual regression tests (recommended: Percy, Chromatic, or Playwright screenshots)
   - Accessibility tests (recommended: axe-core, pa11y)

3. **Code Review Checklist:**
   - [ ] Functional requirements from user story implemented
   - [ ] UI matches ui-spec.md (colors, typography, spacing, animations)
   - [ ] Error handling follows Section 12 Failure Matrix
   - [ ] Performance meets requirements (US-023)
   - [ ] No hard-coded values (use CSS variables from design system)
   - [ ] Responsive behavior tested (if applicable)
   - [ ] Accessibility attributes present (ARIA labels, roles, keyboard navigation)

4. **Designer QA:**
   - Visual inspection against ui-spec.md
   - Interaction behavior matches specifications
   - Animation timing and easing correct
   - Color accuracy verified
   - Typography rendering correct

**Example Acceptance Criteria for US-001 (Display Game Board):**

Functional:
- [ ] 3x3 grid rendered correctly
- [ ] Cell states (EMPTY, X, O) displayed
- [ ] Board updates when game state changes

Visual (per ui-spec.md):
- [ ] Cell dimensions: 100px × 100px
- [ ] Gap between cells: 12px
- [ ] Board background: #0f3460 (Card color)
- [ ] Board border-radius: 16px
- [ ] X symbol color: #e94560 (Player X)
- [ ] O symbol color: #00adb5 (Player O)
- [ ] Cell border: 2px solid #533483 (Grid Lines)
- [ ] Cell border-radius: 6px
- [ ] Empty cell background: #16213e (Surface)
- [ ] X/O font-size: 2.5rem
- [ ] X/O font-weight: 700 (Bold)

Quality:
- [ ] No layout shift on state changes
- [ ] Smooth transitions (0.2s ease)
- [ ] Keyboard accessible
- [ ] Screen reader announces cell states

**Non-Functional Acceptance:**
- Tests do not need 100% code coverage, but critical paths must be tested
- Visual design can have minor deviations (±2px, slight color variance) if approved by designer
- Performance targets are goals; reasonable variance acceptable with justification

---

## 6.1 UI Visual Design Specification

**Note**: Visual design specifications (colors, animations, layouts, typography, spacing, component styling) are defined separately in [docs/ui/ui-spec.md](./ui/ui-spec.md) with an interactive HTML preview. The visual designs reference the user story IDs above (US-001 through US-025) to maintain traceability between functional requirements and visual design.

Visual elements mentioned in Section 12 (Failure Matrix UI Indications) provide guidance for error state presentation but exact styling is documented in ui/ui-spec.md.

**Figma Frames Location**: Exported PNG frames should be placed in `docs/ui/frames/` directory.

---

## 6.2 Accessibility Requirements

The application MUST comply with **WCAG 2.1 Level AA** accessibility guidelines to ensure the game is usable by people with disabilities, including those using assistive technologies.

### Quick Wins (Essential Requirements)

These are high-impact, low-effort accessibility improvements that MUST be implemented:

**1. Alternative Text and Labels**

All interactive elements MUST have descriptive labels or alternative text:

- Game board cells: `aria-label="Row 1, Column 1, Empty"` or `aria-label="Row 2, Column 2, X"`
- Buttons: Use descriptive text or `aria-label` (e.g., "New Game", "Undo Move")
- Agent status indicators: `aria-label="Scout agent processing"` or `aria-label="Strategist agent complete"`
- Icons: All icons MUST have text alternatives via `aria-label` or visually hidden text
- Images: All images MUST have descriptive `alt` attributes (decorative images: `alt=""`)

Example:
```html
<button class="cell" aria-label="Row 1, Column 1, Empty">
  <!-- Cell content -->
</button>

<button aria-label="Start new game">
  <span aria-hidden="true">🎮</span>
  New Game
</button>
```

**2. Keyboard Navigation**

All functionality MUST be accessible via keyboard alone (no mouse required):

- **Tab**: Navigate between interactive elements in logical order
- **Shift+Tab**: Navigate backwards
- **Enter/Space**: Activate buttons and select cells
- **Arrow keys**: Navigate between game board cells (grid navigation)
- **Escape**: Close modals, cancel actions, return to previous state

Game board cell navigation:
- Arrow Right/Left: Move focus horizontally between cells
- Arrow Up/Down: Move focus vertically between cells
- Enter/Space: Make move in focused cell

Tab order MUST follow logical flow:
1. Main navigation tabs (Play, Config, Metrics)
2. Game board cells (row by row: 0,0 → 0,1 → 0,2 → 1,0...)
3. Game controls (New Game, Undo)
4. Configuration controls
5. Metrics tabs and content

**3. Focus Indicators**

All focusable elements MUST have visible focus indicators:

- Focus outline MUST be clearly visible (minimum 3px solid outline)
- Focus outline MUST have high contrast against background
- Focus outline MUST NOT be removed with `outline: none` without providing alternative
- Use `:focus-visible` to show focus only for keyboard navigation (not mouse clicks)

Example:
```css
.cell:focus-visible {
  outline: 3px solid #00adb5;
  outline-offset: 2px;
  box-shadow: 0 0 0 5px rgba(0, 173, 181, 0.2);
}

button:focus-visible {
  outline: 3px solid #00adb5;
  outline-offset: 2px;
}
```

Default browser focus indicators are acceptable but custom focus styles are preferred for better visibility.

**4. Semantic HTML**

Use proper HTML5 semantic elements to provide structure and meaning:

- `<main>`: Main content area (game board and panels)
- `<nav>`: Navigation (main tabs: Play, Config, Metrics)
- `<section>`: Major content sections (game board section, agent insights section)
- `<article>`: Self-contained content (move history entries)
- `<header>`: Page header with title
- `<button>`: Interactive elements that trigger actions (NOT `<div>` with click handlers)
- `<table>`: Tabular data (metrics table, performance summary)
- `<form>`: Configuration inputs (NOT just `<div>` containers)

Example structure:
```html
<header>
  <h1>Tic-Tac-Toe Multi-Agent Game</h1>
</header>

<nav aria-label="Main navigation">
  <button>Play</button>
  <button>Config</button>
  <button>Metrics</button>
</nav>

<main>
  <section aria-label="Game board">
    <!-- Game board content -->
  </section>

  <section aria-label="Agent insights">
    <!-- Agent insights content -->
  </section>
</main>
```

**5. ARIA Live Regions**

Dynamic content updates MUST be announced to screen readers using ARIA live regions:

- **Game status**: `<div role="status" aria-live="polite">It's your turn</div>`
- **AI moves**: `<div role="status" aria-live="polite">AI placed O in row 2, column 2</div>`
- **Agent updates**: `<div role="status" aria-live="polite">Scout agent is analyzing</div>`
- **Errors**: `<div role="alert" aria-live="assertive">Invalid move: cell is occupied</div>`
- **Game over**: `<div role="alert" aria-live="assertive">Game over. You won!</div>`

Use appropriate politeness levels:
- `aria-live="polite"`: Non-critical updates (agent status, moves)
- `aria-live="assertive"`: Important updates (errors, game over)

Example:
```html
<!-- Game status announcements -->
<div role="status" aria-live="polite" aria-atomic="true" class="sr-only">
  <span id="game-status">It's your turn</span>
</div>

<!-- Error announcements -->
<div role="alert" aria-live="assertive" aria-atomic="true" class="sr-only">
  <span id="error-message"></span>
</div>

<!-- Agent processing status -->
<div role="status" aria-live="polite">
  <span>Scout agent is analyzing the board</span>
</div>
```

**6. Browser Zoom Support**

The UI MUST remain functional and usable at 200% zoom:

- Layout MUST NOT break or cause horizontal scrolling at 200% zoom
- Text MUST remain readable and NOT overlap
- Interactive elements MUST remain clickable and NOT be cut off
- Use responsive units (rem, em, %) instead of fixed pixels for font sizes
- Test at zoom levels: 100%, 150%, 200%

Example:
```css
/* Use rem for font sizes */
.cell {
  font-size: 2.5rem; /* Scales with browser zoom */
}

/* Use flexible layouts */
.game-board {
  max-width: 100%;
  display: grid;
  grid-template-columns: repeat(3, minmax(80px, 1fr));
}
```

**7. Lighthouse Accessibility Audit**

Run Chrome DevTools Lighthouse accessibility audit and achieve minimum score of 90:

**How to run:**
1. Open Chrome DevTools (F12)
2. Navigate to "Lighthouse" tab
3. Select "Accessibility" category
4. Click "Generate report"
5. Fix all issues with severity "Error" or "Warning"

**Common issues to fix:**
- Missing `alt` attributes on images
- Low color contrast ratios
- Missing form labels
- Duplicate IDs
- Missing ARIA attributes
- Links without discernible text

**Target:**
- Accessibility score: ≥ 90 (green)
- Zero errors with severity "Error"
- Address all warnings where feasible

**8. Skip Links**

Provide "Skip to main content" link as the first focusable element:

```html
<a href="#main-content" class="skip-link">
  Skip to main content
</a>

<main id="main-content">
  <!-- Main content -->
</main>
```

CSS for skip link (visible only on focus):
```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #00adb5;
  color: #1a1a2e;
  padding: 8px 16px;
  text-decoration: none;
  border-radius: 0 0 4px 0;
  z-index: 1000;
}

.skip-link:focus {
  top: 0;
}
```

This allows keyboard users to bypass navigation and jump directly to main content.

### Additional Accessibility Guidelines

Beyond the 8 quick wins, consider these additional improvements:

**Screen Reader Testing:**
- Test with NVDA (Windows) or VoiceOver (Mac)
- Verify all content is announced correctly
- Verify navigation is logical and efficient
- Test move announcements: "You placed X in row 1, column 1"

**Color and Contrast:**
- Verify color contrast ratios meet WCAG AA standards:
  - Normal text: 4.5:1 minimum
  - Large text (18pt+): 3:1 minimum
  - UI components: 3:1 minimum
- Do NOT rely on color alone to convey information
- Use icons + text + color for status indicators

**Motion and Animations:**
- Respect `prefers-reduced-motion` media query
- Disable or reduce animations for users who prefer reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**Form Accessibility:**
- Associate all labels with inputs using `for` attribute
- Use `aria-describedby` for help text and error messages
- Use `aria-invalid="true"` for invalid inputs
- Group related inputs with `<fieldset>` and `<legend>`

**Testing Tools:**
- **Automated:** axe DevTools, pa11y, Lighthouse
- **Manual:** Screen readers (NVDA, VoiceOver), keyboard-only navigation
- **Simulators:** Color blindness simulators, zoom testing

### Acceptance Criteria for Accessibility

All user stories MUST meet these accessibility criteria to be considered complete:

- [ ] All interactive elements have descriptive labels or alternative text
- [ ] All functionality works with keyboard alone (no mouse required)
- [ ] All focusable elements have visible focus indicators
- [ ] Semantic HTML5 elements used throughout
- [ ] ARIA live regions announce dynamic content updates
- [ ] UI remains functional at 200% browser zoom
- [ ] Lighthouse accessibility score ≥ 90
- [ ] Skip link provided for keyboard navigation
- [ ] No WCAG 2.1 Level AA violations
- [ ] Tested with screen reader (NVDA or VoiceOver)

---

## 7. Project Structure

### Directory Organization

**schemas/**: Domain models (strongly-typed, validated):
- game: Core game models (Position, Board, GameState)
- analysis: Scout agent models (Threat, Opportunity, StrategicMove, BoardAnalysis)
- strategy: Strategist agent models (MovePriority enum, MoveRecommendation, Strategy)
- execution: Executor agent models (ValidationError, MoveExecution)
- results: Result wrapper models (AgentResult)
- api: API request/response models

Note: Domain models must be strongly-typed with runtime validation. Implementation approach (typed classes, interfaces, records, structs, etc.) determined by Section 14. MovePriority enum defines 8 priority levels (IMMEDIATE_WIN=100, BLOCK_THREAT=90, FORCE_WIN=80, PREVENT_FORK=70, CENTER_CONTROL=50, CORNER_CONTROL=40, EDGE_PLAY=30, RANDOM_VALID=10) - see Section 3 for full priority system specification.

**agents/**: Agent implementations:
- interfaces: Abstract base classes and protocols
- scout_local: Local Scout implementation using configured LLM framework
- strategist_local: Local Strategist implementation using configured LLM framework
- executor_local: Local Executor implementation using configured LLM framework
- scout_mcp: Scout with MCP protocol support
- strategist_mcp: Strategist with MCP protocol support
- executor_mcp: Executor with MCP protocol support
- base_mcp_agent: Base class for MCP protocol support

Note: Agents use an LLM framework abstraction layer that supports multiple providers. LLM framework choice (LangChain, LiteLLM, Instructor, Direct SDKs) determines the multi-provider abstraction implementation - see Section 19.

**game/**: Game logic:
- engine: Core game rules and state management
- coordinator: Orchestrates agent pipeline
- state: Game state management (if separate from engine)

**services/**: Service layer (transport-agnostic business logic):
- game_service: Game operations (make_move, get_status, reset, history)
- agent_service: Agent operations (status, metrics)
- interfaces: Service interface definitions

**api/**: REST API transport layer:
- main: API application setup and routes
- routes/game: Game management REST endpoints (wraps game_service)
- routes/agents: Agent status REST endpoints (wraps agent_service)
- routes/mcp: MCP protocol endpoints (optional)
- adapters/rest_adapter: Converts REST requests/responses to/from domain models

Note: REST endpoints are thin wrappers around service layer. Implementation framework choice determined by Section 14. Future transports (WebSocket, GraphQL, CLI) would add new directories with their own adapters.

**ui/**: Web-based UI application:
- main_app: Main UI application entry point
- components/board: Game board component
- components/metrics: Metrics dashboard component
- components/insights: Agent insights component

Note: UI framework choice determined by Section 14.

**models/**: LLM management:
- shared_llm: Shared LLM connection manager with pooling
- factory: LLM provider factory supporting multi-provider frameworks
- provider_adapter: Abstraction layer for different LLM frameworks

**utils/**: Utilities:
- config: Configuration management
- validators: Validation helpers

**tests/**: Test suite:
- test_game_engine: Game logic tests
- test_agents: Agent tests
- test_api: API endpoint tests
- test_integration: End-to-end tests

**docs/**: Documentation:
- ARCHITECTURE.md: System architecture
- API.md: API documentation
- USER_GUIDE.md: User guide
- spec.md: This specification document

**config/**: Configuration files:
- config.json: Main configuration
- .env.example: Environment variables template

---

## 8. System Dependencies and Environment

### Required Capabilities

The implementation must provide:

**API Layer:**
- REST API support with async operations
- Request/response validation
- OpenAPI/Swagger documentation
- CORS support for web clients

**Data Validation:**
- Strongly-typed domain models
- Runtime validation
- Serialization/deserialization
- Schema documentation

**UI Layer:**
- Web-based interface
- API client functionality
- Real-time updates
- Component-based architecture

**LLM Integration:**
- Multi-provider support (OpenAI, Anthropic, Google Gemini)
- Connection pooling and reuse
- Hot-swappable providers via configuration
- Async LLM calls

**Testing:**
- Unit testing framework
- Integration testing support
- API testing capabilities
- Async test support

**Development Tools:**
- Type checking
- Code formatting
- Linting
- Dependency management

### Environment Requirements

**Runtime Environment:**
- Programming language with async/await support
- HTTP server capability
- Environment variable management
- Configuration file parsing (JSON, YAML, etc.)

**External Services:**
- LLM Provider APIs (at least one of: OpenAI, Anthropic, Google Gemini)
- Optional: MCP-compatible agent services (for distributed mode)

**Development Environment:**
- Version control (Git)
- Package manager
- Virtual environment or containerization
- CI/CD pipeline support

See Section 14 for recommended specific technologies that meet these requirements.

---

## 9. Configuration Management

### Configuration Structure

**Agent Framework Configuration**: Mode selection (local or distributed_mcp), LLM framework selection for multi-provider support (see Section 19), model selection per agent or shared, timeout settings per agent (Scout: 5s, Strategist: 5s, Executor: 3s in local mode; 10s/10s/5s in distributed mode), retry logic.

**LLM Provider Configuration**: Provider selection (OpenAI, Anthropic, Google Gemini), API keys (from environment), model name per provider (one model per provider), temperature and other parameters, token limits. Default models: OpenAI uses gpt-5.2, Anthropic uses claude-opus-4.5, Google Gemini uses gemini-3-flash. Model names are configurable in config file.

**Game Configuration**: Default player symbol, AI symbol, game rules (if configurable), move timeout.

**MCP Configuration** (if using MCP mode): Port assignments per agent, server URLs for distributed mode, protocol settings, transport type (stdio, HTTP, SSE).

**Port Configuration**: All service ports must be configurable through the configuration file. API server port (default: 8000), UI port (default: 8501), MCP agent server ports (if using distributed mode). No hardcoded ports in application code.

**UI Configuration**: Theme, refresh intervals, metrics display preferences, debug mode.

### Configuration Sources

**config.json**: Main configuration file with default settings.

**.env file**: Environment-specific settings (API keys, secrets, local paths).

**Environment Variables**: Override config.json values. Prefixed with project name to avoid conflicts.

**Command-line Arguments**: Override for quick testing (model selection, mode selection).

Configuration is loaded in priority order: defaults in code, config.json, .env file, environment variables, command-line arguments.

---

## 10. Deployment Considerations

### Local Development

**Single Process**: All components (API, agents, UI) run in one process or separate processes on different ports.

**Development Server**: Use framework-specific development mode with auto-reload for API and UI.

**Debug Mode**: Enable verbose logging, detailed error messages, agent reasoning display.

### Production Deployment

**Separate Services**: API server, UI, and agent services (if distributed) as separate processes or containers.

**Process Management**: Use systemd, supervisor, or container orchestration (Docker Compose, Kubernetes).

**Scaling**: API and UI can scale horizontally. Agents can be distributed across machines using MCP protocol.

**Monitoring**: Logging to files or centralized system, metrics collection, health check endpoints, error tracking.

### MCP Distributed Mode

**Agent Servers**: Each agent runs as independent MCP server on assigned port. Communicate via MCP protocol (JSON-RPC over HTTP/SSE).

**Coordinator**: Connects to agent servers via MCP client. Can run on same machine or separate machine.

**Discovery**: Agent servers register capabilities via MCP tools/list. Coordinator discovers available tools dynamically.

**Fault Tolerance**: Handle agent server failures gracefully, retry logic, fallback to local mode if MCP unavailable.

### Containerization and Orchestration

**Docker Files**:

The project should include simple, functional Dockerfiles:

**Dockerfile**: Single Dockerfile for the application
- Base image: Language runtime (e.g., Node, Python, Java, Go)
- Install dependencies from package manifest
- Copy application code
- Expose ports: 8000 (API) and 8501 (UI)
- Default command to run the application

**Docker Compose**:

**docker-compose.yml**: Simple compose file for local development
- Services: api and ui
- Network for service communication
- Environment variables from .env file
- Volume mounts for code (development only)

**Kubernetes Helm Charts**:

**Chart Structure**:
```
helm/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml  # Deployments for API and UI services
    ├── service.yaml     # Services for API and UI
    ├── configmap.yaml   # Application configuration
    └── secret.yaml      # API keys and secrets
```

**Helm Chart Components**:

**Deployments**: Simple deployments for API and UI services
- Single replica per service (configurable via values)
- Environment variables from ConfigMap and Secrets
- Basic container image configuration

**Services**: ClusterIP services for API and UI
- API service on port 8000
- UI service on port 8501

**ConfigMap**: Application configuration (model names, timeouts, feature flags)

**Secret**: LLM API keys and sensitive configuration
- Store API keys for OpenAI, Anthropic, Google Gemini
- Use Kubernetes secrets (create manually or via kubectl)

**values.yaml**: Basic configuration
- Image name and tag
- Number of replicas (default: 1)
- Service ports
- LLM provider settings
- Environment-specific overrides

---

## 11. Testing Strategy

### Test-Driven Development Requirement

**MANDATORY**: Every functionality MUST be accompanied by a test. No code should be merged without corresponding tests.

**Acceptance Criteria Format**: All requirements in this specification use the **Given-When-Then** (Gherkin) format for testability:
- **Given** [initial context/state] - Specific inputs and preconditions
- **When** [action/trigger occurs] - The behavior being tested
- **Then** [expected outcome/assertion] - Measurable, verifiable results

Each acceptance criterion maps directly to one or more test cases. Criteria MUST use specific values (e.g., `row=3` not `invalid row`), specific error codes (e.g., `E_MOVE_OUT_OF_BOUNDS`), and measurable assertions (e.g., `returns list of 9 positions` not `returns some positions`).

**Test Coverage Policy**:
- **New Features**: MUST include unit tests before implementation (TDD approach preferred)
- **Bug Fixes**: MUST include a regression test demonstrating the bug and its fix
- **Refactoring**: Existing tests MUST pass; new tests MUST be added for any new code paths
- **API Endpoints**: MUST have integration tests covering success and error cases
- **Domain Logic**: MUST have unit tests covering all business rules and edge cases
- **Agent Behavior**: MUST have tests with mocked LLM responses covering all code paths

**Enforcement**:
- CI/CD pipeline MUST fail if tests are missing for modified code
- Code coverage MUST not decrease with new changes
- Pull requests MUST include tests for all functionality changes

### Unit Tests

**Domain Models**: Test model validation, edge cases, helper methods. Schema validation for all domain models to ensure type safety and data integrity. **REQUIRED**: Every domain model MUST have a corresponding test file.

**Game Engine**: Test move validation, win detection, draw detection, state management. Use parameterized tests for multiple scenarios to cover all game states efficiently. **REQUIRED**: Every game engine method MUST have corresponding tests.

**Agents**: Test each agent in isolation with mocked LLM, validate input/output types, test error handling. Agent interface contract validation to ensure all agents comply with protocol definitions. **REQUIRED**: Every agent implementation MUST have a test suite with mocked LLM responses.

**Test Data Management**: Fixture strategies for common game states (opening, midgame, endgame, win scenarios). Test data generators for board positions to create diverse test cases programmatically. **REQUIRED**: Reusable fixtures MUST be created for common test scenarios.

### Integration Tests

**Agent Pipeline**: Test full pipeline (Scout → Strategist → Executor) with real or mocked LLM. **REQUIRED**: Complete pipeline integration test MUST exist.

**API Endpoints**: Test API endpoints with test client, validate request/response models, test error cases. **REQUIRED**: Every API endpoint MUST have integration tests covering at least success path and primary error cases.

**Game Flow**: Test complete game from start to finish, test win/loss/draw scenarios, test player and AI moves. **REQUIRED**: End-to-end game flow tests MUST cover all winning conditions and draw scenarios.

**Contract Tests**: API contract tests between UI and backend to ensure interface compatibility and prevent breaking changes. **REQUIRED**: Contract tests MUST be maintained for all API endpoints consumed by UI.

**MCP Protocol Tests**: Test MCP client/server communication, protocol compliance, and mode switching between local and distributed modes. **REQUIRED**: If MCP mode is implemented, corresponding integration tests MUST exist.

### End-to-End Tests

**Full System**: Test with complete UI, API backend, and real agents. Test user interactions, verify game state persistence, test metrics collection. **REQUIRED**: At least one full E2E test MUST exist for critical user journey (start game → make move → complete game).

### Performance Tests

**Agent Response Times**: Measure agent execution times, identify bottlenecks, test with different LLM providers. **REQUIRED**: Performance baseline tests MUST be established and monitored.

**Concurrent Games**: Test multiple simultaneous games, verify no state leakage, test resource usage. **REQUIRED**: If concurrent games are supported, stress tests MUST verify isolation.

### Resilience Tests

**LLM Failure Scenarios**: Simulate LLM timeouts/failures to verify graceful degradation and fallback strategies work correctly. **REQUIRED**: Tests MUST verify each error scenario in the Failure Matrix (Section 12).

**Agent Failure Cascade Testing**: Test system behavior when agents fail in sequence, verify error propagation and recovery mechanisms. **REQUIRED**: Tests MUST verify fallback strategies work as specified.

### Test Coverage

**Coverage Targets**:
- **MANDATORY MINIMUM**: 80% code coverage for unit tests
- **MANDATORY MINIMUM**: 70% code coverage for integration tests
- Use language-appropriate coverage tools for reporting
- **NO EXCEPTIONS**: New code MUST maintain or improve coverage percentages

**Critical Path Testing**: Critical path smoke tests for CI/CD to validate core functionality in automated pipelines. **REQUIRED**: Smoke tests MUST run on every commit.

### CI/CD Integration

**GitHub Actions**: Integration with GitHub Actions for automated testing on pull requests and commits. Run unit tests, integration tests, and smoke tests in CI pipeline. Enforce coverage thresholds before merging.

**REQUIRED CI/CD Checks**:
- All tests MUST pass before merge
- Code coverage MUST meet minimum thresholds (80% unit, 70% integration)
- No new code without corresponding tests
- Smoke tests MUST pass on every commit
- Pull requests MUST include test evidence for all changes

**Test Reporting**:
- Test results MUST be visible in pull request status
- Coverage reports MUST be generated and tracked over time
- Failed tests MUST block deployment
- Test execution time MUST be monitored to prevent slow tests

---

## 12. Error Handling and Resilience

### Error Categories

**Validation Errors**: Invalid moves, malformed requests, type mismatches. System MUST return clear error messages with validation details (field name, expected type/constraint, actual value, error code).

**Agent Errors**: LLM failures, timeout errors, parsing errors. System MUST log error details (error code, agent name, execution time, error message), MUST return fallback responses, MUST continue game if fallback succeeds.

**System Errors**: Network failures, database errors, configuration errors. System MUST log critical errors (error code, timestamp, context), MUST provide user-friendly messages (non-technical language), SHOULD implement circuit breakers when errors exceed threshold (e.g., 5 failures in 60 seconds).

### Comprehensive Failure Matrix

This table defines deterministic behavior for all failure scenarios. All error codes MUST match the Error Code Enum defined in Section 5 (Error Response Schema). HTTP status codes MUST follow the mapping in Section 5.

| Error Type | Error Code | HTTP Status | Retry Policy | Fallback Strategy | User Message | UI Indication | Log Level | Test Coverage |
|------------|------------|-------------|--------------|-------------------|--------------|---------------|-----------|---------------|
| **LLM API Timeout** | `E_LLM_TIMEOUT` | 500 | 3 retries, exponential backoff (1s, 2s, 4s); per-agent timeouts: Scout 5s, Strategist 5s, Executor 3s (local mode) | Use rule-based move selection | "AI is taking longer than expected. Using quick analysis..." | Orange warning icon, show retry countdown | WARNING | Resilience test required |
| **LLM Parse Error** | `E_LLM_PARSE_ERROR` | 500 | 2 retries with prompt refinement | Use previous successful agent output or rule-based | "AI response unclear. Using backup strategy..." | Yellow warning badge, show "Using fallback" | ERROR | Unit test required |
| **LLM Rate Limit** | `E_LLM_RATE_LIMIT` | 500 | Wait + retry once after rate limit window | Queue request or use cached response | "AI is busy. Please wait a moment..." | Blue info icon, show wait timer | WARNING | Integration test required |
| **LLM Invalid API Key** | `E_LLM_AUTH_ERROR` | 500 | No retry | Fallback to rule-based moves entirely | "AI configuration error. Using rule-based play." | Red error banner, persist for session | CRITICAL | Smoke test required |
| **Scout Agent Failure** | `E_SCOUT_FAILED` | 500 | 1 retry | Use rule-based board analysis (immediate wins/blocks/center) | "AI analysis unavailable. Using standard tactics..." | Orange agent status icon, show "Rule-based mode" | ERROR | Resilience test required |
| **Strategist Agent Failure** | `E_STRATEGIST_FAILED` | 500 | 1 retry | Use Scout's highest priority opportunity directly | "AI strategy unavailable. Using tactical move..." | Orange agent status icon, show "Tactical mode" | ERROR | Resilience test required |
| **Executor Agent Failure** | `E_EXECUTOR_FAILED` | 500 | 1 retry | Use Strategist's primary move with basic validation | "AI execution error. Applying recommended move..." | Orange agent status icon, show "Direct execution" | ERROR | Resilience test required |
| **Invalid Move (Out of Bounds)** | `E_MOVE_OUT_OF_BOUNDS` | 400 | No retry | Return error to user, request new move | "Invalid move: Position out of bounds (0-2 only)" | Red cell highlight, shake animation | INFO | Unit test required |
| **Invalid Move (Cell Occupied)** | `E_CELL_OCCUPIED` | 400 | No retry | Return error to user, request new move | "Invalid move: Cell already occupied" | Red cell highlight, pulse animation | INFO | Unit test required |
| **Game Already Over** | `E_GAME_ALREADY_OVER` | 400 | No retry | Return error to user | "Game is already over. Winner: [X/O/DRAW]" | Red cell highlight, show game over message | INFO | Unit test required |
| **MCP Connection Failed** | `E_MCP_CONN_FAILED` | 500 | 2 retries with 5s delay | Switch to local mode agents | "Distributed mode unavailable. Using local agents..." | Yellow mode indicator, show "Local mode active" | ERROR | Integration test required |
| **MCP Agent Timeout** | `E_MCP_TIMEOUT` | 500 | 1 retry with 10s timeout | Switch to local mode for that agent | "Agent not responding. Using local fallback..." | Orange agent icon, show timeout countdown | WARNING | Resilience test required |
| **API Request Malformed** | `E_API_MALFORMED` | 400 | No retry | Return 400 Bad Request with validation details | "Invalid request: [specific validation error]" | Red toast notification, 5s auto-dismiss | INFO | Contract test required |
| **Game State Corrupted** | `E_STATE_CORRUPTED` | 500 | No retry | Reset game state, log incident | "Game state error. Please restart the game." | Red modal dialog, require user acknowledgment | CRITICAL | Integration test required |
| **Network Error (API)** | `E_NETWORK_ERROR` | 500 | 3 retries with exponential backoff | Show cached state, allow offline mode | "Connection lost. Retrying..." | Gray offline indicator, show retry attempt (1/3) | WARNING | E2E test required |
| **Configuration Error** | `E_CONFIG_ERROR` | 500 | No retry | Use default configuration | "Configuration issue. Using defaults..." | Yellow banner at top, dismissible | ERROR | Smoke test required |
| **Schema Validation Error** | `E_SCHEMA_VALIDATION_ERROR` | 422 | No retry | Log error, return sanitized default | "Data format error. Using safe defaults..." | Yellow toast notification, 5s auto-dismiss | ERROR | Unit test required |

**Acceptance Criteria for LLM API Timeout:**
- Given Scout LLM call exceeds 5s, when timeout occurs, then retries 3 times with exponential backoff (1s, 2s, 4s)
- Given 3 retries exhausted for Scout, when timeout persists, then uses rule-based board analysis (center/corner heuristic)
- Given timeout on retry attempt 2, when LLM finally responds, then uses response and cancels remaining retries
- Given fallback triggered due to timeout, when move completes, then UI shows orange warning icon with "AI is taking longer than expected. Using quick analysis..."
- Given timeout event, when logging, then includes agent_name, timeout_duration_ms, retry_count=3, fallback_used=true, log_level=WARNING

**Acceptance Criteria for LLM Parse Error:**
- Given LLM returns unparseable JSON, when parse error occurs, then retries 2 times with prompt refinement
- Given 2 retries exhausted, when parse error persists, then uses previous successful agent output or rule-based fallback
- Given parse error logged, when logging, then includes raw_llm_response, parse_error_details, retry_count, log_level=ERROR
- Given parse error fallback triggered, when UI updates, then shows yellow warning badge with "AI response unclear. Using backup strategy..."

**Acceptance Criteria for LLM Rate Limit:**
- Given LLM returns 429 rate limit error, when rate limit detected, then waits for rate limit window (from Retry-After header) + retries once
- Given rate limit wait time, when UI updates, then shows blue info icon with "AI is busy. Please wait a moment..." and countdown timer
- Given rate limit resolved after wait, when retry succeeds, then continues normal operation without fallback
- Given rate limit persists after retry, when second rate limit occurs, then uses cached response or queues request

**Acceptance Criteria for LLM Invalid API Key:**
- Given LLM returns 401/403 authentication error, when invalid API key detected, then does not retry
- Given authentication error, when fallback executes, then switches to rule-based moves for entire session
- Given invalid API key error, when UI updates, then shows red error banner with "AI configuration error. Using rule-based play." persisting for entire session
- Given authentication error logged, when logging, then includes error_code=E_LLM_AUTH_ERROR, provider_name, log_level=CRITICAL (sanitize API key from logs)

**Acceptance Criteria for Scout Agent Failure:**
- Given Scout agent fails, when failure detected, then retries once with same inputs
- Given Scout retry fails, when second failure occurs, then uses rule-based board analysis (check immediate wins, blocks, then center/corner)
- Given Scout fallback triggered, when UI updates, then shows orange agent status icon with "AI analysis unavailable. Using standard tactics..."
- Given Scout fallback used, when logging, then includes error_code=E_SCOUT_FAILED, fallback_strategy="rule-based", log_level=ERROR

**Acceptance Criteria for Strategist Agent Failure:**
- Given Strategist agent fails, when failure detected, then retries once
- Given Strategist retry fails, when second failure occurs, then uses Scout's highest priority opportunity as primary move
- Given Strategist fallback triggered, when UI updates, then shows orange agent status icon with "AI strategy unavailable. Using tactical move..."
- Given Strategist fallback, when move executed, then move is Scout's top-priority opportunity (IMMEDIATE_WIN > BLOCK_THREAT > CENTER_CONTROL, etc.)

**Acceptance Criteria for Executor Agent Failure:**
- Given Executor agent fails, when failure detected, then retries once
- Given Executor retry fails, when second failure occurs, then applies Strategist's primary move with basic validation (bounds, occupancy)
- Given Executor fallback triggered, when UI updates, then shows orange agent status icon with "AI execution error. Applying recommended move..."
- Given Executor fallback validation fails, when move is invalid, then returns error to user (do not apply invalid move)

**Acceptance Criteria for Invalid Move (Out of Bounds):**
- Given move request with row=3, col=1, when validating, then returns HTTP 400 with error_code `E_MOVE_OUT_OF_BOUNDS` and error response schema (status="failure", error_code="E_MOVE_OUT_OF_BOUNDS", message, timestamp, details with position)
- Given out of bounds error, when UI updates, then highlights invalid cell area in red with shake animation
- Given out of bounds error message, when displaying, then shows "Invalid move: Position out of bounds (0-2 only)"
- Given out of bounds error logged, when logging, then includes attempted_position, log_level=INFO

**Acceptance Criteria for Invalid Move (Cell Occupied):**
- Given move request for occupied cell (1,1) with X, when validating, then returns HTTP 400 with error_code `E_CELL_OCCUPIED` and error response schema (status="failure", error_code="E_CELL_OCCUPIED", message, timestamp, details with position and actual cell value)
- Given cell occupied error, when UI updates, then highlights occupied cell in red with pulse animation
- Given cell occupied error message, when displaying, then shows "Invalid move: Cell already occupied"
- Given cell occupied error, when user attempts, then does not modify game state

**Acceptance Criteria for MCP Connection Failed:**
- Given MCP connection attempt fails, when connection failure detected, then retries 2 times with 5s delay between attempts
- Given 2 retries exhausted, when connection still fails, then switches entire agent system to local mode
- Given MCP fallback to local mode, when UI updates, then shows yellow mode indicator with "Distributed mode unavailable. Using local agents..."
- Given MCP connection failure logged, when logging, then includes error_code=E_MCP_CONN_FAILED, mcp_server_url, retry_count=2, log_level=ERROR

**Acceptance Criteria for MCP Agent Timeout:**
- Given MCP agent call exceeds 10s, when timeout occurs, then retries once with 10s timeout
- Given MCP retry fails, when second timeout occurs, then switches that specific agent to local mode (other agents remain MCP if available)
- Given MCP agent timeout, when UI updates, then shows orange agent icon with timeout countdown during retry
- Given partial MCP fallback, when logging, then includes agent_name, timeout_duration_ms=10000, mode="local_fallback", log_level=WARNING

**Acceptance Criteria for API Request Malformed:**
- Given API request with malformed JSON, when parsing, then returns 400 Bad Request with specific validation error details
- Given malformed request, when responding, then includes error_code=API_MALFORMED and JSON path to invalid field
- Given malformed request error, when UI receives, then shows red toast notification with "Invalid request: [specific validation error]" for 5s auto-dismiss
- Given malformed request logged, when logging, then includes raw_request (sanitized), validation_error_details, log_level=INFO

**Acceptance Criteria for Game State Corrupted:**
- Given game state validation fails (e.g., invalid symbol balance, multiple winners), when corruption detected, then does not retry
- Given state corruption, when handling, then resets game state to new game and logs incident with CRITICAL level
- Given state corruption error, when UI updates, then shows red modal dialog with "Game state error. Please restart the game." requiring user acknowledgment
- Given state corruption logged, when logging, then includes corrupted_state_snapshot, validation_failures, incident_id, log_level=CRITICAL

**Acceptance Criteria for Network Error (API):**
- Given API request fails with network error, when failure detected, then retries 3 times with exponential backoff (1s, 2s, 4s)
- Given network error during retries, when UI updates, then shows gray offline indicator with "Connection lost. Retrying... (attempt 1/3)"
- Given all 3 retries fail, when network still unavailable, then shows cached game state and enables offline mode
- Given network restored during retry, when connection succeeds, then syncs local state with server and resumes normal operation

**Acceptance Criteria for Configuration Error:**
- Given invalid configuration file format, when loading config, then does not retry
- Given config error, when handling, then uses default configuration values from Section 9
- Given config error, when UI updates, then shows yellow banner at top with "Configuration issue. Using defaults..." (dismissible by user)
- Given config error logged, when logging, then includes config_file_path, error_details, defaults_used, log_level=ERROR

**Acceptance Criteria for Schema Validation Error:**
- Given API response fails schema validation, when validating, then does not retry
- Given schema validation failure, when handling, then logs full error details and returns sanitized default response
- Given schema error, when UI receives, then shows yellow toast notification with "Data format error. Using safe defaults..." for 5s auto-dismiss
- Given schema error logged, when logging, then includes schema_name, validation_errors, actual_data_structure (sanitized), log_level=ERROR

### UI Indication Specifications

**Visual Hierarchy**:
- **CRITICAL errors**: Red modal dialogs (blocking, require acknowledgment)
- **ERROR level**: Red banners or toast notifications (prominent, persistent until action)
- **WARNING level**: Orange/Yellow icons or banners (visible, auto-dismiss or user-dismissible)
- **INFO level**: Blue info icons or brief toast notifications (subtle, auto-dismiss)

**Color Coding**:
- 🔴 Red: Critical failures, invalid actions, blocking errors
- 🟠 Orange: Agent failures, fallback modes, degraded operation
- 🟡 Yellow: Configuration issues, mode changes, non-blocking warnings
- 🔵 Blue: Informational messages, rate limits, transient states
- ⚫ Gray: Connectivity issues, offline mode, system states

**Animation Types**:
- **Shake**: Invalid input (cell already occupied, out of bounds)
- **Pulse**: Attention needed (occupied cell highlight)
- **Fade**: Transient notifications (toast auto-dismiss)
- **Countdown**: Time-based retries (network, timeout, rate limit)
- **Progress bar**: Multi-step retries with backoff

**Persistence Rules**:
- Blocking errors (CRITICAL): Persist until user acknowledges
- Session errors: Persist for entire session (invalid API key)
- Temporary errors: Auto-dismiss after 5-10 seconds
- Transient states: Update in real-time (retry countdown)

### Fallback Strategies

**Agent Fallbacks**: If Scout fails, use rule-based analysis. If Strategist fails, use Scout's best opportunity. If Executor fails, use Strategist's primary move directly.

**Game Continuity**: Game continues even if agent fails. Use last known good state, provide default moves, allow player to continue.

**UI Resilience**: UI handles API failures gracefully, shows error messages, allows retry, maintains local game state.

### Implementation Guidelines

**Retry Logic**:
- Use exponential backoff for transient errors
- Include jitter to prevent thundering herd
- Set maximum retry limits to prevent infinite loops
- Log each retry attempt with context

**Fallback Execution**:
- Always validate fallback outputs before applying
- Track fallback usage in metrics
- Alert on excessive fallback usage (> 10% of moves)
- Document fallback behavior for users

**Error Logging**:
- Include error code, context, and stack trace
- Track error frequency and patterns
- Implement alerting for CRITICAL errors
- Sanitize sensitive data before logging

**User Communication**:
- Use user-friendly, non-technical language
- Provide actionable guidance when possible
- Show progress indicators during retries
- Allow manual override/retry for failed actions

**Acceptance Criteria for Retry Logic:**
- Given transient error occurs, when retrying, then uses exponential backoff with delays: retry_1=1s, retry_2=2s, retry_3=4s
- Given exponential backoff calculation, when computing delay, then adds random jitter (0-500ms) to prevent thundering herd
- Given retry loop executing, when max retries reached (3 for most errors), then stops retrying and executes fallback
- Given retry attempt, when logging, then includes retry_number, delay_ms, error_type, total_elapsed_time_ms

**Acceptance Criteria for Fallback Execution:**
- Given fallback output generated, when applying fallback, then validates output using same validation rules as primary path
- Given fallback validation fails, when invalid output detected, then returns error to user (do not apply invalid fallback)
- Given fallback executed successfully, when tracking metrics, then increments fallback_usage_count for that agent/error type
- Given fallback usage exceeds 10% of moves in session, when threshold crossed, then logs alert with severity=WARNING

**Acceptance Criteria for Error Logging:**
- Given any error occurs, when logging, then includes: error_code, error_message, timestamp, context (agent_name, game_id, move_number)
- Given exception thrown, when logging ERROR or CRITICAL, then includes full stack trace
- Given error frequency tracking, when same error occurs 5+ times in 1 minute, then logs rate_limit_exceeded warning
- Given CRITICAL error logged, when severity is CRITICAL, then triggers alerting mechanism (email, Slack, PagerDuty, etc.)
- Given logging sensitive data, when sanitizing, then removes API keys, user PII, internal paths before logging

**Acceptance Criteria for User Communication:**
- Given error message displayed, when formatting message, then uses non-technical language (no stack traces, no error codes visible to user)
- Given error with known fix, when displaying error, then includes actionable guidance (e.g., "Check your API key in Config tab")
- Given retry in progress, when UI updates, then shows progress indicator (spinner, countdown, or "Retrying... 2/3")
- Given error with manual retry option, when displaying error, then shows "Retry" button allowing user to trigger manual retry

---

## 12.1 LLM Provider Metadata and Experimentation Tracking

### Purpose

Enable A/B testing, cost optimization, and performance analysis by tracking detailed metadata about LLM provider combinations, their characteristics, and performance metrics across games.

### LLM Provider Metadata Registry

**Location**: Store in `config/llm_providers.json` or database table

**Schema**:
```json
{
  "providers": {
    "openai": {
      "models": {
        "gpt-4o": {
          "cost_per_1k_input_tokens": 0.0025,
          "cost_per_1k_output_tokens": 0.01,
          "avg_latency_ms": 1200,
          "max_tokens": 128000,
          "context_window": 128000,
          "supports_streaming": true,
          "reliability_score": 0.99,
          "last_updated": "2025-01-15"
        },
        "gpt-4o-mini": {
          "cost_per_1k_input_tokens": 0.00015,
          "cost_per_1k_output_tokens": 0.0006,
          "avg_latency_ms": 800,
          "max_tokens": 128000,
          "context_window": 128000,
          "supports_streaming": true,
          "reliability_score": 0.98,
          "last_updated": "2025-01-15"
        }
      }
    },
    "anthropic": {
      "models": {
        "claude-opus-4": {
          "cost_per_1k_input_tokens": 0.015,
          "cost_per_1k_output_tokens": 0.075,
          "avg_latency_ms": 2000,
          "max_tokens": 200000,
          "context_window": 200000,
          "supports_streaming": true,
          "reliability_score": 0.99,
          "last_updated": "2025-01-15"
        },
        "claude-sonnet-4": {
          "cost_per_1k_input_tokens": 0.003,
          "cost_per_1k_output_tokens": 0.015,
          "avg_latency_ms": 1500,
          "max_tokens": 200000,
          "context_window": 200000,
          "supports_streaming": true,
          "reliability_score": 0.98,
          "last_updated": "2025-01-15"
        }
      }
    },
    "google": {
      "models": {
        "gemini-2.0-flash-exp": {
          "cost_per_1k_input_tokens": 0.0,
          "cost_per_1k_output_tokens": 0.0,
          "avg_latency_ms": 1000,
          "max_tokens": 1048576,
          "context_window": 1048576,
          "supports_streaming": true,
          "reliability_score": 0.95,
          "last_updated": "2025-01-15"
        }
      }
    }
  }
}
```

### Game Session Tracking

**Essential Metrics** (5-7 core metrics to track per game):

```json
{
  "game_id": "uuid-v4",
  "timestamp": "2025-01-15T10:30:00Z",
  "game_outcome": "X_WIN|O_WIN|DRAW",

  "agent_config": {
    "scout_model": "openai/gpt-4o-mini",
    "strategist_model": "anthropic/claude-sonnet-4",
    "executor_model": "openai/gpt-4o-mini"
  },

  "metrics": {
    "1_total_cost_usd": 0.016,
    "2_total_tokens": 5800,
    "3_avg_latency_ms": 950,
    "4_game_duration_ms": 45000,
    "5_total_moves": 7,
    "6_fallback_count": 0,
    "7_error_count": 0
  }
}
```

**Metric Definitions**:

1. **total_cost_usd**: Total cost for all LLM calls in the game (calculated from tokens × provider rates)
2. **total_tokens**: Sum of input + output tokens across all agents
3. **avg_latency_ms**: Average time per agent LLM call
4. **game_duration_ms**: Total time from first move to game end
5. **total_moves**: Number of moves in the game
6. **fallback_count**: Number of times fallback strategies were triggered
7. **error_count**: Number of errors encountered during the game

**Why These 7?**
- **Cost tracking**: Essential for budget management (#1)
- **Token usage**: Directly impacts cost and helps identify optimization opportunities (#2)
- **Performance**: Latency affects user experience (#3)
- **Game context**: Duration and moves provide context for other metrics (#4, #5)
- **Reliability**: Fallback and error counts indicate system health (#6, #7)

### Experiment Configuration

**Location**: Store in `config/experiments.json` or database table

**Schema**:
```json
{
  "experiments": [
    {
      "experiment_id": "exp_001_scout_model_comparison",
      "name": "Scout Agent Model Comparison",
      "description": "Compare GPT-4o-mini vs Claude Sonnet-4 for Scout agent",
      "status": "active",
      "start_date": "2025-01-15",
      "end_date": null,
      "target_games": 100,
      "current_games": 42,

      "variants": [
        {
          "variant_id": "variant_a",
          "name": "GPT-4o-mini Scout",
          "weight": 0.5,
          "agent_config": {
            "scout": {
              "provider": "openai",
              "model": "gpt-4o-mini"
            },
            "strategist": {
              "provider": "anthropic",
              "model": "claude-sonnet-4"
            },
            "executor": {
              "provider": "openai",
              "model": "gpt-4o-mini"
            }
          }
        },
        {
          "variant_id": "variant_b",
          "name": "Claude Sonnet-4 Scout",
          "weight": 0.5,
          "agent_config": {
            "scout": {
              "provider": "anthropic",
              "model": "claude-sonnet-4"
            },
            "strategist": {
              "provider": "anthropic",
              "model": "claude-sonnet-4"
            },
            "executor": {
              "provider": "openai",
              "model": "gpt-4o-mini"
            }
          }
        }
      ],

      "success_metrics": [
        "avg_cost_per_game",
        "avg_latency_per_move",
        "win_rate",
        "fallback_rate"
      ]
    }
  ]
}
```

### Analytics and Reporting Requirements

**Simple Analytics API** (GET `/api/analytics/summary`):

Query parameters:
- `start_date`, `end_date`: Date range (optional, defaults to last 30 days)
- `model_combo`: Filter by model combination (optional)

Response (aggregates the 7 core metrics):
```json
{
  "date_range": {
    "start": "2025-01-01",
    "end": "2025-01-15"
  },
  "total_games": 500,
  "summary": {
    "avg_cost_per_game": 0.017,
    "avg_tokens_per_game": 5800,
    "avg_latency": 950,
    "avg_duration": 45000,
    "avg_moves": 7.2,
    "total_fallbacks": 10,
    "total_errors": 5
  },
  "totals": {
    "total_cost": 8.50,
    "total_tokens": 2900000
  }
}
```

**Comparison API** (GET `/api/analytics/compare`):

Compare two model combinations:
```json
{
  "comparison": {
    "config_a": "openai/gpt-4o-mini (all agents)",
    "config_b": "anthropic/claude-sonnet-4 (all agents)",
    "games_each": 50,
    "metrics_a": {
      "avg_cost": 0.015,
      "avg_latency": 850,
      "fallback_rate": 0.02
    },
    "metrics_b": {
      "avg_cost": 0.025,
      "avg_latency": 1400,
      "fallback_rate": 0.01
    },
    "winner": "config_a (33% cheaper, 39% faster)"
  }
}
```

### Storage Requirements

**Phase 1: JSON File Storage (Initial Implementation)**

Start with file-based storage for simplicity and rapid development:

```
logs/
├── games/
│   ├── {game_id}.json          # Individual game results
│   ├── {game_id}.json
│   └── ...
├── analytics/
│   ├── summary_2025-01.json    # Monthly aggregates
│   └── summary_2025-02.json
└── experiments/
    └── exp_001_results.json     # Experiment-specific results
```

**Benefits**:
- No database setup required
- Human-readable and debuggable
- Easy to version control and backup
- Perfect for prototyping and small-scale experiments (< 1000 games)
- Simple to implement and maintain

**Limitations**:
- Limited query capabilities (must read and filter files)
- Manual aggregation required
- Slower performance for large datasets
- No concurrent write protection

**When to Use**: Initial development, prototyping, small-scale experiments, single-machine deployments

**Phase 2: SQLite Database (Production Scale)**

Migrate to SQLite when you need better query performance and analytics:

```sql
CREATE TABLE games (
    game_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    game_outcome TEXT NOT NULL,
    scout_model TEXT NOT NULL,
    strategist_model TEXT NOT NULL,
    executor_model TEXT NOT NULL,
    total_cost_usd REAL,
    total_tokens INTEGER,
    avg_latency_ms INTEGER,
    game_duration_ms INTEGER,
    total_moves INTEGER,
    fallback_count INTEGER,
    error_count INTEGER
);

CREATE INDEX idx_timestamp ON games(timestamp);
CREATE INDEX idx_models ON games(scout_model, strategist_model, executor_model);
CREATE INDEX idx_outcome ON games(game_outcome);
```

**Benefits**:
- Fast queries with SQL
- Built-in aggregation functions
- Indexed searches
- ACID compliance
- No external database server needed

**Limitations**:
- Binary format (not human-readable)
- Requires SQL knowledge
- Single-file database (potential bottleneck)

**When to Use**: Production deployments, complex analytics, > 1000 games, multi-user scenarios

**Phase 3: Parquet Files (Data Science & ML)**

Use columnar format for advanced analytics and machine learning:

```python
import pandas as pd

# Load all games
df = pd.DataFrame(game_results)

# Save as Parquet
df.to_parquet('logs/experiments/exp_001.parquet',
              compression='snappy',
              index=False)

# Query with DuckDB
import duckdb
results = duckdb.query("""
    SELECT scout_model, AVG(total_cost_usd) as avg_cost
    FROM read_parquet('logs/experiments/*.parquet')
    GROUP BY scout_model
""").df()
```

**Benefits**:
- Excellent compression (10-100x smaller than JSON)
- Columnar storage (fast analytics)
- Works with pandas, polars, DuckDB, Spark
- Easy export to data warehouses
- Supports complex nested data

**Limitations**:
- Binary format (not human-readable)
- Requires Python data science stack
- More complex tooling

**When to Use**: Data analysis workflows, ML experiments, large datasets (> 10,000 games), data warehouse integration

**Migration Path**:

1. **Start**: Use JSON files for initial development
2. **Growth**: Migrate to SQLite when query performance becomes an issue
3. **Scale**: Export to Parquet for data science and ML workflows

**Implementation Note**: Design the storage layer with an abstraction (e.g., `ExperimentStorage` interface) that can be swapped between JSON, SQLite, and Parquet without changing application code.

### UI Integration

**Metrics Panel** (US-015, US-017, US-018) displays the 7 core metrics:
1. Total cost for current game
2. Total tokens used
3. Average latency
4. Game duration
5. Move count
6. Fallback count (if any)
7. Error count (if any)

**Optional: Simple Analytics View**:
- Last 10 games: Show the 7 metrics per game in a table
- Compare button: Select two games to compare their metrics side-by-side

### Implementation Guidelines

1. **Automatic Tracking**: All LLM calls MUST be automatically instrumented to capture the 7 metrics
2. **Calculate from Registry**: Use provider metadata to calculate costs (tokens × rates)
3. **Async Logging**: Write metrics asynchronously to avoid blocking game flow
4. **Simple Storage**: JSON files are sufficient; database is optional

---

## 13. Security Considerations

### API Security

**Input Validation**: All inputs validated via type-safe models, sanitize user inputs, prevent injection attacks.

**Acceptance Criteria for Input Validation:**
- Given API request with string input, when validating, then sanitizes HTML/script tags to prevent XSS attacks
- Given API request with special characters in move reasoning, when storing, then escapes SQL special characters to prevent SQL injection
- Given API request with position values, when validating, then enforces type safety (integers only, range 0-2)
- Given malformed JSON in request body, when parsing, then returns 422 Unprocessable Entity without processing
- Given API request with overly long strings (>10KB), when validating, then rejects with error `ERR_INPUT_TOO_LARGE`
- Given API request with null values in required fields, when validating, then returns 400 Bad Request with specific missing field names

**Rate Limiting**: Limit API request rates, prevent abuse, implement per-user limits if multi-user.

**Acceptance Criteria for Rate Limiting:**
- Given single IP makes >100 requests in 1 minute, when rate limit exceeded, then returns 429 Too Many Requests with Retry-After header
- Given rate-limited client, when waiting for rate limit window, then allows requests after window expires
- Given distributed denial of service attempt detected, when anomaly threshold crossed, then implements temporary IP block (5 minute cooldown)
- Given rate limit applied, when logging, then includes client_ip, request_count, time_window, action_taken

**Authentication** (if multi-user): Implement user authentication, session management, authorization checks.

**Acceptance Criteria for Authentication:**
- Given unauthenticated user accessing protected endpoint, when checking auth, then returns 401 Unauthorized
- Given authenticated user with expired session token, when validating session, then returns 401 with error `ERR_SESSION_EXPIRED`
- Given user attempts to access another user's game, when checking authorization, then returns 403 Forbidden
- Given failed login attempt, when logging, then records failed_login event with timestamp, username, ip_address (no password logged)

### Data Security

**API Keys**: Store in environment variables, never commit to version control, use secrets management in production.

**Acceptance Criteria for API Key Management:**
- Given API key stored in code, when code review or security scan runs, then fails with error "API keys must be in environment variables"
- Given API key in environment variable, when application starts, then loads key without logging full key value (log only last 4 characters)
- Given missing required API key (OpenAI/Anthropic/Google), when starting application, then raises error `ERR_MISSING_API_KEY` with provider name
- Given invalid API key format (not matching provider pattern), when validating, then returns error `ERR_INVALID_API_KEY_FORMAT` before making LLM call
- Given API key exposed in logs, when log sanitization runs, then replaces API key with "[REDACTED-****XXXX]" showing only last 4 characters
- Given production environment, when deploying, then uses secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.) not plain env vars

**Game State**: Validate game state integrity, prevent state manipulation, log state changes.

**Acceptance Criteria for Game State Security:**
- Given game state received from client, when validating, then verifies state matches server-side authoritative state
- Given client attempts to modify game_id, when processing request, then ignores client-provided game_id and uses server session game_id
- Given game state change, when persisting, then logs state change with: timestamp, previous_state_hash, new_state_hash, move_made, player
- Given state validation detects tampering (invalid move history, impossible board), when detected, then rejects state and returns error `ERR_STATE_TAMPERING`
- Given checksum mismatch between client and server state, when detected, then forces state sync from server (server is source of truth)

**Agent Communication**: If using MCP over network, use HTTPS, validate MCP protocol messages, prevent unauthorized agent access.

**Acceptance Criteria for Agent Communication Security:**
- Given MCP connection over network, when establishing connection, then enforces HTTPS/TLS (reject HTTP connections)
- Given MCP message received, when parsing, then validates message signature/checksum to prevent message tampering
- Given MCP agent request without valid authentication token, when checking auth, then returns 401 Unauthorized and closes connection
- Given MCP message with unexpected format, when parsing, then returns error `ERR_INVALID_MCP_MESSAGE` and logs security event
- Given multiple failed authentication attempts to MCP server, when threshold exceeded (3 failures), then temporarily blocks client IP for 5 minutes

---

# PART II: IMPLEMENTATION GUIDANCE (NON-NORMATIVE)

This section provides recommended approaches for implementing the core specification. These are guidelines, not requirements. Technologies and frameworks may be substituted as long as they satisfy the normative requirements in Part I.

---

## 14. Implementation Technology Stack

### Technology Stack Options

The following are example technology stacks. Any stack meeting the requirements is acceptable:

**Backend Framework Options:**
- **Node.js**: Express.js, Fastify, NestJS
- **Python**: FastAPI, Flask, Django REST Framework
- **Java**: Spring Boot, Quarkus, Micronaut
- **Go**: Gin, Echo, Fiber
- **C#**: ASP.NET Core
- **Requirements Met**: REST API support, async operations, OpenAPI documentation

**Data Validation Options:**
- **TypeScript**: Zod, io-ts, class-validator
- **Python**: Pydantic, Marshmallow, dataclasses
- **Java**: Bean Validation, Hibernate Validator
- **Go**: go-playground/validator, ozzo-validation
- **C#**: FluentValidation, DataAnnotations
- **Requirements Met**: Type safety, runtime validation, serialization/deserialization

**UI Framework Options:**
- **React**: Next.js, Create React App, Vite
- **Vue.js**: Nuxt, Vite
- **Angular**: Angular CLI
- **Svelte**: SvelteKit
- **Python**: Streamlit, Dash
- **Requirements Met**: Web-based interface, API client, interactive components

**LLM Integration:**
- See Section 19 for framework options (LangChain, LiteLLM, Direct SDKs, etc.)
- Any framework supporting multiple LLM providers
- **Requirements Met**: Multi-provider support, hot-swapping, connection pooling

**Testing Framework Options:**
- **JavaScript/TypeScript**: Jest, Vitest, Mocha
- **Python**: pytest, unittest
- **Java**: JUnit, TestNG
- **Go**: testing package, Testify
- **C#**: xUnit, NUnit, MSTest
- **Requirements Met**: Unit, integration, and E2E testing capabilities

### Technology Selection Criteria

When choosing alternative technologies, ensure they support:
1. **Type Safety**: Strong typing or runtime validation
2. **Async Operations**: Non-blocking I/O for agent operations
3. **API Standards**: REST, OpenAPI, or equivalent
4. **Configuration Management**: External configuration files
5. **Testing**: Comprehensive testing capabilities
6. **Observability**: Logging, metrics, and monitoring hooks

---

## 14.1 Recommended Python Stack

This section provides a complete, opinionated Python technology stack for rapid development. This is one of many possible implementations.

### Core Stack

**Language**: Python 3.11+

**Backend Framework**: FastAPI
- Async support for agent operations
- Automatic OpenAPI documentation
- Built-in data validation with Pydantic
- High performance with ASGI server (uvicorn)

**Data Validation**: Pydantic v2
- Type-safe domain models
- Runtime validation
- JSON serialization/deserialization
- Automatic OpenAPI schema generation

**UI Framework**: Streamlit
- Rapid prototyping
- Real-time updates with minimal code
- Built-in components for metrics and charts
- Easy integration with FastAPI backend

**LLM Integration**: Instructor + Direct SDKs
- Type-safe LLM responses using Pydantic models
- Works with OpenAI, Anthropic, Google SDKs
- Automatic retry and validation
- See Section 19 for details

**Testing**: pytest + pytest-asyncio + pytest-cov
- Async test support
- Fixtures for common test scenarios
- Code coverage reporting
- Parameterized tests

**Type Checking**: mypy
- Static type checking
- Ensures type safety across codebase

**Code Quality**: ruff (linting + formatting)
- Fast Python linter and formatter
- Replaces black, isort, flake8

### Project Structure (Python)

```
project/
├── pyproject.toml              # Project metadata and dependencies
├── README.md
├── .env.example
├── config/
│   ├── config.json            # Main configuration
│   └── llm_providers.json     # LLM provider metadata
├── src/
│   ├── schemas/               # Pydantic domain models
│   │   ├── __init__.py
│   │   ├── game.py           # Position, Board, GameState
│   │   ├── analysis.py       # Threat, Opportunity, BoardAnalysis
│   │   ├── strategy.py       # MovePriority, Strategy
│   │   ├── execution.py      # MoveExecution
│   │   └── api.py            # API request/response models
│   ├── agents/               # Agent implementations
│   │   ├── __init__.py
│   │   ├── interfaces.py     # ABC protocols
│   │   ├── scout_local.py
│   │   ├── strategist_local.py
│   │   ├── executor_local.py
│   │   └── mcp/              # MCP implementations
│   ├── game/                 # Game logic
│   │   ├── __init__.py
│   │   ├── engine.py         # Core game engine
│   │   ├── coordinator.py    # Agent coordinator
│   │   └── state.py          # State management
│   ├── services/             # Service layer
│   │   ├── __init__.py
│   │   ├── game_service.py
│   │   └── agent_service.py
│   ├── api/                  # FastAPI REST layer
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── game.py
│   │       └── agents.py
│   ├── ui/                   # Streamlit UI
│   │   ├── __init__.py
│   │   ├── app.py            # Main Streamlit app
│   │   └── components/
│   │       ├── board.py
│   │       ├── metrics.py
│   │       └── config.py
│   ├── models/               # LLM management
│   │   ├── __init__.py
│   │   ├── shared_llm.py     # Connection pooling
│   │   └── factory.py        # Provider factory
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # pytest fixtures
│   ├── test_game_engine.py
│   ├── test_agents.py
│   ├── test_api.py
│   └── integration/
│       └── test_full_game.py
└── docs/                     # Documentation
```

### Dependencies (pyproject.toml)

```toml
[project]
name = "tictactoe-agents"
version = "0.1.0"
description = "Multi-Agent Tic-Tac-Toe Game"
requires-python = ">=3.11"

dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "streamlit>=1.28.0",
    "instructor>=0.4.0",
    "openai>=1.3.0",
    "anthropic>=0.7.0",
    "google-generativeai>=0.3.0",
    "httpx>=0.25.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.7.0",
    "ruff>=0.1.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### Running the Application (Python)

**Development:**
```bash
# Install dependencies
pip install -e ".[dev]"

# Run API server (with auto-reload)
uvicorn src.api.main:app --reload --port 8000

# Run Streamlit UI (in separate terminal)
streamlit run src/ui/app.py --server.port 8501

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Type checking
mypy src/

# Linting and formatting
ruff check src/
ruff format src/
```

**Production:**
```bash
# API server (with production ASGI server)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Streamlit UI
streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker (Python)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 8501

# Default: run both API and UI
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & streamlit run src.ui.app.py --server.port 8501 --server.address 0.0.0.0"]
```

### Why Python?

**Advantages:**
- **Rapid Development**: Streamlit enables quick UI prototyping
- **LLM Ecosystem**: Best-in-class LLM libraries (LangChain, Instructor, SDKs)
- **Type Safety**: Pydantic provides runtime validation + type hints
- **Async Support**: Native async/await for agent coordination
- **Data Science**: Excellent for metrics and analytics
- **Community**: Large ecosystem for AI/ML development

**Trade-offs:**
- **Performance**: Slower than compiled languages (Go, Java, C#)
- **Concurrency**: GIL limits true parallelism (use async for I/O-bound tasks)
- **Deployment**: Requires Python runtime (vs. single binary)

**When to Use Python:**
- Rapid prototyping and iteration
- Strong emphasis on LLM integration
- Team familiar with Python ecosystem
- Metrics and analytics are important

**When to Consider Alternatives:**
- Need maximum performance (consider Go, Rust)
- Large-scale deployment (consider Java, C#)
- Team expertise in other languages
- Single binary deployment preferred

---

## 15. Performance Optimization

### Agent Performance

**Fast Path Analysis**: Scout MUST use rule-based checks for immediate wins/blocks before LLM calls. Rule-based checks MUST scan all 8 lines (3 rows, 3 columns, 2 diagonals) for patterns of 2 symbols + 1 empty. If pattern found, Scout MUST return result without calling LLM. LLM calls MUST only occur when rule-based checks find no immediate win/block.

**Shared LLM Connection**: Reuse LLM connections across agents, connection pooling, efficient token usage.

**Async Operations**: All agent calls are async, parallel execution where possible, non-blocking I/O.

### Game Performance

**State Management**: Efficient board representation, minimize state copies, lazy evaluation where possible.

**UI Performance**: Minimize unnecessary re-renders, efficient data transfer, use caching for expensive operations.

### Scalability

**Stateless Agents**: Agents are stateless, can be scaled horizontally, easy to distribute.

**Efficient Protocols**: MCP protocol is lightweight, minimal overhead, efficient serialization.

---

## 15. Agent Mode Architecture

### Mode 1: Local (Fast)

**Description**: In-process agent execution using an LLM framework with shared connection pooling. No MCP protocol overhead. The LLM framework (LangChain, LiteLLM, Instructor, or Direct SDKs - see Section 19) provides multi-provider support, allowing LLM provider switching via configuration.

**Characteristics**:
- Fast execution (< 1 second per move)
- Direct in-process method calls between coordinator and agents
- Shared LLM connection for efficiency
- Rule-based pre-checks for immediate wins/blocks
- LLM provider hot-swapping via configuration
- Best for production use

**Implementation**: Agents implement interfaces using the configured LLM framework. Coordinator calls agents via direct in-process method calls. The framework handles provider abstraction and connection management.

### Mode 2: Distributed MCP (Protocol-Based)

**Description**: Agents with MCP protocol support for distributed coordination. Can use any LLM framework internally (see Section 19).

**Characteristics**:
- MCP protocol for inter-agent communication (note: MCP is designed for tool integration and cross-process communication, not optimized for high-frequency agent coordination; use this mode when agents need to run on separate machines)
- Can distribute agents across machines
- Protocol overhead (3-8 seconds per move)
- Standardized API for external clients
- Best for demonstration and distributed scenarios

**Implementation**: Agents inherit from BaseMCPAgent, expose MCP tools, run as MCP servers. Coordinator uses MCP client to communicate.

### Mode Selection

**Configuration**: Agent mode and LLM framework selected via config.json or command-line argument. See Section 19 for framework comparison.

**Runtime**: Can switch modes without code changes (different agent implementations).

**Fallback**: If MCP mode fails, can fall back to local mode automatically.

---

## 16. LLM Integration

**Note**: This section describes LLM provider and model configuration. For LLM framework selection (LangChain, LiteLLM, Instructor, Direct SDKs), see Section 19: Implementation Choices.

### Supported Providers

**OpenAI**: Default model is `gpt-5.2`. Model name is configurable in config file.

**Anthropic**: Default model is `claude-opus-4.5`. Model name is configurable in config file.

**Google Gemini**: Default model is `gemini-3-flash`. Model name is configurable in config file.

**Configuration Constraint**: Only ONE model per provider. Each provider can only have one model configured at a time. To use multiple models from the same provider, switch the configuration and restart.

### Shared LLM Connection

**Purpose**: Reuse single LLM connection across all agents to reduce overhead.

**Implementation**: SharedLLMConnection class manages connection, provides get_connection() method.

**Configuration**: Model selection in config file (one model per provider), API keys from environment. Default models: OpenAI uses gpt-5.2, Anthropic uses claude-opus-4.5, Google Gemini uses gemini-3-flash.

**Error Handling**: Connection retry logic, fallback to individual connections if shared fails.

### LLM Usage Patterns

**Scout**: Uses LLM for strategic analysis when rule-based checks don't find immediate wins/blocks.

**Strategist**: Always uses LLM to synthesize analysis into strategy.

**Executor**: Uses LLM for move validation and reasoning, but can fall back to rule-based validation.

---

## 17. Metrics and Observability

### Agent Metrics

**Per-Agent Tracking**:
- Execution time (min, max, average)
- Success/failure rate
- LLM call count
- Token usage
- Error count and types

**Aggregation**: Metrics aggregated per agent, per game, and system-wide.

### Game Metrics

**Game-Level Tracking**:
- Total moves
- Game duration
- Win/loss/draw statistics
- Average move time
- Agent pipeline success rate

### System Metrics

**System-Level Tracking**:
- Total games played
- System uptime
- Resource usage (CPU, memory)
- API request rates
- Error rates

### Metrics Display

**Metrics Dashboard**: Real-time metrics display with charts and tables.

**API Endpoints**: Metrics available via REST API for external monitoring.

**Logging**: Metrics logged to files for historical analysis.

---

## 18. Future Enhancements

### Potential Features

**Difficulty Levels**: Adjust agent sophistication based on difficulty setting.

**Multi-Player Support**: Support for multiple human players or AI vs AI.

**Game Variants**: Support for different board sizes or game rules.

**Learning**: Track game patterns, learn from player behavior.

**Tournament Mode**: Multiple games, statistics tracking.

### Technical Improvements

**Caching**: Cache common board patterns and analysis results.

**Optimization**: Further optimize LLM prompts, reduce token usage.

**Testing**: Expand test coverage, add property-based testing.

**Documentation**: Expand user guides, add video tutorials.

---

## 19. Implementation Choices and Alternatives

This section discusses architectural decisions and alternative approaches for key system components.

### Agent Communication Patterns

**Coordinator-Mediated (Current Architecture)**:

The core architecture uses coordinator-mediated communication (see Section 3: Agent Architecture, Agent Pipeline Flow). The coordinator orchestrates a sequential pipeline (Scout → Strategist → Executor) where each agent receives input from the coordinator and returns results.

**Why This Pattern**: This game implements a **sequential pipeline architecture** where agents have strict dependencies. Each agent requires the previous agent's output as input, and the coordinator manages the authoritative game state. This pattern provides centralized error handling, clear data flow, and simplified state management.

**Agent-to-Agent (A2A) Communication**:

Agent-to-Agent (A2A) communication, where agents communicate directly without coordinator mediation, is an optional enhancement for advanced use cases.

**Why A2A Is Not Used Here**: The coordinator pattern is simpler, sufficient, and recommended for this game. A2A introduces additional complexity including multiple communication paths, more complex error handling, increased coupling between agents, and additional configuration requirements. A2A is designed for peer-to-peer collaboration scenarios, not sequential pipelines with centralized state management.

**When to Consider A2A**: Consider A2A only if specific requirements emerge that justify the added complexity, such as iterative refinement between agents (Strategist requests Scout re-analyze), advanced collaborative workflows, or autonomous agent negotiation.

If implementing A2A, it should use the same domain models (GameState, BoardAnalysis, Strategy, etc.) to maintain type safety and consistency. In local mode, agents can use direct method calls via dependency injection. In distributed MCP mode, agents would act as both MCP servers and clients for peer-to-peer communication.

### MCP Protocol Usage

**When MCP Is Useful**:

The MCP (Model Context Protocol) mode is useful in specific scenarios:
- **Distributed Deployments**: Agents running on separate physical machines for resource isolation or geographic distribution
- **Microservices Architecture**: Each agent as an independent service with standardized API
- **External Agent Access**: Exposing agents to external systems or third-party clients
- **Development/Learning**: Demonstrating protocol-based agent communication patterns
- **Fault Isolation**: Isolating agent failures to separate processes

**When MCP Is Not Needed**:

For single-machine deployments with co-located agents, the local mode provides better performance (< 1 second vs 3-8 seconds) without protocol overhead. MCP is a transport layer for cross-process communication, not optimized for high-frequency in-process agent coordination.

### LLM Integration Framework Options

Multiple LLM integration framework options exist with different trade-offs:

**Option 1: LangChain**

**Description**: Full-featured LLM application framework with chains, agents, and multi-provider support.

**Pros**:
- Rich ecosystem and community support
- Built-in multi-provider support (OpenAI, Anthropic, Google Gemini)
- Chain abstractions for agent workflows
- Prompt management and templates
- MCP integration available

**Cons**:
- Heavy framework with abstraction layers
- Performance overhead from middleware
- Frequent API changes between versions
- May be overkill for simple LLM calls

**Best for**: Rapid prototyping, complex agent workflows, projects requiring LangChain ecosystem tools.

**Option 2: LiteLLM**

**Description**: Lightweight unified interface for 100+ LLM providers.

**Pros**:
- Single interface for all providers
- Much lighter than LangChain
- Drop-in replacement pattern
- Minimal overhead
- Good for multi-model testing

**Cons**:
- Fewer features than LangChain
- Smaller ecosystem
- Limited agent workflow abstractions

**Best for**: Multi-provider support without framework weight, performance-sensitive applications.

**Option 3: Direct SDK Calls**

**Description**: Use provider SDKs directly (OpenAI SDK, Anthropic SDK, Google GenAI SDK).

**Pros**:
- Lightweight, minimal overhead
- Direct control over API calls
- Better performance (no middleware)
- Stable provider APIs
- Easier debugging

**Cons**:
- Need separate code per provider
- Manual prompt management
- More boilerplate code
- Provider switching requires code changes

**Best for**: Production deployments prioritizing performance, single-provider applications.

**Option 4: Instructor (Type-Safe Structured Outputs)**

**Description**: Type-safe structured outputs from LLMs using strongly-typed domain models.

**Pros**:
- Perfect fit for strongly-typed architectures
- Type-safe LLM responses validated against domain models
- Works with multiple providers
- Automatic retry and validation
- Clean, minimal API

**Cons**:
- Focused on structured outputs
- Needs to be combined with direct SDKs
- Less comprehensive than LangChain

**Best for**: Projects using strongly-typed domain models, type-safe architectures, production deployments requiring validation.

**Recommended Approach**:

Choose based on your stack and requirements:
- **Rapid Prototyping**: LangChain (rich ecosystem, quick setup)
- **Multi-Provider with Minimal Weight**: LiteLLM (lightweight, broad provider support)
- **Type-Safe Production**: Instructor + Direct SDKs (strongly-typed, validated outputs)
- **Performance-Critical**: Direct SDKs (minimal overhead, full control)

**Implementation Strategy**: Make the LLM framework selection configurable. Create an abstraction layer (LLMProvider interface) that can be implemented by any framework, allowing runtime selection via configuration.

---

## Appendix

---

This specification provides a comprehensive foundation for implementing the Tic-Tac-Toe multi-agent game with clear abstractions, type safety, and separation of concerns. The design emphasizes domain models, clean interfaces, and protocol abstraction while maintaining flexibility for different deployment scenarios.

