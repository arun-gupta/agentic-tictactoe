"""Agent Pipeline Orchestration.

The pipeline coordinates the flow: Scout → Strategist → Executor
to produce a final move execution result.
"""

import time

from src.agents.executor import ExecutorAgent
from src.agents.scout import ScoutAgent
from src.agents.strategist import StrategistAgent
from src.domain.agent_models import BoardAnalysis, MoveExecution, Strategy
from src.domain.models import GameState, PlayerSymbol
from src.domain.result import AgentResult


class AgentPipeline:
    """Pipeline coordinator for orchestrating agent execution flow.

    Coordinates Scout → Strategist → Executor flow, passing typed domain
    models between agents and handling failures gracefully.
    """

    def __init__(self, ai_symbol: PlayerSymbol = "O") -> None:
        """Initialize the agent pipeline.

        Args:
            ai_symbol: The symbol this AI is playing as ('X' or 'O')
        """
        self.ai_symbol = ai_symbol
        self.scout = ScoutAgent(ai_symbol=ai_symbol)
        self.strategist = StrategistAgent(ai_symbol=ai_symbol)
        self.executor = ExecutorAgent(ai_symbol=ai_symbol)

    def execute_pipeline(self, game_state: GameState) -> AgentResult[MoveExecution]:
        """Execute the complete agent pipeline: Scout → Strategist → Executor.

        Orchestrates the three agents in sequence, passing outputs between them
        as typed domain models. Handles failures gracefully by returning error results.

        Args:
            game_state: Current game state to process

        Returns:
            AgentResult containing MoveExecution with the final result
        """
        pipeline_start_time = time.time()

        try:
            # Step 1: Scout analyzes the board
            scout_result = self.scout.analyze(game_state)
            if not scout_result.success or scout_result.data is None:
                execution_time = (time.time() - pipeline_start_time) * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_message=f"Scout failed: {scout_result.error_message or 'unknown error'}",
                    execution_time_ms=execution_time,
                )

            board_analysis: BoardAnalysis = scout_result.data

            # Step 2: Strategist plans the move based on Scout's analysis
            strategist_result = self.strategist.plan(board_analysis)
            if not strategist_result.success or strategist_result.data is None:
                execution_time = (time.time() - pipeline_start_time) * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_message=(
                        f"Strategist failed: {strategist_result.error_message or 'unknown error'}"
                    ),
                    execution_time_ms=execution_time,
                )

            strategy: Strategy = strategist_result.data

            # Step 3: Executor executes the move
            executor_result = self.executor.execute(game_state, strategy)
            execution_time = (time.time() - pipeline_start_time) * 1000

            # Return the executor's result (which contains MoveExecution)
            # If executor succeeded but returned MoveExecution, pass it through
            if executor_result.success and executor_result.data:
                return AgentResult[MoveExecution](
                    success=True,
                    data=executor_result.data,
                    execution_time_ms=execution_time,
                )
            elif executor_result.data:
                # Executor returned MoveExecution but with success=False
                # This is valid - it means validation or execution failed
                return AgentResult[MoveExecution](
                    success=True,  # Pipeline succeeded, but MoveExecution indicates failure
                    data=executor_result.data,
                    execution_time_ms=execution_time,
                )
            else:
                # Executor failed completely
                return AgentResult[MoveExecution](
                    success=False,
                    error_message=executor_result.error_message or "Executor failed",
                    execution_time_ms=execution_time,
                )

        except Exception as e:
            execution_time = (time.time() - pipeline_start_time) * 1000
            return AgentResult[MoveExecution](
                success=False,
                error_message=f"Pipeline error: {str(e)}",
                execution_time_ms=execution_time,
            )
