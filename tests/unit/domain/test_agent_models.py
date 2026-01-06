"""Unit tests for agent domain models.

Test Coverage:
- AC-2.4.1 through AC-2.4.4 (Threat acceptance criteria)
- AC-2.5.1 through AC-2.5.4 (Opportunity acceptance criteria)
- AC-2.6.1 through AC-2.6.5 (StrategicMove acceptance criteria)
- AC-2.7.1 through AC-2.7.9 (BoardAnalysis acceptance criteria)
- AC-2.8.1 through AC-2.8.9 (MovePriority acceptance criteria)
- AC-2.9.1 through AC-2.9.6 (MoveRecommendation acceptance criteria)
- AC-2.10.1 through AC-2.10.7 (Strategy acceptance criteria)
- AC-2.11.1 through AC-2.11.7 (MoveExecution acceptance criteria)
"""

import pytest
from pydantic import ValidationError

from src.domain.agent_models import (
    BoardAnalysis,
    MoveExecution,
    MovePriority,
    MoveRecommendation,
    Opportunity,
    StrategicMove,
    Strategy,
    Threat,
)
from src.domain.errors import (
    E_INVALID_LINE_INDEX,
    E_POSITION_OUT_OF_BOUNDS,
)
from src.domain.models import Position


class TestThreatCreation:
    """Test Threat creation and validation."""

    def test_ac_2_4_1_threat_row_0(self):
        """AC-2.4.1: Given opponent has two O's in row 0 with position (0,2) empty, when Threat is created, then position=(0,2), line_type='row', line_index=0, severity='critical'."""
        position = Position(row=0, col=2)
        threat = Threat(position=position, line_type="row", line_index=0)
        assert threat.position == position
        assert threat.line_type == "row"
        assert threat.line_index == 0
        assert threat.severity == "critical"

    def test_ac_2_4_2_threat_column_1(self):
        """AC-2.4.2: Given opponent has two O's in column 1, when Threat is created, then line_type='column' and line_index=1."""
        position = Position(row=1, col=1)
        threat = Threat(position=position, line_type="column", line_index=1)
        assert threat.line_type == "column"
        assert threat.line_index == 1
        assert threat.severity == "critical"

    def test_ac_2_4_3_threat_diagonal(self):
        """AC-2.4.3: Given opponent has two O's on main diagonal, when Threat is created, then line_type='diagonal' and line_index=0."""
        position = Position(row=2, col=2)
        threat = Threat(position=position, line_type="diagonal", line_index=0)
        assert threat.line_type == "diagonal"
        assert threat.line_index == 0
        assert threat.severity == "critical"

    def test_ac_2_4_4_invalid_position(self):
        """AC-2.4.4: Given threat with invalid position (3, 3), when Threat is created, then validation error E_POSITION_OUT_OF_BOUNDS is raised."""
        # Position validation happens in Position class, not Threat
        with pytest.raises(ValidationError) as exc_info:
            Threat(position=Position(row=3, col=3), line_type="row", line_index=0)
        error_str = str(exc_info.value)
        assert E_POSITION_OUT_OF_BOUNDS in error_str or "less than or equal to 2" in error_str


class TestThreatValidation:
    """Test Threat field validation."""

    def test_invalid_line_type(self):
        """Test that invalid line_type raises ValidationError."""
        position = Position(row=0, col=0)
        # Pydantic's Literal type validation happens before custom validators
        # so the error message will be Pydantic's default, not our custom error code
        with pytest.raises(ValidationError):
            Threat(position=position, line_type="invalid", line_index=0)

    def test_invalid_line_index_too_high(self):
        """Test that line_index > 2 raises validation error."""
        position = Position(row=0, col=0)
        with pytest.raises(ValidationError) as exc_info:
            Threat(position=position, line_type="row", line_index=3)
        error_str = str(exc_info.value)
        assert "less than or equal to 2" in error_str or E_INVALID_LINE_INDEX in error_str

    def test_invalid_line_index_too_low(self):
        """Test that line_index < 0 raises validation error."""
        position = Position(row=0, col=0)
        with pytest.raises(ValidationError) as exc_info:
            Threat(position=position, line_type="row", line_index=-1)
        error_str = str(exc_info.value)
        assert "greater than or equal to 0" in error_str

    def test_valid_line_types(self):
        """Test that all valid line types are accepted."""
        position = Position(row=0, col=0)
        for line_type in ["row", "column", "diagonal"]:
            threat = Threat(position=position, line_type=line_type, line_index=0)
            assert threat.line_type == line_type

    def test_valid_line_indices(self):
        """Test that all valid line indices (0-2) are accepted."""
        position = Position(row=0, col=0)
        for line_index in [0, 1, 2]:
            threat = Threat(position=position, line_type="row", line_index=line_index)
            assert threat.line_index == line_index

    def test_severity_defaults_to_critical(self):
        """Test that severity defaults to 'critical'."""
        position = Position(row=0, col=0)
        threat = Threat(position=position, line_type="row", line_index=0)
        assert threat.severity == "critical"

    def test_severity_explicit_critical(self):
        """Test that severity can be explicitly set to 'critical'."""
        position = Position(row=0, col=0)
        threat = Threat(position=position, line_type="row", line_index=0, severity="critical")
        assert threat.severity == "critical"


