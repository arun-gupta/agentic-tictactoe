/**
 * Contract Schemas for API Type Validation
 *
 * These Zod schemas define the expected API contract between the frontend and backend.
 * They mirror the backend Pydantic models and are used for:
 * 1. Runtime validation of API responses
 * 2. Contract testing to ensure frontend/backend alignment
 * 3. Type inference (Zod schemas can infer TypeScript types)
 *
 * IMPORTANT: These schemas MUST stay in sync with:
 * - Backend models: src/api/models.py
 * - Backend domain: src/domain/models.py
 * - OpenAPI schema: /openapi.json
 */

import { z } from "zod";

// ============================================================================
// Primitive Types
// ============================================================================

export const PlayerSymbolSchema = z.enum(["X", "O"]);

export const CellValueSchema = z.union([
  z.literal("X"),
  z.literal("O"),
  z.null(),
]);

export const AgentStatusValueSchema = z.enum([
  "idle",
  "processing",
  "success",
  "failed",
]);

export const GameOutcomeSchema = z.enum([
  "X_WINS",
  "O_WINS",
  "DRAW",
  "IN_PROGRESS",
]);

export const AgentModeSchema = z.enum(["local", "mcp"]);

// ============================================================================
// Domain Models
// ============================================================================

/**
 * Position on the game board
 * Matches: src/domain/models.py::Position
 */
export const PositionSchema = z.object({
  row: z.number().int().min(0).max(2),
  col: z.number().int().min(0).max(2),
});

/**
 * Game board state - 3x3 grid
 * Matches: src/domain/models.py::Board (serialized)
 */
export const BoardSchema = z.array(
  z.array(CellValueSchema).length(3)
).length(3);

/**
 * Complete game state
 * Matches: src/domain/models.py::GameState (serialized)
 */
export const GameStateSchema = z.object({
  board: BoardSchema,
  current_player: PlayerSymbolSchema,
  move_count: z.number().int().min(0).max(9),
  is_game_over: z.boolean(),
  winner: PlayerSymbolSchema.nullable(),
  player_symbol: PlayerSymbolSchema,
  ai_symbol: PlayerSymbolSchema,
});

// ============================================================================
// Agent Models
// ============================================================================

/**
 * Move execution details from AI
 * Matches: src/domain/agent_models.py::MoveExecution
 */
export const MoveExecutionSchema = z.object({
  position: PositionSchema.nullable(),
  confidence: z.number().min(0).max(1).optional(),
  reasoning: z.string().nullable(),
  fallback_used: z.boolean().optional(),
  execution_time_ms: z.number().min(0).optional(),
  success: z.boolean().optional(),
});

/**
 * Agent status response
 * Matches: src/api/models.py::AgentStatus
 */
export const AgentStatusSchema = z.object({
  status: AgentStatusValueSchema,
  elapsed_time_ms: z.number().min(0).nullable(),
  execution_time_ms: z.number().min(0).nullable(),
  success: z.boolean().nullable(),
  error_message: z.string().nullable(),
});

// ============================================================================
// API Request Models
// ============================================================================

/**
 * New game request
 * Matches: src/api/models.py::NewGameRequest
 */
export const NewGameRequestSchema = z.object({
  player_symbol: PlayerSymbolSchema.optional(),
});

/**
 * Move request
 * Matches: src/api/models.py::MoveRequest
 */
export const MoveRequestSchema = z.object({
  game_id: z.string().uuid(),
  row: z.number().int().min(0).max(2),
  col: z.number().int().min(0).max(2),
});

/**
 * Reset game request
 * Matches: src/api/models.py::ResetGameRequest
 */
export const ResetGameRequestSchema = z.object({
  game_id: z.string().uuid(),
});

// ============================================================================
// API Response Models
// ============================================================================

/**
 * New game response
 * Matches: src/api/models.py::NewGameResponse
 */
export const NewGameResponseSchema = z.object({
  game_id: z.string().uuid(),
  game_state: GameStateSchema,
});

/**
 * Move response
 * Matches: src/api/models.py::MoveResponse
 */
export const MoveResponseSchema = z.object({
  success: z.boolean(),
  position: PositionSchema.nullable(),
  updated_game_state: GameStateSchema.nullable(),
  ai_move_execution: MoveExecutionSchema.nullable(),
  error_message: z.string().max(500).nullable(),
  fallback_used: z.boolean().nullable(),
  total_execution_time_ms: z.number().min(0).nullable(),
});

/**
 * Game status response
 * Matches: src/api/models.py::GameStatusResponse
 */
export const GameStatusResponseSchema = z.object({
  game_state: GameStateSchema,
  agent_status: z.record(z.string(), z.any()).nullable(),
  metrics: z.record(z.string(), z.any()).nullable(),
});

