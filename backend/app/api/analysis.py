"""Hand analysis via built-in GTO rule engine (no external API required)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.hand import Hand
from app.poker_engine.analyzer import analyze

router = APIRouter(prefix="/hands", tags=["analysis"])


@router.post("/{hand_id}/analyze")
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
