# Quick Start: Integration Tests with Real API Keys

## 5-Minute Setup

1. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Get API keys** (choose at least one):
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys
   - Google: https://aistudio.google.com/app/apikey

3. **Add keys to `.env`:**
   ```bash
   # Edit .env file
   OPENAI_API_KEY=sk-your-key-here
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   GOOGLE_API_KEY=your-key-here
   ```

4. **Verify keys load:**
   ```bash
   python scripts/test_api_keys.py
   ```

5. **Run integration tests:**
   ```bash
   # Test all providers
   python scripts/test_llm_providers.py

   # Or test one provider
   python scripts/test_llm_providers.py openai
   ```

## Expected Output

```
✅ Response: Hello from OpenAI!
   Tokens used: 12
   Latency: 1234.56ms
```

## Troubleshooting

- **"API key not found"**: Check `.env` file exists and keys are correct (no quotes/spaces)
- **"Rate limit"**: Wait a few seconds and retry
- **"Authentication error"**: Verify API key is valid and has credits
- **"Insufficient quota" (429)**:
  - OpenAI: Check billing at https://platform.openai.com/account/billing
  - Add payment method or check usage limits
  - Try a different provider if you have other keys: `python scripts/test_llm_providers.py anthropic`

## Full Guide

For detailed instructions, troubleshooting, and cost estimates, see:
[Integration Test Setup Guide](docs/guides/INTEGRATION_TEST_SETUP.md)
