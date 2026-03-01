# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend (Python 3.12 + FastAPI)
```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/uvicorn app.main:app --reload          # dev server → http://127.0.0.1:8000
.venv/bin/pytest                                  # all tests (requires 80% coverage)
.venv/bin/pytest tests/test_parser.py -v          # single test file
.venv/bin/pytest -k "TestFastFold"                # single test class
```

### Frontend (React + Vite + TypeScript)
```bash
cd frontend
npm install
npm run dev          # dev server → http://127.0.0.1:5173
npm run build        # production build
```

### Start both at once
```bash
./scripts/start.sh   # macOS / Linux
scripts\start.bat    # Windows
```

## Architecture

### Overview
Local web app: FastAPI backend on :8000, React/Vite frontend on :5173 (Vite proxies `/api` to backend).
SQLite database stored in `data/poker.db` (created automatically on first start).
No authentication — single-user local tool.

### Backend layers
```
app/parser/     → Parse raw .txt hand histories into ParsedHand dataclasses
app/stats/      → Compute stats from DB (engine.py) and positions (positions.py)
app/api/        → FastAPI routers: /api/sessions, /api/hands, /api/stats
app/models/     → SQLAlchemy ORM: ImportSession → Hand → HandPlayer + Action
app/schemas/    → Pydantic response schemas
```

**Parse flow:** `split_hands()` splits multi-hand file → `GGPokerParser.parse()` produces `ParsedHand` → `rush_cash.compute_stats()` fills all derived fields → API layer persists to DB.

**Rush & Cash specifics:**
- `[Fast Fold]` actions are parsed as `action_type = "FAST_FOLD"`
- `hand.is_fast_fold = True` when hero's first preflop action is FAST_FOLD
- VPIP denominator = all hands (fast-folds count as non-VPIP)
- Fast-fold % = `is_fast_fold` hands / total hands
- Positions computed in `stats/positions.py` from button seat + occupied seats

### Frontend routes
| Path | Component | Description |
|------|-----------|-------------|
| `/` | Dashboard | Stats overview + BB/100 chart |
| `/hands` | HandBrowser | Filterable hand table |
| `/hands/:id` | HandDetail | Street-by-street detail view |
| `/positions` | PositionTable | Stats per position |
| `/import` | ImportZone | Drag & drop import |

### Key data model fields
- `Hand.is_fast_fold` — hero used fast-fold
- `Hand.hero_position` — BTN/CO/HJ/MP/UTG/UTG+1/SB/BB
- `Hand.hero_vpip/pfr/3bet` — preflop stats (computed at import time)
- `Hand.hero_profit_bb` — net result in big blinds
- `Hand.run_it_twice` — run-it-twice was used

## Parser edge cases
The parser handles: fast-fold before own turn, all-ins (`and is all-in`), run-it-twice, multiple side pots in SUMMARY, and muck/no-showdown. Blind postings are NOT counted as actions for stats purposes.

## Adding a new stat
1. Add field to `app/models/hand.py` (Hand model)
2. Compute it in `app/parser/rush_cash.py` (`compute_stats()`)
3. Persist it in `app/api/sessions.py` (import loop)
4. Add to `app/stats/engine.py` aggregation
5. Add to `app/schemas/stats.py` Pydantic schema
6. Display in `frontend/src/components/StatsGrid.tsx`
