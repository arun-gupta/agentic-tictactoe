#!/usr/bin/env python3
"""Human vs Agent Tic-Tac-Toe game demo.

This script demonstrates the complete Phase 3 Rule-based Agent System by allowing
a human player to play against rule-based agents using the Agent Pipeline:
- Scout Agent: Rule-based board analysis (threats, opportunities, strategic positions)
- Strategist Agent: Priority-based move selection using rule-based logic
- Executor Agent: Move validation and execution with fallback strategies

With --llm flag (Phase 5):
- Scout Agent: LLM-enhanced board analysis with strategic insights
- Strategist Agent: LLM-based move selection with reasoning
- Executor Agent: Rule-based validation (no LLM, kept fast)

Note: Without --llm flag, uses rule-based agents only.
"""

import argparse
import random
import sys
from typing import Literal

from src.agents.pipeline import AgentPipeline
from src.agents.scout import ScoutAgent
from src.config.llm_config import get_llm_config
from src.domain.agent_models import BoardAnalysis, MoveExecution
from src.domain.models import GameState, Position
from src.domain.result import AgentResult
from src.game.engine import GameEngine


def print_board(engine: GameEngine) -> None:
    """Print the current board state in a nice format."""
    state = engine.get_current_state()
    board = state.board

    print("\n  0   1   2")
    for row in range(3):
        print(f"{row} ", end="")
        for col in range(3):
            cell = board.cells[row][col]
            if cell == "EMPTY":
                print(".", end="")
            else:
                print(cell, end="")
            if col < 2:
                print(" | ", end="")
        print()
        if row < 2:
            print("  -----------")
    print()


def print_game_status(engine: GameEngine) -> None:
    """Print current game status."""
    state = engine.get_current_state()
    print(f"Move #{state.move_count} | Current Player: {state.get_current_player()}")
    print(f"Available moves: {len(engine.get_available_moves())}")


def print_ai_analysis(
    pipeline_result: AgentResult[MoveExecution],
    game_state: GameState,
    scout: ScoutAgent,
    verbose: bool = False,
) -> None:
    """Print AI analysis and reasoning.

    Args:
        pipeline_result: Result from AgentPipeline.execute_pipeline()
        game_state: Current game state
        scout: ScoutAgent instance to get detailed analysis
        verbose: If True, show detailed analysis
    """
    if not pipeline_result.success or not pipeline_result.data:
        print("⚠️  AI failed to generate move")
        if pipeline_result.error_message:
            print(f"   Error: {pipeline_result.error_message}")
        return

    execution = pipeline_result.data
    if not execution.success or not execution.position:
        print("⚠️  AI move execution failed")
        if execution.reasoning:
            print(f"   {execution.reasoning}")
        return

    pos = execution.position
    print(f"🤖 AI plays at ({pos.row}, {pos.col})")

    if execution.actual_priority_used:
        priority_name = (
            execution.actual_priority_used.name
            if hasattr(execution.actual_priority_used, "name")
            else str(execution.actual_priority_used)
        )
        print(f"   Priority: {priority_name}")

    if verbose:
        # Show detailed Scout analysis
        scout_result = scout.analyze(game_state)
        if scout_result.success and scout_result.data:
            analysis: BoardAnalysis = scout_result.data
            print("\n   📊 Scout Analysis:")
            print(f"      Game Phase: {analysis.game_phase}")
            print(f"      Board Evaluation: {analysis.board_evaluation_score:.2f}")

            if analysis.threats:
                print(f"      ⚠️  Threats detected: {len(analysis.threats)}")
                for threat in analysis.threats[:2]:  # Show first 2
                    print(f"         - Threat at ({threat.position.row}, {threat.position.col})")

            if analysis.opportunities:
                print(f"      ✅ Opportunities: {len(analysis.opportunities)}")
                for opp in analysis.opportunities[:2]:  # Show first 2
                    print(
                        f"         - Opportunity at ({opp.position.row}, {opp.position.col}), "
                        f"confidence: {opp.confidence:.2f}"
                    )

            if analysis.strategic_moves:
                print(f"      🎯 Strategic positions: {len(analysis.strategic_moves)}")
                for sm in analysis.strategic_moves[:2]:  # Show first 2
                    print(
                        f"         - {sm.move_type} at ({sm.position.row}, {sm.position.col}), "
                        f"priority: {sm.priority}"
                    )

        if execution.reasoning:
            print(f"\n   💭 Reasoning: {execution.reasoning}")

        exec_time = pipeline_result.execution_time_ms
        print(f"\n   ⏱️  Pipeline time: {exec_time:.2f}ms")

        if pipeline_result.metadata and pipeline_result.metadata.get("fallback_used"):
            print(f"   ⚠️  Fallback used: {pipeline_result.metadata['fallback_used']}")


