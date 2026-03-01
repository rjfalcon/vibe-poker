from __future__ import annotations

import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Ordered numeric sequence across all streets for replay
_STREET_ORDER = {"PREFLOP": 0, "FLOP": 1, "TURN": 2, "RIVER": 3}


class Action(Base):
    """A single player action within a hand."""

    __tablename__ = "actions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    hand_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hands.id"), index=True
    )
    player_name: Mapped[str] = mapped_column(String(100))
    street: Mapped[str] = mapped_column(String(10))  # PREFLOP/FLOP/TURN/RIVER
    sequence: Mapped[int] = mapped_column(Integer)    # global order in hand
    action_type: Mapped[str] = mapped_column(String(15))
    # FOLD | FAST_FOLD | CHECK | CALL | BET | RAISE | ALL_IN
    amount_bb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_all_in: Mapped[bool] = mapped_column(Boolean, default=False)

    hand: Mapped["Hand"] = relationship("Hand", back_populates="actions")  # noqa: F821
