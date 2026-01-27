"""Live integration tests for Agent LLM functionality.

These tests make real LLM API calls to verify end-to-end agent functionality.
They are opt-in (marked with @pytest.mark.live_llm) and skipped unless explicitly enabled.

Usage:
    # Run all live LLM integration tests
    RUN_LIVE_LLM_TESTS=1 pytest -m live_llm tests/integration/agents/

    # Run with specific provider
    RUN_LIVE_LLM_TESTS=1 SCOUT_PROVIDER=gemini pytest -m live_llm

    # Run verbose with detailed output
    RUN_LIVE_LLM_TESTS=1 pytest -m live_llm -v -s tests/integration/agents/

Environment Variables:
    - RUN_LIVE_LLM_TESTS=1: Enable live tests (required)
    - SCOUT_PROVIDER: Override Scout provider (openai, anthropic, gemini)
    - STRATEGIST_PROVIDER: Override Strategist provider
    - LLM_ENABLED=true: Must be set in .env or environment

Cost Warning:
    These tests make real API calls and will incur costs. Each test typically:
    - Scout: ~500-1000 tokens (~$0.001-0.01 depending on provider)
    - Strategist: ~300-800 tokens (~$0.001-0.01 depending on provider)
    - Pipeline: Both agents (~$0.002-0.02 per test)
"""

import os

import pytest

from src.agents.pipeline import AgentPipeline
from src.agents.scout import ScoutAgent
from src.agents.strategist import StrategistAgent
from src.config.llm_config import get_llm_config
from src.domain.models import Board, GameState


def _live_tests_enabled() -> bool:
    """Check if live LLM tests are enabled."""
    return os.getenv("RUN_LIVE_LLM_TESTS", "").strip() in {"1", "true", "yes", "on"}


def _skip_if_not_enabled():
    """Skip test if live tests are not enabled."""
    if not _live_tests_enabled():
        pytest.skip("Set RUN_LIVE_LLM_TESTS=1 to enable live LLM integration tests.")


def _verify_llm_config():
    """Verify LLM configuration is valid."""
    config = get_llm_config()
    config_data = config.get_config()

    if not config_data.enabled:
        pytest.skip("LLM_ENABLED=true must be set in .env or environment")

    is_valid, error = config.validate_config()
    if not is_valid:
        pytest.skip(f"Invalid LLM configuration: {error}")


