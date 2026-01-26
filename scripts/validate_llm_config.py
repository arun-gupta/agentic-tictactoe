#!/usr/bin/env python3
"""Validate LLM configuration for demo script.

This script validates that the LLM configuration is properly set up:
- .env file exists (optional, can use environment variables)
- LLM_ENABLED is true
- SCOUT_PROVIDER and STRATEGIST_PROVIDER are set
- API keys are present for configured providers

Exit codes:
- 0: Configuration is valid
- 1: Configuration is invalid or incomplete
"""

import sys

from src.config.llm_config import get_llm_config


def validate_llm_config() -> bool:
    """Validate LLM configuration for demo script.

    Returns:
        True if configuration is valid, False otherwise
    """
    config = get_llm_config()

    # Check if LLM is enabled
    llm_config = config.get_config()
    if not llm_config.enabled:
        print("❌ LLM_ENABLED is not set to true", file=sys.stderr)
        return False

    # Validate Scout agent configuration
    is_valid, error_msg = config.validate_agent_config("scout")
    if not is_valid:
        print(f"❌ Scout agent configuration invalid: {error_msg}", file=sys.stderr)
        return False

    # Validate Strategist agent configuration
    is_valid, error_msg = config.validate_agent_config("strategist")
    if not is_valid:
        print(f"❌ Strategist agent configuration invalid: {error_msg}", file=sys.stderr)
        return False

    # Get agent configs to display info
    scout_config = config.get_agent_config("scout")
    strategist_config = config.get_agent_config("strategist")

    print("✓ LLM Configuration Valid:")
    print("  - LLM Enabled: True")
    print(f"  - Scout Provider: {scout_config.provider}")
    print(f"  - Scout Model: {scout_config.model}")
    print(f"  - Strategist Provider: {strategist_config.provider}")
    print(f"  - Strategist Model: {strategist_config.model}")

    return True


def main() -> None:
    """Main entry point."""
    if validate_llm_config():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
