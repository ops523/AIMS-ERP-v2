from __future__ import annotations

from sqlalchemy import (
    Integer,
    Float,
    String,
    ForeignKey,
    Text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from models.base import Base, TimestampMixin


class PrintingSession(Base, TimestampMixin):

    __tablename__ = "printing_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    media_roll_id: Mapped[int] = mapped_column(
        ForeignKey("media_rolls.id")
    )

    printer_id: Mapped[int] = mapped_column(
        ForeignKey("printers.id")
    )

    operator_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    campaign_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    artwork_name: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True
    )

    opening_sqft: Mapped[float] = mapped_column(
        Float
    )

    closing_sqft: Mapped[float] = mapped_column(
        Float
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    media_roll = relationship("MediaRoll")
