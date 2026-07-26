from __future__ import annotations

from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from models.base import Base
from models.base import TimestampMixin
from models.base import UUIDMixin


class ProductionItem(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "production_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
    )

    campaign_artwork_id: Mapped[int] = mapped_column(
        ForeignKey("campaign_artworks.id"),
    )

    media_roll_id: Mapped[int | None] = mapped_column(
        ForeignKey("media_rolls.id"),
        nullable=True,
    )

    planned_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    printed_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    wastage_sqft: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
    )

    production_batch = relationship(
        "ProductionBatch",
        back_populates="production_items",
    )

    campaign_artwork = relationship(
        "CampaignArtwork",
    )

    media_roll = relationship(
        "MediaRoll",
    )
