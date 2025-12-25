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

**Operational Principles:**
- **Configuration over Code**: Behavior controlled through config files, environment variables, and command-line arguments
- **Hot-swappability**: LLM providers and models can be changed via configuration without code changes
- **Mode Interchangeability**: Agents can switch between local and distributed modes at runtime
- **Graceful Degradation**: System continues operating with fallback strategies when components fail

---

## 2. Domain Model Design

### Core Game Entities

**Position**: Represents a board cell with row and column (0-2). Immutable and hashable.

**Board**: A 3x3 grid of symbols (X, O, or empty). Provides methods to get/set cells, check emptiness, and list empty positions. Validates size.

**Game State**: Complete game state including:
- Current board
- Current player (player or AI)
- Move number
- Player and AI symbols
- Game over status
- Winner (if any)
- Draw status

Includes helper methods to get the current player's symbol and the opponent.

### Agent Domain Models

**Threat**: Represents an immediate threat where the opponent can win. Includes position, line type (row/column/diagonal), line index, and severity (always critical for Tic-Tac-Toe).

**Opportunity**: Represents a winning opportunity. Includes position, line type, line index, and confidence (0.0 to 1.0).

**Strategic Move**: A strategic position recommendation with position, move type (center/corner/edge/fork/block_fork), priority (1-10), and reasoning.

**Board Analysis**: Scout agent output containing:
- List of threats
- List of opportunities
- List of strategic moves
- Human-readable analysis
- Game phase (opening/midgame/endgame)
- Board evaluation score (-1.0 to 1.0)

**Move Priority**: Enum defining priority levels for move recommendations (see Priority System below for details):
- IMMEDIATE_WIN (priority: 100) - We can win on this move
- BLOCK_THREAT (priority: 90) - Opponent can win next move, must block
- FORCE_WIN (priority: 80) - Create unstoppable winning position (fork)
- PREVENT_FORK (priority: 70) - Block opponent from creating a fork
- CENTER_CONTROL (priority: 50) - Take center position (opening)
- CORNER_CONTROL (priority: 40) - Take corner position (strategic)
- EDGE_PLAY (priority: 30) - Take edge position (less strategic)
- RANDOM_VALID (priority: 10) - Any valid move (fallback)

**Move Recommendation**: Strategist output with position, priority (MovePriority enum), confidence (0.0-1.0), reasoning, and expected outcome.

**Strategy**: Strategist output containing:
- Primary move recommendation (highest priority)
- Alternative move recommendations (sorted by priority descending)
- Overall game plan
- Risk assessment (low/medium/high)

**Move Execution**: Executor output with position, success status, validation errors, execution time, reasoning, and actual priority used.

### Result Wrappers

**Agent Result**: Generic wrapper for agent outputs containing:
- Domain data (typed)
- Success/failure status
- Error message (if failed)
- Execution time in milliseconds
- Timestamp
- Optional metadata dictionary

Provides factory methods for success and error results.

---

## 2.1 Machine-Verifiable Schema Definitions

This section provides formal JSON Schema (OpenAPI 3.1) definitions for all domain models, enabling machine verification, code generation, and automated validation.

### Core Game Schemas

**Position Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Position",
  "description": "Represents a cell position on the 3x3 game board",
  "properties": {
    "row": {
      "type": "integer",
      "minimum": 0,
      "maximum": 2,
      "description": "Row index (0-2)"
    },
    "col": {
      "type": "integer",
      "minimum": 0,
      "maximum": 2,
      "description": "Column index (0-2)"
    }
  },
  "required": ["row", "col"],
  "additionalProperties": false
}
```

**Board Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Board",
  "description": "3x3 Tic-Tac-Toe game board",
  "properties": {
    "cells": {
      "type": "array",
      "description": "3x3 matrix of cell states",
      "items": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["EMPTY", "X", "O"],
          "description": "Cell state: EMPTY, X, or O"
        },
        "minItems": 3,
        "maxItems": 3
      },
      "minItems": 3,
      "maxItems": 3
    }
  },
  "required": ["cells"],
  "additionalProperties": false
}
```

**GameState Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "GameState",
  "description": "Complete game state including board, players, and status",
  "properties": {
    "game_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique game identifier (UUID v4)"
    },
    "board": {
      "$ref": "#/components/schemas/Board"
    },
    "current_player": {
      "type": "string",
      "enum": ["X", "O"],
      "description": "Current player's symbol"
    },
    "move_count": {
      "type": "integer",
      "minimum": 0,
      "maximum": 9,
      "description": "Number of moves made (0-9)"
    },
    "player_symbol": {
      "type": "string",
      "enum": ["X", "O"],
      "description": "Human player's symbol"
    },
    "ai_symbol": {
      "type": "string",
      "enum": ["X", "O"],
      "description": "AI player's symbol"
    },
    "is_game_over": {
      "type": "boolean",
      "description": "Whether the game has ended"
    },
    "winner": {
      "type": ["string", "null"],
      "enum": ["X", "O", "DRAW", null],
      "description": "Winner symbol, DRAW, or null if game ongoing"
    },
    "move_history": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "move_number": {"type": "integer"},
          "player": {"type": "string", "enum": ["X", "O"]},
          "position": {"$ref": "#/components/schemas/Position"},
          "timestamp": {"type": "string", "format": "date-time"}
        },
        "required": ["move_number", "player", "position", "timestamp"]
      },
      "description": "Chronological list of all moves"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Game creation timestamp (ISO 8601)"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Last update timestamp (ISO 8601)"
    },
    "metadata": {
      "type": "object",
      "description": "Optional metadata (agent config, experiment ID, etc.)",
      "additionalProperties": true
    }
  },
  "required": [
    "game_id",
    "board",
    "current_player",
    "move_count",
    "player_symbol",
    "ai_symbol",
    "is_game_over",
    "winner",
    "move_history",
    "created_at",
    "updated_at"
  ],
  "additionalProperties": false
}
```

### Agent Analysis Schemas

**Threat Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Threat",
  "description": "Immediate threat where opponent can win",
  "properties": {
    "position": {
      "$ref": "#/components/schemas/Position"
    },
    "line_type": {
      "type": "string",
      "enum": ["row", "column", "diagonal_main", "diagonal_anti"],
      "description": "Type of winning line threatened"
    },
    "line_index": {
      "type": "integer",
      "minimum": 0,
      "maximum": 2,
      "description": "Index of the line (for rows/columns)"
    },
    "severity": {
      "type": "string",
      "enum": ["critical"],
      "description": "Always critical for Tic-Tac-Toe"
    }
  },
  "required": ["position", "line_type", "severity"],
  "additionalProperties": false
}
```

