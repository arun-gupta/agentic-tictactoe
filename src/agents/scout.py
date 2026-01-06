"""Scout Agent - Board Analysis and Threat Detection.

The Scout Agent analyzes the game board to identify:
- Threats (opponent two-in-a-row with empty position)
- Opportunities (AI two-in-a-row with empty position)
- Strategic positions (center, corners, edges)
- Game phase (opening, midgame, endgame)

This is a rule-based implementation (Phase 3). LLM enhancement comes in Phase 5.
"""

import time
from collections.abc import Sequence
from typing import Literal

from src.agents.base import BaseAgent
from src.domain.agent_models import BoardAnalysis, Opportunity, StrategicMove, Threat
from src.domain.models import GameState, PlayerSymbol, Position
from src.domain.result import AgentResult

GamePhase = Literal["opening", "midgame", "endgame"]


class ScoutAgent(BaseAgent):
    """Scout Agent for board analysis and threat detection.

    Uses rule-based logic to scan the board for threats, opportunities,
    and strategic positions. Returns comprehensive BoardAnalysis.
    """

    def __init__(self, ai_symbol: PlayerSymbol = "O") -> None:
        """Initialize Scout Agent.

        Args:
            ai_symbol: The symbol this AI is playing as ('X' or 'O')
        """
        self.ai_symbol = ai_symbol
        self.opponent_symbol: PlayerSymbol = "X" if ai_symbol == "O" else "O"

    def analyze(self, game_state: GameState) -> AgentResult[BoardAnalysis]:
        """Analyze the game state and return board analysis.

        Detects threats, opportunities, strategic positions, and evaluates board state.

        Args:
            game_state: Current game state to analyze

        Returns:
            AgentResult containing BoardAnalysis with all detected information
        """
        start_time = time.time()

        try:
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
            analysis = BoardAnalysis(
                threats=threats,
                opportunities=opportunities,
                strategic_moves=strategic_moves,
                game_phase=game_phase,
                board_evaluation_score=eval_score,
            )

            execution_time = (time.time() - start_time) * 1000  # Convert to ms

            return AgentResult[BoardAnalysis](
                success=True,
                data=analysis,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return AgentResult[BoardAnalysis](
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time,
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
