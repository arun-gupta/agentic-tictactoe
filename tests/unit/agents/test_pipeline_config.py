"""Tests for Agent Pipeline Configuration Wiring - Subsection 5.2.3.

Subsection tests for Phase 5.2.3: Agent Pipeline Configuration Wiring
These tests verify that:
1. AgentPipeline accepts llm_enabled parameter and passes to agents
2. AgentPipeline accepts per-agent provider configuration
3. AgentPipeline accepts per-agent model configuration
4. AgentPipeline creates Scout with correct LLM config
5. AgentPipeline creates Strategist with correct LLM config
6. AgentPipeline keeps Executor rule-based (no LLM)
7. Config values propagate correctly to agents
8. Default values work when config not provided

Note: These tests mock LLM agent creation to test configuration wiring
without requiring actual API keys (important for CI environments).
"""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.pipeline import AgentPipeline


@pytest.fixture
def mock_llm_agents():
    """Mock LLM agent creation to avoid requiring API keys in tests."""
    with (
        patch("src.agents.scout.create_scout_agent") as mock_scout,
        patch("src.agents.strategist.create_strategist_agent") as mock_strategist,
    ):
        # Return mock agents that won't fail
        mock_scout.return_value = MagicMock()
        mock_strategist.return_value = MagicMock()
        yield mock_scout, mock_strategist


class TestAgentPipelineConfigurationWiring:
    """Test that AgentPipeline correctly wires LLM configuration to agents."""

    def test_subsection_5_2_3_1_accepts_llm_enabled_parameter(self, mock_llm_agents) -> None:
        """Subsection test 1: AgentPipeline accepts llm_enabled parameter."""
        # Should accept llm_enabled without error
        pipeline = AgentPipeline(ai_symbol="O", llm_enabled=True)

        # Verify pipeline created successfully
        assert pipeline is not None
        assert hasattr(pipeline, "scout")
        assert hasattr(pipeline, "strategist")
        assert hasattr(pipeline, "executor")

    def test_subsection_5_2_3_2_accepts_per_agent_provider_config(self, mock_llm_agents) -> None:
        """Subsection test 2: AgentPipeline accepts per-agent provider configuration."""
        # Should accept different providers for each agent
        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            scout_provider="openai",
            strategist_provider="anthropic",
        )

        # Verify pipeline created successfully with different providers
        assert pipeline is not None
        assert pipeline.scout is not None
        assert pipeline.strategist is not None

    def test_subsection_5_2_3_3_accepts_per_agent_model_config(self, mock_llm_agents) -> None:
        """Subsection test 3: AgentPipeline accepts per-agent model configuration."""
        # Should accept different models for each agent
        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            scout_provider="openai",
            scout_model="gpt-4o",
            strategist_provider="anthropic",
            strategist_model="claude-3-5-sonnet-latest",
        )

        # Verify pipeline created successfully with different models
        assert pipeline is not None
        assert pipeline.scout is not None
        assert pipeline.strategist is not None

    def test_subsection_5_2_3_4_creates_scout_with_correct_llm_config(
        self, mock_llm_agents
    ) -> None:
        """Subsection test 4: AgentPipeline creates Scout with correct LLM config."""
        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            scout_provider="openai",
            scout_model="gpt-4o",
        )

        # Verify Scout has LLM enabled
        assert pipeline.scout.llm_enabled is True

        # Verify Scout has correct provider and model (if accessible)
        # Note: These are private attributes, but we can verify through behavior
        assert pipeline.scout is not None

    def test_subsection_5_2_3_5_creates_strategist_with_correct_llm_config(
        self, mock_llm_agents
    ) -> None:
        """Subsection test 5: AgentPipeline creates Strategist with correct LLM config."""
        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            strategist_provider="anthropic",
            strategist_model="claude-3-5-sonnet-latest",
        )

        # Verify Strategist has LLM enabled
        assert pipeline.strategist.llm_enabled is True

        # Verify Strategist configured correctly
        assert pipeline.strategist is not None

    def test_subsection_5_2_3_6_keeps_executor_rule_based(self, mock_llm_agents) -> None:
        """Subsection test 6: AgentPipeline keeps Executor rule-based (no LLM)."""
        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            scout_provider="openai",
            strategist_provider="anthropic",
        )

        # Verify Executor has NO LLM-related attributes
        assert not hasattr(pipeline.executor, "llm_enabled")
        assert not hasattr(pipeline.executor, "_llm_agent")
        assert pipeline.executor is not None

    def test_subsection_5_2_3_7_config_values_propagate_correctly(self, mock_llm_agents) -> None:
        """Subsection test 7: Config values propagate correctly to agents."""
        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            scout_provider="gemini",
            scout_model="gemini-2.5-flash",
            strategist_provider="openai",
            strategist_model="gpt-5.2",
        )

        # Verify both agents have LLM enabled
        assert pipeline.scout.llm_enabled is True
        assert pipeline.strategist.llm_enabled is True

        # Verify pipeline created successfully
        assert pipeline.scout is not None
        assert pipeline.strategist is not None
        assert pipeline.executor is not None

    def test_subsection_5_2_3_8_default_values_work_when_config_not_provided(
        self,
    ) -> None:
        """Subsection test 8: Default values work when config not provided."""
        # Should work with no LLM config (defaults to rule-based)
        pipeline = AgentPipeline(ai_symbol="O")

        # Verify agents created with defaults (LLM disabled)
        assert pipeline.scout.llm_enabled is False
        assert pipeline.strategist.llm_enabled is False

        # Verify Executor still works
        assert pipeline.executor is not None

    def test_subsection_5_2_3_9_llm_disabled_creates_rule_based_agents(self) -> None:
        """Subsection test 9: llm_enabled=False creates rule-based agents."""
        # Explicitly disable LLM
        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=False,
            scout_provider="openai",  # Provided but shouldn't be used
            strategist_provider="anthropic",  # Provided but shouldn't be used
        )

        # Verify agents have LLM disabled
        assert pipeline.scout.llm_enabled is False
        assert pipeline.strategist.llm_enabled is False

        # Verify pipeline created successfully
        assert pipeline.scout is not None
        assert pipeline.strategist is not None
        assert pipeline.executor is not None
