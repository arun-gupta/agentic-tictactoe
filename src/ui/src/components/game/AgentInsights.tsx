"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { apiClient, type AgentStatus } from "@/lib/api-client";

interface AgentInsightsProps {
  isProcessing: boolean;
  onForceFallback?: () => void;
  onRetry?: () => void;
  lastError?: string | null;
}

interface AgentSectionProps {
  name: string;
  status: AgentStatus | null;
  color: string;
  description: string;
}

/**
 * Get the processing phase based on elapsed time
 */
function getProcessingPhase(elapsedMs: number): {
  phase: "spinner" | "message" | "progress" | "warning" | "fallback";
  message: string;
} {
  const seconds = elapsedMs / 1000;
  if (seconds < 2) {
    return { phase: "spinner", message: "Processing..." };
  } else if (seconds < 5) {
    return { phase: "message", message: "Analyzing board position..." };
  } else if (seconds < 10) {
    return { phase: "progress", message: `Still thinking... (${seconds.toFixed(1)}s)` };
  } else if (seconds < 15) {
    return { phase: "warning", message: "Taking longer than expected..." };
  } else {
    return { phase: "fallback", message: "Timeout - using fallback strategy" };
  }
}

function AgentSection({ name, status, color, description }: AgentSectionProps) {
  const isIdle = !status || status.status === "idle";
  const isProcessing = status?.status === "processing";
  const isSuccess = status?.status === "success";
  const isFailed = status?.status === "failed";

  return (
    <div className={cn("p-3 rounded-lg border", "bg-white")}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className={cn("w-2 h-2 rounded-full", color)} />
          <h4 className="text-sm font-medium text-zinc-800 font-mono">{name}</h4>
        </div>
        {/* Status Badge */}
        <span
          className={cn(
            "text-xs px-2 py-0.5 rounded font-mono",
            isIdle && "bg-zinc-100 text-zinc-500",
            isProcessing && "bg-blue-100 text-blue-700 animate-pulse",
            isSuccess && "bg-green-100 text-green-700",
            isFailed && "bg-red-100 text-red-700"
          )}
        >
          {status?.status || "idle"}
        </span>
      </div>

      {/* Description */}
      <p className="text-xs text-zinc-500 mb-2">{description}</p>

      {/* Status Details */}
      {isProcessing && status?.elapsed_time_ms && (
        <div className="text-xs text-blue-600 font-mono">
          Elapsed: {(status.elapsed_time_ms / 1000).toFixed(1)}s
        </div>
      )}

      {isSuccess && status?.execution_time_ms && (
        <div className="text-xs text-green-600 font-mono">
          Completed in {status.execution_time_ms.toFixed(0)}ms
        </div>
      )}

      {isFailed && status?.error_message && (
        <div className="text-xs text-red-600 font-mono truncate">
          Error: {status.error_message}
        </div>
      )}
    </div>
  );
}

