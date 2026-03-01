#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Create data dir
mkdir -p "$ROOT/data"

# Backend
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
  .venv/bin/pip install -e ".[dev]" --quiet
fi
echo "Starting backend on http://127.0.0.1:8000 ..."
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Frontend
cd "$ROOT/frontend"
if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install --silent
fi
echo "Starting frontend on http://127.0.0.1:5173 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "App running at http://127.0.0.1:5173"
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