class TestOpportunityCreation:
    """Test Opportunity creation and validation."""

    def test_ac_2_5_1_opportunity_row_1(self):
        """AC-2.5.1: Given AI has two X's in row 1 with position (1,2) empty, when Opportunity is created, then position=(1,2), line_type='row', line_index=1, confidence=1.0."""
        position = Position(row=1, col=2)
        opportunity = Opportunity(position=position, line_type="row", line_index=1, confidence=1.0)
        assert opportunity.position == position
        assert opportunity.line_type == "row"
        assert opportunity.line_index == 1
        assert opportunity.confidence == 1.0

    def test_ac_2_5_2_opportunity_fork_confidence(self):
        """AC-2.5.2: Given AI has one X in center with corners available, when Opportunity is created for fork, then confidence >= 0.7."""
        position = Position(row=0, col=0)
        opportunity = Opportunity(position=position, line_type="row", line_index=0, confidence=0.75)
        assert opportunity.confidence >= 0.7

    def test_ac_2_5_3_invalid_confidence_too_high(self):
        """AC-2.5.3: Given confidence value 1.5, when Opportunity is created, then validation error E_INVALID_CONFIDENCE is raised (must be 0.0-1.0)."""
        position = Position(row=0, col=0)
        # Pydantic's Field validation happens before field_validator, so error code won't appear
        with pytest.raises(ValidationError):
            Opportunity(position=position, line_type="row", line_index=0, confidence=1.5)

    def test_ac_2_5_4_invalid_confidence_too_low(self):
        """AC-2.5.4: Given confidence value -0.1, when Opportunity is created, then validation error E_INVALID_CONFIDENCE is raised."""
        position = Position(row=0, col=0)
        # Pydantic's Field validation happens before field_validator, so error code won't appear
        with pytest.raises(ValidationError):
            Opportunity(position=position, line_type="row", line_index=0, confidence=-0.1)


class TestOpportunityValidation:
    """Test Opportunity field validation."""

    def test_valid_confidence_values(self):
        """Test that valid confidence values (0.0-1.0) are accepted."""
        position = Position(row=0, col=0)
        for confidence in [0.0, 0.5, 0.7, 1.0]:
            opportunity = Opportunity(
                position=position, line_type="row", line_index=0, confidence=confidence
            )
            assert opportunity.confidence == confidence

    def test_confidence_rounding(self):
        """Test that confidence values are rounded to 2 decimal places."""
        position = Position(row=0, col=0)
        opportunity = Opportunity(
            position=position, line_type="row", line_index=0, confidence=0.123456
        )
        assert opportunity.confidence == 0.12

    def test_invalid_line_type(self):
        """Test that invalid line_type raises ValidationError."""
        position = Position(row=0, col=0)
        with pytest.raises(ValidationError):
            Opportunity(position=position, line_type="invalid", line_index=0, confidence=1.0)

    def test_invalid_line_index_too_high(self):
        """Test that line_index > 2 raises validation error."""
        position = Position(row=0, col=0)
        with pytest.raises(ValidationError):
            Opportunity(position=position, line_type="row", line_index=3, confidence=1.0)

    def test_invalid_line_index_too_low(self):
        """Test that line_index < 0 raises validation error."""
        position = Position(row=0, col=0)
        with pytest.raises(ValidationError):
            Opportunity(position=position, line_type="row", line_index=-1, confidence=1.0)

    def test_valid_line_types(self):
        """Test that all valid line types are accepted."""
        position = Position(row=0, col=0)
        for line_type in ["row", "column", "diagonal"]:
            opportunity = Opportunity(
                position=position, line_type=line_type, line_index=0, confidence=1.0
            )
            assert opportunity.line_type == line_type

    def test_opportunity_column(self):
        """Test Opportunity with column line type."""
        position = Position(row=1, col=1)
        opportunity = Opportunity(
            position=position, line_type="column", line_index=1, confidence=0.9
        )
        assert opportunity.line_type == "column"
        assert opportunity.line_index == 1
        assert opportunity.confidence == 0.9

    def test_opportunity_diagonal(self):
        """Test Opportunity with diagonal line type."""
        position = Position(row=2, col=2)
        opportunity = Opportunity(
            position=position, line_type="diagonal", line_index=0, confidence=1.0
        )
        assert opportunity.line_type == "diagonal"
        assert opportunity.line_index == 0
        assert opportunity.confidence == 1.0


class TestStrategicMoveCreation:
    """Test StrategicMove creation and validation."""

    def test_ac_2_6_1_center_move(self):
        """AC-2.6.1: Given empty board, when StrategicMove for center is created, then position=(1,1), move_type='center', priority >= 8."""
        position = Position(row=1, col=1)
        strategic_move = StrategicMove(
            position=position,
            move_type="center",
            priority=8,
            reasoning="Center is the most strategic position",
        )
        assert strategic_move.position == position
        assert strategic_move.move_type == "center"
        assert strategic_move.priority >= 8
        assert strategic_move.reasoning == "Center is the most strategic position"

    def test_ac_2_6_2_corner_move(self):
        """AC-2.6.2: Given move_type='corner', when StrategicMove is created, then position is one of: (0,0), (0,2), (2,0), (2,2)."""
        corner_positions = [
            Position(row=0, col=0),
            Position(row=0, col=2),
            Position(row=2, col=0),
            Position(row=2, col=2),
        ]
        for position in corner_positions:
            strategic_move = StrategicMove(
                position=position,
                move_type="corner",
                priority=7,
                reasoning="Corner position",
            )
            assert strategic_move.move_type == "corner"
            assert strategic_move.position in corner_positions

    def test_ac_2_6_3_edge_move(self):
        """AC-2.6.3: Given move_type='edge', when StrategicMove is created, then position is one of: (0,1), (1,0), (1,2), (2,1)."""
        edge_positions = [
            Position(row=0, col=1),
            Position(row=1, col=0),
            Position(row=1, col=2),
            Position(row=2, col=1),
        ]
        for position in edge_positions:
            strategic_move = StrategicMove(
                position=position,
                move_type="edge",
                priority=5,
                reasoning="Edge position",
            )
            assert strategic_move.move_type == "edge"
            assert strategic_move.position in edge_positions

    def test_ac_2_6_4_invalid_priority_too_high(self):
        """AC-2.6.4: Given priority value 11, when StrategicMove is created, then validation error E_INVALID_PRIORITY is raised (must be 1-10)."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            StrategicMove(
                position=position,
                move_type="center",
                priority=11,
                reasoning="Test reasoning",
            )

    def test_ac_2_6_5_invalid_priority_too_low(self):
        """AC-2.6.5: Given priority value 0, when StrategicMove is created, then validation error E_INVALID_PRIORITY is raised."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            StrategicMove(
                position=position,
                move_type="center",
                priority=0,
                reasoning="Test reasoning",
            )


