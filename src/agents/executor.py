"""Executor Agent - Move Execution and Validation.

The Executor Agent executes moves recommended by the Strategist:
- Validates recommended moves (position bounds, cell empty, game not over)
- Executes moves via GameEngine
- Handles fallbacks (alternatives, random valid move)
- Returns MoveExecution with success status and metadata

This is a rule-based implementation (Phase 3). LLM enhancement comes in Phase 5.
"""

import time

from src.agents.base import BaseAgent
from src.domain.agent_models import (
    MoveExecution,
    MoveRecommendation,
    Strategy,
)
from src.domain.errors import (
    E_CELL_OCCUPIED,
    E_GAME_ALREADY_OVER,
    E_MOVE_OUT_OF_BOUNDS,
)
from src.domain.models import GameState, PlayerSymbol
from src.domain.result import AgentResult


class ExecutorAgent(BaseAgent):
    """Executor Agent for move execution and validation.

    Validates and executes moves recommended by the Strategist agent,
    with fallback handling for failed moves.
    """

    def __init__(self, ai_symbol: PlayerSymbol = "O") -> None:
        """Initialize Executor Agent.

        Args:
            ai_symbol: The symbol this AI is playing as ('X' or 'O')
        """
        self.ai_symbol = ai_symbol

    def analyze(self, game_state: object) -> object:
        """Not used - Executor uses execute() instead of analyze().

        This satisfies BaseAgent interface but Executor receives
        Strategy from Strategist, not GameState.
        """
        raise NotImplementedError("Executor uses execute() method instead")

    def execute(self, game_state: GameState, strategy: Strategy) -> AgentResult[MoveExecution]:
        """Execute the recommended move from Strategist.

        Validates the move, executes it if valid, handles fallbacks,
        and returns MoveExecution with success status.

        Args:
            game_state: Current game state
            strategy: Strategy from Strategist agent containing move recommendations

        Returns:
            AgentResult containing MoveExecution with execution result
        """
        start_time = time.time()

        try:
            # 3.2.1: Move Validation (IMPLEMENTING NOW)
            validation_errors = self._validate_move(game_state, strategy.primary_move)

            # If validation fails, return error result (execution happens in 3.2.2)
            if validation_errors:
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                return AgentResult[MoveExecution](
                    success=False,
                    data=MoveExecution(
                        position=None,
                        success=False,
                        validation_errors=validation_errors,
                        execution_time_ms=execution_time,
                        reasoning=f"Move validation failed: {', '.join(validation_errors)}",
                    ),
                    execution_time_ms=execution_time,
                )

            # 3.2.2: Move Execution (TODO)
            # 3.2.3: Fallback Handling (TODO)

            # Temporary return for 3.2.1 only
            execution_time = (time.time() - start_time) * 1000
            return AgentResult[MoveExecution](
                success=False,
                error_message="Move execution (3.2.2) not yet implemented",
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentResult[MoveExecution](
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time,
            )

    # =========================================================================
    # 3.2.1: Move Validation
    # =========================================================================

    def _validate_move(
        self, game_state: GameState, move_recommendation: MoveRecommendation
    ) -> list[str]:
        """Validate a move recommendation from Strategist.

        Checks position bounds, cell emptiness, and game over status.
        Collects all validation errors.

        Args:
            game_state: Current game state
            move_recommendation: MoveRecommendation from Strategist

        Returns:
            List of error codes. Empty list if move is valid.
        """
        errors: list[str] = []
        position = move_recommendation.position

        # Check 1: Position is within bounds (0-2 for both row and col)
        # This check happens first before accessing the board
        if not (0 <= position.row <= 2) or not (0 <= position.col <= 2):
            errors.append(E_MOVE_OUT_OF_BOUNDS)
            # Don't check cell emptiness if bounds are invalid
            return errors

        # Check 2: Cell is empty (only if bounds are valid)
        try:
            if not game_state.board.is_empty(position):
                errors.append(E_CELL_OCCUPIED)
        except ValueError:
            # If get_cell raises bounds error, we already caught it above
            # This shouldn't happen, but handle it defensively
            if E_MOVE_OUT_OF_BOUNDS not in errors:
                errors.append(E_MOVE_OUT_OF_BOUNDS)

        # Check 3: Game is not over
        if game_state.is_game_over():
            errors.append(E_GAME_ALREADY_OVER)

        return errors
