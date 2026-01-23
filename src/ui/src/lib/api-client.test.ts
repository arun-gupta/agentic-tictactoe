import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  ApiClient,
  ApiError,
  NetworkError,
  type NewGameResponse,
  type MoveResponse,
  type GameStatusResponse,
  type ResetGameResponse,
  type GameState,
} from "./api-client";

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("ApiClient", () => {
  let client: ApiClient;

  const mockGameState: GameState = {
    board: [
      [null, null, null],
      [null, null, null],
      [null, null, null],
    ],
    current_player: "X",
    move_count: 0,
    is_game_over: false,
    winner: null,
    player_symbol: "X",
    ai_symbol: "O",
  };

  beforeEach(() => {
    client = new ApiClient({ baseUrl: "http://test-api.com" });
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("constructor", () => {
    it("uses default config when no config provided", () => {
      const defaultClient = new ApiClient();
      // We can't directly access private properties, but we can test behavior
      expect(defaultClient).toBeInstanceOf(ApiClient);
    });

    it("uses custom config when provided", () => {
      const customClient = new ApiClient({
        baseUrl: "http://custom.com",
        timeout: 5000,
      });
      expect(customClient).toBeInstanceOf(ApiClient);
    });
  });

  describe("createGame", () => {
    it("creates a new game without player symbol", async () => {
      const response: NewGameResponse = {
        game_id: "test-game-id",
        game_state: mockGameState,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(response),
      });

      const result = await client.createGame();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/game/new",
        expect.objectContaining({
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: undefined,
        })
      );
      expect(result).toEqual(response);
    });

    it("creates a new game with player symbol", async () => {
      const response: NewGameResponse = {
        game_id: "test-game-id",
        game_state: { ...mockGameState, player_symbol: "O", ai_symbol: "X" },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(response),
      });

      const result = await client.createGame("O");

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/game/new",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ player_symbol: "O" }),
        })
      );
      expect(result).toEqual(response);
    });
  });

  describe("makeMove", () => {
    it("makes a valid move", async () => {
      const response: MoveResponse = {
        success: true,
        position: { row: 0, col: 0 },
        updated_game_state: {
          ...mockGameState,
          board: [
            ["X", null, null],
            [null, null, null],
            [null, null, null],
          ],
          move_count: 1,
        },
        ai_move_execution: null,
        error_message: null,
        fallback_used: false,
        total_execution_time_ms: 100,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(response),
      });

      const result = await client.makeMove("game-123", 0, 0);

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/game/move",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ game_id: "game-123", row: 0, col: 0 }),
        })
      );
      expect(result).toEqual(response);
    });
  });

  describe("getGameStatus", () => {
    it("gets game status", async () => {
      const response: GameStatusResponse = {
        game_state: mockGameState,
        agent_status: null,
        metrics: null,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(response),
      });

      const result = await client.getGameStatus("game-123");

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/game/status?game_id=game-123",
        expect.objectContaining({
          method: "GET",
        })
      );
      expect(result).toEqual(response);
    });

    it("encodes game ID in URL", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ game_state: mockGameState }),
      });

      await client.getGameStatus("game with spaces");

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/game/status?game_id=game%20with%20spaces",
        expect.any(Object)
      );
    });
  });

  describe("resetGame", () => {
    it("resets a game", async () => {
      const response: ResetGameResponse = {
        game_id: "game-123",
        game_state: mockGameState,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(response),
      });

      const result = await client.resetGame("game-123");

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/game/reset",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ game_id: "game-123" }),
        })
      );
      expect(result).toEqual(response);
    });
  });

  describe("getGameHistory", () => {
    it("gets game history", async () => {
      const history = [
        {
          move_number: 1,
          player: "X" as const,
          position: { row: 0, col: 0 },
          timestamp: "2024-01-01T00:00:00Z",
          agent_reasoning: null,
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(history),
      });

      const result = await client.getGameHistory("game-123");

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/game/history?game_id=game-123",
        expect.any(Object)
      );
      expect(result).toEqual(history);
    });
  });

  describe("getAgentStatus", () => {
    it("gets agent status", async () => {
      const status = {
        status: "idle" as const,
        elapsed_time_ms: null,
        execution_time_ms: null,
        success: null,
        error_message: null,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(status),
      });

      const result = await client.getAgentStatus("scout");

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/agents/scout/status",
        expect.any(Object)
      );
      expect(result).toEqual(status);
    });
  });

  describe("checkHealth", () => {
    it("checks API health", async () => {
      const health = { status: "healthy", uptime_seconds: 100 };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(health),
      });

      const result = await client.checkHealth();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/health",
        expect.any(Object)
      );
      expect(result).toEqual(health);
    });
  });

  describe("checkReady", () => {
    it("checks API readiness", async () => {
      const ready = { status: "ready", checks: { database: "ok" } };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(ready),
      });

      const result = await client.checkReady();

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/ready",
        expect.any(Object)
      );
      expect(result).toEqual(ready);
    });
  });

  describe("getPostGameMetrics", () => {
    it("gets post-game metrics", async () => {
      const metrics = {
        game_id: "game-123",
        game_summary: {
          total_moves: 5,
          duration_ms: 10000,
          outcome: "X_WINS" as const,
          average_move_time_ms: 2000,
          start_time: "2024-01-01T00:00:00Z",
          end_time: "2024-01-01T00:00:10Z",
        },
        agent_communications: [],
        llm_interactions: [],
        agent_configs: [],
        agent_performances: [],
        total_llm_calls: 0,
        total_tokens_used: 0,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(metrics),
      });

      const result = await client.getPostGameMetrics("game-123");

      expect(mockFetch).toHaveBeenCalledWith(
        "http://test-api.com/api/game/metrics?game_id=game-123",
        expect.any(Object)
      );
      expect(result).toEqual(metrics);
    });
  });

  describe("error handling", () => {
    it("throws ApiError for 400 response", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () =>
          Promise.resolve({
            status: "failure",
            error_code: "E_INVALID_MOVE",
            message: "Invalid move",
            timestamp: "2024-01-01T00:00:00Z",
            details: null,
          }),
      });

      try {
        await client.createGame();
        expect.fail("Should have thrown ApiError");
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).message).toBe("Invalid move");
        expect((error as ApiError).errorCode).toBe("E_INVALID_MOVE");
        expect((error as ApiError).statusCode).toBe(400);
      }
    });

    it("throws ApiError for 404 response", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () =>
          Promise.resolve({
            status: "failure",
            error_code: "E_GAME_NOT_FOUND",
            message: "Game not found",
            timestamp: "2024-01-01T00:00:00Z",
            details: null,
          }),
      });

      await expect(client.getGameStatus("invalid-id")).rejects.toThrow(ApiError);
    });

    it("throws ApiError for 500 response", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () =>
          Promise.resolve({
            status: "failure",
            error_code: "E_SERVER_ERROR",
            message: "Internal server error",
            timestamp: "2024-01-01T00:00:00Z",
            details: null,
          }),
      });

      await expect(client.createGame()).rejects.toThrow(ApiError);
    });

    it("uses default error message when response has no message", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({}),
      });

      try {
        await client.createGame();
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).message).toBe(
          "Invalid request. Please check your input."
        );
      }
    });

    it("throws NetworkError on fetch failure", async () => {
      mockFetch.mockRejectedValueOnce(new Error("fetch failed"));

      await expect(client.createGame()).rejects.toThrow(NetworkError);
    });

    it("throws NetworkError on timeout", async () => {
      const abortError = new Error("Aborted");
      abortError.name = "AbortError";
      mockFetch.mockRejectedValueOnce(abortError);

      try {
        await client.createGame();
        expect.fail("Should have thrown NetworkError");
      } catch (error) {
        expect(error).toBeInstanceOf(NetworkError);
        expect((error as NetworkError).message).toBe(
          "Request timed out. Please try again."
        );
      }
    });
  });
});

describe("ApiError", () => {
  it("creates ApiError with all properties", () => {
    const error = new ApiError("Test message", "TEST_ERROR", 400, {
      field: "value",
    });

    expect(error.message).toBe("Test message");
    expect(error.errorCode).toBe("TEST_ERROR");
    expect(error.statusCode).toBe(400);
    expect(error.details).toEqual({ field: "value" });
    expect(error.name).toBe("ApiError");
  });

  it("creates ApiError without details", () => {
    const error = new ApiError("Test message", "TEST_ERROR", 400);

    expect(error.details).toBeNull();
  });
});

describe("NetworkError", () => {
  it("creates NetworkError with default message", () => {
    const error = new NetworkError();

    expect(error.message).toBe("Network error. Please check your connection.");
    expect(error.name).toBe("NetworkError");
  });

  it("creates NetworkError with custom message", () => {
    const error = new NetworkError("Custom network error");

    expect(error.message).toBe("Custom network error");
  });
});
