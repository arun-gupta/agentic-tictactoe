"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Types for configuration
export type LLMProvider = "openai" | "anthropic" | "gemini";
export type PlayerSymbol = "X" | "O";

export interface AgentConfig {
  scout: LLMProvider;
  strategist: LLMProvider;
  executor: LLMProvider;
}

export interface ApiKeys {
  openai: string;
  anthropic: string;
  gemini: string;
}

export interface GameSettings {
  playerSymbol: PlayerSymbol;
}

interface ConfigurationPanelProps {
  onConfigChange?: (config: AgentConfig) => void;
  onApiKeysChange?: (keys: ApiKeys) => void;
  onSettingsChange?: (settings: GameSettings) => void;
}

// Provider display info
const PROVIDERS: { id: LLMProvider; name: string; model: string }[] = [
  { id: "openai", name: "OpenAI", model: "GPT-5 mini" },
  { id: "anthropic", name: "Anthropic", model: "Claude Opus 4.5" },
  { id: "gemini", name: "Gemini", model: "Gemini 3 Flash" },
];

// LocalStorage keys
const STORAGE_KEYS = {
  agentConfig: "tictactoe_agent_config",
  apiKeys: "tictactoe_api_keys",
  gameSettings: "tictactoe_game_settings",
};

/**
 * Agent LLM Selection Component
 */
