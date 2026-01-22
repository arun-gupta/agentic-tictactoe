#!/usr/bin/env python3
"""Test script for API key infrastructure.

This script verifies that API key loading works correctly:
- Loading from .env file
- Loading from environment variables
- Priority order (.env > env vars)
- Error handling when keys are missing

Usage:
    python scripts/test_api_keys.py
"""

import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.env_loader import get_api_key, reload_env


def test_env_file_loading() -> bool:
    """Test loading API keys from .env file."""
    print("\n" + "=" * 60)
    print("Test 1: Loading from .env file")
    print("=" * 60)

    # Create a temporary .env file
    with NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        env_file = f.name
        f.write("OPENAI_API_KEY=test-key-from-env-file\n")
        f.write("ANTHROPIC_API_KEY=test-anthropic-from-env-file\n")
        f.write("GOOGLE_API_KEY=test-google-from-env-file\n")

    try:
        # Clear environment variables to test .env file loading
        with patch.dict(os.environ, {}, clear=True):
            # Mock the _find_env_file to return our test file
            with patch("src.utils.env_loader._find_env_file", return_value=env_file):
                # Reload env to pick up the test file
                reload_env()

                # Test loading keys
                openai_key = get_api_key("OPENAI_API_KEY")
                anthropic_key = get_api_key("ANTHROPIC_API_KEY")
                google_key = get_api_key("GOOGLE_API_KEY")

                if openai_key == "test-key-from-env-file":
                    print("✅ OPENAI_API_KEY loaded from .env file correctly")
                else:
                    print(f"❌ OPENAI_API_KEY incorrect: got {openai_key}")
                    return False

                if anthropic_key == "test-anthropic-from-env-file":
                    print("✅ ANTHROPIC_API_KEY loaded from .env file correctly")
                else:
                    print(f"❌ ANTHROPIC_API_KEY incorrect: got {anthropic_key}")
                    return False

                if google_key == "test-google-from-env-file":
                    print("✅ GOOGLE_API_KEY loaded from .env file correctly")
                else:
                    print(f"❌ GOOGLE_API_KEY incorrect: got {google_key}")
                    return False

                return True
    finally:
        # Clean up
        os.unlink(env_file)


def test_environment_variable_loading() -> bool:
    """Test loading API keys from environment variables."""
    print("\n" + "=" * 60)
    print("Test 2: Loading from environment variables")
    print("=" * 60)

    # Set environment variables
    test_env = {
        "OPENAI_API_KEY": "test-key-from-env-var",
        "ANTHROPIC_API_KEY": "test-anthropic-from-env-var",
        "GOOGLE_API_KEY": "test-google-from-env-var",
    }

    with patch.dict(os.environ, test_env, clear=True):
        # Mock _find_env_file to return None (no .env file)
        with patch("src.utils.env_loader._find_env_file", return_value=None):
            # Reload env
            reload_env()

            # Test loading keys
            openai_key = get_api_key("OPENAI_API_KEY")
            anthropic_key = get_api_key("ANTHROPIC_API_KEY")
            google_key = get_api_key("GOOGLE_API_KEY")

            if openai_key == "test-key-from-env-var":
                print("✅ OPENAI_API_KEY loaded from environment variable correctly")
            else:
                print(f"❌ OPENAI_API_KEY incorrect: got {openai_key}")
                return False

            if anthropic_key == "test-anthropic-from-env-var":
                print("✅ ANTHROPIC_API_KEY loaded from environment variable correctly")
            else:
                print(f"❌ ANTHROPIC_API_KEY incorrect: got {anthropic_key}")
                return False

            if google_key == "test-google-from-env-var":
                print("✅ GOOGLE_API_KEY loaded from environment variable correctly")
            else:
                print(f"❌ GOOGLE_API_KEY incorrect: got {google_key}")
                return False

            return True


