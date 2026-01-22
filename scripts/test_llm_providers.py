#!/usr/bin/env python3
"""Test script for LLM providers with actual API calls.

This script tests the LLM providers (OpenAI, Anthropic, Google Gemini) with real API calls.
Requires API keys to be set in .env file or environment variables.

Usage:
    python scripts/test_llm_providers.py [provider]

    provider: openai, anthropic, gemini (default: test all available)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.llm_config import get_llm_config  # noqa: E402
from src.llm.anthropic_provider import AnthropicProvider  # noqa: E402
from src.llm.gemini_provider import GeminiProvider  # noqa: E402
from src.llm.openai_provider import OpenAIProvider  # noqa: E402
from src.utils.env_loader import get_api_key  # noqa: E402


def test_openai_provider() -> bool:
    """Test OpenAI provider with real API call."""
    print("\n" + "=" * 60)
    print("Testing OpenAI Provider")
    print("=" * 60)

    api_key = get_api_key("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found. Skipping OpenAI tests.")
        return False

    try:
        provider = OpenAIProvider(api_key=api_key)
        config = get_llm_config()
        models = config.get_supported_models("openai")

        if not models:
            print("❌ No OpenAI models configured in config.json")
            return False

        model = list(models)[0]
        print(f"Using model: {model}")

        prompt = "Say 'Hello from OpenAI!' in exactly 5 words."
        print(f"Prompt: {prompt}")

        response = provider.generate(
            prompt=prompt,
            model=model,
            max_tokens=50,
            temperature=0.7,
        )

        print(f"✅ Response: {response.text}")
        print(f"   Tokens used: {response.tokens_used}")
        print(f"   Latency: {response.latency_ms:.2f}ms")
        print(f"   Model: {model}")
        print("   Provider: anthropic")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_anthropic_provider() -> bool:
    """Test Anthropic provider with real API call."""
    print("\n" + "=" * 60)
    print("Testing Anthropic Provider")
    print("=" * 60)

    api_key = get_api_key("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found. Skipping Anthropic tests.")
        return False

    try:
        provider = AnthropicProvider(api_key=api_key)
        config = get_llm_config()
        models = config.get_supported_models("anthropic")

        if not models:
            print("❌ No Anthropic models configured in config.json")
            return False

        model = list(models)[0]
        print(f"Using model: {model}")

        prompt = "Say 'Hello from Anthropic!' in exactly 5 words."
        print(f"Prompt: {prompt}")

        response = provider.generate(
            prompt=prompt,
            model=model,
            max_tokens=50,
            temperature=0.7,
        )

        print(f"✅ Response: {response.text}")
        print(f"   Tokens used: {response.tokens_used}")
        print(f"   Latency: {response.latency_ms:.2f}ms")
        print(f"   Model: {model}")
        print("   Provider: anthropic")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_gemini_provider() -> bool:
    """Test Google Gemini provider with real API call."""
    print("\n" + "=" * 60)
    print("Testing Google Gemini Provider")
    print("=" * 60)

    api_key = get_api_key("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found. Skipping Gemini tests.")
        return False

    try:
        provider = GeminiProvider(api_key=api_key)
        config = get_llm_config()
        models = config.get_supported_models("gemini")

        if not models:
            print("❌ No Gemini models configured in config.json")
            return False

        # Use first model from config (config is the single source of truth)
        model = list(models)[0]
        print(f"Using model: {model}")

        prompt = "Say 'Hello from Gemini!' in exactly 5 words."
        print(f"Prompt: {prompt}")

        response = provider.generate(
            prompt=prompt,
            model=model,
            max_tokens=50,
            temperature=0.7,
        )

        print(f"✅ Response: {response.text}")
        print(f"   Tokens used: {response.tokens_used}")
        print(f"   Latency: {response.latency_ms:.2f}ms")
        print(f"   Model: {model}")
        print("   Provider: gemini")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_pydantic_ai_agents() -> bool:
    """Test Pydantic AI agents with real API calls."""
    print("\n" + "=" * 60)
    print("Testing Pydantic AI Agents")
    print("=" * 60)

    # Try to find any available provider
    providers = ["openai", "anthropic", "gemini"]
    provider_available = None

    for provider_name in providers:
        api_key_name = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY",
        }[provider_name]

        if get_api_key(api_key_name):
            provider_available = provider_name
            break

    if not provider_available:
        print("❌ No API keys found. Skipping Pydantic AI agent tests.")
        return False

    try:
        from src.domain.agent_models import BoardAnalysis, Strategy
        from src.domain.models import Board, GameState, Position
        from src.llm.pydantic_ai_agents import create_scout_agent, create_strategist_agent

        print(f"Using provider: {provider_available}")

        # Test Scout Agent
        print("\n--- Testing Scout Agent ---")
        scout_agent = create_scout_agent(provider=provider_available)

        # Create a test game state
        board = Board()
        board.set_cell(Position(row=0, col=0), "X")
        board.set_cell(Position(row=1, col=1), "O")
        board.set_cell(Position(row=0, col=1), "X")

        game_state = GameState(
            board=board,
            player_symbol="X",
            ai_symbol="O",
            move_count=3,
        )

        print(
            f"Game state: Move {game_state.move_count}, Current player: {game_state.get_current_player()}"
        )
        print("Board:")
        for row in range(3):
            print(f"  {[board.get_cell(Position(row=row, col=col)) for col in range(3)]}")

        # Run Scout agent (this will make a real LLM call)
        print("\nCalling Scout agent (this may take a few seconds)...")
        result = scout_agent.run_sync(
            f"Analyze this Tic-Tac-Toe board state:\n{game_state.board}\n"
            f"Current player: {game_state.get_current_player()}\n"
            f"Move number: {game_state.move_count}"
        )

        # Pydantic AI returns result with .output attribute
        analysis = result.output
        if isinstance(analysis, BoardAnalysis):
            print("✅ Scout Agent Response:")
            print(f"   Threats detected: {len(analysis.threats)}")
            print(f"   Opportunities: {len(analysis.opportunities)}")
            print(f"   Strategic moves: {len(analysis.strategic_moves)}")
            print(f"   Game phase: {analysis.game_phase}")
            print(f"   Board evaluation: {analysis.board_evaluation_score:.2f}")
        else:
            print(f"❌ Unexpected response type: {type(analysis)}")
            return False

        # Test Strategist Agent
        print("\n--- Testing Strategist Agent ---")
        strategist_agent = create_strategist_agent(provider=provider_available)

        # Use the Scout analysis as input
        scout_analysis = analysis
        print(f"Using Scout analysis with {len(scout_analysis.strategic_moves)} strategic moves")

        print("\nCalling Strategist agent (this may take a few seconds)...")
        strategy_result = strategist_agent.run_sync(
            f"Given this board analysis:\n"
            f"Threats: {len(scout_analysis.threats)}\n"
            f"Opportunities: {len(scout_analysis.opportunities)}\n"
            f"Strategic moves: {len(scout_analysis.strategic_moves)}\n"
            f"Game phase: {scout_analysis.game_phase}\n"
            f"Recommend the best move strategy."
        )

        # Pydantic AI returns result with .output attribute
        strategy = strategy_result.output
        if isinstance(strategy, Strategy):
            print("✅ Strategist Agent Response:")
            print(f"   Primary move: {strategy.primary_move.position}")
            print(f"   Priority: {strategy.primary_move.priority}")
            print(f"   Confidence: {strategy.primary_move.confidence:.2f}")
            print(f"   Reasoning: {strategy.primary_move.reasoning[:100]}...")
            print(f"   Alternatives: {len(strategy.alternatives)}")
            print(f"   Risk assessment: {strategy.risk_assessment}")
        else:
            print(f"❌ Unexpected response type: {type(strategy)}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> None:
    """Run LLM provider tests."""
    print("=" * 60)
    print("LLM Provider Integration Tests")
    print("=" * 60)
    print("\nThis script tests LLM providers with real API calls.")
    print("Make sure API keys are set in .env file or environment variables.\n")

    provider_arg = sys.argv[1] if len(sys.argv) > 1 else None

    results = {}

    if provider_arg == "openai" or provider_arg is None:
        results["OpenAI"] = test_openai_provider()

    if provider_arg == "anthropic" or provider_arg is None:
        results["Anthropic"] = test_anthropic_provider()

    if provider_arg == "gemini" or provider_arg is None:
        results["Gemini"] = test_gemini_provider()

    if provider_arg is None:
        # Test Pydantic AI agents if any provider is available
        results["Pydantic AI Agents"] = test_pydantic_ai_agents()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
