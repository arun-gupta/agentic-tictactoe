"""Strategist Agent - Move Selection and Strategy Assembly.

The Strategist Agent processes BoardAnalysis from Scout and:
- Selects the highest priority move using the Move Priority System
- Assembles a Strategy with primary move and alternatives
- Assigns confidence scores based on priority levels
- Generates game plan and risk assessment

This is a rule-based implementation (Phase 3). LLM enhancement comes in Phase 5.
"""

import time
from typing import Literal

from src.agents.base import BaseAgent
from src.domain.agent_models import (
    BoardAnalysis,
    MovePriority,
    MoveRecommendation,
    Strategy,
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

    def analyze(self, game_state: object) -> object:
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

            # 3.1.2: Strategy Assembly (IMPLEMENTING NOW)
            alternatives = self._generate_alternatives(analysis, primary_move)
            game_plan = self._generate_game_plan(analysis, primary_move)
            risk_assessment = self._assess_risk(analysis)

            # Create complete strategy
            strategy = Strategy(
                primary_move=primary_move,
                alternatives=alternatives,
                game_plan=game_plan,
                risk_assessment=risk_assessment,
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
            return self._create_recommendation(
                position=opportunity.position,
                priority=MovePriority.IMMEDIATE_WIN,
                reasoning="Take immediate winning move",
            )

        # Priority 2: BLOCK_THREAT - Block opponent win
        if analysis.threats:
            threat = analysis.threats[0]  # Block first threat
            return self._create_recommendation(
                position=threat.position,
                priority=MovePriority.BLOCK_THREAT,
                reasoning="Block opponent's winning threat",
            )

        # Priority 5: CENTER_CONTROL - Take center if available
        center = Position(row=1, col=1)
        if self._is_strategic_position_available(analysis, center):
            return self._create_recommendation(
                position=center,
                priority=MovePriority.CENTER_CONTROL,
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
                return self._create_recommendation(
                    position=corner,
                    priority=MovePriority.CORNER_CONTROL,
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
                return self._create_recommendation(
                    position=edge,
                    priority=MovePriority.EDGE_PLAY,
                    reasoning="Take edge position",
                )

        # Fallback: If no strategic moves found, return center
        # (This shouldn't happen in normal gameplay)
        return self._create_recommendation(
            position=Position(row=1, col=1),
            priority=MovePriority.RANDOM_VALID,
            reasoning="Fallback to center position",
        )

    def _is_strategic_position_available(self, analysis: BoardAnalysis, position: Position) -> bool:
        """Check if a strategic position is available (in strategic_moves list).

        Args:
            analysis: BoardAnalysis with strategic_moves
            position: Position to check

        Returns:
            True if position is in strategic_moves list
        """
        return any(move.position == position for move in analysis.strategic_moves)

    # =========================================================================
    # 3.1.3: Confidence Scoring
    # =========================================================================

    def _create_recommendation(
        self, position: Position, priority: MovePriority, reasoning: str
    ) -> MoveRecommendation:
        """Create MoveRecommendation with confidence based on priority.

        Confidence mapping (Section 3.5):
        - IMMEDIATE_WIN: 1.0
        - BLOCK_THREAT: 0.95
        - FORCE_WIN: 0.85
        - PREVENT_FORK: 0.80
        - CENTER_CONTROL: 0.70
        - CORNER_CONTROL: 0.60
        - EDGE_PLAY: 0.50
        - RANDOM_VALID: 0.30

        Args:
            position: Position for the move
            priority: Priority level
            reasoning: Explanation of why this move

        Returns:
            MoveRecommendation with confidence score
        """
        confidence_map = {
            MovePriority.IMMEDIATE_WIN: 1.0,
            MovePriority.BLOCK_THREAT: 0.95,
            MovePriority.FORCE_WIN: 0.85,
            MovePriority.PREVENT_FORK: 0.80,
            MovePriority.CENTER_CONTROL: 0.70,
            MovePriority.CORNER_CONTROL: 0.60,
            MovePriority.EDGE_PLAY: 0.50,
            MovePriority.RANDOM_VALID: 0.30,
        }

        confidence = confidence_map.get(priority, 0.5)

        return MoveRecommendation(
            position=position,
            priority=priority,
            confidence=confidence,
            reasoning=reasoning,
        )

    # =========================================================================
    # 3.1.2: Strategy Assembly
    # =========================================================================

    def _generate_alternatives(
        self, analysis: BoardAnalysis, primary_move: MoveRecommendation
    ) -> list[MoveRecommendation]:
        """Generate alternative moves sorted by priority descending.

        Creates list of backup moves in case primary fails.
        Excludes the primary move from alternatives.

        Args:
            analysis: BoardAnalysis with all available moves
            primary_move: The selected primary move

        Returns:
            List of alternative MoveRecommendations sorted by priority (descending)
        """
        alternatives: list[MoveRecommendation] = []

        # Add opportunities (wins) as alternatives if not primary
        for opp in analysis.opportunities:
            if opp.position != primary_move.position:
                alternatives.append(
                    self._create_recommendation(
                        position=opp.position,
                        priority=MovePriority.IMMEDIATE_WIN,
                        reasoning="Alternative winning move",
                    )
                )

        # Add threats (blocks) as alternatives if not primary
        for threat in analysis.threats:
            if threat.position != primary_move.position:
                alternatives.append(
                    self._create_recommendation(
                        position=threat.position,
                        priority=MovePriority.BLOCK_THREAT,
                        reasoning="Alternative threat blocking move",
                    )
                )

        # Add strategic positions as alternatives
        center = Position(row=1, col=1)
        if (
            self._is_strategic_position_available(analysis, center)
            and center != primary_move.position
        ):
            alternatives.append(
                self._create_recommendation(
                    position=center,
                    priority=MovePriority.CENTER_CONTROL,
                    reasoning="Alternative center control",
                )
            )

        # Add corners
        corners = [
            Position(row=0, col=0),
            Position(row=0, col=2),
            Position(row=2, col=0),
            Position(row=2, col=2),
        ]
        for corner in corners:
            if (
                self._is_strategic_position_available(analysis, corner)
                and corner != primary_move.position
            ):
                alternatives.append(
                    self._create_recommendation(
                        position=corner,
                        priority=MovePriority.CORNER_CONTROL,
                        reasoning=f"Alternative corner at ({corner.row}, {corner.col})",
                    )
                )

        # Add edges
        edges = [
            Position(row=0, col=1),
            Position(row=1, col=0),
            Position(row=1, col=2),
            Position(row=2, col=1),
        ]
        for edge in edges:
            if (
                self._is_strategic_position_available(analysis, edge)
                and edge != primary_move.position
            ):
                alternatives.append(
                    self._create_recommendation(
                        position=edge,
                        priority=MovePriority.EDGE_PLAY,
                        reasoning=f"Alternative edge at ({edge.row}, {edge.col})",
                    )
                )

        # Sort by priority (descending)
        alternatives.sort(key=lambda x: x.priority.value, reverse=True)

        # Return top 5 alternatives
        return alternatives[:5]

    def _generate_game_plan(self, analysis: BoardAnalysis, primary_move: MoveRecommendation) -> str:
        """Generate game plan explanation.

        Creates human-readable explanation of the strategy.

        Args:
            analysis: BoardAnalysis with game state info
            primary_move: The selected primary move

        Returns:
            Game plan string
        """
        phase = analysis.game_phase
        priority = primary_move.priority

        if priority == MovePriority.IMMEDIATE_WIN:
            return f"Win the game immediately by playing at ({primary_move.position.row}, {primary_move.position.col})"

        if priority == MovePriority.BLOCK_THREAT:
            return f"Block opponent's winning threat at ({primary_move.position.row}, {primary_move.position.col})"

        if priority == MovePriority.CENTER_CONTROL:
            return f"Control the center position to maximize future opportunities ({phase} phase)"

        if priority == MovePriority.CORNER_CONTROL:
            return f"Take corner position for strategic advantage ({phase} phase)"

        if priority == MovePriority.EDGE_PLAY:
            return f"Play edge position to maintain board presence ({phase} phase)"

        return f"Make strategic move at ({primary_move.position.row}, {primary_move.position.col})"

    def _assess_risk(self, analysis: BoardAnalysis) -> Literal["low", "medium", "high"]:
        """Assess risk level based on board analysis.

        Risk levels:
        - low: Winning position or no threats
        - medium: Balanced position with some threats
        - high: Multiple threats or losing position

        Args:
            analysis: BoardAnalysis with threats and evaluation

        Returns:
            Risk level: 'low', 'medium', or 'high'
        """
        threat_count = len(analysis.threats)
        eval_score = analysis.board_evaluation_score

        # High risk: Multiple threats or very negative evaluation
        if threat_count >= 2 or eval_score <= -0.5:
            return "high"

        # Low risk: No threats and positive evaluation
        if threat_count == 0 and eval_score >= 0.3:
            return "low"

        # Medium risk: Everything else
        return "medium"