def _get_test_game_state(scenario: str = "opening") -> GameState:
    """Get game state for testing scenarios."""
    if scenario == "opening":
        # Empty board, first move
        board = Board()
        return GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

    elif scenario == "threat":
        # Opponent has two in a row (threat scenario)
        board = Board(
            cells=[
                ["X", "X", "EMPTY"],  # X threatens to win at (0,2)
                ["O", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        return GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

    elif scenario == "opportunity":
        # AI has two in a row (opportunity to win)
        board = Board(
            cells=[
                ["O", "O", "EMPTY"],  # O can win at (0,2)
                ["X", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        return GameState(board=board, player_symbol="X", ai_symbol="O", move_count=4)

    elif scenario == "midgame":
        # Complex midgame position
        board = Board(
            cells=[
                ["X", "O", "EMPTY"],
                ["O", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "X"],
            ]
        )
        return GameState(board=board, player_symbol="X", ai_symbol="O", move_count=5)

    else:
        raise ValueError(f"Unknown scenario: {scenario}")


@pytest.mark.live_llm
@pytest.mark.integration
class TestScoutLiveIntegration:
    """Live integration tests for Scout agent with real LLM calls."""

    def test_scout_analyzes_opening_position_with_llm(self) -> None:
        """Scout agent analyzes opening position using real LLM."""
        _skip_if_not_enabled()
        _verify_llm_config()

        config = get_llm_config()
        scout_config = config.get_agent_config("scout")

        scout = ScoutAgent(
            ai_symbol="O",
            llm_enabled=True,
            provider=scout_config.provider,
            model=scout_config.model,
        )

        game_state = _get_test_game_state("opening")
        result = scout.analyze(game_state)

        # Verify successful analysis
        assert result.success, f"Scout analysis failed: {result.error_message}"
        assert result.data is not None

        # Verify BoardAnalysis structure
        analysis = result.data
        assert hasattr(analysis, "game_phase")
        assert hasattr(analysis, "board_evaluation_score")
        assert hasattr(analysis, "threats")
        assert hasattr(analysis, "opportunities")
        assert hasattr(analysis, "strategic_moves")

        # Opening position should have strategic moves (center/corners)
        assert len(analysis.strategic_moves) > 0, "Opening should suggest strategic positions"

        # Verify metadata
        assert result.execution_time_ms > 0
        print(f"\n✓ Scout analysis completed in {result.execution_time_ms:.2f}ms")
        print(f"  Game phase: {analysis.game_phase}")
        print(f"  Board eval: {analysis.board_evaluation_score:.2f}")
        print(f"  Strategic moves: {len(analysis.strategic_moves)}")

    def test_scout_detects_threat_with_llm(self) -> None:
        """Scout agent detects opponent threat using real LLM."""
        _skip_if_not_enabled()
        _verify_llm_config()

        config = get_llm_config()
        scout_config = config.get_agent_config("scout")

        scout = ScoutAgent(
            ai_symbol="O",
            llm_enabled=True,
            provider=scout_config.provider,
            model=scout_config.model,
        )

        game_state = _get_test_game_state("threat")
        result = scout.analyze(game_state)

        # Verify successful analysis
        assert result.success, f"Scout analysis failed: {result.error_message}"
        assert result.data is not None

        analysis = result.data

        # Should detect threat at (0,2)
        assert len(analysis.threats) > 0, "Scout should detect opponent threat"

        threat = analysis.threats[0]
        assert threat.position.row == 0
        assert threat.position.col == 2

        print(f"\n✓ Scout detected threat at ({threat.position.row}, {threat.position.col})")
        print(f"  Execution time: {result.execution_time_ms:.2f}ms")

    def test_scout_detects_opportunity_with_llm(self) -> None:
        """Scout agent detects winning opportunity using real LLM."""
        _skip_if_not_enabled()
        _verify_llm_config()

        config = get_llm_config()
        scout_config = config.get_agent_config("scout")

        scout = ScoutAgent(
            ai_symbol="O",
            llm_enabled=True,
            provider=scout_config.provider,
            model=scout_config.model,
        )

        game_state = _get_test_game_state("opportunity")
        result = scout.analyze(game_state)

        # Verify successful analysis
        assert result.success, f"Scout analysis failed: {result.error_message}"
        assert result.data is not None

        analysis = result.data

        # Should detect opportunity at (0,2)
        assert len(analysis.opportunities) > 0, "Scout should detect winning opportunity"

        opp = analysis.opportunities[0]
        assert opp.position.row == 0
        assert opp.position.col == 2

        print(f"\n✓ Scout detected opportunity at ({opp.position.row}, {opp.position.col})")
        print(f"  Confidence: {opp.confidence:.2f}")


@pytest.mark.live_llm
@pytest.mark.integration
class TestStrategistLiveIntegration:
    """Live integration tests for Strategist agent with real LLM calls."""

    def test_strategist_plans_opening_move_with_llm(self) -> None:
        """Strategist agent plans opening move using real LLM."""
        _skip_if_not_enabled()
        _verify_llm_config()

        config = get_llm_config()
        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        # First get Scout analysis
        scout = ScoutAgent(
            ai_symbol="O",
            llm_enabled=True,
            provider=scout_config.provider,
            model=scout_config.model,
        )

        game_state = _get_test_game_state("opening")
        scout_result = scout.analyze(game_state)
        assert scout_result.success and scout_result.data

        # Then plan strategy
        strategist = StrategistAgent(
            ai_symbol="O",
            llm_enabled=True,
            provider=strategist_config.provider,
            model=strategist_config.model,
        )

        result = strategist.plan(scout_result.data)

        # Verify successful planning
        assert result.success, f"Strategist planning failed: {result.error_message}"
        assert result.data is not None

        # Verify Strategy structure
        strategy = result.data
        assert strategy.primary_move is not None
        assert strategy.primary_move.position is not None
        assert hasattr(strategy, "game_plan")
        assert hasattr(strategy, "risk_assessment")

        # Opening move should prefer center or corner
        pos = strategy.primary_move.position
        is_center = pos.row == 1 and pos.col == 1
        is_corner = (pos.row, pos.col) in [(0, 0), (0, 2), (2, 0), (2, 2)]
        assert is_center or is_corner, "Opening should prefer center or corner"

        print(f"\n✓ Strategist planned move at ({pos.row}, {pos.col})")
        print(f"  Priority: {strategy.primary_move.priority}")
        print(f"  Confidence: {strategy.primary_move.confidence:.2f}")
        print(f"  Execution time: {result.execution_time_ms:.2f}ms")

    def test_strategist_blocks_threat_with_llm(self) -> None:
        """Strategist agent blocks opponent threat using real LLM."""
        _skip_if_not_enabled()
        _verify_llm_config()

        config = get_llm_config()
        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        # Get Scout analysis (should detect threat)
        scout = ScoutAgent(
            ai_symbol="O",
            llm_enabled=True,
            provider=scout_config.provider,
            model=scout_config.model,
        )

        game_state = _get_test_game_state("threat")
        scout_result = scout.analyze(game_state)
        assert scout_result.success and scout_result.data

        # Plan strategy (should block threat)
        strategist = StrategistAgent(
            ai_symbol="O",
            llm_enabled=True,
            provider=strategist_config.provider,
            model=strategist_config.model,
        )

        result = strategist.plan(scout_result.data)

        # Verify successful planning
        assert result.success, f"Strategist planning failed: {result.error_message}"
        assert result.data is not None

        strategy = result.data

        # Should select move to block threat at (0,2)
        assert strategy.primary_move is not None
        pos = strategy.primary_move.position
        assert (
            pos.row == 0 and pos.col == 2
        ), f"Should block threat at (0,2), got ({pos.row},{pos.col})"

        print(f"\n✓ Strategist blocked threat at ({pos.row}, {pos.col})")
        print(f"  Priority: {strategy.primary_move.priority}")


@pytest.mark.live_llm
@pytest.mark.integration
class TestPipelineLiveIntegration:
    """Live integration tests for full agent pipeline with real LLM calls."""

    def test_pipeline_executes_with_llm_end_to_end(self) -> None:
        """Full pipeline executes Scout → Strategist → Executor with real LLM."""
        _skip_if_not_enabled()
        _verify_llm_config()

        config = get_llm_config()
        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            scout_provider=scout_config.provider,
            scout_model=scout_config.model,
            strategist_provider=strategist_config.provider,
            strategist_model=strategist_config.model,
        )

        game_state = _get_test_game_state("opening")
        result = pipeline.execute_pipeline(game_state)

        # Verify successful execution
        assert result.success, f"Pipeline execution failed: {result.error_message}"
        assert result.data is not None

        # Verify MoveExecution
        execution = result.data
        assert execution.success
        assert execution.position is not None
        assert execution.validation_errors == []

        # Verify move is valid for opening
        pos = execution.position
        assert 0 <= pos.row <= 2 and 0 <= pos.col <= 2
        assert game_state.board.is_empty(pos)

        print("\n✓ Pipeline completed successfully")
        print(f"  Selected move: ({pos.row}, {pos.col})")
        print(f"  Priority used: {execution.actual_priority_used}")
        print(f"  Total time: {result.execution_time_ms:.2f}ms")
        print(f"  Reasoning: {execution.reasoning[:100]}...")

    def test_pipeline_handles_threat_scenario_with_llm(self) -> None:
        """Pipeline correctly handles threat scenario with real LLM."""
        _skip_if_not_enabled()
        _verify_llm_config()

        config = get_llm_config()
        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            scout_provider=scout_config.provider,
            scout_model=scout_config.model,
            strategist_provider=strategist_config.provider,
            strategist_model=strategist_config.model,
        )

        game_state = _get_test_game_state("threat")
        result = pipeline.execute_pipeline(game_state)

        # Verify successful execution
        assert result.success, f"Pipeline execution failed: {result.error_message}"
        assert result.data is not None

        execution = result.data
        assert execution.success

        # Should block threat at (0,2)
        pos = execution.position
        assert pos is not None
        assert (
            pos.row == 0 and pos.col == 2
        ), f"Should block threat at (0,2), got ({pos.row},{pos.col})"

        print(f"\n✓ Pipeline blocked threat at ({pos.row}, {pos.col})")
        print(f"  Total time: {result.execution_time_ms:.2f}ms")

    def test_pipeline_handles_midgame_complexity_with_llm(self) -> None:
        """Pipeline handles complex midgame position with real LLM."""
        _skip_if_not_enabled()
        _verify_llm_config()

        config = get_llm_config()
        scout_config = config.get_agent_config("scout")
        strategist_config = config.get_agent_config("strategist")

        pipeline = AgentPipeline(
            ai_symbol="O",
            llm_enabled=True,
            scout_provider=scout_config.provider,
            scout_model=scout_config.model,
            strategist_provider=strategist_config.provider,
            strategist_model=strategist_config.model,
        )

        game_state = _get_test_game_state("midgame")
        result = pipeline.execute_pipeline(game_state)

        # Verify successful execution
        assert result.success, f"Pipeline execution failed: {result.error_message}"
        assert result.data is not None

        execution = result.data
        assert execution.success
        assert execution.position is not None
        assert game_state.board.is_empty(execution.position)

        print("\n✓ Pipeline handled midgame position")
        print(f"  Selected move: ({execution.position.row}, {execution.position.col})")
        print(f"  Total time: {result.execution_time_ms:.2f}ms")
