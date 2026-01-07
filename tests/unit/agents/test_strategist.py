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
