"""Unit tests for Position domain model.

Test Coverage: AC-2.1.1 through AC-2.1.5 (5 acceptance criteria)
"""

import pytest
from pydantic import ValidationError

from src.domain.models import Position


class TestPositionCreation:
    """Test Position creation and validation."""

    def test_ac_2_1_1_valid_position(self):
        """AC-2.1.1: Given row=0, col=0, when Position is created, then position is valid."""
        position = Position(row=0, col=0)
        assert position.row == 0
        assert position.col == 0

    def test_ac_2_1_2_invalid_row_high(self):
        """AC-2.1.2: Given row=3, col=0, when Position is created, then validation error E_POSITION_OUT_OF_BOUNDS is raised."""
        with pytest.raises(ValidationError):
            Position(row=3, col=0)

    def test_ac_2_1_3_invalid_row_low(self):
        """AC-2.1.3: Given row=-1, col=0, when Position is created, then validation error E_POSITION_OUT_OF_BOUNDS is raised."""

        with pytest.raises(ValidationError):
            Position(row=-1, col=0)

    def test_invalid_col_high(self):
        """Test that col=3 raises validation error."""

        with pytest.raises(ValidationError):
            Position(row=0, col=3)

    def test_invalid_col_low(self):
        """Test that col=-1 raises validation error."""

        with pytest.raises(ValidationError):
            Position(row=0, col=-1)

    def test_valid_boundary_values(self):
        """Test that boundary values (0, 2) are valid."""
        # Minimum values
        pos1 = Position(row=0, col=0)
        assert pos1.row == 0
        assert pos1.col == 0

        # Maximum values
        pos2 = Position(row=2, col=2)
        assert pos2.row == 2
        assert pos2.col == 2

        # Mixed boundary values
        pos3 = Position(row=0, col=2)
        assert pos3.row == 0
        assert pos3.col == 2

        pos4 = Position(row=2, col=0)
        assert pos4.row == 2
        assert pos4.col == 0


class TestPositionHashability:
    """Test Position hashability for use in dictionaries and sets."""

    def test_ac_2_1_4_hashability(self):
        """AC-2.1.4: Given Position(row=1, col=2), when hashed, then produces consistent hash value for use in dictionaries/sets."""
        position = Position(row=1, col=2)
        hash1 = hash(position)
        hash2 = hash(position)
        assert hash1 == hash2, "Hash value should be consistent"

        # Test that Position can be used as dictionary key
        position_dict = {position: "test_value"}
        assert position_dict[position] == "test_value"

        # Test that Position can be used in sets
        position_set = {position}
        assert position in position_set

    def test_different_positions_different_hashes(self):
        """Test that different positions have different hash values (typically)."""
        pos1 = Position(row=0, col=0)
        pos2 = Position(row=0, col=1)
        pos3 = Position(row=1, col=0)

        # While hash collisions can occur, for these specific values they should differ
        assert hash(pos1) != hash(pos2) or hash(pos1) != hash(pos3)


class TestPositionEquality:
    """Test Position equality comparisons."""

    def test_ac_2_1_5_equality(self):
        """AC-2.1.5: Given Position(row=1, col=2) and Position(row=1, col=2), when compared, then positions are equal."""
        pos1 = Position(row=1, col=2)
        pos2 = Position(row=1, col=2)
        assert pos1 == pos2
        assert not (pos1 != pos2)

    def test_inequality_different_row(self):
        """Test that positions with different rows are not equal."""
        pos1 = Position(row=0, col=1)
        pos2 = Position(row=1, col=1)
        assert pos1 != pos2

    def test_inequality_different_col(self):
        """Test that positions with different cols are not equal."""
        pos1 = Position(row=1, col=0)
        pos2 = Position(row=1, col=2)
        assert pos1 != pos2

    def test_inequality_different_type(self):
        """Test that Position is not equal to objects of different types."""
        position = Position(row=1, col=1)
        assert position != (1, 1)
        assert position != "1,1"
        assert position != [1, 1]


class TestPositionImmutability:
    """Test Position immutability."""

    def test_immutability(self):
        """Test that Position is immutable (frozen)."""
        position = Position(row=1, col=2)
        with pytest.raises(ValidationError):  # Pydantic raises ValidationError on frozen models
            position.row = 3  # type: ignore
