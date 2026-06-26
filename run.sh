#!/usr/bin/env bash
# ============================================================
#  HREA RAG - one-click launcher for macOS / Linux.
#  Run:  ./run.sh   (first run sets everything up automatically)
# ============================================================
set -e
cd "$(dirname "$0")"

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then
  echo "Python 3.9+ is required. Install it from https://www.python.org/downloads/"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if [ ! -f ".venv/.installed" ]; then
  echo "Installing dependencies (first run only, may take a few minutes)..."
  pip install --quiet --upgrade pip
  pip install --quiet -r requirements.txt
  touch .venv/.installed
fi

# Open the browser shortly after the server starts.
( sleep 2
  if command -v open >/dev/null 2>&1; then open http://127.0.0.1:5000
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open http://127.0.0.1:5000
  fi ) &

echo "Starting HREA RAG at http://127.0.0.1:5000  (Ctrl+C to stop)"
python app.py
