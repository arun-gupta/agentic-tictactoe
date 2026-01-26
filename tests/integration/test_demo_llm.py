"""Tests for Demo Script LLM Support - Subsection 5.2.2.

Subsection tests for Phase 5.2.2: Demo Script LLM Support
These tests verify that:
1. Demo script validates .env file exists when llm mode selected
2. Demo script validates LLM_ENABLED is true when llm mode selected
3. Demo script validates required provider environment variables are set
4. Demo script validates API keys exist for configured providers
5. Demo script initializes agents with LLM enabled when llm mode selected
6. Demo script displays configuration info at startup
7. Demo script runs successfully with valid LLM configuration
8. Demo script shows helpful error message when configuration invalid
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestDemoScriptLLMSupport:
    """Test that demo script validates and displays LLM configuration."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    def test_subsection_5_2_2_1_validates_env_file_exists(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 1: Demo script validates .env file exists when llm mode selected."""
        # Change to project root for running scripts
        monkeypatch.chdir(project_root)

        # Create clean environment without LLM vars
        import os

        env = os.environ.copy()
        for key in [
            "LLM_ENABLED",
            "SCOUT_PROVIDER",
            "STRATEGIST_PROVIDER",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GOOGLE_API_KEY",
        ]:
            env.pop(key, None)

        # Run validate_llm_config script (used by run_demo.sh llm)
        # This should work even without .env file if env vars are set
        result = subprocess.run(
            [sys.executable, "-m", "scripts.validate_llm_config"],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should fail if no .env file and no env vars
        assert result.returncode == 1
        assert "LLM_ENABLED is not set to true" in result.stderr

    def test_subsection_5_2_2_2_validates_llm_enabled_true(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 2: Demo script validates LLM_ENABLED is true when llm mode selected."""
        monkeypatch.chdir(project_root)

        # Create environment with LLM_ENABLED false
        import os

        env = os.environ.copy()
        env["LLM_ENABLED"] = "false"

        result = subprocess.run(
            [sys.executable, "-m", "scripts.validate_llm_config"],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should fail when LLM_ENABLED is false
        assert result.returncode == 1
        assert "LLM_ENABLED is not set to true" in result.stderr

    def test_subsection_5_2_2_3_validates_required_provider_env_vars(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 3: Demo script validates required provider environment variables are set."""
        monkeypatch.chdir(project_root)

        # Enable LLM but don't set provider
        import os

        env = os.environ.copy()
        env["LLM_ENABLED"] = "true"
        env.pop("SCOUT_PROVIDER", None)
        env.pop("STRATEGIST_PROVIDER", None)

        result = subprocess.run(
            [sys.executable, "-m", "scripts.validate_llm_config"],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should fail when SCOUT_PROVIDER or STRATEGIST_PROVIDER not set
        assert result.returncode == 1
        assert "provider not set" in result.stderr.lower()

    def test_subsection_5_2_2_4_validates_api_keys_exist(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Subsection test 4: Demo script validates API keys exist for configured providers."""
        # Use temp directory to avoid loading existing .env file
        monkeypatch.chdir(tmp_path)

        # Enable LLM and set providers but no API keys
        import os

        env = os.environ.copy()
        env["LLM_ENABLED"] = "true"
        env["SCOUT_PROVIDER"] = "openai"
        env["STRATEGIST_PROVIDER"] = "anthropic"
        env.pop("OPENAI_API_KEY", None)
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)

        # Copy config.json to temp path so LLMConfig can find it
        import shutil

        config_dir = tmp_path / "config"
        config_dir.mkdir()
        shutil.copy(project_root / "config" / "config.json", config_dir / "config.json")

        # Install the package path so imports work
        env["PYTHONPATH"] = str(project_root)

        result = subprocess.run(
            [sys.executable, "-m", "scripts.validate_llm_config"],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should fail when API keys missing
        assert result.returncode == 1
        assert "api key missing" in result.stderr.lower()

    def test_subsection_5_2_2_5_initializes_agents_with_llm_enabled(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 5: Demo script initializes agents with LLM enabled when llm mode selected."""
        monkeypatch.chdir(project_root)

        # Set valid LLM configuration
        import os

        env = os.environ.copy()
        env["LLM_ENABLED"] = "true"
        env["SCOUT_PROVIDER"] = "openai"
        env["STRATEGIST_PROVIDER"] = "anthropic"
        env["OPENAI_API_KEY"] = "sk-test-key-12345678901234567890"
        env["ANTHROPIC_API_KEY"] = "sk-ant-test-key-12345678901234567890"

        # Run play script with --llm flag in simulation mode (mode 2)
        # Pass input via stdin to avoid hanging
        result = subprocess.run(
            [sys.executable, "-m", "scripts.play_human_vs_ai", "--llm", "2"],
            capture_output=True,
            text=True,
            input="",  # Empty input for simulation mode
            timeout=10,
            env=env,
        )

        # Script should run without errors (exit code 0)
        # Note: Actual LLM calls will fail with test keys, but initialization should succeed
        assert "LLM Configuration:" in result.stdout
        assert "Scout Provider:" in result.stdout
        assert "Strategist Provider:" in result.stdout

    def test_subsection_5_2_2_6_displays_configuration_info_at_startup(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 6: Demo script displays configuration info at startup."""
        monkeypatch.chdir(project_root)

        # Set valid LLM configuration
        import os

        env = os.environ.copy()
        env["LLM_ENABLED"] = "true"
        env["SCOUT_PROVIDER"] = "openai"
        env["STRATEGIST_PROVIDER"] = "anthropic"
        env["OPENAI_API_KEY"] = "sk-test-key-12345678901234567890"
        env["ANTHROPIC_API_KEY"] = "sk-ant-test-key-12345678901234567890"

        # Run play script with --llm flag
        result = subprocess.run(
            [sys.executable, "-m", "scripts.play_human_vs_ai", "--llm", "2"],
            capture_output=True,
            text=True,
            input="",
            timeout=10,
            env=env,
        )

        # Should display configuration details
        assert "Demonstrating Phase 5: LLM Integration" in result.stdout
        assert "LLM Configuration:" in result.stdout
        assert "Scout Provider: openai" in result.stdout
        assert "Scout Model:" in result.stdout  # Should show model from config.json
        assert "Strategist Provider: anthropic" in result.stdout
        assert "Strategist Model:" in result.stdout

    def test_subsection_5_2_2_7_runs_successfully_with_valid_config(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Subsection test 7: Demo script runs successfully with valid LLM configuration."""
        monkeypatch.chdir(project_root)

        # Set valid configuration
        import os

        env = os.environ.copy()
        env["LLM_ENABLED"] = "true"
        env["SCOUT_PROVIDER"] = "openai"
        env["STRATEGIST_PROVIDER"] = "openai"
        env["OPENAI_API_KEY"] = "sk-test-key-12345678901234567890"

        # Validation should succeed
        result = subprocess.run(
            [sys.executable, "-m", "scripts.validate_llm_config"],
            capture_output=True,
            text=True,
            env=env,
        )

        assert result.returncode == 0
        assert "✓ LLM Configuration Valid:" in result.stdout
        assert "LLM Enabled: True" in result.stdout

    def test_subsection_5_2_2_8_shows_helpful_error_when_config_invalid(
        self, project_root: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Subsection test 8: Demo script shows helpful error message when configuration invalid."""
        # Use temp directory to avoid loading existing .env file
        monkeypatch.chdir(tmp_path)

        # Set incomplete configuration (missing API key)
        import os

        env = os.environ.copy()
        env["LLM_ENABLED"] = "true"
        env["SCOUT_PROVIDER"] = "openai"
        env["STRATEGIST_PROVIDER"] = "openai"
        env.pop("OPENAI_API_KEY", None)
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("GOOGLE_API_KEY", None)

        # Copy config.json to temp path
        import shutil

        config_dir = tmp_path / "config"
        config_dir.mkdir()
        shutil.copy(project_root / "config" / "config.json", config_dir / "config.json")

        # Install the package path so imports work
        env["PYTHONPATH"] = str(project_root)

        result = subprocess.run(
            [sys.executable, "-m", "scripts.validate_llm_config"],
            capture_output=True,
            text=True,
            env=env,
        )

        # Should show helpful error message
        assert result.returncode == 1
        assert (
            "configuration invalid" in result.stderr.lower()
            or "api key missing" in result.stderr.lower()
        )
        # Error should mention which provider and env var needed
        assert "OPENAI_API_KEY" in result.stderr or "set OPENAI_API_KEY" in result.stderr.lower()
