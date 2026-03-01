"""Hand listing and detail endpoints."""
from __future__ import annotations

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.hand import Hand
from app.schemas.hand import HandDetail, HandSummary

router = APIRouter(prefix="/hands", tags=["hands"])


@router.get("/", response_model=List[HandSummary])
def list_hands(
    session_id: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    is_fast_fold: Optional[bool] = Query(None),
    min_profit: Optional[float] = Query(None),
    max_profit: Optional[float] = Query(None),
    street_reached: Optional[str] = Query(None, description="flop|turn|river|showdown"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Hand)

    if session_id:
        q = q.filter(Hand.session_id == session_id)
    if position:
        q = q.filter(Hand.hero_position == position.upper())
    if is_fast_fold is not None:
        q = q.filter(Hand.is_fast_fold == is_fast_fold)
    if min_profit is not None:
        q = q.filter(Hand.hero_profit_bb >= min_profit)
    if max_profit is not None:
        q = q.filter(Hand.hero_profit_bb <= max_profit)
    if street_reached:
        sr = street_reached.lower()
        if sr == "flop":
            q = q.filter(Hand.flop_cards.isnot(None))
        elif sr == "turn":
            q = q.filter(Hand.turn_card.isnot(None))
        elif sr == "river":
            q = q.filter(Hand.river_card.isnot(None))
        elif sr == "showdown":
            q = q.filter(Hand.hero_went_to_showdown == True)  # noqa: E712

    total = q.count()
    hands = (
        q.order_by(Hand.played_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return hands


@router.get("/{hand_id}", response_model=HandDetail)
def get_hand(hand_id: str, db: Session = Depends(get_db)):
    hand = (
        db.query(Hand)
        .options(selectinload(Hand.players), selectinload(Hand.actions))
        .filter(Hand.id == hand_id)
        .first()
    )
    if not hand:
        raise HTTPException(status_code=404, detail="Hand not found")
    return hand


@router.get("/{hand_id}/replay")
def get_replay(hand_id: str, db: Session = Depends(get_db)):
    """Return structured street-by-street replay data."""
    hand = (
        db.query(Hand)
        .options(selectinload(Hand.players), selectinload(Hand.actions))
        .filter(Hand.id == hand_id)
        .first()
    )
    if not hand:
        raise HTTPException(status_code=404, detail="Hand not found")

    streets = {}
    for street_name in ("PREFLOP", "FLOP", "TURN", "RIVER"):
        acts = [
            {
                "player": a.player_name,
                "action": a.action_type,
                "amount_bb": a.amount_bb,
                "is_all_in": a.is_all_in,
            }
            for a in hand.actions
            if a.street == street_name
        ]
        if acts or street_name == "PREFLOP":
            board: list[str] = []
            if street_name == "FLOP" and hand.flop_cards:
                board = hand.flop_cards.split()
            elif street_name == "TURN" and hand.turn_card:
                board = hand.turn_card.split()
            elif street_name == "RIVER" and hand.river_card:
                board = hand.river_card.split()
            streets[street_name] = {"board": board, "actions": acts}

    return {
        "hand_id": hand_id,
        "stakes_bb": hand.stakes_bb,
        "players": [
            {
                "seat": p.seat,
                "name": p.name,
                "stack_bb": p.stack_bb,
                "position": p.position,
                "is_hero": p.is_hero,
                "hole_cards": p.hole_cards,
            }
            for p in hand.players
        ],
        "streets": streets,
        "run_it_twice": hand.run_it_twice,
    }