function ProcessingIndicator({ elapsedMs }: { elapsedMs: number }) {
  const { phase, message } = getProcessingPhase(elapsedMs);
  const progress = Math.min((elapsedMs / 15000) * 100, 100);

  return (
    <div className="space-y-2">
      {/* Spinner for early phase */}
      {phase === "spinner" && (
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-zinc-300 border-t-zinc-600 rounded-full animate-spin" />
          <span className="text-sm text-zinc-600 font-mono">{message}</span>
        </div>
      )}

      {/* Message phase */}
      {phase === "message" && (
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
          <span className="text-sm text-blue-600 font-mono">{message}</span>
        </div>
      )}

      {/* Progress bar phase */}
      {phase === "progress" && (
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-sm text-zinc-600 font-mono">{message}</span>
            <span className="text-xs text-zinc-400 font-mono">{progress.toFixed(0)}%</span>
          </div>
          <div className="h-2 bg-zinc-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all duration-100"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Warning phase */}
      {phase === "warning" && (
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <svg
              className="w-4 h-4 text-amber-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <span className="text-sm text-amber-600 font-mono">{message}</span>
          </div>
          <p className="text-xs text-amber-500">
            Fallback will be triggered automatically at 15s
          </p>
          <div className="h-2 bg-zinc-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-amber-500 transition-all duration-100"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Fallback phase */}
      {phase === "fallback" && (
        <div className="flex items-center gap-2 text-red-600">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span className="text-sm font-mono">{message}</span>
        </div>
      )}
    </div>
  );
}

export function AgentInsights({
  isProcessing,
  onForceFallback,
  onRetry,
  lastError,
}: AgentInsightsProps) {
  const [scoutStatus, setScoutStatus] = useState<AgentStatus | null>(null);
  const [strategistStatus, setStrategistStatus] = useState<AgentStatus | null>(null);
  const [executorStatus, setExecutorStatus] = useState<AgentStatus | null>(null);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [startTime, setStartTime] = useState<number | null>(null);

  // Poll agent status while processing
  useEffect(() => {
    if (!isProcessing) {
      setStartTime(null);
      setElapsedMs(0);
      return;
    }

    // Set start time when processing begins
    if (startTime === null) {
      setStartTime(Date.now());
    }

    // Update elapsed time every 100ms
    const interval = setInterval(() => {
      if (startTime) {
        setElapsedMs(Date.now() - startTime);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isProcessing, startTime]);

  // Fetch agent statuses
  const fetchAgentStatuses = useCallback(async () => {
    try {
      const [scout, strategist, executor] = await Promise.all([
        apiClient.getAgentStatus("scout"),
        apiClient.getAgentStatus("strategist"),
        apiClient.getAgentStatus("executor"),
      ]);
      setScoutStatus(scout);
      setStrategistStatus(strategist);
      setExecutorStatus(executor);
    } catch {
      // Silently fail - status display is non-critical
    }
  }, []);

  // Poll agent statuses while processing
  useEffect(() => {
    if (!isProcessing) return;

    fetchAgentStatuses();
    const interval = setInterval(fetchAgentStatuses, 500);

    return () => clearInterval(interval);
  }, [isProcessing, fetchAgentStatuses]);

  const showForceFallback = isProcessing && elapsedMs >= 10000;
  const showRetry = !isProcessing && lastError;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-3 py-2 border-b border-zinc-200 bg-zinc-50">
        <h3 className="text-sm font-medium text-zinc-700 font-mono">
          Agent Insights
        </h3>
        <p className="text-xs text-zinc-400 mt-0.5">
          Real-time AI decision making
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {/* Processing Indicator */}
        {isProcessing && (
          <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
            <ProcessingIndicator elapsedMs={elapsedMs} />
          </div>
        )}

        {/* Error Display */}
        {lastError && !isProcessing && (
          <div className="p-3 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center gap-2 text-red-700">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-sm font-mono">Error occurred</span>
            </div>
            <p className="text-xs text-red-600 mt-1 font-mono">{lastError}</p>
          </div>
        )}

        {/* Agent Sections */}
        <AgentSection
          name="Scout"
          status={scoutStatus}
          color="bg-blue-500"
          description="Analyzes board for threats and opportunities"
        />

        <AgentSection
          name="Strategist"
          status={strategistStatus}
          color="bg-purple-500"
          description="Develops move strategy and priorities"
        />

        <AgentSection
          name="Executor"
          status={executorStatus}
          color="bg-green-500"
          description="Validates and executes the chosen move"
        />

        {/* Action Buttons */}
        {(showForceFallback || showRetry) && (
          <div className="pt-2 border-t border-zinc-200 space-y-2">
            {showForceFallback && onForceFallback && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onForceFallback}
                className="w-full text-xs font-mono bg-amber-100 hover:bg-amber-200 text-amber-800 border-amber-300"
              >
                Force Fallback
              </Button>
            )}

            {showRetry && onRetry && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onRetry}
                className="w-full text-xs font-mono bg-blue-100 hover:bg-blue-200 text-blue-800 border-blue-300"
              >
                Retry
              </Button>
            )}

            {showForceFallback && (
              <p className="text-xs text-zinc-500 text-center">
                Use a simple fallback move instead of waiting
              </p>
            )}
          </div>
        )}

        {/* Idle State */}
        {!isProcessing && !lastError && (
          <div className="text-center text-zinc-400 text-sm font-mono py-4">
            Waiting for AI turn...
          </div>
        )}
      </div>
    </div>
  );
}