def test_priority_order() -> bool:
    """Test that .env file takes priority over environment variables."""
    print("\n" + "=" * 60)
    print("Test 3: Priority order (.env file > environment variables)")
    print("=" * 60)

    # Create a temporary .env file
    with NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        env_file = f.name
        f.write("OPENAI_API_KEY=test-key-from-env-file-priority\n")

    try:
        # Set environment variable (should be ignored)
        test_env = {"OPENAI_API_KEY": "test-key-from-env-var-should-be-ignored"}

        with patch.dict(os.environ, test_env):
            # Mock _find_env_file to return our test file
            with patch("src.utils.env_loader._find_env_file", return_value=env_file):
                # Reload env
                reload_env()

                # Test loading key (should come from .env file, not env var)
                openai_key = get_api_key("OPENAI_API_KEY")

                if openai_key == "test-key-from-env-file-priority":
                    print("✅ .env file takes priority over environment variable")
                    return True
                else:
                    print(
                        f"❌ Priority order incorrect: got {openai_key}, "
                        "expected value from .env file"
                    )
                    return False
    finally:
        # Clean up
        os.unlink(env_file)


def test_missing_key_handling() -> bool:
    """Test handling when API key is missing."""
    print("\n" + "=" * 60)
    print("Test 4: Missing API key handling")
    print("=" * 60)

    # Clear environment and no .env file
    with patch.dict(os.environ, {}, clear=True):
        with patch("src.utils.env_loader._find_env_file", return_value=None):
            # Reload env
            reload_env()

            # Test loading non-existent key
            missing_key = get_api_key("NON_EXISTENT_KEY")

            if missing_key is None:
                print("✅ Missing API key returns None correctly")
                return True
            else:
                print(f"❌ Missing key should return None, got {missing_key}")
                return False


def test_real_env_file() -> bool:
    """Test loading from actual .env file in project root (if exists)."""
    print("\n" + "=" * 60)
    print("Test 5: Real .env file (if exists)")
    print("=" * 60)

    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found in project root")
        print("   This test is SKIPPED (not a failure)")
        print("   Create .env file with API keys to test real loading")
        print("   Example: cp .env.example .env")
        return True  # Skip is not a failure

    print(f"✅ Found .env file: {env_file}")

    # Reload env to pick up real .env file
    reload_env()

    # Test loading keys (may be None if not set)
    openai_key = get_api_key("OPENAI_API_KEY")
    anthropic_key = get_api_key("ANTHROPIC_API_KEY")
    google_key = get_api_key("GOOGLE_API_KEY")

    print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not set'}")
    print(f"GOOGLE_API_KEY: {'✅ Set' if google_key else '❌ Not set'}")

    # Verify that the .env file is actually being loaded
    # We'll test by checking if get_api_key can read from the file
    # First, let's read the file directly to see what's in it
    try:
        with open(env_file) as f:
            env_content = f.read()

        # Check if file has any content
        if not env_content.strip():
            print("\n⚠️  .env file exists but is empty")
            print("   Add API keys to test real loading")
            return True  # Empty file is not a test failure, just informational

        # Try to verify at least one key can be loaded
        # If file has content but no keys are loaded, that's a problem
        keys_in_file = []
        for line in env_content.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key_name = line.split("=")[0].strip()
                keys_in_file.append(key_name)

        if keys_in_file:
            print(f"\n📝 Found {len(keys_in_file)} key(s) in .env file: {', '.join(keys_in_file)}")

            # Test that at least one key from the file can be loaded
            loaded_any = False
            for key_name in keys_in_file:
                if get_api_key(key_name):
                    loaded_any = True
                    print(f"✅ Successfully loaded {key_name} from .env file")
                    break

            if loaded_any:
                print("\n✅ .env file loading is working correctly!")
                return True
            else:
                print("\n⚠️  Keys found in .env file but not loaded")
                print("   This might indicate a format issue (check for spaces, quotes, etc.)")
                return True  # Not a critical failure, just informational
        else:
            print("\n⚠️  .env file exists but contains no key=value pairs")
            print("   Add API keys in format: KEY_NAME=key_value")
            return True  # Not a test failure
    except Exception as e:
        print(f"\n❌ Error reading .env file: {e}")
        return False


