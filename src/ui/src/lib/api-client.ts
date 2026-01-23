/**
 * API Client for Agentic Tic-Tac-Toe REST API
 *
 * Phase 8.0.2: API Client
 * - TypeScript wrapper for REST API
 * - Methods: createGame(), makeMove(), getGameStatus(), resetGame()
 * - Error handling with user-friendly messages
 */

// API Types matching backend Pydantic models

export type PlayerSymbol = "X" | "O";
export type CellValue = "X" | "O" | null;

export interface Position {
  row: number;
  col: number;
}

export interface GameState {
  board: CellValue[][];
  current_player: PlayerSymbol;
  move_count: number;
  is_game_over: boolean;
  winner: PlayerSymbol | null;
  player_symbol: PlayerSymbol;
  ai_symbol: PlayerSymbol;
}

export interface MoveExecution {
  position: Position | null;
  confidence?: number;
  reasoning: string | null;
  fallback_used?: boolean;
  execution_time_ms?: number;
  success?: boolean;
}

export interface NewGameRequest {
  player_symbol?: PlayerSymbol;
}

export interface NewGameResponse {
  game_id: string;
  game_state: GameState;
}

export interface MoveRequest {
  game_id: string;
  row: number;
  col: number;
}

export interface MoveResponse {
  success: boolean;
  position: Position | null;
  updated_game_state: GameState | null;
  ai_move_execution: MoveExecution | null;
  error_message: string | null;
  fallback_used: boolean | null;
  total_execution_time_ms: number | null;
}

export interface GameStatusResponse {
  game_state: GameState;
  agent_status: Record<string, unknown> | null;
  metrics: Record<string, unknown> | null;
}

export interface ResetGameRequest {
  game_id: string;
}

export interface ResetGameResponse {
  game_id: string;
  game_state: GameState;
}

export interface MoveHistory {
  move_number: number;
  player: PlayerSymbol;
  position: Position;
  timestamp: string;
  agent_reasoning: string | null;
}

export interface AgentStatus {
  status: "idle" | "processing" | "success" | "failed";
  elapsed_time_ms: number | null;
  execution_time_ms: number | null;
  success: boolean | null;
  error_message: string | null;
}

export interface ErrorResponse {
  status: "failure";
  error_code: string;
  message: string;
  timestamp: string;
  details: Record<string, unknown> | null;
}

// Post-Game Metrics Types (Phase 8.4)

export interface AgentCommunication {
  agent_name: string;
  request: Record<string, unknown>;
  response: Record<string, unknown>;
  timestamp: string;
  execution_time_ms: number;
}

export interface LLMInteraction {
  agent_name: string;
  prompt: string;
  response: string;
  model: string;
  provider: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  latency_ms: number;
  timestamp: string;
}

export interface AgentConfig {
  agent_name: string;
  mode: "local" | "mcp";
  llm_framework: string;
  provider: string | null;
  model: string | null;
  timeout_ms: number;
}

export interface AgentPerformance {
  agent_name: string;
  min_execution_ms: number;
  max_execution_ms: number;
  avg_execution_ms: number;
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  success_rate: number;
}

export interface GameSummary {
  total_moves: number;
  duration_ms: number;
  outcome: "X_WINS" | "O_WINS" | "DRAW" | "IN_PROGRESS";
  average_move_time_ms: number;
  start_time: string;
  end_time: string | null;
}

export interface PostGameMetrics {
  game_id: string;
  game_summary: GameSummary;
  agent_communications: AgentCommunication[];
  llm_interactions: LLMInteraction[];
  agent_configs: AgentConfig[];
  agent_performances: AgentPerformance[];
  total_llm_calls: number;
  total_tokens_used: number;
}

// API Error class for typed error handling
export class ApiError extends Error {
  public readonly errorCode: string;
  public readonly statusCode: number;
  public readonly details: Record<string, unknown> | null;

  constructor(
    message: string,
    errorCode: string,
    statusCode: number,
    details: Record<string, unknown> | null = null
  ) {
    super(message);
    this.name = "ApiError";
    this.errorCode = errorCode;
    this.statusCode = statusCode;
    this.details = details;
  }
}

// Network error class
export class NetworkError extends Error {
  constructor(message: string = "Network error. Please check your connection.") {
    super(message);
    this.name = "NetworkError";
  }
}

// API Client configuration
export interface ApiClientConfig {
  baseUrl: string;
  timeout?: number;
}

const DEFAULT_CONFIG: ApiClientConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 30000,
};

/**
 * API Client for interacting with the Tic-Tac-Toe backend
 */
export class ApiClient {
  private readonly baseUrl: string;
  private readonly timeout: number;

