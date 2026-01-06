"""Tests for Scout Agent - Board Analysis and Threat Detection.

Tests AC-3.1.1 through AC-3.1.10 - Scout Agent functionality
"""

from src.agents.scout import ScoutAgent
from src.domain.models import Board, GameState, Position


class TestThreatDetection:
    """Test threat detection (opponent two-in-a-row)."""

    def test_ac_3_1_1_detects_row_threat(self) -> None:
        """AC-3.1.1: Detects opponent two-in-a-row and returns blocking position."""
        scout = ScoutAgent(ai_symbol="O")

        # X | X | EMPTY
        # . | . | .
        # . | . | .
        board = Board(
            cells=[
                ["X", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)

        assert result.success
        assert result.data is not None
        analysis = result.data

        # Should detect threat in row 0
        assert len(analysis.threats) == 1
        threat = analysis.threats[0]
        assert threat.position == Position(row=0, col=2)
        assert threat.line_type == "row"
        assert threat.line_index == 0

    def test_detects_column_threat(self) -> None:
        """Detects opponent two-in-a-row in column."""
        scout = ScoutAgent(ai_symbol="O")

        # X | . | .
        # X | . | .
        # EMPTY | . | .
        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert len(analysis.threats) == 1
        threat = analysis.threats[0]
        assert threat.position == Position(row=2, col=0)
        assert threat.line_type == "column"
        assert threat.line_index == 0

    def test_detects_diagonal_threat(self) -> None:
        """Detects opponent two-in-a-row on main diagonal."""
        scout = ScoutAgent(ai_symbol="O")

        # X | . | .
        # . | X | .
        # . | . | EMPTY
        board = Board(
            cells=[
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert len(analysis.threats) == 1
        threat = analysis.threats[0]
        assert threat.position == Position(row=2, col=2)
        assert threat.line_type == "diagonal"
        assert threat.line_index == 0

    def test_detects_anti_diagonal_threat(self) -> None:
        """Detects opponent two-in-a-row on anti-diagonal."""
        scout = ScoutAgent(ai_symbol="O")

        # . | . | X
        # . | X | .
        # EMPTY | . | .
        board = Board(
            cells=[
                ["EMPTY", "EMPTY", "X"],
                ["EMPTY", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert len(analysis.threats) == 1
        threat = analysis.threats[0]
        assert threat.position == Position(row=2, col=0)
        assert threat.line_type == "diagonal"
        assert threat.line_index == 1

    def test_detects_multiple_threats(self) -> None:
        """Detects multiple threats on the board."""
        scout = ScoutAgent(ai_symbol="O")

        # X | X | EMPTY  <- threat in row 0
        # X | . | .
        # X | . | .      <- threat in column 0
        board = Board(
            cells=[
                ["X", "X", "EMPTY"],
                ["X", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=3)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        # Should detect threats in row 0 and column 0
        assert len(analysis.threats) == 2

    def test_no_threats_on_empty_board(self) -> None:
        """No threats detected on empty board."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert len(analysis.threats) == 0


class TestOpportunityDetection:
    """Test opportunity detection (AI two-in-a-row)."""

    def test_ac_3_1_2_detects_ai_opportunity(self) -> None:
        """AC-3.1.2: Detects AI two-in-a-row and returns winning position."""
        scout = ScoutAgent(ai_symbol="O")

        # O | O | EMPTY
        # . | . | .
        # . | . | .
        board = Board(
            cells=[
                ["O", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        # Should detect opportunity in row 0
        assert len(analysis.opportunities) == 1
        opportunity = analysis.opportunities[0]
        assert opportunity.position == Position(row=0, col=2)
        assert opportunity.line_type == "row"
        assert opportunity.line_index == 0
        assert opportunity.confidence == 1.0  # Immediate win

    def test_detects_column_opportunity(self) -> None:
        """Detects AI two-in-a-row in column."""
        scout = ScoutAgent(ai_symbol="O")

        # . | O | .
        # . | O | .
        # . | EMPTY | .
        board = Board(
            cells=[
                ["EMPTY", "O", "EMPTY"],
                ["EMPTY", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert len(analysis.opportunities) == 1
        opportunity = analysis.opportunities[0]
        assert opportunity.position == Position(row=2, col=1)
        assert opportunity.confidence == 1.0

    def test_detects_diagonal_opportunity(self) -> None:
        """Detects AI two-in-a-row on diagonal."""
        scout = ScoutAgent(ai_symbol="O")

        # O | . | .
        # . | O | .
        # . | . | EMPTY
        board = Board(
            cells=[
                ["O", "EMPTY", "EMPTY"],
                ["EMPTY", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert len(analysis.opportunities) == 1
        opportunity = analysis.opportunities[0]
        assert opportunity.position == Position(row=2, col=2)
        assert opportunity.line_type == "diagonal"

    def test_no_opportunities_on_empty_board(self) -> None:
        """No opportunities detected on empty board."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert len(analysis.opportunities) == 0


class TestGamePhaseDetection:
    """Test game phase detection."""

    def test_ac_3_1_4_opening_phase(self) -> None:
        """AC-3.1.4: Detects opening phase (0-2 moves)."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert analysis.game_phase == "opening"

    def test_opening_phase_two_moves(self) -> None:
        """Opening phase with 2 moves."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board(
            cells=[
                ["X", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        assert result.data.game_phase == "opening"

    def test_ac_3_1_5_midgame_phase(self) -> None:
        """AC-3.1.5: Detects midgame phase (3-6 moves)."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=4)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert analysis.game_phase == "midgame"

    def test_ac_3_1_6_endgame_phase(self) -> None:
        """AC-3.1.6: Detects endgame phase (7-9 moves)."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=8)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert analysis.game_phase == "endgame"


class TestBoardEvaluation:
    """Test board evaluation scoring."""

    def test_ac_3_1_9_favorable_ai_position(self) -> None:
        """AC-3.1.9: Favorable AI position returns positive score."""
        scout = ScoutAgent(ai_symbol="O")

        # AI has two-in-a-row (opportunity)
        # O | O | EMPTY
        # . | . | .
        # . | . | .
        board = Board(
            cells=[
                ["O", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert analysis.board_evaluation_score > 0.0

    def test_unfavorable_ai_position(self) -> None:
        """Unfavorable AI position returns negative score."""
        scout = ScoutAgent(ai_symbol="O")

        # Opponent has two-in-a-row (threat)
        # X | X | EMPTY
        # . | . | .
        # . | . | .
        board = Board(
            cells=[
                ["X", "X", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert analysis.board_evaluation_score < 0.0

    def test_balanced_position(self) -> None:
        """Balanced position returns score near zero."""
        scout = ScoutAgent(ai_symbol="O")

        # No threats or opportunities
        # X | O | EMPTY
        # . | . | .
        # . | . | .
        board = Board(
            cells=[
                ["X", "O", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
                ["EMPTY", "EMPTY", "EMPTY"],
            ]
        )
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=2)

        result = scout.analyze(game_state)
        assert result.success
        assert result.data is not None
        analysis = result.data

        assert analysis.board_evaluation_score == 0.0


class TestAgentResult:
    """Test AgentResult wrapper functionality."""

    def test_ac_3_1_10_execution_time_recorded(self) -> None:
        """AC-3.1.10: Execution time is recorded in AgentResult."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = scout.analyze(game_state)

        assert result.success
        assert result.execution_time_ms is not None
        assert result.execution_time_ms >= 0.0

    def test_result_contains_timestamp(self) -> None:
        """Result contains ISO format timestamp."""
        scout = ScoutAgent(ai_symbol="O")

        board = Board()
        game_state = GameState(board=board, player_symbol="X", ai_symbol="O", move_count=0)

        result = scout.analyze(game_state)

        assert result.timestamp is not None
        # Verify it's ISO format (basic check)
        assert "T" in result.timestamp
