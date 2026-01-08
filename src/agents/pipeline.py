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
from src.domain.agent_models import BoardAnalysis, MoveExecution, Strategy
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
        scout_timeout: float = 5.0,
        strategist_timeout: float = 3.0,
        executor_timeout: float = 2.0,
        total_timeout: float = 15.0,
    ) -> None:
        """Initialize the agent pipeline.

        Args:
            ai_symbol: The symbol this AI is playing as ('X' or 'O')
            scout_timeout: Timeout for Scout agent in seconds (default: 5.0)
            strategist_timeout: Timeout for Strategist agent in seconds (default: 3.0)
            executor_timeout: Timeout for Executor agent in seconds (default: 2.0)
            total_timeout: Total pipeline timeout in seconds (default: 15.0)
        """
        self.ai_symbol = ai_symbol
        self.scout = ScoutAgent(ai_symbol=ai_symbol)
        self.strategist = StrategistAgent(ai_symbol=ai_symbol)
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

            if not scout_result.success or scout_result.data is None:
                execution_time = (time.time() - pipeline_start_time) * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_code=(
                        E_LLM_TIMEOUT
                        if "timeout" in (scout_result.error_message or "").lower()
                        else None
                    ),
                    error_message=f"Scout failed: {scout_result.error_message or 'unknown error'}",
                    execution_time_ms=execution_time,
                )

            board_analysis: BoardAnalysis = scout_result.data

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

            if not strategist_result.success or strategist_result.data is None:
                execution_time = (time.time() - pipeline_start_time) * 1000
                return AgentResult[MoveExecution](
                    success=False,
                    error_code=(
                        E_LLM_TIMEOUT
                        if "timeout" in (strategist_result.error_message or "").lower()
                        else None
                    ),
                    error_message=(
                        f"Strategist failed: {strategist_result.error_message or 'unknown error'}"
                    ),
                    execution_time_ms=execution_time,
                )

            strategy: Strategy = strategist_result.data

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
                    error_code=(
                        E_LLM_TIMEOUT
                        if "timeout" in (executor_result.error_message or "").lower()
                        else None
                    ),
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

    # =========================================================================
    # 3.3.2: Timeout Configuration
    # =========================================================================

    def _execute_with_timeout(
        self, func: Callable[..., AgentResult[Any]], args: tuple, timeout: float, agent_name: str
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
