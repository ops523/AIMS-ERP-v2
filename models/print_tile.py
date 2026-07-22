from __future__ import annotations

from sqlalchemy import *

from sqlalchemy.orm import *

from models.base import Base, TimestampMixin


class PrintTile(Base, TimestampMixin):

    __tablename__ = "print_tiles"

    id = mapped_column(Integer, primary_key=True)

    printing_session_id = mapped_column(
        ForeignKey("printing_sessions.id")
    )

    tile_no = mapped_column(Integer)

    artwork_code = mapped_column(String(100))

    width_ft = mapped_column(Float)

    height_ft = mapped_column(Float)

    bleed_left_in = mapped_column(Float)

    bleed_right_in = mapped_column(Float)

    printed_sqft = mapped_column(Float)

    trimmed_sqft = mapped_column(Float)

    waste_sqft = mapped_column(Float)

    package_no = mapped_column(
        String(100),
        nullable=True
    )

    printing_session = relationship(
        "PrintingSession"
    )
