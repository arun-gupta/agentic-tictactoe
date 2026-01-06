"""Unit tests for result wrappers.

Test Coverage:
- AC-2.12.1 through AC-2.12.8 (AgentResult acceptance criteria)
"""

import pytest
from pydantic import ValidationError

from src.domain.agent_models import BoardAnalysis
from src.domain.errors import E_MISSING_DATA, E_MISSING_ERROR_MESSAGE
from src.domain.models import Position
from src.domain.result import AgentResult


class TestAgentResultCreation:
    """Test AgentResult creation and validation."""

    def test_ac_2_12_1_success_with_data(self):
        """AC-2.12.1: Given successful agent output with data, when AgentResult.success() is called, then success=True, error_message=None, data is populated."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        result = AgentResult.success(data=board_analysis, execution_time_ms=5.0)
        assert result.success is True
        assert result.data == board_analysis
        assert result.error_message is None
        assert result.error_code is None

    def test_ac_2_12_2_error_with_message(self):
        """AC-2.12.2: Given failed agent execution, when AgentResult.error() is called, then success=False, error_message is populated, data=None."""
        result = AgentResult.error(
            error_message="Test error", execution_time_ms=2.0, error_code="E_TEST_ERROR"
        )
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.error_code == "E_TEST_ERROR"
        assert result.data is None

    def test_ac_2_12_3_execution_time_value(self):
        """AC-2.12.3: Given execution time 2500ms, when AgentResult is created, then execution_time_ms=2500."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        result = AgentResult.success(data=board_analysis, execution_time_ms=2500.0)
        assert result.execution_time_ms == 2500.0

    def test_ac_2_12_4_invalid_execution_time_negative(self):
        """AC-2.12.4: Given negative execution time, when AgentResult is created, then validation error E_INVALID_EXECUTION_TIME is raised."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        with pytest.raises(ValidationError):
            AgentResult.success(data=board_analysis, execution_time_ms=-1.0)

    def test_ac_2_12_5_timestamp_iso_format(self):
        """AC-2.12.5: Given timestamp, when AgentResult is created, then timestamp is ISO 8601 format (e.g., '2025-01-15T10:30:00Z')."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        result = AgentResult.success(data=board_analysis, execution_time_ms=5.0)
        assert result.timestamp is not None
        assert "T" in result.timestamp  # ISO 8601 format
        # Should end with Z or have timezone
        assert (
            result.timestamp.endswith("Z")
            or "+00:00" in result.timestamp
            or "-00:00" in result.timestamp
        )

    def test_ac_2_12_6_metadata_dictionary(self):
        """AC-2.12.6: Given metadata dictionary {'model': 'gpt-4o', 'provider': 'openai'}, when AgentResult is created, then metadata contains both key-value pairs."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        metadata = {"model": "gpt-4o", "provider": "openai"}
        result = AgentResult.success(data=board_analysis, execution_time_ms=5.0, metadata=metadata)
        assert result.metadata == metadata
        assert result.metadata["model"] == "gpt-4o"
        assert result.metadata["provider"] == "openai"

    def test_ac_2_12_7_success_without_data(self):
        """AC-2.12.7: Given success result without data, when AgentResult.success() is called, then validation error E_MISSING_DATA is raised."""
        with pytest.raises(ValidationError) as exc_info:
            AgentResult(
                success=True,
                data=None,
                error_code=None,
                error_message=None,
                execution_time_ms=5.0,
            )
        error_str = str(exc_info.value)
        assert E_MISSING_DATA in error_str or "data is required" in error_str

    def test_ac_2_12_8_error_without_message(self):
        """AC-2.12.8: Given error result without error_message, when AgentResult.error() is called, then validation error E_MISSING_ERROR_MESSAGE is raised."""
        with pytest.raises(ValidationError) as exc_info:
            AgentResult(
                success=False,
                data=None,
                error_code="E_TEST",
                error_message=None,
                execution_time_ms=2.0,
            )
        error_str = str(exc_info.value)
        assert E_MISSING_ERROR_MESSAGE in error_str or "error_message is required" in error_str


class TestAgentResultValidation:
    """Test AgentResult field validation."""

    def test_valid_execution_times(self):
        """Test that valid execution times (>= 0.0) are accepted."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        for time_ms in [0.0, 1.5, 10.0, 100.0]:
            result = AgentResult.success(data=board_analysis, execution_time_ms=time_ms)
            assert result.execution_time_ms == time_ms

    def test_success_helper(self):
        """Test the success class method helper."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        result = AgentResult.success(data=board_analysis, execution_time_ms=5.0)
        assert result.success is True
        assert result.data == board_analysis
        assert result.error_message is None
        assert result.error_code is None
        assert result.execution_time_ms == 5.0

    def test_error_helper(self):
        """Test the error class method helper."""
        result = AgentResult.error(
            error_message="Test error", execution_time_ms=2.0, error_code="E_TEST"
        )
        assert result.success is False
        assert result.data is None
        assert result.error_message == "Test error"
        assert result.error_code == "E_TEST"
        assert result.execution_time_ms == 2.0

    def test_generic_type_parameter(self):
        """Test that AgentResult works with different generic types."""
        # Test with BoardAnalysis
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        result1: AgentResult[BoardAnalysis] = AgentResult.success_result(
            data=board_analysis, execution_time_ms=5.0
        )
        assert isinstance(result1.data, BoardAnalysis)

        # Test with Position
        position = Position(row=1, col=1)
        result2: AgentResult[Position] = AgentResult.success_result(
            data=position, execution_time_ms=1.0
        )
        assert isinstance(result2.data, Position)

    def test_timestamp_format(self):
        """Test that timestamp is in ISO 8601 format."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        result = AgentResult.success(data=board_analysis, execution_time_ms=5.0)
        # ISO 8601 format: YYYY-MM-DDTHH:MM:SS[.ffffff][+HH:MM|Z]
        assert len(result.timestamp) >= 19  # At least YYYY-MM-DDTHH:MM:SS
        assert result.timestamp[4] == "-"  # Date separator
        assert result.timestamp[7] == "-"
        assert result.timestamp[10] == "T"  # Date-time separator

    def test_custom_timestamp(self):
        """Test that custom timestamp can be provided."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        custom_timestamp = "2025-01-01T12:00:00Z"
        result = AgentResult(
            success=True,
            data=board_analysis,
            error_code=None,
            error_message=None,
            execution_time_ms=5.0,
            timestamp=custom_timestamp,
        )
        assert result.timestamp == custom_timestamp

    def test_metadata_validation_max_keys(self):
        """Test that metadata with more than 50 keys raises validation error."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        # Create metadata with 51 keys
        metadata = {f"key_{i}": f"value_{i}" for i in range(51)}
        with pytest.raises(ValidationError):
            AgentResult.success(data=board_analysis, execution_time_ms=5.0, metadata=metadata)

    def test_metadata_validation_max_value_length(self):
        """Test that metadata values longer than 200 chars raise validation error."""
        board_analysis = BoardAnalysis(
            threats=[],
            opportunities=[],
            strategic_moves=[],
            game_phase="opening",
            board_evaluation_score=0.0,
        )
        # Create metadata with value > 200 chars
        metadata = {"key": "a" * 201}
        with pytest.raises(ValidationError):
            AgentResult.success(data=board_analysis, execution_time_ms=5.0, metadata=metadata)
