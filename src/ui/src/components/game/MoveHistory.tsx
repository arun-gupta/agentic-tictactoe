"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import type { MoveHistory as MoveHistoryType, PlayerSymbol } from "@/lib/api-client";

interface MoveHistoryProps {
  moves: MoveHistoryType[];
  playerSymbol: PlayerSymbol;
}

interface MoveEntryProps {
  move: MoveHistoryType;
  isPlayer: boolean;
  isExpanded: boolean;
  onToggle: () => void;
}

function MoveEntry({ move, isPlayer, isExpanded, onToggle }: MoveEntryProps) {
  const formattedTime = new Date(move.timestamp).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return (
    <div
      className={cn(
        "border-b border-zinc-200 last:border-b-0",
        "transition-all duration-200"
      )}
    >
      {/* Move Header - Always visible */}
      <button
        type="button"
        onClick={onToggle}
        className={cn(
          "w-full px-3 py-2 text-left",
          "flex items-center justify-between gap-2",
          "hover:bg-zinc-100 transition-colors",
          "cursor-pointer"
        )}
      >
        <div className="flex items-center gap-3">
          {/* Move Number */}
          <span className="text-xs text-zinc-400 font-mono w-6">
            #{move.move_number}
          </span>

          {/* Player Indicator */}
          <span
            className={cn(
              "text-xs font-medium px-2 py-0.5 rounded",
              isPlayer
                ? "bg-zinc-800 text-zinc-100"
                : "bg-zinc-200 text-zinc-700"
            )}
          >
            {isPlayer ? "You" : "AI"}
          </span>

          {/* Position */}
          <span className="text-sm text-zinc-700 font-mono">
            ({move.position.row}, {move.position.col})
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* Timestamp */}
          <span className="text-xs text-zinc-400 font-mono">{formattedTime}</span>

          {/* Expand/Collapse Indicator */}
          {move.agent_reasoning && (
            <svg
              className={cn(
                "w-4 h-4 text-zinc-400 transition-transform duration-200",
                isExpanded && "rotate-180"
              )}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          )}
        </div>
      </button>

      {/* Expanded Details */}
      {isExpanded && move.agent_reasoning && (
        <div
          className={cn(
            "px-3 pb-3 pt-1",
            "bg-zinc-50 border-t border-zinc-100",
            "animate-in slide-in-from-top-2 duration-200"
          )}
        >
          <div className="space-y-2">
            {/* Agent Reasoning */}
            <div>
              <p className="text-xs font-medium text-zinc-500 mb-1">
                Agent Reasoning
              </p>
              <p className="text-sm text-zinc-700 font-mono leading-relaxed">
                {move.agent_reasoning}
              </p>
            </div>

            {/* Parse and display structured reasoning if available */}
            {move.agent_reasoning.includes("Scout:") && (
              <div className="space-y-2 pt-2 border-t border-zinc-200">
                {/* Scout Analysis */}
                {move.agent_reasoning.includes("Scout:") && (
                  <div>
                    <p className="text-xs font-medium text-blue-600 mb-1">
                      Scout Analysis
                    </p>
                    <p className="text-xs text-zinc-600 font-mono">
                      {extractSection(move.agent_reasoning, "Scout:")}
                    </p>
                  </div>
                )}

                {/* Strategist Strategy */}
                {move.agent_reasoning.includes("Strategist:") && (
                  <div>
                    <p className="text-xs font-medium text-purple-600 mb-1">
                      Strategist Strategy
                    </p>
                    <p className="text-xs text-zinc-600 font-mono">
                      {extractSection(move.agent_reasoning, "Strategist:")}
                    </p>
                  </div>
                )}

                {/* Executor Details */}
                {move.agent_reasoning.includes("Executor:") && (
                  <div>
                    <p className="text-xs font-medium text-green-600 mb-1">
                      Executor Details
                    </p>
                    <p className="text-xs text-zinc-600 font-mono">
                      {extractSection(move.agent_reasoning, "Executor:")}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Extract a section from the reasoning text
 */
function extractSection(text: string, prefix: string): string {
  const startIndex = text.indexOf(prefix);
  if (startIndex === -1) return "";

  const afterPrefix = text.substring(startIndex + prefix.length);
  const endIndex = afterPrefix.search(/\n[A-Z][a-z]+:|$/);
  return afterPrefix.substring(0, endIndex === -1 ? undefined : endIndex).trim();
}

export function MoveHistory({ moves, playerSymbol }: MoveHistoryProps) {
  const [expandedMoves, setExpandedMoves] = useState<Set<number>>(new Set());

  const toggleExpanded = (moveNumber: number) => {
    setExpandedMoves((prev) => {
      const next = new Set(prev);
      if (next.has(moveNumber)) {
        next.delete(moveNumber);
      } else {
        next.add(moveNumber);
      }
      return next;
    });
  };

  if (moves.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-zinc-400 text-sm font-mono">
        No moves yet
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-3 py-2 border-b border-zinc-200 bg-zinc-50">
        <h3 className="text-sm font-medium text-zinc-700 font-mono">
          Move History
        </h3>
        <p className="text-xs text-zinc-400 mt-0.5">
          {moves.length} move{moves.length !== 1 ? "s" : ""} • Click to expand AI reasoning
        </p>
      </div>

      {/* Scrollable Move List */}
      <div className="flex-1 overflow-y-auto max-h-[400px]">
        {moves.map((move) => (
          <MoveEntry
            key={move.move_number}
            move={move}
            isPlayer={move.player === playerSymbol}
            isExpanded={expandedMoves.has(move.move_number)}
            onToggle={() => toggleExpanded(move.move_number)}
          />
        ))}
      </div>
    </div>
  );
}