def get_human_move(engine: GameEngine) -> tuple[int, int] | None:
    """Get move from human player via input."""
    available = engine.get_available_moves()
    if not available:
        return None

    print("\nYour turn! Enter row and column (0-2), or 'q' to quit:")
    while True:
        try:
            user_input = input("Enter move (row,col or 'q'): ").strip().lower()
            if user_input == "q":
                return None

            parts = user_input.split(",")
            if len(parts) != 2:
                print("Invalid format. Use: row,col (e.g., 0,1)")
                continue

            row = int(parts[0].strip())
            col = int(parts[1].strip())

            # Validate bounds
            if not (0 <= row <= 2) or not (0 <= col <= 2):
                print("Row and column must be between 0 and 2")
                continue

            # Check if move is valid
            state = engine.get_current_state()
            if not state.board.is_empty(Position(row=row, col=col)):
                print("That cell is already occupied!")
                continue

            return (row, col)

        except ValueError:
            print("Invalid input. Enter two numbers separated by comma (e.g., 0,1)")
        except KeyboardInterrupt:
            print("\n\nGame cancelled by user")
            return None


def simulate_human_move(engine: GameEngine) -> tuple[int, int] | None:
    """Simulate a human move (random valid move for demo purposes)."""
    available = engine.get_available_moves()
    if not available:
        return None

    pos = random.choice(available)
    return (pos.row, pos.col)


