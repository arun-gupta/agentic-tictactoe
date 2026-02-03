"""Scout Agent - Board Analysis and Threat Detection.

The Scout Agent analyzes the game board to identify:
- Threats (opponent two-in-a-row with empty position)
- Opportunities (AI two-in-a-row with empty position)
- Strategic positions (center, corners, edges)
- Game phase (opening, midgame, endgame)

Phase 5 implementation: LLM-enhanced with Pydantic AI and fallback to rule-based.
"""

import logging
import time
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from typing import Literal

from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelRetry, UnexpectedModelBehavior

from src.agents.base import BaseAgent
from src.domain.agent_models import BoardAnalysis, Opportunity, StrategicMove, Threat
from src.domain.models import GameState, PlayerSymbol, Position
from src.domain.result import AgentResult
from src.llm.pydantic_ai_agents import create_scout_agent

GamePhase = Literal["opening", "midgame", "endgame"]

logger = logging.getLogger(__name__)


class ScoutAgent(BaseAgent):
    """Scout Agent for board analysis and threat detection.

    Uses LLM-enhanced analysis (Pydantic AI) with fallback to rule-based logic.
    Includes retry logic, timeout handling, and comprehensive error handling.
    """

    def __init__(
        self,
        ai_symbol: PlayerSymbol = "O",
        llm_enabled: bool = False,
        provider: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 15.0,
        max_retries: int = 3,
    ) -> None:
        """Initialize Scout Agent.

        Args:
            ai_symbol: The symbol this AI is playing as ('X' or 'O')
            llm_enabled: Whether to use LLM for analysis (defaults to False for backward compatibility)
            provider: LLM provider name (openai, anthropic, gemini). If None, uses first available.
            model: Model name. If None, uses first model from config for the provider.
            timeout_seconds: Timeout for LLM calls in seconds (default: 5.0)
            max_retries: Maximum number of retries on timeout (default: 3)
        """
        self.ai_symbol = ai_symbol
        self.opponent_symbol: PlayerSymbol = "X" if ai_symbol == "O" else "O"
        self.llm_enabled = llm_enabled
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        # Initialize Pydantic AI agent if LLM is enabled
        self._llm_agent: Agent[None, BoardAnalysis] | None = None
        if self.llm_enabled:
            try:
                self._llm_agent = create_scout_agent(provider, model)
                logger.info(
                    f"Scout LLM enabled with provider={provider}, model={model}, "
                    f"timeout={timeout_seconds}s, max_retries={max_retries}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Scout LLM agent: {e}. Falling back to rule-based."
                )
                self.llm_enabled = False
                self._llm_agent = None

    def analyze(self, game_state: GameState) -> AgentResult[BoardAnalysis]:
        """Analyze the game state and return board analysis.

        Uses LLM analysis if enabled, with fallback to rule-based on errors/timeout.
        Detects threats, opportunities, strategic positions, and evaluates board state.

        Args:
            game_state: Current game state to analyze

        Returns:
            AgentResult containing BoardAnalysis with all detected information
        """
        start_time = time.time()

        try:
            # Try LLM analysis if enabled
            if self.llm_enabled and self._llm_agent:
                try:
                    analysis = self._analyze_with_llm(game_state)
                    execution_time = (time.time() - start_time) * 1000
                    logger.info(f"Scout LLM analysis completed in {execution_time:.2f}ms")
                    return AgentResult[BoardAnalysis](
                        success=True,
                        data=analysis,
                        execution_time_ms=execution_time,
                    )
                except Exception as llm_error:
                    # Log LLM failure and fall back to rule-based
                    logger.warning(
                        f"Scout LLM analysis failed: {llm_error}. Falling back to rule-based analysis."
                    )

            # Fallback to rule-based analysis
            analysis = self._analyze_rule_based(game_state)

            execution_time = (time.time() - start_time) * 1000  # Convert to ms

            return AgentResult[BoardAnalysis](
                success=True,
                data=analysis,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Scout analysis failed completely: {e}")
            return AgentResult[BoardAnalysis](
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time,
            )

    def _analyze_with_llm(self, game_state: GameState) -> BoardAnalysis:
        """Analyze game state using Pydantic AI with retry logic.

        Args:
            game_state: Current game state to analyze

        Returns:
            BoardAnalysis from LLM

        Raises:
            TimeoutError: If LLM call exceeds timeout after all retries
            Exception: If LLM call fails with non-timeout error
        """
        # Build prompt with board state and game context
        prompt = self._build_llm_prompt(game_state)

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                llm_start = time.time()

                # Run LLM call with timeout using ThreadPoolExecutor
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self._llm_agent.run_sync, prompt)  # type: ignore[union-attr]
                    try:
                        result = future.result(timeout=self.timeout_seconds)
                    except FuturesTimeoutError as e:
                        raise TimeoutError(
                            f"LLM call timed out after {self.timeout_seconds}s"
                        ) from e

                llm_latency = (time.time() - llm_start) * 1000

                # Extract BoardAnalysis from result
                analysis: BoardAnalysis = result.output

                # Log LLM call metadata
                logger.info(
                    f"Scout LLM call metadata: "
                    f"attempt={attempt + 1}/{self.max_retries}, "
                    f"latency={llm_latency:.2f}ms, "
                    f"prompt_length={len(prompt)}"
                )

                return analysis

            except TimeoutError as timeout_err:
                wait_time = 2**attempt  # Exponential backoff: 1s, 2s, 4s
                logger.warning(
                    f"Scout LLM timeout (attempt {attempt + 1}/{self.max_retries}). "
                    f"Retrying in {wait_time}s..."
                )
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                else:
                    raise TimeoutError(
                        f"Scout LLM call timed out after {self.max_retries} retries "
                        f"(timeout: {self.timeout_seconds}s)"
                    ) from timeout_err

            except (ModelRetry, UnexpectedModelBehavior) as e:
                # Pydantic AI specific errors (parse errors, validation errors)
                logger.error(f"Scout LLM parse/validation error: {e}")
                raise Exception(f"LLM parse error: {e}") from e

            except Exception as e:
                # Authentication errors, API errors, etc.
                logger.error(f"Scout LLM call failed: {e}")
                raise

        # This should never be reached (all paths return or raise)
        raise RuntimeError("LLM analysis failed: no successful attempts")

    def _build_llm_prompt(self, game_state: GameState) -> str:
        """Build prompt for LLM with board state and game context.

        Args:
            game_state: Current game state

        Returns:
            Formatted prompt string
        """
        # Format board state
        board_lines = []
        for row in range(3):
            row_cells = []
            for col in range(3):
                cell = game_state.board.cells[row][col]
                if cell == "EMPTY":
                    row_cells.append(".")
                else:
                    row_cells.append(cell)
            board_lines.append(" ".join(row_cells))

        board_str = "\n".join(board_lines)

        prompt = f"""Analyze this Tic-Tac-Toe board state:

{board_str}

AI Symbol: {self.ai_symbol}
Opponent Symbol: {self.opponent_symbol}
Move Count: {game_state.move_count}
Current Player: {game_state.get_current_player()}

Provide a comprehensive board analysis including:

1. **Opportunities (AI Winning Moves)**: CRITICAL - Check ALL 8 lines (3 rows, 3 columns, 2 diagonals) for patterns where {self.ai_symbol} appears EXACTLY twice with one empty cell. These are IMMEDIATE WINNING MOVES for the AI. Each opportunity must specify:
   - position: The empty cell that completes the winning line
   - line_type: 'row', 'column', or 'diagonal'
   - line_index: Which row/column/diagonal (0-2)
   - confidence: 1.0 (immediate win)

2. **Threats (Opponent Winning Moves)**: Check ALL 8 lines for patterns where {self.opponent_symbol} appears EXACTLY twice with one empty cell. These are positions the AI MUST block. Each threat must specify:
   - position: The empty cell that would complete opponent's winning line
   - line_type: 'row', 'column', or 'diagonal'
   - line_index: Which row/column/diagonal (0-2)
   - severity: 'critical' (must block immediately)

3. Strategic positions: Available center, corner, and edge positions with priorities
4. Game phase: opening (0-2 moves), midgame (3-6 moves), or endgame (7-9 moves)
5. Board evaluation score: -1.0 (opponent winning) to 1.0 (AI winning)

IMPORTANT: Always check for BOTH opportunities AND threats. A position can be BOTH an opportunity (AI winning move) AND a threat blocker, but it should be listed in opportunities if the AI has two-in-a-row there.

Return a structured BoardAnalysis."""

        return prompt

    def _analyze_rule_based(self, game_state: GameState) -> BoardAnalysis:
        """Analyze game state using rule-based logic (fallback).

        Args:
            game_state: Current game state to analyze

        Returns:
            BoardAnalysis from rule-based logic
        """
        # Detect threats (opponent two-in-a-row)
        threats = self._detect_threats(game_state)

        # Detect opportunities (AI two-in-a-row)
        opportunities = self._detect_opportunities(game_state)

        # Analyze strategic positions (center, corners, edges)
        strategic_moves = self._analyze_strategic_positions(game_state)

        # Determine game phase
        game_phase = self._detect_game_phase(game_state)

        # Evaluate board position
        eval_score = self._evaluate_board(game_state, threats, opportunities)

        # Create board analysis
        return BoardAnalysis(
            threats=threats,
            opportunities=opportunities,
            strategic_moves=strategic_moves,
            game_phase=game_phase,
            board_evaluation_score=eval_score,
        )

    def _detect_threats(self, game_state: GameState) -> list[Threat]:
        """Detect opponent threats (two-in-a-row with empty position).

        Scans all 8 lines (3 rows, 3 cols, 2 diagonals) for opponent two-in-a-row
        patterns with one empty cell. Returns blocking positions.

        Args:
            game_state: Current game state

        Returns:
            List of Threat objects with blocking positions
        """
        threats: list[Threat] = []
        board = game_state.board

        # Check all 3 rows
        for row in range(3):
            line = [board.cells[row][col] for col in range(3)]
            if self._is_threat_line(line):
                # Find empty position in this row
                for col in range(3):
                    if board.cells[row][col] == "EMPTY":
                        threat = Threat(
                            position=Position(row=row, col=col),
                            line_type="row",
                            line_index=row,
                        )
                        threats.append(threat)
                        break

        # Check all 3 columns
        for col in range(3):
            line = [board.cells[row][col] for row in range(3)]
            if self._is_threat_line(line):
                # Find empty position in this column
                for row in range(3):
                    if board.cells[row][col] == "EMPTY":
                        threat = Threat(
                            position=Position(row=row, col=col),
                            line_type="column",
                            line_index=col,
                        )
                        threats.append(threat)
                        break

        # Check main diagonal (0,0 -> 1,1 -> 2,2)
        diag_main = [board.cells[i][i] for i in range(3)]
        if self._is_threat_line(diag_main):
            for i in range(3):
                if board.cells[i][i] == "EMPTY":
                    threat = Threat(
                        position=Position(row=i, col=i),
                        line_type="diagonal",
                        line_index=0,
                    )
                    threats.append(threat)
                    break

        # Check anti-diagonal (0,2 -> 1,1 -> 2,0)
        diag_anti = [board.cells[i][2 - i] for i in range(3)]
        if self._is_threat_line(diag_anti):
            for i in range(3):
                if board.cells[i][2 - i] == "EMPTY":
                    threat = Threat(
                        position=Position(row=i, col=2 - i),
                        line_type="diagonal",
                        line_index=1,
                    )
                    threats.append(threat)
                    break

        return threats

    def _is_threat_line(self, line: Sequence[str]) -> bool:
        """Check if a line contains a threat (opponent two-in-a-row + empty).

        Args:
            line: Sequence of 3 cell values

        Returns:
            True if line has exactly 2 opponent symbols and 1 empty
        """
        opponent_count = list(line).count(self.opponent_symbol)
        empty_count = list(line).count("EMPTY")
        return opponent_count == 2 and empty_count == 1

    def _detect_opportunities(self, game_state: GameState) -> list[Opportunity]:
        """Detect AI opportunities (two-in-a-row with empty position).

        Scans all 8 lines for AI two-in-a-row patterns with one empty cell.
        Returns winning positions with confidence=1.0 (immediate win).

        Args:
            game_state: Current game state

        Returns:
            List of Opportunity objects with winning positions
        """
        opportunities: list[Opportunity] = []
        board = game_state.board

        # Check all 3 rows
        for row in range(3):
            line = [board.cells[row][col] for col in range(3)]
            if self._is_opportunity_line(line):
                for col in range(3):
                    if board.cells[row][col] == "EMPTY":
                        opportunity = Opportunity(
                            position=Position(row=row, col=col),
                            line_type="row",
                            line_index=row,
                            confidence=1.0,  # Immediate win
                        )
                        opportunities.append(opportunity)
                        break

        # Check all 3 columns
        for col in range(3):
            line = [board.cells[row][col] for row in range(3)]
            if self._is_opportunity_line(line):
                for row in range(3):
                    if board.cells[row][col] == "EMPTY":
                        opportunity = Opportunity(
                            position=Position(row=row, col=col),
                            line_type="column",
                            line_index=col,
                            confidence=1.0,
                        )
                        opportunities.append(opportunity)
                        break

        # Check main diagonal
        diag_main = [board.cells[i][i] for i in range(3)]
        if self._is_opportunity_line(diag_main):
            for i in range(3):
                if board.cells[i][i] == "EMPTY":
                    opportunity = Opportunity(
                        position=Position(row=i, col=i),
                        line_type="diagonal",
                        line_index=0,
                        confidence=1.0,
                    )
                    opportunities.append(opportunity)
                    break

        # Check anti-diagonal
        diag_anti = [board.cells[i][2 - i] for i in range(3)]
        if self._is_opportunity_line(diag_anti):
            for i in range(3):
                if board.cells[i][2 - i] == "EMPTY":
                    opportunity = Opportunity(
                        position=Position(row=i, col=2 - i),
                        line_type="diagonal",
                        line_index=1,
                        confidence=1.0,
                    )
                    opportunities.append(opportunity)
                    break

        return opportunities

    def _is_opportunity_line(self, line: Sequence[str]) -> bool:
        """Check if a line contains an opportunity (AI two-in-a-row + empty).

        Args:
            line: Sequence of 3 cell values

        Returns:
            True if line has exactly 2 AI symbols and 1 empty
        """
        ai_count = list(line).count(self.ai_symbol)
        empty_count = list(line).count("EMPTY")
        return ai_count == 2 and empty_count == 1

    def _analyze_strategic_positions(self, game_state: GameState) -> list[StrategicMove]:
        """Analyze strategic positions (center, corners, edges).

        Identifies available strategic positions and assigns priorities:
        - Center (1,1): Highest priority
        - Corners (0,0), (0,2), (2,0), (2,2): Medium priority
        - Edges (0,1), (1,0), (1,2), (2,1): Lower priority

        Args:
            game_state: Current game state

        Returns:
            List of StrategicMove objects for empty strategic positions
        """
        strategic_moves: list[StrategicMove] = []
        board = game_state.board

        # Center position (1,1) - highest priority
        if board.cells[1][1] == "EMPTY":
            strategic_moves.append(
                StrategicMove(
                    position=Position(row=1, col=1),
                    move_type="center",
                    priority=10,
                    reasoning="Center position controls the most lines (4 total: 1 row, 1 column, 2 diagonals)",
                )
            )

        # Corner positions - medium priority
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        for row, col in corners:
            if board.cells[row][col] == "EMPTY":
                strategic_moves.append(
                    StrategicMove(
                        position=Position(row=row, col=col),
                        move_type="corner",
                        priority=7,
                        reasoning=f"Corner position ({row},{col}) controls 3 lines (1 row, 1 column, 1 diagonal)",
                    )
                )

        # Edge positions - lower priority
        edges = [(0, 1), (1, 0), (1, 2), (2, 1)]
        for row, col in edges:
            if board.cells[row][col] == "EMPTY":
                strategic_moves.append(
                    StrategicMove(
                        position=Position(row=row, col=col),
                        move_type="edge",
                        priority=4,
                        reasoning=f"Edge position ({row},{col}) controls 2 lines (1 row, 1 column)",
                    )
                )

        return strategic_moves

    def _detect_game_phase(self, game_state: GameState) -> GamePhase:
        """Determine current game phase based on move count.

        Args:
            game_state: Current game state

        Returns:
            'opening' (0-2 moves), 'midgame' (3-6 moves), or 'endgame' (7-9 moves)
        """
        move_count = game_state.move_count

        if move_count <= 2:
            return "opening"
        elif move_count <= 6:
            return "midgame"
        else:
            return "endgame"

    def _evaluate_board(
        self,
        game_state: GameState,
        threats: list[Threat],
        opportunities: list[Opportunity],
    ) -> float:
        """Evaluate board position from AI perspective.

        Returns a score between -1.0 and 1.0:
        - Positive: Favorable for AI
        - Negative: Favorable for opponent
        - Zero: Balanced

        Args:
            game_state: Current game state
            threats: Detected threats
            opportunities: Detected opportunities

        Returns:
            Evaluation score between -1.0 and 1.0
        """
        # Simple evaluation: opportunities - threats
        score = len(opportunities) * 0.3 - len(threats) * 0.3

        # Clamp to [-1.0, 1.0]
        return max(-1.0, min(1.0, score))
