"""Tests for configuration utilities."""

from pathlib import Path
from unittest.mock import patch

from src.utils.config import _find_project_root, get_config_path


class TestGetConfigPath:
    """Test get_config_path() function."""

    def test_returns_config_json_from_current_directory(self, tmp_path: Path) -> None:
        """Test that get_config_path returns config.json from current directory if it exists."""
        with patch("src.utils.config.Path.cwd", return_value=tmp_path):
            config_file = tmp_path / "config.json"
            config_file.write_text("{}")

            result = get_config_path()

            assert result == config_file
            assert result.exists()

    def test_returns_config_json_from_config_directory_in_current_dir(self, tmp_path: Path) -> None:
        """Test that get_config_path returns config/config.json from current directory if it exists."""
        with patch("src.utils.config.Path.cwd", return_value=tmp_path):
            config_dir = tmp_path / "config"
            config_dir.mkdir()
            config_file = config_dir / "config.json"
            config_file.write_text("{}")

            result = get_config_path()

            assert result == config_file
            assert result.exists()

    def test_returns_config_json_from_project_root_config_directory(self, tmp_path: Path) -> None:
        """Test that get_config_path returns config/config.json from project root if it exists."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")

        config_dir = project_root / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.json"
        config_file.write_text("{}")

        with patch("src.utils.config.Path.cwd", return_value=tmp_path):
            with patch("src.utils.config._find_project_root", return_value=project_root):
                result = get_config_path()

                assert result == config_file
                assert result.exists()

    def test_returns_config_json_from_project_root(self, tmp_path: Path) -> None:
        """Test that get_config_path returns config.json from project root if it exists."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")

        config_file = project_root / "config.json"
        config_file.write_text("{}")

        with patch("src.utils.config.Path.cwd", return_value=tmp_path):
            with patch("src.utils.config._find_project_root", return_value=project_root):
                result = get_config_path()

                assert result == config_file
                assert result.exists()

    def test_returns_default_path_when_no_config_exists(self, tmp_path: Path) -> None:
        """Test that get_config_path returns default path when no config file exists."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")

        with patch("src.utils.config.Path.cwd", return_value=tmp_path):
            with patch("src.utils.config._find_project_root", return_value=project_root):
                result = get_config_path()

                # Should return default path even if it doesn't exist
                assert result == project_root / "config" / "config.json"
                # File doesn't exist, but path is returned
                assert not result.exists()

    def test_returns_default_path_when_no_project_root_found(self, tmp_path: Path) -> None:
        """Test that get_config_path returns default path when project root is not found."""
        with patch("src.utils.config.Path.cwd", return_value=tmp_path):
            with patch("src.utils.config._find_project_root", return_value=None):
                result = get_config_path()

                # Should return default path in current directory
                assert result == tmp_path / "config" / "config.json"


class TestFindProjectRoot:
    """Test _find_project_root() function."""

    def test_finds_project_root_with_pyproject_toml(self, tmp_path: Path) -> None:
        """Test that _find_project_root finds directory containing pyproject.toml."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")

        subdir = project_root / "subdir"
        subdir.mkdir()

        with patch("src.utils.config.Path.cwd", return_value=subdir):
            result = _find_project_root()

            assert result == project_root

    def test_returns_none_when_no_pyproject_toml_found(self, tmp_path: Path) -> None:
        """Test that _find_project_root returns None when pyproject.toml is not found."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        with patch("src.utils.config.Path.cwd", return_value=subdir):
            result = _find_project_root()

            assert result is None

    def test_stops_at_filesystem_root(self, tmp_path: Path) -> None:
        """Test that _find_project_root stops searching at filesystem root."""
        # Create a deep directory structure without pyproject.toml
        deep_dir = tmp_path
        for i in range(5):
            deep_dir = deep_dir / f"level{i}"
            deep_dir.mkdir()

        with patch("src.utils.config.Path.cwd", return_value=deep_dir):
            result = _find_project_root()

            # Should return None since we're mocking and no pyproject.toml exists
            # In real scenario, it would stop at filesystem root
            assert result is None
