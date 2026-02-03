"""Agent Pipeline Orchestration.

The pipeline coordinates the flow: Scout → Strategist → Executor
to produce a final move execution result.
"""

import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Any

from src.agents.executor import ExecutorAgent
from src.agents.scout import ScoutAgent
from src.agents.strategist import StrategistAgent
from src.domain.agent_models import (
    BoardAnalysis,
    MoveExecution,
    MovePriority,
    MoveRecommendation,
    Strategy,
)
from src.domain.errors import E_LLM_TIMEOUT
from src.domain.models import GameState, PlayerSymbol
from src.domain.result import AgentResult


class AgentPipeline:
    """Pipeline coordinator for orchestrating agent execution flow.

    Coordinates Scout → Strategist → Executor flow, passing typed domain
    models between agents and handling failures gracefully.
    """

    def __init__(
        self,
        ai_symbol: PlayerSymbol = "O",
        scout_timeout: float = 20.0,
        strategist_timeout: float = 15.0,
        executor_timeout: float = 2.0,
        total_timeout: float = 120.0,
        llm_enabled: bool = False,
        scout_provider: str | None = None,
        scout_model: str | None = None,
        strategist_provider: str | None = None,
        strategist_model: str | None = None,
    ) -> None:
        """Initialize the agent pipeline.

        Args:
            ai_symbol: The symbol this AI is playing as ('X' or 'O')
            scout_timeout: Timeout for Scout agent in seconds (default: 20.0)
            strategist_timeout: Timeout for Strategist agent in seconds (default: 15.0)
            executor_timeout: Timeout for Executor agent in seconds (default: 2.0)
            total_timeout: Total pipeline timeout in seconds (default: 120.0)
            llm_enabled: Enable LLM for Scout and Strategist (default: False)
            scout_provider: LLM provider for Scout (openai, anthropic, gemini)
            scout_model: LLM model for Scout
            strategist_provider: LLM provider for Strategist (openai, anthropic, gemini)
            strategist_model: LLM model for Strategist
        """
        self.ai_symbol = ai_symbol
        self.scout = ScoutAgent(
            ai_symbol=ai_symbol,
            llm_enabled=llm_enabled,
            provider=scout_provider,
            model=scout_model,
            timeout_seconds=scout_timeout,
        )
        self.strategist = StrategistAgent(
            ai_symbol=ai_symbol,
            llm_enabled=llm_enabled,
            provider=strategist_provider,
            model=strategist_model,
            timeout_seconds=strategist_timeout,
        )
        self.executor = ExecutorAgent(ai_symbol=ai_symbol)
        self.scout_timeout = scout_timeout
        self.strategist_timeout = strategist_timeout
        self.executor_timeout = executor_timeout
        self.total_timeout = total_timeout

    def execute_pipeline(self, game_state: GameState) -> AgentResult[MoveExecution]:
        """Execute the complete agent pipeline: Scout → Strategist → Executor.

        Orchestrates the three agents in sequence, passing outputs between them
        as typed domain models. Handles failures gracefully by returning error results.
        Enforces per-agent timeouts and total pipeline timeout.

        Args:
            game_state: Current game state to process

        Returns:
            AgentResult containing MoveExecution with the final result
        """
        pipeline_start_time = time.time()

        try:
            # Check total pipeline timeout before starting
            elapsed_time = time.time() - pipeline_start_time
            if elapsed_time >= self.total_timeout:
                execution_time = elapsed_time * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_code=E_LLM_TIMEOUT,
                    error_message=f"Pipeline exceeded total timeout of {self.total_timeout}s",
                    execution_time_ms=execution_time,
                )

            # Step 1: Scout analyzes the board (with timeout)
            remaining_timeout = self.total_timeout - elapsed_time
            scout_timeout = min(self.scout_timeout, remaining_timeout)
            scout_result = self._execute_with_timeout(
                self.scout.analyze, (game_state,), scout_timeout, "Scout"
            )

            # Handle Scout failure/timeout - use Fallback Rule Set 1
            fallback_metadata = {}
            board_analysis: BoardAnalysis | None = None
            if not scout_result.success or scout_result.data is None:
                # Fallback Rule Set 1: Use rule-based analysis (call Scout directly without timeout)
                board_analysis = self._fallback_rule_set_1_rule_based_analysis(game_state)
                if board_analysis is None:
                    execution_time = (time.time() - pipeline_start_time) * 1000
                    return AgentResult[MoveExecution](
                        success=False,
                        error_code=(
                            E_LLM_TIMEOUT
                            if "timeout" in (scout_result.error_message or "").lower()
                            else None
                        ),
                        error_message=f"Scout failed and fallback failed: {scout_result.error_message or 'unknown error'}",
                        execution_time_ms=execution_time,
                        metadata={"fallback_used": "rule_based_analysis"},
                    )
                fallback_metadata["fallback_used"] = "rule_based_analysis"
            else:
                board_analysis = scout_result.data

            # At this point, board_analysis is guaranteed to be not None
            if board_analysis is None:
                execution_time = (time.time() - pipeline_start_time) * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_message="Internal error: board_analysis is None",
                    execution_time_ms=execution_time,
                )

            # Check total pipeline timeout before continuing
            elapsed_time = time.time() - pipeline_start_time
            if elapsed_time >= self.total_timeout:
                execution_time = elapsed_time * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_code=E_LLM_TIMEOUT,
                    error_message=f"Pipeline exceeded total timeout of {self.total_timeout}s after Scout",
                    execution_time_ms=execution_time,
                )

            # Step 2: Strategist plans the move based on Scout's analysis (with timeout)
            remaining_timeout = self.total_timeout - elapsed_time
            strategist_timeout = min(self.strategist_timeout, remaining_timeout)
            strategist_result = self._execute_with_timeout(
                self.strategist.plan, (board_analysis,), strategist_timeout, "Strategist"
            )

            # Handle Strategist failure/timeout - use Fallback Rule Set 2
            strategy: Strategy | None = None
            if not strategist_result.success or strategist_result.data is None:
                # Fallback Rule Set 2: Select from BoardAnalysis opportunities/strategic_moves
                strategy = self._fallback_rule_set_2_scout_opportunity_fallback(board_analysis)
                if strategy is None:
                    execution_time = (time.time() - pipeline_start_time) * 1000
                    return AgentResult[MoveExecution](
                        success=False,
                        error_code=(
                            E_LLM_TIMEOUT
                            if "timeout" in (strategist_result.error_message or "").lower()
                            else None
                        ),
                        error_message=(
                            f"Strategist failed and fallback failed: {strategist_result.error_message or 'unknown error'}"
                        ),
                        execution_time_ms=execution_time,
                        metadata={**fallback_metadata, "fallback_used": "scout_opportunity"},
                    )
                fallback_metadata["fallback_used"] = "scout_opportunity"
            else:
                strategy = strategist_result.data

            # At this point, strategy is guaranteed to be not None
            if strategy is None:
                execution_time = (time.time() - pipeline_start_time) * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_message="Internal error: strategy is None",
                    execution_time_ms=execution_time,
                )

            # Check total pipeline timeout before continuing
            elapsed_time = time.time() - pipeline_start_time
            if elapsed_time >= self.total_timeout:
                execution_time = elapsed_time * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_code=E_LLM_TIMEOUT,
                    error_message=f"Pipeline exceeded total timeout of {self.total_timeout}s after Strategist",
                    execution_time_ms=execution_time,
                )

            # Step 3: Executor executes the move (with timeout)
            remaining_timeout = self.total_timeout - elapsed_time
            executor_timeout = min(self.executor_timeout, remaining_timeout)
            executor_result = self._execute_with_timeout(
                self.executor.execute, (game_state, strategy), executor_timeout, "Executor"
            )

            execution_time = (time.time() - pipeline_start_time) * 1000

            # Handle Executor failure/timeout - use Fallback Rule Set 3
            if (
                not executor_result.success
                or not executor_result.data
                or not executor_result.data.success
            ):
                # Fallback Rule Set 3: Use Strategy primary move or alternatives, or random valid move
                move_execution = self._fallback_rule_set_3_strategist_fallback(game_state, strategy)
                if move_execution is None:
                    return AgentResult[MoveExecution](
                        success=False,
                        error_code=(
                            E_LLM_TIMEOUT
                            if "timeout" in (executor_result.error_message or "").lower()
                            else None
                        ),
                        error_message=executor_result.error_message
                        or "Executor failed and fallback failed",
                        execution_time_ms=execution_time,
                        metadata={**fallback_metadata, "fallback_used": "strategist_primary"},
                    )
                return AgentResult[MoveExecution](
                    success=True,
                    data=move_execution,
                    execution_time_ms=execution_time,
                    metadata={**fallback_metadata, "fallback_used": "strategist_primary"},
                )

            # Executor succeeded
            return AgentResult[MoveExecution](
                success=True,
                data=executor_result.data,
                execution_time_ms=execution_time,
                metadata=fallback_metadata if fallback_metadata else None,
            )

        except Exception as e:
            execution_time = (time.time() - pipeline_start_time) * 1000
            return AgentResult[MoveExecution](
                success=False,
                error_message=f"Pipeline error: {str(e)}",
                execution_time_ms=execution_time,
            )

    # =========================================================================
    # 3.3.2: Timeout Configuration
    # =========================================================================

    def _execute_with_timeout(
        self,
        func: Callable[..., AgentResult[Any]],
        args: tuple[Any, ...],
        timeout: float,
        agent_name: str,
    ) -> AgentResult[Any]:
        """Execute an agent method with timeout.

        Args:
            func: The agent method to execute
            args: Arguments to pass to the function
            timeout: Timeout in seconds
            agent_name: Name of the agent (for error messages)

        Returns:
            AgentResult from the agent execution (generic type since it can be BoardAnalysis, Strategy, or MoveExecution)
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args)
            try:
                result = future.result(timeout=timeout)
                return result
            except FutureTimeoutError:
                # Return timeout error result
                return AgentResult[Any](
                    success=False,
                    error_code=E_LLM_TIMEOUT,
                    error_message=f"{agent_name} exceeded timeout of {timeout}s",
                    execution_time_ms=timeout * 1000,
                )

    # =========================================================================
    # 3.3.3: Fallback Strategy
    # =========================================================================

    def _fallback_rule_set_1_rule_based_analysis(
        self, game_state: GameState
    ) -> BoardAnalysis | None:
        """Fallback Rule Set 1: Generate rule-based BoardAnalysis when Scout fails.

        Uses Scout's rule-based analysis directly (without timeout wrapper).

        Args:
            game_state: Current game state

        Returns:
            BoardAnalysis from rule-based analysis, or None if analysis fails
        """
        try:
            # Call Scout's analyze directly (it's already rule-based, fast, no LLM)
            scout_result = self.scout.analyze(game_state)
            if scout_result.success and scout_result.data:
                return scout_result.data
            return None
        except Exception:
            return None

    def _fallback_rule_set_2_scout_opportunity_fallback(
        self, board_analysis: BoardAnalysis
    ) -> Strategy | None:
        """Fallback Rule Set 2: Select move from BoardAnalysis when Strategist fails.

        Selects highest priority opportunity (IMMEDIATE_WIN), then threats (BLOCK_THREAT),
        then strategic move, or first empty cell.

        Args:
            board_analysis: BoardAnalysis from Scout

        Returns:
            Strategy with selected move, or None if selection fails
        """
        try:
            # Priority 1: Select opportunity (always IMMEDIATE_WIN=100)
            if board_analysis.opportunities:
                # Sort by confidence (highest first), all opportunities are IMMEDIATE_WIN
                opportunities_sorted = sorted(
                    board_analysis.opportunities,
                    key=lambda opp: opp.confidence,
                    reverse=True,
                )
                selected_opp = opportunities_sorted[0]
                primary_move = MoveRecommendation(
                    position=selected_opp.position,
                    priority=MovePriority.IMMEDIATE_WIN,
                    confidence=selected_opp.confidence,
                    reasoning=f"Fallback: Using highest priority opportunity (IMMEDIATE_WIN, confidence={selected_opp.confidence})",
                )
                return Strategy(
                    primary_move=primary_move,
                    alternatives=[],
                    game_plan="Fallback: Using Scout opportunity analysis",
                    risk_assessment="medium",
                )

            # Priority 2: Select threat to block (BLOCK_THREAT=90)
            if board_analysis.threats:
                selected_threat = board_analysis.threats[0]  # All threats are critical
                primary_move = MoveRecommendation(
                    position=selected_threat.position,
                    priority=MovePriority.BLOCK_THREAT,
                    confidence=1.0,  # Critical threat, high confidence
                    reasoning="Fallback: Blocking threat (BLOCK_THREAT)",
                )
                return Strategy(
                    primary_move=primary_move,
                    alternatives=[],
                    game_plan="Fallback: Using Scout threat analysis",
                    risk_assessment="medium",
                )

            # Priority 3: Select highest priority strategic move
            if board_analysis.strategic_moves:
                strategic_sorted = sorted(
                    board_analysis.strategic_moves,
                    key=lambda sm: sm.priority,
                    reverse=True,
                )
                selected_strategic = strategic_sorted[0]
                # Map strategic move priority (1-10) to MovePriority
                # Center=10 -> CENTER_CONTROL=50, Corner=7 -> CORNER_CONTROL=40, Edge=4 -> EDGE_PLAY=30
                if selected_strategic.move_type == "center":
                    priority = MovePriority.CENTER_CONTROL
                elif selected_strategic.move_type == "corner":
                    priority = MovePriority.CORNER_CONTROL
                else:
                    priority = MovePriority.EDGE_PLAY
                primary_move = MoveRecommendation(
                    position=selected_strategic.position,
                    priority=priority,
                    confidence=0.7,  # Medium confidence for strategic moves
                    reasoning=f"Fallback: Using highest priority strategic move ({selected_strategic.move_type})",
                )
                return Strategy(
                    primary_move=primary_move,
                    alternatives=[],
                    game_plan="Fallback: Using Scout strategic position analysis",
                    risk_assessment="medium",
                )

            # Should not reach here if BoardAnalysis is valid, but return None as fallback
            return None
        except Exception:
            # Fallback failed - return None
            return None

    def _fallback_rule_set_3_strategist_fallback(
        self, game_state: GameState, strategy: Strategy
    ) -> MoveExecution | None:
        """Fallback Rule Set 3: Select move when Executor fails.

        Tries Strategy.primary_move, then alternatives, then random valid move.
        Validates that game is not over and cell is empty.

        Args:
            game_state: Current game state
            strategy: Strategy from Strategist

        Returns:
            MoveExecution with selected move, or None if all options fail
        """
        try:
            # Check if game is over (no valid moves if game is won or draw)
            winner = game_state._check_win()
            if winner is not None:
                # Game is already won
                return MoveExecution(
                    position=None,
                    success=False,
                    validation_errors=["E_GAME_ALREADY_OVER"],
                    execution_time_ms=0.0,
                    reasoning="Fallback: Game is already over, cannot make move",
                    actual_priority_used=None,
                )

            # Try Strategy.primary_move first
            if strategy.primary_move:
                pos = strategy.primary_move.position
                if 0 <= pos.row <= 2 and 0 <= pos.col <= 2 and game_state.board.is_empty(pos):
                    return MoveExecution(
                        position=pos,
                        success=True,
                        validation_errors=[],
                        execution_time_ms=0.0,
                        reasoning=f"Fallback: Using Strategy primary move at ({pos.row}, {pos.col})",
                        actual_priority_used=strategy.primary_move.priority,
                    )

            # Try alternatives
            if strategy.alternatives:
                for alt in strategy.alternatives:
                    pos = alt.position
                    if 0 <= pos.row <= 2 and 0 <= pos.col <= 2 and game_state.board.is_empty(pos):
                        return MoveExecution(
                            position=pos,
                            success=True,
                            validation_errors=[],
                            execution_time_ms=0.0,
                            reasoning=f"Fallback: Using Strategy alternative at ({pos.row}, {pos.col})",
                            actual_priority_used=alt.priority,
                        )

            # Last resort: Select random valid move (first empty cell in position order)
            empty_positions = game_state.board.get_empty_positions()
            if empty_positions:
                # Sort by position order (0,0 < 0,1 < ... < 2,2)
                empty_positions_sorted = sorted(empty_positions, key=lambda p: (p.row, p.col))
                selected_pos = empty_positions_sorted[0]
                return MoveExecution(
                    position=selected_pos,
                    success=True,
                    validation_errors=[],
                    execution_time_ms=0.0,
                    reasoning=f"Fallback: Using first available empty cell at ({selected_pos.row}, {selected_pos.col})",
                    actual_priority_used=MovePriority.RANDOM_VALID,
                )

            return None
        except Exception:
            return None
