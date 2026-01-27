#!/bin/bash

set -euo pipefail

usage() {
  cat <<'EOF'
Unified test runner (pytest markers).

Usage:
  ./run_tests.sh [--unit] [--integration] [--contract] [--llm] [--llm-live] [--all] [--providers LIST] [-- PYTEST_ARGS...]

Defaults:
  If no selection flags are provided, runs all tests except contract + live LLM:
    -m "not contract and not live_llm"

Selection flags (can be combined, except --all):
  --unit           Run unit tests
  --integration    Run integration tests (non-LLM + LLM)
  --contract       Run contract tests
  --llm            Run non-live LLM integration tests
  --llm-live       Run live LLM integration tests (real API calls; may incur cost)
                   Includes: Agent pipeline tests + Provider tests (~$0.50 total)
  --all            Run everything except live LLM tests

Live options:
  --providers LIST   Comma-separated provider list (e.g. "openai,anthropic,gemini")
                    Passed via LIVE_LLM_PROVIDERS for live tests.

Examples:
  ./run_tests.sh
  ./run_tests.sh --unit
  ./run_tests.sh --integration -- -vv
  ./run_tests.sh --llm
  ./run_tests.sh --llm-live --providers openai,anthropic
  ./run_tests.sh --all
EOF
}

python_bin="${PYTHON_BIN:-}"
if [[ -z "$python_bin" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    python_bin="python3"
  elif command -v python >/dev/null 2>&1; then
    python_bin="python"
  else
    echo "error: could not find python (tried python3, python)" >&2
    exit 127
  fi
fi

providers=""
pytest_args=()

selected=()
use_all=false
enable_live=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --unit)
      selected+=("unit")
      shift
      ;;
    --integration)
      selected+=("integration")
      shift
      ;;
    --contract)
      selected+=("contract")
      shift
      ;;
    --llm)
      selected+=("llm")
      shift
      ;;
    --llm-live)
      selected+=("llm_live")
      enable_live=true
      shift
      ;;
    --all)
      use_all=true
      shift
      ;;
    --providers)
      providers="${2:-}"
      if [[ -z "$providers" ]]; then
        echo "error: --providers requires a value" >&2
        exit 2
      fi
      shift 2
      ;;
    --)
      shift
      pytest_args+=("$@")
      break
      ;;
    *)
      if [[ "$1" == -* ]]; then
        pytest_args+=("$1")
        shift
      else
        echo "error: unknown argument: $1" >&2
        echo "" >&2
        usage >&2
        exit 2
      fi
      ;;
  esac
done

if [[ "$use_all" = true && ${#selected[@]} -gt 0 ]]; then
  echo "error: --all cannot be combined with other selection flags" >&2
  exit 2
fi

if [[ -n "$providers" && "$enable_live" != true ]]; then
  echo "error: --providers is only valid with --llm-live" >&2
  exit 2
fi

if [[ -n "$providers" ]]; then
  export LIVE_LLM_PROVIDERS="$providers"
fi

marker_expr=""

if [[ "$use_all" = true ]]; then
  marker_expr="not live_llm"
elif [[ ${#selected[@]} -eq 0 ]]; then
  marker_expr="not contract and not live_llm"
else
  parts=()
  for sel in "${selected[@]}"; do
    case "$sel" in
      unit)
        parts+=("unit")
        ;;
      integration)
        parts+=("integration")
        ;;
      contract)
        parts+=("contract")
        ;;
      llm)
        parts+=("(llm_integration and not live_llm)")
        ;;
      llm_live)
        export RUN_LIVE_LLM_TESTS=1
        parts+=("(llm_integration and live_llm)")
        ;;
      *)
        echo "error: invalid selection: $sel" >&2
        exit 2
        ;;
    esac
  done

  marker_expr="(${parts[0]}"
  for ((i=1; i<${#parts[@]}; i++)); do
    marker_expr="${marker_expr} or ${parts[$i]}"
  done
  marker_expr="${marker_expr})"

  if [[ "$enable_live" != true ]]; then
    marker_expr="${marker_expr} and not live_llm"
  fi
fi

if [[ ${#pytest_args[@]} -gt 0 ]]; then
  exec "$python_bin" -m pytest -m "$marker_expr" -q "${pytest_args[@]}"
fi
exec "$python_bin" -m pytest -m "$marker_expr" -q
