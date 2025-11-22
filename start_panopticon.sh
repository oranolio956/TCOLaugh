#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

API_PORT="${PANOPTICON_PORT:-8000}"
START_CRAWLER="${START_CRAWLER:-false}"
START_CELERY="${START_CELERY:-true}"

if lsof -i :"$API_PORT" &>/dev/null; then
  echo "Port ${API_PORT} already in use. Set PANOPTICON_PORT or stop the existing process."
  exit 1
fi

export PATH=$PATH:/home/ubuntu/.local/bin
export PYTHONPATH=$PYTHONPATH:"$ROOT_DIR"

PIDS=()
function cleanup() {
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" &>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT

echo "Starting Panopticon API on port ${API_PORT}..."
uvicorn panopticon.api.main:app --host 0.0.0.0 --port "$API_PORT" > api.log 2>&1 &
PIDS+=($!)
sleep 3
if ! kill -0 "${PIDS[-1]}" &>/dev/null; then
  echo "API failed to start. Check api.log for details."
  exit 1
fi
echo "API running. Access http://localhost:${API_PORT}"

if [[ "${START_CELERY}" == "true" ]]; then
  echo "Starting Celery worker..."
  celery -A panopticon.worker worker --loglevel=info > worker.log 2>&1 &
  PIDS+=($!)
fi

if [[ "${START_CRAWLER}" == "true" ]]; then
  echo "Starting ingestion crawler..."
  python3 panopticon/ingestion/crawlers/mock_crawler.py --continuous --delay 3.0 > crawler.log 2>&1 &
  PIDS+=($!)
fi

echo "Panopticon services started. Press Ctrl+C to stop."
wait "${PIDS[0]}"