class TestStrategicMoveValidation:
    """Test StrategicMove field validation."""

    def test_invalid_move_type(self):
        """Test that invalid move_type raises ValidationError."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            StrategicMove(
                position=position,
                move_type="invalid",
                priority=5,
                reasoning="Test reasoning",
            )

    def test_valid_move_types(self):
        """Test that all valid move types are accepted."""
        position = Position(row=1, col=1)
        for move_type in ["center", "corner", "edge", "fork", "block_fork"]:
            strategic_move = StrategicMove(
                position=position,
                move_type=move_type,
                priority=5,
                reasoning="Test reasoning",
            )
            assert strategic_move.move_type == move_type

    def test_valid_priorities(self):
        """Test that all valid priorities (1-10) are accepted."""
        position = Position(row=1, col=1)
        for priority in range(1, 11):
            strategic_move = StrategicMove(
                position=position,
                move_type="center",
                priority=priority,
                reasoning="Test reasoning",
            )
            assert strategic_move.priority == priority

    def test_empty_reasoning(self):
        """Test that empty reasoning raises ValidationError."""
        position = Position(row=1, col=1)
        # Pydantic's Field validation (min_length) happens before field_validator
        with pytest.raises(ValidationError):
            StrategicMove(
                position=position,
                move_type="center",
                priority=5,
                reasoning="",
            )

    def test_whitespace_only_reasoning(self):
        """Test that whitespace-only reasoning raises validation error."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            StrategicMove(
                position=position,
                move_type="center",
                priority=5,
                reasoning="   ",
            )

    def test_reasoning_max_length(self):
        """Test that reasoning respects max length of 1000 characters."""
        position = Position(row=1, col=1)
        # Valid: exactly 1000 characters
        valid_reasoning = "a" * 1000
        strategic_move = StrategicMove(
            position=position,
            move_type="center",
            priority=5,
            reasoning=valid_reasoning,
        )
        assert len(strategic_move.reasoning) == 1000

    def test_fork_move_type(self):
        """Test StrategicMove with fork move type."""
        position = Position(row=1, col=1)
        strategic_move = StrategicMove(
            position=position,
            move_type="fork",
            priority=9,
            reasoning="Creating a fork opportunity",
        )
        assert strategic_move.move_type == "fork"
        assert strategic_move.priority == 9

    def test_block_fork_move_type(self):
        """Test StrategicMove with block_fork move type."""
        position = Position(row=0, col=0)
        strategic_move = StrategicMove(
            position=position,
            move_type="block_fork",
            priority=8,
            reasoning="Blocking opponent's fork",
        )
        assert strategic_move.move_type == "block_fork"
        assert strategic_move.priority == 8


class TestBoardAnalysisCreation:
    """Test BoardAnalysis creation and validation."""

    def test_ac_2_7_1_threats_present(self):
        """AC-2.7.1: Given board with opponent about to win, when BoardAnalysis is created, then threats list contains at least one Threat."""
        threat = Threat(position=Position(row=0, col=2), line_type="row", line_index=0)
        analysis = BoardAnalysis(
            threats=[threat],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=-0.5,
        )
        assert len(analysis.threats) >= 1
        assert analysis.threats[0] == threat

    def test_ac_2_7_2_opportunities_present(self):
        """AC-2.7.2: Given board with AI about to win, when BoardAnalysis is created, then opportunities list contains at least one Opportunity with winning position."""
        opportunity = Opportunity(
            position=Position(row=1, col=2), line_type="row", line_index=1, confidence=1.0
        )
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[opportunity],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.8,
        )
        assert len(analysis.opportunities) >= 1
        assert analysis.opportunities[0] == opportunity

    def test_ac_2_7_3_opening_phase(self):
        """AC-2.7.3: Given empty board (move 0-2), when BoardAnalysis is created, then game_phase='opening'."""
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        assert analysis.game_phase == "opening"

    def test_ac_2_7_4_midgame_phase(self):
        """AC-2.7.4: Given board with 3-6 moves, when BoardAnalysis is created, then game_phase='midgame'."""
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.2,
        )
        assert analysis.game_phase == "midgame"

    def test_ac_2_7_5_endgame_phase(self):
        """AC-2.7.5: Given board with 7-9 moves, when BoardAnalysis is created, then game_phase='endgame'."""
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="endgame",
            board_evaluation_score=0.1,
        )
        assert analysis.game_phase == "endgame"

    def test_ac_2_7_6_invalid_eval_score_too_high(self):
        """AC-2.7.6: Given board evaluation score 1.5, when BoardAnalysis is created, then validation error E_INVALID_EVAL_SCORE is raised (must be -1.0 to 1.0)."""
        with pytest.raises(ValidationError):
            BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="midgame",
                board_evaluation_score=1.5,
            )

    def test_ac_2_7_7_favorable_ai_score(self):
        """AC-2.7.7: Given favorable board for AI, when BoardAnalysis is created, then board_evaluation_score > 0.0."""
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[
                Opportunity(
                    position=Position(row=1, col=2), line_type="row", line_index=1, confidence=1.0
                )
            ],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.5,
        )
        assert analysis.board_evaluation_score > 0.0

    def test_ac_2_7_8_favorable_opponent_score(self):
        """AC-2.7.8: Given favorable board for opponent, when BoardAnalysis is created, then board_evaluation_score < 0.0."""
        analysis = BoardAnalysis(
            threats=[Threat(position=Position(row=0, col=2), line_type="row", line_index=0)],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=-0.5,
        )
        assert analysis.board_evaluation_score < 0.0

    def test_ac_2_7_9_balanced_score(self):
        """AC-2.7.9: Given balanced board, when BoardAnalysis is created, then board_evaluation_score ≈ 0.0 (within ±0.2)."""
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.1,
        )
        assert -0.2 <= analysis.board_evaluation_score <= 0.2


