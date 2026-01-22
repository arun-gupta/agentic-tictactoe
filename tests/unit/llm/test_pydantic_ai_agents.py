"""Tests for Pydantic AI agent integration."""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.domain.agent_models import BoardAnalysis, Strategy
from src.llm.pydantic_ai_agents import create_scout_agent, create_strategist_agent


@pytest.fixture(autouse=True)
def setup_env_vars() -> None:
    """Set up environment variables for tests."""
    # Set dummy API keys for tests
    os.environ["OPENAI_API_KEY"] = "test-openai-key"
    os.environ["ANTHROPIC_API_KEY"] = "test-anthropic-key"
    os.environ["GOOGLE_API_KEY"] = "test-google-key"
    yield
    # Cleanup
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]:
        if key in os.environ:
            del os.environ[key]


class TestPydanticAIScoutAgent:
    """Test Pydantic AI Scout Agent creation."""

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    @patch("src.llm.pydantic_ai_agents.OpenAIModel")
    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_create_scout_agent_with_openai(
        self, mock_config: MagicMock, mock_openai_model: MagicMock, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_scout_agent creates Agent with BoardAnalysis response model for OpenAI."""
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_supported_models.return_value = {"gpt-5.2"}
        mock_config.return_value = mock_config_instance
        mock_get_api_key.return_value = "test-openai-key"
        mock_model_instance = MagicMock()
        mock_openai_model.return_value = mock_model_instance

        # Create agent
        agent = create_scout_agent(provider="openai", model="gpt-5.2")

        # Verify
        assert agent is not None
        assert agent.output_type == BoardAnalysis
        mock_openai_model.assert_called_once_with("gpt-5.2")
        mock_get_api_key.assert_called_once_with("OPENAI_API_KEY")

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    @patch("src.llm.pydantic_ai_agents.AnthropicModel")
    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_create_scout_agent_with_anthropic(
        self, mock_config: MagicMock, mock_anthropic_model: MagicMock, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_scout_agent creates Agent with BoardAnalysis response model for Anthropic."""
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_supported_models.return_value = {"claude-haiku-4-5-20251001"}
        mock_config.return_value = mock_config_instance
        mock_get_api_key.return_value = "test-anthropic-key"
        mock_model_instance = MagicMock()
        mock_anthropic_model.return_value = mock_model_instance

        # Create agent
        agent = create_scout_agent(provider="anthropic", model="claude-haiku-4-5-20251001")

        # Verify
        assert agent is not None
        assert agent.output_type == BoardAnalysis
        mock_anthropic_model.assert_called_once_with("claude-haiku-4-5-20251001")
        mock_get_api_key.assert_called_once_with("ANTHROPIC_API_KEY")

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    @patch("src.llm.pydantic_ai_agents.GoogleModel")
    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_create_scout_agent_with_gemini(
        self, mock_config: MagicMock, mock_google_model: MagicMock, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_scout_agent creates Agent with BoardAnalysis response model for Gemini."""
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_supported_models.return_value = {"gemini-3-flash-preview"}
        mock_config.return_value = mock_config_instance
        mock_get_api_key.return_value = "test-google-key"
        mock_model_instance = MagicMock()
        mock_google_model.return_value = mock_model_instance

        # Create agent
        agent = create_scout_agent(provider="gemini", model="gemini-3-flash-preview")

        # Verify
        assert agent is not None
        assert agent.output_type == BoardAnalysis
        mock_google_model.assert_called_once_with("gemini-3-flash-preview")
        mock_get_api_key.assert_called_once_with("GOOGLE_API_KEY")

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    @patch("src.llm.pydantic_ai_agents.OpenAIModel")
    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_create_scout_agent_auto_selects_provider(
        self, mock_config: MagicMock, mock_openai_model: MagicMock, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_scout_agent auto-selects first available provider when not specified."""
        # Setup mocks
        mock_config_instance = MagicMock()
        # Mock get_supported_models to return models for openai (called twice: once in loop, once for model selection)
        mock_config_instance.get_supported_models.return_value = {"gpt-5.2"}
        mock_config.return_value = mock_config_instance
        mock_get_api_key.return_value = "test-openai-key"
        mock_model_instance = MagicMock()
        mock_openai_model.return_value = mock_model_instance

        # Create agent without specifying provider
        agent = create_scout_agent()

        # Verify
        assert agent is not None
        assert agent.output_type == BoardAnalysis
        # Should have tried openai first (called at least once for openai)
        assert mock_config_instance.get_supported_models.call_count >= 1
        mock_openai_model.assert_called_once_with("gpt-5.2")

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    def test_create_scout_agent_raises_error_when_api_key_missing(
        self, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_scout_agent raises ValueError when API key is missing."""
        mock_get_api_key.return_value = None

        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            create_scout_agent(provider="openai", model="gpt-5.2")

    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_create_scout_agent_raises_error_when_provider_not_configured(
        self, mock_config: MagicMock
    ) -> None:
        """Test that create_scout_agent raises ValueError when no provider is configured."""
        mock_config_instance = MagicMock()
        mock_config_instance.get_supported_models.side_effect = ValueError("Provider not found")
        mock_config.return_value = mock_config_instance

        with pytest.raises(ValueError, match="No LLM provider configured"):
            create_scout_agent()


class TestPydanticAIStrategistAgent:
    """Test Pydantic AI Strategist Agent creation."""

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    @patch("src.llm.pydantic_ai_agents.OpenAIModel")
    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_create_strategist_agent_with_openai(
        self, mock_config: MagicMock, mock_openai_model: MagicMock, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_strategist_agent creates Agent with Strategy response model for OpenAI."""
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_supported_models.return_value = {"gpt-5.2"}
        mock_config.return_value = mock_config_instance
        mock_get_api_key.return_value = "test-openai-key"
        mock_model_instance = MagicMock()
        mock_openai_model.return_value = mock_model_instance

        # Create agent
        agent = create_strategist_agent(provider="openai", model="gpt-5.2")

        # Verify
        assert agent is not None
        assert agent.output_type == Strategy
        mock_openai_model.assert_called_once_with("gpt-5.2")
        mock_get_api_key.assert_called_once_with("OPENAI_API_KEY")

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    @patch("src.llm.pydantic_ai_agents.AnthropicModel")
    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_create_strategist_agent_with_anthropic(
        self, mock_config: MagicMock, mock_anthropic_model: MagicMock, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_strategist_agent creates Agent with Strategy response model for Anthropic."""
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_supported_models.return_value = {"claude-haiku-4-5-20251001"}
        mock_config.return_value = mock_config_instance
        mock_get_api_key.return_value = "test-anthropic-key"
        mock_model_instance = MagicMock()
        mock_anthropic_model.return_value = mock_model_instance

        # Create agent
        agent = create_strategist_agent(provider="anthropic", model="claude-haiku-4-5-20251001")

        # Verify
        assert agent is not None
        assert agent.output_type == Strategy
        mock_anthropic_model.assert_called_once_with("claude-haiku-4-5-20251001")
        mock_get_api_key.assert_called_once_with("ANTHROPIC_API_KEY")

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    @patch("src.llm.pydantic_ai_agents.GoogleModel")
    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_create_strategist_agent_with_gemini(
        self, mock_config: MagicMock, mock_google_model: MagicMock, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_strategist_agent creates Agent with Strategy response model for Gemini."""
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_supported_models.return_value = {"gemini-3-flash-preview"}
        mock_config.return_value = mock_config_instance
        mock_get_api_key.return_value = "test-google-key"
        mock_model_instance = MagicMock()
        mock_google_model.return_value = mock_model_instance

        # Create agent
        agent = create_strategist_agent(provider="gemini", model="gemini-3-flash-preview")

        # Verify
        assert agent is not None
        assert agent.output_type == Strategy
        mock_google_model.assert_called_once_with("gemini-3-flash-preview")
        mock_get_api_key.assert_called_once_with("GOOGLE_API_KEY")

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    def test_create_strategist_agent_raises_error_when_api_key_missing(
        self, mock_get_api_key: MagicMock
    ) -> None:
        """Test that create_strategist_agent raises ValueError when API key is missing."""
        mock_get_api_key.return_value = None

        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            create_strategist_agent(provider="openai", model="gpt-5.2")


class TestPydanticAIMultiProviderSupport:
    """Test Pydantic AI multi-provider support."""

    @patch("src.llm.pydantic_ai_agents.get_api_key")
    @patch("src.llm.pydantic_ai_agents.OpenAIModel")
    @patch("src.llm.pydantic_ai_agents.AnthropicModel")
    @patch("src.llm.pydantic_ai_agents.GoogleModel")
    @patch("src.llm.pydantic_ai_agents.get_llm_config")
    def test_multi_provider_support(
        self,
        mock_config: MagicMock,
        mock_google_model: MagicMock,
        mock_anthropic_model: MagicMock,
        mock_openai_model: MagicMock,
        mock_get_api_key: MagicMock,
    ) -> None:
        """Test that Pydantic AI agents support multiple providers (OpenAI, Anthropic, Google Gemini)."""
        # Setup mocks
        mock_config_instance = MagicMock()
        mock_config_instance.get_supported_models.side_effect = [
            {"gpt-5.2"},  # openai
            {"claude-haiku-4-5-20251001"},  # anthropic
            {"gemini-3-flash-preview"},  # gemini
        ]
        mock_config.return_value = mock_config_instance
        mock_get_api_key.side_effect = ["test-openai-key", "test-anthropic-key", "test-google-key"]
        mock_openai_model.return_value = MagicMock()
        mock_anthropic_model.return_value = MagicMock()
        mock_google_model.return_value = MagicMock()

        # Create agents for each provider
        openai_agent = create_scout_agent(provider="openai", model="gpt-5.2")
        anthropic_agent = create_scout_agent(
            provider="anthropic", model="claude-haiku-4-5-20251001"
        )
        gemini_agent = create_scout_agent(provider="gemini", model="gemini-3-flash-preview")

        # Verify all agents created successfully
        assert openai_agent is not None
        assert anthropic_agent is not None
        assert gemini_agent is not None
        assert openai_agent.output_type == BoardAnalysis
        assert anthropic_agent.output_type == BoardAnalysis
        assert gemini_agent.output_type == BoardAnalysis

        # Verify correct models were called
        mock_openai_model.assert_called_once_with("gpt-5.2")
        mock_anthropic_model.assert_called_once_with("claude-haiku-4-5-20251001")
        mock_google_model.assert_called_once_with("gemini-3-flash-preview")
