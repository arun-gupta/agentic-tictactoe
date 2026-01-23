import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { GameBoard } from "./GameBoard";
import { apiClient, type GameState, type MoveResponse, type NewGameResponse } from "@/lib/api-client";

// Mock the api-client
vi.mock("@/lib/api-client", async () => {
  const actual = await vi.importActual("@/lib/api-client");
  return {
    ...actual,
    apiClient: {
      createGame: vi.fn(),
      makeMove: vi.fn(),
      getGameHistory: vi.fn(),
      getAgentStatus: vi.fn(),
      getPostGameMetrics: vi.fn(),
    },
  };
});

describe("GameBoard", () => {
  const mockEmptyGameState: GameState = {
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

  const mockNewGameResponse: NewGameResponse = {
    game_id: "test-game-123",
    game_state: mockEmptyGameState,
  };

  const mockMoveResponse: MoveResponse = {
    success: true,
    position: { row: 0, col: 0 },
    updated_game_state: {
      ...mockEmptyGameState,
      board: [
        ["X", null, "O"],
        [null, null, null],
        [null, null, null],
      ],
      move_count: 2,
      current_player: "X",
    },
    ai_move_execution: {
      position: { row: 0, col: 2 },
      reasoning: "Center control",
      execution_time_ms: 100,
      success: true,
    },
    error_message: null,
    fallback_used: false,
    total_execution_time_ms: 150,
  };

  beforeEach(() => {
    vi.useFakeTimers();
    vi.mocked(apiClient.createGame).mockResolvedValue(mockNewGameResponse);
    vi.mocked(apiClient.makeMove).mockResolvedValue(mockMoveResponse);
    vi.mocked(apiClient.getGameHistory).mockResolvedValue([]);
    vi.mocked(apiClient.getAgentStatus).mockResolvedValue({
      status: "idle",
      elapsed_time_ms: null,
      execution_time_ms: null,
      success: null,
      error_message: null,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  describe("initial render", () => {
    it("displays initial status message", () => {
      render(<GameBoard />);
      expect(screen.getByText(/Status: Click 'New Game' to start/)).toBeInTheDocument();
    });

    it("displays New Game button", () => {
      render(<GameBoard />);
      expect(screen.getByText("New Game")).toBeInTheDocument();
    });

    it("displays all tabs", () => {
      render(<GameBoard />);
      expect(screen.getByText("Board")).toBeInTheDocument();
      expect(screen.getByText("History")).toBeInTheDocument();
      expect(screen.getByText("Insights")).toBeInTheDocument();
      expect(screen.getByText("Config")).toBeInTheDocument();
      expect(screen.getByText("Metrics")).toBeInTheDocument();
    });

    it("shows Board tab as active by default", () => {
      render(<GameBoard />);
      const boardTab = screen.getByText("Board");
      expect(boardTab.closest("button")).toHaveAttribute("data-state", "active");
    });

    it("renders 9 cells in the grid", () => {
      render(<GameBoard />);
      const cells = screen.getAllByRole("button").filter(btn =>
        btn.getAttribute("aria-label")?.startsWith("Cell")
      );
      expect(cells.length).toBe(9);
    });

    it("cells are disabled before game starts", () => {
      render(<GameBoard />);
      const cells = screen.getAllByRole("button").filter(btn =>
        btn.getAttribute("aria-label")?.startsWith("Cell")
      );
      cells.forEach(cell => {
        expect(cell).toBeDisabled();
      });
    });
  });

  describe("tab navigation", () => {
    it("switches to History tab when clicked", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("History"));

      // The History tab shows "No moves yet" when empty
      expect(screen.getByText("No moves yet")).toBeInTheDocument();
    });

    it("switches to Insights tab when clicked", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("Insights"));

      expect(screen.getByText("Agent Insights")).toBeInTheDocument();
    });

    it("switches to Config tab when clicked", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("Config"));

      expect(screen.getByText("Configuration")).toBeInTheDocument();
    });

    it("switches to Metrics tab when clicked", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("Metrics"));

      expect(screen.getByText(/Metrics will appear after game ends/)).toBeInTheDocument();
    });

    it("respects initialTab prop", () => {
      render(<GameBoard initialTab="history" />);
      // The History tab shows "No moves yet" when empty
      expect(screen.getByText("No moves yet")).toBeInTheDocument();
    });
  });

  describe("new game", () => {
    it("calls createGame when New Game button is clicked", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));

      expect(apiClient.createGame).toHaveBeenCalledWith("X");
    });

    it("updates status message after starting new game", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));

      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn \(X\)/)).toBeInTheDocument();
      });
    });

    it("enables cells after starting new game", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));

      await waitFor(() => {
        const cells = screen.getAllByRole("button").filter(btn =>
          btn.getAttribute("aria-label")?.startsWith("Cell")
        );
        const enabledCells = cells.filter(cell => !cell.hasAttribute("disabled"));
        expect(enabledCells.length).toBe(9);
      });
    });

    it("shows loading state while creating game", async () => {
      // Make createGame return a pending promise
      let resolvePromise: (value: NewGameResponse) => void;
      const pendingPromise = new Promise<NewGameResponse>((resolve) => {
        resolvePromise = resolve;
      });
      vi.mocked(apiClient.createGame).mockReturnValue(pendingPromise);

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));

      expect(screen.getByText("Loading...")).toBeInTheDocument();

      // Cleanup
      await act(async () => {
        resolvePromise!(mockNewGameResponse);
      });
    });

    it("displays error when createGame fails", async () => {
      vi.mocked(apiClient.createGame).mockRejectedValue(new Error("Network error"));

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));

      await waitFor(() => {
        expect(screen.getByText("Failed to start new game")).toBeInTheDocument();
      });
    });
  });

  describe("making moves", () => {
    it("calls makeMove when a cell is clicked", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      // Start a new game first
      await user.click(screen.getByText("New Game"));

      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      // Click on cell (0,0)
      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      expect(apiClient.makeMove).toHaveBeenCalledWith("test-game-123", 0, 0);
    });

    it("shows AI thinking message during move", async () => {
      // Make makeMove return a pending promise
      let resolvePromise: (value: MoveResponse) => void;
      const pendingPromise = new Promise<MoveResponse>((resolve) => {
        resolvePromise = resolve;
      });
      vi.mocked(apiClient.makeMove).mockReturnValue(pendingPromise);

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      expect(screen.getByText("AI is thinking...")).toBeInTheDocument();

      // Cleanup
      await act(async () => {
        resolvePromise!(mockMoveResponse);
      });
    });

    it("fetches game history after successful move", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(apiClient.getGameHistory).toHaveBeenCalledWith("test-game-123");
      });
    });

    it("displays move count after moves", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(screen.getByText(/Move: 2/)).toBeInTheDocument();
      });
    });
  });

  describe("error handling", () => {
    it("occupied cells are disabled and cannot be clicked", async () => {
      // Setup game with an occupied cell
      vi.mocked(apiClient.createGame).mockResolvedValue({
        game_id: "test-game-123",
        game_state: {
          ...mockEmptyGameState,
          board: [
            ["X", null, null],
            [null, null, null],
            [null, null, null],
          ],
          move_count: 1,
        },
      });

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      // The occupied cell should be disabled
      const cell = screen.getByLabelText("Cell 0,0: X");
      expect(cell).toBeDisabled();
    });

    it("shows error when move API fails", async () => {
      vi.mocked(apiClient.makeMove).mockRejectedValue(new Error("API Error"));

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(screen.getByText("Failed to make move")).toBeInTheDocument();
      });
    });

    it("shows error when move response has error_message", async () => {
      vi.mocked(apiClient.makeMove).mockResolvedValue({
        ...mockMoveResponse,
        success: false,
        error_message: "Invalid move position",
      });

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(screen.getByText("Invalid move position")).toBeInTheDocument();
      });
    });
  });

  describe("game over states", () => {
    it("displays 'You win!' when player wins", async () => {
      vi.mocked(apiClient.makeMove).mockResolvedValue({
        ...mockMoveResponse,
        updated_game_state: {
          ...mockEmptyGameState,
          is_game_over: true,
          winner: "X",
        },
      });

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(screen.getByText(/Status: You win!/)).toBeInTheDocument();
      });
    });

    it("displays 'AI wins!' when AI wins", async () => {
      vi.mocked(apiClient.makeMove).mockResolvedValue({
        ...mockMoveResponse,
        updated_game_state: {
          ...mockEmptyGameState,
          is_game_over: true,
          winner: "O",
        },
      });

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(screen.getByText(/Status: AI wins!/)).toBeInTheDocument();
      });
    });

    it("displays 'It's a draw!' on draw", async () => {
      vi.mocked(apiClient.makeMove).mockResolvedValue({
        ...mockMoveResponse,
        updated_game_state: {
          ...mockEmptyGameState,
          is_game_over: true,
          winner: null,
        },
      });

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(screen.getByText(/Status: It's a draw!/)).toBeInTheDocument();
      });
    });

    it("disables cells when game is over", async () => {
      vi.mocked(apiClient.makeMove).mockResolvedValue({
        ...mockMoveResponse,
        updated_game_state: {
          ...mockEmptyGameState,
          is_game_over: true,
          winner: "X",
        },
      });

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(screen.getByText(/Status: You win!/)).toBeInTheDocument();
      });

      // All cells should be disabled
      const cells = screen.getAllByRole("button").filter(btn =>
        btn.getAttribute("aria-label")?.startsWith("Cell")
      );
      cells.forEach(cell => {
        expect(cell).toBeDisabled();
      });
    });
  });

  describe("fallback notification", () => {
    it("displays fallback notification when fallback is used", async () => {
      vi.mocked(apiClient.makeMove).mockResolvedValue({
        ...mockMoveResponse,
        fallback_used: true,
        ai_move_execution: {
          position: { row: 0, col: 2 },
          reasoning: "AI timeout - using fallback",
          execution_time_ms: 100,
          success: true,
        },
      });

      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));
      await waitFor(() => {
        expect(screen.getByText(/Status: Your turn/)).toBeInTheDocument();
      });

      const cell = screen.getByLabelText("Cell 0,0: empty");
      await user.click(cell);

      await waitFor(() => {
        expect(screen.getByText("Fallback Used")).toBeInTheDocument();
      });
    });
  });

  describe("move count", () => {
    it("does not display move count before game starts", () => {
      render(<GameBoard />);
      expect(screen.queryByText(/Move:/)).not.toBeInTheDocument();
    });

    it("displays move count after game starts", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      render(<GameBoard />);

      await user.click(screen.getByText("New Game"));

      await waitFor(() => {
        expect(screen.getByText(/Move: 0/)).toBeInTheDocument();
      });
    });
  });
});
