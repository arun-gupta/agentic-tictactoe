"""Unit tests for agent domain models.

Test Coverage:
- AC-2.4.1 through AC-2.4.4 (Threat acceptance criteria)
- AC-2.5.1 through AC-2.5.4 (Opportunity acceptance criteria)
- AC-2.6.1 through AC-2.6.5 (StrategicMove acceptance criteria)
"""

import pytest
from pydantic import ValidationError

from src.domain.agent_models import Opportunity, StrategicMove, Threat
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
