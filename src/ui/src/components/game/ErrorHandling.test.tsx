import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  ErrorProvider,
  useErrorHandling,
  ErrorModal,
  WarningBadge,
  InfoToast,
  FallbackBadge,
  ErrorDisplay,
  type ErrorMessage,
  type FallbackNotification,
} from "./ErrorHandling";

// Helper component to test the hook
function TestComponent() {
  const {
    errors,
    fallback,
    showError,
    showFallback,
    dismissError,
    clearFallback,
    clearAll,
  } = useErrorHandling();

  return (
    <div>
      <div data-testid="error-count">{errors.length}</div>
      <div data-testid="has-fallback">{fallback ? "yes" : "no"}</div>
      <button
        onClick={() =>
          showError("critical", "Test Title", "Test message", "E_TEST")
        }
      >
        Show Critical
      </button>
      <button onClick={() => showError("warning", "Warning", "Warning message")}>
        Show Warning
      </button>
      <button onClick={() => showError("info", "Info", "Info message")}>
        Show Info
      </button>
      <button
        onClick={() => showFallback("LLM timeout", "rule_based_analysis")}
      >
        Show Fallback
      </button>
      <button onClick={() => dismissError(errors[0]?.id)}>Dismiss First</button>
      <button onClick={clearFallback}>Clear Fallback</button>
      <button onClick={clearAll}>Clear All</button>
    </div>
  );
}

describe("ErrorProvider and useErrorHandling", () => {
  it("throws error when useErrorHandling is used outside provider", () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    expect(() => {
      render(
        <div>
          <TestComponent />
        </div>
      );
    }).toThrow("useErrorHandling must be used within ErrorProvider");

    consoleSpy.mockRestore();
  });

  it("provides initial empty state", () => {
    render(
      <ErrorProvider>
        <TestComponent />
      </ErrorProvider>
    );

    expect(screen.getByTestId("error-count")).toHaveTextContent("0");
    expect(screen.getByTestId("has-fallback")).toHaveTextContent("no");
  });

  it("adds error when showError is called", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Critical"));

    expect(screen.getByTestId("error-count")).toHaveTextContent("1");
  });

  it("adds fallback when showFallback is called", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Fallback"));

    expect(screen.getByTestId("has-fallback")).toHaveTextContent("yes");
  });

  it("removes error when dismissError is called", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Warning"));
    expect(screen.getByTestId("error-count")).toHaveTextContent("1");

    await user.click(screen.getByText("Dismiss First"));
    expect(screen.getByTestId("error-count")).toHaveTextContent("0");
  });

  it("clears fallback when clearFallback is called", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Fallback"));
    expect(screen.getByTestId("has-fallback")).toHaveTextContent("yes");

    await user.click(screen.getByText("Clear Fallback"));
    expect(screen.getByTestId("has-fallback")).toHaveTextContent("no");
  });

  it("clears all errors and fallback when clearAll is called", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Warning"));
    await user.click(screen.getByText("Show Fallback"));
    expect(screen.getByTestId("error-count")).toHaveTextContent("1");
    expect(screen.getByTestId("has-fallback")).toHaveTextContent("yes");

    await user.click(screen.getByText("Clear All"));
    expect(screen.getByTestId("error-count")).toHaveTextContent("0");
    expect(screen.getByTestId("has-fallback")).toHaveTextContent("no");
  });
});