**Opportunity Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Opportunity",
  "description": "Winning opportunity for current player",
  "properties": {
    "position": {
      "$ref": "#/components/schemas/Position"
    },
    "line_type": {
      "type": "string",
      "enum": ["row", "column", "diagonal_main", "diagonal_anti"],
      "description": "Type of winning line"
    },
    "line_index": {
      "type": "integer",
      "minimum": 0,
      "maximum": 2,
      "description": "Index of the line (for rows/columns)"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Confidence score (0.0-1.0)"
    }
  },
  "required": ["position", "line_type", "confidence"],
  "additionalProperties": false
}
```

**StrategicMove Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "StrategicMove",
  "description": "Strategic position recommendation",
  "properties": {
    "position": {
      "$ref": "#/components/schemas/Position"
    },
    "move_type": {
      "type": "string",
      "enum": ["center", "corner", "edge", "fork", "block_fork"],
      "description": "Type of strategic move"
    },
    "priority": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "description": "Priority ranking (1-10)"
    },
    "reasoning": {
      "type": "string",
      "description": "Human-readable explanation"
    }
  },
  "required": ["position", "move_type", "priority", "reasoning"],
  "additionalProperties": false
}
```

**BoardAnalysis Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "BoardAnalysis",
  "description": "Scout agent output with board analysis",
  "properties": {
    "threats": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/Threat"
      },
      "description": "List of immediate threats"
    },
    "opportunities": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/Opportunity"
      },
      "description": "List of winning opportunities"
    },
    "strategic_moves": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/StrategicMove"
      },
      "description": "List of strategic position recommendations"
    },
    "analysis": {
      "type": "string",
      "description": "Human-readable board analysis"
    },
    "game_phase": {
      "type": "string",
      "enum": ["opening", "midgame", "endgame"],
      "description": "Current game phase"
    },
    "board_score": {
      "type": "number",
      "minimum": -1.0,
      "maximum": 1.0,
      "description": "Board evaluation score (-1.0 to 1.0)"
    }
  },
  "required": [
    "threats",
    "opportunities",
    "strategic_moves",
    "analysis",
    "game_phase",
    "board_score"
  ],
  "additionalProperties": false
}
```

### Agent Strategy Schemas

**MovePriority Enum**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "string",
  "title": "MovePriority",
  "description": "Priority levels for move recommendations",
  "enum": [
    "IMMEDIATE_WIN",
    "BLOCK_THREAT",
    "FORCE_WIN",
    "PREVENT_FORK",
    "CENTER_CONTROL",
    "CORNER_CONTROL",
    "EDGE_PLAY",
    "RANDOM_VALID"
  ],
  "x-enum-values": {
    "IMMEDIATE_WIN": 100,
    "BLOCK_THREAT": 90,
    "FORCE_WIN": 80,
    "PREVENT_FORK": 70,
    "CENTER_CONTROL": 50,
    "CORNER_CONTROL": 40,
    "EDGE_PLAY": 30,
    "RANDOM_VALID": 10
  }
}
```

**MoveRecommendation Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "MoveRecommendation",
  "description": "Strategist move recommendation",
  "properties": {
    "position": {
      "$ref": "#/components/schemas/Position"
    },
    "priority": {
      "$ref": "#/components/schemas/MovePriority"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Confidence score (0.0-1.0)"
    },
    "reasoning": {
      "type": "string",
      "description": "Explanation for this recommendation"
    },
    "expected_outcome": {
      "type": "string",
      "description": "Expected result of this move"
    }
  },
  "required": ["position", "priority", "confidence", "reasoning"],
  "additionalProperties": false
}
```

**Strategy Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Strategy",
  "description": "Strategist output with move strategy",
  "properties": {
    "primary_move": {
      "$ref": "#/components/schemas/MoveRecommendation",
      "description": "Highest priority move recommendation"
    },
    "alternative_moves": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/MoveRecommendation"
      },
      "description": "Alternative moves sorted by priority descending"
    },
    "game_plan": {
      "type": "string",
      "description": "Overall strategic plan"
    },
    "risk_assessment": {
      "type": "string",
      "enum": ["low", "medium", "high"],
      "description": "Risk level assessment"
    }
  },
  "required": ["primary_move", "alternative_moves", "game_plan", "risk_assessment"],
  "additionalProperties": false
}
```

### Agent Execution Schemas

