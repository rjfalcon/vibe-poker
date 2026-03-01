"""Compute BB/100 over time for chart rendering."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.hand import Hand


@dataclass
class TimelinePoint:
    index: int          # hand number (1-based)
    played_at: datetime
    cumulative_bb: float
    bb_per_100: float   # rolling BB/100 (all hands up to this point)


def build_timeline(
    db: Session,
    session_id: str | None = None,
    sample_every: int = 10,
) -> list[TimelinePoint]:
    """Return timeline points, sampled every `sample_every` hands."""
    q = db.query(Hand).order_by(Hand.played_at.asc())
    if session_id:
        q = q.filter(Hand.session_id == session_id)

    hands = q.all()
    if not hands:
        return []

    points = []
    cumulative = 0.0
    for i, hand in enumerate(hands, start=1):
        cumulative += hand.hero_profit_bb
        if i % sample_every == 0 or i == len(hands):
            bb100 = round((cumulative / i) * 100, 2)
            points.append(
                TimelinePoint(
                    index=i,
                    played_at=hand.played_at,
                    cumulative_bb=round(cumulative, 2),
                    bb_per_100=bb100,
                )
            )
    return points
