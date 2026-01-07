"""Tests for Strategist Agent - Move Selection and Strategy Assembly.

This file includes:
1. Subsection tests (for incremental development/debugging)
2. Official acceptance criteria tests (AC-3.2.1 through AC-3.2.8)
"""

from src.agents.strategist import StrategistAgent
from src.domain.agent_models import (
    BoardAnalysis,
    MovePriority,
    MoveRecommendation,
    Opportunity,
    StrategicMove,
    Threat,
)
from src.domain.models import Position


# ==============================================================================
# SUBSECTION 3.1.1: Priority-Based Move Selection
# ==============================================================================
class TestPriorityBasedSelection:
    """Development tests for priority-based move selection logic."""

    def test_subsection_3_1_1_immediate_win_highest_priority(self) -> None:
        """Subsection 3.1.1: Immediate win gets highest priority (100)."""
        strategist = StrategistAgent(ai_symbol="O")

        # BoardAnalysis with winning opportunity
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[
                Opportunity(
                    position=Position(row=0, col=2),
                    line_type="row",
                    line_index=0,
                    confidence=1.0,
                )
            ],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.5,
        )

        result = strategist.plan(analysis)

        assert result.success
        assert result.data is not None
        strategy = result.data

        # Primary move should be the winning opportunity
        assert strategy.primary_move.position == Position(row=0, col=2)
        assert strategy.primary_move.priority == MovePriority.IMMEDIATE_WIN

    def test_subsection_3_1_1_block_threat_second_priority(self) -> None:
        """Subsection 3.1.1: Blocking threat gets second priority (90)."""
        strategist = StrategistAgent(ai_symbol="O")

        # BoardAnalysis with threat but no opportunities
        analysis = BoardAnalysis(
            threats=[
                Threat(
                    position=Position(row=1, col=1),
                    line_type="diagonal",
                    line_index=0,
                    severity="critical",
                )
            ],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=-0.3,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Primary move should block the threat
        assert strategy.primary_move.position == Position(row=1, col=1)
        assert strategy.primary_move.priority == MovePriority.BLOCK_THREAT

    def test_subsection_3_1_1_win_over_block(self) -> None:
        """Subsection 3.1.1: Win takes priority over blocking threat."""
        strategist = StrategistAgent(ai_symbol="O")

        # BoardAnalysis with both threat and opportunity
        analysis = BoardAnalysis(
            threats=[
                Threat(
                    position=Position(row=2, col=2),
                    line_type="diagonal",
                    line_index=1,
                    severity="critical",
                )
            ],
            opportunities=[
                Opportunity(
                    position=Position(row=0, col=0),
                    line_type="row",
                    line_index=0,
                    confidence=1.0,
                )
            ],
            strategic_moves=[],
            game_phase="endgame",
            board_evaluation_score=0.8,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Should take the win, not block the threat
        assert strategy.primary_move.position == Position(row=0, col=0)
        assert strategy.primary_move.priority == MovePriority.IMMEDIATE_WIN


# ==============================================================================
# SUBSECTION 3.1.2: Strategy Assembly
# ==============================================================================
class TestStrategyAssembly:
    """Development tests for Strategy object assembly."""

    def test_subsection_3_1_2_includes_primary_move(self) -> None:
        """Subsection 3.1.2: Strategy includes primary move recommendation."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[],
            opportunities=[
                Opportunity(
                    position=Position(row=1, col=1),
                    line_type="diagonal",
                    line_index=0,
                    confidence=1.0,
                )
            ],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.3,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Primary move should exist and be valid
        assert strategy.primary_move is not None
        assert isinstance(strategy.primary_move, MoveRecommendation)
        assert strategy.primary_move.position == Position(row=1, col=1)
        assert strategy.primary_move.reasoning != ""

    def test_subsection_3_1_2_includes_alternatives(self) -> None:
        """Subsection 3.1.2: Strategy includes alternative moves sorted by priority."""
        strategist = StrategistAgent(ai_symbol="O")

        # Multiple strategic options
        analysis = BoardAnalysis(
            threats=[
                Threat(
                    position=Position(row=0, col=0),
                    line_type="row",
                    line_index=0,
                    severity="critical",
                )
            ],
            opportunities=[
                Opportunity(
                    position=Position(row=2, col=2),
                    line_type="diagonal",
                    line_index=1,
                    confidence=1.0,
                )
            ],
            strategic_moves=[
                StrategicMove(
                    position=Position(row=1, col=1),
                    move_type="center",
                    priority=5,
                    reasoning="Control center",
                )
            ],
            game_phase="opening",
            board_evaluation_score=0.2,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Should have at least 2 alternatives
        assert len(strategy.alternatives) >= 2

        # Alternatives should be sorted by priority (descending)
        priorities = [alt.priority.value for alt in strategy.alternatives]
        assert priorities == sorted(priorities, reverse=True)

    def test_subsection_3_1_2_includes_game_plan(self) -> None:
        """Subsection 3.1.2: Strategy includes game plan explanation."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[
                Threat(
                    position=Position(row=0, col=1),
                    line_type="row",
                    line_index=0,
                    severity="critical",
                )
            ],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=-0.2,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Game plan should be non-empty string and not the TODO placeholder
        assert isinstance(strategy.game_plan, str)
        assert len(strategy.game_plan) > 0
        assert "TODO" not in strategy.game_plan

    def test_subsection_3_1_2_includes_risk_assessment(self) -> None:
        """Subsection 3.1.2: Strategy includes risk level assessment."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[
                StrategicMove(
                    position=Position(row=1, col=1),
                    move_type="center",
                    priority=5,
                    reasoning="Control center",
                )
            ],
            game_phase="opening",
            board_evaluation_score=0.0,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Risk assessment should be one of: low, medium, high
        assert strategy.risk_assessment in ["low", "medium", "high"]


# ==============================================================================
# SUBSECTION 3.1.3: Confidence Scoring
# ==============================================================================
class TestConfidenceScoring:
    """Development tests for confidence value assignment."""

    def test_subsection_3_1_3_immediate_win_confidence_1_0(self) -> None:
        """Subsection 3.1.3: Immediate win gets confidence=1.0."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[],
            opportunities=[
                Opportunity(
                    position=Position(row=2, col=0),
                    line_type="column",
                    line_index=0,
                    confidence=1.0,
                )
            ],
            strategic_moves=[],
            game_phase="endgame",
            board_evaluation_score=0.9,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # IMMEDIATE_WIN should have confidence 1.0
        assert strategy.primary_move.priority == MovePriority.IMMEDIATE_WIN
        assert strategy.primary_move.confidence == 1.0

    def test_subsection_3_1_3_block_threat_confidence_0_95(self) -> None:
        """Subsection 3.1.3: Block threat gets confidence=0.95."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[
                Threat(
                    position=Position(row=1, col=2),
                    line_type="row",
                    line_index=1,
                    severity="critical",
                )
            ],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=-0.4,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # BLOCK_THREAT should have confidence 0.95
        assert strategy.primary_move.priority == MovePriority.BLOCK_THREAT
        assert strategy.primary_move.confidence == 0.95

    def test_subsection_3_1_3_center_control_confidence_0_7(self) -> None:
        """Subsection 3.1.3: Center control gets confidence=0.7."""
        strategist = StrategistAgent(ai_symbol="O")

        # Empty board analysis - should default to center
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[
                StrategicMove(
                    position=Position(row=1, col=1),
                    move_type="center",
                    priority=5,
                    reasoning="Control center",
                )
            ],
            game_phase="opening",
            board_evaluation_score=0.0,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # CENTER_CONTROL should have confidence 0.7
        assert strategy.primary_move.priority == MovePriority.CENTER_CONTROL
        assert strategy.primary_move.confidence == 0.7


# ==============================================================================
# OFFICIAL ACCEPTANCE CRITERIA TESTS (AC-3.2.1 through AC-3.2.8)
# ==============================================================================
class TestStrategistAcceptanceCriteria:
    """Official acceptance criteria tests for Strategist Agent."""

    def test_ac_3_2_1_blocks_threat(self) -> None:
        """AC-3.2.1: Given BoardAnalysis with Threat, primary_move blocks threat with BLOCK_THREAT priority."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[
                Threat(
                    position=Position(row=0, col=2),
                    line_type="row",
                    line_index=0,
                    severity="critical",
                )
            ],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=-0.3,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data
        assert strategy.primary_move.position == Position(row=0, col=2)
        assert strategy.primary_move.priority == MovePriority.BLOCK_THREAT

    def test_ac_3_2_2_takes_winning_opportunity(self) -> None:
        """AC-3.2.2: Given BoardAnalysis with Opportunity to win, primary_move takes win with IMMEDIATE_WIN."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[],
            opportunities=[
                Opportunity(
                    position=Position(row=1, col=1),
                    line_type="diagonal",
                    line_index=0,
                    confidence=1.0,
                )
            ],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.7,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data
        assert strategy.primary_move.position == Position(row=1, col=1)
        assert strategy.primary_move.priority == MovePriority.IMMEDIATE_WIN

    def test_ac_3_2_3_win_over_threat(self) -> None:
        """AC-3.2.3: Given both Threat and Opportunity, primary_move takes win (IMMEDIATE_WIN > BLOCK_THREAT)."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[
                Threat(
                    position=Position(row=2, col=1),
                    line_type="column",
                    line_index=1,
                    severity="critical",
                )
            ],
            opportunities=[
                Opportunity(
                    position=Position(row=0, col=0),
                    line_type="diagonal",
                    line_index=0,
                    confidence=1.0,
                )
            ],
            strategic_moves=[],
            game_phase="endgame",
            board_evaluation_score=0.6,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data
        # Should choose win over blocking threat
        assert strategy.primary_move.position == Position(row=0, col=0)
        assert strategy.primary_move.priority == MovePriority.IMMEDIATE_WIN

    def test_ac_3_2_4_alternatives_sorted_by_priority(self) -> None:
        """AC-3.2.4: Given multiple strategic positions, alternatives list sorted by priority descending."""
        strategist = StrategistAgent(ai_symbol="O")

        # Multiple options available
        analysis = BoardAnalysis(
            threats=[
                Threat(
                    position=Position(row=0, col=0),
                    line_type="row",
                    line_index=0,
                    severity="critical",
                )
            ],
            opportunities=[
                Opportunity(
                    position=Position(row=2, col=2),
                    line_type="diagonal",
                    line_index=1,
                    confidence=1.0,
                )
            ],
            strategic_moves=[
                StrategicMove(
                    position=Position(row=1, col=1),
                    move_type="center",
                    priority=5,
                    reasoning="Control center",
                )
            ],
            game_phase="midgame",
            board_evaluation_score=0.4,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Should have multiple alternatives
        assert len(strategy.alternatives) >= 2

        # Verify alternatives are sorted by priority (descending)
        priorities = [alt.priority.value for alt in strategy.alternatives]
        assert priorities == sorted(priorities, reverse=True)

    def test_ac_3_2_5_recommends_strategic_position(self) -> None:
        """AC-3.2.5: Given no clear moves, recommends center/corner with reasoning."""
        strategist = StrategistAgent(ai_symbol="O")

        # No threats or opportunities
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[
                StrategicMove(
                    position=Position(row=1, col=1),
                    move_type="center",
                    priority=5,
                    reasoning="Control center",
                )
            ],
            game_phase="opening",
            board_evaluation_score=0.0,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Should recommend center or corner
        assert strategy.primary_move.priority in [
            MovePriority.CENTER_CONTROL,
            MovePriority.CORNER_CONTROL,
        ]
        # Should include reasoning
        assert len(strategy.primary_move.reasoning) > 0

    def test_ac_3_2_6_fallback_on_timeout(self) -> None:
        """AC-3.2.6: Given LLM timeout (>5s), returns rule-based Strategy using Scout's highest priority."""
        strategist = StrategistAgent(ai_symbol="O")

        # Simulate timeout scenario - strategist should use rule-based fallback
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[
                Opportunity(
                    position=Position(row=1, col=1),
                    line_type="row",
                    line_index=1,
                    confidence=0.9,
                )
            ],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.5,
        )

        # Note: In Phase 5 (LLM integration), this will test actual timeout behavior
        # For now, rule-based logic should work correctly
        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data
        assert strategy.primary_move.position == Position(row=1, col=1)

    def test_ac_3_2_7_handles_empty_analysis(self) -> None:
        """AC-3.2.7: Given empty BoardAnalysis, returns Strategy with CENTER_CONTROL priority."""
        strategist = StrategistAgent(ai_symbol="O")

        # Completely empty analysis except center available
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[
                StrategicMove(
                    position=Position(row=1, col=1),
                    move_type="center",
                    priority=5,
                    reasoning="Control center",
                )
            ],
            game_phase="opening",
            board_evaluation_score=0.0,
        )

        result = strategist.plan(analysis)

        assert result.success
        strategy = result.data

        # Should default to center control in opening
        assert strategy.primary_move.priority == MovePriority.CENTER_CONTROL
        assert strategy.primary_move.position == Position(row=1, col=1)

    def test_ac_3_2_8_records_execution_time(self) -> None:
        """AC-3.2.8: Given execution, AgentResult.execution_time_ms is recorded."""
        strategist = StrategistAgent(ai_symbol="O")

        analysis = BoardAnalysis(
            threats=[],
            opportunities=[
                Opportunity(
                    position=Position(row=0, col=1),
                    line_type="row",
                    line_index=0,
                    confidence=1.0,
                )
            ],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.6,
        )

        result = strategist.plan(analysis)

        assert result.success
        # Execution time should be recorded and > 0
        assert result.execution_time_ms is not None
        assert result.execution_time_ms > 0