**ValidationError Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "ValidationError",
  "description": "Move validation error details",
  "properties": {
    "error_code": {
      "type": "string",
      "enum": [
        "MOVE_OUT_OF_BOUNDS",
        "MOVE_OCCUPIED",
        "GAME_ALREADY_OVER",
        "INVALID_PLAYER",
        "WRONG_TURN"
      ],
      "description": "Error code from illegal move conditions"
    },
    "message": {
      "type": "string",
      "description": "Human-readable error message"
    },
    "position": {
      "$ref": "#/components/schemas/Position",
      "description": "Position that failed validation"
    }
  },
  "required": ["error_code", "message"],
  "additionalProperties": false
}
```

**MoveExecution Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "MoveExecution",
  "description": "Executor output with move execution details",
  "properties": {
    "position": {
      "$ref": "#/components/schemas/Position",
      "description": "Executed move position"
    },
    "success": {
      "type": "boolean",
      "description": "Whether move executed successfully"
    },
    "validation_errors": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/ValidationError"
      },
      "description": "List of validation errors (if any)"
    },
    "execution_time_ms": {
      "type": "number",
      "minimum": 0,
      "description": "Execution time in milliseconds"
    },
    "reasoning": {
      "type": "string",
      "description": "Explanation of execution decision"
    },
    "priority_used": {
      "$ref": "#/components/schemas/MovePriority",
      "description": "Actual priority level used"
    }
  },
  "required": [
    "position",
    "success",
    "validation_errors",
    "execution_time_ms"
  ],
  "additionalProperties": false
}
```

### Result Wrapper Schema

**AgentResult Schema** (Generic):
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "AgentResult",
  "description": "Generic wrapper for agent outputs",
  "properties": {
    "data": {
      "oneOf": [
        { "$ref": "#/components/schemas/BoardAnalysis" },
        { "$ref": "#/components/schemas/Strategy" },
        { "$ref": "#/components/schemas/MoveExecution" }
      ],
      "description": "Typed agent output data"
    },
    "success": {
      "type": "boolean",
      "description": "Whether agent operation succeeded"
    },
    "error_message": {
      "type": ["string", "null"],
      "description": "Error message if failed"
    },
    "execution_time_ms": {
      "type": "number",
      "minimum": 0,
      "description": "Agent execution time in milliseconds"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp"
    },
    "metadata": {
      "type": "object",
      "description": "Optional metadata dictionary",
      "additionalProperties": true
    }
  },
  "required": ["data", "success", "execution_time_ms", "timestamp"],
  "additionalProperties": false
}
```

### API Request/Response Schemas

**MoveRequest Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "MoveRequest",
  "description": "API request to make a player move",
  "properties": {
    "row": {
      "type": "integer",
      "minimum": 0,
      "maximum": 2,
      "description": "Row index (0-2)"
    },
    "col": {
      "type": "integer",
      "minimum": 0,
      "maximum": 2,
      "description": "Column index (0-2)"
    }
  },
  "required": ["row", "col"],
  "additionalProperties": false
}
```

**MoveResponse Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "MoveResponse",
  "description": "API response after player move",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether move was successful"
    },
    "position": {
      "$ref": "#/components/schemas/Position",
      "description": "Position of the move (if successful)"
    },
    "game_state": {
      "$ref": "#/components/schemas/GameState",
      "description": "Updated game state"
    },
    "ai_move": {
      "$ref": "#/components/schemas/MoveExecution",
      "description": "AI move execution details (if AI moved)"
    },
    "error_message": {
      "type": ["string", "null"],
      "description": "Error message if move failed"
    }
  },
  "required": ["success", "game_state"],
  "additionalProperties": false
}
```

**GameStatusResponse Schema**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "GameStatusResponse",
  "description": "Current game status including agents and metrics",
  "properties": {
    "game_state": {
      "$ref": "#/components/schemas/GameState",
      "description": "Current game state"
    },
    "agent_status": {
      "type": "object",
      "description": "Status of each agent",
      "properties": {
        "scout": {
          "type": "object",
          "properties": {
            "status": {
              "type": "string",
              "enum": ["idle", "running", "success", "failed"]
            },
            "last_execution_ms": { "type": "number" }
          }
        },
        "strategist": {
          "type": "object",
          "properties": {
            "status": {
              "type": "string",
              "enum": ["idle", "running", "success", "failed"]
            },
            "last_execution_ms": { "type": "number" }
          }
        },
        "executor": {
          "type": "object",
          "properties": {
            "status": {
              "type": "string",
              "enum": ["idle", "running", "success", "failed"]
            },
            "last_execution_ms": { "type": "number" }
          }
        }
      },
      "additionalProperties": false
    },
    "metrics": {
      "type": "object",
      "description": "Game and agent metrics",
      "properties": {
        "total_moves": { "type": "integer" },
        "game_duration_ms": { "type": "number" },
        "avg_move_time_ms": { "type": "number" }
      },
      "additionalProperties": true
    }
  },
  "required": ["game_state", "agent_status", "metrics"],
  "additionalProperties": false
}
```

### Schema Validation Notes

**Validation Requirements**:
1. All schemas MUST validate input/output data at runtime
2. Invalid data MUST be rejected with clear error messages referencing schema violations
3. Schema violations MUST include field name, expected type/constraint, and actual value
4. Implementations SHOULD generate types/classes from these schemas

**Code Generation**:
- JSON Schema can generate: TypeScript interfaces, Python Pydantic models, Java classes, Go structs
- OpenAPI generators: Swagger Codegen, OpenAPI Generator, Postman
- Validation libraries: AJV (JavaScript), jsonschema (Python), go-playground/validator (Go)

**Schema Evolution**:
- Backward-compatible changes: Add optional fields, relax constraints
- Breaking changes: Remove fields, change types, tighten constraints
- Version schemas when making breaking changes
- Maintain migration documentation

---

## 3. Agent Architecture

### Agent Responsibilities

**Scout Agent**: Analyzes the board to identify:
- Immediate threats (opponent can win)
- Winning opportunities (we can win)
- Strategic positions (center, corners, edges)
- Game phase assessment
- Board evaluation score

