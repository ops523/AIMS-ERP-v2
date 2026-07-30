from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base
from models.mixins import UUIDMixin
from models.mixins import TimestampMixin


class MediaRollHistory(
    Base,
    UUIDMixin,
    TimestampMixin,
):

    __tablename__ = "media_roll_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    media_roll_id: Mapped[int] = mapped_column(
        ForeignKey("media_rolls.id"),
        index=True,
    )

    event: Mapped[str] = mapped_column(
        String(50),
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    current_status: Mapped[str] = mapped_column(
        String(40),
    )

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    scanned_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    media_roll = relationship(
        "MediaRoll",
        back_populates="history",
    )
