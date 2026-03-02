"""Hand analysis via built-in GTO rule engine (no external API required)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.hand import Hand
from app.poker_engine.analyzer import analyze
from app.poker_engine.bulk_analyzer import bulk_analyze
from app.stats.engine import StatsEngine

router = APIRouter(tags=["analysis"])


@router.post("/hands/{hand_id}/analyze")
def analyze_hand(hand_id: str, db: Session = Depends(get_db)):
    hand = (
        db.query(Hand)
        .options(selectinload(Hand.players), selectinload(Hand.actions))
        .filter(Hand.id == hand_id)
        .first()
    )
    if not hand:
        raise HTTPException(status_code=404, detail="Hand not found")
    return analyze(hand)


@router.get("/stats/bulk-analysis")
def bulk_analysis(session_id: str = None, db: Session = Depends(get_db)):
    engine = StatsEngine(db)
    overview = engine.overview(session_id=session_id)
    positions = engine.by_position(session_id=session_id)
    return bulk_analyze(overview, positions)
