# Agent Context: Agentic Tic-Tac-Toe

This document provides persistent context about the project for AI assistants. It explains architectural decisions, conventions, and domain knowledge that should inform all development work.

---

## Project Overview

**What**: A multi-agent AI system for playing Tic-Tac-Toe, featuring specialized agents that collaborate to make optimal moves.

**Why**: Demonstrates modern AI agent architecture patterns, LLM integration, and production-ready software engineering practices.

**Status**: Phase 5 (LLM Integration) in progress - 12 subsections complete

---

## Architecture

### Multi-Agent System

The system uses **three specialized agents** working in a pipeline:

1. **Scout Agent** (Analysis)
   - Analyzes the current board state
   - Identifies threats and opportunities
   - Can use LLM for deeper analysis or fall back to rule-based logic
   - Location: `src/agents/scout.py`

2. **Strategist Agent** (Planning)
   - Plans the optimal move based on Scout's analysis
   - Evaluates move priorities and strategic value
   - Can use LLM for strategic reasoning or fall back to priority-based logic
   - Location: `src/agents/strategist.py`

3. **Executor Agent** (Execution)
   - Executes the move planned by Strategist
   - Validates move legality
   - Updates game state
   - **Always rule-based** (no LLM)
   - Location: `src/agents/executor.py`

**Pipeline Flow**:
```
Game State → Scout → Analysis → Strategist → Move Plan → Executor → Updated State
```

**Key Insight**: Each agent has a focused responsibility. LLM enhancement is optional and falls back gracefully to rule-based logic.

### LLM Integration

**Framework**: **Pydantic AI** (not LangChain or direct SDK calls)

**Why Pydantic AI**:
- ✅ Built by Pydantic team - seamless integration with Pydantic v2 models
- ✅ Type-safe structured outputs
- ✅ Agent workflow abstractions match our multi-agent architecture
- ✅ Lighter weight than LangChain
- ✅ Better error handling and validation

**Supported Providers**:
1. **OpenAI** - `gpt-5.2` (from config.json)
2. **Anthropic** - `claude-haiku-4-5` (from config.json)
3. **Google Gemini** - `gemini-2.5-flash` (from config.json)

**Provider Architecture**:
- All providers implement `LLMProvider` interface (`src/llm/provider.py`)
- Unified `generate()` method with retry logic and error handling
- API keys loaded from environment variables (see Configuration section)

**Per-Agent Configuration**:
- Scout and Strategist can use **different providers**
- Set via `SCOUT_PROVIDER` and `STRATEGIST_PROVIDER` env vars
- Each agent loads its own config from `config/config.json`

---

## Key Conventions

### Configuration Hierarchy

**Single Source of Truth**: `config/config.json`

```json
{
  "llm": {
    "providers": {
      "openai": {"models": ["gpt-5.2"]},
      "anthropic": {"models": ["claude-haiku-4-5"]},
      "gemini": {"models": ["gemini-2.5-flash"]}
    }
  }
}
```

**CRITICAL RULES**:
1. ✅ **Integration tests**: MUST read models dynamically from `config.json`
2. ✅ **Unit tests**: CAN use hardcoded/mocked model names (for isolated testing)
3. ❌ **NEVER** hardcode model names in integration tests
4. ✅ Use `get_llm_config().get_supported_models(provider)` to read models

**Environment Variables**:
```bash
# LLM Control
LLM_ENABLED=true|false

# Per-Agent Providers
SCOUT_PROVIDER=gemini|openai|anthropic
STRATEGIST_PROVIDER=gemini|openai|anthropic

# API Keys (provider-specific)
GOOGLE_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

**Priority**: Environment variables > .env file > defaults

### Testing Philosophy

**Test Types** (4 levels):

1. **Unit Tests** (`tests/unit/`)
   - Fast, isolated, no external dependencies
   - Mock all external calls
   - 100% coverage on core logic
   - Can use hardcoded model names in mocks

2. **Integration Tests** (`tests/integration/`)
   - Test component integration without external APIs
   - Mock LLM providers, but test real agent logic
   - MUST read models from `config.json` dynamically
   - Mark with `@pytest.mark.integration`

3. **Live LLM Tests** (`tests/integration/llm/`, `tests/integration/agents/`)
   - **Real API calls** - costs money!
   - Opt-in with `RUN_LIVE_LLM_TESTS=1`
   - Mark with `@pytest.mark.live_llm`
   - Run with: `./run_tests.sh --llm-live`

4. **Contract Tests** (`tests/contract/`)
   - Validate API matches OpenAPI spec
   - Use Schemathesis for property-based testing
   - Mark with `@pytest.mark.contract`

**Subsection Test Naming**:
```python
def test_subsection_X_Y_Z_requirement_description() -> None:
    """Test that subsection X.Y.Z implements requirement."""
