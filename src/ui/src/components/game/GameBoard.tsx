"use client";

import { useState, useCallback, useEffect } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Cell } from "./Cell";
import { MoveHistory } from "./MoveHistory";
import { AgentInsights } from "./AgentInsights";
import { PostGameMetrics } from "./PostGameMetrics";
import { ConfigurationPanel } from "./ConfigurationPanel";
import {
  FallbackBadge,
  type FallbackNotification,
  type FallbackStrategy,
} from "./ErrorHandling";
import {
  apiClient,
  type GameState,
  type CellValue,
  type Position,
  type MoveHistory as MoveHistoryType,
  ApiError,
  NetworkError,
} from "@/lib/api-client";
import { cn } from "@/lib/utils";

type TabValue = "board" | "history" | "insights" | "config" | "metrics";

interface GameBoardProps {
  initialTab?: TabValue;
}

export function GameBoard({ initialTab = "board" }: GameBoardProps) {
  const [activeTab, setActiveTab] = useState<TabValue>(initialTab);
  const [gameId, setGameId] = useState<string | null>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [lastMove, setLastMove] = useState<Position | null>(null);
  const [moveHistory, setMoveHistory] = useState<MoveHistoryType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isAiTurn, setIsAiTurn] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState("Click 'New Game' to start");
  const [fallbackNotification, setFallbackNotification] = useState<FallbackNotification | null>(null);
  const [errorCell, setErrorCell] = useState<Position | null>(null);
  const [shakingCell, setShakingCell] = useState<Position | null>(null);

  // Auto-dismiss error after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  // Start a new game
  const handleNewGame = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setFallbackNotification(null);
    setErrorCell(null);
    setShakingCell(null);
    try {
      const response = await apiClient.createGame("X");
      setGameId(response.game_id);
      setGameState(response.game_state);
      setLastMove(null);
      setMoveHistory([]);
      setIsAiTurn(false);
      setStatusMessage("Your turn (X)");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else if (err instanceof NetworkError) {
        setError(err.message);
      } else {
        setError("Failed to start new game");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Trigger cell shake animation
  const triggerCellShake = useCallback((position: Position) => {
    setErrorCell(position);
    setShakingCell(position);
    // Clear shake animation after 500ms
    setTimeout(() => setShakingCell(null), 500);
    // Clear error highlight after 2s
    setTimeout(() => setErrorCell(null), 2000);
  }, []);

  // Make a player move
  const handleCellClick = useCallback(
    async (row: number, col: number) => {
      if (!gameId || !gameState?.board || isAiTurn || gameState.is_game_over) return;

      // Check if cell is already occupied
      if (gameState.board[row]?.[col]) {
        triggerCellShake({ row, col });
        setError("Cell is already occupied");
        return;
      }

      setIsLoading(true);
      setError(null);
      setFallbackNotification(null);
      setIsAiTurn(true);
      setStatusMessage("AI is thinking...");

      try {
        const response = await apiClient.makeMove(gameId, row, col);

        if (response.success && response.updated_game_state) {
          setGameState(response.updated_game_state);

          // Track last move (AI's move if it played, otherwise player's move)
          if (response.ai_move_execution?.position) {
            setLastMove(response.ai_move_execution.position);
          } else {
            setLastMove({ row, col });
          }

          // Check if fallback was used
          if (response.fallback_used) {
            const reason = response.ai_move_execution?.reasoning || "AI timeout or error";
            setFallbackNotification({
              id: `fallback-${Date.now()}`,
              reason: reason,
              strategy: "rule_based_analysis" as FallbackStrategy,
              timestamp: new Date(),
            });
          }

          // Update move history
          const history = await apiClient.getGameHistory(gameId);
          setMoveHistory(history);

          // Update status message
          const state = response.updated_game_state;
          if (state.is_game_over) {
            if (state.winner === "X") {
              setStatusMessage("You win!");
            } else if (state.winner === "O") {
              setStatusMessage("AI wins!");
            } else {
              setStatusMessage("It's a draw!");
            }
          } else {
            setStatusMessage(
              state.current_player === state.player_symbol
                ? `Your turn (${state.player_symbol})`
                : `AI's turn (${state.ai_symbol})`
            );
          }
        } else {
          setError(response.error_message || "Move failed");
          // Shake the cell on error
          triggerCellShake({ row, col });
        }
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else if (err instanceof NetworkError) {
          setError(err.message);
        } else {
          setError("Failed to make move");
        }
        // Shake the cell on error
        triggerCellShake({ row, col });
      } finally {
        setIsLoading(false);
        setIsAiTurn(false);
      }
    },
    [gameId, gameState, isAiTurn, triggerCellShake]
  );

  // Format move history for display
  const formatMoveHistory = (): string => {
    if (moveHistory.length === 0) return "";

    return moveHistory
      .slice(-3) // Show last 3 moves
      .map((move) => {
        const player = move.player === gameState?.player_symbol ? "You" : "AI";
        return `${player} played: row ${move.position.row}, col ${move.position.col}`;
      })
      .join(" ");
  };

  // Get cell value from board
  const getCellValue = (row: number, col: number): CellValue => {
    if (!gameState?.board?.[row]) return null;
    return gameState.board[row][col];
  };

  // Check if cell is the last move
  const isLastMoveCell = (row: number, col: number): boolean => {
    if (!lastMove) return false;
    return lastMove.row === row && lastMove.col === col;
  };

  // Check if cell has error
  const isCellError = (row: number, col: number): boolean => {
    if (!errorCell) return false;
    return errorCell.row === row && errorCell.col === col;
  };

  // Check if cell is shaking
  const isCellShaking = (row: number, col: number): boolean => {
    if (!shakingCell) return false;
    return shakingCell.row === row && shakingCell.col === col;
  };

  return (
    <div
      className={cn(
        "relative w-[640px] h-[640px]",
        "bg-zinc-100 shadow-lg rounded-lg"
      )}
    >
      {/* Menu Bar */}
      <div className="absolute top-5 left-5 right-5 flex items-center justify-between">
        {/* Tabs */}
        <Tabs
          value={activeTab}
          onValueChange={(value) => setActiveTab(value as TabValue)}
        >
          <TabsList className="bg-transparent border border-zinc-300 rounded-sm">
            <TabsTrigger
              value="board"
              className="data-[state=active]:bg-zinc-900 data-[state=active]:text-zinc-100 rounded-sm text-sm px-4 py-2"
            >
              Board
            </TabsTrigger>
            <TabsTrigger
              value="history"
              className="data-[state=active]:bg-zinc-900 data-[state=active]:text-zinc-100 rounded-sm text-sm px-4 py-2"
            >
              History
            </TabsTrigger>
            <TabsTrigger
              value="insights"
              className="data-[state=active]:bg-zinc-900 data-[state=active]:text-zinc-100 rounded-sm text-sm px-4 py-2"
            >
              Insights
            </TabsTrigger>
            <TabsTrigger
              value="config"
              className="data-[state=active]:bg-zinc-900 data-[state=active]:text-zinc-100 rounded-sm text-sm px-4 py-2"
            >
              Config
            </TabsTrigger>
            <TabsTrigger
              value="metrics"
              className="data-[state=active]:bg-zinc-900 data-[state=active]:text-zinc-100 rounded-sm text-sm px-4 py-2"
            >
              Metrics
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Status */}
        <p className="text-xs text-zinc-700 font-mono">
          Status: {statusMessage}
        </p>

        {/* New Game Button */}
        <Button
          variant="secondary"
          size="sm"
          onClick={handleNewGame}
          disabled={isLoading}
          className="text-xs font-mono h-8 px-3 shadow-sm"
        >
          New Game
        </Button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded text-sm animate-pulse z-40">
          {error}
        </div>
      )}

      {/* Fallback Notification */}
      {fallbackNotification && !error && (
        <div className="absolute top-16 left-5 right-5 z-40">
          <FallbackBadge
            notification={fallbackNotification}
            onDismiss={() => setFallbackNotification(null)}
          />
        </div>
      )}

      {/* Board Tab Content */}
      {activeTab === "board" && (
        <>
          {/* Play Area - 3x3 Grid */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="grid grid-cols-3 gap-0">
              {[0, 1, 2].map((row) =>
                [0, 1, 2].map((col) => (
                  <Cell
                    key={`${row}-${col}`}
                    value={getCellValue(row, col)}
                    row={row}
                    col={col}
                    isLastMove={isLastMoveCell(row, col)}
                    isDisabled={isLoading || isAiTurn || !gameId}
                    isGameOver={gameState?.is_game_over ?? false}
                    hasError={isCellError(row, col)}
                    isShaking={isCellShaking(row, col)}
                    onClick={handleCellClick}
                  />
                ))
              )}
            </div>
          </div>

          {/* Move History */}
          <p className="absolute bottom-5 left-5 text-xs text-zinc-400 font-mono max-w-[600px] truncate">
            {formatMoveHistory() || (gameId ? "Make your first move" : "")}
          </p>

          {/* Move Count */}
          {gameState && (
            <p className="absolute bottom-5 right-5 text-xs text-zinc-500 font-mono">
              Move: {gameState.move_count}
            </p>
          )}
        </>
      )}

      {/* History Tab Content */}
      {activeTab === "history" && (
        <div className="absolute top-16 left-5 right-5 bottom-5 bg-white rounded-lg border border-zinc-200 overflow-hidden">
          <MoveHistory
            moves={moveHistory}
            playerSymbol={gameState?.player_symbol ?? "X"}
          />
        </div>
      )}

      {/* Insights Tab Content */}
      {activeTab === "insights" && (
        <div className="absolute top-16 left-5 right-5 bottom-5 bg-white rounded-lg border border-zinc-200 overflow-hidden">
          <AgentInsights
            isProcessing={isAiTurn}
            lastError={error}
          />
        </div>
      )}

      {/* Config Tab Content */}
      {activeTab === "config" && (
        <div className="absolute top-16 left-5 right-5 bottom-5 bg-white rounded-lg border border-zinc-200 overflow-hidden">
          <ConfigurationPanel />
        </div>
      )}

      {/* Metrics Tab Content */}
      {activeTab === "metrics" && (
        <div className="absolute top-16 left-5 right-5 bottom-5 bg-white rounded-lg border border-zinc-200 overflow-hidden">
          <PostGameMetrics
            gameId={gameId}
            isGameOver={gameState?.is_game_over ?? false}
          />
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-zinc-100/50 flex items-center justify-center rounded-lg">
          <div className="text-zinc-600 font-mono text-sm animate-pulse">
            {isAiTurn ? "AI is thinking..." : "Loading..."}
          </div>
        </div>
      )}
    </div>
  );
}