class TestBoardAnalysisValidation:
    """Test BoardAnalysis field validation."""

    def test_valid_game_phases(self):
        """Test that all valid game phases are accepted."""
        for phase in ["opening", "midgame", "endgame"]:
            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase=phase,
                board_evaluation_score=0.0,
            )
            assert analysis.game_phase == phase

    def test_invalid_game_phase(self):
        """Test that invalid game_phase raises ValidationError."""
        with pytest.raises(ValidationError):
            BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="invalid",  # type: ignore[arg-type]
                board_evaluation_score=0.0,
            )

    def test_valid_eval_scores(self):
        """Test that valid evaluation scores (-1.0 to 1.0) are accepted."""
        for score in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            analysis = BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="midgame",
                board_evaluation_score=score,
            )
            assert analysis.board_evaluation_score == score

    def test_eval_score_rounding(self):
        """Test that evaluation scores are rounded to 2 decimal places."""
        analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="midgame",
            board_evaluation_score=0.123456,
        )
        assert analysis.board_evaluation_score == 0.12

    def test_invalid_eval_score_too_low(self):
        """Test that evaluation score < -1.0 raises validation error."""
        with pytest.raises(ValidationError):
            BoardAnalysis(
                threats=[],
                opportunities=[],
                strategic_moves=[],
                game_phase="midgame",
                board_evaluation_score=-1.5,
            )

    def test_empty_lists_default(self):
        """Test that empty lists are the default for threats, opportunities, and strategic_moves."""
        analysis = BoardAnalysis(
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        assert analysis.threats == []
        assert analysis.opportunities == []
        assert analysis.strategic_moves == []

    def test_complete_board_analysis(self):
        """Test BoardAnalysis with all fields populated."""
        threat = Threat(position=Position(row=0, col=2), line_type="row", line_index=0)
        opportunity = Opportunity(
            position=Position(row=1, col=2), line_type="row", line_index=1, confidence=1.0
        )
        strategic_move = StrategicMove(
            position=Position(row=1, col=1),
            move_type="center",
            priority=8,
            reasoning="Center control",
        )
        analysis = BoardAnalysis(
            threats=[threat],
            opportunities=[opportunity],
            strategic_moves=[strategic_move],
            game_phase="midgame",
            board_evaluation_score=0.3,
        )
        assert len(analysis.threats) == 1
        assert len(analysis.opportunities) == 1
        assert len(analysis.strategic_moves) == 1
        assert analysis.game_phase == "midgame"
        assert analysis.board_evaluation_score == 0.3


class TestMovePriorityEnum:
    """Test MovePriority enum definition and comparison."""

    def test_ac_2_8_1_immediate_win_value(self):
        """AC-2.8.1: Given MovePriority.IMMEDIATE_WIN, when accessed, then value equals 100."""
        assert MovePriority.IMMEDIATE_WIN == 100
        assert MovePriority.IMMEDIATE_WIN.value == 100

    def test_ac_2_8_2_block_threat_value(self):
        """AC-2.8.2: Given MovePriority.BLOCK_THREAT, when accessed, then value equals 90."""
        assert MovePriority.BLOCK_THREAT == 90
        assert MovePriority.BLOCK_THREAT.value == 90

    def test_ac_2_8_3_force_win_value(self):
        """AC-2.8.3: Given MovePriority.FORCE_WIN, when accessed, then value equals 80."""
        assert MovePriority.FORCE_WIN == 80
        assert MovePriority.FORCE_WIN.value == 80

    def test_ac_2_8_4_prevent_fork_value(self):
        """AC-2.8.4: Given MovePriority.PREVENT_FORK, when accessed, then value equals 70."""
        assert MovePriority.PREVENT_FORK == 70
        assert MovePriority.PREVENT_FORK.value == 70

    def test_ac_2_8_5_center_control_value(self):
        """AC-2.8.5: Given MovePriority.CENTER_CONTROL, when accessed, then value equals 50."""
        assert MovePriority.CENTER_CONTROL == 50
        assert MovePriority.CENTER_CONTROL.value == 50

    def test_ac_2_8_6_corner_control_value(self):
        """AC-2.8.6: Given MovePriority.CORNER_CONTROL, when accessed, then value equals 40."""
        assert MovePriority.CORNER_CONTROL == 40
        assert MovePriority.CORNER_CONTROL.value == 40

    def test_ac_2_8_7_edge_play_value(self):
        """AC-2.8.7: Given MovePriority.EDGE_PLAY, when accessed, then value equals 30."""
        assert MovePriority.EDGE_PLAY == 30
        assert MovePriority.EDGE_PLAY.value == 30

    def test_ac_2_8_8_random_valid_value(self):
        """AC-2.8.8: Given MovePriority.RANDOM_VALID, when accessed, then value equals 10."""
        assert MovePriority.RANDOM_VALID == 10
        assert MovePriority.RANDOM_VALID.value == 10

    def test_ac_2_8_9_comparison_order(self):
        """AC-2.8.9: Given all MovePriority values, when compared, then IMMEDIATE_WIN > BLOCK_THREAT > FORCE_WIN > PREVENT_FORK > CENTER_CONTROL > CORNER_CONTROL > EDGE_PLAY > RANDOM_VALID."""
        assert MovePriority.IMMEDIATE_WIN > MovePriority.BLOCK_THREAT
        assert MovePriority.BLOCK_THREAT > MovePriority.FORCE_WIN
        assert MovePriority.FORCE_WIN > MovePriority.PREVENT_FORK
        assert MovePriority.PREVENT_FORK > MovePriority.CENTER_CONTROL
        assert MovePriority.CENTER_CONTROL > MovePriority.CORNER_CONTROL
        assert MovePriority.CORNER_CONTROL > MovePriority.EDGE_PLAY
        assert MovePriority.EDGE_PLAY > MovePriority.RANDOM_VALID

    def test_all_priority_values(self):
        """Test that all priority values are correctly defined."""
        expected_values = {
            MovePriority.IMMEDIATE_WIN: 100,
            MovePriority.BLOCK_THREAT: 90,
            MovePriority.FORCE_WIN: 80,
            MovePriority.PREVENT_FORK: 70,
            MovePriority.CENTER_CONTROL: 50,
            MovePriority.CORNER_CONTROL: 40,
            MovePriority.EDGE_PLAY: 30,
            MovePriority.RANDOM_VALID: 10,
        }
        for priority, expected_value in expected_values.items():
            assert priority == expected_value
            assert priority.value == expected_value

    def test_enum_comparison_with_int(self):
        """Test that enum values can be compared with integers."""
        assert MovePriority.IMMEDIATE_WIN > 90
        assert MovePriority.BLOCK_THREAT == 90
        assert MovePriority.RANDOM_VALID < 20

    def test_enum_ordering(self):
        """Test that enum values maintain correct ordering."""
        priorities = [
            MovePriority.IMMEDIATE_WIN,
            MovePriority.BLOCK_THREAT,
            MovePriority.FORCE_WIN,
            MovePriority.PREVENT_FORK,
            MovePriority.CENTER_CONTROL,
            MovePriority.CORNER_CONTROL,
            MovePriority.EDGE_PLAY,
            MovePriority.RANDOM_VALID,
        ]
        # Verify descending order
        for i in range(len(priorities) - 1):
            assert priorities[i] > priorities[i + 1]


class TestMoveRecommendationCreation:
    """Test MoveRecommendation creation and validation."""

    def test_ac_2_9_1_required_fields(self):
        """AC-2.9.1: Given MoveRecommendation with position, priority, confidence, reasoning, when created, then all required fields are set."""
        position = Position(row=1, col=1)
        recommendation = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control is strategic",
        )
        assert recommendation.position == position
        assert recommendation.priority == MovePriority.CENTER_CONTROL
        assert recommendation.confidence == 0.8
        assert recommendation.reasoning == "Center control is strategic"

    def test_ac_2_9_2_optional_outcome_description(self):
        """AC-2.9.2: Given MoveRecommendation with outcome_description, when created, then outcome_description is set."""
        position = Position(row=0, col=0)
        recommendation = MoveRecommendation(
            position=position,
            priority=MovePriority.CORNER_CONTROL,
            confidence=0.7,
            reasoning="Take corner position",
            outcome_description="Secures corner advantage",
        )
        assert recommendation.outcome_description == "Secures corner advantage"

    def test_ac_2_9_3_no_outcome_description(self):
        """AC-2.9.3: Given MoveRecommendation without outcome_description, when created, then outcome_description is None."""
        position = Position(row=1, col=1)
        recommendation = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control",
        )
        assert recommendation.outcome_description is None

    def test_ac_2_9_4_invalid_confidence_too_high(self):
        """AC-2.9.4: Given confidence value 1.5, when MoveRecommendation is created, then validation error E_INVALID_CONFIDENCE is raised (must be 0.0-1.0)."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            MoveRecommendation(
                position=position,
                priority=MovePriority.CENTER_CONTROL,
                confidence=1.5,
                reasoning="Test reasoning",
            )

    def test_ac_2_9_5_invalid_confidence_too_low(self):
        """AC-2.9.5: Given confidence value -0.1, when MoveRecommendation is created, then validation error E_INVALID_CONFIDENCE is raised."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            MoveRecommendation(
                position=position,
                priority=MovePriority.CENTER_CONTROL,
                confidence=-0.1,
                reasoning="Test reasoning",
            )

    def test_ac_2_9_6_empty_reasoning(self):
        """AC-2.9.6: Given reasoning='', when MoveRecommendation is created, then validation error E_MISSING_REASONING is raised."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            MoveRecommendation(
                position=position,
                priority=MovePriority.CENTER_CONTROL,
                confidence=0.8,
                reasoning="",
            )


class TestMoveRecommendationValidation:
    """Test MoveRecommendation field validation."""

    def test_valid_confidence_values(self):
        """Test that valid confidence values (0.0-1.0) are accepted."""
        position = Position(row=1, col=1)
        for confidence in [0.0, 0.25, 0.5, 0.75, 1.0]:
            recommendation = MoveRecommendation(
                position=position,
                priority=MovePriority.CENTER_CONTROL,
                confidence=confidence,
                reasoning="Test reasoning",
            )
            assert recommendation.confidence == confidence

    def test_confidence_rounding(self):
        """Test that confidence values are rounded to 2 decimal places."""
        position = Position(row=1, col=1)
        recommendation = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.123456,
            reasoning="Test reasoning",
        )
        assert recommendation.confidence == 0.12

    def test_all_priority_levels(self):
        """Test that all MovePriority enum values are accepted."""
        position = Position(row=1, col=1)
        for priority in MovePriority:
            recommendation = MoveRecommendation(
                position=position,
                priority=priority,
                confidence=0.8,
                reasoning="Test reasoning",
            )
            assert recommendation.priority == priority

    def test_reasoning_max_length(self):
        """Test that reasoning respects max length of 1000 characters."""
        position = Position(row=1, col=1)
        # Valid: exactly 1000 characters
        valid_reasoning = "a" * 1000
        recommendation = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning=valid_reasoning,
        )
        assert len(recommendation.reasoning) == 1000

    def test_outcome_description_max_length(self):
        """Test that outcome_description respects max length of 500 characters."""
        position = Position(row=1, col=1)
        # Valid: exactly 500 characters
        valid_outcome = "a" * 500
        recommendation = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Test reasoning",
            outcome_description=valid_outcome,
        )
        assert recommendation.outcome_description == valid_outcome
        assert len(recommendation.outcome_description) == 500

    def test_whitespace_only_reasoning(self):
        """Test that whitespace-only reasoning raises validation error."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            MoveRecommendation(
                position=position,
                priority=MovePriority.CENTER_CONTROL,
                confidence=0.8,
                reasoning="   ",
            )

    def test_complete_move_recommendation(self):
        """Test MoveRecommendation with all fields populated."""
        position = Position(row=2, col=2)
        recommendation = MoveRecommendation(
            position=position,
            priority=MovePriority.IMMEDIATE_WIN,
            confidence=1.0,
            reasoning="This move will win the game",
            outcome_description="Game ends with AI victory",
        )
        assert recommendation.position == position
        assert recommendation.priority == MovePriority.IMMEDIATE_WIN
        assert recommendation.confidence == 1.0
        assert recommendation.reasoning == "This move will win the game"
        assert recommendation.outcome_description == "Game ends with AI victory"


