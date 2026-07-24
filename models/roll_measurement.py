from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Integer,
    Float,
    ForeignKey,
    DateTime,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.base import Base, TimestampMixin


class RollMeasurement(Base, TimestampMixin):

    __tablename__ = "roll_measurements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    media_roll_id: Mapped[int] = mapped_column(
        ForeignKey("media_rolls.id"),
        nullable=False,
        index=True,
    )

    measured_length_ft: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    measured_width_ft: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    actual_sqft: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    measured_by: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    measured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    media_roll = relationship(
        "MediaRoll",
        back_populates="measurements",
    )
