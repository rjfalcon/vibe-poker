from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ImportSession(Base):
    __tablename__ = "import_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    filename: Mapped[str] = mapped_column(String(255))
    imported_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    hero_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hand_count: Mapped[int] = mapped_column(Integer, default=0)

    hands: Mapped[list["Hand"]] = relationship(  # noqa: F821
        "Hand", back_populates="session", cascade="all, delete-orphan"
    )
