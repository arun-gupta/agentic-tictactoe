# LLM Integration Testing Guide

This guide explains how to test the LLM integrations (Phase 5.0) with real API calls.

## Prerequisites

1. **API Keys**: Set up at least one API key in your `.env` file:
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your API keys:
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   ```

2. **Dependencies**: Ensure all dependencies are installed:
   ```bash
   pip install -e ".[dev]"
   ```

## Testing Methods

### 1. Unit Tests (Mocked - No API Calls)

The unit tests use mocks and don't make real API calls. They verify:
- Provider interface implementation
- Error handling
- Parameter validation
- Response structure

**Run unit tests:**
```bash
pytest tests/unit/llm/ -v
```

### 2. Integration Test Script (Real API Calls)

The `scripts/test_llm_providers.py` script tests LLM providers with **real API calls**. This is useful for:
- Verifying API keys work
- Testing actual LLM responses
- Validating Pydantic AI agent integration
- Measuring real latency and token usage

**Run integration tests:**
```bash
# Test all available providers
python scripts/test_llm_providers.py

# Test specific provider
python scripts/test_llm_providers.py openai
python scripts/test_llm_providers.py anthropic
python scripts/test_llm_providers.py gemini
```

**What it tests:**
- ✅ OpenAI Provider: Real API call with gpt-5.2
- ✅ Anthropic Provider: Real API call with Claude Haiku 4.5
- ✅ Google Gemini Provider: Real API call with Gemini 3 Flash
- ✅ Pydantic AI Agents: Scout and Strategist agents with structured outputs

**Example output:**
```
============================================================
Testing OpenAI Provider
============================================================
Using model: gpt-5.2
Prompt: Say 'Hello from OpenAI!' in exactly 5 words.
✅ Response: Hello from OpenAI!
   Tokens used: 12
   Latency: 1234.56ms
   Model: gpt-5.2
   Provider: openai
```

### 3. Manual Testing via Python REPL

You can also test providers interactively:

```python
from src.llm.openai_provider import OpenAIProvider
from src.utils.env_loader import get_api_key

# Initialize provider
api_key = get_api_key("OPENAI_API_KEY")
provider = OpenAIProvider(api_key=api_key)

# Make a test call
response = provider.generate(
    prompt="Say hello in 5 words",
    model="gpt-5.2",
    max_tokens=50,
    temperature=0.7,
)

print(f"Response: {response.text}")
print(f"Tokens: {response.tokens_used}")
print(f"Latency: {response.latency_ms}ms")
```

### 4. Testing Pydantic AI Agents

Test the Scout and Strategist agents with structured outputs:

```python
from src.llm.pydantic_ai_agents import create_scout_agent, create_strategist_agent
from src.domain.models import Board, GameState, Position

# Create a test game state
board = Board()
board.set_cell(Position(0, 0), "X")
board.set_cell(Position(1, 1), "O")

game_state = GameState(
    board=board,
    player_symbol="X",
    ai_symbol="O",
    move_count=2,
)

# Test Scout agent
scout_agent = create_scout_agent(provider="openai")
result = scout_agent.run_sync(
    f"Analyze this board:\n{game_state.board}\n"
    f"Current player: {game_state.get_current_player()}"
)

print(f"Threats: {len(result.data.threats)}")
print(f"Opportunities: {len(result.data.opportunities)}")
print(f"Game phase: {result.data.game_phase}")
```

## What Gets Tested

### Provider Tests
- ✅ API key loading (from .env or environment variables)
- ✅ Model configuration (from config.json)
- ✅ Real API calls with correct parameters
- ✅ Response parsing (text, tokens, latency)
- ✅ Error handling (timeouts, rate limits, auth errors)
- ✅ Retry logic with exponential backoff

### Pydantic AI Agent Tests
- ✅ Agent creation with correct output types
- ✅ Structured output validation (BoardAnalysis, Strategy)
- ✅ Multi-provider support (OpenAI, Anthropic, Gemini)
- ✅ Auto-selection of provider/model when not specified
- ✅ API key passing to Pydantic AI models

## Troubleshooting

### "API key not found" error
- Check that `.env` file exists in project root
- Verify API key is set correctly (no extra spaces)
- Try setting environment variable directly: `export OPENAI_API_KEY=sk-...`

### "Model not supported" error
- Check `config/config.json` has the model configured
- Verify model name matches exactly (case-sensitive)
- For OpenAI: ensure `gpt-5.2` is in config
- For Anthropic: ensure `claude-haiku-4-5-20251001` is in config
- For Gemini: ensure `gemini-3-flash-preview` is in config

### "Rate limit" or "Timeout" errors
- These are expected during testing - the providers have retry logic
- Check your API key has sufficient quota
- Wait a few seconds and try again

### Pydantic AI agent errors
- Ensure API key is set in environment (Pydantic AI reads from `os.environ`)
- Check that the provider/model is configured in `config.json`
- Verify the output models (BoardAnalysis, Strategy) are correctly imported

## Expected Costs

Testing with real API calls will incur small costs:
- **OpenAI**: ~$0.01-0.05 per test run (gpt-5.2)
- **Anthropic**: ~$0.01-0.03 per test run (Claude Haiku 4.5)
- **Gemini**: ~$0.001-0.01 per test run (Gemini 3 Flash)

These are minimal costs for integration testing. Unit tests use mocks and cost nothing.

## Next Steps

After verifying LLM providers work:
1. ✅ Phase 5.0 is complete (Provider abstraction and Pydantic AI)
2. ⏸️ Phase 5.1: Integrate LLM agents into Scout and Strategist (next phase)

See [Implementation Plan](../implementation-plan.md#phase-51-agent-llm-integration-with-pydantic-ai) for Phase 5.1 details.
