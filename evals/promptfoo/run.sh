#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PROMPTFOO_DISABLE_TELEMETRY=1
export PROMPTFOO_DISABLE_UPDATE=1
export PROMPTFOO_CONFIG_DIR="$PWD/.promptfoo"
mkdir -p results
case "${1:-}" in
  smoke)
    exec ./node_modules/.bin/promptfoo eval -c smoke.yaml --no-share --no-cache --max-concurrency 1 -o results/smoke.json
    ;;
  eval)
    if [[ -z "${DEEPSEEK_API_KEY:-}" ]]; then
      echo 'Missing DEEPSEEK_API_KEY; set it with hidden input and export in this terminal.' >&2
      exit 1
    fi
    run_id="$(date -u +%Y%m%dT%H%M%SZ)-$$"
    echo "10 evaluations: 5 questions x 2 prompts x 1 model. Output: results/$run_id.json"
    exec ./node_modules/.bin/promptfoo eval -c promptfooconfig.yaml --no-share --no-cache --max-concurrency 1 -o "results/$run_id.json" "results/$run_id.html"
    ;;
  *) echo 'Usage: bash run.sh smoke|eval' >&2; exit 2 ;;
esac