  constructor(config: Partial<ApiClientConfig> = {}) {
    const mergedConfig = { ...DEFAULT_CONFIG, ...config };
    this.baseUrl = mergedConfig.baseUrl;
    this.timeout = mergedConfig.timeout || 30000;
  }

  /**
   * Make an HTTP request with error handling
   */
  private async request<T>(
    method: "GET" | "POST",
    path: string,
    body?: unknown
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await response.json();

      if (!response.ok) {
        // Handle error responses
        const errorResponse = data as ErrorResponse;
        throw new ApiError(
          errorResponse.message || this.getErrorMessage(response.status),
          errorResponse.error_code || "UNKNOWN_ERROR",
          response.status,
          errorResponse.details
        );
      }

      return data as T;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof ApiError) {
        throw error;
      }

      if (error instanceof Error) {
        if (error.name === "AbortError") {
          throw new NetworkError("Request timed out. Please try again.");
        }
        if (error.message.includes("fetch")) {
          throw new NetworkError("Unable to connect to server. Please check if the server is running.");
        }
      }

      throw new NetworkError();
    }
  }

  /**
   * Get user-friendly error message for HTTP status codes
   */
  private getErrorMessage(statusCode: number): string {
    switch (statusCode) {
      case 400:
        return "Invalid request. Please check your input.";
      case 404:
        return "Resource not found.";
      case 422:
        return "Validation error. Please check your input.";
      case 500:
        return "Server error. Please try again later.";
      case 503:
        return "Service unavailable. Please try again later.";
      default:
        return "An unexpected error occurred.";
    }
  }

  /**
   * Create a new game session
   *
   * @param playerSymbol - Optional player symbol preference ('X' or 'O')
   * @returns New game response with game_id and initial state
   */
  async createGame(playerSymbol?: PlayerSymbol): Promise<NewGameResponse> {
    const body: NewGameRequest | undefined = playerSymbol
      ? { player_symbol: playerSymbol }
      : undefined;

    return this.request<NewGameResponse>("POST", "/api/game/new", body);
  }

  /**
   * Make a player move
   *
   * @param gameId - Game session ID
   * @param row - Row index (0-2)
   * @param col - Column index (0-2)
   * @returns Move response with updated state and AI move
   */
  async makeMove(gameId: string, row: number, col: number): Promise<MoveResponse> {
    const body: MoveRequest = {
      game_id: gameId,
      row,
      col,
    };

    return this.request<MoveResponse>("POST", "/api/game/move", body);
  }

  /**
   * Get current game status
   *
   * @param gameId - Game session ID
   * @returns Game status with state, agent status, and metrics
   */
  async getGameStatus(gameId: string): Promise<GameStatusResponse> {
    return this.request<GameStatusResponse>(
      "GET",
      `/api/game/status?game_id=${encodeURIComponent(gameId)}`
    );
  }

  /**
   * Reset a game to initial state
   *
   * @param gameId - Game session ID
   * @returns Reset response with new initial state
   */
  async resetGame(gameId: string): Promise<ResetGameResponse> {
    const body: ResetGameRequest = {
      game_id: gameId,
    };

    return this.request<ResetGameResponse>("POST", "/api/game/reset", body);
  }

  /**
   * Get move history for a game
   *
   * @param gameId - Game session ID
   * @returns Array of move history entries
   */
  async getGameHistory(gameId: string): Promise<MoveHistory[]> {
    return this.request<MoveHistory[]>(
      "GET",
      `/api/game/history?game_id=${encodeURIComponent(gameId)}`
    );
  }

  /**
   * Get status of a specific agent
   *
   * @param agentName - Agent name ('scout', 'strategist', or 'executor')
   * @returns Agent status
   */
  async getAgentStatus(agentName: string): Promise<AgentStatus> {
    return this.request<AgentStatus>(
      "GET",
      `/api/agents/${encodeURIComponent(agentName)}/status`
    );
  }

  /**
   * Check API health
   *
   * @returns Health status
   */
  async checkHealth(): Promise<{ status: string; uptime_seconds: number }> {
    return this.request<{ status: string; uptime_seconds: number }>(
      "GET",
      "/health"
    );
  }

  /**
   * Check API readiness
   *
   * @returns Readiness status with checks
   */
  async checkReady(): Promise<{ status: string; checks: Record<string, string> }> {
    return this.request<{ status: string; checks: Record<string, string> }>(
      "GET",
      "/ready"
    );
  }

  /**
   * Get post-game metrics
   *
   * @param gameId - Game session ID
   * @returns Post-game metrics including communications, LLM interactions, and performance
   */
  async getPostGameMetrics(gameId: string): Promise<PostGameMetrics> {
    return this.request<PostGameMetrics>(
      "GET",
      `/api/game/metrics?game_id=${encodeURIComponent(gameId)}`
    );
  }
}

// Default API client instance
export const apiClient = new ApiClient();
