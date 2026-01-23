"""Tests for environment variable loader."""

import os
from pathlib import Path
from unittest.mock import patch

from src.utils.env_loader import _find_env_file, _find_project_root, get_api_key, reload_env


class TestFindEnvFile:
    """Test _find_env_file() function."""

    def test_finds_env_file_in_current_directory(self, tmp_path: Path) -> None:
        """Test that _find_env_file finds .env in current directory."""
        with patch("src.utils.env_loader.Path.cwd", return_value=tmp_path):
            env_file = tmp_path / ".env"
            env_file.write_text("TEST_KEY=test_value")

            result = _find_env_file()

            assert result == env_file
            assert result.exists()

    def test_finds_env_file_in_project_root(self, tmp_path: Path) -> None:
        """Test that _find_env_file finds .env in project root."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")

        env_file = project_root / ".env"
        env_file.write_text("TEST_KEY=test_value")

        with patch("src.utils.env_loader.Path.cwd", return_value=tmp_path / "subdir"):
            with patch("src.utils.env_loader._find_project_root", return_value=project_root):
                result = _find_env_file()

                assert result == env_file
                assert result.exists()

    def test_returns_none_when_no_env_file_exists(self, tmp_path: Path) -> None:
        """Test that _find_env_file returns None when no .env file exists."""
        with patch("src.utils.env_loader.Path.cwd", return_value=tmp_path):
            with patch("src.utils.env_loader._find_project_root", return_value=None):
                result = _find_env_file()

                assert result is None

    def test_returns_none_when_project_root_has_no_env_file(self, tmp_path: Path) -> None:
        """Test that _find_env_file returns None when project root exists but has no .env."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")

        with patch("src.utils.env_loader.Path.cwd", return_value=tmp_path):
            with patch("src.utils.env_loader._find_project_root", return_value=project_root):
                result = _find_env_file()

                assert result is None


class TestFindProjectRoot:
    """Test _find_project_root() function."""

    def test_finds_project_root_with_pyproject_toml(self, tmp_path: Path) -> None:
        """Test that _find_project_root finds directory containing pyproject.toml."""
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")

        subdir = project_root / "subdir"
        subdir.mkdir()

        with patch("src.utils.env_loader.Path.cwd", return_value=subdir):
            result = _find_project_root()

            assert result == project_root

    def test_returns_none_when_no_pyproject_toml_found(self, tmp_path: Path) -> None:
        """Test that _find_project_root returns None when pyproject.toml is not found."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        with patch("src.utils.env_loader.Path.cwd", return_value=subdir):
            result = _find_project_root()

            assert result is None


class TestGetApiKey:
    """Test get_api_key() function."""

    def test_gets_api_key_from_environment_variable(self) -> None:
        """Test that get_api_key retrieves value from environment variable."""
        with patch.dict(os.environ, {"TEST_API_KEY": "test-key-value"}, clear=False):
            result = get_api_key("TEST_API_KEY")

            assert result == "test-key-value"

    def test_returns_none_when_key_not_found(self) -> None:
        """Test that get_api_key returns None when key is not found."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_api_key("NONEXISTENT_KEY")

            assert result is None

    def test_returns_default_when_key_not_found(self) -> None:
        """Test that get_api_key returns default value when key is not found."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_api_key("NONEXISTENT_KEY", default="default-value")

            assert result == "default-value"

    def test_returns_environment_value_over_default(self) -> None:
        """Test that get_api_key returns environment value even when default is provided."""
        with patch.dict(os.environ, {"TEST_KEY": "env-value"}, clear=False):
            result = get_api_key("TEST_KEY", default="default-value")

            assert result == "env-value"


class TestReloadEnv:
    """Test reload_env() function."""

    def test_reload_env_finds_and_loads_env_file(self, tmp_path: Path) -> None:
        """Test that reload_env finds and loads .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("RELOAD_TEST_KEY=reload_value")

        with patch("src.utils.env_loader._find_env_file", return_value=env_file):
            with patch("src.utils.env_loader.load_dotenv") as mock_load:
                reload_env()

                mock_load.assert_called_once_with(env_file, override=True)

    def test_reload_env_handles_no_env_file(self) -> None:
        """Test that reload_env handles case when no .env file exists."""
        with patch("src.utils.env_loader._find_env_file", return_value=None):
            with patch("src.utils.env_loader.load_dotenv") as mock_load:
                reload_env()

                # Should not call load_dotenv when no file found
                mock_load.assert_not_called()