Uses a fast path for rule-based checks (immediate wins/blocks) and falls back to LLM analysis for strategic decisions.

**Strategist Agent**: Synthesizes Scout analysis into a strategy:
- Prioritizes moves using the Move Priority System (see below)
- Recommends primary move with alternatives (all sorted by priority)
- Provides game plan and risk assessment
- Considers long-term position and confidence scoring

**Executor Agent**: Executes the recommended move:
- Validates move (bounds, empty cell, rules)
- Executes if valid
- Provides alternative if invalid
- Returns execution result with timing

### Agent Interface Contract

All agents implement a protocol with a single primary method:
- Scout: analyze method takes GameState, returns AgentResult containing BoardAnalysis
- Strategist: plan method takes GameState and BoardAnalysis, returns AgentResult containing Strategy
- Executor: execute method takes GameState and Strategy, returns AgentResult containing MoveExecution

Agents are stateless; all context comes from inputs. Results include execution metadata (timing, success/failure).

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
- Per-provider timeout adjustments (e.g., local Ollama may need longer timeouts)

### Move Priority System

The Move Priority System defines a strict ordering for move selection with numeric priority values and clear decision rules:

**Priority Levels (Descending Order)**:

1. **IMMEDIATE_WIN (100)**: We have two in a row and can complete three
   - Detection: Check all lines (rows, cols, diagonals) for 2 AI symbols + 1 empty
   - Action: Always take this move immediately
   - Confidence: 1.0 (guaranteed win)
   - Example: AI has X at (0,0) and (0,1), play (0,2) to win

2. **BLOCK_THREAT (90)**: Opponent has two in a row and will win next move
   - Detection: Check all lines for 2 opponent symbols + 1 empty
   - Action: Must block immediately (defensive)
   - Confidence: 1.0 (necessary to continue)
   - Example: Opponent has O at (1,0) and (1,1), must play (1,2)

3. **FORCE_WIN (80)**: Create a fork (two winning opportunities simultaneously)
   - Detection: Move creates two unblocked lines with 2 AI symbols each
   - Action: Opponent cannot block both, guarantees eventual win
   - Confidence: 0.95 (near-certain advantage)
   - Example: Play corner to create two diagonal threats

4. **PREVENT_FORK (70)**: Block opponent from creating a fork
   - Detection: Opponent's move would create two winning threats
   - Action: Block the setup position or force opponent to defend
   - Confidence: 0.85 (prevents opponent advantage)
   - Example: Block opponent's second corner when they hold opposite corner

5. **CENTER_CONTROL (50)**: Take center position (1,1)
   - Detection: Center is empty and no higher priority moves exist
   - Action: Center provides most strategic flexibility (4 lines)
   - Confidence: 0.75 (strong opening/midgame)
   - Example: First move or early game when center available

6. **CORNER_CONTROL (40)**: Take corner position (0,0 / 0,2 / 2,0 / 2,2)
   - Detection: Corner is empty and no higher priority moves exist
   - Action: Corners participate in 3 lines each (row, col, diagonal)
   - Confidence: 0.60 (solid strategic position)
   - Example: Opening move or when center taken

7. **EDGE_PLAY (30)**: Take edge position (0,1 / 1,0 / 1,2 / 2,1)
   - Detection: Edge is empty and no higher priority moves exist
   - Action: Edges only participate in 2 lines each (less strategic)
   - Confidence: 0.40 (weaker position)
   - Example: Most corners and center taken

8. **RANDOM_VALID (10)**: Any valid empty cell
   - Detection: No strategic patterns detected
   - Action: Pick any available move (fallback)
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
- All moves must be validated before recommendation
- Invalid moves (occupied, out of bounds) are automatically filtered
- If highest priority move is invalid, try next priority
- Executor performs final validation before execution

### Agent Pipeline Flow

The coordinator orchestrates a sequential pipeline:
1. Convert current game state to GameState domain model
2. Call Scout.analyze with GameState
3. If Scout succeeds, call Strategist.plan with GameState and Scout's BoardAnalysis
4. If Strategist succeeds, call Executor.execute with GameState and Strategist's Strategy
5. Extract position from Executor's MoveExecution
6. Apply move to game engine
7. Return result or fallback on any failure

Each step validates the previous result before proceeding.

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
- Only game engine may modify state (via public methods)

**State Queries**:
```python
# Read-only state access
state = game_engine.get_current_state()  # Returns GameState copy

# State checks
is_player_turn = game_engine.is_player_turn()
is_game_over = game_engine.is_game_over()
winner = game_engine.get_winner()
available_moves = game_engine.get_available_moves()
```

**State Mutations** (only via game engine):
```python
# Mutate state through engine methods
result = game_engine.make_move(position, player)
game_engine.reset_game()
```

### Benefits of State Extraction

1. **Separation of Concerns**: State is independent of game logic, agents, and UI
2. **Testability**: State can be tested independently; mock states for engine tests
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

**Cell States**: Each cell can be in exactly one of three states:
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

#### Draw Conditions

A draw can be declared in two scenarios:

**1. Complete Draw (Mandatory Detection)**:
- All 9 cells are occupied (MoveCount = 9)
- AND no player has achieved a winning line
- This MUST be detected and enforced

**2. Inevitable Draw (Optional Early Detection)**:
- MoveCount ≥ 7
- AND at least one empty cell remains
- AND no player can achieve a winning line regardless of remaining moves
- Implementation MAY detect this early for better UX

**Inevitable Draw Detection Algorithm**:

For each empty cell position P:
1. Temporarily place current player's symbol at P
2. Check if this creates a winning line
3. Temporarily place opponent's symbol at P
4. Check if this creates a winning line
5. Repeat for all remaining empty cells

