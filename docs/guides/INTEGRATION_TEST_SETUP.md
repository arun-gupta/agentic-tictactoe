# Integration Test Setup Guide

This guide walks you through setting up and running integration tests with real LLM API keys.

## Prerequisites

1. **Python environment** with dependencies installed:
   ```bash
   pip install -e ".[dev]"
   ```

2. **API Keys** from at least one LLM provider:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys
   - Google Gemini: https://aistudio.google.com/app/apikey

## Step-by-Step Setup

### Step 1: Create `.env` File

Copy the example file:
```bash
cp .env.example .env
```

### Step 2: Get API Keys

#### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. **Important**: Save it immediately - you won't see it again!

#### Anthropic API Key
1. Go to https://console.anthropic.com/settings/keys
2. Sign in or create an account
3. Click "Create Key"
4. Copy the key (starts with `sk-ant-`)
5. **Important**: Save it immediately - you won't see it again!

#### Google Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Copy the key (no specific prefix)
6. **Important**: Save it immediately - you won't see it again!

### Step 3: Add Keys to `.env` File

Edit `.env` file and replace the placeholder values:

```bash
# LLM API Keys
# Copy this file to .env and fill in your API keys
# Priority: .env file > environment variables

# OpenAI API Key
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini API Key
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Security Note**:
- Never commit `.env` file to git (it's in `.gitignore`)
- Don't share your API keys
- Rotate keys if accidentally exposed

### Step 4: Verify API Key Loading

Test that your keys are loaded correctly:
```bash
python scripts/test_api_keys.py
```

Expected output:
```
✅ All core API key infrastructure tests passed!
```

If you see "SKIP (no .env file)" for "Real .env File" test, that's normal if you haven't created `.env` yet.

### Step 5: Run Integration Tests

#### Test All Providers
```bash
python scripts/test_llm_providers.py
```

#### Test Specific Provider
```bash
# Test only OpenAI
python scripts/test_llm_providers.py openai

# Test only Anthropic
python scripts/test_llm_providers.py anthropic

# Test only Gemini
python scripts/test_llm_providers.py gemini
```

## Expected Output

### Successful Test Output
```
============================================================
LLM Provider Integration Tests
============================================================

This script tests LLM providers with real API calls.
Make sure API keys are set in .env file or environment variables.

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

============================================================
Test Summary
============================================================
OpenAI: ✅ PASS
Anthropic: ✅ PASS
Gemini: ✅ PASS
Pydantic AI Agents: ✅ PASS

