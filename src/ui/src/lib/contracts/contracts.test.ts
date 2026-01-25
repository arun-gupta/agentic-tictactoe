/**
 * Contract Tests for API Response Validation
 *
 * These tests validate that:
 * 1. The contract schemas correctly validate API responses
 * 2. Sample responses from the backend conform to expected contracts
 * 3. Invalid responses are properly rejected
 *
 * This acts as the "consumer" side of consumer-driven contract testing,
 * complementing the backend's Schemathesis tests.
 */

import { describe, it, expect } from "vitest";
import {
  PositionSchema,
  GameStateSchema,
  NewGameResponseSchema,
  MoveResponseSchema,
  GameStatusResponseSchema,
  ResetGameResponseSchema,
  MoveHistorySchema,
  AgentStatusSchema,
  ErrorResponseSchema,
  PostGameMetricsSchema,
  HealthResponseSchema,
  ReadyResponseSchema,
  BoardSchema,
  PlayerSymbolSchema,
  CellValueSchema,
} from "./schemas";

// ============================================================================
// Sample Valid Responses (matching backend format)
// ============================================================================

const VALID_GAME_ID = "123e4567-e89b-12d3-a456-426614174000";

const VALID_POSITION = { row: 1, col: 1 };

const VALID_EMPTY_BOARD = [
  [null, null, null],
  [null, null, null],
  [null, null, null],
];

const VALID_PARTIAL_BOARD = [
  ["X", null, "O"],
  [null, "X", null],
  [null, null, null],
];

const VALID_GAME_STATE = {
  board: VALID_EMPTY_BOARD,
  current_player: "X",
  move_count: 0,
  is_game_over: false,
  winner: null,
  player_symbol: "X",
  ai_symbol: "O",
};

const VALID_NEW_GAME_RESPONSE = {
  game_id: VALID_GAME_ID,
  game_state: VALID_GAME_STATE,
};

const VALID_MOVE_RESPONSE = {
  success: true,
  position: VALID_POSITION,
  updated_game_state: {
    ...VALID_GAME_STATE,
    board: VALID_PARTIAL_BOARD,
    move_count: 3,
  },
  ai_move_execution: {
    position: { row: 0, col: 2 },
    reasoning: "Center control strategy",
    execution_time_ms: 150,
    success: true,
  },
  error_message: null,
  fallback_used: false,
  total_execution_time_ms: 200.5,
};

const VALID_GAME_STATUS_RESPONSE = {
  game_state: VALID_GAME_STATE,
  agent_status: { scout: "idle", strategist: "idle" },
  metrics: { total_moves: 0 },
};

const VALID_MOVE_HISTORY = {
  move_number: 1,
  player: "X",
  position: VALID_POSITION,
  timestamp: "2024-01-01T12:00:00Z",
  agent_reasoning: null,
};

const VALID_AGENT_STATUS = {
  status: "idle",
  elapsed_time_ms: null,
  execution_time_ms: null,
  success: null,
  error_message: null,
};

const VALID_ERROR_RESPONSE = {
  status: "failure",
  error_code: "E_INVALID_MOVE",
  message: "Cell is already occupied",
  timestamp: "2024-01-01T12:00:00Z",
  details: { row: 1, col: 1 },
};

const VALID_HEALTH_RESPONSE = {
  status: "healthy",
  uptime_seconds: 3600,
};

const VALID_READY_RESPONSE = {
  status: "ready",
  checks: { database: "ok", llm: "ok" },
};

const VALID_POST_GAME_METRICS = {
  game_id: VALID_GAME_ID,
  game_summary: {
    total_moves: 5,
    duration_ms: 15000,
    outcome: "X_WINS",
    average_move_time_ms: 3000,
    start_time: "2024-01-01T12:00:00Z",
    end_time: "2024-01-01T12:00:15Z",
  },
  agent_communications: [
    {
      agent_name: "Scout",
      request: { board: VALID_EMPTY_BOARD },
      response: { threats: [], opportunities: [] },
      timestamp: "2024-01-01T12:00:01Z",
      execution_time_ms: 100,
    },
  ],
  llm_interactions: [],
  agent_configs: [
    {
      agent_name: "Scout",
      mode: "local",
      llm_framework: "Pydantic AI",
      provider: null,
      model: null,
      timeout_ms: 5000,
    },
  ],
  agent_performances: [
    {
      agent_name: "Scout",
      min_execution_ms: 100,
      max_execution_ms: 150,
      avg_execution_ms: 125,
      total_calls: 3,
      successful_calls: 3,
      failed_calls: 0,
      success_rate: 1.0,
    },
  ],
  total_llm_calls: 0,
  total_tokens_used: 0,
};

// ============================================================================
// Primitive Type Contract Tests
// ============================================================================

