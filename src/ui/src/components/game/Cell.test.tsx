import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Cell } from "./Cell";

describe("Cell", () => {
  const defaultProps = {
    value: null as "X" | "O" | null,
    row: 0,
    col: 0,
    isLastMove: false,
    isDisabled: false,
    isGameOver: false,
    onClick: vi.fn(),
  };

  describe("rendering", () => {
    it("renders empty cell with no content", () => {
      render(<Cell {...defaultProps} value={null} />);
      const button = screen.getByRole("button");
      expect(button).toHaveTextContent("");
    });

    it("renders X value as lowercase x", () => {
      render(<Cell {...defaultProps} value="X" />);
      const button = screen.getByRole("button");
      expect(button).toHaveTextContent("x");
    });

    it("renders O value as lowercase o", () => {
      render(<Cell {...defaultProps} value="O" />);
      const button = screen.getByRole("button");
      expect(button).toHaveTextContent("o");
    });
  });

  describe("click handling", () => {
    it("calls onClick with row and col when empty cell is clicked", async () => {
      const onClick = vi.fn();
      const user = userEvent.setup();
      render(<Cell {...defaultProps} row={1} col={2} onClick={onClick} />);

      await user.click(screen.getByRole("button"));

      expect(onClick).toHaveBeenCalledTimes(1);
      expect(onClick).toHaveBeenCalledWith(1, 2);
    });

    it("does not call onClick when cell has value", async () => {
      const onClick = vi.fn();
      const user = userEvent.setup();
      render(<Cell {...defaultProps} value="X" onClick={onClick} />);

      await user.click(screen.getByRole("button"));

      expect(onClick).not.toHaveBeenCalled();
    });

    it("does not call onClick when disabled", async () => {
      const onClick = vi.fn();
      const user = userEvent.setup();
      render(<Cell {...defaultProps} isDisabled={true} onClick={onClick} />);

      await user.click(screen.getByRole("button"));

      expect(onClick).not.toHaveBeenCalled();
    });

    it("does not call onClick when game is over", async () => {
      const onClick = vi.fn();
      const user = userEvent.setup();
      render(<Cell {...defaultProps} isGameOver={true} onClick={onClick} />);

      await user.click(screen.getByRole("button"));

      expect(onClick).not.toHaveBeenCalled();
    });
  });

  describe("disabled state", () => {
    it("is enabled when empty and not disabled", () => {
      render(<Cell {...defaultProps} value={null} isDisabled={false} />);
      expect(screen.getByRole("button")).not.toBeDisabled();
    });

    it("is disabled when cell has value", () => {
      render(<Cell {...defaultProps} value="X" />);
      expect(screen.getByRole("button")).toBeDisabled();
    });

    it("is disabled when isDisabled is true", () => {
      render(<Cell {...defaultProps} isDisabled={true} />);
      expect(screen.getByRole("button")).toBeDisabled();
    });

    it("is disabled when game is over", () => {
      render(<Cell {...defaultProps} isGameOver={true} />);
      expect(screen.getByRole("button")).toBeDisabled();
    });
  });

  describe("visual states", () => {
    it("applies last move styles when isLastMove is true", () => {
      render(<Cell {...defaultProps} isLastMove={true} />);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("border-pink-500");
    });

    it("applies game over opacity when isGameOver is true", () => {
      render(<Cell {...defaultProps} isGameOver={true} />);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("opacity-60");
    });

    it("applies error styles when hasError is true", () => {
      render(<Cell {...defaultProps} hasError={true} />);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("border-red-500");
      expect(button).toHaveClass("bg-red-50");
    });

    it("applies shake animation when isShaking is true", () => {
      render(<Cell {...defaultProps} isShaking={true} />);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("animate-shake");
    });

    it("applies X color style", () => {
      render(<Cell {...defaultProps} value="X" />);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("text-zinc-900");
    });

    it("applies O color style", () => {
      render(<Cell {...defaultProps} value="O" />);
      const button = screen.getByRole("button");
      expect(button).toHaveClass("text-zinc-600");
    });
  });

  describe("corner rounding", () => {
    it("applies top-left rounding for cell (0,0)", () => {
      render(<Cell {...defaultProps} row={0} col={0} />);
      expect(screen.getByRole("button")).toHaveClass("rounded-tl-lg");
    });

    it("applies top-right rounding for cell (0,2)", () => {
      render(<Cell {...defaultProps} row={0} col={2} />);
      expect(screen.getByRole("button")).toHaveClass("rounded-tr-lg");
    });

    it("applies bottom-left rounding for cell (2,0)", () => {
      render(<Cell {...defaultProps} row={2} col={0} />);
      expect(screen.getByRole("button")).toHaveClass("rounded-bl-lg");
    });

    it("applies bottom-right rounding for cell (2,2)", () => {
      render(<Cell {...defaultProps} row={2} col={2} />);
      expect(screen.getByRole("button")).toHaveClass("rounded-br-lg");
    });

    it("does not apply corner rounding for center cell (1,1)", () => {
      render(<Cell {...defaultProps} row={1} col={1} />);
      const button = screen.getByRole("button");
      expect(button).not.toHaveClass("rounded-tl-lg");
      expect(button).not.toHaveClass("rounded-tr-lg");
      expect(button).not.toHaveClass("rounded-bl-lg");
      expect(button).not.toHaveClass("rounded-br-lg");
    });
  });

  describe("accessibility", () => {
    it("has correct aria-label for empty cell", () => {
      render(<Cell {...defaultProps} row={1} col={2} value={null} />);
      expect(screen.getByRole("button")).toHaveAttribute(
        "aria-label",
        "Cell 1,2: empty"
      );
    });

    it("has correct aria-label for X cell", () => {
      render(<Cell {...defaultProps} row={0} col={1} value="X" />);
      expect(screen.getByRole("button")).toHaveAttribute(
        "aria-label",
        "Cell 0,1: X"
      );
    });

    it("has correct aria-label for O cell", () => {
      render(<Cell {...defaultProps} row={2} col={0} value="O" />);
      expect(screen.getByRole("button")).toHaveAttribute(
        "aria-label",
        "Cell 2,0: O"
      );
    });
  });
});