def main() -> None:
    """Run a human vs AI game."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Play Tic-Tac-Toe against AI agents")
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Enable LLM-enhanced agents (Phase 5)",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["1", "2"],
        help="Game mode: 1=Interactive, 2=Simulation",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed AI analysis",
    )

    args = parser.parse_args()
    llm_enabled = args.llm
    mode: Literal["1", "2"] | None = args.mode
    verbose = args.verbose

    # Display header
    print("=" * 60)
    if llm_enabled:
        print("TIC-TAC-TOE: Human vs Agent (LLM-Enhanced)")
    else:
        print("TIC-TAC-TOE: Human vs Agent (Rule-based Agent System)")
    print("=" * 60)

    if llm_enabled:
        print("\nDemonstrating Phase 5: LLM Integration")
        print("- Scout Agent: LLM-enhanced board analysis")
        print("- Strategist Agent: LLM-based move selection")
        print("- Executor Agent: Rule-based validation (no LLM)")
        print("- Agent Pipeline: Complete orchestration with timeouts and fallbacks")

        # Display LLM configuration
        llm_config = get_llm_config()
        scout_config = llm_config.get_agent_config("scout")
        strategist_config = llm_config.get_agent_config("strategist")

        print("\nLLM Configuration:")
        print(f"  Scout Provider: {scout_config.provider}")
        print(f"  Scout Model: {scout_config.model}")
        print(f"  Strategist Provider: {strategist_config.provider}")
        print(f"  Strategist Model: {strategist_config.model}\n")
    else:
        print("\nDemonstrating Phase 3: Rule-based Agent System")
        print(
            "Note: Uses rule-based agents (not LLM-based AI). Use --llm flag for LLM integration."
        )
        print("- Scout Agent: Board analysis and threat detection")
        print("- Strategist Agent: Move selection with priority system")
        print("- Executor Agent: Move execution with validation")
        print("- Agent Pipeline: Complete orchestration with timeouts and fallbacks\n")

    # If no mode specified via arguments, always try to prompt (default to interactive for Human vs Agent)
    if mode is None:
        try:
            print("Game Mode:")
            print("1. Interactive (you make moves)")
            print("2. Simulation (both players use AI/random)")
            mode_input = input("Select mode (1 or 2, default=1): ").strip()
            mode = mode_input if mode_input in ("1", "2") else "1"  # type: ignore[assignment]

            if mode == "1":
                verbose_input = (
                    input("Show detailed AI analysis? (y/n, default=n): ").strip().lower()
                )
                verbose = verbose_input == "y"
        except (EOFError, KeyboardInterrupt):
            # If stdin is not available or interrupted, default to simulation mode
            mode = "2"
            verbose = False
            print("\nNo input available. Running in Simulation mode.\n")

    interactive = mode == "1"

    # Initialize game engine and AI pipeline
    engine = GameEngine(player_symbol="X", ai_symbol="O")
    ai_pipeline = AgentPipeline(ai_symbol="O")
    scout = ScoutAgent(ai_symbol="O")  # For detailed analysis display

    print("\n" + "=" * 60)
    print("GAME START")
    print("=" * 60)
    print("\nPlayer (X) vs AI (O)")

    if llm_enabled:
        print(
            "\n⚠️  Note: LLM configuration validated, but agent LLM integration not yet implemented."
        )
        print("    Agents will use rule-based logic until subsection 5.3+ is complete.")
        print("    This demo validates the LLM configuration infrastructure.")

    print_board(engine)
    print_game_status(engine)

    move_count = 0
    max_moves = 9

    while move_count < max_moves and not engine.is_game_over():
        state = engine.get_current_state()
        current_player = state.get_current_player()

        if current_player == "X":
            # Human/Player turn
            print("\n" + "-" * 60)
            print(f"Move {move_count + 1}: PLAYER (X) TURN")
            print("-" * 60)

            if interactive:
                move = get_human_move(engine)
                if move is None:
                    print("\nGame cancelled.")
                    return
                row, col = move
            else:
                # Simulate player move (random)
                move = simulate_human_move(engine)
                if move is None:
                    break
                row, col = move
                print(f"Player (X) plays at ({row}, {col}) [random]")

            # Execute player move
            success, error = engine.make_move(row, col, "X")
            if not success:
                print(f"❌ MOVE FAILED: {error}")
                continue

            print("✓ Move successful")
            print_board(engine)

        else:
            # AI turn
            print("\n" + "-" * 60)
            print(f"Move {move_count + 1}: AI (O) TURN")
            print("-" * 60)
            print("🤖 AI is thinking...")

            # Get current game state for AI
            current_state = engine.get_current_state()

            # Execute AI pipeline
            pipeline_result = ai_pipeline.execute_pipeline(current_state)

            # Print AI analysis
            print_ai_analysis(pipeline_result, current_state, scout, verbose=verbose)

            if (
                not pipeline_result.success
                or not pipeline_result.data
                or not pipeline_result.data.success
            ):
                print("❌ AI failed to make a move")
                print(f"   Error: {pipeline_result.error_message or 'Unknown error'}")
                break

            execution = pipeline_result.data
            if not execution.position:
                print("❌ AI did not provide a valid position")
                break

            pos = execution.position

            # Execute AI move
            success, error = engine.make_move(pos.row, pos.col, "O")
            if not success:
                print(f"❌ AI MOVE FAILED: {error}")
                break

            print("✓ AI move successful")
            print_board(engine)

        move_count += 1

        # Check for win
        winner = engine.check_winner()
        if winner:
            print("\n" + "=" * 60)
            if winner == "X":
                print("🎉 GAME OVER: PLAYER (X) WINS!")
            else:
                print("🎉 GAME OVER: AI (O) WINS!")
            print("=" * 60)
            print("\nFinal Stats:")
            print(f"- Total moves: {engine.get_current_state().move_count}")
            print(f"- Winner: {winner}")

            # Validate final state
            is_valid, error = engine.validate_state()
            print(f"- State validation: {'✓ VALID' if is_valid else f'✗ INVALID ({error})'}")
            break

        # Check for draw
        if engine.check_draw():
            print("\n" + "=" * 60)
            print("🤝 GAME OVER: DRAW!")
            print("=" * 60)
            print("\nFinal Stats:")
            print(f"- Total moves: {engine.get_current_state().move_count}")
            print("- Result: Draw")
            break

        print_game_status(engine)

    # Show API capabilities demonstrated
    print("\n" + "=" * 60)
    print("PHASE 3 CAPABILITIES DEMONSTRATED:")
    print("=" * 60)
    print("✓ AgentPipeline.execute_pipeline() - Complete agent orchestration")
    print("✓ Scout Agent - Board analysis, threat/opportunity detection")
    print("✓ Strategist Agent - Priority-based move selection")
    print("✓ Executor Agent - Move validation and execution")
    print("✓ Fallback strategies - Handles timeouts and failures gracefully")
    print("✓ MoveExecution - Complete move metadata and reasoning")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame cancelled by user")
        sys.exit(0)