class TestStrategyCreation:
    """Test Strategy creation and validation."""

    def test_ac_2_10_1_primary_move_required(self):
        """AC-2.10.1: Given Strategy with primary_move, when created, then primary_move is set."""
        position = Position(row=1, col=1)
        primary_move = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control",
        )
        strategy = Strategy(
            primary_move=primary_move,
            alternatives=[],
            game_plan="Control center and expand",
            risk_assessment="low",
        )
        assert strategy.primary_move == primary_move

    def test_ac_2_10_2_alternatives_sorted(self):
        """AC-2.10.2: Given Strategy with multiple alternatives, when created, then alternatives are sorted by priority descending."""
        position1 = Position(row=0, col=0)
        position2 = Position(row=1, col=1)
        position3 = Position(row=2, col=2)
        alt1 = MoveRecommendation(
            position=position1,
            priority=MovePriority.CORNER_CONTROL,
            confidence=0.7,
            reasoning="Corner move",
        )
        alt2 = MoveRecommendation(
            position=position2,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center move",
        )
        alt3 = MoveRecommendation(
            position=position3,
            priority=MovePriority.EDGE_PLAY,
            confidence=0.6,
            reasoning="Edge move",
        )
        # Create with unsorted alternatives - should be sorted automatically
        strategy = Strategy(
            primary_move=alt2,  # Center has highest priority
            alternatives=[
                alt3,
                alt1,
            ],  # Edge (30) then Corner (40) - should become Corner then Edge
            game_plan="Test plan",
            risk_assessment="medium",
        )
        # After validation, alternatives should be sorted: Corner (40) > Edge (30)
        assert len(strategy.alternatives) == 2
        assert strategy.alternatives[0].priority == MovePriority.CORNER_CONTROL
        assert strategy.alternatives[1].priority == MovePriority.EDGE_PLAY

    def test_ac_2_10_3_empty_alternatives(self):
        """AC-2.10.3: Given Strategy with empty alternatives list, when created, then alternatives is empty list."""
        position = Position(row=1, col=1)
        primary_move = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control",
        )
        strategy = Strategy(
            primary_move=primary_move,
            alternatives=[],
            game_plan="Simple plan",
            risk_assessment="low",
        )
        assert strategy.alternatives == []

    def test_ac_2_10_4_valid_risk_levels(self):
        """AC-2.10.4: Given Strategy with risk_assessment='low', 'medium', or 'high', when created, then risk_assessment is set."""
        position = Position(row=1, col=1)
        primary_move = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control",
        )
        for risk_level in ["low", "medium", "high"]:
            strategy = Strategy(
                primary_move=primary_move,
                alternatives=[],
                game_plan="Test plan",
                risk_assessment=risk_level,
            )
            assert strategy.risk_assessment == risk_level

    def test_ac_2_10_5_invalid_risk_level(self):
        """AC-2.10.5: Given risk_assessment='invalid', when Strategy is created, then validation error E_INVALID_RISK_LEVEL is raised."""
        position = Position(row=1, col=1)
        primary_move = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control",
        )
        with pytest.raises(ValidationError):
            Strategy(
                primary_move=primary_move,
                alternatives=[],
                game_plan="Test plan",
                risk_assessment="invalid",  # type: ignore[arg-type]
            )

    def test_ac_2_10_6_missing_primary_move(self):
        """AC-2.10.6: Given primary_move=None, when Strategy is created, then validation error E_MISSING_PRIMARY_MOVE is raised."""
        with pytest.raises(ValidationError):
            Strategy(
                primary_move=None,  # type: ignore[arg-type]
                alternatives=[],
                game_plan="Test plan",
                risk_assessment="low",
            )

    def test_ac_2_10_7_game_plan_required(self):
        """AC-2.10.7: Given game_plan='', when Strategy is created, then validation error is raised (game_plan must be non-empty)."""
        position = Position(row=1, col=1)
        primary_move = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control",
        )
        with pytest.raises(ValidationError):
            Strategy(
                primary_move=primary_move,
                alternatives=[],
                game_plan="",
                risk_assessment="low",
            )


