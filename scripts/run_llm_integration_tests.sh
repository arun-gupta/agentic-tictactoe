#!/bin/bash

set -euo pipefail

# Backward-compatible wrapper. Prefer using `./run_tests.sh`.

args=()
mode="non-live"
providers=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      exec bash ./run_tests.sh --help
      ;;
    --non-live)
      mode="non-live"
      shift
      ;;
    --live)
      mode="live"
      shift
      ;;
    --all)
      mode="all"
      shift
      ;;
    --providers)
      providers="${2:-}"
      shift 2
      ;;
    --)
      shift
      args+=("--" "$@")
      break
      ;;
    *)
      if [[ "$1" == -* ]]; then
        args+=("$1")
        shift
      else
        echo "error: unknown argument: $1" >&2
        exit 2
      fi
      ;;
  esac
done

case "$mode" in
  non-live)
    exec bash ./run_tests.sh --llm "${args[@]}"
    ;;
  live)
    if [[ -n "$providers" ]]; then
      exec bash ./run_tests.sh --llm-live --providers "$providers" "${args[@]}"
    fi
    exec bash ./run_tests.sh --llm-live "${args[@]}"
    ;;
  all)
    exec bash ./run_tests.sh --llm --llm-live "${args[@]}"
    ;;
  *)
    echo "error: invalid mode: $mode" >&2
    exit 2
    ;;
esac
