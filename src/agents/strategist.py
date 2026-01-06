"""Strategist Agent - Move Selection and Strategy Assembly.

The Strategist Agent processes BoardAnalysis from Scout and:
- Selects the highest priority move using the Move Priority System
- Assembles a Strategy with primary move and alternatives
- Assigns confidence scores based on priority levels
- Generates game plan and risk assessment

This is a rule-based implementation (Phase 3). LLM enhancement comes in Phase 5.
"""

import time
from typing import Optional

from src.agents.base import BaseAgent
from src.domain.agent_models import (
    BoardAnalysis,
    MoveRecommendation,
    MovePriority,
    Opportunity,
    Strategy,
    Threat,
)
from src.domain.models import Position
from src.domain.result import AgentResult


class StrategistAgent(BaseAgent):
    """Strategist Agent for move selection and strategy assembly.

    Uses rule-based priority system to select best moves and generate
    comprehensive game strategy with alternatives.
    """

    def __init__(self, ai_symbol: str = "O") -> None:
        """Initialize Strategist Agent.

        Args:
            ai_symbol: The symbol this AI is playing as ('X' or 'O')
        """
        self.ai_symbol = ai_symbol

    def analyze(self, game_state) -> object:
        """Not used - Strategist uses plan() instead of analyze().

        This satisfies BaseAgent interface but Strategist receives
        BoardAnalysis from Scout, not GameState.
        """
        raise NotImplementedError("Strategist uses plan() method instead")

    def plan(self, analysis: BoardAnalysis) -> AgentResult[Strategy]:
        """Generate strategy from board analysis.

        Currently only implements 3.1.1 (Priority-Based Move Selection).
        3.1.2 (Strategy Assembly) and 3.1.3 (Confidence Scoring) not yet implemented.

        Args:
            analysis: BoardAnalysis from Scout agent

        Returns:
            AgentResult containing Strategy with move recommendations
        """
        start_time = time.time()

        try:
            # 3.1.1: Priority-Based Move Selection (IMPLEMENTED)
            primary_move = self._select_primary_move(analysis)

            # TODO 3.1.2: Strategy Assembly - NOT YET IMPLEMENTED
            # TODO: Generate alternative moves
            # TODO: Generate game plan
            # TODO: Assess risk

            # Minimal strategy for now
            strategy = Strategy(
                primary_move=primary_move,
                alternatives=[],  # TODO: Implement in 3.1.2
                game_plan="TODO: Game plan will be implemented in 3.1.2",  # TODO: Implement in 3.1.2
                risk_assessment="medium",  # TODO: Implement in 3.1.2
            )

            execution_time = (time.time() - start_time) * 1000  # Convert to ms

            return AgentResult[Strategy](
                success=True,
                data=strategy,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentResult[Strategy](
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time,
            )

    # =========================================================================
    # 3.1.1: Priority-Based Move Selection
    # =========================================================================

    def _select_primary_move(self, analysis: BoardAnalysis) -> MoveRecommendation:
        """Select the highest priority move from board analysis.

        Priority order (Section 3.5):
        1. IMMEDIATE_WIN (100) - Take winning opportunity
        2. BLOCK_THREAT (90) - Block opponent win
        3. FORCE_WIN (80) - Create fork (not implemented yet)
        4. PREVENT_FORK (70) - Block opponent fork (not implemented yet)
        5. CENTER_CONTROL (50) - Take center
        6. CORNER_CONTROL (40) - Take corner
        7. EDGE_PLAY (30) - Take edge
        8. RANDOM_VALID (10) - Any valid move

        Args:
            analysis: BoardAnalysis with threats, opportunities, strategic moves

        Returns:
            MoveRecommendation with highest priority move
        """
        # Priority 1: IMMEDIATE_WIN - Take winning opportunity
        if analysis.opportunities:
            opportunity = analysis.opportunities[0]  # Take first opportunity
            # Hardcoded confidence for now (will be 3.1.3)
            return MoveRecommendation(
                position=opportunity.position,
                priority=MovePriority.IMMEDIATE_WIN,
                confidence=1.0,
                reasoning="Take immediate winning move",
            )

        # Priority 2: BLOCK_THREAT - Block opponent win
        if analysis.threats:
            threat = analysis.threats[0]  # Block first threat
            # Hardcoded confidence for now (will be 3.1.3)
            return MoveRecommendation(
                position=threat.position,
                priority=MovePriority.BLOCK_THREAT,
                confidence=0.95,
                reasoning="Block opponent's winning threat",
            )

        # Priority 5: CENTER_CONTROL - Take center if available
        center = Position(row=1, col=1)
        if self._is_strategic_position_available(analysis, center):
            # Hardcoded confidence for now (will be 3.1.3)
            return MoveRecommendation(
                position=center,
                priority=MovePriority.CENTER_CONTROL,
                confidence=0.7,
                reasoning="Control center position for strategic advantage",
            )

        # Priority 6: CORNER_CONTROL - Take corner
        corners = [
            Position(row=0, col=0),
            Position(row=0, col=2),
            Position(row=2, col=0),
            Position(row=2, col=2),
        ]
        for corner in corners:
            if self._is_strategic_position_available(analysis, corner):
                # Hardcoded confidence for now (will be 3.1.3)
                return MoveRecommendation(
                    position=corner,
                    priority=MovePriority.CORNER_CONTROL,
                    confidence=0.6,
                    reasoning="Take corner position for strategic control",
                )

        # Priority 7: EDGE_PLAY - Take edge
        edges = [
            Position(row=0, col=1),
            Position(row=1, col=0),
            Position(row=1, col=2),
            Position(row=2, col=1),
        ]
        for edge in edges:
            if self._is_strategic_position_available(analysis, edge):
                # Hardcoded confidence for now (will be 3.1.3)
                return MoveRecommendation(
                    position=edge,
                    priority=MovePriority.EDGE_PLAY,
                    confidence=0.5,
                    reasoning="Take edge position",
                )

        # Fallback: If no strategic moves found, return center
        # (This shouldn't happen in normal gameplay)
        # Hardcoded confidence for now (will be 3.1.3)
        return MoveRecommendation(
            position=Position(row=1, col=1),
            priority=MovePriority.RANDOM_VALID,
            confidence=0.3,
            reasoning="Fallback to center position",
        )

    def _is_strategic_position_available(
        self, analysis: BoardAnalysis, position: Position
    ) -> bool:
        """Check if a strategic position is available (in strategic_moves list).

        Args:
            analysis: BoardAnalysis with strategic_moves
            position: Position to check

        Returns:
            True if position is in strategic_moves list
        """
        return any(
            move.position == position for move in analysis.strategic_moves
        )
