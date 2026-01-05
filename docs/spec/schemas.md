# JSON Schema Definitions

This document provides formal JSON Schema (OpenAPI 3.1) definitions for all domain models in the Tic-Tac-Toe Multi-Agent Game, enabling machine verification, code generation, and automated validation.

Referenced from: [spec.md Section 2.1](./spec.md#21-machine-verifiable-schema-definitions)

## Core Game Schemas

### Position Schema
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

### Board Schema
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

### GameState Schema
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

## Agent Analysis Schemas

### Threat Schema
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

### Opportunity Schema
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

### StrategicMove Schema
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

### BoardAnalysis Schema
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

## Agent Strategy Schemas

### MovePriority Enum
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

### MoveRecommendation Schema
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

### Strategy Schema
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

## Agent Execution Schemas

### ValidationError Schema
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

### MoveExecution Schema
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

## Result Wrapper Schema

### AgentResult Schema (Generic)
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

## API Request/Response Schemas

### MoveRequest Schema
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

### MoveResponse Schema
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

### GameStatusResponse Schema
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

## API Error Response Schema

### ErrorResponse Schema

All API error responses MUST follow this JSON Schema definition:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "ErrorResponse",
  "description": "Standard error response for all API errors",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["failure"],
      "description": "Always 'failure' for error responses"
    },
    "error_code": {
      "type": "string",
      "description": "Error code enum value (see spec.md Section 5 for error code enum)",
      "pattern": "^E_[A-Z_]+$"
    },
    "message": {
      "type": "string",
      "description": "Human-readable error message"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp (UTC) when error occurred"
    },
    "details": {
      "type": "object",
      "description": "Additional error context (field name, expected value, actual value, etc.)",
      "additionalProperties": true,
      "properties": {
        "field": {
          "type": "string",
          "description": "Field name that caused the error"
        },
        "expected": {
          "description": "Expected value or constraint"
        },
        "actual": {
          "description": "Actual value that caused the error"
        }
      }
    }
  },
  "required": ["status", "error_code", "message", "timestamp"],
  "additionalProperties": false
}
```

**Note**: Error codes are defined in [spec.md Section 5 Error Code Enum](./spec.md#error-code-enum). HTTP status code mappings are defined in [spec.md Section 5 HTTP Status Code Mapping](./spec.md#http-status-code-mapping).

## Schema Validation Notes

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
