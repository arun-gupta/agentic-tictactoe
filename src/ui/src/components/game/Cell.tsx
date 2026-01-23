"use client";

import { cn } from "@/lib/utils";
import type { CellValue } from "@/lib/api-client";

interface CellProps {
  value: CellValue;
  row: number;
  col: number;
  isLastMove: boolean;
  isDisabled: boolean;
  isGameOver: boolean;
  hasError?: boolean;
  isShaking?: boolean;
  onClick: (row: number, col: number) => void;
}

/**
 * Get rounded corner classes based on cell position in grid
 */
function getRoundedCorners(row: number, col: number): string {
  if (row === 0 && col === 0) return "rounded-tl-lg";
  if (row === 0 && col === 2) return "rounded-tr-lg";
  if (row === 2 && col === 0) return "rounded-bl-lg";
  if (row === 2 && col === 2) return "rounded-br-lg";
  return "";
}

export function Cell({
  value,
  row,
  col,
  isLastMove,
  isDisabled,
  isGameOver,
  hasError = false,
  isShaking = false,
  onClick,
}: CellProps) {
  const isEmpty = value === null;
  const canClick = isEmpty && !isDisabled && !isGameOver;

  return (
    <button
      type="button"
      onClick={() => canClick && onClick(row, col)}
      disabled={!canClick}
      className={cn(
        "flex items-center justify-center",
        "size-[100px] border border-zinc-700",
        "font-mono text-4xl font-semibold",
        "transition-all duration-150",
        getRoundedCorners(row, col),
        // Empty cell styles
        isEmpty && canClick && "cursor-pointer hover:bg-zinc-200",
        isEmpty && !canClick && "cursor-default",
        // Occupied cell styles
        !isEmpty && "cursor-default",
        // Value colors - lowercase per Figma
        value === "X" && "text-zinc-900",
        value === "O" && "text-zinc-600",
        // Last move highlight
        isLastMove && "border-2 border-pink-500 shadow-[0_0_8px_rgba(247,37,133,0.5)]",
        // Game over fade
        isGameOver && "opacity-60",
        // Error state - red highlight
        hasError && "border-2 border-red-500 bg-red-50",
        // Shake animation
        isShaking && "animate-shake"
      )}
      aria-label={`Cell ${row},${col}${value ? `: ${value}` : ": empty"}`}
    >
      {/* Display lowercase x/o per Figma design */}
      {value?.toLowerCase()}
    </button>
  );
}
