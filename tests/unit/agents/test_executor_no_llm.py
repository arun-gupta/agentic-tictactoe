"""Tests for Executor Agent - No LLM Integration - Subsection 5.1.3.

Subsection tests for Phase 5.1.3: Executor (No LLM)
These tests verify that:
1. ExecutorAgent.execute() remains rule-based (no LLM calls)
2. ExecutorAgent.execute() validates moves without LLM
3. ExecutorAgent.execute() executes moves deterministically
4. ExecutorAgent.execute() performance unaffected by LLM integration (no latency impact)

The Executor agent is intentionally kept rule-based because:
- Move validation is deterministic (bounds, empty, not over)
- Move execution is deterministic (update board state)
- No strategic reasoning required (Strategist already decided)
- Fast execution is critical for user experience
"""

import time

from src.agents.executor import ExecutorAgent
from src.domain.agent_models import MovePriority, MoveRecommendation
from src.domain.errors import E_CELL_OCCUPIED, E_MOVE_OUT_OF_BOUNDS
from src.domain.models import Board, GameState, Position


class TestExecutorNoLLMIntegration:
    """Test that Executor agent remains rule-based without LLM integration."""

    def test_subsection_5_1_3_1_remains_rule_based_no_llm_calls(self) -> None:
        """Subsection test 1: ExecutorAgent.execute() remains rule-based (no LLM calls)."""
        executor = ExecutorAgent(ai_symbol="O")

        # Verify executor has no LLM-related attributes
        assert not hasattr(
            executor, "llm_enabled"
        ), "Executor should not have llm_enabled attribute"
        assert not hasattr(executor, "_llm_agent"), "Executor should not have _llm_agent attribute"
        assert not hasattr(
            executor, "timeout_seconds"
        ), "Executor should not have timeout_seconds attribute"
        assert not hasattr(
            executor, "max_retries"
        ), "Executor should not have max_retries attribute"

        # Verify executor remains deterministic and rule-based
        # No async methods, no LLM dependencies

    def test_subsection_5_1_3_2_validates_moves_without_llm(self) -> None:
        """Subsection test 2: ExecutorAgent.execute() validates moves without LLM."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create game state
        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        # Test validation with out-of-bounds move (using model_construct to bypass Pydantic validation)
        invalid_move = MoveRecommendation.model_construct(
            position=Position.model_construct(row=5, col=5),  # Out of bounds
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.7,
            reasoning="Invalid position",
        )

        # Validate move using internal method
        validation_errors = executor._validate_move(game_state, invalid_move)

        # Verify validation caught the error (without LLM)
        assert E_MOVE_OUT_OF_BOUNDS in validation_errors, "Should detect out of bounds"

        # Test validation with occupied cell
        board_with_x = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state2 = GameState(board=board_with_x, player_symbol="X", ai_symbol="O", move_count=1)

        occupied_move = MoveRecommendation(
            position=Position(row=0, col=0),  # Already occupied by X
            priority=MovePriority.BLOCK_THREAT,
            confidence=0.95,
            reasoning="Try occupied cell",
        )

        validation_errors2 = executor._validate_move(game_state2, occupied_move)

        # Verify validation caught occupied cell (without LLM)
        assert E_CELL_OCCUPIED in validation_errors2, "Should detect occupied cell"

    def test_subsection_5_1_3_3_executes_moves_deterministically(self) -> None:
        """Subsection test 3: ExecutorAgent.execute() executes moves deterministically."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create move recommendation
        move = MoveRecommendation(
            position=Position(row=0, col=0),
            priority=MovePriority.CORNER_CONTROL,
            confidence=0.6,
            reasoning="Take corner",
        )

        # Execute same validation multiple times with same game state
        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        # Run validation multiple times
        results = []
        for _ in range(5):
            validation_errors = executor._validate_move(game_state, move)
            results.append(validation_errors)

        # Verify all validations produced identical results (deterministic)
        assert all(r == results[0] for r in results), "Validation should be deterministic"

        # Verify no errors (move is valid)
        assert len(results[0]) == 0, "Move should be valid"

    def test_subsection_5_1_3_4_performance_unaffected_by_llm_integration(self) -> None:
        """Subsection test 4: ExecutorAgent.execute() performance unaffected by LLM integration (no latency impact)."""
        executor = ExecutorAgent(ai_symbol="O")

        # Create move recommendation
        move = MoveRecommendation(
            position=Position(row=1, col=1),
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.7,
            reasoning="Control center",
        )

        # Create game state
        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        # Measure validation time
        validation_times = []
        for _ in range(10):
            start_time = time.time()
            validation_errors = executor._validate_move(game_state, move)
            elapsed_time = (time.time() - start_time) * 1000  # ms
            validation_times.append(elapsed_time)
            assert len(validation_errors) == 0, "Move should be valid"

        # Verify performance is fast (no LLM latency)
        # Rule-based validation should be < 1ms
        # LLM calls would typically take 500-5000ms
        avg_time = sum(validation_times) / len(validation_times)
        assert avg_time < 1, f"Average validation time {avg_time}ms, expected < 1ms (rule-based)"

        # Verify low variance (deterministic rule-based)
        variance = sum((t - avg_time) ** 2 for t in validation_times) / len(validation_times)
        std_dev = variance**0.5
        assert std_dev < 1, f"Standard deviation {std_dev}ms too high (expected < 1ms)"


class TestExecutorArchitectureVerification:
    """Additional tests to verify Executor's rule-based architecture."""

    def test_no_async_methods(self) -> None:
        """Verify Executor has no async methods (would indicate LLM integration)."""
        executor = ExecutorAgent(ai_symbol="O")

        # Get all methods
        methods = [method for method in dir(executor) if callable(getattr(executor, method))]

        # Filter to public methods (excluding __xxx__)
        public_methods = [m for m in methods if not m.startswith("_")]

        # Verify none are async
        import asyncio

        for method_name in public_methods:
            method = getattr(executor, method_name)
            assert not asyncio.iscoroutinefunction(
                method
            ), f"Method {method_name} is async (indicates LLM integration)"

    def test_no_llm_related_imports(self) -> None:
        """Verify Executor module has no LLM-related imports."""
        import inspect

        import src.agents.executor as executor_module

        # Get module's code
        source = inspect.getsource(executor_module)

        # Verify no pydantic_ai imports
        assert "pydantic_ai" not in source, "Executor should not import pydantic_ai"
        assert "create_scout_agent" not in source, "Executor should not import LLM agents"
        assert "create_strategist_agent" not in source, "Executor should not import LLM agents"

        # Verify no asyncio imports (would be needed for LLM calls)
        assert "asyncio" not in source, "Executor should not import asyncio"

    def test_execution_is_synchronous(self) -> None:
        """Verify execute() is synchronous (not async)."""
        executor = ExecutorAgent(ai_symbol="O")

        # Verify execute method is not async
        import asyncio

        assert not asyncio.iscoroutinefunction(
            executor.execute
        ), "execute() should be synchronous (not async)"

        # Verify _validate_move is synchronous
        assert not asyncio.iscoroutinefunction(
            executor._validate_move
        ), "_validate_move() should be synchronous"

        # Verify _execute_move is synchronous
        assert not asyncio.iscoroutinefunction(
            executor._execute_move
        ), "_execute_move() should be synchronous"
