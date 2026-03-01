from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Hand(Base):
    """One poker hand from the hero's perspective."""

    __tablename__ = "hands"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("import_sessions.id"), index=True
    )
    ggpoker_hand_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    table_name: Mapped[str] = mapped_column(String(100))
    game_type: Mapped[str] = mapped_column(String(20), default="NLH")
    stakes_sb: Mapped[float] = mapped_column(Float)
    stakes_bb: Mapped[float] = mapped_column(Float)
    played_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    # Seating
    button_seat: Mapped[int] = mapped_column(Integer)
    hero_seat: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    num_players: Mapped[int] = mapped_column(Integer)
    hero_position: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    hero_cards: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Rush & Cash
    is_fast_fold: Mapped[bool] = mapped_column(Boolean, default=False)

    # Preflop stats
    hero_vpip: Mapped[bool] = mapped_column(Boolean, default=False)
    hero_pfr: Mapped[bool] = mapped_column(Boolean, default=False)
    hero_had_3bet_opportunity: Mapped[bool] = mapped_column(Boolean, default=False)
    hero_3bet: Mapped[bool] = mapped_column(Boolean, default=False)

    # Postflop stats
    hero_saw_flop: Mapped[bool] = mapped_column(Boolean, default=False)
    hero_went_to_showdown: Mapped[bool] = mapped_column(Boolean, default=False)
    hero_won_at_showdown: Mapped[bool] = mapped_column(Boolean, default=False)

    # Aggression counts (for AF calculation)
    hero_bet_raise_count: Mapped[int] = mapped_column(Integer, default=0)
    hero_call_count: Mapped[int] = mapped_column(Integer, default=0)

    # Money (in big blinds)
    hero_profit_bb: Mapped[float] = mapped_column(Float, default=0.0)
    rake_bb: Mapped[float] = mapped_column(Float, default=0.0)

    # Board
    flop_cards: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    turn_card: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    river_card: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)

    run_it_twice: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    session: Mapped["ImportSession"] = relationship(  # noqa: F821
        "ImportSession", back_populates="hands"
    )
    players: Mapped[list["HandPlayer"]] = relationship(  # noqa: F821
        "HandPlayer", back_populates="hand", cascade="all, delete-orphan"
    )
    actions: Mapped[list["Action"]] = relationship(  # noqa: F821
        "Action", back_populates="hand", cascade="all, delete-orphan",
        order_by="Action.sequence"
    )