```

Example: `test_subsection_5_1_1_scout_analyzes_with_llm()`

**Why**: Direct traceability to implementation plan subsections.

### Code Style

**Type Hints**: REQUIRED on all functions
```python
def analyze_board(state: GameState, llm_enabled: bool = False) -> Analysis:
```

**Docstrings**: Google style, REQUIRED on all public functions
```python
def generate(self, prompt: str, model: str) -> LLMResponse:
    """Generate text using LLM.

    Args:
        prompt: The input prompt
        model: Model name from config.json

    Returns:
        LLM response with text, tokens, and latency

    Raises:
        ValueError: If model not supported
    """
```

**Error Handling**: Use custom error codes
```python
# Domain: E_MOVE_OUT_OF_BOUNDS, E_CELL_OCCUPIED, E_GAME_ALREADY_OVER
# API: E_SERVICE_NOT_READY, E_GAME_NOT_FOUND, E_INTERNAL_ERROR
```

**Imports**: Suppress warnings when needed
```python
# Gemini provider uses deprecated google.generativeai
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import google.generativeai as genai
```

---

## File Structure

### Key Locations

```
.
├── src/
│   ├── domain/          # Domain models (GameState, Position, Player)
│   ├── engine/          # Game engine (TicTacToeEngine)
│   ├── agents/          # Agent system (Scout, Strategist, Executor, Pipeline)
│   ├── llm/             # LLM providers (OpenAI, Anthropic, Gemini)
│   ├── config/          # Configuration management (llm_config.py)
│   └── api/             # FastAPI REST endpoints
├── tests/
│   ├── unit/            # Fast isolated tests
│   ├── integration/     # Integration tests (mocked LLM)
│   │   ├── agents/      # Live agent LLM tests (@pytest.mark.live_llm)
│   │   └── llm/         # Live provider smoke tests (@pytest.mark.live_llm)
│   └── contract/        # API contract tests
├── config/
│   └── config.json      # ⭐ SINGLE SOURCE OF TRUTH for models
├── docs/
│   ├── implementation-plan.md  # ⭐ Master implementation plan
│   ├── spec/            # Full specification
│   └── guides/          # Setup and testing guides
├── .claude/
│   └── skills/          # ⭐ Workflow skills (procedural)
└── AGENT.md             # ⭐ This file (contextual knowledge)
```

### Implementation Plan

**Location**: `docs/implementation-plan.md`

**Structure**: 12 phases, each with subsections
- Phase 0-4: ✅ Complete
- Phase 5: 🚧 In progress (12 subsections complete)
- Phase 6-11: ⏸️ Planned

**Subsection Format**: `X.Y.Z` (e.g., 5.1.1, 5.2.2)

**Marking Complete**: Add ✅ emoji after subsection title

---

## Technical Decisions

### Why Pydantic AI over LangChain?

**Decision**: Use Pydantic AI for LLM integration

**Rationale**:
1. Project already uses Pydantic v2 extensively for domain models
2. Pydantic AI provides better type safety and integration
3. Lighter weight - no need for LangChain's complexity
4. Agent workflow abstractions map well to our Scout/Strategist pattern
5. Better structured output handling with Pydantic models

**Trade-off**: Smaller ecosystem, but better fit for our architecture

### Why Per-Agent Provider Configuration?

**Decision**: Allow Scout and Strategist to use different LLM providers

**Rationale**:
1. Experimentation: Compare provider performance on same task
2. Cost optimization: Use cheaper models for Scout, expensive for Strategist
3. Fallback strategy: If one provider is down, other agent can continue
4. A/B testing: Compare same agent with different providers

**Implementation**: `SCOUT_PROVIDER` and `STRATEGIST_PROVIDER` env vars

### Why config.json as Single Source of Truth?

**Decision**: All supported models defined in `config/config.json`, never hardcoded

**Rationale**:
1. Easy model updates without code changes
2. Consistent across all tests and production code
3. Clear validation - unsupported models fail fast
4. Easy to add new models for experimentation

**Enforcement**: Integration tests read from config dynamically

### Why Three Test Types (Unit/Integration/Live)?

**Decision**: Separate unit, integration (mocked LLM), and live LLM tests

**Rationale**:
1. **Unit tests**: Fast feedback, no external dependencies, run in CI always
2. **Integration tests**: Test component wiring without API costs
3. **Live LLM tests**: Validate real API behavior, opt-in, expensive

**Cost management**: Live tests only run when explicitly enabled

---

## Common Pitfalls

### ❌ Hardcoding Model Names in Integration Tests

**Wrong**:
```python
def test_provider_loads_models():
    provider = OpenAIProvider()
    assert "gpt-5.2" in provider.SUPPORTED_MODELS  # ❌ Hardcoded
