#!/bin/bash

set -euo pipefail

PROVIDERS=("openai" "anthropic" "gemini")
FAILED=()
PASSED=()

echo "Testing each provider with both Scout and Strategist..."
echo ""

for provider in "${PROVIDERS[@]}"; do
  echo "========================================"
  echo "Testing: $provider (Scout + Strategist)"
  echo "========================================"

  if ./run_tests.sh --llm-live --providers "$provider,$provider"; then
    echo "✅ $provider PASSED"
    PASSED+=("$provider")
  else
    echo "❌ $provider FAILED"
    FAILED+=("$provider")
  fi

  echo ""
done

echo "========================================"
echo "SUMMARY"
echo "========================================"
echo "Passed (${#PASSED[@]}): ${PASSED[*]:-none}"
echo "Failed (${#FAILED[@]}): ${FAILED[*]:-none}"

if [ ${#FAILED[@]} -eq 0 ]; then
  echo ""
  echo "✅ All providers passed!"
  exit 0
else
  echo ""
  echo "❌ Some providers failed"
  exit 1
fi