class TestStrategyValidation:
    """Test Strategy field validation."""

    def test_alternatives_auto_sort(self):
        """Test that alternatives are automatically sorted by priority descending."""
        position1 = Position(row=0, col=0)
        position2 = Position(row=1, col=1)
        position3 = Position(row=2, col=2)
        primary = MoveRecommendation(
            position=position1,
            priority=MovePriority.IMMEDIATE_WIN,
            confidence=1.0,
            reasoning="Win move",
        )
        alt1 = MoveRecommendation(
            position=position2,
            priority=MovePriority.EDGE_PLAY,  # Priority 30
            confidence=0.6,
            reasoning="Edge",
        )
        alt2 = MoveRecommendation(
            position=position3,
            priority=MovePriority.CORNER_CONTROL,  # Priority 40
            confidence=0.7,
            reasoning="Corner",
        )
        # Create with alternatives in wrong order
        strategy = Strategy(
            primary_move=primary,
            alternatives=[alt1, alt2],  # Edge (30) then Corner (40)
            game_plan="Test plan",
            risk_assessment="low",
        )
        # Should be sorted: Corner (40) > Edge (30)
        assert strategy.alternatives[0].priority == MovePriority.CORNER_CONTROL
        assert strategy.alternatives[1].priority == MovePriority.EDGE_PLAY

    def test_game_plan_max_length(self):
        """Test that game_plan respects max length of 2000 characters."""
        position = Position(row=1, col=1)
        primary_move = MoveRecommendation(
            position=position,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control",
        )
        # Valid: exactly 2000 characters
        valid_plan = "a" * 2000
        strategy = Strategy(
            primary_move=primary_move,
            alternatives=[],
            game_plan=valid_plan,
            risk_assessment="low",
        )
        assert len(strategy.game_plan) == 2000

    def test_complete_strategy(self):
        """Test Strategy with all fields populated."""
        position1 = Position(row=1, col=1)
        position2 = Position(row=0, col=0)
        position3 = Position(row=2, col=2)
        primary = MoveRecommendation(
            position=position1,
            priority=MovePriority.IMMEDIATE_WIN,
            confidence=1.0,
            reasoning="This move wins the game",
            outcome_description="Game victory",
        )
        alt1 = MoveRecommendation(
            position=position2,
            priority=MovePriority.BLOCK_THREAT,
            confidence=0.9,
            reasoning="Block opponent",
        )
        alt2 = MoveRecommendation(
            position=position3,
            priority=MovePriority.CENTER_CONTROL,
            confidence=0.8,
            reasoning="Center control",
        )
        strategy = Strategy(
            primary_move=primary,
            alternatives=[alt1, alt2],
            game_plan="Win immediately if possible, otherwise block threats and control center",
            risk_assessment="low",
        )
        assert strategy.primary_move == primary
        assert len(strategy.alternatives) == 2
        assert (
            strategy.game_plan
            == "Win immediately if possible, otherwise block threats and control center"
        )
        assert strategy.risk_assessment == "low"