Total: 4/4 tests passed
```

### Missing API Key Output
```
============================================================
Testing OpenAI Provider
============================================================
❌ OPENAI_API_KEY not found. Skipping OpenAI tests.
```

This is expected if you haven't added that provider's key to `.env`.

## Troubleshooting

### "API key not found" Error

**Problem**: Test script can't find API keys

**Solutions**:
1. Verify `.env` file exists in project root:
   ```bash
   ls -la .env
   ```

2. Check key format (no quotes, no spaces):
   ```bash
   # ✅ Correct
   OPENAI_API_KEY=sk-proj-abc123...

   # ❌ Wrong (quotes)
   OPENAI_API_KEY="sk-proj-abc123..."

   # ❌ Wrong (spaces)
   OPENAI_API_KEY = sk-proj-abc123...
   ```

3. Verify keys are loaded:
   ```bash
   python scripts/test_api_keys.py
   ```

4. Try environment variable instead:
   ```bash
   export OPENAI_API_KEY=sk-proj-abc123...
   python scripts/test_llm_providers.py openai
   ```

### "Model not supported" Error

**Problem**: Model name doesn't match config

**Solution**: Check `config/config.json` has the correct model names:
```json
{
  "llm": {
    "providers": {
      "openai": {
        "models": ["gpt-5.2"]
      },
      "anthropic": {
        "models": ["claude-haiku-4-5-20251001", "claude-haiku-4-5"]
      },
      "gemini": {
        "models": ["gemini-3-flash-preview", "gemini-3-flash"]
      }
    }
  }
}
```

### "Rate limit" or "Timeout" Error

**Problem**: API rate limits or network issues

**Solutions**:
1. Wait a few seconds and retry
2. Check your API key has sufficient quota/credits
3. Verify network connectivity
4. Check provider status pages:
   - OpenAI: https://status.openai.com/
   - Anthropic: https://status.anthropic.com/
   - Google: https://status.cloud.google.com/

### "Insufficient Quota" or "Exceeded Quota" Error (429)

**Problem**: API key has no remaining quota/credits or billing not set up

**Error Message Example**:
```
Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details.', 'type': 'insufficient_quota'}}
```

**Solutions**:

1. **OpenAI**:
   - Check billing: https://platform.openai.com/account/billing
   - Add payment method if needed
   - Check usage limits: https://platform.openai.com/account/limits
   - Free tier may have expired or been exhausted

2. **Anthropic**:
   - Check billing: https://console.anthropic.com/settings/billing
   - Verify account has credits/quota
   - Check usage dashboard

3. **Google Gemini**:
   - Check billing: https://console.cloud.google.com/billing
   - Verify API is enabled in Google Cloud Console
   - Check quota limits: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

4. **Alternative**: Try a different provider if you have keys for others:
   ```bash
   python scripts/test_llm_providers.py anthropic
   python scripts/test_llm_providers.py gemini
   ```

**Note**: This error means the integration test is working correctly - it's successfully making API calls, but the provider is rejecting them due to billing/quota issues.

### "Authentication error" (401/403)

**Problem**: Invalid or expired API key

**Solutions**:
1. Verify key is correct (no typos, full key copied)
2. Check key hasn't expired or been revoked
3. Verify key has correct permissions
4. Generate a new key if needed

### Deprecation Warning (Gemini)

**Problem**: `FutureWarning` about `google.generativeai` package

**Solution**: This is expected and documented. See implementation plan section 5.0.4 for migration plan. The warning doesn't affect functionality.

## Cost Estimates

Running integration tests incurs small costs:

| Provider | Model | Estimated Cost per Test Run |
|----------|-------|----------------------------|
| OpenAI | gpt-5.2 | ~$0.01-0.05 |
| Anthropic | Claude Haiku 4.5 | ~$0.01-0.03 |
| Gemini | Gemini 3 Flash | ~$0.001-0.01 |

**Total for full test suite**: ~$0.02-0.09 per run

These are minimal costs for integration testing. Unit tests use mocks and cost nothing.

## Testing Strategy

### Recommended Approach

1. **Start with one provider**: Test with just one API key first (e.g., OpenAI)
   ```bash
   python scripts/test_llm_providers.py openai
   ```

2. **Verify it works**: Ensure you see successful API calls

3. **Add more providers**: Gradually add other API keys as needed

4. **Test Pydantic AI agents**: Once at least one provider works, test agents:
   ```bash
   python scripts/test_llm_providers.py
   ```

### CI/CD Considerations

- **Don't run integration tests in CI/CD** by default (they require real API keys and cost money)
- Use mocked unit tests for CI/CD: `pytest tests/unit/llm/`
- Integration tests are for local development and manual verification

## Next Steps

After successfully running integration tests:

1. ✅ Verify all providers work correctly
2. ✅ Confirm API key loading infrastructure is functioning
3. ✅ Validate Pydantic AI agents return structured outputs
4. ⏸️ Proceed to Phase 5.1: Agent LLM Integration

## Additional Resources

- [LLM Testing Guide](./LLM_TESTING.md) - Comprehensive testing documentation
- [Implementation Plan](../implementation-plan.md#phase-50-llm-provider-abstraction) - Phase 5.0 details
- [API Key Infrastructure Tests](../scripts/test_api_keys.py) - Test key loading without API calls