```

**Right**:
```python
def test_provider_loads_models():
    provider = OpenAIProvider()
    config = get_llm_config()
    expected = config.get_supported_models("openai")
    assert provider.SUPPORTED_MODELS == expected  # ✅ Dynamic
```

### ❌ Forgetting to Clear Environment Variables in Tests

**Problem**: Tests that modify environment variables can leak state

**Wrong**:
```python
def test_config():
    monkeypatch.setenv("LLM_ENABLED", "true")
    # Test passes, but LLM_ENABLED still set from .env file!
```

**Right**:
```python
def test_config(tmp_path):
    monkeypatch.chdir(tmp_path)  # Avoid loading project .env
    monkeypatch.delenv("LLM_ENABLED", raising=False)  # Clear explicitly
    monkeypatch.setenv("LLM_ENABLED", "false")
    # Now test is isolated
```

### ❌ Running Live Tests Without Cost Awareness

**Problem**: Live LLM tests cost money and hit rate limits

**Solution**:
- Use `--providers` flag to test specific provider: `./run_tests.sh --llm-live --providers gemini`
- Start with smoke tests: `tests/integration/llm/test_live_llm_providers.py` (only 16 tokens per test)
- Avoid running full agent tests repeatedly (500-1000 tokens each)
- Free tier limits: Gemini (5 req/min), OpenAI (quota-based)

### ❌ Committing Without Running Quality Checks

**Problem**: CI fails on black/mypy/pytest

**Solution**:
1. Run locally first: `python -m black src/ tests/`
2. Run mypy: `python -m mypy src/ --strict`
3. Run tests: `python -m pytest`
4. Or use skill: `/pre-commit-validation` (if implemented)
5. If pre-commit hooks fail, use `git commit --no-verify` (only when pytest/mypy not in PATH)

### ❌ Adding Type Ignores Without Understanding Why

**Problem**: Mypy errors masked without documenting reason

**Right approach**:
```python
# Gemini SDK has complex union types that don't match perfectly
gemini_model = genai.GenerativeModel(  # type: ignore[attr-defined]
    model,
    safety_settings=safety_settings,  # type: ignore[arg-type]
)
```

**Document**: Add comment explaining WHY the ignore is needed

---

## Development Workflow

### Standard Subsection Implementation

**Use skill**: `/subsection-implementation X.Y.Z` or `/si X.Y.Z`

**What it does**:
1. Reads requirements from implementation plan
2. Creates task tracking
3. Implements code following all patterns
4. Writes subsection tests
5. Runs quality checks (must pass)
6. Updates implementation plan with ✅
7. Commits with proper format
8. Pushes to GitHub

**Example**:
```
/si 5.1.1
```

This implements subsection 5.1.1 end-to-end.

### Git Workflow

**Commit Format**: Conventional Commits
```
<type>(<scope>): <description>

[body with bullet points]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types**:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Test changes
- `refactor` - Code refactoring
- `style` - Formatting (black, etc.)
- `chore` - Maintenance

