"use client";

import { useState, useEffect, useCallback, createContext, useContext } from "react";
import { Button } from "@/components/ui/button";

// Error severity types
export type ErrorSeverity = "critical" | "warning" | "info";

// Fallback strategy types
export type FallbackStrategy =
  | "rule_based_analysis"
  | "priority_based_selection"
  | "random_valid_move";

// Error message interface
export interface ErrorMessage {
  id: string;
  severity: ErrorSeverity;
  title: string;
  message: string;
  errorCode?: string;
  timestamp: Date;
  autoDismiss?: boolean;
}

// Fallback notification interface
export interface FallbackNotification {
  id: string;
  reason: string;
  strategy: FallbackStrategy;
  timestamp: Date;
}

// Context for error handling
interface ErrorContextType {
  errors: ErrorMessage[];
  fallback: FallbackNotification | null;
  showError: (
    severity: ErrorSeverity,
    title: string,
    message: string,
    errorCode?: string
  ) => void;
  showFallback: (reason: string, strategy: FallbackStrategy) => void;
  dismissError: (id: string) => void;
  clearFallback: () => void;
  clearAll: () => void;
}

const ErrorContext = createContext<ErrorContextType | null>(null);

/**
 * Hook to use error handling context
 */
export function useErrorHandling() {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error("useErrorHandling must be used within ErrorProvider");
  }
  return context;
}

/**
 * Error Provider Component
 */
export function ErrorProvider({ children }: { children: React.ReactNode }) {
  const [errors, setErrors] = useState<ErrorMessage[]>([]);
  const [fallback, setFallback] = useState<FallbackNotification | null>(null);

  const showError = useCallback(
    (
      severity: ErrorSeverity,
      title: string,
      message: string,
      errorCode?: string
    ) => {
      const newError: ErrorMessage = {
        id: `error-${Date.now()}-${Math.random().toString(36).slice(2)}`,
        severity,
        title,
        message,
        errorCode,
        timestamp: new Date(),
        autoDismiss: severity !== "critical",
      };
      setErrors((prev) => [...prev, newError]);
    },
    []
  );

  const showFallback = useCallback(
    (reason: string, strategy: FallbackStrategy) => {
      setFallback({
        id: `fallback-${Date.now()}`,
        reason,
        strategy,
        timestamp: new Date(),
      });
    },
    []
  );

  const dismissError = useCallback((id: string) => {
    setErrors((prev) => prev.filter((e) => e.id !== id));
  }, []);

  const clearFallback = useCallback(() => {
    setFallback(null);
  }, []);

  const clearAll = useCallback(() => {
    setErrors([]);
    setFallback(null);
  }, []);

  return (
    <ErrorContext.Provider
      value={{
        errors,
        fallback,
        showError,
        showFallback,
        dismissError,
        clearFallback,
        clearAll,
      }}
    >
      {children}
    </ErrorContext.Provider>
  );
}

/**
 * Critical Error Modal
 */
export function ErrorModal({
  error,
  onDismiss,
}: {
  error: ErrorMessage;
  onDismiss: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onDismiss}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-red-600 px-4 py-3">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-white"
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
            <h2 className="text-white font-medium font-mono">{error.title}</h2>
          </div>
        </div>

        {/* Body */}
        <div className="px-4 py-4">
          <p className="text-zinc-700 text-sm font-mono">{error.message}</p>
          {error.errorCode && (
            <p className="mt-2 text-xs text-zinc-500 font-mono">
              Error code: {error.errorCode}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-3 bg-zinc-50 flex justify-end">
          <Button
            variant="secondary"
            size="sm"
            onClick={onDismiss}
            className="text-xs font-mono"
          >
            Dismiss
          </Button>
        </div>
      </div>
    </div>
  );
}

/**
 * Warning Badge Component
 */
export function WarningBadge({
  error,
  onDismiss,
}: {
  error: ErrorMessage;
  onDismiss: () => void;
}) {
  // Auto-dismiss after 5 seconds
  useEffect(() => {
    if (error.autoDismiss) {
      const timer = setTimeout(onDismiss, 5000);
      return () => clearTimeout(timer);
    }
  }, [error.autoDismiss, onDismiss]);

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-amber-100 border border-amber-300 rounded-lg animate-in slide-in-from-top-2 duration-200">
      <svg
        className="w-4 h-4 text-amber-600 flex-shrink-0"
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
      <span className="text-xs text-amber-800 font-mono flex-1">
        {error.message}
      </span>
      <button
        type="button"
        onClick={onDismiss}
        className="text-amber-600 hover:text-amber-800 transition-colors"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
  );
}

