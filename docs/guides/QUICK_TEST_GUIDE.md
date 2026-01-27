# Quick Test Guide - All Testing Methods

This guide shows all the ways to test the LLM integration in this project.

## Test Types Quick Reference

| Test Type | Speed | Cost | API Keys | Run Command |
|-----------|-------|------|----------|-------------|
| Unit (mocked) | Fast | $0 | No | `./run_tests.sh --unit` |
| Integration (mocked) | Fast | $0 | No | `./run_tests.sh --integration` |
| Live LLM | Slow | $0.50 | **Yes** | `./run_tests.sh --llm-live` |

## 1. Unit Tests (Mocked) - Fast Development ⚡

**Use when**: Developing features, making changes, before every commit

**Run with**:
```bash
# All unit tests
./run_tests.sh --unit

# Specific test file
./run_tests.sh --unit -- tests/unit/agents/test_pipeline_config.py -v

# Watch mode (requires pytest-watch)
pytest-watch tests/unit/
```

**What they test**:
- ✅ Configuration wiring (parameters pass correctly)
- ✅ Agent behavior (retry, fallback, error handling)
- ✅ Logic correctness (no real LLM needed)

**Speed**: ~2-5 seconds total
**Cost**: $0 (no API calls)
**API Keys**: Not required

## 2. Integration Tests (Mocked) - Before Commit 🔍

**Use when**: Before committing, in CI/CD

**Run with**:
```bash
# All integration tests (excludes live LLM)
./run_tests.sh --integration

# All tests except contract and live LLM (default)
./run_tests.sh
```

**What they test**:
- ✅ Component integration
- ✅ API contract validation
- ✅ End-to-end flows (mocked)

**Speed**: ~10-20 seconds total
**Cost**: $0 (no API calls)
**API Keys**: Not required

## 3. Live LLM Tests - Weekly Validation 💰

**Use when**: Weekly verification, before releases, when debugging LLM issues

**Prerequisites**:
1. Set up `.env` file:
   ```bash
   LLM_ENABLED=true
   SCOUT_PROVIDER=gemini
   STRATEGIST_PROVIDER=gemini
   GOOGLE_API_KEY=your_key_here
   ```

2. Verify configuration:
   ```bash
   python scripts/validate_llm_config.py
   ```

**Run with**:
```bash
# All live LLM tests (agents + providers)
./run_tests.sh --llm-live

# Only agent pipeline tests
./run_tests.sh --llm-live -- tests/integration/agents/ -v

# Only provider tests
./run_tests.sh --llm-live -- tests/integration/llm/ -v

# Specific provider only
./run_tests.sh --llm-live --providers gemini

# Multiple providers
./run_tests.sh --llm-live --providers gemini,openai

# Verbose output with details
./run_tests.sh --llm-live -- -v -s
```

**What they test**:
- ✅ Real API calls work (authentication, network)
- ✅ Structured output parsing (Pydantic models)
- ✅ LLM reasoning quality (Scout detects threats, Strategist blocks)
- ✅ End-to-end pipeline with real LLM
- ✅ Provider compatibility (OpenAI, Anthropic, Gemini)

**Test Coverage** (8 agent tests + 3 provider tests = 11 tests):
- Scout: Opening analysis, threat detection, opportunity detection
- Strategist: Opening planning, threat blocking
- Pipeline: End-to-end, threat handling, midgame complexity
- Providers: OpenAI, Anthropic, Gemini basic calls

**Speed**: ~20-40 seconds total
**Cost**: ~$0.50 for full suite (varies by provider)
**API Keys**: **Required**

## 4. Manual Testing - Play the Game 🎮

**Use when**: Testing the complete experience, demoing features

**Run with**:
```bash
# Play against LLM-powered AI
./run_demo.sh ai

# Or run script directly
python scripts/play_human_vs_ai.py

# Simulation mode (watch AI play)
python scripts/play_human_vs_ai.py 2
```

**What this tests**:
- ✅ Complete user experience
- ✅ AI makes intelligent moves
- ✅ Real-time LLM integration
- ✅ Error handling and fallbacks

**Cost**: ~$0.02-0.05 per game
**API Keys**: Required (LLM_ENABLED=true)

## 5. Quick Validation Scripts 🔧

### Check API Keys (No API Calls)
```bash
# Test key loading infrastructure (mocked)
python scripts/test_api_keys.py
```

### Validate LLM Configuration
```bash
# Check configuration validity (no API calls)
python scripts/validate_llm_config.py
```

### Test Providers (Real API Calls)
```bash
# Test all configured providers
python scripts/test_llm_providers.py

# Test specific provider
python scripts/test_llm_providers.py gemini
```

## Recommended Workflows

### During Active Development
```bash
# Run unit tests frequently (fast, free)
./run_tests.sh --unit

# Run on file save with pytest-watch
pytest-watch tests/unit/
```

### Before Committing
```bash
# Run all tests except live LLM (CI equivalent)
./run_tests.sh

# Or be explicit
./run_tests.sh --unit --integration
```

### Weekly Verification
```bash
# Full validation including live LLM
./run_tests.sh --llm-live -- -v -s

# Then play a game manually
./run_demo.sh ai
```

### Before Release
```bash
# All tests including contract
./run_tests.sh --all

# Then live LLM tests
./run_tests.sh --llm-live -- -v -s

# Manual testing
./run_demo.sh ai
```

## CI/CD Configuration

### Standard CI (No API Keys)
```yaml
- name: Run tests
  run: ./run_tests.sh --all
```

### Optional Live LLM CI (With Secrets)
```yaml
- name: Run live LLM tests (optional)
  if: github.ref == 'refs/heads/main'
  env:
    LLM_ENABLED: true
    SCOUT_PROVIDER: gemini
    GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  run: ./run_tests.sh --llm-live
```

## Cost Management

### Free Tests (No API Keys)
- Unit tests: Always run
- Integration tests: Always run
- Contract tests: Always run

**Total cost**: $0

### Paid Tests (API Keys Required)
- Live LLM tests: ~$0.50 per full run
- Manual game: ~$0.02-0.05 per game

**Budget recommendations**:
- Development: Weekly live tests = ~$2/month
- CI/CD: Main branch only = ~$10/month (20 runs)
- Set API budget limits in provider dashboard

## Troubleshooting

### "Executable pytest not found" in pre-commit
```bash
# Run tests without pre-commit hooks
git commit --no-verify
```

### Tests skip with "RUN_LIVE_LLM_TESTS=1 required"
```bash
# Use run_tests.sh which sets this automatically
./run_tests.sh --llm-live
```

### Tests skip with "Invalid LLM configuration"
```bash
# Validate configuration first
python scripts/validate_llm_config.py

# Check .env file
cat .env | grep LLM
cat .env | grep API_KEY
```

### Tests fail with authentication errors
```bash
# Verify API key is valid
python scripts/test_llm_providers.py gemini

# Check key format
# Gemini: Should be ~39 chars
# OpenAI: Should start with sk-
# Anthropic: Should start with sk-ant-
```

## Summary

**For Speed**: Use unit tests (mocked, fast, free)
**For Confidence**: Use live LLM tests (real API calls, weekly)
**For Experience**: Play the game manually (complete integration)

**Cost-Effective Strategy**:
- Daily: Unit tests only ($0)
- Weekly: Full live LLM tests (~$0.50)
- Monthly cost: ~$2-5

All tests are integrated with `./run_tests.sh` for consistent interface! 🎯
