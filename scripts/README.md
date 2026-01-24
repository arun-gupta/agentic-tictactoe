# Demo Scripts

Demonstration scripts showing implemented phase capabilities.

## Run Demo

```bash
# Default: Human vs Agent (Phase 3 - Rule-based Agent System)
./run_demo.sh

# Human vs Agent (Phase 3)
./run_demo.sh h2agent

# Human vs Human (Phase 2)
./run_demo.sh h2h

# Play via REST API (Phase 4)
./run_demo.sh api

# Interactive menu
./run_demo.sh interactive
```

## Available Demos

### Human vs Human Game

Demonstrates Phase 2 (Game Engine):
- Game rules enforcement (win/draw detection)
- Move validation
- State management
- Random valid moves (stateless gameplay)

**Run:** `python scripts/play_human_vs_human.py`

### Human vs Agent Game

Demonstrates Phase 3 (Rule-based Agent System):
- **Note**: This uses rule-based agents (not LLM-based AI). LLM integration comes in Phase 5.
- Agent Pipeline orchestration (Scout → Strategist → Executor)
- Scout Agent: Rule-based board analysis, threat/opportunity detection
- Strategist Agent: Priority-based move selection using rule-based logic
- Executor Agent: Move validation and execution with fallback strategies
- Fallback strategies for timeouts and failures
- Two modes: Interactive (human input) or Simulation (auto)

**Run:** `python scripts/play_human_vs_ai.py`

### Play via REST API

Demonstrates Phase 4 (REST API Layer):
- Complete game via HTTP requests
- All API endpoints (POST /api/game/new, POST /api/game/move, GET /api/game/status)
- Error handling (invalid moves, out of bounds, occupied cells)
- Game board display from API responses
- AI move execution details (position, reasoning, execution time)
- Interactive gameplay with human input

**Note:** The FastAPI server will be automatically started by `run_demo.sh` if it's not already running.
If running the script directly, start the server manually with: `uvicorn src.api.main:app --reload`

**Run:** `./run_demo.sh api` (recommended - automatically starts server if needed) or `python scripts/play_via_api.py`

### Test LLM Providers

Demonstrates Phase 5.0 (LLM Integration):
- Tests OpenAI, Anthropic, and Google Gemini providers with real API calls
- Tests Pydantic AI agents (Scout and Strategist) with structured outputs
- Requires API keys in `.env` file or environment variables
- Validates LLM provider abstraction and Pydantic AI integration

**Prerequisites:**
- Set up `.env` file with API keys
- **Detailed Setup**: See [Integration Test Setup Guide](../docs/guides/INTEGRATION_TEST_SETUP.md) for step-by-step instructions
- **Quick Setup**: Copy `.env.example` to `.env` and add your API keys
- At least one API key must be configured (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY)

**Run:**
```bash
# Test all available providers
python scripts/test_llm_providers.py

# Test specific provider
python scripts/test_llm_providers.py openai
python scripts/test_llm_providers.py anthropic
python scripts/test_llm_providers.py gemini
```

**Note**: These tests make real API calls and incur small costs (~$0.01-0.05 per test run). See setup guide for details.

### Run LLM Integration Tests (pytest)

Runs the pytest-based LLM integration suite under `tests/integration/llm/`.

**Run:**
```bash
# Non-live (no network calls)
./run_tests.sh --llm

# Live (real API calls; opt-in; may incur cost)
./run_tests.sh --llm-live

# Live, but only for selected providers
./run_tests.sh --llm-live --providers openai,anthropic
```

### Test API Key Infrastructure

Verifies that API key loading works correctly (Phase 5.0):
- Tests loading from `.env` file
- Tests loading from environment variables
- Tests priority order (.env file > environment variables)
- Tests missing key handling
- Tests provider integration

**Run:** `python scripts/test_api_keys.py`

**Note:** This test does NOT make real API calls - it only tests the key loading mechanism. Safe to run without API keys.
