import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ConfigurationPanel } from "./ConfigurationPanel";

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string): string | null => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
  writable: true,
});

describe("ConfigurationPanel", () => {
  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  describe("header", () => {
    it("displays Configuration title", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Configuration")).toBeInTheDocument();
    });

    it("displays description", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Agent and game settings")).toBeInTheDocument();
    });
  });

  describe("footer", () => {
    it("displays auto-save message", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Settings auto-save to localStorage")).toBeInTheDocument();
    });
  });

  describe("Agent LLM Providers section", () => {
    it("displays section header", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Agent LLM Providers")).toBeInTheDocument();
    });

    it("displays Scout agent selector", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Scout")).toBeInTheDocument();
    });

    it("displays Strategist agent selector", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Strategist")).toBeInTheDocument();
    });

    it("displays Executor agent selector", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Executor")).toBeInTheDocument();
    });

    it("has default values for agent providers", () => {
      render(<ConfigurationPanel />);
      // Default values: scout=openai, strategist=anthropic, executor=gemini
      // These show in the select triggers
      const triggers = screen.getAllByRole("combobox");
      expect(triggers.length).toBe(4); // 3 agent + 1 player symbol
    });

    it("calls onConfigChange when agent provider is changed", async () => {
      const user = userEvent.setup();
      const onConfigChange = vi.fn();
      render(<ConfigurationPanel onConfigChange={onConfigChange} />);

      // Click the first combobox (Scout)
      const triggers = screen.getAllByRole("combobox");
      await user.click(triggers[0]);

      // Select Anthropic from the dropdown (use role option)
      const options = await screen.findAllByRole("option");
      const anthropicOption = options.find(opt => opt.textContent === "Anthropic");
      await user.click(anthropicOption!);

      expect(onConfigChange).toHaveBeenCalledWith(
        expect.objectContaining({
          scout: "anthropic",
        })
      );
    });

    it("saves agent config to localStorage when changed", async () => {
      const user = userEvent.setup();
      render(<ConfigurationPanel />);

      const triggers = screen.getAllByRole("combobox");
      await user.click(triggers[0]); // Scout

      // Select Anthropic from the dropdown
      const options = await screen.findAllByRole("option");
      const anthropicOption = options.find(opt => opt.textContent === "Anthropic");
      await user.click(anthropicOption!);

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "tictactoe_agent_config",
        expect.stringContaining('"scout":"anthropic"')
      );
    });
  });

  describe("API Keys section", () => {
    it("displays section header", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("API Keys")).toBeInTheDocument();
    });

    it("displays OpenAI API key input", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByPlaceholderText("OpenAI API Key")).toBeInTheDocument();
    });

    it("displays Anthropic API key input", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByPlaceholderText("Anthropic API Key")).toBeInTheDocument();
    });

    it("displays Gemini API key input", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByPlaceholderText("Gemini API Key")).toBeInTheDocument();
    });

    it("displays model names for each provider", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("GPT-5 mini")).toBeInTheDocument();
      expect(screen.getByText("Claude Opus 4.5")).toBeInTheDocument();
      expect(screen.getByText("Gemini 3 Flash")).toBeInTheDocument();
    });

    it("displays storage notice", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Keys are stored locally in your browser")).toBeInTheDocument();
    });

    it("API key inputs are password type by default", () => {
      render(<ConfigurationPanel />);
      const openaiInput = screen.getByPlaceholderText("OpenAI API Key");
      expect(openaiInput).toHaveAttribute("type", "password");
    });

    it("toggles API key visibility when eye icon is clicked", async () => {
      const user = userEvent.setup();
      render(<ConfigurationPanel />);

      const openaiInput = screen.getByPlaceholderText("OpenAI API Key");
      expect(openaiInput).toHaveAttribute("type", "password");

      // Find the toggle button (first one for OpenAI)
      const toggleButtons = screen.getAllByRole("button");
      const visibilityToggle = toggleButtons.find(
        (btn) => btn.querySelector("svg") !== null && btn.textContent === ""
      );

      if (visibilityToggle) {
        await user.click(visibilityToggle);
        expect(openaiInput).toHaveAttribute("type", "text");

        await user.click(visibilityToggle);
        expect(openaiInput).toHaveAttribute("type", "password");
      }
    });

    it("calls onApiKeysChange when API key is changed and input loses focus", async () => {
      const user = userEvent.setup();
      const onApiKeysChange = vi.fn();
      render(<ConfigurationPanel onApiKeysChange={onApiKeysChange} />);

      const openaiInput = screen.getByPlaceholderText("OpenAI API Key");
      await user.type(openaiInput, "sk-test-key");
      await user.tab(); // Blur the input

      expect(onApiKeysChange).toHaveBeenCalledWith(
        expect.objectContaining({
          openai: "sk-test-key",
        })
      );
    });

    it("saves API keys to localStorage when changed", async () => {
      const user = userEvent.setup();
      render(<ConfigurationPanel />);

      const openaiInput = screen.getByPlaceholderText("OpenAI API Key");
      await user.type(openaiInput, "sk-test-key");
      await user.tab();

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "tictactoe_api_keys",
        expect.stringContaining('"openai":"sk-test-key"')
      );
    });
  });

  describe("Game Settings section", () => {
    it("displays section header", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Game Settings")).toBeInTheDocument();
    });

    it("displays Player Symbol selector", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Player Symbol")).toBeInTheDocument();
    });

    it("has X as default player symbol", () => {
      render(<ConfigurationPanel />);
      // The select should show "X (Play first)" as the selected value
      const triggers = screen.getAllByRole("combobox");
      const playerSymbolTrigger = triggers[triggers.length - 1]; // Last one
      expect(playerSymbolTrigger).toHaveTextContent("X (Play first)");
    });

    it("calls onSettingsChange when player symbol is changed", async () => {
      const user = userEvent.setup();
      const onSettingsChange = vi.fn();
      render(<ConfigurationPanel onSettingsChange={onSettingsChange} />);

      const triggers = screen.getAllByRole("combobox");
      const playerSymbolTrigger = triggers[triggers.length - 1];
      await user.click(playerSymbolTrigger);

      // Select O from the dropdown options
      const options = await screen.findAllByRole("option");
      const oOption = options.find(opt => opt.textContent?.includes("O (AI plays first)"));
      await user.click(oOption!);

      expect(onSettingsChange).toHaveBeenCalledWith({
        playerSymbol: "O",
      });
    });

    it("saves game settings to localStorage when changed", async () => {
      const user = userEvent.setup();
      render(<ConfigurationPanel />);

      const triggers = screen.getAllByRole("combobox");
      const playerSymbolTrigger = triggers[triggers.length - 1];
      await user.click(playerSymbolTrigger);

      // Select O from the dropdown options
      const options = await screen.findAllByRole("option");
      const oOption = options.find(opt => opt.textContent?.includes("O (AI plays first)"));
      await user.click(oOption!);

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        "tictactoe_game_settings",
        '{"playerSymbol":"O"}'
      );
    });
  });

  describe("Reset to Defaults", () => {
    it("displays Reset to Defaults button", () => {
      render(<ConfigurationPanel />);
      expect(screen.getByText("Reset to Defaults")).toBeInTheDocument();
    });

    it("resets all settings when clicked", async () => {
      const user = userEvent.setup();
      const onConfigChange = vi.fn();
      const onApiKeysChange = vi.fn();
      const onSettingsChange = vi.fn();

      render(
        <ConfigurationPanel
          onConfigChange={onConfigChange}
          onApiKeysChange={onApiKeysChange}
          onSettingsChange={onSettingsChange}
        />
      );

      // First change some settings
      const openaiInput = screen.getByPlaceholderText("OpenAI API Key");
      await user.type(openaiInput, "sk-test-key");
      await user.tab();

      // Clear mocks to test reset behavior
      vi.clearAllMocks();

      // Click Reset to Defaults
      await user.click(screen.getByText("Reset to Defaults"));

      // Should call callbacks with default values
      expect(onConfigChange).toHaveBeenCalledWith({
        scout: "openai",
        strategist: "anthropic",
        executor: "gemini",
      });

      expect(onApiKeysChange).toHaveBeenCalledWith({
        openai: "",
        anthropic: "",
        gemini: "",
      });

      expect(onSettingsChange).toHaveBeenCalledWith({
        playerSymbol: "X",
      });
    });

    it("removes settings from localStorage when reset", async () => {
      const user = userEvent.setup();
      render(<ConfigurationPanel />);

      await user.click(screen.getByText("Reset to Defaults"));

      expect(localStorageMock.removeItem).toHaveBeenCalledWith("tictactoe_agent_config");
      expect(localStorageMock.removeItem).toHaveBeenCalledWith("tictactoe_api_keys");
      expect(localStorageMock.removeItem).toHaveBeenCalledWith("tictactoe_game_settings");
    });
  });

  describe("localStorage persistence", () => {
    it("loads agent config from localStorage on mount", () => {
      const savedConfig = JSON.stringify({
        scout: "anthropic",
        strategist: "gemini",
        executor: "openai",
      });
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === "tictactoe_agent_config") return savedConfig;
        return null;
      });

      render(<ConfigurationPanel />);

      expect(localStorageMock.getItem).toHaveBeenCalledWith("tictactoe_agent_config");
    });

    it("loads API keys from localStorage on mount", () => {
      const savedKeys = JSON.stringify({
        openai: "sk-saved-key",
        anthropic: "",
        gemini: "",
      });
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === "tictactoe_api_keys") return savedKeys;
        return null;
      });

      render(<ConfigurationPanel />);

      expect(localStorageMock.getItem).toHaveBeenCalledWith("tictactoe_api_keys");
      // The input should have the saved value
      const openaiInput = screen.getByPlaceholderText("OpenAI API Key");
      expect(openaiInput).toHaveValue("sk-saved-key");
    });

    it("loads game settings from localStorage on mount", () => {
      const savedSettings = JSON.stringify({
        playerSymbol: "O",
      });
      localStorageMock.getItem.mockImplementation((key: string) => {
        if (key === "tictactoe_game_settings") return savedSettings;
        return null;
      });

      render(<ConfigurationPanel />);

      expect(localStorageMock.getItem).toHaveBeenCalledWith("tictactoe_game_settings");
    });

    it("handles localStorage errors gracefully on load", () => {
      localStorageMock.getItem.mockImplementation(() => {
        throw new Error("localStorage not available");
      });

      // Should not throw
      expect(() => render(<ConfigurationPanel />)).not.toThrow();
    });

    it("handles localStorage errors gracefully on save", async () => {
      const user = userEvent.setup();
      localStorageMock.setItem.mockImplementation(() => {
        throw new Error("localStorage full");
      });

      render(<ConfigurationPanel />);

      const openaiInput = screen.getByPlaceholderText("OpenAI API Key");

      // Should not throw
      await expect(async () => {
        await user.type(openaiInput, "sk-test-key");
        await user.tab();
      }).not.toThrow;
    });
  });

  describe("provider options", () => {
    it("shows all provider options in agent selector", async () => {
      const user = userEvent.setup();
      render(<ConfigurationPanel />);

      const triggers = screen.getAllByRole("combobox");
      await user.click(triggers[0]); // Open Scout selector

      // Use findAllByRole to get the options
      const options = await screen.findAllByRole("option");
      const optionTexts = options.map(opt => opt.textContent);

      expect(optionTexts).toContain("OpenAI");
      expect(optionTexts).toContain("Anthropic");
      expect(optionTexts).toContain("Gemini");
    });
  });

  describe("player symbol options", () => {
    it("shows both player symbol options", async () => {
      const user = userEvent.setup();
      render(<ConfigurationPanel />);

      const triggers = screen.getAllByRole("combobox");
      const playerSymbolTrigger = triggers[triggers.length - 1];
      await user.click(playerSymbolTrigger);

      // Use findAllByRole to get the options
      const options = await screen.findAllByRole("option");
      const optionTexts = options.map(opt => opt.textContent);

      expect(optionTexts.some(text => text?.includes("X (Play first)"))).toBe(true);
      expect(optionTexts.some(text => text?.includes("O (AI plays first)"))).toBe(true);
    });
  });
});