class TestMoveExecutionCreation:
    """Test MoveExecution creation and validation."""

    def test_ac_2_11_1_valid_execution(self):
        """AC-2.11.1: Given valid move execution, when MoveExecution is created, then success=True, validation_errors=empty list."""
        position = Position(row=1, col=1)
        execution = MoveExecution(
            position=position,
            success=True,
            validation_errors=[],
            execution_time_ms=5.5,
            reasoning="Move executed successfully",
        )
        assert execution.success is True
        assert execution.validation_errors == []
        assert execution.position == position

    def test_ac_2_11_2_invalid_cell_occupied(self):
        """AC-2.11.2: Given invalid move (cell occupied), when MoveExecution is created, then success=False, validation_errors contains `E_CELL_OCCUPIED`."""
        position = Position(row=0, col=0)
        execution = MoveExecution(
            position=position,
            success=False,
            validation_errors=["E_CELL_OCCUPIED"],
            execution_time_ms=2.0,
            reasoning="Cell is already occupied",
        )
        assert execution.success is False
        assert "E_CELL_OCCUPIED" in execution.validation_errors

    def test_ac_2_11_3_execution_time_rounding(self):
        """AC-2.11.3: Given execution_time_ms=5.123456, when MoveExecution is created, then execution_time_ms=5.12 (rounded to 2 decimal places)."""
        position = Position(row=1, col=1)
        execution = MoveExecution(
            position=position,
            success=True,
            validation_errors=[],
            execution_time_ms=5.123456,
            reasoning="Test execution",
        )
        assert execution.execution_time_ms == 5.12

    def test_ac_2_11_4_invalid_execution_time_negative(self):
        """AC-2.11.4: Given execution_time_ms=-1.0, when MoveExecution is created, then validation error E_INVALID_EXECUTION_TIME is raised (must be >= 0.0)."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            MoveExecution(
                position=position,
                success=True,
                validation_errors=[],
                execution_time_ms=-1.0,
                reasoning="Test execution",
            )

    def test_ac_2_11_5_empty_reasoning(self):
        """AC-2.11.5: Given reasoning='', when MoveExecution is created, then validation error E_MISSING_REASONING is raised."""
        position = Position(row=1, col=1)
        with pytest.raises(ValidationError):
            MoveExecution(
                position=position,
                success=True,
                validation_errors=[],
                execution_time_ms=5.0,
                reasoning="",
            )

    def test_ac_2_11_6_actual_priority_used(self):
        """AC-2.11.6: Given actual_priority_used=IMMEDIATE_WIN, when MoveExecution is created, then actual_priority_used is set."""
        position = Position(row=1, col=1)
        execution = MoveExecution(
            position=position,
            success=True,
            validation_errors=[],
            execution_time_ms=5.0,
            reasoning="Winning move executed",
            actual_priority_used=MovePriority.IMMEDIATE_WIN,
        )
        assert execution.actual_priority_used == MovePriority.IMMEDIATE_WIN

    def test_ac_2_11_7_no_actual_priority_used(self):
        """AC-2.11.7: Given MoveExecution without actual_priority_used, when created, then actual_priority_used is None."""
        position = Position(row=1, col=1)
        execution = MoveExecution(
            position=position,
            success=True,
            validation_errors=[],
            execution_time_ms=5.0,
            reasoning="Move executed",
        )
        assert execution.actual_priority_used is None


class TestMoveExecutionValidation:
    """Test MoveExecution field validation."""

    def test_valid_execution_times(self):
        """Test that valid execution times (>= 0.0) are accepted."""
        position = Position(row=1, col=1)
        for time_ms in [0.0, 1.5, 10.0, 100.0]:
            execution = MoveExecution(
                position=position,
                success=True,
                validation_errors=[],
                execution_time_ms=time_ms,
                reasoning="Test execution",
            )
            assert execution.execution_time_ms == time_ms

    def test_multiple_validation_errors(self):
        """Test that multiple validation errors can be stored."""
        # Note: Position validation happens at Position creation, so we'll use valid position
        # but simulate multiple errors
        execution = MoveExecution(
            position=Position(row=0, col=0),
            success=False,
            validation_errors=["E_CELL_OCCUPIED", "E_GAME_ALREADY_OVER"],
            execution_time_ms=2.0,
            reasoning="Multiple validation errors",
        )
        assert len(execution.validation_errors) == 2
        assert "E_CELL_OCCUPIED" in execution.validation_errors
        assert "E_GAME_ALREADY_OVER" in execution.validation_errors

    def test_reasoning_max_length(self):
        """Test that reasoning respects max length of 1000 characters."""
        position = Position(row=1, col=1)
        # Valid: exactly 1000 characters
        valid_reasoning = "a" * 1000
        execution = MoveExecution(
            position=position,
            success=True,
            validation_errors=[],
            execution_time_ms=5.0,
            reasoning=valid_reasoning,
        )
        assert len(execution.reasoning) == 1000

    def test_position_optional_when_failed(self):
        """Test that position can be None when success=False."""
        execution = MoveExecution(
            position=None,
            success=False,
            validation_errors=["E_POSITION_OUT_OF_BOUNDS"],
            execution_time_ms=1.0,
            reasoning="Invalid position",
        )
        assert execution.position is None
        assert execution.success is False

    def test_all_priority_levels_for_actual_priority(self):
        """Test that all MovePriority enum values can be used for actual_priority_used."""
        position = Position(row=1, col=1)
        for priority in MovePriority:
            execution = MoveExecution(
                position=position,
                success=True,
                validation_errors=[],
                execution_time_ms=5.0,
                reasoning="Test execution",
                actual_priority_used=priority,
            )
            assert execution.actual_priority_used == priority

    def test_complete_move_execution(self):
        """Test MoveExecution with all fields populated."""
        position = Position(row=2, col=2)
        execution = MoveExecution(
            position=position,
            success=True,
            validation_errors=[],
            execution_time_ms=7.5,
            reasoning="Successfully executed winning move",
            actual_priority_used=MovePriority.IMMEDIATE_WIN,
        )
        assert execution.position == position
        assert execution.success is True
        assert execution.validation_errors == []
        assert execution.execution_time_ms == 7.5
        assert execution.reasoning == "Successfully executed winning move"
        assert execution.actual_priority_used == MovePriority.IMMEDIATE_WIN