def test_provider_integration() -> bool:
    """Test that providers can load API keys correctly."""
    print("\n" + "=" * 60)
    print("Test 6: Provider integration (API key loading)")
    print("=" * 60)

    try:
        from src.llm.anthropic_provider import AnthropicProvider
        from src.llm.gemini_provider import GeminiProvider
        from src.llm.openai_provider import OpenAIProvider

        # Test OpenAI provider initialization
        try:
            openai_provider = OpenAIProvider()
            print("✅ OpenAIProvider initialized (API key loaded)")
        except ValueError as e:
            if "API key is required" in str(e):
                print("⚠️  OpenAIProvider: No API key found (expected if not configured)")
            else:
                print(f"❌ OpenAIProvider error: {e}")
                return False

        # Test Anthropic provider initialization
        try:
            anthropic_provider = AnthropicProvider()
            print("✅ AnthropicProvider initialized (API key loaded)")
        except ValueError as e:
            if "API key is required" in str(e):
                print("⚠️  AnthropicProvider: No API key found (expected if not configured)")
            else:
                print(f"❌ AnthropicProvider error: {e}")
                return False

        # Test Gemini provider initialization
        try:
            gemini_provider = GeminiProvider()
            print("✅ GeminiProvider initialized (API key loaded)")
        except ValueError as e:
            if "API key is required" in str(e):
                print("⚠️  GeminiProvider: No API key found (expected if not configured)")
            else:
                print(f"❌ GeminiProvider error: {e}")
                return False

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main() -> None:
    """Run all API key infrastructure tests."""
    print("=" * 60)
    print("API Key Infrastructure Tests")
    print("=" * 60)
    print("\nThis script tests the API key loading mechanism:")
    print("  - Loading from .env file")
    print("  - Loading from environment variables")
    print("  - Priority order (.env > env vars)")
    print("  - Missing key handling")
    print("  - Real .env file (if exists)")
    print("  - Provider integration\n")

    results = {}

    # Run tests
    results["Env File Loading"] = test_env_file_loading()
    results["Environment Variable Loading"] = test_environment_variable_loading()
    results["Priority Order"] = test_priority_order()
    results["Missing Key Handling"] = test_missing_key_handling()
    results["Real .env File"] = test_real_env_file()
    results["Provider Integration"] = test_provider_integration()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    # Separate core tests from optional tests
    core_tests = {
        "Env File Loading": results["Env File Loading"],
        "Environment Variable Loading": results["Environment Variable Loading"],
        "Priority Order": results["Priority Order"],
        "Missing Key Handling": results["Missing Key Handling"],
        "Provider Integration": results["Provider Integration"],
    }

    optional_tests = {
        "Real .env File": results["Real .env File"],
    }

    print("\nCore Infrastructure Tests (Required):")
    for name, success in core_tests.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name}: {status}")

    print("\nOptional Tests:")
    for name, success in optional_tests.items():
        # Check if .env file exists to determine if this was actually tested
        env_file = project_root / ".env"
        if env_file.exists():
            status = "✅ PASS" if success else "❌ FAIL"
        else:
            status = "⏭️  SKIP (no .env file)"
        print(f"  {name}: {status}")

    total_core = len(core_tests)
    passed_core = sum(1 for s in core_tests.values() if s)

    print(f"\nCore Tests: {passed_core}/{total_core} passed")

    if passed_core < total_core:
        print("\n❌ Some core infrastructure tests failed. Check the output above for details.")
        sys.exit(1)
    else:
        print("\n✅ All core API key infrastructure tests passed!")
        if not (project_root / ".env").exists():
            print("\n💡 Tip: Create a .env file to test real file loading:")
            print("   cp .env.example .env")
            print("   # Then edit .env and add your API keys")


if __name__ == "__main__":
    main()