function AgentLLMSelect({
  agentName,
  value,
  onChange,
}: {
  agentName: string;
  value: LLMProvider;
  onChange: (value: LLMProvider) => void;
}) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-zinc-700 font-mono">
        {agentName}
      </label>
      <Select value={value} onValueChange={(v) => onChange(v as LLMProvider)}>
        <SelectTrigger className="w-full h-9 text-sm font-mono">
          <SelectValue placeholder="Select provider" />
        </SelectTrigger>
        <SelectContent>
          {PROVIDERS.map((provider) => (
            <SelectItem
              key={provider.id}
              value={provider.id}
              className="text-sm font-mono"
            >
              {provider.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

/**
 * API Key Input Component
 */
function ApiKeyInput({
  provider,
  model,
  value,
  onChange,
}: {
  provider: string;
  model: string;
  value: string;
  onChange: (value: string) => void;
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [localValue, setLocalValue] = useState(value);

  // Sync with parent value
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleBlur = () => {
    onChange(localValue);
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-baseline gap-2">
        <label className="text-xs font-medium text-zinc-700 font-mono">
          {provider}
        </label>
        <span className="text-xs text-zinc-400 font-mono">{model}</span>
      </div>
      <div className="relative">
        <Input
          type={isVisible ? "text" : "password"}
          value={localValue}
          onChange={(e) => setLocalValue(e.target.value)}
          onBlur={handleBlur}
          placeholder={`${provider} API Key`}
          className="h-9 text-sm font-mono pr-10"
        />
        <button
          type="button"
          onClick={() => setIsVisible(!isVisible)}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 transition-colors"
        >
          {isVisible ? (
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
              />
            </svg>
          ) : (
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

/**
 * Configuration Panel
 *
 * Provides settings for:
 * - Agent LLM provider selection (Scout, Strategist, Executor)
 * - API key inputs for each provider
 * - Game settings (player symbol)
 */
export function ConfigurationPanel({
  onConfigChange,
  onApiKeysChange,
  onSettingsChange,
}: ConfigurationPanelProps) {
  // Agent configuration state
  const [agentConfig, setAgentConfig] = useState<AgentConfig>({
    scout: "openai",
    strategist: "anthropic",
    executor: "gemini",
  });

  // API keys state
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: "",
    anthropic: "",
    gemini: "",
  });

  // Game settings state
  const [gameSettings, setGameSettings] = useState<GameSettings>({
    playerSymbol: "X",
  });

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const savedConfig = localStorage.getItem(STORAGE_KEYS.agentConfig);
      if (savedConfig) {
        // eslint-disable-next-line react-hooks/set-state-in-effect -- Initialize from localStorage
        setAgentConfig(JSON.parse(savedConfig));
      }

      const savedKeys = localStorage.getItem(STORAGE_KEYS.apiKeys);
      if (savedKeys) {
        setApiKeys(JSON.parse(savedKeys));
      }

      const savedSettings = localStorage.getItem(STORAGE_KEYS.gameSettings);
      if (savedSettings) {
        setGameSettings(JSON.parse(savedSettings));
      }
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  // Save agent config to localStorage
  const handleAgentConfigChange = useCallback(
    (agent: keyof AgentConfig, provider: LLMProvider) => {
      const newConfig = { ...agentConfig, [agent]: provider };
      setAgentConfig(newConfig);
      try {
        localStorage.setItem(STORAGE_KEYS.agentConfig, JSON.stringify(newConfig));
      } catch {
        // Ignore localStorage errors
      }
      onConfigChange?.(newConfig);
    },
    [agentConfig, onConfigChange]
  );

  // Save API keys to localStorage
  const handleApiKeyChange = useCallback(
    (provider: keyof ApiKeys, value: string) => {
      const newKeys = { ...apiKeys, [provider]: value };
      setApiKeys(newKeys);
      try {
        localStorage.setItem(STORAGE_KEYS.apiKeys, JSON.stringify(newKeys));
      } catch {
        // Ignore localStorage errors
      }
      onApiKeysChange?.(newKeys);
    },
    [apiKeys, onApiKeysChange]
  );

  // Save game settings to localStorage
  const handleSettingsChange = useCallback(
    (symbol: PlayerSymbol) => {
      const newSettings = { playerSymbol: symbol };
      setGameSettings(newSettings);
      try {
        localStorage.setItem(STORAGE_KEYS.gameSettings, JSON.stringify(newSettings));
      } catch {
        // Ignore localStorage errors
      }
      onSettingsChange?.(newSettings);
    },
    [onSettingsChange]
  );

  // Clear all settings
  const handleClearSettings = () => {
    const defaultConfig: AgentConfig = {
      scout: "openai",
      strategist: "anthropic",
      executor: "gemini",
    };
    const defaultKeys: ApiKeys = {
      openai: "",
      anthropic: "",
      gemini: "",
    };
    const defaultSettings: GameSettings = {
      playerSymbol: "X",
    };

    setAgentConfig(defaultConfig);
    setApiKeys(defaultKeys);
    setGameSettings(defaultSettings);

    try {
      localStorage.removeItem(STORAGE_KEYS.agentConfig);
      localStorage.removeItem(STORAGE_KEYS.apiKeys);
      localStorage.removeItem(STORAGE_KEYS.gameSettings);
    } catch {
      // Ignore localStorage errors
    }

    onConfigChange?.(defaultConfig);
    onApiKeysChange?.(defaultKeys);
    onSettingsChange?.(defaultSettings);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-3 py-2 border-b border-zinc-200 bg-zinc-50">
        <h3 className="text-sm font-medium text-zinc-700 font-mono">
          Configuration
        </h3>
        <p className="text-xs text-zinc-400 mt-0.5">
          Agent and game settings
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3 space-y-6">
        {/* Agent LLM Selection Section */}
        <section>
          <h4 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3">
            Agent LLM Providers
          </h4>
          <div className="space-y-3">
            <AgentLLMSelect
              agentName="Scout"
              value={agentConfig.scout}
              onChange={(v) => handleAgentConfigChange("scout", v)}
            />
            <AgentLLMSelect
              agentName="Strategist"
              value={agentConfig.strategist}
              onChange={(v) => handleAgentConfigChange("strategist", v)}
            />
            <AgentLLMSelect
              agentName="Executor"
              value={agentConfig.executor}
              onChange={(v) => handleAgentConfigChange("executor", v)}
            />
          </div>
        </section>

        {/* API Keys Section */}
        <section>
          <h4 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3">
            API Keys
          </h4>
          <div className="space-y-3">
            {PROVIDERS.map((provider) => (
              <ApiKeyInput
                key={provider.id}
                provider={provider.name}
                model={provider.model}
                value={apiKeys[provider.id]}
                onChange={(v) => handleApiKeyChange(provider.id, v)}
              />
            ))}
          </div>
          <p className="text-xs text-zinc-400 mt-2 font-mono">
            Keys are stored locally in your browser
          </p>
        </section>

        {/* Game Settings Section */}
        <section>
          <h4 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3">
            Game Settings
          </h4>
          <div className="space-y-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-700 font-mono">
                Player Symbol
              </label>
              <Select
                value={gameSettings.playerSymbol}
                onValueChange={(v) => handleSettingsChange(v as PlayerSymbol)}
              >
                <SelectTrigger className="w-full h-9 text-sm font-mono">
                  <SelectValue placeholder="Select symbol" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="X" className="text-sm font-mono">
                    X (Play first)
                  </SelectItem>
                  <SelectItem value="O" className="text-sm font-mono">
                    O (AI plays first)
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </section>

        {/* Actions */}
        <section className="pt-3 border-t border-zinc-200">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleClearSettings}
            className="w-full text-xs font-mono"
          >
            Reset to Defaults
          </Button>
        </section>
      </div>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-zinc-200 bg-zinc-50">
        <p className="text-xs text-zinc-400 font-mono text-center">
          Settings auto-save to localStorage
        </p>
      </div>
    </div>
  );
}
