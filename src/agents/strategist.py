"""Strategist Agent - Move Selection and Strategy Assembly.

The Strategist Agent processes BoardAnalysis from Scout and:
- Selects the highest priority move using the Move Priority System
- Assembles a Strategy with primary move and alternatives
- Assigns confidence scores based on priority levels
- Generates game plan and risk assessment

Phase 5 implementation: LLM-enhanced with Pydantic AI and fallback to priority-based.
"""

import asyncio
import logging
import time
from typing import Literal

from pydantic_ai import Agent
from pydantic_ai.exceptions import UnexpectedModelBehavior

from src.agents.base import BaseAgent
from src.domain.agent_models import (
    BoardAnalysis,
    MovePriority,
    MoveRecommendation,
    Strategy,
)
from src.domain.models import Position
from src.domain.result import AgentResult
from src.llm.pydantic_ai_agents import create_strategist_agent

logger = logging.getLogger(__name__)


class StrategistAgent(BaseAgent):
    """Strategist Agent for move selection and strategy assembly.

    Uses LLM-enhanced strategy with fallback to priority-based logic.
    Includes retry logic, timeout handling, and comprehensive error handling.
    """

    def __init__(
        self,
        ai_symbol: str = "O",
        llm_enabled: bool = False,
        provider: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 5.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize Strategist Agent.

        Args:
            ai_symbol: The symbol this AI is playing as ('X' or 'O')
            llm_enabled: Whether to use LLM for strategy (defaults to False for backward compatibility)
            provider: LLM provider name (openai, anthropic, gemini). If None, uses first available.
            model: Model name. If None, uses first model from config for the provider.
            timeout_seconds: Timeout for LLM calls in seconds (default: 5.0)
            max_retries: Maximum number of retries on timeout (default: 3)
        """
        self.ai_symbol = ai_symbol
        self.llm_enabled = llm_enabled
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        # Initialize Pydantic AI agent if LLM is enabled
        self._llm_agent: Agent[None, Strategy] | None = None
        if self.llm_enabled:
            try:
                self._llm_agent = create_strategist_agent(provider, model)
                logger.info(
                    f"Strategist LLM enabled with provider={provider}, model={model}, "
                    f"timeout={timeout_seconds}s, max_retries={max_retries}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Strategist LLM agent: {e}. Falling back to priority-based."
                )
                self.llm_enabled = False
                self._llm_agent = None

    def analyze(self, game_state: object) -> object:
        """Not used - Strategist uses plan() instead of analyze().

        This satisfies BaseAgent interface but Strategist receives
        BoardAnalysis from Scout, not GameState.
        """
        raise NotImplementedError("Strategist uses plan() method instead")

    def plan(self, analysis: BoardAnalysis) -> AgentResult[Strategy]:
        """Generate strategy from board analysis.

        Uses LLM strategy if enabled, with fallback to priority-based on errors/timeout.
        Implements priority-based move selection, strategy assembly, and confidence scoring.

        Args:
            analysis: BoardAnalysis from Scout agent

        Returns:
            AgentResult containing Strategy with move recommendations
        """
        start_time = time.time()

        try:
            # Try LLM strategy if enabled
            if self.llm_enabled and self._llm_agent:
                try:
                    strategy = self._plan_with_llm(analysis)
                    execution_time = (time.time() - start_time) * 1000
                    logger.info(f"Strategist LLM planning completed in {execution_time:.2f}ms")
                    return AgentResult[Strategy](
                        success=True,
                        data=strategy,
                        execution_time_ms=execution_time,
                    )
                except Exception as llm_error:
                    # Log LLM failure and fall back to priority-based
                    logger.warning(
                        f"Strategist LLM planning failed: {llm_error}. Falling back to priority-based."
                    )

            # Fallback to priority-based strategy
            strategy = self._plan_priority_based(analysis)

            execution_time = (time.time() - start_time) * 1000  # Convert to ms

            return AgentResult[Strategy](
                success=True,
                data=strategy,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Strategist planning failed completely: {e}")
            return AgentResult[Strategy](
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time,
            )

    def _plan_with_llm(self, analysis: BoardAnalysis) -> Strategy:
        """Generate strategy using Pydantic AI with retry logic.

        Args:
            analysis: BoardAnalysis from Scout agent

        Returns:
            Strategy from LLM

        Raises:
            TimeoutError: If LLM call exceeds timeout after all retries
            Exception: If LLM call fails with non-timeout error
        """
        # Build prompt with board analysis and game context
        prompt = self._build_llm_prompt(analysis)

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                llm_start = time.time()

                # Run LLM call with timeout
                result = asyncio.run(
                    asyncio.wait_for(
                        self._llm_agent.run(prompt),  # type: ignore[union-attr]
                        timeout=self.timeout_seconds,
                    )
                )

                llm_latency = (time.time() - llm_start) * 1000

                # Extract Strategy from result
                strategy: Strategy = result.data

                # Log LLM call metadata
                logger.info(
                    f"Strategist LLM call metadata: "
                    f"attempt={attempt + 1}/{self.max_retries}, "
                    f"latency={llm_latency:.2f}ms, "
                    f"prompt_length={len(prompt)}"
                )

                return strategy

            except TimeoutError as timeout_err:
                wait_time = 2**attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(
                    f"Strategist LLM timeout (attempt {attempt + 1}/{self.max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                else:
                    raise TimeoutError(
                        f"Strategist LLM call timed out after {self.max_retries} retries "
                        f"(timeout: {self.timeout_seconds}s)"
                    ) from timeout_err

            except UnexpectedModelBehavior as e:
                # Pydantic AI specific errors (parse errors, validation errors)
                logger.error(f"Strategist LLM parse/validation error: {e}")
                raise Exception(f"LLM parse error: {e}") from e

            except Exception as e:
                # Authentication errors, API errors, etc.
                logger.error(f"Strategist LLM call failed: {e}")
                raise

        # This should never be reached (all paths return or raise)
        raise RuntimeError("LLM planning failed: no successful attempts")

    def _build_llm_prompt(self, analysis: BoardAnalysis) -> str:
        """Build prompt for LLM with board analysis and game context.

        Args:
            analysis: BoardAnalysis from Scout

        Returns:
            Formatted prompt string
        """
        # Format threats
        threats_str = "None"
        if analysis.threats:
            threats_str = ", ".join(
                f"({t.position.row},{t.position.col})" for t in analysis.threats
            )

        # Format opportunities
        opportunities_str = "None"
        if analysis.opportunities:
            opportunities_str = ", ".join(
                f"({o.position.row},{o.position.col})" for o in analysis.opportunities
            )

        # Format strategic moves summary
        strategic_summary = f"{len(analysis.strategic_moves)} positions available"

        prompt = f"""Given this Tic-Tac-Toe board analysis, recommend the best move strategy:

Game Phase: {analysis.game_phase}
Board Evaluation: {analysis.board_evaluation_score}

Threats (opponent wins): {threats_str}
Opportunities (AI wins): {opportunities_str}
Strategic Positions: {strategic_summary}

AI Symbol: {self.ai_symbol}

Provide a comprehensive strategy including:
1. Primary move: The best move with highest priority (IMMEDIATE_WIN, BLOCK_THREAT, CENTER_CONTROL, CORNER_CONTROL, or EDGE_PLAY)
2. Alternative moves: Backup options sorted by priority descending
3. Game plan: Overall strategy explanation (2-3 sentences)
4. Risk assessment: 'low', 'medium', or 'high' based on current position

Return a structured Strategy with MoveRecommendation objects."""

        return prompt

    def _plan_priority_based(self, analysis: BoardAnalysis) -> Strategy:
        """Generate strategy using priority-based logic (fallback).

        Args:
            analysis: BoardAnalysis from Scout agent

        Returns:
            Strategy from priority-based logic
        """
        # 3.1.1: Priority-Based Move Selection
        primary_move = self._select_primary_move(analysis)

        # 3.1.2: Strategy Assembly
        alternatives = self._generate_alternatives(analysis, primary_move)
        game_plan = self._generate_game_plan(analysis, primary_move)
        risk_assessment = self._assess_risk(analysis)

        # Create complete strategy
        return Strategy(
            primary_move=primary_move,
            alternatives=alternatives,
            game_plan=game_plan,
            risk_assessment=risk_assessment,
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
