from __future__ import annotations

from sqlalchemy import *

from sqlalchemy.orm import *

from models.base import Base, TimestampMixin


class Wastage(Base, TimestampMixin):

    __tablename__ = "wastage"

    id = mapped_column(Integer, primary_key=True)

    media_roll_id = mapped_column(
        ForeignKey("media_rolls.id")
    )

    printing_session_id = mapped_column(
        ForeignKey("printing_sessions.id"),
        nullable=True
    )

    reason = mapped_column(String(150))

    sqft = mapped_column(Float)

    remarks = mapped_column(Text)

    photo = mapped_column(
        String(250),
        nullable=True
    )

    media_roll = relationship("MediaRoll")
