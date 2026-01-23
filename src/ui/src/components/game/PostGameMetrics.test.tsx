import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PostGameMetrics } from "./PostGameMetrics";
import { apiClient, type PostGameMetrics as PostGameMetricsType } from "@/lib/api-client";

// Mock the api-client
vi.mock("@/lib/api-client", () => ({
  apiClient: {
    getPostGameMetrics: vi.fn(),
  },
}));

describe("PostGameMetrics", () => {
  const mockMetrics: PostGameMetricsType = {
    game_id: "test-game-123",
    game_summary: {
      total_moves: 7,
      duration_ms: 25000,
      outcome: "X_WINS",
      average_move_time_ms: 3571,
      start_time: "2024-01-01T12:00:00Z",
      end_time: "2024-01-01T12:00:25Z",
    },
    agent_communications: [
      {
        agent_name: "Scout",
        request: { board: [["X", null, null], [null, "O", null], [null, null, null]], player: "O" },
        response: { threats: [], opportunities: [{ position: { row: 0, col: 2 }, confidence: 0.8 }] },
        timestamp: "2024-01-01T12:00:05Z",
        execution_time_ms: 125,
      },
      {
        agent_name: "Strategist",
        request: { analysis: { threats: [], opportunities: [] } },
        response: { primary_move: { row: 0, col: 2 }, priority: 80, reasoning: "Block potential fork" },
        timestamp: "2024-01-01T12:00:06Z",
        execution_time_ms: 200,
      },
    ],
    llm_interactions: [
      {
        agent_name: "Scout",
        provider: "anthropic",
        model: "claude-3-haiku",
        prompt: "Analyze the board",
        response: "Found opportunity at position (0, 2)",
        input_tokens: 100,
        output_tokens: 50,
        total_tokens: 150,
        latency_ms: 500,
        timestamp: "2024-01-01T12:00:01Z",
      },
    ],
    agent_configs: [
      { agent_name: "Scout", mode: "local", llm_framework: "Pydantic AI", provider: null, model: null, timeout_ms: 5000 },
      { agent_name: "Strategist", mode: "mcp", llm_framework: "Pydantic AI", provider: "anthropic", model: "claude-3-haiku", timeout_ms: 10000 },
    ],
    agent_performances: [
      { agent_name: "Scout", min_execution_ms: 100, max_execution_ms: 150, avg_execution_ms: 125, total_calls: 3, successful_calls: 3, failed_calls: 0, success_rate: 1.0 },
      { agent_name: "Strategist", min_execution_ms: 180, max_execution_ms: 220, avg_execution_ms: 200, total_calls: 3, successful_calls: 2, failed_calls: 1, success_rate: 0.67 },
    ],
    total_llm_calls: 5,
    total_tokens_used: 1500,
  };

  beforeEach(() => {
    vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue(mockMetrics);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe("game not over state", () => {
    it("displays placeholder message when game is not over", () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={false} />);
      expect(screen.getByText("Metrics will appear after game ends")).toBeInTheDocument();
    });

    it("does not fetch metrics when game is not over", () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={false} />);
      expect(apiClient.getPostGameMetrics).not.toHaveBeenCalled();
    });
  });

  describe("loading state", () => {
    it("displays loading message while fetching metrics", async () => {
      // Create a promise that we can control
      let resolvePromise: (value: PostGameMetricsType) => void;
      const pendingPromise = new Promise<PostGameMetricsType>((resolve) => {
        resolvePromise = resolve;
      });
      vi.mocked(apiClient.getPostGameMetrics).mockReturnValue(pendingPromise);

      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      expect(screen.getByText("Loading metrics...")).toBeInTheDocument();

      // Clean up by resolving
      await act(async () => {
        resolvePromise!(mockMetrics);
      });
    });
  });

  describe("header", () => {
    it("displays Post-Game Metrics title", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Post-Game Metrics")).toBeInTheDocument();
      });
    });

    it("displays description", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Game analysis and performance data")).toBeInTheDocument();
      });
    });
  });

  describe("tabs", () => {
    it("displays all tab options", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Summary")).toBeInTheDocument();
        expect(screen.getByText("Performance")).toBeInTheDocument();
        expect(screen.getByText("LLM")).toBeInTheDocument();
        expect(screen.getByText("Comms")).toBeInTheDocument();
      });
    });

    it("shows Summary tab by default", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Game Outcome")).toBeInTheDocument();
      });
    });

    it("switches to Performance tab when clicked", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Performance")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Performance"));

      expect(screen.getByText("Total LLM Calls")).toBeInTheDocument();
      expect(screen.getByText("Per-Agent Performance")).toBeInTheDocument();
    });

    it("switches to LLM tab when clicked", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("LLM")).toBeInTheDocument();
      });

      await user.click(screen.getByText("LLM"));

      // Should show LLM interaction with agent name
      expect(screen.getByText("Scout")).toBeInTheDocument();
    });

    it("switches to Communication tab when clicked", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Comms")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Comms"));

      // Should show agent communications
      expect(screen.getByText("125ms")).toBeInTheDocument(); // Scout's execution time
    });
  });

  describe("GameSummaryTab", () => {
    it("displays game outcome as 'X Wins' for X_WINS", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("X Wins")).toBeInTheDocument();
      });
    });

    it("displays game outcome as 'O Wins' for O_WINS", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        game_summary: { ...mockMetrics.game_summary, outcome: "O_WINS" },
      });

      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("O Wins")).toBeInTheDocument();
      });
    });

    it("displays game outcome as 'Draw' for DRAW", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        game_summary: { ...mockMetrics.game_summary, outcome: "DRAW" },
      });

      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Draw")).toBeInTheDocument();
      });
    });

    it("displays total moves", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Total Moves")).toBeInTheDocument();
        expect(screen.getByText("7")).toBeInTheDocument();
      });
    });

    it("displays duration formatted in seconds", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Duration")).toBeInTheDocument();
        expect(screen.getByText("25s")).toBeInTheDocument();
      });
    });

    it("displays duration formatted in minutes for longer games", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        game_summary: { ...mockMetrics.game_summary, duration_ms: 125000 }, // 2m 5s
      });

      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("2m 5s")).toBeInTheDocument();
      });
    });

    it("displays average move time", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Avg Move Time")).toBeInTheDocument();
        expect(screen.getByText("3571ms")).toBeInTheDocument();
      });
    });

    it("displays 'No game summary available' when summary is null", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        game_summary: null as unknown as typeof mockMetrics.game_summary,
      });

      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("No game summary available")).toBeInTheDocument();
      });
    });
  });

  describe("PerformanceTab", () => {
    it("displays total LLM calls", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Performance")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Performance"));

      expect(screen.getByText("Total LLM Calls")).toBeInTheDocument();
      expect(screen.getByText("5")).toBeInTheDocument();
    });

    it("displays total tokens", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Performance")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Performance"));

      expect(screen.getByText("Total Tokens")).toBeInTheDocument();
      expect(screen.getByText("1,500")).toBeInTheDocument();
    });

    it("displays per-agent performance data", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Performance")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Performance"));

      // Should show agent names
      expect(screen.getByText("Scout")).toBeInTheDocument();
      expect(screen.getByText("Strategist")).toBeInTheDocument();

      // Should show success rates
      expect(screen.getByText("100% success")).toBeInTheDocument();
      expect(screen.getByText("67% success")).toBeInTheDocument();
    });

    it("displays execution time stats", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Performance")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Performance"));

      // Should show min/max/avg for Scout
      expect(screen.getByText("100ms")).toBeInTheDocument(); // min
      expect(screen.getByText("150ms")).toBeInTheDocument(); // max
      expect(screen.getByText("125ms")).toBeInTheDocument(); // avg
    });

    it("displays call counts", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Performance")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Performance"));

      expect(screen.getByText("3/3 calls successful")).toBeInTheDocument(); // Scout
      expect(screen.getByText("2/3 calls successful")).toBeInTheDocument(); // Strategist
    });

    it("displays 'No performance data available' when empty", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        agent_performances: [],
      });

      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Performance")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Performance"));

      expect(screen.getByText("No performance data available")).toBeInTheDocument();
    });
  });

  describe("LLMTab", () => {
    it("displays LLM interaction cards", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("LLM")).toBeInTheDocument();
      });

      await user.click(screen.getByText("LLM"));

      expect(screen.getByText("Scout")).toBeInTheDocument();
      expect(screen.getByText("anthropic/claude-3-haiku")).toBeInTheDocument();
      expect(screen.getByText("150 tokens")).toBeInTheDocument();
      expect(screen.getByText("500ms")).toBeInTheDocument();
    });

    it("expands LLM interaction to show details", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("LLM")).toBeInTheDocument();
      });

      await user.click(screen.getByText("LLM"));

      // Click to expand
      const expandButton = screen.getByRole("button", { name: /Scout/i });
      await user.click(expandButton);

      // Should show expanded content
      expect(screen.getByText("Prompt")).toBeInTheDocument();
      expect(screen.getByText("Response")).toBeInTheDocument();
      expect(screen.getByText("Analyze the board")).toBeInTheDocument();
      expect(screen.getByText("Found opportunity at position (0, 2)")).toBeInTheDocument();
    });

    it("shows token breakdown when expanded", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("LLM")).toBeInTheDocument();
      });

      await user.click(screen.getByText("LLM"));

      const expandButton = screen.getByRole("button", { name: /Scout/i });
      await user.click(expandButton);

      expect(screen.getByText("Input: 100")).toBeInTheDocument();
      expect(screen.getByText("Output: 50")).toBeInTheDocument();
    });

    it("displays 'No LLM interactions' message and shows config when empty", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        llm_interactions: [],
      });

      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("LLM")).toBeInTheDocument();
      });

      await user.click(screen.getByText("LLM"));

      expect(screen.getByText("No LLM interactions (rule-based mode)")).toBeInTheDocument();
    });
  });

  describe("CommunicationTab", () => {
    it("displays agent communication cards", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Comms")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Comms"));

      // Should show both communications
      const scoutElements = screen.getAllByText("Scout");
      const strategistElements = screen.getAllByText("Strategist");
      expect(scoutElements.length).toBeGreaterThan(0);
      expect(strategistElements.length).toBeGreaterThan(0);
    });

    it("expands communication to show request/response JSON", async () => {
      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Comms")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Comms"));

      // Find and click the first communication item
      const buttons = screen.getAllByRole("button");
      const scoutButton = buttons.find(btn => btn.textContent?.includes("125ms"));
      await user.click(scoutButton!);

      // Should show Request and Response headers
      expect(screen.getByText("Request")).toBeInTheDocument();
      expect(screen.getByText("Response")).toBeInTheDocument();
    });

    it("displays 'No agent communications recorded' when empty", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        agent_communications: [],
      });

      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("Comms")).toBeInTheDocument();
      });

      await user.click(screen.getByText("Comms"));

      expect(screen.getByText("No agent communications recorded")).toBeInTheDocument();
    });
  });

  describe("ConfigTab (shown in LLM tab when no LLM interactions)", () => {
    it("displays agent configuration when shown", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        llm_interactions: [],
      });

      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("LLM")).toBeInTheDocument();
      });

      await user.click(screen.getByText("LLM"));

      // Should show config info
      expect(screen.getByText("Local")).toBeInTheDocument(); // Scout's mode
      expect(screen.getByText("MCP")).toBeInTheDocument(); // Strategist's mode
    });

    it("displays framework information", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        llm_interactions: [],
      });

      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("LLM")).toBeInTheDocument();
      });

      await user.click(screen.getByText("LLM"));

      expect(screen.getAllByText("Pydantic AI").length).toBe(2);
    });

    it("displays timeout information", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockResolvedValue({
        ...mockMetrics,
        llm_interactions: [],
      });

      const user = userEvent.setup();
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText("LLM")).toBeInTheDocument();
      });

      await user.click(screen.getByText("LLM"));

      expect(screen.getByText("5000ms")).toBeInTheDocument();
      expect(screen.getByText("10000ms")).toBeInTheDocument();
    });
  });

  describe("error handling", () => {
    it("shows error notice when API fails but displays fallback data", async () => {
      vi.mocked(apiClient.getPostGameMetrics).mockRejectedValue(new Error("API Error"));

      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(screen.getByText(/Note: Using demo data/)).toBeInTheDocument();
      });

      // Should still show summary tab with fallback data
      expect(screen.getByText("Game Outcome")).toBeInTheDocument();
    });
  });

  describe("API calls", () => {
    it("fetches metrics when game ends", async () => {
      render(<PostGameMetrics gameId="game-123" isGameOver={true} />);

      await waitFor(() => {
        expect(apiClient.getPostGameMetrics).toHaveBeenCalledWith("game-123");
      });
    });

    it("does not fetch metrics when gameId is null", () => {
      render(<PostGameMetrics gameId={null} isGameOver={true} />);
      expect(apiClient.getPostGameMetrics).not.toHaveBeenCalled();
    });
  });
});
