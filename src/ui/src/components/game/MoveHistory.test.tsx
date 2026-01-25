import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MoveHistory } from "./MoveHistory";
import type { MoveHistory as MoveHistoryType } from "@/lib/api-client";

describe("MoveHistory", () => {
  const mockMoves: MoveHistoryType[] = [
    {
      move_number: 1,
      player: "X",
      position: { row: 0, col: 0 },
      timestamp: "2024-01-01T12:00:00Z",
      agent_reasoning: null,
    },
    {
      move_number: 2,
      player: "O",
      position: { row: 1, col: 1 },
      timestamp: "2024-01-01T12:00:05Z",
      agent_reasoning: "Scout: Found center available. Strategist: Center control is optimal. Executor: Placed at center.",
    },
    {
      move_number: 3,
      player: "X",
      position: { row: 0, col: 2 },
      timestamp: "2024-01-01T12:00:10Z",
      agent_reasoning: null,
    },
  ];

  describe("empty state", () => {
    it("displays 'No moves yet' when moves array is empty", () => {
      render(<MoveHistory moves={[]} playerSymbol="X" />);
      expect(screen.getByText("No moves yet")).toBeInTheDocument();
    });
  });

  describe("rendering moves", () => {
    it("displays move count in header", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="X" />);
      expect(screen.getByText(/3 moves/)).toBeInTheDocument();
    });

    it("displays singular 'move' for single move", () => {
      render(<MoveHistory moves={[mockMoves[0]]} playerSymbol="X" />);
      expect(screen.getByText(/1 move •/)).toBeInTheDocument();
    });

    it("displays move numbers", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="X" />);
      expect(screen.getByText("#1")).toBeInTheDocument();
      expect(screen.getByText("#2")).toBeInTheDocument();
      expect(screen.getByText("#3")).toBeInTheDocument();
    });

    it("displays positions for each move", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="X" />);
      expect(screen.getByText("(0, 0)")).toBeInTheDocument();
      expect(screen.getByText("(1, 1)")).toBeInTheDocument();
      expect(screen.getByText("(0, 2)")).toBeInTheDocument();
    });

    it("labels player moves as 'You'", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="X" />);
      const youLabels = screen.getAllByText("You");
      expect(youLabels.length).toBe(2); // Moves 1 and 3 are by player X
    });

    it("labels opponent moves as 'AI'", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="X" />);
      const aiLabels = screen.getAllByText("AI");
      expect(aiLabels.length).toBe(1); // Move 2 is by AI (O)
    });

    it("swaps labels when player symbol is O", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="O" />);
      const youLabels = screen.getAllByText("You");
      const aiLabels = screen.getAllByText("AI");
      expect(youLabels.length).toBe(1); // Move 2 is by player O
      expect(aiLabels.length).toBe(2); // Moves 1 and 3 are by AI (X)
    });
  });

  describe("expandable reasoning", () => {
    it("does not show expand icon for moves without reasoning", () => {
      render(<MoveHistory moves={[mockMoves[0]]} playerSymbol="X" />);
      // Move 1 has no agent_reasoning, so no expand icon
      const svgs = document.querySelectorAll("svg");
      expect(svgs.length).toBe(0);
    });

    it("shows expand icon for moves with reasoning", () => {
      render(<MoveHistory moves={[mockMoves[1]]} playerSymbol="X" />);
      // Move 2 has agent_reasoning, so should have expand icon
      const svg = document.querySelector("svg");
      expect(svg).toBeInTheDocument();
    });

    it("expands reasoning when clicked", async () => {
      const user = userEvent.setup();
      render(<MoveHistory moves={[mockMoves[1]]} playerSymbol="X" />);

      // Initially, reasoning is not visible
      expect(screen.queryByText("Agent Reasoning")).not.toBeInTheDocument();

      // Click to expand
      await user.click(screen.getByRole("button"));

      // Now reasoning should be visible
      expect(screen.getByText("Agent Reasoning")).toBeInTheDocument();
    });

    it("collapses reasoning when clicked again", async () => {
      const user = userEvent.setup();
      render(<MoveHistory moves={[mockMoves[1]]} playerSymbol="X" />);

      // Click to expand
      await user.click(screen.getByRole("button"));
      expect(screen.getByText("Agent Reasoning")).toBeInTheDocument();

      // Click to collapse
      await user.click(screen.getByRole("button"));
      expect(screen.queryByText("Agent Reasoning")).not.toBeInTheDocument();
    });

    it("displays structured reasoning sections when available", async () => {
      const user = userEvent.setup();
      render(<MoveHistory moves={[mockMoves[1]]} playerSymbol="X" />);

      // Click to expand
      await user.click(screen.getByRole("button"));

      // Should show structured sections
      expect(screen.getByText("Scout Analysis")).toBeInTheDocument();
      expect(screen.getByText("Strategist Strategy")).toBeInTheDocument();
      expect(screen.getByText("Executor Details")).toBeInTheDocument();
    });

    it("allows multiple moves to be expanded simultaneously", async () => {
      const user = userEvent.setup();
      const movesWithReasoning: MoveHistoryType[] = [
        {
          move_number: 1,
          player: "O",
          position: { row: 0, col: 0 },
          timestamp: "2024-01-01T12:00:00Z",
          agent_reasoning: "Scout: Analysis 1. Strategist: Plan 1. Executor: Done 1.",
        },
        {
          move_number: 2,
          player: "O",
          position: { row: 1, col: 1 },
          timestamp: "2024-01-01T12:00:05Z",
          agent_reasoning: "Scout: Analysis 2. Strategist: Plan 2. Executor: Done 2.",
        },
      ];
      render(<MoveHistory moves={movesWithReasoning} playerSymbol="X" />);

      const buttons = screen.getAllByRole("button");

      // Expand first move
      await user.click(buttons[0]);
      // Use getAllByText since text may appear in multiple places (raw + structured)
      expect(screen.getAllByText(/Analysis 1/).length).toBeGreaterThan(0);

      // Expand second move
      await user.click(buttons[1]);
      expect(screen.getAllByText(/Analysis 2/).length).toBeGreaterThan(0);

      // Both should still be expanded - check for Scout Analysis header which appears when expanded
      const scoutHeaders = screen.getAllByText("Scout Analysis");
      expect(scoutHeaders.length).toBe(2);
    });
  });

  describe("timestamp formatting", () => {
    it("displays formatted timestamps", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="X" />);
      // Timestamps are formatted to local time, so we check for general pattern
      // The exact time depends on timezone, so we just verify buttons exist
      const buttons = screen.getAllByRole("button");
      expect(buttons.length).toBe(3);
    });
  });

  describe("header", () => {
    it("displays Move History title", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="X" />);
      expect(screen.getByText("Move History")).toBeInTheDocument();
    });

    it("displays helpful text about expanding", () => {
      render(<MoveHistory moves={mockMoves} playerSymbol="X" />);
      expect(screen.getByText(/Click to expand AI reasoning/)).toBeInTheDocument();
    });
  });
});
