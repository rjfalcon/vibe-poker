"""Statistics endpoints."""
from __future__ import annotations

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.stats import OverviewStatsOut, PositionStatsOut, TimelinePointOut
from app.stats.engine import StatsEngine
from app.stats.timeline import build_timeline

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=OverviewStatsOut)
def overview(
    session_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    engine = StatsEngine(db)
    stats = engine.overview(session_id)
    return OverviewStatsOut(**stats.__dict__)


@router.get("/positions", response_model=List[PositionStatsOut])
def positions(
    session_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    engine = StatsEngine(db)
    rows = engine.by_position(session_id)
    return [PositionStatsOut(**r.__dict__) for r in rows]


@router.get("/timeline", response_model=List[TimelinePointOut])
def timeline(
    session_id: Optional[str] = Query(None),
    sample_every: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    points = build_timeline(db, session_id, sample_every)
    return [
        TimelinePointOut(
            index=p.index,
            played_at=p.played_at,
            cumulative_bb=p.cumulative_bb,
            bb_per_100=p.bb_per_100,
        )
        for p in points
    ]
