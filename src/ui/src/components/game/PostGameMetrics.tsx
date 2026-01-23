"use client";

import { useState, useEffect, useCallback } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { cn } from "@/lib/utils";
import {
  apiClient,
  type PostGameMetrics as PostGameMetricsType,
  type AgentCommunication,
  type LLMInteraction,
  type AgentConfig,
  type AgentPerformance,
  type GameSummary,
} from "@/lib/api-client";

interface PostGameMetricsProps {
  gameId: string | null;
  isGameOver: boolean;
}

type MetricsTab = "summary" | "performance" | "llm" | "communication";

/**
 * JSON Syntax Highlighter Component
 */
function JsonDisplay({ data }: { data: Record<string, unknown> }) {
  const jsonString = JSON.stringify(data, null, 2);

  return (
    <pre className="bg-zinc-900 text-zinc-100 p-3 rounded-lg text-xs font-mono overflow-auto max-h-60">
      <code>{jsonString}</code>
    </pre>
  );
}

/**
 * Game Summary Tab Content
 */
function GameSummaryTab({ summary }: { summary: GameSummary | null }) {
  if (!summary) {
    return (
      <div className="text-center text-zinc-400 text-sm font-mono py-8">
        No game summary available
      </div>
    );
  }

  const formatDuration = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    }
    return `${seconds}s`;
  };

  const formatOutcome = (outcome: string): string => {
    switch (outcome) {
      case "X_WINS":
        return "X Wins";
      case "O_WINS":
        return "O Wins";
      case "DRAW":
        return "Draw";
      default:
        return "In Progress";
    }
  };

  const outcomeColor =
    summary.outcome === "X_WINS"
      ? "text-zinc-900"
      : summary.outcome === "O_WINS"
        ? "text-red-600"
        : "text-amber-600";

  return (
    <div className="space-y-4">
      {/* Outcome Banner */}
      <div
        className={cn(
          "p-4 rounded-lg border text-center",
          summary.outcome === "X_WINS" && "bg-zinc-100 border-zinc-300",
          summary.outcome === "O_WINS" && "bg-red-50 border-red-200",
          summary.outcome === "DRAW" && "bg-amber-50 border-amber-200"
        )}
      >
        <p className="text-xs text-zinc-500 font-mono mb-1">Game Outcome</p>
        <p className={cn("text-2xl font-bold font-mono", outcomeColor)}>
          {formatOutcome(summary.outcome)}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 bg-white rounded-lg border border-zinc-200">
          <p className="text-xs text-zinc-500 font-mono mb-1">Total Moves</p>
          <p className="text-xl font-bold text-zinc-900 font-mono">
            {summary.total_moves}
          </p>
        </div>

        <div className="p-3 bg-white rounded-lg border border-zinc-200">
          <p className="text-xs text-zinc-500 font-mono mb-1">Duration</p>
          <p className="text-xl font-bold text-zinc-900 font-mono">
            {formatDuration(summary.duration_ms)}
          </p>
        </div>

        <div className="p-3 bg-white rounded-lg border border-zinc-200">
          <p className="text-xs text-zinc-500 font-mono mb-1">Avg Move Time</p>
          <p className="text-xl font-bold text-zinc-900 font-mono">
            {summary.average_move_time_ms.toFixed(0)}ms
          </p>
        </div>

        <div className="p-3 bg-white rounded-lg border border-zinc-200">
          <p className="text-xs text-zinc-500 font-mono mb-1">Started</p>
          <p className="text-sm font-medium text-zinc-700 font-mono">
            {new Date(summary.start_time).toLocaleTimeString()}
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Performance Summary Tab Content
 */
function PerformanceTab({
  performances,
  totalLlmCalls,
  totalTokens,
}: {
  performances: AgentPerformance[];
  totalLlmCalls: number;
  totalTokens: number;
}) {
  if (performances.length === 0) {
    return (
      <div className="text-center text-zinc-400 text-sm font-mono py-8">
        No performance data available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Totals */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-xs text-blue-600 font-mono mb-1">Total LLM Calls</p>
          <p className="text-xl font-bold text-blue-900 font-mono">
            {totalLlmCalls}
          </p>
        </div>

        <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
          <p className="text-xs text-purple-600 font-mono mb-1">Total Tokens</p>
          <p className="text-xl font-bold text-purple-900 font-mono">
            {totalTokens.toLocaleString()}
          </p>
        </div>
      </div>

      {/* Per-Agent Performance */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-zinc-700 font-mono">
          Per-Agent Performance
        </h4>

        {performances.map((perf) => (
          <div
            key={perf.agent_name}
            className="p-3 bg-white rounded-lg border border-zinc-200"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-zinc-800 font-mono">
                {perf.agent_name}
              </span>
              <span
                className={cn(
                  "text-xs px-2 py-0.5 rounded font-mono",
                  perf.success_rate >= 0.9
                    ? "bg-green-100 text-green-700"
                    : perf.success_rate >= 0.7
                      ? "bg-amber-100 text-amber-700"
                      : "bg-red-100 text-red-700"
                )}
              >
                {(perf.success_rate * 100).toFixed(0)}% success
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs font-mono">
              <div>
                <span className="text-zinc-500">Min:</span>{" "}
                <span className="text-zinc-700">{perf.min_execution_ms}ms</span>
              </div>
              <div>
                <span className="text-zinc-500">Max:</span>{" "}
                <span className="text-zinc-700">{perf.max_execution_ms}ms</span>
              </div>
              <div>
                <span className="text-zinc-500">Avg:</span>{" "}
                <span className="text-zinc-700">
                  {perf.avg_execution_ms.toFixed(0)}ms
                </span>
              </div>
            </div>

            <div className="mt-2 text-xs text-zinc-500 font-mono">
              {perf.successful_calls}/{perf.total_calls} calls successful
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * LLM Interactions Tab Content
 */
function LLMTab({ interactions }: { interactions: LLMInteraction[] }) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (interactions.length === 0) {
    return (
      <div className="text-center text-zinc-400 text-sm font-mono py-8">
        No LLM interactions (rule-based mode)
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {interactions.map((interaction, index) => (
        <div
          key={index}
          className="bg-white rounded-lg border border-zinc-200 overflow-hidden"
        >
          {/* Header */}
          <button
            type="button"
            onClick={() =>
              setExpandedIndex(expandedIndex === index ? null : index)
            }
            className="w-full px-3 py-2 flex items-center justify-between hover:bg-zinc-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "text-xs px-2 py-0.5 rounded font-mono",
                  interaction.agent_name === "Scout" && "bg-blue-100 text-blue-700",
                  interaction.agent_name === "Strategist" &&
                    "bg-purple-100 text-purple-700",
                  interaction.agent_name === "Executor" &&
                    "bg-green-100 text-green-700"
                )}
              >
                {interaction.agent_name}
              </span>
              <span className="text-xs text-zinc-500 font-mono">
                {interaction.provider}/{interaction.model}
              </span>
            </div>

            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="text-zinc-500">
                {interaction.total_tokens} tokens
              </span>
              <span className="text-zinc-500">{interaction.latency_ms}ms</span>
              <svg
                className={cn(
                  "w-4 h-4 text-zinc-400 transition-transform",
                  expandedIndex === index && "rotate-180"
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
            </div>
          </button>

          {/* Expanded Content */}
          {expandedIndex === index && (
            <div className="px-3 pb-3 space-y-3 border-t border-zinc-100">
              {/* Token Breakdown */}
              <div className="flex gap-4 pt-2 text-xs font-mono">
                <span className="text-zinc-500">
                  Input: {interaction.input_tokens}
                </span>
                <span className="text-zinc-500">
                  Output: {interaction.output_tokens}
                </span>
              </div>

              {/* Prompt */}
              <div>
                <p className="text-xs font-medium text-zinc-500 mb-1">Prompt</p>
                <pre className="bg-zinc-100 p-2 rounded text-xs font-mono text-zinc-700 overflow-auto max-h-40 whitespace-pre-wrap">
                  {interaction.prompt}
                </pre>
              </div>

              {/* Response */}
              <div>
                <p className="text-xs font-medium text-zinc-500 mb-1">Response</p>
                <pre className="bg-zinc-100 p-2 rounded text-xs font-mono text-zinc-700 overflow-auto max-h-40 whitespace-pre-wrap">
                  {interaction.response}
                </pre>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/**
 * Agent Communication Tab Content
 */
function CommunicationTab({
  communications,
}: {
  communications: AgentCommunication[];
}) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (communications.length === 0) {
    return (
      <div className="text-center text-zinc-400 text-sm font-mono py-8">
        No agent communications recorded
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {communications.map((comm, index) => (
        <div
          key={index}
          className="bg-white rounded-lg border border-zinc-200 overflow-hidden"
        >
          {/* Header */}
          <button
            type="button"
            onClick={() =>
              setExpandedIndex(expandedIndex === index ? null : index)
            }
            className="w-full px-3 py-2 flex items-center justify-between hover:bg-zinc-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  "text-xs px-2 py-0.5 rounded font-mono",
                  comm.agent_name === "Scout" && "bg-blue-100 text-blue-700",
                  comm.agent_name === "Strategist" &&
                    "bg-purple-100 text-purple-700",
                  comm.agent_name === "Executor" && "bg-green-100 text-green-700"
                )}
              >
                {comm.agent_name}
              </span>
              <span className="text-xs text-zinc-500 font-mono">
                {new Date(comm.timestamp).toLocaleTimeString()}
              </span>
            </div>

            <div className="flex items-center gap-3 text-xs font-mono">
              <span className="text-zinc-500">{comm.execution_time_ms}ms</span>
              <svg
                className={cn(
                  "w-4 h-4 text-zinc-400 transition-transform",
                  expandedIndex === index && "rotate-180"
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
            </div>
          </button>

          {/* Expanded Content */}
          {expandedIndex === index && (
            <div className="px-3 pb-3 space-y-3 border-t border-zinc-100 pt-2">
              {/* Request */}
              <div>
                <p className="text-xs font-medium text-zinc-500 mb-1">Request</p>
                <JsonDisplay data={comm.request} />
              </div>

              {/* Response */}
              <div>
                <p className="text-xs font-medium text-zinc-500 mb-1">Response</p>
                <JsonDisplay data={comm.response} />
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

/**
 * Agent Configuration Display
 */
function ConfigTab({ configs }: { configs: AgentConfig[] }) {
  if (configs.length === 0) {
    return (
      <div className="text-center text-zinc-400 text-sm font-mono py-8">
        No agent configuration available
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {configs.map((config) => (
        <div
          key={config.agent_name}
          className="p-3 bg-white rounded-lg border border-zinc-200"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-zinc-800 font-mono">
              {config.agent_name}
            </span>
            <span
              className={cn(
                "text-xs px-2 py-0.5 rounded font-mono",
                config.mode === "local"
                  ? "bg-zinc-100 text-zinc-700"
                  : "bg-blue-100 text-blue-700"
              )}
            >
              {config.mode === "local" ? "Local" : "MCP"}
            </span>
          </div>

          <div className="space-y-1 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-zinc-500">Framework:</span>
              <span className="text-zinc-700">{config.llm_framework}</span>
            </div>

            {config.provider && (
              <div className="flex justify-between">
                <span className="text-zinc-500">Provider:</span>
                <span className="text-zinc-700">{config.provider}</span>
              </div>
            )}

            {config.model && (
              <div className="flex justify-between">
                <span className="text-zinc-500">Model:</span>
                <span className="text-zinc-700">{config.model}</span>
              </div>
            )}

            <div className="flex justify-between">
              <span className="text-zinc-500">Timeout:</span>
              <span className="text-zinc-700">{config.timeout_ms}ms</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Post-Game Metrics Panel
 *
 * Displays comprehensive metrics after a game ends including:
 * - Game Summary (outcome, moves, duration)
 * - Performance Summary (per-agent stats)
 * - LLM Interactions (prompts, tokens, latency)
 * - Agent Communication (request/response JSON)
 */
export function PostGameMetrics({ gameId, isGameOver }: PostGameMetricsProps) {
  const [activeTab, setActiveTab] = useState<MetricsTab>("summary");
  const [metrics, setMetrics] = useState<PostGameMetricsType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch metrics when game ends
  const fetchMetrics = useCallback(async () => {
    if (!gameId || !isGameOver) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await apiClient.getPostGameMetrics(gameId);
      setMetrics(data);
    } catch {
      // For now, show placeholder data since backend may not have this endpoint yet
      setError("Metrics endpoint not available yet");
      // Create mock data for UI demonstration
      setMetrics({
        game_id: gameId,
        game_summary: {
          total_moves: 5,
          duration_ms: 15000,
          outcome: "X_WINS",
          average_move_time_ms: 3000,
          start_time: new Date(Date.now() - 15000).toISOString(),
          end_time: new Date().toISOString(),
        },
        agent_communications: [
          {
            agent_name: "Scout",
            request: { board: [["X", null, null], [null, "O", null], [null, null, null]], player: "O" },
            response: { threats: [], opportunities: [{ position: { row: 0, col: 2 }, confidence: 0.8 }] },
            timestamp: new Date().toISOString(),
            execution_time_ms: 125,
          },
          {
            agent_name: "Strategist",
            request: { analysis: { threats: [], opportunities: [] } },
            response: { primary_move: { row: 0, col: 2 }, priority: 80, reasoning: "Block potential fork" },
            timestamp: new Date().toISOString(),
            execution_time_ms: 200,
          },
        ],
        llm_interactions: [],
        agent_configs: [
          { agent_name: "Scout", mode: "local", llm_framework: "Pydantic AI", provider: null, model: null, timeout_ms: 5000 },
          { agent_name: "Strategist", mode: "local", llm_framework: "Pydantic AI", provider: null, model: null, timeout_ms: 5000 },
          { agent_name: "Executor", mode: "local", llm_framework: "Rule-based", provider: null, model: null, timeout_ms: 1000 },
        ],
        agent_performances: [
          { agent_name: "Scout", min_execution_ms: 100, max_execution_ms: 150, avg_execution_ms: 125, total_calls: 3, successful_calls: 3, failed_calls: 0, success_rate: 1.0 },
          { agent_name: "Strategist", min_execution_ms: 180, max_execution_ms: 220, avg_execution_ms: 200, total_calls: 3, successful_calls: 3, failed_calls: 0, success_rate: 1.0 },
          { agent_name: "Executor", min_execution_ms: 5, max_execution_ms: 10, avg_execution_ms: 7, total_calls: 3, successful_calls: 3, failed_calls: 0, success_rate: 1.0 },
        ],
        total_llm_calls: 0,
        total_tokens_used: 0,
      });
    } finally {
      setIsLoading(false);
    }
  }, [gameId, isGameOver]);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  // Show placeholder when game is not over
  if (!isGameOver) {
    return (
      <div className="flex items-center justify-center h-full text-zinc-400 text-sm font-mono">
        Metrics will appear after game ends
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-zinc-500 font-mono text-sm animate-pulse">
          Loading metrics...
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-3 py-2 border-b border-zinc-200 bg-zinc-50">
        <h3 className="text-sm font-medium text-zinc-700 font-mono">
          Post-Game Metrics
        </h3>
        <p className="text-xs text-zinc-400 mt-0.5">
          Game analysis and performance data
        </p>
      </div>

      {/* Sub-tabs */}
      <div className="px-3 pt-2">
        <Tabs
          value={activeTab}
          onValueChange={(value) => setActiveTab(value as MetricsTab)}
        >
          <TabsList className="bg-zinc-100 w-full">
            <TabsTrigger
              value="summary"
              className="flex-1 text-xs font-mono data-[state=active]:bg-white"
            >
              Summary
            </TabsTrigger>
            <TabsTrigger
              value="performance"
              className="flex-1 text-xs font-mono data-[state=active]:bg-white"
            >
              Performance
            </TabsTrigger>
            <TabsTrigger
              value="llm"
              className="flex-1 text-xs font-mono data-[state=active]:bg-white"
            >
              LLM
            </TabsTrigger>
            <TabsTrigger
              value="communication"
              className="flex-1 text-xs font-mono data-[state=active]:bg-white"
            >
              Comms
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-3">
        {error && (
          <div className="mb-3 p-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-700 font-mono">
            Note: Using demo data ({error})
          </div>
        )}

        {activeTab === "summary" && (
          <GameSummaryTab summary={metrics?.game_summary ?? null} />
        )}

        {activeTab === "performance" && (
          <PerformanceTab
            performances={metrics?.agent_performances ?? []}
            totalLlmCalls={metrics?.total_llm_calls ?? 0}
            totalTokens={metrics?.total_tokens_used ?? 0}
          />
        )}

        {activeTab === "llm" && (
          <>
            {metrics?.llm_interactions.length === 0 ? (
              <div className="space-y-4">
                <div className="text-center text-zinc-400 text-sm font-mono py-4">
                  No LLM interactions (rule-based mode)
                </div>
                <ConfigTab configs={metrics?.agent_configs ?? []} />
              </div>
            ) : (
              <LLMTab interactions={metrics?.llm_interactions ?? []} />
            )}
          </>
        )}

        {activeTab === "communication" && (
          <CommunicationTab communications={metrics?.agent_communications ?? []} />
        )}
      </div>
    </div>
  );
}