If NO empty cell allows either player to win:
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

#### Illegal Move Conditions

A move is illegal if ANY of the following conditions are true:

| Condition | Description | Error Code |
|-----------|-------------|------------|
| Out of Bounds | row < 0 OR row > 2 OR col < 0 OR col > 2 | `MOVE_OUT_OF_BOUNDS` |
| Cell Occupied | Board[row][col] ≠ EMPTY | `MOVE_OCCUPIED` |
| Game Over | IsGameOver = true | `GAME_ALREADY_OVER` |
| Invalid Player | Player symbol is not X or O | `INVALID_PLAYER` |
| Wrong Turn | Player ≠ CurrentPlayer | `WRONG_TURN` |

#### Legal Move Invariants

A move at position (row, col) by player P is legal if and only if ALL of the following are true:
1. 0 ≤ row ≤ 2
2. 0 ≤ col ≤ 2
3. Board[row][col] = EMPTY
4. IsGameOver = false
5. P = CurrentPlayer
6. P ∈ {X, O}

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
- **Domain models** (GameState, BoardAnalysis, Strategy, etc.) are transport-agnostic Pydantic models
- **Service interfaces** define business operations independent of transport protocol
- **Transport adapters** translate protocol-specific requests/responses to/from domain models
- **Client libraries** can be generated from domain models for any transport

**Future Transport Options**:

| Transport Type | Use Case | Implementation Notes |
|----------------|----------|---------------------|
| **WebSocket** | Real-time updates, live game streaming | Add WebSocket endpoints wrapping existing service layer; push game state changes via events |
| **GraphQL** | Flexible queries, mobile clients | GraphQL schema generated from Pydantic models; resolvers call service layer |
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