/**
 * Reset game response
 * Matches: src/api/models.py::ResetGameResponse
 */
export const ResetGameResponseSchema = z.object({
  game_id: z.string().uuid(),
  game_state: GameStateSchema,
});

/**
 * Move history entry
 * Matches: src/api/models.py::MoveHistory
 */
export const MoveHistorySchema = z.object({
  move_number: z.number().int().min(1),
  player: PlayerSymbolSchema,
  position: PositionSchema,
  timestamp: z.string().datetime({ offset: true }).or(z.string()), // ISO 8601
  agent_reasoning: z.string().nullable(),
});

/**
 * Error response
 * Matches: src/api/models.py::ErrorResponse
 */
export const ErrorResponseSchema = z.object({
  status: z.literal("failure"),
  error_code: z.string(),
  message: z.string(),
  timestamp: z.string().datetime({ offset: true }).or(z.string()), // ISO 8601
  details: z.record(z.string(), z.any()).nullable(),
});

// ============================================================================
// Post-Game Metrics Models
// ============================================================================

/**
 * Agent communication record
 */
export const AgentCommunicationSchema = z.object({
  agent_name: z.string(),
  request: z.record(z.string(), z.any()),
  response: z.record(z.string(), z.any()),
  timestamp: z.string().datetime({ offset: true }).or(z.string()),
  execution_time_ms: z.number().min(0),
});

/**
 * LLM interaction record
 */
export const LLMInteractionSchema = z.object({
  agent_name: z.string(),
  prompt: z.string(),
  response: z.string(),
  model: z.string(),
  provider: z.string(),
  input_tokens: z.number().int().min(0),
  output_tokens: z.number().int().min(0),
  total_tokens: z.number().int().min(0),
  latency_ms: z.number().min(0),
  timestamp: z.string().datetime({ offset: true }).or(z.string()).optional(),
});

/**
 * Agent configuration
 */
export const AgentConfigSchema = z.object({
  agent_name: z.string(),
  mode: AgentModeSchema,
  llm_framework: z.string(),
  provider: z.string().nullable(),
  model: z.string().nullable(),
  timeout_ms: z.number().int().min(0),
});

/**
 * Agent performance metrics
 */
export const AgentPerformanceSchema = z.object({
  agent_name: z.string(),
  min_execution_ms: z.number().min(0),
  max_execution_ms: z.number().min(0),
  avg_execution_ms: z.number().min(0),
  total_calls: z.number().int().min(0),
  successful_calls: z.number().int().min(0),
  failed_calls: z.number().int().min(0),
  success_rate: z.number().min(0).max(1),
});

/**
 * Game summary
 */
export const GameSummarySchema = z.object({
  total_moves: z.number().int().min(0).max(9),
  duration_ms: z.number().min(0),
  outcome: GameOutcomeSchema,
  average_move_time_ms: z.number().min(0),
  start_time: z.string().datetime({ offset: true }).or(z.string()),
  end_time: z.string().datetime({ offset: true }).or(z.string()).nullable(),
});

/**
 * Post-game metrics response
 */
export const PostGameMetricsSchema = z.object({
  game_id: z.string().uuid(),
  game_summary: GameSummarySchema,
  agent_communications: z.array(AgentCommunicationSchema),
  llm_interactions: z.array(LLMInteractionSchema),
  agent_configs: z.array(AgentConfigSchema),
  agent_performances: z.array(AgentPerformanceSchema),
  total_llm_calls: z.number().int().min(0),
  total_tokens_used: z.number().int().min(0),
});

// ============================================================================
// Health Check Models
// ============================================================================

/**
 * Health check response
 */
export const HealthResponseSchema = z.object({
  status: z.literal("healthy"),
  uptime_seconds: z.number().min(0),
});

/**
 * Ready check response
 */
export const ReadyResponseSchema = z.object({
  status: z.literal("ready"),
  checks: z.record(z.string(), z.string()),
});

// ============================================================================
// Type Exports (inferred from schemas)
// ============================================================================

export type ContractPosition = z.infer<typeof PositionSchema>;
export type ContractGameState = z.infer<typeof GameStateSchema>;
export type ContractNewGameResponse = z.infer<typeof NewGameResponseSchema>;
export type ContractMoveResponse = z.infer<typeof MoveResponseSchema>;
export type ContractGameStatusResponse = z.infer<typeof GameStatusResponseSchema>;
export type ContractErrorResponse = z.infer<typeof ErrorResponseSchema>;
export type ContractAgentStatus = z.infer<typeof AgentStatusSchema>;
export type ContractMoveHistory = z.infer<typeof MoveHistorySchema>;
export type ContractPostGameMetrics = z.infer<typeof PostGameMetricsSchema>;