**Example**:
```
feat(agents): Subsection 5.1.1 - Scout LLM enhancement

- Integrate Pydantic AI for board analysis
- Add LLM fallback to rule-based logic
- Implement structured output parsing

Tests:
- ✅ 8 subsection tests passing
- ✅ Unit tests for analysis logic
- ✅ Integration tests with mocked LLM

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

### Running Tests

**All tests (except live)**:
```bash
./run_tests.sh
```

**Specific test types**:
```bash
./run_tests.sh --unit           # Unit tests only
./run_tests.sh --integration    # Integration tests (mocked LLM)
./run_tests.sh --llm            # Non-live LLM integration tests
./run_tests.sh --llm-live       # Live LLM tests (costs money!)
./run_tests.sh --contract       # Contract tests
```

**With provider filtering**:
```bash
./run_tests.sh --llm-live --providers gemini    # Only Gemini
./run_tests.sh --llm-live --providers openai,anthropic  # Multiple
```

**Direct pytest** (for verbose output):
```bash
python -m pytest tests/integration/llm/test_live_llm_providers.py -v
RUN_LIVE_LLM_TESTS=1 python -m pytest tests/integration/agents/ -v
```

---

## LLM Testing Cost Management

### Cost Estimates (per test)

- **Smoke tests** (`test_live_llm_providers.py`): ~$0.001-0.01 (16 tokens)
- **Scout tests**: ~$0.001-0.01 (500-1000 tokens)
- **Strategist tests**: ~$0.001-0.01 (300-800 tokens)
- **Full agent pipeline**: ~$0.002-0.02 (both agents)

**Full test suite**: ~$0.10-0.50 depending on provider

### Best Practices

1. **Start with smoke tests**: Cheapest way to validate API keys work
2. **Use Gemini for development**: Free tier (5 req/min), good quality
3. **Test one provider at a time**: `--providers gemini`
4. **Avoid repeated full runs**: Run unit/integration (mocked) first
5. **Watch rate limits**: Gemini free tier = 5 requests/minute

### Rate Limits

- **Gemini Free**: 5 requests/minute
- **OpenAI**: Based on quota/tier
- **Anthropic**: Based on quota/tier

**If hitting rate limits**: Use `--providers` to test one provider at a time, or add delays between tests.

---

## FAQ

### Q: Should I use LLM for every agent?

**A**: No. Executor is always rule-based. Scout and Strategist can optionally use LLM with fallback to rule-based logic. LLM is for enhanced intelligence, not required functionality.

### Q: How do I add a new LLM provider?

**A**:
1. Add to `config/config.json` under `llm.providers`
2. Create provider class implementing `LLMProvider` interface
3. Add API key env var to `LLMConfig.API_KEY_ENV_VARS`
4. Add provider factory in agent creation logic
5. Add tests in `tests/unit/llm/test_<provider>_provider.py`
6. Add integration test in `tests/integration/llm/test_llm_provider_config_integration.py`

### Q: Why do some tests use `tmp_path` and `monkeypatch.chdir()`?

**A**: To avoid loading the project's `.env` file. Tests that validate missing config need isolation from the actual project environment.

### Q: When should I use `--no-verify` with git commit?

**A**: Only when pre-commit hooks fail to find `pytest` or `mypy` executables. This is a PATH issue, not a code issue. Always run quality checks manually first.

### Q: How do I know which phase/subsection to work on next?

**A**: Check `docs/implementation-plan.md`. Look for the next subsection without ✅. Currently working on Phase 5 subsections.

### Q: Why does Gemini provider have safety_settings?

**A**: Without lenient safety settings (`BLOCK_NONE`), Gemini can falsely block benign test prompts (like "analyze this tic-tac-toe board"). This is documented in code comments.

---

## Quick Reference

### Key Commands

```bash
# Development
./run_demo.sh bot               # Rule-based bot (no API keys)
./run_demo.sh ai                # LLM-enhanced AI (needs API keys)
python scripts/validate_llm_config.py  # Validate LLM setup

# Testing
./run_tests.sh                  # All tests (no live LLM)
./run_tests.sh --llm-live       # Live LLM tests (costs money!)
./run_tests.sh --llm-live --providers gemini  # Specific provider

# Quality Checks
python -m black src/ tests/     # Format code
python -m mypy src/ --strict    # Type check
python -m pytest                # Run all tests

# Skills
/si 5.1.1                       # Implement subsection 5.1.1
/subsection-implementation 5.2.2  # Full command
```

### Environment Setup

```bash
# Copy template
cp .env.example .env

# Configure (example for Gemini)
LLM_ENABLED=true
SCOUT_PROVIDER=gemini
STRATEGIST_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here

# Verify
python scripts/validate_llm_config.py
```

### Reading the Implementation Plan

**Structure**: `docs/implementation-plan.md`

- Phase X: Major feature area
- X.Y: Section within phase
- X.Y.Z: Specific subsection to implement
- ✅: Marks completed work
- 🚧: In progress
- ⏸️: Not started

**Current Status**: Phase 5.0, 5.1, 5.2 complete (12 subsections)

---

## Last Updated

2026-01-27 - Phase 5 LLM Integration in progress

**Major Changes**:
- Phase 5.0: LLM provider abstraction complete (OpenAI, Anthropic, Gemini)
- Phase 5.1: Scout and Strategist LLM enhancement complete
- Phase 5.2: Configuration and demo script support complete
- 612 tests passing (up from 429 at Phase 4 completion)
