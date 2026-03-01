@echo off
setlocal

set ROOT=%~dp0..

if not exist "%ROOT%\data" mkdir "%ROOT%\data"

cd /d "%ROOT%\backend"
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    .venv\Scripts\pip install -e ".[dev]" --quiet
)
echo Starting backend on http://127.0.0.1:8000 ...
start "Backend" .venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

cd /d "%ROOT%\frontend"
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install --silent
)
echo Starting frontend on http://127.0.0.1:5173 ...
start "Frontend" npm run dev

echo.
echo App running at http://127.0.0.1:5173
echo Close the terminal windows to stop.