describe("Contract: Primitive Types", () => {
  describe("PlayerSymbol", () => {
    it("accepts 'X'", () => {
      expect(PlayerSymbolSchema.safeParse("X").success).toBe(true);
    });

    it("accepts 'O'", () => {
      expect(PlayerSymbolSchema.safeParse("O").success).toBe(true);
    });

    it("rejects lowercase 'x'", () => {
      expect(PlayerSymbolSchema.safeParse("x").success).toBe(false);
    });

    it("rejects invalid symbol", () => {
      expect(PlayerSymbolSchema.safeParse("Y").success).toBe(false);
    });
  });

  describe("CellValue", () => {
    it("accepts 'X'", () => {
      expect(CellValueSchema.safeParse("X").success).toBe(true);
    });

    it("accepts 'O'", () => {
      expect(CellValueSchema.safeParse("O").success).toBe(true);
    });

    it("accepts null", () => {
      expect(CellValueSchema.safeParse(null).success).toBe(true);
    });

    it("rejects 'EMPTY' string (backend converts to null)", () => {
      expect(CellValueSchema.safeParse("EMPTY").success).toBe(false);
    });
  });
});

// ============================================================================
// Position Contract Tests
// ============================================================================

describe("Contract: Position", () => {
  it("accepts valid position", () => {
    const result = PositionSchema.safeParse(VALID_POSITION);
    expect(result.success).toBe(true);
  });

  it("accepts corner positions", () => {
    expect(PositionSchema.safeParse({ row: 0, col: 0 }).success).toBe(true);
    expect(PositionSchema.safeParse({ row: 2, col: 2 }).success).toBe(true);
  });

  it("rejects row out of bounds (negative)", () => {
    const result = PositionSchema.safeParse({ row: -1, col: 0 });
    expect(result.success).toBe(false);
  });

  it("rejects row out of bounds (too large)", () => {
    const result = PositionSchema.safeParse({ row: 3, col: 0 });
    expect(result.success).toBe(false);
  });

  it("rejects col out of bounds", () => {
    const result = PositionSchema.safeParse({ row: 0, col: 3 });
    expect(result.success).toBe(false);
  });

  it("rejects non-integer row", () => {
    const result = PositionSchema.safeParse({ row: 1.5, col: 0 });
    expect(result.success).toBe(false);
  });

  it("rejects missing row", () => {
    const result = PositionSchema.safeParse({ col: 0 });
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// Board Contract Tests
// ============================================================================

describe("Contract: Board", () => {
  it("accepts valid empty board", () => {
    const result = BoardSchema.safeParse(VALID_EMPTY_BOARD);
    expect(result.success).toBe(true);
  });

  it("accepts valid partial board", () => {
    const result = BoardSchema.safeParse(VALID_PARTIAL_BOARD);
    expect(result.success).toBe(true);
  });

  it("accepts full board", () => {
    const fullBoard = [
      ["X", "O", "X"],
      ["O", "X", "O"],
      ["O", "X", "O"],
    ];
    const result = BoardSchema.safeParse(fullBoard);
    expect(result.success).toBe(true);
  });

  it("rejects board with wrong number of rows", () => {
    const board = [
      [null, null, null],
      [null, null, null],
    ];
    const result = BoardSchema.safeParse(board);
    expect(result.success).toBe(false);
  });

  it("rejects board with wrong number of columns", () => {
    const board = [
      [null, null],
      [null, null, null],
      [null, null, null],
    ];
    const result = BoardSchema.safeParse(board);
    expect(result.success).toBe(false);
  });

  it("rejects board with invalid cell value", () => {
    const board = [
      ["X", "INVALID", null],
      [null, null, null],
      [null, null, null],
    ];
    const result = BoardSchema.safeParse(board);
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// GameState Contract Tests
// ============================================================================

describe("Contract: GameState", () => {
  it("accepts valid game state", () => {
    const result = GameStateSchema.safeParse(VALID_GAME_STATE);
    expect(result.success).toBe(true);
  });

  it("accepts game state with winner", () => {
    const stateWithWinner = {
      ...VALID_GAME_STATE,
      is_game_over: true,
      winner: "X",
    };
    const result = GameStateSchema.safeParse(stateWithWinner);
    expect(result.success).toBe(true);
  });

  it("rejects game state with move_count > 9", () => {
    const invalidState = { ...VALID_GAME_STATE, move_count: 10 };
    const result = GameStateSchema.safeParse(invalidState);
    expect(result.success).toBe(false);
  });

  it("rejects game state with negative move_count", () => {
    const invalidState = { ...VALID_GAME_STATE, move_count: -1 };
    const result = GameStateSchema.safeParse(invalidState);
    expect(result.success).toBe(false);
  });

  it("rejects game state with missing required fields", () => {
    const invalidState = { board: VALID_EMPTY_BOARD };
    const result = GameStateSchema.safeParse(invalidState);
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// NewGameResponse Contract Tests
// ============================================================================

describe("Contract: NewGameResponse", () => {
  it("accepts valid response", () => {
    const result = NewGameResponseSchema.safeParse(VALID_NEW_GAME_RESPONSE);
    expect(result.success).toBe(true);
  });

  it("rejects response with invalid game_id", () => {
    const invalid = { ...VALID_NEW_GAME_RESPONSE, game_id: "not-a-uuid" };
    const result = NewGameResponseSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });

  it("rejects response with missing game_state", () => {
    const invalid = { game_id: VALID_GAME_ID };
    const result = NewGameResponseSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// MoveResponse Contract Tests
// ============================================================================

describe("Contract: MoveResponse", () => {
  it("accepts valid successful move response", () => {
    const result = MoveResponseSchema.safeParse(VALID_MOVE_RESPONSE);
    expect(result.success).toBe(true);
  });

  it("accepts failed move response", () => {
    const failedResponse = {
      success: false,
      position: null,
      updated_game_state: null,
      ai_move_execution: null,
      error_message: "Cell is already occupied",
      fallback_used: null,
      total_execution_time_ms: null,
    };
    const result = MoveResponseSchema.safeParse(failedResponse);
    expect(result.success).toBe(true);
  });

  it("accepts response with fallback used", () => {
    const fallbackResponse = {
      ...VALID_MOVE_RESPONSE,
      fallback_used: true,
      ai_move_execution: {
        position: { row: 0, col: 0 },
        reasoning: "Fallback strategy used",
        fallback_used: true,
      },
    };
    const result = MoveResponseSchema.safeParse(fallbackResponse);
    expect(result.success).toBe(true);
  });

  it("rejects response with error_message too long", () => {
    const invalid = {
      ...VALID_MOVE_RESPONSE,
      error_message: "a".repeat(501),
    };
    const result = MoveResponseSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });

  it("rejects response with negative execution time", () => {
    const invalid = {
      ...VALID_MOVE_RESPONSE,
      total_execution_time_ms: -100,
    };
    const result = MoveResponseSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// GameStatusResponse Contract Tests
// ============================================================================

describe("Contract: GameStatusResponse", () => {
  it("accepts valid response", () => {
    const result = GameStatusResponseSchema.safeParse(VALID_GAME_STATUS_RESPONSE);
    expect(result.success).toBe(true);
  });

  it("accepts response with null optional fields", () => {
    const minimal = {
      game_state: VALID_GAME_STATE,
      agent_status: null,
      metrics: null,
    };
    const result = GameStatusResponseSchema.safeParse(minimal);
    expect(result.success).toBe(true);
  });
});

// ============================================================================
// ResetGameResponse Contract Tests
// ============================================================================

describe("Contract: ResetGameResponse", () => {
  it("accepts valid response", () => {
    const response = {
      game_id: VALID_GAME_ID,
      game_state: VALID_GAME_STATE,
    };
    const result = ResetGameResponseSchema.safeParse(response);
    expect(result.success).toBe(true);
  });
});

// ============================================================================
// MoveHistory Contract Tests
// ============================================================================

describe("Contract: MoveHistory", () => {
  it("accepts valid move history entry", () => {
    const result = MoveHistorySchema.safeParse(VALID_MOVE_HISTORY);
    expect(result.success).toBe(true);
  });

  it("accepts entry with agent reasoning", () => {
    const withReasoning = {
      ...VALID_MOVE_HISTORY,
      player: "O",
      agent_reasoning: "Scout: Found threat. Strategist: Block required.",
    };
    const result = MoveHistorySchema.safeParse(withReasoning);
    expect(result.success).toBe(true);
  });

  it("rejects entry with move_number < 1", () => {
    const invalid = { ...VALID_MOVE_HISTORY, move_number: 0 };
    const result = MoveHistorySchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// AgentStatus Contract Tests
// ============================================================================

describe("Contract: AgentStatus", () => {
  it("accepts valid idle status", () => {
    const result = AgentStatusSchema.safeParse(VALID_AGENT_STATUS);
    expect(result.success).toBe(true);
  });

  it("accepts processing status with elapsed time", () => {
    const processing = {
      status: "processing",
      elapsed_time_ms: 500,
      execution_time_ms: null,
      success: null,
      error_message: null,
    };
    const result = AgentStatusSchema.safeParse(processing);
    expect(result.success).toBe(true);
  });

  it("accepts success status", () => {
    const success = {
      status: "success",
      elapsed_time_ms: null,
      execution_time_ms: 250,
      success: true,
      error_message: null,
    };
    const result = AgentStatusSchema.safeParse(success);
    expect(result.success).toBe(true);
  });

  it("accepts failed status with error", () => {
    const failed = {
      status: "failed",
      elapsed_time_ms: null,
      execution_time_ms: 1000,
      success: false,
      error_message: "LLM timeout",
    };
    const result = AgentStatusSchema.safeParse(failed);
    expect(result.success).toBe(true);
  });

  it("rejects invalid status value", () => {
    const invalid = { ...VALID_AGENT_STATUS, status: "unknown" };
    const result = AgentStatusSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// ErrorResponse Contract Tests
// ============================================================================

describe("Contract: ErrorResponse", () => {
  it("accepts valid error response", () => {
    const result = ErrorResponseSchema.safeParse(VALID_ERROR_RESPONSE);
    expect(result.success).toBe(true);
  });

  it("accepts error without details", () => {
    const withoutDetails = { ...VALID_ERROR_RESPONSE, details: null };
    const result = ErrorResponseSchema.safeParse(withoutDetails);
    expect(result.success).toBe(true);
  });

  it("rejects error with status !== 'failure'", () => {
    const invalid = { ...VALID_ERROR_RESPONSE, status: "success" };
    const result = ErrorResponseSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });

  it("rejects error without error_code", () => {
    const invalid = { ...VALID_ERROR_RESPONSE, error_code: undefined };
    const result = ErrorResponseSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// Health/Ready Response Contract Tests
// ============================================================================

describe("Contract: HealthResponse", () => {
  it("accepts valid health response", () => {
    const result = HealthResponseSchema.safeParse(VALID_HEALTH_RESPONSE);
    expect(result.success).toBe(true);
  });

  it("rejects health response with wrong status", () => {
    const invalid = { status: "unhealthy", uptime_seconds: 100 };
    const result = HealthResponseSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});

describe("Contract: ReadyResponse", () => {
  it("accepts valid ready response", () => {
    const result = ReadyResponseSchema.safeParse(VALID_READY_RESPONSE);
    expect(result.success).toBe(true);
  });
});

// ============================================================================
// PostGameMetrics Contract Tests
// ============================================================================

describe("Contract: PostGameMetrics", () => {
  it("accepts valid post-game metrics", () => {
    const result = PostGameMetricsSchema.safeParse(VALID_POST_GAME_METRICS);
    expect(result.success).toBe(true);
  });

  it("accepts metrics with empty arrays", () => {
    const minimal = {
      ...VALID_POST_GAME_METRICS,
      agent_communications: [],
      llm_interactions: [],
      agent_configs: [],
      agent_performances: [],
    };
    const result = PostGameMetricsSchema.safeParse(minimal);
    expect(result.success).toBe(true);
  });

  it("accepts all game outcomes", () => {
    const outcomes = ["X_WINS", "O_WINS", "DRAW", "IN_PROGRESS"];
    outcomes.forEach((outcome) => {
      const metrics = {
        ...VALID_POST_GAME_METRICS,
        game_summary: { ...VALID_POST_GAME_METRICS.game_summary, outcome },
      };
      const result = PostGameMetricsSchema.safeParse(metrics);
      expect(result.success).toBe(true);
    });
  });

  it("rejects invalid success_rate (> 1)", () => {
    const invalid = {
      ...VALID_POST_GAME_METRICS,
      agent_performances: [
        { ...VALID_POST_GAME_METRICS.agent_performances[0], success_rate: 1.5 },
      ],
    };
    const result = PostGameMetricsSchema.safeParse(invalid);
    expect(result.success).toBe(false);
  });
});

// ============================================================================
// Integration: Full Response Validation
// ============================================================================

describe("Contract Integration: Full API Response Flow", () => {
  it("validates complete game flow responses", () => {
    // 1. Create game
    expect(NewGameResponseSchema.safeParse(VALID_NEW_GAME_RESPONSE).success).toBe(true);

    // 2. Make moves
    expect(MoveResponseSchema.safeParse(VALID_MOVE_RESPONSE).success).toBe(true);

    // 3. Check status
    expect(GameStatusResponseSchema.safeParse(VALID_GAME_STATUS_RESPONSE).success).toBe(true);

    // 4. Check agent status
    expect(AgentStatusSchema.safeParse(VALID_AGENT_STATUS).success).toBe(true);

    // 5. Get history
    expect(MoveHistorySchema.safeParse(VALID_MOVE_HISTORY).success).toBe(true);

    // 6. Get post-game metrics
    expect(PostGameMetricsSchema.safeParse(VALID_POST_GAME_METRICS).success).toBe(true);
  });

  it("validates error response in error scenarios", () => {
    expect(ErrorResponseSchema.safeParse(VALID_ERROR_RESPONSE).success).toBe(true);
  });
});
