from __future__ import annotations

import uuid
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HandPlayer(Base):
    """One player's seat in a specific hand."""

    __tablename__ = "hand_players"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    hand_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("hands.id"), index=True
    )
    seat: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    stack_bb: Mapped[float] = mapped_column(Float)
    position: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    is_hero: Mapped[bool] = mapped_column(Boolean, default=False)
    hole_cards: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    profit_bb: Mapped[float] = mapped_column(Float, default=0.0)

    hand: Mapped["Hand"] = relationship("Hand", back_populates="players")  # noqa: F821
