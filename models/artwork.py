from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, UUIDMixin


class Artwork(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "artworks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaigns.id")
    )

    artwork_code: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )

    artwork_name: Mapped[str] = mapped_column(
        String(250)
    )

    width_ft: Mapped[float] = mapped_column(Float)

    height_ft: Mapped[float] = mapped_column(Float)

    total_sqft: Mapped[float] = mapped_column(Float)

    campaign = relationship("Campaign")