/**
 * Info Toast Component (bottom-right)
 */
export function InfoToast({
  error,
  onDismiss,
}: {
  error: ErrorMessage;
  onDismiss: () => void;
}) {
  // Auto-dismiss after 3 seconds
  useEffect(() => {
    const timer = setTimeout(onDismiss, 3000);
    return () => clearTimeout(timer);
  }, [onDismiss]);

  return (
    <div className="flex items-center gap-2 px-3 py-2 bg-blue-100 border border-blue-300 rounded-lg shadow-lg animate-in slide-in-from-right-5 duration-200">
      <svg
        className="w-4 h-4 text-blue-600 flex-shrink-0"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span className="text-xs text-blue-800 font-mono">{error.message}</span>
    </div>
  );
}

/**
 * Fallback Notification Badge
 */
export function FallbackBadge({
  notification,
  onDismiss,
}: {
  notification: FallbackNotification;
  onDismiss: () => void;
}) {
  const strategyLabels: Record<FallbackStrategy, string> = {
    rule_based_analysis: "Rule-based analysis",
    priority_based_selection: "Priority-based selection",
    random_valid_move: "Random valid move",
  };

  return (
    <div className="px-3 py-2 bg-orange-100 border border-orange-300 rounded-lg animate-in fade-in duration-200">
      <div className="flex items-center justify-between gap-2 mb-1">
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4 text-orange-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          <span className="text-xs font-medium text-orange-800 font-mono">
            Fallback Used
          </span>
        </div>
        <button
          type="button"
          onClick={onDismiss}
          className="text-orange-600 hover:text-orange-800 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
      <p className="text-xs text-orange-700 font-mono">
        Reason: {notification.reason}
      </p>
      <p className="text-xs text-orange-600 font-mono mt-0.5">
        Strategy: {strategyLabels[notification.strategy]}
      </p>
    </div>
  );
}

/**
 * Error Display Container
 * Renders all active errors and fallback notifications
 */
export function ErrorDisplay() {
  const { errors, fallback, dismissError, clearFallback } = useErrorHandling();

  const criticalErrors = errors.filter((e) => e.severity === "critical");
  const warnings = errors.filter((e) => e.severity === "warning");
  const infoMessages = errors.filter((e) => e.severity === "info");

  return (
    <>
      {/* Critical Error Modals */}
      {criticalErrors.map((error) => (
        <ErrorModal
          key={error.id}
          error={error}
          onDismiss={() => dismissError(error.id)}
        />
      ))}

      {/* Warning Badges (top of game board) */}
      {warnings.length > 0 && (
        <div className="absolute top-20 left-5 right-5 space-y-2 z-40">
          {warnings.map((error) => (
            <WarningBadge
              key={error.id}
              error={error}
              onDismiss={() => dismissError(error.id)}
            />
          ))}
        </div>
      )}

      {/* Fallback Badge */}
      {fallback && (
        <div className="absolute top-20 left-5 right-5 z-40">
          <FallbackBadge notification={fallback} onDismiss={clearFallback} />
        </div>
      )}

      {/* Info Toasts (bottom-right) */}
      {infoMessages.length > 0 && (
        <div className="absolute bottom-5 right-5 space-y-2 z-40">
          {infoMessages.map((error) => (
            <InfoToast
              key={error.id}
              error={error}
              onDismiss={() => dismissError(error.id)}
            />
          ))}
        </div>
      )}
    </>
  );
}

/**
 * Cell Error Animation Classes
 * Use these with the Cell component for error states
 */
export const cellErrorClasses = {
  shake: "animate-shake",
  errorHighlight: "border-red-500 bg-red-50",
};

/**
 * CSS for shake animation (add to globals.css or tailwind config)
 */
export const shakeAnimationCSS = `
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}
`;
