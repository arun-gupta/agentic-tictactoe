# Agent LLM Integration Tests

Live integration tests that make **real LLM API calls** to verify end-to-end agent functionality.

## ⚠️ Cost Warning

These tests make real API calls and **will incur costs**:
- Scout analysis: ~500-1000 tokens (~$0.001-0.01 per call)
- Strategist planning: ~300-800 tokens (~$0.001-0.01 per call)
- Full pipeline: Both agents (~$0.002-0.02 per test)

**Estimated cost for full test suite**: $0.10-0.50 depending on provider and model

## Prerequisites

1. **Enable LLM** in `.env`:
   ```bash
   LLM_ENABLED=true
   ```

2. **Configure provider** (choose one or more):
   ```bash
   # For Scout
   SCOUT_PROVIDER=gemini

   # For Strategist
   STRATEGIST_PROVIDER=gemini
   ```

3. **Set API key** for your provider:
   ```bash
   # Gemini
   GOOGLE_API_KEY=your_key_here

   # OpenAI
   OPENAI_API_KEY=sk-your_key_here

   # Anthropic
   ANTHROPIC_API_KEY=sk-ant-your_key_here
   ```

4. **Enable live tests** (required to run):
   ```bash
   export RUN_LIVE_LLM_TESTS=1
   ```

## Running Tests

### Run all live agent integration tests
```bash
RUN_LIVE_LLM_TESTS=1 pytest -m live_llm tests/integration/agents/
```

### Run with verbose output
```bash
RUN_LIVE_LLM_TESTS=1 pytest -m live_llm -v -s tests/integration/agents/
```

### Run specific test class
```bash
# Scout tests only
RUN_LIVE_LLM_TESTS=1 pytest -m live_llm tests/integration/agents/ -k TestScout

# Strategist tests only
RUN_LIVE_LLM_TESTS=1 pytest -m live_llm tests/integration/agents/ -k TestStrategist

# Pipeline tests only
RUN_LIVE_LLM_TESTS=1 pytest -m live_llm tests/integration/agents/ -k TestPipeline
```

### Run single test
```bash
RUN_LIVE_LLM_TESTS=1 pytest -m live_llm tests/integration/agents/ \
  -k test_pipeline_executes_with_llm_end_to_end -v -s
```

## Test Coverage

### Scout Integration (3 tests)
- ✓ `test_scout_analyzes_opening_position_with_llm` - Opening position analysis
- ✓ `test_scout_detects_threat_with_llm` - Threat detection
- ✓ `test_scout_detects_opportunity_with_llm` - Opportunity detection

### Strategist Integration (2 tests)
- ✓ `test_strategist_plans_opening_move_with_llm` - Opening move planning
- ✓ `test_strategist_blocks_threat_with_llm` - Threat blocking

### Pipeline Integration (3 tests)
- ✓ `test_pipeline_executes_with_llm_end_to_end` - Full pipeline execution
- ✓ `test_pipeline_handles_threat_scenario_with_llm` - Threat scenario
- ✓ `test_pipeline_handles_midgame_complexity_with_llm` - Complex midgame

**Total**: 8 live integration tests

## What These Tests Verify

### Unit Tests (Mocked) vs Integration Tests (Live)

| Aspect | Unit Tests | Integration Tests |
|--------|-----------|-------------------|
| LLM Calls | Mocked | **Real API calls** |
| API Keys | Not required | **Required** |
| Speed | Fast (~1s total) | Slower (~10-30s total) |
| Cost | Free | **$0.10-0.50** |
| CI | Always run | Opt-in only |
| Purpose | Test behavior/wiring | **Verify actual LLM works** |

### Integration Tests Verify:

1. **Real LLM Communication**:
   - Agents successfully call OpenAI/Anthropic/Gemini APIs
   - API keys work correctly
   - Network connectivity and authentication

2. **Structured Output Parsing**:
   - LLMs return valid JSON matching Pydantic models
   - BoardAnalysis and Strategy models parse correctly
   - No schema validation errors

3. **LLM Reasoning Quality**:
   - Scout detects actual threats and opportunities
   - Strategist makes sensible move decisions
   - Pipeline produces valid game moves

4. **End-to-End Flow**:
   - Configuration → Scout → Strategist → Executor works
   - Timeouts and retries work with real API latency
   - Error handling works with actual API errors

5. **Provider Compatibility**:
   - Each provider (OpenAI, Anthropic, Gemini) works correctly
   - Different models return valid responses
   - Provider-specific quirks are handled

## CI/CD Integration

These tests are **NOT run in CI by default** because:
- They require API keys (security risk)
- They cost money
- They're slower than unit tests

To run in CI (optional):
1. Add API keys as CI secrets
2. Set `RUN_LIVE_LLM_TESTS=1` in CI environment
3. Run as separate job after unit tests pass
4. Use budget limits to prevent runaway costs

## Example Output

```
$ RUN_LIVE_LLM_TESTS=1 pytest -m live_llm tests/integration/agents/ -v -s

tests/integration/agents/test_agent_llm_integration.py::TestScoutLiveIntegration::test_scout_analyzes_opening_position_with_llm
✓ Scout analysis completed in 1234.56ms
  Game phase: opening
  Board eval: 0.00
  Strategic moves: 5
PASSED

tests/integration/agents/test_agent_llm_integration.py::TestStrategistLiveIntegration::test_strategist_plans_opening_move_with_llm
✓ Strategist planned move at (1, 1)
  Priority: MovePriority.CENTER_CONTROL
  Confidence: 0.85
  Execution time: 987.65ms
PASSED

tests/integration/agents/test_agent_llm_integration.py::TestPipelineLiveIntegration::test_pipeline_executes_with_llm_end_to_end
✓ Pipeline completed successfully
  Selected move: (1, 1)
  Priority used: MovePriority.CENTER_CONTROL
  Total time: 2345.67ms
  Reasoning: Center control is the strongest opening move in tic-tac-toe, providing maximum flexibility...
PASSED

========================= 8 passed in 18.45s =========================
```

## Troubleshooting

### Tests skip with "Set RUN_LIVE_LLM_TESTS=1"
Solution: Export the environment variable before running tests

### Tests skip with "LLM_ENABLED=true must be set"
Solution: Add `LLM_ENABLED=true` to your `.env` file

### Tests skip with "Invalid LLM configuration: API key missing"
Solution: Set the API key for your configured provider in `.env`

### Tests fail with authentication errors
Solution: Verify your API key is valid and has sufficient quota

### Tests timeout
Solution:
- Check network connectivity
- Some providers may be slower - increase timeout if needed
- Verify API key has rate limit quota remaining

## Related Documentation

- **Unit Tests**: `tests/unit/agents/test_*_llm.py` - Mocked LLM tests
- **Provider Tests**: `tests/integration/llm/test_live_llm_providers.py` - Basic provider tests
- **LLM Testing Guide**: `docs/guides/LLM_TESTING.md` - Complete testing strategy
- **Configuration**: `docs/guides/LLM_CONFIGURATION.md` - Setting up providers
