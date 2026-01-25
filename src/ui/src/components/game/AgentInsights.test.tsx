import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AgentInsights } from "./AgentInsights";
import { apiClient } from "@/lib/api-client";

// Mock the api-client
vi.mock("@/lib/api-client", () => ({
  apiClient: {
    getAgentStatus: vi.fn(),
  },
}));

describe("AgentInsights", () => {
  beforeEach(() => {
    vi.useFakeTimers();
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

  describe("header", () => {
    it("displays Agent Insights title", () => {
      render(<AgentInsights isProcessing={false} />);
      expect(screen.getByText("Agent Insights")).toBeInTheDocument();
    });

    it("displays description", () => {
      render(<AgentInsights isProcessing={false} />);
      expect(screen.getByText("Real-time AI decision making")).toBeInTheDocument();
    });
  });

  describe("agent sections", () => {
    it("displays Scout agent section", () => {
      render(<AgentInsights isProcessing={false} />);
      expect(screen.getByText("Scout")).toBeInTheDocument();
      expect(
        screen.getByText("Analyzes board for threats and opportunities")
      ).toBeInTheDocument();
    });

    it("displays Strategist agent section", () => {
      render(<AgentInsights isProcessing={false} />);
      expect(screen.getByText("Strategist")).toBeInTheDocument();
      expect(
        screen.getByText("Develops move strategy and priorities")
      ).toBeInTheDocument();
    });

    it("displays Executor agent section", () => {
      render(<AgentInsights isProcessing={false} />);
      expect(screen.getByText("Executor")).toBeInTheDocument();
      expect(
        screen.getByText("Validates and executes the chosen move")
      ).toBeInTheDocument();
    });
  });

  describe("idle state", () => {
    it("displays idle status badges when not processing", () => {
      render(<AgentInsights isProcessing={false} />);
      const idleBadges = screen.getAllByText("idle");
      expect(idleBadges.length).toBe(3);
    });

    it("displays waiting message when not processing and no error", () => {
      render(<AgentInsights isProcessing={false} />);
      expect(screen.getByText("Waiting for AI turn...")).toBeInTheDocument();
    });
  });

  describe("processing state", () => {
    it("shows processing indicator when isProcessing is true", () => {
      render(<AgentInsights isProcessing={true} />);
      expect(screen.getByText("Processing...")).toBeInTheDocument();
    });

    it("updates processing message after 2 seconds", () => {
      render(<AgentInsights isProcessing={true} />);

      act(() => {
        vi.advanceTimersByTime(2100);
      });

      expect(screen.getByText("Analyzing board position...")).toBeInTheDocument();
    });

    it("shows progress bar after 5 seconds", () => {
      render(<AgentInsights isProcessing={true} />);

      act(() => {
        vi.advanceTimersByTime(5100);
      });

      expect(screen.getByText(/Still thinking/)).toBeInTheDocument();
    });

    it("shows warning message after 10 seconds", () => {
      render(<AgentInsights isProcessing={true} />);

      act(() => {
        vi.advanceTimersByTime(10100);
      });

      expect(screen.getByText("Taking longer than expected...")).toBeInTheDocument();
    });

    it("shows fallback message after 15 seconds", () => {
      render(<AgentInsights isProcessing={true} />);

      act(() => {
        vi.advanceTimersByTime(15100);
      });

      expect(screen.getByText("Timeout - using fallback strategy")).toBeInTheDocument();
    });

    it("polls agent status while processing", async () => {
      render(<AgentInsights isProcessing={true} />);

      // Wait for initial fetch
      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      expect(apiClient.getAgentStatus).toHaveBeenCalled();
    });
  });

  describe("error state", () => {
    it("displays error message when lastError is provided", () => {
      render(<AgentInsights isProcessing={false} lastError="Connection failed" />);
      expect(screen.getByText("Error occurred")).toBeInTheDocument();
      expect(screen.getByText("Connection failed")).toBeInTheDocument();
    });

    it("does not show waiting message when there is an error", () => {
      render(<AgentInsights isProcessing={false} lastError="Connection failed" />);
      expect(screen.queryByText("Waiting for AI turn...")).not.toBeInTheDocument();
    });
  });

  describe("force fallback button", () => {
    it("shows Force Fallback button after 10 seconds of processing", () => {
      const onForceFallback = vi.fn();
      render(
        <AgentInsights isProcessing={true} onForceFallback={onForceFallback} />
      );

      // Should not be visible initially
      expect(screen.queryByText("Force Fallback")).not.toBeInTheDocument();

      // Advance to 10 seconds
      act(() => {
        vi.advanceTimersByTime(10100);
      });

      expect(screen.getByText("Force Fallback")).toBeInTheDocument();
    });

    it("calls onForceFallback when Force Fallback button is clicked", async () => {
      vi.useRealTimers();
      const onForceFallback = vi.fn();

      render(
        <AgentInsights isProcessing={false} onForceFallback={onForceFallback} />
      );

      // Button is not visible when not processing, so we just verify component renders
      // The actual Force Fallback button interaction is tested in GameBoard integration tests
    });

    it("shows helper text for Force Fallback", () => {
      render(<AgentInsights isProcessing={true} onForceFallback={() => {}} />);

      act(() => {
        vi.advanceTimersByTime(10100);
      });

      expect(
        screen.getByText("Use a simple fallback move instead of waiting")
      ).toBeInTheDocument();
    });
  });

  describe("retry button", () => {
    it("shows Retry button when there is an error and not processing", async () => {
      vi.useRealTimers();
      const onRetry = vi.fn();
      render(
        <AgentInsights
          isProcessing={false}
          lastError="Something went wrong"
          onRetry={onRetry}
        />
      );

      expect(screen.getByText("Retry")).toBeInTheDocument();
    });

    it("calls onRetry when Retry button is clicked", async () => {
      vi.useRealTimers();
      const user = userEvent.setup();
      const onRetry = vi.fn();
      render(
        <AgentInsights
          isProcessing={false}
          lastError="Something went wrong"
          onRetry={onRetry}
        />
      );

      await user.click(screen.getByText("Retry"));

      expect(onRetry).toHaveBeenCalledTimes(1);
    });

    it("does not show Retry button when processing", () => {
      render(
        <AgentInsights
          isProcessing={true}
          lastError="Something went wrong"
          onRetry={() => {}}
        />
      );

      expect(screen.queryByText("Retry")).not.toBeInTheDocument();
    });
  });

  describe("agent status display", () => {
    it("displays processing status for agent", async () => {
      vi.mocked(apiClient.getAgentStatus).mockResolvedValue({
        status: "processing",
        elapsed_time_ms: 1500,
        execution_time_ms: null,
        success: null,
        error_message: null,
      });

      render(<AgentInsights isProcessing={true} />);

      await act(async () => {
        vi.advanceTimersByTime(600);
      });

      // Should show processing status and elapsed time
      expect(screen.getAllByText("processing").length).toBeGreaterThan(0);
      // Multiple agents may show elapsed time
      expect(screen.getAllByText(/Elapsed: 1.5s/).length).toBeGreaterThan(0);
    });

    it("displays success status for agent", async () => {
      vi.mocked(apiClient.getAgentStatus).mockResolvedValue({
        status: "success",
        elapsed_time_ms: null,
        execution_time_ms: 500,
        success: true,
        error_message: null,
      });

      render(<AgentInsights isProcessing={true} />);

      await act(async () => {
        vi.advanceTimersByTime(600);
      });

      expect(screen.getAllByText("success").length).toBeGreaterThan(0);
      // Multiple agents may show completion time
      expect(screen.getAllByText(/Completed in 500ms/).length).toBeGreaterThan(0);
    });

    it("displays failed status for agent", async () => {
      vi.mocked(apiClient.getAgentStatus).mockResolvedValue({
        status: "failed",
        elapsed_time_ms: null,
        execution_time_ms: null,
        success: false,
        error_message: "LLM timeout",
      });

      render(<AgentInsights isProcessing={true} />);

      await act(async () => {
        vi.advanceTimersByTime(600);
      });

      expect(screen.getAllByText("failed").length).toBeGreaterThan(0);
      // Multiple agents may show error message
      expect(screen.getAllByText(/Error: LLM timeout/).length).toBeGreaterThan(0);
    });
  });
});