describe("ErrorModal", () => {
  const mockError: ErrorMessage = {
    id: "test-error-1",
    severity: "critical",
    title: "Critical Error",
    message: "Something went wrong",
    errorCode: "E_CRITICAL",
    timestamp: new Date(),
  };

  it("renders error title", () => {
    render(<ErrorModal error={mockError} onDismiss={() => {}} />);
    expect(screen.getByText("Critical Error")).toBeInTheDocument();
  });

  it("renders error message", () => {
    render(<ErrorModal error={mockError} onDismiss={() => {}} />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("renders error code when provided", () => {
    render(<ErrorModal error={mockError} onDismiss={() => {}} />);
    expect(screen.getByText(/Error code: E_CRITICAL/)).toBeInTheDocument();
  });

  it("does not render error code when not provided", () => {
    const errorWithoutCode = { ...mockError, errorCode: undefined };
    render(<ErrorModal error={errorWithoutCode} onDismiss={() => {}} />);
    expect(screen.queryByText(/Error code:/)).not.toBeInTheDocument();
  });

  it("calls onDismiss when Dismiss button is clicked", async () => {
    const user = userEvent.setup();
    const onDismiss = vi.fn();
    render(<ErrorModal error={mockError} onDismiss={onDismiss} />);

    await user.click(screen.getByText("Dismiss"));

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("calls onDismiss when backdrop is clicked", async () => {
    const user = userEvent.setup();
    const onDismiss = vi.fn();
    render(<ErrorModal error={mockError} onDismiss={onDismiss} />);

    // Click the backdrop (the div with aria-hidden)
    const backdrop = document.querySelector('[aria-hidden="true"]');
    await user.click(backdrop!);

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });
});

describe("WarningBadge", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const mockWarning: ErrorMessage = {
    id: "test-warning-1",
    severity: "warning",
    title: "Warning",
    message: "Something might be wrong",
    timestamp: new Date(),
    autoDismiss: true,
  };

  it("renders warning message", () => {
    render(<WarningBadge error={mockWarning} onDismiss={() => {}} />);
    expect(screen.getByText("Something might be wrong")).toBeInTheDocument();
  });

  it("calls onDismiss when close button is clicked", async () => {
    vi.useRealTimers(); // Use real timers for user interaction
    const user = userEvent.setup();
    const onDismiss = vi.fn();
    render(<WarningBadge error={mockWarning} onDismiss={onDismiss} />);

    const closeButton = screen.getByRole("button");
    await user.click(closeButton);

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("auto-dismisses after 5 seconds when autoDismiss is true", () => {
    const onDismiss = vi.fn();
    render(<WarningBadge error={mockWarning} onDismiss={onDismiss} />);

    expect(onDismiss).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("does not auto-dismiss when autoDismiss is false", () => {
    const onDismiss = vi.fn();
    const nonAutoDismissWarning = { ...mockWarning, autoDismiss: false };
    render(<WarningBadge error={nonAutoDismissWarning} onDismiss={onDismiss} />);

    act(() => {
      vi.advanceTimersByTime(10000);
    });

    expect(onDismiss).not.toHaveBeenCalled();
  });
});

describe("InfoToast", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const mockInfo: ErrorMessage = {
    id: "test-info-1",
    severity: "info",
    title: "Info",
    message: "Just letting you know",
    timestamp: new Date(),
  };

  it("renders info message", () => {
    render(<InfoToast error={mockInfo} onDismiss={() => {}} />);
    expect(screen.getByText("Just letting you know")).toBeInTheDocument();
  });

  it("auto-dismisses after 3 seconds", () => {
    const onDismiss = vi.fn();
    render(<InfoToast error={mockInfo} onDismiss={onDismiss} />);

    expect(onDismiss).not.toHaveBeenCalled();

    act(() => {
      vi.advanceTimersByTime(3000);
    });

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });
});

describe("FallbackBadge", () => {
  const mockFallback: FallbackNotification = {
    id: "test-fallback-1",
    reason: "LLM timeout",
    strategy: "rule_based_analysis",
    timestamp: new Date(),
  };

  it("renders 'Fallback Used' label", () => {
    render(<FallbackBadge notification={mockFallback} onDismiss={() => {}} />);
    expect(screen.getByText("Fallback Used")).toBeInTheDocument();
  });

  it("renders reason", () => {
    render(<FallbackBadge notification={mockFallback} onDismiss={() => {}} />);
    expect(screen.getByText(/Reason: LLM timeout/)).toBeInTheDocument();
  });

  it("renders strategy label for rule_based_analysis", () => {
    render(<FallbackBadge notification={mockFallback} onDismiss={() => {}} />);
    expect(screen.getByText(/Strategy: Rule-based analysis/)).toBeInTheDocument();
  });

  it("renders strategy label for priority_based_selection", () => {
    const notification = { ...mockFallback, strategy: "priority_based_selection" as const };
    render(<FallbackBadge notification={notification} onDismiss={() => {}} />);
    expect(screen.getByText(/Strategy: Priority-based selection/)).toBeInTheDocument();
  });

  it("renders strategy label for random_valid_move", () => {
    const notification = { ...mockFallback, strategy: "random_valid_move" as const };
    render(<FallbackBadge notification={notification} onDismiss={() => {}} />);
    expect(screen.getByText(/Strategy: Random valid move/)).toBeInTheDocument();
  });

  it("calls onDismiss when close button is clicked", async () => {
    const user = userEvent.setup();
    const onDismiss = vi.fn();
    render(<FallbackBadge notification={mockFallback} onDismiss={onDismiss} />);

    const closeButton = screen.getByRole("button");
    await user.click(closeButton);

    expect(onDismiss).toHaveBeenCalledTimes(1);
  });
});

describe("ErrorDisplay", () => {
  it("renders critical error as modal", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <ErrorDisplay />
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Critical"));

    expect(screen.getByText("Test Title")).toBeInTheDocument();
    expect(screen.getByText("Test message")).toBeInTheDocument();
  });

  it("renders warning as badge", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <ErrorDisplay />
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Warning"));

    expect(screen.getByText("Warning message")).toBeInTheDocument();
  });

  it("renders info as toast", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <ErrorDisplay />
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Info"));

    expect(screen.getByText("Info message")).toBeInTheDocument();
  });

  it("renders fallback notification", async () => {
    const user = userEvent.setup();
    render(
      <ErrorProvider>
        <ErrorDisplay />
        <TestComponent />
      </ErrorProvider>
    );

    await user.click(screen.getByText("Show Fallback"));

    expect(screen.getByText("Fallback Used")).toBeInTheDocument();
    expect(screen.getByText(/Reason: LLM timeout/)).toBeInTheDocument();
  });
});