```python
class GameService:
    def make_move(game_state: GameState, position: Position) -> MoveResponse
    def get_status() -> GameStatusResponse
    def reset_game() -> GameState
    def get_history() -> List[MoveHistory]

class AgentService:
    def get_agent_status(agent_id: str) -> AgentStatusResponse
    def get_agent_metrics(agent_id: str) -> MetricsResponse
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

**Agent Status**:
- GET /api/agents/scout/status - Get Scout agent status and metrics
- GET /api/agents/strategist/status - Get Strategist agent status and metrics
- GET /api/agents/executor/status - Get Executor agent status and metrics

**MCP Protocol** (optional, for distributed mode):
- POST /mcp/{agent_id}/tools/list - List available tools for agent
- POST /mcp/{agent_id}/tools/call - Call a tool on an agent
- GET /mcp/{agent_id}/resources/{resource_id} - Get agent resource

**Configuration** (optional, for programmatic model management):
- GET /api/config/models - Get current LLM model configuration (provider, model name, parameters)
- GET /api/config/models/available - List available models per provider
- POST /api/config/models - Update LLM model configuration (requires game reset to take effect)

**Note**: Model configuration is primarily managed through the UI Configuration Panel, config files, environment variables, or command-line arguments. Configuration API endpoints are optional and primarily useful for programmatic control, external system integration, or observability. Changing models via API should require a game reset to ensure consistency, as model changes affect agent behavior mid-game.

### Request/Response Models

**MoveRequest**: Contains row and column integers (0-2).

**MoveResponse**: Contains success status, position (if successful), updated GameState, AI move execution details (if AI moved), and error message (if failed).

**GameStatusResponse**: Contains current GameState, agent status dictionary, and metrics dictionary.

All API requests and responses must use strongly-typed, validated models. Implementation approach (Pydantic, TypeScript interfaces, Java classes, etc.) determined by technology stack choice in Section 14.

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

**US-003: View Last Move**
- As a player, I MUST see which move was made most recently
- The last move indicator MUST update after each player or AI move

**US-004: View Current Turn**
- As a player, I MUST know whose turn it is (player or AI)
- The current turn indicator MUST update after each move

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
- As a player, I MUST be able to select LLM provider (OpenAI, Anthropic, Google Gemini, Ollama)
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

---

## 6.1 UI Visual Design Specification

**Note**: Visual design specifications (colors, animations, layouts, typography, spacing, component styling) are defined separately in [docs/ui-spec.md](./ui-spec.md) with exported Figma frames. The visual designs reference the user story IDs above (US-001 through US-025) to maintain traceability between functional requirements and visual design.

Visual elements mentioned in Section 12 (Failure Matrix UI Indications) provide guidance for error state presentation but exact styling is documented in ui-spec.md.

**Figma Frames Location**: Exported PNG frames should be placed in `docs/ui/frames/` directory.

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

Note: Domain models must be strongly-typed with runtime validation. Implementation approach (Pydantic, dataclasses, TypeScript, etc.) determined by Section 14. MovePriority enum defines 8 priority levels (IMMEDIATE_WIN=100, BLOCK_THREAT=90, FORCE_WIN=80, PREVENT_FORK=70, CENTER_CONTROL=50, CORNER_CONTROL=40, EDGE_PLAY=30, RANDOM_VALID=10) - see Section 3 for full priority system specification.

**agents/**: Agent implementations:
- interfaces.py: Abstract base classes and protocols
- scout_local.py: Local Scout implementation using configured LLM framework
- strategist_local.py: Local Strategist implementation using configured LLM framework
- executor_local.py: Local Executor implementation using configured LLM framework
- scout_mcp.py: Scout with MCP protocol support
- strategist_mcp.py: Strategist with MCP protocol support
- executor_mcp.py: Executor with MCP protocol support
- base_mcp_agent.py: Base class for MCP protocol support

Note: Agents use an LLM framework abstraction layer that supports multiple providers. LLM framework choice (LangChain, LiteLLM, Instructor, Direct SDKs) determines the multi-provider abstraction implementation - see Section 19.

**game/**: Game logic:
- engine.py: Core game rules and state management
- coordinator.py: Orchestrates agent pipeline
- state.py: Game state management (if separate from engine)

**services/**: Service layer (transport-agnostic business logic):
- game_service.py: Game operations (make_move, get_status, reset, history)
- agent_service.py: Agent operations (status, metrics)
- interfaces.py: Service interface definitions

**api/**: REST API transport layer:
- main.py: API application setup and routes
- routes/game.py: Game management REST endpoints (wraps game_service)
- routes/agents.py: Agent status REST endpoints (wraps agent_service)
- routes/mcp.py: MCP protocol endpoints (optional)
- adapters/rest_adapter.py: Converts REST requests/responses to/from domain models

Note: REST endpoints are thin wrappers around service layer. Implementation framework choice (FastAPI, Flask, Express, etc.) determined by Section 14. Future transports (WebSocket, GraphQL, CLI) would add new directories with their own adapters.

**ui/**: Web-based UI application:
- main_app: Main UI application entry point
- components/board: Game board component
- components/metrics: Metrics dashboard component
- components/insights: Agent insights component

Note: UI framework choice (Streamlit, React, Vue, etc.) determined by Section 14.

**models/**: LLM management:
- shared_llm.py: Shared LLM connection manager with pooling
- factory.py: LLM provider factory supporting multi-provider frameworks
- provider_adapter.py: Abstraction layer for different LLM frameworks

**utils/**: Utilities:
- config.py: Configuration management
- validators.py: Validation helpers

**tests/**: Test suite:
- test_game_engine.py: Game logic tests
- test_agents.py: Agent tests
- test_api.py: API endpoint tests
- test_integration.py: End-to-end tests

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
- Multi-provider support (OpenAI, Anthropic, Google, Ollama)
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
- LLM Provider APIs (at least one of: OpenAI, Anthropic, Google, Ollama)
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

**LLM Provider Configuration**: Provider selection (OpenAI, Anthropic, Google Gemini, Ollama), API keys (from environment), model name per provider (one model per provider), temperature and other parameters, token limits. Default models: OpenAI uses gpt-5.2, Anthropic uses claude-opus-4.5, Google Gemini uses gemini-3-flash. Model names are configurable in config file.

**Game Configuration**: Default player symbol, AI symbol, game rules (if configurable), move timeout.

**MCP Configuration** (if using MCP mode): Port assignments per agent, server URLs for distributed mode, protocol settings, transport type (stdio, HTTP, SSE).

**Port Configuration**: All service ports must be configurable through the configuration file. API server port (default: 8000), Streamlit UI port (default: 8501), MCP agent server ports (if using distributed mode). No hardcoded ports in application code.

**UI Configuration**: Streamlit theme, refresh intervals, metrics display preferences, debug mode.

### Configuration Sources

**config.json**: Main configuration file with default settings.

**.env file**: Environment-specific settings (API keys, secrets, local paths).

**Environment Variables**: Override config.json values. Prefixed with project name to avoid conflicts.

**Command-line Arguments**: Override for quick testing (model selection, mode selection).

Configuration is loaded in priority order: defaults in code, config.json, .env file, environment variables, command-line arguments.

---

## 10. Deployment Considerations

### Local Development

**Single Process**: All components (API, agents, UI) run in one process. FastAPI and Streamlit can run in same process or separate processes on different ports.

**Development Server**: Use uvicorn reload mode for API, Streamlit auto-reload for UI.

**Debug Mode**: Enable verbose logging, detailed error messages, agent reasoning display.

### Production Deployment

**Separate Services**: API server, Streamlit UI, and agent services (if distributed) as separate processes or containers.

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
- Base image: Python 3.11+
- Install dependencies from requirements.txt
- Copy application code
- Expose ports: 8000 (API) and 8501 (UI)
- Default command to run the application

**Docker Compose**:

**docker-compose.yml**: Simple compose file for local development
- Services: api (FastAPI) and ui (Streamlit)
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

### Unit Tests

**Domain Models**: Test Pydantic model validation, edge cases, helper methods. Schema validation for all domain models to ensure type safety and data integrity.

**Game Engine**: Test move validation, win detection, draw detection, state management. Use parameterized tests for multiple scenarios to cover all game states efficiently.

**Agents**: Test each agent in isolation with mocked LLM, validate input/output types, test error handling. Agent interface contract validation to ensure all agents comply with protocol definitions.

**Test Data Management**: Fixture strategies for common game states (opening, midgame, endgame, win scenarios). Test data generators for board positions to create diverse test cases programmatically.

### Integration Tests

**Agent Pipeline**: Test full pipeline (Scout → Strategist → Executor) with real or mocked LLM.

**API Endpoints**: Test API endpoints with test client, validate request/response models, test error cases.

**Game Flow**: Test complete game from start to finish, test win/loss/draw scenarios, test player and AI moves.

**Contract Tests**: API contract tests between UI and backend to ensure interface compatibility and prevent breaking changes.

**MCP Protocol Tests**: Test MCP client/server communication, protocol compliance, and mode switching between local and distributed modes.

### End-to-End Tests

**Full System**: Test with Streamlit UI, FastAPI backend, and real agents. Test user interactions, verify game state persistence, test metrics collection.

### Performance Tests

**Agent Response Times**: Measure agent execution times, identify bottlenecks, test with different LLM providers.

**Concurrent Games**: Test multiple simultaneous games, verify no state leakage, test resource usage.

### Resilience Tests

**LLM Failure Scenarios**: Simulate LLM timeouts/failures to verify graceful degradation and fallback strategies work correctly.

**Agent Failure Cascade Testing**: Test system behavior when agents fail in sequence, verify error propagation and recovery mechanisms.

### Test Coverage

**Coverage Targets**: Minimum code coverage targets of 80% for unit tests and 70% for integration tests. Use pytest-cov for coverage reporting.

**Critical Path Testing**: Critical path smoke tests for CI/CD to validate core functionality in automated pipelines.

### CI/CD Integration

**GitHub Actions**: Integration with GitHub Actions for automated testing on pull requests and commits. Run unit tests, integration tests, and smoke tests in CI pipeline. Enforce coverage thresholds before merging.

---

## 12. Error Handling and Resilience

### Error Categories

**Validation Errors**: Invalid moves, malformed requests, type mismatches. Return clear error messages with validation details.

**Agent Errors**: LLM failures, timeout errors, parsing errors. Log details, return fallback responses, continue game if possible.

**System Errors**: Network failures, database errors, configuration errors. Log critical errors, provide user-friendly messages, implement circuit breakers if needed.

### Comprehensive Failure Matrix

This table defines deterministic behavior for all failure scenarios:

| Error Type | Error Code | Retry Policy | Fallback Strategy | User Message | UI Indication | Log Level | Test Coverage |
|------------|------------|--------------|-------------------|--------------|---------------|-----------|---------------|
| **LLM API Timeout** | `LLM_TIMEOUT` | 3 retries, exponential backoff (1s, 2s, 4s); per-agent timeouts: Scout 5s, Strategist 5s, Executor 3s (local mode) | Use rule-based move selection | "AI is taking longer than expected. Using quick analysis..." | Orange warning icon, show retry countdown | WARNING | Resilience test required |
| **LLM Parse Error** | `LLM_PARSE_ERROR` | 2 retries with prompt refinement | Use previous successful agent output or rule-based | "AI response unclear. Using backup strategy..." | Yellow warning badge, show "Using fallback" | ERROR | Unit test required |
| **LLM Rate Limit** | `LLM_RATE_LIMIT` | Wait + retry once after rate limit window | Queue request or use cached response | "AI is busy. Please wait a moment..." | Blue info icon, show wait timer | WARNING | Integration test required |
| **LLM Invalid API Key** | `LLM_AUTH_ERROR` | No retry | Fallback to rule-based moves entirely | "AI configuration error. Using rule-based play." | Red error banner, persist for session | CRITICAL | Smoke test required |
| **Scout Agent Failure** | `SCOUT_FAILED` | 1 retry | Use rule-based board analysis (immediate wins/blocks/center) | "AI analysis unavailable. Using standard tactics..." | Orange agent status icon, show "Rule-based mode" | ERROR | Resilience test required |
| **Strategist Agent Failure** | `STRATEGIST_FAILED` | 1 retry | Use Scout's highest priority opportunity directly | "AI strategy unavailable. Using tactical move..." | Orange agent status icon, show "Tactical mode" | ERROR | Resilience test required |
| **Executor Agent Failure** | `EXECUTOR_FAILED` | 1 retry | Use Strategist's primary move with basic validation | "AI execution error. Applying recommended move..." | Orange agent status icon, show "Direct execution" | ERROR | Resilience test required |
| **Invalid Move (Out of Bounds)** | `MOVE_OUT_OF_BOUNDS` | No retry | Return error to user, request new move | "Invalid move: Position out of bounds (0-2 only)" | Red cell highlight, shake animation | INFO | Unit test required |
| **Invalid Move (Cell Occupied)** | `MOVE_OCCUPIED` | No retry | Return error to user, request new move | "Invalid move: Cell already occupied" | Red cell highlight, pulse animation | INFO | Unit test required |
| **MCP Connection Failed** | `MCP_CONN_FAILED` | 2 retries with 5s delay | Switch to local mode agents | "Distributed mode unavailable. Using local agents..." | Yellow mode indicator, show "Local mode active" | ERROR | Integration test required |
| **MCP Agent Timeout** | `MCP_TIMEOUT` | 1 retry with 10s timeout | Switch to local mode for that agent | "Agent not responding. Using local fallback..." | Orange agent icon, show timeout countdown | WARNING | Resilience test required |
| **API Request Malformed** | `API_MALFORMED` | No retry | Return 400 Bad Request with validation details | "Invalid request: [specific validation error]" | Red toast notification, 5s auto-dismiss | INFO | Contract test required |
| **Game State Corrupted** | `STATE_CORRUPTED` | No retry | Reset game state, log incident | "Game state error. Please restart the game." | Red modal dialog, require user acknowledgment | CRITICAL | Integration test required |
| **Network Error (API)** | `NETWORK_ERROR` | 3 retries with exponential backoff | Show cached state, allow offline mode | "Connection lost. Retrying..." | Gray offline indicator, show retry attempt (1/3) | WARNING | E2E test required |
| **Configuration Error** | `CONFIG_ERROR` | No retry | Use default configuration | "Configuration issue. Using defaults..." | Yellow banner at top, dismissible | ERROR | Smoke test required |
| **Schema Validation Error** | `SCHEMA_VALIDATION_ERROR` | No retry | Log error, return sanitized default | "Data format error. Using safe defaults..." | Yellow toast notification, 5s auto-dismiss | ERROR | Unit test required |

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
    },
    "ollama": {
      "models": {
        "llama3.2": {
          "cost_per_1k_input_tokens": 0.0,
          "cost_per_1k_output_tokens": 0.0,
          "avg_latency_ms": 3000,
          "max_tokens": 128000,
          "context_window": 128000,
          "supports_streaming": true,
          "reliability_score": 0.90,
          "last_updated": "2025-01-15",
          "requires_local_install": true
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

**Simple Storage**:

Store one JSON file per game in `logs/games/{game_id}.json` with the 7 core metrics.

For analytics, periodically aggregate into `logs/analytics/summary_{date}.json`.

**Optional Database** (for complex queries):
- `games` table with the 7 metrics + agent_config + timestamp
- Simple SELECT queries for aggregation and comparison

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

**Input Validation**: All inputs validated via Pydantic models, sanitize user inputs, prevent injection attacks.

**Rate Limiting**: Limit API request rates, prevent abuse, implement per-user limits if multi-user.

**Authentication** (if multi-user): Implement user authentication, session management, authorization checks.

### Data Security

**API Keys**: Store in environment variables, never commit to version control, use secrets management in production.

**Game State**: Validate game state integrity, prevent state manipulation, log state changes.

**Agent Communication**: If using MCP over network, use HTTPS, validate MCP protocol messages, prevent unauthorized agent access.

---

# PART II: IMPLEMENTATION GUIDANCE (NON-NORMATIVE)

This section provides recommended approaches for implementing the core specification. These are guidelines, not requirements. Technologies and frameworks may be substituted as long as they satisfy the normative requirements in Part I.

---

## 14. Implementation Technology Stack

### Recommended Technologies

The following technology stack is recommended based on proven effectiveness, but alternatives may be used:

**Backend Framework:**
- **Recommended**: FastAPI (Python)
- **Alternatives**: Flask, Django REST Framework, Express.js, Spring Boot
- **Requirements Met**: REST API support, async operations, OpenAPI documentation

**Data Validation:**
- **Recommended**: Pydantic (Python)
- **Alternatives**: Marshmallow, dataclasses + validators, TypeScript interfaces, Java Bean Validation
- **Requirements Met**: Type safety, runtime validation, serialization/deserialization

**UI Framework:**
- **Recommended**: Streamlit (Python)
- **Alternatives**: React, Vue.js, Angular, Svelte, Next.js
- **Requirements Met**: Web-based interface, API client, interactive components

**LLM Integration:**
- **Recommended**: See Section 19 (LangChain, LiteLLM, Instructor, or Direct SDKs)
- **Alternatives**: Any framework supporting multiple LLM providers
- **Requirements Met**: Multi-provider support, hot-swapping, connection pooling

**Testing Framework:**
- **Recommended**: pytest (Python)
- **Alternatives**: unittest, Jest, JUnit, RSpec
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

## 15. Performance Optimization

### Agent Performance

**Fast Path Analysis**: Rule-based checks for immediate wins/blocks before LLM calls, cache common patterns, optimize LLM prompts.

**Shared LLM Connection**: Reuse LLM connections across agents, connection pooling, efficient token usage.

**Async Operations**: All agent calls are async, parallel execution where possible, non-blocking I/O.

### Game Performance

**State Management**: Efficient board representation, minimize state copies, lazy evaluation where possible.

**UI Performance**: Efficient Streamlit reruns, minimize data transfer, use caching for expensive operations.

### Scalability

**Stateless Agents**: Agents are stateless, can be scaled horizontally, easy to distribute.

**Efficient Protocols**: MCP protocol is lightweight, minimal overhead, efficient serialization.

---

## 15. Agent Mode Architecture

### Mode 1: Local (Fast)

**Description**: In-process agent execution using an LLM framework with shared connection pooling. No MCP protocol overhead. The LLM framework (LangChain, LiteLLM, Instructor, or Direct SDKs - see Section 19) provides multi-provider support, allowing LLM provider switching via configuration.

**Characteristics**:
- Fast execution (< 1 second per move)
- Direct Python method calls between coordinator and agents
- Shared LLM connection for efficiency
- Rule-based pre-checks for immediate wins/blocks
- LLM provider hot-swapping via configuration
- Best for production use

**Implementation**: Agents implement interfaces using the configured LLM framework. Coordinator calls agents via direct Python methods. The framework handles provider abstraction and connection management.

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

**Ollama**: Local models. Model name must be specified in config file (e.g., `llama3.2`, `mistral`).

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

**Streamlit Dashboard**: Real-time metrics display with charts and tables.

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
- Built-in multi-provider support (OpenAI, Anthropic, Google, Ollama)
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

**Option 4: Instructor (with Pydantic)**

**Description**: Type-safe structured outputs from LLMs using Pydantic models.

**Pros**:
- Perfect fit for Pydantic-based architectures (like this project)
- Type-safe LLM responses validated against domain models
- Works with multiple providers
- Automatic retry and validation
- Clean, minimal API

**Cons**:
- Focused on structured outputs
- Needs to be combined with direct SDKs
- Less comprehensive than LangChain

**Best for**: Projects using Pydantic domain models, type-safe architectures, production deployments requiring validation.

**Recommended Approach**:

For this project, **Instructor + Direct SDKs** is recommended for production use due to:
- Existing Pydantic domain models (BoardAnalysis, Strategy, MoveExecution)
- Type-safe validation of agent outputs
- Lightweight and performant
- Easy provider switching via configuration

**LangChain** remains a valid choice for rapid prototyping and if ecosystem features are needed.

**Implementation Strategy**: Make the LLM framework selection configurable. Create an abstraction layer (LLMProvider interface) that can be implemented by any framework, allowing runtime selection via configuration.

---

## Appendix

---

This specification provides a comprehensive foundation for implementing the Tic-Tac-Toe multi-agent game with clear abstractions, type safety, and separation of concerns. The design emphasizes domain models, clean interfaces, and protocol abstraction while maintaining flexibility for different deployment scenarios.

