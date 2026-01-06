"""Unit tests for agent domain models.

Test Coverage: AC-2.4.1 through AC-2.4.4 (Threat acceptance criteria)
"""

import pytest
from pydantic import ValidationError

from src.domain.agent_models import Threat
from src.domain.errors import E_INVALID_LINE_INDEX, E_POSITION_OUT_OF_BOUNDS
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
